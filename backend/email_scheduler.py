#!/usr/bin/env python3
"""
QUIRRELY EMAIL SCHEDULER v1.0
Scheduled email jobs for streaks, trials, digests.

Jobs:
- Streak at risk (6 PM user time)
- Trial ending (2 days before, 10 AM)
- Weekly digest (Monday 9 AM)
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pytz

from email_config import (
    EmailType,
    EmailPreferences,
    TIMING_CONFIG,
)
from email_service import get_email_service


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ScheduledJob:
    """A scheduled email job."""
    name: str
    email_type: EmailType
    check_interval_minutes: int = 15
    last_run: Optional[datetime] = None


class EmailScheduler:
    """Scheduler for time-based email jobs."""
    
    def __init__(self):
        self.jobs: List[ScheduledJob] = [
            ScheduledJob(
                name="streak_at_risk",
                email_type=EmailType.STREAK_AT_RISK,
                check_interval_minutes=15,
            ),
            ScheduledJob(
                name="trial_ending",
                email_type=EmailType.TRIAL_ENDING,
                check_interval_minutes=60,
            ),
            ScheduledJob(
                name="weekly_digest",
                email_type=EmailType.WEEKLY_DIGEST,
                check_interval_minutes=60,
            ),
        ]
        self._running = False
    
    async def start(self):
        """Start the scheduler."""
        self._running = True
        while self._running:
            await self._run_jobs()
            await asyncio.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop the scheduler."""
        self._running = False
    
    async def _run_jobs(self):
        """Run due jobs."""
        now = datetime.utcnow()
        
        for job in self.jobs:
            if self._should_run(job, now):
                await self._execute_job(job)
                job.last_run = now
    
    def _should_run(self, job: ScheduledJob, now: datetime) -> bool:
        """Check if job should run."""
        if job.last_run is None:
            return True
        
        elapsed = (now - job.last_run).total_seconds() / 60
        return elapsed >= job.check_interval_minutes
    
    async def _execute_job(self, job: ScheduledJob):
        """Execute a scheduled job."""
        if job.email_type == EmailType.STREAK_AT_RISK:
            await self._send_streak_reminders()
        elif job.email_type == EmailType.TRIAL_ENDING:
            await self._send_trial_ending_reminders()
        elif job.email_type == EmailType.WEEKLY_DIGEST:
            await self._send_weekly_digests()
    
    async def _send_streak_reminders(self):
        """Send streak at risk emails to users at 6 PM their time."""
        service = get_email_service()
        users = await self._get_users_needing_streak_reminder()
        
        for user in users:
            if self._is_target_hour(user["timezone"], 18):  # 6 PM
                await service.send(
                    email_type=EmailType.STREAK_AT_RISK,
                    to_email=user["email"],
                    user_id=user["id"],
                    data={
                        "streak_days": user.get("streak_days", 0),
                    },
                )
    
    async def _send_trial_ending_reminders(self):
        """Send trial ending emails 2 days before expiry."""
        service = get_email_service()
        users = await self._get_users_with_expiring_trials()
        
        for user in users:
            if self._is_target_hour(user["timezone"], 10):  # 10 AM
                await service.send(
                    email_type=EmailType.TRIAL_ENDING,
                    to_email=user["email"],
                    user_id=user["id"],
                    data={
                        "days_remaining": 2,
                        "trial_ends": user.get("trial_ends"),
                    },
                )
    
    async def _send_weekly_digests(self):
        """Send weekly digest on Monday at 9 AM user time."""
        now = datetime.utcnow()
        
        # Only run on Mondays (0 = Monday)
        if now.weekday() != 0:
            return
        
        service = get_email_service()
        users = await self._get_users_for_digest()
        
        for user in users:
            if self._is_target_hour(user["timezone"], 9):  # 9 AM
                await service.send(
                    email_type=EmailType.WEEKLY_DIGEST,
                    to_email=user["email"],
                    user_id=user["id"],
                    data={
                        "week_stats": user.get("week_stats", {}),
                    },
                )
    
    def _is_target_hour(self, timezone: str, target_hour: int) -> bool:
        """Check if it's the target hour in the user's timezone."""
        try:
            tz = pytz.timezone(timezone)
            user_time = datetime.now(tz)
            return user_time.hour == target_hour
        except:
            return False
    
    # ─────────────────────────────────────────────────────────────────────
    # Data fetching (would query database in production)
    # ─────────────────────────────────────────────────────────────────────
    
    async def _get_users_needing_streak_reminder(self) -> List[Dict]:
        """Get users who haven't written today and have an active streak."""
        # Would query:
        # SELECT users.*, milestones.streak_1k_current
        # FROM users
        # JOIN user_milestones milestones ON users.id = milestones.user_id
        # WHERE milestones.streak_1k_current > 0
        #   AND milestones.streak_1k_last_date < CURRENT_DATE
        #   AND users.tier IN ('pro', 'trial')
        return []
    
    async def _get_users_with_expiring_trials(self) -> List[Dict]:
        """Get users whose trial ends in 2 days."""
        # Would query:
        # SELECT users.*, trials.ends_at
        # FROM users
        # JOIN trials ON users.id = trials.user_id
        # WHERE trials.ends_at BETWEEN NOW() AND NOW() + INTERVAL '2 days 1 hour'
        #   AND trials.converted_to_paid = FALSE
        #   AND NOT EXISTS (SELECT 1 FROM email_sends WHERE user_id = users.id AND type = 'trial_ending')
        return []
    
    async def _get_users_for_digest(self) -> List[Dict]:
        """Get users who have digest enabled."""
        # Would query:
        # SELECT users.*, email_preferences.timezone
        # FROM users
        # JOIN email_preferences ON users.id = email_preferences.user_id
        # WHERE email_preferences.digest_enabled = TRUE
        return []


