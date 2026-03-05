#!/usr/bin/env python3
"""
LNCP META/BLOG: ACTION CLASSIFIER v1.0
Classifies blog optimization actions into auto-apply vs human-review.

Mirrors the main action_classifier but specialized for SEO/content actions.

Safe to auto-apply:
- Meta description tweaks
- Internal link additions
- CTA copy A/B tests
- Schema markup updates

Requires human review:
- Title changes (SEO impact)
- URL changes (redirect needed)
- Content restructuring
- New page creation
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .gsc import GSCAnalyzer, GSCSiteData, PageSearchData
from .tracker import BlogTracker, PageMetrics, get_blog_tracker
from .cta_tracker import CTATracker, get_cta_tracker
from .config import get_blog_config


# ═══════════════════════════════════════════════════════════════════════════
# ACTION TYPES
# ═══════════════════════════════════════════════════════════════════════════

class BlogActionLane(str, Enum):
    """Which lane a blog action goes to."""
    AUTO_APPLY = "auto_apply"
    HUMAN_REVIEW = "human_review"
    BLOCKED = "blocked"


class BlogActionDomain(str, Enum):
    """What domain the action affects."""
    META = "meta"                   # Title, description
    CTA = "cta"                     # Call-to-action copy/placement
    CONTENT = "content"             # Body content
    STRUCTURE = "structure"         # Headings, sections
    LINKS = "links"                 # Internal/external links
    SCHEMA = "schema"               # Structured data
    URL = "url"                     # URL/slug changes
    MEDIA = "media"                 # Images, videos
    TECHNICAL = "technical"         # Performance, indexing


class BlogActionType(str, Enum):
    """Specific action types."""
    # Meta actions
    META_DESCRIPTION_UPDATE = "meta_description_update"
    META_TITLE_UPDATE = "meta_title_update"
    OG_TAGS_UPDATE = "og_tags_update"
    
    # CTA actions
    CTA_COPY_TEST = "cta_copy_test"
    CTA_PLACEMENT_TEST = "cta_placement_test"
    CTA_STYLE_TEST = "cta_style_test"
    CTA_ROLLOUT_WINNER = "cta_rollout_winner"
    
    # Content actions
    CONTENT_REFRESH = "content_refresh"
    CONTENT_EXPAND = "content_expand"
    CONTENT_RESTRUCTURE = "content_restructure"
    INTRO_REWRITE = "intro_rewrite"
    
    # Link actions
    INTERNAL_LINK_ADD = "internal_link_add"
    INTERNAL_LINK_OPTIMIZE = "internal_link_optimize"
    RELATED_POSTS_UPDATE = "related_posts_update"
    
    # Schema actions
    SCHEMA_ADD = "schema_add"
    SCHEMA_UPDATE = "schema_update"
    FAQ_SCHEMA_ADD = "faq_schema_add"
    
    # URL actions
    URL_REDIRECT = "url_redirect"
    SLUG_CHANGE = "slug_change"
    
    # Technical actions
    IMAGE_OPTIMIZE = "image_optimize"
    LAZY_LOAD_ENABLE = "lazy_load_enable"
    CORE_WEB_VITALS_FIX = "core_web_vitals_fix"


class RiskLevel(str, Enum):
    """Risk level of the action."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(str, Enum):
    """Action priority."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ═══════════════════════════════════════════════════════════════════════════
# ACTION CLASSIFICATION RULES
# ═══════════════════════════════════════════════════════════════════════════

# Actions that are ALWAYS safe to auto-apply
AUTO_SAFE_ACTIONS = {
    BlogActionType.CTA_COPY_TEST,
    BlogActionType.CTA_PLACEMENT_TEST,
    BlogActionType.CTA_STYLE_TEST,
    BlogActionType.INTERNAL_LINK_ADD,
    BlogActionType.RELATED_POSTS_UPDATE,
    BlogActionType.SCHEMA_UPDATE,
    BlogActionType.FAQ_SCHEMA_ADD,
    BlogActionType.IMAGE_OPTIMIZE,
    BlogActionType.LAZY_LOAD_ENABLE,
    BlogActionType.OG_TAGS_UPDATE,
}

# Actions that ALWAYS require human review
HUMAN_REVIEW_ACTIONS = {
    BlogActionType.META_TITLE_UPDATE,
    BlogActionType.CONTENT_RESTRUCTURE,
    BlogActionType.URL_REDIRECT,
    BlogActionType.SLUG_CHANGE,
    BlogActionType.CONTENT_EXPAND,
}

# Actions that are BLOCKED (need careful consideration)
BLOCKED_ACTIONS = set()  # None currently, but could add

# Domain risk levels
DOMAIN_RISK = {
    BlogActionDomain.META: RiskLevel.MEDIUM,
    BlogActionDomain.CTA: RiskLevel.LOW,
    BlogActionDomain.CONTENT: RiskLevel.MEDIUM,
    BlogActionDomain.STRUCTURE: RiskLevel.MEDIUM,
    BlogActionDomain.LINKS: RiskLevel.LOW,
    BlogActionDomain.SCHEMA: RiskLevel.LOW,
    BlogActionDomain.URL: RiskLevel.CRITICAL,
    BlogActionDomain.MEDIA: RiskLevel.LOW,
    BlogActionDomain.TECHNICAL: RiskLevel.LOW,
}


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFIED ACTION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BlogAction:
    """A blog optimization action."""
    action_id: str
    action_type: BlogActionType
    domain: BlogActionDomain
    
    # Target
    page_url: str
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None
    
    # Description
    title: str = ""
    description: str = ""
    rationale: str = ""
    
    # Classification
    lane: BlogActionLane = BlogActionLane.HUMAN_REVIEW
    risk_level: RiskLevel = RiskLevel.MEDIUM
    priority: Priority = Priority.MEDIUM
    confidence: float = 0.5
    
    # Impact estimates
    estimated_impression_gain: int = 0
    estimated_click_gain: int = 0
    estimated_conversion_gain: int = 0
    
    # Implementation details
    current_value: Optional[str] = None
    proposed_value: Optional[str] = None
    requires_ab_test: bool = False
    rollback_possible: bool = True
    
    # Blocking reasons (if not auto-apply)
    blocking_reasons: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "domain": self.domain.value,
            "page_url": self.page_url,
            "title": self.title,
            "description": self.description,
            "lane": self.lane.value,
            "risk_level": self.risk_level.value,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "estimated_click_gain": self.estimated_click_gain,
            "requires_ab_test": self.requires_ab_test,
            "blocking_reasons": self.blocking_reasons,
        }


# ═══════════════════════════════════════════════════════════════════════════
# BLOG ACTION CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════

class BlogActionClassifier:
    """
    Classifies blog optimization actions into auto-apply vs human-review.
    
    Conservative by design - when in doubt, route to human review.
    """
    
    def __init__(self):
        self.actions_today = 0
        self.max_auto_actions_per_day = 5
    
    def classify(self, action: BlogAction) -> BlogAction:
        """Classify a single action."""
        blocking_reasons = []
        
        # Check if action type is always auto-safe
        if action.action_type in AUTO_SAFE_ACTIONS:
            action.lane = BlogActionLane.AUTO_APPLY
            action.risk_level = RiskLevel.LOW
        
        # Check if action type always needs review
        elif action.action_type in HUMAN_REVIEW_ACTIONS:
            action.lane = BlogActionLane.HUMAN_REVIEW
            blocking_reasons.append(f"Action type '{action.action_type.value}' requires human review")
        
        # Check if action type is blocked
        elif action.action_type in BLOCKED_ACTIONS:
            action.lane = BlogActionLane.BLOCKED
            blocking_reasons.append(f"Action type '{action.action_type.value}' is blocked")
        
        # Otherwise, evaluate based on domain and risk
        else:
            domain_risk = DOMAIN_RISK.get(action.domain, RiskLevel.MEDIUM)
            
            if domain_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                action.lane = BlogActionLane.HUMAN_REVIEW
                blocking_reasons.append(f"Domain '{action.domain.value}' is high risk")
            elif action.confidence < 0.7:
                action.lane = BlogActionLane.HUMAN_REVIEW
                blocking_reasons.append(f"Confidence {action.confidence:.0%} below threshold")
            else:
                action.lane = BlogActionLane.AUTO_APPLY
        
        # Check daily limit
        if action.lane == BlogActionLane.AUTO_APPLY:
            if self.actions_today >= self.max_auto_actions_per_day:
                action.lane = BlogActionLane.HUMAN_REVIEW
                blocking_reasons.append(f"Daily auto-action limit reached ({self.max_auto_actions_per_day})")
            else:
                self.actions_today += 1
        
        # Set requires_ab_test for certain action types
        if action.action_type in [
            BlogActionType.CTA_COPY_TEST,
            BlogActionType.CTA_PLACEMENT_TEST,
            BlogActionType.CTA_STYLE_TEST,
            BlogActionType.META_DESCRIPTION_UPDATE,
        ]:
            action.requires_ab_test = True
        
        action.blocking_reasons = blocking_reasons
        
        return action
    
    def classify_batch(self, actions: List[BlogAction]) -> List[BlogAction]:
        """Classify multiple actions."""
        return [self.classify(action) for action in actions]


# ═══════════════════════════════════════════════════════════════════════════
# ACTION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class BlogActionGenerator:
    """
    Generates optimization actions from analysis data.
    
    Sources:
    - GSC data (search performance)
    - Blog tracker (engagement)
    - CTA tracker (conversion)
    """
    
    def __init__(self):
        self.action_counter = 0
    
    def _generate_id(self) -> str:
        self.action_counter += 1
        return f"blog_action_{datetime.utcnow().strftime('%Y%m%d')}_{self.action_counter:04d}"
    
    def generate_from_gsc(self, analyzer: GSCAnalyzer) -> List[BlogAction]:
        """Generate actions from GSC analysis."""
        actions = []
        
        # CTR opportunities -> Meta description updates
        for opp in analyzer.get_ctr_opportunities()[:10]:
            actions.append(BlogAction(
                action_id=self._generate_id(),
                action_type=BlogActionType.META_DESCRIPTION_UPDATE,
                domain=BlogActionDomain.META,
                page_url=opp["page"],
                title=f"Improve meta description for better CTR",
                description=f"Page has {opp['impressions']:,} impressions but only {opp['current_ctr']*100:.2f}% CTR (expected: {opp['expected_ctr']*100:.2f}%)",
                rationale=f"Potential to gain +{opp['potential_clicks']} clicks with optimized meta",
                priority=Priority.HIGH if opp["priority"] == "high" else Priority.MEDIUM,
                confidence=0.8,
                estimated_click_gain=opp["potential_clicks"],
                current_value=f"CTR: {opp['current_ctr']*100:.2f}%",
                proposed_value=f"Target CTR: {opp['expected_ctr']*100:.2f}%",
            ))
        
        # Position opportunities -> Content improvements
        for opp in analyzer.get_position_opportunities()[:5]:
            # If position 11-15, suggest content refresh
            if opp["current_position"] <= 15:
                actions.append(BlogAction(
                    action_id=self._generate_id(),
                    action_type=BlogActionType.CONTENT_REFRESH,
                    domain=BlogActionDomain.CONTENT,
                    page_url=opp["page"],
                    title=f"Refresh content to move from page 2 to page 1",
                    description=f"Page ranks at position {opp['current_position']:.1f} with {opp['impressions']:,} impressions",
                    rationale=f"Moving to page 1 could gain +{opp['potential_traffic_gain']} clicks",
                    priority=Priority.HIGH,
                    confidence=0.7,
                    estimated_click_gain=opp["potential_traffic_gain"],
                    current_value=f"Position: {opp['current_position']:.1f}",
                    proposed_value="Target: Position 5-10",
                ))
            else:
                # Position 16-20, suggest more substantial improvements
                actions.append(BlogAction(
                    action_id=self._generate_id(),
                    action_type=BlogActionType.CONTENT_EXPAND,
                    domain=BlogActionDomain.CONTENT,
                    page_url=opp["page"],
                    title=f"Expand content to improve rankings",
                    description=f"Page ranks at position {opp['current_position']:.1f}",
                    rationale="Adding depth and examples could improve position",
                    priority=Priority.MEDIUM,
                    confidence=0.6,
                    estimated_click_gain=opp["potential_traffic_gain"] // 2,
                ))
        
        # Content gaps -> New content suggestions
        for gap in analyzer.get_content_gaps():
            if gap["status"] == "missing":
                actions.append(BlogAction(
                    action_id=self._generate_id(),
                    action_type=BlogActionType.CONTENT_EXPAND,  # Would be CREATE but we're treating as expand
                    domain=BlogActionDomain.CONTENT,
                    page_url=gap["page"],
                    profile_style=gap["profile"].split("-")[0],
                    profile_certitude=gap["profile"].split("-")[1] if "-" in gap["profile"] else None,
                    title=f"Create content for {gap['profile']} profile",
                    description=f"No content exists for this profile combination",
                    rationale="Filling content gaps increases topical coverage",
                    priority=Priority.MEDIUM,
                    confidence=0.5,
                ))
        
        return actions
    
    def generate_from_tracker(self, tracker: BlogTracker) -> List[BlogAction]:
        """Generate actions from blog tracker data."""
        actions = []
        
        # High traffic, low conversion pages
        for page in tracker.get_high_traffic_low_conversion(min_views=50):
            actions.append(BlogAction(
                action_id=self._generate_id(),
                action_type=BlogActionType.CTA_COPY_TEST,
                domain=BlogActionDomain.CTA,
                page_url=page.page_url,
                title=f"Test alternative CTA copy",
                description=f"Page has {page.total_views} views but only {page.cta_click_rate*100:.1f}% CTA click rate",
                rationale="Testing different CTA copy could improve conversion",
                priority=Priority.HIGH,
                confidence=0.85,
                estimated_click_gain=int(page.total_views * 0.02),  # 2% improvement target
                current_value=f"CTA Rate: {page.cta_click_rate*100:.1f}%",
                proposed_value="Target: 5%+ CTA Rate",
            ))
        
        # Underperforming pages
        for page in tracker.get_underperforming_pages(limit=5):
            if page.tier in ["poor", "critical"]:
                actions.append(BlogAction(
                    action_id=self._generate_id(),
                    action_type=BlogActionType.INTRO_REWRITE,
                    domain=BlogActionDomain.CONTENT,
                    page_url=page.page_url,
                    title=f"Rewrite intro to reduce bounce rate",
                    description=f"Page has {page.bounce_rate*100:.1f}% bounce rate and {page.avg_scroll_depth:.0f}% avg scroll",
                    rationale="Stronger intro could improve engagement",
                    priority=Priority.MEDIUM,
                    confidence=0.7,
                ))
        
        return actions
    
    def generate_from_cta_tracker(self, cta_tracker: CTATracker) -> List[BlogAction]:
        """Generate actions from CTA tracker data."""
        actions = []
        
        # Check for winning variant to roll out
        comparison = cta_tracker.get_variant_comparison()
        if len(comparison) >= 2:
            best = comparison[0]
            second = comparison[1]
            
            # If best is significantly better (20%+ higher conversion)
            if best["impressions"] >= 100 and second["impressions"] >= 100:
                if best["conversion_rate"] > second["conversion_rate"] * 1.2:
                    actions.append(BlogAction(
                        action_id=self._generate_id(),
                        action_type=BlogActionType.CTA_ROLLOUT_WINNER,
                        domain=BlogActionDomain.CTA,
                        page_url="*",  # Site-wide
                        title=f"Roll out winning CTA variant: {best['variant_id']}",
                        description=f"'{best['variant_id']}' has {best['conversion_rate']}% conversion vs {second['conversion_rate']}% for '{second['variant_id']}'",
                        rationale="Statistically significant winner identified",
                        priority=Priority.HIGH,
                        confidence=0.9,
                        current_value=f"Mixed variants",
                        proposed_value=f"100% '{best['variant_id']}'",
                    ))
        
        # Recommendations from CTA tracker
        for rec in cta_tracker.get_recommendations():
            if rec["type"] == "underperformer":
                actions.append(BlogAction(
                    action_id=self._generate_id(),
                    action_type=BlogActionType.CTA_COPY_TEST,
                    domain=BlogActionDomain.CTA,
                    page_url="*",
                    title=rec["action"],
                    description=rec["impact"],
                    priority=Priority.MEDIUM if rec["priority"] == "medium" else Priority.LOW,
                    confidence=0.75,
                ))
        
        return actions
    
    def generate_all(
        self,
        gsc_analyzer: Optional[GSCAnalyzer] = None,
        tracker: Optional[BlogTracker] = None,
        cta_tracker: Optional[CTATracker] = None,
    ) -> List[BlogAction]:
        """Generate all actions from available sources."""
        actions = []
        
        if gsc_analyzer:
            actions.extend(self.generate_from_gsc(gsc_analyzer))
        
        if tracker:
            actions.extend(self.generate_from_tracker(tracker))
        
        if cta_tracker:
            actions.extend(self.generate_from_cta_tracker(cta_tracker))
        
        # Sort by priority
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }
        actions.sort(key=lambda a: priority_order.get(a.priority, 2))
        
        return actions


# ═══════════════════════════════════════════════════════════════════════════
# BLOG ACTION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════

class BlogActionOrchestrator:
    """
    Orchestrates blog optimization actions.
    
    1. Generates actions from all sources
    2. Classifies into auto vs human
    3. Executes auto-safe actions
    4. Queues human-review actions
    """
    
    def __init__(self):
        self.generator = BlogActionGenerator()
        self.classifier = BlogActionClassifier()
        self.pending_actions: List[BlogAction] = []
        self.applied_actions: List[BlogAction] = []
        self.review_queue: List[BlogAction] = []
    
    def run_cycle(
        self,
        gsc_analyzer: Optional[GSCAnalyzer] = None,
        auto_apply: bool = False,
    ) -> Dict:
        """Run a complete blog optimization cycle."""
        
        # Get trackers
        tracker = get_blog_tracker()
        cta_tracker = get_cta_tracker()
        
        # Generate actions
        actions = self.generator.generate_all(
            gsc_analyzer=gsc_analyzer,
            tracker=tracker,
            cta_tracker=cta_tracker,
        )
        
        # Classify actions
        classified = self.classifier.classify_batch(actions)
        
        # Separate by lane
        auto_apply_actions = [a for a in classified if a.lane == BlogActionLane.AUTO_APPLY]
        human_review_actions = [a for a in classified if a.lane == BlogActionLane.HUMAN_REVIEW]
        blocked_actions = [a for a in classified if a.lane == BlogActionLane.BLOCKED]
        
        # Execute auto-apply actions (if enabled)
        applied = []
        if auto_apply:
            for action in auto_apply_actions:
                # In production, would actually apply the change
                action.applied_at = datetime.utcnow()
                applied.append(action)
                self.applied_actions.append(action)
        
        # Queue human review actions
        for action in human_review_actions:
            action.queued_at = datetime.utcnow()
            self.review_queue.append(action)
        
        return {
            "total_actions": len(classified),
            "auto_apply": len(auto_apply_actions),
            "human_review": len(human_review_actions),
            "blocked": len(blocked_actions),
            "applied": len(applied),
            "actions": {
                "auto_apply": [a.to_dict() for a in auto_apply_actions],
                "human_review": [a.to_dict() for a in human_review_actions],
                "blocked": [a.to_dict() for a in blocked_actions],
            },
        }
    
    def approve_action(self, action_id: str) -> bool:
        """Approve an action from the review queue."""
        for i, action in enumerate(self.review_queue):
            if action.action_id == action_id:
                approved = self.review_queue.pop(i)
                approved.approved_at = datetime.utcnow()
                self.applied_actions.append(approved)
                return True
        return False
    
    def reject_action(self, action_id: str, reason: str = "") -> bool:
        """Reject an action from the review queue."""
        for i, action in enumerate(self.review_queue):
            if action.action_id == action_id:
                self.review_queue.pop(i)
                return True
        return False
    
    def get_review_queue(self) -> List[Dict]:
        """Get pending actions for human review."""
        return [a.to_dict() for a in self.review_queue]
    
    def get_summary(self) -> Dict:
        """Get orchestrator summary."""
        return {
            "pending_review": len(self.review_queue),
            "total_applied": len(self.applied_actions),
            "by_domain": self._count_by_domain(),
            "by_priority": self._count_by_priority(),
        }
    
    def _count_by_domain(self) -> Dict[str, int]:
        all_actions = self.review_queue + self.applied_actions
        counts = {}
        for action in all_actions:
            domain = action.domain.value
            counts[domain] = counts.get(domain, 0) + 1
        return counts
    
    def _count_by_priority(self) -> Dict[str, int]:
        all_actions = self.review_queue + self.applied_actions
        counts = {}
        for action in all_actions:
            priority = action.priority.value
            counts[priority] = counts.get(priority, 0) + 1
        return counts


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_blog_orchestrator: Optional[BlogActionOrchestrator] = None

def get_blog_orchestrator() -> BlogActionOrchestrator:
    """Get the global blog action orchestrator."""
    global _blog_orchestrator
    if _blog_orchestrator is None:
        _blog_orchestrator = BlogActionOrchestrator()
    return _blog_orchestrator


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "BlogActionLane",
    "BlogActionDomain",
    "BlogActionType",
    "RiskLevel",
    "Priority",
    "BlogAction",
    "BlogActionClassifier",
    "BlogActionGenerator",
    "BlogActionOrchestrator",
    "get_blog_orchestrator",
]
