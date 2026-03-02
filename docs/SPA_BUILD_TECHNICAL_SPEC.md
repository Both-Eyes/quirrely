# SENTENSE SPA BUILD — TECHNICAL SPECIFICATION
## Full React Application Roadmap
## Version 1.0.0

**Created:** 2026-02-15  
**Target:** Production-ready SPA with full functionality  
**Prerequisite:** LNCP v5.2.0 (locked)

---

## I. EXECUTIVE SUMMARY

### Objective

Convert the existing static HTML dashboards into a fully functional React Single Page Application (SPA) with:
- Real authentication and session management
- Live data fetching from backend APIs
- Full CRUD operations for all user actions
- Real-time updates where appropriate
- Responsive, accessible, performant UI

### Current State

| Asset | Status | Notes |
|-------|--------|-------|
| Backend APIs | ✅ Built | `curator_api.py`, `authority_api.py`, `dashboard_api.py`, etc. |
| Data Models | ✅ Built | Curator tracker, authority system, milestone system |
| Meta Layer | ✅ Built | Events, lifecycle, HALO safety integration |
| Security | ✅ Built | Gateway, auth, session management |
| HTML/CSS | ✅ Built | Static mockups with full styling |
| Frontend Logic | ❌ Missing | No routing, state, or API wiring |

### Target State

A production-ready React SPA where every button works, every link navigates, every form submits, and every metric displays real data.

---

## II. TECHNICAL ARCHITECTURE

### Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Framework** | React 18 | Industry standard, existing team knowledge |
| **Routing** | React Router v6 | Standard SPA routing |
| **State** | Zustand | Lightweight, simple, scales well |
| **Data Fetching** | TanStack Query (React Query) | Caching, refetching, loading states |
| **Styling** | Tailwind CSS + existing CSS | Keep current design, add utility classes |
| **Forms** | React Hook Form + Zod | Validation, performance |
| **Auth** | Custom (JWT) | Integrate with existing backend |
| **Build** | Vite | Fast builds, modern tooling |
| **Testing** | Vitest + Testing Library | Fast, React-native testing |

### Directory Structure

