/**
 * ═══════════════════════════════════════════════════════════════════════════
 * QUIRRELY PRICING COMPONENTS v1.0
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * Components for pricing display, checkout, and subscription management.
 * 
 * CURRENCIES: CAD, GBP, EUR, AUD (NEVER USD)
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

const CURRENCIES = {
  cad: { symbol: '$', name: 'Canadian Dollar', flag: '🇨🇦' },
  gbp: { symbol: '£', name: 'British Pound', flag: '🇬🇧' },
  eur: { symbol: '€', name: 'Euro', flag: '🇪🇺' },
  aud: { symbol: '$', name: 'Australian Dollar', flag: '🇦🇺' },
  nzd: { symbol: '$', name: 'New Zealand Dollar', flag: '🇳🇿' },
};

// Default currency
const DEFAULT_CURRENCY = 'cad';


// ═══════════════════════════════════════════════════════════════════════════
// CURRENCY SELECTOR
// ═══════════════════════════════════════════════════════════════════════════

class CurrencySelector extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._currency = DEFAULT_CURRENCY;
  }

  static get observedAttributes() { return ['currency']; }
  connectedCallback() { this.render(); }
  attributeChangedCallback(name, _, newVal) {
    if (name === 'currency') this._currency = newVal;
    this.render();
  }

  get currency() { return this._currency; }
  set currency(val) { this._currency = val; this.render(); }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: inline-block; font-family: system-ui, sans-serif; }
        .selector {
          display: flex;
          gap: 0.5rem;
          padding: 0.25rem;
          background: ${COLORS.bgDark};
          border-radius: 8px;
        }
        .option {
          padding: 0.5rem 0.75rem;
          border: none;
          background: transparent;
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.9rem;
          color: ${COLORS.muted};
          transition: all 0.2s;
        }
        .option:hover { background: ${COLORS.border}; }
        .option.active {
          background: white;
          color: ${COLORS.ink};
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .flag { margin-right: 0.25rem; }
      </style>
      <div class="selector">
        ${Object.entries(CURRENCIES).map(([code, info]) => `
          <button class="option ${this._currency === code ? 'active' : ''}" data-currency="${code}">
            <span class="flag">${info.flag}</span>${code.toUpperCase()}
          </button>
        `).join('')}
      </div>
    `;

    this.shadowRoot.querySelectorAll('.option').forEach(btn => {
      btn.addEventListener('click', () => {
        this._currency = btn.dataset.currency;
        this.render();
        this.dispatchEvent(new CustomEvent('currency-change', { 
          detail: { currency: this._currency } 
        }));
      });
    });
  }
}

customElements.define('currency-selector', CurrencySelector);


// ═══════════════════════════════════════════════════════════════════════════
// PRICING CARD
// ═══════════════════════════════════════════════════════════════════════════

class PricingCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['tier', 'monthly', 'annual', 'annual-savings', 'features-json', 'popular', 'current'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get tier() { return this.getAttribute('tier') || 'pro'; }
  get monthly() { return this.getAttribute('monthly') || ''; }
  get annual() { return this.getAttribute('annual') || ''; }
  get annualSavings() { return this.getAttribute('annual-savings') || '0'; }
  get features() {
    try { return JSON.parse(this.getAttribute('features-json') || '[]'); }
    catch { return []; }
  }
  get isPopular() { return this.hasAttribute('popular'); }
  get isCurrent() { return this.hasAttribute('current'); }

  render() {
    const tierNames = {
      pro: 'PRO',
      curator: 'Curator',
      bundle: 'PRO + Curator',
    };
    const tierDescriptions = {
      pro: 'Full writing analysis & voice evolution',
      curator: 'Full reading taste & curation',
      bundle: 'Complete Quirrely experience',
    };
    const tierIcons = {
      pro: '✍️',
      curator: '📚',
      bundle: '🎯',
    };

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .card {
          background: white;
          border: ${this.isPopular ? `2px solid ${COLORS.coral}` : `1px solid ${COLORS.border}`};
          border-radius: 16px;
          padding: 1.5rem;
          position: relative;
          ${this.isPopular ? 'transform: scale(1.02);' : ''}
        }
        .popular-badge {
          position: absolute;
          top: -12px;
          left: 50%;
          transform: translateX(-50%);
          background: ${COLORS.coral};
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }
        .header { text-align: center; margin-bottom: 1.5rem; }
        .icon { font-size: 2rem; margin-bottom: 0.5rem; }
        h3 { font-size: 1.25rem; color: ${COLORS.ink}; margin: 0 0 0.25rem 0; }
        .description { font-size: 0.85rem; color: ${COLORS.muted}; margin: 0; }
        .pricing { text-align: center; margin-bottom: 1.5rem; }
        .price-row { display: flex; justify-content: center; gap: 1rem; margin-bottom: 0.5rem; }
        .price-option { text-align: center; }
        .price-amount { font-size: 1.5rem; font-weight: 700; color: ${COLORS.ink}; }
        .price-interval { font-size: 0.8rem; color: ${COLORS.muted}; }
        .savings { display: inline-block; padding: 0.2rem 0.5rem; background: rgba(0, 184, 148, 0.1); color: ${COLORS.success}; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .features { margin-bottom: 1.5rem; }
        .feature { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9rem; color: ${COLORS.ink}; }
        .feature-check { color: ${COLORS.success}; }
        .cta {
          display: block;
          width: 100%;
          padding: 0.875rem;
          background: ${this.isCurrent ? COLORS.muted : COLORS.coral};
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1rem;
          font-weight: 600;
          cursor: ${this.isCurrent ? 'default' : 'pointer'};
          text-align: center;
          text-decoration: none;
        }
        .cta:hover:not(.current) { background: ${COLORS.coralDark}; }
        .cta.current { cursor: default; }
        .interval-toggle {
          display: flex;
          justify-content: center;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        .interval-btn {
          padding: 0.4rem 0.75rem;
          border: 1px solid ${COLORS.border};
          background: white;
          border-radius: 6px;
          font-size: 0.85rem;
          cursor: pointer;
          color: ${COLORS.muted};
        }
        .interval-btn.active {
          background: ${COLORS.coral};
          color: white;
          border-color: ${COLORS.coral};
        }
      </style>
      
      <div class="card">
        ${this.isPopular ? '<div class="popular-badge">Most Popular</div>' : ''}
        
        <div class="header">
          <div class="icon">${tierIcons[this.tier] || '✨'}</div>
          <h3>${tierNames[this.tier] || this.tier}</h3>
          <p class="description">${tierDescriptions[this.tier] || ''}</p>
        </div>
        
        <div class="interval-toggle">
          <button class="interval-btn active" data-interval="monthly">Monthly</button>
          <button class="interval-btn" data-interval="annual">Annual</button>
        </div>
        
        <div class="pricing">
          <div class="price-row">
            <div class="price-option monthly-price">
              <div class="price-amount">${this.monthly}</div>
              <div class="price-interval">/month</div>
            </div>
            <div class="price-option annual-price" style="display: none;">
              <div class="price-amount">${this.annual}</div>
              <div class="price-interval">/year</div>
            </div>
          </div>
          <div class="savings annual-savings" style="display: none;">Save ${this.annualSavings}%</div>
        </div>
        
        <div class="features">
          ${this.features.map(f => `
            <div class="feature">
              <span class="feature-check">✓</span>
              <span>${f}</span>
            </div>
          `).join('')}
        </div>
        
        <button class="cta ${this.isCurrent ? 'current' : ''}" id="cta-btn">
          ${this.isCurrent ? 'Current Plan' : 'Get Started'}
        </button>
      </div>
    `;

    // Interval toggle
    this.shadowRoot.querySelectorAll('.interval-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.shadowRoot.querySelectorAll('.interval-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const isAnnual = btn.dataset.interval === 'annual';
        this.shadowRoot.querySelector('.monthly-price').style.display = isAnnual ? 'none' : 'block';
        this.shadowRoot.querySelector('.annual-price').style.display = isAnnual ? 'block' : 'none';
        this.shadowRoot.querySelector('.annual-savings').style.display = isAnnual ? 'inline-block' : 'none';
      });
    });

    // CTA click
    if (!this.isCurrent) {
      this.shadowRoot.getElementById('cta-btn')?.addEventListener('click', () => {
        const isAnnual = this.shadowRoot.querySelector('.interval-btn.active')?.dataset.interval === 'annual';
        this.dispatchEvent(new CustomEvent('checkout', { 
          detail: { tier: this.tier, annual: isAnnual } 
        }));
      });
    }
  }
}

customElements.define('pricing-card', PricingCard);


// ═══════════════════════════════════════════════════════════════════════════
// PRICING PAGE
// ═══════════════════════════════════════════════════════════════════════════

class PricingPage extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._currency = DEFAULT_CURRENCY;
    this._pricing = null;
    this._currentTier = null;
  }

  connectedCallback() {
    this.loadPricing();
  }

  async loadPricing() {
    try {
      const response = await fetch('/api/v2/payments/pricing/all');
      this._pricing = await response.json();
      this.render();
    } catch (err) {
      console.error('Failed to load pricing:', err);
      this.render();
    }
  }

  setCurrency(currency) {
    this._currency = currency;
    this.render();
  }

  setCurrentTier(tier) {
    this._currentTier = tier;
    this.render();
  }

  async handleCheckout(tier, annual) {
    try {
      const response = await fetch('/api/v2/payments/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('quirrely_auth_token') || ''}`,
        },
        body: JSON.stringify({
          tier,
          annual,
          currency: this._currency,
        }),
      });
      
      const data = await response.json();
      
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('Failed to create checkout session');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Failed to start checkout');
    }
  }

  render() {
    const prices = this._pricing?.[this._currency];
    
    if (!prices) {
      this.shadowRoot.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: ${COLORS.muted};">
          Loading pricing...
        </div>
      `;
      return;
    }

    const proFeatures = [
      '10,000 words per day',
      'Unlimited analyses',
      'Voice evolution tracking',
      'Full history',
      'Featured Writer eligibility',
      'Authority Writer path',
    ];

    const curatorFeatures = [
      'Full reading taste profile',
      'Unlimited bookmarks',
      'Taste vs Voice comparison',
      'Export reading lists',
      'Featured Curator eligibility',
      'Authority Curator path',
    ];

    const bundleFeatures = [
      'Everything in PRO',
      'Everything in Curator',
      'Voice & Taste badge',
      'Priority support',
    ];

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; margin-bottom: 2rem; }
        h1 { font-size: 2rem; color: ${COLORS.ink}; margin: 0 0 0.5rem 0; }
        .subtitle { color: ${COLORS.muted}; font-size: 1.1rem; margin: 0 0 1.5rem 0; }
        .currency-row { display: flex; justify-content: center; margin-bottom: 2rem; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .refund-note { text-align: center; font-size: 0.85rem; color: ${COLORS.muted}; }
        .refund-note a { color: ${COLORS.coral}; }
      </style>
      
      <div class="container">
        <div class="header">
          <h1>Choose Your Path</h1>
          <p class="subtitle">Your voice. Your taste. Both matter.</p>
        </div>
        
        <div class="currency-row">
          <currency-selector currency="${this._currency}"></currency-selector>
        </div>
        
        <div class="cards">
          <pricing-card
            tier="pro"
            monthly="${prices.pro.monthly}"
            annual="${prices.pro.annual}"
            annual-savings="${prices.pro.annual_savings_percent}"
            features-json='${JSON.stringify(proFeatures)}'
            ${this._currentTier === 'pro' ? 'current' : ''}
          ></pricing-card>
          
          <pricing-card
            tier="bundle"
            monthly="${prices.bundle.monthly}"
            annual="${prices.bundle.annual}"
            annual-savings="${prices.bundle.annual_savings_percent}"
            features-json='${JSON.stringify(bundleFeatures)}'
            popular
            ${this._currentTier === 'bundle' ? 'current' : ''}
          ></pricing-card>
          
          <pricing-card
            tier="curator"
            monthly="${prices.curator.monthly}"
            annual="${prices.curator.annual}"
            annual-savings="${prices.curator.annual_savings_percent}"
            features-json='${JSON.stringify(curatorFeatures)}'
            ${this._currentTier === 'curator' ? 'current' : ''}
          ></pricing-card>
        </div>
        
        <p class="refund-note">
          All subscriptions are non-refundable. 
          <a href="/refund-policy">Read our refund policy</a>
        </p>
      </div>
    `;

    // Listen for currency changes
    this.shadowRoot.querySelector('currency-selector')?.addEventListener('currency-change', (e) => {
      this.setCurrency(e.detail.currency);
    });

    // Listen for checkout events
    this.shadowRoot.querySelectorAll('pricing-card').forEach(card => {
      card.addEventListener('checkout', (e) => {
        this.handleCheckout(e.detail.tier, e.detail.annual);
      });
    });
  }
}

customElements.define('pricing-page', PricingPage);


// ═══════════════════════════════════════════════════════════════════════════
// TRIAL BANNER
// ═══════════════════════════════════════════════════════════════════════════

class TrialBanner extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['days-remaining', 'words-until-unlock', 'trial-active'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  get daysRemaining() { return parseInt(this.getAttribute('days-remaining') || '0'); }
  get wordsUntilUnlock() { return parseInt(this.getAttribute('words-until-unlock') || '500'); }
  get trialActive() { return this.hasAttribute('trial-active'); }

  render() {
    if (this.trialActive) {
      this.renderTrialActive();
    } else if (this.wordsUntilUnlock > 0) {
      this.renderWordsToUnlock();
    } else {
      this.renderTrialAvailable();
    }
  }

  renderTrialActive() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .banner {
          background: linear-gradient(135deg, ${COLORS.coral} 0%, ${COLORS.softGold} 100%);
          color: white;
          padding: 0.75rem 1rem;
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-family: system-ui, sans-serif;
        }
        .text { font-size: 0.9rem; }
        .days { font-weight: 600; }
        .cta {
          padding: 0.4rem 0.75rem;
          background: white;
          color: ${COLORS.coral};
          border: none;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
        }
      </style>
      <div class="banner">
        <span class="text">🎉 PRO Trial Active — <span class="days">${this.daysRemaining} days</span> remaining</span>
        <button class="cta" id="upgrade-btn">Upgrade Now</button>
      </div>
    `;

    this.shadowRoot.getElementById('upgrade-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('upgrade-click'));
    });
  }

  renderWordsToUnlock() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .banner {
          background: ${COLORS.bgDark};
          padding: 0.75rem 1rem;
          border-radius: 8px;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          font-family: system-ui, sans-serif;
        }
        .icon { font-size: 1.25rem; }
        .text { flex: 1; font-size: 0.9rem; color: ${COLORS.ink}; }
        .words { color: ${COLORS.coral}; font-weight: 600; }
      </style>
      <div class="banner">
        <span class="icon">🎁</span>
        <span class="text">Write <span class="words">${this.wordsUntilUnlock}</span> more words to unlock a free 7-day PRO trial!</span>
      </div>
    `;
  }

  renderTrialAvailable() {
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        .banner {
          background: ${COLORS.bgDark};
          padding: 0.75rem 1rem;
          border-radius: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-family: system-ui, sans-serif;
        }
        .text { font-size: 0.9rem; color: ${COLORS.ink}; }
        .cta {
          padding: 0.4rem 0.75rem;
          background: ${COLORS.coral};
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 600;
          cursor: pointer;
        }
      </style>
      <div class="banner">
        <span class="text">🎉 You've unlocked a free 7-day PRO trial!</span>
        <button class="cta" id="start-btn">Start Trial</button>
      </div>
    `;

    this.shadowRoot.getElementById('start-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('start-trial'));
    });
  }
}

customElements.define('trial-banner', TrialBanner);


// ═══════════════════════════════════════════════════════════════════════════
// SUBSCRIPTION STATUS
// ═══════════════════════════════════════════════════════════════════════════

class SubscriptionStatus extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes() {
    return ['tier', 'status', 'renews-at', 'cancels-at', 'amount', 'currency', 'interval'];
  }

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  render() {
    const tier = this.getAttribute('tier') || 'free';
    const status = this.getAttribute('status') || 'active';
    const renewsAt = this.getAttribute('renews-at');
    const cancelsAt = this.getAttribute('cancels-at');
    const amount = this.getAttribute('amount') || '';
    const currency = this.getAttribute('currency') || 'cad';
    const interval = this.getAttribute('interval') || 'month';

    const tierNames = { pro: 'PRO', curator: 'Curator', bundle: 'PRO + Curator', free: 'Free' };
    const currencyInfo = CURRENCIES[currency] || CURRENCIES.cad;

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; font-family: system-ui, sans-serif; }
        .card { background: white; border: 1px solid ${COLORS.border}; border-radius: 12px; padding: 1.25rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
        h3 { font-size: 1rem; color: ${COLORS.ink}; margin: 0; }
        .badge {
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }
        .badge.active { background: rgba(0, 184, 148, 0.1); color: ${COLORS.success}; }
        .badge.cancelled { background: rgba(255, 107, 107, 0.1); color: ${COLORS.coral}; }
        .details { font-size: 0.9rem; color: ${COLORS.muted}; }
        .detail-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .actions { margin-top: 1rem; display: flex; gap: 0.75rem; }
        .btn {
          padding: 0.5rem 1rem;
          border-radius: 6px;
          font-size: 0.85rem;
          cursor: pointer;
          border: none;
        }
        .btn-primary { background: ${COLORS.coral}; color: white; }
        .btn-secondary { background: ${COLORS.bgDark}; color: ${COLORS.ink}; }
      </style>
      
      <div class="card">
        <div class="header">
          <h3>${tierNames[tier] || tier}</h3>
          <span class="badge ${cancelsAt ? 'cancelled' : 'active'}">
            ${cancelsAt ? 'Cancels' : status}
          </span>
        </div>
        
        <div class="details">
          ${amount ? `
            <div class="detail-row">
              <span>Price</span>
              <span>${currencyInfo.symbol}${amount} / ${interval}</span>
            </div>
          ` : ''}
          ${renewsAt && !cancelsAt ? `
            <div class="detail-row">
              <span>Renews</span>
              <span>${new Date(renewsAt).toLocaleDateString()}</span>
            </div>
          ` : ''}
          ${cancelsAt ? `
            <div class="detail-row">
              <span>Access until</span>
              <span>${new Date(cancelsAt).toLocaleDateString()}</span>
            </div>
          ` : ''}
        </div>
        
        <div class="actions">
          ${cancelsAt ? `
            <button class="btn btn-primary" id="reactivate-btn">Reactivate</button>
          ` : tier !== 'free' ? `
            <button class="btn btn-secondary" id="manage-btn">Manage</button>
            <button class="btn btn-secondary" id="cancel-btn">Cancel</button>
          ` : `
            <button class="btn btn-primary" id="upgrade-btn">Upgrade</button>
          `}
        </div>
      </div>
    `;

    this.shadowRoot.getElementById('manage-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('manage-click'));
    });

    this.shadowRoot.getElementById('cancel-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('cancel-click'));
    });

    this.shadowRoot.getElementById('reactivate-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('reactivate-click'));
    });

    this.shadowRoot.getElementById('upgrade-btn')?.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('upgrade-click'));
    });
  }
}

customElements.define('subscription-status', SubscriptionStatus);


// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    CurrencySelector, PricingCard, PricingPage,
    TrialBanner, SubscriptionStatus, CURRENCIES,
  };
}

if (typeof window !== 'undefined') {
  window.QuirrelyPricing = {
    CurrencySelector, PricingCard, PricingPage,
    TrialBanner, SubscriptionStatus, CURRENCIES,
  };
}
