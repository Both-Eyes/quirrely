#!/usr/bin/env python3
"""
QUIRRELY AUTHORITY STATUS WITH META INTEGRATION
Provides authority score and ranking calculated by Meta orchestration system.

This module bridges the frontend authority pages with the Meta health calculator.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Import dependencies
from dependencies import get_current_user, CurrentUser, require_tier

# Configure logging
logger = logging.getLogger(__name__)

# Create router (will be mounted in authority_api.py)
router = APIRouter(tags=["authority-meta"])


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class AuthorityScoreResponse(BaseModel):
    """Authority score response from Meta."""
    score: float
    rank: int
    percentile: float
    level: str
    tier: str
    next_milestone: Optional[Dict[str, Any]] = None
    last_updated: datetime


class AuthorityHealthResponse(BaseModel):
    """Full authority health from Meta."""
    user_id: str
    overall_score: float
    rank: int
    percentile: float
    tier: str
    
    # Component scores
    engagement_score: float
    consistency_score: float
    impact_score: float
    quality_score: float
    
    # Trends
    trend_7d: float  # +/- change over 7 days
    trend_30d: float  # +/- change over 30 days
    
    # Milestones
    milestones_achieved: int
    milestones_total: int
    next_milestone: Optional[Dict[str, Any]] = None
    
    # Meta confidence
    confidence: float  # How confident Meta is in this score
    
    last_calculated: datetime


# ═══════════════════════════════════════════════════════════════════════════
# META INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

class MetaAuthorityBridge:
    """
    Bridge to Meta orchestration system for authority calculations.
    
    Attempts to use real Meta components if available, falls back to
    calculated defaults if not.
    """
    
    def __init__(self):
        self._meta_available = False
        self._health_calculator = None
        self._init_meta()
    
    def _init_meta(self):
        """Initialize Meta components."""
        try:
            from lncp.meta.health_score import get_health_calculator
            self._health_calculator = get_health_calculator()
            self._meta_available = True
            logger.info("Meta health calculator connected")
        except ImportError:
            logger.warning("Meta components not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to init Meta: {e}")
    
    async def get_authority_score(self, user: CurrentUser) -> AuthorityScoreResponse:
        """
        Get authority score for a user.
        
        Uses Meta health calculator if available, otherwise calculates
        based on user tier and activity.
        """
        if self._meta_available and self._health_calculator:
            try:
                health = self._health_calculator.calculate_user_health(user.id)
                
                return AuthorityScoreResponse(
                    score=health.authority_score,
                    rank=health.rank,
                    percentile=health.percentile,
                    level=self._score_to_level(health.authority_score),
                    tier=user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
                    next_milestone=health.next_milestone,
                    last_updated=datetime.utcnow(),
                )
            except Exception as e:
                logger.error(f"Meta calculation failed: {e}")
        
        # Fallback calculation
        return self._calculate_fallback_score(user)
    
    async def get_authority_health(self, user: CurrentUser) -> AuthorityHealthResponse:
        """
        Get full authority health details.
        
        This is the comprehensive view used by the Authority Hub.
        """
        if self._meta_available and self._health_calculator:
            try:
                health = self._health_calculator.calculate_user_health(user.id)
                
                return AuthorityHealthResponse(
                    user_id=user.id,
                    overall_score=health.authority_score,
                    rank=health.rank,
                    percentile=health.percentile,
                    tier=user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
                    engagement_score=health.engagement_score,
                    consistency_score=health.consistency_score,
                    impact_score=health.impact_score,
                    quality_score=health.quality_score,
                    trend_7d=health.trend_7d,
                    trend_30d=health.trend_30d,
                    milestones_achieved=health.milestones_achieved,
                    milestones_total=health.milestones_total,
                    next_milestone=health.next_milestone,
                    confidence=health.confidence,
                    last_calculated=datetime.utcnow(),
                )
            except Exception as e:
                logger.error(f"Meta health calculation failed: {e}")
        
        # Fallback
        return self._calculate_fallback_health(user)
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to level name."""
        if score >= 95:
            return "Legendary"
        elif score >= 85:
            return "Authority"
        elif score >= 70:
            return "Featured"
        elif score >= 50:
            return "Established"
        elif score >= 25:
            return "Rising"
        else:
            return "Newcomer"
    
    def _calculate_fallback_score(self, user: CurrentUser) -> AuthorityScoreResponse:
        """Calculate score without Meta (based on tier)."""
        tier = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
        
        # Base scores by tier
        tier_scores = {
            'free': 10.0,
            'trial': 15.0,
            'pro': 35.0,
            'curator': 35.0,
            'featured_writer': 65.0,
            'featured_curator': 65.0,
            'authority_writer': 90.0,
            'authority_curator': 90.0,
        }
        
        score = tier_scores.get(tier, 10.0)
        
        # Estimate rank based on score
        rank = max(1, int(1000 - (score * 10)))
        percentile = min(99.9, score)
        
        return AuthorityScoreResponse(
            score=score,
            rank=rank,
            percentile=percentile,
            level=self._score_to_level(score),
            tier=tier,
            next_milestone=self._get_next_milestone(tier),
            last_updated=datetime.utcnow(),
        )
    
    def _calculate_fallback_health(self, user: CurrentUser) -> AuthorityHealthResponse:
        """Calculate full health without Meta."""
        score_response = self._calculate_fallback_score(user)
        tier = user.tier.value if hasattr(user.tier, 'value') else str(user.tier)
        
        return AuthorityHealthResponse(
            user_id=user.id,
            overall_score=score_response.score,
            rank=score_response.rank,
            percentile=score_response.percentile,
            tier=tier,
            engagement_score=score_response.score * 0.9,
            consistency_score=score_response.score * 0.85,
            impact_score=score_response.score * 0.8,
            quality_score=score_response.score * 0.95,
            trend_7d=0.0,
            trend_30d=0.0,
            milestones_achieved=self._tier_to_milestones(tier),
            milestones_total=10,
            next_milestone=self._get_next_milestone(tier),
            confidence=0.5,  # Low confidence without Meta
            last_calculated=datetime.utcnow(),
        )
    
    def _tier_to_milestones(self, tier: str) -> int:
        """Estimate milestones achieved based on tier."""
        milestones = {
            'free': 0,
            'trial': 1,
            'pro': 3,
            'curator': 3,
            'featured_writer': 6,
            'featured_curator': 6,
            'authority_writer': 9,
            'authority_curator': 9,
        }
        return milestones.get(tier, 0)
    
    def _get_next_milestone(self, tier: str) -> Optional[Dict[str, Any]]:
        """Get next milestone for tier."""
        next_milestones = {
            'free': {'name': 'Start Trial', 'threshold': 15, 'progress': 10},
            'trial': {'name': 'Upgrade to Pro', 'threshold': 35, 'progress': 15},
            'pro': {'name': 'Reach Featured', 'threshold': 65, 'progress': 35},
            'curator': {'name': 'Reach Featured', 'threshold': 65, 'progress': 35},
            'featured_writer': {'name': 'Reach Authority', 'threshold': 90, 'progress': 65},
            'featured_curator': {'name': 'Reach Authority', 'threshold': 90, 'progress': 65},
            'authority_writer': {'name': 'Legendary Status', 'threshold': 100, 'progress': 90},
            'authority_curator': {'name': 'Legendary Status', 'threshold': 100, 'progress': 90},
        }
        return next_milestones.get(tier)


