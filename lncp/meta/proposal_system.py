#!/usr/bin/env python3
"""
LNCP META: PROPOSAL SYSTEM v4.1
Structured way for Meta to request changes to itself and the system.

When Meta identifies an opportunity to improve, it creates a Proposal.
Proposals go through different lanes based on their scope and risk:
- AUTO: Meta can apply without review
- REVIEW: Standard human review
- SUPER_ADMIN: Requires Super Admin approval

This enables Meta to evolve while maintaining control.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# PROPOSAL TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ProposalType(str, Enum):
    """Types of changes Meta can propose."""
    # Parameter changes
    PARAMETER_ADJUST = "parameter_adjust"       # Adjust a Meta parameter
    PARAMETER_EXPAND = "parameter_expand"       # Expand parameter boundaries
    
    # Classification changes
    LANE_CHANGE = "lane_change"                 # Move action type to different lane
    TRUST_OVERRIDE = "trust_override"           # Override trust score
    
    # Execution changes
    AB_TEST_CONCLUDE = "ab_test_conclude"       # Conclude an experiment
    ROLLBACK = "rollback"                       # Revert a change
    
    # Learning changes
    CALIBRATION_RESET = "calibration_reset"     # Reset calibration factors
    
    # System changes
    NEW_SIGNAL = "new_signal"                   # Add new observation signal
    NEW_ACTION_TYPE = "new_action_type"         # Add new action type
    ARCHITECTURE_CHANGE = "architecture_change" # Change system architecture


class ProposalLane(str, Enum):
    """Where does this proposal go?"""
    AUTO = "auto"               # Meta can apply automatically
    REVIEW = "review"           # Standard review queue
    SUPER_ADMIN = "super_admin" # Requires Super Admin


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    DRAFT = "draft"             # Being prepared
    PENDING = "pending"         # Awaiting decision
    APPROVED = "approved"       # Approved, ready to execute
    REJECTED = "rejected"       # Rejected
    EXECUTED = "executed"       # Applied successfully
    FAILED = "failed"           # Execution failed
    WITHDRAWN = "withdrawn"     # Meta withdrew it


class ProposalPriority(str, Enum):
    """How urgent is this proposal?"""
    CRITICAL = "critical"       # Must address immediately
    HIGH = "high"               # Important, address soon
    MEDIUM = "medium"           # Normal priority
    LOW = "low"                 # When convenient


# ═══════════════════════════════════════════════════════════════════════════
# PROPOSAL DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ProposalEvidence:
    """Evidence supporting a proposal."""
    metric_name: str
    current_value: float
    historical_values: List[float] = field(default_factory=list)
    trend: str = ""                    # "improving", "stable", "declining"
    confidence: float = 0.0
    source: str = ""                   # Where this evidence came from


@dataclass
class ProposalImpact:
    """Expected impact of the proposal."""
    metric_name: str
    current_value: float
    predicted_value: float
    prediction_confidence: float
    worst_case_value: Optional[float] = None
    best_case_value: Optional[float] = None


@dataclass
class ProposalRisk:
    """Risk assessment for the proposal."""
    reversible: bool
    rollback_plan: str
    affected_scope: str               # "parameter", "action_type", "domain", "system"
    affected_users_estimate: int
    revenue_at_risk: float
    confidence_in_assessment: float
    mitigation_steps: List[str] = field(default_factory=list)


@dataclass
class Proposal:
    """
    A complete proposal for Meta to change something.
    
    This is the structured format for all self-modification requests.
    """
    # Identity
    proposal_id: str
    proposal_type: ProposalType
    title: str
    description: str
    
    # Classification
    lane: ProposalLane
    priority: ProposalPriority
    status: ProposalStatus = ProposalStatus.DRAFT
    
    # Content
    current_state: Dict[str, Any] = field(default_factory=dict)
    proposed_state: Dict[str, Any] = field(default_factory=dict)
    
    # Supporting information
    evidence: List[ProposalEvidence] = field(default_factory=list)
    expected_impacts: List[ProposalImpact] = field(default_factory=list)
    risk_assessment: Optional[ProposalRisk] = None
    
    # Recommendation
    recommendation: str = ""          # "approve", "reject", "defer", "needs_more_data"
    recommendation_reasoning: str = ""
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    
    # Decision
    decided_by: Optional[str] = None  # "auto", "reviewer", "super_admin"
    decision_notes: str = ""
    
    # Execution
    execution_result: Optional[str] = None
    execution_error: Optional[str] = None
    
    # Tracking
    cycle_id: Optional[str] = None
    related_proposals: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "proposal_id": self.proposal_id,
            "type": self.proposal_type.value,
            "title": self.title,
            "description": self.description,
            "lane": self.lane.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "current_state": self.current_state,
            "proposed_state": self.proposed_state,
            "recommendation": self.recommendation,
            "evidence_count": len(self.evidence),
            "created_at": self.created_at.isoformat(),
            "risk": {
                "reversible": self.risk_assessment.reversible if self.risk_assessment else None,
                "scope": self.risk_assessment.affected_scope if self.risk_assessment else None,
            } if self.risk_assessment else None,
        }
    
    def to_display_dict(self) -> Dict:
        """Full display format for Super Admin dashboard."""
        return {
            "proposal_id": self.proposal_id,
            "type": self.proposal_type.value,
            "title": self.title,
            "description": self.description,
            "lane": self.lane.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "current_state": self.current_state,
            "proposed_state": self.proposed_state,
            "evidence": [
                {
                    "metric": e.metric_name,
                    "current": e.current_value,
                    "trend": e.trend,
                    "confidence": e.confidence,
                }
                for e in self.evidence
            ],
            "expected_impacts": [
                {
                    "metric": i.metric_name,
                    "current": i.current_value,
                    "predicted": i.predicted_value,
                    "confidence": i.prediction_confidence,
                }
                for i in self.expected_impacts
            ],
            "risk_assessment": {
                "reversible": self.risk_assessment.reversible,
                "rollback_plan": self.risk_assessment.rollback_plan,
                "scope": self.risk_assessment.affected_scope,
                "users_affected": self.risk_assessment.affected_users_estimate,
                "revenue_at_risk": self.risk_assessment.revenue_at_risk,
                "mitigations": self.risk_assessment.mitigation_steps,
            } if self.risk_assessment else None,
            "recommendation": self.recommendation,
            "recommendation_reasoning": self.recommendation_reasoning,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PROPOSAL LANE RULES
# ═══════════════════════════════════════════════════════════════════════════

# Rules for which proposals go to which lane
LANE_RULES: Dict[ProposalType, Dict] = {
    ProposalType.PARAMETER_ADJUST: {
        "default_lane": ProposalLane.AUTO,
        "super_admin_if": ["requires_super_admin", "outside_auto_bounds"],
        "review_if": ["large_change", "affects_revenue"],
    },
    ProposalType.PARAMETER_EXPAND: {
        "default_lane": ProposalLane.SUPER_ADMIN,
        "review_if": [],
        "auto_if": [],
    },
    ProposalType.LANE_CHANGE: {
        "default_lane": ProposalLane.REVIEW,
        "super_admin_if": ["to_auto_lane", "affects_core"],
        "auto_if": ["to_stricter_lane"],
    },
    ProposalType.TRUST_OVERRIDE: {
        "default_lane": ProposalLane.REVIEW,
        "super_admin_if": ["increase_trust"],
        "auto_if": ["decrease_trust"],
    },
    ProposalType.AB_TEST_CONCLUDE: {
        "default_lane": ProposalLane.AUTO,
        "review_if": ["inconclusive", "negative_result"],
        "super_admin_if": [],
    },
    ProposalType.ROLLBACK: {
        "default_lane": ProposalLane.AUTO,
        "review_if": ["partial_rollback"],
        "super_admin_if": [],
    },
    ProposalType.CALIBRATION_RESET: {
        "default_lane": ProposalLane.REVIEW,
        "super_admin_if": ["full_reset"],
        "auto_if": ["minor_adjustment"],
    },
    ProposalType.NEW_SIGNAL: {
        "default_lane": ProposalLane.SUPER_ADMIN,
        "review_if": [],
        "auto_if": [],
    },
    ProposalType.NEW_ACTION_TYPE: {
        "default_lane": ProposalLane.SUPER_ADMIN,
        "review_if": [],
        "auto_if": [],
    },
    ProposalType.ARCHITECTURE_CHANGE: {
        "default_lane": ProposalLane.SUPER_ADMIN,
        "review_if": [],
        "auto_if": [],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# PROPOSAL MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ProposalManager:
    """
    Manages the lifecycle of all proposals.
    
    This is how Meta formally requests changes to itself.
    """
    
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.pending_by_lane: Dict[ProposalLane, List[str]] = {
            lane: [] for lane in ProposalLane
        }
        
        # Counters
        self._proposal_counter = 0
        
        # Callbacks for execution
        self.executors: Dict[ProposalType, Callable[[Proposal], bool]] = {}
    
    # ─────────────────────────────────────────────────────────────────────
    # CREATION
    # ─────────────────────────────────────────────────────────────────────
    
    def create_proposal(
        self,
        proposal_type: ProposalType,
        title: str,
        description: str,
        current_state: Dict[str, Any],
        proposed_state: Dict[str, Any],
        evidence: List[ProposalEvidence],
        expected_impacts: List[ProposalImpact],
        risk_assessment: ProposalRisk,
        priority: ProposalPriority = ProposalPriority.MEDIUM,
        cycle_id: Optional[str] = None,
    ) -> Proposal:
        """Create a new proposal."""
        self._proposal_counter += 1
        proposal_id = f"prop_{datetime.utcnow().strftime('%Y%m%d')}_{self._proposal_counter:04d}"
        
        # Determine lane
        lane = self._determine_lane(
            proposal_type, current_state, proposed_state, risk_assessment
        )
        
        # Generate recommendation
        recommendation, reasoning = self._generate_recommendation(
            proposal_type, evidence, expected_impacts, risk_assessment
        )
        
        # Set expiration (proposals don't last forever)
        expires_at = datetime.utcnow() + timedelta(days=7)
        if priority == ProposalPriority.CRITICAL:
            expires_at = datetime.utcnow() + timedelta(hours=24)
        elif priority == ProposalPriority.HIGH:
            expires_at = datetime.utcnow() + timedelta(days=3)
        
        proposal = Proposal(
            proposal_id=proposal_id,
            proposal_type=proposal_type,
            title=title,
            description=description,
            lane=lane,
            priority=priority,
            status=ProposalStatus.PENDING,
            current_state=current_state,
            proposed_state=proposed_state,
            evidence=evidence,
            expected_impacts=expected_impacts,
            risk_assessment=risk_assessment,
            recommendation=recommendation,
            recommendation_reasoning=reasoning,
            expires_at=expires_at,
            cycle_id=cycle_id,
        )
        
        self.proposals[proposal_id] = proposal
        self.pending_by_lane[lane].append(proposal_id)
        
        # Auto-execute if in AUTO lane
        if lane == ProposalLane.AUTO:
            self._auto_execute(proposal)
        
        return proposal
    
    def _determine_lane(
        self,
        proposal_type: ProposalType,
        current_state: Dict,
        proposed_state: Dict,
        risk: ProposalRisk,
    ) -> ProposalLane:
        """Determine which lane this proposal should go to."""
        rules = LANE_RULES.get(proposal_type, {"default_lane": ProposalLane.REVIEW})
        
        # Check super_admin conditions
        if "requires_super_admin" in rules.get("super_admin_if", []):
            if proposed_state.get("requires_super_admin"):
                return ProposalLane.SUPER_ADMIN
        
        if "affects_core" in rules.get("super_admin_if", []):
            if risk.affected_scope == "system":
                return ProposalLane.SUPER_ADMIN
        
        if "to_auto_lane" in rules.get("super_admin_if", []):
            if proposed_state.get("new_lane") == "auto":
                return ProposalLane.SUPER_ADMIN
        
        # Check review conditions
        if "large_change" in rules.get("review_if", []):
            change_pct = self._calculate_change_pct(current_state, proposed_state)
            if change_pct > 20:
                return ProposalLane.REVIEW
        
        if "affects_revenue" in rules.get("review_if", []):
            if risk.revenue_at_risk > 1000:
                return ProposalLane.REVIEW
        
        # Check auto conditions
        if "to_stricter_lane" in rules.get("auto_if", []):
            # Moving to stricter lane is always safe
            return ProposalLane.AUTO
        
        if "decrease_trust" in rules.get("auto_if", []):
            return ProposalLane.AUTO
        
        return rules["default_lane"]
    
    def _calculate_change_pct(
        self,
        current_state: Dict,
        proposed_state: Dict,
    ) -> float:
        """Calculate percentage change between states."""
        if "value" in current_state and "value" in proposed_state:
            current = current_state["value"]
            proposed = proposed_state["value"]
            if current != 0:
                return abs((proposed - current) / current) * 100
        return 0.0
    
    def _generate_recommendation(
        self,
        proposal_type: ProposalType,
        evidence: List[ProposalEvidence],
        impacts: List[ProposalImpact],
        risk: ProposalRisk,
    ) -> tuple:
        """Generate a recommendation for this proposal."""
        # Calculate evidence strength
        avg_confidence = sum(e.confidence for e in evidence) / len(evidence) if evidence else 0
        
        # Calculate expected benefit
        positive_impacts = [
            i for i in impacts 
            if i.predicted_value > i.current_value and i.prediction_confidence > 0.6
        ]
        
        # Calculate risk score
        risk_score = 0
        if not risk.reversible:
            risk_score += 30
        if risk.revenue_at_risk > 5000:
            risk_score += 25
        if risk.affected_scope == "system":
            risk_score += 20
        if risk.confidence_in_assessment < 0.7:
            risk_score += 15
        
        # Generate recommendation
        if avg_confidence < 0.5:
            return "needs_more_data", "Insufficient evidence confidence"
        
        if risk_score > 50:
            if len(positive_impacts) > 0 and avg_confidence > 0.8:
                return "approve", f"High risk but strong evidence ({avg_confidence:.0%} confidence)"
            return "reject", f"Risk too high (score: {risk_score})"
        
        if len(positive_impacts) >= 1 and avg_confidence >= 0.7:
            return "approve", f"Positive expected impact with {avg_confidence:.0%} confidence"
        
        if len(positive_impacts) == 0:
            return "defer", "No clear positive impact predicted"
        
        return "approve", "Acceptable risk/reward balance"
    
    def _auto_execute(self, proposal: Proposal):
        """Automatically execute an AUTO lane proposal."""
        proposal.decided_at = datetime.utcnow()
        proposal.decided_by = "auto"
        proposal.status = ProposalStatus.APPROVED
        
        # Execute if we have an executor
        if proposal.proposal_type in self.executors:
            try:
                success = self.executors[proposal.proposal_type](proposal)
                if success:
                    proposal.status = ProposalStatus.EXECUTED
                    proposal.executed_at = datetime.utcnow()
                    proposal.execution_result = "success"
                else:
                    proposal.status = ProposalStatus.FAILED
                    proposal.execution_error = "Executor returned False"
            except Exception as e:
                proposal.status = ProposalStatus.FAILED
                proposal.execution_error = str(e)
        
        # Remove from pending
        if proposal.proposal_id in self.pending_by_lane[ProposalLane.AUTO]:
            self.pending_by_lane[ProposalLane.AUTO].remove(proposal.proposal_id)
    
    # ─────────────────────────────────────────────────────────────────────
    # DECISION
    # ─────────────────────────────────────────────────────────────────────
    
    def approve(
        self,
        proposal_id: str,
        decided_by: str,
        notes: str = "",
    ) -> bool:
        """Approve a proposal."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.PENDING:
            return False
        
        proposal.status = ProposalStatus.APPROVED
        proposal.decided_at = datetime.utcnow()
        proposal.decided_by = decided_by
        proposal.decision_notes = notes
        
        # Remove from pending
        if proposal_id in self.pending_by_lane[proposal.lane]:
            self.pending_by_lane[proposal.lane].remove(proposal_id)
        
        return True
    
    def reject(
        self,
        proposal_id: str,
        decided_by: str,
        notes: str = "",
    ) -> bool:
        """Reject a proposal."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.PENDING:
            return False
        
        proposal.status = ProposalStatus.REJECTED
        proposal.decided_at = datetime.utcnow()
        proposal.decided_by = decided_by
        proposal.decision_notes = notes
        
        # Remove from pending
        if proposal_id in self.pending_by_lane[proposal.lane]:
            self.pending_by_lane[proposal.lane].remove(proposal_id)
        
        return True
    
    def defer(
        self,
        proposal_id: str,
        new_expires_at: datetime,
    ) -> bool:
        """Defer a proposal to a later time."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.expires_at = new_expires_at
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────
    # EXECUTION
    # ─────────────────────────────────────────────────────────────────────
    
    def execute(self, proposal_id: str) -> bool:
        """Execute an approved proposal."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != ProposalStatus.APPROVED:
            return False
        
        if proposal.proposal_type not in self.executors:
            proposal.status = ProposalStatus.FAILED
            proposal.execution_error = "No executor registered"
            return False
        
        try:
            success = self.executors[proposal.proposal_type](proposal)
            if success:
                proposal.status = ProposalStatus.EXECUTED
                proposal.executed_at = datetime.utcnow()
                proposal.execution_result = "success"
                return True
            else:
                proposal.status = ProposalStatus.FAILED
                proposal.execution_error = "Executor returned False"
                return False
        except Exception as e:
            proposal.status = ProposalStatus.FAILED
            proposal.execution_error = str(e)
            return False
    
    def register_executor(
        self,
        proposal_type: ProposalType,
        executor: Callable[[Proposal], bool],
    ):
        """Register an executor function for a proposal type."""
        self.executors[proposal_type] = executor
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_pending(self, lane: Optional[ProposalLane] = None) -> List[Proposal]:
        """Get pending proposals, optionally filtered by lane."""
        if lane:
            return [
                self.proposals[pid] 
                for pid in self.pending_by_lane[lane]
                if pid in self.proposals
            ]
        
        all_pending = []
        for lane_proposals in self.pending_by_lane.values():
            all_pending.extend([
                self.proposals[pid] 
                for pid in lane_proposals
                if pid in self.proposals
            ])
        return all_pending
    
    def get_pending_for_super_admin(self) -> List[Proposal]:
        """Get proposals requiring Super Admin attention."""
        return self.get_pending(ProposalLane.SUPER_ADMIN)
    
    def get_expired(self) -> List[Proposal]:
        """Get proposals that have expired."""
        now = datetime.utcnow()
        return [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.PENDING
            and p.expires_at
            and p.expires_at < now
        ]
    
    def get_recent(self, days: int = 7) -> List[Proposal]:
        """Get recent proposals."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return sorted([
            p for p in self.proposals.values()
            if p.created_at >= cutoff
        ], key=lambda p: p.created_at, reverse=True)
    
    def get_summary(self) -> Dict:
        """Get summary of proposal activity."""
        all_proposals = list(self.proposals.values())
        
        return {
            "total": len(all_proposals),
            "pending": {
                "total": sum(len(l) for l in self.pending_by_lane.values()),
                "auto": len(self.pending_by_lane[ProposalLane.AUTO]),
                "review": len(self.pending_by_lane[ProposalLane.REVIEW]),
                "super_admin": len(self.pending_by_lane[ProposalLane.SUPER_ADMIN]),
            },
            "by_status": {
                status.value: sum(1 for p in all_proposals if p.status == status)
                for status in ProposalStatus
            },
            "by_type": {
                ptype.value: sum(1 for p in all_proposals if p.proposal_type == ptype)
                for ptype in ProposalType
            },
            "approval_rate": self._calculate_approval_rate(),
            "avg_time_to_decision_hours": self._calculate_avg_decision_time(),
        }
    
    def _calculate_approval_rate(self) -> float:
        """Calculate approval rate for decided proposals."""
        decided = [
            p for p in self.proposals.values()
            if p.status in [ProposalStatus.APPROVED, ProposalStatus.REJECTED, 
                           ProposalStatus.EXECUTED, ProposalStatus.FAILED]
        ]
        if not decided:
            return 0.0
        
        approved = sum(
            1 for p in decided 
            if p.status in [ProposalStatus.APPROVED, ProposalStatus.EXECUTED]
        )
        return approved / len(decided)
    
    def _calculate_avg_decision_time(self) -> float:
        """Calculate average time to decision in hours."""
        decided = [
            p for p in self.proposals.values()
            if p.decided_at and p.status != ProposalStatus.PENDING
        ]
        if not decided:
            return 0.0
        
        total_hours = sum(
            (p.decided_at - p.created_at).total_seconds() / 3600
            for p in decided
        )
        return total_hours / len(decided)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_proposal_manager: Optional[ProposalManager] = None

def get_proposal_manager() -> ProposalManager:
    """Get the global proposal manager instance."""
    global _proposal_manager
    if _proposal_manager is None:
        _proposal_manager = ProposalManager()
    return _proposal_manager


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
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
]
