#!/usr/bin/env python3
"""
LNCP User Profile Aggregator v1.0

Builds evolving narrator profiles from a user's writing history across sessions.
Tracks patterns, growth, and consistency over time.

This module:
1. Aggregates metrics across all user sessions
2. Detects dominant modes and secondary tendencies
3. Tracks evolution and growth over time
4. Generates personalized profile sketches
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from session_persistence import get_session_store, SessionStore
from narrator_profiles_v1 import (
    MODE_PROFILES, CLUSTER_PROFILES,
    get_marker_cluster, get_complexity_cluster, get_register_cluster,
    generate_narrator_profile
)


# =============================================================================
# USER PROFILE STORAGE
# =============================================================================

USER_PROFILES_DIR = Path(__file__).parent / "user_profiles"


def ensure_profiles_dir():
    """Create profiles directory if needed."""
    USER_PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def get_user_profile_path(user_id: str = "default") -> Path:
    """Get path to user's profile file."""
    ensure_profiles_dir()
    return USER_PROFILES_DIR / f"{user_id}_profile.json"


def save_user_profile(profile: Dict[str, Any], user_id: str = "default"):
    """Save user profile to disk."""
    path = get_user_profile_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, default=str)


def load_user_profile(user_id: str = "default") -> Optional[Dict[str, Any]]:
    """Load user profile from disk."""
    path = get_user_profile_path(user_id)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# =============================================================================
# MODE DETECTION FROM METRICS
# =============================================================================

def detect_mode_from_metrics(hi_profile: Dict[str, Any]) -> Tuple[str, float]:
    """
    Detect the dominant writing mode from a high-intent profile.
    
    Returns (mode, confidence) where confidence is 0.0-1.0
    """
    # Get detection flags
    is_assertive = hi_profile.get("is_assertive_mode", False)
    is_interrogative = hi_profile.get("is_interrogative_mode", False)
    is_poetic = hi_profile.get("is_poetic_mode", False)
    is_dense = hi_profile.get("is_structurally_dense", False)
    is_minimal = hi_profile.get("is_minimal", False)
    is_contradictory = hi_profile.get("is_contradictory", False)
    register = hi_profile.get("register", "FORMAL")
    complexity = hi_profile.get("syntax_complexity", "SIMPLE")
    has_anaphora = hi_profile.get("has_anaphora", False)
    
    # Get metrics
    avg_clauses = hi_profile.get("avg_clauses", 1.0)
    avg_words = hi_profile.get("avg_words", 10.0)
    hi_count = hi_profile.get("total_high_intent_events", 0)
    scope_events = hi_profile.get("structural_summary", {}).get("scope_events", 0)
    question_ratio = hi_profile.get("question_ratio", 0.0)
    informality = hi_profile.get("informality_score", 0.0)
    
    # Score each mode
    scores = {
        "MINIMAL": 0.0,
        "DENSE": 0.0,
        "POETIC": 0.0,
        "INTERROGATIVE": 0.0,
        "ASSERTIVE": 0.0,
        "HEDGED": 0.0,
        "PARENTHETICAL": 0.0,
        "PARALLEL": 0.0,
        "LONGFORM": 0.0,
        "CONVERSATIONAL": 0.0,
    }
    
    # Direct flags (high confidence)
    if is_interrogative:
        scores["INTERROGATIVE"] += 3.0
    if is_assertive:
        scores["ASSERTIVE"] += 2.5
    if is_poetic:
        scores["POETIC"] += 3.0
    if is_dense and scope_events > 3:
        scores["PARENTHETICAL"] += 2.5
    if is_dense and hi_count > 5:
        scores["HEDGED"] += 2.0
    if has_anaphora and is_assertive:
        scores["PARALLEL"] += 2.5
    
    # Metric-based scoring
    if avg_words < 8 and hi_count < 2:
        scores["MINIMAL"] += 2.0
    if avg_words > 20 and complexity == "COMPLEX":
        scores["LONGFORM"] += 2.5
    if informality > 1.0:
        scores["CONVERSATIONAL"] += 2.0
    if hi_count > 6:
        scores["HEDGED"] += 1.5
        scores["DENSE"] += 1.0
    if is_contradictory:
        scores["DENSE"] += 2.0
    
    # Register adjustments
    if register == "INFORMAL":
        scores["CONVERSATIONAL"] += 1.0
        scores["ASSERTIVE"] += 0.5
    
    # Complexity adjustments
    if complexity == "COMPLEX":
        scores["LONGFORM"] += 1.0
        scores["HEDGED"] += 0.5
        scores["DENSE"] += 0.5
    
    # Find top mode
    top_mode = max(scores, key=scores.get)
    top_score = scores[top_mode]
    
    # Calculate confidence (normalize to 0-1)
    total_score = sum(scores.values())
    confidence = top_score / total_score if total_score > 0 else 0.0
    
    # If no clear winner, default to MINIMAL
    if top_score < 1.0:
        return "MINIMAL", 0.3
    
    return top_mode, min(confidence, 1.0)


