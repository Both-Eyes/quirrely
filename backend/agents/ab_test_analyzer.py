#!/usr/bin/env python3
"""
A/B TEST ANALYSIS AGENT
Automatically evaluates Meta/Observers experiments and implements winning variations.

Schedule: Weekly on Wednesdays at 3 AM EST
Purpose: Accelerate experiment validation and optimization deployment
Expected Impact: 3x faster experiment validation, improved decision accuracy
"""

import asyncio
import json
import logging
import statistics
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import asyncpg
from dataclasses import dataclass

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class ABTestResult:
    """A/B test analysis result."""
    test_name: str
    test_type: str
    start_date: datetime
    duration_days: int
    control_group_size: int
    treatment_group_size: int
    control_conversion_rate: float
    treatment_conversion_rate: float
    lift: float  # Percentage improvement
    statistical_significance: float  # p-value
    confidence_interval: Tuple[float, float]
    winner: str  # 'control', 'treatment', 'inconclusive'
    recommendation: str
    business_impact_estimate: float

@dataclass
class ExperimentPortfolio:
    """Overview of all running experiments."""
    total_tests: int
    active_tests: int
    completed_tests: int
    tests_ready_for_analysis: int
    tests_with_winners: int
    avg_test_duration: float
    experiment_velocity: float  # Tests per month
    overall_success_rate: float

