#!/usr/bin/env python3
"""
LNCP User Simulation v1.0
Simulates 100 users per writing mode, runs full analysis, and presents grouped comparisons.
"""

import json
import random
import sys
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import statistics

sys.path.insert(0, '/home/claude/lncp-web-app/backend')
from lncp_orchestrator import quick_analyze

# =============================================================================
# REALISTIC SAMPLE GENERATORS (More varied than test samples)
# =============================================================================

def generate_minimal_sample() -> List[str]:
    """Generate realistic minimal/flat prose from a simulated user."""
    patterns = [
        # Pattern 1: Simple observations
        lambda: [
            f"The {random.choice(['morning', 'evening', 'afternoon', 'day'])} was {random.choice(['quiet', 'still', 'calm', 'gray'])}.",
            f"{random.choice(['She', 'He', 'I'])} {random.choice(['sat', 'stood', 'waited', 'watched'])} {random.choice(['alone', 'silently', 'there', 'nearby'])}.",
            f"{random.choice(['Nothing', 'Something', 'Everything'])} {random.choice(['changed', 'moved', 'happened', 'shifted'])}."
        ],
        # Pattern 2: Sequential actions
        lambda: [
            f"{random.choice(['The door', 'A light', 'The phone', 'The clock'])} {random.choice(['opened', 'flickered', 'rang', 'struck'])}.",
            f"{random.choice(['She', 'He', 'They'])} {random.choice(['turned', 'paused', 'looked up', 'stopped'])}.",
            f"The {random.choice(['moment', 'sound', 'feeling', 'silence'])} {random.choice(['passed', 'faded', 'lingered', 'ended'])}."
        ],
        # Pattern 3: Environmental
        lambda: [
            f"{random.choice(['Rain', 'Snow', 'Light', 'Wind'])} {random.choice(['fell', 'came', 'moved', 'touched'])} the {random.choice(['window', 'ground', 'roof', 'street'])}.",
            f"The {random.choice(['room', 'house', 'air', 'world'])} was {random.choice(['cold', 'warm', 'dark', 'empty'])}.",
            f"{random.choice(['Time', 'Night', 'Day', 'Winter'])} {random.choice(['continued', 'arrived', 'passed', 'waited'])}."
        ],
    ]
    return random.choice(patterns)()


def generate_dense_sample() -> List[str]:
    """Generate dense/nested prose with hedges and certainty markers."""
    openers = [
        "I definitely believed (or thought I did?) that",
        "She was certain—mostly certain, anyway—that",
        "It seemed obvious (perhaps too obvious) that",
        "He must have known (surely he knew?) that",
        "The truth, if there was such a thing, appeared to be that",
        "I knew—or believed I knew—that",
        "It was clear (to me at least) that",
        "She probably understood (though I couldn't be sure) that",
    ]
    
    middles = [
        "the situation—however complicated it seemed—might resolve itself",
        "something had changed (though exactly what remained unclear)",
        "things would work out, or at least that's what I hoped",
        "the answer was hiding somewhere (possibly in plain sight)",
        "nothing was quite as simple as it appeared on the surface",
        "perhaps the whole thing was a misunderstanding after all",
        "certainly there was more to the story than anyone realized",
        "maybe I was wrong about everything (it wouldn't be the first time)",
    ]
    
    closers = [
        "Perhaps that's always how these things work; you know until you don't.",
        "Maybe certainty itself was the illusion I should have questioned.",
        "I definitely had my doubts, though I couldn't articulate them.",
        "The difference, she realized, might not matter in the end.",
        "Whether any of this was true remained, perhaps, beside the point.",
        "Certainly the feeling persisted, whatever its cause might be.",
        "I think we'll never know for certain—and maybe that's okay.",
        "Perhaps understanding was less important than I'd thought.",
    ]
    
    return [
        random.choice(openers) + " " + random.choice(middles) + ".",
        random.choice(middles).capitalize() + ".",
        random.choice(closers)
    ]


