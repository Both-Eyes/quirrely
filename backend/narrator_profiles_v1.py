#!/usr/bin/env python3
"""
LNCP Narrator Profile Sketches v1.0

Generates personalized narrator profiles based on cross-mode similarity clusters
and individual writing metrics.
"""

# =============================================================================
# CLUSTER DEFINITIONS
# =============================================================================

MARKER_CLUSTERS = {
    "SPARSE": ["MINIMAL", "POETIC", "ASSERTIVE", "PARALLEL", "CONVERSATIONAL"],
    "MODERATE": ["INTERROGATIVE", "PARENTHETICAL"],
    "DENSE": ["DENSE", "HEDGED", "LONGFORM"],
}

COMPLEXITY_CLUSTERS = {
    "SIMPLE": ["MINIMAL", "ASSERTIVE", "PARALLEL", "CONVERSATIONAL"],
    "MODERATE": ["POETIC", "INTERROGATIVE", "PARENTHETICAL"],
    "COMPLEX": ["DENSE", "HEDGED", "LONGFORM"],
}

REGISTER_CLUSTERS = {
    "FORMAL": ["DENSE", "POETIC", "INTERROGATIVE", "HEDGED", "PARENTHETICAL", "LONGFORM"],
    "INFORMAL": ["MINIMAL", "ASSERTIVE", "PARALLEL", "CONVERSATIONAL"],
}

# =============================================================================
# PRIMARY MODE PROFILES
# =============================================================================