# ═══════════════════════════════════════════════════════════════════════════
# TRIGGERED EMAILS (called from other services)
# ═══════════════════════════════════════════════════════════════════════════

async def send_welcome_email(user_id: str, email: str):
    """Send welcome email after signup."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.WELCOME,
        to_email=email,
        user_id=user_id,
    )


async def send_verification_email(user_id: str, email: str, verify_url: str):
    """Send email verification."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.EMAIL_VERIFICATION,
        to_email=email,
        user_id=user_id,
        data={"verify_url": verify_url},
    )


async def send_magic_link_email(user_id: str, email: str, magic_url: str):
    """Send magic link for passwordless login."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.MAGIC_LINK,
        to_email=email,
        user_id=user_id,
        data={"magic_url": magic_url},
    )


async def send_password_reset_email(user_id: str, email: str, reset_url: str):
    """Send password reset email."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.PASSWORD_RESET,
        to_email=email,
        user_id=user_id,
        data={"reset_url": reset_url},
    )


async def send_subscription_confirmed_email(user_id: str, email: str, tier_name: str):
    """Send subscription confirmation."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.SUBSCRIPTION_CONFIRMED,
        to_email=email,
        user_id=user_id,
        data={"tier_name": tier_name},
    )


async def send_subscription_cancelled_email(user_id: str, email: str):
    """Send subscription cancellation confirmation."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.SUBSCRIPTION_CANCELLED,
        to_email=email,
        user_id=user_id,
    )


async def send_payment_failed_email(user_id: str, email: str, update_url: str):
    """Send payment failed notification."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.PAYMENT_FAILED,
        to_email=email,
        user_id=user_id,
        data={"update_url": update_url},
    )


async def send_trial_started_email(user_id: str, email: str):
    """Send trial started confirmation."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.TRIAL_STARTED,
        to_email=email,
        user_id=user_id,
    )


async def send_milestone_email(user_id: str, email: str, milestone_name: str, milestone_icon: str):
    """Send milestone achieved notification."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.MILESTONE_ACHIEVED,
        to_email=email,
        user_id=user_id,
        data={
            "milestone_name": milestone_name,
            "milestone_icon": milestone_icon,
        },
    )


async def send_featured_submission_received_email(user_id: str, email: str, submission_type: str):
    """Send Featured submission received confirmation."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.FEATURED_SUBMISSION_RECEIVED,
        to_email=email,
        user_id=user_id,
        data={"submission_type": submission_type},
    )


async def send_featured_accepted_email(user_id: str, email: str, featured_type: str):
    """Send Featured accepted notification."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.FEATURED_ACCEPTED,
        to_email=email,
        user_id=user_id,
        data={"featured_type": featured_type},
    )


async def send_featured_rejected_email(user_id: str, email: str, feedback: str):
    """Send Featured rejected notification with feedback."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.FEATURED_REJECTED,
        to_email=email,
        user_id=user_id,
        data={"feedback": feedback},
    )


async def send_path_followed_email(user_id: str, email: str, follower_count: int):
    """Send notification when someone follows curator's path."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.PATH_FOLLOWED,
        to_email=email,
        user_id=user_id,
        data={"follower_count": follower_count},
    )


async def send_authority_eligible_email(user_id: str, email: str, authority_type: str):
    """Send Authority eligibility notification."""
    service = get_email_service()
    await service.send(
        email_type=EmailType.AUTHORITY_ELIGIBLE,
        to_email=email,
        user_id=user_id,
        data={"authority_type": authority_type},
    )


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_scheduler: Optional[EmailScheduler] = None


def get_email_scheduler() -> EmailScheduler:
    """Get email scheduler singleton."""
    global _scheduler
    if _scheduler is None:
        _scheduler = EmailScheduler()
    return _scheduler
