#!/usr/bin/env python3
"""
QUIRRELY LAUNCH CONFIGURATION v1.0
Multi-country domains, environments, rate limiting, and launch settings.

Domains: quirrely.com (geo-redirect) + .ca / .co.uk / .com.au / .co.nz
Launch Mode: Soft launch
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENVIRONMENTS
# ═══════════════════════════════════════════════════════════════════════════

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


CURRENT_ENV = Environment(os.environ.get("QUIRRELY_ENV", "development"))


ENV_CONFIG = {
    Environment.DEVELOPMENT: {
        "debug": True,
        "api_url": "http://localhost:8000",
        "frontend_url": "http://localhost:3000",
        "database_url": os.environ.get("DEV_DATABASE_URL"),
        "log_level": "DEBUG",
    },
    Environment.STAGING: {
        "debug": True,
        "api_url": "https://api-staging.quirrely.com",
        "frontend_url": "https://staging.quirrely.ca",
        "database_url": os.environ.get("STAGING_DATABASE_URL"),
        "log_level": "INFO",
    },
    Environment.PRODUCTION: {
        "debug": False,
        "api_url": "https://api.quirrely.com",
        "frontend_url": "https://quirrely.ca",
        "database_url": os.environ.get("DATABASE_URL"),
        "log_level": "WARNING",
    },
}


def get_config(key: str):
    """Get config value for current environment."""
    return ENV_CONFIG.get(CURRENT_ENV, {}).get(key)


# ═══════════════════════════════════════════════════════════════════════════
# MULTI-COUNTRY DOMAINS
# ═══════════════════════════════════════════════════════════════════════════

class Country(str, Enum):
    CANADA = "ca"
    UK = "uk"
    AUSTRALIA = "au"
    NEW_ZEALAND = "nz"


@dataclass
class CountryConfig:
    """Configuration for a country."""
    code: str
    name: str
    domain: str
    currency: str
    currency_symbol: str
    flag: str
    timezone: str
    affiliate_partner: str
    affiliate_name: str


COUNTRY_CONFIGS: Dict[Country, CountryConfig] = {
    Country.CANADA: CountryConfig(
        code="ca",
        name="Canada",
        domain="quirrely.ca",
        currency="cad",
        currency_symbol="$",
        flag="🇨🇦",
        timezone="America/Toronto",
        affiliate_partner="indigo",
        affiliate_name="Indigo",
    ),
    Country.UK: CountryConfig(
        code="uk",
        name="United Kingdom",
        domain="quirrely.co.uk",
        currency="gbp",
        currency_symbol="£",
        flag="🇬🇧",
        timezone="Europe/London",
        affiliate_partner="bookshop_uk",
        affiliate_name="Bookshop.org",
    ),
    Country.AUSTRALIA: CountryConfig(
        code="au",
        name="Australia",
        domain="quirrely.com.au",
        currency="aud",
        currency_symbol="$",
        flag="🇦🇺",
        timezone="Australia/Sydney",
        affiliate_partner="booktopia",
        affiliate_name="Booktopia",
    ),
    Country.NEW_ZEALAND: CountryConfig(
        code="nz",
        name="New Zealand",
        domain="quirrely.co.nz",
        currency="nzd",
        currency_symbol="$",
        flag="🇳🇿",
        timezone="Pacific/Auckland",
        affiliate_partner="mighty_ape",
        affiliate_name="Mighty Ape",
    ),
}

# Default country (for unknown geo)
DEFAULT_COUNTRY = Country.CANADA

# Global redirect domain
GLOBAL_DOMAIN = "quirrely.com"

# API domain (shared across all countries)
API_DOMAIN = "api.quirrely.com"


def get_country_by_domain(domain: str) -> Optional[Country]:
    """Get country from domain."""
    for country, config in COUNTRY_CONFIGS.items():
        if config.domain == domain:
            return country
    return None


def get_country_by_code(code: str) -> Optional[Country]:
    """Get country from code."""
    for country, config in COUNTRY_CONFIGS.items():
        if config.code == code:
            return country
    return None


# Geo-IP to country mapping (ISO country codes)
GEO_COUNTRY_MAP = {
    "CA": Country.CANADA,
    "GB": Country.UK,
    "UK": Country.UK,  # Alias
    "AU": Country.AUSTRALIA,
    "NZ": Country.NEW_ZEALAND,
}


def get_country_from_geo(iso_code: str) -> Country:
    """Get country from ISO geo code, default to Canada."""
    return GEO_COUNTRY_MAP.get(iso_code.upper(), DEFAULT_COUNTRY)


# ═══════════════════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    window_seconds: int


RATE_LIMITS = {
    # Auth endpoints (strict)
    "auth_login": RateLimit(10, 60),      # 10/minute
    "auth_signup": RateLimit(10, 60),     # 10/minute
    "auth_password_reset": RateLimit(5, 60),  # 5/minute
    
    # API general
    "api_default": RateLimit(100, 60),    # 100/minute
    
    # Analysis (resource-intensive)
    "analysis": RateLimit(20, 60),        # 20/minute
    
    # Admin
    "admin": RateLimit(60, 60),           # 60/minute
    
    # Public (unauthenticated)
    "public": RateLimit(30, 60),          # 30/minute
}


def get_rate_limit(endpoint_type: str) -> RateLimit:
    """Get rate limit for endpoint type."""
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["api_default"])


# ═══════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

CORS_ORIGINS = [
    # Production
    "https://quirrely.com",
    "https://quirrely.ca",
    "https://quirrely.co.uk",
    "https://quirrely.com.au",
    "https://quirrely.co.nz",
    
    # Staging
    "https://staging.quirrely.ca",
    
    # Development
    "http://localhost:3000",
    "http://localhost:5173",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "X-Country-Code"]


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY
# ═══════════════════════════════════════════════════════════════════════════

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# CSP (Content Security Policy)
CSP_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "https://plausible.io"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'", "https://api.quirrely.com", "https://plausible.io"],
    "frame-ancestors": ["'none'"],
}


def build_csp_header() -> str:
    """Build CSP header string."""
    parts = []
    for directive, sources in CSP_POLICY.items():
        parts.append(f"{directive} {' '.join(sources)}")
    return "; ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# MONITORING & ALERTS
# ═══════════════════════════════════════════════════════════════════════════

MONITORING_CONFIG = {
    "uptime": {
        "provider": "better_uptime",  # or "uptimerobot"
        "check_interval_seconds": 60,
        "endpoints": [
            "https://quirrely.ca/api/health",
            "https://quirrely.co.uk/api/health",
            "https://quirrely.com.au/api/health",
            "https://quirrely.co.nz/api/health",
        ],
    },
    "errors": {
        "provider": "sentry",
        "dsn": os.environ.get("SENTRY_DSN"),
        "environment": CURRENT_ENV.value,
        "sample_rate": 1.0 if CURRENT_ENV == Environment.PRODUCTION else 0.0,
    },
    "alerts": {
        "email": os.environ.get("ALERT_EMAIL", "alerts@quirrely.com"),
        "slack_webhook": os.environ.get("SLACK_ALERT_WEBHOOK"),
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# BACKUP CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

BACKUP_CONFIG = {
    "database": {
        "provider": "supabase",  # Handled by Supabase
        "daily_backup": True,
        "retention_days": 30,
        "point_in_time_recovery": True,
        "pitr_retention_days": 7,
    },
    "code": {
        "provider": "git",
        "remote": "github",
        "retention": "forever",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# SUPPORT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

SUPPORT_CONFIG = {
    "email": "support@quirrely.com",
    "help_url": "https://quirrely.ca/help",
    "feedback_enabled": True,
    "live_chat": False,  # Not for launch
}


# ═══════════════════════════════════════════════════════════════════════════
# LAUNCH MODE
# ═══════════════════════════════════════════════════════════════════════════

LAUNCH_MODE = "soft"  # "soft" or "big_bang"

SOFT_LAUNCH_CONFIG = {
    "public_signup": True,
    "marketing_enabled": False,
    "feature_flags_conservative": True,
    "monitoring_extra_verbose": True,
}
