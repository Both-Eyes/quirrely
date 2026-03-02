/**
 * AFFILIATE CONFIGURATION
 * =======================
 * Country-specific book retailer affiliate settings
 * 
 * Version: 1.0.0
 * Date: February 10, 2026
 */

const AFFILIATE_CONFIG = {
  
  // ═══════════════════════════════════════════════════════════════
  // RETAILER CONFIGURATIONS
  // ═══════════════════════════════════════════════════════════════
  
  retailers: {
    CA: {
      name: 'Indigo',
      slug: 'indigo',
      logo: '/assets/affiliates/indigo.svg',
      baseUrl: 'https://www.indigo.ca',
      searchTemplate: 'https://www.indigo.ca/en-ca/search/?keywords={query}&ref={affiliate_id}',
      productTemplate: 'https://www.indigo.ca/en-ca/product/{isbn}/?ref={affiliate_id}',
      affiliateId: process.env.INDIGO_AFFILIATE_ID || 'quirrely',
      affiliateNetwork: 'rakuten',
      commissionRate: 0.06,
      currency: 'CAD',
      currencySymbol: '$',
      cta: 'Buy at Indigo',
      ctaShort: 'Indigo',
      color: '#006848',
      isActive: true
    },
    
    UK: {
      name: 'Waterstones',
      slug: 'waterstones',
      logo: '/assets/affiliates/waterstones.svg',
      baseUrl: 'https://www.waterstones.com',
      searchTemplate: 'https://www.waterstones.com/search?term={query}&awc={affiliate_id}',
      productTemplate: 'https://www.waterstones.com/book/{slug}/{isbn}?awc={affiliate_id}',
      affiliateId: process.env.WATERSTONES_AWIN_ID || 'quirrely',
      affiliateNetwork: 'awin',
      commissionRate: 0.06,
      currency: 'GBP',
      currencySymbol: '£',
      cta: 'Buy at Waterstones',
      ctaShort: 'Waterstones',
      color: '#1B4D3E',
      isActive: true
    },
    
    AU: {
      name: 'Booktopia',
      slug: 'booktopia',
      logo: '/assets/affiliates/booktopia.svg',
      baseUrl: 'https://www.booktopia.com.au',
      searchTemplate: 'https://www.booktopia.com.au/search.ep?keywords={query}&affiliate={affiliate_id}',
      productTemplate: 'https://www.booktopia.com.au/book/{isbn}.html?affiliate={affiliate_id}',
      affiliateId: process.env.BOOKTOPIA_AFFILIATE_ID || 'quirrely',
      affiliateNetwork: 'booktopia',
      commissionRate: 0.07,
      currency: 'AUD',
      currencySymbol: '$',
      cta: 'Buy at Booktopia',
      ctaShort: 'Booktopia',
      color: '#E31837',
      isActive: true
    },
    
    NZ: {
      name: 'Mighty Ape',
      slug: 'mightyape',
      logo: '/assets/affiliates/mightyape.svg',
      baseUrl: 'https://www.mightyape.co.nz',
      searchTemplate: 'https://www.mightyape.co.nz/books?q={query}&ref={affiliate_id}',
      productTemplate: 'https://www.mightyape.co.nz/product/{product_id}?ref={affiliate_id}',
      affiliateId: process.env.MIGHTYAPE_AFFILIATE_ID || 'quirrely',
      affiliateNetwork: 'mightyape',
      commissionRate: 0.06,
      currency: 'NZD',
      currencySymbol: '$',
      cta: 'Buy at Mighty Ape',
      ctaShort: 'Mighty Ape',
      color: '#FF6600',
      isActive: true
    }
  },
  
  // ═══════════════════════════════════════════════════════════════
  // TRACKING CONFIGURATION
  // ═══════════════════════════════════════════════════════════════
  
  tracking: {
    enabled: true,
    gaEventName: 'affiliate_click',
    cookieDays: 30,
    sources: ['test_results', 'blog', 'newsletter', 'profile', 'featured_writer']
  },
  
  // ═══════════════════════════════════════════════════════════════
  // DISPLAY CONFIGURATION
  // ═══════════════════════════════════════════════════════════════
  
  display: {
    showPrices: false,  // Don't show prices (vary by retailer)
    showCovers: true,
    maxBooksPerView: 3,
    disclosureText: 'We may earn commission from purchases made through these links.',
    disclosureLink: '/legal/affiliate-disclosure'
  },
  
  // ═══════════════════════════════════════════════════════════════
  // HELPER FUNCTIONS
  // ═══════════════════════════════════════════════════════════════
  
  /**
   * Get retailer config for a country
   */
  getRetailer(countryCode) {
    return this.retailers[countryCode] || this.retailers.CA;
  },
  
  /**
   * Generate affiliate link for a book
   */
  generateLink(isbn, countryCode, source = 'unknown') {
    const retailer = this.getRetailer(countryCode);
    if (!retailer.isActive) return null;
    
    let url = retailer.productTemplate
      .replace('{isbn}', isbn)
      .replace('{affiliate_id}', retailer.affiliateId)
      .replace('{product_id}', isbn)
      .replace('{slug}', '');
    
    // Add source tracking
    url += (url.includes('?') ? '&' : '?') + 'src=' + source;
    
    return url;
  },
  
  /**
   * Generate search link for an author
   */
  generateSearchLink(query, countryCode) {
    const retailer = this.getRetailer(countryCode);
    if (!retailer.isActive) return null;
    
    return retailer.searchTemplate
      .replace('{query}', encodeURIComponent(query))
      .replace('{affiliate_id}', retailer.affiliateId);
  },
  
  /**
   * Track affiliate click
   */
  trackClick(isbn, countryCode, profile, stance, source) {
    if (!this.tracking.enabled) return;
    
    const retailer = this.getRetailer(countryCode);
    const estimatedCommission = 30 * retailer.commissionRate; // Avg $30 book
    
    // GA4 tracking
    if (typeof gtag !== 'undefined') {
      gtag('event', this.tracking.gaEventName, {
        isbn,
        country: countryCode,
        retailer: retailer.slug,
        profile,
        stance,
        source,
        value: estimatedCommission,
        currency: 'USD'
      });
    }
    
    // Beacon to backend (non-blocking)
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/affiliate/click', JSON.stringify({
        isbn, countryCode, profile, stance, source,
        timestamp: Date.now()
      }));
    }
  }
};

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AFFILIATE_CONFIG;
}
