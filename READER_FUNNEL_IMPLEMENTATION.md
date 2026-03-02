# QUIRRELY READER FUNNEL IMPLEMENTATION
## "Reading Taste" System

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## Overview

A second funnel entry point targeting **readers** (not just writers). Readers discover their "reading taste" through content exploration, receive book/writer recommendations with affiliate links, and eventually convert to analyzing their own writing.

---

## Decisions Made

| Decision | Choice |
|----------|--------|
| **Storage** | Hybrid: `reader_events` (raw) + `reader_profile` (computed) |
| **Affiliates** | Existing by country (CA, UK, AU, NZ) |
| **Featured Writers** | Conditional section (appears only if exists) |
| **Naming** | "Reading Taste" |
| **Generation** | All 40 posts now |
| **URLs** | `/blog/reading/{profile-slug}` |

---

## Content Created

### 40 Reader Blog Posts

Location: `/blog/reading/`

| Profile | URL | Title |
|---------|-----|-------|
| ASSERTIVE-OPEN | `/blog/reading/assertive-open` | Bold Ideas, Open Conversation |
| ASSERTIVE-CLOSED | `/blog/reading/assertive-closed` | Decisive and Direct |
| ... | ... | ... |
| HEDGED-CONTRADICTORY | `/blog/reading/hedged-contradictory` | Uncertain Wisdom |

Each post includes:
- ~400 words of reader-focused content
- Famous writers with affiliate links (by country)
- Book recommendations (affiliate linked)
- Conditional Featured Writer section
- Reader tracking integration
- "Taste vs Voice" CTA

---

## Database Schema

### Tables Added

| Table | Purpose |
|-------|---------|
| `reader_events` | Raw behavioral events (views, clicks, bookmarks) |
| `reader_profile` | Computed taste profile per user |
| `reader_bookmarks` | Saved content |

### Key Fields: `reader_events`

```sql
- user_id / session_id
- event_type (page_view, read_complete, click_book, etc.)
- profile_type, profile_stance
- content_type (reading_post, book, writer, featured_piece)
- time_on_page_seconds, scroll_depth_percent
- affiliate_partner, country_code
```

### Key Fields: `reader_profile`

```sql
- inferred_profile_id, inferred_confidence
- top_types[], top_stances[]
- profile_scores (JSONB)
- total_reading_posts_viewed, total_books_clicked
- writing_profile_id (for taste vs voice comparison)
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v2/reader/event` | Record behavioral event |
| GET | `/api/v2/reader/taste` | Get computed reading taste |
| GET | `/api/v2/reader/recommendations` | Get personalized recommendations |
| POST | `/api/v2/reader/bookmark` | Toggle bookmark |
| GET | `/api/v2/reader/bookmarks` | Get user's bookmarks |
| GET | `/api/v2/reader/compare` | Compare taste vs voice |

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<reader-tracker>` | Invisible behavior tracking |
| `<reading-taste-card>` | Display computed taste |
| `<taste-vs-voice>` | Compare reading/writing profiles |
| `<book-recommendation>` | Affiliate-linked book card |
| `<reading-recommendations>` | Personalized recommendations grid |

---

## Tracking Events

| Event | Trigger | Weight |
|-------|---------|--------|
| `page_view` | Page load | +1 |
| `read_complete` | >75% scroll OR >2min | +3 |
| `click_book` | Click affiliate link | +2 |
| `click_writer` | Click writer link | +2 |
| `click_featured` | Click Featured Writer | +3 |
| `bookmark` | Save content | +5 |
| `more_like_this` | Click recommendation | +4 |
| `dismiss` | "Not for me" | -3 |

Profile confidence increases with more events (max at ~20 events).

---

## Gating by Tier

| Feature | Visitor | FREE | TRIAL | PRO |
|---------|---------|------|-------|-----|
| Read posts | ✅ | ✅ | ✅ | ✅ |
| Writer recommendations | 3 | 5 | All | All |
| Book recommendations | 2 | 3 | All | All |
| Featured Writer pieces | Preview | 1/day | All | All |
| Reading Taste profile | ❌ | ❌ | ✅ | ✅ |
| Personalized recs | ❌ | Basic | Full | Full |
| Save preferences | ❌ | ✅ | ✅ | ✅ |
| Export reading list | ❌ | ❌ | ❌ | ✅ |

---

## Affiliate Structure

Using existing country-specific affiliates:

| Country | Partner | Tag |
|---------|---------|-----|
| CA | Amazon.ca | quirrely-ca-20 |
| UK | Amazon.co.uk | quirrely-uk-21 |
| AU | Booktopia | quirrely |
| NZ | Mighty Ape | quirrely |

Each reader post dynamically shows affiliate links based on user's detected country.

---

## Conversion Paths

### Reader → Writer

```
1. Reader discovers /blog/reading/assertive-open
2. Enjoys content, clicks books, returns
3. System builds Reading Taste profile
4. CTA: "Do you write like you read?"
5. User analyzes their writing
6. Discovers taste ≠ voice (or matches)
7. Insight creates engagement
8. Trial → Pro conversion
```

### Reader → Affiliate Revenue

```
1. Reader explores posts
2. Clicks book affiliate links
3. Purchases on Amazon/Booktopia
4. Quirrely earns commission
5. Reader may never write — still valuable
```

---

## File Inventory

### Backend

| File | Lines | Purpose |
|------|-------|---------|
| `backend/schema_reader.sql` | ~300 | Database schema + functions |
| `backend/reader_api.py` | ~350 | API endpoints |

### Frontend

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/components/reader-components.js` | ~500 | All reader UI components |

### Content

| Directory | Files | Purpose |
|-----------|-------|---------|
| `blog/reading/` | 40 HTML | Reader-focused blog posts |

### Generator

| File | Lines | Purpose |
|------|-------|---------|
| `generate_reader_posts.py` | ~400 | Blog post generator |

---

## Integration Points

### On Every Reader Post

```html
<!-- Auto-tracking -->
<reader-tracker 
  profile-type="ASSERTIVE" 
  profile-stance="OPEN"
  content-type="reading_post">
</reader-tracker>
```

### On Dashboard (Auth'd Users)

```html
<reading-taste-card
  profile-id="ASSERTIVE-OPEN"
  confidence="0.72"
  posts-viewed="14"
  books-clicked="5">
</reading-taste-card>

<taste-vs-voice
  reading-taste="ASSERTIVE-OPEN"
  writing-voice="CONVERSATIONAL-BALANCED">
</taste-vs-voice>
```

---

## Summary

| Metric | Value |
|--------|-------|
| Reader blog posts | 40 |
| API endpoints | 6 |
| Frontend components | 5 |
| Database tables | 3 |
| Affiliate partners | 4 (by country) |
| Tracking events | 8 types |

**The reader funnel is complete and ready for deployment.**

---

## Content Totals (Full System)

| Content Type | Count | Words |
|--------------|-------|-------|
| Writer posts (`/blog/writing/`) | 40 | ~20,000 |
| Reader posts (`/blog/reading/`) | 40 | ~16,000 |
| **Total blog posts** | **80** | **~36,000** |

**Two complete content funnels targeting complementary user types.**
