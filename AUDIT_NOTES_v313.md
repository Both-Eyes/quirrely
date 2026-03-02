# Quirrely v3.1.3 — Audit Clarification Notes

## Audit False Positives

### F10: 'quick-analyze' not in index.html
**Status:** NOT A BUG — Architecture difference from audit expectation.

The audit checked for the string `quick-analyze` (the API endpoint name).
The frontend `index.html` uses a **client-side LNCP classifier** embedded in the page:
- `analyzeWriting()` — calls the inline LNCP engine (offline-first)
- `runAnalysis()` — UI trigger function

Free-tier users run analysis entirely client-side via the embedded classifier.
The `/api/quick-analyze` endpoint is called by the **Chrome Extension** and for authenticated 
server-side analysis (Pro tier). This is by design.

**Evidence:** `frontend/index.html` contains `analyzeWriting` (6 occurrences), `runAnalysis` (1 occurrence).

---

### F11: JWT not directly in auth_api.py
**Status:** NOT A BUG — Correct separation of concerns.

The audit checked `auth_api.py` for the string `jwt`. JWT logic lives in `auth_middleware.py`
(correct layer separation). `auth_api.py` imports from `auth_config` which wraps `python-jose`.

**Evidence:**
- `backend/auth_middleware.py` line 24: `import jwt`
- `backend/auth_middleware.py` lines 115, 138, 152: `jwt.encode()` / `jwt.decode()`
- `backend/auth_api.py` line 24: `from auth_config import (...)` which exposes `decode_token`

JWT is fully operational. The auth system uses `secrets.token_urlsafe()` for session tokens
plus JWT for stateless verification — a hybrid approach supporting both cookie and bearer auth.

---

### F4: PARALLEL profile missing
**Status:** NOT A BUG — Profile was renamed.

Early architecture docs (pre-v3.1.0) referred to a `PARALLEL` profile. The implemented and 
canonical 10th profile is `ANALYTICAL`. See `backend/PROFILES_MANIFEST.md` for full documentation.

All 10 profiles are present: ASSERTIVE · HEDGED · CONVERSATIONAL · FORMAL · DENSE · MINIMAL 
· POETIC · ANALYTICAL · INTERROGATIVE · LONGFORM
