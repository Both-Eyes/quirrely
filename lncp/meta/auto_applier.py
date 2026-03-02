#!/usr/bin/env python3
"""
QUIRRELY CLOSED-LOOP: AUTO-APPLIER v1.0
Automatically applies safe configuration changes with A/B testing and rollback.

This is the executor. It takes classified auto-apply actions
and carefully implements them with safeguards.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import hashlib

from .action_classifier import ClassifiedAction, ActionLane
from .config_store import ConfigStore, get_config_store, ConfigChange


# ═══════════════════════════════════════════════════════════════════════════
# EXPERIMENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    CONCLUDED = "concluded"
    ROLLED_BACK = "rolled_back"


class ExperimentResult(str, Enum):
    PENDING = "pending"
    WINNER_CONTROL = "winner_control"
    WINNER_VARIANT = "winner_variant"
    NO_DIFFERENCE = "no_difference"
    INCONCLUSIVE = "inconclusive"


@dataclass
class Experiment:
    """An A/B test experiment."""
    experiment_id: str
    action_id: str
    config_key: str
    
    control_value: any
    variant_value: any
    
    status: ExperimentStatus = ExperimentStatus.DRAFT
    result: ExperimentResult = ExperimentResult.PENDING
    
    # Traffic allocation
    variant_percentage: float = 0.50  # Start with 50/50
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    min_duration_hours: int = 24
    max_duration_hours: int = 168  # 7 days
    
    # Success criteria
    success_metric: str = "overall_health"
    success_threshold: float = 0.05  # 5% improvement required
    min_sample_size: int = 100
    
    # Results
    control_metric_value: Optional[float] = None
    variant_metric_value: Optional[float] = None
    control_sample_size: int = 0
    variant_sample_size: int = 0
    statistical_significance: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "experiment_id": self.experiment_id,
            "action_id": self.action_id,
            "config_key": self.config_key,
            "control_value": self.control_value,
            "variant_value": self.variant_value,
            "status": self.status.value,
            "result": self.result.value,
            "variant_percentage": self.variant_percentage,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "success_metric": self.success_metric,
            "control_metric_value": self.control_metric_value,
            "variant_metric_value": self.variant_metric_value,
        }


@dataclass 
class AppliedChange:
    """Record of an applied change."""
    change_id: str
    action_id: str
    config_key: str
    
    old_value: any
    new_value: any
    
    applied_at: datetime
    applied_via: str  # "direct", "experiment", "gradual"
    
    # Rollback info
    rollback_deadline: datetime
    rolled_back: bool = False
    rolled_back_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None
    
    # Impact tracking
    impact_metric: Optional[str] = None
    baseline_metric_value: Optional[float] = None
    current_metric_value: Optional[float] = None
    
    # Experiment reference
    experiment_id: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# AUTO-APPLIER
# ═══════════════════════════════════════════════════════════════════════════

class AutoApplier:
    """
    Automatically applies classified actions with safety mechanisms.
    
    Supports:
    - Direct application (for minimal risk changes)
    - A/B testing (for changes that need validation)
    - Gradual rollout (start small, increase if successful)
    - Automatic rollback (if metrics degrade)
    """
    
    def __init__(self, config_store: Optional[ConfigStore] = None):
        self.config_store = config_store or get_config_store()
        
        # Active experiments
        self.experiments: Dict[str, Experiment] = {}
        
        # Applied changes (for rollback tracking)
        self.applied_changes: List[AppliedChange] = []
        
        # Metrics collector (would connect to real metrics in production)
        self.metrics: Dict[str, float] = {}
    
    def apply(self, action: ClassifiedAction) -> Optional[AppliedChange]:
        """Apply a classified action."""
        if action.lane != ActionLane.AUTO_APPLY:
            raise ValueError(f"Cannot auto-apply action in lane: {action.lane}")
        
        if action.config_key is None:
            raise ValueError("Action has no config_key")
        
        # Determine application strategy
        if action.requires_ab_test:
            return self._apply_via_experiment(action)
        else:
            return self._apply_direct(action)
    
    def _apply_direct(self, action: ClassifiedAction) -> AppliedChange:
        """Apply change directly without A/B test."""
        # Get current value
        old_value = self.config_store.get(action.config_key)
        
        # Apply change
        change_record = self.config_store.set(
            key=action.config_key,
            value=action.proposed_value,
            source="auto",
            reason=f"Auto-applied: {action.title}",
            action_id=action.action_id,
        )
        
        # Record applied change
        applied = AppliedChange(
            change_id=f"change_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{action.action_id}",
            action_id=action.action_id,
            config_key=action.config_key,
            old_value=old_value,
            new_value=action.proposed_value,
            applied_at=datetime.utcnow(),
            applied_via="direct",
            rollback_deadline=datetime.utcnow() + timedelta(hours=action.rollback_window_hours),
            impact_metric=action.success_metric,
            baseline_metric_value=self._get_metric(action.success_metric),
        )
        self.applied_changes.append(applied)
        
        return applied
    
    def _apply_via_experiment(self, action: ClassifiedAction) -> AppliedChange:
        """Apply change via A/B test experiment."""
        # Create experiment
        experiment_id = f"exp_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{action.action_id}"
        
        experiment = Experiment(
            experiment_id=experiment_id,
            action_id=action.action_id,
            config_key=action.config_key,
            control_value=action.current_value,
            variant_value=action.proposed_value,
            success_metric=action.success_metric or "overall_health",
            success_threshold=action.success_threshold or 0.05,
        )
        
        # Start experiment
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        
        # Store experiment config
        self.config_store.set(
            key=action.config_key,
            value=action.proposed_value,
            source="auto",
            reason=f"Experiment variant: {action.title}",
            action_id=action.action_id,
            experiment_id=experiment_id,
        )
        
        self.experiments[experiment_id] = experiment
        
        # Record applied change
        applied = AppliedChange(
            change_id=f"change_{experiment_id}",
            action_id=action.action_id,
            config_key=action.config_key,
            old_value=action.current_value,
            new_value=action.proposed_value,
            applied_at=datetime.utcnow(),
            applied_via="experiment",
            rollback_deadline=datetime.utcnow() + timedelta(hours=action.rollback_window_hours),
            impact_metric=action.success_metric,
            baseline_metric_value=self._get_metric(action.success_metric),
            experiment_id=experiment_id,
        )
        self.applied_changes.append(applied)
        
        return applied
    
    def get_experiment_variant(
        self, 
        experiment_id: str, 
        user_id: str
    ) -> Tuple[str, any]:
        """Get the variant for a user in an experiment."""
        experiment = self.experiments.get(experiment_id)
        if not experiment or experiment.status != ExperimentStatus.RUNNING:
            return "control", experiment.control_value if experiment else None
        
        # Deterministic assignment based on user_id
        hash_input = f"{experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 100) / 100.0
        
        if bucket < experiment.variant_percentage:
            return "variant", experiment.variant_value
        else:
            return "control", experiment.control_value
    
    def record_experiment_metric(
        self,
        experiment_id: str,
        variant: str,
        metric_value: float,
    ):
        """Record a metric observation for an experiment."""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return
        
        if variant == "control":
            experiment.control_sample_size += 1
            # Running average
            if experiment.control_metric_value is None:
                experiment.control_metric_value = metric_value
            else:
                n = experiment.control_sample_size
                experiment.control_metric_value = (
                    experiment.control_metric_value * (n - 1) + metric_value
                ) / n
        else:
            experiment.variant_sample_size += 1
            if experiment.variant_metric_value is None:
                experiment.variant_metric_value = metric_value
            else:
                n = experiment.variant_sample_size
                experiment.variant_metric_value = (
                    experiment.variant_metric_value * (n - 1) + metric_value
                ) / n
    
    def evaluate_experiment(self, experiment_id: str) -> ExperimentResult:
        """Evaluate experiment results and decide winner."""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return ExperimentResult.INCONCLUSIVE
        
        # Check minimum sample size
        if experiment.control_sample_size < experiment.min_sample_size:
            return ExperimentResult.PENDING
        if experiment.variant_sample_size < experiment.min_sample_size:
            return ExperimentResult.PENDING
        
        # Check minimum duration
        if experiment.started_at:
            elapsed = datetime.utcnow() - experiment.started_at
            if elapsed < timedelta(hours=experiment.min_duration_hours):
                return ExperimentResult.PENDING
        
        # Compare metrics
        control = experiment.control_metric_value or 0
        variant = experiment.variant_metric_value or 0
        
        if control == 0:
            return ExperimentResult.INCONCLUSIVE
        
        improvement = (variant - control) / control
        
        if improvement >= experiment.success_threshold:
            experiment.result = ExperimentResult.WINNER_VARIANT
        elif improvement <= -experiment.success_threshold:
            experiment.result = ExperimentResult.WINNER_CONTROL
        else:
            experiment.result = ExperimentResult.NO_DIFFERENCE
        
        return experiment.result
    
    def conclude_experiment(self, experiment_id: str) -> bool:
        """Conclude an experiment and apply winner."""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return False
        
        result = self.evaluate_experiment(experiment_id)
        
        if result == ExperimentResult.PENDING:
            return False
        
        experiment.status = ExperimentStatus.CONCLUDED
        experiment.ended_at = datetime.utcnow()
        
        # Apply winner
        if result == ExperimentResult.WINNER_VARIANT:
            # Variant won - make it the global value
            self.config_store.set(
                key=experiment.config_key,
                value=experiment.variant_value,
                source="auto",
                reason=f"Experiment winner: variant improved by {((experiment.variant_metric_value or 0) / (experiment.control_metric_value or 1) - 1) * 100:.1f}%",
            )
            return True
        elif result == ExperimentResult.WINNER_CONTROL:
            # Control won - rollback to control
            self._rollback_change_by_experiment(experiment_id)
            return True
        else:
            # No difference - keep control (safer)
            self._rollback_change_by_experiment(experiment_id)
            return True
    
    def check_and_rollback_degraded(self, threshold: float = -0.10) -> List[AppliedChange]:
        """Check recent changes and rollback any that degraded metrics."""
        rolled_back = []
        
        for change in self.applied_changes:
            if change.rolled_back:
                continue
            
            if datetime.utcnow() > change.rollback_deadline:
                continue  # Past rollback window
            
            # Get current metric
            if change.impact_metric:
                current = self._get_metric(change.impact_metric)
                change.current_metric_value = current
                
                # Check for degradation
                if change.baseline_metric_value and current:
                    delta = (current - change.baseline_metric_value) / change.baseline_metric_value
                    
                    if delta < threshold:
                        # Metric degraded - rollback
                        self._rollback_change(change, f"Metric {change.impact_metric} degraded by {delta*100:.1f}%")
                        rolled_back.append(change)
        
        return rolled_back
    
    def _rollback_change(self, change: AppliedChange, reason: str):
        """Rollback a specific change."""
        self.config_store.set(
            key=change.config_key,
            value=change.old_value,
            source="rollback",
            reason=reason,
            action_id=change.action_id,
        )
        
        change.rolled_back = True
        change.rolled_back_at = datetime.utcnow()
        change.rollback_reason = reason
    
    def _rollback_change_by_experiment(self, experiment_id: str):
        """Rollback changes associated with an experiment."""
        for change in self.applied_changes:
            if change.experiment_id == experiment_id and not change.rolled_back:
                self._rollback_change(change, f"Experiment {experiment_id} concluded - control wins")
    
    def _get_metric(self, metric_name: str) -> Optional[float]:
        """Get current value of a metric."""
        # In production, this would query real metrics
        # For now, return simulated value
        return self.metrics.get(metric_name, random.uniform(0.8, 1.2))
    
    def set_metric(self, metric_name: str, value: float):
        """Set a metric value (for testing/simulation)."""
        self.metrics[metric_name] = value
    
    def get_status(self) -> Dict:
        """Get current status of auto-applier."""
        active_experiments = [
            e for e in self.experiments.values() 
            if e.status == ExperimentStatus.RUNNING
        ]
        
        pending_rollbacks = [
            c for c in self.applied_changes
            if not c.rolled_back and datetime.utcnow() < c.rollback_deadline
        ]
        
        return {
            "active_experiments": len(active_experiments),
            "pending_rollbacks": len(pending_rollbacks),
            "total_applied": len(self.applied_changes),
            "total_rolled_back": len([c for c in self.applied_changes if c.rolled_back]),
            "experiments": [e.to_dict() for e in active_experiments],
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_applier: Optional[AutoApplier] = None

def get_auto_applier() -> AutoApplier:
    """Get the global auto-applier instance."""
    global _applier
    if _applier is None:
        _applier = AutoApplier()
    return _applier


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from action_classifier import ActionClassifier, classify_actions
    
    # Sample action
    sample_action = {
        "action_id": "act_001",
        "title": "Adjust soft nudge threshold",
        "description": "Soft nudge appearing too early",
        "category": "funnel",
        "severity": "opportunity",
        "current_value": 0.80,
        "baseline_value": 0.75,
        "delta_percent": 6.7,
        "priority_score": 120,
        "funnel_stage": "nudge.soft_threshold",
    }
    
    # Classify
    classifier = ActionClassifier()
    classified = classifier.classify(sample_action)
    
    print("=" * 60)
    print("AUTO-APPLIER TEST")
    print("=" * 60)
    
    print(f"\nAction: {classified.title}")
    print(f"Lane: {classified.lane.value}")
    print(f"Requires A/B Test: {classified.requires_ab_test}")
    
    if classified.lane == ActionLane.AUTO_APPLY:
        applier = get_auto_applier()
        
        # Override config key for test
        classified.config_key = "funnel.nudge.soft_threshold"
        classified.proposed_value = 0.75
        
        applied = applier.apply(classified)
        
        print(f"\n✅ Applied!")
        print(f"   Change ID: {applied.change_id}")
        print(f"   Via: {applied.applied_via}")
        print(f"   Old: {applied.old_value} → New: {applied.new_value}")
        print(f"   Rollback deadline: {applied.rollback_deadline}")
        
        if applied.experiment_id:
            print(f"   Experiment: {applied.experiment_id}")
            
            # Simulate some metrics
            applier.record_experiment_metric(applied.experiment_id, "control", 0.85)
            applier.record_experiment_metric(applied.experiment_id, "variant", 0.92)
            
            print(f"\n   Simulated metrics recorded")
        
        print(f"\n--- APPLIER STATUS ---")
        status = applier.get_status()
        print(f"   Active experiments: {status['active_experiments']}")
        print(f"   Pending rollbacks: {status['pending_rollbacks']}")
        print(f"   Total applied: {status['total_applied']}")
    else:
        print(f"\n❌ Cannot auto-apply: {classified.classification_reason}")
