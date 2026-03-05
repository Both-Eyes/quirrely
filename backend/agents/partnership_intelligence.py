#!/usr/bin/env python3
"""
PARTNERSHIP INTELLIGENCE AGENT
Analyzes collaboration patterns, partnership success metrics, and optimizes 
partnership features for maximum engagement and revenue impact.

Phase 3 - Partnership & Pricing Intelligence (Week 7-9)
"""

import asyncio
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncpg

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class PartnershipMetrics:
    """Partnership engagement and success metrics."""
    total_partnerships: int
    active_partnerships: int
    completed_partnerships: int
    average_duration_days: float
    completion_rate: float
    invitation_acceptance_rate: float
    shared_word_usage_rate: float
    collaboration_frequency: float
    revenue_per_partnership: float

@dataclass
class PartnershipPattern:
    """Discovered partnership usage patterns."""
    pattern_type: str
    user_segment: str
    success_indicators: Dict[str, float]
    optimization_opportunities: List[str]
    estimated_impact: float

class PartnershipIntelligenceAgent(BatchAgent):
    """Agent for analyzing and optimizing partnership features."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="partnership_intelligence",
            schedule_cron="0 2 * * 2",  # Tuesdays at 2 AM EST
            data_sources=[
                "partnership_relationships", 
                "partnership_word_usage",
                "partnership_activity_log",
                "users",
                "user_tier_progressions"
            ],
            db_pool=db_pool
        )
        
        self.config = {
            "analysis_period_days": 30,
            "min_partnerships_for_analysis": 5,
            "partnership_success_threshold": 0.7,
            "optimization_impact_threshold": 0.10,
            "collaboration_frequency_threshold": 3.0,  # interactions per week
            "revenue_correlation_threshold": 0.15
        }
    
    async def analyze(self) -> AnalysisResults:
        """Analyze partnership patterns and performance metrics."""
        
        logger.info("Starting partnership intelligence analysis")
        
        analysis_start = datetime.now() - timedelta(days=self.config["analysis_period_days"])
        
        # Get partnership performance data
        partnership_metrics = await self._get_partnership_metrics(analysis_start)
        
        # Analyze collaboration patterns
        collaboration_patterns = await self._analyze_collaboration_patterns(analysis_start)
        
        # Analyze partnership success factors
        success_factors = await self._analyze_success_factors(analysis_start)
        
        # Analyze revenue impact
        revenue_impact = await self._analyze_partnership_revenue_impact(analysis_start)
        
        # Calculate feature utilization
        feature_utilization = await self._analyze_feature_utilization(analysis_start)
        
        analysis_data = {
            "partnership_metrics": partnership_metrics,
            "collaboration_patterns": collaboration_patterns,
            "success_factors": success_factors,
            "revenue_impact": revenue_impact,
            "feature_utilization": feature_utilization,
            "analysis_period_start": analysis_start.isoformat(),
            "total_partnerships_analyzed": partnership_metrics.total_partnerships
        }
        
        confidence_score = self._calculate_analysis_confidence(partnership_metrics, collaboration_patterns)
        
        logger.info(f"Partnership analysis completed - {partnership_metrics.total_partnerships} partnerships analyzed")
        
        return AnalysisResults(
            agent_name=self.name,
            confidence_score=confidence_score,
            data=analysis_data,
            recommendations=await self._generate_partnership_recommendations(analysis_data)
        )
    
    async def optimize(self, analysis: AnalysisResults) -> OptimizationActions:
        """Generate partnership feature optimizations."""
        
        logger.info("Generating partnership optimizations")
        
        data = analysis.data
        partnership_metrics = data["partnership_metrics"]
        
        optimizations = []
        risk_score = 0.0
        
        # Optimize invitation flow
        if partnership_metrics.invitation_acceptance_rate < 0.6:
            invitation_optimization = await self._optimize_invitation_flow(data)
            optimizations.append(invitation_optimization)
            risk_score = max(risk_score, 0.3)
        
        # Optimize collaboration features
        if partnership_metrics.collaboration_frequency < self.config["collaboration_frequency_threshold"]:
            collaboration_optimization = await self._optimize_collaboration_features(data)
            optimizations.append(collaboration_optimization)
            risk_score = max(risk_score, 0.2)
        
        # Optimize word allocation strategy
        if partnership_metrics.shared_word_usage_rate < 0.4:
            allocation_optimization = await self._optimize_word_allocation(data)
            optimizations.append(allocation_optimization)
            risk_score = max(risk_score, 0.25)
        
        # Optimize partnership matching
        partnership_matching = await self._optimize_partnership_matching(data)
        if partnership_matching["confidence"] > 0.7:
            optimizations.append(partnership_matching)
            risk_score = max(risk_score, 0.15)
        
        logger.info(f"Generated {len(optimizations)} partnership optimizations")
        
        return OptimizationActions(
            agent_name=self.name,
            actions=optimizations,
            risk_assessment=min(risk_score, 0.9),
            rollback_plan=self._create_partnership_rollback_plan()
        )
    
    async def execute(self, optimizations: OptimizationActions) -> Dict[str, Any]:
        """Execute partnership optimizations."""
        
        logger.info(f"Executing {len(optimizations.actions)} partnership optimizations")
        
        execution_results = []
        
        for action in optimizations.actions:
            try:
                if action["type"] == "invitation_flow_optimization":
                    result = await self._execute_invitation_optimization(action)
                elif action["type"] == "collaboration_feature_optimization":
                    result = await self._execute_collaboration_optimization(action)
                elif action["type"] == "word_allocation_optimization":
                    result = await self._execute_allocation_optimization(action)
                elif action["type"] == "partnership_matching_optimization":
                    result = await self._execute_matching_optimization(action)
                else:
                    logger.warning(f"Unknown optimization type: {action['type']}")
                    continue
                
                execution_results.append({
                    "optimization_type": action["type"],
                    "status": "success",
                    "impact": result
                })
                
            except Exception as e:
                logger.error(f"Failed to execute {action['type']}: {str(e)}")
                execution_results.append({
                    "optimization_type": action["type"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "execution_timestamp": datetime.now().isoformat(),
            "optimizations_applied": len([r for r in execution_results if r["status"] == "success"]),
            "optimizations_failed": len([r for r in execution_results if r["status"] == "failed"]),
            "results": execution_results
        }
    
    async def report(self, analysis: AnalysisResults, optimizations: OptimizationActions, 
                    execution: Dict[str, Any]) -> PerformanceMetrics:
        """Generate partnership intelligence performance report."""
        
        # Calculate improvement estimates
        partnership_metrics = analysis.data["partnership_metrics"]
        
        # Estimate partnership success rate improvement
        baseline_success_rate = partnership_metrics.completion_rate
        estimated_success_improvement = 0.0
        
        for result in execution["results"]:
            if result["status"] == "success" and "impact" in result:
                estimated_success_improvement += result["impact"].get("success_rate_improvement", 0.0)
        
        # Calculate revenue impact
        avg_partnership_revenue = partnership_metrics.revenue_per_partnership
        partnership_count_growth = estimated_success_improvement * 0.3  # Assume 30% of success improvement leads to more partnerships
        revenue_impact = avg_partnership_revenue * partnership_count_growth * partnership_metrics.active_partnerships
        
        # Calculate system improvement score
        feature_improvements = len([r for r in execution["results"] if r["status"] == "success"])
        max_possible_improvements = len(optimizations.actions)
        system_improvement = (feature_improvements / max_possible_improvements) if max_possible_improvements > 0 else 0.0
        
        # Calculate ROI estimate
        optimization_cost = 150  # Development and testing cost per optimization
        monthly_revenue_impact = revenue_impact
        roi_estimate = (monthly_revenue_impact / (optimization_cost * feature_improvements)) if feature_improvements > 0 else 0.0
        
        # Log key metrics
        await self._log_partnership_metrics(analysis, execution)
        
        return PerformanceMetrics(
            agent_name=self.name,
            execution_time=datetime.now().isoformat(),
            roi_estimate=roi_estimate,
            optimization_impact=estimated_success_improvement,
            system_improvement=system_improvement,
            additional_metrics={
                "partnerships_analyzed": partnership_metrics.total_partnerships,
                "baseline_success_rate": baseline_success_rate,
                "estimated_success_improvement": estimated_success_improvement,
                "estimated_revenue_impact": revenue_impact,
                "feature_optimizations_applied": feature_improvements
            }
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSIS METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _get_partnership_metrics(self, since: datetime) -> PartnershipMetrics:
        """Get comprehensive partnership performance metrics."""
        
        # Get partnership statistics
        partnership_stats = await self.db.fetchrow("""
            SELECT 
                COUNT(*) as total_partnerships,
                COUNT(*) FILTER (WHERE status = 'active') as active_partnerships,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_partnerships,
                AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/86400) as avg_duration_days
            FROM partnership_relationships 
            WHERE created_at >= $1
        """, since)
        
        # Get invitation metrics
        invitation_metrics = await self.db.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'sent') as invitations_sent,
                COUNT(*) FILTER (WHERE status = 'accepted') as invitations_accepted
            FROM partnership_invitations 
            WHERE created_at >= $1
        """, since)
        
        # Get word usage metrics
        word_usage = await self.db.fetchrow("""
            SELECT 
                AVG(shared_words_used::float / NULLIF(shared_word_allocation, 0)) as shared_usage_rate,
                COUNT(DISTINCT partnership_id) as partnerships_with_usage
            FROM partnership_word_usage 
            WHERE usage_date >= $1
        """, since)
        
        # Get collaboration frequency
        collaboration_freq = await self.db.fetchval("""
            SELECT AVG(weekly_interactions) FROM (
                SELECT 
                    partnership_id,
                    COUNT(*)::float / GREATEST(1, EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at)))/604800) as weekly_interactions
                FROM partnership_activity_log 
                WHERE created_at >= $1
                GROUP BY partnership_id
                HAVING COUNT(*) > 1
            ) AS weekly_stats
        """, since)
        
        # Get revenue per partnership
        revenue_per_partnership = await self.db.fetchval("""
            SELECT 
                AVG(monthly_revenue) 
            FROM user_revenue_metrics urm
            JOIN partnership_relationships pr ON urm.user_id = ANY(ARRAY[pr.user_id_1, pr.user_id_2])
            WHERE pr.created_at >= $1 AND pr.status = 'active'
        """, since) or 0
        
        total_partnerships = partnership_stats["total_partnerships"] or 0
        completed_partnerships = partnership_stats["completed_partnerships"] or 0
        invitations_sent = invitation_metrics["invitations_sent"] or 0
        invitations_accepted = invitation_metrics["invitations_accepted"] or 0
        
        return PartnershipMetrics(
            total_partnerships=total_partnerships,
            active_partnerships=partnership_stats["active_partnerships"] or 0,
            completed_partnerships=completed_partnerships,
            average_duration_days=partnership_stats["avg_duration_days"] or 0.0,
            completion_rate=completed_partnerships / max(1, total_partnerships),
            invitation_acceptance_rate=invitations_accepted / max(1, invitations_sent),
            shared_word_usage_rate=word_usage["shared_usage_rate"] or 0.0,
            collaboration_frequency=collaboration_freq or 0.0,
            revenue_per_partnership=revenue_per_partnership
        )
    
    async def _analyze_collaboration_patterns(self, since: datetime) -> List[Dict[str, Any]]:
        """Analyze collaboration patterns and behaviors."""
        
        patterns = []
        
        # Analyze collaboration timing patterns
        timing_pattern = await self.db.fetchrow("""
            SELECT 
                EXTRACT(hour FROM created_at) as peak_hour,
                EXTRACT(dow FROM created_at) as peak_day,
                COUNT(*) as interaction_count
            FROM partnership_activity_log 
            WHERE created_at >= $1
            GROUP BY EXTRACT(hour FROM created_at), EXTRACT(dow FROM created_at)
            ORDER BY interaction_count DESC
            LIMIT 1
        """, since)
        
        if timing_pattern:
            patterns.append({
                "pattern_type": "peak_collaboration_time",
                "peak_hour": timing_pattern["peak_hour"],
                "peak_day": timing_pattern["peak_day"],
                "interaction_count": timing_pattern["interaction_count"]
            })
        
        # Analyze partnership lifecycle stages
        lifecycle_stages = await self.db.fetch("""
            SELECT 
                CASE 
                    WHEN EXTRACT(EPOCH FROM (NOW() - created_at))/86400 < 7 THEN 'new'
                    WHEN EXTRACT(EPOCH FROM (NOW() - created_at))/86400 < 30 THEN 'developing'
                    WHEN EXTRACT(EPOCH FROM (NOW() - created_at))/86400 < 90 THEN 'mature'
                    ELSE 'long_term'
                END as lifecycle_stage,
                AVG(weekly_activity) as avg_activity,
                COUNT(*) as partnership_count
            FROM (
                SELECT 
                    pr.id,
                    pr.created_at,
                    COUNT(pal.id)::float / GREATEST(1, EXTRACT(EPOCH FROM (NOW() - pr.created_at))/604800) as weekly_activity
                FROM partnership_relationships pr
                LEFT JOIN partnership_activity_log pal ON pr.id = pal.partnership_id AND pal.created_at >= $1
                WHERE pr.created_at >= $1
                GROUP BY pr.id, pr.created_at
            ) AS activity_stats
            GROUP BY lifecycle_stage
        """, since)
        
        patterns.extend([{
            "pattern_type": "lifecycle_activity",
            "lifecycle_stage": stage["lifecycle_stage"],
            "average_weekly_activity": stage["avg_activity"] or 0.0,
            "partnership_count": stage["partnership_count"]
        } for stage in lifecycle_stages])
        
        return patterns
    
    async def _analyze_success_factors(self, since: datetime) -> Dict[str, Any]:
        """Analyze factors that contribute to partnership success."""
        
        # Analyze successful vs unsuccessful partnerships
        success_comparison = await self.db.fetchrow("""
            WITH partnership_success AS (
                SELECT 
                    pr.id,
                    pr.status,
                    CASE WHEN pr.status = 'completed' THEN 1 ELSE 0 END as success,
                    COALESCE(AVG(pwu.shared_words_used), 0) as avg_word_usage,
                    COUNT(pal.id) as total_interactions,
                    EXTRACT(EPOCH FROM (COALESCE(pr.completed_at, NOW()) - pr.created_at))/86400 as duration_days
                FROM partnership_relationships pr
                LEFT JOIN partnership_word_usage pwu ON pr.id = pwu.partnership_id
                LEFT JOIN partnership_activity_log pal ON pr.id = pal.partnership_id
                WHERE pr.created_at >= $1
                GROUP BY pr.id, pr.status, pr.completed_at, pr.created_at
            )
            SELECT 
                AVG(CASE WHEN success = 1 THEN avg_word_usage END) as successful_avg_word_usage,
                AVG(CASE WHEN success = 0 THEN avg_word_usage END) as unsuccessful_avg_word_usage,
                AVG(CASE WHEN success = 1 THEN total_interactions END) as successful_avg_interactions,
                AVG(CASE WHEN success = 0 THEN total_interactions END) as unsuccessful_avg_interactions,
                AVG(CASE WHEN success = 1 THEN duration_days END) as successful_avg_duration,
                AVG(CASE WHEN success = 0 THEN duration_days END) as unsuccessful_avg_duration
            FROM partnership_success
        """, since)
        
        # Analyze user tier correlation with partnership success
        tier_correlation = await self.db.fetch("""
            SELECT 
                u.tier,
                COUNT(*) as total_partnerships,
                AVG(CASE WHEN pr.status = 'completed' THEN 1.0 ELSE 0.0 END) as success_rate
            FROM partnership_relationships pr
            JOIN users u ON u.id = pr.user_id_1 OR u.id = pr.user_id_2
            WHERE pr.created_at >= $1
            GROUP BY u.tier
            HAVING COUNT(*) >= $2
        """, since, self.config["min_partnerships_for_analysis"])
        
        return {
            "word_usage_factor": {
                "successful_avg": success_comparison["successful_avg_word_usage"] or 0.0,
                "unsuccessful_avg": success_comparison["unsuccessful_avg_word_usage"] or 0.0,
                "improvement_factor": (success_comparison["successful_avg_word_usage"] or 0.0) / max(1, success_comparison["unsuccessful_avg_word_usage"] or 1.0)
            },
            "interaction_factor": {
                "successful_avg": success_comparison["successful_avg_interactions"] or 0.0,
                "unsuccessful_avg": success_comparison["unsuccessful_avg_interactions"] or 0.0,
                "improvement_factor": (success_comparison["successful_avg_interactions"] or 0.0) / max(1, success_comparison["unsuccessful_avg_interactions"] or 1.0)
            },
            "duration_factor": {
                "successful_avg_days": success_comparison["successful_avg_duration"] or 0.0,
                "unsuccessful_avg_days": success_comparison["unsuccessful_avg_duration"] or 0.0
            },
            "tier_correlation": [
                {
                    "tier": tier["tier"],
                    "total_partnerships": tier["total_partnerships"],
                    "success_rate": tier["success_rate"]
                } for tier in tier_correlation
            ]
        }
    
    async def _analyze_partnership_revenue_impact(self, since: datetime) -> Dict[str, Any]:
        """Analyze revenue impact of partnership features."""
        
        # Compare revenue between partnership and non-partnership users
        revenue_comparison = await self.db.fetchrow("""
            WITH user_partnership_status AS (
                SELECT DISTINCT
                    u.id,
                    u.tier,
                    CASE WHEN pr.user_id_1 IS NOT NULL OR pr.user_id_2 IS NOT NULL THEN 1 ELSE 0 END as has_partnership
                FROM users u
                LEFT JOIN partnership_relationships pr ON u.id = pr.user_id_1 OR u.id = pr.user_id_2
            ),
            user_revenues AS (
                SELECT 
                    ups.has_partnership,
                    ups.tier,
                    AVG(urm.monthly_revenue) as avg_monthly_revenue,
                    COUNT(*) as user_count
                FROM user_partnership_status ups
                LEFT JOIN user_revenue_metrics urm ON ups.id = urm.user_id
                WHERE urm.month_year >= $1
                GROUP BY ups.has_partnership, ups.tier
            )
            SELECT 
                AVG(CASE WHEN has_partnership = 1 THEN avg_monthly_revenue END) as partnership_user_revenue,
                AVG(CASE WHEN has_partnership = 0 THEN avg_monthly_revenue END) as non_partnership_user_revenue,
                COUNT(CASE WHEN has_partnership = 1 THEN 1 END) as partnership_users,
                COUNT(CASE WHEN has_partnership = 0 THEN 1 END) as non_partnership_users
            FROM user_revenues
        """, since)
        
        # Analyze tier progression correlation
        tier_progression = await self.db.fetchrow("""
            WITH partnership_users AS (
                SELECT DISTINCT
                    CASE 
                        WHEN u1.id IS NOT NULL THEN u1.id 
                        ELSE u2.id 
                    END as user_id
                FROM partnership_relationships pr
                LEFT JOIN users u1 ON pr.user_id_1 = u1.id
                LEFT JOIN users u2 ON pr.user_id_2 = u2.id
                WHERE pr.created_at >= $1
            )
            SELECT 
                COUNT(CASE WHEN pu.user_id IS NOT NULL THEN 1 END) as partnership_user_upgrades,
                COUNT(CASE WHEN pu.user_id IS NULL THEN 1 END) as non_partnership_user_upgrades,
                COUNT(*) as total_upgrades
            FROM user_tier_progressions utp
            LEFT JOIN partnership_users pu ON utp.user_id = pu.user_id
            WHERE utp.transition_date >= $1 AND utp.to_tier = 'pro'
        """, since)
        
        partnership_revenue = revenue_comparison["partnership_user_revenue"] or 0.0
        non_partnership_revenue = revenue_comparison["non_partnership_user_revenue"] or 0.0
        
        return {
            "revenue_lift": {
                "partnership_user_avg": partnership_revenue,
                "non_partnership_user_avg": non_partnership_revenue,
                "revenue_lift_factor": partnership_revenue / max(1, non_partnership_revenue),
                "partnership_users": revenue_comparison["partnership_users"] or 0,
                "non_partnership_users": revenue_comparison["non_partnership_users"] or 0
            },
            "tier_progression": {
                "partnership_user_upgrades": tier_progression["partnership_user_upgrades"] or 0,
                "non_partnership_user_upgrades": tier_progression["non_partnership_user_upgrades"] or 0,
                "total_upgrades": tier_progression["total_upgrades"] or 0,
                "partnership_upgrade_rate": (tier_progression["partnership_user_upgrades"] or 0) / max(1, tier_progression["total_upgrades"] or 1)
            }
        }
    
    async def _analyze_feature_utilization(self, since: datetime) -> Dict[str, Any]:
        """Analyze partnership feature usage patterns."""
        
        # Analyze feature usage by partnerships
        feature_usage = await self.db.fetch("""
            SELECT 
                activity_type,
                COUNT(*) as usage_count,
                COUNT(DISTINCT partnership_id) as partnerships_using,
                AVG(EXTRACT(EPOCH FROM (created_at - LAG(created_at) OVER (PARTITION BY partnership_id ORDER BY created_at)))/3600) as avg_hours_between_usage
            FROM partnership_activity_log
            WHERE created_at >= $1
            GROUP BY activity_type
            ORDER BY usage_count DESC
        """, since)
        
        # Analyze partnership cancellation rates
        cancellation_analysis = await self.db.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled_partnerships,
                COUNT(*) as total_partnerships,
                AVG(CASE WHEN status = 'cancelled' THEN EXTRACT(EPOCH FROM (cancelled_at - created_at))/86400 END) as avg_days_before_cancellation
            FROM partnership_relationships 
            WHERE created_at >= $1
        """, since)
        
        return {
            "feature_adoption": [
                {
                    "feature": usage["activity_type"],
                    "usage_count": usage["usage_count"],
                    "partnerships_using": usage["partnerships_using"],
                    "avg_hours_between_usage": usage["avg_hours_between_usage"] or 0.0
                } for usage in feature_usage
            ],
            "partnership_retention": {
                "cancelled_partnerships": cancellation_analysis["cancelled_partnerships"] or 0,
                "total_partnerships": cancellation_analysis["total_partnerships"] or 0,
                "cancellation_rate": (cancellation_analysis["cancelled_partnerships"] or 0) / max(1, cancellation_analysis["total_partnerships"] or 1),
                "avg_days_before_cancellation": cancellation_analysis["avg_days_before_cancellation"] or 0.0
            }
        }
    
    async def _generate_partnership_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate actionable partnership optimization recommendations."""
        
        recommendations = []
        metrics = analysis_data["partnership_metrics"]
        success_factors = analysis_data["success_factors"]
        
        # Recommendation: Improve invitation acceptance rate
        if metrics.invitation_acceptance_rate < 0.6:
            recommendations.append(
                f"Improve invitation flow - current acceptance rate {metrics.invitation_acceptance_rate:.1%} is below target 60%. "
                f"Consider personalizing invitations and adding partnership preview features."
            )
        
        # Recommendation: Increase collaboration frequency
        if metrics.collaboration_frequency < self.config["collaboration_frequency_threshold"]:
            recommendations.append(
                f"Increase collaboration engagement - current frequency {metrics.collaboration_frequency:.1f} interactions/week is low. "
                f"Add collaboration prompts and shared writing challenges."
            )
        
        # Recommendation: Optimize word allocation
        if metrics.shared_word_usage_rate < 0.4:
            recommendations.append(
                f"Optimize word allocation strategy - only {metrics.shared_word_usage_rate:.1%} of shared words are used. "
                f"Consider dynamic allocation based on partnership activity."
            )
        
        # Recommendation based on success factors
        interaction_factor = success_factors["interaction_factor"]["improvement_factor"]
        if interaction_factor > 1.5:
            recommendations.append(
                f"Promote partnership interactions - successful partnerships have {interaction_factor:.1f}x more interactions. "
                f"Add interaction reminders and collaborative features."
            )
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OPTIMIZATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _optimize_invitation_flow(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize partnership invitation flow and messaging."""
        
        success_factors = analysis_data["success_factors"]
        
        # Calculate optimal invitation parameters
        optimal_timing_hour = 14  # 2 PM default
        collaboration_patterns = analysis_data.get("collaboration_patterns", [])
        
        for pattern in collaboration_patterns:
            if pattern.get("pattern_type") == "peak_collaboration_time":
                optimal_timing_hour = pattern.get("peak_hour", 14)
        
        optimization = {
            "type": "invitation_flow_optimization",
            "parameters": {
                "personalization_level": "high",
                "optimal_send_time": optimal_timing_hour,
                "preview_partnership_features": True,
                "include_success_metrics": True,
                "follow_up_schedule": [24, 72, 168]  # hours
            },
            "target_improvement": {
                "acceptance_rate_increase": 0.15,
                "response_time_reduction": 0.25
            },
            "confidence": 0.75
        }
        
        return optimization
    
    async def _optimize_collaboration_features(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize collaboration features and engagement."""
        
        feature_utilization = analysis_data["feature_utilization"]
        success_factors = analysis_data["success_factors"]
        
        # Identify underutilized features
        underutilized_features = []
        for feature in feature_utilization["feature_adoption"]:
            if feature["partnerships_using"] < analysis_data["partnership_metrics"].active_partnerships * 0.3:
                underutilized_features.append(feature["feature"])
        
        optimization = {
            "type": "collaboration_feature_optimization",
            "parameters": {
                "add_collaboration_prompts": True,
                "implement_shared_writing_challenges": True,
                "add_progress_tracking": True,
                "enable_real_time_collaboration": True,
                "underutilized_features": underutilized_features
            },
            "target_improvement": {
                "collaboration_frequency_increase": 0.30,
                "feature_adoption_increase": 0.25
            },
            "confidence": 0.70
        }
        
        return optimization
    
    async def _optimize_word_allocation(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize word allocation strategy for partnerships."""
        
        metrics = analysis_data["partnership_metrics"]
        
        # Calculate dynamic allocation parameters
        base_shared_allocation = 20000  # Current shared allocation
        usage_rate = metrics.shared_word_usage_rate
        
        # Adjust allocation based on usage patterns
        if usage_rate < 0.3:
            recommended_allocation = int(base_shared_allocation * 0.7)  # Reduce allocation
        elif usage_rate > 0.8:
            recommended_allocation = int(base_shared_allocation * 1.2)  # Increase allocation
        else:
            recommended_allocation = base_shared_allocation
        
        optimization = {
            "type": "word_allocation_optimization",
            "parameters": {
                "dynamic_allocation": True,
                "base_shared_allocation": recommended_allocation,
                "usage_based_adjustments": True,
                "rollover_unused_words": True,
                "bonus_allocation_for_active_partnerships": True
            },
            "target_improvement": {
                "word_utilization_increase": 0.20,
                "partnership_satisfaction_increase": 0.15
            },
            "confidence": 0.80
        }
        
        return optimization
    
    async def _optimize_partnership_matching(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize partnership matching and recommendations."""
        
        success_factors = analysis_data["success_factors"]
        
        # Analyze tier correlation for optimal matching
        tier_correlations = success_factors["tier_correlation"]
        optimal_tier_pairings = []
        
        for tier_data in tier_correlations:
            if tier_data["success_rate"] > self.config["partnership_success_threshold"]:
                optimal_tier_pairings.append(tier_data["tier"])
        
        optimization = {
            "type": "partnership_matching_optimization",
            "parameters": {
                "tier_based_matching": True,
                "optimal_tier_pairings": optimal_tier_pairings,
                "writing_style_compatibility": True,
                "activity_level_matching": True,
                "goal_alignment_scoring": True
            },
            "target_improvement": {
                "partnership_success_rate_increase": 0.18,
                "average_partnership_duration_increase": 0.12
            },
            "confidence": 0.65
        }
        
        return optimization
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _execute_invitation_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute invitation flow optimization."""
        
        params = action["parameters"]
        
        # Update invitation configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'invitation_optimization', $2)
        """, self.name, params)
        
        # Log the optimization
        logger.info(f"Applied invitation flow optimization: personalization={params['personalization_level']}")
        
        return {
            "acceptance_rate_improvement": action["target_improvement"]["acceptance_rate_increase"],
            "response_time_improvement": action["target_improvement"]["response_time_reduction"]
        }
    
    async def _execute_collaboration_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute collaboration feature optimization."""
        
        params = action["parameters"]
        
        # Update collaboration configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'collaboration_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied collaboration optimization: prompts={params['add_collaboration_prompts']}")
        
        return {
            "collaboration_frequency_improvement": action["target_improvement"]["collaboration_frequency_increase"],
            "feature_adoption_improvement": action["target_improvement"]["feature_adoption_increase"]
        }
    
    async def _execute_allocation_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute word allocation optimization."""
        
        params = action["parameters"]
        
        # Update word allocation configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'allocation_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied allocation optimization: allocation={params['base_shared_allocation']}")
        
        return {
            "word_utilization_improvement": action["target_improvement"]["word_utilization_increase"],
            "partnership_satisfaction_improvement": action["target_improvement"]["partnership_satisfaction_increase"]
        }
    
    async def _execute_matching_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute partnership matching optimization."""
        
        params = action["parameters"]
        
        # Update matching configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'matching_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied matching optimization: tier_based={params['tier_based_matching']}")
        
        return {
            "success_rate_improvement": action["target_improvement"]["partnership_success_rate_increase"],
            "duration_improvement": action["target_improvement"]["average_partnership_duration_increase"]
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_analysis_confidence(self, metrics: PartnershipMetrics, patterns: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for partnership analysis."""
        
        # Base confidence on sample size
        sample_size_score = min(1.0, metrics.total_partnerships / 20)  # Full confidence at 20+ partnerships
        
        # Pattern reliability score
        pattern_score = min(1.0, len(patterns) / 5)  # Full confidence with 5+ patterns
        
        # Data quality score
        data_quality_score = 1.0 if metrics.total_partnerships >= self.config["min_partnerships_for_analysis"] else 0.5
        
        return (sample_size_score + pattern_score + data_quality_score) / 3
    
    def _create_partnership_rollback_plan(self) -> List[Dict[str, str]]:
        """Create rollback plan for partnership optimizations."""
        
        return [
            {
                "step": "1",
                "action": "Disable new optimization features via feature flags",
                "estimated_time": "2 minutes"
            },
            {
                "step": "2", 
                "action": "Revert configuration changes in agent_configuration_changes table",
                "estimated_time": "5 minutes"
            },
            {
                "step": "3",
                "action": "Monitor partnership metrics for 24 hours to ensure stability",
                "estimated_time": "24 hours"
            }
        ]
    
    async def _log_partnership_metrics(self, analysis: AnalysisResults, execution: Dict[str, Any]) -> None:
        """Log partnership intelligence metrics for monitoring."""
        
        metrics = analysis.data["partnership_metrics"]
        
        await self.db.execute("""
            INSERT INTO agent_performance_logs (
                agent_name, 
                execution_timestamp, 
                partnerships_analyzed,
                success_rate,
                collaboration_frequency,
                optimizations_applied
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, 
        self.name, 
        datetime.now(),
        metrics.total_partnerships,
        metrics.completion_rate,
        metrics.collaboration_frequency,
        execution["optimizations_applied"]
        )