/**
 * ═══════════════════════════════════════════════════════════════════════════
 * LNCP PROFILE CLASSIFIER v3.8 "Quinquaginta" - Extension Bundle
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Self-contained classifier for browser extension.
 * Runs entirely client-side - no API required for basic analysis.
 * 
 * This is a minified version of the full classifier optimized for extension use.
 */

// ═══════════════════════════════════════════════════════════════════
// TICKER ENCODING
// ═══════════════════════════════════════════════════════════════════

const TICKER_MAP = {
  // 1: First-person anchors
  'i': '1', 'me': '1', 'my': '1', 'mine': '1', 'myself': '1',
  'we': '1', 'us': '1', 'our': '1', 'ours': '1', 'ourselves': '1',
  
  // 2: Relational/connective
  'to': '2', 'of': '2', 'with': '2', 'for': '2', 'by': '2', 'from': '2',
  'in': '2', 'on': '2', 'at': '2', 'as': '2', 'into': '2',
  
  // 3: Determiners/articles
  'the': '3', 'a': '3', 'an': '3', 'this': '3', 'that': '3',
  'these': '3', 'those': '3', 'which': '3', 'what': '3',
  
  // 4: Common verbs/nouns
  'be': '4', 'is': '4', 'am': '4', 'are': '4', 'was': '4', 'were': '4',
  'have': '4', 'has': '4', 'had': '4', 'do': '4', 'does': '4', 'did': '4',
  'go': '4', 'went': '4', 'come': '4', 'came': '4', 'get': '4', 'got': '4',
  'home': '4', 'time': '4', 'way': '4', 'day': '4', 'year': '4',
  
  // 5: Modifiers/adverbs
  'now': '5', 'then': '5', 'here': '5', 'there': '5', 'when': '5',
  'where': '5', 'how': '5', 'why': '5', 'very': '5', 'just': '5',
  'still': '5', 'even': '5', 'only': '5', 'also': '5',
  
  // 6: Action verbs
  'say': '6', 'said': '6', 'tell': '6', 'told': '6', 'ask': '6', 'asked': '6',
  'make': '6', 'made': '6', 'take': '6', 'took': '6', 'give': '6', 'gave': '6',
  'see': '6', 'saw': '6', 'know': '6', 'knew': '6', 'think': '6', 'thought': '6',
  
  // 7: Abstract/state
  'perhaps': '7', 'maybe': '7', 'might': '7', 'could': '7', 'would': '7',
  'should': '7', 'seem': '7', 'seems': '7', 'appear': '7',
  
  // 8: Extended/complex
  'together': '8', 'remember': '8', 'beautiful': '8', 'important': '8',
  'different': '8', 'possible': '8', 'actually': '8', 'especially': '8',
  
  // 9: Nominalization/formal
  'information': '9', 'situation': '9', 'relationship': '9', 'experience': '9',
  'understanding': '9', 'development': '9', 'environment': '9', 'government': '9'
};

