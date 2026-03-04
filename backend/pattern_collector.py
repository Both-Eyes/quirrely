#!/usr/bin/env python3
"""
LNCP Pattern Collector Service
Version: 1.0.0

Collects and stores token patterns from every analysis to enable the virtuous cycle.
This is the core of "LNCP GROWS" - every analysis contributes to system learning.

Usage:
    from pattern_collector import PatternCollector
    
    collector = PatternCollector()
    collector.record_analysis(
        tokens=[3, 1, 4, 1, 5, 9, 2, 6],
        profile="ASSERTIVE",
        stance="OPEN",
        word_count=45,
        sentence_count=3,
        user_id=None,  # or UUID
        session_id="abc123"
    )
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import threading


# ═══════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PatternObservation:
    """A single pattern observation from an analysis."""
    token_signature: str
    token_count: int
    profile: str
    stance: str
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source: str = "web"
    observed_at: str = None
    
    def __post_init__(self):
        if self.observed_at is None:
            self.observed_at = datetime.utcnow().isoformat() + "Z"


@dataclass
class PatternRecord:
    """Aggregated pattern data."""
    token_signature: str
    token_count: int
    profile_counts: Dict[str, int]
    stance_counts: Dict[str, int]
    total_observations: int
    avg_word_count: Optional[float] = None
    avg_sentence_count: Optional[float] = None
    first_seen_at: str = None
    last_seen_at: str = None
    
    def __post_init__(self):
        now = datetime.utcnow().isoformat() + "Z"
        if self.first_seen_at is None:
            self.first_seen_at = now
        if self.last_seen_at is None:
            self.last_seen_at = now
    
    @property
    def dominant_profile(self) -> str:
        """Get the most commonly associated profile."""
        if not self.profile_counts:
            return "UNKNOWN"
        return max(self.profile_counts, key=self.profile_counts.get)
    
    @property
    def dominant_stance(self) -> str:
        """Get the most commonly associated stance."""
        if not self.stance_counts:
            return "UNKNOWN"
        return max(self.stance_counts, key=self.stance_counts.get)
    
    @property
    def profile_confidence(self) -> float:
        """Confidence that dominant profile is correct (0-1)."""
        if not self.profile_counts or self.total_observations == 0:
            return 0.0
        dominant_count = self.profile_counts.get(self.dominant_profile, 0)
        return dominant_count / self.total_observations


@dataclass
class ProfileHistoryEntry:
    """A single entry in user's profile history."""
    id: str
    user_id: Optional[str]
    session_id: Optional[str]
    profile: str
    stance: str
    word_count: Optional[int]
    sentence_count: Optional[int]
    token_signature: str
    confidence_score: Optional[float]
    source: str
    input_preview: Optional[str]
    scores: Optional[Dict[str, Any]]
    analyzed_at: str


# ═══════════════════════════════════════════════════════════════════════════
# Pattern Collector
# ═══════════════════════════════════════════════════════════════════════════

