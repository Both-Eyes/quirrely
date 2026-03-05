#!/usr/bin/env python3
"""
QUIRRELY ADMIN SECURITY MIDDLEWARE v1.0
Enhanced security controls for administrative endpoints.

Features:
- IP-based access control verification
- Admin session validation
- Security event logging
- Rate limiting compliance
- Access attempt monitoring
"""

import os
import ipaddress
import logging
from datetime import datetime, timedelta
from typing import Optional, Set, List
from dataclasses import dataclass
import hashlib

from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger("quirrely.admin_security")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AdminSecurityConfig:
    """Admin security configuration."""
    
    # Allowed IP ranges for admin access (in addition to Nginx whitelist)
    ALLOWED_IP_RANGES: List[str] = None
    ALLOWED_IPS: List[str] = None
    
    # VPN/Network validation
    REQUIRE_VPN_HEADER: bool = True
    VPN_HEADER_NAME: str = "X-VPN-Verified"
    VPN_HEADER_VALUE: str = "true"
    
    # Rate limiting (backup to Nginx)
    MAX_ATTEMPTS_PER_MINUTE: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Session requirements
    REQUIRE_ADMIN_SESSION: bool = True
    ADMIN_SESSION_TIMEOUT_HOURS: int = 8
    
    def __post_init__(self):
        # Load from environment
        self.ALLOWED_IP_RANGES = self._parse_env_list("ADMIN_ALLOWED_IP_RANGES", [
            "192.168.0.0/16",   # Private networks
            "10.0.0.0/8",
            "172.16.0.0/12",
            "127.0.0.1/32",     # Localhost
        ])
        
        self.ALLOWED_IPS = self._parse_env_list("ADMIN_ALLOWED_IPS", [
            "127.0.0.1"
        ])
        
        self.REQUIRE_VPN_HEADER = os.environ.get("ADMIN_REQUIRE_VPN", "true").lower() == "true"
    
    def _parse_env_list(self, env_var: str, default: List[str]) -> List[str]:
        """Parse comma-separated environment variable."""
        env_value = os.environ.get(env_var)
        if env_value:
            return [item.strip() for item in env_value.split(",") if item.strip()]
        return default

config = AdminSecurityConfig()

# ═══════════════════════════════════════════════════════════════════════════
# IP VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def is_ip_allowed(ip_address: str) -> bool:
    """
    Check if IP address is allowed for admin access.
    
    Args:
        ip_address: Client IP address
        
    Returns:
        True if IP is allowed
    """
    try:
        ip = ipaddress.ip_address(ip_address)
        
        # Check explicit allowed IPs
        if ip_address in config.ALLOWED_IPS:
            return True
        
        # Check IP ranges
        for ip_range in config.ALLOWED_IP_RANGES:
            network = ipaddress.ip_network(ip_range, strict=False)
            if ip in network:
                return True
        
        return False
        
    except ValueError as e:
        logger.warning(f"Invalid IP address format: {ip_address} - {e}")
        return False

def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers (from Nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (original client)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

# ═══════════════════════════════════════════════════════════════════════════
# ACCESS CONTROL
# ═══════════════════════════════════════════════════════════════════════════

class AdminAccessController:
    """Controls admin access attempts and lockouts."""
    
    def __init__(self):
        self._failed_attempts: dict = {}  # IP -> (count, last_attempt)
        self._successful_logins: set = set()  # IPs with valid sessions
    
    def record_failed_attempt(self, ip_address: str):
        """Record a failed admin access attempt."""
        now = datetime.utcnow()
        
        if ip_address in self._failed_attempts:
            count, _ = self._failed_attempts[ip_address]
            self._failed_attempts[ip_address] = (count + 1, now)
        else:
            self._failed_attempts[ip_address] = (1, now)
        
        # Log security event
        logger.warning(f"Failed admin access attempt from {ip_address}")
    
    def record_successful_access(self, ip_address: str):
        """Record successful admin access."""
        # Clear failed attempts
        self._failed_attempts.pop(ip_address, None)
        self._successful_logins.add(ip_address)
        
        logger.info(f"Successful admin access from {ip_address}")
    
    def is_ip_locked_out(self, ip_address: str) -> bool:
        """Check if IP is currently locked out."""
        if ip_address not in self._failed_attempts:
            return False
        
        count, last_attempt = self._failed_attempts[ip_address]
        
        # Check if lockout period has expired
        lockout_expires = last_attempt + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)
        if datetime.utcnow() > lockout_expires:
            # Clear expired lockout
            self._failed_attempts.pop(ip_address, None)
            return False
        
        return count >= config.MAX_ATTEMPTS_PER_MINUTE
    
    def cleanup_expired_entries(self):
        """Clean up expired failed attempt records."""
        now = datetime.utcnow()
        expired_ips = []
        
        for ip, (count, last_attempt) in self._failed_attempts.items():
            if now - last_attempt > timedelta(minutes=config.LOCKOUT_DURATION_MINUTES):
                expired_ips.append(ip)
        
        for ip in expired_ips:
            self._failed_attempts.pop(ip, None)

