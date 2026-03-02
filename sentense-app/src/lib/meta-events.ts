/**
 * LNCP Meta Events System
 * Version: 1.0.0
 * 
 * Emits user behavior events to the Meta orchestration system.
 * Uses sendBeacon for non-blocking, reliable delivery.
 * 
 * Usage:
 *   import { MetaEvents } from '@/lib/meta-events';
 *   
 *   // Emit a simple event
 *   MetaEvents.emit('page_view', { page: '/dashboard' });
 *   
 *   // Track feature usage
 *   MetaEvents.trackFeature('voice_profile', { duration_ms: 45000 });
 *   
 *   // Track conversions
 *   MetaEvents.trackConversion('signup', { tier: 'free', country: 'CA' });
 */

// ═══════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════

export interface MetaEvent {
  event: string;
  data: Record<string, unknown>;
  timestamp: number;
  sessionId: string;
  userId: string | null;
  page: string;
  userAgent: string;
  referrer: string;
}

export interface MetaEventOptions {
  /** Override the event endpoint */
  endpoint?: string;
  /** Include additional context */
  context?: Record<string, unknown>;
  /** Force synchronous send (use sparingly) */
  sync?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// SESSION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

const SESSION_KEY = 'quirrely_session_id';
const SESSION_EXPIRY_MS = 30 * 60 * 1000; // 30 minutes

/**
 * Generate a unique session ID
 */
const generateSessionId = (): string => {
  const timestamp = Date.now().toString(36);
  const randomPart = Math.random().toString(36).substring(2, 15);
  return `sess_${timestamp}_${randomPart}`;
};

/**
 * Get or create session ID
 */
const getSessionId = (): string => {
  try {
    const stored = sessionStorage.getItem(SESSION_KEY);
    if (stored) {
      const { id, expiry } = JSON.parse(stored);
      if (Date.now() < expiry) {
        // Extend session on activity
        sessionStorage.setItem(SESSION_KEY, JSON.stringify({
          id,
          expiry: Date.now() + SESSION_EXPIRY_MS,
        }));
        return id;
      }
    }
  } catch {
    // Ignore parsing errors
  }
  
  // Create new session
  const newId = generateSessionId();
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({
      id: newId,
      expiry: Date.now() + SESSION_EXPIRY_MS,
    }));
  } catch {
    // sessionStorage not available
  }
  return newId;
};

/**
 * Get current user ID from auth store (if available)
 */
const getCurrentUserId = (): string | null => {
  try {
    // Try to get from Zustand auth store
    const authState = localStorage.getItem('auth-storage');
    if (authState) {
      const parsed = JSON.parse(authState);
      return parsed?.state?.user?.id || null;
    }
  } catch {
    // Ignore errors
  }
  return null;
};

// ═══════════════════════════════════════════════════════════════════════════
// EVENT QUEUE (for offline/batching)
// ═══════════════════════════════════════════════════════════════════════════

const EVENT_QUEUE_KEY = 'quirrely_event_queue';
const MAX_QUEUE_SIZE = 100;

interface QueuedEvent {
  event: MetaEvent;
  attempts: number;
  lastAttempt: number;
}

/**
 * Get queued events
 */
