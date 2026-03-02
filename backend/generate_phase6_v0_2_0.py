#!/usr/bin/env python3
"""
Phase-6 Summary Generator
Version: 0.2.0

Generates Phase-6 Summary output with SAMPLE-SPECIFIC content.

CHANGELOG v0.2.0:
- Deep interpolation: references actual metrics, patterns, and markers
- Historical awareness: can reference previous sessions
- Paths Forward: replaces mode_reflection with actionable next steps
- Exercise recommendation based on structural patterns

This generator transforms generic templates into personalized summaries
that reference the user's specific sample data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lncp_llm_expander import (
    expand_content,
    select_next_step,
    is_llm_available,
    get_enhancement_notice,
)


# =============================================================================
# Configuration
# =============================================================================

PHASE6_VERSION = "0.2.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.2.0"
SOURCE_PHASE3_VERSION = "0.2.0"

NEXT_STEP_POOL_PATH = Path(__file__).parent / "phase6-next-step-pool-v0.1.0.json"


def load_next_step_pool() -> Dict[str, Any]:
    """Load the next-step prompt pool."""
    with open(NEXT_STEP_POOL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Sample-Specific Content Generators
# =============================================================================

def _format_number(n: float, decimals: int = 1) -> str:
    """Format a number for display."""
    if decimals == 0:
        return str(int(n))
    return f"{n:.{decimals}f}"


def _get_event_description(phase1: Dict[str, Any]) -> str:
    """Generate a description of structural events found."""
    outputs = phase1.get("outputs", {})
    
    # Helper to get nested metric
    def get_metric(output_key: str, metric_key: str, default=0):
        output = outputs.get(output_key, {})
        metrics = output.get("metrics", output)
        return metrics.get(metric_key, default)
    
    zero_count = get_metric("zero_event_presence", "total_zero_event_count", 0)
    op_count = get_metric("operator_event_presence", "total_operator_event_count", 0)
    scope_count = get_metric("scope_event_presence", "total_scope_event_count", 0)
    
    parts = []
    if zero_count > 0:
        marker = "pause marker" if zero_count == 1 else "pause markers"
        parts.append(f"{zero_count} {marker} (ellipses or dashes)")
    if op_count > 0:
        marker = "operator" if op_count == 1 else "operators"
        parts.append(f"{op_count} {marker} (connective symbols)")
    if scope_count > 0:
        marker = "scope marker" if scope_count == 1 else "scope markers"
        parts.append(f"{scope_count} {marker} (parentheses, brackets, or quotes)")
    
    if not parts:
        return "no structural markers like pauses, operators, or nested scopes"
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{parts[0]}, {parts[1]}, and {parts[2]}"


def _get_dominant_pattern_description(phase1: Dict[str, Any]) -> str:
    """Describe the dominant structural pattern."""
    outputs = phase1.get("outputs", {})
    conc = outputs.get("signature_concentration", {})
    metrics = conc.get("metrics", conc)
    
    top_sigs = metrics.get("top_signatures", [])
    coverage = metrics.get("top_signature_coverage", 0)
    
    if not top_sigs:
        return "no dominant pattern—each sentence takes a unique shape"
    
    top = top_sigs[0]
    count = top.get("count", 0)
    
    if count == 1:
        return "no pattern repeats—all structures are unique"
    elif count == 2:
        return f"one pattern appears twice, suggesting an emerging habit"
    else:
        return f"one pattern appears {count} times, a clear structural preference"


def _get_high_intent_summary(hi_profile: Dict[str, Any]) -> str:
    """Summarize high-intent markers found."""
    if not hi_profile:
        return "no epistemic markers detected"
    
    total = hi_profile.get("total_high_intent_events", 0)
    unique = hi_profile.get("unique_markers", [])
    dominant = hi_profile.get("dominant_category", "")
    
    if total == 0:
        return "no stance-marking words like 'perhaps,' 'definitely,' or 'believe'"
    
    marker_examples = ", ".join(f'"{m}"' for m in unique[:3])
    
    if total == 1:
        return f"one stance marker ({marker_examples})"
    else:
        cat_text = f", mostly {dominant.lower()}" if dominant else ""
        return f"{total} stance markers including {marker_examples}{cat_text}"


def generate_structural_overview(
    phase1: Dict[str, Any],
    phase2: Dict[str, Any],
    hi_profile: Dict[str, Any],
    sentences: List[str],
) -> str:
    """
    Generate a deeply personalized structural overview.
    
    References specific metrics from this sample.
    """
    outputs = phase1.get("outputs", {})
    mode = phase2.get("presentation_mode", "DESCRIPTIVE")
    
    # Extract metrics - handle nested 'metrics' structure from Phase-1
    def get_metric(output_key: str, metric_key: str, default=0):
        output = outputs.get(output_key, {})
        metrics = output.get("metrics", output)  # Fallback to output if no nested metrics
        return metrics.get(metric_key, default)
    
    # Extract metrics
    sentence_count = get_metric("sentence_count", "sentence_count", 0)
    total_tokens = get_metric("token_volume", "total_token_count", 0)
    mean_tokens = get_metric("token_volume", "mean_tokens_per_sentence", 0)
    
    unique_sigs = get_metric("structural_variety", "unique_signature_count", 0)
    variety_ratio = get_metric("structural_variety", "signature_variety_ratio", 0)
    
    total_events = get_metric("structural_density", "total_structural_events", 0)
    density = get_metric("structural_density", "structural_density", 0)
    
    # Get specific descriptions
    event_desc = _get_event_description(phase1)
    pattern_desc = _get_dominant_pattern_description(phase1)
    hi_desc = _get_high_intent_summary(hi_profile)
    
    # Build personalized overview
    if mode == "DESCRIPTIVE":
        # Smaller sample - more cautious language
        overview = f"""Your sample contains {sentence_count} sentences totaling {total_tokens} words, averaging {_format_number(mean_tokens)} words per sentence.