# Global access controller
access_controller = AdminAccessController()

# ═══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

class AdminSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for admin endpoint security.
    
    Validates:
    - IP whitelist compliance
    - VPN/network verification
    - Rate limiting
    - Access attempts monitoring
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to admin endpoints
        path = request.url.path
        if not (path.startswith('/api/admin/') or path.startswith('/api/secure/') or path.startswith('/ws/metrics')):
            return await call_next(request)
        
        client_ip = get_client_ip(request)
        
        # Check IP lockout first
        if access_controller.is_ip_locked_out(client_ip):
            logger.warning(f"Blocked locked-out IP {client_ip} attempting admin access")
            raise HTTPException(
                status_code=429,
                detail="Too many failed attempts. Access temporarily restricted."
            )
        
        # IP whitelist validation
        if not is_ip_allowed(client_ip):
            access_controller.record_failed_attempt(client_ip)
            logger.error(f"Unauthorized IP {client_ip} attempted admin access to {path}")
            raise HTTPException(
                status_code=403,
                detail="Access denied. Admin access restricted to authorized networks."
            )
        
        # VPN header validation (if required)
        if config.REQUIRE_VPN_HEADER:
            vpn_header = request.headers.get(config.VPN_HEADER_NAME)
            if vpn_header != config.VPN_HEADER_VALUE:
                access_controller.record_failed_attempt(client_ip)
                logger.warning(f"Missing or invalid VPN verification from {client_ip}")
                raise HTTPException(
                    status_code=403,
                    detail="VPN connection required for admin access."
                )
        
        # Nginx admin IP verification (double-check)
        nginx_admin_verified = request.headers.get("X-Admin-IP-Verified")
        if not nginx_admin_verified:
            access_controller.record_failed_attempt(client_ip)
            logger.error(f"Missing Nginx admin verification for {client_ip}")
            raise HTTPException(
                status_code=403,
                detail="Access denied. Network security verification failed."
            )
        
        # Log successful validation
        access_controller.record_successful_access(client_ip)
        
        # Add security context to request
        request.state.admin_ip_verified = True
        request.state.admin_client_ip = client_ip
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Admin-Security"] = "verified"
        response.headers["X-Client-IP"] = client_ip
        
        return response

# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

async def require_admin_ip_verification(request: Request):
    """
    Dependency that ensures admin IP verification.
    
    Usage:
        @router.get("/admin/dashboard")
        async def admin_dashboard(request: Request = Depends(require_admin_ip_verification)):
            return {"status": "authorized"}
    """
    if not getattr(request.state, "admin_ip_verified", False):
        raise HTTPException(
            status_code=403,
            detail="Admin IP verification required"
        )
    
    return request

async def get_admin_client_info(request: Request):
    """
    Get verified admin client information.
    
    Returns:
        Dict with client IP and verification status
    """
    return {
        "client_ip": getattr(request.state, "admin_client_ip", "unknown"),
        "ip_verified": getattr(request.state, "admin_ip_verified", False),
        "timestamp": datetime.utcnow().isoformat()
    }

# ═══════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def log_admin_access_attempt(request: Request, success: bool, details: str = ""):
    """Log admin access attempt with full context."""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "unknown")
    
    log_data = {
        "event": "admin_access_attempt",
        "success": success,
        "client_ip": client_ip,
        "path": request.url.path,
        "method": request.method,
        "user_agent": user_agent,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if success:
        logger.info(f"Admin access granted: {log_data}")
    else:
        logger.warning(f"Admin access denied: {log_data}")

def get_admin_security_status() -> dict:
    """Get current admin security status for monitoring."""
    return {
        "config": {
            "ip_ranges_count": len(config.ALLOWED_IP_RANGES),
            "explicit_ips_count": len(config.ALLOWED_IPS),
            "vpn_required": config.REQUIRE_VPN_HEADER,
            "max_attempts": config.MAX_ATTEMPTS_PER_MINUTE,
            "lockout_duration": config.LOCKOUT_DURATION_MINUTES
        },
        "current_state": {
            "failed_attempts_count": len(access_controller._failed_attempts),
            "successful_logins_count": len(access_controller._successful_logins),
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'AdminSecurityConfig',
    'config',
    'AdminSecurityMiddleware',
    'require_admin_ip_verification',
    'get_admin_client_info',
    'log_admin_access_attempt',
    'get_admin_security_status',
    'is_ip_allowed',
    'get_client_ip'
]