import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Heart, Users, Briefcase, Palette, Home, Calendar, Star } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP TYPES AND ICONS
// ═══════════════════════════════════════════════════════════════════════════

const PARTNERSHIP_ICONS = {
  heart: Heart,
  growth: Users,
  professional: Briefcase,
  creative: Palette,
  life: Home,
} as const;

const PARTNERSHIP_LABELS = {
  heart: 'Heart Partnership',
  growth: 'Growth Partnership',
  professional: 'Professional Partnership',
  creative: 'Creative Partnership',
  life: 'Life Partnership',
} as const;

const PARTNERSHIP_COLORS = {
  heart: 'bg-rose-50 text-rose-700 border-rose-200',
  growth: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  professional: 'bg-blue-50 text-blue-700 border-blue-200',
  creative: 'bg-purple-50 text-purple-700 border-purple-200',
  life: 'bg-amber-50 text-amber-700 border-amber-200',
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP CARD COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface PartnershipData {
  id: string;
  partnership_name: string;
  partnership_type: keyof typeof PARTNERSHIP_ICONS;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  partner_name: string;
  partner_email: string;
  shared_creative_space: number;
  shared_space_used: number;
  solo_words_remaining: number;
  period_end: string;
  started_at?: string;
}

interface PartnershipCardProps {
  partnership: PartnershipData;
  onManage?: () => void;
  onCancel?: () => void;
  canCancel?: boolean;
  nextCancelDate?: string;
  className?: string;
}

export const PartnershipCard: React.FC<PartnershipCardProps> = ({
  partnership,
  onManage,
  onCancel,
  canCancel = true,
  nextCancelDate,
  className = '',
}) => {
  const Icon = PARTNERSHIP_ICONS[partnership.partnership_type];
  const label = PARTNERSHIP_LABELS[partnership.partnership_type];
  const badgeColor = PARTNERSHIP_COLORS[partnership.partnership_type];
  
  // Calculate usage percentages
  const sharedUsagePercent = Math.round(
    (partnership.shared_space_used / partnership.shared_creative_space) * 100
  );
  
  const sharedRemaining = partnership.shared_creative_space - partnership.shared_space_used;
  
  // Format dates
  const periodEnd = new Date(partnership.period_end);
  const daysUntilReset = Math.ceil(
    (periodEnd.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );
  
  const formatWordCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toLocaleString();
  };

  return (
    <Card className={`${className} transition-all duration-200 hover:shadow-soft`} variant="elevated">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg border ${badgeColor}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg text-gray-900 dark:text-gray-100">
                {partnership.partnership_name}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="secondary" className="text-xs">
                  {label}
                </Badge>
                {partnership.status === 'active' && (
                  <Badge variant="success" className="text-xs">
                    Active
                  </Badge>
                )}
                {partnership.status === 'pending' && (
                  <Badge variant="warning" className="text-xs">
                    Pending
                  </Badge>
                )}
              </div>
            </div>
          </div>
          
          {partnership.status === 'active' && (
            <div className="flex gap-2">
              {onManage && (
                <Button variant="outline" size="sm" onClick={onManage}>
                  Manage
                </Button>
              )}
              {onCancel && (
                <div className="flex flex-col items-end gap-1">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={onCancel}
                    disabled={!canCancel}
                    title={!canCancel ? `Can cancel again on ${nextCancelDate ? new Date(nextCancelDate).toLocaleDateString() : 'next month'}` : undefined}
                  >
                    Leave Partnership
                  </Button>
                  {!canCancel && nextCancelDate && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 text-right">
                      Next: {new Date(nextCancelDate).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Partner Info */}
        <div className="mb-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">Writing with</div>
          <div className="font-medium text-gray-900 dark:text-gray-100">
            {partnership.partner_name}
          </div>
        </div>
        
        {partnership.status === 'active' && (
          <>
            {/* Shared Creative Space */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  🫶 Shared Creative Space
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatWordCount(sharedRemaining)} remaining
                </div>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
                <div
                  className="bg-coral-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${sharedUsagePercent}%` }}
                />
              </div>
              
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {formatWordCount(partnership.shared_space_used)} of {formatWordCount(partnership.shared_creative_space)} used ({sharedUsagePercent}%)
              </div>
            </div>
            
            {/* Solo Space */}
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  ✨ Your Solo Space
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatWordCount(partnership.solo_words_remaining)} remaining
                </div>
              </div>
            </div>
            
            {/* Period Info */}
            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              <Calendar className="h-3 w-3" />
              <span>
                {daysUntilReset > 0 
                  ? `Resets in ${daysUntilReset} day${daysUntilReset !== 1 ? 's' : ''}`
                  : 'Resets soon'
                }
              </span>
            </div>
          </>
        )}
        
        {partnership.status === 'pending' && (
          <div className="text-center py-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              Waiting for {partnership.partner_name} to accept your invitation
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Invitation expires in a few days
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// PARTNERSHIP INVITATION CARD
// ═══════════════════════════════════════════════════════════════════════════

interface InvitationCardProps {
  invitation: {
    id: string;
    partnership_name: string;
    partnership_type: keyof typeof PARTNERSHIP_ICONS;
    partnership_intention?: string;
    initiator_name: string;
    expires_at: string;
  };
  onAccept: () => void;
  onDecline: () => void;
  className?: string;
}

export const PartnershipInvitationCard: React.FC<InvitationCardProps> = ({
  invitation,
  onAccept,
  onDecline,
  className = '',
}) => {
  const Icon = PARTNERSHIP_ICONS[invitation.partnership_type];
  const label = PARTNERSHIP_LABELS[invitation.partnership_type];
  const badgeColor = PARTNERSHIP_COLORS[invitation.partnership_type];
  
  const expiresAt = new Date(invitation.expires_at);
  const hoursUntilExpiry = Math.ceil(
    (expiresAt.getTime() - Date.now()) / (1000 * 60 * 60)
  );

  return (
    <Card className={`${className} border-l-4 border-l-coral-500`} variant="elevated">
      <CardHeader>
        <div className="flex items-center gap-3 mb-3">
          <div className={`p-2 rounded-lg border ${badgeColor}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-lg text-gray-900 dark:text-gray-100">
              Partnership Invitation
            </CardTitle>
            <Badge variant="secondary" className="text-xs mt-1">
              {label}
            </Badge>
          </div>
        </div>
        
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <span className="font-medium text-gray-900 dark:text-gray-100">
            {invitation.initiator_name}
          </span>
          {' '}wants to start a writing partnership with you
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="mb-4">
          <div className="font-medium text-gray-900 dark:text-gray-100 mb-2">
            "{invitation.partnership_name}"
          </div>
          
          {invitation.partnership_intention && (
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {invitation.partnership_intention}
            </div>
          )}
        </div>
        
        {/* What you'll get */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 mb-4">
          <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
            Writing Partnership Benefits:
          </div>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <li className="flex items-center gap-2">
              <div className="w-1 h-1 bg-coral-500 rounded-full"></div>
              20k word shared creative space
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1 h-1 bg-coral-500 rounded-full"></div>
              10k words for your personal work
            </li>
            <li className="flex items-center gap-2">
              <div className="w-1 h-1 bg-coral-500 rounded-full"></div>
              Supportive partnership for meaningful writing
            </li>
          </ul>
        </div>
        
        <div className="flex gap-3">
          <Button 
            variant="primary" 
            onClick={onAccept}
            className="flex-1"
          >
            Accept Partnership
          </Button>
          <Button 
            variant="ghost" 
            onClick={onDecline}
            className="flex-1"
          >
            Decline
          </Button>
        </div>
        
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center mt-3">
          Invitation expires in {hoursUntilExpiry} hours
        </div>
      </CardContent>
    </Card>
  );
};

export default PartnershipCard;