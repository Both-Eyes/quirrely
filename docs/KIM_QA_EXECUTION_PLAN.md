# 🐿️ KIM'S 10-DAY QA EXECUTION PLAN
## Quirrely Comprehensive User Experience Testing
### Start Date: _____________

---

## PRE-FLIGHT CHECKLIST

Before starting Day 1, ensure you have:

- [ ] Access to QA environment (staging.quirrely.com)
- [ ] Password manager with test account credentials
- [ ] Bug tracking system access (Linear/Jira)
- [ ] Screen recording software (Loom/OBS)
- [ ] Multiple browsers installed (Chrome, Firefox, Safari, Edge)
- [ ] Mobile devices available (iPhone, Android)
- [ ] `seed_qa_test_users.sql` has been run on staging database
- [ ] Stripe test mode enabled with test cards ready
- [ ] Slack/communication channel with dev team

---

## DAY 1: SETUP & SMOKE TESTS

### Morning (4 hours)

#### 1.1 Account Verification (2 hours)
Log into each of the 14 Canadian test accounts and verify:

| Account | Expected Badge | Can Access |
|---------|---------------|------------|
| kim_free_none_ca | "Free" | Dashboard only |
| kim_free_vs_ca | "Free" + "✨ Voice + Style" | + Voice Profile, Paths, Authority |
| kim_pro_none_ca | "Pro" | + Analytics |
| kim_pro_vs_ca | "Pro" + "✨ Voice + Style" | + Voice Profile, Paths, Authority |
| kim_curator_none_ca | "Curator" | + Paths, Analytics |
| kim_curator_vs_ca | "Curator" + "✨ Voice + Style" | + Voice Profile, Authority |
| kim_fw_none_ca | "Featured Writer" | + Authority Hub |
| kim_fw_vs_ca | "Featured Writer" + "✨ Voice + Style" | + Voice Profile |
| kim_fc_none_ca | "Featured Curator" | + Authority Hub, Featured |
| kim_fc_vs_ca | "Featured Curator" + "✨ Voice + Style" | + Voice Profile |
| kim_aw_none_ca | "👑 Authority Writer" | Full access |
| kim_aw_vs_ca | "👑 Authority Writer" + "✨ Voice + Style" | Full access + Voice |
| kim_ac_none_ca | "👑 Authority Curator" | Full access |
| kim_ac_vs_ca | "👑 Authority Curator" + "✨ Voice + Style" | Full access + Voice |

**Checkpoint:** All 14 accounts work ✅

#### 1.2 Sidebar Navigation Audit (1 hour)

For EACH tier (use Canadian accounts):

| Sidebar Item | free | pro | curator | featured | authority |
|--------------|------|-----|---------|----------|-----------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Discover | ✅ | ✅ | ✅ | ✅ | ✅ |
| Bookmarks | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reading Streak | ✅ | ✅ | ✅ | ✅ | ✅ |
| My Writing | ✅ | ✅ | ✅ | ✅ | ✅ |
| Drafts | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voice Profile | ❌ | ❌ | ❌ | ❌ | ❌ |
| Analytics | ❌ | ✅ | ✅ | ✅ | ✅ |
| My Paths | ❌ | ❌ | ✅ | C | ✅ |
| Path Followers | ❌ | ❌ | ✅ | C | ✅ |
| Featured | ❌ | ❌ | ❌ | C | C |
| Authority Hub | ❌ | ❌ | ❌ | ✅ | ✅ |
| Leaderboard | ❌ | ❌ | ❌ | ✅ | ✅ |
| Impact Stats | ❌ | ❌ | ❌ | ✅ | ✅ |

Now check WITH voice_style addon:

| Sidebar Item | free+VS | pro+VS | curator+VS |
|--------------|---------|--------|------------|
| Voice Profile | ✅ | ✅ | ✅ |
| My Paths | ✅ | ✅ | ✅ |
| Authority Hub | ✅ | ✅ | ✅ |

**Checkpoint:** Navigation matches permissions ✅

#### 1.3 Quick Smoke Tests (1 hour)

