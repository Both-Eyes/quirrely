#!/usr/bin/env python3
"""
Phase-6 Summary Generator
Version: 0.1.0

Generates Phase-6 Summary output from Phase-2, Phase-3, and Phase-4a/4b outputs.

Phase-6 is the culminating synthesis that:
1. Summarizes structural patterns (from Phase-2)
2. Weaves semiotic syntheses together (from Phase-3)
3. Reflects on the chosen mode (Phase-4a prompting or Phase-4b guidance)
4. Interprets High-Intent patterns
5. Suggests a next step from the prompt pool
6. Points to future exercises

Uses LLM expansion when available; falls back to templates with graceful degradation.
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

PHASE6_VERSION = "0.1.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.1.0"
SOURCE_PHASE3_VERSION = "0.1.0"

NEXT_STEP_POOL_PATH = Path(__file__).parent / "phase6-next-step-pool-v0.1.0.json"


def load_next_step_pool() -> Dict[str, Any]:
    """Load the next-step prompt pool."""
    with open(NEXT_STEP_POOL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# Template Content (used when LLM unavailable)
# =============================================================================

STRUCTURAL_OVERVIEW_TEMPLATES = {
    "DESCRIPTIVE": """
In this sample of {sentence_count} sentences, we observe the initial contours of your structural patterns. The writing contains {token_count} words total, averaging {avg_tokens:.1f} words per sentence. {variety_observation}

{density_observation}

{event_observation} These observations describe what appears in this specific sample. A longer piece of writing would reveal whether these patterns persist, evolve, or represent one moment in a broader range.
""",
    "REFLECTIVE": """
Your sample of {sentence_count} sentences provides enough material to see patterns beginning to stabilize. Across {token_count} words, your sentences average {avg_tokens:.1f} words each. {variety_observation}

{density_observation}

{event_observation} With this amount of material, we can begin to speak of tendencies rather than just observations. The patterns here may reflect deeper habits of composition—or they may shift with context and subject matter. Either possibility is worth noticing.
""",
}

SEMIOTIC_SYNTHESIS_TEMPLATE = """
Looking at your writing through three semiotic lenses reveals different aspects of how meaning forms and moves.

{interpretant_synthesis}

{mediation_synthesis}

{density_synthesis}

These three perspectives—stability, mediation, and density—work together. In your sample, they suggest {overall_character}. This is not a judgment but a description of how your structural choices shape the experience of reading.
"""

MODE_REFLECTION_TEMPLATES = {
    "PROMPTING": """
The reflection prompts generated for your writing invite you to notice, reflect, rewrite, and compare. They are not prescriptions but invitations—ways to become more conscious of the patterns you already use.

The prompts focus on {focus_areas}. Each one offers a different angle: noticing what's there, wondering what it does, trying a variation, and observing what changes. You might find that some prompts resonate more than others. That resonance itself is information.
""",
    "GUIDANCE": """
The guidance items generated for your writing offer practical lenses for thinking about how these patterns might function in different contexts. They suggest scenarios, practice opportunities, and points of comparison.

The guidance touches on {focus_areas}. These are possibilities, not prescriptions. Your writing serves its purposes in ways that analysis can illuminate but not dictate. The goal is awareness, not correction.
""",
}

HIGH_INTENT_REFLECTION_TEMPLATES = {
    "OPEN": """
Your writing shows an open epistemic stance. Words like {example_markers} leave room for interpretation, qualifying claims rather than asserting them absolutely. This openness creates space for the reader to think alongside you rather than simply receive your conclusions.

In Peircean terms, these markers keep interpretants in motion—meaning doesn't settle into a single fixed form but remains available for further development. This can create a sense of intellectual humility, of thinking-in-progress. It can also, in some contexts, create uncertainty about where you actually stand.
""",
    "CLOSED": """
Your writing shows a firm epistemic stance. Words like {example_markers} signal confidence and commitment to claims. This firmness guides the reader toward specific interpretations, closing off alternatives.

In Peircean terms, these markers stabilize interpretants—meaning settles into definite forms. This can create clarity and conviction. It can also, in some contexts, leave less room for the reader's own thinking. Neither is better; each serves different purposes.
""",
    "BALANCED": """
Your writing balances openness and certainty. You use markers like {example_markers}, mixing firm claims with qualified ones. This balance creates a texture where some things are asserted and others are proposed.

