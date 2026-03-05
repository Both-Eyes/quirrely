#!/usr/bin/env python3
"""
LNCP Challenge Test Suite
90 writing samples across 3 structure categories to stress-test analysis
"""

import json
import sys
sys.path.insert(0, '/home/claude/lncp-web-app/backend')

from lncp_orchestrator import quick_analyze

# ============================================================
# CATEGORY 1: MINIMAL STRUCTURE (30 samples)
# No markers, flat rhythm, sparse punctuation
# ============================================================

MINIMAL_SAMPLES = [
    ["The door was open.", "She walked through.", "Nothing happened."],
    ["Rain fell.", "The street was wet.", "Cars passed."],
    ["He sat down.", "The chair creaked.", "Time moved."],
    ["Morning came.", "Light filled the room.", "She woke."],
    ["The phone rang.", "No one answered.", "It stopped."],
    ["Birds flew.", "The sky was clear.", "Wind blew."],
    ["She looked up.", "The ceiling was white.", "She looked down."],
    ["Water dripped.", "The faucet was old.", "No one fixed it."],
    ["He ate breakfast.", "The toast was cold.", "He left."],
    ["Snow fell.", "The ground turned white.", "Children played."],
    ["The train arrived.", "People got off.", "The platform emptied."],
    ["She closed the book.", "The story ended.", "She sat still."],
    ["Leaves fell.", "Autumn came.", "The tree was bare."],
    ["He walked home.", "The streets were quiet.", "Stars appeared."],
    ["The fire burned.", "Smoke rose.", "The wood crackled."],
    ["She typed.", "Words appeared.", "The screen glowed."],
    ["The dog barked.", "The cat ran.", "Silence returned."],
    ["Coffee brewed.", "Steam rose.", "The kitchen warmed."],
    ["He smiled.", "She smiled back.", "Nothing was said."],
    ["The clock ticked.", "Minutes passed.", "The room stayed still."],
    ["Waves crashed.", "Sand shifted.", "The beach was empty."],
    ["She painted.", "Colors mixed.", "The canvas filled."],
    ["The door closed.", "Footsteps faded.", "The house was quiet."],
    ["He ran.", "His lungs burned.", "He kept running."],
    ["The letter arrived.", "She read it.", "She put it down."],
    ["Fog rolled in.", "The city disappeared.", "Sound grew muffled."],
    ["She danced.", "The music played.", "No one watched."],
    ["The glass broke.", "Pieces scattered.", "No one moved."],
    ["He waited.", "The bus came.", "He got on."],
    ["Night fell.", "Lights came on.", "The city hummed."],
]

# ============================================================
# CATEGORY 2: DENSE NESTING, MIXED SIGNALS (30 samples)
# Heavy parentheticals, contradictory markers, complex stance
# ============================================================