- [ ] Light/Dark mode toggle works
- [ ] Country flag displays correctly
- [ ] Currency shows CAD
- [ ] No console errors
- [ ] All images load
- [ ] No broken links in navigation

### Afternoon (4 hours)

#### 1.4 Repeat for UK Accounts (2 hours)
Same verification as 1.1-1.3 but with UK accounts.
Verify currency shows GBP (£).

#### 1.5 Repeat for AU Accounts (1 hour)
Quick verification, verify currency shows AUD.

#### 1.6 Repeat for NZ Accounts (1 hour)
Quick verification, verify currency shows NZD.

### Day 1 Deliverable
- [ ] All 56 accounts verified working
- [ ] Bug report for any access issues
- [ ] Screenshot evidence of tier badges

---

## DAY 2: AUTHENTICATION FLOWS

### Morning (4 hours)

#### 2.1 Login Flow Testing

| Test Case | Steps | Expected | Pass? |
|-----------|-------|----------|-------|
| Valid login | Enter correct email/password | Redirect to dashboard | |
| Invalid password | Enter wrong password | Error toast | |
| Invalid email | Enter non-existent email | Error toast | |
| Empty fields | Submit empty form | Validation errors | |
| Remember me | Check "Remember me", close browser, reopen | Still logged in | |
| Forgot password | Click link, enter email | Reset email sent | |
| Password reset | Use reset link, enter new password | Can login with new password | |
| Google login | Click Google button | OAuth flow works | |
| Apple login | N/A | Button MUST NOT EXIST | |

#### 2.2 Signup Flow Testing

| Test Case | Steps | Expected | Pass? |
|-----------|-------|----------|-------|
| Valid signup | Fill all fields correctly | Account created, logged in | |
| Duplicate email | Use existing email | Error: email exists | |
| Weak password | Use "123456" | Validation error | |
| Country selector | Click dropdown | Shows CA, UK, AU, NZ ONLY | |
| No USA option | Look for USA | MUST NOT EXIST | |
| Terms checkbox | Uncheck, submit | Validation error | |
| Email verification | Check inbox | Verification email received | |

### Afternoon (4 hours)

#### 2.3 Session Management

| Test Case | Steps | Expected | Pass? |
|-----------|-------|----------|-------|
| Session expiry | Wait 24 hours, try action | Redirect to login | |
| Concurrent sessions | Login on 2 devices | Both work | |
| Logout | Click logout | Redirect to login, session cleared | |
| Token refresh | Stay active 30+ min | No logout | |

#### 2.4 Edge Cases

| Test Case | Steps | Expected | Pass? |
|-----------|-------|----------|-------|
| Direct URL while logged out | Go to /dashboard | Redirect to login | |
| Return to original page | Login after redirect | Return to /dashboard | |
| Incognito mode | Full login flow | Works normally | |

### Day 2 Deliverable
- [ ] All auth flows tested
- [ ] Bug report for any issues
- [ ] Evidence of NO Apple login button

---

## DAY 3-4: READER FEATURES

### Day 3: Discover & Bookmarks

#### 3.1 Discover Page (/reader/discover)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | free | Posts display in grid | |
| Search works | free | Filters by keyword | |
| Tag filter | free | Filters by tag | |
| Infinite scroll | free | More posts load | |
| Post card displays | free | Title, author, read time, tags | |
| Bookmark button | free | Toggles state | |
| Click post | free | Opens post detail | |
| Empty search | free | "No results" message | |

#### 3.2 Bookmarks Page (/reader/bookmarks)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | free | Bookmarked posts display | |
| Empty state | new user | "No bookmarks yet" CTA | |
| Remove bookmark | free | Post removed from list | |
| Search bookmarks | free | Filters saved posts | |
| Grid/List toggle | free | Layout changes | |

### Day 4: Reading Streak

#### 4.1 Streak Page (/reader/streak)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | free | Streak info displays | |
| Current streak | free | Day count shown | |
| Calendar | free | Monthly view | |
| Read days marked | free | Coral dots on read days | |
| Milestone progress | free | Visual bar | |
| Streak freeze | pro | Available | |
| Streak freeze | free | Not available / upgrade prompt | |

