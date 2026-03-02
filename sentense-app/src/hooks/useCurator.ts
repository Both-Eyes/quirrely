import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { curatorApi, ReadingPath, CreatePathData, UpdatePathData } from '@/api';
import { useToast } from '@/components/ui/Toast';

// Query keys
export const curatorKeys = {
  all: ['curator'] as const,
  paths: () => [...curatorKeys.all, 'paths'] as const,
  path: (id: string) => [...curatorKeys.all, 'path', id] as const,
  progress: () => [...curatorKeys.all, 'progress'] as const,
  analytics: () => [...curatorKeys.all, 'analytics'] as const,
  pathAnalytics: (id: string) => [...curatorKeys.all, 'pathAnalytics', id] as const,
};

// Get all paths
export const useCuratorPaths = () => {
  return useQuery({
    queryKey: curatorKeys.paths(),
    queryFn: () => curatorApi.getPaths(),
  });
};

// Get single path
export const useCuratorPath = (id: string) => {
  return useQuery({
    queryKey: curatorKeys.path(id),
    queryFn: () => curatorApi.getPath(id),
    enabled: !!id,
  });
};

// Create path
export const useCreatePath = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { success } = useToast();

  return useMutation({
    mutationFn: (data: CreatePathData) => curatorApi.createPath(data),
    onSuccess: (path) => {
      queryClient.invalidateQueries({ queryKey: curatorKeys.paths() });
      success('Path created', 'Your reading path has been created');
      navigate(`/curator/paths/${path.id}/edit`);
    },
  });
};

// Update path
export const useUpdatePath = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdatePathData }) =>
      curatorApi.updatePath(id, data),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
      queryClient.invalidateQueries({ queryKey: curatorKeys.paths() });
      success('Path saved', 'Your changes have been saved');
    },
  });
};

// Delete path
export const useDeletePath = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => curatorApi.deletePath(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: curatorKeys.paths() });
      success('Path deleted', 'The reading path has been deleted');
      navigate('/curator/paths');
    },
  });
};

// Publish path
export const usePublishPath = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => curatorApi.publishPath(id),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
      queryClient.invalidateQueries({ queryKey: curatorKeys.paths() });
      success('Path published!', 'Your reading path is now live');
    },
  });
};

// Unpublish path
export const useUnpublishPath = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (id: string) => curatorApi.unpublishPath(id),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
      queryClient.invalidateQueries({ queryKey: curatorKeys.paths() });
      success('Path unpublished', 'Path moved to drafts');
    },
  });
};

// Get curator progress
export const useCuratorProgress = () => {
  return useQuery({
    queryKey: curatorKeys.progress(),
    queryFn: () => curatorApi.getProgress(),
  });
};

// Get path analytics
export const usePathAnalytics = (pathId: string) => {
  return useQuery({
    queryKey: curatorKeys.pathAnalytics(pathId),
    queryFn: () => curatorApi.getPathAnalytics(pathId),
    enabled: !!pathId,
  });
};

// Reorder posts
export const useReorderPosts = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ pathId, postIds }: { pathId: string; postIds: string[] }) =>
      curatorApi.reorderPosts(pathId, postIds),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
    },
  });
};

// Add post to path
export const useAddPostToPath = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: ({ pathId, postId, note }: { pathId: string; postId: string; note?: string }) =>
      curatorApi.addPostToPath(pathId, postId, note),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
      success('Post added', 'Post added to your path');
    },
  });
};

// Remove post from path
export const useRemovePostFromPath = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: ({ pathId, postId }: { pathId: string; postId: string }) =>
      curatorApi.removePostFromPath(pathId, postId),
    onSuccess: (path) => {
      queryClient.setQueryData(curatorKeys.path(path.id), path);
      success('Post removed', 'Post removed from your path');
    },
  });
};
