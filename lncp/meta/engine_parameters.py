#!/usr/bin/env python3
"""
LNCP META: ENGINE PARAMETERS v4.2
Read-only layer for Engine parameters that Meta can propose changes to.

The Engine (tokens, profiles, scoring) is immutable code.
But its parameters (weights, thresholds, affinities) can be optimized.

This layer:
- Defines all tunable Engine parameters
- Tracks their current values (read from Engine)
- Allows Meta to propose changes (Super Admin only)
- Maintains audit trail of all Engine parameter changes

Changes flow: Meta proposes → Super Admin approves → Deploy new Engine version
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE PARAMETER CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

class EngineParameterCategory(str, Enum):
    """Categories of Engine parameters."""
    SCORING_WEIGHT = "scoring_weight"       # Token scoring weights
    SIGMOID_PARAM = "sigmoid_param"         # Sigmoid midpoints/scales
    PROFILE_AFFINITY = "profile_affinity"   # Profile-token affinities
    THRESHOLD = "threshold"                 # Classification thresholds
    VALUE_CALC = "value_calc"               # Token value calculation


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE PARAMETER DEFINITION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EngineParameter:
    """Definition of a tunable Engine parameter."""
    # Identity
    key: str
    name: str
    description: str
    category: EngineParameterCategory
    
    # Location in Engine
    module: str              # e.g., "scoring", "profiles", "value"
    variable: str            # e.g., "SIGMOID_MIDPOINT_ASSERTIVE"
    
    # Current value
    current_value: Any
    
    # Constraints
    value_type: str          # "float", "int", "tuple", "dict"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    # Impact assessment
    impact_scope: str = "scoring"  # What this affects
    requires_regression_test: bool = True
    
    # Audit
    last_changed: Optional[datetime] = None
    change_count: int = 0


@dataclass
class EngineParameterProposal:
    """Proposal to change an Engine parameter."""
    # Identity
    proposal_id: str
    parameter_key: str
    
    # Change
    current_value: Any
    proposed_value: Any
    
    # Justification
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    expected_impact: str = ""
    
    # Risk
    risk_assessment: str = ""
    rollback_plan: str = ""
    regression_tests_required: List[str] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, approved, rejected, deployed
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    deployed_at: Optional[datetime] = None
    deployed_version: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE PARAMETER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

# Define all tunable Engine parameters
# These mirror the hardcoded values in lncp/engine/scoring.py

ENGINE_PARAMETERS: Dict[str, EngineParameter] = {
    
    # ─────────────────────────────────────────────────────────────────────
    # SIGMOID PARAMETERS (scoring.py)
    # ─────────────────────────────────────────────────────────────────────
    
    "scoring.sigmoid.linear.midpoint": EngineParameter(
        key="scoring.sigmoid.linear.midpoint",
        name="Linear Token Sigmoid Midpoint",
        description="Sentence length midpoint for Linear structure scoring",
        category=EngineParameterCategory.SIGMOID_PARAM,
        module="scoring",
        variable="SIGMOID_LINEAR_MIDPOINT",
        current_value=15,
        value_type="float",
        min_value=5,
        max_value=30,
    ),
    
    "scoring.sigmoid.linear.scale": EngineParameter(
        key="scoring.sigmoid.linear.scale",
        name="Linear Token Sigmoid Scale",
        description="Sigmoid scale for Linear structure scoring",
        category=EngineParameterCategory.SIGMOID_PARAM,
        module="scoring",
        variable="SIGMOID_LINEAR_SCALE",
        current_value=5,
        value_type="float",
        min_value=1,
        max_value=15,
    ),
    
    "scoring.sigmoid.staccato.midpoint": EngineParameter(
        key="scoring.sigmoid.staccato.midpoint",
        name="Staccato Token Sigmoid Midpoint",
        description="Sentence length midpoint for Staccato rhythm scoring",
        category=EngineParameterCategory.SIGMOID_PARAM,
        module="scoring",
        variable="SIGMOID_STACCATO_MIDPOINT",
        current_value=10,
        value_type="float",
        min_value=3,
        max_value=20,
    ),
    
    "scoring.sigmoid.flowing.midpoint": EngineParameter(
        key="scoring.sigmoid.flowing.midpoint",
        name="Flowing Token Sigmoid Midpoint",
        description="Sentence length midpoint for Flowing rhythm scoring",
        category=EngineParameterCategory.SIGMOID_PARAM,
        module="scoring",
        variable="SIGMOID_FLOWING_MIDPOINT",
        current_value=20,
        value_type="float",
        min_value=10,
        max_value=40,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # PROFILE MATCHING WEIGHTS (scoring.py)
    # ─────────────────────────────────────────────────────────────────────
    
    "scoring.profile.primary_weight": EngineParameter(
        key="scoring.profile.primary_weight",
        name="Primary Token Weight",
        description="Weight of primary tokens in profile matching",
        category=EngineParameterCategory.SCORING_WEIGHT,
        module="scoring",
        variable="PROFILE_PRIMARY_WEIGHT",
        current_value=0.7,
        value_type="float",
        min_value=0.5,
        max_value=0.9,
    ),
    
    "scoring.profile.secondary_weight": EngineParameter(
        key="scoring.profile.secondary_weight",
        name="Secondary Token Weight",
        description="Weight of secondary tokens in profile matching",
        category=EngineParameterCategory.SCORING_WEIGHT,
        module="scoring",
        variable="PROFILE_SECONDARY_WEIGHT",
        current_value=0.3,
        value_type="float",
        min_value=0.1,
        max_value=0.5,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # TOKEN SCORING WEIGHTS (scoring.py)
    # ─────────────────────────────────────────────────────────────────────
    
    "scoring.token.assertive_multiplier": EngineParameter(
        key="scoring.token.assertive_multiplier",
        name="Assertive Word Multiplier",
        description="Multiplier for assertive word ratio in T01 scoring",
        category=EngineParameterCategory.SCORING_WEIGHT,
        module="scoring",
        variable="ASSERTIVE_MULTIPLIER",
        current_value=10,
        value_type="float",
        min_value=5,
        max_value=20,
    ),
    
    "scoring.token.hedge_multiplier": EngineParameter(
        key="scoring.token.hedge_multiplier",
        name="Hedge Word Multiplier",
        description="Multiplier for hedge word ratio in T02 scoring",
        category=EngineParameterCategory.SCORING_WEIGHT,
        module="scoring",
        variable="HEDGE_MULTIPLIER",
        current_value=10,
        value_type="float",
        min_value=5,
        max_value=20,
    ),
    
    "scoring.token.complexity_multiplier": EngineParameter(
        key="scoring.token.complexity_multiplier",
        name="Complexity Multiplier",
        description="Multiplier for complex word ratio in C01 scoring",
        category=EngineParameterCategory.SCORING_WEIGHT,
        module="scoring",
        variable="COMPLEXITY_MULTIPLIER",
        current_value=3,
        value_type="float",
        min_value=1,
        max_value=10,
    ),
    
    # ─────────────────────────────────────────────────────────────────────
    # VALUE CALCULATION (value.py)
    # ─────────────────────────────────────────────────────────────────────
    
    "value.base_token_value": EngineParameter(
        key="value.base_token_value",
        name="Base Token Value",
        description="Starting value for all tokens",
        category=EngineParameterCategory.VALUE_CALC,
        module="value",
        variable="BASE_TOKEN_VALUE",
        current_value=1.0,
        value_type="float",
        min_value=0.5,
        max_value=2.0,
    ),
    
    "value.analysis_value": EngineParameter(
        key="value.analysis_value",
        name="Analysis Value",
        description="Value contribution per analysis (log scale)",
        category=EngineParameterCategory.VALUE_CALC,
        module="value",
        variable="ANALYSIS_VALUE",
        current_value=0.5,
        value_type="float",
        min_value=0.1,
        max_value=1.0,
    ),
    
    "value.inactivity_decay_rate": EngineParameter(
        key="value.inactivity_decay_rate",
        name="Inactivity Decay Rate",
        description="Daily decay rate for inactive users",
        category=EngineParameterCategory.VALUE_CALC,
        module="value",
        variable="INACTIVITY_DECAY_RATE",
        current_value=0.02,
        value_type="float",
        min_value=0.01,
        max_value=0.05,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# ENGINE PARAMETER ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class EngineParameterAnalyzer:
    """
    Analyzes Engine performance and proposes parameter changes.
    
    This is how Meta identifies opportunities to improve the Engine.
    All changes require Super Admin approval.
    """
    
    def __init__(self):
        self.parameters = ENGINE_PARAMETERS.copy()
        self.proposals: Dict[str, EngineParameterProposal] = {}
        self.history: List[Dict] = []
        
        self._proposal_counter = 0
    
    # ─────────────────────────────────────────────────────────────────────
    # PARAMETER ACCESS (READ-ONLY)
    # ─────────────────────────────────────────────────────────────────────
    
    def get_parameter(self, key: str) -> Optional[EngineParameter]:
        """Get an Engine parameter definition."""
        return self.parameters.get(key)
    
    def get_all_parameters(self) -> Dict[str, EngineParameter]:
        """Get all Engine parameters."""
        return self.parameters.copy()
    
    def get_by_category(
        self, 
        category: EngineParameterCategory
    ) -> Dict[str, EngineParameter]:
        """Get parameters by category."""
        return {
            k: v for k, v in self.parameters.items()
            if v.category == category
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────────────────────
    
    def analyze_profile_accuracy(
        self,
        predictions: List[Dict],  # [{predicted: str, actual: str, confidence: float}]
    ) -> List[Dict]:
        """
        Analyze profile prediction accuracy to identify parameter issues.
        
        Returns recommendations for parameter adjustments.
        """
        recommendations = []
        
        if len(predictions) < 50:
            return []  # Not enough data
        
        # Calculate accuracy by profile
        by_profile: Dict[str, Dict] = {}
        for pred in predictions:
            profile = pred.get("predicted")
            if profile not in by_profile:
                by_profile[profile] = {"correct": 0, "total": 0}
            by_profile[profile]["total"] += 1
            if pred.get("predicted") == pred.get("actual"):
                by_profile[profile]["correct"] += 1
        
        # Find underperforming profiles
        for profile, stats in by_profile.items():
            if stats["total"] < 10:
                continue
            accuracy = stats["correct"] / stats["total"]
            
            if accuracy < 0.6:
                # This profile is being mispredicted
                recommendations.append({
                    "type": "profile_accuracy",
                    "profile": profile,
                    "accuracy": accuracy,
                    "sample_size": stats["total"],
                    "suggestion": f"Review token affinities for {profile}",
                })
        
        return recommendations
    
    def analyze_token_distribution(
        self,
        token_scores: List[Dict],  # [{token_id: str, score: float}]
    ) -> List[Dict]:
        """
        Analyze token score distributions to identify scoring issues.
        
        Returns recommendations for sigmoid/weight adjustments.
        """
        recommendations = []
        
        if len(token_scores) < 100:
            return []
        
        # Calculate distribution per token
        by_token: Dict[str, List[float]] = {}
        for scores in token_scores:
            for token_id, score in scores.items():
                if token_id not in by_token:
                    by_token[token_id] = []
                by_token[token_id].append(score)
        
        # Check for tokens that are always high or always low
        for token_id, scores in by_token.items():
            avg = sum(scores) / len(scores)
            
            if avg > 0.9:
                recommendations.append({
                    "type": "token_ceiling",
                    "token_id": token_id,
                    "avg_score": avg,
                    "suggestion": f"Token {token_id} scores too high, adjust sigmoid",
                })
            elif avg < 0.1:
                recommendations.append({
                    "type": "token_floor",
                    "token_id": token_id,
                    "avg_score": avg,
                    "suggestion": f"Token {token_id} scores too low, adjust sigmoid",
                })
        
        return recommendations
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL CREATION
    # ─────────────────────────────────────────────────────────────────────
    
    def create_proposal(
        self,
        parameter_key: str,
        proposed_value: Any,
        reason: str,
        evidence: Dict[str, Any],
        expected_impact: str,
    ) -> Optional[EngineParameterProposal]:
        """
        Create a proposal to change an Engine parameter.
        
        All proposals require Super Admin approval.
        """
        if parameter_key not in self.parameters:
            return None
        
        param = self.parameters[parameter_key]
        
        # Validate proposed value
        if param.min_value is not None and proposed_value < param.min_value:
            return None
        if param.max_value is not None and proposed_value > param.max_value:
            return None
        
        self._proposal_counter += 1
        proposal_id = f"engine_prop_{datetime.utcnow().strftime('%Y%m%d')}_{self._proposal_counter:03d}"
        
        proposal = EngineParameterProposal(
            proposal_id=proposal_id,
            parameter_key=parameter_key,
            current_value=param.current_value,
            proposed_value=proposed_value,
            reason=reason,
            evidence=evidence,
            expected_impact=expected_impact,
            risk_assessment=f"Affects {param.impact_scope}",
            rollback_plan=f"Revert {parameter_key} to {param.current_value}",
            regression_tests_required=["profile_accuracy", "token_distribution"],
        )
        
        self.proposals[proposal_id] = proposal
        
        return proposal
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def approve_proposal(
        self,
        proposal_id: str,
        approved_by: str,
    ) -> bool:
        """Approve a proposal (Super Admin only)."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.status = "approved"
        proposal.decided_at = datetime.utcnow()
        proposal.decided_by = approved_by
        
        # Record in history
        self.history.append({
            "action": "approved",
            "proposal_id": proposal_id,
            "parameter": proposal.parameter_key,
            "proposed_value": proposal.proposed_value,
            "approved_by": approved_by,
            "timestamp": datetime.utcnow(),
        })
        
        return True
    
    def reject_proposal(
        self,
        proposal_id: str,
        rejected_by: str,
        reason: str = "",
    ) -> bool:
        """Reject a proposal."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        proposal.status = "rejected"
        proposal.decided_at = datetime.utcnow()
        proposal.decided_by = rejected_by
        
        self.history.append({
            "action": "rejected",
            "proposal_id": proposal_id,
            "parameter": proposal.parameter_key,
            "rejected_by": rejected_by,
            "reason": reason,
            "timestamp": datetime.utcnow(),
        })
        
        return True
    
    def mark_deployed(
        self,
        proposal_id: str,
        version: str,
    ) -> bool:
        """Mark a proposal as deployed to a new Engine version."""
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal.status != "approved":
            return False
        
        proposal.status = "deployed"
        proposal.deployed_at = datetime.utcnow()
        proposal.deployed_version = version
        
        # Update parameter value
        if proposal.parameter_key in self.parameters:
            param = self.parameters[proposal.parameter_key]
            param.current_value = proposal.proposed_value
            param.last_changed = datetime.utcnow()
            param.change_count += 1
        
        self.history.append({
            "action": "deployed",
            "proposal_id": proposal_id,
            "parameter": proposal.parameter_key,
            "new_value": proposal.proposed_value,
            "version": version,
            "timestamp": datetime.utcnow(),
        })
        
        return True
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_pending_proposals(self) -> List[EngineParameterProposal]:
        """Get all pending proposals."""
        return [p for p in self.proposals.values() if p.status == "pending"]
    
    def get_proposal_history(self, limit: int = 20) -> List[Dict]:
        """Get recent proposal history."""
        return sorted(
            self.history,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
    
    def get_summary(self) -> Dict:
        """Get summary of Engine parameters and proposals."""
        return {
            "total_parameters": len(self.parameters),
            "by_category": {
                cat.value: len(self.get_by_category(cat))
                for cat in EngineParameterCategory
            },
            "proposals": {
                "total": len(self.proposals),
                "pending": len([p for p in self.proposals.values() if p.status == "pending"]),
                "approved": len([p for p in self.proposals.values() if p.status == "approved"]),
                "deployed": len([p for p in self.proposals.values() if p.status == "deployed"]),
            },
            "changes_deployed": sum(p.change_count for p in self.parameters.values()),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_engine_analyzer: Optional[EngineParameterAnalyzer] = None

def get_engine_analyzer() -> EngineParameterAnalyzer:
    """Get the global Engine parameter analyzer."""
    global _engine_analyzer
    if _engine_analyzer is None:
        _engine_analyzer = EngineParameterAnalyzer()
    return _engine_analyzer


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "EngineParameterCategory",
    "EngineParameter",
    "EngineParameterProposal",
    "ENGINE_PARAMETERS",
    "EngineParameterAnalyzer",
    "get_engine_analyzer",
]
