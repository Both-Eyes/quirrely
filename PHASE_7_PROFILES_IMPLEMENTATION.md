# PHASE 7: PUBLIC PROFILES & SOCIAL IMPLEMENTATION
## Quirrely Public Presence

**Date:** February 14, 2026  
**Status:** ✅ IMPLEMENTED

---

## Decisions Made

| # | Decision | Choice |
|---|----------|--------|
| 7a | URL Structure | **/@username** |
| 7b | Username Rules | **3-20 chars, letters/numbers/underscore** |
| 7c | Profile Content | **10 elements** |
| 7d | Privacy Levels | **Private (default), Featured Only, Public** |
| 7e | Showcase Pages | **4 pages** |
| 7f | Social Sharing | **Copy link, LinkedIn, Facebook, Email** |
| 7g | Open Graph | **Full OG tags** |
| 7h | Follow System | **Path follows only** |
| 7i | Comments | **None** |
| 7j | View Counter | **Hidden (owner only)** |

---

## Profile URLs

| Format | Example |
|--------|---------|
| Profile | `quirrely.com/@username` |
| Featured Writers | `quirrely.com/featured/writers` |
| Featured Curators | `quirrely.com/featured/curators` |
| Authority | `quirrely.com/featured/authority` |
| Landing | `quirrely.com/featured` |

---

## Username Requirements

| Rule | Value |
|------|-------|
| Minimum length | 3 characters |
| Maximum length | 20 characters |
| Allowed characters | Letters, numbers, underscores |
| Must start with | Letter |
| Case | Case-insensitive (stored lowercase) |
| Change cooldown | 30 days |

### Reserved Usernames
- Brand: quirrely, quirrel, squirrel
- System: admin, support, help, api
- Features: featured, authority, writer, curator
- Pages: settings, dashboard, profile, pricing

---

## Profile Visibility

| Level | Description | Default |
|-------|-------------|---------|
| **Private** | Only owner sees | ✅ Default |
| **Featured Only** | Visible on Featured showcase pages | |
| **Public** | Anyone with link can view | |

---

## Public Profile Content

| Element | Visibility |
|---------|------------|
| Display name | Always |
| Username | Always |
| Join date | Always |
| Avatar | If set |
| Bio | If set (max 160 chars) |
| Voice profile | If sharing enabled |
| Reading taste | If sharing enabled |
| Featured badge | If Featured |
| Authority badge | If Authority |
| Featured pieces | If Featured Writer |
| Curated paths | If Featured Curator |

---

## Recognition Badges

| Badge | Icon | Color |
|-------|------|-------|
| Featured Writer | ⭐ | #D4A574 (Soft Gold) |
| Featured Curator | ⭐ | #D4A574 |
| Authority Writer | 👑 | #FFD700 |
| Authority Curator | 👑 | #FFD700 |
| Voice & Taste | 🏆 | #FF6B6B (Coral) |
| Authority Voice & Taste | 💎 | #6C5CE7 |

---

## Social Sharing

| Platform | Supported |
|----------|-----------|
| Copy link | ✅ |
| LinkedIn | ✅ |
| Facebook | ✅ |
| Email | ✅ |
| X/Twitter | ❌ (excluded) |

---

## Open Graph Tags

```html
<meta property="og:title" content="{Name} on Quirrely">
<meta property="og:description" content="{Bio or voice summary}">
<meta property="og:image" content="{Avatar or default}">
<meta property="og:url" content="https://quirrely.com/@username">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Quirrely">
```

### SEO
- Public profiles: `index, follow`
- Private/Featured-only: `noindex, nofollow`

---

## Files Created

### Backend

| File | Purpose |
|------|---------|
| `profiles_config.py` | URLs, usernames, badges, sharing |
| `profiles_api.py` | Profile and showcase endpoints |
| `schema_profiles.sql` | Usernames, profiles, views |

### Frontend

| File | Purpose |
|------|---------|
| `profiles-components.js` | Profile pages, showcase grids |

---

## API Endpoints

### Username Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/profiles/username/check` | Check availability |
| POST | `/api/v2/profiles/username` | Set/change username |
| GET | `/api/v2/profiles/username` | Get my username |

### Profile Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/profiles/me` | Get my profile settings |
| PATCH | `/api/v2/profiles/me` | Update my profile |

### Public Profiles

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/profiles/{username}` | Get public profile |

### Showcase Pages

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/profiles/featured` | Featured landing |
| GET | `/api/v2/profiles/featured/writers` | Featured Writers grid |
| GET | `/api/v2/profiles/featured/curators` | Featured Curators grid |
| GET | `/api/v2/profiles/featured/authority` | Authority members grid |

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<public-profile>` | Full profile page |
| `<featured-showcase>` | Grid of Featured members |
| `<featured-landing>` | Combined Featured landing |
| `<username-setup>` | Username claim flow |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `usernames` | Username → user mapping |
| `username_history` | Previous usernames |
| `reserved_usernames` | Blocked usernames |
| `public_profiles` | Profile settings + cache |
| `profile_views` | View tracking |
| `profile_view_counts` | Daily view aggregates |
| `profile_featured_pieces` | Writer's showcase pieces |
| `profile_curated_paths` | Curator's paths |
| `path_follows` | Path follow relationships |

---

## Database Functions

| Function | Purpose |
|----------|---------|
| `is_username_available()` | Check availability |
| `claim_username()` | Claim or change username |
| `get_public_profile()` | Fetch profile by username |
| `record_profile_view()` | Track profile view |
| `get_profile_view_count()` | Get view stats |

---

## Database Views

| View | Purpose |
|------|---------|
| `featured_writers_showcase` | Writers for showcase |
| `featured_curators_showcase` | Curators for showcase |
| `authority_members_showcase` | Authority members |

---

## Privacy Features

1. **Private by default** — Profiles not visible until opted in
2. **Owner-only view count** — No public vanity metrics
3. **Granular sharing** — Separate toggles for voice + taste
4. **No comments** — No moderation burden
5. **No follower counts** — Focus on content, not popularity

---

## Social Note

**Excluded:** X/Twitter (brand exclusion list)

**Included:** LinkedIn, Facebook, Email, Copy link

---

## Phase 7 Complete ✅

### Progress Summary

| Phase | Status |
|-------|--------|
| Phase 1: Payments | ✅ Complete |
| Phase 2: Auth | ✅ Complete |
| Phase 3: Email | ✅ Complete |
| Phase 4: Dashboard & Settings | ✅ Complete |
| Phase 5: Admin Panel | ✅ Complete |
| Phase 6: Analytics & Tracking | ✅ Complete |
| Phase 7: Public Profiles & Social | ✅ Complete |
| Phase 8: Launch Prep | ⏳ Next |

---

Ready for **Phase 8: Launch Prep**
