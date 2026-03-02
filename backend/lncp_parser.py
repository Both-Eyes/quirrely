#!/usr/bin/env python3
"""
LNCP Sentence Parser
Version: 0.6.0

Converts raw sentences into LNCP canonical format (v1.1.3-draft).

This parser implements the LNCP structural analysis:
- Tokenization
- Ticker code assignment (structural position codes)
- Event detection (zero, operator, scope, em-dash)
- High-Intent word detection (modal/epistemic markers)
- Base signature generation
- Rhetorical mode detection (v0.6.0)

CHANGELOG v0.6.0:
- Added ASSERTIVE mode detection (short, confident, imperative)
- Added INTERROGATIVE mode detection (question-heavy)
- Added register detection (FORMAL/INFORMAL)
- Added anaphora/repetition detection
- Added syntax complexity metric (clause counting)
- Added em-dash pair detection for parenthetical usage

CHANGELOG v0.5.0:
- Updated High-Intent lexicon v0.5.0 (removed 'were' false positive)
- Added CONTRADICTORY stance detection
- Added em-dash boundary tracking (separate from scope events)
- Added poetic mode detection
- Improved minimal feedback support

CHANGELOG v0.2.0:
- Added High-Intent word detection using modal/epistemic lexicon
- Added high_intent_events to canonical row output
- Added aggregate High-Intent metrics

NOTE: This is the web app application layer parser.
High-Intent detection is a web-app feature, not part of LNCP core.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# =============================================================================
# Lexicon Loading
# =============================================================================

_LEXICON_CACHE: Optional[Dict[str, Any]] = None
_LEXICON_PATH = Path(__file__).parent / "high_intent_lexicon_v0.5.0.json"


def load_high_intent_lexicon() -> Dict[str, Any]:
    """Load the High-Intent lexicon from JSON file."""
    global _LEXICON_CACHE
    
    if _LEXICON_CACHE is not None:
        return _LEXICON_CACHE
    
    if not _LEXICON_PATH.exists():
        # Return empty lexicon if file not found
        return {"categories": {}, "multi_word_expressions": {"expressions": []}}
    
    with open(_LEXICON_PATH, "r", encoding="utf-8") as f:
        _LEXICON_CACHE = json.load(f)
    
    return _LEXICON_CACHE


def get_high_intent_word_sets() -> Tuple[Dict[str, Set[str]], List[str]]:
    """
    Get High-Intent word sets organized by category.
    
    Returns:
        (category_to_words, multi_word_expressions)
    """
    lexicon = load_high_intent_lexicon()
    
    category_to_words: Dict[str, Set[str]] = {}
    for cat_name, cat_data in lexicon.get("categories", {}).items():
        words = cat_data.get("words", [])
        category_to_words[cat_name] = {w.lower() for w in words}
    
    multi_word = lexicon.get("multi_word_expressions", {}).get("expressions", [])
    # Sort by length descending so longer expressions match first
    multi_word = sorted(multi_word, key=len, reverse=True)
    
    return category_to_words, multi_word


# =============================================================================
# Ticker Code Definitions
# =============================================================================

# Code 1: Articles, determiners
# Code 2: Prepositions, conjunctions
# Code 3: Pronouns, common nouns
# Code 4: Verbs, adverbs, adjectives
# Code 5: Proper nouns, special

ARTICLES = {"a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their", "some", "any", "no", "every", "each", "all", "both", "few", "many", "much", "most"}
PREPOSITIONS = {"in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "down", "out", "into", "over", "under", "through", "between", "among", "about", "against", "after", "before", "during", "without", "within", "along", "around", "behind", "below", "beneath", "beside", "beyond", "near", "off", "onto", "toward", "towards", "upon"}
CONJUNCTIONS = {"and", "or", "but", "nor", "yet", "so", "for", "because", "although", "though", "while", "if", "unless", "until", "when", "where", "whether", "as", "than", "that", "which", "who", "whom", "whose"}
PRONOUNS = {"i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "we", "us", "our", "ours", "ourselves", "they", "them", "their", "theirs", "themselves", "who", "whom", "whose", "which", "what", "this", "that", "these", "those", "one", "ones", "someone", "anyone", "everyone", "no one", "nobody", "somebody", "anybody", "everybody", "something", "anything", "everything", "nothing"}
COMMON_VERBS = {"is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "will", "would", "shall", "should", "may", "might", "must", "can", "could", "go", "goes", "went", "gone", "going", "come", "comes", "came", "coming", "get", "gets", "got", "getting", "make", "makes", "made", "making", "take", "takes", "took", "taken", "taking", "see", "sees", "saw", "seen", "seeing", "know", "knows", "knew", "known", "knowing", "think", "thinks", "thought", "thinking", "want", "wants", "wanted", "wanting", "use", "uses", "used", "using", "find", "finds", "found", "finding", "give", "gives", "gave", "given", "giving", "tell", "tells", "told", "telling", "work", "works", "worked", "working", "seem", "seems", "seemed", "seeming", "feel", "feels", "felt", "feeling", "try", "tries", "tried", "trying", "leave", "leaves", "left", "leaving", "call", "calls", "called", "calling", "keep", "keeps", "kept", "keeping", "let", "lets", "letting", "begin", "begins", "began", "begun", "beginning", "help", "helps", "helped", "helping", "show", "shows", "showed", "shown", "showing", "hear", "hears", "heard", "hearing", "play", "plays", "played", "playing", "run", "runs", "ran", "running", "move", "moves", "moved", "moving", "live", "lives", "lived", "living", "believe", "believes", "believed", "believing", "hold", "holds", "held", "holding", "bring", "brings", "brought", "bringing", "happen", "happens", "happened", "happening", "write", "writes", "wrote", "written", "writing", "sit", "sits", "sat", "sitting", "stand", "stands", "stood", "standing", "lose", "loses", "lost", "losing", "pay", "pays", "paid", "paying", "meet", "meets", "met", "meeting", "include", "includes", "included", "including", "continue", "continues", "continued", "continuing", "set", "sets", "setting", "learn", "learns", "learned", "learning", "change", "changes", "changed", "changing", "lead", "leads", "led", "leading", "understand", "understands", "understood", "understanding", "watch", "watches", "watched", "watching", "follow", "follows", "followed", "following", "stop", "stops", "stopped", "stopping", "create", "creates", "created", "creating", "speak", "speaks", "spoke", "spoken", "speaking", "read", "reads", "reading", "spend", "spends", "spent", "spending", "grow", "grows", "grew", "grown", "growing", "open", "opens", "opened", "opening", "walk", "walks", "walked", "walking", "win", "wins", "won", "winning", "offer", "offers", "offered", "offering", "remember", "remembers", "remembered", "remembering", "love", "loves", "loved", "loving", "consider", "considers", "considered", "considering", "appear", "appears", "appeared", "appearing", "buy", "buys", "bought", "buying", "wait", "waits", "waited", "waiting", "serve", "serves", "served", "serving", "die", "dies", "died", "dying", "send", "sends", "sent", "sending", "expect", "expects", "expected", "expecting", "build", "builds", "built", "building", "stay", "stays", "stayed", "staying", "fall", "falls", "fell", "fallen", "falling", "cut", "cuts", "cutting", "reach", "reaches", "reached", "reaching", "kill", "kills", "killed", "killing", "remain", "remains", "remained", "remaining", "suggest", "suggests", "suggested", "suggesting", "raise", "raises", "raised", "raising", "pass", "passes", "passed", "passing", "sell", "sells", "sold", "selling", "require", "requires", "required", "requiring", "report", "reports", "reported", "reporting", "decide", "decides", "decided", "deciding", "pull", "pulls", "pulled", "pulling"}

# Zero event markers (ellipsis, dashes indicating pause/omission)
ZERO_PATTERNS = [
    r'\.{3,}',      # Ellipsis
    r'—',           # Em dash
    r'–',           # En dash
    r'\s-\s',       # Spaced hyphen as pause
]

# Operator event markers (connective symbols)
OPERATOR_PATTERNS = [
    r'/',           # Slash (and/or, either/or)
    r'&',           # Ampersand
    r'\+',          # Plus
    r'@',           # At symbol
    r'#',           # Hash
    r'%',           # Percent
    r'\*',          # Asterisk (when not italics)
]

# Scope event markers (nesting/bracketing)
SCOPE_PATTERNS = [
    r'\([^)]+\)',   # Parentheses
    r'\[[^\]]+\]',  # Square brackets
    r'\{[^}]+\}',   # Curly braces
    r'"[^"]*"',     # Double quotes
    r"'[^']*'",     # Single quotes (longer than one char)
]


# =============================================================================
# Tokenization
# =============================================================================

def tokenize(sentence: str) -> List[str]:
    """
    Tokenize a sentence into words.
    
    Simple whitespace + punctuation tokenization.
    """
    # Remove leading/trailing whitespace
    sentence = sentence.strip()
    
    # Split on whitespace and common punctuation
    # Keep contractions together
    tokens = re.findall(r"\b[\w']+\b", sentence)
    
    return tokens


def get_ticker_code(token: str) -> int:
    """
    Assign a ticker code to a token based on its grammatical category.
    
    Returns code 1-5.
    """
    lower = token.lower()
    
    # Code 1: Articles, determiners
    if lower in ARTICLES:
        return 1
    
    # Code 2: Prepositions, conjunctions
    if lower in PREPOSITIONS or lower in CONJUNCTIONS:
        return 2
    
    # Code 3: Pronouns
    if lower in PRONOUNS:
        return 3
    
    # Code 4: Common verbs (and words ending in common verb suffixes)
    if lower in COMMON_VERBS:
        return 4
    if lower.endswith(('ing', 'ed', 'ly')):
        return 4
    
    # Code 5: Proper nouns (capitalized, not at sentence start)
    # For simplicity, treat unknown words as common nouns (3) or verbs (4)
    
    # Default: common noun or verb based on ending
    if lower.endswith(('tion', 'ness', 'ment', 'ity', 'er', 'or', 'ist')):
        return 3  # Likely noun
    
    return 4  # Default to verb/adjective/adverb


# =============================================================================
# Event Detection
# =============================================================================

def detect_zero_events(sentence: str) -> List[Dict[str, Any]]:
    """Detect zero events (pauses, omissions) in sentence."""
    events = []
    for i, pattern in enumerate(ZERO_PATTERNS):
        for match in re.finditer(pattern, sentence):
            events.append({
                "type": "zero",
                "pattern": pattern,
                "position": match.start(),
                "text": match.group(),
            })
    return events


def detect_operator_events(sentence: str) -> List[Dict[str, Any]]:
    """Detect operator events (connective symbols) in sentence."""
    events = []
    for pattern in OPERATOR_PATTERNS:
        for match in re.finditer(pattern, sentence):
            events.append({
                "type": "operator",
                "pattern": pattern,
                "position": match.start(),
                "text": match.group(),
            })
    return events


def detect_scope_events(sentence: str) -> List[Dict[str, Any]]:
    """Detect scope events (nesting/bracketing) in sentence."""
    events = []
    for pattern in SCOPE_PATTERNS:
        for match in re.finditer(pattern, sentence):
            # Skip very short quoted strings (likely apostrophes)
            if match.group().startswith("'") and len(match.group()) <= 3:
                continue
            events.append({
                "type": "scope",
                "pattern": pattern,
                "position": match.start(),
                "text": match.group(),
            })
    return events


def detect_high_intent_events(sentence: str) -> List[Dict[str, Any]]:
    """
    Detect High-Intent events (modal/epistemic markers) in sentence.
    
    Returns a list of events with:
    - type: "high_intent"
    - category: The lexicon category (e.g., "CERTAINTY", "POSSIBILITY")
    - word: The matched word or phrase
    - position: Character position in sentence
    - semantic_force: HIGH, MEDIUM, or LOW
    """
    category_words, multi_word_exprs = get_high_intent_word_sets()
    lexicon = load_high_intent_lexicon()
    
    events = []
    sentence_lower = sentence.lower()
    
    # Track positions already matched (to avoid double-counting)
    matched_positions: Set[int] = set()
    
    # First, check multi-word expressions (longer matches first)
    for expr in multi_word_exprs:
        expr_lower = expr.lower()
        # Use word boundary matching
        pattern = r'\b' + re.escape(expr_lower) + r'\b'
        for match in re.finditer(pattern, sentence_lower):
            pos = match.start()
            # Check if this position is already matched
            if any(pos <= p < pos + len(expr) for p in matched_positions):
                continue
            
            # Find which category this expression belongs to
            for cat_name, words in category_words.items():
                if expr_lower in words:
                    cat_data = lexicon.get("categories", {}).get(cat_name, {})
                    events.append({
                        "type": "high_intent",
                        "category": cat_name,
                        "word": expr,
                        "position": pos,
                        "semantic_force": cat_data.get("semantic_force", "MEDIUM"),
                        "interpretant_effect": cat_data.get("interpretant_effect", ""),
                    })
                    # Mark these positions as matched
                    for i in range(pos, pos + len(expr)):
                        matched_positions.add(i)
                    break
    
    # Then, check single words
    tokens = tokenize(sentence)
    # Find token positions in original sentence
    token_positions = []
    search_start = 0
    for token in tokens:
        # Find this token in the sentence
        idx = sentence_lower.find(token.lower(), search_start)
        if idx != -1:
            token_positions.append((token, idx))
            search_start = idx + len(token)
        else:
            token_positions.append((token, -1))
    
    for token, pos in token_positions:
        if pos == -1:
            continue
        # Skip if this position is already matched by a multi-word expression
        if pos in matched_positions:
            continue
        
        token_lower = token.lower()
        
        # Check each category
        for cat_name, words in category_words.items():
            if token_lower in words:
                cat_data = lexicon.get("categories", {}).get(cat_name, {})
                events.append({
                    "type": "high_intent",
                    "category": cat_name,
                    "word": token,
                    "position": pos,
                    "semantic_force": cat_data.get("semantic_force", "MEDIUM"),
                    "interpretant_effect": cat_data.get("interpretant_effect", ""),
                })
                matched_positions.add(pos)
                break  # Each word belongs to one category
    
    # Sort by position
    events.sort(key=lambda e: e["position"])
    
    return events


# =============================================================================
# Sentence Parsing
# =============================================================================

def detect_emdash_events(sentence: str) -> List[Dict[str, Any]]:
    """
    Detect em-dash boundary events in sentence.
    Em-dashes (—) create a different kind of boundary than parentheses.
    They're more interruptive, more dramatic, and function differently semantically.
    
    Returns list of events with type, position, and matched text.
    """
    events = []
    
    # Em-dash patterns: — or -- (double hyphen as em-dash substitute)
    emdash_pattern = r'—|--'
    
    for match in re.finditer(emdash_pattern, sentence):
        events.append({
            "type": "emdash",
            "position": match.start(),
            "matched": match.group(),
        })
    
    return events


def parse_sentence(sentence: str, narrator_id: str = "Narrator_A") -> Dict[str, Any]:
    """
    Parse a sentence into LNCP canonical format with High-Intent detection.
    
    Args:
        sentence: Raw sentence text
        narrator_id: Narrator identifier (default: "Narrator_A")
        
    Returns:
        LNCP canonical row dictionary with high_intent_events
    """
    # Tokenize
    tokens = tokenize(sentence)
    
    # Assign ticker codes
    ticker_expanded = [get_ticker_code(t) for t in tokens]
    ticker_numeric = [str(code) for code in ticker_expanded]
    
    # Generate base signature
    base_signature = "|".join(ticker_numeric)
    
    # Detect structural events
    zero_events = detect_zero_events(sentence)
    operator_events = detect_operator_events(sentence)
    scope_events = detect_scope_events(sentence)
    emdash_events = detect_emdash_events(sentence)
    
    # Detect High-Intent events (web-app layer feature)
    high_intent_events = detect_high_intent_events(sentence)
    
    return {
        "sentence": sentence,
        "narrator_id": narrator_id,
        "tokens": tokens,
        "ticker_numeric": ticker_numeric,
        "ticker_expanded": ticker_expanded,
        "base_signature": base_signature,
        "zero_events": zero_events,
        "operator_events": operator_events,
        "scope_events": scope_events,
        "emdash_events": emdash_events,
        "high_intent_events": high_intent_events,
    }


def parse_sentences(sentences: List[str], narrator_id: str = "Narrator_A") -> List[Dict[str, Any]]:
    """
    Parse multiple sentences into LNCP canonical format.
    
    Args:
        sentences: List of raw sentence texts
        narrator_id: Narrator identifier
        
    Returns:
        List of LNCP canonical row dictionaries
    """
    return [parse_sentence(s, narrator_id) for s in sentences]


# =============================================================================
# v0.6.0: Rhetorical Mode Detection
# =============================================================================

# Informal register markers
INFORMAL_MARKERS = {
    'yeah', 'yep', 'nope', 'gonna', 'wanna', 'kinda', 'sorta', 'dunno', 
    'hey', 'wow', 'ugh', 'huh', 'okay', 'ok', 'lol', 'omg', 'btw', 'tbh',
    'ngl', 'idk', 'imo', 'fwiw', 'bruh', 'dude', 'bro', 'man', 'like',
    'basically', 'literally', 'actually', 'seriously', 'honestly', 'whatever',
    'anyways', 'welp', 'yikes', 'oops', 'whoops', 'psych', 'cool', 'chill',
    # v0.6.1: Additional informal markers
    'gotta', 'lemme', 'gimme', 'cause', 'cuz', 'tho', 'ya', 'yup', 'nah',
    'totally', 'super', 'kinda', 'sorta', 'prolly', 'def', 'obvi', 'whatevs',
    'legit', 'lowkey', 'highkey', 'fr', 'rn', 'af', 'smh', 'fam', 'yo'
}

# Discourse markers (sentence starters that signal casual speech)
DISCOURSE_MARKERS = {
    'so', 'well', 'anyway', 'anyways', 'look', 'see', 'right', 'okay', 'ok',
    'now', 'hey', 'listen', 'thing', 'basically', 'honestly', 'actually',
    'apparently', 'clearly', 'obviously', 'seriously', 'literally', 'personally'
}

# Casual phrases (multi-word)
CASUAL_PHRASES = [
    'i mean', 'you know', 'i guess', 'i dunno', "don't know", 'no idea',
    'kind of', 'sort of', 'or something', 'or whatever', 'and stuff',
    'you see', 'the thing is', 'here\'s the thing', 'long story short',
    'at the end of the day', 'to be honest', 'to be fair', 'not gonna lie'
]

# Contraction patterns
CONTRACTION_PATTERNS = ["n't", "'s", "'re", "'ve", "'ll", "'d", "'m"]

# Subordinating conjunctions for clause detection
SUBORDINATORS = {
    'although', 'because', 'since', 'while', 'when', 'whenever', 'where',
    'wherever', 'if', 'unless', 'until', 'though', 'whereas', 'whether',
    'after', 'before', 'as', 'that', 'which', 'who', 'whom', 'whose',
    'having', 'given', 'provided', 'once', 'than'
}

# Imperative verb indicators (common imperative starts)
IMPERATIVE_VERBS = {
    'accept', 'act', 'add', 'allow', 'ask', 'avoid', 'be', 'begin', 'build',
    'call', 'check', 'choose', 'come', 'consider', 'continue', 'create',
    'cut', 'decide', 'develop', 'do', 'eliminate', 'embrace', 'enforce',
    'ensure', 'expect', 'face', 'find', 'focus', 'follow', 'forget', 'get',
    'give', 'go', 'guard', 'handle', 'hold', 'ignore', 'invest', 'keep',
    'know', 'learn', 'let', 'listen', 'look', 'make', 'meet', 'move', 'note',
    'notice', 'pay', 'plan', 'play', 'practice', 'prepare', 'prioritize',
    'protect', 'put', 'question', 'read', 'recognize', 'remember', 'remove',
    'request', 'resist', 'rest', 'run', 'say', 'see', 'seek', 'set', 'ship',
    'show', 'simplify', 'sit', 'sleep', 'speak', 'spend', 'stand', 'start',
    'stay', 'stop', 'study', 'take', 'talk', 'tell', 'think', 'treat', 'trust',
    'try', 'turn', 'understand', 'use', 'verify', 'wait', 'walk', 'watch',
    'welcome', 'work', 'write'
}


def detect_question_ratio(sentences: List[str]) -> float:
    """Calculate ratio of sentences that are questions."""
    if not sentences:
        return 0.0
    question_count = sum(1 for s in sentences if '?' in s)
    return question_count / len(sentences)


def detect_imperatives(sentences: List[str]) -> Tuple[int, List[str]]:
    """
    Detect imperative sentences (commands).
    Returns count and list of detected imperative verbs.
    """
    imperative_count = 0
    detected_verbs = []
    
    for sentence in sentences:
        words = sentence.lower().split()
        if not words:
            continue
        
        first_word = words[0].rstrip('.,!?;:')
        
        # Check if sentence starts with an imperative verb
        if first_word in IMPERATIVE_VERBS:
            imperative_count += 1
            detected_verbs.append(first_word)
        # Also check for "Don't/Do" + verb pattern
        elif first_word in ("don't", "do", "don't") and len(words) > 1:
            second_word = words[1].rstrip('.,!?;:')
            if second_word in IMPERATIVE_VERBS:
                imperative_count += 1
                detected_verbs.append(second_word)
    
    return imperative_count, detected_verbs


def detect_register(sentences: List[str]) -> Tuple[str, float]:
    """
    Detect formality register of text.
    v0.6.1: Improved with discourse markers, casual phrases, punctuation patterns
    Returns (register, informality_score)
    """
    if not sentences:
        return "FORMAL", 0.0
    
    text_lower = ' '.join(sentences).lower()
    text_original = ' '.join(sentences)
    words = text_lower.split()
    
    # Count informal word markers
    informal_count = sum(1 for word in words if word.rstrip('.,!?;:') in INFORMAL_MARKERS)
    
    # Count contractions
    contraction_count = sum(1 for pattern in CONTRACTION_PATTERNS if pattern in text_lower)
    
    # Count fragments (very short sentences ≤ 4 words) - increased threshold
    fragment_count = sum(1 for s in sentences if len(s.split()) <= 4)
    
    # Count exclamations and interjections
    exclamation_count = sum(1 for s in sentences if '!' in s)
    
    # v0.6.1: Count discourse markers at sentence starts
    discourse_count = 0
    for s in sentences:
        first_word = s.split()[0].lower().rstrip('.,!?;:') if s.split() else ''
        if first_word in DISCOURSE_MARKERS:
            discourse_count += 1
    
    # v0.6.1: Count casual phrases
    casual_phrase_count = sum(1 for phrase in CASUAL_PHRASES if phrase in text_lower)
    
    # v0.6.1: Count ellipses
    ellipsis_count = text_original.count('...') + text_original.count('…')
    
    # v0.6.1: Count casual punctuation patterns
    casual_punct = text_original.count('?!') + text_original.count('!!') + text_original.count('??')
    
    # v0.6.1: Sentence-initial conjunctions (casual style)
    initial_conjunction_count = sum(1 for s in sentences 
                                    if s.split() and s.split()[0].lower() in ('and', 'but', 'so', 'or'))
    
    # Compute informality score with weighted signals
    total_signals = (
        informal_count * 1.0 +
        contraction_count * 0.5 +
        fragment_count * 1.0 +
        exclamation_count * 0.5 +
        discourse_count * 0.75 +
        casual_phrase_count * 1.0 +
        ellipsis_count * 0.5 +
        casual_punct * 0.5 +
        initial_conjunction_count * 0.5
    )
    
    informality_score = total_signals / len(sentences) if sentences else 0.0
    
    # Threshold for informal - lowered from 1.0 to 0.75 for better sensitivity
    register = "INFORMAL" if informality_score >= 0.75 else "FORMAL"
    
    return register, round(informality_score, 3)


def detect_anaphora(sentences: List[str]) -> Tuple[bool, Optional[str], float]:
    """
    Detect anaphora (repetitive sentence starts).
    Returns (has_anaphora, repeated_word, repetition_ratio)
    """
    if len(sentences) < 2:
        return False, None, 0.0
    
    # Get first words of each sentence
    starts = []
    for s in sentences:
        words = s.split()
        if words:
            starts.append(words[0].lower().rstrip('.,!?;:'))
    
    if not starts:
        return False, None, 0.0
    
    # Find most common start
    counter = Counter(starts)
    most_common_word, most_common_count = counter.most_common(1)[0]
    
    repetition_ratio = most_common_count / len(sentences)
    
    # Consider anaphora if >= 50% of sentences start the same way
    has_anaphora = repetition_ratio >= 0.5 and most_common_count >= 2
    
    return has_anaphora, most_common_word if has_anaphora else None, round(repetition_ratio, 3)


def estimate_clause_count(sentence: str) -> int:
    """
    Estimate number of clauses in a sentence.
    v0.6.1: Improved with participial phrases and better heuristics
    """
    words = sentence.lower().split()
    
    # Start with 1 (main clause)
    clause_count = 1
    
    # Count subordinating conjunctions
    for word in words:
        clean_word = word.rstrip('.,!?;:')
        if clean_word in SUBORDINATORS:
            clause_count += 1
    
    # v0.6.1: Count participial phrases (-ing, -ed at potential clause boundaries)
    # Look for patterns like ", having", ", walking", "—running"
    participial_patterns = 0
    for i, word in enumerate(words):
        if i > 0:
            prev_char = sentence[sentence.lower().find(word) - 1] if sentence.lower().find(word) > 0 else ''
            if prev_char in ',—-' and (word.endswith('ing') or word.endswith('ed')):
                participial_patterns += 1
    clause_count += participial_patterns
    
    # v0.6.1: Count comma-separated elements more aggressively
    comma_count = sentence.count(',')
    # Each 2 commas likely indicates an additional clause or list
    clause_count += comma_count // 2
    
    # v0.6.1: Semicolons definitely indicate clause boundaries
    semicolon_count = sentence.count(';')
    clause_count += semicolon_count
    
    return clause_count


def compute_syntax_complexity(sentences: List[str]) -> Tuple[str, float, float]:
    """
    Compute syntax complexity metrics.
    v0.6.1: Improved thresholds and added sentence length variance
    Returns (complexity_level, avg_clauses, avg_words)
    """
    if not sentences:
        return "SIMPLE", 0.0, 0.0
    
    clause_counts = [estimate_clause_count(s) for s in sentences]
    total_clauses = sum(clause_counts)
    avg_clauses = total_clauses / len(sentences)
    max_clauses = max(clause_counts) if clause_counts else 0
    
    word_counts = [len(s.split()) for s in sentences]
    total_words = sum(word_counts)
    avg_words = total_words / len(sentences)
    max_words = max(word_counts) if word_counts else 0
    
    # v0.6.1: COMPLEX detection - multiple pathways
    # 1. High average clauses (multi-clause throughout)
    # 2. High average words (long sentences throughout)
    # 3. ANY very long sentence (even one complex sentence counts)
    # 4. ANY high-clause sentence (even one subordinated mess counts)
    is_complex = (
        avg_clauses >= 2.5 or 
        avg_words >= 25 or 
        max_words >= 28 or      # Lowered from 35 - sentences with 28+ words are complex
        max_clauses >= 4 or     # Any sentence with 4+ clauses is complex
        (avg_words >= 15 and avg_clauses >= 2.0)  # Lowered: moderate on both = complex
    )
    
    is_moderate = (
        avg_clauses >= 1.5 or 
        avg_words >= 12 or
        max_words >= 25
    )
    
    if is_complex:
        complexity = "COMPLEX"
    elif is_moderate:
        complexity = "MODERATE"
    else:
        complexity = "SIMPLE"
    
    return complexity, round(avg_clauses, 2), round(avg_words, 2)


def detect_emdash_pairs(sentence: str) -> int:
    """
    Detect paired em-dashes functioning as parentheticals.
    e.g., "The meeting—which nobody wanted—ran long"
    """
    # Count em-dashes and double-hyphens
    emdash_count = sentence.count('—') + sentence.count('--')
    # Return number of pairs
    return emdash_count // 2


def compute_rhetorical_profile(sentences: List[str], rows: List[Dict[str, Any]], 
                                hi_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    v0.6.0: Compute rhetorical mode profile.
    
    This supplements the epistemic stance with structural/rhetorical analysis.
    """
    if not sentences:
        return {
            "is_assertive_mode": False,
            "is_interrogative_mode": False,
            "register": "FORMAL",
            "informality_score": 0.0,
            "has_anaphora": False,
            "anaphora_word": None,
            "repetition_ratio": 0.0,
            "syntax_complexity": "SIMPLE",
            "avg_clauses": 0.0,
            "avg_words": 0.0,
            "question_ratio": 0.0,
            "imperative_count": 0,
            "emdash_pair_count": 0,
            # v0.6.1: Structural density
            "is_structurally_dense": False,
            "structural_density_score": 0.0,
        }
    
    sentence_count = len(sentences)
    
    # Question detection
    question_ratio = detect_question_ratio(sentences)
    is_interrogative = question_ratio >= 0.5
    
    # Imperative detection
    imperative_count, imperative_verbs = detect_imperatives(sentences)
    
    # Register detection
    register, informality_score = detect_register(sentences)
    
    # Anaphora detection
    has_anaphora, anaphora_word, repetition_ratio = detect_anaphora(sentences)
    
    # Syntax complexity
    complexity, avg_clauses, avg_words = compute_syntax_complexity(sentences)
    
    # Em-dash pairs
    emdash_pair_count = sum(detect_emdash_pairs(s) for s in sentences)
    
    # v0.6.1: Structural density detection
    # Dense = lots of parentheticals, em-dashes, nested clauses, OR high marker density
    total_scope = sum(len(row.get("scope_events", [])) for row in rows)
    total_emdash = sum(len(row.get("emdash_events", [])) for row in rows)
    total_markers = hi_profile.get("total_high_intent_events", 0)
    
    # Compute structural density score
    # Weight: parentheticals (1.0), em-dashes (0.75), high clause count (0.5)
    structural_density_score = (
        (total_scope / sentence_count) * 1.0 +
        (total_emdash / sentence_count) * 0.75 +
        (avg_clauses - 1) * 0.5 +  # Subtract 1 since every sentence has at least 1 clause
        (emdash_pair_count / sentence_count) * 0.5
    )
    
    # v0.6.1: Also compute epistemic density (high marker count = dense argumentation)
    epistemic_density_score = total_markers / sentence_count if sentence_count > 0 else 0
    
    # Combined density: structural OR epistemic
    combined_density_score = structural_density_score + (epistemic_density_score * 0.3)
    
    # Structurally dense if:
    # 1. High structural density (parentheticals, em-dashes, clauses)
    # 2. OR high parenthetical count alone
    # 3. OR high combined density (structure + markers)
    # 4. OR very high marker density alone (dense argumentation)
    # 5. OR moderate structural + any markers (combination effect)
    is_structurally_dense = (
        structural_density_score >= 1.5 or 
        total_scope >= sentence_count * 1.5 or
        combined_density_score >= 1.2 or  # Lowered from 1.3
        epistemic_density_score >= 1.5 or  # 1.5+ markers per sentence = dense
        (structural_density_score >= 0.7 and epistemic_density_score >= 0.8)  # Combined moderate
    )
    
    # Assertive mode detection
    # Assertive = short sentences + few markers + imperatives OR confident brevity
    total_markers = hi_profile.get("total_high_intent_events", 0)
    is_assertive = (
        avg_words < 12 and
        total_markers < 2 and
        question_ratio < 0.2 and
        sentence_count >= 2 and
        (imperative_count >= 1 or avg_clauses < 1.5)
    )
    
    return {
        "is_assertive_mode": is_assertive,
        "is_interrogative_mode": is_interrogative,
        "register": register,
        "informality_score": informality_score,
        "has_anaphora": has_anaphora,
        "anaphora_word": anaphora_word,
        "repetition_ratio": repetition_ratio,
        "syntax_complexity": complexity,
        "avg_clauses": avg_clauses,
        "avg_words": avg_words,
        "question_ratio": round(question_ratio, 3),
        "imperative_count": imperative_count,
        "emdash_pair_count": emdash_pair_count,
        # v0.6.1: Structural density
        "is_structurally_dense": is_structurally_dense,
        "structural_density_score": round(structural_density_score, 3),
    }


