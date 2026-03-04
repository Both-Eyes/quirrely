/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EXTENSION v2.0.0 - Popup Controller
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Features:
 * - Voice analysis with LNCP classifier
 * - STRETCH exercise integration
 * - Tier-aware feature gating
 * - Compare voices (v2)
 * - Session sync with web app
 */

(function() {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════════════════

  const CONFIG = {
    webAppUrl: 'https://quirrely.com',
    apiUrl: 'https://api.quirrely.com',
    minChars: 50,
    freeAnalysesPerDay: 5,
    proAnalysesPerDay: 100,
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════════════════════════════════════

  let currentView = 'input';
  let lastAnalysis = null;
  let settings = {};
  let userState = {
    tier: 'free',
    userId: null,
    sessionId: null,
    analysesToday: 0,
    stretchStreak: 0,
    stretchEligible: true,
    lastStretchDate: null,
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // DOM ELEMENTS
  // ═══════════════════════════════════════════════════════════════════════════

  const elements = {
    // Views
    viewInput: document.getElementById('view-input'),
    viewResult: document.getElementById('view-result'),
    viewHistory: document.getElementById('view-history'),
    viewSettings: document.getElementById('view-settings'),
    viewCompare: document.getElementById('view-compare'),
    
    // Input
    textInput: document.getElementById('text-input'),
    charCount: document.getElementById('char-count'),
    dailyLimit: document.getElementById('daily-limit'),
    btnAnalyze: document.getElementById('btn-analyze'),
    
    // Result
    resultIcon: document.getElementById('result-icon'),
    resultTitle: document.getElementById('result-title'),
    resultTagline: document.getElementById('result-tagline'),
    badgeProfile: document.getElementById('badge-profile'),
    badgeStance: document.getElementById('badge-stance'),
    badgeConfidence: document.getElementById('badge-confidence'),
    resultTraits: document.getElementById('result-traits'),
    metricWords: document.getElementById('metric-words'),
    metricSentences: document.getElementById('metric-sentences'),
    metricQuestions: document.getElementById('metric-questions'),
    btnNewAnalysis: document.getElementById('btn-new-analysis'),
    btnFullResults: document.getElementById('btn-full-results'),
    
    // STRETCH
    stretchStreakBanner: document.getElementById('stretch-streak-banner'),
    stretchCount: document.getElementById('streak-count'),
    stretchCta: document.getElementById('stretch-cta'),
    stretchCtaResult: document.getElementById('stretch-cta-result'),
    stretchProgressSection: document.getElementById('stretch-progress-section'),
    
    // History
    historyList: document.getElementById('history-list'),
    historyEmpty: document.getElementById('history-empty'),
    btnClearHistory: document.getElementById('btn-clear-history'),
    
    // Compare
    compareSlot1: document.getElementById('compare-slot-1'),
    compareSlot2: document.getElementById('compare-slot-2'),
    btnBackFromCompare: document.getElementById('btn-back-from-compare'),
    
    // Settings
    settingFloatingButton: document.getElementById('setting-floating-button'),
    settingNotifications: document.getElementById('setting-notifications'),
    settingStoreHistory: document.getElementById('setting-store-history'),
    settingAnonymousData: document.getElementById('setting-anonymous-data'),
    accountSection: document.getElementById('account-section'),
    
    // Navigation
    btnHistory: document.getElementById('btn-history'),
    btnSettings: document.getElementById('btn-settings'),
    btnBackFromHistory: document.getElementById('btn-back-from-history'),
    btnBackFromSettings: document.getElementById('btn-back-from-settings'),
    
    // Footer
    tierBadge: document.getElementById('tier-badge')
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════════════════════

  async function initialize() {
    console.log('🐿️ Quirrely Extension v2.0.0 initializing...');
    
    try {
      // Load settings from storage
      settings = await sendMessage({ type: 'GET_SETTINGS' }) || {};
      applySettings();
      
      // Load user state (tier, session, STRETCH progress)
      await loadUserState();
      
      // Update UI based on user state
      updateTierBadge();
      updateStretchUI();
      updateDailyLimit();
      
      // Check for selected text from context menu
      const selection = await sendMessage({ type: 'GET_SELECTION' });
      if (selection && selection.text) {
        elements.textInput.value = selection.text;
        updateCharCount();
      }
      
      // Check for last analysis
      const lastResponse = await sendMessage({ type: 'GET_LAST_ANALYSIS' });
      if (lastResponse && lastResponse.analysis) {
        lastAnalysis = lastResponse.analysis;
        showView('result');
        displayResult(lastAnalysis);
      }
      
      // Set up event listeners
      setupEventListeners();
      
      console.log('✅ Quirrely Extension initialized');
      
    } catch (error) {
      console.error('❌ Initialization error:', error);
    }
  }

  async function loadUserState() {
    try {
      // Try to sync with web app first
      const syncResponse = await sendMessage({ type: 'SYNC_WITH_WEBAPP' });
      
      if (syncResponse && syncResponse.success) {
        userState = {
          tier: syncResponse.tier || 'free',
          userId: syncResponse.userId,
          sessionId: syncResponse.sessionId,
          analysesToday: syncResponse.analysesToday || 0,
          stretchStreak: syncResponse.stretchStreak || 0,
          stretchEligible: syncResponse.stretchEligible !== false,
          lastStretchDate: syncResponse.lastStretchDate,
        };
      } else {
        // Fall back to local storage
        const localState = await sendMessage({ type: 'GET_USER_STATE' });
        if (localState) {
          userState = { ...userState, ...localState };
        }
      }
    } catch (error) {
      console.warn('Could not load user state:', error);
    }
  }

  function setupEventListeners() {
    // Text input
    elements.textInput.addEventListener('input', handleTextInput);
    elements.btnAnalyze.addEventListener('click', handleAnalyze);
    
    // Navigation
    elements.btnHistory.addEventListener('click', () => showView('history'));
    elements.btnSettings.addEventListener('click', () => showView('settings'));
    elements.btnBackFromHistory?.addEventListener('click', () => showView(lastAnalysis ? 'result' : 'input'));
    elements.btnBackFromSettings?.addEventListener('click', () => showView(lastAnalysis ? 'result' : 'input'));
    elements.btnBackFromCompare?.addEventListener('click', () => showView('history'));
    
    // Result actions
    elements.btnNewAnalysis?.addEventListener('click', handleNewAnalysis);
    
    // History
    elements.btnClearHistory?.addEventListener('click', handleClearHistory);
    
    // Settings toggles
    elements.settingFloatingButton?.addEventListener('change', (e) => updateSetting('showFloatingButton', e.target.checked));
    elements.settingNotifications?.addEventListener('change', (e) => updateSetting('showNotifications', e.target.checked));
    elements.settingStoreHistory?.addEventListener('change', (e) => updateSetting('storeHistory', e.target.checked));
    elements.settingAnonymousData?.addEventListener('change', (e) => updateSetting('sendAnonymousData', e.target.checked));
    
    // Keyboard shortcuts
    elements.textInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        handleAnalyze();
      }
    });
    
    // STRETCH CTA clicks (track engagement)
    document.querySelectorAll('[href*="/stretch"]').forEach(link => {
      link.addEventListener('click', () => {
        sendMessage({ type: 'TRACK_STRETCH_CLICK' });
      });
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // VIEW MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  function showView(view) {
    currentView = view;
    
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    
    // Show requested view
    const viewElement = document.getElementById(`view-${view}`);
    if (viewElement) {
      viewElement.classList.add('active');
    }
    
    // View-specific actions
    switch (view) {
      case 'input':
        elements.textInput.focus();
        break;
      case 'history':
        loadHistory();
        break;
      case 'settings':
        loadSettings();
        break;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TEXT INPUT & ANALYSIS
  // ═══════════════════════════════════════════════════════════════════════════

  function handleTextInput() {
    updateCharCount();
    updateAnalyzeButton();
  }

  function updateCharCount() {
    const text = elements.textInput.value;
    const chars = text.length;
    
    elements.charCount.textContent = `${chars} character${chars !== 1 ? 's' : ''}`;
    elements.charCount.classList.toggle('valid', chars >= CONFIG.minChars);
    elements.charCount.classList.toggle('invalid', chars > 0 && chars < CONFIG.minChars);
  }

  function updateAnalyzeButton() {
    const chars = elements.textInput.value.length;
    const canAnalyze = chars >= CONFIG.minChars && !isAtDailyLimit();
    
    elements.btnAnalyze.disabled = !canAnalyze;
  }

  function isAtDailyLimit() {
    const limit = getTierLimit();
    return userState.analysesToday >= limit;
  }

  function getTierLimit() {
    switch (userState.tier) {
      case 'pro': return CONFIG.proAnalysesPerDay;
      default: return CONFIG.freeAnalysesPerDay;
    }
  }

  function updateDailyLimit() {
    const limit = getTierLimit();
    const remaining = Math.max(0, limit - userState.analysesToday);
    
    if (limit === Infinity) {
      elements.dailyLimit.textContent = '∞ analyses';
      elements.dailyLimit.classList.remove('warning', 'error');
    } else {
      elements.dailyLimit.textContent = `${remaining}/${limit} today`;
      elements.dailyLimit.classList.toggle('warning', remaining <= 2 && remaining > 0);
      elements.dailyLimit.classList.toggle('error', remaining === 0);
    }
  }

  async function handleAnalyze() {
    const text = elements.textInput.value.trim();
    
    if (text.length < CONFIG.minChars) {
      showToast(`Please enter at least ${CONFIG.minChars} characters`);
      return;
    }
    
    if (isAtDailyLimit()) {
      showUpgradePrompt();
      return;
    }
    
    // Show loading state
    elements.btnAnalyze.classList.add('loading');
    elements.btnAnalyze.disabled = true;
    
    try {
      // Run analysis using LNCP classifier
      const analysis = await analyzeText(text);
      
      // Save analysis
      lastAnalysis = analysis;
      await sendMessage({ type: 'SAVE_ANALYSIS', analysis });
      
      // Increment daily count
      userState.analysesToday++;
      updateDailyLimit();
      
      // Display result
      displayResult(analysis);
      showView('result');
      
      // Show STRETCH CTA if eligible
      updateStretchCtaVisibility();
      
    } catch (error) {
      console.error('Analysis error:', error);
      showToast('Analysis failed. Please try again.');
    } finally {
      elements.btnAnalyze.classList.remove('loading');
      updateAnalyzeButton();
    }
  }

  async function analyzeText(text) {
    // Use local LNCP classifier
    if (typeof window.LNCPClassifier !== 'undefined') {
      const result = window.LNCPClassifier.analyze(text);
      return {
        ...result,
        text: text.substring(0, 200), // Store preview
        timestamp: Date.now(),
        source: 'extension',
      };
    }
    
    // Fallback to API
    return await sendMessage({ type: 'ANALYZE_TEXT', text });
  }

  function handleNewAnalysis() {
    lastAnalysis = null;
    elements.textInput.value = '';
    updateCharCount();
    showView('input');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // RESULT DISPLAY
  // ═══════════════════════════════════════════════════════════════════════════

  function displayResult(analysis) {
    if (!analysis) return;
    
    // Profile info
    const profile = getProfileInfo(analysis.profile, analysis.stance);
    
    elements.resultIcon.textContent = profile.icon;
    elements.resultTitle.textContent = profile.title;
    elements.resultTagline.textContent = profile.tagline;
    
    // Badges
    elements.badgeProfile.textContent = analysis.profile.toUpperCase();
    elements.badgeProfile.className = `badge profile ${analysis.profile.toLowerCase()}`;
    
    elements.badgeStance.textContent = analysis.stance.toUpperCase();
    elements.badgeStance.className = `badge stance ${analysis.stance.toLowerCase()}`;
    
    const confidence = Math.round((analysis.confidence || 0.85) * 100);
    elements.badgeConfidence.textContent = `${confidence}%`;
    
    // Traits
    if (analysis.traits && elements.resultTraits) {
      elements.resultTraits.innerHTML = analysis.traits
        .slice(0, 3)
        .map(trait => `<span class="trait">${trait}</span>`)
        .join('');
    }
    
    // Metrics
    elements.metricWords.textContent = analysis.wordCount || 0;
    elements.metricSentences.textContent = analysis.sentenceCount || 0;
    elements.metricQuestions.textContent = `${Math.round((analysis.questionRatio || 0) * 100)}%`;
    
    // Update full results link with analysis data
    if (elements.btnFullResults) {
      const params = new URLSearchParams({
        profile: analysis.profile,
        stance: analysis.stance,
        source: 'extension'
      });
      elements.btnFullResults.href = `${CONFIG.webAppUrl}/results?${params}`;
    }
  }

  function getProfileInfo(profile, stance) {
    const profiles = {
      assertive: { icon: '🚀', titles: { open: 'The Bold Explorer', closed: 'The Confident Authority', balanced: 'The Clear Leader', contradictory: 'The Dynamic Force' }},
      hedged: { icon: '🌊', titles: { open: 'The Thoughtful Guide', closed: 'The Careful Analyst', balanced: 'The Wise Mediator', contradictory: 'The Nuanced Thinker' }},
      conversational: { icon: '☕', titles: { open: 'The Warm Connector', closed: 'The Trusted Confidant', balanced: 'The Friendly Expert', contradictory: 'The Engaging Storyteller' }},
      formal: { icon: '📚', titles: { open: 'The Scholarly Voice', closed: 'The Distinguished Expert', balanced: 'The Professional Authority', contradictory: 'The Versatile Academic' }},
      interrogative: { icon: '🔍', titles: { open: 'The Curious Explorer', closed: 'The Probing Mind', balanced: 'The Inquisitive Guide', contradictory: 'The Questioning Spirit' }},
      dense: { icon: '💎', titles: { open: 'The Deep Thinker', closed: 'The Precise Crafter', balanced: 'The Rich Weaver', contradictory: 'The Complex Artist' }},
      minimal: { icon: '✨', titles: { open: 'The Clear Voice', closed: 'The Sharp Editor', balanced: 'The Elegant Minimalist', contradictory: 'The Selective Stylist' }},
      longform: { icon: '📖', titles: { open: 'The Expansive Narrator', closed: 'The Detailed Builder', balanced: 'The Thorough Guide', contradictory: 'The Flowing Storyteller' }},
      poetic: { icon: '🎭', titles: { open: 'The Creative Soul', closed: 'The Lyrical Artist', balanced: 'The Artistic Voice', contradictory: 'The Expressive Spirit' }},
      balanced: { icon: '⚖️', titles: { open: 'The Versatile Voice', closed: 'The Measured Mind', balanced: 'The Centered Writer', contradictory: 'The Adaptive Author' }},
    };
    
    const p = profiles[profile?.toLowerCase()] || profiles.balanced;
    const title = p.titles[stance?.toLowerCase()] || p.titles.balanced;
    
    const taglines = {
      open: 'Invites dialogue and connection',
      closed: 'Conveys authority and certainty',
      balanced: 'Balances confidence with openness',
      contradictory: 'Blends multiple perspectives',
    };
    
    return {
      icon: p.icon,
      title: title,
      tagline: taglines[stance?.toLowerCase()] || taglines.balanced,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // STRETCH INTEGRATION
  // ═══════════════════════════════════════════════════════════════════════════

  function updateStretchUI() {
    // Show streak banner if user has active streak
    if (userState.stretchStreak > 0 && elements.stretchStreakBanner) {
      elements.stretchStreakBanner.style.display = 'flex';
      elements.stretchCount.textContent = userState.stretchStreak;
    } else if (elements.stretchStreakBanner) {
      elements.stretchStreakBanner.style.display = 'none';
    }
    
    // Show STRETCH CTA for eligible users
    updateStretchCtaVisibility();
    
    // Update STRETCH progress in settings
    if (elements.stretchProgressSection) {
      elements.stretchProgressSection.innerHTML = renderStretchProgress();
    }
  }

  function updateStretchCtaVisibility() {
    const showCta = userState.stretchEligible;
    
    if (elements.stretchCta) {
      elements.stretchCta.style.display = showCta ? 'flex' : 'none';
    }
    
    // Show post-result CTA if user just analyzed and is eligible
    if (elements.stretchCtaResult && lastAnalysis) {
      elements.stretchCtaResult.style.display = showCta ? 'block' : 'none';
      
      // Customize STRETCH link with profile
      const stretchLink = elements.stretchCtaResult.querySelector('a[href*="/stretch"]');
      if (stretchLink && lastAnalysis.profile) {
        const params = new URLSearchParams({
          profile: lastAnalysis.profile,
          source: 'extension_result'
        });
        stretchLink.href = `${CONFIG.webAppUrl}/stretch?${params}`;
      }
    }
  }

  function renderStretchProgress() {
    if (userState.stretchStreak > 0) {
      return `
        <div class="stretch-progress">
          <div class="stretch-stat">
            <span class="stretch-stat-value">🔥 ${userState.stretchStreak}</span>
            <span class="stretch-stat-label">Day Streak</span>
          </div>
          <a href="${CONFIG.webAppUrl}/stretch" target="_blank" class="btn-stretch-small">
            Continue STRETCH →
          </a>
        </div>
      `;
    } else {
      return `
        <div class="stretch-intro">
          <p>STRETCH exercises help you strengthen your writing voice in just 5 minutes a day.</p>
          <a href="${CONFIG.webAppUrl}/stretch" target="_blank" class="btn-stretch-small">
            Try STRETCH →
          </a>
        </div>
      `;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // TIER MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  function updateTierBadge() {
    if (!elements.tierBadge) return;
    
    const tierConfig = {
      free: { icon: '⭐', text: 'Free', class: 'free' },
      trial: { icon: '🎁', text: 'Trial', class: 'trial' },
      pro: { icon: '💎', text: 'Pro', class: 'pro' },

    };
    
    const config = tierConfig[userState.tier] || tierConfig.free;
    
    elements.tierBadge.innerHTML = `
      <span class="tier-icon">${config.icon}</span>
      <span class="tier-text">${config.text}</span>
    `;
    elements.tierBadge.className = `tier-badge ${config.class}`;
  }

  function showUpgradePrompt() {
    const modal = document.createElement('div');
    modal.className = 'upgrade-modal';
    modal.innerHTML = `
      <div class="upgrade-modal-content">
        <h3>Daily Limit Reached</h3>
        <p>You've used all ${getTierLimit()} free analyses today.</p>
        <p>Upgrade to Pro for 100 analyses per day, plus STRETCH exercises!</p>
        <div class="upgrade-actions">
          <a href="${CONFIG.webAppUrl}/billing/upgrade.html?source=extension" target="_blank" class="btn-upgrade">
            Upgrade to Pro
          </a>
          <button class="btn-dismiss" onclick="this.closest('.upgrade-modal').remove()">
            Maybe Later
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // HISTORY
  // ═══════════════════════════════════════════════════════════════════════════

  async function loadHistory() {
    try {
      const response = await sendMessage({ type: 'GET_HISTORY', limit: 20 });
      const history = response?.history || [];
      
      if (history.length === 0) {
        elements.historyList.innerHTML = '';
        elements.historyEmpty.style.display = 'block';
        return;
      }
      
      elements.historyEmpty.style.display = 'none';
      elements.historyList.innerHTML = history.map((item, index) => `
        <div class="history-item" data-index="${index}">
          <div class="history-icon">${getProfileInfo(item.profile, item.stance).icon}</div>
          <div class="history-content">
            <div class="history-title">${getProfileInfo(item.profile, item.stance).title}</div>
            <div class="history-meta">${formatDate(item.timestamp)} • ${item.wordCount || 0} words</div>
          </div>
          <div class="history-badges">
            <span class="badge mini ${item.profile?.toLowerCase()}">${item.profile}</span>
          </div>
        </div>
      `).join('');
      
      // Add click handlers
      elements.historyList.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
          const index = parseInt(item.dataset.index);
          if (history[index]) {
            lastAnalysis = history[index];
            displayResult(lastAnalysis);
            showView('result');
          }
        });
      });
      
    } catch (error) {
      console.error('Error loading history:', error);
    }
  }

  async function handleClearHistory() {
    if (confirm('Clear all analysis history?')) {
      await sendMessage({ type: 'CLEAR_HISTORY' });
      loadHistory();
      showToast('History cleared');
    }
  }

  function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`;
    
    return date.toLocaleDateString();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SETTINGS
  // ═══════════════════════════════════════════════════════════════════════════

  function applySettings() {
    if (elements.settingFloatingButton) {
      elements.settingFloatingButton.checked = settings.showFloatingButton !== false;
    }
    if (elements.settingNotifications) {
      elements.settingNotifications.checked = settings.showNotifications !== false;
    }
    if (elements.settingStoreHistory) {
      elements.settingStoreHistory.checked = settings.storeHistory !== false;
    }
    if (elements.settingAnonymousData) {
      elements.settingAnonymousData.checked = settings.sendAnonymousData === true;
    }
  }

  async function loadSettings() {
    // Update account section
    if (elements.accountSection) {
      if (userState.userId) {
        elements.accountSection.innerHTML = `
          <div class="account-info">
            <span class="account-status">✅ Connected</span>
            <a href="${CONFIG.webAppUrl}/dashboard" target="_blank" class="account-link">
              Open Dashboard →
            </a>
          </div>
        `;
      } else {
        elements.accountSection.innerHTML = `
          <div class="account-prompt">
            <p>Connect to sync your analyses and unlock all features.</p>
            <a href="${CONFIG.webAppUrl}/auth/login.html?source=extension" target="_blank" class="btn-connect">
              Connect Account
            </a>
          </div>
        `;
      }
    }
  }

  async function updateSetting(key, value) {
    settings[key] = value;
    await sendMessage({ type: 'UPDATE_SETTING', key, value });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // UTILITIES
  // ═══════════════════════════════════════════════════════════════════════════

  function sendMessage(message) {
    return new Promise((resolve, reject) => {
      try {
        chrome.runtime.sendMessage(message, response => {
          if (chrome.runtime.lastError) {
            console.warn('Message error:', chrome.runtime.lastError);
            resolve(null);
          } else {
            resolve(response);
          }
        });
      } catch (error) {
        console.warn('Send message error:', error);
        resolve(null);
      }
    });
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // STARTUP
  // ═══════════════════════════════════════════════════════════════════════════

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();
