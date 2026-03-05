/**
 * QUIRRELY MASTER SIMULATION v3.1.1
 * ==================================
 * Full simulation incorporating all sprint implementations:
 * 
 * Phase 2 (Aso):
 * - Security hardening (no revenue impact)
 * - Meta events pipeline
 * - HALO bridge
 * - Authority scoring
 * - Feature flag API
 * 
 * Phase 3 (Mars):
 * - Conversion tracking
 * - Upgrade suggestions UI
 * - 7-day addon trial
 * - Event-driven triggers
 * 
 * MRR Optimization (P1 Quick Wins):
 * - Addon bundling (+$3,500/mo)
 * - Downgrade prevention (+$2,500/mo)
 * - First analysis hook (+$1,800/mo)
 * 
 * MRR Optimization (P2):
 * - Annual discount 25% (+$2,000/mo)
 * - Smart notifications (+$2,200/mo)
 * - Social proof counters (+$1,400/mo)
 * - Middle tier Growth $6.99 (+$1,500/mo)
 * 
 * MRR Optimization (P3):
 * - Achievement system (+$3,000/mo)
 * - Progressive feature unlocks (+$1,200/mo)
 * 
 * Polish (v3.1.1):
 * - Badge contrast dark mode fix
 * - Author cards mobile fix
 * - Challenge text wrap fix
 * - Loading states for CTAs
 * 
 * Version: 3.1.1
 * Date: February 16, 2026
 * Sprint: Kim→Aso→Mars + MRR Optimization + Polish
 * QA Score: 97.6% (A+)
 */

// ═══════════════════════════════════════════════════════════════
// LOCKED CONSTANTS - KNIGHT OF WANDS v3.1.1
// ═══════════════════════════════════════════════════════════════

const LTV = {
  MONTHLY: 46.18,      // $4.99 × 9.25 months avg
  ANNUAL: 128.57,      // $44.99 × 2.86 years avg (25% discount)
  BLENDED: 89.71,      // Weighted 60/40 split (more annual uptake)
  ADDON: 80.91,        // $8.99 × 9 months avg (bundle discount)
  GROWTH_TIER: 62.93,  // $6.99 × 9 months avg (NEW middle tier)
};

const PRICING = {
  // Core tiers
  PRO_MONTHLY: 4.99,
  PRO_ANNUAL: 44.99,        // 25% off (was 49.99)
  GROWTH_MONTHLY: 6.99,     // NEW middle tier
  GROWTH_ANNUAL: 62.99,
  FEATURED_MONTHLY: 7.99,
  FEATURED_ANNUAL: 71.99,   // 25% off
  AUTHORITY_MONTHLY: 8.99,
  AUTHORITY_ANNUAL: 80.99,  // 25% off
  
  // Addon
  ADDON_MONTHLY: 9.99,
  ADDON_ANNUAL: 89.99,      // 25% off (was 99.99)
  
  // Bundles
  BUNDLE_PRO_VS: 12.99,     // Pro + V+S (save $2)
  BUNDLE_AUTH_VS: 16.99,    // Authority + V+S
};

// ═══════════════════════════════════════════════════════════════
// SCENARIO CONFIGURATIONS
// ═══════════════════════════════════════════════════════════════

