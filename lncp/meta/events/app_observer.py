#!/usr/bin/env python3
"""
LNCP META: APP OBSERVER v5.1
Processes app events into actionable signals for Meta.

The App Observer:
- Collects events from the queue
- Aggregates into metrics
- Feeds other components (Activation, Lifecycle, Health)
- Generates alerts on anomalies
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum

from .schema import AppEvent, EventType, EventCategory, UserTier
from .collector import EventCollector, EventAggregator, get_event_collector


# ═══════════════════════════════════════════════════════════════════════════
# SIGNALS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AppSignals:
    """Signals derived from app events."""
    
    # Time window
    window_start: datetime
    window_end: datetime
    
    # Volume metrics
    total_events: int = 0
    unique_users: int = 0
    unique_sessions: int = 0
    
    # Onboarding metrics
    onboarding_started: int = 0
    onboarding_completed: int = 0
    onboarding_abandoned: int = 0
    onboarding_completion_rate: float = 0
    avg_onboarding_duration_seconds: float = 0
    
    # Analysis metrics
    analyses_started: int = 0
    analyses_completed: int = 0
    analysis_completion_rate: float = 0
    avg_analysis_duration_ms: float = 0
    
    # Profile engagement
    profiles_viewed: int = 0
    profiles_switched: int = 0
    profile_switch_rate: float = 0  # Indicates disagreement with prediction
    avg_profile_view_duration: float = 0
    
    # Value indicators
    results_exported: int = 0
    results_saved: int = 0
    export_rate: float = 0  # Per completed analysis
    
    # Session metrics
    sessions_started: int = 0
    sessions_ended: int = 0
    avg_session_duration: float = 0
    avg_pages_per_session: float = 0
    avg_actions_per_session: float = 0
    
    # Account metrics
    accounts_created: int = 0
    accounts_upgraded: int = 0
    accounts_churned: int = 0
    
    # Friction metrics (E11)
    help_accessed: int = 0
    support_contacted: int = 0
    errors_encountered: int = 0
    flows_abandoned: int = 0
    friction_rate: float = 0  # Friction events per session
    
    # By tier
    events_by_tier: Dict[str, int] = field(default_factory=dict)
    
    # Attribution (E1)
    sessions_with_utm: int = 0
    utm_sources: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "window": f"{self.window_start.isoformat()} to {self.window_end.isoformat()}",
            "volume": {
                "total_events": self.total_events,
                "unique_users": self.unique_users,
                "unique_sessions": self.unique_sessions,
            },
            "onboarding": {
                "started": self.onboarding_started,
                "completed": self.onboarding_completed,
                "completion_rate": f"{self.onboarding_completion_rate:.1%}",
            },
            "analysis": {
                "started": self.analyses_started,
                "completed": self.analyses_completed,
                "completion_rate": f"{self.analysis_completion_rate:.1%}",
            },
            "engagement": {
                "profiles_viewed": self.profiles_viewed,
                "profile_switch_rate": f"{self.profile_switch_rate:.1%}",
                "export_rate": f"{self.export_rate:.1%}",
            },
            "sessions": {
                "avg_duration": f"{self.avg_session_duration:.0f}s",
                "avg_pages": f"{self.avg_pages_per_session:.1f}",
            },
            "accounts": {
                "created": self.accounts_created,
                "upgraded": self.accounts_upgraded,
                "churned": self.accounts_churned,
            },
            "friction": {
                "help_accessed": self.help_accessed,
                "support_contacted": self.support_contacted,
                "errors": self.errors_encountered,
                "flows_abandoned": self.flows_abandoned,
                "friction_rate": f"{self.friction_rate:.2f}",
            },
            "attribution": {
                "sessions_with_utm": self.sessions_with_utm,
                "utm_sources": self.utm_sources,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# APP OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class AppObserver:
    """
    Observes app behavior through events.
    
    Responsibilities:
    - Collect events from queue
    - Calculate metrics and signals
    - Track user sessions and journeys
    - Detect anomalies
    """
    
    def __init__(self, collector: Optional[EventCollector] = None):
        self.collector = collector or get_event_collector()
        self.aggregator = EventAggregator()
        
        # Tracking
        self._last_collection: Optional[datetime] = None
        self._signals_history: List[AppSignals] = []
        
        # User state cache
        self._user_sessions: Dict[str, Dict] = {}  # user_id -> session info
        self._user_last_seen: Dict[str, datetime] = {}
    
    # ─────────────────────────────────────────────────────────────────────
    # COLLECTION
    # ─────────────────────────────────────────────────────────────────────
    
    def collect_and_process(self) -> AppSignals:
        """
        Collect new events and process into signals.
        """
        window_start = self._last_collection or (datetime.utcnow() - timedelta(hours=1))
        window_end = datetime.utcnow()
        
        # Collect events
        events = self.collector.collect()
        self.aggregator.add_all(events)
        
        # Process into signals
        signals = self._calculate_signals(events, window_start, window_end)
        
        # Update tracking
        self._last_collection = window_end
        self._signals_history.append(signals)
        
        # Keep only recent history
        if len(self._signals_history) > 100:
            self._signals_history = self._signals_history[-100:]
        
        # Update user tracking
        self._update_user_tracking(events)
        
        return signals
    
    def get_current_signals(self, hours: int = 1) -> AppSignals:
        """
        Get signals for the last N hours without collecting new events.
        """
        window_start = datetime.utcnow() - timedelta(hours=hours)
        window_end = datetime.utcnow()
        
        # Filter aggregator events to window
        events = self.aggregator.filter_by_time(window_start, window_end)
        
        return self._calculate_signals(events, window_start, window_end)
    
    # ─────────────────────────────────────────────────────────────────────
    # SIGNAL CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _calculate_signals(
        self,
        events: List[AppEvent],
        window_start: datetime,
        window_end: datetime,
    ) -> AppSignals:
        """Calculate all signals from events."""
        
        signals = AppSignals(
            window_start=window_start,
            window_end=window_end,
            total_events=len(events),
        )
        
        if not events:
            return signals
        
        # Unique counts
        signals.unique_users = len(set(e.user_id for e in events if e.user_id))
        signals.unique_sessions = len(set(e.session_id for e in events if e.session_id))
        
        # By tier
        for event in events:
            tier = event.tier.value
            signals.events_by_tier[tier] = signals.events_by_tier.get(tier, 0) + 1
        
        # Onboarding
        onboard_started = [e for e in events if e.event_type == EventType.ONBOARDING_STARTED]
        onboard_completed = [e for e in events if e.event_type == EventType.ONBOARDING_COMPLETED]
        onboard_abandoned = [e for e in events if e.event_type == EventType.ONBOARDING_ABANDONED]
        
        signals.onboarding_started = len(onboard_started)
        signals.onboarding_completed = len(onboard_completed)
        signals.onboarding_abandoned = len(onboard_abandoned)
        
        if signals.onboarding_started > 0:
            signals.onboarding_completion_rate = signals.onboarding_completed / signals.onboarding_started
        
        if onboard_completed:
            durations = [e.payload.get("total_duration_seconds", 0) for e in onboard_completed]
            signals.avg_onboarding_duration_seconds = sum(durations) / len(durations)
        
        # Analysis
        analysis_started = [e for e in events if e.event_type == EventType.ANALYSIS_STARTED]
        analysis_completed = [e for e in events if e.event_type == EventType.ANALYSIS_COMPLETED]
        
        signals.analyses_started = len(analysis_started)
        signals.analyses_completed = len(analysis_completed)
        
        if signals.analyses_started > 0:
            signals.analysis_completion_rate = signals.analyses_completed / signals.analyses_started
        
        if analysis_completed:
            durations = [e.payload.get("duration_ms", 0) for e in analysis_completed]
            signals.avg_analysis_duration_ms = sum(durations) / len(durations)
        
        # Profile engagement
        profile_viewed = [e for e in events if e.event_type == EventType.PROFILE_VIEWED]
        profile_switched = [e for e in events if e.event_type == EventType.PROFILE_SWITCHED]
        
        signals.profiles_viewed = len(profile_viewed)
        signals.profiles_switched = len(profile_switched)
        
        if signals.analyses_completed > 0:
            signals.profile_switch_rate = signals.profiles_switched / signals.analyses_completed
        
        if profile_viewed:
            durations = [e.payload.get("view_duration_seconds", 0) for e in profile_viewed]
            signals.avg_profile_view_duration = sum(durations) / len(durations)
        
        # Value indicators
        result_exported = [e for e in events if e.event_type == EventType.RESULT_EXPORTED]
        result_saved = [e for e in events if e.event_type == EventType.RESULT_SAVED]
        
        signals.results_exported = len(result_exported)
        signals.results_saved = len(result_saved)
        
        if signals.analyses_completed > 0:
            signals.export_rate = (signals.results_exported + signals.results_saved) / signals.analyses_completed
        
        # Sessions
        session_started = [e for e in events if e.event_type == EventType.SESSION_STARTED]
        session_ended = [e for e in events if e.event_type == EventType.SESSION_ENDED]
        
        signals.sessions_started = len(session_started)
        signals.sessions_ended = len(session_ended)
        
        if session_ended:
            durations = [e.payload.get("duration_seconds", 0) for e in session_ended]
            pages = [e.payload.get("pages_viewed", 0) for e in session_ended]
            actions = [e.payload.get("actions_taken", 0) for e in session_ended]
            
            signals.avg_session_duration = sum(durations) / len(durations)
            signals.avg_pages_per_session = sum(pages) / len(pages)
            signals.avg_actions_per_session = sum(actions) / len(actions)
        
        # Accounts
        signals.accounts_created = len([e for e in events if e.event_type == EventType.ACCOUNT_CREATED])
        signals.accounts_upgraded = len([e for e in events if e.event_type == EventType.ACCOUNT_UPGRADED])
        signals.accounts_churned = len([e for e in events if e.event_type == EventType.ACCOUNT_CHURNED])
        
        # Friction (E11)
        signals.help_accessed = len([e for e in events if e.event_type == EventType.HELP_ACCESSED])
        signals.support_contacted = len([e for e in events if e.event_type == EventType.SUPPORT_CONTACTED])
        signals.errors_encountered = len([e for e in events if e.event_type == EventType.ERROR_ENCOUNTERED])
        signals.flows_abandoned = len([e for e in events if e.event_type == EventType.FLOW_ABANDONED])
        
        total_friction = (signals.help_accessed + signals.support_contacted + 
                         signals.errors_encountered + signals.flows_abandoned)
        if signals.sessions_started > 0:
            signals.friction_rate = total_friction / signals.sessions_started
        
        # Attribution (E1)
        for session in session_started:
            utm_source = session.payload.get("utm_source")
            if utm_source:
                signals.sessions_with_utm += 1
                signals.utm_sources[utm_source] = signals.utm_sources.get(utm_source, 0) + 1
        
        return signals
    
    # ─────────────────────────────────────────────────────────────────────
    # USER TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def _update_user_tracking(self, events: List[AppEvent]):
        """Update user tracking from events."""
        for event in events:
            if not event.user_id:
                continue
            
            self._user_last_seen[event.user_id] = event.timestamp
            
            # Track session info
            if event.event_type == EventType.SESSION_STARTED:
                self._user_sessions[event.user_id] = {
                    "session_id": event.session_id,
                    "started_at": event.timestamp,
                    "events": 0,
                }
            
            if event.user_id in self._user_sessions:
                self._user_sessions[event.user_id]["events"] += 1
    
    def get_active_users(self, minutes: int = 30) -> Set[str]:
        """Get users active in the last N minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return {
            user_id for user_id, last_seen in self._user_last_seen.items()
            if last_seen >= cutoff
        }
    
    def get_user_activity(self, user_id: str) -> Dict:
        """Get activity summary for a user."""
        events = [e for e in self.aggregator.events if e.user_id == user_id]
        
        if not events:
            return {"user_id": user_id, "events": 0}
        
        return {
            "user_id": user_id,
            "events": len(events),
            "first_seen": min(e.timestamp for e in events).isoformat(),
            "last_seen": max(e.timestamp for e in events).isoformat(),
            "event_types": list(set(e.event_type.value for e in events)),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH INTEGRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_health_inputs(self) -> Dict:
        """Get inputs for health calculator."""
        signals = self.get_current_signals(hours=24)
        
        # Calculate health indicators
        onboard_health = signals.onboarding_completion_rate * 100
        analysis_health = signals.analysis_completion_rate * 100
        engagement_health = min(100, signals.avg_actions_per_session * 10)
        
        # Profile accuracy proxy (low switch rate = good)
        accuracy_health = max(0, 100 - (signals.profile_switch_rate * 200))
        
        # Friction penalty (E11) - high friction reduces health
        friction_penalty = min(20, signals.friction_rate * 10)
        
        base_health = (onboard_health + analysis_health + engagement_health + accuracy_health) / 4
        
        return {
            "onboarding_completion_rate": signals.onboarding_completion_rate,
            "analysis_completion_rate": signals.analysis_completion_rate,
            "profile_switch_rate": signals.profile_switch_rate,
            "export_rate": signals.export_rate,
            "avg_session_duration": signals.avg_session_duration,
            # Friction signals (E11)
            "friction_rate": signals.friction_rate,
            "help_access_rate": signals.help_accessed / signals.sessions_started if signals.sessions_started > 0 else 0,
            "error_rate": signals.errors_encountered / signals.sessions_started if signals.sessions_started > 0 else 0,
            # Attribution (E1)
            "utm_attribution_rate": signals.sessions_with_utm / signals.sessions_started if signals.sessions_started > 0 else 0,
            "top_utm_sources": dict(sorted(signals.utm_sources.items(), key=lambda x: x[1], reverse=True)[:5]),
            # Health
            "health_score": max(0, base_health - friction_penalty),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get observer summary."""
        queue_stats = self.collector.get_queue_stats()
        
        return {
            "events_in_memory": len(self.aggregator.events),
            "unique_users_tracked": len(self._user_last_seen),
            "active_sessions": len(self._user_sessions),
            "signals_history": len(self._signals_history),
            "last_collection": self._last_collection.isoformat() if self._last_collection else None,
            "queue": queue_stats,
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_app_observer: Optional[AppObserver] = None

def get_app_observer() -> AppObserver:
    """Get the global app observer instance."""
    global _app_observer
    if _app_observer is None:
        _app_observer = AppObserver()
    return _app_observer


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "AppSignals",
    "AppObserver",
    "get_app_observer",
]
