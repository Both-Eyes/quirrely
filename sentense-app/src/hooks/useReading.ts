import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { readingApi, Post, Bookmark, ReadHistory, ReadingStreak } from '@/api';
import { useToast } from '@/components/ui/Toast';
import { PaginationParams } from '@/types';

// Query keys
export const readingKeys = {
  all: ['reading'] as const,
  discover: (filters?: Record<string, unknown>) => [...readingKeys.all, 'discover', filters] as const,
  post: (id: string) => [...readingKeys.all, 'post', id] as const,
  bookmarks: () => [...readingKeys.all, 'bookmarks'] as const,
  history: () => [...readingKeys.all, 'history'] as const,
  streak: () => [...readingKeys.all, 'streak'] as const,
};

// Discover posts with infinite scroll
export const useDiscoverPosts = (filter?: string, tag?: string) => {
  return useInfiniteQuery({
    queryKey: readingKeys.discover({ filter, tag }),
    queryFn: ({ pageParam = 1 }) => readingApi.discover({ page: pageParam, limit: 10, filter, tag }),
    getNextPageParam: (lastPage) => lastPage.hasMore ? lastPage.page + 1 : undefined,
    initialPageParam: 1,
  });
};

// Get single post
export const usePost = (id: string) => {
  return useQuery({
    queryKey: readingKeys.post(id),
    queryFn: () => readingApi.getPost(id),
    enabled: !!id,
  });
};

// Get bookmarks
export const useBookmarks = () => {
  return useQuery({
    queryKey: readingKeys.bookmarks(),
    queryFn: () => readingApi.getBookmarks(),
  });
};

// Add bookmark
export const useAddBookmark = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: ({ postId, notes }: { postId: string; notes?: string }) => 
      readingApi.addBookmark(postId, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: readingKeys.bookmarks() });
      success('Bookmarked', 'Post added to your bookmarks');
    },
  });
};

// Remove bookmark
export const useRemoveBookmark = () => {
  const queryClient = useQueryClient();
  const { success } = useToast();

  return useMutation({
    mutationFn: (bookmarkId: string) => readingApi.removeBookmark(bookmarkId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: readingKeys.bookmarks() });
      success('Removed', 'Post removed from bookmarks');
    },
  });
};

// Get reading history
export const useReadingHistory = () => {
  return useQuery({
    queryKey: readingKeys.history(),
    queryFn: () => readingApi.getHistory(),
  });
};

// Track reading
export const useTrackRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ postId, duration, progress }: { postId: string; duration: number; progress: number }) =>
      readingApi.trackRead(postId, duration, progress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: readingKeys.history() });
      queryClient.invalidateQueries({ queryKey: readingKeys.streak() });
    },
  });
};

// Get reading streak
export const useReadingStreak = () => {
  return useQuery({
    queryKey: readingKeys.streak(),
    queryFn: () => readingApi.getStreak(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
