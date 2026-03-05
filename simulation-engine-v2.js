/**
 * QUIRRELY SIMULATION ENGINE v2.1
 * ================================
 * Enhanced growth simulation with:
 * - Cohort-based modeling
 * - Churn rate integration
 * - Fixed viral attribution (including pre-signup card shares)
 * - Source-based conversion rates
 * - CAC/LTV metrics
 * - Country distribution
 * 
 * Version: 2.1.0
 * Date: February 10, 2026
 */

// ═══════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════

const DEFAULT_CONFIG_V2 = {
  // Simulation parameters
  days: 100,
  initialVisitors: 100000,
  
  // Country distribution (4 target markets)
  countryDistribution: {
    CA: { share: 0.40, name: 'Canada', flag: '🍁' },
    UK: { share: 0.25, name: 'United Kingdom', flag: '🇬🇧' },
    AU: { share: 0.20, name: 'Australia', flag: '🇦🇺' },
    NZ: { share: 0.15, name: 'New Zealand', flag: '🇳🇿' }
  },
  
  // Featured Writer standard (LOCKED)
  featuredWriterContentPct: 0.85,
  
  // Traffic distribution by source
  trafficSources: {
    organic: { share: 0.30, dailyGrowth: 1.005 },
    paid: { share: 0.15, dailyGrowth: 1.002, cpc: 0.50 },
    direct: { share: 0.20, dailyGrowth: 1.003 },
    referral: { share: 0.20, dailyGrowth: 1.008 },
    social: { share: 0.10, dailyGrowth: 1.004 },
    email: { share: 0.05, dailyGrowth: 1.010 }
  },
  
  // Conversion rates by source
  conversionBySource: {
    organic: { signup: 0.17, trial: 0.30, paid: 0.38 },
    paid: { signup: 0.11, trial: 0.25, paid: 0.32 },
    direct: { signup: 0.14, trial: 0.28, paid: 0.35 },
    referral: { signup: 0.29, trial: 0.40, paid: 0.48 },
    social: { signup: 0.13, trial: 0.26, paid: 0.33 },
    email: { signup: 0.39, trial: 0.45, paid: 0.52 }
  },
  
  // Viral coefficients
  viral: {
    // PRE-SIGNUP: Results card sharing (NEW)
    resultsCardShareRate: 0.10,      // 10% of test completers share their card
    resultsCardClickRate: 0.25,      // 25% of shares result in a visit
    
    // POST-SIGNUP: Newsletter
    newsletterForwardRate: 0.122,    // 12.2% of subscribers forward
    newsletterClickRate: 0.35,       // 35% of forwards result in click
    
    // PRO USERS
    userReferralRate: 0.08,          // 8% of Pro users refer someone monthly
    profileShareRate: 0.05,          // 5% of public profiles get shared weekly
    profileClickRate: 0.25,          // 25% of shares result in click
    
    // FEATURED WRITERS
    featuredAudienceReach: 500,      // Avg reach per featured writer
    featuredClickRate: 0.03,         // 3% click through
    
    // BLOG
    blogShareRate: 0.02,             // 2% of blog visitors share
    blogClickRate: 0.15              // 15% of shares result in click
  },
  
  // Churn rates (monthly)
  churn: {
    monthly: 0.08,     // 8% monthly subscribers churn per month
    annual: 0.25,      // 25% annual subscribers churn at renewal
    trialDrop: 0.58    // 58% of trials don't convert (inverse of 42%)
  },
  
  // Subscription mix
  subscriptions: {
    monthlyShare: 0.65,
    annualShare: 0.35,
    monthlyPrice: 2.99,
    annualPrice: 30
  },
  
  // Newsletter
  newsletter: {
    signupRate: 0.60,      // 60% of test completers join newsletter
    weeklyOpenRate: 0.42,  // 42% open weekly newsletter
    avgSubscriberLifespan: 180  // days
  },
  
  // Featured writers
  featuredWriters: {
    perWeek: 4,
    countries: ['CA', 'UK', 'AU', 'NZ']
  },
  
  // Engagement multiplier from 85% FW content
  engagementMultiplier: 1.525
};

// ═══════════════════════════════════════════════════════════════
// COHORT TRACKING
// ═══════════════════════════════════════════════════════════════

class CohortTracker {
  constructor() {
    this.cohorts = {};
    this.currentWeek = 0;
  }
  
