#!/usr/bin/env python3
"""
LNCP META: ACTIVATION TRACKER v5.1
Tracks user activation - the moment they get enough value to likely retain.

Activation Definition (Composite):
  User is "activated" when:
  1. Completed at least one analysis, AND
  2. Either viewed profile for 30s+ OR exported/saved result
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from .events import EventType, AppEvent, UserTier, get_event_collector


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ActivationCriteria:
    """Configurable activation criteria."""
    min_analyses: int = 1
    profile_view_threshold_seconds: float = 30
    export_counts_as_engagement: bool = True
    save_counts_as_engagement: bool = True
    activation_window_hours: int = 168  # 7 days


class ActivationStatus(str, Enum):
    PENDING = "pending"
    ACTIVATED = "activated"
    EXPIRED = "expired"


@dataclass
class UserActivation:
    """Activation tracking for a single user."""
    user_id: str
    signup_timestamp: datetime
    tier: UserTier
    status: ActivationStatus = ActivationStatus.PENDING
    activated_at: Optional[datetime] = None
    analyses_completed: int = 0
    total_profile_view_seconds: float = 0
    has_exported: bool = False
    has_saved: bool = False
    hours_to_activation: Optional[float] = None
    signup_source: Optional[str] = None
    signup_date: str = ""
    
    @property
    def has_analysis(self) -> bool:
        return self.analyses_completed >= 1
    
    @property
    def has_engagement(self) -> bool:
        return self.total_profile_view_seconds >= 30 or self.has_exported or self.has_saved
    
    def check_activation(self, criteria: ActivationCriteria) -> bool:
        if self.status == ActivationStatus.ACTIVATED:
            return True
        if self.analyses_completed < criteria.min_analyses:
            return False
        engaged = (
            self.total_profile_view_seconds >= criteria.profile_view_threshold_seconds or
            (criteria.export_counts_as_engagement and self.has_exported) or
            (criteria.save_counts_as_engagement and self.has_saved)
        )
        return engaged


class ActivationTracker:
    """Tracks user activation across the user base."""
    
    def __init__(self, criteria: Optional[ActivationCriteria] = None):
        self.criteria = criteria or ActivationCriteria()
        self.users: Dict[str, UserActivation] = {}
        self._activation_times: List[float] = []
    
    def process_events(self, events: List[AppEvent]):
        """Process events to update activation status."""
        for event in sorted(events, key=lambda e: e.timestamp):
            self._process_event(event)
        self._check_expirations()
    
    def _process_event(self, event: AppEvent):
        if event.event_type == EventType.ACCOUNT_CREATED:
            self._handle_signup(event)
        elif event.event_type == EventType.ANALYSIS_COMPLETED:
            self._handle_analysis(event)
        elif event.event_type == EventType.PROFILE_VIEWED:
            self._handle_profile_view(event)
        elif event.event_type == EventType.RESULT_EXPORTED:
            self._handle_export(event)
        elif event.event_type == EventType.RESULT_SAVED:
            self._handle_save(event)
    
    def _handle_signup(self, event: AppEvent):
        if not event.user_id:
            return
        self.users[event.user_id] = UserActivation(
            user_id=event.user_id,
            signup_timestamp=event.timestamp,
            tier=event.tier,
            signup_source=event.payload.get("source"),
            signup_date=event.timestamp.strftime("%Y-%m-%d"),
        )
    
    def _handle_analysis(self, event: AppEvent):
        if not event.user_id:
            return
        user = self._ensure_user(event)
        if user.status == ActivationStatus.ACTIVATED:
            return
        user.analyses_completed += 1
        self._check_activation(user, event.timestamp)
    
    def _handle_profile_view(self, event: AppEvent):
        if not event.user_id:
            return
        user = self._ensure_user(event)
        if user.status == ActivationStatus.ACTIVATED:
            return
        user.total_profile_view_seconds += event.payload.get("view_duration_seconds", 0)
        self._check_activation(user, event.timestamp)
    
    def _handle_export(self, event: AppEvent):
        if not event.user_id:
            return
        user = self._ensure_user(event)
        if user.status == ActivationStatus.ACTIVATED:
            return
        user.has_exported = True
        self._check_activation(user, event.timestamp)
    
    def _handle_save(self, event: AppEvent):
        if not event.user_id:
            return
        user = self._ensure_user(event)
        if user.status == ActivationStatus.ACTIVATED:
            return
        user.has_saved = True
        self._check_activation(user, event.timestamp)
    
    def _ensure_user(self, event: AppEvent) -> UserActivation:
        if event.user_id not in self.users:
            self.users[event.user_id] = UserActivation(
                user_id=event.user_id,
                signup_timestamp=event.timestamp,
                tier=event.tier,
                signup_date=event.timestamp.strftime("%Y-%m-%d"),
            )
        return self.users[event.user_id]
    
    def _check_activation(self, user: UserActivation, event_time: datetime):
        if user.status != ActivationStatus.PENDING:
            return
        if user.check_activation(self.criteria):
            user.status = ActivationStatus.ACTIVATED
            user.activated_at = event_time
            user.hours_to_activation = (event_time - user.signup_timestamp).total_seconds() / 3600
            self._activation_times.append(user.hours_to_activation)
    
    def _check_expirations(self):
        cutoff = datetime.utcnow() - timedelta(hours=self.criteria.activation_window_hours)
        for user in self.users.values():
            if user.status == ActivationStatus.PENDING and user.signup_timestamp < cutoff:
                user.status = ActivationStatus.EXPIRED
    
    def get_activation_rate(self) -> float:
        if not self.users:
            return 0
        activated = len([u for u in self.users.values() if u.status == ActivationStatus.ACTIVATED])
        total = len([u for u in self.users.values() if u.status != ActivationStatus.PENDING])
        return activated / total if total > 0 else 0
    
    def get_activation_rate_by_tier(self) -> Dict[str, float]:
        by_tier: Dict[str, Tuple[int, int]] = {}
        for user in self.users.values():
            if user.status == ActivationStatus.PENDING:
                continue
            tier = user.tier.value
            if tier not in by_tier:
                by_tier[tier] = (0, 0)
            activated, total = by_tier[tier]
            total += 1
            if user.status == ActivationStatus.ACTIVATED:
                activated += 1
            by_tier[tier] = (activated, total)
        return {t: a / n if n > 0 else 0 for t, (a, n) in by_tier.items()}
    
    def get_median_time_to_activation(self) -> Optional[float]:
        if not self._activation_times:
            return None
        return statistics.median(self._activation_times)
    
    def get_activation_funnel(self) -> Dict:
        total = len(self.users)
        if total == 0:
            return {}
        has_analysis = len([u for u in self.users.values() if u.has_analysis])
        has_engagement = len([u for u in self.users.values() if u.has_engagement])
        activated = len([u for u in self.users.values() if u.status == ActivationStatus.ACTIVATED])
        return {
            "total_users": total,
            "has_analysis": has_analysis,
            "has_analysis_pct": has_analysis / total,
            "has_engagement": has_engagement,
            "has_engagement_pct": has_engagement / total,
            "activated": activated,
            "activated_pct": activated / total,
        }
    
    def get_bottleneck(self) -> str:
        funnel = self.get_activation_funnel()
        if not funnel:
            return "no_data"
        analysis_drop = 1 - funnel.get("has_analysis_pct", 0)
        engagement_drop = funnel.get("has_analysis_pct", 0) - funnel.get("has_engagement_pct", 0)
        return "analysis" if analysis_drop > engagement_drop else "engagement"
    
    def get_health_inputs(self) -> Dict:
        rate = self.get_activation_rate()
        median_time = self.get_median_time_to_activation()
        activation_health = min(100, (rate / 0.3) * 100)
        time_penalty = 0
        if median_time and median_time > 24:
            time_penalty = min(20, (median_time - 24) / 24 * 10)
        return {
            "activation_rate": rate,
            "median_hours_to_activation": median_time,
            "bottleneck": self.get_bottleneck(),
            "health_score": max(0, activation_health - time_penalty),
        }
    
    def get_summary(self) -> Dict:
        return {
            "total_users": len(self.users),
            "activated": len([u for u in self.users.values() if u.status == ActivationStatus.ACTIVATED]),
            "pending": len([u for u in self.users.values() if u.status == ActivationStatus.PENDING]),
            "expired": len([u for u in self.users.values() if u.status == ActivationStatus.EXPIRED]),
            "activation_rate": f"{self.get_activation_rate():.1%}",
            "median_hours": self.get_median_time_to_activation(),
            "bottleneck": self.get_bottleneck(),
        }


_activation_tracker: Optional[ActivationTracker] = None

def get_activation_tracker() -> ActivationTracker:
    global _activation_tracker
    if _activation_tracker is None:
        _activation_tracker = ActivationTracker()
    return _activation_tracker


__all__ = ["ActivationCriteria", "ActivationStatus", "UserActivation", 
           "ActivationTracker", "get_activation_tracker"]
