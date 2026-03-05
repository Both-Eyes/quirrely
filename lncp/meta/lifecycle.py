#!/usr/bin/env python3
"""
LNCP META: USER LIFECYCLE v5.1
State machine for tracking users through their journey.

States:
  ANONYMOUS → SIGNED_UP → ONBOARDING → ACTIVATED → ENGAGED → RETAINED
                 ↓            ↓            ↓           ↓
             BOUNCED     ABANDONED     DORMANT     AT_RISK → CHURNED

Each state has:
- Entry criteria
- Exit criteria
- Time limits
- Optimization targets
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum

from .events import EventType, AppEvent, UserTier, get_event_collector
from .activation import ActivationTracker, ActivationStatus, get_activation_tracker


# ═══════════════════════════════════════════════════════════════════════════
# USER STATES
# ═══════════════════════════════════════════════════════════════════════════

class UserState(str, Enum):
    """User lifecycle states."""
    # Progression states
    ANONYMOUS = "anonymous"         # Visited but not signed up
    SIGNED_UP = "signed_up"         # Created account
    ONBOARDING = "onboarding"       # Started using app
    ACTIVATED = "activated"         # Met activation criteria
    ENGAGED = "engaged"             # Regular usage
    RETAINED = "retained"           # Paying and using
    
    # Terminal/risk states
    BOUNCED = "bounced"             # Signed up, no action in 24h
    ABANDONED = "abandoned"         # Started onboarding, didn't activate in 7d
    DORMANT = "dormant"             # Was engaged, no activity 14d+
    AT_RISK = "at_risk"             # Paying but declining usage
    CHURNED = "churned"             # Subscription ended


# ═══════════════════════════════════════════════════════════════════════════
# STATE THRESHOLDS (Configurable via Parameter Store)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LifecycleThresholds:
    """Configurable thresholds for state transitions."""
    
    # Bounce: no action after signup
    bounce_hours: int = 24
    
    # Abandon: didn't activate
    abandon_days: int = 7
    
    # Engaged: regular usage
    engaged_sessions_per_14d: int = 3
    
    # Dormant: no activity
    dormant_days: int = 14
    
    # At risk: declining usage (paying users)
    at_risk_usage_decline_pct: float = 50  # 50% drop from peak
    at_risk_days_declining: int = 14


# ═══════════════════════════════════════════════════════════════════════════
# USER RECORD
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UserLifecycle:
    """Complete lifecycle tracking for a user."""
    
    user_id: str
    visitor_id: str
    tier: UserTier
    
    # Current state
    current_state: UserState
    state_entered_at: datetime
    
    # History
    state_history: List[Dict] = field(default_factory=list)
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.utcnow)
    signed_up_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    churned_at: Optional[datetime] = None
    
    # Activity tracking
    last_activity: datetime = field(default_factory=datetime.utcnow)
    total_sessions: int = 0
    sessions_last_14d: int = 0
    peak_sessions_14d: int = 0
    
    # Engagement
    total_analyses: int = 0
    total_exports: int = 0
    
    def transition_to(self, new_state: UserState, timestamp: Optional[datetime] = None):
        """Transition to a new state."""
        timestamp = timestamp or datetime.utcnow()
        
        # Record history
        self.state_history.append({
            "from_state": self.current_state.value,
            "to_state": new_state.value,
            "timestamp": timestamp.isoformat(),
            "duration_hours": (timestamp - self.state_entered_at).total_seconds() / 3600,
        })
        
        # Update current
        self.current_state = new_state
        self.state_entered_at = timestamp
        
        # Update specific timestamps
        if new_state == UserState.ACTIVATED:
            self.activated_at = timestamp
        elif new_state == UserState.CHURNED:
            self.churned_at = timestamp
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "tier": self.tier.value,
            "current_state": self.current_state.value,
            "state_entered_at": self.state_entered_at.isoformat(),
            "first_seen": self.first_seen.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_sessions": self.total_sessions,
            "state_transitions": len(self.state_history),
        }


# ═══════════════════════════════════════════════════════════════════════════
# LIFECYCLE MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class UserLifecycleManager:
    """
    Manages user lifecycle state machine.
    
    Responsibilities:
    - Track state per user
    - Process events for state transitions
    - Identify users in each state
    - Calculate state-based metrics
    """
    
    def __init__(
        self,
        thresholds: Optional[LifecycleThresholds] = None,
        activation_tracker: Optional[ActivationTracker] = None,
    ):
        self.thresholds = thresholds or LifecycleThresholds()
        self.activation_tracker = activation_tracker or get_activation_tracker()
        
        # User tracking
        self.users: Dict[str, UserLifecycle] = {}
        
        # State change callbacks
        self._state_callbacks: List[Callable[[str, UserState, UserState], None]] = []
    
    def on_state_change(self, callback: Callable[[str, UserState, UserState], None]):
        """Register callback for state changes."""
        self._state_callbacks.append(callback)
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT PROCESSING
    # ─────────────────────────────────────────────────────────────────────
    
    def process_events(self, events: List[AppEvent]):
        """Process events and update user states."""
        events = sorted(events, key=lambda e: e.timestamp)
        
        for event in events:
            self._process_event(event)
        
        # Check time-based transitions
        self._check_time_transitions()
        
        # Sync with activation tracker
        self._sync_activation()
    
    def _process_event(self, event: AppEvent):
        """Process a single event."""
        user_id = event.user_id or event.visitor_id
        
        # Ensure user exists
        if user_id not in self.users:
            self._create_user(event)
        
        user = self.users[user_id]
        user.last_activity = event.timestamp
        
        # Update activity counters
        if event.event_type == EventType.SESSION_STARTED:
            user.total_sessions += 1
            user.sessions_last_14d += 1
            user.peak_sessions_14d = max(user.peak_sessions_14d, user.sessions_last_14d)
        
        if event.event_type == EventType.ANALYSIS_COMPLETED:
            user.total_analyses += 1
        
        if event.event_type == EventType.RESULT_EXPORTED:
            user.total_exports += 1
        
        # Process state transitions
        self._process_transition(user, event)
    
    def _create_user(self, event: AppEvent):
        """Create new user record."""
        user_id = event.user_id or event.visitor_id
        
        # Determine initial state
        if event.event_type == EventType.ACCOUNT_CREATED:
            initial_state = UserState.SIGNED_UP
        else:
            initial_state = UserState.ANONYMOUS
        
        self.users[user_id] = UserLifecycle(
            user_id=user_id,
            visitor_id=event.visitor_id,
            tier=event.tier,
            current_state=initial_state,
            state_entered_at=event.timestamp,
            first_seen=event.timestamp,
            signed_up_at=event.timestamp if event.event_type == EventType.ACCOUNT_CREATED else None,
        )
    
    def _process_transition(self, user: UserLifecycle, event: AppEvent):
        """Process potential state transitions based on event."""
        old_state = user.current_state
        new_state = None
        
        # ANONYMOUS → SIGNED_UP
        if old_state == UserState.ANONYMOUS:
            if event.event_type == EventType.ACCOUNT_CREATED:
                new_state = UserState.SIGNED_UP
                user.signed_up_at = event.timestamp
        
        # SIGNED_UP → ONBOARDING
        elif old_state == UserState.SIGNED_UP:
            if event.event_type in [EventType.ONBOARDING_STARTED, EventType.ANALYSIS_STARTED]:
                new_state = UserState.ONBOARDING
        
        # ONBOARDING → ACTIVATED (handled by sync)
        
        # ACTIVATED → ENGAGED
        elif old_state == UserState.ACTIVATED:
            if user.sessions_last_14d >= self.thresholds.engaged_sessions_per_14d:
                new_state = UserState.ENGAGED
        
        # ENGAGED → RETAINED
        elif old_state == UserState.ENGAGED:
            if event.event_type == EventType.ACCOUNT_UPGRADED:
                if event.tier in [UserTier.PRO, UserTier.ENTERPRISE]:
                    new_state = UserState.RETAINED
                    user.tier = event.tier
        
        # RETAINED → AT_RISK (usage decline)
        elif old_state == UserState.RETAINED:
            if user.peak_sessions_14d > 0:
                decline = (user.peak_sessions_14d - user.sessions_last_14d) / user.peak_sessions_14d
                if decline >= self.thresholds.at_risk_usage_decline_pct / 100:
                    new_state = UserState.AT_RISK
        
        # AT_RISK → RETAINED (re-engaged)
        elif old_state == UserState.AT_RISK:
            if user.sessions_last_14d >= self.thresholds.engaged_sessions_per_14d:
                new_state = UserState.RETAINED
        
        # CHURNED (from Stripe events)
        if event.event_type == EventType.ACCOUNT_CHURNED:
            new_state = UserState.CHURNED
        
        # Apply transition
        if new_state and new_state != old_state:
            user.transition_to(new_state, event.timestamp)
            self._notify_state_change(user.user_id, old_state, new_state)
    
    def _check_time_transitions(self):
        """Check for time-based state transitions."""
        now = datetime.utcnow()
        
        for user in self.users.values():
            old_state = user.current_state
            new_state = None
            
            time_in_state = (now - user.state_entered_at).total_seconds() / 3600
            time_since_activity = (now - user.last_activity).total_seconds() / 3600
            
            # SIGNED_UP → BOUNCED (no action in 24h)
            if old_state == UserState.SIGNED_UP:
                if time_in_state >= self.thresholds.bounce_hours:
                    new_state = UserState.BOUNCED
            
            # ONBOARDING → ABANDONED (didn't activate in 7d)
            elif old_state == UserState.ONBOARDING:
                if time_in_state >= self.thresholds.abandon_days * 24:
                    new_state = UserState.ABANDONED
            
            # ENGAGED/ACTIVATED → DORMANT (no activity 14d+)
            elif old_state in [UserState.ENGAGED, UserState.ACTIVATED]:
                if time_since_activity >= self.thresholds.dormant_days * 24:
                    new_state = UserState.DORMANT
            
            if new_state and new_state != old_state:
                user.transition_to(new_state, now)
                self._notify_state_change(user.user_id, old_state, new_state)
    
    def _sync_activation(self):
        """Sync with activation tracker."""
        for user_id, user in self.users.items():
            if user.current_state == UserState.ONBOARDING:
                # Check if activated
                if user_id in self.activation_tracker.users:
                    activation = self.activation_tracker.users[user_id]
                    if activation.status == ActivationStatus.ACTIVATED:
                        old_state = user.current_state
                        user.transition_to(UserState.ACTIVATED, activation.activated_at)
                        self._notify_state_change(user_id, old_state, UserState.ACTIVATED)
    
    def _notify_state_change(self, user_id: str, old_state: UserState, new_state: UserState):
        """Notify callbacks of state change."""
        for callback in self._state_callbacks:
            try:
                callback(user_id, old_state, new_state)
            except Exception:
                pass
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_users_in_state(self, state: UserState) -> List[UserLifecycle]:
        """Get all users in a given state."""
        return [u for u in self.users.values() if u.current_state == state]
    
    def get_state_distribution(self) -> Dict[str, int]:
        """Get count of users in each state."""
        dist = {state.value: 0 for state in UserState}
        for user in self.users.values():
            dist[user.current_state.value] += 1
        return dist
    
    def get_at_risk_users(self) -> List[UserLifecycle]:
        """Get users at risk of churning."""
        return self.get_users_in_state(UserState.AT_RISK)
    
    def get_conversion_rates(self) -> Dict[str, float]:
        """Get conversion rates between states."""
        rates = {}
        
        # Signup → Activated
        signups = len([u for u in self.users.values() if u.signed_up_at])
        activated = len([u for u in self.users.values() if u.activated_at])
        rates["signup_to_activated"] = activated / signups if signups > 0 else 0
        
        # Activated → Retained
        paying = len([u for u in self.users.values() 
                     if u.current_state in [UserState.RETAINED, UserState.AT_RISK, UserState.CHURNED]])
        rates["activated_to_paying"] = paying / activated if activated > 0 else 0
        
        return rates
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH INTEGRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_health_inputs(self) -> Dict:
        """Get inputs for health calculation."""
        dist = self.get_state_distribution()
        rates = self.get_conversion_rates()
        
        total = sum(dist.values())
        if total == 0:
            return {"health_score": 50}
        
        # Healthy states
        healthy = dist.get("engaged", 0) + dist.get("retained", 0)
        healthy_pct = healthy / total
        
        # Risk states
        at_risk = dist.get("at_risk", 0) + dist.get("dormant", 0)
        risk_pct = at_risk / total
        
        # Failed states
        failed = dist.get("bounced", 0) + dist.get("abandoned", 0) + dist.get("churned", 0)
        failed_pct = failed / total
        
        health_score = (healthy_pct * 100) - (risk_pct * 30) - (failed_pct * 20)
        
        return {
            "state_distribution": dist,
            "healthy_pct": healthy_pct,
            "risk_pct": risk_pct,
            "failed_pct": failed_pct,
            "signup_to_activated": rates.get("signup_to_activated", 0),
            "health_score": max(0, min(100, health_score)),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get lifecycle manager summary."""
        dist = self.get_state_distribution()
        return {
            "total_users": len(self.users),
            "state_distribution": dist,
            "at_risk_count": dist.get("at_risk", 0),
            "conversion_rates": self.get_conversion_rates(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_lifecycle_manager: Optional[UserLifecycleManager] = None

def get_lifecycle_manager() -> UserLifecycleManager:
    """Get the global lifecycle manager."""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = UserLifecycleManager()
    return _lifecycle_manager


# Alias for backwards compatibility
LifecycleState = UserState

__all__ = [
    "UserState",
    "LifecycleState",  # Alias
    "LifecycleThresholds", 
    "UserLifecycle",
    "UserLifecycleManager",
    "get_lifecycle_manager",
]
