/**
 * QUIRRELY CONVERSION TRACKER v1.0
 * Track conversion funnel events from frontend.
 * 
 * This module provides:
 * - Standardized conversion event tracking
 * - Automatic context enrichment
 * - Revenue attribution
 * - Upgrade prompt tracking
 * 
 * Usage:
 *   import { ConversionTracker } from '@/lib/conversion-tracker';
 *   
 *   // Track trial start
 *   ConversionTracker.trackTrialStarted();
 *   
 *   // Track upgrade prompt
 *   ConversionTracker.trackUpgradePrompt('limit_reached', 'clicked');
 */

import { MetaEvents } from './meta-events';

// ═══════════════════════════════════════════════════════════════════════════
// CONVERSION EVENT TYPES
// ═══════════════════════════════════════════════════════════════════════════

export const ConversionEvent = {
  // Signup funnel
  SIGNUP_STARTED: 'signup.started',
  SIGNUP_COMPLETED: 'signup.completed',
  SIGNUP_ABANDONED: 'signup.abandoned',
  
  // Trial funnel
  TRIAL_STARTED: 'trial.started',
  TRIAL_EXPIRING: 'trial.expiring',
  TRIAL_EXPIRED: 'trial.expired',
  TRIAL_CONVERTED: 'trial.converted',
  
  // Subscription funnel
  SUBSCRIPTION_CREATED: 'subscription.created',
  SUBSCRIPTION_CANCELLED: 'subscription.cancelled',
  
  // Addon funnel
  ADDON_TRIAL_STARTED: 'addon.trial.started',
  ADDON_PURCHASED: 'addon.purchased',
  ADDON_CANCELLED: 'addon.cancelled',
  
  // Tier progression
  TIER_UPGRADED: 'tier.upgraded',
  FEATURED_ACHIEVED: 'tier.featured.achieved',
  AUTHORITY_ACHIEVED: 'tier.authority.achieved',
  
  // Engagement
  ANALYSIS_COMPLETED: 'engagement.analysis.completed',
  ANALYSIS_LIMIT_REACHED: 'engagement.analysis.limit_reached',
  FEATURE_GATED_CLICK: 'engagement.feature.gated_click',
  
  // Upgrade prompts
  UPGRADE_PROMPT_SHOWN: 'prompt.upgrade.shown',
  UPGRADE_PROMPT_CLICKED: 'prompt.upgrade.clicked',
  UPGRADE_PROMPT_DISMISSED: 'prompt.upgrade.dismissed',
} as const;

export type ConversionEventType = typeof ConversionEvent[keyof typeof ConversionEvent];

// ═══════════════════════════════════════════════════════════════════════════
// CONVERSION TRACKER
// ═══════════════════════════════════════════════════════════════════════════

interface TrackOptions {
  revenue?: number;
  metadata?: Record<string, unknown>;
  source?: string;
}

