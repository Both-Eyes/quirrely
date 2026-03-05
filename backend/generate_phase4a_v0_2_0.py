#!/usr/bin/env python3
"""
Phase-4a Prompting Mode Generator
Version: 0.2.0

Generates Phase-4a reflection prompts from Phase-3 synthesis output.

CHANGELOG v0.2.0:
- Expanded prompt texts to 2-3x longer
- Added context-aware framing
- Added forward pointers to exercises
- Integrated with LLM expander for optional enhancement

Phase-4a is prompting (questions/invitations). It must not advise, diagnose,
recompute, or introduce new metric values. Prompts may reference the Phase-3 
synthesis text as the authoritative structural description.

Prompt types: NOTICE → REFLECT → REWRITE → COMPARE
"""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Dict, List, Optional

# Import LLM expander for optional enhancement
try:
    from lncp_llm_expander import expand_content, is_llm_available
except ImportError:
    def expand_content(t, c, e, l): return t, False
    def is_llm_available(): return False


PHASE4A_VERSION = "0.2.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE3_VERSION = "0.2.0"
SOURCE_PHASE2_VERSION = "0.2.0"

PROMPT_TYPE_ORDER = ["NOTICE", "REFLECT", "REWRITE", "COMPARE"]


def _stable_index(seed: str, n: int) -> int:
    if n <= 0:
        raise ValueError("Template list size must be > 0")
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


# =============================================================================
# Expanded Prompt Templates (2-3x longer)
# =============================================================================

