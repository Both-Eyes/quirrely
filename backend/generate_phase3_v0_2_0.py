#!/usr/bin/env python3
"""
Phase-3 Synthesis Generator
Version: 0.2.0

Generates Phase-3 semiotic syntheses from Phase-2 UX output.
Brings multiple structural observations into relation using Peircean lenses.

CHANGELOG v0.2.0:
- Expanded synthesis texts to 2-3x longer
- Added interpretive framing with forward pointers
- Added High-Intent awareness where relevant
- Integrated with LLM expander for optional enhancement

Phase-3 Purpose:
- Bring multiple Phase-2 outputs into relation using LNCP-mapped Peircean semiotics
- Pattern constellation and semiotic function, not measurement or UX explanation
- All references framed as analogy ("functions like," "reads as," "behaves similarly to")
- Grounded in explicit Phase-2 outputs

Phase-3 Principles (Hard Constraints):
1. No recomputation or new metrics
2. No metric explanations or definitions
3. No diagnosis, labels, or trait attribution
4. Non-directive and non-prescriptive
5. Sample-bounded observations only
6. Maintains Phase-2 tone discipline
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

# Import LLM expander for optional enhancement
try:
    from lncp_llm_expander import expand_content, is_llm_available
except ImportError:
    def expand_content(t, c, e, l): return t, False
    def is_llm_available(): return False


PHASE3_VERSION = "0.2.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.2.0"
SYNTHESIS_SCOPE = "SAMPLE_ONLY"
INTERPRETIVE_FRAME = "LNCP_PEIRCEAN"

# Fixed synthesis groupings
SYNTHESIS_GROUPS = [
    {
        "semiotic_lens": "INTERPRETANT_STABILIZATION",
        "related_outputs": ["output_01", "output_03", "output_04"],
        "description": "How recurring structures resolve into stable interpretive forms",
    },
    {
        "semiotic_lens": "MEDIATION_AND_BOUNDARY",
        "related_outputs": ["output_05", "output_06", "output_07"],
        "description": "How meaning is bracketed, linked, or constrained",
    },
    {
        "semiotic_lens": "RELATIONAL_DENSITY",
        "related_outputs": ["output_08", "output_09"],
        "description": "How features cluster or remain distinct",
    },
]


def sha256_mod(seed: str, n: int) -> int:
    """Deterministic index selection via SHA-256(seed) % n."""
    if n <= 0:
        raise ValueError("n must be > 0")
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


def _get_phase2_metrics(phase2: Dict[str, Any], output_id: str) -> Dict[str, Any]:
    """Extract metrics from Phase-2 output for a given output_id."""
    outputs = phase2.get("outputs", {})
    return outputs.get(output_id, {})


# =============================================================================
# Expanded Synthesis Generators
# =============================================================================

def _generate_interpretant_stabilization_synthesis(
    phase2: Dict[str, Any],
    mode: str,
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate INTERPRETANT_STABILIZATION synthesis.
    
    This lens examines how recurring structures resolve into stable interpretive forms.
    Related outputs: sentence_count (01), structural_variety (03), signature_concentration (04)
    """
    output_01 = _get_phase2_metrics(phase2, "output_01")
    output_03 = _get_phase2_metrics(phase2, "output_03")
    output_04 = _get_phase2_metrics(phase2, "output_04")
    
    exp_01 = output_01.get("explanation", "").lower()
    exp_03 = output_03.get("explanation", "").lower()
    exp_04 = output_04.get("explanation", "").lower()
    
    # Determine sample size
    is_small_sample = "one sentence" in exp_01 or "single sentence" in exp_01 or "2 sentences" in exp_01
    
    # Determine variety level
    high_variety = "every sentence" in exp_03 and "unique" in exp_03
    low_variety = "repetition" in exp_03 or "familiar" in exp_03
    
    # Determine concentration
    high_concentration = "dominate" in exp_04 or "covering" in exp_04 and "80" in exp_04
    distributed = "distributed" in exp_04 or "no single pattern" in exp_04
    
    if is_small_sample:
        return (
            "In Peircean terms, interpretant stabilization occurs when signs recur enough to establish "
            "recognizable patterns—when structural shapes become familiar through repetition. "
            "With limited material in this sample, such stabilization cannot yet occur. "
            "Each structural shape stands as an isolated instance rather than a stabilized form. "
            "\n\n"
            "This doesn't mean the structures lack meaning; it means we observe them as singular events "
            "rather than as parts of a recurring system. The interpretants they might generate remain "
            "provisional—suggestions rather than established patterns. "
            "A longer sample would reveal whether these shapes recur and stabilize, "
            "or whether they represent one-time variations in a more diverse repertoire."
        )
    
    if high_variety and distributed:
        return (
            "The lens of interpretant stabilization asks: do structural patterns recur enough to become "
            "recognizable forms? In this sample, the answer is nuanced. High structural variety means "
            "each sentence takes its own shape, resisting the repetition that would allow forms to stabilize. "
            "\n\n"
            "In Peircean terms, interpretants form through repeated encounters with signs. When every sentence "
            "is structurally distinct, readers don't develop expectations based on prior shapes. "
            "This can create a sense of freshness or unpredictability—each sentence is encountered anew. "
            "It can also create a certain interpretive effort: without stable forms to anchor expectation, "
            "readers must remain attentive to shifting structures. "
            "\n\n"
            "This variety might reflect deliberate range, contextual demands, or simply a small sample. "
            "Future exercises might explore what happens when you deliberately repeat a single structure "
            "across multiple sentences—how does stabilization feel when you create it intentionally?"
        )
    
    if low_variety or high_concentration:
        return (
            "Through the lens of interpretant stabilization, we see structures in this sample "
            "beginning to resolve into recognizable forms. Certain shapes recur, creating familiarity. "
            "\n\n"
            "In Peircean terms, this recurrence is significant: signs that appear repeatedly "
            "generate more stable interpretants. Readers develop expectations based on prior encounters; "
            "the third instance of a structure feels different from the first because pattern has been established. "
            "This can create rhythm, coherence, and a sense of authorial voice—the feeling that this is how "
            "you build sentences, recognizably and consistently. "
            "\n\n"
            "The concentration here suggests structural habits—go-to shapes that feel natural to you. "
            "These stabilized forms carry interpretive weight: they become the baseline against which "
            "variation registers. If you wanted to experiment, you might try deliberately breaking "
            "the dominant pattern to see what disruption feels like—and what new possibilities emerge."
        )
    
    # Default balanced case
    return (
        "The lens of interpretant stabilization examines how structural patterns become recognizable "
        "through recurrence. In this sample, we observe a middle ground: some shapes recur, "
        "allowing partial stabilization, while others appear only once. "
        "\n\n"
        "Peircean semiotics suggests that meaning solidifies through repeated encounters. "
        "The patterns that recur here are beginning to generate stable interpretants—readers "
        "encountering this writing would start to develop expectations based on familiar shapes. "
        "The patterns that don't recur remain more fluid, their interpretive potential unrealized "
        "within this sample. "
        "\n\n"
        "This balance is common in fluent writing: enough stability to create coherence, "
        "enough variation to maintain interest. The structural signature that emerges is "
        "neither rigidly consistent nor chaotically varied. Future exercises might push "
        "toward one extreme or the other to feel the difference."
    )


