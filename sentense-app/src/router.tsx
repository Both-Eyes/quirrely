import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout, DashboardLayout, ProtectedRoute } from '@/components/layout';
import { Login, Signup, ForgotPassword } from '@/pages/auth';
import { Overview, Settings, VoiceProfilePage, Partnership } from '@/pages/dashboard';
import { Discover, Bookmarks, Streak } from '@/pages/reader';
import { MyWriting, Drafts, Editor, Analytics } from '@/pages/writer';
import { MyPaths, PathEditor } from '@/pages/curator';
import { AuthorityHub, Leaderboard, ImpactStats } from '@/pages/authority';
import { NotFound } from '@/pages/public';
import { Help } from '@/pages/help';

export const router = createBrowserRouter([
  // Public routes
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },

  // Auth routes
  {
    element: <AuthLayout />,
    children: [
      {
        path: '/login',
        element: <Login />,
      },
      {
        path: '/signup',
        element: <Signup />,
      },
      {
        path: '/forgot-password',
        element: <ForgotPassword />,
      },
    ],
  },

  // Protected dashboard routes
  {
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      // Dashboard
      {
        path: '/dashboard',
        element: <Overview />,
      },
      {
        // Voice Profile - requires voice_style addon
        path: '/dashboard/voice',
        element: (
          <ProtectedRoute requiredAddon="voice_style">
            <VoiceProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/dashboard/settings',
        element: <Settings />,
      },
      {
        // Partnership - requires pro+ tier
        path: '/dashboard/partnership',
        element: (
          <ProtectedRoute 
            requiredTier={['pro', 'curator', 'featured_writer', 'featured_curator', 'authority_writer', 'authority_curator']}
          >
            <Partnership />
          </ProtectedRoute>
        ),
      },

      // Reader
      {
        path: '/reader/discover',
        element: <Discover />,
      },
      {
        path: '/reader/bookmarks',
        element: <Bookmarks />,
      },
      {
        path: '/reader/history',
        element: <div className="p-4">Reading History - Coming Soon</div>,
      },
      {
        path: '/reader/streak',
        element: <Streak />,
      },

      // Writer
      {
        path: '/writer/posts',
        element: <MyWriting />,
      },
      {
        path: '/writer/drafts',
        element: <Drafts />,
      },
      {
        path: '/writer/editor',
        element: <Editor />,
      },
      {
        path: '/writer/editor/:id',
        element: <Editor />,
      },
      {
        // Analytics - requires pro/curator+ tier
        path: '/writer/analytics',
        element: (
          <ProtectedRoute 
            requiredTier={['pro', 'curator', 'featured_writer', 'featured_curator', 'authority_writer', 'authority_curator']}
          >
            <Analytics />
          </ProtectedRoute>
        ),
      },

      // Curator
      {
        path: '/curator/paths',
        element: <MyPaths />,
      },
      {
        path: '/curator/paths/new',
        element: <PathEditor />,
      },
      {
        path: '/curator/paths/:id/edit',
        element: <PathEditor />,
      },
      {
        path: '/curator/followers',
        element: <div className="p-4">Path Followers - Coming Soon</div>,
      },
      {
        path: '/curator/featured',
        element: <div className="p-4">Featured - Coming Soon</div>,
      },
      {
        path: '/curator/analytics',
        element: <div className="p-4">Path Analytics - Coming Soon</div>,
      },

      // Authority
      {
        path: '/authority/hub',
        element: <AuthorityHub />,
      },
      {
        path: '/authority/leaderboard',
        element: <Leaderboard />,
      },
      {
        path: '/authority/impact',
        element: <ImpactStats />,
      },

      // Help
      {
        path: '/help',
        element: <Help />,
      },
    ],
  },

  // Catch all - 404 page
  {
    path: '*',
    element: <NotFound />,
  },
]);
