#!/usr/bin/env python3
"""
QUIRRELY HALO BRIDGE v1.0
Connects voice analysis and user behavior to HALO observation system.

HALO (Holistic Analysis and Learning Observer) uses this data to:
- Improve voice analysis accuracy over time
- Predict user engagement patterns
- Personalize content recommendations
- Track authority progression

This bridge forwards events to the Meta orchestration layer.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class HALOEventType(str, Enum):
    """Types of events HALO observes."""
    # Voice Analysis
    VOICE_ANALYSIS_STARTED = "voice.analysis.started"
    VOICE_ANALYSIS_COMPLETED = "voice.analysis.completed"
    VOICE_ANALYSIS_FAILED = "voice.analysis.failed"
    VOICE_PROFILE_VIEWED = "voice.profile.viewed"
    VOICE_EVOLUTION_VIEWED = "voice.evolution.viewed"
    
    # User Engagement
    USER_SESSION_STARTED = "user.session.started"
    USER_SESSION_ENDED = "user.session.ended"
    USER_FEATURE_USED = "user.feature.used"
    USER_PAGE_VIEWED = "user.page.viewed"
    
    # Writing Activity
    WRITING_STARTED = "writing.started"
    WRITING_COMPLETED = "writing.completed"
    WRITING_PUBLISHED = "writing.published"
    
    # Reading Activity
    READING_STARTED = "reading.started"
    READING_COMPLETED = "reading.completed"
    READING_PATH_FOLLOWED = "reading.path.followed"
    
    # Authority Progression
    AUTHORITY_MILESTONE_REACHED = "authority.milestone.reached"
    AUTHORITY_SCORE_CHANGED = "authority.score.changed"
    
    # Conversions
    TRIAL_STARTED = "conversion.trial.started"
    SUBSCRIPTION_CREATED = "conversion.subscription.created"
    ADDON_PURCHASED = "conversion.addon.purchased"


# ═══════════════════════════════════════════════════════════════════════════
# HALO EVENT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class HALOEvent:
    """Event structure for HALO observation."""
    event_type: HALOEventType
    user_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    
    # Event-specific data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    tier: Optional[str] = None
    country: Optional[str] = None
    device: Optional[str] = None
    
    # Analysis metadata
    confidence: Optional[float] = None
    source: str = "api"  # 'api', 'frontend', 'system'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission."""
        return {
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "data": self.data,
            "tier": self.tier,
            "country": self.country,
            "device": self.device,
            "confidence": self.confidence,
            "source": self.source,
        }


# ═══════════════════════════════════════════════════════════════════════════
# HALO BRIDGE
# ═══════════════════════════════════════════════════════════════════════════

