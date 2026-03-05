#!/usr/bin/env python3
"""
LNCP META: OUTCOME TRACKER v4.1
Tracks the outcome of every action to enable learning.

Without this, Meta cannot learn. Every decision must be followed
to its conclusion so we can calibrate predictions.

Tracks:
- Action outcomes (success, failure, partial, unknown)
- Predicted vs actual impact
- Time to outcome
- Side effects detected
- Rollback events
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import statistics


# ═══════════════════════════════════════════════════════════════════════════
# OUTCOME TYPES
# ═══════════════════════════════════════════════════════════════════════════

class OutcomeStatus(str, Enum):
    """Status of an action's outcome."""
    PENDING = "pending"           # Waiting for enough data
    SUCCESS = "success"           # Achieved predicted outcome
    PARTIAL = "partial"           # Some improvement, less than predicted
    NEUTRAL = "neutral"           # No significant change
    FAILURE = "failure"           # Negative outcome
    ROLLED_BACK = "rolled_back"   # Had to revert
    UNKNOWN = "unknown"           # Cannot determine


class OutcomeConfidence(str, Enum):
    """How confident we are in the outcome assessment."""
    HIGH = "high"         # Clear signal, sufficient data
    MEDIUM = "medium"     # Some signal, moderate data
    LOW = "low"           # Weak signal, limited data
    INSUFFICIENT = "insufficient"  # Not enough data yet


# ═══════════════════════════════════════════════════════════════════════════
# OUTCOME DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PredictedOutcome:
    """What we predicted would happen."""
    metric_name: str              # e.g., "ctr", "conversion_rate", "health"
    baseline_value: float         # Value before action
    predicted_value: float        # What we expected
    predicted_change_pct: float   # Expected % change
    confidence: float             # How confident the prediction was (0-1)
    time_horizon_days: int        # How long until we expect to see results


@dataclass
class ActualOutcome:
    """What actually happened."""
    metric_name: str
    baseline_value: float
    actual_value: float
    actual_change_pct: float
    measurement_time: datetime
    data_points: int              # How many observations
    statistical_significance: float  # p-value or equivalent


