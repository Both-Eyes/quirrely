#!/usr/bin/env python3
"""
LNCP Challenge Test Suite v2.0 - Sample Generator
Generates 100 samples for each of 10 categories and runs analysis
"""

import json
import sys
import random
sys.path.insert(0, '/home/claude/lncp-web-app/backend')

from lncp_orchestrator import quick_analyze

# ============================================================
# SAMPLE GENERATORS
# ============================================================

def gen_minimal():
    """Generate MINIMAL samples - flat, no markers"""
    templates = [
        ["The {noun} was {adj}.", "She {past_verb}.", "Nothing {past_verb}."],
        ["{noun} {past_verb}.", "The {noun} was {adj}.", "{noun} {past_verb}."],
        ["He {past_verb}.", "The {noun} {past_verb}.", "Time {past_verb}."],
        ["Morning came.", "Light filled the {noun}.", "She woke."],
        ["The {noun} {past_verb}.", "No one {past_verb}.", "It stopped."],
    ]
    nouns = ["door", "rain", "street", "chair", "phone", "bird", "sky", "window", "water", "faucet", 
             "toast", "snow", "ground", "train", "platform", "book", "story", "tree", "fire", "smoke",
             "clock", "room", "wave", "sand", "beach", "canvas", "house", "letter", "fog", "city",
             "glass", "bus", "night", "light", "sun", "color", "wind", "star", "moon", "seed"]
    adjs = ["open", "wet", "old", "white", "cold", "clear", "quiet", "still", "empty", "bare",
            "warm", "bright", "dark", "soft", "hard", "slow", "fast", "deep", "high", "low"]
    past_verbs = ["walked", "passed", "creaked", "moved", "rang", "answered", "stopped", "flew", 
                  "blew", "looked", "dripped", "fixed", "ate", "left", "fell", "played", "arrived",
                  "closed", "ended", "sat", "appeared", "burned", "rose", "crackled", "typed",
                  "barked", "ran", "returned", "brewed", "smiled", "ticked", "crashed", "shifted",
                  "painted", "mixed", "filled", "faded", "danced", "broke", "scattered", "waited"]
    
    samples = []
    for i in range(100):
        template = random.choice(templates)
        sample = []
        for sent in template:
            s = sent.format(
                noun=random.choice(nouns),
                adj=random.choice(adjs),
                past_verb=random.choice(past_verbs)
            )
            sample.append(s)
        samples.append(sample)
    return samples

def gen_dense():
    """Generate DENSE samples - nested, contradictory markers"""
    openers = [
        "I definitely believed (or thought I did?) that",
        "She was certain (mostly certain, anyway) that", 
        "It was obvious—painfully obvious, actually—that",
        "He must have known (surely he knew?) that",
        "The truth—if there was such a thing—seemed",
        "I knew—or believed I knew—that",
        "She believed (had always believed, really) that",
        "It seemed clear (to me, anyway) that",
        "He appeared (to everyone) to be",
        "The evidence suggested (strongly suggested, actually) that"
    ]
    middles = [
        "the answer—if there even was one—might be hiding somewhere",
        "something had changed (though I couldn't say what)",
        "things would work out—though lately I'd begun to wonder",
        "everything was falling apart (or maybe that was just my perception)",
        "the situation was more complex than anyone realized",
        "nothing was quite as it seemed—or perhaps it was",
        "the pattern was obvious (to me, anyway) even if no one else noticed",
        "something was wrong (though no one would say what)",
        "the decision seemed right (felt right, at least)",
        "the moment felt significant—or perhaps not"
    ]
    closers = [
        "Perhaps that's always how it works; you know until you don't.",
        "Maybe certainty itself was the illusion.",
        "I definitely had my doubts.",
        "The difference, she realized, might not matter.",
        "Perhaps that was intentional; perhaps not.",
        "I think we'll never know for certain.",
        "Maybe that's the point; maybe it isn't.",
        "Certainly something shifted (or seemed to shift).",
        "The feeling persisted nonetheless.",
        "Perhaps I was imagining things; perhaps I wasn't."
    ]
    
    samples = []
    for i in range(100):
        sample = [
            random.choice(openers) + " " + random.choice(middles) + ".",
            random.choice(middles).capitalize() + ".",
            random.choice(closers)
        ]
        samples.append(sample)
    return samples

