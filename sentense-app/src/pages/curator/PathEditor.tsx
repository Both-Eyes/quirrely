import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Save, Send, Plus, GripVertical, Trash2, Search, X
} from 'lucide-react';
import { useCuratorPath, useCreatePath, useUpdatePath, usePublishPath, useDiscoverPosts } from '@/hooks';
import { Card, CardContent, Button, Input, Badge, Avatar, Skeleton } from '@/components/ui';
import { useToast } from '@/components/ui/Toast';
import { Post } from '@/api';

// Mock posts for adding to path
const mockAvailablePosts: Post[] = [
  { id: 'p1', title: 'The Art of Confident Writing', excerpt: 'Discover how to infuse your prose...', author: { id: 'a1', name: 'Sarah Mitchell', handle: 'sarah' }, readTime: 5, publishedAt: new Date().toISOString(), tags: ['writing'], reactions: 127, bookmarked: false },
  { id: 'p2', title: 'Finding Your Voice in Nature Writing', excerpt: 'How the natural world can inspire...', author: { id: 'a2', name: 'James Crawford', handle: 'james' }, readTime: 8, publishedAt: new Date().toISOString(), tags: ['nature'], reactions: 89, bookmarked: false },
  { id: 'p3', title: 'The Power of Minimalist Prose', excerpt: 'Less is more: why cutting words...', author: { id: 'a3', name: 'Elena Rodriguez', handle: 'elena' }, readTime: 4, publishedAt: new Date().toISOString(), tags: ['minimalism'], reactions: 156, bookmarked: false },
  { id: 'p4', title: 'Storytelling Secrets from Canadian Literature', excerpt: 'What we can learn from...', author: { id: 'a4', name: 'Michael Chen', handle: 'michael' }, readTime: 7, publishedAt: new Date().toISOString(), tags: ['storytelling'], reactions: 203, bookmarked: false },
];

interface PathPostItem {
  id: string;
  postId: string;
  position: number;
  note?: string;
  post: Post;
}

const icons = ['📖', '🌲', '✍️', '📚', '🎯', '💡', '🔥', '⭐', '🚀', '🌟', '📝', '🎨'];

