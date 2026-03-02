/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EXTENSION - Storage Manager
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Manages all extension data:
 * - User authentication state
 * - Analysis history (local)
 * - Cached patterns
 * - Settings/preferences
 * - Sync queue for when online
 */

// Storage keys
const STORAGE_KEYS = {
  // Auth
  USER_ID: 'quirrely_user_id',
  USER_EMAIL: 'quirrely_user_email',
  USER_TIER: 'quirrely_user_tier',
  AUTH_TOKEN: 'quirrely_auth_token',
  SESSION_ID: 'quirrely_session_id',
  
  // Trial
  TRIAL_STARTED: 'quirrely_trial_started',
  TRIAL_ENDS: 'quirrely_trial_ends',
  
  // History
  ANALYSIS_HISTORY: 'quirrely_analysis_history',
  HISTORY_SYNC_QUEUE: 'quirrely_history_sync_queue',
  
  // Patterns
  PATTERN_CACHE: 'quirrely_pattern_cache',
  
  // Settings
  SETTINGS: 'quirrely_settings',
  
  // Stats
  DAILY_USAGE: 'quirrely_daily_usage',
  TOTAL_ANALYSES: 'quirrely_total_analyses'
};

// Default settings
const DEFAULT_SETTINGS = {
  // Analysis
  autoAnalyze: false,           // Auto-analyze on text selection
  minTextLength: 50,            // Minimum characters for analysis
  
  // Display
  showFloatingButton: true,     // Show analyze button on selection
  showNotifications: true,      // Show notification on analysis complete
  compactMode: false,           // Compact popup display
  
  // Privacy
  sendAnonymousData: true,      // Help improve LNCP
  storeHistory: true,           // Store analysis history locally
  
  // Sync
  autoSync: true,               // Sync when online
  syncOnStartup: true           // Sync history on extension startup
};

// Daily limits by tier
const DAILY_LIMITS = {
  anonymous: 3,
  free: 5,
  trial: 100,
  pro: 1000
};

class StorageManager {
  constructor() {
    this._cache = {};
    this._initialized = false;
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Initialization
  // ─────────────────────────────────────────────────────────────────────────
  
  async initialize() {
    if (this._initialized) return;
    
    // Generate session ID if not exists
    const sessionId = await this.get(STORAGE_KEYS.SESSION_ID);
    if (!sessionId) {
      await this.set(STORAGE_KEYS.SESSION_ID, this._generateSessionId());
    }
    
    // Ensure settings exist
    const settings = await this.get(STORAGE_KEYS.SETTINGS);
    if (!settings) {
      await this.set(STORAGE_KEYS.SETTINGS, DEFAULT_SETTINGS);
    }
    
    // Initialize history if needed
    const history = await this.get(STORAGE_KEYS.ANALYSIS_HISTORY);
    if (!history) {
      await this.set(STORAGE_KEYS.ANALYSIS_HISTORY, []);
    }
    
    // Initialize daily usage
    await this._initializeDailyUsage();
    
    this._initialized = true;
  }
  
  _generateSessionId() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let id = 'ext-';
    for (let i = 0; i < 16; i++) {
      id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return id;
  }
  
  async _initializeDailyUsage() {
    const usage = await this.get(STORAGE_KEYS.DAILY_USAGE) || {};
    const today = this._getToday();
    
    if (!usage[today]) {
      usage[today] = 0;
      // Clean old entries (keep last 7 days)
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 7);
      const cutoffStr = cutoff.toISOString().split('T')[0];
      
      for (const date of Object.keys(usage)) {
        if (date < cutoffStr) delete usage[date];
      }
      
      await this.set(STORAGE_KEYS.DAILY_USAGE, usage);
    }
  }
  
