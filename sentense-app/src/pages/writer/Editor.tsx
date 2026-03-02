import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Save, Send, ArrowLeft, Eye, EyeOff, Bold, Italic, 
  List, ListOrdered, Quote, Link, Image, Hash, Sparkles 
} from 'lucide-react';
import { useWritingPost, useCreatePost, useUpdatePost, usePublishPost, useAnalyzeWriting } from '@/hooks';
import { Card, Button, Input, Badge, Skeleton } from '@/components/ui';
import { useToast } from '@/components/ui/Toast';

export const Editor = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success } = useToast();
  
  const isEditing = !!id;
  
  const { data: existingPost, isLoading: postLoading } = useWritingPost(id || '');
  const createPost = useCreatePost();
  const updatePost = useUpdatePost();
  const publishPost = usePublishPost();
  const analyzeWriting = useAnalyzeWriting();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [voiceAnalysis, setVoiceAnalysis] = useState<{ tokens: string[]; profile: string; confidence: number } | null>(null);

  // Load existing post data
  useEffect(() => {
    if (existingPost) {
      setTitle(existingPost.title);
      setContent(existingPost.content);
      setTags(existingPost.tags);
    }
  }, [existingPost]);

  // Auto-save every 30 seconds
  useEffect(() => {
    if (!title && !content) return;
    
    const timer = setInterval(() => {
      handleSave(true);
    }, 30000);

    return () => clearInterval(timer);
  }, [title, content, tags]);

  const handleSave = async (auto = false) => {
    if (!title.trim() && !content.trim()) return;
    
    setIsSaving(true);
    try {
      if (isEditing && id) {
        await updatePost.mutateAsync({
          id,
          data: { title, content, tags },
        });
      } else {
        await createPost.mutateAsync({
          title: title || 'Untitled Draft',
          content,
          tags,
          status: 'draft',
        });
      }
      setLastSaved(new Date());
      if (!auto) {
        success('Saved', 'Your draft has been saved');
      }
    } catch (error) {
      // Error handled by mutation
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!title.trim()) {
      return;
    }
    
    if (isEditing && id) {
      await updatePost.mutateAsync({ id, data: { title, content, tags } });
      await publishPost.mutateAsync(id);
    } else {
      await createPost.mutateAsync({
        title,
        content,
        tags,
        status: 'published',
      });
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim().toLowerCase())) {
      setTags([...tags, tagInput.trim().toLowerCase()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleAnalyze = async () => {
    if (content.length < 100) {
      return;
    }
    
    try {
      const result = await analyzeWriting.mutateAsync(content);
      setVoiceAnalysis(result);
    } catch (error) {
      // Error handled by mutation
    }
  };

  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;
  const readTime = Math.max(1, Math.ceil(wordCount / 200));

  if (postLoading && isEditing) {
    return (
      <div className="space-y-6">
        <Skeleton variant="text" width="30%" height={40} />
        <Skeleton variant="rectangular" height={400} className="rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              {isEditing ? 'Edit Post' : 'New Post'}
            </h1>
            {lastSaved && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Last saved {lastSaved.toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            onClick={() => setShowPreview(!showPreview)}
            leftIcon={showPreview ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          >
            {showPreview ? 'Edit' : 'Preview'}
          </Button>
          <Button
            variant="outline"
            onClick={() => handleSave()}
            isLoading={isSaving}
            leftIcon={<Save className="h-4 w-4" />}
          >
            Save Draft
          </Button>
          <Button
            onClick={handlePublish}
            isLoading={publishPost.isPending || createPost.isPending}
            leftIcon={<Send className="h-4 w-4" />}
            disabled={!title.trim()}
          >
            Publish
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Editor */}
        <div className="lg:col-span-3 space-y-4">
          {/* Title */}
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post title..."
            className="w-full text-3xl font-bold bg-transparent border-none outline-none text-gray-900 dark:text-white placeholder:text-gray-400"
          />

          {/* Toolbar */}
          <div className="flex items-center gap-1 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <Bold className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <Italic className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <List className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <ListOrdered className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <Quote className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <Link className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
            <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
              <Image className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            </button>
          </div>

          {/* Content Area */}
          {showPreview ? (
            <Card className="min-h-[400px] p-6">
              <h1 className="text-2xl font-bold mb-4">{title || 'Untitled'}</h1>
              <div className="prose dark:prose-invert max-w-none">
                {content.split('\n').map((paragraph, i) => (
                  <p key={i}>{paragraph}</p>
                ))}
              </div>
            </Card>
          ) : (
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Start writing your story..."
              className="w-full min-h-[400px] p-4 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl resize-none outline-none focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 text-gray-900 dark:text-white placeholder:text-gray-400"
            />
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Stats */}
          <Card padding="md">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Words</span>
                <span className="font-medium text-gray-900 dark:text-white">{wordCount.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Read time</span>
                <span className="font-medium text-gray-900 dark:text-white">{readTime} min</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Characters</span>
                <span className="font-medium text-gray-900 dark:text-white">{content.length.toLocaleString()}</span>
              </div>
            </div>
          </Card>

          {/* Tags */}
          <Card padding="md">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Tags</h3>
            <div className="flex gap-2 mb-3">
              <Input
                placeholder="Add tag..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                leftIcon={<Hash className="h-4 w-4" />}
              />
              <Button variant="outline" size="sm" onClick={handleAddTag}>
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="primary"
                  className="cursor-pointer"
                  onClick={() => handleRemoveTag(tag)}
                >
                  #{tag} ×
                </Badge>
              ))}
              {tags.length === 0 && (
                <p className="text-sm text-gray-500 dark:text-gray-400">No tags added</p>
              )}
            </div>
          </Card>

          {/* Voice Analysis */}
          <Card padding="md">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 dark:text-white">Voice Analysis</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleAnalyze}
                isLoading={analyzeWriting.isPending}
                disabled={content.length < 100}
                leftIcon={<Sparkles className="h-4 w-4" />}
              >
                Analyze
              </Button>
            </div>
            {voiceAnalysis ? (
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Profile</p>
                  <p className="font-medium text-coral-500 capitalize">{voiceAnalysis.profile}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Tokens</p>
                  <div className="flex flex-wrap gap-1">
                    {voiceAnalysis.tokens.map((token) => (
                      <Badge key={token} variant="default" size="sm">{token}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Confidence</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {Math.round(voiceAnalysis.confidence * 100)}%
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {content.length < 100
                  ? 'Write at least 100 characters to analyze your voice'
                  : 'Click Analyze to see your writing voice'}
              </p>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
