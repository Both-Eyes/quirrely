#!/usr/bin/env python3
"""
QUIRRELY DASHBOARD CONFIGURATION v1.0
Dashboard sections, settings categories, and display configuration.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD SECTIONS
# ═══════════════════════════════════════════════════════════════════════════

class DashboardSection(str, Enum):
    # Writer sections
    TODAY_PROGRESS = "today_progress"
    VOICE_SNAPSHOT = "voice_snapshot"
    MILESTONES = "milestones"
    RECENT_ANALYSES = "recent_analyses"
    FEATURED_STATUS = "featured_status"
    AUTHORITY_PROGRESS = "authority_progress"
    
    # Reader sections
    READING_ACTIVITY = "reading_activity"
    READING_TASTE = "reading_taste"
    BOOKMARKS = "bookmarks"
    CURATOR_PROGRESS = "curator_progress"
    FEATURED_PATHS = "featured_paths"


@dataclass
class SectionConfig:
    """Configuration for a dashboard section."""
    id: DashboardSection
    title: str
    description: str
    icon: str
    requires_tier: Optional[List[str]] = None  # None = all tiers
    requires_feature: Optional[str] = None


WRITER_SECTIONS: List[SectionConfig] = [
    SectionConfig(
        id=DashboardSection.TODAY_PROGRESS,
        title="Today's Progress",
        description="Your writing activity today",
        icon="✍️",
    ),
    SectionConfig(
        id=DashboardSection.VOICE_SNAPSHOT,
        title="Your Voice",
        description="Current voice profile",
        icon="🎯",
    ),
    SectionConfig(
        id=DashboardSection.MILESTONES,
        title="Milestones",
        description="Progress toward achievements",
        icon="🏆",
    ),
    SectionConfig(
        id=DashboardSection.RECENT_ANALYSES,
        title="Recent Analyses",
        description="Your latest writing samples",
        icon="📝",
    ),
    SectionConfig(
        id=DashboardSection.FEATURED_STATUS,
        title="Featured Writer",
        description="Your path to recognition",
        icon="⭐",
        requires_tier=["pro", "trial", "bundle"],
    ),
    SectionConfig(
        id=DashboardSection.AUTHORITY_PROGRESS,
        title="Authority Status",
        description="Sustained excellence",
        icon="👑",
        requires_feature="featured_writer",
    ),
]

READER_SECTIONS: List[SectionConfig] = [
    SectionConfig(
        id=DashboardSection.READING_ACTIVITY,
        title="Reading Activity",
        description="Your reading this week",
        icon="📖",
    ),
    SectionConfig(
        id=DashboardSection.READING_TASTE,
        title="Your Taste",
        description="Reading preference profile",
        icon="🎨",
    ),
    SectionConfig(
        id=DashboardSection.BOOKMARKS,
        title="Bookmarks",
        description="Saved posts",
        icon="🔖",
    ),
    SectionConfig(
        id=DashboardSection.CURATOR_PROGRESS,
        title="Curator Journey",
        description="Path to Featured Curator",
        icon="📚",
        requires_tier=["curator", "bundle"],
    ),
    SectionConfig(
        id=DashboardSection.FEATURED_PATHS,
        title="Your Paths",
        description="Curated reading paths",
        icon="🗺️",
        requires_feature="featured_curator",
    ),
]


# ═══════════════════════════════════════════════════════════════════════════
# SETTINGS CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

class SettingsCategory(str, Enum):
    ACCOUNT = "account"
    PROFILE = "profile"
    SUBSCRIPTION = "subscription"
    EMAIL = "email"
    PRIVACY = "privacy"
    APPEARANCE = "appearance"


@dataclass
class SettingItem:
    """Configuration for a single setting."""
    id: str
    label: str
    description: str
    type: str  # "text", "email", "password", "toggle", "select", "action"
    options: Optional[List[Dict[str, str]]] = None
    action_label: Optional[str] = None
    danger: bool = False


SETTINGS_CONFIG: Dict[SettingsCategory, List[SettingItem]] = {
    SettingsCategory.ACCOUNT: [
        SettingItem(
            id="email",
            label="Email address",
            description="Your login email",
            type="email",
        ),
        SettingItem(
            id="password",
            label="Password",
            description="Change your password",
            type="password",
            action_label="Change password",
        ),
        SettingItem(
            id="display_name",
            label="Display name",
            description="How others see you (required for Featured)",
            type="text",
        ),
        SettingItem(
            id="delete_account",
            label="Delete account",
            description="Permanently delete your account and data",
            type="action",
            action_label="Delete account",
            danger=True,
        ),
    ],
    SettingsCategory.PROFILE: [
        SettingItem(
            id="visibility",
            label="Profile visibility",
            description="Who can see your profile",
            type="select",
            options=[
                {"value": "private", "label": "Private"},
                {"value": "featured_only", "label": "Featured pages only"},
                {"value": "public", "label": "Public"},
            ],
        ),
        SettingItem(
            id="avatar",
            label="Avatar",
            description="Profile picture (optional)",
            type="action",
            action_label="Upload avatar",
        ),
        SettingItem(
            id="bio",
            label="Bio",
            description="Short description (optional, public profiles only)",
            type="text",
        ),
    ],
    SettingsCategory.SUBSCRIPTION: [
        SettingItem(
            id="current_plan",
            label="Current plan",
            description="Your subscription details",
            type="action",
            action_label="Manage subscription",
        ),
        SettingItem(
            id="billing",
            label="Billing",
            description="Payment method and invoices",
            type="action",
            action_label="Manage billing",
        ),
        SettingItem(
            id="upgrade",
            label="Upgrade",
            description="Get more features",
            type="action",
            action_label="View plans",
        ),
    ],
    SettingsCategory.EMAIL: [
        SettingItem(
            id="email_preferences",
            label="Email preferences",
            description="Control what emails you receive",
            type="action",
            action_label="Manage emails",
        ),
    ],
    SettingsCategory.PRIVACY: [
        SettingItem(
            id="voice_sharing",
            label="Share voice profile",
            description="Allow others to see your voice analysis",
            type="toggle",
        ),
        SettingItem(
            id="taste_sharing",
            label="Share reading taste",
            description="Allow others to see your reading preferences",
            type="toggle",
        ),
        SettingItem(
            id="export_data",
            label="Export data",
            description="Download all your data (JSON)",
            type="action",
            action_label="Export data",
        ),
    ],
    SettingsCategory.APPEARANCE: [
        SettingItem(
            id="timezone",
            label="Timezone",
            description="For email timing and streaks",
            type="select",
            options=[
                {"value": "America/Toronto", "label": "Eastern Time (Toronto)"},
                {"value": "America/Chicago", "label": "Central Time (Chicago)"},
                {"value": "America/Denver", "label": "Mountain Time (Denver)"},
                {"value": "America/Vancouver", "label": "Pacific Time (Vancouver)"},
                {"value": "Europe/London", "label": "UK Time (London)"},
                {"value": "Europe/Paris", "label": "Central European (Paris)"},
                {"value": "Australia/Sydney", "label": "Australian Eastern (Sydney)"},
                {"value": "Pacific/Auckland", "label": "New Zealand (Auckland)"},
            ],
        ),
        SettingItem(
            id="currency",
            label="Currency",
            description="For pricing display",
            type="select",
            options=[
                {"value": "cad", "label": "🇨🇦 CAD"},
                {"value": "gbp", "label": "🇬🇧 GBP"},
                {"value": "eur", "label": "🇪🇺 EUR"},
                {"value": "aud", "label": "🇦🇺 AUD"},
                {"value": "nzd", "label": "🇳🇿 NZD"},
            ],
        ),
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# EMPTY STATES
# ═══════════════════════════════════════════════════════════════════════════

EMPTY_STATES: Dict[DashboardSection, Dict[str, str]] = {
    DashboardSection.TODAY_PROGRESS: {
        "icon": "✍️",
        "title": "No writing yet today",
        "message": "Write your first 100 words to see your progress.",
        "cta": "Start writing",
        "cta_url": "/analyze",
    },
    DashboardSection.VOICE_SNAPSHOT: {
        "icon": "🎯",
        "title": "Discover your voice",
        "message": "Analyze some writing to see your unique voice profile.",
        "cta": "Analyze writing",
        "cta_url": "/analyze",
    },
    DashboardSection.MILESTONES: {
        "icon": "🏆",
        "title": "Your journey begins",
        "message": "Write 500 words to unlock your first milestone.",
        "cta": "Start writing",
        "cta_url": "/analyze",
    },
    DashboardSection.RECENT_ANALYSES: {
        "icon": "📝",
        "title": "No analyses yet",
        "message": "Your recent writing analyses will appear here.",
        "cta": "Analyze writing",
        "cta_url": "/analyze",
    },
    DashboardSection.FEATURED_STATUS: {
        "icon": "⭐",
        "title": "Path to Featured",
        "message": "Complete a 7-day 1K streak to become eligible.",
        "cta": "Learn more",
        "cta_url": "/featured",
    },
    DashboardSection.READING_ACTIVITY: {
        "icon": "📖",
        "title": "Start exploring",
        "message": "Read posts to discover your reading taste.",
        "cta": "Browse posts",
        "cta_url": "/explore",
    },
    DashboardSection.READING_TASTE: {
        "icon": "🎨",
        "title": "Discover your taste",
        "message": "Read a few posts to see your preference profile.",
        "cta": "Browse posts",
        "cta_url": "/explore",
    },
    DashboardSection.BOOKMARKS: {
        "icon": "🔖",
        "title": "No bookmarks yet",
        "message": "Save posts you want to revisit.",
        "cta": "Browse posts",
        "cta_url": "/explore",
    },
    DashboardSection.CURATOR_PROGRESS: {
        "icon": "📚",
        "title": "Start your curator journey",
        "message": "Read, explore, and curate to become Featured.",
        "cta": "Learn more",
        "cta_url": "/curator",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA EXPORT
# ═══════════════════════════════════════════════════════════════════════════

EXPORT_CONFIG = {
    "format": "json",
    "filename_template": "quirrely-export-{user_id}-{date}.json",
    "include": [
        "profile",
        "analyses",
        "milestones",
        "featured_submissions",
        "reading_history",
        "bookmarks",
        "preferences",
    ],
    "exclude": [
        "password_hash",
        "internal_ids",
        "admin_notes",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_sections_for_user(user_tier: str, features: List[str]) -> Dict[str, List[SectionConfig]]:
    """Get applicable dashboard sections for a user."""
    def filter_sections(sections: List[SectionConfig]) -> List[SectionConfig]:
        result = []
        for section in sections:
            # Check tier requirement
            if section.requires_tier and user_tier not in section.requires_tier:
                continue
            # Check feature requirement
            if section.requires_feature and section.requires_feature not in features:
                continue
            result.append(section)
        return result
    
    return {
        "writer": filter_sections(WRITER_SECTIONS),
        "reader": filter_sections(READER_SECTIONS),
    }


def get_empty_state(section: DashboardSection) -> Optional[Dict[str, str]]:
    """Get empty state content for a section."""
    return EMPTY_STATES.get(section)
