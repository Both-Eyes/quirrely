#!/usr/bin/env python3
"""
QUIRRELY CLOSED-LOOP: ORCHESTRATOR v1.0
The master controller that runs the complete closed-loop system.

This is the conductor. It coordinates all components:
- Master Test (observation)
- Action Classifier (decision)
- Auto-Applier (execution)
- Feedback Loop (learning)

The result: A self-optimizing system that improves without human intervention
for safe changes, while surfacing complex decisions to humans.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json
import sys

sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app/backend')

from master_test import MasterTest, run_master_test
from closed_loop.action_classifier import ActionClassifier, classify_actions, ActionLane
from closed_loop.config_store import ConfigStore, get_config_store
from closed_loop.auto_applier import AutoApplier, get_auto_applier
from closed_loop.feedback_loop import FeedbackLoop, get_feedback_loop


# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR STATE
# ═══════════════════════════════════════════════════════════════════════════

class OrchestratorMode(str, Enum):
    OBSERVE_ONLY = "observe_only"       # Just watch, don't change anything
    SUGGEST = "suggest"                  # Suggest changes, don't apply
    AUTO_SAFE = "auto_safe"              # Auto-apply safe changes only
    FULL_AUTO = "full_auto"              # Auto-apply all eligible changes


@dataclass
class CycleResult:
    """Result of a single optimization cycle."""
    cycle_id: str
    started_at: datetime
    completed_at: datetime
    
    # Master Test results
    system_health: int
    total_actions: int
    
    # Classification results
    auto_apply_count: int
    human_review_count: int
    blocked_count: int
    
    # Execution results
    changes_applied: int
    experiments_started: int
    rollbacks_triggered: int
    
    # Feedback results
    anomalies_detected: int
    calibration_updates: int
    insights_generated: int
    
    # Human review queue
    pending_review: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            "cycle_id": self.cycle_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": (self.completed_at - self.started_at).total_seconds(),
            "system_health": self.system_health,
            "total_actions": self.total_actions,
            "auto_apply_count": self.auto_apply_count,
            "human_review_count": self.human_review_count,
            "blocked_count": self.blocked_count,
            "changes_applied": self.changes_applied,
            "experiments_started": self.experiments_started,
            "rollbacks_triggered": self.rollbacks_triggered,
            "anomalies_detected": self.anomalies_detected,
            "calibration_updates": self.calibration_updates,
            "insights_generated": self.insights_generated,
            "pending_review": self.pending_review,
        }


# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class ClosedLoopOrchestrator:
    """
    The master controller for the self-optimizing system.
    
    Coordinates:
    1. OBSERVE: Run Master Test to understand current state
    2. DECIDE: Classify actions into auto-apply vs human-review
    3. EXECUTE: Apply safe changes, queue others for review
    4. LEARN: Collect feedback, calibrate predictions
    5. REPEAT: Run continuously or on schedule
    """
    
    def __init__(
        self,
        mode: OrchestratorMode = OrchestratorMode.AUTO_SAFE,
        config_store: Optional[ConfigStore] = None,
        auto_applier: Optional[AutoApplier] = None,
        feedback_loop: Optional[FeedbackLoop] = None,
    ):
        self.mode = mode
        self.config_store = config_store or get_config_store()
        self.auto_applier = auto_applier or get_auto_applier()
        self.feedback_loop = feedback_loop or get_feedback_loop()
        self.classifier = ActionClassifier()
        
        # State
        self.cycle_count = 0
        self.last_cycle_result: Optional[CycleResult] = None
        self.human_review_queue: List[Dict] = []
        
        # Configuration
        self.min_cycle_interval_minutes = 60  # Don't run more than once per hour
        self.last_cycle_time: Optional[datetime] = None
    
    def run_cycle(self, force: bool = False) -> CycleResult:
        """Run a complete optimization cycle."""
        
        # Check if we should run
        if not force and self.last_cycle_time:
            elapsed = datetime.utcnow() - self.last_cycle_time
            if elapsed < timedelta(minutes=self.min_cycle_interval_minutes):
                raise RuntimeError(f"Too soon to run. Wait {self.min_cycle_interval_minutes - elapsed.total_seconds() / 60:.0f} more minutes.")
        
        started_at = datetime.utcnow()
        self.cycle_count += 1
        cycle_id = f"cycle_{started_at.strftime('%Y%m%d_%H%M%S')}_{self.cycle_count}"
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 1: OBSERVE - Run Master Test
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[{cycle_id}] STEP 1: OBSERVE")
        master_test_results = run_master_test()
        
        system_health = master_test_results.get("system_pulse", {}).get("overall_health", 0)
        actions = master_test_results.get("prescriptive_actions", {}).get("actions", [])
        
        print(f"  System Health: {system_health}%")
        print(f"  Actions Generated: {len(actions)}")
        
        # Ingest into feedback loop
        self.feedback_loop.ingest_simulation_results(master_test_results)
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 2: DECIDE - Classify actions
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[{cycle_id}] STEP 2: DECIDE")
        classification = classify_actions(actions)
        
        auto_apply = classification["auto_apply"]
        human_review = classification["human_review"]
        blocked = classification["blocked"]
        
        print(f"  Auto-Apply: {len(auto_apply)}")
        print(f"  Human Review: {len(human_review)}")
        print(f"  Blocked: {len(blocked)}")
        
        # Add to human review queue
        for action in human_review:
            action["queued_at"] = datetime.utcnow().isoformat()
            action["cycle_id"] = cycle_id
            self.human_review_queue.append(action)
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 3: EXECUTE - Apply changes (if mode allows)
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[{cycle_id}] STEP 3: EXECUTE")
        
        changes_applied = 0
        experiments_started = 0
        rollbacks_triggered = 0
        
        if self.mode in [OrchestratorMode.AUTO_SAFE, OrchestratorMode.FULL_AUTO]:
            # Check for degraded metrics first
            rollbacks = self.auto_applier.check_and_rollback_degraded()
            rollbacks_triggered = len(rollbacks)
            
            if rollbacks:
                print(f"  ⚠️ Rolled back {rollbacks_triggered} degraded changes")
            
            # Apply new changes
            for action_dict in auto_apply:
                try:
                    # Convert back to ClassifiedAction for applier
                    from closed_loop.action_classifier import ClassifiedAction, ActionLane, ActionDomain, RiskLevel
                    
                    classified = ClassifiedAction(
                        action_id=action_dict["action_id"],
                        title=action_dict["title"],
                        description=action_dict.get("description", ""),
                        category=action_dict.get("category", ""),
                        severity=action_dict.get("severity", ""),
                        lane=ActionLane.AUTO_APPLY,
                        domain=ActionDomain(action_dict.get("domain", "threshold")),
                        risk_level=RiskLevel(action_dict.get("risk_level", "low")),
                        confidence=action_dict.get("confidence", 0.75),
                        config_key=action_dict.get("config_key"),
                        current_value=action_dict.get("current_value"),
                        proposed_value=action_dict.get("proposed_value"),
                        requires_ab_test=action_dict.get("requires_ab_test", False),
                        success_metric=action_dict.get("success_metric"),
                        success_threshold=action_dict.get("success_threshold"),
                    )
                    
                    if classified.config_key and classified.proposed_value is not None:
                        applied = self.auto_applier.apply(classified)
                        
                        if applied.experiment_id:
                            experiments_started += 1
                            print(f"  🧪 Started experiment: {classified.title}")
                        else:
                            changes_applied += 1
                            print(f"  ✅ Applied: {classified.title}")
                    
                except Exception as e:
                    print(f"  ❌ Failed to apply: {action_dict.get('title')} - {e}")
        
        elif self.mode == OrchestratorMode.SUGGEST:
            print("  Mode: SUGGEST - Changes logged but not applied")
            for action in auto_apply:
                print(f"  📋 Would apply: {action['title']}")
        
        else:
            print("  Mode: OBSERVE_ONLY - No changes")
        
        # ─────────────────────────────────────────────────────────────────
        # STEP 4: LEARN - Run feedback cycle
        # ─────────────────────────────────────────────────────────────────
        print(f"\n[{cycle_id}] STEP 4: LEARN")
        
        feedback_result = self.feedback_loop.run_cycle()
        
        anomalies_detected = len(feedback_result.get("anomalies", []))
        calibration_updates = 1 if feedback_result.get("calibration") else 0
        insights_generated = len(feedback_result.get("insights", []))
        
        print(f"  Anomalies: {anomalies_detected}")
        print(f"  Calibration Updated: {'Yes' if calibration_updates else 'No'}")
        print(f"  Insights: {insights_generated}")
        
        for insight in feedback_result.get("insights", []):
            print(f"    💡 {insight['message']}")
        
        # ─────────────────────────────────────────────────────────────────
        # COMPLETE
        # ─────────────────────────────────────────────────────────────────
        completed_at = datetime.utcnow()
        self.last_cycle_time = completed_at
        
        result = CycleResult(
            cycle_id=cycle_id,
            started_at=started_at,
            completed_at=completed_at,
            system_health=system_health,
            total_actions=len(actions),
            auto_apply_count=len(auto_apply),
            human_review_count=len(human_review),
            blocked_count=len(blocked),
            changes_applied=changes_applied,
            experiments_started=experiments_started,
            rollbacks_triggered=rollbacks_triggered,
            anomalies_detected=anomalies_detected,
            calibration_updates=calibration_updates,
            insights_generated=insights_generated,
            pending_review=self.human_review_queue[-10:],  # Last 10
        )
        
        self.last_cycle_result = result
        
        print(f"\n[{cycle_id}] COMPLETE")
        print(f"  Duration: {(completed_at - started_at).total_seconds():.2f}s")
        print(f"  Changes Applied: {changes_applied}")
        print(f"  Experiments Started: {experiments_started}")
        print(f"  Pending Human Review: {len(self.human_review_queue)}")
        
        return result
    
    def get_human_review_queue(self) -> List[Dict]:
        """Get pending items for human review."""
        return self.human_review_queue
    
    def approve_human_review(self, action_id: str) -> bool:
        """Approve an item from human review queue."""
        for i, action in enumerate(self.human_review_queue):
            if action.get("action_id") == action_id:
                # Remove from queue
                approved = self.human_review_queue.pop(i)
                
                # Apply the change
                # (In production, this would trigger the actual change)
                print(f"Approved: {approved.get('title')}")
                
                return True
        return False
    
    def reject_human_review(self, action_id: str, reason: str = "") -> bool:
        """Reject an item from human review queue."""
        for i, action in enumerate(self.human_review_queue):
            if action.get("action_id") == action_id:
                rejected = self.human_review_queue.pop(i)
                print(f"Rejected: {rejected.get('title')} - {reason}")
                return True
        return False
    
    def get_status(self) -> Dict:
        """Get current orchestrator status."""
        return {
            "mode": self.mode.value,
            "cycle_count": self.cycle_count,
            "last_cycle": self.last_cycle_result.to_dict() if self.last_cycle_result else None,
            "human_review_queue_size": len(self.human_review_queue),
            "auto_applier_status": self.auto_applier.get_status(),
            "feedback_loop_status": self.feedback_loop.get_status(),
            "config_store_changes": len(self.config_store.get_history(hours=24)),
        }
    
    def set_mode(self, mode: OrchestratorMode):
        """Change the orchestrator mode."""
        old_mode = self.mode
        self.mode = mode
        print(f"Mode changed: {old_mode.value} → {mode.value}")


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_orchestrator: Optional[ClosedLoopOrchestrator] = None

def get_orchestrator() -> ClosedLoopOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ClosedLoopOrchestrator()
    return _orchestrator


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("QUIRRELY CLOSED-LOOP ORCHESTRATOR")
    print("=" * 70)
    print()
    print("The self-optimizing system that:")
    print("  1. OBSERVES  - Runs Master Test simulations")
    print("  2. DECIDES   - Classifies actions (auto vs human)")
    print("  3. EXECUTES  - Applies safe changes automatically")
    print("  4. LEARNS    - Calibrates from real vs predicted")
    print()
    print("=" * 70)
    
    # Create orchestrator in AUTO_SAFE mode
    orchestrator = ClosedLoopOrchestrator(mode=OrchestratorMode.AUTO_SAFE)
    
    # Run a cycle
    result = orchestrator.run_cycle(force=True)
    
    print()
    print("=" * 70)
    print("CYCLE SUMMARY")
    print("=" * 70)
    print(json.dumps(result.to_dict(), indent=2, default=str))
    
    print()
    print("=" * 70)
    print("SYSTEM STATUS")
    print("=" * 70)
    print(json.dumps(orchestrator.get_status(), indent=2, default=str))
