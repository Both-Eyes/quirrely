import { Flame, Calendar, BookOpen, Target, Trophy, TrendingUp } from 'lucide-react';
import { useReadingStreak, useReadingHistory } from '@/hooks';
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui';
import { ReadingStreak as ReadingStreakComponent } from '@/components/features';
import { MetricCard } from '@/components/charts';
import { formatDistanceToNow } from 'date-fns';

// Mock data
const mockStreak = {
  current: 23,
  longest: 31,
  lastReadDate: new Date().toISOString(),
  thisWeek: [true, true, true, true, true, true, false],
  thisMonth: 21,
};

const mockHistory = [
  { id: 'h1', title: 'The Art of Confident Writing', author: 'Sarah Mitchell', readAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), duration: 5 },
  { id: 'h2', title: 'Finding Your Voice in Nature Writing', author: 'James Crawford', readAt: new Date(Date.now() - 26 * 60 * 60 * 1000).toISOString(), duration: 8 },
  { id: 'h3', title: 'The Power of Minimalist Prose', author: 'Elena Rodriguez', readAt: new Date(Date.now() - 50 * 60 * 60 * 1000).toISOString(), duration: 4 },
  { id: 'h4', title: 'Storytelling Secrets from Canadian Literature', author: 'Michael Chen', readAt: new Date(Date.now() - 74 * 60 * 60 * 1000).toISOString(), duration: 7 },
];

const mockMilestones = [
  { id: 'm1', name: 'First Read', description: 'Read your first post', achieved: true, date: '2025-08-15' },
  { id: 'm2', name: '7-Day Streak', description: 'Maintain a 7-day reading streak', achieved: true, date: '2025-08-22' },
  { id: 'm3', name: 'Explorer', description: 'Read posts from 5 different voice profiles', achieved: true, date: '2025-09-01' },
  { id: 'm4', name: '30-Day Streak', description: 'Maintain a 30-day reading streak', achieved: false, progress: 23 },
  { id: 'm5', name: 'Deep Reader', description: 'Complete 50 deep reads', achieved: false, progress: 34 },
];

export const Streak = () => {
  const { data: streak, isLoading: streakLoading } = useReadingStreak();
  const { data: history, isLoading: historyLoading } = useReadingHistory();

  const displayStreak = streak || mockStreak;
  const displayHistory = history?.data || mockHistory;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Flame className="h-6 w-6 text-orange-500" />
          Reading Streak
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Track your reading habits and achievements
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Current Streak"
          value={displayStreak.current}
          unit="days"
          icon={<Flame className="h-6 w-6 text-orange-500" />}
          variant="default"
          loading={streakLoading}
        />
        <MetricCard
          label="Longest Streak"
          value={displayStreak.longest}
          unit="days"
          icon={<Trophy className="h-6 w-6 text-coral-500" />}
          loading={streakLoading}
        />
        <MetricCard
          label="This Month"
          value={displayStreak.thisMonth}
          unit="days"
          icon={<Calendar className="h-6 w-6 text-coral-500" />}
          loading={streakLoading}
        />
        <MetricCard
          label="Total Minutes"
          value="2,847"
          icon={<BookOpen className="h-6 w-6 text-coral-500" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Streak Card */}
        <div className="lg:col-span-2">
          <ReadingStreakComponent streak={displayStreak} loading={streakLoading} />
        </div>

        {/* Recent Reads */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Recent Reads
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {historyLoading ? (
                Array(4).fill(0).map((_, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <Skeleton variant="rectangular" width={8} height={40} className="rounded" />
                    <div className="flex-1">
                      <Skeleton variant="text" width="80%" height={16} className="mb-1" />
                      <Skeleton variant="text" width="50%" height={12} />
                    </div>
                  </div>
                ))
              ) : (
                displayHistory.map((item: any) => (
                  <div key={item.id} className="flex items-start gap-3">
                    <div className="w-1 h-full bg-coral-500 rounded-full" />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white text-sm">
                        {item.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {item.author} • {formatDistanceToNow(new Date(item.readAt), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Milestones */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Reading Milestones
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockMilestones.map((milestone) => (
              <div
                key={milestone.id}
                className={`p-4 rounded-xl border-2 ${
                  milestone.achieved
                    ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/30'
                    : 'border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {milestone.achieved ? (
                      <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                        <Trophy className="h-4 w-4 text-white" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-700 flex items-center justify-center">
                        <Target className="h-4 w-4 text-gray-500" />
                      </div>
                    )}
                    <h4 className="font-semibold text-gray-900 dark:text-white">
                      {milestone.name}
                    </h4>
                  </div>
                  {milestone.achieved && (
                    <Badge variant="success" size="sm">Achieved</Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {milestone.description}
                </p>
                {!milestone.achieved && milestone.progress !== undefined && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>{milestone.progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-coral-500 rounded-full"
                        style={{ width: `${milestone.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                {milestone.achieved && milestone.date && (
                  <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                    Achieved on {new Date(milestone.date).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
