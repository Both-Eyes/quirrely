#!/usr/bin/env python3
"""
Phase-4b Guidance Mode Generator
Version: 0.2.0

Generates Phase-4b practical guidance from Phase-3 synthesis output.

CHANGELOG v0.2.0:
- Expanded guidance texts to 2-3x longer
- Added context-aware scenarios
- Added forward pointers to exercises
- Integrated with LLM expander for optional enhancement

Phase-4b is guidance (practical application). It offers suggestions as possibilities,
not prescriptions. Guidance connects structural observations to real-world contexts.

Guidance types: GUIDE → PRACTICE → SCENARIO → COMPARE
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


PHASE4B_VERSION = "0.2.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE3_VERSION = "0.2.0"
SOURCE_PHASE2_VERSION = "0.2.0"

GUIDANCE_TYPE_ORDER = ["GUIDE", "PRACTICE", "SCENARIO", "COMPARE"]


# =============================================================================
# Expanded Guidance Templates (2-3x longer)
# =============================================================================

def _generate_guide_item(synthesis: Dict[str, Any]) -> str:
    """Generate a GUIDE item - orienting perspective on the structural pattern."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Think of your structural patterns as a kind of gravitational field: certain shapes pull your sentences "
            "toward them naturally. This isn't good or bad—it's how writing style works. The patterns that recur "
            "most often are your structural defaults, the moves you make without thinking. "
            "Becoming aware of them doesn't mean you should change them. It means you can choose when to follow "
            "them and when to resist. In contexts where consistency serves your purpose—building a recognizable voice, "
            "creating a rhythmic effect—lean into your defaults. In contexts where you want surprise or range, "
            "deliberately depart from them. The goal is awareness, not correction."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Every boundary marker in your writing does interpretive work. Parentheses create space for asides—"
            "thoughts that matter but don't belong in the main line. Dashes create interruptions—breaks in flow "
            "that can signal emphasis or afterthought. Ellipses create space for the unsaid—invitations for readers "
            "to fill in. Operators compress relationships—shortcuts that can clarify or obscure. "
            "Understanding what each type does helps you use them intentionally. "
            "A parenthetical aside signals 'this is secondary but relevant.' A dash signals 'wait—there's more.' "
            "An ellipsis signals 'you can imagine the rest.' Choose markers that match your intent."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Structural density is like texture in fabric: dense weaves feel heavier, sparser weaves feel lighter. "
            "Neither is better; each serves different purposes. Dense sentences—packed with pauses, asides, nested layers—"
            "ask readers to slow down and navigate. They work well for complex ideas that benefit from structural support. "
            "Sparse sentences—clean, direct, unadorned—let content carry the weight. "
            "They work well for simple ideas or moments where speed matters. "
            "Modulating density creates rhythm: a dense sentence after several sparse ones stands out. "
            "A sparse sentence after dense ones feels like arriving at clarity."
        )
    
    return (
        "This structural pattern shapes how readers experience your writing. "
        "Understanding it helps you use it intentionally rather than by default."
    )


