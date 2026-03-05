/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EMAIL PREFERENCES COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for email preference management.
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
};

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const TIMEZONES = [
  { value: 'America/Toronto', label: 'Eastern Time (Toronto)' },
  { value: 'America/Chicago', label: 'Central Time (Chicago)' },
  { value: 'America/Denver', label: 'Mountain Time (Denver)' },
  { value: 'America/Vancouver', label: 'Pacific Time (Vancouver)' },
  { value: 'Europe/London', label: 'UK Time (London)' },
  { value: 'Europe/Paris', label: 'Central European (Paris)' },
  { value: 'Australia/Sydney', label: 'Australian Eastern (Sydney)' },
  { value: 'Pacific/Auckland', label: 'New Zealand (Auckland)' },
];


// ═══════════════════════════════════════════════════════════════════════════
// EMAIL PREFERENCES PAGE
// ═══════════════════════════════════════════════════════════════════════════

class EmailPreferencesPage extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._preferences = null;
    this._loading = true;
    this._saving = false;
  }

  connectedCallback() {
    this.loadPreferences();
  }

  async loadPreferences() {
    try {
      const response = await fetch('/api/v2/email/preferences', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
      });
      this._preferences = await response.json();
    } catch (err) {
      console.error('Failed to load preferences:', err);
      this._preferences = {
        engagement_enabled: true,
        digest_enabled: true,
        digest_day: 0,
        preferred_hour: 9,
        timezone: 'America/Toronto',
      };
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async savePreferences(updates) {
    this._saving = true;
    this.render();

    try {
      const response = await fetch('/api/v2/email/preferences', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        Object.assign(this._preferences, updates);
      }
    } catch (err) {
      console.error('Failed to save preferences:', err);
    } finally {
      this._saving = false;
      this.render();
    }
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: ${COLORS.muted};">
          Loading preferences...
        </div>
      `;
      return;
    }

    const prefs = this._preferences;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 2rem; }
        h1 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .subtitle { color: ${COLORS.muted}; margin: 0 0 2rem 0; }
        
        .section { margin-bottom: 2rem; }
        .section-title { font-size: 1rem; font-weight: 600; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        .section-desc { font-size: 0.9rem; color: ${COLORS.muted}; margin: 0 0 1rem 0; }
        
        .toggle-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          margin-bottom: 0.75rem;
        }
        .toggle-info { flex: 1; }
        .toggle-label { font-size: 0.95rem; color: ${COLORS.ink}; margin-bottom: 0.25rem; }
        .toggle-desc { font-size: 0.8rem; color: ${COLORS.muted}; }
        
        .toggle {
          width: 48px;
          height: 28px;
          background: ${COLORS.border};
          border-radius: 14px;
          position: relative;
          cursor: pointer;
          transition: background 0.2s;
        }
        .toggle.on { background: ${COLORS.success}; }
        .toggle::after {
          content: '';
          position: absolute;
          width: 22px;
          height: 22px;
          background: white;
          border-radius: 50%;
          top: 3px;
          left: 3px;
          transition: transform 0.2s;
          box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .toggle.on::after { transform: translateX(20px); }
        
        .field { margin-bottom: 1rem; }
        label { display: block; font-size: 0.9rem; color: ${COLORS.ink}; margin-bottom: 0.5rem; }
        select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 0.95rem;
          background: white;
          cursor: pointer;
        }
        select:focus { outline: none; border-color: ${COLORS.coral}; }
        
        .note {
          padding: 1rem;
          background: ${COLORS.bgDark};
          border-radius: 8px;
          font-size: 0.85rem;
          color: ${COLORS.muted};
        }
        .note strong { color: ${COLORS.ink}; }
      </style>
      
      <div class="container">
        <h1>Email Preferences</h1>
        <p class="subtitle">Control what emails you receive from Quirrely.</p>
        
        <div class="section">
          <h2 class="section-title">Notifications</h2>
          <p class="section-desc">Get notified about your writing progress.</p>
          
          <div class="toggle-row">
            <div class="toggle-info">
              <div class="toggle-label">Engagement emails</div>
              <div class="toggle-desc">Streak reminders, milestone celebrations, Authority eligibility</div>
            </div>
            <div class="toggle ${prefs.engagement_enabled ? 'on' : ''}" id="engagement-toggle"></div>
          </div>
          
          <div class="toggle-row">
            <div class="toggle-info">
              <div class="toggle-label">Weekly digest</div>
              <div class="toggle-desc">Summary of your writing activity each week</div>
            </div>
            <div class="toggle ${prefs.digest_enabled ? 'on' : ''}" id="digest-toggle"></div>
          </div>
        </div>
        
        <div class="section">
          <h2 class="section-title">Timing</h2>
          <p class="section-desc">When should we send your emails?</p>
          
          <div class="field">
            <label for="timezone">Your timezone</label>
            <select id="timezone">
              ${TIMEZONES.map(tz => `
                <option value="${tz.value}" ${prefs.timezone === tz.value ? 'selected' : ''}>${tz.label}</option>
              `).join('')}
            </select>
          </div>
          
          <div class="field">
            <label for="digest-day">Weekly digest day</label>
            <select id="digest-day">
              ${DAYS.map((day, i) => `
                <option value="${i}" ${prefs.digest_day === i ? 'selected' : ''}>${day}</option>
              `).join('')}
            </select>
          </div>
          
          <div class="field">
            <label for="preferred-hour">Preferred time</label>
            <select id="preferred-hour">
              ${Array.from({length: 24}, (_, i) => {
                const hour = i === 0 ? '12 AM' : i < 12 ? `${i} AM` : i === 12 ? '12 PM' : `${i - 12} PM`;
                return `<option value="${i}" ${prefs.preferred_hour === i ? 'selected' : ''}>${hour}</option>`;
              }).join('')}
            </select>
          </div>
        </div>
        
        <div class="note">
          <strong>Note:</strong> You'll always receive essential emails about your account, payments, and security regardless of these settings.
        </div>
      </div>
    `;

    // Event listeners
    this.shadowRoot.getElementById('engagement-toggle')?.addEventListener('click', () => {
      this.savePreferences({ engagement_enabled: !prefs.engagement_enabled });
    });

    this.shadowRoot.getElementById('digest-toggle')?.addEventListener('click', () => {
      this.savePreferences({ digest_enabled: !prefs.digest_enabled });
    });

    this.shadowRoot.getElementById('timezone')?.addEventListener('change', (e) => {
      this.savePreferences({ timezone: e.target.value });
    });

    this.shadowRoot.getElementById('digest-day')?.addEventListener('change', (e) => {
      this.savePreferences({ digest_day: parseInt(e.target.value) });
    });

    this.shadowRoot.getElementById('preferred-hour')?.addEventListener('change', (e) => {
      this.savePreferences({ preferred_hour: parseInt(e.target.value) });
    });
  }
}