DENSE_SAMPLES = [
    ["I definitely believed (or thought I did?) that the answer—if there even was one—might be hiding somewhere in the margins.", "The certainty I'd felt before seemed, somehow, less certain now.", "Perhaps that's always how it works; you know until you don't."],
    ["She was certain (mostly certain, anyway) that he would come back—though when she thought about it, she wasn't sure why.", "Maybe it was hope; maybe it was habit.", "The difference, she realized, might not matter."],
    ["I knew—or believed I knew—that something had changed (though I couldn't say what).", "The feeling was definitely there, lurking beneath the surface.", "Perhaps I was imagining it; perhaps I wasn't."],
    ["He must have known (surely he knew?) that she was watching—and yet he acted as if no one could see.", "Possibly he didn't care; possibly that was the point.", "I think we'll never know for certain."],
    ["The truth—if there was such a thing—seemed to shift depending on who was telling it.", "I definitely felt confused (or was it something else?).", "Maybe certainty itself was the illusion."],
    ["She believed (had always believed, really) that things would work out—though lately she'd begun to wonder.", "Perhaps hope was just another form of denial.", "Still, she couldn't quite let it go."],
    ["It was obvious—painfully obvious, actually—that something was wrong (though no one would say what).", "I might have been imagining things; I probably was.", "But the feeling persisted nonetheless."],
    ["He seemed certain (too certain, she thought) that he was right—even though the evidence suggested otherwise.", "Maybe confidence was its own kind of blindness.", "She definitely had her doubts."],
    ["The moment felt significant—or perhaps it just felt that way because I wanted it to.", "Certainly something shifted (or seemed to shift).", "Whether it mattered, I couldn't say."],
    ["I thought I understood (believed I did, anyway) what she meant—but maybe I was projecting.", "The words were clear; the meaning wasn't.", "Perhaps that was intentional; perhaps not."],
    ["She must have noticed (how could she not?) that things were different—and yet she said nothing.", "Maybe silence was its own kind of answer.", "I definitely didn't know how to read it."],
    ["The decision seemed right (felt right, at least) even though I couldn't explain why.", "Perhaps intuition was just rationality in disguise.", "Or maybe—probably—it was the opposite."],
    ["He knew (or thought he knew) exactly what would happen—which is perhaps why he was so surprised.", "Certainty, it turns out, is fragile.", "I believe that's the lesson; I'm not sure."],
    ["It was definitely (almost definitely) going to rain—though the sky, I noticed, had other plans.", "Perhaps forecasts were just organized guessing.", "Maybe everything was."],
    ["She felt certain (reasonably certain) that the answer was somewhere in the details—if only she could see them.", "The truth might be hiding in plain sight.", "Or possibly it wasn't there at all."],
    ["I believed—had convinced myself, really—that things would be different this time (though history suggested otherwise).", "Maybe hope was just memory with amnesia.", "Still, I couldn't help it."],
    ["The pattern was obvious (to me, anyway) even if no one else seemed to notice.", "Perhaps I was seeing things; perhaps I wasn't.", "Certainly it felt real."],
    ["He might have been lying (probably was, actually) but she couldn't quite prove it.", "The truth—whatever it was—remained elusive.", "Maybe that was the point."],
    ["It seemed important (felt important, anyway) to say something—though I wasn't sure what.", "Perhaps silence would have been better.", "I definitely regretted speaking."],
    ["She knew (must have known) that things couldn't continue this way—and yet they did.", "Maybe inertia was stronger than intention.", "I believe that's often true."],
    ["The answer was there (I was certain of it) hiding somewhere in the question itself.", "Perhaps understanding was just rearranging confusion.", "Or maybe—probably—I was overthinking."],
    ["He seemed to believe (genuinely believe) that none of it mattered—which is perhaps why it did.", "Indifference, I've noticed, has its own weight.", "Maybe that's the irony."],
    ["I thought (had always thought) that certainty would feel different—more solid, somehow.", "Perhaps doubt was just certainty's shadow.", "Or possibly its substance."],
    ["She was definitely (almost definitely) going to leave—though something (I'm not sure what) kept her there.", "Maybe leaving was harder than staying.", "Perhaps that's always true."],
    ["The truth seemed (felt, anyway) closer than it had before—though still just out of reach.", "Perhaps proximity was its own kind of torture.", "I definitely felt something."],
    ["He believed (claimed to believe) that everything happened for a reason—which might be true, or might be comfort.", "Certainly it was easier than randomness.", "Maybe that was enough."],
    ["It was obvious—should have been obvious, at least—that things had changed (though I couldn't say when).", "Perhaps change was just accumulation.", "I think that's how it works."],
    ["She must have felt (surely she felt?) that something was wrong—even if she couldn't name it.", "Maybe feelings didn't need names.", "Perhaps that was their power."],
    ["I knew (thought I knew) that the moment would pass—which is perhaps why I held on.", "Impermanence, it turns out, makes things precious.", "Or maybe just desperate."],
    ["The meaning—if there was one—seemed to depend on how you looked at it.", "Perhaps perspective was everything (or nothing).", "I definitely couldn't decide."],
]

# ============================================================
# CATEGORY 3: POETIC FRAGMENT, NON-STANDARD PUNCTUATION (30 samples)
# Operators as style, em-dashes, unconventional structure
# ============================================================

