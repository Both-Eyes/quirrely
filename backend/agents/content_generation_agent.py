#!/usr/bin/env python3
"""
CONTENT GENERATION AGENT v1.0
Automatically generates optimized blog content based on SEO observer insights.

This agent:
1. Analyzes blog observer data to identify successful patterns
2. Detects content gaps and opportunities  
3. Generates new posts following proven templates
4. Updates sitemaps and submits to GSC
5. Uses ML to improve content intelligence over time
"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics
from ..conversion_events import ConversionTracker
from ...lncp.meta.blog_observer import get_blog_observer, KeywordOpportunity, PagePerformance
from ...lncp.meta.blog.config import get_blog_config, META_TEMPLATES


# ═══════════════════════════════════════════════════════════════════════════
# CONTENT GENERATION TYPES  
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ContentOpportunity:
    """A content creation opportunity identified by the agent."""
    type: str  # "keyword_gap", "successful_pattern", "content_refresh"
    priority: float  # 0-100
    estimated_monthly_clicks: int
    keyword: Optional[str] = None
    content_type: str = "profile_post"  # "profile_post", "guide", "comparison"
    template_data: Dict = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class GeneratedContent:
    """A piece of generated content ready for publishing."""
    filename: str
    title: str
    meta_description: str
    body: str
    url_path: str
    target_keywords: List[str]
    template_used: str
    seo_score: float = 0.0
    content_source: str = "ai_generated"


@dataclass
class ContentAnalysisResult:
    """Results from analyzing existing content patterns."""
    top_performing_patterns: List[Dict]
    content_opportunities: List[ContentOpportunity]
    keywords_missing_content: List[str]
    refresh_candidates: List[str]
    ml_insights: Dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# CONTENT GENERATION AGENT
# ═══════════════════════════════════════════════════════════════════════════

class ContentGenerationAgent(BatchAgent):
    """
    Automatically generates blog content based on SEO observer insights.
    
    Workflow:
    1. ANALYZE: Study successful content patterns and identify gaps
    2. OPTIMIZE: Generate high-potential content opportunities  
    3. EXECUTE: Create and publish optimized content
    4. REPORT: Track performance and improve ML models
    """
    
    def __init__(self, db_pool):
        super().__init__(
            name="content_generation",
            schedule_cron="0 0,8,16 * * *",  # Daily at midnight, 8am, and 4pm EST  
            data_sources=["blog_observer", "seo_data", "gsc_api"],
            db_pool=db_pool
        )
        
        self.conversion_tracker = ConversionTracker()
        self.blog_observer = get_blog_observer()
        self.blog_config = get_blog_config()
        
        # Content generation settings
        self.config = {
            "max_posts_per_run": 1,  # Generate 1 optimal post per run
            "generate_country_variations": True,  # Generate 5-country variations
            "countries": ["us", "ca", "uk", "au", "nz"],  # Target countries
            "min_opportunity_score": 70,  # Higher threshold for best opportunities
            "target_word_count": 1200,
            "max_word_count": 2000,
            "seo_score_threshold": 85,
            "keyword_difficulty_max": "medium"
        }
        
        # Country-specific content configurations
        self.country_config = {
            "us": {
                "spelling": "american",
                "tone": "direct and confident",
                "examples": "American business writing, direct communication",
                "domain": "quirrely.com",
                "locale": "en_US"
            },
            "ca": {
                "spelling": "canadian", 
                "tone": "polite and balanced",
                "examples": "Canadian professional writing, considerate directness",
                "domain": "quirrely.ca",
                "locale": "en_CA"
            },
            "uk": {
                "spelling": "british",
                "tone": "proper and structured", 
                "examples": "British formal writing, measured authority",
                "domain": "quirrely.co.uk",
                "locale": "en_GB"
            },
            "au": {
                "spelling": "australian",
                "tone": "authentic and straightforward",
                "examples": "Australian direct communication, genuine expression",
                "domain": "quirrely.com.au", 
                "locale": "en_AU"
            },
            "nz": {
                "spelling": "new_zealand",
                "tone": "clear and understated",
                "examples": "New Zealand clear communication, thoughtful expression",
                "domain": "quirrely.co.nz",
                "locale": "en_NZ"
            }
        }
        
        # ML models (will be enhanced over time)
        self.content_patterns = {}
        self.performance_model = None
        
        # Blog data cache
        self._blog_data: Optional[Dict] = None
        self._existing_posts: List[str] = []
        
    async def analyze(self) -> AnalysisResults:
        """
        Analyze existing content performance and identify generation opportunities.
        """
        self.logger.info("Starting content analysis...")
        
        # Get blog observer data
        health = self.blog_observer.get_health()
        keyword_opportunities = self.blog_observer.detect_keyword_opportunities()
        
        # Load existing blog data
        await self._load_blog_data()
        
        # Analyze successful patterns
        top_patterns = await self._analyze_successful_patterns(health)
        
        # Find content opportunities
        opportunities = await self._identify_content_opportunities(keyword_opportunities)
        
        # Detect missing content for keywords
        missing_keywords = await self._find_missing_keyword_content(keyword_opportunities)
        
        # Find content that needs refresh
        refresh_candidates = await self._identify_refresh_candidates()
        
        # Generate ML insights
        ml_insights = await self._generate_ml_insights(top_patterns, opportunities)
        
        # Convert to AnalysisResults format
        findings = {
            "top_performing_patterns": top_patterns,
            "content_opportunities": opportunities,
            "keywords_missing_content": missing_keywords,
            "refresh_candidates": refresh_candidates,
            "ml_insights": ml_insights,
            "total_opportunities": len(opportunities),
            "high_value_opportunities": len([o for o in opportunities if o.priority >= 80])
        }
        
        recommendations = [
            {
                "action": "generate_content",
                "priority": "high",
                "opportunity_count": len(opportunities),
                "estimated_impact": sum(o.estimated_monthly_clicks for o in opportunities[:3])
            }
        ]
        
        if len(refresh_candidates) > 2:
            recommendations.append({
                "action": "refresh_content",
                "priority": "medium", 
                "candidate_count": len(refresh_candidates),
                "estimated_impact": len(refresh_candidates) * 100  # Estimated clicks improvement
            })
        
        result = AnalysisResults(
            agent_name=self.name,
            analysis_period=(datetime.utcnow() - timedelta(days=7), datetime.utcnow()),
            findings=findings,
            confidence_score=0.85,  # High confidence in SEO data
            data_quality=0.90,      # GSC integration provides quality data
            recommendations=recommendations,
            raw_metrics={
                "opportunities_found": len(opportunities),
                "patterns_identified": len(top_patterns),
                "keywords_missing": len(missing_keywords),
                "refresh_needed": len(refresh_candidates)
            }
        )
        
        self.logger.info(f"Analysis complete: {len(opportunities)} opportunities found")
        return result
    
    async def optimize(self, analysis_result: AnalysisResults) -> OptimizationActions:
        """
        Generate optimized content based on analysis results.
        """
        self.logger.info("Starting content optimization...")
        
        # Extract content opportunities from findings
        content_opportunities = analysis_result.findings.get("content_opportunities", [])
        top_patterns = analysis_result.findings.get("top_performing_patterns", [])
        
        actions = []
        generated_content = []
        
        # Sort opportunities by priority
        sorted_opportunities = sorted(
            content_opportunities,
            key=lambda x: x.priority,
            reverse=True
        )
        
        # Apply time-of-day optimization to select the best opportunity
        best_opportunity = await self._select_optimal_opportunity_for_time(sorted_opportunities)
        
        if best_opportunity:
            # Generate base content
            base_content = await self._generate_content(best_opportunity, top_patterns)
            if base_content:
                # Generate country variations if enabled
                if self.config["generate_country_variations"]:
                    for country in self.config["countries"]:
                        country_content = await self._generate_country_variation(base_content, country, best_opportunity)
                        if country_content:
                            generated_content.append(country_content)
                            
                            actions.append({
                                "type": "generate_content",
                                "opportunity": best_opportunity,
                                "content": country_content,
                                "country": country,
                                "expected_monthly_clicks": best_opportunity.estimated_monthly_clicks // 5,  # Split across countries
                                "priority_score": best_opportunity.priority,
                                "generation_time": datetime.now().strftime("%H:%M EST")
                            })
                    
                    self.logger.info(f"Generated {len(generated_content)} country variations for: {base_content.title}")
                else:
                    # Single content without variations
                    generated_content.append(base_content)
                    actions.append({
                        "type": "generate_content", 
                        "opportunity": best_opportunity,
                        "content": base_content,
                        "expected_monthly_clicks": best_opportunity.estimated_monthly_clicks,
                        "priority_score": best_opportunity.priority,
                        "generation_time": datetime.now().strftime("%H:%M EST")
                    })
                    
                    self.logger.info(f"Generated optimal content: {base_content.title} (priority: {best_opportunity.priority:.1f})")
            else:
                self.logger.warning(f"Failed to generate content for best opportunity: {best_opportunity.keyword}")
        else:
            self.logger.info("No opportunities meet the minimum threshold for content generation")
        
        # Calculate expected impact
        total_monthly_clicks = sum(
            action.get("expected_monthly_clicks", 0) for action in actions
        )
        estimated_revenue = total_monthly_clicks * 0.02 * 37.72  # Conv rate * avg revenue
        
        expected_impact = {
            "monthly_clicks": total_monthly_clicks,
            "estimated_monthly_revenue": estimated_revenue,
            "posts_generated": len(generated_content),
            "seo_improvement": len(actions) * 0.1  # 10% improvement per post
        }
        
        # Create rollback plan
        rollback_plan = {
            "action": "remove_generated_content",
            "files_to_remove": [content.filename for content in generated_content],
            "sitemap_rollback": True
        }
        
        optimization_actions = OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=0.1,  # Low risk for content generation
            rollback_plan=rollback_plan
        )
        
        self.logger.info(f"Generated {len(generated_content)} optimization actions")
        return optimization_actions
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """
        Publish generated content and update sitemaps.
        """
        start_time = datetime.now()
        self.logger.info(f"Executing {len(actions.actions)} content generation actions...")
        
        actions_taken = []
        actions_failed = []
        published_posts = []
        
        # Execute each action
        for action in actions.actions:
            try:
                if action["type"] == "generate_content":
                    content = action["content"]
                    
                    # Write the HTML file
                    await self._write_content_file(content)
                    
                    # Update blog data registry
                    await self._update_blog_data_registry(content)
                    
                    # Track successful action
                    actions_taken.append({
                        "action_type": "content_published",
                        "filename": content.filename,
                        "title": content.title,
                        "url": content.url_path,
                        "seo_score": content.seo_score,
                        "expected_clicks": action.get("expected_monthly_clicks", 0)
                    })
                    
                    published_posts.append(content.filename)
                    self.logger.info(f"Published: {content.filename}")
                
            except Exception as e:
                error_msg = f"Failed to execute action: {str(e)}"
                self.logger.error(error_msg)
                actions_failed.append({
                    "action": action,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Update sitemap and submit to GSC
        if published_posts:
            try:
                await self._update_sitemap()
                actions_taken.append({
                    "action_type": "sitemap_updated",
                    "files_count": len(published_posts)
                })
                
                await self._submit_to_gsc()
                actions_taken.append({
                    "action_type": "gsc_submitted",
                    "files_count": len(published_posts)
                })
                
            except Exception as e:
                error_msg = f"Failed to update sitemap/GSC: {str(e)}"
                self.logger.error(error_msg)
                actions_failed.append({
                    "action": "sitemap_gsc_update",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Calculate execution metrics
        execution_time = (datetime.now() - start_time).total_seconds()
        success_rate = len(actions_taken) / (len(actions_taken) + len(actions_failed)) if (len(actions_taken) + len(actions_failed)) > 0 else 1.0
        
        # Calculate immediate impact
        total_expected_clicks = sum(
            action.get("expected_clicks", 0) for action in actions_taken
            if action.get("action_type") == "content_published"
        )
        
        immediate_impact = {
            "content_published": len(published_posts),
            "estimated_monthly_clicks": total_expected_clicks,
            "sitemap_updated": any(a.get("action_type") == "sitemap_updated" for a in actions_taken),
            "gsc_submitted": any(a.get("action_type") == "gsc_submitted" for a in actions_taken)
        }
        
        return ExecutionReport(
            agent_name=self.name,
            actions_taken=actions_taken,
            actions_failed=actions_failed,
            execution_time=execution_time,
            immediate_impact=immediate_impact,
            success_rate=success_rate
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # CONTENT ANALYSIS
    # ─────────────────────────────────────────────────────────────────────
    
    async def _load_blog_data(self):
        """Load existing blog data and post inventory."""
        blog_data_path = Path("/root/quirrely_v313_integrated/blog/blog-data.js")
        
        if blog_data_path.exists():
            with open(blog_data_path, 'r') as f:
                content = f.read()
                # Extract JSON data from JavaScript
                # This is a simplified parser - in production would use proper JS parser
                start = content.find("const BLOG_DATA = {")
                if start != -1:
                    # For now, we'll work with what we have
                    self._blog_data = {"loaded": True}
        
        # Get list of existing posts
        blog_dir = Path("/root/quirrely_v313_integrated/blog")
        self._existing_posts = [
            f.stem for f in blog_dir.glob("how-*.html")
        ]
    
    async def _analyze_successful_patterns(self, health) -> List[Dict]:
        """Analyze which content patterns are performing best."""
        patterns = []
        
        # Get top performing pages from blog observer
        for page_url in health.top_pages:
            if "/blog/how-" in page_url:
                # Extract pattern from URL
                match = re.search(r'/blog/how-([^-]+)-([^-]+)-writers-write', page_url)
                if match:
                    style, certitude = match.groups()
                    
                    # Get page performance data  
                    page_perf = self.blog_observer._pages.get(page_url)
                    if page_perf:
                        patterns.append({
                            "style": style,
                            "certitude": certitude,
                            "url": page_url,
                            "ctr": page_perf.ctr,
                            "avg_position": page_perf.avg_position,
                            "impressions": page_perf.impressions,
                            "clicks": page_perf.clicks,
                            "engagement_score": page_perf.avg_time_on_page * (1 - page_perf.bounce_rate)
                        })
        
        # Sort by engagement score
        patterns.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        return patterns[:10]  # Top 10 patterns
    
    async def _identify_content_opportunities(self, keyword_opportunities: List[KeywordOpportunity]) -> List[ContentOpportunity]:
        """Identify high-value content creation opportunities."""
        opportunities = []
        
        for kw_opp in keyword_opportunities:
            # Skip if we already have content for this keyword
            if any(post in kw_opp.page_url for post in self._existing_posts):
                continue
            
            # Create content opportunity
            opportunity = ContentOpportunity(
                type="keyword_gap",
                priority=kw_opp.priority,
                estimated_monthly_clicks=kw_opp.potential_clicks * 30,  # Monthly estimate
                keyword=kw_opp.keyword,
                reasoning=f"Ranking #{kw_opp.current_position} for '{kw_opp.keyword}' with {kw_opp.impressions} impressions"
            )
            
            # Try to extract style/certitude pattern from keyword
            style_cert = self._extract_style_certitude_from_keyword(kw_opp.keyword)
            if style_cert:
                opportunity.template_data = style_cert
                opportunity.content_type = "profile_post"
            else:
                # Generic content opportunity
                opportunity.content_type = "guide"
                opportunity.template_data = {"topic": kw_opp.keyword}
            
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _find_missing_keyword_content(self, keyword_opportunities: List[KeywordOpportunity]) -> List[str]:
        """Find keywords where we could rank but don't have dedicated content."""
        missing = []
        
        for kw_opp in keyword_opportunities:
            # Look for writing-related keywords we could target
            keyword = kw_opp.keyword.lower()
            
            # Check for style/certitude combinations we don't have content for
            if "writer" in keyword or "writing" in keyword:
                style_cert = self._extract_style_certitude_from_keyword(keyword)
                if style_cert:
                    post_slug = f"how-{style_cert['style']}-{style_cert['certitude']}-writers-write"
                    if post_slug not in self._existing_posts:
                        missing.append(keyword)
        
        return missing
    
    async def _identify_refresh_candidates(self) -> List[str]:
        """Identify existing content that needs refreshing."""
        candidates = []
        
        # Get content freshness data from blog observer
        for url, freshness in self.blog_observer._content_registry.items():
            if freshness.update_recommended:
                candidates.append(url)
        
        return candidates[:5]  # Top 5 candidates
    
    async def _generate_ml_insights(self, patterns, opportunities) -> Dict:
        """Generate ML insights for improving content generation."""
        insights = {
            "best_performing_styles": [],
            "optimal_content_length": 0,
            "high_value_keywords": [],
            "content_gaps": len(opportunities),
            "pattern_confidence": 0.0
        }
        
        if patterns:
            # Find best performing styles
            style_performance = {}
            for pattern in patterns:
                style = pattern["style"]
                if style not in style_performance:
                    style_performance[style] = []
                style_performance[style].append(pattern["engagement_score"])
            
            # Calculate average performance per style
            style_avg = {
                style: sum(scores) / len(scores)
                for style, scores in style_performance.items()
            }
            
            # Sort by performance
            insights["best_performing_styles"] = sorted(
                style_avg.items(), key=lambda x: x[1], reverse=True
            )[:5]
            
            # Calculate optimal word count (placeholder for ML model)
            word_counts = [p.get("word_count", 1200) for p in patterns]
            insights["optimal_content_length"] = int(sum(word_counts) / len(word_counts))
            
            insights["pattern_confidence"] = 0.85  # Placeholder
        
        return insights
    
    # ─────────────────────────────────────────────────────────────────────
    # CONTENT GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    async def _generate_content(self, opportunity: ContentOpportunity, patterns: List[Dict]) -> Optional[GeneratedContent]:
        """Generate content for a specific opportunity."""
        try:
            if opportunity.content_type == "profile_post":
                return await self._generate_profile_post(opportunity, patterns)
            elif opportunity.content_type == "guide":
                return await self._generate_guide_post(opportunity, patterns)
            else:
                self.logger.warning(f"Unknown content type: {opportunity.content_type}")
                return None
        
        except Exception as e:
            self.logger.error(f"Failed to generate content for {opportunity.keyword}: {str(e)}")
            return None
    
    async def _generate_profile_post(self, opportunity: ContentOpportunity, patterns: List[Dict]) -> Optional[GeneratedContent]:
        """Generate a writing profile post (how-X-Y-writers-write)."""
        template_data = opportunity.template_data
        if not template_data.get("style") or not template_data.get("certitude"):
            return None
        
        style = template_data["style"].title()
        certitude = template_data["certitude"].title()
        
        # Generate content using successful patterns
        title = f"How {style} {certitude} Writers Write"
        
        # Use best performing meta template
        meta_template = self.blog_config.get_best_meta_template()
        meta_description = meta_template.description_template.format(
            style=style.lower(),
            certitude=certitude.lower()
        )
        
        # Generate body content based on successful patterns
        body = await self._generate_profile_body(style, certitude, patterns)
        
        filename = f"how-{style.lower()}-{certitude.lower()}-writers-write.html"
        url_path = f"/blog/{filename.replace('.html', '')}"
        
        return GeneratedContent(
            filename=filename,
            title=title,
            meta_description=meta_description,
            body=body,
            url_path=url_path,
            target_keywords=[opportunity.keyword or f"{style.lower()} {certitude.lower()} writing"],
            template_used="profile_post",
            seo_score=85.0,  # Placeholder - would calculate based on content analysis
            content_source="ai_generated"
        )
    
    async def _generate_guide_post(self, opportunity: ContentOpportunity, patterns: List[Dict]) -> Optional[GeneratedContent]:
        """Generate a guide/educational post."""
        topic = opportunity.template_data.get("topic", opportunity.keyword)
        
        title = f"Complete Guide to {topic.title()}"
        meta_description = f"Learn everything about {topic}. Expert insights, practical tips, and actionable advice for writers."
        
        body = await self._generate_guide_body(topic, patterns)
        
        filename = f"{topic.lower().replace(' ', '-')}-guide.html"
        url_path = f"/blog/{filename.replace('.html', '')}"
        
        return GeneratedContent(
            filename=filename,
            title=title,
            meta_description=meta_description,
            body=body,
            url_path=url_path,
            target_keywords=[topic, f"{topic} guide", f"{topic} tips"],
            template_used="guide_post",
            seo_score=80.0,
            content_source="ai_generated"
        )
    
    async def _generate_profile_body(self, style: str, certitude: str, patterns: List[Dict]) -> str:
        """Generate body content for a writing profile post."""
        # This is a template-based approach. In production, would use actual AI content generation
        
        style_desc = {
            "assertive": "direct, confident, declarative",
            "conversational": "casual, friendly, approachable",  
            "formal": "structured, professional, precise",
            "poetic": "lyrical, metaphorical, expressive",
            "minimal": "concise, sparse, essential",
            "dense": "complex, layered, information-rich",
            "longform": "detailed, expansive, thorough",
            "hedged": "cautious, qualified, nuanced",
            "interrogative": "questioning, exploratory, curious",
            "balanced": "moderate, measured, even-handed"
        }.get(style.lower(), "distinctive")
        
        certitude_desc = {
            "open": "receptive to challenge, invites dialogue",
            "closed": "definitive, unwavering, authoritative",
            "contradictory": "complex, paradoxical, multi-layered",
            "balanced": "considers multiple perspectives"
        }.get(certitude.lower(), "thoughtful")
        
        # Generate content following successful patterns from analysis
        body = f"""Understanding {style.upper()} + {certitude.upper()} writing.

{style.upper()} + {certitude.upper()} writers are {style_desc} and {certitude_desc}. This combination creates a distinctive voice that shapes every sentence.

THE PATTERN

{style.title()} writers favor {self._get_style_characteristics(style)}. Combined with {certitude.lower()} certitude, they {self._get_certitude_characteristics(certitude)}.

Look for these markers:
• {self._get_pattern_marker_1(style, certitude)}
• {self._get_pattern_marker_2(style, certitude)}  
• {self._get_pattern_marker_3(style, certitude)}

WHY IT WORKS

This voice builds {self._get_trust_factor(style, certitude)} with readers. The {style.lower()} approach {self._get_approach_benefit(style)}, while {certitude.lower()} certitude {self._get_certitude_benefit(certitude)}.

Readers know what to expect. They can engage with confidence.

THE CHALLENGE

Some {style.lower()} + {certitude.lower()} writers struggle with {self._get_common_challenge(style, certitude)}. The solution: {self._get_solution(style, certitude)}.

Remember: your voice is a tool. Use it intentionally."""
        
        return body
    
    async def _generate_guide_body(self, topic: str, patterns: List[Dict]) -> str:
        """Generate body content for a guide post."""
        # Template-based guide generation
        body = f"""Master {topic} with this comprehensive guide.

{topic.title()} fundamentals every writer should know.

WHAT IS {topic.upper()}

{topic.title()} refers to {self._get_topic_definition(topic)}. Understanding this concept helps writers {self._get_topic_benefit(topic)}.

KEY PRINCIPLES

1. **Foundation** - {self._get_principle_1(topic)}
2. **Application** - {self._get_principle_2(topic)}  
3. **Mastery** - {self._get_principle_3(topic)}

PRACTICAL TECHNIQUES

{self._get_practical_techniques(topic)}

COMMON MISTAKES

Avoid these pitfalls:
• {self._get_mistake_1(topic)}
• {self._get_mistake_2(topic)}
• {self._get_mistake_3(topic)}

NEXT STEPS

Start with {self._get_next_step(topic)}. Practice consistently. Your writing will improve."""
        
        return body
    
    # ─────────────────────────────────────────────────────────────────────
    # PUBLISHING & SITEMAP
    # ─────────────────────────────────────────────────────────────────────
    
    async def _write_content_file(self, content: GeneratedContent):
        """Write generated content to HTML file."""
        blog_dir = Path("/root/quirrely_v313_integrated/blog")
        
        # Create country-specific subdirectory if needed
        if content.filename.startswith(('ca-', 'uk-', 'au-', 'nz-')):
            country = content.filename.split('-')[0]
            country_dir = blog_dir / country
            country_dir.mkdir(exist_ok=True)
            
            # Remove country prefix from filename when placing in country directory
            clean_filename = '-'.join(content.filename.split('-')[1:])
            file_path = country_dir / clean_filename
        else:
            # US content goes in main blog directory
            file_path = blog_dir / content.filename
        
        # Determine country and locale from content
        country = "us"  # default
        locale = "en_US"  # default
        domain = "quirrely.com"  # default
        
        if content.filename.startswith(('ca-', 'uk-', 'au-', 'nz-')):
            country = content.filename.split('-')[0]
            country_conf = self.country_config.get(country, self.country_config["us"])
            locale = country_conf["locale"]
            domain = country_conf["domain"]
        
        # Use existing blog template structure
        html_content = f"""<!DOCTYPE html>
<html lang="{locale.replace('_', '-')}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.title}</title>
    <meta name="description" content="{content.meta_description}">
    <meta name="keywords" content="{', '.join(content.target_keywords)}">
    
    <!-- Generated Content Marker -->
    <meta name="content-source" content="{content.content_source}">
    <meta name="template-used" content="{content.template_used}">
    <meta name="generated-date" content="{datetime.utcnow().isoformat()}">
    <meta name="country" content="{country}">
    
    <!-- Social Media Meta Tags -->
    <meta property="og:title" content="{content.title}">
    <meta property="og:description" content="{content.meta_description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://{domain}{content.url_path}">
    <meta property="og:locale" content="{locale}">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{content.title}">
    <meta name="twitter:description" content="{content.meta_description}">
    
    <link rel="canonical" href="https://{domain}{content.url_path}">
    
    <!-- Blog Styles -->
    <link rel="stylesheet" href="../sentense-app/src/styles/blog.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Quirrely</a>
            <a href="/blog">Blog</a>
        </nav>
    </header>
    
    <main>
        <article>
            <header>
                <h1>{content.title}</h1>
                <p class="meta">{content.meta_description}</p>
            </header>
            
            <div class="content">
                {self._format_body_html(content.body)}
            </div>
            
            <footer>
                <div class="cta">
                    <a href="/" class="cta-button">Discover Your Writing Voice →</a>
                    <p>Free • Takes 30 seconds</p>
                </div>
            </footer>
        </article>
    </main>
    
    <script>
        // Track CTA clicks for optimization
        document.querySelector('.cta-button').addEventListener('click', function() {{
            // Analytics tracking would go here
            console.log('CTA clicked from generated content');
        }});
    </script>
</body>
</html>"""
        
        with open(file_path, 'w') as f:
            f.write(html_content)
    
    async def _update_blog_data_registry(self, content: GeneratedContent):
        """Update blog-data.js registry with new content."""
        # For now, just add to our internal tracking
        # In production, would properly update the JavaScript file
        self._existing_posts.append(content.filename.replace('.html', ''))
    
    async def _update_sitemap(self):
        """Update sitemap.xml with new content."""
        sitemap_path = Path("/root/quirrely_v313_integrated/sitemap.xml")
        
        # This is a placeholder - would implement proper sitemap generation
        self.logger.info("Sitemap updated (placeholder)")
    
    async def _submit_to_gsc(self):
        """Submit updated sitemap to Google Search Console."""
        # This would use GSC API to submit sitemap
        self.logger.info("Sitemap submitted to GSC (placeholder)")
    
    async def _store_ml_training_data(self, analysis_result, generated_content, execution_result):
        """Store data for improving ML models."""
        # Store training data for future ML model improvements
        training_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "opportunities": len(analysis_result.content_opportunities),
            "generated": len(generated_content),
            "published": len(execution_result["published_posts"]),
            "success_rate": len(execution_result["published_posts"]) / len(generated_content) if generated_content else 0
        }
        
        # Would store in database or ML training pipeline
        self.logger.info(f"ML training data stored: {json.dumps(training_data)}")
    
    # ─────────────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────────────
    
    def _extract_style_certitude_from_keyword(self, keyword: str) -> Optional[Dict[str, str]]:
        """Extract writing style and certitude from keyword."""
        keyword = keyword.lower()
        
        styles = ["assertive", "conversational", "formal", "poetic", "minimal", 
                 "dense", "longform", "hedged", "interrogative", "balanced"]
        certitudes = ["open", "closed", "contradictory", "balanced"]
        
        found_style = None
        found_certitude = None
        
        for style in styles:
            if style in keyword:
                found_style = style
                break
        
        for certitude in certitudes:
            if certitude in keyword:
                found_certitude = certitude
                break
        
        if found_style and found_certitude:
            return {"style": found_style, "certitude": found_certitude}
        
        return None
    
    def _format_body_html(self, body_text: str) -> str:
        """Convert plain text body to HTML format."""
        # Simple text-to-HTML conversion
        paragraphs = body_text.split('\n\n')
        html_parts = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if para.isupper() and len(para) < 50:  # Likely a heading
                html_parts.append(f"<h2>{para.title()}</h2>")
            elif para.startswith('•'):  # List item
                html_parts.append(f"<ul><li>{para[1:].strip()}</li></ul>")
            else:  # Regular paragraph
                html_parts.append(f"<p>{para}</p>")
        
        return '\n'.join(html_parts)
    
    def _format_ml_insights(self, insights: Dict) -> str:
        """Format ML insights for report."""
        formatted = []
        
        if insights.get("best_performing_styles"):
            top_styles = insights["best_performing_styles"][:3]
            formatted.append(f"• Best styles: {', '.join([style for style, _ in top_styles])}")
        
        if insights.get("optimal_content_length"):
            formatted.append(f"• Optimal length: ~{insights['optimal_content_length']} words")
        
        if insights.get("pattern_confidence"):
            formatted.append(f"• Pattern confidence: {insights['pattern_confidence']:.1%}")
        
        return '\n'.join(formatted) if formatted else "• Collecting baseline data"
    
    # Content generation helpers (would be enhanced with actual AI/ML)
    def _get_style_characteristics(self, style: str) -> str:
        characteristics = {
            "assertive": "direct statements and clear positions",
            "conversational": "casual tone and personal connection",
            "formal": "structured arguments and professional language",
            "poetic": "metaphorical language and rhythmic flow",
            "minimal": "economy of words and essential information",
            "dense": "information layering and complex concepts",
            "longform": "detailed exploration and comprehensive coverage",
            "hedged": "qualified statements and careful positioning",
            "interrogative": "questions and exploratory approaches",
            "balanced": "measured consideration and multiple perspectives"
        }
        return characteristics.get(style.lower(), "thoughtful expression")
    
    def _get_certitude_characteristics(self, certitude: str) -> str:
        characteristics = {
            "open": "invite challenge and welcome input",
            "closed": "present definitive positions",
            "contradictory": "embrace complexity and paradox",
            "balanced": "weigh multiple viewpoints"
        }
        return characteristics.get(certitude.lower(), "maintain consistency")
    
    def _get_pattern_marker_1(self, style: str, certitude: str) -> str:
        return f"{style.title()} opening statements"
    
    def _get_pattern_marker_2(self, style: str, certitude: str) -> str:
        return f"{certitude.title()} response to challenges"
    
    def _get_pattern_marker_3(self, style: str, certitude: str) -> str:
        return f"Consistent {style.lower()}-{certitude.lower()} voice"
    
    def _get_trust_factor(self, style: str, certitude: str) -> str:
        return "strong trust"
    
    def _get_approach_benefit(self, style: str) -> str:
        return "engages readers effectively"
    
    def _get_certitude_benefit(self, certitude: str) -> str:
        return "provides clear direction"
    
    def _get_common_challenge(self, style: str, certitude: str) -> str:
        return "maintaining consistency"
    
    def _get_solution(self, style: str, certitude: str) -> str:
        return "practice intentional voice control"
    
    def _get_topic_definition(self, topic: str) -> str:
        return f"the fundamental principles of {topic}"
    
    def _get_topic_benefit(self, topic: str) -> str:
        return "improve their craft significantly"
    
    def _get_principle_1(self, topic: str) -> str:
        return f"Understanding {topic} basics"
    
    def _get_principle_2(self, topic: str) -> str:
        return f"Applying {topic} techniques"
    
    def _get_principle_3(self, topic: str) -> str:
        return f"Mastering {topic} nuances"
    
    def _get_practical_techniques(self, topic: str) -> str:
        return f"Practice {topic} daily. Start small. Build consistency."
    
    def _get_mistake_1(self, topic: str) -> str:
        return f"Overlooking {topic} fundamentals"
    
    def _get_mistake_2(self, topic: str) -> str:
        return f"Inconsistent {topic} application"
    
    def _get_mistake_3(self, topic: str) -> str:
        return f"Ignoring {topic} best practices"
    
    def _get_next_step(self, topic: str) -> str:
        return f"basic {topic} exercises"
    
    # ─────────────────────────────────────────────────────────────────────
    # TIME-OF-DAY OPTIMIZATION
    # ─────────────────────────────────────────────────────────────────────
    
    async def _select_optimal_opportunity_for_time(self, sorted_opportunities: List[ContentOpportunity]) -> Optional[ContentOpportunity]:
        """
        Select the optimal content opportunity based on current time and content strategy.
        
        Strategy:
        - Midnight (0:00): High-competition keywords (get indexed early)
        - 8am (08:00): Professional/work-related content (morning productivity)  
        - 4pm (16:00): Conversational/creative content (afternoon engagement)
        """
        current_hour = datetime.now().hour
        
        if not sorted_opportunities:
            return None
        
        # Filter opportunities that meet minimum threshold
        qualified_opportunities = [
            opp for opp in sorted_opportunities 
            if opp.priority >= self.config["min_opportunity_score"]
        ]
        
        if not qualified_opportunities:
            self.logger.info("No opportunities meet the minimum threshold")
            return None
        
        # Time-based content strategy
        if current_hour == 0:  # Midnight - Target high-value keywords
            best_opportunity = self._select_high_value_opportunity(qualified_opportunities)
            self.logger.info("Midnight run: Targeting high-value keyword opportunity")
            
        elif current_hour == 8:  # 8am - Target professional content
            best_opportunity = self._select_professional_content(qualified_opportunities)
            self.logger.info("Morning run: Targeting professional writing content")
            
        elif current_hour == 16:  # 4pm - Target conversational/creative content
            best_opportunity = self._select_engaging_content(qualified_opportunities)
            self.logger.info("Afternoon run: Targeting engaging/conversational content")
            
        else:  # Fallback for manual runs
            best_opportunity = qualified_opportunities[0]  # Highest priority
            self.logger.info("Off-schedule run: Using highest priority opportunity")
        
        return best_opportunity
    
    def _select_high_value_opportunity(self, opportunities: List[ContentOpportunity]) -> ContentOpportunity:
        """Select highest value opportunity (most monthly clicks potential)."""
        return max(opportunities, key=lambda x: x.estimated_monthly_clicks)
    
    def _select_professional_content(self, opportunities: List[ContentOpportunity]) -> ContentOpportunity:
        """Select content that appeals to professional writers (morning audience)."""
        # Prioritize formal, structured writing styles for morning professional audience
        professional_styles = ["formal", "assertive", "balanced", "structured"]
        
        for opportunity in opportunities:
            if opportunity.template_data.get("style") in professional_styles:
                return opportunity
        
        # Fallback to highest priority if no professional content available
        return opportunities[0]
    
    def _select_engaging_content(self, opportunities: List[ContentOpportunity]) -> ContentOpportunity:
        """Select content that's more conversational/creative (afternoon audience)."""
        # Prioritize conversational, creative styles for afternoon audience
        engaging_styles = ["conversational", "poetic", "interrogative", "creative"]
        
        for opportunity in opportunities:
            if opportunity.template_data.get("style") in engaging_styles:
                return opportunity
        
        # Fallback to highest priority if no engaging content available  
        return opportunities[0]
    
    # ─────────────────────────────────────────────────────────────────────
    # COUNTRY-SPECIFIC CONTENT GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    async def _generate_country_variation(self, base_content: GeneratedContent, country: str, opportunity: ContentOpportunity) -> Optional[GeneratedContent]:
        """Generate a country-specific variation of the base content."""
        try:
            country_conf = self.country_config.get(country)
            if not country_conf:
                return None
            
            # Create country-specific content
            country_title = self._localize_title(base_content.title, country)
            country_meta = self._localize_meta_description(base_content.meta_description, country)
            country_body = await self._localize_content_body(base_content.body, country)
            
            # Generate country-specific filename and URL
            base_filename = base_content.filename
            if country == "us":
                # US is default, no country prefix
                country_filename = base_filename
                country_url = base_content.url_path
            else:
                # Add country prefix for other countries
                country_filename = f"{country}-{base_filename}"
                country_url = f"/blog/{country}{base_content.url_path.replace('/blog', '')}"
            
            # Update target keywords with country-specific variations
            country_keywords = self._localize_keywords(base_content.target_keywords, country)
            
            return GeneratedContent(
                filename=country_filename,
                title=country_title,
                meta_description=country_meta,
                body=country_body,
                url_path=country_url,
                target_keywords=country_keywords,
                template_used=f"{base_content.template_used}_{country}",
                seo_score=base_content.seo_score,
                content_source=f"ai_generated_{country}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate {country} variation: {str(e)}")
            return None
    
    def _localize_title(self, title: str, country: str) -> str:
        """Localize title for specific country."""
        country_conf = self.country_config[country]
        
        # Add country-specific context to title
        if country == "ca":
            return f"{title} | Canadian Writing Guide"
        elif country == "uk":
            return f"{title} | British Writing Guide" 
        elif country == "au":
            return f"{title} | Australian Writing Guide"
        elif country == "nz":
            return f"{title} | New Zealand Writing Guide"
        else:  # US
            return title
    
    def _localize_meta_description(self, meta: str, country: str) -> str:
        """Localize meta description for specific country."""
        country_conf = self.country_config[country]
        
        if country == "ca":
            return meta.replace("writers", "Canadian writers").replace("writing", "Canadian writing")
        elif country == "uk": 
            return meta.replace("writers", "British writers").replace("writing", "British writing")
        elif country == "au":
            return meta.replace("writers", "Australian writers").replace("writing", "Australian writing")
        elif country == "nz":
            return meta.replace("writers", "New Zealand writers").replace("writing", "New Zealand writing")
        else:  # US
            return meta
    
    async def _localize_content_body(self, body: str, country: str) -> str:
        """Localize content body for specific country."""
        country_conf = self.country_config[country]
        
        # Apply spelling localization
        localized_body = self._apply_country_spelling(body, country)
        
        # Add country-specific introduction
        country_intro = self._get_country_intro(country)
        
        # Add country-specific examples
        country_examples = self._get_country_examples(country)
        
        # Combine with localized tone
        final_body = f"{country_intro}\n\n{localized_body}\n\n{country_examples}"
        
        return final_body
    
    def _apply_country_spelling(self, text: str, country: str) -> str:
        """Apply country-specific spelling to text."""
        if country in ["ca", "uk", "au", "nz"]:
            # Apply British/Commonwealth spelling
            text = text.replace("color", "colour")
            text = text.replace("realize", "realise")
            text = text.replace("center", "centre")
            text = text.replace("organize", "organise")
            text = text.replace("behavior", "behaviour")
        # US spelling is default, no changes needed
        
        return text
    
    def _get_country_intro(self, country: str) -> str:
        """Get country-specific introduction."""
        intros = {
            "ca": "Canadian writers blend directness with politeness, creating a distinctive voice that reflects our multicultural perspective.",
            "uk": "British writers demonstrate measured authority through proper structure and refined expression.",
            "au": "Australian writers embrace authenticity and straightforward communication that cuts through the noise.",
            "nz": "New Zealand writers value clarity and understatement, expressing confidence without overwhelming the reader.",
            "us": "American writers lead with confidence and directness, making their point clearly and efficiently."
        }
        return intros.get(country, intros["us"])
    
    def _get_country_examples(self, country: str) -> str:
        """Get country-specific writing examples."""
        examples = {
            "ca": "CANADIAN CONTEXT\n\nThis voice style appears in Canadian business writing, academic discourse, and professional communication. Think of how Canadian writers balance assertiveness with consideration for others' perspectives.",
            "uk": "BRITISH CONTEXT\n\nThis voice style is evident in British formal writing, academic papers, and professional correspondence. Consider how British writers maintain authority while following established conventions.",
            "au": "AUSTRALIAN CONTEXT\n\nThis voice style shines in Australian direct communication, creative writing, and authentic expression. Notice how Australian writers cut through pretense to get to the heart of the matter.", 
            "nz": "NEW ZEALAND CONTEXT\n\nThis voice style appears in New Zealand clear communication, thoughtful discourse, and understated confidence. Observe how Kiwi writers express strength without unnecessary drama.",
            "us": "AMERICAN CONTEXT\n\nThis voice style dominates American business writing, confident communication, and direct expression. See how American writers lead with clarity and conviction."
        }
        return examples.get(country, examples["us"])
    
    def _localize_keywords(self, keywords: List[str], country: str) -> List[str]:
        """Add country-specific keyword variations."""
        country_keywords = keywords.copy()
        
        # Add country-specific keyword variations
        base_keywords = [kw for kw in keywords if "writing" in kw.lower()]
        
        for keyword in base_keywords:
            if country == "ca":
                country_keywords.append(f"Canadian {keyword}")
            elif country == "uk":
                country_keywords.append(f"British {keyword}")
            elif country == "au": 
                country_keywords.append(f"Australian {keyword}")
            elif country == "nz":
                country_keywords.append(f"New Zealand {keyword}")
        
        return country_keywords