class PatternCollector:
    """
    Collects and manages token patterns from analyses.
    
    Currently uses file-based storage. When deployed with Supabase,
    will use PostgreSQL via the provided functions.
    """
    
    SIGNATURE_LENGTH = 10  # First N tokens to use as signature
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the pattern collector.
        
        Args:
            storage_dir: Directory for file-based storage. Defaults to ./patterns/
        """
        self.storage_dir = storage_dir or Path(__file__).parent / "patterns"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.patterns_file = self.storage_dir / "patterns.json"
        self.history_file = self.storage_dir / "history.json"
        self.daily_file = self.storage_dir / "daily.json"
        
        self._lock = threading.Lock()
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure storage files exist."""
        if not self.patterns_file.exists():
            self._write_json(self.patterns_file, {"patterns": {}, "version": "1.0"})
        if not self.history_file.exists():
            self._write_json(self.history_file, {"history": [], "version": "1.0"})
        if not self.daily_file.exists():
            self._write_json(self.daily_file, {"daily": {}, "version": "1.0"})
    
    def _read_json(self, path: Path) -> Dict[str, Any]:
        """Read JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: Dict[str, Any]):
        """Write JSON file atomically."""
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            os.replace(tmp_path, str(path))
        except Exception:
            try: os.unlink(tmp_path)
            except OSError: pass
            raise

    def _locked_update(self, path: Path, updater):
        """Read-modify-write a JSON file with file locking."""
        import fcntl
        lock_path = str(path) + ".lock"
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                data = self._read_json(path)
                result = updater(data)
                self._write_json(path, data)
                return result
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    
    def _create_signature(self, tokens: List[int]) -> str:
        """
        Create a token signature from a list of tokens.
        
        Uses first N tokens joined by dashes.
        """
        sig_tokens = tokens[:self.SIGNATURE_LENGTH]
        return "-".join(str(t) for t in sig_tokens)
    
    def record_analysis(
        self,
        tokens: List[int],
        profile: str,
        stance: str,
        word_count: Optional[int] = None,
        sentence_count: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source: str = "web",
        input_preview: Optional[str] = None,
        scores: Optional[Dict[str, Any]] = None,
        confidence_score: Optional[float] = None,
    ) -> Tuple[str, str]:
        """
        Record an analysis, storing both pattern and history.
        
        Args:
            tokens: List of token values from LNCP
            profile: Classified profile (e.g., "ASSERTIVE")
            stance: Classified stance (e.g., "OPEN")
            word_count: Number of words analyzed
            sentence_count: Number of sentences analyzed
            user_id: User ID if authenticated
            session_id: Session ID for anonymous users
            source: Source of analysis (web, extension, api)
            input_preview: First ~100 chars of input
            scores: Full scores dict
            confidence_score: Confidence in classification
            
        Returns:
            Tuple of (pattern_id, history_id)
        """
        signature = self._create_signature(tokens)
        
        import fcntl
        lock_path = str(self.storage_dir / "collector.lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                # Record pattern
                pattern_id = self._record_pattern(
                    signature=signature,
                    token_count=len(tokens),
                    profile=profile,
                    stance=stance,
                    word_count=word_count,
                    sentence_count=sentence_count,
                )

                # Record history
                history_id = self._record_history(
                    signature=signature,
                    profile=profile,
                    stance=stance,
                    word_count=word_count,
                    sentence_count=sentence_count,
                    user_id=user_id,
                    session_id=session_id,
                    source=source,
                    input_preview=input_preview,
                    scores=scores,
                    confidence_score=confidence_score,
                )

                # Update daily stats
                self._update_daily_stats(profile, stance)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

        return pattern_id, history_id
    
    def _record_pattern(
        self,
        signature: str,
        token_count: int,
        profile: str,
        stance: str,
        word_count: Optional[int],
        sentence_count: Optional[int],
    ) -> str:
        """Record or update a pattern observation."""
        data = self._read_json(self.patterns_file)
        patterns = data.get("patterns", {})
        
        now = datetime.utcnow().isoformat() + "Z"
        
        if signature in patterns:
            # Update existing pattern
            p = patterns[signature]
            p["profile_counts"][profile] = p["profile_counts"].get(profile, 0) + 1
            p["stance_counts"][stance] = p["stance_counts"].get(stance, 0) + 1
            p["total_observations"] += 1
            p["last_seen_at"] = now
            
            # Update running averages
            n = p["total_observations"]
            if word_count is not None:
                old_avg = p.get("avg_word_count") or word_count
                p["avg_word_count"] = (old_avg * (n - 1) + word_count) / n
            if sentence_count is not None:
                old_avg = p.get("avg_sentence_count") or sentence_count
                p["avg_sentence_count"] = (old_avg * (n - 1) + sentence_count) / n
        else:
            # Create new pattern
            patterns[signature] = {
                "token_signature": signature,
                "token_count": token_count,
                "profile_counts": {profile: 1},
                "stance_counts": {stance: 1},
                "total_observations": 1,
                "avg_word_count": word_count,
                "avg_sentence_count": sentence_count,
                "first_seen_at": now,
                "last_seen_at": now,
            }
        
        data["patterns"] = patterns
        self._write_json(self.patterns_file, data)
        
        return signature
    
    def _record_history(
        self,
        signature: str,
        profile: str,
        stance: str,
        word_count: Optional[int],
        sentence_count: Optional[int],
        user_id: Optional[str],
        session_id: Optional[str],
        source: str,
        input_preview: Optional[str],
        scores: Optional[Dict[str, Any]],
        confidence_score: Optional[float],
    ) -> str:
        """Record a profile history entry."""
        data = self._read_json(self.history_file)
        history = data.get("history", [])
        
        # Generate ID
        history_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{signature}{user_id or session_id}".encode()
        ).hexdigest()[:16]
        
        entry = {
            "id": history_id,
            "user_id": user_id,
            "session_id": session_id,
            "profile": profile,
            "stance": stance,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "token_signature": signature,
            "confidence_score": confidence_score,
            "source": source,
            "input_preview": input_preview[:100] if input_preview else None,
            "scores": scores,
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
        }
        
        history.append(entry)
        
        # Keep last 10000 entries max (trim oldest)
        if len(history) > 10000:
            history = history[-10000:]
        
        data["history"] = history
        self._write_json(self.history_file, data)
        
        return history_id
    
    def _update_daily_stats(self, profile: str, stance: str):
        """Update daily statistics."""
        data = self._read_json(self.daily_file)
        daily = data.get("daily", {})
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if today not in daily:
            daily[today] = {
                "total_analyses": 0,
                "profile_distribution": {},
                "stance_distribution": {},
                "new_patterns": 0,
            }
        
        day = daily[today]
        day["total_analyses"] += 1
        day["profile_distribution"][profile] = day["profile_distribution"].get(profile, 0) + 1
        day["stance_distribution"][stance] = day["stance_distribution"].get(stance, 0) + 1
        
        data["daily"] = daily
        self._write_json(self.daily_file, data)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Query Methods
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_pattern(self, signature: str) -> Optional[PatternRecord]:
        """Get a pattern by signature."""
        data = self._read_json(self.patterns_file)
        p = data.get("patterns", {}).get(signature)
        if p:
            return PatternRecord(**p)
        return None
    
    def get_top_patterns(self, limit: int = 20) -> List[PatternRecord]:
        """Get most observed patterns."""
        data = self._read_json(self.patterns_file)
        patterns = list(data.get("patterns", {}).values())
        patterns.sort(key=lambda p: p["total_observations"], reverse=True)
        return [PatternRecord(**p) for p in patterns[:limit]]
    
    def get_patterns_for_profile(self, profile: str, limit: int = 10) -> List[PatternRecord]:
        """Get patterns most associated with a profile."""
        data = self._read_json(self.patterns_file)
        patterns = []
        
        for p in data.get("patterns", {}).values():
            if profile in p.get("profile_counts", {}):
                patterns.append(p)
        
        # Sort by count for this profile
        patterns.sort(
            key=lambda p: p["profile_counts"].get(profile, 0),
            reverse=True
        )
        
        return [PatternRecord(**p) for p in patterns[:limit]]
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[ProfileHistoryEntry]:
        """Get profile history for a user."""
        data = self._read_json(self.history_file)
        history = data.get("history", [])
        
        user_history = [h for h in history if h.get("user_id") == user_id]
        user_history.sort(key=lambda h: h.get("analyzed_at", ""), reverse=True)
        
        return [ProfileHistoryEntry(**h) for h in user_history[:limit]]
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[ProfileHistoryEntry]:
        """Get profile history for a session."""
        data = self._read_json(self.history_file)
        history = data.get("history", [])
        
        session_history = [h for h in history if h.get("session_id") == session_id]
        session_history.sort(key=lambda h: h.get("analyzed_at", ""), reverse=True)
        
        return [ProfileHistoryEntry(**h) for h in session_history[:limit]]
    
    def link_session_to_user(self, session_id: str, user_id: str) -> int:
        """
        Link a session to a user, migrating all history entries.
        
        Returns:
            Number of history entries migrated
        """
        import fcntl
        lock_path = str(self.storage_dir / "collector.lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                data = self._read_json(self.history_file)
                history = data.get("history", [])

                migrated = 0
                for entry in history:
                    if entry.get("session_id") == session_id and entry.get("user_id") is None:
                        entry["user_id"] = user_id
                        migrated += 1

                data["history"] = history
                self._write_json(self.history_file, data)

                return migrated
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    
    def get_profile_evolution(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get profile evolution data for a user.
        
        Returns summary of how their profiles have changed over time.
        """
        history = self.get_user_history(user_id, limit=100)
        
        if not history:
            return {"entries": 0, "profiles": {}, "stances": {}, "trend": None}
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [h for h in history if h.analyzed_at >= cutoff.isoformat()]
        
        # Count profiles and stances
        profile_counts = {}
        stance_counts = {}
        timeline = []
        
        for h in recent:
            profile_counts[h.profile] = profile_counts.get(h.profile, 0) + 1
            stance_counts[h.stance] = stance_counts.get(h.stance, 0) + 1
            timeline.append({
                "date": h.analyzed_at[:10],
                "profile": h.profile,
                "stance": h.stance,
            })
        
        # Determine trend
        trend = None
        if len(recent) >= 3:
            first_half = recent[len(recent)//2:]
            second_half = recent[:len(recent)//2]
            
            first_profile = max(set(h.profile for h in first_half), 
                               key=lambda p: sum(1 for h in first_half if h.profile == p))
            second_profile = max(set(h.profile for h in second_half),
                                key=lambda p: sum(1 for h in second_half if h.profile == p))
            
            if first_profile != second_profile:
                trend = f"Shifted from {first_profile} to {second_profile}"
            else:
                trend = f"Consistent {first_profile}"
        
        return {
            "entries": len(recent),
            "profiles": profile_counts,
            "stances": stance_counts,
            "timeline": timeline[:20],
            "trend": trend,
            "dominant_profile": max(profile_counts, key=profile_counts.get) if profile_counts else None,
            "dominant_stance": max(stance_counts, key=stance_counts.get) if stance_counts else None,
        }
    
    def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for the last N days."""
        data = self._read_json(self.daily_file)
        daily = data.get("daily", {})
        
        stats = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in daily:
                stats.append({"date": date, **daily[date]})
            else:
                stats.append({
                    "date": date,
                    "total_analyses": 0,
                    "profile_distribution": {},
                    "stance_distribution": {},
                })
        
        return stats
    
    def get_learning_candidates(self, min_observations: int = 50) -> List[Dict[str, Any]]:
        """
        Get patterns that might inform LNCP improvements.
        
        Returns patterns with high observation counts where the
        profile distribution might suggest threshold adjustments.
        """
        data = self._read_json(self.patterns_file)
        patterns = data.get("patterns", {})
        
        candidates = []
        for sig, p in patterns.items():
            if p["total_observations"] >= min_observations:
                # Calculate profile concentration
                counts = p["profile_counts"]
                total = sum(counts.values())
                max_count = max(counts.values()) if counts else 0
                concentration = max_count / total if total > 0 else 0
                
                # High concentration = clear signal
                # Low concentration = ambiguous pattern
                candidates.append({
                    "signature": sig,
                    "observations": p["total_observations"],
                    "dominant_profile": max(counts, key=counts.get) if counts else None,
                    "concentration": concentration,
                    "profile_counts": counts,
                    "recommendation": (
                        "Strong signal" if concentration > 0.8 else
                        "Moderate signal" if concentration > 0.6 else
                        "Ambiguous - needs review"
                    )
                })
        
        # Sort by observations
        candidates.sort(key=lambda c: c["observations"], reverse=True)
        return candidates[:20]


# ═══════════════════════════════════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════════════════════════════════

_collector: Optional[PatternCollector] = None


def get_pattern_collector() -> PatternCollector:
    """Get or create the global pattern collector instance."""
    global _collector
    if _collector is None:
        _collector = PatternCollector()
    return _collector


# ═══════════════════════════════════════════════════════════════════════════
# Demo / Test
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Pattern Collector Demo")
    print("=" * 60)
    
    collector = PatternCollector()
    
    # Simulate some analyses
    test_data = [
        ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], "ASSERTIVE", "OPEN", 45, 3),
        ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], "ASSERTIVE", "OPEN", 52, 4),
        ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], "MINIMAL", "CLOSED", 38, 2),
        ([2, 7, 1, 8, 2, 8, 1, 8, 2, 8], "POETIC", "OPEN", 120, 8),
        ([2, 7, 1, 8, 2, 8, 1, 8, 2, 8], "POETIC", "BALANCED", 95, 6),
        ([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], "MINIMAL", "CLOSED", 15, 5),
    ]
    
    print("\nRecording test analyses...")
    for tokens, profile, stance, wc, sc in test_data:
        pattern_id, history_id = collector.record_analysis(
            tokens=tokens,
            profile=profile,
            stance=stance,
            word_count=wc,
            sentence_count=sc,
            session_id="demo-session-123",
            source="demo",
        )
        print(f"  Recorded: {profile}/{stance} -> pattern {pattern_id[:20]}...")
    
    print("\n" + "=" * 60)
    print("Top Patterns:")
    print("=" * 60)
    for p in collector.get_top_patterns(5):
        print(f"  {p.token_signature}")
        print(f"    Observations: {p.total_observations}")
        print(f"    Dominant: {p.dominant_profile}/{p.dominant_stance}")
        print(f"    Confidence: {p.profile_confidence:.1%}")
        print()
    
    print("=" * 60)
    print("Daily Stats:")
    print("=" * 60)
    for day in collector.get_daily_stats(3):
        print(f"  {day['date']}: {day['total_analyses']} analyses")
    
    print("\n" + "=" * 60)
    print("Learning Candidates:")
    print("=" * 60)
    candidates = collector.get_learning_candidates(min_observations=2)
    for c in candidates[:3]:
        print(f"  {c['signature']}")
        print(f"    {c['observations']} obs, {c['recommendation']}")
    
    print("\n✅ Pattern Collector working")
