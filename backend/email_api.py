#!/usr/bin/env python3
"""
QUIRRELY EMAIL API v1.0
Email preferences and unsubscribe endpoints.
"""

from datetime import datetime, time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel

from email_config import (
    EmailType,
    EmailCategory,
    EMAIL_CATEGORIES,
    EmailPreferences,
    get_preferences_url,
    get_unsubscribe_url,
)
from email_service import get_email_service, EmailService


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/email", tags=["email"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class EmailPreferencesResponse(BaseModel):
    engagement_enabled: bool
    digest_enabled: bool
    digest_day: int
    preferred_hour: int
    timezone: str


class UpdatePreferencesRequest(BaseModel):
    engagement_enabled: Optional[bool] = None
    digest_enabled: Optional[bool] = None
    digest_day: Optional[int] = None
    preferred_hour: Optional[int] = None
    timezone: Optional[str] = None


class UnsubscribeRequest(BaseModel):
    category: str  # "engagement" | "digest" | "all"


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (Replace with database)
# ═══════════════════════════════════════════════════════════════════════════

_preferences: Dict[str, EmailPreferences] = {}
_unsubscribed: Dict[str, List[str]] = {}  # user_id -> list of categories


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def require_auth(authorization: Optional[str] = Header(None)) -> str:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    raise HTTPException(status_code=401, detail="Authentication required")


def verify_unsubscribe_token(uid: str, cat: str, t: str) -> bool:
    """Verify unsubscribe token."""
    import hashlib
    expected = hashlib.sha256(f"{uid}:{cat}".encode()).hexdigest()[:16]
    return t == expected


# ═══════════════════════════════════════════════════════════════════════════
# PREFERENCES ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/preferences", response_model=EmailPreferencesResponse)
async def get_email_preferences(user_id: str = Depends(require_auth)):
    """Get user's email preferences."""
    prefs = _preferences.get(user_id, EmailPreferences(user_id=user_id))
    
    return EmailPreferencesResponse(
        engagement_enabled=prefs.engagement_enabled,
        digest_enabled=prefs.digest_enabled,
        digest_day=prefs.digest_day,
        preferred_hour=prefs.preferred_time.hour,
        timezone=prefs.timezone,
    )


@router.patch("/preferences")
async def update_email_preferences(
    request: UpdatePreferencesRequest,
    user_id: str = Depends(require_auth),
):
    """Update user's email preferences."""
    prefs = _preferences.get(user_id, EmailPreferences(user_id=user_id))
    
    if request.engagement_enabled is not None:
        prefs.engagement_enabled = request.engagement_enabled
    
    if request.digest_enabled is not None:
        prefs.digest_enabled = request.digest_enabled
    
    if request.digest_day is not None:
        if 0 <= request.digest_day <= 6:
            prefs.digest_day = request.digest_day
    
    if request.preferred_hour is not None:
        if 0 <= request.preferred_hour <= 23:
            prefs.preferred_time = time(request.preferred_hour, 0)
    
    if request.timezone is not None:
        prefs.timezone = request.timezone
    
    _preferences[user_id] = prefs
    
    return {"success": True, "message": "Preferences updated"}


# ═══════════════════════════════════════════════════════════════════════════
# UNSUBSCRIBE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/unsubscribe")
async def unsubscribe_one_click(
    uid: str = Query(...),
    cat: str = Query(...),
    t: str = Query(...),
):
    """One-click unsubscribe (from email link)."""
    if not verify_unsubscribe_token(uid, cat, t):
        raise HTTPException(status_code=400, detail="Invalid unsubscribe link")
    
    prefs = _preferences.get(uid, EmailPreferences(user_id=uid))
    
    if cat == "engagement":
        prefs.engagement_enabled = False
    elif cat == "digest":
        prefs.digest_enabled = False
    elif cat == "all":
        prefs.engagement_enabled = False
        prefs.digest_enabled = False
    
    _preferences[uid] = prefs
    
    # Return simple HTML confirmation
    return {
        "success": True,
        "message": f"You've been unsubscribed from {cat} emails.",
        "preferences_url": get_preferences_url(uid),
    }


@router.post("/unsubscribe")
async def unsubscribe(
    request: UnsubscribeRequest,
    user_id: str = Depends(require_auth),
):
    """Unsubscribe from email category (authenticated)."""
    prefs = _preferences.get(user_id, EmailPreferences(user_id=user_id))
    
    if request.category == "engagement":
        prefs.engagement_enabled = False
    elif request.category == "digest":
        prefs.digest_enabled = False
    elif request.category == "all":
        prefs.engagement_enabled = False
        prefs.digest_enabled = False
    else:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    _preferences[user_id] = prefs
    
    return {"success": True, "message": f"Unsubscribed from {request.category} emails"}


@router.post("/resubscribe")
async def resubscribe(
    category: str,
    user_id: str = Depends(require_auth),
):
    """Resubscribe to email category."""
    prefs = _preferences.get(user_id, EmailPreferences(user_id=user_id))
    
    if category == "engagement":
        prefs.engagement_enabled = True
    elif category == "digest":
        prefs.digest_enabled = True
    elif category == "all":
        prefs.engagement_enabled = True
        prefs.digest_enabled = True
    else:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    _preferences[user_id] = prefs
    
    return {"success": True, "message": f"Resubscribed to {category} emails"}


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL HISTORY (for user to see what was sent)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/history")
async def get_email_history(
    user_id: str = Depends(require_auth),
    limit: int = 20,
):
    """Get user's email history."""
    # Would fetch from database
    return {
        "emails": [],
        "total": 0,
    }


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN/TESTING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/send-test")
async def send_test_email(
    email_type: str,
    to_email: str,
    user_id: str = Depends(require_auth),
    service: EmailService = Depends(get_email_service),
):
    """Send a test email (for development)."""
    try:
        email_type_enum = EmailType(email_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid email type: {email_type}")
    
    result = await service.send(
        email_type=email_type_enum,
        to_email=to_email,
        user_id=user_id,
        data={
            "streak_days": 7,
            "milestone_name": "7-Day Streak",
            "milestone_icon": "🔥",
            "tier_name": "PRO",
            "featured_type": "Writer",
            "verify_url": "https://quirrely.com/verify/test",
            "magic_url": "https://quirrely.com/auth/test",
            "reset_url": "https://quirrely.com/reset/test",
            "update_url": "https://quirrely.com/billing",
        },
    )
    
    return result
