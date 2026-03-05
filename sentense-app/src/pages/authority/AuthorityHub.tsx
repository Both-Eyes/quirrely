import { Crown, TrendingUp, Users, Target, Award, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuthorityStatus, useAuthorityProgress, useAuthorityBadges } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Badge, Avatar, Skeleton } from '@/components/ui';
import { MetricCard } from '@/components/charts';
import { AuthorityProgress as AuthorityProgressComponent } from '@/components/features';

// Mock data
const mockStatus = {
  score: 94.7,
  level: 'authority_curator',
  rank: 23,
  percentile: 99.2,
  tier: 'Authority Curator',
  nextMilestone: {
    name: 'Legendary Curator',
    threshold: 100,
    progress: 94.7,
  },
};

const mockProgress = {
  currentScore: 94.7,
  previousScore: 92.4,
  change: 2.3,
  milestones: [
    { id: 'm1', name: 'First Path', description: 'Create your first reading path', threshold: 10, achieved: true, achievedAt: '2025-06-15' },
    { id: 'm2', name: 'Community Builder', description: 'Reach 100 path followers', threshold: 30, achieved: true, achievedAt: '2025-07-20' },
    { id: 'm3', name: 'Trusted Voice', description: 'Reach 500 path followers', threshold: 50, achieved: true, achievedAt: '2025-09-01' },
    { id: 'm4', name: 'Authority Status', description: 'Achieve Authority Curator tier', threshold: 80, achieved: true, achievedAt: '2025-11-15' },
    { id: 'm5', name: 'Legendary Curator', description: 'Reach perfect authority score', threshold: 100, achieved: false },
  ],
  history: [],
};

const mockBadges = [
  { id: 'b1', name: 'Trailblazer', description: 'Created 10+ reading paths', icon: '🛤️', rarity: 'rare' as const, earnedAt: '2025-08-15' },
  { id: 'b2', name: 'Crowd Favorite', description: '1000+ path followers', icon: '👑', rarity: 'epic' as const, earnedAt: '2025-10-01' },
  { id: 'b3', name: 'Consistent Creator', description: '30-day curation streak', icon: '🔥', rarity: 'rare' as const, earnedAt: '2025-09-20' },
  { id: 'b4', name: 'Canadian Voice', description: 'Featured in Canadian spotlight', icon: '🍁', rarity: 'legendary' as const, earnedAt: '2025-11-01' },
];

const rarityColors = {
  common: 'bg-gray-100 dark:bg-gray-800 text-gray-600',
  rare: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600',
  epic: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600',
  legendary: 'bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30 text-amber-600',
};

export const AuthorityHub = () => {
  const { data: status, isLoading: statusLoading } = useAuthorityStatus();
  const { data: progress, isLoading: progressLoading } = useAuthorityProgress();
  const { data: badges, isLoading: badgesLoading } = useAuthorityBadges();

  const displayStatus = status || mockStatus;
  const displayProgress = progress || mockProgress;
  const displayBadges = badges || mockBadges;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-amber-500 to-yellow-500 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
            <Crown className="h-8 w-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Authority Hub</h1>
            <p className="text-amber-100">Welcome to the highest tier of Quirrely</p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Authority Score"
          value={displayStatus.score.toFixed(1)}
          trend={{ value: displayProgress.change, direction: 'up', period: 'this month' }}
          icon={<Crown className="h-6 w-6 text-amber-600" />}
          variant="gold"
          loading={statusLoading}
        />
        <MetricCard
          label="Global Rank"
          value={`#${displayStatus.rank}`}
          icon={<TrendingUp className="h-6 w-6 text-coral-500" />}
          loading={statusLoading}
        />
        <MetricCard
          label="Percentile"
          value={`${displayStatus.percentile}%`}
          icon={<Target className="h-6 w-6 text-coral-500" />}
          loading={statusLoading}
        />
        <MetricCard
          label="Badges Earned"
          value={displayBadges.length}
          icon={<Award className="h-6 w-6 text-coral-500" />}
          loading={badgesLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Progress */}
        <div className="lg:col-span-2">
          <AuthorityProgressComponent
            score={displayStatus.score}
            level={displayStatus.level}
            rank={displayStatus.rank}
            percentile={displayStatus.percentile}
            loading={statusLoading}
          />
        </div>

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Link
                to="/authority/leaderboard"
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">
                    <TrendingUp className="h-5 w-5 text-amber-600" />
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">Leaderboard</span>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </Link>
              <Link
                to="/authority/impact"
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                    <Users className="h-5 w-5 text-green-600" />
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">Impact Stats</span>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </Link>
              <Link
                to="/curator/paths"
                className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-coral-100 dark:bg-coral-900/30 rounded-lg flex items-center justify-center">
                    <Target className="h-5 w-5 text-coral-600" />
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">Manage Paths</span>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Milestones */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Authority Milestones
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {/* Progress Line */}
            <div className="absolute top-6 left-6 right-6 h-1 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-yellow-500 rounded-full"
                style={{ width: `${displayStatus.score}%` }}
              />
            </div>
            
            {/* Milestone Points */}
            <div className="flex justify-between relative">
              {displayProgress.milestones.map((milestone, i) => (
                <div key={milestone.id} className="flex flex-col items-center">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center z-10 ${
                      milestone.achieved
                        ? 'bg-gradient-to-br from-amber-400 to-yellow-500 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-400'
                    }`}
                  >
                    {milestone.achieved ? '✓' : milestone.threshold}
                  </div>
                  <p className="text-xs font-medium text-gray-900 dark:text-white mt-2 text-center max-w-20">
                    {milestone.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    {milestone.threshold} pts
                  </p>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Badges */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Your Badges
          </CardTitle>
        </CardHeader>
        <CardContent>
          {badgesLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Array(4).fill(0).map((_, i) => (
                <Skeleton key={i} variant="rectangular" height={120} className="rounded-xl" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {displayBadges.map((badge) => (
                <div
                  key={badge.id}
                  className={`p-4 rounded-xl ${rarityColors[badge.rarity]} text-center`}
                >
                  <div className="text-3xl mb-2">{badge.icon}</div>
                  <p className="font-semibold text-gray-900 dark:text-white text-sm">{badge.name}</p>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{badge.description}</p>
                  <Badge
                    variant={badge.rarity === 'legendary' ? 'gold' : 'default'}
                    size="sm"
                    className="mt-2 capitalize"
                  >
                    {badge.rarity}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
