#!/usr/bin/env python3
"""
QUIRRELY ADMIN CONFIGURATION v1.0
Admin roles, permissions, and dashboard configuration.

Roles: Admin (full access), Moderator (Featured review only)
URL: /admin
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# ROLES & PERMISSIONS
# ═══════════════════════════════════════════════════════════════════════════

class AdminRole(str, Enum):
    ADMIN = "admin"           # Full access
    MODERATOR = "moderator"   # Featured review only


class Permission(str, Enum):
    # Overview
    VIEW_OVERVIEW = "view_overview"
    VIEW_METRICS = "view_metrics"
    
    # Users
    VIEW_USERS = "view_users"
    EDIT_USER = "edit_user"
    CHANGE_TIER = "change_tier"
    GRANT_TRIAL = "grant_trial"
    SUSPEND_USER = "suspend_user"
    DELETE_USER = "delete_user"
    IMPERSONATE_USER = "impersonate_user"
    
    # Subscriptions
    VIEW_SUBSCRIPTIONS = "view_subscriptions"
    REFUND_PAYMENT = "refund_payment"  # Even though no refunds policy, keep for edge cases
    
    # Featured
    VIEW_FEATURED_QUEUE = "view_featured_queue"
    REVIEW_FEATURED = "review_featured"
    APPROVE_FEATURED = "approve_featured"
    REJECT_FEATURED = "reject_featured"
    
    # Content
    VIEW_CONTENT = "view_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    
    # System
    VIEW_SYSTEM = "view_system"
    VIEW_LOGS = "view_logs"
    VIEW_ERRORS = "view_errors"
    
    # Admin
    MANAGE_ADMINS = "manage_admins"
    VIEW_AUDIT_LOG = "view_audit_log"


ROLE_PERMISSIONS: Dict[AdminRole, Set[Permission]] = {
    AdminRole.ADMIN: set(Permission),  # All permissions
    
    AdminRole.MODERATOR: {
        Permission.VIEW_OVERVIEW,
        Permission.VIEW_FEATURED_QUEUE,
        Permission.REVIEW_FEATURED,
        Permission.APPROVE_FEATURED,
        Permission.REJECT_FEATURED,
        Permission.VIEW_USERS,  # Read-only
    },
}


def has_permission(role: AdminRole, permission: Permission) -> bool:
    """Check if role has permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD SECTIONS
# ═══════════════════════════════════════════════════════════════════════════

class AdminSection(str, Enum):
    OVERVIEW = "overview"
    USERS = "users"
    SUBSCRIPTIONS = "subscriptions"
    FEATURED = "featured"
    CONTENT = "content"
    SYSTEM = "system"


@dataclass
class SectionConfig:
    """Configuration for an admin section."""
    id: AdminSection
    label: str
    icon: str
    required_permission: Permission
    

ADMIN_SECTIONS: List[SectionConfig] = [
    SectionConfig(
        id=AdminSection.OVERVIEW,
        label="Overview",
        icon="📊",
        required_permission=Permission.VIEW_OVERVIEW,
    ),
    SectionConfig(
        id=AdminSection.USERS,
        label="Users",
        icon="👥",
        required_permission=Permission.VIEW_USERS,
    ),
    SectionConfig(
        id=AdminSection.SUBSCRIPTIONS,
        label="Subscriptions",
        icon="💳",
        required_permission=Permission.VIEW_SUBSCRIPTIONS,
    ),
    SectionConfig(
        id=AdminSection.FEATURED,
        label="Featured Review",
        icon="⭐",
        required_permission=Permission.VIEW_FEATURED_QUEUE,
    ),
    SectionConfig(
        id=AdminSection.CONTENT,
        label="Content",
        icon="📝",
        required_permission=Permission.VIEW_CONTENT,
    ),
    SectionConfig(
        id=AdminSection.SYSTEM,
        label="System",
        icon="⚙️",
        required_permission=Permission.VIEW_SYSTEM,
    ),
]


def get_sections_for_role(role: AdminRole) -> List[SectionConfig]:
    """Get admin sections accessible to a role."""
    return [
        section for section in ADMIN_SECTIONS
        if has_permission(role, section.required_permission)
    ]


# ═══════════════════════════════════════════════════════════════════════════
# USER ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

class UserAction(str, Enum):
    VIEW = "view"
    CHANGE_TIER = "change_tier"
    GRANT_TRIAL = "grant_trial"
    SUSPEND = "suspend"
    UNSUSPEND = "unsuspend"
    DELETE = "delete"
    IMPERSONATE = "impersonate"


USER_ACTION_PERMISSIONS: Dict[UserAction, Permission] = {
    UserAction.VIEW: Permission.VIEW_USERS,
    UserAction.CHANGE_TIER: Permission.CHANGE_TIER,
    UserAction.GRANT_TRIAL: Permission.GRANT_TRIAL,
    UserAction.SUSPEND: Permission.SUSPEND_USER,
    UserAction.UNSUSPEND: Permission.SUSPEND_USER,
    UserAction.DELETE: Permission.DELETE_USER,
    UserAction.IMPERSONATE: Permission.IMPERSONATE_USER,
}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED REVIEW
# ═══════════════════════════════════════════════════════════════════════════