customElements.define('email-preferences-page', EmailPreferencesPage);


// ═══════════════════════════════════════════════════════════════════════════
// UNSUBSCRIBE CONFIRMATION PAGE
// ═══════════════════════════════════════════════════════════════════════════

class UnsubscribeConfirmation extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['category', 'success'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get category() { return this.getAttribute('category') || 'emails'; }
  get success() { return this.hasAttribute('success'); }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container {
          max-width: 480px;
          margin: 80px auto;
          padding: 2rem;
          text-align: center;
        }
        .icon { font-size: 3rem; margin-bottom: 1rem; }
        h1 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        p { color: ${COLORS.muted}; margin: 0 0 2rem 0; line-height: 1.6; }
        .btn {
          display: inline-block;
          padding: 0.75rem 1.5rem;
          background: ${COLORS.coral};
          color: white;
          text-decoration: none;
          border-radius: 8px;
          font-weight: 500;
        }
        .btn:hover { background: ${COLORS.coralDark}; }
        .btn-secondary {
          background: ${COLORS.bgDark};
          color: ${COLORS.ink};
          margin-left: 0.75rem;
        }
      </style>
      
      <div class="container">
        ${this.success ? `
          <div class="icon">✅</div>
          <h1>You've been unsubscribed</h1>
          <p>You won't receive ${this.category} emails from Quirrely anymore.</p>
          <a href="/email-preferences" class="btn">Manage Preferences</a>
          <a href="/" class="btn btn-secondary">Back to Quirrely</a>
        ` : `
          <div class="icon">❌</div>
          <h1>Something went wrong</h1>
          <p>We couldn't process your unsubscribe request. Please try again or contact support.</p>
          <a href="mailto:support@quirrely.com" class="btn">Contact Support</a>
        `}
      </div>
    `;
  }
}

customElements.define('unsubscribe-confirmation', UnsubscribeConfirmation);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EmailPreferencesPage, UnsubscribeConfirmation };
}

if (typeof window !== 'undefined') {
  window.QuirrelyEmail = { EmailPreferencesPage, UnsubscribeConfirmation };
}