```
sentense-app/
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── package.json
├── tsconfig.json
│
├── src/
│   ├── main.tsx                    # App entry point
│   ├── App.tsx                     # Root component + providers
│   ├── router.tsx                  # Route definitions
│   │
│   ├── api/                        # API client layer
│   │   ├── client.ts               # Axios/fetch wrapper
│   │   ├── auth.ts                 # Auth endpoints
│   │   ├── user.ts                 # User endpoints
│   │   ├── curator.ts              # Curator endpoints
│   │   ├── authority.ts            # Authority endpoints
│   │   ├── reading.ts              # Reading/paths endpoints
│   │   ├── writing.ts              # Writing endpoints
│   │   ├── analytics.ts            # Analytics endpoints
│   │   └── safety.ts               # HALO safety endpoints
│   │
│   ├── stores/                     # Zustand stores
│   │   ├── authStore.ts            # Auth state
│   │   ├── userStore.ts            # User profile state
│   │   ├── uiStore.ts              # UI state (theme, sidebar, modals)
│   │   └── notificationStore.ts    # Toast/notification state
│   │
│   ├── hooks/                      # Custom hooks
│   │   ├── useAuth.ts              # Auth hook
│   │   ├── useUser.ts              # User data hook
│   │   ├── useCurator.ts           # Curator data hooks
│   │   ├── useAuthority.ts         # Authority data hooks
│   │   ├── useReadingPaths.ts      # Reading path hooks
│   │   ├── useAnalytics.ts         # Analytics hooks
│   │   └── useSafety.ts            # Safety/HALO hooks
│   │
│   ├── components/                 # Shared components
│   │   ├── ui/                     # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Dropdown.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Avatar.tsx
│   │   │   ├── Progress.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/                 # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── AuthLayout.tsx
│   │   │   └── PublicLayout.tsx
│   │   │
│   │   ├── charts/                 # Data visualization
│   │   │   ├── RadarChart.tsx      # Voice profile chart
│   │   │   ├── LineChart.tsx       # Trends
│   │   │   ├── BarChart.tsx        # Comparisons
│   │   │   └── MetricCard.tsx      # Single metric display
│   │   │
│   │   └── features/               # Feature-specific components
│   │       ├── VoiceProfile.tsx
│   │       ├── ReadingPath.tsx
│   │       ├── ActivityFeed.tsx
│   │       ├── AuthorityProgress.tsx
│   │       ├── WritingEditor.tsx
│   │       └── SafetyStatus.tsx
│   │
│   ├── pages/                      # Page components (routes)
│   │   ├── public/
│   │   │   ├── Home.tsx
│   │   │   ├── About.tsx
│   │   │   ├── Pricing.tsx
│   │   │   └── Blog.tsx
│   │   │
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── ForgotPassword.tsx
│   │   │   └── ResetPassword.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── Overview.tsx        # Main dashboard
│   │   │   ├── VoiceAnalysis.tsx   # Voice profile detail
│   │   │   └── Settings.tsx        # User settings
│   │   │
│   │   ├── reader/
│   │   │   ├── Discover.tsx        # Browse content
│   │   │   ├── Bookmarks.tsx       # Saved items
│   │   │   ├── ReadingHistory.tsx  # Read history
│   │   │   └── Streak.tsx          # Reading streak
│   │   │
│   │   ├── writer/
│   │   │   ├── MyWriting.tsx       # Published posts
│   │   │   ├── Drafts.tsx          # Draft posts
│   │   │   ├── Editor.tsx          # Write/edit post
│   │   │   └── Analytics.tsx       # Writing analytics
│   │   │
│   │   ├── curator/
│   │   │   ├── MyPaths.tsx         # Curated paths
│   │   │   ├── CreatePath.tsx      # Create new path
│   │   │   ├── EditPath.tsx        # Edit path
│   │   │   └── PathAnalytics.tsx   # Path performance
│   │   │
│   │   └── authority/
│   │       ├── AuthorityHub.tsx    # Authority dashboard
│   │       ├── Leaderboard.tsx     # Rankings
│   │       └── Impact.tsx          # Impact metrics
│   │
│   ├── utils/                      # Utility functions
│   │   ├── formatters.ts           # Date, number formatting
│   │   ├── validators.ts           # Form validation
│   │   ├── constants.ts            # App constants
│   │   └── helpers.ts              # Misc helpers
│   │
│   ├── types/                      # TypeScript types
│   │   ├── user.ts
│   │   ├── auth.ts
│   │   ├── curator.ts
│   │   ├── authority.ts
│   │   ├── reading.ts
│   │   ├── writing.ts
│   │   ├── analytics.ts
│   │   └── api.ts
│   │
│   └── styles/
│       ├── globals.css             # Global styles
│       └── themes.css              # Theme variables
│
└── public/
    ├── favicon.svg
    └── assets/
        └── logo/
```

---

## III. FEATURE BREAKDOWN

### Phase 1: Foundation (Day 1)

**Objective:** Working app shell with auth

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Vite + React + TypeScript setup | P0 | 30min | Working dev server |
| Tailwind CSS configuration | P0 | 15min | Styling ready |
| React Router setup | P0 | 30min | Route structure |
| API client with interceptors | P0 | 45min | `api/client.ts` |
| Auth store (Zustand) | P0 | 30min | `stores/authStore.ts` |
| Auth API integration | P0 | 45min | Login/logout working |
| Protected route wrapper | P0 | 30min | Route guards |
| Base layout components | P0 | 1hr | Header, Sidebar, layouts |
| Login page | P0 | 45min | Functional login |
| Signup page | P1 | 45min | Functional signup |

**Deliverable:** User can sign up, log in, see protected dashboard shell

---

### Phase 2: Dashboard Core (Day 1-2)

**Objective:** Main dashboard with real data

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| User API integration | P0 | 30min | `api/user.ts` |
| User store | P0 | 30min | `stores/userStore.ts` |
| useUser hook with React Query | P0 | 30min | Data fetching |
| Dashboard Overview page | P0 | 2hr | Main dashboard |
| Metric cards component | P0 | 45min | Reusable metrics |
| Voice profile component | P0 | 1hr | Radar chart + tokens |
| Activity feed component | P1 | 45min | Recent activity |
| Settings page | P1 | 1.5hr | User settings |
| Theme toggle | P1 | 30min | Dark/light mode |

**Deliverable:** Fully functional main dashboard with real user data

---

### Phase 3: Reader Features (Day 2)

**Objective:** Complete reader functionality

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Reading API integration | P0 | 45min | `api/reading.ts` |
| useReadingPaths hook | P0 | 30min | Path data |
| Discover page | P0 | 1.5hr | Browse content |
| Bookmarks page | P0 | 1hr | Saved items |
| Reading streak component | P1 | 45min | Streak display |
| Reading history page | P1 | 1hr | History list |
| Bookmark actions | P0 | 30min | Add/remove bookmark |
| Read tracking | P1 | 45min | Mark as read |

