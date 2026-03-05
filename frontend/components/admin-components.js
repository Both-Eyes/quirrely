/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY ADMIN COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Admin panel components for user management, Featured review, and monitoring.
 * URL: /admin
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
  danger: '#E74C3C',
  admin: '#6C5CE7',
};


// ═══════════════════════════════════════════════════════════════════════════
// ADMIN LAYOUT
// ═══════════════════════════════════════════════════════════════════════════

class AdminLayout extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._admin = null;
    this._sections = [];
    this._activeSection = 'overview';
    this._loading = true;
  }

  connectedCallback() { this.loadAdminInfo(); }

  async loadAdminInfo() {
    try {
      const response = await fetch('/api/v2/admin/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      
      if (!response.ok) {
        window.location.href = '/admin/login';
        return;
      }
      
      const data = await response.json();
      this._admin = data.admin;
      this._sections = data.sections;
    } catch (err) {
      console.error('Failed to load admin info:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  setSection(section) {
    this._activeSection = section;
    this.render();
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: ${COLORS.ink}; color: white;">
          Loading admin panel...
        </div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; min-height: 100vh; background: ${COLORS.bgDark}; }
        
        .layout { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
        @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
        
        .sidebar {
          background: ${COLORS.ink};
          color: white;
          padding: 1.5rem;
          position: sticky;
          top: 0;
          height: 100vh;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }
        @media (max-width: 900px) { .sidebar { display: none; } }
        
        .logo { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .admin-badge { 
          display: inline-block;
          padding: 0.25rem 0.5rem;
          background: ${COLORS.admin};
          border-radius: 4px;
          font-size: 0.7rem;
          text-transform: uppercase;
          margin-bottom: 2rem;
        }
        
        .nav { display: flex; flex-direction: column; gap: 0.25rem; }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          border-radius: 8px;
          color: rgba(255,255,255,0.7);
          cursor: pointer;
          transition: all 0.2s;
          text-decoration: none;
        }
        .nav-item:hover { background: rgba(255,255,255,0.1); color: white; }
        .nav-item.active { background: ${COLORS.admin}; color: white; }
        .nav-icon { font-size: 1.1rem; }
        
        .admin-info {
          margin-top: auto;
          padding-top: 2rem;
          border-top: 1px solid rgba(255,255,255,0.1);
        }
        .admin-email { font-size: 0.85rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem; }
        .logout-btn {
          padding: 0.5rem 1rem;
          background: rgba(255,255,255,0.1);
          border: none;
          border-radius: 6px;
          color: white;
          cursor: pointer;
          font-size: 0.85rem;
          width: 100%;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.2); }
        
        .main { padding: 2rem; }
        .main-header { margin-bottom: 2rem; }
        .main-title { font-size: 1.5rem; color: ${COLORS.ink}; margin: 0; }
      </style>
      
      <div class="layout">
        <aside class="sidebar">
          <div class="logo">🐿️ Quirrely</div>
          <div class="admin-badge">${this._admin?.role || 'Admin'}</div>
          
          <nav class="nav">
            ${this._sections.map(s => `
              <a class="nav-item ${this._activeSection === s.id ? 'active' : ''}" data-section="${s.id}">
                <span class="nav-icon">${s.icon}</span>
                ${s.label}
              </a>
            `).join('')}
          </nav>
          
          <div class="admin-info">
            <div class="admin-email">${this._admin?.email || ''}</div>
            <button class="logout-btn" id="logout-btn">Logout</button>
          </div>
        </aside>
        
        <main class="main">
          <div class="main-header">
            <h1 class="main-title">${this._sections.find(s => s.id === this._activeSection)?.label || 'Admin'}</h1>
          </div>
          
          <div id="section-content"></div>
        </main>
      </div>
    `;

    const content = this.shadowRoot.getElementById('section-content');
    content.innerHTML = this.renderSection(this._activeSection);

    this.shadowRoot.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        this.setSection(item.dataset.section);
      });
    });

    this.shadowRoot.getElementById('logout-btn')?.addEventListener('click', () => {
      localStorage.removeItem('quirrely_admin_token');
      window.location.href = '/admin/login';
    });
  }

  renderSection(section) {
    switch (section) {
      case 'overview': return '<admin-overview></admin-overview>';
      case 'users': return '<admin-users></admin-users>';
      case 'subscriptions': return '<admin-subscriptions></admin-subscriptions>';
      case 'featured': return '<admin-featured-queue></admin-featured-queue>';
      case 'content': return '<admin-content></admin-content>';
      case 'system': return '<admin-system></admin-system>';
      default: return '<p>Section not found</p>';
    }
  }
}

customElements.define('admin-layout', AdminLayout);


// ═══════════════════════════════════════════════════════════════════════════
// OVERVIEW SECTION
// ═══════════════════════════════════════════════════════════════════════════

class AdminOverview extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/admin/overview', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load overview:', err);
    }
    this.render();
  }

  render() {
    const m = this._data?.metrics || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .metric { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; }
        .metric-value { font-size: 2rem; font-weight: 700; color: ${COLORS.ink}; }
        .metric-label { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        .metric.highlight { border-color: ${COLORS.admin}; }
        .metric.highlight .metric-value { color: ${COLORS.admin}; }
        
        .section-title { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        
        .activity-list { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; }
        .activity-item { padding: 1rem; border-bottom: 1px solid ${COLORS.border}; display: flex; align-items: center; gap: 1rem; }
        .activity-item:last-child { border-bottom: none; }
        .activity-icon { font-size: 1.25rem; }
        .activity-text { flex: 1; font-size: 0.9rem; color: ${COLORS.ink}; }
        .activity-time { font-size: 0.8rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="metrics">
        <div class="metric">
          <div class="metric-value">${m.total_users?.toLocaleString() || 0}</div>
          <div class="metric-label">Total Users</div>
        </div>
        <div class="metric">
          <div class="metric-value">${m.active_subscriptions?.toLocaleString() || 0}</div>
          <div class="metric-label">Active Subscriptions</div>
        </div>
        <div class="metric">
          <div class="metric-value">$${m.mrr?.toLocaleString() || 0}</div>
          <div class="metric-label">MRR (CAD)</div>
        </div>
        <div class="metric">
          <div class="metric-value">${m.active_trials || 0}</div>
          <div class="metric-label">Active Trials</div>
        </div>
        <div class="metric highlight">
          <div class="metric-value">${m.pending_submissions || 0}</div>
          <div class="metric-label">Pending Reviews</div>
        </div>
        <div class="metric ${m.pending_escalations > 0 ? 'highlight' : ''}">
          <div class="metric-value">${m.pending_escalations || 0}</div>
          <div class="metric-label">Escalations</div>
        </div>
        <div class="metric">
          <div class="metric-value">${m.signups_today || 0}</div>
          <div class="metric-label">Signups Today</div>
        </div>
        <div class="metric">
          <div class="metric-value">${(m.words_today || 0).toLocaleString()}</div>
          <div class="metric-label">Words Today</div>
        </div>
      </div>
      
      <h2 class="section-title">Recent Activity</h2>
      <div class="activity-list">
        ${(this._data?.recent_activity || []).map(a => `
          <div class="activity-item">
            <span class="activity-icon">${a.type === 'signup' ? '👤' : a.type === 'subscription' ? '💳' : '📝'}</span>
            <span class="activity-text">${a.user} ${a.type === 'subscription' ? `subscribed to ${a.tier}` : 'signed up'}</span>
            <span class="activity-time">Just now</span>
          </div>
        `).join('') || '<div class="activity-item"><span class="activity-text" style="color: ' + COLORS.muted + '">No recent activity</span></div>'}
      </div>
    `;
  }
}

customElements.define('admin-overview', AdminOverview);


// ═══════════════════════════════════════════════════════════════════════════
// USERS SECTION
// ═══════════════════════════════════════════════════════════════════════════

class AdminUsers extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._users = [];
    this._total = 0;
    this._page = 1;
    this._search = '';
    this._tierFilter = '';
  }

  connectedCallback() { this.loadUsers(); }

  async loadUsers() {
    try {
      const params = new URLSearchParams({
        page: this._page,
        per_page: 20,
        ...(this._search && { search: this._search }),
        ...(this._tierFilter && { tier: this._tierFilter }),
      });
      
      const response = await fetch(`/api/v2/admin/users?${params}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      const data = await response.json();
      this._users = data.users;
      this._total = data.total;
    } catch (err) {
      console.error('Failed to load users:', err);
    }
    this.render();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .filters { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
        .search-input { flex: 1; min-width: 200px; padding: 0.75rem 1rem; border: 1px solid ${COLORS.border}; border-radius: 8px; font-size: 0.95rem; }
        select { padding: 0.75rem 1rem; border: 1px solid ${COLORS.border}; border-radius: 8px; background: white; font-size: 0.95rem; }
        
        .users-table { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; overflow: hidden; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 1rem; background: ${COLORS.bgDark}; font-size: 0.85rem; color: ${COLORS.muted}; font-weight: 500; }
        td { padding: 1rem; border-top: 1px solid ${COLORS.border}; font-size: 0.9rem; }
        tr:hover td { background: ${COLORS.bg}; }
        
        .tier-badge { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
        .tier-free { background: ${COLORS.border}; color: ${COLORS.muted}; }
        .tier-trial { background: rgba(253, 203, 110, 0.3); color: #D68910; }
        .tier-pro { background: rgba(108, 92, 231, 0.2); color: ${COLORS.admin}; }
        .tier-curator { background: rgba(212, 165, 116, 0.3); color: #8B6914; }
        .tier-bundle { background: rgba(0, 184, 148, 0.2); color: ${COLORS.success}; }
        
        .actions-btn { padding: 0.4rem 0.75rem; background: ${COLORS.bgDark}; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
        .actions-btn:hover { background: ${COLORS.border}; }
        
        .pagination { display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; }
        .page-info { font-size: 0.9rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="filters">
        <input type="text" class="search-input" placeholder="Search by email..." id="search-input" value="${this._search}">
        <select id="tier-filter">
          <option value="">All tiers</option>
          <option value="free" ${this._tierFilter === 'free' ? 'selected' : ''}>Free</option>
          <option value="trial" ${this._tierFilter === 'trial' ? 'selected' : ''}>Trial</option>
          <option value="pro" ${this._tierFilter === 'pro' ? 'selected' : ''}>PRO</option>
          <option value="curator" ${this._tierFilter === 'curator' ? 'selected' : ''}>Curator</option>
          <option value="bundle" ${this._tierFilter === 'bundle' ? 'selected' : ''}>Bundle</option>
        </select>
      </div>
      
      <div class="users-table">
        <table>
          <thead><tr><th>Email</th><th>Tier</th><th>Status</th><th>Joined</th><th>Actions</th></tr></thead>
          <tbody>
            ${this._users.length ? this._users.map(u => `
              <tr>
                <td style="font-weight: 500;">${u.email || 'N/A'}</td>
                <td><span class="tier-badge tier-${u.tier || 'free'}">${u.tier || 'free'}</span></td>
                <td style="color: ${u.status === 'suspended' ? COLORS.danger : COLORS.success};">${u.status || 'active'}</td>
                <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}</td>
                <td><button class="actions-btn" data-user-id="${u.id}">View</button></td>
              </tr>
            `).join('') : '<tr><td colspan="5" style="text-align: center; color: ' + COLORS.muted + ';">No users found</td></tr>'}
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
        <span class="page-info">Showing ${this._users.length} of ${this._total} users</span>
      </div>
    `;

    let searchTimeout;
    this.shadowRoot.getElementById('search-input')?.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => { this._search = e.target.value; this._page = 1; this.loadUsers(); }, 300);
    });

    this.shadowRoot.getElementById('tier-filter')?.addEventListener('change', (e) => {
      this._tierFilter = e.target.value; this._page = 1; this.loadUsers();
    });
  }
}

