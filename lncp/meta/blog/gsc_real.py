#!/usr/bin/env python3
"""
LNCP META/BLOG: GSC REAL API CLIENT v1.0
Production-ready Google Search Console API client.

This module provides the actual API integration with GSC.

Setup Requirements:
1. Google Cloud Project with Search Console API enabled
2. Service Account with domain-wide delegation OR OAuth2 credentials
3. Site verified in Google Search Console
4. Credentials JSON file

Environment Variables:
- GSC_CREDENTIALS_PATH: Path to service account JSON
- GSC_SITE_URL: The site URL as registered in GSC (e.g., https://quirrely.io)
"""

import os
import json
from datetime import date, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import from main gsc module
from .gsc import (
    SearchMetrics,
    PageSearchData,
    QuerySearchData,
    GSCSiteData,
    SearchType,
    DeviceDimension,
)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class GSCConfig:
    """Configuration for GSC API client."""
    credentials_path: str
    site_url: str
    
    # API settings
    row_limit: int = 25000
    start_row: int = 0
    
    # Default dimensions
    default_dimensions: List[str] = None
    
    # Rate limiting
    requests_per_minute: int = 1200
    
    def __post_init__(self):
        if self.default_dimensions is None:
            self.default_dimensions = ['page', 'query', 'date']
    
    @classmethod
    def from_env(cls) -> 'GSCConfig':
        """Create config from environment variables."""
        return cls(
            credentials_path=os.environ.get('GSC_CREDENTIALS_PATH', 'credentials/gsc-service-account.json'),
            site_url=os.environ.get('GSC_SITE_URL', 'https://quirrely.io'),
        )


# ═══════════════════════════════════════════════════════════════════════════
# REAL GSC CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class RealGSCClient:
    """
    Production Google Search Console API client.
    
    Uses the official Google API client library.
    
    Installation:
        pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
    """
    
    def __init__(self, config: GSCConfig):
        self.config = config
        self.service = None
        self._authenticated = False
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Search Console API.
        
        Returns True if successful, False otherwise.
        """
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.config.credentials_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )
            
            # Build service
            self.service = build(
                'searchconsole',
                'v1',
                credentials=credentials,
                cache_discovery=False,
            )
            
            self._authenticated = True
            return True
            
        except FileNotFoundError:
            print(f"GSC credentials file not found: {self.config.credentials_path}")
            return False
        except Exception as e:
            print(f"GSC authentication failed: {e}")
            return False
    
    def fetch_search_analytics(
        self,
        start_date: date,
        end_date: date,
        dimensions: List[str] = None,
        dimension_filter_groups: List[Dict] = None,
        row_limit: int = None,
        start_row: int = 0,
        search_type: SearchType = SearchType.WEB,
    ) -> List[Dict]:
        """
        Fetch search analytics data from GSC API.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            dimensions: List of dimensions (date, query, page, device, country)
            dimension_filter_groups: Filters to apply
            row_limit: Max rows to return
            start_row: Starting row for pagination
            search_type: Type of search (web, image, video, news)
            
        Returns:
            List of row data from GSC
        """
        if not self._authenticated:
            if not self.authenticate():
                return []
        
        if dimensions is None:
            dimensions = self.config.default_dimensions
        
        if row_limit is None:
            row_limit = self.config.row_limit
        
        request_body = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'dimensions': dimensions,
            'rowLimit': row_limit,
            'startRow': start_row,
            'searchType': search_type.value,
        }
        
        if dimension_filter_groups:
            request_body['dimensionFilterGroups'] = dimension_filter_groups
        
        try:
            response = self.service.searchanalytics().query(
                siteUrl=self.config.site_url,
                body=request_body,
            ).execute()
            
            return response.get('rows', [])
            
        except Exception as e:
            print(f"GSC API request failed: {e}")
            return []
    
    def fetch_all_pages(
        self,
        start_date: date,
        end_date: date,
    ) -> List[Dict]:
        """
        Fetch all pages with their metrics.
        
        Handles pagination automatically.
        """
        all_rows = []
        start_row = 0
        
        while True:
            rows = self.fetch_search_analytics(
                start_date=start_date,
                end_date=end_date,
                dimensions=['page'],
                row_limit=self.config.row_limit,
                start_row=start_row,
            )
            
            if not rows:
                break
            
            all_rows.extend(rows)
            
            if len(rows) < self.config.row_limit:
                break
            
            start_row += self.config.row_limit
        
        return all_rows
    
    def fetch_page_queries(
        self,
        page_url: str,
        start_date: date,
        end_date: date,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Fetch top queries for a specific page.
        """
        return self.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['query'],
            dimension_filter_groups=[{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url,
                }]
            }],
            row_limit=limit,
        )
    
    def fetch_by_device(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, SearchMetrics]:
        """
        Fetch metrics broken down by device.
        """
        rows = self.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['device'],
        )
        
        result = {}
        for row in rows:
            device = row['keys'][0]
            result[device] = SearchMetrics(
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            )
        
        return result
    
    def fetch_by_country(
        self,
        start_date: date,
        end_date: date,
        limit: int = 20,
    ) -> Dict[str, SearchMetrics]:
        """
        Fetch metrics broken down by country.
        """
        rows = self.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['country'],
            row_limit=limit,
        )
        
        result = {}
        for row in rows:
            country = row['keys'][0]
            result[country] = SearchMetrics(
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            )
        
        return result
    
    def fetch_daily_metrics(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, SearchMetrics]:
        """
        Fetch daily metrics for trend analysis.
        """
        rows = self.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['date'],
        )
        
        result = {}
        for row in rows:
            date_str = row['keys'][0]
            result[date_str] = SearchMetrics(
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            )
        
        return result