POETIC_SAMPLES = [
    ["Light & shadow & the space between—that's where it lives.", "Not in the saying / but in the almost-said.", "(And what does 'lives' even mean here?)"],
    ["Here / not here / the difference thin as breath.", "She moves through rooms like water through fingers.", "What stays & what goes—who decides?"],
    ["Morning—or what passes for it—arrives without announcement.", "The day / the night / the gray between.", "We measure time; it measures us back."],
    ["Words & silences & the weight of both.", "He speaks; she listens / she speaks; he's gone.", "(The conversation continues anyway.)"],
    ["Time folds: now / then / the blurring edge.", "Memory is just imagination facing backward.", "What we remember & what remembers us—different things."],
    ["The window—half-open, half-closed—frames nothing in particular.", "Inside / outside / the glass deciding.", "She watches the watching."],
    ["Sound & silence & the pause between heartbeats.", "The music stops; the room keeps humming.", "What we hear / what we listen for—not the same."],
    ["Here: the moment, whole & unbroken.", "There: the same moment, already dissolving.", "(Time does this; we just notice.)"],
    ["Love / loss / the comma between.", "She holds what isn't there anymore.", "The shape of absence—that's what stays."],
    ["Light through leaves / leaves through light—which one's moving?", "The tree & its shadow have a conversation.", "We only hear half."],
    ["The edge of things—that's where meaning hides.", "Not in centers / but in margins.", "(The margins are wider than we think.)"],
    ["She writes & erases & writes again.", "The words underneath show through anyway.", "Palimpsest—that's what we are."],
    ["Now / then / the thin wall between.", "Memory leaks; the past gets in.", "We clean up what we can."],
    ["Sound—or the shape of sound—fills the room.", "Vibration / air / the ear's translation.", "What we call 'music' is just agreement."],
    ["The photograph—fading, curling at edges—still holds.", "Then & now / here & there.", "(Time flattens in two dimensions.)"],
    ["Breath & breadth & the lungs' slow question.", "She inhales the morning; it changes her.", "What enters / what leaves—chemistry or poetry?"],
    ["The door between—neither open nor closed—waits.", "Threshold: the word itself hesitates.", "We stand here often; we rarely notice."],
    ["Water / stone / the long negotiation.", "The river wins; the rock doesn't care.", "(Winning isn't everything; patience is.)"],
    ["Here's the thing about edges—they're also beginnings.", "End / start / the fold where they meet.", "She traces the crease."],
    ["Color & light & the eye's soft compromise.", "We see what we can; the rest goes dark.", "The visible is just the local."],
    ["The room—empty now—still holds the shape of presence.", "Where she sat / where he stood.", "Absence has its own geography."],
    ["Sound travels; silence stays put.", "The voice / the echo / the space between.", "(Rooms remember what we said.)"],
    ["Morning light / evening shadow—the day's parentheses.", "What happens between gets bracketed.", "We call it 'living.'"],
    ["She & the mirror & the third thing watching.", "Reflection / refraction / the truth somewhere else.", "The glass keeps its secrets."],
    ["The word—spoken, then gone—leaves residue.", "Meaning / sound / the evaporating middle.", "What stays is what we can't quite hear."],
    ["Time / space / the grammar of being.", "He conjugates presence: am, was, will be.", "(The tenses don't quite fit.)"],
    ["Here: the letter, unopened.", "There: the words inside, waiting.", "The envelope—that's the real message."],
    ["Light & dark & the dimmer between.", "She adjusts; the room adjusts back.", "Control is just responsive hoping."],
    ["The line breaks—here / or here—matter.", "Breath / pause / the white space speaking.", "Poetry is just arranged silence."],
    ["Now & then & the bridge of always.", "She crosses back and forth.", "(The tolls are invisible but real.)"],
]

