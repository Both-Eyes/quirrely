/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY SAVE CONSENT & VOICE PROFILE PROMPTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Prompts that encourage users to enable voice profile (save) feature.
 * 
 * Components:
 * - <save-consent-prompt> - Contextual prompts at key moments
 * - <voice-profile-toggle> - Settings toggle
 * - <visitor-signup-prompt> - Encourage visitors to sign up
 */

const COLORS = {
  coral: '#FF6B6B',
  coralDark: '#E55A4A',
  softGold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  blue: '#0984E3',
};


// ═══════════════════════════════════════════════════════════════════════════
// SAVE CONSENT PROMPT
// ═══════════════════════════════════════════════════════════════════════════

class SaveConsentPrompt extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'words-today', 'words-session', 'open'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get type() { return this.getAttribute('type') || 'first-analysis'; }
  get wordsToday() { return parseInt(this.getAttribute('words-today') || '0'); }
  get wordsSession() { return parseInt(this.getAttribute('words-session') || '0'); }
  get isOpen() { return this.hasAttribute('open'); }

  show(type, data = {}) {
    this.setAttribute('type', type);
    if (data.wordsToday) this.setAttribute('words-today', data.wordsToday);
    if (data.wordsSession) this.setAttribute('words-session', data.wordsSession);
    this.setAttribute('open', '');
  }

  close() {
    this.removeAttribute('open');
    this.dispatchEvent(new CustomEvent('prompt-closed'));
  }

  enable() {
    this.dispatchEvent(new CustomEvent('enable-save'));
    this.close();
  }

  render() {
    const { type, wordsToday, wordsSession, isOpen } = this;
    const content = this.getContent(type, wordsToday, wordsSession);

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      <div class="prompt ${isOpen ? 'visible' : ''}">
        <div class="icon">${content.icon}</div>
        <div class="content">
          <p class="stat">${content.stat}</p>
          <p class="message">${content.message}</p>
        </div>
        <div class="actions">
          <button class="btn-enable" id="enable-btn">${content.buttonText}</button>
          <button class="btn-dismiss" id="dismiss-btn">${content.dismissText}</button>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('enable-btn')?.addEventListener('click', () => this.enable());
    this.shadowRoot.getElementById('dismiss-btn')?.addEventListener('click', () => this.close());
  }

  getContent(type, wordsToday, wordsSession) {
    const contents = {
      'first-analysis': {
        icon: '✍️',
        stat: `${wordsSession} original words analyzed`,
        message: 'This is a single snapshot. Enable Voice Profile to let Quirrely learn your patterns across sessions — and show you how your writing voice evolves.',
        buttonText: 'Build My Voice Profile',
        dismissText: 'Stay anonymous',
      },
      'near-milestone': {
        icon: '🌰',
        stat: `${wordsSession} original words this session`,
        message: 'You\'re developing a pattern. Without saving, this insight disappears when you leave.',
        buttonText: 'Start Building My Profile',
        dismissText: 'Not yet',
      },
      'returning-user': {
        icon: '👋',
        stat: `Last session: ${wordsSession} original words (not saved)`,
        message: 'Enable Voice Profile to start building streaks and see how your writing evolves.',
        buttonText: 'Enable Voice Profile',
        dismissText: 'Maybe later',
      },
      'milestone-achieved': {
        icon: '🎉',
        stat: `${wordsToday} original words today!`,
        message: 'You just hit a milestone! Enable saving to preserve your achievement and keep building.',
        buttonText: 'Save My Progress',
        dismissText: 'Skip',
      },
    };

    return contents[type] || contents['first-analysis'];
  }

  getStyles() {
    return `
      :host {
        display: block;
      }

      .prompt {
        background: white;
        border: 1px solid ${COLORS.border};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        display: none;
        animation: slideIn 0.3s ease-out;
      }

      .prompt.visible {
        display: block;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(-10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .icon {
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
      }

      .content {
        margin-bottom: 1rem;
      }

      .stat {
        font-weight: 600;
        color: ${COLORS.ink};
        margin: 0 0 0.5rem 0;
        font-size: 0.95rem;
      }

      .message {
        color: ${COLORS.muted};
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.5;
      }

      .actions {
        display: flex;
        gap: 0.75rem;
      }

      .btn-enable {
        flex: 1;
        padding: 0.6rem 1rem;
        background: ${COLORS.coral};
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
      }

      .btn-enable:hover {
        background: ${COLORS.coralDark};
      }

      .btn-dismiss {
        padding: 0.6rem 1rem;
        background: transparent;
        color: ${COLORS.muted};
        border: 1px solid ${COLORS.border};
        border-radius: 8px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
      }

      .btn-dismiss:hover {
        background: ${COLORS.bgDark};
      }
    `;
  }
}

