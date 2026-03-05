/**
 * QUIRRELY SIMULATION ENGINE v3.1
 * ================================
 * Standard funnel simulation with 85% featured writer newsletter content
 * 
 * USE THIS FOR ALL FUTURE SIMULATIONS
 * 
 * Usage:
 *   const sim = runSimulation({ days: 100, targetVisitors: 100000 });
 *   console.log(sim.totals);
 */

const DEFAULT_CONFIG = {
  days: 100,
  targetVisitors: 100000,
  
  // ═══════════════════════════════════════════════════════════════
  // NEWSLETTER CONTENT MIX — STANDARD: 85% FEATURED WRITERS
  // ═══════════════════════════════════════════════════════════════
  featuredWriterContentPct: 0.85,  // DO NOT CHANGE WITHOUT APPROVAL
  
  // Pricing
  pricing: {
    proMonthly: 2.99,
    proAnnual: 30,
    annualRatio: 0.35,
    monthlyChurn: 0.05
  },
  
  // Countries
  countries: {
    CA: { share: 0.40, flag: '🍁', name: 'Canada' },
    UK: { share: 0.25, flag: '🇬🇧', name: 'United Kingdom' },
    AU: { share: 0.20, flag: '🇦🇺', name: 'Australia' },
    NZ: { share: 0.15, flag: '🇳🇿', name: 'New Zealand' }
  }
};

/**
 * Calculate engagement multiplier based on featured writer content %
 * Baseline: 50% = 1.0x
 * Standard: 85% = 1.525x
 */
function getEngagementMultiplier(featuredWriterPct) {
  return 1 + (featuredWriterPct - 0.50) * 1.5;
}

/**
 * Get viral coefficients adjusted for featured writer content %
 */
function getViralCoefficients(engagementMult) {
  return {
    // Base user referral
    userReferral: {
      rate: 0.25,
      conversionRate: 0.40,
      delayDays: 7
    },
    
    // Blog post sharing
    blogShares: {
      postsTotal: 40,
      dailyShareRate: 0.4,
      sharesPerPost: 3,
      visitorsPerShare: 2,
      conversionRate: 0.15
    },
    
    // Newsletter (scales with engagement)
    newsletter: {
      forwardRate: 0.08 * engagementMult,
      openRate: 0.35 * engagementMult,
      clickRate: 0.12 * engagementMult,
      visitorsPerForward: 1.5,
      conversionRate: 0.25
    },
    
    // Featured writer promotion (scales with engagement)
    featuredWriter: {
      writersPerWeek: 4,
      avgAudience: 500,
      shareRate: 0.80 * engagementMult,
      clickRate: 0.03 * engagementMult,
      conversionRate: 0.20
    },
    
    // Profile shares (scales with engagement)
    profileShares: {
      shareRate: 0.15 * engagementMult,
      visitorsPerShare: 8,
      conversionRate: 0.18
    }
  };
}

/**
 * Get traffic source configuration
 */
function getTrafficSources(engagementMult) {
  return {
    organic: { share: 0.30, convMult: 1.2 },
    direct: { share: 0.18, convMult: 1.0 },
    social: { share: 0.15, convMult: 0.9 },
    referral: { share: 0.12, convMult: 1.4 },
    email: { share: 0.15, convMult: 1.6 * engagementMult },  // Scales with content quality
    paid: { share: 0.10, convMult: 0.85 }
  };
}

/**
 * Get funnel conversion rates
 */
function getFunnelRates(engagementMult) {
  return {
    landingToStart: 0.42,
    startToComplete: 0.78,
    completeToSignup: 0.31,
    
    // Pro conversion drivers
    signupToProTrial: {
      base: 0.08,
      featuredWriterCTA: 0.04 * engagementMult,
      proContentTeaser: 0.03,
      profileCTA: 0.02
    },
    
    proTrialToProPaid: 0.42,
    proToPublicProfile: 0.60
  };
}

/**
 * S-curve daily visitor growth
 */
