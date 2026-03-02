"""
LNCP META v5.1.0-G2M
The self-optimizing layer of LNCP Core.
Knight of Wands v3.1.1 G2M (Go-To-Market) Release.

This is CORE IP (Extension).
Requires LNCP Engine. Cannot exist independently.

META provides:
- Observation: Master Test simulation, outcome tracking
- Decision: Action classification, proposal system
- Execution: Auto-apply with A/B testing
- Learning: Feedback calibration, prediction logging

G2M Release Features:
- Achievement Observer: P3 gamification tracking
- Retention Observer: P1 downgrade prevention tracking
- Bundle Tracker: P1 addon bundling tracking
- Progressive Tracker: P3 feature unlocks tracking
- Blog Observer: GSC integration, content freshness
- Extended action domains (19 domains)
- Extended event types (151 events)

The result: A system that optimizes itself without human intervention
for safe changes, while surfacing complex decisions to humans.

NO AI/LLM REQUIRED AT RUNTIME

Usage:
    from lncp.meta import get_meta_orchestrator, MetaMode
    
    orchestrator = get_meta_orchestrator()
    orchestrator.set_mode(MetaMode.STANDARD)
    result = orchestrator.run_cycle()
"""

__version__ = "5.1.0-G2M"
__release__ = "G2M"
__requires__ = "lncp.engine>=3.8.0"

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

from .simulation import (
    SimulationConfig,
    BaselineExpectations,
    UserStage,
    SimulatedUser,
    SimulationEngine,
    MasterTest,
    run_master_test,
)

from .orchestrator import (
    ClosedLoopOrchestrator,
    OrchestratorMode,
    CycleResult,
    get_orchestrator,
)

from .unified_orchestrator import (
    UnifiedOrchestrator,
    UnifiedMode,
    UnifiedCycleResult,
    Domain,
    get_unified_orchestrator,
)

# v4.1 Components
from .outcome_tracker import (
    OutcomeStatus,
    OutcomeConfidence,
    PredictedOutcome,
    ActualOutcome,
    OutcomeRecord,
    OutcomeTracker,
    get_outcome_tracker,
)

from .prediction_logger import (
    PredictionType,
    PredictionAccuracy,
    PredictionRecord,
    PredictionLogger,
    get_prediction_logger,
)

from .parameter_store import (
    ParameterType,
    ParameterCategory,
    ChangeSource,
    ParameterBoundary,
    ParameterDefinition,
    ParameterChange,
    ParameterState,
    META_PARAMETERS,
    MetaParameterStore,
    get_parameter_store,
)

from .health_score import (
    HealthLevel,
    RiskTolerance,
    DomainHealth,
    SystemHealth,
    HealthCalculator,
    get_health_calculator,
)

from .proposal_system import (
    ProposalType,
    ProposalLane,
    ProposalStatus,
    ProposalPriority,
    ProposalEvidence,
    ProposalImpact,
    ProposalRisk,
    Proposal,
    LANE_RULES,
    ProposalManager,
    get_proposal_manager,
)

# v4.2 Components
from .meta_orchestrator import (
    MetaMode,
    MetaCycleResult,
    MetaOrchestrator,
    get_meta_orchestrator,
)

from .trust_store import (
    TrustLevel,
    OutcomeType,
    OUTCOME_VALUES,
    TrustEvent,
    TrustScore,
    TrustStore,
    get_trust_store,
)

from .engine_parameters import (
    EngineParameterCategory,
    EngineParameter,
    EngineParameterProposal,
    ENGINE_PARAMETERS,
    EngineParameterAnalyzer,
    get_engine_analyzer,
)

from .revenue_observer import (
    RevenueMetrics,
    RevenueEvent,
    ChurnEvent,
    ConversionEvent,
    StripeClient,
    RevenueObserver,
    get_revenue_observer,
)

from .attribution_tracker import (
    BlogVisit,
    AppSignup,
    Subscription,
    AttributionChain,
    AttributionTracker,
    get_attribution_tracker,
)

# v5.0 Components (v3.1.1 Support)
from .achievement_observer import (
    AchievementObserver,
    AchievementHealth,
    BadgeMetrics,
    ChallengeMetrics,
    StreakMetrics,
    LeaderboardMetrics,
    get_achievement_observer,
)

from .retention_observer import (
    RetentionObserver,
    RetentionHealth,
    InterventionMetrics,
    ChurnIntentMetrics,
    ChurnIntent,
    InterventionType,
    InterventionOutcome,
    get_retention_observer,
)

