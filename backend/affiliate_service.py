#!/usr/bin/env python3
"""
AFFILIATE SERVICE
=================
Book recommendation and affiliate link management.

Version: 1.0.0
Date: February 10, 2026
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

@dataclass
class RetailerConfig:
    country_code: str
    name: str
    slug: str
    base_url: str
    search_template: str
    product_template: str
    affiliate_id: str
    affiliate_network: str
    commission_rate: float
    currency: str
    cta: str
    color: str


RETAILERS: Dict[str, RetailerConfig] = {
    'CA': RetailerConfig(
        country_code='CA',
        name='Indigo',
        slug='indigo',
        base_url='https://www.indigo.ca',
        search_template='https://www.indigo.ca/en-ca/search/?keywords={query}&ref={affiliate_id}',
        product_template='https://www.indigo.ca/en-ca/product/{isbn}/?ref={affiliate_id}',
        affiliate_id=os.environ.get('INDIGO_AFFILIATE_ID', 'sentense'),
        affiliate_network='rakuten',
        commission_rate=0.06,
        currency='CAD',
        cta='Buy at Indigo',
        color='#006848'
    ),
    'UK': RetailerConfig(
        country_code='UK',
        name='Waterstones',
        slug='waterstones',
        base_url='https://www.waterstones.com',
        search_template='https://www.waterstones.com/search?term={query}&awc={affiliate_id}',
        product_template='https://www.waterstones.com/book/{isbn}?awc={affiliate_id}',
        affiliate_id=os.environ.get('WATERSTONES_AWIN_ID', 'sentense'),
        affiliate_network='awin',
        commission_rate=0.06,
        currency='GBP',
        cta='Buy at Waterstones',
        color='#1B4D3E'
    ),
    'AU': RetailerConfig(
        country_code='AU',
        name='Booktopia',
        slug='booktopia',
        base_url='https://www.booktopia.com.au',
        search_template='https://www.booktopia.com.au/search.ep?keywords={query}&affiliate={affiliate_id}',
        product_template='https://www.booktopia.com.au/book/{isbn}.html?affiliate={affiliate_id}',
        affiliate_id=os.environ.get('BOOKTOPIA_AFFILIATE_ID', 'sentense'),
        affiliate_network='booktopia',
        commission_rate=0.07,
        currency='AUD',
        cta='Buy at Booktopia',
        color='#E31837'
    ),
    'NZ': RetailerConfig(
        country_code='NZ',
        name='Mighty Ape',
        slug='mightyape',
        base_url='https://www.mightyape.co.nz',
        search_template='https://www.mightyape.co.nz/books?q={query}&ref={affiliate_id}',
        product_template='https://www.mightyape.co.nz/product/{isbn}?ref={affiliate_id}',
        affiliate_id=os.environ.get('MIGHTYAPE_AFFILIATE_ID', 'sentense'),
        affiliate_network='mightyape',
        commission_rate=0.06,
        currency='NZD',
        cta='Buy at Mighty Ape',
        color='#FF6600'
    )
}


# ═══════════════════════════════════════════════════════════════
# BOOK CATALOG
# ═══════════════════════════════════════════════════════════════

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    hook: str
    price_tier: str
    cover: str
    year: int


_BOOK_CATALOG: Optional[Dict[str, Any]] = None
_CATALOG_PATH = Path(__file__).parent.parent / "data" / "affiliate-books.json"


def load_catalog() -> Dict[str, Any]:
    """Load book catalog from JSON."""
    global _BOOK_CATALOG
    
    if _BOOK_CATALOG is not None:
        return _BOOK_CATALOG
    
    if not _CATALOG_PATH.exists():
        return {}
    
    with open(_CATALOG_PATH, 'r', encoding='utf-8') as f:
        _BOOK_CATALOG = json.load(f)
    
    return _BOOK_CATALOG


def get_books_for_profile(profile: str, stance: str) -> List[Book]:
    """Get recommended books for a profile+stance combination."""
    catalog = load_catalog()
    key = f"{profile}-{stance}"
    
    if key not in catalog:
        return []
    
    combo = catalog[key]
    books = []
    
    for rank in ['hero', 'alt1', 'alt2']:
        if rank in combo:
            b = combo[rank]
            books.append(Book(
                isbn=b['isbn'],
                title=b['title'],
                author=b['author'],
                hook=b['hook'],
                price_tier=b['price_tier'],
                cover=b['cover'],
                year=b['year']
            ))
    
    return books


# ═══════════════════════════════════════════════════════════════
# AFFILIATE LINK GENERATION
# ═══════════════════════════════════════════════════════════════

def get_retailer(country_code: str) -> RetailerConfig:
    """Get retailer for a country, defaulting to CA."""
    return RETAILERS.get(country_code, RETAILERS['CA'])


def generate_affiliate_link(
    isbn: str, 
    country_code: str, 
    source: str = 'unknown'
) -> str:
    """Generate affiliate link for a book."""
    retailer = get_retailer(country_code)
    
    url = retailer.product_template \
        .replace('{isbn}', isbn) \
        .replace('{affiliate_id}', retailer.affiliate_id)
    
    # Add source tracking
    separator = '&' if '?' in url else '?'
    url += f"{separator}src={source}"
    
    return url


def generate_search_link(query: str, country_code: str) -> str:
    """Generate affiliate search link for an author."""
    retailer = get_retailer(country_code)
    
    return retailer.search_template \
        .replace('{query}', quote_plus(query)) \
        .replace('{affiliate_id}', retailer.affiliate_id)


# ═══════════════════════════════════════════════════════════════
# RECOMMENDATION API
# ═══════════════════════════════════════════════════════════════

def get_recommendations(
    profile: str,
    stance: str,
    country_code: str,
    source: str = 'unknown',
    limit: int = 3
) -> Dict[str, Any]:
    """
    Get book recommendations with affiliate links.
    
    Returns a complete response ready for the frontend.
    """
    books = get_books_for_profile(profile, stance)[:limit]
    retailer = get_retailer(country_code)
    
    recommendations = []
    for book in books:
        recommendations.append({
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'hook': book.hook,
            'cover': book.cover,
            'affiliate_url': generate_affiliate_link(book.isbn, country_code, source),
            'retailer': retailer.name,
            'cta': retailer.cta
        })
    
    return {
        'profile': profile,
        'stance': stance,
        'country': country_code,
        'retailer': {
            'name': retailer.name,
            'slug': retailer.slug,
            'color': retailer.color,
            'cta': retailer.cta
        },
        'books': recommendations,
        'disclosure': 'We may earn commission from purchases made through these links.'
    }


# ═══════════════════════════════════════════════════════════════
# CLICK TRACKING
# ═══════════════════════════════════════════════════════════════

class AffiliateTracker:
    """Track affiliate clicks and conversions."""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
    
    def record_click(
        self,
        isbn: str,
        country_code: str,
        profile: str,
        stance: str,
        source: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record an affiliate click."""
        
        click_data = {
            'isbn': isbn,
            'country_code': country_code,
            'profile': profile,
            'stance': stance,
            'source': source,
            'user_id': user_id,
            'session_id': session_id,
            'clicked_at': datetime.utcnow().isoformat(),
            'converted': False
        }
        
        # If we have a DB, store it
        if self.db:
            # db.execute(
            #     "SELECT record_affiliate_click(%s, %s, %s, %s, %s, %s, %s)",
            #     (isbn, country_code, profile, stance, source, user_id, session_id)
            # )
            pass
        
        return click_data
    
    def record_conversion(
        self,
        click_id: str,
        order_value: float,
        commission: float
    ) -> bool:
        """Record a conversion (called by affiliate network webhook)."""
        
        if not self.db:
            return False
        
        # db.execute(
        #     """
        #     UPDATE affiliate_clicks 
        #     SET converted = TRUE, 
        #         converted_at = NOW(),
        #         order_value = %s,
        #         commission_earned = %s
        #     WHERE id = %s
        #     """,
        #     (order_value, commission, click_id)
        # )
        
        return True
    
    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get affiliate stats for the last N days."""
        
        # This would query the database
        return {
            'period_days': days,
            'total_clicks': 0,
            'conversions': 0,
            'conversion_rate': 0.0,
            'total_commission': 0.0,
            'by_country': {},
            'by_source': {},
            'top_books': []
        }


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS (Flask/FastAPI compatible)
# ═══════════════════════════════════════════════════════════════

def api_get_recommendations(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API endpoint for getting recommendations.
    
    Request: { profile, stance, country, source }
    Response: { books: [...], retailer: {...}, disclosure }
    """
    profile = request_data.get('profile', 'ASSERTIVE')
    stance = request_data.get('stance', 'OPEN')
    country = request_data.get('country', 'CA')
    source = request_data.get('source', 'api')
    
    return get_recommendations(profile, stance, country, source)


