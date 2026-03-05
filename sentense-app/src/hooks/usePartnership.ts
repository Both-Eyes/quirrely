import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { CollaborationTracker } from '../lib/collaboration-tracker';

// ═══════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════

interface Partnership {
  id: string;
  partnership_name: string;
  partnership_type: 'heart' | 'growth' | 'professional' | 'creative' | 'life';
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  partner_name: string;
  partner_email: string;
  shared_creative_space: number;
  shared_space_used: number;
  solo_words_remaining: number;
  period_end: string;
  started_at?: string;
}

interface PartnershipInvitation {
  id: string;
  partnership_name: string;
  partnership_type: 'heart' | 'growth' | 'professional' | 'creative' | 'life';
  partnership_intention?: string;
  initiator_name: string;
  expires_at: string;
}

interface WordAllocation {
  has_collaboration: boolean;
  shared_words_available: number;
  shared_words_used: number;
  shared_words_remaining: number;
  solo_words_remaining: number;
  period_end?: string;
  usage_history: Array<{
    usage_type: 'shared' | 'solo';
    words_used: number;
    analysis_type: string;
    created_at: string;
  }>;
}

interface CancellationStatus {
  can_cancel: boolean;
  next_available_date: string;
  message: string;
}

interface InviteRequest {
  email: string;
  partnership_name: string;
  partnership_intention: string;
  partnership_type: 'heart' | 'growth' | 'professional' | 'creative' | 'life';
}

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP HOOK
// ═══════════════════════════════════════════════════════════════════════════

