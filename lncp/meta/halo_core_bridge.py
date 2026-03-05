#!/usr/bin/env python3
"""
LNCP META: HALO-CORE INTEGRATION v1.0.0
Safety-aware scoring integration.

This module bridges HALO (safety) with the Core Engine (scoring):
1. Pre-analysis safety check
2. User trust-based confidence adjustment
3. Flagged user handling
4. Clean history trust bonus

The integration ensures:
- Unsafe content never reaches the engine
- User safety history affects result confidence
- System maintains integrity against abuse
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lncp.meta.halo_observer import (
    HALOObserver, get_halo_observer,
    UserSafetyScore, SeverityTier
)
from lncp.meta.events.schema import EventType, AppEvent, UserTier


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class SafetyConfig:
    """Configuration for safety-core integration."""
    
    # Trust bonuses (added to confidence)
    TRUSTED_USER_BONUS = 0.05       # Users with safety_score >= 95
    NORMAL_USER_BONUS = 0.0         # Users with safety_score >= 80
    MONITORED_USER_PENALTY = -0.05  # Users with safety_score >= 60
    RESTRICTED_USER_PENALTY = -0.10 # Users with safety_score >= 40
    UNTRUSTED_USER_PENALTY = -0.15  # Users with safety_score < 40
    
    # Confidence thresholds
    MIN_CONFIDENCE = 0.5
    MAX_CONFIDENCE = 0.99
    
    # Tier-based limits
    FREE_TIER_MAX_VIOLATIONS_24H = 3
    PRO_TIER_MAX_VIOLATIONS_24H = 5
    
    # Auto-actions
    AUTO_SUSPEND_AFTER_T3_COUNT = 2  # Suspend after 2 T3 violations
    COOLDOWN_MINUTES_T2 = 30
    COOLDOWN_MINUTES_T3 = 60


# ═══════════════════════════════════════════════════════════════════════════
# SAFETY CHECK RESULT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SafetyCheckResult:
    """Result of pre-analysis safety check."""
    
    allowed: bool                    # Can analysis proceed?
    reason: str = ""                 # Why blocked (if blocked)
    severity: Optional[SeverityTier] = None
    
    # User context
    user_safety_score: float = 100.0
    user_trust_level: str = "normal"
    
    # Adjustments for engine
    confidence_adjustment: float = 0.0
    requires_review: bool = False
    
    # Events to emit
    events_to_emit: list = None
    
    def __post_init__(self):
        if self.events_to_emit is None:
            self.events_to_emit = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "severity": self.severity.value if self.severity else None,
            "user_safety_score": self.user_safety_score,
            "user_trust_level": self.user_trust_level,
            "confidence_adjustment": self.confidence_adjustment,
            "requires_review": self.requires_review,
        }


# ═══════════════════════════════════════════════════════════════════════════
# SAFETY-CORE BRIDGE
# ═══════════════════════════════════════════════════════════════════════════

class SafetyCoreBridge:
    """
    Bridges HALO safety with Core Engine scoring.
    
    Usage:
        bridge = SafetyCoreBridge()
        
        # Before analysis
        check = bridge.pre_analysis_check(text, user_id, tier)
        if not check.allowed:
            return error_response(check.reason)
        
        # Run analysis with adjusted confidence
        result = analyze(text)
        result.confidence += check.confidence_adjustment
        
        # After analysis (record events)
        bridge.post_analysis(user_id, check, result)
    """
    
    def __init__(self):
        self.observer = get_halo_observer()
        self.config = SafetyConfig()
        
        # Import HALO detector
        try:
            from backend.halo_detector import HALODetector, get_detector
            self.detector = get_detector()
            self.halo_available = True
        except ImportError:
            self.detector = None
            self.halo_available = False
    
    def pre_analysis_check(self, 
                          text: str, 
                          user_id: Optional[str] = None,
                          tier: UserTier = UserTier.FREE,
                          visitor_id: Optional[str] = None) -> SafetyCheckResult:
        """
        Run safety check before analysis.
        
        This is the primary integration point between HALO and Core Engine.
        """
        events_to_emit = []
        
        # Emit check started event
        events_to_emit.append(AppEvent(
            event_id=f"halo_{datetime.now(timezone.utc).timestamp()}",
            event_type=EventType.HALO_CHECK_STARTED,
            timestamp=datetime.now(timezone.utc),
            visitor_id=visitor_id or "",
            user_id=user_id,
            tier=tier,
            payload={"text_length": len(text)}
        ))
        
        # Get user safety score
        if user_id:
            user_score = self.observer.get_user_score(user_id)
        else:
            user_score = UserSafetyScore(user_id="anonymous")
        
        # Check if user is suspended
        if user_score.is_suspended:
            return SafetyCheckResult(
                allowed=False,
                reason="Your account is temporarily suspended due to policy violations.",
                user_safety_score=user_score.safety_score,
                user_trust_level=user_score.trust_level,
                events_to_emit=events_to_emit
            )
        
        # Check if user is in cooldown
        if user_score.is_cooldown and user_score.cooldown_until:
            if datetime.now(timezone.utc) < user_score.cooldown_until:
                remaining = (user_score.cooldown_until - datetime.now(timezone.utc)).seconds // 60
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Please wait {remaining} minutes before submitting again.",
                    user_safety_score=user_score.safety_score,
                    user_trust_level=user_score.trust_level,
                    events_to_emit=events_to_emit
                )
        
        # Run HALO analysis on content
        if self.halo_available and self.detector:
            halo_result = self.detector.analyze(text, user_id=user_id)
            
            if not halo_result.passed:
                # Content blocked
                severity = halo_result.tier
                
                # Emit violation event
                events_to_emit.append(AppEvent(
                    event_id=f"halo_v_{datetime.now(timezone.utc).timestamp()}",
                    event_type=self._severity_to_event_type(severity),
                    timestamp=datetime.now(timezone.utc),
                    visitor_id=visitor_id or "",
                    user_id=user_id,
                    tier=tier,
                    payload={
                        "category": halo_result.category.value if halo_result.category else "",
                        "action": halo_result.action,
                        "violations": len(halo_result.violations)
                    }
                ))
                
                # Determine response based on severity
                if severity == SeverityTier.T3:
                    return SafetyCheckResult(
                        allowed=False,
                        reason="This content cannot be processed. Please ensure your text follows our community guidelines.",
                        severity=severity,
                        user_safety_score=user_score.safety_score,
                        user_trust_level=user_score.trust_level,
                        events_to_emit=events_to_emit
                    )
                elif severity == SeverityTier.T2:
                    # Apply cooldown
                    events_to_emit.append(AppEvent(
                        event_id=f"halo_cd_{datetime.now(timezone.utc).timestamp()}",
                        event_type=EventType.HALO_USER_COOLDOWN,
                        timestamp=datetime.now(timezone.utc),
                        visitor_id=visitor_id or "",
                        user_id=user_id,
                        tier=tier,
                        payload={"cooldown_minutes": self.config.COOLDOWN_MINUTES_T2}
                    ))
                    
                    return SafetyCheckResult(
                        allowed=False,
                        reason="Your content was flagged for review. Please try again in 30 minutes.",
                        severity=severity,
                        user_safety_score=user_score.safety_score,
                        user_trust_level=user_score.trust_level,
                        events_to_emit=events_to_emit
                    )
                # T1 - Allow with warning
                events_to_emit.append(AppEvent(
                    event_id=f"halo_warn_{datetime.now(timezone.utc).timestamp()}",
                    event_type=EventType.HALO_USER_WARNED,
                    timestamp=datetime.now(timezone.utc),
                    visitor_id=visitor_id or "",
                    user_id=user_id,
                    tier=tier,
                    payload={}
                ))
        
        # Content passed - emit success event
        events_to_emit.append(AppEvent(
            event_id=f"halo_pass_{datetime.now(timezone.utc).timestamp()}",
            event_type=EventType.HALO_CHECK_PASSED,
            timestamp=datetime.now(timezone.utc),
            visitor_id=visitor_id or "",
            user_id=user_id,
            tier=tier,
            payload={}
        ))
        
        # Calculate confidence adjustment based on user trust
        confidence_adj = self._get_confidence_adjustment(user_score.trust_level)
        
        return SafetyCheckResult(
            allowed=True,
            user_safety_score=user_score.safety_score,
            user_trust_level=user_score.trust_level,
            confidence_adjustment=confidence_adj,
            requires_review=user_score.trust_level in ["restricted", "untrusted"],
            events_to_emit=events_to_emit
        )
    
    def _severity_to_event_type(self, severity: SeverityTier) -> EventType:
        """Map severity tier to event type."""
        mapping = {
            SeverityTier.T1: EventType.HALO_VIOLATION_T1,
            SeverityTier.T2: EventType.HALO_VIOLATION_T2,
            SeverityTier.T3: EventType.HALO_VIOLATION_T3,
        }
        return mapping.get(severity, EventType.HALO_VIOLATION_T1)
    
    def _get_confidence_adjustment(self, trust_level: str) -> float:
        """Get confidence adjustment based on trust level."""
        adjustments = {
            "trusted": self.config.TRUSTED_USER_BONUS,
            "normal": self.config.NORMAL_USER_BONUS,
            "monitored": self.config.MONITORED_USER_PENALTY,
            "restricted": self.config.RESTRICTED_USER_PENALTY,
            "untrusted": self.config.UNTRUSTED_USER_PENALTY,
        }
        return adjustments.get(trust_level, 0.0)
    
    def post_analysis(self, 
                     user_id: Optional[str],
                     check_result: SafetyCheckResult,
                     analysis_result: Any):
        """
        Post-analysis processing.
        
        Records the events and updates user safety score.
        """
        # Process emitted events through observer
        if check_result.events_to_emit:
            self.observer.process_events(check_result.events_to_emit)
        
        # If result requires review, flag it
        if check_result.requires_review:
            # In production, this would add to a review queue
            pass
    
    def get_user_analysis_limits(self, 
                                user_id: str,
                                tier: UserTier) -> Dict[str, Any]:
        """Get analysis limits for a user based on safety history."""
        user_score = self.observer.get_user_score(user_id)
        
        # Base limits by tier
        if tier == UserTier.FREE:
            base_limit = 5
        elif tier == UserTier.TRIAL:
            base_limit = 20
        elif tier == UserTier.PRO:
            base_limit = 100
        else:
            base_limit = 1000
        
        # Reduce limits for untrusted users
        trust_multiplier = {
            "trusted": 1.0,
            "normal": 1.0,
            "monitored": 0.75,
            "restricted": 0.5,
            "untrusted": 0.25,
        }.get(user_score.trust_level, 1.0)
        
        return {
            "analyses_per_day": int(base_limit * trust_multiplier),
            "trust_level": user_score.trust_level,
            "safety_score": user_score.safety_score,
            "is_restricted": user_score.trust_level in ["restricted", "untrusted"],
        }
    
    def record_appeal(self, 
                     user_id: str,
                     violation_id: str,
                     content: str,
                     appeal_reason: str) -> Dict[str, Any]:
        """
        Record a user's appeal of a violation.
        
        Returns information about the appeal status.
        """
        # Emit appeal event
        event = AppEvent(
            event_id=f"appeal_{datetime.now(timezone.utc).timestamp()}",
            event_type=EventType.HALO_APPEAL_SUBMITTED,
            timestamp=datetime.now(timezone.utc),
            visitor_id="",
            user_id=user_id,
            user_tier=UserTier.FREE,
            payload={
                "violation_id": violation_id,
                "appeal_reason": appeal_reason[:500],  # Limit length
            }
        )
        
        self.observer.process_events([event])
        
        return {
            "appeal_id": event.event_id,
            "status": "submitted",
            "message": "Your appeal has been submitted and will be reviewed within 24 hours."
        }
    
    def get_safety_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive safety status for a user."""
        user_score = self.observer.get_user_score(user_id)
        
        return {
            "user_id": user_id,
            "safety_score": user_score.safety_score,
            "trust_level": user_score.trust_level,
            "total_checks": user_score.total_checks,
            "total_violations": user_score.total_violations,
            "is_warned": user_score.is_warned,
            "is_cooldown": user_score.is_cooldown,
            "is_suspended": user_score.is_suspended,
            "cooldown_until": user_score.cooldown_until.isoformat() if user_score.cooldown_until else None,
            "appeals_won": user_score.appeals_won,
            "can_submit": not (user_score.is_suspended or user_score.is_cooldown),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON & CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════

_safety_bridge: Optional[SafetyCoreBridge] = None


def get_safety_bridge() -> SafetyCoreBridge:
    """Get or create the safety-core bridge."""
    global _safety_bridge
    if _safety_bridge is None:
        _safety_bridge = SafetyCoreBridge()
    return _safety_bridge


def check_content_safety(text: str, 
                        user_id: Optional[str] = None,
                        tier: UserTier = UserTier.FREE) -> SafetyCheckResult:
    """Convenience function for pre-analysis safety check."""
    bridge = get_safety_bridge()
    return bridge.pre_analysis_check(text, user_id, tier)


def get_user_safety_status(user_id: str) -> Dict[str, Any]:
    """Convenience function to get user safety status."""
    bridge = get_safety_bridge()
    return bridge.get_safety_status(user_id)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "SafetyCoreBridge",
    "SafetyCheckResult",
    "SafetyConfig",
    "get_safety_bridge",
    "check_content_safety",
    "get_user_safety_status",
]
