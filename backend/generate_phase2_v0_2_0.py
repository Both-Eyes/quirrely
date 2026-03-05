#!/usr/bin/env python3
"""
Phase-2 UX Presentation Generator
Version: 0.2.0

Generates Phase-2 UX output from Phase-1 compute output.
Uses template-based generation with optional LLM expansion.

CHANGELOG v0.2.0:
- Expanded explanations to 2-3x longer
- Added interpretive framing (non-directive)
- Added forward pointers to exercises
- Added High-Intent awareness in relevant outputs
- Integrated with LLM expander for optional enhancement

This generator transforms Phase-1 metrics into user-facing explanations
with example insights. Explanations are longer and more interpretive
while remaining non-prescriptive.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

# Import LLM expander for optional enhancement
try:
    from lncp_llm_expander import expand_content, is_llm_available
except ImportError:
    def expand_content(t, c, e, l): return t, False
    def is_llm_available(): return False


PHASE2_VERSION = "0.2.0"
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


# =============================================================================
# Expanded Explanation Generators (2-3x longer)
# =============================================================================

def _generate_explanation_output_01(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 01: How Much You Shared."""
    count = metrics.get("sentence_count", {}).get("count", 0)
    token = metrics.get("token_volume", {})
    total_words = token.get("total_tokens", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 1:
            return (
                f"One sentence is present in this sample, containing {total_words} words. "
                f"With a single sentence, what we observe here is descriptive rather than pattern-revealing. "
                f"Think of this as a snapshot—a single frame that hints at style but doesn't yet show rhythm or repetition. "
                f"A longer sample would allow structural habits to emerge, showing whether this sentence's shape is typical for you or an exception."
            )
        elif count < 4:
            return (
                f"This sample contains {count} sentences with {total_words} words total. "
                f"With this amount of material, we can describe what appears but are cautious about claiming patterns. "
                f"Structural habits need repetition to reveal themselves, and {count} sentences sit at the threshold of visibility. "
                f"What you see here reflects this specific sample; a longer piece might confirm or complicate these observations."
            )
        else:
            return (
                f"You've provided {count} sentences totaling {total_words} words. "
                f"This gives us enough material to begin noticing structural tendencies—though we remain descriptive rather than definitive. "
                f"Each additional sentence adds evidence; patterns that appear across multiple sentences carry more weight than isolated features."
            )
    else:  # REFLECTIVE
        if count < 6:
            return (
                f"You've shared {count} sentences, offering {total_words} words to work with. "
                f"This is enough to see shapes forming, though the patterns are still provisional. "
                f"Structural habits become clearer with more material—what appears here might represent your typical style, "
                f"or it might be specific to this particular piece of writing. "
                f"If you're curious whether these patterns persist, a longer sample or a second round would tell us more."
            )
        else:
            return (
                f"Your sample of {count} sentences ({total_words} words) provides solid ground for observation. "
                f"With this much material, patterns begin to stabilize—what recurs starts to feel like habit rather than coincidence. "
                f"The structures here likely reflect something genuine about how you build sentences, "
                f"though context always matters: the same writer might structure differently in an email versus an essay. "
                f"What we see here is a portrait of this sample, suggestive but not exhaustive."
            )


def _generate_explanation_output_02(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 02: Word-Level Detail."""
    token = metrics.get("token_volume", {})
    total = token.get("total_tokens", 0)
    avg = token.get("mean_tokens_per_sentence", 0)
    
    if mode == "DESCRIPTIVE":
        return (
            f"This sample contains {total} words distributed across your sentences, averaging {avg:.1f} words each. "
            f"Sentence length is one of the most basic structural features, yet it shapes reading experience profoundly. "
            f"Shorter sentences tend to feel punchy and direct; longer ones create room for complexity and qualification. "
            f"This average describes what's here without judging what's better—different contexts call for different lengths."
        )
    else:  # REFLECTIVE
        if avg < 10:
            return (
                f"Your sentences run lean—{avg:.1f} words on average, {total} words total. "
                f"This compact style creates a certain rhythm: quick, direct, each sentence carrying a single thought before moving on. "
                f"Short sentences can create urgency or clarity; they leave less room for hedging or elaboration. "
                f"In some contexts this directness serves well; in others, you might choose to let sentences breathe longer. "
                f"Neither is inherently better—what matters is whether the length serves your purpose."
            )
        elif avg < 20:
            return (
                f"Your sentences average {avg:.1f} words, totaling {total} across the sample. "
                f"This sits in a comfortable middle range—not clipped, not sprawling. "
                f"Medium-length sentences can balance accessibility with nuance, giving ideas room to develop without losing readers in complexity. "
                f"The rhythm here feels conversational: thoughts unfold at a readable pace. "
                f"If you wanted to experiment, you might try writing the same content in very short or very long sentences to feel the difference."
            )
        else:
            return (
                f"Your sentences stretch out—{avg:.1f} words on average, {total} total. "
                f"Longer sentences create space for qualification, subordination, and layers of thought. "
                f"They ask more of readers, requiring attention across more material before reaching resolution. "
                f"This style can feel literary, formal, or exploratory—the extended breath of a writer thinking through complexity. "
                f"In some contexts it's a strength; in others, breaking into shorter units might serve clarity. "
                f"The question isn't whether this is right, but whether it matches your intent."
            )


def _generate_explanation_output_03(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 03: Structural Fingerprints."""
    variety = metrics.get("structural_variety", {})
    unique = variety.get("unique_signatures", 0)
    ratio = variety.get("variety_ratio", 0)
    sentence_count = metrics.get("sentence_count", {}).get("count", 0)
    
    if mode == "DESCRIPTIVE":
        return (
            f"Your sample shows {unique} unique structural signature(s), yielding a variety ratio of {ratio:.2f}. "
            f"A structural signature captures the shape of a sentence—its grammatical skeleton stripped of content. "
            f"When signatures repeat, it suggests a recurring way of building sentences; when they vary, each sentence takes its own form. "
            f"This ratio compares unique shapes to total sentences: 1.0 means every sentence is structurally distinct, "
            f"while lower ratios indicate repetition. Here, we describe what appears without inferring habit from limited data."
        )
    else:  # REFLECTIVE
        if ratio < 0.5:
            return (
                f"You're working with {unique} structural shapes across {sentence_count} sentences, a ratio of {ratio:.2f}. "
                f"This suggests some repetition in how you build sentences—certain structures recur while others don't appear at all. "
                f"Repetition isn't a flaw; it creates rhythm and coherence. Readers often find comfort in familiar shapes, "
                f"even when content varies. At the same time, you might notice which shapes you return to naturally "
                f"and consider whether expanding your range could add texture. "
                f"Structural exercises—deliberately trying unfamiliar shapes—can reveal moves you didn't know you had."
            )
        elif ratio < 1.0:
            return (
                f"Your sample contains {unique} distinct structural fingerprints (ratio: {ratio:.2f}), "
                f"suggesting a mix of familiar shapes and fresh ones. "
                f"This balance often characterizes fluent writing: enough consistency to feel coherent, "
                f"enough variation to maintain interest. "
                f"Some sentences share a skeleton; others take their own form. "
                f"If you look closely, you might notice which shapes you return to—those are likely your structural defaults. "
                f"A future exercise might involve deliberately using only your least common structures to see what emerges."
            )
        else:
            return (
                f"Every sentence in this sample has its own structural shape—{unique} unique signatures, no repeats. "
                f"This high variety (ratio: {ratio:.2f}) means you're not falling into repetitive patterns, at least not here. "
                f"Whether this reflects intentional variation or simply a small sample size, it's worth noticing. "
                f"High structural variety can create a sense of restlessness or richness, depending on how it interacts with content. "
                f"In a longer sample, we'd see whether this variety persists or whether certain shapes begin to dominate. "
                f"For now, it suggests flexibility in how you construct sentences."
            )


def _generate_explanation_output_04(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 04: Your Most Common Patterns."""
    conc = metrics.get("signature_concentration", {})
    top = conc.get("top_signatures", [])
    coverage = conc.get("top_3_coverage", 0)
    
    if mode == "DESCRIPTIVE":
        if len(top) == 0:
            return (
                "No patterns concentrate in this sample—structure is distributed across unique shapes. "
                "This might mean high variety, or simply that the sample is too small for patterns to repeat. "
                "Pattern concentration becomes meaningful when we have enough sentences for shapes to recur; "
                "with limited material, absence of concentration is expected rather than significant."
            )
        return (
            f"The most common structural pattern appears {top[0].get('count', 0)} time(s) in this sample. "
            f"Together, your top patterns account for {coverage:.0%} of sentences. "
            f"Pattern concentration reveals whether certain structures dominate your writing or spread evenly. "
            f"High concentration means a few shapes do most of the work; low concentration means variety rules. "
            f"Neither is inherently better—consistency can create rhythm while variety prevents monotony."
        )
    else:  # REFLECTIVE
        if coverage > 0.8:
            return (
                f"Your top structural patterns cover {coverage:.0%} of this sample—strong concentration. "
                f"This means a few sentence shapes are doing most of the work, recurring throughout the writing. "
                f"Such consistency creates a recognizable rhythm; readers come to expect certain shapes and are oriented by them. "
                f"The question is whether this concentration serves your purpose. "
                f"In some contexts, structural consistency reinforces message; in others, deliberate variation might open new possibilities. "
                f"If you're curious, try rewriting a few sentences in deliberately different structures and notice what shifts."
            )
        elif coverage > 0.5:
            return (
                f"Your top patterns account for {coverage:.0%} of sentences—a balance between habit and variation. "
                f"Some shapes recur, establishing a kind of structural baseline, while others appear only once. "
                f"This balance often characterizes flexible writing: you have go-to structures but aren't locked into them. "
                f"The patterns that repeat likely reflect what feels natural; the ones that don't might be stretches or experiments. "
                f"Noticing your most common shapes can help you recognize when you're on autopilot and when you're reaching for something new."
            )
        else:
            return (
                f"No single pattern dominates this sample—your top shapes cover only {coverage:.0%} of sentences. "
                f"This suggests wide distribution rather than structural habit. "
                f"Either you're naturally varied in how you build sentences, or this particular piece called for diverse shapes. "
                f"Low concentration can feel lively or restless, depending on context. "
                f"If you wanted more consistency, you might pick one or two shapes and practice using them repeatedly. "
                f"If you prefer variety, you're already there—at least in this sample."
            )


def _generate_explanation_output_05(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 05: What's Left Unsaid."""
    zero = metrics.get("zero_event_presence", {})
    count = zero.get("count", 0)
    rate = zero.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return (
                "No zero events appear in this sample—no ellipses, dashes, or other markers of pause or omission. "
                "Zero events signal places where meaning trails off, hesitates, or leaves room for the reader. "
                "Their absence means sentences complete their thoughts without visible gaps. "
                "This is descriptive, not evaluative: different writing contexts call for different amounts of such markers."
            )
        return (
            f"This sample contains {count} zero event(s), appearing at a rate of {rate:.2f} per sentence. "
            f"Zero events include ellipses (... or …), em-dashes used as interruptions, and similar markers of pause or omission. "
            f"They represent places where meaning hesitates, trails off, or creates space. "
            f"Their presence signals a particular texture—moments where the writing acknowledges incompleteness or invites inference."
        )
    else:  # REFLECTIVE
        if count == 0:
            return (
                "Your writing moves without hesitation markers—no ellipses, no trailing pauses, no visible gaps. "
                "This creates a sense of completeness: each sentence says what it says and moves on. "
                "Some contexts call for this directness; the writing proceeds without asking readers to fill in blanks. "
                "In other contexts, pauses and omissions can be powerful—what's left unsaid sometimes speaks loudest. "
                "If you wanted to experiment, try adding a single ellipsis or dash-interrupted thought and notice what it does to the rhythm."
            )
        elif rate < 0.3:
            return (
                f"A few pause markers appear in your writing ({count} total, rate {rate:.2f})—moments where meaning hesitates or trails off. "
                f"These zero events create small pockets of silence within the text. "
                f"An ellipsis might suggest a thought unfinished; a dash might mark an interruption. "
                f"Used sparingly, as here, they punctuate the prose without overwhelming it. "
                f"These are places where you've invited the reader to pause, perhaps to infer what isn't said explicitly."
            )
        else:
            return (
                f"Pauses and gaps appear often in this sample ({count} total, rate {rate:.2f}). "
                f"Your writing makes frequent use of zero events—places where meaning trails off or gets interrupted. "
                f"This creates a particular texture: the prose acknowledges its own incompleteness, leaving room for inference. "
                f"In some contexts this feels contemplative or honest; in others it might feel hesitant. "
                f"The effect depends on what you're after. If these pauses feel right, they're doing their work. "
                f"If they feel excessive, you might try filling some in and seeing what changes."
            )


def _generate_explanation_output_06(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 06: Connective Moves."""
    op = metrics.get("operator_event_presence", {})
    count = op.get("count", 0)
    rate = op.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return (
                "No operator events appear in this sample—no slashes, ampersands, or similar connective symbols. "
                "Operators compress meaning by linking alternatives (and/or, either/or) or combining terms (research & development). "
                "Their absence means connections are spelled out in words rather than symbolized. "
                "This is neither good nor bad; it simply describes how this particular sample handles linkage."
            )
        return (
            f"This sample contains {count} operator event(s) at a rate of {rate:.2f}. "
            f"Operators include slashes (/), ampersands (&), plus signs, and similar symbols that connect or relate terms. "
            f"They're a form of structural shorthand: 'and/or' compresses 'and or or' into a symbol. "
            f"Their presence indicates a certain conciseness or perhaps technical register."
        )
    else:  # REFLECTIVE
        if count == 0:
            return (
                "Your writing handles connections through words rather than symbols—no slashes, ampersands, or similar operators. "
                "This creates a particular texture: relationships between terms are spelled out rather than compressed. "
                "In formal or literary writing, this is often the norm. In technical or business writing, operators are common shortcuts. "
                "Neither approach is better; they suit different contexts and create different effects. "
                "If you wanted to experiment, try replacing a phrase like 'this or that' with 'this/that' and notice how it reads."
            )
        else:
            return (
                f"Connective symbols appear in your writing ({count} total)—slashes, ampersands, or similar operators. "
                f"These marks compress meaning: they link alternatives, combine terms, or signal relationships without spelling them out. "
                f"Their presence can signal efficiency or technical register, depending on context. "
                f"In some writing, operators feel natural; in others, they might feel too compact or informal. "
                f"Pay attention to where you use them and whether they serve clarity or create ambiguity."
            )


def _generate_explanation_output_07(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 07: Layered Meaning."""
    scope = metrics.get("scope_event_presence", {})
    count = scope.get("count", 0)
    rate = scope.get("rate", 0)
    
    if mode == "DESCRIPTIVE":
        if count == 0:
            return (
                "No scope events appear in this sample—no parentheses, brackets, or quotations creating nested meaning. "
                "Scope events add layers: a thought within a thought, a quoted phrase, an aside. "
                "Their absence means sentences proceed without such nesting. "
                "This describes the structural texture without evaluating it."
            )
        return (
            f"This sample contains {count} scope event(s) at a rate of {rate:.2f}. "
            f"Scope events include parenthetical asides, bracketed content, and quoted material—structures that create layers within sentences. "
            f"They represent moments where meaning nests: a thought contains another thought, a sentence holds a quotation. "
            f"The rate indicates how often such layering occurs in this sample."
        )
    else:  # REFLECTIVE
        if count == 0:
            return (
                "Your sentences proceed without nested layers—no parenthetical asides, no bracketed clarifications, no embedded quotes. "
                "This creates a linear reading experience: one thought follows another without detours. "
                "Some writers use layering extensively to qualify, digress, or add nuance; others keep things streamlined. "
                "Neither is inherently better. If you wanted to experiment, try adding a single parenthetical aside to one sentence "
                "and notice how it changes the rhythm—it's like adding a whispered comment in the middle of speech."
            )
        elif rate < 0.5:
            return (
                f"Some layering appears in your writing ({count} scope events)—moments where meaning nests within meaning. "
                f"A parenthetical aside, a quoted phrase, a bracketed clarification: these create texture and depth. "
                f"Used occasionally, as here, they add nuance without overwhelming the main line of thought. "
                f"These are places where you've chosen to include extra information or signal that something is being quoted or qualified. "
                f"Readers enter a different space briefly, then return to the main sentence."
            )
        else:
            return (
                f"Layering is prominent in this sample ({count} scope events, rate {rate:.2f}). "
                f"Parentheses, brackets, and quotations create a textured reading experience—thoughts within thoughts, "
                f"frequent detours and qualifications. "
                f"This can feel rich and nuanced, or it can feel crowded, depending on execution and context. "
                f"If the layers feel purposeful, they're doing their work. If they feel excessive, "
                f"try flattening a few and seeing whether the main thoughts stand stronger on their own."
            )


def _generate_explanation_output_08(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 08: Complexity at a Glance."""
    density = metrics.get("structural_density", {})
    total = density.get("total_events", 0)
    avg = density.get("mean_events_per_sentence", 0)
    
    if mode == "DESCRIPTIVE":
        return (
            f"This sample contains {total} structural event(s) total, averaging {avg:.2f} per sentence. "
            f"Structural density aggregates all event types—pauses, operators, and scope markers. "
            f"It offers a rough measure of how 'busy' sentences are structurally, independent of length or content. "
            f"Higher density means more structural features per sentence; lower density means cleaner, simpler shapes. "
            f"This is a descriptive measure, not a quality judgment."
        )
    else:  # REFLECTIVE
        if avg < 0.3:
            return (
                f"Structural density is low in this sample ({total} events total, {avg:.2f} per sentence). "
                f"Your sentences carry minimal structural decoration—few pauses, operators, or nested layers. "
                f"This creates a clean, direct texture: content speaks without much structural scaffolding. "
                f"Some writing benefits from this clarity; readers move through without navigating complexity. "
                f"Other writing might benefit from more structural features to create rhythm or signal nuance. "
                f"The question is whether this simplicity serves your purpose or whether adding some texture would help."
            )
        elif avg < 1.0:
            return (
                f"Structural density is moderate ({total} events, {avg:.2f} per sentence). "
                f"Some sentences carry structural features; others proceed cleanly. "
                f"This creates a varied texture—moments of complexity punctuate stretches of simplicity. "
                f"Such modulation often characterizes readable prose: enough structure to create interest, "
                f"not so much that readers get lost. "
                f"Pay attention to where density clusters and where it's absent; those patterns reveal something about how you build emphasis."
            )
        else:
            return (
                f"Structural density is high ({total} events total, averaging {avg:.2f} per sentence). "
                f"Your sentences carry significant structural weight—pauses, operators, nested layers. "
                f"This creates a complex reading experience: readers navigate not just content but form. "
                f"Dense structure can feel literary, technical, or overwrought, depending on execution. "
                f"If the complexity feels purposeful, it's doing its work. If it feels like clutter, "
                f"try simplifying a few sentences and see whether the ideas land more clearly."
            )


def _generate_explanation_output_09(metrics: Dict[str, Any], mode: str) -> str:
    """Generate explanation for Output 09: How Your Patterns Combine."""
    coop = metrics.get("event_co_occurrence_profile", {})
    dist = coop.get("distribution", {})
    
    # Find dominant combination
    dominant = max(dist.items(), key=lambda x: x[1]) if dist else ("none", 0)
    
    if mode == "DESCRIPTIVE":
        if not dist or dominant[0] == "none":
            return (
                "Most sentences in this sample contain no structural events to combine. "
                "Co-occurrence tracks which event types appear together within sentences: zero events, operators, and scope markers. "
                "When sentences are structurally sparse, there's little to combine. "
                "This describes the distribution without implying it should be otherwise."
            )
        return (
            f"The dominant co-occurrence pattern is '{dominant[0]}' ({dominant[1]} sentences). "
            f"Co-occurrence shows how structural event types combine within sentences. "
            f"Some sentences might have only scope events; others might mix pauses with operators. "
            f"The distribution reveals your combinatorial tendencies—which structural features tend to appear together."
        )
    else:  # REFLECTIVE
        if not dist or dominant[0] == "none":
            return (
                f"Most of your sentences ({dominant[1]} total) contain no structural markers to combine. "
                f"This means content carries meaning without much structural decoration—no pauses, operators, or nested layers. "
                f"Such structural minimalism creates directness: ideas land without navigating complex forms. "
                f"If you wanted to experiment with combination, try adding both a parenthetical aside and a pause marker "
                f"to the same sentence and notice how the texture changes."
            )
        else:
            return (
                f"Your sentences tend toward '{dominant[0]}' combinations ({dominant[1]} sentences). "
                f"This reveals which structural features you combine and which you keep separate. "
                f"Some writers mix everything; others keep pause markers in some sentences, scope in others. "
                f"These combinatorial habits shape reading experience in subtle ways. "
                f"Noticing your tendencies lets you choose when to follow them and when to try something different."
            )


def _generate_explanation_output_10(metrics: Dict[str, Any], mode: str, status: str) -> str:
    """Generate explanation for Output 10: Your Structural Codes."""
    if status == "NOT_AVAILABLE":
        return (
            "Ticker codes require at least two sentences to display meaningfully. "
            "These codes represent word-level structural positions—a finer-grained analysis than sentence-level patterns. "
            "With more material, we could show how you use different word types and positions, "
            "revealing rhythms beneath the surface of content."
        )
    
    ticker = metrics.get("ticker_profile", {})
    unique = ticker.get("unique_codes", 0)
    total = ticker.get("total_positions", 0)
    
    if mode == "DESCRIPTIVE":
        return (
            f"This sample uses {unique} distinct structural code(s) across {total} word positions. "
            f"Ticker codes represent grammatical categories at each position in each sentence. "
            f"They're like a skeleton beneath the flesh of words—the structural frame that carries meaning. "
            f"The ratio of unique codes to total positions indicates variety at the word level."
        )
    else:  # REFLECTIVE
        return (
            f"Your writing employs {unique} distinct structural codes across {total} positions. "
            f"These codes form a kind of fingerprint—not of what you say, but of how you build sentences at the word level. "
            f"Different codes represent different grammatical functions: articles, prepositions, verbs, nouns. "
            f"The patterns here reveal micro-rhythms: which positions carry which functions, how variety distributes. "
            f"This is the most granular level of structural analysis, revealing habits invisible to the conscious writer."
        )


# =============================================================================
# Expanded Insights (2-3 insights, longer)
# =============================================================================

def _generate_insights(output_id: str, metrics: Dict[str, Any], mode: str) -> List[str]:
    """Generate 2-3 example insights for an output."""
    
    insights_templates = {
        "output_01": {
            "DESCRIPTIVE": [
                "This sample provides the material for description, not deep pattern analysis.",
                "More sentences would reveal whether structural features here are typical or exceptional.",
                "What appears in these sentences describes this moment of writing, not necessarily your broader habits.",
            ],
            "REFLECTIVE": [
                "The sample is large enough to see patterns stabilizing—shapes that recur start to feel like habits.",
                "If you wrote more on the same topic, we'd see whether these patterns persist or shift.",
                "Future rounds could compare this sample to others, revealing consistency or variation across contexts.",
            ],
        },
        "output_02": {
            "DESCRIPTIVE": [
                "Sentence length is computed from available words and sentences.",
                "The average reflects this sample specifically; other writing might differ.",
                "Length shapes pacing—shorter sentences quicken reading, longer ones slow it.",
            ],
            "REFLECTIVE": [
                "Your average sentence length creates a particular reading rhythm.",
                "Experimenting with deliberately shorter or longer sentences could reveal new textures.",
                "In some contexts, varying length within a piece creates emphasis; uniform length creates consistency.",
            ],
        },
        "output_03": {
            "DESCRIPTIVE": [
                "Structural variety measures unique shapes against total sentences.",
                "A high ratio means many distinct shapes; a low ratio means repetition.",
                "This describes the distribution without inferring habit from limited data.",
            ],
            "REFLECTIVE": [
                "The structural variety here suggests your range in this sample.",
                "Deliberately varying structure can prevent monotony; deliberate repetition can build rhythm.",
                "Future exercises might focus on either expanding variety or deepening consistency.",
            ],
        },
        "output_04": {
            "DESCRIPTIVE": [
                "Pattern concentration shows which shapes dominate, if any.",
                "Top patterns are ranked by frequency in this sample.",
                "Low concentration means variety; high concentration means repetition.",
            ],
            "REFLECTIVE": [
                "Your most common patterns are your structural defaults—what comes naturally.",
                "Noticing these can help you recognize when you're on autopilot.",
                "Less common patterns might be where you're stretching or experimenting.",
            ],
        },
        "output_05": {
            "DESCRIPTIVE": [
                "Zero events count pauses, ellipses, and markers of omission.",
                "Their rate shows frequency relative to sentence count.",
                "Presence or absence of pauses describes structural texture.",
            ],
            "REFLECTIVE": [
                "Pauses create space for what's unsaid—meaning that readers infer rather than receive.",
                "Heavy use of zero events can feel contemplative; absence can feel decisive.",
                "If you added one pause marker to a sentence without pauses, what would change?",
            ],
        },
        "output_06": {
            "DESCRIPTIVE": [
                "Operators include slashes, ampersands, and connective symbols.",
                "Their count reflects shorthand connections in this sample.",
                "Different contexts call for different amounts of such compression.",
            ],
            "REFLECTIVE": [
                "Operators compress relationships into symbols—efficient but sometimes ambiguous.",
                "Their presence often signals technical or business register.",
                "Spelling out what operators compress can clarify meaning or add nuance.",
            ],
        },
        "output_07": {
            "DESCRIPTIVE": [
                "Scope events include parentheses, brackets, and quotations.",
                "They create nested meaning—thoughts within thoughts.",
                "The rate shows how often layering occurs.",
            ],
            "REFLECTIVE": [
                "Parenthetical asides add nuance but can interrupt flow.",
                "Heavy layering creates texture; light layering keeps things streamlined.",
                "Try reading your sentences aloud, including the parentheticals, and notice the rhythm.",
            ],
        },
        "output_08": {
            "DESCRIPTIVE": [
                "Structural density sums all event types into one measure.",
                "The average shows events per sentence, regardless of sentence length.",
                "Higher density means more structural activity; lower means cleaner shapes.",
            ],
            "REFLECTIVE": [
                "Dense structure asks more of readers—more to navigate beyond content.",
                "Sparse structure lets content carry the weight.",
                "Modulating density creates emphasis: a dense sentence after sparse ones stands out.",
            ],
        },
        "output_09": {
            "DESCRIPTIVE": [
                "Co-occurrence tracks which event types appear together.",
                "The distribution shows how structural features combine.",
                "Different combinations create different textures.",
            ],
            "REFLECTIVE": [
                "Some combinations feel natural; others create productive tension.",
                "Your combinatorial habits are part of your structural signature.",
                "Deliberately mixing features you usually keep separate can yield surprises.",
            ],
        },
        "output_10": {
            "DESCRIPTIVE": [
                "Ticker codes represent word-level structural positions.",
                "Unique codes show grammatical variety at the micro level.",
                "This is the most granular structural measure.",
            ],
            "REFLECTIVE": [
                "These codes reveal rhythms beneath conscious awareness.",
                "Word-level patterns often reflect deeply ingrained habits.",
                "Advanced exercises might involve manipulating these codes directly.",
            ],
        },
    }
    
    templates = insights_templates.get(output_id, {})
    mode_insights = templates.get(mode, templates.get("DESCRIPTIVE", []))
    
    if not mode_insights:
        return [
            "This metric reflects structural patterns in your writing.",
            "More material would reveal whether these patterns persist.",
        ]
    
    return mode_insights[:3]  # Return up to 3 insights


# =============================================================================
# Main Generator
# =============================================================================

def generate_phase2(phase1: Dict[str, Any], high_intent_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate Phase-2 UX output from Phase-1 compute output.
    
    Args:
        phase1: Phase-1 compute output with 'outputs' containing metrics
        high_intent_profile: Optional High-Intent profile for awareness
        
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
    
    # Generator functions for each output
    generators = {
        "output_01": lambda: _generate_explanation_output_01(metrics, mode),
        "output_02": lambda: _generate_explanation_output_02(metrics, mode),
        "output_03": lambda: _generate_explanation_output_03(metrics, mode),
        "output_04": lambda: _generate_explanation_output_04(metrics, mode),
        "output_05": lambda: _generate_explanation_output_05(metrics, mode),
        "output_06": lambda: _generate_explanation_output_06(metrics, mode),
        "output_07": lambda: _generate_explanation_output_07(metrics, mode),
        "output_08": lambda: _generate_explanation_output_08(metrics, mode),
        "output_09": lambda: _generate_explanation_output_09(metrics, mode),
        "output_10": lambda: _generate_explanation_output_10(metrics, mode, output_10_status),
    }
    
    # Generate outputs
    outputs = {}
    for defn in OUTPUT_DEFINITIONS:
        output_id = defn["output_id"]
        
        # Generate explanation
        explanation = generators.get(output_id, lambda: "")()
        
        # Optionally expand with LLM
        if is_llm_available():
            explanation, _ = expand_content(
                explanation,
                {"metrics": metrics, "mode": mode, "output_id": output_id},
                "phase2_explanation",
                "medium"
            )
        
        # Generate insights
        insights = _generate_insights(output_id, metrics, mode)
        
        # Build output
        outputs[output_id] = {
            "output_id": output_id,
            "name_user_facing": defn["name_user_facing"],
            "explanation": explanation,
            "example_insights": insights,
            "status": output_10_status if output_id == "output_10" else "AVAILABLE",
        }
    
    return {
        "phase2_version": PHASE2_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase1_version": phase1.get("phase1_version", "unknown"),
        "presentation_mode": mode,
        "outputs": outputs,
    }


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Demo with mock Phase-1 output
    mock_phase1 = {
        "phase1_version": "1.0.0",
        "outputs": {
            "sentence_count": {"count": 5},
            "token_volume": {"total_tokens": 45, "mean_tokens_per_sentence": 9.0},
            "structural_variety": {"unique_signatures": 4, "variety_ratio": 0.8},
            "signature_concentration": {"top_signatures": [{"sig": "3|4|2|1|4", "count": 2}], "top_3_coverage": 0.4},
            "zero_event_presence": {"count": 1, "rate": 0.2},
            "operator_event_presence": {"count": 0, "rate": 0.0},
            "scope_event_presence": {"count": 2, "rate": 0.4},
            "structural_density": {"total_events": 3, "mean_events_per_sentence": 0.6},
            "event_co_occurrence_profile": {"distribution": {"none": 2, "scope_only": 2, "zero_only": 1}},
            "ticker_profile": {"unique_codes": 12, "total_positions": 45},
        }
    }
    
    print("Phase-2 Generator v0.2.0 Demo")
    print("=" * 60)
    
    result = generate_phase2(mock_phase1)
    
    print(f"Presentation mode: {result['presentation_mode']}")
    print(f"Version: {result['phase2_version']}")
    print()
    
    for output_id, output in result['outputs'].items():
        print(f"--- {output['name_user_facing']} ---")
        print(f"Explanation ({len(output['explanation'])} chars):")
        print(output['explanation'][:200] + "..." if len(output['explanation']) > 200 else output['explanation'])
        print(f"Insights: {len(output['example_insights'])}")
        print()
