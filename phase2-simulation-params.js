/**
 * QUIRRELY PHASE 2 SIMULATION PARAMETERS
 * =======================================
 * Commercial impact parameters from Phase 2 implementation.
 * 
 * These parameters model the expected lift from:
 * - Meta events pipeline (conversion triggers)
 * - HALO bridge (ML personalization)
 * - Authority scoring (gamification)
 * - Feature flag API (better targeting)
 * 
 * Version: 1.0.0
 * Date: February 15, 2026
 * Author: Mars (Marketing & Revenue Systems Lead)
 */

// ═══════════════════════════════════════════════════════════════
// PHASE 2 IMPACT MULTIPLIERS
// ═══════════════════════════════════════════════════════════════

const PHASE2_IMPACT = {
  // Security changes (no revenue impact)
  security: {
    countryGateImpact: 0,          // No conversion change
    httpOnlyCookieImpact: 0,       // No UX change
    apiAuditImpact: 0,             // No user-facing change
  },
  
  // Meta events enable conversion optimization
  metaEvents: {
    trialExpirationTrigger: 0.05,  // +5% trial conversion from email triggers
    usageLimitTrigger: 0.03,       // +3% conversion from limit warnings
    engagementTrigger: 0.02,       // +2% from high-engagement prompts
    churnPrevention: 0.02,         // -2% churn from win-back triggers
  },
  
  // HALO enables ML-driven personalization
  halo: {
    contentRecommendations: 0.10,  // +10% engagement from recommendations
    writerMatchSocialProof: 0.03,  // +3% conversion from "writers like you"
    voiceEvolutionRetention: 0.05, // +5% retention from progress tracking
    personalizedUpgrades: 0.02,    // +2% upsell from personalized prompts
  },
  
  // Authority scoring enables gamification
  authority: {
    leaderboardEngagement: 0.15,   // +15% authority feature usage
    scoreMilestones: 0.08,         // +8% progression rate
    peerComparison: 0.05,          // +5% satisfaction/retention
    badgeUnlocks: 0.03,            // +3% continued engagement
  },
  
  // Feature flag API enables better targeting
  featureApi: {
    dynamicUpgradeSuggestions: 0.02,  // +2% from relevant prompts
    usageLimitVisibility: 0.03,       // +3% from urgency
    sectionRestrictions: 0.01,        // +1% from clear value prop
  },
};

// ═══════════════════════════════════════════════════════════════
// UPDATED CONVERSION RATES (POST-PHASE 2)
// ═══════════════════════════════════════════════════════════════

const PRE_PHASE2_CONVERSIONS = {
  visit_to_signup: 0.148,
  signup_to_trial: 0.30,
  trial_to_paid: 0.42,
  paid_to_addon: 0.08,
  paid_to_featured: 0.03,
  featured_to_authority: 0.15,
  monthly_churn: 0.08,
  annual_churn: 0.25,
};

const POST_PHASE2_CONVERSIONS = {
  visit_to_signup: 0.148,      // No change (security doesn't affect)
  signup_to_trial: 0.32,       // +0.02 from better UX
  trial_to_paid: 0.44,         // +0.02 from targeting
  paid_to_addon: 0.10,         // +0.02 from suggestions
  paid_to_featured: 0.04,      // +0.01 from gamification
  featured_to_authority: 0.18, // +0.03 from scoring
  monthly_churn: 0.07,         // -0.01 from retention
  annual_churn: 0.23,          // -0.02 from engagement
};

// ═══════════════════════════════════════════════════════════════
// ADDON ECONOMICS
// ═══════════════════════════════════════════════════════════════

const ADDON_ECONOMICS = {
  voiceStyle: {
    price: 4.99,
    monthlyChurn: 0.10,
    avgLifespanMonths: 9,
    ltv: 44.91,  // $4.99 × 9 months
    
    // Cross-sell rates by tier
    crossSellByTier: {
      free: 0.02,       // 2% free users buy addon
      trial: 0.05,      // 5% trial users
      pro: 0.10,        // 10% pro users (up from 8%)
      curator: 0.08,    // 8% curator users
      featured: 0.20,   // 20% featured users (up from 15%)
      authority: 0.35,  // 35% authority users (up from 25%)
    },
  },
};

// ═══════════════════════════════════════════════════════════════
// GAP CLOSURE SCENARIOS
// ═══════════════════════════════════════════════════════════════

const GAP_CLOSURES = {
  // GAP-001: Add addon trial
  addonTrial: {
    enabled: false,
    trialDays: 7,
    trialToPayRate: 0.50,  // 50% of trial users convert
    attachRateLift: 0.50,  // +50% more users try addon
    expectedNewAttach: 0.15, // 15% attach rate (up from 10%)
    monthlyRevenueDelta: 2000, // Per 10K users
  },
  
  // GAP-002: Increase annual discount
  annualDiscount: {
    enabled: false,
    currentDiscount: 0.16,  // 16% ($30 vs $35.88)
    newDiscount: 0.20,      // 20% ($28.70)
    newAnnualPrice: 28.70,
    splitShift: { monthly: 0.55, annual: 0.45 }, // From 65/35
    initialRevenueDelta: -1500, // Lower price
    longTermLtvGain: 500,       // Better retention
  },
  
  // GAP-003: Referral program
  referralProgram: {
    enabled: false,
    giveAmount: 1.00,
    getAmount: 1.00,
    referralRateLift: 0.20, // +20% viral coefficient
    monthlyReferredRevenue: 1000,
    cac: 2.00, // Cost per referred user
  },
  
  // GAP-004: Win-back flow
  winBackFlow: {
    enabled: false,
    emailSequenceLength: 5,
    discountOffer: 0.50,    // 50% off return
    recoveryRate: 0.10,     // 10% of churned return
    monthlyRecovered: 300,
  },
  
  // GAP-005: Usage-based upgrade prompts
  usageBasedPrompts: {
    enabled: false,
    triggers: ['5th_analysis', 'comparison_limit', 'history_limit'],
    engagementLift: 0.15,   // +15% prompt engagement
    conversionLift: 0.05,   // +5% conversion rate
    monthlyRevenueDelta: 500,
  },
};

