/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY CURATOR COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for Curator tier:
 * - <curator-welcome> - Welcome modal with milestone overview
 * - <curator-progress> - Progress dashboard toward Featured Curator
 * - <curator-milestone-prompt> - Contextual prompts during journey
 * - <curator-path-submission> - Featured Curator path submission form
 * - <featured-path-card> - Display a curated reading path
 * - <tier-upgrade-prompt> - Prompts for Visitor→Reader and Reader→Curator
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
  success: '#00B894',
  warning: '#FDCB6E',
  error: '#E74C3C',
};

const MILESTONE_META = {
  posts_read: { name: 'Breadth', target: 20, icon: '📖', complete: 'You know the landscape' },
  deep_reads: { name: 'Depth', target: 5, icon: '📚', complete: 'You engage seriously' },
  profile_types: { name: 'Range', target: 5, icon: '🌈', complete: 'You have range' },
  bookmarks: { name: 'Curation', target: 10, icon: '📑', complete: 'You\'re curating' },
  reading_streak: { name: 'Consistency', target: 7, icon: '🔥', complete: 'You\'re consistent' },
};


// ═══════════════════════════════════════════════════════════════════════════
// CURATOR WELCOME MODAL
// ═══════════════════════════════════════════════════════════════════════════

class CuratorWelcome extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
  }

  close() {
    this.removeAttribute('open');
    this.dispatchEvent(new CustomEvent('welcome-closed'));
  }

  startExploring() {
    this.dispatchEvent(new CustomEvent('start-exploring'));
    this.close();
  }

  render() {
    const isOpen = this.hasAttribute('open');

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .overlay {
          position: fixed; inset: 0;
          background: rgba(0, 0, 0, 0.6);
          display: ${isOpen ? 'flex' : 'none'};
          align-items: center; justify-content: center;
          z-index: 10000;
        }
        .modal {
          background: ${COLORS.bg}; border-radius: 20px;
          padding: 2rem; max-width: 480px; width: 90%;
        }
        .header { text-align: center; margin-bottom: 1.5rem; }
        .icon { font-size: 3rem; margin-bottom: 1rem; }
        h2 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .intro { color: ${COLORS.muted}; font-size: 0.95rem; margin: 0; }
        .milestones { background: ${COLORS.bgDark}; border-radius: 12px; padding: 1.25rem; margin: 1.5rem 0; }
        .milestones-title { font-size: 0.9rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        .milestone-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0; }
        .milestone-icon { font-size: 1.25rem; }
        .milestone-text { flex: 1; font-size: 0.9rem; color: ${COLORS.muted}; }
        .milestone-target { font-size: 0.8rem; color: ${COLORS.coral}; font-weight: 600; }
        .window-note { text-align: center; padding: 0.75rem; background: rgba(255, 107, 107, 0.1); border-radius: 8px; font-size: 0.85rem; color: ${COLORS.coral}; margin-bottom: 1.5rem; }
        .cta { display: block; width: 100%; padding: 1rem; background: ${COLORS.coral}; color: white; border: none; border-radius: 12px; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .cta:hover { background: ${COLORS.coralDark}; }
      </style>
      
      <div class="overlay">
        <div class="modal">
          <div class="header">
            <div class="icon">📚</div>
            <h2>Welcome, Curator</h2>
            <p class="intro">You've joined a community of thoughtful readers building their taste.</p>
          </div>
          <div class="milestones">
            <p class="milestones-title">In the next 30 days, unlock Featured Curator by:</p>
            ${Object.entries(MILESTONE_META).map(([key, meta]) => `
              <div class="milestone-item">
                <span class="milestone-icon">${meta.icon}</span>
                <span class="milestone-text">${meta.name}</span>
                <span class="milestone-target">${meta.target}${key === 'reading_streak' ? ' days' : ''}</span>
              </div>
            `).join('')}
          </div>
          <div class="window-note">30 days remaining</div>
          <button class="cta" id="start-btn">Start Exploring →</button>
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('start-btn')?.addEventListener('click', () => this.startExploring());
  }
}

customElements.define('curator-welcome', CuratorWelcome);