export const usePartnership = () => {
  const { user, isAuthenticated } = useAuth();
  const [partnership, setPartnership] = useState<Partnership | null>(null);
  const [invitations, setInvitations] = useState<PartnershipInvitation[]>([]);
  const [wordAllocation, setWordAllocation] = useState<WordAllocation | null>(null);
  const [cancellationStatus, setCancellationStatus] = useState<CancellationStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ═══════════════════════════════════════════════════════════════════════════
  // API FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const apiCall = async (endpoint: string, options?: any) => {
    const { default: apiClient } = await import('../api/client');
    
    try {
      const response = await apiClient({
        url: `/v2/collaboration${endpoint}`,
        method: options?.method || 'GET',
        data: options?.body ? JSON.parse(options.body) : undefined,
        ...options,
      });
      
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || 'API request failed');
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // LOAD PARTNERSHIP DATA
  // ═══════════════════════════════════════════════════════════════════════════

  const loadPartnershipData = async () => {
    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Load current partnership
      const partnershipData = await apiCall('/status');
      setPartnership(partnershipData);

      // Load word allocation
      const wordData = await apiCall('/words');
      setWordAllocation(wordData);

      // Load cancellation status if user has partnership
      if (partnershipData) {
        const cancelStatus = await apiCall('/cancel-status');
        setCancellationStatus(cancelStatus);
      }

      // Load pending invitations (if we add this endpoint)
      // const invitationData = await apiCall('/invitations/pending');
      // setInvitations(invitationData);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load partnership data');
      console.error('Partnership data load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load data when user changes
  useEffect(() => {
    loadPartnershipData();
  }, [isAuthenticated, user?.id]);

  // ═══════════════════════════════════════════════════════════════════════════
  // PARTNERSHIP ACTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const sendInvitation = async (inviteData: InviteRequest): Promise<void> => {
    try {
      setError(null);
      
      await apiCall('/invite', {
        method: 'POST',
        body: JSON.stringify({
          email: inviteData.email,
          project_title: inviteData.partnership_name,
          project_description: inviteData.partnership_intention,
          category: inviteData.partnership_type,
        }),
      });

      // Track the invitation
      CollaborationTracker.trackInvitationSent(
        inviteData.email,
        inviteData.partnership_name,
        inviteData.partnership_type
      );

      // Reload data to show pending partnership
      await loadPartnershipData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send invitation';
      setError(message);
      throw new Error(message);
    }
  };

  const acceptInvitation = async (token: string): Promise<void> => {
    try {
      setError(null);
      
      await apiCall('/accept', {
        method: 'POST',
        body: JSON.stringify({ token }),
      });

      // Track acceptance
      if (partnership) {
        CollaborationTracker.trackInvitationAccepted(
          partnership.id,
          partnership.partnership_type
        );
      }

      // Reload data to show active partnership
      await loadPartnershipData();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to accept invitation';
      setError(message);
      throw new Error(message);
    }
  };

  const cancelPartnership = async (): Promise<void> => {
    if (!partnership) return;

    try {
      setError(null);
      
      await apiCall('/cancel', {
        method: 'POST',
      });

      // Track cancellation
      CollaborationTracker.trackProjectCancelled(
        partnership.id,
        partnership.partnership_type,
        'user_initiated'
      );

      // Clear local state
      setPartnership(null);
      setWordAllocation(null);
      setCancellationStatus(null);
      
    } catch (err: any) {
      let message = 'Failed to cancel partnership';
      
      // Handle rate limiting error (HTTP 429)
      if (err.status === 429) {
        message = err.message || 'You can only cancel one collaboration per month';
      } else {
        message = err instanceof Error ? err.message : message;
      }
      
      setError(message);
      throw new Error(message);
    }
  };

  const getCancellationStatus = (): CancellationStatus | null => {
    return cancellationStatus;
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // WORD USAGE
  // ═══════════════════════════════════════════════════════════════════════════

  const useWords = async (
    words_used: number,
    usage_type: 'shared' | 'solo',
    analysis_type: string,
    analysis_id?: string
  ): Promise<void> => {
    if (!partnership || partnership.status !== 'active') {
      throw new Error('No active partnership found');
    }

    try {
      setError(null);
      
      await apiCall('/use-words', {
        method: 'POST',
        body: JSON.stringify({
          words_used,
          usage_type,
          analysis_type,
          analysis_id,
        }),
      });

      // Track word usage
      if (usage_type === 'shared' && wordAllocation) {
        CollaborationTracker.trackSharedWordsUsed(
          partnership.id,
          words_used,
          analysis_type,
          wordAllocation.shared_words_remaining - words_used
        );
      } else if (usage_type === 'solo' && wordAllocation) {
        CollaborationTracker.trackSoloWordsUsed(
          partnership.id,
          words_used,
          analysis_type,
          wordAllocation.solo_words_remaining - words_used
        );
      }

      // Reload word allocation
      const wordData = await apiCall('/words');
      setWordAllocation(wordData);
      
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to use words';
      setError(message);
      throw new Error(message);
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // UTILITY FUNCTIONS
  // ═══════════════════════════════════════════════════════════════════════════

  const canUseWords = (words_needed: number, type: 'shared' | 'solo'): boolean => {
    if (!wordAllocation?.has_collaboration) return false;
    
    if (type === 'shared') {
      return wordAllocation.shared_words_remaining >= words_needed;
    } else {
      return wordAllocation.solo_words_remaining >= words_needed;
    }
  };

  const getWordAllowance = (): { shared: number; solo: number } => {
    if (!wordAllocation?.has_collaboration) {
      return { shared: 0, solo: 0 };
    }
    
    return {
      shared: wordAllocation.shared_words_remaining,
      solo: wordAllocation.solo_words_remaining,
    };
  };

  const hasActivePartnership = (): boolean => {
    return partnership?.status === 'active';
  };

  const hasPendingPartnership = (): boolean => {
    return partnership?.status === 'pending';
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // RETURN HOOK INTERFACE
  // ═══════════════════════════════════════════════════════════════════════════

  return {
    // State
    partnership,
    invitations,
    wordAllocation,
    cancellationStatus,
    isLoading,
    error,
    
    // Actions
    sendInvitation,
    acceptInvitation,
    cancelPartnership,
    useWords,
    refresh: loadPartnershipData,
    
    // Utilities
    canUseWords,
    getWordAllowance,
    hasActivePartnership,
    hasPendingPartnership,
    getCancellationStatus,
  };
};

export default usePartnership;