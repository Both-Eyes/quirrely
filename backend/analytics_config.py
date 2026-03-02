#!/usr/bin/env python3
"""
QUIRRELY ANALYTICS CONFIGURATION v1.0
Privacy-focused analytics with Plausible + internal metrics.

External: Plausible (no cookies, GDPR compliant)
Internal: PostgreSQL (full control)
Errors: Sentry
"""

import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import timedelta


# ═══════════════════════════════════════════════════════════════════════════
# EXTERNAL PROVIDERS
# ═══════════════════════════════════════════════════════════════════════════

# Plausible Analytics (privacy-focused, no cookies)
PLAUSIBLE_DOMAIN = "quirrely.com"
PLAUSIBLE_API_KEY = os.environ.get("PLAUSIBLE_API_KEY", "")

# Sentry Error Tracking
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "development")


# ═══════════════════════════════════════════════════════════════════════════
# EVENT CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

class EventCategory(str, Enum):
    PAGE_VIEW = "page_view"
    CORE_ACTION = "core_action"
    FEATURE_USAGE = "feature_usage"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"


class EventName(str, Enum):
    # Page views (tracked automatically by Plausible)
    
    # Core actions
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    ANALYZE = "analyze"
    SUBSCRIBE = "subscribe"
    
    # Feature usage
    MILESTONE_ACHIEVED = "milestone_achieved"
    FEATURED_SUBMISSION = "featured_submission"
    FEATURED_APPROVED = "featured_approved"
    BOOKMARK_ADDED = "bookmark_added"
    PATH_CREATED = "path_created"
    PATH_FOLLOWED = "path_followed"
    
    # Engagement
    STREAK_STARTED = "streak_started"
    STREAK_CONTINUED = "streak_continued"
    STREAK_BROKEN = "streak_broken"
    DEEP_READ = "deep_read"
    PROFILE_VIEWED = "profile_viewed"
    
    # Conversions
    TRIAL_STARTED = "trial_started"
    TRIAL_CONVERTED = "trial_converted"
    TRIAL_EXPIRED = "trial_expired"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    CHURN = "churn"


EVENT_CATEGORIES: Dict[EventName, EventCategory] = {
    # Core actions
    EventName.SIGNUP: EventCategory.CORE_ACTION,
    EventName.LOGIN: EventCategory.CORE_ACTION,
    EventName.LOGOUT: EventCategory.CORE_ACTION,
    EventName.ANALYZE: EventCategory.CORE_ACTION,
    EventName.SUBSCRIBE: EventCategory.CORE_ACTION,
    
    # Feature usage
    EventName.MILESTONE_ACHIEVED: EventCategory.FEATURE_USAGE,
    EventName.FEATURED_SUBMISSION: EventCategory.FEATURE_USAGE,
    EventName.FEATURED_APPROVED: EventCategory.FEATURE_USAGE,
    EventName.BOOKMARK_ADDED: EventCategory.FEATURE_USAGE,
    EventName.PATH_CREATED: EventCategory.FEATURE_USAGE,
    EventName.PATH_FOLLOWED: EventCategory.FEATURE_USAGE,
    
    # Engagement
    EventName.STREAK_STARTED: EventCategory.ENGAGEMENT,
    EventName.STREAK_CONTINUED: EventCategory.ENGAGEMENT,
    EventName.STREAK_BROKEN: EventCategory.ENGAGEMENT,
    EventName.DEEP_READ: EventCategory.ENGAGEMENT,
    EventName.PROFILE_VIEWED: EventCategory.ENGAGEMENT,
    
    # Conversions
    EventName.TRIAL_STARTED: EventCategory.CONVERSION,
    EventName.TRIAL_CONVERTED: EventCategory.CONVERSION,
    EventName.TRIAL_EXPIRED: EventCategory.CONVERSION,
    EventName.UPGRADE: EventCategory.CONVERSION,
    EventName.DOWNGRADE: EventCategory.CONVERSION,
    EventName.CHURN: EventCategory.CONVERSION,
}


# ═══════════════════════════════════════════════════════════════════════════
# INTERNAL METRICS
# ═══════════════════════════════════════════════════════════════════════════

class MetricType(str, Enum):
    COUNTER = "counter"      # Cumulative count
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution


@dataclass
class MetricDefinition:
    """Definition of an internal metric."""
    name: str
    type: MetricType
    description: str
    unit: Optional[str] = None


