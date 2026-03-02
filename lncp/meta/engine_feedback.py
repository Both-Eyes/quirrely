#!/usr/bin/env python3
"""
LNCP META: ENGINE FEEDBACK COLLECTOR v5.1
Collects implicit feedback signals about Engine accuracy.

Signals collected (implicit):
- Profile acceptance (user proceeds with predicted profile)
- Profile switch (user selects different profile)
- Result export/save (user values the result)
- Return usage (user analyzes more text)

These signals feed into:
- Engine accuracy tracking
- EngineParameterAnalyzer for proposals
- Health calculation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from .events import (
    EventType, AppEvent, EventCollector, EventAggregator,
    get_event_collector
)


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK TYPES
# ═══════════════════════════════════════════════════════════════════════════

class FeedbackSignal(str, Enum):
    """Types of implicit feedback signals."""
    PROFILE_ACCEPTED = "profile_accepted"     # Used predicted profile
    PROFILE_SWITCHED = "profile_switched"     # Changed to different profile
    RESULT_VALUED = "result_valued"           # Exported or saved
    USER_RETURNED = "user_returned"           # Came back for more
    LONG_ENGAGEMENT = "long_engagement"       # Spent time with result


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK RECORD
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EngineFeedback:
    """A single feedback record for an analysis."""
    
    # Identity
    feedback_id: str
    user_id: str
    analysis_timestamp: datetime
    
    # Analysis context
    text_length: int
    predicted_profile_id: str
    predicted_profile_name: str
    confidence: float
    
    # Signals observed
    signals: List[FeedbackSignal] = field(default_factory=list)
    
    # Derived
    final_profile_id: Optional[str] = None  # May differ from predicted
    profile_view_duration: float = 0
    was_exported: bool = False
    was_saved: bool = False
    
    # Inferred accuracy
    inferred_accuracy: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "predicted_profile": self.predicted_profile_id,
            "final_profile": self.final_profile_id,
            "signals": [s.value for s in self.signals],
            "confidence": self.confidence,
            "inferred_accuracy": self.inferred_accuracy,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE ACCURACY TRACKER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ProfileAccuracy:
    """Accuracy tracking for a specific profile."""
    profile_id: str
    profile_name: str
    
    # Counts
    times_predicted: int = 0
    times_accepted: int = 0
    times_switched_away: int = 0
    times_switched_to: int = 0
    
    # Value signals
    times_exported: int = 0
    times_saved: int = 0
    
    # Engagement
    total_view_duration: float = 0
    
    @property
    def acceptance_rate(self) -> float:
        if self.times_predicted == 0:
            return 0
        return self.times_accepted / self.times_predicted
    
    @property
    def switch_away_rate(self) -> float:
        if self.times_predicted == 0:
            return 0
        return self.times_switched_away / self.times_predicted
    
    @property
    def value_rate(self) -> float:
        """Rate at which users valued the result."""
        if self.times_accepted == 0:
            return 0
        return (self.times_exported + self.times_saved) / self.times_accepted
    
    @property
    def avg_view_duration(self) -> float:
        if self.times_predicted == 0:
            return 0
        return self.total_view_duration / self.times_predicted
    
    def to_dict(self) -> Dict:
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "times_predicted": self.times_predicted,
            "acceptance_rate": f"{self.acceptance_rate:.1%}",
            "switch_away_rate": f"{self.switch_away_rate:.1%}",
            "value_rate": f"{self.value_rate:.1%}",
            "avg_view_duration": f"{self.avg_view_duration:.1f}s",
        }


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE FEEDBACK COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class EngineFeedbackCollector:
    """
    Collects and analyzes feedback about Engine accuracy.
    
    Works by:
    1. Watching for analysis.completed events
    2. Tracking subsequent profile_viewed, profile_switched, result_exported events
    3. Inferring accuracy from behavior patterns
    4. Aggregating by profile for Engine parameter proposals
    """
    
    # Time window to associate events with an analysis
    ASSOCIATION_WINDOW_MINUTES = 30
    
    # Thresholds for accuracy inference
    ACCEPTANCE_THRESHOLD_SECONDS = 10  # Viewed for 10s+ = acceptance signal
    
    def __init__(self, collector: Optional[EventCollector] = None):
        self.collector = collector or get_event_collector()
        
        # Feedback storage
        self.feedback_records: Dict[str, EngineFeedback] = {}  # feedback_id -> record
        
        # Profile accuracy tracking
        self.profile_accuracy: Dict[str, ProfileAccuracy] = {}  # profile_id -> accuracy
        
        # Pending analyses (waiting for follow-up events)
        self._pending_analyses: Dict[str, Dict] = {}  # user_id -> analysis info
        
        # User return tracking
        self._user_analysis_count: Dict[str, int] = {}
        self._user_last_analysis: Dict[str, datetime] = {}
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT PROCESSING
    # ─────────────────────────────────────────────────────────────────────
    
    def process_events(self, events: List[AppEvent]):
        """Process events to extract feedback signals."""
        # Sort by timestamp
        events = sorted(events, key=lambda e: e.timestamp)
        
        for event in events:
            self._process_event(event)
        
        # Finalize any pending analyses past the window
        self._finalize_pending()
    
    def _process_event(self, event: AppEvent):
        """Process a single event."""
        
        if event.event_type == EventType.ANALYSIS_COMPLETED:
            self._handle_analysis_completed(event)
        
        elif event.event_type == EventType.PROFILE_VIEWED:
            self._handle_profile_viewed(event)
        
        elif event.event_type == EventType.PROFILE_SWITCHED:
            self._handle_profile_switched(event)
        
        elif event.event_type == EventType.RESULT_EXPORTED:
            self._handle_result_exported(event)
        
        elif event.event_type == EventType.RESULT_SAVED:
            self._handle_result_saved(event)
    
    def _handle_analysis_completed(self, event: AppEvent):
        """Handle analysis completion."""
        if not event.user_id:
            return
        
        profile_id = event.payload.get("profile_id", "unknown")
        profile_name = event.payload.get("profile_name", "Unknown")
        confidence = event.payload.get("confidence", 0)
        
        # Store pending analysis
        self._pending_analyses[event.user_id] = {
            "event": event,
            "profile_id": profile_id,
            "profile_name": profile_name,
            "confidence": confidence,
            "text_length": event.payload.get("text_length", 0),
            "signals": [],
            "profile_view_duration": 0,
            "was_exported": False,
            "was_saved": False,
            "final_profile_id": profile_id,  # Assume accepted until switch
        }
        
        # Track user analysis count
        self._user_analysis_count[event.user_id] = self._user_analysis_count.get(event.user_id, 0) + 1
        
        # Check for return signal
        last_analysis = self._user_last_analysis.get(event.user_id)
        if last_analysis:
            days_since = (event.timestamp - last_analysis).days
            if 1 <= days_since <= 30:
                # User returned - positive signal for previous analysis
                self._pending_analyses[event.user_id]["signals"].append(FeedbackSignal.USER_RETURNED)
        
        self._user_last_analysis[event.user_id] = event.timestamp
        
        # Update profile accuracy
        self._ensure_profile_accuracy(profile_id, profile_name)
        self.profile_accuracy[profile_id].times_predicted += 1
    
    def _handle_profile_viewed(self, event: AppEvent):
        """Handle profile view."""
        if not event.user_id or event.user_id not in self._pending_analyses:
            return
        
        pending = self._pending_analyses[event.user_id]
        view_duration = event.payload.get("view_duration_seconds", 0)
        
        pending["profile_view_duration"] += view_duration
        
        # Long engagement signal
        if view_duration >= self.ACCEPTANCE_THRESHOLD_SECONDS:
            if FeedbackSignal.LONG_ENGAGEMENT not in pending["signals"]:
                pending["signals"].append(FeedbackSignal.LONG_ENGAGEMENT)
        
        # Update profile accuracy
        profile_id = pending["profile_id"]
        if profile_id in self.profile_accuracy:
            self.profile_accuracy[profile_id].total_view_duration += view_duration
    
    def _handle_profile_switched(self, event: AppEvent):
        """Handle profile switch - indicates disagreement."""
        if not event.user_id or event.user_id not in self._pending_analyses:
            return
        
        pending = self._pending_analyses[event.user_id]
        from_profile = event.payload.get("from_profile_id")
        to_profile = event.payload.get("to_profile_id")
        
        # Check if switching away from predicted profile
        if from_profile == pending["profile_id"]:
            pending["signals"].append(FeedbackSignal.PROFILE_SWITCHED)
            pending["final_profile_id"] = to_profile
            
            # Update accuracy
            if from_profile in self.profile_accuracy:
                self.profile_accuracy[from_profile].times_switched_away += 1
            
            # Track what they switched to
            self._ensure_profile_accuracy(to_profile, "")
            self.profile_accuracy[to_profile].times_switched_to += 1
    
    def _handle_result_exported(self, event: AppEvent):
        """Handle result export - strong value signal."""
        if not event.user_id or event.user_id not in self._pending_analyses:
            return
        
        pending = self._pending_analyses[event.user_id]
        pending["was_exported"] = True
        pending["signals"].append(FeedbackSignal.RESULT_VALUED)
        
        # Update accuracy
        profile_id = pending["final_profile_id"]
        if profile_id in self.profile_accuracy:
            self.profile_accuracy[profile_id].times_exported += 1
    
    def _handle_result_saved(self, event: AppEvent):
        """Handle result save - value signal."""
        if not event.user_id or event.user_id not in self._pending_analyses:
            return
        
        pending = self._pending_analyses[event.user_id]
        pending["was_saved"] = True
        if FeedbackSignal.RESULT_VALUED not in pending["signals"]:
            pending["signals"].append(FeedbackSignal.RESULT_VALUED)
        
        # Update accuracy
        profile_id = pending["final_profile_id"]
        if profile_id in self.profile_accuracy:
            self.profile_accuracy[profile_id].times_saved += 1
    
    def _finalize_pending(self):
        """Finalize pending analyses past the association window."""
        cutoff = datetime.utcnow() - timedelta(minutes=self.ASSOCIATION_WINDOW_MINUTES)
        
        to_finalize = []
        for user_id, pending in self._pending_analyses.items():
            if pending["event"].timestamp < cutoff:
                to_finalize.append(user_id)
        
        for user_id in to_finalize:
            self._finalize_analysis(user_id)
    
    def _finalize_analysis(self, user_id: str):
        """Finalize a pending analysis into a feedback record."""
        if user_id not in self._pending_analyses:
            return
        
        pending = self._pending_analyses.pop(user_id)
        event = pending["event"]
        
        # Determine acceptance
        profile_id = pending["profile_id"]
        if FeedbackSignal.PROFILE_SWITCHED not in pending["signals"]:
            # User accepted the predicted profile
            pending["signals"].append(FeedbackSignal.PROFILE_ACCEPTED)
            
            if profile_id in self.profile_accuracy:
                self.profile_accuracy[profile_id].times_accepted += 1
        
        # Infer accuracy
        accuracy = self._infer_accuracy(pending["signals"], pending["profile_view_duration"])
        
        # Create feedback record
        feedback = EngineFeedback(
            feedback_id=f"fb_{event.event_id}",
            user_id=user_id,
            analysis_timestamp=event.timestamp,
            text_length=pending["text_length"],
            predicted_profile_id=profile_id,
            predicted_profile_name=pending["profile_name"],
            confidence=pending["confidence"],
            signals=pending["signals"],
            final_profile_id=pending["final_profile_id"],
            profile_view_duration=pending["profile_view_duration"],
            was_exported=pending["was_exported"],
            was_saved=pending["was_saved"],
            inferred_accuracy=accuracy,
        )
        
        self.feedback_records[feedback.feedback_id] = feedback
    
    def _infer_accuracy(self, signals: List[FeedbackSignal], view_duration: float) -> float:
        """
        Infer accuracy score from signals.
        
        Returns 0-1 score.
        """
        score = 0.5  # Start neutral
        
        # Strong positive signals
        if FeedbackSignal.PROFILE_ACCEPTED in signals:
            score += 0.2
        if FeedbackSignal.RESULT_VALUED in signals:
            score += 0.2
        if FeedbackSignal.USER_RETURNED in signals:
            score += 0.1
        
        # Engagement signal
        if FeedbackSignal.LONG_ENGAGEMENT in signals:
            score += 0.1
        
        # Strong negative signal
        if FeedbackSignal.PROFILE_SWITCHED in signals:
            score -= 0.4
        
        # Clamp to 0-1
        return max(0, min(1, score))
    
    def _ensure_profile_accuracy(self, profile_id: str, profile_name: str):
        """Ensure profile accuracy record exists."""
        if profile_id not in self.profile_accuracy:
            self.profile_accuracy[profile_id] = ProfileAccuracy(
                profile_id=profile_id,
                profile_name=profile_name,
            )
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_overall_accuracy(self) -> float:
        """Get overall Engine accuracy estimate."""
        if not self.feedback_records:
            return 0.75  # Default assumption
        
        accuracies = [f.inferred_accuracy for f in self.feedback_records.values() 
                      if f.inferred_accuracy is not None]
        
        if not accuracies:
            return 0.75
        
        return statistics.mean(accuracies)
    
    def get_accuracy_by_profile(self) -> Dict[str, float]:
        """Get accuracy breakdown by profile."""
        return {
            pid: pa.acceptance_rate 
            for pid, pa in self.profile_accuracy.items()
        }
    
    def get_problematic_profiles(self, threshold: float = 0.6) -> List[ProfileAccuracy]:
        """Get profiles with low acceptance rates."""
        return [
            pa for pa in self.profile_accuracy.values()
            if pa.times_predicted >= 10 and pa.acceptance_rate < threshold
        ]
    
    def get_engine_health_inputs(self) -> Dict:
        """Get inputs for Engine health calculation."""
        overall = self.get_overall_accuracy()
        problematic = self.get_problematic_profiles()
        
        # Calculate switch rate
        total_predicted = sum(pa.times_predicted for pa in self.profile_accuracy.values())
        total_switched = sum(pa.times_switched_away for pa in self.profile_accuracy.values())
        switch_rate = total_switched / total_predicted if total_predicted > 0 else 0
        
        return {
            "overall_accuracy": overall,
            "switch_rate": switch_rate,
            "problematic_profiles": len(problematic),
            "total_feedback": len(self.feedback_records),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get feedback collector summary."""
        return {
            "total_feedback_records": len(self.feedback_records),
            "profiles_tracked": len(self.profile_accuracy),
            "overall_accuracy": f"{self.get_overall_accuracy():.1%}",
            "pending_analyses": len(self._pending_analyses),
            "users_with_multiple_analyses": len([
                u for u, c in self._user_analysis_count.items() if c > 1
            ]),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_feedback_collector: Optional[EngineFeedbackCollector] = None

def get_engine_feedback_collector() -> EngineFeedbackCollector:
    """Get the global engine feedback collector."""
    global _feedback_collector
    if _feedback_collector is None:
        _feedback_collector = EngineFeedbackCollector()
    return _feedback_collector


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "FeedbackSignal",
    "EngineFeedback",
    "ProfileAccuracy",
    "EngineFeedbackCollector",
    "get_engine_feedback_collector",
]