# ═══════════════════════════════════════════════════════════════════════════
# DATA FETCHER (High-level interface)
# ═══════════════════════════════════════════════════════════════════════════

class GSCDataFetcher:
    """
    High-level interface for fetching and assembling GSC data.
    
    Combines multiple API calls into structured data objects.
    """
    
    def __init__(self, client: RealGSCClient):
        self.client = client
    
    def fetch_site_data(
        self,
        days: int = 28,
        include_queries: bool = True,
        include_daily: bool = True,
    ) -> GSCSiteData:
        """
        Fetch complete site data for the specified period.
        
        Args:
            days: Number of days to fetch (default 28)
            include_queries: Whether to fetch top queries per page
            include_daily: Whether to fetch daily breakdown
            
        Returns:
            GSCSiteData object with all metrics
        """
        # GSC has ~2 day data delay
        end_date = date.today() - timedelta(days=2)
        start_date = end_date - timedelta(days=days)
        
        site_data = GSCSiteData(
            site_url=self.client.config.site_url,
            date_range_start=start_date,
            date_range_end=end_date,
            fetched_at=datetime.utcnow(),
        )
        
        # Fetch all pages
        page_rows = self.client.fetch_all_pages(start_date, end_date)
        
        for row in page_rows:
            page_url = row['keys'][0]
            
            page_data = PageSearchData(
                page_url=page_url,
                date_range_start=start_date,
                date_range_end=end_date,
                metrics=SearchMetrics(
                    clicks=row.get('clicks', 0),
                    impressions=row.get('impressions', 0),
                    ctr=row.get('ctr', 0),
                    position=row.get('position', 0),
                ),
            )
            
            # Fetch queries for this page (optional)
            if include_queries:
                query_rows = self.client.fetch_page_queries(
                    page_url, start_date, end_date, limit=10
                )
                for qrow in query_rows:
                    page_data.top_queries.append((
                        qrow['keys'][0],
                        SearchMetrics(
                            clicks=qrow.get('clicks', 0),
                            impressions=qrow.get('impressions', 0),
                            ctr=qrow.get('ctr', 0),
                            position=qrow.get('position', 0),
                        ),
                    ))
            
            site_data.pages[page_url] = page_data
            site_data.total_metrics = site_data.total_metrics + page_data.metrics
        
        # Fetch device breakdown
        site_data.by_device = self.client.fetch_by_device(start_date, end_date)
        
        # Fetch country breakdown
        site_data.by_country = self.client.fetch_by_country(start_date, end_date)
        
        return site_data
    
    def fetch_page_detail(
        self,
        page_url: str,
        days: int = 28,
    ) -> PageSearchData:
        """
        Fetch detailed data for a single page.
        """
        end_date = date.today() - timedelta(days=2)
        start_date = end_date - timedelta(days=days)
        
        # Overall metrics
        rows = self.client.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['page'],
            dimension_filter_groups=[{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url,
                }]
            }],
        )
        
        if not rows:
            return PageSearchData(
                page_url=page_url,
                date_range_start=start_date,
                date_range_end=end_date,
            )
        
        row = rows[0]
        page_data = PageSearchData(
            page_url=page_url,
            date_range_start=start_date,
            date_range_end=end_date,
            metrics=SearchMetrics(
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
            ),
        )
        
        # Fetch queries
        query_rows = self.client.fetch_page_queries(
            page_url, start_date, end_date, limit=20
        )
        for qrow in query_rows:
            page_data.top_queries.append((
                qrow['keys'][0],
                SearchMetrics(
                    clicks=qrow.get('clicks', 0),
                    impressions=qrow.get('impressions', 0),
                    ctr=qrow.get('ctr', 0),
                    position=qrow.get('position', 0),
                ),
            ))
        
        # Fetch daily metrics
        daily_rows = self.client.fetch_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['date'],
            dimension_filter_groups=[{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page_url,
                }]
            }],
        )
        for drow in daily_rows:
            date_str = drow['keys'][0]
            page_data.daily_metrics[date_str] = SearchMetrics(
                clicks=drow.get('clicks', 0),
                impressions=drow.get('impressions', 0),
                ctr=drow.get('ctr', 0),
                position=drow.get('position', 0),
            )
        
        return page_data


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