# =============================================================================
# PROFILE AGGREGATION
# =============================================================================

def aggregate_user_history(user_id: str = "default", limit: int = 50) -> Dict[str, Any]:
    """
    Aggregate metrics from user's session history.
    
    Returns comprehensive stats across all sessions.
    """
    store = get_session_store()
    sessions = store.list_sessions(limit=limit)
    
    if not sessions:
        return {"session_count": 0, "has_history": False}
    
    # Collect metrics from each session
    all_metrics = {
        "word_counts": [],
        "avg_words": [],
        "hi_counts": [],
        "hi_rates": [],
        "openness_scores": [],
        "density_scores": [],
        "informality_scores": [],
        "clause_counts": [],
        "modes_detected": [],
        "stances": [],
        "complexities": [],
        "registers": [],
        "timestamps": [],
    }
    
    for session_entry in sessions:
        session_id = session_entry.get("session_id")
        session = store.load_session(session_id)
        
        if not session:
            continue
        
        data = session.get("data", {})
        hi_profile = data.get("high_intent_profile", {})
        phase1 = data.get("phase1", {}).get("outputs", {})
        
        # Extract metrics
        word_count = phase1.get("token_volume", {}).get("metrics", {}).get("total_token_count", 0)
        avg_words = phase1.get("token_volume", {}).get("metrics", {}).get("mean_tokens_per_sentence", 0)
        
        all_metrics["word_counts"].append(word_count)
        all_metrics["avg_words"].append(avg_words if avg_words else 0)
        all_metrics["hi_counts"].append(hi_profile.get("total_high_intent_events", 0))
        all_metrics["hi_rates"].append(hi_profile.get("high_intent_rate", 0))
        all_metrics["openness_scores"].append(hi_profile.get("epistemic_openness", 0.5))
        all_metrics["density_scores"].append(hi_profile.get("structural_density_score", 0))
        all_metrics["informality_scores"].append(hi_profile.get("informality_score", 0))
        all_metrics["clause_counts"].append(hi_profile.get("avg_clauses", 1.0))
        all_metrics["stances"].append(hi_profile.get("epistemic_stance", "UNKNOWN"))
        all_metrics["complexities"].append(hi_profile.get("syntax_complexity", "SIMPLE"))
        all_metrics["registers"].append(hi_profile.get("register", "FORMAL"))
        all_metrics["timestamps"].append(session_entry.get("created_at", ""))
        
        # Detect mode for this session
        mode, confidence = detect_mode_from_metrics(hi_profile)
        all_metrics["modes_detected"].append((mode, confidence))
    
    # Compute aggregate statistics
    def safe_mean(vals):
        return statistics.mean(vals) if vals else 0.0
    
    def safe_stdev(vals):
        return statistics.stdev(vals) if len(vals) > 1 else 0.0
    
    aggregated = {
        "session_count": len(sessions),
        "has_history": True,
        "first_session": all_metrics["timestamps"][-1] if all_metrics["timestamps"] else None,
        "latest_session": all_metrics["timestamps"][0] if all_metrics["timestamps"] else None,
        
        # Metric averages
        "avg_word_count": safe_mean(all_metrics["word_counts"]),
        "avg_words_per_sentence": safe_mean(all_metrics["avg_words"]),
        "avg_marker_count": safe_mean(all_metrics["hi_counts"]),
        "avg_marker_rate": safe_mean(all_metrics["hi_rates"]),
        "avg_openness": safe_mean(all_metrics["openness_scores"]),
        "avg_density": safe_mean(all_metrics["density_scores"]),
        "avg_informality": safe_mean(all_metrics["informality_scores"]),
        "avg_clauses": safe_mean(all_metrics["clause_counts"]),
        
        # Metric ranges
        "word_count_range": (min(all_metrics["word_counts"]) if all_metrics["word_counts"] else 0,
                            max(all_metrics["word_counts"]) if all_metrics["word_counts"] else 0),
        "marker_range": (min(all_metrics["hi_counts"]) if all_metrics["hi_counts"] else 0,
                        max(all_metrics["hi_counts"]) if all_metrics["hi_counts"] else 0),
        "openness_range": (min(all_metrics["openness_scores"]) if all_metrics["openness_scores"] else 0,
                          max(all_metrics["openness_scores"]) if all_metrics["openness_scores"] else 0),
        
        # Variability (consistency)
        "word_count_std": safe_stdev(all_metrics["word_counts"]),
        "marker_std": safe_stdev(all_metrics["hi_counts"]),
        "openness_std": safe_stdev(all_metrics["openness_scores"]),
        
        # Distributions
        "stance_distribution": dict(Counter(all_metrics["stances"])),
        "complexity_distribution": dict(Counter(all_metrics["complexities"])),
        "register_distribution": dict(Counter(all_metrics["registers"])),
        
        # Mode analysis
        "modes_detected": all_metrics["modes_detected"],
        
        # Raw data for trend analysis
        "_raw_openness": all_metrics["openness_scores"],
        "_raw_markers": all_metrics["hi_counts"],
        "_raw_timestamps": all_metrics["timestamps"],
    }
    
    return aggregated


