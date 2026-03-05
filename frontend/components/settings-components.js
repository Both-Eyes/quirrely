/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY SETTINGS COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Settings page with categories: Account, Profile, Subscription, Email, Privacy, Appearance
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
  danger: '#E74C3C',
};

const CATEGORY_META = {
  account: { label: 'Account', icon: '👤' },
  profile: { label: 'Profile', icon: '🎨' },
  subscription: { label: 'Subscription', icon: '💳' },
  email: { label: 'Email', icon: '📧' },
  privacy: { label: 'Privacy', icon: '🔒' },
  appearance: { label: 'Appearance', icon: '⚙️' },
};


// ═══════════════════════════════════════════════════════════════════════════
// SETTINGS PAGE
// ═══════════════════════════════════════════════════════════════════════════

class SettingsPage extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._settings = null;
    this._activeCategory = 'account';
    this._loading = true;
  }

  connectedCallback() {
    this.loadSettings();
  }

  async loadSettings() {
    try {
      const response = await fetch('/api/v2/dashboard/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
      });
      this._settings = await response.json();
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async saveSetting(settingId, value) {
    try {
      await fetch('/api/v2/dashboard/settings', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ setting_id: settingId, value }),
      });
      
      if (this._settings?.current_values) {
        this._settings.current_values[settingId] = value;
      }
    } catch (err) {
      console.error('Failed to save setting:', err);
    }
  }

  setCategory(category) {
    this._activeCategory = category;
    this.render();
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 4rem; color: ${COLORS.muted};">
          Loading settings...
        </div>
      `;
      return;
    }

    const categories = Object.keys(this._settings?.categories || {});
    const currentValues = this._settings?.current_values || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; background: ${COLORS.bg}; min-height: 100vh; }
        .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
        
        .header { margin-bottom: 2rem; }
        h1 { font-size: 1.75rem; color: ${COLORS.ink}; margin: 0; }
        
        .layout { display: grid; grid-template-columns: 200px 1fr; gap: 2rem; }
        @media (max-width: 700px) {
          .layout { grid-template-columns: 1fr; }
          .nav { display: flex; overflow-x: auto; gap: 0.5rem; padding-bottom: 1rem; border-bottom: 1px solid ${COLORS.border}; margin-bottom: 1rem; }
        }
        
        .nav { display: flex; flex-direction: column; gap: 0.25rem; }
        @media (max-width: 700px) { .nav { flex-direction: row; } }
        
        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: 8px;
          color: ${COLORS.muted};
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }
        .nav-item:hover { background: ${COLORS.bgDark}; color: ${COLORS.ink}; }
        .nav-item.active { background: white; color: ${COLORS.ink}; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .nav-icon { font-size: 1.1rem; }
        
        .content { }
        .category-title { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0 0 1.5rem 0; }
        
        .settings-list { display: flex; flex-direction: column; gap: 1rem; }
        
        .setting-item {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 10px;
          padding: 1rem 1.25rem;
        }
        .setting-item.danger { border-color: rgba(231, 76, 60, 0.3); }
        
        .setting-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
        .setting-info { flex: 1; }
        .setting-label { font-size: 0.95rem; font-weight: 500; color: ${COLORS.ink}; margin-bottom: 0.25rem; }
        .setting-desc { font-size: 0.85rem; color: ${COLORS.muted}; }
        
        .setting-control { flex-shrink: 0; }
        
        input[type="text"], input[type="email"] {
          width: 100%;
          padding: 0.625rem 0.875rem;
          border: 1px solid ${COLORS.border};
          border-radius: 6px;
          font-size: 0.9rem;
          margin-top: 0.75rem;
          box-sizing: border-box;
        }
        input:focus { outline: none; border-color: ${COLORS.coral}; }
        
        select {
          padding: 0.5rem 2rem 0.5rem 0.75rem;
          border: 1px solid ${COLORS.border};
          border-radius: 6px;
          font-size: 0.9rem;
          background: white;
          cursor: pointer;
          appearance: none;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23636E72' d='M6 8L2 4h8z'/%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 0.75rem center;
        }
        
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
        
        .btn {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 6px;
          font-size: 0.9rem;
          cursor: pointer;
          font-weight: 500;
        }
        .btn-primary { background: ${COLORS.coral}; color: white; }
        .btn-secondary { background: ${COLORS.bgDark}; color: ${COLORS.ink}; }
        .btn-danger { background: ${COLORS.danger}; color: white; }
        .btn:hover { filter: brightness(0.95); }
      </style>
      
      <div class="container">
        <div class="header">
          <h1>Settings</h1>
        </div>
        
        <div class="layout">
          <nav class="nav">
            ${categories.map(cat => `
              <div class="nav-item ${this._activeCategory === cat ? 'active' : ''}" data-category="${cat}">
                <span class="nav-icon">${CATEGORY_META[cat]?.icon || '⚙️'}</span>
                <span>${CATEGORY_META[cat]?.label || cat}</span>
              </div>
            `).join('')}
          </nav>
          
          <div class="content">
            <h2 class="category-title">${CATEGORY_META[this._activeCategory]?.label || this._activeCategory}</h2>
            
            <div class="settings-list">
              ${(this._settings?.categories?.[this._activeCategory] || []).map(setting => 
                this.renderSetting(setting, currentValues[setting.id])
              ).join('')}
            </div>
          </div>
        </div>
      </div>
    `;

    // Event listeners
    this.shadowRoot.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => this.setCategory(item.dataset.category));
    });

    this.shadowRoot.querySelectorAll('.toggle').forEach(toggle => {
      toggle.addEventListener('click', () => {
        const settingId = toggle.dataset.setting;
        const newValue = !toggle.classList.contains('on');
        toggle.classList.toggle('on', newValue);
        this.saveSetting(settingId, newValue);
      });
    });

    this.shadowRoot.querySelectorAll('select').forEach(select => {
      select.addEventListener('change', (e) => {
        this.saveSetting(e.target.dataset.setting, e.target.value);
      });
    });

    this.shadowRoot.querySelectorAll('input[type="text"], input[type="email"]').forEach(input => {
      let timeout;
      input.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          this.saveSetting(e.target.dataset.setting, e.target.value);
        }, 500);
      });
    });

    this.shadowRoot.querySelectorAll('.btn[data-action]').forEach(btn => {
      btn.addEventListener('click', () => this.handleAction(btn.dataset.action, btn.dataset.setting));
    });
  }

  renderSetting(setting, currentValue) {
    let control = '';

    switch (setting.type) {
      case 'toggle':
        control = `<div class="toggle ${currentValue ? 'on' : ''}" data-setting="${setting.id}"></div>`;
        break;
      
      case 'select':
        control = `
          <select data-setting="${setting.id}">
            ${(setting.options || []).map(opt => 
              `<option value="${opt.value}" ${currentValue === opt.value ? 'selected' : ''}>${opt.label}</option>`
            ).join('')}
          </select>
        `;
        break;
      
      case 'action':
        control = `<button class="btn ${setting.danger ? 'btn-danger' : 'btn-secondary'}" data-action="${setting.id}" data-setting="${setting.id}">${setting.action_label}</button>`;
        break;
      
      case 'password':
        control = `<button class="btn btn-secondary" data-action="change_password" data-setting="${setting.id}">${setting.action_label}</button>`;
        break;
    }

    const needsInput = setting.type === 'text' || setting.type === 'email';

    return `
      <div class="setting-item ${setting.danger ? 'danger' : ''}">
        <div class="setting-header">
          <div class="setting-info">
            <div class="setting-label">${setting.label}</div>
            <div class="setting-desc">${setting.description}</div>
          </div>
          <div class="setting-control">${control}</div>
        </div>
        ${needsInput ? `<input type="${setting.type}" data-setting="${setting.id}" value="${currentValue || ''}" placeholder="${setting.label}">` : ''}
      </div>
    `;
  }

  async handleAction(action, settingId) {
    switch (action) {
      case 'delete_account':
        window.location.href = '/account/delete';
        break;
      
      case 'change_password':
        window.location.href = '/account/password';
        break;
      
      case 'current_plan':
      case 'billing':
        try {
          const response = await fetch('/api/v2/payments/billing-portal', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
          });
          const data = await response.json();
          if (data.url) window.location.href = data.url;
        } catch (err) {
          console.error('Failed to open billing portal:', err);
        }
        break;
      
      case 'upgrade':
        window.location.href = '/pricing';
        break;
      
      case 'email_preferences':
        window.location.href = '/email-preferences';
        break;
      
      case 'export_data':
        window.location.href = '/api/v2/dashboard/settings/export';
        break;
      
      case 'avatar':
        alert('Avatar upload coming soon!');
        break;
    }
  }
}

