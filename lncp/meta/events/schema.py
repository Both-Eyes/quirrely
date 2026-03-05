#!/usr/bin/env python3
"""
LNCP META: EVENT SCHEMA v5.1.0-G2M
Defines all event types and structures for full-stack observability.
G2M (Go-To-Market) Release - 151 event types.

This is the CONTRACT between App and Meta.
App emits events matching this schema.
Meta consumes and processes them.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import uuid


# ═══════════════════════════════════════════════════════════════════════════
# USER TIERS
# ═══════════════════════════════════════════════════════════════════════════

class UserTier(str, Enum):
    """User subscription tiers."""
    ANONYMOUS = "anonymous"   # Not signed up
    FREE = "free"             # Signed up, no payment
    TRIAL = "trial"           # In trial period
    PRO = "pro"               # Paying monthly/annual
    ENTERPRISE = "enterprise" # Custom plan


# ═══════════════════════════════════════════════════════════════════════════
# EVENT CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

class EventCategory(str, Enum):
    """High-level event categories."""
    ONBOARDING = "onboarding"
    ANALYSIS = "analysis"
    ENGAGEMENT = "engagement"
    ACCOUNT = "account"
    FEEDBACK = "feedback"
    SYSTEM = "system"


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class EventType(str, Enum):
    """All trackable event types."""
    
    # ─────────────────────────────────────────────────────────────────────
    # ONBOARDING
    # ─────────────────────────────────────────────────────────────────────
    ONBOARDING_STARTED = "onboarding.started"
    ONBOARDING_STEP_COMPLETED = "onboarding.step_completed"
    ONBOARDING_COMPLETED = "onboarding.completed"
    ONBOARDING_ABANDONED = "onboarding.abandoned"
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYSIS (Core product usage)
    # ─────────────────────────────────────────────────────────────────────
    ANALYSIS_STARTED = "analysis.started"
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    
    PROFILE_VIEWED = "analysis.profile_viewed"
    PROFILE_SWITCHED = "analysis.profile_switched"
    PROFILE_ACCEPTED = "analysis.profile_accepted"  # Implicit: proceeded with predicted
    
    RESULT_EXPORTED = "analysis.result_exported"
    RESULT_SAVED = "analysis.result_saved"
    RESULT_SHARED = "analysis.result_shared"
    
    # ─────────────────────────────────────────────────────────────────────
    # ENGAGEMENT (Session & feature usage)
    # ─────────────────────────────────────────────────────────────────────
    SESSION_STARTED = "session.started"
    SESSION_ENDED = "session.ended"
    SESSION_HEARTBEAT = "session.heartbeat"  # Periodic ping
    
    PAGE_VIEWED = "engagement.page_viewed"
    FEATURE_USED = "engagement.feature_used"
    
    # Friction signals (E5)
    HELP_ACCESSED = "engagement.help_accessed"
    SUPPORT_CONTACTED = "engagement.support_contacted"
    ERROR_ENCOUNTERED = "engagement.error_encountered"
    FLOW_ABANDONED = "engagement.flow_abandoned"
    
    # ─────────────────────────────────────────────────────────────────────
    # ACCOUNT (Lifecycle events)
    # ─────────────────────────────────────────────────────────────────────
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_VERIFIED = "account.verified"
    ACCOUNT_UPGRADED = "account.upgraded"
    ACCOUNT_DOWNGRADED = "account.downgraded"
    ACCOUNT_CHURNED = "account.churned"
    ACCOUNT_REACTIVATED = "account.reactivated"
    
    TRIAL_STARTED = "account.trial_started"
    TRIAL_ENDING_SOON = "account.trial_ending_soon"  # 3 days left
    TRIAL_ENDED = "account.trial_ended"
    TRIAL_CONVERTED = "account.trial_converted"
    
    # ─────────────────────────────────────────────────────────────────────
    # FEEDBACK (Explicit user signals)
    # ─────────────────────────────────────────────────────────────────────
    FEEDBACK_PROFILE_RATING = "feedback.profile_rating"
    FEEDBACK_NPS_SUBMITTED = "feedback.nps_submitted"
    FEEDBACK_FEATURE_REQUEST = "feedback.feature_request"
    FEEDBACK_BUG_REPORT = "feedback.bug_report"
    
    # ─────────────────────────────────────────────────────────────────────
    # SYSTEM (Internal events)
    # ─────────────────────────────────────────────────────────────────────
    SYSTEM_ERROR = "system.error"
    SYSTEM_PERFORMANCE = "system.performance"
    
    # ─────────────────────────────────────────────────────────────────────
    # HALO SAFETY EVENTS (v5.2.0)
    # ─────────────────────────────────────────────────────────────────────
    HALO_CHECK_STARTED = "safety.check_started"
    HALO_CHECK_PASSED = "safety.check_passed"
    HALO_VIOLATION_T1 = "safety.violation_t1"      # Warning - allowed with notice
    HALO_VIOLATION_T2 = "safety.violation_t2"      # Caution - cooldown applied
    HALO_VIOLATION_T3 = "safety.violation_t3"      # Block - immediate rejection
    HALO_FALSE_POSITIVE = "safety.false_positive"  # User appealed, overturned
    HALO_APPEAL_SUBMITTED = "safety.appeal_submitted"
    HALO_PATTERN_TRIGGERED = "safety.pattern_triggered"
    HALO_USER_WARNED = "safety.user_warned"
    HALO_USER_COOLDOWN = "safety.user_cooldown"
    HALO_USER_SUSPENDED = "safety.user_suspended"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: ACHIEVEMENT EVENTS (P3)
    # ─────────────────────────────────────────────────────────────────────
    BADGE_EARNED = "achievement.badge_earned"
    BADGE_PROGRESS = "achievement.badge_progress"
    XP_GAINED = "achievement.xp_gained"
    LEVEL_UP = "achievement.level_up"
    CHALLENGE_STARTED = "achievement.challenge_started"
    CHALLENGE_PROGRESS = "achievement.challenge_progress"
    CHALLENGE_COMPLETED = "achievement.challenge_completed"
    CHALLENGE_FAILED = "achievement.challenge_failed"
    STREAK_STARTED = "achievement.streak_started"
    STREAK_CONTINUED = "achievement.streak_continued"
    STREAK_BROKEN = "achievement.streak_broken"
    STREAK_MILESTONE = "achievement.streak_milestone"
    LEADERBOARD_VIEWED = "achievement.leaderboard_viewed"
    LEADERBOARD_RANK_CHANGED = "achievement.leaderboard_rank_changed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: PROGRESSIVE UNLOCK EVENTS (P3)
    # ─────────────────────────────────────────────────────────────────────
    FEATURE_UNLOCKED = "progressive.feature_unlocked"
    UNLOCK_AVAILABLE = "progressive.unlock_available"
    UNLOCK_REMINDER = "progressive.unlock_reminder"
    DAY_7_OFFER_SHOWN = "progressive.day7_offer_shown"
    DAY_7_OFFER_CLICKED = "progressive.day7_offer_clicked"
    DAY_7_OFFER_CLAIMED = "progressive.day7_offer_claimed"
    DAY_7_OFFER_DISMISSED = "progressive.day7_offer_dismissed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: BUNDLING EVENTS (P1)
    # ─────────────────────────────────────────────────────────────────────
    BUNDLE_SECTION_VIEWED = "bundle.section_viewed"
    BUNDLE_VIEWED = "bundle.viewed"
    BUNDLE_COMPARED = "bundle.compared"
    BUNDLE_SELECTED = "bundle.selected"
    BUNDLE_PURCHASED = "bundle.purchased"
    STANDALONE_SELECTED = "bundle.standalone_selected"
    BUNDLE_SAVINGS_SHOWN = "bundle.savings_shown"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: RETENTION EVENTS (P1)
    # ─────────────────────────────────────────────────────────────────────
    CHURN_INTENT_DETECTED = "retention.churn_intent"
    RETENTION_FLOW_STARTED = "retention.flow_started"
    PAUSE_OFFERED = "retention.pause_offered"
    PAUSE_ACCEPTED = "retention.pause_accepted"
    PAUSE_DECLINED = "retention.pause_declined"
    DOWNGRADE_OFFERED = "retention.downgrade_offered"
    DOWNGRADE_ACCEPTED = "retention.downgrade_accepted"
    DOWNGRADE_DECLINED = "retention.downgrade_declined"
    SAVE_OFFER_SHOWN = "retention.save_offer_shown"
    SAVE_OFFER_ACCEPTED = "retention.save_offer_accepted"
    SAVE_OFFER_DECLINED = "retention.save_offer_declined"
    CANCEL_PROCEEDED = "retention.cancel_proceeded"
    CANCEL_ABANDONED = "retention.cancel_abandoned"
    WIN_BACK_SENT = "retention.win_back_sent"
    WIN_BACK_CONVERTED = "retention.win_back_converted"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: ANNUAL CONVERSION EVENTS (P2)
    # ─────────────────────────────────────────────────────────────────────
    ANNUAL_BANNER_SHOWN = "annual.banner_shown"
    ANNUAL_BANNER_CLICKED = "annual.banner_clicked"
    ANNUAL_BANNER_DISMISSED = "annual.banner_dismissed"
    ANNUAL_SAVINGS_VIEWED = "annual.savings_viewed"
    ANNUAL_SWITCH_INITIATED = "annual.switch_initiated"
    ANNUAL_SWITCH_COMPLETED = "annual.switch_completed"
    ANNUAL_SWITCH_FAILED = "annual.switch_failed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: SMART NOTIFICATION EVENTS (P2)
    # ─────────────────────────────────────────────────────────────────────
    NOTIFICATION_SHOWN = "notification.shown"
    NOTIFICATION_CLICKED = "notification.clicked"
    NOTIFICATION_DISMISSED = "notification.dismissed"
    NOTIFICATION_SNOOZED = "notification.snoozed"
    VOICE_EVOLUTION_NOTIF = "notification.voice_evolution"
    SOCIAL_PROOF_NOTIF = "notification.social_proof"
    BADGE_PROGRESS_NOTIF = "notification.badge_progress"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: SOCIAL PROOF EVENTS (P2)
    # ─────────────────────────────────────────────────────────────────────
    SOCIAL_PROOF_VIEWED = "social.proof_viewed"
    SOCIAL_PROOF_CLICKED = "social.proof_clicked"
    SOCIAL_PROOF_STAT_VIEWED = "social.stat_viewed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: TIER EVENTS (P2)
    # ─────────────────────────────────────────────────────────────────────
    GROWTH_TIER_VIEWED = "tier.growth_viewed"
    GROWTH_TIER_SELECTED = "tier.growth_selected"
    GROWTH_TIER_PURCHASED = "tier.growth_purchased"
    TIER_COMPARISON_VIEWED = "tier.comparison_viewed"
    TIER_UPGRADE_PATH_SHOWN = "tier.upgrade_path_shown"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: FIRST ANALYSIS HOOK EVENTS (P1)
    # ─────────────────────────────────────────────────────────────────────
    HOOK_SHOWN = "hook.shown"
    HOOK_AUTHOR_CARD_VIEWED = "hook.author_card_viewed"
    HOOK_AUTHOR_CLICKED = "hook.author_clicked"
    HOOK_UNLOCK_CLICKED = "hook.unlock_clicked"
    HOOK_UPGRADE_CLICKED = "hook.upgrade_clicked"
    HOOK_DISMISSED = "hook.dismissed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: CTA INTERACTION EVENTS (M4)
    # ─────────────────────────────────────────────────────────────────────
    CTA_CLICKED = "cta.clicked"
    CTA_LOADING_STARTED = "cta.loading_started"
    CTA_LOADING_COMPLETED = "cta.loading_completed"
    CTA_LOADING_FAILED = "cta.loading_failed"
    
    # ─────────────────────────────────────────────────────────────────────
    # v3.1.1: CURRENCY/COUNTRY EVENTS
    # ─────────────────────────────────────────────────────────────────────
    COUNTRY_DETECTED = "geo.country_detected"
    CURRENCY_DISPLAYED = "geo.currency_displayed"
    CURRENCY_CONVERTED = "geo.currency_converted"
    
    # ─────────────────────────────────────────────────────────────────────
    # v5.1: BLOG EVENTS
    # ─────────────────────────────────────────────────────────────────────
    BLOG_PAGE_VIEWED = "blog.page_viewed"
    BLOG_CTA_SHOWN = "blog.cta_shown"
    BLOG_CTA_CLICKED = "blog.cta_clicked"
    BLOG_CTA_CONVERTED = "blog.cta_converted"
    BLOG_SCROLL_DEPTH = "blog.scroll_depth"
    BLOG_TIME_ON_PAGE = "blog.time_on_page"
    BLOG_EXIT_INTENT = "blog.exit_intent"
    BLOG_INTERNAL_LINK_CLICKED = "blog.internal_link_clicked"
    BLOG_RELATED_POST_CLICKED = "blog.related_post_clicked"
    BLOG_SHARE_CLICKED = "blog.share_clicked"
    BLOG_COMMENT_SUBMITTED = "blog.comment_submitted"
    
    # ─────────────────────────────────────────────────────────────────────
    # v5.1: SEO EVENTS
    # ─────────────────────────────────────────────────────────────────────
    SEO_IMPRESSION = "seo.impression"
    SEO_CLICK = "seo.click"
    SEO_POSITION_CHANGED = "seo.position_changed"
    SEO_NEW_KEYWORD_RANKED = "seo.new_keyword_ranked"
    SEO_KEYWORD_LOST = "seo.keyword_lost"
    SEO_PAGE_INDEXED = "seo.page_indexed"
    SEO_PAGE_DEINDEXED = "seo.page_deindexed"
    SEO_CRAWL_ERROR = "seo.crawl_error"
    SEO_CORE_WEB_VITALS = "seo.core_web_vitals"
    
    # ─────────────────────────────────────────────────────────────────────
    # v5.1: CONTENT EVENTS
    # ─────────────────────────────────────────────────────────────────────
    CONTENT_PUBLISHED = "content.published"
    CONTENT_UPDATED = "content.updated"
    CONTENT_REFRESH_NEEDED = "content.refresh_needed"
    CONTENT_PERFORMANCE_ALERT = "content.performance_alert"
    
    @property
    def category(self) -> EventCategory:
        """Get category for this event type."""
        prefix = self.value.split(".")[0]
        mapping = {
            "onboarding": EventCategory.ONBOARDING,
            "analysis": EventCategory.ANALYSIS,
            "session": EventCategory.ENGAGEMENT,
            "engagement": EventCategory.ENGAGEMENT,
            "account": EventCategory.ACCOUNT,
            "feedback": EventCategory.FEEDBACK,
            "system": EventCategory.SYSTEM,
            "safety": EventCategory.SYSTEM,
            # v3.1.1 categories
            "achievement": EventCategory.ENGAGEMENT,
            "progressive": EventCategory.ENGAGEMENT,
            "bundle": EventCategory.ACCOUNT,
            "retention": EventCategory.ACCOUNT,
            "annual": EventCategory.ACCOUNT,
            "notification": EventCategory.ENGAGEMENT,
            "social": EventCategory.ENGAGEMENT,
            "tier": EventCategory.ACCOUNT,
            "hook": EventCategory.ONBOARDING,
            "cta": EventCategory.ENGAGEMENT,
            "geo": EventCategory.SYSTEM,
            # v5.1 blog/SEO categories
            "blog": EventCategory.ENGAGEMENT,
            "seo": EventCategory.SYSTEM,
            "content": EventCategory.SYSTEM,
        }
        return mapping.get(prefix, EventCategory.SYSTEM)


# ═══════════════════════════════════════════════════════════════════════════
# CORE EVENT STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AppEvent:
    """
    Core event structure.
    
    This is the contract between App and Meta.
    All events must conform to this structure.
    """
    
    # ─────────────────────────────────────────────────────────────────────
    # IDENTITY
    # ─────────────────────────────────────────────────────────────────────
    
    event_id: str                    # Unique event ID (UUID)
    event_type: EventType            # From EventType enum
    timestamp: datetime              # When event occurred (UTC)
    
    # ─────────────────────────────────────────────────────────────────────
    # USER CONTEXT
    # ─────────────────────────────────────────────────────────────────────
    
    visitor_id: str                  # Always present (anonymous tracking)
    user_id: Optional[str] = None    # Present after signup
    tier: UserTier = UserTier.ANONYMOUS
    
    # ─────────────────────────────────────────────────────────────────────
    # SESSION CONTEXT
    # ─────────────────────────────────────────────────────────────────────
    
    session_id: str = ""             # Groups events in a session
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT DATA
    # ─────────────────────────────────────────────────────────────────────
    
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # ─────────────────────────────────────────────────────────────────────
    # SOURCE & METADATA
    # ─────────────────────────────────────────────────────────────────────
    
    source: str = "app"              # "app", "blog", "api", "system"
    version: str = "1.0"             # Schema version
    
    # ─────────────────────────────────────────────────────────────────────
    # METHODS
    # ─────────────────────────────────────────────────────────────────────
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "visitor_id": self.visitor_id,
            "user_id": self.user_id,
            "tier": self.tier.value,
            "session_id": self.session_id,
            "payload": self.payload,
            "source": self.source,
            "version": self.version,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AppEvent":
        """Create from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            visitor_id=data["visitor_id"],
            user_id=data.get("user_id"),
            tier=UserTier(data.get("tier", "anonymous")),
            session_id=data.get("session_id", ""),
            payload=data.get("payload", {}),
            source=data.get("source", "app"),
            version=data.get("version", "1.0"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "AppEvent":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique event ID."""
        return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════
# PAYLOAD SCHEMAS (Type hints for specific events)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class OnboardingStepPayload:
    """Payload for onboarding step events."""
    step: int
    step_name: str
    duration_seconds: float = 0
    
    def to_dict(self) -> Dict:
        return {"step": self.step, "step_name": self.step_name, 
                "duration_seconds": self.duration_seconds}


@dataclass
class AnalysisPayload:
    """Payload for analysis events."""
    text_length: int
    token_count: int = 0
    profile_id: Optional[str] = None
    profile_name: Optional[str] = None
    confidence: float = 0
    duration_ms: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "text_length": self.text_length,
            "token_count": self.token_count,
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "confidence": self.confidence,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ProfileViewPayload:
    """Payload for profile view events."""
    profile_id: str
    profile_name: str
    view_duration_seconds: float
    scroll_depth_percent: float = 0
    sections_viewed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "view_duration_seconds": self.view_duration_seconds,
            "scroll_depth_percent": self.scroll_depth_percent,
            "sections_viewed": self.sections_viewed,
        }


@dataclass
class ProfileSwitchPayload:
    """Payload for profile switch events."""
    from_profile_id: str
    from_profile_name: str
    to_profile_id: str
    to_profile_name: str
    reason: Optional[str] = None  # If user provides reason
    
    def to_dict(self) -> Dict:
        return {
            "from_profile_id": self.from_profile_id,
            "from_profile_name": self.from_profile_name,
            "to_profile_id": self.to_profile_id,
            "to_profile_name": self.to_profile_name,
            "reason": self.reason,
        }


@dataclass
class SessionPayload:
    """Payload for session events."""
    referrer: Optional[str] = None
    landing_page: Optional[str] = None
    duration_seconds: float = 0
    pages_viewed: int = 0
    actions_taken: int = 0
    device_type: str = "unknown"
    
    # UTM attribution parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "referrer": self.referrer,
            "landing_page": self.landing_page,
            "duration_seconds": self.duration_seconds,
            "pages_viewed": self.pages_viewed,
            "actions_taken": self.actions_taken,
            "device_type": self.device_type,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "utm_term": self.utm_term,
            "utm_content": self.utm_content,
        }


@dataclass 
class AccountPayload:
    """Payload for account events."""
    source: Optional[str] = None  # signup source
    referrer: Optional[str] = None
    from_tier: Optional[str] = None
    to_tier: Optional[str] = None
    plan: Optional[str] = None
    reason: Optional[str] = None
    lifetime_days: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "referrer": self.referrer,
            "from_tier": self.from_tier,
            "to_tier": self.to_tier,
            "plan": self.plan,
            "reason": self.reason,
            "lifetime_days": self.lifetime_days,
        }


@dataclass
class FrictionPayload:
    """Payload for friction events (help, errors, abandonment)."""
    context: str  # Where in the app
    action: Optional[str] = None  # What user was trying to do
    error_code: Optional[str] = None  # For errors
    error_message: Optional[str] = None
    flow_name: Optional[str] = None  # For abandonment
    flow_step: Optional[int] = None
    help_topic: Optional[str] = None  # For help access
    
    def to_dict(self) -> Dict:
        return {
            "context": self.context,
            "action": self.action,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "flow_name": self.flow_name,
            "flow_step": self.flow_step,
            "help_topic": self.help_topic,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EVENT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_event(event: AppEvent) -> List[str]:
    """
    Validate an event.
    
    Returns list of validation errors (empty if valid).
    """
    errors = []
    
    # Required fields
    if not event.event_id:
        errors.append("event_id is required")
    if not event.visitor_id:
        errors.append("visitor_id is required")
    if not event.timestamp:
        errors.append("timestamp is required")
    
    # User context
    if event.tier != UserTier.ANONYMOUS and not event.user_id:
        errors.append("user_id required for non-anonymous tier")
    
    # Payload requirements by event type
    required_payload = {
        EventType.ANALYSIS_COMPLETED: ["text_length"],
        EventType.PROFILE_VIEWED: ["profile_id", "view_duration_seconds"],
        EventType.PROFILE_SWITCHED: ["from_profile_id", "to_profile_id"],
        EventType.ACCOUNT_UPGRADED: ["from_tier", "to_tier"],
    }
    
    if event.event_type in required_payload:
        for field in required_payload[event.event_type]:
            if field not in event.payload:
                errors.append(f"payload.{field} required for {event.event_type.value}")
    
    return errors


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "UserTier",
    "EventCategory",
    "EventType",
    "AppEvent",
    "OnboardingStepPayload",
    "AnalysisPayload",
    "ProfileViewPayload",
    "ProfileSwitchPayload",
    "SessionPayload",
    "AccountPayload",
    "FrictionPayload",
    "validate_event",
]
