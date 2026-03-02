# PHASE 3: EMAIL SYSTEM IMPLEMENTATION
## Quirrely Email Infrastructure

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## Decisions Made

| # | Decision | Choice |
|---|----------|--------|
| 3a | Email Provider | **Resend** |
| 3b | Template Approach | **React Email** (HTML for now) |
| 3c | Transactional Emails | **12 types** |
| 3d | Engagement Emails | **5 types** |
| 3e | Frequency Controls | **Per-category opt-out** |
| 3f | Unsubscribe | **One-click + preferences page** |
| 3g | Send Times | **User timezone** |
| 3h | Analytics | **Basic (opens, clicks)** |
| 3i | Reply Handling | **No-reply with support link** |
| 3j | Branding | **Minimal (logo + colors)** |

---

## Email Types

### Transactional (Always Sent)

| Email | Trigger |
|-------|---------|
| Welcome | After signup |
| Email verification | After signup |
| Magic link | On request |
| Password reset | On request |
| Subscription confirmed | After payment |
| Subscription cancelled | After cancellation |
| Payment failed | On failure |
| Trial started | On trial start |
| Trial ending | 2 days before end |
| Featured submission received | On submission |
| Featured accepted | On acceptance |
| Featured rejected | On rejection |

### Engagement (Opt-out Available)

| Email | Trigger |
|-------|---------|
| Streak at risk | 6 PM if no activity |
| Milestone achieved | On milestone |
| Path followed | Someone follows Curator's path |
| Authority eligible | All requirements met |

### Digest (Opt-out Available)

| Email | Trigger |
|-------|---------|
| Weekly digest | Monday 9 AM |

---

## Email Preferences

### Categories

| Category | Can Unsubscribe | Examples |
|----------|-----------------|----------|
| **Transactional** | ❌ No | Payment, security, account |
| **Engagement** | ✅ Yes | Streaks, milestones |
| **Digest** | ✅ Yes | Weekly summary |

### User Controls

- Toggle engagement emails on/off
- Toggle digest emails on/off
- Set preferred timezone
- Set digest day (Mon-Sun)
- Set preferred hour (for reminders)

---

## Timing

| Email | When |
|-------|------|
| Streak at risk | 6 PM user's local time |
| Trial ending | 2 days before, 10 AM |
| Weekly digest | User's chosen day, 9 AM |

---

## Unsubscribe Flow

1. User clicks "Unsubscribe" in email footer
2. One-click unsubscribe processes immediately
3. Confirmation page shown with option to manage preferences
4. User can resubscribe anytime from preferences

---

## Files Created

### Backend

| File | Purpose |
|------|---------|
| `email_config.py` | Configuration, email types, templates |
| `email_service.py` | Resend integration, sending logic |
| `email_api.py` | Preferences and unsubscribe endpoints |
| `email_scheduler.py` | Timed email jobs |
| `schema_email.sql` | Preferences, send log, analytics |

### Frontend

| File | Purpose |
|------|---------|
| `email-preferences.js` | Preferences page, unsubscribe confirmation |

---

## API Endpoints

### Preferences

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/email/preferences` | Get preferences |
| PATCH | `/api/v2/email/preferences` | Update preferences |

### Unsubscribe

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/email/unsubscribe` | One-click unsubscribe |
| POST | `/api/v2/email/unsubscribe` | Authenticated unsubscribe |
| POST | `/api/v2/email/resubscribe` | Resubscribe to category |

### History

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/email/history` | Get user's email history |

### Testing

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v2/email/send-test` | Send test email (dev) |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `email_preferences` | User preferences |
| `email_sends` | Send log with analytics |
| `email_events` | Open/click tracking |
| `email_unsubscribes` | Unsubscribe audit |
| `email_suppression` | Bounced/complained emails |

---

## Branding

| Element | Value |
|---------|-------|
| Logo | 🐿️ |
| Primary color | #FF6B6B (Coral) |
| Secondary color | #D4A574 (Soft Gold) |
| From address | hello@quirrely.com |
| No-reply | noreply@quirrely.com |
| Support | support@quirrely.com |

---

## Email Template Structure

```
┌─────────────────────────────────────┐
│              🐿️                     │
├─────────────────────────────────────┤
│                                     │
│  Heading                            │
│                                     │
│  Body content with message          │
│                                     │
│  ┌─────────────────────────┐        │
│  │     [CTA Button]        │        │
│  └─────────────────────────┘        │
│                                     │
│  Questions? Contact support         │
│                                     │
├─────────────────────────────────────┤
│  Email preferences · Unsubscribe    │
│          © 2026 Quirrely            │
└─────────────────────────────────────┘
```

---

## Triggered Email Functions

```python
# Available in email_scheduler.py

await send_welcome_email(user_id, email)
await send_verification_email(user_id, email, verify_url)
await send_magic_link_email(user_id, email, magic_url)
await send_password_reset_email(user_id, email, reset_url)
await send_subscription_confirmed_email(user_id, email, tier_name)
await send_subscription_cancelled_email(user_id, email)
await send_payment_failed_email(user_id, email, update_url)
await send_trial_started_email(user_id, email)
await send_milestone_email(user_id, email, milestone_name, milestone_icon)
await send_featured_submission_received_email(user_id, email, submission_type)
await send_featured_accepted_email(user_id, email, featured_type)
await send_featured_rejected_email(user_id, email, feedback)
await send_path_followed_email(user_id, email, follower_count)
await send_authority_eligible_email(user_id, email, authority_type)
```

---

## Scheduled Jobs

| Job | Frequency | Check |
|-----|-----------|-------|
| Streak at risk | Every 15 min | Users at 6 PM local |
| Trial ending | Every 60 min | Users 2 days before |
| Weekly digest | Every 60 min | Users on their digest day |

---

## Analytics Tracked

| Metric | How |
|--------|-----|
| Sent | On send |
| Delivered | Webhook |
| Opened | Tracking pixel |
| Clicked | Link redirect |
| Bounced | Webhook |
| Complained | Webhook |

---

## Suppression List

Emails automatically added to suppression list:
- Hard bounces
- Spam complaints

Suppressed emails are never sent to again until manually removed.

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<email-preferences-page>` | Full preferences management |
| `<unsubscribe-confirmation>` | Post-unsubscribe page |

---

## Environment Variables

```bash
RESEND_API_KEY=re_...
```

---

## Resend Setup

1. Create account at resend.com
2. Verify domain (quirrely.com)
3. Add DNS records (SPF, DKIM, DMARC)
4. Generate API key
5. Configure webhook endpoint for events

---

## Phase 3 Complete ✅

Ready for **Phase 4: Dashboard & Settings**
