#!/usr/bin/env python3
"""
LNCP Country Gate Middleware
Version: 1.0.0

Enforces geographic restrictions on API access.
Quirrely is only available in: Canada, UK, Australia, New Zealand (NO USA)

Usage:
    from middleware.country_gate import CountryGate, get_country_gate
    
    # As FastAPI middleware
    app.add_middleware(CountryGateMiddleware)
    
    # Or as dependency
    @app.get("/protected")
    async def protected_route(country: str = Depends(get_country_gate)):
        ...
"""

from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Optional, Set, Tuple
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CountryGateConfig:
    """Country gate configuration."""
    
    # Allowed countries (ISO 3166-1 alpha-2 codes)
    ALLOWED_COUNTRIES: Set[str] = None
    
    # Blocked countries (explicit block list)
    BLOCKED_COUNTRIES: Set[str] = None
    
    # IPs to skip (localhost, internal)
    SKIP_IPS: Set[str] = None
    
    # Paths to skip (health checks, public endpoints)
    SKIP_PATHS: Set[str] = None
    
    # GeoIP database path
    GEOIP_DB_PATH: str = None
    
    # Enable/disable enforcement
    ENABLED: bool = True
    
    # Log blocked requests
    LOG_BLOCKED: bool = True
    
    def __post_init__(self):
        self.ALLOWED_COUNTRIES = self.ALLOWED_COUNTRIES or {'CA', 'GB', 'AU', 'NZ'}
        self.BLOCKED_COUNTRIES = self.BLOCKED_COUNTRIES or {'US'}
        self.SKIP_IPS = self.SKIP_IPS or {
            '127.0.0.1', 
            '::1', 
            'localhost',
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16',
        }
        self.SKIP_PATHS = self.SKIP_PATHS or {
            '/health',
            '/healthz',
            '/ready',
            '/metrics',
            '/api/health',
            '/api/status',
            '/',
            '/docs',
            '/redoc',
            '/openapi.json',
        }
        self.GEOIP_DB_PATH = self.GEOIP_DB_PATH or os.environ.get(
            'GEOIP_DB_PATH', 
            '/var/lib/GeoIP/GeoLite2-Country.mmdb'
        )


# Default configuration
DEFAULT_CONFIG = CountryGateConfig()


# ═══════════════════════════════════════════════════════════════════════════
# GEOIP LOOKUP
# ═══════════════════════════════════════════════════════════════════════════