customElements.define('admin-users', AdminUsers);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED QUEUE
// ═══════════════════════════════════════════════════════════════════════════

class AdminFeaturedQueue extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._submissions = [];
  }

  connectedCallback() { this.loadQueue(); }

  async loadQueue() {
    try {
      const response = await fetch('/api/v2/admin/featured/queue', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      const data = await response.json();
      this._submissions = data.submissions;
    } catch (err) {
      console.error('Failed to load queue:', err);
    }
    this.render();
  }

  async reviewSubmission(submissionId, action, feedback, rejectionReason) {
    try {
      await fetch(`/api/v2/admin/featured/${submissionId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
        body: JSON.stringify({ action, feedback, rejection_reason: rejectionReason }),
      });
      this.loadQueue();
    } catch (err) {
      console.error('Failed to review:', err);
    }
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .stats { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
        .stat { padding: 1rem; background: white; border: 1px solid ${COLORS.border}; border-radius: 8px; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.8rem; color: ${COLORS.muted}; }
        
        .submissions { display: flex; flex-direction: column; gap: 1rem; }
        .submission { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.5rem; }
        .submission.escalated { border-color: ${COLORS.warning}; }
        .submission-header { display: flex; justify-content: space-between; margin-bottom: 1rem; }
        .submission-user { font-weight: 600; color: ${COLORS.ink}; }
        .submission-meta { font-size: 0.85rem; color: ${COLORS.muted}; }
        .escalated-badge { display: inline-block; padding: 0.2rem 0.5rem; background: ${COLORS.warning}; color: white; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem; }
        .submission-content { padding: 1rem; background: ${COLORS.bgDark}; border-radius: 8px; margin-bottom: 1rem; font-size: 0.9rem; line-height: 1.6; }
        
        .actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 6px; font-size: 0.9rem; cursor: pointer; font-weight: 500; }
        .btn-approve { background: ${COLORS.success}; color: white; }
        .btn-reject { background: ${COLORS.danger}; color: white; }
        .btn-changes { background: ${COLORS.warning}; color: white; }
        .btn-escalate { background: ${COLORS.admin}; color: white; }
        
        .empty { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="stats">
        <div class="stat"><div class="stat-value">${this._submissions.filter(s => s.status === 'pending').length}</div><div class="stat-label">Pending</div></div>
        <div class="stat"><div class="stat-value">${this._submissions.filter(s => s.escalated).length}</div><div class="stat-label">Escalated</div></div>
      </div>
      
      <div class="submissions">
        ${this._submissions.length ? this._submissions.map(s => `
          <div class="submission ${s.escalated ? 'escalated' : ''}" data-id="${s.id}">
            <div class="submission-header">
              <div>
                <span class="submission-user">${s.user_display_name || s.user_email}</span>
                ${s.escalated ? '<span class="escalated-badge">Escalated</span>' : ''}
                <div class="submission-meta">${s.submission_type} • ${new Date(s.submitted_at).toLocaleDateString()}</div>
              </div>
            </div>
            <div class="submission-content">${s.content?.preview || s.content?.text?.substring(0, 500) || 'No preview'}...</div>
            <div class="actions">
              <button class="btn btn-approve" data-action="approve">✓ Approve</button>
              <button class="btn btn-reject" data-action="reject">✗ Reject</button>
              <button class="btn btn-changes" data-action="request_changes">Request Changes</button>
              ${!s.escalated ? '<button class="btn btn-escalate" data-action="escalate">↑ Escalate</button>' : ''}
            </div>
          </div>
        `).join('') : '<div class="empty">🎉 No pending submissions!</div>'}
      </div>
    `;

    this.shadowRoot.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = e.target.closest('.submission').dataset.id;
        const action = e.target.dataset.action;
        
        if (action === 'approve' && confirm('Approve?')) {
          this.reviewSubmission(id, action, 'Approved');
        } else if (action === 'reject') {
          const reason = prompt('Rejection reason:');
          if (reason) this.reviewSubmission(id, action, reason, reason);
        } else if (action === 'request_changes') {
          const feedback = prompt('What changes?');
          if (feedback) this.reviewSubmission(id, action, feedback);
        } else if (action === 'escalate') {
          const reason = prompt('Escalation reason:');
          if (reason) this.reviewSubmission(id, action, reason);
        }
      });
    });
  }
}