def run_analysis(sentences, sample_id, category):
    """Run a sample through LNCP and return key metrics"""
    try:
        result = quick_analyze(
            sentences=sentences,
            phase4_mode="PROMPTING"
        )
        
        # Extract key metrics from nested structure
        phase1 = result.get('phase1', {})
        outputs = phase1.get('outputs', {})
        phase2 = result.get('phase2', {})
        hi_profile = result.get('high_intent_profile', {})
        
        # Get metrics from nested outputs
        sentence_count = outputs.get('sentence_count', {}).get('metrics', {}).get('sentence_count', 0)
        word_count = outputs.get('token_volume', {}).get('metrics', {}).get('total_token_count', 0)
        avg_words = outputs.get('token_volume', {}).get('metrics', {}).get('mean_tokens_per_sentence', 0)
        zero_events = outputs.get('zero_event_presence', {}).get('metrics', {}).get('total_zero_event_count', 0)
        operator_events = outputs.get('operator_event_presence', {}).get('metrics', {}).get('total_operator_event_count', 0)
        scope_events = outputs.get('scope_event_presence', {}).get('metrics', {}).get('total_scope_event_count', 0)
        variety_ratio = outputs.get('structural_variety', {}).get('metrics', {}).get('signature_variety_ratio', 0)
        
        return {
            'sample_id': sample_id,
            'category': category,
            'sentences': sentences,
            'sentence_count': sentence_count,
            'word_count': word_count,
            'avg_words': avg_words,
            'variety_ratio': variety_ratio,
            'zero_events': zero_events,
            'operator_events': operator_events,
            'scope_events': scope_events,
            'hi_markers': hi_profile.get('unique_markers', []),
            'hi_count': hi_profile.get('total_high_intent_events', 0),
            'epistemic_stance': hi_profile.get('epistemic_stance', 'UNKNOWN'),
            'epistemic_openness': hi_profile.get('epistemic_openness', 0.5),
            'presentation_mode': phase2.get('presentation_mode', 'UNKNOWN'),
            # v0.5.0 new fields
            'is_contradictory': hi_profile.get('is_contradictory', False),
            'is_minimal': hi_profile.get('is_minimal', False),
            'is_poetic_mode': hi_profile.get('is_poetic_mode', False),
            'emdash_count': hi_profile.get('emdash_count', 0),
            'opening_markers': hi_profile.get('opening_marker_count', 0),
            'closing_markers': hi_profile.get('closing_marker_count', 0),
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'sample_id': sample_id,
            'category': category,
            'sentences': sentences,
            'success': False,
            'error': str(e)
        }

