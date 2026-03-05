#!/usr/bin/env python3
"""
QUIRRELY CURATOR API ENDPOINTS
Curator tier management, milestone tracking, and Featured Curator submissions.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from curator_tracker import (
    CuratorMilestoneTracker,
    get_curator_tracker,
    CURATOR_TARGETS,
    MILESTONE_META,
    CuratorMilestoneType,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/curator", tags=["curator"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class MilestoneProgress(BaseModel):
    current: int
    target: int
    complete: bool
    icon: str
    explored: Optional[List[str]] = None


class ProgressResponse(BaseModel):
    window_active: bool
    days_remaining: int
    window_expired: bool
    milestones: Dict[str, MilestoneProgress]
    completed_count: int
    total_count: int
    percent_complete: int
    featured_eligible: bool
    featured_curator: bool


class NextActionResponse(BaseModel):
    action: str
    message: str
    cta: str
    profile_type: Optional[str] = None


class PathSubmissionRequest(BaseModel):
    title: str = Field(..., max_length=100, description="Path title")
    intro: str = Field(..., description="100-word intro")
    post_ids: List[str] = Field(..., min_items=4, max_items=6, description="4-6 profile IDs")
    agreement_original: bool = Field(..., description="Confirm original curation")
    agreement_permission: bool = Field(..., description="Grant permission to feature")
    agreement_read_all: bool = Field(..., description="Confirm read all posts")


class PathSubmissionResponse(BaseModel):
    success: bool
    path_id: Optional[str] = None
    message: str
    error: Optional[str] = None


class FeaturedPathResponse(BaseModel):
    id: str
    user_id: str
    title: str
    intro: str
    post_ids: List[str]
    published_url: Optional[str]
    published_at: Optional[str]


class TriggeredMilestone(BaseModel):
    type: str
    name: str
    icon: str
    message: str


class RecordEventResponse(BaseModel):
    recorded: bool
    triggered: List[TriggeredMilestone]
    progress: ProgressResponse
    reason: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_tracker() -> CuratorMilestoneTracker:
    return get_curator_tracker()


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


def require_curator(
    authorization: Optional[str] = Header(None),
) -> str:
    """Require Curator tier."""
    user_id = require_auth(authorization)
    # In production, check tier from database
    # For now, assume authenticated = curator for demo
    return user_id


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS: Progress
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/start-window")
async def start_curator_window(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Start or restart the 30-day Featured Curator window."""
    state = tracker.start_window(user_id)
    progress = tracker.get_progress(user_id)
    
    return {
        "success": True,
        "window_start": state.window_start.isoformat(),
        "window_end": state.window_end.isoformat(),
        "days_remaining": progress["days_remaining"],
        "message": "Your 30-day window has started. Complete all milestones to unlock Featured Curator.",
    }


