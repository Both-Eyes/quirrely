#!/usr/bin/env python3
"""
QUIRRELY GEO-REDIRECT & MULTI-DOMAIN v1.0
Handles geo-detection, country redirect, and domain-specific configuration.

Domains:
- quirrely.com (geo-redirect entry point)
- quirrely.ca (Canada)
- quirrely.co.uk (UK)
- quirrely.com.au (Australia)
- quirrely.co.nz (New Zealand)
- quirrely.com (United States)
"""

from typing import Optional, Dict
from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from launch_config import (
    Country,
    CountryConfig,
    COUNTRY_CONFIGS,
    DEFAULT_COUNTRY,
    GLOBAL_DOMAIN,
    get_country_from_geo,
    get_country_by_domain,
    get_country_by_code,
)


# ═══════════════════════════════════════════════════════════════════════════
# GEO-DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def get_geo_country_from_request(request: Request) -> Optional[str]:
    """
    Extract country code from request headers.
    Works with Vercel, Cloudflare, and other edge providers.
    """
    # Vercel
    country = request.headers.get("x-vercel-ip-country")
    if country:
        return country.upper()
    
    # Cloudflare
    country = request.headers.get("cf-ipcountry")
    if country:
        return country.upper()
    
    # Generic
    country = request.headers.get("x-country-code")
    if country:
        return country.upper()
    
    return None


def get_user_country_preference(request: Request) -> Optional[Country]:
    """
    Get user's country preference from cookie or query param.
    Allows manual override of geo-detection.
    """
    # Check query param (for manual switch)
    country_code = request.query_params.get("country")
    if country_code:
        country = get_country_by_code(country_code)
        if country:
            return country
    
    # Check cookie
    country_code = request.cookies.get("quirrely_country")
    if country_code:
        country = get_country_by_code(country_code)
        if country:
            return country
    
    return None


def determine_country(request: Request) -> Country:
    """
    Determine the appropriate country for the request.
    Priority: User preference > Geo-detection > Default
    """
    # 1. User preference (cookie or query param)
    preference = get_user_country_preference(request)
    if preference:
        return preference
    
    # 2. Geo-detection
    geo_code = get_geo_country_from_request(request)
    if geo_code:
        return get_country_from_geo(geo_code)
    
    # 3. Default to Canada
    return DEFAULT_COUNTRY


# ═══════════════════════════════════════════════════════════════════════════
# REDIRECT LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def should_redirect(request: Request) -> bool:
    """Check if request should be redirected to country domain."""
    host = request.headers.get("host", "").lower()
    
    # Only redirect from global domain
    if GLOBAL_DOMAIN not in host:
        return False
    
    # Don't redirect API calls
    if request.url.path.startswith("/api"):
        return False
    
    # Don't redirect health checks
    if request.url.path in ["/health", "/api/health"]:
        return False
    
    return True


def get_redirect_url(request: Request, country: Country) -> str:
    """Build redirect URL for country domain."""
    config = COUNTRY_CONFIGS[country]
    
    # Preserve path and query
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    
    url = f"https://{config.domain}{path}"
    if query:
        url += f"?{query}"
    
    return url


def create_country_redirect(request: Request) -> Optional[RedirectResponse]:
    """
    Create redirect response to appropriate country domain.
    Returns None if no redirect needed.
    """
    if not should_redirect(request):
        return None
    
    country = determine_country(request)
    redirect_url = get_redirect_url(request, country)
    
    response = RedirectResponse(url=redirect_url, status_code=302)
    
    # Set country cookie for future visits
    response.set_cookie(
        key="quirrely_country",
        value=country.value,
        max_age=60 * 60 * 24 * 365,  # 1 year
        httponly=True,
        secure=True,
        samesite="lax",
    )
    
    return response


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN CONTEXT
# ═══════════════════════════════════════════════════════════════════════════

def get_country_from_request(request: Request) -> Country:
    """
    Get country from the current domain.
    For use on country-specific domains.
    """
    host = request.headers.get("host", "").lower()
    
    # Check each country domain
    for country, config in COUNTRY_CONFIGS.items():
        if config.domain in host:
            return country
    
    # Check for user preference
    preference = get_user_country_preference(request)
    if preference:
        return preference
    
    # Default
    return DEFAULT_COUNTRY


def get_country_config(request: Request) -> CountryConfig:
    """Get full country config for current request."""
    country = get_country_from_request(request)
    return COUNTRY_CONFIGS[country]


# ═══════════════════════════════════════════════════════════════════════════
# COUNTRY SWITCHER
# ═══════════════════════════════════════════════════════════════════════════

def get_country_switcher_data(current_country: Country) -> list:
    """Get data for country switcher dropdown."""
    return [
        {
            "code": config.code,
            "name": config.name,
            "flag": config.flag,
            "domain": config.domain,
            "currency": config.currency.upper(),
            "is_current": country == current_country,
        }
        for country, config in COUNTRY_CONFIGS.items()
    ]


def switch_country_url(request: Request, target_country: Country) -> str:
    """Generate URL to switch to another country domain."""
    config = COUNTRY_CONFIGS[target_country]
    path = request.url.path
    
    return f"https://{config.domain}{path}?country={config.code}"


# ═══════════════════════════════════════════════════════════════════════════
# SEO: HREFLANG TAGS
# ═══════════════════════════════════════════════════════════════════════════

# Pages that need hreflang (content differs by country)
HREFLANG_PAGES = [
    "/",
    "/pricing",
    "/featured",
    "/featured/writers",
    "/featured/curators",
    "/featured/authority",
]


def should_include_hreflang(path: str) -> bool:
    """Check if page should have hreflang tags."""
    return path in HREFLANG_PAGES


def generate_hreflang_tags(path: str) -> list:
    """
    Generate hreflang tags for a page.
    Only for pages where content actually differs.
    """
    if not should_include_hreflang(path):
        return []
    
    tags = []
    
    for country, config in COUNTRY_CONFIGS.items():
        # Map country to hreflang locale
        locale_map = {
            Country.CANADA: "en-CA",
            Country.UK: "en-GB",
            Country.AUSTRALIA: "en-AU",
            Country.NEW_ZEALAND: "en-NZ",
            Country.US: "en-US",
        }
        
        tags.append({
            "hreflang": locale_map[country],
            "href": f"https://{config.domain}{path}",
        })
    
    # x-default (global entry point)
    tags.append({
        "hreflang": "x-default",
        "href": f"https://{GLOBAL_DOMAIN}{path}",
    })
    
    return tags


def render_hreflang_html(path: str) -> str:
    """Render hreflang tags as HTML."""
    tags = generate_hreflang_tags(path)
    
    if not tags:
        return ""
    
    lines = []
    for tag in tags:
        lines.append(f'<link rel="alternate" hreflang="{tag["hreflang"]}" href="{tag["href"]}" />')
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# SEO: CANONICAL URLS
# ═══════════════════════════════════════════════════════════════════════════

def get_canonical_url(request: Request) -> str:
    """
    Get canonical URL for current page.
    - For hreflang pages: current domain is canonical
    - For other pages: quirrely.ca is canonical
    """
    path = request.url.path
    
    if should_include_hreflang(path):
        # Each country version is its own canonical
        country_config = get_country_config(request)
        return f"https://{country_config.domain}{path}"
    else:
        # Default to Canada for identical content (blog posts, etc.)
        return f"https://{COUNTRY_CONFIGS[DEFAULT_COUNTRY].domain}{path}"
