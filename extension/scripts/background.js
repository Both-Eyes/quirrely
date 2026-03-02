/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EXTENSION - Background Service Worker
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Handles:
 * - Context menu creation
 * - Message routing between popup/content scripts
 * - Keyboard shortcut handling
 * - Periodic sync
 * - Badge updates
 */

// Import modules (service worker context)
importScripts('lncp-classifier.js');

// ═══════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════

let lastAnalysis = null;
let sessionId = null;

// ═══════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════

chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Quirrely extension installed/updated:', details.reason);
  
  // Create context menu
  chrome.contextMenus.create({
    id: 'quirrely-analyze',
    title: 'Analyze with Quirrely',
    contexts: ['selection']
  });
  
  // Initialize session ID
  const result = await chrome.storage.local.get(['quirrely_session_id']);
  if (!result.quirrely_session_id) {
    sessionId = generateSessionId();
    await chrome.storage.local.set({ quirrely_session_id: sessionId });
  } else {
    sessionId = result.quirrely_session_id;
  }
  
  // Set initial badge
  updateBadge(null);
  
  // Show welcome on install
  if (details.reason === 'install') {
    chrome.tabs.create({ url: 'pages/welcome.html' });
  }
});

chrome.runtime.onStartup.addListener(async () => {
  // Restore session ID
  const result = await chrome.storage.local.get(['quirrely_session_id']);
  sessionId = result.quirrely_session_id;
  
  // Schedule sync
  scheduleSync();
});

// ═══════════════════════════════════════════════════════════════════
// Context Menu
// ═══════════════════════════════════════════════════════════════════

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'quirrely-analyze' && info.selectionText) {
    await analyzeAndNotify(info.selectionText, tab);
  }
});

// ═══════════════════════════════════════════════════════════════════
// Keyboard Commands
// ═══════════════════════════════════════════════════════════════════

chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'analyze-selection') {
    // Get selected text from active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      try {
        const results = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: () => window.getSelection()?.toString() || ''
        });
        
        const selectedText = results[0]?.result;
        if (selectedText && selectedText.trim().length > 20) {
          await analyzeAndNotify(selectedText, tab);
        }
      } catch (error) {
        console.error('Failed to get selection:', error);
      }
    }
  }
});

// ═══════════════════════════════════════════════════════════════════
// Message Handling
// ═══════════════════════════════════════════════════════════════════

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message, sender).then(sendResponse);
  return true; // Keep channel open for async response
});

async function handleMessage(message, sender) {
  switch (message.type) {
    case 'ANALYZE_TEXT':
      return await analyzeText(message.text, message.options);
    
    case 'GET_LAST_ANALYSIS':
      return { success: true, analysis: lastAnalysis };
    
    case 'GET_HISTORY':
      return await getHistory(message.limit);
    
    case 'GET_STATS':
      return await getStats();
    
    case 'CHECK_LIMIT':
      return await checkDailyLimit();
    
    case 'GET_AUTH_STATE':
      return await getAuthState();
    
    case 'START_TRIAL':
      return await startTrial();
    
    case 'GET_SETTINGS':
      return await getSettings();
    
    case 'UPDATE_SETTINGS':
      return await updateSettings(message.settings);
    
    case 'SYNC_HISTORY':
      return await syncHistory();
    
    case 'CLEAR_HISTORY':
      return await clearHistory();
    
    // v2.0.0: Save analysis from popup
    case 'SAVE_ANALYSIS':
      return await saveAnalysisFromPopup(message.analysis);
    
    // v2.0.0: Sync with web app
    case 'SYNC_WITH_WEBAPP':
      return await syncWithWebApp();
    
    // v2.0.0: Track events
    case 'TRACK_EVENT':
      return await trackEvent(message.event, message.data);
    
    // v2.0.0: Logout
    case 'LOGOUT':
      return await handleLogout();
    
    // v2.0.0: Get user state for popup
    case 'GET_USER_STATE':
      return await getUserState();
    
    // v2.0.0: Get selected text
    case 'GET_SELECTION':
      return await getSelection();
    
    // v2.0.0: Update single setting
    case 'UPDATE_SETTING':
      return await updateSingleSetting(message.key, message.value);
    
    // v2.0.0: Track STRETCH CTA clicks
    case 'TRACK_STRETCH_CLICK':
      return await trackEvent('stretch_cta_click', { source: 'extension_popup' });
    
    default:
      return { success: false, error: 'Unknown message type' };
  }
}

