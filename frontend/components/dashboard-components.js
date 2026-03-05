/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY DASHBOARD COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Dashboard sections for writers and readers.
 * Responsive, single-page layout with empty states.
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


// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD PAGE
// ═══════════════════════════════════════════════════════════════════════════

class DashboardPage extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._data = null;
    this._loading = true;
  }

  connectedCallback() {
    this.loadDashboard();
  }

  async loadDashboard() {
    try {
      const response = await fetch('/api/v2/dashboard/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}`,
        },
      });
      this._data = await response.json();
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      this._loading = false;
      this.render();
    }
  }

  render() {
    if (this._loading) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 4rem; color: ${COLORS.muted};">
          Loading your dashboard...
        </div>
      `;
      return;
    }

    const data = this._data || {};
    const hasWriter = data.has_writer_features;
    const hasReader = data.has_reader_features;
    const isBundle = hasWriter && hasReader;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; background: ${COLORS.bg}; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .header { margin-bottom: 2rem; }
        h1 { font-size: 1.75rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .subtitle { color: ${COLORS.muted}; margin: 0; }
        
        .quick-actions { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
        .quick-action {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 8px;
          text-decoration: none;
          color: ${COLORS.ink};
          font-size: 0.9rem;
          transition: border-color 0.2s;
        }
        .quick-action:hover { border-color: ${COLORS.coral}; }
        .quick-action.high { border-color: ${COLORS.coral}; background: rgba(255, 107, 107, 0.05); }
        .quick-action-icon { font-size: 1.25rem; }
        
        .sections { display: flex; flex-direction: column; gap: 2rem; }
        
        ${isBundle ? `
          .dual-view { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
          @media (max-width: 900px) { .dual-view { grid-template-columns: 1fr; } }
          .view-section { }
          .view-title { font-size: 1.1rem; color: ${COLORS.ink}; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; }
        ` : ''}
      </style>
      
      <div class="container">
        <div class="header">
          <h1>Welcome back 🐿️</h1>
          <p class="subtitle">Your ${isBundle ? 'voice and taste' : hasWriter ? 'writing' : 'reading'} at a glance</p>
        </div>
        
        <div class="quick-actions" id="quick-actions"></div>
        
        ${isBundle ? `
          <div class="dual-view">
            <div class="view-section">
              <h2 class="view-title">✍️ Writing</h2>
              <div class="sections" id="writer-sections"></div>
            </div>
            <div class="view-section">
              <h2 class="view-title">📖 Reading</h2>
              <div class="sections" id="reader-sections"></div>
            </div>
          </div>
        ` : `
          <div class="sections" id="main-sections"></div>
        `}
      </div>
    `;

    this.renderQuickActions();
    
    if (isBundle) {
      this.renderWriterSections(this.shadowRoot.getElementById('writer-sections'));
      this.renderReaderSections(this.shadowRoot.getElementById('reader-sections'));
    } else if (hasWriter) {
      this.renderWriterSections(this.shadowRoot.getElementById('main-sections'));
    } else if (hasReader) {
      this.renderReaderSections(this.shadowRoot.getElementById('main-sections'));
    }
  }

  async renderQuickActions() {
    try {
      const response = await fetch('/api/v2/dashboard/quick-actions', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token')}` },
      });
      const data = await response.json();
      
      const container = this.shadowRoot.getElementById('quick-actions');
      if (!container || !data.actions?.length) return;
      
      container.innerHTML = data.actions.map(action => `
        <a href="${action.url}" class="quick-action ${action.priority}">
          <span class="quick-action-icon">${action.icon}</span>
          ${action.label}
        </a>
      `).join('');
    } catch (err) {
      console.error('Failed to load quick actions:', err);
    }
  }

  renderWriterSections(container) {
    if (!container) return;
    const data = this._data?.writer_data || {};
    
    container.innerHTML = `
      <dashboard-today-progress data-json='${JSON.stringify(data.today_progress || {})}'></dashboard-today-progress>
      <dashboard-voice-snapshot data-json='${JSON.stringify(data.voice_snapshot || {})}'></dashboard-voice-snapshot>
      <dashboard-milestones data-json='${JSON.stringify(data.milestones || {})}'></dashboard-milestones>
      <dashboard-recent-analyses data-json='${JSON.stringify(data.recent_analyses || {})}'></dashboard-recent-analyses>
      ${data.featured_status ? `<dashboard-featured-status data-json='${JSON.stringify(data.featured_status)}'></dashboard-featured-status>` : ''}
      ${data.authority_progress ? `<dashboard-authority-progress data-json='${JSON.stringify(data.authority_progress)}'></dashboard-authority-progress>` : ''}
    `;
  }

  renderReaderSections(container) {
    if (!container) return;
    const data = this._data?.reader_data || {};
    
    container.innerHTML = `
      <dashboard-reading-activity data-json='${JSON.stringify(data.reading_activity || {})}'></dashboard-reading-activity>
      <dashboard-reading-taste data-json='${JSON.stringify(data.reading_taste || {})}'></dashboard-reading-taste>
      <dashboard-bookmarks data-json='${JSON.stringify(data.bookmarks || {})}'></dashboard-bookmarks>
      ${data.curator_progress ? `<dashboard-curator-progress data-json='${JSON.stringify(data.curator_progress)}'></dashboard-curator-progress>` : ''}
    `;
  }
}