**Deliverable:** Reader can browse, bookmark, track reads

---

### Phase 4: Writer Features (Day 2-3)

**Objective:** Complete writer functionality

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Writing API integration | P0 | 45min | `api/writing.ts` |
| My Writing page | P0 | 1hr | Published posts |
| Drafts page | P0 | 45min | Draft management |
| Writing editor | P0 | 3hr | Rich text editor |
| Publish flow | P0 | 1hr | Draft → Published |
| Writing analytics page | P1 | 1.5hr | Stats and charts |
| Delete/archive actions | P1 | 30min | Post management |

**Deliverable:** Writer can create, edit, publish, manage posts

---

### Phase 5: Curator Features (Day 3)

**Objective:** Complete curator functionality

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Curator API integration | P0 | 45min | `api/curator.ts` |
| useCurator hooks | P0 | 30min | Curator data |
| My Paths page | P0 | 1.5hr | Path list |
| Create Path page | P0 | 2hr | Path builder |
| Edit Path page | P0 | 1hr | Path editing |
| Path analytics | P1 | 1hr | Path performance |
| Reorder path items | P1 | 45min | Drag and drop |
| Path publishing | P0 | 30min | Draft → Live |

**Deliverable:** Curator can create, manage, analyze paths

---

### Phase 6: Authority Features (Day 3)

**Objective:** Complete authority functionality

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Authority API integration | P0 | 45min | `api/authority.ts` |
| useAuthority hooks | P0 | 30min | Authority data |
| Authority Hub page | P0 | 2hr | Authority dashboard |
| Leaderboard page | P1 | 1.5hr | Rankings |
| Impact page | P1 | 1hr | Impact metrics |
| Authority progress component | P0 | 45min | Progress display |
| Badge showcase | P1 | 30min | Earned badges |

**Deliverable:** Authority features fully functional

---

### Phase 7: Polish & Integration (Day 3+)

**Objective:** Production-ready quality

| Task | Priority | Effort | Output |
|------|----------|--------|--------|
| Error boundaries | P0 | 45min | Graceful errors |
| Loading skeletons | P0 | 1hr | Better UX |
| Toast notifications | P0 | 45min | User feedback |
| Form validation | P0 | 1hr | All forms |
| Responsive testing | P0 | 1hr | Mobile/tablet |
| Accessibility audit | P1 | 1hr | A11y fixes |
| Performance audit | P1 | 45min | Optimize |
| Safety integration | P0 | 45min | HALO checks |
| E2E test suite | P2 | 2hr | Critical paths |

**Deliverable:** Production-ready application

---

## IV. API CONTRACT

### Endpoints Required

```typescript
// Auth
POST   /api/auth/login           { email, password } → { token, user }
POST   /api/auth/signup          { email, password, name } → { token, user }
POST   /api/auth/logout          {} → { success }
POST   /api/auth/refresh         {} → { token }
POST   /api/auth/forgot-password { email } → { success }
POST   /api/auth/reset-password  { token, password } → { success }

// User
GET    /api/user/me              → { user }
PUT    /api/user/me              { updates } → { user }
GET    /api/user/profile         → { profile, voice, stats }
PUT    /api/user/settings        { settings } → { settings }
GET    /api/user/activity        → { activities[] }

// Reading
GET    /api/reading/discover     ?page&limit&filter → { posts[], total }
GET    /api/reading/bookmarks    → { bookmarks[] }
POST   /api/reading/bookmarks    { post_id } → { bookmark }
DELETE /api/reading/bookmarks/:id → { success }
GET    /api/reading/history      → { reads[] }
POST   /api/reading/track        { post_id, duration, scroll } → { read }
GET    /api/reading/streak       → { streak }

// Writing
GET    /api/writing/posts        → { posts[] }
GET    /api/writing/posts/:id    → { post }
POST   /api/writing/posts        { title, content, status } → { post }
PUT    /api/writing/posts/:id    { updates } → { post }
DELETE /api/writing/posts/:id    → { success }
GET    /api/writing/drafts       → { drafts[] }
POST   /api/writing/publish/:id  → { post }
GET    /api/writing/analytics    → { analytics }

// Curator
GET    /api/curator/paths        → { paths[] }
GET    /api/curator/paths/:id    → { path }
POST   /api/curator/paths        { title, description, items } → { path }
PUT    /api/curator/paths/:id    { updates } → { path }
DELETE /api/curator/paths/:id    → { success }
POST   /api/curator/paths/:id/publish → { path }
GET    /api/curator/progress     → { progress }
GET    /api/curator/analytics    → { analytics }

// Authority
GET    /api/authority/status     → { authority }
GET    /api/authority/progress   → { progress, milestones }
GET    /api/authority/leaderboard ?limit → { rankings[] }
GET    /api/authority/impact     → { impact }
GET    /api/authority/badges     → { badges[] }

// Safety
POST   /api/safety/check         { content } → { result }
GET    /api/safety/status        → { safety_score, trust_level }
POST   /api/safety/appeal        { violation_id, reason } → { appeal }

// Analytics (for charts)
GET    /api/analytics/overview   → { metrics }
GET    /api/analytics/trends     ?period → { data[] }
GET    /api/analytics/voice      → { voice_profile }
```