function dailyBaseVisitors(day, days, targetVisitors) {
  const midpoint = days * 0.55;
  const steepness = 0.085;
  const maxDaily = targetVisitors / 45;
  const curve = maxDaily / (1 + Math.exp(-steepness * (day - midpoint)));
  const noise = 0.88 + Math.random() * 0.24;
  return Math.round(curve * noise);
}

/**
 * MAIN SIMULATION FUNCTION
 */
function runSimulation(customConfig = {}) {
  const config = { ...DEFAULT_CONFIG, ...customConfig };
  const { days, targetVisitors, featuredWriterContentPct, pricing, countries } = config;
  
  // Calculate engagement multiplier
  const engagementMult = getEngagementMultiplier(featuredWriterContentPct);
  
  // Get scaled coefficients
  const viral = getViralCoefficients(engagementMult);
  const sources = getTrafficSources(engagementMult);
  const funnel = getFunnelRates(engagementMult);
  
  // State
  let state = {
    newsletterSubs: 0,
    activeMonthlyPro: 0,
    activeAnnualPro: 0,
    publicProfiles: 0,
    featuredWriters: 0
  };
  
  // Results
  let totals = {
    visitors: 0,
    baseVisitors: 0,
    viralVisitors: 0,
    testStarts: 0,
    testCompletes: 0,
    signups: 0,
    proTrials: 0,
    proPaid: 0,
    revenue: 0,
    mrr: 0
  };
  
  let viralBreakdown = {
    userReferral: 0,
    blogShares: 0,
    newsletter: 0,
    featuredWriter: 0,
    profileShares: 0
  };
  
  let byCountry = {};
  let bySource = {};
  
  Object.keys(countries).forEach(c => { byCountry[c] = { visitors: 0, signups: 0, pro: 0 }; });
  Object.keys(sources).forEach(s => { bySource[s] = { visitors: 0, signups: 0 }; });
  
  let daily = [];
  let pendingViral = [];
  
  // ─────────────────────────────────────────────────────────────
  // SIMULATION LOOP
  // ─────────────────────────────────────────────────────────────
  
  for (let day = 1; day <= days; day++) {
    let dayData = {
      day,
      baseVisitors: dailyBaseVisitors(day, days, targetVisitors),
      viralVisitors: 0,
      totalVisitors: 0,
      signups: 0,
      proTrials: 0,
      proPaid: 0,
      revenue: 0,
      mrr: 0
    };
    
    // Process pending viral arrivals
    pendingViral = pendingViral.filter(v => {
      if (v.day <= day) {
        dayData.viralVisitors += v.count;
        viralBreakdown[v.source] += v.count;
        return false;
      }
      return true;
    });
    
    // Blog shares (daily)
    const blogViral = Math.round(
      viral.blogShares.dailyShareRate * 
      viral.blogShares.sharesPerPost * 
      viral.blogShares.visitorsPerShare *
      (0.5 + day / days)
    );
    dayData.viralVisitors += blogViral;
    viralBreakdown.blogShares += blogViral;
    
    // Weekly: Newsletter + Featured writer promo
    if (day % 7 === 0 && state.newsletterSubs > 0) {
      // Newsletter forwards
      const forwards = Math.round(state.newsletterSubs * viral.newsletter.forwardRate);
      const nlVisitors = Math.round(forwards * viral.newsletter.visitorsPerForward);
      pendingViral.push({ day: day + 2, count: nlVisitors, source: 'newsletter' });
      
      // Featured writer promotion
      const fwVisitors = Math.round(
        viral.featuredWriter.writersPerWeek *
        viral.featuredWriter.avgAudience *
        viral.featuredWriter.shareRate *
        viral.featuredWriter.clickRate
      );
      pendingViral.push({ day: day + 1, count: fwVisitors, source: 'featuredWriter' });
      state.featuredWriters += 4;
    }
    
    // Profile shares
    if (state.publicProfiles > 0) {
      const profileViral = Math.round(
        state.publicProfiles * 
        (viral.profileShares.shareRate / 30) * 
        viral.profileShares.visitorsPerShare
      );
      dayData.viralVisitors += profileViral;
      viralBreakdown.profileShares += profileViral;
    }
    
    dayData.totalVisitors = dayData.baseVisitors + dayData.viralVisitors;
    totals.visitors += dayData.totalVisitors;
    totals.baseVisitors += dayData.baseVisitors;
    totals.viralVisitors += dayData.viralVisitors;
    
    // ─────────────────────────────────────────────────────────────
    // FUNNEL PROCESSING
    // ─────────────────────────────────────────────────────────────
    
    for (let i = 0; i < dayData.totalVisitors; i++) {
      // Assign country
      const countryRoll = Math.random();
      let country = 'CA';
      let cum = 0;
      for (const [c, data] of Object.entries(countries)) {
        cum += data.share;
        if (countryRoll < cum) { country = c; break; }
      }
      byCountry[country].visitors++;
      
      // Assign source
      let source = 'direct';
      let convMult = 1.0;
      
      if (i < dayData.viralVisitors) {
        source = Math.random() < 0.6 ? 'referral' : 'email';
        convMult = sources[source].convMult;
      } else {
        const roll = Math.random();
        cum = 0;
        for (const [s, data] of Object.entries(sources)) {
          cum += data.share;
          if (roll < cum) { source = s; convMult = data.convMult; break; }
        }
      }
      bySource[source].visitors++;
      
      // Funnel
      if (Math.random() < funnel.landingToStart * convMult) {
        totals.testStarts++;
        
        if (Math.random() < funnel.startToComplete) {
          totals.testCompletes++;
          
          if (Math.random() < funnel.completeToSignup * convMult) {
            dayData.signups++;
            totals.signups++;
            state.newsletterSubs++;
            byCountry[country].signups++;
            bySource[source].signups++;
            
            // User referral
            if (Math.random() < viral.userReferral.rate) {
              const delay = viral.userReferral.delayDays + Math.floor(Math.random() * 7);
              pendingViral.push({ day: day + delay, count: 1, source: 'userReferral' });
            }
            
            // Pro trial
            const proTrialRate = 
              funnel.signupToProTrial.base +
              funnel.signupToProTrial.featuredWriterCTA +
              funnel.signupToProTrial.proContentTeaser +
              funnel.signupToProTrial.profileCTA;
            
            if (Math.random() < proTrialRate * convMult) {
              dayData.proTrials++;
              totals.proTrials++;
              
              if (Math.random() < funnel.proTrialToProPaid) {
                dayData.proPaid++;
                totals.proPaid++;
                byCountry[country].pro++;
                
                // Annual vs Monthly
                if (Math.random() < pricing.annualRatio) {
                  state.activeAnnualPro++;
                  dayData.revenue += pricing.proAnnual;
                } else {
                  state.activeMonthlyPro++;
                  dayData.revenue += pricing.proMonthly;
                }
                
                // Public profile
                if (Math.random() < funnel.proToPublicProfile) {
                  state.publicProfiles++;
                }
              }
            }
          }
        }
      }
    }
    
    // Churn
    if (day > 30) {
      const churnToday = Math.floor(state.activeMonthlyPro * pricing.monthlyChurn / 30);
      state.activeMonthlyPro = Math.max(0, state.activeMonthlyPro - churnToday);
    }
    
    // MRR
    dayData.mrr = (state.activeMonthlyPro * pricing.proMonthly) + 
                  (state.activeAnnualPro * pricing.proAnnual / 12);
    dayData.revenue += dayData.mrr / 30;
    
    totals.revenue += dayData.revenue;
    totals.mrr = dayData.mrr;
    
    daily.push(dayData);
  }
  
  // ─────────────────────────────────────────────────────────────
  // CALCULATE EFFECTIVE VIRAL K
  // ─────────────────────────────────────────────────────────────
  
  const totalViralVisitors = Object.values(viralBreakdown).reduce((a, b) => a + b, 0);
  const effectiveK = totals.signups > 0 ? totalViralVisitors / totals.signups : 0;
  
  // ─────────────────────────────────────────────────────────────
  // RETURN RESULTS
  // ─────────────────────────────────────────────────────────────
  
  return {
    config: {
      days,
      targetVisitors,
      featuredWriterContentPct,
      engagementMultiplier: engagementMult
    },
    totals,
    viralBreakdown,
    effectiveK,
    byCountry,
    bySource,
    state,
    daily,
    projections: {
      annualVisitors: Math.round(totals.visitors * (365 / days)),
      annualSignups: Math.round(totals.signups * (365 / days)),
      annualProUsers: Math.round(totals.proPaid * (365 / days)),
      annualRevenue: Math.round(totals.mrr * 12 + totals.revenue),
      arr: Math.round(totals.mrr * 12)
    }
  };
}

