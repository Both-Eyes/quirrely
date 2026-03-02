/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY SUPER ADMIN DASHBOARD v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * System Pulse and Prescriptive Actions for Super Admins.
 * Surfaces Master Test results with actionable recommendations.
 */

const COLORS = {
  coral: '#FF6B6B',
  softGold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  success: '#00B894',
  warning: '#FDCB6E',
  danger: '#E74C3C',
  purple: '#6C5CE7',
};


// ═══════════════════════════════════════════════════════════════════════════
// SYSTEM PULSE WIDGET (Top of Dashboard)
// ═══════════════════════════════════════════════════════════════════════════

class SystemPulse extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._loading = true;
    this._running = false;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    this._loading = true;
    this.render();

    try {
      const response = await fetch('/api/v2/super-admin/pulse', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load pulse:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  async runTest(quick = false) {
    this._running = true;
    this.render();

    try {
      await fetch('/api/v2/super-admin/run-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}`,
        },
        body: JSON.stringify({ quick }),
      });

      // Poll for completion
      const checkStatus = async () => {
        const res = await fetch('/api/v2/super-admin/test-status', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
        });
        const status = await res.json();
        
        if (!status.is_running) {
          this._running = false;
          this.loadData();
        } else {
          setTimeout(checkStatus, 2000);
        }
      };
      
      setTimeout(checkStatus, 2000);
    } catch (err) {
      console.error('Failed to run test:', err);
      this._running = false;
      this.render();
    }
  }

  render() {
    const d = this._data || {};
    const health = d.overall_health || 0;
    const breakdown = d.health_breakdown || {};
    const metrics = d.key_metrics || {};
    const actions = d.top_actions || [];

    // Health color
    const healthColor = health >= 70 ? COLORS.success : health >= 50 ? COLORS.warning : COLORS.danger;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .pulse-container {
          background: linear-gradient(135deg, ${COLORS.ink} 0%, #1a1a2e 100%);
          border-radius: 16px;
          padding: 2rem;
          color: white;
          margin-bottom: 2rem;
        }
        
        .pulse-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .pulse-title {
          font-size: 1.5rem;
          font-weight: 700;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        
        .pulse-icon { font-size: 1.75rem; }
        
        .refresh-btn {
          padding: 0.5rem 1rem;
          background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 8px;
          color: white;
          cursor: pointer;
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .refresh-btn:hover { background: rgba(255,255,255,0.2); }
        .refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .pulse-grid {
          display: grid;
          grid-template-columns: 200px 1fr 1fr;
          gap: 2rem;
          align-items: start;
        }
        @media (max-width: 900px) { .pulse-grid { grid-template-columns: 1fr; } }
        
        .health-ring {
          width: 160px;
          height: 160px;
          position: relative;
          margin: 0 auto;
        }
        .health-ring svg { transform: rotate(-90deg); }
        .health-ring-bg { fill: none; stroke: rgba(255,255,255,0.1); stroke-width: 12; }
        .health-ring-progress { fill: none; stroke: ${healthColor}; stroke-width: 12; stroke-linecap: round; transition: stroke-dashoffset 0.5s; }
        .health-value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
        }
        .health-number { font-size: 2.5rem; font-weight: 700; }
        .health-label { font-size: 0.85rem; opacity: 0.7; }
        
        .breakdown { display: flex; flex-direction: column; gap: 1rem; }
        .breakdown-item { display: flex; align-items: center; gap: 1rem; }
        .breakdown-label { width: 100px; font-size: 0.9rem; opacity: 0.8; }
        .breakdown-bar { flex: 1; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
        .breakdown-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
        .breakdown-value { width: 40px; text-align: right; font-size: 0.9rem; font-weight: 600; }
        
        .metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
        .metric { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 1rem; }
        .metric-value { font-size: 1.5rem; font-weight: 700; }
        .metric-label { font-size: 0.8rem; opacity: 0.7; margin-top: 0.25rem; }
        
        .actions-section { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); }
        .actions-title { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; }
        .action-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .action-item {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 0.75rem;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
        }
        .action-severity {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-top: 0.4rem;
          flex-shrink: 0;
        }
        .action-severity.opportunity { background: ${COLORS.success}; }
        .action-severity.watch { background: ${COLORS.warning}; }
        .action-severity.risk { background: ${COLORS.danger}; }
        .action-content { flex: 1; }
        .action-title { font-size: 0.9rem; font-weight: 500; margin-bottom: 0.25rem; }
        .action-rec { font-size: 0.8rem; opacity: 0.7; }
        
        .stale-warning {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: rgba(253, 203, 110, 0.2);
          border-radius: 8px;
          font-size: 0.85rem;
          margin-bottom: 1rem;
        }
        
        .loading { text-align: center; padding: 3rem; opacity: 0.7; }
      </style>
      
      <div class="pulse-container">
        ${this._loading ? '<div class="loading">Loading system pulse...</div>' : `
          <div class="pulse-header">
            <h2 class="pulse-title">
              <span class="pulse-icon">💓</span>
              System Pulse
            </h2>
            <button class="refresh-btn" id="refresh-btn" ${this._running ? 'disabled' : ''}>
              ${this._running ? '⏳ Running...' : '🔄 Refresh Test'}
            </button>
          </div>
          
          ${d.is_stale ? `
            <div class="stale-warning">
              ⚠️ Results are over 24 hours old. Consider running a fresh test.
            </div>
          ` : ''}
          
          <div class="pulse-grid">
            <div class="health-ring">
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle class="health-ring-bg" cx="80" cy="80" r="70" />
                <circle 
                  class="health-ring-progress" 
                  cx="80" cy="80" r="70"
                  stroke-dasharray="${2 * Math.PI * 70}"
                  stroke-dashoffset="${2 * Math.PI * 70 * (1 - health / 100)}"
                />
              </svg>
              <div class="health-value">
                <div class="health-number">${health}</div>
                <div class="health-label">Health</div>
              </div>
            </div>
            
            <div class="breakdown">
              <div class="breakdown-item">
                <span class="breakdown-label">Conversion</span>
                <div class="breakdown-bar">
                  <div class="breakdown-fill" style="width: ${breakdown.conversion || 0}%; background: ${COLORS.coral};"></div>
                </div>
                <span class="breakdown-value">${breakdown.conversion || 0}%</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">Value</span>
                <div class="breakdown-bar">
                  <div class="breakdown-fill" style="width: ${breakdown.value || 0}%; background: ${COLORS.softGold};"></div>
                </div>
                <span class="breakdown-value">${breakdown.value || 0}%</span>
              </div>
              <div class="breakdown-item">
                <span class="breakdown-label">Retention</span>
                <div class="breakdown-bar">
                  <div class="breakdown-fill" style="width: ${breakdown.retention || 0}%; background: ${COLORS.success};"></div>
                </div>
                <span class="breakdown-value">${breakdown.retention || 0}%</span>
              </div>
            </div>
            
            <div class="metrics">
              <div class="metric">
                <div class="metric-value">${(metrics.total_users || 0).toLocaleString()}</div>
                <div class="metric-label">Simulated Users</div>
              </div>
              <div class="metric">
                <div class="metric-value">${(metrics.avg_value || 0).toFixed(2)}</div>
                <div class="metric-label">Avg Token Value</div>
              </div>
              <div class="metric">
                <div class="metric-value">${((metrics.trial_conversion || 0) * 100).toFixed(1)}%</div>
                <div class="metric-label">Trial Conversion</div>
              </div>
              <div class="metric">
                <div class="metric-value">${((metrics.churn_rate || 0) * 100).toFixed(1)}%</div>
                <div class="metric-label">Churn Rate</div>
              </div>
            </div>
          </div>
          
          ${actions.length ? `
            <div class="actions-section">
              <h3 class="actions-title">Top Actions</h3>
              <div class="action-list">
                ${actions.map(a => `
                  <div class="action-item">
                    <div class="action-severity ${a.severity}"></div>
                    <div class="action-content">
                      <div class="action-title">${a.title}</div>
                      <div class="action-rec">→ ${a.action}</div>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
        `}
      </div>
    `;

    this.shadowRoot.getElementById('refresh-btn')?.addEventListener('click', () => {
      this.runTest(false);
    });
  }
}

customElements.define('system-pulse', SystemPulse);


// ═══════════════════════════════════════════════════════════════════════════
// PRESCRIPTIVE ACTIONS LIST
// ═══════════════════════════════════════════════════════════════════════════

class PrescriptiveActions extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._filter = 'all';
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/super-admin/actions', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_admin_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load actions:', err);
    }
    this.render();
  }

  setFilter(filter) {
    this._filter = filter;
    this.render();
  }

  render() {
    const d = this._data || {};
    const allActions = d.actions || [];
    const bySeverity = d.by_severity || {};
    
    let actions = allActions;
    if (this._filter !== 'all') {
      actions = allActions.filter(a => a.severity === this._filter);
    }

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        h2 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0; }
        
        .filters { display: flex; gap: 0.5rem; }
        .filter-btn {
          padding: 0.5rem 1rem;
          border: 1px solid ${COLORS.border};
          background: white;
          border-radius: 8px;
          cursor: pointer;
          font-size: 0.85rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        .filter-btn.active { background: ${COLORS.ink}; color: white; border-color: ${COLORS.ink}; }
        .filter-count { font-weight: 600; }
        
        .actions-list { display: flex; flex-direction: column; gap: 1rem; }
        
        .action-card {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 12px;
          padding: 1.25rem;
          border-left: 4px solid;
        }
        .action-card.opportunity { border-left-color: ${COLORS.success}; }
        .action-card.watch { border-left-color: ${COLORS.warning}; }
        .action-card.risk { border-left-color: ${COLORS.danger}; }
        
        .action-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
        .action-title { font-size: 1rem; font-weight: 600; color: ${COLORS.ink}; margin: 0; }
        .action-category { font-size: 0.75rem; padding: 0.2rem 0.5rem; background: ${COLORS.bgDark}; border-radius: 4px; color: ${COLORS.muted}; }
        
        .action-description { font-size: 0.9rem; color: ${COLORS.muted}; margin-bottom: 1rem; }
        
        .action-metrics { display: flex; gap: 1.5rem; margin-bottom: 1rem; font-size: 0.85rem; }
        .metric-item { display: flex; flex-direction: column; }
        .metric-label { color: ${COLORS.muted}; font-size: 0.75rem; }
        .metric-value { font-weight: 600; color: ${COLORS.ink}; }
        .metric-value.positive { color: ${COLORS.success}; }
        .metric-value.negative { color: ${COLORS.danger}; }
        
        .action-recommendation {
          padding: 0.75rem 1rem;
          background: ${COLORS.bg};
          border-radius: 8px;
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
        }
        .rec-icon { font-size: 1.25rem; }
        .rec-content { flex: 1; }
        .rec-text { font-size: 0.9rem; color: ${COLORS.ink}; margin-bottom: 0.25rem; }
        .rec-meta { font-size: 0.8rem; color: ${COLORS.muted}; }
        
        .empty { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="header">
        <h2>Prescriptive Actions</h2>
        <div class="filters">
          <button class="filter-btn ${this._filter === 'all' ? 'active' : ''}" data-filter="all">
            All <span class="filter-count">${d.total || 0}</span>
          </button>
          <button class="filter-btn ${this._filter === 'risk' ? 'active' : ''}" data-filter="risk">
            🔴 Risks <span class="filter-count">${bySeverity.risk || 0}</span>
          </button>
          <button class="filter-btn ${this._filter === 'watch' ? 'active' : ''}" data-filter="watch">
            🟡 Watch <span class="filter-count">${bySeverity.watch || 0}</span>
          </button>
          <button class="filter-btn ${this._filter === 'opportunity' ? 'active' : ''}" data-filter="opportunity">
            🟢 Opps <span class="filter-count">${bySeverity.opportunity || 0}</span>
          </button>
        </div>
      </div>
      
      <div class="actions-list">
        ${actions.length ? actions.map(a => `
          <div class="action-card ${a.severity}">
            <div class="action-header">
              <h3 class="action-title">${a.title}</h3>
              <span class="action-category">${a.category}</span>
            </div>
            
            <p class="action-description">${a.description}</p>
            
            <div class="action-metrics">
              <div class="metric-item">
                <span class="metric-label">Current</span>
                <span class="metric-value">${typeof a.current_value === 'number' ? (a.current_value < 1 ? (a.current_value * 100).toFixed(1) + '%' : a.current_value.toFixed(2)) : a.current_value}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Baseline</span>
                <span class="metric-value">${typeof a.baseline_value === 'number' ? (a.baseline_value < 1 ? (a.baseline_value * 100).toFixed(1) + '%' : a.baseline_value.toFixed(2)) : a.baseline_value}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Delta</span>
                <span class="metric-value ${a.delta_percent > 0 ? 'positive' : 'negative'}">${a.delta_percent > 0 ? '+' : ''}${a.delta_percent.toFixed(1)}%</span>
              </div>
              ${a.country_code ? `<div class="metric-item"><span class="metric-label">Country</span><span class="metric-value">${a.country_code.toUpperCase()}</span></div>` : ''}
            </div>
            
            <div class="action-recommendation">
              <span class="rec-icon">💡</span>
              <div class="rec-content">
                <div class="rec-text">${a.action_recommended}</div>
                <div class="rec-meta">Impact: ${a.action_impact} • Effort: ${a.action_effort}</div>
              </div>
            </div>
          </div>
        `).join('') : '<div class="empty">No actions to display</div>'}
      </div>
    `;

    this.shadowRoot.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => this.setFilter(btn.dataset.filter));
    });
  }
}

customElements.define('prescriptive-actions', PrescriptiveActions);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrleySuperAdmin = {
    SystemPulse,
    PrescriptiveActions,
  };
}
