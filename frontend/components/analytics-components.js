/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY ANALYTICS COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * User-facing analytics dashboards for writers and readers.
 * Privacy-focused: Shows only user's own data.
 */

const COLORS = {
  coral: '#FF6B6B',
  coralLight: 'rgba(255, 107, 107, 0.1)',
  softGold: '#D4A574',
  softGoldLight: 'rgba(212, 165, 116, 0.1)',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  bgDark: '#F8F5F0',
  border: '#E9ECEF',
  success: '#00B894',
};


// ═══════════════════════════════════════════════════════════════════════════
// WRITER ANALYTICS
// ═══════════════════════════════════════════════════════════════════════════

class WriterAnalytics extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._period = '30d';
    this._loading = true;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    this._loading = true;
    this.render();
    
    try {
      const response = await fetch(`/api/v2/analytics/me/writer?period=${this._period}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  setPeriod(period) {
    this._period = period;
    this.loadData();
  }

  render() {
    const d = this._data || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        h2 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0; }
        
        .period-selector { display: flex; gap: 0.5rem; }
        .period-btn {
          padding: 0.5rem 1rem;
          border: 1px solid ${COLORS.border};
          background: white;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          color: ${COLORS.muted};
        }
        .period-btn.active { border-color: ${COLORS.coral}; color: ${COLORS.coral}; background: ${COLORS.coralLight}; }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; text-align: center; }
        .stat-value { font-size: 2rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        .stat.highlight { border-color: ${COLORS.coral}; }
        .stat.highlight .stat-value { color: ${COLORS.coral}; }
        
        .chart-section { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.5rem; margin-bottom: 1.5rem; }
        .chart-title { font-size: 1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        .chart { height: 200px; display: flex; align-items: flex-end; gap: 2px; }
        .bar { background: ${COLORS.coral}; border-radius: 2px 2px 0 0; flex: 1; min-width: 4px; transition: height 0.3s; }
        .bar:hover { background: ${COLORS.coralDark}; }
        
        .streak-section { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.5rem; }
        .streak-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .streak-icon { font-size: 2.5rem; }
        .streak-info h3 { margin: 0; font-size: 1.1rem; color: ${COLORS.ink}; }
        .streak-info p { margin: 0.25rem 0 0 0; font-size: 0.9rem; color: ${COLORS.muted}; }
        
        .streak-history { display: flex; gap: 0.25rem; flex-wrap: wrap; }
        .streak-day { width: 16px; height: 16px; border-radius: 3px; background: ${COLORS.border}; }
        .streak-day.active { background: ${COLORS.coral}; }
        .streak-day.today { box-shadow: 0 0 0 2px ${COLORS.coral}; }
        
        .loading { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      ${this._loading ? '<div class="loading">Loading your analytics...</div>' : `
        <div class="header">
          <h2>📊 Your Writing Analytics</h2>
          <div class="period-selector">
            <button class="period-btn ${this._period === '30d' ? 'active' : ''}" data-period="30d">30 days</button>
            <button class="period-btn ${this._period === '90d' ? 'active' : ''}" data-period="90d">90 days</button>
            <button class="period-btn ${this._period === '365d' ? 'active' : ''}" data-period="365d">1 year</button>
          </div>
        </div>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${(d.total_words || 0).toLocaleString()}</div>
            <div class="stat-label">Total Words</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.total_analyses || 0}</div>
            <div class="stat-label">Analyses</div>
          </div>
          <div class="stat highlight">
            <div class="stat-value">${d.current_streak || 0}</div>
            <div class="stat-label">Current Streak</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.longest_streak || 0}</div>
            <div class="stat-label">Longest Streak</div>
          </div>
        </div>
        
        <div class="chart-section">
          <h3 class="chart-title">Words Over Time</h3>
          <div class="chart">
            ${this.renderChart(d.words_over_time || [])}
          </div>
        </div>
        
        <div class="streak-section">
          <div class="streak-header">
            <span class="streak-icon">${d.current_streak > 0 ? '🔥' : '💤'}</span>
            <div class="streak-info">
              <h3>${d.current_streak > 0 ? `${d.current_streak}-Day Streak!` : 'No Active Streak'}</h3>
              <p>${d.current_streak > 0 ? 'Keep it going!' : 'Write 1,000 words today to start a new streak'}</p>
            </div>
          </div>
          <div class="streak-history">
            ${this.renderStreakHistory(d.streak_history || [])}
          </div>
        </div>
      `}
    `;

    this.shadowRoot.querySelectorAll('.period-btn').forEach(btn => {
      btn.addEventListener('click', () => this.setPeriod(btn.dataset.period));
    });
  }

  renderChart(data) {
    if (!data.length) return '<div style="color: ' + COLORS.muted + '; text-align: center; width: 100%;">No data yet</div>';
    
    const max = Math.max(...data.map(d => d.words || 0), 1);
    return data.map(d => {
      const height = Math.max(4, (d.words / max) * 180);
      return `<div class="bar" style="height: ${height}px;" title="${d.date}: ${d.words} words"></div>`;
    }).join('');
  }

  renderStreakHistory(history) {
    // Show last 30 days
    const days = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const isActive = history.some(h => h.date === dateStr && h.met_goal);
      const isToday = i === 0;
      
      days.push(`<div class="streak-day ${isActive ? 'active' : ''} ${isToday ? 'today' : ''}" title="${dateStr}"></div>`);
    }
    
    return days.join('');
  }
}

customElements.define('writer-analytics', WriterAnalytics);


// ═══════════════════════════════════════════════════════════════════════════
// READER ANALYTICS
// ═══════════════════════════════════════════════════════════════════════════

