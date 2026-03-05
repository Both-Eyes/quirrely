#!/usr/bin/env python3
"""
LNCP META: UNIFIED HEALTH SCORE v4.1
Single system health metric that guides risk tolerance.

This combines all domain health signals into one number that
tells Meta how aggressive or conservative to be.

When health is high → more autonomy, faster changes
When health is low → more caution, more human review
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH LEVELS
# ═══════════════════════════════════════════════════════════════════════════

class HealthLevel(str, Enum):
    """Overall system health classification."""
    CRITICAL = "critical"     # 0-30: System in danger, pause everything
    DEGRADED = "degraded"     # 30-50: Problems detected, minimize changes
    CAUTIOUS = "cautious"     # 50-70: Some concerns, be careful
    HEALTHY = "healthy"       # 70-85: Normal operations
    OPTIMAL = "optimal"       # 85-100: Everything great, maximize autonomy


class RiskTolerance(str, Enum):
    """How much risk can Meta take?"""
    NONE = "none"             # No auto-apply, all to Super Admin
    MINIMAL = "minimal"       # Only safest actions
    MODERATE = "moderate"     # Normal operations
    ELEVATED = "elevated"     # Can be more aggressive
    MAXIMUM = "maximum"       # Full autonomy mode


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN HEALTH
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DomainHealth:
    """Health metrics for a single domain."""
    domain: str
    score: float                    # 0-100
    weight: float                   # Contribution to system health
    
    # Components
    components: Dict[str, float] = field(default_factory=dict)
    
    # Trend
    trend: float = 0.0              # Positive = improving, negative = degrading
    trend_days: int = 7             # Days used for trend calculation
    
    # Alerts
    alerts: List[str] = field(default_factory=list)
    
    # Metadata
    measured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemHealth:
    """Complete system health assessment."""
    # Overall
    score: float                    # 0-100
    level: HealthLevel
    risk_tolerance: RiskTolerance
    
    # By domain
    app_health: DomainHealth
    blog_health: DomainHealth
    revenue_health: DomainHealth
    meta_health: DomainHealth
    
    # System-wide
    trend: float                    # Overall trend
    volatility: float               # How much health fluctuates
    
    # Guidance
    auto_apply_enabled: bool
    max_actions_per_cycle: int
    review_escalation_factor: float  # Multiply normal thresholds
    
    # Alerts
    alerts: List[str] = field(default_factory=list)
    
    # Metadata
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "level": self.level.value,
            "risk_tolerance": self.risk_tolerance.value,
            "auto_apply_enabled": self.auto_apply_enabled,
            "max_actions_per_cycle": self.max_actions_per_cycle,
            "domains": {
                "app": {"score": self.app_health.score, "trend": self.app_health.trend},
                "blog": {"score": self.blog_health.score, "trend": self.blog_health.trend},
                "revenue": {"score": self.revenue_health.score, "trend": self.revenue_health.trend},
                "meta": {"score": self.meta_health.score, "trend": self.meta_health.trend},
            },
            "alerts": self.alerts,
        }


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════

class HealthCalculator:
    """
    Calculates unified system health from all domain signals.
    
    This is the single source of truth for "how is the system doing?"
    """
    
    def __init__(self):
        # Default weights (can be overridden by parameter store)
        self.weights = {
            "app": 0.40,
            "blog": 0.20,
            "revenue": 0.30,
            "meta": 0.10,
        }
        
        # Risk tolerance thresholds
        self.thresholds = {
            "critical": 30,
            "degraded": 50,
            "cautious": 70,
            "healthy": 85,
        }
        
        # Historical data for trends
        self.history: List[Tuple[datetime, float]] = []
    
    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN HEALTH CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def calculate_app_health(
        self,
        master_test_health: float,
        funnel_conversion_rate: float,
        error_rate: float,
        response_time_p95: float,
    ) -> DomainHealth:
        """Calculate app domain health."""
        components = {
            "master_test": master_test_health,
            "conversion": min(100, funnel_conversion_rate * 1000),  # Normalize
            "errors": max(0, 100 - error_rate * 100),  # Invert error rate
            "performance": max(0, 100 - (response_time_p95 / 10)),  # <1s = 90+
        }
        
        # Weighted combination
        score = (
            components["master_test"] * 0.50 +
            components["conversion"] * 0.25 +
            components["errors"] * 0.15 +
            components["performance"] * 0.10
        )
        
        alerts = []
        if components["errors"] < 90:
            alerts.append(f"Error rate elevated: {error_rate*100:.1f}%")
        if components["performance"] < 70:
            alerts.append(f"Response time slow: {response_time_p95:.0f}ms")
        
        return DomainHealth(
            domain="app",
            score=score,
            weight=self.weights["app"],
            components=components,
            alerts=alerts,
        )
    
    def calculate_blog_health(
        self,
        impressions_trend: float,     # % change vs previous period
        ctr_trend: float,             # % change
        click_to_signup_rate: float,  # Conversion rate
        pages_performing: int,        # Pages above baseline
        pages_total: int,
    ) -> DomainHealth:
        """Calculate blog domain health."""
        # Normalize trends to 0-100 scale
        impressions_score = 50 + (impressions_trend * 2)  # +25% = 100
        impressions_score = max(0, min(100, impressions_score))
        
        ctr_score = 50 + (ctr_trend * 5)  # +10% = 100
        ctr_score = max(0, min(100, ctr_score))
        
        conversion_score = min(100, click_to_signup_rate * 2000)  # 5% = 100
        
        coverage_score = (pages_performing / max(1, pages_total)) * 100
        
        components = {
            "impressions": impressions_score,
            "ctr": ctr_score,
            "conversion": conversion_score,
            "coverage": coverage_score,
        }
        
        score = (
            components["impressions"] * 0.30 +
            components["ctr"] * 0.30 +
            components["conversion"] * 0.25 +
            components["coverage"] * 0.15
        )
        
        alerts = []
        if impressions_trend < -10:
            alerts.append(f"Impressions declining: {impressions_trend:.1f}%")
        if ctr_trend < -5:
            alerts.append(f"CTR declining: {ctr_trend:.1f}%")
        
        return DomainHealth(
            domain="blog",
            score=score,
            weight=self.weights["blog"],
            components=components,
            trend=impressions_trend,
            alerts=alerts,
        )
    
    def calculate_revenue_health(
        self,
        mrr: float,
        mrr_growth_rate: float,       # Monthly growth %
        churn_rate: float,            # Monthly churn %
        trial_conversion_rate: float,
        ltv_cac_ratio: float,
    ) -> DomainHealth:
        """Calculate revenue domain health."""
        # Normalize to 0-100
        growth_score = 50 + (mrr_growth_rate * 5)  # +10% = 100
        growth_score = max(0, min(100, growth_score))
        
        churn_score = max(0, 100 - (churn_rate * 20))  # <5% = good
        
        conversion_score = min(100, trial_conversion_rate * 400)  # 25% = 100
        
        ltv_cac_score = min(100, ltv_cac_ratio * 33)  # 3:1 = 100
        
        components = {
            "growth": growth_score,
            "retention": churn_score,
            "conversion": conversion_score,
            "efficiency": ltv_cac_score,
        }
        
        score = (
            components["growth"] * 0.30 +
            components["retention"] * 0.30 +
            components["conversion"] * 0.25 +
            components["efficiency"] * 0.15
        )
        
        alerts = []
        if churn_rate > 5:
            alerts.append(f"Churn elevated: {churn_rate:.1f}%")
        if mrr_growth_rate < 0:
            alerts.append(f"MRR declining: {mrr_growth_rate:.1f}%")
        
        return DomainHealth(
            domain="revenue",
            score=score,
            weight=self.weights["revenue"],
            components=components,
            trend=mrr_growth_rate,
            alerts=alerts,
        )
    
    def calculate_meta_health(
        self,
        prediction_accuracy: float,   # 0-1
        action_success_rate: float,   # 0-1
        rollback_rate: float,         # 0-1
        calibration_drift: float,     # How much calibration has shifted
    ) -> DomainHealth:
        """Calculate meta (self-optimization) health."""
        accuracy_score = prediction_accuracy * 100
        success_score = action_success_rate * 100
        stability_score = max(0, 100 - (rollback_rate * 500))  # <20% = good
        calibration_score = max(0, 100 - (calibration_drift * 100))
        
        components = {
            "accuracy": accuracy_score,
            "success": success_score,
            "stability": stability_score,
            "calibration": calibration_score,
        }
        
        score = (
            components["accuracy"] * 0.35 +
            components["success"] * 0.35 +
            components["stability"] * 0.20 +
            components["calibration"] * 0.10
        )
        
        alerts = []
        if prediction_accuracy < 0.7:
            alerts.append(f"Prediction accuracy low: {prediction_accuracy*100:.0f}%")
        if rollback_rate > 0.1:
            alerts.append(f"Rollback rate high: {rollback_rate*100:.0f}%")
        
        return DomainHealth(
            domain="meta",
            score=score,
            weight=self.weights["meta"],
            components=components,
            alerts=alerts,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # SYSTEM HEALTH
    # ─────────────────────────────────────────────────────────────────────
    
    def calculate_system_health(
        self,
        app: DomainHealth,
        blog: DomainHealth,
        revenue: DomainHealth,
        meta: DomainHealth,
    ) -> SystemHealth:
        """Calculate unified system health from all domains."""
        # Weighted score
        score = (
            app.score * app.weight +
            blog.score * blog.weight +
            revenue.score * revenue.weight +
            meta.score * meta.weight
        )
        
        # Determine level
        if score < self.thresholds["critical"]:
            level = HealthLevel.CRITICAL
        elif score < self.thresholds["degraded"]:
            level = HealthLevel.DEGRADED
        elif score < self.thresholds["cautious"]:
            level = HealthLevel.CAUTIOUS
        elif score < self.thresholds["healthy"]:
            level = HealthLevel.HEALTHY
        else:
            level = HealthLevel.OPTIMAL
        
        # Determine risk tolerance
        risk_tolerance = self._determine_risk_tolerance(level, app, revenue)
        
        # Determine operational parameters
        auto_apply_enabled = level not in [HealthLevel.CRITICAL, HealthLevel.DEGRADED]
        max_actions = self._calculate_max_actions(level)
        escalation_factor = self._calculate_escalation_factor(level)
        
        # Calculate trend
        self.history.append((datetime.utcnow(), score))
        self.history = [
            (t, s) for t, s in self.history 
            if t >= datetime.utcnow() - timedelta(days=7)
        ]
        trend = self._calculate_trend()
        
        # Calculate volatility
        volatility = self._calculate_volatility()
        
        # Collect alerts
        alerts = app.alerts + blog.alerts + revenue.alerts + meta.alerts
        
        # Add system-level alerts
        if trend < -5:
            alerts.append(f"System health declining: {trend:.1f}% over 7 days")
        if volatility > 10:
            alerts.append(f"Health unstable: {volatility:.1f}% volatility")
        
        return SystemHealth(
            score=score,
            level=level,
            risk_tolerance=risk_tolerance,
            app_health=app,
            blog_health=blog,
            revenue_health=revenue,
            meta_health=meta,
            trend=trend,
            volatility=volatility,
            auto_apply_enabled=auto_apply_enabled,
            max_actions_per_cycle=max_actions,
            review_escalation_factor=escalation_factor,
            alerts=alerts,
        )
    
    def _determine_risk_tolerance(
        self,
        level: HealthLevel,
        app: DomainHealth,
        revenue: DomainHealth,
    ) -> RiskTolerance:
        """Determine how much risk Meta can take."""
        # Base on health level
        if level == HealthLevel.CRITICAL:
            return RiskTolerance.NONE
        elif level == HealthLevel.DEGRADED:
            return RiskTolerance.MINIMAL
        elif level == HealthLevel.CAUTIOUS:
            return RiskTolerance.MODERATE
        elif level == HealthLevel.HEALTHY:
            # Check if any critical domain is struggling
            if app.score < 60 or revenue.score < 60:
                return RiskTolerance.MODERATE
            return RiskTolerance.ELEVATED
        else:  # OPTIMAL
            if app.score >= 85 and revenue.score >= 85:
                return RiskTolerance.MAXIMUM
            return RiskTolerance.ELEVATED
    
    def _calculate_max_actions(self, level: HealthLevel) -> int:
        """Calculate maximum actions per cycle based on health."""
        base = {
            HealthLevel.CRITICAL: 0,
            HealthLevel.DEGRADED: 2,
            HealthLevel.CAUTIOUS: 5,
            HealthLevel.HEALTHY: 10,
            HealthLevel.OPTIMAL: 25,
        }
        return base.get(level, 5)
    
    def _calculate_escalation_factor(self, level: HealthLevel) -> float:
        """Calculate how much to tighten review thresholds."""
        # Factor > 1 means tighter thresholds (more gets escalated)
        factors = {
            HealthLevel.CRITICAL: 2.0,
            HealthLevel.DEGRADED: 1.5,
            HealthLevel.CAUTIOUS: 1.2,
            HealthLevel.HEALTHY: 1.0,
            HealthLevel.OPTIMAL: 0.8,
        }
        return factors.get(level, 1.0)
    
    def _calculate_trend(self) -> float:
        """Calculate health trend over recent history."""
        if len(self.history) < 2:
            return 0.0
        
        # Compare first third to last third
        n = len(self.history)
        first_third = [s for _, s in self.history[:n//3]] or [self.history[0][1]]
        last_third = [s for _, s in self.history[-n//3:]] or [self.history[-1][1]]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        if first_avg == 0:
            return 0.0
        
        return ((last_avg - first_avg) / first_avg) * 100
    
    def _calculate_volatility(self) -> float:
        """Calculate how much health fluctuates."""
        if len(self.history) < 3:
            return 0.0
        
        scores = [s for _, s in self.history]
        mean = sum(scores) / len(scores)
        
        if mean == 0:
            return 0.0
        
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Coefficient of variation
        return (std_dev / mean) * 100


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_health_calculator: Optional[HealthCalculator] = None

def get_health_calculator() -> HealthCalculator:
    """Get the global health calculator instance."""
    global _health_calculator
    if _health_calculator is None:
        _health_calculator = HealthCalculator()
    return _health_calculator


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "HealthLevel",
    "RiskTolerance",
    "DomainHealth",
    "SystemHealth",
    "HealthCalculator",
    "get_health_calculator",
]
