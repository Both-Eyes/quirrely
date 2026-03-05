#!/usr/bin/env python3
"""
LNCP META: RETENTION OBSERVER v1.0.0
Tracks and optimizes the P1 Downgrade Prevention system.

This observer monitors:
- Churn intent signals
- Retention intervention outcomes
- Pause/downgrade/save rates
- MRR saved through interventions
- Win-back effectiveness

It provides:
- Real-time retention metrics
- Churn health scoring
- Intervention optimization suggestions
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# RETENTION ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class ChurnIntent(str, Enum):
    """Types of churn intent signals."""
    CANCEL_CLICKED = "cancel_clicked"
    BILLING_PAGE_VISITED = "billing_page_visited"
    DOWNGRADE_EXPLORED = "downgrade_explored"
    SUPPORT_CONTACTED = "support_contacted"
    LOW_USAGE = "low_usage"
    PAYMENT_FAILED = "payment_failed"


class InterventionType(str, Enum):
    """Types of retention interventions."""
    PAUSE_OFFER = "pause_offer"
    DOWNGRADE_OFFER = "downgrade_offer"
    SAVE_OFFER_50 = "save_offer_50"      # 50% discount
    WIN_BACK_EMAIL = "win_back_email"
    ENGAGEMENT_PROMPT = "engagement_prompt"


class InterventionOutcome(str, Enum):
    """Outcomes of retention interventions."""
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IGNORED = "ignored"
    CONVERTED_LATER = "converted_later"


# ═══════════════════════════════════════════════════════════════════════════
# RETENTION METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class InterventionMetrics:
    """Metrics for a specific intervention type."""
    intervention_type: InterventionType
    
    # Offer stats
    offers_shown: int = 0
    offers_accepted: int = 0
    offers_declined: int = 0
    offers_ignored: int = 0
    
    # Rates
    acceptance_rate: float = 0.0
    decline_rate: float = 0.0
    
    # MRR impact
    mrr_at_risk: float = 0.0
    mrr_saved: float = 0.0
    save_rate: float = 0.0
    
    # Timing
    avg_response_time_seconds: float = 0.0


@dataclass
class ChurnIntentMetrics:
    """Metrics for churn intent detection."""
    # Signals
    total_signals_24h: int = 0
    total_signals_7d: int = 0
    
    # By type
    cancel_clicks: int = 0
    billing_visits: int = 0
    downgrade_explores: int = 0
    support_contacts: int = 0
    low_usage_flags: int = 0
    payment_failures: int = 0
    
    # Conversion to actual churn
    signals_to_churn_rate: float = 0.0


@dataclass
class RetentionHealth:
    """Overall retention system health."""
    # Scores (0-100)
    overall_score: float = 0.0
    intervention_effectiveness: float = 0.0
    churn_prevention_rate: float = 0.0
    
    # MRR
    mrr_at_risk_30d: float = 0.0
    mrr_saved_30d: float = 0.0
    mrr_lost_30d: float = 0.0
    net_mrr_impact: float = 0.0
    
    # User counts
    users_at_risk: int = 0
    users_saved: int = 0
    users_paused: int = 0
    users_downgraded: int = 0
    users_churned: int = 0
    
    # Rates
    save_rate: float = 0.0        # % of at-risk saved
    pause_rate: float = 0.0       # % choosing pause
    downgrade_rate: float = 0.0   # % choosing downgrade
    cancel_rate: float = 0.0      # % proceeding to cancel
    
    # Issues
    issues: List[str] = field(default_factory=list)
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# RETENTION OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class RetentionObserver:
    """
    Observes and optimizes the P1 Downgrade Prevention system.
    
    Responsibilities:
    1. Track churn intent signals
    2. Monitor intervention outcomes
    3. Calculate MRR saved
    4. Measure retention health
    5. Suggest intervention optimizations
    """
    
    def __init__(self):
        # Intervention configuration
        self.interventions = {
            InterventionType.PAUSE_OFFER: {
                "name": "Pause Subscription",
                "description": "1-3 month pause, keep data",
                "mrr_impact": 0,  # Temporary zero
                "priority": 1,
            },
            InterventionType.DOWNGRADE_OFFER: {
                "name": "Downgrade Tier",
                "description": "Move to lower tier",
                "mrr_impact": -0.4,  # Avg 40% reduction
                "priority": 2,
            },
            InterventionType.SAVE_OFFER_50: {
                "name": "Stay & Save 50%",
                "description": "50% off next 3 months",
                "mrr_impact": -0.5,  # 50% reduction
                "priority": 3,
            },
        }
        
        # Storage
        self._intent_events: List[Dict] = []
        self._intervention_events: List[Dict] = []
        self._outcome_events: List[Dict] = []
        self._churn_events: List[Dict] = []
        
        # Cached metrics
        self._last_health: Optional[RetentionHealth] = None
        self._last_calculated: Optional[datetime] = None
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_churn_intent(
        self,
        user_id: str,
        intent_type: ChurnIntent,
        mrr_at_risk: float,
        tier: str,
        days_as_customer: int = 0
    ) -> None:
        """Track a churn intent signal."""
        self._intent_events.append({
            "user_id": user_id,
            "intent_type": intent_type.value,
            "mrr_at_risk": mrr_at_risk,
            "tier": tier,
            "days_as_customer": days_as_customer,
            "timestamp": datetime.utcnow(),
        })
    
    def track_intervention_shown(
        self,
        user_id: str,
        intervention_type: InterventionType,
        mrr_at_risk: float,
        context: Optional[Dict] = None
    ) -> str:
        """Track an intervention being shown. Returns intervention_id."""
        intervention_id = f"int_{user_id}_{datetime.utcnow().timestamp()}"
        
        self._intervention_events.append({
            "intervention_id": intervention_id,
            "user_id": user_id,
            "intervention_type": intervention_type.value,
            "mrr_at_risk": mrr_at_risk,
            "context": context or {},
            "shown_at": datetime.utcnow(),
            "outcome": None,
            "outcome_at": None,
        })
        
        return intervention_id
    
    def track_intervention_outcome(
        self,
        intervention_id: str,
        outcome: InterventionOutcome,
        mrr_saved: float = 0,
        response_time_seconds: float = 0
    ) -> None:
        """Track the outcome of an intervention."""
        # Find and update intervention
        for event in self._intervention_events:
            if event.get("intervention_id") == intervention_id:
                event["outcome"] = outcome.value
                event["outcome_at"] = datetime.utcnow()
                event["mrr_saved"] = mrr_saved
                event["response_time_seconds"] = response_time_seconds
                break
        
        self._outcome_events.append({
            "intervention_id": intervention_id,
            "outcome": outcome.value,
            "mrr_saved": mrr_saved,
            "response_time_seconds": response_time_seconds,
            "timestamp": datetime.utcnow(),
        })
    
    def track_pause_accepted(
        self,
        user_id: str,
        pause_months: int,
        mrr_paused: float
    ) -> None:
        """Track a pause being accepted."""
        self._outcome_events.append({
            "user_id": user_id,
            "type": "pause_accepted",
            "pause_months": pause_months,
            "mrr_paused": mrr_paused,
            "timestamp": datetime.utcnow(),
        })
    
    def track_downgrade_accepted(
        self,
        user_id: str,
        from_tier: str,
        to_tier: str,
        mrr_before: float,
        mrr_after: float
    ) -> None:
        """Track a downgrade being accepted."""
        self._outcome_events.append({
            "user_id": user_id,
            "type": "downgrade_accepted",
            "from_tier": from_tier,
            "to_tier": to_tier,
            "mrr_before": mrr_before,
            "mrr_after": mrr_after,
            "mrr_retained": mrr_after,
            "timestamp": datetime.utcnow(),
        })
    
    def track_save_offer_accepted(
        self,
        user_id: str,
        discount_percent: float,
        mrr_before: float,
        mrr_discounted: float,
        duration_months: int = 3
    ) -> None:
        """Track a save offer being accepted."""
        self._outcome_events.append({
            "user_id": user_id,
            "type": "save_accepted",
            "discount_percent": discount_percent,
            "mrr_before": mrr_before,
            "mrr_discounted": mrr_discounted,
            "duration_months": duration_months,
            "timestamp": datetime.utcnow(),
        })
    
    def track_cancel_proceeded(
        self,
        user_id: str,
        mrr_lost: float,
        tier: str,
        days_as_customer: int,
        reason: Optional[str] = None
    ) -> None:
        """Track a user proceeding with cancellation."""
        self._churn_events.append({
            "user_id": user_id,
            "mrr_lost": mrr_lost,
            "tier": tier,
            "days_as_customer": days_as_customer,
            "reason": reason,
            "timestamp": datetime.utcnow(),
        })
    
    def track_win_back(
        self,
        user_id: str,
        campaign: str,
        converted: bool,
        mrr_recovered: float = 0
    ) -> None:
        """Track win-back campaign results."""
        self._outcome_events.append({
            "user_id": user_id,
            "type": "win_back",
            "campaign": campaign,
            "converted": converted,
            "mrr_recovered": mrr_recovered,
            "timestamp": datetime.utcnow(),
        })
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_intervention_metrics(
        self,
        intervention_type: InterventionType
    ) -> InterventionMetrics:
        """Get metrics for a specific intervention type."""
        events = [
            e for e in self._intervention_events
            if e.get("intervention_type") == intervention_type.value
        ]
        
        shown = len(events)
        accepted = len([e for e in events if e.get("outcome") == "accepted"])
        declined = len([e for e in events if e.get("outcome") == "declined"])
        ignored = len([e for e in events if e.get("outcome") == "ignored"])
        
        mrr_at_risk = sum(e.get("mrr_at_risk", 0) for e in events)
        mrr_saved = sum(e.get("mrr_saved", 0) for e in events if e.get("outcome") == "accepted")
        
        response_times = [
            e.get("response_time_seconds", 0) for e in events
            if e.get("response_time_seconds")
        ]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        return InterventionMetrics(
            intervention_type=intervention_type,
            offers_shown=shown,
            offers_accepted=accepted,
            offers_declined=declined,
            offers_ignored=ignored,
            acceptance_rate=accepted / shown if shown else 0,
            decline_rate=declined / shown if shown else 0,
            mrr_at_risk=mrr_at_risk,
            mrr_saved=mrr_saved,
            save_rate=mrr_saved / mrr_at_risk if mrr_at_risk else 0,
            avg_response_time_seconds=avg_response,
        )
    
    def get_churn_intent_metrics(self) -> ChurnIntentMetrics:
        """Get churn intent signal metrics."""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        events_24h = [e for e in self._intent_events if e["timestamp"] > day_ago]
        events_7d = [e for e in self._intent_events if e["timestamp"] > week_ago]
        
        return ChurnIntentMetrics(
            total_signals_24h=len(events_24h),
            total_signals_7d=len(events_7d),
            cancel_clicks=len([e for e in events_7d if e.get("intent_type") == "cancel_clicked"]),
            billing_visits=len([e for e in events_7d if e.get("intent_type") == "billing_page_visited"]),
            downgrade_explores=len([e for e in events_7d if e.get("intent_type") == "downgrade_explored"]),
            support_contacts=len([e for e in events_7d if e.get("intent_type") == "support_contacted"]),
            low_usage_flags=len([e for e in events_7d if e.get("intent_type") == "low_usage"]),
            payment_failures=len([e for e in events_7d if e.get("intent_type") == "payment_failed"]),
        )
    
    def calculate_mrr_saved(self, days: int = 30) -> Tuple[float, float, float]:
        """Calculate MRR saved, lost, and net impact over period."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Saved through interventions
        saved_events = [
            e for e in self._outcome_events
            if e["timestamp"] > cutoff and e.get("type") in ["save_accepted", "downgrade_accepted"]
        ]
        mrr_saved = sum(
            e.get("mrr_retained", 0) or e.get("mrr_discounted", 0)
            for e in saved_events
        )
        
        # Lost to churn
        churn_events = [e for e in self._churn_events if e["timestamp"] > cutoff]
        mrr_lost = sum(e.get("mrr_lost", 0) for e in churn_events)
        
        # Net
        net = mrr_saved - mrr_lost
        
        return mrr_saved, mrr_lost, net
    
    def get_health(self) -> RetentionHealth:
        """Calculate overall retention system health."""
        # Cache for 5 minutes
        if (
            self._last_health and self._last_calculated and
            datetime.utcnow() - self._last_calculated < timedelta(minutes=5)
        ):
            return self._last_health
        
        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)
        
        # MRR calculations
        mrr_saved, mrr_lost, net_impact = self.calculate_mrr_saved(30)
        
        # User counts
        intent_users = set(e["user_id"] for e in self._intent_events if e["timestamp"] > month_ago)
        churn_users = set(e["user_id"] for e in self._churn_events if e["timestamp"] > month_ago)
        
        saved_outcomes = [
            e for e in self._outcome_events
            if e["timestamp"] > month_ago and e.get("type") in ["save_accepted", "downgrade_accepted", "pause_accepted"]
        ]
        saved_users = set(e["user_id"] for e in saved_outcomes)
        
        paused_users = len([e for e in saved_outcomes if e.get("type") == "pause_accepted"])
        downgraded_users = len([e for e in saved_outcomes if e.get("type") == "downgrade_accepted"])
        
        # Rates
        total_at_risk = len(intent_users)
        save_rate = len(saved_users) / total_at_risk if total_at_risk else 0
        cancel_rate = len(churn_users) / total_at_risk if total_at_risk else 0
        
        # Intervention effectiveness
        all_interventions = [
            e for e in self._intervention_events
            if e.get("shown_at") and e["shown_at"] > month_ago
        ]
        accepted = len([e for e in all_interventions if e.get("outcome") == "accepted"])
        effectiveness = accepted / len(all_interventions) if all_interventions else 0
        
        # Overall score
        overall = (
            (save_rate * 40) +
            (effectiveness * 30) +
            ((1 - cancel_rate) * 30)
        )
        
        # Issues
        issues = []
        if save_rate < 0.3:
            issues.append("Low save rate - review intervention copy")
        if effectiveness < 0.2:
            issues.append("Low intervention acceptance - offers may not be compelling")
        if cancel_rate > 0.5:
            issues.append("High cancel rate - retention flow may be ineffective")
        
        health = RetentionHealth(
            overall_score=overall,
            intervention_effectiveness=effectiveness * 100,
            churn_prevention_rate=save_rate * 100,
            mrr_at_risk_30d=sum(e.get("mrr_at_risk", 0) for e in self._intent_events if e["timestamp"] > month_ago),
            mrr_saved_30d=mrr_saved,
            mrr_lost_30d=mrr_lost,
            net_mrr_impact=net_impact,
            users_at_risk=total_at_risk,
            users_saved=len(saved_users),
            users_paused=paused_users,
            users_downgraded=downgraded_users,
            users_churned=len(churn_users),
            save_rate=save_rate,
            pause_rate=paused_users / total_at_risk if total_at_risk else 0,
            downgrade_rate=downgraded_users / total_at_risk if total_at_risk else 0,
            cancel_rate=cancel_rate,
            issues=issues,
            calculated_at=now,
        )
        
        self._last_health = health
        self._last_calculated = now
        
        return health
    
    # ─────────────────────────────────────────────────────────────────────
    # OPTIMIZATION SUGGESTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for retention system."""
        suggestions = []
        health = self.get_health()
        
        # Intervention ordering
        pause_metrics = self.get_intervention_metrics(InterventionType.PAUSE_OFFER)
        save_metrics = self.get_intervention_metrics(InterventionType.SAVE_OFFER_50)
        
        if save_metrics.acceptance_rate > pause_metrics.acceptance_rate * 1.5:
            suggestions.append({
                "type": "intervention_order",
                "current": "pause_first",
                "suggested": "save_first",
                "reason": "Save offer has 1.5x higher acceptance rate",
                "confidence": 0.7,
                "domain": "retention",
            })
        
        # Save offer discount
        if save_metrics.acceptance_rate < 0.2 and save_metrics.offers_shown > 50:
            suggestions.append({
                "type": "discount_amount",
                "intervention": "save_offer",
                "current_discount": 50,
                "suggested_discount": 60,
                "reason": "Low acceptance rate - test higher discount",
                "confidence": 0.6,
                "domain": "retention",
            })
        
        # Pause duration options
        if health.pause_rate < 0.15 and health.users_at_risk > 20:
            suggestions.append({
                "type": "pause_options",
                "current": "1-3 months",
                "suggested": "1-6 months",
                "reason": "Low pause rate - offer longer pause periods",
                "confidence": 0.55,
                "domain": "retention",
            })
        
        # Copy optimization
        if health.intervention_effectiveness < 0.25:
            suggestions.append({
                "type": "copy_test",
                "component": "retention_header",
                "current": "Need a break?",
                "suggested": "We'd hate to see you go",
                "reason": "Low effectiveness - test emotional copy",
                "confidence": 0.5,
                "domain": "retention",
            })
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_retention_observer: Optional[RetentionObserver] = None


def get_retention_observer() -> RetentionObserver:
    """Get singleton retention observer."""
    global _retention_observer
    if _retention_observer is None:
        _retention_observer = RetentionObserver()
    return _retention_observer