class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    ESCALATE = "escalate"


@dataclass
class ReviewDecision:
    """A Featured review decision."""
    action: ReviewAction
    submission_id: str
    reviewer_id: str
    feedback: Optional[str] = None
    escalation_reason: Optional[str] = None
    decided_at: datetime = None
    
    def __post_init__(self):
        if self.decided_at is None:
            self.decided_at = datetime.utcnow()


REJECTION_REASONS = [
    "Does not meet word count requirement (max 500 words)",
    "Writing sample does not demonstrate consistent voice",
    "Keystroke verification failed",
    "Agreements not properly acknowledged",
    "Content violates community guidelines",
    "Other (please specify)",
]


# ═══════════════════════════════════════════════════════════════════════════
# AUDIT LOGGING
# ═══════════════════════════════════════════════════════════════════════════

class AuditAction(str, Enum):
    # User actions
    USER_VIEWED = "user_viewed"
    USER_TIER_CHANGED = "user_tier_changed"
    USER_TRIAL_GRANTED = "user_trial_granted"
    USER_SUSPENDED = "user_suspended"
    USER_UNSUSPENDED = "user_unsuspended"
    USER_DELETED = "user_deleted"
    USER_IMPERSONATED = "user_impersonated"
    
    # Featured actions
    SUBMISSION_REVIEWED = "submission_reviewed"
    SUBMISSION_APPROVED = "submission_approved"
    SUBMISSION_REJECTED = "submission_rejected"
    SUBMISSION_ESCALATED = "submission_escalated"
    
    # Content actions
    CONTENT_EDITED = "content_edited"
    CONTENT_DELETED = "content_deleted"
    
    # Admin actions
    ADMIN_CREATED = "admin_created"
    ADMIN_REMOVED = "admin_removed"
    ADMIN_ROLE_CHANGED = "admin_role_changed"


@dataclass
class AuditLogEntry:
    """An audit log entry."""
    action: AuditAction
    admin_id: str
    admin_email: str
    target_type: str  # "user", "submission", "content", "admin"
    target_id: str
    details: Dict
    ip_address: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# ═══════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════

class AdminNotificationType(str, Enum):
    NEW_FEATURED_SUBMISSION = "new_featured_submission"
    PAYMENT_FAILURE_SPIKE = "payment_failure_spike"
    ERROR_RATE_SPIKE = "error_rate_spike"
    AUTHORITY_ELIGIBLE = "authority_eligible"
    ESCALATED_SUBMISSION = "escalated_submission"


NOTIFICATION_THRESHOLDS = {
    AdminNotificationType.PAYMENT_FAILURE_SPIKE: {
        "count": 5,
        "window_minutes": 60,
    },
    AdminNotificationType.ERROR_RATE_SPIKE: {
        "count": 10,
        "window_minutes": 1,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════════════════════════════

OVERVIEW_METRICS = [
    # Real-time
    {"id": "total_users", "label": "Total Users", "type": "count"},
    {"id": "active_subscriptions", "label": "Active Subscriptions", "type": "count"},
    {"id": "mrr", "label": "MRR", "type": "currency"},
    {"id": "active_trials", "label": "Active Trials", "type": "count"},
    
    # Today
    {"id": "signups_today", "label": "Signups Today", "type": "count"},
    {"id": "analyses_today", "label": "Analyses Today", "type": "count"},
    {"id": "words_today", "label": "Words Analyzed Today", "type": "count"},
    
    # Pending
    {"id": "pending_submissions", "label": "Pending Reviews", "type": "count"},
    {"id": "pending_escalations", "label": "Escalations", "type": "count"},
]

SUBSCRIPTION_METRICS = [
    {"id": "total_mrr", "label": "Monthly Recurring Revenue", "type": "currency"},
    {"id": "total_arr", "label": "Annual Run Rate", "type": "currency"},
    {"id": "pro_subscribers", "label": "PRO Subscribers", "type": "count"},
    {"id": "curator_subscribers", "label": "Curator Subscribers", "type": "count"},
    {"id": "bundle_subscribers", "label": "Bundle Subscribers", "type": "count"},
    {"id": "trial_conversion_rate", "label": "Trial Conversion", "type": "percent"},
    {"id": "churn_rate", "label": "Monthly Churn", "type": "percent"},
]


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def can_perform_user_action(role: AdminRole, action: UserAction) -> bool:
    """Check if role can perform user action."""
    required = USER_ACTION_PERMISSIONS.get(action)
    return required and has_permission(role, required)


def get_available_user_actions(role: AdminRole) -> List[UserAction]:
    """Get user actions available to a role."""
    return [
        action for action in UserAction
        if can_perform_user_action(role, action)
    ]
