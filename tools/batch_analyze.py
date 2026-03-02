#!/usr/bin/env python3
"""
QUIRRELY BATCH ANALYSIS CLI v1.0
Test LNCP v3.8 locally with sample texts.

Usage:
    python batch_analyze.py --file samples.txt
    python batch_analyze.py --dir ./texts/
    python batch_analyze.py --text "Your text here"
    python batch_analyze.py --interactive
    
Options:
    --file FILE       Analyze texts from a file (one per line or JSON)
    --dir DIR         Analyze all .txt files in a directory
    --text TEXT       Analyze a single text string
    --interactive     Interactive mode - enter texts one at a time
    --output FILE     Output results to file (JSON)
    --format FORMAT   Output format: json, csv, table (default: table)
    --verbose         Show detailed metrics
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════════════════════
# LNCP v3.8 CLASSIFIER (embedded for standalone use)
# ═══════════════════════════════════════════════════════════════════════════

PROFILE_META = {
    'ASSERTIVE-OPEN': {'title': 'The Confident Listener', 'icon': '🎯'},
    'ASSERTIVE-CLOSED': {'title': 'The Commander', 'icon': '⚡'},
    'ASSERTIVE-BALANCED': {'title': 'The Measured Leader', 'icon': '⚖️'},
    'ASSERTIVE-CONTRADICTORY': {'title': 'The Confident Paradox', 'icon': '🎭'},
    'MINIMAL-OPEN': {'title': 'The Quiet Inviter', 'icon': '🌿'},
    'MINIMAL-CLOSED': {'title': 'The Essentialist', 'icon': '💎'},
    'MINIMAL-BALANCED': {'title': 'The Brief Diplomat', 'icon': '🪶'},
    'MINIMAL-CONTRADICTORY': {'title': 'The Zen Paradox', 'icon': '☯️'},
    'POETIC-OPEN': {'title': 'The Lyrical Explorer', 'icon': '🌊'},
    'POETIC-CLOSED': {'title': 'The Oracle', 'icon': '🔮'},
    'POETIC-BALANCED': {'title': 'The Dual Painter', 'icon': '🎨'},
    'POETIC-CONTRADICTORY': {'title': 'The Shadow Dancer', 'icon': '🌓'},
    'DENSE-OPEN': {'title': 'The Curious Scholar', 'icon': '📚'},
    'DENSE-CLOSED': {'title': 'The Authority', 'icon': '🏛️'},
    'DENSE-BALANCED': {'title': 'The Synthesizer', 'icon': '🔬'},
    'DENSE-CONTRADICTORY': {'title': 'The Complexity Theorist', 'icon': '🌀'},
    'CONVERSATIONAL-OPEN': {'title': 'The Curious Friend', 'icon': '💬'},
    'CONVERSATIONAL-CLOSED': {'title': 'The Straight Talker', 'icon': '🎤'},
    'CONVERSATIONAL-BALANCED': {'title': 'The Thoughtful Pal', 'icon': '🤝'},
    'CONVERSATIONAL-CONTRADICTORY': {'title': 'The Honest Mess', 'icon': '🫶'},
    'FORMAL-OPEN': {'title': 'The Diplomatic Professional', 'icon': '📋'},
    'FORMAL-CLOSED': {'title': 'The Executive', 'icon': '🏢'},
    'FORMAL-BALANCED': {'title': 'The Impartial Analyst', 'icon': '📊'},
    'FORMAL-CONTRADICTORY': {'title': 'The Institutional Realist', 'icon': '🏗️'},
    'BALANCED-OPEN': {'title': 'The Humble Seeker', 'icon': '🔍'},
    'BALANCED-CLOSED': {'title': 'The Fair Judge', 'icon': '⚖️'},
    'BALANCED-BALANCED': {'title': 'The True Moderate', 'icon': '🎚️'},
    'BALANCED-CONTRADICTORY': {'title': 'The Tension Holder', 'icon': '🔀'},
    'LONGFORM-OPEN': {'title': 'The Patient Explorer', 'icon': '🗺️'},
    'LONGFORM-CLOSED': {'title': 'The Thorough Advocate', 'icon': '📖'},
    'LONGFORM-BALANCED': {'title': 'The Deep Diver', 'icon': '🌊'},
    'LONGFORM-CONTRADICTORY': {'title': 'The Complexity Navigator', 'icon': '🧭'},
    'INTERROGATIVE-OPEN': {'title': 'The Questioner', 'icon': '❓'},
    'INTERROGATIVE-CLOSED': {'title': 'The Socratic', 'icon': '🏺'},
    'INTERROGATIVE-BALANCED': {'title': 'The Facilitator', 'icon': '🎯'},
    'INTERROGATIVE-CONTRADICTORY': {'title': 'The Koan Master', 'icon': '🪷'},
    'HEDGED-OPEN': {'title': 'The Tentative Thinker', 'icon': '🌱'},
    'HEDGED-CLOSED': {'title': 'The Careful Concluder', 'icon': '🎓'},
    'HEDGED-BALANCED': {'title': 'The Nuanced Voice', 'icon': '🌫️'},
    'HEDGED-CONTRADICTORY': {'title': 'The Uncertain Sage', 'icon': '💭'},
}

def count_words(text: str) -> int:
    return len(text.split())

def count_sentences(text: str) -> int:
    import re
    return len(re.findall(r'[.!?]+', text)) or 1

def analyze_text_simple(text: str) -> Dict[str, Any]:
    """Simplified LNCP analysis for CLI tool."""
    words = text.split()
    word_count = len(words)
    sentences = count_sentences(text)
    avg_sentence_length = word_count / max(sentences, 1)
    
    questions = text.count('?')
    exclamations = text.count('!')
    first_person = sum(1 for w in words if w.lower() in ['i', 'me', 'my', 'mine', 'we', 'us', 'our'])
    hedging_words = sum(1 for w in words if w.lower() in ['perhaps', 'maybe', 'might', 'could', 'possibly', 'seems', 'appears', 'likely'])
    assertive_words = sum(1 for w in words if w.lower() in ['must', 'will', 'certainly', 'clearly', 'obviously', 'definitely', 'always', 'never'])
    
    question_rate = questions / max(sentences, 1)
    first_person_rate = first_person / max(word_count, 1)
    hedging_rate = hedging_words / max(word_count, 1)
    assertive_rate = assertive_words / max(word_count, 1)
    
    # Determine profile type
    profile_type = 'CONVERSATIONAL'
    
    if question_rate > 0.4:
        profile_type = 'INTERROGATIVE'
    elif hedging_rate > 0.03:
        profile_type = 'HEDGED'
    elif assertive_rate > 0.02 and avg_sentence_length < 15:
        profile_type = 'ASSERTIVE'
    elif avg_sentence_length < 8 and word_count < 100:
        profile_type = 'MINIMAL'
    elif avg_sentence_length > 25:
        profile_type = 'DENSE'
    elif sentences > 5 and first_person_rate > 0.03:
        profile_type = 'LONGFORM'
    elif first_person_rate < 0.01 and hedging_rate < 0.01:
        profile_type = 'FORMAL'
    elif 'on one hand' in text.lower() or 'on the other' in text.lower():
        profile_type = 'BALANCED'
    elif avg_sentence_length > 15 and any(w in text.lower() for w in ['rhythm', 'flow', 'beauty', 'light', 'shadow', 'dream']):
        profile_type = 'POETIC'
    
    # Determine stance
    stance = 'BALANCED'
    
    if question_rate > 0.2 or 'what do you think' in text.lower() or first_person_rate > 0.05:
        stance = 'OPEN'
    elif assertive_rate > 0.015 and question_rate < 0.1:
        stance = 'CLOSED'
    elif 'both' in text.lower() and ('true' in text.lower() or 'right' in text.lower()):
        stance = 'CONTRADICTORY'
    
    profile_id = f"{profile_type}-{stance}"
    meta = PROFILE_META.get(profile_id, {'title': profile_id, 'icon': '📝'})
    
    confidence = 0.7
    if word_count > 100:
        confidence += 0.1
    if word_count > 200:
        confidence += 0.05
    confidence = min(confidence, 0.95)
    
    return {
        'profile_id': profile_id,
        'profile_type': profile_type,
        'stance': stance,
        'title': meta['title'],
        'icon': meta['icon'],
        'confidence': round(confidence, 2),
        'metrics': {
            'word_count': word_count,
            'sentence_count': sentences,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'question_rate': round(question_rate * 100, 1),
            'first_person_rate': round(first_person_rate * 100, 2),
            'hedging_rate': round(hedging_rate * 100, 2),
            'assertive_rate': round(assertive_rate * 100, 2),
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLI FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def analyze_single(text: str, verbose: bool = False) -> Dict[str, Any]:
    """Analyze a single text."""
    result = analyze_text_simple(text)
    result['text_preview'] = text[:100] + '...' if len(text) > 100 else text
    result['analyzed_at'] = datetime.utcnow().isoformat() + 'Z'
    return result


def analyze_file(filepath: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """Analyze texts from a file."""
    results = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        data = json.loads(content)
        if isinstance(data, list):
            texts = [item.get('text', item) if isinstance(item, dict) else item for item in data]
        else:
            texts = [content]
    except json.JSONDecodeError:
        if '\n\n' in content:
            texts = [t.strip() for t in content.split('\n\n') if t.strip()]
        else:
            texts = [content]
    
    for i, text in enumerate(texts):
        if len(text) < 50:
            continue
        result = analyze_single(text, verbose)
        result['source'] = f"{filepath}#{i+1}"
        results.append(result)
    
    return results


def analyze_directory(dirpath: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """Analyze all .txt files in a directory."""
    results = []
    dir_path = Path(dirpath)
    
    for filepath in sorted(dir_path.glob('*.txt')):
        text = filepath.read_text(encoding='utf-8')
        if len(text) < 50:
            continue
        result = analyze_single(text, verbose)
        result['source'] = str(filepath)
        results.append(result)
    
    return results


def format_table(results: List[Dict[str, Any]], verbose: bool = False) -> str:
    """Format results as a table."""
    lines = []
    
    if verbose:
        header = f"{'#':<3} {'Profile':<25} {'Type':<15} {'Stance':<12} {'Conf':<6} {'Words':<6} {'Sents':<5} {'Q%':<5}"
    else:
        header = f"{'#':<3} {'Profile':<25} {'Type':<15} {'Stance':<12} {'Conf':<6} {'Words':<6}"
    
    lines.append('=' * len(header))
    lines.append(header)
    lines.append('=' * len(header))
    
    for i, r in enumerate(results, 1):
        m = r.get('metrics', {})
        if verbose:
            row = f"{i:<3} {r['title']:<25} {r['profile_type']:<15} {r['stance']:<12} {r['confidence']:<6} {m.get('word_count', 0):<6} {m.get('sentence_count', 0):<5} {m.get('question_rate', 0):<5}"
        else:
            row = f"{i:<3} {r['title']:<25} {r['profile_type']:<15} {r['stance']:<12} {r['confidence']:<6} {m.get('word_count', 0):<6}"
        lines.append(row)
    
    lines.append('=' * len(header))
    lines.append(f"Total: {len(results)} texts analyzed")
    
    return '\n'.join(lines)


def format_csv(results: List[Dict[str, Any]]) -> str:
    """Format results as CSV."""
    lines = ['profile_id,profile_type,stance,title,confidence,word_count,sentence_count,question_rate']
    
    for r in results:
        m = r.get('metrics', {})
        line = f"{r['profile_id']},{r['profile_type']},{r['stance']},\"{r['title']}\",{r['confidence']},{m.get('word_count', 0)},{m.get('sentence_count', 0)},{m.get('question_rate', 0)}"
        lines.append(line)
    
    return '\n'.join(lines)


def interactive_mode(verbose: bool = False):
    """Interactive analysis mode."""
    print("\n" + "=" * 60)
    print("QUIRRELY BATCH ANALYZER — Interactive Mode")
    print("=" * 60)
    print("Enter text to analyze (min 50 characters)")
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for commands")
    print("=" * 60 + "\n")
    
    results_history = []
    
    while True:
        try:
            print("\n📝 Enter text (or paste multiple lines, then press Enter twice):")
            lines = []
            while True:
                line = input()
                if line == '':
                    if lines:
                        break
                    continue
                lines.append(line)
                if line.lower() in ('quit', 'exit', 'q'):
                    break
            
            text = ' '.join(lines).strip()
            
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break
        
        if text.lower() in ('quit', 'exit', 'q'):
            print("\nGoodbye!")
            break
        
        if text.lower() == 'help':
            print("\nCommands:")
            print("  quit/exit/q  - Exit interactive mode")
            print("  help         - Show this help")
            print("  history      - Show analysis history")
            print("  export       - Export history to JSON")
            continue
        
        if text.lower() == 'history':
            if results_history:
                print(format_table(results_history, verbose))
            else:
                print("No analyses yet.")
            continue
        
        if text.lower() == 'export':
            if results_history:
                filename = f"quirrely_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(results_history, f, indent=2)
                print(f"Exported to {filename}")
            else:
                print("No analyses to export.")
            continue
        
        if len(text) < 50:
            print(f"⚠️  Text too short ({len(text)} chars). Need at least 50.")
            continue
        
        # Analyze
        result = analyze_single(text, verbose)
        results_history.append(result)
        
        # Display
        print(f"\n{'─' * 50}")
        print(f"{result['icon']} {result['title']}")
        print(f"   {result['profile_type']} + {result['stance']}")
        print(f"   Confidence: {int(result['confidence'] * 100)}%")
        
        if verbose:
            m = result['metrics']
            print(f"\n   Metrics:")
            print(f"   • Words: {m['word_count']}")
            print(f"   • Sentences: {m['sentence_count']}")
            print(f"   • Avg sentence: {m['avg_sentence_length']} words")
            print(f"   • Questions: {m['question_rate']}%")
            print(f"   • First person: {m['first_person_rate']}%")
            print(f"   • Hedging: {m['hedging_rate']}%")
            print(f"   • Assertive: {m['assertive_rate']}%")
        
        print(f"{'─' * 50}")


# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE TEXTS FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_TEXTS = [
    {
        "name": "Assertive Closed",
        "text": "This is the way it must be done. There is no alternative. The evidence clearly shows that our approach works. We will proceed accordingly. End of discussion."
    },
    {
        "name": "Hedged Open",
        "text": "I think, perhaps, there might be something worth considering here. It seems like the data could suggest a pattern, though I'm not entirely certain. What do you think? Maybe we should explore this further together?"
    },
    {
        "name": "Interrogative",
        "text": "What if we looked at this differently? Have you considered the alternative? Why do we assume the current approach is correct? Isn't it possible that we've been missing something fundamental all along?"
    },
    {
        "name": "Formal Balanced",
        "text": "The committee has reviewed the evidence presented by both parties. While the initial proposal demonstrates merit in several key areas, the alternative approach also presents compelling arguments. The organization will consider both perspectives before rendering a final determination."
    },
    {
        "name": "Conversational Open",
        "text": "So here's the thing—I've been thinking about this a lot lately, and I'm honestly not sure where I land. On one hand, I can see the appeal. On the other hand, there are some real concerns. What's your take on it? I'd love to hear what you think."
    },
]


def run_samples():
    """Run analysis on sample texts."""
    print("\n" + "=" * 60)
    print("QUIRRELY BATCH ANALYZER — Sample Analysis")
    print("=" * 60 + "\n")
    
    results = []
    for sample in SAMPLE_TEXTS:
        print(f"Analyzing: {sample['name']}...")
        result = analyze_single(sample['text'])
        result['expected'] = sample['name']
        results.append(result)
    
    print("\n" + format_table(results, verbose=True))
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Quirrely Batch Analysis CLI - Test LNCP v3.8 locally',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python batch_analyze.py --samples              Run built-in sample texts
    python batch_analyze.py --text "Your text"    Analyze single text
    python batch_analyze.py --file texts.txt      Analyze from file
    python batch_analyze.py --dir ./samples/      Analyze directory
    python batch_analyze.py --interactive         Interactive mode
        """
    )
    
    parser.add_argument('--file', '-f', help='Analyze texts from a file')
    parser.add_argument('--dir', '-d', help='Analyze all .txt files in directory')
    parser.add_argument('--text', '-t', help='Analyze a single text string')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--samples', '-s', action='store_true', help='Run sample analyses')
    parser.add_argument('--output', '-o', help='Output file (JSON)')
    parser.add_argument('--format', choices=['json', 'csv', 'table'], default='table', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed metrics')
    
    args = parser.parse_args()
    
    results = []
    
    # Determine mode
    if args.samples:
        results = run_samples()
    elif args.interactive:
        interactive_mode(args.verbose)
        return
    elif args.text:
        if len(args.text) < 50:
            print(f"Error: Text too short ({len(args.text)} chars). Need at least 50.")
            sys.exit(1)
        results = [analyze_single(args.text, args.verbose)]
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        results = analyze_file(args.file, args.verbose)
    elif args.dir:
        if not os.path.isdir(args.dir):
            print(f"Error: Directory not found: {args.dir}")
            sys.exit(1)
        results = analyze_directory(args.dir, args.verbose)
    else:
        # Default to samples if no input provided
        print("No input specified. Running sample analyses...\n")
        results = run_samples()
    
    # Format output
    if results:
        if args.format == 'json':
            output = json.dumps(results, indent=2)
        elif args.format == 'csv':
            output = format_csv(results)
        else:
            output = format_table(results, args.verbose)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nResults written to: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
