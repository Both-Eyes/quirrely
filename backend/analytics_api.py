#!/usr/bin/env python3
"""
QUIRRELY ANALYTICS API v1.0
Endpoints for user-facing analytics and admin reporting.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel

from analytics_config import (
    EventName,
    FUNNELS,
    FEATURE_FLAGS,
    is_feature_enabled,
)
from analytics_service import (
    get_analytics_service,
    get_metrics_collector,
    get_funnel_analyzer,
    get_retention_analyzer,
    get_user_analytics,
    AnalyticsService,
    MetricsCollector,
    UserAnalytics,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/analytics", tags=["analytics"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class TrackEventRequest(BaseModel):
    event: str
    properties: Optional[Dict[str, Any]] = None


class WriterAnalyticsResponse(BaseModel):
    period: str
    words_over_time: List[Dict[str, Any]]
    streak_history: List[Dict[str, Any]]
    total_words: int
    total_analyses: int
    longest_streak: int
    current_streak: int


class ReaderAnalyticsResponse(BaseModel):
    period: str
    reading_over_time: List[Dict[str, Any]]
    deep_read_ratio: float
    total_posts_read: int
    total_deep_reads: int
    profiles_explored: List[str]


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    return None


def require_auth(authorization: Optional[str] = Header(None)) -> str:
    user_id = get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


def require_admin(authorization: Optional[str] = Header(None)) -> str:
    # Would check admin role
    if not authorization:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return "admin"


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TRACKING
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/track")
async def track_event(
    request: TrackEventRequest,
    user_id: Optional[str] = Depends(get_user_id),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Track an analytics event."""
    try:
        event_name = EventName(request.event)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid event: {request.event}")
    
    await service.track(
        event_name=event_name,
        user_id=user_id,
        properties=request.properties,
    )
    
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════════════
# USER-FACING ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/me/writer")
async def get_my_writer_analytics(
    period: str = "30d",
    user_id: str = Depends(require_auth),
    analytics: UserAnalytics = Depends(get_user_analytics),
):
    """Get authenticated user's writer analytics."""
    if period not in ["30d", "90d", "365d"]:
        period = "30d"
    
    return await analytics.get_writer_analytics(user_id, period)


@router.get("/me/reader")
async def get_my_reader_analytics(
    period: str = "30d",
    user_id: str = Depends(require_auth),
    analytics: UserAnalytics = Depends(get_user_analytics),
):
    """Get authenticated user's reader analytics."""
    if period not in ["30d", "90d", "365d"]:
        period = "30d"
    
    return await analytics.get_reader_analytics(user_id, period)


@router.get("/me/featured")
async def get_my_featured_analytics(
    period: str = "30d",
    user_id: str = Depends(require_auth),
    analytics: UserAnalytics = Depends(get_user_analytics),
):
    """Get authenticated user's Featured analytics."""
    if period not in ["30d", "90d", "365d"]:
        period = "30d"
    
    return await analytics.get_featured_analytics(user_id, period)


@router.get("/me/summary")
async def get_my_analytics_summary(
    user_id: str = Depends(require_auth),
    analytics: UserAnalytics = Depends(get_user_analytics),
):
    """Get quick summary of user's analytics."""
    writer = await analytics.get_writer_analytics(user_id, "30d")
    
    return {
        "total_words": writer.get("total_words", 0),
        "total_analyses": writer.get("total_analyses", 0),
        "current_streak": writer.get("current_streak", 0),
        "longest_streak": writer.get("longest_streak", 0),
    }


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/metrics")
async def get_admin_metrics(
    for_date: Optional[str] = None,
    admin: str = Depends(require_admin),
    collector: MetricsCollector = Depends(get_metrics_collector),
):
    """Get admin metrics for a date."""
    target_date = date.fromisoformat(for_date) if for_date else date.today() - timedelta(days=1)
    return await collector.collect_daily_metrics(target_date)


