#!/usr/bin/env python3
"""
Phase-4b Guidance Mode Generator
Version: 0.3.0

Generates Phase-4b guidance items from Phase-3 synthesis output.

CHANGELOG v0.3.0:
- Collaborative-Curious tone throughout
- "We/let's" language positioning guidance as shared discovery
- Light customization (references patterns, not heavy metrics)
- Partnership framing, not authority

CHANGELOG v0.2.0:
- Expanded guidance texts to 2-3x longer
- Added context-aware framing
- Added forward pointers to exercises
- Integrated with LLM expander for optional enhancement

Phase-4b is guidance (gentle suggestions). Unlike prompting, it may
offer a perspective or framing, but must remain exploratory rather
than prescriptive.

Item types: GUIDE → PRACTICE → SCENARIO → COMPARE
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


PHASE4B_VERSION = "0.3.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE3_VERSION = "0.2.0"
SOURCE_PHASE2_VERSION = "0.2.0"

ITEM_TYPE_ORDER = ["GUIDE", "PRACTICE", "SCENARIO", "COMPARE"]


def _stable_index(seed: str, n: int) -> int:
    if n <= 0:
        raise ValueError("Template list size must be > 0")
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


# =============================================================================
# Collaborative-Curious Guidance Templates (v0.3.0)
# =============================================================================

def _generate_guide_item(synthesis: Dict[str, Any]) -> str:
    """Generate a GUIDE item - shared wisdom about structural patterns."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Together, let's think of structural patterns as a kind of gravitational field: certain shapes pull sentences "
            "toward them naturally. This isn't good or bad—it's how writing style works. What we often find "
            "is that the patterns recurring most often become structural defaults, the moves made without thinking. "
            "Becoming aware of them together doesn't mean we should change them. It means we can explore when to follow "
            "them and when to experiment with resisting. In contexts where consistency serves the purpose—building a recognizable voice, "
            "creating a rhythmic effect—we might lean into the defaults. In contexts where surprise or range feels right, "
            "we might deliberately depart. What we're after together is awareness, not correction."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "What we notice together is that every boundary marker does interpretive work. Parentheses create space for asides—"
            "thoughts that matter but don't quite belong in the main line. Dashes create interruptions—breaks that can signal "
            "emphasis or afterthought. Ellipses create space for the unsaid—invitations for readers to fill in. "
            "Operators compress relationships—shortcuts that can clarify or obscure. "
            "Understanding together what each type does helps with using them intentionally. "
            "A parenthetical signals 'this is secondary but relevant.' A dash signals 'wait—there's more.' "
            "An ellipsis signals 'you can imagine the rest.' Let's think about which markers match which intents."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's think of structural density together like texture in fabric: dense weaves feel heavier, sparser weaves feel lighter. "
            "Neither is better; each serves different purposes. Dense sentences—packed with pauses, asides, nested layers—"
            "ask readers to slow down and navigate. They can work well for complex ideas that benefit from structural support. "
            "Sparse sentences—clean, direct, unadorned—let content carry the weight. "
            "They can work well for simple ideas or moments where speed matters. "
            "What we often find is that modulating density creates rhythm: a dense sentence after several sparse ones stands out. "
            "A sparse sentence after dense ones can feel like arriving at clarity."
        )
    
    return (
        "Together, we can see how this structural pattern shapes how readers experience your writing. "
        "Understanding it helps us think about using it intentionally rather than by default."
    )


def _generate_practice_item(synthesis: Dict[str, Any]) -> str:
    """Generate a PRACTICE item - collaborative exercise suggestion."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Let's try a practice exercise together: write five sentences about any topic, but use exactly the same structural pattern "
            "for all five. We might choose a pattern from your sample—perhaps the most common one—and repeat it deliberately. "
            "I'm curious: how does it feel to stay within a single shape? Does it feel constraining? Rhythmic? Natural? "
            "Then let's try five more sentences using five different structures—deliberately varying each one. "
            "Together, we can notice how that feels. The contrast between deliberate consistency and deliberate variety "
            "often reveals something interesting about structural range and preferences."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Here's something we can explore together: take a paragraph and remove all boundary markers—every parenthesis, "
            "dash, ellipsis, bracket, and connector symbol. Let's read the stripped version. What's lost? What's gained? "
            "Then we can add boundary markers back, but in different places than before. Put parentheses where there were none; "
            "add dashes where the flow was smooth; insert ellipses where thoughts completed. "
            "Let's read this version together. The exercise often reveals what boundary markers do and how placement changes effect. "
            "I think we'll develop a better feel for when to add and when to remove."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's practice modulating density together deliberately. Write three sentences: one with no structural features (sparse), "
            "one with two features (moderate), and one with four or more (dense). "
            "Together, we can read them in sequence and notice how the reading experience changes as density increases. "
            "Then let's arrange them in different orders: sparse-moderate-dense, dense-moderate-sparse, dense-sparse-dense. "
            "I'm curious about how order affects rhythm. This exercise often builds intuition for when density serves "
            "and when simplicity does."
        )
    
    return (
        "Let's try a deliberate exercise together: write the same idea in two different structural forms "
        "and notice together what each version does to the reading experience."
    )


def _generate_scenario_item(synthesis: Dict[str, Any]) -> str:
    """Generate a SCENARIO item - shared exploration of real-world contexts."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Together, let's consider different contexts where structural consistency matters: "
            "In a professional email, consistent patterns can create a sense of reliability and clarity. "
            "Readers learn what to expect; information lands predictably. "
            "In a creative piece, some consistency grounds the reader while variation creates interest. "
            "Too much consistency can feel monotonous; too much variation can feel disorienting. "
            "I wonder about your current writing context: does it call for more stability (building trust, conveying reliability) "
            "or more variety (maintaining interest, creating surprise)? Let's think together about how structural patterns "
            "serve different purposes in different settings."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Let's think together about where boundary markers serve in real writing contexts: "
            "In emails, a parenthetical aside can soften a direct statement—'We need to reschedule (sorry for the short notice).' "
            "In reports, brackets can add clarifications without interrupting flow. "
            "In creative writing, dashes can create dramatic pauses or pivot points. "
            "In academic writing, parenthetical citations integrate sources without disrupting argument. "
            "What we find together is that the same boundary marker does different work in different contexts. "
            "I'm curious: in what you're writing now, which markers might serve your purpose? Which might clutter?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Imagine together: you're writing an email to a colleague about a complex issue. "
            "Where might density serve you—packing a sentence with qualifications and asides—"
            "and where might simplicity serve you—letting a clear statement land without decoration? "
            "Now imagine you're writing a story. Dense sentences can slow time, create atmosphere, invite lingering. "
            "Sparse sentences can accelerate, create urgency, mimic action. "
            "Together, we can see that context shapes when density works. "
            "Let's think about your current context: what does it ask for?"
        )
    
    return (
        "Together, let's imagine this pattern in different contexts. "
        "Where might it serve well? Where might a different approach work better?"
    )


