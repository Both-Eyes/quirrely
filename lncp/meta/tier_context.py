#!/usr/bin/env python3
"""
LNCP META: TIER CONTEXT v5.1
Tier-aware optimization with different targets per user segment.

Tier Strategy:
- FREE: Maximize activation and upgrade intent
- TRIAL: Maximize conversion to paid  
- PRO: Maximize retention and expansion
- ENTERPRISE: Maximize satisfaction and referrals

This module provides:
- Tier-segmented metrics
- Tier-aware trust scoring
- Tier-specific proposal evaluation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .events import EventType, AppEvent, UserTier


# ═══════════════════════════════════════════════════════════════════════════
# TIER OPTIMIZATION TARGETS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TierTargets:
    """Optimization targets for a tier."""
    
    tier: UserTier
    
    # Primary KPI
    primary_metric: str
    primary_target: float
    
    # Secondary metrics
    secondary_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Weights for proposal evaluation
    retention_weight: float = 0.5
    activation_weight: float = 0.3
    expansion_weight: float = 0.2


# Default targets per tier
TIER_TARGETS: Dict[UserTier, TierTargets] = {
    UserTier.FREE: TierTargets(
        tier=UserTier.FREE,
        primary_metric="activation_rate",
        primary_target=0.30,  # 30% should activate
        secondary_metrics={
            "upgrade_intent": 0.10,  # 10% show upgrade intent
            "return_rate": 0.40,     # 40% return within 7 days
        },
        activation_weight=0.6,
        retention_weight=0.2,
        expansion_weight=0.2,
    ),
    UserTier.TRIAL: TierTargets(
        tier=UserTier.TRIAL,
        primary_metric="trial_conversion",
        primary_target=0.25,  # 25% convert to paid
        secondary_metrics={
            "feature_adoption": 0.60,  # 60% try key features
            "activation_rate": 0.50,   # 50% should activate
        },
        activation_weight=0.4,
        retention_weight=0.2,
        expansion_weight=0.4,
    ),
    UserTier.PRO: TierTargets(
        tier=UserTier.PRO,
        primary_metric="retention_rate",
        primary_target=0.95,  # 95% monthly retention
        secondary_metrics={
            "nps_score": 50,           # NPS of 50+
            "expansion_rate": 0.05,    # 5% upgrade/expand
        },
        retention_weight=0.6,
        activation_weight=0.1,
        expansion_weight=0.3,
    ),
    UserTier.ENTERPRISE: TierTargets(
        tier=UserTier.ENTERPRISE,
        primary_metric="retention_rate",
        primary_target=0.98,  # 98% retention
        secondary_metrics={
            "nps_score": 70,           # NPS of 70+
            "referral_rate": 0.10,     # 10% refer others
        },
        retention_weight=0.7,
        activation_weight=0.0,
        expansion_weight=0.3,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# TIER METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TierMetrics:
    """Metrics for a specific tier."""
    
    tier: UserTier
    
    # Counts
    total_users: int = 0
    active_users: int = 0
    
    # Engagement
    avg_sessions_per_user: float = 0
    avg_analyses_per_user: float = 0
    
    # Conversion/Retention
    activation_rate: float = 0
    retention_rate: float = 0
    churn_rate: float = 0
    
    # Target performance
    primary_metric_value: float = 0
    primary_metric_target: float = 0
    target_achievement: float = 0  # % of target achieved
    
    def to_dict(self) -> Dict:
        return {
            "tier": self.tier.value,
            "users": self.total_users,
            "active": self.active_users,
            "activation_rate": f"{self.activation_rate:.1%}",
            "retention_rate": f"{self.retention_rate:.1%}",
            "target_achievement": f"{self.target_achievement:.1%}",
        }


# ═══════════════════════════════════════════════════════════════════════════
# TIER-AWARE TRUST
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TierTrustScore:
    """Trust score for an action type, segmented by tier."""
    
    action_type: str
    
    # Per-tier trust
    tier_scores: Dict[UserTier, float] = field(default_factory=dict)
    tier_event_counts: Dict[UserTier, int] = field(default_factory=dict)
    
    def get_score(self, tier: UserTier) -> float:
        """Get trust score for a tier."""
        return self.tier_scores.get(tier, 0)
    
    def record_outcome(self, tier: UserTier, success: bool, weight: float = 1.0):
        """Record an outcome for a tier."""
        current = self.tier_scores.get(tier, 0)
        count = self.tier_event_counts.get(tier, 0)
        
        # Simple weighted average
        value = weight if success else -weight
        new_score = (current * count + value) / (count + 1)
        
        self.tier_scores[tier] = new_score
        self.tier_event_counts[tier] = count + 1
    
    def should_apply_for_tier(self, tier: UserTier, threshold: float = 0) -> bool:
        """Check if action should auto-apply for this tier."""
        score = self.get_score(tier)
        count = self.tier_event_counts.get(tier, 0)
        
        # Need enough data AND positive score
        return count >= 5 and score >= threshold


# ═══════════════════════════════════════════════════════════════════════════
# TIER CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class TierContextManager:
    """
    Manages tier-aware optimization context.
    
    Responsibilities:
    - Track metrics per tier
    - Provide tier context for proposals
    - Evaluate actions against tier targets
    """
    
    def __init__(self):
        self.targets = TIER_TARGETS.copy()
        self.metrics: Dict[UserTier, TierMetrics] = {}
        self.tier_trust: Dict[str, TierTrustScore] = {}
        
        # User tier tracking
        self._user_tiers: Dict[str, UserTier] = {}
        self._tier_users: Dict[UserTier, set] = {t: set() for t in UserTier}
    
    # ─────────────────────────────────────────────────────────────────────
    # USER TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def set_user_tier(self, user_id: str, tier: UserTier):
        """Update user's tier."""
        old_tier = self._user_tiers.get(user_id)
        if old_tier:
            self._tier_users[old_tier].discard(user_id)
        
        self._user_tiers[user_id] = tier
        self._tier_users[tier].add(user_id)
    
    def get_user_tier(self, user_id: str) -> UserTier:
        """Get user's tier."""
        return self._user_tiers.get(user_id, UserTier.FREE)
    
    def get_users_in_tier(self, tier: UserTier) -> set:
        """Get all users in a tier."""
        return self._tier_users[tier].copy()
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT PROCESSING
    # ─────────────────────────────────────────────────────────────────────
    
    def process_events(self, events: List[AppEvent]):
        """Process events to update tier context."""
        for event in events:
            if event.user_id:
                self.set_user_tier(event.user_id, event.tier)
            
            # Track tier changes
            if event.event_type == EventType.ACCOUNT_UPGRADED:
                if event.user_id:
                    new_tier = UserTier(event.payload.get("to_tier", "pro"))
                    self.set_user_tier(event.user_id, new_tier)
    
    # ─────────────────────────────────────────────────────────────────────
    # TIER TRUST
    # ─────────────────────────────────────────────────────────────────────
    
    def record_action_outcome(
        self,
        action_type: str,
        tier: UserTier,
        success: bool,
        impact: float = 1.0,
    ):
        """Record action outcome for tier-specific trust."""
        if action_type not in self.tier_trust:
            self.tier_trust[action_type] = TierTrustScore(action_type=action_type)
        
        self.tier_trust[action_type].record_outcome(tier, success, impact)
    
    def get_tier_trust(self, action_type: str, tier: UserTier) -> float:
        """Get trust score for action type + tier combination."""
        if action_type not in self.tier_trust:
            return 0
        return self.tier_trust[action_type].get_score(tier)
    
    def should_auto_apply(self, action_type: str, tier: UserTier) -> bool:
        """Check if action should auto-apply for this tier."""
        if action_type not in self.tier_trust:
            return False
        return self.tier_trust[action_type].should_apply_for_tier(tier)
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL EVALUATION
    # ─────────────────────────────────────────────────────────────────────
    
    def evaluate_proposal_impact(
        self,
        expected_impacts: Dict[str, float],
        affected_tiers: List[UserTier],
    ) -> Dict:
        """
        Evaluate a proposal's impact considering tier targets.
        
        Returns tier breakdown and recommendation.
        """
        evaluation = {
            "tier_impacts": {},
            "overall_score": 0,
            "recommendation": "neutral",
            "concerns": [],
        }
        
        total_weight = 0
        weighted_score = 0
        
        for tier in affected_tiers:
            if tier not in self.targets:
                continue
            
            targets = self.targets[tier]
            tier_score = 0
            
            # Check impact on primary metric
            primary_impact = expected_impacts.get(targets.primary_metric, 0)
            if primary_impact > 0:
                tier_score += 0.5
            elif primary_impact < 0:
                tier_score -= 0.5
                evaluation["concerns"].append(
                    f"Negative impact on {tier.value} primary metric ({targets.primary_metric})"
                )
            
            # Weight by tier value (higher tiers matter more for revenue)
            tier_weight = {
                UserTier.FREE: 0.1,
                UserTier.TRIAL: 0.2,
                UserTier.PRO: 0.5,
                UserTier.ENTERPRISE: 0.2,
            }.get(tier, 0.1)
            
            evaluation["tier_impacts"][tier.value] = {
                "score": tier_score,
                "weight": tier_weight,
                "primary_impact": primary_impact,
            }
            
            weighted_score += tier_score * tier_weight
            total_weight += tier_weight
        
        if total_weight > 0:
            evaluation["overall_score"] = weighted_score / total_weight
        
        # Recommendation
        if evaluation["overall_score"] > 0.3:
            evaluation["recommendation"] = "approve"
        elif evaluation["overall_score"] < -0.2:
            evaluation["recommendation"] = "reject"
        else:
            evaluation["recommendation"] = "review"
        
        return evaluation
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS
    # ─────────────────────────────────────────────────────────────────────
    
    def calculate_tier_metrics(
        self,
        activation_rates: Dict[str, float],
        retention_data: Dict,
    ) -> Dict[UserTier, TierMetrics]:
        """Calculate metrics for each tier."""
        for tier in UserTier:
            if tier == UserTier.ANONYMOUS:
                continue
            
            users = self._tier_users[tier]
            targets = self.targets.get(tier)
            
            metrics = TierMetrics(
                tier=tier,
                total_users=len(users),
                activation_rate=activation_rates.get(tier.value, 0),
            )
            
            if targets:
                metrics.primary_metric_target = targets.primary_target
                metrics.primary_metric_value = activation_rates.get(tier.value, 0)
                if targets.primary_target > 0:
                    metrics.target_achievement = metrics.primary_metric_value / targets.primary_target
            
            self.metrics[tier] = metrics
        
        return self.metrics
    
    def get_underperforming_tiers(self, threshold: float = 0.8) -> List[UserTier]:
        """Get tiers performing below target threshold."""
        underperforming = []
        
        for tier, metrics in self.metrics.items():
            if metrics.target_achievement < threshold:
                underperforming.append(tier)
        
        return underperforming
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH INTEGRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_health_inputs(self) -> Dict:
        """Get inputs for health calculation."""
        tier_health = {}
        
        for tier, metrics in self.metrics.items():
            tier_health[tier.value] = {
                "users": metrics.total_users,
                "target_achievement": metrics.target_achievement,
            }
        
        # Overall tier health is weighted average
        total_users = sum(m.total_users for m in self.metrics.values())
        if total_users > 0:
            weighted_achievement = sum(
                m.target_achievement * m.total_users 
                for m in self.metrics.values()
            ) / total_users
        else:
            weighted_achievement = 0
        
        return {
            "tier_health": tier_health,
            "overall_target_achievement": weighted_achievement,
            "underperforming_tiers": [t.value for t in self.get_underperforming_tiers()],
            "health_score": weighted_achievement * 100,
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get tier context summary."""
        return {
            "users_by_tier": {t.value: len(u) for t, u in self._tier_users.items()},
            "action_types_tracked": len(self.tier_trust),
            "metrics_calculated": len(self.metrics),
            "underperforming": [t.value for t in self.get_underperforming_tiers()],
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_tier_manager: Optional[TierContextManager] = None

def get_tier_manager() -> TierContextManager:
    """Get the global tier context manager."""
    global _tier_manager
    if _tier_manager is None:
        _tier_manager = TierContextManager()
    return _tier_manager


__all__ = [
    "TierTargets",
    "TIER_TARGETS",
    "TierMetrics",
    "TierTrustScore",
    "TierContextManager",
    "get_tier_manager",
]