Structurally, we find {event_desc}. Your sentences show {unique_sigs} unique structural shapes out of {sentence_count} (variety ratio: {_format_number(variety_ratio, 2)}), meaning {pattern_desc}.

At the word level, we detect {hi_desc}. With {sentence_count} sentences, these observations describe what appears in this specific sample—a longer piece would reveal whether these patterns persist or represent one moment in a broader range."""

    else:
        # Larger sample - more interpretive
        density_desc = "minimal structural decoration" if mean_events < 0.3 else (
            "moderate structural activity" if mean_events < 1.0 else "rich structural density"
        )
        
        overview = f"""Your {sentence_count} sentences ({total_tokens} words, averaging {_format_number(mean_tokens)} per sentence) reveal a structural portrait beginning to stabilize.

We find {event_desc}, creating {density_desc} across the sample. Your {unique_sigs} unique structural shapes yield a variety ratio of {_format_number(variety_ratio, 2)}—{pattern_desc}.

The epistemic layer shows {hi_desc}, shaping how your claims land with readers. These patterns likely reflect something genuine about how you build sentences, though context always matters—the same writer structures differently in different settings."""

    return overview.strip()


def generate_semiotic_synthesis(
    phase1: Dict[str, Any],
    phase3: Dict[str, Any],
    sentences: List[str],
) -> str:
    """
    Generate semiotic synthesis with sample-specific observations.
    """
    outputs = phase1.get("outputs", {})
    syntheses = phase3.get("syntheses", [])
    
    # Helper to get nested metric
    def get_metric(output_key: str, metric_key: str, default=0):
        output = outputs.get(output_key, {})
        metrics = output.get("metrics", output)
        return metrics.get(metric_key, default)
    
    # Extract specific metrics for each lens
    variety_ratio = get_metric("structural_variety", "signature_variety_ratio", 0)
    zero_count = get_metric("zero_event_presence", "total_zero_event_count", 0)
    scope_count = get_metric("scope_event_presence", "total_scope_event_count", 0)
    density = get_metric("structural_density", "structural_density", 0)
    
    # Interpretant stabilization observation
    if variety_ratio >= 0.9:
        stab_obs = "each sentence takes its own shape, resisting the repetition that would allow interpretants to stabilize"
    elif variety_ratio >= 0.6:
        stab_obs = "some shapes recur while others appear only once, creating partial stabilization"
    else:
        stab_obs = "recurring shapes dominate, generating stable interpretive patterns readers can anticipate"
    
    # Mediation observation
    if zero_count == 0 and scope_count == 0:
        med_obs = "meaning passes through largely unmediated—no pauses or nested layers interrupt the flow"
    elif zero_count > 0 and scope_count > 0:
        med_obs = f"both pause markers ({zero_count}) and scope markers ({scope_count}) create a textured passage where meaning is shaped and layered"
    elif zero_count > 0:
        med_obs = f"pause markers ({zero_count}) create moments of suspension, but no nested scopes add layers"
    else:
        med_obs = f"scope markers ({scope_count}) create nested meaning, but no pauses interrupt the flow"
    
    # Density observation
    if density < 0.3:
        dens_obs = "sparse—structural features remain distinct rather than clustering"
    elif density < 1.0:
        dens_obs = "moderate—some sentences carry structural weight while others proceed cleanly"
    else:
        dens_obs = "high—structural features cluster, creating rich interpretive texture"
    
    synthesis = f"""Through three semiotic lenses, your sample reveals distinct patterns:

