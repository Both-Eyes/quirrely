/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY READER FUNNEL COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for reader behavior tracking and taste display.
 * 
 * Components:
 * - <reader-tracker> - Invisible component for tracking behavior
 * - <reading-taste-card> - Display computed reading taste
 * - <taste-vs-voice> - Compare reading taste with writing voice
 * - <book-recommendation> - Affiliate-linked book card
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
};

const PROFILE_META = {
  'ASSERTIVE-OPEN': { title: 'Bold Ideas, Open Conversation', icon: '⚡' },
  'ASSERTIVE-CLOSED': { title: 'Decisive and Direct', icon: '⚡' },
  'ASSERTIVE-BALANCED': { title: 'Strong Views, Fair Treatment', icon: '⚡' },
  'ASSERTIVE-CONTRADICTORY': { title: 'Confident Complexity', icon: '⚡' },
  'MINIMAL-OPEN': { title: 'Space to Think', icon: '💎' },
  'MINIMAL-CLOSED': { title: 'Nothing Wasted', icon: '💎' },
  'MINIMAL-BALANCED': { title: 'Brief and Fair', icon: '💎' },
  'MINIMAL-CONTRADICTORY': { title: 'Zen Simplicity', icon: '💎' },
  'POETIC-OPEN': { title: 'Beauty Seeking Truth', icon: '🌙' },
  'POETIC-CLOSED': { title: 'Truth in Beauty', icon: '🌙' },
  'POETIC-BALANCED': { title: 'Light and Shadow', icon: '🌙' },
  'POETIC-CONTRADICTORY': { title: 'Dancing with Opposites', icon: '🌙' },
  'DENSE-OPEN': { title: 'Deep and Curious', icon: '📚' },
  'DENSE-CLOSED': { title: 'Authoritative Depth', icon: '📚' },
  'DENSE-BALANCED': { title: 'Comprehensive Fairness', icon: '📚' },
  'DENSE-CONTRADICTORY': { title: 'Systematic Paradox', icon: '📚' },
  'CONVERSATIONAL-OPEN': { title: 'Warm and Wondering', icon: '💬' },
  'CONVERSATIONAL-CLOSED': { title: 'Friendly Certainty', icon: '💬' },
  'CONVERSATIONAL-BALANCED': { title: 'Easy Fairness', icon: '💬' },
  'CONVERSATIONAL-CONTRADICTORY': { title: 'Honestly Conflicted', icon: '💬' },
  'FORMAL-OPEN': { title: 'Professional Inquiry', icon: '🏛️' },
  'FORMAL-CLOSED': { title: 'Executive Clarity', icon: '🏛️' },
  'FORMAL-BALANCED': { title: 'Institutional Fairness', icon: '🏛️' },
  'FORMAL-CONTRADICTORY': { title: 'Structured Tension', icon: '🏛️' },
  'BALANCED-OPEN': { title: 'Genuinely Uncertain', icon: '⚖️' },
  'BALANCED-CLOSED': { title: 'Fair Conclusions', icon: '⚖️' },
  'BALANCED-BALANCED': { title: 'True Moderation', icon: '⚖️' },
  'BALANCED-CONTRADICTORY': { title: 'Productive Tension', icon: '⚖️' },
  'LONGFORM-OPEN': { title: 'Patient Exploration', icon: '🗺️' },
  'LONGFORM-CLOSED': { title: 'Thorough Persuasion', icon: '🗺️' },
  'LONGFORM-BALANCED': { title: 'Comprehensive Coverage', icon: '🗺️' },
  'LONGFORM-CONTRADICTORY': { title: 'Extended Paradox', icon: '🗺️' },
  'INTERROGATIVE-OPEN': { title: 'Questions That Open', icon: '❓' },
  'INTERROGATIVE-CLOSED': { title: 'Socratic Certainty', icon: '❓' },
  'INTERROGATIVE-BALANCED': { title: 'Fair Questions', icon: '❓' },
  'INTERROGATIVE-CONTRADICTORY': { title: 'Impossible Questions', icon: '❓' },
  'HEDGED-OPEN': { title: 'Careful Curiosity', icon: '🌫️' },
  'HEDGED-CLOSED': { title: 'Qualified Conclusions', icon: '🌫️' },
  'HEDGED-BALANCED': { title: 'Nuanced Fairness', icon: '🌫️' },
  'HEDGED-CONTRADICTORY': { title: 'Uncertain Wisdom', icon: '🌫️' },
};


