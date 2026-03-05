/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY MILESTONE CELEBRATION COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Animations and UI for milestone achievements.
 * 
 * Components:
 * - <milestone-celebration> - Main celebration overlay
 * - <shareable-milestone-card> - LinkedIn/Facebook shareable card
 * - <badge-display> - Badge collection display
 * - <writing-progress> - Progress toward next milestone
 * 
 * Animations:
 * - Acorn Collect (First 500) - Coral
 * - Acorn Stack (3-Day Streak) - Coral
 * - Glow Pulse (Daily 1K) - Coral → Soft Gold
 * - Golden Acorn Crown (3-Day 1K) - Soft Gold
 * - Golden Acorn Ring (7-Day 1K) - Soft Gold
 * - Golden Acorn Orbit (14-Day 1K) - Soft Gold
 * - Golden Acorn Tree (30-Day 1K) - Soft Gold
 */

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════

const COLORS = {
  coral: '#FF6B6B',
  coralDark: '#E55A4A',
  softGold: '#D4A574',
  softGoldLight: '#E8C9A0',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
};

const MILESTONE_META = {
  first_500: {
    name: 'First 500',
    description: 'You wrote 500 original words!',
    icon: '✍️',
    animation: 'acorn_collect',
    color: COLORS.coral,
    celebrationTitle: '500 Original Words!',
    celebrationMessage: 'You\'ve started building your voice profile.',
  },
  streak_3_day: {
    name: '3-Day Streak',
    description: '500+ original words for 3 consecutive days',
    icon: '🌰🌰🌰',
    animation: 'acorn_stack',
    color: COLORS.coral,
    celebrationTitle: '3-Day Streak!',
    celebrationMessage: 'Three days of consistent writing. You\'re building a habit.',
  },
  daily_1k: {
    name: 'Daily 1K',
    description: '1,000+ original words today',
    icon: '🔥',
    animation: 'glow_pulse',
    color: COLORS.softGold,
    celebrationTitle: '1,000 Words Today!',
    celebrationMessage: 'A serious day of writing.',
  },
  streak_3_day_1k: {
    name: '3-Day 1K Streak',
    description: '1,000+ original words for 3 consecutive days',
    icon: '👑',
    animation: 'golden_acorn_crown',
    color: COLORS.softGold,
    celebrationTitle: '3-Day 1K Streak!',
    celebrationMessage: 'Three thousand words in three days. Impressive commitment.',
  },
  streak_7_day_1k: {
    name: '7-Day 1K Streak',
    description: '1,000+ original words for 7 consecutive days',
    icon: '💫',
    animation: 'golden_acorn_ring',
    color: COLORS.softGold,
    celebrationTitle: '7-Day 1K Streak!',
    celebrationMessage: 'You\'ve unlocked Featured Writer eligibility.',
    unlocks: 'featured_eligibility',
  },
  streak_14_day_1k: {
    name: '14-Day 1K Streak',
    description: '1,000+ original words for 14 consecutive days',
    icon: '🌟',
    animation: 'golden_acorn_orbit',
    color: COLORS.softGold,
    celebrationTitle: '14-Day 1K Streak!',
    celebrationMessage: 'Two weeks of dedicated writing. Remarkable.',
  },
  streak_30_day_1k: {
    name: '30-Day 1K Streak',
    description: '1,000+ original words for 30 consecutive days',
    icon: '🌳',
    animation: 'golden_acorn_tree',
    color: COLORS.softGold,
    celebrationTitle: '30-Day 1K Streak!',
    celebrationMessage: 'Legendary. Thirty days of 1,000+ words.',
    grantsFlair: true,
  },
  featured_writer: {
    name: 'Featured Writer',
    description: 'Your work is featured on Quirrely',
    icon: '⭐',
    animation: 'none',
    color: COLORS.softGold,
  },
};