def gen_poetic():
    """Generate POETIC samples - operators, em-dashes, fragments"""
    patterns = [
        ["{thing1} & {thing2} & the space between—that's where it lives.", 
         "Not in the {gerund} / but in the almost-{past}.", 
         "(And what does '{word}' even mean here?)"],
        ["Here / not here / the difference thin as breath.",
         "She moves through {place}s like water through fingers.",
         "What stays & what goes—who decides?"],
        ["{thing1}—or what passes for it—arrives without announcement.",
         "The {thing1} / the {thing2} / the {adj} between.",
         "We measure {thing1}; it measures us back."],
        ["{thing1} & {thing2} & the weight of both.",
         "He speaks; she listens / she speaks; he's gone.",
         "(The conversation continues anyway.)"],
        ["Time folds: now / then / the blurring edge.",
         "{thing1} is just {thing2} facing backward.",
         "What we {verb} & what {verb}s us—different things."],
    ]
    things = ["light", "shadow", "sound", "silence", "time", "space", "memory", "love", "loss", 
              "breath", "word", "voice", "echo", "water", "stone", "fire", "ice", "wind", "rain"]
    gerunds = ["saying", "hearing", "seeing", "knowing", "being", "feeling", "thinking", "waiting"]
    pasts = ["said", "heard", "seen", "known", "felt", "thought", "waited", "lost"]
    adjs = ["gray", "thin", "wide", "deep", "dark", "light", "soft", "hard", "cold", "warm"]
    places = ["room", "hall", "street", "garden", "house", "space", "moment", "memory"]
    verbs = ["remember", "forget", "hold", "release", "see", "hear", "feel", "know"]
    words = ["live", "love", "time", "space", "meaning", "truth", "real", "here"]
    
    samples = []
    for i in range(100):
        pattern = random.choice(patterns)
        sample = []
        for sent in pattern:
            s = sent.format(
                thing1=random.choice(things),
                thing2=random.choice(things),
                gerund=random.choice(gerunds),
                past=random.choice(pasts),
                adj=random.choice(adjs),
                place=random.choice(places),
                verb=random.choice(verbs),
                word=random.choice(words)
            )
            sample.append(s)
        samples.append(sample)
    return samples

def gen_interrogative():
    """Generate INTERROGATIVE samples - all questions"""
    q_starts = ["Why do we", "What makes", "Where does", "How can", "Who decides", "When did",
                "Is it", "Does anyone", "Can we", "Should we", "Would it", "Could there be"]
    q_middles = ["always wait", "hesitation feel safer", "the time go", "silence be so loud",
                 "what's normal", "certainty matter", "love go when it ends", "fear help",
                 "memory work", "truth hide", "patterns comfort us", "change come",
                 "trust develop", "wisdom emerge", "courage appear", "meaning form"]
    q_ends = ["?", "?", "?"]  # Always questions
    
    follow_ups = [
        "Is it fear, or something else?",
        "Does anyone really know?",
        "Can we even know?",
        "Or is that the wrong question?",
        "And does it matter?",
        "Who gets to decide?",
        "Is there a right answer?",
        "What would change if we knew?",
        "Would the answer help?",
        "Or are we asking the wrong thing?"
    ]
    
    samples = []
    for i in range(100):
        sample = [
            f"{random.choice(q_starts)} {random.choice(q_middles)}?",
            f"{random.choice(q_starts)} {random.choice(q_middles)}?",
            random.choice(follow_ups)
        ]
        samples.append(sample)
    return samples