def generate_poetic_sample() -> List[str]:
    """Generate poetic/fragmented prose with unconventional structure."""
    patterns = [
        lambda: [
            f"{random.choice(['Light', 'Sound', 'Time', 'Space'])} & {random.choice(['shadow', 'silence', 'memory', 'distance'])} & the {random.choice(['space', 'pause', 'weight', 'edge'])} between—that's where it lives.",
            f"Not in the {random.choice(['saying', 'seeing', 'knowing', 'being'])} / but in the almost-{random.choice(['said', 'seen', 'known', 'felt'])}.",
            f"(And what does '{random.choice(['lives', 'love', 'time', 'truth'])}' even mean here?)"
        ],
        lambda: [
            f"Here / not here / the difference thin as {random.choice(['breath', 'glass', 'paper', 'light'])}.",
            f"She moves through {random.choice(['rooms', 'days', 'years', 'words'])} like {random.choice(['water', 'light', 'smoke', 'music'])} through {random.choice(['fingers', 'windows', 'air', 'time'])}.",
            f"What {random.choice(['stays', 'goes', 'breaks', 'holds'])} & what {random.choice(['goes', 'stays', 'mends', 'releases'])}—who decides?"
        ],
        lambda: [
            f"{random.choice(['Morning', 'Evening', 'Midnight', 'Dawn'])}—or what passes for it—arrives without {random.choice(['announcement', 'warning', 'ceremony', 'fanfare'])}.",
            f"The {random.choice(['day', 'night', 'light', 'dark'])} / the {random.choice(['night', 'day', 'dark', 'light'])} / the {random.choice(['gray', 'blur', 'edge', 'fold'])} between.",
            f"We measure {random.choice(['time', 'love', 'loss', 'distance'])}; it measures us back."
        ],
    ]
    return random.choice(patterns)()


def generate_interrogative_sample() -> List[str]:
    """Generate question-heavy prose."""
    q_templates = [
        "Why do we {verb}?",
        "What makes {noun} feel {adj}?",
        "Where does {noun} go when it {verb}s?",
        "How can {noun} be so {adj}?",
        "Who decides what's {adj}?",
        "When did {noun} become so {adj}?",
        "Is it {adj}, or something else?",
        "Does anyone really {verb}?",
        "Can we ever truly {verb}?",
        "Should we even try to {verb}?",
    ]
    
    verbs = ["wait", "hope", "fear", "love", "forget", "remember", "pretend", "understand", "change", "stay"]
    nouns = ["time", "love", "silence", "distance", "memory", "hope", "fear", "change", "truth", "meaning"]
    adjs = ["important", "real", "lasting", "meaningful", "possible", "necessary", "enough", "clear", "certain", "worth it"]
    
    questions = []
    for _ in range(3):
        template = random.choice(q_templates)
        q = template.format(
            verb=random.choice(verbs),
            noun=random.choice(nouns),
            adj=random.choice(adjs)
        )
        questions.append(q)
    
    return questions


def generate_assertive_sample() -> List[str]:
    """Generate confident, declarative prose."""
    assertions = [
        "This is how it works.", "You show up.", "Results follow.",
        "There are no shortcuts.", "The work is the work.", "Accept it.",
        "Action beats intention.", "Always.", "No exceptions.",
        "Fear is a liar.", "Ignore it.", "Move forward.",
        "Discipline creates freedom.", "Trust the process.", "Stay consistent.",
        "Words mean nothing.", "Actions prove everything.", "Watch closely.",
        "The past is dead.", "Only now matters.", "Use it wisely.",
        "Failure teaches.", "Success flatters.", "Learn from both.",
        "Boundaries matter.", "Enforce them.", "Protect your energy.",
        "Sleep is essential.", "Rest enables performance.", "Prioritize it.",
        "Quality beats quantity.", "Every time.", "Without exception.",
        "Focus multiplies effort.", "Eliminate distractions.", "Do the work.",
    ]
    
    # Pick 3 related assertions
    start = random.randint(0, len(assertions) - 3)
    return assertions[start:start + 3]


