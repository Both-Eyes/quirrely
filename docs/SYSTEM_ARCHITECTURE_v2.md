# 🐿️ QUIRRELY SYSTEM ARCHITECTURE
## Complete Technical Reference
### Version 2.0.0 | February 2026

---

## 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUIRRELY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │   React     │     │   FastAPI   │     │  PostgreSQL │     │  Stripe   │ │
│  │   SPA       │────▶│   Backend   │────▶│  (Supabase) │     │  Payments │ │
│  │  (Vite)     │     │   (Python)  │     │             │     │           │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│        │                   │                   │                   │        │
│        │                   │                   │                   │        │
│        ▼                   ▼                   ▼                   ▼        │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │  Zustand    │     │  Feature    │     │   Auth      │     │  Webhook  │ │
│  │  State      │     │  Gate       │     │  (Supabase) │     │  Handler  │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. USER TIER & ADDON SYSTEM

### 2.1 Tier Hierarchy

```
Level 3:  authority_writer ◄────────────────────► authority_curator
              │                                         │
Level 2:  featured_writer ◄─────────────────────► featured_curator
              │                                         │
              │              voice_style                │
              │            ┌───────────┐               │
Level 1:      pro ◄────────┤  (addon)  ├────────► curator
              │            └───────────┘               │
              │                                         │
Level 0:                        free
```

### 2.2 Data Model

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT,
  preferred_currency TEXT CHECK (currency IN ('cad', 'gbp', 'aud', 'nzd')),
  status TEXT DEFAULT 'active'
);

-- Subscriptions table
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  tier TEXT CHECK (tier IN (
    'pro', 'curator',
    'featured_writer', 'featured_curator',
    'authority_writer', 'authority_curator'
  )),
  status TEXT,
  currency TEXT,
  amount_cents INTEGER
);

-- User addons table
CREATE TABLE user_addons (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  addon TEXT CHECK (addon IN ('voice_style')),
  status TEXT DEFAULT 'active',
  source TEXT -- 'purchase', 'bundle', 'promotion'
);
```

### 2.3 TypeScript Types

```typescript
// Frontend types
export type UserTier = 
  | 'free'
  | 'pro'
  | 'curator'
  | 'featured_writer'
  | 'featured_curator'
  | 'authority_writer'
  | 'authority_curator';

export type UserAddon = 'voice_style';

export interface User {
  id: string;
  email: string;
  name: string;
  tier: UserTier;
  addons: UserAddon[];
  country: string;
  // ...
}
```

### 2.4 Python Enums

```python
# Backend enums
class Tier(str, Enum):
    FREE = "free"
    PRO = "pro"
    CURATOR = "curator"
    FEATURED_WRITER = "featured_writer"
    FEATURED_CURATOR = "featured_curator"
    AUTHORITY_WRITER = "authority_writer"
    AUTHORITY_CURATOR = "authority_curator"

class Addon(str, Enum):
    VOICE_STYLE = "voice_style"
```

---

## 3. PERMISSION SYSTEM

### 3.1 Permission Check Logic

```typescript
// Frontend (Sidebar.tsx)
const hasAccess = (item: NavItem) => {
  const hasTier = !item.requiredTier || item.requiredTier.includes(userTier);
  const hasAddon = !item.requiredAddon || userAddons.includes(item.requiredAddon);
  
  if (item.tierOrAddon) {
    // User needs tier OR addon
    return item.requiredTier?.includes(userTier) || 
           (item.requiredAddon && userAddons.includes(item.requiredAddon));
  }
  
  // User needs both (if specified)
  return hasTier && hasAddon;
};
```

```python
# Backend (feature_gate.py)
def check_access(self, tier: Tier, addons: List[str] = None) -> bool:
    tier_access = {
        Tier.FREE: self.tier_free,
        Tier.PRO: self.tier_pro,
        # ... etc
    }
    has_tier = tier_access.get(tier, False)
    has_addon = Addon.VOICE_STYLE.value in (addons or [])
    
    if self.tier_or_addon:
        return has_tier or has_addon
    return has_tier and (not self.addon_voice_style or has_addon)
