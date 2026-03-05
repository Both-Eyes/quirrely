#!/usr/bin/env python3
"""
LNCP META/BLOG: CONFIG v1.0
Tunable configuration for blog content and SEO optimization.

All blog parameters that can be auto-adjusted live here.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# BLOG CONFIG TYPES
# ═══════════════════════════════════════════════════════════════════════════

class CTAPlacement(str, Enum):
    AFTER_INTRO = "after_intro"
    FLOATING = "floating"
    END_OF_CONTENT = "end"
    MULTIPLE = "multiple"  # After intro + end


class CTAStyle(str, Enum):
    BUTTON = "button"
    INLINE_LINK = "inline_link"
    CARD = "card"
    BANNER = "banner"


# ═══════════════════════════════════════════════════════════════════════════
# META TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MetaTemplate:
    """Template for meta tags."""
    id: str
    title_template: str
    description_template: str
    active: bool = True
    performance_score: float = 0.0  # Updated by feedback loop
    impressions: int = 0
    clicks: int = 0
    
    @property
    def ctr(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions


# Default meta templates (will A/B test these)
META_TEMPLATES: Dict[str, MetaTemplate] = {
    "default": MetaTemplate(
        id="default",
        title_template="How {style} {certitude} Writers Write | Quirrely",
        description_template="Discover the unique patterns of {style} {certitude} writers. Learn how this voice profile shapes writing style, word choice, and expression.",
    ),
    "question": MetaTemplate(
        id="question",
        title_template="Are You a {style} {certitude} Writer? | Quirrely",
        description_template="Find out if you're a {style} {certitude} writer. Take the free voice analysis and discover your unique writing profile.",
    ),
    "discovery": MetaTemplate(
        id="discovery",
        title_template="{style} {certitude} Writing Style: What Makes It Unique",
        description_template="The {style} {certitude} voice profile explained. See real examples and discover if this is your natural writing style.",
    ),
    "action": MetaTemplate(
        id="action",
        title_template="Write Like a {style} {certitude} Writer | Free Analysis",
        description_template="Unlock your {style} {certitude} writing potential. Get instant feedback on your voice profile with Quirrely's free analysis.",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# CTA CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CTAVariant:
    """A CTA copy/style variant."""
    id: str
    text: str
    subtext: Optional[str] = None
    style: CTAStyle = CTAStyle.BUTTON
    active: bool = True
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    
    @property
    def click_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions
    
    @property
    def conversion_rate(self) -> float:
        if self.clicks == 0:
            return 0.0
        return self.conversions / self.clicks


# CTA variants to test
CTA_VARIANTS: Dict[str, CTAVariant] = {
    "discover": CTAVariant(
        id="discover",
        text="Discover Your Voice →",
        subtext="Free • Takes 30 seconds",
    ),
    "find": CTAVariant(
        id="find",
        text="Find Your Writing Profile →",
        subtext="No signup required",
    ),
    "whats_your": CTAVariant(
        id="whats_your",
        text="What's Your Voice?",
        subtext="Paste any text to find out",
    ),
    "analyze": CTAVariant(
        id="analyze",
        text="Analyze Your Writing →",
        subtext="Instant results",
    ),
    "am_i": CTAVariant(
        id="am_i",
        text="Am I a {profile}?",
        subtext="Find out now →",
    ),
    "try_free": CTAVariant(
        id="try_free",
        text="Try Free Voice Analysis",
        subtext="See your profile in seconds",
        style=CTAStyle.CARD,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# CONTENT STRUCTURE CONFIG
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ContentConfig:
    """Configuration for blog content structure."""
    
    # CTA placement
    cta_placement: CTAPlacement = CTAPlacement.MULTIPLE
    cta_after_intro_position: int = 2  # After paragraph 2
    show_floating_cta: bool = False
    floating_cta_delay_seconds: int = 30
    
    # Internal linking
    related_profiles_count: int = 3
    show_opposite_profile: bool = True
    internal_links_per_post: int = 5
    
    # Schema
    include_article_schema: bool = True
    include_faq_schema: bool = True
    include_howto_schema: bool = False
    include_breadcrumb_schema: bool = True
    
    # Social
    include_twitter_card: bool = True
    include_og_tags: bool = True
    
    # Performance
    lazy_load_images: bool = True
    preconnect_domains: List[str] = None
    
    def __post_init__(self):
        if self.preconnect_domains is None:
            self.preconnect_domains = [
                "https://fonts.googleapis.com",
                "https://www.googletagmanager.com",
            ]


# ═══════════════════════════════════════════════════════════════════════════
# SEO CONFIG
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SEOConfig:
    """SEO-specific configuration."""
    
    # Keyword strategy
    primary_keyword_in_title: bool = True
    primary_keyword_in_h1: bool = True
    primary_keyword_in_first_100_words: bool = True
    
    # URL structure
    url_pattern: str = "/blog/how-{style}-{certitude}-writers-write"
    
    # Canonical
    use_canonical: bool = True
    canonical_domain: str = "https://quirrely.io"
    
    # Indexing
    noindex_thin_content: bool = True
    thin_content_word_threshold: int = 300
    
    # Performance targets
    target_word_count_min: int = 1200
    target_word_count_max: int = 2500
    target_reading_time_minutes: int = 6
    
    # Freshness
    show_updated_date: bool = True
    auto_update_threshold_days: int = 90  # Flag for refresh after 90 days


# ═══════════════════════════════════════════════════════════════════════════
# BLOG CONFIG STORE
# ═══════════════════════════════════════════════════════════════════════════

class BlogConfigStore:
    """
    Centralized store for all blog configuration.
    Mirrors the main ConfigStore pattern but for blog-specific settings.
    """
    
    def __init__(self):
        self.meta_templates = META_TEMPLATES.copy()
        self.cta_variants = CTA_VARIANTS.copy()
        self.content_config = ContentConfig()
        self.seo_config = SEOConfig()
        
        # A/B test assignments (page_url -> variant_id)
        self.meta_assignments: Dict[str, str] = {}
        self.cta_assignments: Dict[str, str] = {}
        
        # Change history
        self.changes: List[Dict] = []
    
    def get_meta_template(self, page_url: str) -> MetaTemplate:
        """Get the meta template for a page (respecting A/B assignment)."""
        if page_url in self.meta_assignments:
            template_id = self.meta_assignments[page_url]
            return self.meta_templates.get(template_id, self.meta_templates["default"])
        return self.meta_templates["default"]
    
    def get_cta_variant(self, page_url: str) -> CTAVariant:
        """Get the CTA variant for a page (respecting A/B assignment)."""
        if page_url in self.cta_assignments:
            variant_id = self.cta_assignments[page_url]
            return self.cta_variants.get(variant_id, self.cta_variants["discover"])
        return self.cta_variants["discover"]
    
    def assign_meta_template(self, page_url: str, template_id: str):
        """Assign a meta template to a page."""
        old = self.meta_assignments.get(page_url)
        self.meta_assignments[page_url] = template_id
        self._log_change("meta_template", page_url, old, template_id)
    
    def assign_cta_variant(self, page_url: str, variant_id: str):
        """Assign a CTA variant to a page."""
        old = self.cta_assignments.get(page_url)
        self.cta_assignments[page_url] = variant_id
        self._log_change("cta_variant", page_url, old, variant_id)
    
    def update_meta_performance(self, template_id: str, impressions: int, clicks: int):
        """Update performance metrics for a meta template."""
        if template_id in self.meta_templates:
            t = self.meta_templates[template_id]
            t.impressions += impressions
            t.clicks += clicks
    
    def update_cta_performance(self, variant_id: str, impressions: int, clicks: int, conversions: int):
        """Update performance metrics for a CTA variant."""
        if variant_id in self.cta_variants:
            v = self.cta_variants[variant_id]
            v.impressions += impressions
            v.clicks += clicks
            v.conversions += conversions
    
    def get_best_meta_template(self) -> MetaTemplate:
        """Get the best performing meta template."""
        active = [t for t in self.meta_templates.values() if t.active and t.impressions > 100]
        if not active:
            return self.meta_templates["default"]
        return max(active, key=lambda t: t.ctr)
    
    def get_best_cta_variant(self) -> CTAVariant:
        """Get the best performing CTA variant."""
        active = [v for v in self.cta_variants.values() if v.active and v.impressions > 100]
        if not active:
            return self.cta_variants["discover"]
        return max(active, key=lambda v: v.conversion_rate)
    
    def _log_change(self, change_type: str, target: str, old_value: Any, new_value: Any):
        """Log a configuration change."""
        self.changes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": change_type,
            "target": target,
            "old_value": old_value,
            "new_value": new_value,
        })
    
    def get_status(self) -> Dict:
        """Get current status of blog config."""
        return {
            "meta_templates": {
                "count": len(self.meta_templates),
                "active": len([t for t in self.meta_templates.values() if t.active]),
                "best": self.get_best_meta_template().id,
            },
            "cta_variants": {
                "count": len(self.cta_variants),
                "active": len([v for v in self.cta_variants.values() if v.active]),
                "best": self.get_best_cta_variant().id,
            },
            "assignments": {
                "meta": len(self.meta_assignments),
                "cta": len(self.cta_assignments),
            },
            "changes": len(self.changes),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_blog_config: Optional[BlogConfigStore] = None

def get_blog_config() -> BlogConfigStore:
    """Get the global blog config store."""
    global _blog_config
    if _blog_config is None:
        _blog_config = BlogConfigStore()
    return _blog_config


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "CTAPlacement",
    "CTAStyle",
    "MetaTemplate",
    "CTAVariant",
    "ContentConfig",
    "SEOConfig",
    "BlogConfigStore",
    "META_TEMPLATES",
    "CTA_VARIANTS",
    "get_blog_config",
]
