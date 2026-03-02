import apiClient from './client';
import { PaginatedResponse, PaginationParams } from '@/types';
import { Post } from './reading';

export interface ReadingPath {
  id: string;
  title: string;
  description: string;
  icon?: string;
  status: 'draft' | 'published';
  posts: PathPost[];
  followers: number;
  completions: number;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

export interface PathPost {
  id: string;
  postId: string;
  position: number;
  note?: string;
  post: Post;
}

export interface CuratorProgress {
  level: number;
  currentXp: number;
  nextLevelXp: number;
  totalPaths: number;
  totalFollowers: number;
  badges: CuratorBadge[];
}

export interface CuratorBadge {
  id: string;
  name: string;
  description: string;
  icon: string;
  earnedAt: string;
}

export interface PathAnalytics {
  pathId: string;
  views: number;
  followers: number;
  completions: number;
  avgCompletionRate: number;
  viewsTrend: { date: string; views: number }[];
  topPosts: { postId: string; title: string; reads: number }[];
}

export interface CreatePathData {
  title: string;
  description: string;
  icon?: string;
  posts?: { postId: string; note?: string }[];
}

export interface UpdatePathData {
  title?: string;
  description?: string;
  icon?: string;
  posts?: { postId: string; note?: string; position: number }[];
}

export const curatorApi = {
  /**
   * Get all paths
   */
  async getPaths(params?: PaginationParams): Promise<PaginatedResponse<ReadingPath>> {
    const response = await apiClient.get<PaginatedResponse<ReadingPath>>('/curator/paths', { params });
    return response.data;
  },

  /**
   * Get single path
   */
  async getPath(id: string): Promise<ReadingPath> {
    const response = await apiClient.get<ReadingPath>(`/curator/paths/${id}`);
    return response.data;
  },

  /**
   * Create new path
   */
  async createPath(data: CreatePathData): Promise<ReadingPath> {
    const response = await apiClient.post<ReadingPath>('/curator/paths', data);
    return response.data;
  },

  /**
   * Update path
   */
  async updatePath(id: string, data: UpdatePathData): Promise<ReadingPath> {
    const response = await apiClient.put<ReadingPath>(`/curator/paths/${id}`, data);
    return response.data;
  },

  /**
   * Delete path
   */
  async deletePath(id: string): Promise<void> {
    await apiClient.delete(`/curator/paths/${id}`);
  },

  /**
   * Publish path
   */
  async publishPath(id: string): Promise<ReadingPath> {
    const response = await apiClient.post<ReadingPath>(`/curator/paths/${id}/publish`);
    return response.data;
  },

  /**
   * Unpublish path
   */
  async unpublishPath(id: string): Promise<ReadingPath> {
    const response = await apiClient.post<ReadingPath>(`/curator/paths/${id}/unpublish`);
    return response.data;
  },

  /**
   * Get curator progress
   */
  async getProgress(): Promise<CuratorProgress> {
    const response = await apiClient.get<CuratorProgress>('/curator/progress');
    return response.data;
  },

  /**
   * Get path analytics
   */
  async getPathAnalytics(pathId: string): Promise<PathAnalytics> {
    const response = await apiClient.get<PathAnalytics>(`/curator/paths/${pathId}/analytics`);
    return response.data;
  },

  /**
   * Get overall curator analytics
   */
  async getAnalytics(): Promise<{ totalFollowers: number; totalViews: number; topPaths: ReadingPath[] }> {
    const response = await apiClient.get('/curator/analytics');
    return response.data;
  },

  /**
   * Reorder posts in a path
   */
  async reorderPosts(pathId: string, postIds: string[]): Promise<ReadingPath> {
    const response = await apiClient.put<ReadingPath>(`/curator/paths/${pathId}/reorder`, { postIds });
    return response.data;
  },

  /**
   * Add post to path
   */
  async addPostToPath(pathId: string, postId: string, note?: string): Promise<ReadingPath> {
    const response = await apiClient.post<ReadingPath>(`/curator/paths/${pathId}/posts`, { postId, note });
    return response.data;
  },

  /**
   * Remove post from path
   */
  async removePostFromPath(pathId: string, postId: string): Promise<ReadingPath> {
    const response = await apiClient.delete<ReadingPath>(`/curator/paths/${pathId}/posts/${postId}`);
    return response.data;
  },
};