// Ticker assignment based on word structure
function assignTicker(word) {
  const lower = word.toLowerCase().replace(/[^a-z'-]/g, '');
  if (!lower) return null;
  
  // Check direct map
  if (TICKER_MAP[lower]) return TICKER_MAP[lower];
  
  const len = lower.length;
  
  // Suffix-based rules
  if (lower.endsWith('tion') || lower.endsWith('sion') || lower.endsWith('ment') || lower.endsWith('ness')) return '9';
  if (lower.endsWith('ing') && len > 5) return '4-7';
  if (lower.endsWith('ly') && len > 4) return '4-6';
  if (lower.endsWith('ful') || lower.endsWith('less')) return '7-8';
  if (lower.endsWith('able') || lower.endsWith('ible')) return '7-8';
  
  // Length-based fallback
  if (len <= 2) return '2';
  if (len <= 3) return '3';
  if (len <= 4) return '4';
  if (len <= 5) return '5';
  if (len <= 6) return '6';
  if (len <= 7) return '7';
  if (len <= 9) return '8';
  return '9';
}

// ═══════════════════════════════════════════════════════════════════
// SENTENCE ENCODING
// ═══════════════════════════════════════════════════════════════════

function encodeSentence(sentence, maxTokens = 50) {
  const words = sentence.trim().split(/\s+/).slice(0, maxTokens);
  const tickers = [];
  
  for (const word of words) {
    const ticker = assignTicker(word);
    if (ticker) tickers.push(ticker);
  }
  
  return {
    original: sentence,
    wordCount: words.length,
    tickers,
    tickerString: tickers.join('-'),
    // Compute signature (first 10 tickers as pattern)
    signature: tickers.slice(0, 10).join('-')
  };
}

// ═══════════════════════════════════════════════════════════════════
// TOOL DETECTION
// ═══════════════════════════════════════════════════════════════════

function computeDigitalRoot(n) {
  while (n >= 10) {
    n = String(n).split('').reduce((a, b) => a + parseInt(b), 0);
  }
  return n;
}

function detectTools(tickers) {
  const tools = { T1: false, T2: false, T3: false, T4: false, T5: false, T6: false };
  
  // Convert compound tickers to primary values
  const values = tickers.map(t => {
    const parts = t.split('-').map(Number);
    return parts[0] || 5; // Default to 5 if invalid
  });
  
  if (values.length < 2) return tools;
  
  // T1: Adjacent even-odd binding (4-5, 6-7, 8-9)
  for (let i = 0; i < values.length - 1; i++) {
    const a = values[i], b = values[i + 1];
    if ((a % 2 === 0 && b % 2 === 1 && b === a + 1) ||
        (a % 2 === 1 && b % 2 === 0 && a === b + 1)) {
      tools.T1 = true;
      break;
    }
  }
  
  // T2: Oscillation (e.g., 3-5-3 or 4-6-4)
  for (let i = 0; i < values.length - 2; i++) {
    if (values[i] === values[i + 2] && values[i] !== values[i + 1]) {
      tools.T2 = true;
      break;
    }
  }
  
  // T3: Harmonic (digital root patterns)
  const roots = values.slice(0, 5).map(computeDigitalRoot);
  const uniqueRoots = new Set(roots);
  if (uniqueRoots.size <= 2 && values.length >= 4) {
    tools.T3 = true;
  }
  
  // T4: Mirror/symmetry
  if (values.length >= 4) {
    const first2 = values.slice(0, 2).join('-');
    const last2 = values.slice(-2).reverse().join('-');
    if (first2 === last2) tools.T4 = true;
  }
  
  // T5: Extended run (3+ of same parity)
  let evenRun = 0, oddRun = 0;
  for (const v of values) {
    if (v % 2 === 0) { evenRun++; oddRun = 0; }
    else { oddRun++; evenRun = 0; }
    if (evenRun >= 3 || oddRun >= 3) { tools.T5 = true; break; }
  }
  
  // T6: Sustained high values (3+ values >= 7)
  let highRun = 0;
  for (const v of values) {
    if (v >= 7) highRun++;
    else highRun = 0;
    if (highRun >= 3) { tools.T6 = true; break; }
  }
  
  return tools;
}

// ═══════════════════════════════════════════════════════════════════
// PROFILE DERIVATION
// ═══════════════════════════════════════════════════════════════════

const PROFILE_META = {
  'ASSERTIVE-OPEN': { title: 'The Bold Explorer', icon: '🚀', tagline: 'Confident voice that invites dialogue' },
  'ASSERTIVE-CLOSED': { title: 'The Decisive Voice', icon: '⚡', tagline: 'Strong convictions, clear conclusions' },
  'ASSERTIVE-BALANCED': { title: 'The Grounded Leader', icon: '🎯', tagline: 'Confident yet measured authority' },
  'MINIMAL-OPEN': { title: 'The Curious Minimalist', icon: '🔍', tagline: 'Economy of words, wealth of wonder' },
  'MINIMAL-CLOSED': { title: 'The Precise Crafter', icon: '✂️', tagline: 'Every word earns its place' },
  'MINIMAL-BALANCED': { title: 'The Quiet Observer', icon: '🌿', tagline: 'Stillness speaks volumes' },
  'POETIC-OPEN': { title: 'The Lyrical Dreamer', icon: '🌙', tagline: 'Language as living art' },
  'POETIC-CLOSED': { title: 'The Verse Weaver', icon: '🎭', tagline: 'Beauty in structured form' },
  'POETIC-BALANCED': { title: 'The Rhythmic Voice', icon: '🎵', tagline: 'Melody meets meaning' },
  'DENSE-OPEN': { title: 'The Deep Diver', icon: '🌊', tagline: 'Complex ideas, open inquiry' },
  'DENSE-CLOSED': { title: 'The Scholarly Mind', icon: '📚', tagline: 'Thorough, authoritative, complete' },
  'DENSE-BALANCED': { title: 'The Thoughtful Analyst', icon: '🔬', tagline: 'Depth with deliberation' },
  'CONVERSATIONAL-OPEN': { title: 'The Warm Connector', icon: '☕', tagline: 'Writing that feels like talking' },
  'CONVERSATIONAL-CLOSED': { title: 'The Friendly Guide', icon: '🗣️', tagline: 'Approachable expertise' },
  'CONVERSATIONAL-BALANCED': { title: 'The Natural Storyteller', icon: '🌻', tagline: 'Effortless engagement' },
  'FORMAL-OPEN': { title: 'The Diplomatic Voice', icon: '🏛️', tagline: 'Professional polish, genuine curiosity' },
  'FORMAL-CLOSED': { title: 'The Authority', icon: '📋', tagline: 'Commanding with credibility' },
  'FORMAL-BALANCED': { title: 'The Composed Professional', icon: '🎩', tagline: 'Measured excellence' },
  'INTERROGATIVE-OPEN': { title: 'The Questioner', icon: '❓', tagline: 'Curiosity as method' },
  'INTERROGATIVE-CLOSED': { title: 'The Examiner', icon: '🔎', tagline: 'Questions that lead somewhere' },
  'INTERROGATIVE-BALANCED': { title: 'The Socratic Mind', icon: '💭', tagline: 'Wisdom through inquiry' },
  'HEDGED-OPEN': { title: 'The Thoughtful Explorer', icon: '🌫️', tagline: 'Nuance over certainty' },
  'HEDGED-CLOSED': { title: 'The Careful Analyst', icon: '⚖️', tagline: 'Measured conclusions' },
  'HEDGED-BALANCED': { title: 'The Nuanced Voice', icon: '🎨', tagline: 'Complexity acknowledged' },
  'PARALLEL-OPEN': { title: 'The Pattern Maker', icon: '🔗', tagline: 'Rhythm creates meaning' },
  'PARALLEL-CLOSED': { title: 'The Structural Artist', icon: '🏗️', tagline: 'Architecture in prose' },
  'PARALLEL-BALANCED': { title: 'The Balanced Builder', icon: '⚙️', tagline: 'Form serves function' },
  'LONGFORM-OPEN': { title: 'The Epic Voice', icon: '📖', tagline: 'Stories that unfold' },
  'LONGFORM-CLOSED': { title: 'The Comprehensive Mind', icon: '🗺️', tagline: 'Thorough exploration' },
  'LONGFORM-BALANCED': { title: 'The Patient Narrator', icon: '🌳', tagline: 'Ideas given room to breathe' }
};

function deriveProfileType(metrics) {
  const scores = {
    ASSERTIVE: 0, MINIMAL: 0, POETIC: 0, DENSE: 0, CONVERSATIONAL: 0,
    FORMAL: 0, INTERROGATIVE: 0, HEDGED: 0, PARALLEL: 0, LONGFORM: 0
  };
  
  // Token-based signals
  if (metrics.avgTokens < 6) scores.MINIMAL += 3;
  else if (metrics.avgTokens > 12) scores.LONGFORM += 3;
  else if (metrics.avgTokens > 9) scores.DENSE += 2;
  
  // First-person signals
  if (metrics.firstPersonRate > 0.12) scores.ASSERTIVE += 2;
  if (metrics.firstPersonRate > 0.08) scores.CONVERSATIONAL += 1;
  if (metrics.firstPersonRate < 0.03) scores.FORMAL += 2;
  
  // Question signals
  if (metrics.questionRate > 0.3) scores.INTERROGATIVE += 4;
  else if (metrics.questionRate > 0.15) scores.INTERROGATIVE += 2;
  
  // Abstract/hedging signals
  if (metrics.abstractRate > 0.2) scores.HEDGED += 3;
  else if (metrics.abstractRate > 0.12) scores.HEDGED += 1;
  
  // Nominalization signals
  if (metrics.nominalizationRate > 0.15) scores.FORMAL += 3;
  else if (metrics.nominalizationRate > 0.08) scores.DENSE += 2;
  
  // Tool signals
  if (metrics.tools.T1) scores.ASSERTIVE += 2;
  if (metrics.tools.T2) scores.POETIC += 2;
  if (metrics.tools.T3) scores.POETIC += 2;
  if (metrics.tools.T5) scores.LONGFORM += 2;
  if (metrics.tools.T6) scores.DENSE += 2;
  
  // Complexity signals
  if (metrics.tickerComplexity > 1.5) scores.DENSE += 2;
  if (metrics.tickerComplexity < 1.1) scores.MINIMAL += 1;
  
  // Parity signals
  if (metrics.parityImbalance < 0.1) scores.PARALLEL += 2;
  if (metrics.parityDominance === 'even') scores.FORMAL += 1;
  if (metrics.parityDominance === 'odd') scores.CONVERSATIONAL += 1;
  
  // Find winner
  let maxScore = 0, winner = 'CONVERSATIONAL';
  for (const [type, score] of Object.entries(scores)) {
    if (score > maxScore) { maxScore = score; winner = type; }
  }
  
  return { type: winner, score: maxScore, allScores: scores };
}

function deriveStance(metrics) {
  const scores = { OPEN: 0, CLOSED: 0, BALANCED: 0, CONTRADICTORY: 0 };
  
  // Question rate → openness
  if (metrics.questionRate > 0.2) scores.OPEN += 3;
  else if (metrics.questionRate > 0.1) scores.OPEN += 1;
  else if (metrics.questionRate < 0.05) scores.CLOSED += 2;
  
  // Abstract rate → openness
  if (metrics.abstractRate > 0.15) scores.OPEN += 2;
  
  // First person + low questions → closed
  if (metrics.firstPersonRate > 0.1 && metrics.questionRate < 0.1) scores.CLOSED += 2;
  
  // Nominalization → closed
  if (metrics.nominalizationRate > 0.12) scores.CLOSED += 2;
  
  // Tool signals
  if (metrics.tools.T1 && metrics.tools.T2) scores.BALANCED += 2;
  if (metrics.tools.T4) scores.BALANCED += 1;
  
  // Parity balance → balanced
  if (metrics.parityImbalance < 0.15) scores.BALANCED += 2;
  
  // Mixed signals → contradictory
  if (scores.OPEN >= 2 && scores.CLOSED >= 2) scores.CONTRADICTORY += 2;
  
  // Find winner
  let maxScore = 0, winner = 'BALANCED';
  for (const [stance, score] of Object.entries(scores)) {
    if (score > maxScore) { maxScore = score; winner = stance; }
  }
  
  return { stance: winner, score: maxScore, allScores: scores };
}

// ═══════════════════════════════════════════════════════════════════
// MAIN CLASSIFIER
// ═══════════════════════════════════════════════════════════════════

function classifyProfile(text) {
  // Split into sentences
  const sentences = text
    .replace(/([.!?])\s+/g, '$1|||')
    .split('|||')
    .map(s => s.trim())
    .filter(s => s.length > 0);
  
  if (sentences.length === 0) {
    return { error: 'No sentences found', profileId: null };
  }
  
  // Encode sentences
  const encoded = sentences.map(s => encodeSentence(s, 50));
  
  // Aggregate metrics
  const allTickers = encoded.flatMap(e => e.tickers);
  const values = allTickers.map(t => parseInt(t.split('-')[0]) || 5);
  
  // Compute metrics
  const metrics = {
    sentenceCount: sentences.length,
    avgTokens: allTickers.length / sentences.length,
    questionRate: sentences.filter(s => s.includes('?')).length / sentences.length,
    
    // First-person rate
    firstPersonRate: allTickers.filter(t => t === '1').length / allTickers.length,
    
    // Abstract rate (7s)
    abstractRate: allTickers.filter(t => t.includes('7')).length / allTickers.length,
    
    // Nominalization rate (9s)
    nominalizationRate: allTickers.filter(t => t.includes('9')).length / allTickers.length,
    
    // Parity
    evenCount: values.filter(v => v % 2 === 0).length,
    oddCount: values.filter(v => v % 2 === 1).length,
    parityDominance: values.filter(v => v % 2 === 0).length > values.length / 2 ? 'even' : 'odd',
    parityImbalance: Math.abs(values.filter(v => v % 2 === 0).length - values.filter(v => v % 2 === 1).length) / values.length,
    
    // Complexity (compound tickers)
    tickerComplexity: allTickers.reduce((sum, t) => sum + t.split('-').length, 0) / allTickers.length,
    
    // Tools (aggregate)
    tools: detectTools(allTickers)
  };
  
  // Derive profile and stance
  const typeResult = deriveProfileType(metrics);
  const stanceResult = deriveStance(metrics);
  
  // Build profile ID
  const profileId = `${typeResult.type}-${stanceResult.stance}`;
  const meta = PROFILE_META[profileId] || {
    title: `${typeResult.type} + ${stanceResult.stance}`,
    icon: '📝',
    tagline: 'A unique voice.'
  };
  
  // Calculate confidence
  const maxTypeScore = 12;
  const maxStanceScore = 8;
  const confidence = (
    Math.min(1, typeResult.score / maxTypeScore) * 0.6 +
    Math.min(1, stanceResult.score / maxStanceScore) * 0.4
  );
  
  // Build traits
  const traits = [];
  if (metrics.tools.T1) traits.push('Strong parity binding');
  if (metrics.tools.T2) traits.push('Structural oscillation');
  if (metrics.tools.T3) traits.push('Harmonic resonance');
  if (metrics.firstPersonRate > 0.1) traits.push('Personal anchor');
  if (metrics.abstractRate > 0.15) traits.push('Abstract tendency');
  if (metrics.nominalizationRate > 0.1) traits.push('Formal register');
  if (metrics.questionRate > 0.2) traits.push('Inquiry-driven');
  if (metrics.tickerComplexity > 1.5) traits.push('Layered meaning');
  
  return {
    profileId,
    profileType: typeResult.type,
    stance: stanceResult.stance,
    title: meta.title,
    icon: meta.icon,
    tagline: meta.tagline,
    confidence: Math.round(confidence * 100) / 100,
    traits: traits.slice(0, 5),
    
    metrics: {
      sentenceCount: metrics.sentenceCount,
      avgTokens: Math.round(metrics.avgTokens * 10) / 10,
      wordCount: allTickers.length,
      questionRate: Math.round(metrics.questionRate * 100),
      firstPersonRate: Math.round(metrics.firstPersonRate * 100),
      abstractRate: Math.round(metrics.abstractRate * 100)
    },
    
    lncp: {
      tools: metrics.tools,
      parityDominance: metrics.parityDominance,
      parityImbalance: Math.round(metrics.parityImbalance * 100) / 100,
      tickerComplexity: Math.round(metrics.tickerComplexity * 100) / 100
    },
    
    // For pattern storage
    signature: encoded[0]?.signature || '',
    tokens: allTickers.slice(0, 50),
    
    scores: {
      type: typeResult.allScores,
      stance: stanceResult.allScores
    }
  };
}

// Export for extension use
if (typeof window !== 'undefined') {
  window.LNCP = { classifyProfile, encodeSentence, detectTools, PROFILE_META };
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { classifyProfile, encodeSentence, detectTools, PROFILE_META };
}