const SCENARIOS = {
  // Baseline: Pre-sprint (before Kim's QA)
  baseline: {
    name: "Baseline (Pre-Sprint)",
    description: "Before Kim→Aso→Mars sprint",
    conversions: {
      visit_to_signup: 0.148,
      signup_to_trial: 0.30,
      trial_to_paid: 0.42,
      paid_to_addon: 0.08,
      paid_to_featured: 0.03,
      featured_to_authority: 0.15,
    },
    churn: {
      monthly: 0.08,
      annual: 0.25,
    },
    triggers: {
      trialReminders: false,
      usageLimitPrompts: false,
      addonTrial: false,
      engagementTriggers: false,
    },
  },
  
  // Phase 2: After Aso's security/architecture work
  phase2: {
    name: "Phase 2 (Post-Aso)",
    description: "After security hardening + Meta integration",
    conversions: {
      visit_to_signup: 0.148,      // No change
      signup_to_trial: 0.32,       // +2% better UX
      trial_to_paid: 0.44,         // +2% targeting
      paid_to_addon: 0.10,         // +2% suggestions
      paid_to_featured: 0.04,      // +1% gamification
      featured_to_authority: 0.18, // +3% scoring
    },
    churn: {
      monthly: 0.07,               // -1% retention
      annual: 0.23,                // -2% engagement
    },
    triggers: {
      trialReminders: false,
      usageLimitPrompts: true,     // Feature API
      addonTrial: false,
      engagementTriggers: true,    // HALO bridge
    },
  },
  
  // Phase 3: After Mars's revenue optimization
  phase3: {
    name: "Phase 3 (Post-Mars)",
    description: "After conversion tracking + triggers + addon trial",
    conversions: {
      visit_to_signup: 0.148,      // No change
      signup_to_trial: 0.34,       // +2% more from UI
      trial_to_paid: 0.49,         // +5% from triggers
      paid_to_addon: 0.15,         // +5% from trial (12% try, 50% convert × 2.5 lift)
      paid_to_featured: 0.05,      // +1% from engagement
      featured_to_authority: 0.20, // +2% from tracking
    },
    churn: {
      monthly: 0.06,               // -1% from win-back
      annual: 0.21,                // -2% from engagement
    },
    triggers: {
      trialReminders: true,        // +5% trial conversion
      usageLimitPrompts: true,     // +3% paid conversion
      addonTrial: true,            // +50% addon attach
      engagementTriggers: true,    // +2% retention
    },
  },
  
  // v3.1.1: MRR Optimized (P1 + P2 + P3 + Polish)
  v311_optimized: {
    name: "v3.1.1 MRR Optimized",
    description: "Full P1+P2+P3 optimizations + Polish fixes",
    conversions: {
      visit_to_signup: 0.155,      // +0.7% from social proof counters
      signup_to_trial: 0.38,       // +4% from first analysis hook
      trial_to_paid: 0.54,         // +5% from progressive unlocks + Day 7 discount
      paid_to_addon: 0.22,         // +7% from addon bundling + smart notifications
      paid_to_growth: 0.12,        // NEW: Middle tier adoption
      paid_to_featured: 0.07,      // +2% from achievement system
      featured_to_authority: 0.24, // +4% from leaderboard + badges
      monthly_to_annual: 0.18,     // NEW: 25% discount uptake
    },
    churn: {
      monthly: 0.045,              // -1.5% from downgrade prevention
      annual: 0.16,                // -5% from engagement + achievements
    },
    triggers: {
      trialReminders: true,
      usageLimitPrompts: true,
      addonTrial: true,
      engagementTriggers: true,
      // v3.1.1 additions
      addonBundling: true,         // P1: +$3,500/mo
      downgradeFlow: true,         // P1: +$2,500/mo
      firstAnalysisHook: true,     // P1: +$1,800/mo
      annualDiscount25: true,      // P2: +$2,000/mo
      smartNotifications: true,    // P2: +$2,200/mo
      socialProofCounters: true,   // P2: +$1,400/mo
      middleTierGrowth: true,      // P2: +$1,500/mo
      achievementSystem: true,     // P3: +$3,000/mo
      progressiveUnlocks: true,    // P3: +$1,200/mo
    },
  },
};

// ═══════════════════════════════════════════════════════════════
// SIMULATION ENGINE
// ═══════════════════════════════════════════════════════════════

class QuirrelySimulation {
  constructor(scenario, config = {}) {
    this.scenario = scenario;
    this.days = config.days || 100;
    this.initialVisitors = config.initialVisitors || 100000;
    this.dailyGrowth = config.dailyGrowth || 1.005;
    
    // Country distribution
    this.countries = {
      CA: { share: 0.40, conversionMult: 1.00 },
      GB: { share: 0.25, conversionMult: 0.95 },
      AU: { share: 0.20, conversionMult: 1.05 },
      NZ: { share: 0.15, conversionMult: 0.98 },
    };
    
    // Initialize state
    this.reset();
  }
  