export const PathEditor = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success } = useToast();
  
  const isEditing = !!id && id !== 'new';
  
  const { data: existingPath, isLoading: pathLoading } = useCuratorPath(isEditing ? id : '');
  const createPath = useCreatePath();
  const updatePath = useUpdatePath();
  const publishPath = usePublishPath();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [icon, setIcon] = useState('📖');
  const [posts, setPosts] = useState<PathPostItem[]>([]);
  const [showAddPost, setShowAddPost] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Load existing path data
  useEffect(() => {
    if (existingPath) {
      setTitle(existingPath.title);
      setDescription(existingPath.description);
      setIcon(existingPath.icon || '📖');
      setPosts(existingPath.posts);
    }
  }, [existingPath]);

  const handleSave = async () => {
    if (!title.trim()) return;
    
    setIsSaving(true);
    try {
      const data = {
        title,
        description,
        icon,
        posts: posts.map((p, i) => ({ postId: p.postId, note: p.note, position: i })),
      };
      
      if (isEditing && id) {
        await updatePath.mutateAsync({ id, data });
      } else {
        await createPath.mutateAsync(data);
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!title.trim() || posts.length === 0) return;
    
    await handleSave();
    if (id) {
      await publishPath.mutateAsync(id);
    }
  };

  const handleAddPost = (post: Post) => {
    if (posts.some((p) => p.postId === post.id)) return;
    
    setPosts([
      ...posts,
      {
        id: `temp_${Date.now()}`,
        postId: post.id,
        position: posts.length,
        post,
      },
    ]);
    setShowAddPost(false);
    setSearchQuery('');
  };

  const handleRemovePost = (postId: string) => {
    setPosts(posts.filter((p) => p.postId !== postId));
  };

  const handleMovePost = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === posts.length - 1)
    ) return;
    
    const newPosts = [...posts];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newPosts[index], newPosts[targetIndex]] = [newPosts[targetIndex], newPosts[index]];
    setPosts(newPosts);
  };

  const filteredAvailablePosts = mockAvailablePosts.filter(
    (p) =>
      !posts.some((pp) => pp.postId === p.id) &&
      (p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.author.name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (pathLoading && isEditing) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" width="30%" height={40} />
        <Skeleton variant="rectangular" height={200} className="rounded-xl" />
        <Skeleton variant="rectangular" height={300} className="rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/curator/paths')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              {isEditing ? 'Edit Path' : 'Create New Path'}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {posts.length} posts in this path
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleSave}
            isLoading={isSaving}
            leftIcon={<Save className="h-4 w-4" />}
          >
            Save
          </Button>
          <Button
            onClick={handlePublish}
            isLoading={publishPath.isPending}
            leftIcon={<Send className="h-4 w-4" />}
            disabled={!title.trim() || posts.length === 0}
          >
            Publish
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Path Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <Card padding="lg">
            <h2 className="font-semibold text-gray-900 dark:text-white mb-4">Path Details</h2>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-16 h-16 bg-gradient-to-br from-coral-400 to-coral-600 rounded-xl flex items-center justify-center text-3xl">
                    {icon}
                  </div>
                  <p className="text-xs text-gray-500">Icon</p>
                </div>
                <div className="flex-1">
                  <Input
                    label="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Give your path a compelling title..."
                  />
                </div>
              </div>
              
              {/* Icon Picker */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Choose an icon
                </label>
                <div className="flex flex-wrap gap-2">
                  {icons.map((i) => (
                    <button
                      key={i}
                      onClick={() => setIcon(i)}
                      className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl transition-colors ${
                        icon === i
                          ? 'bg-coral-100 dark:bg-coral-900/30 ring-2 ring-coral-500'
                          : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
                      }`}
                    >
                      {i}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="block w-full px-4 py-2.5 text-sm rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500"
                  placeholder="Describe what readers will learn or experience..."
                />
              </div>
            </div>
          </Card>

          {/* Posts in Path */}
          <Card padding="lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-gray-900 dark:text-white">Posts in Path</h2>
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Plus className="h-4 w-4" />}
                onClick={() => setShowAddPost(true)}
              >
                Add Post
              </Button>
            </div>

            {posts.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <p>No posts added yet</p>
                <p className="text-sm mt-1">Add posts to build your reading path</p>
              </div>
            ) : (
              <div className="space-y-3">
                {posts.map((item, index) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg group"
                  >
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => handleMovePost(index, 'up')}
                        disabled={index === 0}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ▲
                      </button>
                      <button
                        onClick={() => handleMovePost(index, 'down')}
                        disabled={index === posts.length - 1}
                        className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
                      >
                        ▼
                      </button>
                    </div>
                    <div className="w-8 h-8 bg-coral-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>
                    <Avatar name={item.post.author.name} size="sm" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {item.post.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {item.post.author.name} • {item.post.readTime} min read
                      </p>
                    </div>
                    <button
                      onClick={() => handleRemovePost(item.postId)}
                      className="p-2 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card padding="md">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Path Stats</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Posts</span>
                <span className="font-medium text-gray-900 dark:text-white">{posts.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Est. Time</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {posts.reduce((sum, p) => sum + p.post.readTime, 0)} min
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Status</span>
                <Badge variant={existingPath?.status === 'published' ? 'success' : 'warning'} size="sm">
                  {existingPath?.status === 'published' ? 'Published' : 'Draft'}
                </Badge>
              </div>
            </div>
          </Card>

          <Card padding="md">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• Start with an engaging introduction post</li>
              <li>• Order posts to build understanding</li>
              <li>• Include varied perspectives</li>
              <li>• End with actionable takeaways</li>
            </ul>
          </Card>
        </div>
      </div>

      {/* Add Post Modal */}
      {showAddPost && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-white">Add Post to Path</h3>
              <button onClick={() => setShowAddPost(false)}>
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
            <div className="p-4">
              <Input
                placeholder="Search posts..."
                leftIcon={<Search className="h-5 w-5" />}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="mb-4"
              />
              <div className="max-h-80 overflow-y-auto space-y-2">
                {filteredAvailablePosts.map((post) => (
                  <button
                    key={post.id}
                    onClick={() => handleAddPost(post)}
                    className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-left"
                  >
                    <Avatar name={post.author.name} size="sm" />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {post.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {post.author.name} • {post.readTime} min
                      </p>
                    </div>
                    <Plus className="h-5 w-5 text-coral-500" />
                  </button>
                ))}
                {filteredAvailablePosts.length === 0 && (
                  <p className="text-center py-4 text-gray-500">No posts found</p>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
