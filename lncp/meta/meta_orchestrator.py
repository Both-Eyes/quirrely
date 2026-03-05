#!/usr/bin/env python3
"""
LNCP META: META ORCHESTRATOR v5.1.0-G2M
The master orchestrator for Knight of Wands G2M (Go-To-Market) Release.

This is the brain of the self-optimizing system. It:
1. Calculates system health before making decisions
2. Reads thresholds from parameter store
3. Registers every action with outcome tracker
4. Logs predictions for calibration
5. Assesses outcomes and updates learning
6. Creates proposals when opportunities arise

G2M Release (v3.1.1 + v5.1):
- Achievement Observer (P3 gamification)
- Retention Observer (P1 downgrade prevention)
- Bundle Tracker (P1 addon bundling)
- Progressive Tracker (P3 feature unlocks)
- Blog Observer (GSC integration, content freshness)
- 151 event types, 19 action domains

Pattern: Adapter wrapping UnifiedOrchestrator + v4.1 + v5.0 + v5.1 components
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS FROM v4.1 COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════

from .outcome_tracker import (
    OutcomeTracker, OutcomeStatus, PredictedOutcome, 
    OutcomeRecord, get_outcome_tracker
)
from .prediction_logger import (
    PredictionLogger, PredictionType, get_prediction_logger
)
from .parameter_store import (
    MetaParameterStore, ChangeSource, get_parameter_store
)
from .health_score import (
    HealthCalculator, HealthLevel, RiskTolerance, 
    SystemHealth, DomainHealth, get_health_calculator
)
from .proposal_system import (
    ProposalManager, ProposalType, ProposalPriority,
    ProposalEvidence, ProposalImpact, ProposalRisk,
    Proposal, get_proposal_manager
)

# Import existing orchestrator
from .unified_orchestrator import (
    UnifiedOrchestrator, UnifiedMode, UnifiedCycleResult,
    Domain, get_unified_orchestrator
)

# Import for action handling
from .action_classifier import ClassifiedAction, ActionLane, ActionDomain

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS FROM v5.0 COMPONENTS (v3.1.1)
# ═══════════════════════════════════════════════════════════════════════════

from .achievement_observer import (
    AchievementObserver, AchievementHealth, BadgeMetrics,
    ChallengeMetrics, StreakMetrics, get_achievement_observer
)
from .retention_observer import (
    RetentionObserver, RetentionHealth, InterventionMetrics,
    ChurnIntent, InterventionType, InterventionOutcome,
    get_retention_observer
)
from .bundle_tracker import (
    BundleTracker, BundleHealth, BundleMetrics,
    get_bundle_tracker
)
from .progressive_tracker import (
    ProgressiveTracker, ProgressiveHealth, DayMetrics,
    Day7OfferMetrics, get_progressive_tracker
)

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS FROM v5.1 COMPONENTS (Blog/SEO)
# ═══════════════════════════════════════════════════════════════════════════

from .blog_observer import (
    BlogObserver, BlogHealth, PagePerformance,
    KeywordOpportunity, ContentFreshness,
    get_blog_observer
)


# ═══════════════════════════════════════════════════════════════════════════
# META ORCHESTRATOR MODE
# ═══════════════════════════════════════════════════════════════════════════

class MetaMode(str, Enum):
    """Operating modes for MetaOrchestrator."""
    OBSERVE_ONLY = "observe_only"     # Only observe, no actions
    LEARN_ONLY = "learn_only"         # Observe + learn, no auto-apply
    CAUTIOUS = "cautious"             # Conservative auto-apply
    STANDARD = "standard"             # Normal operations
    AGGRESSIVE = "aggressive"         # Maximum autonomy


# ═══════════════════════════════════════════════════════════════════════════
# META CYCLE RESULT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MetaCycleResult:
    """Complete result of a Meta orchestration cycle."""
    # Identity
    cycle_id: str
    mode: MetaMode
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    # Health
    system_health: SystemHealth
    health_changed: bool
    previous_health_score: Optional[float]
    
    # Actions
    actions_generated: int
    actions_auto_applied: int
    actions_queued_review: int
    actions_queued_super_admin: int
    actions_skipped: int
    
    # Learning
    outcomes_assessed: int
    predictions_logged: int
    calibrations_updated: int
    
    # Proposals
    proposals_created: int
    proposals_auto_executed: int
    
    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "cycle_id": self.cycle_id,
            "mode": self.mode.value,
            "duration_seconds": self.duration_seconds,
            "health": {
                "score": self.system_health.score,
                "level": self.system_health.level.value,
                "risk_tolerance": self.system_health.risk_tolerance.value,
            },
            "actions": {
                "generated": self.actions_generated,
                "auto_applied": self.actions_auto_applied,
                "review": self.actions_queued_review,
                "super_admin": self.actions_queued_super_admin,
            },
            "learning": {
                "outcomes_assessed": self.outcomes_assessed,
                "predictions_logged": self.predictions_logged,
                "calibrations_updated": self.calibrations_updated,
            },
            "proposals": {
                "created": self.proposals_created,
                "auto_executed": self.proposals_auto_executed,
            },
            "errors": len(self.errors),
            "warnings": len(self.warnings),
        }


# ═══════════════════════════════════════════════════════════════════════════
# META ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class MetaOrchestrator:
    """
    The master orchestrator that coordinates all Meta components.
    
    This wraps UnifiedOrchestrator and integrates:
    - Outcome Tracker (learning from actions)
    - Prediction Logger (calibrating predictions)
    - Parameter Store (tunable thresholds)
    - Health Calculator (risk tolerance)
    - Proposal Manager (self-modification)
    
    v5.0 additions:
    - Achievement Observer (P3 gamification)
    - Retention Observer (P1 downgrade prevention)
    - Bundle Tracker (P1 addon bundling)
    - Progressive Tracker (P3 feature unlocks)
    
    Every cycle:
    1. PRE: Calculate health, read parameters, check constraints
    2. OBSERVE: Collect metrics from all v3.1.1 systems
    3. EXECUTE: Run actions with full tracking
    4. POST: Assess outcomes, update calibration, create proposals
    """
    
    VERSION = "5.1.0-G2M"
    RELEASE = "G2M"
    
    def __init__(self):
        # Core orchestrator
        self.unified = get_unified_orchestrator()
        
        # v4.1 Components
        self.outcome_tracker = get_outcome_tracker()
        self.prediction_logger = get_prediction_logger()
        self.parameter_store = get_parameter_store()
        self.health_calculator = get_health_calculator()
        self.proposal_manager = get_proposal_manager()
        
        # v5.0 Components (v3.1.1 support)
        self.achievement_observer = get_achievement_observer()
        self.retention_observer = get_retention_observer()
        self.bundle_tracker = get_bundle_tracker()
        self.progressive_tracker = get_progressive_tracker()
        
        # v5.1 Components (Blog/SEO)
        self.blog_observer = get_blog_observer()
        
        # State
        self.mode = MetaMode.STANDARD
        self.last_health: Optional[SystemHealth] = None
        self.cycle_count = 0
        
        # v3.1.1 health caches
        self.last_achievement_health: Optional[AchievementHealth] = None
        self.last_retention_health: Optional[RetentionHealth] = None
        self.last_bundle_health: Optional[BundleHealth] = None
        self.last_progressive_health: Optional[ProgressiveHealth] = None
        
        # v5.1 health cache
        self.last_blog_health: Optional[BlogHealth] = None
        
        # Metrics for this session
        self.session_start = datetime.utcnow()
        self.total_actions_applied = 0
        self.total_outcomes_assessed = 0
        
        # v3.1.1 metrics
        self.v311_actions_generated = 0
        self.v311_optimizations_suggested = 0
        
        # v5.1 metrics
        self.seo_actions_generated = 0
        self.seo_optimizations_suggested = 0
        
    # ─────────────────────────────────────────────────────────────────────
    # CONFIGURATION
    # ─────────────────────────────────────────────────────────────────────
    
    def set_mode(self, mode: MetaMode):
        """Set the operating mode."""
        self.mode = mode
        
        # Map to unified orchestrator mode
        mode_map = {
            MetaMode.OBSERVE_ONLY: UnifiedMode.OBSERVE_ONLY,
            MetaMode.LEARN_ONLY: UnifiedMode.SUGGEST,
            MetaMode.CAUTIOUS: UnifiedMode.AUTO_SAFE,
            MetaMode.STANDARD: UnifiedMode.AUTO_SAFE,
            MetaMode.AGGRESSIVE: UnifiedMode.FULL_AUTO,
        }
        self.unified.set_mode(mode_map.get(mode, UnifiedMode.AUTO_SAFE))
    
    # ─────────────────────────────────────────────────────────────────────
    # MAIN CYCLE
    # ─────────────────────────────────────────────────────────────────────
    
    def run_cycle(
        self,
        domains: Optional[List[Domain]] = None,
        force_health_recalc: bool = False,
    ) -> MetaCycleResult:
        """
        Run a complete Meta orchestration cycle.
        
        This is the main entry point for the self-optimizing system.
        """
        started_at = datetime.utcnow()
        self.cycle_count += 1
        cycle_id = f"meta_{started_at.strftime('%Y%m%d_%H%M%S')}_{self.cycle_count}"
        
        errors = []
        warnings = []
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 1: PRE-CYCLE (Health, Parameters, Constraints)
        # ─────────────────────────────────────────────────────────────────
        
        # Calculate system health
        try:
            system_health = self._calculate_system_health()
        except Exception as e:
            errors.append(f"Health calculation failed: {e}")
            system_health = self._get_fallback_health()
        
        health_changed = (
            self.last_health is None or 
            abs(system_health.score - self.last_health.score) > 5
        )
        previous_health = self.last_health.score if self.last_health else None
        self.last_health = system_health
        
        # Check if we should proceed based on health
        if system_health.level == HealthLevel.CRITICAL:
            warnings.append("System health CRITICAL - pausing all actions")
            if self.mode != MetaMode.OBSERVE_ONLY:
                self.mode = MetaMode.OBSERVE_ONLY
        
        # Read parameters for this cycle
        params = self._read_cycle_parameters()
        
        # Check constraints
        if not system_health.auto_apply_enabled and self.mode in [MetaMode.STANDARD, MetaMode.AGGRESSIVE]:
            warnings.append("Auto-apply disabled due to health - switching to LEARN_ONLY")
            self.mode = MetaMode.LEARN_ONLY
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 2: OBSERVE v3.1.1 SYSTEMS
        # ─────────────────────────────────────────────────────────────────
        
        v311_actions = []
        
        try:
            # Collect health from all v3.1.1 observers
            self.last_achievement_health = self.achievement_observer.get_health()
            self.last_retention_health = self.retention_observer.get_health()
            self.last_bundle_health = self.bundle_tracker.get_health()
            self.last_progressive_health = self.progressive_tracker.get_health()
            
            # v5.1: Blog/SEO observer
            self.last_blog_health = self.blog_observer.get_health()
            
            # Collect optimization suggestions from each observer
            achievement_suggestions = self.achievement_observer.suggest_optimizations()
            retention_suggestions = self.retention_observer.suggest_optimizations()
            bundle_suggestions = self.bundle_tracker.suggest_optimizations()
            progressive_suggestions = self.progressive_tracker.suggest_optimizations()
            
            # v5.1: Blog/SEO suggestions
            blog_suggestions = self.blog_observer.suggest_optimizations()
            
            v311_actions = (
                achievement_suggestions + 
                retention_suggestions + 
                bundle_suggestions + 
                progressive_suggestions +
                blog_suggestions  # v5.1
            )
            
            self.v311_optimizations_suggested += len(v311_actions) - len(blog_suggestions)
            self.seo_optimizations_suggested += len(blog_suggestions)
            
        except Exception as e:
            errors.append(f"v3.1.1/v5.1 observation failed: {e}")
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 3: EXECUTE (Run unified orchestrator with tracking)
        # ─────────────────────────────────────────────────────────────────
        
        actions_generated = 0
        actions_auto_applied = 0
        actions_queued_review = 0
        actions_queued_super_admin = 0
        actions_skipped = 0
        predictions_logged = 0
        
        if self.mode != MetaMode.OBSERVE_ONLY:
            try:
                # Run the unified orchestrator
                unified_result = self.unified.run_cycle(domains=domains)
                
                actions_generated = unified_result.total_actions + len(v311_actions)
                self.v311_actions_generated += len(v311_actions)
                
                # Process v3.1.1 and v5.1 actions
                for action in v311_actions:
                    domain = action.get("domain", "unknown")
                    confidence = action.get("confidence", 0.5)
                    
                    # Classify based on domain
                    if domain in ["gamification", "progressive", "notification", "social_proof"]:
                        if confidence >= 0.7:
                            self._track_v311_action(action, "auto_applied", system_health.score)
                            actions_auto_applied += 1
                        else:
                            self._track_v311_action(action, "queued_review", system_health.score)
                            actions_queued_review += 1
                    elif domain in ["retention"]:
                        if action.get("type") in ["copy_test", "reminder_timing"]:
                            self._track_v311_action(action, "auto_applied", system_health.score)
                            actions_auto_applied += 1
                        else:
                            self._track_v311_action(action, "queued_review", system_health.score)
                            actions_queued_review += 1
                    # v5.1: SEO domains
                    elif domain in ["seo"]:
                        if action.get("type") in ["meta_optimization", "cta_optimization"] and confidence >= 0.65:
                            self._track_v311_action(action, "auto_applied", system_health.score)
                            actions_auto_applied += 1
                            self.seo_actions_generated += 1
                        else:
                            self._track_v311_action(action, "queued_review", system_health.score)
                            actions_queued_review += 1
                    elif domain in ["seo_content"]:
                        # Content changes always need review
                        self._track_v311_action(action, "queued_review", system_health.score)
                        actions_queued_review += 1
                    else:
                        # Bundling, tier_pricing, seo_technical always human review
                        self._track_v311_action(action, "queued_super_admin", system_health.score)
                        actions_queued_super_admin += 1
                    
                    predictions_logged += 1
                
                # Process existing actions from unified orchestrator
                for action in unified_result.actions_applied:
                    self._track_action(action, "applied", system_health.score)
                    predictions_logged += 1
                    actions_auto_applied += 1
                
                for action in unified_result.actions_pending:
                    if hasattr(action, 'lane'):
                        if action.lane == ActionLane.HUMAN_REVIEW:
                            actions_queued_review += 1
                        elif action.lane == ActionLane.SUPER_ADMIN:
                            actions_queued_super_admin += 1
                    else:
                        actions_queued_review += 1
                
                # Respect max actions from health
                if actions_auto_applied > system_health.max_actions_per_cycle:
                    warnings.append(
                        f"Hit max actions limit: {system_health.max_actions_per_cycle}"
                    )
                
            except Exception as e:
                errors.append(f"Execution failed: {e}")
        
        # ─────────────────────────────────────────────────────────────────
        # PHASE 3: POST-CYCLE (Learn, Calibrate, Propose)
        # ─────────────────────────────────────────────────────────────────
        
        # Assess pending outcomes
        outcomes_assessed = 0
        try:
            assessed = self.outcome_tracker.assess_all_pending()
            outcomes_assessed = len(assessed)
            self.total_outcomes_assessed += outcomes_assessed
            
            # Update calibration based on outcomes
            for outcome in assessed:
                self._update_calibration_from_outcome(outcome)
                
        except Exception as e:
            errors.append(f"Outcome assessment failed: {e}")
        
        # Check for proposal opportunities
        proposals_created = 0
        proposals_auto_executed = 0
        try:
            new_proposals = self._check_proposal_opportunities(system_health)
            proposals_created = len(new_proposals)
            proposals_auto_executed = sum(
                1 for p in new_proposals 
                if p.status.value == "executed"
            )
        except Exception as e:
            errors.append(f"Proposal check failed: {e}")
        
        # Calculate calibrations updated
        calibrations_updated = self._count_calibration_updates()
        
        # ─────────────────────────────────────────────────────────────────
        # COMPLETE
        # ─────────────────────────────────────────────────────────────────
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        self.total_actions_applied += actions_auto_applied
        
        return MetaCycleResult(
            cycle_id=cycle_id,
            mode=self.mode,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            system_health=system_health,
            health_changed=health_changed,
            previous_health_score=previous_health,
            actions_generated=actions_generated,
            actions_auto_applied=actions_auto_applied,
            actions_queued_review=actions_queued_review,
            actions_queued_super_admin=actions_queued_super_admin,
            actions_skipped=actions_skipped,
            outcomes_assessed=outcomes_assessed,
            predictions_logged=predictions_logged,
            calibrations_updated=calibrations_updated,
            proposals_created=proposals_created,
            proposals_auto_executed=proposals_auto_executed,
            errors=errors,
            warnings=warnings,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # HEALTH CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _calculate_system_health(self) -> SystemHealth:
        """Calculate current system health from all sources."""
        # Get data from unified orchestrator's data sources
        # In production, these would come from real data
        
        # App health from Master Test
        app_data = self._get_app_metrics()
        app_health = self.health_calculator.calculate_app_health(
            master_test_health=app_data.get("health", 80),
            funnel_conversion_rate=app_data.get("conversion", 0.05),
            error_rate=app_data.get("error_rate", 0.02),
            response_time_p95=app_data.get("response_time", 400),
        )
        
        # Blog health from GSC/tracking
        blog_data = self._get_blog_metrics()
        blog_health = self.health_calculator.calculate_blog_health(
            impressions_trend=blog_data.get("impressions_trend", 0),
            ctr_trend=blog_data.get("ctr_trend", 0),
            click_to_signup_rate=blog_data.get("conversion", 0.03),
            pages_performing=blog_data.get("pages_up", 30),
            pages_total=blog_data.get("pages_total", 40),
        )
        
        # Revenue health from Stripe (or simulation)
        revenue_data = self._get_revenue_metrics()
        revenue_health = self.health_calculator.calculate_revenue_health(
            mrr=revenue_data.get("mrr", 16000),
            mrr_growth_rate=revenue_data.get("growth", 5),
            churn_rate=revenue_data.get("churn", 4),
            trial_conversion_rate=revenue_data.get("trial_conv", 0.20),
            ltv_cac_ratio=revenue_data.get("ltv_cac", 2.5),
        )
        
        # Meta health from our own performance
        meta_data = self._get_meta_metrics()
        meta_health = self.health_calculator.calculate_meta_health(
            prediction_accuracy=meta_data.get("accuracy", 0.75),
            action_success_rate=meta_data.get("success_rate", 0.85),
            rollback_rate=meta_data.get("rollback_rate", 0.05),
            calibration_drift=meta_data.get("calibration_drift", 0.1),
        )
        
        return self.health_calculator.calculate_system_health(
            app_health, blog_health, revenue_health, meta_health
        )
    
    def _get_fallback_health(self) -> SystemHealth:
        """Get conservative fallback health if calculation fails."""
        # Create minimal health objects
        app = DomainHealth(domain="app", score=50, weight=0.4)
        blog = DomainHealth(domain="blog", score=50, weight=0.2)
        revenue = DomainHealth(domain="revenue", score=50, weight=0.3)
        meta = DomainHealth(domain="meta", score=50, weight=0.1)
        return self.health_calculator.calculate_system_health(app, blog, revenue, meta)
    
    def _get_app_metrics(self) -> Dict:
        """Get app metrics - override in production."""
        # Try to get from unified orchestrator's simulation
        try:
            if hasattr(self.unified, 'app_orchestrator'):
                sim = self.unified.app_orchestrator.simulation
                if sim and hasattr(sim, 'current_state'):
                    return {
                        "health": sim.current_state.get("health", 80),
                        "conversion": 0.05,
                        "error_rate": 0.02,
                        "response_time": 350,
                    }
        except:
            pass
        return {"health": 80, "conversion": 0.05, "error_rate": 0.02, "response_time": 350}
    
    def _get_blog_metrics(self) -> Dict:
        """Get blog metrics from BlogObserver."""
        try:
            health = self.blog_observer.get_health()
            return {
                "impressions_trend": health.impressions_trend,
                "ctr_trend": health.ctr_trend,
                "conversion": health.avg_ctr,  # Using CTR as conversion proxy
                "pages_up": health.pages_performing,
                "pages_total": health.total_pages,
            }
        except Exception:
            # Fallback to defaults
            return {
                "impressions_trend": 5,
                "ctr_trend": 2,
                "conversion": 0.03,
                "pages_up": 32,
                "pages_total": 40,
            }
    
    def _get_revenue_metrics(self) -> Dict:
        """Get revenue metrics - override in production."""
        return {
            "mrr": 16170,
            "growth": 8,
            "churn": 3.5,
            "trial_conv": 0.22,
            "ltv_cac": 2.8,
        }
    
    def _get_meta_metrics(self) -> Dict:
        """Get Meta's own performance metrics."""
        summary = self.outcome_tracker.get_learning_summary()
        pred_report = self.prediction_logger.get_accuracy_report(days=30)
        
        return {
            "accuracy": pred_report.get("overall_accuracy_rate", 0.75),
            "success_rate": summary.get("overall_success_rate", 0.85),
            "rollback_rate": summary.get("overall_rollback_rate", 0.05),
            "calibration_drift": 0.1,  # Would calculate from calibration changes
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # PARAMETER READING
    # ─────────────────────────────────────────────────────────────────────
    
    def _read_cycle_parameters(self) -> Dict[str, Any]:
        """Read all relevant parameters for this cycle."""
        return {
            "confidence_threshold_auto": self.parameter_store.get(
                "classification.confidence_threshold.auto_apply"
            ),
            "confidence_threshold_review": self.parameter_store.get(
                "classification.confidence_threshold.review"
            ),
            "max_auto_per_cycle": self.parameter_store.get(
                "execution.auto_apply.max_per_cycle"
            ),
            "health_threshold_safe": self.parameter_store.get(
                "health.threshold.safe_for_auto"
            ),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # ACTION TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def _track_action(
        self,
        action: Any,
        status: str,
        system_health: float,
    ):
        """Track an action with outcome tracker and prediction logger."""
        action_id = getattr(action, 'id', f"action_{datetime.utcnow().timestamp()}")
        action_type = getattr(action, 'action_type', 'unknown')
        domain = getattr(action, 'domain', 'unknown')
        
        # Create prediction
        predicted_impact = getattr(action, 'predicted_impact', 5.0)
        confidence = getattr(action, 'confidence', 0.75)
        
        prediction = PredictedOutcome(
            metric_name="impact",
            baseline_value=0,
            predicted_value=predicted_impact,
            predicted_change_pct=predicted_impact,
            confidence=confidence,
            time_horizon_days=7,
        )
        
        # Register with outcome tracker
        self.outcome_tracker.register_action(
            action_id=action_id,
            action_type=action_type,
            domain=domain if isinstance(domain, str) else domain.value,
            predictions=[prediction],
            classification_lane=status,
            system_health=system_health,
        )
        
        # Log prediction
        self.prediction_logger.log_prediction(
            prediction_type=PredictionType.ACTION_IMPACT,
            predicted_value=predicted_impact,
            confidence=confidence,
            context_id=action_id,
            context_type="action",
            reasoning=f"Action {action_type} expected impact",
        )
    
    def _track_v311_action(
        self,
        action: Dict[str, Any],
        status: str,
        system_health: float,
    ):
        """Track a v3.1.1 optimization action."""
        action_id = f"v311_{action.get('type', 'unknown')}_{datetime.utcnow().timestamp()}"
        action_type = action.get("type", "unknown")
        domain = action.get("domain", "unknown")
        confidence = action.get("confidence", 0.5)
        
        # Estimate impact based on action type
        impact_map = {
            "badge_threshold": 2.0,
            "xp_rate": 3.0,
            "unlock_timing": 4.0,
            "day7_discount": 8.0,
            "intervention_order": 5.0,
            "discount_amount": 6.0,
            "bundle_pricing": 7.0,
            "copy_test": 2.0,
            "reminder_timing": 3.0,
        }
        predicted_impact = impact_map.get(action_type, 3.0)
        
        prediction = PredictedOutcome(
            metric_name="v311_impact",
            baseline_value=0,
            predicted_value=predicted_impact,
            predicted_change_pct=predicted_impact,
            confidence=confidence,
            time_horizon_days=14,
        )
        
        # Register with outcome tracker
        self.outcome_tracker.register_action(
            action_id=action_id,
            action_type=action_type,
            domain=domain,
            predictions=[prediction],
            classification_lane=status,
            system_health=system_health,
        )
        
        # Log prediction
        self.prediction_logger.log_prediction(
            prediction_type=PredictionType.ACTION_IMPACT,
            predicted_value=predicted_impact,
            confidence=confidence,
            context_id=action_id,
            context_type="v311_action",
            reasoning=action.get("reason", f"v3.1.1 {action_type} optimization"),
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # CALIBRATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _update_calibration_from_outcome(self, outcome: OutcomeRecord):
        """Update calibration based on an assessed outcome."""
        if outcome.prediction_accuracy is None:
            return
        
        # If prediction was way off, adjust parameters
        if outcome.prediction_accuracy < 0.5:
            # Consider proposing calibration adjustment
            self._maybe_propose_calibration_adjustment(outcome)
    
    def _count_calibration_updates(self) -> int:
        """Count calibration updates this cycle."""
        # Check prediction logger for recent calibration changes
        summary = self.prediction_logger.get_calibration_summary()
        return len([c for c in summary.values() if c.get("sample_size", 0) > 0])
    
    def _maybe_propose_calibration_adjustment(self, outcome: OutcomeRecord):
        """Maybe create a proposal for calibration adjustment."""
        # Only propose if we have enough evidence
        accuracy = self.outcome_tracker.get_accuracy_for_action_type(outcome.action_type)
        if accuracy is None or accuracy > 0.6:
            return
        
        # Create proposal
        evidence = ProposalEvidence(
            metric_name="prediction_accuracy",
            current_value=accuracy,
            historical_values=[],
            trend="declining",
            confidence=0.8,
            source="outcome_tracker",
        )
        
        impact = ProposalImpact(
            metric_name="prediction_accuracy",
            current_value=accuracy,
            predicted_value=accuracy + 0.1,
            prediction_confidence=0.6,
        )
        
        risk = ProposalRisk(
            reversible=True,
            rollback_plan="Revert calibration factors",
            affected_scope="action_type",
            affected_users_estimate=0,
            revenue_at_risk=0,
            confidence_in_assessment=0.7,
        )
        
        self.proposal_manager.create_proposal(
            proposal_type=ProposalType.CALIBRATION_RESET,
            title=f"Recalibrate predictions for {outcome.action_type}",
            description=f"Prediction accuracy for {outcome.action_type} is {accuracy:.0%}, below threshold",
            current_state={"accuracy": accuracy, "action_type": outcome.action_type},
            proposed_state={"action": "recalibrate", "action_type": outcome.action_type},
            evidence=[evidence],
            expected_impacts=[impact],
            risk_assessment=risk,
            priority=ProposalPriority.MEDIUM,
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL OPPORTUNITIES
    # ─────────────────────────────────────────────────────────────────────
    
    def _check_proposal_opportunities(self, health: SystemHealth) -> List[Proposal]:
        """Check for opportunities to propose self-improvements."""
        proposals = []
        
        # Check for lane promotion opportunities
        lane_proposals = self._check_lane_promotion_opportunities()
        proposals.extend(lane_proposals)
        
        # Check for parameter adjustment opportunities
        param_proposals = self._check_parameter_opportunities(health)
        proposals.extend(param_proposals)
        
        return proposals
    
    def _check_lane_promotion_opportunities(self) -> List[Proposal]:
        """Check if any action types should be promoted to auto lane."""
        proposals = []
        
        # Get success rates by action type
        summary = self.outcome_tracker.get_learning_summary()
        success_rates = summary.get("success_rate_by_action_type", {})
        
        for action_type, success_rate in success_rates.items():
            # If success rate is very high, consider promotion
            if success_rate >= 0.95:
                evidence = ProposalEvidence(
                    metric_name="success_rate",
                    current_value=success_rate,
                    trend="stable",
                    confidence=0.9,
                    source="outcome_tracker",
                )
                
                impact = ProposalImpact(
                    metric_name="time_saved",
                    current_value=0,
                    predicted_value=4,  # hours per action
                    prediction_confidence=0.8,
                )
                
                risk = ProposalRisk(
                    reversible=True,
                    rollback_plan="Demote back to review lane",
                    affected_scope="action_type",
                    affected_users_estimate=0,
                    revenue_at_risk=0,
                    confidence_in_assessment=0.85,
                    mitigation_steps=["A/B test first 5 auto-applies"],
                )
                
                proposal = self.proposal_manager.create_proposal(
                    proposal_type=ProposalType.LANE_CHANGE,
                    title=f"Promote {action_type} to AUTO lane",
                    description=f"{success_rate:.0%} success rate suggests safe for auto-apply",
                    current_state={"lane": "review", "action_type": action_type},
                    proposed_state={"lane": "auto", "action_type": action_type},
                    evidence=[evidence],
                    expected_impacts=[impact],
                    risk_assessment=risk,
                    priority=ProposalPriority.LOW,
                )
                proposals.append(proposal)
        
        return proposals
    
    def _check_parameter_opportunities(self, health: SystemHealth) -> List[Proposal]:
        """Check if any parameters should be adjusted."""
        proposals = []
        
        # If health is consistently high, maybe we can be more aggressive
        if health.level == HealthLevel.OPTIMAL:
            current_threshold = self.parameter_store.get(
                "classification.confidence_threshold.auto_apply"
            )
            
            # Propose lowering threshold slightly
            if current_threshold > 0.80:
                evidence = ProposalEvidence(
                    metric_name="system_health",
                    current_value=health.score,
                    trend="stable",
                    confidence=0.85,
                    source="health_calculator",
                )
                
                risk = ProposalRisk(
                    reversible=True,
                    rollback_plan="Increase threshold back",
                    affected_scope="parameter",
                    affected_users_estimate=0,
                    revenue_at_risk=0,
                    confidence_in_assessment=0.8,
                )
                
                proposal = self.proposal_manager.create_proposal(
                    proposal_type=ProposalType.PARAMETER_ADJUST,
                    title="Lower auto-apply confidence threshold",
                    description=f"System health optimal ({health.score:.0f}), can be more aggressive",
                    current_state={
                        "parameter": "classification.confidence_threshold.auto_apply",
                        "value": current_threshold,
                    },
                    proposed_state={
                        "parameter": "classification.confidence_threshold.auto_apply",
                        "value": current_threshold - 0.02,
                    },
                    evidence=[evidence],
                    expected_impacts=[],
                    risk_assessment=risk,
                    priority=ProposalPriority.LOW,
                )
                proposals.append(proposal)
        
        return proposals
    
    # ─────────────────────────────────────────────────────────────────────
    # STATUS & REPORTING
    # ─────────────────────────────────────────────────────────────────────
    
    def get_status(self) -> Dict:
        """Get current status of the Meta orchestrator."""
        return {
            "version": self.VERSION,
            "mode": self.mode.value,
            "cycle_count": self.cycle_count,
            "session_start": self.session_start.isoformat(),
            "total_actions_applied": self.total_actions_applied,
            "total_outcomes_assessed": self.total_outcomes_assessed,
            "last_health": self.last_health.to_dict() if self.last_health else None,
            "pending_proposals": len(self.proposal_manager.get_pending()),
            "pending_outcomes": len(self.outcome_tracker.pending_assessment),
            # v3.1.1 metrics
            "v311": {
                "actions_generated": self.v311_actions_generated,
                "optimizations_suggested": self.v311_optimizations_suggested,
            },
            # v5.1 SEO metrics
            "seo": {
                "actions_generated": self.seo_actions_generated,
                "optimizations_suggested": self.seo_optimizations_suggested,
            },
        }
    
    def get_seo_health(self) -> Dict:
        """Get SEO health summary for dashboard."""
        if not self.last_blog_health:
            self.last_blog_health = self.blog_observer.get_health()
        
        health = self.last_blog_health
        return {
            "overall_score": health.overall_score,
            "seo_score": health.seo_score,
            "engagement_score": health.engagement_score,
            "content_score": health.content_score,
            "cta_score": health.cta_score,
            "impressions": {
                "total": health.total_impressions,
                "trend": health.impressions_trend,
            },
            "clicks": {
                "total": health.total_clicks,
                "trend": health.clicks_trend,
            },
            "ctr": {
                "current": health.avg_ctr,
                "trend": health.ctr_trend,
            },
            "position": {
                "average": health.avg_position,
            },
            "pages": {
                "total": health.total_pages,
                "performing": health.pages_performing,
                "declining": health.pages_declining,
                "need_refresh": health.pages_need_refresh,
            },
            "top_pages": health.top_pages,
            "declining_pages": health.declining_pages,
            "opportunities": {
                "keywords": health.keyword_opportunities,
                "content_refresh": health.content_refresh_needed,
            },
            "issues": health.issues,
        }
    
    def get_v311_health(self) -> Dict:
        """Get health summary for all v3.1.1 systems."""
        return {
            "achievement": {
                "score": self.last_achievement_health.overall_score if self.last_achievement_health else 0,
                "badge_engagement": self.last_achievement_health.badge_engagement if self.last_achievement_health else 0,
                "streak_health": self.last_achievement_health.streak_health if self.last_achievement_health else 0,
                "issues": self.last_achievement_health.issues if self.last_achievement_health else [],
            },
            "retention": {
                "score": self.last_retention_health.overall_score if self.last_retention_health else 0,
                "mrr_saved_30d": self.last_retention_health.mrr_saved_30d if self.last_retention_health else 0,
                "save_rate": self.last_retention_health.save_rate if self.last_retention_health else 0,
                "issues": self.last_retention_health.issues if self.last_retention_health else [],
            },
            "bundle": {
                "score": self.last_bundle_health.overall_score if self.last_bundle_health else 0,
                "bundle_share": self.last_bundle_health.bundle_share if self.last_bundle_health else 0,
                "bundle_mrr": self.last_bundle_health.bundle_mrr if self.last_bundle_health else 0,
                "issues": self.last_bundle_health.issues if self.last_bundle_health else [],
            },
            "progressive": {
                "score": self.last_progressive_health.overall_score if self.last_progressive_health else 0,
                "progression_rate": self.last_progressive_health.progression_rate if self.last_progressive_health else 0,
                "day7_conversion": self.last_progressive_health.day7_offer.conversion_rate if self.last_progressive_health else 0,
                "issues": self.last_progressive_health.issues if self.last_progressive_health else [],
            },
        }
    
    def get_v311_summary(self) -> Dict:
        """Get comprehensive v3.1.1 system summary."""
        v311_health = self.get_v311_health()
        seo_health = self.get_seo_health()
        
        # Calculate overall v3.1.1 score (including blog)
        scores = [
            v311_health["achievement"]["score"],
            v311_health["retention"]["score"],
            v311_health["bundle"]["score"],
            v311_health["progressive"]["score"],
            seo_health["overall_score"],  # v5.1
        ]
        overall_v311_score = sum(scores) / len(scores) if scores else 0
        
        # Collect all issues
        all_issues = (
            v311_health["achievement"]["issues"] +
            v311_health["retention"]["issues"] +
            v311_health["bundle"]["issues"] +
            v311_health["progressive"]["issues"] +
            seo_health["issues"]  # v5.1
        )
        
        return {
            "version": "3.1.1",
            "orchestrator_version": self.VERSION,
            "overall_score": overall_v311_score,
            "systems": v311_health,
            "seo": seo_health,  # v5.1
            "total_issues": len(all_issues),
            "issues": all_issues,
            "actions_generated": self.v311_actions_generated + self.seo_actions_generated,
            "optimizations_suggested": self.v311_optimizations_suggested + self.seo_optimizations_suggested,
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_meta_orchestrator: Optional[MetaOrchestrator] = None

def get_meta_orchestrator() -> MetaOrchestrator:
    """Get the global Meta orchestrator instance."""
    global _meta_orchestrator
    if _meta_orchestrator is None:
        _meta_orchestrator = MetaOrchestrator()
    return _meta_orchestrator


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "MetaMode",
    "MetaCycleResult",
    "MetaOrchestrator",
    "get_meta_orchestrator",
]
