/**
 * QUIRRELY COLLABORATION TRACKER
 * Tracks collaboration-related events and integrates with compare feature.
 * 
 * Flow: Compare → Auth → Upgrade → Collaborate
 * 
 * Events tracked:
 * - Compare feature usage leading to collaboration interest
 * - Collaboration invitations sent/received
 * - Word usage from shared pools
 * - Featured collaboration submissions
 */

import { MetaEvents } from './meta-events';
import { ConversionTracker } from './conversion-tracker';

// ═══════════════════════════════════════════════════════════════════════════
// COLLABORATION EVENT TYPES
// ═══════════════════════════════════════════════════════════════════════════

export const CollaborationEvent = {
  // Compare → Collaboration funnel
  COMPARE_COLLAB_INTEREST: 'compare.collaboration.interest',
  COMPARE_TO_AUTH_REDIRECT: 'compare.auth.redirect',
  COMPARE_TO_UPGRADE_PROMPT: 'compare.upgrade.prompt',
  
  // Collaboration lifecycle
  INVITATION_SENT: 'collaboration.invitation.sent',
  INVITATION_RECEIVED: 'collaboration.invitation.received',
  INVITATION_ACCEPTED: 'collaboration.invitation.accepted',
  INVITATION_DECLINED: 'collaboration.invitation.declined',
  
  // Word usage tracking
  SHARED_WORDS_USED: 'collaboration.words.shared.used',
  SOLO_WORDS_USED: 'collaboration.words.solo.used',
  WORD_POOL_DEPLETED: 'collaboration.words.pool_depleted',
  
  // Project management
  PROJECT_CREATED: 'collaboration.project.created',
  PROJECT_COMPLETED: 'collaboration.project.completed',
  PROJECT_CANCELLED: 'collaboration.project.cancelled',
  
  // Featured collaborations
  FEATURED_SUBMISSION_STARTED: 'collaboration.featured.submission.started',
  FEATURED_SUBMISSION_COMPLETED: 'collaboration.featured.submission.completed',
  FEATURED_COLLABORATION_VIEWED: 'collaboration.featured.viewed',
  
} as const;

export type CollaborationEventType = typeof CollaborationEvent[keyof typeof CollaborationEvent];

// ═══════════════════════════════════════════════════════════════════════════
// COLLABORATION TRACKER
// ═══════════════════════════════════════════════════════════════════════════

interface CollabTrackOptions {
  metadata?: Record<string, unknown>;
  collaborationId?: string;
  partnerId?: string;
  category?: string;
  wordCount?: number;
}