customElements.define('save-consent-prompt', SaveConsentPrompt);


// ═══════════════════════════════════════════════════════════════════════════
// VOICE PROFILE TOGGLE (Settings)
// ═══════════════════════════════════════════════════════════════════════════

class VoiceProfileToggle extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['enabled'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get enabled() {
    return this.hasAttribute('enabled');
  }

  set enabled(value) {
    if (value) {
      this.setAttribute('enabled', '');
    } else {
      this.removeAttribute('enabled');
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    this.dispatchEvent(new CustomEvent('toggle-change', { detail: { enabled: this.enabled } }));
  }

  render() {
    const { enabled } = this;

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      <div class="container">
        <div class="info">
          <div class="icon">💾</div>
          <div class="text">
            <h4>Build Your Voice Profile</h4>
            <p>When enabled, Quirrely learns from each writing session to give you deeper insights about your evolving voice.</p>
            <p class="privacy">We only store word counts and patterns — never your actual text.</p>
          </div>
        </div>
        <label class="toggle">
          <input type="checkbox" id="toggle" ${enabled ? 'checked' : ''}>
          <span class="slider"></span>
        </label>
      </div>
      ${enabled ? `
        <div class="enabled-info">
          <span class="check">✓</span>
          <span>Voice profile active. Your writing patterns will be tracked across sessions.</span>
        </div>
      ` : ''}
    `;

    this.shadowRoot.getElementById('toggle')?.addEventListener('change', () => this.toggle());
  }

  getStyles() {
    return `
      :host {
        display: block;
      }

      .container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1.5rem;
        padding: 1.25rem;
        background: ${COLORS.bgDark};
        border-radius: 12px;
      }

      .info {
        display: flex;
        gap: 1rem;
      }

      .icon {
        font-size: 1.5rem;
      }

      .text h4 {
        font-size: 1rem;
        color: ${COLORS.ink};
        margin: 0 0 0.5rem 0;
      }

      .text p {
        font-size: 0.9rem;
        color: ${COLORS.muted};
        margin: 0;
        line-height: 1.5;
      }

      .privacy {
        font-size: 0.8rem !important;
        margin-top: 0.5rem !important;
        color: ${COLORS.muted};
        opacity: 0.8;
      }

      .toggle {
        position: relative;
        width: 52px;
        height: 28px;
        flex-shrink: 0;
      }

      .toggle input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      .slider {
        position: absolute;
        cursor: pointer;
        inset: 0;
        background: ${COLORS.border};
        border-radius: 28px;
        transition: 0.3s;
      }

      .slider:before {
        content: '';
        position: absolute;
        height: 22px;
        width: 22px;
        left: 3px;
        bottom: 3px;
        background: white;
        border-radius: 50%;
        transition: 0.3s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
      }

      .toggle input:checked + .slider {
        background: ${COLORS.coral};
      }

      .toggle input:checked + .slider:before {
        transform: translateX(24px);
      }

      .enabled-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        background: rgba(0, 184, 148, 0.1);
        border-radius: 8px;
        font-size: 0.85rem;
        color: #00B894;
      }

      .check {
        font-weight: 600;
      }
    `;
  }
}

customElements.define('voice-profile-toggle', VoiceProfileToggle);


// ═══════════════════════════════════════════════════════════════════════════
// VISITOR SIGNUP PROMPT
// ═══════════════════════════════════════════════════════════════════════════

class VisitorSignupPrompt extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['words-session', 'near-milestone', 'open'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get wordsSession() { return parseInt(this.getAttribute('words-session') || '0'); }
  get nearMilestone() { return this.hasAttribute('near-milestone'); }
  get isOpen() { return this.hasAttribute('open'); }

  show(data = {}) {
    if (data.wordsSession) this.setAttribute('words-session', data.wordsSession);
    if (data.nearMilestone) this.setAttribute('near-milestone', '');
    this.setAttribute('open', '');
  }

  close() {
    this.removeAttribute('open');
  }

  signup() {
    this.dispatchEvent(new CustomEvent('signup-click'));
  }

  render() {
    const { wordsSession, nearMilestone, isOpen } = this;

    const content = nearMilestone ? {
      icon: '🎉',
      title: 'You just hit 500 original words!',
      message: 'Sign up to claim your First 500 badge and make it permanent.',
      buttonText: 'Claim Badge — Sign Up Free',
    } : {
      icon: '✍️',
      title: `You wrote ${wordsSession} original words`,
      message: 'Right now, Quirrely sees a snapshot. Sign up to build a complete picture of your writing voice — over days, weeks, months.',
      buttonText: 'Create Free Account',
    };

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      <div class="prompt ${isOpen ? 'visible' : ''}">
        <button class="close-btn" id="close-btn">×</button>
        <div class="icon">${content.icon}</div>
        <h3>${content.title}</h3>
        <p>${content.message}</p>
        <button class="signup-btn" id="signup-btn">${content.buttonText}</button>
        <button class="guest-btn" id="guest-btn">Continue as guest</button>
      </div>
    `;

    this.shadowRoot.getElementById('close-btn')?.addEventListener('click', () => this.close());
    this.shadowRoot.getElementById('signup-btn')?.addEventListener('click', () => this.signup());
    this.shadowRoot.getElementById('guest-btn')?.addEventListener('click', () => this.close());
  }

  getStyles() {
    return `
      :host {
        display: block;
      }

      .prompt {
        background: white;
        border: 1px solid ${COLORS.border};
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        position: relative;
        display: none;
        animation: fadeIn 0.3s ease-out;
      }

      .prompt.visible {
        display: block;
      }

      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: scale(0.95);
        }
        to {
          opacity: 1;
          transform: scale(1);
        }
      }

      .close-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 28px;
        height: 28px;
        border: none;
        background: ${COLORS.bgDark};
        border-radius: 50%;
        font-size: 1.2rem;
        color: ${COLORS.muted};
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .close-btn:hover {
        background: ${COLORS.border};
      }

      .icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
      }

      h3 {
        font-size: 1.25rem;
        color: ${COLORS.ink};
        margin: 0 0 0.75rem 0;
      }

      p {
        font-size: 0.95rem;
        color: ${COLORS.muted};
        margin: 0 0 1.5rem 0;
        line-height: 1.5;
      }

      .signup-btn {
        display: block;
        width: 100%;
        padding: 0.875rem;
        background: ${COLORS.coral};
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
      }

      .signup-btn:hover {
        background: ${COLORS.coralDark};
      }

      .guest-btn {
        display: block;
        width: 100%;
        margin-top: 0.75rem;
        padding: 0.75rem;
        background: transparent;
        color: ${COLORS.muted};
        border: none;
        font-size: 0.9rem;
        cursor: pointer;
      }

      .guest-btn:hover {
        color: ${COLORS.ink};
      }
    `;
  }
}

