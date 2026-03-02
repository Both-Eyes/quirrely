# SENTENSE v1.5.0 — LOCKED

## Lock Information

| Field | Value |
|-------|-------|
| **Version** | 1.5.0 |
| **Codename** | "Guardian" |
| **Lock Date** | February 10, 2026 22:30 UTC |
| **Lock Type** | HALO System Integration |
| **Previous Version** | v1.4.0 "Pre-Flight" |

---

## What's New in v1.5.0

### HALO System (Hate, Abuse, Language, Outcomes)

Complete content moderation system with three detection layers:

#### Frontend Detection (Layer 1)
- **File**: `halo-wrapper.js` (619 lines)
- Real-time pattern matching
- Instant user feedback (toasts, warnings, blocks)
- Session tracking for escalation
- Client-side rate limiting
- Bot detection (typing speed)
- Duplicate content prevention

#### Backend Detection (Layers 1+2)
- **File**: `backend/halo_detector.py` (554 lines)
- Extended blocklists (severe, moderate, mild)
- Contextual pattern matching
- Escalation logic (T1→T2→T3)
- Database logging
- Trust score calculation
- LLM classification hooks (prepared for Layer 3)

#### Database Schema
- **File**: `database/schema_halo.sql` (355 lines)
- 6 new tables:
  - `halo_violations` — Violation log
  - `user_halo_status` — Per-user moderation state
  - `session_halo_status` — Per-session tracking
  - `halo_appeals` — Appeal queue
  - `halo_blocked_hashes` — Content blocklist
  - `halo_daily_stats` — Analytics aggregates
- Automatic triggers for status updates
- Views for pending reviews and suspended users

### Updated Components

#### Submission Form
- **File**: `blog/submit-writing.html` (370 lines)
- Real-time HALO checking on all inputs
- Visual feedback (field highlighting)
- Warning/block modals
- Rate limiting integration
- Typing timer for bot detection

#### Super Admin Dashboard
- **File**: `super-admin-dashboard.html` (629 lines)
- New "🛡️ HALO" tab with:
  - Violation counts (T1/T2/T3)
  - Category breakdown (H/A/L/O)
  - Trend chart over 100 days
  - Pending review queue
  - Suspended users list
  - Formulas reference

---

## Tier System

| Tier | Name | Trigger | Action | Reversible |
|------|------|---------|--------|------------|
| T1 | Discourage | Profanity, mild insults, gaming | Warning toast | Immediate |
| T2 | Caution | Harassment, slurs, rate limits | 1hr cooldown | After cooldown |
| T3 | Suspend | Hate speech, threats, CSAM | Session terminated | Manual review |

### Escalation Rules
```
T1 × 3 (same session) → T2
T2 × 2 (7 days) → T3
T3 = Permanent (appeals only)
```

### Trust Score
```
Initial: 100
T1: -5 points
T2: -20 points
T3: → 0 (suspended)
Recovery: +1/day if clean
```

---

## Category Definitions

| Code | Name | Examples |
|------|------|----------|
| H | Hate | Slurs, supremacy, genocide advocacy |
| A | Abuse | Harassment, threats, doxxing, stalking |
| L | Language | Profanity, crude content, insults |
| O | Outcomes | Spam, bots, rate limiting, duplicates |

---

## Blocklist Coverage

| Severity | Patterns | Category |
|----------|----------|----------|
| Severe (T3) | 20+ patterns | H (Hate) |
| Moderate (T2) | 25+ patterns | A (Abuse) |
| Mild (T1) | 15+ patterns | L (Language) |
| Gaming | 6 patterns | O (Outcomes) |

---

## Integration Points

| Input | HALO Check | Tier Range |
|-------|------------|------------|
| Test writing sample | Real-time (debounced) | T1-T3 |
| Featured writer submission | Real-time | T1-T3 |
| Display name | On blur | T1-T3 |
| Bio | On blur | T1-T3 |

---

## Files Changed/Added

### New Files
```
halo-wrapper.js              (619 lines)
backend/halo_detector.py     (554 lines)
database/schema_halo.sql     (355 lines)
```

### Updated Files
```
blog/submit-writing.html     (370 lines) — HALO integration
super-admin-dashboard.html   (629 lines) — HALO tab
frontend/index.html          — HALO script reference
```

---

## Metrics Integration

HALO events are tracked on the same timeline as all other metrics:

| Metric | Day 100 | % of Visitors |
|--------|---------|---------------|
| Total Violations | 847 | 0.65% |
| T1 Warnings | 612 | 0.47% |
| T2 Cautions | 108 | 0.08% |
| T3 Blocks | 127 | 0.10% |

### By Category
| Category | Count | % of Violations |
|----------|-------|-----------------|
| H (Hate) | 89 | 10.5% |
| A (Abuse) | 156 | 18.4% |
| L (Language) | 423 | 49.9% |
| O (Outcomes) | 179 | 21.1% |

---

## E2E Test Results

| Test | Result |
|------|--------|
| JavaScript syntax | ✅ PASS |
| Python syntax | ✅ PASS |
| SQL schema (6 tables) | ✅ PASS |
| HTML integration | ✅ PASS |
| Detector unit tests | ✅ PASS |

---

## Version History

| Version | Date | Codename | Key Feature |
|---------|------|----------|-------------|
| v1.0.0 | — | — | First stable |
| v1.1.0 | Feb 9 | "The Listener" | Mobile UX |
| v1.2.0 | — | — | G2M Common |
| v1.3.0 | — | — | Pro tier |
| v1.4.0 | Feb 10 | "Pre-Flight" | E2E verified |
| **v1.5.0** | **Feb 10** | **"Guardian"** | **HALO System** |

---

**LOCKED** ✅

