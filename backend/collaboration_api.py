#!/usr/bin/env python3
"""
QUIRRELY COLLABORATION API
Pro tier collaboration system for shared writing projects.

Features:
- Secure invitation system with expiring tokens
- Word pool management (shared + individual allocations)
- Project categorization and management
- Featured collaboration submissions
- Integration with existing compare feature
- One collaboration per user limit enforcement

Endpoints:
  POST   /api/v2/collaboration/invite     - Send collaboration invitation
  POST   /api/v2/collaboration/accept     - Accept invitation via token
  GET    /api/v2/collaboration/status     - Get user's collaboration status
  POST   /api/v2/collaboration/cancel     - Cancel/leave collaboration
  
  GET    /api/v2/collaboration/words      - Get word allocation status
  POST   /api/v2/collaboration/use-words  - Record word usage
  
  POST   /api/v2/collaboration/featured   - Submit for Featured status
  GET    /api/v2/collaboration/featured   - Get featured collaborations
"""

import asyncio
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, validator
from enum import Enum

from feature_gate import Tier
from conversion_tracker import ConversionTracker

# Use the same auth pattern as api_v2.py
async def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from header.""" 
    return x_user_id

def require_pro_tier():
    """Require Pro tier or higher for collaboration features."""
    def check_tier(user_id: str = Depends(get_user_id)) -> str:
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # TODO: Check user's actual tier from database
        # For now, allow all authenticated users
        return user_id
    return check_tier


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class CollaborationCategory(str, Enum):
    BUSINESS = "business"
    CREATIVE = "creative"
    PERSONAL = "personal"
    ACADEMIC = "academic"
    JOURNALISM = "journalism"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    OTHER = "other"


class CollaborationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class WordUsageType(str, Enum):
    SHARED = "shared"
    SOLO = "solo"


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════

class InviteCollaboratorRequest(BaseModel):
    email: str = Field(..., description="Email of user to invite")
    project_title: str = Field(..., min_length=5, max_length=200)
    project_description: Optional[str] = Field(None, max_length=2000)
    category: CollaborationCategory
    
    @validator('email')
    def validate_email(cls, v):
        # Basic email validation
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Invalid email format')
        return v.lower().strip()


class AcceptInvitationRequest(BaseModel):
    token: str = Field(..., description="Invitation token")


class UseWordsRequest(BaseModel):
    words_used: int = Field(..., ge=1, le=50000)
    usage_type: WordUsageType
    analysis_type: Optional[str] = Field(None, max_length=50)
    analysis_id: Optional[str] = None
    session_id: Optional[str] = None


class SubmitFeaturedRequest(BaseModel):
    submission_title: str = Field(..., min_length=5, max_length=200)
    submission_summary: str = Field(..., min_length=50, max_length=2000)
    submission_tags: Optional[str] = Field(None, max_length=500)
    sample_text: str = Field(..., min_length=100, max_length=5000)
    
    @validator('submission_tags')
    def validate_tags(cls, v):
        if v:
            tags = [tag.strip() for tag in v.split(',')]
            if len(tags) > 10:
                raise ValueError('Maximum 10 tags allowed')
            return ', '.join(tags)
        return v


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class CollaborationInfo(BaseModel):
    id: str
    project_title: str
    category: CollaborationCategory
    status: CollaborationStatus
    partner_name: str
    partner_email: str
    shared_words_available: int
    shared_words_used: int
    solo_words_remaining: int
    period_end: datetime
    started_at: Optional[datetime]


class WordAllocationStatus(BaseModel):
    has_collaboration: bool
    shared_words_available: int = 0
    shared_words_used: int = 0
    shared_words_remaining: int = 0
    solo_words_remaining: int = 0
    period_end: Optional[datetime] = None
    usage_history: List[Dict] = Field(default_factory=list)


class FeaturedCollaboration(BaseModel):
    id: str
    public_title: str
    public_description: str
    category: CollaborationCategory
    collaborator_1: str
    collaborator_2: str
    featured_start_date: str
    views_count: int = 0


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/collaboration", tags=["collaboration"])


# ═══════════════════════════════════════════════════════════════════════════
# COLLABORATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/invite")
async def invite_collaborator(
    request: InviteCollaboratorRequest,
    user_id: str = Depends(require_pro_tier())
):
    """
    Send collaboration invitation to another Pro user.
    
    Requirements:
    - User must be Pro tier
    - User cannot have active collaboration
    - Target user must exist and be Pro tier
    - Target user cannot have active collaboration
    """
    
    # Check if user can start collaboration
    can_collaborate = await check_collaboration_eligibility(user_id)
    if not can_collaborate:
        raise HTTPException(
            status_code=400,
            detail="You already have an active collaboration or are not Pro tier"
        )
    
    # Find target user
    target_user = await find_user_by_email(request.email)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user['id'] == user_id:
        raise HTTPException(status_code=400, detail="Cannot collaborate with yourself")
    
    # Check target user eligibility
    can_target_collaborate = await check_collaboration_eligibility(target_user['id'])
    if not can_target_collaborate:
        raise HTTPException(
            status_code=400,
            detail="Target user already has an active collaboration or is not Pro tier"
        )
    
    # Check invitation limits (prevent spam)
    await check_invitation_limits(user_id)
    
    # Create invitation
    invitation_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    collaboration_id = await create_collaboration_invitation(
        initiator_id=user_id,
        target_email=request.email,
        target_user_id=target_user['id'],
        partnership_name=request.project_title,
        partnership_intention=request.project_description,
        partnership_type=request.category.value,
        invitation_token=invitation_token,
        expires_at=expires_at
    )
    
    # Send invitation email
    await send_invitation_email(
        target_email=request.email,
        target_name=target_user['display_name'],
        initiator_name=await get_user_name(user_id),
        partnership_name=request.project_title,
        partnership_type=request.category.value,
        partnership_intention=request.project_description or "",
        invitation_token=invitation_token
    )
    
    # Update invitation tracking
    await update_invitation_tracking(user_id)
    
    # Track conversion event
    ConversionTracker.track_feature_engagement(
        user_id=user_id,
        feature="collaboration_invite_sent",
        metadata={"category": request.category.value}
    )
    
    return {
        "success": True,
        "collaboration_id": collaboration_id,
        "message": f"Invitation sent to {request.email}",
        "expires_at": expires_at.isoformat()
    }


@router.post("/accept")
async def accept_invitation(
    request: AcceptInvitationRequest,
    user_id: str = Depends(get_user_id)
):
    """Accept collaboration invitation using token."""
    
    # Find invitation
    collaboration = await _find_collaboration_by_token(request.token)
    if not collaboration:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")
    
    # Verify user is the intended recipient
    if collaboration['collaborator_user_id'] != user_id:
        raise HTTPException(status_code=403, detail="This invitation is not for you")
    
    # Check if still eligible
    can_collaborate = await _check_collaboration_eligibility(user_id)
    if not can_collaborate:
        raise HTTPException(
            status_code=400,
            detail="You are not eligible to collaborate"
        )
    
    # Activate collaboration
    await _activate_collaboration(collaboration['id'])
    
    # Initialize word pools (25k each user: 25k shared + 12.5k solo each)
    await _initialize_word_pools(collaboration['id'])
    
    # Track conversion event
    ConversionTracker.track_feature_engagement(
        user_id=user_id,
        feature="collaboration_accepted",
        metadata={"category": collaboration['category']}
    )
    
    return {
        "success": True,
        "collaboration_id": collaboration['id'],
        "message": "Collaboration started successfully"
    }


@router.get("/status")
async def get_collaboration_status(user_id: str = Depends(get_user_id)) -> Optional[CollaborationInfo]:
    """Get user's current collaboration status."""
    
    collaboration = await _get_user_collaboration(user_id)
    if not collaboration:
        return None
    
    # Get partner info
    partner_id = (collaboration['collaborator_user_id'] 
                 if collaboration['initiator_user_id'] == user_id 
                 else collaboration['initiator_user_id'])
    partner = await _get_user_info(partner_id)
    
    # Get user's solo words remaining
    solo_words = (collaboration['collaborator_solo_words_remaining'] 
                 if collaboration['initiator_user_id'] == user_id 
                 else collaboration['initiator_solo_words_remaining'])
    
    return CollaborationInfo(
        id=collaboration['id'],
        project_title=collaboration['project_title'],
        category=collaboration['category'],
        status=collaboration['status'],
        partner_name=partner['display_name'],
        partner_email=partner['email'],
        shared_words_available=collaboration['shared_words_available'],
        shared_words_used=collaboration['shared_words_used'],
        solo_words_remaining=solo_words,
        period_end=collaboration['current_period_end'],
        started_at=collaboration['started_at']
    )


