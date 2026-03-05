import apiClient from './client';
import { PaginatedResponse, PaginationParams } from '@/types';

export interface Post {
  id: string;
  title: string;
  excerpt: string;
  content?: string;
  author: {
    id: string;
    name: string;
    handle: string;
    avatarUrl?: string;
  };
  voiceProfile?: string;
  readTime: number;
  publishedAt: string;
  tags: string[];
  reactions: number;
  bookmarked?: boolean;
  read?: boolean;
}

export interface Bookmark {
  id: string;
  post: Post;
  createdAt: string;
  notes?: string;
}

export interface ReadHistory {
  id: string;
  post: Post;
  readAt: string;
  progress: number;
  duration: number;
}

export interface ReadingStreak {
  current: number;
  longest: number;
  lastReadDate: string;
  thisWeek: boolean[];
  thisMonth: number;
}

export const readingApi = {
  /**
   * Discover posts
   */
  async discover(params?: PaginationParams & { filter?: string; tag?: string }): Promise<PaginatedResponse<Post>> {
    const response = await apiClient.get<PaginatedResponse<Post>>('/reading/discover', { params });
    return response.data;
  },

  /**
   * Get single post
   */
  async getPost(id: string): Promise<Post> {
    const response = await apiClient.get<Post>(`/reading/posts/${id}`);
    return response.data;
  },

  /**
   * Get bookmarks
   */
  async getBookmarks(params?: PaginationParams): Promise<PaginatedResponse<Bookmark>> {
    const response = await apiClient.get<PaginatedResponse<Bookmark>>('/reading/bookmarks', { params });
    return response.data;
  },

  /**
   * Add bookmark
   */
  async addBookmark(postId: string, notes?: string): Promise<Bookmark> {
    const response = await apiClient.post<Bookmark>('/reading/bookmarks', { postId, notes });
    return response.data;
  },

  /**
   * Remove bookmark
   */
  async removeBookmark(bookmarkId: string): Promise<void> {
    await apiClient.delete(`/reading/bookmarks/${bookmarkId}`);
  },

  /**
   * Get reading history
   */
  async getHistory(params?: PaginationParams): Promise<PaginatedResponse<ReadHistory>> {
    const response = await apiClient.get<PaginatedResponse<ReadHistory>>('/reading/history', { params });
    return response.data;
  },

  /**
   * Track reading progress
   */
  async trackRead(postId: string, duration: number, progress: number): Promise<void> {
    await apiClient.post('/reading/track', { postId, duration, progress });
  },

  /**
   * Get reading streak
   */
  async getStreak(): Promise<ReadingStreak> {
    const response = await apiClient.get<ReadingStreak>('/reading/streak');
    return response.data;
  },
};