// ═══════════════════════════════════════════════════════════════════════════
// MILESTONE CELEBRATION COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class MilestoneCelebration extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['type', 'keystroke-words', 'streak-days', 'open'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get type() { return this.getAttribute('type') || 'first_500'; }
  get keystrokeWords() { return parseInt(this.getAttribute('keystroke-words') || '0'); }
  get streakDays() { return parseInt(this.getAttribute('streak-days') || '0'); }
  get isOpen() { return this.hasAttribute('open'); }

  show(milestoneData) {
    if (milestoneData) {
      this.setAttribute('type', milestoneData.type);
      if (milestoneData.keystroke_words) {
        this.setAttribute('keystroke-words', milestoneData.keystroke_words);
      }
      if (milestoneData.streak_days) {
        this.setAttribute('streak-days', milestoneData.streak_days);
      }
    }
    this.setAttribute('open', '');
    this.render();
    
    // Auto-close after animation
    const meta = MILESTONE_META[this.type] || {};
    const duration = meta.animation === 'acorn_collect' ? 3000 : 
                     meta.animation === 'golden_acorn_tree' ? 4000 : 2500;
    
    setTimeout(() => this.close(), duration);
  }

  close() {
    this.removeAttribute('open');
    this.dispatchEvent(new CustomEvent('milestone-closed'));
  }

  render() {
    const { type, keystrokeWords, streakDays, isOpen } = this;
    const meta = MILESTONE_META[type] || MILESTONE_META.first_500;

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles(meta)}</style>
      <div class="overlay ${isOpen ? 'visible' : ''}" onclick="this.getRootNode().host.close()">
        <div class="celebration" onclick="event.stopPropagation()">
          <div class="animation-container">
            ${this.getAnimationSVG(meta.animation, meta.color)}
          </div>
          <div class="content">
            <h2 class="title">${meta.celebrationTitle || meta.name}</h2>
            <p class="message">${meta.celebrationMessage || meta.description}</p>
            ${keystrokeWords ? `<p class="stat">${keystrokeWords.toLocaleString()} original words</p>` : ''}
            ${streakDays ? `<p class="stat">${streakDays} day streak</p>` : ''}
            ${meta.unlocks ? `<p class="unlock">🔓 ${this.getUnlockMessage(meta.unlocks)}</p>` : ''}
          </div>
          <div class="actions">
            <button class="btn-share" onclick="this.getRootNode().host.share()">Share Achievement</button>
            <button class="btn-close" onclick="this.getRootNode().host.close()">Continue</button>
          </div>
        </div>
      </div>
    `;
  }

  getUnlockMessage(unlock) {
    const messages = {
      'featured_eligibility': 'Featured Writer eligibility unlocked!',
    };
    return messages[unlock] || unlock;
  }

  share() {
    this.dispatchEvent(new CustomEvent('share-milestone', {
      detail: {
        type: this.type,
        keystrokeWords: this.keystrokeWords,
        streakDays: this.streakDays,
      }
    }));
  }

  getAnimationSVG(animation, color) {
    switch (animation) {
      case 'acorn_collect':
        return this.getAcornCollectSVG(color);
      case 'acorn_stack':
        return this.getAcornStackSVG(color);
      case 'glow_pulse':
        return this.getGlowPulseSVG(color);
      case 'golden_acorn_crown':
        return this.getGoldenAcornCrownSVG();
      case 'golden_acorn_ring':
        return this.getGoldenAcornRingSVG();
      case 'golden_acorn_orbit':
        return this.getGoldenAcornOrbitSVG();
      case 'golden_acorn_tree':
        return this.getGoldenAcornTreeSVG();
      default:
        return this.getAcornCollectSVG(color);
    }
  }

  getAcornCollectSVG(color) {
    return `
      <svg class="animation acorn-collect" viewBox="0 0 100 100" width="120" height="120">
        <defs>
          <linearGradient id="acornGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${color}"/>
            <stop offset="100%" style="stop-color:${COLORS.coralDark}"/>
          </linearGradient>
        </defs>
        <!-- Acorn body -->
        <ellipse class="acorn-body" cx="50" cy="60" rx="18" ry="22" fill="url(#acornGrad)"/>
        <!-- Acorn cap -->
        <path class="acorn-cap" d="M32 48 Q50 35 68 48 Q68 55 50 52 Q32 55 32 48" fill="#8B7355"/>
        <!-- Acorn stem -->
        <rect class="acorn-stem" x="48" y="32" width="4" height="10" rx="2" fill="#6B5344"/>
        <!-- Sparkles -->
        <circle class="sparkle s1" cx="25" cy="40" r="3" fill="${color}" opacity="0"/>
        <circle class="sparkle s2" cx="75" cy="45" r="2" fill="${color}" opacity="0"/>
        <circle class="sparkle s3" cx="50" cy="25" r="2.5" fill="${color}" opacity="0"/>
      </svg>
    `;
  }

  getAcornStackSVG(color) {
    return `
      <svg class="animation acorn-stack" viewBox="0 0 120 80" width="150" height="100">
        <!-- Three acorns stacking -->
        <g class="acorn a1" transform="translate(20, 30)">
          <ellipse cx="20" cy="25" rx="12" ry="15" fill="${color}"/>
          <path d="M8 18 Q20 10 32 18 Q32 22 20 20 Q8 22 8 18" fill="#8B7355"/>
        </g>
        <g class="acorn a2" transform="translate(50, 30)">
          <ellipse cx="20" cy="25" rx="12" ry="15" fill="${color}"/>
          <path d="M8 18 Q20 10 32 18 Q32 22 20 20 Q8 22 8 18" fill="#8B7355"/>
        </g>
        <g class="acorn a3" transform="translate(80, 30)">
          <ellipse cx="20" cy="25" rx="12" ry="15" fill="${color}"/>
          <path d="M8 18 Q20 10 32 18 Q32 22 20 20 Q8 22 8 18" fill="#8B7355"/>
        </g>
      </svg>
    `;
  }

  getGlowPulseSVG(color) {
    return `
      <svg class="animation glow-pulse" viewBox="0 0 100 100" width="120" height="120">
        <circle class="glow-ring r1" cx="50" cy="50" r="35" fill="none" stroke="${color}" stroke-width="3" opacity="0"/>
        <circle class="glow-ring r2" cx="50" cy="50" r="25" fill="none" stroke="${COLORS.softGold}" stroke-width="2" opacity="0"/>
        <text x="50" y="55" text-anchor="middle" font-size="24" fill="${color}">🔥</text>
      </svg>
    `;
  }

  getGoldenAcornCrownSVG() {
    return `
      <svg class="animation golden-crown" viewBox="0 0 120 80" width="150" height="100">
        <defs>
          <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${COLORS.softGoldLight}"/>
            <stop offset="100%" style="stop-color:${COLORS.softGold}"/>
          </linearGradient>
        </defs>
        <!-- Crown formation - 3 golden acorns -->
        <g class="crown-acorn c1" transform="translate(25, 35)">
          <ellipse cx="15" cy="18" rx="10" ry="13" fill="url(#goldGrad)"/>
          <path d="M5 12 Q15 5 25 12 Q25 15 15 14 Q5 15 5 12" fill="#A08060"/>
        </g>
        <g class="crown-acorn c2" transform="translate(50, 20)">
          <ellipse cx="15" cy="18" rx="10" ry="13" fill="url(#goldGrad)"/>
          <path d="M5 12 Q15 5 25 12 Q25 15 15 14 Q5 15 5 12" fill="#A08060"/>
        </g>
        <g class="crown-acorn c3" transform="translate(75, 35)">
          <ellipse cx="15" cy="18" rx="10" ry="13" fill="url(#goldGrad)"/>
          <path d="M5 12 Q15 5 25 12 Q25 15 15 14 Q5 15 5 12" fill="#A08060"/>
        </g>
        <!-- Crown shimmer -->
        <path class="crown-shimmer" d="M30 50 L60 25 L90 50" fill="none" stroke="${COLORS.softGold}" stroke-width="2" opacity="0"/>
      </svg>
    `;
  }

  getGoldenAcornRingSVG() {
    return `
      <svg class="animation golden-ring" viewBox="0 0 120 120" width="140" height="140">
        <defs>
          <linearGradient id="goldGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${COLORS.softGoldLight}"/>
            <stop offset="100%" style="stop-color:${COLORS.softGold}"/>
          </linearGradient>
        </defs>
        <!-- 7 acorns in a ring -->
        ${[0, 1, 2, 3, 4, 5, 6].map(i => {
          const angle = (i * 360 / 7 - 90) * Math.PI / 180;
          const x = 60 + 35 * Math.cos(angle);
          const y = 60 + 35 * Math.sin(angle);
          return `
            <g class="ring-acorn r${i}" transform="translate(${x - 8}, ${y - 10})">
              <ellipse cx="8" cy="12" rx="6" ry="8" fill="url(#goldGrad2)"/>
              <path d="M2 8 Q8 4 14 8 Q14 10 8 9 Q2 10 2 8" fill="#A08060"/>
            </g>
          `;
        }).join('')}
      </svg>
    `;
  }

  getGoldenAcornOrbitSVG() {
    return `
      <svg class="animation golden-orbit" viewBox="0 0 120 120" width="140" height="140">
        <defs>
          <linearGradient id="goldGrad3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${COLORS.softGoldLight}"/>
            <stop offset="100%" style="stop-color:${COLORS.softGold}"/>
          </linearGradient>
        </defs>
        <!-- Orbit paths -->
        <ellipse class="orbit-path" cx="60" cy="60" rx="40" ry="20" fill="none" stroke="${COLORS.softGold}" stroke-width="1" opacity="0.3"/>
        <ellipse class="orbit-path" cx="60" cy="60" rx="20" ry="40" fill="none" stroke="${COLORS.softGold}" stroke-width="1" opacity="0.3"/>
        <!-- Orbiting acorns -->
        <g class="orbit-acorn o1">
          <ellipse cx="60" cy="20" rx="6" ry="8" fill="url(#goldGrad3)"/>
        </g>
        <g class="orbit-acorn o2">
          <ellipse cx="100" cy="60" rx="6" ry="8" fill="url(#goldGrad3)"/>
        </g>
        <g class="orbit-acorn o3">
          <ellipse cx="60" cy="100" rx="6" ry="8" fill="url(#goldGrad3)"/>
        </g>
        <g class="orbit-acorn o4">
          <ellipse cx="20" cy="60" rx="6" ry="8" fill="url(#goldGrad3)"/>
        </g>
      </svg>
    `;
  }

  getGoldenAcornTreeSVG() {
    return `
      <svg class="animation golden-tree" viewBox="0 0 100 120" width="120" height="144">
        <defs>
          <linearGradient id="goldGrad4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${COLORS.softGoldLight}"/>
            <stop offset="100%" style="stop-color:${COLORS.softGold}"/>
          </linearGradient>
        </defs>
        <!-- Tree trunk -->
        <rect class="trunk" x="45" y="80" width="10" height="35" rx="2" fill="#8B7355"/>
        <!-- Tree canopy made of acorns -->
        <g class="canopy">
          <ellipse class="tree-acorn t1" cx="50" cy="25" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t2" cx="35" cy="40" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t3" cx="65" cy="40" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t4" cx="25" cy="55" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t5" cx="50" cy="55" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t6" cx="75" cy="55" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t7" cx="35" cy="70" rx="8" ry="10" fill="url(#goldGrad4)"/>
          <ellipse class="tree-acorn t8" cx="65" cy="70" rx="8" ry="10" fill="url(#goldGrad4)"/>
        </g>
        <!-- Golden shimmer -->
        <circle class="tree-shimmer" cx="50" cy="50" r="45" fill="none" stroke="${COLORS.softGold}" stroke-width="2" opacity="0"/>
      </svg>
    `;
  }

  getStyles(meta) {
    return `
      :host {
        display: block;
      }
      
      .overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
      }
      
      .overlay.visible {
        opacity: 1;
        visibility: visible;
      }
      
      .celebration {
        background: ${COLORS.bg};
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        max-width: 360px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        transform: scale(0.9);
        transition: transform 0.3s ease-out;
      }
      
      .overlay.visible .celebration {
        transform: scale(1);
      }
      
      .animation-container {
        margin-bottom: 1.5rem;
        height: 140px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .title {
        font-family: system-ui, sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: ${meta.color};
        margin: 0 0 0.5rem 0;
      }
      
      .message {
        font-size: 1rem;
        color: ${COLORS.ink};
        margin: 0 0 0.5rem 0;
        line-height: 1.5;
      }
      
      .stat {
        font-size: 0.9rem;
        color: ${COLORS.muted};
        margin: 0.25rem 0;
      }
      
      .unlock {
        font-size: 0.95rem;
        color: ${COLORS.softGold};
        font-weight: 600;
        margin: 1rem 0 0 0;
        padding: 0.5rem;
        background: rgba(212, 165, 116, 0.1);
        border-radius: 8px;
      }
      
      .actions {
        display: flex;
        gap: 0.75rem;
        margin-top: 1.5rem;
      }
      
      .btn-share, .btn-close {
        flex: 1;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
      }
      
      .btn-share {
        background: ${meta.color};
        color: white;
      }
      
      .btn-share:hover {
        filter: brightness(1.1);
      }
      
      .btn-close {
        background: transparent;
        color: ${COLORS.muted};
        border: 1px solid ${COLORS.muted};
      }
      
      .btn-close:hover {
        background: rgba(0, 0, 0, 0.05);
      }
      
      /* Acorn Collect Animation */
      .acorn-collect .acorn-body,
      .acorn-collect .acorn-cap,
      .acorn-collect .acorn-stem {
        animation: acornDrop 0.6s ease-out forwards;
      }
      
      .acorn-collect .sparkle {
        animation: sparkle 0.4s ease-out 0.5s forwards;
      }
      
      .acorn-collect .sparkle.s2 { animation-delay: 0.6s; }
      .acorn-collect .sparkle.s3 { animation-delay: 0.7s; }
      
      @keyframes acornDrop {
        0% { transform: translateY(-30px); opacity: 0; }
        60% { transform: translateY(5px); }
        100% { transform: translateY(0); opacity: 1; }
      }
      
      @keyframes sparkle {
        0% { opacity: 0; transform: scale(0); }
        50% { opacity: 1; transform: scale(1.5); }
        100% { opacity: 0; transform: scale(0); }
      }
      
      /* Acorn Stack Animation */
      .acorn-stack .acorn {
        opacity: 0;
        animation: stackIn 0.4s ease-out forwards;
      }
      
      .acorn-stack .a2 { animation-delay: 0.2s; }
      .acorn-stack .a3 { animation-delay: 0.4s; }
      
      @keyframes stackIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      
      /* Glow Pulse Animation */
      .glow-pulse .glow-ring {
        animation: glowPulse 1s ease-out infinite;
      }
      
      .glow-pulse .glow-ring.r2 {
        animation-delay: 0.3s;
      }
      
      @keyframes glowPulse {
        0% { opacity: 0.8; transform: scale(0.8); }
        100% { opacity: 0; transform: scale(1.5); }
      }
      
      /* Golden Crown Animation */
      .golden-crown .crown-acorn {
        opacity: 0;
        animation: crownRise 0.5s ease-out forwards;
      }
      
      .golden-crown .c2 { animation-delay: 0.15s; }
      .golden-crown .c3 { animation-delay: 0.3s; }
      
      .golden-crown .crown-shimmer {
        animation: shimmerIn 0.4s ease-out 0.6s forwards;
      }
      
      @keyframes crownRise {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes shimmerIn {
        0% { opacity: 0; }
        50% { opacity: 0.8; }
        100% { opacity: 0.3; }
      }
      
      /* Golden Ring Animation */
      .golden-ring .ring-acorn {
        opacity: 0;
        animation: ringAppear 0.3s ease-out forwards;
      }
      
      ${[0, 1, 2, 3, 4, 5, 6].map(i => `
        .golden-ring .r${i} { animation-delay: ${i * 0.1}s; }
      `).join('')}
      
      @keyframes ringAppear {
        0% { opacity: 0; transform: scale(0); }
        100% { opacity: 1; transform: scale(1); }
      }
      
      /* Golden Tree Animation */
      .golden-tree .trunk {
        animation: trunkGrow 0.5s ease-out forwards;
        transform-origin: bottom center;
      }
      
      .golden-tree .tree-acorn {
        opacity: 0;
        animation: leafAppear 0.3s ease-out forwards;
      }
      
      ${[1, 2, 3, 4, 5, 6, 7, 8].map(i => `
        .golden-tree .t${i} { animation-delay: ${0.3 + i * 0.1}s; }
      `).join('')}
      
      .golden-tree .tree-shimmer {
        animation: treeShimmer 1s ease-out 1.2s forwards;
      }
      
      @keyframes trunkGrow {
        0% { transform: scaleY(0); }
        100% { transform: scaleY(1); }
      }
      
      @keyframes leafAppear {
        0% { opacity: 0; transform: scale(0); }
        100% { opacity: 1; transform: scale(1); }
      }
      
      @keyframes treeShimmer {
        0% { opacity: 0; transform: scale(0.8); }
        50% { opacity: 0.6; transform: scale(1.1); }
        100% { opacity: 0; transform: scale(1.2); }
      }
    `;
  }
}

customElements.define('milestone-celebration', MilestoneCelebration);


// ═══════════════════════════════════════════════════════════════════════════
// SHAREABLE MILESTONE CARD
// ═══════════════════════════════════════════════════════════════════════════

class ShareableMilestoneCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['profile-type', 'profile-stance', 'profile-title', 'lifetime-words', 
            'badges', 'featured-url', 'user-name'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get profileType() { return this.getAttribute('profile-type') || 'ASSERTIVE'; }
  get profileStance() { return this.getAttribute('profile-stance') || 'OPEN'; }
  get profileTitle() { return this.getAttribute('profile-title') || 'The Confident Listener'; }
  get lifetimeWords() { return parseInt(this.getAttribute('lifetime-words') || '0'); }
  get badges() { 
    try { return JSON.parse(this.getAttribute('badges') || '[]'); } 
    catch { return []; }
  }
  get featuredUrl() { return this.getAttribute('featured-url'); }
  get userName() { return this.getAttribute('user-name'); }

  render() {
    const { profileType, profileStance, profileTitle, lifetimeWords, badges, featuredUrl, userName } = this;

    this.shadowRoot.innerHTML = `
      <style>${this.getStyles()}</style>
      <div class="card">
        <div class="header">
          <div class="profile-icon">🎯</div>
          <div class="profile-info">
            <h2 class="profile-title">${profileTitle}</h2>
            <p class="profile-meta">${profileType} + ${profileStance}</p>
          </div>
        </div>
        
        <div class="voice-profile">
          <p class="voice-label">Voice profile built from</p>
          <p class="voice-words">${lifetimeWords.toLocaleString()} original words</p>
        </div>
        
        ${badges.length > 0 ? `
          <div class="badges">
            ${badges.map(b => `<span class="badge">${b.icon || '🏆'}</span>`).join('')}
          </div>
        ` : ''}
        
        ${featuredUrl ? `
          <div class="featured">
            <span class="featured-badge">⭐ Featured Writer</span>
            <a href="${featuredUrl}" class="featured-link">Read my featured piece →</a>
          </div>
        ` : ''}
        
        <div class="footer">
          <span class="logo">🐿️ quirrely.com</span>
          ${userName ? `<span class="username">@${userName}</span>` : ''}
        </div>
      </div>
    `;
  }

  getStyles() {
    return `
      :host {
        display: block;
      }
      
      .card {
        width: 600px;
        height: 315px;
        background: linear-gradient(135deg, ${COLORS.bg} 0%, #FFF8F0 100%);
        border-radius: 16px;
        padding: 2rem;
        font-family: system-ui, sans-serif;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      }
      
      .header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
      }
      
      .profile-icon {
        font-size: 3rem;
      }
      
      .profile-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: ${COLORS.ink};
        margin: 0;
      }
      
      .profile-meta {
        font-size: 1rem;
        color: ${COLORS.coral};
        margin: 0.25rem 0 0 0;
        font-weight: 600;
      }
      
      .voice-profile {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      
      .voice-label {
        font-size: 0.9rem;
        color: ${COLORS.muted};
        margin: 0;
      }
      
      .voice-words {
        font-size: 2rem;
        font-weight: 700;
        color: ${COLORS.ink};
        margin: 0.25rem 0 0 0;
      }
      
      .badges {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
      }
      
      .badge {
        font-size: 1.5rem;
      }
      
      .featured {
        background: rgba(212, 165, 116, 0.15);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
      }
      
      .featured-badge {
        font-size: 0.9rem;
        font-weight: 600;
        color: ${COLORS.softGold};
      }
      
      .featured-link {
        display: block;
        font-size: 0.85rem;
        color: ${COLORS.coral};
        text-decoration: none;
        margin-top: 0.25rem;
      }
      
      .footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
      }
      
      .logo {
        font-size: 1rem;
        color: ${COLORS.muted};
      }
      
      .username {
        font-size: 0.9rem;
        color: ${COLORS.muted};
      }
    `;
  }

  async toImage() {
    // In production, use html2canvas or server-side rendering
    console.log('Generating shareable image...');
    // Returns base64 image or blob
  }
}

customElements.define('shareable-milestone-card', ShareableMilestoneCard);


// ═══════════════════════════════════════════════════════════════════════════
// BADGE DISPLAY COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class BadgeDisplay extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['badges', 'layout'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get badges() {
    try { return JSON.parse(this.getAttribute('badges') || '[]'); }
    catch { return []; }
  }

  get layout() { return this.getAttribute('layout') || 'inline'; }

  render() {
    const { badges, layout } = this;

    // Sort by tier (most impressive first)
    const tierOrder = ['streak_30_day_1k', 'streak_14_day_1k', 'streak_7_day_1k', 
                       'streak_3_day_1k', 'daily_1k', 'streak_3_day', 'first_500', 'featured_writer'];
    
    const sorted = [...badges].sort((a, b) => {
      const aIdx = tierOrder.indexOf(a.type);
      const bIdx = tierOrder.indexOf(b.type);
      return (aIdx === -1 ? 999 : aIdx) - (bIdx === -1 ? 999 : bIdx);
    });

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .badges {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        .badges.grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          gap: 1rem;
        }
        .badge {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          padding: 0.4rem 0.75rem;
          background: ${COLORS.bg};
          border: 1px solid rgba(0, 0, 0, 0.1);
          border-radius: 20px;
          font-family: system-ui, sans-serif;
          font-size: 0.8rem;
        }
        .badge.has-flair {
          border-color: ${COLORS.softGold};
          background: linear-gradient(135deg, rgba(212, 165, 116, 0.1) 0%, rgba(212, 165, 116, 0.05) 100%);
        }
        .badge-icon { font-size: 1rem; }
        .badge-name { color: ${COLORS.ink}; font-weight: 500; }
        .badge-count { color: ${COLORS.muted}; font-size: 0.75rem; }
      </style>
      <div class="badges ${layout}">
        ${sorted.map(b => {
          const meta = MILESTONE_META[b.type] || {};
          return `
            <div class="badge ${b.has_flair ? 'has-flair' : ''}">
              <span class="badge-icon">${b.icon || meta.icon || '🏆'}</span>
              <span class="badge-name">${b.name || meta.name || b.type}</span>
              ${b.count && b.count > 1 ? `<span class="badge-count">×${b.count}</span>` : ''}
            </div>
          `;
        }).join('')}
      </div>
    `;
  }
}

customElements.define('badge-display', BadgeDisplay);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { MilestoneCelebration, ShareableMilestoneCard, BadgeDisplay, MILESTONE_META };
}

if (typeof window !== 'undefined') {
  window.QuirrelyMilestones = { MilestoneCelebration, ShareableMilestoneCard, BadgeDisplay, MILESTONE_META };
}
