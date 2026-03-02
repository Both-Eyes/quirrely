#!/usr/bin/env python3
"""
QUIRRELY EMAIL SERVICE v1.0
Resend integration for sending emails.

Features:
- Template rendering
- User timezone handling
- Analytics tracking
- Preference checking
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx

from email_config import (
    RESEND_API_KEY,
    FROM_EMAIL,
    FROM_EMAIL_NOREPLY,
    SUPPORT_EMAIL,
    BRAND,
    EmailType,
    EmailCategory,
    EMAIL_TEMPLATES,
    EMAIL_CATEGORIES,
    EmailPreferences,
    DEFAULT_PREFERENCES,
    ANALYTICS_CONFIG,
    get_template,
    is_transactional,
    get_unsubscribe_url,
    get_preferences_url,
)


# ═══════════════════════════════════════════════════════════════════════════
# RESEND CLIENT
# ═══════════════════════════════════════════════════════════════════════════

RESEND_API_URL = "https://api.resend.com"


async def send_email_via_resend(
    to: str,
    subject: str,
    html: str,
    from_email: str = FROM_EMAIL_NOREPLY,
    reply_to: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Send email via Resend API."""
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "from": from_email,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    
    if reply_to:
        payload["reply_to"] = reply_to
    
    if tags:
        payload["tags"] = [{"name": k, "value": v} for k, v in tags.items()]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{RESEND_API_URL}/emails",
            headers=headers,
            json=payload,
        )
        
        return response.json()


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL SERVICE
# ═══════════════════════════════════════════════════════════════════════════

class EmailService:
    """Service for sending Quirrely emails."""
    
    def __init__(self):
        self._preferences_cache: Dict[str, EmailPreferences] = {}
    
    async def send(
        self,
        email_type: EmailType,
        to_email: str,
        user_id: str,
        data: Optional[Dict[str, Any]] = None,
        preferences: Optional[EmailPreferences] = None,
    ) -> Dict[str, Any]:
        """Send an email of the specified type."""
        template = get_template(email_type)
        if not template:
            return {"success": False, "error": "Template not found"}
        
        # Check preferences
        prefs = preferences or self._get_preferences(user_id)
        if not prefs.can_receive(email_type):
            return {"success": False, "error": "User unsubscribed", "skipped": True}
        
        # Render template
        data = data or {}
        data["brand"] = BRAND
        data["support_email"] = SUPPORT_EMAIL
        data["current_year"] = datetime.utcnow().year
        
        # Add unsubscribe links for non-transactional
        if not is_transactional(email_type):
            category = EMAIL_CATEGORIES.get(email_type)
            data["unsubscribe_url"] = get_unsubscribe_url(user_id, category)
            data["preferences_url"] = get_preferences_url(user_id)
        
        # Render subject and HTML
        subject = self._render_string(template.subject, data)
        html = self._render_html(email_type, data)
        
        # Send via Resend
        result = await send_email_via_resend(
            to=to_email,
            subject=subject,
            html=html,
            from_email=template.from_email,
            reply_to=template.reply_to,
            tags={
                "email_type": email_type.value,
                "user_id": user_id,
            },
        )
        
        # Log send
        await self._log_send(user_id, email_type, to_email, result)
        
        return {"success": True, "result": result}
    
    def _get_preferences(self, user_id: str) -> EmailPreferences:
        """Get user email preferences."""
        # Would fetch from database
        return self._preferences_cache.get(user_id, DEFAULT_PREFERENCES)
    
    def _render_string(self, template: str, data: Dict[str, Any]) -> str:
        """Simple string template rendering."""
        result = template
        for key, value in data.items():
            if isinstance(value, str):
                result = result.replace(f"{{{key}}}", value)
        return result
    
    def _render_html(self, email_type: EmailType, data: Dict[str, Any]) -> str:
        """Render HTML email template."""
        # In production, would use React Email rendered templates
        # For now, use simple HTML templates
        return TEMPLATES.get(email_type, self._default_template)(data)
    
    async def _log_send(
        self,
        user_id: str,
        email_type: EmailType,
        to_email: str,
        result: Dict[str, Any],
    ):
        """Log email send for analytics."""
        # Would save to database
        pass


# ═══════════════════════════════════════════════════════════════════════════
# HTML TEMPLATES (Simple versions - would use React Email in production)
# ═══════════════════════════════════════════════════════════════════════════

def _base_template(content: str, data: Dict[str, Any]) -> str:
    """Base email template wrapper."""
    brand = data.get("brand", BRAND)
    unsubscribe_html = ""
    
    if data.get("unsubscribe_url"):
        unsubscribe_html = f"""
        <p style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #E9ECEF; font-size: 12px; color: #636E72;">
            <a href="{data['preferences_url']}" style="color: #636E72;">Email preferences</a> · 
            <a href="{data['unsubscribe_url']}" style="color: #636E72;">Unsubscribe</a>
        </p>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: {brand['colors']['background']}; margin: 0; padding: 40px 20px;">
    <div style="max-width: 560px; margin: 0 auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="text-align: center; margin-bottom: 32px;">
            <span style="font-size: 32px;">🐿️</span>
        </div>
        
        {content}
        
        <p style="margin-top: 32px; font-size: 14px; color: #636E72;">
            Questions? Reply to this email or contact <a href="mailto:{data.get('support_email', SUPPORT_EMAIL)}" style="color: {brand['colors']['primary']};">{data.get('support_email', SUPPORT_EMAIL)}</a>
        </p>
        
        {unsubscribe_html}
        
        <p style="margin-top: 16px; font-size: 12px; color: #636E72; text-align: center;">
            © {data.get('current_year', 2026)} Quirrely
        </p>
    </div>
</body>
</html>
"""