MODE_PROFILES = {
    "MINIMAL": {
        "title": "The Quiet Observer",
        "essence": "You write like someone watching rain through a window—present, patient, unhurried.",
        "sketch": """You let silence do the heavy lifting. Where others explain, you simply show. Your sentences land like footsteps in snow: distinct, deliberate, then absorbed into stillness.

You trust your reader. You don't hold their hand through every implication or spell out what the moment means. The door opens. Light comes in. That's enough.

There's a kind of confidence in this restraint—not the loud confidence of assertion, but the quieter kind that comes from knowing that not everything needs to be said to be understood. Your writing breathes. It leaves room for the reader to sit with what's there, rather than being told what to feel about it.

This is prose that accumulates meaning through accumulation itself. Three short sentences can carry the weight of a paragraph, if they're the right three sentences. Yours often are.""",
        "strengths": [
            "Economy of language",
            "Trust in the reader",
            "Atmospheric precision",
            "Emotional restraint that amplifies impact"
        ],
        "growth_edges": [
            "When complexity genuinely requires it, you might explore longer, more subordinated structures",
            "Consider when a moment deserves more explicit emotional excavation",
            "Experiment with hedging—not as weakness, but as intellectual honesty"
        ],
        "writing_ancestors": "Hemingway, Carver, early Didion, Amy Hempel"
    },
    
    "DENSE": {
        "title": "The Layered Thinker",
        "essence": "You write like someone who sees the asterisks, the footnotes, the 'yes, buts' hiding inside every claim.",
        "sketch": """Your mind doesn't move in straight lines—it spirals, qualifies, circles back. And your prose follows. You're the writer who can't say 'it was raining' without wondering (or at least noting) whether 'rain' is even the right word, whether your perception of wetness is trustworthy, whether the whole category of weather is beside the point.

This isn't indecision. It's intellectual honesty. You see the layers—the ways any statement is both true and incomplete, the ways certainty hides assumptions. Your parentheticals aren't digressions; they're the real argument, tucked inside what looks like an aside.

The reader who follows you through these nested thoughts is rewarded with something richer than simple declarations could provide. They're getting your actual thinking process, not the cleaned-up summary.

The risk, of course, is that the layers obscure the core. But at your best, the density isn't fog—it's depth.""",
        "strengths": [
            "Intellectual nuance",
            "Honest representation of complex thought",
            "Rich epistemic texture",
            "Resistance to false simplicity"
        ],
        "growth_edges": [
            "Practice finding the one thing you actually mean, underneath all the qualifications",
            "Let some sentences be simple—contrast makes density more effective",
            "Trust that readers can hold uncertainty without constant reminders"
        ],
        "writing_ancestors": "David Foster Wallace, Zadie Smith, Maggie Nelson, Geoff Dyer"
    },
    
    "POETIC": {
        "title": "The Fragment Weaver",
        "essence": "You write at the edges of language—where grammar bends and meaning happens in the spaces between.",
        "sketch": """You've discovered something that prose writers sometimes forget: the line break, the slash, the ampersand aren't just punctuation. They're instruments. They change how time moves through a sentence. They make the reader pause where you want them to pause, breathe where you want them to breathe.

Your writing doesn't explain—it evokes. You trust in juxtaposition, in the electricity that jumps between fragments. Light & shadow & the space between. The meaning isn't in any single word; it's in the constellation they form together.

This is writing that asks to be read slowly, maybe aloud. It rewards attention. It falls apart if skimmed—but that's a feature, not a bug. You're selecting for readers who will meet you where you are.

The risk is preciousness, or obscurity for its own sake. But at your best, the fragmentation isn't difficulty—it's precision. You've found the exact shape of a thought that prose couldn't hold.""",
        "strengths": [
            "Sonic awareness",
            "Visual composition on the page",
            "Meaning through juxtaposition",
            "Controlled ambiguity"
        ],
        "growth_edges": [
            "Ensure fragmentation serves meaning, not just aesthetics",
            "Practice conventional prose to keep the choice intentional",
            "Consider when clarity might be its own kind of poetry"
        ],
        "writing_ancestors": "Anne Carson, Claudia Rankine, Maggie Nelson, Ocean Vuong, Jenny Offill"
    },
    
    "INTERROGATIVE": {
        "title": "The Questioner",
        "essence": "You write in questions because you've learned that the asking often matters more than the answering.",
        "sketch": """Your prose leans forward. It wonders. It invites the reader into uncertainty rather than handing them conclusions. 'Why do we wait?' you ask, and the reader finds themselves actually wondering—actually pausing to consider their own waiting, their own reasons.

This is generous writing. You're not performing knowledge; you're sharing curiosity. You're saying: I don't know either. Let's think about this together.

Questions create a different relationship with the reader than statements do. Statements position you as the authority, the reader as the recipient. Questions make you collaborators in meaning-making. Both of you are looking at the same puzzle, turning it over together.

The risk is that questions can become evasive—a way of never committing to anything, of seeming deep while saying nothing. But at your best, your questions aren't rhetorical dodges. They're genuine openings. They leave the reader changed.""",
        "strengths": [
            "Reader engagement",
            "Intellectual humility",
            "Invitational tone",
            "Productive uncertainty"
        ],
        "growth_edges": [
            "Practice committing to answers when you have them",
            "Balance inquiry with assertion—questions land differently after a firm statement",
            "Distinguish between generative questions and evasive ones"
        ],
        "writing_ancestors": "James Baldwin, Rebecca Solnit, Ta-Nehisi Coates, Sarah Manguso"
    },
    
    "ASSERTIVE": {
        "title": "The Direct Voice",
        "essence": "You write like you mean it. No hedging. No hiding. The sentence says what it says.",
        "sketch": """There's power in directness, and you know how to wield it. Your sentences don't apologize for themselves. They don't soften their edges with 'perhaps' or 'it seems.' They arrive. They land. They trust the reader to receive them.

This is confident writing—not arrogant, but clear-eyed. You've thought about what you believe, and you're willing to say it plainly. In a world of qualified statements and endless caveats, there's something almost radical about prose that just... states things.

Short sentences. Clear claims. The cumulative effect is momentum. The reader moves through your writing like walking downhill—the energy carries them forward.

The risk is that certainty can shade into oversimplification, that directness can become dismissiveness. But at your best, your assertions aren't bluster. They're earned. They've been tested. They've survived the qualifications and emerged intact.""",
        "strengths": [
            "Clarity",
            "Momentum",
            "Memorability",
            "Conviction that invites response"
        ],
        "growth_edges": [
            "Practice acknowledging complexity without losing directness",
            "Explore hedging as precision rather than weakness",
            "Let some sentences breathe—rhythm needs variation"
        ],
        "writing_ancestors": "Joan Didion, James Baldwin, George Orwell, Annie Dillard"
    },
    
    "HEDGED": {
        "title": "The Careful Scholar",
        "essence": "You write with the precision of someone who knows that every claim hides assumptions, and you want them visible.",
        "sketch": """Your prose is meticulous. 'It seems possible, perhaps even likely'—that construction isn't vagueness. It's accuracy. You're saying exactly how much confidence you have, no more, no less.

This is academic honesty extended into prose style. You've been trained (or trained yourself) to see the gaps in every argument, the ways evidence can mislead, the difference between correlation and causation. And you bring all of that to your sentences.

The effect is a kind of intellectual humility made structural. The reader knows where you're certain and where you're speculating. They can calibrate their own confidence accordingly. You're modeling good epistemic hygiene.

The risk is that over-qualification can drain the life from prose—that endless hedging can make a reader wonder if you believe anything at all. But at your best, the hedges aren't evasions. They're invitations to think carefully alongside you.""",
        "strengths": [
            "Epistemic precision",
            "Trustworthiness",
            "Modeling careful reasoning",
            "Appropriate uncertainty"
        ],
        "growth_edges": [
            "Practice strategic assertion—sometimes the hedge undermines the point",
            "Vary sentence structure to keep hedged prose from becoming monotonous",
            "Trust that readers can handle unqualified claims when they're warranted"
        ],
        "writing_ancestors": "Academic writing at its best, Susan Sontag, Adam Phillips"
    },
    
    "PARENTHETICAL": {
        "title": "The Aside Artist",
        "essence": "You write in layers—main text and subtext, the said and the whispered, all happening at once.",
        "sketch": """Your sentences have rooms within rooms. The parenthetical isn't an interruption; it's where the real thinking often happens. (You know this. You've been doing it your whole life—the comment under your breath, the thought too true for the main conversation.)

This style makes prose feel conversational in a specific way: the way you'd tell a story to a friend, constantly adding context, adjusting, noting the things that complicate the simple version. 'The meeting (which nobody wanted) ran long (as usual)'—the official story and the real story, nested together.

The effect is intimacy. The reader feels like they're getting the inside version, the one with the editorial comments left in. They're being trusted with your actual thinking, not just the polished summary.

The risk is that too many asides can swamp the main current. But at your best, the parentheticals aren't clutter. They're depth. They're the proof that you're thinking in real-time, not reciting.""",
        "strengths": [
            "Intimacy with the reader",
            "Layered meaning",
            "Conversational authenticity",
            "Complexity without losing the thread"
        ],
        "growth_edges": [
            "Practice integrating asides into the main sentence when they're essential",
            "Reserve parentheticals for genuine additions, not reflexive habit",
            "Experiment with other ways to layer meaning—em-dashes, subordinate clauses"
        ],
        "writing_ancestors": "Nicholson Baker, David Foster Wallace, Lorrie Moore"
    },
    
    "PARALLEL": {
        "title": "The Pattern Maker",
        "essence": "You write in rhythms—repetition that builds, structure that echoes, meaning that accumulates through form.",
        "sketch": """She walked. She stopped. She turned. There's something hypnotic about this, and you know it. The repeated structure isn't laziness; it's music. It's the prose equivalent of a bass line—something steady underneath that lets other elements move.

Parallel structure is ancient. It's Biblical. It's rhetorical. And it works because human brains are pattern-recognition machines. We hear the structure, we anticipate the next iteration, and when it arrives (or when it doesn't), meaning happens.

Your writing has a kind of inevitability to it. Each element prepares the ground for the next. The accumulation isn't just additive—it's multiplicative. Three simple sentences can land harder than one complex one, if they're the right shape.

The risk is monotony—that the pattern becomes predictable, that the reader starts to skim. But at your best, you know when to break the pattern, when the third element needs to be the surprise.""",
        "strengths": [
            "Rhythmic control",
            "Memorable structure",
            "Cumulative power",
            "Formal elegance"
        ],
        "growth_edges": [
            "Practice strategic pattern-breaking—the variation is what makes the pattern land",
            "Explore longer, more complex parallel structures",
            "Balance repetition with variety to avoid hypnosis becoming numbness"
        ],
        "writing_ancestors": "The King James Bible, Lincoln, MLK, Marilynne Robinson"
    },
    
    "LONGFORM": {
        "title": "The Sentence Builder",
        "essence": "You write sentences that unfold like rivers—branching, rejoining, carrying the reader through complexity to clarity.",
        "sketch": """Your sentences have architecture. They're built to hold multiple ideas in relation, to show how one thing connects to another, to trace the actual shape of complicated thinking. Where others might break the thought into pieces, you trust the sentence to hold it whole.

This is ambitious prose. It asks something of the reader—attention, patience, the willingness to follow a thought through its subordinate clauses and participial phrases to wherever it's going. But it rewards that attention with something other structures can't provide: the experience of complex thought as complex thought, not simplified for easier consumption.

There's honesty in this. The world is complicated. Causes are multiple. Context matters. Your sentences acknowledge this structurally, not just semantically. They don't pretend that hard things are simple.

The risk is losing the reader in the branching, asking too much, forgetting that prose needs air. But at your best, your long sentences aren't obstacles. They're vessels. They carry more than short ones could.""",
        "strengths": [
            "Capacity for complexity",
            "Structural mimesis (form matches content)",
            "Intellectual ambition",
            "Rhythmic variation"
        ],
        "growth_edges": [
            "Practice short sentences as contrast—they'll make the long ones land harder",
            "Ensure every clause earns its place",
            "Read aloud to find where readers need breath"
        ],
        "writing_ancestors": "Henry James, Virginia Woolf, William Faulkner, Toni Morrison"
    },
    
    "CONVERSATIONAL": {
        "title": "The Voice in the Room",
        "essence": "You write like you talk—or rather, like the best version of how you talk. Warm, immediate, real.",
        "sketch": """So here's the thing. (See? You just did it.) Your prose has a presence. It feels like someone is actually in the room, telling you this, probably with a coffee in hand and an opinion about everything.

This isn't sloppiness. Conversational prose is hard to do well. It requires an ear for rhythm, a sense of what makes speech feel alive on the page. The fragments. The contractions. The way a sentence can trail off and still land...

The effect is intimacy and accessibility. Readers feel addressed, not lectured at. They feel like they're in on something. The formality barrier comes down, and what's left is just two people thinking together.

The risk is that casual can slide into sloppy, that the voice can overwhelm the content, that what reads as fresh can become a shtick. But at your best, the conversational mode isn't a lack of craft. It's a specific craft—the craft of sounding like yourself, of making the page feel like presence.""",
        "strengths": [
            "Accessibility",
            "Voice",
            "Immediacy",
            "Reader connection"
        ],
        "growth_edges": [
            "Practice modulating register—knowing when to shift toward formality",
            "Ensure substance matches style—casualness can mask thin thinking",
            "Explore how conversational can coexist with complex"
        ],
        "writing_ancestors": "Nora Ephron, David Sedaris, Samantha Irby, Roxane Gay, early Chuck Klosterman"
    },
}


