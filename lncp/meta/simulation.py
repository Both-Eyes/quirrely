#!/usr/bin/env python3
"""
LNCP META: SIMULATION v1.0
Master Test simulation engine integrated into LNCP Core.

Simulates user behavior and token economy to identify
optimization opportunities.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import math

# Import from Engine
import sys
sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app')
from lncp.engine.value import TokenGeneration, calculate_token_value, GENERATION_MULTIPLIERS


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION CONFIG
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SimulationConfig:
    """Configuration for simulation."""
    total_users: int = 1000
    simulation_days: int = 90
    seed: int = 42
    
    # Traffic
    direct_traffic_pct: float = 0.60
    com_traffic_pct: float = 0.40
    com_to_ca_pct: float = 0.35
    com_to_uk_pct: float = 0.30
    com_to_au_pct: float = 0.20
    com_to_nz_pct: float = 0.10
    com_to_other_pct: float = 0.05
    
    # Funnel
    signup_rate: float = 0.30
    first_analysis_rate: float = 0.60
    hit_limit_rate: float = 0.40
    trial_start_rate: float = 0.70
    trial_convert_rate: float = 0.25
    featured_eligible_rate: float = 0.15
    featured_submit_rate: float = 0.60
    featured_approve_rate: float = 0.70
    authority_rate: float = 0.10
    
    # Behavior
    daily_active_rate: float = 0.30
    streak_continue_rate: float = 0.70
    exploration_rate: float = 0.20
    
    # Churn
    base_churn_rate: float = 0.02
    inactive_churn_multiplier: float = 3.0
    
    # Timing
    avg_days_to_signup: int = 2
    avg_days_to_first_analysis: int = 3
    avg_days_to_hit_limit: int = 14
    trial_duration_days: int = 7
    avg_days_to_featured_eligible: int = 45
    avg_days_to_authority: int = 120


@dataclass
class BaselineExpectations:
    """Baseline expectations for comparison."""
    signup_rate: float = 0.30
    first_analysis_rate: float = 0.60
    trial_start_rate: float = 0.70
    trial_convert_rate: float = 0.25
    featured_approve_rate: float = 0.70
    avg_user_value: float = 3.5
    value_per_subscriber: float = 8.0
    avg_streak_length: float = 5.0
    exploration_rate: float = 0.20
    monthly_churn_rate: float = 0.05
    token_velocity: float = 0.5
    country_deviation_tolerance: float = 0.15
    entry_type_deviation_tolerance: float = 0.10


# ═══════════════════════════════════════════════════════════════════════════
# USER SIMULATION
# ═══════════════════════════════════════════════════════════════════════════

class UserStage(str, Enum):
    VISITOR = "visitor"
    SIGNED_UP = "signed_up"
    FIRST_ANALYSIS = "first_analysis"
    HIT_LIMIT = "hit_limit"
    TRIAL_STARTED = "trial_started"
    SUBSCRIBED = "subscribed"
    FEATURED_ELIGIBLE = "featured_eligible"
    FEATURED_APPROVED = "featured_approved"
    AUTHORITY = "authority"
    CHURNED = "churned"


@dataclass
class SimulatedUser:
    """A simulated user."""
    user_id: str
    country: str
    entry_type: str
    stage: UserStage
    generation: TokenGeneration
    
    created_day: int
    last_active_day: int
    analyses_count: int = 0
    streak_days: int = 0
    milestones: int = 0
    
    token_value: float = 0.0
    churned: bool = False


class SimulationEngine:
    """Simulates user behavior over time."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        random.seed(config.seed)
        self.users: List[SimulatedUser] = []
        self.events: List[Dict] = []
    
    def run(self) -> Dict:
        """Run the full simulation."""
        # Generate users
        self._generate_users()
        
        # Simulate each day
        for day in range(self.config.simulation_days):
            self._simulate_day(day)
        
        # Calculate final values
        self._calculate_final_values()
        
        return self._compile_results()
    
    def _generate_users(self):
        """Generate initial users."""
        countries = {
            "ca": self.config.com_to_ca_pct,
            "uk": self.config.com_to_uk_pct,
            "au": self.config.com_to_au_pct,
            "nz": self.config.com_to_nz_pct,
        }
        
        for i in range(self.config.total_users):
            # Determine entry
            is_direct = random.random() < self.config.direct_traffic_pct
            
            if is_direct:
                country = random.choices(list(countries.keys()), weights=list(countries.values()))[0]
                entry_type = "direct"
            else:
                country = random.choices(list(countries.keys()), weights=list(countries.values()))[0]
                entry_type = "via_com"
            
            # Determine arrival day
            arrival_day = random.randint(0, self.config.simulation_days - 1)
            
            user = SimulatedUser(
                user_id=f"user_{i:05d}",
                country=country,
                entry_type=entry_type,
                stage=UserStage.VISITOR,
                generation=TokenGeneration.GEN_0_RAW,
                created_day=arrival_day,
                last_active_day=arrival_day,
            )
            self.users.append(user)
    
    def _simulate_day(self, day: int):
        """Simulate a single day."""
        for user in self.users:
            if user.churned:
                continue
            if user.created_day > day:
                continue
            
            days_since_created = day - user.created_day
            
            # Progress through funnel
            self._progress_user(user, day, days_since_created)
            
            # Check for churn
            self._check_churn(user, day)
    
    def _progress_user(self, user: SimulatedUser, day: int, days_active: int):
        """Progress user through funnel."""
        cfg = self.config
        
        if user.stage == UserStage.VISITOR:
            if days_active >= cfg.avg_days_to_signup and random.random() < cfg.signup_rate:
                user.stage = UserStage.SIGNED_UP
                user.generation = TokenGeneration.GEN_1_PROFILE
                self._log_event(user, day, "signed_up")
        
        elif user.stage == UserStage.SIGNED_UP:
            if random.random() < cfg.first_analysis_rate:
                user.stage = UserStage.FIRST_ANALYSIS
                user.analyses_count = 1
                user.generation = TokenGeneration.GEN_2_EXPLORED
                self._log_event(user, day, "first_analysis")
        
        elif user.stage == UserStage.FIRST_ANALYSIS:
            # Daily activity
            if random.random() < cfg.daily_active_rate:
                user.analyses_count += 1
                user.last_active_day = day
                user.streak_days += 1
            
            if user.analyses_count >= 5 and random.random() < cfg.hit_limit_rate:
                user.stage = UserStage.HIT_LIMIT
                self._log_event(user, day, "hit_limit")
        
        elif user.stage == UserStage.HIT_LIMIT:
            if random.random() < cfg.trial_start_rate:
                user.stage = UserStage.TRIAL_STARTED
                self._log_event(user, day, "trial_started")
        
        elif user.stage == UserStage.TRIAL_STARTED:
            if days_active >= cfg.trial_duration_days:
                if random.random() < cfg.trial_convert_rate:
                    user.stage = UserStage.SUBSCRIBED
                    user.generation = TokenGeneration.GEN_3_BEHAVIORAL
                    self._log_event(user, day, "subscribed")
        
        elif user.stage == UserStage.SUBSCRIBED:
            # Daily activity
            if random.random() < cfg.daily_active_rate:
                user.analyses_count += 1
                user.last_active_day = day
                if random.random() < cfg.streak_continue_rate:
                    user.streak_days += 1
            
            if days_active >= cfg.avg_days_to_featured_eligible:
                if random.random() < cfg.featured_eligible_rate:
                    user.stage = UserStage.FEATURED_ELIGIBLE
                    self._log_event(user, day, "featured_eligible")
        
        elif user.stage == UserStage.FEATURED_ELIGIBLE:
            if random.random() < cfg.featured_submit_rate * cfg.featured_approve_rate:
                user.stage = UserStage.FEATURED_APPROVED
                user.generation = TokenGeneration.GEN_4_FEATURED
                self._log_event(user, day, "featured_approved")
        
        elif user.stage == UserStage.FEATURED_APPROVED:
            if days_active >= cfg.avg_days_to_authority:
                if random.random() < cfg.authority_rate:
                    user.stage = UserStage.AUTHORITY
                    user.generation = TokenGeneration.GEN_5_AUTHORITY
                    self._log_event(user, day, "authority")
    
    def _check_churn(self, user: SimulatedUser, day: int):
        """Check if user churns."""
        if user.stage not in [UserStage.SUBSCRIBED, UserStage.FEATURED_ELIGIBLE, 
                               UserStage.FEATURED_APPROVED, UserStage.AUTHORITY]:
            return
        
        days_inactive = day - user.last_active_day
        churn_rate = self.config.base_churn_rate
        
        if days_inactive > 7:
            churn_rate *= self.config.inactive_churn_multiplier
        
        if random.random() < churn_rate:
            user.churned = True
            user.stage = UserStage.CHURNED
            self._log_event(user, day, "churned")
    
    def _log_event(self, user: SimulatedUser, day: int, event_type: str):
        """Log a simulation event."""
        self.events.append({
            "user_id": user.user_id,
            "day": day,
            "event": event_type,
            "country": user.country,
            "generation": user.generation.value,
        })
    
    def _calculate_final_values(self):
        """Calculate final token values for all users."""
        for user in self.users:
            value = calculate_token_value(
                user_id=user.user_id,
                analyses_count=user.analyses_count,
                unique_profiles_seen=min(user.analyses_count, 10),
                streak_days=user.streak_days,
                milestones_achieved=user.milestones,
                generation=user.generation,
                days_inactive=self.config.simulation_days - user.last_active_day,
            )
            user.token_value = value.final_value
    
    def _compile_results(self) -> Dict:
        """Compile simulation results."""
        # Count by stage
        stage_counts = {s.value: 0 for s in UserStage}
        for user in self.users:
            stage_counts[user.stage.value] += 1
        
        # Count by country
        country_stats = {}
        for country in ["ca", "uk", "au", "nz"]:
            country_users = [u for u in self.users if u.country == country]
            country_stats[country] = {
                "total_users": len(country_users),
                "signed_up": len([u for u in country_users if u.stage != UserStage.VISITOR]),
                "subscribed": len([u for u in country_users if u.stage in [
                    UserStage.SUBSCRIBED, UserStage.FEATURED_ELIGIBLE,
                    UserStage.FEATURED_APPROVED, UserStage.AUTHORITY
                ]]),
                "featured": len([u for u in country_users if u.stage in [
                    UserStage.FEATURED_APPROVED, UserStage.AUTHORITY
                ]]),
                "churned": len([u for u in country_users if u.churned]),
                "total_value": sum(u.token_value for u in country_users),
                "avg_value": sum(u.token_value for u in country_users) / max(1, len(country_users)),
            }
        
        # Count by entry type
        entry_stats = {}
        for entry in ["direct", "via_com"]:
            entry_users = [u for u in self.users if u.entry_type == entry]
            subscribed = len([u for u in entry_users if u.stage in [
                UserStage.SUBSCRIBED, UserStage.FEATURED_ELIGIBLE,
                UserStage.FEATURED_APPROVED, UserStage.AUTHORITY
            ]])
            entry_stats[entry] = {
                "total_users": len(entry_users),
                "conversion_rate": subscribed / max(1, len(entry_users)),
                "avg_value": sum(u.token_value for u in entry_users) / max(1, len(entry_users)),
            }
        
        # Generation distribution
        gen_dist = {}
        for gen in TokenGeneration:
            gen_users = [u for u in self.users if u.generation == gen]
            gen_dist[gen.value] = {
                "count": len(gen_users),
                "total_value": sum(u.token_value for u in gen_users),
            }
        
        # Value metrics
        all_values = [u.token_value for u in self.users]
        
        # Churn stats
        total_subs = len([u for u in self.users if u.stage in [
            UserStage.SUBSCRIBED, UserStage.FEATURED_ELIGIBLE,
            UserStage.FEATURED_APPROVED, UserStage.AUTHORITY
        ] or u.churned])
        total_churned = len([u for u in self.users if u.churned])
        
        # Funnel rates
        visitors = len(self.users)
        signed_up = len([u for u in self.users if u.stage != UserStage.VISITOR])
        first_analysis = len([u for u in self.users if u.analyses_count > 0])
        subscribed = len([u for u in self.users if u.stage in [
            UserStage.SUBSCRIBED, UserStage.FEATURED_ELIGIBLE,
            UserStage.FEATURED_APPROVED, UserStage.AUTHORITY
        ] or u.churned])
        
        return {
            "config": {
                "total_users": self.config.total_users,
                "simulation_days": self.config.simulation_days,
                "seed": self.config.seed,
            },
            "summary": {
                "total_users": len(self.users),
                "simulation_days": self.config.simulation_days,
                "total_events": len(self.events),
            },
            "stage_distribution": stage_counts,
            "country_stats": country_stats,
            "entry_stats": entry_stats,
            "generation_distribution": gen_dist,
            "value_metrics": {
                "total_value": sum(all_values),
                "mean_value": sum(all_values) / max(1, len(all_values)),
                "max_value": max(all_values) if all_values else 0,
            },
            "churn_stats": {
                "total_churned": total_churned,
                "churn_rate": total_churned / max(1, total_subs),
            },
            "funnel_rates": {
                "visitor_to_signed_up": signed_up / max(1, visitors),
                "signed_up_to_first_analysis": first_analysis / max(1, signed_up),
                "first_analysis_to_subscribed": subscribed / max(1, first_analysis),
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# MASTER TEST
# ═══════════════════════════════════════════════════════════════════════════

class MasterTest:
    """Master Test orchestration."""
    
    def __init__(
        self,
        config: Optional[SimulationConfig] = None,
        baseline: Optional[BaselineExpectations] = None,
    ):
        self.config = config or SimulationConfig()
        self.baseline = baseline or BaselineExpectations()
    
    def run(self) -> Dict:
        """Run the Master Test."""
        started_at = datetime.utcnow()
        
        # Run simulation
        engine = SimulationEngine(self.config)
        sim_results = engine.run()
        
        # Generate prescriptive actions
        actions = self._generate_actions(sim_results)
        
        # Calculate system pulse
        pulse = self._calculate_pulse(sim_results, actions)
        
        completed_at = datetime.utcnow()
        
        return {
            "meta": {
                "run_started_at": started_at.isoformat(),
                "run_completed_at": completed_at.isoformat(),
                "duration_seconds": (completed_at - started_at).total_seconds(),
            },
            "config": {
                "total_users": self.config.total_users,
                "simulation_days": self.config.simulation_days,
                "seed": self.config.seed,
            },
            "baseline": {
                "signup_rate": self.baseline.signup_rate,
                "first_analysis_rate": self.baseline.first_analysis_rate,
                "trial_start_rate": self.baseline.trial_start_rate,
                "trial_convert_rate": self.baseline.trial_convert_rate,
                "monthly_churn_rate": self.baseline.monthly_churn_rate,
            },
            "simulation_results": sim_results,
            "prescriptive_actions": actions,
            "system_pulse": pulse,
        }
    
    def _generate_actions(self, sim: Dict) -> Dict:
        """Generate prescriptive actions from simulation results."""
        actions = []
        
        # Check funnel rates
        funnel = sim.get("funnel_rates", {})
        
        signup_rate = funnel.get("visitor_to_signed_up", 0)
        if signup_rate < self.baseline.signup_rate * 0.8:
            actions.append({
                "severity": "risk",
                "category": "funnel",
                "title": "Signup conversion below baseline",
                "description": f"Signup at {signup_rate*100:.1f}% vs {self.baseline.signup_rate*100:.1f}% expected",
                "current_value": signup_rate,
                "baseline_value": self.baseline.signup_rate,
                "delta_percent": (signup_rate - self.baseline.signup_rate) / self.baseline.signup_rate * 100,
                "action_recommended": "Audit signup flow for friction",
                "priority_score": 160,
            })
        
        # Check churn
        churn = sim.get("churn_stats", {}).get("churn_rate", 0)
        if churn < self.baseline.monthly_churn_rate:
            actions.append({
                "severity": "opportunity",
                "category": "retention",
                "title": "Churn rate better than expected",
                "description": f"Churn at {churn*100:.1f}% vs {self.baseline.monthly_churn_rate*100:.1f}% expected",
                "current_value": churn,
                "baseline_value": self.baseline.monthly_churn_rate,
                "delta_percent": (churn - self.baseline.monthly_churn_rate) / self.baseline.monthly_churn_rate * 100,
                "action_recommended": "Document retention drivers for marketing",
                "priority_score": 140,
            })
        
        # Check value
        avg_value = sim.get("value_metrics", {}).get("mean_value", 0)
        if avg_value < self.baseline.avg_user_value * 0.8:
            actions.append({
                "severity": "watch",
                "category": "value",
                "title": "Average user value below target",
                "description": f"Value at {avg_value:.2f} vs {self.baseline.avg_user_value:.2f} target",
                "current_value": avg_value,
                "baseline_value": self.baseline.avg_user_value,
                "delta_percent": (avg_value - self.baseline.avg_user_value) / self.baseline.avg_user_value * 100,
                "action_recommended": "Review engagement drivers",
                "priority_score": 120,
            })
        
        by_severity = {
            "risk": len([a for a in actions if a["severity"] == "risk"]),
            "watch": len([a for a in actions if a["severity"] == "watch"]),
            "opportunity": len([a for a in actions if a["severity"] == "opportunity"]),
        }
        
        return {
            "total": len(actions),
            "by_severity": by_severity,
            "actions": actions,
        }
    
    def _calculate_pulse(self, sim: Dict, actions: Dict) -> Dict:
        """Calculate system pulse (health score)."""
        # Conversion health
        funnel = sim.get("funnel_rates", {})
        signup = funnel.get("visitor_to_signed_up", 0)
        conversion_health = min(100, int(signup / self.baseline.signup_rate * 100))
        
        # Value health
        avg_value = sim.get("value_metrics", {}).get("mean_value", 0)
        value_health = min(100, int(avg_value / self.baseline.avg_user_value * 100))
        
        # Retention health
        churn = sim.get("churn_stats", {}).get("churn_rate", 1)
        retention_health = min(100, int((1 - churn) / (1 - self.baseline.monthly_churn_rate) * 100))
        
        # Overall health (weighted average)
        overall = int(conversion_health * 0.35 + value_health * 0.35 + retention_health * 0.30)
        
        # Key metrics
        total_users = sum(c.get("total_users", 0) for c in sim.get("country_stats", {}).values())
        total_subscribed = sum(c.get("subscribed", 0) for c in sim.get("country_stats", {}).values())
        
        return {
            "overall_health": overall,
            "health_breakdown": {
                "conversion": conversion_health,
                "value": value_health,
                "retention": retention_health,
            },
            "key_metrics": {
                "total_users": total_users,
                "total_value": sim.get("value_metrics", {}).get("total_value", 0),
                "avg_value": avg_value,
                "subscription_rate": total_subscribed / max(1, total_users),
                "churn_rate": churn,
            },
            "top_actions": actions.get("actions", [])[:5],
        }


def run_master_test(
    config: Optional[SimulationConfig] = None,
    baseline: Optional[BaselineExpectations] = None,
) -> Dict:
    """Convenience function to run Master Test."""
    test = MasterTest(config=config, baseline=baseline)
    return test.run()


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "SimulationConfig",
    "BaselineExpectations",
    "UserStage",
    "SimulatedUser",
    "SimulationEngine",
    "MasterTest",
    "run_master_test",
]