export const ConversionTracker = {
  /**
   * Track any conversion event
   */
  track(event: ConversionEventType, options: TrackOptions = {}): void {
    // Send to backend
    fetch('/api/v2/conversions/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        event,
        metadata: options.metadata || {},
        source: options.source,
      }),
    }).catch(console.error);
    
    // Also emit to Meta events
    MetaEvents.emit('conversion', {
      event,
      ...options.metadata,
      revenue: options.revenue,
      source: options.source,
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Signup Events
  // ─────────────────────────────────────────────────────────────────────────

  trackSignupStarted(source?: string): void {
    this.track(ConversionEvent.SIGNUP_STARTED, { source });
  },

  trackSignupCompleted(source?: string): void {
    this.track(ConversionEvent.SIGNUP_COMPLETED, { source });
  },

  trackSignupAbandoned(step: string): void {
    this.track(ConversionEvent.SIGNUP_ABANDONED, {
      metadata: { abandoned_at_step: step },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Trial Events
  // ─────────────────────────────────────────────────────────────────────────

  trackTrialStarted(): void {
    this.track(ConversionEvent.TRIAL_STARTED);
  },

  trackTrialExpiring(daysLeft: number): void {
    this.track(ConversionEvent.TRIAL_EXPIRING, {
      metadata: { days_left: daysLeft },
    });
  },

  trackTrialExpired(): void {
    this.track(ConversionEvent.TRIAL_EXPIRED);
  },

  trackTrialConverted(plan: 'monthly' | 'annual', revenue: number): void {
    this.track(ConversionEvent.TRIAL_CONVERTED, {
      revenue,
      metadata: { plan },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Subscription Events
  // ─────────────────────────────────────────────────────────────────────────

  trackSubscriptionCreated(
    tier: string,
    plan: 'monthly' | 'annual',
    revenue: number
  ): void {
    this.track(ConversionEvent.SUBSCRIPTION_CREATED, {
      revenue,
      metadata: { tier, plan },
    });
  },

  trackSubscriptionCancelled(tier: string, reason?: string): void {
    this.track(ConversionEvent.SUBSCRIPTION_CANCELLED, {
      metadata: { tier, reason },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Addon Events
  // ─────────────────────────────────────────────────────────────────────────

  trackAddonTrialStarted(addon: string): void {
    this.track(ConversionEvent.ADDON_TRIAL_STARTED, {
      metadata: { addon },
    });
  },

  trackAddonPurchased(addon: string, revenue: number): void {
    this.track(ConversionEvent.ADDON_PURCHASED, {
      revenue,
      metadata: { addon },
    });
  },

  trackAddonCancelled(addon: string, reason?: string): void {
    this.track(ConversionEvent.ADDON_CANCELLED, {
      metadata: { addon, reason },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Tier Events
  // ─────────────────────────────────────────────────────────────────────────

  trackTierUpgraded(oldTier: string, newTier: string): void {
    this.track(ConversionEvent.TIER_UPGRADED, {
      metadata: { old_tier: oldTier, new_tier: newTier },
    });
  },

  trackFeaturedAchieved(track: 'writer' | 'curator'): void {
    this.track(ConversionEvent.FEATURED_ACHIEVED, {
      metadata: { track },
    });
  },

  trackAuthorityAchieved(track: 'writer' | 'curator'): void {
    this.track(ConversionEvent.AUTHORITY_ACHIEVED, {
      metadata: { track },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Engagement Events
  // ─────────────────────────────────────────────────────────────────────────

  trackAnalysisCompleted(wordCount: number, profileType: string): void {
    this.track(ConversionEvent.ANALYSIS_COMPLETED, {
      metadata: { word_count: wordCount, profile_type: profileType },
    });
  },

  trackAnalysisLimitReached(limit: number, used: number): void {
    this.track(ConversionEvent.ANALYSIS_LIMIT_REACHED, {
      metadata: { limit, used },
    });
  },

  trackFeatureGatedClick(feature: string, currentTier: string): void {
    this.track(ConversionEvent.FEATURE_GATED_CLICK, {
      metadata: { feature, current_tier: currentTier },
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Upgrade Prompt Events
  // ─────────────────────────────────────────────────────────────────────────

  trackUpgradePrompt(
    promptType: string,
    action: 'shown' | 'clicked' | 'dismissed',
    targetTier?: string
  ): void {
    const eventMap = {
      shown: ConversionEvent.UPGRADE_PROMPT_SHOWN,
      clicked: ConversionEvent.UPGRADE_PROMPT_CLICKED,
      dismissed: ConversionEvent.UPGRADE_PROMPT_DISMISSED,
    };
    
    this.track(eventMap[action], {
      metadata: { prompt_type: promptType, target_tier: targetTier },
    });
    
    // Also send to dedicated endpoint for faster processing
    fetch('/api/v2/conversions/upgrade-prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        prompt_type: promptType,
        action,
      }),
    }).catch(console.error);
  },

  /**
   * Helper to wrap upgrade prompts with tracking
   */
  wrapUpgradePrompt(
    promptType: string,
    onShow: () => void,
    onClick: () => void,
    onDismiss: () => void
  ): {
    show: () => void;
    click: () => void;
    dismiss: () => void;
  } {
    return {
      show: () => {
        this.trackUpgradePrompt(promptType, 'shown');
        onShow();
      },
      click: () => {
        this.trackUpgradePrompt(promptType, 'clicked');
        onClick();
      },
      dismiss: () => {
        this.trackUpgradePrompt(promptType, 'dismissed');
        onDismiss();
      },
    };
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// REACT HOOKS
// ═══════════════════════════════════════════════════════════════════════════

import { useEffect, useCallback } from 'react';

/**
 * Hook to track page views as funnel steps
 */
export const useFunnelStep = (step: string): void => {
  useEffect(() => {
    MetaEvents.emit('funnel_step', { step });
  }, [step]);
};

/**
 * Hook to track upgrade prompt with auto-shown tracking
 */
export const useUpgradePromptTracking = (
  promptType: string,
  isVisible: boolean
) => {
  useEffect(() => {
    if (isVisible) {
      ConversionTracker.trackUpgradePrompt(promptType, 'shown');
    }
  }, [promptType, isVisible]);

  const trackClick = useCallback(() => {
    ConversionTracker.trackUpgradePrompt(promptType, 'clicked');
  }, [promptType]);

  const trackDismiss = useCallback(() => {
    ConversionTracker.trackUpgradePrompt(promptType, 'dismissed');
  }, [promptType]);

  return { trackClick, trackDismiss };
};

/**
 * Hook to track feature gate interactions
 */
export const useFeatureGateTracking = (feature: string, currentTier: string) => {
  const trackGatedClick = useCallback(() => {
    ConversionTracker.trackFeatureGatedClick(feature, currentTier);
  }, [feature, currentTier]);

  return { trackGatedClick };
};

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export default ConversionTracker;
