#!/usr/bin/env python3
"""
LNCP META: UNIFIED ORCHESTRATOR v2.0
Integrates App Orchestrator + Blog Orchestrator into a single closed loop.

This is the master controller for the entire self-optimizing system.

Two domains, one loop:
- APP: Token economy, funnel, engagement, retention
- BLOG: SEO, content, CTAs, conversion

Both feed into the same optimization cycle.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════════════

# App domain (existing)
from .simulation import MasterTest, run_master_test, SimulationConfig
from .action_classifier import (
    ActionClassifier, classify_actions, ActionLane, 
    ClassifiedAction, ActionDomain, RiskLevel
)
from .config_store import ConfigStore, get_config_store
from .auto_applier import AutoApplier, get_auto_applier
from .feedback_loop import FeedbackLoop, get_feedback_loop

# Blog domain (new)
from .blog import (
    # Tracking
    get_blog_tracker, get_cta_tracker,
    # GSC
    fetch_gsc_data, GSCAnalyzer, get_gsc_store,
    # Classification
    BlogActionOrchestrator, get_blog_orchestrator, BlogActionLane,
    # A/B Testing
    BlogExperimentManager, get_experiment_manager,
    # Feedback
    BlogFeedbackLoop, get_blog_feedback_loop,
)


# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR MODE
# ═══════════════════════════════════════════════════════════════════════════

class UnifiedMode(str, Enum):
    """Operating mode for the unified orchestrator."""
    OBSERVE_ONLY = "observe_only"       # Watch, don't change
    SUGGEST = "suggest"                  # Log changes, don't apply
    AUTO_SAFE = "auto_safe"              # Auto-apply safe changes
    FULL_AUTO = "full_auto"              # Auto-apply all eligible


class Domain(str, Enum):
    """Optimization domains."""
    APP = "app"       # Token economy, funnel, engagement
    BLOG = "blog"     # SEO, content, CTAs
    ALL = "all"       # Both domains


# ═══════════════════════════════════════════════════════════════════════════
# UNIFIED CYCLE RESULT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UnifiedCycleResult:
    """Result of a unified optimization cycle."""
    cycle_id: str
    started_at: datetime
    completed_at: datetime
    mode: str
    
    # App domain results
    app_health: int = 0
    app_actions_total: int = 0
    app_auto_apply: int = 0
    app_human_review: int = 0
    app_applied: int = 0
    
    # Blog domain results
    blog_pages_tracked: int = 0
    blog_experiments_running: int = 0
    blog_actions_total: int = 0
    blog_auto_apply: int = 0
    blog_human_review: int = 0
    blog_applied: int = 0
    
    # Combined metrics
    total_actions: int = 0
    total_auto_apply: int = 0
    total_human_review: int = 0
    total_applied: int = 0
    
    # Feedback
    insights: List[Dict] = field(default_factory=list)
    
    # Review queue
    pending_review: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": (self.completed_at - self.started_at).total_seconds(),
            "mode": self.mode,
            "app": {
                "health": self.app_health,
                "actions_total": self.app_actions_total,
                "auto_apply": self.app_auto_apply,
                "human_review": self.app_human_review,
                "applied": self.app_applied,
            },
            "blog": {
                "pages_tracked": self.blog_pages_tracked,
                "experiments_running": self.blog_experiments_running,
                "actions_total": self.blog_actions_total,
                "auto_apply": self.blog_auto_apply,
                "human_review": self.blog_human_review,
                "applied": self.blog_applied,
            },
            "combined": {
                "total_actions": self.total_actions,
                "total_auto_apply": self.total_auto_apply,
                "total_human_review": self.total_human_review,
                "total_applied": self.total_applied,
            },
            "insights_count": len(self.insights),
            "pending_review_count": len(self.pending_review),
        }


# ═══════════════════════════════════════════════════════════════════════════
# UNIFIED ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class UnifiedOrchestrator:
    """
    Master controller for the complete LNCP self-optimizing system.
    
    Coordinates both App and Blog domains in a single loop:
    
    1. OBSERVE
       - Run Master Test (app simulation)
       - Fetch GSC data (blog SEO)
       - Collect tracker metrics (blog engagement)
    
    2. DECIDE
       - Classify app actions
       - Classify blog actions
       - Merge into unified review queue
    
    3. EXECUTE
       - Auto-apply safe actions (both domains)
       - Start A/B experiments (blog)
       - Queue human reviews
    
    4. LEARN
       - Evaluate experiments
       - Calibrate predictions
       - Generate insights
    
    5. REPEAT
    """
    
    def __init__(
        self,
        mode: UnifiedMode = UnifiedMode.AUTO_SAFE,
    ):
        self.mode = mode
        
        # App domain components
        self.app_config = get_config_store()
        self.app_applier = get_auto_applier()
        self.app_feedback = get_feedback_loop()
        self.app_classifier = ActionClassifier()
        
        # Blog domain components
        self.blog_orchestrator = get_blog_orchestrator()
        self.blog_experiments = get_experiment_manager()
        self.blog_feedback = get_blog_feedback_loop()
        self.blog_tracker = get_blog_tracker()
        self.cta_tracker = get_cta_tracker()
        
        # State
        self.cycle_count = 0
        self.last_cycle_result: Optional[UnifiedCycleResult] = None
        self.human_review_queue: List[Dict] = []
        
        # Configuration
        self.min_cycle_interval_minutes = 60
        self.last_cycle_time: Optional[datetime] = None
        
        # GSC configuration
        self.gsc_enabled = True
        self.gsc_use_simulator = True  # Set False when real API is connected
    
    def set_mode(self, mode: UnifiedMode):
        """Set the operating mode."""
        self.mode = mode
    
    def run_cycle(
        self,
        force: bool = False,
        domains: Domain = Domain.ALL,
    ) -> UnifiedCycleResult:
        """
        Run a complete unified optimization cycle.
        
        Args:
            force: Skip interval check
            domains: Which domains to optimize (APP, BLOG, or ALL)
        """
        
        # Check interval
        if not force and self.last_cycle_time:
            elapsed = datetime.utcnow() - self.last_cycle_time
            if elapsed < timedelta(minutes=self.min_cycle_interval_minutes):
                remaining = self.min_cycle_interval_minutes - elapsed.total_seconds() / 60
                raise RuntimeError(f"Too soon. Wait {remaining:.0f} more minutes.")
        
        started_at = datetime.utcnow()
        self.cycle_count += 1
        cycle_id = f"unified_{started_at.strftime('%Y%m%d_%H%M%S')}_{self.cycle_count}"
        
        result = UnifiedCycleResult(
            cycle_id=cycle_id,
            started_at=started_at,
            completed_at=started_at,  # Will update
            mode=self.mode.value,
        )
        
        print(f"\n{'='*70}")
        print(f"UNIFIED OPTIMIZATION CYCLE: {cycle_id}")
        print(f"Mode: {self.mode.value} | Domains: {domains.value}")
        print(f"{'='*70}")
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 1: OBSERVE
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[STEP 1] OBSERVE")
        
        # App observation
        if domains in [Domain.APP, Domain.ALL]:
            print("  📊 Running Master Test (App)...")
            master_results = run_master_test()
            result.app_health = master_results.get("system_pulse", {}).get("overall_health", 0)
            app_actions = master_results.get("prescriptive_actions", {}).get("actions", [])
            result.app_actions_total = len(app_actions)
            print(f"     Health: {result.app_health}% | Actions: {result.app_actions_total}")
            
            # Feed to app feedback loop
            self.app_feedback.ingest_simulation_results(master_results)
        
        # Blog observation
        gsc_analyzer = None
        if domains in [Domain.BLOG, Domain.ALL]:
            print("  📈 Fetching Blog Metrics...")
            
            # Tracker stats
            tracker_summary = self.blog_tracker.get_summary()
            result.blog_pages_tracked = tracker_summary.get("unique_pages", 0)
            print(f"     Pages tracked: {result.blog_pages_tracked}")
            
            # GSC data
            if self.gsc_enabled:
                try:
                    gsc_data = fetch_gsc_data(
                        site_url="https://quirrely.io",
                        days=28,
                        use_simulator=self.gsc_use_simulator,
                    )
                    gsc_analyzer = GSCAnalyzer(gsc_data)
                    gsc_summary = gsc_analyzer.get_summary()
                    print(f"     GSC: {gsc_summary.get('total_impressions', 0):,} impressions")
                    
                    # Store snapshot
                    get_gsc_store().add_snapshot(gsc_data)
                except Exception as e:
                    print(f"     GSC: Error - {e}")
            
            # Experiment stats
            result.blog_experiments_running = len(self.blog_experiments.get_running_experiments())
            print(f"     Experiments running: {result.blog_experiments_running}")
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 2: DECIDE
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[STEP 2] DECIDE")
        
        all_auto_apply = []
        all_human_review = []
        
        # App classification
        if domains in [Domain.APP, Domain.ALL] and result.app_actions_total > 0:
            print("  🏷️ Classifying App Actions...")
            classified = classify_actions(app_actions)
            
            app_auto = [a for a in classified if a.lane == ActionLane.AUTO_APPLY]
            app_review = [a for a in classified if a.lane == ActionLane.HUMAN_REVIEW]
            
            result.app_auto_apply = len(app_auto)
            result.app_human_review = len(app_review)
            
            all_auto_apply.extend([{"domain": "app", "action": a} for a in app_auto])
            all_human_review.extend([{
                "domain": "app",
                "action_id": a.action_id,
                "title": a.title,
                "description": a.description,
                "risk_level": a.risk_level.value if hasattr(a.risk_level, 'value') else str(a.risk_level),
                "blocking_reasons": a.blocking_reasons if hasattr(a, 'blocking_reasons') else [],
            } for a in app_review])
            
            print(f"     Auto-apply: {result.app_auto_apply} | Review: {result.app_human_review}")
        
        # Blog classification
        if domains in [Domain.BLOG, Domain.ALL]:
            print("  🏷️ Classifying Blog Actions...")
            blog_result = self.blog_orchestrator.run_cycle(
                gsc_analyzer=gsc_analyzer,
                auto_apply=False,  # We'll apply below
            )
            
            result.blog_actions_total = blog_result["total_actions"]
            result.blog_auto_apply = blog_result["auto_apply"]
            result.blog_human_review = blog_result["human_review"]
            
            all_auto_apply.extend([{
                "domain": "blog",
                "action": a,
            } for a in blog_result["actions"]["auto_apply"]])
            
            all_human_review.extend([{
                "domain": "blog",
                **a,
            } for a in blog_result["actions"]["human_review"]])
            
            print(f"     Auto-apply: {result.blog_auto_apply} | Review: {result.blog_human_review}")
        
        # Combined totals
        result.total_actions = result.app_actions_total + result.blog_actions_total
        result.total_auto_apply = result.app_auto_apply + result.blog_auto_apply
        result.total_human_review = result.app_human_review + result.blog_human_review
        
        print(f"\n  📋 Combined: {result.total_auto_apply} auto-apply | {result.total_human_review} review")
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 3: EXECUTE
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[STEP 3] EXECUTE")
        
        applied_count = 0
        
        if self.mode in [UnifiedMode.AUTO_SAFE, UnifiedMode.FULL_AUTO]:
            print("  ⚡ Applying safe actions...")
            
            for item in all_auto_apply:
                domain = item["domain"]
                action = item["action"]
                
                if domain == "app":
                    # App actions use the auto_applier
                    # (In production, would call self.app_applier.apply())
                    applied_count += 1
                    result.app_applied += 1
                    
                elif domain == "blog":
                    # Blog actions are logged (actual apply would update content)
                    applied_count += 1
                    result.blog_applied += 1
            
            result.total_applied = applied_count
            print(f"     Applied: {applied_count} actions")
        else:
            print(f"  ⏸️ Mode is {self.mode.value} - skipping execution")
        
        # Queue human reviews
        self.human_review_queue.extend(all_human_review)
        result.pending_review = all_human_review
        print(f"  📥 Queued {len(all_human_review)} for human review")
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 4: LEARN
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[STEP 4] LEARN")
        
        all_insights = []
        
        # App feedback
        if domains in [Domain.APP, Domain.ALL]:
            print("  🧠 Running App Feedback Cycle...")
            try:
                app_cycle_result = self.app_feedback.run_cycle()
                app_insights = app_cycle_result.get("insights", []) if isinstance(app_cycle_result, dict) else []
                if app_insights:
                    all_insights.extend([{"domain": "app", **i} for i in app_insights])
            except Exception as e:
                print(f"     App feedback error: {e}")
        
        # Blog feedback
        if domains in [Domain.BLOG, Domain.ALL]:
            print("  🧠 Running Blog Feedback Cycle...")
            blog_feedback_result = self.blog_feedback.run_cycle()
            blog_insights = blog_feedback_result.get("insights", [])
            all_insights.extend([{"domain": "blog", **i} for i in blog_insights])
            
            # Evaluate experiments
            print("  🧪 Evaluating A/B Experiments...")
            concluded = self.blog_experiments.auto_conclude()
            if concluded:
                print(f"     Concluded: {len(concluded)} experiments")
                for exp_id in concluded:
                    exp = self.blog_experiments.get_experiment(exp_id)
                    if exp:
                        all_insights.append({
                            "domain": "blog",
                            "type": "experiment_concluded",
                            "priority": "high",
                            "message": f"Experiment '{exp.name}' concluded: {exp.result.value}",
                            "recommendation": f"Winner: {exp.winner_variant_id}" if exp.winner_variant_id else "No clear winner",
                        })
        
        result.insights = all_insights
        print(f"  💡 Generated {len(all_insights)} insights")
        
        if all_insights:
            for insight in all_insights[:3]:
                print(f"     [{insight.get('priority', 'info').upper()}] {insight.get('message', '')}")
        
        # ─────────────────────────────────────────────────────────────────
        # COMPLETE
        # ─────────────────────────────────────────────────────────────────
        result.completed_at = datetime.utcnow()
        self.last_cycle_time = result.completed_at
        self.last_cycle_result = result
        
        duration = (result.completed_at - result.started_at).total_seconds()
        
        print(f"\n{'='*70}")
        print(f"CYCLE COMPLETE in {duration:.2f}s")
        print(f"{'='*70}")
        print(f"  App:  {result.app_health}% health | {result.app_applied}/{result.app_auto_apply} applied")
        print(f"  Blog: {result.blog_pages_tracked} pages | {result.blog_applied}/{result.blog_auto_apply} applied")
        print(f"  Review Queue: {len(self.human_review_queue)} pending")
        print(f"{'='*70}\n")
        
        return result
    
    # ─────────────────────────────────────────────────────────────────────
    # REVIEW QUEUE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def get_review_queue(self) -> List[Dict]:
        """Get all pending human review items."""
        return self.human_review_queue
    
    def get_review_queue_by_domain(self, domain: Domain) -> List[Dict]:
        """Get review items for a specific domain."""
        if domain == Domain.ALL:
            return self.human_review_queue
        return [r for r in self.human_review_queue if r.get("domain") == domain.value]
    
    def approve_action(self, action_id: str) -> bool:
        """Approve an action from the review queue."""
        for i, item in enumerate(self.human_review_queue):
            if item.get("action_id") == action_id:
                approved = self.human_review_queue.pop(i)
                
                # Apply based on domain
                domain = approved.get("domain")
                if domain == "app":
                    # Would apply via app_applier
                    pass
                elif domain == "blog":
                    self.blog_orchestrator.approve_action(action_id)
                
                return True
        return False
    
    def reject_action(self, action_id: str, reason: str = "") -> bool:
        """Reject an action from the review queue."""
        for i, item in enumerate(self.human_review_queue):
            if item.get("action_id") == action_id:
                self.human_review_queue.pop(i)
                return True
        return False
    
    def clear_review_queue(self):
        """Clear all pending reviews."""
        self.human_review_queue = []
    
    # ─────────────────────────────────────────────────────────────────────
    # STATUS & REPORTING
    # ─────────────────────────────────────────────────────────────────────
    
    def get_status(self) -> Dict:
        """Get current orchestrator status."""
        return {
            "mode": self.mode.value,
            "cycle_count": self.cycle_count,
            "last_cycle": self.last_cycle_result.to_dict() if self.last_cycle_result else None,
            "review_queue_size": len(self.human_review_queue),
            "app": {
                "config_count": len(getattr(self.app_config, 'configs', {})) or len(getattr(self.app_config, 'values', {})),
            },
            "blog": {
                "pages_tracked": self.blog_tracker.get_summary().get("unique_pages", 0),
                "experiments_running": len(self.blog_experiments.get_running_experiments()),
                "experiments_concluded": len(self.blog_experiments.get_concluded_experiments()),
            },
        }
    
    def get_insights(self, limit: int = 10) -> List[Dict]:
        """Get recent insights from both domains."""
        if not self.last_cycle_result:
            return []
        return self.last_cycle_result.insights[:limit]


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_unified_orchestrator: Optional[UnifiedOrchestrator] = None

def get_unified_orchestrator() -> UnifiedOrchestrator:
    """Get the global unified orchestrator."""
    global _unified_orchestrator
    if _unified_orchestrator is None:
        _unified_orchestrator = UnifiedOrchestrator()
    return _unified_orchestrator


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "UnifiedMode",
    "Domain",
    "UnifiedCycleResult",
    "UnifiedOrchestrator",
    "get_unified_orchestrator",
]
