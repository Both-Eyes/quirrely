import React, { useState, useCallback, useEffect } from 'react';

// =============================================================================
// LNCP Web App - Structural Writing Analysis
// Design Direction: Editorial/Literary - Like a beautifully typeset manuscript
// =============================================================================

// API Configuration
const API_BASE = 'http://localhost:8000';

// =============================================================================
// API Functions
// =============================================================================

const api = {
  async initGame(mode = 'STORY') {
    const res = await fetch(`${API_BASE}/api/game/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    if (!res.ok) throw new Error('Failed to initialize game');
    return res.json();
  },

  async submitGroup(sessionId, sentences) {
    const res = await fetch(`${API_BASE}/api/game/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, sentences }),
    });
    if (!res.ok) throw new Error('Failed to submit group');
    return res.json();
  },

  async runAnalysis(sessionId) {
    const res = await fetch(`${API_BASE}/api/analyze/${sessionId}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to run analysis');
    return res.json();
  },

  async quickAnalyze(sentences) {
    const res = await fetch(`${API_BASE}/api/quick-analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sentences }),
    });
    if (!res.ok) throw new Error('Failed to analyze');
    return res.json();
  },
};

// =============================================================================
// Mock API for Demo Mode (when backend unavailable)
// =============================================================================

const mockApi = {
  sessionCounter: 0,
  sessions: {},

  async initGame(mode = 'STORY') {
    const sessionId = `mock-${++this.sessionCounter}`;
    this.sessions[sessionId] = {
      mode,
      groups: [],
      currentPromptIndex: 0,
    };
    return {
      session_id: sessionId,
      mode,
      current_prompt: {
        prompt_id: 'MOCK_001',
        text: mode === 'STORY' 
          ? 'Write 2–3 sentences about a moment of quiet realization.'
          : 'Write 2–3 sentences using at least one parenthetical aside.',
      },
      gate: { required: 3, completed: 0, is_complete: false },
    };
  },

  async submitGroup(sessionId, sentences) {
    const session = this.sessions[sessionId];
    if (!session) throw new Error('Session not found');
    
    session.groups.push(sentences);
    const completed = session.groups.length;
    const isComplete = completed >= 3;
    
    const prompts = [
      'Write 2–3 sentences that capture a small, overlooked detail.',
      'Write 2–3 sentences where something changes—subtly.',
      'Write 2–3 sentences that end on an open question.',
    ];
    
    return {
      session_id: sessionId,
      state: isComplete ? 'COMPLETION' : 'PLAY',
      gate: { required: 3, completed, is_complete: isComplete },
      last_submission: { status: 'VALID', message: 'Group accepted.' },
      current_prompt: isComplete ? null : {
        prompt_id: `MOCK_00${completed + 1}`,
        text: prompts[completed] || prompts[0],
      },
      coverage: { zero: true, operator: false, scope: true, is_satisfied: completed >= 2 },
      safety: { actor_state: 'NORMAL', is_deescalating: false, message: null },
    };
  },

  async runAnalysis(sessionId) {
    const session = this.sessions[sessionId];
    if (!session) throw new Error('Session not found');
    
    const sentences = session.groups.flat();
    return this.quickAnalyze(sentences, sessionId);
  },

  async quickAnalyze(sentences, sessionId = null) {
    // Generate mock results
    return {
      session_id: sessionId,
      sentences_analyzed: sentences,
      phase1: {
        outputs: {
          sentence_count: { count: sentences.length },
          token_volume: { total_tokens: sentences.join(' ').split(' ').length, mean_tokens_per_sentence: 8.5 },
          structural_variety: { unique_signatures: sentences.length, variety_ratio: 1.0 },
          signature_concentration: { top_signatures: [], top_3_coverage: 0 },
          zero_event_presence: { count: 1, rate: 0.17 },
          operator_event_presence: { count: 0, rate: 0 },
          scope_event_presence: { count: 2, rate: 0.33 },
          structural_density: { total_events: 3, mean_events_per_sentence: 0.5 },
          event_co_occurrence_profile: { distribution: { none: 4, scope_only: 2 } },
          ticker_profile: { unique_codes: 15, total_positions: 45 },
        },
      },
      phase2: {
        presentation_mode: sentences.length < 4 ? 'DESCRIPTIVE' : 'REFLECTIVE',
        outputs: {
          output_01: { name_user_facing: 'How Much You Shared', explanation: `${sentences.length} sentences present.`, example_insights: ['A sample to work with.', 'Patterns may emerge with more.'] },
          output_02: { name_user_facing: 'Word-Level Detail', explanation: 'Your sentences average about 8-9 words each.', example_insights: ['Compact and direct.', 'Room for expansion if needed.'] },
          output_03: { name_user_facing: 'Structural Fingerprints', explanation: 'Each sentence has a unique shape.', example_insights: ['Variety in your structures.', 'No two are alike.'] },
          output_04: { name_user_facing: 'Your Most Common Patterns', explanation: 'No dominant pattern yet.', example_insights: ['Your shapes are distributed.', 'Consistency may come with more writing.'] },
          output_05: { name_user_facing: "What's Left Unsaid", explanation: 'A few pauses appear in your writing.', example_insights: ['Moments of hesitation.', 'Space for the reader.'] },
          output_06: { name_user_facing: 'Connective Moves', explanation: 'No connective symbols detected.', example_insights: ['Clean flow without shortcuts.', 'Ideas stand alone.'] },
          output_07: { name_user_facing: 'Layered Meaning', explanation: 'Some nesting appears in parentheses.', example_insights: ['Asides add depth.', 'Thoughts within thoughts.'] },
          output_08: { name_user_facing: 'Complexity at a Glance', explanation: 'Light structural activity overall.', example_insights: ['Mostly straightforward.', 'Content leads the way.'] },
          output_09: { name_user_facing: 'How Your Patterns Combine', explanation: 'Most sentences have no structural markers.', example_insights: ['Clean and direct.', 'Structural simplicity.'] },
          output_10: { name_user_facing: 'Your Structural Codes', explanation: '15 distinct position codes.', example_insights: ['A fingerprint of your writing.', 'Unique to this sample.'] },
        },
      },
      phase3: {
        synthesis_scope: 'SAMPLE_ONLY',
        interpretive_frame: 'LNCP_PEIRCEAN',
        syntheses: [
          { synthesis_id: 'SYN_01', semiotic_lens: 'INTERPRETANT_STABILIZATION', synthesis_text: 'With this sample, patterns are beginning to form. The structures function as initial instances rather than stabilized forms.', related_outputs: ['output_01', 'output_03', 'output_04'] },
          { synthesis_id: 'SYN_02', semiotic_lens: 'MEDIATION_AND_BOUNDARY', synthesis_text: 'Boundary markers are sparse. Meaning flows without heavy mediation in this sample.', related_outputs: ['output_05', 'output_06', 'output_07'] },
          { synthesis_id: 'SYN_03', semiotic_lens: 'RELATIONAL_DENSITY', synthesis_text: 'Structural events remain light. The features do not cluster densely in this material.', related_outputs: ['output_08', 'output_09'] },
        ],
      },
      phase4a: {
        prompt_sets: [
          { prompt_set_id: 'PS_01', synthesis_id: 'SYN_01', semiotic_lens: 'INTERPRETANT_STABILIZATION', prompts: [
            { prompt_type: 'NOTICE', prompt_text: 'What stands out when you read your sentences back?' },
            { prompt_type: 'REFLECT', prompt_text: 'What might this structure make effortless?' },
            { prompt_type: 'REWRITE', prompt_text: 'Rewrite one sentence with a single aside in parentheses.' },
            { prompt_type: 'COMPARE', prompt_text: 'Compare the original to your rewrite—what shifted?' },
          ]},
          { prompt_set_id: 'PS_02', synthesis_id: 'SYN_02', semiotic_lens: 'MEDIATION_AND_BOUNDARY', prompts: [
            { prompt_type: 'NOTICE', prompt_text: 'Where does meaning pass through without pause?' },
            { prompt_type: 'REFLECT', prompt_text: 'What does this openness enable?' },
            { prompt_type: 'REWRITE', prompt_text: 'Add one boundary—a dash, parenthesis, or ellipsis.' },
            { prompt_type: 'COMPARE', prompt_text: 'How does the bounded version feel different?' },
          ]},
          { prompt_set_id: 'PS_03', synthesis_id: 'SYN_03', semiotic_lens: 'RELATIONAL_DENSITY', prompts: [
            { prompt_type: 'NOTICE', prompt_text: 'Where is the structure most sparse?' },
            { prompt_type: 'REFLECT', prompt_text: 'What does sparseness allow here?' },
            { prompt_type: 'REWRITE', prompt_text: 'Add one structural event—a pause or bracket.' },
            { prompt_type: 'COMPARE', prompt_text: 'Did adding density change the feel?' },
          ]},
        ],
      },
      phase4b: {
        synthesis_scope: 'SAMPLE_ONLY',
        interpretive_frame: 'LNCP_PEIRCEAN',
        guidance_sets: [
          { guidance_set_id: 'GS_01', synthesis_id: 'SYN_01', semiotic_lens: 'INTERPRETANT_STABILIZATION', items: [
            { item_type: 'GUIDE', text: 'Treat this as a structural snapshot: patterns are forming but not yet fixed.' },
            { item_type: 'PRACTICE', text: 'Write one more sentence in the same style, then compare.' },
            { item_type: 'SCENARIO', text: 'Imagine this structure in an email—how would it land?' },
            { item_type: 'COMPARE', text: 'Add a single structural layer and notice the shift.' },
          ]},
          { guidance_set_id: 'GS_02', synthesis_id: 'SYN_02', semiotic_lens: 'MEDIATION_AND_BOUNDARY', items: [
            { item_type: 'GUIDE', text: 'Your writing moves without heavy mediation—clean and direct.' },
            { item_type: 'PRACTICE', text: 'Try adding one pause marker and see what changes.' },
            { item_type: 'SCENARIO', text: 'Picture this in a work note—what does it make easier?' },
            { item_type: 'COMPARE', text: 'Compare a bounded version to the original.' },
          ]},
          { guidance_set_id: 'GS_03', synthesis_id: 'SYN_03', semiotic_lens: 'RELATIONAL_DENSITY', items: [
            { item_type: 'GUIDE', text: 'Structural density is light. Content leads, structure follows.' },
            { item_type: 'PRACTICE', text: 'Add one bracket or aside and reread.' },
            { item_type: 'SCENARIO', text: 'How might this read in a longer piece?' },
            { item_type: 'COMPARE', text: 'Notice what changes when density increases.' },
          ]},
        ],
      },
    };
  },
};

