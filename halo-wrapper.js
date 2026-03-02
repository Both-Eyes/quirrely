/**
 * HALO WRAPPER — Frontend Detection (Layer 1)
 * ============================================
 * Hate, Abuse, Language, Outcomes
 * 
 * Fast client-side detection for immediate user feedback.
 * This is Layer 1 only — backend performs deeper analysis.
 * 
 * Version: 1.0.0
 * Date: February 10, 2026
 */

const HALO = (function() {
  'use strict';

  // ═══════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════
  
  const CONFIG = {
    // Tier thresholds
    T1_THRESHOLD: 1,      // 1 violation = warning
    T2_THRESHOLD: 3,      // 3 violations in session = caution
    T3_IMMEDIATE: true,   // Severe content = immediate block
    
    // Session tracking
    SESSION_KEY: 'halo_session',
    VIOLATIONS_KEY: 'halo_violations',
    
    // Rate limiting (Outcomes)
    MAX_SUBMISSIONS_PER_HOUR: 5,
    MIN_TYPING_TIME_MS: 3000,  // Minimum time to type sample (bot detection)
    
    // Cooldown
    T2_COOLDOWN_MS: 3600000,  // 1 hour
  };

  // ═══════════════════════════════════════════════════════════════
  // BLOCKLISTS (Layer 1 — Fast Pattern Matching)
  // ═══════════════════════════════════════════════════════════════
  
  // Severe (T3 immediate) — Slurs, extreme hate
  const BLOCKLIST_SEVERE = [
    // Racial slurs (obfuscated for code review)
    /\bn[i1]gg[e3]r/i,
    /\bk[i1]ke/i,
    /\bsp[i1]c/i,
    /\bch[i1]nk/i,
    /\bw[e3]tb[a4]ck/i,
    /\bg[o0][o0]k/i,
    
    // Extreme hate
    /\bh[i1]tl[e3]r\s*(was|did)\s*(right|nothing\s*wrong)/i,
    /\b(kill|murder|exterminate)\s*(all|every)\s*(jews?|blacks?|muslims?|gays?)/i,
    /\bgas\s*the\s*(jews?|kikes?)/i,
    /\bwhite\s*(power|supremacy)/i,
    /\b(race|holy)\s*war/i,
    
    // Direct threats
    /\bi('ll|m\s*going\s*to)\s*(kill|murder|shoot|stab)\s*(you|them)/i,
    /\byou('re|\s*are)\s*(going\s*to\s*)?(die|dead)/i,
    /\b(bomb|shoot\s*up)\s*(the|this)\s*(school|office|building)/i,
  ];
  
  // Moderate (T2) — Harassment, targeted abuse
  const BLOCKLIST_MODERATE = [
    // Harassment
    /\bkill\s*yourself/i,
    /\bkys\b/i,
    /\bgo\s*die/i,
    /\byou('re|\s*are)\s*(worthless|garbage|trash|pathetic)/i,
    /\bnobody\s*(loves|cares\s*about)\s*you/i,
    
    // Gendered slurs
    /\bc[u\*]nt/i,
    /\bwh[o0]re/i,
    /\bsl[u\*]t/i,
    /\bbitch/i,
    
    // Homophobic
    /\bf[a4]gg?[o0]t/i,
    /\bdyke/i,
    /\btr[a4]nny/i,
    
    // Ableist
    /\br[e3]t[a4]rd/i,
    
    // Doxxing indicators
    /\b(here'?s?|posting)\s*(your|their)\s*(address|phone|email)/i,
  ];
  
  // Mild (T1) — Profanity, crude language
  const BLOCKLIST_MILD = [
    /\bf+u+c+k+/i,
    /\bs+h+i+t+/i,
    /\ba+s+s+h+o+l+e+/i,
    /\bd+a+m+n+/i,
    /\bh+e+l+l+\b/i,
    /\bcrap/i,
    /\bpiss/i,
    /\bcock\b/i,
    /\bdick\b/i,
    /\bboobs?\b/i,
  ];

  // ═══════════════════════════════════════════════════════════════
  // OUTCOMES DETECTION (Gaming, Spam, Bots)
  // ═══════════════════════════════════════════════════════════════
  
  const OUTCOMES_PATTERNS = {
    // Spam indicators
    duplicateContent: new Set(),  // Track content hashes
    submissionTimes: [],          // Track submission velocity
    
    // Bot indicators
    typingStartTime: null,
    
    // Gaming indicators
    suspiciousPatterns: [
      /(.)\1{10,}/,               // Same character repeated 10+ times
      /^[a-z]{100,}$/i,           // Just letters, no spaces, very long
      /^(.{1,5})\1{5,}$/,         // Short pattern repeated many times
      /test\s*test\s*test/i,      // Obvious test content
      /asdf|qwerty|lorem\s*ipsum/i,
    ]
  };

  // ═══════════════════════════════════════════════════════════════
  // CORE DETECTION FUNCTIONS
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Check text against blocklists
   * @param {string} text - Text to analyze
   * @returns {Object} { tier: 'T1'|'T2'|'T3'|null, category: 'H'|'A'|'L', matches: [] }
   */
  function checkBlocklists(text) {
    if (!text || typeof text !== 'string') {
      return { tier: null, category: null, matches: [] };
    }
    
    const normalizedText = text.toLowerCase().trim();
    
    // Check severe first (T3)
    for (const pattern of BLOCKLIST_SEVERE) {
      const match = normalizedText.match(pattern);
      if (match) {
        return {
          tier: 'T3',
          category: 'H', // Hate (severe is always hate-related)
          matches: [match[0]],
          message: 'Content violates community guidelines and cannot be submitted.'
        };
      }
    }
    
    // Check moderate (T2)
    for (const pattern of BLOCKLIST_MODERATE) {
      const match = normalizedText.match(pattern);
      if (match) {
        return {
          tier: 'T2',
          category: 'A', // Abuse
          matches: [match[0]],
          message: 'This content may be harmful. Please revise before submitting.'
        };
      }
    }
    
    // Check mild (T1)
    const mildMatches = [];
    for (const pattern of BLOCKLIST_MILD) {
      const match = normalizedText.match(pattern);
      if (match) {
        mildMatches.push(match[0]);
      }
    }
    
    if (mildMatches.length > 0) {
      return {
        tier: 'T1',
        category: 'L', // Language
        matches: mildMatches,
        message: 'Your text contains strong language. Consider revising for a wider audience.'
      };
    }
    
    return { tier: null, category: null, matches: [] };
  }
  
  /**
   * Check for Outcomes violations (gaming, spam, bots)
   * @param {string} text - Text to analyze
   * @param {Object} context - Additional context (timing, etc.)
   * @returns {Object} { tier: 'T1'|'T2'|null, category: 'O', reason: string }
   */
  function checkOutcomes(text, context = {}) {
    if (!text || typeof text !== 'string') {
      return { tier: null, category: null };
    }
    
    // Check for suspicious patterns (gaming)
    for (const pattern of OUTCOMES_PATTERNS.suspiciousPatterns) {
      if (pattern.test(text)) {
        return {
          tier: 'T1',
          category: 'O',
          reason: 'suspicious_pattern',
          message: 'Please provide genuine writing for accurate analysis.'
        };
      }
    }
    
    // Check for duplicate content
    const contentHash = simpleHash(text);
    if (OUTCOMES_PATTERNS.duplicateContent.has(contentHash)) {
      return {
        tier: 'T1',
        category: 'O',
        reason: 'duplicate',
        message: 'This content has already been submitted.'
      };
    }
    
    // Check typing speed (bot detection)
    if (context.typingDuration && context.typingDuration < CONFIG.MIN_TYPING_TIME_MS) {
      const wordsPerMinute = (text.split(/\s+/).length / context.typingDuration) * 60000;
      if (wordsPerMinute > 300) { // Impossibly fast
        return {
          tier: 'T2',
          category: 'O',
          reason: 'bot_suspected',
          message: 'Unusual activity detected. Please try again.'
        };
      }
    }
    
    // Check submission velocity
    const now = Date.now();
    const recentSubmissions = OUTCOMES_PATTERNS.submissionTimes.filter(
      t => now - t < 3600000 // Last hour
    );
    
    if (recentSubmissions.length >= CONFIG.MAX_SUBMISSIONS_PER_HOUR) {
      return {
        tier: 'T2',
        category: 'O',
        reason: 'rate_limit',
        message: 'Too many submissions. Please wait before trying again.'
      };
    }
    
    return { tier: null, category: null };
  }
  
  /**
   * Simple string hash for duplicate detection
   */
  function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(36);
  }

  // ═══════════════════════════════════════════════════════════════
  // SESSION MANAGEMENT
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Get or create session
   */
  function getSession() {
    let session = null;
    try {
      session = JSON.parse(localStorage.getItem(CONFIG.SESSION_KEY));
    } catch (e) {}
    
    if (!session || Date.now() - session.created > 86400000) { // 24hr expiry
      session = {
        id: 'ses_' + Math.random().toString(36).substr(2, 9),
        created: Date.now(),
        violations: [],
        t1Count: 0,
        t2Count: 0,
        cooldownUntil: null
      };
      saveSession(session);
    }
    
    return session;
  }
  
  /**
   * Save session
   */
  function saveSession(session) {
    try {
      localStorage.setItem(CONFIG.SESSION_KEY, JSON.stringify(session));
    } catch (e) {}
  }
  
  /**
   * Record violation
   */
  function recordViolation(tier, category, content) {
    const session = getSession();
    
    const violation = {
      tier,
      category,
      timestamp: Date.now(),
      contentHash: simpleHash(content || '')
    };
    
    session.violations.push(violation);
    
    if (tier === 'T1') session.t1Count++;
    if (tier === 'T2') session.t2Count++;
    
    // Escalation check
    if (session.t1Count >= CONFIG.T2_THRESHOLD) {
      session.cooldownUntil = Date.now() + CONFIG.T2_COOLDOWN_MS;
    }
    
    saveSession(session);
    
    return session;
  }
  
  /**
   * Check if user is in cooldown
   */
  function isInCooldown() {
    const session = getSession();
    if (session.cooldownUntil && Date.now() < session.cooldownUntil) {
      return {
        inCooldown: true,
        remainingMs: session.cooldownUntil - Date.now(),
        message: 'You are in a cooldown period. Please wait before submitting.'
      };
    }
    return { inCooldown: false };
  }

  // ═══════════════════════════════════════════════════════════════
  // MAIN API
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Analyze text for HALO violations
   * @param {string} text - Text to analyze
   * @param {Object} options - Optional context
   * @returns {Object} Analysis result
   */
  function analyze(text, options = {}) {
    // Check cooldown first
    const cooldown = isInCooldown();
    if (cooldown.inCooldown) {
      return {
        pass: false,
        tier: 'T2',
        category: 'O',
        action: 'COOLDOWN',
        message: cooldown.message,
        remainingMs: cooldown.remainingMs
      };
    }
    
    // Check HAL (Hate, Abuse, Language)
    const halResult = checkBlocklists(text);
    
    if (halResult.tier === 'T3') {
      recordViolation('T3', halResult.category, text);
      return {
        pass: false,
        tier: 'T3',
        category: halResult.category,
        action: 'BLOCK',
        message: halResult.message,
        matches: halResult.matches
      };
    }
    
    if (halResult.tier === 'T2') {
      const session = recordViolation('T2', halResult.category, text);
      return {
        pass: false,
        tier: 'T2',
        category: halResult.category,
        action: session.cooldownUntil ? 'COOLDOWN' : 'CAUTION',
        message: halResult.message,
        matches: halResult.matches
      };
    }
    
    // Check Outcomes
    const outcomesResult = checkOutcomes(text, options);
    
    if (outcomesResult.tier) {
      const session = recordViolation(outcomesResult.tier, 'O', text);
      return {
        pass: false,
        tier: outcomesResult.tier,
        category: 'O',
        action: outcomesResult.tier === 'T2' ? 'CAUTION' : 'WARN',
        message: outcomesResult.message,
        reason: outcomesResult.reason
      };
    }
    
    // T1 Language check (warning but allows continue)
    if (halResult.tier === 'T1') {
      recordViolation('T1', 'L', text);
      return {
        pass: true,  // Allow with warning
        tier: 'T1',
        category: 'L',
        action: 'WARN',
        message: halResult.message,
        matches: halResult.matches
      };
    }
    
    // All clear
    return {
      pass: true,
      tier: null,
      category: null,
      action: 'ALLOW'
    };
  }
  
  /**
   * Record successful submission (for rate limiting)
   */
  function recordSubmission(text) {
    OUTCOMES_PATTERNS.submissionTimes.push(Date.now());
    OUTCOMES_PATTERNS.duplicateContent.add(simpleHash(text));
    
    // Cleanup old entries
    const cutoff = Date.now() - 3600000;
    OUTCOMES_PATTERNS.submissionTimes = OUTCOMES_PATTERNS.submissionTimes.filter(t => t > cutoff);
  }
  
  /**
   * Start typing timer (for bot detection)
   */
  function startTyping() {
    OUTCOMES_PATTERNS.typingStartTime = Date.now();
  }
  
  /**
   * Get typing duration
   */
  function getTypingDuration() {
    if (!OUTCOMES_PATTERNS.typingStartTime) return null;
    return Date.now() - OUTCOMES_PATTERNS.typingStartTime;
  }
  
  /**
   * Get session stats (for admin/debugging)
   */
  function getStats() {
    const session = getSession();
    return {
      sessionId: session.id,
      t1Count: session.t1Count,
      t2Count: session.t2Count,
      totalViolations: session.violations.length,
      inCooldown: isInCooldown().inCooldown,
      cooldownRemaining: isInCooldown().remainingMs || 0
    };
  }
  
  /**
   * Reset session (for testing)
   */
  function reset() {
    localStorage.removeItem(CONFIG.SESSION_KEY);
    OUTCOMES_PATTERNS.duplicateContent.clear();
    OUTCOMES_PATTERNS.submissionTimes = [];
  }

  // ═══════════════════════════════════════════════════════════════
  // UI HELPERS
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Show HALO warning toast
   */
  function showWarning(result) {
    // Remove existing
    const existing = document.getElementById('halo-warning');
    if (existing) existing.remove();
    
    const colors = {
      T1: { bg: '#FFF3CD', border: '#FFECB5', text: '#856404' },
      T2: { bg: '#F8D7DA', border: '#F5C6CB', text: '#721C24' },
      T3: { bg: '#721C24', border: '#721C24', text: '#FFFFFF' }
    };
    
    const color = colors[result.tier] || colors.T1;
    
    const toast = document.createElement('div');
    toast.id = 'halo-warning';
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: ${color.bg};
      border: 1px solid ${color.border};
      color: ${color.text};
      padding: 1rem 1.5rem;
      border-radius: 8px;
      font-family: system-ui, sans-serif;
      font-size: 0.95rem;
      z-index: 10000;
      max-width: 400px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: haloSlideIn 0.3s ease;
    `;
    
    toast.innerHTML = `
      <strong>${result.tier === 'T3' ? '⛔' : result.tier === 'T2' ? '⚠️' : '💡'} ${
        result.tier === 'T3' ? 'Blocked' : result.tier === 'T2' ? 'Caution' : 'Notice'
      }</strong><br>
      ${result.message}
      ${result.tier !== 'T3' ? '<br><small style="opacity:0.7">Click to dismiss</small>' : ''}
    `;
    
    if (result.tier !== 'T3') {
      toast.style.cursor = 'pointer';
      toast.onclick = () => toast.remove();
      setTimeout(() => toast.remove(), 8000);
    }
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes haloSlideIn {
        from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
      }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(toast);
  }
  
  /**
   * Show block modal (T3)
   */
  function showBlockModal() {
    const modal = document.createElement('div');
    modal.id = 'halo-block-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.9);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10001;
      font-family: system-ui, sans-serif;
    `;
    
    modal.innerHTML = `
      <div style="background: #1a1a1a; color: white; padding: 3rem; border-radius: 16px; text-align: center; max-width: 400px;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">⛔</div>
        <h2 style="margin: 0 0 1rem;">Session Terminated</h2>
        <p style="color: #999; margin: 0 0 2rem;">
          Your session has been ended due to a serious violation of our community guidelines.
          If you believe this was an error, please contact support.
        </p>
        <a href="mailto:support@quirrely.com" style="color: #FF6B6B;">Contact Support</a>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Disable page interaction
    document.body.style.overflow = 'hidden';
  }

  // ═══════════════════════════════════════════════════════════════
  // PUBLIC API
  // ═══════════════════════════════════════════════════════════════
  
  return {
    analyze,
    recordSubmission,
    startTyping,
    getTypingDuration,
    getStats,
    reset,
    showWarning,
    showBlockModal,
    isInCooldown,
    
    // Constants for external use
    TIERS: { T1: 'T1', T2: 'T2', T3: 'T3' },
    CATEGORIES: { H: 'Hate', A: 'Abuse', L: 'Language', O: 'Outcomes' }
  };
  
})();

// Export for Node.js (testing)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HALO;
}
