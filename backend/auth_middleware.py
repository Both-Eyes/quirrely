#!/usr/bin/env python3
"""
QUIRRELY AUTH MIDDLEWARE v1.0
Secure httpOnly cookie authentication middleware.

This module provides:
1. httpOnly cookie-based JWT authentication
2. Automatic token refresh
3. Secure cookie settings for production
4. CSRF protection via SameSite cookies

Usage:
    from auth_middleware import (
        set_auth_cookies,
        clear_auth_cookies,
        get_user_from_cookie,
        AuthCookieMiddleware,
    )
"""

from __future__ import annotations

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AuthCookieConfig:
    """Authentication cookie configuration."""
    
    # Cookie names
    ACCESS_TOKEN_COOKIE: str = "quirrely_auth"
    REFRESH_TOKEN_COOKIE: str = "quirrely_refresh"
    
    # Cookie settings
    COOKIE_DOMAIN: Optional[str] = None  # None = current domain only
    COOKIE_PATH: str = "/"
    COOKIE_SECURE: bool = True  # HTTPS only in production
    COOKIE_HTTPONLY: bool = True  # Not accessible via JavaScript
    COOKIE_SAMESITE: str = "lax"  # Protects against CSRF
    
    # Token lifetimes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 1 week
    
    # JWT settings
    JWT_SECRET: str = None
    JWT_ALGORITHM: str = "HS256"
    
    def __post_init__(self):
        # Get from environment
        self.JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-change-in-production')
        self.COOKIE_SECURE = os.environ.get('ENVIRONMENT', 'development') == 'production'
        self.COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN', None)


# Default configuration
config = AuthCookieConfig()


