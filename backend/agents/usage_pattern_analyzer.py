#!/usr/bin/env python3
"""
USAGE PATTERN INTELLIGENCE AGENT
Optimizes word pool allocations based on actual usage patterns.

Schedule: Bi-weekly (1st & 15th) at 4 AM EST
Purpose: Reduce unused word allocations and improve tier progression  
Expected Impact: 25% reduction in unused allocations, improved tier progression
"""

import asyncio
import json
import logging
import statistics
# import numpy as np  # Using statistics instead for compatibility
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import asyncpg
from dataclasses import dataclass

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics
try:
    from ..word_pool_service import UserTier, WORD_LIMITS
except ImportError:
    # Fallback for testing
    from enum import Enum
    class UserTier(Enum):
        ANONYMOUS = "anonymous"
        FREE = "free"
        PRO = "pro"
        PARTNERSHIP = "partnership"
    WORD_LIMITS = {}

logger = logging.getLogger(__name__)

@dataclass
class UsagePattern:
    """Usage pattern for a specific tier and time period."""
    tier: UserTier
    time_period: str  # 'daily', 'weekly', 'monthly'
    avg_usage: float
    peak_usage: float
    usage_distribution: Dict[str, float]  # usage by time of day/week
    efficiency_score: float
    sample_size: int

@dataclass
class TierTransition:
    """Analysis of user transitions between tiers."""
    from_tier: UserTier
    to_tier: UserTier
    avg_time_to_transition: float
    transition_triggers: List[str]
    success_rate: float
    sample_size: int

