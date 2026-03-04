#!/usr/bin/env python3
"""
QUIRRELY AUTHENTICATION CONFIGURATION v1.0
Supabase Auth setup and configuration.

Auth Methods:
- Email/password
- Magic link
- Google OAuth

Social Logins:
- Google only (NEVER Apple)

Password Policy:
- 12+ characters OR 8+ with complexity
- Passphrase encouraged
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "your-anon-key")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "your-service-key")

# OAuth providers
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID", "")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET", "")
LINKEDIN_CLIENT_ID = os.environ.get("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")

OAUTH_REDIRECT_BASE = os.environ.get("APP_URL", "https://quirrely.ca")

OAUTH_PROVIDERS = {
    "google": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": "openid email profile",
    },
    "facebook": {
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "userinfo_url": "https://graph.facebook.com/v18.0/me?fields=id,name,email,picture",
        "scopes": "email,public_profile",
    },
    "linkedin": {
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/userinfo",
        "scopes": "openid profile email",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# AUTH METHODS
# ═══════════════════════════════════════════════════════════════════════════

class AuthMethod(str, Enum):
    EMAIL_PASSWORD = "email_password"
    MAGIC_LINK = "magic_link"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"


ENABLED_AUTH_METHODS = [
    AuthMethod.EMAIL_PASSWORD,
    AuthMethod.MAGIC_LINK,
    AuthMethod.GOOGLE,
    AuthMethod.FACEBOOK,
    AuthMethod.LINKEDIN,
]

SOCIAL_PROVIDERS = ["google", "facebook", "linkedin"]


# ═══════════════════════════════════════════════════════════════════════════
# PASSWORD POLICY
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PasswordPolicy:
    """
    Password requirements:
    - 12+ characters (passphrase style), OR
    - 8+ characters with complexity (number + uppercase)
    
    Passphrase encouraged for better security + memorability.
    """
    min_length_simple: int = 12  # No complexity required
    min_length_complex: int = 8   # With complexity requirements
    require_uppercase: bool = True  # For complex passwords
    require_lowercase: bool = True  # For complex passwords
    require_number: bool = True     # For complex passwords
    require_symbol: bool = False    # Not required (too annoying)
    max_length: int = 128           # Reasonable upper limit
    
    def validate(self, password: str) -> Dict[str, Any]:
        """Validate password against policy."""
        length = len(password)
        
        if length > self.max_length:
            return {
                "valid": False,
                "error": f"Password must be {self.max_length} characters or fewer",
            }
        
        # Option 1: 12+ characters (passphrase) - no complexity needed
        if length >= self.min_length_simple:
            return {
                "valid": True,
                "strength": "strong",
                "message": "Great passphrase!",
            }
        
        # Option 2: 8+ characters with complexity
        if length >= self.min_length_complex:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_number = any(c.isdigit() for c in password)
            
            missing = []
            if self.require_uppercase and not has_upper:
                missing.append("uppercase letter")
            if self.require_lowercase and not has_lower:
                missing.append("lowercase letter")
            if self.require_number and not has_number:
                missing.append("number")
            
            if missing:
                return {
                    "valid": False,
                    "error": f"Password needs: {', '.join(missing)}",
                    "suggestion": "Or use 12+ characters for a passphrase",
                }
            
            return {
                "valid": True,
                "strength": "good",
                "message": "Password meets requirements",
            }
        
        # Too short
        return {
            "valid": False,
            "error": f"Password must be at least {self.min_length_complex} characters",
            "suggestion": f"Try a passphrase with {self.min_length_simple}+ characters",
        }
    
    def get_strength(self, password: str) -> Dict[str, Any]:
        """Get password strength for UI meter."""
        length = len(password)
        
        if length == 0:
            return {"score": 0, "label": "", "color": "#E9ECEF"}
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_number = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        
        # Calculate score
        score = 0
        score += min(length / 4, 3)  # Up to 3 points for length
        score += 1 if has_upper else 0
        score += 1 if has_lower else 0
        score += 1 if has_number else 0
        score += 1 if has_symbol else 0
        score += 1 if length >= 12 else 0
        score += 1 if length >= 16 else 0
        
        # Normalize to 0-4 scale
        normalized = min(int(score / 2.5), 4)
        
        labels = ["Weak", "Fair", "Good", "Strong", "Excellent"]
        colors = ["#E74C3C", "#E67E22", "#F1C40F", "#2ECC71", "#27AE60"]
        
        return {
            "score": normalized,
            "label": labels[normalized],
            "color": colors[normalized],
        }


PASSWORD_POLICY = PasswordPolicy()


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

EMAIL_VERIFICATION_CONFIG = {
    # Required before these actions
    "required_for": [
        "subscribe",        # Must verify before paying
        "start_trial",      # Must verify before trial
        "submit_featured",  # Must verify before Featured submission
    ],
    
    # Not required for these (can do unverified)
    "not_required_for": [
        "browse",           # Can browse FREE content
        "analyze_free",     # Can use FREE tier analysis
        "save_preferences", # Can save settings
    ],
    
    # Verification email settings
    "email_subject": "Verify your Quirrely account",
    "link_expires_hours": 24,
    "resend_cooldown_seconds": 60,
}


# ═══════════════════════════════════════════════════════════════════════════
# DISPLAY NAME
# ═══════════════════════════════════════════════════════════════════════════

DISPLAY_NAME_CONFIG = {
    # When is it required?
    "required_for": [
        "featured_writer_submission",
        "featured_curator_submission",
        "public_profile",
    ],
    
    # Validation rules
    "min_length": 2,
    "max_length": 50,
    "allowed_characters": "letters, numbers, spaces, hyphens, underscores",
    "reserved_names": [
        "admin", "quirrely", "support", "help", "system",
        "moderator", "mod", "staff", "official",
    ],
}


def validate_display_name(name: str) -> Dict[str, Any]:
    """Validate display name."""
    import re
    
    if not name or len(name.strip()) == 0:
        return {"valid": False, "error": "Display name is required"}
    
    name = name.strip()
    
    if len(name) < DISPLAY_NAME_CONFIG["min_length"]:
        return {"valid": False, "error": f"Must be at least {DISPLAY_NAME_CONFIG['min_length']} characters"}
    
    if len(name) > DISPLAY_NAME_CONFIG["max_length"]:
        return {"valid": False, "error": f"Must be {DISPLAY_NAME_CONFIG['max_length']} characters or fewer"}
    
    # Only allow letters, numbers, spaces, hyphens, underscores
    if not re.match(r'^[\w\s\-]+$', name, re.UNICODE):
        return {"valid": False, "error": "Only letters, numbers, spaces, hyphens, and underscores allowed"}
    
    # Check reserved names
    if name.lower() in DISPLAY_NAME_CONFIG["reserved_names"]:
        return {"valid": False, "error": "This name is reserved"}
    
    return {"valid": True}


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════

class ProfileVisibility(str, Enum):
    PRIVATE = "private"      # Only visible to user
    PUBLIC = "public"        # Visible to everyone
    FEATURED_ONLY = "featured_only"  # Visible only on Featured pages


PROFILE_VISIBILITY_CONFIG = {
    "default": ProfileVisibility.PRIVATE,
    
    # What's visible at each level
    "visibility_levels": {
        ProfileVisibility.PRIVATE: [],
        ProfileVisibility.FEATURED_ONLY: [
            "display_name",
            "featured_work",  # Featured piece/path only
        ],
        ProfileVisibility.PUBLIC: [
            "display_name",
            "featured_work",
            "badges",
            "member_since",
            "voice_profile",  # If opted in
            "reading_taste",  # If opted in
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# ACCOUNT DELETION
# ═══════════════════════════════════════════════════════════════════════════

ACCOUNT_DELETION_CONFIG = {
    # Soft delete (default)
    "soft_delete": {
        "enabled": True,
        "recovery_days": 30,  # Can recover within 30 days
        "data_retained": True,
    },
    
    # Hard delete (on request)
    "hard_delete": {
        "enabled": True,
        "confirmation_required": True,
        "confirmation_phrase": "DELETE MY ACCOUNT",
        "cooldown_hours": 24,  # Must wait 24h after requesting
    },
    
    # What gets deleted
    "soft_delete_actions": [
        "deactivate_account",
        "cancel_subscriptions",
        "hide_public_profile",
        "anonymize_featured_work",  # Replace name with "Former Member"
    ],
    
    "hard_delete_actions": [
        "delete_user_record",
        "delete_analyses",
        "delete_milestones",
        "delete_bookmarks",
        "delete_payment_history",  # Keep invoice records for legal
        "anonymize_featured_work",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

SESSION_CONFIG = {
    # Multi-session (unlimited devices)
    "max_sessions": None,  # Unlimited
    
    # Session duration
    "session_lifetime_hours": 24 * 7,  # 7 days
    "refresh_token_lifetime_days": 30,
    
    # Security
    "invalidate_on_password_change": True,
    "invalidate_on_email_change": True,
}


# ═══════════════════════════════════════════════════════════════════════════
# SIGN-UP FIELDS
# ═══════════════════════════════════════════════════════════════════════════

SIGNUP_FIELDS = {
    "required": [
        "email",
    ],
    "optional": [
        "password",      # Not required if using magic link
        "display_name",  # Can set later
    ],
    "auto_detected": [
        "country",       # From IP for currency
        "timezone",      # From browser
        "preferred_currency",  # From country
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# SUPABASE AUTH CONFIG (for dashboard setup)
# ═══════════════════════════════════════════════════════════════════════════

SUPABASE_AUTH_CONFIG = """
# Supabase Dashboard Settings

