# 🐿️ KIM'S QA EXECUTION PLAN v3.1.1
## Knight of Wands MRR Optimization + Polish Sprint Audit
### Date: February 16, 2026
### Updated: v3.1.1 Polish Verification Added

---

## SCOPE OVERVIEW

This audit covers ALL changes introduced in Knight of Wands v3.1.0 + v3.1.1 Polish:

### New Features to Test (v3.1.0)
- **P1 Quick Wins**: Addon Bundling, Downgrade Prevention, First Analysis Hook
- **P2 Optimizations**: Annual Discount (25%), Smart Notifications, Social Proof, Middle Tier (Growth)
- **P3 Optimizations**: Achievement System, Progressive Feature Unlocks

### v3.1.1 Polish Fixes to Verify
- **M1**: Badge contrast in dark mode
- **M2**: Author cards mobile horizontal scroll
- **M3**: Weekly challenge text wrap
- **M4**: Loading states for CTAs

### Existing Features to Retest
- 40+ user permutations
- 12 dashboard views
- 4 settings tabs
- 4-country pricing
- Feature gating by tier
- Dark mode consistency
- Mobile responsiveness

---

## SECTION 0: v3.1.1 POLISH VERIFICATION (PRIORITY)

### 0.1 M1: Badge Contrast Dark Mode

**Test Location**: Any user → Achievements view → Dark mode ON

| Test Case | Expected | Status |
|-----------|----------|--------|
| Toggle dark mode on | UI switches to dark | |
| Navigate to Achievements | View loads | |
| Find locked badge (e.g., "Bookworm") | Badge visible | |
| Locked badge emoji | Grayscale + 60% opacity | |
| Locked badge name text | Gray-400 color, readable | |
| Locked badge progress text | Amber-400 color, visible | |
| Earned badges unaffected | Full color, green check | |
| All 4 badge sections consistent | Same styling | |

### 0.2 M2: Author Cards Mobile

**Test Location**: "New Reader" → Dashboard → Resize to <400px

| Test Case | Expected | Status |
|-----------|----------|--------|
| Select "New Reader" user | Dashboard loads | |
| First Analysis Hook visible | Voice match card shows | |
| Resize browser to <400px | Layout adapts | |
| Author cards change to horizontal scroll | flex + overflow-x-auto | |
| Cards have fixed width | ~130px each | |
| Horizontal scroll indicator | Scrollbar or visual cue | |
| Swipe/scroll to see all 3 cards | All accessible | |
| Resize back to desktop | Grid layout returns | |

### 0.3 M3: Weekly Challenge Text Wrap

**Test Location**: Any user → Achievements → Resize to mobile

| Test Case | Expected | Status |
|-----------|----------|--------|
| Navigate to Achievements view | Weekly Challenge card visible | |
| Resize to mobile width (~375px) | Layout adapts | |
| "Weekly Challenge" text | Wraps cleanly | |
| "Ends in 3 days" badge | Stays intact (no mid-word break) | |
| "500 XP Reward" text | Stays intact (whitespace-nowrap) | |
| Zap icon | Stays with text (flex-shrink-0) | |
| Progress bar + button | Stack on mobile | |
| Resize back to desktop | Horizontal layout returns | |

### 0.4 M4: Loading States for CTAs

**Test Users**: Various (see table)
**Expected Behavior**: Click → Spinner + "Processing..." → Returns to normal (~1.5s)

| CTA | Location | User to Test | Status |
|-----|----------|--------------|--------|
| Upgrade to Pro | First Analysis Hook | New Reader | |
| Switch to Annual | Billing (Annual Banner) | Pro Writer | |
| Analyze Now | Weekly Challenge | Any user → Achievements | |
| Explore Featured | Social Proof Notification | Pro Writer → Dashboard | |
| Analyze Now | Badge Notification | Pro Writer → Dashboard | |
| Claim 20% Off | Progressive Day 7 | Voice Explorer (14 days) | |
| Upgrade Now | Progressive Teaser | New Reader | |

**For each CTA verify**:
- [ ] Button shows spinner SVG on click
- [ ] Text changes to "Processing..."
- [ ] Button is disabled (no double-click)
- [ ] Returns to normal state after ~1.5s
- [ ] Hover states work before/after

---

## PRE-FLIGHT CHECKLIST

- [x] Access to composable-dashboard-demo.jsx
- [x] All 9 user profiles available in demo
- [x] Documentation reviewed (P1, P2, P3 implementation docs)
- [x] Previous audit report reviewed (KIM_E2E_AUDIT_REPORT.md)

