#!/usr/bin/env python3
"""
LNCP META/BLOG: GSC INTEGRATION v1.0
Google Search Console integration for SEO metrics.

Collects:
- Impressions, clicks, CTR, position by page
- Query performance (keywords)
- Device breakdown
- Country breakdown

This module provides:
1. GSCClient - API client for fetching data
2. GSCDataStore - Storage and aggregation
3. GSCAnalyzer - Insights and recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# GSC DATA TYPES
# ═══════════════════════════════════════════════════════════════════════════

class SearchType(str, Enum):
    WEB = "web"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"


class DeviceDimension(str, Enum):
    DESKTOP = "DESKTOP"
    MOBILE = "MOBILE"
    TABLET = "TABLET"


@dataclass
class SearchMetrics:
    """Core search metrics from GSC."""
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0  # 0.0 to 1.0
    position: float = 0.0  # Average position
    
    def __add__(self, other: 'SearchMetrics') -> 'SearchMetrics':
        """Combine metrics (for aggregation)."""
        total_impressions = self.impressions + other.impressions
        combined_ctr = (
            (self.ctr * self.impressions + other.ctr * other.impressions) / total_impressions
            if total_impressions > 0 else 0
        )
        combined_position = (
            (self.position * self.impressions + other.position * other.impressions) / total_impressions
            if total_impressions > 0 else 0
        )
        return SearchMetrics(
            clicks=self.clicks + other.clicks,
            impressions=total_impressions,
            ctr=combined_ctr,
            position=combined_position,
        )


@dataclass
class PageSearchData:
    """Search data for a single page."""
    page_url: str
    date_range_start: date
    date_range_end: date
    
    # Overall metrics
    metrics: SearchMetrics = field(default_factory=SearchMetrics)
    
    # Top queries driving traffic to this page
    top_queries: List[Tuple[str, SearchMetrics]] = field(default_factory=list)
    
    # Device breakdown
    by_device: Dict[str, SearchMetrics] = field(default_factory=dict)
    
    # Country breakdown
    by_country: Dict[str, SearchMetrics] = field(default_factory=dict)
    
    # Trends
    daily_metrics: Dict[str, SearchMetrics] = field(default_factory=dict)
    
    # Calculated fields
    @property
    def impressions_trend(self) -> float:
        """Calculate impressions trend (% change over period)."""
        if len(self.daily_metrics) < 2:
            return 0.0
        dates = sorted(self.daily_metrics.keys())
        first_half = sum(self.daily_metrics[d].impressions for d in dates[:len(dates)//2])
        second_half = sum(self.daily_metrics[d].impressions for d in dates[len(dates)//2:])
        if first_half == 0:
            return 100.0 if second_half > 0 else 0.0
        return ((second_half - first_half) / first_half) * 100
    
    @property
    def position_trend(self) -> float:
        """Calculate position trend (negative = improving)."""
        if len(self.daily_metrics) < 2:
            return 0.0
        dates = sorted(self.daily_metrics.keys())
        first_half = [self.daily_metrics[d].position for d in dates[:len(dates)//2] if self.daily_metrics[d].position > 0]
        second_half = [self.daily_metrics[d].position for d in dates[len(dates)//2:] if self.daily_metrics[d].position > 0]
        if not first_half or not second_half:
            return 0.0
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        return avg_second - avg_first  # Negative = improving (lower position number is better)


@dataclass
class QuerySearchData:
    """Search data for a query (keyword)."""
    query: str
    metrics: SearchMetrics = field(default_factory=SearchMetrics)
    
    # Pages this query leads to
    top_pages: List[Tuple[str, SearchMetrics]] = field(default_factory=list)
    
    # Profile association (inferred from page)
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None


@dataclass
class GSCSiteData:
    """Complete GSC data for the site."""
    site_url: str
    date_range_start: date
    date_range_end: date
    fetched_at: datetime
    
    # Overall metrics
    total_metrics: SearchMetrics = field(default_factory=SearchMetrics)
    
    # By page
    pages: Dict[str, PageSearchData] = field(default_factory=dict)
    
    # By query
    queries: Dict[str, QuerySearchData] = field(default_factory=dict)
    
    # By device
    by_device: Dict[str, SearchMetrics] = field(default_factory=dict)
    
    # By country
    by_country: Dict[str, SearchMetrics] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# GSC CLIENT (API WRAPPER)
# ═══════════════════════════════════════════════════════════════════════════

class GSCClient:
    """
    Google Search Console API client.
    
    In production, this would use the actual GSC API.
    For now, it provides the interface and can be mocked/simulated.
    
    Required setup:
    1. Create project in Google Cloud Console
    2. Enable Search Console API
    3. Create OAuth2 credentials
    4. Verify site ownership in GSC
    """
    
    def __init__(
        self,
        site_url: str,
        credentials_path: Optional[str] = None,
    ):
        self.site_url = site_url
        self.credentials_path = credentials_path
        self._authenticated = False
        
        # In production, would initialize Google API client here
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build
    
    def authenticate(self) -> bool:
        """
        Authenticate with GSC API.
        
        Returns True if successful.
        """
        # Production implementation:
        # credentials = service_account.Credentials.from_service_account_file(
        #     self.credentials_path,
        #     scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        # )
        # self.service = build('searchconsole', 'v1', credentials=credentials)
        
        self._authenticated = True
        return True
    
    def fetch_search_analytics(
        self,
        start_date: date,
        end_date: date,
        dimensions: List[str] = None,
        row_limit: int = 1000,
        search_type: SearchType = SearchType.WEB,
    ) -> List[Dict]:
        """
        Fetch search analytics data from GSC.
        
        Dimensions can include: 'date', 'query', 'page', 'device', 'country'
        """
        if dimensions is None:
            dimensions = ['page', 'query']
        
        # Production implementation:
        # request = {
        #     'startDate': start_date.isoformat(),
        #     'endDate': end_date.isoformat(),
        #     'dimensions': dimensions,
        #     'rowLimit': row_limit,
        #     'searchType': search_type.value,
        # }
        # response = self.service.searchanalytics().query(
        #     siteUrl=self.site_url, body=request
        # ).execute()
        # return response.get('rows', [])
        
        # For now, return empty (will be populated by simulator)
        return []
    
    def fetch_page_data(
        self,
        page_url: str,
        start_date: date,
        end_date: date,
    ) -> PageSearchData:
        """Fetch all data for a specific page."""
        # Would combine multiple API calls
        return PageSearchData(
            page_url=page_url,
            date_range_start=start_date,
            date_range_end=end_date,
        )


# ═══════════════════════════════════════════════════════════════════════════
# GSC DATA SIMULATOR (For development/testing)
# ═══════════════════════════════════════════════════════════════════════════

class GSCSimulator:
    """
    Simulates GSC data for development and testing.
    
    Generates realistic search data based on:
    - Profile pages (40 profiles)
    - Blog structure
    - Typical SEO patterns
    """
    
    def __init__(self, site_url: str = "https://quirrely.io"):
        self.site_url = site_url
        
        # Profile-based pages
        self.styles = [
            "assertive", "hedged", "conversational", "formal", "dense",
            "minimal", "poetic", "analytical", "interrogative", "longform"
        ]
        self.certitudes = ["open", "closed", "balanced", "contradictory"]
        
        # Base metrics by page type
        self.base_impressions = {
            "profile_page": (500, 5000),  # (min, max) per 28 days
            "blog_index": (1000, 3000),
            "homepage": (2000, 8000),
        }
    
    def generate_site_data(
        self,
        start_date: date,
        end_date: date,
        seed: int = 42,
    ) -> GSCSiteData:
        """Generate complete simulated GSC data."""
        import random
        random.seed(seed)
        
        site_data = GSCSiteData(
            site_url=self.site_url,
            date_range_start=start_date,
            date_range_end=end_date,
            fetched_at=datetime.utcnow(),
        )
        
        # Generate data for each profile page
        for style in self.styles:
            for certitude in self.certitudes:
                page_url = f"/blog/how-{style}-{certitude}-writers-write"
                page_data = self._generate_page_data(
                    page_url, style, certitude, start_date, end_date, random
                )
                site_data.pages[page_url] = page_data
                
                # Add to total
                site_data.total_metrics = site_data.total_metrics + page_data.metrics
        
        # Generate query data
        site_data.queries = self._generate_query_data(site_data.pages, random)
        
        # Aggregate by device
        for device in DeviceDimension:
            device_metrics = SearchMetrics()
            for page in site_data.pages.values():
                if device.value in page.by_device:
                    device_metrics = device_metrics + page.by_device[device.value]
            site_data.by_device[device.value] = device_metrics
        
        # Aggregate by country
        countries = ["USA", "GBR", "CAN", "AUS", "NZL", "IND"]
        for country in countries:
            country_metrics = SearchMetrics()
            for page in site_data.pages.values():
                if country in page.by_country:
                    country_metrics = country_metrics + page.by_country[country]
            site_data.by_country[country] = country_metrics
        
        return site_data
    
    def _generate_page_data(
        self,
        page_url: str,
        style: str,
        certitude: str,
        start_date: date,
        end_date: date,
        random,
    ) -> PageSearchData:
        """Generate data for a single page."""
        
        # Some profiles are more popular
        popularity_factor = {
            "assertive": 1.5,
            "conversational": 1.3,
            "formal": 1.2,
            "poetic": 0.8,
            "minimal": 0.7,
        }.get(style, 1.0)
        
        # Base impressions
        min_imp, max_imp = self.base_impressions["profile_page"]
        total_impressions = int(random.randint(min_imp, max_imp) * popularity_factor)
        
        # CTR varies by position and quality (1-5%)
        avg_position = random.uniform(8, 35)
        base_ctr = max(0.01, 0.15 - (avg_position * 0.004))  # Higher position = higher CTR
        ctr = base_ctr * random.uniform(0.7, 1.3)
        
        total_clicks = int(total_impressions * ctr)
        
        page_data = PageSearchData(
            page_url=page_url,
            date_range_start=start_date,
            date_range_end=end_date,
            metrics=SearchMetrics(
                clicks=total_clicks,
                impressions=total_impressions,
                ctr=ctr,
                position=avg_position,
            ),
        )
        
        # Generate daily metrics
        days = (end_date - start_date).days + 1
        daily_impressions = total_impressions // days
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_str = day.isoformat()
            # Add some variance
            day_imp = int(daily_impressions * random.uniform(0.5, 1.5))
            day_clicks = int(day_imp * ctr * random.uniform(0.7, 1.3))
            page_data.daily_metrics[day_str] = SearchMetrics(
                clicks=day_clicks,
                impressions=day_imp,
                ctr=day_clicks / day_imp if day_imp > 0 else 0,
                position=avg_position + random.uniform(-3, 3),
            )
        
        # Generate device breakdown (60% mobile, 35% desktop, 5% tablet)
        page_data.by_device = {
            "MOBILE": SearchMetrics(
                clicks=int(total_clicks * 0.60),
                impressions=int(total_impressions * 0.60),
                ctr=ctr * 0.9,  # Mobile CTR slightly lower
                position=avg_position + 1,
            ),
            "DESKTOP": SearchMetrics(
                clicks=int(total_clicks * 0.35),
                impressions=int(total_impressions * 0.35),
                ctr=ctr * 1.1,  # Desktop CTR slightly higher
                position=avg_position - 1,
            ),
            "TABLET": SearchMetrics(
                clicks=int(total_clicks * 0.05),
                impressions=int(total_impressions * 0.05),
                ctr=ctr,
                position=avg_position,
            ),
        }
        
        # Generate country breakdown
        page_data.by_country = {
            "USA": SearchMetrics(clicks=int(total_clicks * 0.40), impressions=int(total_impressions * 0.40), ctr=ctr, position=avg_position),
            "GBR": SearchMetrics(clicks=int(total_clicks * 0.20), impressions=int(total_impressions * 0.20), ctr=ctr, position=avg_position + 2),
            "CAN": SearchMetrics(clicks=int(total_clicks * 0.15), impressions=int(total_impressions * 0.15), ctr=ctr, position=avg_position + 1),
            "AUS": SearchMetrics(clicks=int(total_clicks * 0.10), impressions=int(total_impressions * 0.10), ctr=ctr, position=avg_position + 3),
            "NZL": SearchMetrics(clicks=int(total_clicks * 0.05), impressions=int(total_impressions * 0.05), ctr=ctr, position=avg_position + 4),
            "IND": SearchMetrics(clicks=int(total_clicks * 0.10), impressions=int(total_impressions * 0.10), ctr=ctr * 0.8, position=avg_position + 5),
        }
        
        # Generate top queries
        query_templates = [
            f"{style} writing style",
            f"{style} writer",
            f"how to write {style}",
            f"{style} {certitude} writing",
            f"am i a {style} writer",
            f"{style} voice in writing",
            f"writing personality {style}",
        ]
        
        page_data.top_queries = []
        remaining_clicks = total_clicks
        for i, query in enumerate(query_templates[:5]):
            query_clicks = int(remaining_clicks * random.uniform(0.2, 0.4))
            query_imp = int(query_clicks / ctr) if ctr > 0 else 0
            page_data.top_queries.append((
                query,
                SearchMetrics(
                    clicks=query_clicks,
                    impressions=query_imp,
                    ctr=query_clicks / query_imp if query_imp > 0 else 0,
                    position=avg_position + random.uniform(-5, 5),
                )
            ))
            remaining_clicks -= query_clicks
        
        return page_data
    
    def _generate_query_data(
        self,
        pages: Dict[str, PageSearchData],
        random,
    ) -> Dict[str, QuerySearchData]:
        """Generate query-level data by aggregating from pages."""
        queries = {}
        
        for page_url, page_data in pages.items():
            # Extract style/certitude from URL
            parts = page_url.split("/")[-1].replace("how-", "").replace("-writers-write", "").split("-")
            style = parts[0] if len(parts) > 0 else None
            certitude = parts[1] if len(parts) > 1 else None
            
            for query, metrics in page_data.top_queries:
                if query not in queries:
                    queries[query] = QuerySearchData(
                        query=query,
                        profile_style=style,
                        profile_certitude=certitude,
                    )
                
                queries[query].metrics = queries[query].metrics + metrics
                queries[query].top_pages.append((page_url, metrics))
        
        return queries


# ═══════════════════════════════════════════════════════════════════════════
# GSC DATA STORE
# ═══════════════════════════════════════════════════════════════════════════

class GSCDataStore:
    """
    Stores and manages GSC data over time.
    
    Provides:
    - Historical data storage
    - Trend calculation
    - Comparison between periods
    """
    
    def __init__(self):
        self.snapshots: List[GSCSiteData] = []
        self.latest: Optional[GSCSiteData] = None
    
    def add_snapshot(self, data: GSCSiteData):
        """Add a new data snapshot."""
        self.snapshots.append(data)
        self.latest = data
    
    def get_page_history(self, page_url: str) -> List[Tuple[date, SearchMetrics]]:
        """Get historical metrics for a page."""
        history = []
        for snapshot in self.snapshots:
            if page_url in snapshot.pages:
                history.append((
                    snapshot.date_range_end,
                    snapshot.pages[page_url].metrics,
                ))
        return sorted(history, key=lambda x: x[0])
    
    def compare_periods(
        self,
        current: GSCSiteData,
        previous: GSCSiteData,
    ) -> Dict[str, Dict]:
        """Compare two periods and identify changes."""
        changes = {
            "improved": [],
            "declined": [],
            "new": [],
            "lost": [],
        }
        
        current_pages = set(current.pages.keys())
        previous_pages = set(previous.pages.keys())
        
        # New pages
        for page in current_pages - previous_pages:
            changes["new"].append({
                "page": page,
                "metrics": current.pages[page].metrics,
            })
        
        # Lost pages (no longer ranking)
        for page in previous_pages - current_pages:
            changes["lost"].append({
                "page": page,
                "metrics": previous.pages[page].metrics,
            })
        
        # Compare existing pages
        for page in current_pages & previous_pages:
            curr = current.pages[page].metrics
            prev = previous.pages[page].metrics
            
            click_change = (curr.clicks - prev.clicks) / prev.clicks if prev.clicks > 0 else 0
            position_change = prev.position - curr.position  # Positive = improved
            
            if click_change > 0.1 or position_change > 3:
                changes["improved"].append({
                    "page": page,
                    "click_change": click_change,
                    "position_change": position_change,
                    "current": curr,
                    "previous": prev,
                })
            elif click_change < -0.1 or position_change < -3:
                changes["declined"].append({
                    "page": page,
                    "click_change": click_change,
                    "position_change": position_change,
                    "current": curr,
                    "previous": prev,
                })
        
        return changes


# ═══════════════════════════════════════════════════════════════════════════
# GSC ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class GSCAnalyzer:
    """
    Analyzes GSC data and generates recommendations.
    
    Identifies:
    - High-impression low-CTR opportunities
    - Position improvement targets
    - Content gaps
    - Quick wins
    """
    
    def __init__(self, data: GSCSiteData):
        self.data = data
    
    def get_ctr_opportunities(self, min_impressions: int = 100) -> List[Dict]:
        """
        Find pages with high impressions but low CTR.
        These are opportunities for meta tag optimization.
        """
        opportunities = []
        
        for page_url, page_data in self.data.pages.items():
            m = page_data.metrics
            if m.impressions >= min_impressions:
                # Expected CTR based on position
                expected_ctr = self._expected_ctr_for_position(m.position)
                ctr_gap = expected_ctr - m.ctr
                
                if ctr_gap > 0.01:  # At least 1% below expected
                    opportunities.append({
                        "page": page_url,
                        "impressions": m.impressions,
                        "current_ctr": m.ctr,
                        "expected_ctr": expected_ctr,
                        "ctr_gap": ctr_gap,
                        "potential_clicks": int(m.impressions * ctr_gap),
                        "position": m.position,
                        "priority": "high" if ctr_gap > 0.03 else "medium",
                    })
        
        return sorted(opportunities, key=lambda x: x["potential_clicks"], reverse=True)
    
    def get_position_opportunities(self, max_position: float = 20) -> List[Dict]:
        """
        Find pages on page 2+ that could move to page 1.
        Position 11-20 are prime candidates.
        """
        opportunities = []
        
        for page_url, page_data in self.data.pages.items():
            m = page_data.metrics
            if 10 < m.position <= max_position and m.impressions > 50:
                # Estimate traffic gain from moving to page 1
                current_ctr = m.ctr
                page1_ctr = self._expected_ctr_for_position(5)  # If moved to position 5
                traffic_gain = m.impressions * (page1_ctr - current_ctr)
                
                opportunities.append({
                    "page": page_url,
                    "current_position": m.position,
                    "impressions": m.impressions,
                    "current_clicks": m.clicks,
                    "potential_traffic_gain": int(traffic_gain),
                    "top_queries": [q[0] for q in page_data.top_queries[:3]],
                    "priority": "high" if m.position <= 15 else "medium",
                })
        
        return sorted(opportunities, key=lambda x: x["potential_traffic_gain"], reverse=True)
    
    def get_content_gaps(self) -> List[Dict]:
        """
        Find profile combinations without strong content.
        """
        gaps = []
        
        # Check all profile combinations
        styles = ["assertive", "hedged", "conversational", "formal", "dense",
                  "minimal", "poetic", "analytical", "interrogative", "longform"]
        certitudes = ["open", "closed", "balanced", "contradictory"]
        
        for style in styles:
            for certitude in certitudes:
                page_url = f"/blog/how-{style}-{certitude}-writers-write"
                
                if page_url not in self.data.pages:
                    gaps.append({
                        "profile": f"{style}-{certitude}",
                        "page": page_url,
                        "status": "missing",
                        "priority": "high",
                    })
                else:
                    m = self.data.pages[page_url].metrics
                    if m.impressions < 100:
                        gaps.append({
                            "profile": f"{style}-{certitude}",
                            "page": page_url,
                            "status": "low_visibility",
                            "impressions": m.impressions,
                            "priority": "medium",
                        })
        
        return gaps
    
    def get_quick_wins(self) -> List[Dict]:
        """
        Find pages where small improvements could have big impact.
        """
        wins = []
        
        # CTR opportunities (meta optimization)
        for opp in self.get_ctr_opportunities()[:5]:
            wins.append({
                "type": "ctr_optimization",
                "page": opp["page"],
                "action": "Rewrite meta title/description for higher CTR",
                "effort": "low",
                "impact": f"+{opp['potential_clicks']} potential clicks",
                "priority": opp["priority"],
            })
        
        # Position opportunities (content/link building)
        for opp in self.get_position_opportunities()[:3]:
            if opp["current_position"] <= 15:
                wins.append({
                    "type": "position_improvement",
                    "page": opp["page"],
                    "action": f"Improve content to move from position {opp['current_position']:.1f} to page 1",
                    "effort": "medium",
                    "impact": f"+{opp['potential_traffic_gain']} potential clicks",
                    "priority": opp["priority"],
                })
        
        return wins
    
    def get_trending_queries(self, limit: int = 10) -> List[Dict]:
        """Get queries with growing impressions."""
        # Would require historical data to calculate true trends
        # For now, return top queries by volume
        sorted_queries = sorted(
            self.data.queries.items(),
            key=lambda x: x[1].metrics.impressions,
            reverse=True
        )
        
        return [
            {
                "query": q[0],
                "impressions": q[1].metrics.impressions,
                "clicks": q[1].metrics.clicks,
                "ctr": q[1].metrics.ctr,
                "position": q[1].metrics.position,
                "profile": f"{q[1].profile_style}-{q[1].profile_certitude}" if q[1].profile_style else None,
            }
            for q in sorted_queries[:limit]
        ]
    
    def _expected_ctr_for_position(self, position: float) -> float:
        """
        Expected CTR based on position (industry averages).
        
        Position 1: ~28%
        Position 2: ~15%
        Position 3: ~11%
        Position 4-5: ~8%
        Position 6-10: ~3-5%
        Position 11+: <2%
        """
        if position <= 1:
            return 0.28
        elif position <= 2:
            return 0.15
        elif position <= 3:
            return 0.11
        elif position <= 5:
            return 0.08
        elif position <= 10:
            return 0.04
        elif position <= 20:
            return 0.02
        else:
            return 0.01
    
    def get_summary(self) -> Dict:
        """Get analysis summary."""
        ctr_opps = self.get_ctr_opportunities()
        pos_opps = self.get_position_opportunities()
        gaps = self.get_content_gaps()
        
        return {
            "total_impressions": self.data.total_metrics.impressions,
            "total_clicks": self.data.total_metrics.clicks,
            "overall_ctr": self.data.total_metrics.ctr,
            "avg_position": self.data.total_metrics.position,
            "pages_tracked": len(self.data.pages),
            "queries_tracked": len(self.data.queries),
            "ctr_opportunities": len(ctr_opps),
            "position_opportunities": len(pos_opps),
            "content_gaps": len([g for g in gaps if g["status"] == "missing"]),
            "potential_clicks_from_ctr": sum(o["potential_clicks"] for o in ctr_opps),
            "potential_clicks_from_position": sum(o["potential_traffic_gain"] for o in pos_opps),
        }


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def fetch_gsc_data(
    site_url: str = "https://quirrely.io",
    days: int = 28,
    use_simulator: bool = True,
    credentials_path: str = None,
) -> GSCSiteData:
    """
    Fetch GSC data (real or simulated).
    
    Args:
        site_url: The site URL in GSC
        days: Number of days to fetch
        use_simulator: If True, use simulated data; if False, use real API
        credentials_path: Path to GSC credentials JSON (for real API)
        
    Returns:
        GSCSiteData object with search metrics
    """
    end_date = date.today() - timedelta(days=2)  # GSC has 2-day delay
    start_date = end_date - timedelta(days=days)
    
    if use_simulator:
        simulator = GSCSimulator(site_url)
        return simulator.generate_site_data(start_date, end_date)
    else:
        # Use real GSC API
        try:
            from .gsc_real import fetch_real_gsc_data
            
            result = fetch_real_gsc_data(
                credentials_path=credentials_path,
                site_url=site_url,
                days=days,
            )
            
            if result is None:
                # Fall back to simulator if real API fails
                print("GSC real API failed, falling back to simulator")
                simulator = GSCSimulator(site_url)
                return simulator.generate_site_data(start_date, end_date)
            
            return result
            
        except ImportError as e:
            print(f"GSC real API dependencies not installed: {e}")
            print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            # Fall back to simulator
            simulator = GSCSimulator(site_url)
            return simulator.generate_site_data(start_date, end_date)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════════════════════════

_gsc_store: Optional[GSCDataStore] = None

def get_gsc_store() -> GSCDataStore:
    """Get the global GSC data store."""
    global _gsc_store
    if _gsc_store is None:
        _gsc_store = GSCDataStore()
    return _gsc_store


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "SearchType",
    "DeviceDimension",
    "SearchMetrics",
    "PageSearchData",
    "QuerySearchData",
    "GSCSiteData",
    "GSCClient",
    "GSCSimulator",
    "GSCDataStore",
    "GSCAnalyzer",
    "fetch_gsc_data",
    "get_gsc_store",
]