def analyze_mode_tendencies(modes_detected: List[Tuple[str, float]]) -> Dict[str, Any]:
    """
    Analyze mode tendencies from detection history.
    
    Returns primary mode, secondary modes, and consistency score.
    """
    if not modes_detected:
        return {
            "primary_mode": "MINIMAL",
            "primary_confidence": 0.0,
            "secondary_modes": [],
            "consistency": 0.0,
            "mode_distribution": {},
        }
    
    # Weight by confidence
    weighted_counts = defaultdict(float)
    for mode, confidence in modes_detected:
        weighted_counts[mode] += confidence
    
    # Simple counts
    simple_counts = Counter(mode for mode, _ in modes_detected)
    
    # Find primary and secondary
    sorted_modes = sorted(weighted_counts.items(), key=lambda x: x[1], reverse=True)
    
    primary_mode = sorted_modes[0][0] if sorted_modes else "MINIMAL"
    primary_weight = sorted_modes[0][1] if sorted_modes else 0.0
    
    secondary_modes = [mode for mode, _ in sorted_modes[1:3] if weighted_counts[mode] > 0.5]
    
    # Calculate consistency (how often primary mode appears)
    total_sessions = len(modes_detected)
    primary_count = simple_counts.get(primary_mode, 0)
    consistency = primary_count / total_sessions if total_sessions > 0 else 0.0
    
    # Normalize confidence
    total_weight = sum(weighted_counts.values())
    primary_confidence = primary_weight / total_weight if total_weight > 0 else 0.0
    
    return {
        "primary_mode": primary_mode,
        "primary_confidence": round(primary_confidence, 3),
        "secondary_modes": secondary_modes,
        "consistency": round(consistency, 3),
        "mode_distribution": dict(simple_counts),
        "weighted_distribution": {k: round(v, 2) for k, v in weighted_counts.items()},
    }