from datetime import datetime

def fetch_real_gsc_data(
    credentials_path: str = None,
    site_url: str = None,
    days: int = 28,
) -> Optional[GSCSiteData]:
    """
    Fetch real GSC data using credentials.
    
    Args:
        credentials_path: Path to service account JSON
        site_url: Site URL as registered in GSC
        days: Number of days to fetch
        
    Returns:
        GSCSiteData or None if authentication fails
    """
    config = GSCConfig(
        credentials_path=credentials_path or os.environ.get('GSC_CREDENTIALS_PATH', 'credentials/gsc-service-account.json'),
        site_url=site_url or os.environ.get('GSC_SITE_URL', 'https://quirrely.io'),
    )
    
    client = RealGSCClient(config)
    
    if not client.authenticate():
        return None
    
    fetcher = GSCDataFetcher(client)
    return fetcher.fetch_site_data(days=days)


def check_gsc_credentials(credentials_path: str = None) -> Dict:
    """
    Check if GSC credentials are valid and accessible.
    
    Returns status dict with details.
    """
    path = credentials_path or os.environ.get('GSC_CREDENTIALS_PATH', 'credentials/gsc-service-account.json')
    
    result = {
        "credentials_path": path,
        "file_exists": os.path.exists(path),
        "valid_json": False,
        "has_required_fields": False,
        "authentication_tested": False,
        "authentication_success": False,
        "error": None,
    }
    
    if not result["file_exists"]:
        result["error"] = f"Credentials file not found: {path}"
        return result
    
    try:
        with open(path, 'r') as f:
            creds = json.load(f)
        result["valid_json"] = True
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        result["has_required_fields"] = all(f in creds for f in required_fields)
        
        if not result["has_required_fields"]:
            result["error"] = "Credentials file missing required fields"
            return result
        
    except json.JSONDecodeError as e:
        result["error"] = f"Invalid JSON: {e}"
        return result
    
    # Test authentication
    try:
        config = GSCConfig(credentials_path=path, site_url="https://example.com")
        client = RealGSCClient(config)
        result["authentication_tested"] = True
        result["authentication_success"] = client.authenticate()
        
        if not result["authentication_success"]:
            result["error"] = "Authentication failed"
            
    except Exception as e:
        result["error"] = f"Authentication error: {e}"
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "GSCConfig",
    "RealGSCClient",
    "GSCDataFetcher",
    "fetch_real_gsc_data",
    "check_gsc_credentials",
]
