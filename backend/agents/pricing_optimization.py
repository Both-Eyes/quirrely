#!/usr/bin/env python3
"""
PRICING OPTIMIZATION AGENT
Analyzes pricing sensitivity, tier progression patterns, and optimizes pricing 
strategies to maximize revenue and user lifetime value.

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
class PricingMetrics:
    """Pricing and revenue performance metrics."""
    total_revenue: float
    mrr: float
    average_revenue_per_user: float
    conversion_rate_to_pro: float
    tier_distribution: Dict[str, int]
    churn_rate_by_tier: Dict[str, float]
    lifetime_value_by_tier: Dict[str, float]
    price_sensitivity_score: float

@dataclass
class PricePoint:
    """Price point analysis data."""
    tier: str
    current_price: float
    optimal_price: float
    demand_elasticity: float
    revenue_impact: float
    confidence_level: float

class PricingOptimizationAgent(BatchAgent):
    """Agent for analyzing and optimizing pricing strategies."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="pricing_optimization",
            schedule_cron="0 4 * * 0",  # Sundays at 4 AM EST
            data_sources=[
                "users",
                "user_tier_progressions", 
                "subscription_events",
                "payment_history",
                "user_revenue_metrics",
                "feature_usage_logs"
            ],
            db_pool=db_pool
        )
        
        self.config = {
            "analysis_period_days": 90,
            "min_users_per_tier_for_analysis": 10,
            "price_sensitivity_threshold": 0.7,
            "optimization_confidence_threshold": 0.75,
            "max_price_adjustment": 0.2,  # Maximum 20% price change
            "revenue_impact_threshold": 0.05,  # 5% revenue impact minimum
            "elasticity_calculation_window": 60  # days
        }
    
    async def analyze(self) -> AnalysisResults:
        """Analyze pricing performance and optimization opportunities."""
        
        logger.info("Starting pricing optimization analysis")
        
        analysis_start = datetime.now() - timedelta(days=self.config["analysis_period_days"])
        
        # Get pricing performance metrics
        pricing_metrics = await self._get_pricing_metrics(analysis_start)
        
        # Analyze price sensitivity
        price_sensitivity = await self._analyze_price_sensitivity(analysis_start)
        
        # Analyze tier progression patterns
        tier_progression = await self._analyze_tier_progression_patterns(analysis_start)
        
        # Analyze competitive positioning
        competitive_analysis = await self._analyze_competitive_positioning(analysis_start)
        
        # Calculate demand elasticity
        demand_elasticity = await self._calculate_demand_elasticity(analysis_start)
        
        # Identify optimal price points
        optimal_pricing = await self._identify_optimal_price_points(pricing_metrics, demand_elasticity)
        
        analysis_data = {
            "pricing_metrics": pricing_metrics,
            "price_sensitivity": price_sensitivity,
            "tier_progression": tier_progression,
            "competitive_analysis": competitive_analysis,
            "demand_elasticity": demand_elasticity,
            "optimal_pricing": optimal_pricing,
            "analysis_period_start": analysis_start.isoformat(),
            "total_revenue_analyzed": pricing_metrics.total_revenue
        }
        
        confidence_score = self._calculate_pricing_analysis_confidence(pricing_metrics, demand_elasticity)
        
        logger.info(f"Pricing analysis completed - ${pricing_metrics.total_revenue:.2f} revenue analyzed")
        
        return AnalysisResults(
            agent_name=self.name,
            confidence_score=confidence_score,
            data=analysis_data,
            recommendations=await self._generate_pricing_recommendations(analysis_data)
        )
    
    async def optimize(self, analysis: AnalysisResults) -> OptimizationActions:
        """Generate pricing optimization strategies."""
        
        logger.info("Generating pricing optimizations")
        
        data = analysis.data
        pricing_metrics = data["pricing_metrics"]
        optimal_pricing = data["optimal_pricing"]
        
        optimizations = []
        risk_score = 0.0
        
        # Optimize tier pricing
        for price_point in optimal_pricing:
            if price_point.confidence_level > self.config["optimization_confidence_threshold"]:
                price_adjustment = abs(price_point.optimal_price - price_point.current_price) / price_point.current_price
                
                if price_adjustment > self.config["revenue_impact_threshold"]:
                    pricing_optimization = await self._optimize_tier_pricing(price_point, data)
                    optimizations.append(pricing_optimization)
                    risk_score = max(risk_score, price_adjustment)
        
        # Optimize tier progression incentives
        if pricing_metrics.conversion_rate_to_pro < 0.15:  # Below 15%
            progression_optimization = await self._optimize_tier_progression(data)
            optimizations.append(progression_optimization)
            risk_score = max(risk_score, 0.3)
        
        # Optimize pricing for partnerships
        partnership_pricing = await self._optimize_partnership_pricing(data)
        if partnership_pricing["confidence"] > 0.7:
            optimizations.append(partnership_pricing)
            risk_score = max(risk_score, 0.25)
        
        # Dynamic pricing strategies
        dynamic_pricing = await self._optimize_dynamic_pricing(data)
        if dynamic_pricing["confidence"] > 0.6:
            optimizations.append(dynamic_pricing)
            risk_score = max(risk_score, 0.4)
        
        logger.info(f"Generated {len(optimizations)} pricing optimizations")
        
        return OptimizationActions(
            agent_name=self.name,
            actions=optimizations,
            risk_assessment=min(risk_score, 0.9),
            rollback_plan=self._create_pricing_rollback_plan()
        )
    
    async def execute(self, optimizations: OptimizationActions) -> Dict[str, Any]:
        """Execute pricing optimizations."""
        
        logger.info(f"Executing {len(optimizations.actions)} pricing optimizations")
        
        execution_results = []
        
        for action in optimizations.actions:
            try:
                if action["type"] == "tier_pricing_optimization":
                    result = await self._execute_tier_pricing_optimization(action)
                elif action["type"] == "tier_progression_optimization":
                    result = await self._execute_progression_optimization(action)
                elif action["type"] == "partnership_pricing_optimization":
                    result = await self._execute_partnership_pricing_optimization(action)
                elif action["type"] == "dynamic_pricing_optimization":
                    result = await self._execute_dynamic_pricing_optimization(action)
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
        """Generate pricing optimization performance report."""
        
        # Calculate improvement estimates
        pricing_metrics = analysis.data["pricing_metrics"]
        optimal_pricing = analysis.data["optimal_pricing"]
        
        # Estimate revenue impact
        total_revenue_impact = 0.0
        successful_optimizations = 0
        
        for result in execution["results"]:
            if result["status"] == "success" and "impact" in result:
                total_revenue_impact += result["impact"].get("revenue_impact", 0.0)
                successful_optimizations += 1
        
        # Calculate pricing optimization effectiveness
        baseline_mrr = pricing_metrics.mrr
        estimated_mrr_improvement = total_revenue_impact
        optimization_impact = estimated_mrr_improvement / max(1, baseline_mrr)
        
        # Calculate system improvement score
        pricing_improvements = successful_optimizations
        max_possible_improvements = len(optimizations.actions)
        system_improvement = (pricing_improvements / max_possible_improvements) if max_possible_improvements > 0 else 0.0
        
        # Calculate ROI estimate
        optimization_cost = 200  # Analysis and testing cost per optimization
        monthly_revenue_impact = estimated_mrr_improvement
        roi_estimate = (monthly_revenue_impact / (optimization_cost * pricing_improvements)) if pricing_improvements > 0 else 0.0
        
        # Log key metrics
        await self._log_pricing_metrics(analysis, execution)
        
        return PerformanceMetrics(
            agent_name=self.name,
            execution_time=datetime.now().isoformat(),
            roi_estimate=roi_estimate,
            optimization_impact=optimization_impact,
            system_improvement=system_improvement,
            additional_metrics={
                "baseline_mrr": baseline_mrr,
                "estimated_mrr_improvement": estimated_mrr_improvement,
                "pricing_optimizations_applied": pricing_improvements,
                "total_revenue_analyzed": pricing_metrics.total_revenue,
                "conversion_rate_baseline": pricing_metrics.conversion_rate_to_pro
            }
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSIS METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _get_pricing_metrics(self, since: datetime) -> PricingMetrics:
        """Get comprehensive pricing performance metrics."""
        
        # Get revenue metrics
        revenue_metrics = await self.db.fetchrow("""
            SELECT 
                SUM(monthly_revenue) as total_revenue,
                AVG(monthly_revenue) as avg_revenue_per_user,
                COUNT(DISTINCT user_id) as total_users
            FROM user_revenue_metrics 
            WHERE month_year >= $1
        """, since)
        
        # Get MRR calculation
        current_mrr = await self.db.fetchval("""
            SELECT SUM(monthly_revenue) 
            FROM user_revenue_metrics 
            WHERE month_year = DATE_TRUNC('month', NOW())
        """) or 0
        
        # Get tier distribution
        tier_distribution = await self.db.fetch("""
            SELECT 
                tier,
                COUNT(*) as user_count
            FROM users 
            WHERE created_at >= $1
            GROUP BY tier
        """, since)
        
        # Get conversion rate to pro
        conversion_data = await self.db.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE to_tier = 'pro') as conversions_to_pro,
                COUNT(DISTINCT user_id) as total_users_with_progressions
            FROM user_tier_progressions 
            WHERE transition_date >= $1
        """, since)
        
        # Get churn rate by tier
        churn_by_tier = await self.db.fetch("""
            WITH tier_churn AS (
                SELECT 
                    u.tier,
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE u.last_activity < NOW() - INTERVAL '30 days') as churned_users
                FROM users u
                WHERE u.created_at >= $1
                GROUP BY u.tier
            )
            SELECT 
                tier,
                COALESCE(churned_users::float / NULLIF(total_users, 0), 0) as churn_rate
            FROM tier_churn
        """, since)
        
        # Calculate lifetime value by tier
        ltv_by_tier = await self.db.fetch("""
            SELECT 
                u.tier,
                AVG(urm.monthly_revenue * 12 / GREATEST(1, EXTRACT(EPOCH FROM (NOW() - u.created_at))/2592000)) as estimated_ltv
            FROM users u
            JOIN user_revenue_metrics urm ON u.id = urm.user_id
            WHERE u.created_at >= $1
            GROUP BY u.tier
            HAVING COUNT(*) >= $2
        """, since, self.config["min_users_per_tier_for_analysis"])
        
        total_revenue = revenue_metrics["total_revenue"] or 0
        total_users = revenue_metrics["total_users"] or 1
        conversions = conversion_data["conversions_to_pro"] or 0
        total_progressions = conversion_data["total_users_with_progressions"] or 1
        
        return PricingMetrics(
            total_revenue=total_revenue,
            mrr=current_mrr,
            average_revenue_per_user=total_revenue / total_users,
            conversion_rate_to_pro=conversions / total_progressions,
            tier_distribution={row["tier"]: row["user_count"] for row in tier_distribution},
            churn_rate_by_tier={row["tier"]: row["churn_rate"] for row in churn_by_tier},
            lifetime_value_by_tier={row["tier"]: row["estimated_ltv"] or 0 for row in ltv_by_tier},
            price_sensitivity_score=0.0  # Will be calculated in price sensitivity analysis
        )
    
    async def _analyze_price_sensitivity(self, since: datetime) -> Dict[str, Any]:
        """Analyze user price sensitivity and willingness to pay."""
        
        # Analyze tier upgrade patterns around price changes
        upgrade_patterns = await self.db.fetch("""
            WITH price_change_periods AS (
                SELECT 
                    tier,
                    price_change_date,
                    old_price,
                    new_price,
                    LAG(price_change_date) OVER (PARTITION BY tier ORDER BY price_change_date) as prev_change_date
                FROM pricing_history
                WHERE price_change_date >= $1
            ),
            upgrade_impact AS (
                SELECT 
                    pcp.tier,
                    pcp.price_change_date,
                    pcp.new_price / pcp.old_price - 1 as price_change_percent,
                    COUNT(utp.id) as upgrades_before,
                    COUNT(utp2.id) as upgrades_after
                FROM price_change_periods pcp
                LEFT JOIN user_tier_progressions utp ON 
                    utp.to_tier = pcp.tier AND 
                    utp.transition_date BETWEEN pcp.prev_change_date AND pcp.price_change_date
                LEFT JOIN user_tier_progressions utp2 ON 
                    utp2.to_tier = pcp.tier AND 
                    utp2.transition_date BETWEEN pcp.price_change_date AND pcp.price_change_date + INTERVAL '30 days'
                GROUP BY pcp.tier, pcp.price_change_date, pcp.old_price, pcp.new_price
            )
            SELECT 
                tier,
                AVG(price_change_percent) as avg_price_change,
                AVG(CASE WHEN upgrades_before > 0 THEN upgrades_after::float / upgrades_before ELSE 1 END) as upgrade_rate_change
            FROM upgrade_impact
            GROUP BY tier
        """, since)
        
        # Analyze feature usage vs pricing tier
        feature_value_analysis = await self.db.fetch("""
            SELECT 
                u.tier,
                AVG(ful.daily_usage_count) as avg_daily_feature_usage,
                COUNT(DISTINCT ful.feature_name) as features_used,
                AVG(urm.monthly_revenue) as avg_monthly_revenue
            FROM users u
            JOIN feature_usage_logs ful ON u.id = ful.user_id
            JOIN user_revenue_metrics urm ON u.id = urm.user_id
            WHERE ful.usage_date >= $1
            GROUP BY u.tier
        """, since)
        
        # Calculate price sensitivity score
        sensitivity_scores = {}
        for upgrade in upgrade_patterns:
            if upgrade["avg_price_change"] != 0:
                # Price elasticity = % change in quantity / % change in price
                elasticity = (upgrade["upgrade_rate_change"] - 1) / upgrade["avg_price_change"]
                sensitivity_scores[upgrade["tier"]] = abs(elasticity)
        
        return {
            "upgrade_sensitivity": [
                {
                    "tier": row["tier"],
                    "avg_price_change": row["avg_price_change"],
                    "upgrade_rate_change": row["upgrade_rate_change"],
                    "price_elasticity": sensitivity_scores.get(row["tier"], 0.5)
                } for row in upgrade_patterns
            ],
            "feature_value_correlation": [
                {
                    "tier": row["tier"],
                    "avg_daily_usage": row["avg_daily_feature_usage"],
                    "features_used": row["features_used"],
                    "revenue_per_feature": row["avg_monthly_revenue"] / max(1, row["features_used"]),
                    "usage_intensity": row["avg_daily_feature_usage"] * row["features_used"]
                } for row in feature_value_analysis
            ],
            "overall_sensitivity_score": statistics.mean(sensitivity_scores.values()) if sensitivity_scores else 0.5
        }
    
    async def _analyze_tier_progression_patterns(self, since: datetime) -> Dict[str, Any]:
        """Analyze user tier progression patterns and timing."""
        
        # Analyze progression timing
        progression_timing = await self.db.fetch("""
            SELECT 
                from_tier,
                to_tier,
                AVG(EXTRACT(EPOCH FROM (transition_date - u.created_at))/86400) as avg_days_to_upgrade,
                COUNT(*) as progression_count,
                AVG(CASE WHEN from_tier = 'free' THEN EXTRACT(EPOCH FROM (transition_date - u.created_at))/86400 END) as avg_free_to_pro_days
            FROM user_tier_progressions utp
            JOIN users u ON utp.user_id = u.id
            WHERE utp.transition_date >= $1
            GROUP BY from_tier, to_tier
            HAVING COUNT(*) >= 5
        """, since)
        
        # Analyze progression triggers
        progression_triggers = await self.db.fetch("""
            SELECT 
                utp.trigger_event,
                COUNT(*) as trigger_count,
                AVG(CASE WHEN utp.to_tier = 'pro' THEN 1.0 ELSE 0.0 END) as pro_conversion_rate
            FROM user_tier_progressions utp
            WHERE utp.transition_date >= $1 AND utp.trigger_event IS NOT NULL
            GROUP BY utp.trigger_event
            ORDER BY trigger_count DESC
        """, since)
        
        # Analyze progression abandonment
        abandonment_analysis = await self.db.fetchrow("""
            WITH progression_attempts AS (
                SELECT 
                    COUNT(*) FILTER (WHERE event_type = 'upgrade_initiated') as upgrade_attempts,
                    COUNT(*) FILTER (WHERE event_type = 'upgrade_completed') as upgrade_completions,
                    COUNT(*) FILTER (WHERE event_type = 'upgrade_abandoned') as upgrade_abandonments
                FROM conversion_events
                WHERE created_at >= $1
            )
            SELECT 
                upgrade_attempts,
                upgrade_completions,
                upgrade_abandonments,
                CASE WHEN upgrade_attempts > 0 
                     THEN upgrade_abandonments::float / upgrade_attempts 
                     ELSE 0 END as abandonment_rate
            FROM progression_attempts
        """, since)
        
        return {
            "progression_patterns": [
                {
                    "from_tier": row["from_tier"],
                    "to_tier": row["to_tier"],
                    "avg_days_to_upgrade": row["avg_days_to_upgrade"],
                    "progression_count": row["progression_count"]
                } for row in progression_timing
            ],
            "common_triggers": [
                {
                    "trigger": row["trigger_event"],
                    "count": row["trigger_count"],
                    "pro_conversion_rate": row["pro_conversion_rate"]
                } for row in progression_triggers
            ],
            "abandonment_metrics": {
                "upgrade_attempts": abandonment_analysis["upgrade_attempts"] or 0,
                "upgrade_completions": abandonment_analysis["upgrade_completions"] or 0,
                "abandonment_rate": abandonment_analysis["abandonment_rate"] or 0.0
            }
        }
    
    async def _analyze_competitive_positioning(self, since: datetime) -> Dict[str, Any]:
        """Analyze competitive pricing positioning."""
        
        # Analyze user feedback mentioning pricing or competitors
        pricing_feedback = await self.db.fetch("""
            SELECT 
                sentiment_score,
                feedback_text,
                user_tier,
                created_at
            FROM user_feedback
            WHERE created_at >= $1 
                AND (LOWER(feedback_text) LIKE '%price%' 
                     OR LOWER(feedback_text) LIKE '%cost%'
                     OR LOWER(feedback_text) LIKE '%expensive%'
                     OR LOWER(feedback_text) LIKE '%cheap%'
                     OR LOWER(feedback_text) LIKE '%competitor%')
            ORDER BY created_at DESC
            LIMIT 50
        """, since)
        
        # Analyze signup sources and pricing concerns
        signup_analysis = await self.db.fetch("""
            SELECT 
                signup_source,
                COUNT(*) as signups,
                AVG(CASE WHEN tier = 'pro' THEN 1.0 ELSE 0.0 END) as pro_conversion_rate,
                AVG(EXTRACT(EPOCH FROM (first_pro_upgrade - created_at))/86400) as avg_days_to_pro
            FROM (
                SELECT 
                    u.id,
                    u.signup_source,
                    u.tier,
                    u.created_at,
                    MIN(utp.transition_date) FILTER (WHERE utp.to_tier = 'pro') as first_pro_upgrade
                FROM users u
                LEFT JOIN user_tier_progressions utp ON u.id = utp.user_id
                WHERE u.created_at >= $1
                GROUP BY u.id, u.signup_source, u.tier, u.created_at
            ) as user_progression
            GROUP BY signup_source
            HAVING COUNT(*) >= 10
        """, since)
        
        # Calculate pricing sentiment
        positive_sentiment = len([f for f in pricing_feedback if f["sentiment_score"] > 0.1])
        negative_sentiment = len([f for f in pricing_feedback if f["sentiment_score"] < -0.1])
        total_feedback = len(pricing_feedback)
        
        sentiment_score = (positive_sentiment - negative_sentiment) / max(1, total_feedback)
        
        return {
            "pricing_sentiment": {
                "sentiment_score": sentiment_score,
                "positive_mentions": positive_sentiment,
                "negative_mentions": negative_sentiment,
                "total_feedback": total_feedback
            },
            "source_performance": [
                {
                    "source": row["signup_source"],
                    "signups": row["signups"],
                    "pro_conversion_rate": row["pro_conversion_rate"],
                    "avg_days_to_pro": row["avg_days_to_pro"]
                } for row in signup_analysis
            ],
            "feedback_themes": [
                {
                    "sentiment": f["sentiment_score"],
                    "user_tier": f["user_tier"],
                    "text": f["feedback_text"][:100]  # First 100 characters
                } for f in pricing_feedback[:10]  # Top 10 most recent
            ]
        }
    
    async def _calculate_demand_elasticity(self, since: datetime) -> Dict[str, float]:
        """Calculate price elasticity of demand for each tier."""
        
        elasticity_data = await self.db.fetch("""
            WITH monthly_metrics AS (
                SELECT 
                    DATE_TRUNC('month', utp.transition_date) as month,
                    utp.to_tier as tier,
                    COUNT(*) as conversions,
                    AVG(ph.price) as avg_price
                FROM user_tier_progressions utp
                LEFT JOIN pricing_history ph ON 
                    utp.to_tier = ph.tier AND 
                    utp.transition_date >= ph.price_change_date AND
                    (utp.transition_date < ph.next_change_date OR ph.next_change_date IS NULL)
                WHERE utp.transition_date >= $1
                GROUP BY DATE_TRUNC('month', utp.transition_date), utp.to_tier
            ),
            price_changes AS (
                SELECT 
                    tier,
                    month,
                    conversions,
                    avg_price,
                    LAG(conversions) OVER (PARTITION BY tier ORDER BY month) as prev_conversions,
                    LAG(avg_price) OVER (PARTITION BY tier ORDER BY month) as prev_price
                FROM monthly_metrics
                WHERE avg_price IS NOT NULL
            )
            SELECT 
                tier,
                AVG(
                    CASE WHEN prev_price > 0 AND prev_conversions > 0 AND avg_price != prev_price
                         THEN ((conversions - prev_conversions)::float / prev_conversions) / 
                              ((avg_price - prev_price) / prev_price)
                         ELSE NULL 
                    END
                ) as price_elasticity
            FROM price_changes
            WHERE prev_price IS NOT NULL
            GROUP BY tier
        """, since)
        
        return {row["tier"]: row["price_elasticity"] or -0.5 for row in elasticity_data}
    
    async def _identify_optimal_price_points(self, metrics: PricingMetrics, elasticity: Dict[str, float]) -> List[PricePoint]:
        """Identify optimal price points for each tier."""
        
        # Get current pricing
        current_prices = await self.db.fetch("""
            SELECT 
                tier,
                price as current_price
            FROM pricing_tiers
            WHERE active = true
        """)
        
        optimal_points = []
        
        for price_data in current_prices:
            tier = price_data["tier"]
            current_price = price_data["current_price"]
            
            # Get demand elasticity for this tier
            tier_elasticity = elasticity.get(tier, -0.5)  # Default elasticity
            
            # Calculate optimal price using elasticity
            # Optimal price = current_price * (1 + 1/elasticity) for profit maximization
            if tier_elasticity < -0.001:  # Avoid division by zero and ensure negative elasticity
                optimal_price_factor = 1 + (1 / tier_elasticity)
                optimal_price = current_price * max(0.5, min(2.0, optimal_price_factor))  # Cap between 50% and 200%
            else:
                optimal_price = current_price  # Keep current price if elasticity is invalid
            
            # Calculate revenue impact
            price_change_factor = optimal_price / current_price
            demand_change_factor = 1 + (tier_elasticity * (price_change_factor - 1))
            revenue_impact = (price_change_factor * demand_change_factor - 1) * 100  # Percentage change
            
            # Calculate confidence based on data quality
            tier_users = metrics.tier_distribution.get(tier, 0)
            confidence = min(1.0, tier_users / 50)  # Full confidence with 50+ users
            
            optimal_points.append(PricePoint(
                tier=tier,
                current_price=current_price,
                optimal_price=optimal_price,
                demand_elasticity=tier_elasticity,
                revenue_impact=revenue_impact,
                confidence_level=confidence
            ))
        
        return optimal_points
    
    async def _generate_pricing_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate actionable pricing optimization recommendations."""
        
        recommendations = []
        pricing_metrics = analysis_data["pricing_metrics"]
        optimal_pricing = analysis_data["optimal_pricing"]
        price_sensitivity = analysis_data["price_sensitivity"]
        
        # Recommendation: Optimize tier pricing
        for price_point in optimal_pricing:
            price_diff_percent = abs(price_point.optimal_price - price_point.current_price) / price_point.current_price
            if price_diff_percent > 0.05 and price_point.confidence_level > 0.7:
                direction = "increase" if price_point.optimal_price > price_point.current_price else "decrease"
                recommendations.append(
                    f"{price_point.tier.title()} tier: {direction} price from ${price_point.current_price:.2f} to "
                    f"${price_point.optimal_price:.2f} (estimated {price_point.revenue_impact:+.1f}% revenue impact)"
                )
        
        # Recommendation: Improve conversion rate
        if pricing_metrics.conversion_rate_to_pro < 0.15:
            recommendations.append(
                f"Improve free-to-pro conversion rate from {pricing_metrics.conversion_rate_to_pro:.1%} to 15%+ "
                f"through better tier progression incentives and value demonstration"
            )
        
        # Recommendation: Address price sensitivity
        sensitivity_score = price_sensitivity["overall_sensitivity_score"]
        if sensitivity_score > 0.8:
            recommendations.append(
                f"High price sensitivity detected (score: {sensitivity_score:.2f}). Consider value-based pricing "
                f"strategies and clearer feature differentiation between tiers"
            )
        
        # Recommendation: Optimize partnership pricing
        partnership_tier_users = pricing_metrics.tier_distribution.get("partnership", 0)
        if partnership_tier_users > 0:
            recommendations.append(
                f"Optimize partnership tier pricing - {partnership_tier_users} users at this tier provide "
                f"opportunity for specialized pricing strategy"
            )
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OPTIMIZATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _optimize_tier_pricing(self, price_point: PricePoint, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pricing for a specific tier."""
        
        price_change_percent = (price_point.optimal_price - price_point.current_price) / price_point.current_price
        
        # Implement gradual price changes to minimize shock
        if abs(price_change_percent) > self.config["max_price_adjustment"]:
            # Phase the change over multiple periods
            target_price = price_point.current_price * (1 + (self.config["max_price_adjustment"] * (1 if price_change_percent > 0 else -1)))
            implementation_phases = 2
        else:
            target_price = price_point.optimal_price
            implementation_phases = 1
        
        optimization = {
            "type": "tier_pricing_optimization",
            "parameters": {
                "tier": price_point.tier,
                "current_price": price_point.current_price,
                "target_price": target_price,
                "implementation_phases": implementation_phases,
                "confidence_level": price_point.confidence_level,
                "expected_elasticity": price_point.demand_elasticity
            },
            "target_improvement": {
                "revenue_impact": price_point.revenue_impact,
                "price_optimization_confidence": price_point.confidence_level
            },
            "confidence": price_point.confidence_level
        }
        
        return optimization
    
    async def _optimize_tier_progression(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize tier progression incentives and flow."""
        
        tier_progression = analysis_data["tier_progression"]
        abandonment_rate = tier_progression["abandonment_metrics"]["abandonment_rate"]
        
        # Analyze most effective triggers
        effective_triggers = [t for t in tier_progression["common_triggers"] 
                            if t["pro_conversion_rate"] > 0.2]
        
        optimization = {
            "type": "tier_progression_optimization",
            "parameters": {
                "reduce_abandonment_rate": True,
                "target_abandonment_reduction": min(0.3, abandonment_rate * 0.5),
                "optimize_trigger_timing": True,
                "effective_triggers": [t["trigger"] for t in effective_triggers],
                "implement_progressive_pricing": True,
                "add_trial_periods": True
            },
            "target_improvement": {
                "conversion_rate_increase": 0.25,
                "abandonment_reduction": abandonment_rate * 0.3
            },
            "confidence": 0.75
        }
        
        return optimization
    
    async def _optimize_partnership_pricing(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pricing strategy for partnership tier."""
        
        pricing_metrics = analysis_data["pricing_metrics"]
        partnership_users = pricing_metrics.tier_distribution.get("partnership", 0)
        
        if partnership_users < 5:
            return {"confidence": 0.3}  # Not enough data
        
        optimization = {
            "type": "partnership_pricing_optimization",
            "parameters": {
                "implement_volume_discounts": True,
                "add_collaboration_premium": True,
                "optimize_shared_allocation_pricing": True,
                "introduce_team_features_premium": True
            },
            "target_improvement": {
                "partnership_revenue_per_user_increase": 0.15,
                "partnership_adoption_increase": 0.20
            },
            "confidence": 0.7
        }
        
        return optimization
    
    async def _optimize_dynamic_pricing(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize dynamic pricing strategies."""
        
        price_sensitivity = analysis_data["price_sensitivity"]
        
        # Implement personalized pricing based on usage patterns
        optimization = {
            "type": "dynamic_pricing_optimization",
            "parameters": {
                "implement_usage_based_pricing": True,
                "add_seasonal_pricing_adjustments": True,
                "implement_cohort_based_pricing": True,
                "add_geographic_pricing_optimization": True,
                "enable_smart_discount_timing": True
            },
            "target_improvement": {
                "overall_revenue_increase": 0.12,
                "conversion_rate_improvement": 0.18
            },
            "confidence": 0.65
        }
        
        return optimization
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _execute_tier_pricing_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tier pricing optimization."""
        
        params = action["parameters"]
        
        # Update pricing configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'tier_pricing_optimization', $2)
        """, self.name, params)
        
        # Log the pricing change
        await self.db.execute("""
            INSERT INTO pricing_history (
                tier, 
                old_price, 
                new_price, 
                price_change_date, 
                change_reason
            ) VALUES ($1, $2, $3, NOW(), 'agent_optimization')
        """, 
        params["tier"], 
        params["current_price"], 
        params["target_price"]
        )
        
        logger.info(f"Applied pricing optimization for {params['tier']}: ${params['current_price']:.2f} -> ${params['target_price']:.2f}")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "price_change_amount": params["target_price"] - params["current_price"]
        }
    
    async def _execute_progression_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tier progression optimization."""
        
        params = action["parameters"]
        
        # Update progression configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'progression_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied progression optimization: abandonment reduction target {params['target_abandonment_reduction']:.1%}")
        
        return {
            "conversion_improvement": action["target_improvement"]["conversion_rate_increase"],
            "abandonment_reduction": action["target_improvement"]["abandonment_reduction"]
        }
    
    async def _execute_partnership_pricing_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute partnership pricing optimization."""
        
        params = action["parameters"]
        
        # Update partnership pricing configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'partnership_pricing_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied partnership pricing optimization with volume discounts: {params['implement_volume_discounts']}")
        
        return {
            "revenue_improvement": action["target_improvement"]["partnership_revenue_per_user_increase"],
            "adoption_improvement": action["target_improvement"]["partnership_adoption_increase"]
        }
    
    async def _execute_dynamic_pricing_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dynamic pricing optimization."""
        
        params = action["parameters"]
        
        # Update dynamic pricing configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'dynamic_pricing_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied dynamic pricing optimization: usage-based={params['implement_usage_based_pricing']}")
        
        return {
            "revenue_impact": action["target_improvement"]["overall_revenue_increase"],
            "conversion_improvement": action["target_improvement"]["conversion_rate_improvement"]
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_pricing_analysis_confidence(self, metrics: PricingMetrics, elasticity: Dict[str, float]) -> float:
        """Calculate confidence score for pricing analysis."""
        
        # Base confidence on revenue sample size
        revenue_confidence = min(1.0, metrics.total_revenue / 50000)  # Full confidence at $50k+ revenue
        
        # Elasticity data quality
        valid_elasticity_count = len([e for e in elasticity.values() if e is not None and e < 0])
        elasticity_confidence = min(1.0, valid_elasticity_count / 3)  # Full confidence with 3+ valid elasticity measurements
        
        # User base size
        total_users = sum(metrics.tier_distribution.values())
        user_confidence = min(1.0, total_users / 100)  # Full confidence with 100+ users
        
        return (revenue_confidence + elasticity_confidence + user_confidence) / 3
    
    def _create_pricing_rollback_plan(self) -> List[Dict[str, str]]:
        """Create rollback plan for pricing optimizations."""
        
        return [
            {
                "step": "1",
                "action": "Revert to previous pricing through pricing_history table",
                "estimated_time": "1 minute"
            },
            {
                "step": "2",
                "action": "Disable dynamic pricing features via feature flags",
                "estimated_time": "2 minutes"
            },
            {
                "step": "3",
                "action": "Notify users of pricing changes if applicable",
                "estimated_time": "15 minutes"
            },
            {
                "step": "4",
                "action": "Monitor conversion metrics for 48 hours",
                "estimated_time": "48 hours"
            }
        ]
    
    async def _log_pricing_metrics(self, analysis: AnalysisResults, execution: Dict[str, Any]) -> None:
        """Log pricing optimization metrics for monitoring."""
        
        metrics = analysis.data["pricing_metrics"]
        
        await self.db.execute("""
            INSERT INTO agent_performance_logs (
                agent_name,
                execution_timestamp,
                total_revenue_analyzed,
                mrr_baseline,
                conversion_rate,
                optimizations_applied
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """,
        self.name,
        datetime.now(),
        metrics.total_revenue,
        metrics.mrr,
        metrics.conversion_rate_to_pro,
        execution["optimizations_applied"]
        )