def generate_hedged_sample() -> List[str]:
    """Generate heavily qualified academic-style prose."""
    openers = [
        "It seems possible, perhaps even likely, that",
        "The evidence appears to suggest, tentatively at least, that",
        "One might reasonably argue, with some caveats, that",
        "There is arguably some indication, however preliminary, that",
        "It could be the case, though perhaps not certainly, that",
    ]
    
    claims = [
        "the observed effects might be attributable to several factors",
        "further investigation would presumably be needed to clarify matters",
        "the relationship, while suggestive, remains somewhat unclear",
        "additional research could potentially illuminate the underlying dynamics",
        "the preliminary findings, while interesting, should be interpreted cautiously",
    ]
    
    closers = [
        "Further research would presumably be needed to establish causality with any confidence.",
        "These findings should probably be interpreted with appropriate caution and skepticism.",
        "One should perhaps consider alternative explanations before drawing firm conclusions.",
        "The matter remains, arguably, somewhat unresolved pending additional investigation.",
        "A balanced and nuanced view would seem to be warranted given the current evidence.",
    ]
    
    return [
        random.choice(openers) + " " + random.choice(claims) + ".",
        random.choice(openers) + " " + random.choice(claims) + ".",
        random.choice(closers)
    ]


def generate_parenthetical_sample() -> List[str]:
    """Generate prose with heavy parenthetical asides."""
    templates = [
        "The {event} ({detail1}) {verb} ({detail2}), and by the end ({timing}) we had {outcome}.",
        "{person} ({description}) seemed {emotion}.",
        "The {object} ({qualifier}, if I remember correctly) would have to {action}.",
    ]
    
    events = ["meeting", "conversation", "presentation", "interview", "discussion"]
    detail1s = ["which nobody wanted", "originally scheduled for Tuesday", "the third one this week", "held in the small room"]
    verbs = ["ran long", "ended abruptly", "went surprisingly well", "took an unexpected turn"]
    detail2s = ["as usual", "despite our best efforts", "to everyone's relief", "against all odds"]
    timings = ["around 4pm", "much later than expected", "after what felt like hours", "just before dinner"]
    outcomes = ["decided to postpone", "reached a tentative agreement", "agreed to disagree", "scheduled another one"]
    
    persons = ["Sarah", "The manager", "My colleague", "The director"]
    descriptions = ["our team lead", "a veteran of such situations", "usually unflappable", "new to the company"]
    emotions = ["relieved", "frustrated", "surprisingly calm", "visibly exhausted"]
    
    objects = ["project", "report", "proposal", "deadline"]
    qualifiers = ["version 3.2", "the revised one", "originally due last month", "the one we discussed"]
    actions = ["wait", "be reconsidered", "go through another review", "be submitted separately"]
    
    return [
        f"The {random.choice(events)} ({random.choice(detail1s)}) {random.choice(verbs)} ({random.choice(detail2s)}), and by the end ({random.choice(timings)}) we had {random.choice(outcomes)}.",
        f"{random.choice(persons)} ({random.choice(descriptions)}) seemed {random.choice(emotions)}.",
        f"The {random.choice(objects)} ({random.choice(qualifiers)}, if I remember correctly) would have to {random.choice(actions)}."
    ]


def generate_parallel_sample() -> List[str]:
    """Generate repetitive/parallel structure prose."""
    patterns = [
        lambda: [f"She {v}." for v in random.sample(["walked", "stopped", "turned", "waited", "breathed", "continued"], 3)],
        lambda: [f"He {v}." for v in random.sample(["entered", "sat", "listened", "nodded", "rose", "left"], 3)],
        lambda: [f"The {random.choice(['sun', 'moon', 'rain', 'wind', 'light', 'dark'])} {v}." 
                for v in random.sample(["came", "went", "stayed", "passed", "returned", "faded"], 3)],
        lambda: [f"{n} {random.choice(['arrived', 'departed', 'continued', 'ended'])}." 
                for n in random.sample(["Morning", "Evening", "Night", "Day", "Summer", "Winter"], 3)],
    ]
    return random.choice(patterns)()