---

## SECTION 1: USER PROFILE AUDIT

### 1.1 Test User Matrix (9 Profiles)

| ID | Name | Writer Tier | Curator Tier | Addons | Country | Days |
|----|------|-------------|--------------|--------|---------|------|
| U1 | New Reader | free | free | none | CA | 3 |
| U2 | Voice Explorer | free | free | voice_style | GB | 14 |
| U3 | Pro Writer | pro | free | none | AU | 45 |
| U4 | Path Curator | free | curator | none | NZ | 60 |
| U5 | Dual Creator | pro | curator | voice_style | CA | 75 |
| U6 | Authority Writer | authority_writer | free | voice_style | CA | 90 |
| U7 | Authority Curator | free | authority_curator | none | GB | 120 |
| U8 | Authority Dual | authority_writer | authority_curator | voice_style | CA | 180 |
| U9 | Featured Dual | featured_writer | curator | voice_style | AU | 100 |

### 1.2 Profile Test Cases

For EACH user profile, verify:
- [ ] Correct name displays in sidebar and header
- [ ] Correct badges display (tier + addon)
- [ ] Correct country flag displays
- [ ] Correct currency displays in billing
- [ ] Correct features accessible in sidebar
- [ ] Correct dashboard metrics show

---

## SECTION 2: P1 QUICK WINS AUDIT

### 2.1 Addon Bundling (Free Users Only)

**Test Users**: U1 (New Reader), U2 (Voice Explorer)
**Location**: Settings → Billing Tab

| Test Case | Expected | Status |
|-----------|----------|--------|
| "Choose Your Plan" section visible | Yes for free users | |
| Standalone Plans section present | Pro, Growth, Featured listed | |
| Growth tier shows "Popular" badge | Purple badge visible | |
| Growth tier pricing correct | $6.99/mo, $62.99/yr | |
| Best Value Bundles section present | Pro+V+S, Authority+V+S listed | |
| Pro + V+S bundle shows $12.99 | Correct with "Save $2/mo" | |
| Authority + V+S shows "Best Value" | Amber badge visible | |
| Authority + V+S shows $16.99 | Correct with strikethrough original | |
| All CTAs are clickable | Buttons respond to hover/click | |

### 2.2 Downgrade Prevention (Paid Users Only)

**Test Users**: U3, U5, U6, U8, U9 (any paid user)
**Location**: Settings → Billing Tab → Subscription Management

| Test Case | Expected | Status |
|-----------|----------|--------|
| "Subscription Management" card visible | Yes for paid users | |
| Pause Subscription option present | Blue highlight, "Recommended" badge | |
| Downgrade option shows correct tier | Dynamic based on current tier | |
| "Stay & Save 50%" shows discount | Calculated 50% of current price | |
| Cancel link at bottom (subtle) | Gray text, not prominent | |
| All 3 retention options clickable | Buttons respond | |

### 2.3 First Analysis Hook (New Free Users ≤7 days)

**Test Users**: U1 (New Reader, 3 days)
**Location**: Dashboard (top)

| Test Case | Expected | Status |
|-----------|----------|--------|
| Voice Match card visible for U1 | Yes (daysInSystem: 3) | |
| Voice Match NOT visible for U2 | No (daysInSystem: 14) | |
| Shows 3 author matches | Hemingway, Orwell, Didion | |
| Percentages display correctly | 78%, 65%, 62% | |
| "Unlock 10 more" teaser visible | Yes with upgrade CTA | |
| "Upgrade to Pro" button works | Clickable with Zap icon | |

---

## SECTION 3: P2 OPTIMIZATIONS AUDIT

### 3.1 Annual Discount 25% (Paid Users)

**Test Users**: U3, U5, U6, U8, U9
**Location**: Settings → Billing Tab

| Test Case | Expected | Status |
|-----------|----------|--------|
| "Switch to Annual & Save 25%" banner | Visible for monthly subscribers | |
| Shows current yearly cost | Calculated from monthly × 12 | |
| Shows annual price | Correct 25% discount price | |
| Shows savings amount | Difference calculated correctly | |
| "Limited Time" badge present | Yes | |
| "Switch to Annual" CTA clickable | Yes with Zap icon | |

**Pricing Verification**:
| Tier | Monthly × 12 | Annual (25% off) | Savings |
|------|--------------|------------------|---------|
| Pro | $59.88 | $44.99 | $14.89 |
| Featured | $95.88 | $71.99 | $23.89 |
| Authority | $107.88 | $80.99 | $26.89 |
| Voice+Style | $119.88 | $89.99 | $29.89 |