customElements.define('settings-page', SettingsPage);


// ═══════════════════════════════════════════════════════════════════════════
// DELETE ACCOUNT PAGE
// ═══════════════════════════════════════════════════════════════════════════

class DeleteAccountPage extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._step = 'confirm';
    this._deleting = false;
  }

  connectedCallback() { this.render(); }

  async softDelete() {
    this._deleting = true;
    this.render();

    try {
      const response = await fetch('/api/v2/auth/account/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ hard_delete: false }),
      });

      if (response.ok) {
        this._step = 'done';
        localStorage.removeItem('quirrely_auth_token');
      }
    } catch (err) {
      console.error('Failed to delete account:', err);
    } finally {
      this._deleting = false;
      this.render();
    }
  }

  showHardDelete() {
    this._step = 'hard_delete';
    this.render();
  }

  async hardDelete(confirmation) {
    if (confirmation !== 'DELETE MY ACCOUNT') {
      alert('Please type "DELETE MY ACCOUNT" exactly to confirm.');
      return;
    }

    this._deleting = true;
    this.render();

    try {
      const response = await fetch('/api/v2/auth/account/delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
        body: JSON.stringify({ hard_delete: true, confirmation }),
      });

      if (response.ok) {
        this._step = 'done';
        localStorage.removeItem('quirrely_auth_token');
      }
    } catch (err) {
      console.error('Failed to delete account:', err);
    } finally {
      this._deleting = false;
      this.render();
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; background: ${COLORS.bg}; min-height: 100vh; }
        .container { max-width: 500px; margin: 0 auto; padding: 4rem 2rem; }
        .card { background: white; border: 1px solid ${COLORS.border}; border-radius: 12px; padding: 2rem; }
        .icon { font-size: 3rem; text-align: center; margin-bottom: 1rem; }
        h1 { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; text-align: center; }
        p { color: ${COLORS.muted}; line-height: 1.6; margin: 0 0 1rem 0; }
        .warning { padding: 1rem; background: rgba(231, 76, 60, 0.1); border-radius: 8px; margin-bottom: 1.5rem; }
        .warning p { color: ${COLORS.danger}; margin: 0; }
        .actions { display: flex; flex-direction: column; gap: 0.75rem; }
        .btn {
          width: 100%;
          padding: 0.875rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
        }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-danger { background: ${COLORS.danger}; color: white; }
        .btn-secondary { background: ${COLORS.bgDark}; color: ${COLORS.ink}; }
        input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          font-size: 1rem;
          margin-bottom: 1rem;
          box-sizing: border-box;
        }
        .link { color: ${COLORS.coral}; cursor: pointer; text-decoration: underline; font-size: 0.9rem; }
        .footer { text-align: center; margin-top: 1.5rem; }
      </style>
      
      <div class="container">
        <div class="card">
          ${this._step === 'done' ? this.renderDone() : 
            this._step === 'hard_delete' ? this.renderHardDelete() : 
            this.renderConfirm()}
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('soft-delete')?.addEventListener('click', () => this.softDelete());
    this.shadowRoot.getElementById('hard-delete-link')?.addEventListener('click', () => this.showHardDelete());
    this.shadowRoot.getElementById('cancel')?.addEventListener('click', () => window.location.href = '/settings');
    this.shadowRoot.getElementById('back')?.addEventListener('click', () => { this._step = 'confirm'; this.render(); });
    this.shadowRoot.getElementById('go-home')?.addEventListener('click', () => window.location.href = '/');
    
    this.shadowRoot.getElementById('hard-delete-btn')?.addEventListener('click', () => {
      const input = this.shadowRoot.getElementById('confirmation-input');
      this.hardDelete(input?.value || '');
    });
  }

  renderConfirm() {
    return `
      <div class="icon">😢</div>
      <h1>Delete your account?</h1>
      <p>We're sorry to see you go. Before you leave:</p>
      
      <div class="warning">
        <p><strong>What happens when you delete:</strong></p>
        <p>• Your account will be deactivated</p>
        <p>• You have 30 days to recover it</p>
        <p>• After 30 days, data is permanently deleted</p>
      </div>
      
      <div class="actions">
        <button class="btn btn-danger" id="soft-delete" ${this._deleting ? 'disabled' : ''}>
          ${this._deleting ? 'Deleting...' : 'Delete my account'}
        </button>
        <button class="btn btn-secondary" id="cancel">Cancel</button>
      </div>
      
      <div class="footer">
        <span class="link" id="hard-delete-link">I want to permanently delete everything now</span>
      </div>
    `;
  }

  renderHardDelete() {
    return `
      <div class="icon">⚠️</div>
      <h1>Permanent deletion</h1>
      
      <div class="warning">
        <p><strong>This cannot be undone.</strong></p>
        <p>All your data will be immediately and permanently deleted. There is no recovery.</p>
      </div>
      
      <p>Type <strong>DELETE MY ACCOUNT</strong> to confirm:</p>
      <input type="text" id="confirmation-input" placeholder="DELETE MY ACCOUNT">
      
      <div class="actions">
        <button class="btn btn-danger" id="hard-delete-btn" ${this._deleting ? 'disabled' : ''}>
          ${this._deleting ? 'Deleting...' : 'Permanently delete everything'}
        </button>
        <button class="btn btn-secondary" id="back">Go back</button>
      </div>
    `;
  }

  renderDone() {
    return `
      <div class="icon">👋</div>
      <h1>Account deleted</h1>
      <p style="text-align: center;">Your account has been deleted. We hope to see you again someday.</p>
      
      <div class="actions">
        <button class="btn btn-secondary" id="go-home">Go to homepage</button>
      </div>
    `;
  }
}

customElements.define('delete-account-page', DeleteAccountPage);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelySettings = {
    SettingsPage,
    DeleteAccountPage,
  };
}