  addWeek(weekNum, data) {
    this.cohorts[weekNum] = {
      signups: data.signups || 0,
      trials: data.trials || 0,
      monthlyPaid: data.monthlyPaid || 0,
      annualPaid: data.annualPaid || 0,
      churned: 0,
      weekStarted: weekNum
    };
  }
  
  applyChurn(weekNum, monthlyChurnRate, annualChurnRate) {
    const weeklyMonthlyChurn = monthlyChurnRate / 4;
    
    for (const [week, cohort] of Object.entries(this.cohorts)) {
      const weeksActive = weekNum - parseInt(week);
      
      if (cohort.monthlyPaid > 0) {
        const churnCount = Math.floor(cohort.monthlyPaid * weeklyMonthlyChurn);
        cohort.monthlyPaid -= churnCount;
        cohort.churned += churnCount;
      }
      
      if (weeksActive > 0 && weeksActive % 52 === 0 && cohort.annualPaid > 0) {
        const churnCount = Math.floor(cohort.annualPaid * annualChurnRate);
        cohort.annualPaid -= churnCount;
        cohort.churned += churnCount;
      }
    }
  }
  
  getTotals() {
    let totalMonthly = 0;
    let totalAnnual = 0;
    let totalChurned = 0;
    
    for (const cohort of Object.values(this.cohorts)) {
      totalMonthly += cohort.monthlyPaid;
      totalAnnual += cohort.annualPaid;
      totalChurned += cohort.churned;
    }
    
    return { monthlyPaid: totalMonthly, annualPaid: totalAnnual, churned: totalChurned };
  }
  
  getMRR() {
    const totals = this.getTotals();
    return (totals.monthlyPaid * 12) + (totals.annualPaid * 2.50);
  }
}

// ═══════════════════════════════════════════════════════════════
// VIRAL CALCULATOR (Updated with Results Card Shares)
// ═══════════════════════════════════════════════════════════════

function calculateViralVisitors(state, config, dailySignups) {
  const v = config.viral;
  const viral = {
    resultsCardShares: 0,    // NEW: Pre-signup card shares
    newsletterForwards: 0,
    userReferrals: 0,
    profileShares: 0,
    featuredPromotion: 0,
    blogShares: 0
  };
  
  // ─────────────────────────────────────────────────────────────
  // PRE-SIGNUP: Results card shares (HIGHEST VOLUME)
  // Test completers share their profile card on social/messaging
  // ─────────────────────────────────────────────────────────────
  viral.resultsCardShares = Math.floor(
    dailySignups *              // People who completed test
    v.resultsCardShareRate *    // 10% share their card
    v.resultsCardClickRate      // 25% of shares → visit
  );
  
  // ─────────────────────────────────────────────────────────────
  // POST-SIGNUP: Newsletter forwards
  // Active subscribers × open rate × forward rate × click rate
  // ─────────────────────────────────────────────────────────────
  const activeNewsletterSubs = Math.floor(state.newsletterSubs * 0.7);
  viral.newsletterForwards = Math.floor(
    activeNewsletterSubs * 
    config.newsletter.weeklyOpenRate * 
    v.newsletterForwardRate * 
    v.newsletterClickRate / 7
  );
  
  // ─────────────────────────────────────────────────────────────
  // PRO USERS: Referrals
  // Pro users × monthly referral rate (daily portion)
  // ─────────────────────────────────────────────────────────────
  viral.userReferrals = Math.floor(state.proPaid * v.userReferralRate / 30);
  
  // ─────────────────────────────────────────────────────────────
  // PRO USERS: Profile shares
  // Public profiles (60% of Pro) × weekly share rate × click rate
  // ─────────────────────────────────────────────────────────────
  const publicProfiles = Math.floor(state.proPaid * 0.6);
  viral.profileShares = Math.floor(
    publicProfiles * v.profileShareRate * v.profileClickRate / 7
  );
  
  // ─────────────────────────────────────────────────────────────
  // FEATURED WRITERS: Promotion
  // Cumulative featured writers × audience reach × click rate
  // ─────────────────────────────────────────────────────────────
  const weekNum = Math.floor(state.day / 7);
  const totalFeatured = weekNum * config.featuredWriters.perWeek;
  viral.featuredPromotion = Math.floor(
    totalFeatured * v.featuredAudienceReach * v.featuredClickRate / 100
  );
  
  // ─────────────────────────────────────────────────────────────
  // BLOG: Shares
  // Blog pageviews (20% of organic) × share rate × click rate
  // ─────────────────────────────────────────────────────────────
  const blogViews = Math.floor(state.dailyVisitors * 0.2);
  viral.blogShares = Math.floor(blogViews * v.blogShareRate * v.blogClickRate);
  
  return viral;
}

