#!/usr/bin/env python3
"""
LNCP META: PREDICTION LOGGER v4.1
Logs every prediction and its eventual actual value for calibration.

This is the foundation for calibration. Every time Meta makes a prediction,
we log it. Later, we compare to actual and adjust confidence factors.

Key insight: Good predictions should be trusted more, bad predictions
should reduce confidence in that prediction type.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import statistics
import math


# ═══════════════════════════════════════════════════════════════════════════
# PREDICTION TYPES
# ═══════════════════════════════════════════════════════════════════════════

class PredictionType(str, Enum):
    """Types of predictions Meta makes."""
    # Action predictions
    ACTION_IMPACT = "action_impact"           # Predicted effect of an action
    ACTION_SUCCESS = "action_success"         # Will action succeed?
    ACTION_RISK = "action_risk"               # Risk level assessment
    
    # Classification predictions
    CLASSIFICATION_CORRECT = "classification_correct"  # Lane assignment
    REVIEW_DECISION = "review_decision"       # What will reviewer decide?
    
    # Metric predictions
    HEALTH_CHANGE = "health_change"           # System health impact
    CONVERSION_CHANGE = "conversion_change"   # Conversion rate impact
    ENGAGEMENT_CHANGE = "engagement_change"   # Engagement metric impact
    REVENUE_CHANGE = "revenue_change"         # Revenue impact
    
    # SEO predictions
    CTR_CHANGE = "ctr_change"                 # Click-through rate
    POSITION_CHANGE = "position_change"       # Search ranking
    IMPRESSIONS_CHANGE = "impressions_change" # Search impressions
    
    # Experiment predictions
    EXPERIMENT_WINNER = "experiment_winner"   # Which variant wins
    SIGNIFICANCE_TIME = "significance_time"   # Time to significance


class PredictionAccuracy(str, Enum):
    """How accurate was the prediction?"""
    EXACT = "exact"           # Within 5% of predicted
    CLOSE = "close"           # Within 20% of predicted
    DIRECTIONAL = "directional"  # Right direction, wrong magnitude
    WRONG = "wrong"           # Wrong direction or far off
    PENDING = "pending"       # Not yet determined


# ═══════════════════════════════════════════════════════════════════════════
# PREDICTION RECORD
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PredictionRecord:
    """A single prediction with its eventual outcome."""
    # Identity
    prediction_id: str
    prediction_type: PredictionType
    context_id: str           # Action ID, experiment ID, etc.
    context_type: str         # "action", "experiment", "cycle"
    
    # The prediction
    predicted_at: datetime
    predicted_value: float    # What we predicted
    confidence: float         # How confident (0-1)
    reasoning: str            # Why we made this prediction
    
    # The actual
    actual_value: Optional[float] = None
    actual_recorded_at: Optional[datetime] = None
    
    # Assessment
    accuracy: PredictionAccuracy = PredictionAccuracy.PENDING
    error: Optional[float] = None  # Absolute error
    error_pct: Optional[float] = None  # Percentage error
    
    # Calibration signals
    was_overconfident: bool = False  # Confidence was too high
    was_underconfident: bool = False  # Confidence was too low
    
    def to_dict(self) -> Dict:
        return {
            "prediction_id": self.prediction_id,
            "type": self.prediction_type.value,
            "context_id": self.context_id,
            "predicted_value": self.predicted_value,
            "confidence": self.confidence,
            "actual_value": self.actual_value,
            "accuracy": self.accuracy.value,
            "error_pct": self.error_pct,
        }


# ═══════════════════════════════════════════════════════════════════════════
# CALIBRATION FACTOR
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CalibrationFactor:
    """Calibration adjustment for a prediction type."""
    prediction_type: PredictionType
    
    # Adjustments
    confidence_multiplier: float = 1.0   # Multiply confidence by this
    value_bias: float = 0.0              # Add this to predicted values
    value_scale: float = 1.0             # Multiply predicted values by this
    
    # Evidence
    sample_size: int = 0
    avg_error: float = 0.0
    avg_confidence: float = 0.0
    accuracy_rate: float = 0.0           # % of predictions that were close
    
    last_updated: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════════════════
# PREDICTION LOGGER
# ═══════════════════════════════════════════════════════════════════════════

class PredictionLogger:
    """
    Logs all predictions and tracks their accuracy.
    
    The core of Meta's calibration system. Every prediction is logged,
    and we continuously update calibration factors based on results.
    """
    
    def __init__(self):
        self.predictions: Dict[str, PredictionRecord] = {}
        self.pending: List[str] = []
        
        # Calibration factors per prediction type
        self.calibration: Dict[PredictionType, CalibrationFactor] = {
            ptype: CalibrationFactor(prediction_type=ptype)
            for ptype in PredictionType
        }
        
        # Counters
        self._prediction_counter = 0
    
    # ─────────────────────────────────────────────────────────────────────
    # LOGGING PREDICTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def log_prediction(
        self,
        prediction_type: PredictionType,
        predicted_value: float,
        confidence: float,
        context_id: str,
        context_type: str,
        reasoning: str = "",
    ) -> str:
        """
        Log a new prediction.
        
        Returns the prediction ID for later recording actual.
        """
        self._prediction_counter += 1
        prediction_id = f"pred_{datetime.utcnow().strftime('%Y%m%d')}_{self._prediction_counter:06d}"
        
        # Apply calibration to the prediction
        calibration = self.calibration[prediction_type]
        calibrated_value = (predicted_value * calibration.value_scale) + calibration.value_bias
        calibrated_confidence = min(1.0, confidence * calibration.confidence_multiplier)
        
        record = PredictionRecord(
            prediction_id=prediction_id,
            prediction_type=prediction_type,
            context_id=context_id,
            context_type=context_type,
            predicted_at=datetime.utcnow(),
            predicted_value=calibrated_value,
            confidence=calibrated_confidence,
            reasoning=reasoning,
        )
        
        self.predictions[prediction_id] = record
        self.pending.append(prediction_id)
        
        return prediction_id
    
    def record_actual(
        self,
        prediction_id: str,
        actual_value: float,
    ) -> Optional[PredictionRecord]:
        """
        Record the actual value for a prediction.
        
        This triggers accuracy assessment and calibration update.
        """
        if prediction_id not in self.predictions:
            return None
        
        record = self.predictions[prediction_id]
        record.actual_value = actual_value
        record.actual_recorded_at = datetime.utcnow()
        
        # Calculate error
        record.error = abs(actual_value - record.predicted_value)
        if record.predicted_value != 0:
            record.error_pct = abs(record.error / record.predicted_value) * 100
        else:
            record.error_pct = 100 if actual_value != 0 else 0
        
        # Assess accuracy
        if record.error_pct <= 5:
            record.accuracy = PredictionAccuracy.EXACT
        elif record.error_pct <= 20:
            record.accuracy = PredictionAccuracy.CLOSE
        elif (record.predicted_value > 0) == (actual_value > 0):
            record.accuracy = PredictionAccuracy.DIRECTIONAL
        else:
            record.accuracy = PredictionAccuracy.WRONG
        
        # Assess confidence calibration
        # If confidence was high but we were wrong, overconfident
        # If confidence was low but we were exact, underconfident
        if record.confidence >= 0.8 and record.accuracy == PredictionAccuracy.WRONG:
            record.was_overconfident = True
        elif record.confidence <= 0.5 and record.accuracy in [PredictionAccuracy.EXACT, PredictionAccuracy.CLOSE]:
            record.was_underconfident = True
        
        # Remove from pending
        if prediction_id in self.pending:
            self.pending.remove(prediction_id)
        
        # Update calibration
        self._update_calibration(record.prediction_type)
        
        return record
    
    # ─────────────────────────────────────────────────────────────────────
    # CALIBRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _update_calibration(self, prediction_type: PredictionType):
        """Update calibration factors based on recent predictions."""
        # Get recent completed predictions of this type
        recent = [
            p for p in self.predictions.values()
            if p.prediction_type == prediction_type
            and p.actual_value is not None
            and p.predicted_at >= datetime.utcnow() - timedelta(days=90)
        ]
        
        if len(recent) < 5:
            return  # Not enough data
        
        calibration = self.calibration[prediction_type]
        calibration.sample_size = len(recent)
        calibration.last_updated = datetime.utcnow()
        
        # Calculate average error
        errors = [p.error for p in recent if p.error is not None]
        calibration.avg_error = statistics.mean(errors) if errors else 0
        
        # Calculate average confidence
        calibration.avg_confidence = statistics.mean([p.confidence for p in recent])
        
        # Calculate accuracy rate (exact + close)
        accurate = sum(
            1 for p in recent 
            if p.accuracy in [PredictionAccuracy.EXACT, PredictionAccuracy.CLOSE]
        )
        calibration.accuracy_rate = accurate / len(recent)
        
        # Adjust confidence multiplier
        # If we're often overconfident, reduce multiplier
        # If we're often underconfident, increase multiplier
        overconfident_count = sum(1 for p in recent if p.was_overconfident)
        underconfident_count = sum(1 for p in recent if p.was_underconfident)
        
        if overconfident_count > len(recent) * 0.2:
            calibration.confidence_multiplier = max(0.5, calibration.confidence_multiplier * 0.95)
        elif underconfident_count > len(recent) * 0.2:
            calibration.confidence_multiplier = min(1.5, calibration.confidence_multiplier * 1.05)
        
        # Adjust value scale based on systematic bias
        if len(recent) >= 10:
            # Calculate if we systematically over or under predict
            ratios = [
                p.actual_value / p.predicted_value 
                for p in recent 
                if p.predicted_value != 0
            ]
            if ratios:
                avg_ratio = statistics.mean(ratios)
                # Slowly adjust toward correct scale
                calibration.value_scale = (calibration.value_scale * 0.9) + (avg_ratio * 0.1)
    
    def get_calibrated_prediction(
        self,
        prediction_type: PredictionType,
        raw_value: float,
        raw_confidence: float,
    ) -> Tuple[float, float]:
        """
        Apply calibration to a raw prediction.
        
        Returns (calibrated_value, calibrated_confidence).
        """
        calibration = self.calibration[prediction_type]
        
        calibrated_value = (raw_value * calibration.value_scale) + calibration.value_bias
        calibrated_confidence = min(1.0, raw_confidence * calibration.confidence_multiplier)
        
        return calibrated_value, calibrated_confidence
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_accuracy_report(self, days: int = 30) -> Dict:
        """Get accuracy report for recent predictions."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        recent = [
            p for p in self.predictions.values()
            if p.predicted_at >= cutoff and p.actual_value is not None
        ]
        
        if not recent:
            return {"message": "No completed predictions in period"}
        
        by_type: Dict[str, Dict] = {}
        for ptype in PredictionType:
            type_preds = [p for p in recent if p.prediction_type == ptype]
            if type_preds:
                accurate = sum(
                    1 for p in type_preds 
                    if p.accuracy in [PredictionAccuracy.EXACT, PredictionAccuracy.CLOSE]
                )
                by_type[ptype.value] = {
                    "count": len(type_preds),
                    "accuracy_rate": accurate / len(type_preds),
                    "avg_error_pct": statistics.mean([
                        p.error_pct for p in type_preds if p.error_pct is not None
                    ]),
                    "calibration_factor": self.calibration[ptype].confidence_multiplier,
                }
        
        overall_accurate = sum(
            1 for p in recent 
            if p.accuracy in [PredictionAccuracy.EXACT, PredictionAccuracy.CLOSE]
        )
        
        return {
            "period_days": days,
            "total_predictions": len(recent),
            "pending": len(self.pending),
            "overall_accuracy_rate": overall_accurate / len(recent),
            "by_type": by_type,
            "by_accuracy": {
                acc.value: sum(1 for p in recent if p.accuracy == acc)
                for acc in PredictionAccuracy
                if acc != PredictionAccuracy.PENDING
            },
        }
    
    def get_calibration_summary(self) -> Dict:
        """Get summary of all calibration factors."""
        return {
            ptype.value: {
                "confidence_multiplier": cal.confidence_multiplier,
                "value_scale": cal.value_scale,
                "value_bias": cal.value_bias,
                "sample_size": cal.sample_size,
                "accuracy_rate": cal.accuracy_rate,
                "last_updated": cal.last_updated.isoformat() if cal.last_updated else None,
            }
            for ptype, cal in self.calibration.items()
            if cal.sample_size > 0
        }
    
    def get_worst_predictions(self, limit: int = 10) -> List[PredictionRecord]:
        """Get worst recent predictions for analysis."""
        completed = [
            p for p in self.predictions.values()
            if p.actual_value is not None and p.error_pct is not None
        ]
        return sorted(completed, key=lambda p: p.error_pct, reverse=True)[:limit]


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_prediction_logger: Optional[PredictionLogger] = None

def get_prediction_logger() -> PredictionLogger:
    """Get the global prediction logger instance."""
    global _prediction_logger
    if _prediction_logger is None:
        _prediction_logger = PredictionLogger()
    return _prediction_logger


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "PredictionType",
    "PredictionAccuracy",
    "PredictionRecord",
    "CalibrationFactor",
    "PredictionLogger",
    "get_prediction_logger",
]
