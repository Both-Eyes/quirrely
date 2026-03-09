#!/usr/bin/env python3
"""
LNCP FastAPI Dependencies
Version: 1.0.0

Provides reusable FastAPI dependencies for:
- Authentication (get_current_user)
- Feature gating (require_feature_dep)
- Tier checking (require_tier)
- Admin access (require_admin)
- Country enforcement (require_country)

Usage:
    from dependencies import get_current_user, require_feature_dep, require_tier
    
    @router.get("/protected")
    async def protected_endpoint(
        user: User = Depends(get_current_user),
        _: None = Depends(require_feature_dep("analytics")),
    ):
        return {"user_id": user.id}
"""

from __future__ import annotations

import logging
from typing import Optional, List, Callable, Any
from functools import wraps

from fastapi import Depends, HTTPException, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from feature_gate import (
    FeatureGate, 
    Tier, 
    Addon,
    get_feature_gate,
    TIER_LEVELS,
)

# Configure logging
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


# ═══════════════════════════════════════════════════════════════════════════
# USER MODEL (simplified for dependencies)
# ═══════════════════════════════════════════════════════════════════════════

class CurrentUser:
    """Represents the currently authenticated user."""
    
    def __init__(
        self,
        id: str,
        email: str,
        name: str,
        tier: Tier,
        addons: List[str] = None,
        country: str = None,
        is_admin: bool = False,
        is_super_admin: bool = False,
    ):
        self.id = id
        self.email = email
        self.name = name
        self.tier = tier
        self.addons = addons or []
        self.country = country
        self.is_admin = is_admin
        self.is_super_admin = is_super_admin
    
    @property
    def tier_level(self) -> int:
        """Get numeric tier level."""
        return TIER_LEVELS.get(self.tier, 0)
    
    def has_addon(self, addon: str) -> bool:
        """Check if user has an addon."""
        return addon in self.addons
    
    def has_tier(self, required_tiers: List[str]) -> bool:
        """Check if user has one of the required tiers."""
        return self.tier.value in required_tiers
    
    def has_feature(self, feature: str) -> bool:
        """Check if user can access a feature."""
        gate = get_feature_gate()
        result = gate.can_access(feature, self.id)
        return result.allowed


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> CurrentUser:
    """
    Get the current authenticated user.
    
    Supports:
    - Bearer token (production)
    - X-User-ID header (development/testing)
    
    Raises:
        HTTPException 401 if not authenticated
    """
    user_id = None
    
    # Try Bearer token first
    if credentials:
        token = credentials.credentials
        user_id = _validate_token(token)
    
    # Fall back to X-User-ID header (dev only)
    if not user_id and x_user_id:
        # Only allow in development
        import os
        if os.environ.get('ENVIRONMENT', 'development') == 'development':
            user_id = x_user_id
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database/cache
    user = await _get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    
    # Add country from request state (set by CountryGateMiddleware)
    if hasattr(request.state, 'country_code'):
        user.country = request.state.country_code
    
    return user


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
) -> Optional[CurrentUser]:
    """
    Get the current user if authenticated, None otherwise.
    
    Use for endpoints that work with or without authentication.
    """
    try:
        return await get_current_user(request, credentials, x_user_id)
    except HTTPException:
        return None


def _validate_token(token: str) -> Optional[str]:
    """Validate session token against auth_sessions table."""
    try:
        import psycopg2
        conn = psycopg2.connect('postgresql://quirrely:QuirrDB2026xK9m@localhost:5432/quirrely_prod')
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM auth_sessions WHERE access_token = %s LIMIT 1', (token,))
        row = cur.fetchone()
        conn.close()
        return str(row[0]) if row else None
    except Exception as e:
        logger.debug(f"Token validation failed: {e}")
        return None


