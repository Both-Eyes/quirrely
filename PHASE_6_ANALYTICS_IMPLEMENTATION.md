# PHASE 6: ANALYTICS & TRACKING IMPLEMENTATION
## Quirrely Analytics System

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## Decisions Made

| # | Decision | Choice |
|---|----------|--------|
| 6a | Analytics Provider | **Plausible** (privacy-focused) |
| 6b | Event Tracking | **5 categories** |
| 6c | Internal Metrics | **DAU/WAU/MAU, retention, funnels** |
| 6d | User-Facing Analytics | **Writers + Readers + Featured** |
| 6e | Privacy | **No cookies, no tracking scripts** |
| 6f | Data Retention | **Aggregates forever, events 90d** |
| 6g | Processing | **Hybrid (real-time + batch)** |
| 6h | A/B Testing | **Simple feature flags** |
| 6i | Error Tracking | **Sentry** |
| 6j | Performance | **Core Web Vitals via Plausible** |

---

## Event Categories

| Category | Events |
|----------|--------|
| **Core Actions** | signup, login, logout, analyze, subscribe |
| **Feature Usage** | milestone_achieved, featured_submission, bookmark_added, path_created |
| **Engagement** | streak_started, streak_continued, streak_broken, deep_read |
| **Conversions** | trial_started, trial_converted, trial_expired, upgrade, churn |

---

## Internal Metrics

### User Metrics
- DAU (Daily Active Users)
- WAU (Weekly Active Users)
- MAU (Monthly Active Users)
- Total users
- New signups

### Subscription Metrics
- MRR (Monthly Recurring Revenue)
- ARR (Annual Run Rate)
- Active subscriptions
- Trial conversion rate
- Churn rate

### Activity Metrics
- Analyses count
- Words analyzed
- Posts read
- Deep reads

### Feature Metrics
- Active streaks
- Featured writers
- Featured curators
- Milestones achieved

---

## User-Facing Analytics

### Writers See
- Words over time (chart)
- Streak history (visual calendar)
- Total words written
- Total analyses
- Current streak
- Longest streak

### Readers See
- Reading over time
- Deep read ratio
- Total posts read
- Profiles explored
- Taste evolution

### Featured Members See
- Profile views
- Piece engagement
- Path follows

---

## Privacy Approach

| Principle | Implementation |
|-----------|----------------|
| No cookies | Plausible doesn't use cookies |
| No PII in events | User IDs hashed before storage |
| Server-side tracking | No client-side tracking scripts |
| Data minimization | Only track what's needed |
| User control | Users see only their own data |

---

## Data Retention

| Data Type | Retention |
|-----------|-----------|
| Aggregate metrics | Forever |
| Daily snapshots | Forever |
| User activity | 1 year |
| Raw events | 90 days |
| Audit logs | 2 years |

---

## Funnels Defined

| Funnel | Steps |
|--------|-------|
| **Signup to First Analysis** | signup → email_verified → first_analysis |
| **Free to Trial** | signup → hit_word_limit → trial_started |
| **Trial to Paid** | trial_started → active_day_3 → active_day_7 → subscribed |
| **Writer to Featured** | subscribed → daily_1k → streak_7_day → eligible → submitted → approved |
| **Reader to Curator** | subscribed → posts_read_10 → deep_reads_5 → eligible → submitted → approved |

---

## Feature Flags

Simple feature flag system for controlled rollouts:

```python
FEATURE_FLAGS = {
    "new_voice_algorithm": {
        "enabled": False,
        "percentage": 0,
    },
    "reading_recommendations": {
        "enabled": False,
        "percentage": 0,
    },
    "dark_mode": {
        "enabled": False,
        "percentage": 0,
    },
}
```

Features:
- Percentage-based rollout (0-100%)
- User-specific allowlists
- Deterministic hashing for consistent experience

---

## Files Created

### Backend

| File | Purpose |
|------|---------|
| `analytics_config.py` | Events, metrics, feature flags |
| `analytics_service.py` | Tracking, collection, analysis |
| `analytics_api.py` | User + admin endpoints |
| `schema_analytics.sql` | Events, metrics, retention |