// ═══════════════════════════════════════════════════════════════
// MAIN SIMULATION
// ═══════════════════════════════════════════════════════════════

function runSimulationV2(customConfig = {}) {
  const config = { ...DEFAULT_CONFIG_V2, ...customConfig };
  
  // Initialize state
  const state = {
    day: 0,
    dailyVisitors: 0,
    totalVisitors: 0,
    totalViralVisitors: 0,
    signups: 0,
    trials: 0,
    proPaid: 0,
    newsletterSubs: 0,
    revenue: 0,
    adSpend: 0
  };
  
  // Country tracking
  const countryMetrics = {};
  for (const [code, data] of Object.entries(config.countryDistribution)) {
    countryMetrics[code] = {
      name: data.name,
      flag: data.flag,
      visitors: 0,
      signups: 0,
      proPaid: 0,
      revenue: 0
    };
  }
  
  const cohorts = new CohortTracker();
  const daily = [];
  const viralBreakdownTotal = {
    resultsCardShares: 0,
    newsletterForwards: 0,
    userReferrals: 0,
    profileShares: 0,
    featuredPromotion: 0,
    blogShares: 0
  };
  
  const dailyBase = config.initialVisitors / config.days;
  
  for (let day = 1; day <= config.days; day++) {
    state.day = day;
    const weekNum = Math.floor(day / 7);
    
    let dayVisitors = 0;
    let daySignups = 0;
    let dayTrials = 0;
    let dayPaid = 0;
    let dayAdSpend = 0;
    
    // ─────────────────────────────────────────────────────────
    // TRAFFIC BY SOURCE
    // ─────────────────────────────────────────────────────────
    for (const [source, sourceConfig] of Object.entries(config.trafficSources)) {
      const baseVisitors = dailyBase * sourceConfig.share;
      const growthMultiplier = Math.pow(sourceConfig.dailyGrowth, day);
      const sourceVisitors = Math.floor(baseVisitors * growthMultiplier);
      
      const conv = config.conversionBySource[source];
      const adjustedSignupRate = conv.signup * config.engagementMultiplier;
      const adjustedTrialRate = conv.trial * config.engagementMultiplier;
      const adjustedPaidRate = conv.paid;
      
      const sourceSignups = Math.floor(sourceVisitors * Math.min(adjustedSignupRate, 0.95));
      const sourceTrials = Math.floor(sourceSignups * Math.min(adjustedTrialRate, 0.90));
      const sourcePaid = Math.floor(sourceTrials * adjustedPaidRate);
      
      dayVisitors += sourceVisitors;
      daySignups += sourceSignups;
      dayTrials += sourceTrials;
      dayPaid += sourcePaid;
      
      if (source === 'paid' && sourceConfig.cpc) {
        dayAdSpend += sourceVisitors * sourceConfig.cpc;
      }
    }
    
    // Store for viral calculation
    state.dailyVisitors = dayVisitors;
    
    // ─────────────────────────────────────────────────────────
    // VIRAL TRAFFIC (Including Results Card Shares)
    // ─────────────────────────────────────────────────────────
    const viral = calculateViralVisitors(state, config, daySignups);
    const totalViralToday = Object.values(viral).reduce((a, b) => a + b, 0);
    
    // Viral visitors convert at referral rates
    const viralConv = config.conversionBySource.referral;
    const viralSignups = Math.floor(totalViralToday * viralConv.signup * config.engagementMultiplier);
    const viralTrials = Math.floor(viralSignups * viralConv.trial * config.engagementMultiplier);
    const viralPaid = Math.floor(viralTrials * viralConv.paid);
    
    dayVisitors += totalViralToday;
    daySignups += viralSignups;
    dayTrials += viralTrials;
    dayPaid += viralPaid;
    
    // Track viral breakdown
    for (const [key, value] of Object.entries(viral)) {
      viralBreakdownTotal[key] += value;
    }
    
    // ─────────────────────────────────────────────────────────
    // COUNTRY DISTRIBUTION
    // ─────────────────────────────────────────────────────────
    for (const [code, data] of Object.entries(config.countryDistribution)) {
      countryMetrics[code].visitors += Math.floor(dayVisitors * data.share);
      countryMetrics[code].signups += Math.floor(daySignups * data.share);
    }
    
    // ─────────────────────────────────────────────────────────
    // COHORT MANAGEMENT (Weekly)
    // ─────────────────────────────────────────────────────────
    if (day % 7 === 0) {
      const weeklyPaid = dayPaid * 7;
      const monthlyPaid = Math.floor(weeklyPaid * config.subscriptions.monthlyShare);
      const annualPaid = Math.floor(weeklyPaid * config.subscriptions.annualShare);
      
      cohorts.addWeek(weekNum, {
        signups: daySignups * 7,
        trials: dayTrials * 7,
        monthlyPaid,
        annualPaid
      });
      
      cohorts.applyChurn(weekNum, config.churn.monthly, config.churn.annual);
    }
    
    // ─────────────────────────────────────────────────────────
    // NEWSLETTER
    // ─────────────────────────────────────────────────────────
    const newNewsletterSubs = Math.floor(daySignups * config.newsletter.signupRate);
    state.newsletterSubs += newNewsletterSubs;
    
    // ─────────────────────────────────────────────────────────
    // REVENUE
    // ─────────────────────────────────────────────────────────
    const cohortTotals = cohorts.getTotals();
    const monthlyRevenue = cohortTotals.monthlyPaid * (config.subscriptions.monthlyPrice / 30);
    const annualRevenue = cohortTotals.annualPaid * (config.subscriptions.annualPrice / 365);
    const dayRevenue = monthlyRevenue + annualRevenue;
    
    // ─────────────────────────────────────────────────────────
    // UPDATE STATE
    // ─────────────────────────────────────────────────────────
    state.totalVisitors += dayVisitors;
    state.totalViralVisitors += totalViralToday;
    state.signups += daySignups;
    state.trials += dayTrials;
    state.proPaid = cohortTotals.monthlyPaid + cohortTotals.annualPaid;
    state.revenue += dayRevenue;
    state.adSpend += dayAdSpend;
    
    // Update country Pro paid (proportional)
    for (const [code, data] of Object.entries(config.countryDistribution)) {
      countryMetrics[code].proPaid = Math.floor(state.proPaid * data.share);
      countryMetrics[code].revenue = Math.floor(state.revenue * data.share);
    }
    
    daily.push({
      day,
      visitors: dayVisitors,
      viralVisitors: totalViralToday,
      signups: daySignups,
      trials: dayTrials,
      proPaid: state.proPaid,
      newsletterSubs: state.newsletterSubs,
      revenue: dayRevenue,
      cumulativeRevenue: state.revenue,
      mrr: cohorts.getMRR(),
      adSpend: dayAdSpend,
      viral: { ...viral }
    });
  }
  
  // ─────────────────────────────────────────────────────────
  // FINAL CALCULATIONS
  // ─────────────────────────────────────────────────────────
  const cohortTotals = cohorts.getTotals();
  const finalMRR = cohorts.getMRR();
  const nonViralVisitors = state.totalVisitors - state.totalViralVisitors;
  const effectiveK = nonViralVisitors > 0 ? state.totalViralVisitors / nonViralVisitors : 0;
  
  // CAC/LTV
  const totalPaidUsers = cohortTotals.monthlyPaid + cohortTotals.annualPaid;
  const cac = totalPaidUsers > 0 ? state.adSpend / totalPaidUsers : 0;
  const avgMonthlyRevenue = (config.subscriptions.monthlyPrice * config.subscriptions.monthlyShare) +
                            (config.subscriptions.annualPrice / 12 * config.subscriptions.annualShare);
  const avgLifetimeMonths = 1 / config.churn.monthly;
  const ltv = avgMonthlyRevenue * avgLifetimeMonths * 0.80;
  
  return {
    config,
    daily,
    totals: {
      visitors: state.totalVisitors,
      viralVisitors: state.totalViralVisitors,
      signups: state.signups,
      trials: state.trials,
      proPaid: totalPaidUsers,
      monthlyPaid: cohortTotals.monthlyPaid,
      annualPaid: cohortTotals.annualPaid,
      churned: cohortTotals.churned,
      newsletterSubs: state.newsletterSubs,
      revenue: state.revenue,
      adSpend: state.adSpend
    },
    metrics: {
      effectiveK,
      viralPercent: state.totalViralVisitors / state.totalVisitors,
      signupRate: state.signups / state.totalVisitors,
      trialRate: state.trials / state.signups,
      paidRate: totalPaidUsers / state.trials,
      churnedPercent: cohortTotals.churned / (totalPaidUsers + cohortTotals.churned),
      mrr: finalMRR,
      arr: finalMRR * 12,
      arpu: state.revenue / totalPaidUsers,
      cac,
      ltv,
      ltvCacRatio: cac > 0 ? ltv / cac : Infinity
    },
    viralBreakdown: viralBreakdownTotal,
    countryMetrics,
    cohorts: cohorts.cohorts
  };
}

