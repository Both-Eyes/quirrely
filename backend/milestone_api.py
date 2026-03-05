#!/usr/bin/env python3
"""
QUIRRELY MILESTONE API ENDPOINTS
Extends api_v2.py with milestone tracking and Featured Writer submissions.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from milestone_tracker import (
    MilestoneTracker,
    get_milestone_tracker,
    Tier,
    MilestoneType,
    MILESTONE_META,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/milestones", tags=["milestones"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class MilestoneResponse(BaseModel):
    type: str
    name: str
    description: str
    icon: str
    animation: str
    color: str
    triggered_at: datetime
    keystroke_words: int
    streak_days: Optional[int] = None


class UserMilestonesResponse(BaseModel):
    lifetime_keystroke_words: int
    today_keystroke_words: int
    
    # Achievements
    first_500_achieved: bool
    first_500_achieved_at: Optional[datetime] = None
    
    # Streaks
    streak_500_current: int
    streak_1k_current: int
    streak_1k_longest: int
    
    # Featured
    featured_eligible: bool
    featured_writer: bool
    featured_piece_url: Optional[str] = None
    
    # Badges
    badges: List[Dict[str, Any]]


class FeaturedEligibilityResponse(BaseModel):
    eligible: bool
    reason: Optional[str] = None
    current_streak: Optional[int] = None
    needed: Optional[int] = None
    featured_since: Optional[datetime] = None
    featured_url: Optional[str] = None


class FeaturedSubmissionRequest(BaseModel):
    text: str = Field(..., max_length=5000, description="Submission text (max 500 words)")
    keystroke_verified: bool = Field(..., description="Confirm text was typed, not pasted")
    agreement_original: bool = Field(..., description="Confirm this is original writing")
    agreement_no_compensation: bool = Field(..., description="Agree to feature without compensation")
    agreement_grant_permission: bool = Field(..., description="Grant permission to feature on Quirrely")


class FeaturedSubmissionResponse(BaseModel):
    success: bool
    submission_id: Optional[str] = None
    message: str
    error: Optional[str] = None


class BadgeResponse(BaseModel):
    type: str
    name: str
    icon: str
    count: Optional[int] = None
    earned_at: Optional[datetime] = None
    has_flair: Optional[bool] = None
    url: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_tracker() -> MilestoneTracker:
    return get_milestone_tracker()


def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """Extract user_id from auth header."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    return None


