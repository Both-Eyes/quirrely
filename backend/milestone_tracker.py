#!/usr/bin/env python3
"""
QUIRRELY MILESTONE SYSTEM v1.0
Original Writing Recognition & Featured Writer Eligibility

Tracks:
- Keystroke word accumulation
- Streaks (3-day 500, 3/7/14/30-day 1K)
- Featured Writer eligibility and submissions

Aligned with Quirrely v2.1.0 "Quinquaginta"
"""

from __future__ import annotations

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & TYPES
# ═══════════════════════════════════════════════════════════════════════════

class MilestoneType(str, Enum):
    FIRST_500 = "first_500"
    STREAK_3_DAY = "streak_3_day"           # 500+/day, 3 consecutive
    DAILY_1K = "daily_1k"                    # 1000+ in single day (PRO)
    STREAK_3_DAY_1K = "streak_3_day_1k"     # 1000+/day, 3 consecutive (PRO)
    STREAK_7_DAY_1K = "streak_7_day_1k"     # 1000+/day, 7 consecutive (PRO) → Featured eligibility
    STREAK_14_DAY_1K = "streak_14_day_1k"   # 1000+/day, 14 consecutive (PRO)
    STREAK_30_DAY_1K = "streak_30_day_1k"   # 1000+/day, 30 consecutive (PRO)
    AUTHORITY_ELIGIBLE = "authority_eligible"  # All Authority requirements met
    AUTHORITY_WRITER = "authority_writer"      # Authority status granted


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Tier(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"


@dataclass
class Milestone:
    """A triggered milestone event."""
    type: MilestoneType
    triggered_at: datetime
    keystroke_words: int
    streak_days: Optional[int] = None


@dataclass
class FeaturedSubmission:
    """A Featured Writer submission."""
    id: str
    user_id: str
    submitted_at: datetime
    text: str
    word_count: int
    keystroke_verified: bool
    agreement_accepted_at: datetime
    status: SubmissionStatus
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


@dataclass
class UserMilestones:
    """Complete milestone state for a user."""
    user_id: str
    
    # Lifetime stats
    lifetime_keystroke_words: int = 0
    first_500_achieved: bool = False
    first_500_achieved_at: Optional[datetime] = None
    
    # 500/day streak (auth'd users)
    streak_500_current: int = 0
    streak_500_last_date: Optional[date] = None
    streak_500_3_count: int = 0  # Times achieved 3-day
    
    # 1K/day tracking (PRO only)
    daily_1k_count: int = 0  # Total days with 1K+
    
    # 1K/day streaks (PRO only)
    streak_1k_current: int = 0
    streak_1k_last_date: Optional[date] = None
    streak_1k_longest: int = 0
    streak_1k_3_count: int = 0
    streak_1k_7_count: int = 0
    streak_1k_14_count: int = 0
    streak_1k_30_count: int = 0
    streak_1k_30_first_at: Optional[datetime] = None
    
    # Featured Writer
    featured_eligible: bool = False
    featured_eligible_at: Optional[datetime] = None
    featured_writer: bool = False
    featured_writer_since: Optional[datetime] = None
    featured_piece_url: Optional[str] = None
    featured_pieces_count: int = 0  # Total accepted pieces
    
    # Authority Writer
    authority_eligible: bool = False
    authority_eligible_at: Optional[datetime] = None
    authority_writer: bool = False
    authority_writer_since: Optional[datetime] = None
    authority_last_active: Optional[datetime] = None  # For inactivity tracking


# ═══════════════════════════════════════════════════════════════════════════
# MILESTONE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

MILESTONE_META = {
    MilestoneType.FIRST_500: {
        "name": "First 500",
        "description": "Wrote 500 original words",
        "icon": "✍️",
        "animation": "acorn_collect",
        "color": "#FF6B6B",  # Coral
        "user_types": ["free", "trial", "pro"],
    },
    MilestoneType.STREAK_3_DAY: {
        "name": "3-Day Streak",
        "description": "500+ original words for 3 consecutive days",
        "icon": "🌰🌰🌰",
        "animation": "acorn_stack",
        "color": "#FF6B6B",  # Coral
        "user_types": ["free", "trial", "pro"],  # Auth'd only (handled in logic)
    },
    MilestoneType.DAILY_1K: {
        "name": "Daily 1K",
        "description": "1,000+ original words in a single day",
        "icon": "🔥",
        "animation": "glow_pulse",
        "color": "#D4A574",  # Soft Gold fade
        "user_types": ["pro"],
    },
    MilestoneType.STREAK_3_DAY_1K: {
        "name": "3-Day 1K Streak",
        "description": "1,000+ original words for 3 consecutive days",
        "icon": "👑",
        "animation": "golden_acorn_crown",
        "color": "#D4A574",  # Soft Gold
        "user_types": ["pro"],
    },
    MilestoneType.STREAK_7_DAY_1K: {
        "name": "7-Day 1K Streak",
        "description": "1,000+ original words for 7 consecutive days",
        "icon": "💫",
        "animation": "golden_acorn_ring",
        "color": "#D4A574",  # Soft Gold
        "user_types": ["pro"],
        "unlocks": "featured_eligibility",
    },
    MilestoneType.STREAK_14_DAY_1K: {
        "name": "14-Day 1K Streak",
        "description": "1,000+ original words for 14 consecutive days",
        "icon": "🌟",
        "animation": "golden_acorn_orbit",
        "color": "#D4A574",  # Soft Gold
        "user_types": ["pro"],
    },
    MilestoneType.STREAK_30_DAY_1K: {
        "name": "30-Day 1K Streak",
        "description": "1,000+ original words for 30 consecutive days",
        "icon": "🌳",
        "animation": "golden_acorn_tree",
        "color": "#D4A574",  # Soft Gold
        "user_types": ["pro"],
        "grants_flair": True,
    },
    MilestoneType.AUTHORITY_ELIGIBLE: {
        "name": "Authority Eligible",
        "description": "Met all requirements for Authority Writer status",
        "icon": "👑",
        "animation": "authority_glow",
        "color": "#D4A574",  # Gold
        "user_types": ["pro"],
    },
    MilestoneType.AUTHORITY_WRITER: {
        "name": "Authority Writer",
        "description": "Recognized voice in the Quirrely community",
        "icon": "👑",
        "animation": "authority_crown",
        "color": "#D4A574",  # Gold
        "user_types": ["pro"],
        "grants_flair": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_WRITER_REQUIREMENTS = {
    "featured_pieces": 3,           # 3+ accepted pieces
    "lifetime_words": 50000,        # 50K+ lifetime keystroke words
    "streak_30_count": 2,           # 2+ 30-day streaks completed
    "days_as_featured": 90,         # 90+ days since first Featured
}


# ═══════════════════════════════════════════════════════════════════════════
# MILESTONE TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class MilestoneTracker:
    """
    Tracks and triggers milestones based on keystroke word accumulation.
    
    Usage:
        tracker = MilestoneTracker()
        triggered = tracker.record_keystroke_words(
            user_id="123",
            word_count=250,
            tier=Tier.PRO,
            is_authenticated=True
        )
        
        for milestone in triggered:
            # Show celebration UI
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).parent / "milestones"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.milestones_file = self.storage_dir / "user_milestones.json"
        self.submissions_file = self.storage_dir / "featured_submissions.json"
        self._ensure_files()
    
    def _ensure_files(self):
        if not self.milestones_file.exists():
            self._write_json(self.milestones_file, {"users": {}})
        if not self.submissions_file.exists():
            self._write_json(self.submissions_file, {"submissions": []})
    
    def _read_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _write_json(self, path: Path, data: Dict[str, Any]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    # ─────────────────────────────────────────────────────────────────────
    # User Milestone State
    # ─────────────────────────────────────────────────────────────────────
    
    def get_user_milestones(self, user_id: str) -> UserMilestones:
        """Get milestone state for a user."""
        data = self._read_json(self.milestones_file)
        user_data = data.get("users", {}).get(user_id, {})
        
        if not user_data:
            return UserMilestones(user_id=user_id)
        
        # Parse dates
        for field in ["first_500_achieved_at", "featured_eligible_at", 
                      "featured_writer_since", "streak_1k_30_first_at"]:
            if user_data.get(field):
                user_data[field] = datetime.fromisoformat(user_data[field])
        
        for field in ["streak_500_last_date", "streak_1k_last_date"]:
            if user_data.get(field):
                user_data[field] = date.fromisoformat(user_data[field])
        
        return UserMilestones(**user_data)
    
    def _save_user_milestones(self, milestones: UserMilestones):
        """Save milestone state for a user."""
        data = self._read_json(self.milestones_file)
        if "users" not in data:
            data["users"] = {}
        
        user_data = asdict(milestones)
        # Convert dates to strings
        for key, value in user_data.items():
            if isinstance(value, (datetime, date)):
                user_data[key] = value.isoformat()
        
        data["users"][milestones.user_id] = user_data
        self._write_json(self.milestones_file, data)
    
    # ─────────────────────────────────────────────────────────────────────
    # Core Recording
    # ─────────────────────────────────────────────────────────────────────
    
    def record_keystroke_words(
        self,
        user_id: str,
        word_count: int,
        tier: Tier,
        is_authenticated: bool,
        save_enabled: bool = True,
    ) -> List[Milestone]:
        """
        Record keystroke words and check for triggered milestones.
        
        Args:
            user_id: User or session ID
            word_count: Number of keystroke words in this analysis
            tier: User's current tier
            is_authenticated: Whether user is logged in
            save_enabled: Whether user has opted into voice profile
            
        Returns:
            List of newly triggered milestones
        """
        if not save_enabled:
            # Without save, we can only track session — no milestones
            return []
        
        triggered = []
        today = date.today()
        now = datetime.utcnow()
        
        state = self.get_user_milestones(user_id)
        
        # Update lifetime total
        state.lifetime_keystroke_words += word_count
        
        # ─────────────────────────────────────────────────────────────────
        # FIRST 500 (any user)
        # ─────────────────────────────────────────────────────────────────
        if not state.first_500_achieved and state.lifetime_keystroke_words >= 500:
            state.first_500_achieved = True
            state.first_500_achieved_at = now
            triggered.append(Milestone(
                type=MilestoneType.FIRST_500,
                triggered_at=now,
                keystroke_words=state.lifetime_keystroke_words,
            ))
        
        # ─────────────────────────────────────────────────────────────────
        # DAILY TRACKING (need to track per-day totals)
        # ─────────────────────────────────────────────────────────────────
        daily_total = self._get_daily_keystroke_total(user_id, today) + word_count
        self._set_daily_keystroke_total(user_id, today, daily_total)
        
        # ─────────────────────────────────────────────────────────────────
        # 500/DAY STREAK (auth'd users)
        # ─────────────────────────────────────────────────────────────────
        if is_authenticated and daily_total >= 500:
            # Check if this extends streak
            if state.streak_500_last_date == today:
                pass  # Already counted today
            elif state.streak_500_last_date == today - timedelta(days=1):
                state.streak_500_current += 1
                state.streak_500_last_date = today
            else:
                state.streak_500_current = 1
                state.streak_500_last_date = today
            
            # Check for 3-day milestone
            if state.streak_500_current == 3:
                state.streak_500_3_count += 1
                triggered.append(Milestone(
                    type=MilestoneType.STREAK_3_DAY,
                    triggered_at=now,
                    keystroke_words=state.lifetime_keystroke_words,
                    streak_days=3,
                ))
        
        # ─────────────────────────────────────────────────────────────────
        # 1K/DAY TRACKING (PRO only)
        # ─────────────────────────────────────────────────────────────────
        if tier == Tier.PRO and daily_total >= 1000:
            # Daily 1K milestone (first time today)
            if state.streak_1k_last_date != today:
                # Check if this is genuinely the first 1K today
                prev_daily = daily_total - word_count
                if prev_daily < 1000:
                    state.daily_1k_count += 1
                    triggered.append(Milestone(
                        type=MilestoneType.DAILY_1K,
                        triggered_at=now,
                        keystroke_words=daily_total,
                    ))
            
            # Update streak
            if state.streak_1k_last_date == today:
                pass  # Already counted today
            elif state.streak_1k_last_date == today - timedelta(days=1):
                state.streak_1k_current += 1
                state.streak_1k_last_date = today
            else:
                state.streak_1k_current = 1
                state.streak_1k_last_date = today
            
            # Update longest
            if state.streak_1k_current > state.streak_1k_longest:
                state.streak_1k_longest = state.streak_1k_current
            
            # Check streak milestones
            streak = state.streak_1k_current
            
            if streak == 3 and state.streak_1k_3_count < self._count_streak_achievements(state, 3):
                state.streak_1k_3_count += 1
                triggered.append(Milestone(
                    type=MilestoneType.STREAK_3_DAY_1K,
                    triggered_at=now,
                    keystroke_words=state.lifetime_keystroke_words,
                    streak_days=3,
                ))
            
            if streak == 7:
                # Only trigger once per streak
                if not self._streak_milestone_triggered_this_streak(state, 7):
                    state.streak_1k_7_count += 1
                    state.featured_eligible = True
                    state.featured_eligible_at = now
                    triggered.append(Milestone(
                        type=MilestoneType.STREAK_7_DAY_1K,
                        triggered_at=now,
                        keystroke_words=state.lifetime_keystroke_words,
                        streak_days=7,
                    ))
            
            if streak == 14:
                if not self._streak_milestone_triggered_this_streak(state, 14):
                    state.streak_1k_14_count += 1
                    triggered.append(Milestone(
                        type=MilestoneType.STREAK_14_DAY_1K,
                        triggered_at=now,
                        keystroke_words=state.lifetime_keystroke_words,
                        streak_days=14,
                    ))
            
            if streak == 30:
                if not self._streak_milestone_triggered_this_streak(state, 30):
                    state.streak_1k_30_count += 1
                    if state.streak_1k_30_first_at is None:
                        state.streak_1k_30_first_at = now
                    triggered.append(Milestone(
                        type=MilestoneType.STREAK_30_DAY_1K,
                        triggered_at=now,
                        keystroke_words=state.lifetime_keystroke_words,
                        streak_days=30,
                    ))
        
        # Save state
        self._save_user_milestones(state)
        
        return triggered
    
    def _count_streak_achievements(self, state: UserMilestones, days: int) -> int:
        """Count how many times a streak milestone should have been achieved."""
        # This is a simplification — in production, track each achievement
        return state.streak_1k_current // days
    
    def _streak_milestone_triggered_this_streak(self, state: UserMilestones, days: int) -> bool:
        """Check if milestone already triggered in current streak."""
        # Simplified: if current streak is exactly the milestone, it's new
        return state.streak_1k_current > days
    
    # ─────────────────────────────────────────────────────────────────────
    # Daily Totals Storage
    # ─────────────────────────────────────────────────────────────────────
    
    def _get_daily_keystroke_total(self, user_id: str, day: date) -> int:
        """Get total keystroke words for a user on a specific day."""
        daily_file = self.storage_dir / "daily_totals.json"
        if not daily_file.exists():
            return 0
        
        data = self._read_json(daily_file)
        return data.get(user_id, {}).get(day.isoformat(), 0)
    
    def _set_daily_keystroke_total(self, user_id: str, day: date, total: int):
        """Set total keystroke words for a user on a specific day."""
        daily_file = self.storage_dir / "daily_totals.json"
        if daily_file.exists():
            data = self._read_json(daily_file)
        else:
            data = {}
        
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id][day.isoformat()] = total
        
        # Clean up old entries (keep 60 days)
        cutoff = (date.today() - timedelta(days=60)).isoformat()
        data[user_id] = {k: v for k, v in data[user_id].items() if k >= cutoff}
        
        self._write_json(daily_file, data)
    
    # ─────────────────────────────────────────────────────────────────────
    # Featured Writer Submissions
    # ─────────────────────────────────────────────────────────────────────
    
    def can_submit_featured(self, user_id: str, tier: Tier) -> Dict[str, Any]:
        """Check if user can submit for Featured Writer."""
        if tier != Tier.PRO:
            return {"eligible": False, "reason": "PRO subscription required"}
        
        state = self.get_user_milestones(user_id)
        
        if not state.featured_eligible:
            return {
                "eligible": False,
                "reason": "Complete a 7-day 1K streak to unlock eligibility",
                "current_streak": state.streak_1k_current,
                "needed": 7,
            }
        
        if state.featured_writer:
            return {
                "eligible": False,
                "reason": "Already a Featured Writer",
                "featured_since": state.featured_writer_since,
                "featured_url": state.featured_piece_url,
            }
        
        # Check for pending submission
        pending = self._get_pending_submission(user_id)
        if pending:
            return {
                "eligible": False,
                "reason": "Submission pending review",
                "submitted_at": pending.submitted_at,
            }
        
        return {"eligible": True}
    
    def submit_featured_piece(
        self,
        user_id: str,
        text: str,
        keystroke_verified: bool,
    ) -> Dict[str, Any]:
        """
        Submit a piece for Featured Writer consideration.
        
        Args:
            user_id: User ID
            text: The submission text (max 500 words)
            keystroke_verified: Whether input was verified as keystroke
            
        Returns:
            Result dict with success status
        """
        word_count = len(text.split())
        
        # Validations
        if word_count > 500:
            return {"success": False, "error": "Submission must be 500 words or fewer"}
        
        if not keystroke_verified:
            return {"success": False, "error": "Submission must be original typed writing"}
        
        # Create submission
        import uuid
        submission = FeaturedSubmission(
            id=str(uuid.uuid4()),
            user_id=user_id,
            submitted_at=datetime.utcnow(),
            text=text,
            word_count=word_count,
            keystroke_verified=keystroke_verified,
            agreement_accepted_at=datetime.utcnow(),
            status=SubmissionStatus.PENDING,
        )
        
        # Save
        data = self._read_json(self.submissions_file)
        submissions = data.get("submissions", [])
        submissions.append(asdict(submission))
        data["submissions"] = submissions
        self._write_json(self.submissions_file, data)
        
        return {
            "success": True,
            "submission_id": submission.id,
            "message": "Submission received. We'll review and get back to you.",
        }
    
    def _get_pending_submission(self, user_id: str) -> Optional[FeaturedSubmission]:
        """Get pending submission for a user."""
        data = self._read_json(self.submissions_file)
        for sub in data.get("submissions", []):
            if sub["user_id"] == user_id and sub["status"] == "pending":
                return FeaturedSubmission(**sub)
        return None
    
    def review_submission(
        self,
        submission_id: str,
        accept: bool,
        reviewer_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Review a Featured Writer submission (admin function).
        
        Args:
            submission_id: Submission ID
            accept: Whether to accept the submission
            reviewer_notes: Internal notes
            
        Returns:
            Result dict
        """
        data = self._read_json(self.submissions_file)
        
        for i, sub in enumerate(data.get("submissions", [])):
            if sub["id"] == submission_id:
                sub["status"] = "accepted" if accept else "declined"
                sub["reviewed_at"] = datetime.utcnow().isoformat()
                sub["reviewer_notes"] = reviewer_notes
                data["submissions"][i] = sub
                self._write_json(self.submissions_file, data)
                
                if accept:
                    # Update user milestone state
                    user_id = sub["user_id"]
                    state = self.get_user_milestones(user_id)
                    state.featured_writer = True
                    state.featured_writer_since = datetime.utcnow()
                    state.featured_piece_url = f"/featured/{user_id}"
                    self._save_user_milestones(state)
                
                return {"success": True, "status": sub["status"]}
        
        return {"success": False, "error": "Submission not found"}
    
    # ─────────────────────────────────────────────────────────────────────
    # Badge Generation
    # ─────────────────────────────────────────────────────────────────────
    
    def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all earned badges for a user (for public profile)."""
        state = self.get_user_milestones(user_id)
        badges = []
        
        # Authority Writer (highest tier - show first)
        if state.authority_writer:
            badges.append({
                "type": "authority_writer",
                "name": "Authority Writer",
                "icon": "👑",
                "since": state.authority_writer_since,
                "tier": "authority",
            })
        
        # Featured Writer
        if state.featured_writer:
            badges.append({
                "type": "featured_writer",
                "name": "Featured Writer",
                "icon": "⭐",
                "since": state.featured_writer_since,
                "url": state.featured_piece_url,
                "count": state.featured_pieces_count,
            })
        
        if state.first_500_achieved:
            badges.append({
                "type": "first_500",
                "name": "First 500",
                "icon": "✍️",
                "earned_at": state.first_500_achieved_at,
            })
        
        if state.streak_500_3_count > 0:
            badges.append({
                "type": "streak_3_day",
                "name": "3-Day Streak",
                "icon": "🌰🌰🌰",
                "count": state.streak_500_3_count,
            })
        
        if state.daily_1k_count > 0:
            badges.append({
                "type": "daily_1k",
                "name": "Daily 1K",
                "icon": "🔥",
                "count": state.daily_1k_count,
            })
        
        if state.streak_1k_3_count > 0:
            badges.append({
                "type": "streak_3_day_1k",
                "name": "3-Day 1K Streak",
                "icon": "👑",
                "count": state.streak_1k_3_count,
            })
        
        if state.streak_1k_7_count > 0:
            badges.append({
                "type": "streak_7_day_1k",
                "name": "7-Day 1K Streak",
                "icon": "💫",
                "count": state.streak_1k_7_count,
            })
        
        if state.streak_1k_14_count > 0:
            badges.append({
                "type": "streak_14_day_1k",
                "name": "14-Day 1K Streak",
                "icon": "🌟",
                "count": state.streak_1k_14_count,
            })
        
        if state.streak_1k_30_count > 0:
            badges.append({
                "type": "streak_30_day_1k",
                "name": "30-Day 1K Streak",
                "icon": "🌳",
                "count": state.streak_1k_30_count,
                "has_flair": True,
            })
        
        return badges
    
    # ─────────────────────────────────────────────────────────────────────
    # Authority Writer Tracking
    # ─────────────────────────────────────────────────────────────────────
    
    def check_authority_eligibility(self, user_id: str) -> Dict[str, Any]:
        """Check if user meets Authority Writer requirements."""
        state = self.get_user_milestones(user_id)
        reqs = AUTHORITY_WRITER_REQUIREMENTS
        
        # Must be Featured Writer first
        if not state.featured_writer:
            return {
                "eligible": False,
                "reason": "Must be a Featured Writer first",
                "progress": {},
            }
        
        # Calculate days as Featured
        days_as_featured = 0
        if state.featured_writer_since:
            days_as_featured = (datetime.utcnow() - state.featured_writer_since).days
        
        progress = {
            "featured_pieces": {
                "current": state.featured_pieces_count,
                "target": reqs["featured_pieces"],
                "complete": state.featured_pieces_count >= reqs["featured_pieces"],
            },
            "lifetime_words": {
                "current": state.lifetime_keystroke_words,
                "target": reqs["lifetime_words"],
                "complete": state.lifetime_keystroke_words >= reqs["lifetime_words"],
            },
            "streak_30_count": {
                "current": state.streak_1k_30_count,
                "target": reqs["streak_30_count"],
                "complete": state.streak_1k_30_count >= reqs["streak_30_count"],
            },
            "days_as_featured": {
                "current": days_as_featured,
                "target": reqs["days_as_featured"],
                "complete": days_as_featured >= reqs["days_as_featured"],
            },
        }
        
        all_complete = all(p["complete"] for p in progress.values())
        
        return {
            "eligible": all_complete,
            "progress": progress,
            "percent_complete": sum(1 for p in progress.values() if p["complete"]) * 25,
        }
    
    def grant_authority_writer(self, user_id: str) -> Dict[str, Any]:
        """Grant Authority Writer status (called after eligibility confirmed)."""
        state = self.get_user_milestones(user_id)
        
        eligibility = self.check_authority_eligibility(user_id)
        if not eligibility["eligible"]:
            return {"success": False, "reason": "Not eligible"}
        
        if state.authority_writer:
            return {"success": False, "reason": "Already an Authority Writer"}
        
        state.authority_eligible = True
        state.authority_eligible_at = datetime.utcnow()
        state.authority_writer = True
        state.authority_writer_since = datetime.utcnow()
        state.authority_last_active = datetime.utcnow()
        
        self._save_user_milestones(state)
        
        return {
            "success": True,
            "message": "Authority Writer status granted",
            "since": state.authority_writer_since,
        }
    
    def check_authority_active(self, user_id: str) -> Dict[str, Any]:
        """Check if Authority status is still active (not lapsed)."""
        state = self.get_user_milestones(user_id)
        
        if not state.authority_writer:
            return {"active": False, "reason": "Not an Authority Writer"}
        
        # Check for 180-day inactivity
        if state.authority_last_active:
            days_inactive = (datetime.utcnow() - state.authority_last_active).days
            if days_inactive > 180:
                return {
                    "active": False,
                    "reason": "Inactive for 180+ days",
                    "days_inactive": days_inactive,
                    "can_reactivate": True,
                }
        
        return {"active": True, "since": state.authority_writer_since}
    
    def update_authority_activity(self, user_id: str):
        """Update last active timestamp for Authority Writer."""
        state = self.get_user_milestones(user_id)
        if state.authority_writer:
            state.authority_last_active = datetime.utcnow()
            self._save_user_milestones(state)
    
    def record_featured_piece_accepted(self, user_id: str) -> Dict[str, Any]:
        """Record when a Featured Writer piece is accepted."""
        state = self.get_user_milestones(user_id)
        
        state.featured_pieces_count += 1
        
        # Check for Authority eligibility
        triggered = []
        if not state.authority_eligible:
            eligibility = self.check_authority_eligibility(user_id)
            if eligibility["eligible"]:
                state.authority_eligible = True
                state.authority_eligible_at = datetime.utcnow()
                triggered.append(MilestoneType.AUTHORITY_ELIGIBLE)
        
        self._save_user_milestones(state)
        
        return {
            "pieces_count": state.featured_pieces_count,
            "authority_eligible": state.authority_eligible,
            "triggered": [t.value for t in triggered],
        }
    
    def get_authority_progress(self, user_id: str) -> Dict[str, Any]:
        """Get progress toward Authority Writer for dashboard."""
        state = self.get_user_milestones(user_id)
        eligibility = self.check_authority_eligibility(user_id)
        
        return {
            "is_featured_writer": state.featured_writer,
            "is_authority_writer": state.authority_writer,
            "authority_eligible": state.authority_eligible,
            "progress": eligibility.get("progress", {}),
            "percent_complete": eligibility.get("percent_complete", 0),
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_tracker: Optional[MilestoneTracker] = None


def get_milestone_tracker() -> MilestoneTracker:
    global _tracker
    if _tracker is None:
        _tracker = MilestoneTracker()
    return _tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tracker = MilestoneTracker()
    
    # Simulate a PRO user writing over several days
    print("=== Milestone Tracker Demo ===\n")
    
    # Day 1: 1,200 words
    triggered = tracker.record_keystroke_words(
        user_id="demo_user",
        word_count=1200,
        tier=Tier.PRO,
        is_authenticated=True,
        save_enabled=True,
    )
    print(f"Day 1 (1,200 words): {[m.type.value for m in triggered]}")
    
    # Check state
    state = tracker.get_user_milestones("demo_user")
    print(f"  Lifetime words: {state.lifetime_keystroke_words}")
    print(f"  First 500: {state.first_500_achieved}")
    print(f"  1K streak: {state.streak_1k_current}")
    
    # Get badges
    badges = tracker.get_user_badges("demo_user")
    print(f"  Badges: {[b['name'] for b in badges]}")
