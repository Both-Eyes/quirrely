#!/usr/bin/env python3
"""
QUIRRELY EMAIL CONFIGURATION v1.0
Resend integration with React Email templates.

Provider: Resend
Templates: React Email (component-based)
Analytics: Basic (opens, clicks)
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import time


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_...")

# Sender addresses
FROM_EMAIL = "Quirrely <hello@quirrely.com>"
FROM_EMAIL_NOREPLY = "Quirrely <noreply@quirrely.com>"
SUPPORT_EMAIL = "support@quirrely.com"

# Branding
BRAND = {
    "name": "Quirrely",
    "logo_url": "https://quirrely.com/logo.png",
    "website_url": "https://quirrely.com",
    "support_url": "https://quirrely.com/support",
    "colors": {
        "primary": "#FF6B6B",      # Coral
        "secondary": "#D4A574",    # Soft Gold
        "text": "#2D3436",         # Ink
        "muted": "#636E72",        # Muted
        "background": "#FFFBF5",   # Warm white
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL TYPES
# ═══════════════════════════════════════════════════════════════════════════

class EmailType(str, Enum):
    # Transactional (always sent)
    WELCOME = "welcome"
    EMAIL_VERIFICATION = "email_verification"
    MAGIC_LINK = "magic_link"
    PASSWORD_RESET = "password_reset"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    PAYMENT_FAILED = "payment_failed"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDING = "trial_ending"
    FEATURED_SUBMISSION_RECEIVED = "featured_submission_received"
    FEATURED_ACCEPTED = "featured_accepted"
    FEATURED_REJECTED = "featured_rejected"
    
    # Engagement (opt-out available)
    STREAK_AT_RISK = "streak_at_risk"
    MILESTONE_ACHIEVED = "milestone_achieved"
    WEEKLY_DIGEST = "weekly_digest"
    PATH_FOLLOWED = "path_followed"
    AUTHORITY_ELIGIBLE = "authority_eligible"


class EmailCategory(str, Enum):
    TRANSACTIONAL = "transactional"  # Cannot unsubscribe
    ENGAGEMENT = "engagement"         # Can unsubscribe
    DIGEST = "digest"                 # Can unsubscribe


EMAIL_CATEGORIES: Dict[EmailType, EmailCategory] = {
    # Transactional
    EmailType.WELCOME: EmailCategory.TRANSACTIONAL,
    EmailType.EMAIL_VERIFICATION: EmailCategory.TRANSACTIONAL,
    EmailType.MAGIC_LINK: EmailCategory.TRANSACTIONAL,
    EmailType.PASSWORD_RESET: EmailCategory.TRANSACTIONAL,
    EmailType.SUBSCRIPTION_CONFIRMED: EmailCategory.TRANSACTIONAL,
    EmailType.SUBSCRIPTION_CANCELLED: EmailCategory.TRANSACTIONAL,
    EmailType.PAYMENT_FAILED: EmailCategory.TRANSACTIONAL,
    EmailType.TRIAL_STARTED: EmailCategory.TRANSACTIONAL,
    EmailType.TRIAL_ENDING: EmailCategory.TRANSACTIONAL,
    EmailType.FEATURED_SUBMISSION_RECEIVED: EmailCategory.TRANSACTIONAL,
    EmailType.FEATURED_ACCEPTED: EmailCategory.TRANSACTIONAL,
    EmailType.FEATURED_REJECTED: EmailCategory.TRANSACTIONAL,
    
    # Engagement
    EmailType.STREAK_AT_RISK: EmailCategory.ENGAGEMENT,
    EmailType.MILESTONE_ACHIEVED: EmailCategory.ENGAGEMENT,
    EmailType.PATH_FOLLOWED: EmailCategory.ENGAGEMENT,
    EmailType.AUTHORITY_ELIGIBLE: EmailCategory.ENGAGEMENT,
    
    # Digest
    EmailType.WEEKLY_DIGEST: EmailCategory.DIGEST,
}


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL METADATA
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EmailTemplate:
    """Email template configuration."""
    type: EmailType
    subject: str
    preview_text: str
    category: EmailCategory
    from_email: str = FROM_EMAIL_NOREPLY
    reply_to: Optional[str] = None
    

EMAIL_TEMPLATES: Dict[EmailType, EmailTemplate] = {
    # Transactional
    EmailType.WELCOME: EmailTemplate(
        type=EmailType.WELCOME,
        subject="Welcome to Quirrely 🐿️",
        preview_text="Your voice matters. Let's discover it together.",
        category=EmailCategory.TRANSACTIONAL,
        from_email=FROM_EMAIL,
    ),
    EmailType.EMAIL_VERIFICATION: EmailTemplate(
        type=EmailType.EMAIL_VERIFICATION,
        subject="Verify your email",
        preview_text="Click to verify your Quirrely account",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.MAGIC_LINK: EmailTemplate(
        type=EmailType.MAGIC_LINK,
        subject="Your Quirrely login link",
        preview_text="Click to sign in to Quirrely",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.PASSWORD_RESET: EmailTemplate(
        type=EmailType.PASSWORD_RESET,
        subject="Reset your password",
        preview_text="Click to reset your Quirrely password",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.SUBSCRIPTION_CONFIRMED: EmailTemplate(
        type=EmailType.SUBSCRIPTION_CONFIRMED,
        subject="Welcome to {tier_name}! 🎉",
        preview_text="Your subscription is active",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.SUBSCRIPTION_CANCELLED: EmailTemplate(
        type=EmailType.SUBSCRIPTION_CANCELLED,
        subject="Your subscription has been cancelled",
        preview_text="We're sorry to see you go",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.PAYMENT_FAILED: EmailTemplate(
        type=EmailType.PAYMENT_FAILED,
        subject="Payment failed - action required",
        preview_text="Please update your payment method",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.TRIAL_STARTED: EmailTemplate(
        type=EmailType.TRIAL_STARTED,
        subject="Your PRO trial has started! 🚀",
        preview_text="7 days of full access",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.TRIAL_ENDING: EmailTemplate(
        type=EmailType.TRIAL_ENDING,
        subject="Your trial ends in 2 days",
        preview_text="Upgrade to keep your PRO features",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.FEATURED_SUBMISSION_RECEIVED: EmailTemplate(
        type=EmailType.FEATURED_SUBMISSION_RECEIVED,
        subject="We received your Featured submission",
        preview_text="We'll review it soon",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.FEATURED_ACCEPTED: EmailTemplate(
        type=EmailType.FEATURED_ACCEPTED,
        subject="Congratulations! You're now Featured ⭐",
        preview_text="Your work will be showcased on Quirrely",
        category=EmailCategory.TRANSACTIONAL,
    ),
    EmailType.FEATURED_REJECTED: EmailTemplate(
        type=EmailType.FEATURED_REJECTED,
        subject="About your Featured submission",
        preview_text="Feedback on your submission",
        category=EmailCategory.TRANSACTIONAL,
    ),
    
    # Engagement
    EmailType.STREAK_AT_RISK: EmailTemplate(
        type=EmailType.STREAK_AT_RISK,
        subject="Don't break your streak! 🔥",
        preview_text="Write today to keep your {streak_days}-day streak alive",
        category=EmailCategory.ENGAGEMENT,
    ),
    EmailType.MILESTONE_ACHIEVED: EmailTemplate(
        type=EmailType.MILESTONE_ACHIEVED,
        subject="Milestone unlocked: {milestone_name} 🏆",
        preview_text="You've achieved something special",
        category=EmailCategory.ENGAGEMENT,
    ),
    EmailType.PATH_FOLLOWED: EmailTemplate(
        type=EmailType.PATH_FOLLOWED,
        subject="Someone is following your path",
        preview_text="Your curation is guiding readers",
        category=EmailCategory.ENGAGEMENT,
    ),
    EmailType.AUTHORITY_ELIGIBLE: EmailTemplate(
        type=EmailType.AUTHORITY_ELIGIBLE,
        subject="You're eligible for Authority status 👑",
        preview_text="Claim your place as a recognized voice",
        category=EmailCategory.ENGAGEMENT,
    ),
    
    # Digest
    EmailType.WEEKLY_DIGEST: EmailTemplate(
        type=EmailType.WEEKLY_DIGEST,
        subject="Your week in writing",
        preview_text="Here's what you accomplished this week",
        category=EmailCategory.DIGEST,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL PREFERENCES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class EmailPreferences:
    """User email preferences."""
    user_id: str
    engagement_enabled: bool = True
    digest_enabled: bool = True
    digest_day: int = 0  # 0 = Monday
    preferred_time: time = field(default_factory=lambda: time(9, 0))  # 9 AM
    timezone: str = "UTC"
    
    def can_receive(self, email_type: EmailType) -> bool:
        """Check if user can receive this email type."""
        category = EMAIL_CATEGORIES.get(email_type)
        
        if category == EmailCategory.TRANSACTIONAL:
            return True  # Always send transactional
        elif category == EmailCategory.ENGAGEMENT:
            return self.engagement_enabled
        elif category == EmailCategory.DIGEST:
            return self.digest_enabled
        
        return True


DEFAULT_PREFERENCES = EmailPreferences(user_id="")


# ═══════════════════════════════════════════════════════════════════════════
# TIMING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

TIMING_CONFIG = {
    # Streak at risk: Send at 6 PM user's local time
    EmailType.STREAK_AT_RISK: {
        "send_hour": 18,
        "check_condition": "no_activity_today",
    },
    
    # Trial ending: Send 2 days before end
    EmailType.TRIAL_ENDING: {
        "days_before": 2,
        "send_hour": 10,
    },
    
    # Weekly digest: Send on Monday at 9 AM
    EmailType.WEEKLY_DIGEST: {
        "day_of_week": 0,  # Monday
        "send_hour": 9,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

ANALYTICS_CONFIG = {
    "track_opens": True,
    "track_clicks": True,
    "track_unsubscribes": True,
}


# ═══════════════════════════════════════════════════════════════════════════
# UNSUBSCRIBE
# ═══════════════════════════════════════════════════════════════════════════

UNSUBSCRIBE_CONFIG = {
    "one_click_enabled": True,
    "preferences_url": "https://quirrely.com/email-preferences",
    "unsubscribe_url": "https://quirrely.com/unsubscribe",
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_template(email_type: EmailType) -> Optional[EmailTemplate]:
    """Get email template by type."""
    return EMAIL_TEMPLATES.get(email_type)


def is_transactional(email_type: EmailType) -> bool:
    """Check if email is transactional (cannot unsubscribe)."""
    return EMAIL_CATEGORIES.get(email_type) == EmailCategory.TRANSACTIONAL


def get_unsubscribe_url(user_id: str, category: EmailCategory) -> str:
    """Generate unsubscribe URL."""
    import hashlib
    token = hashlib.sha256(f"{user_id}:{category.value}".encode()).hexdigest()[:16]
    return f"{UNSUBSCRIBE_CONFIG['unsubscribe_url']}?uid={user_id}&cat={category.value}&t={token}"


def get_preferences_url(user_id: str) -> str:
    """Generate preferences URL."""
    import hashlib
    token = hashlib.sha256(f"{user_id}:prefs".encode()).hexdigest()[:16]
    return f"{UNSUBSCRIBE_CONFIG['preferences_url']}?uid={user_id}&t={token}"