export const CollaborationTracker = {
  /**
   * Track any collaboration event
   */
  track(event: CollaborationEventType, options: CollabTrackOptions = {}): void {
    // Send to backend API
    fetch('/api/v2/collaboration/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        event,
        collaboration_id: options.collaborationId,
        partner_id: options.partnerId,
        category: options.category,
        word_count: options.wordCount,
        metadata: options.metadata || {},
        timestamp: new Date().toISOString(),
      }),
    }).catch(console.error);
    
    // Also emit to Meta events for real-time processing
    MetaEvents.emit('collaboration', {
      event,
      collaboration_id: options.collaborationId,
      partner_id: options.partnerId,
      category: options.category,
      word_count: options.wordCount,
      ...options.metadata,
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Compare → Collaboration Integration
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Track when users show interest in collaboration from compare feature
   */
  trackCompareCollaborationInterest(compareId: string, comparePartner: string): void {
    this.track(CollaborationEvent.COMPARE_COLLAB_INTEREST, {
      metadata: {
        compare_id: compareId,
        compare_partner: comparePartner,
        source: 'compare_results'
      }
    });
    
    // Also track as conversion event for funnel analysis
    ConversionTracker.trackFeatureGatedClick('collaboration', 'compare_user');
  },

  /**
   * Track redirect from compare to auth/signup
   */
  trackCompareToAuthRedirect(compareId: string, targetAction: 'signup' | 'login'): void {
    this.track(CollaborationEvent.COMPARE_TO_AUTH_REDIRECT, {
      metadata: {
        compare_id: compareId,
        target_action: targetAction,
        conversion_source: 'collaboration_interest'
      }
    });
    
    ConversionTracker.trackSignupStarted('collaboration_compare');
  },

  /**
   * Track upgrade prompt shown after compare → auth
   */
  trackCompareToUpgradePrompt(compareId: string): void {
    this.track(CollaborationEvent.COMPARE_TO_UPGRADE_PROMPT, {
      metadata: {
        compare_id: compareId,
        upgrade_reason: 'collaboration_access'
      }
    });
    
    ConversionTracker.trackUpgradePrompt('collaboration_compare', 'shown', 'pro');
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Collaboration Lifecycle
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Track collaboration invitation sent
   */
  trackInvitationSent(
    partnerEmail: string,
    projectTitle: string,
    category: string
  ): void {
    this.track(CollaborationEvent.INVITATION_SENT, {
      metadata: {
        partner_email: partnerEmail,
        project_title: projectTitle
      },
      category
    });
  },

  /**
   * Track collaboration invitation received
   */
  trackInvitationReceived(
    collaborationId: string,
    initiatorName: string,
    category: string
  ): void {
    this.track(CollaborationEvent.INVITATION_RECEIVED, {
      collaborationId,
      metadata: {
        initiator_name: initiatorName
      },
      category
    });
  },

  /**
   * Track collaboration invitation accepted
   */
  trackInvitationAccepted(collaborationId: string, category: string): void {
    this.track(CollaborationEvent.INVITATION_ACCEPTED, {
      collaborationId,
      category
    });
    
    // Track as conversion event
    ConversionTracker.trackFeatureEngagement(
      'collaboration_started',
      { category }
    );
  },

  /**
   * Track collaboration invitation declined
   */
  trackInvitationDeclined(
    collaborationId: string,
    reason?: string
  ): void {
    this.track(CollaborationEvent.INVITATION_DECLINED, {
      collaborationId,
      metadata: { decline_reason: reason }
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Word Usage Tracking
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Track shared word usage
   */
  trackSharedWordsUsed(
    collaborationId: string,
    wordsUsed: number,
    analysisType: string,
    remainingShared: number
  ): void {
    this.track(CollaborationEvent.SHARED_WORDS_USED, {
      collaborationId,
      wordCount: wordsUsed,
      metadata: {
        analysis_type: analysisType,
        remaining_shared: remainingShared,
        pool_type: 'shared'
      }
    });

    // Alert if pool getting low
    if (remainingShared <= 1000) {
      this.track(CollaborationEvent.WORD_POOL_DEPLETED, {
        collaborationId,
        metadata: {
          pool_type: 'shared',
          remaining: remainingShared,
          threshold: 1000
        }
      });
    }
  },

  /**
   * Track solo word usage in collaboration context
   */
  trackSoloWordsUsed(
    collaborationId: string,
    wordsUsed: number,
    analysisType: string,
    remainingSolo: number
  ): void {
    this.track(CollaborationEvent.SOLO_WORDS_USED, {
      collaborationId,
      wordCount: wordsUsed,
      metadata: {
        analysis_type: analysisType,
        remaining_solo: remainingSolo,
        pool_type: 'solo'
      }
    });

    // Alert if solo pool getting low
    if (remainingSolo <= 500) {
      this.track(CollaborationEvent.WORD_POOL_DEPLETED, {
        collaborationId,
        metadata: {
          pool_type: 'solo',
          remaining: remainingSolo,
          threshold: 500
        }
      });
    }
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Project Management
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Track project created
   */
  trackProjectCreated(
    collaborationId: string,
    projectTitle: string,
    category: string
  ): void {
    this.track(CollaborationEvent.PROJECT_CREATED, {
      collaborationId,
      category,
      metadata: {
        project_title: projectTitle
      }
    });
  },

  /**
   * Track project completed
   */
  trackProjectCompleted(
    collaborationId: string,
    category: string,
    totalWordsUsed: number,
    durationDays: number
  ): void {
    this.track(CollaborationEvent.PROJECT_COMPLETED, {
      collaborationId,
      category,
      metadata: {
        total_words_used: totalWordsUsed,
        duration_days: durationDays,
        completion_rate: 1.0
      }
    });

    // Track as conversion event
    ConversionTracker.trackFeatureEngagement(
      'collaboration_completed',
      { category, words_used: totalWordsUsed }
    );
  },

  /**
   * Track project cancelled
   */
  trackProjectCancelled(
    collaborationId: string,
    category: string,
    reason?: string,
    wordsUsed?: number
  ): void {
    this.track(CollaborationEvent.PROJECT_CANCELLED, {
      collaborationId,
      category,
      metadata: {
        cancel_reason: reason,
        words_used_before_cancel: wordsUsed
      }
    });
  },

  // ─────────────────────────────────────────────────────────────────────────
  // Featured Collaborations
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Track featured submission started
   */
  trackFeaturedSubmissionStarted(collaborationId: string, category: string): void {
    this.track(CollaborationEvent.FEATURED_SUBMISSION_STARTED, {
      collaborationId,
      category
    });
  },

  /**
   * Track featured submission completed
   */
  trackFeaturedSubmissionCompleted(
    collaborationId: string,
    category: string,
    submissionTitle: string,
    sampleWordCount: number
  ): void {
    this.track(CollaborationEvent.FEATURED_SUBMISSION_COMPLETED, {
      collaborationId,
      category,
      metadata: {
        submission_title: submissionTitle,
        sample_word_count: sampleWordCount
      }
    });

    // Track as conversion event
    ConversionTracker.trackFeatureEngagement(
      'featured_collaboration_submitted',
      { category }
    );
  },

  /**
   * Track featured collaboration viewed (public)
   */
  trackFeaturedCollaborationViewed(
    featuredId: string,
    category: string,
    viewerType: 'anonymous' | 'user' | 'pro'
  ): void {
    this.track(CollaborationEvent.FEATURED_COLLABORATION_VIEWED, {
      metadata: {
        featured_id: featuredId,
        viewer_type: viewerType
      },
      category
    });
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// REACT HOOKS FOR COLLABORATION
// ═══════════════════════════════════════════════════════════════════════════

import { useEffect, useCallback } from 'react';

/**
 * Hook for tracking compare → collaboration funnel
 */
export const useCompareToCollaborationTracking = (compareId?: string) => {
  const trackCollaborationInterest = useCallback(() => {
    if (compareId) {
      CollaborationTracker.trackCompareCollaborationInterest(compareId, 'compare_partner');
    }
  }, [compareId]);

  const trackAuthRedirect = useCallback((action: 'signup' | 'login') => {
    if (compareId) {
      CollaborationTracker.trackCompareToAuthRedirect(compareId, action);
    }
  }, [compareId]);

  const trackUpgradePrompt = useCallback(() => {
    if (compareId) {
      CollaborationTracker.trackCompareToUpgradePrompt(compareId);
    }
  }, [compareId]);

  return {
    trackCollaborationInterest,
    trackAuthRedirect,
    trackUpgradePrompt
  };
};

/**
 * Hook for tracking collaboration word usage
 */
export const useCollaborationWordTracking = (collaborationId?: string) => {
  const trackSharedWords = useCallback((
    words: number,
    analysisType: string,
    remaining: number
  ) => {
    if (collaborationId) {
      CollaborationTracker.trackSharedWordsUsed(
        collaborationId,
        words,
        analysisType,
        remaining
      );
    }
  }, [collaborationId]);

  const trackSoloWords = useCallback((
    words: number,
    analysisType: string,
    remaining: number
  ) => {
    if (collaborationId) {
      CollaborationTracker.trackSoloWordsUsed(
        collaborationId,
        words,
        analysisType,
        remaining
      );
    }
  }, [collaborationId]);

  return { trackSharedWords, trackSoloWords };
};

/**
 * Hook for tracking collaboration project lifecycle
 */
export const useCollaborationProjectTracking = (
  collaborationId?: string,
  category?: string
) => {
  const trackProjectCreated = useCallback((title: string) => {
    if (collaborationId && category) {
      CollaborationTracker.trackProjectCreated(collaborationId, title, category);
    }
  }, [collaborationId, category]);

  const trackProjectCompleted = useCallback((
    totalWords: number,
    durationDays: number
  ) => {
    if (collaborationId && category) {
      CollaborationTracker.trackProjectCompleted(
        collaborationId,
        category,
        totalWords,
        durationDays
      );
    }
  }, [collaborationId, category]);

  const trackProjectCancelled = useCallback((reason?: string, wordsUsed?: number) => {
    if (collaborationId && category) {
      CollaborationTracker.trackProjectCancelled(
        collaborationId,
        category,
        reason,
        wordsUsed
      );
    }
  }, [collaborationId, category]);

  return {
    trackProjectCreated,
    trackProjectCompleted,
    trackProjectCancelled
  };
};

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export default CollaborationTracker;