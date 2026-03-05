/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY FEATURED ELIGIBILITY SYSTEM v1.1
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Updates based on Master Test findings:
 * - Added streak forgiveness (1 grace day per 7)
 * - Added progress visibility component
 * - Added motivation mechanics
 */

const COLORS = {
  coral: '#FF6B6B',
  softGold: '#D4A574',
  ink: '#2D3436',
  muted: '#636E72',
  bg: '#FFFBF5',
  success: '#00B894',
  purple: '#6C5CE7',
};


// ═══════════════════════════════════════════════════════════════════════════
// UPDATED STREAK LOGIC WITH FORGIVENESS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate streak with 1 grace day per 7.
 * Users can miss 1 day in any 7-day window without breaking streak.
 * 
 * @param {Array<string>} activeDates - Array of ISO date strings when user was active
 * @returns {Object} - { currentStreak, longestStreak, graceDaysUsed, isAtRisk }
 */
function calculateStreakWithForgiveness(activeDates) {
  if (!activeDates || activeDates.length === 0) {
    return { currentStreak: 0, longestStreak: 0, graceDaysUsed: 0, isAtRisk: false };
  }

  // Sort dates
  const dates = activeDates
    .map(d => new Date(d))
    .sort((a, b) => a - b);

  // Convert to day indices (days since first activity)
  const firstDay = dates[0];
  const dayIndices = new Set(
    dates.map(d => Math.floor((d - firstDay) / (1000 * 60 * 60 * 24)))
  );

  // Find today's index
  const today = new Date();
  const todayIndex = Math.floor((today - firstDay) / (1000 * 60 * 60 * 24));

  // Calculate current streak with forgiveness
  let currentStreak = 0;
  let graceDaysUsed = 0;
  let consecutiveMissed = 0;

  for (let i = todayIndex; i >= 0; i--) {
    if (dayIndices.has(i)) {
      currentStreak++;
      consecutiveMissed = 0;
    } else {
      consecutiveMissed++;
      
      // Allow 1 grace day per 7
      const graceDaysAllowed = Math.floor(currentStreak / 6);
      
      if (graceDaysUsed < graceDaysAllowed && consecutiveMissed <= 1) {
        graceDaysUsed++;
        // Don't break streak, but don't increment either
      } else if (consecutiveMissed > 1) {
        break; // Streak broken - missed 2+ days in a row
      } else if (graceDaysUsed >= graceDaysAllowed) {
        break; // Used all grace days
      }
    }
  }

  // Calculate longest streak (simpler, without forgiveness for historical)
  let longestStreak = 0;
  let tempStreak = 0;
  let lastIndex = -2;

  for (const idx of [...dayIndices].sort((a, b) => a - b)) {
    if (idx === lastIndex + 1) {
      tempStreak++;
    } else {
      tempStreak = 1;
    }
    longestStreak = Math.max(longestStreak, tempStreak);
    lastIndex = idx;
  }

  // Is user at risk? (hasn't been active today and no grace days left)
  const wasActiveToday = dayIndices.has(todayIndex);
  const graceDaysAllowed = Math.floor(currentStreak / 6);
  const isAtRisk = !wasActiveToday && graceDaysUsed >= graceDaysAllowed;

  return {
    currentStreak,
    longestStreak,
    graceDaysUsed,
    graceDaysRemaining: Math.max(0, graceDaysAllowed - graceDaysUsed),
    isAtRisk,
    wasActiveToday,
  };
}


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED ELIGIBILITY REQUIREMENTS
// ═══════════════════════════════════════════════════════════════════════════

const FEATURED_REQUIREMENTS = {
  minStreak: 7,
  minWordsTotal: 7000,  // 7 days × 1000 words
  minActiveDays: 14,    // Reduced from 30 for earlier visibility
  requiresPro: true,
  minPiecesForSubmission: 4,
  maxPiecesForSubmission: 6,
};


/**
 * Calculate user's progress toward Featured eligibility.
 * 
 * @param {Object} userStats - User's current statistics
 * @returns {Object} - Eligibility status and progress
 */
