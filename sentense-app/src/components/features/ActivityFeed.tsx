import { formatDistanceToNow } from 'date-fns';
import { clsx } from 'clsx';
import {
  BookOpen,
  Users,
  Award,
  Route,
  FileText,
  Star,
  Target,
  TrendingUp,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Skeleton } from '@/components/ui';
import { Activity } from '@/types';

interface ActivityFeedProps {
  activities?: Activity[];
  loading?: boolean;
  limit?: number;
  showHeader?: boolean;
  compact?: boolean;
}

const activityIcons: Record<string, React.ReactNode> = {
  read: <BookOpen className="h-4 w-4" />,
  follow: <Users className="h-4 w-4" />,
  badge: <Award className="h-4 w-4" />,
  path: <Route className="h-4 w-4" />,
  publish: <FileText className="h-4 w-4" />,
  feature: <Star className="h-4 w-4" />,
  milestone: <Target className="h-4 w-4" />,
  default: <TrendingUp className="h-4 w-4" />,
};

const activityColors: Record<string, string> = {
  read: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
  follow: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
  badge: 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400',
  path: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
  publish: 'bg-coral-100 dark:bg-coral-900/30 text-coral-600 dark:text-coral-400',
  feature: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
  milestone: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400',
  default: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
};

const formatTime = (timestamp: string): string => {
  try {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  } catch {
    return 'recently';
  }
};

interface ActivityItemProps {
  activity: Activity;
  compact?: boolean;
}

const ActivityItem = ({ activity, compact }: ActivityItemProps) => {
  const icon = activityIcons[activity.type] || activityIcons.default;
  const colorClass = activityColors[activity.type] || activityColors.default;

  return (
    <div className={clsx(
      'flex items-start gap-3',
      !compact && 'pb-4 border-b border-gray-100 dark:border-gray-800 last:border-0 last:pb-0'
    )}>
      <div className={clsx(
        'rounded-full flex items-center justify-center flex-shrink-0',
        compact ? 'w-8 h-8' : 'w-10 h-10',
        colorClass
      )}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className={clsx(
          'text-gray-900 dark:text-white',
          compact ? 'text-sm' : 'text-sm'
        )}>
          {activity.content}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
          {formatTime(activity.timestamp)}
        </p>
      </div>
    </div>
  );
};

const ActivitySkeleton = () => (
  <div className="flex items-start gap-3 pb-4 border-b border-gray-100 dark:border-gray-800 last:border-0">
    <Skeleton variant="circular" width={40} height={40} />
    <div className="flex-1">
      <Skeleton variant="text" width="80%" height={16} className="mb-1" />
      <Skeleton variant="text" width="30%" height={12} />
    </div>
  </div>
);

export const ActivityFeed = ({
  activities,
  loading,
  limit,
  showHeader = true,
  compact = false,
}: ActivityFeedProps) => {
  const displayActivities = limit ? activities?.slice(0, limit) : activities;

  const content = (
    <div className={clsx('space-y-4', compact && 'space-y-3')}>
      {loading ? (
        <>
          <ActivitySkeleton />
          <ActivitySkeleton />
          <ActivitySkeleton />
          <ActivitySkeleton />
        </>
      ) : displayActivities && displayActivities.length > 0 ? (
        displayActivities.map((activity) => (
          <ActivityItem key={activity.id} activity={activity} compact={compact} />
        ))
      ) : (
        <div className="text-center py-6 text-gray-500 dark:text-gray-400">
          <p>No recent activity</p>
        </div>
      )}
    </div>
  );

  if (!showHeader) {
    return content;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          📋 Recent Activity
        </CardTitle>
        {activities && activities.length > (limit || 0) && (
          <a href="/dashboard/activity" className="text-sm text-coral-500 hover:text-coral-600 font-medium">
            View All →
          </a>
        )}
      </CardHeader>
      <CardContent>{content}</CardContent>
    </Card>
  );
};