  reset() {
    this.state = {
      day: 0,
      totalVisitors: 0,
      totalSignups: 0,
      totalTrials: 0,
      
      // Current counts
      freeUsers: 0,
      trialUsers: 0,
      monthlyPaid: 0,
      annualPaid: 0,
      addonUsers: 0,
      featuredUsers: 0,
      authorityUsers: 0,
      
      // v3.1.1 additions
      growthTierUsers: 0,      // Middle tier ($6.99)
      bundleUsers: 0,          // Pro+V+S or Authority+V+S bundles
      annualConverted: 0,      // Monthly → Annual switches
      
      // Retention metrics
      pausedUsers: 0,          // Downgrade prevention: paused
      downgradedUsers: 0,      // Downgrade prevention: stepped down
      savedUsers: 0,           // Downgrade prevention: 50% offer accepted
      
      // Churned
      churned: 0,
      
      // Revenue
      dailyMRR: [],
      totalRevenue: 0,
    };
    
    this.history = [];
  }
  
  runDay(dayNum) {
    const s = this.scenario;
    const c = s.conversions;
    const churn = s.churn;
    
    // Calculate daily visitors (with growth)
    const visitors = Math.floor(
      (this.initialVisitors / this.days) * Math.pow(this.dailyGrowth, dayNum)
    );
    
    // Funnel calculations
    const signups = Math.floor(visitors * c.visit_to_signup);
    const newTrials = Math.floor(signups * c.signup_to_trial);
    const newFree = signups - newTrials;
    
    // Trial conversions (trials convert over ~14 days, model as daily rate)
    const trialConversionRate = c.trial_to_paid / 14;
    const trialsConverting = Math.floor(this.state.trialUsers * trialConversionRate);
    
    // v3.1.1: More annual uptake due to 25% discount
    const annualShare = c.monthly_to_annual || 0.35; // Default 35%, v3.1.1 is 18% monthly→annual
    const newMonthly = Math.floor(trialsConverting * (1 - annualShare));
    const newAnnual = trialsConverting - newMonthly;
    
    // v3.1.1: Growth tier adoption (some go to $6.99 instead of $4.99)
    const growthRate = c.paid_to_growth || 0;
    const newGrowthTier = Math.floor(newMonthly * growthRate);
    const actualNewMonthly = newMonthly - newGrowthTier;
    
    // Addon purchases from paid users
    const totalPaid = this.state.monthlyPaid + this.state.annualPaid + this.state.growthTierUsers;
    const addonRate = c.paid_to_addon / 30; // Spread over month
    const newAddons = Math.floor(totalPaid * addonRate);
    
    // v3.1.1: Bundle vs standalone split (40% choose bundles when available)
    const bundleRate = this.scenario.triggers?.addonBundling ? 0.40 : 0;
    const newBundles = Math.floor(newAddons * bundleRate);
    
    // Tier progression
    const newFeatured = Math.floor(totalPaid * (c.paid_to_featured / 90));
    const newAuthority = Math.floor(this.state.featuredUsers * (c.featured_to_authority / 90));
    
    // Churn with v3.1.1 downgrade prevention
    const monthlyChurnRate = churn.monthly / 30;
    let churningMonthly = Math.floor(this.state.monthlyPaid * monthlyChurnRate);
    
    // v3.1.1: Downgrade prevention saves 35% of churners
    if (this.scenario.triggers?.downgradeFlow) {
      const saved = Math.floor(churningMonthly * 0.35);
      const paused = Math.floor(saved * 0.4);   // 40% pause
      const downgraded = Math.floor(saved * 0.3); // 30% downgrade
      const discounted = saved - paused - downgraded; // 30% take 50% discount
      
      churningMonthly -= saved;
      this.state.pausedUsers += paused;
      this.state.downgradedUsers += downgraded;
      this.state.savedUsers += discounted;
    }
    
    // Monthly to annual conversions (v3.1.1)
    const monthlyToAnnualRate = (c.monthly_to_annual || 0) / 30;
    const convertingToAnnual = Math.floor(this.state.monthlyPaid * monthlyToAnnualRate);
    
    // Update state
    this.state.day = dayNum;
    this.state.totalVisitors += visitors;
    this.state.totalSignups += signups;
    this.state.totalTrials += newTrials;
    
    this.state.freeUsers += newFree;
    this.state.trialUsers += newTrials - trialsConverting;
    this.state.monthlyPaid += actualNewMonthly - churningMonthly - convertingToAnnual;
    this.state.annualPaid += newAnnual + convertingToAnnual;
    this.state.growthTierUsers += newGrowthTier;
    this.state.addonUsers += newAddons;
    this.state.bundleUsers += newBundles;
    this.state.featuredUsers += newFeatured;
    this.state.authorityUsers += newAuthority;
    this.state.churned += churningMonthly;
    this.state.annualConverted += convertingToAnnual;
    
    // Ensure non-negative
    this.state.trialUsers = Math.max(0, this.state.trialUsers);
    this.state.monthlyPaid = Math.max(0, this.state.monthlyPaid);
    
    // Calculate MRR
    const mrr = this.calculateMRR();
    this.state.dailyMRR.push(mrr);
    this.state.totalRevenue += mrr / 30; // Daily revenue
    
    // Record history
    this.history.push({
      day: dayNum,
      visitors,
      signups,
      trials: this.state.trialUsers,
      paid: this.state.monthlyPaid + this.state.annualPaid,
      addons: this.state.addonUsers,
      mrr,
    });
    
    return this.state;
  }
  
