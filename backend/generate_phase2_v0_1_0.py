#!/usr/bin/env python3
"""
Phase-2 UX Presentation Generator
Version: 0.1.0

Generates Phase-2 UX output from Phase-1 compute output.
Uses template-based generation (no LLM required).

This is a deterministic generator that transforms Phase-1 metrics
into user-facing explanations and example insights.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


PHASE2_VERSION = "0.1.0"
SOURCE_CONTRACT_VERSION = "1.0.0"

# Output definitions with user-facing names and metric mappings
OUTPUT_DEFINITIONS = [
    {
        "output_id": "output_01",
        "name_user_facing": "How Much You Shared",
        "metric_key": "sentence_count",
        "secondary_key": "token_volume",
    },
    {
        "output_id": "output_02",
        "name_user_facing": "Word-Level Detail",
        "metric_key": "token_volume",
        "secondary_key": "sentence_count",
    },
    {
        "output_id": "output_03",
        "name_user_facing": "Structural Fingerprints",
        "metric_key": "structural_variety",
        "secondary_key": "sentence_count",
    },
    {
        "output_id": "output_04",
        "name_user_facing": "Your Most Common Patterns",
        "metric_key": "signature_concentration",
        "secondary_key": "structural_variety",
    },
    {
        "output_id": "output_05",
        "name_user_facing": "What's Left Unsaid",
        "metric_key": "zero_event_presence",
        "secondary_key": None,
    },
    {
        "output_id": "output_06",
        "name_user_facing": "Connective Moves",
        "metric_key": "operator_event_presence",
        "secondary_key": None,
    },
    {
        "output_id": "output_07",
        "name_user_facing": "Layered Meaning",
        "metric_key": "scope_event_presence",
        "secondary_key": None,
    },
    {
        "output_id": "output_08",
        "name_user_facing": "Complexity at a Glance",
        "metric_key": "structural_density",
        "secondary_key": None,
    },
    {
        "output_id": "output_09",
        "name_user_facing": "How Your Patterns Combine",
        "metric_key": "event_co_occurrence_profile",
        "secondary_key": None,
    },
    {
        "output_id": "output_10",
        "name_user_facing": "Your Structural Codes",
        "metric_key": "ticker_profile",
        "secondary_key": None,
    },
]


def _get_presentation_mode(sentence_count: int) -> str:
    """Determine presentation mode based on sentence count."""
    return "DESCRIPTIVE" if sentence_count < 4 else "REFLECTIVE"


def _generate_explanation_output_01(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 01: How Much You Shared."""
    count = metrics.get("sentence_count", {}).get("count", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 1:
            return "One sentence is present. With limited material, observations here describe what appears rather than broader patterns."
        else:
            return f"{count} sentences are present in this sample."
    else:
        if count < 5:
            return f"You've shared {count} sentences. Enough to see some shapes, though patterns are still forming."
        else:
            return f"You've shared {count} sentences. That's enough material for patterns to start emerging."


def _generate_explanation_output_02(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 02: Word-Level Detail."""
    token = metrics.get("token_volume", {})
    total = token.get("total_tokens", 0)
    avg = token.get("mean_tokens_per_sentence", 0)
    
    if mode == "DESCRIPTIVE":
        return f"{total} words appear across the sample. The average is {avg:.1f} words per sentence."
    else:
        if avg < 10:
            return f"Your sentences run lean—{avg:.1f} words on average across {total} total. Compact and direct."
        elif avg < 20:
            return f"Your sentences average {avg:.1f} words ({total} total). A comfortable middle ground."
        else:
            return f"Your sentences stretch out—{avg:.1f} words on average, {total} total. Room to breathe."


def _generate_explanation_output_03(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 03: Structural Fingerprints."""
    variety = metrics.get("structural_variety", {})
    unique = variety.get("unique_signatures", 0)
    ratio = variety.get("variety_ratio", 0)
    
    if mode == "DESCRIPTIVE":
        return f"{unique} unique structural shape(s) appear. The variety ratio is {ratio:.2f}."
    else:
        if ratio < 0.5:
            return f"You're working with {unique} structural shapes. Some repetition here—familiar moves."
        elif ratio < 1.0:
            return f"{unique} different structural fingerprints. A mix of familiar and fresh."
        else:
            return f"Every sentence has its own shape—{unique} unique structures, no repeats."


def _generate_explanation_output_04(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 04: Your Most Common Patterns."""
    conc = metrics.get("signature_concentration", {})
    top = conc.get("top_signatures", [])
    coverage = conc.get("top_3_coverage", 0)
    
    if mode == "DESCRIPTIVE":
        if len(top) == 0:
            return "No patterns to concentrate—structure is entirely varied."
        return f"The most common pattern appears {top[0].get('count', 0)} time(s). Top patterns cover {coverage:.0%} of sentences."
    else:
        if coverage > 0.8:
            return f"Your top patterns dominate—covering {coverage:.0%} of your writing. Strong consistency."
        elif coverage > 0.5:
            return f"Your top patterns account for {coverage:.0%}. A balance of habit and variation."
        else:
            return f"No single pattern dominates. Your structures are distributed across many shapes."


def _generate_explanation_output_05(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 05: What's Left Unsaid."""
    zero = metrics.get("zero_event_presence", {})
    count = zero.get("count", 0)
    rate = zero.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return "Zero events are absent from this sample. The rate is 0.0."
        return f"{count} zero event(s) appear. The rate is {rate:.2f}."
    else:
        if count == 0:
            return "No pause markers or ellipses. Your sentences move without hesitation."
        elif rate < 0.3:
            return f"A few pauses ({count} total)—moments where meaning trails off or waits."
        else:
            return f"Pauses and gaps appear often ({count} total). Space for what's unsaid."


def _generate_explanation_output_06(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 06: Connective Moves."""
    op = metrics.get("operator_event_presence", {})
    count = op.get("count", 0)
    rate = op.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return "Operators are absent from this sample. The count is zero."
        return f"{count} operator(s) appear. The rate is {rate:.2f}."
    else:
        if count == 0:
            return "No connective symbols like slashes or ampersands. Meaning flows without shortcuts."
        else:
            return f"{count} connective marks appear—shortcuts that link or divide meaning."


def _generate_explanation_output_07(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 07: Layered Meaning."""
    scope = metrics.get("scope_event_presence", {})
    count = scope.get("count", 0)
    rate = scope.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return "Scope markers are absent. No parentheses or brackets appear."
        return f"{count} scope marker(s) appear. The rate is {rate:.2f}."
    else:
        if count == 0:
            return "No nesting or bracketing. Your sentences stay on one level."
        else:
            return f"{count} scope markers create layers—asides, clarifications, nested thoughts."


def _generate_explanation_output_08(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 08: Complexity at a Glance."""
    density = metrics.get("structural_density", {})
    total = density.get("total_events", 0)
    avg = density.get("mean_events_per_sentence", 0)
    
    if mode == "DESCRIPTIVE":
        if total == 0:
            return "Structural events are absent. The density is 0.0."
        return f"{total} structural event(s) total. Average density is {avg:.2f} per sentence."
    else:
        if total == 0:
            return "Structurally quiet—no special markers. Clean and unadorned."
        elif avg < 1:
            return f"Light structural activity ({avg:.1f} events per sentence). Mostly straightforward."
        else:
            return f"Structurally active—{avg:.1f} events per sentence on average. Lots happening."


def _generate_explanation_output_09(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 09: How Your Patterns Combine."""
    profile = metrics.get("event_co_occurrence_profile", {})
    dist = profile.get("distribution", {})
    
    # Find most common combination
    if not dist:
        if mode == "DESCRIPTIVE":
            return "No event combinations to analyze in this sample."
        return "No events to combine—your sentences carry meaning without structural markers."
    
    dominant = max(dist.items(), key=lambda x: x[1])
    
    if mode == "DESCRIPTIVE":
        return f"The most common event combination is '{dominant[0]}' ({dominant[1]} sentence(s))."
    else:
        if dominant[0] == "none":
            return f"Most sentences ({dominant[1]}) have no structural events. Clean and direct."
        else:
            return f"Your sentences tend toward '{dominant[0]}' combinations ({dominant[1]} total)."


def _generate_explanation_output_10(metrics: Dict[str, Any], mode: str, status: str) -> str:
    """Generate explanation for Output 10: Your Structural Codes."""
    if status == "NOT_AVAILABLE":
        return "Ticker codes require more material to display meaningfully."
    
    ticker = metrics.get("ticker_profile", {})
    unique = ticker.get("unique_codes", 0)
    total = ticker.get("total_positions", 0)
    
    if mode == "DESCRIPTIVE":
        return f"{unique} distinct ticker code(s) appear across {total} word position(s)."
    else:
        return f"Your writing uses {unique} distinct structural codes across {total} positions."


def _generate_insights(output_id: str, metrics: Dict[str, Any], mode: str) -> List[str]:
    """Generate two example insights for an output."""
    # Template-based insights - kept simple and universal
    insights_templates = {
        "output_01": [
            ("DESCRIPTIVE", ["A single sentence is present in this sample.", "One sentence—observations will be descriptive, not interpretive."]),
            ("REFLECTIVE", ["The sample contains enough material to see patterns forming.", "More sentences would reveal whether these shapes persist."]),
        ],
        "output_02": [
            ("DESCRIPTIVE", ["The word count reflects what appears in the sample.", "Average sentence length is computed from available material."]),
            ("REFLECTIVE", ["Sentence length shapes how ideas land on the reader.", "Shorter sentences punch; longer ones unfold."]),
        ],
        "output_03": [
            ("DESCRIPTIVE", ["Structural variety is measured across the sample.", "The variety ratio compares unique shapes to total sentences."]),
            ("REFLECTIVE", ["Repeated structures create rhythm; varied ones create texture.", "Your structural fingerprint is as unique as your voice."]),
        ],
        "output_04": [
            ("DESCRIPTIVE", ["Pattern concentration shows how shapes distribute.", "Top patterns are ranked by frequency in the sample."]),
            ("REFLECTIVE", ["Dominant patterns reveal what comes naturally to you.", "Less common patterns might be where you stretch."]),
        ],
        "output_05": [
            ("DESCRIPTIVE", ["Zero events count pauses, ellipses, and gaps.", "The rate shows zero events relative to sentence count."]),
            ("REFLECTIVE", ["Pauses let meaning settle before moving on.", "What's left unsaid can speak as loud as words."]),
        ],
        "output_06": [
            ("DESCRIPTIVE", ["Operators include slashes, ampersands, and similar marks.", "The count reflects connective symbols in the sample."]),
            ("REFLECTIVE", ["Operators compress meaning—and/or, either/or, this/that.", "These shortcuts show how you link ideas."]),
        ],
        "output_07": [
            ("DESCRIPTIVE", ["Scope markers include parentheses, brackets, and quotes.", "The count reflects nesting depth in the sample."]),
            ("REFLECTIVE", ["Parentheses create asides—thoughts within thoughts.", "Layered meaning invites the reader to look closer."]),
        ],
        "output_08": [
            ("DESCRIPTIVE", ["Structural density sums all event types.", "The average shows events per sentence."]),
            ("REFLECTIVE", ["Dense sentences carry more structural weight.", "Sparse sentences let content speak for itself."]),
        ],
        "output_09": [
            ("DESCRIPTIVE", ["Co-occurrence tracks which event types appear together.", "Distribution shows how combinations spread across sentences."]),
            ("REFLECTIVE", ["Some combinations feel natural; others create tension.", "How you mix markers shapes your structural signature."]),
        ],
        "output_10": [
            ("DESCRIPTIVE", ["Ticker codes represent word-level structural positions.", "Unique codes show the variety of positions used."]),
            ("REFLECTIVE", ["Your codes form a kind of structural fingerprint.", "Patterns in codes reveal rhythms beneath the words."]),
        ],
    }
    
    templates = insights_templates.get(output_id, [])
    for m, insights in templates:
        if m == mode:
            return insights
    
    # Fallback
    return [
        "This metric reflects structural patterns in your writing.",
        "Patterns become clearer with more material."
    ]


def generate_phase2(phase1: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Phase-2 UX output from Phase-1 compute output.
    
    Args:
        phase1: Phase-1 compute output with 'outputs' containing metrics
        
    Returns:
        Phase-2 UX output JSON
    """
    metrics = phase1.get("outputs", {})
    
    # Determine presentation mode
    sentence_count = metrics.get("sentence_count", {}).get("count", 0)
    mode = _get_presentation_mode(sentence_count)
    
    # Determine Output 10 status
    ticker = metrics.get("ticker_profile", {})
    output_10_status = ticker.get("status", "AVAILABLE")
    if sentence_count < 2:
        output_10_status = "NOT_AVAILABLE"
    
    # Generate outputs
    outputs = {}
    
    explanation_generators = {
        "output_01": _generate_explanation_output_01,
        "output_02": _generate_explanation_output_02,
        "output_03": _generate_explanation_output_03,
        "output_04": _generate_explanation_output_04,
        "output_05": _generate_explanation_output_05,
        "output_06": _generate_explanation_output_06,
        "output_07": _generate_explanation_output_07,
        "output_08": _generate_explanation_output_08,
        "output_09": _generate_explanation_output_09,
    }
    
    for defn in OUTPUT_DEFINITIONS:
        output_id = defn["output_id"]
        
        if output_id == "output_10":
            explanation = _generate_explanation_output_10(metrics, mode, output_10_status)
            outputs[output_id] = {
                "output_id": output_id,
                "name_user_facing": defn["name_user_facing"],
                "explanation": explanation,
                "example_insights": _generate_insights(output_id, metrics, mode),
                "status": output_10_status,
            }
        else:
            gen_fn = explanation_generators.get(output_id)
            explanation = gen_fn(metrics, mode) if gen_fn else ""
            
            outputs[output_id] = {
                "output_id": output_id,
                "name_user_facing": defn["name_user_facing"],
                "explanation": explanation,
                "example_insights": _generate_insights(output_id, metrics, mode),
            }
    
    return {
        "phase2_version": PHASE2_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "presentation_mode": mode,
        "outputs": outputs,
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Phase-2 UX output from Phase-1")
    parser.add_argument("--phase1", required=True, help="Path to Phase-1 output JSON")
    parser.add_argument("--out", required=True, help="Path to write Phase-2 output JSON")
    args = parser.parse_args()
    
    with open(args.phase1, "r") as f:
        phase1 = json.load(f)
    
    phase2 = generate_phase2(phase1)
    
    with open(args.out, "w") as f:
        json.dump(phase2, f, indent=2)
    
    print(f"Phase-2 output written to {args.out}")