// ═══════════════════════════════════════════════════════════════
// PROJECTION FUNCTIONS
// ═══════════════════════════════════════════════════════════════

function projectMetrics(simulation, targetDays) {
  // Get daily averages from last 14 days for stable projection
  const last14 = simulation.daily.slice(-14);
  
  const avgDailyVisitors = last14.reduce((a, d) => a + d.visitors, 0) / 14;
  const avgDailySignups = last14.reduce((a, d) => a + d.signups, 0) / 14;
  const avgDailyRevenue = last14.reduce((a, d) => a + d.revenue, 0) / 14;
  const avgDailyViral = last14.reduce((a, d) => a + d.viralVisitors, 0) / 14;
  
  // Calculate growth rate
  const first7 = simulation.daily.slice(-14, -7);
  const last7 = simulation.daily.slice(-7);
  const visitorGrowth = (last7.reduce((a,d) => a + d.visitors, 0) / first7.reduce((a,d) => a + d.visitors, 0));
  const weeklyGrowthRate = Math.pow(visitorGrowth, 1/7);
  
  const daysToProject = targetDays - simulation.config.days;
  const weeksToProject = daysToProject / 7;
  
  // Compound growth
  const growthMultiplier = Math.pow(weeklyGrowthRate, weeksToProject);
  
  // Current state
  const current = simulation.totals;
  const currentMRR = simulation.metrics.mrr;
  
  // Apply churn to existing users over projection period
  const monthlyChurnRate = simulation.config.churn.monthly;
  const retentionRate = Math.pow(1 - monthlyChurnRate/4, weeksToProject);
  
  // New users during projection period
  const projectedNewVisitors = avgDailyVisitors * daysToProject * growthMultiplier;
  const projectedNewSignups = avgDailySignups * daysToProject * growthMultiplier;
  const conversionToPaid = simulation.metrics.signupRate * simulation.metrics.trialRate * simulation.metrics.paidRate;
  const projectedNewPaid = Math.floor(projectedNewVisitors * conversionToPaid);
  
  // Retained existing + new
  const retainedExisting = Math.floor(current.proPaid * retentionRate);
  const totalProPaid = retainedExisting + projectedNewPaid;
  
  // MRR growth
  const projectedMRR = Math.floor(currentMRR * retentionRate + (projectedNewPaid * 10.5)); // Blended monthly
  
  // Revenue = existing cumulative + new period revenue
  const existingRevenue = current.revenue;
  const newPeriodRevenue = avgDailyRevenue * daysToProject * growthMultiplier;
  
  return {
    days: targetDays,
    daysProjected: daysToProject,
    visitors: Math.floor(current.visitors + projectedNewVisitors),
    signups: Math.floor(current.signups + projectedNewSignups),
    proPaid: totalProPaid,
    retainedFromDay100: retainedExisting,
    newPaidInPeriod: projectedNewPaid,
    mrr: projectedMRR,
    arr: projectedMRR * 12,
    revenue: Math.floor(existingRevenue + newPeriodRevenue),
    growthMultiplier: growthMultiplier.toFixed(3),
    retentionRate: (retentionRate * 100).toFixed(1) + '%'
  };
}

// ═══════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════

module.exports = {
  runSimulationV2,
  projectMetrics,
  DEFAULT_CONFIG_V2,
  CohortTracker
};
