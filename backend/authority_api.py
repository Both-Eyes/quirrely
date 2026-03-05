#!/usr/bin/env python3
"""
QUIRRELY AUTHORITY API ENDPOINTS
Authority Writer and Authority Curator status management.

Authority = sustained excellence over time:
- Authority Writer: 3 featured pieces, 50K words, 2x 30-day streaks, 90 days as Featured
- Authority Curator: 3 featured paths, 50 path follows, 100 deep reads, 90 days as Featured
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from milestone_tracker import (
    MilestoneTracker,
    get_milestone_tracker,
    AUTHORITY_WRITER_REQUIREMENTS,
)
from curator_tracker import (
    CuratorMilestoneTracker,
    get_curator_tracker,
    AUTHORITY_CURATOR_REQUIREMENTS,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/authority", tags=["authority"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class ProgressItem(BaseModel):
    current: int
    target: int
    complete: bool
    icon: Optional[str] = None


class AuthorityProgressResponse(BaseModel):
    is_featured: bool
    is_authority: bool
    authority_eligible: bool
    progress: Dict[str, ProgressItem]
    percent_complete: int
    next_milestone: Optional[str] = None


class AuthorityStatusResponse(BaseModel):
    active: bool
    since: Optional[datetime] = None
    reason: Optional[str] = None
    days_inactive: Optional[int] = None
    can_reactivate: Optional[bool] = None


class VoiceAndTasteResponse(BaseModel):
    has_both_featured: bool
    has_voice_and_taste: bool
    has_authority_voice_and_taste: bool
    writer_status: Dict[str, Any]
    curator_status: Dict[str, Any]
    badge: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_writer_tracker() -> MilestoneTracker:
    return get_milestone_tracker()


def get_curator_tracker_dep() -> CuratorMilestoneTracker:
    return get_curator_tracker()


def require_auth(authorization: Optional[str] = Header(None)) -> str:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    raise HTTPException(status_code=401, detail="Authentication required")


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY WRITER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/writer/requirements")
async def get_writer_requirements():
    """Get Authority Writer requirements."""
    return {
        "requirements": AUTHORITY_WRITER_REQUIREMENTS,
        "description": {
            "featured_pieces": "Featured pieces accepted",
            "lifetime_words": "Lifetime keystroke words written",
            "streak_30_count": "30-day 1K streaks completed",
            "days_as_featured": "Days since becoming Featured Writer",
        },
    }


@router.get("/writer/progress", response_model=AuthorityProgressResponse)
async def get_writer_authority_progress(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_writer_tracker),
):
    """Get progress toward Authority Writer status."""
    progress = tracker.get_authority_progress(user_id)
    
    # Find next milestone
    next_milestone = None
    for name, data in progress.get("progress", {}).items():
        if not data.get("complete"):
            next_milestone = name
            break
    
    return AuthorityProgressResponse(
        is_featured=progress["is_featured_writer"],
        is_authority=progress["is_authority_writer"],
        authority_eligible=progress["authority_eligible"],
        progress={k: ProgressItem(**v) for k, v in progress.get("progress", {}).items()},
        percent_complete=progress["percent_complete"],
        next_milestone=next_milestone,
    )


@router.get("/writer/status", response_model=AuthorityStatusResponse)
async def get_writer_authority_status(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_writer_tracker),
):
    """Check if Authority Writer status is active."""
    status = tracker.check_authority_active(user_id)
    return AuthorityStatusResponse(**status)


@router.post("/writer/claim")
async def claim_authority_writer(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_writer_tracker),
):
    """Claim Authority Writer status (if eligible)."""
    result = tracker.grant_authority_writer(user_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason"))
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY CURATOR ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/curator/requirements")
async def get_curator_requirements():
    """Get Authority Curator requirements."""
    return {
        "requirements": AUTHORITY_CURATOR_REQUIREMENTS,
        "description": {
            "featured_paths": "Featured paths accepted",
            "total_path_follows": "Total times others followed your paths",
            "lifetime_deep_reads": "Lifetime deep reads (>80% scroll + >2min)",
            "days_as_featured": "Days since becoming Featured Curator",
        },
    }


@router.get("/curator/progress", response_model=AuthorityProgressResponse)
async def get_curator_authority_progress(
    user_id: str = Depends(require_auth),
    tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Get progress toward Authority Curator status."""
    progress = tracker.get_authority_curator_progress(user_id)
    
    # Find next milestone
    next_milestone = None
    for name, data in progress.get("progress", {}).items():
        if not data.get("complete"):
            next_milestone = name
            break
    
    return AuthorityProgressResponse(
        is_featured=progress["is_featured_curator"],
        is_authority=progress["is_authority_curator"],
        authority_eligible=progress["authority_eligible"],
        progress={k: ProgressItem(**v) for k, v in progress.get("progress", {}).items()},
        percent_complete=progress["percent_complete"],
        next_milestone=next_milestone,
    )


