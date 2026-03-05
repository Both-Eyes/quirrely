#!/usr/bin/env python3
"""
QUIRRELY DASHBOARD API v1.0
Dashboard data aggregation and settings management.
"""

import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from dashboard_config import (
    DashboardSection,
    SettingsCategory,
    SETTINGS_CONFIG,
    EXPORT_CONFIG,
    get_sections_for_user,
    get_empty_state,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/dashboard", tags=["dashboard"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class TodayProgressResponse(BaseModel):
    words_today: int
    goal: int
    percent: int
    streak_days: int
    streak_active: bool
    words_until_goal: int


class VoiceSnapshotResponse(BaseModel):
    profile_type: Optional[str]
    stance: Optional[str]
    top_traits: List[Dict[str, Any]]
    last_updated: Optional[datetime]


class MilestoneProgressResponse(BaseModel):
    current_milestone: Optional[str]
    next_milestone: Optional[str]
    progress_percent: int
    milestones_achieved: List[str]


class RecentAnalysisResponse(BaseModel):
    id: str
    preview: str
    word_count: int
    profile_type: str
    analyzed_at: datetime


class ReadingActivityResponse(BaseModel):
    posts_this_week: int
    deep_reads_this_week: int
    streak_days: int
    profile_types_explored: List[str]


class DashboardResponse(BaseModel):
    user_tier: str
    user_addons: List[str] = []
    tier_level: int = 0
    track: str = "none"  # "writer", "curator", or "none"
    has_voice_style: bool = False
    has_writer_features: bool
    has_reader_features: bool
    writer_data: Optional[Dict[str, Any]]
    reader_data: Optional[Dict[str, Any]]


class SettingsResponse(BaseModel):
    categories: Dict[str, List[Dict[str, Any]]]
    current_values: Dict[str, Any]


class UpdateSettingRequest(BaseModel):
    setting_id: str
    value: Any


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (Replace with database)
# ═══════════════════════════════════════════════════════════════════════════

_user_settings: Dict[str, Dict[str, Any]] = {}
_user_data: Dict[str, Dict[str, Any]] = {}


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def require_auth(authorization: Optional[str] = Header(None)) -> str:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    raise HTTPException(status_code=401, detail="Authentication required")


def get_user_tier(user_id: str) -> str:
    """Get user's current tier."""
    # Would query subscriptions table via: SELECT get_user_tier(user_id)
    return _user_data.get(user_id, {}).get("tier", "free")


def get_user_addons(user_id: str) -> List[str]:
    """Get user's active addons."""
    # Would query user_addons table via: SELECT get_user_addons(user_id)
    return _user_data.get(user_id, {}).get("addons", [])


def get_user_features(user_id: str) -> List[str]:
    """Get user's enabled features."""
    # Would query milestones and featured status
    return _user_data.get(user_id, {}).get("features", [])


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

# Tier levels and track mapping
TIER_LEVELS = {
    "free": 0, "trial": 0,
    "pro": 1, "curator": 1,
    "featured_writer": 2, "featured_curator": 2,
    "authority_writer": 3, "authority_curator": 3,
}

WRITER_TIERS = {"free", "trial", "pro", "featured_writer", "authority_writer", "bundle"}
CURATOR_TIERS = {"curator", "featured_curator", "authority_curator", "bundle"}


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(user_id: str = Depends(require_auth)):
    """Get complete dashboard data."""
    tier = get_user_tier(user_id)
    addons = get_user_addons(user_id)
    features = get_user_features(user_id)
    
    # Calculate tier level and track
    tier_level = TIER_LEVELS.get(tier, 0)
    if tier in {"pro", "featured_writer", "authority_writer"}:
        track = "writer"
    elif tier in {"curator", "featured_curator", "authority_curator"}:
        track = "curator"
    else:
        track = "none"
    
    has_voice_style = "voice_style" in addons
    
    # Determine feature access
    # Writers get writer features, curators get reader features
    # voice_style addon grants cross-track access
    has_writer = tier in WRITER_TIERS or has_voice_style
    has_reader = tier in CURATOR_TIERS or has_voice_style
    
    writer_data = None
    reader_data = None
    
    if has_writer:
        writer_data = await _get_writer_dashboard(user_id, tier, features)
    
    if has_reader:
        reader_data = await _get_reader_dashboard(user_id, tier, features)
    
    return DashboardResponse(
        user_tier=tier,
        user_addons=addons,
        tier_level=tier_level,
        track=track,
        has_voice_style=has_voice_style,
        has_writer_features=has_writer,
        has_reader_features=has_reader,
        writer_data=writer_data,
        reader_data=reader_data,
    )


async def _get_writer_dashboard(user_id: str, tier: str, features: List[str]) -> Dict[str, Any]:
    """Aggregate writer dashboard data."""
    return {
        "today_progress": await get_today_progress(user_id),
        "voice_snapshot": await get_voice_snapshot(user_id),
        "milestones": await get_milestone_progress(user_id),
        "recent_analyses": await get_recent_analyses(user_id),
        "featured_status": await get_featured_status(user_id) if tier in ["pro", "trial", "bundle"] else None,
        "authority_progress": await get_authority_progress(user_id) if "featured_writer" in features else None,
    }


async def _get_reader_dashboard(user_id: str, tier: str, features: List[str]) -> Dict[str, Any]:
    """Aggregate reader dashboard data."""
    return {
        "reading_activity": await get_reading_activity(user_id),
        "reading_taste": await get_reading_taste(user_id),
        "bookmarks": await get_bookmarks_summary(user_id),
        "curator_progress": await get_curator_progress(user_id) if tier in ["curator", "bundle"] else None,
        "featured_paths": await get_featured_paths(user_id) if "featured_curator" in features else None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# WRITER SECTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/writer/today")
async def get_today_progress(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get today's writing progress."""
    # Would query daily_keystroke_totals
    data = _user_data.get(user_id, {})
    words_today = data.get("words_today", 0)
    goal = 1000 if data.get("tier") in ["pro", "trial", "bundle"] else 500
    streak = data.get("streak_days", 0)
    
    return {
        "words_today": words_today,
        "goal": goal,
        "percent": min(100, int((words_today / goal) * 100)) if goal > 0 else 0,
        "streak_days": streak,
        "streak_active": words_today >= goal,
        "words_until_goal": max(0, goal - words_today),
        "empty_state": get_empty_state(DashboardSection.TODAY_PROGRESS) if words_today == 0 else None,
    }


@router.get("/writer/voice")
async def get_voice_snapshot(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get voice profile snapshot."""
    # Would query user's latest profile
    data = _user_data.get(user_id, {})
    profile = data.get("voice_profile")
    
    if not profile:
        return {
            "has_profile": False,
            "empty_state": get_empty_state(DashboardSection.VOICE_SNAPSHOT),
        }
    
    return {
        "has_profile": True,
        "profile_type": profile.get("type"),
        "stance": profile.get("stance"),
        "top_traits": profile.get("top_traits", [])[:3],
        "last_updated": profile.get("updated_at"),
    }


@router.get("/writer/milestones")
async def get_milestone_progress(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get milestone progress."""
    # Would query user_milestones
    data = _user_data.get(user_id, {})
    milestones = data.get("milestones", {})
    
    achieved = []
    if milestones.get("first_500"):
        achieved.append("first_500")
    if milestones.get("streak_3_day"):
        achieved.append("streak_3_day")
    if milestones.get("daily_1k"):
        achieved.append("daily_1k")
    
    # Determine next milestone
    next_milestone = None
    progress = 0
    
    if not milestones.get("first_500"):
        next_milestone = "first_500"
        lifetime = data.get("lifetime_words", 0)
        progress = min(100, int((lifetime / 500) * 100))
    elif not milestones.get("streak_3_day"):
        next_milestone = "streak_3_day"
        current_streak = data.get("streak_days", 0)
        progress = min(100, int((current_streak / 3) * 100))
    
    return {
        "achieved": achieved,
        "next_milestone": next_milestone,
        "progress_percent": progress,
        "empty_state": get_empty_state(DashboardSection.MILESTONES) if not achieved else None,
    }


@router.get("/writer/recent")
async def get_recent_analyses(
    user_id: str = Depends(require_auth),
    limit: int = 5,
) -> Dict[str, Any]:
    """Get recent analyses."""
    # Would query analyses table
    data = _user_data.get(user_id, {})
    analyses = data.get("analyses", [])[:limit]
    
    if not analyses:
        return {
            "analyses": [],
            "empty_state": get_empty_state(DashboardSection.RECENT_ANALYSES),
        }
    
    return {
        "analyses": analyses,
        "total_count": len(data.get("analyses", [])),
    }


@router.get("/writer/featured")
async def get_featured_status(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get Featured Writer status."""
    # Would query featured_submissions and user_milestones
    data = _user_data.get(user_id, {})
    
    is_featured = data.get("featured_writer", False)
    is_eligible = data.get("featured_eligible", False)
    
    if is_featured:
        return {
            "status": "featured",
            "since": data.get("featured_since"),
            "piece_url": data.get("featured_piece_url"),
            "pieces_count": data.get("featured_pieces_count", 1),
        }
    elif is_eligible:
        return {
            "status": "eligible",
            "message": "You're eligible to submit for Featured!",
            "cta": "Submit your work",
        }
    else:
        # Show progress toward eligibility
        streak_7_progress = min(100, int((data.get("streak_days", 0) / 7) * 100))
        return {
            "status": "in_progress",
            "requirement": "7-day 1K streak",
            "progress_percent": streak_7_progress,
        }


@router.get("/writer/authority")
async def get_authority_progress(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get Authority Writer progress."""
    # Would query authority tracking
    data = _user_data.get(user_id, {})
    
    if not data.get("featured_writer"):
        return {"error": "Must be Featured Writer first"}
    
    return {
        "is_authority": data.get("authority_writer", False),
        "progress": {
            "featured_pieces": {"current": data.get("featured_pieces_count", 1), "target": 3},
            "lifetime_words": {"current": data.get("lifetime_words", 0), "target": 50000},
            "streak_30_count": {"current": data.get("streak_30_count", 0), "target": 2},
            "days_as_featured": {"current": data.get("days_as_featured", 0), "target": 90},
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# READER SECTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/reader/activity")
async def get_reading_activity(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get reading activity stats."""
    data = _user_data.get(user_id, {})
    
    posts_this_week = data.get("posts_read_this_week", 0)
    
    if posts_this_week == 0:
        return {
            "has_activity": False,
            "empty_state": get_empty_state(DashboardSection.READING_ACTIVITY),
        }
    
    return {
        "has_activity": True,
        "posts_this_week": posts_this_week,
        "deep_reads_this_week": data.get("deep_reads_this_week", 0),
        "streak_days": data.get("reading_streak", 0),
        "profile_types_explored": data.get("profile_types_explored", []),
    }


@router.get("/reader/taste")
async def get_reading_taste(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get reading taste profile."""
    data = _user_data.get(user_id, {})
    taste = data.get("reading_taste")
    
    if not taste:
        return {
            "has_taste": False,
            "empty_state": get_empty_state(DashboardSection.READING_TASTE),
        }
    
    return {
        "has_taste": True,
        "primary_type": taste.get("primary_type"),
        "stance_preference": taste.get("stance"),
        "top_preferences": taste.get("top_preferences", [])[:3],
    }


@router.get("/reader/bookmarks")
async def get_bookmarks_summary(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get bookmarks summary."""
    data = _user_data.get(user_id, {})
    tier = data.get("tier", "free")
    
    bookmarks = data.get("bookmarks", [])
    limit = -1 if tier in ["curator", "bundle"] else 10
    
    if not bookmarks:
        return {
            "has_bookmarks": False,
            "empty_state": get_empty_state(DashboardSection.BOOKMARKS),
        }
    
    return {
        "has_bookmarks": True,
        "count": len(bookmarks),
        "limit": limit,
        "at_limit": limit > 0 and len(bookmarks) >= limit,
        "recent": bookmarks[:5],
    }


@router.get("/reader/curator")
async def get_curator_progress(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get Curator milestone progress."""
    data = _user_data.get(user_id, {})
    
    return {
        "window_active": data.get("curator_window_active", False),
        "window_days_remaining": data.get("curator_window_days", 30),
        "progress": {
            "posts_read": {"current": data.get("curator_posts_read", 0), "target": 20},
            "deep_reads": {"current": data.get("curator_deep_reads", 0), "target": 5},
            "profile_types": {"current": len(data.get("profile_types_explored", [])), "target": 5},
            "bookmarks": {"current": len(data.get("bookmarks", [])), "target": 10},
            "reading_streak": {"current": data.get("reading_streak", 0), "target": 7},
        },
        "featured_eligible": data.get("featured_curator_eligible", False),
    }


@router.get("/reader/paths")
async def get_featured_paths(user_id: str = Depends(require_auth)) -> Dict[str, Any]:
    """Get Featured Curator paths."""
    data = _user_data.get(user_id, {})
    
    if not data.get("featured_curator"):
        return {"error": "Must be Featured Curator first"}
    
    return {
        "paths": data.get("curated_paths", []),
        "total_follows": data.get("total_path_follows", 0),
    }


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(user_id: str = Depends(require_auth)):
    """Get all settings with current values."""
    current = _user_settings.get(user_id, {
        "email": "",
        "display_name": "",
        "visibility": "private",
        "timezone": "America/Toronto",
        "currency": "cad",
        "voice_sharing": False,
        "taste_sharing": False,
    })
    
    categories = {}
    for category, items in SETTINGS_CONFIG.items():
        categories[category.value] = [
            {
                "id": item.id,
                "label": item.label,
                "description": item.description,
                "type": item.type,
                "options": item.options,
                "action_label": item.action_label,
                "danger": item.danger,
            }
            for item in items
        ]
    
    return SettingsResponse(
        categories=categories,
        current_values=current,
    )


@router.patch("/settings")
async def update_setting(
    request: UpdateSettingRequest,
    user_id: str = Depends(require_auth),
):
    """Update a single setting."""
    settings = _user_settings.get(user_id, {})
    settings[request.setting_id] = request.value
    _user_settings[user_id] = settings
    
    return {"success": True, "setting_id": request.setting_id}


@router.post("/settings/export")
async def export_data(user_id: str = Depends(require_auth)):
    """Export all user data as JSON."""
    # Aggregate all user data
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "profile": _user_settings.get(user_id, {}),
        "dashboard_data": _user_data.get(user_id, {}),
        # Would include: analyses, milestones, bookmarks, etc.
    }
    
    # Create JSON file
    json_str = json.dumps(export_data, indent=2, default=str)
    
    filename = EXPORT_CONFIG["filename_template"].format(
        user_id=user_id[:8],
        date=date.today().isoformat(),
    )
    
    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# QUICK ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/quick-actions")
async def get_quick_actions(user_id: str = Depends(require_auth)):
    """Get contextual quick actions for user."""
    tier = get_user_tier(user_id)
    data = _user_data.get(user_id, {})
    
    actions = []
    
    # Streak at risk
    if data.get("streak_days", 0) > 0 and not data.get("wrote_today"):
        actions.append({
            "id": "save_streak",
            "label": f"Save your {data.get('streak_days')}-day streak!",
            "icon": "🔥",
            "url": "/analyze",
            "priority": "high",
        })
    
    # Trial ending soon
    if tier == "trial" and data.get("trial_days_left", 0) <= 2:
        actions.append({
            "id": "upgrade",
            "label": f"Trial ends in {data.get('trial_days_left')} days",
            "icon": "⏰",
            "url": "/pricing",
            "priority": "high",
        })
    
    # Featured eligible
    if data.get("featured_eligible") and not data.get("featured_writer"):
        actions.append({
            "id": "submit_featured",
            "label": "Submit for Featured Writer!",
            "icon": "⭐",
            "url": "/featured/submit",
            "priority": "medium",
        })
    
    return {"actions": actions}
