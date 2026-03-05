#!/usr/bin/env python3
"""
QUIRRELY SIMULATION ENGINE v1.0
Generates synthetic user journeys through the token economy.

This engine simulates users progressing through:
- Entry (direct vs .com redirect)
- Signup and first analysis
- Trial and conversion
- Feature usage and streaks
- Featured and Authority achievement

The simulation is:
- Seeded (reproducible)
- Configurable (adjustable probabilities)
- Self-documenting (tracks all state changes)
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

from value_functions import (
    TokenGeneration,
    UserState,
    calculate_token_value,
    calculate_generation_upgrade,
    calculate_streak_break,
    calculate_inactivity_decay,
    calculate_churn_risk,
)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    
    # Scale
    total_users: int = 4667
    simulation_days: int = 90
    seed: int = 42
    
    # Traffic distribution
    direct_traffic_pct: float = 0.60      # 60% direct to country domains
    com_traffic_pct: float = 0.40         # 40% via quirrely.com
    
    # Country distribution (of .com traffic)
    com_to_ca_pct: float = 0.35
    com_to_uk_pct: float = 0.30
    com_to_au_pct: float = 0.20
    com_to_nz_pct: float = 0.10
    com_to_other_pct: float = 0.05        # Defaults to CA
    
    # Funnel conversion rates
    signup_rate: float = 0.30             # Visitors → Signup
    first_analysis_rate: float = 0.60     # Signup → First analysis (within 7 days)
    hit_limit_rate: float = 0.40          # First analysis → Hit word limit (within 30 days)
    trial_start_rate: float = 0.70        # Hit limit → Start trial
    trial_convert_rate: float = 0.25      # Trial → Paid
    featured_eligible_rate: float = 0.15  # Paid → Featured eligible
    featured_submit_rate: float = 0.60    # Eligible → Submit
    featured_approve_rate: float = 0.70   # Submit → Approved
    authority_rate: float = 0.10          # Featured → Authority (long-term)
    
    # Behavioral rates
    daily_active_rate: float = 0.30       # Probability of being active on any day
    streak_continue_rate: float = 0.70    # Probability of continuing streak
    exploration_rate: float = 0.20        # Probability of exploring new stance
    
    # Churn rates
    base_churn_rate: float = 0.02         # Base monthly churn
    inactive_churn_multiplier: float = 3.0  # Churn multiplier for inactive users
    
    # Time factors
    avg_days_to_signup: int = 2
    avg_days_to_first_analysis: int = 3
    avg_days_to_hit_limit: int = 14
    trial_duration_days: int = 7
    avg_days_to_featured_eligible: int = 45
    avg_days_to_authority: int = 120


# ═══════════════════════════════════════════════════════════════════════════
# USER JOURNEY STAGES
# ═══════════════════════════════════════════════════════════════════════════

class JourneyStage(str, Enum):
    VISITOR = "visitor"
    SIGNED_UP = "signed_up"
    FIRST_ANALYSIS = "first_analysis"
    HIT_LIMIT = "hit_limit"
    TRIAL_STARTED = "trial_started"
    TRIAL_CONVERTED = "trial_converted"
    SUBSCRIBED = "subscribed"
    FEATURED_ELIGIBLE = "featured_eligible"
    FEATURED_SUBMITTED = "featured_submitted"
    FEATURED_APPROVED = "featured_approved"
    AUTHORITY = "authority"
    CHURNED = "churned"


STAGE_ORDER = [
    JourneyStage.VISITOR,
    JourneyStage.SIGNED_UP,
    JourneyStage.FIRST_ANALYSIS,
    JourneyStage.HIT_LIMIT,
    JourneyStage.TRIAL_STARTED,
    JourneyStage.TRIAL_CONVERTED,
    JourneyStage.SUBSCRIBED,
    JourneyStage.FEATURED_ELIGIBLE,
    JourneyStage.FEATURED_SUBMITTED,
    JourneyStage.FEATURED_APPROVED,
    JourneyStage.AUTHORITY,
]


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATED USER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SimulatedUser:
    """A synthetic user in the simulation."""
    
    id: str
    country_code: str
    entry_type: str  # 'direct' or 'via_com'
    entry_domain: str
    
    # Journey state
    current_stage: JourneyStage = JourneyStage.VISITOR
    stage_history: List[Tuple[int, str]] = field(default_factory=list)  # (day, stage)
    
    # Token state
    token_generation: int = 0
    token_value: float = 0.0
    token_history: List[Dict] = field(default_factory=list)
    
    # Behavioral state
    days_active: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    stances_explored: int = 0
    last_active_day: int = -1
    
    # Subscription state
    is_trial: bool = False
    trial_start_day: Optional[int] = None
    is_subscribed: bool = False
    subscription_start_day: Optional[int] = None
    
    # Featured state
    is_featured: bool = False
    featured_day: Optional[int] = None
    is_authority: bool = False
    authority_day: Optional[int] = None
    
    # Churn state
    churned: bool = False
    churn_day: Optional[int] = None
    
    # Simulation metadata
    created_day: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "country_code": self.country_code,
            "entry_type": self.entry_type,
            "current_stage": self.current_stage.value,
            "token_generation": self.token_generation,
            "token_value": self.token_value,
            "current_streak": self.current_streak,
            "stances_explored": self.stances_explored,
            "is_subscribed": self.is_subscribed,
            "is_featured": self.is_featured,
            "is_authority": self.is_authority,
            "churned": self.churned,
        }


# ═══════════════════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class SimulationEngine:
    """
    Engine for running user journey simulations.
    
    The engine:
    1. Creates synthetic users based on traffic distribution
    2. Advances users through journey stages probabilistically
    3. Tracks token generation and value changes
    4. Simulates behavioral patterns (streaks, exploration)
    5. Records all state changes for analysis
    """
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        self.users: List[SimulatedUser] = []
        self.daily_events: List[Dict] = []
        self.current_day: int = 0
        
        # Seed random for reproducibility
        random.seed(self.config.seed)
    
    def run(self) -> Dict:
        """Run the full simulation."""
        # Initialize users
        self._create_users()
        
        # Run day by day
        for day in range(self.config.simulation_days):
            self.current_day = day
            self._simulate_day(day)
        
        # Compile results
        return self._compile_results()
    
    def _create_users(self):
        """Create all synthetic users with appropriate distribution."""
        users_per_country = self.config.total_users // 4
        
        # Direct traffic (60%): 1000 per country
        direct_per_country = int(users_per_country * self.config.direct_traffic_pct / 0.6)
        
        # Via .com traffic (40%): distributed by geo
        com_total = int(self.config.total_users * self.config.com_traffic_pct)
        com_ca = int(com_total * self.config.com_to_ca_pct)
        com_uk = int(com_total * self.config.com_to_uk_pct)
        com_au = int(com_total * self.config.com_to_au_pct)
        com_nz = int(com_total * self.config.com_to_nz_pct)
        com_other = com_total - com_ca - com_uk - com_au - com_nz  # Goes to CA
        
        user_id = 0
        
        # Create direct users
        for country in ["ca", "uk", "au", "nz"]:
            domain = {
                "ca": "quirrely.ca",
                "uk": "quirrely.co.uk",
                "au": "quirrely.com.au",
                "nz": "quirrely.co.nz",
            }[country]
            
            for _ in range(direct_per_country):
                self.users.append(SimulatedUser(
                    id=f"sim_{user_id:05d}",
                    country_code=country,
                    entry_type="direct",
                    entry_domain=domain,
                    created_day=random.randint(0, self.config.simulation_days // 3),
                ))
                user_id += 1
        
        # Create .com redirect users
        com_distribution = [
            ("ca", com_ca + com_other),
            ("uk", com_uk),
            ("au", com_au),
            ("nz", com_nz),
        ]
        
        for country, count in com_distribution:
            domain = {
                "ca": "quirrely.ca",
                "uk": "quirrely.co.uk",
                "au": "quirrely.com.au",
                "nz": "quirrely.co.nz",
            }[country]
            
            for _ in range(count):
                self.users.append(SimulatedUser(
                    id=f"sim_{user_id:05d}",
                    country_code=country,
                    entry_type="via_com",
                    entry_domain=domain,
                    created_day=random.randint(0, self.config.simulation_days // 3),
                ))
                user_id += 1
    
    def _simulate_day(self, day: int):
        """Simulate one day of user activity."""
        for user in self.users:
            if user.created_day > day:
                continue  # User hasn't arrived yet
            
            if user.churned:
                continue  # User has churned
            
            self._simulate_user_day(user, day)
    
    def _simulate_user_day(self, user: SimulatedUser, day: int):
        """Simulate one day for a single user."""
        days_since_arrival = day - user.created_day
        
        # Check for churn
        if self._should_churn(user, day):
            self._churn_user(user, day)
            return
        
        # Progress through stages
        self._try_stage_progression(user, day, days_since_arrival)
        
        # Behavioral simulation (if past first analysis)
        if user.current_stage.value >= JourneyStage.FIRST_ANALYSIS.value:
            self._simulate_behavior(user, day)
    
    def _should_churn(self, user: SimulatedUser, day: int) -> bool:
        """Determine if user churns today."""
        if user.current_stage == JourneyStage.VISITOR:
            return False  # Can't churn if never signed up
        
        days_inactive = day - user.last_active_day if user.last_active_day >= 0 else 0
        
        # Calculate churn probability
        churn_prob = self.config.base_churn_rate / 30  # Daily rate
        
        if days_inactive > 7:
            churn_prob *= self.config.inactive_churn_multiplier
        
        if days_inactive > 30:
            churn_prob *= 2
        
        # Subscribers churn less
        if user.is_subscribed:
            churn_prob *= 0.5
        
        # Featured churn even less
        if user.is_featured:
            churn_prob *= 0.3
        
        return random.random() < churn_prob
    
    def _churn_user(self, user: SimulatedUser, day: int):
        """Mark user as churned."""
        user.churned = True
        user.churn_day = day
        user.stage_history.append((day, "churned"))
        
        self.daily_events.append({
            "day": day,
            "user_id": user.id,
            "event": "churn",
            "from_stage": user.current_stage.value,
            "value_at_churn": user.token_value,
        })
    
    def _try_stage_progression(self, user: SimulatedUser, day: int, days_since_arrival: int):
        """Try to progress user to next stage."""
        stage = user.current_stage
        
        if stage == JourneyStage.VISITOR:
            if days_since_arrival >= self.config.avg_days_to_signup:
                if random.random() < self.config.signup_rate:
                    self._advance_stage(user, JourneyStage.SIGNED_UP, day)
        
        elif stage == JourneyStage.SIGNED_UP:
            if random.random() < self.config.first_analysis_rate / self.config.avg_days_to_first_analysis:
                self._advance_stage(user, JourneyStage.FIRST_ANALYSIS, day)
                self._generate_token(user, 0, 1, day, "first_analysis")
        
        elif stage == JourneyStage.FIRST_ANALYSIS:
            if random.random() < self.config.hit_limit_rate / self.config.avg_days_to_hit_limit:
                self._advance_stage(user, JourneyStage.HIT_LIMIT, day)
        
        elif stage == JourneyStage.HIT_LIMIT:
            if random.random() < self.config.trial_start_rate:
                self._advance_stage(user, JourneyStage.TRIAL_STARTED, day)
                user.is_trial = True
                user.trial_start_day = day
        
        elif stage == JourneyStage.TRIAL_STARTED:
            days_in_trial = day - user.trial_start_day
            if days_in_trial >= self.config.trial_duration_days:
                if random.random() < self.config.trial_convert_rate:
                    self._advance_stage(user, JourneyStage.SUBSCRIBED, day)
                    user.is_trial = False
                    user.is_subscribed = True
                    user.subscription_start_day = day
                else:
                    self._advance_stage(user, JourneyStage.TRIAL_CONVERTED, day)
                    user.is_trial = False
        
        elif stage == JourneyStage.SUBSCRIBED:
            if user.token_generation >= 3:  # Behavioral stage
                if random.random() < self.config.featured_eligible_rate / self.config.avg_days_to_featured_eligible:
                    self._advance_stage(user, JourneyStage.FEATURED_ELIGIBLE, day)
        
        elif stage == JourneyStage.FEATURED_ELIGIBLE:
            if random.random() < self.config.featured_submit_rate / 7:  # ~1 week to decide
                self._advance_stage(user, JourneyStage.FEATURED_SUBMITTED, day)
        
        elif stage == JourneyStage.FEATURED_SUBMITTED:
            if random.random() < self.config.featured_approve_rate / 3:  # ~3 days review
                self._advance_stage(user, JourneyStage.FEATURED_APPROVED, day)
                user.is_featured = True
                user.featured_day = day
                self._generate_token(user, user.token_generation, 4, day, "featured_approved")
        
        elif stage == JourneyStage.FEATURED_APPROVED:
            days_as_featured = day - user.featured_day
            if days_as_featured >= 90:  # 90 days as Featured required
                if random.random() < self.config.authority_rate / (self.config.avg_days_to_authority - 90):
                    self._advance_stage(user, JourneyStage.AUTHORITY, day)
                    user.is_authority = True
                    user.authority_day = day
                    self._generate_token(user, 4, 5, day, "authority_achieved")
    
    def _advance_stage(self, user: SimulatedUser, new_stage: JourneyStage, day: int):
        """Advance user to a new stage."""
        old_stage = user.current_stage
        user.current_stage = new_stage
        user.stage_history.append((day, new_stage.value))
        
        self.daily_events.append({
            "day": day,
            "user_id": user.id,
            "event": "stage_advance",
            "from_stage": old_stage.value,
            "to_stage": new_stage.value,
        })
    
    def _simulate_behavior(self, user: SimulatedUser, day: int):
        """Simulate daily behavioral patterns."""
        # Is user active today?
        activity_prob = self.config.daily_active_rate
        
        # Subscribers more active
        if user.is_subscribed:
            activity_prob *= 1.5
        
        # Featured even more active
        if user.is_featured:
            activity_prob *= 1.3
        
        is_active_today = random.random() < activity_prob
        
        if is_active_today:
            user.days_active += 1
            
            # Streak logic
            if user.last_active_day == day - 1:
                # Continue streak
                if random.random() < self.config.streak_continue_rate:
                    user.current_streak += 1
                    user.longest_streak = max(user.longest_streak, user.current_streak)
                    
                    # Check for behavioral milestone (Gen 1 → Gen 3)
                    if user.current_streak >= 7 and user.token_generation < 3:
                        self._generate_token(user, user.token_generation, 3, day, "streak_7_day")
                else:
                    # Streak break
                    if user.current_streak >= 3:
                        self._record_streak_break(user, day)
                    user.current_streak = 1
            else:
                # New streak
                if user.current_streak >= 3:
                    self._record_streak_break(user, day)
                user.current_streak = 1
            
            user.last_active_day = day
            
            # Exploration
            if random.random() < self.config.exploration_rate:
                user.stances_explored += 1
                
                # Check for exploration milestone (Gen 1 → Gen 2)
                if user.stances_explored >= 3 and user.token_generation < 2:
                    self._generate_token(user, user.token_generation, 2, day, "exploration_milestone")
            
            # Recalculate token value
            self._recalculate_value(user, day)
    
    def _generate_token(self, user: SimulatedUser, from_gen: int, to_gen: int, day: int, reason: str):
        """Generate token upgrade."""
        old_value = user.token_value
        result = calculate_generation_upgrade(max(old_value, 1.0), from_gen, to_gen)
        
        user.token_generation = to_gen
        user.token_value = result.value_after
        
        user.token_history.append({
            "day": day,
            "from_gen": from_gen,
            "to_gen": to_gen,
            "value_before": old_value,
            "value_after": result.value_after,
            "reason": reason,
        })
        
        self.daily_events.append({
            "day": day,
            "user_id": user.id,
            "event": "token_generation",
            "from_gen": from_gen,
            "to_gen": to_gen,
            "value_delta": result.value_delta,
        })
    
    def _record_streak_break(self, user: SimulatedUser, day: int):
        """Record a streak break."""
        old_value = user.token_value
        result = calculate_streak_break(old_value)
        
        user.token_value = result.value_after
        
        self.daily_events.append({
            "day": day,
            "user_id": user.id,
            "event": "streak_break",
            "streak_length": user.current_streak,
            "value_lost": result.value_delta,
        })
    
    def _recalculate_value(self, user: SimulatedUser, day: int):
        """Recalculate user's token value based on current state."""
        state = UserState(
            token_generation=user.token_generation,
            current_value=user.token_value,
            streak_days=user.current_streak,
            days_since_active=day - user.last_active_day if user.last_active_day >= 0 else 0,
            stances_explored=user.stances_explored,
            is_featured=user.is_featured,
            is_authority=user.is_authority,
            country_code=user.country_code,
        )
        
        result = calculate_token_value(state)
        user.token_value = result.final_value
    
    def _compile_results(self) -> Dict:
        """Compile simulation results."""
        # Stage distribution
        stage_counts = {}
        for stage in JourneyStage:
            stage_counts[stage.value] = sum(1 for u in self.users if u.current_stage == stage)
        
        # Country breakdown
        country_stats = {}
        for country in ["ca", "uk", "au", "nz"]:
            country_users = [u for u in self.users if u.country_code == country]
            country_stats[country] = {
                "total_users": len(country_users),
                "signed_up": sum(1 for u in country_users if u.current_stage.value >= JourneyStage.SIGNED_UP.value),
                "subscribed": sum(1 for u in country_users if u.is_subscribed),
                "featured": sum(1 for u in country_users if u.is_featured),
                "authority": sum(1 for u in country_users if u.is_authority),
                "churned": sum(1 for u in country_users if u.churned),
                "total_value": sum(u.token_value for u in country_users),
                "avg_value": sum(u.token_value for u in country_users) / len(country_users) if country_users else 0,
            }
        
        # Entry type comparison
        direct_users = [u for u in self.users if u.entry_type == "direct"]
        com_users = [u for u in self.users if u.entry_type == "via_com"]
        
        entry_stats = {
            "direct": {
                "total_users": len(direct_users),
                "conversion_rate": sum(1 for u in direct_users if u.is_subscribed) / len(direct_users) if direct_users else 0,
                "avg_value": sum(u.token_value for u in direct_users) / len(direct_users) if direct_users else 0,
            },
            "via_com": {
                "total_users": len(com_users),
                "conversion_rate": sum(1 for u in com_users if u.is_subscribed) / len(com_users) if com_users else 0,
                "avg_value": sum(u.token_value for u in com_users) / len(com_users) if com_users else 0,
            },
        }
        
        # Token generation distribution
        gen_distribution = {}
        for gen in range(6):
            gen_users = [u for u in self.users if u.token_generation == gen]
            gen_distribution[gen] = {
                "count": len(gen_users),
                "total_value": sum(u.token_value for u in gen_users),
            }
        
        # Value metrics
        all_values = [u.token_value for u in self.users]
        value_metrics = {
            "total_value": sum(all_values),
            "mean_value": sum(all_values) / len(all_values) if all_values else 0,
            "max_value": max(all_values) if all_values else 0,
            "min_value": min(all_values) if all_values else 0,
        }
        
        # Funnel conversion rates
        funnel_rates = {}
        stages = [
            ("visitor", "signed_up"),
            ("signed_up", "first_analysis"),
            ("first_analysis", "hit_limit"),
            ("hit_limit", "trial_started"),
            ("trial_started", "subscribed"),
            ("subscribed", "featured_eligible"),
            ("featured_eligible", "featured_submitted"),
            ("featured_submitted", "featured_approved"),
            ("featured_approved", "authority"),
        ]
        
        for from_stage, to_stage in stages:
            from_count = sum(1 for u in self.users if u.current_stage.value >= JourneyStage[from_stage.upper()].value)
            to_count = sum(1 for u in self.users if u.current_stage.value >= JourneyStage[to_stage.upper()].value)
            funnel_rates[f"{from_stage}_to_{to_stage}"] = to_count / from_count if from_count > 0 else 0
        
        return {
            "config": asdict(self.config),
            "summary": {
                "total_users": len(self.users),
                "simulation_days": self.config.simulation_days,
                "total_events": len(self.daily_events),
            },
            "stage_distribution": stage_counts,
            "country_stats": country_stats,
            "entry_stats": entry_stats,
            "generation_distribution": gen_distribution,
            "value_metrics": value_metrics,
            "funnel_rates": funnel_rates,
            "churn_stats": {
                "total_churned": sum(1 for u in self.users if u.churned),
                "churn_rate": sum(1 for u in self.users if u.churned) / len(self.users),
            },
        }
    
    def get_user_details(self) -> List[Dict]:
        """Get detailed state for all users."""
        return [u.to_dict() for u in self.users]
    
    def get_daily_events(self) -> List[Dict]:
        """Get all recorded daily events."""
        return self.daily_events