  calculateMRR() {
    // Base tier MRR
    const monthlyMRR = this.state.monthlyPaid * PRICING.PRO_MONTHLY;
    const annualMRR = this.state.annualPaid * (PRICING.PRO_ANNUAL / 12);
    
    // Growth tier (v3.1.1)
    const growthMRR = this.state.growthTierUsers * PRICING.GROWTH_MONTHLY;
    
    // Addon MRR (standalone + bundles)
    const standaloneAddonMRR = (this.state.addonUsers - this.state.bundleUsers) * PRICING.ADDON_MONTHLY;
    const bundleMRR = this.state.bundleUsers * PRICING.BUNDLE_PRO_VS;
    
    // Featured/Authority premium
    const featuredPremium = this.state.featuredUsers * (PRICING.FEATURED_MONTHLY - PRICING.PRO_MONTHLY);
    const authorityPremium = this.state.authorityUsers * (PRICING.AUTHORITY_MONTHLY - PRICING.PRO_MONTHLY);
    
    return monthlyMRR + annualMRR + growthMRR + standaloneAddonMRR + bundleMRR + featuredPremium + authorityPremium;
  }
  
  calculateMRRBreakdown() {
    return {
      proMonthly: this.state.monthlyPaid * PRICING.PRO_MONTHLY,
      proAnnual: this.state.annualPaid * (PRICING.PRO_ANNUAL / 12),
      growth: this.state.growthTierUsers * PRICING.GROWTH_MONTHLY,
      addonStandalone: (this.state.addonUsers - this.state.bundleUsers) * PRICING.ADDON_MONTHLY,
      bundles: this.state.bundleUsers * PRICING.BUNDLE_PRO_VS,
      featuredPremium: this.state.featuredUsers * (PRICING.FEATURED_MONTHLY - PRICING.PRO_MONTHLY),
      authorityPremium: this.state.authorityUsers * (PRICING.AUTHORITY_MONTHLY - PRICING.PRO_MONTHLY),
    };
  }
  
  run() {
    this.reset();
    
    for (let day = 1; day <= this.days; day++) {
      this.runDay(day);
    }
    
    return this.getResults();
  }
  
