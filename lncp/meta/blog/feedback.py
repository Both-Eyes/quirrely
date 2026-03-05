#!/usr/bin/env python3
"""
LNCP META/BLOG: FEEDBACK LOOP v1.0
Calibrates blog optimization from real vs predicted results.

Learns:
- Which meta templates actually improve CTR
- Which CTA variants actually convert
- Which content changes move rankings
- How accurate our predictions are

This closes the loop: Predict → Act → Measure → Calibrate → Predict Better
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import statistics

from .gsc import SearchMetrics, PageSearchData
from .tracker import PageMetrics
from .ab_testing import Experiment, ExperimentResult


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK TYPES
# ═══════════════════════════════════════════════════════════════════════════

class MetricType(str, Enum):
    CTR = "ctr"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    POSITION = "position"
    CONVERSION_RATE = "conversion_rate"
    CTA_CLICK_RATE = "cta_click_rate"
    TIME_ON_PAGE = "time_on_page"
    SCROLL_DEPTH = "scroll_depth"
    BOUNCE_RATE = "bounce_rate"


class PredictionAccuracy(str, Enum):
    ACCURATE = "accurate"           # Within 10%
    SLIGHTLY_OFF = "slightly_off"   # 10-25% off
    INACCURATE = "inaccurate"       # 25-50% off
    WILDLY_OFF = "wildly_off"       # >50% off


@dataclass
class Prediction:
    """A prediction we made about an action's impact."""
    prediction_id: str
    action_id: str
    action_type: str
    page_url: str
    
    # What we predicted
    metric_type: MetricType
    predicted_value: float
    predicted_change: float  # Expected delta
    confidence: float
    
    # Timestamps
    predicted_at: datetime = field(default_factory=datetime.utcnow)
    
    # Actual results (filled in later)
    actual_value: Optional[float] = None
    actual_change: Optional[float] = None
    measured_at: Optional[datetime] = None
    
    # Accuracy assessment
    accuracy: Optional[PredictionAccuracy] = None
    error_percent: Optional[float] = None
    
    def assess_accuracy(self):
        """Assess prediction accuracy once actual value is known."""
        if self.actual_change is None or self.predicted_change == 0:
            return
        
        self.error_percent = abs(self.actual_change - self.predicted_change) / abs(self.predicted_change) * 100
        
        if self.error_percent <= 10:
            self.accuracy = PredictionAccuracy.ACCURATE
        elif self.error_percent <= 25:
            self.accuracy = PredictionAccuracy.SLIGHTLY_OFF
        elif self.error_percent <= 50:
            self.accuracy = PredictionAccuracy.INACCURATE
        else:
            self.accuracy = PredictionAccuracy.WILDLY_OFF


@dataclass
class CalibrationFactor:
    """Adjustment factor for a metric type."""
    metric_type: MetricType
    factor: float  # Multiply predictions by this
    confidence: float
    sample_size: int
    last_updated: datetime