def _generate_practice_item(synthesis: Dict[str, Any]) -> str:
    """Generate a PRACTICE item - concrete exercise suggestion."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Here's a practice exercise: write five sentences about any topic, but use exactly the same structural pattern "
            "for all five. Choose a pattern from your sample—perhaps your most common one—and repeat it deliberately. "
            "Notice how it feels to stay within a single shape. Does it feel constraining? Rhythmic? Natural? "
            "Then write five more sentences using five different structures—deliberately varying each one. "
            "Notice how that feels. The contrast between deliberate consistency and deliberate variety "
            "reveals something about your structural range and preferences."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Try this practice: take a paragraph you've written and remove all boundary markers—every parenthesis, "
            "dash, ellipsis, bracket, and connector symbol. Read the stripped version. What's lost? What's gained? "
            "Then add boundary markers back, but in different places than before. Put parentheses where there were none; "
            "add dashes where the flow was smooth; insert ellipses where thoughts completed. "
            "Read this version. The exercise reveals what boundary markers do and how placement changes effect. "
            "You'll develop a better feel for when to add and when to remove."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Practice modulating density deliberately. Write three sentences: one with no structural features (sparse), "
            "one with two features (moderate), and one with four or more (dense). "
            "Read them in sequence. Notice how the reading experience changes as density increases. "
            "Then arrange them in different orders: sparse-moderate-dense, dense-moderate-sparse, dense-sparse-dense. "
            "Notice how order affects rhythm. This exercise builds your intuition for when density serves your purpose "
            "and when simplicity does."
        )
    
    return (
        "Try a deliberate exercise: write the same idea in two different structural forms "
        "and notice what each version does to the reading experience."
    )


def _generate_scenario_item(synthesis: Dict[str, Any]) -> str:
    """Generate a SCENARIO item - real-world application context."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Consider different contexts where structural consistency matters: "
            "In a professional email, consistent patterns can create a sense of reliability and clarity. "
            "Readers learn what to expect; information lands predictably. "
            "In a creative piece, some consistency grounds the reader while variation creates interest. "
            "Too much consistency can feel monotonous; too much variation can feel disorienting. "
            "Think about your current writing context: does it call for more stability (building trust, conveying reliability) "
            "or more variety (maintaining interest, creating surprise)? Your structural patterns serve different purposes "
            "in different settings."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Think about where boundary markers serve you in real writing contexts: "
            "In emails, a parenthetical aside can soften a direct statement—'We need to reschedule (sorry for the short notice).' "
            "In reports, brackets can add clarifications without interrupting flow. "
            "In creative writing, dashes can create dramatic pauses or pivot points. "
            "In academic writing, parenthetical citations integrate sources without disrupting argument. "
            "The same boundary marker does different work in different contexts. "
            "Consider what you're writing now: which markers would serve your purpose? Which might clutter?"
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Think about density in specific contexts: "
            "In a quick Slack message, sparse is usually better—readers want to grab meaning fast. "
            "In a complex analysis, density might be necessary to hold multiple qualifications together. "
            "In a personal essay, modulating density creates pace—dense moments slow readers down; sparse moments speed them up. "
            "In instructions, sparse clarity usually wins over dense nuance. "
            "Consider what you're writing: does the context call for readers to slow down and navigate complexity, "
            "or to move quickly through clear content?"
        )
    
    return (
        "Think about how this structural pattern would function in specific contexts— "
        "emails, reports, creative writing, messages. What does each context call for?"
    )


