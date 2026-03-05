#!/usr/bin/env python3
"""
LNCP META: BUNDLE TRACKER v1.0.0
Tracks and optimizes the P1 Addon Bundling system.

This tracker monitors:
- Bundle vs standalone selection rates
- Bundle pricing effectiveness
- Savings display impact
- Bundle attach rate by tier
- Revenue from bundles

It provides:
- Real-time bundle metrics
- Bundle health scoring
- Pricing optimization suggestions
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# BUNDLE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BundleDefinition:
    """Definition of a bundle offering."""
    bundle_id: str
    name: str
    components: List[str]       # e.g., ["pro", "voice_style"]
    base_price: float           # Without bundle discount
    bundle_price: float         # With bundle discount
    savings: float              # Difference
    savings_percent: float
    badge: Optional[str] = None # e.g., "Best Value"


# v3.1.1 Bundle Definitions
BUNDLES = {
    "pro_vs": BundleDefinition(
        bundle_id="pro_vs",
        name="Pro + Voice & Style",
        components=["pro", "voice_style"],
        base_price=14.98,    # $4.99 + $9.99
        bundle_price=12.99,
        savings=1.99,
        savings_percent=13.3,
    ),
    "featured_vs": BundleDefinition(
        bundle_id="featured_vs",
        name="Featured + Voice & Style",
        components=["featured", "voice_style"],
        base_price=17.98,    # $7.99 + $9.99
        bundle_price=14.99,
        savings=2.99,
        savings_percent=16.6,
    ),
    "authority_vs": BundleDefinition(
        bundle_id="authority_vs",
        name="Authority + Voice & Style",
        components=["authority", "voice_style"],
        base_price=18.98,    # $8.99 + $9.99
        bundle_price=16.99,
        savings=1.99,
        savings_percent=10.5,
        badge="Best Value",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# BUNDLE METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BundleMetrics:
    """Metrics for a specific bundle."""
    bundle_id: str
    bundle_name: str
    
    # Selection stats
    times_viewed: int = 0
    times_selected: int = 0
    times_purchased: int = 0
    selection_rate: float = 0.0
    purchase_rate: float = 0.0
    
    # Revenue
    total_revenue: float = 0.0
    mrr_contribution: float = 0.0
    
    # vs Standalone
    standalone_selected_instead: int = 0
    bundle_preference_rate: float = 0.0
    
    # Savings shown
    avg_savings_shown: float = 0.0


@dataclass
class BundleHealth:
    """Overall bundle system health."""
    # Scores (0-100)
    overall_score: float = 0.0
    bundle_awareness: float = 0.0       # % who view bundles
    bundle_adoption: float = 0.0        # % who choose bundles
    
    # Totals
    total_bundle_purchases: int = 0
    total_standalone_purchases: int = 0
    bundle_share: float = 0.0           # % of purchases that are bundles
    
    # Revenue
    bundle_mrr: float = 0.0
    standalone_addon_mrr: float = 0.0
    total_addon_mrr: float = 0.0
    
    # Savings
    total_savings_offered: float = 0.0
    total_savings_claimed: float = 0.0
    
    # By bundle
    bundle_breakdown: Dict[str, Dict] = field(default_factory=dict)
    
    # Issues
    issues: List[str] = field(default_factory=list)
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# BUNDLE TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class BundleTracker:
    """
    Tracks and optimizes the P1 Addon Bundling system.
    
    Responsibilities:
    1. Track bundle views and selections
    2. Compare bundle vs standalone choices
    3. Calculate bundle revenue impact
    4. Measure savings effectiveness
    5. Suggest pricing optimizations
    """
    
    def __init__(self):
        self.bundles = BUNDLES
        
        # Storage
        self._view_events: List[Dict] = []
        self._selection_events: List[Dict] = []
        self._purchase_events: List[Dict] = []
        self._comparison_events: List[Dict] = []
        
        # Cached
        self._last_health: Optional[BundleHealth] = None
        self._last_calculated: Optional[datetime] = None
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_bundle_section_viewed(
        self,
        user_id: str,
        bundles_shown: List[str],
        user_tier: str,
        country: str
    ) -> None:
        """Track bundle section being viewed."""
        self._view_events.append({
            "user_id": user_id,
            "bundles_shown": bundles_shown,
            "user_tier": user_tier,
            "country": country,
            "timestamp": datetime.utcnow(),
        })
    
    def track_bundle_viewed(
        self,
        user_id: str,
        bundle_id: str,
        savings_shown: float,
        duration_seconds: float = 0
    ) -> None:
        """Track specific bundle being viewed/hovered."""
        self._view_events.append({
            "user_id": user_id,
            "bundle_id": bundle_id,
            "type": "bundle_detail",
            "savings_shown": savings_shown,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow(),
        })
    
    def track_bundle_compared(
        self,
        user_id: str,
        bundles_compared: List[str]
    ) -> None:
        """Track user comparing bundles."""
        self._comparison_events.append({
            "user_id": user_id,
            "bundles_compared": bundles_compared,
            "timestamp": datetime.utcnow(),
        })
    
    def track_bundle_selected(
        self,
        user_id: str,
        bundle_id: str,
        over_standalone: bool = True
    ) -> None:
        """Track bundle being selected (clicked to purchase)."""
        self._selection_events.append({
            "user_id": user_id,
            "bundle_id": bundle_id,
            "type": "bundle",
            "over_standalone": over_standalone,
            "timestamp": datetime.utcnow(),
        })
    
    def track_standalone_selected(
        self,
        user_id: str,
        product_id: str,
        bundles_available: List[str]
    ) -> None:
        """Track standalone being selected over bundles."""
        self._selection_events.append({
            "user_id": user_id,
            "product_id": product_id,
            "type": "standalone",
            "bundles_available": bundles_available,
            "timestamp": datetime.utcnow(),
        })
    
    def track_bundle_purchased(
        self,
        user_id: str,
        bundle_id: str,
        price: float,
        savings: float,
        currency: str,
        billing_period: str = "monthly"
    ) -> None:
        """Track bundle purchase completion."""
        self._purchase_events.append({
            "user_id": user_id,
            "bundle_id": bundle_id,
            "type": "bundle",
            "price": price,
            "savings": savings,
            "currency": currency,
            "billing_period": billing_period,
            "timestamp": datetime.utcnow(),
        })
    
    def track_standalone_purchased(
        self,
        user_id: str,
        product_id: str,
        price: float,
        currency: str,
        billing_period: str = "monthly"
    ) -> None:
        """Track standalone addon purchase."""
        self._purchase_events.append({
            "user_id": user_id,
            "product_id": product_id,
            "type": "standalone",
            "price": price,
            "currency": currency,
            "billing_period": billing_period,
            "timestamp": datetime.utcnow(),
        })
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_bundle_metrics(self, bundle_id: str) -> BundleMetrics:
        """Get metrics for a specific bundle."""
        bundle_def = self.bundles.get(bundle_id)
        if not bundle_def:
            return BundleMetrics(bundle_id=bundle_id, bundle_name="Unknown")
        
        # Views
        views = len([
            e for e in self._view_events
            if e.get("bundle_id") == bundle_id or bundle_id in e.get("bundles_shown", [])
        ])
        
        # Selections
        selections = len([
            e for e in self._selection_events
            if e.get("bundle_id") == bundle_id and e.get("type") == "bundle"
        ])
        
        # Purchases
        purchases = [
            e for e in self._purchase_events
            if e.get("bundle_id") == bundle_id and e.get("type") == "bundle"
        ]
        purchase_count = len(purchases)
        
        # Revenue
        revenue = sum(e.get("price", 0) for e in purchases)
        mrr = sum(
            e.get("price", 0) if e.get("billing_period") == "monthly"
            else e.get("price", 0) / 12
            for e in purchases
        )
        
        # Standalone chosen instead
        standalone_instead = len([
            e for e in self._selection_events
            if e.get("type") == "standalone" and bundle_id in e.get("bundles_available", [])
        ])
        
        # Rates
        selection_rate = selections / views if views else 0
        purchase_rate = purchase_count / selections if selections else 0
        preference_rate = selections / (selections + standalone_instead) if (selections + standalone_instead) else 0
        
        # Savings
        savings_events = [
            e for e in self._view_events
            if e.get("bundle_id") == bundle_id and e.get("savings_shown")
        ]
        avg_savings = (
            sum(e.get("savings_shown", 0) for e in savings_events) / len(savings_events)
            if savings_events else bundle_def.savings
        )
        
        return BundleMetrics(
            bundle_id=bundle_id,
            bundle_name=bundle_def.name,
            times_viewed=views,
            times_selected=selections,
            times_purchased=purchase_count,
            selection_rate=selection_rate,
            purchase_rate=purchase_rate,
            total_revenue=revenue,
            mrr_contribution=mrr,
            standalone_selected_instead=standalone_instead,
            bundle_preference_rate=preference_rate,
            avg_savings_shown=avg_savings,
        )
    
    def get_health(self) -> BundleHealth:
        """Calculate overall bundle system health."""
        # Cache for 5 minutes
        if (
            self._last_health and self._last_calculated and
            datetime.utcnow() - self._last_calculated < timedelta(minutes=5)
        ):
            return self._last_health
        
        now = datetime.utcnow()
        
        # Total purchases
        bundle_purchases = [e for e in self._purchase_events if e.get("type") == "bundle"]
        standalone_purchases = [e for e in self._purchase_events if e.get("type") == "standalone"]
        
        total_bundle = len(bundle_purchases)
        total_standalone = len(standalone_purchases)
        total_all = total_bundle + total_standalone
        
        bundle_share = total_bundle / total_all if total_all else 0
        
        # Revenue
        bundle_mrr = sum(
            e.get("price", 0) if e.get("billing_period") == "monthly"
            else e.get("price", 0) / 12
            for e in bundle_purchases
        )
        standalone_mrr = sum(
            e.get("price", 0) if e.get("billing_period") == "monthly"
            else e.get("price", 0) / 12
            for e in standalone_purchases
        )
        
        # Savings
        savings_claimed = sum(e.get("savings", 0) for e in bundle_purchases)
        savings_offered = sum(
            self.bundles[e.get("bundle_id", "")].savings
            for e in self._view_events
            if e.get("bundle_id") in self.bundles
        )
        
        # Awareness (% who viewed bundles)
        unique_viewers = len(set(e["user_id"] for e in self._view_events))
        # Would compare to total users to get awareness
        
        # Bundle breakdown
        breakdown = {}
        for bundle_id in self.bundles:
            metrics = self.get_bundle_metrics(bundle_id)
            breakdown[bundle_id] = {
                "purchases": metrics.times_purchased,
                "mrr": metrics.mrr_contribution,
                "preference_rate": metrics.bundle_preference_rate,
            }
        
        # Overall score
        overall = (bundle_share * 50) + (min(bundle_mrr / 1000, 1) * 30) + 20
        
        # Issues
        issues = []
        if bundle_share < 0.3 and total_all > 20:
            issues.append("Low bundle adoption - review pricing or visibility")
        if bundle_mrr < standalone_mrr * 0.5:
            issues.append("Bundle revenue low - bundles may not be compelling")
        
        health = BundleHealth(
            overall_score=min(100, overall),
            bundle_awareness=unique_viewers,  # Would be % in production
            bundle_adoption=bundle_share * 100,
            total_bundle_purchases=total_bundle,
            total_standalone_purchases=total_standalone,
            bundle_share=bundle_share,
            bundle_mrr=bundle_mrr,
            standalone_addon_mrr=standalone_mrr,
            total_addon_mrr=bundle_mrr + standalone_mrr,
            total_savings_offered=savings_offered,
            total_savings_claimed=savings_claimed,
            bundle_breakdown=breakdown,
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
        """Generate optimization suggestions for bundle system."""
        suggestions = []
        health = self.get_health()
        
        # Bundle pricing
        for bundle_id, bundle_def in self.bundles.items():
            metrics = self.get_bundle_metrics(bundle_id)
            
            # If low preference rate, suggest higher savings
            if metrics.bundle_preference_rate < 0.4 and metrics.times_viewed > 20:
                current_savings_pct = bundle_def.savings_percent
                suggested_savings_pct = min(25, current_savings_pct + 5)
                
                suggestions.append({
                    "type": "bundle_pricing",
                    "bundle_id": bundle_id,
                    "current_savings_percent": current_savings_pct,
                    "suggested_savings_percent": suggested_savings_pct,
                    "reason": f"Low preference rate ({metrics.bundle_preference_rate:.1%}) - increase savings",
                    "confidence": 0.65,
                    "domain": "bundling",
                })
        
        # Badge effectiveness
        authority_metrics = self.get_bundle_metrics("authority_vs")
        pro_metrics = self.get_bundle_metrics("pro_vs")
        
        if authority_metrics.times_purchased < pro_metrics.times_purchased * 0.3:
            suggestions.append({
                "type": "bundle_badge",
                "bundle_id": "authority_vs",
                "current_badge": "Best Value",
                "suggested_badge": "Most Popular",
                "reason": "Best Value badge not driving purchases - test different badge",
                "confidence": 0.55,
                "domain": "bundling",
            })
        
        # Standalone pricing
        if health.bundle_share < 0.25 and health.total_standalone_purchases > 30:
            suggestions.append({
                "type": "standalone_pricing",
                "suggestion": "increase_standalone_price",
                "reason": "Low bundle share - make standalone less attractive",
                "confidence": 0.5,
                "domain": "bundling",
            })
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_bundle_tracker: Optional[BundleTracker] = None


def get_bundle_tracker() -> BundleTracker:
    """Get singleton bundle tracker."""
    global _bundle_tracker
    if _bundle_tracker is None:
        _bundle_tracker = BundleTracker()
    return _bundle_tracker