### Day 3-4 Deliverable
- [ ] All reader features tested
- [ ] Screenshots of empty states
- [ ] Bug report for any issues

---

## DAY 5: WRITER FEATURES

### Morning (4 hours)

#### 5.1 My Writing (/writer/posts)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | pro | Posts list displays | |
| Empty state | new user | "Start writing" CTA | |
| Filter tabs | pro | All/Published/Draft work | |
| Post stats | pro | Views, reads shown | |
| Edit button | pro | Opens editor | |
| Delete button | pro | Confirmation modal | |
| Delete confirm | pro | Post deleted | |

#### 5.2 Drafts (/writer/drafts)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | pro | Drafts list displays | |
| Last edited time | pro | Relative timestamp | |
| Quick publish | pro | Publishes immediately | |
| Edit draft | pro | Opens editor | |
| Delete draft | pro | With confirmation | |

### Afternoon (4 hours)

#### 5.3 Editor (/writer/editor)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| New post | pro | Empty editor loads | |
| Title input | pro | Can type title | |
| Content editor | pro | Rich text works | |
| Bold/Italic | pro | Formatting applies | |
| Tag input | pro | Can add/remove tags | |
| Preview toggle | pro | Shows preview | |
| Auto-save | pro | "Saving..." indicator | |
| Save draft | pro | Saves without publishing | |
| Publish | pro | Confirmation modal | |
| Word count | pro | Live updates | |
| Edit existing | pro | Loads post content | |

#### 5.4 Analytics (/writer/analytics) - PRO+ ONLY

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | pro | Analytics display | |
| Access denied | free | Redirect to dashboard | |
| Views chart | pro | Line graph shows | |
| Date range filter | pro | Changes data | |
| Top posts | pro | Ranked list | |

### Day 5 Deliverable
- [ ] All writer features tested
- [ ] Editor functionality verified
- [ ] Analytics access verified per tier

---

## DAY 6: VOICE PROFILE & CURATOR FEATURES

### Morning (4 hours)

#### 6.1 Voice Profile (/dashboard/voice) - VOICE_STYLE ONLY

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Access denied | pro (no VS) | Redirect | |
| Access denied | free | Redirect | |
| Page loads | pro+VS | Voice profile displays | |
| Page loads | curator+VS | Voice profile displays | |
| Page loads | free+VS | Voice profile displays | |
| Radar chart | pro+VS | 6 dimensions shown | |
| Dimension bars | pro+VS | Progress bars | |
| AI Insights | pro+VS | 3 insight cards | |
| Voice Evolution | pro+VS | Timeline history | |
| Export button | pro+VS | Download works | |
| Share button | pro+VS | Share modal | |

### Afternoon (4 hours)

#### 6.2 My Paths (/curator/paths) - CURATOR+ OR VOICE_STYLE

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Access denied | pro (no VS) | Redirect | |
| Access denied | free | Redirect | |
| Page loads | curator | Paths list displays | |
| Page loads | free+VS | Paths list displays | |
| Create path | curator | Opens editor | |
| Path stats | curator | Followers shown | |
| Publish/Unpublish | curator | Toggle works | |
| Edit path | curator | Opens editor | |
| Delete path | curator | With confirmation | |

#### 6.3 Path Editor

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| New path | curator | Empty editor | |
| Title input | curator | Can type title | |
| Description | curator | Textarea works | |
| Icon picker | curator | 12 emoji options | |
| Add posts | curator | Modal opens | |
| Search posts | curator | Filters posts | |
| Reorder posts | curator | Arrows work | |
| Remove post | curator | Post removed | |
| Save draft | curator | Saves | |
| Publish path | curator | Validates, publishes | |

### Day 6 Deliverable
- [ ] Voice Profile access verified (addon-only)
- [ ] Curator features verified (tier OR addon)
- [ ] Path creation flow tested

---

## DAY 7: AUTHORITY FEATURES

### Morning (4 hours)

