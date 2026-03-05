import apiClient from './client';

export interface SafetyCheckResult {
  safe: boolean;
  score: number;
  flags: SafetyFlag[];
  suggestions?: string[];
}

export interface SafetyFlag {
  type: 'tone' | 'content' | 'language' | 'safety';
  severity: 'low' | 'medium' | 'high';
  message: string;
  span?: { start: number; end: number };
}

export interface SafetyStatus {
  safetyScore: number;
  trustLevel: 'new' | 'standard' | 'trusted' | 'authority';
  violations: number;
  lastCheck: string;
}

export const safetyApi = {
  /**
   * Check content for safety
   */
  async checkContent(content: string): Promise<SafetyCheckResult> {
    const response = await apiClient.post<SafetyCheckResult>('/safety/check', { content });
    return response.data;
  },

  /**
   * Get user's safety status
   */
  async getStatus(): Promise<SafetyStatus> {
    const response = await apiClient.get<SafetyStatus>('/safety/status');
    return response.data;
  },

  /**
   * Appeal a violation
   */
  async appeal(violationId: string, reason: string): Promise<{ success: boolean }> {
    const response = await apiClient.post('/safety/appeal', { violationId, reason });
    return response.data;
  },
};