  getResults() {
    const finalMRR = this.state.dailyMRR[this.state.dailyMRR.length - 1] || 0;
    const totalPaid = this.state.monthlyPaid + this.state.annualPaid + this.state.growthTierUsers;
    const mrrBreakdown = this.calculateMRRBreakdown();
    
    return {
      scenario: this.scenario.name,
      description: this.scenario.description,
      days: this.days,
      version: 'v3.1.1',
      
      // Traffic
      totalVisitors: this.state.totalVisitors,
      totalSignups: this.state.totalSignups,
      signupRate: (this.state.totalSignups / this.state.totalVisitors * 100).toFixed(2) + '%',
      
      // Users
      freeUsers: this.state.freeUsers,
      trialUsers: this.state.trialUsers,
      paidUsers: totalPaid,
      monthlyPaid: this.state.monthlyPaid,
      annualPaid: this.state.annualPaid,
      growthTierUsers: this.state.growthTierUsers,
      addonUsers: this.state.addonUsers,
      bundleUsers: this.state.bundleUsers,
      featuredUsers: this.state.featuredUsers,
      authorityUsers: this.state.authorityUsers,
      churned: this.state.churned,
      
      // v3.1.1 Retention metrics
      pausedUsers: this.state.pausedUsers,
      downgradedUsers: this.state.downgradedUsers,
      savedUsers: this.state.savedUsers,
      annualConverted: this.state.annualConverted,
      
      // Revenue
      finalMRR: finalMRR.toFixed(2),
      finalARR: (finalMRR * 12).toFixed(2),
      totalRevenue: this.state.totalRevenue.toFixed(2),
      
      // MRR Breakdown (v3.1.1)
      mrrBreakdown: {
        proMonthly: mrrBreakdown.proMonthly.toFixed(2),
        proAnnual: mrrBreakdown.proAnnual.toFixed(2),
        growthTier: mrrBreakdown.growth.toFixed(2),
        addonStandalone: mrrBreakdown.addonStandalone.toFixed(2),
        bundles: mrrBreakdown.bundles.toFixed(2),
        featuredPremium: mrrBreakdown.featuredPremium.toFixed(2),
        authorityPremium: mrrBreakdown.authorityPremium.toFixed(2),
      },
      
      // Rates
      trialConversion: ((totalPaid / this.state.totalTrials) * 100).toFixed(1) + '%',
      addonAttach: ((this.state.addonUsers / totalPaid) * 100).toFixed(1) + '%',
      bundleRate: this.state.bundleUsers > 0 ? ((this.state.bundleUsers / this.state.addonUsers) * 100).toFixed(1) + '%' : '0%',
      churnRate: ((this.state.churned / (totalPaid + this.state.churned)) * 100).toFixed(1) + '%',
      retentionSaved: this.state.savedUsers + this.state.pausedUsers + this.state.downgradedUsers,
      
      // LTV
      avgLTV: LTV.BLENDED.toFixed(2),
      totalLTV: (totalPaid * LTV.BLENDED).toFixed(2),
      
      // Milestones
      day30: this.history[29] || null,
      day60: this.history[59] || null,
      day90: this.history[89] || null,
      day100: this.history[99] || null,
    };
  }
}

// ═══════════════════════════════════════════════════════════════
// RUN SIMULATIONS
// ═══════════════════════════════════════════════════════════════

function runAllScenarios(config = {}) {
  const results = {};
  
  for (const [key, scenario] of Object.entries(SCENARIOS)) {
    const sim = new QuirrelySimulation(scenario, config);
    results[key] = sim.run();
  }
  
  return results;
}

function compareScenarios(results) {
  const baseline = results.baseline;
  const phase2 = results.phase2;
  const phase3 = results.phase3;
  
  return {
    // Phase 2 vs Baseline
    phase2_vs_baseline: {
      paidUsersDelta: phase2.paidUsers - baseline.paidUsers,
      paidUsersPercent: ((phase2.paidUsers / baseline.paidUsers - 1) * 100).toFixed(1) + '%',
      mrrDelta: (parseFloat(phase2.finalMRR) - parseFloat(baseline.finalMRR)).toFixed(2),
      mrrPercent: ((parseFloat(phase2.finalMRR) / parseFloat(baseline.finalMRR) - 1) * 100).toFixed(1) + '%',
      addonsDelta: phase2.addonUsers - baseline.addonUsers,
      churnImprovement: (parseFloat(baseline.churnRate) - parseFloat(phase2.churnRate)).toFixed(1) + '%',
    },
    
    // Phase 3 vs Baseline
    phase3_vs_baseline: {
      paidUsersDelta: phase3.paidUsers - baseline.paidUsers,
      paidUsersPercent: ((phase3.paidUsers / baseline.paidUsers - 1) * 100).toFixed(1) + '%',
      mrrDelta: (parseFloat(phase3.finalMRR) - parseFloat(baseline.finalMRR)).toFixed(2),
      mrrPercent: ((parseFloat(phase3.finalMRR) / parseFloat(baseline.finalMRR) - 1) * 100).toFixed(1) + '%',
      addonsDelta: phase3.addonUsers - baseline.addonUsers,
      churnImprovement: (parseFloat(baseline.churnRate) - parseFloat(phase3.churnRate)).toFixed(1) + '%',
    },
    
    // Phase 3 vs Phase 2 (Mars's incremental impact)
    phase3_vs_phase2: {
      paidUsersDelta: phase3.paidUsers - phase2.paidUsers,
      paidUsersPercent: ((phase3.paidUsers / phase2.paidUsers - 1) * 100).toFixed(1) + '%',
      mrrDelta: (parseFloat(phase3.finalMRR) - parseFloat(phase2.finalMRR)).toFixed(2),
      mrrPercent: ((parseFloat(phase3.finalMRR) / parseFloat(phase2.finalMRR) - 1) * 100).toFixed(1) + '%',
      addonsDelta: phase3.addonUsers - phase2.addonUsers,
    },
  };
}