@router.get("/admin/metrics/range")
async def get_admin_metrics_range(
    start_date: str,
    end_date: str,
    admin: str = Depends(require_admin),
    collector: MetricsCollector = Depends(get_metrics_collector),
):
    """Get admin metrics for a date range."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    
    metrics = []
    current = start
    while current <= end:
        day_metrics = await collector.collect_daily_metrics(current)
        metrics.append(day_metrics)
        current += timedelta(days=1)
    
    return {"metrics": metrics}


@router.get("/admin/funnels")
async def list_funnels(admin: str = Depends(require_admin)):
    """List available funnels."""
    return {
        "funnels": [
            {"name": name, "display_name": config["name"], "steps": config["steps"]}
            for name, config in FUNNELS.items()
        ]
    }


@router.get("/admin/funnels/{funnel_name}")
async def get_funnel_analysis(
    funnel_name: str,
    start_date: str,
    end_date: str,
    admin: str = Depends(require_admin),
):
    """Analyze a specific funnel."""
    analyzer = get_funnel_analyzer()
    
    return await analyzer.analyze_funnel(
        funnel_name,
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    )


@router.get("/admin/retention")
async def get_retention_analysis(
    cohort_date: str,
    periods: int = 12,
    period_type: str = "weekly",
    admin: str = Depends(require_admin),
):
    """Get retention cohort analysis."""
    analyzer = get_retention_analyzer()
    
    return await analyzer.get_cohort_retention(
        date.fromisoformat(cohort_date),
        periods,
        period_type,
    )


@router.get("/admin/retention/matrix")
async def get_retention_matrix(
    start_date: str,
    cohort_count: int = 12,
    period_type: str = "weekly",
    admin: str = Depends(require_admin),
):
    """Get retention matrix for multiple cohorts."""
    analyzer = get_retention_analyzer()
    start = date.fromisoformat(start_date)
    
    matrix = []
    for i in range(cohort_count):
        if period_type == "weekly":
            cohort_date = start - timedelta(weeks=i)
        else:
            cohort_date = start - timedelta(days=30 * i)
        
        cohort = await analyzer.get_cohort_retention(cohort_date, 12, period_type)
        matrix.append(cohort)
    
    return {"matrix": matrix}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/features")
async def get_feature_flags(
    user_id: Optional[str] = Depends(get_user_id),
):
    """Get feature flags for user."""
    flags = {}
    for flag_name in FEATURE_FLAGS:
        flags[flag_name] = is_feature_enabled(flag_name, user_id)
    
    return {"flags": flags}


@router.get("/features/{flag_name}")
async def check_feature_flag(
    flag_name: str,
    user_id: Optional[str] = Depends(get_user_id),
):
    """Check specific feature flag."""
    if flag_name not in FEATURE_FLAGS:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    
    return {
        "flag": flag_name,
        "enabled": is_feature_enabled(flag_name, user_id),
    }


@router.get("/admin/features")
async def get_all_feature_flags(admin: str = Depends(require_admin)):
    """Get all feature flags with config (admin)."""
    return {
        "flags": [
            {
                "name": flag.name,
                "description": flag.description,
                "enabled": flag.enabled,
                "percentage": flag.percentage,
                "allowed_users_count": len(flag.allowed_users) if flag.allowed_users else 0,
            }
            for flag in FEATURE_FLAGS.values()
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════
# REAL-TIME METRICS (for dashboard)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/realtime")
async def get_realtime_metrics(admin: str = Depends(require_admin)):
    """Get real-time metrics for admin dashboard."""
    # Would query real-time data
    return {
        "active_users_now": 47,
        "analyses_last_hour": 123,
        "words_last_hour": 34567,
        "signups_today": 12,
        "revenue_today": 89.97,
    }


# ═══════════════════════════════════════════════════════════════════════════
# VOICE PROFILE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/distribution/profiles")
async def get_profile_distribution(admin: str = Depends(require_admin)):
    """Get distribution of voice profiles."""
    # Would query from database
    return {
        "profiles": [
            {"type": "The Analyst", "count": 234, "percent": 18.8},
            {"type": "The Storyteller", "count": 312, "percent": 25.0},
            {"type": "The Advocate", "count": 198, "percent": 15.9},
            {"type": "The Observer", "count": 156, "percent": 12.5},
            {"type": "The Guide", "count": 187, "percent": 15.0},
            {"type": "The Innovator", "count": 160, "percent": 12.8},
        ],
        "total": 1247,
    }


@router.get("/admin/distribution/stances")
async def get_stance_distribution(admin: str = Depends(require_admin)):
    """Get distribution of stances."""
    return {
        "stances": [
            {"stance": "Assertive", "count": 423, "percent": 33.9},
            {"stance": "Measured", "count": 512, "percent": 41.1},
            {"stance": "Exploratory", "count": 312, "percent": 25.0},
        ],
        "total": 1247,
    }
