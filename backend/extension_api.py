#!/usr/bin/env python3
"""
QUIRRELY EXTENSION API v1.0
Sync endpoint for Chrome Extension v2.0.0

This API provides:
- /api/extension/sync - Get user data, tier, STRETCH progress
- /api/extension/events - Track extension analytics
- /api/extension/health - Extension-specific health check

Deployed as part of the main API or as standalone service.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class ExtensionSyncResponse(BaseModel):
    """Response for /api/extension/sync"""
    success: bool = True
    user: Optional[Dict[str, Any]] = None
    stretch: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, bool]] = None


class ExtensionEventRequest(BaseModel):
    """Request body for /api/extension/events"""
    event: str
    data: Optional[Dict[str, Any]] = None
    source: str = "extension"
    version: str = "2.0.0"
    timestamp: Optional[str] = None


class ExtensionEventResponse(BaseModel):
    """Response for /api/extension/events"""
    success: bool = True
    tracked: bool = True
    event_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# MOCK DATA STORES (Replace with actual DB queries in production)
# ═══════════════════════════════════════════════════════════════════════════

class MockUserStore:
    """Mock user data store."""
    
    _users = {
        "test_user_123": {
            "id": "test_user_123",
            "email": "test@example.com",
            "tier": "pro",
            "trial_ends": None,
            "trial_days_remaining": 0,
            "created_at": "2026-01-15T10:00:00Z"
        }
    }
    
    _stretch_data = {
        "test_user_123": {
            "streak": 5,
            "completed": 23,
            "last_completed": "2026-02-18T14:30:00Z",
            "eligible": True,
            "exercises_today": 1,
            "milestones": ["first_stretch", "week_streak", "voice_explorer"]
        }
    }
    
    @classmethod
    def get_user_by_session(cls, session_token: str) -> Optional[Dict]:
        """Get user data by session token."""
        # In production, validate session token and fetch from DB
        if session_token and session_token.startswith("qr_sess_"):
            return cls._users.get("test_user_123")
        return None
    
    @classmethod
    def get_stretch_data(cls, user_id: str) -> Optional[Dict]:
        """Get STRETCH progress for user."""
        return cls._stretch_data.get(user_id)


class MockAnalyticsStore:
    """Mock analytics event store."""
    
    _events = []
    
    @classmethod
    def track_event(cls, event: str, data: Dict, source: str, version: str) -> str:
        """Track an analytics event."""
        event_id = f"evt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(cls._events)}"
        cls._events.append({
            "id": event_id,
            "event": event,
            "data": data,
            "source": source,
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        })
        return event_id


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/extension", tags=["Extension"])


@router.get("/sync", response_model=ExtensionSyncResponse)
async def sync_extension(
    request: Request,
    x_extension_version: Optional[str] = Header(None, alias="X-Extension-Version"),
    authorization: Optional[str] = Header(None)
):
    """
    Sync extension with web app.
    
    Returns user data, tier info, and STRETCH progress.
    Used by extension on popup open.
    
    Headers:
    - X-Extension-Version: Extension version (e.g., "2.0.0")
    - Authorization: Session token (optional, from cookies)
    """
    # Try to get session from cookie or header
    session_token = None
    
    # Check for session cookie
    if request.cookies.get("qr_session"):
        session_token = request.cookies.get("qr_session")
    
    # Check for Authorization header (Bearer token)
    if authorization and authorization.startswith("Bearer "):
        session_token = authorization[7:]
    
    # If no session, return anonymous state
    if not session_token:
        return ExtensionSyncResponse(
            success=True,
            user=None,
            stretch={
                "streak": 0,
                "completed": 0,
                "eligible": True
            },
            limits={
                "daily_limit": 3,
                "used_today": 0,
                "remaining": 3
            },
            features={
                "stretch": True,
                "compare": True,
                "history": True,
                "export": False,
                "api_access": False
            }
        )
    
    # Get user data
    user = MockUserStore.get_user_by_session(session_token)
    
    if not user:
        return ExtensionSyncResponse(
            success=True,
            user=None,
            stretch={"streak": 0, "completed": 0, "eligible": True},
            limits={"daily_limit": 3, "used_today": 0, "remaining": 3},
            features={"stretch": True, "compare": True, "history": True, "export": False, "api_access": False}
        )
    
    # Get STRETCH data
    stretch_data = MockUserStore.get_stretch_data(user["id"])
    
    # Determine limits based on tier
    tier_limits = {
        "free": 5,
        "trial": 100,
        "pro": 1000,
        "authority": 10000
    }
    
    daily_limit = tier_limits.get(user.get("tier", "free"), 5)
    
    # Determine feature access based on tier
    tier_features = {
        "free": {"stretch": True, "compare": True, "history": True, "export": False, "api_access": False},
        "trial": {"stretch": True, "compare": True, "history": True, "export": True, "api_access": False},
        "pro": {"stretch": True, "compare": True, "history": True, "export": True, "api_access": True},
        "authority": {"stretch": True, "compare": True, "history": True, "export": True, "api_access": True}
    }
    
    features = tier_features.get(user.get("tier", "free"), tier_features["free"])
    
    return ExtensionSyncResponse(
        success=True,
        user={
            "id": user["id"],
            "email": user.get("email"),
            "tier": user.get("tier", "free"),
            "trial_ends": user.get("trial_ends"),
            "trial_days_remaining": user.get("trial_days_remaining", 0)
        },
        stretch={
            "streak": stretch_data.get("streak", 0) if stretch_data else 0,
            "completed": stretch_data.get("completed", 0) if stretch_data else 0,
            "eligible": stretch_data.get("eligible", True) if stretch_data else True,
            "last_completed": stretch_data.get("last_completed") if stretch_data else None,
            "milestones": stretch_data.get("milestones", []) if stretch_data else []
        },
        limits={
            "daily_limit": daily_limit,
            "used_today": 0,  # Would query from DB
            "remaining": daily_limit
        },
        features=features
    )


@router.post("/events", response_model=ExtensionEventResponse)
async def track_extension_event(
    event_request: ExtensionEventRequest,
    x_extension_version: Optional[str] = Header(None, alias="X-Extension-Version")
):
    """
    Track an analytics event from the extension.
    
    Events:
    - analysis_complete: User completed an analysis
    - popup_opened: Extension popup was opened
    - stretch_cta_clicked: User clicked STRETCH CTA
    - compare_used: User used compare feature
    - settings_changed: User changed settings
    """
    # Track the event
    event_id = MockAnalyticsStore.track_event(
        event=event_request.event,
        data=event_request.data or {},
        source=event_request.source,
        version=event_request.version or x_extension_version or "unknown"
    )
    
    return ExtensionEventResponse(
        success=True,
        tracked=True,
        event_id=event_id
    )


@router.get("/health")
async def extension_health():
    """
    Health check for extension API.
    
    Returns service status for extension to verify connectivity.
    """
    return {
        "status": "healthy",
        "service": "extension-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "sync": True,
            "events": True,
            "stretch_integration": True
        }
    }


@router.options("/sync")
async def sync_options():
    """Handle CORS preflight for sync endpoint."""
    return Response(status_code=200)


@router.options("/events")
async def events_options():
    """Handle CORS preflight for events endpoint."""
    return Response(status_code=200)


# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE APP (for testing)
# ═══════════════════════════════════════════════════════════════════════════

def create_extension_app() -> FastAPI:
    """Create standalone FastAPI app for extension API."""
    app = FastAPI(
        title="Quirrely Extension API",
        version="1.0.0",
        description="API for Chrome Extension sync and analytics"
    )
    
    # CORS for extension
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "chrome-extension://*",
            "https://quirrely.com",
            "http://localhost:*"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Extension-Version"]
    )
    
    app.include_router(router)
    
    @app.get("/")
    async def root():
        return {"service": "Quirrely Extension API", "version": "1.0.0"}
    
    return app


# For direct execution
if __name__ == "__main__":
    import uvicorn
    app = create_extension_app()
    print("Starting Quirrely Extension API...")
    print("Docs: http://localhost:8001/docs")
    print("Sync: http://localhost:8001/api/extension/sync")
    uvicorn.run(app, host="0.0.0.0", port=8001)