def gen_assertive():
    """Generate ASSERTIVE samples - confident, no hedging"""
    assertions = [
        "This is how it works.", "You show up.", "Results follow.",
        "There are no shortcuts.", "The work is the work.", "Accept it.",
        "Action beats intention.", "Always.", "No debate.",
        "Fear is a liar.", "It speaks loudly.", "Ignore it.",
        "Discipline creates freedom.", "This is fact.", "Not paradox.",
        "Consistency wins.", "Talent fades.", "Showing up doesn't.",
        "Pain is information.", "Listen to it.", "Then proceed.",
        "Time waits for no one.", "Neither should you.", "Go.",
        "Words mean nothing.", "Actions prove everything.", "Watch hands.",
        "The past is dead.", "Only now exists.", "Use it.",
        "Failure teaches.", "Success flatters.", "Learn from both.",
        "Sleep is not optional.", "Rest enables performance.", "Prioritize it.",
        "Health comes first.", "Everything else follows.", "No debate.",
        "Quality beats quantity.", "Every time.", "Without exception.",
        "Focus is the multiplier.", "Eliminate distractions.", "Results follow.",
        "Speed matters.", "Perfectionism kills.", "Ship it.",
        "Execution beats ideas.", "Ideas are cheap.", "Doing is expensive.",
        "Trust is earned slowly.", "Lost quickly.", "Handle carefully.",
        "Simple is hard.", "That's the point.", "Worth the effort."
    ]
    
    samples = []
    for i in range(100):
        # Pick 3 consecutive assertions or random ones
        if random.random() > 0.5:
            idx = random.randint(0, len(assertions) - 3)
            sample = assertions[idx:idx+3]
        else:
            sample = random.sample(assertions, 3)
        samples.append(sample)
    return samples

def gen_hedged():
    """Generate HEDGED samples - heavy qualification"""
    openers = [
        "It seems possible, perhaps even likely, that",
        "The evidence appears to suggest, tentatively at least, that",
        "There is arguably some indication that",
        "One could reasonably argue that",
        "It might be the case that",
        "There appears to be some reason to believe that",
        "The data seems to point, however uncertainly, toward",
        "It could be argued, with some justification perhaps, that",
        "There is possibly some evidence that",
        "The findings seem to indicate, though perhaps inconclusively, that"
    ]
    claims = [
        "the observed effects might be attributable to some combination of factors",
        "there may be some correlation worth investigating",
        "the phenomenon might exist, though perhaps not universally",
        "the relationship could potentially be significant",
        "further research would presumably be needed",
        "the approach has some merit, however limited",
        "the theory might have some validity",
        "the results could possibly support the hypothesis",
        "the pattern appears somewhat consistent with predictions",
        "the evidence tips slightly in one direction"
    ]
    closers = [
        "Further research would presumably be needed to establish causality.",
        "These findings should probably be interpreted with some caution.",
        "One should perhaps consider alternative explanations.",
        "Caution would seem warranted in generalizing.",
        "Additional research could potentially elucidate matters.",
        "Interpretation should perhaps proceed cautiously.",
        "The matter remains perhaps somewhat unresolved.",
        "A balanced view would seem appropriate.",
        "Definitive conclusions might be premature.",
        "Further evidence would likely be helpful."
    ]
    
    samples = []
    for i in range(100):
        sample = [
            random.choice(openers) + " " + random.choice(claims) + ".",
            random.choice(openers) + " " + random.choice(claims) + ".",
            random.choice(closers)
        ]
        samples.append(sample)
    return samples

