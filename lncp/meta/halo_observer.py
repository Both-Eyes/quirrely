#!/usr/bin/env python3
"""
LNCP META: HALO OBSERVER v1.0.0
Safety as a first-class citizen of the Meta layer.

This module:
1. Collects all HALO safety events
2. Aggregates safety signals (violation rates, categories, trends)
3. Tracks per-user safety scores
4. Feeds into Command Center as SAFETY domain
5. Provides health inputs for system health calculation

Part of the virtuous cycle:
Safe Content → Better UX → Higher Trust → Better Retention → Higher MRR
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import defaultdict

# Import from existing modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lncp.meta.events.schema import EventType, AppEvent, UserTier


# ═══════════════════════════════════════════════════════════════════════════
# HALO CATEGORIES & TIERS (mirror backend/halo_detector.py)
# ═══════════════════════════════════════════════════════════════════════════

class HALOCategory(str, Enum):
    """HALO violation categories."""
    HATE = "H"       # Hate speech, slurs, discrimination
    ABUSE = "A"      # Harassment, threats, doxxing
    LANGUAGE = "L"   # Profanity, crude content
    OUTCOMES = "O"   # Gaming, spam, manipulation


class SeverityTier(str, Enum):
    """HALO severity tiers."""
    T1 = "T1"  # Warning - content allowed with notice
    T2 = "T2"  # Caution - cooldown applied
    T3 = "T3"  # Block - immediate rejection


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SafetySignals:
    """Aggregated safety signals over a time period."""
    
    # Volume
    total_checks: int = 0
    total_passed: int = 0
    total_violations: int = 0
    
    # By tier
    violations_t1: int = 0  # Warnings
    violations_t2: int = 0  # Cautions
    violations_t3: int = 0  # Blocks
    
    # By category
    violations_hate: int = 0
    violations_abuse: int = 0
    violations_language: int = 0
    violations_outcomes: int = 0
    
    # Appeals
    appeals_submitted: int = 0
    false_positives: int = 0
    
    # User actions
    users_warned: int = 0
    users_cooldown: int = 0
    users_suspended: int = 0
    
    # Computed metrics
    @property
    def pass_rate(self) -> float:
        """Percentage of checks that passed."""
        if self.total_checks == 0:
            return 1.0
        return self.total_passed / self.total_checks
    
    @property
    def violation_rate(self) -> float:
        """Percentage of checks with violations."""
        if self.total_checks == 0:
            return 0.0
        return self.total_violations / self.total_checks
    
    @property
    def severe_violation_rate(self) -> float:
        """Percentage of checks with T2/T3 violations."""
        if self.total_checks == 0:
            return 0.0
        return (self.violations_t2 + self.violations_t3) / self.total_checks
    
    @property
    def false_positive_rate(self) -> float:
        """Percentage of violations that were false positives."""
        if self.total_violations == 0:
            return 0.0
        return self.false_positives / self.total_violations
    
    @property
    def appeal_rate(self) -> float:
        """Percentage of violations that were appealed."""
        if self.total_violations == 0:
            return 0.0
        return self.appeals_submitted / self.total_violations
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_checks": self.total_checks,
            "total_passed": self.total_passed,
            "total_violations": self.total_violations,
            "violations_t1": self.violations_t1,
            "violations_t2": self.violations_t2,
            "violations_t3": self.violations_t3,
            "violations_hate": self.violations_hate,
            "violations_abuse": self.violations_abuse,
            "violations_language": self.violations_language,
            "violations_outcomes": self.violations_outcomes,
            "appeals_submitted": self.appeals_submitted,
            "false_positives": self.false_positives,
            "users_warned": self.users_warned,
            "users_cooldown": self.users_cooldown,
            "users_suspended": self.users_suspended,
            "pass_rate": self.pass_rate,
            "violation_rate": self.violation_rate,
            "severe_violation_rate": self.severe_violation_rate,
            "false_positive_rate": self.false_positive_rate,
            "appeal_rate": self.appeal_rate,
        }


@dataclass
class UserSafetyScore:
    """Per-user safety score."""
    user_id: str
    
    # Lifetime counts
    total_checks: int = 0
    total_violations: int = 0
    violations_t1: int = 0
    violations_t2: int = 0
    violations_t3: int = 0
    
    # Recent (30 days)
    recent_violations: int = 0
    recent_severe: int = 0
    
    # Status
    is_warned: bool = False
    is_cooldown: bool = False
    is_suspended: bool = False
    cooldown_until: Optional[datetime] = None
    
    # Appeals
    appeals_submitted: int = 0
    appeals_won: int = 0
    
    @property
    def safety_score(self) -> float:
        """
        Safety score from 0-100.
        100 = perfect safety record
        Decreases with violations, increases over time
        """
        if self.total_checks == 0:
            return 100.0  # New user, benefit of doubt
        
        # Base: pass rate
        base = (self.total_checks - self.total_violations) / self.total_checks * 100
        
        # Penalties for severe violations
        penalty = (self.violations_t2 * 5) + (self.violations_t3 * 15)
        
        # Bonus for successful appeals (they weren't actually bad)
        bonus = self.appeals_won * 2
        
        return max(0, min(100, base - penalty + bonus))
    
    @property
    def trust_level(self) -> str:
        """Categorical trust level."""
        score = self.safety_score
        if score >= 95:
            return "trusted"
        elif score >= 80:
            return "normal"
        elif score >= 60:
            return "monitored"
        elif score >= 40:
            return "restricted"
        else:
            return "untrusted"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "safety_score": self.safety_score,
            "trust_level": self.trust_level,
            "total_checks": self.total_checks,
            "total_violations": self.total_violations,
            "recent_violations": self.recent_violations,
            "is_suspended": self.is_suspended,
            "appeals_won": self.appeals_won,
        }


@dataclass
class PatternPerformance:
    """Track how well each HALO pattern is performing."""
    pattern_id: str
    pattern_type: str  # e.g., "blocklist_severe", "contextual"
    
    triggers: int = 0
    false_positives: int = 0
    confirmed_violations: int = 0
    
    @property
    def precision(self) -> float:
        """How often triggers are actual violations."""
        if self.triggers == 0:
            return 1.0
        return self.confirmed_violations / self.triggers
    
    @property
    def needs_review(self) -> bool:
        """Does this pattern need human review?"""
        # High false positive rate
        if self.triggers >= 10 and self.precision < 0.8:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
# HALO SIGNAL AGGREGATOR
# ═══════════════════════════════════════════════════════════════════════════

class HALOSignalAggregator:
    """Aggregates HALO events into safety signals."""
    
    def __init__(self):
        self.events: List[AppEvent] = []
        self._signals_cache: Optional[SafetySignals] = None
        self._cache_time: Optional[datetime] = None
    
    def add_event(self, event: AppEvent):
        """Add a single event."""
        self.events.append(event)
        self._signals_cache = None  # Invalidate cache
    
    def add_all(self, events: List[AppEvent]):
        """Add multiple events."""
        # Filter to safety events only
        safety_events = [
            e for e in events 
            if e.event_type.value.startswith("safety.")
        ]
        self.events.extend(safety_events)
        self._signals_cache = None
    
    def get_signals(self, hours: int = 24) -> SafetySignals:
        """Get aggregated safety signals for time period."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        signals = SafetySignals()
        
        for event in self.events:
            # Handle timezone-aware comparison
            event_time = event.timestamp
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)
            
            if event_time < cutoff:
                continue
            
            # Count by event type
            if event.event_type == EventType.HALO_CHECK_STARTED:
                signals.total_checks += 1
            
            elif event.event_type == EventType.HALO_CHECK_PASSED:
                signals.total_passed += 1
            
            elif event.event_type == EventType.HALO_VIOLATION_T1:
                signals.total_violations += 1
                signals.violations_t1 += 1
                self._count_category(event, signals)
            
            elif event.event_type == EventType.HALO_VIOLATION_T2:
                signals.total_violations += 1
                signals.violations_t2 += 1
                self._count_category(event, signals)
            
            elif event.event_type == EventType.HALO_VIOLATION_T3:
                signals.total_violations += 1
                signals.violations_t3 += 1
                self._count_category(event, signals)
            
            elif event.event_type == EventType.HALO_APPEAL_SUBMITTED:
                signals.appeals_submitted += 1
            
            elif event.event_type == EventType.HALO_FALSE_POSITIVE:
                signals.false_positives += 1
            
            elif event.event_type == EventType.HALO_USER_WARNED:
                signals.users_warned += 1
            
            elif event.event_type == EventType.HALO_USER_COOLDOWN:
                signals.users_cooldown += 1
            
            elif event.event_type == EventType.HALO_USER_SUSPENDED:
                signals.users_suspended += 1
        
        return signals
    
    def _count_category(self, event: AppEvent, signals: SafetySignals):
        """Count violation by category from event payload."""
        category = event.payload.get("category", "")
        if category == "H":
            signals.violations_hate += 1
        elif category == "A":
            signals.violations_abuse += 1
        elif category == "L":
            signals.violations_language += 1
        elif category == "O":
            signals.violations_outcomes += 1


