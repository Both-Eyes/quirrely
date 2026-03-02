/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY EXTENSION - API Client
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Handles communication with Quirrely backend:
 * - Authentication
 * - Analysis sync
 * - Pattern reporting
 * - Feature access checks
 * 
 * Designed to work offline-first with sync when available.
 */

// API Configuration
const API_CONFIG = {
  // Production (update when deployed)
  baseUrl: 'https://api.quirrely.com',
  
  // Development fallback
  devUrl: 'http://localhost:8000',
  
  // Timeout in ms
  timeout: 10000,
  
  // Retry settings
  maxRetries: 3,
  retryDelay: 1000
};

class APIClient {
  constructor() {
    this._baseUrl = API_CONFIG.baseUrl;
    this._storage = null;
    this._online = navigator.onLine;
    
    // Listen for online/offline
    window.addEventListener('online', () => { this._online = true; this._onOnline(); });
    window.addEventListener('offline', () => { this._online = false; });
  }
  
  setStorage(storage) {
    this._storage = storage;
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Core Request Methods
  // ─────────────────────────────────────────────────────────────────────────
  
  async _request(method, endpoint, data = null, options = {}) {
    if (!this._online && !options.allowOffline) {
      throw new Error('Offline - request queued');
    }
    
    const url = `${this._baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Add auth headers if available
    if (this._storage) {
      const auth = await this._storage.getAuthState();
      if (auth.userId) {
        headers['X-User-Id'] = auth.userId;
      }
      headers['X-Session-Id'] = auth.sessionId;
    }
    
    const fetchOptions = {
      method,
      headers,
      ...(data && { body: JSON.stringify(data) })
    };
    
    // Timeout wrapper
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeout || API_CONFIG.timeout);
    fetchOptions.signal = controller.signal;
    
    try {
      const response = await fetch(url, fetchOptions);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new APIError(response.status, error.detail || 'Request failed');
      }
      
      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new APIError(408, 'Request timeout');
      }
      
      throw error;
    }
  }
  
  async get(endpoint, options = {}) {
    return this._request('GET', endpoint, null, options);
  }
  
  async post(endpoint, data, options = {}) {
    return this._request('POST', endpoint, data, options);
  }
  
  async put(endpoint, data, options = {}) {
    return this._request('PUT', endpoint, data, options);
  }
  
  async delete(endpoint, options = {}) {
    return this._request('DELETE', endpoint, null, options);
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Connection Status
  // ─────────────────────────────────────────────────────────────────────────
  
  isOnline() {
    return this._online;
  }
  
  async checkConnection() {
    try {
      await this.get('/api/v2/health', { timeout: 5000 });
      this._online = true;
      return true;
    } catch {
      this._online = false;
      return false;
    }
  }
  
  async _onOnline() {
    // Trigger sync when coming back online
    if (this._storage) {
      await this.syncHistory();
    }
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Authentication
  // ─────────────────────────────────────────────────────────────────────────
  
  async register(email, password) {
    const sessionId = this._storage ? (await this._storage.getAuthState()).sessionId : null;
    
    const response = await this.post('/api/v2/auth/register', {
      email,
      password,
      session_id: sessionId
    });
    
    if (response.success && this._storage) {
      await this._storage.setAuthState(
        response.user_id,
        email,
        response.tier || 'free',
        response.token
      );
    }
    
    return response;
  }
  
  async login(email, password) {
    const response = await this.post('/api/v2/auth/login', { email, password });
    
    if (response.success && this._storage) {
      await this._storage.setAuthState(
        response.user_id,
        email,
        response.tier || 'free',
        response.token
      );
      
      // Sync after login
      await this.syncHistory();
    }
    
    return response;
  }
  
  async logout() {
    try {
      await this.post('/api/v2/auth/logout', {});
    } catch {
      // Ignore errors on logout
    }
    
    if (this._storage) {
      await this._storage.clearAuth();
    }
  }
  
  async linkSession(sessionId) {
    return await this.post('/api/v2/auth/link-session', { session_id: sessionId });
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Trial
  // ─────────────────────────────────────────────────────────────────────────
  
  async startTrial() {
    const response = await this.post('/api/v2/trial/start', {});
    
    if (response.success && this._storage) {
      await this._storage.startTrial();
    }
    
    return response;
  }
  
  async getTrialStatus() {
    return await this.get('/api/v2/trial/status');
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Analysis
  // ─────────────────────────────────────────────────────────────────────────
  
  async analyzeText(text, options = {}) {
    return await this.post('/api/v2/analyze', {
      text,
      source: options.source || 'extension'
    });
  }
  
  async submitPattern(analysis) {
    // Submit pattern for virtuous cycle
    // Only sends if user has opted in
    if (!this._storage) return;
    
    const settings = await this._storage.getSettings();
    if (!settings.sendAnonymousData) return;
    
    try {
      await this.post('/api/v2/patterns/submit', {
        signature: analysis.signature,
        tokens: analysis.tokens,
        profile: analysis.profileType,
        stance: analysis.stance,
        word_count: analysis.metrics?.wordCount
      });
    } catch {
      // Silently fail pattern submission
    }
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // History Sync
  // ─────────────────────────────────────────────────────────────────────────
  
  async syncHistory() {
    if (!this._storage || !this._online) return { synced: 0 };
    
    const auth = await this._storage.getAuthState();
    if (!auth.isAuthenticated) return { synced: 0 };
    
    const queue = await this._storage.getSyncQueue();
    if (queue.length === 0) return { synced: 0 };
    
    try {
      const response = await this.post('/api/v2/history/sync', {
        entries: queue
      });
      
      if (response.success) {
        await this._storage.markSynced(queue.map(e => e.id));
        await this._storage.clearSyncQueue();
        return { synced: queue.length };
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
    
    return { synced: 0 };
  }
  
  async getRemoteHistory(limit = 20) {
    return await this.get(`/api/v2/user/history?limit=${limit}`);
  }
  
  async getEvolution(days = 30) {
    return await this.get(`/api/v2/user/evolution?days=${days}`);
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // Features
  // ─────────────────────────────────────────────────────────────────────────
  
  async checkFeature(featureKey) {
    try {
      return await this.get(`/api/v2/features/check/${featureKey}`);
    } catch {
      // Default to restrictive on error
      return { allowed: false, reason: 'Unable to verify' };
    }
  }
  
  async getAllFeatures() {
    return await this.get('/api/v2/features');
  }
  
  // ─────────────────────────────────────────────────────────────────────────
  // User
  // ─────────────────────────────────────────────────────────────────────────
  
  async getTier() {
    return await this.get('/api/v2/user/tier');
  }
  
  async getProfile() {
    return await this.get('/api/v2/user/profile');
  }
}

// Custom error class
class APIError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Export singleton
const api = new APIClient();

if (typeof window !== 'undefined') {
  window.QuirrelyAPI = api;
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = api;
}