def _generate_compare_item(synthesis: Dict[str, Any]) -> str:
    """Generate a COMPARE item - invitation to joint comparative analysis."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Let's compare structural patterns together with writing you admire. Find a paragraph from a favorite author "
            "and together we can analyze its structures: do shapes repeat? How much variation appears? "
            "Then let's look at your own sample side by side. The comparison isn't about who's better—"
            "it's about noticing different approaches. What patterns does the admired writer use? "
            "What patterns do you use? Are there moves in their toolkit that you might explore? "
            "Together, we're not looking for 'right' structures—we're expanding our sense of what's possible."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Together, let's compare how different contexts use boundary markers. Look at a news article, a novel, "
            "an academic paper. Notice together where parentheses appear, where dashes create interruption, "
            "where ellipses leave space. Each genre has conventions—and each writer within a genre makes choices. "
            "Now let's look at your sample. Where do your boundary choices fit with convention? "
            "Where do they depart? Neither fitting nor departing is better—"
            "but noticing together helps us think about whether our choices are intentional."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Let's compare density patterns together across different texts. Take a paragraph from a text you find "
            "'easy to read' and one from a text you find 'challenging.' Together, we can count structural features. "
            "What we often find is that the 'easy' text has lower density—fewer features per sentence, "
            "cleaner passage from start to finish. The 'challenging' text may have higher density. "
            "Now let's look at your sample. Where does your density fall? Is it serving your purpose? "
            "Together, we're not judging—just noticing and wondering."
        )
    
    return (
        "Let's place your patterns alongside another text together and notice what emerges. "
        "Comparison often reveals choices we didn't know we were making."
    )


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase4b(phase3_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Phase-4b output from Phase-3 synthesis.
    
    Args:
        phase3_output: Phase-3 synthesis output containing syntheses array
        
    Returns:
        Phase-4b guidance output conforming to schema
    """
    syntheses = phase3_output.get("syntheses", [])
    llm_enhanced = is_llm_available()
    
    guidance_sets = []
    for synthesis in syntheses:
        lens = synthesis.get("semiotic_lens", "UNKNOWN")
        synthesis_id = synthesis.get("synthesis_id", "")
        
        # Generate items for each type
        items = [
            {
                "item_type": "GUIDE",
                "text": _generate_guide_item(synthesis),
            },
            {
                "item_type": "PRACTICE",
                "text": _generate_practice_item(synthesis),
            },
            {
                "item_type": "SCENARIO",
                "text": _generate_scenario_item(synthesis),
            },
            {
                "item_type": "COMPARE",
                "text": _generate_compare_item(synthesis),
            },
        ]
        
        # Optional LLM enhancement
        if llm_enhanced:
            for item in items:
                context = {
                    "semiotic_lens": lens,
                    "item_type": item["item_type"],
                    "synthesis_text": synthesis.get("synthesis_text", ""),
                }
                enhanced, _ = expand_content(
                    item["text"],
                    context,
                    "phase4b_item",
                    lens,
                )
                item["text"] = enhanced
        
        guidance_sets.append({
            "guidance_set_id": f"GS_{synthesis_id[-3:] if synthesis_id else '001'}",
            "semiotic_lens": lens,
            "source_synthesis_id": synthesis_id,
            "items": items,
        })
    
    return {
        "phase4b_version": PHASE4B_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "mode": "GUIDANCE",
        "item_type_order": ITEM_TYPE_ORDER,
        "guidance_sets": guidance_sets,
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
                "synthesis_text": "Patterns are beginning to stabilize.",
            },
            {
                "synthesis_id": "SYN_002",
                "semiotic_lens": "MEDIATION_AND_BOUNDARY",
                "synthesis_text": "Boundary markers create texture.",
            },
        ]
    }
    
    print("Phase-4b Generator v0.3.0 Demo (Collaborative-Curious Tone)")
    print("=" * 70)
    
    result = generate_phase4b(mock_phase3)
    
    for gs in result["guidance_sets"]:
        print(f"\n{gs['semiotic_lens']}:")
        for item in gs["items"]:
            print(f"\n  [{item['item_type']}]")
            print(f"  {item['text'][:150]}...")
