# QUIRRELY MILESTONE SYSTEM IMPLEMENTATION
## Original Writing Recognition & Featured Writer Flow

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## What Was Decided

### Milestone Structure

| Milestone | Trigger | User Type | Animation | Color |
|-----------|---------|-----------|-----------|-------|
| **First 500** | 500 keystroke words (lifetime) | ANY | Acorn Collect | Coral (#FF6B6B) |
| **3-Day Streak** | 500+/day, 3 consecutive days | Auth'd (any tier) | Acorn Stack | Coral |
| **Daily 1K** | 1,000 keystroke words (single day) | PRO only | Glow Pulse | Coral → Soft Gold |
| **3-Day 1K Streak** | 1,000+/day, 3 consecutive days | PRO only | Golden Acorn Crown | Soft Gold (#D4A574) |
| **7-Day 1K Streak** | 1,000+/day, 7 consecutive days | PRO only | Golden Acorn Ring | Soft Gold |
| **14-Day 1K Streak** | 1,000+/day, 14 consecutive days | PRO only | Golden Acorn Orbit | Soft Gold |
| **30-Day 1K Streak** | 1,000+/day, 30 consecutive days | PRO only | Golden Acorn Tree | Soft Gold + flair |

### Featured Writer Flow

1. **Eligibility:** PRO + 7-Day 1K Streak
2. **Submission:** ≤500 words, keystroke-only (paste blocked), 3 agreements checked
3. **Review:** Editorial review (quality/fit)
4. **Outcome:** Featured badge + published piece + profile link

### Agreements (All Required)

- ☐ This is entirely my original writing (typed by me, not pasted or AI-generated)
- ☐ I grant Quirrely permission to feature this piece without compensation (this may change in the future)
- ☐ This is 500 words or fewer

### Save Consent (Voice Profile)

- **Toggle default:** OFF (respects privacy)
- **Prompts at key moments:**
  - First analysis (auth'd, save OFF)
  - Near milestone
  - Returning user (once per week)
  - Visitor signup prompt
- **Without save:** Milestones don't accumulate, session-only data

### Badges

- **Public on profiles:** Yes
- **Display order:** By tier (most impressive first)
- **Shareable cards:** LinkedIn + Facebook optimized (1200×630)

---

## Files Created

### Backend

| File | Purpose | Lines |
|------|---------|-------|
| `backend/milestone_tracker.py` | Core milestone tracking logic | ~450 |
| `backend/milestone_api.py` | API endpoints for milestones | ~200 |
| `backend/schema_milestones.sql` | Database schema + functions | ~300 |

### Frontend

| File | Purpose | Lines |
|------|---------|-------|
| `frontend/components/milestone-celebrations.js` | Celebration overlays + animations | ~700 |
| `frontend/components/featured-submission-form.js` | Featured Writer submission | ~400 |
| `frontend/components/save-consent-prompts.js` | Save consent + voice profile prompts | ~450 |

---

## API Endpoints Added

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/milestones/me` | Get current user's milestone state |
| GET | `/api/v2/milestones/badges` | Get current user's badges |
| GET | `/api/v2/milestones/badges/{username}` | Get public user's badges |
| GET | `/api/v2/milestones/definitions` | Get all milestone definitions |
| GET | `/api/v2/milestones/featured/eligibility` | Check Featured Writer eligibility |
| POST | `/api/v2/milestones/featured/submit` | Submit for Featured Writer |
| GET | `/api/v2/milestones/featured/submission` | Get pending submission status |
| GET | `/api/v2/milestones/admin/submissions` | Admin: Get pending submissions |
| POST | `/api/v2/milestones/admin/submissions/{id}/review` | Admin: Review submission |

---

## Database Tables Added

| Table | Purpose |
|-------|---------|
| `user_milestones` | User milestone state (streaks, achievements) |
| `daily_keystroke_totals` | Per-day keystroke word tracking |
| `milestone_events` | Audit log of triggered milestones |
| `featured_submissions` | Submission queue for Featured Writer |
| `featured_writers` | Published Featured Writers |

---

## Animations Defined

| Animation | Description | Used For |
|-----------|-------------|----------|
| **Acorn Collect** | Single acorn drops, sparkles | First 500 |
| **Acorn Stack** | 3 acorns stack horizontally | 3-Day Streak |
| **Glow Pulse** | Coral → Gold pulsing rings | Daily 1K |
| **Golden Acorn Crown** | 3 golden acorns form crown arc | 3-Day 1K |
| **Golden Acorn Ring** | 7 golden acorns form circle | 7-Day 1K |
| **Golden Acorn Orbit** | Acorns orbit, form double ring | 14-Day 1K |
| **Golden Acorn Tree** | Acorns cascade, form tree shape | 30-Day 1K |

All animations use Soft Gold (#D4A574) for PRO milestones, Coral (#FF6B6B) for others.

---

## Trial Conversion Integration

The 7-day trial aligns with 7-day 1K streak:

```
Day 1-6: User builds streak toward 7-day 1K
Day 7:   Trial ends + 7-day 1K achieved (if consistent)
         → "You've unlocked Featured Writer eligibility!"
         → "Upgrade to PRO to keep your streak and submit."
         
Loss aversion: User invested 7K+ words, doesn't want to lose progress.
```

---

## Core Invariants (Protected)

This system is **additive** — it does NOT change:

- ❌ LNCP classification logic
- ❌ Word limits (500/2000/10000)
- ❌ Input method detection
- ❌ Profile types or stances
- ❌ Analysis accuracy

It only tracks **keystroke words over time** and celebrates milestones.

---

## What's NOT Implemented Yet

| Item | Status | Notes |
|------|--------|-------|
| Actual SVG animation files | Defined in JS | Ready for design polish |
| Shareable card image generation | Template ready | Needs html2canvas or server-side |
| Featured Writers page | Schema ready | Needs frontend page |
| Admin review UI | API ready | Needs admin dashboard |
| Email notifications | Not started | For submission decisions |

---

## Integration Points

### On Every Analysis (with keystroke input)

```python
# In api_v2.py analyze endpoint
from milestone_api import process_milestones_after_analysis

# After successful analysis
milestones = process_milestones_after_analysis(
    user_id=user_id,
    keystroke_words=word_count,
    tier=user_tier,
    is_authenticated=True,
    save_enabled=user.save_enabled,
)

# Return in response
response["milestones"] = milestones
```

### Frontend: Show Celebration

```javascript
// After analysis response
if (response.milestones && response.milestones.length > 0) {
  const celebration = document.querySelector('milestone-celebration');
  celebration.show(response.milestones[0]);
}
```

---

## Summary

**Implemented:** Complete backend + frontend for milestone tracking, celebrations, Featured Writer submissions, and save consent prompts.

**Ready for:** Integration with existing analyze flow, design polish on animations, and admin review UI.

**Philosophy:** Quietly encourage original writing by celebrating keystroke input. Users who invest in Quirrely (via writing) get recognized. PRO users who maintain 7-day 1K streaks can become Featured Writers.
