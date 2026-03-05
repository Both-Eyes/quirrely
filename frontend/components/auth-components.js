/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY AUTHENTICATION COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for authentication UI.
 * 
 * Auth Methods: Email/password, Magic link, Google (NEVER Apple)
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
  error: '#E74C3C',
  google: '#4285F4',
};

const PASSWORD_CONFIG = {
  minLengthSimple: 12,
  minLengthComplex: 8,
};


// ═══════════════════════════════════════════════════════════════════════════
// AUTH FORM (Sign Up / Login)
// ═══════════════════════════════════════════════════════════════════════════

class AuthForm extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._mode = 'login'; // 'login' | 'signup' | 'magic-link'
    this._loading = false;
    this._error = null;
  }

  static get observedAttributes() { return ['mode']; }
  
  connectedCallback() { this.render(); }
  
  attributeChangedCallback(name, _, newVal) {
    if (name === 'mode') this._mode = newVal;
    this.render();
  }

  get mode() { return this._mode; }
  set mode(val) { this._mode = val; this.render(); }

  async handleSubmit(e) {
    e.preventDefault();
    this._loading = true;
    this._error = null;
    this.render();

    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');

    try {
      let endpoint, body;

      if (this._mode === 'magic-link') {
        endpoint = '/api/v2/auth/login/magic-link';
        body = { email };
      } else if (this._mode === 'signup') {
        endpoint = '/api/v2/auth/signup';
        body = { email, password };
      } else {
        endpoint = '/api/v2/auth/login';
        body = { email, password };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      // Store tokens if returned
      if (data.access_token) {
        localStorage.setItem('quirrely_auth_token', data.access_token);
        localStorage.setItem('quirrely_refresh_token', data.refresh_token);
      }

      this.dispatchEvent(new CustomEvent('auth-success', { detail: data }));

    } catch (err) {
      this._error = err.message;
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async handleGoogleAuth() {
    try {
      const response = await fetch('/api/v2/auth/login/google', { method: 'POST' });
      const data = await response.json();
      
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      }
    } catch (err) {
      this._error = 'Google authentication failed';
      this.render();
    }
  }

  render() {
    const isLogin = this._mode === 'login';
    const isSignup = this._mode === 'signup';
    const isMagicLink = this._mode === 'magic-link';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { max-width: 400px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        .logo { font-size: 2rem; margin-bottom: 0.5rem; }
        h2 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .subtitle { color: ${COLORS.muted}; font-size: 0.95rem; margin: 0; }
        
        .social-buttons { margin-bottom: 1.5rem; }
        .google-btn {
          width: 100%;
          padding: 0.875rem;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 0.95rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          color: ${COLORS.ink};
          transition: background 0.2s;
        }
        .google-btn:hover { background: ${COLORS.bgDark}; }
        .google-btn svg { width: 20px; height: 20px; }
        
        .divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; color: ${COLORS.muted}; font-size: 0.85rem; }
        .divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: ${COLORS.border}; }
        
        form { display: flex; flex-direction: column; gap: 1rem; }
        .field { display: flex; flex-direction: column; gap: 0.5rem; }
        label { font-size: 0.9rem; font-weight: 500; color: ${COLORS.ink}; }
        input {
          padding: 0.875rem;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }
        input:focus { outline: none; border-color: ${COLORS.coral}; }
        
        .password-field { position: relative; }
        .toggle-password {
          position: absolute;
          right: 0.875rem;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: ${COLORS.muted};
          cursor: pointer;
          padding: 0.25rem;
        }
        
        .error {
          padding: 0.75rem;
          background: rgba(231, 76, 60, 0.1);
          border: 1px solid ${COLORS.error};
          border-radius: 8px;
          color: ${COLORS.error};
          font-size: 0.9rem;
        }
        
        .submit-btn {
          padding: 1rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        .submit-btn:hover:not(:disabled) { background: ${COLORS.coralDark}; }
        .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        
        .mode-switch { text-align: center; margin-top: 1.5rem; font-size: 0.9rem; color: ${COLORS.muted}; }
        .mode-switch a { color: ${COLORS.coral}; text-decoration: none; font-weight: 500; cursor: pointer; }
        .mode-switch a:hover { text-decoration: underline; }
        
        .magic-link-option { text-align: center; margin-top: 1rem; }
        .magic-link-option a { color: ${COLORS.muted}; font-size: 0.85rem; cursor: pointer; }
      </style>
      
      <div class="container">
        <div class="header">
          <div class="logo">🐿️</div>
          <h2>${isSignup ? 'Create your account' : isMagicLink ? 'Sign in with email' : 'Welcome back'}</h2>
          <p class="subtitle">${isSignup ? 'Start discovering your voice' : isMagicLink ? 'We\'ll send you a magic link' : 'Sign in to continue'}</p>
        </div>
        
        ${!isMagicLink ? `
          <div class="social-buttons">
            <button class="google-btn" id="google-btn">
              <svg viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              Continue with Google
            </button>
          </div>
          
          <div class="divider">or</div>
        ` : ''}
        
        <form id="auth-form">
          <div class="field">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required placeholder="you@example.com">
          </div>
          
          ${!isMagicLink ? `
            <div class="field">
              <label for="password">${isSignup ? 'Create password' : 'Password'}</label>
              <div class="password-field">
                <input type="password" id="password" name="password" required 
                  placeholder="${isSignup ? '12+ characters recommended' : 'Enter your password'}"
                  minlength="${isSignup ? PASSWORD_CONFIG.minLengthComplex : 1}">
                <button type="button" class="toggle-password" id="toggle-password">👁️</button>
              </div>
            </div>
            ${isSignup ? '<password-strength-meter></password-strength-meter>' : ''}
          ` : ''}
          
          ${this._error ? `<div class="error">${this._error}</div>` : ''}
          
          <button type="submit" class="submit-btn" ${this._loading ? 'disabled' : ''}>
            ${this._loading ? 'Please wait...' : isMagicLink ? 'Send magic link' : isSignup ? 'Create account' : 'Sign in'}
          </button>
        </form>
        
        ${!isMagicLink && !isSignup ? `
          <div class="magic-link-option">
            <a id="magic-link-switch">Sign in with magic link instead</a>
          </div>
        ` : ''}
        
        <div class="mode-switch">
          ${isSignup ? 
            'Already have an account? <a id="login-switch">Sign in</a>' : 
            isMagicLink ?
            '<a id="password-switch">Sign in with password</a>' :
            'Don\'t have an account? <a id="signup-switch">Sign up</a>'}
        </div>
      </div>
    `;

    // Event listeners
    this.shadowRoot.getElementById('auth-form')?.addEventListener('submit', (e) => this.handleSubmit(e));
    this.shadowRoot.getElementById('google-btn')?.addEventListener('click', () => this.handleGoogleAuth());
    
    this.shadowRoot.getElementById('toggle-password')?.addEventListener('click', () => {
      const input = this.shadowRoot.getElementById('password');
      input.type = input.type === 'password' ? 'text' : 'password';
    });
    
    this.shadowRoot.getElementById('login-switch')?.addEventListener('click', () => { this._mode = 'login'; this.render(); });
    this.shadowRoot.getElementById('signup-switch')?.addEventListener('click', () => { this._mode = 'signup'; this.render(); });
    this.shadowRoot.getElementById('magic-link-switch')?.addEventListener('click', () => { this._mode = 'magic-link'; this.render(); });
    this.shadowRoot.getElementById('password-switch')?.addEventListener('click', () => { this._mode = 'login'; this.render(); });

    // Password strength meter connection
    const passwordInput = this.shadowRoot.getElementById('password');
    const strengthMeter = this.shadowRoot.querySelector('password-strength-meter');
    if (passwordInput && strengthMeter) {
      passwordInput.addEventListener('input', (e) => {
        strengthMeter.setAttribute('password', e.target.value);
      });
    }
  }
}

customElements.define('auth-form', AuthForm);


// ═══════════════════════════════════════════════════════════════════════════
// PASSWORD STRENGTH METER
// ═══════════════════════════════════════════════════════════════════════════

class PasswordStrengthMeter extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() { return ['password']; }
  
  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get password() { return this.getAttribute('password') || ''; }

  getStrength(password) {
    if (!password) return { score: 0, label: '', color: COLORS.border };

    const length = password.length;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSymbol = /[^a-zA-Z0-9]/.test(password);

    let score = 0;
    score += Math.min(length / 4, 3);
    score += hasUpper ? 1 : 0;
    score += hasLower ? 1 : 0;
    score += hasNumber ? 1 : 0;
    score += hasSymbol ? 1 : 0;
    score += length >= 12 ? 1 : 0;
    score += length >= 16 ? 1 : 0;

    const normalized = Math.min(Math.floor(score / 2.5), 4);

    const labels = ['Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
    const colors = [COLORS.error, '#E67E22', '#F1C40F', COLORS.success, '#27AE60'];

    return {
      score: normalized,
      label: labels[normalized],
      color: colors[normalized],
    };
  }

  render() {
    const strength = this.getStrength(this.password);
    const percentage = (strength.score / 4) * 100;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; margin-top: 0.5rem; }
        .meter { height: 4px; background: ${COLORS.border}; border-radius: 2px; overflow: hidden; }
        .fill { height: 100%; transition: width 0.3s, background 0.3s; }
        .label { display: flex; justify-content: space-between; margin-top: 0.25rem; font-size: 0.75rem; }
        .strength { color: ${strength.color}; font-weight: 500; }
        .hint { color: ${COLORS.muted}; }
      </style>
      
      <div class="meter">
        <div class="fill" style="width: ${percentage}%; background: ${strength.color};"></div>
      </div>
      ${this.password ? `
        <div class="label">
          <span class="strength">${strength.label}</span>
          <span class="hint">${this.password.length < 12 ? '12+ chars for passphrase' : '✓ Good length'}</span>
        </div>
      ` : ''}
    `;
  }
}

customElements.define('password-strength-meter', PasswordStrengthMeter);


// ═══════════════════════════════════════════════════════════════════════════
// EMAIL VERIFICATION BANNER
// ═══════════════════════════════════════════════════════════════════════════

class EmailVerificationBanner extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._sending = false;
    this._sent = false;
  }

  static get observedAttributes() { return ['email', 'action']; }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get email() { return this.getAttribute('email') || ''; }
  get action() { return this.getAttribute('action') || ''; }

  async resendVerification() {
    this._sending = true;
    this.render();

    try {
      const response = await fetch('/api/v2/auth/verify/resend', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
      });

      if (response.ok) {
        this._sent = true;
      }
    } catch (err) {
      console.error('Failed to resend verification:', err);
    } finally {
      this._sending = false;
      this.render();
    }
  }

  render() {
    const actionText = this.action ? ` to ${this.action}` : '';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .banner {
          padding: 1rem;
          background: rgba(255, 107, 107, 0.1);
          border: 1px solid ${COLORS.coral};
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 1rem;
        }
        .content { flex: 1; }
        .title { font-weight: 600; color: ${COLORS.ink}; font-size: 0.95rem; margin-bottom: 0.25rem; }
        .message { color: ${COLORS.muted}; font-size: 0.85rem; }
        .resend-btn {
          padding: 0.5rem 1rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.85rem;
          cursor: pointer;
          white-space: nowrap;
        }
        .resend-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .sent { color: ${COLORS.success}; font-size: 0.85rem; }
      </style>
      
      <div class="banner">
        <div class="content">
          <div class="title">📧 Verify your email${actionText}</div>
          <div class="message">Check ${this.email || 'your inbox'} for a verification link.</div>
        </div>
        ${this._sent ? 
          '<span class="sent">✓ Email sent</span>' :
          `<button class="resend-btn" id="resend-btn" ${this._sending ? 'disabled' : ''}>
            ${this._sending ? 'Sending...' : 'Resend'}
          </button>`
        }
      </div>
    `;

    this.shadowRoot.getElementById('resend-btn')?.addEventListener('click', () => this.resendVerification());
  }
}

customElements.define('email-verification-banner', EmailVerificationBanner);


// ═══════════════════════════════════════════════════════════════════════════
// DISPLAY NAME FORM
// ═══════════════════════════════════════════════════════════════════════════

class DisplayNameForm extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._saving = false;
    this._error = null;
  }

  static get observedAttributes() { return ['current-name', 'context']; }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get currentName() { return this.getAttribute('current-name') || ''; }
  get context() { return this.getAttribute('context') || ''; }

  async handleSubmit(e) {
    e.preventDefault();
    this._saving = true;
    this._error = null;
    this.render();

    const formData = new FormData(e.target);
    const displayName = formData.get('display_name');

    try {
      const response = await fetch('/api/v2/auth/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ display_name: displayName }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update name');
      }

      this.dispatchEvent(new CustomEvent('name-saved', { detail: { displayName } }));

    } catch (err) {
      this._error = err.message;
    } finally {
      this._saving = false;
      this.render();
    }
  }

  render() {
    const contextText = this.context ? ` for ${this.context}` : '';

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { padding: 1.5rem; background: white; border: 1px solid ${COLORS.border}; border-radius: 12px; }
        h3 { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .subtitle { color: ${COLORS.muted}; font-size: 0.9rem; margin: 0 0 1rem 0; }
        .field { margin-bottom: 1rem; }
        label { display: block; font-size: 0.9rem; font-weight: 500; color: ${COLORS.ink}; margin-bottom: 0.5rem; }
        input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 1rem;
          box-sizing: border-box;
        }
        input:focus { outline: none; border-color: ${COLORS.coral}; }
        .hint { font-size: 0.8rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        .error { padding: 0.75rem; background: rgba(231, 76, 60, 0.1); border: 1px solid ${COLORS.error}; border-radius: 6px; color: ${COLORS.error}; font-size: 0.9rem; margin-bottom: 1rem; }
        .submit-btn {
          width: 100%;
          padding: 0.875rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
        }
        .submit-btn:hover:not(:disabled) { background: ${COLORS.coralDark}; }
        .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
      </style>
      
      <div class="container">
        <h3>Choose your display name</h3>
        <p class="subtitle">This is how you'll appear${contextText}.</p>
        
        <form id="name-form">
          <div class="field">
            <label for="display_name">Display name</label>
            <input type="text" id="display_name" name="display_name" 
              value="${this.currentName}"
              minlength="2" maxlength="50" required
              placeholder="Your name">
            <div class="hint">2-50 characters. Letters, numbers, spaces, hyphens.</div>
          </div>
          
          ${this._error ? `<div class="error">${this._error}</div>` : ''}
          
          <button type="submit" class="submit-btn" ${this._saving ? 'disabled' : ''}>
            ${this._saving ? 'Saving...' : 'Save name'}
          </button>
        </form>
      </div>
    `;

    this.shadowRoot.getElementById('name-form')?.addEventListener('submit', (e) => this.handleSubmit(e));
  }
}