class HALOBridge:
    """
    Bridge to HALO observation system.
    
    Collects events and forwards them to Meta for analysis.
    Falls back to local storage if Meta is unavailable.
    """
    
    def __init__(self):
        self._meta_available = False
        self._halo_observer = None
        self._event_queue: List[HALOEvent] = []
        self._max_queue_size = 1000
        self._init_meta()
    
    def _init_meta(self):
        """Initialize Meta HALO connection."""
        try:
            from lncp.meta.halo_observer import get_halo_observer
            self._halo_observer = get_halo_observer()
            self._meta_available = True
            logger.info("HALO observer connected")
        except ImportError:
            logger.warning("HALO observer not available, using local queue")
        except Exception as e:
            logger.error(f"Failed to init HALO: {e}")
    
    async def observe(self, event: HALOEvent) -> bool:
        """
        Send an event to HALO.
        
        Returns True if successfully forwarded to Meta.
        """
        if self._meta_available and self._halo_observer:
            try:
                await self._halo_observer.observe(
                    event_type=event.event_type.value,
                    user_id=event.user_id,
                    data=event.data,
                    timestamp=event.timestamp,
                    session_id=event.session_id,
                )
                logger.debug(f"HALO event sent: {event.event_type.value}")
                return True
            except Exception as e:
                logger.error(f"Failed to send HALO event: {e}")
        
        # Queue for later
        self._queue_event(event)
        return False
    
    def _queue_event(self, event: HALOEvent):
        """Queue event for later processing."""
        self._event_queue.append(event)
        
        # Trim queue if too large
        while len(self._event_queue) > self._max_queue_size:
            self._event_queue.pop(0)
    
    async def flush_queue(self) -> int:
        """Flush queued events to Meta."""
        if not self._meta_available or not self._event_queue:
            return 0
        
        sent = 0
        for event in self._event_queue[:]:
            try:
                await self._halo_observer.observe(
                    event_type=event.event_type.value,
                    user_id=event.user_id,
                    data=event.data,
                    timestamp=event.timestamp,
                    session_id=event.session_id,
                )
                self._event_queue.remove(event)
                sent += 1
            except Exception:
                break
        
        return sent
    
    # ─────────────────────────────────────────────────────────────────────────
    # Voice Analysis Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_voice_analysis_started(
        self,
        user_id: str,
        word_count: int,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record start of voice analysis."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.VOICE_ANALYSIS_STARTED,
            user_id=user_id,
            session_id=session_id,
            data={
                "word_count": word_count,
                **kwargs,
            },
        ))
    
    async def observe_voice_analysis_completed(
        self,
        user_id: str,
        profile_type: str,
        confidence: float,
        tokens: List[str],
        word_count: int,
        analysis_duration_ms: int,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record completed voice analysis."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.VOICE_ANALYSIS_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            confidence=confidence,
            data={
                "profile_type": profile_type,
                "confidence": confidence,
                "tokens": tokens,
                "word_count": word_count,
                "analysis_duration_ms": analysis_duration_ms,
                **kwargs,
            },
        ))
    
    async def observe_voice_analysis_failed(
        self,
        user_id: str,
        error: str,
        word_count: int,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record failed voice analysis."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.VOICE_ANALYSIS_FAILED,
            user_id=user_id,
            session_id=session_id,
            data={
                "error": error,
                "word_count": word_count,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # User Engagement Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_session_started(
        self,
        user_id: str,
        session_id: str,
        tier: Optional[str] = None,
        country: Optional[str] = None,
        device: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record session start."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.USER_SESSION_STARTED,
            user_id=user_id,
            session_id=session_id,
            tier=tier,
            country=country,
            device=device,
            data=kwargs,
        ))
    
    async def observe_session_ended(
        self,
        user_id: str,
        session_id: str,
        duration_seconds: int,
        pages_viewed: int,
        features_used: List[str],
        **kwargs,
    ) -> bool:
        """Record session end."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.USER_SESSION_ENDED,
            user_id=user_id,
            session_id=session_id,
            data={
                "duration_seconds": duration_seconds,
                "pages_viewed": pages_viewed,
                "features_used": features_used,
                **kwargs,
            },
        ))
    
    async def observe_feature_used(
        self,
        user_id: str,
        feature: str,
        duration_ms: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record feature usage."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.USER_FEATURE_USED,
            user_id=user_id,
            session_id=session_id,
            data={
                "feature": feature,
                "duration_ms": duration_ms,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Writing Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_writing_completed(
        self,
        user_id: str,
        word_count: int,
        duration_minutes: int,
        profile_type: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record completed writing session."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.WRITING_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            data={
                "word_count": word_count,
                "duration_minutes": duration_minutes,
                "profile_type": profile_type,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Reading Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_reading_completed(
        self,
        user_id: str,
        post_id: str,
        read_time_seconds: int,
        scroll_depth: float,
        is_deep_read: bool,
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record completed reading."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.READING_COMPLETED,
            user_id=user_id,
            session_id=session_id,
            data={
                "post_id": post_id,
                "read_time_seconds": read_time_seconds,
                "scroll_depth": scroll_depth,
                "is_deep_read": is_deep_read,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Authority Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_authority_milestone(
        self,
        user_id: str,
        milestone: str,
        new_score: float,
        previous_score: float,
        **kwargs,
    ) -> bool:
        """Record authority milestone reached."""
        return await self.observe(HALOEvent(
            event_type=HALOEventType.AUTHORITY_MILESTONE_REACHED,
            user_id=user_id,
            data={
                "milestone": milestone,
                "new_score": new_score,
                "previous_score": previous_score,
                "score_change": new_score - previous_score,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Conversion Events
    # ─────────────────────────────────────────────────────────────────────────
    
    async def observe_conversion(
        self,
        user_id: str,
        conversion_type: str,  # 'trial', 'subscription', 'addon'
        details: Dict[str, Any],
        session_id: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Record conversion event."""
        event_type = {
            'trial': HALOEventType.TRIAL_STARTED,
            'subscription': HALOEventType.SUBSCRIPTION_CREATED,
            'addon': HALOEventType.ADDON_PURCHASED,
        }.get(conversion_type, HALOEventType.SUBSCRIPTION_CREATED)
        
        return await self.observe(HALOEvent(
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            data={
                "conversion_type": conversion_type,
                **details,
                **kwargs,
            },
        ))
    
    # ─────────────────────────────────────────────────────────────────────────
    # Stats
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            "meta_available": self._meta_available,
            "queue_size": len(self._event_queue),
            "max_queue_size": self._max_queue_size,
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_halo_bridge: Optional[HALOBridge] = None


def get_halo_bridge() -> HALOBridge:
    """Get or create HALO bridge instance."""
    global _halo_bridge
    if _halo_bridge is None:
        _halo_bridge = HALOBridge()
    return _halo_bridge


# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

from fastapi import BackgroundTasks


async def track_voice_analysis(
    background_tasks: BackgroundTasks,
    user_id: str,
    profile_type: str,
    confidence: float,
    tokens: List[str],
    word_count: int,
    analysis_duration_ms: int,
    session_id: Optional[str] = None,
):
    """
    Helper to track voice analysis in background.
    
    Usage in endpoint:
        @router.post("/analyze")
        async def analyze(
            text: str,
            user: User = Depends(get_current_user),
            background_tasks: BackgroundTasks,
        ):
            result = voice_analyzer.analyze(text)
            
            await track_voice_analysis(
                background_tasks,
                user_id=user.id,
                profile_type=result.profile_type,
                confidence=result.confidence,
                tokens=result.tokens,
                word_count=len(text.split()),
                analysis_duration_ms=result.duration_ms,
            )
            
            return result
    """
    bridge = get_halo_bridge()
    background_tasks.add_task(
        bridge.observe_voice_analysis_completed,
        user_id=user_id,
        profile_type=profile_type,
        confidence=confidence,
        tokens=tokens,
        word_count=word_count,
        analysis_duration_ms=analysis_duration_ms,
        session_id=session_id,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("HALO Bridge module loaded")
    bridge = get_halo_bridge()
    print(f"Stats: {bridge.get_stats()}")
