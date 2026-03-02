#!/usr/bin/env python3
"""
LNCP META/BLOG: CTA TRACKER v1.0
Tracks CTA performance across blog for optimization.

Integrates with:
- Blog Config (for variant assignment)
- Blog Tracker (for conversion attribution)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .config import CTAVariant, CTAPlacement, CTAStyle, get_blog_config
from .tracker import get_blog_tracker


# ═══════════════════════════════════════════════════════════════════════════
# CTA EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class CTAEventType(str, Enum):
    IMPRESSION = "impression"  # CTA was visible
    HOVER = "hover"           # User hovered (desktop)
    CLICK = "click"           # User clicked
    CONVERT = "convert"       # User completed signup


@dataclass
class CTAEvent:
    """A single CTA interaction event."""
    event_id: str
    event_type: CTAEventType
    timestamp: datetime
    
    # Context
    page_url: str
    view_id: str  # Links to PageView
    session_id: str
    visitor_id: str
    
    # CTA info
    variant_id: str
    placement: CTAPlacement
    position_index: int  # 0 = first CTA on page, 1 = second, etc.
    
    # Content context
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None
    
    # Scroll position when event occurred
    scroll_depth_at_event: int = 0
    time_on_page_at_event: int = 0


@dataclass
class CTAPerformance:
    """Performance metrics for a CTA variant."""
    variant_id: str
    
    # Totals
    impressions: int = 0
    hovers: int = 0
    clicks: int = 0
    conversions: int = 0
    
    # Rates
    @property
    def hover_rate(self) -> float:
        return self.hovers / self.impressions if self.impressions > 0 else 0
    
    @property
    def click_rate(self) -> float:
        return self.clicks / self.impressions if self.impressions > 0 else 0
    
    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.clicks if self.clicks > 0 else 0
    
    @property
    def overall_conversion_rate(self) -> float:
        return self.conversions / self.impressions if self.impressions > 0 else 0
    
    # By placement
    performance_by_placement: Dict[str, Dict] = field(default_factory=dict)
    
    # By profile
    performance_by_profile: Dict[str, Dict] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# CTA TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class CTATracker:
    """
    Tracks CTA performance for A/B testing and optimization.
    
    Provides:
    - Event tracking (impression, hover, click, convert)
    - Variant comparison
    - Placement analysis
    - Profile-specific performance
    """
    
    def __init__(self):
        self.events: List[CTAEvent] = []
        self.performance: Dict[str, CTAPerformance] = {}
        
        # Initialize performance for all known variants
        config = get_blog_config()
        for variant_id in config.cta_variants:
            self.performance[variant_id] = CTAPerformance(variant_id=variant_id)
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_impression(
        self,
        page_url: str,
        view_id: str,
        session_id: str,
        visitor_id: str,
        variant_id: str,
        placement: CTAPlacement,
        position_index: int = 0,
        profile_style: Optional[str] = None,
        profile_certitude: Optional[str] = None,
        scroll_depth: int = 0,
        time_on_page: int = 0,
    ) -> CTAEvent:
        """Track a CTA impression (became visible)."""
        return self._track_event(
            CTAEventType.IMPRESSION,
            page_url, view_id, session_id, visitor_id,
            variant_id, placement, position_index,
            profile_style, profile_certitude,
            scroll_depth, time_on_page,
        )
    
    def track_hover(
        self,
        page_url: str,
        view_id: str,
        session_id: str,
        visitor_id: str,
        variant_id: str,
        placement: CTAPlacement,
        position_index: int = 0,
        scroll_depth: int = 0,
        time_on_page: int = 0,
    ) -> CTAEvent:
        """Track a CTA hover."""
        return self._track_event(
            CTAEventType.HOVER,
            page_url, view_id, session_id, visitor_id,
            variant_id, placement, position_index,
            None, None, scroll_depth, time_on_page,
        )
    
    def track_click(
        self,
        page_url: str,
        view_id: str,
        session_id: str,
        visitor_id: str,
        variant_id: str,
        placement: CTAPlacement,
        position_index: int = 0,
        profile_style: Optional[str] = None,
        profile_certitude: Optional[str] = None,
        scroll_depth: int = 0,
        time_on_page: int = 0,
    ) -> CTAEvent:
        """Track a CTA click."""
        event = self._track_event(
            CTAEventType.CLICK,
            page_url, view_id, session_id, visitor_id,
            variant_id, placement, position_index,
            profile_style, profile_certitude,
            scroll_depth, time_on_page,
        )
        
        # Also update the page tracker
        tracker = get_blog_tracker()
        tracker.track_cta_click(view_id, variant_id, placement.value)
        
        return event
    
    def track_conversion(
        self,
        page_url: str,
        view_id: str,
        session_id: str,
        visitor_id: str,
        variant_id: str,
        placement: CTAPlacement,
        position_index: int = 0,
    ) -> CTAEvent:
        """Track a CTA conversion (signup completed)."""
        event = self._track_event(
            CTAEventType.CONVERT,
            page_url, view_id, session_id, visitor_id,
            variant_id, placement, position_index,
            None, None, 0, 0,
        )
        
        # Also update the page tracker
        tracker = get_blog_tracker()
        tracker.track_signup(view_id)
        
        return event
    
    def _track_event(
        self,
        event_type: CTAEventType,
        page_url: str,
        view_id: str,
        session_id: str,
        visitor_id: str,
        variant_id: str,
        placement: CTAPlacement,
        position_index: int,
        profile_style: Optional[str],
        profile_certitude: Optional[str],
        scroll_depth: int,
        time_on_page: int,
    ) -> CTAEvent:
        """Internal method to track any CTA event."""
        event_id = f"cta_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        event = CTAEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            page_url=page_url,
            view_id=view_id,
            session_id=session_id,
            visitor_id=visitor_id,
            variant_id=variant_id,
            placement=placement,
            position_index=position_index,
            profile_style=profile_style,
            profile_certitude=profile_certitude,
            scroll_depth_at_event=scroll_depth,
            time_on_page_at_event=time_on_page,
        )
        
        self.events.append(event)
        self._update_performance(event)
        
        # Update blog config with performance data
        if event_type == CTAEventType.IMPRESSION:
            get_blog_config().update_cta_performance(variant_id, 1, 0, 0)
        elif event_type == CTAEventType.CLICK:
            get_blog_config().update_cta_performance(variant_id, 0, 1, 0)
        elif event_type == CTAEventType.CONVERT:
            get_blog_config().update_cta_performance(variant_id, 0, 0, 1)
        
        return event
    
    def _update_performance(self, event: CTAEvent):
        """Update performance metrics after an event."""
        variant_id = event.variant_id
        
        if variant_id not in self.performance:
            self.performance[variant_id] = CTAPerformance(variant_id=variant_id)
        
        perf = self.performance[variant_id]
        
        # Update totals
        if event.event_type == CTAEventType.IMPRESSION:
            perf.impressions += 1
        elif event.event_type == CTAEventType.HOVER:
            perf.hovers += 1
        elif event.event_type == CTAEventType.CLICK:
            perf.clicks += 1
        elif event.event_type == CTAEventType.CONVERT:
            perf.conversions += 1
        
        # Update by placement
        placement_key = event.placement.value
        if placement_key not in perf.performance_by_placement:
            perf.performance_by_placement[placement_key] = {
                "impressions": 0, "clicks": 0, "conversions": 0
            }
        
        if event.event_type == CTAEventType.IMPRESSION:
            perf.performance_by_placement[placement_key]["impressions"] += 1
        elif event.event_type == CTAEventType.CLICK:
            perf.performance_by_placement[placement_key]["clicks"] += 1
        elif event.event_type == CTAEventType.CONVERT:
            perf.performance_by_placement[placement_key]["conversions"] += 1
        
        # Update by profile
        if event.profile_style and event.profile_certitude:
            profile_key = f"{event.profile_style}-{event.profile_certitude}"
            if profile_key not in perf.performance_by_profile:
                perf.performance_by_profile[profile_key] = {
                    "impressions": 0, "clicks": 0, "conversions": 0
                }
            
            if event.event_type == CTAEventType.IMPRESSION:
                perf.performance_by_profile[profile_key]["impressions"] += 1
            elif event.event_type == CTAEventType.CLICK:
                perf.performance_by_profile[profile_key]["clicks"] += 1
            elif event.event_type == CTAEventType.CONVERT:
                perf.performance_by_profile[profile_key]["conversions"] += 1
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_variant_performance(self, variant_id: str) -> Optional[CTAPerformance]:
        """Get performance for a specific variant."""
        return self.performance.get(variant_id)
    
    def get_all_performance(self) -> Dict[str, CTAPerformance]:
        """Get performance for all variants."""
        return self.performance
    
    def get_best_variant(self, min_impressions: int = 100) -> Optional[str]:
        """Get the best performing variant by conversion rate."""
        eligible = [
            (vid, perf) for vid, perf in self.performance.items()
            if perf.impressions >= min_impressions
        ]
        
        if not eligible:
            return None
        
        best = max(eligible, key=lambda x: x[1].conversion_rate)
        return best[0]
    
    def get_best_placement(self, min_impressions: int = 50) -> Optional[str]:
        """Get the best performing placement."""
        placement_totals = {}
        
        for perf in self.performance.values():
            for placement, data in perf.performance_by_placement.items():
                if placement not in placement_totals:
                    placement_totals[placement] = {"impressions": 0, "clicks": 0, "conversions": 0}
                
                placement_totals[placement]["impressions"] += data["impressions"]
                placement_totals[placement]["clicks"] += data["clicks"]
                placement_totals[placement]["conversions"] += data["conversions"]
        
        eligible = [
            (p, d) for p, d in placement_totals.items()
            if d["impressions"] >= min_impressions
        ]
        
        if not eligible:
            return None
        
        best = max(eligible, key=lambda x: x[1]["conversions"] / x[1]["impressions"] if x[1]["impressions"] > 0 else 0)
        return best[0]
    
    def get_variant_comparison(self) -> List[Dict]:
        """Get comparison of all variants."""
        results = []
        
        for variant_id, perf in self.performance.items():
            results.append({
                "variant_id": variant_id,
                "impressions": perf.impressions,
                "clicks": perf.clicks,
                "conversions": perf.conversions,
                "click_rate": round(perf.click_rate * 100, 2),
                "conversion_rate": round(perf.conversion_rate * 100, 2),
                "overall_rate": round(perf.overall_conversion_rate * 100, 3),
            })
        
        return sorted(results, key=lambda x: x["overall_rate"], reverse=True)
    
    def get_recommendations(self) -> List[Dict]:
        """Get optimization recommendations based on data."""
        recommendations = []
        
        # Check for winning variant
        best = self.get_best_variant(min_impressions=100)
        if best:
            best_perf = self.performance[best]
            avg_rate = sum(p.conversion_rate for p in self.performance.values()) / len(self.performance) if self.performance else 0
            
            if best_perf.conversion_rate > avg_rate * 1.2:  # 20% better than average
                recommendations.append({
                    "type": "winner",
                    "priority": "high",
                    "action": f"Roll out '{best}' as primary CTA",
                    "impact": f"{(best_perf.conversion_rate - avg_rate) / avg_rate * 100:.1f}% better than average",
                })
        
        # Check for underperforming variants
        for variant_id, perf in self.performance.items():
            if perf.impressions >= 100 and perf.click_rate < 0.01:
                recommendations.append({
                    "type": "underperformer",
                    "priority": "medium",
                    "action": f"Retire or revise '{variant_id}' CTA",
                    "impact": f"Only {perf.click_rate*100:.2f}% click rate",
                })
        
        # Check for placement optimization
        best_placement = self.get_best_placement(min_impressions=50)
        if best_placement:
            recommendations.append({
                "type": "placement",
                "priority": "medium",
                "action": f"Prioritize '{best_placement}' CTA placement",
                "impact": "Best performing position",
            })
        
        return recommendations
    
    def get_summary(self) -> Dict:
        """Get tracker summary."""
        total_impressions = sum(p.impressions for p in self.performance.values())
        total_clicks = sum(p.clicks for p in self.performance.values())
        total_conversions = sum(p.conversions for p in self.performance.values())
        
        return {
            "total_events": len(self.events),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "overall_click_rate": total_clicks / total_impressions if total_impressions > 0 else 0,
            "overall_conversion_rate": total_conversions / total_clicks if total_clicks > 0 else 0,
            "variants_tracked": len(self.performance),
            "best_variant": self.get_best_variant(),
            "best_placement": self.get_best_placement(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_cta_tracker: Optional[CTATracker] = None

def get_cta_tracker() -> CTATracker:
    """Get the global CTA tracker."""
    global _cta_tracker
    if _cta_tracker is None:
        _cta_tracker = CTATracker()
    return _cta_tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "CTAEventType",
    "CTAEvent",
    "CTAPerformance",
    "CTATracker",
    "get_cta_tracker",
]