def analyze_evolution(raw_values: List[float], timestamps: List[str], metric_name: str) -> Dict[str, Any]:
    """
    Analyze how a metric has evolved over time.
    
    Returns trend direction, rate of change, and stability.
    """
    if len(raw_values) < 3:
        return {
            "metric": metric_name,
            "trend": "INSUFFICIENT_DATA",
            "trend_description": "Need more sessions to detect trends",
            "change_rate": 0.0,
            "stability": 0.0,
        }
    
    # Values are in reverse chronological order (newest first)
    # Reverse for chronological analysis
    values = list(reversed(raw_values))
    
    # Simple linear trend (compare first half to second half)
    mid = len(values) // 2
    first_half_avg = statistics.mean(values[:mid]) if mid > 0 else 0
    second_half_avg = statistics.mean(values[mid:]) if mid < len(values) else 0
    
    # Calculate change
    if first_half_avg > 0:
        change_rate = (second_half_avg - first_half_avg) / first_half_avg
    else:
        change_rate = 0.0
    
    # Determine trend
    if abs(change_rate) < 0.1:
        trend = "STABLE"
        trend_desc = f"Your {metric_name} has remained consistent"
    elif change_rate > 0.2:
        trend = "INCREASING"
        trend_desc = f"Your {metric_name} has been growing"
    elif change_rate > 0:
        trend = "SLIGHTLY_INCREASING"
        trend_desc = f"Your {metric_name} has increased slightly"
    elif change_rate < -0.2:
        trend = "DECREASING"
        trend_desc = f"Your {metric_name} has been declining"
    else:
        trend = "SLIGHTLY_DECREASING"
        trend_desc = f"Your {metric_name} has decreased slightly"
    
    # Calculate stability (inverse of coefficient of variation)
    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values) if len(values) > 1 else 0
    cv = std_val / mean_val if mean_val > 0 else 0
    stability = max(0, 1 - cv)  # 1 = very stable, 0 = highly variable
    
    return {
        "metric": metric_name,
        "trend": trend,
        "trend_description": trend_desc,
        "change_rate": round(change_rate, 3),
        "stability": round(stability, 3),
        "early_avg": round(first_half_avg, 3),
        "recent_avg": round(second_half_avg, 3),
    }


# =============================================================================
# PROFILE GENERATION
# =============================================================================