In Peircean terms, interpretants both stabilize and remain in motion throughout your sample. The reader encounters moments of clarity and moments of invitation. This texture can make writing feel alive, responsive to the complexity of its subject.
""",
    "MINIMAL": """
Your writing uses few epistemic markers. The sample moves forward without much explicit signaling of certainty or doubt. This absence creates a particular effect: statements stand on their own terms, without the writer's stance foregrounded.

In Peircean terms, interpretants form without much explicit guidance from modal language. Readers must infer your stance from content and context rather than from explicit markers. This can create directness or ambiguity, depending on the material.
""",
}


# =============================================================================
# Template Generation Functions
# =============================================================================

def generate_structural_overview_template(
    phase1: Dict[str, Any],
    phase2: Dict[str, Any],
) -> str:
    """Generate structural overview from templates."""
    outputs = phase1.get("outputs", {})
    mode = phase2.get("presentation_mode", "DESCRIPTIVE")
    
    sentence_count = outputs.get("sentence_count", {}).get("count", 0)
    token_volume = outputs.get("token_volume", {})
    token_count = token_volume.get("total_tokens", 0)
    avg_tokens = token_volume.get("mean_tokens_per_sentence", 0)
    
    variety = outputs.get("structural_variety", {})
    unique_sigs = variety.get("unique_signatures", 0)
    variety_ratio = variety.get("variety_ratio", 0)
    
    if variety_ratio >= 0.8:
        variety_observation = "Each sentence has a distinct structural shape, suggesting variety in how you build sentences."
    elif variety_ratio >= 0.5:
        variety_observation = "There's a mix of structural shapes—some repetition, some variation."
    else:
        variety_observation = "Several sentences share structural shapes, suggesting recurring patterns in how you build sentences."
    
    density = outputs.get("structural_density", {})
    total_events = density.get("total_events", 0)
    mean_events = density.get("mean_events_per_sentence", 0)
    
    if mean_events < 0.3:
        density_observation = "Structurally, the writing is quite clean—few markers like parentheses, dashes, or ellipses appear."
    elif mean_events < 1.0:
        density_observation = "Some structural markers appear—parentheses, dashes, or other punctuation that creates layers in the prose."
    else:
        density_observation = "The writing has notable structural density, with markers that create layers, pauses, and nested meanings."
    
    zero_count = outputs.get("zero_event_presence", {}).get("count", 0)
    scope_count = outputs.get("scope_event_presence", {}).get("count", 0)
    
    event_parts = []
    if zero_count > 0:
        event_parts.append(f"{zero_count} pause marker(s) (ellipses, dashes)")
    if scope_count > 0:
        event_parts.append(f"{scope_count} scope marker(s) (parentheses, brackets, quotes)")
    
    if event_parts:
        event_observation = f"Specifically, we find {' and '.join(event_parts)}."
    else:
        event_observation = "No structural markers like ellipses, parentheses, or brackets appear in this sample."
    
    template = STRUCTURAL_OVERVIEW_TEMPLATES.get(mode, STRUCTURAL_OVERVIEW_TEMPLATES["DESCRIPTIVE"])
    
    return template.format(
        sentence_count=sentence_count,
        token_count=token_count,
        avg_tokens=avg_tokens,
        variety_observation=variety_observation,
        density_observation=density_observation,
        event_observation=event_observation,
    ).strip()


def generate_semiotic_synthesis_template(phase3: Dict[str, Any]) -> str:
    """Generate semiotic synthesis from templates."""
    syntheses = phase3.get("syntheses", [])
    
    lens_texts = {}
    for syn in syntheses:
        lens = syn.get("semiotic_lens", "")
        text = syn.get("synthesis_text", "")
        lens_texts[lens] = text
    
    interpretant = lens_texts.get("INTERPRETANT_STABILIZATION", "Patterns of meaning are beginning to form in this sample.")
    mediation = lens_texts.get("MEDIATION_AND_BOUNDARY", "Meaning flows through the sentences with its own texture of mediation.")
    density = lens_texts.get("RELATIONAL_DENSITY", "Structural features relate to each other in particular ways.")
    
    # Derive overall character
    if all(lens_texts):
        overall_character = "a writing voice with its own structural signature—not better or worse than others, but distinctly shaped"
    else:
        overall_character = "an initial structural character that would clarify with more material"
    
    return SEMIOTIC_SYNTHESIS_TEMPLATE.format(
        interpretant_synthesis=f"Through the lens of interpretant stabilization: {interpretant}",
        mediation_synthesis=f"Through the lens of mediation and boundary: {mediation}",
        density_synthesis=f"Through the lens of relational density: {density}",
        overall_character=overall_character,
    ).strip()


def generate_mode_reflection_template(
    phase4: Dict[str, Any],
    mode: str,
) -> str:
    """Generate mode-specific reflection from templates."""
    template = MODE_REFLECTION_TEMPLATES.get(mode, MODE_REFLECTION_TEMPLATES["PROMPTING"])
    
    # Extract focus areas from phase4 content
    if mode == "PROMPTING":
        prompt_sets = phase4.get("prompt_sets", [])
        lenses = [ps.get("semiotic_lens", "").replace("_", " ").lower() for ps in prompt_sets]
        focus_areas = ", ".join(lenses[:3]) if lenses else "structural patterns and their effects"
    else:
        guidance_sets = phase4.get("guidance_sets", [])
        lenses = [gs.get("semiotic_lens", "").replace("_", " ").lower() for gs in guidance_sets]
        focus_areas = ", ".join(lenses[:3]) if lenses else "structural patterns and their practical applications"
    
    return template.format(focus_areas=focus_areas).strip()


def generate_high_intent_reflection_template(
    high_intent_profile: Dict[str, Any],
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Generate High-Intent reflection from templates.
    
    Returns:
        (overview_text, epistemic_stance, notable_markers)
    """
    if not high_intent_profile or high_intent_profile.get("total_high_intent_events", 0) == 0:
        return (
            "This sample contains few or no explicit epistemic markers—words that signal certainty, possibility, belief, or evidence. The writing proceeds without much modal scaffolding, letting content carry the weight of stance.",
            "MINIMAL",
            [],
        )
    
    openness = high_intent_profile.get("epistemic_openness", 0.5)
    coverage = high_intent_profile.get("coverage_rate", 0)
    markers = high_intent_profile.get("unique_markers", [])
    category_dist = high_intent_profile.get("category_distribution", {})
    
    # Determine stance
    if coverage < 0.2:
        stance = "MINIMAL"
    elif openness < 0.35:
        stance = "CLOSED"
    elif openness > 0.65:
        stance = "OPEN"
    else:
        stance = "BALANCED"
    
    # Get example markers
    example_markers = ", ".join(f'"{m}"' for m in markers[:4]) if markers else '"perhaps," "certainly"'
    
    template = HIGH_INTENT_REFLECTION_TEMPLATES.get(stance, HIGH_INTENT_REFLECTION_TEMPLATES["BALANCED"])
    overview = template.format(example_markers=example_markers).strip()
    
    # Build notable markers list
    notable = []
    for marker in markers[:3]:
        # Find its category
        for cat, count in category_dist.items():
            if count > 0:
                notable.append({
                    "word": marker,
                    "category": cat,
                    "interpretation": f"This marker shapes how firmly the claim is held.",
                })
                break
    
    return overview, stance, notable