```

### 3.2 Feature Access Matrix

| Feature | Tiers | Addon | Mode |
|---------|-------|-------|------|
| Basic Analysis | All | — | — |
| Analytics | pro, curator+ | — | tier only |
| Voice Profile | — | voice_style | addon only |
| Create Paths | curator+ | voice_style | tier OR addon |
| Authority Hub | featured+ | voice_style | tier OR addon |
| Leaderboard | featured+ | voice_style | tier OR addon |

---

## 4. API REFERENCE

### 4.1 Authentication

```
POST /api/v2/auth/login
POST /api/v2/auth/signup
POST /api/v2/auth/logout
POST /api/v2/auth/refresh
POST /api/v2/auth/forgot-password
POST /api/v2/auth/reset-password
```

### 4.2 User

```
GET  /api/v2/user/me          → User profile with tier + addons
PUT  /api/v2/user/me          → Update profile
GET  /api/v2/user/settings    → User settings
PUT  /api/v2/user/settings    → Update settings
GET  /api/v2/user/stats       → User statistics
```

### 4.3 Dashboard

```
GET /api/v2/dashboard
Response:
{
  "user_tier": "pro",
  "user_addons": ["voice_style"],
  "tier_level": 1,
  "track": "writer",
  "has_voice_style": true,
  "has_writer_features": true,
  "has_reader_features": true,
  "writer_data": {...},
  "reader_data": {...}
}
```

### 4.4 Reading

```
GET  /api/v2/posts/discover   → Paginated posts
GET  /api/v2/posts/:id        → Single post
GET  /api/v2/bookmarks        → User's bookmarks
POST /api/v2/bookmarks        → Add bookmark
DELETE /api/v2/bookmarks/:id  → Remove bookmark
GET  /api/v2/streak           → Reading streak
```

### 4.5 Writing

```
GET  /api/v2/writing/posts    → User's posts
POST /api/v2/writing/posts    → Create post
PUT  /api/v2/writing/posts/:id → Update post
DELETE /api/v2/writing/posts/:id → Delete post
POST /api/v2/writing/posts/:id/publish → Publish
GET  /api/v2/writing/drafts   → User's drafts
```

### 4.6 Curator (requires curator+ OR voice_style)

```
GET  /api/v2/curator/paths    → User's paths
POST /api/v2/curator/paths    → Create path
PUT  /api/v2/curator/paths/:id → Update path
DELETE /api/v2/curator/paths/:id → Delete path
POST /api/v2/curator/paths/:id/publish → Publish
GET  /api/v2/curator/paths/:id/analytics → Path stats
```

### 4.7 Authority (requires featured+ OR voice_style)

```
GET /api/v2/authority/status      → Authority status
GET /api/v2/authority/progress    → Progress to next level
GET /api/v2/authority/leaderboard → Global rankings
GET /api/v2/authority/impact      → Impact statistics
GET /api/v2/authority/badges      → Earned badges
```

### 4.8 Voice (requires voice_style addon)

```
GET  /api/v2/voice/profile    → Full voice profile
POST /api/v2/voice/analyze    → Analyze text
GET  /api/v2/voice/history    → Voice evolution
GET  /api/v2/voice/insights   → AI insights
```

---

## 5. FRONTEND STRUCTURE

### 5.1 Directory Layout

```
sentense-app/
├── src/
│   ├── api/                 # API client & endpoints
│   │   ├── client.ts        # Axios instance
│   │   ├── auth.ts          # Auth endpoints
│   │   ├── user.ts          # User endpoints
│   │   ├── reading.ts       # Reading endpoints
│   │   ├── writing.ts       # Writing endpoints
│   │   ├── curator.ts       # Curator endpoints
│   │   ├── authority.ts     # Authority endpoints
│   │   └── safety.ts        # Safety endpoints
│   │
│   ├── stores/              # Zustand stores
│   │   ├── authStore.ts     # Auth state
│   │   ├── uiStore.ts       # UI preferences
│   │   └── notificationStore.ts
│   │
│   ├── hooks/               # React Query hooks
│   │   ├── useAuth.ts
│   │   ├── useUser.ts
│   │   ├── useReading.ts
│   │   ├── useWriting.ts
│   │   ├── useCurator.ts
│   │   └── useAuthority.ts
│   │
│   ├── components/
│   │   ├── ui/              # Base components
│   │   ├── layout/          # Layout components
│   │   ├── charts/          # Chart components
│   │   └── features/        # Feature components
│   │
│   ├── pages/
│   │   ├── auth/            # Login, Signup
│   │   ├── dashboard/       # Overview, Settings, Voice
│   │   ├── reader/          # Discover, Bookmarks, Streak
│   │   ├── writer/          # MyWriting, Drafts, Editor
│   │   ├── curator/         # MyPaths, PathEditor
│   │   ├── authority/       # Hub, Leaderboard, Impact
│   │   └── public/          # NotFound
│   │
│   ├── types/               # TypeScript types
│   ├── styles/              # Global CSS
│   ├── router.tsx           # Route definitions
│   ├── App.tsx              # Root component
│   └── main.tsx             # Entry point
│
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### 5.2 Route Definitions

```typescript
// router.tsx
const routes = [
  // Public
  { path: '/login', element: <Login /> },
  { path: '/signup', element: <Signup /> },
  
  // Protected (all authenticated users)
  { path: '/dashboard', element: <Overview /> },
  { path: '/dashboard/settings', element: <Settings /> },
  { path: '/dashboard/voice', element: <VoiceProfilePage /> }, // voice_style
  
  // Reader
  { path: '/reader/discover', element: <Discover /> },
  { path: '/reader/bookmarks', element: <Bookmarks /> },
  { path: '/reader/streak', element: <Streak /> },
  
  // Writer
  { path: '/writer/posts', element: <MyWriting /> },
  { path: '/writer/drafts', element: <Drafts /> },
  { path: '/writer/editor', element: <Editor /> },
  { path: '/writer/editor/:id', element: <Editor /> },
  { path: '/writer/analytics', element: <Analytics /> }, // pro+
  
  // Curator (curator+ OR voice_style)
  { path: '/curator/paths', element: <MyPaths /> },
  { path: '/curator/paths/new', element: <PathEditor /> },
  { path: '/curator/paths/:id/edit', element: <PathEditor /> },
  
  // Authority (featured+ OR voice_style)
  { path: '/authority/hub', element: <AuthorityHub /> },
  { path: '/authority/leaderboard', element: <Leaderboard /> },
  { path: '/authority/impact', element: <ImpactStats /> },
  
  // Catch-all
  { path: '*', element: <NotFound /> },
];
```

