#!/usr/bin/env python3
"""
Phase-6 Summary Generator
Version: 0.3.0

Generates Phase-6 Summary output with MODE-AWARE, SAMPLE-SPECIFIC content.

CHANGELOG v0.3.0:
- Story Mode: Warm-Companion tone with narrative metaphors
- School Mode: Collaborative-Curious tone (unchanged from v0.2.0)
- Mode detection from session or default
- Story-specific reflections: structural → narrative translation

CHANGELOG v0.2.0:
- Deep interpolation: references actual metrics, patterns, and markers
- Historical awareness: can reference previous sessions
- Paths Forward: replaces mode_reflection with actionable next steps
- Exercise recommendation based on structural patterns
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from lncp_llm_expander import (
        expand_content,
        select_next_step,
        is_llm_available,
        get_enhancement_notice,
    )
except ImportError:
    def expand_content(t, c, e, l): return t, False
    def select_next_step(p, c): return p.get("next_steps", [{}])[0], False
    def is_llm_available(): return False
    def get_enhancement_notice(): return "Enhanced analysis available when connected to backend."


# =============================================================================
# Configuration
# =============================================================================

PHASE6_VERSION = "0.3.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.2.0"
SOURCE_PHASE3_VERSION = "0.2.0"

NEXT_STEP_POOL_PATH = Path(__file__).parent / "phase6-next-step-pool-v0.1.0.json"


def load_next_step_pool() -> Dict[str, Any]:
    """Load the next-step prompt pool."""
    try:
        with open(NEXT_STEP_POOL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"next_steps": []}


# =============================================================================
# Utility Functions
# =============================================================================

def _format_number(n: float, decimals: int = 1) -> str:
    """Format a number for display."""
    if decimals == 0:
        return str(int(n))
    return f"{n:.{decimals}f}"


def _get_metric(outputs: Dict, output_key: str, metric_key: str, default=0):
    """Helper to get nested metric from Phase-1 outputs."""
    output = outputs.get(output_key, {})
    metrics = output.get("metrics", output)
    return metrics.get(metric_key, default)


# =============================================================================
# Mode-Specific Tone Functions
# =============================================================================

def _story_mode_title(sentence_count: int, variety_ratio: float, epistemic_stance: str) -> str:
    """Generate a warm, evocative title for Story Mode."""
    # Size descriptor
    if sentence_count <= 3:
        size = "A Small Gathering"
    elif sentence_count <= 6:
        size = "A Quiet Collection"
    else:
        size = "A Full Page"
    
    # Character descriptor - warmer language
    if variety_ratio >= 0.8:
        character = "Each Finding Its Shape"
    elif variety_ratio <= 0.4:
        character = "Returning to Familiar Ground"
    elif epistemic_stance == "OPEN":
        character = "Left Open"
    elif epistemic_stance == "CLOSED":
        character = "Settled and Sure"
    else:
        character = "At Rest"
    
    return f"{size}: {character}"


def _school_mode_title(sentence_count: int, variety_ratio: float, epistemic_stance: str) -> str:
    """Generate a descriptive title for School Mode."""
    if sentence_count <= 3:
        size = "A Glimpse"
    elif sentence_count <= 6:
        size = "A Portrait"
    else:
        size = "A Study"
    
    if variety_ratio >= 0.8:
        character = "in Variety"
    elif variety_ratio <= 0.4:
        character = "in Rhythm"
    elif epistemic_stance == "OPEN":
        character = "in Question"
    elif epistemic_stance == "CLOSED":
        character = "in Conviction"
    else:
        character = "in Balance"
    
    return f"{size}: Your Structure {character}"


# =============================================================================
# Story Mode Content (Warm-Companion Tone)
# =============================================================================

def _story_structural_overview(
    phase1: Dict[str, Any],
    hi_profile: Dict[str, Any],
    sentences: List[str],
) -> str:
    """Generate structural overview with Warm-Companion tone."""
    outputs = phase1.get("outputs", {})
    
    # Extract metrics
    sentence_count = _get_metric(outputs, "sentence_count", "sentence_count", len(sentences))
    total_tokens = _get_metric(outputs, "token_volume", "total_token_count", 0)
    mean_tokens = _get_metric(outputs, "token_volume", "mean_tokens_per_sentence", 0)
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    zero_count = _get_metric(outputs, "zero_event_presence", "total_zero_event_count", 0)
    scope_count = _get_metric(outputs, "scope_event_presence", "total_scope_event_count", 0)
    
    # Warm framing for size
    if sentence_count <= 3:
        size_feel = f"{sentence_count} sentences, {total_tokens} words. A small offering—enough to see something, not enough to be sure what it means."
    elif sentence_count <= 6:
        size_feel = f"{sentence_count} sentences, {total_tokens} words. They move at a comfortable pace—unhurried, like thoughts arriving one at a time."
    else:
        size_feel = f"{sentence_count} sentences, {total_tokens} words. There's room here to settle in, to notice what recurs and what surprises."
    
    # Rhythm observation with narrative metaphor
    if mean_tokens < 8:
        rhythm_feel = "The sentences are short—quick breaths, each one landing before the next begins."
    elif mean_tokens < 12:
        rhythm_feel = "The sentences find a middle ground—not rushed, not lingering. Room to think, but not too much."
    else:
        rhythm_feel = "These are longer sentences, ones that take their time. There's space inside them for clauses, asides, second thoughts."
    
    # Variety observation
    if variety_ratio >= 0.8:
        variety_feel = "Each sentence finds its own shape. No two quite alike—like different ways of saying something true."
    elif variety_ratio >= 0.5:
        variety_feel = "Some shapes recur, others appear just once. A rhythm is forming, but it's not rigid."
    else:
        variety_feel = "The sentences return to familiar shapes. There's comfort in that—a voice finding its natural form."
    
    # Boundary markers with warm observation
    if zero_count == 0 and scope_count == 0:
        boundary_feel = "The writing flows without interruption—no pauses, no asides, just straight through."
    elif scope_count > 0 and zero_count == 0:
        scope_word = "aside" if scope_count == 1 else "asides"
        boundary_feel = f"There's {scope_count} parenthetical {scope_word}—a thought tucked inside another thought. Something that wanted to be said but not quite in the main line."
    elif zero_count > 0 and scope_count == 0:
        boundary_feel = "Pauses appear—places where the writing holds its breath."
    else:
        boundary_feel = "Both pauses and asides appear. The writing makes room for hesitation and addition."
    
    # High-Intent observation (warm)
    total_hi = hi_profile.get("total_high_intent_events", 0) if hi_profile else 0
    if total_hi > 0:
        markers = hi_profile.get("unique_markers", [])[:3]
        if markers:
            marker_list = ", ".join(f'"{m}"' for m in markers)
            stance_feel = f"\n\nWords like {marker_list} appear—they soften things, or firm them up. They're signals of how sure you are, how open you're leaving things."
        else:
            stance_feel = ""
    else:
        stance_feel = ""
    
    return f"""{size_feel}

