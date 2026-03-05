import apiClient from './client';

export interface AuthorityStatus {
  score: number;
  level: string;
  rank: number;
  percentile: number;
  tier: string;
  nextMilestone?: {
    name: string;
    threshold: number;
    progress: number;
  };
}

export interface AuthorityProgress {
  currentScore: number;
  previousScore: number;
  change: number;
  milestones: AuthorityMilestone[];
  history: { date: string; score: number }[];
}

export interface AuthorityMilestone {
  id: string;
  name: string;
  description: string;
  threshold: number;
  achieved: boolean;
  achievedAt?: string;
  reward?: string;
}

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  name: string;
  handle: string;
  avatarUrl?: string;
  country: string;
  countryFlag: string;
  score: number;
  tier: string;
  pathFollowers: number;
  isCurrentUser?: boolean;
}

export interface ImpactStats {
  totalReach: number;
  totalInfluence: number;
  writersInspired: number;
  pathsCompleted: number;
  topContributions: {
    type: 'path' | 'post' | 'feature';
    title: string;
    impact: number;
    date: string;
  }[];
  impactTrend: { date: string; impact: number }[];
  categoryBreakdown: { category: string; percentage: number }[];
}

export interface AuthorityBadge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  earnedAt: string;
}

export const authorityApi = {
  /**
   * Get authority status
   */
  async getStatus(): Promise<AuthorityStatus> {
    const response = await apiClient.get<AuthorityStatus>('/authority/status');
    return response.data;
  },

  /**
   * Get authority progress
   */
  async getProgress(): Promise<AuthorityProgress> {
    const response = await apiClient.get<AuthorityProgress>('/authority/progress');
    return response.data;
  },

  /**
   * Get leaderboard
   */
  async getLeaderboard(limit: number = 50, region?: string): Promise<LeaderboardEntry[]> {
    const response = await apiClient.get<LeaderboardEntry[]>('/authority/leaderboard', {
      params: { limit, region },
    });
    return response.data;
  },

  /**
   * Get impact stats
   */
  async getImpact(): Promise<ImpactStats> {
    const response = await apiClient.get<ImpactStats>('/authority/impact');
    return response.data;
  },

  /**
   * Get authority badges
   */
  async getBadges(): Promise<AuthorityBadge[]> {
    const response = await apiClient.get<AuthorityBadge[]>('/authority/badges');
    return response.data;
  },

  /**
   * Get user's authority rank among peers
   */
  async getPeerComparison(): Promise<{
    rank: number;
    totalInTier: number;
    percentile: number;
    nearbyUsers: LeaderboardEntry[];
  }> {
    const response = await apiClient.get('/authority/peers');
    return response.data;
  },
};