def generate_evolving_profile(user_id: str = "default") -> Dict[str, Any]:
    """
    Generate a comprehensive evolving profile for a user.
    
    This is the main entry point for the profile tab.
    """
    # Aggregate history
    history = aggregate_user_history(user_id)
    
    if not history.get("has_history"):
        return {
            "has_profile": False,
            "message": "Start writing to build your profile. Each session adds to your narrator portrait.",
            "session_count": 0,
        }
    
    session_count = history["session_count"]
    
    # Analyze mode tendencies
    mode_analysis = analyze_mode_tendencies(history.get("modes_detected", []))
    primary_mode = mode_analysis["primary_mode"]
    
    # Get base profile for primary mode
    base_profile = generate_narrator_profile(
        primary_mode,
        {
            "epistemic_openness": history["avg_openness"],
            "informality_score": history["avg_informality"],
            "structural_density_score": history["avg_density"],
        }
    )
    
    # Analyze evolution
    evolution = {
        "openness": analyze_evolution(
            history.get("_raw_openness", []),
            history.get("_raw_timestamps", []),
            "epistemic openness"
        ),
        "markers": analyze_evolution(
            history.get("_raw_markers", []),
            history.get("_raw_timestamps", []),
            "marker density"
        ),
    }
    
    # Build profile maturity description
    if session_count < 3:
        maturity = "EMERGING"
        maturity_desc = "Your profile is just beginning to take shape. A few more sessions will sharpen the picture."
    elif session_count < 10:
        maturity = "DEVELOPING"
        maturity_desc = "Patterns are emerging. Your writing tendencies are becoming clearer with each session."
    elif session_count < 25:
        maturity = "ESTABLISHED"
        maturity_desc = "A clear picture of your writing voice has emerged. Your patterns are consistent."
    else:
        maturity = "MATURE"
        maturity_desc = "Your narrator profile is well-established, built from substantial writing history."
    
    # Generate personalized insights
    insights = generate_personalized_insights(history, mode_analysis, evolution)
    
    # Generate the "You write..." sketch
    personalized_sketch = generate_personalized_sketch(
        primary_mode, 
        mode_analysis, 
        history, 
        evolution
    )
    
    return {
        "has_profile": True,
        "session_count": session_count,
        "profile_maturity": maturity,
        "maturity_description": maturity_desc,
        "first_session": history.get("first_session"),
        "latest_session": history.get("latest_session"),
        
        # Primary profile
        "primary_mode": primary_mode,
        "profile_title": base_profile["title"],
        "profile_essence": base_profile["essence"],
        "personalized_sketch": personalized_sketch,
        
        # Mode analysis
        "mode_confidence": mode_analysis["primary_confidence"],
        "secondary_modes": mode_analysis["secondary_modes"],
        "mode_consistency": mode_analysis["consistency"],
        "mode_distribution": mode_analysis["mode_distribution"],
        
        # Aggregate metrics
        "metrics": {
            "avg_word_count": round(history["avg_word_count"], 1),
            "avg_words_per_sentence": round(history["avg_words_per_sentence"], 1),
            "avg_marker_count": round(history["avg_marker_count"], 1),
            "avg_openness": round(history["avg_openness"], 3),
            "avg_density": round(history["avg_density"], 2),
            "avg_informality": round(history["avg_informality"], 2),
        },
        
        # Ranges (your spectrum)
        "ranges": {
            "word_count": history["word_count_range"],
            "markers": history["marker_range"],
            "openness": history["openness_range"],
        },
        
        # Distributions
        "distributions": {
            "stance": history["stance_distribution"],
            "complexity": history["complexity_distribution"],
            "register": history["register_distribution"],
        },
        
        # Evolution
        "evolution": evolution,
        
        # Personalized insights
        "insights": insights,
        
        # Growth edges from base profile
        "growth_edges": base_profile["growth_edges"],
        
        # Writing ancestors
        "writing_ancestors": base_profile["writing_ancestors"],
        
        # Clusters
        "clusters": base_profile["clusters"],
    }


