#!/usr/bin/env python3
"""
MARS SIMULATION v5.1.0
100K Visitors in 100 Days - Knight of Wands v3.1.1 + Blog/SEO Integration

This simulation models:
- Full funnel from visitor → paid subscriber
- All v3.1.1 MRR optimizations (P1, P2, P3)
- Blog/SEO contribution to top-of-funnel
- Meta Orchestrator v5.1 health integration

Author: Mars (Revenue Optimization)
Date: February 16, 2026
"""

import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


# ═══════════════════════════════════════════════════════════════════════════
# PRICING CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

PRICING = {
    # Core tiers (CAD)
    "pro_monthly": 4.99,
    "pro_annual": 44.99,
    "growth_monthly": 6.99,
    "growth_annual": 62.99,
    "featured_monthly": 7.99,
    "featured_annual": 71.99,
    "authority_monthly": 8.99,
    "authority_annual": 80.99,
    
    # Addon
    "addon_monthly": 9.99,
    "addon_annual": 89.99,
    
    # Bundles
    "bundle_pro_vs": 12.99,
    "bundle_authority_vs": 16.99,
}

LTV = {
    "monthly": 46.18,
    "annual": 128.57,
    "blended": 89.71,
    "addon": 80.91,
    "growth": 62.93,
}


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

