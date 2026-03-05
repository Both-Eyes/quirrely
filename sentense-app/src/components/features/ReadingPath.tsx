import { clsx } from 'clsx';
import { Users, Clock, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge, Skeleton } from '@/components/ui';

export interface ReadingPathData {
  id: string;
  title: string;
  description?: string;
  postsCount: number;
  followers: number;
  completions?: number;
  updatedAt: string;
  icon?: string;
}

interface ReadingPathProps {
  path: ReadingPathData;
  variant?: 'card' | 'list' | 'compact';
  onClick?: () => void;
}

interface ReadingPathListProps {
  paths?: ReadingPathData[];
  loading?: boolean;
  title?: string;
  showHeader?: boolean;
  limit?: number;
}

const formatUpdated = (date: string): string => {
  try {
    const d = new Date(date);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Updated today';
    if (diffDays === 1) return 'Updated yesterday';
    if (diffDays < 7) return `Updated ${diffDays} days ago`;
    if (diffDays < 30) return `Updated ${Math.floor(diffDays / 7)} weeks ago`;
    return `Updated ${Math.floor(diffDays / 30)} months ago`;
  } catch {
    return 'Recently updated';
  }
};

export const ReadingPath = ({ path, variant = 'list', onClick }: ReadingPathProps) => {
  const icons = ['📖', '🌲', '✍️', '🎯', '💡', '🔥', '⭐', '🚀'];
  const icon = path.icon || icons[path.id.charCodeAt(0) % icons.length];

  if (variant === 'compact') {
    return (
      <button
        onClick={onClick}
        className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left"
      >
        <span className="text-xl">{icon}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 dark:text-white truncate">
            {path.title}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {path.followers} followers
          </p>
        </div>
        <ChevronRight className="h-4 w-4 text-gray-400" />
      </button>
    );
  }

  if (variant === 'card') {
    return (
      <Card
        className="cursor-pointer hover:shadow-lg transition-shadow"
        onClick={onClick}
      >
        <CardContent>
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-coral-400 to-coral-600 rounded-xl flex items-center justify-center text-white text-2xl flex-shrink-0">
              {icon}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                {path.title}
              </h4>
              {path.description && (
                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
                  {path.description}
                </p>
              )}
              <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <span>{path.postsCount} posts</span>
                <span className="flex items-center gap-1">
                  <Users className="h-3.5 w-3.5" />
                  {path.followers}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // List variant (default)
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-4 w-full p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left"
    >
      <div className="w-12 h-12 bg-gradient-to-br from-coral-400 to-coral-600 rounded-xl flex items-center justify-center text-white text-xl flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-gray-900 dark:text-white truncate">
          {path.title}
        </h4>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {path.postsCount} posts • {formatUpdated(path.updatedAt)}
        </p>
      </div>
      <div className="text-right flex-shrink-0">
        <p className="text-xl font-bold text-green-600 dark:text-green-400">
          {path.followers.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">followers</p>
      </div>
    </button>
  );
};

const PathSkeleton = () => (
  <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
    <Skeleton variant="rectangular" width={48} height={48} className="rounded-xl" />
    <div className="flex-1">
      <Skeleton variant="text" width="60%" height={20} className="mb-1" />
      <Skeleton variant="text" width="40%" height={16} />
    </div>
    <div className="text-right">
      <Skeleton variant="text" width={40} height={24} className="mb-1" />
      <Skeleton variant="text" width={50} height={12} />
    </div>
  </div>
);

export const ReadingPathList = ({
  paths,
  loading,
  title = 'Reading Paths',
  showHeader = true,
  limit,
}: ReadingPathListProps) => {
  const displayPaths = limit ? paths?.slice(0, limit) : paths;

  const content = (
    <div className="space-y-3">
      {loading ? (
        <>
          <PathSkeleton />
          <PathSkeleton />
          <PathSkeleton />
        </>
      ) : displayPaths && displayPaths.length > 0 ? (
        displayPaths.map((path) => (
          <ReadingPath key={path.id} path={path} />
        ))
      ) : (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No reading paths yet</p>
          <p className="text-sm mt-1">Create your first reading path to share curated content</p>
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
          🛤️ {title}
        </CardTitle>
        {paths && paths.length > (limit || 0) && (
          <a href="/curator/paths" className="text-sm text-coral-500 hover:text-coral-600 font-medium">
            Manage Paths →
          </a>
        )}
      </CardHeader>
      <CardContent>{content}</CardContent>
    </Card>
  );
};
