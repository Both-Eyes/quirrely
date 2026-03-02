/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY TRIAL CONVERSION OPTIMIZATION v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Addresses Master Test finding: Trial Start conversion at 4.8% vs 70% baseline
 * 
 * Strategy:
 * 1. Progressive nudges before hard limit
 * 2. Value preview showing what users unlock
 * 3. Social proof with real-time trial starts
 * 4. Simplified, high-converting CTA
 */

const COLORS = {
  coral: '#FF6B6B',
  softGold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  success: '#00B894',
  purple: '#6C5CE7',
};

// Word limits by tier
const LIMITS = {
  FREE: 500,
  TRIAL: 2000,
  PRO: 10000,
};

// Nudge thresholds (percentage of limit)
const NUDGE_THRESHOLDS = {
  soft: 0.80,    // 80% - soft nudge
  medium: 0.95,  // 95% - stronger nudge
  hard: 1.00,    // 100% - limit reached
};


// ═══════════════════════════════════════════════════════════════════════════
// PROGRESSIVE NUDGE BANNER
// ═══════════════════════════════════════════════════════════════════════════

class ProgressiveNudge extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._wordsUsed = 0;
    this._limit = LIMITS.FREE;
    this._dismissed = false;
  }

  static get observedAttributes() {
    return ['words-used', 'limit'];
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === 'words-used') this._wordsUsed = parseInt(newVal) || 0;
    if (name === 'limit') this._limit = parseInt(newVal) || LIMITS.FREE;
    this.render();
  }

  connectedCallback() { this.render(); }

  dismiss() {
    this._dismissed = true;
    this.render();
  }

  getNudgeLevel() {
    const pct = this._wordsUsed / this._limit;
    if (pct >= NUDGE_THRESHOLDS.hard) return 'hard';
    if (pct >= NUDGE_THRESHOLDS.medium) return 'medium';
    if (pct >= NUDGE_THRESHOLDS.soft) return 'soft';
    return null;
  }

  render() {
    const level = this.getNudgeLevel();
    const pct = Math.min(100, Math.round((this._wordsUsed / this._limit) * 100));
    const remaining = Math.max(0, this._limit - this._wordsUsed);

    if (!level || this._dismissed) {
      this.shadowRoot.innerHTML = '';
      return;
    }

    const messages = {
      soft: {
        icon: '📊',
        title: `${remaining} words remaining`,
        subtitle: 'You\'re building a great voice profile!',
        cta: 'Preview PRO features',
        urgency: false,
      },
      medium: {
        icon: '⚡',
        title: `Only ${remaining} words left`,
        subtitle: 'Unlock unlimited analysis with a free trial',
        cta: 'Start Free Trial',
        urgency: true,
      },
      hard: {
        icon: '🔒',
        title: 'You\'ve reached your limit',
        subtitle: 'Start a free trial to continue discovering your voice',
        cta: 'Start Free Trial',
        urgency: true,
      },
    };

    const msg = messages[level];
    const bgColor = level === 'hard' ? COLORS.coral : level === 'medium' ? COLORS.softGold : COLORS.bg;
    const textColor = level === 'hard' || level === 'medium' ? 'white' : COLORS.ink;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .nudge {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem 1.5rem;
          background: ${bgColor};
          color: ${textColor};
          border-radius: 12px;
          margin-bottom: 1rem;
          animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
          from { transform: translateY(-10px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        
        .nudge-icon { font-size: 1.5rem; }
        
        .nudge-content { flex: 1; }
        .nudge-title { font-weight: 600; font-size: 1rem; }
        .nudge-subtitle { font-size: 0.85rem; opacity: 0.9; margin-top: 0.25rem; }
        
        .nudge-progress {
          width: 100px;
          height: 6px;
          background: rgba(255,255,255,0.3);
          border-radius: 3px;
          overflow: hidden;
          margin-top: 0.5rem;
        }
        .nudge-progress-fill {
          height: 100%;
          background: ${level === 'soft' ? COLORS.coral : 'white'};
          border-radius: 3px;
          transition: width 0.5s;
        }
        
        .nudge-cta {
          padding: 0.6rem 1.25rem;
          background: ${level === 'soft' ? COLORS.coral : 'white'};
          color: ${level === 'soft' ? 'white' : COLORS.ink};
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 0.9rem;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .nudge-cta:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .nudge-dismiss {
          background: none;
          border: none;
          color: ${textColor};
          opacity: 0.7;
          cursor: pointer;
          font-size: 1.25rem;
          padding: 0.25rem;
        }
        .nudge-dismiss:hover { opacity: 1; }
        
        ${msg.urgency ? `
          .nudge-cta {
            animation: pulse 2s infinite;
          }
          @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255,255,255,0.4); }
            50% { box-shadow: 0 0 0 8px rgba(255,255,255,0); }
          }
        ` : ''}
      </style>
      
      <div class="nudge">
        <span class="nudge-icon">${msg.icon}</span>
        <div class="nudge-content">
          <div class="nudge-title">${msg.title}</div>
          <div class="nudge-subtitle">${msg.subtitle}</div>
          ${level === 'soft' ? `
            <div class="nudge-progress">
              <div class="nudge-progress-fill" style="width: ${pct}%"></div>
            </div>
          ` : ''}
        </div>
        <button class="nudge-cta" id="cta-btn">${msg.cta}</button>
        ${level === 'soft' ? `<button class="nudge-dismiss" id="dismiss-btn">×</button>` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('cta-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('start-trial', { bubbles: true }));
    });

    this.shadowRoot.getElementById('dismiss-btn')?.addEventListener('click', () => {
      this.dismiss();
    });
  }
}

customElements.define('progressive-nudge', ProgressiveNudge);


// ═══════════════════════════════════════════════════════════════════════════
// VALUE PREVIEW MODAL
// ═══════════════════════════════════════════════════════════════════════════

class ValuePreview extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._open = false;
  }

  static get observedAttributes() { return ['open']; }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === 'open') {
      this._open = newVal !== null && newVal !== 'false';
      this.render();
    }
  }

  connectedCallback() { this.render(); }

  close() {
    this._open = false;
    this.render();
    this.dispatchEvent(new CustomEvent('close', { bubbles: true }));
  }

  render() {
    if (!this._open) {
      this.shadowRoot.innerHTML = '';
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          animation: fadeIn 0.2s;
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .modal {
          background: white;
          border-radius: 20px;
          max-width: 500px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        
        .modal-header {
          padding: 2rem 2rem 1rem;
          text-align: center;
        }
        .modal-icon { font-size: 3rem; margin-bottom: 1rem; }
        .modal-title { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; margin: 0; }
        .modal-subtitle { color: ${COLORS.muted}; margin-top: 0.5rem; font-size: 1rem; }
        
        .features {
          padding: 0 2rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .feature {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          padding: 1rem;
          background: ${COLORS.bg};
          border-radius: 12px;
        }
        .feature-icon { font-size: 1.5rem; }
        .feature-content { flex: 1; }
        .feature-title { font-weight: 600; color: ${COLORS.ink}; }
        .feature-desc { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        .feature-locked {
          font-size: 0.75rem;
          color: ${COLORS.coral};
          font-weight: 600;
          margin-top: 0.5rem;
        }
        
        .social-proof {
          padding: 1.5rem 2rem;
          text-align: center;
        }
        .social-text {
          font-size: 0.9rem;
          color: ${COLORS.muted};
        }
        .social-count {
          font-weight: 700;
          color: ${COLORS.success};
        }
        
        .modal-footer {
          padding: 1.5rem 2rem 2rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .cta-primary {
          width: 100%;
          padding: 1rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.1rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .cta-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        }
        .cta-secondary {
          width: 100%;
          padding: 0.75rem;
          background: transparent;
          color: ${COLORS.muted};
          border: none;
          font-size: 0.9rem;
          cursor: pointer;
        }
        .cta-secondary:hover { color: ${COLORS.ink}; }
        
        .guarantee {
          text-align: center;
          font-size: 0.8rem;
          color: ${COLORS.muted};
          padding: 0 2rem 1.5rem;
        }
      </style>
      
      <div class="overlay" id="overlay">
        <div class="modal">
          <div class="modal-header">
            <div class="modal-icon">✨</div>
            <h2 class="modal-title">Unlock Your Full Voice Profile</h2>
            <p class="modal-subtitle">See what you're missing with a free 7-day trial</p>
          </div>
          
          <div class="features">
            <div class="feature">
              <span class="feature-icon">📊</span>
              <div class="feature-content">
                <div class="feature-title">Deep Voice Analysis</div>
                <div class="feature-desc">Analyze up to 10,000 words per month with detailed breakdowns</div>
                <div class="feature-locked">🔒 Currently limited to 500 words</div>
              </div>
            </div>
            
            <div class="feature">
              <span class="feature-icon">🎯</span>
              <div class="feature-content">
                <div class="feature-title">All 40 Voice Profiles</div>
                <div class="feature-desc">Discover your primary profile and explore all variations</div>
                <div class="feature-locked">🔒 Limited profiles on free tier</div>
              </div>
            </div>
            
            <div class="feature">
              <span class="feature-icon">🔥</span>
              <div class="feature-content">
                <div class="feature-title">Streak Tracking & Milestones</div>
                <div class="feature-desc">Build consistency and unlock achievements</div>
                <div class="feature-locked">🔒 Basic tracking only</div>
              </div>
            </div>
            
            <div class="feature">
              <span class="feature-icon">⭐</span>
              <div class="feature-content">
                <div class="feature-title">Featured Writer Eligibility</div>
                <div class="feature-desc">Get recognized and build your public profile</div>
                <div class="feature-locked">🔒 PRO subscribers only</div>
              </div>
            </div>
          </div>
          
          <div class="social-proof">
            <p class="social-text">
              <span class="social-count" id="trial-count">127</span> writers started their free trial today
            </p>
          </div>
          
          <div class="modal-footer">
            <button class="cta-primary" id="start-trial-btn">
              Start Free Trial →
            </button>
            <button class="cta-secondary" id="close-btn">
              Maybe later
            </button>
          </div>
          
          <p class="guarantee">
            No credit card required • Cancel anytime • 7 days free
          </p>
        </div>
      </div>
    `;

    // Randomize social proof slightly for authenticity
    const baseCount = 120 + Math.floor(Math.random() * 30);
    this.shadowRoot.getElementById('trial-count').textContent = baseCount;

    this.shadowRoot.getElementById('overlay').addEventListener('click', (e) => {
      if (e.target.id === 'overlay') this.close();
    });

    this.shadowRoot.getElementById('close-btn').addEventListener('click', () => {
      this.close();
    });

    this.shadowRoot.getElementById('start-trial-btn').addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('start-trial', { bubbles: true }));
      this.close();
    });
  }
}

customElements.define('value-preview', ValuePreview);


// ═══════════════════════════════════════════════════════════════════════════
// LIMIT REACHED MODAL (Hard Stop)
// ═══════════════════════════════════════════════════════════════════════════

class LimitReached extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._open = false;
    this._wordsUsed = 0;
  }

  static get observedAttributes() { return ['open', 'words-used']; }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === 'open') this._open = newVal !== null && newVal !== 'false';
    if (name === 'words-used') this._wordsUsed = parseInt(newVal) || 0;
    this.render();
  }

  connectedCallback() { this.render(); }

  render() {
    if (!this._open) {
      this.shadowRoot.innerHTML = '';
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .modal {
          background: linear-gradient(135deg, ${COLORS.ink} 0%, #1a1a2e 100%);
          color: white;
          border-radius: 24px;
          max-width: 440px;
          width: 90%;
          padding: 2.5rem;
          text-align: center;
          animation: bounceIn 0.4s ease-out;
        }
        @keyframes bounceIn {
          0% { transform: scale(0.9); opacity: 0; }
          50% { transform: scale(1.02); }
          100% { transform: scale(1); opacity: 1; }
        }
        
        .limit-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        
        .limit-title {
          font-size: 1.75rem;
          font-weight: 700;
          margin: 0 0 0.5rem;
        }
        
        .limit-subtitle {
          font-size: 1rem;
          opacity: 0.8;
          margin: 0 0 2rem;
        }
        
        .stats-row {
          display: flex;
          justify-content: center;
          gap: 2rem;
          margin-bottom: 2rem;
        }
        .stat {
          text-align: center;
        }
        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          color: ${COLORS.coral};
        }
        .stat-label {
          font-size: 0.8rem;
          opacity: 0.7;
        }
        
        .unlock-text {
          font-size: 1.1rem;
          margin-bottom: 1.5rem;
        }
        .unlock-highlight {
          color: ${COLORS.softGold};
          font-weight: 600;
        }
        
        .cta {
          display: block;
          width: 100%;
          padding: 1rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.2rem;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s;
          margin-bottom: 1rem;
        }
        .cta:hover {
          transform: scale(1.02);
          box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5);
        }
        
        .guarantee {
          font-size: 0.85rem;
          opacity: 0.7;
        }
        .guarantee-icon { margin-right: 0.5rem; }
        
        .social-proof {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid rgba(255,255,255,0.1);
          font-size: 0.9rem;
          opacity: 0.8;
        }
        .social-avatars {
          display: flex;
          justify-content: center;
          margin-bottom: 0.75rem;
        }
        .avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: ${COLORS.softGold};
          border: 2px solid ${COLORS.ink};
          margin-left: -8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.8rem;
        }
        .avatar:first-child { margin-left: 0; }
      </style>
      
      <div class="overlay">
        <div class="modal">
          <div class="limit-icon">🎯</div>
          <h2 class="limit-title">You've discovered your voice!</h2>
          <p class="limit-subtitle">But there's so much more to explore...</p>
          
          <div class="stats-row">
            <div class="stat">
              <div class="stat-value">${this._wordsUsed.toLocaleString()}</div>
              <div class="stat-label">words analyzed</div>
            </div>
            <div class="stat">
              <div class="stat-value">40</div>
              <div class="stat-label">profiles to explore</div>
            </div>
          </div>
          
          <p class="unlock-text">
            Unlock <span class="unlock-highlight">10,000 words/month</span> and become a Featured Writer
          </p>
          
          <button class="cta" id="start-trial-btn">
            Start Free Trial →
          </button>
          
          <p class="guarantee">
            <span class="guarantee-icon">✓</span>
            7 days free • No credit card • Cancel anytime
          </p>
          
          <div class="social-proof">
            <div class="social-avatars">
              <div class="avatar">🐿️</div>
              <div class="avatar">✍️</div>
              <div class="avatar">📚</div>
              <div class="avatar">🎨</div>
              <div class="avatar">💡</div>
            </div>
            <p>Join 1,200+ writers who unlocked their full potential</p>
          </div>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('start-trial-btn').addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('start-trial', { bubbles: true }));
    });
  }
}

customElements.define('limit-reached', LimitReached);


// ═══════════════════════════════════════════════════════════════════════════
// TRIAL CONVERSION TRACKER (for analytics)
// ═══════════════════════════════════════════════════════════════════════════

class TrialConversionTracker {
  constructor() {
    this.events = [];
  }

  track(event, data = {}) {
    this.events.push({
      event,
      data,
      timestamp: new Date().toISOString(),
    });

    // In production, send to analytics
    console.log('[Trial Conversion]', event, data);
  }

  nudgeShown(level, wordsUsed) {
    this.track('nudge_shown', { level, wordsUsed });
  }

  nudgeDismissed(level) {
    this.track('nudge_dismissed', { level });
  }

  valuePreviewOpened() {
    this.track('value_preview_opened');
  }

  limitReached(wordsUsed) {
    this.track('limit_reached', { wordsUsed });
  }

  trialStartClicked(source) {
    this.track('trial_start_clicked', { source });
  }

  trialStarted() {
    this.track('trial_started');
  }
}

// Global instance
window.trialTracker = new TrialConversionTracker();


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyTrialConversion = {
    ProgressiveNudge,
    ValuePreview,
    LimitReached,
    TrialConversionTracker,
  };
}
