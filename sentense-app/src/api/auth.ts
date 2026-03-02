import apiClient, { setAccessToken } from './client';
import { AuthResponse, LoginCredentials, SignupData, User } from '@/types';

export const authApi = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    
    // Store tokens
    setAccessToken(response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refresh_token', response.data.refreshToken);
    }
    
    return response.data;
  },

  /**
   * Sign up new user
   */
  async signup(data: SignupData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/signup', data);
    
    // Store tokens
    setAccessToken(response.data.token);
    if (response.data.refreshToken) {
      localStorage.setItem('refresh_token', response.data.refreshToken);
    }
    
    return response.data;
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      // Always clear local tokens
      setAccessToken(null);
      localStorage.removeItem('refresh_token');
    }
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/user/me');
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<{ token: string }> {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await apiClient.post<{ token: string }>('/auth/refresh', {
      refreshToken,
    });
    
    setAccessToken(response.data.token);
    return response.data;
  },

  /**
   * Request password reset
   */
  async forgotPassword(email: string): Promise<{ success: boolean }> {
    const response = await apiClient.post<{ success: boolean }>('/auth/forgot-password', {
      email,
    });
    return response.data;
  },

  /**
   * Reset password with token
   */
  async resetPassword(token: string, password: string): Promise<{ success: boolean }> {
    const response = await apiClient.post<{ success: boolean }>('/auth/reset-password', {
      token,
      password,
    });
    return response.data;
  },
};
