import apiClient from './client';
import { PaginatedResponse, PaginationParams } from '@/types';

export type PostStatus = 'draft' | 'published' | 'archived';

export interface WritingPost {
  id: string;
  title: string;
  content: string;
  excerpt?: string;
  status: PostStatus;
  publishedAt?: string;
  createdAt: string;
  updatedAt: string;
  wordCount: number;
  readTime: number;
  tags: string[];
  reactions: number;
  views: number;
  comments: number;
}

export interface WritingAnalytics {
  totalViews: number;
  totalReactions: number;
  totalComments: number;
  avgReadTime: number;
  topPosts: WritingPost[];
  viewsTrend: { date: string; views: number }[];
}

export interface CreatePostData {
  title: string;
  content: string;
  tags?: string[];
  status?: PostStatus;
}

export interface UpdatePostData {
  title?: string;
  content?: string;
  tags?: string[];
  status?: PostStatus;
}

export const writingApi = {
  /**
   * Get all posts (published)
   */
  async getPosts(params?: PaginationParams): Promise<PaginatedResponse<WritingPost>> {
    const response = await apiClient.get<PaginatedResponse<WritingPost>>('/writing/posts', { params });
    return response.data;
  },

  /**
   * Get single post
   */
  async getPost(id: string): Promise<WritingPost> {
    const response = await apiClient.get<WritingPost>(`/writing/posts/${id}`);
    return response.data;
  },

  /**
   * Create new post
   */
  async createPost(data: CreatePostData): Promise<WritingPost> {
    const response = await apiClient.post<WritingPost>('/writing/posts', data);
    return response.data;
  },

  /**
   * Update post
   */
  async updatePost(id: string, data: UpdatePostData): Promise<WritingPost> {
    const response = await apiClient.put<WritingPost>(`/writing/posts/${id}`, data);
    return response.data;
  },

  /**
   * Delete post
   */
  async deletePost(id: string): Promise<void> {
    await apiClient.delete(`/writing/posts/${id}`);
  },

  /**
   * Get drafts
   */
  async getDrafts(params?: PaginationParams): Promise<PaginatedResponse<WritingPost>> {
    const response = await apiClient.get<PaginatedResponse<WritingPost>>('/writing/drafts', { params });
    return response.data;
  },

  /**
   * Publish a draft
   */
  async publish(id: string): Promise<WritingPost> {
    const response = await apiClient.post<WritingPost>(`/writing/posts/${id}/publish`);
    return response.data;
  },

  /**
   * Unpublish (move to draft)
   */
  async unpublish(id: string): Promise<WritingPost> {
    const response = await apiClient.post<WritingPost>(`/writing/posts/${id}/unpublish`);
    return response.data;
  },

  /**
   * Archive post
   */
  async archive(id: string): Promise<WritingPost> {
    const response = await apiClient.post<WritingPost>(`/writing/posts/${id}/archive`);
    return response.data;
  },

  /**
   * Get writing analytics
   */
  async getAnalytics(): Promise<WritingAnalytics> {
    const response = await apiClient.get<WritingAnalytics>('/writing/analytics');
    return response.data;
  },

  /**
   * Analyze writing voice
   */
  async analyzeVoice(content: string): Promise<{ tokens: string[]; profile: string; confidence: number }> {
    const response = await apiClient.post('/writing/analyze', { content });
    return response.data;
  },
};