def generate_personalized_insights(
    history: Dict[str, Any],
    mode_analysis: Dict[str, Any],
    evolution: Dict[str, Any]
) -> List[str]:
    """Generate personalized insights based on user's writing patterns."""
    insights = []
    
    # Consistency insight
    consistency = mode_analysis["consistency"]
    if consistency > 0.8:
        insights.append(
            f"You have a remarkably consistent voice. {int(consistency * 100)}% of your sessions "
            f"show the same dominant mode—you know what you're doing and you do it."
        )
    elif consistency > 0.5:
        insights.append(
            f"Your writing voice is developing consistency. About {int(consistency * 100)}% of "
            f"sessions share your primary mode, with healthy variation in the rest."
        )
    elif consistency < 0.3 and history["session_count"] > 5:
        secondary = mode_analysis.get("secondary_modes", [])
        if secondary:
            insights.append(
                f"You're a versatile writer—your mode shifts between {mode_analysis['primary_mode']} "
                f"and {', '.join(secondary)}. This range is an asset, not inconsistency."
            )
    
    # Openness insight
    avg_openness = history["avg_openness"]
    openness_range = history["openness_range"]
    if openness_range[1] - openness_range[0] > 0.5:
        insights.append(
            "You have wide epistemic range—sometimes certain, sometimes exploratory. "
            "You're not locked into one stance."
        )
    elif avg_openness > 0.7:
        insights.append(
            "You consistently leave room for uncertainty. Your prose invites rather than declares."
        )
    elif avg_openness < 0.4:
        insights.append(
            "You write with conviction. Your prose moves toward closure, toward knowing."
        )
    
    # Evolution insight
    openness_trend = evolution.get("openness", {}).get("trend", "STABLE")
    if openness_trend == "INCREASING":
        insights.append(
            "Over time, you've become more open in your prose—more hedges, more possibilities, "
            "more room for the reader to think alongside you."
        )
    elif openness_trend == "DECREASING":
        insights.append(
            "Your writing has grown more assertive over time—moving toward clearer claims, "
            "stronger positions."
        )
    
    # Register insight
    register_dist = history.get("register_distribution", {})
    informal_pct = register_dist.get("INFORMAL", 0) / history["session_count"] if history["session_count"] > 0 else 0
    if informal_pct > 0.7:
        insights.append(
            "Your default register is conversational—you write like you're talking to someone. "
            "This creates intimacy."
        )
    elif informal_pct < 0.3:
        insights.append(
            "You tend toward formal register. Your prose has weight, authority—the feeling "
            "that something important is being said."
        )
    
    # Complexity insight
    avg_clauses = history.get("avg_clauses", 1.0)
    if avg_clauses > 2.5:
        insights.append(
            "You build complex sentences—multiple clauses, subordination, architecture. "
            "Your prose asks for (and rewards) attention."
        )
    elif avg_clauses < 1.3:
        insights.append(
            "Your sentences are clean and direct. One clause, one thought. "
            "This is a kind of discipline."
        )
    
    return insights[:5]  # Limit to top 5 insights


def generate_personalized_sketch(
    primary_mode: str,
    mode_analysis: Dict[str, Any],
    history: Dict[str, Any],
    evolution: Dict[str, Any]
) -> str:
    """Generate a personalized 'You write...' sketch."""
    
    # Get base elements
    base = MODE_PROFILES.get(primary_mode, MODE_PROFILES["MINIMAL"])
    title = base["title"]
    
    # Build personalized opening
    consistency = mode_analysis["consistency"]
    secondary = mode_analysis.get("secondary_modes", [])
    
    if consistency > 0.7:
        if not secondary:
            opening = f"You are, consistently and distinctly, **{title}**."
        else:
            opening = f"You are primarily **{title}**, with occasional ventures into {' and '.join(secondary)} territory."
    elif consistency > 0.4:
        if secondary:
            opening = f"You move between **{title}** and **{MODE_PROFILES.get(secondary[0], {}).get('title', secondary[0])}**—two sides of your writing voice."
        else:
            opening = f"You're developing as **{title}**, though your voice is still finding its settled shape."
    else:
        opening = f"You're a shape-shifter. Your writing moves through multiple modes, with **{title}** as your most frequent home base."
    
    # Add metric-based observations
    observations = []
    
    avg_openness = history["avg_openness"]
    if avg_openness > 0.7:
        observations.append("Your prose leans toward openness—you'd rather suggest than assert, wonder than declare.")
    elif avg_openness < 0.4:
        observations.append("Your prose tends toward conviction. When you say something, you mean it.")
    
    avg_informality = history.get("avg_informality", 0)
    if avg_informality > 1.0:
        observations.append("You write with casual warmth—the reader feels addressed, not lectured.")
    elif avg_informality < 0.3:
        observations.append("Your register runs formal—there's weight to your sentences, a sense of occasion.")
    
    # Add evolution observation
    openness_evolution = evolution.get("openness", {})
    if openness_evolution.get("trend") == "INCREASING" and history["session_count"] > 5:
        observations.append("And over time, you've been opening up—more uncertainty, more room for questions.")
    elif openness_evolution.get("trend") == "DECREASING" and history["session_count"] > 5:
        observations.append("And over time, you've been moving toward firmer ground—fewer hedges, clearer claims.")
    
    # Combine into sketch
    obs_text = " ".join(observations) if observations else ""
    
    session_note = ""
    if history["session_count"] < 5:
        session_note = f"\n\n*(Based on {history['session_count']} sessions. Your profile will sharpen with more writing.)*"
    elif history["session_count"] >= 25:
        session_note = f"\n\n*(Built from {history['session_count']} sessions—a substantial portrait of your writing voice.)*"
    
    return f"{opening}\n\n{obs_text}{session_note}"


