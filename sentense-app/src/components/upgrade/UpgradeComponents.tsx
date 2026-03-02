/**
 * QUIRRELY UPGRADE COMPONENTS v1.0
 * UI components for displaying upgrade prompts and suggestions.
 * 
 * Components:
 * - UpgradeBanner: Dismissible banner for sidebar/header
 * - UpgradeModal: Full modal for upgrade flow
 * - UsageLimitWarning: Warning when approaching limits
 * - AddonPrompt: Voice + Style addon promotion
 */

import React, { useState, useEffect } from 'react';
import { X, Zap, TrendingUp, Mic, Crown, ArrowRight, AlertCircle } from 'lucide-react';
import { useFeatures, UpgradeSuggestion } from '@/hooks/useFeatures';
import { ConversionTracker, useUpgradePromptTracking } from '@/lib/conversion-tracker';

// ═══════════════════════════════════════════════════════════════════════════
// UPGRADE BANNER
// ═══════════════════════════════════════════════════════════════════════════

interface UpgradeBannerProps {
  suggestion?: UpgradeSuggestion;
  onDismiss?: () => void;
  variant?: 'default' | 'compact' | 'prominent';
}

export const UpgradeBanner: React.FC<UpgradeBannerProps> = ({
  suggestion,
  onDismiss,
  variant = 'default',
}) => {
  const { upgradeSuggestions, tier } = useFeatures();
  const [dismissed, setDismissed] = useState(false);
  
  // Use first suggestion if none provided
  const activeSuggestion = suggestion || upgradeSuggestions[0];
  
  // Track prompt visibility
  const { trackClick, trackDismiss } = useUpgradePromptTracking(
    `banner_${activeSuggestion?.type || 'default'}`,
    !dismissed && !!activeSuggestion
  );
  
  if (dismissed || !activeSuggestion) return null;
  
  const handleDismiss = () => {
    trackDismiss();
    setDismissed(true);
    onDismiss?.();
  };
  
  const handleClick = () => {
    trackClick();
    // Navigate to upgrade page
    window.location.href = `/settings/subscription?upgrade=${activeSuggestion.type}`;
  };
  
  const icons = {
    trial: Zap,
    pro: TrendingUp,
    addon: Mic,
    featured: Crown,
  };
  const Icon = icons[activeSuggestion.type as keyof typeof icons] || Zap;
  
  if (variant === 'compact') {
    return (
      <div className="bg-gradient-to-r from-coral-50 to-amber-50 border border-coral-200 rounded-lg p-3 flex items-center gap-3">
        <Icon className="w-5 h-5 text-coral-600 flex-shrink-0" />
        <span className="text-sm text-coral-800 flex-1">{activeSuggestion.title}</span>
        <button
          onClick={handleClick}
          className="text-xs font-medium text-coral-600 hover:text-coral-700"
        >
          {activeSuggestion.cta}
        </button>
        <button onClick={handleDismiss} className="text-coral-400 hover:text-coral-600">
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }
  
  if (variant === 'prominent') {
    return (
      <div className="bg-gradient-to-r from-coral-500 to-amber-500 rounded-xl p-6 text-white relative overflow-hidden">
        <button
          onClick={handleDismiss}
          className="absolute top-4 right-4 text-white/70 hover:text-white"
        >
          <X className="w-5 h-5" />
        </button>
        <div className="flex items-start gap-4">
          <div className="bg-white/20 rounded-full p-3">
            <Icon className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold mb-1">{activeSuggestion.title}</h3>
            <p className="text-white/90 text-sm mb-4">{activeSuggestion.description}</p>
            <button
              onClick={handleClick}
              className="bg-white text-coral-600 px-4 py-2 rounded-lg font-medium text-sm hover:bg-coral-50 transition-colors inline-flex items-center gap-2"
            >
              {activeSuggestion.cta}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  // Default variant
  return (
    <div className="bg-coral-50 border border-coral-200 rounded-lg p-4 flex items-center gap-4">
      <div className="bg-coral-100 rounded-full p-2">
        <Icon className="w-5 h-5 text-coral-600" />
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium text-coral-800">{activeSuggestion.title}</p>
        <p className="text-xs text-coral-600">{activeSuggestion.description}</p>
      </div>
      <button
        onClick={handleClick}
        className="bg-coral-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-coral-600 transition-colors"
      >
        {activeSuggestion.cta}
      </button>
      <button onClick={handleDismiss} className="text-coral-400 hover:text-coral-600">
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// UPGRADE MODAL
// ═══════════════════════════════════════════════════════════════════════════

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetTier?: string;
  feature?: string;
}

export const UpgradeModal: React.FC<UpgradeModalProps> = ({
  isOpen,
  onClose,
  targetTier = 'pro',
  feature,
}) => {
  const { trackClick, trackDismiss } = useUpgradePromptTracking(
    `modal_${targetTier}`,
    isOpen
  );
  
  if (!isOpen) return null;
  
  const handleUpgrade = () => {
    trackClick();
    window.location.href = `/settings/subscription?upgrade=${targetTier}`;
  };
  
  const handleClose = () => {
    trackDismiss();
    onClose();
  };
  
  const tierDetails = {
    pro: {
      name: 'Pro',
      price: '$2.99/mo',
      features: [
        'Unlimited voice analyses',
        'Save all your results',
        'Full comparison history',
        'Advanced analytics',
        'Priority support',
      ],
    },
    curator: {
      name: 'Curator',
      price: '$2.99/mo',
      features: [
        'Create reading paths',
        'Curate content collections',
        'Build follower base',
        'Curator analytics',
        'Featured path eligibility',
      ],
    },
  };
  
  const tier = tierDetails[targetTier as keyof typeof tierDetails] || tierDetails.pro;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-xl">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-coral-100 rounded-full p-3">
              <Crown className="w-6 h-6 text-coral-600" />
            </div>
            <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Upgrade to {tier.name}
          </h2>
          
          {feature && (
            <p className="text-coral-600 text-sm mb-4">
              Unlock <strong>{feature}</strong> and more
            </p>
          )}
          
          <p className="text-gray-600 mb-6">
            Get full access to all {tier.name} features for just {tier.price}
          </p>
          
          <ul className="space-y-3 mb-6">
            {tier.features.map((f, i) => (
              <li key={i} className="flex items-center gap-3 text-gray-700">
                <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                {f}
              </li>
            ))}
          </ul>
          
          <div className="space-y-3">
            <button
              onClick={handleUpgrade}
              className="w-full bg-coral-500 text-white py-3 rounded-xl font-semibold hover:bg-coral-600 transition-colors"
            >
              Upgrade to {tier.name}
            </button>
            <button
              onClick={handleClose}
              className="w-full text-gray-500 py-2 text-sm hover:text-gray-700"
            >
              Maybe later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// USAGE LIMIT WARNING
// ═══════════════════════════════════════════════════════════════════════════

interface UsageLimitWarningProps {
  used: number;
  limit: number;
  onUpgrade?: () => void;
}

export const UsageLimitWarning: React.FC<UsageLimitWarningProps> = ({
  used,
  limit,
  onUpgrade,
}) => {
  const remaining = limit - used;
  const percentage = (used / limit) * 100;
  
  // Track when shown at different thresholds
  useEffect(() => {
    if (percentage >= 80 && percentage < 100) {
      ConversionTracker.trackUpgradePrompt('limit_warning_80', 'shown');
    } else if (percentage >= 100) {
      ConversionTracker.trackAnalysisLimitReached(limit, used);
    }
  }, [percentage, limit, used]);
  
  if (percentage < 80) return null;
  
  const isAtLimit = percentage >= 100;
  
  return (
    <div className={`rounded-lg p-4 ${isAtLimit ? 'bg-red-50 border border-red-200' : 'bg-amber-50 border border-amber-200'}`}>
      <div className="flex items-start gap-3">
        <AlertCircle className={`w-5 h-5 flex-shrink-0 ${isAtLimit ? 'text-red-500' : 'text-amber-500'}`} />
        <div className="flex-1">
          <p className={`font-medium ${isAtLimit ? 'text-red-800' : 'text-amber-800'}`}>
            {isAtLimit ? 'Daily limit reached' : `${remaining} analyses remaining today`}
          </p>
          <p className={`text-sm mt-1 ${isAtLimit ? 'text-red-600' : 'text-amber-600'}`}>
            {isAtLimit 
              ? 'Upgrade to Pro for unlimited analyses'
              : 'Upgrade to Pro for unlimited daily analyses'
            }
          </p>
          
          {/* Progress bar */}
          <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${isAtLimit ? 'bg-red-500' : 'bg-amber-500'}`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{used} / {limit} used</p>
          
          {onUpgrade && (
            <button
              onClick={() => {
                ConversionTracker.trackUpgradePrompt('limit_warning', 'clicked');
                onUpgrade();
              }}
              className={`mt-3 px-4 py-2 rounded-lg text-sm font-medium ${
                isAtLimit 
                  ? 'bg-red-500 text-white hover:bg-red-600' 
                  : 'bg-amber-500 text-white hover:bg-amber-600'
              }`}
            >
              Upgrade to Pro
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// ADDON PROMPT (Voice + Style)
// ═══════════════════════════════════════════════════════════════════════════

interface AddonPromptProps {
  variant?: 'inline' | 'card' | 'modal';
  onDismiss?: () => void;
}

export const AddonPrompt: React.FC<AddonPromptProps> = ({
  variant = 'card',
  onDismiss,
}) => {
  const [dismissed, setDismissed] = useState(false);
  const { trackClick, trackDismiss } = useUpgradePromptTracking(
    'addon_voice_style',
    !dismissed
  );
  
  if (dismissed) return null;
  
  const handleDismiss = () => {
    trackDismiss();
    setDismissed(true);
    onDismiss?.();
  };
  
  const handlePurchase = () => {
    trackClick();
    window.location.href = '/settings/addons?addon=voice_style';
  };
  
  if (variant === 'inline') {
    return (
      <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
        <Mic className="w-5 h-5 text-purple-600" />
        <span className="text-sm text-purple-800 flex-1">
          Unlock deep voice analysis with Voice + Style
        </span>
        <button
          onClick={handlePurchase}
          className="text-sm font-medium text-purple-600 hover:text-purple-700"
        >
          $4.99/mo
        </button>
      </div>
    );
  }
  
  if (variant === 'modal') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl max-w-md w-full shadow-xl p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-purple-100 rounded-full p-3">
              <Mic className="w-6 h-6 text-purple-600" />
            </div>
            <button onClick={handleDismiss} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Voice + Style
          </h2>
          <p className="text-gray-600 mb-6">
            Deep voice analysis with style insights, evolution tracking, and personalized recommendations.
          </p>
          
          <ul className="space-y-3 mb-6">
            {[
              'Full voice profile analysis',
              'Writing style breakdown',
              'Voice evolution over time',
              'Personalized writing tips',
              'Compare with famous authors',
            ].map((f, i) => (
              <li key={i} className="flex items-center gap-3 text-gray-700">
                <div className="w-5 h-5 bg-purple-100 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                {f}
              </li>
            ))}
          </ul>
          
          <button
            onClick={handlePurchase}
            className="w-full bg-purple-500 text-white py-3 rounded-xl font-semibold hover:bg-purple-600 transition-colors"
          >
            Add for $4.99/mo
          </button>
        </div>
      </div>
    );
  }
  
  // Card variant (default)
  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-5 border border-purple-200 relative">
      <button
        onClick={handleDismiss}
        className="absolute top-3 right-3 text-purple-300 hover:text-purple-500"
      >
        <X className="w-4 h-4" />
      </button>
      
      <div className="flex items-start gap-4">
        <div className="bg-purple-100 rounded-full p-3">
          <Mic className="w-6 h-6 text-purple-600" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-purple-900 mb-1">Voice + Style</h3>
          <p className="text-sm text-purple-700 mb-3">
            Deep voice analysis with style insights and evolution tracking.
          </p>
          <button
            onClick={handlePurchase}
            className="bg-purple-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-600 transition-colors inline-flex items-center gap-2"
          >
            Add for $4.99/mo
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export default {
  UpgradeBanner,
  UpgradeModal,
  UsageLimitWarning,
  AddonPrompt,
};