class GeoIPLookup:
    """
    GeoIP lookup service.
    
    Supports multiple backends:
    1. MaxMind GeoLite2 database (preferred)
    2. IP-API.com (fallback, rate limited)
    3. Mock mode (development)
    """
    
    def __init__(self, config: CountryGateConfig = None):
        self.config = config or DEFAULT_CONFIG
        self._reader = None
        self._init_geoip()
    
    def _init_geoip(self):
        """Initialize GeoIP database reader."""
        try:
            import geoip2.database
            if os.path.exists(self.config.GEOIP_DB_PATH):
                self._reader = geoip2.database.Reader(self.config.GEOIP_DB_PATH)
                logger.info(f"GeoIP database loaded: {self.config.GEOIP_DB_PATH}")
            else:
                logger.warning(f"GeoIP database not found: {self.config.GEOIP_DB_PATH}")
                logger.warning("Falling back to IP-API lookup")
        except ImportError:
            logger.warning("geoip2 not installed. Using IP-API fallback.")
        except Exception as e:
            logger.error(f"Failed to load GeoIP database: {e}")
    
    def lookup(self, ip: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Look up country for IP address.
        
        Returns:
            Tuple of (country_code, country_name) or (None, None) if lookup fails
        """
        # Skip private/local IPs
        if self._is_private_ip(ip):
            return ('LOCAL', 'Local Network')
        
        # Try MaxMind database first
        if self._reader:
            try:
                response = self._reader.country(ip)
                return (
                    response.country.iso_code,
                    response.country.name
                )
            except Exception as e:
                logger.debug(f"GeoIP lookup failed for {ip}: {e}")
        
        # Fallback to IP-API
        return self._lookup_ipapi(ip)
    
    def _lookup_ipapi(self, ip: str) -> Tuple[Optional[str], Optional[str]]:
        """Fallback lookup using IP-API.com (free tier: 45 req/min)."""
        try:
            import requests
            response = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,countryCode,country",
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return (data.get('countryCode'), data.get('country'))
        except Exception as e:
            logger.debug(f"IP-API lookup failed for {ip}: {e}")
        
        return (None, None)
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/local."""
        if ip in ('127.0.0.1', '::1', 'localhost'):
            return True
        
        try:
            import ipaddress
            addr = ipaddress.ip_address(ip)
            return addr.is_private or addr.is_loopback or addr.is_reserved
        except ValueError:
            return False
    
    def close(self):
        """Close the GeoIP database reader."""
        if self._reader:
            self._reader.close()
            self._reader = None


# Singleton instance
_geoip_lookup: Optional[GeoIPLookup] = None

def get_geoip_lookup() -> GeoIPLookup:
    """Get or create GeoIP lookup instance."""
    global _geoip_lookup
    if _geoip_lookup is None:
        _geoip_lookup = GeoIPLookup()
    return _geoip_lookup


# ═══════════════════════════════════════════════════════════════════════════
# COUNTRY GATE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CountryCheckResult:
    """Result of a country check."""
    allowed: bool
    country_code: Optional[str]
    country_name: Optional[str]
    reason: str
    ip: str
    timestamp: datetime = None
    
    def __post_init__(self):
        self.timestamp = self.timestamp or datetime.utcnow()


class CountryGate:
    """
    Country gate enforcement.
    
    Determines whether a request should be allowed based on geographic origin.
    """
    
    def __init__(self, config: CountryGateConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.geoip = get_geoip_lookup()
        self._blocked_log: list = []
    
    def check(self, ip: str, path: str = None) -> CountryCheckResult:
        """
        Check if request from IP should be allowed.
        
        Args:
            ip: Client IP address
            path: Request path (optional, for path-based skipping)
            
        Returns:
            CountryCheckResult with decision
        """
        # Skip if disabled
        if not self.config.ENABLED:
            return CountryCheckResult(
                allowed=True,
                country_code=None,
                country_name=None,
                reason="enforcement_disabled",
                ip=ip
            )
        
        # Skip certain paths
        if path and path in self.config.SKIP_PATHS:
            return CountryCheckResult(
                allowed=True,
                country_code=None,
                country_name=None,
                reason="path_skipped",
                ip=ip
            )
        
        # Skip private/local IPs
        if self._should_skip_ip(ip):
            return CountryCheckResult(
                allowed=True,
                country_code='LOCAL',
                country_name='Local Network',
                reason="local_ip_skipped",
                ip=ip
            )
        
        # Look up country
        country_code, country_name = self.geoip.lookup(ip)
        
        # Handle lookup failure
        if country_code is None:
            # Fail open or closed based on config
            # For now, fail open (allow) but log
            logger.warning(f"GeoIP lookup failed for {ip}, allowing request")
            return CountryCheckResult(
                allowed=True,
                country_code=None,
                country_name=None,
                reason="lookup_failed_allow",
                ip=ip
            )
        
        # Check if explicitly blocked
        if country_code in self.config.BLOCKED_COUNTRIES:
            result = CountryCheckResult(
                allowed=False,
                country_code=country_code,
                country_name=country_name,
                reason="country_blocked",
                ip=ip
            )
            self._log_blocked(result)
            return result
        
        # Check if in allowed list
        if country_code in self.config.ALLOWED_COUNTRIES:
            return CountryCheckResult(
                allowed=True,
                country_code=country_code,
                country_name=country_name,
                reason="country_allowed",
                ip=ip
            )
        
        # Not in allowed list = blocked
        result = CountryCheckResult(
            allowed=False,
            country_code=country_code,
            country_name=country_name,
            reason="country_not_in_allowlist",
            ip=ip
        )
        self._log_blocked(result)
        return result
    
    def _should_skip_ip(self, ip: str) -> bool:
        """Check if IP should be skipped."""
        if ip in self.config.SKIP_IPS:
            return True
        
        try:
            import ipaddress
            addr = ipaddress.ip_address(ip)
            return addr.is_private or addr.is_loopback
        except ValueError:
            return False
    
    def _log_blocked(self, result: CountryCheckResult):
        """Log blocked request."""
        if self.config.LOG_BLOCKED:
            log_entry = {
                'timestamp': result.timestamp.isoformat(),
                'ip': result.ip,
                'country_code': result.country_code,
                'country_name': result.country_name,
                'reason': result.reason,
            }
            self._blocked_log.append(log_entry)
            logger.warning(f"Country gate blocked: {log_entry}")
    
    def get_blocked_log(self, limit: int = 100) -> list:
        """Get recent blocked requests."""
        return self._blocked_log[-limit:]


# Singleton instance
_country_gate: Optional[CountryGate] = None

def get_country_gate() -> CountryGate:
    """Get or create CountryGate instance."""
    global _country_gate
    if _country_gate is None:
        _country_gate = CountryGate()
    return _country_gate


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

class CountryGateMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for country gate enforcement.
    
    Usage:
        from middleware.country_gate import CountryGateMiddleware
        app.add_middleware(CountryGateMiddleware)
    """
    
    def __init__(self, app, config: CountryGateConfig = None):
        super().__init__(app)
        self.gate = CountryGate(config)
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP (handle proxies)
        ip = self._get_client_ip(request)
        path = request.url.path
        
        # Check country
        result = self.gate.check(ip, path)
        
        if not result.allowed:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "geographic_restriction",
                    "message": "Quirrely is not available in your region.",
                    "detail": "We currently serve Canada, United Kingdom, Australia, and New Zealand only.",
                    "country_detected": result.country_name,
                    "support_email": "support@quirrely.com"
                }
            )
        
        # Add country info to request state for downstream use
        request.state.country_code = result.country_code
        request.state.country_name = result.country_name
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP, handling proxy headers."""
        # Check X-Forwarded-For (from reverse proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP (nginx)
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return '127.0.0.1'


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

async def require_allowed_country(request: Request) -> CountryCheckResult:
    """
    FastAPI dependency to enforce country restrictions.
    
    Usage:
        @app.get("/protected")
        async def protected(country: CountryCheckResult = Depends(require_allowed_country)):
            return {"country": country.country_code}
    """
    gate = get_country_gate()
    ip = _get_request_ip(request)
    path = request.url.path
    
    result = gate.check(ip, path)
    
    if not result.allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "geographic_restriction",
                "message": "Quirrely is not available in your region.",
                "country_detected": result.country_name,
            }
        )
    
    return result