# =============================================================================
# PROFILE TAB DATA FORMATTER
# =============================================================================

def get_profile_tab_data(user_id: str = "default") -> Dict[str, Any]:
    """
    Get all data needed to render the Profile tab in the frontend.
    
    This formats the evolving profile for display.
    """
    profile = generate_evolving_profile(user_id)
    
    if not profile.get("has_profile"):
        return {
            "status": "NO_HISTORY",
            "message": profile.get("message", "Start writing to build your profile."),
            "cta": "Write your first sample to begin",
        }
    
    # Format for frontend display
    return {
        "status": "ACTIVE",
        
        # Header section
        "header": {
            "title": profile["profile_title"],
            "essence": profile["profile_essence"],
            "maturity": profile["profile_maturity"],
            "maturity_description": profile["maturity_description"],
            "session_count": profile["session_count"],
        },
        
        # Main sketch
        "sketch": profile["personalized_sketch"],
        
        # Mode breakdown
        "modes": {
            "primary": profile["primary_mode"],
            "confidence": f"{int(profile['mode_confidence'] * 100)}%",
            "consistency": f"{int(profile['mode_consistency'] * 100)}%",
            "secondary": profile["secondary_modes"],
            "distribution": profile["mode_distribution"],
        },
        
        # Your Numbers section
        "metrics": {
            "words_per_session": f"{profile['metrics']['avg_word_count']:.0f}",
            "words_per_sentence": f"{profile['metrics']['avg_words_per_sentence']:.1f}",
            "markers_per_session": f"{profile['metrics']['avg_marker_count']:.1f}",
            "epistemic_openness": f"{profile['metrics']['avg_openness']:.0%}",
            "structural_density": f"{profile['metrics']['avg_density']:.2f}",
            "informality": f"{profile['metrics']['avg_informality']:.2f}",
        },
        
        # Your Spectrum section
        "spectrum": {
            "openness": {
                "min": profile["ranges"]["openness"][0],
                "max": profile["ranges"]["openness"][1],
                "avg": profile["metrics"]["avg_openness"],
            },
            "markers": {
                "min": profile["ranges"]["markers"][0],
                "max": profile["ranges"]["markers"][1],
                "avg": profile["metrics"]["avg_marker_count"],
            },
        },
        
        # Distributions
        "distributions": profile["distributions"],
        
        # Evolution section
        "evolution": {
            "openness": {
                "trend": profile["evolution"]["openness"]["trend"],
                "description": profile["evolution"]["openness"]["trend_description"],
            },
            "markers": {
                "trend": profile["evolution"]["markers"]["trend"],
                "description": profile["evolution"]["markers"]["trend_description"],
            },
        },
        
        # Insights
        "insights": profile["insights"],
        
        # Growth edges
        "growth_edges": profile["growth_edges"],
        
        # Writing ancestors
        "writing_ancestors": profile["writing_ancestors"],
        
        # Meta
        "meta": {
            "first_session": profile["first_session"],
            "latest_session": profile["latest_session"],
            "clusters": profile["clusters"],
        },
    }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LNCP USER PROFILE AGGREGATOR")
    print("=" * 70)
    
    # Try to generate profile from existing sessions
    profile = generate_evolving_profile()
    
    if not profile.get("has_profile"):
        print("\nNo session history found. Creating mock sessions for demo...")
        
        # Create some mock sessions for testing
        from session_persistence import get_session_store
        from datetime import datetime
        import uuid
        
        store = get_session_store()
        
        # Mock sessions with different characteristics
        mock_sessions = [
            {
                "high_intent_profile": {
                    "total_high_intent_events": 2,
                    "high_intent_rate": 0.67,
                    "epistemic_openness": 0.6,
                    "epistemic_stance": "OPEN",
                    "is_assertive_mode": False,
                    "is_minimal": True,
                    "register": "INFORMAL",
                    "syntax_complexity": "SIMPLE",
                    "structural_density_score": 0.2,
                    "informality_score": 1.2,
                    "avg_clauses": 1.0,
                },
                "phase1": {"outputs": {"token_volume": {"metrics": {"total_token_count": 25, "mean_tokens_per_sentence": 8}}}},
                "phase6": {"summary": {"title": "Session 1"}, "high_intent_reflection": {"epistemic_stance": "OPEN"}},
            },
            {
                "high_intent_profile": {
                    "total_high_intent_events": 5,
                    "high_intent_rate": 1.67,
                    "epistemic_openness": 0.75,
                    "epistemic_stance": "OPEN",
                    "is_assertive_mode": False,
                    "is_structurally_dense": True,
                    "register": "FORMAL",
                    "syntax_complexity": "MODERATE",
                    "structural_density_score": 1.5,
                    "informality_score": 0.3,
                    "avg_clauses": 2.0,
                },
                "phase1": {"outputs": {"token_volume": {"metrics": {"total_token_count": 45, "mean_tokens_per_sentence": 15}}}},
                "phase6": {"summary": {"title": "Session 2"}, "high_intent_reflection": {"epistemic_stance": "OPEN"}},
            },
            {
                "high_intent_profile": {
                    "total_high_intent_events": 1,
                    "high_intent_rate": 0.33,
                    "epistemic_openness": 0.5,
                    "epistemic_stance": "MINIMAL",
                    "is_assertive_mode": True,
                    "is_minimal": True,
                    "register": "INFORMAL",
                    "syntax_complexity": "SIMPLE",
                    "structural_density_score": 0.0,
                    "informality_score": 1.0,
                    "avg_clauses": 1.0,
                },
                "phase1": {"outputs": {"token_volume": {"metrics": {"total_token_count": 18, "mean_tokens_per_sentence": 6}}}},
                "phase6": {"summary": {"title": "Session 3"}, "high_intent_reflection": {"epistemic_stance": "MINIMAL"}},
            },
        ]
        
        for i, mock in enumerate(mock_sessions):
            session_id = f"demo-{uuid.uuid4().hex[:8]}"
            store.save_session(session_id, mock, {"mode": "STORY"})
            print(f"  Created mock session {i+1}: {session_id}")
        
        # Regenerate profile
        profile = generate_evolving_profile()
    
    print(f"\n{'='*70}")
    print("GENERATED PROFILE")
    print("=" * 70)
    
    print(f"\nSession count: {profile['session_count']}")
    print(f"Maturity: {profile['profile_maturity']}")
    print(f"\nPrimary mode: {profile['primary_mode']}")
    print(f"Title: {profile['profile_title']}")
    print(f"Confidence: {profile['mode_confidence']:.0%}")
    print(f"Consistency: {profile['mode_consistency']:.0%}")
    
    print(f"\n--- PERSONALIZED SKETCH ---")
    print(profile['personalized_sketch'])
    
    print(f"\n--- INSIGHTS ---")
    for insight in profile['insights']:
        print(f"• {insight}")
    
    print(f"\n--- GROWTH EDGES ---")
    for edge in profile['growth_edges']:
        print(f"→ {edge}")
    
    print(f"\n--- WRITING ANCESTORS ---")
    print(profile['writing_ancestors'])