function calculateFeaturedProgress(userStats) {
  const {
    currentStreak = 0,
    totalWordsAnalyzed = 0,
    totalActiveDays = 0,
    isPro = false,
    submittedPiecesCount = 0,
  } = userStats;

  const requirements = [
    {
      id: 'streak',
      label: '7-day writing streak',
      current: currentStreak,
      required: FEATURED_REQUIREMENTS.minStreak,
      progress: Math.min(100, (currentStreak / FEATURED_REQUIREMENTS.minStreak) * 100),
      complete: currentStreak >= FEATURED_REQUIREMENTS.minStreak,
      icon: '🔥',
    },
    {
      id: 'words',
      label: '7,000 words analyzed',
      current: totalWordsAnalyzed,
      required: FEATURED_REQUIREMENTS.minWordsTotal,
      progress: Math.min(100, (totalWordsAnalyzed / FEATURED_REQUIREMENTS.minWordsTotal) * 100),
      complete: totalWordsAnalyzed >= FEATURED_REQUIREMENTS.minWordsTotal,
      icon: '📝',
    },
    {
      id: 'activity',
      label: '14 active days',
      current: totalActiveDays,
      required: FEATURED_REQUIREMENTS.minActiveDays,
      progress: Math.min(100, (totalActiveDays / FEATURED_REQUIREMENTS.minActiveDays) * 100),
      complete: totalActiveDays >= FEATURED_REQUIREMENTS.minActiveDays,
      icon: '📅',
    },
    {
      id: 'pro',
      label: 'PRO subscription',
      current: isPro ? 1 : 0,
      required: 1,
      progress: isPro ? 100 : 0,
      complete: isPro,
      icon: '⭐',
    },
  ];

  const completedCount = requirements.filter(r => r.complete).length;
  const overallProgress = (completedCount / requirements.length) * 100;
  const isEligible = requirements.every(r => r.complete);

  return {
    requirements,
    completedCount,
    totalCount: requirements.length,
    overallProgress,
    isEligible,
    canSubmit: isEligible && submittedPiecesCount === 0,
    nextMilestone: requirements.find(r => !r.complete),
  };
}


// ═══════════════════════════════════════════════════════════════════════════
// FEATURED PROGRESS COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