from .bundle_tracker import (
    BundleTracker,
    BundleHealth,
    BundleMetrics,
    BundleDefinition,
    get_bundle_tracker,
)

from .progressive_tracker import (
    ProgressiveTracker,
    ProgressiveHealth,
    DayMetrics,
    Day7OfferMetrics,
    UnlockDefinition,
    get_progressive_tracker,
)

# v5.1 Components (Blog/SEO Integration)
from .blog_observer import (
    BlogObserver,
    BlogHealth,
    PagePerformance,
    KeywordOpportunity,
    ContentFreshness,
    get_blog_observer,
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
    
    # Simulation
    "SimulationConfig",
    "BaselineExpectations",
    "UserStage",
    "SimulatedUser",
    "SimulationEngine",
    "MasterTest",
    "run_master_test",
    
    # Orchestrator
    "ClosedLoopOrchestrator",
    "OrchestratorMode",
    "CycleResult",
    "get_orchestrator",
    
    # Unified Orchestrator
    "UnifiedOrchestrator",
    "UnifiedMode",
    "UnifiedCycleResult",
    "Domain",
    "get_unified_orchestrator",
    
    # v4.1: Outcome Tracker
    "OutcomeStatus",
    "OutcomeConfidence",
    "PredictedOutcome",
    "ActualOutcome",
    "OutcomeRecord",
    "OutcomeTracker",
    "get_outcome_tracker",
    
    # v4.1: Prediction Logger
    "PredictionType",
    "PredictionAccuracy",
    "PredictionRecord",
    "PredictionLogger",
    "get_prediction_logger",
    
    # v4.1: Parameter Store
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
    
    # v4.1: Health Score
    "HealthLevel",
    "RiskTolerance",
    "DomainHealth",
    "SystemHealth",
    "HealthCalculator",
    "get_health_calculator",
    
    # v4.1: Proposal System
    "ProposalType",
    "ProposalLane",
    "ProposalStatus",
    "ProposalPriority",
    "ProposalEvidence",
    "ProposalImpact",
    "ProposalRisk",
    "Proposal",
    "LANE_RULES",
    "ProposalManager",
    "get_proposal_manager",
    
    # v4.2: Meta Orchestrator
    "MetaMode",
    "MetaCycleResult",
    "MetaOrchestrator",
    "get_meta_orchestrator",
    
    # v4.2: Trust Store
    "TrustLevel",
    "OutcomeType",
    "OUTCOME_VALUES",
    "TrustEvent",
    "TrustScore",
    "TrustStore",
    "get_trust_store",
    
    # v4.2: Engine Parameters
    "EngineParameterCategory",
    "EngineParameter",
    "EngineParameterProposal",
    "ENGINE_PARAMETERS",
    "EngineParameterAnalyzer",
    "get_engine_analyzer",
    
    # v4.2: Revenue Observer
    "RevenueMetrics",
    "RevenueEvent",
    "ChurnEvent",
    "ConversionEvent",
    "StripeClient",
    "RevenueObserver",
    "get_revenue_observer",
    
    # v4.2: Attribution Tracker
    "BlogVisit",
    "AppSignup",
    "Subscription",
    "AttributionChain",
    "AttributionTracker",
    "get_attribution_tracker",
    
    # v5.0: Achievement Observer
    "AchievementObserver",
    "AchievementHealth",
    "BadgeMetrics",
    "ChallengeMetrics",
    "StreakMetrics",
    "LeaderboardMetrics",
    "get_achievement_observer",
    
    # v5.0: Retention Observer
    "RetentionObserver",
    "RetentionHealth",
    "InterventionMetrics",
    "ChurnIntentMetrics",
    "ChurnIntent",
    "InterventionType",
    "InterventionOutcome",
    "get_retention_observer",
    
    # v5.0: Bundle Tracker
    "BundleTracker",
    "BundleHealth",
    "BundleMetrics",
    "BundleDefinition",
    "get_bundle_tracker",
    
    # v5.0: Progressive Tracker
    "ProgressiveTracker",
    "ProgressiveHealth",
    "DayMetrics",
    "Day7OfferMetrics",
    "UnlockDefinition",
    "get_progressive_tracker",
    
    # v5.1: Blog Observer
    "BlogObserver",
    "BlogHealth",
    "PagePerformance",
    "KeywordOpportunity",
    "ContentFreshness",
    "get_blog_observer",
]
