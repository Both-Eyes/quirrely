import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { Info, Clock, Users, Zap, Crown, Heart } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// NEW WORD POOL USAGE DISPLAY FOR ALL TIERS
// ═══════════════════════════════════════════════════════════════════════════

interface WordPoolUsage {
  tier: 'anonymous' | 'free' | 'pro' | 'partnership';
  daily?: {
    used: number;
    limit: number;
    remaining: number;
  };
  monthly?: {
    used: number;
    limit: number;
    remaining: number;
  };
  partnership?: {
    personal: {
      used: number;
      limit: number;
      remaining: number;
    };
    shared: {
      total_used: number;
      total_limit: number;
      total_remaining: number;
      user_share_limit: number;
    };
    total: {
      available: number;
      theoretical_max: number;
    };
  };
}

interface WordPoolUsageDisplayProps {
  usage: WordPoolUsage;
  onUpgrade?: () => void;
  onPartnershipInvite?: () => void;
  className?: string;
}

const TIER_CONFIG = {
  anonymous: {
    name: 'Guest User',
    icon: Clock,
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 border-gray-200',
    description: '50 words per day',
    upgradeText: 'Create free account for 250 words/day',
    benefits: 'Sign up free for 5x more words daily'
  },
  free: {
    name: 'Free User',
    icon: Zap,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
    description: '250 words per day',
    upgradeText: 'Upgrade to Pro for 20k words/month',
    benefits: '80x more words with Pro upgrade'
  },
  pro: {
    name: 'Pro User',
    icon: Crown,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
    description: '20,000 words per month',
    upgradeText: 'Start a partnership for collaboration',
    benefits: 'Add collaboration with partnerships'
  },
  partnership: {
    name: 'Partnership',
    icon: Heart,
    color: 'text-rose-600',
    bgColor: 'bg-rose-50 border-rose-200',
    description: '10k personal + 10k shared pool',
    upgradeText: '',
    benefits: 'Collaborative writing at its finest'
  },
};