#### 7.1 Authority Hub (/authority/hub) - FEATURED+ OR VOICE_STYLE

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Access denied | pro (no VS) | Redirect | |
| Access denied | curator (no VS) | Redirect | |
| Access granted | featured_writer | Page loads | |
| Access granted | free+VS | Page loads | |
| Authority score | authority_writer | Gold card | |
| Global rank | authority_writer | "#23" format | |
| Percentile | authority_writer | "Top 1%" | |
| Milestone progress | authority_writer | 5 milestones | |
| Badge showcase | authority_writer | Grid of badges | |

#### 7.2 Leaderboard (/authority/leaderboard)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | featured_writer | Leaderboard displays | |
| Global view | featured_writer | All countries | |
| Filter: Canada | featured_writer | Only 🇨🇦 | |
| Filter: UK | featured_writer | Only 🇬🇧 | |
| Filter: Australia | featured_writer | Only 🇦🇺 | |
| Filter: NZ | featured_writer | Only 🇳🇿 | |
| Top 3 styling | featured_writer | Gold/Silver/Bronze | |
| Current user | featured_writer | Highlighted | |

### Afternoon (4 hours)

#### 7.3 Impact Stats (/authority/impact)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | authority_curator | Stats display | |
| Total reach | authority_curator | Metric shown | |
| Influence score | authority_curator | Metric shown | |
| Trend chart | authority_curator | Line chart | |
| Category breakdown | authority_curator | Pie chart | |

### Day 7 Deliverable
- [ ] All Authority features tested
- [ ] Leaderboard filters work per country
- [ ] Access control verified

---

## DAY 8: SETTINGS & EDGE CASES

### Morning (4 hours)

#### 8.1 Settings Page (/dashboard/settings)

| Test Case | Account | Expected | Pass? |
|-----------|---------|----------|-------|
| Page loads | all | Settings display | |
| Profile section | all | Name, email, avatar | |
| Change name | all | Updates successfully | |
| Country display | CA | 🇨🇦 Canada shown | |
| Country display | UK | 🇬🇧 UK shown | |
| Change password | all | Works | |
| Notification toggles | all | Work | |
| Delete account | all | Confirmation modal | |
| Billing section | free | Not shown | |
| Billing section | pro | Shows subscription | |
| Cancel subscription | pro | Processes | |
| Currency: CA | CA | CAD | |
| Currency: UK | UK | GBP | |
| Currency: AU | AU | AUD | |
| Currency: NZ | NZ | NZD | |

#### 8.2 Error States

| Test Case | Expected | Pass? |
|-----------|----------|-------|
| 404 page | Squirrel + message | |
| Go Back button | Works | |
| Network error | Error message | |

### Afternoon (4 hours)

#### 8.3 Permission Edge Cases

| Test Case | Expected | Pass? |
|-----------|----------|-------|
| Direct URL /authority/hub as free | Redirect | |
| Direct URL /dashboard/voice as pro | Redirect | |
| Direct URL /authority/hub as pro+VS | Works | |

### Day 8 Deliverable
- [ ] Settings fully tested
- [ ] All error states verified
- [ ] Edge cases documented

---

## DAY 9: CROSS-BROWSER & MOBILE

### Morning: Browser Testing (4 hours)

For EACH browser (Chrome, Firefox, Safari, Edge):
- [ ] Login works
- [ ] Dashboard loads
- [ ] Navigation works
- [ ] Forms submit
- [ ] Modals work
- [ ] No console errors

### Afternoon: Mobile Testing (4 hours)

**iPhone Safari**
- [ ] Responsive layout
- [ ] Sidebar opens/closes
- [ ] Touch interactions
- [ ] Forms usable

**Android Chrome**
- [ ] Responsive layout
- [ ] Sidebar opens/closes
- [ ] Back button works

### Day 9 Deliverable
- [ ] Browser matrix complete
- [ ] Mobile issues documented

---

## DAY 9b: BROWSER EXTENSION TESTING

### Morning: Chrome Extension (4 hours)

#### Installation & Setup
| Test | Expected | Pass? |
|------|----------|-------|
| Install from Chrome Web Store | Installs successfully | |
| Extension icon in toolbar | Visible | |
| Click icon (logged out) | Login prompt | |
| Login via extension | Authenticates | |
| Session syncs with web app | Same user shown | |

