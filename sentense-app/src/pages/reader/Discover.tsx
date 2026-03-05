import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, TrendingUp, Clock, Sparkles } from 'lucide-react';
import { useDiscoverPosts, useAddBookmark } from '@/hooks';
import { Input, Button, Badge } from '@/components/ui';
import { PostList } from '@/components/features';
import { Post } from '@/api';

// Mock data for demo
const mockPosts: Post[] = [
  {
    id: '1',
    title: 'The Art of Confident Writing',
    excerpt: 'Discover how to infuse your prose with conviction and clarity. Learn techniques that top writers use to command attention...',
    author: { id: 'a1', name: 'Sarah Mitchell', handle: 'sarahmitchell', avatarUrl: undefined },
    voiceProfile: 'assertive',
    readTime: 5,
    publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['writing', 'craft', 'confidence'],
    reactions: 127,
    bookmarked: false,
  },
  {
    id: '2',
    title: 'Finding Your Voice in Nature Writing',
    excerpt: 'How the natural world can inspire your unique literary voice. Explore the intersection of environment and expression...',
    author: { id: 'a2', name: 'James Crawford', handle: 'jcrawford', avatarUrl: undefined },
    voiceProfile: 'narrative',
    readTime: 8,
    publishedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['nature', 'voice', 'inspiration'],
    reactions: 89,
    bookmarked: true,
  },
  {
    id: '3',
    title: 'The Power of Minimalist Prose',
    excerpt: 'Less is more: why cutting words can amplify your message. A guide to editing for maximum impact...',
    author: { id: 'a3', name: 'Elena Rodriguez', handle: 'elenawrites', avatarUrl: undefined },
    voiceProfile: 'minimal',
    readTime: 4,
    publishedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['minimalism', 'editing', 'style'],
    reactions: 156,
    bookmarked: false,
  },
  {
    id: '4',
    title: 'Storytelling Secrets from Canadian Literature',
    excerpt: 'What we can learn from the great Canadian storytellers. Techniques that bring narratives to life...',
    author: { id: 'a4', name: 'Michael Chen', handle: 'mchen', avatarUrl: undefined },
    voiceProfile: 'narrative',
    readTime: 7,
    publishedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['canada', 'storytelling', 'literature'],
    reactions: 203,
    bookmarked: false,
  },
  {
    id: '5',
    title: 'Building Emotional Resonance in Essays',
    excerpt: 'Connect with readers on a deeper level through strategic emotional cues and authentic vulnerability...',
    author: { id: 'a5', name: 'Amanda Foster', handle: 'amandaf', avatarUrl: undefined },
    voiceProfile: 'poetic',
    readTime: 6,
    publishedAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['essays', 'emotion', 'connection'],
    reactions: 98,
    bookmarked: false,
  },
  {
    id: '6',
    title: 'The Science of Reader Engagement',
    excerpt: 'Data-driven insights into what keeps readers hooked. Understanding attention patterns and flow...',
    author: { id: 'a6', name: 'David Park', handle: 'dpark', avatarUrl: undefined },
    voiceProfile: 'analytical',
    readTime: 10,
    publishedAt: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ['engagement', 'analytics', 'craft'],
    reactions: 145,
    bookmarked: true,
  },
];

const filters = [
  { id: 'trending', label: 'Trending', icon: <TrendingUp className="h-4 w-4" /> },
  { id: 'recent', label: 'Recent', icon: <Clock className="h-4 w-4" /> },
  { id: 'for-you', label: 'For You', icon: <Sparkles className="h-4 w-4" /> },
];

const tags = ['writing', 'craft', 'voice', 'canada', 'storytelling', 'essays', 'minimalism'];

export const Discover = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('trending');
  const [activeTag, setActiveTag] = useState<string | null>(null);

  // Use API when connected, fallback to mock
  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } = useDiscoverPosts(
    activeFilter,
    activeTag || undefined
  );

  const addBookmark = useAddBookmark();

  // Flatten pages or use mock data
  const posts = data?.pages.flatMap((page) => page.data) || mockPosts;
  const loading = isLoading && !posts.length;

  const handleBookmark = (postId: string) => {
    addBookmark.mutate({ postId });
  };

  const handlePostClick = (postId: string) => {
    navigate(`/reader/post/${postId}`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Discover</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Explore writing from voices that resonate with yours
        </p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search posts..."
            leftIcon={<Search className="h-5 w-5" />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {filters.map((filter) => (
            <Button
              key={filter.id}
              variant={activeFilter === filter.id ? 'primary' : 'outline'}
              size="sm"
              leftIcon={filter.icon}
              onClick={() => setActiveFilter(filter.id)}
            >
              {filter.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <button
            key={tag}
            onClick={() => setActiveTag(activeTag === tag ? null : tag)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              activeTag === tag
                ? 'bg-coral-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            #{tag}
          </button>
        ))}
      </div>

      {/* Posts Grid */}
      <PostList
        posts={posts}
        loading={loading}
        variant="card"
        onBookmark={handleBookmark}
        onPostClick={handlePostClick}
        emptyMessage="No posts found. Try adjusting your filters."
      />

      {/* Load More */}
      {hasNextPage && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={() => fetchNextPage()}
            isLoading={isFetchingNextPage}
          >
            Load More
          </Button>
        </div>
      )}
    </div>
  );
};