# =============================================================================
# CLUSTER PROFILES (COMBINATIONS)
# =============================================================================

CLUSTER_PROFILES = {
    # Marker + Complexity combinations
    ("SPARSE", "SIMPLE"): {
        "title": "The Minimalist",
        "sketch": """You've found the power in restraint. Simple structures, few markers, maximum impact per word. Your writing is the opposite of decorative—every element earns its place, and what's not there matters as much as what is.

This is prose stripped to essentials. Not because you can't do complexity, but because you've learned that complexity often hides rather than reveals. You trust the reader. You trust silence. You trust that three words can do what thirty can't.""",
    },
    
    ("SPARSE", "MODERATE"): {
        "title": "The Lyricist",
        "sketch": """You write with restraint but not simplicity. Few markers, yet sophisticated structures. There's something musical here—prose that moves in unexpected ways, that achieves complexity through form rather than explanation.

You've discovered that you don't need to tell readers what to think. You can shape their experience through rhythm, through structure, through the space between things.""",
    },
    
    ("MODERATE", "MODERATE"): {
        "title": "The Balanced Voice",
        "sketch": """You've found a middle path—neither stripped bare nor overly dense, neither simple nor byzantine. This is sustainable prose, the kind that can go the distance. It has room to breathe but doesn't waste breath.

There's craft in this balance. It's harder than extremes. You're making constant decisions about what needs marking and what doesn't, what needs subordination and what stands alone.""",
    },
    
    ("DENSE", "COMPLEX"): {
        "title": "The Architect",
        "sketch": """You build cathedrals. Dense with markers, complex in structure, your prose is designed to hold sophisticated ideas in all their difficulty. This is ambitious writing that doesn't apologize for asking something of its reader.

The markers aren't clutter; they're precision. The complexity isn't showing off; it's necessity. Some thoughts can only be held in elaborate structures, and you're building them.""",
    },
    
    # Register combinations
    ("FORMAL", "DENSE"): {
        "title": "The Scholar's Voice",
        "sketch": """Formal register, dense with qualification—you write with academic precision extended into style. Every claim is calibrated, every uncertainty acknowledged. This is trustworthy prose that shows its work.

The formality isn't coldness; it's respect. Respect for the complexity of what you're discussing, respect for the reader's intelligence, respect for the difficulty of knowing anything with certainty.""",
    },
    
    ("INFORMAL", "SPARSE"): {
        "title": "The Friend at the Table",
        "sketch": """Casual and spare—you write like a good conversation. No pretense, no padding. Just what needs to be said, said in a way that feels human. This is writing that connects before it instructs.

The informality isn't a lack of care; it's a choice to prioritize connection. And the sparseness isn't emptiness; it's the discipline to stop when you're done.""",
    },
}