**Interpretant Stabilization**: With a variety ratio of {_format_number(variety_ratio, 2)}, {stab_obs}. In Peircean terms, this shapes whether readers develop expectations or encounter each sentence fresh.

**Mediation & Boundary**: In this sample, {med_obs}. These structural features—or their absence—shape how readers navigate from sign to meaning.

**Relational Density**: Structural density is {dens_obs} (averaging {_format_number(density, 2)} events per sentence). This determines whether readers engage primarily with content or must also navigate form."""

    return synthesis.strip()


def generate_paths_forward(
    phase1: Dict[str, Any],
    phase4a: Dict[str, Any],
    phase4b: Dict[str, Any],
    hi_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate Paths Forward with recommended exercise.
    
    Returns structured data for the three options:
    - Next Sample
    - Do an Exercise (recommended based on patterns)
    - Switch to School Mode
    """
    outputs = phase1.get("outputs", {})
    
    # Helper to get nested metric
    def get_metric(output_key: str, metric_key: str, default=0):
        output = outputs.get(output_key, {})
        metrics = output.get("metrics", output)
        return metrics.get(metric_key, default)
    
    # Extract key metrics for recommendation
    sentence_count = get_metric("sentence_count", "sentence_count", 0)
    variety_ratio = get_metric("structural_variety", "signature_variety_ratio", 0)
    zero_count = get_metric("zero_event_presence", "total_zero_event_count", 0)
    scope_count = get_metric("scope_event_presence", "total_scope_event_count", 0)
    density = get_metric("structural_density", "structural_density", 0)
    
    epistemic_openness = hi_profile.get("epistemic_openness", 0.5) if hi_profile else 0.5
    
    # Rule-based exercise recommendation (2C approach)
    recommended_exercise = None
    exercise_rationale = ""
    exercise_lens = ""
    
    # Priority rules for exercise selection
    if sentence_count < 5:
        # Small sample - recommend volume
        recommended_exercise = {
            "type": "REWRITE",
            "prompt": "Choose one of your sentences and expand it into three sentences, keeping the same core idea but adding detail and qualification.",
            "source": "INTERPRETANT_STABILIZATION",
        }
        exercise_rationale = f"With only {sentence_count} sentences, expanding your sample would reveal whether your patterns persist."
        exercise_lens = "Building Volume"
        
    elif variety_ratio < 0.5:
        # Low variety - recommend structural experimentation
        recommended_exercise = {
            "type": "REWRITE",
            "prompt": "Rewrite your most-repeated structural pattern in three different ways: as a shorter sentence, as a longer sentence with an embedded clause, and as a sentence with a parenthetical aside.",
            "source": "INTERPRETANT_STABILIZATION",
        }
        exercise_rationale = f"Your variety ratio of {_format_number(variety_ratio, 2)} suggests structural habits—this exercise expands your range."
        exercise_lens = "Structural Variety"
        
    elif zero_count == 0 and scope_count == 0:
        # No boundary markers - recommend adding mediation
        recommended_exercise = {
            "type": "PRACTICE",
            "prompt": "Take one of your sentences and add both a pause marker (ellipsis or dash) and a parenthetical aside. Notice how the reading experience changes.",
            "source": "MEDIATION_AND_BOUNDARY",
        }
        exercise_rationale = "Your sentences flow without boundary markers—this exercise explores what mediation adds."
        exercise_lens = "Adding Boundaries"
        
    elif density > 1.5:
        # High density - recommend simplification
        recommended_exercise = {
            "type": "REWRITE",
            "prompt": "Find your densest sentence and rewrite it three ways: removing one structural feature at a time. Notice what each removal costs and what it gains.",
            "source": "RELATIONAL_DENSITY",
        }
        exercise_rationale = f"With {_format_number(density, 1)} structural events per sentence, this exercise explores simplification."
        exercise_lens = "Reducing Density"
        
    elif epistemic_openness < 0.35:
        # Closed stance - recommend opening
        recommended_exercise = {
            "type": "REFLECT",
            "prompt": "Rewrite one of your most certain statements using tentative language: 'might,' 'perhaps,' 'could.' How does the meaning shift?",
            "source": "HIGH_INTENT",
        }
        exercise_rationale = "Your writing shows firm epistemic stance—this exercise explores tentativeness."
        exercise_lens = "Epistemic Range"
        
    elif epistemic_openness > 0.65:
        # Open stance - recommend closing
        recommended_exercise = {
            "type": "REFLECT",
            "prompt": "Rewrite one of your most tentative statements with certainty: 'definitely,' 'must,' 'clearly.' How does the meaning shift?",
            "source": "HIGH_INTENT",
        }
        exercise_rationale = "Your writing leaves room for interpretation—this exercise explores commitment."
        exercise_lens = "Epistemic Range"
        
    else:
        # Default - exploratory exercise
        recommended_exercise = {
            "type": "COMPARE",
            "prompt": "Write the same idea in two registers: one formal and one casual. Compare the structural differences that emerge.",
            "source": "EXPLORATION",
        }
        exercise_rationale = "Your patterns are balanced—this exercise explores how register shapes structure."
        exercise_lens = "Register Exploration"
    
    return {
        "next_sample": {
            "title": "Write Another Sample",
            "description": "Start a new writing session to see how your patterns compare across different pieces.",
            "action": "new_session",
        },
        "recommended_exercise": {
            "title": f"Exercise: {exercise_lens}",
            "description": exercise_rationale,
            "exercise": recommended_exercise,
            "action": "do_exercise",
        },
        "school_mode": {
            "title": "Enter School Mode",
            "description": "Structured lessons that build your structural awareness step by step.",
            "action": "school_mode",
        },
    }