// ═══════════════════════════════════════════════════════════════
// COUNTRY-SPECIFIC PARAMETERS
// ═══════════════════════════════════════════════════════════════

const COUNTRY_PARAMS = {
  CA: {
    share: 0.40,
    conversionRate: 0.028,
    mrrContribution: 0.42,
    opportunities: ['SEO priority', 'Local partnerships'],
  },
  GB: {
    share: 0.25,
    conversionRate: 0.025,
    mrrContribution: 0.24,
    opportunities: ['Writing blog partnerships', 'UK media'],
  },
  AU: {
    share: 0.20,
    conversionRate: 0.029,
    mrrContribution: 0.22,
    opportunities: ['Highest conversion - paid ads', 'AU content'],
  },
  NZ: {
    share: 0.15,
    conversionRate: 0.026,
    mrrContribution: 0.12,
    opportunities: ['Underserved market', 'NZ-specific content'],
  },
};

// ═══════════════════════════════════════════════════════════════
// TIER PROGRESSION MODEL
// ═══════════════════════════════════════════════════════════════

const TIER_PROGRESSION = {
  prePhase2: {
    free_to_trial: 0.30,
    trial_to_pro: 0.42,
    pro_to_featured: 0.03,
    featured_to_authority: 0.15,
  },
  postPhase2: {
    free_to_trial: 0.32,       // +2% better UX
    trial_to_pro: 0.44,        // +2% targeting
    pro_to_featured: 0.04,     // +1% gamification
    featured_to_authority: 0.18, // +3% scoring
  },
  withGapClosures: {
    free_to_trial: 0.35,       // +3% more with addon trial
    trial_to_pro: 0.48,        // +4% with triggers
    pro_to_featured: 0.06,     // +2% with referrals
    featured_to_authority: 0.22, // +4% with full gamification
  },
};

// ═══════════════════════════════════════════════════════════════
// SIMULATION HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

/**
 * Calculate projected MRR with Phase 2 parameters
 */
function calculatePhase2MRR(visitors, params = POST_PHASE2_CONVERSIONS) {
  const signups = Math.floor(visitors * params.visit_to_signup);
  const trials = Math.floor(signups * params.signup_to_trial);
  const paidUsers = Math.floor(trials * params.trial_to_paid);
  
  // Split monthly/annual (65/35)
  const monthlyUsers = Math.floor(paidUsers * 0.65);
  const annualUsers = paidUsers - monthlyUsers;
  
  // Base MRR
  const monthlyMRR = monthlyUsers * 2.99;
  const annualMRR = annualUsers * (30 / 12);
  
  // Addon MRR
  const addonUsers = Math.floor(paidUsers * params.paid_to_addon);
  const addonMRR = addonUsers * 4.99;
  
  return {
    signups,
    trials,
    paidUsers,
    monthlyUsers,
    annualUsers,
    addonUsers,
    monthlyMRR,
    annualMRR,
    addonMRR,
    totalMRR: monthlyMRR + annualMRR + addonMRR,
    arr: (monthlyMRR + annualMRR + addonMRR) * 12,
  };
}

/**
 * Compare pre and post Phase 2 projections
 */
function comparePhase2Impact(visitors) {
  const pre = calculatePhase2MRR(visitors, PRE_PHASE2_CONVERSIONS);
  const post = calculatePhase2MRR(visitors, POST_PHASE2_CONVERSIONS);
  
  return {
    visitors,
    prePhase2: pre,
    postPhase2: post,
    delta: {
      paidUsers: post.paidUsers - pre.paidUsers,
      addonUsers: post.addonUsers - pre.addonUsers,
      mrr: post.totalMRR - pre.totalMRR,
      arr: post.arr - pre.arr,
      mrrPercent: ((post.totalMRR / pre.totalMRR) - 1) * 100,
    },
  };
}

// ═══════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PHASE2_IMPACT,
    PRE_PHASE2_CONVERSIONS,
    POST_PHASE2_CONVERSIONS,
    ADDON_ECONOMICS,
    GAP_CLOSURES,
    COUNTRY_PARAMS,
    TIER_PROGRESSION,
    calculatePhase2MRR,
    comparePhase2Impact,
  };
}

// Browser global
if (typeof window !== 'undefined') {
  window.Phase2Params = {
    PHASE2_IMPACT,
    PRE_PHASE2_CONVERSIONS,
    POST_PHASE2_CONVERSIONS,
    ADDON_ECONOMICS,
    GAP_CLOSURES,
    COUNTRY_PARAMS,
    TIER_PROGRESSION,
    calculatePhase2MRR,
    comparePhase2Impact,
  };
}