### 3.2 Smart Notifications (Paid/Addon Users)

**Test Users**: U5, U6, U8, U9 (with features)
**Location**: Dashboard (above metrics)

| Test Case | Expected | Status |
|-----------|----------|--------|
| Voice Evolution notification (V+S users) | "Your voice evolved 12% this week!" | |
| Shows confidence change | "75% to 87%" | |
| "View Details" links to Voice Profile | Yes | |
| Social Proof notification (non-Authority) | "3 writers upgraded to Featured" | |
| "Explore Featured" CTA present | Yes | |
| Badge Progress notification (writers) | "2 analyses away from badge" | |
| "Analyze Now" CTA present | Yes | |

### 3.3 Social Proof Counters (Free Users)

**Test Users**: U1, U2
**Location**: Dashboard

| Test Case | Expected | Status |
|-----------|----------|--------|
| Three-column stats bar visible | Yes for free users only | |
| "4,271 writers upgraded" displays | Yes | |
| "12,847 analyses today" displays | Yes | |
| "89% of [Country] recommend Pro" | Shows user's country flag | |
| NOT visible for paid users | Hidden for U3-U9 | |

### 3.4 Middle Tier - Growth ($6.99)

**Test Users**: U1, U2 (free users)
**Location**: Settings → Billing Tab

| Test Case | Expected | Status |
|-----------|----------|--------|
| Growth tier in Standalone Plans | Between Pro and Featured | |
| "Popular" badge on Growth | Purple badge visible | |
| Price: $6.99/mo, $62.99/yr | Correct for CAD | |
| GBP price: £3.49/mo | Correct conversion | |
| Description matches | "Pro + comparison tools + priority support" | |
| Purple gradient highlight | Visual distinction | |

---

## SECTION 4: P3 OPTIMIZATIONS AUDIT

### 4.1 Achievement System

**Test Users**: All users
**Location**: Streak view (click Flame icon in sidebar)

| Test Case | Expected | Status |
|-----------|----------|--------|
| View renamed to "Achievements & Streaks" | Title with Trophy icon | |
| Level display in header | "Level 7 • 2,340 XP" | |
| XP progress bar visible | 78% filled, gradient gold | |
| "660 XP until next level" text | Correct calculation | |
| Next level reward preview | "Elite Writer badge + Featured priority" | |

**Streak Stats Cards (4)**:
| Card | Value | Subtext | Status |
|------|-------|---------|--------|
| Day Streak | 23 | "+50 XP/day" | |
| Longest Streak | 47 | "Personal Best" | |
| Total Reading Days | 312 | "Top 5% of readers" | |
| Badges Earned | 12 | "4 more available" | |

**Weekly Challenge**:
| Test Case | Expected | Status |
|-----------|----------|--------|
| Challenge card visible | Purple gradient | |
| Title: "Voice Evolution Week" | Correct | |
| Progress: "3/5 analyses" | 60% bar | |
| Reward: "500 XP" | Displayed | |
| "Ends in 3 days" badge | Present | |
| "Analyze Now" CTA | Clickable | |

**Badge Collection (16 badges)**:

*Reading Streaks (4)*:
| Badge | Status | XP/Progress | Visual |
|-------|--------|-------------|--------|
| First Week 🌱 | Earned | +100 XP | Green check | |
| Committed 📚 | Earned | +200 XP | Green check | |
| Dedicated 🔥 | Earned | +300 XP | Green check | |
| Bookworm 📖 | Locked | 23/30 | 50% opacity | |

*Writing Achievements (4)*:
| Badge | Status | XP/Progress | Visual |
|-------|--------|-------------|--------|
| First Analysis ✍️ | Earned | +50 XP | Green check | |
| Voice Found 🎯 | Earned | +150 XP | Green check | |
| Prolific 📝 | Locked | 48/50 | 50% opacity | |
| Voice Master 👑 | Locked | 87% | 50% opacity | |

*Community (4)*:
| Badge | Status | XP/Progress | Visual |
|-------|--------|-------------|--------|
| Social 👋 | Earned | +100 XP | Green check | |
| Engaged 💬 | Earned | +150 XP | Green check | |
| Influencer ⭐ | Earned | +300 XP | Green check | |
| Thought Leader 🏆 | Locked | 234/1000 | 50% opacity | |