const getEventQueue = (): QueuedEvent[] => {
  try {
    const stored = localStorage.getItem(EVENT_QUEUE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

/**
 * Add event to queue
 */
const queueEvent = (event: MetaEvent): void => {
  try {
    const queue = getEventQueue();
    queue.push({ event, attempts: 0, lastAttempt: 0 });
    
    // Trim queue if too large
    while (queue.length > MAX_QUEUE_SIZE) {
      queue.shift();
    }
    
    localStorage.setItem(EVENT_QUEUE_KEY, JSON.stringify(queue));
  } catch {
    // Storage full or not available
  }
};

/**
 * Clear event queue
 */
const clearEventQueue = (): void => {
  try {
    localStorage.removeItem(EVENT_QUEUE_KEY);
  } catch {
    // Ignore
  }
};

// ═══════════════════════════════════════════════════════════════════════════
// META EVENTS API
// ═══════════════════════════════════════════════════════════════════════════

const DEFAULT_ENDPOINT = '/api/meta/events';

export const MetaEvents = {
  /**
   * Configuration
   */
  config: {
    endpoint: DEFAULT_ENDPOINT,
    enabled: true,
    debug: process.env.NODE_ENV === 'development',
    batchSize: 10,
    flushInterval: 5000, // 5 seconds
  },

  /**
   * Enable/disable event emission
   */
  setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
  },

  /**
   * Emit a raw event
   */
  emit(eventName: string, data: Record<string, unknown> = {}, options: MetaEventOptions = {}): void {
    if (!this.config.enabled) return;

    const event: MetaEvent = {
      event: eventName,
      data,
      timestamp: Date.now(),
      sessionId: getSessionId(),
      userId: getCurrentUserId(),
      page: typeof window !== 'undefined' ? window.location.pathname : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      referrer: typeof document !== 'undefined' ? document.referrer : '',
    };

    // Add additional context
    if (options.context) {
      event.data = { ...event.data, ...options.context };
    }

    // Debug logging
    if (this.config.debug) {
      console.log('[MetaEvents]', eventName, event);
    }

    // Send the event
    this._send(event, options);
  },

  /**
   * Track a page view
   */
  trackPageView(page?: string, additionalData: Record<string, unknown> = {}): void {
    this.emit('page_view', {
      page: page || window.location.pathname,
      title: document.title,
      ...additionalData,
    });
  },

  /**
   * Track feature usage
   */
  trackFeature(feature: string, data: Record<string, unknown> = {}): void {
    this.emit('feature_used', {
      feature,
      ...data,
    });
  },

  /**
   * Track a conversion event
   */
  trackConversion(type: string, data: Record<string, unknown> = {}): void {
    this.emit('conversion', {
      conversion_type: type,
      ...data,
    });
  },

  /**
   * Track user engagement (time on page, scroll depth, etc.)
   */
  trackEngagement(data: {
    timeOnPage?: number;
    scrollDepth?: number;
    interactions?: number;
    [key: string]: unknown;
  }): void {
    this.emit('engagement', data);
  },

  /**
   * Track errors
   */
  trackError(error: Error | string, context: Record<string, unknown> = {}): void {
    this.emit('error', {
      message: error instanceof Error ? error.message : error,
      stack: error instanceof Error ? error.stack : undefined,
      ...context,
    });
  },

  /**
   * Track tier/addon changes
   */
  trackTierChange(oldTier: string, newTier: string, data: Record<string, unknown> = {}): void {
    this.emit('tier_change', {
      old_tier: oldTier,
      new_tier: newTier,
      ...data,
    });
  },

  /**
   * Track voice analysis events
   */
  trackVoiceAnalysis(data: {
    profile_type: string;
    confidence: number;
    tokens?: string[];
    word_count?: number;
    [key: string]: unknown;
  }): void {
    this.emit('voice_analysis_complete', data);
  },

  /**
   * Track authority progression
   */
  trackAuthorityProgress(data: {
    score: number;
    rank?: number;
    milestone?: string;
    [key: string]: unknown;
  }): void {
    this.emit('authority_progress', data);
  },

  /**
   * Internal: Send event to backend
   */
  _send(event: MetaEvent, options: MetaEventOptions = {}): void {
    const endpoint = options.endpoint || this.config.endpoint;
    const payload = JSON.stringify(event);

    // Use sendBeacon for non-blocking delivery
    if (!options.sync && typeof navigator !== 'undefined' && navigator.sendBeacon) {
      const blob = new Blob([payload], { type: 'application/json' });
      const success = navigator.sendBeacon(endpoint, blob);
      
      if (!success) {
        // Queue for retry
        queueEvent(event);
      }
    } else {
      // Fallback to fetch (async)
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true, // Allow request to complete even if page unloads
      }).catch(() => {
        // Queue for retry
        queueEvent(event);
      });
    }
  },

  /**
   * Flush queued events
   */
  async flushQueue(): Promise<void> {
    const queue = getEventQueue();
    if (queue.length === 0) return;

    const endpoint = this.config.endpoint;
    const batch = queue.slice(0, this.config.batchSize);

    try {
      const response = await fetch(`${endpoint}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events: batch.map(q => q.event) }),
      });

      if (response.ok) {
        // Remove sent events from queue
        const remaining = queue.slice(this.config.batchSize);
        if (remaining.length > 0) {
          localStorage.setItem(EVENT_QUEUE_KEY, JSON.stringify(remaining));
        } else {
          clearEventQueue();
        }
      }
    } catch {
      // Will retry on next flush
    }
  },

  /**
   * Initialize event tracking
   */
  init(): void {
    if (typeof window === 'undefined') return;

    // Track initial page view
    this.trackPageView();

    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        // User is leaving, send engagement data
        this.trackEngagement({
          timeOnPage: performance.now(),
          event: 'page_hidden',
        });
      }
    });

    // Track before unload
    window.addEventListener('beforeunload', () => {
      this.flushQueue();
    });

    // Periodic queue flush
    setInterval(() => {
      this.flushQueue();
    }, this.config.flushInterval);

    // Initial queue flush
    this.flushQueue();

    if (this.config.debug) {
      console.log('[MetaEvents] Initialized');
    }
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// REACT HOOKS
// ═══════════════════════════════════════════════════════════════════════════

import { useEffect, useRef } from 'react';

/**
 * Hook to track page views on route changes
 */
export const usePageTracking = (): void => {
  const previousPath = useRef<string>('');

  useEffect(() => {
    const currentPath = window.location.pathname;
    
    if (currentPath !== previousPath.current) {
      MetaEvents.trackPageView(currentPath);
      previousPath.current = currentPath;
    }
  });
};

/**
 * Hook to track feature usage duration
 */
export const useFeatureTracking = (featureName: string): void => {
  const startTime = useRef<number>(Date.now());

  useEffect(() => {
    startTime.current = Date.now();

    return () => {
      const duration = Date.now() - startTime.current;
      MetaEvents.trackFeature(featureName, {
        duration_ms: duration,
      });
    };
  }, [featureName]);
};

/**
 * Hook to track time on page
 */
export const useEngagementTracking = (): void => {
  const startTime = useRef<number>(Date.now());
  const scrollDepth = useRef<number>(0);
  const interactions = useRef<number>(0);

  useEffect(() => {
    startTime.current = Date.now();

    const handleScroll = () => {
      const depth = Math.round(
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
      );
      scrollDepth.current = Math.max(scrollDepth.current, depth);
    };

    const handleInteraction = () => {
      interactions.current += 1;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('click', handleInteraction);
    window.addEventListener('keydown', handleInteraction);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('click', handleInteraction);
      window.removeEventListener('keydown', handleInteraction);

      MetaEvents.trackEngagement({
        timeOnPage: Date.now() - startTime.current,
        scrollDepth: scrollDepth.current,
        interactions: interactions.current,
      });
    };
  }, []);
};

// ═══════════════════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════════════════

export default MetaEvents;