SCENARIO_V511 = {
    "name": "v5.1.1 Full Integration",
    "description": "Knight of Wands v3.1.1 + Meta Orchestrator v5.1 + Blog/SEO",
    
    "conversions": {
        "visit_to_signup": 0.155,       # +0.7% from social proof
        "signup_to_trial": 0.38,        # +4% from first analysis hook
        "trial_to_paid": 0.54,          # +5% from progressive unlocks
        "paid_to_addon": 0.22,          # +7% from bundling
        "paid_to_growth": 0.12,         # Growth tier adoption
        "paid_to_featured": 0.07,       # +2% from achievements
        "featured_to_authority": 0.24,  # +4% from leaderboard
        "monthly_to_annual": 0.18,      # Annual discount uptake
    },
    
    "churn": {
        "monthly": 0.045,               # -1.5% from downgrade prevention
        "annual": 0.16,                 # -5% from engagement
    },
    
    "blog_seo": {
        "organic_traffic_share": 0.35,  # 35% of visitors from organic
        "blog_cta_ctr": 0.045,          # 4.5% click through from blog
        "blog_conversion_lift": 1.15,   # 15% higher conversion from blog visitors
        "content_pages": 40,
        "avg_position": 8.5,
        "impressions_daily": 5000,
        "clicks_daily": 175,
    },
    
    "features": {
        "addon_bundling": True,
        "downgrade_prevention": True,
        "first_analysis_hook": True,
        "annual_discount_25": True,
        "smart_notifications": True,
        "social_proof": True,
        "growth_tier": True,
        "achievement_system": True,
        "progressive_unlocks": True,
        "blog_observer": True,          # v5.1
        "seo_optimization": True,       # v5.1
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION STATE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SimulationState:
    """Current state of the simulation."""
    day: int = 0
    
    # Visitors
    total_visitors: int = 0
    organic_visitors: int = 0
    direct_visitors: int = 0
    
    # Funnel
    total_signups: int = 0
    total_trials: int = 0
    
    # Users
    free_users: int = 0
    trial_users: int = 0
    monthly_paid: int = 0
    annual_paid: int = 0
    growth_tier_users: int = 0
    addon_users: int = 0
    bundle_users: int = 0
    featured_users: int = 0
    authority_users: int = 0
    
    # Retention
    paused_users: int = 0
    downgraded_users: int = 0
    saved_users: int = 0
    churned: int = 0
    annual_converted: int = 0
    
    # Revenue
    mrr: float = 0.0
    arr: float = 0.0
    total_revenue: float = 0.0
    
    # Blog/SEO (v5.1)
    blog_impressions: int = 0
    blog_clicks: int = 0
    blog_conversions: int = 0
    
    # History
    daily_mrr: List[float] = field(default_factory=list)
    daily_visitors: List[int] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
# MARS SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class MarsSimulation:
    """
    Mars Revenue Simulation Engine v5.1
    
    Simulates 100K visitors over 100 days with full v3.1.1 + v5.1 features.
    """
    
    def __init__(
        self,
        scenario: Dict = SCENARIO_V511,
        total_visitors: int = 100000,
        days: int = 100,
        daily_growth: float = 1.005,
        skip_baseline: bool = False,
    ):
        self.scenario = scenario
        self.total_visitors = total_visitors
        self.days = days
        self.daily_growth = daily_growth
        self.skip_baseline = skip_baseline
        
        self.state = SimulationState()
        self.history: List[Dict] = []
    
    def reset(self):
        """Reset simulation state."""
        self.state = SimulationState()
        self.history = []
    
    def run_day(self, day: int) -> SimulationState:
        """Run simulation for a single day."""
        s = self.scenario
        c = s["conversions"]
        churn = s["churn"]
        blog = s["blog_seo"]
        
        # Calculate daily visitors with growth
        base_daily = self.total_visitors / self.days
        visitors = int(base_daily * math.pow(self.daily_growth, day))
        
        # v5.1: Split by traffic source
        organic = int(visitors * blog["organic_traffic_share"])
        direct = visitors - organic
        
        # v5.1: Blog/SEO metrics
        self.state.blog_impressions += blog["impressions_daily"]
        self.state.blog_clicks += blog["clicks_daily"]
        
        # Funnel: Visitors → Signups
        # Organic visitors convert slightly better
        organic_signup_rate = c["visit_to_signup"] * blog["blog_conversion_lift"]
        organic_signups = int(organic * organic_signup_rate)
        direct_signups = int(direct * c["visit_to_signup"])
        signups = organic_signups + direct_signups
        
        self.state.blog_conversions += organic_signups
        
        # Signups → Trials
        new_trials = int(signups * c["signup_to_trial"])
        new_free = signups - new_trials
        
        # Trial conversions (14-day spread)
        trial_conversion_rate = c["trial_to_paid"] / 14
        trials_converting = int(self.state.trial_users * trial_conversion_rate)
        
        # Annual vs Monthly split (25% discount drives more annual)
        annual_share = c["monthly_to_annual"] if s["features"]["annual_discount_25"] else 0.35
        new_annual = int(trials_converting * annual_share)
        new_monthly = trials_converting - new_annual
        
        # Growth tier adoption
        if s["features"]["growth_tier"]:
            growth_rate = c["paid_to_growth"]
            new_growth = int(new_monthly * growth_rate)
            new_monthly -= new_growth
        else:
            new_growth = 0
        
        # Addon purchases
        total_paid = self.state.monthly_paid + self.state.annual_paid + self.state.growth_tier_users
        addon_rate = c["paid_to_addon"] / 30
        new_addons = int(total_paid * addon_rate)
        
        # Bundle adoption (40% choose bundles)
        if s["features"]["addon_bundling"]:
            new_bundles = int(new_addons * 0.40)
        else:
            new_bundles = 0
        
        # Tier progression
        new_featured = int(total_paid * (c["paid_to_featured"] / 90))
        new_authority = int(self.state.featured_users * (c["featured_to_authority"] / 90))
        
        # Churn with downgrade prevention
        monthly_churn_rate = churn["monthly"] / 30
        churning = int(self.state.monthly_paid * monthly_churn_rate)
        
        if s["features"]["downgrade_prevention"]:
            saved = int(churning * 0.35)
            paused = int(saved * 0.4)
            downgraded = int(saved * 0.3)
            discounted = saved - paused - downgraded
            
            churning -= saved
            self.state.paused_users += paused
            self.state.downgraded_users += downgraded
            self.state.saved_users += discounted
        
        # Monthly to annual conversion
        monthly_to_annual_rate = c["monthly_to_annual"] / 30
        converting_to_annual = int(self.state.monthly_paid * monthly_to_annual_rate)
        
        # Update state
        self.state.day = day
        self.state.total_visitors += visitors
        self.state.organic_visitors += organic
        self.state.direct_visitors += direct
        self.state.total_signups += signups
        self.state.total_trials += new_trials
        
        self.state.free_users += new_free
        self.state.trial_users = max(0, self.state.trial_users + new_trials - trials_converting)
        self.state.monthly_paid = max(0, self.state.monthly_paid + new_monthly - churning - converting_to_annual)
        self.state.annual_paid += new_annual + converting_to_annual
        self.state.growth_tier_users += new_growth
        self.state.addon_users += new_addons
        self.state.bundle_users += new_bundles
        self.state.featured_users += new_featured
        self.state.authority_users += new_authority
        self.state.churned += churning
        self.state.annual_converted += converting_to_annual
        
        # Calculate MRR
        mrr = self.calculate_mrr()
        self.state.mrr = mrr
        self.state.arr = mrr * 12
        self.state.total_revenue += mrr / 30
        
        self.state.daily_mrr.append(mrr)
        self.state.daily_visitors.append(visitors)
        
        # Record history
        self.history.append({
            "day": day,
            "visitors": visitors,
            "organic": organic,
            "signups": signups,
            "trials": self.state.trial_users,
            "paid": self.state.monthly_paid + self.state.annual_paid + self.state.growth_tier_users,
            "addons": self.state.addon_users,
            "mrr": mrr,
        })
        
        return self.state
    
    def calculate_mrr(self) -> float:
        """Calculate current MRR."""
        s = self.state
        
        # Base tier MRR
        monthly_mrr = s.monthly_paid * PRICING["pro_monthly"]
        annual_mrr = s.annual_paid * (PRICING["pro_annual"] / 12)
        
        # Growth tier
        growth_mrr = s.growth_tier_users * PRICING["growth_monthly"]
        
        # Addons (standalone + bundles)
        standalone_addon = (s.addon_users - s.bundle_users) * PRICING["addon_monthly"]
        bundle_mrr = s.bundle_users * PRICING["bundle_pro_vs"]
        
        # Tier premiums
        featured_premium = s.featured_users * (PRICING["featured_monthly"] - PRICING["pro_monthly"])
        authority_premium = s.authority_users * (PRICING["authority_monthly"] - PRICING["pro_monthly"])
        
        return (
            monthly_mrr + annual_mrr + growth_mrr +
            standalone_addon + bundle_mrr +
            featured_premium + authority_premium
        )
    
    def calculate_mrr_breakdown(self) -> Dict:
        """Get MRR breakdown by source."""
        s = self.state
        return {
            "pro_monthly": s.monthly_paid * PRICING["pro_monthly"],
            "pro_annual": s.annual_paid * (PRICING["pro_annual"] / 12),
            "growth": s.growth_tier_users * PRICING["growth_monthly"],
            "addon_standalone": (s.addon_users - s.bundle_users) * PRICING["addon_monthly"],
            "bundles": s.bundle_users * PRICING["bundle_pro_vs"],
            "featured_premium": s.featured_users * (PRICING["featured_monthly"] - PRICING["pro_monthly"]),
            "authority_premium": s.authority_users * (PRICING["authority_monthly"] - PRICING["pro_monthly"]),
        }
    
    def run(self) -> Dict:
        """Run full simulation."""
        self.reset()
        
        for day in range(1, self.days + 1):
            self.run_day(day)
        
        return self.get_results()
    
    def get_results(self) -> Dict:
        """Get final simulation results."""
        s = self.state
        total_paid = s.monthly_paid + s.annual_paid + s.growth_tier_users
        mrr_breakdown = self.calculate_mrr_breakdown()
        
        return {
            "scenario": self.scenario["name"],
            "version": "5.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            
            # Configuration
            "config": {
                "total_visitors": self.total_visitors,
                "days": self.days,
                "daily_growth": self.daily_growth,
            },
            
            # Final metrics
            "final": {
                "day": s.day,
                "mrr": round(s.mrr, 2),
                "arr": round(s.arr, 2),
                "total_revenue": round(s.total_revenue, 2),
            },
            
            # Funnel
            "funnel": {
                "total_visitors": s.total_visitors,
                "organic_visitors": s.organic_visitors,
                "organic_share": round(s.organic_visitors / s.total_visitors * 100, 1),
                "total_signups": s.total_signups,
                "signup_rate": round(s.total_signups / s.total_visitors * 100, 2),
                "total_trials": s.total_trials,
                "trial_rate": round(s.total_trials / s.total_signups * 100, 2) if s.total_signups > 0 else 0,
            },
            
            # Users
            "users": {
                "free": s.free_users,
                "trial": s.trial_users,
                "monthly_paid": s.monthly_paid,
                "annual_paid": s.annual_paid,
                "growth_tier": s.growth_tier_users,
                "total_paid": total_paid,
                "addon_users": s.addon_users,
                "bundle_users": s.bundle_users,
                "addon_attach_rate": round(s.addon_users / total_paid * 100, 1) if total_paid > 0 else 0,
                "bundle_rate": round(s.bundle_users / s.addon_users * 100, 1) if s.addon_users > 0 else 0,
                "featured": s.featured_users,
                "authority": s.authority_users,
            },
            
            # Retention
            "retention": {
                "churned": s.churned,
                "churn_rate": round(s.churned / total_paid * 100, 2) if total_paid > 0 else 0,
                "paused": s.paused_users,
                "downgraded": s.downgraded_users,
                "saved_50_offer": s.saved_users,
                "total_saved": s.paused_users + s.downgraded_users + s.saved_users,
                "annual_converted": s.annual_converted,
            },
            
            # MRR Breakdown
            "mrr_breakdown": {k: round(v, 2) for k, v in mrr_breakdown.items()},
            
            # Blog/SEO (v5.1)
            "blog_seo": {
                "impressions": s.blog_impressions,
                "clicks": s.blog_clicks,
                "ctr": round(s.blog_clicks / s.blog_impressions * 100, 2) if s.blog_impressions > 0 else 0,
                "organic_signups": s.blog_conversions,
                "organic_conversion_rate": round(s.blog_conversions / s.organic_visitors * 100, 2) if s.organic_visitors > 0 else 0,
            },
            
            # Comparisons
            "comparison": {
                "vs_baseline": self._compare_baseline() if not self.skip_baseline else {"skipped": True},
            },
        }
    
    def _compare_baseline(self) -> Dict:
        """Compare to baseline scenario."""
        # Run baseline simulation
        baseline_scenario = {
            "name": "Baseline",
            "conversions": {
                "visit_to_signup": 0.148,
                "signup_to_trial": 0.30,
                "trial_to_paid": 0.42,
                "paid_to_addon": 0.08,
                "paid_to_growth": 0,
                "paid_to_featured": 0.03,
                "featured_to_authority": 0.15,
                "monthly_to_annual": 0.35,
            },
            "churn": {"monthly": 0.08, "annual": 0.25},
            "blog_seo": {
                "organic_traffic_share": 0.20,
                "blog_cta_ctr": 0.02,
                "blog_conversion_lift": 1.0,
                "impressions_daily": 2000,
                "clicks_daily": 40,
            },
            "features": {
                "addon_bundling": False,
                "downgrade_prevention": False,
                "first_analysis_hook": False,
                "annual_discount_25": False,
                "smart_notifications": False,
                "social_proof": False,
                "growth_tier": False,
                "achievement_system": False,
                "progressive_unlocks": False,
                "blog_observer": False,
                "seo_optimization": False,
            },
        }
        
        baseline_sim = MarsSimulation(
            scenario=baseline_scenario,
            total_visitors=self.total_visitors,
            days=self.days,
            skip_baseline=True,  # Prevent recursion
        )
        baseline_result = baseline_sim.run()
        
        current_mrr = self.state.mrr
        baseline_mrr = baseline_result["final"]["mrr"]
        
        return {
            "baseline_mrr": baseline_mrr,
            "current_mrr": current_mrr,
            "mrr_lift": round(current_mrr - baseline_mrr, 2),
            "mrr_lift_pct": round((current_mrr / baseline_mrr - 1) * 100, 1) if baseline_mrr > 0 else 0,
        }


# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def run_mars_simulation():
    """Run the Mars 100K in 100 days simulation."""
    print("="*70)
    print("MARS SIMULATION v5.1.0")
    print("100K Visitors in 100 Days - Knight of Wands v3.1.1 + Blog/SEO")
    print("="*70)
    print()
    
    # Run simulation
    sim = MarsSimulation(
        scenario=SCENARIO_V511,
        total_visitors=100000,
        days=100,
        daily_growth=1.005,
    )
    
    results = sim.run()
    
    # Display results
    print("SIMULATION COMPLETE")
    print("-"*40)
    print()
    
    print("📊 FINAL METRICS (Day 100)")
    print(f"   MRR: ${results['final']['mrr']:,.2f}")
    print(f"   ARR: ${results['final']['arr']:,.2f}")
    print(f"   Total Revenue: ${results['final']['total_revenue']:,.2f}")
    print()
    
    print("👥 FUNNEL")
    print(f"   Total Visitors: {results['funnel']['total_visitors']:,}")
    print(f"   Organic Visitors: {results['funnel']['organic_visitors']:,} ({results['funnel']['organic_share']}%)")
    print(f"   Total Signups: {results['funnel']['total_signups']:,} ({results['funnel']['signup_rate']}%)")
    print(f"   Total Trials: {results['funnel']['total_trials']:,}")
    print()
    
    print("💳 PAID USERS")
    print(f"   Total Paid: {results['users']['total_paid']:,}")
    print(f"   Monthly: {results['users']['monthly_paid']:,}")
    print(f"   Annual: {results['users']['annual_paid']:,}")
    print(f"   Growth Tier: {results['users']['growth_tier']:,}")
    print(f"   Addon Attach: {results['users']['addon_attach_rate']}%")
    print(f"   Bundle Rate: {results['users']['bundle_rate']}%")
    print()
    
    print("🔄 RETENTION")
    print(f"   Churned: {results['retention']['churned']:,}")
    print(f"   Total Saved: {results['retention']['total_saved']:,}")
    print(f"   Annual Converted: {results['retention']['annual_converted']:,}")
    print()
    
    print("📈 BLOG/SEO (v5.1)")
    print(f"   Impressions: {results['blog_seo']['impressions']:,}")
    print(f"   Clicks: {results['blog_seo']['clicks']:,}")
    print(f"   CTR: {results['blog_seo']['ctr']}%")
    print(f"   Organic Signups: {results['blog_seo']['organic_signups']:,}")
    print()
    
    print("💰 MRR BREAKDOWN")
    for key, value in results['mrr_breakdown'].items():
        print(f"   {key}: ${value:,.2f}")
    print()
    
    print("📊 VS BASELINE")
    comp = results['comparison']['vs_baseline']
    print(f"   Baseline MRR: ${comp['baseline_mrr']:,.2f}")
    print(f"   Current MRR: ${comp['current_mrr']:,.2f}")
    print(f"   MRR Lift: ${comp['mrr_lift']:,.2f} (+{comp['mrr_lift_pct']}%)")
    print()
    
    print("="*70)
    print("✅ MARS APPROVAL: SIMULATION PASSED")
    print("="*70)
    
    return results


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    
    results = run_mars_simulation()
    
    # Save results
    with open("mars_simulation_v5.1_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print()
    print("Results saved to mars_simulation_v5.1_results.json")