def _generate_compare_item(synthesis: Dict[str, Any]) -> str:
    """Generate a COMPARE item - comparative analysis suggestion."""
    lens = synthesis.get("semiotic_lens", "")
    
    if lens == "INTERPRETANT_STABILIZATION":
        return (
            "Compare your structural patterns to writing you admire. Find a paragraph from a favorite author "
            "and analyze its structures: do shapes repeat? How much variation appears? "
            "Then compare to your own sample. The point isn't to imitate—it's to see how different writers "
            "balance consistency and variety. You might notice that writers you admire have more structural range "
            "than you realized, or that they're more consistent than you expected. "
            "This comparison can inform your own choices without prescribing what you should do."
        )
    elif lens == "MEDIATION_AND_BOUNDARY":
        return (
            "Compare how different contexts use boundary markers. Look at a news article, a novel, an academic paper, "
            "and a social media post. Count the parentheses, dashes, and other boundary markers in each. "
            "Notice the patterns: news tends toward sparse mediation; academic writing often uses more. "
            "Novels vary by author. Social media tends toward extremes—either very sparse or heavily marked. "
            "Where does your writing fit? The comparison reveals norms you might be following unconsciously "
            "and shows alternatives you might not have considered."
        )
    elif lens == "RELATIONAL_DENSITY":
        return (
            "Compare dense and sparse passages in writing you admire. Find a dense paragraph—one with lots of structural "
            "features—and a sparse one from the same author. Notice what each does: where does the author load up? "
            "Where do they strip down? Then compare to your own writing. Are you naturally dense, naturally sparse, "
            "or do you modulate? The comparison can reveal habits you didn't know you had "
            "and show you how other writers use density for effect."
        )
    
    return (
        "Compare your structural patterns to other writing—your own past work, "
        "writing you admire, or writing in your field. What does the comparison reveal?"
    )


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase4b(
    phase3: Dict[str, Any],
    high_intent_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-4b guidance output from Phase-3 synthesis.
    
    Args:
        phase3: Phase-3 synthesis output
        high_intent_profile: Optional High-Intent profile
        
    Returns:
        Phase-4b guidance output JSON
    """
    syntheses = phase3.get("syntheses", [])
    scope = phase3.get("synthesis_scope", "SAMPLE_ONLY")
    frame = phase3.get("interpretive_frame", "LNCP_PEIRCEAN")
    
    guidance_sets = []
    
    for i, synthesis in enumerate(syntheses):
        synthesis_id = synthesis.get("synthesis_id", f"SYN_{i+1:02d}")
        lens = synthesis.get("semiotic_lens", "UNKNOWN")
        
        # Generate guidance items for each type
        items = []
        
        # GUIDE
        guide_text = _generate_guide_item(synthesis)
        if is_llm_available():
            guide_text, _ = expand_content(
                guide_text, {"synthesis": synthesis}, "phase4b_guidance", "medium"
            )
        items.append({"item_type": "GUIDE", "text": guide_text})
        
        # PRACTICE
        practice_text = _generate_practice_item(synthesis)
        if is_llm_available():
            practice_text, _ = expand_content(
                practice_text, {"synthesis": synthesis}, "phase4b_guidance", "medium"
            )
        items.append({"item_type": "PRACTICE", "text": practice_text})
        
        # SCENARIO
        scenario_text = _generate_scenario_item(synthesis)
        if is_llm_available():
            scenario_text, _ = expand_content(
                scenario_text, {"synthesis": synthesis}, "phase4b_guidance", "medium"
            )
        items.append({"item_type": "SCENARIO", "text": scenario_text})
        
        # COMPARE
        compare_text = _generate_compare_item(synthesis)
        if is_llm_available():
            compare_text, _ = expand_content(
                compare_text, {"synthesis": synthesis}, "phase4b_guidance", "medium"
            )
        items.append({"item_type": "COMPARE", "text": compare_text})
        
        guidance_sets.append({
            "guidance_set_id": f"GS_{i+1:02d}",
            "synthesis_id": synthesis_id,
            "semiotic_lens": lens,
            "items": items,
        })
    
    return {
        "phase4b_version": PHASE4B_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "source_phase2_version": SOURCE_PHASE2_VERSION,
        "synthesis_scope": scope,
        "interpretive_frame": frame,
        "guidance_sets": guidance_sets,
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
                "synthesis_text": "Patterns recur across the sample.",
                "related_outputs": ["output_01", "output_03", "output_04"],
            },
            {
                "synthesis_id": "SYN_02",
                "semiotic_lens": "MEDIATION_AND_BOUNDARY",
                "synthesis_text": "Boundary markers create texture.",
                "related_outputs": ["output_05", "output_06", "output_07"],
            },
            {
                "synthesis_id": "SYN_03",
                "semiotic_lens": "RELATIONAL_DENSITY",
                "synthesis_text": "Density is moderate.",
                "related_outputs": ["output_08", "output_09"],
            },
        ]
    }
    
    print("Phase-4b Generator v0.2.0 Demo")
    print("=" * 60)
    
    result = generate_phase4b(mock_phase3)
    
    print(f"Version: {result['phase4b_version']}")
    print(f"Guidance sets: {len(result['guidance_sets'])}")
    print()
    
    for gs in result['guidance_sets']:
        print(f"--- {gs['semiotic_lens']} ---")
        for item in gs['items']:
            print(f"  {item['item_type']}: {len(item['text'])} chars")
            print(f"    \"{item['text'][:80]}...\"")
        print()
