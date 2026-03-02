# QUIRRELY CURATOR TIER & FEATURED CURATOR IMPLEMENTATION
## Reader Tier System + Featured Curator Eligibility

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## Tier Structure

| Tier | Name | Cost | Identity |
|------|------|------|----------|
| Anonymous | **Visitor** | Free | Browsing |
| Auth'd Free | **Reader** | Free | Exploring |
| Paid | **Curator** | $1.99/mo or $20/yr | Curating |

---

## Feature Gating

| Feature | Visitor | Reader | Curator |
|---------|---------|--------|---------|
| **Content** | | | |
| Read blog posts | 3/day | Unlimited | Unlimited |
| Writer recommendations | 2/post | 4/post | All |
| Book recommendations | 1/post | 3/post | All |
| Featured Writer pieces | Preview | 1 full/day | Unlimited |
| **Taste Profile** | | | |
| Reading Taste computed | ❌ | Basic | Full |
| Taste vs Voice comparison | ❌ | ❌ | ✅ |
| **Personalization** | | | |
| Recommendations | Popular | Views-based | Full behavioral |
| Bookmarks | ❌ | 10 max | Unlimited |
| Reading history | ❌ | 7 days | Unlimited |
| **Extras** | | | |
| Export reading list | ❌ | ❌ | ✅ |
| Shareable taste card | ❌ | ❌ | ✅ |
| Featured Curator path | ❌ | ❌ | ✅ (if eligible) |

---

## Featured Curator Eligibility

### Requirements (All within 30 days)

| Milestone | Target | Proof |
|-----------|--------|-------|
| **Breadth** | 20 posts read | Explored widely |
| **Depth** | 5 deep reads (>80% scroll + >2min) | Engaged seriously |
| **Range** | 5 profile types explored | Open-minded |
| **Curation** | 10 bookmarks | Active collector |
| **Consistency** | 7-day reading streak | Committed habit |

### Submission

