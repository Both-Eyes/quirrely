#!/usr/bin/env python3
"""
QUIRRELY CONVERSION EVENTS v1.0
Track and analyze conversion funnel events.

This module provides:
1. Standardized conversion event definitions
2. Event emission to Meta pipeline
3. Funnel analytics aggregation
4. Revenue attribution tracking

Events tracked:
- Signup, trial, subscription lifecycle
- Addon purchases
- Tier upgrades/downgrades
- Feature engagement
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from dependencies import get_current_user, CurrentUser
from halo_bridge import get_halo_bridge, HALOEventType

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/conversions", tags=["conversions"])


# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ConversionEvent(str, Enum):
    """Conversion funnel events."""
    
    # Signup funnel
    SIGNUP_STARTED = "signup.started"
    SIGNUP_COMPLETED = "signup.completed"
    SIGNUP_ABANDONED = "signup.abandoned"
    
    # Trial funnel
    TRIAL_STARTED = "trial.started"
    TRIAL_EXTENDED = "trial.extended"
    TRIAL_EXPIRING = "trial.expiring"        # 3 days left
    TRIAL_EXPIRED = "trial.expired"
    TRIAL_CONVERTED = "trial.converted"
    
    # Subscription funnel
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_RENEWED = "subscription.renewed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    SUBSCRIPTION_EXPIRED = "subscription.expired"
    SUBSCRIPTION_REACTIVATED = "subscription.reactivated"
    
    # Addon funnel
    ADDON_TRIAL_STARTED = "addon.trial.started"
    ADDON_TRIAL_EXPIRED = "addon.trial.expired"
    ADDON_PURCHASED = "addon.purchased"
    ADDON_CANCELLED = "addon.cancelled"
    
    # Tier progression
    TIER_UPGRADED = "tier.upgraded"
    TIER_DOWNGRADED = "tier.downgraded"
    
    # Engagement
    ANALYSIS_COMPLETED = "engagement.analysis.completed"
    ANALYSIS_LIMIT_REACHED = "engagement.analysis.limit_reached"
    FEATURE_GATED_CLICK = "engagement.feature.gated_click"
    
    # Upgrade prompts
    UPGRADE_PROMPT_SHOWN = "prompt.upgrade.shown"
    UPGRADE_PROMPT_CLICKED = "prompt.upgrade.clicked"
    UPGRADE_PROMPT_DISMISSED = "prompt.upgrade.dismissed"
    
    # Churn signals
    CHURN_RISK_DETECTED = "churn.risk.detected"
    WINBACK_EMAIL_SENT = "churn.winback.sent"
    WINBACK_CONVERTED = "churn.winback.converted"


# ═══════════════════════════════════════════════════════════════════════════
# EVENT DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ConversionEventData:
    """Conversion event with metadata."""
    event: ConversionEvent
    user_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Event context
    tier: Optional[str] = None
    country: Optional[str] = None
    source: Optional[str] = None  # organic, paid, referral, etc.
    
    # Revenue data
    revenue: Optional[float] = None
    currency: str = "USD"
    
    # Attribution
    session_id: Optional[str] = None
    campaign_id: Optional[str] = None
    referrer_id: Optional[str] = None
    
    # Event-specific data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "tier": self.tier,
            "country": self.country,
            "source": self.source,
            "revenue": self.revenue,
            "currency": self.currency,
            "session_id": self.session_id,
            "campaign_id": self.campaign_id,
            "referrer_id": self.referrer_id,
            "metadata": self.metadata,
        }


class ConversionEventRequest(BaseModel):
    """API request for conversion event."""
    event: str = Field(..., description="Event type")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    source: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class ConversionTracker:
    """
    Tracks conversion events and forwards to Meta/HALO.
    """
    
    def __init__(self):
        self._events: List[ConversionEventData] = []
        self._max_events = 10000
        self._halo = get_halo_bridge()
        
        # Aggregated stats
        self._stats = defaultdict(int)
        self._revenue = defaultdict(float)
    
    async def track(self, event: ConversionEventData) -> bool:
        """
        Track a conversion event.
        
        Returns True if successfully forwarded to Meta.
        """
        # Store locally
        self._events.append(event)
        self._stats[event.event.value] += 1
        
        if event.revenue:
            self._revenue[event.event.value] += event.revenue
        
        # Trim old events
        while len(self._events) > self._max_events:
            self._events.pop(0)
        
        # Forward to HALO
        try:
            await self._halo.observe_conversion(
                user_id=event.user_id,
                conversion_type=event.event.value,
                details=event.to_dict(),
                session_id=event.session_id,
            )
            logger.info(f"Conversion tracked: {event.event.value} for {event.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to forward conversion: {e}")
            return False
    
    # ─────────────────────────────────────────────────────────────────────────
    # Convenience Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    async def track_signup(
        self,
        user_id: str,
        country: str,
        source: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Track signup completion."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.SIGNUP_COMPLETED,
            user_id=user_id,
            country=country,
            source=source,
            metadata=kwargs,
        ))
    
    async def track_trial_started(
        self,
        user_id: str,
        tier: str = "trial",
        **kwargs,
    ) -> bool:
        """Track trial start."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.TRIAL_STARTED,
            user_id=user_id,
            tier=tier,
            metadata=kwargs,
        ))
    
    async def track_subscription(
        self,
        user_id: str,
        tier: str,
        plan: str,  # "monthly" or "annual"
        revenue: float,
        **kwargs,
    ) -> bool:
        """Track subscription creation."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.SUBSCRIPTION_CREATED,
            user_id=user_id,
            tier=tier,
            revenue=revenue,
            metadata={"plan": plan, **kwargs},
        ))
    
    async def track_addon_purchase(
        self,
        user_id: str,
        addon: str,
        revenue: float,
        **kwargs,
    ) -> bool:
        """Track addon purchase."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.ADDON_PURCHASED,
            user_id=user_id,
            revenue=revenue,
            metadata={"addon": addon, **kwargs},
        ))
    
    async def track_tier_upgrade(
        self,
        user_id: str,
        old_tier: str,
        new_tier: str,
        **kwargs,
    ) -> bool:
        """Track tier upgrade."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.TIER_UPGRADED,
            user_id=user_id,
            tier=new_tier,
            metadata={"old_tier": old_tier, "new_tier": new_tier, **kwargs},
        ))
    
    async def track_upgrade_prompt(
        self,
        user_id: str,
        prompt_type: str,
        action: str,  # "shown", "clicked", "dismissed"
        **kwargs,
    ) -> bool:
        """Track upgrade prompt interaction."""
        event_map = {
            "shown": ConversionEvent.UPGRADE_PROMPT_SHOWN,
            "clicked": ConversionEvent.UPGRADE_PROMPT_CLICKED,
            "dismissed": ConversionEvent.UPGRADE_PROMPT_DISMISSED,
        }
        event = event_map.get(action, ConversionEvent.UPGRADE_PROMPT_SHOWN)
        
        return await self.track(ConversionEventData(
            event=event,
            user_id=user_id,
            metadata={"prompt_type": prompt_type, **kwargs},
        ))
    
    async def track_analysis_limit(
        self,
        user_id: str,
        limit: int,
        used: int,
        **kwargs,
    ) -> bool:
        """Track analysis limit reached."""
        return await self.track(ConversionEventData(
            event=ConversionEvent.ANALYSIS_LIMIT_REACHED,
            user_id=user_id,
            metadata={"limit": limit, "used": used, **kwargs},
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Analytics
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversion statistics."""
        return {
            "total_events": len(self._events),
            "events_by_type": dict(self._stats),
            "revenue_by_type": dict(self._revenue),
            "total_revenue": sum(self._revenue.values()),
        }
    
    def get_funnel(self, days: int = 30) -> Dict[str, int]:
        """Get funnel metrics for time period."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        funnel = defaultdict(int)
        for event in self._events:
            if event.timestamp >= cutoff:
                funnel[event.event.value] += 1
        
        return dict(funnel)
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events."""
        return [e.to_dict() for e in self._events[-limit:]]


