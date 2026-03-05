import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Search, Grid, List, Trash2 } from 'lucide-react';
import { useBookmarks, useRemoveBookmark } from '@/hooks';
import { Input, Button, Card, CardContent, Avatar, Badge, Skeleton } from '@/components/ui';
import { Bookmark as BookmarkType, Post } from '@/api';
import { formatDistanceToNow } from 'date-fns';

// Mock data
const mockBookmarks: BookmarkType[] = [
  {
    id: 'b1',
    post: {
      id: '1',
      title: 'The Art of Confident Writing',
      excerpt: 'Discover how to infuse your prose with conviction and clarity...',
      author: { id: 'a1', name: 'Sarah Mitchell', handle: 'sarahmitchell' },
      readTime: 5,
      publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['writing', 'craft'],
      reactions: 127,
      bookmarked: true,
    },
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'b2',
    post: {
      id: '2',
      title: 'Finding Your Voice in Nature Writing',
      excerpt: 'How the natural world can inspire your unique literary voice...',
      author: { id: 'a2', name: 'James Crawford', handle: 'jcrawford' },
      readTime: 8,
      publishedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['nature', 'voice'],
      reactions: 89,
      bookmarked: true,
    },
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'b3',
    post: {
      id: '6',
      title: 'The Science of Reader Engagement',
      excerpt: 'Data-driven insights into what keeps readers hooked...',
      author: { id: 'a6', name: 'David Park', handle: 'dpark' },
      readTime: 10,
      publishedAt: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['engagement', 'analytics'],
      reactions: 145,
      bookmarked: true,
    },
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export const Bookmarks = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

  const { data, isLoading } = useBookmarks();
  const removeBookmark = useRemoveBookmark();

  const bookmarks = data?.data || mockBookmarks;
  const loading = isLoading && !bookmarks.length;

  const filteredBookmarks = bookmarks.filter((b) =>
    b.post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    b.post.author.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRemove = (e: React.MouseEvent, bookmarkId: string) => {
    e.stopPropagation();
    removeBookmark.mutate(bookmarkId);
  };

  const handlePostClick = (postId: string) => {
    navigate(`/reader/post/${postId}`);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Bookmarks</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Your saved posts</p>
        </div>
        <div className="space-y-3">
          {Array(5).fill(0).map((_, i) => (
            <div key={i} className="flex items-start gap-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800">
              <Skeleton variant="circular" width={40} height={40} />
              <div className="flex-1">
                <Skeleton variant="text" width="70%" height={20} className="mb-2" />
                <Skeleton variant="text" width="100%" height={14} className="mb-1" />
                <Skeleton variant="text" width="40%" height={12} />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Bookmark className="h-6 w-6 text-coral-500" />
            Bookmarks
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {bookmarks.length} saved {bookmarks.length === 1 ? 'post' : 'posts'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'list' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Search */}
      <Input
        placeholder="Search bookmarks..."
        leftIcon={<Search className="h-5 w-5" />}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      {/* Bookmarks List */}
      {filteredBookmarks.length === 0 ? (
        <div className="text-center py-12">
          <Bookmark className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No bookmarks match your search' : 'No bookmarks yet'}
          </p>
          {!searchQuery && (
            <Button variant="outline" className="mt-4" onClick={() => navigate('/reader/discover')}>
              Discover Posts
            </Button>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : 'space-y-3'}>
          {filteredBookmarks.map((bookmark) => (
            <Card
              key={bookmark.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handlePostClick(bookmark.post.id)}
            >
              <CardContent>
                <div className="flex items-start gap-4">
                  <Avatar name={bookmark.post.author.name} size="md" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                      {bookmark.post.title}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">
                      {bookmark.post.excerpt}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                      <span>{bookmark.post.author.name}</span>
                      <span>•</span>
                      <span>{bookmark.post.readTime} min read</span>
                      <span>•</span>
                      <span>Saved {formatDistanceToNow(new Date(bookmark.createdAt), { addSuffix: true })}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleRemove(e, bookmark.id)}
                    className="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove bookmark"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                {bookmark.post.tags.length > 0 && (
                  <div className="flex gap-1.5 mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                    {bookmark.post.tags.map((tag) => (
                      <Badge key={tag} variant="default" size="sm">#{tag}</Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
