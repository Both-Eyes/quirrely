#!/usr/bin/env python3
"""
LNCP ENGINE v3.8
Linguistic Numerical Curation Protocol - Core Analysis Engine

This is IMMUTABLE CORE IP.
The engine that transforms text into voice profiles.

Components:
- tokens: The 50-token vocabulary
- profiles: The 40 voice profiles
- scoring: The analysis algorithm
- value: Token economics

Usage:
    from lncp.engine import analyze, get_profile, calculate_token_value
    
    result = analyze("Your text here...")
    print(result.primary_profile.name)
"""

__version__ = "3.8.0"
__author__ = "Quirrely"
__license__ = "Proprietary"

# Tokens
from .tokens import (
    ENGINE_VERSION,
    TOKENS_VERSION,
    TokenCategory,
    Token,
    ALL_TOKENS,
    TOKEN_BY_ID,
    TOKEN_BY_NAME,
    TOKENS_BY_CATEGORY,
    get_token,
    get_tokens_by_category,
    get_token_ids,
    get_token_names,
)

# Profiles
from .profiles import (
    PROFILES_VERSION,
    StyleAxis,
    CertitudeAxis,
    Profile,
    ALL_PROFILES,
    PROFILE_BY_ID,
    PROFILE_BY_SLUG,
    get_profile,
    get_profiles_by_style,
    get_profiles_by_certitude,
    get_profile_ids,
    get_profile_slugs,
)

# Scoring
from .scoring import (
    SCORING_VERSION,
    TokenScore,
    ProfileMatch,
    AnalysisResult,
    TextFeatures,
    extract_features,
    score_tokens,
    match_profiles,
    analyze,
)

# Value
from .value import (
    VALUE_VERSION,
    TokenGeneration,
    GENERATION_MULTIPLIERS,
    TokenValue,
    calculate_base_value,
    apply_generation_multiplier,
    apply_decay,
    calculate_token_value,
    calculate_system_value,
)

__all__ = [
    # Version
    "__version__",
    "ENGINE_VERSION",
    
    # Tokens
    "TokenCategory",
    "Token", 
    "ALL_TOKENS",
    "TOKEN_BY_ID",
    "get_token",
    "get_tokens_by_category",
    
    # Profiles
    "StyleAxis",
    "CertitudeAxis",
    "Profile",
    "ALL_PROFILES",
    "PROFILE_BY_ID",
    "get_profile",
    "get_profiles_by_style",
    
    # Scoring
    "TokenScore",
    "ProfileMatch",
    "AnalysisResult",
    "analyze",
    "extract_features",
    
    # Value
    "TokenGeneration",
    "TokenValue",
    "calculate_token_value",
    "calculate_system_value",
]
