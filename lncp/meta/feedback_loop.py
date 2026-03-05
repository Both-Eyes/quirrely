#!/usr/bin/env python3
"""
QUIRRELY CLOSED-LOOP: FEEDBACK & CALIBRATION v1.0
Collects results, compares to predictions, and calibrates the system.

This is the learner. It watches what actually happens and
adjusts the system's understanding of itself.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics
import random


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK TYPES
# ═══════════════════════════════════════════════════════════════════════════

class FeedbackSource(str, Enum):
    SIMULATION = "simulation"
    REAL_METRICS = "real_metrics"
    EXPERIMENT = "experiment"
    MANUAL = "manual"


class CalibrationStatus(str, Enum):
    ACCURATE = "accurate"
    UNDERESTIMATING = "underestimating"
    OVERESTIMATING = "overestimating"
    UNSTABLE = "unstable"


@dataclass
class Observation:
    """A single observation of predicted vs actual."""
    timestamp: datetime
    metric_name: str
    predicted_value: float
    actual_value: float
    source: FeedbackSource
    context: Dict = field(default_factory=dict)
    
    @property
    def error(self) -> float:
        return self.actual_value - self.predicted_value
    
    @property
    def error_pct(self) -> float:
        if self.predicted_value == 0:
            return float('inf') if self.actual_value != 0 else 0
        return (self.actual_value - self.predicted_value) / self.predicted_value * 100
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "predicted_value": self.predicted_value,
            "actual_value": self.actual_value,
            "error": self.error,
            "error_pct": self.error_pct,
            "source": self.source.value,
        }


@dataclass
class CalibrationFactor:
    """Adjustment factor for a metric's predictions."""
    metric_name: str
    factor: float
    confidence: float
    sample_size: int
    last_updated: datetime
    status: CalibrationStatus
    
    def apply(self, predicted: float) -> float:
        return predicted * self.factor


