import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { ApiError } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance with credentials for httpOnly cookies
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
  withCredentials: true, // Include httpOnly cookies in requests
});

// ═══════════════════════════════════════════════════════════════════════════
// NOTE: Token management moved to httpOnly cookies
// ═══════════════════════════════════════════════════════════════════════════
// 
// Tokens are now managed server-side via httpOnly cookies:
// - Set by server on login/signup/refresh
// - Automatically included in requests via withCredentials: true
// - Not accessible via JavaScript (XSS protection)
// - Cleared by server on logout
//
// Legacy localStorage functions kept for backwards compatibility during migration

let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  // Legacy: kept for migration period
  // New auth flow uses httpOnly cookies set by server
  accessToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
};

export const getAccessToken = (): string | null => {
  // Legacy: returns null in new cookie-based flow
  if (accessToken) return accessToken;
  return localStorage.getItem('auth_token');
};

export const clearTokens = () => {
  accessToken = null;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('refresh_token');
  // Note: httpOnly cookies are cleared server-side via /auth/logout
};

// Check if we're using the new cookie-based auth
export const isUsingCookieAuth = (): boolean => {
  // If no localStorage token but user is authenticated, we're using cookies
  return !localStorage.getItem('auth_token');
};

// Request interceptor - add auth header (legacy) or rely on cookies (new)
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Only add Authorization header if we have a legacy token
    // New flow relies on httpOnly cookies sent automatically
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config;
    
    // Handle 401 - try to refresh token
    if (error.response?.status === 401 && originalRequest) {
      // Check for X-Token-Expired header (new cookie flow)
      const tokenExpired = error.response.headers['x-token-expired'] === 'true';
      
      if (tokenExpired || isUsingCookieAuth()) {
        // New flow: call refresh endpoint (cookies sent automatically)
        try {
          await axios.post(
            `${API_BASE_URL}/v2/auth/refresh`,
            {},
            { withCredentials: true }
          );
          
          // Retry original request (new cookies will be sent)
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - redirect to login
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // Legacy flow: use refresh token from localStorage
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          try {
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refreshToken,
            });
            
            const { token } = response.data;
            setAccessToken(token);
            
            // Retry original request
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          } catch (refreshError) {
            // Refresh failed - clear tokens and redirect to login
            clearTokens();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        } else {
          // No refresh token - redirect to login
          clearTokens();
          window.location.href = '/login';
        }
      }
    }
    
    // Handle rate limiting
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      console.warn(`Rate limited. Retry after ${retryAfter} seconds.`);
    }
    
    // Format error response
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'An error occurred',
      code: error.response?.data?.code,
      status: error.response?.status || 500,
      details: error.response?.data?.details,
    };
    
    return Promise.reject(apiError);
  }
);

export default apiClient;
