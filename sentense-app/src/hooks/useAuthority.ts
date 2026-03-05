import { useQuery } from '@tanstack/react-query';
import { authorityApi } from '@/api';

// Query keys
export const authorityKeys = {
  all: ['authority'] as const,
  status: () => [...authorityKeys.all, 'status'] as const,
  progress: () => [...authorityKeys.all, 'progress'] as const,
  leaderboard: (region?: string) => [...authorityKeys.all, 'leaderboard', region] as const,
  impact: () => [...authorityKeys.all, 'impact'] as const,
  badges: () => [...authorityKeys.all, 'badges'] as const,
  peers: () => [...authorityKeys.all, 'peers'] as const,
};

// Get authority status
export const useAuthorityStatus = () => {
  return useQuery({
    queryKey: authorityKeys.status(),
    queryFn: () => authorityApi.getStatus(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Get authority progress
export const useAuthorityProgress = () => {
  return useQuery({
    queryKey: authorityKeys.progress(),
    queryFn: () => authorityApi.getProgress(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Get leaderboard
export const useLeaderboard = (limit: number = 50, region?: string) => {
  return useQuery({
    queryKey: authorityKeys.leaderboard(region),
    queryFn: () => authorityApi.getLeaderboard(limit, region),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
};

// Get impact stats
export const useImpactStats = () => {
  return useQuery({
    queryKey: authorityKeys.impact(),
    queryFn: () => authorityApi.getImpact(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

// Get badges
export const useAuthorityBadges = () => {
  return useQuery({
    queryKey: authorityKeys.badges(),
    queryFn: () => authorityApi.getBadges(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};

// Get peer comparison
export const usePeerComparison = () => {
  return useQuery({
    queryKey: authorityKeys.peers(),
    queryFn: () => authorityApi.getPeerComparison(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};
