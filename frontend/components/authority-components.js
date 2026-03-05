/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY AUTHORITY COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for Authority status display and progress tracking.
 * 
 * - <authority-progress> - Progress toward Authority status
 * - <authority-badge> - Display Authority badge with flair
 * - <authority-prompt> - Prompts on the path to Authority
 * - <voice-and-taste-badge> - Combined achievement badge
 */

const COLORS = {
  coral: '#FF6B6B',
  softGold: '#D4A574',
  gold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  success: '#00B894',
};

const AUTHORITY_WRITER_META = {
  featured_pieces: { name: 'Featured Pieces', icon: '📝', target: 3 },
  lifetime_words: { name: 'Lifetime Words', icon: '✍️', target: 50000 },
  streak_30_count: { name: '30-Day Streaks', icon: '🔥', target: 2 },
  days_as_featured: { name: 'Days as Featured', icon: '📅', target: 90 },
};

const AUTHORITY_CURATOR_META = {
  featured_paths: { name: 'Featured Paths', icon: '📚', target: 3 },
  total_path_follows: { name: 'Path Followers', icon: '👥', target: 50 },
  lifetime_deep_reads: { name: 'Deep Reads', icon: '📖', target: 100 },
  days_as_featured: { name: 'Days as Featured', icon: '📅', target: 90 },
};


// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY PROGRESS COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class AuthorityProgress extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'progress-json', 'is-featured', 'is-authority'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get type() { return this.getAttribute('type') || 'writer'; }
  get isFeatured() { return this.hasAttribute('is-featured'); }
  get isAuthority() { return this.hasAttribute('is-authority'); }
  get progress() {
    try { return JSON.parse(this.getAttribute('progress-json') || '{}'); }
    catch { return {}; }
  }

  render() {
    const { type, isFeatured, isAuthority, progress } = this;
    const meta = type === 'writer' ? AUTHORITY_WRITER_META : AUTHORITY_CURATOR_META;
    const title = type === 'writer' ? 'Authority Writer' : 'Authority Curator';
    
    const items = Object.entries(progress);
    const completeCount = items.filter(([_, v]) => v.complete).length;
    const percent = items.length > 0 ? Math.round((completeCount / items.length) * 100) : 0;

    if (isAuthority) {
      this.renderAchieved(title);
      return;
    }

    if (!isFeatured) {
      this.renderNotEligible(type);
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        h3 { font-size: 1rem; color: ${COLORS.ink}; margin: 0; }
        .percent { font-size: 0.9rem; color: ${COLORS.gold}; font-weight: 600; }
        .progress-bar { height: 8px; background: ${COLORS.border}; border-radius: 4px; margin-bottom: 1.5rem; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, ${COLORS.softGold} 0%, ${COLORS.gold} 100%); transition: width 0.5s; }
        .milestones { display: flex; flex-direction: column; gap: 0.75rem; }
        .milestone { display: flex; align-items: center; gap: 0.75rem; }
        .milestone-check { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; }
        .milestone-check.complete { background: ${COLORS.gold}; color: white; }
        .milestone-check.incomplete { background: ${COLORS.border}; color: ${COLORS.muted}; }
        .milestone-info { flex: 1; }
        .milestone-name { font-size: 0.9rem; color: ${COLORS.ink}; }
        .milestone-progress { font-size: 0.8rem; color: ${COLORS.muted}; }
        .eligible-banner { margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.05) 100%); border: 1px solid ${COLORS.gold}; border-radius: 12px; text-align: center; }
        .eligible-banner h4 { color: ${COLORS.gold}; margin: 0 0 0.5rem 0; }
        .eligible-cta { padding: 0.75rem 1.5rem; background: ${COLORS.gold}; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .eligible-cta:hover { filter: brightness(1.1); }
      </style>
      
      <div class="container">
        <div class="header">
          <h3>👑 Path to ${title}</h3>
          <span class="percent">${percent}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${percent}%"></div>
        </div>
        <div class="milestones">
          ${items.map(([key, data]) => `
            <div class="milestone ${data.complete ? 'complete' : 'incomplete'}">
              <div class="milestone-check ${data.complete ? 'complete' : 'incomplete'}">
                ${data.complete ? '✓' : meta[key]?.icon || '○'}
              </div>
              <div class="milestone-info">
                <div class="milestone-name">${meta[key]?.name || key}</div>
                <div class="milestone-progress">${this.formatValue(key, data.current)} / ${this.formatValue(key, data.target)}</div>
              </div>
            </div>
          `).join('')}
        </div>
        ${percent === 100 ? `
          <div class="eligible-banner">
            <h4>👑 You're eligible for ${title}!</h4>
            <button class="eligible-cta" id="claim-btn">Claim ${title} Status</button>
          </div>
        ` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('claim-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('claim-authority', { detail: { type } }));
    });
  }

  renderAchieved(title) {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .achieved { background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(212, 165, 116, 0.1) 100%); border: 2px solid ${COLORS.gold}; border-radius: 16px; padding: 2rem; text-align: center; }
        .crown { font-size: 3rem; margin-bottom: 1rem; }
        h3 { color: ${COLORS.gold}; margin: 0 0 0.5rem 0; font-size: 1.25rem; }
        p { color: ${COLORS.muted}; margin: 0; }
      </style>
      <div class="achieved">
        <div class="crown">👑</div>
        <h3>${title}</h3>
        <p>You've earned your place as a recognized voice in this community.</p>
      </div>
    `;
  }

  renderNotEligible(type) {
    const featuredType = type === 'writer' ? 'Featured Writer' : 'Featured Curator';
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .locked { background: ${COLORS.bgDark}; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 2rem; text-align: center; }
        .icon { font-size: 2rem; margin-bottom: 1rem; opacity: 0.5; }
        h3 { color: ${COLORS.muted}; margin: 0 0 0.5rem 0; }
        p { color: ${COLORS.muted}; margin: 0; font-size: 0.9rem; }
      </style>
      <div class="locked">
        <div class="icon">🔒</div>
        <h3>Authority Status Locked</h3>
        <p>Become a ${featuredType} first to unlock the path to Authority.</p>
      </div>
    `;
  }

  formatValue(key, value) {
    if (key === 'lifetime_words') {
      return value >= 1000 ? `${Math.round(value / 1000)}K` : value;
    }
    return value.toLocaleString();
  }
}

