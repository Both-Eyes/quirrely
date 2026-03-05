# LNCP v0.8 — LOCKED

**Lock Date:** February 8, 2026  
**Status:** ✅ LOCKED — Do not modify without version increment

---

## What's in This Version

### Core Features
- **3-round progressive analysis** with cumulative sentence collection
- **10 rhetorical profiles**: MINIMAL, DENSE, POETIC, INTERROGATIVE, ASSERTIVE, HEDGED, CONVERSATIONAL, LONGFORM, PARALLEL, PARENTHETICAL
- **5 epistemic stances**: MINIMAL, OPEN, CLOSED, BALANCED, CONTRADICTORY
- **40 stance-modified profile variants** (profile × stance combinations)
- **Sentence-by-sentence analysis** with notable sentence detection
- **Social sharing** (Facebook, Twitter/X, LinkedIn, Copy) on final analysis

### Detection Algorithm (v0.7.3+)
- Word boundary regex (`\b...\b`) for precise marker matching
- Occurrence counting (not just presence detection)
- Tightened CONVERSATIONAL (requires 2+ signals)
- Strong anaphora (60%+) overrides CONVERSATIONAL
- Positive MINIMAL definition (specific criteria, not default)
- CONTRADICTORY requires 4+ markers of each type
- BALANCED uses 35-65% ratio range

### Warm Workshop Theme (v0.8)
**Color Palette ("Morning Pages")**
- Background: `#FDF8F3` (warm cream)
- Text: `#3D3229` (warm charcoal)
- Accent: `#C4785A` (terracotta)
- Secondary: `#8B9E8B` (sage)
- Highlight: `#F5E6D3` (blush)

**Typography ("Classic Workshop")**
- Headers: Playfair Display
- Body: Source Serif Pro
- Data: IBM Plex Mono

**Profile Icons (Organic Symbols)**
| Profile | Icon |
|---------|------|
| MINIMAL | ○ |
| DENSE | ◉ |
| POETIC | ✦ |
| INTERROGATIVE | ◇ |
| ASSERTIVE | ▸ |
| HEDGED | ≈ |
| CONVERSATIONAL | ❧ |
| LONGFORM | ───── |
| PARALLEL | ║ |
| PARENTHETICAL | ⟨⟩ |

**Stance Icons (Spectrum Symbols)**
| Stance | Icon |
|--------|------|
| MINIMAL | · |
| OPEN | ◠ |
| CLOSED | ● |
| BALANCED | ⚖ |
| CONTRADICTORY | ⟷ |

**UI Components**
- Stepping stones progress: `◉ ─ ─ ○ ─ ─ ○` (visible on all screens)
- Soft pill buttons (border-radius: 50px)
- Soft cards (16px radius, gentle shadows)
- Gentle slide animations with stagger

### "I Notice" Section (Profile-Aware Nudges)
- **Profile-specific observations** (10 profiles × 3 variants each)
- **Stance additions** appended to observation
- **Profile-specific questions** (10 profiles × 3 each)
- **General exploratory questions** (6 variants)
- Questions alternate between profile-specific and general across rounds

### Social Sharing (Final Round Only)
- Share section appears under progress bar on Round 3
- **Facebook** — Share dialog with profile title + essence
- **Twitter/X** — Tweet with profile icon, title, excerpt
- **LinkedIn** — Share link
- **Copy** — Clipboard with "✓ Copied!" confirmation

### Removed Features
- "Try This" exercise section (removed in v0.8)

---

## Files

```
/mnt/user-data/outputs/lncp-web-app/
├── frontend/
│   └── index.html          # Main application (single-page)
└── LOCK_v0.8.md           # This document
```

---

## Test Results (57/57 ✅)

### UI Components: 32/32
- Version badge, progress container, stepping stones
- Warm Workshop colors (Morning Pages palette)
- Soft pill buttons, soft cards
- Profile icons (10), stance icons (5)
- Profile-specific observations and questions
- Share section with all 4 buttons
- Share only on final round
- No "Try This" section

### Flow Logic: 10/10
- 3 rounds (MAX_ROUNDS = 3)
- Input, story, results screens
- All navigation functions
- Accumulated sentences tracking
- Progress updates per round

### Profiles & Stances: 15/15
- All 10 profiles with icons and definitions
- All 5 stances with badges and detection

---

## To Unlock

1. Increment version to v0.9 or v1.0
2. Document changes in new lock file
3. Run E2E tests before re-locking

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v0.1-v0.6 | Feb 2026 | Core profiles, stances, language sets |
| v0.7.0 | Feb 2026 | Single-page frontend, profile tab |
| v0.7.1 | Feb 2026 | Notable sentences, stance-modified titles |
| v0.7.2 | Feb 2026 | Mass testing (3,500 samples) |
| v0.7.3 | Feb 2026 | Detection improvements (+10% accuracy) |
| **v0.8** | **Feb 2026** | **Warm Workshop theme, profile-aware nudges, progress on all screens, social sharing** |