def _welcome_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Welcome to Quirrely! 🐿️
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Your voice matters. We're excited to help you discover it.
        </p>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Quirrely analyzes your writing to reveal your unique voice — the patterns, 
            rhythms, and style that make your words distinctly yours.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{brand['website_url']}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Start Writing →
            </a>
        </div>
        <p style="font-size: 14px; color: {brand['colors']['muted']};">
            Here's what you can do:
        </p>
        <ul style="font-size: 14px; color: {brand['colors']['text']}; line-height: 1.8;">
            <li>Analyze up to 500 words per day (FREE)</li>
            <li>Discover your voice profile</li>
            <li>Track your writing streaks</li>
        </ul>
    """
    return _base_template(content, data)


def _email_verification_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    verify_url = data.get("verify_url", "#")
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Verify your email
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Click the button below to verify your email address.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{verify_url}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Verify Email
            </a>
        </div>
        <p style="font-size: 14px; color: {brand['colors']['muted']};">
            This link expires in 24 hours. If you didn't create a Quirrely account, you can ignore this email.
        </p>
    """
    return _base_template(content, data)


def _magic_link_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    magic_url = data.get("magic_url", "#")
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Your login link
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Click the button below to sign in to Quirrely.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{magic_url}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Sign In
            </a>
        </div>
        <p style="font-size: 14px; color: {brand['colors']['muted']};">
            This link expires in 1 hour and can only be used once.
        </p>
    """
    return _base_template(content, data)


def _password_reset_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    reset_url = data.get("reset_url", "#")
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Reset your password
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Click the button below to reset your password.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{reset_url}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Reset Password
            </a>
        </div>
        <p style="font-size: 14px; color: {brand['colors']['muted']};">
            This link expires in 1 hour. If you didn't request this, you can ignore this email.
        </p>
    """
    return _base_template(content, data)


def _subscription_confirmed_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    tier_name = data.get("tier_name", "PRO")
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Welcome to {tier_name}! 🎉
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            Your subscription is now active. Thank you for supporting Quirrely.
        </p>
        <div style="margin: 24px 0; padding: 20px; background: {brand['colors']['background']}; border-radius: 8px;">
            <p style="margin: 0; font-size: 14px; color: {brand['colors']['muted']};">Plan</p>
            <p style="margin: 4px 0 0 0; font-size: 18px; font-weight: 600; color: {brand['colors']['text']};">{tier_name}</p>
        </div>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{brand['website_url']}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Start Exploring →
            </a>
        </div>
    """
    return _base_template(content, data)


def _payment_failed_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    update_url = data.get("update_url", "#")
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Payment failed
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            We couldn't process your payment. Please update your payment method to keep your subscription active.
        </p>
        <p style="font-size: 14px; color: {brand['colors']['muted']}; line-height: 1.6;">
            You have 2 days to update your payment before your subscription is cancelled.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{update_url}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Update Payment Method
            </a>
        </div>
    """
    return _base_template(content, data)


def _streak_at_risk_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    streak_days = data.get("streak_days", 0)
    content = f"""
        <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
            Don't break your streak! 🔥
        </h1>
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            You're on a <strong>{streak_days}-day streak</strong>. Write today to keep it alive.
        </p>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{brand['website_url']}" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                Write Now →
            </a>
        </div>
        <p style="font-size: 14px; color: {brand['colors']['muted']};">
            Even 100 words keeps the streak going.
        </p>
    """
    return _base_template(content, data)


def _milestone_achieved_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    milestone_name = data.get("milestone_name", "Milestone")
    milestone_icon = data.get("milestone_icon", "🏆")
    content = f"""
        <div style="text-align: center;">
            <div style="font-size: 64px; margin-bottom: 16px;">{milestone_icon}</div>
            <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
                {milestone_name}
            </h1>
            <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
                You've achieved something special. Keep going!
            </p>
        </div>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{brand['website_url']}/milestones" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['primary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                View All Milestones
            </a>
        </div>
    """
    return _base_template(content, data)


def _featured_accepted_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    featured_type = data.get("featured_type", "Writer")
    content = f"""
        <div style="text-align: center;">
            <div style="font-size: 64px; margin-bottom: 16px;">⭐</div>
            <h1 style="font-size: 24px; color: {brand['colors']['text']}; margin: 0 0 16px 0;">
                You're now a Featured {featured_type}!
            </h1>
            <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
                Congratulations! Your work will be showcased on Quirrely for others to discover.
            </p>
        </div>
        <div style="margin: 32px 0; text-align: center;">
            <a href="{brand['website_url']}/featured" style="display: inline-block; padding: 14px 28px; background: {brand['colors']['secondary']}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                View Your Feature
            </a>
        </div>
    """
    return _base_template(content, data)


def _default_template(data: Dict[str, Any]) -> str:
    brand = data.get("brand", BRAND)
    message = data.get("message", "")
    content = f"""
        <p style="font-size: 16px; color: {brand['colors']['text']}; line-height: 1.6;">
            {message}
        </p>
    """
    return _base_template(content, data)


# Template registry
TEMPLATES = {
    EmailType.WELCOME: _welcome_template,
    EmailType.EMAIL_VERIFICATION: _email_verification_template,
    EmailType.MAGIC_LINK: _magic_link_template,
    EmailType.PASSWORD_RESET: _password_reset_template,
    EmailType.SUBSCRIPTION_CONFIRMED: _subscription_confirmed_template,
    EmailType.PAYMENT_FAILED: _payment_failed_template,
    EmailType.STREAK_AT_RISK: _streak_at_risk_template,
    EmailType.MILESTONE_ACHIEVED: _milestone_achieved_template,
    EmailType.FEATURED_ACCEPTED: _featured_accepted_template,
}


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get email service singleton."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