/**
 * Format helpers
 */
const fmt = n => Math.round(n).toLocaleString();
const pct = (n, d) => d > 0 ? ((n / d) * 100).toFixed(2) + '%' : '0%';
const money = n => '$' + Math.round(n).toLocaleString();

/**
 * Generate report
 */
function generateReport(sim) {
  const { config, totals, viralBreakdown, effectiveK, projections } = sim;
  
  return `
═══════════════════════════════════════════════════════════════
  QUIRRELY SIMULATION REPORT
  Generated: ${new Date().toISOString()}
═══════════════════════════════════════════════════════════════

CONFIGURATION
───────────────────────────────────────────────────────────────
  Days:                      ${config.days}
  Target Visitors:           ${fmt(config.targetVisitors)}
  Featured Writer Content:   ${(config.featuredWriterContentPct * 100)}% ← STANDARD
  Engagement Multiplier:     ${config.engagementMultiplier.toFixed(2)}x

TRAFFIC
───────────────────────────────────────────────────────────────
  Base Visitors:             ${fmt(totals.baseVisitors)}
  Viral Visitors:            ${fmt(totals.viralVisitors)} (${pct(totals.viralVisitors, totals.visitors)})
  TOTAL VISITORS:            ${fmt(totals.visitors)}

VIRAL BREAKDOWN (K = ${effectiveK.toFixed(2)})
───────────────────────────────────────────────────────────────
  Newsletter Forwards:       ${fmt(viralBreakdown.newsletter)}
  User Referrals:            ${fmt(viralBreakdown.userReferral)}
  Featured Writer Promo:     ${fmt(viralBreakdown.featuredWriter)}
  Profile Shares:            ${fmt(viralBreakdown.profileShares)}
  Blog Shares:               ${fmt(viralBreakdown.blogShares)}

FUNNEL
───────────────────────────────────────────────────────────────
  Test Starts:               ${fmt(totals.testStarts)} (${pct(totals.testStarts, totals.visitors)})
  Test Completes:            ${fmt(totals.testCompletes)} (${pct(totals.testCompletes, totals.testStarts)})
  Signups:                   ${fmt(totals.signups)} (${pct(totals.signups, totals.testCompletes)})
  Pro Trials:                ${fmt(totals.proTrials)} (${pct(totals.proTrials, totals.signups)})
  Pro Paid:                  ${fmt(totals.proPaid)} (${pct(totals.proPaid, totals.proTrials)})

REVENUE
───────────────────────────────────────────────────────────────
  Total Revenue (${config.days}d):      ${money(totals.revenue)}
  MRR (Day ${config.days}):             ${money(totals.mrr)}
  ARR (Projected):           ${money(projections.arr)}

YEAR 1 PROJECTIONS
───────────────────────────────────────────────────────────────
  Visitors:                  ${fmt(projections.annualVisitors)}
  Signups:                   ${fmt(projections.annualSignups)}
  Pro Users:                 ${fmt(projections.annualProUsers)}
  Revenue:                   ${money(projections.annualRevenue)}

═══════════════════════════════════════════════════════════════
`;
}

// ═══════════════════════════════════════════════════════════════
// EXPORT / RUN
// ═══════════════════════════════════════════════════════════════

if (typeof module !== 'undefined') {
  module.exports = { runSimulation, generateReport, DEFAULT_CONFIG, getEngagementMultiplier };
}

// Run if executed directly
if (typeof require !== 'undefined' && require.main === module) {
  const sim = runSimulation();
  console.log(generateReport(sim));
  console.log('JSON_OUTPUT_START');
  console.log(JSON.stringify(sim, null, 2));
  console.log('JSON_OUTPUT_END');
}