customElements.define('dashboard-page', DashboardPage);


// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD CARD (Base component)
// ═══════════════════════════════════════════════════════════════════════════

class DashboardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  get data() {
    try { return JSON.parse(this.getAttribute('data-json') || '{}'); }
    catch { return {}; }
  }

  getBaseStyles() {
    return `
      :host { display: block; }
      .card {
        background: white;
        border: 1px solid ${COLORS.border};
        border-radius: 12px;
        padding: 1.25rem;
      }
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
      }
      .card-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        color: ${COLORS.ink};
        margin: 0;
      }
      .card-icon { font-size: 1.25rem; }
      .empty-state {
        text-align: center;
        padding: 1.5rem;
      }
      .empty-icon { font-size: 2rem; margin-bottom: 0.75rem; opacity: 0.5; }
      .empty-title { font-size: 0.95rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
      .empty-message { font-size: 0.85rem; color: ${COLORS.muted}; margin: 0 0 1rem 0; }
      .empty-cta {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: ${COLORS.coral};
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
      }
    `;
  }

  renderEmptyState(emptyState) {
    if (!emptyState) return '';
    return `
      <div class="empty-state">
        <div class="empty-icon">${emptyState.icon}</div>
        <h3 class="empty-title">${emptyState.title}</h3>
        <p class="empty-message">${emptyState.message}</p>
        <a href="${emptyState.cta_url}" class="empty-cta">${emptyState.cta}</a>
      </div>
    `;
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// TODAY'S PROGRESS
// ═══════════════════════════════════════════════════════════════════════════

class DashboardTodayProgress extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (d.empty_state) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .progress-bar { height: 12px; background: ${COLORS.border}; border-radius: 6px; overflow: hidden; margin-bottom: 1rem; }
        .progress-fill { height: 100%; background: ${d.percent >= 100 ? COLORS.success : COLORS.coral}; transition: width 0.5s; }
        .stats { display: flex; justify-content: space-between; }
        .stat { text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.75rem; color: ${COLORS.muted}; text-transform: uppercase; }
        .streak { display: flex; align-items: center; gap: 0.5rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid ${COLORS.border}; }
        .streak-icon { font-size: 1.5rem; }
        .streak-text { font-size: 0.9rem; color: ${COLORS.ink}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">✍️</span> Today's Progress</h2>
        </div>
        
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${d.percent}%"></div>
        </div>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${d.words_today?.toLocaleString() || 0}</div>
            <div class="stat-label">Words today</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.goal?.toLocaleString() || 0}</div>
            <div class="stat-label">Goal</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.percent || 0}%</div>
            <div class="stat-label">Complete</div>
          </div>
        </div>
        
        ${d.streak_days > 0 ? `
          <div class="streak">
            <span class="streak-icon">🔥</span>
            <span class="streak-text"><strong>${d.streak_days}-day streak</strong> ${d.streak_active ? '— Keep it going!' : '— Write today to continue!'}</span>
          </div>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('dashboard-today-progress', DashboardTodayProgress);


// ═══════════════════════════════════════════════════════════════════════════
// VOICE SNAPSHOT
// ═══════════════════════════════════════════════════════════════════════════

class DashboardVoiceSnapshot extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (!d.has_profile) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .profile-type { font-size: 1.25rem; font-weight: 600; color: ${COLORS.coral}; margin-bottom: 0.25rem; }
        .stance { font-size: 0.9rem; color: ${COLORS.muted}; margin-bottom: 1rem; }
        .traits { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .trait { padding: 0.25rem 0.75rem; background: ${COLORS.bgDark}; border-radius: 20px; font-size: 0.85rem; color: ${COLORS.ink}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">🎯</span> Your Voice</h2>
        </div>
        
        <div class="profile-type">${d.profile_type || 'Unknown'}</div>
        <div class="stance">${d.stance || ''}</div>
        
        <div class="traits">
          ${(d.top_traits || []).map(t => `<span class="trait">${t.name || t}</span>`).join('')}
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-voice-snapshot', DashboardVoiceSnapshot);


// ═══════════════════════════════════════════════════════════════════════════
// MILESTONES
// ═══════════════════════════════════════════════════════════════════════════

class DashboardMilestones extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (d.empty_state) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    const milestoneNames = {
      first_500: '✍️ First 500',
      streak_3_day: '🌰 3-Day Streak',
      daily_1k: '🔥 Daily 1K',
      streak_7_day_1k: '💫 7-Day 1K Streak',
    };

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .achieved { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
        .badge { padding: 0.25rem 0.75rem; background: ${COLORS.softGold}; color: white; border-radius: 20px; font-size: 0.85rem; }
        .next-milestone { padding: 1rem; background: ${COLORS.bgDark}; border-radius: 8px; }
        .next-label { font-size: 0.75rem; color: ${COLORS.muted}; text-transform: uppercase; margin-bottom: 0.5rem; }
        .next-name { font-size: 1rem; color: ${COLORS.ink}; font-weight: 500; margin-bottom: 0.75rem; }
        .progress-bar { height: 8px; background: ${COLORS.border}; border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: ${COLORS.coral}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">🏆</span> Milestones</h2>
        </div>
        
        ${d.achieved?.length ? `
          <div class="achieved">
            ${d.achieved.map(m => `<span class="badge">${milestoneNames[m] || m}</span>`).join('')}
          </div>
        ` : ''}
        
        ${d.next_milestone ? `
          <div class="next-milestone">
            <div class="next-label">Next milestone</div>
            <div class="next-name">${milestoneNames[d.next_milestone] || d.next_milestone}</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${d.progress_percent}%"></div>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('dashboard-milestones', DashboardMilestones);


// ═══════════════════════════════════════════════════════════════════════════
// RECENT ANALYSES
// ═══════════════════════════════════════════════════════════════════════════

class DashboardRecentAnalyses extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (d.empty_state) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .analyses { display: flex; flex-direction: column; gap: 0.75rem; }
        .analysis {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background: ${COLORS.bgDark};
          border-radius: 8px;
          cursor: pointer;
          transition: background 0.2s;
        }
        .analysis:hover { background: ${COLORS.border}; }
        .analysis-preview { font-size: 0.9rem; color: ${COLORS.ink}; flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 1rem; }
        .analysis-meta { font-size: 0.8rem; color: ${COLORS.muted}; white-space: nowrap; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">📝</span> Recent Analyses</h2>
        </div>
        
        <div class="analyses">
          ${(d.analyses || []).map(a => `
            <div class="analysis" onclick="window.location='/analysis/${a.id}'">
              <span class="analysis-preview">${a.preview || 'Untitled'}</span>
              <span class="analysis-meta">${a.word_count} words</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-recent-analyses', DashboardRecentAnalyses);


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED STATUS
// ═══════════════════════════════════════════════════════════════════════════

class DashboardFeaturedStatus extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;

    let content = '';
    if (d.status === 'featured') {
      content = `
        <div style="display: flex; align-items: center; gap: 1rem;">
          <span style="font-size: 2.5rem;">⭐</span>
          <div>
            <div style="font-size: 1.1rem; font-weight: 600; color: ${COLORS.softGold};">Featured Writer</div>
            <div style="font-size: 0.85rem; color: ${COLORS.muted};">${d.pieces_count} piece${d.pieces_count > 1 ? 's' : ''} featured</div>
          </div>
        </div>
      `;
    } else if (d.status === 'eligible') {
      content = `
        <div style="text-align: center; padding: 1rem;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
          <div style="font-size: 1rem; color: ${COLORS.ink}; margin-bottom: 0.5rem;">You're eligible!</div>
          <a href="/featured/submit" style="display: inline-block; padding: 0.5rem 1rem; background: ${COLORS.coral}; color: white; text-decoration: none; border-radius: 6px; font-size: 0.9rem;">Submit your work</a>
        </div>
      `;
    } else {
      content = `
        <div>
          <div style="font-size: 0.85rem; color: ${COLORS.muted}; margin-bottom: 0.5rem;">Complete a 7-day 1K streak to become eligible</div>
          <div style="height: 8px; background: ${COLORS.border}; border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: ${d.progress_percent}%; background: ${COLORS.coral};"></div>
          </div>
          <div style="font-size: 0.8rem; color: ${COLORS.muted}; margin-top: 0.25rem;">${d.progress_percent}% complete</div>
        </div>
      `;
    }

    this.shadowRoot.innerHTML = `
      <style>${this.getBaseStyles()}</style>
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">⭐</span> Featured Writer</h2>
        </div>
        ${content}
      </div>
    `;
  }
}

customElements.define('dashboard-featured-status', DashboardFeaturedStatus);


// ═══════════════════════════════════════════════════════════════════════════
// READING ACTIVITY
// ═══════════════════════════════════════════════════════════════════════════

class DashboardReadingActivity extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (!d.has_activity) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
        .stat { text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; }
        .stat-label { font-size: 0.75rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">📖</span> Reading Activity</h2>
        </div>
        
        <div class="stats">
          <div class="stat">
            <div class="stat-value">${d.posts_this_week || 0}</div>
            <div class="stat-label">Posts this week</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.deep_reads_this_week || 0}</div>
            <div class="stat-label">Deep reads</div>
          </div>
          <div class="stat">
            <div class="stat-value">${d.streak_days || 0}</div>
            <div class="stat-label">Day streak</div>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-reading-activity', DashboardReadingActivity);


// ═══════════════════════════════════════════════════════════════════════════
// READING TASTE
// ═══════════════════════════════════════════════════════════════════════════

class DashboardReadingTaste extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (!d.has_taste) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .taste-type { font-size: 1.25rem; font-weight: 600; color: ${COLORS.softGold}; margin-bottom: 0.25rem; }
        .stance { font-size: 0.9rem; color: ${COLORS.muted}; margin-bottom: 1rem; }
        .preferences { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .pref { padding: 0.25rem 0.75rem; background: ${COLORS.bgDark}; border-radius: 20px; font-size: 0.85rem; color: ${COLORS.ink}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">🎨</span> Your Taste</h2>
        </div>
        
        <div class="taste-type">${d.primary_type || 'Discovering...'}</div>
        <div class="stance">${d.stance_preference || ''}</div>
        
        <div class="preferences">
          ${(d.top_preferences || []).map(p => `<span class="pref">${p}</span>`).join('')}
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-reading-taste', DashboardReadingTaste);


// ═══════════════════════════════════════════════════════════════════════════
// BOOKMARKS
// ═══════════════════════════════════════════════════════════════════════════

class DashboardBookmarks extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    
    if (!d.has_bookmarks) {
      this.shadowRoot.innerHTML = `
        <style>${this.getBaseStyles()}</style>
        <div class="card">${this.renderEmptyState(d.empty_state)}</div>
      `;
      return;
    }

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .count { font-size: 0.9rem; color: ${COLORS.muted}; margin-bottom: 1rem; }
        .count strong { color: ${COLORS.ink}; }
        .at-limit { color: ${COLORS.coral}; }
        .bookmarks { display: flex; flex-direction: column; gap: 0.5rem; }
        .bookmark {
          padding: 0.5rem 0.75rem;
          background: ${COLORS.bgDark};
          border-radius: 6px;
          font-size: 0.9rem;
          color: ${COLORS.ink};
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">🔖</span> Bookmarks</h2>
        </div>
        
        <div class="count ${d.at_limit ? 'at-limit' : ''}">
          <strong>${d.count}</strong>${d.limit > 0 ? ` / ${d.limit}` : ''} saved
          ${d.at_limit ? ' — Upgrade for unlimited' : ''}
        </div>
        
        <div class="bookmarks">
          ${(d.recent || []).map(b => `<div class="bookmark">${b.title || 'Untitled'}</div>`).join('')}
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-bookmarks', DashboardBookmarks);


// ═══════════════════════════════════════════════════════════════════════════
// CURATOR PROGRESS
// ═══════════════════════════════════════════════════════════════════════════

class DashboardCuratorProgress extends DashboardCard {
  connectedCallback() { this.render(); }
  
  render() {
    const d = this.data;
    const progress = d.progress || {};

    this.shadowRoot.innerHTML = `
      <style>
        ${this.getBaseStyles()}
        .window-info { font-size: 0.85rem; color: ${COLORS.muted}; margin-bottom: 1rem; }
        .requirements { display: flex; flex-direction: column; gap: 0.75rem; }
        .requirement { display: flex; align-items: center; gap: 0.75rem; }
        .req-check { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
        .req-check.complete { background: ${COLORS.success}; color: white; }
        .req-check.incomplete { background: ${COLORS.border}; color: ${COLORS.muted}; }
        .req-info { flex: 1; }
        .req-name { font-size: 0.9rem; color: ${COLORS.ink}; }
        .req-progress { font-size: 0.8rem; color: ${COLORS.muted}; }
      </style>
      
      <div class="card">
        <div class="card-header">
          <h2 class="card-title"><span class="card-icon">📚</span> Curator Journey</h2>
        </div>
        
        <div class="window-info">
          ${d.window_active ? `${d.window_days_remaining} days remaining` : 'Start your 30-day window'}
        </div>
        
        <div class="requirements">
          ${Object.entries(progress).map(([key, val]) => {
            const complete = val.current >= val.target;
            const labels = {
              posts_read: 'Posts read',
              deep_reads: 'Deep reads',
              profile_types: 'Profile types explored',
              bookmarks: 'Bookmarks',
              reading_streak: 'Reading streak',
            };
            return `
              <div class="requirement">
                <div class="req-check ${complete ? 'complete' : 'incomplete'}">${complete ? '✓' : ''}</div>
                <div class="req-info">
                  <div class="req-name">${labels[key] || key}</div>
                  <div class="req-progress">${val.current} / ${val.target}</div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }
}

customElements.define('dashboard-curator-progress', DashboardCuratorProgress);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyDashboard = {
    DashboardPage,
    DashboardTodayProgress,
    DashboardVoiceSnapshot,
    DashboardMilestones,
    DashboardRecentAnalyses,
    DashboardFeaturedStatus,
    DashboardReadingActivity,
    DashboardReadingTaste,
    DashboardBookmarks,
    DashboardCuratorProgress,
  };
}