def _get_request_ip(request: Request) -> str:
    """Extract client IP from request."""
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()
    
    if request.client:
        return request.client.host
    
    return '127.0.0.1'


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_allowed_country(country_code: str):
    """Add a country to the allowed list."""
    gate = get_country_gate()
    gate.config.ALLOWED_COUNTRIES.add(country_code.upper())
    logger.info(f"Added {country_code} to allowed countries")


def remove_allowed_country(country_code: str):
    """Remove a country from the allowed list."""
    gate = get_country_gate()
    gate.config.ALLOWED_COUNTRIES.discard(country_code.upper())
    logger.info(f"Removed {country_code} from allowed countries")


def add_blocked_country(country_code: str):
    """Add a country to the blocked list."""
    gate = get_country_gate()
    gate.config.BLOCKED_COUNTRIES.add(country_code.upper())
    logger.info(f"Added {country_code} to blocked countries")


def set_enforcement_enabled(enabled: bool):
    """Enable or disable country enforcement."""
    gate = get_country_gate()
    gate.config.ENABLED = enabled
    logger.info(f"Country enforcement {'enabled' if enabled else 'disabled'}")


def get_enforcement_status() -> dict:
    """Get current enforcement status."""
    gate = get_country_gate()
    return {
        "enabled": gate.config.ENABLED,
        "allowed_countries": list(gate.config.ALLOWED_COUNTRIES),
        "blocked_countries": list(gate.config.BLOCKED_COUNTRIES),
        "recent_blocks": len(gate.get_blocked_log(100)),
    }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test the module
    gate = get_country_gate()
    
    # Test local IP
    result = gate.check('127.0.0.1')
    print(f"Local IP: {result}")
    
    # Test with enforcement
    print(f"Status: {get_enforcement_status()}")
