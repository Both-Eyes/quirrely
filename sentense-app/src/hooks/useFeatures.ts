/**
 * useFeatures Hook
 * 
 * Fetches and caches user's available features from the backend.
 * Provides a single source of truth for feature gating in the frontend.
 * 
 * Usage:
 *   const { features, hasFeature, isLoading } = useFeatures();
 *   
 *   if (hasFeature('analytics')) {
 *     // Show analytics
 *   }
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';

// ═══════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════

export interface FeatureStatus {
  key: string;
  name: string;
  description: string;
  enabled: boolean;
  reason: string;
}

export interface UsageLimits {
  daily_analyses: number;
  daily_analyses_used: number;
  daily_analyses_remaining: number;
  resets_at: string;
}

export interface UpgradeSuggestion {
  type: string;
  title: string;
  description: string;
  cta: string;
}

export interface FeaturesResponse {
  user_id: string;
  user_tier: string;
  user_tier_level: number;
  user_addons: string[];
  track: 'writer' | 'curator' | 'both' | 'none';
  features: Record<string, boolean>;
  feature_details: FeatureStatus[];
  limits: UsageLimits;
  available_sections: string[];
  upgrade_suggestions: UpgradeSuggestion[];
  cached_at: string;
  cache_ttl_seconds: number;
}

export interface FeatureCheckResponse {
  feature: string;
  enabled: boolean;
  reason: string;
  upgrade_path?: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════════════════════════════════

const featuresApi = {
  /**
   * Get all features for current user
   */
  async getAll(): Promise<FeaturesResponse> {
    const response = await apiClient.get<FeaturesResponse>('/v2/features');
    return response.data;
  },

  /**
   * Check a specific feature
   */
  async check(featureKey: string): Promise<FeatureCheckResponse> {
    const response = await apiClient.get<FeatureCheckResponse>(
      `/v2/features/check/${featureKey}`
    );
    return response.data;
  },

  /**
   * Get usage limits
   */
  async getLimits(): Promise<UsageLimits> {
    const response = await apiClient.get<UsageLimits>('/v2/features/limits');
    return response.data;
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// QUERY KEYS
// ═══════════════════════════════════════════════════════════════════════════

export const featureKeys = {
  all: ['features'] as const,
  list: () => [...featureKeys.all, 'list'] as const,
  check: (key: string) => [...featureKeys.all, 'check', key] as const,
  limits: () => [...featureKeys.all, 'limits'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// HOOKS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Main hook for feature access
 */
export const useFeatures = () => {
  const query = useQuery({
    queryKey: featureKeys.list(),
    queryFn: featuresApi.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes (matches backend cache_ttl)
    gcTime: 10 * 60 * 1000, // 10 minutes
  });

  /**
   * Check if user has access to a feature
   */
  const hasFeature = (featureKey: string): boolean => {
    return query.data?.features[featureKey] ?? false;
  };

  /**
   * Check if user has access to any of the given features
   */
  const hasAnyFeature = (featureKeys: string[]): boolean => {
    return featureKeys.some((key) => hasFeature(key));
  };

  /**
   * Check if user has access to all of the given features
   */
  const hasAllFeatures = (featureKeys: string[]): boolean => {
    return featureKeys.every((key) => hasFeature(key));
  };

  /**
   * Get feature details
   */
  const getFeatureDetails = (featureKey: string): FeatureStatus | undefined => {
    return query.data?.feature_details.find((f) => f.key === featureKey);
  };

  /**
   * Check if a section is available
   */
  const hasSection = (section: string): boolean => {
    return query.data?.available_sections.includes(section) ?? false;
  };

  return {
    // Query state
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,

    // User info
    tier: query.data?.user_tier,
    tierLevel: query.data?.user_tier_level,
    addons: query.data?.user_addons ?? [],
    track: query.data?.track,

    // Features
    features: query.data?.features ?? {},
    featureDetails: query.data?.feature_details ?? [],
    hasFeature,
    hasAnyFeature,
    hasAllFeatures,
    getFeatureDetails,

    // Sections
    availableSections: query.data?.available_sections ?? [],
    hasSection,

    // Limits
    limits: query.data?.limits,

    // Upgrades
    upgradeSuggestions: query.data?.upgrade_suggestions ?? [],

    // Refresh
    refetch: query.refetch,
  };
};

/**
 * Hook to check a specific feature with real-time validation
 */
export const useFeatureCheck = (featureKey: string) => {
  return useQuery({
    queryKey: featureKeys.check(featureKey),
    queryFn: () => featuresApi.check(featureKey),
    staleTime: 60 * 1000, // 1 minute
  });
};

/**
 * Hook for usage limits (refreshes more frequently)
 */
export const useUsageLimits = () => {
  return useQuery({
    queryKey: featureKeys.limits(),
    queryFn: featuresApi.getLimits,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
};

/**
 * Hook to invalidate feature cache (call after upgrade/downgrade)
 */
export const useInvalidateFeatures = () => {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: featureKeys.all });
  };
};

// ═══════════════════════════════════════════════════════════════════════════
// UTILITY: Feature Guard Component
// ═══════════════════════════════════════════════════════════════════════════

import { ReactNode } from 'react';

interface FeatureGateProps {
  feature: string;
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Component to conditionally render based on feature access
 * 
 * Usage:
 *   <FeatureGate feature="analytics" fallback={<UpgradePrompt />}>
 *     <AnalyticsDashboard />
 *   </FeatureGate>
 */
export const FeatureGate = ({ feature, children, fallback = null }: FeatureGateProps) => {
  const { hasFeature, isLoading } = useFeatures();

  if (isLoading) {
    return null; // Or a loading skeleton
  }

  if (hasFeature(feature)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export default useFeatures;