@dataclass
class ActionOutcome:
    """The outcome of an applied action."""
    action_id: str
    action_type: str
    page_url: str
    
    # Before/after metrics
    before_metrics: Dict[str, float] = field(default_factory=dict)
    after_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Calculated changes
    changes: Dict[str, float] = field(default_factory=dict)
    
    # Success assessment
    success: bool = False
    success_metric: Optional[str] = None
    success_threshold: Optional[float] = None
    
    # Timing
    applied_at: datetime = field(default_factory=datetime.utcnow)
    measured_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class BlogFeedbackCollector:
    """
    Collects feedback data for calibration.
    
    Tracks:
    - Predictions made
    - Actions applied
    - Actual outcomes
    """
    
    def __init__(self):
        self.predictions: Dict[str, Prediction] = {}
        self.outcomes: Dict[str, ActionOutcome] = {}
        
        # Baseline snapshots for comparison
        self.baselines: Dict[str, Dict[str, float]] = {}  # page_url -> metrics
    
    def record_baseline(self, page_url: str, metrics: Dict[str, float]):
        """Record baseline metrics for a page before changes."""
        self.baselines[page_url] = {
            **metrics,
            "recorded_at": datetime.utcnow().isoformat(),
        }
    
    def record_prediction(
        self,
        action_id: str,
        action_type: str,
        page_url: str,
        metric_type: MetricType,
        predicted_change: float,
        confidence: float,
        current_value: float = 0,
    ) -> Prediction:
        """Record a prediction about an action's impact."""
        pred_id = f"pred_{action_id}_{metric_type.value}"
        
        prediction = Prediction(
            prediction_id=pred_id,
            action_id=action_id,
            action_type=action_type,
            page_url=page_url,
            metric_type=metric_type,
            predicted_value=current_value + predicted_change,
            predicted_change=predicted_change,
            confidence=confidence,
        )
        
        self.predictions[pred_id] = prediction
        return prediction
    
    def record_outcome(
        self,
        action_id: str,
        action_type: str,
        page_url: str,
        before_metrics: Dict[str, float],
        after_metrics: Dict[str, float],
        success_metric: str = "ctr",
        success_threshold: float = 0.05,
    ) -> ActionOutcome:
        """Record the actual outcome of an action."""
        
        # Calculate changes
        changes = {}
        for key in after_metrics:
            if key in before_metrics and before_metrics[key] != 0:
                changes[key] = (after_metrics[key] - before_metrics[key]) / before_metrics[key]
            else:
                changes[key] = 0
        
        # Assess success
        success = changes.get(success_metric, 0) >= success_threshold
        
        outcome = ActionOutcome(
            action_id=action_id,
            action_type=action_type,
            page_url=page_url,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            changes=changes,
            success=success,
            success_metric=success_metric,
            success_threshold=success_threshold,
            measured_at=datetime.utcnow(),
        )
        
        self.outcomes[action_id] = outcome
        
        # Update related predictions
        for pred in self.predictions.values():
            if pred.action_id == action_id:
                metric_key = pred.metric_type.value
                if metric_key in after_metrics:
                    pred.actual_value = after_metrics[metric_key]
                    pred.actual_change = changes.get(metric_key, 0)
                    pred.measured_at = datetime.utcnow()
                    pred.assess_accuracy()
        
        return outcome
    
    def get_prediction_accuracy_stats(self) -> Dict:
        """Get accuracy statistics for predictions."""
        assessed = [p for p in self.predictions.values() if p.accuracy is not None]
        
        if not assessed:
            return {"sample_size": 0}
        
        by_accuracy = {}
        for acc in PredictionAccuracy:
            by_accuracy[acc.value] = len([p for p in assessed if p.accuracy == acc])
        
        errors = [p.error_percent for p in assessed if p.error_percent is not None]
        
        return {
            "sample_size": len(assessed),
            "by_accuracy": by_accuracy,
            "mean_error_percent": statistics.mean(errors) if errors else 0,
            "median_error_percent": statistics.median(errors) if errors else 0,
            "accuracy_rate": by_accuracy.get("accurate", 0) / len(assessed) if assessed else 0,
        }
    
    def get_success_rate(self) -> Dict:
        """Get success rate of actions."""
        if not self.outcomes:
            return {"sample_size": 0}
        
        successes = len([o for o in self.outcomes.values() if o.success])
        
        return {
            "sample_size": len(self.outcomes),
            "successes": successes,
            "success_rate": successes / len(self.outcomes),
        }


# ═══════════════════════════════════════════════════════════════════════════
# CALIBRATOR
# ═══════════════════════════════════════════════════════════════════════════

