#!/usr/bin/env python3
"""
LNCP Meta Events API
Version: 1.0.0

Receives frontend events and forwards them to the Meta orchestration system.
Provides the backend endpoint for the MetaEvents frontend library.

Endpoints:
    POST /api/meta/events      - Single event
    POST /api/meta/events/batch - Batch events
    GET  /api/meta/events/stats - Event statistics (admin)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

# Import Meta components
try:
    from lncp.meta.events.bus import get_event_bus, Event
    from lncp.meta.halo_observer import get_halo_observer
    META_AVAILABLE = True
except ImportError:
    META_AVAILABLE = False
    logging.warning("Meta components not available, events will be logged only")


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/meta", tags=["meta-events"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class MetaEventData(BaseModel):
    """Single event from frontend."""
    event: str = Field(..., description="Event name")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    sessionId: str = Field(..., description="Session ID")
    userId: Optional[str] = Field(None, description="User ID if authenticated")
    page: str = Field("", description="Current page path")
    userAgent: str = Field("", description="User agent string")
    referrer: str = Field("", description="Referrer URL")


class BatchEventsRequest(BaseModel):
    """Batch of events from frontend."""
    events: List[MetaEventData] = Field(..., description="List of events")


class EventStats(BaseModel):
    """Event statistics."""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_page: Dict[str, int]
    unique_sessions: int
    unique_users: int
    time_range_hours: int


# ═══════════════════════════════════════════════════════════════════════════
# EVENT STORAGE (in-memory for now, production would use DB/queue)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EventStore:
    """In-memory event store with basic statistics."""
    events: List[Dict] = field(default_factory=list)
    max_events: int = 10000
    
    # Statistics
    events_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    events_by_page: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    sessions: set = field(default_factory=set)
    users: set = field(default_factory=set)
    
    def add_event(self, event: MetaEventData) -> None:
        """Add an event to the store."""
        event_dict = event.dict()
        event_dict['received_at'] = datetime.utcnow().isoformat()
        
        self.events.append(event_dict)
        
        # Update statistics
        self.events_by_type[event.event] += 1
        if event.page:
            self.events_by_page[event.page] += 1
        self.sessions.add(event.sessionId)
        if event.userId:
            self.users.add(event.userId)
        
        # Trim if needed
        while len(self.events) > self.max_events:
            self.events.pop(0)
    
    def get_stats(self, hours: int = 24) -> EventStats:
        """Get event statistics."""
        return EventStats(
            total_events=len(self.events),
            events_by_type=dict(self.events_by_type),
            events_by_page=dict(self.events_by_page),
            unique_sessions=len(self.sessions),
            unique_users=len(self.users),
            time_range_hours=hours,
        )
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events."""
        return self.events[-limit:]


# Singleton store
_event_store: Optional[EventStore] = None

def get_event_store() -> EventStore:
    """Get or create event store."""
    global _event_store
    if _event_store is None:
        _event_store = EventStore()
    return _event_store


# ═══════════════════════════════════════════════════════════════════════════
# META INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

async def forward_to_meta(event: MetaEventData) -> None:
    """Forward event to Meta orchestration system."""
    if not META_AVAILABLE:
        logger.debug(f"Meta not available, event logged: {event.event}")
        return
    
    try:
        # Get event bus
        bus = get_event_bus()
        
        # Create Meta event
        meta_event = Event(
            type=f"frontend.{event.event}",
            source="frontend",
            data={
                **event.data,
                'session_id': event.sessionId,
                'user_id': event.userId,
                'page': event.page,
                'timestamp_ms': event.timestamp,
            },
            timestamp=datetime.utcfromtimestamp(event.timestamp / 1000),
        )
        
        # Publish to event bus
        await bus.publish(meta_event)
        
        # Forward to HALO observer for user behavior tracking
        if event.userId:
            observer = get_halo_observer()
            await observer.observe_user_event(
                user_id=event.userId,
                event_type=event.event,
                event_data=event.data,
            )
        
        logger.debug(f"Event forwarded to Meta: {event.event}")
        
    except Exception as e:
        logger.error(f"Failed to forward event to Meta: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/events")
async def receive_event(
    event: MetaEventData,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receive a single event from the frontend.
    
    This endpoint is designed to be fast and non-blocking.
    Event processing is done in the background.
    """
    # Add to local store
    store = get_event_store()
    store.add_event(event)
    
    # Forward to Meta in background
    background_tasks.add_task(forward_to_meta, event)
    
    # Add request context
    event.data['client_ip'] = request.client.host if request.client else None
    
    logger.info(f"Event received: {event.event} from session {event.sessionId[:8]}...")
    
    return {"status": "accepted", "event_id": f"{event.sessionId}_{event.timestamp}"}


@router.post("/events/batch")
async def receive_batch_events(
    batch: BatchEventsRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Receive a batch of events from the frontend.
    
    Used for queue flush and reliable delivery.
    """
    store = get_event_store()
    client_ip = request.client.host if request.client else None
    
    accepted = 0
    for event in batch.events:
        # Add request context
        event.data['client_ip'] = client_ip
        
        # Add to store
        store.add_event(event)
        
        # Forward to Meta
        background_tasks.add_task(forward_to_meta, event)
        
        accepted += 1
    
    logger.info(f"Batch received: {accepted} events")
    
    return {
        "status": "accepted",
        "events_accepted": accepted,
        "events_total": len(batch.events),
    }


@router.get("/events/stats")
async def get_event_stats(
    hours: int = 24,
):
    """
    Get event statistics (admin endpoint).
    
    TODO: Add admin authentication
    """
    store = get_event_store()
    stats = store.get_stats(hours)
    
    return {
        "status": "ok",
        "stats": stats.dict(),
    }


@router.get("/events/recent")
async def get_recent_events(
    limit: int = 50,
):
    """
    Get recent events (admin endpoint).
    
    TODO: Add admin authentication
    """
    store = get_event_store()
    events = store.get_recent_events(limit)
    
    return {
        "status": "ok",
        "count": len(events),
        "events": events,
    }


@router.get("/health")
async def meta_health():
    """Health check for Meta events system."""
    store = get_event_store()
    
    return {
        "status": "healthy",
        "meta_available": META_AVAILABLE,
        "events_stored": len(store.events),
        "unique_sessions": len(store.sessions),
    }


# ═══════════════════════════════════════════════════════════════════════════
# BEACON SUPPORT
# ═══════════════════════════════════════════════════════════════════════════

# sendBeacon sends data as text/plain, so we need to handle that
@router.post("/events", include_in_schema=False)
async def receive_beacon_event(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle sendBeacon requests which may have different content types.
    """
    content_type = request.headers.get('content-type', '')
    
    try:
        if 'application/json' in content_type:
            body = await request.json()
        else:
            # sendBeacon may send as text/plain
            raw_body = await request.body()
            body = json.loads(raw_body)
        
        event = MetaEventData(**body)
        
        # Add to store and forward
        store = get_event_store()
        store.add_event(event)
        background_tasks.add_task(forward_to_meta, event)
        
        return {"status": "accepted"}
        
    except Exception as e:
        logger.error(f"Failed to parse beacon event: {e}")
        raise HTTPException(status_code=400, detail="Invalid event data")


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

def init_meta_events(app):
    """Initialize Meta events routes on FastAPI app."""
    app.include_router(router)
    logger.info("Meta events API initialized")


if __name__ == "__main__":
    # Test the module
    print("Meta Events API module loaded")
    print(f"META_AVAILABLE: {META_AVAILABLE}")
