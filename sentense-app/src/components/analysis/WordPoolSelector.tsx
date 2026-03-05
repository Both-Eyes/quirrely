import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Heart, User, AlertTriangle, Users } from 'lucide-react';
import { usePartnership } from '../../hooks/usePartnership';

// ═══════════════════════════════════════════════════════════════════════════
// WORD POOL SELECTOR COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface WordPoolSelectorProps {
  wordsNeeded: number;
  onPoolSelected: (poolType: 'shared' | 'solo' | 'regular') => void;
  selectedPool?: 'shared' | 'solo' | 'regular';
  className?: string;
}

export const WordPoolSelector: React.FC<WordPoolSelectorProps> = ({
  wordsNeeded,
  onPoolSelected,
  selectedPool,
  className = '',
}) => {
  const { hasActivePartnership, canUseWords, getWordAllowance } = usePartnership();
  const [allowance, setAllowance] = useState({ shared: 0, solo: 0 });

  useEffect(() => {
    if (hasActivePartnership()) {
      const currentAllowance = getWordAllowance();
      setAllowance(currentAllowance);
    }
  }, [hasActivePartnership, getWordAllowance]);

  // If no partnership, use regular analysis flow
  if (!hasActivePartnership()) {
    return null;
  }

  const formatWordCount = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toLocaleString();
  };

  const canUseShared = canUseWords(wordsNeeded, 'shared');
  const canUseSolo = canUseWords(wordsNeeded, 'solo');

  return (
    <Card className={`${className} border-l-4 border-l-coral-500 bg-gradient-to-r from-coral-50 to-rose-50 dark:from-coral-950/30 dark:to-rose-950/30`}>
      <CardContent>
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-coral-100 dark:bg-coral-900 rounded-lg">
              <Heart className="h-5 w-5 text-coral-600 dark:text-coral-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                Choose Your Creative Space
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Words needed: {formatWordCount(wordsNeeded)}
              </p>
            </div>
          </div>

          {/* Pool Options */}
          <div className="space-y-3">
            {/* Shared Pool */}
            <button
              onClick={() => onPoolSelected('shared')}
              disabled={!canUseShared}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                selectedPool === 'shared'
                  ? 'border-coral-500 bg-coral-50 dark:bg-coral-950/50'
                  : canUseShared
                  ? 'border-gray-200 dark:border-gray-700 hover:border-coral-300 hover:bg-coral-25 dark:hover:bg-coral-950/25'
                  : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <Users className={`h-5 w-5 mt-1 ${
                    canUseShared ? 'text-coral-600 dark:text-coral-400' : 'text-gray-400'
                  }`} />
                  <div>
                    <div className={`font-medium ${
                      canUseShared ? 'text-gray-900 dark:text-gray-100' : 'text-gray-500'
                    }`}>
                      🫶 Shared Creative Space
                    </div>
                    <div className={`text-sm ${
                      canUseShared ? 'text-gray-600 dark:text-gray-400' : 'text-gray-400'
                    }`}>
                      Writing together with your partner
                    </div>
                    <div className={`text-xs mt-1 ${
                      canUseShared ? 'text-gray-500' : 'text-gray-400'
                    }`}>
                      {formatWordCount(allowance.shared)} words available
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1">
                  {selectedPool === 'shared' && (
                    <Badge variant="primary" className="text-xs">
                      Selected
                    </Badge>
                  )}
                  {!canUseShared && (
                    <Badge variant="secondary" className="text-xs">
                      Insufficient
                    </Badge>
                  )}
                </div>
              </div>
            </button>

            {/* Solo Pool */}
            <button
              onClick={() => onPoolSelected('solo')}
              disabled={!canUseSolo}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                selectedPool === 'solo'
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-950/50'
                  : canUseSolo
                  ? 'border-gray-200 dark:border-gray-700 hover:border-purple-300 hover:bg-purple-25 dark:hover:bg-purple-950/25'
                  : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <User className={`h-5 w-5 mt-1 ${
                    canUseSolo ? 'text-purple-600 dark:text-purple-400' : 'text-gray-400'
                  }`} />
                  <div>
                    <div className={`font-medium ${
                      canUseSolo ? 'text-gray-900 dark:text-gray-100' : 'text-gray-500'
                    }`}>
                      ✨ Your Solo Space
                    </div>
                    <div className={`text-sm ${
                      canUseSolo ? 'text-gray-600 dark:text-gray-400' : 'text-gray-400'
                    }`}>
                      For your personal discoveries
                    </div>
                    <div className={`text-xs mt-1 ${
                      canUseSolo ? 'text-gray-500' : 'text-gray-400'
                    }`}>
                      {formatWordCount(allowance.solo)} words available
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1">
                  {selectedPool === 'solo' && (
                    <Badge variant="primary" className="text-xs">
                      Selected
                    </Badge>
                  )}
                  {!canUseSolo && (
                    <Badge variant="secondary" className="text-xs">
                      Insufficient
                    </Badge>
                  )}
                </div>
              </div>
            </button>
          </div>

          {/* Warning if neither pool has enough words */}
          {!canUseShared && !canUseSolo && (
            <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              <div className="text-sm text-amber-800 dark:text-amber-200">
                <div className="font-medium">Insufficient words available</div>
                <div className="text-xs text-amber-600 dark:text-amber-400">
                  Your partnership will renew at the beginning of next month
                </div>
              </div>
            </div>
          )}

          {/* Help Text */}
          <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg">
            <div className="font-medium mb-1">💡 Partnership Tips:</div>
            <ul className="space-y-1">
              <li>• <strong>Shared Space</strong>: Perfect for collaborative writing and feedback</li>
              <li>• <strong>Solo Space</strong>: Great for preparing drafts before sharing</li>
              <li>• Both pools reset monthly and track your creative growth</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// USAGE TRACKING COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface WordUsageTrackerProps {
  wordsUsed: number;
  poolType: 'shared' | 'solo';
  onUsageComplete?: () => void;
  className?: string;
}

export const WordUsageTracker: React.FC<WordUsageTrackerProps> = ({
  wordsUsed,
  poolType,
  onUsageComplete,
  className = '',
}) => {
  const { useWords } = usePartnership();

  useEffect(() => {
    const trackUsage = async () => {
      try {
        await useWords(
          wordsUsed,
          poolType,
          'writing_analysis',  // analysis type
          undefined            // analysis_id
        );
        
        if (onUsageComplete) {
          onUsageComplete();
        }
      } catch (error) {
        console.error('Failed to track word usage:', error);
      }
    };

    if (wordsUsed > 0) {
      trackUsage();
    }
  }, [wordsUsed, poolType, useWords, onUsageComplete]);

  return (
    <div className={`${className} text-sm text-gray-600 dark:text-gray-400`}>
      <div className="flex items-center gap-2">
        {poolType === 'shared' ? (
          <Users className="h-4 w-4 text-coral-500" />
        ) : (
          <User className="h-4 w-4 text-purple-500" />
        )}
        <span>
          {wordsUsed} words used from your {poolType === 'shared' ? 'shared' : 'solo'} space
        </span>
      </div>
    </div>
  );
};

export default WordPoolSelector;