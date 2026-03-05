# PHASE 2 WEEK 2: IMPLEMENTATION PLAN
## Public Launch Preparation - Auth Security & API Contracts

---

**Sprint:** Phase 2, Week 2  
**Start:** February 15, 2026  
**Status:** ✅ COMPLETE  
**Focus:** httpOnly cookies, API contracts, Meta authority wiring  

---

## DELIVERABLES

| ID | Task | Est. Hours | Priority | Status |
|----|------|------------|----------|--------|
| SEC-001 | Migrate to httpOnly cookies | 4h | CRITICAL | ✅ DONE |
| ARCH-003 | API contract tests | 8h | HIGH | ✅ DONE |
| META-003 | Wire authority score to Meta | 2h | HIGH | ✅ DONE |

**Total:** 14 hours

---

## TASK 1: SEC-001 - httpOnly Cookie Authentication

### Current State
- JWT tokens stored in localStorage (via Zustand)
- Vulnerable to XSS attacks
- Token sent in Authorization header

### Target State
- JWT stored in httpOnly cookie (not accessible to JS)
- Cookie set by backend on login
- Cookie automatically sent with requests
- Refresh token flow for session extension

### Files to Modify/Create

**Backend:**
- `backend/auth_api.py` - Add cookie setting on login/signup
- `backend/auth_middleware.py` - Create cookie validation middleware
- `backend/dependencies.py` - Update get_current_user for cookies

**Frontend:**
- `sentense-app/src/api/client.ts` - Add credentials: 'include'
- `sentense-app/src/api/auth.ts` - Remove token storage
- `sentense-app/src/stores/authStore.ts` - Remove token handling

### Implementation Details

```python
# Backend: Set httpOnly cookie on login
response.set_cookie(
    key="quirrely_auth",
    value=jwt_token,
    httponly=True,
    secure=True,  # HTTPS only in production
    samesite="lax",
    max_age=3600 * 24,  # 24 hours
    path="/",
)
```

```typescript
// Frontend: Include cookies in requests
const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Include cookies
});
```

---

## TASK 2: ARCH-003 - API Contract Tests

### Purpose
Ensure frontend mock data shapes match actual backend responses.

### Test Categories
1. User API contracts
2. Dashboard API contracts
3. Authority API contracts
4. Curator API contracts
5. Writer API contracts

### Files to Create
- `sentense-app/src/__tests__/contracts/user.contract.test.ts`
- `sentense-app/src/__tests__/contracts/dashboard.contract.test.ts`
- `sentense-app/src/__tests__/contracts/authority.contract.test.ts`

### Test Pattern
```typescript
describe('User API Contract', () => {
  it('GET /user matches expected shape', () => {
    const response = mockUserResponse;
    
    expect(response).toMatchObject({
      id: expect.any(String),
      email: expect.any(String),
      name: expect.any(String),
      tier: expect.stringMatching(/^(free|pro|curator|...)$/),
      addons: expect.any(Array),
      country: expect.stringMatching(/^(CA|GB|AU|NZ)$/),
    });
  });
});
```

---

## TASK 3: META-003 - Wire Authority Score to Meta

### Current State
- Frontend uses mock `score: 94.7`
- Backend has Meta health calculator
- No connection between them

### Target State
- Frontend calls real API endpoint
- Backend queries Meta for authority score
- Real-time score updates

### Files to Modify

**Backend:**
- `backend/authority_api.py` - Add Meta integration

**Frontend:**
- `sentense-app/src/hooks/useAuthority.ts` - Use real API

### Implementation
```python
# Backend
from lncp.meta import get_health_calculator

@router.get("/status")
async def get_authority_status(user: CurrentUser = Depends(get_current_user)):
    calculator = get_health_calculator()
    health = calculator.calculate_user_health(user.id)
    
    return {
        "score": health.authority_score,
        "rank": health.rank,
        "percentile": health.percentile,
        "level": user.tier.value,
    }
```

---

## EXECUTION ORDER

1. SEC-001: httpOnly cookies (highest security impact)
2. META-003: Authority score wiring (smaller, enables testing)
3. ARCH-003: API contract tests (validates everything works)

---

## SUCCESS CRITERIA

- [ ] Login sets httpOnly cookie instead of returning token
- [ ] Frontend sends cookies with all API requests
- [ ] Token not accessible via JavaScript
- [ ] Authority score fetched from Meta
- [ ] Contract tests pass for core API shapes
- [ ] No breaking changes to existing functionality

