import { Users, BookOpen, Flame, PenTool, Crown } from 'lucide-react';
import { useAuthStore } from '@/stores';
import { useUserStats, useVoiceProfile, useActivity } from '@/hooks';
import { MetricCard } from '@/components/charts';
import { VoiceProfile, ActivityFeed, ReadingPathList, AuthorityProgress } from '@/components/features';
import type { ReadingPathData } from '@/components/features';

// Mock data for demo (will be replaced with real API calls)
const mockPaths: ReadingPathData[] = [
  {
    id: 'path_01',
    title: 'Canadian Voices: Modern Literary Fiction',
    postsCount: 12,
    followers: 438,
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'path_02',
    title: 'Nature Writing & Environmental Essays',
    postsCount: 8,
    followers: 312,
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'path_03',
    title: "Finding Your Voice: A Writer's Journey",
    postsCount: 15,
    followers: 297,
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

const mockActivity = [
  { id: '1', type: 'follow' as const, content: '23 new followers on your Canadian Voices path', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: '2', type: 'badge' as const, content: 'Earned Consistency Badge — 23 day reading streak!', timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString() },
  { id: '3', type: 'feature' as const, content: 'Your essay was featured in Weekly Picks', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() },
  { id: '4', type: 'milestone' as const, content: 'Your path reached 400+ followers', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString() },
];

const mockVoiceProfile = {
  primary: 'assertive',
  secondary: 'narrative',
  openness: 'balanced' as const,
  mode: 'ASSERTIVE_BALANCED',
  tokens: [
    { name: 'Confident', weight: 0.89 },
    { name: 'Warm', weight: 0.76 },
    { name: 'Structured', weight: 0.82 },
    { name: 'Narrative', weight: 0.91 },
    { name: 'Engaged', weight: 0.85 },
  ],
  dimensions: {
    assertiveness: 0.87,
    formality: 0.62,
    detail: 0.74,
    poeticism: 0.68,
    openness: 0.55,
    dynamism: 0.81,
  },
  confidence: 0.872,
  analysesCount: 47,
  lastAnalysis: new Date().toISOString(),
};

export const Overview = () => {
  const { user } = useAuthStore();
  
  // React Query hooks (will use mock data for now since API isn't connected)
  const { data: stats, isLoading: statsLoading } = useUserStats();
  const { data: voiceProfile, isLoading: voiceLoading } = useVoiceProfile();
  const { data: activity, isLoading: activityLoading } = useActivity(5);

  // Tier checks
  const isAuthorityTier = user?.tier === 'authority_curator' || user?.tier === 'authority_writer';
  const isFeaturedTier = user?.tier === 'featured_writer' || user?.tier === 'featured_curator';
  const isPaidTier = isAuthorityTier || isFeaturedTier || user?.tier === 'pro' || user?.tier === 'curator';
  const isCuratorTrack = user?.tier === 'curator' || user?.tier === 'featured_curator' || user?.tier === 'authority_curator';
  const isWriterTrack = user?.tier === 'pro' || user?.tier === 'featured_writer' || user?.tier === 'authority_writer';
  
  // Addon checks
  const hasVoiceStyle = user?.addons?.includes('voice_style') ?? false;
  
  // Use real data if available, otherwise use mocks
  const displayVoice = voiceProfile || mockVoiceProfile;
  const displayActivity = activity || mockActivity;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back, {user?.name?.split(' ')[0] || 'Writer'}! {user?.countryFlag || '🍁'}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Here's what's happening with your writing journey
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isAuthorityTier && (
          <MetricCard
            label="Authority Score"
            value="94.7"
            trend={{ value: 2.3, direction: 'up', period: 'this month' }}
            icon={<Crown className="h-6 w-6 text-amber-600" />}
            variant="gold"
            loading={statsLoading}
          />
        )}
        <MetricCard
          label="Path Followers"
          value={stats?.pathFollowers?.toLocaleString() || '1,247'}
          trend={{ value: 12, direction: 'up', period: 'this week' }}
          icon={<Users className="h-6 w-6 text-coral-500" />}
          loading={statsLoading}
        />
        <MetricCard
          label="Total Reads"
          value={stats?.postsRead?.toLocaleString() || '3,842'}
          trend={{ value: 8, direction: 'up', period: 'this month' }}
          icon={<BookOpen className="h-6 w-6 text-coral-500" />}
          loading={statsLoading}
        />
        <MetricCard
          label="Reading Streak"
          value={`${stats?.readingStreak || 23} days`}
          icon={<Flame className="h-6 w-6 text-coral-500" />}
          loading={statsLoading}
        />
        {!isAuthorityTier && (
          <MetricCard
            label="Posts Written"
            value={stats?.postsWritten || 8}
            trend={{ value: 5, direction: 'up', period: 'this month' }}
            icon={<PenTool className="h-6 w-6 text-coral-500" />}
            loading={statsLoading}
          />
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Voice Profile - takes 2 columns */}
        <div className="lg:col-span-2">
          <VoiceProfile profile={displayVoice} loading={voiceLoading} />
        </div>

        {/* Right column */}
        <div className="space-y-6">
          {/* Authority Progress (if authority tier) */}
          {isAuthorityTier && (
            <AuthorityProgress
              score={94.7}
              level={user?.tier || 'authority_curator'}
              rank={23}
              percentile={99.2}
            />
          )}
          
          {/* Activity Feed */}
          <ActivityFeed
            activities={displayActivity}
            loading={activityLoading}
            limit={4}
          />
        </div>
      </div>

      {/* Reading Paths */}
      <ReadingPathList
        paths={mockPaths}
        title="Your Popular Reading Paths"
        limit={3}
      />
    </div>
  );
};
