#!/usr/bin/env python3
"""
QUIRRELY FEATURES API v1.0
Single source of truth for feature flags.

This API exposes the user's available features based on their tier and addons,
eliminating the need for duplicate permission logic in the frontend.

Endpoints:
    GET /api/v2/features          - Get all features for current user
    GET /api/v2/features/{key}    - Check specific feature
    GET /api/v2/features/limits   - Get usage limits
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from feature_gate import (
    FeatureGate,
    Tier,
    Addon,
    FeatureFlag,
    get_feature_gate,
    DEFAULT_FEATURES,
    TIER_LEVELS,
)
from dependencies import get_current_user, CurrentUser

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/features", tags=["features"])


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class FeatureStatus(BaseModel):
    """Status of a single feature."""
    key: str
    name: str
    description: str
    enabled: bool
    reason: str  # 'tier', 'addon', 'both', 'disabled'


class UsageLimits(BaseModel):
    """User's usage limits."""
    daily_analyses: int
    daily_analyses_used: int
    daily_analyses_remaining: int
    resets_at: str


class FeaturesResponse(BaseModel):
    """Complete features response."""
    user_id: str
    user_tier: str
    user_tier_level: int
    user_addons: List[str]
    track: str  # 'writer', 'curator', 'both', 'none'
    
    # Feature access
    features: Dict[str, bool]
    feature_details: List[FeatureStatus]
    
    # Usage limits
    limits: UsageLimits
    
    # Navigation hints
    available_sections: List[str]
    upgrade_suggestions: List[Dict[str, str]]
    
    # Cache control
    cached_at: datetime
    cache_ttl_seconds: int = 300  # 5 minutes


class FeatureCheckResponse(BaseModel):
    """Response for single feature check."""
    feature: str
    enabled: bool
    reason: str
    upgrade_path: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_user_track(tier: str) -> str:
    """Determine user's track based on tier."""
    if tier in ('pro', 'featured_writer', 'authority_writer'):
        return 'writer'
    elif tier in ('curator', 'featured_curator', 'authority_curator'):
        return 'curator'
    elif tier in ('free', 'trial'):
        return 'none'
    else:
        return 'none'


def get_available_sections(tier: str, addons: List[str]) -> List[str]:
    """Get available dashboard sections for user."""
    sections = ['dashboard', 'settings']
    
    # Reader sections (all users)
    sections.extend(['reader/discover', 'reader/bookmarks', 'reader/streak'])
    
    # Writer sections
    if tier in ('pro', 'featured_writer', 'authority_writer'):
        sections.extend(['writer/posts', 'writer/drafts', 'writer/editor', 'writer/analytics'])
    
    # Curator sections
    if tier in ('curator', 'featured_curator', 'authority_curator'):
        sections.extend(['curator/paths', 'curator/followers', 'curator/analytics'])
    
    # Voice profile (addon)
    if 'voice_style' in addons:
        sections.append('dashboard/voice')
    
    # Authority sections
    if tier in ('authority_writer', 'authority_curator'):
        sections.extend(['authority/hub', 'authority/leaderboard', 'authority/impact'])
    
    return sections


def get_upgrade_suggestions(tier: str, addons: List[str]) -> List[Dict[str, str]]:
    """Get relevant upgrade suggestions for user."""
    suggestions = []
    
    if tier == 'free':
        suggestions.append({
            'type': 'trial',
            'title': 'Start Free Trial',
            'description': 'Try all Pro features free for 14 days',
            'cta': 'Start Trial',
        })
    
    if tier in ('free', 'trial'):
        suggestions.append({
            'type': 'pro',
            'title': 'Upgrade to Pro',
            'description': 'Unlimited analyses, save results, full analytics',
            'cta': 'Upgrade Now',
        })
    
    if 'voice_style' not in addons:
        suggestions.append({
            'type': 'addon',
            'title': 'Add Voice + Style',
            'description': 'Deep voice analysis and style insights',
            'cta': 'Add for $4.99/mo',
        })
    
    if tier in ('pro', 'curator') and tier not in ('featured_writer', 'featured_curator'):
        suggestions.append({
            'type': 'featured',
            'title': 'Reach Featured Status',
            'description': 'Get featured and unlock advanced features',
            'cta': 'View Requirements',
        })
    
    return suggestions


