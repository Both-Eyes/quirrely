/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY PROFILE RESULT CARD COMPONENT v2.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Reusable component for displaying analysis results.
 * Can be used in:
 * - Main app results page
 * - Dashboard
 * - History list
 * - Blog embeds
 * - Shareable cards
 * 
 * Aligned with LNCP v3.8 and profile-system.js
 */

class ProfileResultCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  static get observedAttributes() {
    return ['profile-id', 'compact', 'shareable'];
  }
  
  connectedCallback() {
    this.render();
  }
  
  attributeChangedCallback() {
    this.render();
  }
  
  get profileId() {
    return this.getAttribute('profile-id') || 'ASSERTIVE-OPEN';
  }
  
  get isCompact() {
    return this.hasAttribute('compact');
  }
  
  get isShareable() {
    return this.hasAttribute('shareable');
  }
  
  getProfileData() {
    // Get from window.QuirrelyProfiles if available, otherwise use fallback
    if (window.QuirrelyProfiles) {
      return window.QuirrelyProfiles.getProfile(this.profileId);
    }
    
    // Fallback data
    const [type, stance] = this.profileId.split('-');
    return {
      id: this.profileId,
      type,
      stance,
      title: `${type} + ${stance}`,
      icon: '📝',
      tagline: 'A unique writing voice.',
      color: '#FF6B6B'
    };
  }
  
  render() {
    const profile = this.getProfileData();
    const data = JSON.parse(this.getAttribute('data') || '{}');
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }
        
        .card {
          background: linear-gradient(135deg, ${profile.color || '#FF6B6B'} 0%, ${this.darkenColor(profile.color || '#FF6B6B')} 100%);
          color: white;
          border-radius: 16px;
          padding: ${this.isCompact ? '1rem' : '1.5rem 2rem'};
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .header {
          display: flex;
          align-items: ${this.isCompact ? 'center' : 'flex-start'};
          gap: ${this.isCompact ? '0.75rem' : '1rem'};
          margin-bottom: ${this.isCompact ? '0' : '1rem'};
        }
        
        .icon {
          font-size: ${this.isCompact ? '1.5rem' : '2.5rem'};
          line-height: 1;
          ${!this.isCompact ? 'background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 12px;' : ''}
        }
        
        .info {
          flex: 1;
        }
        
        .title {
          font-size: ${this.isCompact ? '1rem' : '1.25rem'};
          font-weight: 700;
          margin-bottom: ${this.isCompact ? '0' : '0.25rem'};
        }
        
        .tagline {
          font-size: ${this.isCompact ? '0.8rem' : '0.95rem'};
          opacity: 0.9;
          display: ${this.isCompact ? 'none' : 'block'};
        }
        
        .badges {
          display: ${this.isCompact ? 'none' : 'flex'};
          gap: 0.5rem;
          margin: 1rem 0;
          flex-wrap: wrap;
        }
        
        .badge {
          padding: 0.25rem 0.75rem;
          background: rgba(255,255,255,0.2);
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .traits {
          display: ${this.isCompact ? 'none' : 'flex'};
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        
        .trait {
          padding: 0.2rem 0.6rem;
          background: rgba(255,255,255,0.15);
          border-radius: 6px;
          font-size: 0.75rem;
        }
        
        .metrics {
          display: ${this.isCompact ? 'none' : 'flex'};
          justify-content: space-around;
          padding: 1rem 0;
          border-top: 1px solid rgba(255,255,255,0.2);
          margin-top: 1rem;
        }
        
        .metric {
          text-align: center;
        }
        
        .metric-value {
          font-size: 1.25rem;
          font-weight: 700;
        }
        
        .metric-label {
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          opacity: 0.8;
        }
        
        .actions {
          display: ${this.isCompact ? 'none' : 'flex'};
          gap: 0.75rem;
          margin-top: 1rem;
        }
        
        .btn {
          flex: 1;
          padding: 0.6rem 1rem;
          background: white;
          color: ${profile.color || '#FF6B6B'};
          border: none;
          border-radius: 8px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .share-row {
          display: ${this.isShareable && !this.isCompact ? 'flex' : 'none'};
          justify-content: center;
          gap: 1rem;
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .share-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: rgba(255,255,255,0.2);
          border: none;
          color: white;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .share-btn:hover {
          background: rgba(255,255,255,0.3);
          transform: scale(1.1);
        }
        
        .branding {
          text-align: center;
          margin-top: 1rem;
          font-size: 0.7rem;
          opacity: 0.7;
        }
        
        .branding a {
          color: white;
          text-decoration: none;
        }
      </style>
      
      <div class="card">
        <div class="header">
          <span class="icon">${profile.icon}</span>
          <div class="info">
            <h2 class="title">${profile.title}</h2>
            <p class="tagline">${profile.tagline}</p>
          </div>
        </div>
        
        <div class="badges">
          <span class="badge">${profile.type}</span>
          <span class="badge">${profile.stance}</span>
          ${data.confidence ? `<span class="badge">${Math.round(data.confidence * 100)}% confident</span>` : ''}
        </div>
        
        ${data.traits ? `
          <div class="traits">
            ${data.traits.slice(0, 4).map(t => `<span class="trait">${t}</span>`).join('')}
          </div>
        ` : ''}
        
        ${data.metrics ? `
          <div class="metrics">
            <div class="metric">
              <div class="metric-value">${data.metrics.wordCount || 0}</div>
              <div class="metric-label">Words</div>
            </div>
            <div class="metric">
              <div class="metric-value">${data.metrics.sentenceCount || 0}</div>
              <div class="metric-label">Sentences</div>
            </div>
            <div class="metric">
              <div class="metric-value">${data.metrics.questionRate || 0}%</div>
              <div class="metric-label">Questions</div>
            </div>
          </div>
        ` : ''}
        
        <div class="actions">
          <button class="btn" onclick="this.getRootNode().host.dispatchEvent(new CustomEvent('analyze-again'))">
            Analyze Again
          </button>
          <button class="btn" onclick="this.getRootNode().host.dispatchEvent(new CustomEvent('view-details'))">
            View Details
          </button>
        </div>
        
        <div class="share-row">
          <button class="share-btn" title="Share on Twitter" onclick="this.getRootNode().host.shareTwitter()">𝕏</button>
          <button class="share-btn" title="Share on LinkedIn" onclick="this.getRootNode().host.shareLinkedIn()">in</button>
          <button class="share-btn" title="Copy Link" onclick="this.getRootNode().host.copyLink()">🔗</button>
          <button class="share-btn" title="Download Image" onclick="this.getRootNode().host.downloadImage()">📥</button>
        </div>
        
        ${this.isShareable ? `
          <div class="branding">
            Discover your writing voice at <a href="https://quirrely.com">quirrely.com</a>
          </div>
        ` : ''}
      </div>
    `;
  }
  
  darkenColor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const factor = 0.8;
    return `rgb(${Math.floor(r * factor)}, ${Math.floor(g * factor)}, ${Math.floor(b * factor)})`;
  }
  
  shareTwitter() {
    const profile = this.getProfileData();
    const text = encodeURIComponent(`I'm "${profile.title}" - ${profile.tagline}\n\nDiscover your writing voice at quirrely.com`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
  }
  
  shareLinkedIn() {
    const url = encodeURIComponent('https://quirrely.com');
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank');
  }
  
  copyLink() {
    navigator.clipboard.writeText('https://quirrely.com');
    // Show toast notification
    this.dispatchEvent(new CustomEvent('link-copied'));
  }
  
  downloadImage() {
    this.dispatchEvent(new CustomEvent('download-image'));
  }
}

// Register the component
customElements.define('profile-result-card', ProfileResultCard);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProfileResultCard;
}