class UsagePatternAnalyzer(BatchAgent):
    """Agent for analyzing usage patterns and optimizing word allocations."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="usage_pattern_analyzer",
            schedule_cron="0 4 1,15 * *",  # 4 AM on 1st and 15th of month
            data_sources=["user_word_usage", "users", "conversion_events"],
            db_pool=db_pool,
            config={
                "analysis_period_days": 14,
                "min_users_per_tier": 30,
                "efficiency_threshold": 0.6,  # 60% usage efficiency
                "peak_usage_percentile": 0.95,
                "transition_analysis_days": 30
            }
        )
    
    async def analyze(self) -> AnalysisResults:
        """Analyze usage patterns and efficiency across all tiers."""
        
        logger.info("Starting usage pattern analysis")
        
        # Define analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config["analysis_period_days"])
        
        # Analyze usage patterns by tier
        tier_patterns = await self._analyze_tier_usage_patterns(start_date, end_date)
        
        # Analyze tier transition patterns
        transition_patterns = await self._analyze_tier_transitions(start_date, end_date)
        
        # Analyze temporal usage patterns (time of day, day of week)
        temporal_patterns = await self._analyze_temporal_usage_patterns(start_date, end_date)
        
        # Calculate allocation efficiency
        allocation_efficiency = await self._calculate_allocation_efficiency(tier_patterns)
        
        # Identify optimization opportunities
        opportunities = await self._identify_usage_optimization_opportunities(
            tier_patterns, transition_patterns, allocation_efficiency
        )
        
        confidence_score = self._calculate_analysis_confidence(tier_patterns, transition_patterns)
        
        findings = {
            "tier_usage_patterns": {tier.value: pattern.__dict__ for tier, pattern in tier_patterns.items()},
            "transition_patterns": [t.__dict__ for t in transition_patterns],
            "temporal_patterns": temporal_patterns,
            "allocation_efficiency": allocation_efficiency,
            "optimization_opportunities": opportunities,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        recommendations = self._generate_usage_recommendations(opportunities, tier_patterns)
        
        return AnalysisResults(
            agent_name=self.name,
            analysis_period=(start_date, end_date),
            findings=findings,
            confidence_score=confidence_score,
            data_quality=self._assess_usage_data_quality(tier_patterns),
            recommendations=recommendations,
            raw_metrics={
                "overall_efficiency": allocation_efficiency.get("overall_efficiency", 0),
                "tier_count": len(tier_patterns),
                "transition_count": len(transition_patterns),
                "optimization_opportunities": len(opportunities)
            }
        )
    
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions for word pool allocations."""
        
        logger.info("Generating usage pattern optimization actions")
        
        opportunities = results.findings["optimization_opportunities"]
        tier_patterns = results.findings["tier_usage_patterns"]
        actions = []
        expected_impact = {}
        
        # Generate allocation adjustment actions
        for opportunity in opportunities:
            if opportunity["type"] == "allocation_adjustment":
                action = await self._create_allocation_adjustment_action(opportunity)
                actions.append(action)
                expected_impact[f"allocation_efficiency_{opportunity['tier']}"] = opportunity["expected_improvement"]
        
        # Generate tier progression optimization actions
        for opportunity in opportunities:
            if opportunity["type"] == "progression_optimization":
                action = await self._create_progression_optimization_action(opportunity)
                actions.append(action)
                expected_impact[f"progression_improvement_{opportunity['tier']}"] = opportunity["expected_improvement"]
        
        # Generate temporal optimization actions
        for opportunity in opportunities:
            if opportunity["type"] == "temporal_optimization":
                action = await self._create_temporal_optimization_action(opportunity)
                actions.append(action)
                expected_impact[f"temporal_efficiency"] = opportunity["expected_improvement"]
        
        risk_assessment = self._assess_usage_optimization_risk(actions, results)
        rollback_plan = await self._create_usage_rollback_plan(actions)
        
        return OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute usage pattern optimization actions."""
        
        logger.info(f"Executing {len(actions.actions)} usage optimization actions")
        
        actions_taken = []
        actions_failed = []
        immediate_impact = {}
        
        for action in actions.actions:
            try:
                if action["type"] == "allocation_adjustment":
                    result = await self._execute_allocation_adjustment(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"allocation_updated_{action['tier']}"] = 1.0
                    
                elif action["type"] == "progression_optimization":
                    result = await self._execute_progression_optimization(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"progression_updated_{action['tier']}"] = 1.0
                    
                elif action["type"] == "temporal_optimization":
                    result = await self._execute_temporal_optimization(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["temporal_optimization"] = action.get("impact_score", 1.0)
                
            except Exception as e:
                logger.error(f"Usage optimization action failed: {action['type']} - {str(e)}")
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
    
    async def _analyze_tier_usage_patterns(self, start_date: datetime, end_date: datetime) -> Dict[UserTier, UsagePattern]:
        """Analyze usage patterns for each tier."""
        
        tier_patterns = {}
        
        for tier in [UserTier.ANONYMOUS, UserTier.FREE, UserTier.PRO, UserTier.PARTNERSHIP]:
            
            # Get usage data for this tier
            usage_data = await self.db.fetch("""
                SELECT 
                    u.id as user_id,
                    uwu.usage_date,
                    SUM(uwo.word_count) as daily_usage,
                    COUNT(DISTINCT uwo.session_id) as sessions_count
                FROM users u
                JOIN user_word_usage uwo ON u.id = uwo.user_id
                LEFT JOIN user_word_usage uwo ON u.id = uwo.user_id AND uwo.usage_date = uwo.usage_date
                WHERE u.tier = $1 
                    AND uwo.usage_date BETWEEN $2 AND $3
                GROUP BY u.id, uwo.usage_date
                ORDER BY uwo.usage_date
            """, tier.value, start_date.date(), end_date.date())
            
            if not usage_data:
                continue
            
            # Calculate usage statistics
            daily_usages = [row["daily_usage"] for row in usage_data if row["daily_usage"]]
            
            if not daily_usages:
                continue
                
            avg_usage = statistics.mean(daily_usages)
            # Calculate percentile using statistics
            sorted_usages = sorted(daily_usages)
            percentile_index = int((self.config["peak_usage_percentile"] * len(sorted_usages)))
            peak_usage = sorted_usages[min(percentile_index, len(sorted_usages) - 1)]
            
            # Calculate efficiency (actual usage vs allocation)
            tier_limit = WORD_LIMITS.get(tier, {})
            if tier == UserTier.PARTNERSHIP:
                # For partnerships, use total allocation (personal + shared)
                allocated_limit = tier_limit.get("total_per_user", 20000)
            else:
                allocated_limit = tier_limit.get("daily_limit", tier_limit.get("monthly_limit", 1000))
                if tier_limit.get("period") == "monthly":
                    allocated_limit = allocated_limit / 30  # Convert to daily for comparison
            
            efficiency_score = avg_usage / allocated_limit if allocated_limit > 0 else 0
            
            # Analyze usage distribution (simplified - by day of week)
            usage_by_day = defaultdict(list)
            for row in usage_data:
                day_of_week = row["usage_date"].weekday()
                usage_by_day[day_of_week].append(row["daily_usage"])
            
            usage_distribution = {
                str(day): statistics.mean(usages) if usages else 0 
                for day, usages in usage_by_day.items()
            }
            
            tier_patterns[tier] = UsagePattern(
                tier=tier,
                time_period="daily",
                avg_usage=avg_usage,
                peak_usage=peak_usage,
                usage_distribution=usage_distribution,
                efficiency_score=efficiency_score,
                sample_size=len(set(row["user_id"] for row in usage_data))
            )
            
            logger.info(f"Analyzed {tier.value}: avg={avg_usage:.1f}, efficiency={efficiency_score:.2f}")
        
        return tier_patterns
    
    async def _analyze_tier_transitions(self, start_date: datetime, end_date: datetime) -> List[TierTransition]:
        """Analyze patterns in tier transitions."""
        
        # Get tier transition events
        transitions = await self.db.fetch("""
            SELECT 
                user_id,
                from_tier,
                to_tier,
                transition_date,
                trigger_event
            FROM tier_transition_history 
            WHERE transition_date BETWEEN $1 AND $2
            ORDER BY user_id, transition_date
        """, start_date, end_date)
        
        if not transitions:
            return []
        
        # Group transitions by tier pair
        transition_groups = defaultdict(list)
        for transition in transitions:
            key = (transition["from_tier"], transition["to_tier"])
            transition_groups[key].append(transition)
        
        transition_patterns = []
        
        for (from_tier, to_tier), group_transitions in transition_groups.items():
            if len(group_transitions) < 5:  # Skip small samples
                continue
            
            # Calculate transition timing
            transition_times = []
            triggers = []
            
            for transition in group_transitions:
                # Calculate time from user creation to transition (simplified)
                user_created = await self.db.fetchval("""
                    SELECT created_at FROM users WHERE id = $1
                """, transition["user_id"])
                
                if user_created:
                    time_to_transition = (transition["transition_date"] - user_created).total_seconds() / 86400  # days
                    transition_times.append(time_to_transition)
                
                if transition["trigger_event"]:
                    triggers.append(transition["trigger_event"])
            
            avg_time = statistics.mean(transition_times) if transition_times else 0
            success_rate = len(group_transitions) / len(set(t["user_id"] for t in group_transitions))
            
            # Count trigger types
            trigger_counts = Counter(triggers)
            top_triggers = [trigger for trigger, count in trigger_counts.most_common(3)]
            
            transition_patterns.append(TierTransition(
                from_tier=UserTier(from_tier),
                to_tier=UserTier(to_tier),
                avg_time_to_transition=avg_time,
                transition_triggers=top_triggers,
                success_rate=success_rate,
                sample_size=len(group_transitions)
            ))
        
        return transition_patterns
    
    async def _analyze_temporal_usage_patterns(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze usage patterns by time of day and day of week."""
        
        # Get hourly usage data
        hourly_usage = await self.db.fetch("""
            SELECT 
                EXTRACT(HOUR FROM created_at) as hour,
                EXTRACT(DOW FROM created_at) as day_of_week,
                COUNT(*) as usage_events,
                SUM(word_count) as total_words
            FROM user_word_usage 
            WHERE created_at BETWEEN $1 AND $2
            GROUP BY EXTRACT(HOUR FROM created_at), EXTRACT(DOW FROM created_at)
            ORDER BY day_of_week, hour
        """, start_date, end_date)
        
        # Organize by time patterns
        hourly_patterns = defaultdict(int)
        daily_patterns = defaultdict(int)
        
        for row in hourly_usage:
            hour = int(row["hour"])
            day_of_week = int(row["day_of_week"])
            word_count = row["total_words"]
            
            hourly_patterns[hour] += word_count
            daily_patterns[day_of_week] += word_count
        
        # Find peak usage times
        peak_hour = max(hourly_patterns.items(), key=lambda x: x[1])[0] if hourly_patterns else 0
        peak_day = max(daily_patterns.items(), key=lambda x: x[1])[0] if daily_patterns else 0
        
        # Calculate usage variance (how much usage varies by time)
        hourly_variance = statistics.variance(list(hourly_patterns.values())) if len(hourly_patterns) > 1 else 0
        daily_variance = statistics.variance(list(daily_patterns.values())) if len(daily_patterns) > 1 else 0
        
        return {
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "hourly_distribution": dict(hourly_patterns),
            "daily_distribution": dict(daily_patterns),
            "hourly_variance": float(hourly_variance),
            "daily_variance": float(daily_variance),
            "usage_concentration": {
                "hour": max(hourly_patterns.values()) / sum(hourly_patterns.values()) if hourly_patterns else 0,
                "day": max(daily_patterns.values()) / sum(daily_patterns.values()) if daily_patterns else 0
            }
        }
    
    async def _calculate_allocation_efficiency(self, tier_patterns: Dict[UserTier, UsagePattern]) -> Dict[str, float]:
        """Calculate overall allocation efficiency metrics."""
        
        efficiency_scores = []
        unutilized_allocations = []
        
        for tier, pattern in tier_patterns.items():
            efficiency_scores.append(pattern.efficiency_score)
            
            # Calculate unutilized allocation percentage
            unutilized = max(0, 1 - pattern.efficiency_score)
            unutilized_allocations.append(unutilized)
        
        overall_efficiency = statistics.mean(efficiency_scores) if efficiency_scores else 0
        avg_unutilized = statistics.mean(unutilized_allocations) if unutilized_allocations else 0
        
        # Calculate potential savings
        total_allocated_words = 0
        total_used_words = 0
        
        for tier, pattern in tier_patterns.items():
            tier_limit = WORD_LIMITS.get(tier, {})
            if tier == UserTier.PARTNERSHIP:
                daily_limit = tier_limit.get("total_per_user", 20000) / 30
            else:
                daily_limit = tier_limit.get("daily_limit", tier_limit.get("monthly_limit", 1000))
                if tier_limit.get("period") == "monthly":
                    daily_limit = daily_limit / 30
            
            allocated_words = daily_limit * pattern.sample_size
            used_words = pattern.avg_usage * pattern.sample_size
            
            total_allocated_words += allocated_words
            total_used_words += used_words
        
        potential_savings = (total_allocated_words - total_used_words) / total_allocated_words if total_allocated_words > 0 else 0
        
        return {
            "overall_efficiency": overall_efficiency,
            "avg_unutilized_percentage": avg_unutilized,
            "potential_savings_percentage": potential_savings,
            "efficiency_by_tier": {tier.value: pattern.efficiency_score for tier, pattern in tier_patterns.items()}
        }
    
    async def _identify_usage_optimization_opportunities(
        self, 
        tier_patterns: Dict[UserTier, UsagePattern],
        transition_patterns: List[TierTransition],
        allocation_efficiency: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities."""
        
        opportunities = []
        
        # Identify overallocated tiers
        for tier, pattern in tier_patterns.items():
            if pattern.efficiency_score < self.config["efficiency_threshold"]:
                # Calculate optimal allocation
                optimal_allocation = pattern.peak_usage * 1.1  # 10% buffer above peak
                current_allocation = WORD_LIMITS.get(tier, {}).get("daily_limit", 0)
                if tier == UserTier.PRO or tier == UserTier.PARTNERSHIP:
                    current_allocation = WORD_LIMITS.get(tier, {}).get("monthly_limit", 0) / 30
                
                if optimal_allocation < current_allocation * 0.8:  # Significant reduction possible
                    opportunities.append({
                        "type": "allocation_adjustment",
                        "tier": tier.value,
                        "current_allocation": current_allocation,
                        "recommended_allocation": optimal_allocation,
                        "expected_improvement": (current_allocation - optimal_allocation) / current_allocation,
                        "confidence": "high" if pattern.sample_size > 50 else "medium",
                        "efficiency_gain": (optimal_allocation / pattern.avg_usage) - pattern.efficiency_score
                    })
        
        # Identify tier progression optimization opportunities
        for transition in transition_patterns:
            if transition.avg_time_to_transition > 14:  # More than 2 weeks to upgrade
                opportunities.append({
                    "type": "progression_optimization",
                    "from_tier": transition.from_tier.value,
                    "to_tier": transition.to_tier.value,
                    "current_avg_time": transition.avg_time_to_transition,
                    "recommended_triggers": transition.transition_triggers,
                    "expected_improvement": 0.3,  # 30% reduction in transition time
                    "confidence": "medium"
                })
        
        # Identify temporal optimization opportunities
        temporal_patterns = await self._analyze_temporal_usage_patterns(
            datetime.now() - timedelta(days=self.config["analysis_period_days"]),
            datetime.now()
        )
        
        # High usage concentration suggests potential for load balancing
        if temporal_patterns["usage_concentration"]["hour"] > 0.3:  # More than 30% usage in single hour
            opportunities.append({
                "type": "temporal_optimization",
                "optimization_target": "load_balancing",
                "peak_hour": temporal_patterns["peak_hour"],
                "concentration_level": temporal_patterns["usage_concentration"]["hour"],
                "expected_improvement": 0.2,
                "confidence": "medium"
            })
        
        return opportunities
    
    async def _execute_allocation_adjustment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute word allocation adjustment."""
        
        tier = UserTier(action["tier"])
        new_allocation = action["recommended_allocation"]
        old_allocation = action["current_allocation"]
        
        # Update word limits configuration
        if tier in WORD_LIMITS:
            if WORD_LIMITS[tier].get("period") == "daily":
                WORD_LIMITS[tier]["daily_limit"] = int(new_allocation)
            else:
                WORD_LIMITS[tier]["monthly_limit"] = int(new_allocation * 30)
            
            logger.info(f"Updated {tier.value} allocation: {old_allocation} → {new_allocation}")
            
            # Store configuration change
            await self.db.execute("""
                INSERT INTO agent_configuration_changes (
                    agent_name, change_type, change_data, created_at
                ) VALUES ($1, $2, $3, NOW())
            """,
            self.name,
            "allocation_adjustment",
            json.dumps({
                "tier": tier.value,
                "old_allocation": old_allocation,
                "new_allocation": new_allocation,
                "expected_savings": action.get("expected_improvement", 0)
            })
            )
            
            return {
                "status": "success",
                "tier": tier.value,
                "old_allocation": old_allocation,
                "new_allocation": new_allocation
            }
        
        return {"status": "failed", "reason": "tier_not_found"}
    
    async def _execute_progression_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tier progression optimization."""
        
        # Store progression optimization recommendations
        optimization_data = {
            "from_tier": action["from_tier"],
            "to_tier": action["to_tier"],
            "current_avg_time": action["current_avg_time"],
            "recommended_triggers": action["recommended_triggers"],
            "optimization_type": "progression_acceleration"
        }
        
        await self.db.execute("""
            INSERT INTO progression_optimizations (
                from_tier, to_tier, optimization_data, agent_name, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        action["from_tier"],
        action["to_tier"],
        json.dumps(optimization_data),
        self.name
        )
        
        logger.info(f"Optimized progression: {action['from_tier']} → {action['to_tier']}")
        
        return {
            "status": "success",
            "optimization_id": f"prog_{int(datetime.now().timestamp())}"
        }
    
    async def _execute_temporal_optimization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute temporal usage optimization."""
        
        # Store temporal optimization event
        temporal_data = {
            "optimization_target": action["optimization_target"],
            "peak_hour": action["peak_hour"],
            "concentration_level": action["concentration_level"],
            "recommendations": ["implement_usage_incentives_off_peak", "load_balancing_suggestions"],
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO temporal_optimizations (
                optimization_type, optimization_data, agent_name, created_at
            ) VALUES ($1, $2, $3, NOW())
        """,
        action["optimization_target"],
        json.dumps(temporal_data),
        self.name
        )
        
        logger.info(f"Executed temporal optimization: {action['optimization_target']}")
        
        return {
            "status": "success",
            "optimization_type": action["optimization_target"]
        }
    
    def _calculate_analysis_confidence(
        self, 
        tier_patterns: Dict[UserTier, UsagePattern],
        transition_patterns: List[TierTransition]
    ) -> float:
        """Calculate confidence in usage analysis."""
        
        factors = []
        
        # Sample size factor
        total_users = sum(pattern.sample_size for pattern in tier_patterns.values())
        if total_users >= 500:
            factors.append(1.0)
        elif total_users >= 100:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Tier coverage factor
        tier_coverage = len(tier_patterns) / len(UserTier)
        factors.append(tier_coverage)
        
        # Data consistency factor
        efficiency_scores = [p.efficiency_score for p in tier_patterns.values()]
        if efficiency_scores:
            consistency = 1 - (statistics.stdev(efficiency_scores) / statistics.mean(efficiency_scores))
            factors.append(max(0.5, consistency))
        else:
            factors.append(0.5)
        
        return statistics.mean(factors)
    
    def _assess_usage_data_quality(self, tier_patterns: Dict[UserTier, UsagePattern]) -> float:
        """Assess quality of usage pattern data."""
        
        quality_factors = []
        
        # Sample size adequacy per tier
        for pattern in tier_patterns.values():
            if pattern.sample_size >= 50:
                quality_factors.append(1.0)
            elif pattern.sample_size >= 20:
                quality_factors.append(0.8)
            else:
                quality_factors.append(0.5)
        
        # Usage pattern reasonableness
        for pattern in tier_patterns.values():
            if 0.1 <= pattern.efficiency_score <= 1.5:  # Reasonable efficiency range
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.6)
        
        return statistics.mean(quality_factors) if quality_factors else 0.5
    
    def _generate_usage_recommendations(
        self, 
        opportunities: List[Dict[str, Any]], 
        tier_patterns: Dict[str, UsagePattern]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations for usage optimization."""
        
        recommendations = []
        
        for opp in opportunities:
            if opp["type"] == "allocation_adjustment":
                recommendations.append({
                    "title": f"Optimize {opp['tier']} word allocation",
                    "description": f"Reduce allocation from {opp['current_allocation']:.0f} to {opp['recommended_allocation']:.0f} words",
                    "expected_impact": f"{opp['expected_improvement']:.1%} efficiency improvement",
                    "confidence": opp["confidence"],
                    "action_type": "immediate",
                    "priority": "high"
                })
            
            elif opp["type"] == "progression_optimization":
                recommendations.append({
                    "title": f"Accelerate {opp['from_tier']} → {opp['to_tier']} progression",
                    "description": f"Reduce average transition time from {opp['current_avg_time']:.1f} days",
                    "expected_impact": f"{opp['expected_improvement']:.1%} faster conversions",
                    "confidence": opp["confidence"],
                    "action_type": "strategic",
                    "priority": "medium"
                })
            
            elif opp["type"] == "temporal_optimization":
                recommendations.append({
                    "title": "Optimize usage timing distribution",
                    "description": f"Balance peak hour usage (currently {opp['concentration_level']:.1%} at hour {opp['peak_hour']})",
                    "expected_impact": "Improved system performance and user experience",
                    "confidence": opp["confidence"],
                    "action_type": "gradual",
                    "priority": "low"
                })
        
        return recommendations
    
    def _assess_usage_optimization_risk(self, actions: List[Dict[str, Any]], results: AnalysisResults) -> float:
        """Assess risk of usage optimization actions."""
        
        risk_factors = []
        
        # Data quality risk
        data_quality = results.data_quality
        risk_factors.append(1 - data_quality)
        
        # Sample size risk
        total_opportunities = results.raw_metrics.get("optimization_opportunities", 0)
        if total_opportunities > 5:
            risk_factors.append(0.6)  # High number of changes = higher risk
        else:
            risk_factors.append(0.2)
        
        # Allocation reduction risk
        allocation_reductions = [a for a in actions if a.get("type") == "allocation_adjustment"]
        if len(allocation_reductions) > 2:
            risk_factors.append(0.5)  # Multiple tier changes = medium risk
        else:
            risk_factors.append(0.1)
        
        return statistics.mean(risk_factors)
    
    async def _create_usage_rollback_plan(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create rollback plan for usage optimization actions."""
        
        rollback_actions = []
        
        for action in actions:
            if action.get("type") == "allocation_adjustment":
                rollback_actions.append({
                    "action": "restore_allocation",
                    "tier": action["tier"],
                    "restore_to": action.get("current_allocation"),
                    "trigger": "user_complaints_or_usage_spikes"
                })
        
        return {
            "rollback_actions": rollback_actions,
            "trigger_conditions": [
                "user_hit_limits_significantly_more",
                "conversion_rates_drop",
                "user_satisfaction_scores_decline"
            ],
            "monitoring_period_days": 14
        }
    
    # Additional placeholder methods for completeness
    async def _create_allocation_adjustment_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "allocation_adjustment", **opportunity}
    
    async def _create_progression_optimization_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "progression_optimization", **opportunity}
    
    async def _create_temporal_optimization_action(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        return {"type": "temporal_optimization", **opportunity}


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
    
    # Create and run usage pattern analyzer agent
    agent = UsagePatternAnalyzer(db_pool)
    
    try:
        performance_metrics = await agent.run_full_cycle()
        print(f"Usage pattern analysis completed successfully!")
        print(f"ROI Estimate: {performance_metrics.roi_estimate:.2f}")
        print(f"System Improvement: {performance_metrics.system_improvement}")
        
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        raise
    
    finally:
        await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())