def gen_parenthetical():
    """Generate PARENTHETICAL samples - nested asides"""
    templates = [
        "The {noun} ({adj_phrase}) {verb} ({time_phrase}), and by the end ({when}) we had {outcome}.",
        "I found the {noun} (a {description}) at the {place} ({location_detail}) tucked between two {items}.",
        "The {noun} ({history}) served the best {food} ({detail}) I'd ever tasted.",
        "My {relation}'s {noun} (the {color} one on {street}) had a {feature} ({condition}) where we used to {activity}.",
        "The {event} ({timing}) was late again ({duration}, this time)."
    ]
    
    nouns = ["meeting", "book", "restaurant", "house", "train", "office", "movie", "apartment", 
             "wedding", "concert", "flight", "interview", "painting", "party", "hike"]
    adj_phrases = ["which nobody wanted", "a first edition, surprisingly", "which had been open since 1952",
                   "the blue one on Oak Avenue", "the 7:45 express, supposedly", "on the 23rd floor, with a view",
                   "a French film from the 60s", "a one-bedroom in Brooklyn", "her cousin's, I think"]
    verbs = ["ran long", "was found", "seemed fine", "went well", "started late", "ended early"]
    
    samples = []
    for i in range(100):
        # Generate heavily parenthetical sentences
        sample = [
            f"The meeting (which nobody wanted) ran long (as usual), and by the end (around {random.randint(2,6)}pm) we decided (tentatively) to postpone.",
            f"Sarah (our team lead) seemed {random.choice(['relieved', 'frustrated', 'confused', 'pleased'])}.",
            f"The project (version {random.randint(1,5)}.{random.randint(0,9)}, if I remember correctly) would have to wait."
        ]
        samples.append(sample)
    return samples

def gen_parallel():
    """Generate PARALLEL samples - repetitive structure"""
    patterns = [
        ["She {v1}.", "She {v2}.", "She {v3}."],
        ["{N1} {v1}.", "{N2} {v2}.", "{N3} {v3}."],
        ["He {v1}.", "He {v2}.", "He {v3} again."],
        ["The {n} {v1}.", "The {n} {v2}.", "The {n} {v3}."],
        ["{V1} came.", "{V2} followed.", "{V3} remained."],
    ]
    
    verbs = ["walked", "ran", "stopped", "waited", "looked", "turned", "spoke", "listened",
             "rose", "fell", "entered", "left", "opened", "closed", "started", "ended",
             "smiled", "laughed", "cried", "sighed", "breathed", "slept", "woke", "dreamed"]
    nouns = ["sun", "moon", "rain", "wind", "door", "clock", "bell", "light", "shadow", "silence"]
    subjects = ["Morning", "Evening", "Night", "Day", "Winter", "Summer", "Silence", "Sound"]
    
    samples = []
    for i in range(100):
        pattern = random.choice(patterns)
        v = random.sample(verbs, 3)
        n = random.choice(nouns)
        N = random.sample(nouns, 3)
        V = random.sample(subjects, 3)
        
        sample = []
        for sent in pattern:
            s = sent.format(v1=v[0], v2=v[1], v3=v[2], n=n, N1=N[0].capitalize(), N2=N[1].capitalize(), 
                           N3=N[2].capitalize(), V1=V[0], V2=V[1], V3=V[2])
            sample.append(s)
        samples.append(sample)
    return samples

def gen_longform():
    """Generate LONGFORM samples - complex multi-clause sentences"""
    openers = [
        "Although she had intended to arrive early, having planned her route the night before and set multiple alarms,",
        "When the results came back from the laboratory, showing levels that were not only above normal but significantly outside the expected range,",
        "Because the contract had been written by lawyers who specialized in exactly this kind of ambiguous language,",
        "Having spent the better part of his career studying a phenomenon that few others cared about,",
        "What had started as a simple disagreement over a relatively minor issue,",
        "Despite having rehearsed the speech dozens of times in front of various audiences,",
        "By the time the investigation concluded, having expanded from a simple inquiry to a full examination,",
        "Given the complexity of the situation, involving as it did multiple parties with conflicting interests,",
        "If you considered all the factors involved, including the unexpected complications and the limited resources,",
        "Although every indication suggested that the outcome was essentially predetermined,"
    ]
    
    middles = [
        "the unexpected complications, combined with circumstances she hadn't anticipated, meant that by the time she finally arrived,",
        "she sat in the sterile waiting room trying to process what this might mean for her future,",
        "the dispute that arose required multiple hearings before anyone could make sense of it,",
        "the professor found himself in the unusual position of being both an expert and a target,",
        "had escalated over the course of several years into something no one could have predicted,",
        "she found that standing at the actual podium, facing the audience, her mind went blank,",
        "the original person who had raised concerns had long since moved on,",
        "the fact that anything was accomplished at all represented a minor miracle,",
        "it was actually remarkable that the project came in only slightly late,",
        "participants continued to argue passionately as if their words might actually matter,"
    ]
    
    closers = [
        "The consequences would take years to fully understand.",
        "She learned something important that day, though she couldn't quite articulate what.",
        "Everyone affected would remember it differently.",
        "The official record would tell a different story entirely.",
        "In retrospect, the signs had been there all along.",
        "What happened next surprised everyone, including those who thought they knew better.",
        "The lesson, if there was one, remained unclear.",
        "Life, as it tends to do, continued regardless.",
        "The matter was eventually resolved, though not to anyone's complete satisfaction.",
        "Time would tell whether any of it had mattered."
    ]
    
    samples = []
    for i in range(100):
        sample = [
            random.choice(openers) + " " + random.choice(middles),
            random.choice(middles).capitalize().rstrip(',') + ".",
            random.choice(closers)
        ]
        samples.append(sample)
    return samples

