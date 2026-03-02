#!/usr/bin/env python3
"""
LNCP ENGINE: TOKENS v3.8
The 50-token vocabulary that defines writing voice.

This is IMMUTABLE CORE IP.
Changes require version bump and full regression testing.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# VERSION
# ═══════════════════════════════════════════════════════════════════════════

ENGINE_VERSION = "3.8.0"
TOKENS_VERSION = "3.8.0"


# ═══════════════════════════════════════════════════════════════════════════
# TOKEN CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════

class TokenCategory(str, Enum):
    """The five primary dimensions of writing voice."""
    STRUCTURE = "structure"     # How ideas are organized
    TONE = "tone"               # Emotional quality
    COMPLEXITY = "complexity"   # Cognitive density
    PERSPECTIVE = "perspective" # Point of view
    RHYTHM = "rhythm"           # Flow and pacing


# ═══════════════════════════════════════════════════════════════════════════
# THE 50 TOKENS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Token:
    """A single LNCP token."""
    id: str
    name: str
    category: TokenCategory
    description: str
    weight: float = 1.0  # Relative importance in scoring


# Structure Tokens (10)
STRUCTURE_TOKENS: List[Token] = [
    Token("S01", "Linear", TokenCategory.STRUCTURE, "Sequential, step-by-step progression"),
    Token("S02", "Circular", TokenCategory.STRUCTURE, "Returns to beginning, cyclical"),
    Token("S03", "Fragmented", TokenCategory.STRUCTURE, "Broken, non-continuous"),
    Token("S04", "Nested", TokenCategory.STRUCTURE, "Ideas within ideas"),
    Token("S05", "Parallel", TokenCategory.STRUCTURE, "Multiple simultaneous threads"),
    Token("S06", "Hierarchical", TokenCategory.STRUCTURE, "Clear levels of importance"),
    Token("S07", "Associative", TokenCategory.STRUCTURE, "Connection-based, tangential"),
    Token("S08", "Dialogic", TokenCategory.STRUCTURE, "Call and response pattern"),
    Token("S09", "Episodic", TokenCategory.STRUCTURE, "Distinct segments or scenes"),
    Token("S10", "Spiral", TokenCategory.STRUCTURE, "Returning with deeper insight"),
]

# Tone Tokens (10)
TONE_TOKENS: List[Token] = [
    Token("T01", "Assertive", TokenCategory.TONE, "Confident, declarative"),
    Token("T02", "Hedged", TokenCategory.TONE, "Qualified, uncertain"),
    Token("T03", "Intimate", TokenCategory.TONE, "Personal, close"),
    Token("T04", "Distant", TokenCategory.TONE, "Removed, observational"),
    Token("T05", "Urgent", TokenCategory.TONE, "Pressing, immediate"),
    Token("T06", "Contemplative", TokenCategory.TONE, "Reflective, measured"),
    Token("T07", "Playful", TokenCategory.TONE, "Light, humorous"),
    Token("T08", "Somber", TokenCategory.TONE, "Heavy, serious"),
    Token("T09", "Provocative", TokenCategory.TONE, "Challenging, confrontational"),
    Token("T10", "Nurturing", TokenCategory.TONE, "Supportive, encouraging"),
]

# Complexity Tokens (10)
COMPLEXITY_TOKENS: List[Token] = [
    Token("C01", "Dense", TokenCategory.COMPLEXITY, "Information-rich, compact"),
    Token("C02", "Sparse", TokenCategory.COMPLEXITY, "Minimal, essential only"),
    Token("C03", "Layered", TokenCategory.COMPLEXITY, "Multiple meanings"),
    Token("C04", "Transparent", TokenCategory.COMPLEXITY, "Single, clear meaning"),
    Token("C05", "Technical", TokenCategory.COMPLEXITY, "Specialized vocabulary"),
    Token("C06", "Accessible", TokenCategory.COMPLEXITY, "Common vocabulary"),
    Token("C07", "Abstract", TokenCategory.COMPLEXITY, "Conceptual, theoretical"),
    Token("C08", "Concrete", TokenCategory.COMPLEXITY, "Specific, tangible"),
    Token("C09", "Allusive", TokenCategory.COMPLEXITY, "References external works"),
    Token("C10", "Self-contained", TokenCategory.COMPLEXITY, "No external references needed"),
]

# Perspective Tokens (10)
PERSPECTIVE_TOKENS: List[Token] = [
    Token("P01", "First-person", TokenCategory.PERSPECTIVE, "I/we centered"),
    Token("P02", "Second-person", TokenCategory.PERSPECTIVE, "You centered"),
    Token("P03", "Third-person", TokenCategory.PERSPECTIVE, "They/it centered"),
    Token("P04", "Omniscient", TokenCategory.PERSPECTIVE, "All-knowing narrator"),
    Token("P05", "Limited", TokenCategory.PERSPECTIVE, "Restricted viewpoint"),
    Token("P06", "Shifting", TokenCategory.PERSPECTIVE, "Changes perspective"),
    Token("P07", "Collective", TokenCategory.PERSPECTIVE, "Group voice"),
    Token("P08", "Singular", TokenCategory.PERSPECTIVE, "Individual voice"),
    Token("P09", "Embedded", TokenCategory.PERSPECTIVE, "Story within story"),
    Token("P10", "Direct", TokenCategory.PERSPECTIVE, "Unmediated narration"),
]

# Rhythm Tokens (10)
RHYTHM_TOKENS: List[Token] = [
    Token("R01", "Staccato", TokenCategory.RHYTHM, "Short, punchy"),
    Token("R02", "Flowing", TokenCategory.RHYTHM, "Long, connected"),
    Token("R03", "Varied", TokenCategory.RHYTHM, "Mixed sentence lengths"),
    Token("R04", "Repetitive", TokenCategory.RHYTHM, "Recurring patterns"),
    Token("R05", "Building", TokenCategory.RHYTHM, "Escalating intensity"),
    Token("R06", "Diminishing", TokenCategory.RHYTHM, "Decreasing intensity"),
    Token("R07", "Syncopated", TokenCategory.RHYTHM, "Unexpected breaks"),
    Token("R08", "Steady", TokenCategory.RHYTHM, "Consistent pace"),
    Token("R09", "Accelerating", TokenCategory.RHYTHM, "Speeding up"),
    Token("R10", "Decelerating", TokenCategory.RHYTHM, "Slowing down"),
]


# ═══════════════════════════════════════════════════════════════════════════
# ALL TOKENS
# ═══════════════════════════════════════════════════════════════════════════

ALL_TOKENS: List[Token] = (
    STRUCTURE_TOKENS + 
    TONE_TOKENS + 
    COMPLEXITY_TOKENS + 
    PERSPECTIVE_TOKENS + 
    RHYTHM_TOKENS
)

TOKEN_BY_ID: Dict[str, Token] = {t.id: t for t in ALL_TOKENS}
TOKEN_BY_NAME: Dict[str, Token] = {t.name.lower(): t for t in ALL_TOKENS}

TOKENS_BY_CATEGORY: Dict[TokenCategory, List[Token]] = {
    TokenCategory.STRUCTURE: STRUCTURE_TOKENS,
    TokenCategory.TONE: TONE_TOKENS,
    TokenCategory.COMPLEXITY: COMPLEXITY_TOKENS,
    TokenCategory.PERSPECTIVE: PERSPECTIVE_TOKENS,
    TokenCategory.RHYTHM: RHYTHM_TOKENS,
}


# ═══════════════════════════════════════════════════════════════════════════
# TOKEN OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_token(identifier: str) -> Token:
    """Get a token by ID or name."""
    if identifier in TOKEN_BY_ID:
        return TOKEN_BY_ID[identifier]
    if identifier.lower() in TOKEN_BY_NAME:
        return TOKEN_BY_NAME[identifier.lower()]
    raise ValueError(f"Unknown token: {identifier}")


def get_tokens_by_category(category: TokenCategory) -> List[Token]:
    """Get all tokens in a category."""
    return TOKENS_BY_CATEGORY[category]


def get_token_ids() -> List[str]:
    """Get all token IDs."""
    return [t.id for t in ALL_TOKENS]


def get_token_names() -> List[str]:
    """Get all token names."""
    return [t.name for t in ALL_TOKENS]


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "ENGINE_VERSION",
    "TOKENS_VERSION",
    "TokenCategory",
    "Token",
    "ALL_TOKENS",
    "TOKEN_BY_ID",
    "TOKEN_BY_NAME",
    "TOKENS_BY_CATEGORY",
    "STRUCTURE_TOKENS",
    "TONE_TOKENS", 
    "COMPLEXITY_TOKENS",
    "PERSPECTIVE_TOKENS",
    "RHYTHM_TOKENS",
    "get_token",
    "get_tokens_by_category",
    "get_token_ids",
    "get_token_names",
]
