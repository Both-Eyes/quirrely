/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY UNIFIED PROFILE SYSTEM v2.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Single source of truth for all profile metadata across:
 * - Web app frontend
 * - Browser extension
 * - Blog system
 * - Dashboard
 * - API responses
 * 
 * Aligned with LNCP v3.8 "Quinquaginta"
 * 
 * Profile Types: 10 (ASSERTIVE, MINIMAL, POETIC, DENSE, CONVERSATIONAL,
 *                    FORMAL, BALANCED, LONGFORM, INTERROGATIVE, HEDGED)
 * Stances: 4 (OPEN, CLOSED, BALANCED, CONTRADICTORY)
 * Total Combinations: 40
 */

const QUIRRELY_VERSION = '2.0.0';
const LNCP_VERSION = '3.8';

// ═══════════════════════════════════════════════════════════════════════════
// PROFILE TYPE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════

const PROFILE_TYPES = {
  ASSERTIVE: {
    name: 'Assertive',
    shortDesc: 'Direct and confident',
    longDesc: 'You lead with conviction. Your sentences are declarations, not suggestions. Readers know where you stand.',
    color: '#FF6B6B',
    gradient: 'linear-gradient(135deg, #FF6B6B 0%, #E55A4A 100%)',
    icon: '⚡',
    traits: ['Direct statements', 'High confidence', 'Clear positions', 'Action-oriented'],
    writerExamples: ['Ernest Hemingway', 'Christopher Hitchens', 'Joan Didion'],
    lncpSignals: ['High first-person rate', 'Low abstract rate', 'T1 tool activation', 'Short sentences']
  },
  
  MINIMAL: {
    name: 'Minimal',
    shortDesc: 'Economical and precise',
    longDesc: 'Every word earns its place. You trust readers to fill the gaps. Less is more.',
    color: '#4ECDC4',
    gradient: 'linear-gradient(135deg, #4ECDC4 0%, #3BB8B0 100%)',
    icon: '💎',
    traits: ['Economy of words', 'Precise diction', 'White space', 'Implied meaning'],
    writerExamples: ['Raymond Carver', 'Lydia Davis', 'Amy Hempel'],
    lncpSignals: ['Low token count', 'Simple ticker patterns', 'Single-sentence dominance']
  },
  
  POETIC: {
    name: 'Poetic',
    shortDesc: 'Rhythmic and evocative',
    longDesc: 'Language as music. Your prose has cadence, imagery, and resonance beyond literal meaning.',
    color: '#A29BFE',
    gradient: 'linear-gradient(135deg, #A29BFE 0%, #8B7CF0 100%)',
    icon: '🌙',
    traits: ['Rhythmic flow', 'Imagery', 'Sound patterns', 'Emotional resonance'],
    writerExamples: ['Toni Morrison', 'Ocean Vuong', 'Annie Dillard'],
    lncpSignals: ['T2/T3 tool activation', 'High token variance', 'Complex ticker patterns']
  },
  
  DENSE: {
    name: 'Dense',
    shortDesc: 'Complex and thorough',
    longDesc: 'You pack meaning tightly. Subordinate clauses, qualifications, layered ideas. Readers must engage actively.',
    color: '#6C5CE7',
    gradient: 'linear-gradient(135deg, #6C5CE7 0%, #5B4BD5 100%)',
    icon: '📚',
    traits: ['Layered complexity', 'Subordination', 'Technical precision', 'Comprehensive'],
    writerExamples: ['David Foster Wallace', 'Zadie Smith', 'Ta-Nehisi Coates'],
    lncpSignals: ['High ticker complexity', 'High nominalization rate', 'Long sentences', 'T6 activation']
  },
  
  CONVERSATIONAL: {
    name: 'Conversational',
    shortDesc: 'Warm and accessible',
    longDesc: 'Writing that feels like talking. You bridge the page-reader gap with directness and warmth.',
    color: '#FDCB6E',
    gradient: 'linear-gradient(135deg, #FDCB6E 0%, #F0B93D 100%)',
    icon: '💬',
    traits: ['Informal tone', 'Reader address', 'Contractions', 'Personal asides'],
    writerExamples: ['David Sedaris', 'Nora Ephron', 'Bill Bryson'],
    lncpSignals: ['Odd parity dominance', 'First-person present', 'Question markers']
  },
  
  FORMAL: {
    name: 'Formal',
    shortDesc: 'Professional and structured',
    longDesc: 'Institutional voice. Clear, professional, appropriate for official contexts. Authority through register.',
    color: '#636E72',
    gradient: 'linear-gradient(135deg, #636E72 0%, #4A5459 100%)',
    icon: '🏛️',
    traits: ['Professional register', 'Third-person', 'Structured', 'Authoritative'],
    writerExamples: ['Academic journals', 'Legal writing', 'Official communications'],
    lncpSignals: ['Even parity dominance', 'High nominalization', 'Low first-person', 'No questions']
  },
  
  BALANCED: {
    name: 'Balanced',
    shortDesc: 'Measured and fair',
    longDesc: 'You see multiple sides. Your writing weighs perspectives, acknowledges complexity, avoids extremes.',
    color: '#00B894',
    gradient: 'linear-gradient(135deg, #00B894 0%, #00A381 100%)',
    icon: '⚖️',
    traits: ['Multiple perspectives', 'Measured tone', 'Acknowledgment', 'Nuance'],
    writerExamples: ['Malcolm Gladwell', 'Atul Gawande', 'Michael Lewis'],
    lncpSignals: ['Balance phrases detected', 'Moderate abstract rate', 'Parity equilibrium']
  },
  
  LONGFORM: {
    name: 'Longform',
    shortDesc: 'Sustained and exploratory',
    longDesc: 'You take your time. Ideas unfold across paragraphs. Readers are invited on a journey.',
    color: '#0984E3',
    gradient: 'linear-gradient(135deg, #0984E3 0%, #0770C4 100%)',
    icon: '🗺️',
    traits: ['Extended development', 'Narrative arc', 'Deep exploration', 'Patient unfolding'],
    writerExamples: ['John McPhee', 'Rebecca Solnit', 'George Orwell'],
    lncpSignals: ['High sentence count', 'T6 sustained', 'First-person exploration', 'Low abstract']
  },
  
  INTERROGATIVE: {
    name: 'Interrogative',
    shortDesc: 'Question-driven',
    longDesc: 'You lead with questions. Inquiry is your method. You invite readers to think alongside you.',
    color: '#E17055',
    gradient: 'linear-gradient(135deg, #E17055 0%, #D15F44 100%)',
    icon: '❓',
    traits: ['Questions as structure', 'Socratic method', 'Inquiry-based', 'Reader engagement'],
    writerExamples: ['Socrates (via Plato)', 'Maria Popova', 'Alain de Botton'],
    lncpSignals: ['High question rate (>40%)', 'WH/FP questions', 'Parity balanced']
  },
  
  HEDGED: {
    name: 'Hedged',
    shortDesc: 'Cautious and qualified',
    longDesc: 'You acknowledge uncertainty. "Perhaps," "might," "seems." Intellectual honesty over false confidence.',
    color: '#81ECEC',
    gradient: 'linear-gradient(135deg, #81ECEC 0%, #6DDADA 100%)',
    icon: '🌫️',
    traits: ['Qualification', 'Uncertainty markers', 'Tentative claims', 'Epistemic humility'],
    writerExamples: ['Academic writing', 'Scientific papers', 'Philosophical inquiry'],
    lncpSignals: ['High abstract rate (>20%)', 'Low nominalization', 'Odd parity', 'Soft language']
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// STANCE DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════

const STANCES = {
  OPEN: {
    name: 'Open',
    shortDesc: 'Inviting dialogue',
    longDesc: 'You write to explore, not conclude. Questions welcome. The conversation continues.',
    color: '#4ECDC4',
    icon: '🔓',
    indicators: ['Questions', 'Exploration', 'Invitation', 'Uncertainty acknowledged']
  },
  
  CLOSED: {
    name: 'Closed',
    shortDesc: 'Conclusive',
    longDesc: 'You write to declare. The thinking is done. Readers receive conclusions.',
    color: '#FF6B6B',
    icon: '🔒',
    indicators: ['Declarations', 'Conclusions', 'Certainty', 'Finality']
  },
  
  BALANCED: {
    name: 'Balanced',
    shortDesc: 'Weighing sides',
    longDesc: 'You present multiple perspectives fairly. Neither fully open nor closed—deliberately measured.',
    color: '#A29BFE',
    icon: '⚖️',
    indicators: ['Both sides', 'Acknowledgment', 'Fair treatment', 'Measured']
  },
  
  CONTRADICTORY: {
    name: 'Contradictory',
    shortDesc: 'Embracing tension',
    longDesc: 'You hold opposing ideas simultaneously. The contradiction is the point, not a flaw.',
    color: '#FDCB6E',
    icon: '🔀',
    indicators: ['Paradox', 'Tension', 'Both/and', 'Complexity']
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// FULL PROFILE COMBINATIONS (40 total)
// ═══════════════════════════════════════════════════════════════════════════

const PROFILE_META = {
  // ASSERTIVE combinations
  'ASSERTIVE-OPEN': {
    title: 'The Confident Listener',
    icon: '🎯',
    tagline: 'You state your case. Then you listen.',
    description: 'You lead with conviction but remain genuinely curious about pushback. Strong positions, open ears.',
    famousWriters: ['Barack Obama (speeches)', 'Brené Brown', 'Simon Sinek']
  },
  'ASSERTIVE-CLOSED': {
    title: 'The Commander',
    icon: '⚡',
    tagline: 'This is how it is.',
    description: 'No hedging, no qualification. You state truth as you see it. Readers follow or don\'t.',
    famousWriters: ['Ernest Hemingway', 'Christopher Hitchens', 'Ayn Rand']
  },
  'ASSERTIVE-BALANCED': {
    title: 'The Measured Leader',
    icon: '⚖️',
    tagline: 'Here\'s what I believe. Here\'s why reasonable people disagree.',
    description: 'Strong convictions paired with intellectual honesty about alternatives.',
    famousWriters: ['David Brooks', 'Peggy Noonan', 'George Will']
  },
  'ASSERTIVE-CONTRADICTORY': {
    title: 'The Confident Paradox',
    icon: '🎭',
    tagline: 'I believe X. I also believe not-X. Deal with it.',
    description: 'You assert contradictions confidently. The paradox is the message.',
    famousWriters: ['Nassim Taleb', 'G.K. Chesterton', 'Oscar Wilde']
  },
  
  // MINIMAL combinations
  'MINIMAL-OPEN': {
    title: 'The Quiet Inviter',
    icon: '🌿',
    tagline: 'Few words. Open ears.',
    description: 'Sparse prose that leaves room for reader participation and interpretation.',
    famousWriters: ['Raymond Carver', 'Lydia Davis', 'Samuel Beckett']
  },
  'MINIMAL-CLOSED': {
    title: 'The Essentialist',
    icon: '💎',
    tagline: 'Said enough.',
    description: 'Every word final. Nothing to add. Complete in its brevity.',
    famousWriters: ['Cormac McCarthy', 'Amy Hempel', 'Hemingway (at his sparsest)']
  },
  'MINIMAL-BALANCED': {
    title: 'The Brief Diplomat',
    icon: '🪶',
    tagline: 'This. Also that.',
    description: 'Balanced perspectives delivered with extreme economy.',
    famousWriters: ['Haiku masters', 'Aphorism writers']
  },
  'MINIMAL-CONTRADICTORY': {
    title: 'The Zen Paradox',
    icon: '☯️',
    tagline: 'Yes and no.',
    description: 'Koans in prose. Contradictions expressed with radical simplicity.',
    famousWriters: ['Zen teachers', 'Kahlil Gibran']
  },
  
  // POETIC combinations
  'POETIC-OPEN': {
    title: 'The Lyrical Explorer',
    icon: '🌊',
    tagline: 'The words arrive like weather, unbidden.',
    description: 'Beautiful language in service of open inquiry. Imagery meets curiosity.',
    famousWriters: ['Ocean Vuong', 'Mary Oliver', 'Pablo Neruda']
  },
  'POETIC-CLOSED': {
    title: 'The Oracle',
    icon: '🔮',
    tagline: 'The truth arrives dressed in silk.',
    description: 'Prophetic certainty delivered through beauty. Declarations that sing.',
    famousWriters: ['Toni Morrison', 'James Baldwin', 'Rainer Maria Rilke']
  },
  'POETIC-BALANCED': {
    title: 'The Dual Painter',
    icon: '🎨',
    tagline: 'On one hand, the morning light. On the other, the same light fading.',
    description: 'Multiple perspectives rendered with equal beauty.',
    famousWriters: ['Virginia Woolf', 'Michael Ondaatje', 'Marilynne Robinson']
  },
  'POETIC-CONTRADICTORY': {
    title: 'The Shadow Dancer',
    icon: '🌓',
    tagline: 'We are made of opposites. Light that casts shadow.',
    description: 'Paradox as poetry. Beauty in the tension between opposites.',
    famousWriters: ['Rumi', 'William Blake', 'Emily Dickinson']
  },
  
  // DENSE combinations
  'DENSE-OPEN': {
    title: 'The Curious Scholar',
    icon: '📚',
    tagline: 'The phenomenon invites analysis, though certainty remains elusive.',
    description: 'Complex exploration that acknowledges limits of knowledge.',
    famousWriters: ['Susan Sontag', 'Judith Butler', 'Michel Foucault']
  },
  'DENSE-CLOSED': {
    title: 'The Authority',
    icon: '🏛️',
    tagline: 'The evidence demonstrates conclusively.',
    description: 'Comprehensive arguments leading to definitive conclusions.',
    famousWriters: ['Academic papers', 'Legal briefs', 'Scientific reviews']
  },
  'DENSE-BALANCED': {
    title: 'The Synthesizer',
    icon: '🔬',
    tagline: 'While one view emphasizes X, another foregrounds Y.',
    description: 'Complex treatment of multiple sophisticated positions.',
    famousWriters: ['Isaiah Berlin', 'Martha Nussbaum', 'Amartya Sen']
  },
  'DENSE-CONTRADICTORY': {
    title: 'The Complexity Theorist',
    icon: '🌀',
    tagline: 'The contradiction inheres in the phenomenon itself.',
    description: 'Sophisticated analysis revealing irreducible paradox.',
    famousWriters: ['Slavoj Žižek', 'Jacques Derrida', 'David Foster Wallace']
  },
  
  // CONVERSATIONAL combinations
  'CONVERSATIONAL-OPEN': {
    title: 'The Curious Friend',
    icon: '💬',
    tagline: 'So here\'s the thing—I\'ve been thinking about this a lot.',
    description: 'Warm, accessible exploration. Like chatting with a thoughtful friend.',
    famousWriters: ['David Sedaris', 'Nora Ephron', 'Samantha Irby']
  },
  'CONVERSATIONAL-CLOSED': {
    title: 'The Straight Talker',
    icon: '🎤',
    tagline: 'Look, I\'m just going to tell you how it is.',
    description: 'Direct, no-nonsense communication with personal warmth.',
    famousWriters: ['Anthony Bourdain', 'Hunter S. Thompson', 'Roxane Gay']
  },
  'CONVERSATIONAL-BALANCED': {
    title: 'The Thoughtful Pal',
    icon: '🤝',
    tagline: 'Okay, so here\'s where it gets complicated.',
    description: 'Friendly voice navigating complexity with the reader.',
    famousWriters: ['Malcolm Gladwell', 'Mary Roach', 'Jon Ronson']
  },
  'CONVERSATIONAL-CONTRADICTORY': {
    title: 'The Honest Mess',
    icon: '🫶',
    tagline: 'Can I be honest? I believe two completely opposite things.',
    description: 'Authentic admission of internal contradiction, warmly shared.',
    famousWriters: ['Anne Lamott', 'Cheryl Strayed', 'Glennon Doyle']
  },
  
  // FORMAL combinations
  'FORMAL-OPEN': {
    title: 'The Diplomatic Professional',
    icon: '📋',
    tagline: 'The question before us merits careful consideration.',
    description: 'Professional register employed for genuine inquiry.',
    famousWriters: ['Policy papers', 'Diplomatic communications', 'Academic proposals']
  },
  'FORMAL-CLOSED': {
    title: 'The Executive',
    icon: '🏢',
    tagline: 'The organization has determined the following.',
    description: 'Institutional authority delivering definitive positions.',
    famousWriters: ['Corporate communications', 'Legal rulings', 'Official statements']
  },
  'FORMAL-BALANCED': {
    title: 'The Impartial Analyst',
    icon: '📊',
    tagline: 'The evidence supports multiple interpretations.',
    description: 'Professional fairness in presenting competing views.',
    famousWriters: ['Policy analyses', 'Research summaries', 'Judicial opinions']
  },
  'FORMAL-CONTRADICTORY': {
    title: 'The Institutional Realist',
    icon: '🏗️',
    tagline: 'The organization recognizes conflicting imperatives.',
    description: 'Formal acknowledgment of structural tensions.',
    famousWriters: ['Organizational theory', 'Systems analysis']
  },
  
  // BALANCED combinations
  'BALANCED-OPEN': {
    title: 'The Humble Seeker',
    icon: '🔍',
    tagline: 'There are good arguments on multiple sides, and I\'m genuinely uncertain.',
    description: 'Fair-minded exploration without premature closure.',
    famousWriters: ['Atul Gawande', 'Oliver Sacks', 'Carl Sagan']
  },
  'BALANCED-CLOSED': {
    title: 'The Fair Judge',
    icon: '⚖️',
    tagline: 'Having considered all sides, the evidence most strongly supports this conclusion.',
    description: 'Conclusion reached through demonstrated fairness.',
    famousWriters: ['Supreme Court opinions', 'Editorial boards']
  },
  'BALANCED-BALANCED': {
    title: 'The True Moderate',
    icon: '🎚️',
    tagline: 'There are compelling arguments on multiple sides, and I hold my view with uncertainty.',
    description: 'Genuine moderation—not fence-sitting, but earned ambivalence.',
    famousWriters: ['Isaiah Berlin', 'John Stuart Mill']
  },
  'BALANCED-CONTRADICTORY': {
    title: 'The Tension Holder',
    icon: '🔀',
    tagline: 'Each position has merit. They also contradict. The contradiction might be the point.',
    description: 'Fair treatment revealing that both sides may be right and wrong.',
    famousWriters: ['F. Scott Fitzgerald ("The test of a first-rate intelligence...")']
  },
  
  // LONGFORM combinations
  'LONGFORM-OPEN': {
    title: 'The Patient Explorer',
    icon: '🗺️',
    tagline: 'The question I want to explore is one I\'ve been sitting with for some time.',
    description: 'Extended inquiry that takes the reader on a journey of discovery.',
    famousWriters: ['Rebecca Solnit', 'John McPhee', 'Annie Dillard']
  },
  'LONGFORM-CLOSED': {
    title: 'The Thorough Advocate',
    icon: '📖',
    tagline: 'What follows is a thorough examination demonstrating conclusively the position I advance.',
    description: 'Comprehensive argument building to definitive conclusion.',
    famousWriters: ['Legal briefs', 'Investigative journalism', 'Thomas Piketty']
  },
  'LONGFORM-BALANCED': {
    title: 'The Deep Diver',
    icon: '🌊',
    tagline: 'The complexity of this issue demands extended treatment.',
    description: 'Sustained exploration giving fair treatment to all perspectives.',
    famousWriters: ['The New Yorker profiles', 'Robert Caro', 'Katherine Boo']
  },
  'LONGFORM-CONTRADICTORY': {
    title: 'The Complexity Navigator',
    icon: '🧭',
    tagline: 'What follows cannot be neatly resolved. I will take you through the contradictions.',
    description: 'Extended meditation on irreducible tensions.',
    famousWriters: ['David Foster Wallace', 'Maggie Nelson', 'Teju Cole']
  },
  
  // INTERROGATIVE combinations
  'INTERROGATIVE-OPEN': {
    title: 'The Questioner',
    icon: '❓',
    tagline: 'What if we asked a different question entirely?',
    description: 'Questions that open rather than close, inviting genuine inquiry.',
    famousWriters: ['Maria Popova', 'Krista Tippett', 'Parker Palmer']
  },
  'INTERROGATIVE-CLOSED': {
    title: 'The Socratic',
    icon: '🏺',
    tagline: 'Is it not obvious what the answer must be?',
    description: 'Rhetorical questions that lead to predetermined conclusions.',
    famousWriters: ['Socrates (via Plato)', 'Trial lawyers', 'Political rhetoric']
  },
  'INTERROGATIVE-BALANCED': {
    title: 'The Facilitator',
    icon: '🎯',
    tagline: 'What are the strongest arguments on each side?',
    description: 'Questions designed to illuminate multiple perspectives fairly.',
    famousWriters: ['Mediators', 'Skilled interviewers', 'Discussion facilitators']
  },
  'INTERROGATIVE-CONTRADICTORY': {
    title: 'The Koan Master',
    icon: '🪷',
    tagline: 'What if both questions lead to opposite truths?',
    description: 'Questions that reveal paradox rather than resolve it.',
    famousWriters: ['Zen masters', 'Philosophical provocateurs']
  },
  
  // HEDGED combinations
  'HEDGED-OPEN': {
    title: 'The Tentative Thinker',
    icon: '🌱',
    tagline: 'I think, perhaps, there might be something worth considering here.',
    description: 'Cautious exploration with full acknowledgment of uncertainty.',
    famousWriters: ['Early-career academics', 'Thoughtful bloggers']
  },
  'HEDGED-CLOSED': {
    title: 'The Careful Concluder',
    icon: '🎓',
    tagline: 'It would seem, on balance, that this conclusion is warranted.',
    description: 'Conclusions reached with appropriate epistemic humility.',
    famousWriters: ['Scientific papers', 'Philosophical arguments']
  },
  'HEDGED-BALANCED': {
    title: 'The Nuanced Voice',
    icon: '🌫️',
    tagline: 'There seem to be reasonable arguments on multiple sides.',
    description: 'Tentative fairness—acknowledging uncertainty about uncertainty.',
    famousWriters: ['Academic reviews', 'Careful journalism']
  },
  'HEDGED-CONTRADICTORY': {
    title: 'The Uncertain Sage',
    icon: '💭',
    tagline: 'It might be that both things are true, though perhaps neither is.',
    description: 'Humble acknowledgment that even contradictions are uncertain.',
    famousWriters: ['Philosophical essays', 'Contemplative writing']
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// TIER DEFINITIONS (aligned with backend feature_gate.py)
// ═══════════════════════════════════════════════════════════════════════════

const TIERS = {
  free: {
    name: 'Free',
    price: 0,
    features: ['Basic analysis', 'Writer matches', '5 analyses/day'],
    limits: { dailyAnalyses: 5 },
    badge: { text: 'FREE', color: '#636E72' }
  },
  trial: {
    name: '7-Day Trial',
    price: 0,
    duration: 7,
    features: ['All Pro features', 'Save results', 'Profile history', 'Evolution tracking', '100 analyses/day'],
    limits: { dailyAnalyses: 100 },
    badge: { text: 'TRIAL', color: '#0984E3' }
  },
  pro: {
    name: 'Pro',
    priceMonthly: 4.99,
    priceAnnual: 50,
    features: [
      'Unlimited analyses',
      'Save all results',
      'Profile history',
      'Evolution tracking',
      'Detailed insights',
      'Export results',
      'Featured submission',
      'Extension sync',
      'Priority support'
    ],
    limits: { dailyAnalyses: 1000 },
    badge: { text: 'PRO', color: '#FF6B6B' }
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE DEFINITIONS (aligned with backend feature_gate.py)
// ═══════════════════════════════════════════════════════════════════════════

const FEATURES = {
  basic_analysis: {
    name: 'Basic Analysis',
    description: 'Run LNCP analysis and see your profile',
    tiers: { free: true, trial: true, pro: true },
    icon: '🔍'
  },
  writer_matches: {
    name: 'Writer Matches',
    description: 'See famous writers with similar voices',
    tiers: { free: true, trial: true, pro: true },
    icon: '✍️'
  },
  save_results: {
    name: 'Save Results',
    description: 'Save analysis results to your account',
    tiers: { free: false, trial: true, pro: true },
    icon: '💾'
  },
  profile_history: {
    name: 'Profile History',
    description: 'View your past analyses and compare them',
    tiers: { free: false, trial: true, pro: true },
    icon: '📜'
  },
  evolution_tracking: {
    name: 'Evolution Tracking',
    description: 'See how your writing voice changes over time',
    tiers: { free: false, trial: true, pro: true },
    icon: '📈'
  },
  detailed_insights: {
    name: 'Detailed Insights',
    description: 'Deep dive into your profile characteristics',
    tiers: { free: false, trial: false, pro: true },
    icon: '🔬'
  },
  export_results: {
    name: 'Export Results',
    description: 'Download results as PDF or JSON',
    tiers: { free: false, trial: false, pro: true },
    icon: '📤'
  },
  featured_submission: {
    name: 'Featured Submission',
    description: 'Submit your writing for the featured section',
    tiers: { free: false, trial: false, pro: true },
    icon: '⭐'
  },
  unlimited_analyses: {
    name: 'Unlimited Analyses',
    description: 'No daily analysis limit',
    tiers: { free: false, trial: true, pro: true },
    icon: '♾️'
  },
  extension_sync: {
    name: 'Extension Sync',
    description: 'Sync history with browser extension',
    tiers: { free: false, trial: true, pro: true },
    icon: '🔄'
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get full profile data by ID
 */
function getProfile(profileId) {
  const [type, stance] = profileId.split('-');
  const meta = PROFILE_META[profileId];
  const typeData = PROFILE_TYPES[type];
  const stanceData = STANCES[stance];
  
  if (!meta || !typeData || !stanceData) {
    return null;
  }
  
  return {
    id: profileId,
    type,
    stance,
    ...meta,
    typeData,
    stanceData,
    color: typeData.color,
    gradient: typeData.gradient
  };
}

/**
 * Get all profiles of a specific type
 */
function getProfilesByType(type) {
  return Object.keys(PROFILE_META)
    .filter(id => id.startsWith(type + '-'))
    .map(getProfile);
}

/**
 * Get all profiles with a specific stance
 */
function getProfilesByStance(stance) {
  return Object.keys(PROFILE_META)
    .filter(id => id.endsWith('-' + stance))
    .map(getProfile);
}

/**
 * Check if user has access to a feature
 */
function hasFeatureAccess(feature, tier) {
  const featureDef = FEATURES[feature];
  if (!featureDef) return false;
  return featureDef.tiers[tier] === true;
}

/**
 * Get upgrade prompt for a feature
 */
function getUpgradePrompt(feature, currentTier) {
  const featureDef = FEATURES[feature];
  if (!featureDef) return null;
  
  if (featureDef.tiers[currentTier]) return null; // Already has access
  
  if (currentTier === 'free' && featureDef.tiers.trial) {
    return {
      message: `Start your free 7-day trial to unlock ${featureDef.name}`,
      action: 'start_trial',
      buttonText: 'Start Free Trial'
    };
  }
  
  return {
    message: `Upgrade to Pro to unlock ${featureDef.name}`,
    action: 'upgrade',
    buttonText: 'Upgrade to Pro — $4.99/mo'
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    QUIRRELY_VERSION,
    LNCP_VERSION,
    PROFILE_TYPES,
    STANCES,
    PROFILE_META,
    TIERS,
    FEATURES,
    getProfile,
    getProfilesByType,
    getProfilesByStance,
    hasFeatureAccess,
    getUpgradePrompt
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyProfiles = {
    QUIRRELY_VERSION,
    LNCP_VERSION,
    PROFILE_TYPES,
    STANCES,
    PROFILE_META,
    TIERS,
    FEATURES,
    getProfile,
    getProfilesByType,
    getProfilesByStance,
    hasFeatureAccess,
    getUpgradePrompt
  };
}
