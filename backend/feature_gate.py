#!/usr/bin/env python3
"""
LNCP Feature Gating System
Version: 1.0.0

Controls access to features based on user tier (free, trial, pro).
Works with both file-based storage (development) and PostgreSQL (production).

Usage:
    from feature_gate import FeatureGate, require_feature
    
    gate = FeatureGate()
    
    # Check access
    if gate.can_access("save_results", user_id="123"):
        # Allow feature
        
    # Or use decorator
    @require_feature("detailed_insights")
    def get_insights(user_id: str):
        ...
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# Enums and Types
# ═══════════════════════════════════════════════════════════════════════════

class Tier(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"                       # Writer track - Paid Tier 1
    CURATOR = "curator"               # Reader track - Paid Tier 1
    FEATURED_WRITER = "featured_writer"   # Writer track - Paid Tier 2
    FEATURED_CURATOR = "featured_curator" # Reader track - Paid Tier 2
    AUTHORITY_WRITER = "authority_writer" # Writer track - Paid Tier 3
    AUTHORITY_CURATOR = "authority_curator" # Reader track - Paid Tier 3


# Tier hierarchy levels
TIER_LEVELS = {
    Tier.FREE: 0,
    Tier.TRIAL: 0,
    Tier.PRO: 1,
    Tier.CURATOR: 1,
    Tier.FEATURED_WRITER: 2,
    Tier.FEATURED_CURATOR: 2,
    Tier.AUTHORITY_WRITER: 3,
    Tier.AUTHORITY_CURATOR: 3,
}


class Addon(str, Enum):
    """Available add-on features."""
    VOICE_STYLE = "voice_style"  # Voice + Style analysis (cross-track)


@dataclass
class FeatureFlag:
    """Definition of a feature flag."""
    key: str
    name: str
    description: str
    # Base tier access
    tier_free: bool
    tier_trial: bool
    tier_pro: bool
    tier_curator: bool = False
    tier_featured_writer: bool = False
    tier_featured_curator: bool = False
    tier_authority_writer: bool = False
    tier_authority_curator: bool = False
    # Addon access (if True, having this addon grants access regardless of tier)
    addon_voice_style: bool = False
    # Tier OR addon mode (if True, user needs tier OR addon, not both)
    tier_or_addon: bool = False
    is_active: bool = True

    def check_access(self, tier: Tier, addons: List[str] = None) -> bool:
        """Check if a tier/addon combination grants access."""
        addons = addons or []
        
        # Check tier access
        tier_access = {
            Tier.FREE: self.tier_free,
            Tier.TRIAL: self.tier_trial,
            Tier.PRO: self.tier_pro,
            Tier.CURATOR: self.tier_curator,
            Tier.FEATURED_WRITER: self.tier_featured_writer,
            Tier.FEATURED_CURATOR: self.tier_featured_curator,
            Tier.AUTHORITY_WRITER: self.tier_authority_writer,
            Tier.AUTHORITY_CURATOR: self.tier_authority_curator,
        }
        has_tier = tier_access.get(tier, False)
        
        # Check addon access
        has_addon = False
        if self.addon_voice_style and Addon.VOICE_STYLE.value in addons:
            has_addon = True
        
        # Evaluate based on tier_or_addon mode
        if self.tier_or_addon:
            return has_tier or has_addon
        else:
            # Both must be satisfied if both are required
            if self.addon_voice_style and not has_addon:
                return False
            return has_tier


@dataclass
class UserTier:
    """User's effective tier information."""
    user_id: str
    base_tier: Tier
    effective_tier: Tier
    addons: List[str] = None
    trial_ends_at: Optional[datetime] = None
    trial_analyses: int = 0
    
    def __post_init__(self):
        if self.addons is None:
            self.addons = []
    
    def has_addon(self, addon: Addon) -> bool:
        """Check if user has a specific addon."""
        return addon.value in self.addons
    
    @property
    def tier_level(self) -> int:
        """Get numeric tier level for comparisons."""
        return TIER_LEVELS.get(self.effective_tier, 0)


@dataclass
class FeatureAccessResult:
    """Result of a feature access check."""
    allowed: bool
    feature: str
    tier: Tier
    reason: str