Once eligible, Curator submits:
- **Title** — Name for their reading path
- **Posts** — 4-6 profile IDs in sequence
- **Intro** — 100-word explanation (why this path, who it's for)
- **Agreements** — Original curation, permission, read all posts

### Review

Editorial review for quality/fit. If accepted:
- **Featured Curator** badge
- Path published at `/paths/{user_id}`
- Displayed on Quirrely for others to follow

---

## Journey Touchpoints

### Day 1: Welcome

```
📚 Welcome, Curator

In the next 30 days, unlock Featured Curator by:
○ Reading 20 posts
○ Deep reading 5 posts  
○ Exploring 5 profile types
○ Bookmarking 10 favorites
○ Reading 7 days in a row

[Start Exploring →]
```

### Progress Milestones

| Trigger | Prompt |
|---------|--------|
| Post 5 | "You're off to a great start" |
| First deep read | "You spent real time with that piece" |
| Post 10 | "Halfway there — your taste is emerging" |
| 5th profile type | "You have range" |
| 7-day streak | "Consistency is the heart of curation" |
| 10 bookmarks | "You're curating, not just reading" |
| Post 20 | "You know the landscape" |
| **All complete** | "⭐ Featured Curator Eligible!" |

### Streak Maintenance

| Situation | Prompt |
|-----------|--------|
| Day 5 of streak | "Two more days — keep the momentum" |
| No visit by 6pm | "Don't break your streak" (email/push) |
| Day 28, incomplete | "2 days left — so close!" |
| Day 30, final hours | "Final day — complete now" |

### Window Expired

```
⏳ Your 30-day window has closed

You completed 4 of 5 milestones. So close.

Your bookmarks are saved. Your new window starts now.

[Start fresh →]
```

---

## Conversion Prompts

### Visitor → Reader

| Moment | Trigger | Message |
|--------|---------|---------|
| Third post | 3 posts viewed | "You've explored 3 styles. Sign up free to continue." |
| More like this | Clicks recommendation | "Sign up for personalized recommendations." |
| Bookmark attempt | Clicks bookmark | "Create free account to save favorites." |

### Reader → Curator

| Moment | Trigger | Message |
|--------|---------|---------|
| Tenth post | 10 posts viewed | "Your taste is emerging. Upgrade for full profile." |
| Bookmark limit | 11th bookmark | "Free accounts save 10. Curators get unlimited." |
| Featured preview | Daily limit hit | "Curators get unlimited Featured Writers." |
| Taste vs voice | Has writing analysis | "Compare your writing voice to reading taste." |

---

## Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `curator_milestone_state` | Window, progress, eligibility |
| `curated_paths` | Submitted/published paths |
| `path_follows` | Users following paths |
| `curator_milestone_events` | Audit log |

### Key Fields: `curator_milestone_state`

```sql
window_start, window_end, window_active
posts_read, posts_read_ids[], posts_read_complete
deep_reads, deep_read_ids[], deep_reads_complete
profile_types_explored[], profile_types_complete
bookmarks_count, bookmarks_complete
reading_streak_current, streak_complete
featured_eligible, featured_eligible_at
featured_curator, featured_curator_since
featured_path_id, featured_path_url
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v2/curator/start-window` | Start 30-day window |
| GET | `/api/v2/curator/progress` | Get milestone progress |
| GET | `/api/v2/curator/next-action` | Get recommended next action |
| POST | `/api/v2/curator/record/read` | Record post read |
| POST | `/api/v2/curator/record/bookmark` | Record bookmark |
| GET | `/api/v2/curator/featured/eligibility` | Check submission eligibility |
| POST | `/api/v2/curator/featured/submit` | Submit curated path |
| GET | `/api/v2/curator/featured/paths` | Get all featured paths |
| GET | `/api/v2/curator/featured/paths/{user_id}` | Get specific path |

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<curator-welcome>` | Welcome modal with milestones |
| `<curator-progress>` | Progress dashboard |
| `<curator-path-submission>` | Path submission form |
| `<featured-path-card>` | Display a curated path |
| `<tier-upgrade-prompt>` | Visitor→Reader, Reader→Curator prompts |
| `<curator-milestone-toast>` | Milestone completion notifications |

---

## Files Created

### Backend

| File | Lines | Purpose |
|------|-------|---------|
| `backend/curator_tracker.py` | ~500 | Milestone tracking logic |
| `backend/curator_api.py` | ~300 | API endpoints |
| `backend/schema_curator.sql` | ~250 | Database schema |

### Frontend

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/components/curator-components.js` | ~600 | All curator UI components |

---

## Parallel with Writer System

| Aspect | Featured Writer | Featured Curator |
|--------|-----------------|------------------|
| Tier required | PRO ($4.99/mo) | Curator ($1.99/mo) |
| Proof | 7-day 1K word streak | 20 posts, 5 deep, 5 types, 10 bookmarks, 7-day streak |
| Window | Ongoing | 30 days |
| Submission | 500-word original piece | 4-6 post curated path + 100-word intro |
| Value created | Content | Curation |
| Badge | ⭐ Featured Writer | ⭐ Featured Curator |
| Ultimate combo | — | 🏆 Voice & Taste (both) |

---

## Revenue Model

| Tier | Monthly | Annual | Value |
|------|---------|--------|-------|
| Reader | Free | Free | Explore, save basics |
| **Curator** | **$1.99** | **$20** | Full taste, all access, Featured path |
| PRO (Writer) | $4.99 | $50 | Full analysis, evolution, Featured piece |
| **Bundle** | $5.99 | $60 | Both (save $1/mo) |

---

## Summary

The Curator tier creates a parallel recognition path for readers:

1. **Visitors** sample (3 posts/day)
2. **Readers** explore free (unlimited posts, basic features)
3. **Curators** ($1.99/mo) get full taste analysis + Featured path eligibility
4. **Featured Curators** earn recognition by curating paths others follow

This mirrors the writer journey (FREE → TRIAL → PRO → Featured Writer) but optimized for consumption rather than creation.

**Both paths lead to engagement, recognition, and community contribution.**
