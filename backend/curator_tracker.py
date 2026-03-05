#!/usr/bin/env python3
"""
QUIRRELY CURATOR MILESTONE SYSTEM v1.0
Featured Curator eligibility tracking and submission.

Requirements (all within 30 days):
- 20 posts read
- 5 deep reads (>80% scroll + >2min)
- 5 different profile types explored
- 10 bookmarks
- 7-day reading streak

Aligned with Reader Funnel and Writer Milestone systems.
"""

from __future__ import annotations

import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & TYPES
# ═══════════════════════════════════════════════════════════════════════════

class CuratorMilestoneType(str, Enum):
    POSTS_READ = "posts_read"           # 20 posts
    DEEP_READS = "deep_reads"           # 5 deep reads
    PROFILE_TYPES = "profile_types"     # 5 different types
    BOOKMARKS = "bookmarks"             # 10 bookmarks
    READING_STREAK = "reading_streak"   # 7-day streak
    FEATURED_ELIGIBLE = "featured_eligible"  # All complete within 30 days


class CuratorSubmissionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


@dataclass
class CuratorMilestoneState:
    """Complete milestone state for a Curator."""
    user_id: str
    
    # Window tracking
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    window_active: bool = False
    
    # Milestone progress
    posts_read: int = 0
    posts_read_ids: List[str] = field(default_factory=list)
    
    deep_reads: int = 0
    deep_read_ids: List[str] = field(default_factory=list)
    
    profile_types_explored: List[str] = field(default_factory=list)
    
    bookmarks_count: int = 0
    
    reading_streak_current: int = 0
    reading_streak_last_date: Optional[date] = None
    reading_streak_completed: bool = False
    
    # Completion tracking
    posts_read_complete: bool = False
    deep_reads_complete: bool = False
    profile_types_complete: bool = False
    bookmarks_complete: bool = False
    streak_complete: bool = False
    
    # Featured eligibility
    featured_eligible: bool = False
    featured_eligible_at: Optional[datetime] = None
    
    # Featured Curator status
    featured_curator: bool = False
    featured_curator_since: Optional[datetime] = None
    featured_path_id: Optional[str] = None
    featured_path_url: Optional[str] = None
    featured_paths_count: int = 0  # Total accepted paths
    
    # Lifetime stats (for Authority)
    lifetime_posts_read: int = 0
    lifetime_deep_reads: int = 0
    total_path_follows: int = 0  # How many times others followed their paths
    
    # Authority Curator
    authority_eligible: bool = False
    authority_eligible_at: Optional[datetime] = None
    authority_curator: bool = False
    authority_curator_since: Optional[datetime] = None
    authority_last_active: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CuratedPath:
    """A curated reading path submission."""
    id: str
    user_id: str
    
    # Path content
    title: str
    intro: str  # 100 words max
    post_ids: List[str]  # 4-6 profile IDs in order
    
    # Agreements
    agreement_original: bool
    agreement_permission: bool
    agreement_read_all: bool
    agreement_accepted_at: datetime
    
    # Review status
    status: CuratorSubmissionStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    
    # If accepted
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None


# ═══════════════════════════════════════════════════════════════════════════
# MILESTONE TARGETS
# ═══════════════════════════════════════════════════════════════════════════

CURATOR_TARGETS = {
    "posts_read": 20,
    "deep_reads": 5,
    "profile_types": 5,
    "bookmarks": 10,
    "reading_streak": 7,
    "window_days": 30,
}

# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY CURATOR REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════

AUTHORITY_CURATOR_REQUIREMENTS = {
    "featured_paths": 3,           # 3+ accepted paths
    "total_path_follows": 50,      # 50+ people followed their paths
    "lifetime_deep_reads": 100,    # 100+ deep reads lifetime
    "days_as_featured": 90,        # 90+ days since first Featured
}

