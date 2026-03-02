import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { writingApi, WritingPost, CreatePostData, UpdatePostData } from '@/api';
import { useToast } from '@/components/ui/Toast';

// Query keys
export const writingKeys = {
  all: ['writing'] as const,
  posts: () => [...writingKeys.all, 'posts'] as const,
  post: (id: string) => [...writingKeys.all, 'post', id] as const,
  drafts: () => [...writingKeys.all, 'drafts'] as const,
  analytics: () => [...writingKeys.all, 'analytics'] as const,
};

// Get published posts
export const useWritingPosts = () => {
  return useQuery({
    queryKey: writingKeys.posts(),
    queryFn: () => writingApi.getPosts(),
  });
};

// Get single post
export const useWritingPost = (id: string) => {
  return useQuery({
    queryKey: writingKeys.post(id),
    queryFn: () => writingApi.getPost(id),
    enabled: !!id,
  });
};

// Get drafts
export const useDrafts = () => {
  return useQuery({
    queryKey: writingKeys.drafts(),
    queryFn: () => writingApi.getDrafts(),
  });
};

// Create post
export const useCreatePost = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { success } = useToast();

  return useMutation({
    mutationFn: (data: CreatePostData) => writingApi.createPost(data),
    onSuccess: (post) => {
      queryClient.invalidateQueries({ queryKey: writingKeys.all });
      success('Post created', post.status === 'published' ? 'Your post is now live!' : 'Draft saved');
      navigate(`/writer/editor/${post.id}`);
    },
  });
};

// Update post
export const useUpdatePost = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdatePostData }) => 
      writingApi.updatePost(id, data),
    onSuccess: (post) => {
      queryClient.setQueryData(writingKeys.post(post.id), post);
      queryClient.invalidateQueries({ queryKey: writingKeys.posts() });
      queryClient.invalidateQueries({ queryKey: writingKeys.drafts() });
      success('Saved', 'Your changes have been saved');
    },
  });
};

// Delete post
export const useDeletePost = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => writingApi.deletePost(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: writingKeys.all });
      success('Deleted', 'Post has been deleted');
      navigate('/writer/posts');
    },
  });
};

// Publish post
export const usePublishPost = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => writingApi.publish(id),
    onSuccess: (post) => {
      queryClient.setQueryData(writingKeys.post(post.id), post);
      queryClient.invalidateQueries({ queryKey: writingKeys.posts() });
      queryClient.invalidateQueries({ queryKey: writingKeys.drafts() });
      success('Published!', 'Your post is now live');
    },
  });
};

// Unpublish post
export const useUnpublishPost = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => writingApi.unpublish(id),
    onSuccess: (post) => {
      queryClient.setQueryData(writingKeys.post(post.id), post);
      queryClient.invalidateQueries({ queryKey: writingKeys.posts() });
      queryClient.invalidateQueries({ queryKey: writingKeys.drafts() });
      success('Unpublished', 'Post moved to drafts');
    },
  });
};

// Archive post
export const useArchivePost = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => writingApi.archive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: writingKeys.all });
      success('Archived', 'Post has been archived');
    },
  });
};

// Get analytics
export const useWritingAnalytics = () => {
  return useQuery({
    queryKey: writingKeys.analytics(),
    queryFn: () => writingApi.getAnalytics(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Analyze writing
export const useAnalyzeWriting = () => {
  return useMutation({
    mutationFn: (content: string) => writingApi.analyzeVoice(content),
  });
};
