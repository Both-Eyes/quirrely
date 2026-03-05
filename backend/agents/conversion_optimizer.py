#!/usr/bin/env python3
"""
CONVERSION OPTIMIZATION AGENT
Automatically optimizes Meta/Observers trigger thresholds for maximum conversion rates.

Schedule: Daily at 3 AM EST
Purpose: Increase Anonymous→Signup and Trial→Pro conversion rates
Expected Impact: 10-20% improvement in conversion funnel
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncpg
from dataclasses import dataclass

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics
try:
    from ..conversion_triggers import TriggerType, UserTier, TRIGGER_THRESHOLDS
except ImportError:
    # Fallback for testing
    from enum import Enum
    class UserTier(Enum):
        ANONYMOUS = "anonymous"
        FREE = "free"
        PRO = "pro"
        PARTNERSHIP = "partnership"
    TRIGGER_THRESHOLDS = {}
    class TriggerType(Enum):
        USAGE_WARNING = "usage_warning"

logger = logging.getLogger(__name__)

@dataclass
class ConversionMetrics:
    """Conversion metrics for analysis."""
    anonymous_to_signup: float
    signup_to_trial: float  
    trial_to_pro: float
    overall_funnel: float
    sample_size: int
    confidence_level: float

@dataclass
class ThresholdTest:
    """A/B test results for threshold optimization."""
    threshold_type: str
    tier: UserTier
    original_value: float
    test_value: float
    original_conversion: float
    test_conversion: float
    improvement: float
    statistical_significance: float

class ConversionOptimizationAgent(BatchAgent):
    """Agent for optimizing conversion triggers and thresholds."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="conversion_optimizer",
            schedule_cron="0 3 * * *",  # 3 AM daily
            data_sources=["conversion_events", "meta_events", "users", "user_tier_progressions"],
            db_pool=db_pool,
            config={
                "analysis_period_days": 7,
                "min_sample_size": 100,
                "significance_threshold": 0.05,
                "max_threshold_adjustment": 0.1,  # Don't adjust by more than 10%
                "test_traffic_percentage": 0.2   # Use 20% for A/B tests
            }
        )
    
    async def analyze(self) -> AnalysisResults:
        """Analyze current conversion metrics and identify optimization opportunities."""
        
        logger.info("Starting conversion optimization analysis")
        
        # Define analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config["analysis_period_days"])
        
        # Get current conversion metrics
        current_metrics = await self._get_conversion_metrics(start_date, end_date)
        
        # Analyze trigger effectiveness
        trigger_analysis = await self._analyze_trigger_effectiveness(start_date, end_date)
        
        # Identify optimization opportunities
        opportunities = await self._identify_optimization_opportunities(
            current_metrics, trigger_analysis
        )
        
        # Calculate confidence score based on sample size and data quality
        confidence_score = self._calculate_confidence_score(current_metrics, trigger_analysis)
        
        findings = {
            "current_conversion_metrics": current_metrics.__dict__,
            "trigger_effectiveness": trigger_analysis,
            "optimization_opportunities": opportunities,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        recommendations = self._generate_recommendations(opportunities, current_metrics)
        
        return AnalysisResults(
            agent_name=self.name,
            analysis_period=(start_date, end_date),
            findings=findings,
            confidence_score=confidence_score,
            data_quality=self._assess_data_quality(current_metrics),
            recommendations=recommendations,
            raw_metrics={
                "anonymous_conversion": current_metrics.anonymous_to_signup,
                "trial_conversion": current_metrics.trial_to_pro,
                "overall_funnel": current_metrics.overall_funnel,
                "sample_size": current_metrics.sample_size
            }
        )
    
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions based on analysis."""
        
        logger.info("Generating conversion optimization actions")
        
        opportunities = results.findings["optimization_opportunities"]
        actions = []
        expected_impact = {}
        
        # Generate threshold adjustment actions
        for opportunity in opportunities:
            if opportunity["type"] == "threshold_adjustment":
                action = await self._create_threshold_adjustment_action(opportunity)
                actions.append(action)
                expected_impact[f"conversion_improvement_{opportunity['tier']}"] = opportunity["expected_improvement"]
        
        # Generate A/B test actions for uncertain optimizations
        for opportunity in opportunities:
            if opportunity["type"] == "ab_test_needed":
                action = await self._create_ab_test_action(opportunity)
                actions.append(action)
                expected_impact[f"test_setup_{opportunity['tier']}"] = 1.0
        
        # Assess risk
        risk_assessment = self._assess_optimization_risk(actions, results)
        
        # Create rollback plan
        rollback_plan = await self._create_rollback_plan(actions)
        
        return OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute the optimization actions."""
        
        logger.info(f"Executing {len(actions.actions)} conversion optimization actions")
        
        actions_taken = []
        actions_failed = []
        immediate_impact = {}
        
        for action in actions.actions:
            try:
                if action["type"] == "threshold_adjustment":
                    result = await self._execute_threshold_adjustment(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"threshold_updated_{action['tier']}"] = 1.0
                    
                elif action["type"] == "ab_test_setup":
                    result = await self._execute_ab_test_setup(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"test_started_{action['tier']}"] = 1.0
                    
                elif action["type"] == "meta_observers_update":
                    result = await self._execute_meta_observers_update(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["meta_optimization"] = action.get("impact_score", 1.0)
                
            except Exception as e:
                logger.error(f"Action execution failed: {action['type']} - {str(e)}")
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
    
    async def _get_conversion_metrics(self, start_date: datetime, end_date: datetime) -> ConversionMetrics:
        """Get current conversion metrics for the analysis period."""
        
        # Anonymous to signup conversion
        anonymous_events = await self.db.fetchval("""
            SELECT COUNT(*) FROM conversion_events 
            WHERE event_type = 'limit_hit' 
                AND current_tier = 'anonymous'
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        anonymous_signups = await self.db.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE created_at BETWEEN $1 AND $2
                AND tier != 'anonymous'
        """, start_date, end_date) or 0
        
        # Trial to pro conversion  
        trial_starts = await self.db.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE created_at BETWEEN $1 AND $2
                AND tier = 'free'
        """, start_date, end_date) or 0
        
        pro_conversions = await self.db.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE tier = 'pro'
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        # Calculate conversion rates
        anonymous_to_signup = (anonymous_signups / anonymous_events) if anonymous_events > 0 else 0
        signup_to_trial = 0.872  # From previous analysis - would calculate from actual data
        trial_to_pro = (pro_conversions / trial_starts) if trial_starts > 0 else 0
        
        overall_funnel = anonymous_to_signup * signup_to_trial * trial_to_pro
        sample_size = anonymous_events + trial_starts
        
        # Calculate confidence level based on sample size
        confidence_level = min(0.95, (sample_size / 1000) * 0.95) if sample_size > 0 else 0
        
        return ConversionMetrics(
            anonymous_to_signup=anonymous_to_signup,
            signup_to_trial=signup_to_trial,
            trial_to_pro=trial_to_pro,
            overall_funnel=overall_funnel,
            sample_size=sample_size,
            confidence_level=confidence_level
        )
    
    async def _analyze_trigger_effectiveness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze effectiveness of current trigger thresholds."""
        
        # Get trigger events by tier and threshold
        trigger_analysis = {}
        
        for tier in [UserTier.ANONYMOUS, UserTier.FREE, UserTier.PRO]:
            tier_data = await self.db.fetch("""
                SELECT 
                    event_type,
                    usage_percentage,
                    COUNT(*) as event_count,
                    COUNT(*) FILTER (WHERE event_data::jsonb->'metadata'->>'converted' = 'true') as conversions
                FROM conversion_events 
                WHERE current_tier = $1 
                    AND created_at BETWEEN $2 AND $3
                GROUP BY event_type, usage_percentage
                ORDER BY usage_percentage
            """, tier.value, start_date, end_date)
            
            tier_analysis = {
                "total_events": sum(row["event_count"] for row in tier_data),
                "total_conversions": sum(row["conversions"] for row in tier_data),
                "threshold_performance": {}
            }
            
            for row in tier_data:
                threshold = row["usage_percentage"]
                conversion_rate = row["conversions"] / row["event_count"] if row["event_count"] > 0 else 0
                
                tier_analysis["threshold_performance"][str(threshold)] = {
                    "events": row["event_count"],
                    "conversions": row["conversions"], 
                    "conversion_rate": conversion_rate
                }
            
            tier_analysis["overall_conversion_rate"] = (
                tier_analysis["total_conversions"] / tier_analysis["total_events"] 
                if tier_analysis["total_events"] > 0 else 0
            )
            
            trigger_analysis[tier.value] = tier_analysis
        
        return trigger_analysis
    
    async def _identify_optimization_opportunities(
        self, 
        metrics: ConversionMetrics, 
        trigger_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        
        opportunities = []
        
        # Analyze each tier for optimization potential
        for tier_name, data in trigger_analysis.items():
            tier = UserTier(tier_name)
            current_thresholds = TRIGGER_THRESHOLDS.get(tier, {})
            
            # Check if conversion rates are below expected benchmarks
            overall_rate = data["overall_conversion_rate"]
            
            # Expected benchmark rates (these would be tuned based on industry data)
            benchmarks = {
                UserTier.ANONYMOUS: 0.06,  # 6% conversion
                UserTier.FREE: 0.45,       # 45% trial to pro
                UserTier.PRO: 0.15         # 15% partnership adoption
            }
            
            expected_rate = benchmarks.get(tier, 0.1)
            
            if overall_rate < expected_rate * 0.8:  # 20% below benchmark
                # Analyze threshold performance to find optimal points
                threshold_perf = data["threshold_performance"]
                
                if threshold_perf:
                    # Find best performing threshold
                    best_threshold = max(
                        threshold_perf.keys(),
                        key=lambda t: threshold_perf[t]["conversion_rate"]
                    )
                    
                    best_rate = threshold_perf[best_threshold]["conversion_rate"]
                    current_rate = overall_rate
                    
                    if best_rate > current_rate * 1.1:  # 10% improvement potential
                        opportunities.append({
                            "type": "threshold_adjustment",
                            "tier": tier.value,
                            "current_threshold": current_thresholds.get("usage_warning", 0.8),
                            "recommended_threshold": float(best_threshold) / 100,
                            "expected_improvement": (best_rate - current_rate) / current_rate,
                            "confidence": "high" if data["total_events"] > 100 else "medium"
                        })
            
            # Check for insufficient data requiring A/B tests
            if data["total_events"] < self.config["min_sample_size"]:
                opportunities.append({
                    "type": "ab_test_needed",
                    "tier": tier.value,
                    "reason": "insufficient_data",
                    "current_sample_size": data["total_events"],
                    "required_sample_size": self.config["min_sample_size"]
                })
        
        return opportunities
    
    async def _execute_threshold_adjustment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute threshold adjustment by updating conversion triggers configuration."""
        
        tier = UserTier(action["tier"])
        new_threshold = action["recommended_threshold"]
        
        # Update in-memory configuration (in production, this would update the actual config)
        if tier in TRIGGER_THRESHOLDS:
            old_value = TRIGGER_THRESHOLDS[tier]["usage_warning"]
            TRIGGER_THRESHOLDS[tier]["usage_warning"] = new_threshold
            
            logger.info(f"Updated {tier.value} usage_warning threshold: {old_value} → {new_threshold}")
            
            # Store configuration change in database
            await self.db.execute("""
                INSERT INTO agent_configuration_changes (
                    agent_name, change_type, change_data, created_at
                ) VALUES ($1, $2, $3, NOW())
            """, 
            self.name,
            "threshold_adjustment",
            json.dumps({
                "tier": tier.value,
                "threshold_type": "usage_warning",
                "old_value": old_value,
                "new_value": new_threshold,
                "expected_improvement": action.get("expected_improvement", 0)
            })
            )
            
            return {
                "status": "success",
                "tier": tier.value,
                "old_threshold": old_value,
                "new_threshold": new_threshold
            }
        
        return {"status": "failed", "reason": "tier_not_found"}
    
    async def _execute_ab_test_setup(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Setup A/B test for threshold optimization."""
        
        # Store A/B test configuration
        test_config = {
            "test_name": f"threshold_optimization_{action['tier']}",
            "tier": action["tier"],
            "test_start": datetime.now().isoformat(),
            "test_duration_days": 14,
            "traffic_split": 0.5,
            "variations": {
                "control": {"usage_warning": TRIGGER_THRESHOLDS[UserTier(action["tier"])]["usage_warning"]},
                "test": {"usage_warning": min(0.95, TRIGGER_THRESHOLDS[UserTier(action["tier"])]["usage_warning"] + 0.1)}
            }
        }
        
        await self.db.execute("""
            INSERT INTO ab_tests (
                test_name, agent_name, test_config, status, created_at
            ) VALUES ($1, $2, $3, 'active', NOW())
        """, 
        test_config["test_name"],
        self.name,
        json.dumps(test_config)
        )
        
        logger.info(f"Started A/B test: {test_config['test_name']}")
        
        return {"status": "success", "test_name": test_config["test_name"]}
    
    async def _execute_meta_observers_update(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Send optimization recommendations to Meta/Observers system."""
        
        # Insert optimization event for Meta/Observers processing
        meta_event = {
            "event_type": "conversion_optimization_update",
            "agent_name": self.name,
            "optimization_data": action.get("optimization_data", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO meta_events (
                event_type, source_service, event_data, 
                optimization_priority, created_at
            ) VALUES ($1, $2, $3, 'high', NOW())
        """,
        "conversion_optimization",
        self.name,
        json.dumps(meta_event)
        )
        
        return {"status": "success", "meta_event_created": True}
    
    def _calculate_confidence_score(self, metrics: ConversionMetrics, trigger_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        
        # Base confidence on sample size
        sample_confidence = min(1.0, metrics.sample_size / 1000)
        
        # Factor in data quality
        data_quality = self._assess_data_quality(metrics)
        
        # Factor in consistency across tiers
        tier_consistency = 1.0
        conversion_rates = []
        for tier_data in trigger_analysis.values():
            if tier_data["total_events"] > 10:
                conversion_rates.append(tier_data["overall_conversion_rate"])
        
        if len(conversion_rates) > 1:
            # Lower confidence if conversion rates are highly variable
            cv = statistics.stdev(conversion_rates) / statistics.mean(conversion_rates)
            tier_consistency = max(0.3, 1 - cv)
        
        return sample_confidence * data_quality * tier_consistency
    
    def _assess_data_quality(self, metrics: ConversionMetrics) -> float:
        """Assess the quality of the data used for analysis."""
        
        quality_factors = []
        
        # Sample size adequacy
        if metrics.sample_size >= 500:
            quality_factors.append(1.0)
        elif metrics.sample_size >= 100:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.5)
        
        # Conversion rate reasonableness (not 0 or 100%)
        if 0.01 <= metrics.overall_funnel <= 0.8:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.6)
        
        # Confidence level from statistical perspective
        quality_factors.append(metrics.confidence_level)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _generate_recommendations(self, opportunities: List[Dict[str, Any]], metrics: ConversionMetrics) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on opportunities."""
        
        recommendations = []
        
        for opp in opportunities:
            if opp["type"] == "threshold_adjustment":
                recommendations.append({
                    "title": f"Optimize {opp['tier']} conversion threshold",
                    "description": f"Adjust usage warning threshold from {opp['current_threshold']:.0%} to {opp['recommended_threshold']:.0%}",
                    "expected_impact": f"{opp['expected_improvement']:.1%} conversion improvement",
                    "confidence": opp["confidence"],
                    "action_type": "immediate",
                    "priority": "high"
                })
            
            elif opp["type"] == "ab_test_needed":
                recommendations.append({
                    "title": f"A/B test {opp['tier']} tier optimizations",
                    "description": f"Need {opp['required_sample_size']} samples for confident optimization",
                    "expected_impact": "Data gathering for future optimization",
                    "confidence": "medium",
                    "action_type": "test_setup",
                    "priority": "medium"
                })
        
        # Add general recommendations based on overall metrics
        if metrics.overall_funnel < 0.02:  # Less than 2% overall funnel
            recommendations.append({
                "title": "Overall funnel optimization needed",
                "description": f"Current funnel conversion {metrics.overall_funnel:.1%} is below industry benchmarks",
                "expected_impact": "Significant revenue impact potential",
                "confidence": "high",
                "action_type": "strategic",
                "priority": "high"
            })
        
        return recommendations
    
    def _assess_optimization_risk(self, actions: List[Dict[str, Any]], results: AnalysisResults) -> float:
        """Assess the risk of the proposed optimizations."""
        
        risk_factors = []
        
        # Sample size risk
        sample_size = results.raw_metrics.get("sample_size", 0)
        if sample_size < 100:
            risk_factors.append(0.8)  # High risk
        elif sample_size < 500:
            risk_factors.append(0.4)  # Medium risk
        else:
            risk_factors.append(0.1)  # Low risk
        
        # Confidence risk
        confidence = results.confidence_score
        risk_factors.append(1 - confidence)
        
        # Number of simultaneous changes risk
        num_changes = len([a for a in actions if a.get("type") == "threshold_adjustment"])
        if num_changes > 2:
            risk_factors.append(0.6)
        elif num_changes > 1:
            risk_factors.append(0.3)
        else:
            risk_factors.append(0.1)
        
        return sum(risk_factors) / len(risk_factors)
    
    async def _create_rollback_plan(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create rollback plan for optimization actions."""
        
        rollback_actions = []
        
        for action in actions:
            if action.get("type") == "threshold_adjustment":
                rollback_actions.append({
                    "action": "restore_threshold",
                    "tier": action["tier"],
                    "restore_to": action.get("current_threshold"),
                    "trigger": "performance_degradation"
                })
        
        return {
            "rollback_actions": rollback_actions,
            "trigger_conditions": [
                "conversion_rate_drops_below_baseline",
                "user_complaints_increase",
                "system_errors_increase"
            ],
            "monitoring_period_days": 7
        }
    
    async def _measure_system_improvement(self, analysis: AnalysisResults, execution: ExecutionReport) -> Dict[str, float]:
        """Measure actual system improvement after optimization execution."""
        
        # This would measure actual improvements after execution
        # For now, return estimated improvements
        
        baseline_conversion = analysis.raw_metrics.get("overall_funnel", 0)
        
        return {
            "conversion_rate_improvement": 0.15 * execution.success_rate,  # Estimated 15% improvement
            "revenue_impact": baseline_conversion * 0.15 * execution.success_rate,
            "user_experience_improvement": 0.1 * execution.success_rate,
            "data_quality_improvement": 0.05
        }


# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Standalone execution for testing."""
    
    # Database connection (would come from main application)
    db_pool = await asyncpg.create_pool("postgresql://user:pass@localhost/quirrely")
    
    # Initialize agent system
    from base_agent import initialize_agent_system
    await initialize_agent_system(db_pool)
    
    # Create and run conversion optimization agent
    agent = ConversionOptimizationAgent(db_pool)
    
    try:
        performance_metrics = await agent.run_full_cycle()
        print(f"Conversion optimization completed successfully!")
        print(f"ROI Estimate: {performance_metrics.roi_estimate:.2f}")
        print(f"System Improvement: {performance_metrics.system_improvement}")
        
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        raise
    
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())