@router.get("/cancel-status")
async def get_cancellation_status(user_id: str = Depends(get_user_id)):
    """Get user's cancellation status and next available date."""
    
    can_cancel = await can_user_cancel_collaboration(user_id)
    next_date = await get_next_cancellation_date(user_id)
    
    return {
        "can_cancel": can_cancel,
        "next_available_date": next_date.isoformat(),
        "message": "Ready to cancel" if can_cancel else f"Next cancellation available on {next_date.strftime('%B %d, %Y')}"
    }


@router.post("/cancel")
async def cancel_collaboration(user_id: str = Depends(get_user_id)):
    """Cancel or leave current collaboration (rate limited: 1 per month)."""
    
    collaboration = await get_user_collaboration(user_id)
    if not collaboration:
        raise HTTPException(status_code=404, detail="No active collaboration found")
    
    try:
        # Cancel collaboration (includes rate limiting check)
        await cancel_collaboration(collaboration['id'], user_id)
        
        # Track conversion event
        ConversionTracker.track_feature_engagement(
            user_id=user_id,
            feature="collaboration_cancelled",
            metadata={"status": collaboration['status']}
        )
        
        return {"success": True, "message": "Collaboration cancelled successfully"}
        
    except ValueError as e:
        # Rate limiting error
        raise HTTPException(
            status_code=429, 
            detail=str(e),
            headers={"Retry-After": "2592000"}  # 30 days in seconds
        )