MILESTONE_META = {
    CuratorMilestoneType.POSTS_READ: {
        "name": "Breadth",
        "target": 20,
        "description": "Read 20 posts",
        "complete_message": "You know the landscape",
        "icon": "📖",
    },
    CuratorMilestoneType.DEEP_READS: {
        "name": "Depth",
        "target": 5,
        "description": "Deep read 5 posts",
        "complete_message": "You engage seriously",
        "icon": "📚",
    },
    CuratorMilestoneType.PROFILE_TYPES: {
        "name": "Range",
        "target": 5,
        "description": "Explore 5 profile types",
        "complete_message": "You have range",
        "icon": "🌈",
    },
    CuratorMilestoneType.BOOKMARKS: {
        "name": "Curation",
        "target": 10,
        "description": "Bookmark 10 favorites",
        "complete_message": "You're curating",
        "icon": "📑",
    },
    CuratorMilestoneType.READING_STREAK: {
        "name": "Consistency",
        "target": 7,
        "description": "7-day reading streak",
        "complete_message": "You're consistent",
        "icon": "🔥",
    },
    CuratorMilestoneType.FEATURED_ELIGIBLE: {
        "name": "Featured Curator Eligible",
        "target": 1,
        "description": "Complete all milestones within 30 days",
        "complete_message": "You're eligible to become a Featured Curator",
        "icon": "⭐",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# CURATOR TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class CuratorMilestoneTracker:
    """
    Tracks Curator milestones and Featured Curator eligibility.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).parent / "curator_milestones"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.storage_dir / "curator_states.json"
        self.paths_file = self.storage_dir / "curated_paths.json"
        self._ensure_files()
    
    def _ensure_files(self):
        if not self.state_file.exists():
            self._write_json(self.state_file, {"users": {}})
        if not self.paths_file.exists():
            self._write_json(self.paths_file, {"paths": []})
    
    def _read_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _write_json(self, path: Path, data: Dict[str, Any]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    # ─────────────────────────────────────────────────────────────────────
    # State Management
    # ─────────────────────────────────────────────────────────────────────
    
    def get_state(self, user_id: str) -> CuratorMilestoneState:
        """Get milestone state for a Curator."""
        data = self._read_json(self.state_file)
        user_data = data.get("users", {}).get(user_id, {})
        
        if not user_data:
            return CuratorMilestoneState(user_id=user_id)
        
        # Parse dates
        for field_name in ["window_start", "window_end", "featured_eligible_at", 
                          "featured_curator_since", "created_at", "updated_at"]:
            if user_data.get(field_name):
                user_data[field_name] = datetime.fromisoformat(user_data[field_name])
        
        if user_data.get("reading_streak_last_date"):
            user_data["reading_streak_last_date"] = date.fromisoformat(
                user_data["reading_streak_last_date"]
            )
        
        return CuratorMilestoneState(**user_data)
    
    def _save_state(self, state: CuratorMilestoneState):
        """Save milestone state."""
        data = self._read_json(self.state_file)
        if "users" not in data:
            data["users"] = {}
        
        state.updated_at = datetime.utcnow()
        state_dict = asdict(state)
        
        # Convert dates to strings
        for key, value in state_dict.items():
            if isinstance(value, (datetime, date)):
                state_dict[key] = value.isoformat()
        
        data["users"][state.user_id] = state_dict
        self._write_json(self.state_file, data)
    
    # ─────────────────────────────────────────────────────────────────────
    # Window Management
    # ─────────────────────────────────────────────────────────────────────
    
    def start_window(self, user_id: str) -> CuratorMilestoneState:
        """Start or reset the 30-day window for a Curator."""
        state = self.get_state(user_id)
        now = datetime.utcnow()
        
        state.window_start = now
        state.window_end = now + timedelta(days=CURATOR_TARGETS["window_days"])
        state.window_active = True
        
        # Reset progress
        state.posts_read = 0
        state.posts_read_ids = []
        state.deep_reads = 0
        state.deep_read_ids = []
        state.profile_types_explored = []
        state.bookmarks_count = 0
        state.reading_streak_current = 0
        state.reading_streak_last_date = None
        state.reading_streak_completed = False
        
        state.posts_read_complete = False
        state.deep_reads_complete = False
        state.profile_types_complete = False
        state.bookmarks_complete = False
        state.streak_complete = False
        state.featured_eligible = False
        state.featured_eligible_at = None
        
        self._save_state(state)
        return state
    
    def check_window(self, state: CuratorMilestoneState) -> Dict[str, Any]:
        """Check window status and days remaining."""
        if not state.window_active or not state.window_end:
            return {"active": False, "days_remaining": 0, "expired": False}
        
        now = datetime.utcnow()
        if now > state.window_end:
            return {"active": False, "days_remaining": 0, "expired": True}
        
        days_remaining = (state.window_end - now).days
        return {"active": True, "days_remaining": days_remaining, "expired": False}
    
    # ─────────────────────────────────────────────────────────────────────
    # Progress Recording
    # ─────────────────────────────────────────────────────────────────────
    
    def record_post_read(
        self,
        user_id: str,
        profile_id: str,
        is_deep_read: bool = False,
    ) -> Dict[str, Any]:
        """Record a post read event."""
        state = self.get_state(user_id)
        window = self.check_window(state)
        
        if not window["active"]:
            if window["expired"]:
                # Auto-restart window
                state = self.start_window(user_id)
            else:
                # Not a Curator yet or window not started
                return {"recorded": False, "reason": "no_active_window"}
        
        triggered = []
        today = date.today()
        profile_type = profile_id.split("-")[0] if "-" in profile_id else profile_id
        
        # Posts read
        if profile_id not in state.posts_read_ids:
            state.posts_read_ids.append(profile_id)
            state.posts_read = len(state.posts_read_ids)
            
            if state.posts_read >= CURATOR_TARGETS["posts_read"] and not state.posts_read_complete:
                state.posts_read_complete = True
                triggered.append(CuratorMilestoneType.POSTS_READ)
        
        # Deep reads
        if is_deep_read and profile_id not in state.deep_read_ids:
            state.deep_read_ids.append(profile_id)
            state.deep_reads = len(state.deep_read_ids)
            
            if state.deep_reads >= CURATOR_TARGETS["deep_reads"] and not state.deep_reads_complete:
                state.deep_reads_complete = True
                triggered.append(CuratorMilestoneType.DEEP_READS)
        
        # Profile types
        if profile_type not in state.profile_types_explored:
            state.profile_types_explored.append(profile_type)
            
            if len(state.profile_types_explored) >= CURATOR_TARGETS["profile_types"] and not state.profile_types_complete:
                state.profile_types_complete = True
                triggered.append(CuratorMilestoneType.PROFILE_TYPES)
        
        # Reading streak
        if state.reading_streak_last_date == today:
            pass  # Already counted today
        elif state.reading_streak_last_date == today - timedelta(days=1):
            state.reading_streak_current += 1
            state.reading_streak_last_date = today
        else:
            state.reading_streak_current = 1
            state.reading_streak_last_date = today
        
        if state.reading_streak_current >= CURATOR_TARGETS["reading_streak"] and not state.streak_complete:
            state.streak_complete = True
            state.reading_streak_completed = True
            triggered.append(CuratorMilestoneType.READING_STREAK)
        
        # Check for Featured eligibility
        if self._check_all_complete(state) and not state.featured_eligible:
            state.featured_eligible = True
            state.featured_eligible_at = datetime.utcnow()
            triggered.append(CuratorMilestoneType.FEATURED_ELIGIBLE)
        
        self._save_state(state)
        
        return {
            "recorded": True,
            "triggered": [t.value for t in triggered],
            "progress": self.get_progress(user_id),
        }
    
    def record_bookmark(self, user_id: str) -> Dict[str, Any]:
        """Record a bookmark event."""
        state = self.get_state(user_id)
        window = self.check_window(state)
        
        if not window["active"]:
            return {"recorded": False, "reason": "no_active_window"}
        
        triggered = []
        state.bookmarks_count += 1
        
        if state.bookmarks_count >= CURATOR_TARGETS["bookmarks"] and not state.bookmarks_complete:
            state.bookmarks_complete = True
            triggered.append(CuratorMilestoneType.BOOKMARKS)
        
        # Check for Featured eligibility
        if self._check_all_complete(state) and not state.featured_eligible:
            state.featured_eligible = True
            state.featured_eligible_at = datetime.utcnow()
            triggered.append(CuratorMilestoneType.FEATURED_ELIGIBLE)
        
        self._save_state(state)
        
        return {
            "recorded": True,
            "triggered": [t.value for t in triggered],
            "progress": self.get_progress(user_id),
        }
    
    def _check_all_complete(self, state: CuratorMilestoneState) -> bool:
        """Check if all milestones are complete."""
        return (
            state.posts_read_complete and
            state.deep_reads_complete and
            state.profile_types_complete and
            state.bookmarks_complete and
            state.streak_complete
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # Progress Retrieval
    # ─────────────────────────────────────────────────────────────────────
    
    def get_progress(self, user_id: str) -> Dict[str, Any]:
        """Get current progress toward Featured Curator."""
        state = self.get_state(user_id)
        window = self.check_window(state)
        
        milestones = {
            "posts_read": {
                "current": state.posts_read,
                "target": CURATOR_TARGETS["posts_read"],
                "complete": state.posts_read_complete,
                "icon": "📖",
            },
            "deep_reads": {
                "current": state.deep_reads,
                "target": CURATOR_TARGETS["deep_reads"],
                "complete": state.deep_reads_complete,
                "icon": "📚",
            },
            "profile_types": {
                "current": len(state.profile_types_explored),
                "target": CURATOR_TARGETS["profile_types"],
                "complete": state.profile_types_complete,
                "explored": state.profile_types_explored,
                "icon": "🌈",
            },
            "bookmarks": {
                "current": state.bookmarks_count,
                "target": CURATOR_TARGETS["bookmarks"],
                "complete": state.bookmarks_complete,
                "icon": "📑",
            },
            "reading_streak": {
                "current": state.reading_streak_current,
                "target": CURATOR_TARGETS["reading_streak"],
                "complete": state.streak_complete,
                "icon": "🔥",
            },
        }
        
        completed_count = sum(1 for m in milestones.values() if m["complete"])
        total_count = len(milestones)
        
        return {
            "window_active": window["active"],
            "days_remaining": window["days_remaining"],
            "window_expired": window.get("expired", False),
            "milestones": milestones,
            "completed_count": completed_count,
            "total_count": total_count,
            "percent_complete": round((completed_count / total_count) * 100),
            "featured_eligible": state.featured_eligible,
            "featured_curator": state.featured_curator,
        }
    
    def get_next_action(self, user_id: str) -> Dict[str, Any]:
        """Get the recommended next action for the Curator."""
        progress = self.get_progress(user_id)
        milestones = progress["milestones"]
        
        # Priority: streak (time-sensitive) > types (exploration) > others
        if not milestones["reading_streak"]["complete"]:
            days_in = milestones["reading_streak"]["current"]
            if days_in > 0:
                return {
                    "action": "maintain_streak",
                    "message": f"Day {days_in + 1} — Keep your streak alive",
                    "cta": "Read today",
                }
        
        if not milestones["profile_types"]["complete"]:
            explored = set(milestones["profile_types"]["explored"])
            all_types = {"ASSERTIVE", "MINIMAL", "POETIC", "DENSE", "CONVERSATIONAL", 
                        "FORMAL", "BALANCED", "LONGFORM", "INTERROGATIVE", "HEDGED"}
            unexplored = all_types - explored
            if unexplored:
                next_type = sorted(unexplored)[0]
                return {
                    "action": "explore_type",
                    "message": f"Explore a {next_type} voice",
                    "cta": f"Discover {next_type}",
                    "profile_type": next_type,
                }
        
        if not milestones["deep_reads"]["complete"]:
            return {
                "action": "deep_read",
                "message": "Take time with a post — read deeply",
                "cta": "Find a post to savor",
            }
        
        if not milestones["bookmarks"]["complete"]:
            return {
                "action": "bookmark",
                "message": "Save your favorites",
                "cta": "Bookmark posts you'd recommend",
            }
        
        if not milestones["posts_read"]["complete"]:
            remaining = milestones["posts_read"]["target"] - milestones["posts_read"]["current"]
            return {
                "action": "read_more",
                "message": f"{remaining} more posts to explore",
                "cta": "Keep reading",
            }
        
        if progress["featured_eligible"]:
            return {
                "action": "submit_path",
                "message": "You're eligible! Create your reading path",
                "cta": "Create My Path",
            }
        
        return {
            "action": "continue",
            "message": "Keep exploring",
            "cta": "Continue",
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # Featured Path Submission
    # ─────────────────────────────────────────────────────────────────────
    
    def can_submit_path(self, user_id: str) -> Dict[str, Any]:
        """Check if user can submit a curated path."""
        state = self.get_state(user_id)
        
        if state.featured_curator:
            return {
                "can_submit": False,
                "reason": "Already a Featured Curator",
                "featured_since": state.featured_curator_since,
            }
        
        if not state.featured_eligible:
            progress = self.get_progress(user_id)
            return {
                "can_submit": False,
                "reason": "Complete all milestones to unlock",
                "progress": progress,
            }
        
        # Check for pending submission
        pending = self._get_pending_path(user_id)
        if pending:
            return {
                "can_submit": False,
                "reason": "Submission pending review",
                "submitted_at": pending.submitted_at,
            }
        
        return {"can_submit": True}
    
    def submit_path(
        self,
        user_id: str,
        title: str,
        intro: str,
        post_ids: List[str],
    ) -> Dict[str, Any]:
        """Submit a curated reading path."""
        # Validations
        word_count = len(intro.split())
        if word_count > 100:
            return {"success": False, "error": f"Intro must be 100 words or fewer ({word_count} words)"}
        
        if len(post_ids) < 4 or len(post_ids) > 6:
            return {"success": False, "error": "Path must contain 4-6 posts"}
        
        if len(title) > 100:
            return {"success": False, "error": "Title too long"}
        
        # Create path
        import uuid
        path = CuratedPath(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            intro=intro,
            post_ids=post_ids,
            agreement_original=True,
            agreement_permission=True,
            agreement_read_all=True,
            agreement_accepted_at=datetime.utcnow(),
            status=CuratorSubmissionStatus.PENDING,
            submitted_at=datetime.utcnow(),
        )
        
        # Save
        data = self._read_json(self.paths_file)
        paths = data.get("paths", [])
        paths.append(asdict(path))
        data["paths"] = paths
        self._write_json(self.paths_file, data)
        
        return {
            "success": True,
            "path_id": path.id,
            "message": "Your path has been submitted for review.",
        }
    
    def _get_pending_path(self, user_id: str) -> Optional[CuratedPath]:
        """Get pending path submission for a user."""
        data = self._read_json(self.paths_file)
        for path_data in data.get("paths", []):
            if path_data["user_id"] == user_id and path_data["status"] == "pending":
                return CuratedPath(**path_data)
        return None
    
    def review_path(
        self,
        path_id: str,
        accept: bool,
        reviewer_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Review a curated path submission (admin)."""
        data = self._read_json(self.paths_file)
        
        for i, path_data in enumerate(data.get("paths", [])):
            if path_data["id"] == path_id:
                path_data["status"] = "accepted" if accept else "declined"
                path_data["reviewed_at"] = datetime.utcnow().isoformat()
                path_data["reviewer_notes"] = reviewer_notes
                
                if accept:
                    user_id = path_data["user_id"]
                    path_data["published_url"] = f"/paths/{user_id}"
                    path_data["published_at"] = datetime.utcnow().isoformat()
                    
                    # Update user state
                    state = self.get_state(user_id)
                    state.featured_curator = True
                    state.featured_curator_since = datetime.utcnow()
                    state.featured_path_id = path_id
                    state.featured_path_url = path_data["published_url"]
                    self._save_state(state)
                
                data["paths"][i] = path_data
                self._write_json(self.paths_file, data)
                
                return {"success": True, "status": path_data["status"]}
        
        return {"success": False, "error": "Path not found"}
    
    # ─────────────────────────────────────────────────────────────────────
    # Published Paths
    # ─────────────────────────────────────────────────────────────────────
    
    def get_featured_paths(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get published featured paths."""
        data = self._read_json(self.paths_file)
        accepted = [
            p for p in data.get("paths", [])
            if p["status"] == "accepted"
        ]
        # Sort by published date, newest first
        accepted.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return accepted[:limit]
    
    def get_path_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's published path."""
        data = self._read_json(self.paths_file)
        for path_data in data.get("paths", []):
            if path_data["user_id"] == user_id and path_data["status"] == "accepted":
                return path_data
        return None
    
    # ─────────────────────────────────────────────────────────────────────
    # Authority Curator Tracking
    # ─────────────────────────────────────────────────────────────────────
    
    def check_authority_curator_eligibility(self, user_id: str) -> Dict[str, Any]:
        """Check if user meets Authority Curator requirements."""
        state = self.get_state(user_id)
        reqs = AUTHORITY_CURATOR_REQUIREMENTS
        
        # Must be Featured Curator first
        if not state.featured_curator:
            return {
                "eligible": False,
                "reason": "Must be a Featured Curator first",
                "progress": {},
            }
        
        # Calculate days as Featured
        days_as_featured = 0
        if state.featured_curator_since:
            days_as_featured = (datetime.utcnow() - state.featured_curator_since).days
        
        progress = {
            "featured_paths": {
                "current": state.featured_paths_count,
                "target": reqs["featured_paths"],
                "complete": state.featured_paths_count >= reqs["featured_paths"],
                "icon": "📚",
            },
            "total_path_follows": {
                "current": state.total_path_follows,
                "target": reqs["total_path_follows"],
                "complete": state.total_path_follows >= reqs["total_path_follows"],
                "icon": "👥",
            },
            "lifetime_deep_reads": {
                "current": state.lifetime_deep_reads,
                "target": reqs["lifetime_deep_reads"],
                "complete": state.lifetime_deep_reads >= reqs["lifetime_deep_reads"],
                "icon": "📖",
            },
            "days_as_featured": {
                "current": days_as_featured,
                "target": reqs["days_as_featured"],
                "complete": days_as_featured >= reqs["days_as_featured"],
                "icon": "📅",
            },
        }
        
        all_complete = all(p["complete"] for p in progress.values())
        
        return {
            "eligible": all_complete,
            "progress": progress,
            "percent_complete": sum(1 for p in progress.values() if p["complete"]) * 25,
        }
    
    def grant_authority_curator(self, user_id: str) -> Dict[str, Any]:
        """Grant Authority Curator status (called after eligibility confirmed)."""
        state = self.get_state(user_id)
        
        eligibility = self.check_authority_curator_eligibility(user_id)
        if not eligibility["eligible"]:
            return {"success": False, "reason": "Not eligible"}
        
        if state.authority_curator:
            return {"success": False, "reason": "Already an Authority Curator"}
        
        state.authority_eligible = True
        state.authority_eligible_at = datetime.utcnow()
        state.authority_curator = True
        state.authority_curator_since = datetime.utcnow()
        state.authority_last_active = datetime.utcnow()
        
        self._save_state(state)
        
        return {
            "success": True,
            "message": "Authority Curator status granted",
            "since": state.authority_curator_since,
        }
    
    def check_authority_curator_active(self, user_id: str) -> Dict[str, Any]:
        """Check if Authority Curator status is still active."""
        state = self.get_state(user_id)
        
        if not state.authority_curator:
            return {"active": False, "reason": "Not an Authority Curator"}
        
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
        
        return {"active": True, "since": state.authority_curator_since}
    
    def update_authority_curator_activity(self, user_id: str):
        """Update last active timestamp for Authority Curator."""
        state = self.get_state(user_id)
        if state.authority_curator:
            state.authority_last_active = datetime.utcnow()
            self._save_state(state)
        
        # Also update lifetime stats
        state.lifetime_posts_read = state.posts_read
        state.lifetime_deep_reads = max(state.lifetime_deep_reads, state.deep_reads)
        self._save_state(state)
    
    def record_path_accepted(self, user_id: str, path_id: str) -> Dict[str, Any]:
        """Record when a Featured Curator path is accepted."""
        state = self.get_state(user_id)
        
        # Update Featured Curator status if first path
        if not state.featured_curator:
            state.featured_curator = True
            state.featured_curator_since = datetime.utcnow()
            state.featured_path_id = path_id
            state.featured_path_url = f"/paths/{user_id}"
        
        state.featured_paths_count += 1
        
        # Check for Authority eligibility
        triggered = []
        if not state.authority_eligible:
            eligibility = self.check_authority_curator_eligibility(user_id)
            if eligibility["eligible"]:
                state.authority_eligible = True
                state.authority_eligible_at = datetime.utcnow()
                triggered.append("authority_eligible")
        
        self._save_state(state)
        
        return {
            "paths_count": state.featured_paths_count,
            "authority_eligible": state.authority_eligible,
            "triggered": triggered,
        }
    
    def record_path_follow(self, curator_user_id: str) -> Dict[str, Any]:
        """Record when someone follows a Curator's path."""
        state = self.get_state(curator_user_id)
        
        state.total_path_follows += 1
        
        # Check for Authority eligibility
        triggered = []
        if state.featured_curator and not state.authority_eligible:
            eligibility = self.check_authority_curator_eligibility(curator_user_id)
            if eligibility["eligible"]:
                state.authority_eligible = True
                state.authority_eligible_at = datetime.utcnow()
                triggered.append("authority_eligible")
        
        self._save_state(state)
        
        return {
            "total_follows": state.total_path_follows,
            "authority_eligible": state.authority_eligible,
            "triggered": triggered,
        }
    
    def get_authority_curator_progress(self, user_id: str) -> Dict[str, Any]:
        """Get progress toward Authority Curator for dashboard."""
        state = self.get_state(user_id)
        eligibility = self.check_authority_curator_eligibility(user_id)
        
        return {
            "is_featured_curator": state.featured_curator,
            "is_authority_curator": state.authority_curator,
            "authority_eligible": state.authority_eligible,
            "progress": eligibility.get("progress", {}),
            "percent_complete": eligibility.get("percent_complete", 0),
        }
    
    def get_curator_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all earned badges for a Curator."""
        state = self.get_state(user_id)
        badges = []
        
        # Authority Curator (highest tier - show first)
        if state.authority_curator:
            badges.append({
                "type": "authority_curator",
                "name": "Authority Curator",
                "icon": "👑",
                "since": state.authority_curator_since,
                "tier": "authority",
            })
        
        # Featured Curator
        if state.featured_curator:
            badges.append({
                "type": "featured_curator",
                "name": "Featured Curator",
                "icon": "⭐",
                "since": state.featured_curator_since,
                "url": state.featured_path_url,
                "count": state.featured_paths_count,
            })
        
        return badges


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_tracker: Optional[CuratorMilestoneTracker] = None


def get_curator_tracker() -> CuratorMilestoneTracker:
    global _tracker
    if _tracker is None:
        _tracker = CuratorMilestoneTracker()
    return _tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tracker = CuratorMilestoneTracker()
    
    print("=== Curator Milestone Tracker Demo ===\n")
    
    # Start window
    state = tracker.start_window("demo_curator")
    print(f"Window started. Ends: {state.window_end}")
    
    # Record some reads
    for i, profile in enumerate(["ASSERTIVE-OPEN", "POETIC-CLOSED", "MINIMAL-BALANCED"]):
        result = tracker.record_post_read("demo_curator", profile, is_deep_read=(i == 0))
        print(f"Read {profile}: {result['triggered']}")
    
    # Check progress
    progress = tracker.get_progress("demo_curator")
    print(f"\nProgress: {progress['percent_complete']}% complete")
    print(f"Days remaining: {progress['days_remaining']}")
    
    # Next action
    next_action = tracker.get_next_action("demo_curator")
    print(f"\nNext: {next_action['message']}")