---

## 6. BACKEND STRUCTURE

### 6.1 Directory Layout

```
backend/
├── api_v2.py              # Main FastAPI app
├── auth_api.py            # Authentication routes
├── dashboard_api.py       # Dashboard routes
├── curator_api.py         # Curator routes
├── authority_api.py       # Authority routes
├── analytics_api.py       # Analytics routes
│
├── feature_gate.py        # Permission system
├── curator_tracker.py     # Curator milestones
│
├── schema_auth.sql        # Auth tables
├── schema_payments.sql    # Payment tables
├── schema_subscriptions_v2.sql  # Tier & addon tables
├── schema_curator.sql     # Curator tables
├── schema_authority.sql   # Authority tables
│
├── email_service.py       # Email handling
├── analytics_service.py   # Analytics processing
│
└── seed_qa_test_users.sql # Test user data
```

### 6.2 Feature Gate Usage

```python
from feature_gate import FeatureGate, Tier, Addon

gate = FeatureGate()

# Check feature access
@app.get("/api/v2/curator/paths")
async def get_paths(user_id: str = Depends(get_user_id)):
    user_tier = gate.get_user_tier(user_id)
    
    if not gate.can_access("create_paths", user_id):
        raise HTTPException(403, "Curator features require curator tier or voice_style addon")
    
    return await get_user_paths(user_id)
```

---

## 7. DATABASE SCHEMA

### 7.1 Core Tables

```
users
├── id (UUID, PK)
├── email (TEXT, UNIQUE)
├── display_name (TEXT)
├── preferred_currency (TEXT)
├── status (TEXT)
└── created_at (TIMESTAMPTZ)

subscriptions
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── tier (TEXT)
├── status (TEXT)
├── currency (TEXT)
├── amount_cents (INTEGER)
└── current_period_end (TIMESTAMPTZ)

user_addons
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── addon (TEXT)
├── status (TEXT)
├── source (TEXT)
└── expires_at (TIMESTAMPTZ, nullable)
```

### 7.2 Helper Functions

```sql
-- Get user's effective tier
SELECT get_user_tier('user-uuid');

-- Get user's active addons
SELECT get_user_addons('user-uuid');

-- Check feature access
SELECT check_feature_access(
  'user-uuid',
  ARRAY['featured_writer', 'featured_curator'],
  'voice_style',
  TRUE  -- tier_or_addon
);

-- Grant addon
SELECT grant_addon('user-uuid', 'voice_style', 'purchase');
```

---

## 8. COUNTRY CONFIGURATION

### 8.1 Supported Countries

| Code | Country | Currency | Flag |
|------|---------|----------|------|
| CA | Canada | CAD | 🇨🇦 |
| GB | United Kingdom | GBP | 🇬🇧 |
| AU | Australia | AUD | 🇦🇺 |
| NZ | New Zealand | NZD | 🇳🇿 |

**⚠️ USA/USD is explicitly NOT supported.**

### 8.2 Pricing (Monthly)

| Tier | CAD | GBP | AUD | NZD |
|------|-----|-----|-----|-----|
| Pro / Curator | $14.99 | £11.99 | $19.99 | $21.99 |
| Featured | $24.99 | £19.99 | $34.99 | $37.99 |
| Authority | $49.99 | £39.99 | $69.99 | $74.99 |
| voice_style (addon) | $9.99 | £7.99 | $14.99 | $15.99 |

---

## 9. DEPLOYMENT

### 9.1 Environment Variables

```bash
# Frontend (.env)
VITE_API_URL=/api
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx

# Backend (.env)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### 9.2 Commands

```bash
# Frontend
cd sentense-app
npm install
npm run dev      # Development
npm run build    # Production build
npm run preview  # Preview build

# Backend
cd backend
pip install -r requirements.txt
uvicorn api_v2:app --reload  # Development
uvicorn api_v2:app --workers 4  # Production
```

---

## 10. TESTING

### 10.1 Test User Accounts

Run `seed_qa_test_users.sql` to create 56 test accounts:
- 14 tier+addon combinations
- 4 countries
- Password: `QuirrelyQA2026!`

### 10.2 Stripe Test Cards

| Country | Card Number |
|---------|-------------|
| Canada | 4000001240000000 |
| UK | 4000008260000000 |
| Australia | 4000000360000006 |
| New Zealand | 4000005540000008 |

---

**Document Version:** 2.0.0
**Last Updated:** February 15, 2026