#### Core Functionality
| Test | Account | Expected | Pass? |
|------|---------|----------|-------|
| Highlight text on webpage | any | Context menu shows "Analyze" | |
| Analyze text | free | Results display (limited) | |
| Analyze text | pro | Full results | |
| Save to account | free | Blocked/upgrade prompt | |
| Save to account | pro | Saves successfully | |
| View history | pro | Shows past analyses | |
| Voice insights | pro (no VS) | Not shown | |
| Voice insights | pro+VS | Shown | |

#### Site Compatibility
| Site | Works? | Notes |
|------|--------|-------|
| Medium.com | | |
| Substack.com | | |
| WordPress sites | | |
| Twitter/X | | |
| LinkedIn | | |
| Google Docs | | (may not work) |
| PDF in browser | | |
| News sites (BBC, Guardian) | | |

#### Edge Cases
- [ ] Extension with expired subscription
- [ ] Logout mid-analysis
- [ ] Very long text selection (5000+ words)
- [ ] Text with special characters/emoji
- [ ] Multiple tabs analyzing simultaneously
- [ ] Extension popup while offline

### Afternoon: Firefox Extension (3 hours)

#### Installation & Setup
| Test | Expected | Pass? |
|------|----------|-------|
| Install from Firefox Add-ons | Installs successfully | |
| Extension icon in toolbar | Visible | |
| Login via extension | Authenticates | |
| Session syncs with web app | Same user | |

#### Core Functionality (repeat Chrome tests)
- [ ] Analyze text works
- [ ] Save results (paid tiers)
- [ ] Tier permissions respected
- [ ] History accessible

#### Cross-Browser Parity
| Feature | Chrome | Firefox | Parity? |
|---------|--------|---------|---------|
| Analyze text | | | |
| Save results | | | |
| View history | | | |
| Voice insights | | | |
| Settings sync | | | |

### Day 9b Deliverable
- [ ] Chrome extension fully tested
- [ ] Firefox extension fully tested
- [ ] Site compatibility matrix complete
- [ ] Extension bugs documented

---

## DAY 10: USER JOURNEYS & FINAL REPORT

### Morning: Complete Journeys (4 hours)

**Journey 1: Free → Pro (Canada)**
1. Log in as free_none_ca
2. Try Analytics → Blocked ✅/❌
3. Upgrade to Pro
4. Pay with test card
5. Analytics → Works ✅/❌

**Journey 2: Pro + voice_style (UK)**
1. Log in as pro_none_uk
2. Try Voice Profile → Blocked ✅/❌
3. Add voice_style
4. Voice Profile → Works ✅/❌
5. Authority Hub → Works ✅/❌

**Journey 3: Curator Path Creation (AU)**
1. Log in as curator_none_au
2. Create path
3. Add posts
4. Publish

**Journey 4: Authority Experience (NZ)**
1. Log in as authority_writer_nz
2. All Authority features work

### Afternoon: Final Report (4 hours)

**Summary:**
- Total tests: ______
- Passed: ______
- Failed: ______
- Pass rate: ______%

**Critical Issues:** (List any blockers)

**Recommendation:**
- [ ] READY FOR RELEASE
- [ ] NEEDS FIXES
- [ ] NOT READY

---

## QUICK REFERENCE

### Test Accounts (Password: QuirrelyQA2026!)
```
kim_{tier}_{addon}_{country}@test.quirrely.com

Examples:
kim_free_none_ca@test.quirrely.com
kim_pro_vs_uk@test.quirrely.com
kim_authority_curator_none_au@test.quirrely.com
```

### Stripe Test Cards
```
Canada:      4000001240000000
UK:          4000008260000000
Australia:   4000000360000006
New Zealand: 4000005540000008
Decline:     4000000000000002
```

---

## SIGN-OFF

**QA Lead:** Kim
**Date Completed:** _______________
**Final Status:** _______________

QA Lead: _______________________
Dev Lead: _______________________
Product Owner: _______________________