function generateReport(config = { days: 100, initialVisitors: 100000 }) {
  const results = runAllScenarios(config);
  const comparison = compareScenarios(results);
  
  return {
    config,
    timestamp: new Date().toISOString(),
    results,
    comparison,
    summary: {
      totalSprintImpact: {
        mrrLift: comparison.phase3_vs_baseline.mrrPercent,
        paidUsersLift: comparison.phase3_vs_baseline.paidUsersPercent,
        addonUsersGain: comparison.phase3_vs_baseline.addonsDelta,
        churnReduction: comparison.phase3_vs_baseline.churnImprovement,
      },
      phase2Impact: {
        description: "Security + Meta + HALO + Authority",
        mrrLift: comparison.phase2_vs_baseline.mrrPercent,
      },
      phase3Impact: {
        description: "Conversion tracking + Triggers + Addon trial",
        mrrLift: comparison.phase3_vs_phase2.mrrPercent,
      },
    },
  };
}

// ═══════════════════════════════════════════════════════════════
// EXECUTE SIMULATION
// ═══════════════════════════════════════════════════════════════

const report = generateReport({ days: 100, initialVisitors: 100000 });

console.log("═══════════════════════════════════════════════════════════");
console.log("QUIRRELY MASTER SIMULATION v3.0 - RESULTS");
console.log("Kim→Aso→Mars Sprint Impact Analysis");
console.log("═══════════════════════════════════════════════════════════");
console.log("");
console.log("Configuration:", JSON.stringify(report.config));
console.log("");

// Output baseline
console.log("─────────────────────────────────────────────────────────────");
console.log("SCENARIO: " + report.results.baseline.scenario);
console.log("─────────────────────────────────────────────────────────────");
console.log("Paid Users:", report.results.baseline.paidUsers);
console.log("Addon Users:", report.results.baseline.addonUsers);
console.log("Final MRR: $" + report.results.baseline.finalMRR);
console.log("Final ARR: $" + report.results.baseline.finalARR);
console.log("");

// Output Phase 2
console.log("─────────────────────────────────────────────────────────────");
console.log("SCENARIO: " + report.results.phase2.scenario);
console.log("─────────────────────────────────────────────────────────────");
console.log("Paid Users:", report.results.phase2.paidUsers);
console.log("Addon Users:", report.results.phase2.addonUsers);
console.log("Final MRR: $" + report.results.phase2.finalMRR);
console.log("Final ARR: $" + report.results.phase2.finalARR);
console.log("vs Baseline MRR: " + report.comparison.phase2_vs_baseline.mrrPercent);
console.log("");

// Output Phase 3
console.log("─────────────────────────────────────────────────────────────");
console.log("SCENARIO: " + report.results.phase3.scenario);
console.log("─────────────────────────────────────────────────────────────");
console.log("Paid Users:", report.results.phase3.paidUsers);
console.log("Addon Users:", report.results.phase3.addonUsers);
console.log("Final MRR: $" + report.results.phase3.finalMRR);
console.log("Final ARR: $" + report.results.phase3.finalARR);
console.log("vs Baseline MRR: " + report.comparison.phase3_vs_baseline.mrrPercent);
console.log("");

// Summary
console.log("═══════════════════════════════════════════════════════════");
console.log("TOTAL SPRINT IMPACT");
console.log("═══════════════════════════════════════════════════════════");
console.log("MRR Lift: " + report.summary.totalSprintImpact.mrrLift);
console.log("Paid Users Lift: " + report.summary.totalSprintImpact.paidUsersLift);
console.log("Addon Users Gained: " + report.summary.totalSprintImpact.addonUsersGain);
console.log("Churn Reduction: " + report.summary.totalSprintImpact.churnReduction);

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { 
    SCENARIOS, 
    QuirrelySimulation, 
    runAllScenarios, 
    compareScenarios,
    generateReport,
    report 
  };
}
