# Sentense SPA

A React-based Single Page Application for the Sentense writing voice analysis platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Routing**: React Router v6
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts
- **Icons**: Lucide React
- **Build Tool**: Vite

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test
```

## Project Structure

```
src/
├── api/           # API client and endpoint definitions
│   ├── client.ts  # Axios instance with interceptors
│   ├── auth.ts    # Authentication endpoints
│   ├── user.ts    # User profile endpoints
│   ├── reading.ts # Reading/discovery endpoints
│   ├── writing.ts # Writing/posts endpoints
│   ├── curator.ts # Path curation endpoints
│   ├── authority.ts # Authority/leaderboard endpoints
│   └── safety.ts  # Content safety endpoints
│
├── stores/        # Zustand state stores
│   ├── authStore.ts      # Authentication state
│   ├── uiStore.ts        # UI preferences (theme, sidebar)
│   └── notificationStore.ts # Toast notifications
│
├── hooks/         # React Query hooks
│   ├── useAuth.ts    # Auth mutations
│   ├── useUser.ts    # User queries
│   ├── useReading.ts # Reading queries
│   ├── useWriting.ts # Writing queries
│   ├── useCurator.ts # Curator queries
│   └── useAuthority.ts # Authority queries
│
├── components/
│   ├── ui/        # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Avatar.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Toast.tsx
│   │   ├── Modal.tsx
│   │   ├── ErrorBoundary.tsx
│   │   ├── PageLoader.tsx
│   │   └── EmptyState.tsx
│   │
│   ├── layout/    # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── DashboardLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   └── ProtectedRoute.tsx
│   │
│   ├── charts/    # Chart components
│   │   ├── RadarChart.tsx
│   │   └── MetricCard.tsx
│   │
│   └── features/  # Feature-specific components
│       ├── VoiceProfile.tsx
│       ├── ActivityFeed.tsx
│       ├── AuthorityProgress.tsx
│       ├── ReadingPath.tsx
│       ├── ReadingStreak.tsx
│       ├── PostCard.tsx
│       └── SafetyBadge.tsx
│
├── pages/
│   ├── auth/      # Login, Signup
│   ├── dashboard/ # Overview, Settings
│   ├── reader/    # Discover, Bookmarks, Streak
│   ├── writer/    # MyWriting, Drafts, Editor
│   ├── curator/   # MyPaths, PathEditor
│   ├── authority/ # AuthorityHub, Leaderboard, ImpactStats
│   └── public/    # NotFound
│
├── types/         # TypeScript type definitions
├── styles/        # Global CSS
├── router.tsx     # Route definitions
├── App.tsx        # Root component
└── main.tsx       # Entry point
```

## Features

### Reader Features
- Post discovery with filters and tags
- Bookmark management
- Reading history tracking
- Reading streak with milestones

### Writer Features
- Post creation and editing
- Draft management
- Auto-save functionality
- Voice analysis integration
- Publish flow

### Curator Features
- Reading path creation
- Drag-and-drop post ordering
- Path analytics
- Publish/unpublish paths

### Authority Features
- Authority score tracking
- Global leaderboard with region filters
- Impact statistics
- Badge showcase

## Environment Variables

```env
VITE_API_URL=/api  # Backend API URL
```

## API Proxy

Development server proxies `/api` requests to `http://localhost:8000`.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Proprietary - All rights reserved.
