import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Plus, Search, Clock, Edit, Trash2, Send } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useDrafts, useDeletePost, usePublishPost } from '@/hooks';
import { Card, CardContent, Button, Input, Badge, Skeleton } from '@/components/ui';
import { WritingPost } from '@/api';

// Mock data
const mockDrafts: WritingPost[] = [
  {
    id: 'd1',
    title: 'The Evolution of Digital Writing',
    content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
    excerpt: 'How technology is changing the way we write and express ourselves...',
    status: 'draft',
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    wordCount: 856,
    readTime: 4,
    tags: ['technology', 'writing'],
    reactions: 0,
    views: 0,
    comments: 0,
  },
  {
    id: 'd2',
    title: 'Embracing Vulnerability in Personal Essays',
    content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit...',
    excerpt: 'Why opening up can make your writing more powerful...',
    status: 'draft',
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    wordCount: 1245,
    readTime: 5,
    tags: ['essays', 'vulnerability'],
    reactions: 0,
    views: 0,
    comments: 0,
  },
  {
    id: 'd3',
    title: 'Untitled Draft',
    content: 'Starting to explore ideas about...',
    excerpt: '',
    status: 'draft',
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
    wordCount: 127,
    readTime: 1,
    tags: [],
    reactions: 0,
    views: 0,
    comments: 0,
  },
];

export const Drafts = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading } = useDrafts();
  const deletePost = useDeletePost();
  const publishPost = usePublishPost();

  const drafts = data?.data || mockDrafts;
  const loading = isLoading && !drafts.length;

  const filteredDrafts = drafts.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleEdit = (draftId: string) => {
    navigate(`/writer/editor/${draftId}`);
  };

  const handleDelete = (draftId: string) => {
    if (confirm('Are you sure you want to delete this draft?')) {
      deletePost.mutate(draftId);
    }
  };

  const handlePublish = (draftId: string) => {
    publishPost.mutate(draftId);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <FileText className="h-6 w-6 text-coral-500" />
            Drafts
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {drafts.length} {drafts.length === 1 ? 'draft' : 'drafts'} in progress
          </p>
        </div>
        <Button leftIcon={<Plus className="h-4 w-4" />} onClick={() => navigate('/writer/editor')}>
          New Draft
        </Button>
      </div>

      {/* Search */}
      <Input
        placeholder="Search drafts..."
        leftIcon={<Search className="h-5 w-5" />}
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      {/* Drafts List */}
      {loading ? (
        <div className="space-y-4">
          {Array(3).fill(0).map((_, i) => (
            <Card key={i}>
              <CardContent>
                <Skeleton variant="text" width="50%" height={24} className="mb-2" />
                <Skeleton variant="text" width="100%" height={16} className="mb-3" />
                <Skeleton variant="text" width="30%" height={14} />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredDrafts.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No drafts match your search' : 'No drafts yet'}
          </p>
          {!searchQuery && (
            <Button variant="outline" className="mt-4" onClick={() => navigate('/writer/editor')}>
              Start Writing
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDrafts.map((draft) => (
            <Card
              key={draft.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleEdit(draft.id)}
            >
              <CardContent>
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                        {draft.title || 'Untitled Draft'}
                      </h3>
                      <Badge variant="warning" size="sm">Draft</Badge>
                    </div>
                    {draft.excerpt && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2 mb-3">
                        {draft.excerpt}
                      </p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>{draft.wordCount.toLocaleString()} words</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        Last edited {formatDistanceToNow(new Date(draft.updatedAt), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="outline"
                      size="sm"
                      leftIcon={<Send className="h-4 w-4" />}
                      onClick={() => handlePublish(draft.id)}
                      isLoading={publishPost.isPending}
                    >
                      Publish
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(draft.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(draft.id)}
                      className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                {draft.tags.length > 0 && (
                  <div className="flex gap-1.5 mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                    {draft.tags.map((tag) => (
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