// v2.0.0: Get full user state for popup
async function getUserState() {
  const result = await chrome.storage.local.get([
    'quirrely_user_id',
    'quirrely_user_tier',
    'quirrely_stretch_streak',
    'quirrely_stretch_eligible',
    'quirrely_daily_usage'
  ]);
  
  const today = new Date().toISOString().split('T')[0];
  const usage = result.quirrely_daily_usage || {};
  
  return {
    tier: result.quirrely_user_tier || 'free',
    userId: result.quirrely_user_id || null,
    stretchStreak: result.quirrely_stretch_streak || 0,
    stretchEligible: result.quirrely_stretch_eligible !== false,
    analysesToday: usage[today] || 0
  };
}

// v2.0.0: Get selected text from active tab
async function getSelection() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return { text: null };
    
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.getSelection()?.toString() || ''
    });
    
    return { text: result?.result || null };
  } catch (error) {
    console.warn('Could not get selection:', error);
    return { text: null };
  }
}

// v2.0.0: Update single setting
async function updateSingleSetting(key, value) {
  const settings = await getSettings();
  settings[key] = value;
  await chrome.storage.sync.set({ quirrely_settings: settings });
  return { success: true };

// v2.0.0: Save analysis from popup
async function saveAnalysisFromPopup(analysis) {
  if (!analysis) return { success: false, error: 'No analysis provided' };
  
  lastAnalysis = analysis;
  
  // Convert to history format
  const entry = {
    id: analysis.id || `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: analysis.timestamp || new Date().toISOString(),
    profile: analysis.profile,
    stance: analysis.stance,
    confidence: analysis.confidence,
    wordCount: analysis.wordCount,
    sentenceCount: analysis.sentenceCount,
    text: analysis.text,
    synced: false
  };
  
  // Get existing history
  const result = await chrome.storage.local.get(['quirrely_analysis_history', 'quirrely_daily_usage']);
  const history = result.quirrely_analysis_history || [];
  const usage = result.quirrely_daily_usage || {};
  
  // Add to history
  history.unshift(entry);
  if (history.length > 100) history.splice(100);
  
  // Update daily usage
  const today = new Date().toISOString().split('T')[0];
  usage[today] = (usage[today] || 0) + 1;
  
  await chrome.storage.local.set({
    quirrely_analysis_history: history,
    quirrely_daily_usage: usage
  });
  
  // Update badge
  updateBadge(analysis.profile?.toUpperCase());
  
  return { success: true };
}

// v2.0.0: Sync with web app for STRETCH data
async function syncWithWebApp() {
  try {
    // Try to fetch user data from web app
    const response = await fetch('https://api.quirrely.com/api/extension/sync', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Version': '2.0.0'
      },
      credentials: 'include' // Include cookies for auth
    });
    
    if (!response.ok) {
      // User not logged in or API unavailable
      return { success: false, error: 'Not authenticated' };
    }
    
    const data = await response.json();
    
    // Store user data locally
    if (data.user) {
      await chrome.storage.local.set({
        quirrely_user_id: data.user.id,
        quirrely_user_email: data.user.email,
        quirrely_user_tier: data.user.tier,
        quirrely_stretch_streak: data.stretch?.streak || 0,
        quirrely_stretch_completed: data.stretch?.completed || 0,
        quirrely_trial_ends: data.user.trialEnds
      });
    }
    
    return {
      success: true,
      data: {
        isAuthenticated: !!data.user,
        tier: data.user?.tier || 'free',
        stretchStreak: data.stretch?.streak || 0,
        stretchCompleted: data.stretch?.completed || 0,
        stretchEligible: data.stretch?.eligible !== false,
        trialDaysRemaining: data.user?.trialDaysRemaining || 0
      }
    };
  } catch (error) {
    console.warn('Web app sync failed:', error);
    
    // Return cached data if available
    const cached = await chrome.storage.local.get([
      'quirrely_user_tier',
      'quirrely_stretch_streak',
      'quirrely_stretch_completed'
    ]);
    
    return {
      success: true,
      data: {
        tier: cached.quirrely_user_tier || 'free',
        stretchStreak: cached.quirrely_stretch_streak || 0,
        stretchCompleted: cached.quirrely_stretch_completed || 0,
        stretchEligible: true
      }
    };
  }
}

// v2.0.0: Track events
async function trackEvent(event, data) {
  const settings = await getSettings();
  
  if (!settings.sendAnonymousData) {
    return { success: true, tracked: false };
  }
  
  try {
    await fetch('https://api.quirrely.com/api/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event,
        data,
        source: 'extension',
        version: '2.0.0',
        timestamp: new Date().toISOString()
      })
    });
    return { success: true, tracked: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// v2.0.0: Handle logout
async function handleLogout() {
  await chrome.storage.local.remove([
    'quirrely_user_id',
    'quirrely_user_email',
    'quirrely_user_tier',
    'quirrely_stretch_streak',
    'quirrely_stretch_completed',
    'quirrely_trial_started',
    'quirrely_trial_ends'
  ]);
  
  return { success: true };
}

// ═══════════════════════════════════════════════════════════════════
// Analysis
// ═══════════════════════════════════════════════════════════════════

async function analyzeText(text, options = {}) {
  // Check daily limit
  const limitCheck = await checkDailyLimit();
  if (!limitCheck.allowed) {
    return {
      success: false,
      error: 'Daily limit reached',
      limitInfo: limitCheck
    };
  }
  
  // Run local classification
  const analysis = LNCP.classifyProfile(text);
  
  if (analysis.error) {
    return { success: false, error: analysis.error };
  }
  
  // Add metadata
  analysis.analyzedAt = new Date().toISOString();
  analysis.source = options.source || 'extension';
  analysis.url = options.url || null;
  analysis.inputPreview = text.slice(0, 100);
  
  // Store last analysis
  lastAnalysis = analysis;
  
  // Save to history
  await saveToHistory(analysis);
  
  // Update badge
  updateBadge(analysis.profileType);
  
  return { success: true, analysis };
}

async function analyzeAndNotify(text, tab) {
  const result = await analyzeText(text, {
    source: 'context_menu',
    url: tab?.url
  });
  
  if (result.success) {
    // Show notification
    const settings = await getSettings();
    if (settings.showNotifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon-128.png',
        title: `${result.analysis.icon} ${result.analysis.title}`,
        message: result.analysis.tagline,
        contextMessage: `Confidence: ${Math.round(result.analysis.confidence * 100)}%`
      });
    }
    
    // Open popup or inject result
    // (User can click extension icon to see full results)
  } else {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon-128.png',
      title: 'Analysis Failed',
      message: result.error || 'Unable to analyze text'
    });
  }
}

// ═══════════════════════════════════════════════════════════════════
// Storage Helpers
// ═══════════════════════════════════════════════════════════════════

async function saveToHistory(analysis) {
  const result = await chrome.storage.local.get(['quirrely_analysis_history', 'quirrely_daily_usage', 'quirrely_total_analyses']);
  
  const history = result.quirrely_analysis_history || [];
  const usage = result.quirrely_daily_usage || {};
  const total = result.quirrely_total_analyses || 0;
  
  // Add to history
  const entry = {
    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: analysis.analyzedAt,
    profileId: analysis.profileId,
    profileType: analysis.profileType,
    stance: analysis.stance,
    title: analysis.title,
    icon: analysis.icon,
    confidence: analysis.confidence,
    wordCount: analysis.metrics?.wordCount || 0,
    source: analysis.source,
    url: analysis.url,
    inputPreview: analysis.inputPreview,
    signature: analysis.signature,
    synced: false
  };
  
  history.unshift(entry);
  if (history.length > 100) history.splice(100);
  
  // Update daily usage
  const today = new Date().toISOString().split('T')[0];
  usage[today] = (usage[today] || 0) + 1;
  
  // Clean old usage data
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 7);
  const cutoffStr = cutoff.toISOString().split('T')[0];
  for (const date of Object.keys(usage)) {
    if (date < cutoffStr) delete usage[date];
  }
  
  await chrome.storage.local.set({
    quirrely_analysis_history: history,
    quirrely_daily_usage: usage,
    quirrely_total_analyses: total + 1
  });
}

async function getHistory(limit = 20) {
  const result = await chrome.storage.local.get(['quirrely_analysis_history']);
  const history = result.quirrely_analysis_history || [];
  return { success: true, history: history.slice(0, limit) };
}

async function clearHistory() {
  await chrome.storage.local.set({
    quirrely_analysis_history: [],
    quirrely_history_sync_queue: []
  });
  return { success: true };
}

async function getStats() {
  const result = await chrome.storage.local.get([
    'quirrely_analysis_history',
    'quirrely_daily_usage',
    'quirrely_total_analyses'
  ]);
  
  const history = result.quirrely_analysis_history || [];
  const usage = result.quirrely_daily_usage || {};
  const total = result.quirrely_total_analyses || 0;
  
  // Profile distribution
  const profileCounts = {};
  const stanceCounts = {};
  
  for (const entry of history) {
    profileCounts[entry.profileType] = (profileCounts[entry.profileType] || 0) + 1;
    stanceCounts[entry.stance] = (stanceCounts[entry.stance] || 0) + 1;
  }
  
  // Dominant
  let dominantProfile = null, maxP = 0;
  for (const [p, c] of Object.entries(profileCounts)) {
    if (c > maxP) { maxP = c; dominantProfile = p; }
  }
  
  let dominantStance = null, maxS = 0;
  for (const [s, c] of Object.entries(stanceCounts)) {
    if (c > maxS) { maxS = c; dominantStance = s; }
  }
  
  // Weekly trend
  const last7Days = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    last7Days.push({ date: dateStr, count: usage[dateStr] || 0 });
  }
  
  const today = new Date().toISOString().split('T')[0];
  
  return {
    success: true,
    stats: {
      totalAnalyses: total,
      historyCount: history.length,
      profileDistribution: profileCounts,
      stanceDistribution: stanceCounts,
      dominantProfile,
      dominantStance,
      weeklyTrend: last7Days,
      todayCount: usage[today] || 0
    }
  };
}

async function checkDailyLimit() {
  const result = await chrome.storage.local.get([
    'quirrely_user_tier',
    'quirrely_trial_ends',
    'quirrely_daily_usage'
  ]);
  
  // Determine effective tier
  let tier = result.quirrely_user_tier || 'anonymous';
  
  if (tier === 'free' && result.quirrely_trial_ends) {
    const trialEnds = new Date(result.quirrely_trial_ends);
    if (trialEnds > new Date()) {
      tier = 'trial';
    }
  }
  
  const limits = { anonymous: 3, free: 5, trial: 100, pro: 1000 };
  const limit = limits[tier] || 3;
  
  const usage = result.quirrely_daily_usage || {};
  const today = new Date().toISOString().split('T')[0];
  const used = usage[today] || 0;
  
  return {
    allowed: used < limit,
    used,
    limit,
    remaining: Math.max(0, limit - used),
    tier
  };
}

// ═══════════════════════════════════════════════════════════════════
// Auth & Trial
// ═══════════════════════════════════════════════════════════════════

async function getAuthState() {
  const result = await chrome.storage.local.get([
    'quirrely_user_id',
    'quirrely_user_email',
    'quirrely_user_tier',
    'quirrely_session_id',
    'quirrely_trial_started',
    'quirrely_trial_ends'
  ]);
  
  let effectiveTier = result.quirrely_user_tier || 'anonymous';
  
  if (effectiveTier === 'free' && result.quirrely_trial_ends) {
    const trialEnds = new Date(result.quirrely_trial_ends);
    if (trialEnds > new Date()) {
      effectiveTier = 'trial';
    }
  }
  
  return {
    success: true,
    auth: {
      isAuthenticated: !!result.quirrely_user_id,
      userId: result.quirrely_user_id,
      email: result.quirrely_user_email,
      tier: result.quirrely_user_tier || 'anonymous',
      effectiveTier,
      sessionId: result.quirrely_session_id,
      trialStarted: result.quirrely_trial_started,
      trialEnds: result.quirrely_trial_ends
    }
  };
}

async function startTrial() {
  const now = new Date();
  const ends = new Date(now);
  ends.setDate(ends.getDate() + 7);
  
  await chrome.storage.local.set({
    quirrely_trial_started: now.toISOString(),
    quirrely_trial_ends: ends.toISOString()
  });
  
  return {
    success: true,
    trial: {
      started: now.toISOString(),
      ends: ends.toISOString(),
      daysRemaining: 7
    }
  };
}

// ═══════════════════════════════════════════════════════════════════
// Settings
// ═══════════════════════════════════════════════════════════════════

const DEFAULT_SETTINGS = {
  autoAnalyze: false,
  minTextLength: 50,
  showFloatingButton: true,
  showNotifications: true,
  compactMode: false,
  sendAnonymousData: true,
  storeHistory: true,
  autoSync: true,
  syncOnStartup: true
};

async function getSettings() {
  const result = await chrome.storage.local.get(['quirrely_settings']);
  return { ...DEFAULT_SETTINGS, ...result.quirrely_settings };
}

async function updateSettings(updates) {
  const current = await getSettings();
  const newSettings = { ...current, ...updates };
  await chrome.storage.local.set({ quirrely_settings: newSettings });
  return { success: true, settings: newSettings };
}

// ═══════════════════════════════════════════════════════════════════
// Sync
// ═══════════════════════════════════════════════════════════════════

async function syncHistory() {
  // This would sync with the API when online
  // For now, just mark as attempted
  return { success: true, synced: 0, message: 'Sync available when connected to Quirrely' };
}

function scheduleSync() {
  // Schedule periodic sync alarm
  chrome.alarms.create('quirrely-sync', { periodInMinutes: 30 });
}

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'quirrely-sync') {
    await syncHistory();
  }
});

// ═══════════════════════════════════════════════════════════════════
// Badge
// ═══════════════════════════════════════════════════════════════════

function updateBadge(profileType) {
  if (!profileType) {
    chrome.action.setBadgeText({ text: '' });
    return;
  }
  
  // Short abbreviations
  const abbrevs = {
    ASSERTIVE: 'AS', MINIMAL: 'MI', POETIC: 'PO', DENSE: 'DE',
    CONVERSATIONAL: 'CO', FORMAL: 'FO', INTERROGATIVE: 'IN',
    HEDGED: 'HE', PARALLEL: 'PA', LONGFORM: 'LO'
  };
  
  chrome.action.setBadgeText({ text: abbrevs[profileType] || '?' });
  chrome.action.setBadgeBackgroundColor({ color: '#FF6B5A' }); // Coral
}

// ═══════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════

function generateSessionId() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let id = 'ext-';
  for (let i = 0; i < 16; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
}