{rhythm_feel}

{variety_feel}

{boundary_feel}{stance_feel}"""


def _story_semiotic_synthesis(
    phase1: Dict[str, Any],
    phase3: Dict[str, Any],
    sentences: List[str],
) -> str:
    """Generate semiotic synthesis with narrative metaphors."""
    outputs = phase1.get("outputs", {})
    
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    zero_count = _get_metric(outputs, "zero_event_presence", "total_zero_event_count", 0)
    scope_count = _get_metric(outputs, "scope_event_presence", "total_scope_event_count", 0)
    density = _get_metric(outputs, "structural_density", "structural_density", 0)
    
    # Interpretant stabilization - narrative framing
    if variety_ratio >= 0.8:
        stab = "Each sentence arrives as itself. There's no pattern yet for a reader to lean on—each one asks to be met fresh. Like a conversation that keeps changing direction."
    elif variety_ratio >= 0.5:
        stab = "Some shapes return, others don't. A reader starts to develop expectations but can't quite settle in. Like a song with a verse that varies each time."
    else:
        stab = "The sentences find familiar shapes. A reader knows what to expect—there's comfort in that, a voice that sounds like itself. Like a friend whose cadence you recognize."
    
    # Mediation - narrative framing
    if zero_count == 0 and scope_count == 0:
        med = "The meaning moves directly from beginning to end. No detours, no whispered asides. What's said is said."
    elif scope_count > 0:
        med = "Parentheses create pockets—spaces where something extra lives, subordinate but present. Like the things we say under our breath, meant to be heard but not emphasized."
    elif zero_count > 0:
        med = "Pauses interrupt the flow. Places where meaning hesitates, or where the unsaid makes space for itself."
    else:
        med = "Both pauses and asides appear—the writing has texture, layers, places where readers slow down or lean in."
    
    # Density - narrative framing
    if density < 0.3:
        dens = "The writing is lean. Sentences carry their content without much structural weight—clean, direct, unadorned."
    elif density < 0.8:
        dens = "There's moderate density—some sentences carry structural features, others move cleanly through. Variety in texture."
    else:
        dens = "The writing is dense, textured. Multiple structural features share space within sentences. Readers navigate form as well as meaning."
    
    return f"""Three ways of seeing what's here:

**How Patterns Form**: {stab}

**Where Meaning Pauses**: {med}

**How Dense It Feels**: {dens}"""


def _story_high_intent_reflection(hi_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate High-Intent reflection with Warm-Companion tone."""
    if not hi_profile:
        return {
            "present": False,
            "overview": "The writing proceeds without many stance markers—no 'perhaps' or 'definitely' signaling how sure you are. The words just say what they say.",
            "epistemic_stance": "MINIMAL",
            "notable_markers": [],
        }
    
    total = hi_profile.get("total_high_intent_events", 0)
    openness = hi_profile.get("epistemic_openness", 0.5)
    markers = hi_profile.get("unique_markers", [])
    dominant = hi_profile.get("dominant_category", "")
    
    # Determine stance
    if total == 0:
        stance = "MINIMAL"
    elif openness >= 0.6:
        stance = "OPEN"
    elif openness <= 0.4:
        stance = "CLOSED"
    else:
        stance = "BALANCED"
    
    # Warm overview based on stance
    if stance == "OPEN":
        overview = """The writing holds things lightly. Words like "perhaps" and "might" leave doors open—there's room for things to be otherwise.

This isn't hedging. It's a way of saying: here's what seems true, but come see for yourself."""
    elif stance == "CLOSED":
        overview = """The writing lands with confidence. Words like "definitely" and "must" close down alternatives—they say: this is how it is.

There's power in that. Readers know where you stand."""
    elif stance == "BALANCED":
        overview = """Some things are held firmly, others left open. The writing moves between certainty and tentativeness—some claims proposed, others asserted.

This creates texture. Readers can feel which parts are settled and which are still finding their shape."""
    else:
        overview = """The writing proceeds without much explicit signaling about certainty or doubt. The words just carry their meaning, without framing.

This has its own effect—it lets content speak without commentary on how sure you are."""
    
    # Format notable markers with warm interpretation
    notable = []
    category_interpretations = {
        "POSSIBILITY": "softens the claim, leaves room",
        "CERTAINTY": "firms things up, closes down alternatives",
        "BELIEF": "anchors it to personal perspective",
        "EVIDENCE": "points to something outside the claim itself",
        "INFERENCE": "shows the thinking behind it",
        "NECESSITY": "says it has to be this way",
        "TEMPORAL": "places it in time, maybe past certainty",
        "CONTRAST": "sets up what it isn't, before what it is",
    }
    
    for marker in markers[:5]:
        cat = ""
        for c, dist in hi_profile.get("category_distribution", {}).items():
            if marker.lower() in [m.lower() for m in hi_profile.get("unique_markers", [])]:
                cat = c
                break
        
        interp = category_interpretations.get(cat, "signals something about your relationship to the claim")
        notable.append({
            "word": marker,
            "category": cat or "STANCE",
            "interpretation": f'"{marker}" {interp}.',
        })
    
    return {
        "present": total > 0,
        "overview": overview,
        "epistemic_stance": stance,
        "notable_markers": notable,
    }


# =============================================================================
# School Mode Content (Collaborative-Curious Tone - from v0.2.0)
# =============================================================================