def generate_longform_sample() -> List[str]:
    """Generate complex multi-clause sentences."""
    openers = [
        "Although she had intended to arrive early, having planned her route the night before and set multiple alarms,",
        "When the results came back from the laboratory, showing levels that were not only above normal but significantly outside the expected range,",
        "Because the situation had evolved in ways that nobody could have anticipated, requiring adjustments to plans that had already been revised several times,",
        "Despite having spent weeks preparing for this moment, rehearsing every possible scenario and anticipating every conceivable objection,",
        "Given that the circumstances were far more complicated than they had initially appeared, involving multiple parties with conflicting interests,",
    ]
    
    middles = [
        "the unexpected complications, combined with factors that had only recently come to light, meant that the original timeline would need to be completely reconsidered",
        "she found herself facing a situation that demanded not only technical expertise but also a kind of emotional intelligence that couldn't be learned from books",
        "the team realized that their assumptions, which had seemed so reasonable at the time, were based on information that turned out to be incomplete at best",
        "what had started as a straightforward task gradually revealed itself to be something far more complex and challenging than anyone had imagined",
    ]
    
    closers = [
        "The consequences of this revelation would take years to fully understand and even longer to address.",
        "In retrospect, the signs had been there all along, visible to anyone willing to look closely enough.",
        "What happened next would change everything, though no one realized it at the time.",
        "The lesson, if there was one, remained frustratingly unclear even after extensive reflection.",
    ]
    
    return [
        random.choice(openers) + " " + random.choice(middles) + ".",
        random.choice(middles).capitalize() + ".",
        random.choice(closers)
    ]


def generate_conversational_sample() -> List[str]:
    """Generate casual, conversational prose."""
    patterns = [
        lambda: [
            random.choice(["So yeah.", "Look, I get it.", "Thing is,", "Okay so.", "I mean, sure."]),
            random.choice(["That happened.", "It's complicated.", "Nobody told me.", "We figured it out.", "It didn't work."]),
            random.choice(["But hey—what can you do?", "And now here we are.", "Whatever.", "It is what it is.", "Moving on."])
        ],
        lambda: [
            random.choice(["Honestly?", "Real talk though.", "Not gonna lie.", "Between you and me.", "Here's the thing."]),
            random.choice(["It's not great.", "Could be worse.", "I've seen better.", "It's a whole thing.", "Totally fine."]),
            random.choice(["But we deal.", "So there's that.", "Anyway.", "You know how it is.", "Same old."])
        ],
        lambda: [
            random.choice(["Wait, what?", "Hold up.", "Okay okay.", "So get this.", "You won't believe it."]),
            random.choice(["No way.", "Seriously?", "That's wild.", "Didn't see that coming.", "Plot twist."]),
            random.choice(["I know, right?", "Crazy.", "Totally.", "Makes no sense.", "But here we are."])
        ],
    ]
    return random.choice(patterns)()


# =============================================================================
# GENERATORS MAP
# =============================================================================

GENERATORS = {
    "MINIMAL": generate_minimal_sample,
    "DENSE": generate_dense_sample,
    "POETIC": generate_poetic_sample,
    "INTERROGATIVE": generate_interrogative_sample,
    "ASSERTIVE": generate_assertive_sample,
    "HEDGED": generate_hedged_sample,
    "PARENTHETICAL": generate_parenthetical_sample,
    "PARALLEL": generate_parallel_sample,
    "LONGFORM": generate_longform_sample,
    "CONVERSATIONAL": generate_conversational_sample,
}


# =============================================================================
# SIMULATION & ANALYSIS
# =============================================================================

