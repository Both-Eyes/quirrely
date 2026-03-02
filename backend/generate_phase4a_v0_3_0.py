#!/usr/bin/env python3
"""
Phase-4a Prompting Mode Generator
Version: 0.3.0

Generates Phase-4a reflection prompts from Phase-3 synthesis output.

CHANGELOG v0.3.0:
- Collaborative-Curious tone throughout
- "We/let's" language positioning analysis as shared inquiry
- Light customization (references patterns, not heavy metrics)
- Partnership framing, not authority

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


PHASE4A_VERSION = "0.3.0"
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
# Collaborative-Curious Prompt Templates (v0.3.0)
# =============================================================================

def _generate_notice_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a NOTICE prompt - inviting shared attention to structural features."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Let's read through your sentences together, slowly, as if we're encountering them for the first time. "
            "What we're seeing is that certain structural patterns are beginning to find their shape—some forms recur, "
            "becoming recognizable, while others appear just once. As we look together, I wonder: which shapes feel "
            "most familiar to you? Is there a structure you find yourself returning to without quite meaning to? "
            "Let's pay attention not to what you said, but to how the sentences are built. "
            "The pattern that catches your attention first might be the one closest to your natural default."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Let's look through your writing together for the boundary markers—pauses, parentheses, connective symbols. "
            "These are the places where meaning doesn't flow smoothly but gets interrupted, nested, or compressed. "
            "Together, let's notice where they appear: Are they clustered in certain sentences? Absent from others? "
            "Each boundary marker does specific work—a pause creates space, a parenthesis creates a layer, "
            "a connector compresses a relationship. As we scan together, I'm curious: where is the boundary-work "
            "happening in your writing? What's being set apart, and what's being joined?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's read your sentences together with an eye for density—how much structural 'stuff' each one carries. "
            "Some sentences will feel clean and direct, moving straight through their content. "
            "Others will feel layered, textured, carrying multiple structural features. "
            "Together, let's notice the contrast: where do dense moments appear? Where is the writing sparse? "
            "The distribution of density creates rhythm. I'm curious about where your writing breathes "
            "and where it loads up. Neither is better—let's just notice what's happening."
        )
    
    return (
        "Let's read through your sentences together, paying attention to their structural shapes rather than their content. "
        "What patterns emerge when we focus on how sentences are built rather than what they say?"
    )


def _generate_reflect_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a REFLECT prompt - inviting shared consideration of implications."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Together, let's consider what it would feel like to write three more sentences in exactly the same "
            "structural pattern as the shapes we're seeing recur. Would it feel comfortable? Constraining? Natural? "
            "The patterns that come easily are often the ones we've internalized deeply—they feel like 'how I write.' "
            "Now I wonder: what about the opposite? Writing sentences in a structure you've never used. "
            "What does your structural range make effortless, and what does it make harder to reach? "
            "There's no right answer here—let's just sit with what emerges when we think about this together."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Let's think together about what the boundary markers in your writing let in and keep out. "
            "A parenthetical aside creates space for qualification, digression, or afterthought—but it also "
            "signals that something is secondary. A pause marker creates room for the unsaid—"
            "but it also invites the reader to fill in. Together, I wonder: what do your boundary choices make room for? "
            "What do they set aside or subordinate? There's interpretive work happening at every boundary, "
            "and reflecting on it together can reveal something interesting about what gets the main line "
            "and what gets bracketed."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's consider together how density creates texture in your writing. In moments of high density, "
            "multiple structural features share the space—the reader navigates form as well as content. "
            "In sparse moments, content carries the weight alone. Together, I'm wondering: what does your density pattern do "
            "to the reading experience? Does it create variety and rhythm? "
            "If you wanted to place emphasis on a particular sentence, would you make it denser "
            "or sparser? Let's sit with that question—there's no single answer."
        )
    
    return (
        "Let's reflect together on what your structural patterns make easy and what they make difficult. "
        "What might a reader experience moving through writing built this way?"
    )


def _generate_rewrite_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a REWRITE prompt - inviting collaborative structural experimentation."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "What if we tried rewriting one of your sentences together in a deliberately different structural shape? "
            "If the original is short and direct, let's try making it longer with an embedded clause. "
            "If it's complex, let's try breaking it into simpler units. The goal isn't to improve the sentence—"
            "it's to feel the difference between structures together. Keep the same basic meaning, but change the shape. "
            "Then let's read both versions aloud. I'm curious: how does the structural change affect rhythm, emphasis, "
            "and feel? This isn't about finding the 'right' structure—let's just expand our sense of what's possible."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Let's experiment together: take a sentence that currently has no boundary markers—no parentheses, "
            "no dashes, no pauses—and add one. We could insert a parenthetical aside that qualifies the main idea, "
            "or add an ellipsis where meaning might trail off, or use a dash to create an interruption. "
            "Together, let's notice what the boundary marker does to the sentence. Does it add nuance? Create hesitation? "
            "Open a new layer? Then what if we try removing a boundary marker from a sentence that has one? "
            "I wonder: what closes down or simplifies when the boundary disappears?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's find your densest sentence together—the one with the most structural features—and simplify it. "
            "We can strip out one layer: remove a parenthetical, eliminate a pause marker, spell out a connector. "
            "Then let's read both versions. What's lost? What's gained? "
            "Now let's try the opposite: take your sparsest sentence and add a structural feature together. "
            "Insert an aside, add a hesitation, create a nested layer. "
            "I'm curious about the difference between adding and removing density. Both moves are available—"
            "the question we're exploring is when each might serve your purpose."
        )
    
    return (
        "What if we chose one sentence together and rewrote it with a different structural approach? "
        "Then we could compare the original to the rewrite—let's see what shifts when structure changes."
    )


def _generate_compare_prompt(synthesis: Dict[str, Any]) -> str:
    """Generate a COMPARE prompt - inviting joint analysis of variations."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Let's place two versions of a sentence side by side together: your original and a structural variation. "
            "Reading them as if we're encountering each for the first time, I wonder: "
            "which feels more 'like you'? Which feels like a stretch? "
            "The version that feels natural is probably closer to your stabilized pattern—"
            "the shape that has become default through repetition. The version that feels odd "
            "might be where growth happens. Together, let's notice which is which, "
            "without judging either as better or worse."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Let's compare a sentence with boundary markers to a version without them, side by side. "
            "Together, what do we notice? The bounded version might feel more nuanced, more layered; "
            "the unbounded version might feel more direct, more committed. "
            "Neither is inherently better—but they create different reading experiences. "
            "I'm curious which feels closer to your intent for this particular moment. "
            "What does adding or removing boundaries do to the relationship between you and your reader?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's look at two sentences together—one dense, one sparse—and see what we notice. "
            "In the dense sentence, structural features layer and compete. In the sparse one, content stands alone. "
            "Together, let's feel the difference in how we read each one. "
            "Does the dense version feel richer or busier? Does the sparse version feel cleaner or emptier? "
            "I wonder: what does each texture invite? There's no right answer—let's just explore what emerges "
            "when we pay attention to density together."
        )
    
    return (
        "Let's compare two structural approaches side by side together. "
        "What do we notice about how each one shapes the reading experience?"
    )


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase4a_prompting_output(phase3_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Phase-4a output from Phase-3 synthesis.
    
    Args:
        phase3_output: Phase-3 synthesis output containing syntheses array
        
    Returns:
        Phase-4a prompting output conforming to schema
    """
    syntheses = phase3_output.get("syntheses", [])
    llm_enhanced = is_llm_available()
    
    prompt_sets = []
    for synthesis in syntheses:
        lens = synthesis.get("semiotic_lens", "UNKNOWN")
        synthesis_id = synthesis.get("synthesis_id", "")
        
        # Generate prompts for each type
        prompts = [
            {
                "prompt_type": "NOTICE",
                "prompt_text": _generate_notice_prompt(synthesis),
            },
            {
                "prompt_type": "REFLECT",
                "prompt_text": _generate_reflect_prompt(synthesis),
            },
            {
                "prompt_type": "REWRITE",
                "prompt_text": _generate_rewrite_prompt(synthesis),
            },
            {
                "prompt_type": "COMPARE",
                "prompt_text": _generate_compare_prompt(synthesis),
            },
        ]
        
        # Optional LLM enhancement
        if llm_enhanced:
            for prompt in prompts:
                context = {
                    "semiotic_lens": lens,
                    "prompt_type": prompt["prompt_type"],
                    "synthesis_text": synthesis.get("synthesis_text", ""),
                }
                enhanced, _ = expand_content(
                    prompt["prompt_text"],
                    context,
                    "phase4a_prompt",
                    lens,
                )
                prompt["prompt_text"] = enhanced
        
        prompt_sets.append({
            "prompt_set_id": f"PS_{synthesis_id[-3:] if synthesis_id else '001'}",
            "semiotic_lens": lens,
            "source_synthesis_id": synthesis_id,
            "prompts": prompts,
        })
    
    return {
        "phase4a_version": PHASE4A_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "mode": "PROMPTING",
        "prompt_type_order": PROMPT_TYPE_ORDER,
        "prompt_sets": prompt_sets,
        "llm_enhanced": llm_enhanced,
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with mock Phase-3 input
    mock_phase3 = {
        "syntheses": [
            {
                "synthesis_id": "SYN_001",
                "semiotic_lens": "INTERPRETANT_STABILIZATION",
                "synthesis_text": "Patterns are beginning to stabilize in this sample.",
            },
            {
                "synthesis_id": "SYN_002",
                "semiotic_lens": "MEDIATION_AND_BOUNDARY",
                "synthesis_text": "Boundary markers create texture.",
            },
        ]
    }
    
    print("Phase-4a Generator v0.3.0 Demo (Collaborative-Curious Tone)")
    print("=" * 70)
    
    result = generate_phase4a_prompting_output(mock_phase3)
    
    for ps in result["prompt_sets"]:
        print(f"\n{ps['semiotic_lens']}:")
        for p in ps["prompts"]:
            print(f"\n  [{p['prompt_type']}]")
            print(f"  {p['prompt_text'][:150]}...")
