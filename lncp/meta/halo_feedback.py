#!/usr/bin/env python3
"""
LNCP META: HALO FEEDBACK LOOP v1.0.0
Self-learning safety optimization.

This module:
1. Learns from false positives and negatives
2. Tracks pattern effectiveness
3. Proposes pattern adjustments
4. Auto-tunes severity thresholds
5. Feeds improvements back to HALO detector

The feedback loop enables:
- Fewer false positives → Better UX
- Catch more actual violations → Safer platform
- Continuous improvement without manual intervention
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import defaultdict
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lncp.meta.halo_observer import (
    HALOObserver, get_halo_observer,
    SafetySignals, UserSafetyScore, PatternPerformance,
    HALOCategory, SeverityTier
)
from lncp.meta.events.schema import EventType, AppEvent, UserTier


# ═══════════════════════════════════════════════════════════════════════════
# FEEDBACK DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PatternFeedback:
    """Feedback on a specific HALO pattern."""
    pattern_id: str
    pattern_text: str
    severity: SeverityTier
    category: HALOCategory
    
    # Outcomes
    true_positives: int = 0   # Correctly caught violations
    false_positives: int = 0  # Wrongly flagged safe content
    true_negatives: int = 0   # Correctly allowed safe content
    false_negatives: int = 0  # Missed actual violations
    
    # Context
    contexts_triggered: List[str] = field(default_factory=list)
    
    @property
    def precision(self) -> float:
        """How often triggers are actual violations."""
        total_positive = self.true_positives + self.false_positives
        if total_positive == 0:
            return 1.0
        return self.true_positives / total_positive
    
    @property
    def recall(self) -> float:
        """How many actual violations we catch."""
        total_actual = self.true_positives + self.false_negatives
        if total_actual == 0:
            return 1.0
        return self.true_positives / total_actual
    
    @property
    def f1_score(self) -> float:
        """Harmonic mean of precision and recall."""
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)
    
    @property
    def recommendation(self) -> str:
        """Get improvement recommendation."""
        if self.precision < 0.7:
            return "tighten"  # Too many false positives, make more specific
        elif self.recall < 0.7:
            return "loosen"   # Missing too much, broaden pattern
        elif self.precision < 0.9 and self.severity == SeverityTier.T3:
            return "downgrade"  # High severity needs high precision
        else:
            return "keep"


@dataclass
class SeverityAdjustment:
    """Proposed adjustment to severity tier."""
    pattern_id: str
    current_tier: SeverityTier
    proposed_tier: SeverityTier
    reason: str
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternProposal:
    """Proposed new or modified pattern."""
    action: str  # "add", "modify", "remove", "adjust_severity"
    pattern_id: str
    current_pattern: Optional[str]
    proposed_pattern: Optional[str]
    severity: SeverityTier
    category: HALOCategory
    reason: str
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# HALO FEEDBACK LOOP
# ═══════════════════════════════════════════════════════════════════════════

class HALOFeedbackLoop:
    """
    Learns from HALO outcomes and proposes improvements.
    
    The feedback loop:
    1. Collects outcomes (was the violation real? did user appeal?)
    2. Analyzes pattern performance
    3. Proposes adjustments
    4. Tracks improvement over time
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "data/halo_feedback.db"
        self.observer = get_halo_observer()
        self.pattern_feedback: Dict[str, PatternFeedback] = {}
        self.pending_proposals: List[PatternProposal] = []
        self.applied_changes: List[Dict] = []
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pattern_feedback (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_text TEXT,
                    severity TEXT,
                    category TEXT,
                    true_positives INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    true_negatives INTEGER DEFAULT 0,
                    false_negatives INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT,
                    pattern_id TEXT,
                    current_pattern TEXT,
                    proposed_pattern TEXT,
                    severity TEXT,
                    category TEXT,
                    reason TEXT,
                    confidence REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    resolved_at TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS applied_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_type TEXT,
                    pattern_id TEXT,
                    before_state TEXT,
                    after_state TEXT,
                    impact TEXT,
                    applied_at TEXT,
                    applied_by TEXT
                )
            ''')
            
            conn.commit()
    
    def record_outcome(self, 
                      pattern_id: str,
                      was_violation: bool,
                      was_flagged: bool,
                      content_snippet: str = "",
                      user_appealed: bool = False,
                      appeal_result: Optional[bool] = None):
        """
        Record the outcome of a HALO check.
        
        Args:
            pattern_id: Which pattern triggered (or should have)
            was_violation: Was this actually a violation?
            was_flagged: Did HALO flag it?
            content_snippet: Sample of content (for analysis)
            user_appealed: Did user appeal?
            appeal_result: Was appeal successful? (True = false positive)
        """
        if pattern_id not in self.pattern_feedback:
            self.pattern_feedback[pattern_id] = PatternFeedback(
                pattern_id=pattern_id,
                pattern_text="",
                severity=SeverityTier.T1,
                category=HALOCategory.LANGUAGE
            )
        
        fb = self.pattern_feedback[pattern_id]
        
        if was_flagged and was_violation:
            fb.true_positives += 1
        elif was_flagged and not was_violation:
            fb.false_positives += 1
        elif not was_flagged and not was_violation:
            fb.true_negatives += 1
        elif not was_flagged and was_violation:
            fb.false_negatives += 1
        
        # Store context for pattern improvement
        if content_snippet:
            fb.contexts_triggered.append(content_snippet[:200])
            # Keep only recent 100
            fb.contexts_triggered = fb.contexts_triggered[-100:]
        
        # Appeal overrides our assessment
        if user_appealed and appeal_result is not None:
            if appeal_result:  # Appeal successful = we were wrong
                fb.false_positives += 1
                fb.true_positives = max(0, fb.true_positives - 1)
    
    def analyze_patterns(self) -> List[PatternProposal]:
        """
        Analyze all patterns and generate improvement proposals.
        
        Returns list of proposals for Command Center review.
        """
        proposals = []
        
        for pattern_id, fb in self.pattern_feedback.items():
            total = fb.true_positives + fb.false_positives
            if total < 10:
                continue  # Need more data
            
            # Check precision
            if fb.precision < 0.7:
                proposals.append(PatternProposal(
                    action="modify",
                    pattern_id=pattern_id,
                    current_pattern=fb.pattern_text,
                    proposed_pattern=None,  # Needs human review
                    severity=fb.severity,
                    category=fb.category,
                    reason=f"Low precision ({fb.precision:.0%}) - too many false positives",
                    confidence=0.8,
                    evidence={
                        "precision": fb.precision,
                        "false_positives": fb.false_positives,
                        "sample_contexts": fb.contexts_triggered[:5]
                    }
                ))
            
            # Check if severity should be adjusted
            if fb.precision < 0.8 and fb.severity == SeverityTier.T3:
                proposals.append(PatternProposal(
                    action="adjust_severity",
                    pattern_id=pattern_id,
                    current_pattern=fb.pattern_text,
                    proposed_pattern=fb.pattern_text,
                    severity=SeverityTier.T2,  # Downgrade
                    category=fb.category,
                    reason=f"T3 pattern with only {fb.precision:.0%} precision - downgrade to T2",
                    confidence=0.9,
                    evidence={
                        "current_severity": fb.severity.value,
                        "precision": fb.precision,
                    }
                ))
            
            # Check for patterns that are never triggered
            # (This would need integration with HALO detector to know)
        
        self.pending_proposals = proposals
        return proposals
    
    def analyze_false_positive_clusters(self) -> List[Dict]:
        """
        Find patterns in false positives to suggest improvements.
        
        Returns clusters of similar false positives.
        """
        clusters = []
        
        for pattern_id, fb in self.pattern_feedback.items():
            if fb.false_positives < 3:
                continue
            
            # Group similar contexts
            contexts = fb.contexts_triggered
            
            # Simple clustering: find common words/phrases
            word_counts = defaultdict(int)
            for ctx in contexts:
                words = ctx.lower().split()
                for word in words:
                    if len(word) > 3:
                        word_counts[word] += 1
            
            common_words = [w for w, c in word_counts.items() if c >= len(contexts) * 0.3]
            
            if common_words:
                clusters.append({
                    "pattern_id": pattern_id,
                    "false_positive_count": fb.false_positives,
                    "common_words": common_words[:10],
                    "sample_contexts": contexts[:3],
                    "suggestion": f"Consider excluding contexts with: {', '.join(common_words[:5])}"
                })
        
        return clusters
    
    def get_severity_recommendations(self) -> List[SeverityAdjustment]:
        """
        Get recommendations for severity tier adjustments.
        """
        recommendations = []
        
        for pattern_id, fb in self.pattern_feedback.items():
            total = fb.true_positives + fb.false_positives
            if total < 20:
                continue
            
            # T3 patterns must have very high precision
            if fb.severity == SeverityTier.T3 and fb.precision < 0.95:
                recommendations.append(SeverityAdjustment(
                    pattern_id=pattern_id,
                    current_tier=SeverityTier.T3,
                    proposed_tier=SeverityTier.T2,
                    reason=f"Precision {fb.precision:.0%} too low for T3 (blocks immediately)",
                    confidence=0.85,
                    evidence={"precision": fb.precision, "total": total}
                ))
            
            # T2 patterns with very high precision could be T3
            if fb.severity == SeverityTier.T2 and fb.precision > 0.98 and total > 50:
                recommendations.append(SeverityAdjustment(
                    pattern_id=pattern_id,
                    current_tier=SeverityTier.T2,
                    proposed_tier=SeverityTier.T3,
                    reason=f"Very high precision {fb.precision:.0%} - could be T3",
                    confidence=0.7,
                    evidence={"precision": fb.precision, "total": total}
                ))
            
            # T1 patterns that are always violations could be T2
            if fb.severity == SeverityTier.T1 and fb.precision > 0.95 and total > 30:
                recommendations.append(SeverityAdjustment(
                    pattern_id=pattern_id,
                    current_tier=SeverityTier.T1,
                    proposed_tier=SeverityTier.T2,
                    reason=f"High precision {fb.precision:.0%} - consider T2",
                    confidence=0.6,
                    evidence={"precision": fb.precision, "total": total}
                ))
        
        return recommendations
    
    def apply_proposal(self, proposal_id: str, approved_by: str) -> Dict:
        """
        Apply an approved proposal.
        
        This creates a change record and returns the update to apply
        to HALO detector.
        """
        # Find proposal
        proposal = None
        for p in self.pending_proposals:
            if p.pattern_id == proposal_id:
                proposal = p
                break
        
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        # Record the change
        change = {
            "change_type": proposal.action,
            "pattern_id": proposal.pattern_id,
            "before_state": proposal.current_pattern,
            "after_state": proposal.proposed_pattern,
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "applied_by": approved_by,
        }
        
        self.applied_changes.append(change)
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO applied_changes
                (change_type, pattern_id, before_state, after_state, applied_at, applied_by)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                change["change_type"],
                change["pattern_id"],
                change["before_state"],
                change["after_state"],
                change["applied_at"],
                change["applied_by"]
            ))
            conn.commit()
        
        # Remove from pending
        self.pending_proposals = [p for p in self.pending_proposals if p.pattern_id != proposal_id]
        
        return {
            "success": True,
            "change": change,
            "instruction": self._generate_update_instruction(proposal)
        }
    
    def _generate_update_instruction(self, proposal: PatternProposal) -> Dict:
        """Generate instruction for HALO detector update."""
        if proposal.action == "adjust_severity":
            return {
                "type": "severity_change",
                "pattern_id": proposal.pattern_id,
                "new_severity": proposal.severity.value,
            }
        elif proposal.action == "modify":
            return {
                "type": "pattern_modification",
                "pattern_id": proposal.pattern_id,
                "old_pattern": proposal.current_pattern,
                "new_pattern": proposal.proposed_pattern,
                "requires_manual_review": proposal.proposed_pattern is None,
            }
        elif proposal.action == "remove":
            return {
                "type": "pattern_removal",
                "pattern_id": proposal.pattern_id,
            }
        elif proposal.action == "add":
            return {
                "type": "pattern_addition",
                "pattern": proposal.proposed_pattern,
                "severity": proposal.severity.value,
                "category": proposal.category.value,
            }
        return {}
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what the feedback loop has learned."""
        total_patterns = len(self.pattern_feedback)
        
        low_precision = sum(1 for fb in self.pattern_feedback.values() if fb.precision < 0.8)
        high_precision = sum(1 for fb in self.pattern_feedback.values() if fb.precision > 0.95)
        
        total_outcomes = sum(
            fb.true_positives + fb.false_positives + fb.true_negatives + fb.false_negatives
            for fb in self.pattern_feedback.values()
        )
        
        total_false_positives = sum(fb.false_positives for fb in self.pattern_feedback.values())
        total_true_positives = sum(fb.true_positives for fb in self.pattern_feedback.values())
        
        overall_precision = (
            total_true_positives / (total_true_positives + total_false_positives)
            if (total_true_positives + total_false_positives) > 0
            else 1.0
        )
        
        return {
            "patterns_tracked": total_patterns,
            "patterns_low_precision": low_precision,
            "patterns_high_precision": high_precision,
            "total_outcomes_recorded": total_outcomes,
            "overall_precision": overall_precision,
            "pending_proposals": len(self.pending_proposals),
            "applied_changes": len(self.applied_changes),
            "health_status": "healthy" if overall_precision > 0.9 else "needs_attention",
        }
    
    def get_health_inputs(self) -> Dict[str, Any]:
        """Get inputs for Meta health calculation."""
        summary = self.get_learning_summary()
        
        # Health based on precision and proposal queue
        health_score = summary["overall_precision"] * 100
        
        # Penalize for too many pending proposals
        if summary["pending_proposals"] > 5:
            health_score -= (summary["pending_proposals"] - 5) * 2
        
        return {
            "health_score": max(0, min(100, health_score)),
            "precision": summary["overall_precision"],
            "patterns_tracked": summary["patterns_tracked"],
            "pending_proposals": summary["pending_proposals"],
            "status": summary["health_status"],
        }
    
    def save_state(self):
        """Persist current state to database."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now(timezone.utc).isoformat()
            
            for pattern_id, fb in self.pattern_feedback.items():
                conn.execute('''
                    INSERT OR REPLACE INTO pattern_feedback
                    (pattern_id, pattern_text, severity, category, 
                     true_positives, false_positives, true_negatives, false_negatives, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_id, fb.pattern_text, fb.severity.value, fb.category.value,
                    fb.true_positives, fb.false_positives, fb.true_negatives, fb.false_negatives, now
                ))
            
            for proposal in self.pending_proposals:
                conn.execute('''
                    INSERT INTO proposals
                    (action, pattern_id, current_pattern, proposed_pattern, severity, category, 
                     reason, confidence, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                ''', (
                    proposal.action, proposal.pattern_id, proposal.current_pattern,
                    proposal.proposed_pattern, proposal.severity.value, proposal.category.value,
                    proposal.reason, proposal.confidence, now
                ))
            
            conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_halo_feedback: Optional[HALOFeedbackLoop] = None


def get_halo_feedback() -> HALOFeedbackLoop:
    """Get or create the global HALO feedback loop."""
    global _halo_feedback
    if _halo_feedback is None:
        _halo_feedback = HALOFeedbackLoop()
    return _halo_feedback


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "HALOFeedbackLoop",
    "PatternFeedback",
    "SeverityAdjustment",
    "PatternProposal",
    "get_halo_feedback",
]
