/**
 * LNCP Blog Tracking Script v1.0
 * 
 * Tracks user behavior on blog pages for optimization:
 * - Page views
 * - Scroll depth
 * - Time on page
 * - CTA impressions and clicks
 * - A/B experiment assignments
 * 
 * Usage:
 *   <script src="/js/lncp-tracker.js"></script>
 *   <script>
 *     LNCPTracker.init({
 *       endpoint: '/api/track',
 *       debug: false,
 *     });
 *   </script>
 */

(function(window, document) {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════════════

  const DEFAULT_CONFIG = {
    endpoint: '/api/track',
    batchSize: 10,
    batchInterval: 5000,  // 5 seconds
    heartbeatInterval: 30000,  // 30 seconds
    scrollDepthMarks: [25, 50, 75, 90, 100],
    debug: false,
    cookieDomain: '',
    visitorIdKey: 'lncp_vid',
    sessionIdKey: 'lncp_sid',
    sessionTimeout: 30 * 60 * 1000,  // 30 minutes
  };

  // ═══════════════════════════════════════════════════════════════════════
  // UTILITIES
  // ═══════════════════════════════════════════════════════════════════════

  function generateId(prefix = '') {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substring(2, 10);
    return prefix + timestamp + random;
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function setCookie(name, value, days = 365) {
    const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
  }

  function getScrollDepth() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const docHeight = Math.max(
      document.body.scrollHeight,
      document.documentElement.scrollHeight
    );
    const winHeight = window.innerHeight;
    const scrollPercent = Math.round((scrollTop / (docHeight - winHeight)) * 100);
    return Math.min(100, Math.max(0, scrollPercent));
  }

  function getPageInfo() {
    // Extract profile info from URL if present
    const url = window.location.pathname;
    const match = url.match(/how-(\w+)-(\w+)-writers-write/);
    
    return {
      url: url,
      title: document.title,
      referrer: document.referrer,
      profileStyle: match ? match[1] : null,
      profileCertitude: match ? match[2] : null,
    };
  }

  function getDeviceInfo() {
    const ua = navigator.userAgent;
    let device = 'desktop';
    
    if (/Mobile|Android|iPhone|iPad/.test(ua)) {
      device = /iPad|Tablet/.test(ua) ? 'tablet' : 'mobile';
    }
    
    return {
      device: device,
      screenWidth: window.screen.width,
      screenHeight: window.screen.height,
      language: navigator.language,
    };
  }

  function getTrafficSource() {
    const referrer = document.referrer;
    const params = new URLSearchParams(window.location.search);
    
    // Check UTM parameters first
    if (params.get('utm_source')) {
      const source = params.get('utm_source').toLowerCase();
      if (source.includes('google') || source.includes('bing')) return 'paid';
      if (source.includes('facebook') || source.includes('twitter') || source.includes('linkedin')) return 'social';
      if (source.includes('email') || source.includes('newsletter')) return 'email';
      return 'referral';
    }
    
    // Check referrer
    if (!referrer) return 'direct';
    
    const ref = referrer.toLowerCase();
    if (ref.includes('google.') || ref.includes('bing.') || ref.includes('yahoo.') || ref.includes('duckduckgo.')) {
      return 'organic';
    }
    if (ref.includes('facebook.') || ref.includes('twitter.') || ref.includes('linkedin.') || ref.includes('instagram.')) {
      return 'social';
    }
    if (ref.includes(window.location.hostname)) {
      return 'internal';
    }
    
    return 'referral';
  }

  // ═══════════════════════════════════════════════════════════════════════
  // TRACKER CLASS
  // ═══════════════════════════════════════════════════════════════════════

  class LNCPTracker {
    constructor() {
      this.config = { ...DEFAULT_CONFIG };
      this.initialized = false;
      this.eventQueue = [];
      this.visitorId = null;
      this.sessionId = null;
      this.viewId = null;
      this.pageStartTime = Date.now();
      this.maxScrollDepth = 0;
      this.scrollMarksReached = new Set();
      this.ctaImpressions = new Set();
      this.experimentAssignments = {};
      this.heartbeatTimer = null;
      this.batchTimer = null;
    }

    // ─────────────────────────────────────────────────────────────────────
    // INITIALIZATION
    // ─────────────────────────────────────────────────────────────────────

    init(options = {}) {
      if (this.initialized) {
        this.log('Already initialized');
        return;
      }

      this.config = { ...this.config, ...options };
      this.log('Initializing with config:', this.config);

      // Set up visitor and session
      this.initIdentity();

      // Generate view ID
      this.viewId = generateId('view_');

      // Track page view
      this.trackPageView();

      // Set up event listeners
      this.setupEventListeners();

      // Start heartbeat
      this.startHeartbeat();

      // Start batch timer
      this.startBatchTimer();

      this.initialized = true;
      this.log('Initialized successfully');
    }

    initIdentity() {
      // Visitor ID (persistent)
      this.visitorId = getCookie(this.config.visitorIdKey);
      if (!this.visitorId) {
        this.visitorId = generateId('vis_');
        setCookie(this.config.visitorIdKey, this.visitorId, 365);
      }

      // Session ID (expires after inactivity)
      const sessionData = this.getSessionData();
      if (sessionData && (Date.now() - sessionData.lastActivity) < this.config.sessionTimeout) {
        this.sessionId = sessionData.sessionId;
        this.updateSessionActivity();
      } else {
        this.sessionId = generateId('sess_');
        this.updateSessionActivity();
      }

      this.log('Identity:', { visitorId: this.visitorId, sessionId: this.sessionId });
    }

    getSessionData() {
      try {
        const data = sessionStorage.getItem(this.config.sessionIdKey);
        return data ? JSON.parse(data) : null;
      } catch (e) {
        return null;
      }
    }

    updateSessionActivity() {
      try {
        sessionStorage.setItem(this.config.sessionIdKey, JSON.stringify({
          sessionId: this.sessionId,
          lastActivity: Date.now(),
        }));
      } catch (e) {
        // Storage might be disabled
      }
    }

    // ─────────────────────────────────────────────────────────────────────
    // EVENT TRACKING
    // ─────────────────────────────────────────────────────────────────────

    trackPageView() {
      const pageInfo = getPageInfo();
      const deviceInfo = getDeviceInfo();
      const source = getTrafficSource();

      this.queueEvent('page_view', {
        viewId: this.viewId,
        ...pageInfo,
        ...deviceInfo,
        source: source,
      });
    }

    trackScroll(depth) {
      if (depth > this.maxScrollDepth) {
        this.maxScrollDepth = depth;

        // Check scroll marks
        for (const mark of this.config.scrollDepthMarks) {
          if (depth >= mark && !this.scrollMarksReached.has(mark)) {
            this.scrollMarksReached.add(mark);
            this.queueEvent('scroll_depth', {
              viewId: this.viewId,
              depth: mark,
              timeOnPage: this.getTimeOnPage(),
            });
          }
        }
      }
    }

    trackEngagement() {
      this.queueEvent('engagement', {
        viewId: this.viewId,
        timeOnPage: this.getTimeOnPage(),
        scrollDepth: this.maxScrollDepth,
      });
    }

    trackCTAImpression(ctaId, variantId, placement, position = 0) {
      const key = `${ctaId}_${variantId}_${placement}`;
      if (this.ctaImpressions.has(key)) return;

      this.ctaImpressions.add(key);

      this.queueEvent('cta_impression', {
        viewId: this.viewId,
        ctaId: ctaId,
        variantId: variantId,
        placement: placement,
        position: position,
        scrollDepth: this.maxScrollDepth,
        timeOnPage: this.getTimeOnPage(),
        experimentId: this.experimentAssignments[ctaId] || null,
      });
    }

    trackCTAClick(ctaId, variantId, placement, position = 0) {
      this.queueEvent('cta_click', {
        viewId: this.viewId,
        ctaId: ctaId,
        variantId: variantId,
        placement: placement,
        position: position,
        scrollDepth: this.maxScrollDepth,
        timeOnPage: this.getTimeOnPage(),
        experimentId: this.experimentAssignments[ctaId] || null,
      });
    }

    trackConversion(conversionType, metadata = {}) {
      this.queueEvent('conversion', {
        viewId: this.viewId,
        conversionType: conversionType,
        timeOnPage: this.getTimeOnPage(),
        ...metadata,
      });
    }

    // ─────────────────────────────────────────────────────────────────────
    // A/B EXPERIMENTS
    // ─────────────────────────────────────────────────────────────────────

    getExperimentVariant(experimentId, variants) {
      // Deterministic assignment based on visitor ID
      const hash = this.hashString(`${experimentId}:${this.visitorId}`);
      const index = hash % variants.length;
      const variant = variants[index];

      this.experimentAssignments[experimentId] = experimentId;

      this.queueEvent('experiment_assignment', {
        viewId: this.viewId,
        experimentId: experimentId,
        variantId: variant.id,
        variantName: variant.name,
      });

      return variant;
    }

    hashString(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }
      return Math.abs(hash);
    }

    // ─────────────────────────────────────────────────────────────────────
    // EVENT QUEUE & SENDING
    // ─────────────────────────────────────────────────────────────────────

    queueEvent(eventType, data) {
      const event = {
        type: eventType,
        timestamp: new Date().toISOString(),
        visitorId: this.visitorId,
        sessionId: this.sessionId,
        pageUrl: window.location.pathname,
        ...data,
      };

      this.eventQueue.push(event);
      this.log('Queued event:', event);

      // Immediate send for important events
      if (['cta_click', 'conversion'].includes(eventType)) {
        this.flushEvents();
      }

      // Check batch size
      if (this.eventQueue.length >= this.config.batchSize) {
        this.flushEvents();
      }
    }

    async flushEvents() {
      if (this.eventQueue.length === 0) return;

      const events = [...this.eventQueue];
      this.eventQueue = [];

      try {
        const response = await fetch(this.config.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            events: events,
            meta: {
              trackerVersion: '1.0',
              userAgent: navigator.userAgent,
            },
          }),
          keepalive: true,
        });

        if (!response.ok) {
          // Put events back in queue on failure
          this.eventQueue = [...events, ...this.eventQueue];
          this.log('Failed to send events, re-queued');
        } else {
          this.log('Sent', events.length, 'events');
        }
      } catch (error) {
        // Put events back in queue on error
        this.eventQueue = [...events, ...this.eventQueue];
        this.log('Error sending events:', error);
      }
    }

    // ─────────────────────────────────────────────────────────────────────
    // EVENT LISTENERS
    // ─────────────────────────────────────────────────────────────────────

    setupEventListeners() {
      // Scroll tracking
      let scrollTimeout;
      window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
          this.trackScroll(getScrollDepth());
        }, 100);
      }, { passive: true });

      // Visibility change (tab switch)
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
          this.trackEngagement();
          this.flushEvents();
        }
      });

      // Page unload
      window.addEventListener('beforeunload', () => {
        this.trackEngagement();
        this.flushEvents();
      });

      // CTA click tracking (delegated)
      document.addEventListener('click', (e) => {
        const cta = e.target.closest('[data-lncp-cta]');
        if (cta) {
          this.trackCTAClick(
            cta.dataset.lncpCta,
            cta.dataset.lncpVariant || 'default',
            cta.dataset.lncpPlacement || 'unknown',
            parseInt(cta.dataset.lncpPosition || '0', 10)
          );
        }
      });

      // CTA impression tracking with IntersectionObserver
      if ('IntersectionObserver' in window) {
        this.setupCTAImpressionObserver();
      }
    }

    setupCTAImpressionObserver() {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const cta = entry.target;
            this.trackCTAImpression(
              cta.dataset.lncpCta,
              cta.dataset.lncpVariant || 'default',
              cta.dataset.lncpPlacement || 'unknown',
              parseInt(cta.dataset.lncpPosition || '0', 10)
            );
          }
        });
      }, {
        threshold: 0.5,  // 50% visible
      });

      // Observe all CTAs
      document.querySelectorAll('[data-lncp-cta]').forEach((cta) => {
        observer.observe(cta);
      });

      // Also observe dynamically added CTAs
      const mutationObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              if (node.hasAttribute && node.hasAttribute('data-lncp-cta')) {
                observer.observe(node);
              }
              node.querySelectorAll && node.querySelectorAll('[data-lncp-cta]').forEach((cta) => {
                observer.observe(cta);
              });
            }
          });
        });
      });

      mutationObserver.observe(document.body, {
        childList: true,
        subtree: true,
      });
    }

    // ─────────────────────────────────────────────────────────────────────
    // TIMERS
    // ─────────────────────────────────────────────────────────────────────

    startHeartbeat() {
      this.heartbeatTimer = setInterval(() => {
        this.updateSessionActivity();
        this.trackEngagement();
      }, this.config.heartbeatInterval);
    }

    startBatchTimer() {
      this.batchTimer = setInterval(() => {
        this.flushEvents();
      }, this.config.batchInterval);
    }

    getTimeOnPage() {
      return Math.round((Date.now() - this.pageStartTime) / 1000);
    }

    // ─────────────────────────────────────────────────────────────────────
    // HELPERS
    // ─────────────────────────────────────────────────────────────────────

    log(...args) {
      if (this.config.debug) {
        console.log('[LNCP Tracker]', ...args);
      }
    }

    // Public API for manual tracking
    track(eventType, data = {}) {
      this.queueEvent(eventType, {
        viewId: this.viewId,
        ...data,
      });
    }

    // Get current visitor/session for external use
    getIdentity() {
      return {
        visitorId: this.visitorId,
        sessionId: this.sessionId,
        viewId: this.viewId,
      };
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  // EXPORT
  // ═══════════════════════════════════════════════════════════════════════

  window.LNCPTracker = new LNCPTracker();

})(window, document);
