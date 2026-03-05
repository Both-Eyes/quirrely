#!/usr/bin/env python3
"""
CONTENT OPTIMIZATION AGENT
Optimizes writing insights and suggestions based on user engagement and effectiveness.

Schedule: Weekly on Saturdays at 2 AM EST
Purpose: Improve content quality and personalization for better user engagement
Expected Impact: 40% increase in insight engagement, improved writing outcomes
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import asyncpg
from dataclasses import dataclass

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class ContentInsight:
    """Analysis of content insight performance."""
    insight_type: str
    insight_category: str
    total_shown: int
    total_engaged: int
    engagement_rate: float
    avg_rating: float
    improvement_score: float  # How much user writing improved after seeing this insight
    effectiveness_score: float  # Combined engagement + improvement
    user_feedback: List[str]
    recommendation: str

@dataclass
class ContentPerformance:
    """Overall content performance metrics."""
    total_insights_shown: int
    total_engagements: int
    overall_engagement_rate: float
    avg_improvement_score: float
    top_performing_insights: List[str]
    underperforming_insights: List[str]
    content_freshness_score: float
    personalization_effectiveness: float

class ContentOptimizationAgent(BatchAgent):
    """Agent for optimizing writing insights and content recommendations."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="content_optimizer",
            schedule_cron="0 2 * * 6",  # 2 AM every Saturday
            data_sources=["content_insights", "user_interactions", "lncp_analysis_results", "user_feedback"],
            db_pool=db_pool,
            config={
                "analysis_period_days": 14,
                "min_insight_impressions": 50,
                "engagement_threshold": 0.15,  # 15% minimum engagement rate
                "improvement_threshold": 0.1,   # 10% minimum improvement score
                "freshness_threshold_days": 30,  # Content older than 30 days needs refresh
                "personalization_segments": 5   # Number of user segments for personalization
            }
        )
    
    async def analyze(self) -> AnalysisResults:
        """Analyze content performance and identify optimization opportunities."""
        
        logger.info("Starting content optimization analysis")
        
        # Define analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config["analysis_period_days"])
        
        # Analyze content insight performance
        insight_performance = await self._analyze_content_insights(start_date, end_date)
        
        # Analyze overall content performance
        overall_performance = await self._analyze_overall_performance(insight_performance, start_date, end_date)
        
        # Analyze personalization effectiveness
        personalization_analysis = await self._analyze_personalization_effectiveness(start_date, end_date)
        
        # Identify content gaps and opportunities
        content_opportunities = await self._identify_content_opportunities(
            insight_performance, personalization_analysis
        )
        
        # Analyze content freshness and relevance
        freshness_analysis = await self._analyze_content_freshness(start_date, end_date)
        
        confidence_score = self._calculate_content_analysis_confidence(overall_performance, insight_performance)
        
        findings = {
            "overall_performance": overall_performance.__dict__,
            "insight_performance": [insight.__dict__ for insight in insight_performance],
            "personalization_analysis": personalization_analysis,
            "content_opportunities": content_opportunities,
            "freshness_analysis": freshness_analysis,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        recommendations = self._generate_content_recommendations(
            overall_performance, content_opportunities, freshness_analysis
        )
        
        return AnalysisResults(
            agent_name=self.name,
            analysis_period=(start_date, end_date),
            findings=findings,
            confidence_score=confidence_score,
            data_quality=self._assess_content_data_quality(overall_performance, insight_performance),
            recommendations=recommendations,
            raw_metrics={
                "total_insights_analyzed": len(insight_performance),
                "overall_engagement_rate": overall_performance.overall_engagement_rate,
                "avg_improvement_score": overall_performance.avg_improvement_score,
                "personalization_effectiveness": overall_performance.personalization_effectiveness,
                "content_freshness_score": overall_performance.content_freshness_score
            }
        )
    
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions for content improvement."""
        
        logger.info("Generating content optimization actions")
        
        insight_performance = results.findings["insight_performance"]
        content_opportunities = results.findings["content_opportunities"]
        freshness_analysis = results.findings["freshness_analysis"]
        personalization_analysis = results.findings["personalization_analysis"]
        
        actions = []
        expected_impact = {}
        
        # Generate actions for underperforming content
        underperforming_insights = [
            insight for insight in insight_performance 
            if insight["engagement_rate"] < self.config["engagement_threshold"]
        ]
        
        for insight in underperforming_insights[:5]:  # Limit to top 5 priorities
            action = await self._create_content_improvement_action(insight)
            actions.append(action)
            expected_impact[f"improve_{insight['insight_type']}"] = 0.3  # 30% engagement improvement
        
        # Generate actions for content gaps
        for opportunity in content_opportunities:
            if opportunity["type"] == "content_gap":
                action = await self._create_content_creation_action(opportunity)
                actions.append(action)
                expected_impact[f"create_{opportunity['category']}"] = opportunity["expected_engagement"]
        
        # Generate personalization improvement actions
        if personalization_analysis.get("effectiveness_score", 0) < 0.6:
            action = await self._create_personalization_improvement_action(personalization_analysis)
            actions.append(action)
            expected_impact["personalization_improvement"] = 0.25
        
        # Generate content freshness actions
        stale_content = freshness_analysis.get("stale_content_count", 0)
        if stale_content > 0:
            action = await self._create_content_refresh_action(freshness_analysis)
            actions.append(action)
            expected_impact["content_refresh"] = stale_content * 0.05
        
        # Generate high-performing content amplification actions
        top_performers = [
            insight for insight in insight_performance 
            if insight["effectiveness_score"] > 0.8
        ]
        
        if top_performers:
            action = await self._create_content_amplification_action(top_performers)
            actions.append(action)
            expected_impact["amplify_top_content"] = 0.2
        
        risk_assessment = self._assess_content_optimization_risk(actions, results)
        rollback_plan = await self._create_content_rollback_plan(actions)
        
        return OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute content optimization actions."""
        
        logger.info(f"Executing {len(actions.actions)} content optimization actions")
        
        actions_taken = []
        actions_failed = []
        immediate_impact = {}
        
        for action in actions.actions:
            try:
                if action["type"] == "improve_content":
                    result = await self._execute_content_improvement(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"content_improved_{action['insight_type']}"] = 1.0
                    
                elif action["type"] == "create_content":
                    result = await self._execute_content_creation(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"content_created_{action['category']}"] = 1.0
                    
                elif action["type"] == "improve_personalization":
                    result = await self._execute_personalization_improvement(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["personalization_improved"] = 1.0
                    
                elif action["type"] == "refresh_content":
                    result = await self._execute_content_refresh(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["content_refreshed"] = len(action.get("stale_items", []))
                    
                elif action["type"] == "amplify_content":
                    result = await self._execute_content_amplification(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["top_content_amplified"] = len(action.get("top_performers", []))
                
            except Exception as e:
                logger.error(f"Content optimization action failed: {action['type']} - {str(e)}")
                actions_failed.append({"action": action, "error": str(e)})
        
        success_rate = len(actions_taken) / len(actions.actions) if actions.actions else 1.0
        execution_time = 0.0  # Would be measured in real execution
        
        return ExecutionReport(
            agent_name=self.name,
            actions_taken=actions_taken,
            actions_failed=actions_failed,
            execution_time=execution_time,
            immediate_impact=immediate_impact,
            success_rate=success_rate
        )
    
    async def _analyze_content_insights(self, start_date: datetime, end_date: datetime) -> List[ContentInsight]:
        """Analyze performance of individual content insights."""
        
        # Get content insights with engagement data
        insights_data = await self.db.fetch("""
            SELECT 
                ci.insight_type,
                ci.insight_category,
                COUNT(*) as total_shown,
                COUNT(*) FILTER (WHERE ui.interaction_type = 'engaged') as total_engaged,
                AVG(ui.rating) FILTER (WHERE ui.rating IS NOT NULL) as avg_rating,
                ARRAY_AGG(ui.feedback) FILTER (WHERE ui.feedback IS NOT NULL) as user_feedback
            FROM content_insights ci
            LEFT JOIN user_interactions ui ON ci.id = ui.content_insight_id
            WHERE ci.created_at BETWEEN $1 AND $2
            GROUP BY ci.insight_type, ci.insight_category
            HAVING COUNT(*) >= $3
        """, start_date, end_date, self.config["min_insight_impressions"])
        
        content_insights = []
        
        for insight_data in insights_data:
            insight_type = insight_data["insight_type"]
            insight_category = insight_data["insight_category"]
            total_shown = insight_data["total_shown"]
            total_engaged = insight_data["total_engaged"] or 0
            
            engagement_rate = total_engaged / total_shown if total_shown > 0 else 0
            avg_rating = float(insight_data["avg_rating"]) if insight_data["avg_rating"] else 0
            
            # Calculate improvement score based on user writing progress
            improvement_score = await self._calculate_improvement_score(
                insight_type, start_date, end_date
            )
            
            # Calculate overall effectiveness score
            effectiveness_score = self._calculate_effectiveness_score(
                engagement_rate, avg_rating, improvement_score
            )
            
            # Generate recommendation
            recommendation = self._generate_insight_recommendation(
                engagement_rate, improvement_score, effectiveness_score
            )
            
            # Clean up user feedback
            feedback = insight_data["user_feedback"] or []
            clean_feedback = [f for f in feedback if f and f.strip()][:10]  # Top 10 feedback items
            
            content_insights.append(ContentInsight(
                insight_type=insight_type,
                insight_category=insight_category,
                total_shown=total_shown,
                total_engaged=total_engaged,
                engagement_rate=engagement_rate,
                avg_rating=avg_rating,
                improvement_score=improvement_score,
                effectiveness_score=effectiveness_score,
                user_feedback=clean_feedback,
                recommendation=recommendation
            ))
        
        return content_insights
    
    async def _calculate_improvement_score(self, insight_type: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate how much user writing improved after seeing specific insights."""
        
        # Get users who saw this insight type
        users_with_insight = await self.db.fetch("""
            SELECT DISTINCT ui.user_id, ui.created_at as insight_date
            FROM user_interactions ui
            JOIN content_insights ci ON ui.content_insight_id = ci.id
            WHERE ci.insight_type = $1 
                AND ui.created_at BETWEEN $2 AND $3
                AND ui.interaction_type = 'engaged'
        """, insight_type, start_date, end_date)
        
        if not users_with_insight:
            return 0.0
        
        improvement_scores = []
        
        for user_insight in users_with_insight:
            user_id = user_insight["user_id"]
            insight_date = user_insight["insight_date"]
            
            # Get LNCP scores before and after insight
            before_score = await self._get_average_lncp_score(
                user_id, insight_date - timedelta(days=7), insight_date
            )
            after_score = await self._get_average_lncp_score(
                user_id, insight_date, insight_date + timedelta(days=7)
            )
            
            if before_score > 0 and after_score > 0:
                improvement = (after_score - before_score) / before_score
                improvement_scores.append(improvement)
        
        return statistics.mean(improvement_scores) if improvement_scores else 0.0
    
    async def _get_average_lncp_score(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Get average LNCP confidence score for user in date range."""
        
        avg_score = await self.db.fetchval("""
            SELECT AVG(confidence_score) 
            FROM lncp_analysis_results lar
            JOIN writing_samples ws ON lar.writing_sample_id = ws.id
            WHERE ws.user_id = $1 
                AND lar.created_at BETWEEN $2 AND $3
        """, user_id, start_date, end_date)
        
        return float(avg_score) if avg_score else 0.0
    
    def _calculate_effectiveness_score(self, engagement_rate: float, avg_rating: float, improvement_score: float) -> float:
        """Calculate overall effectiveness score for content insight."""
        
        # Normalize rating to 0-1 scale (assuming 1-5 rating scale)
        normalized_rating = (avg_rating - 1) / 4 if avg_rating > 0 else 0
        
        # Weight the components
        effectiveness = (
            engagement_rate * 0.4 +           # 40% engagement
            normalized_rating * 0.3 +         # 30% user satisfaction
            min(1.0, improvement_score + 0.5) * 0.3  # 30% actual improvement
        )
        
        return max(0.0, min(1.0, effectiveness))
    
    def _generate_insight_recommendation(self, engagement_rate: float, improvement_score: float, effectiveness_score: float) -> str:
        """Generate recommendation for insight optimization."""
        
        if effectiveness_score >= 0.8:
            return "amplify_content"
        elif effectiveness_score >= 0.6:
            return "maintain_content"
        elif engagement_rate < 0.1:
            return "redesign_presentation"
        elif improvement_score < 0.05:
            return "improve_actionability"
        else:
            return "comprehensive_revision"
    
    async def _analyze_overall_performance(self, insights: List[ContentInsight], start_date: datetime, end_date: datetime) -> ContentPerformance:
        """Analyze overall content performance metrics."""
        
        if not insights:
            return ContentPerformance(
                total_insights_shown=0,
                total_engagements=0,
                overall_engagement_rate=0.0,
                avg_improvement_score=0.0,
                top_performing_insights=[],
                underperforming_insights=[],
                content_freshness_score=0.0,
                personalization_effectiveness=0.0
            )
        
        total_shown = sum(insight.total_shown for insight in insights)
        total_engaged = sum(insight.total_engaged for insight in insights)
        overall_engagement_rate = total_engaged / total_shown if total_shown > 0 else 0
        
        avg_improvement_score = statistics.mean([insight.improvement_score for insight in insights])
        
        # Identify top and underperforming insights
        sorted_insights = sorted(insights, key=lambda x: x.effectiveness_score, reverse=True)
        top_performing = [insight.insight_type for insight in sorted_insights[:3]]
        underperforming = [
            insight.insight_type for insight in sorted_insights 
            if insight.effectiveness_score < 0.4
        ]
        
        # Calculate content freshness score
        freshness_score = await self._calculate_content_freshness_score(start_date, end_date)
        
        # Calculate personalization effectiveness
        personalization_score = await self._calculate_personalization_effectiveness(start_date, end_date)
        
        return ContentPerformance(
            total_insights_shown=total_shown,
            total_engagements=total_engaged,
            overall_engagement_rate=overall_engagement_rate,
            avg_improvement_score=avg_improvement_score,
            top_performing_insights=top_performing,
            underperforming_insights=underperforming,
            content_freshness_score=freshness_score,
            personalization_effectiveness=personalization_score
        )
    
    async def _calculate_content_freshness_score(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate how fresh/current the content library is."""
        
        # Get content age distribution
        content_ages = await self.db.fetch("""
            SELECT 
                insight_type,
                EXTRACT(DAY FROM $2 - created_at) as age_days
            FROM content_insights
            WHERE created_at <= $2
                AND last_updated >= $1  -- Only include recently active content
        """, start_date, end_date)
        
        if not content_ages:
            return 0.5  # Neutral score if no data
        
        # Calculate freshness score based on age distribution
        fresh_content = len([c for c in content_ages if c["age_days"] <= 30])
        stale_content = len([c for c in content_ages if c["age_days"] > 90])
        total_content = len(content_ages)
        
        if total_content == 0:
            return 0.5
        
        freshness_score = (fresh_content / total_content) - (stale_content / total_content * 0.5)
        return max(0.0, min(1.0, freshness_score))
    
    async def _calculate_personalization_effectiveness(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate effectiveness of content personalization."""
        
        # Compare engagement rates for personalized vs non-personalized content
        personalized_engagement = await self.db.fetchval("""
            SELECT AVG(CASE WHEN ui.interaction_type = 'engaged' THEN 1.0 ELSE 0.0 END)
            FROM user_interactions ui
            JOIN content_insights ci ON ui.content_insight_id = ci.id
            WHERE ci.is_personalized = true 
                AND ui.created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        generic_engagement = await self.db.fetchval("""
            SELECT AVG(CASE WHEN ui.interaction_type = 'engaged' THEN 1.0 ELSE 0.0 END)
            FROM user_interactions ui
            JOIN content_insights ci ON ui.content_insight_id = ci.id
            WHERE ci.is_personalized = false 
                AND ui.created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        if generic_engagement == 0:
            return 0.5  # Neutral if no baseline
        
        # Personalization effectiveness is the lift over generic content
        effectiveness = personalized_engagement / generic_engagement if generic_engagement > 0 else 1.0
        return min(1.0, effectiveness)
    
    async def _analyze_personalization_effectiveness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze personalization effectiveness across user segments."""
        
        # Get engagement by user tier (as a proxy for user segments)
        tier_engagement = await self.db.fetch("""
            SELECT 
                u.tier,
                COUNT(*) as total_interactions,
                AVG(CASE WHEN ui.interaction_type = 'engaged' THEN 1.0 ELSE 0.0 END) as engagement_rate,
                AVG(ui.rating) as avg_rating
            FROM user_interactions ui
            JOIN users u ON ui.user_id = u.id
            JOIN content_insights ci ON ui.content_insight_id = ci.id
            WHERE ui.created_at BETWEEN $1 AND $2
            GROUP BY u.tier
            HAVING COUNT(*) >= 20  -- Minimum sample size
        """, start_date, end_date)
        
        # Calculate personalization gaps
        tier_performance = {}
        overall_engagement = 0
        total_interactions = 0
        
        for tier_data in tier_engagement:
            tier = tier_data["tier"]
            engagement = float(tier_data["engagement_rate"])
            interactions = tier_data["total_interactions"]
            
            tier_performance[tier] = {
                "engagement_rate": engagement,
                "interactions": interactions,
                "avg_rating": float(tier_data["avg_rating"]) if tier_data["avg_rating"] else 0
            }
            
            overall_engagement += engagement * interactions
            total_interactions += interactions
        
        avg_engagement = overall_engagement / total_interactions if total_interactions > 0 else 0
        
        # Identify segments that need better personalization
        underperforming_segments = [
            tier for tier, data in tier_performance.items() 
            if data["engagement_rate"] < avg_engagement * 0.8
        ]
        
        # Calculate personalization effectiveness score
        if tier_performance:
            engagement_variance = statistics.variance([data["engagement_rate"] for data in tier_performance.values()])
            # Lower variance indicates better personalization (more consistent engagement)
            effectiveness_score = max(0.0, 1.0 - (engagement_variance * 10))
        else:
            effectiveness_score = 0.5
        
        return {
            "effectiveness_score": effectiveness_score,
            "tier_performance": tier_performance,
            "underperforming_segments": underperforming_segments,
            "avg_engagement_rate": avg_engagement,
            "personalization_opportunities": len(underperforming_segments)
        }
    
    async def _identify_content_opportunities(self, insights: List[ContentInsight], personalization_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify opportunities for content improvement and creation."""
        
        opportunities = []
        
        # Content gap analysis
        insight_categories = set(insight.insight_category for insight in insights)
        expected_categories = {"grammar", "style", "structure", "vocabulary", "clarity", "engagement"}
        missing_categories = expected_categories - insight_categories
        
        for missing_category in missing_categories:
            opportunities.append({
                "type": "content_gap",
                "category": missing_category,
                "description": f"No insights available for {missing_category}",
                "expected_engagement": 0.3,  # Estimated engagement rate
                "priority": "medium"
            })
        
        # Low-performing content improvement opportunities
        low_performers = [insight for insight in insights if insight.effectiveness_score < 0.4]
        for insight in low_performers[:3]:  # Top 3 priorities
            opportunities.append({
                "type": "content_improvement",
                "insight_type": insight.insight_type,
                "current_effectiveness": insight.effectiveness_score,
                "target_effectiveness": 0.6,
                "improvement_areas": self._identify_improvement_areas(insight),
                "priority": "high"
            })
        
        # Personalization opportunities
        underperforming_segments = personalization_analysis.get("underperforming_segments", [])
        if underperforming_segments:
            opportunities.append({
                "type": "personalization_improvement",
                "segments": underperforming_segments,
                "current_effectiveness": personalization_analysis.get("effectiveness_score", 0),
                "target_effectiveness": 0.7,
                "expected_improvement": 0.25,
                "priority": "medium"
            })
        
        # Content amplification opportunities (high performers)
        top_performers = [insight for insight in insights if insight.effectiveness_score > 0.8]
        if top_performers:
            opportunities.append({
                "type": "content_amplification",
                "top_insights": [insight.insight_type for insight in top_performers],
                "current_reach": sum(insight.total_shown for insight in top_performers),
                "amplification_potential": 2.0,  # 2x reach potential
                "expected_engagement_increase": 0.2,
                "priority": "high"
            })
        
        return opportunities
    
    def _identify_improvement_areas(self, insight: ContentInsight) -> List[str]:
        """Identify specific areas where content insight needs improvement."""
        
        areas = []
        
        if insight.engagement_rate < 0.1:
            areas.append("presentation_design")
            areas.append("headline_optimization")
        
        if insight.avg_rating < 3.0:
            areas.append("content_quality")
            areas.append("actionability")
        
        if insight.improvement_score < 0.05:
            areas.append("practical_applicability")
            areas.append("follow_up_guidance")
        
        if not areas:
            areas.append("comprehensive_review")
        
        return areas
    
    async def _analyze_content_freshness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze content freshness and identify stale content."""
        
        # Get content by age
        content_by_age = await self.db.fetch("""
            SELECT 
                insight_type,
                insight_category,
                created_at,
                last_updated,
                EXTRACT(DAY FROM $2 - last_updated) as days_since_update
            FROM content_insights
            WHERE created_at <= $2
            ORDER BY days_since_update DESC
        """, start_date, end_date)
        
        # Categorize content by freshness
        fresh_content = [c for c in content_by_age if c["days_since_update"] <= 30]
        aging_content = [c for c in content_by_age if 30 < c["days_since_update"] <= 90]
        stale_content = [c for c in content_by_age if c["days_since_update"] > 90]
        
        # Identify priority refresh candidates
        priority_refresh = []
        for content in stale_content[:5]:  # Top 5 stale items
            # Check if this content type is still being used
            recent_usage = await self.db.fetchval("""
                SELECT COUNT(*) FROM user_interactions ui
                JOIN content_insights ci ON ui.content_insight_id = ci.id
                WHERE ci.insight_type = $1 
                    AND ui.created_at >= $2
            """, content["insight_type"], end_date - timedelta(days=30))
            
            if recent_usage > 10:  # Still being used
                priority_refresh.append({
                    "insight_type": content["insight_type"],
                    "days_stale": content["days_since_update"],
                    "recent_usage": recent_usage
                })
        
        return {
            "total_content_items": len(content_by_age),
            "fresh_content_count": len(fresh_content),
            "aging_content_count": len(aging_content),
            "stale_content_count": len(stale_content),
            "freshness_score": len(fresh_content) / len(content_by_age) if content_by_age else 0,
            "priority_refresh_candidates": priority_refresh
        }
    
    # Execution methods
    async def _execute_content_improvement(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content improvement action."""
        
        insight_type = action["insight_type"]
        improvement_areas = action.get("improvement_areas", [])
        
        # Store content improvement task
        improvement_data = {
            "insight_type": insight_type,
            "improvement_areas": improvement_areas,
            "current_effectiveness": action.get("current_effectiveness", 0),
            "target_effectiveness": action.get("target_effectiveness", 0.6),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO content_improvement_tasks (
                insight_type, improvement_data, agent_name, 
                status, created_at
            ) VALUES ($1, $2, $3, 'pending', NOW())
        """,
        insight_type,
        json.dumps(improvement_data),
        self.name
        )
        
        logger.info(f"Created content improvement task for {insight_type}: {improvement_areas}")
        
        return {
            "status": "success",
            "insight_type": insight_type,
            "improvement_areas": improvement_areas
        }
    
    async def _execute_content_creation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content creation action."""
        
        category = action["category"]
        expected_engagement = action.get("expected_engagement", 0.3)
        
        # Store content creation task
        creation_data = {
            "category": category,
            "content_gap": True,
            "expected_engagement": expected_engagement,
            "priority": action.get("priority", "medium"),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO content_creation_tasks (
                category, creation_data, agent_name,
                status, created_at
            ) VALUES ($1, $2, $3, 'pending', NOW())
        """,
        category,
        json.dumps(creation_data),
        self.name
        )
        
        logger.info(f"Created content creation task for category: {category}")
        
        return {
            "status": "success",
            "category": category,
            "expected_engagement": expected_engagement
        }
    
    async def _execute_personalization_improvement(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute personalization improvement action."""
        
        segments = action.get("segments", [])
        current_effectiveness = action.get("current_effectiveness", 0)
        target_effectiveness = action.get("target_effectiveness", 0.7)
        
        # Store personalization improvement task
        personalization_data = {
            "underperforming_segments": segments,
            "current_effectiveness": current_effectiveness,
            "target_effectiveness": target_effectiveness,
            "improvement_type": "segment_specific_content",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO personalization_improvements (
                improvement_data, agent_name, status, created_at
            ) VALUES ($1, $2, 'pending', NOW())
        """,
        json.dumps(personalization_data),
        self.name
        )
        
        logger.info(f"Created personalization improvement task for segments: {segments}")
        
        return {
            "status": "success",
            "segments": segments,
            "target_improvement": target_effectiveness - current_effectiveness
        }
    
    async def _execute_content_refresh(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content refresh action."""
        
        stale_items = action.get("stale_items", [])
        
        # Store content refresh tasks
        for item in stale_items:
            refresh_data = {
                "insight_type": item["insight_type"],
                "days_stale": item["days_stale"],
                "recent_usage": item["recent_usage"],
                "refresh_priority": "high" if item["recent_usage"] > 50 else "medium",
                "timestamp": datetime.now().isoformat()
            }
            
            await self.db.execute("""
                INSERT INTO content_refresh_tasks (
                    insight_type, refresh_data, agent_name,
                    status, created_at
                ) VALUES ($1, $2, $3, 'pending', NOW())
            """,
            item["insight_type"],
            json.dumps(refresh_data),
            self.name
            )
        
        logger.info(f"Created {len(stale_items)} content refresh tasks")
        
        return {
            "status": "success",
            "stale_items_count": len(stale_items)
        }
    
    async def _execute_content_amplification(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content amplification action."""
        
        top_performers = action.get("top_performers", [])
        amplification_potential = action.get("amplification_potential", 2.0)
        
        # Store content amplification task
        amplification_data = {
            "top_performing_insights": [p["insight_type"] for p in top_performers],
            "current_reach": sum(p["total_shown"] for p in top_performers),
            "amplification_factor": amplification_potential,
            "amplification_methods": ["increased_visibility", "cross_promotion", "recommendation_boost"],
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO content_amplification_tasks (
                amplification_data, agent_name, status, created_at
            ) VALUES ($1, $2, 'pending', NOW())
        """,
        json.dumps(amplification_data),
        self.name
        )
        
        logger.info(f"Created content amplification task for {len(top_performers)} top performers")
        
        return {
            "status": "success",
            "top_performers_count": len(top_performers),
            "amplification_factor": amplification_potential
        }
    
    # Action creation methods
    async def _create_content_improvement_action(self, insight: Dict) -> Dict[str, Any]:
        improvement_areas = self._identify_improvement_areas(ContentInsight(**insight))
        return {
            "type": "improve_content",
            "insight_type": insight["insight_type"],
            "current_effectiveness": insight["effectiveness_score"],
            "target_effectiveness": 0.6,
            "improvement_areas": improvement_areas
        }
    
    async def _create_content_creation_action(self, opportunity: Dict) -> Dict[str, Any]:
        return {
            "type": "create_content",
            "category": opportunity["category"],
            "expected_engagement": opportunity["expected_engagement"],
            "priority": opportunity["priority"]
        }
    
    async def _create_personalization_improvement_action(self, analysis: Dict) -> Dict[str, Any]:
        return {
            "type": "improve_personalization",
            "segments": analysis.get("underperforming_segments", []),
            "current_effectiveness": analysis.get("effectiveness_score", 0),
            "target_effectiveness": 0.7
        }
    
    async def _create_content_refresh_action(self, freshness_analysis: Dict) -> Dict[str, Any]:
        return {
            "type": "refresh_content",
            "stale_items": freshness_analysis.get("priority_refresh_candidates", [])
        }
    
    async def _create_content_amplification_action(self, top_performers: List[ContentInsight]) -> Dict[str, Any]:
        return {
            "type": "amplify_content",
            "top_performers": [insight.__dict__ for insight in top_performers],
            "amplification_potential": 2.0
        }
    
    # Helper methods
    def _calculate_content_analysis_confidence(self, performance: ContentPerformance, insights: List[ContentInsight]) -> float:
        """Calculate confidence in content analysis."""
        
        factors = []
        
        # Sample size factor
        if performance.total_insights_shown >= 1000:
            factors.append(1.0)
        elif performance.total_insights_shown >= 500:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Content diversity factor
        if len(insights) >= 10:
            factors.append(1.0)
        elif len(insights) >= 5:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Engagement data quality factor
        if performance.overall_engagement_rate > 0:
            factors.append(1.0)
        else:
            factors.append(0.3)
        
        return statistics.mean(factors)
    
    def _assess_content_data_quality(self, performance: ContentPerformance, insights: List[ContentInsight]) -> float:
        """Assess quality of content analysis data."""
        
        quality_factors = []
        
        # Sufficient sample sizes
        adequate_sample_insights = len([i for i in insights if i.total_shown >= self.config["min_insight_impressions"]])
        sample_adequacy = adequate_sample_insights / len(insights) if insights else 0
        quality_factors.append(sample_adequacy)
        
        # Reasonable engagement rates
        if 0.05 <= performance.overall_engagement_rate <= 0.5:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.7)
        
        # Content freshness
        quality_factors.append(performance.content_freshness_score)
        
        return statistics.mean(quality_factors)
    
    def _generate_content_recommendations(self, performance: ContentPerformance, opportunities: List[Dict], freshness: Dict) -> List[Dict[str, Any]]:
        """Generate content optimization recommendations."""
        
        recommendations = []
        
        # Overall performance recommendations
        if performance.overall_engagement_rate < 0.15:
            recommendations.append({
                "title": "Critical content engagement issue",
                "description": f"Overall engagement rate {performance.overall_engagement_rate:.1%} below threshold",
                "expected_impact": "30-40% engagement improvement",
                "priority": "high",
                "action_type": "comprehensive_content_audit"
            })
        
        # Content gap recommendations
        content_gaps = [op for op in opportunities if op["type"] == "content_gap"]
        if content_gaps:
            recommendations.append({
                "title": f"Fill {len(content_gaps)} content gaps",
                "description": f"Missing content in categories: {[gap['category'] for gap in content_gaps]}",
                "expected_impact": "Improved user experience coverage",
                "priority": "medium",
                "action_type": "content_creation"
            })
        
        # Underperforming content recommendations
        if performance.underperforming_insights:
            recommendations.append({
                "title": f"Optimize {len(performance.underperforming_insights)} underperforming insights",
                "description": "Improve content quality and presentation for low-engagement insights",
                "expected_impact": "25-30% engagement improvement for affected content",
                "priority": "high",
                "action_type": "content_improvement"
            })
        
        # Content freshness recommendations
        if freshness.get("freshness_score", 0) < 0.6:
            recommendations.append({
                "title": "Refresh stale content",
                "description": f"{freshness.get('stale_content_count', 0)} content items need updating",
                "expected_impact": "Improved relevance and engagement",
                "priority": "medium",
                "action_type": "content_refresh"
            })
        
        return recommendations
    
    def _assess_content_optimization_risk(self, actions: List[Dict], results: AnalysisResults) -> float:
        """Assess risk of content optimization actions."""
        
        # Content optimization is generally low risk
        return 0.25
    
    async def _create_content_rollback_plan(self, actions: List[Dict]) -> Dict[str, Any]:
        """Create rollback plan for content optimizations."""
        
        return {
            "rollback_actions": ["restore_previous_content_versions", "disable_new_content"],
            "trigger_conditions": ["engagement_drop_below_baseline", "user_satisfaction_decline"],
            "monitoring_period_days": 14
        }


# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Standalone execution for testing."""
    
    # Database connection (would come from main application)
    db_pool = await asyncpg.create_pool("postgresql://user:pass@localhost/quirrely")
    
    # Initialize agent system
    from .base_agent import initialize_agent_system
    await initialize_agent_system(db_pool)
    
    # Create and run content optimization agent
    agent = ContentOptimizationAgent(db_pool)
    
    try:
        performance_metrics = await agent.run_full_cycle()
        print(f"Content optimization completed successfully!")
        print(f"ROI Estimate: {performance_metrics.roi_estimate:.2f}")
        print(f"System Improvement: {performance_metrics.system_improvement}")
        
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        raise
    
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())