def gen_conversational():
    """Generate CONVERSATIONAL samples - fragments, casual"""
    openers = ["So yeah.", "Look, I get it.", "Thing is,", "Wait, what?", "Okay so.", 
               "I mean, sure.", "Right?", "Dunno.", "Ugh.", "Huh.", "Anyway.", "Weird, right?",
               "Yeah, no.", "Oh!", "Honestly?", "Cool, cool, cool.", "Nope.", "Man.", "Well then.",
               "Just saying.", "Ha!", "Yikes.", "So apparently.", "Like, obviously.", "Okay okay."]
    
    middles = ["That happened.", "You're frustrated.", "Nobody told me.", "No way.", "Basically.",
               "Could've been worse.", "That's what I said!", "Maybe.", "Not this again.", "Interesting.",
               "I tried.", "Can't complain.", "Long story short.", "Thought so too.", "That's not happening.",
               "Almost forgot.", "No idea.", "Totally fine.", "Nobody listens.", "Let me think.",
               "You know how it goes.", "Tried that.", "What a day.", "Here we are.", "That's wrong."]
    
    closers = ["But hey—what can you do?", "And now here we are.", "You're kidding me.", "It's a whole thing.",
               "But still.", "Exactly.", "We'll see I guess.", "Every single time.", "Didn't expect that.",
               "It didn't work.", "But won't.", "We figured it out.", "Whatever.", "Sorry.", "There's one more thing.",
               "Your guess is good as mine.", "Not stressed at all.", "Ever.", "Actually—no.", "Same old same old.",
               "Doesn't work.", "Need a drink.", "Now what?", "But okay.", "But seriously."]
    
    samples = []
    for i in range(100):
        sample = [
            random.choice(openers),
            random.choice(middles),
            random.choice(closers)
        ]
        samples.append(sample)
    return samples

# ============================================================
# ANALYSIS
# ============================================================

