#!/usr/bin/env python3
"""
LNCP ENGINE: VALUE v3.8
Token value calculation functions - the economics layer.

This is IMMUTABLE CORE IP.
Changes require version bump and full regression testing.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import math


# ═══════════════════════════════════════════════════════════════════════════
# VERSION
# ═══════════════════════════════════════════════════════════════════════════

VALUE_VERSION = "3.8.0"


# ═══════════════════════════════════════════════════════════════════════════
# TOKEN GENERATIONS
# ═══════════════════════════════════════════════════════════════════════════

class TokenGeneration(int, Enum):
    """Token generation levels with value multipliers."""
    GEN_0_RAW = 0           # Visitor, no profile
    GEN_1_PROFILE = 1       # Has profile
    GEN_2_EXPLORED = 2      # Explored multiple analyses
    GEN_3_BEHAVIORAL = 3    # Consistent behavior patterns
    GEN_4_FEATURED = 4      # Featured writer
    GEN_5_AUTHORITY = 5     # Authority status


# Value multipliers by generation
GENERATION_MULTIPLIERS: Dict[TokenGeneration, float] = {
    TokenGeneration.GEN_0_RAW: 0.95,
    TokenGeneration.GEN_1_PROFILE: 1.00,
    TokenGeneration.GEN_2_EXPLORED: 1.10,
    TokenGeneration.GEN_3_BEHAVIORAL: 1.35,
    TokenGeneration.GEN_4_FEATURED: 1.80,
    TokenGeneration.GEN_5_AUTHORITY: 2.50,
}


# ═══════════════════════════════════════════════════════════════════════════
# VALUE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# Base values
BASE_TOKEN_VALUE = 1.0
ANALYSIS_VALUE = 0.5
PROFILE_DISCOVERY_VALUE = 2.0
STREAK_DAY_VALUE = 0.25
MILESTONE_VALUE = 1.0

# Caps
MAX_DAILY_VALUE = 10.0
MAX_TOKEN_VALUE = 25.0

# Decay
INACTIVITY_DECAY_RATE = 0.02  # 2% per day of inactivity
MAX_DECAY = 0.50  # Never decay below 50% of value


# ═══════════════════════════════════════════════════════════════════════════
# VALUE CALCULATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TokenValue:
    """Calculated value for a user token."""
    user_id: str
    base_value: float
    generation: TokenGeneration
    multiplier: float
    final_value: float
    components: Dict[str, float]
    calculated_at: datetime


def calculate_base_value(
    analyses_count: int,
    unique_profiles_seen: int,
    streak_days: int,
    milestones_achieved: int,
) -> float:
    """Calculate base token value from user activity."""
    
    # Analysis value (diminishing returns)
    analysis_value = ANALYSIS_VALUE * math.log1p(analyses_count)
    
    # Profile exploration value
    profile_value = PROFILE_DISCOVERY_VALUE * min(unique_profiles_seen, 10) / 10
    
    # Streak value
    streak_value = STREAK_DAY_VALUE * min(streak_days, 30)
    
    # Milestone value
    milestone_value = MILESTONE_VALUE * milestones_achieved
    
    # Sum with base
    total = BASE_TOKEN_VALUE + analysis_value + profile_value + streak_value + milestone_value
    
    return min(MAX_TOKEN_VALUE, total)


def apply_generation_multiplier(base_value: float, generation: TokenGeneration) -> float:
    """Apply generation multiplier to base value."""
    multiplier = GENERATION_MULTIPLIERS.get(generation, 1.0)
    return base_value * multiplier


def apply_decay(value: float, days_inactive: int) -> float:
    """Apply inactivity decay to token value."""
    if days_inactive <= 0:
        return value
    
    decay_factor = 1.0 - (INACTIVITY_DECAY_RATE * days_inactive)
    decay_factor = max(1.0 - MAX_DECAY, decay_factor)
    
    return value * decay_factor


def calculate_token_value(
    user_id: str,
    analyses_count: int,
    unique_profiles_seen: int,
    streak_days: int,
    milestones_achieved: int,
    generation: TokenGeneration,
    days_inactive: int = 0,
) -> TokenValue:
    """
    Calculate complete token value for a user.
    
    This is the primary value function for the token economy.
    """
    # Calculate components
    base = calculate_base_value(
        analyses_count,
        unique_profiles_seen,
        streak_days,
        milestones_achieved,
    )
    
    # Apply generation multiplier
    multiplier = GENERATION_MULTIPLIERS.get(generation, 1.0)
    with_multiplier = base * multiplier
    
    # Apply decay
    final = apply_decay(with_multiplier, days_inactive)
    
    return TokenValue(
        user_id=user_id,
        base_value=base,
        generation=generation,
        multiplier=multiplier,
        final_value=round(final, 3),
        components={
            "base": BASE_TOKEN_VALUE,
            "analyses": ANALYSIS_VALUE * math.log1p(analyses_count),
            "profiles": PROFILE_DISCOVERY_VALUE * min(unique_profiles_seen, 10) / 10,
            "streak": STREAK_DAY_VALUE * min(streak_days, 30),
            "milestones": MILESTONE_VALUE * milestones_achieved,
            "decay": -1 * (with_multiplier - final) if days_inactive > 0 else 0,
        },
        calculated_at=datetime.utcnow(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# AGGREGATE VALUE
# ═══════════════════════════════════════════════════════════════════════════

def calculate_system_value(token_values: List[TokenValue]) -> Dict:
    """Calculate aggregate system value from all tokens."""
    if not token_values:
        return {
            "total_value": 0,
            "mean_value": 0,
            "median_value": 0,
            "max_value": 0,
            "by_generation": {},
        }
    
    values = [tv.final_value for tv in token_values]
    sorted_values = sorted(values)
    
    by_gen = {}
    for gen in TokenGeneration:
        gen_tokens = [tv for tv in token_values if tv.generation == gen]
        if gen_tokens:
            by_gen[gen.name] = {
                "count": len(gen_tokens),
                "total": sum(tv.final_value for tv in gen_tokens),
                "mean": sum(tv.final_value for tv in gen_tokens) / len(gen_tokens),
            }
    
    return {
        "total_value": sum(values),
        "mean_value": sum(values) / len(values),
        "median_value": sorted_values[len(sorted_values) // 2],
        "max_value": max(values),
        "by_generation": by_gen,
    }


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "VALUE_VERSION",
    "TokenGeneration",
    "GENERATION_MULTIPLIERS",
    "BASE_TOKEN_VALUE",
    "ANALYSIS_VALUE",
    "PROFILE_DISCOVERY_VALUE",
    "STREAK_DAY_VALUE",
    "MILESTONE_VALUE",
    "MAX_DAILY_VALUE",
    "MAX_TOKEN_VALUE",
    "INACTIVITY_DECAY_RATE",
    "MAX_DECAY",
    "TokenValue",
    "calculate_base_value",
    "apply_generation_multiplier",
    "apply_decay",
    "calculate_token_value",
    "calculate_system_value",
]
