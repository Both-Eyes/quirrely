#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
LNCP CORE v4.0
Linguistic Numerical Curation Protocol
═══════════════════════════════════════════════════════════════════════════════

LNCP is a self-sustaining, self-optimizing token economy for voice analysis.

ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LNCP CORE v4.0                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ENGINE v3.8 (Immutable)                                            │   │
│  │  • 50-token vocabulary (tokens.py)                                  │   │
│  │  • 40 voice profiles (profiles.py)                                  │   │
│  │  • Scoring algorithm (scoring.py)                                   │   │
│  │  • Token economics (value.py)                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  META v1.0 (Core Extension)                                         │   │
│  │  • Action Classification (action_classifier.py)                     │   │
│  │  • Config Store (config_store.py)                                   │   │
│  │  • Auto-Applier (auto_applier.py)                                   │   │
│  │  • Feedback Loop (feedback_loop.py)                                 │   │
│  │  • Orchestrator (orchestrator.py)                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

ENGINE: Transforms text into voice profiles (WHAT)
META: Makes the system self-optimizing (HOW IT EVOLVES)

Both are CORE IP. Neither requires AI/LLM at runtime.

USAGE:

    # Engine only (pure, no deps)
    from lncp.engine import analyze, get_profile
    result = analyze("Your text here...")
    
    # Full system (Engine + Meta)
    from lncp import LNCP
    lncp = LNCP()
    lncp.analyze("Your text here...")
    lncp.run_optimization_cycle()

LICENSE: Proprietary
COPYRIGHT: Quirrely Inc.
"""

__version__ = "4.0.0"
__engine_version__ = "3.8.0"
__meta_version__ = "1.0.0"

# Import Engine
from .engine import (
    # Analysis
    analyze,
    extract_features,
    
    # Tokens
    TokenCategory,
    Token,
    ALL_TOKENS,
    get_token,
    
    # Profiles
    StyleAxis,
    CertitudeAxis,
    Profile,
    ALL_PROFILES,
    get_profile,
    
    # Scoring
    TokenScore,
    ProfileMatch,
    AnalysisResult,
    
    # Value
    TokenGeneration,
    TokenValue,
    calculate_token_value,
    calculate_system_value,
)

# Import Meta
from .meta import (
    # Orchestrator
    ClosedLoopOrchestrator,
    OrchestratorMode,
    CycleResult,
    get_orchestrator,
    
    # Classification
    ActionClassifier,
    ClassifiedAction,
    ActionLane,
    classify_actions,
    
    # Config
    ConfigStore,
    get_config_store,
    
    # Applier
    AutoApplier,
    get_auto_applier,
    
    # Feedback
    FeedbackLoop,
    get_feedback_loop,
)


class LNCP:
    """
    Unified LNCP interface combining Engine and Meta.
    
    This is the recommended way to use LNCP when you want
    the full self-optimizing system.
    """
    
    def __init__(self, mode: OrchestratorMode = OrchestratorMode.OBSERVE_ONLY):
        """
        Initialize LNCP with optional orchestration mode.
        
        Args:
            mode: How aggressive the self-optimization should be
                  - OBSERVE_ONLY: Just watch, don't change anything
                  - SUGGEST: Log changes but don't apply
                  - AUTO_SAFE: Auto-apply safe changes only
                  - FULL_AUTO: Auto-apply all eligible changes
        """
        self._orchestrator = get_orchestrator()
        self._orchestrator.set_mode(mode)
        self._config = get_config_store()
    
    @property
    def version(self) -> str:
        return __version__
    
    @property
    def engine_version(self) -> str:
        return __engine_version__
    
    @property
    def meta_version(self) -> str:
        return __meta_version__
    
    # ─────────────────────────────────────────────────────────────────────
    # ENGINE FUNCTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def analyze(self, text: str) -> AnalysisResult:
        """Analyze text and return voice profile."""
        return analyze(text)
    
    def get_profile(self, identifier: str) -> Profile:
        """Get a profile by ID or slug."""
        return get_profile(identifier)
    
    def calculate_value(
        self,
        user_id: str,
        analyses_count: int,
        unique_profiles_seen: int,
        streak_days: int,
        milestones_achieved: int,
        generation: TokenGeneration,
        days_inactive: int = 0,
    ) -> TokenValue:
        """Calculate token value for a user."""
        return calculate_token_value(
            user_id=user_id,
            analyses_count=analyses_count,
            unique_profiles_seen=unique_profiles_seen,
            streak_days=streak_days,
            milestones_achieved=milestones_achieved,
            generation=generation,
            days_inactive=days_inactive,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # META FUNCTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def run_optimization_cycle(self, force: bool = False) -> CycleResult:
        """Run a complete self-optimization cycle."""
        return self._orchestrator.run_cycle(force=force)
    
    def set_mode(self, mode: OrchestratorMode):
        """Set the optimization mode."""
        self._orchestrator.set_mode(mode)
    
    def get_config(self, key: str) -> any:
        """Get a configuration value."""
        return self._config.get(key)
    
    def get_status(self) -> dict:
        """Get current system status."""
        return self._orchestrator.get_status()
    
    def get_human_review_queue(self) -> list:
        """Get pending items for human review."""
        return self._orchestrator.get_human_review_queue()


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Main class
    "LNCP",
    
    # Version
    "__version__",
    "__engine_version__",
    "__meta_version__",
    
    # Engine - Analysis
    "analyze",
    "extract_features",
    "TokenScore",
    "ProfileMatch", 
    "AnalysisResult",
    
    # Engine - Tokens
    "TokenCategory",
    "Token",
    "ALL_TOKENS",
    "get_token",
    
    # Engine - Profiles
    "StyleAxis",
    "CertitudeAxis",
    "Profile",
    "ALL_PROFILES",
    "get_profile",
    
    # Engine - Value
    "TokenGeneration",
    "TokenValue",
    "calculate_token_value",
    "calculate_system_value",
    
    # Meta - Orchestration
    "ClosedLoopOrchestrator",
    "OrchestratorMode",
    "CycleResult",
    "get_orchestrator",
    
    # Meta - Classification
    "ActionClassifier",
    "ClassifiedAction",
    "ActionLane",
    "classify_actions",
    
    # Meta - Config
    "ConfigStore",
    "get_config_store",
    
    # Meta - Auto-Apply
    "AutoApplier",
    "get_auto_applier",
    
    # Meta - Feedback
    "FeedbackLoop",
    "get_feedback_loop",
]