---

## V. STATE MANAGEMENT

### Auth Store

```typescript
interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  setUser: (user: User) => void;
}
```

### User Store

```typescript
interface UserState {
  profile: UserProfile | null;
  settings: UserSettings | null;
  voiceProfile: VoiceProfile | null;
  stats: UserStats | null;
  
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  updateSettings: (data: Partial<UserSettings>) => Promise<void>;
}
```

### UI Store

```typescript
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeModal: string | null;
  
  toggleTheme: () => void;
  toggleSidebar: () => void;
  openModal: (id: string) => void;
  closeModal: () => void;
}
```

---

## VI. COMPONENT SPECIFICATIONS

### Key Components

#### `<VoiceProfile />`

```typescript
interface VoiceProfileProps {
  profile: {
    primary: string;
    secondary: string;
    openness: string;
    tokens: Array<{ name: string; weight: number }>;
    dimensions: Record<string, number>;
    confidence: number;
  };
  size?: 'sm' | 'md' | 'lg';
  showTokens?: boolean;
  showChart?: boolean;
}
```

#### `<ReadingPath />`

```typescript
interface ReadingPathProps {
  path: {
    id: string;
    title: string;
    description: string;
    items: PathItem[];
    followers: number;
    completions: number;
  };
  variant?: 'card' | 'list' | 'detail';
  onFollow?: () => void;
  onEdit?: () => void;
}
```

#### `<MetricCard />`

```typescript
interface MetricCardProps {
  label: string;
  value: number | string;
  unit?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    period: string;
  };
  variant?: 'default' | 'gold' | 'success' | 'warning';
}
```

#### `<ActivityFeed />`

```typescript
interface ActivityFeedProps {
  activities: Array<{
    id: string;
    type: 'read' | 'follow' | 'badge' | 'path' | 'publish';
    content: string;
    timestamp: string;
    metadata?: Record<string, any>;
  }>;
  limit?: number;
  showLoadMore?: boolean;
}
```

---

## VII. ROUTING STRUCTURE

```typescript
const routes = [
  // Public
  { path: '/', element: <Home /> },
  { path: '/about', element: <About /> },
  { path: '/pricing', element: <Pricing /> },
  { path: '/blog', element: <Blog /> },
  
  // Auth
  { path: '/login', element: <Login /> },
  { path: '/signup', element: <Signup /> },
  { path: '/forgot-password', element: <ForgotPassword /> },
  { path: '/reset-password', element: <ResetPassword /> },
  
  // Protected - Dashboard
  { 
    path: '/dashboard',
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { index: true, element: <Overview /> },
      { path: 'voice', element: <VoiceAnalysis /> },
      { path: 'settings', element: <Settings /> },
    ]
  },
  
  // Protected - Reader
  {
    path: '/reader',
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: 'discover', element: <Discover /> },
      { path: 'bookmarks', element: <Bookmarks /> },
      { path: 'history', element: <ReadingHistory /> },
      { path: 'streak', element: <Streak /> },
    ]
  },
  
  // Protected - Writer
  {
    path: '/writer',
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: 'posts', element: <MyWriting /> },
      { path: 'drafts', element: <Drafts /> },
      { path: 'editor', element: <Editor /> },
      { path: 'editor/:id', element: <Editor /> },
      { path: 'analytics', element: <WritingAnalytics /> },
    ]
  },
  
  // Protected - Curator
  {
    path: '/curator',
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: 'paths', element: <MyPaths /> },
      { path: 'paths/new', element: <CreatePath /> },
      { path: 'paths/:id/edit', element: <EditPath /> },
      { path: 'analytics', element: <PathAnalytics /> },
    ]
  },
  
  // Protected - Authority
  {
    path: '/authority',
    element: <ProtectedRoute><DashboardLayout /></ProtectedRoute>,
    children: [
      { path: 'hub', element: <AuthorityHub /> },
      { path: 'leaderboard', element: <Leaderboard /> },
      { path: 'impact', element: <Impact /> },
    ]
  },
];
```