## Authentication > Providers

### Email
- Enable Email provider: YES
- Confirm email: YES
- Secure email change: YES
- Enable magic link: YES

### Google
- Enable Google provider: YES
- Client ID: (from Google Cloud Console)
- Client Secret: (from Google Cloud Console)

### Apple
- Enable Apple provider: NO (NEVER)

## Authentication > URL Configuration
- Site URL: https://quirrely.com
- Redirect URLs:
  - https://quirrely.com/auth/callback
  - https://quirrely.com/auth/confirm
  - http://localhost:3000/auth/callback (dev)

## Authentication > Email Templates
- Customize for Quirrely branding

## Authentication > Rate Limits
- Sign-ups per hour: 100
- Token refreshes per hour: 1000
- Magic links per hour: 50
"""


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def requires_email_verification(action: str) -> bool:
    """Check if an action requires email verification."""
    return action in EMAIL_VERIFICATION_CONFIG["required_for"]


def requires_display_name(action: str) -> bool:
    """Check if an action requires display name."""
    return action in DISPLAY_NAME_CONFIG["required_for"]


def get_visible_fields(visibility: ProfileVisibility) -> list:
    """Get fields visible at a given visibility level."""
    return PROFILE_VISIBILITY_CONFIG["visibility_levels"].get(visibility, [])