customElements.define('display-name-form', DisplayNameForm);


// ═══════════════════════════════════════════════════════════════════════════
// PROFILE VISIBILITY SELECTOR
// ═══════════════════════════════════════════════════════════════════════════

class ProfileVisibilitySelector extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() { return ['value']; }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get value() { return this.getAttribute('value') || 'private'; }
  set value(val) { this.setAttribute('value', val); }

  async handleChange(visibility) {
    try {
      const response = await fetch('/api/v2/auth/me', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ profile_visibility: visibility }),
      });

      if (response.ok) {
        this.value = visibility;
        this.dispatchEvent(new CustomEvent('visibility-change', { detail: { visibility } }));
      }
    } catch (err) {
      console.error('Failed to update visibility:', err);
    }
  }

  render() {
    const options = [
      { value: 'private', label: 'Private', icon: '🔒', desc: 'Only you can see your profile' },
      { value: 'featured_only', label: 'Featured only', icon: '⭐', desc: 'Visible on Featured pages' },
      { value: 'public', label: 'Public', icon: '🌐', desc: 'Anyone can see your profile' },
    ];

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .options { display: flex; flex-direction: column; gap: 0.75rem; }
        .option {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 1rem;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          cursor: pointer;
          transition: border-color 0.2s, background 0.2s;
        }
        .option:hover { background: ${COLORS.bgDark}; }
        .option.selected { border-color: ${COLORS.coral}; background: rgba(255, 107, 107, 0.05); }
        .option-radio {
          width: 20px;
          height: 20px;
          border: 2px solid ${COLORS.border};
          border-radius: 50%;
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .option.selected .option-radio { border-color: ${COLORS.coral}; }
        .option.selected .option-radio::after {
          content: '';
          width: 10px;
          height: 10px;
          background: ${COLORS.coral};
          border-radius: 50%;
        }
        .option-content { flex: 1; }
        .option-label { display: flex; align-items: center; gap: 0.5rem; font-weight: 500; color: ${COLORS.ink}; }
        .option-desc { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
      </style>
      
      <div class="options">
        ${options.map(opt => `
          <div class="option ${this.value === opt.value ? 'selected' : ''}" data-value="${opt.value}">
            <div class="option-radio"></div>
            <div class="option-content">
              <div class="option-label">${opt.icon} ${opt.label}</div>
              <div class="option-desc">${opt.desc}</div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    this.shadowRoot.querySelectorAll('.option').forEach(opt => {
      opt.addEventListener('click', () => this.handleChange(opt.dataset.value));
    });
  }
}

customElements.define('profile-visibility-selector', ProfileVisibilitySelector);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    AuthForm, PasswordStrengthMeter, EmailVerificationBanner,
    DisplayNameForm, ProfileVisibilitySelector,
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyAuth = {
    AuthForm, PasswordStrengthMeter, EmailVerificationBanner,
    DisplayNameForm, ProfileVisibilitySelector,
  };
}
