"""
QUIRRELY CLOSED-LOOP SYSTEM v1.0

A self-optimizing architecture that:
1. OBSERVES  - Runs Master Test simulations to understand state
2. DECIDES   - Classifies actions into auto-apply vs human-review
3. EXECUTES  - Applies safe changes automatically with A/B testing
4. LEARNS    - Calibrates predictions from real vs expected results

NO AI/LLM REQUIRED AT RUNTIME

Components:
- ActionClassifier: Determines which actions are safe to auto-apply
- ConfigStore: Centralized store for tunable parameters
- AutoApplier: Executes changes with A/B testing and rollback
- FeedbackLoop: Collects results and calibrates the system
- Orchestrator: Coordinates all components in a continuous loop

Usage:
    from closed_loop import get_orchestrator, OrchestratorMode
    
    orchestrator = get_orchestrator()
    orchestrator.set_mode(OrchestratorMode.AUTO_SAFE)
    result = orchestrator.run_cycle()
"""

from .action_classifier import (
    ActionClassifier,
    ClassifiedAction,
    ActionLane,
    ActionDomain,
    RiskLevel,
    classify_actions,
)

from .config_store import (
    ConfigStore,
    ConfigDefinition,
    ConfigChange,
    ConfigType,
    ConfigScope,
    get_config_store,
    CONFIG_DEFINITIONS,
)

from .auto_applier import (
    AutoApplier,
    AppliedChange,
    Experiment,
    ExperimentStatus,
    ExperimentResult,
    get_auto_applier,
)

from .feedback_loop import (
    FeedbackLoop,
    FeedbackCollector,
    Calibrator,
    AnomalyDetector,
    Observation,
    CalibrationFactor,
    FeedbackSource,
    CalibrationStatus,
    get_feedback_loop,
)

from .orchestrator import (
    ClosedLoopOrchestrator,
    OrchestratorMode,
    CycleResult,
    get_orchestrator,
)

__all__ = [
    # Classifier
    "ActionClassifier",
    "ClassifiedAction", 
    "ActionLane",
    "ActionDomain",
    "RiskLevel",
    "classify_actions",
    
    # Config
    "ConfigStore",
    "ConfigDefinition",
    "ConfigChange",
    "ConfigType",
    "ConfigScope",
    "get_config_store",
    "CONFIG_DEFINITIONS",
    
    # Applier
    "AutoApplier",
    "AppliedChange",
    "Experiment",
    "ExperimentStatus",
    "ExperimentResult",
    "get_auto_applier",
    
    # Feedback
    "FeedbackLoop",
    "FeedbackCollector",
    "Calibrator",
    "AnomalyDetector",
    "Observation",
    "CalibrationFactor",
    "FeedbackSource",
    "CalibrationStatus",
    "get_feedback_loop",
    
    # Orchestrator
    "ClosedLoopOrchestrator",
    "OrchestratorMode",
    "CycleResult",
    "get_orchestrator",
]
