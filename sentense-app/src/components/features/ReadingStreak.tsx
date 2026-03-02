import { clsx } from 'clsx';
import { Flame, Calendar, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Skeleton } from '@/components/ui';
import { ReadingStreak as ReadingStreakType } from '@/api';

interface ReadingStreakProps {
  streak?: ReadingStreakType;
  loading?: boolean;
  compact?: boolean;
}

const dayNames = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

export const ReadingStreak = ({ streak, loading, compact = false }: ReadingStreakProps) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5" />
            Reading Streak
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Skeleton variant="circular" width={64} height={64} />
              <div>
                <Skeleton variant="text" width={80} height={32} />
                <Skeleton variant="text" width={60} height={16} />
              </div>
            </div>
            <div className="flex gap-2">
              {Array(7).fill(0).map((_, i) => (
                <Skeleton key={i} variant="rectangular" width={32} height={32} className="rounded-lg" />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentStreak = streak?.current || 0;
  const longestStreak = streak?.longest || 0;
  const thisWeek = streak?.thisWeek || Array(7).fill(false);

  if (compact) {
    return (
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center">
          <Flame className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{currentStreak}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">day streak</p>
        </div>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="h-5 w-5 text-orange-500" />
          Reading Streak
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Current Streak */}
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
              <Flame className="h-8 w-8 text-white" />
            </div>
            <div>
              <p className="text-4xl font-bold text-gray-900 dark:text-white">{currentStreak}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {currentStreak === 1 ? 'day' : 'days'} current streak
              </p>
            </div>
          </div>

          {/* This Week */}
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">This Week</p>
            <div className="flex gap-2">
              {thisWeek.map((completed, i) => (
                <div key={i} className="flex flex-col items-center gap-1">
                  <div
                    className={clsx(
                      'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                      completed
                        ? 'bg-gradient-to-br from-orange-400 to-red-500 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-400'
                    )}
                  >
                    {completed ? (
                      <Flame className="h-5 w-5" />
                    ) : (
                      <span className="text-sm">{dayNames[i]}</span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{dayNames[i]}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-800">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">{longestStreak}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Longest streak</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">{streak?.thisMonth || 0}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">This month</p>
              </div>
            </div>
          </div>

          {/* Motivation */}
          {currentStreak > 0 && currentStreak < longestStreak && (
            <div className="bg-orange-50 dark:bg-orange-950/30 rounded-lg p-3">
              <p className="text-sm text-orange-700 dark:text-orange-400">
                🔥 {longestStreak - currentStreak} more {longestStreak - currentStreak === 1 ? 'day' : 'days'} to beat your record!
              </p>
            </div>
          )}
          {currentStreak >= longestStreak && currentStreak > 0 && (
            <div className="bg-green-50 dark:bg-green-950/30 rounded-lg p-3">
              <p className="text-sm text-green-700 dark:text-green-400">
                🎉 You're at your longest streak! Keep it going!
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
