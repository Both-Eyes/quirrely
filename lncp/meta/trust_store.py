#!/usr/bin/env python3
"""
LNCP META: TRUST STORE v4.2
Tracks trust scores for action types using weighted decay model.

Trust is earned through successful outcomes:
- Recent outcomes matter more than old ones
- Failures have higher impact than successes
- Trust accumulates to enable lane promotion

Formula:
  trust_score = Σ(outcome_value × recency_weight)
  recency_weight = 0.95^days_ago
  outcome_value = +1 (success), +0.5 (partial), -2 (failure), -5 (rollback)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


# ═══════════════════════════════════════════════════════════════════════════
# TRUST LEVELS
# ═══════════════════════════════════════════════════════════════════════════

class TrustLevel(str, Enum):
    """Trust level for an action type."""
    UNTRUSTED = "untrusted"       # No history, requires super admin
    LOW = "low"                   # Some history, requires review
    MEDIUM = "medium"             # Good history, can be reviewed quickly
    HIGH = "high"                 # Strong history, candidate for auto
    TRUSTED = "trusted"           # Earned auto-apply privileges


# ═══════════════════════════════════════════════════════════════════════════
# TRUST EVENT
# ═══════════════════════════════════════════════════════════════════════════

class OutcomeType(str, Enum):
    """Type of outcome that affects trust."""
    SUCCESS = "success"           # Action achieved predicted outcome
    PARTIAL = "partial"           # Some improvement
    NEUTRAL = "neutral"           # No change
    FAILURE = "failure"           # Negative outcome
    ROLLBACK = "rollback"         # Had to revert


# Outcome values for trust calculation
OUTCOME_VALUES: Dict[OutcomeType, float] = {
    OutcomeType.SUCCESS: 1.0,
    OutcomeType.PARTIAL: 0.5,
    OutcomeType.NEUTRAL: 0.0,
    OutcomeType.FAILURE: -2.0,
    OutcomeType.ROLLBACK: -5.0,
}


@dataclass
class TrustEvent:
    """A single event that affects trust."""
    action_type: str
    outcome: OutcomeType
    timestamp: datetime
    action_id: Optional[str] = None
    notes: str = ""
    
    @property
    def value(self) -> float:
        return OUTCOME_VALUES.get(self.outcome, 0.0)


# ═══════════════════════════════════════════════════════════════════════════
# TRUST SCORE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TrustScore:
    """Trust score for an action type."""
    action_type: str
    
    # Current score
    score: float = 0.0
    level: TrustLevel = TrustLevel.UNTRUSTED
    
    # Statistics
    total_events: int = 0
    successes: int = 0
    failures: int = 0
    rollbacks: int = 0
    
    # Timing
    first_event: Optional[datetime] = None
    last_event: Optional[datetime] = None
    
    # Lane status
    current_lane: str = "super_admin"
    eligible_for_promotion: bool = False
    promotion_blocked_until: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "action_type": self.action_type,
            "score": round(self.score, 2),
            "level": self.level.value,
            "total_events": self.total_events,
            "successes": self.successes,
            "failures": self.failures,
            "rollbacks": self.rollbacks,
            "current_lane": self.current_lane,
            "eligible_for_promotion": self.eligible_for_promotion,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TRUST STORE
# ═══════════════════════════════════════════════════════════════════════════

class TrustStore:
    """
    Manages trust scores for all action types.
    
    Trust is calculated using weighted decay:
    - Recent events have more weight
    - Failures and rollbacks have outsized negative impact
    - Trust thresholds determine lane eligibility
    """
    
    # Decay rate (0.95 = 5% decay per day)
    DECAY_RATE = 0.95
    
    # Trust thresholds
    THRESHOLDS = {
        TrustLevel.UNTRUSTED: float('-inf'),
        TrustLevel.LOW: 0,
        TrustLevel.MEDIUM: 5,
        TrustLevel.HIGH: 10,
        TrustLevel.TRUSTED: 15,
    }
    
    # Lane thresholds
    LANE_THRESHOLDS = {
        "super_admin": float('-inf'),
        "review": 3,
        "auto": 15,
    }
    
    # Cooldown after failure
    FAILURE_COOLDOWN_DAYS = 7
    ROLLBACK_COOLDOWN_DAYS = 14
    
    def __init__(self):
        self.scores: Dict[str, TrustScore] = {}
        self.events: List[TrustEvent] = []
        
        # Override settings
        self.overrides: Dict[str, Dict] = {}  # action_type -> override config
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT RECORDING
    # ─────────────────────────────────────────────────────────────────────
    
    def record_outcome(
        self,
        action_type: str,
        outcome: OutcomeType,
        action_id: Optional[str] = None,
        notes: str = "",
    ) -> TrustScore:
        """
        Record an outcome for an action type.
        
        This is the primary way trust changes.
        """
        event = TrustEvent(
            action_type=action_type,
            outcome=outcome,
            timestamp=datetime.utcnow(),
            action_id=action_id,
            notes=notes,
        )
        self.events.append(event)
        
        # Ensure score exists
        if action_type not in self.scores:
            self.scores[action_type] = TrustScore(action_type=action_type)
        
        score = self.scores[action_type]
        
        # Update statistics
        score.total_events += 1
        if outcome == OutcomeType.SUCCESS:
            score.successes += 1
        elif outcome == OutcomeType.FAILURE:
            score.failures += 1
        elif outcome == OutcomeType.ROLLBACK:
            score.rollbacks += 1
        
        # Update timing
        if score.first_event is None:
            score.first_event = event.timestamp
        score.last_event = event.timestamp
        
        # Handle cooldowns for failures
        if outcome == OutcomeType.FAILURE:
            score.promotion_blocked_until = (
                datetime.utcnow() + timedelta(days=self.FAILURE_COOLDOWN_DAYS)
            )
        elif outcome == OutcomeType.ROLLBACK:
            score.promotion_blocked_until = (
                datetime.utcnow() + timedelta(days=self.ROLLBACK_COOLDOWN_DAYS)
            )
        
        # Recalculate score
        self._recalculate_score(action_type)
        
        return score
    
    # ─────────────────────────────────────────────────────────────────────
    # SCORE CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _recalculate_score(self, action_type: str):
        """Recalculate trust score using weighted decay."""
        if action_type not in self.scores:
            return
        
        score = self.scores[action_type]
        now = datetime.utcnow()
        
        # Get all events for this action type
        events = [e for e in self.events if e.action_type == action_type]
        
        # Calculate weighted sum
        weighted_sum = 0.0
        for event in events:
            days_ago = (now - event.timestamp).total_seconds() / 86400
            recency_weight = math.pow(self.DECAY_RATE, days_ago)
            weighted_sum += event.value * recency_weight
        
        score.score = weighted_sum
        
        # Determine level
        score.level = self._score_to_level(weighted_sum)
        
        # Check promotion eligibility
        score.eligible_for_promotion = self._check_promotion_eligibility(score)
    
    def _score_to_level(self, score: float) -> TrustLevel:
        """Convert numeric score to trust level."""
        if score >= self.THRESHOLDS[TrustLevel.TRUSTED]:
            return TrustLevel.TRUSTED
        elif score >= self.THRESHOLDS[TrustLevel.HIGH]:
            return TrustLevel.HIGH
        elif score >= self.THRESHOLDS[TrustLevel.MEDIUM]:
            return TrustLevel.MEDIUM
        elif score >= self.THRESHOLDS[TrustLevel.LOW]:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    def _check_promotion_eligibility(self, score: TrustScore) -> bool:
        """Check if action type is eligible for lane promotion."""
        # Check cooldown
        if score.promotion_blocked_until:
            if datetime.utcnow() < score.promotion_blocked_until:
                return False
        
        # Check minimum events
        if score.total_events < 5:
            return False
        
        # Check score threshold for next lane
        current_lane = score.current_lane
        if current_lane == "super_admin":
            return score.score >= self.LANE_THRESHOLDS["review"]
        elif current_lane == "review":
            return score.score >= self.LANE_THRESHOLDS["auto"]
        else:
            return False  # Already at auto
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_score(self, action_type: str) -> Optional[TrustScore]:
        """Get trust score for an action type."""
        return self.scores.get(action_type)
    
    def get_lane_for_action(self, action_type: str) -> str:
        """Get the appropriate lane for an action type based on trust."""
        # Check for override
        if action_type in self.overrides:
            override = self.overrides[action_type]
            if "lane" in override:
                return override["lane"]
        
        # Get score
        score = self.scores.get(action_type)
        if not score:
            return "super_admin"  # Unknown = untrusted
        
        # Return current lane (which may have been promoted)
        return score.current_lane
    
    def get_all_scores(self) -> List[TrustScore]:
        """Get all trust scores."""
        return list(self.scores.values())
    
    def get_promotion_candidates(self) -> List[TrustScore]:
        """Get action types eligible for promotion."""
        return [s for s in self.scores.values() if s.eligible_for_promotion]
    
    def get_recent_events(self, days: int = 7) -> List[TrustEvent]:
        """Get recent trust events."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [e for e in self.events if e.timestamp >= cutoff]
    
    # ─────────────────────────────────────────────────────────────────────
    # LANE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def promote(self, action_type: str, to_lane: str, reason: str = "") -> bool:
        """Promote an action type to a higher-trust lane."""
        if action_type not in self.scores:
            return False
        
        score = self.scores[action_type]
        
        # Validate promotion path
        valid_promotions = {
            "super_admin": ["review"],
            "review": ["auto"],
            "auto": [],
        }
        
        if to_lane not in valid_promotions.get(score.current_lane, []):
            return False
        
        score.current_lane = to_lane
        return True
    
    def demote(self, action_type: str, to_lane: str, reason: str = "") -> bool:
        """Demote an action type to a lower-trust lane."""
        if action_type not in self.scores:
            return False
        
        score = self.scores[action_type]
        
        # Validate demotion path
        valid_demotions = {
            "auto": ["review", "super_admin"],
            "review": ["super_admin"],
            "super_admin": [],
        }
        
        if to_lane not in valid_demotions.get(score.current_lane, []):
            return False
        
        score.current_lane = to_lane
        return True
    
    def set_override(
        self,
        action_type: str,
        lane: Optional[str] = None,
        trust_multiplier: Optional[float] = None,
        blocked: bool = False,
    ):
        """Set a manual override for an action type."""
        self.overrides[action_type] = {
            "lane": lane,
            "trust_multiplier": trust_multiplier,
            "blocked": blocked,
            "set_at": datetime.utcnow(),
        }
    
    def clear_override(self, action_type: str):
        """Clear override for an action type."""
        if action_type in self.overrides:
            del self.overrides[action_type]
    
    # ─────────────────────────────────────────────────────────────────────
    # REPORTING
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get summary of trust status."""
        scores = list(self.scores.values())
        
        by_level = {level.value: 0 for level in TrustLevel}
        for s in scores:
            by_level[s.level.value] += 1
        
        by_lane = {"super_admin": 0, "review": 0, "auto": 0}
        for s in scores:
            by_lane[s.current_lane] += 1
        
        return {
            "total_action_types": len(scores),
            "total_events": len(self.events),
            "by_level": by_level,
            "by_lane": by_lane,
            "promotion_candidates": len(self.get_promotion_candidates()),
            "overrides": len(self.overrides),
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[TrustScore]:
        """Get top trusted action types."""
        return sorted(
            self.scores.values(),
            key=lambda s: s.score,
            reverse=True
        )[:limit]


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_trust_store: Optional[TrustStore] = None

def get_trust_store() -> TrustStore:
    """Get the global trust store instance."""
    global _trust_store
    if _trust_store is None:
        _trust_store = TrustStore()
    return _trust_store


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "TrustLevel",
    "OutcomeType",
    "OUTCOME_VALUES",
    "TrustEvent",
    "TrustScore",
    "TrustStore",
    "get_trust_store",
]
