# STRETCH Exercise System — Implementation Documentation

## Version 1.0.0 | February 2026

---

## Overview

STRETCH is a guided writing exercise system that helps users develop their voice by writing in profiles different from their natural style. Users who complete 5 rounds of analysis on any paid tier become eligible.

### Core Concept

**1 STRETCH = 5 Cycles × 3 Prompts × 100+ words = 2,500+ words minimum**

Each exercise stretches a user FROM their current profile TO a target profile (e.g., ASSERTIVE → HEDGED).

---

## Resolved Specifications

| Specification | Value |
|--------------|-------|
| Paste Detection | 100% enforcement. Zero tolerance. No appeals. |
| Prompt Bank Size | 450 base prompts (10 profiles × 5 cycles × 3 positions × 3 variants) |
| Growth Mapping | Both opposites AND adjacent growth valid |
| Tier Differentiation | Pro: 3 types (opposites) / Authority: 6 types / Curator: 10 types |
| Time Limits | Open-ended, 7-day completion incentive for trial→paid conversion |
| Failure States | Save at last cycle completion, surface for resume |
| Country Groups | Commonwealth (CA, UK, AU, NZ, IE) + US |

---

## Profile Stretch Matrix

### Opposite Pairs (Maximum Stretch, Difficulty 5)

| From | To | Rationale |
|------|-----|-----------|
| ASSERTIVE | HEDGED | Certainty ↔ Qualification |
| ASSERTIVE | POETIC | Direct ↔ Evocative |
| CONVERSATIONAL | FORMAL | Casual ↔ Elevated |
| DENSE | MINIMAL | Layered ↔ Stripped |
| FORMAL | POETIC | Precise ↔ Lyrical |
| INTERROGATIVE | MINIMAL | Questions ↔ Statements |
| LONGFORM | MINIMAL | Extended ↔ Compressed |

### All Adjacent Stretches

All non-opposite profile combinations are valid as adjacent stretches (difficulty 2-4).

---

## Implementation Files

### Database Schema

**File:** `backend/schema_stretch.sql`  
**Size:** 31 KB (650 lines)

Tables created:
- `stretch_mappings` — Valid FROM→TO combinations with growth type
- `tier_stretch_config` — Tier-based access rules
- `tier_stretch_allowlist` — Specific stretches per tier
- `stretch_prompts_base` — 450 base prompts
- `prompt_modifiers_country` — Commonwealth vs US modifications
- `prompt_modifiers_stance` — OPEN/CLOSED/BALANCED/CONTRADICTORY suffixes
- `stretch_exercises` — User exercise records
- `stretch_cycles` — 5 cycles per exercise
- `stretch_inputs` — 3 inputs per cycle (15 per exercise)
- `user_stretch_stats` — Lifetime accumulation (never decreases)
- `stretch_eligibility` — Eligibility and CTA tracking

### Backend API

**File:** `backend/stretch_api.py`  
**Size:** 26 KB (721 lines)

Endpoints:
- `GET /stretch/eligibility/{user_id}` — Check eligibility
- `GET /stretch/recommend/{user_id}` — Get recommendations
- `POST /stretch/start` — Start exercise
- `GET /stretch/current/{user_id}` — Current exercise
- `GET /stretch/prompt/{exercise_id}/{cycle}/{prompt}` — Get prompt
- `POST /stretch/input/{exercise_id}/{cycle}/{prompt}` — Submit input
- `GET /stretch/progress/{user_id}` — Dashboard data
- `GET /stretch/cta/{user_id}` — CTA data

Classes:
- `KeystrokeValidator` — 100% paste detection, zero tolerance
- `PromptResolver` — Applies country/stance modifiers
- `StretchRecommender` — Tier-aware recommendations

### Prompt Generator

**File:** `backend/generate_stretch_prompts.py`  
**Size:** 28 KB (539 lines)

Generates 450 base prompts with:
- Story starters per profile (evocative openings)
- Instructions per profile (voice guidance)
- Word guidance from profile traits

### Generated Prompt Bank

**Files:**
- `backend/stretch_prompts_base.json` — 342 KB (full data)
- `backend/stretch_prompts_base.sql` — 250 KB (INSERT statements)

Distribution: 45 prompts per profile (5 cycles × 3 positions × 3 variants)

### Frontend — Keystroke Tracker

**File:** `frontend/js/stretch-keystroke-tracker.js`  
**Size:** 14 KB (392 lines)