// ═══════════════════════════════════════════════════════════════════════════
// CURATOR PROGRESS DASHBOARD
// ═══════════════════════════════════════════════════════════════════════════

class CuratorProgress extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() { return ['progress-json']; }
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get progress() {
    try { return JSON.parse(this.getAttribute('progress-json') || '{}'); }
    catch { return {}; }
  }

  render() {
    const { milestones, days_remaining, percent_complete, featured_eligible, featured_curator } = this.progress;
    if (!milestones) { this.shadowRoot.innerHTML = '<p>Loading...</p>'; return; }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        h3 { font-size: 1rem; color: ${COLORS.ink}; margin: 0; }
        .days { font-size: 0.85rem; color: ${days_remaining <= 3 ? COLORS.error : COLORS.muted}; }
        .progress-bar { height: 8px; background: ${COLORS.border}; border-radius: 4px; margin-bottom: 1.5rem; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, ${COLORS.coral} 0%, ${COLORS.softGold} 100%); border-radius: 4px; transition: width 0.5s; }
        .milestones { display: flex; flex-direction: column; gap: 0.75rem; }
        .milestone { display: flex; align-items: center; gap: 0.75rem; }
        .milestone-check { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
        .milestone-check.complete { background: ${COLORS.success}; color: white; }
        .milestone-check.incomplete { background: ${COLORS.border}; color: ${COLORS.muted}; }
        .milestone-info { flex: 1; }
        .milestone-name { font-size: 0.9rem; color: ${COLORS.ink}; }
        .milestone-progress { font-size: 0.8rem; color: ${COLORS.muted}; }
        .milestone.complete .milestone-name { color: ${COLORS.success}; }
        .eligible-banner { margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, rgba(212, 165, 116, 0.15) 0%, rgba(212, 165, 116, 0.05) 100%); border: 1px solid ${COLORS.softGold}; border-radius: 12px; text-align: center; }
        .eligible-banner h4 { color: ${COLORS.softGold}; margin: 0 0 0.5rem 0; }
        .eligible-banner p { color: ${COLORS.muted}; font-size: 0.9rem; margin: 0 0 1rem 0; }
        .eligible-cta { padding: 0.75rem 1.5rem; background: ${COLORS.softGold}; color: white; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; }
      </style>
      
      <div class="container">
        <div class="header">
          <h3>🎯 Path to Featured Curator</h3>
          <span class="days">${days_remaining} days remaining</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" style="width: ${percent_complete}%"></div></div>
        <div class="milestones">
          ${Object.entries(milestones).map(([key, m]) => `
            <div class="milestone ${m.complete ? 'complete' : 'incomplete'}">
              <div class="milestone-check ${m.complete ? 'complete' : 'incomplete'}">${m.complete ? '✓' : m.icon}</div>
              <div class="milestone-info">
                <div class="milestone-name">${m.current}/${m.target} ${MILESTONE_META[key]?.name || key}</div>
                ${m.complete ? `<div class="milestone-progress">${MILESTONE_META[key]?.complete}</div>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
        ${featured_eligible && !featured_curator ? `
          <div class="eligible-banner">
            <h4>⭐ Featured Curator Eligible!</h4>
            <p>You've completed all milestones. Create your reading path.</p>
            <button class="eligible-cta" id="create-path-btn">Create My Path →</button>
          </div>
        ` : ''}
      </div>
    `;
    this.shadowRoot.getElementById('create-path-btn')?.addEventListener('click', () => this.dispatchEvent(new CustomEvent('create-path')));
  }
}

customElements.define('curator-progress', CuratorProgress);


// ═══════════════════════════════════════════════════════════════════════════
// CURATOR PATH SUBMISSION FORM
// ═══════════════════════════════════════════════════════════════════════════

class CuratorPathSubmission extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._title = '';
    this._intro = '';
    this._selectedPosts = [];
    this._agreements = { original: false, permission: false, readAll: false };
    this._submitting = false;
    this._submitted = false;
    this._error = null;
  }

  static get observedAttributes() { return ['bookmarks-json']; }
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get bookmarks() {
    try { return JSON.parse(this.getAttribute('bookmarks-json') || '[]'); }
    catch { return []; }
  }

  get allAgreed() { return this._agreements.original && this._agreements.permission && this._agreements.readAll; }
  get introWordCount() { return this._intro.trim() ? this._intro.trim().split(/\s+/).length : 0; }
  get canSubmit() {
    return this.allAgreed && this._title.length > 0 && this.introWordCount <= 100 &&
           this._selectedPosts.length >= 4 && this._selectedPosts.length <= 6 && !this._submitting;
  }

  render() {
    if (this._submitted) {
      this.shadowRoot.innerHTML = `
        <style>
          :host { display: block; font-family: system-ui, sans-serif; }
          .container { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 2rem; text-align: center; }
          .icon { font-size: 3rem; margin-bottom: 1rem; }
          h3 { color: ${COLORS.success}; margin: 0 0 0.5rem 0; }
          p { color: ${COLORS.muted}; margin: 0; }
        </style>
        <div class="container">
          <div class="icon">✅</div>
          <h3>Path Submitted!</h3>
          <p>We'll review your path and get back to you soon.</p>
        </div>
      `;
      return;
    }

    const bookmarks = this.bookmarks;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; }
        .header { margin-bottom: 1.5rem; }
        h2 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .header p { color: ${COLORS.muted}; font-size: 0.9rem; margin: 0; }
        .field { margin-bottom: 1.25rem; }
        label { display: block; font-size: 0.9rem; font-weight: 600; color: ${COLORS.ink}; margin-bottom: 0.5rem; }
        .field-hint { font-size: 0.8rem; color: ${COLORS.muted}; margin: 0 0 0.5rem 0; }
        input, textarea, select { width: 100%; padding: 0.75rem; border: 1px solid ${COLORS.border}; border-radius: 8px; font-size: 0.9rem; font-family: inherit; box-sizing: border-box; }
        input:focus, textarea:focus, select:focus { outline: none; border-color: ${COLORS.coral}; }
        textarea { resize: vertical; min-height: 100px; }
        .word-count { font-size: 0.8rem; color: ${COLORS.muted}; margin-top: 0.25rem; text-align: right; }
        .word-count.over { color: ${COLORS.error}; }
        .post-selection { display: flex; flex-direction: column; gap: 0.5rem; }
        .selected-post { display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0.75rem; background: ${COLORS.bgDark}; border-radius: 8px; }
        .post-number { width: 24px; height: 24px; background: ${COLORS.coral}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 600; }
        .post-id { flex: 1; font-size: 0.9rem; }
        .remove-post { background: none; border: none; color: ${COLORS.muted}; cursor: pointer; font-size: 1.2rem; }
        select { cursor: pointer; }
        .field-error { font-size: 0.8rem; color: ${COLORS.error}; margin: 0.5rem 0 0 0; }
        .agreements { margin: 1.5rem 0; }
        .agreement { display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem; cursor: pointer; font-size: 0.9rem; color: ${COLORS.ink}; }
        .agreement input { margin-top: 0.2rem; }
        .error { padding: 0.75rem; background: rgba(231, 76, 60, 0.1); border: 1px solid ${COLORS.error}; border-radius: 8px; color: ${COLORS.error}; font-size: 0.9rem; margin-bottom: 1rem; }
        .submit-btn { width: 100%; padding: 1rem; background: ${COLORS.coral}; color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .submit-btn:hover:not(:disabled) { background: ${COLORS.coralDark}; }
        .submit-btn:disabled { background: ${COLORS.muted}; cursor: not-allowed; opacity: 0.6; }
      </style>
      
      <div class="container">
        <div class="header">
          <h2>⭐ Create Your Reading Path</h2>
          <p>Curate 4-6 posts into a meaningful sequence that others can follow.</p>
        </div>
        
        <div class="field">
          <label>Path Title</label>
          <input type="text" id="title-input" placeholder="e.g., The Direct Path" maxlength="100" value="${this._title}">
        </div>
        
        <div class="field">
          <label>Select Posts (${this._selectedPosts.length}/6)</label>
          <p class="field-hint">Choose 4-6 posts from your bookmarks and arrange them in order.</p>
          <div class="post-selection">
            ${this._selectedPosts.map((postId, i) => `
              <div class="selected-post">
                <span class="post-number">${i + 1}</span>
                <span class="post-id">${postId}</span>
                <button class="remove-post" data-post="${postId}">×</button>
              </div>
            `).join('')}
            ${this._selectedPosts.length < 6 ? `
              <select id="add-post-select">
                <option value="">+ Add a post...</option>
                ${bookmarks.filter(b => !this._selectedPosts.includes(b.profile_id || b.content_id))
                  .map(b => `<option value="${b.profile_id || b.content_id}">${b.profile_id || b.content_id}</option>`).join('')}
              </select>
            ` : ''}
          </div>
          ${this._selectedPosts.length < 4 ? `<p class="field-error">Select at least 4 posts</p>` : ''}
        </div>
        
        <div class="field">
          <label>Introduction</label>
          <p class="field-hint">Why this path? Who is it for? (100 words max)</p>
          <textarea id="intro-input" rows="4" placeholder="I'm drawn to writers who...">${this._intro}</textarea>
          <div class="word-count ${this.introWordCount > 100 ? 'over' : ''}">${this.introWordCount}/100 words</div>
        </div>
        
        <div class="agreements">
          <label class="agreement"><input type="checkbox" id="agree-original" ${this._agreements.original ? 'checked' : ''}><span>This is my original curation</span></label>
          <label class="agreement"><input type="checkbox" id="agree-permission" ${this._agreements.permission ? 'checked' : ''}><span>I grant Quirrely permission to feature without compensation</span></label>
          <label class="agreement"><input type="checkbox" id="agree-read-all" ${this._agreements.readAll ? 'checked' : ''}><span>I have read all posts in this path</span></label>
        </div>
        
        ${this._error ? `<div class="error">${this._error}</div>` : ''}
        <button class="submit-btn" id="submit-btn" ${!this.canSubmit ? 'disabled' : ''}>${this._submitting ? 'Submitting...' : 'Submit for Review'}</button>
      </div>
    `;

    this.attachListeners();
  }

  attachListeners() {
    this.shadowRoot.getElementById('title-input')?.addEventListener('input', e => { this._title = e.target.value; this.updateSubmit(); });
    this.shadowRoot.getElementById('intro-input')?.addEventListener('input', e => {
      this._intro = e.target.value;
      const wc = this.shadowRoot.querySelector('.word-count');
      if (wc) { wc.textContent = `${this.introWordCount}/100 words`; wc.classList.toggle('over', this.introWordCount > 100); }
      this.updateSubmit();
    });
    this.shadowRoot.getElementById('add-post-select')?.addEventListener('change', e => {
      if (e.target.value && this._selectedPosts.length < 6) { this._selectedPosts.push(e.target.value); this.render(); }
    });
    this.shadowRoot.querySelectorAll('.remove-post').forEach(btn => {
      btn.addEventListener('click', () => { this._selectedPosts = this._selectedPosts.filter(p => p !== btn.dataset.post); this.render(); });
    });
    ['original', 'permission', 'readAll'].forEach(key => {
      const el = this.shadowRoot.getElementById(`agree-${key === 'readAll' ? 'read-all' : key}`);
      el?.addEventListener('change', e => { this._agreements[key] = e.target.checked; this.updateSubmit(); });
    });
    this.shadowRoot.getElementById('submit-btn')?.addEventListener('click', () => this.submit());
  }

  updateSubmit() { const btn = this.shadowRoot.getElementById('submit-btn'); if (btn) btn.disabled = !this.canSubmit; }

  async submit() {
    if (!this.canSubmit) return;
    this._submitting = true; this._error = null; this.render();
    try {
      const response = await fetch('/api/v2/curator/featured/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token') || ''}` },
        body: JSON.stringify({
          title: this._title, intro: this._intro, post_ids: this._selectedPosts,
          agreement_original: this._agreements.original, agreement_permission: this._agreements.permission, agreement_read_all: this._agreements.readAll,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Submission failed');
      this._submitted = true;
      this.dispatchEvent(new CustomEvent('path-submitted', { detail: data }));
    } catch (err) { this._error = err.message; }
    finally { this._submitting = false; this.render(); }
  }
}

customElements.define('curator-path-submission', CuratorPathSubmission);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED PATH CARD
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedPathCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() { return ['title', 'intro', 'curator-name', 'posts-json', 'url']; }
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get pathTitle() { return this.getAttribute('title') || ''; }
  get intro() { return this.getAttribute('intro') || ''; }
  get curatorName() { return this.getAttribute('curator-name') || ''; }
  get posts() { try { return JSON.parse(this.getAttribute('posts-json') || '[]'); } catch { return []; } }
  get url() { return this.getAttribute('url') || '#'; }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .card { background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; transition: box-shadow 0.2s; }
        .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
        .header { margin-bottom: 1rem; }
        .badge { display: inline-block; padding: 0.25rem 0.5rem; background: ${COLORS.softGold}; color: white; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem; }
        h3 { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 0.25rem 0; }
        .curator { font-size: 0.85rem; color: ${COLORS.muted}; }
        .intro { font-size: 0.9rem; color: ${COLORS.ink}; line-height: 1.5; margin-bottom: 1rem; font-style: italic; }
        .posts { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
        .post-tag { padding: 0.3rem 0.6rem; background: ${COLORS.bgDark}; border-radius: 6px; font-size: 0.8rem; color: ${COLORS.muted}; }
        .cta { display: block; text-align: center; padding: 0.75rem; background: ${COLORS.coral}; color: white; text-decoration: none; border-radius: 8px; font-weight: 500; }
        .cta:hover { background: ${COLORS.coralDark}; }
      </style>
      
      <div class="card">
        <div class="header">
          <span class="badge">⭐ Featured Path</span>
          <h3>${this.pathTitle}</h3>
          <p class="curator">Curated by ${this.curatorName}</p>
        </div>
        <p class="intro">"${this.intro}"</p>
        <div class="posts">
          ${this.posts.map((p, i) => `<span class="post-tag">${i + 1}. ${p}</span>`).join('')}
        </div>
        <a href="${this.url}" class="cta">Start This Path →</a>
      </div>
    `;
  }
}

