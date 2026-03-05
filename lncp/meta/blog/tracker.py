#!/usr/bin/env python3
"""
LNCP META/BLOG: TRACKER v1.0
Tracks blog page performance for optimization.

Collects:
- Page views
- Time on page
- Scroll depth
- Source/referrer
- Profile associations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import hashlib


# ═══════════════════════════════════════════════════════════════════════════
# TRACKING TYPES
# ═══════════════════════════════════════════════════════════════════════════

class TrafficSource(str, Enum):
    ORGANIC = "organic"
    DIRECT = "direct"
    REFERRAL = "referral"
    SOCIAL = "social"
    EMAIL = "email"
    PAID = "paid"
    INTERNAL = "internal"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


@dataclass
class PageView:
    """A single page view event."""
    view_id: str
    page_url: str
    timestamp: datetime
    
    # User info (anonymized)
    session_id: str
    visitor_id: str  # Hashed, persistent
    
    # Context
    source: TrafficSource
    referrer: Optional[str] = None
    device: DeviceType = DeviceType.DESKTOP
    country: Optional[str] = None
    
    # Content
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None
    
    # Engagement (updated async)
    time_on_page_seconds: int = 0
    scroll_depth_percent: int = 0
    
    # Conversion path
    clicked_cta: bool = False
    started_analysis: bool = False
    completed_signup: bool = False


@dataclass
class PageMetrics:
    """Aggregated metrics for a page."""
    page_url: str
    
    # Volume
    total_views: int = 0
    unique_visitors: int = 0
    
    # Engagement
    avg_time_on_page: float = 0.0
    avg_scroll_depth: float = 0.0
    bounce_rate: float = 0.0  # Left without scrolling 25%+
    
    # Sources
    views_by_source: Dict[str, int] = field(default_factory=dict)
    
    # Conversion
    cta_clicks: int = 0
    cta_click_rate: float = 0.0
    analyses_started: int = 0
    analysis_rate: float = 0.0
    signups: int = 0
    signup_rate: float = 0.0
    
    # Content
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None
    
    # Performance tier
    performance_score: float = 0.0
    tier: str = "unknown"  # "top", "good", "average", "poor", "critical"


# ═══════════════════════════════════════════════════════════════════════════
# BLOG TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class BlogTracker:
    """
    Tracks blog page performance.
    
    In production, this would write to a database.
    For now, it maintains in-memory state that can be
    serialized/loaded.
    """
    
    def __init__(self):
        # Raw events
        self.page_views: List[PageView] = []
        
        # Aggregated metrics by page
        self.page_metrics: Dict[str, PageMetrics] = {}
        
        # Session tracking
        self.active_sessions: Dict[str, Dict] = {}
        
        # Visitor paths
        self.visitor_paths: Dict[str, List[str]] = {}
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_page_view(
        self,
        page_url: str,
        session_id: str,
        visitor_id: str,
        source: TrafficSource = TrafficSource.DIRECT,
        referrer: Optional[str] = None,
        device: DeviceType = DeviceType.DESKTOP,
        country: Optional[str] = None,
        profile_style: Optional[str] = None,
        profile_certitude: Optional[str] = None,
    ) -> PageView:
        """Track a page view."""
        view_id = self._generate_id("view")
        
        view = PageView(
            view_id=view_id,
            page_url=page_url,
            timestamp=datetime.utcnow(),
            session_id=session_id,
            visitor_id=visitor_id,
            source=source,
            referrer=referrer,
            device=device,
            country=country,
            profile_style=profile_style,
            profile_certitude=profile_certitude,
        )
        
        self.page_views.append(view)
        
        # Update session
        self.active_sessions[session_id] = {
            "current_page": page_url,
            "started_at": datetime.utcnow(),
            "visitor_id": visitor_id,
        }
        
        # Update visitor path
        if visitor_id not in self.visitor_paths:
            self.visitor_paths[visitor_id] = []
        self.visitor_paths[visitor_id].append(page_url)
        
        # Update page metrics
        self._update_page_metrics(view)
        
        return view
    
    def track_engagement(
        self,
        view_id: str,
        time_on_page_seconds: int,
        scroll_depth_percent: int,
    ):
        """Update engagement metrics for a view."""
        for view in self.page_views:
            if view.view_id == view_id:
                view.time_on_page_seconds = time_on_page_seconds
                view.scroll_depth_percent = scroll_depth_percent
                self._recalculate_page_metrics(view.page_url)
                break
    
    def track_cta_click(
        self,
        view_id: str,
        cta_variant_id: Optional[str] = None,
        cta_position: Optional[str] = None,
    ):
        """Track a CTA click."""
        for view in self.page_views:
            if view.view_id == view_id:
                view.clicked_cta = True
                self._recalculate_page_metrics(view.page_url)
                break
    
    def track_analysis_start(self, view_id: str):
        """Track when user starts analysis from blog."""
        for view in self.page_views:
            if view.view_id == view_id:
                view.started_analysis = True
                self._recalculate_page_metrics(view.page_url)
                break
    
    def track_signup(self, view_id: str):
        """Track when user signs up from blog."""
        for view in self.page_views:
            if view.view_id == view_id:
                view.completed_signup = True
                self._recalculate_page_metrics(view.page_url)
                break
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _update_page_metrics(self, view: PageView):
        """Update metrics for a page after a new view."""
        url = view.page_url
        
        if url not in self.page_metrics:
            self.page_metrics[url] = PageMetrics(
                page_url=url,
                profile_style=view.profile_style,
                profile_certitude=view.profile_certitude,
            )
        
        metrics = self.page_metrics[url]
        metrics.total_views += 1
        
        # Track unique visitors
        unique = set(v.visitor_id for v in self.page_views if v.page_url == url)
        metrics.unique_visitors = len(unique)
        
        # Track by source
        source = view.source.value
        metrics.views_by_source[source] = metrics.views_by_source.get(source, 0) + 1
    
    def _recalculate_page_metrics(self, page_url: str):
        """Recalculate all metrics for a page."""
        views = [v for v in self.page_views if v.page_url == page_url]
        
        if not views:
            return
        
        if page_url not in self.page_metrics:
            self.page_metrics[page_url] = PageMetrics(page_url=page_url)
        
        metrics = self.page_metrics[page_url]
        
        # Volume
        metrics.total_views = len(views)
        metrics.unique_visitors = len(set(v.visitor_id for v in views))
        
        # Engagement
        times = [v.time_on_page_seconds for v in views if v.time_on_page_seconds > 0]
        metrics.avg_time_on_page = sum(times) / len(times) if times else 0
        
        scrolls = [v.scroll_depth_percent for v in views if v.scroll_depth_percent > 0]
        metrics.avg_scroll_depth = sum(scrolls) / len(scrolls) if scrolls else 0
        
        bounces = len([v for v in views if v.scroll_depth_percent < 25 and v.time_on_page_seconds < 10])
        metrics.bounce_rate = bounces / len(views) if views else 0
        
        # Conversion
        metrics.cta_clicks = len([v for v in views if v.clicked_cta])
        metrics.cta_click_rate = metrics.cta_clicks / len(views) if views else 0
        
        metrics.analyses_started = len([v for v in views if v.started_analysis])
        metrics.analysis_rate = metrics.analyses_started / len(views) if views else 0
        
        metrics.signups = len([v for v in views if v.completed_signup])
        metrics.signup_rate = metrics.signups / len(views) if views else 0
        
        # Calculate performance score and tier
        self._calculate_performance_score(metrics)
    
    def _calculate_performance_score(self, metrics: PageMetrics):
        """Calculate overall performance score for a page."""
        # Weighted score (0-100)
        # - 30% engagement (time + scroll)
        # - 30% CTA performance
        # - 40% conversion
        
        # Engagement score (target: 120s time, 75% scroll)
        time_score = min(100, metrics.avg_time_on_page / 120 * 100)
        scroll_score = min(100, metrics.avg_scroll_depth / 75 * 100)
        engagement_score = (time_score + scroll_score) / 2
        
        # CTA score (target: 5% click rate)
        cta_score = min(100, metrics.cta_click_rate / 0.05 * 100)
        
        # Conversion score (target: 2% signup rate)
        conversion_score = min(100, metrics.signup_rate / 0.02 * 100)
        
        # Weighted total
        metrics.performance_score = (
            engagement_score * 0.30 +
            cta_score * 0.30 +
            conversion_score * 0.40
        )
        
        # Assign tier
        if metrics.performance_score >= 80:
            metrics.tier = "top"
        elif metrics.performance_score >= 60:
            metrics.tier = "good"
        elif metrics.performance_score >= 40:
            metrics.tier = "average"
        elif metrics.performance_score >= 20:
            metrics.tier = "poor"
        else:
            metrics.tier = "critical"
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_page_metrics(self, page_url: str) -> Optional[PageMetrics]:
        """Get metrics for a specific page."""
        return self.page_metrics.get(page_url)
    
    def get_all_pages(self) -> List[PageMetrics]:
        """Get metrics for all pages."""
        return list(self.page_metrics.values())
    
    def get_top_pages(self, limit: int = 10) -> List[PageMetrics]:
        """Get top performing pages."""
        pages = sorted(
            self.page_metrics.values(),
            key=lambda p: p.performance_score,
            reverse=True
        )
        return pages[:limit]
    
    def get_underperforming_pages(self, limit: int = 10) -> List[PageMetrics]:
        """Get pages that need optimization."""
        pages = sorted(
            self.page_metrics.values(),
            key=lambda p: p.performance_score
        )
        return pages[:limit]
    
    def get_high_traffic_low_conversion(self, min_views: int = 100) -> List[PageMetrics]:
        """Get pages with high traffic but low conversion (optimization targets)."""
        candidates = [
            p for p in self.page_metrics.values()
            if p.total_views >= min_views and p.cta_click_rate < 0.02
        ]
        return sorted(candidates, key=lambda p: p.total_views, reverse=True)
    
    def get_views_by_profile(self) -> Dict[str, int]:
        """Get view counts by profile."""
        by_profile = {}
        for view in self.page_views:
            key = f"{view.profile_style}-{view.profile_certitude}"
            by_profile[key] = by_profile.get(key, 0) + 1
        return by_profile
    
    def get_conversion_by_source(self) -> Dict[str, Dict]:
        """Get conversion metrics by traffic source."""
        by_source = {}
        
        for source in TrafficSource:
            views = [v for v in self.page_views if v.source == source]
            if views:
                by_source[source.value] = {
                    "views": len(views),
                    "cta_clicks": len([v for v in views if v.clicked_cta]),
                    "signups": len([v for v in views if v.completed_signup]),
                    "click_rate": len([v for v in views if v.clicked_cta]) / len(views),
                    "signup_rate": len([v for v in views if v.completed_signup]) / len(views),
                }
        
        return by_source
    
    # ─────────────────────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────────────────────
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}_{timestamp}"
    
    def get_summary(self) -> Dict:
        """Get tracker summary."""
        return {
            "total_views": len(self.page_views),
            "unique_pages": len(self.page_metrics),
            "unique_visitors": len(self.visitor_paths),
            "total_cta_clicks": sum(1 for v in self.page_views if v.clicked_cta),
            "total_signups": sum(1 for v in self.page_views if v.completed_signup),
            "avg_performance_score": (
                sum(p.performance_score for p in self.page_metrics.values()) / 
                len(self.page_metrics) if self.page_metrics else 0
            ),
            "pages_by_tier": {
                tier: len([p for p in self.page_metrics.values() if p.tier == tier])
                for tier in ["top", "good", "average", "poor", "critical"]
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_tracker: Optional[BlogTracker] = None

def get_blog_tracker() -> BlogTracker:
    """Get the global blog tracker."""
    global _tracker
    if _tracker is None:
        _tracker = BlogTracker()
    return _tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "TrafficSource",
    "DeviceType",
    "PageView",
    "PageMetrics",
    "BlogTracker",
    "get_blog_tracker",
]