*Special (4)*:
| Badge | Status | XP/Progress | Visual |
|-------|--------|-------------|--------|
| Early Adopter 🚀 | Earned | +500 XP | Green check | |
| Beta Tester 🧪 | Earned | +250 XP | Green check | |
| Referrer 🎁 | Locked | 1/3 | 50% opacity | |
| Annual Pro 💎 | Locked | "Upgrade" | 50% opacity | |

**Leaderboard Teaser**:
| Test Case | Expected | Status |
|-----------|----------|--------|
| Top 3 displayed | Elena, Marcus, You | |
| "You" highlighted | Amber background | |
| Rank changes shown | +2, -1, +5 | |
| "View Full →" link | Links to leaderboard | |

### 4.2 Progressive Feature Unlocks (Free Users)

**Test Users**: U1 (3 days), U2 (14 days)
**Location**: Dashboard

| Test Case | Expected | Status |
|-----------|----------|--------|
| "Your Feature Journey" card visible | For free users only | |
| Shows "Day X of 7" | Correct day count | |
| 7-segment progress bar | Correct segments filled | |

**Day-by-Day Unlocks (U1 - Day 3)**:
| Day | Feature | Status for Day 3 |
|-----|---------|------------------|
| Day 1 | Basic Voice Analysis | ✓ Unlocked (green) | |
| Day 3 | Voice Profile | ✓ Unlocked (green) | |
| Day 5 | Author Comparison | 🔒 Locked (gray) | |
| Day 7 | History + 20% Off | 🔒 Locked (purple highlight) | |

**Day-by-Day Unlocks (U2 - Day 14)**:
| Day | Feature | Status for Day 14 |
|-----|---------|-------------------|
| Day 1 | Basic Voice Analysis | ✓ Unlocked | |
| Day 3 | Voice Profile | ✓ Unlocked | |
| Day 5 | Author Comparison | ✓ Unlocked | |
| Day 7 | History + 20% Off | ✓ Unlocked + "Claim 20% Off" | |

| Test Case | Expected | Status |
|-----------|----------|--------|
| Pro Features teaser at bottom | Always visible | |
| "Upgrade Now" CTA | Clickable | |
| NOT visible for paid users | Hidden for U3-U9 | |

---

## SECTION 5: EXISTING FEATURES RETEST

### 5.1 Dashboard Views (12)

| View | Access Test | Content Test | Dark Mode | Status |
|------|-------------|--------------|-----------|--------|
| Dashboard | All users | Metrics load | Consistent | |
| Discover | All users | Featured section | Consistent | |
| Streak/Achievements | All users | Full P3 system | Consistent | |
| Voice Profile | Pro+/V+S | Confidence circle | Consistent | |
| My Writing | Writers | Posts list | Consistent | |
| Writer Analytics | Writers | Charts render | Consistent | |
| Reading Paths | Curators | Paths list | Consistent | |
| Path Followers | Curators | Follower list | Consistent | |
| Authority Hub | Featured+ | Hub content | Consistent | |
| Leaderboard | Featured+ | Rankings | Consistent | |
| Settings | All users | 4 tabs work | Consistent | |
| Help | All users | FAQ system | Consistent | |

### 5.2 Settings Tabs (4)

| Tab | Content Test | Form Test | Save Test | Status |
|-----|--------------|-----------|-----------|--------|
| Profile | Avatar, name, bio | Fields editable | Changes save | |
| Preferences | Theme, language | Dropdowns work | Changes save | |
| Notifications | Toggles | All toggles work | State persists | |
| Billing | Plan, bundles, history | All P1/P2 features | CTAs work | |

### 5.3 Multi-Currency Display

| Country | Currency | Symbol | Verified Locations | Status |
|---------|----------|--------|-------------------|--------|
| CA | CAD | $ | Billing, Bundles, Annual | |
| GB | GBP | £ | Billing, Bundles, Annual | |
| AU | AUD | A$ | Billing, Bundles, Annual | |
| NZ | NZD | NZ$ | Billing, Bundles, Annual | |

### 5.4 Feature Gating Matrix

| Feature | Free | Pro | Curator | Featured | Authority |
|---------|------|-----|---------|----------|-----------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Discover | ✅ | ✅ | ✅ | ✅ | ✅ |
| Achievements | ✅ | ✅ | ✅ | ✅ | ✅ |
| My Writing | ❌ | ✅ | ❌ | ✅ | ✅ |
| Voice Profile | ❌* | ✅ | ❌* | ✅ | ✅ |
| Analytics | ❌ | ✅ | ✅ | ✅ | ✅ |
| Reading Paths | ❌ | ❌ | ✅ | ✅** | ✅** |
| Authority Hub | ❌ | ❌ | ❌ | ✅ | ✅ |
| Leaderboard | ❌ | ❌ | ❌ | ✅ | ✅ |