---

## VIII. TESTING STRATEGY

### Unit Tests

- All utility functions
- Store actions
- Custom hooks
- Form validation

### Component Tests

- All UI components render correctly
- User interactions work
- Props variations

### Integration Tests

- Auth flow (signup → login → logout)
- CRUD operations per feature
- Navigation flows

### E2E Tests (Critical Paths)

1. New user signup → onboarding → first analysis
2. Login → view dashboard → update settings
3. Create reading path → publish → view analytics
4. Write post → save draft → publish
5. Authority progress tracking

---

## IX. PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Time to Interactive | < 3.0s |
| Cumulative Layout Shift | < 0.1 |
| Bundle Size (gzipped) | < 150KB |

### Optimization Strategies

- Code splitting by route
- Lazy loading non-critical components
- Image optimization
- React Query caching
- Memoization where appropriate

---

## X. IMPLEMENTATION SCHEDULE

### Session 1: Foundation
- [ ] Project setup (Vite, React, TypeScript, Tailwind)
- [ ] API client with auth interceptors
- [ ] Auth store and hooks
- [ ] Login/Signup pages (functional)
- [ ] Protected route wrapper
- [ ] Base layout (Header, Sidebar)

### Session 2: Dashboard Core
- [ ] User API and store
- [ ] Dashboard Overview page
- [ ] Voice Profile component with chart
- [ ] Metric cards
- [ ] Activity feed
- [ ] Settings page
- [ ] Theme toggle

### Session 3: Reader + Writer
- [ ] Reading API integration
- [ ] Discover, Bookmarks, History pages
- [ ] Reading streak component
- [ ] Writing API integration
- [ ] My Writing, Drafts pages
- [ ] Writing editor (basic)
- [ ] Publish flow

### Session 4: Curator + Authority
- [ ] Curator API integration
- [ ] Path management pages
- [ ] Path builder/editor
- [ ] Authority API integration
- [ ] Authority Hub, Leaderboard pages
- [ ] Impact metrics

### Session 5: Polish
- [ ] Error boundaries
- [ ] Loading states/skeletons
- [ ] Toast notifications
- [ ] Form validation
- [ ] Responsive fixes
- [ ] Safety integration
- [ ] Final testing

---

## XI. DEPENDENCIES

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.294.0",
    "clsx": "^2.0.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0"
  }
}
```

---

## XII. SUCCESS CRITERIA

### Functional

- [ ] User can complete full signup → dashboard flow
- [ ] All navigation links work
- [ ] All forms submit successfully
- [ ] All CRUD operations functional
- [ ] Real data displayed everywhere
- [ ] Theme toggle works
- [ ] Responsive on mobile/tablet

### Quality

- [ ] No console errors in production
- [ ] Loading states on all data fetches
- [ ] Error messages for failures
- [ ] Form validation feedback
- [ ] Accessible (keyboard nav, screen reader)

### Performance

- [ ] Lighthouse score > 90
- [ ] Bundle size < 150KB gzipped
- [ ] No layout shifts

---

## XIII. RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend API gaps | High | Audit endpoints before starting; mock missing |
| Complex editor | Medium | Use existing library (TipTap/Slate); iterate |
| Auth edge cases | Medium | Handle token expiry, refresh, logout gracefully |
| Scope creep | High | Stick to spec; defer nice-to-haves |
| State complexity | Medium | Keep stores minimal; use React Query for server state |

---

## XIV. NEXT STEPS

1. **Review this spec** — Confirm scope and priorities
2. **Audit backend APIs** — Verify all endpoints exist or identify gaps
3. **Session 1** — Build foundation (auth + layouts)
4. **Iterate** — Build features phase by phase
5. **Test** — Each phase before moving on
6. **Deploy** — When all success criteria met

---

**Ready to build.** 🚀

*This spec will be the source of truth for the SPA build. Reference it at the start of each session.*