export const WordPoolUsageDisplay: React.FC<WordPoolUsageDisplayProps> = ({
  usage,
  onUpgrade,
  onPartnershipInvite,
  className = '',
}) => {
  const [selectedPool, setSelectedPool] = useState<'personal' | 'shared'>('personal');
  const tierConfig = TIER_CONFIG[usage.tier];
  const TierIcon = tierConfig.icon;

  // Calculate usage percentages and warnings
  const getUsageData = () => {
    if (usage.tier === 'partnership' && usage.partnership) {
      return {
        personal: {
          percentage: Math.round((usage.partnership.personal.used / usage.partnership.personal.limit) * 100),
          remaining: usage.partnership.personal.remaining,
          limit: usage.partnership.personal.limit,
          used: usage.partnership.personal.used,
        },
        shared: {
          percentage: Math.round((usage.partnership.shared.total_used / usage.partnership.shared.total_limit) * 100),
          remaining: usage.partnership.shared.total_remaining,
          limit: usage.partnership.shared.total_limit,
          used: usage.partnership.shared.total_used,
        },
      };
    } else if (usage.daily) {
      return {
        main: {
          percentage: Math.round((usage.daily.used / usage.daily.limit) * 100),
          remaining: usage.daily.remaining,
          limit: usage.daily.limit,
          used: usage.daily.used,
          period: 'daily',
        },
      };
    } else if (usage.monthly) {
      return {
        main: {
          percentage: Math.round((usage.monthly.used / usage.monthly.limit) * 100),
          remaining: usage.monthly.remaining,
          limit: usage.monthly.limit,
          used: usage.monthly.used,
          period: 'monthly',
        },
      };
    }
    return {};
  };

  const usageData = getUsageData();

  const formatWordCount = (count: number): string => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  const getUsageColor = (percentage: number): string => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 80) return 'text-amber-600';
    return 'text-green-600';
  };

  const getProgressColor = (percentage: number): string => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 80) return 'bg-amber-500';
    return 'bg-green-500';
  };

  const showUpgradePrompt = (): boolean => {
    if (usage.tier === 'anonymous' && usageData.main && usageData.main.remaining <= 5) {
      return true;
    }
    if (usage.tier === 'free' && usageData.main && usageData.main.remaining <= 25) {
      return true;
    }
    if (usage.tier === 'pro' && usageData.main && usageData.main.remaining <= 1000) {
      return true;
    }
    return false;
  };

  return (
    <Card className={`${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TierIcon className={`h-5 w-5 ${tierConfig.color}`} />
          <span>Word Usage</span>
          <Badge variant="secondary" className={tierConfig.bgColor}>
            {tierConfig.name}
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Tier Description */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Info className="h-4 w-4" />
          <span>{tierConfig.description}</span>
        </div>

        {/* Partnership Pool Selector */}
        {usage.tier === 'partnership' && usage.partnership && (
          <div className="flex gap-2 mb-4">
            <Button
              variant={selectedPool === 'personal' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPool('personal')}
              className="flex-1"
            >
              Personal Pool
            </Button>
            <Button
              variant={selectedPool === 'shared' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPool('shared')}
              className="flex-1"
            >
              <Users className="h-4 w-4 mr-1" />
              Shared Pool
            </Button>
          </div>
        )}

        {/* Usage Display */}
        {usage.tier === 'partnership' && usage.partnership ? (
          // Partnership usage display
          <div className="space-y-3">
            {selectedPool === 'personal' && usageData.personal && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Personal Words</span>
                  <span className={`text-sm ${getUsageColor(usageData.personal.percentage)}`}>
                    {formatWordCount(usageData.personal.used)} / {formatWordCount(usageData.personal.limit)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getProgressColor(usageData.personal.percentage)}`}
                    style={{ width: `${Math.min(usageData.personal.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatWordCount(usageData.personal.remaining)} words remaining this month
                </div>
              </div>
            )}

            {selectedPool === 'shared' && usageData.shared && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Shared Words</span>
                  <span className={`text-sm ${getUsageColor(usageData.shared.percentage)}`}>
                    {formatWordCount(usageData.shared.used)} / {formatWordCount(usageData.shared.limit)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getProgressColor(usageData.shared.percentage)}`}
                    style={{ width: `${Math.min(usageData.shared.percentage, 100)}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatWordCount(usageData.shared.remaining)} words remaining in shared pool
                </div>
              </div>
            )}

            {/* Total Available */}
            <div className="pt-2 border-t">
              <div className="text-sm font-medium text-green-600">
                Total Available: {formatWordCount(usage.partnership.total.available)} words
              </div>
            </div>
          </div>
        ) : (
          // Standard tier usage display
          usageData.main && (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">
                  Word Usage ({usageData.main.period === 'daily' ? 'Today' : 'This Month'})
                </span>
                <span className={`text-sm ${getUsageColor(usageData.main.percentage)}`}>
                  {formatWordCount(usageData.main.used)} / {formatWordCount(usageData.main.limit)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${getProgressColor(usageData.main.percentage)}`}
                  style={{ width: `${Math.min(usageData.main.percentage, 100)}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500">
                {formatWordCount(usageData.main.remaining)} words remaining 
                {usageData.main.period === 'daily' ? ' today' : ' this month'}
              </div>
            </div>
          )
        )}

        {/* Upgrade Prompt */}
        {showUpgradePrompt() && (
          <div className="pt-3 border-t border-amber-200 bg-amber-50 -mx-6 -mb-6 px-6 pb-6 rounded-b-lg">
            <div className="text-sm text-amber-800 mb-2 font-medium">
              You're running low on words!
            </div>
            <div className="text-xs text-amber-700 mb-3">
              {tierConfig.upgradeText}
            </div>
            <div className="flex gap-2">
              {usage.tier === 'anonymous' && onUpgrade && (
                <Button size="sm" onClick={onUpgrade} className="flex-1">
                  Sign Up Free
                </Button>
              )}
              {usage.tier === 'free' && onUpgrade && (
                <Button size="sm" onClick={onUpgrade} className="flex-1">
                  Upgrade to Pro
                </Button>
              )}
              {usage.tier === 'pro' && onPartnershipInvite && (
                <Button size="sm" onClick={onPartnershipInvite} className="flex-1">
                  Start Partnership
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Tier Benefits Summary */}
        {!showUpgradePrompt() && (
          <div className="text-xs text-gray-500 pt-2 border-t">
            {tierConfig.benefits}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WordPoolUsageDisplay;