def run_user_simulation(mode: str, user_id: int) -> Dict[str, Any]:
    """Simulate one user's writing and full LNCP analysis."""
    generator = GENERATORS[mode]
    sentences = generator()
    
    try:
        result = quick_analyze(sentences=sentences, phase4_mode="PROMPTING")
        
        # Extract key metrics
        phase1 = result.get('phase1', {})
        outputs = phase1.get('outputs', {})
        phase2 = result.get('phase2', {})
        hi_profile = result.get('high_intent_profile', {})
        phase6 = result.get('phase6', {})
        
        return {
            'user_id': user_id,
            'mode': mode,
            'sentences': sentences,
            'success': True,
            # Structural metrics
            'word_count': outputs.get('token_volume', {}).get('metrics', {}).get('total_token_count', 0),
            'avg_words': outputs.get('token_volume', {}).get('metrics', {}).get('mean_tokens_per_sentence', 0),
            'scope_events': outputs.get('scope_event_presence', {}).get('metrics', {}).get('total_scope_event_count', 0),
            'operator_events': outputs.get('operator_event_presence', {}).get('metrics', {}).get('total_operator_event_count', 0),
            'zero_events': outputs.get('zero_event_presence', {}).get('metrics', {}).get('total_zero_event_count', 0),
            'variety_ratio': outputs.get('structural_variety', {}).get('metrics', {}).get('signature_variety_ratio', 0),
            # High-intent metrics
            'hi_count': hi_profile.get('total_high_intent_events', 0),
            'hi_rate': hi_profile.get('high_intent_rate', 0),
            'epistemic_openness': hi_profile.get('epistemic_openness', 0.5),
            'epistemic_stance': hi_profile.get('epistemic_stance', 'UNKNOWN'),
            # Detection flags
            'is_contradictory': hi_profile.get('is_contradictory', False),
            'is_minimal': hi_profile.get('is_minimal', False),
            'is_poetic_mode': hi_profile.get('is_poetic_mode', False),
            'is_assertive_mode': hi_profile.get('is_assertive_mode', False),
            'is_interrogative_mode': hi_profile.get('is_interrogative_mode', False),
            'is_structurally_dense': hi_profile.get('is_structurally_dense', False),
            'register': hi_profile.get('register', 'FORMAL'),
            'syntax_complexity': hi_profile.get('syntax_complexity', 'SIMPLE'),
            'has_anaphora': hi_profile.get('has_anaphora', False),
            # Derived scores
            'informality_score': hi_profile.get('informality_score', 0),
            'structural_density_score': hi_profile.get('structural_density_score', 0),
            'avg_clauses': hi_profile.get('avg_clauses', 1),
            'question_ratio': hi_profile.get('question_ratio', 0),
            # Phase 2 presentation
            'presentation_mode': phase2.get('presentation_mode', 'UNKNOWN'),
            # Phase 6 summary title
            'summary_title': phase6.get('summary', {}).get('title', ''),
        }
    except Exception as e:
        return {
            'user_id': user_id,
            'mode': mode,
            'sentences': sentences,
            'success': False,
            'error': str(e)
        }