class ReaderAnalytics extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._period = '30d';
    this._loading = true;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    this._loading = true;
    this.render();
    
    try {
      const response = await fetch(`/api/v2/analytics/me/reader?period=${this._period}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  setPeriod(period) {
    this._period = period;
    this.loadData();
  }

  render() {
    const d = this._data || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        h2 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0; }
        
        .period-selector { display: flex; gap: 0.5rem; }
        .period-btn {
          padding: 0.5rem 1rem;
          border: 1px solid ${COLORS.border};
          background: white;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.85rem;
          color: ${COLORS.muted};
        }
        .period-btn.active { border-color: ${COLORS.softGold}; color: ${COLORS.softGold}; background: ${COLORS.softGoldLight}; }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; text-align: center; }
        .stat-value { font-size: 2rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        .stat.highlight { border-color: ${COLORS.softGold}; }
        .stat.highlight .stat-value { color: ${COLORS.softGold}; }
        
        .profiles-section { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.5rem; }
        .profiles-title { font-size: 1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; }
        .profiles-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .profile-tag { padding: 0.4rem 0.8rem; background: ${COLORS.bgDark}; border-radius: 20px; font-size: 0.85rem; color: ${COLORS.ink}; }
        
        .loading { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      ${this._loading ? '<div class="loading">Loading your reading analytics...</div>' : `
        <div class="header">
          <h2>📖 Your Reading Analytics</h2>
          <div class="period-selector">
            <button class="period-btn ${this._period === '30d' ? 'active' : ''}" data-period="30d">30 days</button>
            <button class="period-btn ${this._period === '90d' ? 'active' : ''}" data-period="90d">90 days</button>
            <button class="period-btn ${this._period === '365d' ? 'active' : ''}" data-period="365d">1 year</button>
          </div>
        </div>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${d.total_posts_read || 0}</div>
            <div class="stat-label">Posts Read</div>
          </div>
          <div class="stat highlight">
            <div class="stat-value">${d.total_deep_reads || 0}</div>
            <div class="stat-label">Deep Reads</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.deep_read_ratio ? Math.round(d.deep_read_ratio * 100) : 0}%</div>
            <div class="stat-label">Deep Read Rate</div>
          </div>
          <div class="stat">
            <div class="stat-value">${(d.profiles_explored || []).length}</div>
            <div class="stat-label">Profiles Explored</div>
          </div>
        </div>
        
        <div class="profiles-section">
          <h3 class="profiles-title">Voice Profiles You've Explored</h3>
          <div class="profiles-list">
            ${(d.profiles_explored || []).map(p => `<span class="profile-tag">${p}</span>`).join('') || '<span style="color: ' + COLORS.muted + '">Start reading to discover voice profiles!</span>'}
          </div>
        </div>
      `}
    `;

    this.shadowRoot.querySelectorAll('.period-btn').forEach(btn => {
      btn.addEventListener('click', () => this.setPeriod(btn.dataset.period));
    });
  }
}

customElements.define('reader-analytics', ReaderAnalytics);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED ANALYTICS
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedAnalytics extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._loading = true;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/analytics/me/featured?period=30d', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  render() {
    const d = this._data || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        h2 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0 0 1.5rem 0; }
        
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .stat { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; text-align: center; }
        .stat-value { font-size: 2rem; font-weight: 700; color: ${COLORS.softGold}; }
        .stat-label { font-size: 0.85rem; color: ${COLORS.muted}; margin-top: 0.25rem; }
        
        .loading { text-align: center; padding: 3rem; color: ${COLORS.muted}; }
      </style>
      
      ${this._loading ? '<div class="loading">Loading...</div>' : `
        <h2>⭐ Your Featured Analytics (Last 30 Days)</h2>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${d.profile_views || 0}</div>
            <div class="stat-label">Profile Views</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.piece_engagement?.views || 0}</div>
            <div class="stat-label">Piece Views</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.path_follows || 0}</div>
            <div class="stat-label">Path Follows</div>
          </div>
        </div>
      `}
    `;
  }
}

customElements.define('featured-analytics', FeaturedAnalytics);


// ═══════════════════════════════════════════════════════════════════════════
// ANALYTICS SUMMARY CARD (for dashboard)
// ═══════════════════════════════════════════════════════════════════════════

class AnalyticsSummary extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
  }

  connectedCallback() { this.loadData(); }

  async loadData() {
    try {
      const response = await fetch('/api/v2/analytics/me/summary', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed:', err);
    }
    this.render();
  }

  render() {
    const d = this._data || {};

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .card { background: white; border: 1px solid ${COLORS.border}; border-radius: 10px; padding: 1.25rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        .title { font-size: 1rem; font-weight: 600; color: ${COLORS.ink}; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
        .view-all { font-size: 0.85rem; color: ${COLORS.coral}; text-decoration: none; }
        
        .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.75rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="card">
        <div class="header">
          <h3 class="title">📊 Your Progress</h3>
          <a href="/analytics" class="view-all">View details →</a>
        </div>
        
        <div class="stats">
          <div>
            <div class="stat-value">${(d.total_words || 0).toLocaleString()}</div>
            <div class="stat-label">Total words</div>
          </div>
          <div>
            <div class="stat-value">${d.current_streak || 0}🔥</div>
            <div class="stat-label">Current streak</div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('analytics-summary', AnalyticsSummary);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyAnalytics = {
    WriterAnalytics,
    ReaderAnalytics,
    FeaturedAnalytics,
    AnalyticsSummary,
  };
}
