import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';
import { Bookmark, BookmarkCheck, Clock, Heart, MessageCircle } from 'lucide-react';
import { Card, Avatar, Badge, Skeleton } from '@/components/ui';
import { Post } from '@/api';

interface PostCardProps {
  post: Post;
  variant?: 'card' | 'list' | 'compact';
  onBookmark?: (postId: string) => void;
  onClick?: () => void;
}

interface PostListProps {
  posts?: Post[];
  loading?: boolean;
  variant?: 'card' | 'list';
  onBookmark?: (postId: string) => void;
  onPostClick?: (postId: string) => void;
  emptyMessage?: string;
}

const formatDate = (date: string): string => {
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
  } catch {
    return 'recently';
  }
};

export const PostCard = ({ post, variant = 'card', onBookmark, onClick }: PostCardProps) => {
  const handleBookmarkClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onBookmark?.(post.id);
  };

  if (variant === 'compact') {
    return (
      <button
        onClick={onClick}
        className="flex items-start gap-3 w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors text-left"
      >
        <Avatar name={post.author.name} src={post.author.avatarUrl} size="sm" />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 dark:text-white truncate">{post.title}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {post.author.name} • {post.readTime} min read
          </p>
        </div>
      </button>
    );
  }

  if (variant === 'list') {
    return (
      <button
        onClick={onClick}
        className="flex items-start gap-4 w-full p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-coral-300 dark:hover:border-coral-700 transition-colors text-left"
      >
        <Avatar name={post.author.name} src={post.author.avatarUrl} size="md" />
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{post.title}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">{post.excerpt}</p>
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span>{post.author.name}</span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {post.readTime} min
            </span>
            <span>{formatDate(post.publishedAt)}</span>
          </div>
        </div>
        <button
          onClick={handleBookmarkClick}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          {post.bookmarked ? (
            <BookmarkCheck className="h-5 w-5 text-coral-500" />
          ) : (
            <Bookmark className="h-5 w-5 text-gray-400" />
          )}
        </button>
      </button>
    );
  }

  // Card variant (default)
  return (
    <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={onClick}>
      <div className="p-5">
        {/* Author */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Avatar name={post.author.name} src={post.author.avatarUrl} size="sm" />
            <div>
              <p className="font-medium text-gray-900 dark:text-white text-sm">{post.author.name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">@{post.author.handle}</p>
            </div>
          </div>
          <button
            onClick={handleBookmarkClick}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {post.bookmarked ? (
              <BookmarkCheck className="h-5 w-5 text-coral-500" />
            ) : (
              <Bookmark className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>

        {/* Content */}
        <h3 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">{post.title}</h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-3 mb-4">{post.excerpt}</p>

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {post.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="default" size="sm">{tag}</Badge>
            ))}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-800">
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {post.readTime} min
            </span>
            <span className="flex items-center gap-1">
              <Heart className="h-4 w-4" />
              {post.reactions}
            </span>
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatDate(post.publishedAt)}
          </span>
        </div>
      </div>
    </Card>
  );
};

const PostSkeleton = ({ variant = 'card' }: { variant?: 'card' | 'list' }) => {
  if (variant === 'list') {
    return (
      <div className="flex items-start gap-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
        <Skeleton variant="circular" width={40} height={40} />
        <div className="flex-1">
          <Skeleton variant="text" width="70%" height={20} className="mb-2" />
          <Skeleton variant="text" width="100%" height={14} className="mb-1" />
          <Skeleton variant="text" width="80%" height={14} className="mb-2" />
          <Skeleton variant="text" width="40%" height={12} />
        </div>
      </div>
    );
  }

  return (
    <Card>
      <div className="p-5">
        <div className="flex items-center gap-3 mb-4">
          <Skeleton variant="circular" width={32} height={32} />
          <div>
            <Skeleton variant="text" width={100} height={14} className="mb-1" />
            <Skeleton variant="text" width={60} height={12} />
          </div>
        </div>
        <Skeleton variant="text" width="80%" height={20} className="mb-2" />
        <Skeleton variant="text" width="100%" height={14} className="mb-1" />
        <Skeleton variant="text" width="90%" height={14} className="mb-4" />
        <div className="flex gap-2 mb-4">
          <Skeleton variant="rectangular" width={60} height={22} className="rounded-full" />
          <Skeleton variant="rectangular" width={60} height={22} className="rounded-full" />
        </div>
        <Skeleton variant="text" width="50%" height={14} />
      </div>
    </Card>
  );
};

export const PostList = ({
  posts,
  loading,
  variant = 'card',
  onBookmark,
  onPostClick,
  emptyMessage = 'No posts found',
}: PostListProps) => {
  if (loading) {
    return (
      <div className={clsx(
        variant === 'card' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-3'
      )}>
        {Array(6).fill(0).map((_, i) => (
          <PostSkeleton key={i} variant={variant} />
        ))}
      </div>
    );
  }

  if (!posts || posts.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={clsx(
      variant === 'card' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-3'
    )}>
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          variant={variant}
          onBookmark={onBookmark}
          onClick={() => onPostClick?.(post.id)}
        />
      ))}
    </div>
  );
};