// =============================================================================
// Styles
// =============================================================================

const styles = {
  // CSS Custom Properties
  vars: `
    :root {
      --color-ink: #1a1a1a;
      --color-paper: #faf8f5;
      --color-cream: #f5f0e8;
      --color-sepia: #d4c4a8;
      --color-rust: #8b4513;
      --color-sage: #5d6d5e;
      --color-muted: #6b6b6b;
      --color-accent: #2d4a3e;
      
      --font-display: 'Playfair Display', Georgia, serif;
      --font-body: 'Source Serif Pro', Georgia, serif;
      --font-mono: 'IBM Plex Mono', 'Courier New', monospace;
      
      --shadow-soft: 0 2px 8px rgba(0,0,0,0.06);
      --shadow-card: 0 4px 20px rgba(0,0,0,0.08);
      --shadow-elevated: 0 8px 32px rgba(0,0,0,0.12);
      
      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 16px;
      
      --transition-fast: 150ms ease;
      --transition-base: 250ms ease;
      --transition-slow: 400ms ease;
    }
  `,

  global: `
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Source+Serif+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    html {
      font-size: 18px;
      scroll-behavior: smooth;
    }
    
    body {
      font-family: var(--font-body);
      background: var(--color-paper);
      color: var(--color-ink);
      line-height: 1.7;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }
    
    ::selection {
      background: var(--color-sepia);
      color: var(--color-ink);
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    
    .fade-in {
      animation: fadeIn 0.5s ease forwards;
    }
    
    .slide-in {
      animation: slideIn 0.4s ease forwards;
    }
  `,

  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '2rem',
    minHeight: '100vh',
  },

  header: {
    textAlign: 'center',
    marginBottom: '3rem',
    paddingBottom: '2rem',
    borderBottom: '1px solid var(--color-sepia)',
  },

  title: {
    fontFamily: 'var(--font-display)',
    fontSize: '2.5rem',
    fontWeight: '500',
    letterSpacing: '-0.02em',
    marginBottom: '0.5rem',
    color: 'var(--color-ink)',
  },

  subtitle: {
    fontFamily: 'var(--font-body)',
    fontSize: '1.1rem',
    color: 'var(--color-muted)',
    fontWeight: '300',
    fontStyle: 'italic',
  },

  card: {
    background: 'white',
    borderRadius: 'var(--radius-md)',
    padding: '2rem',
    boxShadow: 'var(--shadow-card)',
    marginBottom: '1.5rem',
  },

  button: {
    fontFamily: 'var(--font-body)',
    fontSize: '1rem',
    padding: '0.875rem 2rem',
    borderRadius: 'var(--radius-sm)',
    border: 'none',
    cursor: 'pointer',
    transition: 'all var(--transition-base)',
    fontWeight: '500',
  },

  buttonPrimary: {
    background: 'var(--color-accent)',
    color: 'white',
  },

  buttonSecondary: {
    background: 'transparent',
    color: 'var(--color-accent)',
    border: '1px solid var(--color-accent)',
  },

  textarea: {
    width: '100%',
    minHeight: '150px',
    padding: '1rem',
    fontFamily: 'var(--font-body)',
    fontSize: '1rem',
    lineHeight: '1.8',
    border: '1px solid var(--color-sepia)',
    borderRadius: 'var(--radius-sm)',
    resize: 'vertical',
    transition: 'border-color var(--transition-fast)',
    background: 'var(--color-paper)',
  },

  label: {
    display: 'block',
    fontFamily: 'var(--font-mono)',
    fontSize: '0.75rem',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    color: 'var(--color-muted)',
    marginBottom: '0.5rem',
  },

  progress: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1.5rem',
  },

  progressDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    background: 'var(--color-sepia)',
    transition: 'all var(--transition-base)',
  },

  progressDotActive: {
    background: 'var(--color-accent)',
    transform: 'scale(1.2)',
  },

  progressDotComplete: {
    background: 'var(--color-sage)',
  },
};