customElements.define('admin-featured-queue', AdminFeaturedQueue);


// ═══════════════════════════════════════════════════════════════════════════
// SUBSCRIPTIONS SECTION
// ═══════════════════════════════════════════════════════════════════════════

class AdminSubscriptions extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/admin/subscriptions', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      this._data = await response.json();
    } catch (err) { console.error('Failed:', err); }
    this.render();
  }

  render() {
    const m = this._data?.metrics || {};
    const byCurrency = this._data?.by_currency || {};
    const flags = { cad: '🇨🇦', gbp: '🇬🇧', eur: '🇪🇺', aud: '🇦🇺', nzd: '🇳🇿' };

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .metric { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; }
        .metric-value { font-size: 1.75rem; font-weight: 700; color: ${COLORS.ink}; }
        .metric-label { font-size: 0.85rem; color: ${COLORS.muted}; }
        .section-title { font-size: 1.1rem; color: ${COLORS.ink}; margin: 2rem 0 1rem 0; }
        .currency-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem; }
        .currency-card { background: white; border: 1px solid ${COLORS.border}; border-radius: 8px; padding: 1rem; text-align: center; }
        .currency-flag { font-size: 2rem; margin-bottom: 0.5rem; }
        .currency-count { font-size: 1.25rem; font-weight: 600; color: ${COLORS.ink}; }
        .currency-mrr { font-size: 0.85rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="metrics">
        <div class="metric"><div class="metric-value">$${m.total_mrr?.toLocaleString() || 0}</div><div class="metric-label">MRR (CAD)</div></div>
        <div class="metric"><div class="metric-value">$${m.total_arr?.toLocaleString() || 0}</div><div class="metric-label">ARR (CAD)</div></div>
        <div class="metric"><div class="metric-value">${m.pro_subscribers || 0}</div><div class="metric-label">PRO</div></div>
        <div class="metric"><div class="metric-value">${m.curator_subscribers || 0}</div><div class="metric-label">Curator</div></div>
        <div class="metric"><div class="metric-value">${m.bundle_subscribers || 0}</div><div class="metric-label">Bundle</div></div>
        <div class="metric"><div class="metric-value">${m.trial_conversion_rate || 0}%</div><div class="metric-label">Conversion</div></div>
        <div class="metric"><div class="metric-value">${m.churn_rate || 0}%</div><div class="metric-label">Churn</div></div>
      </div>
      
      <h2 class="section-title">By Currency</h2>
      <div class="currency-grid">
        ${Object.entries(byCurrency).map(([code, data]) => `
          <div class="currency-card">
            <div class="currency-flag">${flags[code] || '💰'}</div>
            <div class="currency-count">${data.count}</div>
            <div class="currency-mrr">${code.toUpperCase()} ${data.mrr?.toFixed(2)}/mo</div>
          </div>
        `).join('')}
      </div>
    `;
  }
}

customElements.define('admin-subscriptions', AdminSubscriptions);


// ═══════════════════════════════════════════════════════════════════════════
// SYSTEM SECTION
// ═══════════════════════════════════════════════════════════════════════════

class AdminSystem extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/admin/system', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      this._data = await response.json();
    } catch (err) { console.error('Failed:', err); }
    this.render();
  }

  render() {
    const services = this._data?.services || {};
    const resources = this._data?.resources || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .status-banner { padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 2rem; display: flex; align-items: center; gap: 1rem; }
        .status-healthy { background: rgba(0, 184, 148, 0.1); border: 1px solid ${COLORS.success}; }
        .status-unhealthy { background: rgba(231, 76, 60, 0.1); border: 1px solid ${COLORS.danger}; }
        .status-icon { font-size: 1.5rem; }
        .status-text { font-size: 1.1rem; font-weight: 600; color: ${COLORS.ink}; }
        
        .section-title { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        
        .services { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .service { background: white; border: 1px solid ${COLORS.border}; border-radius: 8px; padding: 1rem; display: flex; align-items: center; gap: 0.75rem; }
        .service-status { width: 12px; height: 12px; border-radius: 50%; }
        .service-status.up { background: ${COLORS.success}; }
        .service-status.down { background: ${COLORS.danger}; }
        .service-name { font-weight: 500; color: ${COLORS.ink}; }
        .service-latency { font-size: 0.8rem; color: ${COLORS.muted}; margin-left: auto; }
        
        .resources { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .resource { background: white; border: 1px solid ${COLORS.border}; border-radius: 8px; padding: 1rem; }
        .resource-label { font-size: 0.85rem; color: ${COLORS.muted}; margin-bottom: 0.5rem; }
        .resource-bar { height: 8px; background: ${COLORS.border}; border-radius: 4px; overflow: hidden; }
        .resource-fill { height: 100%; background: ${COLORS.success}; }
        .resource-fill.warning { background: ${COLORS.warning}; }
        .resource-fill.danger { background: ${COLORS.danger}; }
        .resource-value { font-size: 0.8rem; color: ${COLORS.muted}; margin-top: 0.25rem; text-align: right; }
      </style>
      
      <div class="status-banner status-${this._data?.status === 'healthy' ? 'healthy' : 'unhealthy'}">
        <span class="status-icon">${this._data?.status === 'healthy' ? '✅' : '⚠️'}</span>
        <span class="status-text">System ${this._data?.status || 'Unknown'}</span>
      </div>
      
      <h2 class="section-title">Services</h2>
      <div class="services">
        ${Object.entries(services).map(([name, info]) => `
          <div class="service">
            <div class="service-status ${info.status}"></div>
            <span class="service-name">${name}</span>
            ${info.latency_ms ? `<span class="service-latency">${info.latency_ms}ms</span>` : ''}
          </div>
        `).join('')}
      </div>
      
      <h2 class="section-title">Resources</h2>
      <div class="resources">
        <div class="resource">
          <div class="resource-label">CPU</div>
          <div class="resource-bar"><div class="resource-fill ${resources.cpu_percent > 80 ? 'danger' : resources.cpu_percent > 60 ? 'warning' : ''}" style="width: ${resources.cpu_percent || 0}%"></div></div>
          <div class="resource-value">${resources.cpu_percent || 0}%</div>
        </div>
        <div class="resource">
          <div class="resource-label">Memory</div>
          <div class="resource-bar"><div class="resource-fill ${resources.memory_percent > 80 ? 'danger' : resources.memory_percent > 60 ? 'warning' : ''}" style="width: ${resources.memory_percent || 0}%"></div></div>
          <div class="resource-value">${resources.memory_percent || 0}%</div>
        </div>
        <div class="resource">
          <div class="resource-label">Disk</div>
          <div class="resource-bar"><div class="resource-fill ${resources.disk_percent > 80 ? 'danger' : resources.disk_percent > 60 ? 'warning' : ''}" style="width: ${resources.disk_percent || 0}%"></div></div>
          <div class="resource-value">${resources.disk_percent || 0}%</div>
        </div>
      </div>
    `;
  }
}

customElements.define('admin-system', AdminSystem);


// ═══════════════════════════════════════════════════════════════════════════
// CONTENT SECTION (Placeholder)
// ═══════════════════════════════════════════════════════════════════════════

class AdminContent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .placeholder { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      <div class="placeholder">
        <p>📝 Content management coming soon</p>
        <p>Blog posts, Featured pieces, etc.</p>
      </div>
    `;
  }
}

customElements.define('admin-content', AdminContent);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyAdmin = {
    AdminLayout, AdminOverview, AdminUsers, AdminFeaturedQueue,
    AdminSubscriptions, AdminSystem, AdminContent,
  };
}