# Singleton bridge
_bridge: Optional[MetaAuthorityBridge] = None

def get_authority_bridge() -> MetaAuthorityBridge:
    """Get or create authority bridge."""
    global _bridge
    if _bridge is None:
        _bridge = MetaAuthorityBridge()
    return _bridge


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/status", response_model=AuthorityScoreResponse)
async def get_authority_status(
    user: CurrentUser = Depends(get_current_user),
    bridge: MetaAuthorityBridge = Depends(get_authority_bridge),
):
    """
    Get authority score and status.
    
    This endpoint is used by the Authority Hub to display the user's
    current authority score, rank, and next milestone.
    
    The score is calculated by Meta's health calculator if available,
    otherwise a fallback calculation based on tier is used.
    """
    return await bridge.get_authority_score(user)


@router.get("/health", response_model=AuthorityHealthResponse)
async def get_authority_health(
    user: CurrentUser = Depends(get_current_user),
    bridge: MetaAuthorityBridge = Depends(get_authority_bridge),
):
    """
    Get full authority health details.
    
    Returns comprehensive breakdown of authority score components,
    trends, and milestone progress.
    """
    return await bridge.get_authority_health(user)


@router.get("/leaderboard/position")
async def get_leaderboard_position(
    user: CurrentUser = Depends(get_current_user),
    bridge: MetaAuthorityBridge = Depends(get_authority_bridge),
):
    """
    Get user's position on the leaderboard.
    
    Returns rank, percentile, and nearby users.
    """
    score = await bridge.get_authority_score(user)
    
    return {
        "user_id": user.id,
        "rank": score.rank,
        "percentile": score.percentile,
        "score": score.score,
        "level": score.level,
    }


# ═══════════════════════════════════════════════════════════════════════════
# MOUNT ROUTER
# ═══════════════════════════════════════════════════════════════════════════

def mount_authority_meta_router(app):
    """Mount the authority Meta router on a FastAPI app."""
    app.include_router(router, prefix="/api/v2/authority/meta")
    logger.info("Authority Meta router mounted")
