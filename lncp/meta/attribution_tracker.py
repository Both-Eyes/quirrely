#!/usr/bin/env python3
"""
LNCP META: ATTRIBUTION TRACKER v4.2
Tracks cross-domain attribution from Blog → App → Revenue.

Simple attribution model:
- Track which blog page led to signup (UTM or referrer)
- Track which profile type converts best
- Track time from blog visit to signup
- Track time from signup to subscription

This enables understanding the full funnel impact of changes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics


# ═══════════════════════════════════════════════════════════════════════════
# ATTRIBUTION EVENTS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BlogVisit:
    """A tracked blog visit."""
    visitor_id: str
    page_path: str
    timestamp: datetime
    
    # Source tracking
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    referrer: Optional[str] = None
    
    # Content metadata
    profile_shown: Optional[str] = None  # If profile-related content
    cta_shown: Optional[str] = None
    cta_clicked: bool = False


@dataclass
class AppSignup:
    """An app signup event."""
    user_id: str
    visitor_id: Optional[str]  # Links to blog visitor if same session
    timestamp: datetime
    
    # Attribution
    source_page: Optional[str] = None
    source_profile: Optional[str] = None
    source_cta: Optional[str] = None
    
    # User data
    detected_profile: Optional[str] = None  # Profile detected during onboarding


@dataclass
class Subscription:
    """A subscription event."""
    user_id: str
    timestamp: datetime
    plan: str
    mrr: float
    
    # Attribution chain
    signup_date: Optional[datetime] = None
    source_page: Optional[str] = None
    source_profile: Optional[str] = None


@dataclass
class AttributionChain:
    """Complete attribution from blog to revenue."""
    # Identity
    user_id: str
    visitor_id: Optional[str]
    
    # Journey
    first_blog_visit: Optional[BlogVisit] = None
    signup: Optional[AppSignup] = None
    subscription: Optional[Subscription] = None
    
    # Timing
    visit_to_signup_hours: Optional[float] = None
    signup_to_subscription_hours: Optional[float] = None
    total_journey_hours: Optional[float] = None
    
    # Attribution
    attributed_page: Optional[str] = None
    attributed_profile: Optional[str] = None
    attributed_cta: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "attributed_page": self.attributed_page,
            "attributed_profile": self.attributed_profile,
            "visit_to_signup_hours": self.visit_to_signup_hours,
            "signup_to_subscription_hours": self.signup_to_subscription_hours,
            "converted": self.subscription is not None,
            "mrr": self.subscription.mrr if self.subscription else 0,
        }


# ═══════════════════════════════════════════════════════════════════════════
# ATTRIBUTION TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class AttributionTracker:
    """
    Tracks attribution across the Blog → App → Revenue funnel.
    
    This enables:
    - Understanding which blog content drives signups
    - Measuring which profiles convert best
    - Calculating cross-domain impact of changes
    """
    
    def __init__(self):
        # Event storage
        self.blog_visits: Dict[str, List[BlogVisit]] = {}  # visitor_id -> visits
        self.signups: Dict[str, AppSignup] = {}  # user_id -> signup
        self.subscriptions: Dict[str, Subscription] = {}  # user_id -> subscription
        
        # Attribution chains
        self.chains: Dict[str, AttributionChain] = {}  # user_id -> chain
        
        # Aggregates
        self.page_conversions: Dict[str, Dict] = {}  # page -> {visits, signups, subscriptions}
        self.profile_conversions: Dict[str, Dict] = {}  # profile -> {shown, signups, subscriptions}
        self.cta_conversions: Dict[str, Dict] = {}  # cta -> {shown, clicked, signups}
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT RECORDING
    # ─────────────────────────────────────────────────────────────────────
    
    def record_blog_visit(
        self,
        visitor_id: str,
        page_path: str,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        referrer: Optional[str] = None,
        profile_shown: Optional[str] = None,
        cta_shown: Optional[str] = None,
    ) -> BlogVisit:
        """Record a blog visit."""
        visit = BlogVisit(
            visitor_id=visitor_id,
            page_path=page_path,
            timestamp=datetime.utcnow(),
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            referrer=referrer,
            profile_shown=profile_shown,
            cta_shown=cta_shown,
        )
        
        if visitor_id not in self.blog_visits:
            self.blog_visits[visitor_id] = []
        self.blog_visits[visitor_id].append(visit)
        
        # Update page aggregates
        if page_path not in self.page_conversions:
            self.page_conversions[page_path] = {"visits": 0, "signups": 0, "subscriptions": 0, "mrr": 0}
        self.page_conversions[page_path]["visits"] += 1
        
        # Update profile aggregates
        if profile_shown:
            if profile_shown not in self.profile_conversions:
                self.profile_conversions[profile_shown] = {"shown": 0, "signups": 0, "subscriptions": 0, "mrr": 0}
            self.profile_conversions[profile_shown]["shown"] += 1
        
        # Update CTA aggregates
        if cta_shown:
            if cta_shown not in self.cta_conversions:
                self.cta_conversions[cta_shown] = {"shown": 0, "clicked": 0, "signups": 0}
            self.cta_conversions[cta_shown]["shown"] += 1
        
        return visit
    
    def record_cta_click(self, visitor_id: str, cta_id: str):
        """Record a CTA click."""
        # Update most recent visit
        if visitor_id in self.blog_visits and self.blog_visits[visitor_id]:
            last_visit = self.blog_visits[visitor_id][-1]
            last_visit.cta_clicked = True
        
        # Update CTA aggregates
        if cta_id in self.cta_conversions:
            self.cta_conversions[cta_id]["clicked"] += 1
    
    def record_signup(
        self,
        user_id: str,
        visitor_id: Optional[str] = None,
        detected_profile: Optional[str] = None,
    ) -> AppSignup:
        """Record an app signup with attribution."""
        # Find source from blog visits
        source_page = None
        source_profile = None
        source_cta = None
        
        if visitor_id and visitor_id in self.blog_visits:
            visits = self.blog_visits[visitor_id]
            if visits:
                # Use most recent visit as source
                last_visit = visits[-1]
                source_page = last_visit.page_path
                source_profile = last_visit.profile_shown
                source_cta = last_visit.cta_shown if last_visit.cta_clicked else None
        
        signup = AppSignup(
            user_id=user_id,
            visitor_id=visitor_id,
            timestamp=datetime.utcnow(),
            source_page=source_page,
            source_profile=source_profile,
            source_cta=source_cta,
            detected_profile=detected_profile,
        )
        
        self.signups[user_id] = signup
        
        # Update aggregates
        if source_page and source_page in self.page_conversions:
            self.page_conversions[source_page]["signups"] += 1
        
        if source_profile and source_profile in self.profile_conversions:
            self.profile_conversions[source_profile]["signups"] += 1
        
        if source_cta and source_cta in self.cta_conversions:
            self.cta_conversions[source_cta]["signups"] += 1
        
        # Build attribution chain
        self._build_chain(user_id, visitor_id, signup)
        
        return signup
    
    def record_subscription(
        self,
        user_id: str,
        plan: str,
        mrr: float,
    ) -> Optional[Subscription]:
        """Record a subscription with attribution."""
        signup = self.signups.get(user_id)
        
        subscription = Subscription(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            plan=plan,
            mrr=mrr,
            signup_date=signup.timestamp if signup else None,
            source_page=signup.source_page if signup else None,
            source_profile=signup.source_profile if signup else None,
        )
        
        self.subscriptions[user_id] = subscription
        
        # Update aggregates
        if signup:
            if signup.source_page and signup.source_page in self.page_conversions:
                self.page_conversions[signup.source_page]["subscriptions"] += 1
                self.page_conversions[signup.source_page]["mrr"] += mrr
            
            if signup.source_profile and signup.source_profile in self.profile_conversions:
                self.profile_conversions[signup.source_profile]["subscriptions"] += 1
                self.profile_conversions[signup.source_profile]["mrr"] += mrr
        
        # Update attribution chain
        self._update_chain_subscription(user_id, subscription)
        
        return subscription
    
    # ─────────────────────────────────────────────────────────────────────
    # ATTRIBUTION CHAIN BUILDING
    # ─────────────────────────────────────────────────────────────────────
    
    def _build_chain(
        self,
        user_id: str,
        visitor_id: Optional[str],
        signup: AppSignup,
    ):
        """Build attribution chain for a user."""
        chain = AttributionChain(
            user_id=user_id,
            visitor_id=visitor_id,
            signup=signup,
        )
        
        # Find first blog visit
        if visitor_id and visitor_id in self.blog_visits:
            visits = self.blog_visits[visitor_id]
            if visits:
                chain.first_blog_visit = visits[0]
                chain.visit_to_signup_hours = (
                    signup.timestamp - visits[0].timestamp
                ).total_seconds() / 3600
        
        # Set attribution
        chain.attributed_page = signup.source_page
        chain.attributed_profile = signup.source_profile
        chain.attributed_cta = signup.source_cta
        
        self.chains[user_id] = chain
    
    def _update_chain_subscription(
        self,
        user_id: str,
        subscription: Subscription,
    ):
        """Update attribution chain with subscription."""
        if user_id not in self.chains:
            return
        
        chain = self.chains[user_id]
        chain.subscription = subscription
        
        if chain.signup:
            chain.signup_to_subscription_hours = (
                subscription.timestamp - chain.signup.timestamp
            ).total_seconds() / 3600
        
        if chain.first_blog_visit:
            chain.total_journey_hours = (
                subscription.timestamp - chain.first_blog_visit.timestamp
            ).total_seconds() / 3600
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_page_performance(self) -> List[Dict]:
        """Get conversion performance by page."""
        results = []
        
        for page, stats in self.page_conversions.items():
            visits = stats["visits"]
            if visits == 0:
                continue
            
            results.append({
                "page": page,
                "visits": visits,
                "signups": stats["signups"],
                "signup_rate": stats["signups"] / visits,
                "subscriptions": stats["subscriptions"],
                "subscription_rate": stats["subscriptions"] / max(1, stats["signups"]),
                "mrr": stats["mrr"],
                "mrr_per_visit": stats["mrr"] / visits,
            })
        
        return sorted(results, key=lambda x: x["mrr"], reverse=True)
    
    def get_profile_performance(self) -> List[Dict]:
        """Get conversion performance by profile shown."""
        results = []
        
        for profile, stats in self.profile_conversions.items():
            shown = stats["shown"]
            if shown == 0:
                continue
            
            results.append({
                "profile": profile,
                "shown": shown,
                "signups": stats["signups"],
                "signup_rate": stats["signups"] / shown,
                "subscriptions": stats["subscriptions"],
                "mrr": stats["mrr"],
            })
        
        return sorted(results, key=lambda x: x["mrr"], reverse=True)
    
    def get_cta_performance(self) -> List[Dict]:
        """Get CTA performance."""
        results = []
        
        for cta, stats in self.cta_conversions.items():
            shown = stats["shown"]
            if shown == 0:
                continue
            
            results.append({
                "cta": cta,
                "shown": shown,
                "clicked": stats["clicked"],
                "click_rate": stats["clicked"] / shown,
                "signups": stats["signups"],
                "signup_rate": stats["signups"] / max(1, stats["clicked"]),
            })
        
        return sorted(results, key=lambda x: x["signups"], reverse=True)
    
    def get_journey_metrics(self) -> Dict:
        """Get average journey timing metrics."""
        chains_with_signup = [c for c in self.chains.values() if c.signup]
        chains_with_sub = [c for c in self.chains.values() if c.subscription]
        
        visit_to_signup_times = [
            c.visit_to_signup_hours for c in chains_with_signup
            if c.visit_to_signup_hours is not None
        ]
        
        signup_to_sub_times = [
            c.signup_to_subscription_hours for c in chains_with_sub
            if c.signup_to_subscription_hours is not None
        ]
        
        return {
            "total_chains": len(self.chains),
            "with_signup": len(chains_with_signup),
            "with_subscription": len(chains_with_sub),
            "conversion_rate": len(chains_with_sub) / max(1, len(chains_with_signup)),
            "avg_visit_to_signup_hours": statistics.mean(visit_to_signup_times) if visit_to_signup_times else None,
            "avg_signup_to_subscription_hours": statistics.mean(signup_to_sub_times) if signup_to_sub_times else None,
            "median_visit_to_signup_hours": statistics.median(visit_to_signup_times) if visit_to_signup_times else None,
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # IMPACT MEASUREMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def measure_page_impact(
        self,
        page_path: str,
        since: datetime,
    ) -> Dict:
        """Measure the revenue impact of a specific page."""
        # Get chains attributed to this page since the date
        attributed_chains = [
            c for c in self.chains.values()
            if c.attributed_page == page_path
            and c.signup
            and c.signup.timestamp >= since
        ]
        
        signups = len(attributed_chains)
        subscriptions = len([c for c in attributed_chains if c.subscription])
        mrr = sum(c.subscription.mrr for c in attributed_chains if c.subscription)
        
        return {
            "page": page_path,
            "period_start": since.isoformat(),
            "signups_attributed": signups,
            "subscriptions_attributed": subscriptions,
            "mrr_attributed": mrr,
            "conversion_rate": subscriptions / max(1, signups),
        }
    
    def measure_change_impact(
        self,
        page_path: str,
        change_date: datetime,
        days_before: int = 14,
        days_after: int = 14,
    ) -> Dict:
        """Measure the impact of a change to a page."""
        before_start = change_date - timedelta(days=days_before)
        after_end = change_date + timedelta(days=days_after)
        
        # Get chains in each period
        before_chains = [
            c for c in self.chains.values()
            if c.attributed_page == page_path
            and c.signup
            and before_start <= c.signup.timestamp < change_date
        ]
        
        after_chains = [
            c for c in self.chains.values()
            if c.attributed_page == page_path
            and c.signup
            and change_date <= c.signup.timestamp <= after_end
        ]
        
        before_signups = len(before_chains)
        after_signups = len(after_chains)
        
        before_subs = len([c for c in before_chains if c.subscription])
        after_subs = len([c for c in after_chains if c.subscription])
        
        before_mrr = sum(c.subscription.mrr for c in before_chains if c.subscription)
        after_mrr = sum(c.subscription.mrr for c in after_chains if c.subscription)
        
        return {
            "page": page_path,
            "change_date": change_date.isoformat(),
            "before": {
                "signups": before_signups,
                "subscriptions": before_subs,
                "mrr": before_mrr,
                "conversion_rate": before_subs / max(1, before_signups),
            },
            "after": {
                "signups": after_signups,
                "subscriptions": after_subs,
                "mrr": after_mrr,
                "conversion_rate": after_subs / max(1, after_signups),
            },
            "delta": {
                "signups": after_signups - before_signups,
                "subscriptions": after_subs - before_subs,
                "mrr": after_mrr - before_mrr,
            },
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # REPORTING
    # ─────────────────────────────────────────────────────────────────────
    
    def get_summary(self) -> Dict:
        """Get summary of attribution data."""
        total_mrr = sum(s.mrr for s in self.subscriptions.values())
        
        return {
            "visitors_tracked": len(self.blog_visits),
            "signups_tracked": len(self.signups),
            "subscriptions_tracked": len(self.subscriptions),
            "total_mrr_attributed": total_mrr,
            "pages_tracked": len(self.page_conversions),
            "profiles_tracked": len(self.profile_conversions),
            "ctas_tracked": len(self.cta_conversions),
            "attribution_chains": len(self.chains),
            "journey_metrics": self.get_journey_metrics(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_attribution_tracker: Optional[AttributionTracker] = None

def get_attribution_tracker() -> AttributionTracker:
    """Get the global attribution tracker instance."""
    global _attribution_tracker
    if _attribution_tracker is None:
        _attribution_tracker = AttributionTracker()
    return _attribution_tracker


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "BlogVisit",
    "AppSignup",
    "Subscription",
    "AttributionChain",
    "AttributionTracker",
    "get_attribution_tracker",
]
