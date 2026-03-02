import { clsx } from 'clsx';
import { Crown, Star, Shield, Zap, PenTool } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui';

interface AuthorityProgressProps {
  score?: number;
  level?: string;
  rank?: number;
  percentile?: number;
  loading?: boolean;
  compact?: boolean;
}

const levelConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  free: {
    icon: <Zap className="h-5 w-5" />,
    color: 'text-gray-500',
    label: 'Free',
  },
  pro: {
    icon: <Star className="h-5 w-5" />,
    color: 'text-coral-500',
    label: 'Pro',
  },
  curator: {
    icon: <Star className="h-5 w-5" />,
    color: 'text-coral-500',
    label: 'Curator',
  },
  featured_writer: {
    icon: <PenTool className="h-5 w-5" />,
    color: 'text-blue-500',
    label: 'Featured Writer',
  },
  featured_curator: {
    icon: <Shield className="h-5 w-5" />,
    color: 'text-purple-500',
    label: 'Featured Curator',
  },
  authority_writer: {
    icon: <Crown className="h-5 w-5" />,
    color: 'text-amber-500',
    label: 'Authority Writer',
  },
  authority_curator: {
    icon: <Crown className="h-5 w-5" />,
    color: 'text-amber-500',
    label: 'Authority Curator',
  },
};

export const AuthorityProgress = ({
  score = 0,
  level = 'free',
  rank,
  percentile,
  loading,
  compact = false,
}: AuthorityProgressProps) => {
  const config = levelConfig[level] || levelConfig.free;
  const isAuthority = level === 'authority_curator' || level === 'authority_writer';

  if (loading) {
    return (
      <Card variant={isAuthority ? 'gold' : 'default'}>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Skeleton variant="circular" width={40} height={40} />
              <div className="flex-1">
                <Skeleton variant="text" width="50%" height={20} />
                <Skeleton variant="text" width="30%" height={14} />
              </div>
            </div>
            <Skeleton variant="rectangular" height={8} className="rounded-full" />
            <Skeleton variant="text" width="40%" height={14} />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-3">
        <div className={clsx(
          'w-10 h-10 rounded-full flex items-center justify-center',
          isAuthority ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-gray-100 dark:bg-gray-800'
        )}>
          <span className={config.color}>{config.icon}</span>
        </div>
        <div>
          <p className="font-semibold text-gray-900 dark:text-white">
            {score.toFixed(1)}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {config.label}
          </p>
        </div>
      </div>
    );
  }

  return (
    <Card variant={isAuthority ? 'gold' : 'default'}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isAuthority ? '👑' : '🎯'} Authority Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Level indicator */}
          <div className="flex items-center gap-3">
            <div className={clsx(
              'w-12 h-12 rounded-full flex items-center justify-center',
              isAuthority ? 'bg-amber-100 dark:bg-amber-900/30' : 'bg-gray-100 dark:bg-gray-800'
            )}>
              <span className={config.color}>{config.icon}</span>
            </div>
            <div>
              <p className={clsx('font-bold', config.color)}>
                {config.label}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {isAuthority ? 'Highest Tier Achieved' : 'Current Level'}
              </p>
            </div>
          </div>

          {/* Progress bar */}
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Authority Score</span>
              <span className={clsx('font-semibold', isAuthority ? 'text-amber-600 dark:text-amber-400' : 'text-gray-900 dark:text-white')}>
                {score.toFixed(1)} / 100
              </span>
            </div>
            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className={clsx(
                  'h-full rounded-full transition-all duration-500',
                  isAuthority
                    ? 'bg-gradient-to-r from-amber-400 to-yellow-500'
                    : 'bg-coral-500'
                )}
                style={{ width: `${Math.min(score, 100)}%` }}
              />
            </div>
          </div>

          {/* Stats */}
          {(rank || percentile) && (
            <div className="flex gap-4 pt-2">
              {rank && (
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    #{rank}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Global Rank</p>
                </div>
              )}
              {percentile && (
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {percentile.toFixed(1)}%
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Percentile</p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