// ═══════════════════════════════════════════════════════════════════════════
// READER TRACKER (Invisible)
// ═══════════════════════════════════════════════════════════════════════════

class ReaderTracker extends HTMLElement {
  constructor() {
    super();
    this._startTime = Date.now();
    this._maxScroll = 0;
  }

  connectedCallback() {
    this.setupTracking();
  }

  disconnectedCallback() {
    this.cleanup();
  }

  get profileType() { return this.getAttribute('profile-type'); }
  get profileStance() { return this.getAttribute('profile-stance'); }
  get contentType() { return this.getAttribute('content-type') || 'reading_post'; }

  setupTracking() {
    this._scrollHandler = this._onScroll.bind(this);
    this._clickHandler = this._onClick.bind(this);
    this._exitHandler = this._onExit.bind(this);

    window.addEventListener('scroll', this._scrollHandler);
    document.addEventListener('click', this._clickHandler);
    window.addEventListener('beforeunload', this._exitHandler);

    // Send initial page view
    this.sendEvent('page_view');
  }

  cleanup() {
    window.removeEventListener('scroll', this._scrollHandler);
    document.removeEventListener('click', this._clickHandler);
    window.removeEventListener('beforeunload', this._exitHandler);
  }

  _onScroll() {
    const scrollPercent = Math.round(
      (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
    );
    this._maxScroll = Math.max(this._maxScroll, scrollPercent);
  }

  _onClick(e) {
    const link = e.target.closest('a[data-track]');
    if (link) {
      const trackType = link.dataset.track;
      const eventType = trackType === 'book' ? 'click_book' :
                        trackType === 'writer' ? 'click_writer' :
                        trackType === 'featured' ? 'click_featured' : 'click_writer';

      this.sendEvent(eventType, {
        content_id: link.dataset.contentId,
        affiliate_partner: link.dataset.affiliate,
      });
    }

    // Track "more like this" buttons
    const moreBtn = e.target.closest('[data-action="more-like-this"]');
    if (moreBtn) {
      this.sendEvent('more_like_this');
    }

    // Track dismiss buttons
    const dismissBtn = e.target.closest('[data-action="dismiss"]');
    if (dismissBtn) {
      this.sendEvent('dismiss');
    }
  }

  _onExit() {
    const timeOnPage = Math.round((Date.now() - this._startTime) / 1000);

    if (this._maxScroll > 75 || timeOnPage > 120) {
      this.sendEvent('read_complete', {
        time_on_page_seconds: timeOnPage,
        scroll_depth_percent: this._maxScroll,
      });
    }
  }

  sendEvent(eventType, extra = {}) {
    const payload = {
      event_type: eventType,
      profile_type: this.profileType,
      profile_stance: this.profileStance,
      content_type: this.contentType,
      ...extra,
    };

    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/v2/reader/event', JSON.stringify(payload));
    } else {
      fetch('/api/v2/reader/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true,
      });
    }
  }
}

customElements.define('reader-tracker', ReaderTracker);


// ═══════════════════════════════════════════════════════════════════════════
// READING TASTE CARD
// ═══════════════════════════════════════════════════════════════════════════

class ReadingTasteCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['profile-id', 'confidence', 'posts-viewed', 'books-clicked'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get profileId() { return this.getAttribute('profile-id'); }
  get confidence() { return parseFloat(this.getAttribute('confidence') || '0'); }
  get postsViewed() { return parseInt(this.getAttribute('posts-viewed') || '0'); }
  get booksClicked() { return parseInt(this.getAttribute('books-clicked') || '0'); }

  render() {
    const { profileId, confidence, postsViewed, booksClicked } = this;
    const meta = PROFILE_META[profileId] || { title: 'Discovering...', icon: '🔍' };
    const [type, stance] = profileId ? profileId.split('-') : ['?', '?'];

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .card {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 16px;
          padding: 1.5rem;
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        
        .icon {
          font-size: 2.5rem;
        }
        
        .title-group h3 {
          margin: 0;
          font-size: 1.25rem;
          color: ${COLORS.ink};
        }
        
        .meta {
          margin: 0.25rem 0 0 0;
          font-size: 0.9rem;
          color: ${COLORS.coral};
          font-weight: 500;
        }
        
        .confidence {
          margin-bottom: 1.5rem;
        }
        
        .confidence-label {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
          color: ${COLORS.muted};
          margin-bottom: 0.5rem;
        }
        
        .confidence-bar {
          height: 8px;
          background: ${COLORS.border};
          border-radius: 4px;
          overflow: hidden;
        }
        
        .confidence-fill {
          height: 100%;
          background: linear-gradient(90deg, ${COLORS.coral} 0%, ${COLORS.softGold} 100%);
          border-radius: 4px;
          transition: width 0.5s ease;
        }
        
        .confidence-hint {
          font-size: 0.8rem;
          color: ${COLORS.muted};
          margin: 0.5rem 0 0 0;
          font-style: italic;
        }
        
        .stats {
          display: flex;
          gap: 2rem;
          margin-bottom: 1.5rem;
        }
        
        .stat {
          text-align: center;
        }
        
        .stat-value {
          display: block;
          font-size: 1.5rem;
          font-weight: 700;
          color: ${COLORS.ink};
        }
        
        .stat-label {
          font-size: 0.75rem;
          color: ${COLORS.muted};
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .explore-link {
          display: block;
          text-align: center;
          padding: 0.75rem;
          background: ${COLORS.bgDark};
          color: ${COLORS.coral};
          text-decoration: none;
          border-radius: 8px;
          font-weight: 500;
          transition: background 0.2s;
        }
        
        .explore-link:hover {
          background: ${COLORS.border};
        }
      </style>
      
      <div class="card">
        <div class="header">
          <span class="icon">${meta.icon}</span>
          <div class="title-group">
            <h3>${meta.title}</h3>
            <p class="meta">${type} + ${stance}</p>
          </div>
        </div>
        
        <div class="confidence">
          <div class="confidence-label">
            <span>Reading Taste Confidence</span>
            <span>${Math.round(confidence * 100)}%</span>
          </div>
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${confidence * 100}%"></div>
          </div>
          <p class="confidence-hint">
            ${confidence < 0.3 ? 'Keep exploring to refine your taste profile' :
              confidence < 0.7 ? 'Your reading taste is emerging' :
              'Your reading taste is well-defined'}
          </p>
        </div>
        
        <div class="stats">
          <div class="stat">
            <span class="stat-value">${postsViewed}</span>
            <span class="stat-label">Posts Read</span>
          </div>
          <div class="stat">
            <span class="stat-value">${booksClicked}</span>
            <span class="stat-label">Books Explored</span>
          </div>
        </div>
        
        <a href="/blog/reading/${profileId?.toLowerCase()}" class="explore-link">
          Explore this voice →
        </a>
      </div>
    `;
  }
}

customElements.define('reading-taste-card', ReadingTasteCard);


// ═══════════════════════════════════════════════════════════════════════════
// TASTE VS VOICE COMPARISON
// ═══════════════════════════════════════════════════════════════════════════

class TasteVsVoice extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['reading-taste', 'writing-voice'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get readingTaste() { return this.getAttribute('reading-taste'); }
  get writingVoice() { return this.getAttribute('writing-voice'); }

  render() {
    const { readingTaste, writingVoice } = this;
    const tasteMeta = PROFILE_META[readingTaste] || {};
    const voiceMeta = PROFILE_META[writingVoice] || {};
    const matches = readingTaste === writingVoice;

    const hasReading = !!readingTaste;
    const hasWriting = !!writingVoice;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .comparison {
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 16px;
          padding: 1.5rem;
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .title {
          font-size: 1rem;
          font-weight: 600;
          color: ${COLORS.ink};
          margin: 0 0 1.5rem 0;
          text-align: center;
        }
        
        .profiles {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          gap: 1rem;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .profile {
          text-align: center;
          padding: 1rem;
          background: ${COLORS.bgDark};
          border-radius: 12px;
        }
        
        .profile.empty {
          border: 2px dashed ${COLORS.border};
          background: transparent;
        }
        
        .profile-label {
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: ${COLORS.muted};
          margin-bottom: 0.5rem;
        }
        
        .profile-icon {
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }
        
        .profile-title {
          font-size: 0.9rem;
          font-weight: 600;
          color: ${COLORS.ink};
        }
        
        .profile-id {
          font-size: 0.8rem;
          color: ${COLORS.coral};
        }
        
        .connector {
          font-size: 1.5rem;
          color: ${matches ? COLORS.softGold : COLORS.muted};
        }
        
        .insight {
          text-align: center;
          padding: 1rem;
          background: ${matches ? 'rgba(212, 165, 116, 0.1)' : COLORS.bgDark};
          border-radius: 8px;
          font-size: 0.9rem;
          color: ${COLORS.ink};
        }
        
        .cta {
          display: block;
          text-align: center;
          margin-top: 1rem;
          padding: 0.75rem;
          background: ${COLORS.coral};
          color: white;
          text-decoration: none;
          border-radius: 8px;
          font-weight: 500;
        }
        
        .cta:hover {
          background: ${COLORS.coralDark};
        }
      </style>
      
      <div class="comparison">
        <h3 class="title">Your Reading Taste vs Writing Voice</h3>
        
        <div class="profiles">
          <div class="profile ${hasReading ? '' : 'empty'}">
            <div class="profile-label">Reading Taste</div>
            ${hasReading ? `
              <div class="profile-icon">${tasteMeta.icon || '📖'}</div>
              <div class="profile-title">${tasteMeta.title || 'Unknown'}</div>
              <div class="profile-id">${readingTaste}</div>
            ` : `
              <div class="profile-icon">❓</div>
              <div class="profile-title">Keep exploring</div>
            `}
          </div>
          
          <div class="connector">${matches ? '=' : '≠'}</div>
          
          <div class="profile ${hasWriting ? '' : 'empty'}">
            <div class="profile-label">Writing Voice</div>
            ${hasWriting ? `
              <div class="profile-icon">${voiceMeta.icon || '✍️'}</div>
              <div class="profile-title">${voiceMeta.title || 'Unknown'}</div>
              <div class="profile-id">${writingVoice}</div>
            ` : `
              <div class="profile-icon">❓</div>
              <div class="profile-title">Analyze your writing</div>
            `}
          </div>
        </div>
        
        <div class="insight">
          ${hasReading && hasWriting ? (
            matches ? 
              "You read what you write! Your taste and voice are aligned." :
              `Interesting! You're drawn to ${tasteMeta.title} writing, but you write as ${voiceMeta.title}.`
          ) : hasReading ? 
            "You know what you like to read. Now discover how you write!" :
            hasWriting ?
            "You know your writing voice. Explore your reading taste next!" :
            "Explore reading styles and analyze your writing to compare."
          }
        </div>
        
        ${!hasWriting ? `
          <a href="/analyze" class="cta">Analyze My Writing →</a>
        ` : !hasReading ? `
          <a href="/blog/reading" class="cta">Explore Reading Styles →</a>
        ` : ''}
      </div>
    `;
  }
}

customElements.define('taste-vs-voice', TasteVsVoice);


// ═══════════════════════════════════════════════════════════════════════════
// BOOK RECOMMENDATION CARD
// ═══════════════════════════════════════════════════════════════════════════

class BookRecommendation extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['title', 'author', 'profile-id', 'country', 'affiliate-url'];
  }

  connectedCallback() {
    this.render();
  }

  attributeChangedCallback() {
    this.render();
  }

  get bookTitle() { return this.getAttribute('title'); }
  get author() { return this.getAttribute('author'); }
  get profileId() { return this.getAttribute('profile-id'); }
  get country() { return this.getAttribute('country') || 'CA'; }
  get affiliateUrl() { return this.getAttribute('affiliate-url'); }

  render() {
    const { bookTitle, author, profileId, country, affiliateUrl } = this;
    const flags = { CA: '🇨🇦', UK: '🇬🇧', AU: '🇦🇺', NZ: '🇳🇿', US: '🇺🇸' };

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .book {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 10px;
          transition: box-shadow 0.2s;
        }
        
        .book:hover {
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .flag {
          font-size: 1.5rem;
        }
        
        .info {
          flex: 1;
        }
        
        .book-title {
          font-weight: 600;
          color: ${COLORS.ink};
          margin: 0 0 0.25rem 0;
          font-size: 0.95rem;
        }
        
        .author {
          color: ${COLORS.muted};
          font-size: 0.85rem;
          margin: 0;
        }
        
        .buy-link {
          padding: 0.5rem 1rem;
          background: ${COLORS.coral};
          color: white;
          text-decoration: none;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
          white-space: nowrap;
        }
        
        .buy-link:hover {
          background: ${COLORS.coralDark};
        }
      </style>
      
      <div class="book">
        <span class="flag">${flags[country] || '🌍'}</span>
        <div class="info">
          <p class="book-title">${bookTitle}</p>
          <p class="author">${author}</p>
        </div>
        <a href="${affiliateUrl}" 
           target="_blank" 
           rel="noopener" 
           class="buy-link"
           data-track="book"
           data-content-id="${bookTitle}"
           data-affiliate="${country}">
          Find Book →
        </a>
      </div>
    `;
  }
}