def require_auth(
    authorization: Optional[str] = Header(None),
) -> str:
    """Require authenticated user."""
    user_id = get_current_user(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


def get_user_tier(user_id: str) -> Tier:
    """Get user's tier (placeholder - integrate with feature_gate)."""
    # In production, fetch from feature_gate
    # For now, return PRO for demo
    return Tier.PRO


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/me", response_model=UserMilestonesResponse)
async def get_my_milestones(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Get current user's milestone state and badges."""
    state = tracker.get_user_milestones(user_id)
    badges = tracker.get_user_badges(user_id)
    
    # Get today's total
    from datetime import date
    today_total = tracker._get_daily_keystroke_total(user_id, date.today())
    
    return UserMilestonesResponse(
        lifetime_keystroke_words=state.lifetime_keystroke_words,
        today_keystroke_words=today_total,
        first_500_achieved=state.first_500_achieved,
        first_500_achieved_at=state.first_500_achieved_at,
        streak_500_current=state.streak_500_current,
        streak_1k_current=state.streak_1k_current,
        streak_1k_longest=state.streak_1k_longest,
        featured_eligible=state.featured_eligible,
        featured_writer=state.featured_writer,
        featured_piece_url=state.featured_piece_url,
        badges=badges,
    )


@router.get("/badges", response_model=List[BadgeResponse])
async def get_my_badges(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Get current user's earned badges."""
    badges = tracker.get_user_badges(user_id)
    return [BadgeResponse(**b) for b in badges]


@router.get("/badges/{username}", response_model=List[BadgeResponse])
async def get_user_badges(
    username: str,
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Get badges for a public user profile."""
    # In production, resolve username to user_id
    # For now, treat username as user_id
    badges = tracker.get_user_badges(username)
    return [BadgeResponse(**b) for b in badges]


@router.get("/definitions")
async def get_milestone_definitions():
    """Get all milestone definitions for UI."""
    definitions = []
    for mtype, meta in MILESTONE_META.items():
        definitions.append({
            "type": mtype.value,
            **meta,
        })
    return {"milestones": definitions}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED WRITER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/featured/eligibility", response_model=FeaturedEligibilityResponse)
async def check_featured_eligibility(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Check if user can submit for Featured Writer."""
    tier = get_user_tier(user_id)
    result = tracker.can_submit_featured(user_id, tier)
    return FeaturedEligibilityResponse(**result)


@router.post("/featured/submit", response_model=FeaturedSubmissionResponse)
async def submit_featured_piece(
    request: FeaturedSubmissionRequest,
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Submit a piece for Featured Writer consideration."""
    tier = get_user_tier(user_id)
    
    # Check eligibility
    eligibility = tracker.can_submit_featured(user_id, tier)
    if not eligibility.get("eligible"):
        raise HTTPException(
            status_code=403,
            detail=eligibility.get("reason", "Not eligible for submission")
        )
    
    # Validate agreements
    if not all([
        request.agreement_original,
        request.agreement_no_compensation,
        request.agreement_grant_permission,
    ]):
        raise HTTPException(
            status_code=400,
            detail="All agreement checkboxes must be confirmed"
        )
    
    # Validate word count
    word_count = len(request.text.split())
    if word_count > 500:
        raise HTTPException(
            status_code=400,
            detail=f"Submission must be 500 words or fewer (currently {word_count})"
        )
    
    # Validate keystroke
    if not request.keystroke_verified:
        raise HTTPException(
            status_code=400,
            detail="Submission must be original typed writing"
        )
    
    # Submit
    result = tracker.submit_featured_piece(
        user_id=user_id,
        text=request.text,
        keystroke_verified=request.keystroke_verified,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return FeaturedSubmissionResponse(**result)


@router.get("/featured/submission")
async def get_my_submission(
    user_id: str = Depends(require_auth),
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Get current user's pending submission status."""
    submission = tracker._get_pending_submission(user_id)
    
    if not submission:
        return {"has_submission": False}
    
    return {
        "has_submission": True,
        "submission_id": submission.id,
        "submitted_at": submission.submitted_at,
        "word_count": submission.word_count,
        "status": submission.status.value,
    }


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS (for editorial review)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/submissions")
async def get_pending_submissions(
    # Add admin auth in production
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Get all pending submissions for review (admin only)."""
    data = tracker._read_json(tracker.submissions_file)
    pending = [s for s in data.get("submissions", []) if s["status"] == "pending"]
    return {"submissions": pending, "count": len(pending)}


@router.post("/admin/submissions/{submission_id}/review")
async def review_submission(
    submission_id: str,
    accept: bool,
    notes: Optional[str] = None,
    # Add admin auth in production
    tracker: MilestoneTracker = Depends(get_tracker),
):
    """Review a Featured Writer submission (admin only)."""
    result = tracker.review_submission(
        submission_id=submission_id,
        accept=accept,
        reviewer_notes=notes,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH ANALYZE ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

def process_milestones_after_analysis(
    user_id: str,
    keystroke_words: int,
    tier: Tier,
    is_authenticated: bool,
    save_enabled: bool,
) -> List[Dict[str, Any]]:
    """
    Call this after successful analysis to check for triggered milestones.
    
    Returns list of triggered milestones with full metadata for UI.
    """
    tracker = get_milestone_tracker()
    
    triggered = tracker.record_keystroke_words(
        user_id=user_id,
        word_count=keystroke_words,
        tier=tier,
        is_authenticated=is_authenticated,
        save_enabled=save_enabled,
    )
    
    # Enrich with metadata
    results = []
    for milestone in triggered:
        meta = MILESTONE_META.get(milestone.type, {})
        results.append({
            "type": milestone.type.value,
            "name": meta.get("name", milestone.type.value),
            "description": meta.get("description", ""),
            "icon": meta.get("icon", "🏆"),
            "animation": meta.get("animation", "none"),
            "color": meta.get("color", "#FF6B6B"),
            "triggered_at": milestone.triggered_at.isoformat(),
            "keystroke_words": milestone.keystroke_words,
            "streak_days": milestone.streak_days,
            "unlocks": meta.get("unlocks"),
        })
    
    return results