// =============================================================================
// Components
// =============================================================================

// Style injector
const StyleInjector = () => {
  useEffect(() => {
    const styleEl = document.createElement('style');
    styleEl.textContent = styles.vars + styles.global;
    document.head.appendChild(styleEl);
    return () => styleEl.remove();
  }, []);
  return null;
};

// Progress indicator
const ProgressIndicator = ({ current, total }) => (
  <div style={styles.progress}>
    {Array.from({ length: total }, (_, i) => (
      <div
        key={i}
        style={{
          ...styles.progressDot,
          ...(i < current ? styles.progressDotComplete : {}),
          ...(i === current ? styles.progressDotActive : {}),
        }}
      />
    ))}
    <span style={{ marginLeft: '0.5rem', fontSize: '0.875rem', color: 'var(--color-muted)' }}>
      {current} of {total}
    </span>
  </div>
);

// Welcome Screen
const WelcomeScreen = ({ onStart, onQuickStart }) => (
  <div className="fade-in" style={{ textAlign: 'center', padding: '2rem 0' }}>
    <div style={{ marginBottom: '3rem' }}>
      <p style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto 2rem', lineHeight: '1.8' }}>
        LNCP examines the <em>structure</em> of your writing—not what you say, 
        but how your sentences are built. Through a brief writing exercise, 
        we'll map your structural patterns and offer reflection prompts.
      </p>
      <p style={{ color: 'var(--color-muted)', fontSize: '0.95rem' }}>
        You'll write three groups of sentences. Each takes about a minute.
      </p>
    </div>
    
    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
      <button
        onClick={() => onStart('STORY')}
        style={{ ...styles.button, ...styles.buttonPrimary }}
        onMouseOver={e => e.target.style.transform = 'translateY(-2px)'}
        onMouseOut={e => e.target.style.transform = 'translateY(0)'}
      >
        Begin with Story Prompts
      </button>
      <button
        onClick={() => onStart('LAB')}
        style={{ ...styles.button, ...styles.buttonSecondary }}
        onMouseOver={e => e.target.style.opacity = '0.8'}
        onMouseOut={e => e.target.style.opacity = '1'}
      >
        Begin with Lab Prompts
      </button>
    </div>
    
    <div style={{ marginTop: '2rem' }}>
      <button
        onClick={onQuickStart}
        style={{ 
          ...styles.button, 
          background: 'transparent', 
          color: 'var(--color-muted)',
          fontSize: '0.875rem',
          textDecoration: 'underline',
          padding: '0.5rem 1rem',
        }}
      >
        or paste your own text for quick analysis →
      </button>
    </div>
  </div>
);