def generate_summary_title(
    phase2: Dict[str, Any],
    high_intent_profile: Dict[str, Any],
) -> str:
    """Generate an evocative title for the analysis."""
    mode = phase2.get("presentation_mode", "DESCRIPTIVE")
    stance = "MINIMAL"
    
    if high_intent_profile:
        openness = high_intent_profile.get("epistemic_openness", 0.5)
        if openness < 0.35:
            stance = "firm"
        elif openness > 0.65:
            stance = "open"
        else:
            stance = "balanced"
    
    titles = {
        ("DESCRIPTIVE", "firm"): "A First Glimpse: Structure with Conviction",
        ("DESCRIPTIVE", "open"): "A First Glimpse: Structure with Questions",
        ("DESCRIPTIVE", "balanced"): "A First Glimpse: Structure in Balance",
        ("DESCRIPTIVE", "MINIMAL"): "A First Glimpse: Structure Unadorned",
        ("REFLECTIVE", "firm"): "Patterns Emerging: Writing with Certainty",
        ("REFLECTIVE", "open"): "Patterns Emerging: Writing with Possibility",
        ("REFLECTIVE", "balanced"): "Patterns Emerging: Writing in Dialogue",
        ("REFLECTIVE", "MINIMAL"): "Patterns Emerging: Writing Directly",
    }
    
    return titles.get((mode, stance), "Your Structural Portrait")


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
) -> Dict[str, Any]:
    """
    Generate Phase-6 Summary output.
    
    Args:
        phase1: Phase-1 compute output
        phase2: Phase-2 UX output
        phase3: Phase-3 synthesis output
        phase4: Phase-4a or Phase-4b output
        phase4_mode: "PROMPTING" or "GUIDANCE"
        high_intent_profile: High-Intent profile from parser
        
    Returns:
        Phase-6 Summary output conforming to schema
    """
    llm_available = is_llm_available()
    
    # Build context for LLM expansion
    context = {
        "phase1": phase1,
        "phase2": phase2,
        "phase3": phase3,
        "phase4": phase4,
        "phase4_mode": phase4_mode,
        "high_intent_profile": high_intent_profile,
    }
    
    # Generate title
    title = generate_summary_title(phase2, high_intent_profile)
    
    # Generate structural overview
    structural_template = generate_structural_overview_template(phase1, phase2)
    structural_overview, _ = expand_content(
        structural_template,
        {"phase1": phase1, "phase2": phase2},
        "phase6_summary",
        "medium",
    )
    
    # Generate semiotic synthesis
    semiotic_template = generate_semiotic_synthesis_template(phase3)
    semiotic_synthesis, _ = expand_content(
        semiotic_template,
        {"phase3": phase3},
        "phase3_synthesis",
        "medium",
    )
    
    # Generate mode reflection
    mode_template = generate_mode_reflection_template(phase4, phase4_mode)
    mode_reflection, _ = expand_content(
        mode_template,
        {"phase4": phase4, "mode": phase4_mode},
        "phase6_summary",
        "short",
    )
    
    # Generate High-Intent reflection
    hi_template, hi_stance, hi_notable = generate_high_intent_reflection_template(high_intent_profile)
    hi_overview, _ = expand_content(
        hi_template,
        {"high_intent_profile": high_intent_profile},
        "high_intent_reflection",
        "medium",
    )
    
    # Select next step
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
        "synthesis_scope": "SAMPLE_ONLY",
        "interpretive_frame": "LNCP_PEIRCEAN",
        "summary": {
            "title": title,
            "structural_overview": structural_overview,
            "semiotic_synthesis": semiotic_synthesis,
            "mode_reflection": mode_reflection,
        },
        "high_intent_reflection": {
            "present": high_intent_profile.get("total_high_intent_events", 0) > 0,
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
    
    return output


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with mock data
    mock_phase1 = {
        "outputs": {
            "sentence_count": {"count": 6},
            "token_volume": {"total_tokens": 52, "mean_tokens_per_sentence": 8.7},
            "structural_variety": {"unique_signatures": 5, "variety_ratio": 0.83},
            "structural_density": {"total_events": 3, "mean_events_per_sentence": 0.5},
            "zero_event_presence": {"count": 1, "rate": 0.17},
            "scope_event_presence": {"count": 2, "rate": 0.33},
        }
    }
    
    mock_phase2 = {
        "presentation_mode": "DESCRIPTIVE",
        "outputs": {},
    }
    
    mock_phase3 = {
        "syntheses": [
            {"semiotic_lens": "INTERPRETANT_STABILIZATION", "synthesis_text": "Patterns are forming but not yet fixed."},
            {"semiotic_lens": "MEDIATION_AND_BOUNDARY", "synthesis_text": "Meaning flows without heavy mediation."},
            {"semiotic_lens": "RELATIONAL_DENSITY", "synthesis_text": "Structural events remain light."},
        ]
    }
    
    mock_phase4 = {
        "prompt_sets": [
            {"semiotic_lens": "INTERPRETANT_STABILIZATION", "prompts": []},
        ]
    }
    
    mock_hi_profile = {
        "total_high_intent_events": 5,
        "coverage_rate": 0.5,
        "epistemic_openness": 0.6,
        "unique_markers": ["perhaps", "might", "believe"],
        "category_distribution": {"POSSIBILITY": 2, "BELIEF": 2, "CERTAINTY": 1},
    }
    
    print("Phase-6 Generator Demo")
    print("=" * 60)
    
    result = generate_phase6(
        mock_phase1,
        mock_phase2,
        mock_phase3,
        mock_phase4,
        "PROMPTING",
        mock_hi_profile,
    )
    
    print(f"Title: {result['summary']['title']}")
    print(f"LLM Enhanced: {result['llm_enhanced']}")
    print(f"Epistemic Stance: {result['high_intent_reflection']['epistemic_stance']}")
    print(f"Next Step: {result['next_step']['prompt_text']}")
    print()
    print("Structural Overview (first 200 chars):")
    print(result['summary']['structural_overview'][:200] + "...")
