#!/usr/bin/env python3
"""
QUIRRELY CLOSED-LOOP: CONFIG STORE v1.0
Centralized store for all tunable system parameters.

Every parameter that the system can auto-adjust lives here.
All changes are versioned, audited, and reversible.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import copy


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ConfigType(str, Enum):
    """Type of configuration value."""
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"  # 0.0 to 1.0
    BOOLEAN = "boolean"
    STRING = "string"
    DURATION_SECONDS = "duration_seconds"
    DURATION_DAYS = "duration_days"


class ConfigScope(str, Enum):
    """Scope of the configuration."""
    GLOBAL = "global"           # Applies everywhere
    COUNTRY = "country"         # Per-country override
    TIER = "tier"               # Per-subscription tier
    EXPERIMENT = "experiment"   # A/B test variant


@dataclass
class ConfigChange:
    """Record of a configuration change."""
    timestamp: datetime
    key: str
    old_value: Any
    new_value: Any
    change_source: str  # "auto", "human", "rollback", "experiment"
    change_reason: str
    action_id: Optional[str] = None
    experiment_id: Optional[str] = None
    rollback_of: Optional[str] = None  # ID of change this rolls back
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_source": self.change_source,
            "change_reason": self.change_reason,
            "action_id": self.action_id,
            "experiment_id": self.experiment_id,
            "rollback_of": self.rollback_of,
        }


@dataclass
class ConfigDefinition:
    """Definition of a configurable parameter."""
    key: str
    name: str
    description: str
    config_type: ConfigType
    default_value: Any
    
    # Constraints
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    
    # Metadata
    scope: ConfigScope = ConfigScope.GLOBAL
    auto_adjustable: bool = True
    requires_ab_test: bool = False
    rollback_window_hours: int = 24
    
    # Related metrics
    impact_metric: Optional[str] = None
    expected_direction: Optional[str] = None  # "increase", "decrease"


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

CONFIG_DEFINITIONS: Dict[str, ConfigDefinition] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # FUNNEL THRESHOLDS
    # ─────────────────────────────────────────────────────────────────────
    
    "funnel.nudge.soft_threshold": ConfigDefinition(
        key="funnel.nudge.soft_threshold",
        name="Soft Nudge Threshold",
        description="Percentage of word limit at which soft nudge appears",
        config_type=ConfigType.PERCENTAGE,
        default_value=0.80,
        min_value=0.50,
        max_value=0.95,
        auto_adjustable=True,
        impact_metric="trial_start_rate",
        expected_direction="increase",
    ),
    
    "funnel.nudge.medium_threshold": ConfigDefinition(
        key="funnel.nudge.medium_threshold",
        name="Medium Nudge Threshold",
        description="Percentage of word limit at which medium nudge appears",
        config_type=ConfigType.PERCENTAGE,
        default_value=0.95,
        min_value=0.80,
        max_value=0.99,
        auto_adjustable=True,
        impact_metric="trial_start_rate",
        expected_direction="increase",
    ),
    
    "funnel.trial.duration_days": ConfigDefinition(
        key="funnel.trial.duration_days",
        name="Trial Duration",
        description="Number of days for free trial",
        config_type=ConfigType.DURATION_DAYS,
        default_value=7,
        min_value=3,
        max_value=14,
        auto_adjustable=False,  # Changing trial length needs human review
        requires_ab_test=True,
        impact_metric="trial_conversion_rate",
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # ENGAGEMENT / STREAKS
    # ─────────────────────────────────────────────────────────────────────
    
    "engagement.streak.grace_days": ConfigDefinition(
        key="engagement.streak.grace_days",
        name="Streak Grace Days",
        description="Number of grace days allowed per streak period",
        config_type=ConfigType.INTEGER,
        default_value=1,
        min_value=0,
        max_value=2,
        auto_adjustable=True,
        impact_metric="streak_continuation_rate",
        expected_direction="increase",
    ),
    
    "engagement.streak.period_days": ConfigDefinition(
        key="engagement.streak.period_days",
        name="Streak Period",
        description="Number of days in a streak period for grace calculation",
        config_type=ConfigType.INTEGER,
        default_value=7,
        min_value=5,
        max_value=14,
        auto_adjustable=True,
        impact_metric="streak_continuation_rate",
    ),
    
    "engagement.daily_active.reminder_hour": ConfigDefinition(
        key="engagement.daily_active.reminder_hour",
        name="Daily Reminder Hour",
        description="Hour of day (UTC) to send streak reminder",
        config_type=ConfigType.INTEGER,
        default_value=18,
        min_value=6,
        max_value=22,
        auto_adjustable=True,
        impact_metric="daily_active_rate",
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # FEATURED WRITER
    # ─────────────────────────────────────────────────────────────────────
    
    "featured.eligibility.min_streak": ConfigDefinition(
        key="featured.eligibility.min_streak",
        name="Featured Min Streak",
        description="Minimum streak days required for Featured eligibility",
        config_type=ConfigType.INTEGER,
        default_value=7,
        min_value=3,
        max_value=14,
        auto_adjustable=True,
        requires_ab_test=True,
        impact_metric="featured_submission_rate",
    ),
    
    "featured.eligibility.min_words": ConfigDefinition(
        key="featured.eligibility.min_words",
        name="Featured Min Words",
        description="Minimum total words analyzed for Featured eligibility",
        config_type=ConfigType.INTEGER,
        default_value=7000,
        min_value=3000,
        max_value=15000,
        auto_adjustable=True,
        impact_metric="featured_submission_rate",
    ),
    
    "featured.eligibility.min_active_days": ConfigDefinition(
        key="featured.eligibility.min_active_days",
        name="Featured Min Active Days",
        description="Minimum active days for Featured eligibility",
        config_type=ConfigType.INTEGER,
        default_value=14,
        min_value=7,
        max_value=30,
        auto_adjustable=True,
        impact_metric="featured_submission_rate",
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # COPY / MESSAGING
    # ─────────────────────────────────────────────────────────────────────
    
    "copy.trial_cta.primary": ConfigDefinition(
        key="copy.trial_cta.primary",
        name="Trial CTA Text",
        description="Primary call-to-action text for trial signup",
        config_type=ConfigType.STRING,
        default_value="Start Free Trial",
        allowed_values=[
            "Start Free Trial",
            "Start Free Trial →",
            "Try Free for 7 Days",
            "Unlock Full Access",
            "Continue Writing →",
        ],
        auto_adjustable=True,
        requires_ab_test=True,
        impact_metric="trial_start_rate",
    ),
    
    "copy.limit_reached.title": ConfigDefinition(
        key="copy.limit_reached.title",
        name="Limit Reached Title",
        description="Title shown when user hits word limit",
        config_type=ConfigType.STRING,
        default_value="You've discovered your voice!",
        auto_adjustable=True,
        requires_ab_test=True,
        impact_metric="trial_start_rate",
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # CHURN PREVENTION
    # ─────────────────────────────────────────────────────────────────────
    
    "churn.inactive_days_warning": ConfigDefinition(
        key="churn.inactive_days_warning",
        name="Inactive Days Before Warning",
        description="Days of inactivity before sending re-engagement email",
        config_type=ConfigType.INTEGER,
        default_value=5,
        min_value=3,
        max_value=14,
        auto_adjustable=True,
        impact_metric="churn_rate",
        expected_direction="decrease",
    ),
    
    "churn.inactive_days_urgent": ConfigDefinition(
        key="churn.inactive_days_urgent",
        name="Inactive Days Before Urgent",
        description="Days of inactivity before urgent re-engagement",
        config_type=ConfigType.INTEGER,
        default_value=10,
        min_value=7,
        max_value=21,
        auto_adjustable=True,
        impact_metric="churn_rate",
        expected_direction="decrease",
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # SOCIAL PROOF
    # ─────────────────────────────────────────────────────────────────────
    
    "social_proof.show_trial_count": ConfigDefinition(
        key="social_proof.show_trial_count",
        name="Show Trial Count",
        description="Whether to show 'X writers started today' social proof",
        config_type=ConfigType.BOOLEAN,
        default_value=True,
        auto_adjustable=True,
        impact_metric="trial_start_rate",
    ),
    
    "social_proof.trial_count_base": ConfigDefinition(
        key="social_proof.trial_count_base",
        name="Trial Count Base",
        description="Base number for social proof (randomized around this)",
        config_type=ConfigType.INTEGER,
        default_value=120,
        min_value=50,
        max_value=500,
        auto_adjustable=True,
        impact_metric="trial_start_rate",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG STORE
# ═══════════════════════════════════════════════════════════════════════════

class ConfigStore:
    """
    Centralized store for all tunable configuration.
    
    Features:
    - Versioned changes with full audit trail
    - Country-specific overrides
    - A/B test variants
    - Instant rollback capability
    """
    
    def __init__(self):
        # Current values (key -> value)
        self._values: Dict[str, Any] = {}
        
        # Country overrides (country_code -> key -> value)
        self._country_overrides: Dict[str, Dict[str, Any]] = {}
        
        # Active experiments (experiment_id -> key -> variant_value)
        self._experiments: Dict[str, Dict[str, Any]] = {}
        
        # Change history (append-only log)
        self._history: List[ConfigChange] = []
        
        # Initialize with defaults
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize all configs with default values."""
        for key, definition in CONFIG_DEFINITIONS.items():
            self._values[key] = definition.default_value
    
    def get(
        self, 
        key: str, 
        country_code: Optional[str] = None,
        experiment_id: Optional[str] = None,
    ) -> Any:
        """Get a configuration value."""
        # Check experiment first
        if experiment_id and experiment_id in self._experiments:
            exp_values = self._experiments[experiment_id]
            if key in exp_values:
                return exp_values[key]
        
        # Check country override
        if country_code and country_code in self._country_overrides:
            country_values = self._country_overrides[country_code]
            if key in country_values:
                return country_values[key]
        
        # Return global value
        return self._values.get(key)
    
    def set(
        self,
        key: str,
        value: Any,
        source: str = "human",
        reason: str = "",
        action_id: Optional[str] = None,
        country_code: Optional[str] = None,
        experiment_id: Optional[str] = None,
    ) -> ConfigChange:
        """Set a configuration value."""
        definition = CONFIG_DEFINITIONS.get(key)
        if not definition:
            raise ValueError(f"Unknown config key: {key}")
        
        # Validate value
        self._validate_value(definition, value)
        
        # Get old value
        old_value = self.get(key, country_code, experiment_id)
        
        # Apply change
        if experiment_id:
            if experiment_id not in self._experiments:
                self._experiments[experiment_id] = {}
            self._experiments[experiment_id][key] = value
        elif country_code:
            if country_code not in self._country_overrides:
                self._country_overrides[country_code] = {}
            self._country_overrides[country_code][key] = value
        else:
            self._values[key] = value
        
        # Record change
        change = ConfigChange(
            timestamp=datetime.utcnow(),
            key=key,
            old_value=old_value,
            new_value=value,
            change_source=source,
            change_reason=reason,
            action_id=action_id,
            experiment_id=experiment_id,
        )
        self._history.append(change)
        
        return change
    
    def rollback(self, change_index: int, reason: str = "Manual rollback") -> ConfigChange:
        """Rollback to before a specific change."""
        if change_index < 0 or change_index >= len(self._history):
            raise ValueError(f"Invalid change index: {change_index}")
        
        target_change = self._history[change_index]
        
        # Apply rollback
        rollback_change = self.set(
            key=target_change.key,
            value=target_change.old_value,
            source="rollback",
            reason=reason,
        )
        rollback_change.rollback_of = str(change_index)
        
        return rollback_change
    
    def rollback_recent(
        self, 
        hours: int = 24, 
        source_filter: Optional[str] = None
    ) -> List[ConfigChange]:
        """Rollback all changes in the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        rollbacks = []
        
        # Find changes to rollback (in reverse order)
        for i in range(len(self._history) - 1, -1, -1):
            change = self._history[i]
            if change.timestamp < cutoff:
                break
            if change.change_source == "rollback":
                continue  # Don't rollback rollbacks
            if source_filter and change.change_source != source_filter:
                continue
            
            rollback = self.rollback(i, f"Bulk rollback of last {hours}h")
            rollbacks.append(rollback)
        
        return rollbacks
    
    def _validate_value(self, definition: ConfigDefinition, value: Any):
        """Validate a value against its definition."""
        # Type check
        if definition.config_type == ConfigType.INTEGER:
            if not isinstance(value, int):
                raise ValueError(f"Expected integer, got {type(value)}")
        elif definition.config_type in [ConfigType.FLOAT, ConfigType.PERCENTAGE]:
            if not isinstance(value, (int, float)):
                raise ValueError(f"Expected number, got {type(value)}")
        elif definition.config_type == ConfigType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Expected boolean, got {type(value)}")
        elif definition.config_type == ConfigType.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Expected string, got {type(value)}")
        
        # Range check
        if definition.min_value is not None and value < definition.min_value:
            raise ValueError(f"Value {value} below minimum {definition.min_value}")
        if definition.max_value is not None and value > definition.max_value:
            raise ValueError(f"Value {value} above maximum {definition.max_value}")
        
        # Allowed values check
        if definition.allowed_values and value not in definition.allowed_values:
            raise ValueError(f"Value {value} not in allowed values: {definition.allowed_values}")
    
    def get_history(
        self, 
        key: Optional[str] = None,
        hours: Optional[int] = None,
        source: Optional[str] = None,
    ) -> List[ConfigChange]:
        """Get change history with optional filters."""
        history = self._history
        
        if key:
            history = [c for c in history if c.key == key]
        
        if hours:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            history = [c for c in history if c.timestamp >= cutoff]
        
        if source:
            history = [c for c in history if c.change_source == source]
        
        return history
    
    def get_auto_adjustable_keys(self) -> List[str]:
        """Get list of keys that can be auto-adjusted."""
        return [
            key for key, defn in CONFIG_DEFINITIONS.items()
            if defn.auto_adjustable
        ]
    
    def export_state(self) -> Dict:
        """Export current state for persistence."""
        return {
            "values": copy.deepcopy(self._values),
            "country_overrides": copy.deepcopy(self._country_overrides),
            "experiments": copy.deepcopy(self._experiments),
            "history": [c.to_dict() for c in self._history],
        }
    
    def get_definition(self, key: str) -> Optional[ConfigDefinition]:
        """Get the definition for a config key."""
        return CONFIG_DEFINITIONS.get(key)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_store: Optional[ConfigStore] = None

def get_config_store() -> ConfigStore:
    """Get the global config store instance."""
    global _store
    if _store is None:
        _store = ConfigStore()
    return _store


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    store = get_config_store()
    
    print("=" * 60)
    print("QUIRRELY CONFIG STORE")
    print("=" * 60)
    print(f"\nTotal configs: {len(CONFIG_DEFINITIONS)}")
    print(f"Auto-adjustable: {len(store.get_auto_adjustable_keys())}")
    
    print("\n--- CURRENT VALUES ---")
    for key in sorted(store._values.keys()):
        defn = CONFIG_DEFINITIONS[key]
        value = store.get(key)
        auto = "✅" if defn.auto_adjustable else "❌"
        print(f"  {auto} {key}: {value}")
    
    print("\n--- MAKING TEST CHANGE ---")
    change = store.set(
        key="funnel.nudge.soft_threshold",
        value=0.75,
        source="auto",
        reason="Test auto-adjustment",
        action_id="test_001",
    )
    print(f"  Changed: {change.key}")
    print(f"  From: {change.old_value} → To: {change.new_value}")
    
    print("\n--- ROLLING BACK ---")
    rollback = store.rollback(0, "Testing rollback")
    print(f"  Rolled back: {rollback.key}")
    print(f"  Restored: {rollback.new_value}")
    
    print("\n--- HISTORY ---")
    for change in store.get_history():
        print(f"  [{change.timestamp.strftime('%H:%M:%S')}] {change.change_source}: {change.key} = {change.new_value}")
