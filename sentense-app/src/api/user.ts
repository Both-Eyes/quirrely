import apiClient from './client';
import { UserProfile, UserSettings, UserStats, VoiceProfile, Activity } from '@/types';

export const userApi = {
  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/user/profile');
    return response.data;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>('/user/me', data);
    return response.data;
  },

  /**
   * Get user settings
   */
  async getSettings(): Promise<UserSettings> {
    const response = await apiClient.get<UserSettings>('/user/settings');
    return response.data;
  },

  /**
   * Update user settings
   */
  async updateSettings(data: Partial<UserSettings>): Promise<UserSettings> {
    const response = await apiClient.put<UserSettings>('/user/settings', data);
    return response.data;
  },

  /**
   * Get user stats
   */
  async getStats(): Promise<UserStats> {
    const response = await apiClient.get<UserStats>('/user/stats');
    return response.data;
  },

  /**
   * Get voice profile
   */
  async getVoiceProfile(): Promise<VoiceProfile> {
    const response = await apiClient.get<VoiceProfile>('/analytics/voice');
    return response.data;
  },

  /**
   * Get recent activity
   */
  async getActivity(limit: number = 10): Promise<Activity[]> {
    const response = await apiClient.get<Activity[]>('/user/activity', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Upload avatar
   */
  async uploadAvatar(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await apiClient.post<{ url: string }>('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