customElements.define('featured-path-card', FeaturedPathCard);


// ═══════════════════════════════════════════════════════════════════════════
// TIER UPGRADE PROMPTS
// ═══════════════════════════════════════════════════════════════════════════

class TierUpgradePrompt extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() { return ['type', 'context', 'open']; }
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get type() { return this.getAttribute('type') || 'visitor-to-reader'; }
  get context() { return this.getAttribute('context') || 'default'; }
  get isOpen() { return this.hasAttribute('open'); }

  close() { this.removeAttribute('open'); this.dispatchEvent(new CustomEvent('prompt-closed')); }
  action() { this.dispatchEvent(new CustomEvent('upgrade-action', { detail: { type: this.type } })); this.close(); }

  getContent() {
    const contents = {
      'visitor-to-reader': {
        'third-post': {
          icon: '📚', title: 'You\'ve explored 3 writing styles',
          message: 'Sign up free to read unlimited posts, start building your Reading Taste, and save your favorites.',
          cta: 'Create Free Account', dismiss: 'Continue browsing'
        },
        'more-like-this': {
          icon: '🎯', title: 'You\'re developing a pattern',
          message: 'Sign up to get personalized recommendations based on what you actually like.',
          cta: 'Sign Up Free', dismiss: 'Just show me the post'
        },
        'bookmark': {
          icon: '📑', title: 'Want to save this?',
          message: 'Create a free account to bookmark posts and build your personal reading list.',
          cta: 'Create Free Account', dismiss: 'Maybe later'
        },
      },
      'reader-to-curator': {
        'tenth-post': {
          icon: '📖', title: 'You\'ve read 10 posts',
          message: 'Your Reading Taste is emerging. Upgrade to Curator to see your full profile, unlock all Featured Writers, and get curated recommendations.',
          cta: 'Become a Curator — $1.99/mo', dismiss: 'Maybe later'
        },
        'bookmark-limit': {
          icon: '📚', title: 'Your bookmarks are full',
          message: 'Free accounts can save up to 10 favorites. Curators get unlimited bookmarks, full taste analysis, and a shareable reading profile.',
          cta: 'Upgrade to Curator — $1.99/mo', dismiss: 'Manage list'
        },
        'featured-preview': {
          icon: '⭐', title: 'This is a Featured Writer piece',
          message: 'You\'ve read your free piece today. Curators get unlimited access to all Featured Writers — real voices from our community.',
          cta: 'Become a Curator — $1.99/mo', dismiss: 'Explore more'
        },
        'taste-vs-voice': {
          icon: '✍️', title: 'Your Reading Taste: ???',
          message: 'Do you read what you write? Curators can compare their writing voice to their reading taste — often the gap is fascinating.',
          cta: 'Unlock Taste vs Voice — $1.99/mo', dismiss: 'Not now'
        },
      },
    };
    return contents[this.type]?.[this.context] || contents['visitor-to-reader']['third-post'];
  }

  render() {
    const content = this.getContent();
    const isCurator = this.type === 'reader-to-curator';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .prompt { display: ${this.isOpen ? 'block' : 'none'}; background: white; border: 1px solid ${COLORS.border}; border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 32px rgba(0,0,0,0.12); animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
        .icon { font-size: 2rem; margin-bottom: 1rem; text-align: center; }
        h3 { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 0.75rem 0; text-align: center; }
        p { font-size: 0.9rem; color: ${COLORS.muted}; line-height: 1.5; margin: 0 0 1.25rem 0; text-align: center; }
        .cta { display: block; width: 100%; padding: 0.875rem; background: ${isCurator ? COLORS.softGold : COLORS.coral}; color: white; border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600; cursor: pointer; margin-bottom: 0.75rem; }
        .cta:hover { filter: brightness(1.1); }
        .dismiss { display: block; width: 100%; padding: 0.75rem; background: none; border: none; color: ${COLORS.muted}; font-size: 0.9rem; cursor: pointer; }
        .dismiss:hover { color: ${COLORS.ink}; }
      </style>
      
      <div class="prompt">
        <div class="icon">${content.icon}</div>
        <h3>${content.title}</h3>
        <p>${content.message}</p>
        <button class="cta" id="cta-btn">${content.cta}</button>
        <button class="dismiss" id="dismiss-btn">${content.dismiss}</button>
      </div>
    `;

    this.shadowRoot.getElementById('cta-btn')?.addEventListener('click', () => this.action());
    this.shadowRoot.getElementById('dismiss-btn')?.addEventListener('click', () => this.close());
  }
}

customElements.define('tier-upgrade-prompt', TierUpgradePrompt);


// ═══════════════════════════════════════════════════════════════════════════
// CURATOR MILESTONE TOAST
// ═══════════════════════════════════════════════════════════════════════════

class CuratorMilestoneToast extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  show(milestone) {
    this.setAttribute('milestone', milestone.type);
    this.setAttribute('message', milestone.message || MILESTONE_META[milestone.type]?.complete || 'Milestone complete!');
    this.setAttribute('icon', milestone.icon || MILESTONE_META[milestone.type]?.icon || '🏆');
    this.setAttribute('open', '');
    this.render();
    setTimeout(() => this.close(), 4000);
  }

  close() { this.removeAttribute('open'); }

  render() {
    const isOpen = this.hasAttribute('open');
    const icon = this.getAttribute('icon') || '🏆';
    const message = this.getAttribute('message') || '';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; position: fixed; bottom: 2rem; right: 2rem; z-index: 9999; }
        .toast { display: ${isOpen ? 'flex' : 'none'}; align-items: center; gap: 0.75rem; padding: 1rem 1.25rem; background: white; border: 1px solid ${COLORS.success}; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
        .icon { font-size: 1.5rem; }
        .message { font-size: 0.95rem; color: ${COLORS.ink}; font-family: system-ui, sans-serif; }
      </style>
      <div class="toast">
        <span class="icon">${icon}</span>
        <span class="message">${message}</span>
      </div>
    `;
  }
}

customElements.define('curator-milestone-toast', CuratorMilestoneToast);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CuratorWelcome, CuratorProgress, CuratorPathSubmission,
    FeaturedPathCard, TierUpgradePrompt, CuratorMilestoneToast, MILESTONE_META
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyCurator = {
    CuratorWelcome, CuratorProgress, CuratorPathSubmission,
    FeaturedPathCard, TierUpgradePrompt, CuratorMilestoneToast, MILESTONE_META
  };
}