@router.get("/progress", response_model=ProgressResponse)
async def get_curator_progress(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get current progress toward Featured Curator."""
    progress = tracker.get_progress(user_id)
    return ProgressResponse(**progress)


@router.get("/next-action", response_model=NextActionResponse)
async def get_next_action(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get recommended next action."""
    action = tracker.get_next_action(user_id)
    return NextActionResponse(**action)


@router.get("/targets")
async def get_milestone_targets():
    """Get milestone target values."""
    return {
        "targets": CURATOR_TARGETS,
        "milestones": {
            mtype.value: {
                "name": meta["name"],
                "target": meta["target"],
                "description": meta["description"],
                "icon": meta["icon"],
            }
            for mtype, meta in MILESTONE_META.items()
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS: Recording Events
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/record/read", response_model=RecordEventResponse)
async def record_post_read(
    profile_id: str,
    is_deep_read: bool = False,
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Record a post read event."""
    result = tracker.record_post_read(
        user_id=user_id,
        profile_id=profile_id,
        is_deep_read=is_deep_read,
    )
    
    # Enrich triggered milestones
    triggered = []
    for mtype_value in result.get("triggered", []):
        mtype = CuratorMilestoneType(mtype_value)
        meta = MILESTONE_META.get(mtype, {})
        triggered.append(TriggeredMilestone(
            type=mtype_value,
            name=meta.get("name", mtype_value),
            icon=meta.get("icon", "🏆"),
            message=meta.get("complete_message", "Milestone complete!"),
        ))
    
    return RecordEventResponse(
        recorded=result["recorded"],
        triggered=triggered,
        progress=ProgressResponse(**result.get("progress", {})),
        reason=result.get("reason"),
    )


@router.post("/record/bookmark", response_model=RecordEventResponse)
async def record_bookmark(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Record a bookmark event."""
    result = tracker.record_bookmark(user_id)
    
    triggered = []
    for mtype_value in result.get("triggered", []):
        mtype = CuratorMilestoneType(mtype_value)
        meta = MILESTONE_META.get(mtype, {})
        triggered.append(TriggeredMilestone(
            type=mtype_value,
            name=meta.get("name", mtype_value),
            icon=meta.get("icon", "🏆"),
            message=meta.get("complete_message", "Milestone complete!"),
        ))
    
    return RecordEventResponse(
        recorded=result["recorded"],
        triggered=triggered,
        progress=ProgressResponse(**result.get("progress", {})),
        reason=result.get("reason"),
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS: Featured Path Submission
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/featured/eligibility")
async def check_featured_eligibility(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Check if user can submit for Featured Curator."""
    return tracker.can_submit_path(user_id)


@router.post("/featured/submit", response_model=PathSubmissionResponse)
async def submit_featured_path(
    request: PathSubmissionRequest,
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Submit a curated reading path for Featured Curator consideration."""
    # Check eligibility
    eligibility = tracker.can_submit_path(user_id)
    if not eligibility.get("can_submit"):
        raise HTTPException(
            status_code=403,
            detail=eligibility.get("reason", "Not eligible for submission")
        )
    
    # Validate agreements
    if not all([
        request.agreement_original,
        request.agreement_permission,
        request.agreement_read_all,
    ]):
        raise HTTPException(
            status_code=400,
            detail="All agreement checkboxes must be confirmed"
        )
    
    # Validate word count
    word_count = len(request.intro.split())
    if word_count > 100:
        raise HTTPException(
            status_code=400,
            detail=f"Intro must be 100 words or fewer (currently {word_count})"
        )
    
    # Submit
    result = tracker.submit_path(
        user_id=user_id,
        title=request.title,
        intro=request.intro,
        post_ids=request.post_ids,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return PathSubmissionResponse(**result)


@router.get("/featured/my-path")
async def get_my_path(
    user_id: str = Depends(require_curator),
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get current user's published path."""
    path = tracker.get_path_by_user(user_id)
    
    if not path:
        return {"has_path": False}
    
    return {
        "has_path": True,
        "path": FeaturedPathResponse(**path),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS: Featured Paths (Public)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/featured/paths", response_model=List[FeaturedPathResponse])
async def get_featured_paths(
    limit: int = 10,
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get all published featured paths."""
    paths = tracker.get_featured_paths(limit)
    return [FeaturedPathResponse(**p) for p in paths]


@router.get("/featured/paths/{user_id}")
async def get_path_by_user(
    user_id: str,
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get a specific user's featured path."""
    path = tracker.get_path_by_user(user_id)
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    
    return FeaturedPathResponse(**path)


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS: Admin
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/pending-paths")
async def get_pending_paths(
    # Add admin auth in production
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Get all pending path submissions (admin only)."""
    data = tracker._read_json(tracker.paths_file)
    pending = [p for p in data.get("paths", []) if p["status"] == "pending"]
    return {"paths": pending, "count": len(pending)}


@router.post("/admin/paths/{path_id}/review")
async def review_path(
    path_id: str,
    accept: bool,
    notes: Optional[str] = None,
    # Add admin auth in production
    tracker: CuratorMilestoneTracker = Depends(get_tracker),
):
    """Review a path submission (admin only)."""
    result = tracker.review_path(
        path_id=path_id,
        accept=accept,
        reviewer_notes=notes,
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def process_curator_read_event(
    user_id: str,
    profile_id: str,
    scroll_depth: int,
    time_on_page: int,
) -> Dict[str, Any]:
    """
    Call this when a Curator reads a post.
    
    Used by reader_api.py to integrate with curator tracking.
    """
    tracker = get_curator_tracker()
    
    # Determine if deep read (>80% scroll + >2min)
    is_deep_read = scroll_depth >= 80 and time_on_page >= 120
    
    return tracker.record_post_read(
        user_id=user_id,
        profile_id=profile_id,
        is_deep_read=is_deep_read,
    )


def process_curator_bookmark_event(user_id: str) -> Dict[str, Any]:
    """
    Call this when a Curator bookmarks a post.
    
    Used by reader_api.py to integrate with curator tracking.
    """
    tracker = get_curator_tracker()
    return tracker.record_bookmark(user_id)