customElements.define('book-recommendation', BookRecommendation);


// ═══════════════════════════════════════════════════════════════════════════
// READING RECOMMENDATIONS
// ═══════════════════════════════════════════════════════════════════════════

class ReadingRecommendations extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._recommendations = [];
  }

  connectedCallback() {
    this.fetchRecommendations();
  }

  async fetchRecommendations() {
    try {
      const response = await fetch('/api/v2/reader/recommendations?limit=4');
      const data = await response.json();
      this._recommendations = data;
      this.render();
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      this.render();
    }
  }

  render() {
    const recs = this._recommendations;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        
        .container {
          font-family: system-ui, -apple-system, sans-serif;
        }
        
        .title {
          font-size: 1rem;
          font-weight: 600;
          color: ${COLORS.ink};
          margin: 0 0 1rem 0;
        }
        
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1rem;
        }
        
        .rec {
          padding: 1rem;
          background: white;
          border: 1px solid ${COLORS.border};
          border-radius: 10px;
          text-decoration: none;
          transition: all 0.2s;
        }
        
        .rec:hover {
          border-color: ${COLORS.coral};
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        
        .rec-icon {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }
        
        .rec-title {
          font-weight: 600;
          color: ${COLORS.ink};
          font-size: 0.9rem;
          margin-bottom: 0.25rem;
        }
        
        .rec-tagline {
          font-size: 0.8rem;
          color: ${COLORS.muted};
          margin-bottom: 0.5rem;
        }
        
        .rec-reason {
          font-size: 0.75rem;
          color: ${COLORS.coral};
        }
        
        .empty {
          text-align: center;
          padding: 2rem;
          color: ${COLORS.muted};
        }
      </style>
      
      <div class="container">
        <h3 class="title">Recommended For You</h3>
        ${recs.length > 0 ? `
          <div class="grid">
            ${recs.map(r => `
              <a href="${r.url}" class="rec" data-action="more-like-this">
                <div class="rec-icon">${PROFILE_META[r.profile_id]?.icon || '📖'}</div>
                <div class="rec-title">${r.title}</div>
                <div class="rec-tagline">${r.tagline}</div>
                <div class="rec-reason">${r.reason}</div>
              </a>
            `).join('')}
          </div>
        ` : `
          <div class="empty">
            <p>Start exploring to get personalized recommendations!</p>
          </div>
        `}
      </div>
    `;
  }
}

customElements.define('reading-recommendations', ReadingRecommendations);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ReaderTracker,
    ReadingTasteCard,
    TasteVsVoice,
    BookRecommendation,
    ReadingRecommendations,
    PROFILE_META,
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyReader = {
    ReaderTracker,
    ReadingTasteCard,
    TasteVsVoice,
    BookRecommendation,
    ReadingRecommendations,
    PROFILE_META,
  };
}