# ═══════════════════════════════════════════════════════════════════════════
# JWT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def create_access_token(
    user_id: str,
    email: str,
    tier: str,
    addons: list = None,
    extra_claims: Dict[str, Any] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        tier: User's subscription tier
        addons: User's active addons
        extra_claims: Additional JWT claims
        
    Returns:
        Encoded JWT token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_id,
        "email": email,
        "tier": tier,
        "addons": addons or [],
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    
    if extra_claims:
        payload.update(extra_claims)
    
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }
    
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.debug("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid token: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """Check if a token is expired."""
    payload = decode_token(token)
    return payload is None


# ═══════════════════════════════════════════════════════════════════════════
# COOKIE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def set_auth_cookies(
    response: Response,
    user_id: str,
    email: str,
    tier: str,
    addons: list = None,
) -> Tuple[str, str]:
    """
    Set authentication cookies on response.
    
    Args:
        response: FastAPI Response object
        user_id: User's unique identifier
        email: User's email
        tier: User's subscription tier
        addons: User's active addons
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = create_access_token(user_id, email, tier, addons)
    refresh_token = create_refresh_token(user_id)
    
    # Set access token cookie
    response.set_cookie(
        key=config.ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    
    # Set refresh token cookie
    response.set_cookie(
        key=config.REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    
    logger.info(f"Auth cookies set for user {user_id}")
    
    return access_token, refresh_token


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies from response.
    
    Args:
        response: FastAPI Response object
    """
    response.delete_cookie(
        key=config.ACCESS_TOKEN_COOKIE,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
    )
    response.delete_cookie(
        key=config.REFRESH_TOKEN_COOKIE,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
    )
    
    logger.info("Auth cookies cleared")


def get_token_from_cookie(request: Request, cookie_name: str) -> Optional[str]:
    """
    Get token from request cookie.
    
    Args:
        request: FastAPI Request object
        cookie_name: Name of the cookie
        
    Returns:
        Token string or None
    """
    return request.cookies.get(cookie_name)


def get_access_token(request: Request) -> Optional[str]:
    """Get access token from request."""
    return get_token_from_cookie(request, config.ACCESS_TOKEN_COOKIE)


def get_refresh_token(request: Request) -> Optional[str]:
    """Get refresh token from request."""
    return get_token_from_cookie(request, config.REFRESH_TOKEN_COOKIE)


# ═══════════════════════════════════════════════════════════════════════════
# USER EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AuthenticatedUser:
    """Represents an authenticated user from cookie."""
    id: str
    email: str
    tier: str
    addons: list
    token_type: str  # "access" or "refresh"


def get_user_from_cookie(request: Request) -> Optional[AuthenticatedUser]:
    """
    Extract authenticated user from request cookies.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        AuthenticatedUser or None if not authenticated
    """
    # Try access token first
    access_token = get_access_token(request)
    if access_token:
        payload = decode_token(access_token)
        if payload and payload.get("type") == "access":
            return AuthenticatedUser(
                id=payload["sub"],
                email=payload.get("email", ""),
                tier=payload.get("tier", "free"),
                addons=payload.get("addons", []),
                token_type="access",
            )
    
    # Try refresh token (for token refresh flow)
    refresh_token = get_refresh_token(request)
    if refresh_token:
        payload = decode_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            return AuthenticatedUser(
                id=payload["sub"],
                email="",  # Refresh token doesn't contain email
                tier="",   # Need to fetch from DB
                addons=[],
                token_type="refresh",
            )
    
    return None


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════

class AuthCookieMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle cookie-based authentication.
    
    - Extracts user from cookies
    - Adds user to request.state
    - Handles automatic token refresh
    """
    
    def __init__(self, app, auto_refresh: bool = True):
        super().__init__(app)
        self.auto_refresh = auto_refresh
    
    async def dispatch(self, request: Request, call_next):
        # Extract user from cookies
        user = get_user_from_cookie(request)
        
        if user:
            request.state.user = user
            request.state.authenticated = True
            
            # Check if access token needs refresh
            if self.auto_refresh and user.token_type == "refresh":
                # Access token expired but refresh token valid
                # The endpoint should handle token refresh
                request.state.needs_refresh = True
            else:
                request.state.needs_refresh = False
        else:
            request.state.user = None
            request.state.authenticated = False
            request.state.needs_refresh = False
        
        response = await call_next(request)
        
        return response


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

async def require_auth_cookie(request: Request) -> AuthenticatedUser:
    """
    Dependency that requires cookie authentication.
    
    Usage:
        @router.get("/protected")
        async def protected(user: AuthenticatedUser = Depends(require_auth_cookie)):
            return {"user_id": user.id}
    """
    user = get_user_from_cookie(request)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )
    
    if user.token_type == "refresh":
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh.",
            headers={"X-Token-Expired": "true"},
        )
    
    return user


async def get_auth_cookie_optional(request: Request) -> Optional[AuthenticatedUser]:
    """
    Dependency that optionally gets authenticated user from cookie.
    
    Usage:
        @router.get("/public-or-private")
        async def endpoint(user: Optional[AuthenticatedUser] = Depends(get_auth_cookie_optional)):
            if user:
                return {"authenticated": True, "user_id": user.id}
            return {"authenticated": False}
    """
    return get_user_from_cookie(request)


# ═══════════════════════════════════════════════════════════════════════════
# REFRESH TOKEN ENDPOINT HELPER
# ═══════════════════════════════════════════════════════════════════════════

async def handle_token_refresh(
    request: Request,
    response: Response,
    get_user_data: callable,
) -> Dict[str, Any]:
    """
    Handle token refresh flow.
    
    Args:
        request: FastAPI Request
        response: FastAPI Response
        get_user_data: Async callable that takes user_id and returns user data dict
        
    Returns:
        Dict with user data and new tokens set in cookies
    """
    refresh_token = get_refresh_token(request)
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload["sub"]
    
    # Get fresh user data
    user_data = await get_user_data(user_id)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Set new cookies
    set_auth_cookies(
        response=response,
        user_id=user_id,
        email=user_data.get("email", ""),
        tier=user_data.get("tier", "free"),
        addons=user_data.get("addons", []),
    )
    
    return user_data


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'AuthCookieConfig',
    'config',
    'create_access_token',
    'create_refresh_token',
    'decode_token',
    'is_token_expired',
    'set_auth_cookies',
    'clear_auth_cookies',
    'get_access_token',
    'get_refresh_token',
    'get_user_from_cookie',
    'AuthenticatedUser',
    'AuthCookieMiddleware',
    'require_auth_cookie',
    'get_auth_cookie_optional',
    'handle_token_refresh',
]
