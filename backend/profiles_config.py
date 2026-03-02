#!/usr/bin/env python3
"""
QUIRRELY PUBLIC PROFILES CONFIGURATION v1.0
Profile URLs, usernames, visibility, and social sharing.

URL: /@username
Privacy: Private by default
"""

import re
from typing import List, Optional, Set
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# URL STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════

PROFILE_URL_PREFIX = "/@"  # /@username


def get_profile_url(username: str) -> str:
    """Generate profile URL for username."""
    return f"{PROFILE_URL_PREFIX}{username.lower()}"


def parse_profile_url(url: str) -> Optional[str]:
    """Extract username from profile URL."""
    if url.startswith(PROFILE_URL_PREFIX):
        return url[len(PROFILE_URL_PREFIX):].lower()
    return None


# ═══════════════════════════════════════════════════════════════════════════
# USERNAME REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
USERNAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
USERNAME_CHANGE_COOLDOWN_DAYS = 30

# Reserved usernames (cannot be registered)
RESERVED_USERNAMES: Set[str] = {
    # Brand
    "quirrely", "quirrel", "squirrel",
    
    # Admin/System
    "admin", "administrator", "support", "help", "info",
    "system", "root", "mod", "moderator",
    
    # Features
    "featured", "authority", "writer", "curator", "reader",
    "blog", "explore", "discover", "search",
    
    # Pages
    "settings", "dashboard", "profile", "account",
    "login", "signup", "register", "logout",
    "pricing", "subscribe", "billing",
    
    # API
    "api", "webhook", "callback",
    
    # Legal
    "terms", "privacy", "legal", "dmca", "copyright",
    
    # Other
    "null", "undefined", "anonymous", "guest", "user",
}


@dataclass
class UsernameValidation:
    """Result of username validation."""
    valid: bool
    error: Optional[str] = None


def validate_username(username: str) -> UsernameValidation:
    """Validate a username."""
    if not username:
        return UsernameValidation(False, "Username is required")
    
    username_lower = username.lower()
    
    if len(username) < USERNAME_MIN_LENGTH:
        return UsernameValidation(False, f"Username must be at least {USERNAME_MIN_LENGTH} characters")
    
    if len(username) > USERNAME_MAX_LENGTH:
        return UsernameValidation(False, f"Username must be at most {USERNAME_MAX_LENGTH} characters")
    
    if not USERNAME_PATTERN.match(username):
        return UsernameValidation(False, "Username must start with a letter and contain only letters, numbers, and underscores")
    
    if username_lower in RESERVED_USERNAMES:
        return UsernameValidation(False, "This username is reserved")
    
    return UsernameValidation(True)


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════

class ProfileVisibility(str, Enum):
    PRIVATE = "private"           # Only owner sees
    FEATURED_ONLY = "featured_only"  # On Featured pages only
    PUBLIC = "public"             # Anyone with link


DEFAULT_VISIBILITY = ProfileVisibility.PRIVATE


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE CONTENT
# ═══════════════════════════════════════════════════════════════════════════

BIO_MAX_LENGTH = 160

@dataclass
class PublicProfileContent:
    """What's shown on a public profile."""
    # Always visible
    display_name: str
    username: str
    join_date: str
    
    # Optional
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    # Voice (if sharing enabled)
    voice_profile_type: Optional[str] = None
    voice_stance: Optional[str] = None
    voice_traits: Optional[List[str]] = None
    
    # Reading taste (if sharing enabled)
    reading_taste_type: Optional[str] = None
    
    # Recognition
    is_featured_writer: bool = False
    is_featured_curator: bool = False
    is_authority_writer: bool = False
    is_authority_curator: bool = False
    
    # Featured content
    featured_pieces: Optional[List[dict]] = None  # Writer's Featured pieces
    curated_paths: Optional[List[dict]] = None    # Curator's paths


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED SHOWCASE PAGES
# ═══════════════════════════════════════════════════════════════════════════