Features:
- Blocks paste at event level
- Blocks Ctrl+V / Cmd+V
- Blocks drag-and-drop
- Tracks every keystroke with timing
- Detects suspicious input patterns
- Real-time word counting
- Visual paste warning

### Frontend — Components

**File:** `frontend/components/stretch-components.js`  
**Size:** 39 KB (1,013 lines)

Components:
- `StretchOffer` — CTA variants (card, banner, sidebar, inline)
- `StretchProgress` — Progress display (full, compact, mini)
- `StretchExerciseUI` — Main exercise interface

### Meta Orchestrator Observer

**File:** `lncp/meta/stretch_observer.py`  
**Size:** 21 KB (494 lines)

Event types tracked:
- Eligibility changes
- CTA engagement
- Exercise lifecycle
- Cycle/input events
- Word accumulation
- Paste attempts

Signals generated:
- `engagement_opportunity`
- `high_intent`
- `commitment`
- `trial_engagement`
- `achievement`
- `conversion_ready`
- `churn_risk`
- `progress`
- `content_created`
- `friction`

---

## Data Flow

```
User completes 5 analysis rounds
        ↓
stretch_eligibility.is_eligible = TRUE
        ↓
CTA appears in dashboard/sidebar/funnel
        ↓
User clicks CTA → stretch_exercises created
        ↓
Prompt resolved (base + country + stance modifiers)
        ↓
User types (keystrokes tracked, paste blocked)
        ↓
Input submitted → KeystrokeValidator checks
        ↓
If valid: stretch_inputs saved, stats updated
        ↓
3 prompts → cycle complete
        ↓
5 cycles → exercise complete
        ↓
Signals sent to meta orchestrator
        ↓
Future recommendations personalized
```

---

## Tier Access

| Tier | Max Types | Opposites | Adjacents | Features |
|------|-----------|-----------|-----------|----------|
| Free | 0 | ✗ | ✗ | Not available |
| Pro | 3 | ✓ (limited) | ✗ | Basic progress |
| Authority | 6 | ✓ (all) | ✓ (limited) | Analytics, voice comparison |
| Curator | 10 | ✓ (all) | ✓ (all) | All + custom creation |

### Pro Tier Stretches
1. ASSERTIVE ↔ HEDGED
2. DENSE ↔ MINIMAL
3. FORMAL ↔ CONVERSATIONAL

---

## 7-Day Trial Incentive

Trial users who start STRETCH within their 7-day window:

1. **Day 1-3:** Encouragement to continue
2. **Day 4-5:** Progress reminders
3. **Day 6-7:** Urgency + upgrade prompt
4. **Trial expired:** Progress saved, locked behind paywall

Completion during trial triggers `conversion_ready` signal (strength 0.95).

---

## Word Accumulation

- Every keystroke-validated word adds to `user_stretch_stats.total_words_written`
- This counter **never decreases**
- Displayed prominently in dashboard
- Separate from analysis word counts
- Contributes to profile exploration tracking

---

## Future Expansion Hooks

The system is designed for extensibility:

1. **Additional stretch types** — Genre stretches, format stretches
2. **Collaborative stretches** — Multiple users
3. **Timed challenges** — Speed writing
4. **Leaderboards** — Competition
5. **LLM prompt generation** — Dynamic prompts based on user history
6. **Custom stretches** — Curator tier feature

---

## Integration Points

### Dashboard
- `StretchOffer` component (card variant)
- `StretchProgress` component (full variant)

### Sidebar
- `StretchOffer` component (sidebar variant)
- `StretchProgress` component (mini variant)

### Post-Analysis Funnel
- `StretchOffer` component (inline variant)
- Shows after 5th round completion

### Meta Orchestrator
- `StretchObserver` registered on startup
- Receives all STRETCH events
- Generates learning signals
- Informs recommendation engine

---

## Testing Checklist

- [ ] Eligibility check (5 rounds + paid tier)
- [ ] Paste blocking (all methods)
- [ ] Keystroke tracking accuracy
- [ ] Word count validation (100 minimum)
- [ ] Cycle completion flow
- [ ] Exercise completion flow
- [ ] Progress persistence
- [ ] Resume from abandonment
- [ ] Trial incentive tracking
- [ ] Tier access enforcement
- [ ] Country modifier application
- [ ] Stance modifier application
- [ ] Recommendation generation
- [ ] Signal emission to orchestrator

---

*Document generated: February 2026*
*STRETCH System v1.0.0*
