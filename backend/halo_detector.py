#!/usr/bin/env python3
"""
HALO Detector — Backend Detection (Layers 1+2)
===============================================
Hate, Abuse, Language, Outcomes

Deeper analysis than frontend, with:
- Extended blocklists
- Regex pattern matching
- Context analysis
- LLM classification hooks
- Database logging

Version: 1.0.0
Date: February 10, 2026
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# ═══════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════

class HALOCategory(Enum):
    HATE = "H"
    ABUSE = "A"
    LANGUAGE = "L"
    OUTCOMES = "O"


class SeverityTier(Enum):
    T1 = "T1"  # Discourage (warning)
    T2 = "T2"  # Caution (cooldown)
    T3 = "T3"  # Suspend (immediate block)


@dataclass
class HALOViolation:
    tier: SeverityTier
    category: HALOCategory
    matches: List[str] = field(default_factory=list)
    reason: str = ""
    message: str = ""
    confidence: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HALOResult:
    passed: bool
    tier: Optional[SeverityTier] = None
    category: Optional[HALOCategory] = None
    action: str = "ALLOW"
    message: str = ""
    violations: List[HALOViolation] = field(default_factory=list)
    content_hash: str = ""
    analysis_time_ms: float = 0.0


# ═══════════════════════════════════════════════════════════════
# BLOCKLISTS (Layer 1 — Pattern Matching)
# ═══════════════════════════════════════════════════════════════

# Severe (T3) — Immediate suspension
BLOCKLIST_SEVERE: List[Tuple[re.Pattern, str]] = [
    # Racial slurs
    (re.compile(r'\bn[i1!]gg[e3]r', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bk[i1!]ke\b', re.IGNORECASE), "antisemitic_slur"),
    (re.compile(r'\bsp[i1!]c\b', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bch[i1!]nk\b', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bw[e3]tb[a4@]ck', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bg[o0][o0]k\b', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bcoon\b', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bjigaboo', re.IGNORECASE), "racial_slur"),
    (re.compile(r'\bporch\s*monkey', re.IGNORECASE), "racial_slur"),
    
    # Extreme hate speech
    (re.compile(r'h[i1!]tl[e3]r\s*(was|did)\s*(right|nothing\s*wrong)', re.IGNORECASE), "nazi_apologia"),
    (re.compile(r'\b(kill|murder|exterminate|genocide)\s*(all|every|the)\s*(jews?|blacks?|muslims?|gays?|whites?|asians?)', re.IGNORECASE), "genocide_advocacy"),
    (re.compile(r'gas\s*the\s*(jews?|kikes?)', re.IGNORECASE), "genocide_advocacy"),
    (re.compile(r'white\s*(power|supremacy|genocide)', re.IGNORECASE), "white_supremacy"),
    (re.compile(r'\b(race|holy|race)\s*war\b', re.IGNORECASE), "extremism"),
    (re.compile(r'\b(1488|14\s*words|heil\s*hitler)\b', re.IGNORECASE), "nazi_symbols"),
    
    # Direct threats
    (re.compile(r"i('ll|m\s*going\s*to|will)\s*(kill|murder|shoot|stab|rape)\s*(you|them|her|him)", re.IGNORECASE), "direct_threat"),
    (re.compile(r"you('re|\s*are)\s*(going\s*to\s*)?(die|dead|get\s*(killed|shot))", re.IGNORECASE), "death_threat"),
    (re.compile(r'\b(bomb|shoot\s*up|attack)\s*(the|this|a)\s*(school|office|building|church|mosque|synagogue)', re.IGNORECASE), "mass_violence_threat"),
    (re.compile(r'i\s*(have|got)\s*a\s*(gun|bomb|knife)\s*(for|to)', re.IGNORECASE), "weapon_threat"),
    
    # CSAM indicators
    (re.compile(r'\b(child|kid|minor|underage)\s*(porn|sex|nude)', re.IGNORECASE), "csam_indicator"),
    (re.compile(r'\bpedo(phile)?', re.IGNORECASE), "csam_indicator"),
]

# Moderate (T2) — Caution
BLOCKLIST_MODERATE: List[Tuple[re.Pattern, str]] = [
    # Self-harm encouragement
    (re.compile(r'kill\s*yourself', re.IGNORECASE), "self_harm_encouragement"),
    (re.compile(r'\bkys\b', re.IGNORECASE), "self_harm_encouragement"),
    (re.compile(r'go\s*(and\s*)?(die|hang\s*yourself)', re.IGNORECASE), "self_harm_encouragement"),
    (re.compile(r'the\s*world\s*(would\s*be|is)\s*better\s*without\s*you', re.IGNORECASE), "self_harm_encouragement"),
    
    # Severe harassment
    (re.compile(r"you('re|\s*are)\s*(worthless|garbage|trash|pathetic|disgusting|subhuman)", re.IGNORECASE), "severe_harassment"),
    (re.compile(r'nobody\s*(loves|cares\s*(about)?|wants)\s*you', re.IGNORECASE), "severe_harassment"),
    (re.compile(r"i\s*(hope|wish)\s*(you|your\s*(family|mother|father))\s*(dies?|gets?\s*(cancer|sick))", re.IGNORECASE), "harassment"),
    
    # Gendered slurs
    (re.compile(r'\bc[u*]+nt', re.IGNORECASE), "gendered_slur"),
    (re.compile(r'\bwh[o0*]re', re.IGNORECASE), "gendered_slur"),
    (re.compile(r'\bsl[u*]+t', re.IGNORECASE), "gendered_slur"),
    
    # Homophobic/Transphobic slurs
    (re.compile(r'\bf[a4@]+gg?[o0]+t', re.IGNORECASE), "homophobic_slur"),
    (re.compile(r'\bdyke\b', re.IGNORECASE), "homophobic_slur"),
    (re.compile(r'\btr[a4@]+nn(y|ie)', re.IGNORECASE), "transphobic_slur"),
    (re.compile(r'\bshemale', re.IGNORECASE), "transphobic_slur"),
    
    # Ableist slurs
    (re.compile(r'\br[e3]+t[a4@]+rd', re.IGNORECASE), "ableist_slur"),
    (re.compile(r'\bspaz\b', re.IGNORECASE), "ableist_slur"),
    
    # Doxxing
    (re.compile(r"(here'?s?|posting|sharing)\s*(your|their|his|her)\s*(address|phone|email|location)", re.IGNORECASE), "doxxing"),
    (re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', re.IGNORECASE), "phone_number"),  # US phone
    
    # Stalking language
    (re.compile(r'i\s*(know|found)\s*where\s*you\s*(live|work|go)', re.IGNORECASE), "stalking"),
    (re.compile(r"i('m|am)\s*(watching|following|tracking)\s*you", re.IGNORECASE), "stalking"),
]

# Mild (T1) — Warning
BLOCKLIST_MILD: List[Tuple[re.Pattern, str]] = [
    # Profanity
    (re.compile(r'\bf+u+c+k+', re.IGNORECASE), "profanity"),
    (re.compile(r'\bs+h+[i1!]+t+', re.IGNORECASE), "profanity"),
    (re.compile(r'\ba+s+s+h+o+l+e+', re.IGNORECASE), "profanity"),
    (re.compile(r'\bb[i1!]+t+c+h+', re.IGNORECASE), "profanity"),
    (re.compile(r'\bd+a+m+n+\b', re.IGNORECASE), "profanity"),
    (re.compile(r'\bcrap\b', re.IGNORECASE), "profanity"),
    (re.compile(r'\bpiss', re.IGNORECASE), "profanity"),
    
    # Crude sexual references
    (re.compile(r'\bcock\b', re.IGNORECASE), "crude_sexual"),
    (re.compile(r'\bdick\b', re.IGNORECASE), "crude_sexual"),
    (re.compile(r'\bboobs?\b', re.IGNORECASE), "crude_sexual"),
    (re.compile(r'\btits?\b', re.IGNORECASE), "crude_sexual"),
    (re.compile(r'\bass\b', re.IGNORECASE), "crude_sexual"),
    
    # Mild insults
    (re.compile(r'\bidiot\b', re.IGNORECASE), "insult"),
    (re.compile(r'\bstupid\b', re.IGNORECASE), "insult"),
    (re.compile(r'\bmoron\b', re.IGNORECASE), "insult"),
    (re.compile(r'\bdumb(ass)?\b', re.IGNORECASE), "insult"),
]

# ═══════════════════════════════════════════════════════════════
# REGEX PATTERNS (Layer 2 — Contextual)
# ═══════════════════════════════════════════════════════════════

CONTEXTUAL_PATTERNS: List[Tuple[re.Pattern, SeverityTier, HALOCategory, str]] = [
    # Targeting patterns (group + negative action)
    (re.compile(r'(all|every|those)\s+(jews?|blacks?|muslims?|gays?|women|men|trans)\s+(should|must|need\s*to)\s+(die|be\s*killed|be\s*removed)', re.IGNORECASE),
     SeverityTier.T3, HALOCategory.HATE, "group_targeting"),
    
    # Dehumanization
    (re.compile(r'(jews?|blacks?|muslims?|gays?|women|immigrants?)\s+(are|is)\s+(animals?|vermin|parasites?|subhuman|disease)', re.IGNORECASE),
     SeverityTier.T3, HALOCategory.HATE, "dehumanization"),
    
    # Conspiracy theories (harmful)
    (re.compile(r'jews?\s+(control|run|own)\s+(the\s+)?(world|banks?|media|government)', re.IGNORECASE),
     SeverityTier.T2, HALOCategory.HATE, "antisemitic_conspiracy"),
    
    # Sexual harassment
    (re.compile(r'(send|show)\s*(me|us)\s*(your)?\s*(nudes?|pics?|body)', re.IGNORECASE),
     SeverityTier.T2, HALOCategory.ABUSE, "sexual_harassment"),
    
    # Blackmail
    (re.compile(r"(i('ll|will)|or\s+i('ll|will))\s+(expose|share|post|send)\s+(your|the)\s+(nudes?|photos?|pics?)", re.IGNORECASE),
     SeverityTier.T3, HALOCategory.ABUSE, "blackmail"),
]

# ═══════════════════════════════════════════════════════════════
# OUTCOMES DETECTION
# ═══════════════════════════════════════════════════════════════

GAMING_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r'(.)\1{15,}'), "character_spam"),  # Same char 15+ times
    (re.compile(r'^[a-z]{200,}$', re.IGNORECASE), "no_spaces_spam"),
    (re.compile(r'^(.{1,10})\1{10,}$'), "repeated_pattern"),
    (re.compile(r'test\s*test\s*test\s*test', re.IGNORECASE), "test_content"),
    (re.compile(r'asdf|qwerty|zxcv|lorem\s*ipsum', re.IGNORECASE), "placeholder_content"),
    (re.compile(r'^[\s\n\r]+$'), "whitespace_only"),
]


# ═══════════════════════════════════════════════════════════════
# DETECTOR CLASS
# ═══════════════════════════════════════════════════════════════

class HALODetector:
    """Main HALO detection engine."""
    
    def __init__(self, db_connection=None, llm_client=None):
        self.db = db_connection
        self.llm = llm_client
        self._content_hashes: Set[str] = set()
        self._submission_times: List[float] = []
        
        # Rate limiting config
        self.max_submissions_per_hour = 10
        self.min_content_length = 10
        self.max_content_length = 10000
    
    def _hash_content(self, text: str) -> str:
        """Generate hash for duplicate detection."""
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _check_blocklists(self, text: str) -> List[HALOViolation]:
        """Check text against all blocklists."""
        violations = []
        
        # Severe (T3)
        for pattern, reason in BLOCKLIST_SEVERE:
            matches = pattern.findall(text)
            if matches:
                violations.append(HALOViolation(
                    tier=SeverityTier.T3,
                    category=HALOCategory.HATE,
                    matches=list(set(matches)),
                    reason=reason,
                    message="Content violates community guidelines.",
                    confidence=1.0
                ))
        
        # Moderate (T2)
        for pattern, reason in BLOCKLIST_MODERATE:
            matches = pattern.findall(text)
            if matches:
                violations.append(HALOViolation(
                    tier=SeverityTier.T2,
                    category=HALOCategory.ABUSE,
                    matches=list(set(matches)),
                    reason=reason,
                    message="This content may be harmful.",
                    confidence=0.95
                ))
        
        # Mild (T1)
        for pattern, reason in BLOCKLIST_MILD:
            matches = pattern.findall(text)
            if matches:
                violations.append(HALOViolation(
                    tier=SeverityTier.T1,
                    category=HALOCategory.LANGUAGE,
                    matches=list(set(matches)),
                    reason=reason,
                    message="Content contains strong language.",
                    confidence=0.9
                ))
        
        return violations
    
    def _check_contextual(self, text: str) -> List[HALOViolation]:
        """Check contextual patterns."""
        violations = []
        
        for pattern, tier, category, reason in CONTEXTUAL_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                violations.append(HALOViolation(
                    tier=tier,
                    category=category,
                    matches=[str(m) for m in matches] if isinstance(matches[0], tuple) else matches,
                    reason=reason,
                    message="Content contains harmful patterns.",
                    confidence=0.85
                ))
        
        return violations
    
    def _check_outcomes(self, text: str, user_id: Optional[str] = None, 
                        session_id: Optional[str] = None) -> List[HALOViolation]:
        """Check for gaming, spam, and abuse patterns."""
        violations = []
        
        # Gaming patterns
        for pattern, reason in GAMING_PATTERNS:
            if pattern.search(text):
                violations.append(HALOViolation(
                    tier=SeverityTier.T1,
                    category=HALOCategory.OUTCOMES,
                    reason=reason,
                    message="Please provide genuine writing for analysis.",
                    confidence=0.9
                ))
        
        # Length checks
        if len(text.strip()) < self.min_content_length:
            violations.append(HALOViolation(
                tier=SeverityTier.T1,
                category=HALOCategory.OUTCOMES,
                reason="too_short",
                message="Content is too short for analysis.",
                confidence=1.0
            ))
        
        if len(text) > self.max_content_length:
            violations.append(HALOViolation(
                tier=SeverityTier.T1,
                category=HALOCategory.OUTCOMES,
                reason="too_long",
                message="Content exceeds maximum length.",
                confidence=1.0
            ))
        
        # Duplicate check
        content_hash = self._hash_content(text)
        if content_hash in self._content_hashes:
            violations.append(HALOViolation(
                tier=SeverityTier.T1,
                category=HALOCategory.OUTCOMES,
                reason="duplicate",
                message="This content has already been submitted.",
                confidence=1.0
            ))
        
        # Rate limiting
        now = time.time()
        hour_ago = now - 3600
        recent = [t for t in self._submission_times if t > hour_ago]
        
        if len(recent) >= self.max_submissions_per_hour:
            violations.append(HALOViolation(
                tier=SeverityTier.T2,
                category=HALOCategory.OUTCOMES,
                reason="rate_limit",
                message="Too many submissions. Please wait.",
                confidence=1.0
            ))
        
        return violations
    
    def analyze(self, text: str, user_id: Optional[str] = None,
                session_id: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None) -> HALOResult:
        """
        Analyze text for HALO violations.
        
        Args:
            text: Content to analyze
            user_id: Optional user identifier
            session_id: Optional session identifier
            context: Additional context (typing_duration, etc.)
        
        Returns:
            HALOResult with pass/fail and details
        """
        start_time = time.time()
        
        if not text or not isinstance(text, str):
            return HALOResult(
                passed=False,
                tier=SeverityTier.T1,
                category=HALOCategory.OUTCOMES,
                action="REJECT",
                message="Invalid input.",
                content_hash=""
            )
        
        content_hash = self._hash_content(text)
        all_violations: List[HALOViolation] = []
        
        # Layer 1: Blocklists
        all_violations.extend(self._check_blocklists(text))
        
        # Layer 2: Contextual patterns
        all_violations.extend(self._check_contextual(text))
        
        # Outcomes check
        all_violations.extend(self._check_outcomes(text, user_id, session_id))
        
        # Calculate analysis time
        analysis_time_ms = (time.time() - start_time) * 1000
        
        # Determine highest severity
        if not all_violations:
            return HALOResult(
                passed=True,
                action="ALLOW",
                content_hash=content_hash,
                analysis_time_ms=analysis_time_ms
            )
        
        # Find highest tier
        has_t3 = any(v.tier == SeverityTier.T3 for v in all_violations)
        has_t2 = any(v.tier == SeverityTier.T2 for v in all_violations)
        
        if has_t3:
            highest_tier = SeverityTier.T3
            action = "BLOCK"
            passed = False
        elif has_t2:
            highest_tier = SeverityTier.T2
            action = "CAUTION"
            passed = False
        else:
            highest_tier = SeverityTier.T1
            action = "WARN"
            passed = True  # T1 allows with warning
        
        # Get primary category
        primary_violation = next(v for v in all_violations if v.tier == highest_tier)
        
        return HALOResult(
            passed=passed,
            tier=highest_tier,
            category=primary_violation.category,
            action=action,
            message=primary_violation.message,
            violations=all_violations,
            content_hash=content_hash,
            analysis_time_ms=analysis_time_ms
        )
    
    def record_submission(self, text: str, user_id: Optional[str] = None):
        """Record successful submission for rate limiting."""
        self._content_hashes.add(self._hash_content(text))
        self._submission_times.append(time.time())
        
        # Cleanup old entries
        cutoff = time.time() - 3600
        self._submission_times = [t for t in self._submission_times if t > cutoff]
    
    def log_violation(self, result: HALOResult, user_id: Optional[str] = None,
                      session_id: Optional[str] = None, content_snippet: str = ""):
        """Log violation to database."""
        if not self.db or not result.violations:
            return
        
        # This would be implemented based on your database setup
        # Example structure:
        violation_record = {
            "user_id": user_id,
            "session_id": session_id,
            "tier": result.tier.value if result.tier else None,
            "category": result.category.value if result.category else None,
            "content_hash": result.content_hash,
            "content_snippet": content_snippet[:100],
            "violation_count": len(result.violations),
            "reasons": [v.reason for v in result.violations],
            "created_at": datetime.utcnow().isoformat()
        }
        
        # db.insert("halo_violations", violation_record)
        return violation_record
    
    def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's HALO status (for escalation logic)."""
        # This would query the database
        # Example return:
        return {
            "user_id": user_id,
            "t1_count_24h": 0,
            "t2_count_7d": 0,
            "is_suspended": False,
            "cooldown_until": None
        }
    
    def check_escalation(self, user_id: str, new_tier: SeverityTier) -> SeverityTier:
        """Check if violation should be escalated based on history."""
        status = self.get_user_status(user_id)
        
        # Escalation rules
        if new_tier == SeverityTier.T1:
            if status["t1_count_24h"] >= 2:
                return SeverityTier.T2  # Escalate
        
        if new_tier == SeverityTier.T2:
            if status["t2_count_7d"] >= 1:
                return SeverityTier.T3  # Escalate
        
        return new_tier


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