def _school_structural_overview(
    phase1: Dict[str, Any],
    phase2: Dict[str, Any],
    hi_profile: Dict[str, Any],
    sentences: List[str],
) -> str:
    """Generate structural overview with Collaborative-Curious tone."""
    outputs = phase1.get("outputs", {})
    mode = phase2.get("presentation_mode", "DESCRIPTIVE")
    
    sentence_count = _get_metric(outputs, "sentence_count", "sentence_count", len(sentences))
    total_tokens = _get_metric(outputs, "token_volume", "total_token_count", 0)
    mean_tokens = _get_metric(outputs, "token_volume", "mean_tokens_per_sentence", 0)
    unique_sigs = _get_metric(outputs, "structural_variety", "unique_signature_count", 0)
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    total_events = _get_metric(outputs, "structural_density", "total_structural_events", 0)
    
    event_desc = _get_event_description(phase1)
    pattern_desc = _get_dominant_pattern_description(phase1)
    hi_desc = _get_high_intent_summary(hi_profile)
    
    if mode == "DESCRIPTIVE":
        overview = f"""Your sample contains {sentence_count} sentences totaling {total_tokens} words, averaging {_format_number(mean_tokens)} words per sentence.

Structurally, we find {event_desc}. Your sentences show {unique_sigs} unique structural shapes out of {sentence_count} (variety ratio: {_format_number(variety_ratio, 2)}), meaning {pattern_desc}.

{hi_desc}These patterns likely describe this particular moment of writing—more material would reveal whether they persist."""
    else:
        overview = f"""Your sample contains {sentence_count} sentences totaling {total_tokens} words, averaging {_format_number(mean_tokens)} words per sentence.

Together, we find {event_desc}. With {unique_sigs} unique shapes and a variety ratio of {_format_number(variety_ratio, 2)}, {pattern_desc}.

{hi_desc}These patterns reflect something genuine about how you build sentences, though context always matters."""
    
    return overview


def _school_semiotic_synthesis(
    phase1: Dict[str, Any],
    phase3: Dict[str, Any],
    sentences: List[str],
) -> str:
    """Generate semiotic synthesis with Collaborative-Curious tone."""
    outputs = phase1.get("outputs", {})
    
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    zero_count = _get_metric(outputs, "zero_event_presence", "total_zero_event_count", 0)
    scope_count = _get_metric(outputs, "scope_event_presence", "total_scope_event_count", 0)
    density = _get_metric(outputs, "structural_density", "structural_density", 0)
    
    if variety_ratio >= 0.9:
        stab_obs = "each sentence takes its own shape, resisting the repetition that would allow interpretants to stabilize"
    elif variety_ratio >= 0.6:
        stab_obs = "some shapes recur while others appear only once, creating partial stabilization"
    else:
        stab_obs = "recurring shapes dominate, generating stable interpretive patterns readers can anticipate"
    
    if zero_count == 0 and scope_count == 0:
        med_obs = "meaning passes through largely unmediated—no pauses or nested layers interrupt the flow"
    elif zero_count > 0 and scope_count > 0:
        med_obs = f"both pause markers ({zero_count}) and scope markers ({scope_count}) create a textured passage where meaning is shaped and layered"
    elif zero_count > 0:
        med_obs = f"pause markers ({zero_count}) create moments of suspension, but no nested scopes add layers"
    else:
        med_obs = f"scope markers ({scope_count}) create nested meaning, but no pauses interrupt the flow"
    
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