def compute_range_stats(values: List[float]) -> Dict[str, float]:
    """Compute statistical ranges for a list of values."""
    if not values:
        return {'min': 0, 'max': 0, 'mean': 0, 'median': 0, 'std': 0, 'p25': 0, 'p75': 0}
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    return {
        'min': min(values),
        'max': max(values),
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'std': statistics.stdev(values) if len(values) > 1 else 0,
        'p25': sorted_vals[n // 4] if n >= 4 else sorted_vals[0],
        'p75': sorted_vals[3 * n // 4] if n >= 4 else sorted_vals[-1],
    }


def categorize_users(results: List[Dict], metric: str, bins: List[Tuple[float, float, str]]) -> Dict[str, List[int]]:
    """Categorize users into bins based on a metric."""
    categories = defaultdict(list)
    
    for r in results:
        if not r['success']:
            continue
        value = r.get(metric, 0)
        for low, high, label in bins:
            if low <= value < high:
                categories[label].append(r['user_id'])
                break
    
    return dict(categories)


def run_full_simulation():
    """Run simulation for all modes and present grouped comparisons."""
    print("=" * 80)
    print("LNCP USER SIMULATION v1.0")
    print("100 users × 10 modes = 1000 simulated writing sessions")
    print("=" * 80)
    
    all_results = {}
    mode_stats = {}
    
    for mode in GENERATORS.keys():
        print(f"\nSimulating {mode}...", end=" ", flush=True)
        results = []
        
        for user_id in range(1, 101):
            result = run_user_simulation(mode, user_id)
            results.append(result)
        
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ {success_count}/100 successful")
        
        all_results[mode] = results
        
        # Compute stats for successful results
        successful = [r for r in results if r['success']]
        if successful:
            mode_stats[mode] = {
                'word_count': compute_range_stats([r['word_count'] for r in successful]),
                'avg_words': compute_range_stats([r['avg_words'] for r in successful]),
                'hi_count': compute_range_stats([r['hi_count'] for r in successful]),
                'hi_rate': compute_range_stats([r['hi_rate'] for r in successful]),
                'epistemic_openness': compute_range_stats([r['epistemic_openness'] for r in successful]),
                'scope_events': compute_range_stats([r['scope_events'] for r in successful]),
                'avg_clauses': compute_range_stats([r['avg_clauses'] for r in successful]),
                'informality_score': compute_range_stats([r['informality_score'] for r in successful]),
                'structural_density_score': compute_range_stats([r['structural_density_score'] for r in successful]),
                'question_ratio': compute_range_stats([r['question_ratio'] for r in successful]),
                # Distributions
                'stance_dist': defaultdict(int),
                'complexity_dist': defaultdict(int),
                'register_dist': defaultdict(int),
                # Detection counts
                'detection_counts': {
                    'minimal': sum(1 for r in successful if r['is_minimal']),
                    'poetic': sum(1 for r in successful if r['is_poetic_mode']),
                    'assertive': sum(1 for r in successful if r['is_assertive_mode']),
                    'interrogative': sum(1 for r in successful if r['is_interrogative_mode']),
                    'dense': sum(1 for r in successful if r['is_structurally_dense']),
                    'contradictory': sum(1 for r in successful if r['is_contradictory']),
                    'anaphora': sum(1 for r in successful if r['has_anaphora']),
                    'informal': sum(1 for r in successful if r['register'] == 'INFORMAL'),
                    'complex': sum(1 for r in successful if r['syntax_complexity'] == 'COMPLEX'),
                },
            }
            for r in successful:
                mode_stats[mode]['stance_dist'][r['epistemic_stance']] += 1
                mode_stats[mode]['complexity_dist'][r['syntax_complexity']] += 1
                mode_stats[mode]['register_dist'][r['register']] += 1
    
    # =============================================================================
    # PRESENT RESULTS
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("STRUCTURAL METRICS BY MODE")
    print("=" * 80)
    print("\n{:<14} {:>12} {:>12} {:>12} {:>12}".format(
        "Mode", "Words", "Avg/Sent", "Markers", "Scope"))
    print("{:<14} {:>12} {:>12} {:>12} {:>12}".format(
        "", "(range)", "(range)", "(range)", "(range)"))
    print("-" * 65)
    
    for mode, stats in mode_stats.items():
        w = stats['word_count']
        a = stats['avg_words']
        h = stats['hi_count']
        s = stats['scope_events']
        print("{:<14} {:>5.0f}-{:<5.0f} {:>5.1f}-{:<5.1f} {:>5.1f}-{:<5.1f} {:>5.1f}-{:<5.1f}".format(
            mode, w['min'], w['max'], a['min'], a['max'], h['min'], h['max'], s['min'], s['max']))
    
    print("\n" + "=" * 80)
    print("EPISTEMIC PROFILE BY MODE")
    print("=" * 80)
    print("\n{:<14} {:>10} {:>10} {:>10} {:>10} {:>10}".format(
        "Mode", "MINIMAL", "OPEN", "CLOSED", "CONTRA", "BALANCED"))
    print("-" * 65)
    
    for mode, stats in mode_stats.items():
        sd = stats['stance_dist']
        print("{:<14} {:>10} {:>10} {:>10} {:>10} {:>10}".format(
            mode, 
            sd.get('MINIMAL', 0),
            sd.get('OPEN', 0),
            sd.get('CLOSED', 0),
            sd.get('CONTRADICTORY', 0),
            sd.get('BALANCED', 0)))
    
    print("\n" + "=" * 80)
    print("RHETORICAL DETECTION BY MODE")
    print("=" * 80)
    print("\n{:<14} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
        "Mode", "Assert", "Interr", "Inform", "Dense", "Complex", "Anaph"))
    print("-" * 70)
    
    for mode, stats in mode_stats.items():
        d = stats['detection_counts']
        print("{:<14} {:>8} {:>8} {:>8} {:>8} {:>8} {:>8}".format(
            mode,
            d['assertive'],
            d['interrogative'],
            d['informal'],
            d['dense'],
            d['complex'],
            d['anaphora']))
    
    print("\n" + "=" * 80)
    print("DETAILED METRIC RANGES (Mean ± Std)")
    print("=" * 80)
    print("\n{:<14} {:>14} {:>14} {:>14} {:>14}".format(
        "Mode", "Openness", "Informality", "Density", "Clauses"))
    print("-" * 70)
    
    for mode, stats in mode_stats.items():
        o = stats['epistemic_openness']
        i = stats['informality_score']
        d = stats['structural_density_score']
        c = stats['avg_clauses']
        print("{:<14} {:>6.2f}±{:<5.2f} {:>6.2f}±{:<5.2f} {:>6.2f}±{:<5.2f} {:>6.2f}±{:<5.2f}".format(
            mode,
            o['mean'], o['std'],
            i['mean'], i['std'],
            d['mean'], d['std'],
            c['mean'], c['std']))
    
    # =============================================================================
    # USER GROUPINGS
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("USER GROUPINGS BY MARKER DENSITY")
    print("=" * 80)
    
    marker_bins = [
        (0, 1, "Sparse (0)"),
        (1, 3, "Light (1-2)"),
        (3, 6, "Moderate (3-5)"),
        (6, 10, "Dense (6-9)"),
        (10, 100, "Heavy (10+)")
    ]
    
    print("\n{:<14} {:>12} {:>12} {:>12} {:>12} {:>12}".format(
        "Mode", "Sparse", "Light", "Moderate", "Dense", "Heavy"))
    print("-" * 75)
    
    for mode, results in all_results.items():
        groups = categorize_users(results, 'hi_count', marker_bins)
        print("{:<14} {:>12} {:>12} {:>12} {:>12} {:>12}".format(
            mode,
            len(groups.get("Sparse (0)", [])),
            len(groups.get("Light (1-2)", [])),
            len(groups.get("Moderate (3-5)", [])),
            len(groups.get("Dense (6-9)", [])),
            len(groups.get("Heavy (10+)", []))))
    
    print("\n" + "=" * 80)
    print("USER GROUPINGS BY SENTENCE LENGTH")
    print("=" * 80)
    
    length_bins = [
        (0, 8, "Brief (<8)"),
        (8, 15, "Short (8-14)"),
        (15, 25, "Medium (15-24)"),
        (25, 40, "Long (25-39)"),
        (40, 200, "Very Long (40+)")
    ]
    
    print("\n{:<14} {:>12} {:>12} {:>12} {:>12} {:>12}".format(
        "Mode", "Brief", "Short", "Medium", "Long", "Very Long"))
    print("-" * 75)
    
    for mode, results in all_results.items():
        groups = categorize_users(results, 'avg_words', length_bins)
        print("{:<14} {:>12} {:>12} {:>12} {:>12} {:>12}".format(
            mode,
            len(groups.get("Brief (<8)", [])),
            len(groups.get("Short (8-14)", [])),
            len(groups.get("Medium (15-24)", [])),
            len(groups.get("Long (25-39)", [])),
            len(groups.get("Very Long (40+)", []))))
    
    print("\n" + "=" * 80)
    print("USER GROUPINGS BY EPISTEMIC OPENNESS")
    print("=" * 80)
    
    openness_bins = [
        (0, 0.3, "Closed (<0.3)"),
        (0.3, 0.45, "Leaning Closed"),
        (0.45, 0.55, "Neutral (0.5)"),
        (0.55, 0.7, "Leaning Open"),
        (0.7, 1.01, "Open (>0.7)")
    ]
    
    print("\n{:<14} {:>12} {:>14} {:>12} {:>14} {:>12}".format(
        "Mode", "Closed", "Lean Closed", "Neutral", "Lean Open", "Open"))
    print("-" * 80)
    
    for mode, results in all_results.items():
        groups = categorize_users(results, 'epistemic_openness', openness_bins)
        print("{:<14} {:>12} {:>14} {:>12} {:>14} {:>12}".format(
            mode,
            len(groups.get("Closed (<0.3)", [])),
            len(groups.get("Leaning Closed", [])),
            len(groups.get("Neutral (0.5)", [])),
            len(groups.get("Leaning Open", [])),
            len(groups.get("Open (>0.7)", []))))
    
    # =============================================================================
    # CROSS-MODE COMPARISONS
    # =============================================================================
    
    print("\n" + "=" * 80)
    print("CROSS-MODE SIMILARITY CLUSTERS")
    print("=" * 80)
    
    # Group modes by primary characteristics
    print("\n📊 By Marker Density:")
    sparse_modes = [m for m, s in mode_stats.items() if s['hi_count']['mean'] < 1]
    moderate_modes = [m for m, s in mode_stats.items() if 1 <= s['hi_count']['mean'] < 4]
    dense_modes = [m for m, s in mode_stats.items() if s['hi_count']['mean'] >= 4]
    print(f"   Sparse markers: {', '.join(sparse_modes)}")
    print(f"   Moderate markers: {', '.join(moderate_modes)}")
    print(f"   Dense markers: {', '.join(dense_modes)}")
    
    print("\n📊 By Sentence Complexity:")
    simple_modes = [m for m, s in mode_stats.items() if s['avg_clauses']['mean'] < 1.3]
    moderate_complexity = [m for m, s in mode_stats.items() if 1.3 <= s['avg_clauses']['mean'] < 2]
    complex_modes = [m for m, s in mode_stats.items() if s['avg_clauses']['mean'] >= 2]
    print(f"   Simple syntax: {', '.join(simple_modes)}")
    print(f"   Moderate syntax: {', '.join(moderate_complexity)}")
    print(f"   Complex syntax: {', '.join(complex_modes)}")
    
    print("\n📊 By Register:")
    formal_modes = [m for m, s in mode_stats.items() if s['detection_counts']['informal'] < 30]
    informal_modes = [m for m, s in mode_stats.items() if s['detection_counts']['informal'] >= 30]
    print(f"   Formal register: {', '.join(formal_modes)}")
    print(f"   Informal register: {', '.join(informal_modes)}")
    
    # Save full results
    output = {
        'mode_stats': {m: {k: v for k, v in s.items() if k != 'stance_dist' and k != 'complexity_dist' and k != 'register_dist'} 
                      for m, s in mode_stats.items()},
        'summary': {
            'total_simulations': 1000,
            'successful': sum(sum(1 for r in results if r['success']) for results in all_results.values()),
            'modes': list(GENERATORS.keys())
        }
    }
    
    with open('/home/claude/lncp-web-app/user_simulation_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print("✅ Simulation complete. Results saved to user_simulation_results.json")
    print("=" * 80)


if __name__ == "__main__":
    run_full_simulation()