SHOWCASE_PAGES = {
    "featured": {
        "path": "/featured",
        "title": "Featured on Quirrely",
        "description": "Discover writers and curators recognized for their exceptional work.",
    },
    "featured_writers": {
        "path": "/featured/writers",
        "title": "Featured Writers",
        "description": "Writers recognized for their consistent voice and dedication.",
    },
    "featured_curators": {
        "path": "/featured/curators",
        "title": "Featured Curators",
        "description": "Curators recognized for their exceptional reading taste.",
    },
    "authority": {
        "path": "/featured/authority",
        "title": "Authority Members",
        "description": "The most distinguished voices on Quirrely.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# SOCIAL SHARING
# ═══════════════════════════════════════════════════════════════════════════

class SharePlatform(str, Enum):
    COPY_LINK = "copy_link"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    EMAIL = "email"
    # Note: X/Twitter explicitly excluded


SHARE_PLATFORMS = [
    SharePlatform.COPY_LINK,
    SharePlatform.LINKEDIN,
    SharePlatform.FACEBOOK,
    SharePlatform.EMAIL,
]


def get_share_url(platform: SharePlatform, profile_url: str, title: str) -> str:
    """Generate share URL for platform."""
    encoded_url = profile_url.replace(":", "%3A").replace("/", "%2F")
    encoded_title = title.replace(" ", "%20")
    
    if platform == SharePlatform.LINKEDIN:
        return f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"
    
    elif platform == SharePlatform.FACEBOOK:
        return f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    
    elif platform == SharePlatform.EMAIL:
        return f"mailto:?subject={encoded_title}&body=Check%20out%20this%20profile%20on%20Quirrely%3A%20{encoded_url}"
    
    return profile_url


# ═══════════════════════════════════════════════════════════════════════════
# OPEN GRAPH / SEO
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_OG_IMAGE = "https://quirrely.com/og-default.png"

@dataclass
class OpenGraphTags:
    """Open Graph meta tags for profile."""
    title: str
    description: str
    image: str
    url: str
    type: str = "profile"
    site_name: str = "Quirrely"


def generate_og_tags(profile: PublicProfileContent, profile_url: str) -> OpenGraphTags:
    """Generate Open Graph tags for profile."""
    # Title
    title = f"{profile.display_name} on Quirrely"
    
    # Description
    if profile.bio:
        description = profile.bio
    elif profile.voice_profile_type:
        description = f"{profile.voice_profile_type} • Discover their unique voice on Quirrely"
    else:
        description = "Discover this writer's unique voice on Quirrely"
    
    # Image
    image = profile.avatar_url or DEFAULT_OG_IMAGE
    
    return OpenGraphTags(
        title=title,
        description=description,
        image=image,
        url=f"https://quirrely.com{profile_url}",
    )


def get_robots_directive(visibility: ProfileVisibility) -> str:
    """Get robots meta directive based on visibility."""
    if visibility == ProfileVisibility.PUBLIC:
        return "index, follow"
    return "noindex, nofollow"


# ═══════════════════════════════════════════════════════════════════════════
# BADGES
# ═══════════════════════════════════════════════════════════════════════════

BADGES = {
    "featured_writer": {
        "icon": "⭐",
        "label": "Featured Writer",
        "color": "#D4A574",
    },
    "featured_curator": {
        "icon": "⭐",
        "label": "Featured Curator",
        "color": "#D4A574",
    },
    "authority_writer": {
        "icon": "👑",
        "label": "Authority Writer",
        "color": "#FFD700",
    },
    "authority_curator": {
        "icon": "👑",
        "label": "Authority Curator",
        "color": "#FFD700",
    },
    "voice_and_taste": {
        "icon": "🏆",
        "label": "Voice & Taste",
        "color": "#FF6B6B",
    },
    "authority_voice_and_taste": {
        "icon": "💎",
        "label": "Authority Voice & Taste",
        "color": "#6C5CE7",
    },
}


def get_badges(profile: PublicProfileContent) -> List[dict]:
    """Get badges for profile."""
    badges = []
    
    # Authority takes precedence over Featured
    if profile.is_authority_writer and profile.is_authority_curator:
        badges.append(BADGES["authority_voice_and_taste"])
    elif profile.is_authority_writer:
        badges.append(BADGES["authority_writer"])
    elif profile.is_authority_curator:
        badges.append(BADGES["authority_curator"])
    elif profile.is_featured_writer and profile.is_featured_curator:
        badges.append(BADGES["voice_and_taste"])
    else:
        if profile.is_featured_writer:
            badges.append(BADGES["featured_writer"])
        if profile.is_featured_curator:
            badges.append(BADGES["featured_curator"])
    
    return badges