def run_analysis(sentences, sample_id, category):
    """Run a sample through LNCP and return key metrics"""
    try:
        result = quick_analyze(sentences=sentences, phase4_mode="PROMPTING")
        
        phase1 = result.get('phase1', {})
        outputs = phase1.get('outputs', {})
        hi_profile = result.get('high_intent_profile', {})
        
        return {
            'sample_id': sample_id,
            'category': category,
            'word_count': outputs.get('token_volume', {}).get('metrics', {}).get('total_token_count', 0),
            'avg_words': outputs.get('token_volume', {}).get('metrics', {}).get('mean_tokens_per_sentence', 0),
            'scope_events': outputs.get('scope_event_presence', {}).get('metrics', {}).get('total_scope_event_count', 0),
            'operator_events': outputs.get('operator_event_presence', {}).get('metrics', {}).get('total_operator_event_count', 0),
            'zero_events': outputs.get('zero_event_presence', {}).get('metrics', {}).get('total_zero_event_count', 0),
            'hi_count': hi_profile.get('total_high_intent_events', 0),
            'epistemic_stance': hi_profile.get('epistemic_stance', 'UNKNOWN'),
            'is_contradictory': hi_profile.get('is_contradictory', False),
            'is_minimal': hi_profile.get('is_minimal', False),
            'is_poetic_mode': hi_profile.get('is_poetic_mode', False),
            'emdash_count': hi_profile.get('emdash_count', 0),
            # v0.6.0 fields
            'is_assertive_mode': hi_profile.get('is_assertive_mode', False),
            'is_interrogative_mode': hi_profile.get('is_interrogative_mode', False),
            'register': hi_profile.get('register', 'FORMAL'),
            'informality_score': hi_profile.get('informality_score', 0.0),
            'has_anaphora': hi_profile.get('has_anaphora', False),
            'syntax_complexity': hi_profile.get('syntax_complexity', 'SIMPLE'),
            'avg_clauses': hi_profile.get('avg_clauses', 0.0),
            'question_ratio': hi_profile.get('question_ratio', 0.0),
            'imperative_count': hi_profile.get('imperative_count', 0),
            # v0.6.1 fields
            'is_structurally_dense': hi_profile.get('is_structurally_dense', False),
            'structural_density_score': hi_profile.get('structural_density_score', 0.0),
            'success': True
        }
    except Exception as e:
        return {'sample_id': sample_id, 'category': category, 'success': False, 'error': str(e)}