@router.get("/curator/status", response_model=AuthorityStatusResponse)
async def get_curator_authority_status(
    user_id: str = Depends(require_auth),
    tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Check if Authority Curator status is active."""
    status = tracker.check_authority_curator_active(user_id)
    return AuthorityStatusResponse(**status)


@router.post("/curator/claim")
async def claim_authority_curator(
    user_id: str = Depends(require_auth),
    tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Claim Authority Curator status (if eligible)."""
    result = tracker.grant_authority_curator(user_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("reason"))
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# VOICE & TASTE COMBINED STATUS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/voice-and-taste", response_model=VoiceAndTasteResponse)
async def get_voice_and_taste_status(
    user_id: str = Depends(require_auth),
    writer_tracker: MilestoneTracker = Depends(get_writer_tracker),
    curator_tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Get combined Voice & Taste status (both Writer and Curator achievements)."""
    writer_state = writer_tracker.get_user_milestones(user_id)
    curator_state = curator_tracker.get_state(user_id)
    
    # Check for various combined statuses
    has_both_featured = writer_state.featured_writer and curator_state.featured_curator
    has_both_authority = writer_state.authority_writer and curator_state.authority_curator
    
    # Determine badge
    badge = None
    if has_both_authority:
        badge = "💎 Authority Voice & Taste"
    elif has_both_featured:
        badge = "🏆 Voice & Taste"
    
    return VoiceAndTasteResponse(
        has_both_featured=has_both_featured,
        has_voice_and_taste=has_both_featured,
        has_authority_voice_and_taste=has_both_authority,
        writer_status={
            "featured": writer_state.featured_writer,
            "featured_since": writer_state.featured_writer_since,
            "authority": writer_state.authority_writer,
            "authority_since": writer_state.authority_writer_since,
            "pieces_count": writer_state.featured_pieces_count,
            "lifetime_words": writer_state.lifetime_keystroke_words,
        },
        curator_status={
            "featured": curator_state.featured_curator,
            "featured_since": curator_state.featured_curator_since,
            "authority": curator_state.authority_curator,
            "authority_since": curator_state.authority_curator_since,
            "paths_count": curator_state.featured_paths_count,
            "total_follows": curator_state.total_path_follows,
        },
        badge=badge,
    )


# ═══════════════════════════════════════════════════════════════════════════
# COMBINED BADGES
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/badges")
async def get_all_authority_badges(
    user_id: str = Depends(require_auth),
    writer_tracker: MilestoneTracker = Depends(get_writer_tracker),
    curator_tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Get all Authority-related badges for a user."""
    writer_badges = writer_tracker.get_user_badges(user_id)
    curator_badges = curator_tracker.get_curator_badges(user_id)
    
    # Check for combined badge
    writer_state = writer_tracker.get_user_milestones(user_id)
    curator_state = curator_tracker.get_state(user_id)
    
    combined_badges = []
    
    if writer_state.authority_writer and curator_state.authority_curator:
        combined_badges.append({
            "type": "authority_voice_and_taste",
            "name": "Authority Voice & Taste",
            "icon": "💎",
            "tier": "ultimate",
            "description": "Authority in both writing and curation",
        })
    elif writer_state.featured_writer and curator_state.featured_curator:
        combined_badges.append({
            "type": "voice_and_taste",
            "name": "Voice & Taste",
            "icon": "🏆",
            "tier": "combined",
            "description": "Featured as both Writer and Curator",
        })
    
    return {
        "writer_badges": writer_badges,
        "curator_badges": curator_badges,
        "combined_badges": combined_badges,
        "total_badges": len(writer_badges) + len(curator_badges) + len(combined_badges),
    }


# ═══════════════════════════════════════════════════════════════════════════
# LEADERBOARDS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/leaderboard/writers")
async def get_authority_writers_leaderboard(
    limit: int = 10,
    writer_tracker: MilestoneTracker = Depends(get_writer_tracker),
):
    """Get top Authority Writers."""
    # In production, query database
    # For now, return placeholder
    return {
        "leaderboard": [],
        "total_authority_writers": 0,
        "message": "Authority Writer leaderboard coming soon",
    }


@router.get("/leaderboard/curators")
async def get_authority_curators_leaderboard(
    limit: int = 10,
    curator_tracker: CuratorMilestoneTracker = Depends(get_curator_tracker_dep),
):
    """Get top Authority Curators."""
    return {
        "leaderboard": [],
        "total_authority_curators": 0,
        "message": "Authority Curator leaderboard coming soon",
    }