class FeaturedProgress extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._stats = {};
  }

  static get observedAttributes() {
    return ['current-streak', 'total-words', 'active-days', 'is-pro'];
  }

  attributeChangedCallback(name, oldVal, newVal) {
    const key = name.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    if (key === 'isPro') {
      this._stats[key] = newVal === 'true';
    } else {
      this._stats[key] = parseInt(newVal) || 0;
    }
    this.render();
  }

  connectedCallback() { this.render(); }

  render() {
    const progress = calculateFeaturedProgress({
      currentStreak: this._stats.currentStreak || 0,
      totalWordsAnalyzed: this._stats.totalWords || 0,
      totalActiveDays: this._stats.activeDays || 0,
      isPro: this._stats.isPro || false,
    });

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .progress-card {
          background: white;
          border: 1px solid #E9ECEF;
          border-radius: 16px;
          padding: 1.5rem;
        }
        
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .title {
          font-size: 1.1rem;
          font-weight: 600;
          color: ${COLORS.ink};
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .badge {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
        }
        .badge.eligible {
          background: ${COLORS.success};
          color: white;
        }
        .badge.in-progress {
          background: ${COLORS.softGold};
          color: white;
        }
        
        .overall-progress {
          margin-bottom: 1.5rem;
        }
        .overall-bar {
          height: 8px;
          background: #E9ECEF;
          border-radius: 4px;
          overflow: hidden;
        }
        .overall-fill {
          height: 100%;
          background: linear-gradient(90deg, ${COLORS.coral} 0%, ${COLORS.softGold} 100%);
          border-radius: 4px;
          transition: width 0.5s ease-out;
        }
        .overall-text {
          display: flex;
          justify-content: space-between;
          margin-top: 0.5rem;
          font-size: 0.85rem;
          color: ${COLORS.muted};
        }
        
        .requirements {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .requirement {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .req-icon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.25rem;
          background: #F8F5F0;
        }
        .req-icon.complete {
          background: ${COLORS.success};
        }
        
        .req-content { flex: 1; }
        .req-label {
          font-size: 0.9rem;
          font-weight: 500;
          color: ${COLORS.ink};
        }
        .req-progress-container {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-top: 0.25rem;
        }
        .req-bar {
          flex: 1;
          height: 4px;
          background: #E9ECEF;
          border-radius: 2px;
          overflow: hidden;
        }
        .req-fill {
          height: 100%;
          border-radius: 2px;
          transition: width 0.3s;
        }
        .req-fill.complete { background: ${COLORS.success}; }
        .req-fill.in-progress { background: ${COLORS.softGold}; }
        .req-value {
          font-size: 0.8rem;
          color: ${COLORS.muted};
          min-width: 60px;
          text-align: right;
        }
        
        .req-check {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.9rem;
        }
        .req-check.complete {
          background: ${COLORS.success};
          color: white;
        }
        .req-check.incomplete {
          background: #E9ECEF;
          color: ${COLORS.muted};
        }
        
        .cta-section {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid #E9ECEF;
        }
        
        .cta-btn {
          width: 100%;
          padding: 0.875rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        .cta-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
        }
        .cta-btn:disabled {
          background: #E9ECEF;
          color: ${COLORS.muted};
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        
        .next-milestone {
          margin-top: 1rem;
          padding: 1rem;
          background: #F8F5F0;
          border-radius: 10px;
          font-size: 0.9rem;
          color: ${COLORS.ink};
        }
        .next-label {
          font-size: 0.75rem;
          color: ${COLORS.muted};
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 0.25rem;
        }
      </style>
      
      <div class="progress-card">
        <div class="header">
          <h3 class="title">
            ⭐ Featured Writer Progress
          </h3>
          <span class="badge ${progress.isEligible ? 'eligible' : 'in-progress'}">
            ${progress.isEligible ? '✓ Eligible' : `${progress.completedCount}/${progress.totalCount}`}
          </span>
        </div>
        
        <div class="overall-progress">
          <div class="overall-bar">
            <div class="overall-fill" style="width: ${progress.overallProgress}%"></div>
          </div>
          <div class="overall-text">
            <span>${progress.completedCount} of ${progress.totalCount} requirements met</span>
            <span>${Math.round(progress.overallProgress)}%</span>
          </div>
        </div>
        
        <div class="requirements">
          ${progress.requirements.map(req => `
            <div class="requirement">
              <div class="req-icon ${req.complete ? 'complete' : ''}">
                ${req.icon}
              </div>
              <div class="req-content">
                <div class="req-label">${req.label}</div>
                <div class="req-progress-container">
                  <div class="req-bar">
                    <div class="req-fill ${req.complete ? 'complete' : 'in-progress'}" style="width: ${req.progress}%"></div>
                  </div>
                  <span class="req-value">
                    ${req.id === 'pro' 
                      ? (req.complete ? 'Active' : 'Required')
                      : `${req.current.toLocaleString()} / ${req.required.toLocaleString()}`
                    }
                  </span>
                </div>
              </div>
              <div class="req-check ${req.complete ? 'complete' : 'incomplete'}">
                ${req.complete ? '✓' : '○'}
              </div>
            </div>
          `).join('')}
        </div>
        
        ${progress.isEligible ? `
          <div class="cta-section">
            <button class="cta-btn" id="submit-btn">
              Submit for Featured →
            </button>
          </div>
        ` : progress.nextMilestone ? `
          <div class="next-milestone">
            <div class="next-label">Next milestone</div>
            <strong>${progress.nextMilestone.icon} ${progress.nextMilestone.label}</strong>
            — ${progress.nextMilestone.required - progress.nextMilestone.current} more to go
          </div>
        ` : ''}
      </div>
    `;

    this.shadowRoot.getElementById('submit-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('submit-featured', { bubbles: true }));
    });
  }
}

customElements.define('featured-progress', FeaturedProgress);


// ═══════════════════════════════════════════════════════════════════════════
// STREAK STATUS COMPONENT (with forgiveness indicator)
// ═══════════════════════════════════════════════════════════════════════════

class StreakStatus extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._streakData = {};
  }

  setStreakData(data) {
    this._streakData = data;
    this.render();
  }

  connectedCallback() { this.render(); }

  render() {
    const {
      currentStreak = 0,
      longestStreak = 0,
      graceDaysRemaining = 0,
      isAtRisk = false,
      wasActiveToday = false,
    } = this._streakData;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        
        .streak-card {
          background: ${isAtRisk ? 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)' : 'linear-gradient(135deg, #FF6B6B 0%, #D4A574 100%)'};
          color: white;
          border-radius: 16px;
          padding: 1.5rem;
        }
        
        .streak-main {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .streak-icon { font-size: 2.5rem; }
        
        .streak-info { flex: 1; }
        .streak-count {
          font-size: 2rem;
          font-weight: 700;
          line-height: 1.2;
        }
        .streak-label {
          font-size: 0.9rem;
          opacity: 0.9;
        }
        
        .streak-meta {
          display: flex;
          gap: 1.5rem;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .meta-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
        }
        .meta-icon { font-size: 1rem; }
        
        .grace-days {
          display: flex;
          gap: 0.25rem;
          margin-left: auto;
        }
        .grace-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255,255,255,0.3);
        }
        .grace-dot.available { background: white; }
        
        .risk-warning {
          margin-top: 1rem;
          padding: 0.75rem;
          background: rgba(0,0,0,0.2);
          border-radius: 8px;
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
      </style>
      
      <div class="streak-card">
        <div class="streak-main">
          <span class="streak-icon">${currentStreak >= 7 ? '🔥' : '✨'}</span>
          <div class="streak-info">
            <div class="streak-count">${currentStreak} day${currentStreak !== 1 ? 's' : ''}</div>
            <div class="streak-label">${currentStreak >= 7 ? 'Incredible streak!' : 'Current streak'}</div>
          </div>
        </div>
        
        <div class="streak-meta">
          <div class="meta-item">
            <span class="meta-icon">🏆</span>
            <span>Best: ${longestStreak} days</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">${wasActiveToday ? '✓' : '○'}</span>
            <span>${wasActiveToday ? 'Active today' : 'Write today!'}</span>
          </div>
          <div class="grace-days" title="Grace days remaining">
            ${[0, 1].map(i => `<div class="grace-dot ${i < graceDaysRemaining ? 'available' : ''}"></div>`).join('')}
          </div>
        </div>
        
        ${isAtRisk ? `
          <div class="risk-warning">
            <span>⚠️</span>
            <span>Write today to keep your streak! No grace days left.</span>
          </div>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('streak-status', StreakStatus);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof window !== 'undefined') {
  window.QuirrelyFeatured = {
    calculateStreakWithForgiveness,
    calculateFeaturedProgress,
    FEATURED_REQUIREMENTS,
    FeaturedProgress,
    StreakStatus,
  };
}