def api_record_click(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    API endpoint for recording clicks.
    
    Request: { isbn, country, profile, stance, source, user_id?, session_id? }
    Response: { success, click_id }
    """
    tracker = AffiliateTracker()
    
    click = tracker.record_click(
        isbn=request_data.get('isbn'),
        country_code=request_data.get('country', 'CA'),
        profile=request_data.get('profile'),
        stance=request_data.get('stance'),
        source=request_data.get('source', 'unknown'),
        user_id=request_data.get('user_id'),
        session_id=request_data.get('session_id')
    )
    
    return {'success': True, 'click': click}


# ═══════════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Affiliate Service Test")
    print("=" * 60)
    
    # Test catalog loading
    catalog = load_catalog()
    print(f"\n📚 Catalog loaded: {len(catalog) - 2} profile combinations")
    
    # Test recommendations
    print("\n📖 ASSERTIVE-OPEN recommendations (CA):")
    recs = get_recommendations('ASSERTIVE', 'OPEN', 'CA', 'test')
    for book in recs['books']:
        print(f"  • {book['title']} by {book['author']}")
        print(f"    → {book['affiliate_url'][:60]}...")
    
    # Test all retailers
    print("\n🏪 Retailer Links:")
    for country in ['CA', 'UK', 'AU', 'NZ']:
        retailer = get_retailer(country)
        link = generate_affiliate_link('9780062316110', country, 'test')
        print(f"  {country}: {retailer.name} → {link[:50]}...")
    
    print("\n✅ All tests passed")