def _school_high_intent_reflection(hi_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Generate High-Intent reflection with Collaborative-Curious tone."""
    if not hi_profile:
        return {
            "present": False,
            "overview": "No stance markers detected in this sample.",
            "epistemic_stance": "MINIMAL",
            "notable_markers": [],
        }
    
    total = hi_profile.get("total_high_intent_events", 0)
    openness = hi_profile.get("epistemic_openness", 0.5)
    markers = hi_profile.get("unique_markers", [])
    dominant = hi_profile.get("dominant_category", "")
    
    if total == 0:
        stance = "MINIMAL"
    elif openness >= 0.6:
        stance = "OPEN"
    elif openness <= 0.4:
        stance = "CLOSED"
    else:
        stance = "BALANCED"
    
    # Generate overview based on stance
    if stance == "OPEN":
        overview = """Your writing shows an open epistemic stance—words like "perhaps," "might," and "could" leave room for interpretation. They qualify rather than assert, inviting readers to consider possibilities rather than accepting conclusions.

In Peircean terms, interpretants remain in motion. The writing proposes rather than pronounces."""
    elif stance == "CLOSED":
        overview = """Your writing shows a closed epistemic stance—words like "definitely," "must," and "clearly" signal confidence and commitment. They close down alternatives, asking readers to accept rather than question.

In Peircean terms, interpretants stabilize quickly. The writing pronounces rather than proposes."""
    elif stance == "BALANCED":
        overview = """Your writing shows a balanced epistemic stance—mixing commitment with qualification. Some claims are asserted, others proposed. This creates texture where readers navigate between what you're sure of and what you're exploring.

In Peircean terms, interpretants both stabilize and remain in motion."""
    else:
        overview = """Your writing proceeds without explicit epistemic signaling. No "perhaps" or "definitely" marks your relationship to the claims. The content speaks without framing.

In Peircean terms, interpretants form based on content alone, without stance markers guiding their formation."""
    
    notable = []
    for marker in markers[:5]:
        notable.append({
            "word": marker,
            "category": dominant or "STANCE",
            "interpretation": f"Signals {dominant.lower() if dominant else 'stance'} in the claim.",
        })
    
    return {
        "present": total > 0,
        "overview": overview,
        "epistemic_stance": stance,
        "notable_markers": notable,
    }


# =============================================================================
# Helper Functions (shared)
# =============================================================================

def _get_event_description(phase1: Dict[str, Any]) -> str:
    """Generate a description of structural events found."""
    outputs = phase1.get("outputs", {})
    
    zero_count = _get_metric(outputs, "zero_event_presence", "total_zero_event_count", 0)
    op_count = _get_metric(outputs, "operator_event_presence", "total_operator_event_count", 0)
    scope_count = _get_metric(outputs, "scope_event_presence", "total_scope_event_count", 0)
    
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
    
    if not top_sigs:
        return "no dominant pattern—each sentence takes a unique shape"
    
    top = top_sigs[0]
    count = top.get("count", 0)
    
    if count == 1:
        return "no pattern repeats—all structures are unique"
    elif count == 2:
        return "one pattern appears twice, suggesting an emerging habit"
    else:
        return f"one pattern appears {count} times, a clear structural preference"


def _get_high_intent_summary(hi_profile: Dict[str, Any]) -> str:
    """Generate a brief summary of high-intent markers."""
    if not hi_profile:
        return ""
    
    total = hi_profile.get("total_high_intent_events", 0)
    if total == 0:
        return ""
    
    markers = hi_profile.get("unique_markers", [])
    dominant = hi_profile.get("dominant_category", "")
    
    unique = list(dict.fromkeys(markers))
    marker_examples = ", ".join(f'"{m}"' for m in unique[:3])
    
    if total == 1:
        return f"The epistemic layer shows one stance marker ({marker_examples}). "
    else:
        cat_text = f", mostly {dominant.lower()}" if dominant else ""
        return f"The epistemic layer shows {total} stance markers including {marker_examples}{cat_text}. "


# =============================================================================
# Paths Forward (shared, with mode-aware language)
# =============================================================================

def generate_paths_forward(
    phase1: Dict[str, Any],
    phase4a: Dict[str, Any],
    phase4b: Dict[str, Any],
    hi_profile: Dict[str, Any],
    mode: str = "STORY",
) -> Dict[str, Any]:
    """Generate Paths Forward with mode-aware language."""
    outputs = phase1.get("outputs", {})
    
    sentence_count = _get_metric(outputs, "sentence_count", "sentence_count", 0)
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    zero_count = _get_metric(outputs, "zero_event_presence", "total_zero_event_count", 0)
    scope_count = _get_metric(outputs, "scope_event_presence", "total_scope_event_count", 0)
    density = _get_metric(outputs, "structural_density", "structural_density", 0)
    
    epistemic_openness = hi_profile.get("epistemic_openness", 0.5) if hi_profile else 0.5
    
    # Determine recommended exercise based on patterns
    if sentence_count < 5:
        if mode == "STORY":
            exercise = {
                "type": "EXPAND",
                "prompt": "Take one of your sentences and let it unfold into three. Same idea, more room to breathe.",
                "source": "VOLUME",
            }
            rationale = f"With {sentence_count} sentences, there's not quite enough to see what persists. A few more would help."
            lens = "Building Volume"
        else:
            exercise = {
                "type": "REWRITE",
                "prompt": "Choose one sentence and expand it into three, keeping the core idea but adding detail and qualification.",
                "source": "INTERPRETANT_STABILIZATION",
            }
            rationale = f"With only {sentence_count} sentences, expanding your sample would reveal whether your patterns persist."
            lens = "Building Volume"
    elif variety_ratio < 0.5:
        if mode == "STORY":
            exercise = {
                "type": "VARY",
                "prompt": "Find your most common sentence shape and write the same thought in a completely different structure. Short if it was long. Long if it was short.",
                "source": "VARIETY",
            }
            rationale = "The sentences keep returning to similar shapes. What happens when you deliberately break the pattern?"
            lens = "Finding New Shapes"
        else:
            exercise = {
                "type": "REWRITE",
                "prompt": "Rewrite your most-repeated structural pattern in three different ways: shorter, longer with embedded clause, and with a parenthetical aside.",
                "source": "INTERPRETANT_STABILIZATION",
            }
            rationale = f"Your variety ratio of {_format_number(variety_ratio, 2)} suggests structural habits—this exercise expands your range."
            lens = "Structural Variety"
    elif zero_count == 0 and scope_count == 0:
        if mode == "STORY":
            exercise = {
                "type": "ADD",
                "prompt": "Take one of your sentences and add a pause—a dash, an ellipsis—or a parenthetical aside. Something that interrupts the flow.",
                "source": "BOUNDARY",
            }
            rationale = "Your sentences move without interruption. Sometimes a pause lets things land differently."
            lens = "Adding Space"
        else:
            exercise = {
                "type": "PRACTICE",
                "prompt": "Take one sentence and add both a pause marker (ellipsis or dash) and a parenthetical aside. Notice how the reading experience changes.",
                "source": "MEDIATION_AND_BOUNDARY",
            }
            rationale = "Your sentences flow without boundary markers—this exercise explores what mediation adds."
            lens = "Adding Boundaries"
    elif density > 1.5:
        if mode == "STORY":
            exercise = {
                "type": "SIMPLIFY",
                "prompt": "Find your densest sentence and strip something out. One less aside, one fewer pause. What's left?",
                "source": "DENSITY",
            }
            rationale = "The sentences carry a lot of structural weight. Sometimes simpler hits harder."
            lens = "Making Space"
        else:
            exercise = {
                "type": "REWRITE",
                "prompt": "Find your densest sentence and rewrite it three ways: removing one structural feature at a time. Notice what each removal costs and what it gains.",
                "source": "RELATIONAL_DENSITY",
            }
            rationale = f"With {_format_number(density, 1)} structural events per sentence, this exercise explores simplification."
            lens = "Reducing Density"
    elif epistemic_openness < 0.35:
        if mode == "STORY":
            exercise = {
                "type": "SOFTEN",
                "prompt": "Find your most certain statement and soften it. Add a 'perhaps' or 'might.' How does the meaning shift?",
                "source": "STANCE",
            }
            rationale = "The writing lands with confidence. What happens when you leave a door open?"
            lens = "Leaving Room"
        else:
            exercise = {
                "type": "REFLECT",
                "prompt": "Rewrite one of your most certain statements using tentative language: 'might,' 'perhaps,' 'could.' How does the meaning shift?",
                "source": "HIGH_INTENT",
            }
            rationale = "Your writing shows firm epistemic stance—this exercise explores tentativeness."
            lens = "Epistemic Range"
    elif epistemic_openness > 0.65:
        if mode == "STORY":
            exercise = {
                "type": "FIRM",
                "prompt": "Find your most tentative statement and commit to it. Remove the 'maybe.' Say it like you mean it.",
                "source": "STANCE",
            }
            rationale = "The writing stays open, provisional. What happens when you plant a flag?"
            lens = "Taking a Stand"
        else:
            exercise = {
                "type": "REFLECT",
                "prompt": "Rewrite one of your most tentative statements with certainty: 'definitely,' 'must,' 'clearly.' How does the meaning shift?",
                "source": "HIGH_INTENT",
            }
            rationale = "Your writing leaves room for interpretation—this exercise explores commitment."
            lens = "Epistemic Range"
    else:
        if mode == "STORY":
            exercise = {
                "type": "EXPLORE",
                "prompt": "Write the same thought twice—once formally, once casually. Notice what changes besides the words.",
                "source": "REGISTER",
            }
            rationale = "Sometimes the same idea wears different clothes. The structure changes with the register."
            lens = "Register Play"
        else:
            exercise = {
                "type": "COMPARE",
                "prompt": "Write the same idea in two registers: one formal and one casual. Compare the structural differences that emerge.",
                "source": "EXPLORATION",
            }
            rationale = "Your patterns are balanced—this exercise explores how register shapes structure."
            lens = "Register Exploration"
    
    # Mode-aware descriptions
    if mode == "STORY":
        return {
            "next_sample": {
                "title": "Write Something New",
                "description": "Start fresh. See if the same shapes appear, or if new ones do.",
                "action": "new_session",
            },
            "recommended_exercise": {
                "title": f"Try This: {lens}",
                "description": rationale,
                "exercise": exercise,
                "action": "do_exercise",
            },
            "school_mode": {
                "title": "Switch to School Mode",
                "description": "More structured lessons about specific structural features.",
                "action": "school_mode",
            },
        }
    else:
        return {
            "next_sample": {
                "title": "Write Another Sample",
                "description": "Start a new writing session to see how your patterns compare across different pieces.",
                "action": "new_session",
            },
            "recommended_exercise": {
                "title": f"Exercise: {lens}",
                "description": rationale,
                "exercise": exercise,
                "action": "do_exercise",
            },
            "school_mode": {
                "title": "Continue in School Mode",
                "description": "Structured lessons that build your structural awareness step by step.",
                "action": "school_mode",
            },
        }


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase6(
    phase1: Dict[str, Any],
    phase2: Dict[str, Any],
    phase3: Dict[str, Any],
    phase4a: Dict[str, Any],
    phase4b: Dict[str, Any],
    hi_profile: Dict[str, Any],
    sentences: List[str],
    mode: str = "STORY",
) -> Dict[str, Any]:
    """
    Generate Phase-6 summary output with mode-aware tone.
    
    Args:
        phase1-phase4b: Outputs from previous phases
        hi_profile: High-Intent profile from parser
        sentences: Original sentences for reference
        mode: "STORY" or "SCHOOL"
    
    Returns:
        Phase-6 output with summary, paths forward, and high-intent reflection
    """
    outputs = phase1.get("outputs", {})
    phase4_mode = "PROMPTING"  # Default
    
    # Extract key metrics for title
    sentence_count = _get_metric(outputs, "sentence_count", "sentence_count", len(sentences))
    variety_ratio = _get_metric(outputs, "structural_variety", "signature_variety_ratio", 0)
    
    # Determine epistemic stance
    if hi_profile:
        openness = hi_profile.get("epistemic_openness", 0.5)
        total_hi = hi_profile.get("total_high_intent_events", 0)
        if total_hi == 0:
            stance = "MINIMAL"
        elif openness >= 0.6:
            stance = "OPEN"
        elif openness <= 0.4:
            stance = "CLOSED"
        else:
            stance = "BALANCED"
    else:
        stance = "MINIMAL"
    
    # Generate mode-specific content
    if mode == "STORY":
        title = _story_mode_title(sentence_count, variety_ratio, stance)
        structural_overview = _story_structural_overview(phase1, hi_profile, sentences)
        semiotic_synthesis = _story_semiotic_synthesis(phase1, phase3, sentences)
        high_intent_reflection = _story_high_intent_reflection(hi_profile)
    else:
        title = _school_mode_title(sentence_count, variety_ratio, stance)
        structural_overview = _school_structural_overview(phase1, phase2, hi_profile, sentences)
        semiotic_synthesis = _school_semiotic_synthesis(phase1, phase3, sentences)
        high_intent_reflection = _school_high_intent_reflection(hi_profile)
    
    # Generate paths forward
    paths_forward = generate_paths_forward(phase1, phase4a, phase4b, hi_profile, mode)
    
    # Load and select next step
    try:
        pool = load_next_step_pool()
        next_step, _ = select_next_step(pool, {"mode": mode, "sentence_count": sentence_count})
    except Exception:
        next_step = {
            "prompt_id": "NS_001",
            "prompt_text": "What if you wrote a bit more?",
            "rationale": "More material reveals whether patterns persist.",
            "category": "VOLUME",
        }
    
    # Forward pointers
    forward_pointers = [
        {
            "pointer_id": "FP_001",
            "title": "Extended Analysis",
            "description": "Write a full page and see deeper patterns emerge.",
            "availability": "COMING_SOON",
        },
        {
            "pointer_id": "FP_002",
            "title": "Compare Two Samples",
            "description": "See how different pieces reveal different patterns.",
            "availability": "COMING_SOON",
        },
        {
            "pointer_id": "FP_003",
            "title": "Track Over Time",
            "description": "Watch how your patterns evolve across sessions.",
            "availability": "COMING_SOON",
        },
    ]
    
    return {
        "phase6_version": PHASE6_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase4_mode": phase4_mode,
        "synthesis_scope": "SAMPLE_SPECIFIC",
        "interpretive_frame": "STRUCTURAL_SEMIOTIC",
        "mode": mode,
        "summary": {
            "title": title,
            "structural_overview": structural_overview,
            "semiotic_synthesis": semiotic_synthesis,
        },
        "paths_forward": paths_forward,
        "high_intent_reflection": high_intent_reflection,
        "next_step": next_step,
        "forward_pointers": forward_pointers,
        "llm_enhanced": is_llm_available(),
        "enhancement_notice": get_enhancement_notice() if not is_llm_available() else None,
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with sample data
    mock_sentences = [
        "The light came through the window.",
        "She sat down (quietly, carefully) and waited.",
        "Perhaps nothing would happen.",
        "The phone might ring eventually.",
    ]
    
    mock_phase1 = {
        "outputs": {
            "sentence_count": {"metrics": {"sentence_count": 4}},
            "token_volume": {"metrics": {"total_token_count": 28, "mean_tokens_per_sentence": 7.0}},
            "structural_variety": {"metrics": {"unique_signature_count": 4, "signature_variety_ratio": 1.0}},
            "structural_density": {"metrics": {"total_structural_events": 1, "structural_density": 0.25}},
            "zero_event_presence": {"metrics": {"total_zero_event_count": 0}},
            "scope_event_presence": {"metrics": {"total_scope_event_count": 1}},
            "operator_event_presence": {"metrics": {"total_operator_event_count": 0}},
            "signature_concentration": {"metrics": {"top_signatures": []}},
        }
    }
    
    mock_hi_profile = {
        "total_high_intent_events": 3,
        "epistemic_openness": 0.7,
        "unique_markers": ["Perhaps", "might", "eventually"],
        "dominant_category": "POSSIBILITY",
        "category_distribution": {"POSSIBILITY": 2, "TEMPORAL": 1},
    }
    
    print("=" * 70)
    print("STORY MODE (Warm-Companion Tone)")
    print("=" * 70)
    result_story = generate_phase6(
        mock_phase1, {}, {}, {}, {}, mock_hi_profile, mock_sentences, mode="STORY"
    )
    print(f"\nTitle: {result_story['summary']['title']}")
    print(f"\nStructural Overview:\n{result_story['summary']['structural_overview'][:500]}...")
    print(f"\nEpistemic Stance: {result_story['high_intent_reflection']['epistemic_stance']}")
    
    print("\n" + "=" * 70)
    print("SCHOOL MODE (Collaborative-Curious Tone)")
    print("=" * 70)
    result_school = generate_phase6(
        mock_phase1, {}, {}, {}, {}, mock_hi_profile, mock_sentences, mode="SCHOOL"
    )
    print(f"\nTitle: {result_school['summary']['title']}")
    print(f"\nStructural Overview:\n{result_school['summary']['structural_overview'][:500]}...")