// Writing Prompt Card
const WritingPrompt = ({ prompt, onSubmit, groupNumber, isLoading }) => {
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    // Split into sentences (simple split on . ! ?)
    const sentences = text
      .split(/(?<=[.!?])\s+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);

    if (sentences.length < 2) {
      setError('Please write at least 2 sentences.');
      return;
    }
    if (sentences.length > 3) {
      setError('Please write no more than 3 sentences.');
      return;
    }

    setError('');
    onSubmit(sentences);
    setText('');
  };

  return (
    <div className="fade-in" style={styles.card}>
      <ProgressIndicator current={groupNumber - 1} total={3} />
      
      <div style={{ marginBottom: '1.5rem' }}>
        <span style={styles.label}>Prompt {groupNumber}</span>
        <p style={{ 
          fontFamily: 'var(--font-display)', 
          fontSize: '1.4rem', 
          fontStyle: 'italic',
          lineHeight: '1.6',
          color: 'var(--color-ink)',
        }}>
          "{prompt?.text || 'Write 2–3 sentences...'}"
        </p>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="Write your sentences here..."
          style={{
            ...styles.textarea,
            borderColor: error ? 'var(--color-rust)' : 'var(--color-sepia)',
          }}
          disabled={isLoading}
        />
        {error && (
          <p style={{ color: 'var(--color-rust)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            {error}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '0.875rem', color: 'var(--color-muted)' }}>
          Write 2–3 complete sentences
        </span>
        <button
          onClick={handleSubmit}
          disabled={isLoading || text.trim().length < 10}
          style={{
            ...styles.button,
            ...styles.buttonPrimary,
            opacity: isLoading || text.trim().length < 10 ? 0.5 : 1,
            cursor: isLoading || text.trim().length < 10 ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Submitting...' : 'Submit'}
        </button>
      </div>
    </div>
  );
};

// Quick Analyze Screen
const QuickAnalyzeScreen = ({ onAnalyze, onBack, isLoading }) => {
  const [text, setText] = useState('');
  const [error, setError] = useState('');

  const handleAnalyze = () => {
    const sentences = text
      .split(/(?<=[.!?])\s+/)
      .map(s => s.trim())
      .filter(s => s.length > 0);

    if (sentences.length < 2) {
      setError('Please enter at least 2 sentences.');
      return;
    }

    setError('');
    onAnalyze(sentences);
  };

  return (
    <div className="fade-in" style={styles.card}>
      <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', marginBottom: '1rem' }}>
        Quick Analysis
      </h2>
      <p style={{ color: 'var(--color-muted)', marginBottom: '1.5rem' }}>
        Paste or type your text below. We'll analyze its structural patterns.
      </p>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Paste your writing here... (at least 2 sentences)"
        style={{
          ...styles.textarea,
          minHeight: '200px',
          borderColor: error ? 'var(--color-rust)' : 'var(--color-sepia)',
        }}
        disabled={isLoading}
      />
      {error && (
        <p style={{ color: 'var(--color-rust)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          {error}
        </p>
      )}

      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <button
          onClick={onBack}
          style={{ ...styles.button, ...styles.buttonSecondary }}
        >
          ← Back
        </button>
        <button
          onClick={handleAnalyze}
          disabled={isLoading || text.trim().length < 20}
          style={{
            ...styles.button,
            ...styles.buttonPrimary,
            opacity: isLoading || text.trim().length < 20 ? 0.5 : 1,
          }}
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>
    </div>
  );
};

// Gate Complete Screen
const GateCompleteScreen = ({ onAnalyze, isLoading }) => (
  <div className="fade-in" style={{ ...styles.card, textAlign: 'center', padding: '3rem 2rem' }}>
    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✦</div>
    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', marginBottom: '1rem' }}>
      Writing Complete
    </h2>
    <p style={{ color: 'var(--color-muted)', marginBottom: '2rem', maxWidth: '400px', margin: '0 auto 2rem' }}>
      You've submitted all three groups. We're ready to analyze the structural 
      patterns in your writing.
    </p>
    <button
      onClick={onAnalyze}
      disabled={isLoading}
      style={{
        ...styles.button,
        ...styles.buttonPrimary,
        fontSize: '1.1rem',
        padding: '1rem 2.5rem',
      }}
    >
      {isLoading ? 'Analyzing...' : 'View My Analysis'}
    </button>
  </div>
);

// Results Display
const ResultsScreen = ({ results, onReset }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [activePhase4, setActivePhase4] = useState('prompting');

  const phase2Outputs = results?.phase2?.outputs || {};
  const phase3Syntheses = results?.phase3?.syntheses || [];
  const phase4aPrompts = results?.phase4a?.prompt_sets || [];
  const phase4bGuidance = results?.phase4b?.guidance_sets || [];

  return (
    <div className="fade-in">
      {/* Navigation Tabs */}
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem', 
        marginBottom: '2rem',
        borderBottom: '1px solid var(--color-sepia)',
        paddingBottom: '1rem',
      }}>
        {['overview', 'synthesis', 'reflect'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...styles.button,
              padding: '0.5rem 1rem',
              background: activeTab === tab ? 'var(--color-accent)' : 'transparent',
              color: activeTab === tab ? 'white' : 'var(--color-muted)',
              fontSize: '0.875rem',
            }}
          >
            {tab === 'overview' ? 'Overview' : tab === 'synthesis' ? 'Synthesis' : 'Reflect'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          <div style={{ marginBottom: '2rem' }}>
            <span style={styles.label}>Presentation Mode</span>
            <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem' }}>
              {results?.phase2?.presentation_mode === 'DESCRIPTIVE' 
                ? 'Descriptive — We describe what appears in this sample.'
                : 'Reflective — Patterns are emerging for deeper reflection.'}
            </p>
          </div>

          <div style={{ display: 'grid', gap: '1rem' }}>
            {Object.values(phase2Outputs).slice(0, 6).map((output, i) => (
              <div 
                key={i} 
                className="slide-in"
                style={{ 
                  ...styles.card, 
                  padding: '1.5rem',
                  animationDelay: `${i * 0.1}s`,
                  opacity: 0,
                  animation: `slideIn 0.4s ease ${i * 0.1}s forwards`,
                }}
              >
                <h3 style={{ 
                  fontFamily: 'var(--font-display)', 
                  fontSize: '1.1rem',
                  marginBottom: '0.5rem',
                  color: 'var(--color-accent)',
                }}>
                  {output.name_user_facing}
                </h3>
                <p style={{ marginBottom: '0.75rem' }}>{output.explanation}</p>
                <div style={{ 
                  display: 'flex', 
                  gap: '1rem', 
                  fontSize: '0.875rem',
                  color: 'var(--color-muted)',
                  fontStyle: 'italic',
                }}>
                  {output.example_insights?.map((insight, j) => (
                    <span key={j}>• {insight}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Synthesis Tab */}
      {activeTab === 'synthesis' && (
        <div>
          <p style={{ marginBottom: '2rem', color: 'var(--color-muted)' }}>
            These syntheses bring your structural patterns into relation using 
            semiotic lenses. Each one reveals a different aspect of how your 
            writing works.
          </p>

          {phase3Syntheses.map((syn, i) => (
            <div 
              key={syn.synthesis_id}
              className="fade-in"
              style={{ 
                ...styles.card,
                borderLeft: '4px solid var(--color-sage)',
                animationDelay: `${i * 0.15}s`,
              }}
            >
              <span style={{
                ...styles.label,
                color: 'var(--color-sage)',
              }}>
                {syn.semiotic_lens.replace(/_/g, ' ')}
              </span>
              <p style={{ 
                fontFamily: 'var(--font-display)', 
                fontSize: '1.15rem',
                lineHeight: '1.8',
                fontStyle: 'italic',
              }}>
                {syn.synthesis_text}
              </p>
              <div style={{ 
                marginTop: '1rem', 
                fontSize: '0.8rem', 
                color: 'var(--color-muted)',
              }}>
                Related: {syn.related_outputs?.join(', ')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Reflect Tab */}
      {activeTab === 'reflect' && (
        <div>
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            marginBottom: '2rem',
          }}>
            <button
              onClick={() => setActivePhase4('prompting')}
              style={{
                ...styles.button,
                ...styles.buttonSecondary,
                background: activePhase4 === 'prompting' ? 'var(--color-cream)' : 'transparent',
              }}
            >
              Prompting Mode
            </button>
            <button
              onClick={() => setActivePhase4('guidance')}
              style={{
                ...styles.button,
                ...styles.buttonSecondary,
                background: activePhase4 === 'guidance' ? 'var(--color-cream)' : 'transparent',
              }}
            >
              Guidance Mode
            </button>
          </div>

          {activePhase4 === 'prompting' && phase4aPrompts.map((set, i) => (
            <div key={set.prompt_set_id} style={{ ...styles.card, marginBottom: '1.5rem' }}>
              <span style={{ ...styles.label, color: 'var(--color-sage)' }}>
                {set.semiotic_lens?.replace(/_/g, ' ')}
              </span>
              <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
                {set.prompts?.map((prompt, j) => (
                  <div key={j} style={{ 
                    padding: '1rem',
                    background: 'var(--color-paper)',
                    borderRadius: 'var(--radius-sm)',
                  }}>
                    <span style={{ 
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.7rem',
                      color: 'var(--color-rust)',
                      textTransform: 'uppercase',
                    }}>
                      {prompt.prompt_type}
                    </span>
                    <p style={{ marginTop: '0.25rem' }}>{prompt.prompt_text}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {activePhase4 === 'guidance' && phase4bGuidance.map((set, i) => (
            <div key={set.guidance_set_id} style={{ ...styles.card, marginBottom: '1.5rem' }}>
              <span style={{ ...styles.label, color: 'var(--color-sage)' }}>
                {set.semiotic_lens?.replace(/_/g, ' ')}
              </span>
              <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
                {set.items?.map((item, j) => (
                  <div key={j} style={{ 
                    padding: '1rem',
                    background: 'var(--color-paper)',
                    borderRadius: 'var(--radius-sm)',
                  }}>
                    <span style={{ 
                      fontFamily: 'var(--font-mono)',
                      fontSize: '0.7rem',
                      color: 'var(--color-accent)',
                      textTransform: 'uppercase',
                    }}>
                      {item.item_type}
                    </span>
                    <p style={{ marginTop: '0.25rem' }}>{item.text}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Reset Button */}
      <div style={{ textAlign: 'center', marginTop: '3rem', paddingTop: '2rem', borderTop: '1px solid var(--color-sepia)' }}>
        <button
          onClick={onReset}
          style={{ ...styles.button, ...styles.buttonSecondary }}
        >
          Start Over
        </button>
      </div>
    </div>
  );
};

// =============================================================================
// Main App
// =============================================================================

export default function LNCPApp() {
  const [screen, setScreen] = useState('welcome'); // welcome, game, quick, complete, results
  const [sessionId, setSessionId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useMock, setUseMock] = useState(false);

  // Choose API based on availability
  const getApi = useCallback(() => useMock ? mockApi : api, [useMock]);

  // Initialize game
  const handleStartGame = async (mode) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getApi().initGame(mode);
      setSessionId(data.session_id);
      setGameState(data);
      setScreen('game');
    } catch (err) {
      // Fall back to mock if API unavailable
      console.warn('API unavailable, using mock mode:', err);
      setUseMock(true);
      const data = await mockApi.initGame(mode);
      setSessionId(data.session_id);
      setGameState(data);
      setScreen('game');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit sentence group
  const handleSubmitGroup = async (sentences) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getApi().submitGroup(sessionId, sentences);
      setGameState(prev => ({
        ...prev,
        ...data,
      }));
      if (data.gate?.is_complete) {
        setScreen('complete');
      }
    } catch (err) {
      setError('Failed to submit. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Run analysis
  const handleRunAnalysis = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getApi().runAnalysis(sessionId);
      setResults(data);
      setScreen('results');
    } catch (err) {
      setError('Analysis failed. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Quick analyze
  const handleQuickAnalyze = async (sentences) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getApi().quickAnalyze(sentences);
      setResults(data);
      setScreen('results');
    } catch (err) {
      // Fall back to mock
      console.warn('API unavailable, using mock:', err);
      const data = await mockApi.quickAnalyze(sentences);
      setResults(data);
      setScreen('results');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset
  const handleReset = () => {
    setScreen('welcome');
    setSessionId(null);
    setGameState(null);
    setResults(null);
    setError(null);
  };

  return (
    <>
      <StyleInjector />
      <div style={styles.container}>
        <header style={styles.header}>
          <h1 style={styles.title}>LNCP</h1>
          <p style={styles.subtitle}>Structural Writing Analysis</p>
        </header>

        {error && (
          <div style={{ 
            ...styles.card, 
            background: '#fef2f2', 
            borderLeft: '4px solid var(--color-rust)',
            marginBottom: '1.5rem',
          }}>
            <p style={{ color: 'var(--color-rust)' }}>{error}</p>
          </div>
        )}

        {screen === 'welcome' && (
          <WelcomeScreen 
            onStart={handleStartGame} 
            onQuickStart={() => setScreen('quick')}
          />
        )}

        {screen === 'game' && gameState && (
          <WritingPrompt
            prompt={gameState.current_prompt}
            onSubmit={handleSubmitGroup}
            groupNumber={(gameState.gate?.completed || 0) + 1}
            isLoading={isLoading}
          />
        )}

        {screen === 'quick' && (
          <QuickAnalyzeScreen
            onAnalyze={handleQuickAnalyze}
            onBack={() => setScreen('welcome')}
            isLoading={isLoading}
          />
        )}

        {screen === 'complete' && (
          <GateCompleteScreen
            onAnalyze={handleRunAnalysis}
            isLoading={isLoading}
          />
        )}

        {screen === 'results' && results && (
          <ResultsScreen
            results={results}
            onReset={handleReset}
          />
        )}

        {useMock && (
          <div style={{ 
            textAlign: 'center', 
            marginTop: '2rem',
            fontSize: '0.75rem',
            color: 'var(--color-muted)',
          }}>
            Demo mode — API unavailable
          </div>
        )}
      </div>
    </>
  );
}