  _getToday() {
    return new Date().toISOString().split('T')[0];
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Core Storage Operations
  // ─────────────────────────────────────────────────────────────────────────
  
  async get(key) {
    return new Promise((resolve) => {
      chrome.storage.local.get([key], (result) => {
        resolve(result[key]);
      });
    });
  }
  
  async set(key, value) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [key]: value }, resolve);
    });
  }
  
  async remove(key) {
    return new Promise((resolve) => {
      chrome.storage.local.remove([key], resolve);
    });
  }
  
  async getMultiple(keys) {
    return new Promise((resolve) => {
      chrome.storage.local.get(keys, resolve);
    });
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Auth State
  // ─────────────────────────────────────────────────────────────────────────
  
  async isAuthenticated() {
    const userId = await this.get(STORAGE_KEYS.USER_ID);
    return !!userId;
  }
  
  async getAuthState() {
    const data = await this.getMultiple([
      STORAGE_KEYS.USER_ID,
      STORAGE_KEYS.USER_EMAIL,
      STORAGE_KEYS.USER_TIER,
      STORAGE_KEYS.SESSION_ID,
      STORAGE_KEYS.TRIAL_STARTED,
      STORAGE_KEYS.TRIAL_ENDS
    ]);
    
    const isAuthenticated = !!data[STORAGE_KEYS.USER_ID];
    let effectiveTier = data[STORAGE_KEYS.USER_TIER] || 'anonymous';
    
    // Check trial status
    if (effectiveTier === 'free' && data[STORAGE_KEYS.TRIAL_ENDS]) {
      const trialEnds = new Date(data[STORAGE_KEYS.TRIAL_ENDS]);
      if (trialEnds > new Date()) {
        effectiveTier = 'trial';
      }
    }
    
    return {
      isAuthenticated,
      userId: data[STORAGE_KEYS.USER_ID],
      email: data[STORAGE_KEYS.USER_EMAIL],
      tier: data[STORAGE_KEYS.USER_TIER] || 'anonymous',
      effectiveTier,
      sessionId: data[STORAGE_KEYS.SESSION_ID],
      trialStarted: data[STORAGE_KEYS.TRIAL_STARTED],
      trialEnds: data[STORAGE_KEYS.TRIAL_ENDS]
    };
  }
  
  async setAuthState(userId, email, tier, token = null) {
    await this.set(STORAGE_KEYS.USER_ID, userId);
    await this.set(STORAGE_KEYS.USER_EMAIL, email);
    await this.set(STORAGE_KEYS.USER_TIER, tier);
    if (token) {
      await this.set(STORAGE_KEYS.AUTH_TOKEN, token);
    }
  }
  
  async clearAuth() {
    await this.remove(STORAGE_KEYS.USER_ID);
    await this.remove(STORAGE_KEYS.USER_EMAIL);
    await this.remove(STORAGE_KEYS.USER_TIER);
    await this.remove(STORAGE_KEYS.AUTH_TOKEN);
    // Keep session ID for anonymous tracking
  }
  
  async startTrial() {
    const now = new Date();
    const ends = new Date(now);
    ends.setDate(ends.getDate() + 7);
    
    await this.set(STORAGE_KEYS.TRIAL_STARTED, now.toISOString());
    await this.set(STORAGE_KEYS.TRIAL_ENDS, ends.toISOString());
    
    return {
      started: now.toISOString(),
      ends: ends.toISOString(),
      daysRemaining: 7
    };
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Analysis History
  // ─────────────────────────────────────────────────────────────────────────
  
  async addAnalysis(analysis) {
    const settings = await this.getSettings();
    if (!settings.storeHistory) return null;
    
    const history = await this.get(STORAGE_KEYS.ANALYSIS_HISTORY) || [];
    
    const entry = {
      id: this._generateId(),
      timestamp: new Date().toISOString(),
      profileId: analysis.profileId,
      profileType: analysis.profileType,
      stance: analysis.stance,
      title: analysis.title,
      confidence: analysis.confidence,
      wordCount: analysis.metrics?.wordCount || 0,
      source: analysis.source || 'extension',
      url: analysis.url || null,
      inputPreview: analysis.inputPreview || null,
      signature: analysis.signature || null,
      synced: false
    };
    
    history.unshift(entry);
    
    // Keep max 100 entries
    if (history.length > 100) {
      history.splice(100);
    }
    
    await this.set(STORAGE_KEYS.ANALYSIS_HISTORY, history);
    
    // Add to sync queue if authenticated
    const auth = await this.getAuthState();
    if (auth.isAuthenticated && settings.autoSync) {
      await this._addToSyncQueue(entry);
    }
    
    // Update daily usage
    await this._incrementDailyUsage();
    
    // Update total
    const total = (await this.get(STORAGE_KEYS.TOTAL_ANALYSES)) || 0;
    await this.set(STORAGE_KEYS.TOTAL_ANALYSES, total + 1);
    
    return entry;
  }
  
  async getHistory(limit = 20) {
    const history = await this.get(STORAGE_KEYS.ANALYSIS_HISTORY) || [];
    return history.slice(0, limit);
  }
  
  async clearHistory() {
    await this.set(STORAGE_KEYS.ANALYSIS_HISTORY, []);
    await this.set(STORAGE_KEYS.HISTORY_SYNC_QUEUE, []);
  }
  
  async _addToSyncQueue(entry) {
    const queue = await this.get(STORAGE_KEYS.HISTORY_SYNC_QUEUE) || [];
    queue.push(entry);
    await this.set(STORAGE_KEYS.HISTORY_SYNC_QUEUE, queue);
  }
  
  async getSyncQueue() {
    return await this.get(STORAGE_KEYS.HISTORY_SYNC_QUEUE) || [];
  }
  
  async clearSyncQueue() {
    await this.set(STORAGE_KEYS.HISTORY_SYNC_QUEUE, []);
  }
  
  async markSynced(ids) {
    const history = await this.get(STORAGE_KEYS.ANALYSIS_HISTORY) || [];
    
    for (const entry of history) {
      if (ids.includes(entry.id)) {
        entry.synced = true;
      }
    }
    
    await this.set(STORAGE_KEYS.ANALYSIS_HISTORY, history);
  }
  
  _generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Usage Limits
  // ─────────────────────────────────────────────────────────────────────────
  
  async checkDailyLimit() {
    const auth = await this.getAuthState();
    const limit = DAILY_LIMITS[auth.effectiveTier] || DAILY_LIMITS.anonymous;
    
    const usage = await this.get(STORAGE_KEYS.DAILY_USAGE) || {};
    const today = this._getToday();
    const used = usage[today] || 0;
    
    return {
      allowed: used < limit,
      used,
      limit,
      remaining: Math.max(0, limit - used),
      tier: auth.effectiveTier,
      resetsAt: `${today}T23:59:59Z`
    };
  }
  
  async _incrementDailyUsage() {
    const usage = await this.get(STORAGE_KEYS.DAILY_USAGE) || {};
    const today = this._getToday();
    usage[today] = (usage[today] || 0) + 1;
    await this.set(STORAGE_KEYS.DAILY_USAGE, usage);
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Settings
  // ─────────────────────────────────────────────────────────────────────────
  
  async getSettings() {
    const settings = await this.get(STORAGE_KEYS.SETTINGS);
    return { ...DEFAULT_SETTINGS, ...settings };
  }
  
  async updateSettings(updates) {
    const current = await this.getSettings();
    const newSettings = { ...current, ...updates };
    await this.set(STORAGE_KEYS.SETTINGS, newSettings);
    return newSettings;
  }
  
  async resetSettings() {
    await this.set(STORAGE_KEYS.SETTINGS, DEFAULT_SETTINGS);
    return DEFAULT_SETTINGS;
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Stats
  // ─────────────────────────────────────────────────────────────────────────
  
  async getStats() {
    const history = await this.get(STORAGE_KEYS.ANALYSIS_HISTORY) || [];
    const total = await this.get(STORAGE_KEYS.TOTAL_ANALYSES) || 0;
    const usage = await this.get(STORAGE_KEYS.DAILY_USAGE) || {};
    
    // Profile distribution
    const profileCounts = {};
    const stanceCounts = {};
    
    for (const entry of history) {
      profileCounts[entry.profileType] = (profileCounts[entry.profileType] || 0) + 1;
      stanceCounts[entry.stance] = (stanceCounts[entry.stance] || 0) + 1;
    }
    
    // Find dominant
    let dominantProfile = null, maxProfileCount = 0;
    for (const [profile, count] of Object.entries(profileCounts)) {
      if (count > maxProfileCount) {
        maxProfileCount = count;
        dominantProfile = profile;
      }
    }
    
    let dominantStance = null, maxStanceCount = 0;
    for (const [stance, count] of Object.entries(stanceCounts)) {
      if (count > maxStanceCount) {
        maxStanceCount = count;
        dominantStance = stance;
      }
    }
    
    // Weekly trend
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      last7Days.push({
        date: dateStr,
        count: usage[dateStr] || 0
      });
    }
    
    return {
      totalAnalyses: total,
      historyCount: history.length,
      profileDistribution: profileCounts,
      stanceDistribution: stanceCounts,
      dominantProfile,
      dominantStance,
      weeklyTrend: last7Days,
      todayCount: usage[this._getToday()] || 0
    };
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Pattern Cache
  // ─────────────────────────────────────────────────────────────────────────
  
  async cachePattern(signature, data) {
    const cache = await this.get(STORAGE_KEYS.PATTERN_CACHE) || {};
    cache[signature] = {
      ...data,
      cachedAt: new Date().toISOString()
    };
    
    // Keep max 200 patterns
    const keys = Object.keys(cache);
    if (keys.length > 200) {
      // Remove oldest
      keys.sort((a, b) => new Date(cache[a].cachedAt) - new Date(cache[b].cachedAt));
      for (let i = 0; i < keys.length - 200; i++) {
        delete cache[keys[i]];
      }
    }
    
    await this.set(STORAGE_KEYS.PATTERN_CACHE, cache);
  }
  
  async getPatternFromCache(signature) {
    const cache = await this.get(STORAGE_KEYS.PATTERN_CACHE) || {};
    return cache[signature] || null;
  }
}

// Export singleton
const storage = new StorageManager();

if (typeof window !== 'undefined') {
  window.QuirrelyStorage = storage;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = storage;
}