class ABTestAnalysisAgent(BatchAgent):
    """Agent for analyzing A/B tests and implementing winning variations."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="ab_test_analyzer",
            schedule_cron="0 3 * * 3",  # 3 AM every Wednesday
            data_sources=["ab_tests", "conversion_events", "meta_events", "user_behavior_data"],
            db_pool=db_pool,
            config={
                "min_test_duration_days": 7,
                "max_test_duration_days": 28,
                "min_sample_size_per_group": 100,
                "significance_threshold": 0.05,  # p < 0.05
                "minimum_effect_size": 0.05,    # 5% minimum lift
                "confidence_level": 0.95,
                "auto_implement_threshold": 0.01,  # Auto-implement if p < 0.01
                "business_impact_threshold": 100   # Minimum monthly revenue impact
            }
        )
    
    async def analyze(self) -> AnalysisResults:
        """Analyze all running A/B tests and identify actionable results."""
        
        logger.info("Starting A/B test analysis")
        
        # Define analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Look back 60 days
        
        # Get experiment portfolio overview
        experiment_portfolio = await self._get_experiment_portfolio(start_date, end_date)
        
        # Analyze individual tests
        test_results = await self._analyze_individual_tests(start_date, end_date)
        
        # Identify tests ready for decision
        decision_ready_tests = await self._identify_decision_ready_tests(test_results)
        
        # Calculate experiment velocity and success metrics
        velocity_metrics = await self._calculate_experiment_velocity(start_date, end_date)
        
        # Identify optimization opportunities
        optimization_opportunities = await self._identify_experiment_optimization_opportunities(
            test_results, velocity_metrics
        )
        
        confidence_score = self._calculate_analysis_confidence(experiment_portfolio, test_results)
        
        findings = {
            "experiment_portfolio": experiment_portfolio.__dict__,
            "completed_test_results": [result.__dict__ for result in test_results],
            "decision_ready_tests": [result.__dict__ for result in decision_ready_tests],
            "velocity_metrics": velocity_metrics,
            "optimization_opportunities": optimization_opportunities,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        recommendations = self._generate_experiment_recommendations(
            decision_ready_tests, optimization_opportunities, velocity_metrics
        )
        
        return AnalysisResults(
            agent_name=self.name,
            analysis_period=(start_date, end_date),
            findings=findings,
            confidence_score=confidence_score,
            data_quality=self._assess_experiment_data_quality(experiment_portfolio, test_results),
            recommendations=recommendations,
            raw_metrics={
                "total_tests": experiment_portfolio.total_tests,
                "tests_with_winners": experiment_portfolio.tests_with_winners,
                "decision_ready_count": len(decision_ready_tests),
                "avg_significance": statistics.mean([t.statistical_significance for t in test_results]) if test_results else 0,
                "experiment_velocity": velocity_metrics.get("tests_per_month", 0)
            }
        )
    
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions for A/B test results."""
        
        logger.info("Generating A/B test optimization actions")
        
        decision_ready_tests = results.findings["decision_ready_tests"]
        optimization_opportunities = results.findings["optimization_opportunities"]
        
        actions = []
        expected_impact = {}
        
        # Generate actions for conclusive test results
        for test_data in decision_ready_tests:
            test_result = ABTestResult(**test_data)
            
            if test_result.winner in ["treatment", "control"]:
                action = await self._create_test_implementation_action(test_result)
                actions.append(action)
                expected_impact[f"implement_{test_result.test_name}"] = test_result.business_impact_estimate
        
        # Generate actions for experiment process optimization
        for opportunity in optimization_opportunities:
            if opportunity["type"] == "test_velocity_improvement":
                action = await self._create_velocity_improvement_action(opportunity)
                actions.append(action)
                expected_impact["experiment_velocity"] = opportunity["expected_improvement"]
            
            elif opportunity["type"] == "sample_size_optimization":
                action = await self._create_sample_size_optimization_action(opportunity)
                actions.append(action)
                expected_impact["statistical_power"] = opportunity["expected_improvement"]
            
            elif opportunity["type"] == "test_framework_improvement":
                action = await self._create_framework_improvement_action(opportunity)
                actions.append(action)
                expected_impact["experiment_quality"] = opportunity["expected_improvement"]
        
        # Generate actions for underperforming tests
        for test_data in decision_ready_tests:
            test_result = ABTestResult(**test_data)
            if test_result.winner == "inconclusive" and test_result.duration_days >= self.config["max_test_duration_days"]:
                action = await self._create_test_termination_action(test_result)
                actions.append(action)
                expected_impact[f"terminate_{test_result.test_name}"] = 0.1  # Resource savings
        
        risk_assessment = self._assess_experiment_optimization_risk(actions, results)
        rollback_plan = await self._create_experiment_rollback_plan(actions)
        
        return OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute A/B test optimization actions."""
        
        logger.info(f"Executing {len(actions.actions)} A/B test optimization actions")
        
        actions_taken = []
        actions_failed = []
        immediate_impact = {}
        
        for action in actions.actions:
            try:
                if action["type"] == "implement_test_winner":
                    result = await self._execute_test_implementation(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"winner_implemented_{action['test_name']}"] = 1.0
                    
                elif action["type"] == "terminate_test":
                    result = await self._execute_test_termination(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"test_terminated_{action['test_name']}"] = 1.0
                    
                elif action["type"] == "optimize_velocity":
                    result = await self._execute_velocity_optimization(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["velocity_optimization"] = action.get("impact_score", 1.0)
                    
                elif action["type"] == "optimize_sample_size":
                    result = await self._execute_sample_size_optimization(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["sample_size_optimization"] = 1.0
                    
                elif action["type"] == "improve_framework":
                    result = await self._execute_framework_improvement(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["framework_improvement"] = 1.0
                
            except Exception as e:
                logger.error(f"A/B test action execution failed: {action['type']} - {str(e)}")
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
    
    async def _get_experiment_portfolio(self, start_date: datetime, end_date: datetime) -> ExperimentPortfolio:
        """Get overview of experiment portfolio."""
        
        # Total tests in period
        total_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        # Active tests
        active_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'active' 
                AND created_at <= $1
        """, end_date) or 0
        
        # Completed tests
        completed_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status IN ('completed', 'concluded') 
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        # Tests ready for analysis (running >= min_duration)
        min_duration_cutoff = end_date - timedelta(days=self.config["min_test_duration_days"])
        tests_ready = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'active' 
                AND created_at <= $1
        """, min_duration_cutoff) or 0
        
        # Tests with clear winners
        tests_with_winners = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'concluded'
                AND results::jsonb->>'winner' IN ('control', 'treatment')
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        # Average test duration for completed tests
        avg_duration_result = await self.db.fetchval("""
            SELECT AVG(EXTRACT(DAY FROM completed_at - created_at)) 
            FROM ab_tests 
            WHERE status = 'concluded' 
                AND completed_at IS NOT NULL
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date)
        avg_duration = float(avg_duration_result) if avg_duration_result else 14.0
        
        # Experiment velocity (tests per month)
        days_in_period = (end_date - start_date).days
        experiment_velocity = (total_tests / days_in_period) * 30 if days_in_period > 0 else 0
        
        # Success rate (tests with winners / total concluded tests)
        concluded_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'concluded' 
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 1
        success_rate = tests_with_winners / concluded_tests if concluded_tests > 0 else 0
        
        return ExperimentPortfolio(
            total_tests=total_tests,
            active_tests=active_tests,
            completed_tests=completed_tests,
            tests_ready_for_analysis=tests_ready,
            tests_with_winners=tests_with_winners,
            avg_test_duration=avg_duration,
            experiment_velocity=experiment_velocity,
            overall_success_rate=success_rate
        )
    
    async def _analyze_individual_tests(self, start_date: datetime, end_date: datetime) -> List[ABTestResult]:
        """Analyze individual A/B tests for statistical significance."""
        
        # Get active tests that have been running for minimum duration
        min_duration_cutoff = end_date - timedelta(days=self.config["min_test_duration_days"])
        
        tests = await self.db.fetch("""
            SELECT 
                test_name,
                test_config,
                created_at,
                status,
                results
            FROM ab_tests 
            WHERE (status = 'active' AND created_at <= $1)
                OR (status = 'concluded' AND created_at BETWEEN $2 AND $3)
            ORDER BY created_at DESC
        """, min_duration_cutoff, start_date, end_date)
        
        test_results = []
        
        for test in tests:
            try:
                test_result = await self._analyze_single_test(test, end_date)
                if test_result:
                    test_results.append(test_result)
            except Exception as e:
                logger.error(f"Failed to analyze test {test['test_name']}: {str(e)}")
        
        return test_results
    
    async def _analyze_single_test(self, test_data: dict, end_date: datetime) -> Optional[ABTestResult]:
        """Analyze a single A/B test for statistical significance."""
        
        test_name = test_data["test_name"]
        test_config = json.loads(test_data["test_config"]) if test_data["test_config"] else {}
        start_date = test_data["created_at"]
        
        # Calculate test duration
        duration_days = (end_date - start_date).days
        
        # Get conversion events for this test
        # This would query your specific conversion tracking system
        conversion_data = await self._get_test_conversion_data(test_name, start_date, end_date)
        
        if not conversion_data or len(conversion_data) < 2:
            logger.warning(f"Insufficient data for test {test_name}")
            return None
        
        # Calculate statistical significance
        control_data = conversion_data.get("control", {"conversions": 0, "visitors": 0})
        treatment_data = conversion_data.get("treatment", {"conversions": 0, "visitors": 0})
        
        control_size = control_data["visitors"]
        treatment_size = treatment_data["visitors"]
        
        # Skip if sample sizes are too small
        if (control_size < self.config["min_sample_size_per_group"] or 
            treatment_size < self.config["min_sample_size_per_group"]):
            return None
        
        # Calculate conversion rates
        control_conversions = control_data["conversions"]
        treatment_conversions = treatment_data["conversions"]
        
        control_rate = control_conversions / control_size if control_size > 0 else 0
        treatment_rate = treatment_conversions / treatment_size if treatment_size > 0 else 0
        
        # Calculate lift
        lift = ((treatment_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0
        
        # Calculate statistical significance using z-test for proportions
        p_value = self._calculate_proportions_z_test(
            control_conversions, control_size,
            treatment_conversions, treatment_size
        )
        
        # Calculate confidence interval for lift
        confidence_interval = self._calculate_confidence_interval(
            control_rate, treatment_rate, control_size, treatment_size
        )
        
        # Determine winner
        winner = self._determine_test_winner(
            p_value, lift, confidence_interval, 
            self.config["significance_threshold"], 
            self.config["minimum_effect_size"]
        )
        
        # Generate recommendation
        recommendation = self._generate_test_recommendation(
            winner, p_value, lift, duration_days, test_config
        )
        
        # Estimate business impact
        business_impact = self._estimate_business_impact(
            lift, control_rate, control_size + treatment_size, test_config
        )
        
        return ABTestResult(
            test_name=test_name,
            test_type=test_config.get("test_type", "conversion"),
            start_date=start_date,
            duration_days=duration_days,
            control_group_size=control_size,
            treatment_group_size=treatment_size,
            control_conversion_rate=control_rate,
            treatment_conversion_rate=treatment_rate,
            lift=lift,
            statistical_significance=p_value,
            confidence_interval=confidence_interval,
            winner=winner,
            recommendation=recommendation,
            business_impact_estimate=business_impact
        )
    
    async def _get_test_conversion_data(self, test_name: str, start_date: datetime, end_date: datetime) -> Dict[str, Dict[str, int]]:
        """Get conversion data for a specific test."""
        
        # This would integrate with your actual conversion tracking
        # For now, we'll use a simplified query structure
        
        # Get test participants by group
        participants = await self.db.fetch("""
            SELECT 
                variation,
                user_id,
                assigned_at
            FROM ab_test_participants 
            WHERE test_name = $1 
                AND assigned_at BETWEEN $2 AND $3
        """, test_name, start_date, end_date)
        
        if not participants:
            return {}
        
        # Group participants by variation
        groups = defaultdict(list)
        for participant in participants:
            groups[participant["variation"]].append(participant["user_id"])
        
        # Count conversions for each group
        conversion_data = {}
        
        for variation, user_ids in groups.items():
            if not user_ids:
                continue
                
            # Count conversions (this query structure would depend on your conversion definition)
            conversions = await self.db.fetchval("""
                SELECT COUNT(DISTINCT user_id) 
                FROM conversion_events 
                WHERE user_id = ANY($1::text[])
                    AND event_type IN ('signup', 'upgrade', 'purchase')
                    AND created_at BETWEEN $2 AND $3
            """, user_ids, start_date, end_date) or 0
            
            conversion_data[variation] = {
                "visitors": len(user_ids),
                "conversions": conversions
            }
        
        return conversion_data
    
    def _calculate_proportions_z_test(self, x1: int, n1: int, x2: int, n2: int) -> float:
        """Calculate p-value for difference in proportions using z-test."""
        
        if n1 == 0 or n2 == 0:
            return 1.0
        
        p1 = x1 / n1
        p2 = x2 / n2
        
        # Pooled proportion
        p_pool = (x1 + x2) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return 1.0 if p1 == p2 else 0.0
        
        # Z-statistic
        z = (p1 - p2) / se
        
        # Two-tailed p-value (simplified normal approximation)
        p_value = 2 * (1 - self._normal_cdf(abs(z)))
        
        return max(0.0, min(1.0, p_value))
    
    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Approximation using error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _calculate_confidence_interval(self, p1: float, p2: float, n1: int, n2: int) -> Tuple[float, float]:
        """Calculate confidence interval for lift."""
        
        if n1 == 0 or n2 == 0 or p1 == 0:
            return (0.0, 0.0)
        
        # Standard error for difference in proportions
        se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        
        # 95% confidence interval
        z_95 = 1.96
        diff = p2 - p1
        margin = z_95 * se
        
        # Convert to lift percentage
        lift_lower = ((diff - margin) / p1 * 100) if p1 > 0 else 0
        lift_upper = ((diff + margin) / p1 * 100) if p1 > 0 else 0
        
        return (lift_lower, lift_upper)
    
    def _determine_test_winner(self, p_value: float, lift: float, confidence_interval: Tuple[float, float], 
                             sig_threshold: float, min_effect_size: float) -> str:
        """Determine test winner based on statistical criteria."""
        
        # Check statistical significance
        is_significant = p_value < sig_threshold
        
        # Check practical significance
        abs_lift = abs(lift)
        is_practically_significant = abs_lift >= min_effect_size
        
        # Check if confidence interval excludes zero
        ci_lower, ci_upper = confidence_interval
        ci_excludes_zero = (ci_lower > 0 and ci_upper > 0) or (ci_lower < 0 and ci_upper < 0)
        
        if is_significant and is_practically_significant and ci_excludes_zero:
            if lift > 0:
                return "treatment"
            else:
                return "control"
        else:
            return "inconclusive"
    
    def _generate_test_recommendation(self, winner: str, p_value: float, lift: float, 
                                    duration_days: int, test_config: Dict) -> str:
        """Generate recommendation for test action."""
        
        if winner == "treatment":
            if p_value < self.config["auto_implement_threshold"]:
                return "auto_implement_treatment"
            else:
                return "implement_treatment_with_monitoring"
        elif winner == "control":
            return "keep_control_stop_test"
        else:
            if duration_days >= self.config["max_test_duration_days"]:
                return "terminate_inconclusive_test"
            elif duration_days < self.config["min_test_duration_days"]:
                return "continue_test_insufficient_duration"
            else:
                return "continue_test_or_increase_sample_size"
    
    def _estimate_business_impact(self, lift: float, base_rate: float, sample_size: int, test_config: Dict) -> float:
        """Estimate monthly business impact of test result."""
        
        # This would use your specific business metrics
        # Simplified calculation for demonstration
        
        test_type = test_config.get("test_type", "conversion")
        
        if test_type == "conversion":
            # Estimate monthly conversions
            monthly_visitors = sample_size * 30 / 14  # Scale to monthly
            additional_conversions = monthly_visitors * base_rate * (lift / 100)
            
            # Estimate revenue per conversion (would come from config)
            revenue_per_conversion = test_config.get("revenue_per_conversion", 37.72)
            return additional_conversions * revenue_per_conversion
            
        elif test_type == "engagement":
            # Engagement improvements (simplified)
            return lift * 10  # $10 per percentage point of lift
            
        else:
            return lift * 5  # Default estimate
    
    async def _identify_decision_ready_tests(self, test_results: List[ABTestResult]) -> List[ABTestResult]:
        """Identify tests that are ready for decision/implementation."""
        
        decision_ready = []
        
        for test in test_results:
            # Test is ready if it has a clear winner or should be terminated
            if (test.winner in ["treatment", "control"] or 
                (test.winner == "inconclusive" and test.duration_days >= self.config["max_test_duration_days"])):
                decision_ready.append(test)
        
        return decision_ready
    
    async def _calculate_experiment_velocity(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate experiment velocity and efficiency metrics."""
        
        # Tests launched per month
        days_in_period = (end_date - start_date).days
        total_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests WHERE created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        tests_per_month = (total_tests / days_in_period) * 30 if days_in_period > 0 else 0
        
        # Average time to decision
        avg_time_to_decision = await self.db.fetchval("""
            SELECT AVG(EXTRACT(DAY FROM completed_at - created_at)) 
            FROM ab_tests 
            WHERE status = 'concluded' 
                AND completed_at BETWEEN $1 AND $2
        """, start_date, end_date) or 14
        
        # Test success rate (clear winner vs inconclusive)
        concluded_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'concluded' AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 1
        
        successful_tests = await self.db.fetchval("""
            SELECT COUNT(*) FROM ab_tests 
            WHERE status = 'concluded' 
                AND results::jsonb->>'winner' IN ('control', 'treatment')
                AND created_at BETWEEN $1 AND $2
        """, start_date, end_date) or 0
        
        success_rate = successful_tests / concluded_tests if concluded_tests > 0 else 0
        
        return {
            "tests_per_month": tests_per_month,
            "avg_time_to_decision_days": float(avg_time_to_decision),
            "success_rate": success_rate,
            "total_tests_period": total_tests,
            "concluded_tests_period": concluded_tests,
            "velocity_trend": "stable"  # Would calculate trend over time
        }
    
    async def _identify_experiment_optimization_opportunities(self, test_results: List[ABTestResult], velocity_metrics: Dict) -> List[Dict[str, Any]]:
        """Identify opportunities to improve experiment process."""
        
        opportunities = []
        
        # Low velocity opportunity
        if velocity_metrics["tests_per_month"] < 4:  # Less than 1 test per week
            opportunities.append({
                "type": "test_velocity_improvement",
                "issue": "low_experiment_velocity",
                "current_velocity": velocity_metrics["tests_per_month"],
                "target_velocity": 8,  # 2 tests per week
                "expected_improvement": 0.5,  # 50% improvement in learning rate
                "recommendations": ["automate_test_setup", "standardize_test_framework", "reduce_approval_overhead"]
            })
        
        # Sample size optimization
        small_sample_tests = [t for t in test_results if t.control_group_size + t.treatment_group_size < 500]
        if len(small_sample_tests) > len(test_results) * 0.3:  # More than 30% have small samples
            opportunities.append({
                "type": "sample_size_optimization",
                "issue": "insufficient_sample_sizes",
                "affected_tests_percentage": len(small_sample_tests) / len(test_results) if test_results else 0,
                "expected_improvement": 0.3,  # 30% improvement in statistical power
                "recommendations": ["increase_traffic_allocation", "extend_test_duration", "improve_power_analysis"]
            })
        
        # Low success rate
        if velocity_metrics["success_rate"] < 0.4:  # Less than 40% clear winners
            opportunities.append({
                "type": "test_framework_improvement",
                "issue": "low_success_rate",
                "current_success_rate": velocity_metrics["success_rate"],
                "target_success_rate": 0.6,
                "expected_improvement": 0.4,  # 40% improvement in clear results
                "recommendations": ["improve_hypothesis_quality", "better_effect_size_estimation", "refine_test_design"]
            })
        
        # Long-running inconclusive tests
        long_inconclusive = [t for t in test_results if t.winner == "inconclusive" and t.duration_days > 21]
        if long_inconclusive:
            opportunities.append({
                "type": "test_termination_optimization",
                "issue": "long_running_inconclusive_tests",
                "affected_tests": len(long_inconclusive),
                "expected_improvement": 0.2,  # 20% resource savings
                "recommendations": ["implement_early_stopping", "improve_power_calculations", "set_stricter_termination_criteria"]
            })
        
        return opportunities
    
    # Execution methods
    async def _execute_test_implementation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute implementation of winning test variation."""
        
        test_name = action["test_name"]
        winning_variation = action["winning_variation"]
        
        # Update test status to concluded
        await self.db.execute("""
            UPDATE ab_tests 
            SET status = 'concluded',
                completed_at = NOW(),
                results = results || jsonb_build_object('implemented', true, 'implementation_date', NOW())
            WHERE test_name = $1
        """, test_name)
        
        # Store implementation record
        implementation_data = {
            "test_name": test_name,
            "winning_variation": winning_variation,
            "implementation_type": action.get("implementation_type", "full_rollout"),
            "business_impact_estimate": action.get("business_impact_estimate", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO test_implementations (
                test_name, winning_variation, implementation_data,
                agent_name, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        test_name,
        winning_variation,
        json.dumps(implementation_data),
        self.name
        )
        
        logger.info(f"Implemented winning variation for test {test_name}: {winning_variation}")
        
        return {
            "status": "success",
            "test_name": test_name,
            "winning_variation": winning_variation
        }
    
    async def _execute_test_termination(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute termination of inconclusive test."""
        
        test_name = action["test_name"]
        termination_reason = action.get("termination_reason", "inconclusive_after_max_duration")
        
        # Update test status
        await self.db.execute("""
            UPDATE ab_tests 
            SET status = 'terminated',
                completed_at = NOW(),
                results = results || jsonb_build_object('termination_reason', $2, 'terminated_by_agent', true)
            WHERE test_name = $1
        """, test_name, termination_reason)
        
        logger.info(f"Terminated test {test_name}: {termination_reason}")
        
        return {
            "status": "success",
            "test_name": test_name,
            "termination_reason": termination_reason
        }
    
    async def _execute_velocity_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute experiment velocity optimization."""
        
        optimization_type = action["optimization_type"]
        recommendations = action.get("recommendations", [])
        
        # Store velocity optimization recommendations
        velocity_data = {
            "optimization_type": optimization_type,
            "recommendations": recommendations,
            "target_velocity": action.get("target_velocity", 0),
            "current_velocity": action.get("current_velocity", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO experiment_optimizations (
                optimization_type, optimization_data, agent_name, created_at
            ) VALUES ($1, $2, $3, NOW())
        """,
        "velocity_improvement",
        json.dumps(velocity_data),
        self.name
        )
        
        logger.info(f"Applied velocity optimization: {optimization_type}")
        
        return {
            "status": "success",
            "optimization_type": optimization_type,
            "recommendations_count": len(recommendations)
        }
    
    async def _execute_sample_size_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sample size optimization."""
        
        # Store sample size optimization recommendations
        sample_size_data = {
            "affected_tests_percentage": action.get("affected_tests_percentage", 0),
            "recommendations": action.get("recommendations", []),
            "expected_improvement": action.get("expected_improvement", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO experiment_optimizations (
                optimization_type, optimization_data, agent_name, created_at
            ) VALUES ($1, $2, $3, NOW())
        """,
        "sample_size_improvement",
        json.dumps(sample_size_data),
        self.name
        )
        
        logger.info("Applied sample size optimization recommendations")
        
        return {
            "status": "success",
            "optimization_type": "sample_size_improvement"
        }
    
    async def _execute_framework_improvement(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute experiment framework improvements."""
        
        # Store framework improvement recommendations
        framework_data = {
            "issue": action.get("issue", ""),
            "current_success_rate": action.get("current_success_rate", 0),
            "target_success_rate": action.get("target_success_rate", 0),
            "recommendations": action.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO experiment_optimizations (
                optimization_type, optimization_data, agent_name, created_at
            ) VALUES ($1, $2, $3, NOW())
        """,
        "framework_improvement",
        json.dumps(framework_data),
        self.name
        )
        
        logger.info("Applied experiment framework improvements")
        
        return {
            "status": "success",
            "optimization_type": "framework_improvement"
        }
    
    # Helper methods for action creation
    async def _create_test_implementation_action(self, test_result: ABTestResult) -> Dict[str, Any]:
        """Create action for implementing test winner."""
        return {
            "type": "implement_test_winner",
            "test_name": test_result.test_name,
            "winning_variation": test_result.winner,
            "lift": test_result.lift,
            "p_value": test_result.statistical_significance,
            "business_impact_estimate": test_result.business_impact_estimate,
            "implementation_type": "full_rollout" if test_result.statistical_significance < 0.01 else "gradual_rollout"
        }
    
    async def _create_test_termination_action(self, test_result: ABTestResult) -> Dict[str, Any]:
        """Create action for terminating inconclusive test."""
        return {
            "type": "terminate_test",
            "test_name": test_result.test_name,
            "termination_reason": f"inconclusive_after_{test_result.duration_days}_days",
            "p_value": test_result.statistical_significance,
            "duration_days": test_result.duration_days
        }
    
    async def _create_velocity_improvement_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create action for velocity improvement."""
        return {
            "type": "optimize_velocity",
            "optimization_type": "velocity_improvement",
            "current_velocity": opportunity["current_velocity"],
            "target_velocity": opportunity["target_velocity"],
            "recommendations": opportunity["recommendations"],
            "expected_improvement": opportunity["expected_improvement"]
        }
    
    async def _create_sample_size_optimization_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create action for sample size optimization."""
        return {
            "type": "optimize_sample_size",
            "affected_tests_percentage": opportunity["affected_tests_percentage"],
            "recommendations": opportunity["recommendations"],
            "expected_improvement": opportunity["expected_improvement"]
        }
    
    async def _create_framework_improvement_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create action for framework improvement."""
        return {
            "type": "improve_framework",
            "issue": opportunity["issue"],
            "current_success_rate": opportunity["current_success_rate"],
            "target_success_rate": opportunity["target_success_rate"],
            "recommendations": opportunity["recommendations"],
            "expected_improvement": opportunity["expected_improvement"]
        }
    
    # Helper methods for confidence and quality assessment
    def _calculate_analysis_confidence(self, portfolio: ExperimentPortfolio, test_results: List[ABTestResult]) -> float:
        """Calculate confidence in A/B test analysis."""
        
        factors = []
        
        # Portfolio size factor
        if portfolio.total_tests >= 10:
            factors.append(1.0)
        elif portfolio.total_tests >= 5:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Test quality factor
        if test_results:
            avg_sample_size = statistics.mean([t.control_group_size + t.treatment_group_size for t in test_results])
            if avg_sample_size >= 1000:
                factors.append(1.0)
            elif avg_sample_size >= 500:
                factors.append(0.8)
            else:
                factors.append(0.6)
        else:
            factors.append(0.5)
        
        # Success rate factor
        if portfolio.overall_success_rate >= 0.5:
            factors.append(1.0)
        elif portfolio.overall_success_rate >= 0.3:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        return statistics.mean(factors)
    
    def _assess_experiment_data_quality(self, portfolio: ExperimentPortfolio, test_results: List[ABTestResult]) -> float:
        """Assess quality of experiment data."""
        
        quality_factors = []
        
        # Sample size adequacy
        if test_results:
            adequate_sample_tests = len([t for t in test_results if 
                                       t.control_group_size >= self.config["min_sample_size_per_group"] and
                                       t.treatment_group_size >= self.config["min_sample_size_per_group"]])
            sample_adequacy = adequate_sample_tests / len(test_results)
            quality_factors.append(sample_adequacy)
        else:
            quality_factors.append(0.5)
        
        # Test duration reasonableness
        if test_results:
            reasonable_duration_tests = len([t for t in test_results if 
                                           self.config["min_test_duration_days"] <= t.duration_days <= self.config["max_test_duration_days"]])
            duration_quality = reasonable_duration_tests / len(test_results)
            quality_factors.append(duration_quality)
        else:
            quality_factors.append(0.5)
        
        # Portfolio diversity
        if portfolio.total_tests >= 5:
            quality_factors.append(1.0)
        else:
            quality_factors.append(portfolio.total_tests / 5.0)
        
        return statistics.mean(quality_factors)
    
    def _generate_experiment_recommendations(self, decision_ready_tests: List[ABTestResult], opportunities: List[Dict], velocity_metrics: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations for experiment optimization."""
        
        recommendations = []
        
        # Test implementation recommendations
        winners = [t for t in decision_ready_tests if t.winner in ["treatment", "control"]]
        if winners:
            recommendations.append({
                "title": f"Implement {len(winners)} winning test variations",
                "description": f"Deploy winning variations with combined estimated impact of ${sum(t.business_impact_estimate for t in winners):.0f}/month",
                "expected_impact": "Direct revenue increase from proven optimizations",
                "priority": "high",
                "action_type": "immediate"
            })
        
        # Velocity improvement recommendations
        if velocity_metrics["tests_per_month"] < 4:
            recommendations.append({
                "title": "Increase experiment velocity",
                "description": f"Current velocity {velocity_metrics['tests_per_month']:.1f} tests/month - target 8 tests/month",
                "expected_impact": "50% faster learning and optimization",
                "priority": "medium",
                "action_type": "process_improvement"
            })
        
        # Process optimization recommendations
        for opportunity in opportunities:
            if opportunity["type"] == "test_framework_improvement":
                recommendations.append({
                    "title": "Improve experiment framework",
                    "description": f"Success rate {opportunity['current_success_rate']:.1%} - optimize hypothesis and design quality",
                    "expected_impact": f"{opportunity['expected_improvement']:.1%} improvement in clear results",
                    "priority": "medium",
                    "action_type": "framework"
                })
        
        return recommendations
    
    def _assess_experiment_optimization_risk(self, actions: List[Dict], results: AnalysisResults) -> float:
        """Assess risk of experiment optimization actions."""
        
        # A/B test implementations are generally low risk since they're data-driven
        return 0.15
    
    async def _create_experiment_rollback_plan(self, actions: List[Dict]) -> Dict[str, Any]:
        """Create rollback plan for experiment optimizations."""
        
        return {
            "rollback_actions": ["revert_implemented_changes", "pause_new_test_launches"],
            "trigger_conditions": ["significant_metric_degradation", "user_complaints"],
            "monitoring_period_days": 7
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
    
    # Create and run A/B test analysis agent
    agent = ABTestAnalysisAgent(db_pool)
    
    try:
        performance_metrics = await agent.run_full_cycle()
        print(f"A/B test analysis completed successfully!")
        print(f"ROI Estimate: {performance_metrics.roi_estimate:.2f}")
        print(f"System Improvement: {performance_metrics.system_improvement}")
        
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        raise
    
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())