*Unlocked with Voice+Style addon
**Only if has Curator track

---

## SECTION 6: BRAND & STYLE ALIGNMENT

### 6.1 Color Palette Verification

| Element | Expected Color | Hex | Status |
|---------|----------------|-----|--------|
| Primary CTA | Coral | #FF6B6B | |
| Primary Hover | Darker Coral | #ff5252 | |
| Voice/V+S | Emerald | #10B981 | |
| Curator | Purple | #8B5CF6 | |
| Authority | Amber/Gold | #F59E0B | |
| Featured | Blue | #3B82F6 | |
| Growth Tier | Purple | #8B5CF6 | |

### 6.2 Typography Consistency

| Element | Font Weight | Size | Status |
|---------|-------------|------|--------|
| Page titles | Bold | 2xl | |
| Card headers | Semibold | Base | |
| Body text | Normal | Sm | |
| Muted text | Normal | Sm (gray) | |
| Badge text | Medium | Xs | |

### 6.3 Dark Mode Audit

| Component | Light Mode | Dark Mode | Status |
|-----------|------------|-----------|--------|
| Background | gray-50 | gray-950 | |
| Cards | white | gray-900 | |
| Borders | gray-200 | gray-800 | |
| Muted text | gray-500 | gray-400 | |
| All P1 features | Correct | Correct | |
| All P2 features | Correct | Correct | |
| All P3 features | Correct | Correct | |

### 6.4 Quirrely Mascot Presence

| Location | Logo Type | Status |
|----------|-----------|--------|
| Header | SVG mascot | |
| Auth pages | Full logo | |
| Loading states | Animated (if present) | |

---

## SECTION 7: MOBILE RESPONSIVENESS

### 7.1 Breakpoint Tests

| Breakpoint | Width | Components Test | Status |
|------------|-------|-----------------|--------|
| Mobile | <640px | Sidebar collapses, stacks | |
| Tablet | 640-1024px | 2-column grids | |
| Desktop | >1024px | Full layout | |

### 7.2 Mobile-Specific Tests

| Test | Expected | Status |
|------|----------|--------|
| Hamburger menu works | Opens sidebar | |
| Touch targets ≥44px | All buttons | |
| No horizontal scroll | Content fits | |
| Cards stack vertically | Single column | |
| Badges wrap properly | No overflow | |

---

## SECTION 8: CTA FUNCTIONALITY

### 8.1 All CTAs Inventory

| CTA | Location | Action | Status |
|-----|----------|--------|--------|
| Upgrade to Pro | First Analysis Hook | Alert/Modal | |
| Switch to Annual | Annual Banner | Alert/Modal | |
| Analyze Now | Badge Notification | Navigate | |
| View Details | Voice Notification | Navigate to Voice | |
| Explore Featured | Social Proof Notif | Alert/Modal | |
| Claim 20% Off | Progressive Day 7 | Alert/Modal | |
| Pause Subscription | Downgrade Prevention | Alert/Modal | |
| Stay & Save 50% | Downgrade Prevention | Alert/Modal | |
| Change Plan | Current Plan | Alert/Modal | |
| View Full → | Leaderboard Teaser | Navigate | |

---

## EXECUTION TIMELINE

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | 1 hour | User profiles, basic navigation |
| Phase 2 | 1 hour | P1 Quick Wins audit |
| Phase 3 | 1 hour | P2 Optimizations audit |
| Phase 4 | 1 hour | P3 Optimizations audit |
| Phase 5 | 30 min | Existing features retest |
| Phase 6 | 30 min | Brand/style/dark mode |
| Phase 7 | 30 min | Mobile responsiveness |
| Phase 8 | 30 min | CTA functionality |
| Reporting | 1 hour | Compile findings |

**Total: ~7 hours**

---

## SIGN-OFF

- [ ] All P1 features tested
- [ ] All P2 features tested
- [ ] All P3 features tested
- [ ] All user profiles verified
- [ ] All views audited
- [ ] Brand alignment confirmed
- [ ] Dark mode consistent
- [ ] Mobile responsive
- [ ] All CTAs functional

**QA Lead**: Kim
**Date**: February 16, 2026
**Version**: 3.1.0 (Knight of Wands MRR Optimized)