_default_detector: Optional[HALODetector] = None

def get_detector() -> HALODetector:
    """Get or create default detector instance."""
    global _default_detector
    if _default_detector is None:
        _default_detector = HALODetector()
    return _default_detector


def analyze(text: str, **kwargs) -> HALOResult:
    """Convenience function for quick analysis."""
    return get_detector().analyze(text, **kwargs)


def is_safe(text: str) -> bool:
    """Quick check if content is safe."""
    result = analyze(text)
    return result.passed


# ═══════════════════════════════════════════════════════════════
# CLI FOR TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    detector = HALODetector()
    
    test_cases = [
        "This is a normal, friendly message about writing.",
        "I think your idea is really stupid.",
        "You should go kill yourself.",
        "I will find where you live.",
        "asdfasdfasdfasdfasdfasdf",
        "test test test test",
    ]
    
    print("HALO Detector Test Suite")
    print("=" * 60)
    
    for text in test_cases:
        result = detector.analyze(text)
        status = "✅ PASS" if result.passed else f"❌ {result.action}"
        tier = result.tier.value if result.tier else "—"
        cat = result.category.value if result.category else "—"
        
        print(f"\n{status} [{tier}/{cat}]")
        print(f"  Text: {text[:50]}...")
        if result.violations:
            for v in result.violations[:2]:
                print(f"  → {v.tier.value}: {v.reason}")
        print(f"  Time: {result.analysis_time_ms:.2f}ms")