# ═══════════════════════════════════════════════════════════════════════════
# WORD MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/words")
async def get_word_allocation(user_id: str = Depends(get_user_id)) -> WordAllocationStatus:
    """Get user's word allocation status including collaboration pool."""
    
    collaboration = await _get_user_collaboration(user_id)
    if not collaboration:
        return WordAllocationStatus(has_collaboration=False)
    
    # Get usage history
    usage_history = await _get_word_usage_history(user_id, collaboration['id'])
    
    # Calculate remaining
    shared_remaining = max(0, 
        collaboration['shared_words_available'] - collaboration['shared_words_used']
    )
    
    solo_remaining = (collaboration['collaborator_solo_words_remaining'] 
                     if collaboration['initiator_user_id'] == user_id 
                     else collaboration['initiator_solo_words_remaining'])
    
    return WordAllocationStatus(
        has_collaboration=True,
        shared_words_available=collaboration['shared_words_available'],
        shared_words_used=collaboration['shared_words_used'],
        shared_words_remaining=shared_remaining,
        solo_words_remaining=solo_remaining,
        period_end=collaboration['current_period_end'],
        usage_history=usage_history[-10:]  # Last 10 entries
    )


@router.post("/use-words")
async def use_collaboration_words(
    request: UseWordsRequest,
    user_id: str = Depends(get_user_id)
):
    """
    Record word usage from collaboration pool or solo allocation.
    Called by analysis system when Pro users use words.
    """
    
    collaboration = await _get_user_collaboration(user_id)
    if not collaboration:
        raise HTTPException(status_code=404, detail="No active collaboration found")
    
    # Check allocation availability
    if request.usage_type == WordUsageType.SHARED:
        available = collaboration['shared_words_available'] - collaboration['shared_words_used']
        if request.words_used > available:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient shared words. Available: {available}"
            )
    else:  # SOLO
        solo_remaining = (collaboration['collaborator_solo_words_remaining'] 
                         if collaboration['initiator_user_id'] == user_id 
                         else collaboration['initiator_solo_words_remaining'])
        if request.words_used > solo_remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient solo words. Available: {solo_remaining}"
            )
    
    # Record usage
    await _record_word_usage(
        collaboration_id=collaboration['id'],
        user_id=user_id,
        words_used=request.words_used,
        usage_type=request.usage_type.value,
        analysis_type=request.analysis_type,
        analysis_id=request.analysis_id,
        session_id=request.session_id
    )
    
    # Update allocation
    await _update_word_allocation(collaboration['id'], user_id, request)
    
    return {"success": True, "words_used": request.words_used}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED COLLABORATIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/featured")
async def submit_for_featured(
    request: SubmitFeaturedRequest,
    user_id: str = Depends(get_user_id)
):
    """Submit collaboration for Featured Collaboration consideration."""
    
    collaboration = await _get_user_collaboration(user_id)
    if not collaboration or collaboration['status'] != 'active':
        raise HTTPException(
            status_code=400, 
            detail="Must have active collaboration to submit"
        )
    
    # Check if already submitted
    existing_submission = await _get_featured_submission(collaboration['id'])
    if existing_submission:
        raise HTTPException(
            status_code=400,
            detail="Collaboration already submitted for featured status"
        )
    
    # Create submission
    submission_id = await _create_featured_submission(
        collaboration_id=collaboration['id'],
        submission_title=request.submission_title,
        submission_summary=request.submission_summary,
        submission_tags=request.submission_tags,
        sample_text=request.sample_text,
        word_count=len(request.sample_text.split())
    )
    
    # Track conversion event
    ConversionTracker.track_feature_engagement(
        user_id=user_id,
        feature="featured_collaboration_submitted",
        metadata={"category": collaboration['category']}
    )
    
    return {
        "success": True,
        "submission_id": submission_id,
        "message": "Submitted for featured collaboration review"
    }


@router.get("/featured")
async def get_featured_collaborations(
    limit: int = Query(default=10, le=50)
) -> List[FeaturedCollaboration]:
    """Get list of currently featured collaborations (public endpoint)."""
    
    featured = await _get_featured_collaborations(limit)
    
    return [
        FeaturedCollaboration(
            id=collab['id'],
            public_title=collab['public_title'],
            public_description=collab['public_description'],
            category=collab['category'],
            collaborator_1=collab['collaborator_1'],
            collaborator_2=collab['collaborator_2'],
            featured_start_date=collab['featured_start_date'],
            views_count=collab['views_count']
        )
        for collab in featured
    ]


# Import real database functions
from collaboration_service import (
    check_collaboration_eligibility,
    find_user_by_email,
    check_invitation_limits,
    create_collaboration_invitation,
    send_invitation_email,
    get_user_name,
    update_invitation_tracking,
    find_collaboration_by_token,
    activate_collaboration,
    initialize_word_pools,
    get_user_collaboration,
    get_user_info,
    cancel_collaboration,
    can_user_cancel_collaboration,
    get_next_cancellation_date,
    get_word_usage_history,
    record_word_usage,
    update_word_allocation,
    get_featured_submission,
    create_featured_submission,
    get_featured_collaborations,
)