def main():
    print("=" * 70)
    print("LNCP CHALLENGE TEST SUITE v2.0")
    print("1000 samples across 10 categories")
    print("=" * 70)
    
    generators = [
        ("MINIMAL", gen_minimal),
        ("DENSE", gen_dense),
        ("POETIC", gen_poetic),
        ("INTERROGATIVE", gen_interrogative),
        ("ASSERTIVE", gen_assertive),
        ("HEDGED", gen_hedged),
        ("PARENTHETICAL", gen_parenthetical),
        ("PARALLEL", gen_parallel),
        ("LONGFORM", gen_longform),
        ("CONVERSATIONAL", gen_conversational),
    ]
    
    all_results = []
    category_stats = {}
    
    for cat_name, gen_func in generators:
        print(f"\n{cat_name}...")
        samples = gen_func()
        results = []
        
        for i, sample in enumerate(samples):
            result = run_analysis(sample, f"{cat_name[:3]}_{i+1:03d}", cat_name)
            results.append(result)
        
        success = [r for r in results if r['success']]
        
        if success:
            stats = {
                'count': len(success),
                'avg_words': sum(r['word_count'] for r in success) / len(success),
                'avg_markers': sum(r['hi_count'] for r in success) / len(success),
                'avg_scope': sum(r['scope_events'] for r in success) / len(success),
                'avg_operators': sum(r['operator_events'] for r in success) / len(success),
                'avg_emdash': sum(r['emdash_count'] for r in success) / len(success),
                'stance_dist': {},
                'poetic': sum(1 for r in success if r['is_poetic_mode']),
                'minimal': sum(1 for r in success if r['is_minimal']),
                'contradictory': sum(1 for r in success if r['is_contradictory']),
                # v0.6.0 stats
                'assertive': sum(1 for r in success if r.get('is_assertive_mode', False)),
                'interrogative': sum(1 for r in success if r.get('is_interrogative_mode', False)),
                'informal': sum(1 for r in success if r.get('register') == 'INFORMAL'),
                'anaphora': sum(1 for r in success if r.get('has_anaphora', False)),
                'complex': sum(1 for r in success if r.get('syntax_complexity') == 'COMPLEX'),
                'avg_clauses': sum(r.get('avg_clauses', 0) for r in success) / len(success),
                'avg_question_ratio': sum(r.get('question_ratio', 0) for r in success) / len(success),
                # v0.6.1 stats
                'structurally_dense': sum(1 for r in success if r.get('is_structurally_dense', False)),
                'avg_density_score': sum(r.get('structural_density_score', 0) for r in success) / len(success),
            }
            for r in success:
                s = r['epistemic_stance']
                stats['stance_dist'][s] = stats['stance_dist'].get(s, 0) + 1
            
            category_stats[cat_name] = stats
            print(f"  ✅ {len(success)}/100 | words={stats['avg_words']:.1f} markers={stats['avg_markers']:.1f} stance={max(stats['stance_dist'].items(), key=lambda x:x[1])[0]}")
        
        all_results.extend(results)
    
    # Summary table
    print("\n" + "=" * 70)
    print("CROSS-CATEGORY COMPARISON")
    print("=" * 70)
    print("\n{:<14} {:>6} {:>7} {:>6} {:>6} {:>6} {:>12}".format(
        "Category", "Words", "Markers", "Scope", "Ops", "EmDash", "Top Stance"))
    print("-" * 65)
    
    for cat_name, stats in category_stats.items():
        top_stance = max(stats['stance_dist'].items(), key=lambda x: x[1])[0]
        print("{:<14} {:>6.1f} {:>7.1f} {:>6.1f} {:>6.1f} {:>6.1f} {:>12}".format(
            cat_name, stats['avg_words'], stats['avg_markers'], 
            stats['avg_scope'], stats['avg_operators'], stats['avg_emdash'], top_stance))
    
    # v0.5.0 Detection summary
    print("\n" + "=" * 70)
    print("v0.5.0 DETECTION")
    print("=" * 70)
    print("\n{:<14} {:>8} {:>10} {:>14}".format("Category", "Poetic", "Minimal", "Contradictory"))
    print("-" * 50)
    for cat_name, stats in category_stats.items():
        print("{:<14} {:>8} {:>10} {:>14}".format(
            cat_name, stats['poetic'], stats['minimal'], stats['contradictory']))
    
    # v0.6.0 Detection summary
    print("\n" + "=" * 70)
    print("v0.6.0 DETECTION")
    print("=" * 70)
    print("\n{:<14} {:>10} {:>12} {:>10} {:>10} {:>10}".format(
        "Category", "Assertive", "Interrogat", "Informal", "Anaphora", "Complex"))
    print("-" * 70)
    for cat_name, stats in category_stats.items():
        print("{:<14} {:>10} {:>12} {:>10} {:>10} {:>10}".format(
            cat_name, 
            stats.get('assertive', 0), 
            stats.get('interrogative', 0),
            stats.get('informal', 0),
            stats.get('anaphora', 0),
            stats.get('complex', 0)))
    
    # v0.6.1 Structural density
    print("\n" + "=" * 70)
    print("v0.6.1 STRUCTURAL DENSITY")
    print("=" * 70)
    print("\n{:<14} {:>12} {:>14}".format("Category", "Dense Count", "Avg Density"))
    print("-" * 45)
    for cat_name, stats in category_stats.items():
        print("{:<14} {:>12} {:>14.2f}".format(
            cat_name, 
            stats.get('structurally_dense', 0),
            stats.get('avg_density_score', 0)))
    
    # Detailed metrics
    print("\n" + "=" * 70)
    print("DETAILED METRICS")
    print("=" * 70)
    print("\n{:<14} {:>10} {:>12}".format("Category", "Avg Clauses", "Question %"))
    print("-" * 40)
    for cat_name, stats in category_stats.items():
        print("{:<14} {:>10.2f} {:>11.1%}".format(
            cat_name, 
            stats.get('avg_clauses', 0),
            stats.get('avg_question_ratio', 0)))
    
    # Save results
    with open('/home/claude/lncp-web-app/challenge_test_results_v2.json', 'w') as f:
        json.dump({'results': all_results, 'stats': category_stats}, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to challenge_test_results_v2.json")
    print(f"Total: {sum(1 for r in all_results if r['success'])}/{len(all_results)} successful")

if __name__ == "__main__":
    main()