def get_feature_reason(flag: FeatureFlag, tier: Tier, addons: List[str]) -> str:
    """Determine why a feature is enabled/disabled."""
    tier_access = getattr(flag, f'tier_{tier.value}', False)
    addon_access = flag.addon_voice_style and 'voice_style' in addons
    
    if flag.tier_or_addon:
        if tier_access and addon_access:
            return 'tier_and_addon'
        elif tier_access:
            return 'tier'
        elif addon_access:
            return 'addon'
        else:
            return 'requires_tier_or_addon'
    else:
        if tier_access and (not flag.addon_voice_style or addon_access):
            return 'tier'
        elif addon_access:
            return 'addon'
        else:
            return 'requires_upgrade'


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("", response_model=FeaturesResponse)
async def get_all_features(
    user: CurrentUser = Depends(get_current_user),
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Get all features available to the current user.
    
    This is the primary endpoint for frontend feature gating.
    Call on login and cache for 5 minutes.
    """
    tier_str = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
    tier = Tier(tier_str) if tier_str in [t.value for t in Tier] else Tier.FREE
    addons = user.addons or []
    
    # Build feature map
    features: Dict[str, bool] = {}
    feature_details: List[FeatureStatus] = []
    
    for flag in DEFAULT_FEATURES:
        if not flag.is_active:
            continue
        
        result = gate.can_access(flag.key, user.id)
        features[flag.key] = result.allowed
        
        feature_details.append(FeatureStatus(
            key=flag.key,
            name=flag.name,
            description=flag.description,
            enabled=result.allowed,
            reason=get_feature_reason(flag, tier, addons),
        ))
    
    # Get usage limits
    limits_data = gate.check_daily_limit(user.id)
    limits = UsageLimits(
        daily_analyses=limits_data['limit'],
        daily_analyses_used=limits_data['used'],
        daily_analyses_remaining=limits_data['remaining'],
        resets_at=limits_data['resets_at'],
    )
    
    return FeaturesResponse(
        user_id=user.id,
        user_tier=tier_str,
        user_tier_level=TIER_LEVELS.get(tier, 0),
        user_addons=addons,
        track=get_user_track(tier_str),
        features=features,
        feature_details=feature_details,
        limits=limits,
        available_sections=get_available_sections(tier_str, addons),
        upgrade_suggestions=get_upgrade_suggestions(tier_str, addons),
        cached_at=datetime.utcnow(),
        cache_ttl_seconds=300,
    )


@router.get("/check/{feature_key}", response_model=FeatureCheckResponse)
async def check_feature(
    feature_key: str,
    user: CurrentUser = Depends(get_current_user),
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Check if user has access to a specific feature.
    
    Use this for real-time checks before performing actions.
    """
    result = gate.can_access(feature_key, user.id)
    
    # Get upgrade path if not allowed
    upgrade_path = None
    if not result.allowed:
        upgrade_paths = {
            'save_results': 'Start a free trial to save your results',
            'analytics': 'Upgrade to Pro to access analytics',
            'voice_profile': 'Add Voice + Style to unlock voice analysis',
            'create_paths': 'Upgrade to Curator to create reading paths',
            'authority_features': 'Reach Authority status for this feature',
        }
        upgrade_path = upgrade_paths.get(feature_key, 'Upgrade your plan')
    
    return FeatureCheckResponse(
        feature=feature_key,
        enabled=result.allowed,
        reason=result.reason,
        upgrade_path=upgrade_path,
    )


@router.get("/limits", response_model=UsageLimits)
async def get_usage_limits(
    user: CurrentUser = Depends(get_current_user),
    gate: FeatureGate = Depends(get_feature_gate),
):
    """
    Get current usage limits for the user.
    
    Returns daily analysis limits and usage.
    """
    limits_data = gate.check_daily_limit(user.id)
    
    return UsageLimits(
        daily_analyses=limits_data['limit'],
        daily_analyses_used=limits_data['used'],
        daily_analyses_remaining=limits_data['remaining'],
        resets_at=limits_data['resets_at'],
    )


@router.get("/sections")
async def get_available_sections_endpoint(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Get available navigation sections for the user.
    
    Use this to build the sidebar navigation.
    """
    tier_str = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
    addons = user.addons or []
    
    return {
        "sections": get_available_sections(tier_str, addons),
        "track": get_user_track(tier_str),
    }


@router.get("/upgrades")
async def get_upgrade_suggestions_endpoint(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Get upgrade suggestions for the user.
    
    Use this to show relevant upgrade CTAs.
    """
    tier_str = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
    addons = user.addons or []
    
    return {
        "suggestions": get_upgrade_suggestions(tier_str, addons),
        "current_tier": tier_str,
        "current_addons": addons,
    }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

def init_features_api(app):
    """Initialize features API routes on FastAPI app."""
    app.include_router(router)
    logger.info("Features API initialized")


if __name__ == "__main__":
    print("Features API module loaded")
    print(f"Total features defined: {len(DEFAULT_FEATURES)}")
