#!/usr/bin/env python3
"""
QUIRRELY VALUE FUNCTIONS v1.0
The mathematical foundation of the token economy.

These are pure functions - no side effects, deterministic, composable.
They calculate token values, growth rates, decay rates, and system health.

Token Generations:
  Gen 0: Raw user input (feedstock)         Base: 1.0
  Gen 1: Structured profile (LNCP output)   Base: 2.0
  Gen 2: Explored variations                Base: 2.5
  Gen 3: Behavioral patterns                Base: 3.5
  Gen 4: Social validation (Featured)       Base: 7.0
  Gen 5: Authority/permanence               Base: 15.0
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

class TokenGeneration(int, Enum):
    RAW_INPUT = 0
    STRUCTURED_PROFILE = 1
    EXPLORED_VARIATION = 2
    BEHAVIORAL_PATTERN = 3
    SOCIAL_VALIDATION = 4
    AUTHORITY = 5


# Base value for each token generation
BASE_VALUES: Dict[int, float] = {
    0: 1.0,    # Raw input
    1: 2.0,    # Structured profile
    2: 2.5,    # Explored variations
    3: 3.5,    # Behavioral patterns
    4: 7.0,    # Social validation (Featured)
    5: 15.0,   # Authority/permanence
}

# Value multipliers
STREAK_MULTIPLIER_PER_DAY = 0.02      # +2% per streak day
MAX_STREAK_MULTIPLIER = 2.0            # Cap at 2x (100 days)
EXPLORATION_MULTIPLIER_PER_STANCE = 0.05  # +5% per stance explored
MAX_EXPLORATION_MULTIPLIER = 1.5       # Cap at 1.5x (10 stances)
RECENCY_DECAY_PER_DAY = 0.01          # -1% per inactive day
MIN_RECENCY_MULTIPLIER = 0.5           # Floor at 50%

# Upgrade value multipliers (value gained when upgrading generation)
UPGRADE_MULTIPLIERS: Dict[Tuple[int, int], float] = {
    (0, 1): 1.0,    # Raw → Structured: +100%
    (1, 2): 0.25,   # Structured → Explored: +25%
    (1, 3): 0.50,   # Structured → Behavioral: +50%
    (2, 3): 0.40,   # Explored → Behavioral: +40%
    (3, 4): 2.0,    # Behavioral → Social: +200%
    (4, 5): 5.0,    # Social → Authority: +500%
}

# Decay/loss rates
STREAK_BREAK_LOSS = 0.30              # -30% on streak break
INACTIVITY_DECAY_PER_MONTH = 0.10     # -10% per month inactive
FEATURED_LAPSE_LOSS = 0.50            # -50% on Featured lapse


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UserState:
    """Current state of a user for value calculations."""
    token_generation: int
    current_value: float
    streak_days: int
    days_since_active: int
    stances_explored: int
    is_featured: bool
    is_authority: bool
    country_code: str
    days_as_subscriber: int = 0


@dataclass
class ValueResult:
    """Result of a value calculation."""
    base_value: float
    streak_multiplier: float
    recency_multiplier: float
    exploration_multiplier: float
    final_value: float
    components: Dict[str, float]


@dataclass
class TransitionResult:
    """Result of a generation transition."""
    from_gen: int
    to_gen: int
    value_before: float
    value_after: float
    value_delta: float
    reason: str


# ═══════════════════════════════════════════════════════════════════════════
# CORE VALUE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def calculate_base_value(generation: int) -> float:
    """Get base value for a token generation."""
    return BASE_VALUES.get(generation, 0.0)


def calculate_streak_multiplier(streak_days: int) -> float:
    """
    Calculate streak multiplier.
    Compounds daily, capped at MAX_STREAK_MULTIPLIER.
    """
    if streak_days <= 0:
        return 1.0
    
    multiplier = 1.0 + (streak_days * STREAK_MULTIPLIER_PER_DAY)
    return min(multiplier, MAX_STREAK_MULTIPLIER)


def calculate_recency_multiplier(days_since_active: int) -> float:
    """
    Calculate recency multiplier (decay for inactivity).
    Decays daily, floored at MIN_RECENCY_MULTIPLIER.
    """
    if days_since_active <= 0:
        return 1.0
    
    multiplier = 1.0 - (days_since_active * RECENCY_DECAY_PER_DAY)
    return max(multiplier, MIN_RECENCY_MULTIPLIER)


def calculate_exploration_multiplier(stances_explored: int) -> float:
    """
    Calculate exploration multiplier.
    Rewards users who explore different stances/profiles.
    """
    if stances_explored <= 1:
        return 1.0
    
    # Only count additional stances beyond the first
    additional = stances_explored - 1
    multiplier = 1.0 + (additional * EXPLORATION_MULTIPLIER_PER_STANCE)
    return min(multiplier, MAX_EXPLORATION_MULTIPLIER)


def calculate_token_value(state: UserState) -> ValueResult:
    """
    Calculate current token value for a user.
    
    This is the core value function that combines all factors.
    """
    base = calculate_base_value(state.token_generation)
    streak_mult = calculate_streak_multiplier(state.streak_days)
    recency_mult = calculate_recency_multiplier(state.days_since_active)
    exploration_mult = calculate_exploration_multiplier(state.stances_explored)
    
    # Compound all multipliers
    final_value = base * streak_mult * recency_mult * exploration_mult
    
    # Round to 4 decimal places
    final_value = round(final_value, 4)
    
    return ValueResult(
        base_value=base,
        streak_multiplier=streak_mult,
        recency_multiplier=recency_mult,
        exploration_multiplier=exploration_mult,
        final_value=final_value,
        components={
            "base": base,
            "streak_contribution": base * (streak_mult - 1),
            "recency_impact": base * streak_mult * (recency_mult - 1),
            "exploration_contribution": base * streak_mult * recency_mult * (exploration_mult - 1),
        }
    )


# ═══════════════════════════════════════════════════════════════════════════
# TRANSITION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def calculate_generation_upgrade(
    current_value: float,
    from_gen: int,
    to_gen: int,
) -> TransitionResult:
    """
    Calculate value change when upgrading token generation.
    """
    if to_gen <= from_gen:
        raise ValueError(f"Cannot upgrade from gen {from_gen} to gen {to_gen}")
    
    # Get upgrade multiplier
    key = (from_gen, to_gen)
    if key not in UPGRADE_MULTIPLIERS:
        # For non-standard transitions, interpolate
        multiplier = (BASE_VALUES[to_gen] / BASE_VALUES[from_gen]) - 1
    else:
        multiplier = UPGRADE_MULTIPLIERS[key]
    
    value_delta = current_value * multiplier
    value_after = current_value + value_delta
    
    return TransitionResult(
        from_gen=from_gen,
        to_gen=to_gen,
        value_before=current_value,
        value_after=round(value_after, 4),
        value_delta=round(value_delta, 4),
        reason=f"upgrade_gen_{from_gen}_to_{to_gen}",
    )


def calculate_streak_break(current_value: float) -> TransitionResult:
    """
    Calculate value loss when streak breaks.
    """
    value_delta = -current_value * STREAK_BREAK_LOSS
    value_after = current_value + value_delta
    
    return TransitionResult(
        from_gen=3,  # Behavioral
        to_gen=1,    # Back to structured
        value_before=current_value,
        value_after=round(max(value_after, 0), 4),
        value_delta=round(value_delta, 4),
        reason="streak_broken",
    )


def calculate_inactivity_decay(
    current_value: float,
    months_inactive: int,
) -> TransitionResult:
    """
    Calculate value decay from inactivity.
    """
    decay_rate = INACTIVITY_DECAY_PER_MONTH * months_inactive
    decay_rate = min(decay_rate, 0.9)  # Never lose more than 90%
    
    value_delta = -current_value * decay_rate
    value_after = current_value + value_delta
    
    return TransitionResult(
        from_gen=-1,  # Not a generation change
        to_gen=-1,
        value_before=current_value,
        value_after=round(max(value_after, 0), 4),
        value_delta=round(value_delta, 4),
        reason=f"inactivity_decay_{months_inactive}mo",
    )


def calculate_featured_lapse(current_value: float) -> TransitionResult:
    """
    Calculate value loss when Featured status lapses.
    """
    value_delta = -current_value * FEATURED_LAPSE_LOSS
    value_after = current_value + value_delta
    
    return TransitionResult(
        from_gen=4,  # Social validation
        to_gen=3,    # Back to behavioral
        value_before=current_value,
        value_after=round(max(value_after, 0), 4),
        value_delta=round(value_delta, 4),
        reason="featured_lapsed",
    )


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM HEALTH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def calculate_token_velocity(
    events_count: int,
    unique_users: int,
    days: int,
) -> float:
    """
    Calculate token velocity (events per user per day).
    Higher velocity = more active system.
    """
    if unique_users == 0 or days == 0:
        return 0.0
    
    return events_count / unique_users / days


def calculate_value_efficiency(
    total_value_created: float,
    total_tokens_generated: int,
) -> float:
    """
    Calculate value efficiency (value per token).
    Higher efficiency = users reaching higher generations.
    """
    if total_tokens_generated == 0:
        return 0.0
    
    return total_value_created / total_tokens_generated


def calculate_funnel_health(
    stage_counts: Dict[str, int],
) -> Dict[str, float]:
    """
    Calculate conversion rates between funnel stages.
    Returns dict of stage -> conversion_rate_to_next.
    """
    stages = [
        "visitor", "signed_up", "first_analysis", "hit_limit",
        "trial_started", "subscribed", "featured_eligible",
        "featured_submitted", "featured_approved", "authority"
    ]
    
    health = {}
    for i, stage in enumerate(stages[:-1]):
        current = stage_counts.get(stage, 0)
        next_stage = stages[i + 1]
        next_count = stage_counts.get(next_stage, 0)
        
        if current > 0:
            health[f"{stage}_to_{next_stage}"] = next_count / current
        else:
            health[f"{stage}_to_{next_stage}"] = 0.0
    
    return health


def calculate_churn_risk(state: UserState) -> float:
    """
    Calculate churn risk score (0-1).
    Higher = more likely to churn.
    """
    risk = 0.0
    
    # Inactivity increases risk
    if state.days_since_active > 0:
        risk += min(state.days_since_active * 0.02, 0.4)
    
    # Low value increases risk
    if state.current_value < 2.0:
        risk += 0.2
    
    # Broken streak increases risk
    if state.streak_days == 0 and state.token_generation >= 3:
        risk += 0.15
    
    # Low exploration increases risk
    if state.stances_explored <= 1:
        risk += 0.1
    
    # Being a subscriber decreases risk
    if state.days_as_subscriber > 0:
        risk -= min(state.days_as_subscriber * 0.005, 0.2)
    
    return max(0.0, min(1.0, risk))


def calculate_upgrade_potential(state: UserState) -> Dict[str, float]:
    """
    Calculate potential value gain from next upgrade.
    Returns possible upgrades and their value impact.
    """
    potential = {}
    current_gen = state.token_generation
    current_value = state.current_value
    
    # What upgrades are possible from current generation?
    possible_upgrades = {
        0: [1],           # Raw → Structured
        1: [2, 3],        # Structured → Explored or Behavioral
        2: [3],           # Explored → Behavioral
        3: [4],           # Behavioral → Social
        4: [5],           # Social → Authority
        5: [],            # Max generation
    }
    
    for target_gen in possible_upgrades.get(current_gen, []):
        result = calculate_generation_upgrade(current_value, current_gen, target_gen)
        potential[f"gen_{current_gen}_to_{target_gen}"] = result.value_delta
    
    return potential


# ═══════════════════════════════════════════════════════════════════════════
# AGGREGATE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def calculate_system_value(
    portfolios: List[Dict],
) -> Dict[str, float]:
    """
    Calculate aggregate system value metrics.
    """
    if not portfolios:
        return {
            "total_value": 0.0,
            "mean_value": 0.0,
            "median_value": 0.0,
            "value_at_risk": 0.0,
        }
    
    values = [p.get("total_value", 0.0) for p in portfolios]
    values.sort()
    
    total = sum(values)
    mean = total / len(values)
    median = values[len(values) // 2]
    
    # Value at risk: sum of value for users with high churn risk
    at_risk_values = [
        p.get("total_value", 0.0)
        for p in portfolios
        if p.get("days_since_active", 0) > 14
    ]
    value_at_risk = sum(at_risk_values)
    
    return {
        "total_value": round(total, 4),
        "mean_value": round(mean, 4),
        "median_value": round(median, 4),
        "value_at_risk": round(value_at_risk, 4),
    }


def calculate_generation_distribution(
    portfolios: List[Dict],
) -> Dict[int, Dict[str, float]]:
    """
    Calculate distribution of users and value across generations.
    """
    distribution = {gen: {"count": 0, "value": 0.0} for gen in range(6)}
    
    for p in portfolios:
        gen = p.get("token_generation", 0)
        value = p.get("total_value", 0.0)
        
        if gen in distribution:
            distribution[gen]["count"] += 1
            distribution[gen]["value"] += value
    
    total_users = sum(d["count"] for d in distribution.values())
    total_value = sum(d["value"] for d in distribution.values())
    
    # Add percentages
    for gen, data in distribution.items():
        data["user_pct"] = data["count"] / total_users if total_users > 0 else 0.0
        data["value_pct"] = data["value"] / total_value if total_value > 0 else 0.0
    
    return distribution


def calculate_country_comparison(
    portfolios: List[Dict],
) -> Dict[str, Dict[str, float]]:
    """
    Calculate metrics by country for comparison.
    """
    countries = {"ca": [], "uk": [], "au": [], "nz": []}
    
    for p in portfolios:
        country = p.get("country_code", "ca")
        if country in countries:
            countries[country].append(p)
    
    comparison = {}
    for country, users in countries.items():
        if not users:
            comparison[country] = {
                "user_count": 0,
                "total_value": 0.0,
                "mean_value": 0.0,
                "avg_generation": 0.0,
            }
        else:
            values = [u.get("total_value", 0.0) for u in users]
            gens = [u.get("token_generation", 0) for u in users]
            
            comparison[country] = {
                "user_count": len(users),
                "total_value": round(sum(values), 4),
                "mean_value": round(sum(values) / len(values), 4),
                "avg_generation": round(sum(gens) / len(gens), 2),
            }
    
    return comparison
