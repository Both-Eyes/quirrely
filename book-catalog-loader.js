/**
 * BOOK CATALOG LOADER
 * ===================
 * Loads affiliate book catalog and provides recommendations.
 * Works with affiliate-config.js and data/affiliate-books.json
 * 
 * Version: 1.0.0
 */

const BOOK_CATALOG = (function() {
  'use strict';
  
  let _catalog = null;
  let _loaded = false;
  
  /**
   * Load catalog from JSON file
   */
  async function load() {
    if (_loaded) return _catalog;
    
    try {
      const response = await fetch('/data/affiliate-books.json');
      _catalog = await response.json();
      _loaded = true;
      return _catalog;
    } catch (error) {
      console.error('Failed to load book catalog:', error);
      return null;
    }
  }
  
  /**
   * Get books for a profile+stance combination
   */
  function getBooks(profile, stance) {
    if (!_catalog) {
      console.warn('Catalog not loaded. Call BOOK_CATALOG.load() first.');
      return [];
    }
    
    const key = `${profile}-${stance}`;
    const combo = _catalog[key];
    
    if (!combo) return [];
    
    return [combo.hero, combo.alt1, combo.alt2].filter(Boolean);
  }
  
  /**
   * Get country-specific author recommendations
   */
  function getLocalAuthors(countryCode) {
    if (!_catalog || !_catalog._country_authors) return [];
    return _catalog._country_authors[countryCode] || [];
  }
  
  /**
   * Search books by author name
   */
  function searchByAuthor(authorName) {
    if (!_catalog) return [];
    
    const results = [];
    for (const [key, combo] of Object.entries(_catalog)) {
      if (key.startsWith('_')) continue;
      
      for (const book of [combo.hero, combo.alt1, combo.alt2]) {
        if (book && book.author.toLowerCase().includes(authorName.toLowerCase())) {
          results.push({ ...book, profile: key });
        }
      }
    }
    return results;
  }
  
  /**
   * Get all unique profiles
   */
  function getProfiles() {
    if (!_catalog) return [];
    return [...new Set(
      Object.keys(_catalog)
        .filter(k => !k.startsWith('_'))
        .map(k => k.split('-')[0])
    )];
  }
  
  return {
    load,
    getBooks,
    getLocalAuthors,
    searchByAuthor,
    getProfiles,
    get isLoaded() { return _loaded; },
    get catalog() { return _catalog; }
  };
})();

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BOOK_CATALOG;
}