def main():
    print("=" * 70)
    print("LNCP CHALLENGE TEST SUITE")
    print("90 samples across 3 structure categories")
    print("=" * 70)
    print()
    
    all_results = []
    
    # Category 1: Minimal
    print("CATEGORY 1: MINIMAL STRUCTURE (30 samples)")
    print("-" * 50)
    minimal_results = []
    for i, sample in enumerate(MINIMAL_SAMPLES):
        result = run_analysis(sample, f"MIN_{i+1:02d}", "MINIMAL")
        minimal_results.append(result)
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"  {status} MIN_{i+1:02d}: {result['word_count']} words, {result['hi_count']} markers, {result['scope_events']} scope")
        else:
            print(f"  {status} MIN_{i+1:02d}: ERROR - {result['error']}")
    all_results.extend(minimal_results)
    print()
    
    # Category 2: Dense
    print("CATEGORY 2: DENSE NESTING (30 samples)")
    print("-" * 50)
    dense_results = []
    for i, sample in enumerate(DENSE_SAMPLES):
        result = run_analysis(sample, f"DNS_{i+1:02d}", "DENSE")
        dense_results.append(result)
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"  {status} DNS_{i+1:02d}: {result['word_count']} words, {result['hi_count']} markers, {result['scope_events']} scope")
        else:
            print(f"  {status} DNS_{i+1:02d}: ERROR - {result['error']}")
    all_results.extend(dense_results)
    print()
    
    # Category 3: Poetic
    print("CATEGORY 3: POETIC FRAGMENT (30 samples)")
    print("-" * 50)
    poetic_results = []
    for i, sample in enumerate(POETIC_SAMPLES):
        result = run_analysis(sample, f"POE_{i+1:02d}", "POETIC")
        poetic_results.append(result)
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"  {status} POE_{i+1:02d}: {result['word_count']} words, {result['hi_count']} markers, {result['scope_events']} scope")
        else:
            print(f"  {status} POE_{i+1:02d}: ERROR - {result['error']}")
    all_results.extend(poetic_results)
    print()
    
    # Summary statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    
    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]
    
    print(f"\nOverall: {len(successful)}/90 successful, {len(failed)} failed")
    
    if failed:
        print(f"\nFailed samples:")
        for f in failed:
            print(f"  - {f['sample_id']}: {f['error']}")
    
    # Per-category stats
    for cat_name, cat_results in [("MINIMAL", minimal_results), ("DENSE", dense_results), ("POETIC", poetic_results)]:
        cat_success = [r for r in cat_results if r['success']]
        if not cat_success:
            print(f"\n{cat_name}: No successful analyses")
            continue
            
        avg_words = sum(r['word_count'] for r in cat_success) / len(cat_success)
        avg_hi = sum(r['hi_count'] for r in cat_success) / len(cat_success)
        avg_scope = sum(r['scope_events'] for r in cat_success) / len(cat_success)
        avg_operator = sum(r['operator_events'] for r in cat_success) / len(cat_success)
        avg_zero = sum(r['zero_events'] for r in cat_success) / len(cat_success)
        
        # Count samples with zero markers
        zero_marker_samples = [r for r in cat_success if r['hi_count'] == 0]
        
        print(f"\n{cat_name} ({len(cat_success)}/30 successful):")
        print(f"  Avg words: {avg_words:.1f}")
        print(f"  Avg high-intent markers: {avg_hi:.1f}")
        print(f"  Avg scope events: {avg_scope:.1f}")
        print(f"  Avg operator events: {avg_operator:.1f}")
        print(f"  Avg zero events: {avg_zero:.1f}")
        print(f"  Samples with NO markers: {len(zero_marker_samples)}")
        
        # Most common markers
        all_markers = []
        for r in cat_success:
            all_markers.extend(r.get('hi_markers', []))
        if all_markers:
            from collections import Counter
            marker_counts = Counter(all_markers).most_common(5)
            print(f"  Top markers: {marker_counts}")
    
    # Edge case analysis
    print("\n" + "=" * 70)
    print("EDGE CASE ANALYSIS")
    print("=" * 70)
    
    # Samples with no markers at all
    no_markers = [r for r in successful if r['hi_count'] == 0]
    print(f"\nSamples with ZERO high-intent markers: {len(no_markers)}")
    for r in no_markers[:5]:
        print(f"  - {r['sample_id']}: \"{r['sentences'][0][:40]}...\"")
    
    # Samples with very high marker count
    high_markers = [r for r in successful if r['hi_count'] >= 5]
    print(f"\nSamples with 5+ high-intent markers: {len(high_markers)}")
    for r in sorted(high_markers, key=lambda x: x['hi_count'], reverse=True)[:5]:
        print(f"  - {r['sample_id']}: {r['hi_count']} markers - {r['hi_markers'][:5]}")
    
    # Samples with high scope events (parentheticals)
    high_scope = [r for r in successful if r['scope_events'] >= 3]
    print(f"\nSamples with 3+ scope events: {len(high_scope)}")
    for r in sorted(high_scope, key=lambda x: x['scope_events'], reverse=True)[:5]:
        print(f"  - {r['sample_id']}: {r['scope_events']} scope events")
    
    # Samples with operator events
    has_operators = [r for r in successful if r['operator_events'] >= 1]
    print(f"\nSamples with operator events (/ & etc): {len(has_operators)}")
    for r in sorted(has_operators, key=lambda x: x['operator_events'], reverse=True)[:5]:
        print(f"  - {r['sample_id']}: {r['operator_events']} operator events")
    
    # v0.5.0 Analysis
    print("\n" + "=" * 70)
    print("v0.5.0 ANALYSIS")
    print("=" * 70)
    
    # CONTRADICTORY stance detection
    contradictory = [r for r in successful if r.get('is_contradictory', False)]
    print(f"\nSamples with CONTRADICTORY stance: {len(contradictory)}")
    for r in contradictory[:5]:
        print(f"  - {r['sample_id']}: opening={r.get('opening_markers',0)}, closing={r.get('closing_markers',0)}")
    
    # MINIMAL stance detection
    minimal = [r for r in successful if r.get('is_minimal', False)]
    print(f"\nSamples with MINIMAL stance: {len(minimal)}")
    
    # Poetic mode detection
    poetic = [r for r in successful if r.get('is_poetic_mode', False)]
    print(f"\nSamples detected as POETIC MODE: {len(poetic)}")
    for r in poetic[:5]:
        print(f"  - {r['sample_id']}: operators={r['operator_events']}, em-dashes={r.get('emdash_count',0)}")
    
    # Em-dash tracking
    has_emdash = [r for r in successful if r.get('emdash_count', 0) > 0]
    print(f"\nSamples with em-dashes: {len(has_emdash)}")
    for r in sorted(has_emdash, key=lambda x: x.get('emdash_count', 0), reverse=True)[:5]:
        print(f"  - {r['sample_id']}: {r.get('emdash_count', 0)} em-dashes")
    
    # Stance distribution
    print("\nStance Distribution (v0.5.0):")
    stance_counts = {}
    for r in successful:
        stance = r.get('epistemic_stance', 'UNKNOWN')
        stance_counts[stance] = stance_counts.get(stance, 0) + 1
    for stance, count in sorted(stance_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {stance}: {count}")
    
    # Save full results
    with open('/home/claude/lncp-web-app/challenge_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("Full results saved to challenge_test_results.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
