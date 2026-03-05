import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { EmptyState } from '../../components/ui/EmptyState';
import { PartnershipCard, PartnershipInvitationCard } from '../../components/collaboration/PartnershipCard';
import { PartnershipInvite } from '../../components/collaboration/PartnershipInvite';
import { usePartnership } from '../../hooks/usePartnership';
import { UserPlus, Heart, Users, Briefcase, Palette, Home, Sparkles } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP DASHBOARD PAGE
// ═══════════════════════════════════════════════════════════════════════════

export const Partnership: React.FC = () => {
  const {
    partnership,
    invitations,
    wordAllocation,
    cancellationStatus,
    isLoading,
    error,
    sendInvitation,
    acceptInvitation,
    cancelPartnership,
    hasActivePartnership,
    hasPendingPartnership,
    getCancellationStatus,
  } = usePartnership();

  const [showInviteForm, setShowInviteForm] = useState(false);
  const [isInviting, setIsInviting] = useState(false);

  // ═══════════════════════════════════════════════════════════════════════════
  // HANDLERS
  // ═══════════════════════════════════════════════════════════════════════════

  const handleSendInvitation = async (inviteData: {
    email: string;
    partnership_name: string;
    partnership_intention: string;
    partnership_type: 'heart' | 'growth' | 'professional' | 'creative' | 'life';
  }) => {
    setIsInviting(true);
    try {
      await sendInvitation(inviteData);
      setShowInviteForm(false);
    } catch (error) {
      console.error('Failed to send invitation:', error);
      // Error is handled by the hook
    } finally {
      setIsInviting(false);
    }
  };

  const handleAcceptInvitation = async (token: string) => {
    try {
      await acceptInvitation(token);
    } catch (error) {
      console.error('Failed to accept invitation:', error);
      // Error is handled by the hook
    }
  };

  const handleCancelPartnership = async () => {
    if (window.confirm('Are you sure you want to leave this partnership? This action cannot be undone.')) {
      try {
        await cancelPartnership();
      } catch (error) {
        console.error('Failed to cancel partnership:', error);
        // Error is handled by the hook
      }
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // LOADING AND ERROR STATES
  // ═══════════════════════════════════════════════════════════════════════════

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-6"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDER PARTNERSHIP STATES
  // ═══════════════════════════════════════════════════════════════════════════

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          🌸 Your Writing Community
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Connect with other Pro tier writers who understand the power of authentic voices. 
          Writing partnerships that support your growth and celebrate your discoveries.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <Card variant="bordered" className="border-red-200 bg-red-50 dark:bg-red-950/20">
          <CardContent>
            <div className="flex items-center gap-3 text-red-700 dark:text-red-400">
              <div className="text-red-500">⚠️</div>
              <div>
                <div className="font-medium">Partnership Error</div>
                <div className="text-sm">{error}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invitations Received */}
      {invitations.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Partnership Invitations
          </h2>
          {invitations.map((invitation) => (
            <PartnershipInvitationCard
              key={invitation.id}
              invitation={invitation}
              onAccept={() => handleAcceptInvitation('invitation-token')} // TODO: pass actual token
              onDecline={() => {/* TODO: implement decline */}}
            />
          ))}
        </div>
      )}

      {/* Active Partnership */}
      {hasActivePartnership() && partnership && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              Your Writing Partnership
            </h2>
          </div>
          
          <PartnershipCard
            partnership={partnership}
            onManage={() => {/* TODO: implement manage */}}
            onCancel={handleCancelPartnership}
            canCancel={cancellationStatus?.can_cancel ?? true}
            nextCancelDate={cancellationStatus?.next_available_date}
          />

          {/* Growth Celebration */}
          {wordAllocation && wordAllocation.usage_history.length > 0 && (
            <Card variant="elevated" className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
              <CardContent>
                <div className="flex items-center gap-3">
                  <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100">
                      🎉 Your Partnership Journey
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      You've written together {wordAllocation.usage_history.length} times! 
                      Each session is building something beautiful.
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Pending Partnership */}
      {hasPendingPartnership() && partnership && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Partnership Invitation Sent
          </h2>
          
          <PartnershipCard
            partnership={partnership}
            onCancel={handleCancelPartnership}
            canCancel={cancellationStatus?.can_cancel ?? true}
            nextCancelDate={cancellationStatus?.next_available_date}
          />
        </div>
      )}

      {/* No Partnership - Show Options */}
      {!partnership && !showInviteForm && (
        <div className="space-y-6">
          {/* Partnership Benefits */}
          <Card variant="elevated" className="bg-gradient-to-br from-coral-50 to-rose-50 dark:from-coral-950/30 dark:to-rose-950/30">
            <CardContent className="text-center">
              <div className="mb-4">
                <Heart className="h-12 w-12 text-coral-500 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  Ready to Write with Someone Special?
                </h3>
                <p className="text-gray-600 dark:text-gray-400 max-w-lg mx-auto">
                  Writing partnerships create a safe, supportive space where you can explore your voice, 
                  share vulnerable work, and grow together through meaningful creative expression.
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg mb-2">
                    <Users className="h-6 w-6 text-coral-500 mx-auto" />
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Shared Creative Space</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">25k words together</div>
                </div>
                <div className="text-center">
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg mb-2">
                    <Sparkles className="h-6 w-6 text-coral-500 mx-auto" />
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Personal Growth</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">12.5k words for you</div>
                </div>
                <div className="text-center">
                  <div className="bg-white dark:bg-gray-800 p-3 rounded-lg mb-2">
                    <Heart className="h-6 w-6 text-coral-500 mx-auto" />
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-gray-100">Meaningful Connection</div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Safe, supportive space</div>
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                onClick={() => setShowInviteForm(true)}
                leftIcon={<UserPlus className="h-5 w-5" />}
              >
                Invite Your Writing Partner
              </Button>
            </CardContent>
          </Card>

          {/* Partnership Types Preview */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Types of Writing Partnerships</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {[
                  {
                    icon: Heart,
                    name: 'Heart Partnerships',
                    description: 'Life\'s most meaningful moments',
                    examples: 'Wedding vows, family stories, letters to children',
                    color: 'text-rose-600 dark:text-rose-400',
                  },
                  {
                    icon: Users,
                    name: 'Growth Partnerships',
                    description: 'Supporting each other\'s journey',
                    examples: 'Mentorship, accountability, creative challenges',
                    color: 'text-emerald-600 dark:text-emerald-400',
                  },
                  {
                    icon: Briefcase,
                    name: 'Professional Partnerships',
                    description: 'Authentic voice at work',
                    examples: 'Presentations, proposals, performance reviews',
                    color: 'text-blue-600 dark:text-blue-400',
                  },
                  {
                    icon: Palette,
                    name: 'Creative Partnerships',
                    description: 'Playing with possibilities',
                    examples: 'Fiction, poetry, blogs, creative experiments',
                    color: 'text-purple-600 dark:text-purple-400',
                  },
                ].map((type) => {
                  const Icon = type.icon;
                  return (
                    <div key={type.name} className="flex gap-3">
                      <div className="mt-1">
                        <Icon className={`h-5 w-5 ${type.color}`} />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                          {type.name}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          {type.description}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-500">
                          {type.examples}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Invitation Form */}
      {showInviteForm && (
        <PartnershipInvite
          onInvite={handleSendInvitation}
          isLoading={isInviting}
        />
      )}

      {/* Cancel Invitation Form */}
      {showInviteForm && (
        <div className="text-center">
          <Button
            variant="ghost"
            onClick={() => setShowInviteForm(false)}
          >
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
};

export default Partnership;