def _generate_notice_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a NOTICE prompt - inviting attention to structural features."""
    lens = synthesis.get("semiotic_lens", "")
    text = synthesis.get("synthesis_text", "")[:200]
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Take a moment to read through your sentences slowly, as if encountering them for the first time. "
            "The analysis suggests that certain structural patterns are beginning to stabilize—shapes that recur "
            "and become recognizable. As you read, notice: which sentence shapes feel most familiar? "
            "Is there a structure you return to without thinking? Pay attention not to what you said, "
            "but to how the sentences are built. The pattern that catches your attention first "
            "is often the one closest to your structural default."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Look through your writing for the boundary markers—pauses, parentheses, connective symbols. "
            "These are the places where meaning doesn't flow smoothly but is interrupted, nested, or compressed. "
            "Notice where they appear: Are they clustered in certain sentences? Absent from others? "
            "Each boundary marker does specific work: a pause creates space; a parenthesis creates a layer; "
            "a connector compresses a relationship. As you scan, ask: where is the boundary-work happening? "
            "What is being set apart, and what is being joined?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Read your sentences with an eye for density—how much structural 'stuff' each one carries. "
            "Some sentences will feel clean and direct, moving straight through their content. "
            "Others will feel layered, textured, carrying multiple structural features. "
            "Notice the contrast: where do dense moments appear? Where is the writing sparse? "
            "The distribution of density creates rhythm. Pay attention to where your writing breathes "
            "and where it loads up. Neither is better; each serves different purposes."
        )
    
    return (
        "Read through your sentences slowly, paying attention to their structural shapes rather than their content. "
        "What patterns emerge when you focus on how sentences are built rather than what they say?"
    )


def _generate_reflect_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a REFLECT prompt - inviting consideration of implications."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Consider what it would feel like to write three more sentences in exactly the same structural pattern "
            "as your most common shape. Would it feel comfortable? Constraining? Natural? "
            "The patterns that come easily are often the ones we've internalized deeply—they feel like 'how I write.' "
            "Now consider the opposite: writing three sentences in a structure you've never used. "
            "What does your structural range make effortless, and what does it make hard to reach? "
            "There's no right answer here—just the chance to notice how your patterns shape your possibilities."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Think about what the boundary markers in your writing let in and keep out. "
            "A parenthetical aside creates space for qualification, digression, or afterthought—but it also "
            "signals that something is secondary. A pause marker (ellipsis, dash) creates room for the unsaid—"
            "but it also asks the reader to fill in. Consider: what do your boundary choices make room for? "
            "What do they exclude or subordinate? There's interpretive work happening at every boundary. "
            "Reflecting on it can reveal assumptions about what deserves the main line and what gets bracketed."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Consider how density creates texture in your writing. In moments of high density, "
            "multiple structural features compete for attention—the reader navigates form as well as content. "
            "In sparse moments, content carries the weight alone. Think about what your density pattern does "
            "to the reading experience. Does it create variety and rhythm? Does it feel intentional? "
            "If you wanted to place emphasis on a particular sentence, would you make it denser (more structural weight) "
            "or sparser (letting content stand alone)? The choice shapes how readers encounter your ideas."
        )
    
    return (
        "Reflect on what your structural patterns make easy and what they make difficult. "
        "What might a reader experience moving through writing built this way?"
    )


def _generate_rewrite_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a REWRITE prompt - inviting structural experimentation."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Choose one of your sentences and rewrite it in a deliberately different structural shape. "
            "If the original is short and direct, try making it longer with an embedded clause. "
            "If it's complex, try breaking it into simpler units. The goal isn't to improve the sentence—"
            "it's to feel the difference between structures. Keep the same basic meaning, but change the shape. "
            "Then read both versions aloud. Notice how the structural change affects rhythm, emphasis, and feel. "
            "This exercise isn't about finding the 'right' structure; it's about expanding your sense of what's possible."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Take a sentence that currently has no boundary markers—no parentheses, no dashes, no pauses—"
            "and add one. Insert a parenthetical aside that qualifies or comments on the main idea. "
            "Or add an ellipsis where meaning might trail off. Or use a dash to create an interruption. "
            "Notice what the boundary marker does to the sentence. Does it add nuance? Create hesitation? "
            "Open a new layer? Then try removing a boundary marker from a sentence that has one. "
            "What closes down or simplifies when the boundary disappears?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Find your densest sentence—the one with the most structural features—and simplify it. "
            "Strip out one layer: remove a parenthetical, eliminate a pause marker, spell out a connector. "
            "Then read both versions. What's lost? What's gained? "
            "Now try the opposite: take your sparsest sentence and add a structural feature. "
            "Insert an aside, add a hesitation, create a nested layer. "
            "Feel the difference between adding and removing density. Both moves are available to you; "
            "the question is when each serves your purpose."
        )
    
    return (
        "Choose one sentence and rewrite it with a different structural approach. "
        "Then compare the original to your rewrite—what shifts when structure changes?"
    )


def _generate_compare_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a COMPARE prompt - inviting analysis of variations."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Place two versions of a sentence side by side: your original and a structural variation. "
            "Read them as if you're a reader encountering each for the first time. "
            "Which feels more 'like you'? Which feels like a stretch? "
            "The version that feels natural is probably closer to your stabilized pattern—"
            "the shape that has become default through repetition. The version that feels odd "
            "might represent territory you don't often visit. Neither is better. "
            "But noticing which is which tells you something about your structural habits. "
            "If you wanted to expand your range, the stretch version shows a direction to explore."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Compare a sentence with boundary markers to a version without them. "
            "Read the bounded version—with its pauses, asides, or nested layers—"
            "then read the unbounded version, with those features stripped away. "
            "What's different? The bounded version might feel more nuanced, more qualified, more textured. "
            "The unbounded version might feel more direct, more assertive, more clean. "
            "Neither is inherently better; they do different work. "
            "The comparison reveals what boundary markers add and what they cost."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Compare a dense sentence to a sparse one—either two of your own, or two versions of the same sentence. "
            "Read the dense version slowly, noticing how you navigate its structural features. "
            "Then read the sparse version, noticing how directly it moves. "
            "Which feels more appropriate for what you're trying to say? The answer might differ by context. "
            "Dense structure can create emphasis or complexity; sparse structure can create clarity or speed. "
            "Comparing them side by side sharpens your sense of when each serves your purpose."
        )
    
    return (
        "Compare your original sentence to a structural variation. "
        "Notice what each version does well and what each loses."
    )


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase4a_prompting_output(
    phase3: Dict[str, Any],
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-4a prompting output from Phase-3 synthesis.
    
    Args:
        phase3: Phase-3 synthesis output
        high_intent_profile: Optional High-Intent profile
        
    Returns:
        Phase-4a prompting output JSON
    """
    syntheses = phase3.get("syntheses", [])
    scope = phase3.get("synthesis_scope", "SAMPLE_ONLY")
    frame = phase3.get("interpretive_frame", "LNCP_PEIRCEAN")
    
    prompt_sets = []
    
    for i, synthesis in enumerate(syntheses):
        synthesis_id = synthesis.get("synthesis_id", f"SYN_{i+1:02d}")
        lens = synthesis.get("semiotic_lens", "UNKNOWN")
        
        # Generate prompts for each type
        prompts = []
        
        # NOTICE
        notice_text = _generate_notice_prompt(synthesis)
        if is_llm_available():
            notice_text, _ = expand_content(
                notice_text, {"synthesis": synthesis}, "phase4a_prompt", "medium"
            )
        prompts.append({"prompt_type": "NOTICE", "prompt_text": notice_text})
        
        # REFLECT
        reflect_text = _generate_reflect_prompt(synthesis)
        if is_llm_available():
            reflect_text, _ = expand_content(
                reflect_text, {"synthesis": synthesis}, "phase4a_prompt", "medium"
            )
        prompts.append({"prompt_type": "REFLECT", "prompt_text": reflect_text})
        
        # REWRITE
        rewrite_text = _generate_rewrite_prompt(synthesis)
        if is_llm_available():
            rewrite_text, _ = expand_content(
                rewrite_text, {"synthesis": synthesis}, "phase4a_prompt", "medium"
            )
        prompts.append({"prompt_type": "REWRITE", "prompt_text": rewrite_text})
        
        # COMPARE
        compare_text = _generate_compare_prompt(synthesis)
        if is_llm_available():
            compare_text, _ = expand_content(
                compare_text, {"synthesis": synthesis}, "phase4a_prompt", "medium"
            )
        prompts.append({"prompt_type": "COMPARE", "prompt_text": compare_text})
        
        prompt_sets.append({
            "prompt_set_id": f"PS_{i+1:02d}",
            "synthesis_id": synthesis_id,
            "semiotic_lens": lens,
            "prompts": prompts,
        })
    
    return {
        "phase4a_version": PHASE4A_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "source_phase2_version": SOURCE_PHASE2_VERSION,
        "synthesis_scope": scope,
        "interpretive_frame": frame,
        "prompt_sets": prompt_sets,
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with mock Phase-3 output
    mock_phase3 = {
        "synthesis_scope": "SAMPLE_ONLY",
        "interpretive_frame": "LNCP_PEIRCEAN",
        "syntheses": [
            {
                "synthesis_id": "SYN_01",
                "semiotic_lens": "INTERPRETANT_STABILIZATION",
                "synthesis_text": "Patterns recur across the sample, allowing structural resolution.",
                "related_outputs": ["output_01", "output_03", "output_04"],
            },
            {
                "synthesis_id": "SYN_02",
                "semiotic_lens": "MEDIATION_AND_BOUNDARY",
                "synthesis_text": "Boundary markers create texture in the prose.",
                "related_outputs": ["output_05", "output_06", "output_07"],
            },
            {
                "synthesis_id": "SYN_03",
                "semiotic_lens": "RELATIONAL_DENSITY",
                "synthesis_text": "Density is moderate, with some clustering.",
                "related_outputs": ["output_08", "output_09"],
            },
        ]
    }
    
    print("Phase-4a Generator v0.2.0 Demo")
    print("=" * 60)
    
    result = generate_phase4a_prompting_output(mock_phase3)
    
    print(f"Version: {result['phase4a_version']}")
    print(f"Prompt sets: {len(result['prompt_sets'])}")
    print()
    
    for ps in result['prompt_sets']:
        print(f"--- {ps['semiotic_lens']} ---")
        for prompt in ps['prompts']:
            print(f"  {prompt['prompt_type']}: {len(prompt['prompt_text'])} chars")
            print(f"    \"{prompt['prompt_text'][:80]}...\"")
        print()