@dataclass
class OutcomeRecord:
    """Complete record of an action's outcome."""
    # Identity
    action_id: str
    action_type: str
    domain: str                   # "app", "blog", "meta"
    
    # Timing
    executed_at: datetime
    outcome_assessed_at: Optional[datetime] = None
    time_to_outcome_hours: Optional[float] = None
    
    # Predictions and actuals
    predictions: List[PredictedOutcome] = field(default_factory=list)
    actuals: List[ActualOutcome] = field(default_factory=list)
    
    # Assessment
    status: OutcomeStatus = OutcomeStatus.PENDING
    confidence: OutcomeConfidence = OutcomeConfidence.INSUFFICIENT
    
    # Learning signals
    prediction_accuracy: Optional[float] = None  # How close was prediction? (0-1)
    was_rollback_needed: bool = False
    rollback_reason: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    
    # Context for learning
    system_health_at_execution: Optional[float] = None
    classification_lane: Optional[str] = None  # "auto", "review", "super_admin"
    reviewer_decision: Optional[str] = None    # If reviewed: "approved", "rejected"
    
    # Notes
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "domain": self.domain,
            "executed_at": self.executed_at.isoformat(),
            "outcome_assessed_at": self.outcome_assessed_at.isoformat() if self.outcome_assessed_at else None,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "prediction_accuracy": self.prediction_accuracy,
            "was_rollback_needed": self.was_rollback_needed,
            "predictions": [
                {
                    "metric": p.metric_name,
                    "predicted_change": p.predicted_change_pct,
                    "confidence": p.confidence,
                }
                for p in self.predictions
            ],
            "actuals": [
                {
                    "metric": a.metric_name,
                    "actual_change": a.actual_change_pct,
                    "significance": a.statistical_significance,
                }
                for a in self.actuals
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════
# OUTCOME TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class OutcomeTracker:
    """
    Tracks outcomes for all actions across the system.
    
    This is the foundation of Meta's learning capability.
    Every action gets tracked, and outcomes feed back into calibration.
    """
    
    def __init__(self):
        self.outcomes: Dict[str, OutcomeRecord] = {}
        self.pending_assessment: List[str] = []
        
        # Aggregated learning
        self.accuracy_by_action_type: Dict[str, List[float]] = {}
        self.success_rate_by_action_type: Dict[str, float] = {}
        self.rollback_rate_by_action_type: Dict[str, float] = {}
    
    # ─────────────────────────────────────────────────────────────────────
    # REGISTRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def register_action(
        self,
        action_id: str,
        action_type: str,
        domain: str,
        predictions: List[PredictedOutcome],
        classification_lane: str,
        system_health: float,
    ) -> OutcomeRecord:
        """
        Register an action that was just executed.
        
        This must be called for EVERY action so we can track its outcome.
        """
        record = OutcomeRecord(
            action_id=action_id,
            action_type=action_type,
            domain=domain,
            executed_at=datetime.utcnow(),
            predictions=predictions,
            classification_lane=classification_lane,
            system_health_at_execution=system_health,
        )
        
        self.outcomes[action_id] = record
        self.pending_assessment.append(action_id)
        
        return record
    
    def register_review_decision(
        self,
        action_id: str,
        decision: str,
        reviewer_notes: Optional[str] = None,
    ):
        """Record the decision made during human review."""
        if action_id in self.outcomes:
            self.outcomes[action_id].reviewer_decision = decision
            if reviewer_notes:
                self.outcomes[action_id].notes.append(f"Reviewer: {reviewer_notes}")
    
    # ─────────────────────────────────────────────────────────────────────
    # OUTCOME RECORDING
    # ─────────────────────────────────────────────────────────────────────
    
    def record_actual(
        self,
        action_id: str,
        metric_name: str,
        baseline_value: float,
        actual_value: float,
        data_points: int,
        statistical_significance: float = 0.0,
    ):
        """Record an actual outcome measurement for an action."""
        if action_id not in self.outcomes:
            return
        
        record = self.outcomes[action_id]
        
        actual = ActualOutcome(
            metric_name=metric_name,
            baseline_value=baseline_value,
            actual_value=actual_value,
            actual_change_pct=((actual_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0,
            measurement_time=datetime.utcnow(),
            data_points=data_points,
            statistical_significance=statistical_significance,
        )
        
        record.actuals.append(actual)
    
    def record_rollback(
        self,
        action_id: str,
        reason: str,
    ):
        """Record that an action had to be rolled back."""
        if action_id not in self.outcomes:
            return
        
        record = self.outcomes[action_id]
        record.was_rollback_needed = True
        record.rollback_reason = reason
        record.status = OutcomeStatus.ROLLED_BACK
        record.outcome_assessed_at = datetime.utcnow()
        
        if action_id in self.pending_assessment:
            self.pending_assessment.remove(action_id)
        
        self._update_aggregates(record)
    
    def record_side_effect(
        self,
        action_id: str,
        side_effect: str,
    ):
        """Record an unintended side effect of an action."""
        if action_id in self.outcomes:
            self.outcomes[action_id].side_effects.append(side_effect)
    
    # ─────────────────────────────────────────────────────────────────────
    # OUTCOME ASSESSMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def assess_outcome(
        self,
        action_id: str,
        force: bool = False,
    ) -> Optional[OutcomeRecord]:
        """
        Assess the outcome of an action based on collected data.
        
        Returns the updated record, or None if not enough data.
        """
        if action_id not in self.outcomes:
            return None
        
        record = self.outcomes[action_id]
        
        # Check if we have enough data
        if not record.actuals and not force:
            return None
        
        # Check if enough time has passed
        min_horizon = min(
            (p.time_horizon_days for p in record.predictions),
            default=7
        )
        elapsed = datetime.utcnow() - record.executed_at
        
        if elapsed < timedelta(days=min_horizon) and not force:
            record.confidence = OutcomeConfidence.INSUFFICIENT
            return record
        
        # Assess each prediction vs actual
        accuracy_scores = []
        status_votes = []
        
        for prediction in record.predictions:
            # Find matching actual
            actual = next(
                (a for a in record.actuals if a.metric_name == prediction.metric_name),
                None
            )
            
            if not actual:
                continue
            
            # Calculate prediction accuracy
            if prediction.predicted_change_pct != 0:
                accuracy = 1 - abs(
                    (actual.actual_change_pct - prediction.predicted_change_pct) 
                    / prediction.predicted_change_pct
                )
                accuracy = max(0, min(1, accuracy))
            else:
                accuracy = 1.0 if abs(actual.actual_change_pct) < 5 else 0.5
            
            accuracy_scores.append(accuracy)
            
            # Vote on status
            if actual.actual_change_pct >= prediction.predicted_change_pct * 0.8:
                status_votes.append(OutcomeStatus.SUCCESS)
            elif actual.actual_change_pct >= prediction.predicted_change_pct * 0.3:
                status_votes.append(OutcomeStatus.PARTIAL)
            elif actual.actual_change_pct >= -5:
                status_votes.append(OutcomeStatus.NEUTRAL)
            else:
                status_votes.append(OutcomeStatus.FAILURE)
        
        # Aggregate assessment
        if accuracy_scores:
            record.prediction_accuracy = statistics.mean(accuracy_scores)
        
        # Determine overall status
        if status_votes:
            # Worst vote wins (conservative)
            if OutcomeStatus.FAILURE in status_votes:
                record.status = OutcomeStatus.FAILURE
            elif OutcomeStatus.NEUTRAL in status_votes:
                record.status = OutcomeStatus.NEUTRAL
            elif OutcomeStatus.PARTIAL in status_votes:
                record.status = OutcomeStatus.PARTIAL
            else:
                record.status = OutcomeStatus.SUCCESS
        else:
            record.status = OutcomeStatus.UNKNOWN
        
        # Determine confidence
        total_data_points = sum(a.data_points for a in record.actuals)
        avg_significance = statistics.mean(
            [a.statistical_significance for a in record.actuals]
        ) if record.actuals else 0
        
        if total_data_points >= 1000 and avg_significance >= 0.95:
            record.confidence = OutcomeConfidence.HIGH
        elif total_data_points >= 100 and avg_significance >= 0.80:
            record.confidence = OutcomeConfidence.MEDIUM
        elif total_data_points >= 10:
            record.confidence = OutcomeConfidence.LOW
        else:
            record.confidence = OutcomeConfidence.INSUFFICIENT
        
        # Finalize
        record.outcome_assessed_at = datetime.utcnow()
        record.time_to_outcome_hours = (
            record.outcome_assessed_at - record.executed_at
        ).total_seconds() / 3600
        
        if action_id in self.pending_assessment:
            self.pending_assessment.remove(action_id)
        
        self._update_aggregates(record)
        
        return record
    
    def assess_all_pending(self) -> List[OutcomeRecord]:
        """Assess all pending outcomes that are ready."""
        assessed = []
        for action_id in list(self.pending_assessment):
            result = self.assess_outcome(action_id)
            if result and result.status != OutcomeStatus.PENDING:
                assessed.append(result)
        return assessed
    
    # ─────────────────────────────────────────────────────────────────────
    # AGGREGATE LEARNING
    # ─────────────────────────────────────────────────────────────────────
    
    def _update_aggregates(self, record: OutcomeRecord):
        """Update aggregate statistics based on a new outcome."""
        action_type = record.action_type
        
        # Track accuracy
        if record.prediction_accuracy is not None:
            if action_type not in self.accuracy_by_action_type:
                self.accuracy_by_action_type[action_type] = []
            self.accuracy_by_action_type[action_type].append(record.prediction_accuracy)
        
        # Update success rate
        assessed = [
            o for o in self.outcomes.values()
            if o.action_type == action_type and o.status != OutcomeStatus.PENDING
        ]
        if assessed:
            successes = sum(
                1 for o in assessed 
                if o.status in [OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL]
            )
            self.success_rate_by_action_type[action_type] = successes / len(assessed)
            
            rollbacks = sum(1 for o in assessed if o.was_rollback_needed)
            self.rollback_rate_by_action_type[action_type] = rollbacks / len(assessed)
    
    def get_accuracy_for_action_type(self, action_type: str) -> Optional[float]:
        """Get average prediction accuracy for an action type."""
        accuracies = self.accuracy_by_action_type.get(action_type, [])
        return statistics.mean(accuracies) if accuracies else None
    
    def get_success_rate_for_action_type(self, action_type: str) -> Optional[float]:
        """Get success rate for an action type."""
        return self.success_rate_by_action_type.get(action_type)
    
    def get_rollback_rate_for_action_type(self, action_type: str) -> Optional[float]:
        """Get rollback rate for an action type."""
        return self.rollback_rate_by_action_type.get(action_type)
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_recent_outcomes(
        self,
        days: int = 30,
        domain: Optional[str] = None,
        action_type: Optional[str] = None,
    ) -> List[OutcomeRecord]:
        """Get recent assessed outcomes."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        results = [
            o for o in self.outcomes.values()
            if o.executed_at >= cutoff and o.status != OutcomeStatus.PENDING
        ]
        
        if domain:
            results = [o for o in results if o.domain == domain]
        if action_type:
            results = [o for o in results if o.action_type == action_type]
        
        return sorted(results, key=lambda o: o.executed_at, reverse=True)
    
    def get_failures(self, days: int = 30) -> List[OutcomeRecord]:
        """Get recent failures for analysis."""
        return [
            o for o in self.get_recent_outcomes(days)
            if o.status in [OutcomeStatus.FAILURE, OutcomeStatus.ROLLED_BACK]
        ]
    
    def get_learning_summary(self) -> Dict:
        """Get summary of learning from outcomes."""
        all_assessed = [
            o for o in self.outcomes.values()
            if o.status != OutcomeStatus.PENDING
        ]
        
        if not all_assessed:
            return {
                "total_tracked": len(self.outcomes),
                "pending": len(self.pending_assessment),
                "assessed": 0,
                "learning": "No outcomes assessed yet",
            }
        
        return {
            "total_tracked": len(self.outcomes),
            "pending": len(self.pending_assessment),
            "assessed": len(all_assessed),
            "by_status": {
                status.value: sum(1 for o in all_assessed if o.status == status)
                for status in OutcomeStatus
                if status != OutcomeStatus.PENDING
            },
            "overall_success_rate": sum(
                1 for o in all_assessed 
                if o.status in [OutcomeStatus.SUCCESS, OutcomeStatus.PARTIAL]
            ) / len(all_assessed),
            "overall_rollback_rate": sum(
                1 for o in all_assessed if o.was_rollback_needed
            ) / len(all_assessed),
            "avg_prediction_accuracy": statistics.mean([
                o.prediction_accuracy for o in all_assessed
                if o.prediction_accuracy is not None
            ]) if any(o.prediction_accuracy for o in all_assessed) else None,
            "accuracy_by_action_type": {
                k: statistics.mean(v) if v else None
                for k, v in self.accuracy_by_action_type.items()
            },
            "success_rate_by_action_type": self.success_rate_by_action_type,
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_outcome_tracker: Optional[OutcomeTracker] = None

def get_outcome_tracker() -> OutcomeTracker:
    """Get the global outcome tracker instance."""
    global _outcome_tracker
    if _outcome_tracker is None:
        _outcome_tracker = OutcomeTracker()
    return _outcome_tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "OutcomeStatus",
    "OutcomeConfidence",
    "PredictedOutcome",
    "ActualOutcome",
    "OutcomeRecord",
    "OutcomeTracker",
    "get_outcome_tracker",
]