# ═══════════════════════════════════════════════════════════════════════════
# Default Feature Definitions
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_FEATURES: List[FeatureFlag] = [
    # === UNIVERSAL FEATURES (all tiers) ===
    FeatureFlag(
        key="basic_analysis",
        name="Basic Analysis",
        description="Run LNCP analysis and see profile",
        tier_free=True, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="writer_matches",
        name="Writer Matches",
        description="See famous writer recommendations",
        tier_free=True, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    
    # === PAID TIER FEATURES (Pro/Curator+) ===
    FeatureFlag(
        key="save_results",
        name="Save Results",
        description="Save analysis results to account",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="profile_history",
        name="Profile History",
        description="View past analyses and compare",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="evolution_tracking",
        name="Evolution Tracking",
        description="See how voice changes over time",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="analytics",
        name="Analytics",
        description="View writing and reading analytics",
        tier_free=False, tier_trial=False, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="unlimited_analyses",
        name="Unlimited Analyses",
        description="No daily analysis limit",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="extension_sync",
        name="Extension Sync",
        description="Sync with browser extension",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="compare_profiles",
        name="Compare Profiles",
        description="Compare multiple analyses side by side",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    
    # === VOICE + STYLE ADDON FEATURES ===
    FeatureFlag(
        key="voice_profile",
        name="Voice Profile",
        description="Deep voice analysis and insights",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=False, tier_featured_curator=False,
        tier_authority_writer=False, tier_authority_curator=False,
        addon_voice_style=True,
    ),
    FeatureFlag(
        key="voice_evolution",
        name="Voice Evolution",
        description="Track how your voice changes over time",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=False, tier_featured_curator=False,
        tier_authority_writer=False, tier_authority_curator=False,
        addon_voice_style=True,
    ),
    
    # === CURATOR TRACK FEATURES ===
    FeatureFlag(
        key="create_paths",
        name="Create Reading Paths",
        description="Create and manage reading paths",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=True, tier_featured_writer=False, tier_featured_curator=True,
        tier_authority_writer=False, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    FeatureFlag(
        key="path_followers",
        name="Path Followers",
        description="View and manage path followers",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=True, tier_featured_writer=False, tier_featured_curator=True,
        tier_authority_writer=False, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    
    # === FEATURED TIER FEATURES ===
    FeatureFlag(
        key="featured_submission",
        name="Featured Submission",
        description="Submit writing for featured section",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    FeatureFlag(
        key="featured_page",
        name="Featured Page",
        description="Access to featured content curation",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=False, tier_featured_curator=True,
        tier_authority_writer=False, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    
    # === AUTHORITY TIER FEATURES ===
    FeatureFlag(
        key="authority_hub",
        name="Authority Hub",
        description="Access to authority dashboard and metrics",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    FeatureFlag(
        key="leaderboard",
        name="Leaderboard",
        description="View global and regional leaderboards",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    FeatureFlag(
        key="impact_stats",
        name="Impact Stats",
        description="View your community impact metrics",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
        addon_voice_style=True, tier_or_addon=True,
    ),
    
    # === PRO FEATURES ===
    FeatureFlag(
        key="detailed_insights",
        name="Detailed Insights",
        description="Deep dive into profile characteristics",
        tier_free=False, tier_trial=False, tier_pro=True,
        tier_curator=False, tier_featured_writer=True, tier_featured_curator=False,
        tier_authority_writer=True, tier_authority_curator=False,
    ),
    FeatureFlag(
        key="export_results",
        name="Export Results",
        description="Download results as PDF/JSON",
        tier_free=False, tier_trial=False, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="api_access",
        name="API Access",
        description="Access LNCP via API",
        tier_free=False, tier_trial=False, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    
    # === BROWSER EXTENSION FEATURES ===
    FeatureFlag(
        key="extension_sync",
        name="Extension Sync",
        description="Sync browser extension with web app",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="extension_save",
        name="Extension Save",
        description="Save analysis results from extension",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="extension_history",
        name="Extension History",
        description="View analysis history in extension",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="extension_voice_insights",
        name="Extension Voice Insights",
        description="View voice insights in extension popup",
        tier_free=False, tier_trial=False, tier_pro=False,
        tier_curator=False, tier_featured_writer=False, tier_featured_curator=False,
        tier_authority_writer=False, tier_authority_curator=False,
        addon_voice_style=True,
    ),
    FeatureFlag(
        key="extension_compare",
        name="Extension Compare",
        description="Compare profiles from extension",
        tier_free=False, tier_trial=True, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
    FeatureFlag(
        key="extension_export",
        name="Extension Export",
        description="Export results from extension",
        tier_free=False, tier_trial=False, tier_pro=True,
        tier_curator=True, tier_featured_writer=True, tier_featured_curator=True,
        tier_authority_writer=True, tier_authority_curator=True,
    ),
]

# Daily analysis limits by tier
DAILY_LIMITS = {
    Tier.FREE: 5,
    Tier.TRIAL: 100,
    Tier.PRO: 1000,
    Tier.CURATOR: 1000,
    Tier.FEATURED_WRITER: 1000,
    Tier.FEATURED_CURATOR: 1000,
    Tier.AUTHORITY_WRITER: 10000,
    Tier.AUTHORITY_CURATOR: 10000,
}


# ═══════════════════════════════════════════════════════════════════════════
# Feature Gate
# ═══════════════════════════════════════════════════════════════════════════

class FeatureGate:
    """
    Controls feature access based on user tier.
    
    Uses file-based storage for development, can be extended
    to use PostgreSQL via the check_feature_access() function.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the feature gate.
        
        Args:
            storage_dir: Directory for file-based user data. Defaults to ./users/
        """
        self.storage_dir = storage_dir or Path(__file__).parent / "users"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.users_file = self.storage_dir / "users.json"
        self.trials_file = self.storage_dir / "trials.json"
        self.usage_file = self.storage_dir / "usage.json"
        
        # Load feature definitions
        self.features: Dict[str, FeatureFlag] = {
            f.key: f for f in DEFAULT_FEATURES
        }
        
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure storage files exist."""
        if not self.users_file.exists():
            self._write_json(self.users_file, {"users": {}})
        if not self.trials_file.exists():
            self._write_json(self.trials_file, {"trials": {}})
        if not self.usage_file.exists():
            self._write_json(self.usage_file, {"usage": {}})
    
    def _read_json(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _write_json(self, path: Path, data: Dict[str, Any]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    # ─────────────────────────────────────────────────────────────────────────
    # User Tier Management
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_user_tier(self, user_id: str) -> UserTier:
        """
        Get a user's effective tier, accounting for active trials.
        """
        users = self._read_json(self.users_file).get("users", {})
        trials = self._read_json(self.trials_file).get("trials", {})
        
        user = users.get(user_id, {})
        trial = trials.get(user_id, {})
        
        # Base tier from subscription
        base_tier = Tier(user.get("subscription_tier", "free"))
        
        # Check for active trial
        effective_tier = base_tier
        trial_ends_at = None
        trial_analyses = 0
        
        if base_tier == Tier.FREE and trial:
            trial_end_str = trial.get("ends_at")
            if trial_end_str:
                trial_ends_at = datetime.fromisoformat(trial_end_str.replace("Z", "+00:00"))
                if trial_ends_at > datetime.now(trial_ends_at.tzinfo):
                    effective_tier = Tier.TRIAL
                    trial_analyses = trial.get("analyses_count", 0)
        
        return UserTier(
            user_id=user_id,
            base_tier=base_tier,
            effective_tier=effective_tier,
            trial_ends_at=trial_ends_at,
            trial_analyses=trial_analyses,
        )
    
    def set_user_tier(self, user_id: str, tier: Tier):
        """Set a user's subscription tier."""
        data = self._read_json(self.users_file)
        if user_id not in data["users"]:
            data["users"][user_id] = {}
        data["users"][user_id]["subscription_tier"] = tier.value
        self._write_json(self.users_file, data)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Trial Management
    # ─────────────────────────────────────────────────────────────────────────
    
    def start_trial(self, user_id: str) -> bool:
        """
        Start a 7-day trial for a user.
        
        Returns:
            True if trial started, False if user already had one
        """
        data = self._read_json(self.trials_file)
        trials = data.get("trials", {})
        
        if user_id in trials:
            # Already had trial
            return False
        
        now = datetime.utcnow()
        trials[user_id] = {
            "started_at": now.isoformat() + "Z",
            "ends_at": (now + timedelta(days=7)).isoformat() + "Z",
            "status": "active",
            "analyses_count": 0,
            "features_used": [],
        }
        
        data["trials"] = trials
        self._write_json(self.trials_file, data)
        return True
    
    def get_trial_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get trial status for a user."""
        trials = self._read_json(self.trials_file).get("trials", {})
        trial = trials.get(user_id)
        
        if not trial:
            return None
        
        # Calculate status
        ends_at = datetime.fromisoformat(trial["ends_at"].replace("Z", "+00:00"))
        now = datetime.now(ends_at.tzinfo)
        
        if trial["status"] == "converted":
            status = "converted"
            days_remaining = 0
        elif now > ends_at:
            status = "expired"
            days_remaining = 0
        else:
            status = "active"
            days_remaining = (ends_at - now).days
        
        return {
            "user_id": user_id,
            "status": status,
            "started_at": trial["started_at"],
            "ends_at": trial["ends_at"],
            "days_remaining": days_remaining,
            "analyses_count": trial.get("analyses_count", 0),
            "features_used": trial.get("features_used", []),
        }
    
    def record_trial_usage(self, user_id: str, feature: str):
        """Record feature usage during trial."""
        data = self._read_json(self.trials_file)
        trial = data.get("trials", {}).get(user_id)
        
        if trial and trial.get("status") == "active":
            trial["analyses_count"] = trial.get("analyses_count", 0) + 1
            features = set(trial.get("features_used", []))
            features.add(feature)
            trial["features_used"] = list(features)
            self._write_json(self.trials_file, data)
    
    def convert_trial(self, user_id: str, price: float = 4.99):
        """Mark trial as converted to pro."""
        data = self._read_json(self.trials_file)
        trial = data.get("trials", {}).get(user_id)
        
        if trial:
            trial["status"] = "converted"
            trial["conversion_date"] = datetime.utcnow().isoformat() + "Z"
            trial["conversion_price"] = price
            self._write_json(self.trials_file, data)
        
        # Upgrade user tier
        self.set_user_tier(user_id, Tier.PRO)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Feature Access
    # ─────────────────────────────────────────────────────────────────────────
    
    def can_access(
        self,
        feature: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> FeatureAccessResult:
        """
        Check if a user/session can access a feature.
        
        Args:
            feature: Feature key to check
            user_id: User ID (if authenticated)
            session_id: Session ID (if anonymous)
            
        Returns:
            FeatureAccessResult with allowed status and reason
        """
        # Get feature definition
        flag = self.features.get(feature)
        if not flag:
            return FeatureAccessResult(
                allowed=False,
                feature=feature,
                tier=Tier.FREE,
                reason=f"Unknown feature: {feature}",
            )
        
        if not flag.is_active:
            return FeatureAccessResult(
                allowed=False,
                feature=feature,
                tier=Tier.FREE,
                reason="Feature is disabled",
            )
        
        # Anonymous users = free tier
        if not user_id:
            allowed = flag.tier_free
            return FeatureAccessResult(
                allowed=allowed,
                feature=feature,
                tier=Tier.FREE,
                reason="Allowed for free tier" if allowed else "Requires signup",
            )
        
        # Get user's effective tier
        user_tier = self.get_user_tier(user_id)
        tier = user_tier.effective_tier
        
        # Check tier access
        if tier == Tier.PRO:
            allowed = flag.tier_pro
        elif tier == Tier.TRIAL:
            allowed = flag.tier_trial
        else:
            allowed = flag.tier_free
        
        if allowed:
            reason = f"Allowed for {tier.value} tier"
            # Record trial usage if applicable
            if tier == Tier.TRIAL:
                self.record_trial_usage(user_id, feature)
        else:
            if tier == Tier.FREE and flag.tier_trial:
                reason = "Start free trial to unlock"
            elif tier in (Tier.FREE, Tier.TRIAL) and flag.tier_pro:
                reason = "Upgrade to Pro to unlock"
            else:
                reason = f"Not available for {tier.value} tier"
        
        return FeatureAccessResult(
            allowed=allowed,
            feature=feature,
            tier=tier,
            reason=reason,
        )
    
    def get_all_features(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all features with access status for a user.
        
        Useful for displaying feature comparison / upgrade prompts.
        """
        tier = Tier.FREE
        if user_id:
            tier = self.get_user_tier(user_id).effective_tier
        
        result = []
        for flag in self.features.values():
            access = self.can_access(flag.key, user_id)
            result.append({
                "key": flag.key,
                "name": flag.name,
                "description": flag.description,
                "allowed": access.allowed,
                "reason": access.reason,
                "free": flag.tier_free,
                "trial": flag.tier_trial,
                "pro": flag.tier_pro,
            })
        
        return result
    
    # ─────────────────────────────────────────────────────────────────────────
    # Usage Limits
    # ─────────────────────────────────────────────────────────────────────────
    
    def check_daily_limit(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check if user/session has reached daily analysis limit.
        
        Returns:
            Dict with allowed, used, limit, remaining
        """
        identifier = user_id or session_id or "anonymous"
        
        # Get tier
        if user_id:
            tier = self.get_user_tier(user_id).effective_tier
        else:
            tier = Tier.FREE
        
        limit = DAILY_LIMITS.get(tier, 5)
        
        # Get today's usage
        usage = self._read_json(self.usage_file).get("usage", {})
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        user_usage = usage.get(identifier, {})
        today_count = user_usage.get(today, 0)
        
        return {
            "allowed": today_count < limit,
            "used": today_count,
            "limit": limit,
            "remaining": max(0, limit - today_count),
            "tier": tier.value,
            "resets_at": f"{today}T23:59:59Z",
        }
    
    def record_analysis(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """Record an analysis for usage tracking."""
        identifier = user_id or session_id or "anonymous"
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        data = self._read_json(self.usage_file)
        usage = data.get("usage", {})
        
        if identifier not in usage:
            usage[identifier] = {}
        
        usage[identifier][today] = usage[identifier].get(today, 0) + 1
        
        # Clean up old entries (keep last 7 days)
        cutoff = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        usage[identifier] = {
            k: v for k, v in usage[identifier].items()
            if k >= cutoff
        }
        
        data["usage"] = usage
        self._write_json(self.usage_file, data)


# ═══════════════════════════════════════════════════════════════════════════
# Decorator
# ═══════════════════════════════════════════════════════════════════════════

_gate: Optional[FeatureGate] = None


def get_feature_gate() -> FeatureGate:
    """Get or create the global feature gate instance."""
    global _gate
    if _gate is None:
        _gate = FeatureGate()
    return _gate


def require_feature(feature: str):
    """
    Decorator to require a feature for a function.
    
    The decorated function must have user_id as first argument.
    Raises PermissionError if feature access is denied.
    
    Usage:
        @require_feature("detailed_insights")
        def get_insights(user_id: str, profile: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(user_id: str, *args, **kwargs):
            gate = get_feature_gate()
            result = gate.can_access(feature, user_id)
            
            if not result.allowed:
                raise PermissionError(f"Feature '{feature}' not allowed: {result.reason}")
            
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Feature Gate Demo")
    print("=" * 60)
    
    gate = FeatureGate()
    
    # Create test users
    gate.set_user_tier("user-free", Tier.FREE)
    gate.set_user_tier("user-pro", Tier.PRO)
    
    # Start trial for one user
    print("\nStarting trial for user-trial...")
    gate.start_trial("user-trial")
    
    # Check features for each tier
    test_features = ["basic_analysis", "save_results", "detailed_insights"]
    test_users = [None, "user-free", "user-trial", "user-pro"]
    
    print("\n" + "=" * 60)
    print("Feature Access Matrix:")
    print("=" * 60)
    print(f"{'Feature':<20} {'Anonymous':<12} {'Free':<12} {'Trial':<12} {'Pro':<12}")
    print("-" * 68)
    
    for feature in test_features:
        row = [feature]
        for user_id in test_users:
            result = gate.can_access(feature, user_id)
            row.append("✅" if result.allowed else "❌")
        print(f"{row[0]:<20} {row[1]:<12} {row[2]:<12} {row[3]:<12} {row[4]:<12}")
    
    # Check trial status
    print("\n" + "=" * 60)
    print("Trial Status:")
    print("=" * 60)
    status = gate.get_trial_status("user-trial")
    if status:
        print(f"  Status: {status['status']}")
        print(f"  Days remaining: {status['days_remaining']}")
        print(f"  Analyses: {status['analyses_count']}")
    
    # Check daily limits
    print("\n" + "=" * 60)
    print("Daily Limits:")
    print("=" * 60)
    for user_id in ["user-free", "user-trial", "user-pro"]:
        limits = gate.check_daily_limit(user_id)
        print(f"  {user_id}: {limits['remaining']}/{limits['limit']} remaining ({limits['tier']})")
    
    print("\n✅ Feature Gate working")
