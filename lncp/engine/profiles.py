#!/usr/bin/env python3
"""
LNCP ENGINE: PROFILES v3.8
The 40 voice profiles derived from token combinations.

This is IMMUTABLE CORE IP.
Changes require version bump and full regression testing.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .tokens import TokenCategory


# ═══════════════════════════════════════════════════════════════════════════
# VERSION
# ═══════════════════════════════════════════════════════════════════════════

PROFILES_VERSION = "3.8.0"


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE AXES
# ═══════════════════════════════════════════════════════════════════════════

class StyleAxis(str, Enum):
    """Primary style dimension (10 values)."""
    ASSERTIVE = "assertive"
    HEDGED = "hedged"
    CONVERSATIONAL = "conversational"
    FORMAL = "formal"
    DENSE = "dense"
    MINIMAL = "minimal"
    POETIC = "poetic"
    ANALYTICAL = "analytical"
    INTERROGATIVE = "interrogative"
    LONGFORM = "longform"


class CertitudeAxis(str, Enum):
    """Secondary certitude dimension (4 values)."""
    OPEN = "open"           # Explores possibilities
    CLOSED = "closed"       # Definitive conclusions
    BALANCED = "balanced"   # Mix of both
    CONTRADICTORY = "contradictory"  # Intentional tension


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE DEFINITION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Profile:
    """A voice profile (one of 40)."""
    id: str
    name: str
    style: StyleAxis
    certitude: CertitudeAxis
    description: str
    
    # Token affinities (which tokens this profile tends toward)
    primary_tokens: Tuple[str, ...]
    secondary_tokens: Tuple[str, ...]
    
    # Scoring thresholds
    min_score: float = 0.0
    max_score: float = 100.0
    
    @property
    def slug(self) -> str:
        return f"{self.style.value}-{self.certitude.value}"
    
    @property
    def display_name(self) -> str:
        return f"{self.style.value.title()} {self.certitude.value.title()}"


# ═══════════════════════════════════════════════════════════════════════════
# THE 40 PROFILES (10 styles × 4 certitudes)
# ═══════════════════════════════════════════════════════════════════════════

def _generate_profiles() -> List[Profile]:
    """Generate all 40 profiles."""
    
    # Style definitions with primary/secondary token affinities
    STYLE_TOKENS = {
        StyleAxis.ASSERTIVE: (("T01", "S06", "R01"), ("P01", "C04")),
        StyleAxis.HEDGED: (("T02", "S07", "R03"), ("P05", "C03")),
        StyleAxis.CONVERSATIONAL: (("T03", "S08", "R03"), ("P02", "C06")),
        StyleAxis.FORMAL: (("T04", "S06", "R08"), ("P03", "C05")),
        StyleAxis.DENSE: (("C01", "S04", "R02"), ("T01", "P04")),
        StyleAxis.MINIMAL: (("C02", "S01", "R01"), ("T06", "P05")),
        StyleAxis.POETIC: (("C03", "S10", "R03"), ("T03", "P01")),
        StyleAxis.ANALYTICAL: (("C01", "S06", "R08"), ("T04", "P03")),
        StyleAxis.INTERROGATIVE: (("S08", "T09", "R07"), ("P02", "C03")),
        StyleAxis.LONGFORM: (("S01", "R02", "C01"), ("T06", "P04")),
    }
    
    # Certitude descriptions
    CERTITUDE_DESC = {
        CertitudeAxis.OPEN: "explores possibilities without forcing conclusions",
        CertitudeAxis.CLOSED: "arrives at definitive conclusions",
        CertitudeAxis.BALANCED: "weighs options before deciding",
        CertitudeAxis.CONTRADICTORY: "embraces productive tension",
    }
    
    profiles = []
    profile_id = 1
    
    for style in StyleAxis:
        primary, secondary = STYLE_TOKENS[style]
        
        for certitude in CertitudeAxis:
            profile = Profile(
                id=f"P{profile_id:02d}",
                name=f"{style.value.title()} {certitude.value.title()}",
                style=style,
                certitude=certitude,
                description=f"A {style.value} voice that {CERTITUDE_DESC[certitude]}",
                primary_tokens=primary,
                secondary_tokens=secondary,
            )
            profiles.append(profile)
            profile_id += 1
    
    return profiles


ALL_PROFILES: List[Profile] = _generate_profiles()
PROFILE_BY_ID: Dict[str, Profile] = {p.id: p for p in ALL_PROFILES}
PROFILE_BY_SLUG: Dict[str, Profile] = {p.slug: p for p in ALL_PROFILES}


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_profile(identifier: str) -> Profile:
    """Get a profile by ID or slug."""
    if identifier in PROFILE_BY_ID:
        return PROFILE_BY_ID[identifier]
    if identifier in PROFILE_BY_SLUG:
        return PROFILE_BY_SLUG[identifier]
    raise ValueError(f"Unknown profile: {identifier}")


def get_profiles_by_style(style: StyleAxis) -> List[Profile]:
    """Get all profiles with a given style."""
    return [p for p in ALL_PROFILES if p.style == style]


def get_profiles_by_certitude(certitude: CertitudeAxis) -> List[Profile]:
    """Get all profiles with a given certitude."""
    return [p for p in ALL_PROFILES if p.certitude == certitude]


def get_profile_ids() -> List[str]:
    """Get all profile IDs."""
    return [p.id for p in ALL_PROFILES]


def get_profile_slugs() -> List[str]:
    """Get all profile slugs."""
    return [p.slug for p in ALL_PROFILES]


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "PROFILES_VERSION",
    "StyleAxis",
    "CertitudeAxis", 
    "Profile",
    "ALL_PROFILES",
    "PROFILE_BY_ID",
    "PROFILE_BY_SLUG",
    "get_profile",
    "get_profiles_by_style",
    "get_profiles_by_certitude",
    "get_profile_ids",
    "get_profile_slugs",
]