INTERNAL_METRICS: List[MetricDefinition] = [
    # User metrics
    MetricDefinition("dau", MetricType.GAUGE, "Daily Active Users"),
    MetricDefinition("wau", MetricType.GAUGE, "Weekly Active Users"),
    MetricDefinition("mau", MetricType.GAUGE, "Monthly Active Users"),
    MetricDefinition("total_users", MetricType.GAUGE, "Total registered users"),
    MetricDefinition("new_signups", MetricType.COUNTER, "New signups", "users"),
    
    # Subscription metrics
    MetricDefinition("mrr", MetricType.GAUGE, "Monthly Recurring Revenue", "CAD"),
    MetricDefinition("arr", MetricType.GAUGE, "Annual Run Rate", "CAD"),
    MetricDefinition("active_subscriptions", MetricType.GAUGE, "Active subscriptions"),
    MetricDefinition("trial_conversion_rate", MetricType.GAUGE, "Trial to paid rate", "percent"),
    MetricDefinition("churn_rate", MetricType.GAUGE, "Monthly churn rate", "percent"),
    
    # Activity metrics
    MetricDefinition("analyses_count", MetricType.COUNTER, "Total analyses", "analyses"),
    MetricDefinition("words_analyzed", MetricType.COUNTER, "Total words analyzed", "words"),
    MetricDefinition("avg_session_duration", MetricType.GAUGE, "Average session", "seconds"),
    
    # Feature metrics
    MetricDefinition("active_streaks", MetricType.GAUGE, "Users with active streaks"),
    MetricDefinition("featured_writers", MetricType.GAUGE, "Total Featured Writers"),
    MetricDefinition("featured_curators", MetricType.GAUGE, "Total Featured Curators"),
    
    # Content metrics
    MetricDefinition("profile_distribution", MetricType.HISTOGRAM, "Voice profile distribution"),
    MetricDefinition("stance_distribution", MetricType.HISTOGRAM, "Stance distribution"),
]


# ═══════════════════════════════════════════════════════════════════════════
# USER-FACING ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

WRITER_ANALYTICS = [
    "words_over_time",        # Daily/weekly/monthly word counts
    "streak_history",         # Streak starts, lengths, breaks
    "voice_evolution",        # Profile changes over time
    "milestone_timeline",     # When milestones achieved
    "analysis_frequency",     # How often they write
]

READER_ANALYTICS = [
    "reading_over_time",      # Posts read per period
    "deep_read_ratio",        # Deep reads vs skims
    "taste_evolution",        # Preference changes
    "profile_exploration",    # Voice types explored
    "bookmark_activity",      # Bookmarking patterns
]

FEATURED_ANALYTICS = [
    "profile_views",          # How many viewed their profile
    "piece_engagement",       # Views on Featured piece
    "path_follows",           # Followers on curated paths
    "referral_traffic",       # Traffic from Featured placement
]


# ═══════════════════════════════════════════════════════════════════════════
# DATA RETENTION
# ═══════════════════════════════════════════════════════════════════════════

DATA_RETENTION = {
    "aggregate_metrics": None,              # Forever
    "daily_snapshots": None,                # Forever
    "user_activity": timedelta(days=365),   # 1 year
    "raw_events": timedelta(days=90),       # 90 days
    "audit_logs": timedelta(days=730),      # 2 years
    "error_logs": timedelta(days=30),       # 30 days
}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FeatureFlag:
    """Simple feature flag configuration."""
    name: str
    description: str
    enabled: bool = False
    percentage: int = 0  # 0-100 for gradual rollout
    allowed_users: Optional[List[str]] = None  # Specific user IDs


FEATURE_FLAGS: Dict[str, FeatureFlag] = {
    "new_voice_algorithm": FeatureFlag(
        name="new_voice_algorithm",
        description="Updated voice profile calculation",
        enabled=False,
        percentage=0,
    ),
    "reading_recommendations": FeatureFlag(
        name="reading_recommendations",
        description="AI-powered reading suggestions",
        enabled=False,
        percentage=0,
    ),
    "dark_mode": FeatureFlag(
        name="dark_mode",
        description="Dark theme option",
        enabled=False,
        percentage=0,
    ),
}


def is_feature_enabled(flag_name: str, user_id: Optional[str] = None) -> bool:
    """Check if feature is enabled for user."""
    flag = FEATURE_FLAGS.get(flag_name)
    if not flag:
        return False
    
    if not flag.enabled:
        return False
    
    # Check specific user allowlist
    if flag.allowed_users and user_id in flag.allowed_users:
        return True
    
    # Check percentage rollout
    if flag.percentage >= 100:
        return True
    
    if flag.percentage > 0 and user_id:
        # Deterministic hash for consistent experience
        import hashlib
        hash_val = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
        return (hash_val % 100) < flag.percentage
    
    return False


# ═══════════════════════════════════════════════════════════════════════════
# FUNNEL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

FUNNELS = {
    "signup_to_first_analysis": {
        "name": "Signup to First Analysis",
        "steps": ["signup", "email_verified", "first_analysis"],
    },
    "free_to_trial": {
        "name": "Free to Trial",
        "steps": ["signup", "hit_word_limit", "trial_started"],
    },
    "trial_to_paid": {
        "name": "Trial to Paid",
        "steps": ["trial_started", "trial_active_day_3", "trial_active_day_7", "subscribed"],
    },
    "writer_to_featured": {
        "name": "Writer to Featured",
        "steps": ["subscribed", "daily_1k", "streak_7_day", "featured_eligible", "featured_submitted", "featured_approved"],
    },
    "reader_to_curator": {
        "name": "Reader to Curator",
        "steps": ["reader_subscribed", "posts_read_10", "deep_reads_5", "curator_eligible", "curator_submitted", "curator_approved"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# COHORT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

COHORT_PERIODS = ["daily", "weekly", "monthly"]

RETENTION_ACTIONS = {
    "writer": "analyze",     # Writers retained if they analyze
    "reader": "read_post",   # Readers retained if they read
    "any": "active",         # Any activity counts
}