async def _get_user_by_id(user_id: str) -> Optional[CurrentUser]:
    """Get user from database."""
    try:
        import psycopg2
        conn = psycopg2.connect('postgresql://quirrely:QuirrDB2026xK9m@localhost:5432/quirrely_prod')
        cur = conn.cursor()
        cur.execute('SELECT email, display_name, subscription_tier FROM users WHERE id = %s', (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        email, name, sub_tier = row
        tier_str = sub_tier or 'free'
        valid = [t.value for t in Tier]
        tier = Tier(tier_str) if tier_str in valid else Tier.FREE
        return CurrentUser(id=user_id, email=email, name=name or email, tier=tier, addons=[])
    except Exception as e:
        logger.debug(f"User lookup failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE GATE DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

def require_feature_dep(feature: str):
    """
    Dependency to require a feature.
    
    Usage:
        @router.get("/analytics")
        async def get_analytics(
            user: CurrentUser = Depends(get_current_user),
            _: None = Depends(require_feature_dep("analytics")),
        ):
            ...
    """
    async def check_feature(user: CurrentUser = Depends(get_current_user)) -> None:
        gate = get_feature_gate()
        result = gate.can_access(feature, user.id)
        
        if not result.allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_not_allowed",
                    "feature": feature,
                    "reason": result.reason,
                    "user_tier": user.tier.value,
                    "upgrade_path": _get_upgrade_path(feature),
                }
            )
    
    return check_feature


def _get_upgrade_path(feature: str) -> Optional[str]:
    """Get upgrade path for a feature."""
    # Map features to upgrade suggestions
    upgrade_paths = {
        "save_results": "Start a free trial to save your results",
        "analytics": "Upgrade to Pro to access analytics",
        "voice_profile": "Add Voice + Style to unlock voice analysis",
        "create_paths": "Upgrade to Curator to create reading paths",
        "authority_features": "Reach Authority status to access this feature",
    }
    return upgrade_paths.get(feature)


# ═══════════════════════════════════════════════════════════════════════════
# TIER CHECK DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

def require_tier(allowed_tiers: List[str]):
    """
    Dependency to require specific tiers.
    
    Usage:
        @router.get("/pro-feature")
        async def pro_feature(
            user: CurrentUser = Depends(get_current_user),
            _: None = Depends(require_tier(["pro", "curator", "featured_writer", ...])),
        ):
            ...
    """
    async def check_tier(user: CurrentUser = Depends(get_current_user)) -> None:
        if user.tier.value not in allowed_tiers:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "tier_not_allowed",
                    "user_tier": user.tier.value,
                    "required_tiers": allowed_tiers,
                }
            )
    
    return check_tier


def require_tier_level(min_level: int):
    """
    Dependency to require minimum tier level.
    
    Levels:
        0: free, trial
        1: pro, curator
        2: featured_*
        3: authority_*
    """
    async def check_tier_level(user: CurrentUser = Depends(get_current_user)) -> None:
        if user.tier_level < min_level:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "tier_level_insufficient",
                    "user_tier": user.tier.value,
                    "user_level": user.tier_level,
                    "required_level": min_level,
                }
            )
    
    return check_tier_level


# ═══════════════════════════════════════════════════════════════════════════
# ADDON CHECK DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

def require_addon(addon: str):
    """
    Dependency to require a specific addon.
    
    Usage:
        @router.get("/voice")
        async def voice_feature(
            user: CurrentUser = Depends(get_current_user),
            _: None = Depends(require_addon("voice_style")),
        ):
            ...
    """
    async def check_addon(user: CurrentUser = Depends(get_current_user)) -> None:
        if not user.has_addon(addon):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "addon_not_available",
                    "addon": addon,
                    "message": f"This feature requires the {addon} addon",
                }
            )
    
    return check_addon


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency to require admin access.
    
    Usage:
        @router.get("/admin/users")
        async def list_users(user: CurrentUser = Depends(require_admin)):
            ...
    """
    if not user.is_admin and not user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )
    return user


async def require_super_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    Dependency to require super admin access.
    
    Usage:
        @router.get("/admin/system")
        async def system_config(user: CurrentUser = Depends(require_super_admin)):
            ...
    """
    if not user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Super admin access required",
        )
    return user


# ═══════════════════════════════════════════════════════════════════════════
# COUNTRY CHECK DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════

def require_country(allowed_countries: List[str]):
    """
    Dependency to require user from specific countries.
    
    Note: This is a secondary check. Primary enforcement is via middleware.
    
    Usage:
        @router.get("/ca-only")
        async def canada_only(
            user: CurrentUser = Depends(get_current_user),
            _: None = Depends(require_country(["CA"])),
        ):
            ...
    """
    async def check_country(
        request: Request,
        user: CurrentUser = Depends(get_current_user),
    ) -> None:
        country = getattr(request.state, 'country_code', user.country)
        
        if country and country not in allowed_countries:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "country_not_allowed",
                    "country": country,
                    "allowed_countries": allowed_countries,
                }
            )
    
    return check_country


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'CurrentUser',
    'get_current_user',
    'get_current_user_optional',
    'require_feature_dep',
    'require_tier',
    'require_tier_level',
    'require_addon',
    'require_admin',
    'require_super_admin',
    'require_country',
]
