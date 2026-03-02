#!/usr/bin/env python3
"""
LNCP ENGINE: SCORING v3.8
The analysis algorithm that scores text against tokens and profiles.

This is IMMUTABLE CORE IP.
Changes require version bump and full regression testing.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
import math

from .tokens import (
    Token, TokenCategory, ALL_TOKENS, TOKEN_BY_ID,
    STRUCTURE_TOKENS, TONE_TOKENS, COMPLEXITY_TOKENS,
    PERSPECTIVE_TOKENS, RHYTHM_TOKENS
)
from .profiles import Profile, ALL_PROFILES, StyleAxis, CertitudeAxis


# ═══════════════════════════════════════════════════════════════════════════
# VERSION
# ═══════════════════════════════════════════════════════════════════════════

SCORING_VERSION = "3.8.0"


# ═══════════════════════════════════════════════════════════════════════════
# SCORING RESULT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TokenScore:
    """Score for a single token."""
    token_id: str
    token_name: str
    category: str
    score: float  # 0.0 to 1.0
    evidence: List[str]  # Text snippets that contributed


@dataclass
class ProfileMatch:
    """Match result for a profile."""
    profile_id: str
    profile_name: str
    style: str
    certitude: str
    score: float  # 0.0 to 100.0
    confidence: float  # 0.0 to 1.0
    rank: int


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    text_length: int
    word_count: int
    sentence_count: int
    
    # Token scores by category
    token_scores: Dict[str, TokenScore]
    category_scores: Dict[str, float]
    
    # Profile matches
    primary_profile: ProfileMatch
    secondary_profiles: List[ProfileMatch]
    all_profile_scores: Dict[str, float]
    
    # Metadata
    analysis_version: str
    
    def to_dict(self) -> Dict:
        return {
            "text_length": self.text_length,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "token_scores": {k: {"score": v.score, "category": v.category} for k, v in self.token_scores.items()},
            "category_scores": self.category_scores,
            "primary_profile": {
                "id": self.primary_profile.profile_id,
                "name": self.primary_profile.profile_name,
                "style": self.primary_profile.style,
                "certitude": self.primary_profile.certitude,
                "score": self.primary_profile.score,
                "confidence": self.primary_profile.confidence,
            },
            "secondary_profiles": [
                {"id": p.profile_id, "name": p.profile_name, "score": p.score}
                for p in self.secondary_profiles[:3]
            ],
            "analysis_version": self.analysis_version,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TEXT FEATURES EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TextFeatures:
    """Extracted features from text."""
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    
    avg_word_length: float
    avg_sentence_length: float
    sentence_length_variance: float
    
    question_ratio: float
    exclamation_ratio: float
    
    first_person_ratio: float
    second_person_ratio: float
    third_person_ratio: float
    
    hedge_word_ratio: float
    assertive_word_ratio: float
    
    complex_word_ratio: float  # Words > 3 syllables
    unique_word_ratio: float   # Type-token ratio
    
    comma_density: float
    semicolon_density: float


def extract_features(text: str) -> TextFeatures:
    """Extract linguistic features from text."""
    
    # Basic counts
    chars = len(text)
    words = text.split()
    word_count = len(words)
    
    # Sentences (simple split)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(1, len(sentences))
    
    # Paragraphs
    paragraphs = text.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    # Averages
    avg_word_length = sum(len(w) for w in words) / max(1, word_count)
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / max(1, len(sentence_lengths))
    
    # Variance
    if len(sentence_lengths) > 1:
        mean = avg_sentence_length
        variance = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    else:
        variance = 0
    
    # Punctuation ratios
    question_count = text.count('?')
    exclamation_count = text.count('!')
    question_ratio = question_count / max(1, sentence_count)
    exclamation_ratio = exclamation_count / max(1, sentence_count)
    
    # Pronouns
    text_lower = text.lower()
    first_person = len(re.findall(r'\b(i|me|my|mine|we|us|our|ours)\b', text_lower))
    second_person = len(re.findall(r'\b(you|your|yours)\b', text_lower))
    third_person = len(re.findall(r'\b(he|she|it|they|him|her|them|his|hers|its|their|theirs)\b', text_lower))
    
    total_pronouns = first_person + second_person + third_person
    first_person_ratio = first_person / max(1, total_pronouns)
    second_person_ratio = second_person / max(1, total_pronouns)
    third_person_ratio = third_person / max(1, total_pronouns)
    
    # Hedge words
    hedge_words = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'seem', 'appear', 
                   'somewhat', 'rather', 'fairly', 'quite', 'probably', 'likely']
    hedge_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in hedge_words)
    hedge_word_ratio = hedge_count / max(1, word_count)
    
    # Assertive words
    assertive_words = ['must', 'will', 'shall', 'definitely', 'certainly', 'clearly',
                       'obviously', 'always', 'never', 'absolutely', 'undoubtedly']
    assertive_count = sum(len(re.findall(r'\b' + w + r'\b', text_lower)) for w in assertive_words)
    assertive_word_ratio = assertive_count / max(1, word_count)
    
    # Complex words (simplified: > 8 chars)
    complex_count = sum(1 for w in words if len(w) > 8)
    complex_word_ratio = complex_count / max(1, word_count)
    
    # Unique words
    unique_words = len(set(w.lower() for w in words))
    unique_word_ratio = unique_words / max(1, word_count)
    
    # Punctuation density
    comma_density = text.count(',') / max(1, word_count)
    semicolon_density = text.count(';') / max(1, word_count)
    
    return TextFeatures(
        char_count=chars,
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        avg_word_length=avg_word_length,
        avg_sentence_length=avg_sentence_length,
        sentence_length_variance=variance,
        question_ratio=question_ratio,
        exclamation_ratio=exclamation_ratio,
        first_person_ratio=first_person_ratio,
        second_person_ratio=second_person_ratio,
        third_person_ratio=third_person_ratio,
        hedge_word_ratio=hedge_word_ratio,
        assertive_word_ratio=assertive_word_ratio,
        complex_word_ratio=complex_word_ratio,
        unique_word_ratio=unique_word_ratio,
        comma_density=comma_density,
        semicolon_density=semicolon_density,
    )


# ═══════════════════════════════════════════════════════════════════════════
# TOKEN SCORING
# ═══════════════════════════════════════════════════════════════════════════

def score_tokens(features: TextFeatures) -> Dict[str, TokenScore]:
    """Score all tokens based on text features."""
    scores = {}
    
    # Structure tokens
    scores["S01"] = TokenScore("S01", "Linear", "structure", 
        _sigmoid(features.avg_sentence_length, 15, 5) * (1 - features.sentence_length_variance / 100), [])
    scores["S06"] = TokenScore("S06", "Hierarchical", "structure",
        _sigmoid(features.paragraph_count, 3, 2) * _sigmoid(features.semicolon_density, 0.02, 0.01), [])
    scores["S08"] = TokenScore("S08", "Dialogic", "structure",
        _sigmoid(features.question_ratio, 0.3, 0.1) * _sigmoid(features.second_person_ratio, 0.3, 0.2), [])
    
    # Tone tokens
    scores["T01"] = TokenScore("T01", "Assertive", "tone",
        features.assertive_word_ratio * 10 + _sigmoid(features.exclamation_ratio, 0.1, 0.05), [])
    scores["T02"] = TokenScore("T02", "Hedged", "tone",
        features.hedge_word_ratio * 10, [])
    scores["T03"] = TokenScore("T03", "Intimate", "tone",
        features.first_person_ratio * 0.5 + _sigmoid(features.avg_sentence_length, 12, 5), [])
    
    # Complexity tokens
    scores["C01"] = TokenScore("C01", "Dense", "complexity",
        features.complex_word_ratio * 3 + (1 - features.unique_word_ratio) * 0.5, [])
    scores["C02"] = TokenScore("C02", "Sparse", "complexity",
        _sigmoid(20 - features.avg_sentence_length, 10, 5) * (1 - features.complex_word_ratio), [])
    scores["C06"] = TokenScore("C06", "Accessible", "complexity",
        (1 - features.complex_word_ratio) * _sigmoid(12 - features.avg_word_length / 2, 5, 2), [])
    
    # Perspective tokens
    scores["P01"] = TokenScore("P01", "First-person", "perspective",
        features.first_person_ratio, [])
    scores["P02"] = TokenScore("P02", "Second-person", "perspective",
        features.second_person_ratio, [])
    scores["P03"] = TokenScore("P03", "Third-person", "perspective",
        features.third_person_ratio, [])
    
    # Rhythm tokens
    scores["R01"] = TokenScore("R01", "Staccato", "rhythm",
        _sigmoid(10 - features.avg_sentence_length, 5, 3), [])
    scores["R02"] = TokenScore("R02", "Flowing", "rhythm",
        _sigmoid(features.avg_sentence_length, 20, 8) * _sigmoid(features.comma_density, 0.05, 0.02), [])
    scores["R03"] = TokenScore("R03", "Varied", "rhythm",
        _sigmoid(features.sentence_length_variance, 50, 20), [])
    
    # Normalize all scores to 0-1
    for key in scores:
        scores[key] = TokenScore(
            scores[key].token_id,
            scores[key].token_name,
            scores[key].category,
            min(1.0, max(0.0, scores[key].score)),
            scores[key].evidence
        )
    
    return scores


def _sigmoid(x: float, midpoint: float, scale: float) -> float:
    """Sigmoid function for smooth scoring."""
    try:
        return 1 / (1 + math.exp(-(x - midpoint) / scale))
    except OverflowError:
        return 0.0 if x < midpoint else 1.0


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE MATCHING
# ═══════════════════════════════════════════════════════════════════════════

def match_profiles(token_scores: Dict[str, TokenScore]) -> List[ProfileMatch]:
    """Match token scores to profiles."""
    matches = []
    
    for profile in ALL_PROFILES:
        # Calculate profile score based on token affinities
        primary_score = sum(
            token_scores.get(tid, TokenScore(tid, "", "", 0.0, [])).score
            for tid in profile.primary_tokens
        ) / len(profile.primary_tokens) if profile.primary_tokens else 0
        
        secondary_score = sum(
            token_scores.get(tid, TokenScore(tid, "", "", 0.0, [])).score
            for tid in profile.secondary_tokens
        ) / len(profile.secondary_tokens) if profile.secondary_tokens else 0
        
        # Weighted combination
        profile_score = (primary_score * 0.7 + secondary_score * 0.3) * 100
        
        # Confidence based on score separation
        confidence = min(1.0, profile_score / 50)
        
        matches.append(ProfileMatch(
            profile_id=profile.id,
            profile_name=profile.name,
            style=profile.style.value,
            certitude=profile.certitude.value,
            score=profile_score,
            confidence=confidence,
            rank=0,
        ))
    
    # Sort by score and assign ranks
    matches.sort(key=lambda m: m.score, reverse=True)
    for i, match in enumerate(matches):
        matches[i] = ProfileMatch(
            profile_id=match.profile_id,
            profile_name=match.profile_name,
            style=match.style,
            certitude=match.certitude,
            score=match.score,
            confidence=match.confidence,
            rank=i + 1,
        )
    
    return matches


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════════════════

def analyze(text: str) -> AnalysisResult:
    """
    Analyze text and return complete LNCP result.
    
    This is the primary entry point for LNCP Engine.
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Extract features
    features = extract_features(text)
    
    # Score tokens
    token_scores = score_tokens(features)
    
    # Calculate category scores
    category_scores = {}
    for category in ["structure", "tone", "complexity", "perspective", "rhythm"]:
        cat_tokens = [s for s in token_scores.values() if s.category == category]
        if cat_tokens:
            category_scores[category] = sum(t.score for t in cat_tokens) / len(cat_tokens)
        else:
            category_scores[category] = 0.0
    
    # Match profiles
    profile_matches = match_profiles(token_scores)
    
    return AnalysisResult(
        text_length=features.char_count,
        word_count=features.word_count,
        sentence_count=features.sentence_count,
        token_scores=token_scores,
        category_scores=category_scores,
        primary_profile=profile_matches[0],
        secondary_profiles=profile_matches[1:4],
        all_profile_scores={m.profile_id: m.score for m in profile_matches},
        analysis_version=SCORING_VERSION,
    )


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "SCORING_VERSION",
    "TokenScore",
    "ProfileMatch",
    "AnalysisResult",
    "TextFeatures",
    "extract_features",
    "score_tokens",
    "match_profiles",
    "analyze",
]