def generate_summary_title(
    phase1: Dict[str, Any],
    hi_profile: Dict[str, Any],
) -> str:
    """Generate an evocative, sample-aware title."""
    outputs = phase1.get("outputs", {})
    sentence_count = outputs.get("sentence_count", {}).get("count", 0)
    variety_ratio = outputs.get("structural_variety", {}).get("variety_ratio", 0)
    
    # Determine size descriptor
    if sentence_count < 4:
        size = "A Glimpse"
    elif sentence_count < 8:
        size = "A Portrait"
    else:
        size = "A Study"
    
    # Determine character from variety and stance
    openness = hi_profile.get("epistemic_openness", 0.5) if hi_profile else 0.5
    
    if variety_ratio > 0.8:
        character = "in Variety"
    elif variety_ratio < 0.4:
        character = "in Rhythm"
    elif openness < 0.35:
        character = "in Conviction"
    elif openness > 0.65:
        character = "in Question"
    else:
        character = "in Balance"
    
    return f"{size}: Your Structure {character}"


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase6(
    phase1: Dict[str, Any],
    phase2: Dict[str, Any],
    phase3: Dict[str, Any],
    phase4: Dict[str, Any],
    phase4_mode: str,
    high_intent_profile: Dict[str, Any],
    sentences: Optional[List[str]] = None,
    historical_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-6 Summary output with sample-specific content.
    
    Args:
        phase1: Phase-1 compute output
        phase2: Phase-2 UX output
        phase3: Phase-3 synthesis output
        phase4: Phase-4a or Phase-4b output
        phase4_mode: "PROMPTING" or "GUIDANCE"
        high_intent_profile: High-Intent profile from parser
        sentences: Original sentences (for reference)
        historical_context: Optional data from previous sessions
        
    Returns:
        Phase-6 Summary output conforming to schema
    """
    sentences = sentences or []
    llm_available = is_llm_available()
    
    # Generate title
    title = generate_summary_title(phase1, high_intent_profile)
    
    # Generate sample-specific content
    structural_overview = generate_structural_overview(
        phase1, phase2, high_intent_profile, sentences
    )
    
    semiotic_synthesis = generate_semiotic_synthesis(
        phase1, phase3, sentences
    )
    
    # Generate paths forward (replaces mode_reflection)
    phase4a = phase4 if phase4_mode == "PROMPTING" else {}
    phase4b = phase4 if phase4_mode == "GUIDANCE" else {}
    paths_forward = generate_paths_forward(
        phase1,
        phase4a,
        phase4b if phase4_mode == "GUIDANCE" else {},
        high_intent_profile,
    )
    
    # Generate High-Intent reflection
    hi_overview, hi_stance, hi_notable = _generate_high_intent_reflection(
        high_intent_profile, phase1
    )
    
    # Select next step from pool
    context = {
        "phase1": phase1,
        "high_intent_profile": high_intent_profile,
    }
    pool_data = load_next_step_pool()
    prompts = pool_data.get("prompts", [])
    selected_prompt, rationale = select_next_step(context, prompts)
    
    # Get forward pointers
    forward_pointers = pool_data.get("forward_pointers", [])[:3]
    
    # Build output
    output = {
        "phase6_version": PHASE6_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase2_version": SOURCE_PHASE2_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "source_phase4_mode": phase4_mode,
        "synthesis_scope": "SAMPLE_SPECIFIC",
        "interpretive_frame": "LNCP_PEIRCEAN",
        "summary": {
            "title": title,
            "structural_overview": structural_overview,
            "semiotic_synthesis": semiotic_synthesis,
        },
        "paths_forward": paths_forward,
        "high_intent_reflection": {
            "present": high_intent_profile.get("total_high_intent_events", 0) > 0 if high_intent_profile else False,
            "overview": hi_overview,
            "epistemic_stance": hi_stance,
            "notable_markers": hi_notable,
        },
        "next_step": {
            "prompt_id": selected_prompt.get("prompt_id", "NS_001"),
            "prompt_text": selected_prompt.get("prompt_text", "Would you like to continue exploring?"),
            "rationale": rationale,
            "category": selected_prompt.get("category", "EXPLORATION"),
        },
        "forward_pointers": [
            {
                "pointer_id": fp.get("pointer_id", f"FP_{i:03d}"),
                "title": fp.get("title", "Future Exercise"),
                "description": fp.get("description", "Coming soon."),
                "availability": fp.get("availability", "COMING_SOON"),
            }
            for i, fp in enumerate(forward_pointers, 1)
        ],
        "llm_enhanced": llm_available,
    }
    
    # Add enhancement notice if not LLM enhanced
    if not llm_available:
        output["enhancement_notice"] = get_enhancement_notice()
    
    # Add historical comparison if available
    if historical_context:
        output["historical_comparison"] = historical_context
    
    return output


def _generate_high_intent_reflection(
    hi_profile: Dict[str, Any],
    phase1: Dict[str, Any],
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """Generate High-Intent reflection with sample-specific content."""
    
    if not hi_profile or hi_profile.get("total_high_intent_events", 0) == 0:
        return (
            "This sample contains no explicit stance-marking words—no 'perhaps,' 'definitely,' 'believe,' or similar markers. Your sentences proceed without signaling certainty or doubt, letting content carry the interpretive weight. This directness can feel confident or neutral, depending on context.",
            "MINIMAL",
            [],
        )
    
    total = hi_profile.get("total_high_intent_events", 0)
    openness = hi_profile.get("epistemic_openness", 0.5)
    coverage = hi_profile.get("coverage_rate", 0)
    markers = hi_profile.get("unique_markers", [])
    category_dist = hi_profile.get("category_distribution", {})
    dominant = hi_profile.get("dominant_category", "")
    
    # Determine stance
    if coverage < 0.2:
        stance = "MINIMAL"
    elif openness < 0.35:
        stance = "CLOSED"
    elif openness > 0.65:
        stance = "OPEN"
    else:
        stance = "BALANCED"
    
    # Build marker examples
    marker_examples = ", ".join(f'"{m}"' for m in markers[:4])
    
    # Generate stance-specific overview
    sentences_with_markers = int(coverage * phase1.get("outputs", {}).get("sentence_count", {}).get("count", 1))
    
    if stance == "OPEN":
        overview = f"""Your writing shows an open epistemic stance, with {total} stance markers including {marker_examples} appearing across {sentences_with_markers} sentence(s). These words leave room for interpretation—they qualify rather than assert, creating space for the reader to think alongside you.

The dominant category is {dominant.upper() if dominant else 'mixed'}, suggesting you foreground {
    'possibility and contingency' if dominant == 'POSSIBILITY' else
    'your own perspective and belief' if dominant == 'BELIEF' else
    'evidence and appearance' if dominant == 'EVIDENCE' else
    'a mix of epistemic moves'
}. In Peircean terms, these markers keep interpretants in motion—meaning doesn't settle but remains available for development."""

    elif stance == "CLOSED":
        overview = f"""Your writing shows a firm epistemic stance, with {total} stance markers including {marker_examples} appearing across {sentences_with_markers} sentence(s). These words signal confidence and commitment—they close down alternatives rather than opening them.

The dominant category is {dominant.upper() if dominant else 'mixed'}, suggesting you foreground {
    'certainty and necessity' if dominant == 'CERTAINTY' else
    'emphasis and importance' if dominant == 'EMPHASIS' else
    'a clear position'
}. In Peircean terms, these markers stabilize interpretants—meaning settles into definite forms, guiding readers toward specific conclusions."""

    elif stance == "BALANCED":
        overview = f"""Your writing balances openness and certainty, with {total} stance markers including {marker_examples}. Some moments assert firmly; others leave room for interpretation. This texture—mixing commitment with qualification—creates a dialogue between what's claimed and what's proposed.

The markers distribute across categories, with {dominant.upper() if dominant else 'mixed'} appearing most often. In Peircean terms, interpretants both stabilize and remain in motion—the reader encounters moments of clarity and moments of invitation."""

    else:  # MINIMAL with some markers
        overview = f"""Your writing uses stance markers sparingly—just {total} instances ({marker_examples}) across the sample. Most sentences proceed without explicit epistemic signaling, letting content carry meaning without the writer's stance foregrounded.

This restraint creates directness. Readers must infer your certainty or doubt from context rather than from explicit markers. Whether this feels confident or ambiguous depends on the material."""

    # Build notable markers list with interpretations
    notable = []
    for marker in markers[:3]:
        # Find category for this marker
        category = ""
        for cat, count in category_dist.items():
            if count > 0:
                category = cat
                break
        
        interpretation_map = {
            "CERTAINTY": "Closes down interpretation, signaling commitment.",
            "POSSIBILITY": "Opens space for alternatives and contingency.",
            "BELIEF": "Anchors the claim to your subjective perspective.",
            "EVIDENCE": "Grounds the claim in observation or appearance.",
            "HEDGING": "Softens the claim, creating buffer room.",
            "CONDITIONALITY": "Makes the claim dependent on circumstances.",
            "CONTRAST": "Creates tension between what's said and what's implied.",
            "EMPHASIS": "Amplifies the claim's importance or certainty.",
        }
        
        notable.append({
            "word": marker,
            "category": category,
            "interpretation": interpretation_map.get(category, "Shapes how the claim is received."),
        })
    
    return overview.strip(), stance, notable


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with realistic mock data
    mock_sentences = [
        "The morning light definitely came through the window.",
        "She made coffee (black, no sugar) and sat down.",
        "Perhaps nothing would happen for a long time.",
        "I believe the phone might ring eventually.",
        "The silence stretched on...",
        "Then everything changed.",
    ]
    
    mock_phase1 = {
        "outputs": {
            "sentence_count": {"count": 6},
            "token_volume": {"total_tokens": 47, "mean_tokens_per_sentence": 7.8},
            "structural_variety": {"unique_signatures": 5, "variety_ratio": 0.83},
            "signature_concentration": {"top_signatures": [{"sig": "A", "count": 2}], "top_3_coverage": 0.33},
            "zero_event_presence": {"count": 1, "rate": 0.17},
            "operator_event_presence": {"count": 0, "rate": 0.0},
            "scope_event_presence": {"count": 1, "rate": 0.17},
            "structural_density": {"total_events": 2, "mean_events_per_sentence": 0.33},
        }
    }
    
    mock_phase2 = {"presentation_mode": "REFLECTIVE"}
    
    mock_phase3 = {
        "syntheses": [
            {"semiotic_lens": "INTERPRETANT_STABILIZATION", "synthesis_text": "..."},
            {"semiotic_lens": "MEDIATION_AND_BOUNDARY", "synthesis_text": "..."},
            {"semiotic_lens": "RELATIONAL_DENSITY", "synthesis_text": "..."},
        ]
    }
    
    mock_phase4 = {"prompt_sets": []}
    
    mock_hi_profile = {
        "total_high_intent_events": 5,
        "coverage_rate": 0.67,
        "epistemic_openness": 0.6,
        "stance_intensity": 0.2,
        "dominant_category": "POSSIBILITY",
        "unique_markers": ["definitely", "perhaps", "believe", "might"],
        "category_distribution": {"CERTAINTY": 1, "POSSIBILITY": 3, "BELIEF": 1},
    }
    
    print("Phase-6 Generator v0.2.0 Demo (Sample-Specific)")
    print("=" * 70)
    
    result = generate_phase6(
        mock_phase1,
        mock_phase2,
        mock_phase3,
        mock_phase4,
        "PROMPTING",
        mock_hi_profile,
        mock_sentences,
    )
    
    print(f"\nTitle: {result['summary']['title']}")
    print(f"\n--- Structural Overview ---")
    print(result['summary']['structural_overview'])
    print(f"\n--- Semiotic Synthesis ---")
    print(result['summary']['semiotic_synthesis'][:500] + "...")
    print(f"\n--- Paths Forward ---")
    pf = result['paths_forward']
    print(f"  Recommended: {pf['recommended_exercise']['title']}")
    print(f"  Rationale: {pf['recommended_exercise']['description']}")
    print(f"\n--- High-Intent ---")
    print(f"  Stance: {result['high_intent_reflection']['epistemic_stance']}")
    print(f"  Overview: {result['high_intent_reflection']['overview'][:200]}...")
