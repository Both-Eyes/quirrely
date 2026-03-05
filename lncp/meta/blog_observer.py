#!/usr/bin/env python3
"""
LNCP META: BLOG OBSERVER v1.0.0-G2M
Tracks and optimizes the Blog/SEO system.
G2M (Go-To-Market) Release.

This observer monitors:
- GSC performance (impressions, clicks, CTR, position)
- Blog page engagement (views, time on page, scroll depth)
- CTA performance (click-through, conversion)
- Content freshness and health
- Keyword opportunities

It provides:
- Real-time blog health metrics
- SEO optimization suggestions
- Keyword opportunity detection
- Content refresh recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# BLOG METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PagePerformance:
    """Performance metrics for a single blog page."""
    page_url: str
    page_title: str
    
    # GSC metrics
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_position: float = 0.0
    
    # Trends (vs previous period)
    impressions_trend: float = 0.0
    clicks_trend: float = 0.0
    position_trend: float = 0.0
    
    # Engagement metrics
    page_views: int = 0
    avg_time_on_page: float = 0.0
    bounce_rate: float = 0.0
    scroll_depth_avg: float = 0.0
    
    # CTA metrics
    cta_impressions: int = 0
    cta_clicks: int = 0
    cta_ctr: float = 0.0
    cta_conversions: int = 0
    
    # Content metrics
    word_count: int = 0
    publish_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    days_since_update: int = 0
    freshness_score: float = 100.0
    
    # Status
    is_performing: bool = True
    needs_attention: bool = False
    opportunities: List[str] = field(default_factory=list)


@dataclass
class KeywordOpportunity:
    """A keyword ranking opportunity."""
    keyword: str
    page_url: str
    current_position: float
    impressions: int
    clicks: int
    ctr: float
    potential_clicks: int      # Estimated clicks if position 5
    difficulty: str            # "easy", "medium", "hard"
    suggested_action: str
    priority: float            # 0-100


@dataclass
class ContentFreshness:
    """Content freshness tracking."""
    page_url: str
    publish_date: datetime
    last_updated: datetime
    word_count: int
    days_since_update: int
    freshness_score: float     # 0-100
    update_recommended: bool
    reason: Optional[str] = None


@dataclass
class BlogHealth:
    """Overall blog system health."""
    # Scores (0-100)
    overall_score: float = 0.0
    seo_score: float = 0.0
    engagement_score: float = 0.0
    content_score: float = 0.0
    cta_score: float = 0.0
    
    # GSC totals
    total_impressions: int = 0
    total_clicks: int = 0
    avg_ctr: float = 0.0
    avg_position: float = 0.0
    
    # Trends
    impressions_trend: float = 0.0
    clicks_trend: float = 0.0
    ctr_trend: float = 0.0
    
    # Page counts
    total_pages: int = 0
    pages_performing: int = 0
    pages_declining: int = 0
    pages_need_refresh: int = 0
    
    # Top performers
    top_pages: List[str] = field(default_factory=list)
    declining_pages: List[str] = field(default_factory=list)
    
    # Opportunities
    keyword_opportunities: int = 0
    content_refresh_needed: int = 0
    
    # Issues
    issues: List[str] = field(default_factory=list)
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# BLOG OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class BlogObserver:
    """
    Observes and optimizes the Blog/SEO system.
    
    Responsibilities:
    1. Track GSC performance metrics
    2. Monitor blog engagement
    3. Detect keyword opportunities
    4. Track content freshness
    5. Generate SEO optimization suggestions
    """
    
    def __init__(self):
        # Page tracking
        self._pages: Dict[str, PagePerformance] = {}
        
        # GSC data
        self._gsc_data: List[Dict] = []
        self._last_gsc_fetch: Optional[datetime] = None
        
        # Engagement events
        self._page_view_events: List[Dict] = []
        self._cta_events: List[Dict] = []
        self._scroll_events: List[Dict] = []
        
        # Content tracking
        self._content_registry: Dict[str, ContentFreshness] = {}
        
        # Cached health
        self._last_health: Optional[BlogHealth] = None
        self._last_calculated: Optional[datetime] = None
        
        # Configuration
        self.config = {
            "striking_distance_min": 8,
            "striking_distance_max": 20,
            "min_impressions_opportunity": 100,
            "freshness_threshold_days": 90,
            "declining_threshold_pct": -10,
            "performing_position_max": 20,
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # GSC DATA TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def ingest_gsc_data(
        self,
        page_url: str,
        impressions: int,
        clicks: int,
        ctr: float,
        position: float,
        date_str: str,
        queries: Optional[List[Dict]] = None
    ) -> None:
        """Ingest GSC data for a page."""
        self._gsc_data.append({
            "page_url": page_url,
            "impressions": impressions,
            "clicks": clicks,
            "ctr": ctr,
            "position": position,
            "date": date_str,
            "queries": queries or [],
            "timestamp": datetime.utcnow(),
        })
        
        # Update page performance
        if page_url not in self._pages:
            self._pages[page_url] = PagePerformance(
                page_url=page_url,
                page_title=page_url.split("/")[-1].replace("-", " ").title()
            )
        
        page = self._pages[page_url]
        page.impressions = impressions
        page.clicks = clicks
        page.ctr = ctr
        page.avg_position = position
        
        self._last_gsc_fetch = datetime.utcnow()
    
    def bulk_ingest_gsc(self, pages_data: List[Dict]) -> None:
        """Bulk ingest GSC data for multiple pages."""
        for data in pages_data:
            self.ingest_gsc_data(
                page_url=data.get("page_url", ""),
                impressions=data.get("impressions", 0),
                clicks=data.get("clicks", 0),
                ctr=data.get("ctr", 0.0),
                position=data.get("position", 0.0),
                date_str=data.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
                queries=data.get("queries"),
            )
    
    # ─────────────────────────────────────────────────────────────────────
    # ENGAGEMENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_page_view(
        self,
        page_url: str,
        session_id: str,
        user_id: Optional[str] = None,
        referrer: Optional[str] = None,
        device: str = "desktop"
    ) -> None:
        """Track a blog page view."""
        self._page_view_events.append({
            "page_url": page_url,
            "session_id": session_id,
            "user_id": user_id,
            "referrer": referrer,
            "device": device,
            "timestamp": datetime.utcnow(),
        })
        
        if page_url in self._pages:
            self._pages[page_url].page_views += 1
    
    def track_scroll_depth(
        self,
        page_url: str,
        session_id: str,
        depth_percent: float
    ) -> None:
        """Track scroll depth on a page."""
        self._scroll_events.append({
            "page_url": page_url,
            "session_id": session_id,
            "depth_percent": depth_percent,
            "timestamp": datetime.utcnow(),
        })
    
    def track_time_on_page(
        self,
        page_url: str,
        session_id: str,
        seconds: float
    ) -> None:
        """Track time spent on page."""
        if page_url in self._pages:
            # Running average
            current = self._pages[page_url].avg_time_on_page
            views = self._pages[page_url].page_views
            self._pages[page_url].avg_time_on_page = (
                (current * (views - 1) + seconds) / views if views > 0 else seconds
            )
    
    def track_cta_event(
        self,
        page_url: str,
        cta_id: str,
        event_type: str,    # "impression", "click", "conversion"
        session_id: str,
        variant: Optional[str] = None
    ) -> None:
        """Track CTA events."""
        self._cta_events.append({
            "page_url": page_url,
            "cta_id": cta_id,
            "event_type": event_type,
            "session_id": session_id,
            "variant": variant,
            "timestamp": datetime.utcnow(),
        })
        
        if page_url in self._pages:
            page = self._pages[page_url]
            if event_type == "impression":
                page.cta_impressions += 1
            elif event_type == "click":
                page.cta_clicks += 1
            elif event_type == "conversion":
                page.cta_conversions += 1
            
            if page.cta_impressions > 0:
                page.cta_ctr = page.cta_clicks / page.cta_impressions
    
    # ─────────────────────────────────────────────────────────────────────
    # CONTENT FRESHNESS TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def register_content(
        self,
        page_url: str,
        publish_date: datetime,
        last_updated: datetime,
        word_count: int
    ) -> None:
        """Register content for freshness tracking."""
        days_since = (datetime.utcnow() - last_updated).days
        freshness = max(0, 100 - (days_since / self.config["freshness_threshold_days"]) * 100)
        
        self._content_registry[page_url] = ContentFreshness(
            page_url=page_url,
            publish_date=publish_date,
            last_updated=last_updated,
            word_count=word_count,
            days_since_update=days_since,
            freshness_score=freshness,
            update_recommended=days_since > self.config["freshness_threshold_days"],
            reason="Content over 90 days old" if days_since > 90 else None,
        )
        
        if page_url in self._pages:
            self._pages[page_url].word_count = word_count
            self._pages[page_url].publish_date = publish_date
            self._pages[page_url].last_updated = last_updated
            self._pages[page_url].days_since_update = days_since
            self._pages[page_url].freshness_score = freshness
    
    # ─────────────────────────────────────────────────────────────────────
    # KEYWORD OPPORTUNITY DETECTION
    # ─────────────────────────────────────────────────────────────────────
    
    def detect_keyword_opportunities(self) -> List[KeywordOpportunity]:
        """Find keywords where we rank in striking distance (8-20)."""
        opportunities = []
        
        for data in self._gsc_data:
            for query in data.get("queries", []):
                position = query.get("position", 0)
                impressions = query.get("impressions", 0)
                
                if (self.config["striking_distance_min"] <= position <= self.config["striking_distance_max"]
                    and impressions >= self.config["min_impressions_opportunity"]):
                    
                    # Estimate potential clicks at position 5
                    # Position 5 CTR is roughly 5-7%
                    potential_ctr = 0.06
                    potential_clicks = int(impressions * potential_ctr)
                    current_clicks = query.get("clicks", 0)
                    
                    # Difficulty based on position
                    if position <= 10:
                        difficulty = "easy"
                    elif position <= 15:
                        difficulty = "medium"
                    else:
                        difficulty = "hard"
                    
                    # Priority based on impressions and position
                    priority = min(100, (impressions / 1000) * (21 - position))
                    
                    opportunities.append(KeywordOpportunity(
                        keyword=query.get("query", ""),
                        page_url=data["page_url"],
                        current_position=position,
                        impressions=impressions,
                        clicks=current_clicks,
                        ctr=query.get("ctr", 0),
                        potential_clicks=potential_clicks,
                        difficulty=difficulty,
                        suggested_action=self._suggest_keyword_action(position, impressions),
                        priority=priority,
                    ))
        
        # Sort by priority
        opportunities.sort(key=lambda x: x.priority, reverse=True)
        return opportunities[:20]  # Top 20
    
    def _suggest_keyword_action(self, position: float, impressions: int) -> str:
        """Suggest action for keyword opportunity."""
        if position <= 10:
            return "optimize_meta_description"
        elif position <= 15:
            return "add_internal_links"
        else:
            return "expand_content"
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_health(self) -> BlogHealth:
        """Calculate overall blog system health."""
        # Cache for 5 minutes
        if (
            self._last_health and self._last_calculated and
            datetime.utcnow() - self._last_calculated < timedelta(minutes=5)
        ):
            return self._last_health
        
        now = datetime.utcnow()
        
        # Aggregate GSC metrics
        total_impressions = sum(p.impressions for p in self._pages.values())
        total_clicks = sum(p.clicks for p in self._pages.values())
        avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        avg_position = (
            sum(p.avg_position * p.impressions for p in self._pages.values()) / total_impressions
            if total_impressions > 0 else 0
        )
        
        # Calculate trends (simplified - would compare to previous period)
        impressions_trend = sum(p.impressions_trend for p in self._pages.values()) / max(1, len(self._pages))
        clicks_trend = sum(p.clicks_trend for p in self._pages.values()) / max(1, len(self._pages))
        
        # Page classification
        performing = [p for p in self._pages.values() if p.avg_position < self.config["performing_position_max"]]
        declining = [p for p in self._pages.values() if p.impressions_trend < self.config["declining_threshold_pct"]]
        need_refresh = [url for url, cf in self._content_registry.items() if cf.update_recommended]
        
        # Keyword opportunities
        opportunities = self.detect_keyword_opportunities()
        
        # Calculate component scores
        seo_score = self._calculate_seo_score(avg_position, avg_ctr, total_impressions)
        engagement_score = self._calculate_engagement_score()
        content_score = self._calculate_content_score()
        cta_score = self._calculate_cta_score()
        
        # Overall score
        overall = (
            seo_score * 0.40 +
            engagement_score * 0.25 +
            content_score * 0.20 +
            cta_score * 0.15
        )
        
        # Issues
        issues = []
        if impressions_trend < -10:
            issues.append(f"Impressions declining: {impressions_trend:.1f}%")
        if len(declining) > len(self._pages) * 0.3:
            issues.append(f"{len(declining)} pages declining (>{30}% of total)")
        if len(need_refresh) > 5:
            issues.append(f"{len(need_refresh)} pages need content refresh")
        if avg_position > 15:
            issues.append(f"Average position too low: {avg_position:.1f}")
        
        health = BlogHealth(
            overall_score=overall,
            seo_score=seo_score,
            engagement_score=engagement_score,
            content_score=content_score,
            cta_score=cta_score,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            avg_ctr=avg_ctr,
            avg_position=avg_position,
            impressions_trend=impressions_trend,
            clicks_trend=clicks_trend,
            ctr_trend=0,  # Would calculate
            total_pages=len(self._pages),
            pages_performing=len(performing),
            pages_declining=len(declining),
            pages_need_refresh=len(need_refresh),
            top_pages=[p.page_url for p in sorted(performing, key=lambda x: x.clicks, reverse=True)[:5]],
            declining_pages=[p.page_url for p in declining[:5]],
            keyword_opportunities=len(opportunities),
            content_refresh_needed=len(need_refresh),
            issues=issues,
            calculated_at=now,
        )
        
        self._last_health = health
        self._last_calculated = now
        
        return health
    
    def _calculate_seo_score(self, avg_position: float, avg_ctr: float, impressions: int) -> float:
        """Calculate SEO component score."""
        # Position score (position 1 = 100, position 50 = 0)
        position_score = max(0, 100 - (avg_position - 1) * 2)
        
        # CTR score (10% = 100)
        ctr_score = min(100, avg_ctr * 1000)
        
        # Impressions score (log scale)
        import math
        impressions_score = min(100, math.log10(max(1, impressions)) * 20)
        
        return (position_score * 0.4 + ctr_score * 0.3 + impressions_score * 0.3)
    
    def _calculate_engagement_score(self) -> float:
        """Calculate engagement component score."""
        if not self._pages:
            return 50.0
        
        # Average time on page (target: 3 minutes = 180 seconds)
        avg_time = sum(p.avg_time_on_page for p in self._pages.values()) / len(self._pages)
        time_score = min(100, (avg_time / 180) * 100)
        
        # Scroll depth (target: 75%)
        scroll_depths = [e.get("depth_percent", 0) for e in self._scroll_events[-1000:]]
        avg_scroll = sum(scroll_depths) / len(scroll_depths) if scroll_depths else 50
        scroll_score = min(100, (avg_scroll / 75) * 100)
        
        return (time_score * 0.5 + scroll_score * 0.5)
    
    def _calculate_content_score(self) -> float:
        """Calculate content freshness score."""
        if not self._content_registry:
            return 70.0
        
        avg_freshness = sum(cf.freshness_score for cf in self._content_registry.values()) / len(self._content_registry)
        return avg_freshness
    
    def _calculate_cta_score(self) -> float:
        """Calculate CTA performance score."""
        total_impressions = sum(p.cta_impressions for p in self._pages.values())
        total_clicks = sum(p.cta_clicks for p in self._pages.values())
        
        if total_impressions == 0:
            return 50.0
        
        ctr = total_clicks / total_impressions
        # Target CTR: 5%
        return min(100, (ctr / 0.05) * 100)
    
    # ─────────────────────────────────────────────────────────────────────
    # OPTIMIZATION SUGGESTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Generate SEO optimization suggestions."""
        suggestions = []
        health = self.get_health()
        
        # Keyword opportunities
        opportunities = self.detect_keyword_opportunities()
        for opp in opportunities[:5]:  # Top 5
            suggestions.append({
                "type": "keyword_opportunity",
                "page_url": opp.page_url,
                "keyword": opp.keyword,
                "current_position": opp.current_position,
                "potential_clicks": opp.potential_clicks,
                "suggested_action": opp.suggested_action,
                "confidence": 0.7 if opp.difficulty == "easy" else 0.5,
                "domain": "seo",
                "reason": f"Keyword '{opp.keyword}' at position {opp.current_position:.1f} with {opp.impressions} impressions",
            })
        
        # Declining pages
        for page_url in health.declining_pages[:3]:
            if page_url in self._pages:
                page = self._pages[page_url]
                suggestions.append({
                    "type": "page_recovery",
                    "page_url": page_url,
                    "impressions_trend": page.impressions_trend,
                    "suggested_action": "content_refresh",
                    "confidence": 0.6,
                    "domain": "seo_content",
                    "reason": f"Page declining {page.impressions_trend:.1f}% - needs attention",
                })
        
        # Content freshness
        stale_content = [
            (url, cf) for url, cf in self._content_registry.items()
            if cf.update_recommended
        ]
        for url, cf in sorted(stale_content, key=lambda x: x[1].days_since_update, reverse=True)[:3]:
            suggestions.append({
                "type": "content_refresh",
                "page_url": url,
                "days_since_update": cf.days_since_update,
                "freshness_score": cf.freshness_score,
                "suggested_action": "update_content",
                "confidence": 0.65,
                "domain": "seo_content",
                "reason": f"Content {cf.days_since_update} days old",
            })
        
        # CTA optimization
        low_ctr_pages = [
            p for p in self._pages.values()
            if p.cta_impressions > 100 and p.cta_ctr < 0.02
        ]
        for page in low_ctr_pages[:2]:
            suggestions.append({
                "type": "cta_optimization",
                "page_url": page.page_url,
                "current_ctr": page.cta_ctr,
                "cta_impressions": page.cta_impressions,
                "suggested_action": "cta_copy_test",
                "confidence": 0.55,
                "domain": "seo",
                "reason": f"CTA CTR {page.cta_ctr:.1%} below target",
            })
        
        # Meta description optimization
        low_ctr_in_serp = [
            p for p in self._pages.values()
            if p.impressions > 500 and p.ctr < 0.02 and p.avg_position < 10
        ]
        for page in low_ctr_in_serp[:2]:
            suggestions.append({
                "type": "meta_optimization",
                "page_url": page.page_url,
                "current_ctr": page.ctr,
                "position": page.avg_position,
                "suggested_action": "meta_description_update",
                "confidence": 0.7,
                "domain": "seo",
                "reason": f"Position {page.avg_position:.1f} but CTR only {page.ctr:.1%}",
            })
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_blog_observer: Optional[BlogObserver] = None


def get_blog_observer() -> BlogObserver:
    """Get singleton blog observer."""
    global _blog_observer
    if _blog_observer is None:
        _blog_observer = BlogObserver()
    return _blog_observer
