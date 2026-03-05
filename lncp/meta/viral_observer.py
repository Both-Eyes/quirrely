#!/usr/bin/env python3
"""
LNCP META: VIRAL OBSERVER v1.0.0
Tracks organic sharing, word-of-mouth loops, and viral coefficient.

This observer monitors:
- Share card generation and click-through rates
- Referred user signups and their conversion quality
- Viral coefficient (K-factor) per cohort
- Blog post shares and inbound traffic
- UTM parameter performance
- LinkedIn / social link effectiveness

It provides:
- Real-time K-factor estimate
- Top-performing share surfaces
- Referral chain quality scoring
- Optimisation proposals for viral loops
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# VIRAL ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class ShareSurface(str, Enum):
    """Where sharing occurs."""
    WEB_SHARE_API   = "web_share_api"     # Mobile native share sheet
    CLIPBOARD       = "clipboard"          # Copy-to-clipboard fallback
    BLOG_CTA        = "blog_cta"           # CTA in blog post
    TWITTER         = "twitter"
    LINKEDIN        = "linkedin"
    DIRECT_LINK     = "direct_link"        # User copies URL manually


class ShareOutcome(str, Enum):
    """What happened to the shared link."""
    IGNORED          = "ignored"           # No click recorded
    CLICKED          = "clicked"           # Link opened
    ANALYSIS_RUN     = "analysis_run"      # Referred user ran analysis
    SIGNUP           = "signup"            # Referred user signed up
    PRO_CONVERSION   = "pro_conversion"    # Referred user went Pro


class UTMSource(str, Enum):
    """UTM source categories."""
    BLOG     = "blog"
    SHARE    = "share"
    REFERRAL = "referral"
    DIRECT   = "direct"
    UNKNOWN  = "unknown"


# ═══════════════════════════════════════════════════════════════════════════
# VIRAL METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ShareEvent:
    """A single share action."""
    share_id: str
    user_id: str
    surface: ShareSurface
    ts: datetime
    profile_shared: Optional[str] = None   # e.g. "ASSERTIVE"
    utm_source: Optional[str] = None
    outcome: ShareOutcome = ShareOutcome.IGNORED
    referral_signups: int = 0
    referral_conversions: int = 0


@dataclass
class ViralMetrics:
    """Viral performance metrics."""
    k_factor: float              # K = shares_per_user × conversion_rate
    shares_total: int
    referred_signups: int
    referred_pro_conversions: int
    top_surface: str
    blog_referral_traffic: int
    health_score: float


# ═══════════════════════════════════════════════════════════════════════════
# VIRAL OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class ViralObserver:
    """
    Observes and analyses Quirrely's viral and referral mechanics.
    Registered with MetaOrchestrator as 'viral_observer'.
    """

    OBSERVER_ID = "viral_observer"
    VERSION     = "1.0.0"

    # Target K-factor benchmarks
    K_FACTOR_TARGET    = 0.35   # Each user brings 0.35 new users (sustainable growth)
    K_FACTOR_VIRAL     = 0.80   # K > 0.8 = true viral growth
    SHARE_RATE_TARGET  = 0.25   # 25% of users share at least once

    def __init__(self):
        self._shares: List[ShareEvent] = []
        self._surface_counts: Dict[str, int] = {s.value: 0 for s in ShareSurface}
        self._outcome_counts: Dict[str, int] = {o.value: 0 for o in ShareOutcome}
        self._unique_sharers: set = set()
        self._unique_users: set = set()
        self._blog_referrals: int = 0
        self._utm_tracking: Dict[str, int] = {}
        self._proposals: List[Dict[str, Any]] = []

    # ── PUBLIC INTERFACE ────────────────────────────────────────────────────

    def on_share(self, user_id: str, surface: ShareSurface,
                 profile: Optional[str] = None,
                 utm_source: Optional[str] = None) -> str:
        """Record a share event. Returns share_id for tracking."""
        import uuid
        share_id = str(uuid.uuid4())
        event = ShareEvent(
            share_id=share_id,
            user_id=user_id,
            surface=surface,
            ts=datetime.utcnow(),
            profile_shared=profile,
            utm_source=utm_source,
        )
        self._shares.append(event)
        self._surface_counts[surface.value] = self._surface_counts.get(surface.value, 0) + 1
        self._unique_sharers.add(user_id)
        return share_id

    def on_referral_visit(self, share_id: str, referred_user_id: str) -> None:
        """Record when a shared link results in a visit."""
        self._resolve_outcome(share_id, ShareOutcome.CLICKED, referred_user_id)

    def on_referral_signup(self, share_id: str, referred_user_id: str) -> Dict[str, Any]:
        """
        Record when a referred visit converts to signup.
        Returns a signal for MetaOrchestrator.
        """
        self._resolve_outcome(share_id, ShareOutcome.SIGNUP, referred_user_id)
        return {
            "type":          "referral_signup",
            "share_id":      share_id,
            "referred_user": referred_user_id,
            "k_factor":      self.get_k_factor(),
            "priority":      "high",
            "ts":            datetime.utcnow().isoformat(),
        }

    def on_referral_conversion(self, share_id: str, referred_user_id: str) -> Dict[str, Any]:
        """Record when a referred signup converts to paid."""
        self._resolve_outcome(share_id, ShareOutcome.PRO_CONVERSION, referred_user_id)
        return {
            "type":          "referral_paid_conversion",
            "share_id":      share_id,
            "referred_user": referred_user_id,
            "priority":      "urgent",
            "ts":            datetime.utcnow().isoformat(),
        }

    def on_blog_referral(self, utm_source: str, page: str) -> None:
        """Record inbound traffic from blog CTAs."""
        self._blog_referrals += 1
        key = f"{utm_source}:{page}"
        self._utm_tracking[key] = self._utm_tracking.get(key, 0) + 1

    def on_user_registered(self, user_id: str) -> None:
        """Track total user base size for K-factor denominator."""
        self._unique_users.add(user_id)

    def get_k_factor(self) -> float:
        """
        K = (shares / users) × (referred_signups / shares)
        = referred_signups / users
        """
        users = max(len(self._unique_users), 1)
        referral_signups = self._outcome_counts.get(ShareOutcome.SIGNUP.value, 0)
        return round(referral_signups / users, 4)

    def get_metrics(self) -> ViralMetrics:
        """Return full viral metrics snapshot."""
        top_surface = max(self._surface_counts, key=self._surface_counts.get,
                          default=ShareSurface.CLIPBOARD.value)
        total_users = max(len(self._unique_users), 1)
        share_rate = len(self._unique_sharers) / total_users

        return ViralMetrics(
            k_factor=self.get_k_factor(),
            shares_total=len(self._shares),
            referred_signups=self._outcome_counts.get(ShareOutcome.SIGNUP.value, 0),
            referred_pro_conversions=self._outcome_counts.get(ShareOutcome.PRO_CONVERSION.value, 0),
            top_surface=top_surface,
            blog_referral_traffic=self._blog_referrals,
            health_score=self._compute_health(share_rate),
        )

    def get_status(self) -> Dict[str, Any]:
        """Status summary for admin dashboard."""
        m = self.get_metrics()
        return {
            "observer":           self.OBSERVER_ID,
            "version":            self.VERSION,
            "k_factor":           m.k_factor,
            "k_factor_target":    self.K_FACTOR_TARGET,
            "shares_total":       m.shares_total,
            "referred_signups":   m.referred_signups,
            "top_surface":        m.top_surface,
            "blog_referrals":     m.blog_referral_traffic,
            "health_score":       m.health_score,
            "proposals_pending":  len(self._proposals),
        }

    def get_proposals(self) -> List[Dict[str, Any]]:
        return list(self._proposals)

    # ── PRIVATE ─────────────────────────────────────────────────────────────

    def _resolve_outcome(self, share_id: str, outcome: ShareOutcome,
                         referred_user_id: str) -> None:
        for share in self._shares:
            if share.share_id == share_id:
                # Escalate outcome only (SIGNUP > CLICKED > IGNORED)
                order = [ShareOutcome.IGNORED, ShareOutcome.CLICKED,
                         ShareOutcome.ANALYSIS_RUN, ShareOutcome.SIGNUP,
                         ShareOutcome.PRO_CONVERSION]
                if order.index(outcome) > order.index(share.outcome):
                    share.outcome = outcome
                    self._outcome_counts[outcome.value] = (
                        self._outcome_counts.get(outcome.value, 0) + 1
                    )
                break

    def _compute_health(self, share_rate: float) -> float:
        """0–100 health score."""
        k = self.get_k_factor()
        k_score    = min(k / self.K_FACTOR_TARGET * 50, 50)
        share_score = min(share_rate / self.SHARE_RATE_TARGET * 50, 50)
        score = k_score + share_score

        # Generate proposals if below par
        if k < self.K_FACTOR_TARGET * 0.5:
            self._proposals.append({
                "type":      "low_k_factor",
                "current":   k,
                "target":    self.K_FACTOR_TARGET,
                "priority":  "high",
                "action":    "Increase share card visibility on analysis result page",
                "ts":        datetime.utcnow().isoformat(),
            })

        return round(score, 1)


# Singleton for MetaOrchestrator registration
viral_observer = ViralObserver()