class BlogCalibrator:
    """
    Calibrates predictions based on historical accuracy.
    
    If we consistently overestimate CTR gains by 20%, we apply
    a 0.8 factor to future CTR predictions.
    """
    
    def __init__(self, collector: BlogFeedbackCollector):
        self.collector = collector
        self.calibration_factors: Dict[MetricType, CalibrationFactor] = {}
        
        # Learning parameters
        self.min_samples_for_calibration = 10
        self.max_factor_change_per_cycle = 0.2  # Don't change more than 20% at once
        self.recalibration_interval_hours = 24
        self.last_calibration: Optional[datetime] = None
    
    def calibrate_metric(self, metric_type: MetricType) -> Optional[CalibrationFactor]:
        """Calibrate predictions for a specific metric type."""
        
        # Get predictions for this metric
        predictions = [
            p for p in self.collector.predictions.values()
            if p.metric_type == metric_type and p.actual_change is not None
        ]
        
        if len(predictions) < self.min_samples_for_calibration:
            return None
        
        # Calculate ratio of actual to predicted
        ratios = []
        for pred in predictions:
            if pred.predicted_change != 0:
                ratio = pred.actual_change / pred.predicted_change
                ratios.append(ratio)
        
        if not ratios:
            return None
        
        # Use median for robustness
        raw_factor = statistics.median(ratios)
        
        # Limit change from current factor
        current = self.calibration_factors.get(metric_type)
        if current:
            max_delta = current.factor * self.max_factor_change_per_cycle
            clamped_factor = max(
                current.factor - max_delta,
                min(current.factor + max_delta, raw_factor)
            )
        else:
            clamped_factor = raw_factor
        
        # Calculate confidence based on consistency
        stdev = statistics.stdev(ratios) if len(ratios) > 1 else 0
        consistency = max(0, 1 - stdev)
        confidence = min(1.0, (len(ratios) / 50) * consistency)
        
        factor = CalibrationFactor(
            metric_type=metric_type,
            factor=clamped_factor,
            confidence=confidence,
            sample_size=len(predictions),
            last_updated=datetime.utcnow(),
        )
        
        self.calibration_factors[metric_type] = factor
        return factor
    
    def calibrate_all(self) -> Dict[str, CalibrationFactor]:
        """Calibrate all metric types."""
        for metric_type in MetricType:
            self.calibrate_metric(metric_type)
        
        self.last_calibration = datetime.utcnow()
        return self.calibration_factors
    
    def get_calibrated_prediction(
        self,
        metric_type: MetricType,
        raw_prediction: float,
    ) -> Tuple[float, float]:
        """
        Get calibrated prediction.
        
        Returns (calibrated_value, confidence).
        """
        factor = self.calibration_factors.get(metric_type)
        
        if factor:
            calibrated = raw_prediction * factor.factor
            confidence = factor.confidence
        else:
            calibrated = raw_prediction
            confidence = 0.5  # Default confidence
        
        return calibrated, confidence
    
    def should_recalibrate(self) -> bool:
        """Check if recalibration is needed."""
        if self.last_calibration is None:
            return True
        
        hours_since = (datetime.utcnow() - self.last_calibration).total_seconds() / 3600
        return hours_since >= self.recalibration_interval_hours
    
    def get_calibration_status(self) -> Dict:
        """Get current calibration status."""
        return {
            "factors": {
                mt.value: {
                    "factor": f.factor,
                    "confidence": f.confidence,
                    "sample_size": f.sample_size,
                }
                for mt, f in self.calibration_factors.items()
            },
            "last_calibration": self.last_calibration.isoformat() if self.last_calibration else None,
            "needs_recalibration": self.should_recalibrate(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# INSIGHT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class BlogInsightGenerator:
    """
    Generates insights from feedback data.
    
    Identifies:
    - What's working
    - What's not working
    - Systematic biases in predictions
    - Opportunities
    """
    
    def __init__(self, collector: BlogFeedbackCollector, calibrator: BlogCalibrator):
        self.collector = collector
        self.calibrator = calibrator
    
    def generate_insights(self) -> List[Dict]:
        """Generate insights from collected data."""
        insights = []
        
        # Prediction accuracy insights
        accuracy_stats = self.collector.get_prediction_accuracy_stats()
        if accuracy_stats.get("sample_size", 0) >= 10:
            accuracy_rate = accuracy_stats.get("accuracy_rate", 0)
            
            if accuracy_rate < 0.3:
                insights.append({
                    "type": "prediction_quality",
                    "priority": "high",
                    "message": f"Prediction accuracy is low ({accuracy_rate*100:.0f}%)",
                    "recommendation": "Review prediction models and data sources",
                })
            elif accuracy_rate > 0.7:
                insights.append({
                    "type": "prediction_quality",
                    "priority": "info",
                    "message": f"Prediction accuracy is good ({accuracy_rate*100:.0f}%)",
                    "recommendation": "Continue current approach",
                })
        
        # Success rate insights
        success_stats = self.collector.get_success_rate()
        if success_stats.get("sample_size", 0) >= 5:
            success_rate = success_stats.get("success_rate", 0)
            
            if success_rate < 0.3:
                insights.append({
                    "type": "action_effectiveness",
                    "priority": "high",
                    "message": f"Only {success_rate*100:.0f}% of actions are succeeding",
                    "recommendation": "Re-evaluate action selection criteria",
                })
            elif success_rate > 0.6:
                insights.append({
                    "type": "action_effectiveness",
                    "priority": "info",
                    "message": f"{success_rate*100:.0f}% of actions are succeeding",
                    "recommendation": "Consider increasing auto-apply threshold",
                })
        
        # Calibration insights
        for metric_type, factor in self.calibrator.calibration_factors.items():
            if factor.factor < 0.7:
                insights.append({
                    "type": "calibration",
                    "priority": "medium",
                    "message": f"Systematically overestimating {metric_type.value} by {(1-factor.factor)*100:.0f}%",
                    "recommendation": f"Apply {factor.factor:.2f}x factor to {metric_type.value} predictions",
                })
            elif factor.factor > 1.3:
                insights.append({
                    "type": "calibration",
                    "priority": "medium",
                    "message": f"Systematically underestimating {metric_type.value} by {(factor.factor-1)*100:.0f}%",
                    "recommendation": f"Apply {factor.factor:.2f}x factor to {metric_type.value} predictions",
                })
        
        # Action type insights
        action_success_by_type = {}
        for outcome in self.collector.outcomes.values():
            atype = outcome.action_type
            if atype not in action_success_by_type:
                action_success_by_type[atype] = {"success": 0, "total": 0}
            action_success_by_type[atype]["total"] += 1
            if outcome.success:
                action_success_by_type[atype]["success"] += 1
        
        for atype, stats in action_success_by_type.items():
            if stats["total"] >= 3:
                rate = stats["success"] / stats["total"]
                if rate == 0:
                    insights.append({
                        "type": "action_type",
                        "priority": "high",
                        "message": f"'{atype}' actions have 0% success rate",
                        "recommendation": f"Pause or revise '{atype}' actions",
                    })
                elif rate == 1:
                    insights.append({
                        "type": "action_type",
                        "priority": "info",
                        "message": f"'{atype}' actions have 100% success rate",
                        "recommendation": f"Consider auto-applying '{atype}' actions",
                    })
        
        return insights


# ═══════════════════════════════════════════════════════════════════════════
# BLOG FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════════════════════

class BlogFeedbackLoop:
    """
    Orchestrates the complete blog feedback loop.
    
    1. Collect predictions when actions are created
    2. Track baselines before actions are applied
    3. Measure outcomes after actions are applied
    4. Calibrate predictions based on accuracy
    5. Generate insights
    """
    
    def __init__(self):
        self.collector = BlogFeedbackCollector()
        self.calibrator = BlogCalibrator(self.collector)
        self.insight_generator = BlogInsightGenerator(self.collector, self.calibrator)
    
    def record_action_prediction(
        self,
        action_id: str,
        action_type: str,
        page_url: str,
        predicted_changes: Dict[str, float],
        confidence: float,
        current_metrics: Dict[str, float],
    ):
        """Record predictions when an action is created."""
        for metric_name, predicted_change in predicted_changes.items():
            try:
                metric_type = MetricType(metric_name)
                current_value = current_metrics.get(metric_name, 0)
                
                # Apply calibration to prediction
                calibrated_change, cal_confidence = self.calibrator.get_calibrated_prediction(
                    metric_type, predicted_change
                )
                
                self.collector.record_prediction(
                    action_id=action_id,
                    action_type=action_type,
                    page_url=page_url,
                    metric_type=metric_type,
                    predicted_change=calibrated_change,
                    confidence=min(confidence, cal_confidence),
                    current_value=current_value,
                )
            except ValueError:
                pass  # Skip unknown metric types
    
    def record_baseline(self, page_url: str, metrics: Dict[str, float]):
        """Record baseline before an action."""
        self.collector.record_baseline(page_url, metrics)
    
    def record_outcome(
        self,
        action_id: str,
        action_type: str,
        page_url: str,
        after_metrics: Dict[str, float],
    ):
        """Record outcome after an action."""
        before_metrics = self.collector.baselines.get(page_url, {})
        
        self.collector.record_outcome(
            action_id=action_id,
            action_type=action_type,
            page_url=page_url,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
        )
    
    def run_cycle(self) -> Dict:
        """Run a complete feedback cycle."""
        
        # Recalibrate if needed
        if self.calibrator.should_recalibrate():
            self.calibrator.calibrate_all()
        
        # Generate insights
        insights = self.insight_generator.generate_insights()
        
        # Get stats
        accuracy_stats = self.collector.get_prediction_accuracy_stats()
        success_stats = self.collector.get_success_rate()
        calibration_status = self.calibrator.get_calibration_status()
        
        return {
            "accuracy": accuracy_stats,
            "success": success_stats,
            "calibration": calibration_status,
            "insights": insights,
            "predictions_count": len(self.collector.predictions),
            "outcomes_count": len(self.collector.outcomes),
        }
    
    def get_status(self) -> Dict:
        """Get current feedback loop status."""
        return {
            "predictions": len(self.collector.predictions),
            "outcomes": len(self.collector.outcomes),
            "baselines": len(self.collector.baselines),
            "calibration": self.calibrator.get_calibration_status(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_feedback_loop: Optional[BlogFeedbackLoop] = None

def get_blog_feedback_loop() -> BlogFeedbackLoop:
    """Get the global blog feedback loop."""
    global _feedback_loop
    if _feedback_loop is None:
        _feedback_loop = BlogFeedbackLoop()
    return _feedback_loop


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "MetricType",
    "PredictionAccuracy",
    "Prediction",
    "CalibrationFactor",
    "ActionOutcome",
    "BlogFeedbackCollector",
    "BlogCalibrator",
    "BlogInsightGenerator",
    "BlogFeedbackLoop",
    "get_blog_feedback_loop",
]
