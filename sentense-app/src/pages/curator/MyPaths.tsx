import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Route, Plus, Search, Users, Eye, MoreHorizontal, Edit, Trash2, Send, Archive } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useCuratorPaths, useDeletePath, usePublishPath, useUnpublishPath } from '@/hooks';
import { Card, CardContent, Button, Input, Badge, Skeleton } from '@/components/ui';
import { ReadingPath } from '@/api';

// Mock data
const mockPaths: ReadingPath[] = [
  {
    id: 'path_01',
    title: 'Canadian Voices: Modern Literary Fiction',
    description: 'A curated journey through contemporary Canadian literature, featuring diverse voices and perspectives.',
    icon: '📖',
    status: 'published',
    posts: [],
    followers: 438,
    completions: 127,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    publishedAt: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'path_02',
    title: 'Nature Writing & Environmental Essays',
    description: 'Explore the intersection of nature and narrative through powerful environmental writing.',
    icon: '🌲',
    status: 'published',
    posts: [],
    followers: 312,
    completions: 89,
    createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    publishedAt: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'path_03',
    title: "Finding Your Voice: A Writer's Journey",
    description: 'A path for aspiring writers looking to develop their unique voice and style.',
    icon: '✍️',
    status: 'published',
    posts: [],
    followers: 297,
    completions: 156,
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    publishedAt: new Date(Date.now() - 55 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 'path_04',
    title: 'The Art of Short Fiction',
    description: 'Master the craft of short story writing with examples from the best.',
    icon: '📚',
    status: 'draft',
    posts: [],
    followers: 0,
    completions: 0,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

export const MyPaths = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'published' | 'draft'>('all');

  const { data, isLoading } = useCuratorPaths();
  const deletePath = useDeletePath();
  const publishPath = usePublishPath();
  const unpublishPath = useUnpublishPath();

  const paths = data?.data || mockPaths;
  const loading = isLoading && !paths.length;

  const filteredPaths = paths
    .filter((p) => filter === 'all' || p.status === filter)
    .filter((p) => p.title.toLowerCase().includes(searchQuery.toLowerCase()));

  const totalFollowers = paths.reduce((sum, p) => sum + p.followers, 0);
  const publishedCount = paths.filter((p) => p.status === 'published').length;

  const handleEdit = (pathId: string) => {
    navigate(`/curator/paths/${pathId}/edit`);
    setMenuOpen(null);
  };

  const handleDelete = (pathId: string) => {
    if (confirm('Are you sure you want to delete this path?')) {
      deletePath.mutate(pathId);
    }
    setMenuOpen(null);
  };

  const handlePublish = (pathId: string) => {
    publishPath.mutate(pathId);
    setMenuOpen(null);
  };

  const handleUnpublish = (pathId: string) => {
    unpublishPath.mutate(pathId);
    setMenuOpen(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Route className="h-6 w-6 text-coral-500" />
            My Paths
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {publishedCount} published • {totalFollowers.toLocaleString()} total followers
          </p>
        </div>
        <Button leftIcon={<Plus className="h-4 w-4" />} onClick={() => navigate('/curator/paths/new')}>
          Create Path
        </Button>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search paths..."
            leftIcon={<Search className="h-5 w-5" />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {(['all', 'published', 'draft'] as const).map((f) => (
            <Button
              key={f}
              variant={filter === f ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setFilter(f)}
              className="capitalize"
            >
              {f}
            </Button>
          ))}
        </div>
      </div>

      {/* Paths List */}
      {loading ? (
        <div className="space-y-4">
          {Array(3).fill(0).map((_, i) => (
            <Card key={i}>
              <CardContent>
                <div className="flex items-start gap-4">
                  <Skeleton variant="rectangular" width={56} height={56} className="rounded-xl" />
                  <div className="flex-1">
                    <Skeleton variant="text" width="50%" height={24} className="mb-2" />
                    <Skeleton variant="text" width="100%" height={16} className="mb-3" />
                    <Skeleton variant="text" width="40%" height={14} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredPaths.length === 0 ? (
        <div className="text-center py-12">
          <Route className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No paths match your search' : 'No paths yet'}
          </p>
          {!searchQuery && (
            <Button variant="outline" className="mt-4" onClick={() => navigate('/curator/paths/new')}>
              Create Your First Path
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPaths.map((path) => (
            <Card
              key={path.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleEdit(path.id)}
            >
              <CardContent>
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-coral-400 to-coral-600 rounded-xl flex items-center justify-center text-white text-2xl flex-shrink-0">
                    {path.icon || '📚'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                        {path.title}
                      </h3>
                      <Badge
                        variant={path.status === 'published' ? 'success' : 'warning'}
                        size="sm"
                      >
                        {path.status === 'published' ? 'Published' : 'Draft'}
                      </Badge>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2 mb-3">
                      {path.description}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        {path.followers.toLocaleString()} followers
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        {path.completions} completions
                      </span>
                      <span>•</span>
                      <span>Updated {formatDistanceToNow(new Date(path.updatedAt), { addSuffix: true })}</span>
                    </div>
                  </div>
                  <div className="relative" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setMenuOpen(menuOpen === path.id ? null : path.id)}
                    >
                      <MoreHorizontal className="h-5 w-5" />
                    </Button>
                    {menuOpen === path.id && (
                      <div className="absolute right-0 mt-1 w-44 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 shadow-lg py-1 z-10">
                        <button
                          onClick={() => handleEdit(path.id)}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                          <Edit className="h-4 w-4" />
                          Edit
                        </button>
                        {path.status === 'draft' ? (
                          <button
                            onClick={() => handlePublish(path.id)}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-950/30"
                          >
                            <Send className="h-4 w-4" />
                            Publish
                          </button>
                        ) : (
                          <button
                            onClick={() => handleUnpublish(path.id)}
                            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                          >
                            <Archive className="h-4 w-4" />
                            Unpublish
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(path.id)}
                          className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30"
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
