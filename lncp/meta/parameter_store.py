#!/usr/bin/env python3
"""
LNCP META: PARAMETER STORE v4.1
Centralized store for ALL Meta parameters, separate from code.

This makes Meta's behavior auditable and tunable without deployment.
Every parameter has boundaries, history, and change tracking.

Key principle: Code defines WHAT can change and HOW.
Parameters define the ACTUAL VALUES at runtime.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import json
import copy


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ParameterType(str, Enum):
    """Types of parameters."""
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    LIST = "list"
    DICT = "dict"


class ParameterCategory(str, Enum):
    """Categories of parameters."""
    # Classification
    CLASSIFICATION_THRESHOLD = "classification_threshold"
    CONFIDENCE_REQUIREMENT = "confidence_requirement"
    RISK_WEIGHT = "risk_weight"
    
    # Execution
    AB_TEST_CONFIG = "ab_test_config"
    AUTO_APPLY_LIMIT = "auto_apply_limit"
    ROLLBACK_TRIGGER = "rollback_trigger"
    
    # Learning
    CALIBRATION_FACTOR = "calibration_factor"
    LEARNING_RATE = "learning_rate"
    MEMORY_DECAY = "memory_decay"
    
    # Health
    HEALTH_WEIGHT = "health_weight"
    HEALTH_THRESHOLD = "health_threshold"
    
    # Trust
    TRUST_INCREMENT = "trust_increment"
    TRUST_DECREMENT = "trust_decrement"
    TRUST_THRESHOLD = "trust_threshold"


class ChangeSource(str, Enum):
    """Who/what made the change."""
    SYSTEM_INIT = "system_init"           # Initial value
    SUPER_ADMIN = "super_admin"           # Human override
    AUTO_CALIBRATION = "auto_calibration" # Self-calibration
    PROPOSAL_APPROVED = "proposal_approved"  # Approved proposal
    ROLLBACK = "rollback"                 # Reverted change


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER DEFINITION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ParameterBoundary:
    """Defines the safe boundaries for a parameter."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    
    # Auto-calibration boundaries (tighter than absolute)
    auto_min: Optional[float] = None
    auto_max: Optional[float] = None
    
    # Change rate limits
    max_change_per_cycle: Optional[float] = None  # Max % change per cycle
    max_change_per_day: Optional[float] = None    # Max % change per day


@dataclass
class ParameterDefinition:
    """
    Complete definition of a tunable parameter.
    
    This is the "schema" for a parameter - what it is, what it can be.
    """
    # Identity
    key: str
    name: str
    description: str
    category: ParameterCategory
    param_type: ParameterType
    
    # Default and boundaries
    default_value: Any
    boundaries: ParameterBoundary
    
    # Control
    requires_super_admin: bool = False   # Only Super Admin can change
    can_auto_calibrate: bool = True      # Meta can self-adjust
    requires_ab_test: bool = False       # Changes must be A/B tested
    
    # Impact
    impact_scope: str = "local"          # "local", "domain", "system"
    reversible: bool = True


@dataclass
class ParameterChange:
    """Record of a parameter change."""
    parameter_key: str
    old_value: Any
    new_value: Any
    changed_at: datetime
    source: ChangeSource
    reason: str
    
    # Context
    cycle_id: Optional[str] = None
    proposal_id: Optional[str] = None
    approved_by: Optional[str] = None
    
    # Validation
    was_within_bounds: bool = True
    was_within_auto_bounds: bool = True


@dataclass
class ParameterState:
    """Current state of a parameter."""
    key: str
    current_value: Any
    last_changed: datetime
    change_count: int = 0
    
    # Recent history
    changes_today: int = 0
    total_change_today_pct: float = 0.0
    
    # Performance
    value_at_best_performance: Optional[Any] = None
    best_performance_metric: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════════════
# META PARAMETER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

