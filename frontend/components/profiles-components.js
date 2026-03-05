/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY PUBLIC PROFILES COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Public profile pages, showcase grids, and social sharing.
 * URL: /@username
 */

const COLORS = {
  coral: '#FF6B6B',
  coralLight: 'rgba(255, 107, 107, 0.1)',
  softGold: '#D4A574',
  softGoldLight: 'rgba(212, 165, 116, 0.2)',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  success: '#00B894',
  authority: '#6C5CE7',
};


// ═══════════════════════════════════════════════════════════════════════════
// PUBLIC PROFILE PAGE
// ═══════════════════════════════════════════════════════════════════════════

class PublicProfile extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._profile = null;
    this._loading = true;
    this._notFound = false;
  }

  static get observedAttributes() { return ['username']; }

  connectedCallback() { this.loadProfile(); }
  attributeChangedCallback() { this.loadProfile(); }

  get username() { return this.getAttribute('username'); }

  async loadProfile() {
    if (!this.username) return;
    
    this._loading = true;
    this._notFound = false;
    this.render();

    try {
      const response = await fetch(`/api/v2/profiles/${this.username}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token') || ''}`,
        },
      });
      
      if (response.status === 404) {
        this._notFound = true;
      } else {
        this._profile = await response.json();
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
      this._notFound = true;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async copyLink() {
    const url = this._profile?.share_urls?.copy_link;
    if (url) {
      await navigator.clipboard.writeText(url);
      // Show toast
      const btn = this.shadowRoot.getElementById('copy-btn');
      if (btn) {
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = '🔗 Copy link', 2000);
      }
    }
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 4rem; color: ${COLORS.muted};">
          Loading profile...
        </div>
      `;
      return;
    }

    if (this._notFound) {
      this.shadowRoot.innerHTML = `
        <style>
          :host { display: block; font-family: system-ui, sans-serif; }
          .not-found { text-align: center; padding: 4rem 2rem; }
          .not-found-icon { font-size: 4rem; margin-bottom: 1rem; }
          h1 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
          p { color: ${COLORS.muted}; }
          .btn { display: inline-block; margin-top: 1rem; padding: 0.75rem 1.5rem; background: ${COLORS.coral}; color: white; text-decoration: none; border-radius: 8px; }
        </style>
        <div class="not-found">
          <div class="not-found-icon">🐿️</div>
          <h1>Profile not found</h1>
          <p>This profile doesn't exist or is set to private.</p>
          <a href="/" class="btn">Go home</a>
        </div>
      `;
      return;
    }

    const p = this._profile;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; background: ${COLORS.bg}; min-height: 100vh; }
        
        .profile-header {
          background: white;
          border-bottom: 1px solid ${COLORS.border};
          padding: 3rem 2rem 2rem;
        }
        .header-content { max-width: 800px; margin: 0 auto; display: flex; gap: 2rem; align-items: flex-start; }
        @media (max-width: 600px) { .header-content { flex-direction: column; align-items: center; text-align: center; } }
        
        .avatar {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: ${COLORS.bgDark};
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 3rem;
          flex-shrink: 0;
          overflow: hidden;
        }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        
        .info { flex: 1; }
        .display-name { font-size: 1.75rem; font-weight: 700; color: ${COLORS.ink}; margin: 0; }
        .username { font-size: 1rem; color: ${COLORS.muted}; margin: 0.25rem 0 0.75rem 0; }
        
        .badges { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: 500;
        }
        .badge-featured { background: ${COLORS.softGoldLight}; color: #8B6914; }
        .badge-authority { background: rgba(108, 92, 231, 0.15); color: ${COLORS.authority}; }
        
        .bio { font-size: 1rem; color: ${COLORS.ink}; line-height: 1.6; margin-bottom: 1rem; }
        
        .voice-card {
          display: inline-block;
          padding: 0.75rem 1rem;
          background: ${COLORS.bgDark};
          border-radius: 8px;
          margin-bottom: 1rem;
        }
        .voice-label { font-size: 0.75rem; color: ${COLORS.muted}; text-transform: uppercase; margin-bottom: 0.25rem; }
        .voice-type { font-size: 1.1rem; font-weight: 600; color: ${COLORS.coral}; }
        .voice-stance { font-size: 0.9rem; color: ${COLORS.muted}; }
        
        .share-buttons { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .share-btn {
          padding: 0.5rem 1rem;
          border: 1px solid ${COLORS.border};
          background: white;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          color: ${COLORS.ink};
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
        }
        .share-btn:hover { background: ${COLORS.bgDark}; }
        
        .content { max-width: 800px; margin: 2rem auto; padding: 0 2rem; }
        
        .section { margin-bottom: 2rem; }
        .section-title { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        
        .pieces-grid, .paths-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
        .piece, .path {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 10px;
          padding: 1.25rem;
        }
        .piece-title, .path-title { font-size: 1rem; font-weight: 600; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .piece-preview, .path-desc { font-size: 0.9rem; color: ${COLORS.muted}; line-height: 1.5; }
        .piece-meta, .path-meta { font-size: 0.8rem; color: ${COLORS.muted}; margin-top: 0.75rem; }
        
        .join-date { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 1rem; }
      </style>
      
      <div class="profile-header">
        <div class="header-content">
          <div class="avatar">
            ${p.avatar_url ? `<img src="${p.avatar_url}" alt="${p.display_name}">` : '🐿️'}
          </div>
          
          <div class="info">
            <h1 class="display-name">${p.display_name}</h1>
            <p class="username">@${p.username}</p>
            
            ${p.badges?.length ? `
              <div class="badges">
                ${p.badges.map(b => `
                  <span class="badge ${b.label.includes('Authority') ? 'badge-authority' : 'badge-featured'}">
                    ${b.icon} ${b.label}
                  </span>
                `).join('')}
              </div>
            ` : ''}
            
            ${p.bio ? `<p class="bio">${p.bio}</p>` : ''}
            
            ${p.voice_profile_type ? `
              <div class="voice-card">
                <div class="voice-label">Voice Profile</div>
                <div class="voice-type">${p.voice_profile_type}</div>
                ${p.voice_stance ? `<div class="voice-stance">${p.voice_stance}</div>` : ''}
              </div>
            ` : ''}
            
            <div class="share-buttons">
              <button class="share-btn" id="copy-btn">🔗 Copy link</button>
              <a class="share-btn" href="${p.share_urls?.linkedin || '#'}" target="_blank">LinkedIn</a>
              <a class="share-btn" href="${p.share_urls?.facebook || '#'}" target="_blank">Facebook</a>
              <a class="share-btn" href="${p.share_urls?.email || '#'}">📧 Email</a>
            </div>
            
            <p class="join-date">Member since ${p.join_date}</p>
          </div>
        </div>
      </div>
      
      <div class="content">
        ${p.featured_pieces?.length ? `
          <div class="section">
            <h2 class="section-title">⭐ Featured Pieces</h2>
            <div class="pieces-grid">
              ${p.featured_pieces.map(piece => `
                <div class="piece">
                  <h3 class="piece-title">${piece.title}</h3>
                  <p class="piece-preview">${piece.preview || ''}</p>
                  <p class="piece-meta">${piece.word_count} words • ${piece.voice_profile_type || ''}</p>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
        
        ${p.curated_paths?.length ? `
          <div class="section">
            <h2 class="section-title">📚 Curated Reading Paths</h2>
            <div class="paths-grid">
              ${p.curated_paths.map(path => `
                <div class="path">
                  <h3 class="path-title">${path.title}</h3>
                  <p class="path-desc">${path.description || ''}</p>
                  <p class="path-meta">${path.post_count} posts • ${path.follow_count} followers</p>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('copy-btn')?.addEventListener('click', () => this.copyLink());
  }
}

customElements.define('public-profile', PublicProfile);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED SHOWCASE GRID
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedShowcase extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._loading = true;
  }

  static get observedAttributes() { return ['type']; }

  connectedCallback() { this.loadData(); }
  attributeChangedCallback() { this.loadData(); }

  get type() { return this.getAttribute('type') || 'writers'; }

  async loadData() {
    this._loading = true;
    this.render();

    try {
      const response = await fetch(`/api/v2/profiles/featured/${this.type}`);
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load showcase:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: ${COLORS.muted};">
          Loading...
        </div>
      `;
      return;
    }

    const meta = this._data?.meta || {};
    const items = this._data?.writers || this._data?.curators || this._data?.members || [];

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .header { text-align: center; margin-bottom: 2rem; }
        h1 { font-size: 2rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .description { font-size: 1.1rem; color: ${COLORS.muted}; }
        
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
          gap: 1.5rem;
        }
        
        .card {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 12px;
          padding: 1.5rem;
          text-align: center;
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
          text-decoration: none;
          display: block;
        }
        .card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: ${COLORS.bgDark};
          margin: 0 auto 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          overflow: hidden;
        }
        .avatar img { width: 100%; height: 100%; object-fit: cover; }
        
        .name { font-size: 1.1rem; font-weight: 600; color: ${COLORS.ink}; margin: 0 0 0.25rem 0; }
        .username { font-size: 0.85rem; color: ${COLORS.muted}; margin: 0 0 0.75rem 0; }
        
        .profile-type { font-size: 0.9rem; color: ${COLORS.coral}; margin-bottom: 0.5rem; }
        
        .badges { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; }
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.2rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
          background: ${COLORS.softGoldLight};
          color: #8B6914;
        }
        .badge.authority { background: rgba(108, 92, 231, 0.15); color: ${COLORS.authority}; }
        
        .empty { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="header">
        <h1>${meta.title || 'Featured'}</h1>
        <p class="description">${meta.description || ''}</p>
      </div>
      
      ${items.length ? `
        <div class="grid">
          ${items.map(item => `
            <a class="card" href="${item.profile_url}">
              <div class="avatar">
                ${item.avatar_url ? `<img src="${item.avatar_url}" alt="${item.display_name}">` : '🐿️'}
              </div>
              <h3 class="name">${item.display_name}</h3>
              <p class="username">@${item.username}</p>
              ${item.voice_profile_type ? `<p class="profile-type">${item.voice_profile_type}</p>` : ''}
              ${item.reading_taste_type ? `<p class="profile-type">${item.reading_taste_type}</p>` : ''}
              <div class="badges">
                ${item.badges?.map(b => `
                  <span class="badge ${b.label.includes('Authority') ? 'authority' : ''}">${b.icon} ${b.label}</span>
                `).join('') || ''}
              </div>
            </a>
          `).join('')}
        </div>
      ` : `
        <div class="empty">No featured members yet. Be the first!</div>
      `}
    `;
  }
}

customElements.define('featured-showcase', FeaturedShowcase);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED LANDING PAGE
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedLanding extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/profiles/featured');
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load:', err);
    }
    this.render();
  }

  render() {
    const d = this._data || {};
    const counts = d.counts || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; background: ${COLORS.bg}; }
        
        .hero {
          text-align: center;
          padding: 4rem 2rem;
          background: linear-gradient(135deg, ${COLORS.coral} 0%, ${COLORS.softGold} 100%);
          color: white;
        }
        .hero h1 { font-size: 2.5rem; margin: 0 0 1rem 0; }
        .hero p { font-size: 1.25rem; opacity: 0.9; max-width: 600px; margin: 0 auto; }
        
        .stats {
          display: flex;
          justify-content: center;
          gap: 3rem;
          margin-top: 2rem;
          flex-wrap: wrap;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 2.5rem; font-weight: 700; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        
        .sections { max-width: 1200px; margin: 3rem auto; padding: 0 2rem; }
        
        .section-card {
          display: block;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 12px;
          padding: 2rem;
          margin-bottom: 1.5rem;
          text-decoration: none;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .section-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .section-card h2 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .section-card p { font-size: 1rem; color: ${COLORS.muted}; margin: 0; }
        .section-card .arrow { float: right; font-size: 1.5rem; color: ${COLORS.coral}; }
      </style>
      
      <div class="hero">
        <h1>⭐ Featured on Quirrely</h1>
        <p>Discover writers and curators recognized for their exceptional work and consistent dedication.</p>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${counts.featured_writers || 0}</div>
            <div class="stat-label">Featured Writers</div>
          </div>
          <div class="stat">
            <div class="stat-value">${counts.featured_curators || 0}</div>
            <div class="stat-label">Featured Curators</div>
          </div>
          <div class="stat">
            <div class="stat-value">${counts.authority_members || 0}</div>
            <div class="stat-label">Authority Members</div>
          </div>
        </div>
      </div>
      
      <div class="sections">
        <a class="section-card" href="/featured/writers">
          <span class="arrow">→</span>
          <h2>✍️ Featured Writers</h2>
          <p>Writers recognized for their consistent voice and dedication to the craft.</p>
        </a>
        
        <a class="section-card" href="/featured/curators">
          <span class="arrow">→</span>
          <h2>📚 Featured Curators</h2>
          <p>Curators recognized for their exceptional reading taste and curation skills.</p>
        </a>
        
        <a class="section-card" href="/featured/authority">
          <span class="arrow">→</span>
          <h2>👑 Authority Members</h2>
          <p>The most distinguished voices on Quirrely — sustained excellence over time.</p>
        </a>
      </div>
    `;
  }
}

customElements.define('featured-landing', FeaturedLanding);


// ═══════════════════════════════════════════════════════════════════════════
// USERNAME SETUP
// ═══════════════════════════════════════════════════════════════════════════

class UsernameSetup extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._username = '';
    this._available = null;
    this._error = null;
    this._checking = false;
    this._saving = false;
  }

  connectedCallback() { this.render(); }

  async checkUsername(username) {
    this._username = username;
    this._checking = true;
    this._available = null;
    this._error = null;
    this.render();

    try {
      const response = await fetch(`/api/v2/profiles/username/check?username=${encodeURIComponent(username)}`);
      const data = await response.json();
      this._available = data.available;
      this._error = data.error;
    } catch (err) {
      this._error = 'Failed to check availability';
    } finally {
      this._checking = false;
      this.render();
    }
  }

  async saveUsername() {
    if (!this._available) return;

    this._saving = true;
    this.render();

    try {
      const response = await fetch('/api/v2/profiles/username', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ username: this._username }),
      });

      const data = await response.json();

      if (data.success) {
        this.dispatchEvent(new CustomEvent('username-set', { detail: data }));
      } else {
        this._error = data.detail || 'Failed to set username';
      }
    } catch (err) {
      this._error = 'Failed to save username';
    } finally {
      this._saving = false;
      this.render();
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { max-width: 400px; margin: 0 auto; padding: 2rem; }
        h2 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        p { color: ${COLORS.muted}; margin: 0 0 1.5rem 0; }
        
        .input-group { position: relative; margin-bottom: 1rem; }
        .prefix {
          position: absolute;
          left: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: ${COLORS.muted};
          font-size: 1rem;
        }
        input {
          width: 100%;
          padding: 0.875rem 1rem 0.875rem 2.5rem;
          border: 2px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 1rem;
          box-sizing: border-box;
        }
        input:focus { outline: none; border-color: ${COLORS.coral}; }
        input.valid { border-color: ${COLORS.success}; }
        input.invalid { border-color: ${COLORS.coral}; }
        
        .status { font-size: 0.85rem; margin-bottom: 1rem; min-height: 1.2em; }
        .status.checking { color: ${COLORS.muted}; }
        .status.available { color: ${COLORS.success}; }
        .status.error { color: ${COLORS.coral}; }
        
        .btn {
          width: 100%;
          padding: 0.875rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          background: ${COLORS.coral};
          color: white;
        }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .preview { margin-top: 1.5rem; padding: 1rem; background: ${COLORS.bgDark}; border-radius: 8px; text-align: center; }
        .preview-label { font-size: 0.8rem; color: ${COLORS.muted}; margin-bottom: 0.25rem; }
        .preview-url { font-size: 1rem; color: ${COLORS.ink}; font-weight: 500; }
      </style>
      
      <div class="container">
        <h2>Choose your username</h2>
        <p>This will be your public profile URL. You can change it once every 30 days.</p>
        
        <div class="input-group">
          <span class="prefix">@</span>
          <input 
            type="text" 
            id="username-input"
            placeholder="username"
            value="${this._username}"
            class="${this._available === true ? 'valid' : this._available === false ? 'invalid' : ''}"
          >
        </div>
        
        <div class="status ${this._checking ? 'checking' : this._available ? 'available' : this._error ? 'error' : ''}">
          ${this._checking ? 'Checking availability...' : 
            this._available ? '✓ Username is available' : 
            this._error ? this._error : ''}
        </div>
        
        <button class="btn" id="save-btn" ${!this._available || this._saving ? 'disabled' : ''}>
          ${this._saving ? 'Saving...' : 'Claim username'}
        </button>
        
        ${this._username && this._available ? `
          <div class="preview">
            <div class="preview-label">Your profile URL</div>
            <div class="preview-url">quirrely.com/@${this._username.toLowerCase()}</div>
          </div>
        ` : ''}
      </div>
    `;

    let debounceTimer;
    this.shadowRoot.getElementById('username-input')?.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const value = e.target.value.trim();
      if (value.length >= 3) {
        debounceTimer = setTimeout(() => this.checkUsername(value), 300);
      } else {
        this._available = null;
        this._error = value.length > 0 ? 'Username must be at least 3 characters' : null;
        this.render();
      }
    });

    this.shadowRoot.getElementById('save-btn')?.addEventListener('click', () => this.saveUsername());
  }
}

customElements.define('username-setup', UsernameSetup);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyProfiles = {
    PublicProfile,
    FeaturedShowcase,
    FeaturedLanding,
    UsernameSetup,
  };
}
