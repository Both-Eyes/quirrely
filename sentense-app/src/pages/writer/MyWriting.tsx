import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PenTool, Plus, Search, Eye, Heart, MessageCircle, MoreHorizontal, Edit, Trash2, Archive } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useWritingPosts, useDeletePost, useArchivePost } from '@/hooks';
import { Card, CardContent, Button, Input, Badge, Skeleton } from '@/components/ui';
import { WritingPost } from '@/api';

// Mock data
const mockPosts: WritingPost[] = [
  {
    id: 'p1',
    title: 'The Art of Confident Writing',
    content: '',
    excerpt: 'Discover how to infuse your prose with conviction and clarity...',
    status: 'published',
    publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    wordCount: 1234,
    readTime: 5,
    tags: ['writing', 'craft'],
    reactions: 127,
    views: 1543,
    comments: 23,
  },
  {
    id: 'p2',
    title: 'Finding Your Voice Through Nature',
    content: '',
    excerpt: 'How the natural world can inspire your unique literary voice...',
    status: 'published',
    publishedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    wordCount: 2156,
    readTime: 8,
    tags: ['nature', 'voice'],
    reactions: 89,
    views: 876,
    comments: 15,
  },
  {
    id: 'p3',
    title: 'Lessons from Canadian Literature',
    content: '',
    excerpt: 'What we can learn from the great Canadian storytellers...',
    status: 'published',
    publishedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
    wordCount: 1876,
    readTime: 7,
    tags: ['canada', 'literature'],
    reactions: 156,
    views: 2341,
    comments: 34,
  },
];

export const MyWriting = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  const { data, isLoading } = useWritingPosts();
  const deletePost = useDeletePost();
  const archivePost = useArchivePost();

  const posts = data?.data || mockPosts;
  const loading = isLoading && !posts.length;

  const filteredPosts = posts.filter((p) =>
    p.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleEdit = (postId: string) => {
    navigate(`/writer/editor/${postId}`);
  };

  const handleDelete = (postId: string) => {
    if (confirm('Are you sure you want to delete this post?')) {
      deletePost.mutate(postId);
    }
    setMenuOpen(null);
  };

  const handleArchive = (postId: string) => {
    archivePost.mutate(postId);
    setMenuOpen(null);
  };

  const totalViews = posts.reduce((sum, p) => sum + p.views, 0);
  const totalReactions = posts.reduce((sum, p) => sum + p.reactions, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <PenTool className="h-6 w-6 text-coral-500" />
            My Writing
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {posts.length} published {posts.length === 1 ? 'post' : 'posts'} • {totalViews.toLocaleString()} views • {totalReactions} reactions
          </p>
        </div>
        <Button leftIcon={<Plus className="h-4 w-4" />} onClick={() => navigate('/writer/editor')}>
          New Post
        </Button>
      </div>

      {/* Search */}
      <Input
        placeholder="Search your posts..."
        leftIcon={<Search className="h-5 w-5" />}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      {/* Posts List */}
      {loading ? (
        <div className="space-y-4">
          {Array(3).fill(0).map((_, i) => (
            <Card key={i}>
              <CardContent>
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <Skeleton variant="text" width="60%" height={24} className="mb-2" />
                    <Skeleton variant="text" width="100%" height={16} className="mb-1" />
                    <Skeleton variant="text" width="80%" height={16} className="mb-3" />
                    <Skeleton variant="text" width="40%" height={14} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="text-center py-12">
          <PenTool className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No posts match your search' : 'No published posts yet'}
          </p>
          {!searchQuery && (
            <Button variant="outline" className="mt-4" onClick={() => navigate('/writer/editor')}>
              Write Your First Post
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPosts.map((post) => (
            <Card key={post.id} className="hover:shadow-md transition-shadow">
              <CardContent>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                        {post.title}
                      </h3>
                      <Badge variant="success" size="sm">Published</Badge>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2 mb-3">
                      {post.excerpt}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        {post.views.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        {post.reactions}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        {post.comments}
                      </span>
                      <span>•</span>
                      <span>{post.wordCount.toLocaleString()} words</span>
                      <span>•</span>
                      <span>Published {formatDistanceToNow(new Date(post.publishedAt!), { addSuffix: true })}</span>
                    </div>
                  </div>
                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setMenuOpen(menuOpen === post.id ? null : post.id)}
                    >
                      <MoreHorizontal className="h-5 w-5" />
                    </Button>
                    {menuOpen === post.id && (
                      <div className="absolute right-0 mt-1 w-40 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 shadow-lg py-1 z-10">
                        <button
                          onClick={() => handleEdit(post.id)}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                          <Edit className="h-4 w-4" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleArchive(post.id)}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                          <Archive className="h-4 w-4" />
                          Archive
                        </button>
                        <button
                          onClick={() => handleDelete(post.id)}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30"
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                {post.tags.length > 0 && (
                  <div className="flex gap-1.5 mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                    {post.tags.map((tag) => (
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