# =============================================================================
# High-Intent Aggregation
# =============================================================================

def compute_high_intent_profile(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute aggregate High-Intent profile from parsed rows.
    
    v0.5.0: Added CONTRADICTORY stance, em-dash tracking, poetic mode detection
    
    Returns metrics about modal/epistemic marker usage across the sample.
    """
    total_events = 0
    category_counts: Dict[str, int] = {}
    force_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    all_words: List[str] = []
    sentences_with_high_intent = 0
    
    # v0.5.0: Track em-dash and operator events for poetic mode detection
    total_emdash_events = 0
    total_operator_events = 0
    total_scope_events = 0
    
    for row in rows:
        events = row.get("high_intent_events", [])
        if events:
            sentences_with_high_intent += 1
        
        for event in events:
            total_events += 1
            
            cat = event.get("category", "UNKNOWN")
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
            force = event.get("semantic_force", "MEDIUM")
            force_counts[force] = force_counts.get(force, 0) + 1
            
            all_words.append(event.get("word", ""))
        
        # Track structural events
        total_emdash_events += len(row.get("emdash_events", []))
        total_operator_events += len(row.get("operator_events", []))
        total_scope_events += len(row.get("scope_events", []))
    
    sentence_count = len(rows)
    
    # Compute derived metrics
    high_intent_rate = total_events / sentence_count if sentence_count > 0 else 0.0
    coverage_rate = sentences_with_high_intent / sentence_count if sentence_count > 0 else 0.0
    
    # Dominant category
    dominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
    
    # Epistemic openness: ratio of POSSIBILITY+HEDGING to CERTAINTY+EMPHASIS
    opening_count = category_counts.get("POSSIBILITY", 0) + category_counts.get("HEDGING", 0) + category_counts.get("CONDITIONALITY", 0)
    closing_count = category_counts.get("CERTAINTY", 0) + category_counts.get("EMPHASIS", 0)
    
    if closing_count > 0:
        epistemic_openness = opening_count / (opening_count + closing_count)
    elif opening_count > 0:
        epistemic_openness = 1.0
    else:
        epistemic_openness = 0.5  # Neutral when no markers
    
    # Stance intensity: ratio of HIGH force to total
    stance_intensity = force_counts["HIGH"] / total_events if total_events > 0 else 0.0
    
    # v0.5.0: Determine epistemic stance with CONTRADICTORY detection
    epistemic_stance = _compute_epistemic_stance(opening_count, closing_count, total_events)
    
    # v0.5.0: Detect poetic mode
    # Poetic writing often has: operators > scope, em-dashes, low marker count
    avg_words = sum(len(row.get("tokens", [])) for row in rows) / sentence_count if sentence_count > 0 else 0
    is_poetic_mode = (
        total_operator_events > total_scope_events and 
        total_events < sentence_count and  # Low marker density
        avg_words < 25  # Shorter sentences typical of poetic writing
    )
    
    # v0.5.0: Minimal marker flag for improved feedback
    is_minimal = total_events < 2
    
    return {
        "total_high_intent_events": total_events,
        "sentences_with_high_intent": sentences_with_high_intent,
        "high_intent_rate": round(high_intent_rate, 3),
        "coverage_rate": round(coverage_rate, 3),
        "category_distribution": category_counts,
        "force_distribution": force_counts,
        "dominant_category": dominant_category,
        "epistemic_openness": round(epistemic_openness, 3),
        "stance_intensity": round(stance_intensity, 3),
        "unique_markers": list(set(all_words)),
        "marker_count": len(all_words),
        # v0.5.0: New fields
        "epistemic_stance": epistemic_stance,
        "opening_marker_count": opening_count,
        "closing_marker_count": closing_count,
        "is_contradictory": epistemic_stance == "CONTRADICTORY",
        "is_minimal": is_minimal,
        "is_poetic_mode": is_poetic_mode,
        "emdash_count": total_emdash_events,
        "structural_summary": {
            "emdash_events": total_emdash_events,
            "operator_events": total_operator_events,
            "scope_events": total_scope_events,
        }
    }


def _compute_epistemic_stance(opening_count: int, closing_count: int, total_events: int) -> str:
    """
    Compute epistemic stance category.
    
    v0.5.0: Added CONTRADICTORY stance when both opening AND closing markers present.
    
    Returns one of: OPEN, CLOSED, CONTRADICTORY, BALANCED, MINIMAL
    """
    # MINIMAL: Few or no markers
    if total_events < 2:
        return "MINIMAL"
    
    # CONTRADICTORY: Significant presence of BOTH opening AND closing markers
    # This suggests mixed signals, not balanced writing
    if opening_count >= 2 and closing_count >= 2:
        return "CONTRADICTORY"
    
    # OPEN: Predominantly opening markers
    if opening_count > closing_count and opening_count >= 2:
        return "OPEN"
    
    # CLOSED: Predominantly closing markers
    if closing_count > opening_count and closing_count >= 2:
        return "CLOSED"
    
    # BALANCED: Some of each, but not enough to be contradictory
    if opening_count > 0 and closing_count > 0:
        return "BALANCED"
    
    # Default to MINIMAL if we get here
    return "MINIMAL"


# =============================================================================
# Main Entry Point
# =============================================================================

def sentences_to_lncp_rows(sentences: List[str]) -> List[Dict[str, Any]]:
    """
    Convert raw sentences to LNCP canonical rows.
    
    This is the main entry point for the web app.
    """
    return parse_sentences(sentences)


def sentences_to_lncp_rows_with_profile(sentences: List[str]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convert raw sentences to LNCP canonical rows and compute full profile.
    
    v0.6.0: Now includes rhetorical profile (assertive, interrogative, register, etc.)
    
    Returns:
        (rows, combined_profile)
    """
    rows = parse_sentences(sentences)
    hi_profile = compute_high_intent_profile(rows)
    
    # v0.6.0: Compute rhetorical profile and merge
    rhetorical = compute_rhetorical_profile(sentences, rows, hi_profile)
    
    # Merge profiles
    combined_profile = {**hi_profile, **rhetorical}
    
    return rows, combined_profile


def compute_full_profile(sentences: List[str], rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    v0.6.0: Compute complete analysis profile including epistemic and rhetorical features.
    
    Args:
        sentences: Original sentence strings
        rows: Parsed LNCP rows
        
    Returns:
        Combined profile with all v0.5.0 and v0.6.0 fields
    """
    hi_profile = compute_high_intent_profile(rows)
    rhetorical = compute_rhetorical_profile(sentences, rows, hi_profile)
    return {**hi_profile, **rhetorical}


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    demo_sentences = [
        "The morning light came through the window.",
        "She definitely made coffee and sat down.",
        "Nothing happened for a long time.",
        "The book (a worn paperback) probably sat on the table.",
        "He said \"hello\" and waited...",
        "I believe this might be important.",
        "Perhaps we should consider other options.",
        "It certainly seems like the right choice.",
    ]
    
    print("LNCP Sentence Parser Demo (v0.6.0 with Rhetorical Modes)")
    print("=" * 60)
    
    rows = []
    for sentence in demo_sentences:
        row = parse_sentence(sentence)
        rows.append(row)
        print(f"\nSentence: {sentence}")
        print(f"  Tokens: {row['tokens']}")
        print(f"  Signature: {row['base_signature']}")
        print(f"  Zero events: {len(row['zero_events'])}")
        print(f"  Operator events: {len(row['operator_events'])}")
        print(f"  Scope events: {len(row['scope_events'])}")
        print(f"  High-Intent events: {len(row['high_intent_events'])}")
        for hi in row['high_intent_events']:
            print(f"    - {hi['word']} ({hi['category']}, {hi['semantic_force']})")
    
    print("\n" + "=" * 60)
    print("Combined Profile (v0.6.0)")
    print("=" * 60)
    
    profile = compute_full_profile(demo_sentences, rows)
    
    print("\n--- Epistemic Profile ---")
    print(f"  Total markers: {profile['total_high_intent_events']}")
    print(f"  Coverage rate: {profile['coverage_rate']:.1%}")
    print(f"  Epistemic stance: {profile['epistemic_stance']}")
    print(f"  Epistemic openness: {profile['epistemic_openness']:.2f}")
    print(f"  Is contradictory: {profile['is_contradictory']}")
    print(f"  Is minimal: {profile['is_minimal']}")
    print(f"  Is poetic mode: {profile['is_poetic_mode']}")
    
    print("\n--- Rhetorical Profile (v0.6.0) ---")
    print(f"  Is assertive mode: {profile['is_assertive_mode']}")
    print(f"  Is interrogative mode: {profile['is_interrogative_mode']}")
    print(f"  Register: {profile['register']}")
    print(f"  Informality score: {profile['informality_score']}")
    print(f"  Has anaphora: {profile['has_anaphora']}")
    print(f"  Syntax complexity: {profile['syntax_complexity']}")
    print(f"  Avg clauses: {profile['avg_clauses']}")
    print(f"  Question ratio: {profile['question_ratio']}")
    print(f"  Imperative count: {profile['imperative_count']}")