# All Meta parameters defined here
META_PARAMETERS: Dict[str, ParameterDefinition] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # CLASSIFICATION PARAMETERS
    # ─────────────────────────────────────────────────────────────────────
    
    "classification.confidence_threshold.auto_apply": ParameterDefinition(
        key="classification.confidence_threshold.auto_apply",
        name="Auto-Apply Confidence Threshold",
        description="Minimum confidence required for auto-apply lane",
        category=ParameterCategory.CONFIDENCE_REQUIREMENT,
        param_type=ParameterType.FLOAT,
        default_value=0.85,
        boundaries=ParameterBoundary(
            min_value=0.5, max_value=0.99,
            auto_min=0.75, auto_max=0.95,
            max_change_per_cycle=0.05,
        ),
        can_auto_calibrate=True,
    ),
    
    "classification.confidence_threshold.review": ParameterDefinition(
        key="classification.confidence_threshold.review",
        name="Review Confidence Threshold",
        description="Minimum confidence required for review lane (vs super admin)",
        category=ParameterCategory.CONFIDENCE_REQUIREMENT,
        param_type=ParameterType.FLOAT,
        default_value=0.60,
        boundaries=ParameterBoundary(
            min_value=0.3, max_value=0.85,
            auto_min=0.50, auto_max=0.75,
            max_change_per_cycle=0.05,
        ),
        can_auto_calibrate=True,
    ),
    
    "classification.risk_weight.user_impact": ParameterDefinition(
        key="classification.risk_weight.user_impact",
        name="User Impact Risk Weight",
        description="Weight of user impact in risk calculation",
        category=ParameterCategory.RISK_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.30,
        boundaries=ParameterBoundary(
            min_value=0.1, max_value=0.5,
            auto_min=0.2, auto_max=0.4,
        ),
        can_auto_calibrate=True,
    ),
    
    "classification.risk_weight.revenue_impact": ParameterDefinition(
        key="classification.risk_weight.revenue_impact",
        name="Revenue Impact Risk Weight",
        description="Weight of revenue impact in risk calculation",
        category=ParameterCategory.RISK_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.35,
        boundaries=ParameterBoundary(
            min_value=0.2, max_value=0.6,
            auto_min=0.25, auto_max=0.45,
        ),
        can_auto_calibrate=True,
    ),
    
    "classification.risk_weight.reversibility": ParameterDefinition(
        key="classification.risk_weight.reversibility",
        name="Reversibility Risk Weight",
        description="Weight of reversibility in risk calculation",
        category=ParameterCategory.RISK_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.20,
        boundaries=ParameterBoundary(
            min_value=0.1, max_value=0.4,
            auto_min=0.15, auto_max=0.30,
        ),
        can_auto_calibrate=True,
    ),
    
    "classification.risk_weight.precedent": ParameterDefinition(
        key="classification.risk_weight.precedent",
        name="Precedent Risk Weight",
        description="Weight of historical precedent in risk calculation",
        category=ParameterCategory.RISK_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.15,
        boundaries=ParameterBoundary(
            min_value=0.05, max_value=0.3,
            auto_min=0.10, auto_max=0.25,
        ),
        can_auto_calibrate=True,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # EXECUTION PARAMETERS
    # ─────────────────────────────────────────────────────────────────────
    
    "execution.auto_apply.max_per_cycle": ParameterDefinition(
        key="execution.auto_apply.max_per_cycle",
        name="Max Auto-Apply Per Cycle",
        description="Maximum actions to auto-apply in one cycle",
        category=ParameterCategory.AUTO_APPLY_LIMIT,
        param_type=ParameterType.INT,
        default_value=10,
        boundaries=ParameterBoundary(
            min_value=1, max_value=50,
            auto_min=5, auto_max=25,
        ),
        can_auto_calibrate=True,
    ),
    
    "execution.auto_apply.max_per_day": ParameterDefinition(
        key="execution.auto_apply.max_per_day",
        name="Max Auto-Apply Per Day",
        description="Maximum actions to auto-apply in one day",
        category=ParameterCategory.AUTO_APPLY_LIMIT,
        param_type=ParameterType.INT,
        default_value=50,
        boundaries=ParameterBoundary(
            min_value=10, max_value=200,
            auto_min=25, auto_max=100,
        ),
        can_auto_calibrate=True,
    ),
    
    "execution.ab_test.min_duration_days": ParameterDefinition(
        key="execution.ab_test.min_duration_days",
        name="Minimum A/B Test Duration",
        description="Minimum days before concluding A/B test",
        category=ParameterCategory.AB_TEST_CONFIG,
        param_type=ParameterType.INT,
        default_value=7,
        boundaries=ParameterBoundary(
            min_value=3, max_value=30,
            auto_min=5, auto_max=14,
        ),
        can_auto_calibrate=True,
    ),
    
    "execution.ab_test.significance_threshold": ParameterDefinition(
        key="execution.ab_test.significance_threshold",
        name="A/B Test Significance Threshold",
        description="Statistical significance required to conclude test",
        category=ParameterCategory.AB_TEST_CONFIG,
        param_type=ParameterType.FLOAT,
        default_value=0.95,
        boundaries=ParameterBoundary(
            min_value=0.80, max_value=0.99,
            auto_min=0.90, auto_max=0.98,
        ),
        can_auto_calibrate=True,
    ),
    
    "execution.rollback.health_drop_threshold": ParameterDefinition(
        key="execution.rollback.health_drop_threshold",
        name="Rollback Health Drop Threshold",
        description="Health drop % that triggers automatic rollback",
        category=ParameterCategory.ROLLBACK_TRIGGER,
        param_type=ParameterType.FLOAT,
        default_value=10.0,
        boundaries=ParameterBoundary(
            min_value=3.0, max_value=25.0,
            auto_min=5.0, auto_max=15.0,
        ),
        can_auto_calibrate=True,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # LEARNING PARAMETERS
    # ─────────────────────────────────────────────────────────────────────
    
    "learning.calibration.update_rate": ParameterDefinition(
        key="learning.calibration.update_rate",
        name="Calibration Update Rate",
        description="How quickly calibration factors adjust (0-1)",
        category=ParameterCategory.LEARNING_RATE,
        param_type=ParameterType.FLOAT,
        default_value=0.1,
        boundaries=ParameterBoundary(
            min_value=0.01, max_value=0.5,
            auto_min=0.05, auto_max=0.25,
        ),
        can_auto_calibrate=True,
    ),
    
    "learning.memory.outcome_retention_days": ParameterDefinition(
        key="learning.memory.outcome_retention_days",
        name="Outcome Retention Days",
        description="Days to retain outcome data for learning",
        category=ParameterCategory.MEMORY_DECAY,
        param_type=ParameterType.INT,
        default_value=90,
        boundaries=ParameterBoundary(
            min_value=30, max_value=365,
            auto_min=60, auto_max=180,
        ),
        can_auto_calibrate=False,
    ),
    
    "learning.memory.prediction_weight_decay": ParameterDefinition(
        key="learning.memory.prediction_weight_decay",
        name="Prediction Weight Decay",
        description="Daily decay rate for old prediction weights",
        category=ParameterCategory.MEMORY_DECAY,
        param_type=ParameterType.FLOAT,
        default_value=0.99,
        boundaries=ParameterBoundary(
            min_value=0.90, max_value=1.0,
            auto_min=0.95, auto_max=0.995,
        ),
        can_auto_calibrate=True,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH PARAMETERS
    # ─────────────────────────────────────────────────────────────────────
    
    "health.weight.app": ParameterDefinition(
        key="health.weight.app",
        name="App Health Weight",
        description="Weight of app health in system health",
        category=ParameterCategory.HEALTH_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.40,
        boundaries=ParameterBoundary(
            min_value=0.2, max_value=0.6,
            auto_min=0.30, auto_max=0.50,
        ),
        can_auto_calibrate=True,
    ),
    
    "health.weight.blog": ParameterDefinition(
        key="health.weight.blog",
        name="Blog Health Weight",
        description="Weight of blog health in system health",
        category=ParameterCategory.HEALTH_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.20,
        boundaries=ParameterBoundary(
            min_value=0.1, max_value=0.4,
            auto_min=0.15, auto_max=0.30,
        ),
        can_auto_calibrate=True,
    ),
    
    "health.weight.revenue": ParameterDefinition(
        key="health.weight.revenue",
        name="Revenue Health Weight",
        description="Weight of revenue health in system health",
        category=ParameterCategory.HEALTH_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.30,
        boundaries=ParameterBoundary(
            min_value=0.2, max_value=0.5,
            auto_min=0.25, auto_max=0.40,
        ),
        can_auto_calibrate=True,
    ),
    
    "health.weight.meta_accuracy": ParameterDefinition(
        key="health.weight.meta_accuracy",
        name="Meta Accuracy Health Weight",
        description="Weight of Meta prediction accuracy in system health",
        category=ParameterCategory.HEALTH_WEIGHT,
        param_type=ParameterType.FLOAT,
        default_value=0.10,
        boundaries=ParameterBoundary(
            min_value=0.05, max_value=0.2,
            auto_min=0.08, auto_max=0.15,
        ),
        can_auto_calibrate=True,
    ),
    
    "health.threshold.safe_for_auto": ParameterDefinition(
        key="health.threshold.safe_for_auto",
        name="Safe Health Threshold",
        description="Minimum system health for auto-apply",
        category=ParameterCategory.HEALTH_THRESHOLD,
        param_type=ParameterType.FLOAT,
        default_value=70.0,
        boundaries=ParameterBoundary(
            min_value=50.0, max_value=90.0,
            auto_min=60.0, auto_max=80.0,
        ),
        can_auto_calibrate=True,
    ),
    
    "health.threshold.pause_all": ParameterDefinition(
        key="health.threshold.pause_all",
        name="Pause All Health Threshold",
        description="System health below which all changes pause",
        category=ParameterCategory.HEALTH_THRESHOLD,
        param_type=ParameterType.FLOAT,
        default_value=50.0,
        boundaries=ParameterBoundary(
            min_value=30.0, max_value=70.0,
            auto_min=40.0, auto_max=60.0,
        ),
        can_auto_calibrate=False,
        requires_super_admin=True,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # TRUST PARAMETERS
    # ─────────────────────────────────────────────────────────────────────
    
    "trust.increment.success": ParameterDefinition(
        key="trust.increment.success",
        name="Trust Increment on Success",
        description="Trust points gained on successful action",
        category=ParameterCategory.TRUST_INCREMENT,
        param_type=ParameterType.INT,
        default_value=1,
        boundaries=ParameterBoundary(
            min_value=1, max_value=5,
            auto_min=1, auto_max=3,
        ),
        can_auto_calibrate=True,
    ),
    
    "trust.decrement.failure": ParameterDefinition(
        key="trust.decrement.failure",
        name="Trust Decrement on Failure",
        description="Trust points lost on failed action",
        category=ParameterCategory.TRUST_DECREMENT,
        param_type=ParameterType.INT,
        default_value=3,
        boundaries=ParameterBoundary(
            min_value=1, max_value=10,
            auto_min=2, auto_max=5,
        ),
        can_auto_calibrate=True,
    ),
    
    "trust.threshold.auto_apply": ParameterDefinition(
        key="trust.threshold.auto_apply",
        name="Auto-Apply Trust Threshold",
        description="Trust score required for action type to auto-apply",
        category=ParameterCategory.TRUST_THRESHOLD,
        param_type=ParameterType.INT,
        default_value=10,
        boundaries=ParameterBoundary(
            min_value=5, max_value=50,
            auto_min=8, auto_max=20,
        ),
        can_auto_calibrate=True,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER STORE
# ═══════════════════════════════════════════════════════════════════════════

class MetaParameterStore:
    """
    Centralized store for all Meta parameters.
    
    - All parameters defined in code (schema)
    - All values stored here (runtime)
    - All changes tracked (audit)
    - All boundaries enforced (safety)
    """
    
    def __init__(self):
        self.definitions: Dict[str, ParameterDefinition] = META_PARAMETERS
        self.state: Dict[str, ParameterState] = {}
        self.history: List[ParameterChange] = []
        
        # Initialize all parameters to defaults
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize all parameters to their default values."""
        now = datetime.utcnow()
        for key, definition in self.definitions.items():
            self.state[key] = ParameterState(
                key=key,
                current_value=definition.default_value,
                last_changed=now,
            )
    
    # ─────────────────────────────────────────────────────────────────────
    # GET/SET
    # ─────────────────────────────────────────────────────────────────────
    
    def get(self, key: str) -> Any:
        """Get current value of a parameter."""
        if key not in self.state:
            raise KeyError(f"Unknown parameter: {key}")
        return self.state[key].current_value
    
    def get_with_metadata(self, key: str) -> Tuple[Any, ParameterDefinition, ParameterState]:
        """Get value with full metadata."""
        if key not in self.state:
            raise KeyError(f"Unknown parameter: {key}")
        return (
            self.state[key].current_value,
            self.definitions[key],
            self.state[key],
        )
    
    def set(
        self,
        key: str,
        value: Any,
        source: ChangeSource,
        reason: str,
        cycle_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
        approved_by: Optional[str] = None,
        force: bool = False,
    ) -> Tuple[bool, str]:
        """
        Set a parameter value.
        
        Returns (success, message).
        """
        if key not in self.definitions:
            return False, f"Unknown parameter: {key}"
        
        definition = self.definitions[key]
        state = self.state[key]
        old_value = state.current_value
        
        # Check if Super Admin required
        if definition.requires_super_admin and source != ChangeSource.SUPER_ADMIN:
            return False, f"Parameter {key} requires Super Admin"
        
        # Check boundaries
        within_bounds = self._check_boundaries(value, definition.boundaries)
        within_auto = self._check_auto_boundaries(value, definition.boundaries)
        
        if not within_bounds and not force:
            return False, f"Value {value} outside boundaries for {key}"
        
        if source == ChangeSource.AUTO_CALIBRATION and not within_auto:
            return False, f"Auto-calibration value {value} outside auto boundaries for {key}"
        
        # Check rate limits
        if not self._check_rate_limits(key, old_value, value, definition.boundaries):
            return False, f"Change rate limit exceeded for {key}"
        
        # Apply change
        state.current_value = value
        state.last_changed = datetime.utcnow()
        state.change_count += 1
        state.changes_today += 1
        
        if old_value != 0:
            state.total_change_today_pct += abs((value - old_value) / old_value) * 100
        
        # Record history
        change = ParameterChange(
            parameter_key=key,
            old_value=old_value,
            new_value=value,
            changed_at=datetime.utcnow(),
            source=source,
            reason=reason,
            cycle_id=cycle_id,
            proposal_id=proposal_id,
            approved_by=approved_by,
            was_within_bounds=within_bounds,
            was_within_auto_bounds=within_auto,
        )
        self.history.append(change)
        
        return True, f"Parameter {key} updated from {old_value} to {value}"
    
    def _check_boundaries(self, value: Any, boundaries: ParameterBoundary) -> bool:
        """Check if value is within absolute boundaries."""
        if boundaries.allowed_values is not None:
            return value in boundaries.allowed_values
        
        if boundaries.min_value is not None and value < boundaries.min_value:
            return False
        if boundaries.max_value is not None and value > boundaries.max_value:
            return False
        
        return True
    
    def _check_auto_boundaries(self, value: Any, boundaries: ParameterBoundary) -> bool:
        """Check if value is within auto-calibration boundaries."""
        if boundaries.auto_min is not None and value < boundaries.auto_min:
            return False
        if boundaries.auto_max is not None and value > boundaries.auto_max:
            return False
        return True
    
    def _check_rate_limits(
        self,
        key: str,
        old_value: Any,
        new_value: Any,
        boundaries: ParameterBoundary,
    ) -> bool:
        """Check if change rate is within limits."""
        if old_value == 0:
            return True
        
        change_pct = abs((new_value - old_value) / old_value) * 100
        
        if boundaries.max_change_per_cycle is not None:
            if change_pct > boundaries.max_change_per_cycle * 100:
                return False
        
        # Check daily limit
        state = self.state[key]
        if boundaries.max_change_per_day is not None:
            total_today = state.total_change_today_pct + change_pct
            if total_today > boundaries.max_change_per_day * 100:
                return False
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_all(self) -> Dict[str, Any]:
        """Get all current values."""
        return {key: state.current_value for key, state in self.state.items()}
    
    def get_by_category(self, category: ParameterCategory) -> Dict[str, Any]:
        """Get all parameters in a category."""
        return {
            key: self.state[key].current_value
            for key, definition in self.definitions.items()
            if definition.category == category
        }
    
    def get_auto_calibratable(self) -> List[str]:
        """Get keys of all auto-calibratable parameters."""
        return [
            key for key, definition in self.definitions.items()
            if definition.can_auto_calibrate
        ]
    
    def get_recent_changes(self, hours: int = 24) -> List[ParameterChange]:
        """Get recent parameter changes."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [c for c in self.history if c.changed_at >= cutoff]
    
    def get_change_history(self, key: str, limit: int = 10) -> List[ParameterChange]:
        """Get change history for a specific parameter."""
        changes = [c for c in self.history if c.parameter_key == key]
        return sorted(changes, key=lambda c: c.changed_at, reverse=True)[:limit]
    
    def get_audit_summary(self) -> Dict:
        """Get summary for audit purposes."""
        return {
            "total_parameters": len(self.definitions),
            "total_changes": len(self.history),
            "changes_last_24h": len(self.get_recent_changes(24)),
            "auto_calibratable": len(self.get_auto_calibratable()),
            "super_admin_only": sum(
                1 for d in self.definitions.values() if d.requires_super_admin
            ),
            "by_category": {
                cat.value: len([
                    d for d in self.definitions.values() if d.category == cat
                ])
                for cat in ParameterCategory
            },
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # DAILY RESET
    # ─────────────────────────────────────────────────────────────────────
    
    def reset_daily_counters(self):
        """Reset daily change counters (call at start of each day)."""
        for state in self.state.values():
            state.changes_today = 0
            state.total_change_today_pct = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_parameter_store: Optional[MetaParameterStore] = None

def get_parameter_store() -> MetaParameterStore:
    """Get the global parameter store instance."""
    global _parameter_store
    if _parameter_store is None:
        _parameter_store = MetaParameterStore()
    return _parameter_store


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "ParameterType",
    "ParameterCategory",
    "ChangeSource",
    "ParameterBoundary",
    "ParameterDefinition",
    "ParameterChange",
    "ParameterState",
    "META_PARAMETERS",
    "MetaParameterStore",
    "get_parameter_store",
]
