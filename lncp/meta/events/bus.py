#!/usr/bin/env python3
"""
LNCP META: EVENT BUS v5.1
App-side event emitter for the file-based queue.

Usage (in app code):
    from lncp.meta.events import EventBus, EventType, UserTier
    
    bus = EventBus()
    
    # Simple event
    bus.emit(
        EventType.ANALYSIS_COMPLETED,
        visitor_id="v_123",
        user_id="u_456",
        tier=UserTier.PRO,
        payload={"text_length": 500, "profile_id": "assertive-open"}
    )
    
    # With session context
    bus.emit(
        EventType.PAGE_VIEWED,
        visitor_id="v_123",
        session_id="s_789",
        payload={"page": "/dashboard"}
    )
"""

import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .schema import AppEvent, EventType, UserTier, validate_event


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_EVENTS_DIR = os.environ.get("LNCP_EVENTS_DIR", "/var/lib/lncp/events")
FLUSH_INTERVAL_SECONDS = 5
MAX_BATCH_SIZE = 100
MAX_FILE_SIZE_MB = 10


# ═══════════════════════════════════════════════════════════════════════════
# EVENT BUS
# ═══════════════════════════════════════════════════════════════════════════

class EventBus:
    """
    File-based event bus for emitting events from app to Meta.
    
    Features:
    - Batched writes for performance
    - Automatic file rotation
    - Thread-safe
    - Graceful degradation on errors
    """
    
    def __init__(
        self,
        events_dir: str = DEFAULT_EVENTS_DIR,
        flush_interval: float = FLUSH_INTERVAL_SECONDS,
        max_batch_size: int = MAX_BATCH_SIZE,
    ):
        self.events_dir = events_dir
        self.flush_interval = flush_interval
        self.max_batch_size = max_batch_size
        
        # Ensure directory exists
        Path(events_dir).mkdir(parents=True, exist_ok=True)
        
        # Event buffer
        self._buffer: List[AppEvent] = []
        self._lock = threading.Lock()
        
        # Background flusher
        self._running = True
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        
        # Metrics
        self._events_emitted = 0
        self._events_flushed = 0
        self._errors = 0
    
    # ─────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────
    
    def emit(
        self,
        event_type: EventType,
        visitor_id: str,
        user_id: Optional[str] = None,
        tier: UserTier = UserTier.ANONYMOUS,
        session_id: str = "",
        payload: Optional[Dict[str, Any]] = None,
        source: str = "app",
    ) -> Optional[str]:
        """
        Emit an event.
        
        Returns event_id if successful, None if failed.
        """
        event = AppEvent(
            event_id=AppEvent.generate_id(),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            visitor_id=visitor_id,
            user_id=user_id,
            tier=tier,
            session_id=session_id,
            payload=payload or {},
            source=source,
        )
        
        # Validate
        errors = validate_event(event)
        if errors:
            self._errors += 1
            return None
        
        # Add to buffer
        with self._lock:
            self._buffer.append(event)
            self._events_emitted += 1
            
            # Flush if buffer full
            if len(self._buffer) >= self.max_batch_size:
                self._flush()
        
        return event.event_id
    
    def emit_raw(self, event: AppEvent) -> bool:
        """Emit a pre-constructed event."""
        errors = validate_event(event)
        if errors:
            self._errors += 1
            return False
        
        with self._lock:
            self._buffer.append(event)
            self._events_emitted += 1
            
            if len(self._buffer) >= self.max_batch_size:
                self._flush()
        
        return True
    
    def flush(self):
        """Force flush buffer to disk."""
        with self._lock:
            self._flush()
    
    def close(self):
        """Close the event bus, flushing remaining events."""
        self._running = False
        self.flush()
    
    # ─────────────────────────────────────────────────────────────────────
    # CONVENIENCE METHODS
    # ─────────────────────────────────────────────────────────────────────
    
    def onboarding_started(self, visitor_id: str, user_id: str, tier: UserTier = UserTier.FREE):
        """Emit onboarding started event."""
        return self.emit(EventType.ONBOARDING_STARTED, visitor_id, user_id, tier,
                        payload={"step": 1})
    
    def onboarding_step(self, visitor_id: str, user_id: str, step: int, 
                       step_name: str, duration_seconds: float, tier: UserTier = UserTier.FREE):
        """Emit onboarding step completed."""
        return self.emit(EventType.ONBOARDING_STEP_COMPLETED, visitor_id, user_id, tier,
                        payload={"step": step, "step_name": step_name, 
                                "duration_seconds": duration_seconds})
    
    def onboarding_completed(self, visitor_id: str, user_id: str, 
                            total_duration: float, tier: UserTier = UserTier.FREE):
        """Emit onboarding completed."""
        return self.emit(EventType.ONBOARDING_COMPLETED, visitor_id, user_id, tier,
                        payload={"total_duration_seconds": total_duration})
    
    def analysis_completed(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        text_length: int,
        token_count: int,
        profile_id: str,
        profile_name: str,
        confidence: float,
        duration_ms: int,
    ):
        """Emit analysis completed event."""
        return self.emit(
            EventType.ANALYSIS_COMPLETED, visitor_id, user_id, tier,
            payload={
                "text_length": text_length,
                "token_count": token_count,
                "profile_id": profile_id,
                "profile_name": profile_name,
                "confidence": confidence,
                "duration_ms": duration_ms,
            }
        )
    
    def profile_viewed(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        profile_id: str,
        profile_name: str,
        view_duration_seconds: float,
    ):
        """Emit profile viewed event."""
        return self.emit(
            EventType.PROFILE_VIEWED, visitor_id, user_id, tier,
            payload={
                "profile_id": profile_id,
                "profile_name": profile_name,
                "view_duration_seconds": view_duration_seconds,
            }
        )
    
    def profile_switched(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        from_profile_id: str,
        to_profile_id: str,
    ):
        """Emit profile switch event."""
        return self.emit(
            EventType.PROFILE_SWITCHED, visitor_id, user_id, tier,
            payload={
                "from_profile_id": from_profile_id,
                "to_profile_id": to_profile_id,
            }
        )
    
    def result_exported(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        profile_id: str,
        export_format: str,
    ):
        """Emit result exported event."""
        return self.emit(
            EventType.RESULT_EXPORTED, visitor_id, user_id, tier,
            payload={"profile_id": profile_id, "format": export_format}
        )
    
    def session_started(
        self,
        visitor_id: str,
        session_id: str,
        user_id: Optional[str] = None,
        tier: UserTier = UserTier.ANONYMOUS,
        referrer: Optional[str] = None,
        landing_page: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_term: Optional[str] = None,
        utm_content: Optional[str] = None,
    ):
        """Emit session started event with UTM attribution."""
        return self.emit(
            EventType.SESSION_STARTED, visitor_id, user_id, tier,
            session_id=session_id,
            payload={
                "referrer": referrer,
                "landing_page": landing_page,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
            }
        )
    
    def session_ended(
        self,
        visitor_id: str,
        session_id: str,
        duration_seconds: float,
        pages_viewed: int,
        actions_taken: int,
        user_id: Optional[str] = None,
        tier: UserTier = UserTier.ANONYMOUS,
    ):
        """Emit session ended event."""
        return self.emit(
            EventType.SESSION_ENDED, visitor_id, user_id, tier,
            session_id=session_id,
            payload={
                "duration_seconds": duration_seconds,
                "pages_viewed": pages_viewed,
                "actions_taken": actions_taken,
            }
        )
    
    def account_created(
        self,
        visitor_id: str,
        user_id: str,
        source: Optional[str] = None,
        referrer: Optional[str] = None,
    ):
        """Emit account created event."""
        return self.emit(
            EventType.ACCOUNT_CREATED, visitor_id, user_id, UserTier.FREE,
            payload={"source": source, "referrer": referrer}
        )
    
    def account_upgraded(
        self,
        visitor_id: str,
        user_id: str,
        from_tier: UserTier,
        to_tier: UserTier,
        plan: str,
    ):
        """Emit account upgraded event."""
        return self.emit(
            EventType.ACCOUNT_UPGRADED, visitor_id, user_id, to_tier,
            payload={"from_tier": from_tier.value, "to_tier": to_tier.value, "plan": plan}
        )
    
    def account_churned(
        self,
        visitor_id: str,
        user_id: str,
        tier: UserTier,
        lifetime_days: int,
        reason: Optional[str] = None,
    ):
        """Emit account churned event."""
        return self.emit(
            EventType.ACCOUNT_CHURNED, visitor_id, user_id, tier,
            payload={"lifetime_days": lifetime_days, "reason": reason}
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # FRICTION EVENTS (E5)
    # ─────────────────────────────────────────────────────────────────────
    
    def help_accessed(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        context: str,
        help_topic: Optional[str] = None,
    ):
        """Emit help accessed event - indicates user confusion/friction."""
        return self.emit(
            EventType.HELP_ACCESSED, visitor_id, user_id, tier,
            payload={"context": context, "help_topic": help_topic}
        )
    
    def support_contacted(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        context: str,
        action: Optional[str] = None,
    ):
        """Emit support contacted event - indicates significant friction."""
        return self.emit(
            EventType.SUPPORT_CONTACTED, visitor_id, user_id, tier,
            payload={"context": context, "action": action}
        )
    
    def error_encountered(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        context: str,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Emit error event - tracks system/user errors."""
        return self.emit(
            EventType.ERROR_ENCOUNTERED, visitor_id, user_id, tier,
            payload={
                "context": context,
                "error_code": error_code,
                "error_message": error_message,
            }
        )
    
    def flow_abandoned(
        self,
        visitor_id: str,
        user_id: Optional[str],
        tier: UserTier,
        flow_name: str,
        flow_step: int,
        context: str,
    ):
        """Emit flow abandonment - user quit mid-process."""
        return self.emit(
            EventType.FLOW_ABANDONED, visitor_id, user_id, tier,
            payload={
                "flow_name": flow_name,
                "flow_step": flow_step,
                "context": context,
            }
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────────────────────────────
    
    def _flush(self):
        """Flush buffer to disk. Must be called with lock held."""
        if not self._buffer:
            return
        
        try:
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"events_{timestamp}_{len(self._buffer)}.jsonl"
            filepath = os.path.join(self.events_dir, filename)
            
            # Write events as JSON lines
            with open(filepath, 'w') as f:
                for event in self._buffer:
                    f.write(event.to_json() + "\n")
            
            self._events_flushed += len(self._buffer)
            self._buffer.clear()
            
        except Exception as e:
            self._errors += 1
            # Don't clear buffer on error - will retry
    
    def _flush_loop(self):
        """Background thread that flushes periodically."""
        while self._running:
            time.sleep(self.flush_interval)
            with self._lock:
                self._flush()
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_metrics(self) -> Dict:
        """Get event bus metrics."""
        with self._lock:
            return {
                "events_emitted": self._events_emitted,
                "events_flushed": self._events_flushed,
                "events_pending": len(self._buffer),
                "errors": self._errors,
            }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "EventBus",
    "get_event_bus",
    "DEFAULT_EVENTS_DIR",
]
