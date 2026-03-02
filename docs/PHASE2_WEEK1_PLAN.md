# PHASE 2 WEEK 1: IMPLEMENTATION PLAN
## Public Launch Preparation - Security & Meta Foundation

---

**Sprint:** Phase 2, Week 1  
**Start:** February 15, 2026  
**Status:** ✅ COMPLETE  
**Focus:** Security hardening + Meta event foundation  

---

## DELIVERABLES

| ID | Task | Est. Hours | Priority | Status |
|----|------|------------|----------|--------|
| SEC-002 | Backend country enforcement (GeoIP) | 2h | CRITICAL | ✅ DONE |
| SEC-003 | Audit API endpoints for @require_feature | 4h | CRITICAL | ✅ DONE |
| META-001 | Frontend event emission system | 2h | HIGH | ✅ DONE |

**Total:** 8 hours

---

## COMPLETED WORK

### SEC-002: Backend Country Enforcement ✅

**Files Created:**
- `backend/middleware/country_gate.py` (450 lines)
- `backend/middleware/__init__.py`

**Features Implemented:**
- GeoIP lookup (MaxMind + IP-API fallback)
- Allowed countries: CA, GB, AU, NZ
- Blocked countries: US (explicit)
- Local IP bypass for development
- FastAPI middleware + dependency options
- Admin functions for runtime config
- Audit logging for blocked requests

**Usage:**
```python
# As middleware (recommended)
from middleware.country_gate import CountryGateMiddleware
app.add_middleware(CountryGateMiddleware)

# Or as dependency
from middleware.country_gate import require_allowed_country
@router.get("/protected")
async def endpoint(country = Depends(require_allowed_country)):
    ...
```

---

### SEC-003: API Endpoint Security Audit ✅

**Files Created:**
- `docs/SEC003_API_SECURITY_AUDIT.md` (full audit report)
- `backend/dependencies.py` (reusable FastAPI dependencies)

**Audit Results:**
- 14 API files audited
- ~85 total endpoints
- ~60 protected endpoints
- 3 minor issues documented (non-blocking)

**Dependencies Created:**
- `get_current_user` - Authentication
- `require_feature_dep(feature)` - Feature gating
- `require_tier([tiers])` - Tier checking
- `require_addon(addon)` - Addon checking
- `require_admin` - Admin access
- `require_super_admin` - Super admin access
- `require_country([countries])` - Country checking

---

### META-001: Frontend Event Emission ✅

**Files Created:**
- `sentense-app/src/lib/meta-events.ts` (350 lines)
- `backend/meta_events_api.py` (280 lines)

**Frontend Features:**
- `MetaEvents.emit(event, data)` - Raw event emission
- `MetaEvents.trackPageView()` - Page view tracking
- `MetaEvents.trackFeature(name)` - Feature usage
- `MetaEvents.trackConversion(type)` - Conversion events
- `MetaEvents.trackVoiceAnalysis(data)` - Voice analysis
- `MetaEvents.trackAuthorityProgress(data)` - Authority tracking
- Session management with auto-expiry
- Event queue for offline/retry
- React hooks: `usePageTracking`, `useFeatureTracking`, `useEngagementTracking`

**Backend Features:**
- `POST /api/meta/events` - Single event
- `POST /api/meta/events/batch` - Batch events
- `GET /api/meta/events/stats` - Statistics (admin)
- `GET /api/meta/events/recent` - Recent events (admin)
- Background forwarding to Meta orchestrator
- In-memory event store with statistics

---

## SUCCESS CRITERIA ✅

- [x] Non-CA/GB/AU/NZ IPs blocked at backend
- [x] All protected endpoints have appropriate guards
- [x] Frontend emits events to Meta
- [x] Events received and stored in backend
- [x] Security audit document produced
- [x] Reusable dependencies created

---

## FILES CREATED THIS SPRINT

| File | Lines | Purpose |
|------|-------|---------|
| backend/middleware/country_gate.py | ~450 | GeoIP enforcement |
| backend/middleware/__init__.py | ~30 | Module exports |
| backend/meta_events_api.py | ~280 | Meta events endpoint |
| backend/dependencies.py | ~300 | FastAPI dependencies |
| sentense-app/src/lib/meta-events.ts | ~350 | Frontend event lib |
| docs/SEC003_API_SECURITY_AUDIT.md | ~200 | Audit report |
| docs/PHASE2_WEEK1_PLAN.md | this file | Sprint plan |

**Total new code:** ~1,600 lines

---

## NEXT: PHASE 2 WEEK 2

Ready to proceed with:
- SEC-001: Migrate to httpOnly cookies
- ARCH-003: API contract tests
- META-003: Wire authority score to Meta