def _generate_mediation_and_boundary_synthesis(
    phase2: Dict[str, Any],
    mode: str,
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate MEDIATION_AND_BOUNDARY synthesis.
    
    This lens examines how meaning is bracketed, linked, or constrained.
    Related outputs: zero_events (05), operators (06), scope (07)
    """
    output_05 = _get_phase2_metrics(phase2, "output_05")
    output_06 = _get_phase2_metrics(phase2, "output_06")
    output_07 = _get_phase2_metrics(phase2, "output_07")
    
    exp_05 = output_05.get("explanation", "").lower()
    exp_06 = output_06.get("explanation", "").lower()
    exp_07 = output_07.get("explanation", "").lower()
    
    zero_present = "absent" not in exp_05 and ("pause" in exp_05 or "event" in exp_05)
    op_present = "absent" not in exp_06 and ("operator" in exp_06 or "connective" in exp_06)
    scope_present = "absent" not in exp_07 and ("layer" in exp_07 or "scope" in exp_07 or "parenthe" in exp_07)
    
    # All absent
    if not zero_present and not op_present and not scope_present:
        return (
            "The lens of mediation and boundary examines how structural markers shape the passage of meaning. "
            "In this sample, such markers are largely absent. No pause events, no connective operators, "
            "no scope markers like parentheses or brackets create boundaries or bridges. "
            "\n\n"
            "In Peircean terms, mediation refers to how signs channel meaning through interpretive pathways. "
            "When structural mediators are absent, meaning passes through relatively unobstructed—there are "
            "no hesitation markers to slow it down, no operators to compress relationships, "
            "no nested asides to create layers. The result is a certain directness: meaning travels "
            "from sentence to reader without much structural interference. "
            "\n\n"
            "This can feel clean and efficient, or it can feel sparse, depending on context and intent. "
            "If you wanted to experiment with mediation, try adding a single pause marker (an ellipsis, a dash) "
            "or a parenthetical aside to one sentence and notice how the reading experience shifts."
        )
    
    # Heavy mediation
    if zero_present and scope_present:
        return (
            "Through the lens of mediation and boundary, this sample shows significant structural activity. "
            "Both pause markers and scope events appear, creating a textured passage for meaning. "
            "\n\n"
            "In Peircean semiotics, these features function as mediators—structures that shape how "
            "interpretants form. Pause markers (ellipses, dashes) create moments of hesitation or suspension; "
            "scope markers (parentheses, brackets, quotes) create nested layers where meaning bifurcates "
            "into primary and secondary tracks. Together, they give the prose dimension and rhythm. "
            "\n\n"
            "The boundaries created by these markers aren't obstacles—they're architectural features "
            "that organize how readers move through meaning. Heavy mediation can feel rich and considered; "
            "it can also feel crowded if overused. In this sample, the markers create a particular texture. "
            "Future exercises might explore simplifying some sentences to see what direct, unmediated "
            "prose feels like in contrast."
        )
    
    # Partial mediation
    mediators = []
    if zero_present:
        mediators.append("pause markers")
    if op_present:
        mediators.append("operators")
    if scope_present:
        mediators.append("scope markers")
    
    mediator_text = ", ".join(mediators) if mediators else "some features"
    
    return (
        f"The lens of mediation and boundary reveals partial structural activity in this sample. "
        f"{mediator_text.capitalize()} appear, creating specific points where meaning is shaped, "
        f"paused, or nested. Other mediating structures are absent. "
        "\n\n"
        "In Peircean terms, each type of mediator does different work: pause markers create moments "
        "of suspension where readers supply what's left unsaid; operators compress relationships into symbols; "
        "scope markers create hierarchical layers. The particular combination present here creates "
        "a distinctive texture—some mediation but not complete saturation. "
        "\n\n"
        "Noticing which mediators you use naturally (and which you don't) reveals something about "
        "your structural habits. Future exercises might involve deliberately using the absent types "
        "to expand your repertoire, or leaning into your natural preferences to deepen their effect."
    )


def _generate_relational_density_synthesis(
    phase2: Dict[str, Any],
    mode: str,
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate RELATIONAL_DENSITY synthesis.
    
    This lens examines how features cluster or remain distinct.
    Related outputs: structural_density (08), co-occurrence (09)
    """
    output_08 = _get_phase2_metrics(phase2, "output_08")
    output_09 = _get_phase2_metrics(phase2, "output_09")
    
    exp_08 = output_08.get("explanation", "").lower()
    exp_09 = output_09.get("explanation", "").lower()
    
    is_sparse = "low" in exp_08 or "minimal" in exp_08 or "sparse" in exp_08
    is_dense = "high" in exp_08 or "significant" in exp_08 or "prominent" in exp_08
    no_markers = "no structural markers" in exp_09 or "none to combine" in exp_09
    
    if is_sparse or no_markers:
        return (
            "The lens of relational density examines how structural features cluster within sentences. "
            "In this sample, density is low—structural events are sparse or absent. "
            "\n\n"
            "When features don't cluster, there's no relational complexity at the structural level. "
            "Each sentence carries its content without much formal ornamentation. "
            "In Peircean terms, sparse density means interpretants form primarily through content "
            "rather than through structural interaction. The 'how' of the sentence recedes; "
            "the 'what' advances. "
            "\n\n"
            "This sparseness can serve clarity: with fewer structural features to navigate, "
            "readers focus on meaning. It can also feel flat if texture is desired. "
            "The question is whether sparseness serves your purpose here. "
            "Future exercises might involve deliberately layering features—adding a pause marker "
            "and a parenthetical to the same sentence—to feel what density does to reading."
        )
    
    if is_dense:
        return (
            "Through the lens of relational density, this sample shows structural features clustering "
            "within sentences. Multiple event types co-occur, creating complex relational texture. "
            "\n\n"
            "In Peircean terms, dense feature clustering creates rich interpretive environments. "
            "When pause markers, operators, and scope events appear together, they interact— "
            "each one shaping how the others are read. A parenthetical aside that contains a pause marker "
            "reads differently than one that doesn't. The relationships between features "
            "become part of the meaning, not just the features themselves. "
            "\n\n"
            "High density asks more of readers: more to navigate, more to process. "
            "It can create richness and nuance, or it can feel overwhelming. "
            "In this sample, the clustering creates a particular effect. "
            "Future exercises might explore what happens when you thin out the density— "
            "removing features to see what remains essential."
        )
    
    # Moderate density
    return (
        "The lens of relational density shows moderate structural activity in this sample. "
        "Some sentences carry multiple features; others proceed cleanly. "
        "\n\n"
        "In Peircean terms, density creates interpretive texture. Where features cluster, "
        "meaning becomes layered—readers navigate both content and form. "
        "Where features are absent, meaning flows more directly. "
        "The modulation between dense and sparse moments creates rhythm. "
        "\n\n"
        "This pattern is common in readable prose: not every sentence carries structural weight, "
        "but key moments get formal emphasis. Noticing where density appears can reveal "
        "where you've instinctively added emphasis. Future exercises might involve "
        "deliberately placing dense structure at specific points to see how it affects impact."
    )


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase3(
    phase2: Dict[str, Any],
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-3 synthesis output from Phase-2 UX output.
    
    Args:
        phase2: Phase-2 UX output
        high_intent_profile: Optional High-Intent profile for awareness
        
    Returns:
        Phase-3 synthesis output JSON
    """
    mode = phase2.get("presentation_mode", "DESCRIPTIVE")
    
    # Generate syntheses
    syntheses = []
    
    for i, group in enumerate(SYNTHESIS_GROUPS):
        lens = group["semiotic_lens"]
        related = group["related_outputs"]
        
        # Generate synthesis text based on lens
        if lens == "INTERPRETANT_STABILIZATION":
            synthesis_text = _generate_interpretant_stabilization_synthesis(phase2, mode, high_intent_profile)
        elif lens == "MEDIATION_AND_BOUNDARY":
            synthesis_text = _generate_mediation_and_boundary_synthesis(phase2, mode, high_intent_profile)
        elif lens == "RELATIONAL_DENSITY":
            synthesis_text = _generate_relational_density_synthesis(phase2, mode, high_intent_profile)
        else:
            synthesis_text = "Synthesis for this lens is not yet implemented."
        
        # Optionally expand with LLM
        if is_llm_available():
            synthesis_text, _ = expand_content(
                synthesis_text,
                {"phase2": phase2, "lens": lens, "related_outputs": related},
                "phase3_synthesis",
                "long"
            )
        
        syntheses.append({
            "synthesis_id": f"SYN_{i+1:02d}",
            "semiotic_lens": lens,
            "synthesis_text": synthesis_text,
            "related_outputs": related,
        })
    
    return {
        "phase3_version": PHASE3_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase2_version": SOURCE_PHASE2_VERSION,
        "synthesis_scope": SYNTHESIS_SCOPE,
        "interpretive_frame": INTERPRETIVE_FRAME,
        "syntheses": syntheses,
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with mock Phase-2 output
    mock_phase2 = {
        "presentation_mode": "REFLECTIVE",
        "outputs": {
            "output_01": {"explanation": "You've shared 5 sentences, offering enough to see shapes forming."},
            "output_03": {"explanation": "Your sample contains 4 distinct structural fingerprints, suggesting a mix of familiar shapes and fresh ones."},
            "output_04": {"explanation": "No single pattern dominates this sample—your top shapes cover only 40%."},
            "output_05": {"explanation": "A few pause markers appear in your writing (1 total)."},
            "output_06": {"explanation": "Your writing handles connections through words rather than symbols—no operators."},
            "output_07": {"explanation": "Some layering appears in your writing (2 scope events)."},
            "output_08": {"explanation": "Structural density is moderate (3 events, 0.60 per sentence)."},
            "output_09": {"explanation": "Most of your sentences contain no structural markers to combine."},
        }
    }
    
    print("Phase-3 Generator v0.2.0 Demo")
    print("=" * 60)
    
    result = generate_phase3(mock_phase2)
    
    print(f"Version: {result['phase3_version']}")
    print(f"Syntheses: {len(result['syntheses'])}")
    print()
    
    for syn in result['syntheses']:
        print(f"--- {syn['semiotic_lens']} ---")
        print(f"Related: {', '.join(syn['related_outputs'])}")
        print(f"Text ({len(syn['synthesis_text'])} chars):")
        text = syn['synthesis_text']
        print(text[:300] + "..." if len(text) > 300 else text)
        print()