# =============================================================================
# PROFILE GENERATION
# =============================================================================

def get_marker_cluster(mode: str) -> str:
    for cluster, modes in MARKER_CLUSTERS.items():
        if mode in modes:
            return cluster
    return "MODERATE"

def get_complexity_cluster(mode: str) -> str:
    for cluster, modes in COMPLEXITY_CLUSTERS.items():
        if mode in modes:
            return cluster
    return "MODERATE"

def get_register_cluster(mode: str) -> str:
    for cluster, modes in REGISTER_CLUSTERS.items():
        if mode in modes:
            return cluster
    return "FORMAL"


def generate_narrator_profile(primary_mode: str, metrics: dict = None) -> dict:
    """
    Generate a complete narrator profile based on detected mode and metrics.
    
    Args:
        primary_mode: The dominant writing mode detected
        metrics: Optional dict with epistemic_openness, informality_score, etc.
    
    Returns:
        Complete profile dict with title, sketch, strengths, growth edges, etc.
    """
    # Get primary mode profile
    profile = MODE_PROFILES.get(primary_mode, MODE_PROFILES["MINIMAL"]).copy()
    
    # Get cluster memberships
    marker_cluster = get_marker_cluster(primary_mode)
    complexity_cluster = get_complexity_cluster(primary_mode)
    register_cluster = get_register_cluster(primary_mode)
    
    # Add cluster context
    profile["clusters"] = {
        "marker_density": marker_cluster,
        "syntax_complexity": complexity_cluster,
        "register": register_cluster,
    }
    
    # Add cluster combination insights if available
    cluster_key = (marker_cluster, complexity_cluster)
    if cluster_key in CLUSTER_PROFILES:
        profile["cluster_profile"] = CLUSTER_PROFILES[cluster_key]
    
    # Add metric-specific observations if metrics provided
    if metrics:
        observations = []
        
        openness = metrics.get("epistemic_openness", 0.5)
        if openness > 0.7:
            observations.append("Your writing leans toward openness—you prefer possibility to certainty, questions to answers.")
        elif openness < 0.3:
            observations.append("Your writing leans toward closure—you prefer clarity to ambiguity, conviction to hedge.")
        
        informality = metrics.get("informality_score", 0)
        if informality > 1.0:
            observations.append("Your register runs casual—this creates intimacy but watch for when formality would serve better.")
        elif informality < 0.3:
            observations.append("Your register runs formal—this creates authority but watch for when warmth would help.")
        
        density = metrics.get("structural_density_score", 0)
        if density > 1.5:
            observations.append("Your prose is structurally dense—lots happening in each sentence. This rewards attention but demands it too.")
        elif density < 0.5:
            observations.append("Your prose is structurally lean—each sentence does one thing clearly. This is accessible but can feel thin.")
        
        profile["metric_observations"] = observations
    
    return profile