### Frontend

| File | Purpose |
|------|---------|
| `analytics-components.js` | User-facing analytics UI |

---

## API Endpoints

### Event Tracking

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v2/analytics/track` | Track event |

### User Analytics

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/analytics/me/writer` | Writer's analytics |
| GET | `/api/v2/analytics/me/reader` | Reader's analytics |
| GET | `/api/v2/analytics/me/featured` | Featured analytics |
| GET | `/api/v2/analytics/me/summary` | Quick summary |

### Admin Analytics

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/analytics/admin/metrics` | Daily metrics |
| GET | `/api/v2/analytics/admin/metrics/range` | Metrics range |
| GET | `/api/v2/analytics/admin/funnels` | List funnels |
| GET | `/api/v2/analytics/admin/funnels/{name}` | Analyze funnel |
| GET | `/api/v2/analytics/admin/retention` | Cohort retention |
| GET | `/api/v2/analytics/admin/retention/matrix` | Retention matrix |
| GET | `/api/v2/analytics/admin/realtime` | Real-time metrics |
| GET | `/api/v2/analytics/admin/distribution/profiles` | Profile distribution |
| GET | `/api/v2/analytics/admin/distribution/stances` | Stance distribution |

### Feature Flags

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/analytics/features` | User's feature flags |
| GET | `/api/v2/analytics/features/{name}` | Check specific flag |
| GET | `/api/v2/analytics/admin/features` | All flags (admin) |

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<writer-analytics>` | Full writer analytics page |
| `<reader-analytics>` | Full reader analytics page |
| `<featured-analytics>` | Featured member analytics |
| `<analytics-summary>` | Dashboard summary card |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `analytics_events` | Raw events (90-day retention) |
| `user_activity` | User activity log (1-year retention) |
| `daily_analytics` | Daily metric snapshots (forever) |
| `funnel_events` | Funnel step completions |
| `retention_cohorts` | Pre-calculated cohort retention |
| `user_analytics_cache` | Cached user stats |
| `feature_flags` | Feature flag configuration |
| `profile_distribution` | Voice profile distribution snapshots |

---

## Database Functions

| Function | Purpose |
|----------|---------|
| `hash_user_id()` | Hash user ID for privacy |
| `track_event()` | Record analytics event |
| `record_activity()` | Record user activity |
| `record_funnel_step()` | Record funnel completion |
| `get_dau()` | Calculate DAU |
| `get_wau()` | Calculate WAU |
| `get_mau()` | Calculate MAU |
| `calculate_daily_analytics()` | Daily batch job |
| `cleanup_old_events()` | 90-day retention cleanup |
| `cleanup_old_activity()` | 1-year retention cleanup |

---

## External Integrations

### Plausible Analytics
- Domain: quirrely.com
- No cookies required
- GDPR compliant out of the box
- Core Web Vitals tracking included

### Sentry Error Tracking
- Captures JavaScript and Python errors
- Stack traces with context
- Release tracking

---

## Environment Variables

```bash
PLAUSIBLE_API_KEY=plausible_...
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
```

---

## Batch Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `calculate_daily_analytics` | Daily 2 AM | Snapshot metrics |
| `calculate_retention_cohorts` | Daily 3 AM | Update retention |
| `cleanup_old_events` | Daily 4 AM | 90-day purge |
| `cleanup_old_activity` | Daily 4:30 AM | 1-year purge |
| `snapshot_profile_distribution` | Daily 5 AM | Profile stats |

---

## Phase 6 Complete ✅

### Progress Summary

| Phase | Status |
|-------|--------|
| Phase 1: Payments | ✅ Complete |
| Phase 2: Auth | ✅ Complete |
| Phase 3: Email | ✅ Complete |
| Phase 4: Dashboard & Settings | ✅ Complete |
| Phase 5: Admin Panel | ✅ Complete |
| Phase 6: Analytics & Tracking | ✅ Complete |
| Phase 7: Public Profiles & Social | ⏳ Next |
| Phase 8: Launch Prep | ⏳ |

---

Ready for **Phase 7: Public Profiles & Social**