customElements.define('visitor-signup-prompt', VisitorSignupPrompt);


// ═══════════════════════════════════════════════════════════════════════════
// PROMPT MANAGER
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Manages prompt display frequency and context.
 */
class PromptManager {
  constructor() {
    this.storage = window.localStorage;
    this.STORAGE_KEY = 'quirrely_prompts';
  }

  getState() {
    try {
      return JSON.parse(this.storage.getItem(this.STORAGE_KEY) || '{}');
    } catch {
      return {};
    }
  }

  saveState(state) {
    this.storage.setItem(this.STORAGE_KEY, JSON.stringify(state));
  }

  /**
   * Check if a prompt should be shown.
   */
  shouldShow(promptType) {
    const state = this.getState();
    const now = Date.now();
    const oneWeek = 7 * 24 * 60 * 60 * 1000;

    switch (promptType) {
      case 'first-analysis':
        // Show once per user
        return !state.firstAnalysisShown;

      case 'near-milestone':
        // Once per session
        return !state.nearMilestoneShownThisSession;

      case 'returning-user':
        // Once per week
        return !state.returningUserShown || (now - state.returningUserShown) > oneWeek;

      case 'visitor-signup':
        // Once per session
        return !state.visitorSignupShownThisSession;

      default:
        return true;
    }
  }

  /**
   * Mark a prompt as shown.
   */
  markShown(promptType) {
    const state = this.getState();
    const now = Date.now();

    switch (promptType) {
      case 'first-analysis':
        state.firstAnalysisShown = true;
        break;
      case 'near-milestone':
        state.nearMilestoneShownThisSession = true;
        break;
      case 'returning-user':
        state.returningUserShown = now;
        break;
      case 'visitor-signup':
        state.visitorSignupShownThisSession = true;
        break;
    }

    this.saveState(state);
  }

  /**
   * Reset session-based prompts (call on new session).
   */
  resetSession() {
    const state = this.getState();
    delete state.nearMilestoneShownThisSession;
    delete state.visitorSignupShownThisSession;
    this.saveState(state);
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { 
    SaveConsentPrompt, 
    VoiceProfileToggle, 
    VisitorSignupPrompt, 
    PromptManager 
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyPrompts = { 
    SaveConsentPrompt, 
    VoiceProfileToggle, 
    VisitorSignupPrompt, 
    PromptManager 
  };
}