customElements.define('authority-progress', AuthorityProgress);


// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY BADGE COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class AuthorityBadge extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'since', 'size'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get type() { return this.getAttribute('type') || 'writer'; }
  get since() { return this.getAttribute('since'); }
  get size() { return this.getAttribute('size') || 'medium'; }

  render() {
    const { type, since, size } = this;
    const title = type === 'writer' ? 'Authority Writer' : 
                  type === 'curator' ? 'Authority Curator' :
                  type === 'voice_and_taste' ? 'Voice & Taste' :
                  type === 'authority_voice_and_taste' ? 'Authority Voice & Taste' : 'Authority';
    
    const icon = type === 'authority_voice_and_taste' ? '💎' : 
                 type === 'voice_and_taste' ? '🏆' : '👑';
    
    const bgGradient = type === 'authority_voice_and_taste' ? 
      'linear-gradient(135deg, #E8D5B7 0%, #D4A574 50%, #E8D5B7 100%)' :
      'linear-gradient(135deg, #D4A574 0%, #D4A574 100%)';

    const sizes = {
      small: { badge: '24px', icon: '0.8rem', text: '0.7rem' },
      medium: { badge: '36px', icon: '1.2rem', text: '0.85rem' },
      large: { badge: '48px', icon: '1.5rem', text: '1rem' },
    };
    const s = sizes[size] || sizes.medium;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-flex; align-items: center; gap: 0.5rem; }
        .badge {
          width: ${s.badge}; height: ${s.badge};
          background: ${bgGradient};
          border-radius: 50%;
          display: flex; align-items: center; justify-content: center;
          font-size: ${s.icon};
          box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
          animation: shimmer 3s ease-in-out infinite;
        }
        @keyframes shimmer {
          0%, 100% { box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3); }
          50% { box-shadow: 0 2px 16px rgba(255, 215, 0, 0.6); }
        }
        .text { font-size: ${s.text}; color: ${COLORS.gold}; font-weight: 600; font-family: system-ui, sans-serif; }
        .since { font-size: 0.75rem; color: ${COLORS.muted}; margin-left: 0.25rem; }
      </style>
      <span class="badge">${icon}</span>
      <span class="text">${title}</span>
      ${since ? `<span class="since">since ${new Date(since).toLocaleDateString()}</span>` : ''}
    `;
  }
}

customElements.define('authority-badge', AuthorityBadge);


// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY PROMPT COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class AuthorityPrompt extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'milestone', 'current', 'target', 'message', 'open'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get type() { return this.getAttribute('type') || 'writer'; }
  get milestone() { return this.getAttribute('milestone') || ''; }
  get current() { return parseInt(this.getAttribute('current') || '0'); }
  get target() { return parseInt(this.getAttribute('target') || '0'); }
  get message() { return this.getAttribute('message') || ''; }
  get isOpen() { return this.hasAttribute('open'); }

  close() { this.removeAttribute('open'); }

  render() {
    const { type, milestone, current, target, message, isOpen } = this;
    const meta = type === 'writer' ? AUTHORITY_WRITER_META : AUTHORITY_CURATOR_META;
    const m = meta[milestone] || {};
    const isComplete = current >= target;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .prompt {
          display: ${isOpen ? 'block' : 'none'};
          background: white;
          border: 1px solid ${isComplete ? COLORS.gold : COLORS.border};
          border-radius: 12px;
          padding: 1rem 1.25rem;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
          position: relative;
        }
        .close { position: absolute; top: 0.5rem; right: 0.5rem; width: 24px; height: 24px; border: none; background: none; color: ${COLORS.muted}; cursor: pointer; font-size: 1.2rem; }
        .header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
        .icon { font-size: 1.5rem; }
        .title { font-size: 0.95rem; font-weight: 600; color: ${isComplete ? COLORS.gold : COLORS.ink}; }
        .message { font-size: 0.9rem; color: ${COLORS.muted}; margin: 0; }
        .progress { margin-top: 0.75rem; font-size: 0.85rem; color: ${COLORS.gold}; font-weight: 500; }
      </style>
      
      <div class="prompt">
        <button class="close" id="close-btn">×</button>
        <div class="header">
          <span class="icon">${isComplete ? '✅' : m.icon || '👑'}</span>
          <span class="title">${isComplete ? `${m.name} Complete!` : m.name}</span>
        </div>
        <p class="message">${message || (isComplete ? 'One step closer to Authority!' : `${target - current} more to go.`)}</p>
        ${!isComplete ? `<div class="progress">${current} / ${target}</div>` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('close-btn')?.addEventListener('click', () => this.close());
  }
}

customElements.define('authority-prompt', AuthorityPrompt);


// ═══════════════════════════════════════════════════════════════════════════
// VOICE & TASTE BADGE
// ═══════════════════════════════════════════════════════════════════════════

class VoiceAndTasteBadge extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['level', 'writer-since', 'curator-since'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get level() { return this.getAttribute('level') || 'featured'; }
  get writerSince() { return this.getAttribute('writer-since'); }
  get curatorSince() { return this.getAttribute('curator-since'); }

  render() {
    const { level, writerSince, curatorSince } = this;
    const isAuthority = level === 'authority';
    const icon = isAuthority ? '💎' : '🏆';
    const title = isAuthority ? 'Authority Voice & Taste' : 'Voice & Taste';
    const subtitle = isAuthority ? 
      'Authority in both writing and curation' : 
      'Featured as both Writer and Curator';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .badge {
          background: ${isAuthority ? 
            'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' : 
            'linear-gradient(135deg, #2D3436 0%, #636E72 100%)'};
          border-radius: 16px;
          padding: 1.5rem;
          text-align: center;
          position: relative;
          overflow: hidden;
        }
        .badge::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(45deg, transparent 0%, rgba(255,215,0,0.1) 50%, transparent 100%);
          animation: shine 3s ease-in-out infinite;
        }
        @keyframes shine {
          0%, 100% { transform: translateX(-100%); }
          50% { transform: translateX(100%); }
        }
        .icon { font-size: 3rem; margin-bottom: 1rem; position: relative; z-index: 1; }
        h3 { color: ${isAuthority ? COLORS.gold : COLORS.softGold}; margin: 0 0 0.5rem 0; font-size: 1.25rem; position: relative; z-index: 1; }
        .subtitle { color: rgba(255,255,255,0.7); font-size: 0.9rem; margin: 0 0 1rem 0; position: relative; z-index: 1; }
        .dates { display: flex; justify-content: center; gap: 2rem; position: relative; z-index: 1; }
        .date { text-align: center; }
        .date-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; color: rgba(255,255,255,0.5); }
        .date-value { font-size: 0.85rem; color: white; margin-top: 0.25rem; }
      </style>
      
      <div class="badge">
        <div class="icon">${icon}</div>
        <h3>${title}</h3>
        <p class="subtitle">${subtitle}</p>
        <div class="dates">
          <div class="date">
            <div class="date-label">Writer Since</div>
            <div class="date-value">${writerSince ? new Date(writerSince).toLocaleDateString() : '—'}</div>
          </div>
          <div class="date">
            <div class="date-label">Curator Since</div>
            <div class="date-value">${curatorSince ? new Date(curatorSince).toLocaleDateString() : '—'}</div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('voice-and-taste-badge', VoiceAndTasteBadge);


// ═══════════════════════════════════════════════════════════════════════════
// AUTHORITY STATUS CARD (Combined view)
// ═══════════════════════════════════════════════════════════════════════════

class AuthorityStatusCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['writer-status-json', 'curator-status-json'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get writerStatus() {
    try { return JSON.parse(this.getAttribute('writer-status-json') || '{}'); }
    catch { return {}; }
  }

  get curatorStatus() {
    try { return JSON.parse(this.getAttribute('curator-status-json') || '{}'); }
    catch { return {}; }
  }

  render() {
    const w = this.writerStatus;
    const c = this.curatorStatus;

    const hasBothAuthority = w.authority && c.authority;
    const hasBothFeatured = w.featured && c.featured;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; }
        h3 { font-size: 1rem; color: ${COLORS.ink}; margin: 0 0 1.5rem 0; text-align: center; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .status-card { padding: 1rem; border-radius: 12px; text-align: center; }
        .status-card.writer { background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 107, 107, 0.05) 100%); }
        .status-card.curator { background: linear-gradient(135deg, rgba(212, 165, 116, 0.1) 0%, rgba(212, 165, 116, 0.05) 100%); }
        .status-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .status-title { font-size: 0.9rem; font-weight: 600; color: ${COLORS.ink}; margin-bottom: 0.25rem; }
        .status-level { font-size: 0.8rem; color: ${COLORS.muted}; }
        .status-level.authority { color: ${COLORS.gold}; font-weight: 600; }
        .status-level.featured { color: ${COLORS.softGold}; }
        .combined { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid ${COLORS.border}; text-align: center; }
        .combined-badge { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: linear-gradient(135deg, ${hasBothAuthority ? COLORS.gold : COLORS.softGold} 0%, ${hasBothAuthority ? '#E8D5B7' : COLORS.coral} 100%); border-radius: 20px; }
        .combined-icon { font-size: 1.25rem; }
        .combined-text { font-size: 0.9rem; color: white; font-weight: 600; }
      </style>
      
      <div class="container">
        <h3>Your Status</h3>
        <div class="grid">
          <div class="status-card writer">
            <div class="status-icon">${w.authority ? '👑' : w.featured ? '⭐' : '✍️'}</div>
            <div class="status-title">Writer</div>
            <div class="status-level ${w.authority ? 'authority' : w.featured ? 'featured' : ''}">
              ${w.authority ? 'Authority' : w.featured ? 'Featured' : 'Active'}
            </div>
          </div>
          <div class="status-card curator">
            <div class="status-icon">${c.authority ? '👑' : c.featured ? '⭐' : '📚'}</div>
            <div class="status-title">Curator</div>
            <div class="status-level ${c.authority ? 'authority' : c.featured ? 'featured' : ''}">
              ${c.authority ? 'Authority' : c.featured ? 'Featured' : 'Active'}
            </div>
          </div>
        </div>
        ${hasBothFeatured ? `
          <div class="combined">
            <div class="combined-badge">
              <span class="combined-icon">${hasBothAuthority ? '💎' : '🏆'}</span>
              <span class="combined-text">${hasBothAuthority ? 'Authority Voice & Taste' : 'Voice & Taste'}</span>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('authority-status-card', AuthorityStatusCard);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AuthorityProgress, AuthorityBadge, AuthorityPrompt,
    VoiceAndTasteBadge, AuthorityStatusCard,
    AUTHORITY_WRITER_META, AUTHORITY_CURATOR_META,
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyAuthority = {
    AuthorityProgress, AuthorityBadge, AuthorityPrompt,
    VoiceAndTasteBadge, AuthorityStatusCard,
    AUTHORITY_WRITER_META, AUTHORITY_CURATOR_META,
  };
}
