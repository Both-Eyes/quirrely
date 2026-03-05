# 🐿️ QUIRRELY QA PACKAGE FOR KIM
## Complete User Experience Testing Guide
### Version 1.0.0 | February 2026

---

## TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [User Tier & Addon Model](#2-user-tier--addon-model)
3. [Country Configuration](#3-country-configuration)
4. [Test User Personas](#4-test-user-personas)
5. [Feature Access Matrix](#5-feature-access-matrix)
6. [Screen-by-Screen Test Cases](#6-screen-by-screen-test-cases)
7. [User Journey Test Flows](#7-user-journey-test-flows)
8. [Edge Cases & Error States](#8-edge-cases--error-states)
9. [QA Execution Checklist](#9-qa-execution-checklist)
10. [Bug Report Template](#10-bug-report-template)

---

## 1. SYSTEM OVERVIEW

### What is Quirrely?

Quirrely (formerly Sentense) is a writing voice analysis platform that helps writers discover and develop their unique writing voice. The platform serves both **Writers** (content creators) and **Curators** (readers who create reading paths).

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend SPA | React 18 + TypeScript + Vite |
| State Management | Zustand + React Query |
| Styling | Tailwind CSS |
| Backend API | FastAPI (Python) |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth |
| Payments | Stripe |

### Four Target Countries

| Country | Currency | Flag |
|---------|----------|------|
| Canada | CAD | 🇨🇦 |
| United Kingdom | GBP | 🇬🇧 |
| Australia | AUD | 🇦🇺 |
| New Zealand | NZD | 🇳🇿 |

**⚠️ NEVER USD. NEVER USA.**

---

## 2. USER TIER & ADDON MODEL

### Two Parallel Tracks

```
        READER TRACK              WRITER TRACK
        ────────────              ────────────
            free                      free
              │                         │
              ▼                         ▼
          curator ◄───────────────────► pro
              │                         │
              │    ┌─────────────┐      │
              └───►│ voice_style │◄─────┘
                   │  (add-on)   │
                   └─────────────┘
              │                         │
              ▼                         ▼
      featured_curator            featured_writer
              │                         │
              ▼                         ▼
      authority_curator           authority_writer
```

### 7 Tiers

| Tier | Track | Level | Description |
|------|-------|-------|-------------|
| `free` | Both | 0 | Non-paying users |
| `pro` | Writer | 1 | Paid writer subscription |
| `curator` | Reader | 1 | Paid curator subscription |
| `featured_writer` | Writer | 2 | Platform-recognized writer |
| `featured_curator` | Reader | 2 | Platform-recognized curator |
| `authority_writer` | Writer | 3 | Top-tier writer with influence |
| `authority_curator` | Reader | 3 | Top-tier curator with influence |

### 1 Addon

| Addon | Description |
|-------|-------------|
| `voice_style` | Cross-track power user pass. Unlocks Voice Profile, path creation, and Authority features regardless of base tier. |

### Tier + Addon Combinations to Test

| # | Tier | Addon | Expected Access |
|---|------|-------|-----------------|
| 1 | free | none | Basic reading/writing only |
| 2 | free | voice_style | Voice Profile + Paths + Authority Hub |
| 3 | pro | none | Writer analytics, no paths |
| 4 | pro | voice_style | Full Writer + Voice + Paths + Authority |
| 5 | curator | none | Path creation, no Voice Profile |
| 6 | curator | voice_style | Full Curator + Voice + Authority |
| 7 | featured_writer | none | Featured + Authority Hub |
| 8 | featured_writer | voice_style | Featured + Voice + full access |
| 9 | featured_curator | none | Featured + Authority Hub |
| 10 | featured_curator | voice_style | Featured + Voice + full access |
| 11 | authority_writer | none | Full Authority access |
| 12 | authority_writer | voice_style | Full access + Voice |
| 13 | authority_curator | none | Full Authority access |
| 14 | authority_curator | voice_style | Full access + Voice |

---

## 3. COUNTRY CONFIGURATION

### Currency Display

| Country | Symbol | Format Example |
|---------|--------|----------------|
| Canada | $CAD | $14.99 CAD/month |
| UK | £ | £11.99/month |
| Australia | $AUD | $19.99 AUD/month |
| New Zealand | $NZD | $21.99 NZD/month |

### Localization Checks

- [ ] Date format: DD/MM/YYYY for UK, NZ, AU; MM/DD/YYYY avoided
- [ ] Spelling: "colour" not "color", "analyse" not "analyze"
- [ ] Currency symbol position: Before amount
- [ ] No USD pricing anywhere
- [ ] Country flag displays correctly in header/profile

### Country-Specific Test Accounts

```
kim_canada@test.quirrely.com     | 🇨🇦 | CAD
kim_uk@test.quirrely.com         | 🇬🇧 | GBP
kim_australia@test.quirrely.com  | 🇦🇺 | AUD
kim_newzealand@test.quirrely.com | 🇳🇿 | NZD
```

---

## 4. TEST USER PERSONAS

### Create these 14 test accounts (one per tier+addon combo, per country = 56 total)

#### Naming Convention
```
kim_{tier}_{addon}_{country}@test.quirrely.com

Examples:
kim_free_none_ca@test.quirrely.com
kim_pro_voicestyle_uk@test.quirrely.com
kim_authority_curator_none_au@test.quirrely.com
```

#### Quick Reference: Canadian Test Accounts

| Account | Tier | Addon | Badge Display |
|---------|------|-------|---------------|
| kim_free_none_ca | free | — | "Free" |
| kim_free_vs_ca | free | voice_style | "Free" + "✨ Voice + Style" |
| kim_pro_none_ca | pro | — | "Pro" |
| kim_pro_vs_ca | pro | voice_style | "Pro" + "✨ Voice + Style" |
| kim_curator_none_ca | curator | — | "Curator" |
| kim_curator_vs_ca | curator | voice_style | "Curator" + "✨ Voice + Style" |
| kim_fw_none_ca | featured_writer | — | "Featured Writer" |
| kim_fw_vs_ca | featured_writer | voice_style | "Featured Writer" + "✨ Voice + Style" |
| kim_fc_none_ca | featured_curator | — | "Featured Curator" |
| kim_fc_vs_ca | featured_curator | voice_style | "Featured Curator" + "✨ Voice + Style" |
| kim_aw_none_ca | authority_writer | — | "👑 Authority Writer" |
| kim_aw_vs_ca | authority_writer | voice_style | "👑 Authority Writer" + "✨ Voice + Style" |
| kim_ac_none_ca | authority_curator | — | "👑 Authority Curator" |
| kim_ac_vs_ca | authority_curator | voice_style | "👑 Authority Curator" + "✨ Voice + Style" |

---

## 5. FEATURE ACCESS MATRIX

### Navigation Visibility

| Feature | free | pro | curator | +voice_style | featured | authority |
|---------|------|-----|---------|--------------|----------|-----------|
| **READER SECTION** |
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Discover | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bookmarks | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reading Streak | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **WRITER SECTION** |
| My Writing | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Drafts | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voice Profile | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Analytics | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CURATOR SECTION** |
| My Paths | ❌ | ❌ | ✅ | ✅ | Curator | ✅ |
| Path Followers | ❌ | ❌ | ✅ | ✅ | Curator | ✅ |
| Featured | ❌ | ❌ | ❌ | ✅ | Curator | Curator |
| **AUTHORITY SECTION** |
| Authority Hub | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Leaderboard | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Impact Stats | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |

### Backend Feature Flags

| Feature Key | Description | Access Pattern |
|-------------|-------------|----------------|
| `basic_analysis` | Run voice analysis | All tiers |
| `save_results` | Save to account | Paid tiers |
| `analytics` | View analytics | pro/curator+ |
| `voice_profile` | Deep voice analysis | voice_style addon only |
| `create_paths` | Create reading paths | curator track OR voice_style |
| `authority_hub` | Authority dashboard | featured+ OR voice_style |
| `leaderboard` | Global rankings | featured+ OR voice_style |
| `impact_stats` | Impact metrics | featured+ OR voice_style |
| `extension_sync` | Browser extension sync | Paid tiers |
| `extension_history` | Extension analysis history | Paid tiers |
| `extension_voice_insights` | Voice insights in extension | voice_style addon only |

### Browser Extension Features

| Feature | free | pro | curator | +voice_style | featured | authority |
|---------|------|-----|---------|--------------|----------|-----------|
| Install extension | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Analyze text | ✅ (5/day) | ✅ | ✅ | ✅ | ✅ | ✅ |
| View results | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Save to account | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| View history | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Sync with web app | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voice insights | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Compare profiles | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export from extension | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 6. SCREEN-BY-SCREEN TEST CASES

### 6.1 Authentication Screens

#### Login (`/login`)
| Test | Expected |
|------|----------|
| Email field accepts valid email | ✅ Validation passes |
| Password field masks input | ✅ Dots shown |
| "Forgot Password" link works | ✅ Navigates to reset |
| Google sign-in button present | ✅ Visible |
| Apple sign-in button | ❌ MUST NOT EXIST |
| Invalid credentials show error | ✅ Toast notification |
| Successful login redirects to dashboard | ✅ |
| Country remembered from signup | ✅ |

#### Signup (`/signup`)
| Test | Expected |
|------|----------|
| Country selector shows 4 countries | 🇨🇦 🇬🇧 🇦🇺 🇳🇿 only |
| No USA option | ❌ MUST NOT EXIST |
| Password requirements enforced | Min 8 chars |
| Email validation | Must be valid format |
| Successful signup creates free account | ✅ |
| Welcome email sent | ✅ Check inbox |

### 6.2 Dashboard (`/dashboard`)

#### Header
| Test | Tier | Expected |
|------|------|----------|
| Tier badge displays | free | "Free" (gray) |
| Tier badge displays | pro | "Pro" (coral) |
| Tier badge displays | curator | "Curator" (coral) |
| Tier badge displays | featured_writer | "Featured Writer" (coral) |
| Tier badge displays | authority_curator | "👑 Authority Curator" (gold) |
| Addon badge displays | +voice_style | "✨ Voice + Style" (green) |
| Theme toggle works | all | Light ↔ Dark |
| Country flag shows | all | 🇨🇦/🇬🇧/🇦🇺/🇳🇿 |

#### Metrics Grid
| Test | Tier | Expected |
|------|------|----------|
| Authority Score card shows | authority_* | ✅ Gold card |
| Authority Score card hidden | non-authority | ❌ Not visible |
| Followers count shows | all | ✅ |
| Total Reads shows | all | ✅ |
| Reading Streak shows | all | ✅ |
| Posts Written shows | non-authority | ✅ |

#### Voice Profile Widget
| Test | Expected |
|------|----------|
| Radar chart renders | ✅ 6 dimensions |
| Voice tokens display | ✅ Top 5 traits |
| Confidence score shows | ✅ Percentage |
| "View Full Profile" link | voice_style only |

#### Activity Feed
| Test | Expected |
|------|----------|
| Recent activities show | ✅ Last 5 |
| Activity icons correct | ✅ Type-specific |
| Timestamps relative | "2 hours ago" format |
| Empty state if no activity | ✅ Friendly message |

### 6.3 Reader Section

#### Discover (`/reader/discover`)
| Test | Expected |
|------|----------|
| Post cards load | ✅ Grid layout |
| Search works | ✅ Filters posts |
| Tag filters work | ✅ Click to filter |
| Infinite scroll | ✅ Load more on scroll |
| Bookmark button | ✅ Toggle state |
| Read time shows | ✅ "5 min read" |
| Author avatar | ✅ With name |

#### Bookmarks (`/reader/bookmarks`)
| Test | Expected |
|------|----------|
| Saved posts show | ✅ |
| Remove bookmark | ✅ Updates list |
| Empty state | ✅ "No bookmarks yet" |
| Search bookmarks | ✅ Filters saved |
| Grid/List toggle | ✅ Layout changes |

#### Reading Streak (`/reader/streak`)
| Test | Expected |
|------|----------|
| Current streak shows | ✅ Day count |
| Calendar displays | ✅ Monthly view |
| Read days highlighted | ✅ Coral dots |
| Milestone progress | ✅ Visual progress |
| Streak freeze available | Paid tiers |

### 6.4 Writer Section

#### My Writing (`/writer/posts`)
| Test | Expected |
|------|----------|
| Published posts list | ✅ |
| Post stats (views, reads) | ✅ |
| Edit button | ✅ Opens editor |
| Delete with confirmation | ✅ Modal |
| Empty state | ✅ "Start writing" CTA |
| Status filter tabs | ✅ All/Published/Draft |

#### Drafts (`/writer/drafts`)
| Test | Expected |
|------|----------|
| Draft posts list | ✅ |
| Last edited timestamp | ✅ Relative time |
| Quick publish button | ✅ |
| Edit draft | ✅ Opens editor |
| Delete draft | ✅ With confirmation |

#### Editor (`/writer/editor`)
| Test | Expected |
|------|----------|
| Title input | ✅ Placeholder text |
| Content editor | ✅ Rich text |
| Toolbar (bold, italic, etc) | ✅ Formatting works |
| Tag input | ✅ Add/remove tags |
| Preview toggle | ✅ Shows preview |
| Auto-save indicator | ✅ "Saved" / "Saving..." |
| Publish button | ✅ Confirms publish |
| Voice analysis button | ✅ Analyzes content |
| Word count | ✅ Live count |

#### Voice Profile (`/dashboard/voice`) - **voice_style addon only**
| Test | Expected |
|------|----------|
| Page loads | ✅ Only with voice_style |
| Large radar chart | ✅ 6 dimensions |
| Dimension breakdowns | ✅ Progress bars |
| AI Insights | ✅ 3 insight cards |
| Voice Evolution history | ✅ Timeline |
| Export button | ✅ Download option |
| Share button | ✅ Share modal |

#### Analytics (`/writer/analytics`) - **pro/curator+ only**
| Test | Expected |
|------|----------|
| Page loads | ✅ Only with analytics access |
| Views chart | ✅ Line graph |
| Engagement metrics | ✅ Cards |
| Top posts table | ✅ Ranked list |
| Date range filter | ✅ Last 7/30/90 days |

### 6.5 Curator Section - **curator track OR voice_style**

#### My Paths (`/curator/paths`)
| Test | Expected |
|------|----------|
| Path list shows | ✅ |
| Create Path button | ✅ Opens editor |
| Path stats (followers) | ✅ |
| Publish/Unpublish toggle | ✅ |
| Edit path | ✅ Opens editor |
| Delete path | ✅ With confirmation |
| Filter tabs | ✅ All/Published/Draft |

#### Path Editor (`/curator/paths/new` or `/curator/paths/:id/edit`)
| Test | Expected |
|------|----------|
| Title input | ✅ |
| Description textarea | ✅ |
| Icon picker | ✅ 12 emoji options |
| Add posts button | ✅ Opens modal |
| Search posts in modal | ✅ |
| Reorder posts (drag/arrows) | ✅ |
| Remove post from path | ✅ |
| Save draft | ✅ |
| Publish button | ✅ Validates |

#### Featured (`/curator/featured`) - **featured_curator+ OR voice_style**
| Test | Expected |
|------|----------|
| Featured paths list | ✅ |
| Submit for featuring | ✅ |
| Featuring status | ✅ Pending/Approved |

### 6.6 Authority Section - **featured+ OR voice_style**

#### Authority Hub (`/authority/hub`)
| Test | Expected |
|------|----------|
| Authority score card | ✅ Gold gradient |
| Global rank | ✅ "#23" format |
| Percentile | ✅ "Top 1%" |
| Milestone progress | ✅ 5 milestones |
| Badge showcase | ✅ Grid |
| Quick action links | ✅ |

#### Leaderboard (`/authority/leaderboard`)
| Test | Expected |
|------|----------|
| Global leaderboard | ✅ Default view |
| Region filter buttons | 🇨🇦 🇬🇧 🇦🇺 🇳🇿 |
| Top 3 special styling | ✅ Gold/Silver/Bronze |
| Current user highlight | ✅ Coral background |
| Country flags on entries | ✅ |
| Avatar displays | ✅ |

#### Impact Stats (`/authority/impact`)
| Test | Expected |
|------|----------|
| Total reach metric | ✅ |
| Influence score | ✅ |
| Writers inspired count | ✅ |
| Paths completed | ✅ |
| Impact trend chart | ✅ Line chart |
| Category breakdown | ✅ Pie chart |
| Top contributions list | ✅ |

### 6.7 Settings (`/dashboard/settings`)

| Test | Expected |
|------|----------|
| Profile section | ✅ Name, email, avatar |
| Country display | ✅ With flag |
| Change password | ✅ |
| Notification preferences | ✅ Toggles |
| Privacy settings | ✅ |
| Delete account | ✅ With confirmation |
| Billing section | Paid tiers only |
| Subscription management | ✅ If subscribed |
| Currency display | ✅ Correct for country |

### 6.8 Error & Edge States

#### 404 Page (`/nonexistent`)
| Test | Expected |
|------|----------|
| 404 message shows | ✅ "Page not found" |
| Quirrel mascot | ✅ Confused squirrel |
| Go Back button | ✅ Works |
| Dashboard button | ✅ Redirects |

#### Error Boundary
| Test | Expected |
|------|----------|
| Error message | ✅ "Something went wrong" |
| Try Again button | ✅ Refreshes |
| Go to Dashboard | ✅ Redirects |
| Technical details | ✅ Expandable |

---

## 7. USER JOURNEY TEST FLOWS

### Journey 1: Free User to Pro

```
1. Sign up (free) in Canada
2. Verify email
3. Log in → Dashboard
4. Navigate to Analytics → Should be blocked
5. Click upgrade prompt
6. Select Pro plan
7. Enter payment (CAD)
8. Complete payment
9. Verify badge changes to "Pro"
10. Navigate to Analytics → Should work
11. Voice Profile → Should still be blocked
```

### Journey 2: Pro User Adds voice_style

```
1. Log in as Pro user
2. Navigate to Voice Profile → Blocked
3. Go to Settings → Billing
4. Add voice_style addon
5. Complete payment
6. Verify "✨ Voice + Style" badge appears
7. Navigate to Voice Profile → Works
8. Navigate to My Paths → Now works (cross-track)
9. Navigate to Authority Hub → Now works
```

### Journey 3: Curator Track Complete Journey

```
1. Sign up as free (Australia)
2. Upgrade to Curator tier (AUD)
3. Verify Curator badge
4. Create a reading path
5. Add 5 posts to path
6. Publish path
7. Check analytics (should work)
8. Voice Profile → Should be blocked
9. Add voice_style addon
10. Voice Profile → Now works
11. Authority Hub → Now works
12. Leaderboard → Filter by Australia
```

### Journey 4: Authority Writer Experience

```
1. Log in as Authority Writer (UK)
2. Verify "👑 Authority Writer" gold badge
3. Dashboard shows Authority Score card
4. Authority Hub accessible
5. Leaderboard shows user in list
6. Filter by UK → User still visible
7. Impact Stats shows metrics
8. Create a post
9. Publish post
10. Check Analytics
11. Verify all Writer features work
```

### Journey 5: Cross-Country Consistency

```
For each country (CA, UK, AU, NZ):
1. Log in as free user
2. Verify country flag in header
3. Go to Settings → Verify country display
4. Check any pricing → Verify correct currency
5. Leaderboard → Filter by own country
6. Verify users from same country shown
```

---

## 8. EDGE CASES & ERROR STATES

### Authentication Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Expired session | Wait 24h, try action | Redirect to login |
| Invalid token | Manually corrupt | Redirect to login |
| Concurrent sessions | Login on 2 devices | Both work |
| Password reset | Request reset, use link | Can log in with new password |
| Email change | Change email in settings | Confirmation required |

### Subscription Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Payment failure | Use test card that fails | Error message, no tier change |
| Downgrade | Cancel subscription | Access until period end |
| Resubscribe | Resubscribe after cancel | Immediate access |
| Addon without base tier | Add voice_style as free | Works, unlock features |
| Multiple addons | N/A currently | Only voice_style exists |

### Data Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Empty states | New user, no posts | Friendly empty messages |
| Long content | Very long post title | Truncates with ellipsis |
| Special characters | Title with emoji 🐿️ | Displays correctly |
| No internet | Disable network | Offline message |
| Slow network | Throttle to 3G | Loading states show |

### Permission Edge Cases

| Case | Test | Expected |
|------|------|----------|
| Direct URL to locked page | Go to /authority/hub as free | Redirect to /dashboard |
| Bookmark locked page | Bookmark then downgrade | Redirect on access |
| API direct call | Call analytics API as free | 403 Forbidden |
| Tier downgrade mid-session | Admin removes tier | Next action blocked |

---

## 9. QA EXECUTION CHECKLIST

### Phase 1: Setup (Day 1)

- [ ] Create 56 test accounts (14 tier combos × 4 countries)
- [ ] Document account credentials in password manager
- [ ] Set up test Stripe cards for each country
- [ ] Install in multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Install on mobile devices (iOS Safari, Android Chrome)
- [ ] Prepare bug tracking template
- [ ] Set up screen recording software

### Phase 2: Smoke Tests (Day 1-2)

- [ ] Login works for all account types
- [ ] Dashboard loads for all tiers
- [ ] Navigation shows correct items per tier
- [ ] No console errors in browser
- [ ] No broken images
- [ ] Dark mode works everywhere

### Phase 3: Feature Testing (Day 2-5)

#### By Screen (2 hours each)
- [ ] Login/Signup screens
- [ ] Dashboard
- [ ] Discover
- [ ] Bookmarks
- [ ] Reading Streak
- [ ] My Writing
- [ ] Drafts
- [ ] Editor
- [ ] Voice Profile (voice_style)
- [ ] Analytics (pro+)
- [ ] My Paths (curator/voice_style)
- [ ] Path Editor
- [ ] Featured (featured+/voice_style)
- [ ] Authority Hub
- [ ] Leaderboard
- [ ] Impact Stats
- [ ] Settings
- [ ] 404 page
- [ ] Error states

### Phase 4: User Journeys (Day 5-6)

- [ ] Journey 1: Free → Pro (all countries)
- [ ] Journey 2: Pro + voice_style (all countries)
- [ ] Journey 3: Curator track (all countries)
- [ ] Journey 4: Authority experience (all countries)
- [ ] Journey 5: Cross-country consistency

### Phase 5: Edge Cases (Day 6-7)

- [ ] All authentication edge cases
- [ ] All subscription edge cases
- [ ] All data edge cases
- [ ] All permission edge cases

### Phase 6: Cross-Browser (Day 7-8)

For each browser:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

Run:
- [ ] Smoke tests
- [ ] Critical journeys
- [ ] Visual check

### Phase 7: Mobile Testing (Day 8-9)

For each device:
- [ ] iPhone (Safari)
- [ ] iPad (Safari)
- [ ] Android phone (Chrome)
- [ ] Android tablet (Chrome)

Check:
- [ ] Responsive layout
- [ ] Touch interactions
- [ ] Sidebar behavior
- [ ] Modal dialogs
- [ ] Form inputs

### Phase 7b: Browser Extension Testing (Day 9)

**Chrome Extension:**
- [ ] Extension installs from Chrome Web Store
- [ ] Extension icon appears in toolbar
- [ ] Click extension → Login prompt (if not logged in)
- [ ] Login via extension works
- [ ] Extension syncs with web app session
- [ ] Highlight text on any webpage → Analyze option appears
- [ ] Analyze selected text → Voice profile results show
- [ ] Save to account works (paid tiers)
- [ ] Extension respects tier permissions (free vs paid)
- [ ] Extension shows correct tier badge
- [ ] Extension works on major sites (Medium, Substack, WordPress)
- [ ] Extension doesn't break page layouts
- [ ] Extension popup responsive
- [ ] Logout from extension works
- [ ] Extension settings accessible

**Firefox Extension:**
- [ ] Extension installs from Firefox Add-ons
- [ ] Extension icon appears in toolbar
- [ ] Click extension → Login prompt (if not logged in)
- [ ] Login via extension works
- [ ] Extension syncs with web app session
- [ ] Highlight text → Analyze option appears
- [ ] Analyze selected text → Results show
- [ ] Save to account works (paid tiers)
- [ ] Extension respects tier permissions
- [ ] Extension works on major sites
- [ ] Extension doesn't break page layouts
- [ ] Logout from extension works

**Extension + Tier Interactions:**

| Test | free | pro | curator | +voice_style |
|------|------|-----|---------|--------------|
| Analyze text | ✅ (limited) | ✅ | ✅ | ✅ |
| Save results | ❌ | ✅ | ✅ | ✅ |
| View history | ❌ | ✅ | ✅ | ✅ |
| Voice insights | ❌ | ❌ | ❌ | ✅ |
| Daily limit | 5 | Unlimited | Unlimited | Unlimited |

**Extension Edge Cases:**
- [ ] Extension behavior when logged out mid-session
- [ ] Extension behavior with expired subscription
- [ ] Extension on pages with Content Security Policy
- [ ] Extension on PDF viewers
- [ ] Extension on Google Docs (may not work - document)
- [ ] Multiple tabs with extension active
- [ ] Extension update notification

### Phase 8: Final Report (Day 10)

- [ ] Compile all bugs found
- [ ] Categorize by severity (Critical/Major/Minor/Cosmetic)
- [ ] Document reproduction steps
- [ ] Include screenshots/videos
- [ ] Prioritize fixes
- [ ] Sign off or request fixes

---

## 10. BUG REPORT TEMPLATE

```markdown
## Bug Report

**ID:** BUG-XXX
**Date:** YYYY-MM-DD
**Tester:** Kim
**Severity:** Critical / Major / Minor / Cosmetic

### Summary
One-line description of the bug

### Environment
- **Browser:** Chrome 121
- **OS:** macOS 14.3
- **Device:** MacBook Pro 14"
- **Account:** kim_pro_vs_ca@test.quirrely.com
- **Tier:** Pro + voice_style
- **Country:** Canada

### Steps to Reproduce
1. Log in with test account
2. Navigate to /curator/paths
3. Click "Create Path"
4. ...

### Expected Result
What should happen

### Actual Result
What actually happened

### Screenshots/Video
[Attach files]

### Console Errors
```
Any JavaScript errors from browser console
```

### Additional Notes
Any other relevant information
```

---

## APPENDIX A: API Endpoints to Verify

| Endpoint | Method | Auth | Access |
|----------|--------|------|--------|
| `/api/v2/dashboard` | GET | ✅ | All authenticated |
| `/api/v2/user/profile` | GET | ✅ | All authenticated |
| `/api/v2/user/addons` | GET | ✅ | All authenticated |
| `/api/v2/analytics/writer` | GET | ✅ | pro/curator+ |
| `/api/v2/voice/profile` | GET | ✅ | voice_style |
| `/api/v2/curator/paths` | GET | ✅ | curator+/voice_style |
| `/api/v2/authority/status` | GET | ✅ | featured+/voice_style |
| `/api/v2/authority/leaderboard` | GET | ✅ | featured+/voice_style |

---

## APPENDIX B: Test Card Numbers

| Country | Test Card | CVV | Expiry |
|---------|-----------|-----|--------|
| Canada | 4000001240000000 | Any | Future |
| UK | 4000008260000000 | Any | Future |
| Australia | 4000000360000006 | Any | Future |
| New Zealand | 4000005540000008 | Any | Future |

**Decline Test:** 4000000000000002

---

## APPENDIX C: Quick Reference Commands

```bash
# Start frontend dev server
cd sentense-app && npm run dev

# Start backend server
cd backend && uvicorn api_v2:app --reload

# Run frontend tests
cd sentense-app && npm test

# Check TypeScript errors
cd sentense-app && npm run typecheck
```

---

**Document Version:** 1.0.0
**Last Updated:** February 15, 2026
**Author:** System Architecture Team
**Reviewer:** Kim (QA Lead)