@dataclass
class SystemCalibration:
    """Overall system calibration state."""
    factors: Dict[str, CalibrationFactor]
    overall_accuracy: float
    last_calibration: datetime
    observations_since_calibration: int
    
    def to_dict(self) -> Dict:
        return {
            "overall_accuracy": self.overall_accuracy,
            "last_calibration": self.last_calibration.isoformat(),
            "observations_since_calibration": self.observations_since_calibration,
            "factors": {
                name: {
                    "factor": f.factor,
                    "confidence": f.confidence,
                    "status": f.status.value,
                }
                for name, f in self.factors.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class FeedbackCollector:
    """Collects and stores feedback observations."""
    
    def __init__(self):
        self.observations: List[Observation] = []
        self.predictions: Dict[str, float] = {}
    
    def set_prediction(self, metric_name: str, value: float):
        self.predictions[metric_name] = value
    
    def record_actual(
        self,
        metric_name: str,
        actual_value: float,
        source: FeedbackSource = FeedbackSource.REAL_METRICS,
        context: Optional[Dict] = None,
    ) -> Observation:
        predicted = self.predictions.get(metric_name, actual_value)
        
        observation = Observation(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            predicted_value=predicted,
            actual_value=actual_value,
            source=source,
            context=context or {},
        )
        self.observations.append(observation)
        return observation
    
    def get_observations(
        self,
        metric_name: Optional[str] = None,
        source: Optional[FeedbackSource] = None,
        hours: Optional[int] = None,
    ) -> List[Observation]:
        obs = self.observations
        
        if metric_name:
            obs = [o for o in obs if o.metric_name == metric_name]
        if source:
            obs = [o for o in obs if o.source == source]
        if hours:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            obs = [o for o in obs if o.timestamp >= cutoff]
        
        return obs


# ═══════════════════════════════════════════════════════════════════════════
# CALIBRATOR
# ═══════════════════════════════════════════════════════════════════════════

class Calibrator:
    """Calibrates system predictions based on observed feedback."""
    
    def __init__(self, collector: FeedbackCollector):
        self.collector = collector
        self.calibration = SystemCalibration(
            factors={},
            overall_accuracy=1.0,
            last_calibration=datetime.utcnow(),
            observations_since_calibration=0,
        )
        self.min_observations_for_calibration = 10
        self.max_factor_change = 0.20
        self.recalibration_interval_hours = 24
    
    def calibrate_metric(self, metric_name: str) -> Optional[CalibrationFactor]:
        obs = self.collector.get_observations(metric_name=metric_name, hours=168)
        
        if len(obs) < self.min_observations_for_calibration:
            return None
        
        ratios = []
        for o in obs:
            if o.predicted_value != 0:
                ratios.append(o.actual_value / o.predicted_value)
        
        if not ratios:
            return None
        
        raw_factor = statistics.median(ratios)
        
        current_factor = self.calibration.factors.get(metric_name)
        if current_factor:
            max_delta = current_factor.factor * self.max_factor_change
            clamped_factor = max(
                current_factor.factor - max_delta,
                min(current_factor.factor + max_delta, raw_factor)
            )
        else:
            clamped_factor = raw_factor
        
        stdev = statistics.stdev(ratios) if len(ratios) > 1 else 0
        consistency = max(0, 1 - stdev)
        confidence = min(1.0, (len(ratios) / 50) * consistency)
        
        mean_error = statistics.mean([o.error_pct for o in obs])
        if abs(mean_error) < 5:
            status = CalibrationStatus.ACCURATE
        elif mean_error > 5:
            status = CalibrationStatus.UNDERESTIMATING
        elif mean_error < -5:
            status = CalibrationStatus.OVERESTIMATING
        else:
            status = CalibrationStatus.UNSTABLE if stdev > 0.3 else CalibrationStatus.ACCURATE
        
        factor = CalibrationFactor(
            metric_name=metric_name,
            factor=clamped_factor,
            confidence=confidence,
            sample_size=len(obs),
            last_updated=datetime.utcnow(),
            status=status,
        )
        
        self.calibration.factors[metric_name] = factor
        return factor
    
    def calibrate_all(self) -> SystemCalibration:
        metrics = set(o.metric_name for o in self.collector.observations)
        
        for metric in metrics:
            self.calibrate_metric(metric)
        
        if self.calibration.factors:
            accuracies = [1 - abs(1 - f.factor) for f in self.calibration.factors.values()]
            self.calibration.overall_accuracy = statistics.mean(accuracies)
        
        self.calibration.last_calibration = datetime.utcnow()
        self.calibration.observations_since_calibration = 0
        
        return self.calibration
    
    def should_recalibrate(self) -> bool:
        hours_since = (datetime.utcnow() - self.calibration.last_calibration).total_seconds() / 3600
        return hours_since >= self.recalibration_interval_hours
    
    def get_calibrated_prediction(self, metric_name: str, raw_prediction: float) -> Tuple[float, float]:
        factor = self.calibration.factors.get(metric_name)
        
        if factor:
            calibrated = raw_prediction * factor.factor
            confidence = factor.confidence
        else:
            calibrated = raw_prediction
            confidence = 0.5
        
        return calibrated, confidence


# ═══════════════════════════════════════════════════════════════════════════
# ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════════════════════

class AnomalyDetector:
    """Detects anomalies in metrics that might indicate problems."""
    
    def __init__(self, collector: FeedbackCollector):
        self.collector = collector
        self.baselines: Dict[str, Tuple[float, float]] = {}
        self.anomaly_threshold_sigma = 2.5
    
    def establish_baseline(self, metric_name: str, hours: int = 168):
        obs = self.collector.get_observations(metric_name=metric_name, hours=hours)
        
        if len(obs) < 10:
            return None
        
        values = [o.actual_value for o in obs]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        self.baselines[metric_name] = (mean, stdev)
        return {"mean": mean, "stdev": stdev}
    
    def check_anomaly(self, metric_name: str, value: float) -> Optional[Dict]:
        if metric_name not in self.baselines:
            return None
        
        mean, stdev = self.baselines[metric_name]
        
        if stdev == 0:
            return None
        
        z_score = (value - mean) / stdev
        
        if abs(z_score) > self.anomaly_threshold_sigma:
            return {
                "metric": metric_name,
                "value": value,
                "expected_mean": mean,
                "z_score": z_score,
                "direction": "high" if z_score > 0 else "low",
                "severity": "critical" if abs(z_score) > 4 else "warning",
            }
        
        return None
    
    def detect_all_anomalies(self) -> List[Dict]:
        anomalies = []
        recent = self.collector.get_observations(hours=24)
        
        for obs in recent:
            anomaly = self.check_anomaly(obs.metric_name, obs.actual_value)
            if anomaly:
                anomaly["timestamp"] = obs.timestamp.isoformat()
                anomalies.append(anomaly)
        
        return anomalies


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK LOOP ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class FeedbackLoop:
    """
    Orchestrates the full feedback loop:
    1. Collect observations
    2. Detect anomalies
    3. Calibrate predictions
    4. Generate insights
    """
    
    def __init__(self):
        self.collector = FeedbackCollector()
        self.calibrator = Calibrator(self.collector)
        self.anomaly_detector = AnomalyDetector(self.collector)
    
    def ingest_simulation_results(self, master_test_results: Dict):
        """Ingest results from a Master Test simulation."""
        sim = master_test_results.get("simulation_results", {})
        pulse = master_test_results.get("system_pulse", {})
        
        value_metrics = sim.get("value_metrics", {})
        churn_stats = sim.get("churn_stats", {})
        funnel_rates = sim.get("funnel_rates", {})
        
        if "mean_value" in value_metrics:
            self.collector.set_prediction("avg_user_value", value_metrics["mean_value"])
        if "churn_rate" in churn_stats:
            self.collector.set_prediction("churn_rate", churn_stats["churn_rate"])
        if "overall_health" in pulse:
            self.collector.set_prediction("overall_health", pulse["overall_health"])
        
        for stage, rate in funnel_rates.items():
            self.collector.set_prediction(f"funnel.{stage}", rate)
    
    def ingest_real_metrics(self, metrics: Dict[str, float]):
        """Ingest real production metrics."""
        for name, value in metrics.items():
            self.collector.record_actual(
                metric_name=name,
                actual_value=value,
                source=FeedbackSource.REAL_METRICS,
            )
    
    def run_cycle(self) -> Dict:
        """Run a full feedback cycle."""
        anomalies = self.anomaly_detector.detect_all_anomalies()
        
        calibration = None
        if self.calibrator.should_recalibrate():
            calibration = self.calibrator.calibrate_all()
        
        insights = self._generate_insights()
        
        return {
            "anomalies": anomalies,
            "calibration": calibration.to_dict() if calibration else None,
            "insights": insights,
            "observation_count": len(self.collector.observations),
        }
    
    def _generate_insights(self) -> List[Dict]:
        """Generate insights from feedback data."""
        insights = []
        
        for metric, factor in self.calibrator.calibration.factors.items():
            if factor.status == CalibrationStatus.UNDERESTIMATING:
                insights.append({
                    "type": "calibration",
                    "metric": metric,
                    "message": f"Simulation underestimates {metric} by {(factor.factor - 1) * 100:.1f}%",
                    "recommendation": "Adjust simulation parameters upward",
                })
            elif factor.status == CalibrationStatus.OVERESTIMATING:
                insights.append({
                    "type": "calibration",
                    "metric": metric,
                    "message": f"Simulation overestimates {metric} by {(1 - factor.factor) * 100:.1f}%",
                    "recommendation": "Adjust simulation parameters downward",
                })
        
        for metric, factor in self.calibrator.calibration.factors.items():
            if factor.confidence < 0.5:
                insights.append({
                    "type": "stability",
                    "metric": metric,
                    "message": f"{metric} shows high variance (confidence: {factor.confidence:.0%})",
                    "recommendation": "Investigate sources of variability",
                })
        
        return insights
    
    def get_status(self) -> Dict:
        """Get current status of feedback loop."""
        return {
            "observations": len(self.collector.observations),
            "metrics_tracked": len(set(o.metric_name for o in self.collector.observations)),
            "calibration": self.calibrator.calibration.to_dict(),
            "baselines_established": len(self.anomaly_detector.baselines),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_feedback_loop: Optional[FeedbackLoop] = None

def get_feedback_loop() -> FeedbackLoop:
    """Get the global feedback loop instance."""
    global _feedback_loop
    if _feedback_loop is None:
        _feedback_loop = FeedbackLoop()
    return _feedback_loop


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("FEEDBACK LOOP TEST")
    print("=" * 60)
    
    loop = FeedbackLoop()
    
    # Simulate ingesting Master Test predictions
    loop.collector.set_prediction("churn_rate", 0.05)
    loop.collector.set_prediction("avg_user_value", 2.93)
    loop.collector.set_prediction("overall_health", 86)
    
    # Simulate real metrics coming in (with some variance)
    print("\n--- SIMULATING REAL METRICS ---")
    for i in range(20):
        loop.collector.record_actual("churn_rate", 0.05 * random.uniform(0.7, 1.1))
        loop.collector.record_actual("avg_user_value", 2.93 * random.uniform(0.95, 1.15))
        loop.collector.record_actual("overall_health", 86 * random.uniform(0.98, 1.05))
    
    print(f"  Recorded {len(loop.collector.observations)} observations")
    
    # Establish baselines
    print("\n--- ESTABLISHING BASELINES ---")
    for metric in ["churn_rate", "avg_user_value", "overall_health"]:
        baseline = loop.anomaly_detector.establish_baseline(metric)
        if baseline:
            print(f"  {metric}: mean={baseline['mean']:.3f}, stdev={baseline['stdev']:.3f}")
    
    # Calibrate
    print("\n--- CALIBRATING ---")
    calibration = loop.calibrator.calibrate_all()
    print(f"  Overall accuracy: {calibration.overall_accuracy:.1%}")
    for metric, factor in calibration.factors.items():
        print(f"  {metric}: factor={factor.factor:.3f}, status={factor.status.value}")
    
    # Run full cycle
    print("\n--- RUNNING FEEDBACK CYCLE ---")
    result = loop.run_cycle()
    
    print(f"  Anomalies detected: {len(result['anomalies'])}")
    print(f"  Insights generated: {len(result['insights'])}")
    
    for insight in result['insights']:
        print(f"    • {insight['message']}")
    
    # Test calibrated prediction
    print("\n--- CALIBRATED PREDICTIONS ---")
    raw_prediction = 0.05
    calibrated, confidence = loop.calibrator.get_calibrated_prediction("churn_rate", raw_prediction)
    print(f"  Raw prediction: {raw_prediction}")
    print(f"  Calibrated: {calibrated:.4f} (confidence: {confidence:.0%})")