def format_profile_for_display(profile: dict) -> str:
    """Format a narrator profile for text display."""
    lines = []
    
    lines.append("=" * 70)
    lines.append(f"NARRATOR PROFILE: {profile['title']}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"✦ {profile['essence']}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append(profile['sketch'])
    lines.append("")
    
    if "cluster_profile" in profile:
        lines.append("-" * 70)
        lines.append(f"CLUSTER: {profile['cluster_profile']['title']}")
        lines.append("-" * 70)
        lines.append("")
        lines.append(profile['cluster_profile']['sketch'])
        lines.append("")
    
    lines.append("-" * 70)
    lines.append("STRENGTHS")
    lines.append("-" * 70)
    for strength in profile['strengths']:
        lines.append(f"  • {strength}")
    lines.append("")
    
    lines.append("-" * 70)
    lines.append("GROWTH EDGES")
    lines.append("-" * 70)
    for edge in profile['growth_edges']:
        lines.append(f"  → {edge}")
    lines.append("")
    
    if profile.get("metric_observations"):
        lines.append("-" * 70)
        lines.append("BASED ON YOUR METRICS")
        lines.append("-" * 70)
        for obs in profile['metric_observations']:
            lines.append(f"  ○ {obs}")
        lines.append("")
    
    lines.append("-" * 70)
    lines.append("WRITING ANCESTORS")
    lines.append("-" * 70)
    lines.append(f"  {profile['writing_ancestors']}")
    lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("\nLNCP NARRATOR PROFILE SKETCHES")
    print("=" * 70)
    
    # Demo each mode
    for mode in MODE_PROFILES.keys():
        print(f"\n{'='*70}")
        print(f"MODE: {mode}")
        print(f"{'='*70}")
        
        # Generate with sample metrics
        sample_metrics = {
            "MINIMAL": {"epistemic_openness": 0.5, "informality_score": 1.0, "structural_density_score": 0.0},
            "DENSE": {"epistemic_openness": 0.77, "informality_score": 0.3, "structural_density_score": 1.5},
            "POETIC": {"epistemic_openness": 0.5, "informality_score": 0.2, "structural_density_score": 0.6},
            "INTERROGATIVE": {"epistemic_openness": 0.43, "informality_score": 0.4, "structural_density_score": 0.2},
            "ASSERTIVE": {"epistemic_openness": 0.47, "informality_score": 1.0, "structural_density_score": 0.0},
            "HEDGED": {"epistemic_openness": 0.96, "informality_score": 0.0, "structural_density_score": 1.1},
            "PARENTHETICAL": {"epistemic_openness": 1.0, "informality_score": 0.1, "structural_density_score": 1.9},
            "PARALLEL": {"epistemic_openness": 0.5, "informality_score": 1.0, "structural_density_score": 0.0},
            "LONGFORM": {"epistemic_openness": 0.78, "informality_score": 0.2, "structural_density_score": 1.7},
            "CONVERSATIONAL": {"epistemic_openness": 0.53, "informality_score": 1.6, "structural_density_score": 0.1},
        }
        
        profile = generate_narrator_profile(mode, sample_metrics.get(mode, {}))
        print(f"\n{profile['title']}")
        print(f"✦ {profile['essence']}")
        print(f"\nClusters: {profile['clusters']}")
        print(f"Ancestors: {profile['writing_ancestors']}")