# Singleton tracker
_tracker: Optional[ConversionTracker] = None

def get_conversion_tracker() -> ConversionTracker:
    """Get or create conversion tracker."""
    global _tracker
    if _tracker is None:
        _tracker = ConversionTracker()
    return _tracker


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/track")
async def track_conversion_event(
    request: ConversionEventRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Track a conversion event from frontend.
    """
    tracker = get_conversion_tracker()
    
    try:
        event_type = ConversionEvent(request.event)
    except ValueError:
        return {"status": "error", "message": f"Unknown event: {request.event}"}
    
    event = ConversionEventData(
        event=event_type,
        user_id=user.id,
        tier=user.tier.value if hasattr(user.tier, 'value') else str(user.tier),
        country=user.country,
        source=request.source,
        session_id=request.session_id,
        metadata=request.metadata,
    )
    
    # Track in background
    background_tasks.add_task(tracker.track, event)
    
    return {"status": "accepted", "event": request.event}


@router.post("/upgrade-prompt")
async def track_upgrade_prompt_event(
    prompt_type: str,
    action: str,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Track upgrade prompt interaction.
    """
    tracker = get_conversion_tracker()
    
    background_tasks.add_task(
        tracker.track_upgrade_prompt,
        user_id=user.id,
        prompt_type=prompt_type,
        action=action,
    )
    
    return {"status": "accepted"}


@router.get("/stats")
async def get_conversion_stats():
    """
    Get conversion statistics (admin endpoint).
    """
    tracker = get_conversion_tracker()
    return tracker.get_stats()


@router.get("/funnel")
async def get_conversion_funnel(days: int = 30):
    """
    Get funnel metrics (admin endpoint).
    """
    tracker = get_conversion_tracker()
    return {
        "period_days": days,
        "funnel": tracker.get_funnel(days),
    }


@router.get("/events/recent")
async def get_recent_conversion_events(limit: int = 50):
    """
    Get recent conversion events (admin endpoint).
    """
    tracker = get_conversion_tracker()
    return {
        "events": tracker.get_recent_events(limit),
    }


# ═══════════════════════════════════════════════════════════════════════════
# HELPER: Track from other modules
# ═══════════════════════════════════════════════════════════════════════════

async def track_signup_conversion(
    user_id: str,
    country: str,
    source: str = "organic",
    background_tasks: BackgroundTasks = None,
):
    """Helper to track signup from auth module."""
    tracker = get_conversion_tracker()
    
    if background_tasks:
        background_tasks.add_task(
            tracker.track_signup,
            user_id=user_id,
            country=country,
            source=source,
        )
    else:
        await tracker.track_signup(user_id, country, source)


async def track_subscription_conversion(
    user_id: str,
    tier: str,
    plan: str,
    revenue: float,
    background_tasks: BackgroundTasks = None,
):
    """Helper to track subscription from payments module."""
    tracker = get_conversion_tracker()
    
    if background_tasks:
        background_tasks.add_task(
            tracker.track_subscription,
            user_id=user_id,
            tier=tier,
            plan=plan,
            revenue=revenue,
        )
    else:
        await tracker.track_subscription(user_id, tier, plan, revenue)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

def init_conversion_events(app):
    """Initialize conversion events routes."""
    app.include_router(router)
    logger.info("Conversion events API initialized")


if __name__ == "__main__":
    print("Conversion Events module loaded")
    print(f"Event types: {len(ConversionEvent)}")
