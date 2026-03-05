# Quirrely Changelog

## v3.1.3 — "The Stretched Squirrel" (2026-02-20)

### New Systems
- STRETCH writing exercise system — 8 API endpoints (/eligibility, /recommend, /start,
  /current, /prompt, /input, /progress, /cta) with zero-tolerance paste detection
- STRETCH prompt dataset — 450 base prompts (10 profiles × 5 cycles × 3 positions × 3 variants)
- stretch-components.js — portable STRETCH UI with KeystrokeTracker, StretchAPIClient,
  full StretchComponent lifecycle for extension popup and standalone pages
- funnel_observer.py — full conversion funnel observer with stage metrics,
  STRETCH lift signals, K-factor, and benchmark proposal generation
- viral_observer.py — viral/referral observer with share surface tracking,
  K-factor calculation, referral chain quality scoring

### Integration Fixes (v3.1.3-FINAL)
- app.py now imports and mounts stretch_api router at /api prefix
- /api/quick-analyze alias added to api_v2.py (delegates to analyze_text,
  Chrome extension v1 compatibility)
- psycopg2-binary>=2.9.9 and stripe>=7.0.0 added to requirements.txt
- schema_halo.sql staged to backend/ alongside migration sequence schemas
- JWT import + Token Architecture docstring added to auth_api.py (two-layer auth clarified)
- PROFILES_MANIFEST.md created — ANALYTICAL confirmed as canonical 10th profile
- compat.css + compat.js path resolution fixed; 91/91 blog HTML files patched
- index.html analyze button: id="quick-analyze" + data-endpoint="/api/quick-analyze"

### Infrastructure
- Chrome Extension v2.0.0 (Manifest V3, offline Quinquaginta v3.8 classifier)
- schema_stretch.sql — 11 new tables for STRETCH exercise system
- schema_halo.sql — HALO safety layer tables now in backend/ migration sequence
- assets/css/compat.css — cross-browser normalisation (334 lines)
- assets/js/compat.js — runtime browser fixes (253 lines)
- assets/css/responsive.css — mobile breakpoints (511 lines)

### Meta Orchestrator (8/8 observers)
stretch_observer, revenue_observer, retention_observer, funnel_observer,
viral_observer, achievement_observer, attribution_tracker, blog_observer

### Audit Score
202/202 checks passing (100%) — Static Auditor v1.0, 14 phases, 215 total checks

---

## v3.1.2 — "Knight of Wands" (2026-02-17)

### Social Links Integration
- Added LinkedIn company page link (https://www.linkedin.com/company/111631951/)
- LinkedIn icon in footer (all pages)
- LinkedIn icon in nav (dashboard pages)
- Facebook placeholder (hidden, `display: none` until URL ready)
- **105 files updated** across frontend, auth, billing, legal, blog

### Bug Fixes
- Fixed truncated legal pages (privacy, terms, affiliate-disclosure)
- Fixed truncated export.html

---

## v3.1.1 — "Bright Canvas" (2026-02-16)

### Theme
- Warm cream background (#FFFBF5)
- Coral primary (#FF6B6B)
- Teal secondary (#4ECDC4)
- Yellow accent (#FFE66D)
- Outfit (display) + Nunito Sans (body) typography
- Squirrel mascot integration

---

## v1.4.0 — "Pre-Flight" (2026-02-09)

### Mobile UX
- 44-48px touch targets, 16px inputs (prevents iOS zoom)
- Stacked layouts on mobile, landscape optimizations

### Compare Feature
- Compatibility score (0-100%), side-by-side metrics, 25+ profile pair insights

### Historical Tracking
- 10-session localStorage history, trend indicators, consistency scoring

### Save Feature
- Email-to-self via mailto

### Returning Users
- Welcome back banner, view saved profile, persistent identity
