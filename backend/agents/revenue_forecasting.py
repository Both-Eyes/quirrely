#!/usr/bin/env python3
"""
REVENUE FORECASTING AGENT
Analyzes revenue trends, predicts future performance, and optimizes revenue 
strategies through advanced forecasting models and trend analysis.

Phase 3 - Partnership & Pricing Intelligence (Week 7-9)
"""

import asyncio
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncpg
import math

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class RevenueMetrics:
    """Revenue performance and forecasting metrics."""
    historical_mrr: List[Tuple[str, float]]  # (month, mrr)
    current_mrr: float
    mrr_growth_rate: float
    user_growth_rate: float
    churn_rate: float
    ltv_by_cohort: Dict[str, float]
    revenue_per_tier: Dict[str, float]
    forecasting_confidence: float

@dataclass
class RevenueForecast:
    """Revenue forecast data and scenarios."""
    forecast_horizon_months: int
    base_scenario: List[Tuple[str, float]]  # (month, predicted_mrr)
    optimistic_scenario: List[Tuple[str, float]]
    conservative_scenario: List[Tuple[str, float]]
    key_assumptions: Dict[str, Any]
    confidence_intervals: List[float]

class RevenueForecastingAgent(BatchAgent):
    """Agent for revenue forecasting and growth optimization."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="revenue_forecasting",
            schedule_cron="0 3 * * 5",  # Fridays at 3 AM EST
            data_sources=[
                "user_revenue_metrics",
                "users",
                "user_tier_progressions",
                "subscription_events",
                "partnership_relationships",
                "conversion_events"
            ],
            db_pool=db_pool
        )
        
        self.config = {
            "forecast_horizon_months": 12,
            "historical_analysis_months": 24,
            "min_data_points_for_forecasting": 6,
            "confidence_threshold": 0.70,
            "growth_optimization_threshold": 0.15,
            "scenario_variance_factor": 0.3,
            "trend_smoothing_factor": 0.7,
            "seasonality_adjustment": True
        }
    
    async def analyze(self) -> AnalysisResults:
        """Analyze revenue trends and generate forecasts."""
        
        logger.info("Starting revenue forecasting analysis")
        
        historical_start = datetime.now() - timedelta(days=30 * self.config["historical_analysis_months"])
        
        # Get historical revenue data
        revenue_metrics = await self._get_revenue_metrics(historical_start)
        
        # Analyze revenue trends
        trend_analysis = await self._analyze_revenue_trends(revenue_metrics)
        
        # Analyze cohort performance
        cohort_analysis = await self._analyze_cohort_performance(historical_start)
        
        # Generate revenue forecasts
        revenue_forecasts = await self._generate_revenue_forecasts(revenue_metrics, trend_analysis)
        
        # Analyze revenue optimization opportunities
        optimization_opportunities = await self._identify_revenue_opportunities(revenue_metrics, cohort_analysis)
        
        # Calculate seasonality patterns
        seasonality_analysis = await self._analyze_seasonality_patterns(historical_start)
        
        analysis_data = {
            "revenue_metrics": revenue_metrics,
            "trend_analysis": trend_analysis,
            "cohort_analysis": cohort_analysis,
            "revenue_forecasts": revenue_forecasts,
            "optimization_opportunities": optimization_opportunities,
            "seasonality_patterns": seasonality_analysis,
            "analysis_period_start": historical_start.isoformat(),
            "current_mrr": revenue_metrics.current_mrr
        }
        
        confidence_score = self._calculate_forecasting_confidence(revenue_metrics, trend_analysis)
        
        logger.info(f"Revenue forecasting completed - ${revenue_metrics.current_mrr:.2f} MRR, {revenue_metrics.mrr_growth_rate:.1%} growth")
        
        return AnalysisResults(
            agent_name=self.name,
            confidence_score=confidence_score,
            data=analysis_data,
            recommendations=await self._generate_revenue_recommendations(analysis_data)
        )
    
    async def optimize(self, analysis: AnalysisResults) -> OptimizationActions:
        """Generate revenue optimization strategies."""
        
        logger.info("Generating revenue optimizations")
        
        data = analysis.data
        revenue_metrics = data["revenue_metrics"]
        forecasts = data["revenue_forecasts"]
        opportunities = data["optimization_opportunities"]
        
        optimizations = []
        risk_score = 0.0
        
        # Optimize growth rate
        if revenue_metrics.mrr_growth_rate < self.config["growth_optimization_threshold"]:
            growth_optimization = await self._optimize_revenue_growth(data)
            optimizations.append(growth_optimization)
            risk_score = max(risk_score, 0.25)
        
        # Optimize churn reduction
        if revenue_metrics.churn_rate > 0.05:  # Above 5% monthly churn
            churn_optimization = await self._optimize_churn_reduction(data)
            optimizations.append(churn_optimization)
            risk_score = max(risk_score, 0.2)
        
        # Optimize tier mix
        tier_optimization = await self._optimize_tier_revenue_mix(data)
        if tier_optimization["confidence"] > 0.65:
            optimizations.append(tier_optimization)
            risk_score = max(risk_score, 0.15)
        
        # Optimize seasonal strategies
        seasonal_optimization = await self._optimize_seasonal_strategies(data)
        if seasonal_optimization["confidence"] > 0.6:
            optimizations.append(seasonal_optimization)
            risk_score = max(risk_score, 0.1)
        
        # Optimize cohort value
        cohort_optimization = await self._optimize_cohort_value(data)
        if cohort_optimization["confidence"] > 0.7:
            optimizations.append(cohort_optimization)
            risk_score = max(risk_score, 0.3)
        
        logger.info(f"Generated {len(optimizations)} revenue optimizations")
        
        return OptimizationActions(
            agent_name=self.name,
            actions=optimizations,
            risk_assessment=min(risk_score, 0.9),
            rollback_plan=self._create_revenue_rollback_plan()
        )
    
    async def execute(self, optimizations: OptimizationActions) -> Dict[str, Any]:
        """Execute revenue optimization strategies."""
        
        logger.info(f"Executing {len(optimizations.actions)} revenue optimizations")
        
        execution_results = []
        
        for action in optimizations.actions:
            try:
                if action["type"] == "revenue_growth_optimization":
                    result = await self._execute_growth_optimization(action)
                elif action["type"] == "churn_reduction_optimization":
                    result = await self._execute_churn_optimization(action)
                elif action["type"] == "tier_revenue_optimization":
                    result = await self._execute_tier_optimization(action)
                elif action["type"] == "seasonal_strategy_optimization":
                    result = await self._execute_seasonal_optimization(action)
                elif action["type"] == "cohort_value_optimization":
                    result = await self._execute_cohort_optimization(action)
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
        """Generate revenue forecasting performance report."""
        
        # Calculate improvement estimates
        revenue_metrics = analysis.data["revenue_metrics"]
        forecasts = analysis.data["revenue_forecasts"]
        
        # Estimate revenue impact
        total_revenue_improvement = 0.0
        successful_optimizations = 0
        
        for result in execution["results"]:
            if result["status"] == "success" and "impact" in result:
                total_revenue_improvement += result["impact"].get("revenue_impact", 0.0)
                successful_optimizations += 1
        
        # Calculate forecasting accuracy (using most recent forecast vs actual)
        baseline_mrr = revenue_metrics.current_mrr
        baseline_growth_rate = revenue_metrics.mrr_growth_rate
        
        # Estimate improvement in growth rate
        growth_rate_improvement = total_revenue_improvement / max(1, baseline_mrr)
        
        # Calculate system improvement score
        revenue_improvements = successful_optimizations
        max_possible_improvements = len(optimizations.actions)
        system_improvement = (revenue_improvements / max_possible_improvements) if max_possible_improvements > 0 else 0.0
        
        # Calculate ROI estimate
        optimization_cost = 250  # Analysis and implementation cost per optimization
        annual_revenue_impact = total_revenue_improvement * 12
        roi_estimate = (annual_revenue_impact / (optimization_cost * revenue_improvements)) if revenue_improvements > 0 else 0.0
        
        # Log key metrics
        await self._log_revenue_metrics(analysis, execution)
        
        return PerformanceMetrics(
            agent_name=self.name,
            execution_time=datetime.now().isoformat(),
            roi_estimate=roi_estimate,
            optimization_impact=growth_rate_improvement,
            system_improvement=system_improvement,
            additional_metrics={
                "baseline_mrr": baseline_mrr,
                "baseline_growth_rate": baseline_growth_rate,
                "estimated_revenue_improvement": total_revenue_improvement,
                "forecasting_confidence": revenue_metrics.forecasting_confidence,
                "churn_rate_baseline": revenue_metrics.churn_rate,
                "revenue_optimizations_applied": revenue_improvements
            }
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSIS METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _get_revenue_metrics(self, since: datetime) -> RevenueMetrics:
        """Get comprehensive revenue metrics for analysis."""
        
        # Get historical MRR by month
        historical_mrr = await self.db.fetch("""
            SELECT 
                TO_CHAR(month_year, 'YYYY-MM') as month,
                SUM(monthly_revenue) as mrr
            FROM user_revenue_metrics
            WHERE month_year >= $1
            GROUP BY month_year
            ORDER BY month_year
        """, since)
        
        # Get current MRR
        current_mrr = await self.db.fetchval("""
            SELECT SUM(monthly_revenue)
            FROM user_revenue_metrics
            WHERE month_year = DATE_TRUNC('month', NOW())
        """) or 0
        
        # Calculate MRR growth rate
        if len(historical_mrr) >= 2:
            recent_mrr = historical_mrr[-1]["mrr"]
            previous_mrr = historical_mrr[-2]["mrr"]
            mrr_growth_rate = (recent_mrr - previous_mrr) / max(1, previous_mrr)
        else:
            mrr_growth_rate = 0.0
        
        # Get user growth rate
        user_growth = await self.db.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as new_users_month,
                COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '60 days' AND created_at < NOW() - INTERVAL '30 days') as new_users_prev_month
            FROM users
        """)
        
        new_users_month = user_growth["new_users_month"] or 0
        new_users_prev_month = user_growth["new_users_prev_month"] or 1
        user_growth_rate = (new_users_month - new_users_prev_month) / new_users_prev_month
        
        # Calculate churn rate
        churn_analysis = await self.db.fetchrow("""
            SELECT 
                COUNT(*) FILTER (WHERE last_activity < NOW() - INTERVAL '30 days') as churned_users,
                COUNT(*) as total_active_users
            FROM users
            WHERE tier != 'anonymous' AND created_at < NOW() - INTERVAL '30 days'
        """)
        
        churned_users = churn_analysis["churned_users"] or 0
        total_active_users = churn_analysis["total_active_users"] or 1
        churn_rate = churned_users / total_active_users
        
        # Get LTV by cohort (signup month)
        ltv_by_cohort = await self.db.fetch("""
            SELECT 
                TO_CHAR(u.created_at, 'YYYY-MM') as signup_month,
                AVG(urm.monthly_revenue * 12 / GREATEST(1, EXTRACT(EPOCH FROM (NOW() - u.created_at))/2592000)) as estimated_ltv,
                COUNT(DISTINCT u.id) as cohort_size
            FROM users u
            JOIN user_revenue_metrics urm ON u.id = urm.user_id
            WHERE u.created_at >= $1
            GROUP BY TO_CHAR(u.created_at, 'YYYY-MM')
            HAVING COUNT(DISTINCT u.id) >= 5
            ORDER BY signup_month
        """, since)
        
        # Get revenue per tier
        revenue_per_tier = await self.db.fetch("""
            SELECT 
                u.tier,
                AVG(urm.monthly_revenue) as avg_revenue_per_user,
                COUNT(DISTINCT u.id) as tier_users
            FROM users u
            JOIN user_revenue_metrics urm ON u.id = urm.user_id
            WHERE urm.month_year >= DATE_TRUNC('month', NOW()) - INTERVAL '3 months'
            GROUP BY u.tier
        """)
        
        return RevenueMetrics(
            historical_mrr=[(row["month"], row["mrr"]) for row in historical_mrr],
            current_mrr=current_mrr,
            mrr_growth_rate=mrr_growth_rate,
            user_growth_rate=user_growth_rate,
            churn_rate=churn_rate,
            ltv_by_cohort={row["signup_month"]: row["estimated_ltv"] for row in ltv_by_cohort},
            revenue_per_tier={row["tier"]: row["avg_revenue_per_user"] for row in revenue_per_tier},
            forecasting_confidence=0.0  # Will be calculated later
        )
    
    async def _analyze_revenue_trends(self, metrics: RevenueMetrics) -> Dict[str, Any]:
        """Analyze revenue trends and patterns."""
        
        if len(metrics.historical_mrr) < 3:
            return {"trend": "insufficient_data", "volatility": 0.0, "acceleration": 0.0}
        
        # Calculate trend direction
        mrr_values = [mrr for _, mrr in metrics.historical_mrr]
        
        # Calculate moving averages for trend smoothing
        ma_window = min(3, len(mrr_values) // 2)
        moving_averages = []
        for i in range(ma_window - 1, len(mrr_values)):
            ma = sum(mrr_values[i - ma_window + 1:i + 1]) / ma_window
            moving_averages.append(ma)
        
        # Determine trend
        if len(moving_averages) >= 2:
            trend_direction = "increasing" if moving_averages[-1] > moving_averages[0] else "decreasing"
            trend_strength = abs(moving_averages[-1] - moving_averages[0]) / max(1, moving_averages[0])
        else:
            trend_direction = "stable"
            trend_strength = 0.0
        
        # Calculate volatility
        if len(mrr_values) >= 2:
            growth_rates = [(mrr_values[i] - mrr_values[i-1]) / max(1, mrr_values[i-1]) 
                          for i in range(1, len(mrr_values))]
            volatility = statistics.stdev(growth_rates) if len(growth_rates) > 1 else 0.0
        else:
            volatility = 0.0
        
        # Calculate acceleration (change in growth rate)
        if len(growth_rates) >= 2:
            acceleration = growth_rates[-1] - growth_rates[-2]
        else:
            acceleration = 0.0
        
        return {
            "trend": trend_direction,
            "trend_strength": trend_strength,
            "volatility": volatility,
            "acceleration": acceleration,
            "moving_averages": moving_averages,
            "growth_rates": growth_rates[-6:] if len(growth_rates) >= 6 else growth_rates  # Last 6 months
        }
    
    async def _analyze_cohort_performance(self, since: datetime) -> Dict[str, Any]:
        """Analyze cohort performance and retention patterns."""
        
        # Analyze revenue retention by cohort
        cohort_retention = await self.db.fetch("""
            WITH cohorts AS (
                SELECT 
                    u.id,
                    TO_CHAR(u.created_at, 'YYYY-MM') as signup_month,
                    u.created_at
                FROM users u
                WHERE u.created_at >= $1 AND u.tier != 'anonymous'
            ),
            cohort_revenue AS (
                SELECT 
                    c.signup_month,
                    EXTRACT(EPOCH FROM (urm.month_year - DATE_TRUNC('month', c.created_at)))/2592000 as months_since_signup,
                    AVG(urm.monthly_revenue) as avg_revenue,
                    COUNT(DISTINCT urm.user_id) as active_users,
                    COUNT(DISTINCT c.id) as cohort_size
                FROM cohorts c
                LEFT JOIN user_revenue_metrics urm ON c.id = urm.user_id
                WHERE urm.month_year IS NOT NULL
                GROUP BY c.signup_month, months_since_signup
            )
            SELECT 
                signup_month,
                months_since_signup,
                avg_revenue,
                active_users,
                cohort_size,
                active_users::float / cohort_size as retention_rate
            FROM cohort_revenue
            WHERE months_since_signup >= 0 AND months_since_signup <= 12
            ORDER BY signup_month, months_since_signup
        """, since)
        
        # Calculate average cohort metrics
        cohort_metrics = {}
        for row in cohort_retention:
            month = row["signup_month"]
            if month not in cohort_metrics:
                cohort_metrics[month] = {
                    "retention_rates": [],
                    "revenue_progression": [],
                    "cohort_size": row["cohort_size"]
                }
            cohort_metrics[month]["retention_rates"].append(row["retention_rate"])
            cohort_metrics[month]["revenue_progression"].append(row["avg_revenue"] or 0)
        
        # Calculate cohort quality metrics
        cohort_quality = {}
        for month, metrics in cohort_metrics.items():
            if len(metrics["retention_rates"]) > 0:
                cohort_quality[month] = {
                    "month_1_retention": metrics["retention_rates"][0] if len(metrics["retention_rates"]) > 0 else 0.0,
                    "month_6_retention": metrics["retention_rates"][5] if len(metrics["retention_rates"]) > 5 else None,
                    "month_12_retention": metrics["retention_rates"][11] if len(metrics["retention_rates"]) > 11 else None,
                    "revenue_growth": (metrics["revenue_progression"][-1] - metrics["revenue_progression"][0]) / max(1, metrics["revenue_progression"][0]) if len(metrics["revenue_progression"]) > 1 else 0.0,
                    "cohort_size": metrics["cohort_size"]
                }
        
        return {
            "cohort_retention_data": [
                {
                    "signup_month": row["signup_month"],
                    "months_since_signup": row["months_since_signup"],
                    "retention_rate": row["retention_rate"],
                    "avg_revenue": row["avg_revenue"]
                } for row in cohort_retention
            ],
            "cohort_quality_metrics": cohort_quality
        }
    
    async def _generate_revenue_forecasts(self, metrics: RevenueMetrics, trends: Dict[str, Any]) -> RevenueForecast:
        """Generate revenue forecasts using trend analysis."""
        
        if len(metrics.historical_mrr) < self.config["min_data_points_for_forecasting"]:
            # Insufficient data for reliable forecasting
            return RevenueForecast(
                forecast_horizon_months=self.config["forecast_horizon_months"],
                base_scenario=[],
                optimistic_scenario=[],
                conservative_scenario=[],
                key_assumptions={},
                confidence_intervals=[]
            )
        
        horizon = self.config["forecast_horizon_months"]
        current_mrr = metrics.current_mrr
        base_growth_rate = metrics.mrr_growth_rate
        
        # Apply trend smoothing
        smoothing_factor = self.config["trend_smoothing_factor"]
        adjusted_growth_rate = base_growth_rate * smoothing_factor
        
        # Generate base scenario
        base_scenario = []
        current_value = current_mrr
        
        for month in range(1, horizon + 1):
            # Apply growth with some variability based on historical volatility
            monthly_growth = adjusted_growth_rate * (1 + (trends.get("acceleration", 0) * month * 0.1))
            current_value *= (1 + monthly_growth)
            
            forecast_date = (datetime.now() + timedelta(days=30 * month)).strftime("%Y-%m")
            base_scenario.append((forecast_date, current_value))
        
        # Generate optimistic scenario (15% better performance)
        optimistic_multiplier = 1.15
        optimistic_scenario = [(date, mrr * optimistic_multiplier) for date, mrr in base_scenario]
        
        # Generate conservative scenario (15% worse performance)
        conservative_multiplier = 0.85
        conservative_scenario = [(date, mrr * conservative_multiplier) for date, mrr in base_scenario]
        
        # Calculate confidence intervals based on historical volatility
        volatility = trends.get("volatility", 0.1)
        confidence_intervals = [max(0.1, 1.0 - (volatility * math.sqrt(month))) for month in range(1, horizon + 1)]
        
        key_assumptions = {
            "base_growth_rate": adjusted_growth_rate,
            "user_growth_rate": metrics.user_growth_rate,
            "churn_rate": metrics.churn_rate,
            "current_mrr": current_mrr,
            "trend_direction": trends.get("trend", "unknown"),
            "volatility": volatility
        }
        
        return RevenueForecast(
            forecast_horizon_months=horizon,
            base_scenario=base_scenario,
            optimistic_scenario=optimistic_scenario,
            conservative_scenario=conservative_scenario,
            key_assumptions=key_assumptions,
            confidence_intervals=confidence_intervals
        )
    
    async def _identify_revenue_opportunities(self, metrics: RevenueMetrics, cohorts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify revenue optimization opportunities."""
        
        opportunities = []
        
        # Opportunity 1: Improve tier mix
        tier_revenues = metrics.revenue_per_tier
        if "pro" in tier_revenues and "free" in tier_revenues:
            pro_revenue = tier_revenues["pro"]
            free_revenue = tier_revenues.get("free", 0)
            
            if pro_revenue > free_revenue * 10:  # High value difference
                opportunities.append({
                    "type": "tier_optimization",
                    "description": "Significant revenue opportunity from converting free to pro users",
                    "potential_impact": pro_revenue * 0.15,  # Assume 15% conversion improvement
                    "confidence": 0.7
                })
        
        # Opportunity 2: Reduce churn
        if metrics.churn_rate > 0.05:
            churn_revenue_impact = metrics.current_mrr * metrics.churn_rate
            opportunities.append({
                "type": "churn_reduction",
                "description": f"High churn rate ({metrics.churn_rate:.1%}) creates revenue loss opportunity",
                "potential_impact": churn_revenue_impact * 0.3,  # Assume 30% churn reduction
                "confidence": 0.8
            })
        
        # Opportunity 3: Cohort value optimization
        cohort_quality = cohorts.get("cohort_quality_metrics", {})
        if cohort_quality:
            recent_cohorts = sorted(cohort_quality.keys())[-3:]  # Last 3 months
            cohort_sizes = [cohort_quality[month]["cohort_size"] for month in recent_cohorts if month in cohort_quality]
            
            if cohort_sizes and sum(cohort_sizes) > 50:  # Significant volume
                opportunities.append({
                    "type": "cohort_optimization",
                    "description": "Optimize new user cohort value and retention",
                    "potential_impact": metrics.current_mrr * 0.1,  # 10% improvement from better onboarding
                    "confidence": 0.6
                })
        
        # Opportunity 4: Partnership revenue
        if "partnership" in metrics.revenue_per_tier:
            partnership_revenue = metrics.revenue_per_tier["partnership"]
            opportunities.append({
                "type": "partnership_expansion",
                "description": "Expand partnership tier adoption and value",
                "potential_impact": partnership_revenue * 0.25,  # 25% growth in partnership revenue
                "confidence": 0.65
            })
        
        return opportunities
    
    async def _analyze_seasonality_patterns(self, since: datetime) -> Dict[str, Any]:
        """Analyze seasonal revenue patterns."""
        
        # Analyze revenue by month
        monthly_patterns = await self.db.fetch("""
            SELECT 
                EXTRACT(MONTH FROM month_year) as month_number,
                TO_CHAR(month_year, 'Month') as month_name,
                AVG(monthly_revenue) as avg_revenue,
                COUNT(DISTINCT user_id) as avg_users
            FROM user_revenue_metrics
            WHERE month_year >= $1
            GROUP BY EXTRACT(MONTH FROM month_year), TO_CHAR(month_year, 'Month')
            ORDER BY month_number
        """, since)
        
        if len(monthly_patterns) < 12:
            return {"seasonality_detected": False, "patterns": []}
        
        # Calculate seasonal indices
        overall_avg_revenue = statistics.mean([p["avg_revenue"] for p in monthly_patterns])
        seasonal_indices = []
        
        for pattern in monthly_patterns:
            seasonal_index = pattern["avg_revenue"] / overall_avg_revenue
            seasonal_indices.append({
                "month": pattern["month_name"].strip(),
                "month_number": pattern["month_number"],
                "seasonal_index": seasonal_index,
                "avg_revenue": pattern["avg_revenue"],
                "avg_users": pattern["avg_users"]
            })
        
        # Detect significant seasonality (coefficient of variation > 0.1)
        revenues = [p["avg_revenue"] for p in monthly_patterns]
        seasonality_strength = statistics.stdev(revenues) / statistics.mean(revenues) if len(revenues) > 1 else 0.0
        
        return {
            "seasonality_detected": seasonality_strength > 0.1,
            "seasonality_strength": seasonality_strength,
            "seasonal_indices": seasonal_indices,
            "peak_months": [s["month"] for s in seasonal_indices if s["seasonal_index"] > 1.15],
            "low_months": [s["month"] for s in seasonal_indices if s["seasonal_index"] < 0.85]
        }
    
    async def _generate_revenue_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate actionable revenue optimization recommendations."""
        
        recommendations = []
        metrics = analysis_data["revenue_metrics"]
        forecasts = analysis_data["revenue_forecasts"]
        opportunities = analysis_data["optimization_opportunities"]
        trends = analysis_data["trend_analysis"]
        
        # Recommendation: Growth rate optimization
        if metrics.mrr_growth_rate < self.config["growth_optimization_threshold"]:
            recommendations.append(
                f"Accelerate MRR growth from {metrics.mrr_growth_rate:.1%} to {self.config['growth_optimization_threshold']:.1%} "
                f"through tier conversion optimization and churn reduction"
            )
        
        # Recommendation: Churn reduction
        if metrics.churn_rate > 0.05:
            potential_savings = metrics.current_mrr * metrics.churn_rate * 0.3
            recommendations.append(
                f"Reduce churn rate from {metrics.churn_rate:.1%} to <5% to save ${potential_savings:.0f}/month in lost revenue"
            )
        
        # Recommendation: Tier optimization
        for opportunity in opportunities:
            if opportunity["type"] == "tier_optimization" and opportunity["confidence"] > 0.6:
                recommendations.append(
                    f"Focus on free-to-pro conversions with ${opportunity['potential_impact']:.0f}/month revenue potential"
                )
        
        # Recommendation: Seasonal optimization
        seasonality = analysis_data.get("seasonality_patterns", {})
        if seasonality.get("seasonality_detected", False):
            peak_months = seasonality.get("peak_months", [])
            if peak_months:
                recommendations.append(
                    f"Leverage seasonal peaks in {', '.join(peak_months)} for targeted growth campaigns"
                )
        
        # Recommendation: Forecasting confidence
        avg_confidence = statistics.mean(forecasts.confidence_intervals) if forecasts.confidence_intervals else 0.5
        if avg_confidence < 0.7:
            recommendations.append(
                f"Improve forecasting accuracy (current {avg_confidence:.1%}) by increasing data collection and analysis frequency"
            )
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OPTIMIZATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _optimize_revenue_growth(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize overall revenue growth strategies."""
        
        metrics = analysis_data["revenue_metrics"]
        current_growth = metrics.mrr_growth_rate
        target_growth = self.config["growth_optimization_threshold"]
        
        optimization = {
            "type": "revenue_growth_optimization",
            "parameters": {
                "current_growth_rate": current_growth,
                "target_growth_rate": target_growth,
                "focus_on_tier_conversions": True,
                "implement_growth_loops": True,
                "optimize_pricing_strategy": True,
                "enhance_value_proposition": True
            },
            "target_improvement": {
                "mrr_growth_increase": target_growth - current_growth,
                "revenue_impact": metrics.current_mrr * (target_growth - current_growth)
            },
            "confidence": 0.75
        }
        
        return optimization
    
    async def _optimize_churn_reduction(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize churn reduction strategies."""
        
        metrics = analysis_data["revenue_metrics"]
        current_churn = metrics.churn_rate
        target_churn = 0.03  # 3% monthly churn target
        
        churn_reduction_potential = max(0, current_churn - target_churn)
        revenue_impact = metrics.current_mrr * churn_reduction_potential
        
        optimization = {
            "type": "churn_reduction_optimization",
            "parameters": {
                "current_churn_rate": current_churn,
                "target_churn_rate": target_churn,
                "implement_early_warning_system": True,
                "enhance_customer_success": True,
                "improve_onboarding": True,
                "add_retention_campaigns": True
            },
            "target_improvement": {
                "churn_rate_reduction": churn_reduction_potential,
                "revenue_impact": revenue_impact
            },
            "confidence": 0.8
        }
        
        return optimization
    
    async def _optimize_tier_revenue_mix(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize revenue mix across user tiers."""
        
        metrics = analysis_data["revenue_metrics"]
        tier_revenues = metrics.revenue_per_tier
        
        # Calculate optimization potential
        pro_revenue = tier_revenues.get("pro", 0)
        free_revenue = tier_revenues.get("free", 0)
        
        optimization_potential = 0.0
        if pro_revenue > free_revenue * 5:  # Significant tier value difference
            optimization_potential = pro_revenue * 0.15  # 15% improvement potential
        
        optimization = {
            "type": "tier_revenue_optimization",
            "parameters": {
                "focus_on_pro_conversions": True,
                "optimize_tier_benefits": True,
                "implement_progressive_pricing": True,
                "enhance_upgrade_flows": True,
                "tier_revenue_distribution": tier_revenues
            },
            "target_improvement": {
                "revenue_mix_optimization": 0.2,
                "revenue_impact": optimization_potential
            },
            "confidence": 0.7 if optimization_potential > 0 else 0.4
        }
        
        return optimization
    
    async def _optimize_seasonal_strategies(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize seasonal revenue strategies."""
        
        seasonality = analysis_data.get("seasonality_patterns", {})
        
        if not seasonality.get("seasonality_detected", False):
            return {"confidence": 0.3}
        
        peak_months = seasonality.get("peak_months", [])
        low_months = seasonality.get("low_months", [])
        
        optimization = {
            "type": "seasonal_strategy_optimization",
            "parameters": {
                "peak_months": peak_months,
                "low_months": low_months,
                "implement_seasonal_campaigns": True,
                "adjust_pricing_seasonally": True,
                "optimize_content_timing": True,
                "seasonal_feature_releases": True
            },
            "target_improvement": {
                "seasonal_revenue_optimization": 0.1,
                "revenue_impact": analysis_data["revenue_metrics"].current_mrr * 0.08
            },
            "confidence": 0.65
        }
        
        return optimization
    
    async def _optimize_cohort_value(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize new user cohort value and progression."""
        
        cohort_data = analysis_data["cohort_analysis"]
        cohort_quality = cohort_data.get("cohort_quality_metrics", {})
        
        if not cohort_quality:
            return {"confidence": 0.4}
        
        # Analyze recent cohort performance
        recent_cohorts = sorted(cohort_quality.keys())[-3:]
        avg_month_1_retention = statistics.mean([
            cohort_quality[month]["month_1_retention"] 
            for month in recent_cohorts 
            if cohort_quality[month]["month_1_retention"] is not None
        ]) if recent_cohorts else 0.0
        
        optimization = {
            "type": "cohort_value_optimization",
            "parameters": {
                "current_month_1_retention": avg_month_1_retention,
                "target_month_1_retention": min(0.9, avg_month_1_retention * 1.3),
                "optimize_onboarding_flow": True,
                "implement_early_engagement": True,
                "personalize_user_journey": True,
                "add_value_demonstration": True
            },
            "target_improvement": {
                "cohort_value_increase": 0.15,
                "revenue_impact": analysis_data["revenue_metrics"].current_mrr * 0.12
            },
            "confidence": 0.7
        }
        
        return optimization
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _execute_growth_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute revenue growth optimization."""
        
        params = action["parameters"]
        
        # Update growth optimization configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'growth_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied growth optimization: target rate {params['target_growth_rate']:.1%}")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "growth_rate_improvement": action["target_improvement"]["mrr_growth_increase"]
        }
    
    async def _execute_churn_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute churn reduction optimization."""
        
        params = action["parameters"]
        
        # Update churn reduction configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'churn_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied churn optimization: target rate {params['target_churn_rate']:.1%}")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "churn_reduction": action["target_improvement"]["churn_rate_reduction"]
        }
    
    async def _execute_tier_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tier revenue mix optimization."""
        
        params = action["parameters"]
        
        # Update tier optimization configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'tier_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied tier optimization: focus on pro conversions")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "revenue_mix_improvement": action["target_improvement"]["revenue_mix_optimization"]
        }
    
    async def _execute_seasonal_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute seasonal strategy optimization."""
        
        params = action["parameters"]
        
        # Update seasonal strategy configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'seasonal_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied seasonal optimization: peak months {params['peak_months']}")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "seasonal_optimization": action["target_improvement"]["seasonal_revenue_optimization"]
        }
    
    async def _execute_cohort_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cohort value optimization."""
        
        params = action["parameters"]
        
        # Update cohort optimization configuration
        await self.db.execute("""
            INSERT INTO agent_configuration_changes (agent_name, change_type, change_data)
            VALUES ($1, 'cohort_optimization', $2)
        """, self.name, params)
        
        logger.info(f"Applied cohort optimization: target retention {params['target_month_1_retention']:.1%}")
        
        return {
            "revenue_impact": action["target_improvement"]["revenue_impact"],
            "cohort_value_increase": action["target_improvement"]["cohort_value_increase"]
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _calculate_forecasting_confidence(self, metrics: RevenueMetrics, trends: Dict[str, Any]) -> float:
        """Calculate confidence score for revenue forecasting."""
        
        # Base confidence on data quantity
        data_points = len(metrics.historical_mrr)
        data_confidence = min(1.0, data_points / 12)  # Full confidence with 12+ months data
        
        # Trend stability confidence
        volatility = trends.get("volatility", 0.5)
        stability_confidence = max(0.1, 1.0 - volatility)
        
        # Revenue scale confidence
        revenue_confidence = min(1.0, metrics.current_mrr / 10000)  # Full confidence at $10k+ MRR
        
        return (data_confidence + stability_confidence + revenue_confidence) / 3
    
    def _create_revenue_rollback_plan(self) -> List[Dict[str, str]]:
        """Create rollback plan for revenue optimizations."""
        
        return [
            {
                "step": "1",
                "action": "Revert growth and churn optimization parameters to baseline",
                "estimated_time": "5 minutes"
            },
            {
                "step": "2",
                "action": "Disable new revenue optimization features via feature flags",
                "estimated_time": "3 minutes"
            },
            {
                "step": "3",
                "action": "Monitor revenue metrics for 7 days to ensure stability",
                "estimated_time": "7 days"
            },
            {
                "step": "4",
                "action": "Analyze impact and adjust forecasting models if needed",
                "estimated_time": "2 hours"
            }
        ]
    
    async def _log_revenue_metrics(self, analysis: AnalysisResults, execution: Dict[str, Any]) -> None:
        """Log revenue forecasting metrics for monitoring."""
        
        metrics = analysis.data["revenue_metrics"]
        forecasts = analysis.data["revenue_forecasts"]
        
        await self.db.execute("""
            INSERT INTO agent_performance_logs (
                agent_name,
                execution_timestamp,
                current_mrr,
                mrr_growth_rate,
                churn_rate,
                forecasting_confidence,
                optimizations_applied
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        self.name,
        datetime.now(),
        metrics.current_mrr,
        metrics.mrr_growth_rate,
        metrics.churn_rate,
        metrics.forecasting_confidence,
        execution["optimizations_applied"]
        )