# ═══════════════════════════════════════════════════════════════════════════
# HALO OBSERVER (Main Interface)
# ═══════════════════════════════════════════════════════════════════════════

class HALOObserver:
    """
    Observes HALO safety events and provides signals to Meta layer.
    
    This is the bridge between HALO (content safety) and Meta (optimization).
    It enables the virtuous cycle where safety improvements feed into
    UX, Health, and MRR improvements.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "data/halo_meta.db"
        self.aggregator = HALOSignalAggregator()
        self.user_scores: Dict[str, UserSafetyScore] = {}
        self.pattern_performance: Dict[str, PatternPerformance] = {}
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence."""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # User safety scores
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_safety_scores (
                    user_id TEXT PRIMARY KEY,
                    total_checks INTEGER DEFAULT 0,
                    total_violations INTEGER DEFAULT 0,
                    violations_t1 INTEGER DEFAULT 0,
                    violations_t2 INTEGER DEFAULT 0,
                    violations_t3 INTEGER DEFAULT 0,
                    recent_violations INTEGER DEFAULT 0,
                    is_warned INTEGER DEFAULT 0,
                    is_cooldown INTEGER DEFAULT 0,
                    is_suspended INTEGER DEFAULT 0,
                    cooldown_until TEXT,
                    appeals_submitted INTEGER DEFAULT 0,
                    appeals_won INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            ''')
            
            # Pattern performance
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pattern_performance (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    triggers INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    confirmed_violations INTEGER DEFAULT 0,
                    updated_at TEXT
                )
            ''')
            
            # Signal history (for trends)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS signal_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_checks INTEGER,
                    total_violations INTEGER,
                    pass_rate REAL,
                    violation_rate REAL,
                    false_positive_rate REAL
                )
            ''')
            
            conn.commit()
    
    def process_events(self, events: List[AppEvent]):
        """Process a batch of events and update state."""
        self.aggregator.add_all(events)
        
        # Update per-user scores
        for event in events:
            if not event.event_type.value.startswith("safety."):
                continue
            
            user_id = event.user_id
            if not user_id:
                continue
            
            if user_id not in self.user_scores:
                self.user_scores[user_id] = UserSafetyScore(user_id=user_id)
            
            score = self.user_scores[user_id]
            
            if event.event_type == EventType.HALO_CHECK_STARTED:
                score.total_checks += 1
            
            elif event.event_type in [
                EventType.HALO_VIOLATION_T1,
                EventType.HALO_VIOLATION_T2,
                EventType.HALO_VIOLATION_T3
            ]:
                score.total_violations += 1
                score.recent_violations += 1
                
                if event.event_type == EventType.HALO_VIOLATION_T1:
                    score.violations_t1 += 1
                elif event.event_type == EventType.HALO_VIOLATION_T2:
                    score.violations_t2 += 1
                elif event.event_type == EventType.HALO_VIOLATION_T3:
                    score.violations_t3 += 1
                    score.recent_severe += 1
            
            elif event.event_type == EventType.HALO_USER_WARNED:
                score.is_warned = True
            
            elif event.event_type == EventType.HALO_USER_COOLDOWN:
                score.is_cooldown = True
                cooldown_mins = event.payload.get("cooldown_minutes", 60)
                score.cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=cooldown_mins)
            
            elif event.event_type == EventType.HALO_USER_SUSPENDED:
                score.is_suspended = True
            
            elif event.event_type == EventType.HALO_APPEAL_SUBMITTED:
                score.appeals_submitted += 1
            
            elif event.event_type == EventType.HALO_FALSE_POSITIVE:
                score.appeals_won += 1
                # Restore some trust
                if score.total_violations > 0:
                    score.total_violations -= 1
            
            # Track pattern performance
            if event.event_type == EventType.HALO_PATTERN_TRIGGERED:
                pattern_id = event.payload.get("pattern_id", "unknown")
                if pattern_id not in self.pattern_performance:
                    self.pattern_performance[pattern_id] = PatternPerformance(
                        pattern_id=pattern_id,
                        pattern_type=event.payload.get("pattern_type", "unknown")
                    )
                self.pattern_performance[pattern_id].triggers += 1
    
    def get_current_signals(self, hours: int = 24) -> SafetySignals:
        """Get current aggregated safety signals."""
        return self.aggregator.get_signals(hours)
    
    def get_user_score(self, user_id: str) -> UserSafetyScore:
        """Get safety score for a user."""
        if user_id in self.user_scores:
            return self.user_scores[user_id]
        return UserSafetyScore(user_id=user_id)
    
    def get_health_inputs(self) -> Dict[str, Any]:
        """
        Get safety health inputs for the Meta orchestrator.
        
        Returns metrics that feed into:
        1. System health calculation
        2. Command Center SAFETY domain
        3. Proposal generation
        """
        signals = self.get_current_signals(hours=24)
        
        # Calculate safety health score (0-100)
        # High pass rate + low severe violations + low false positives = good
        health_score = 100.0
        
        # Penalize low pass rate
        if signals.pass_rate < 0.99:
            health_score -= (0.99 - signals.pass_rate) * 100
        
        # Penalize severe violations
        if signals.severe_violation_rate > 0.001:
            health_score -= signals.severe_violation_rate * 1000
        
        # Penalize high false positive rate (bad for UX)
        if signals.false_positive_rate > 0.05:
            health_score -= (signals.false_positive_rate - 0.05) * 200
        
        health_score = max(0, min(100, health_score))
        
        return {
            "health_score": health_score,
            "pass_rate": signals.pass_rate,
            "violation_rate": signals.violation_rate,
            "severe_violation_rate": signals.severe_violation_rate,
            "false_positive_rate": signals.false_positive_rate,
            "appeal_rate": signals.appeal_rate,
            "total_checks_24h": signals.total_checks,
            "total_violations_24h": signals.total_violations,
            "users_suspended_24h": signals.users_suspended,
            "patterns_needing_review": len([
                p for p in self.pattern_performance.values() 
                if p.needs_review
            ]),
        }
    
    def get_command_center_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for Command Center SAFETY domain.
        
        Returns 4 key metrics like other domains:
        1. Safety Score (overall)
        2. Violation Rate
        3. False Positive Rate
        4. User Trust
        """
        signals = self.get_current_signals(hours=24)
        health = self.get_health_inputs()
        
        # Calculate average user trust
        if self.user_scores:
            avg_trust = sum(s.safety_score for s in self.user_scores.values()) / len(self.user_scores)
        else:
            avg_trust = 100.0
        
        return {
            "metrics": [
                {
                    "id": "safety_score",
                    "name": "Safety Score",
                    "value": health["health_score"],
                    "unit": "%",
                    "trend": "stable",
                    "target": 98.0,
                },
                {
                    "id": "violation_rate",
                    "name": "Violation Rate",
                    "value": signals.violation_rate * 100,
                    "unit": "%",
                    "trend": "stable",
                    "target": 0.5,  # Target: <0.5% violations
                },
                {
                    "id": "false_positive_rate",
                    "name": "False Positive Rate",
                    "value": signals.false_positive_rate * 100,
                    "unit": "%",
                    "trend": "stable",
                    "target": 2.0,  # Target: <2% false positives
                },
                {
                    "id": "user_trust",
                    "name": "Avg User Trust",
                    "value": avg_trust,
                    "unit": "%",
                    "trend": "stable",
                    "target": 95.0,
                },
            ],
            "alerts": self._generate_alerts(signals, health),
            "summary": {
                "total_checks": signals.total_checks,
                "total_violations": signals.total_violations,
                "users_affected": signals.users_warned + signals.users_cooldown + signals.users_suspended,
            }
        }
    
    def _generate_alerts(self, signals: SafetySignals, health: Dict) -> List[Dict]:
        """Generate alerts based on safety signals."""
        alerts = []
        
        # High violation rate
        if signals.violation_rate > 0.01:
            alerts.append({
                "severity": "warning",
                "title": "Elevated Violation Rate",
                "message": f"{signals.violation_rate:.1%} of submissions flagged",
            })
        
        if signals.violation_rate > 0.05:
            alerts.append({
                "severity": "critical",
                "title": "High Violation Rate",
                "message": f"{signals.violation_rate:.1%} violations - possible attack",
            })
        
        # High false positive rate
        if signals.false_positive_rate > 0.1:
            alerts.append({
                "severity": "warning",
                "title": "High False Positive Rate",
                "message": f"{signals.false_positive_rate:.1%} of violations were overturned",
            })
        
        # Suspensions
        if signals.users_suspended > 0:
            alerts.append({
                "severity": "info",
                "title": "Users Suspended",
                "message": f"{signals.users_suspended} user(s) suspended in last 24h",
            })
        
        # Pattern review needed
        if health.get("patterns_needing_review", 0) > 0:
            alerts.append({
                "severity": "info",
                "title": "Patterns Need Review",
                "message": f"{health['patterns_needing_review']} pattern(s) may need adjustment",
            })
        
        return alerts
    
    def generate_proposals(self) -> List[Dict]:
        """
        Generate optimization proposals for HALO patterns.
        
        These feed into the Command Center proposal queue.
        """
        proposals = []
        signals = self.get_current_signals(hours=168)  # 7 days
        
        # Propose pattern adjustments based on false positives
        for pattern_id, perf in self.pattern_performance.items():
            if perf.needs_review:
                proposals.append({
                    "id": f"halo_pattern_{pattern_id}",
                    "domain": "SAFETY",
                    "title": f"Review pattern: {pattern_id}",
                    "description": f"Pattern has {perf.precision:.0%} precision ({perf.false_positives} false positives)",
                    "impact": {
                        "ux_percent": 5,  # Better UX from fewer false blocks
                        "health_percent": 2,
                        "mrr_dollars": 0,
                    },
                    "tier": "24hour",
                    "confidence": 0.7,
                    "evidence": f"{perf.triggers} triggers, {perf.false_positives} false positives",
                })
        
        # Propose severity adjustment if false positive rate is high
        if signals.false_positive_rate > 0.1:
            proposals.append({
                "id": "halo_reduce_sensitivity",
                "domain": "SAFETY",
                "title": "Reduce HALO sensitivity",
                "description": f"False positive rate is {signals.false_positive_rate:.1%} - consider relaxing T1 patterns",
                "impact": {
                    "ux_percent": 8,
                    "health_percent": -2,  # Slight risk
                    "mrr_dollars": 100,
                },
                "tier": "24hour",
                "confidence": 0.6,
                "evidence": f"{signals.false_positives} false positives in period",
            })
        
        # Propose stricter enforcement if severe violations are high
        if signals.severe_violation_rate > 0.005:
            proposals.append({
                "id": "halo_increase_enforcement",
                "domain": "SAFETY",
                "title": "Increase HALO enforcement",
                "description": f"Severe violation rate is {signals.severe_violation_rate:.2%} - consider stricter patterns",
                "impact": {
                    "ux_percent": -2,  # Some friction
                    "health_percent": 5,
                    "mrr_dollars": 0,
                },
                "tier": "30day",
                "confidence": 0.7,
                "evidence": f"{signals.violations_t2 + signals.violations_t3} severe violations",
            })
        
        return proposals
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete safety summary."""
        signals = self.get_current_signals(hours=24)
        health = self.get_health_inputs()
        
        return {
            "status": "operational",
            "health_score": health["health_score"],
            "signals": signals.to_dict(),
            "users_tracked": len(self.user_scores),
            "patterns_tracked": len(self.pattern_performance),
            "patterns_needing_review": health["patterns_needing_review"],
            "proposals": len(self.generate_proposals()),
        }
    
    def save_state(self):
        """Persist state to database."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now(timezone.utc).isoformat()
            
            for user_id, score in self.user_scores.items():
                conn.execute('''
                    INSERT OR REPLACE INTO user_safety_scores
                    (user_id, total_checks, total_violations, violations_t1, violations_t2, violations_t3,
                     recent_violations, is_warned, is_cooldown, is_suspended, cooldown_until,
                     appeals_submitted, appeals_won, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, score.total_checks, score.total_violations,
                    score.violations_t1, score.violations_t2, score.violations_t3,
                    score.recent_violations, int(score.is_warned), int(score.is_cooldown),
                    int(score.is_suspended), 
                    score.cooldown_until.isoformat() if score.cooldown_until else None,
                    score.appeals_submitted, score.appeals_won, now
                ))
            
            for pattern_id, perf in self.pattern_performance.items():
                conn.execute('''
                    INSERT OR REPLACE INTO pattern_performance
                    (pattern_id, pattern_type, triggers, false_positives, confirmed_violations, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_id, perf.pattern_type, perf.triggers,
                    perf.false_positives, perf.confirmed_violations, now
                ))
            
            conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON & CONVENIENCE
# ═══════════════════════════════════════════════════════════════════════════

_halo_observer: Optional[HALOObserver] = None


def get_halo_observer() -> HALOObserver:
    """Get or create the global HALO observer."""
    global _halo_observer
    if _halo_observer is None:
        _halo_observer = HALOObserver()
    return _halo_observer


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "HALOObserver",
    "HALOSignalAggregator",
    "SafetySignals",
    "UserSafetyScore",
    "PatternPerformance",
    "HALOCategory",
    "SeverityTier",
    "get_halo_observer",
]
