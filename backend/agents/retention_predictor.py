#!/usr/bin/env python3
"""
RETENTION PREDICTION AGENT
Identifies users at risk of churning and triggers retention interventions.

Schedule: Daily at 1 AM EST
Purpose: Identify churn risk and implement retention strategies
Expected Impact: 30% improvement in 30-day retention rates
"""

import asyncio
import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import asyncpg
from dataclasses import dataclass

from .base_agent import BatchAgent, AnalysisResults, OptimizationActions, ExecutionReport, PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class UserRiskProfile:
    """Risk profile for a specific user."""
    user_id: str
    tier: str
    risk_score: float  # 0-1, higher = more likely to churn
    risk_factors: List[str]
    last_activity: datetime
    days_since_signup: int
    usage_trend: str  # 'increasing', 'stable', 'declining'
    engagement_score: float
    intervention_recommendations: List[str]

@dataclass
class RetentionMetrics:
    """Overall retention metrics for analysis."""
    total_users: int
    at_risk_users: int
    high_risk_users: int
    recent_churned_users: int
    retention_rate_7_day: float
    retention_rate_30_day: float
    avg_risk_score: float
    risk_distribution: Dict[str, int]

class RetentionPredictionAgent(BatchAgent):
    """Agent for predicting user churn and implementing retention strategies."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        super().__init__(
            name="retention_predictor",
            schedule_cron="0 1 * * *",  # 1 AM daily
            data_sources=["users", "user_word_usage", "user_activity_log", "conversion_events"],
            db_pool=db_pool,
            config={
                "analysis_period_days": 30,
                "risk_threshold_medium": 0.5,
                "risk_threshold_high": 0.75,
                "min_activity_days": 3,  # Minimum days since signup to analyze
                "churn_definition_days": 14,  # Consider churned if inactive for 14 days
                "intervention_cooldown_days": 7  # Don't re-intervene within 7 days
            }
        )
    
    async def analyze(self) -> AnalysisResults:
        """Analyze user behavior patterns to predict churn risk."""
        
        logger.info("Starting retention prediction analysis")
        
        # Define analysis period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.config["analysis_period_days"])
        
        # Get user risk profiles
        user_risk_profiles = await self._calculate_user_risk_profiles(start_date, end_date)
        
        # Calculate overall retention metrics
        retention_metrics = await self._calculate_retention_metrics(user_risk_profiles, start_date, end_date)
        
        # Identify intervention opportunities
        intervention_opportunities = await self._identify_intervention_opportunities(user_risk_profiles)
        
        # Analyze churn patterns
        churn_patterns = await self._analyze_churn_patterns(start_date, end_date)
        
        confidence_score = self._calculate_prediction_confidence(retention_metrics, user_risk_profiles)
        
        findings = {
            "retention_metrics": retention_metrics.__dict__,
            "high_risk_users": [profile.__dict__ for profile in user_risk_profiles if profile.risk_score >= self.config["risk_threshold_high"]],
            "medium_risk_users": [profile.__dict__ for profile in user_risk_profiles if self.config["risk_threshold_medium"] <= profile.risk_score < self.config["risk_threshold_high"]],
            "intervention_opportunities": intervention_opportunities,
            "churn_patterns": churn_patterns,
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
        recommendations = self._generate_retention_recommendations(
            retention_metrics, intervention_opportunities, churn_patterns
        )
        
        return AnalysisResults(
            agent_name=self.name,
            analysis_period=(start_date, end_date),
            findings=findings,
            confidence_score=confidence_score,
            data_quality=self._assess_retention_data_quality(retention_metrics, user_risk_profiles),
            recommendations=recommendations,
            raw_metrics={
                "total_users_analyzed": retention_metrics.total_users,
                "at_risk_users": retention_metrics.at_risk_users,
                "high_risk_users": retention_metrics.high_risk_users,
                "avg_risk_score": retention_metrics.avg_risk_score,
                "retention_rate_30_day": retention_metrics.retention_rate_30_day
            }
        )
    
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions for retention improvement."""
        
        logger.info("Generating retention optimization actions")
        
        intervention_opportunities = results.findings["intervention_opportunities"]
        high_risk_users = results.findings["high_risk_users"]
        churn_patterns = results.findings["churn_patterns"]
        
        actions = []
        expected_impact = {}
        
        # Generate personalized intervention actions for high-risk users
        for user_profile in high_risk_users:
            action = await self._create_personalized_intervention_action(user_profile)
            actions.append(action)
            expected_impact[f"intervention_{user_profile['user_id']}"] = 0.4  # 40% reduction in churn risk
        
        # Generate cohort-based intervention actions
        for opportunity in intervention_opportunities:
            if opportunity["type"] == "cohort_intervention":
                action = await self._create_cohort_intervention_action(opportunity)
                actions.append(action)
                expected_impact[f"cohort_intervention_{opportunity['cohort']}"] = opportunity["expected_improvement"]
        
        # Generate feature engagement actions
        for opportunity in intervention_opportunities:
            if opportunity["type"] == "feature_engagement":
                action = await self._create_feature_engagement_action(opportunity)
                actions.append(action)
                expected_impact[f"feature_engagement_{opportunity['feature']}"] = opportunity["expected_improvement"]
        
        # Generate early warning system actions
        if churn_patterns:
            early_warning_action = await self._create_early_warning_action(churn_patterns)
            actions.append(early_warning_action)
            expected_impact["early_warning_system"] = 0.25  # 25% better churn prediction
        
        risk_assessment = self._assess_retention_optimization_risk(actions, results)
        rollback_plan = await self._create_retention_rollback_plan(actions)
        
        return OptimizationActions(
            agent_name=self.name,
            actions=actions,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            rollback_plan=rollback_plan
        )
    
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute retention optimization actions."""
        
        logger.info(f"Executing {len(actions.actions)} retention optimization actions")
        
        actions_taken = []
        actions_failed = []
        immediate_impact = {}
        
        for action in actions.actions:
            try:
                if action["type"] == "personalized_intervention":
                    result = await self._execute_personalized_intervention(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"intervention_sent_{action['user_id']}"] = 1.0
                    
                elif action["type"] == "cohort_intervention":
                    result = await self._execute_cohort_intervention(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"cohort_campaign_{action['cohort']}"] = len(action.get("target_users", []))
                    
                elif action["type"] == "feature_engagement":
                    result = await self._execute_feature_engagement(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact[f"engagement_campaign_{action['feature']}"] = 1.0
                    
                elif action["type"] == "early_warning_system":
                    result = await self._execute_early_warning_system(action)
                    actions_taken.append({"action": action, "result": result})
                    immediate_impact["early_warning_implemented"] = 1.0
                
            except Exception as e:
                logger.error(f"Retention action execution failed: {action['type']} - {str(e)}")
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
    
    async def _calculate_user_risk_profiles(self, start_date: datetime, end_date: datetime) -> List[UserRiskProfile]:
        """Calculate churn risk profiles for all active users."""
        
        # Get users who have been active in analysis period or recently churned
        users_data = await self.db.fetch("""
            SELECT 
                u.id,
                u.tier,
                u.created_at,
                u.last_login,
                COALESCE(recent_activity.last_activity, u.last_login) as last_activity,
                COALESCE(usage_stats.total_words, 0) as total_words_period,
                COALESCE(usage_stats.active_days, 0) as active_days_period,
                COALESCE(usage_stats.avg_daily_words, 0) as avg_daily_words
            FROM users u
            LEFT JOIN (
                SELECT 
                    user_id,
                    MAX(created_at) as last_activity
                FROM user_word_usage 
                WHERE created_at >= $1
                GROUP BY user_id
            ) recent_activity ON u.id = recent_activity.user_id
            LEFT JOIN (
                SELECT 
                    user_id,
                    SUM(word_count) as total_words,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    AVG(word_count) as avg_daily_words
                FROM user_word_usage 
                WHERE created_at BETWEEN $1 AND $2
                GROUP BY user_id
            ) usage_stats ON u.id = usage_stats.user_id
            WHERE u.created_at <= $2 - INTERVAL '{} days'
            ORDER BY u.created_at DESC
            LIMIT 1000
        """.format(self.config["min_activity_days"]), start_date, end_date)
        
        risk_profiles = []
        
        for user in users_data:
            risk_profile = await self._calculate_individual_risk_score(user, start_date, end_date)
            if risk_profile:
                risk_profiles.append(risk_profile)
        
        return risk_profiles
    
    async def _calculate_individual_risk_score(self, user_data: dict, start_date: datetime, end_date: datetime) -> Optional[UserRiskProfile]:
        """Calculate churn risk score for individual user."""
        
        user_id = user_data["id"]
        tier = user_data["tier"]
        created_at = user_data["created_at"]
        last_activity = user_data["last_activity"] or user_data["created_at"]
        
        # Calculate time-based factors
        days_since_signup = (end_date - created_at).days
        days_since_activity = (end_date - last_activity).days
        
        # Skip very new users (less than minimum activity days)
        if days_since_signup < self.config["min_activity_days"]:
            return None
        
        risk_factors = []
        risk_score = 0.0
        
        # Activity recency factor (0.4 weight)
        if days_since_activity >= self.config["churn_definition_days"]:
            risk_score += 0.4
            risk_factors.append("inactive_user")
        elif days_since_activity >= 7:
            risk_score += 0.2
            risk_factors.append("declining_activity")
        elif days_since_activity >= 3:
            risk_score += 0.1
            risk_factors.append("reduced_activity")
        
        # Usage trend factor (0.3 weight)
        usage_trend = await self._calculate_usage_trend(user_id, start_date, end_date)
        if usage_trend == "declining":
            risk_score += 0.3
            risk_factors.append("declining_usage")
        elif usage_trend == "stable":
            risk_score += 0.1
            risk_factors.append("stable_usage")
        # Increasing usage gets 0 additional risk
        
        # Engagement factor (0.2 weight)
        engagement_score = await self._calculate_engagement_score(user_id, start_date, end_date)
        if engagement_score < 0.3:
            risk_score += 0.2
            risk_factors.append("low_engagement")
        elif engagement_score < 0.6:
            risk_score += 0.1
            risk_factors.append("medium_engagement")
        
        # Tier-specific factors (0.1 weight)
        if tier == "anonymous":
            risk_score += 0.1
            risk_factors.append("anonymous_user")
        elif tier == "free" and days_since_signup > 30:
            risk_score += 0.05
            risk_factors.append("long_term_free")
        
        # Generate intervention recommendations
        recommendations = self._generate_intervention_recommendations(risk_factors, tier, engagement_score)
        
        return UserRiskProfile(
            user_id=user_id,
            tier=tier,
            risk_score=min(1.0, risk_score),  # Cap at 1.0
            risk_factors=risk_factors,
            last_activity=last_activity,
            days_since_signup=days_since_signup,
            usage_trend=usage_trend,
            engagement_score=engagement_score,
            intervention_recommendations=recommendations
        )
    
    async def _calculate_usage_trend(self, user_id: str, start_date: datetime, end_date: datetime) -> str:
        """Calculate whether user's usage is increasing, stable, or declining."""
        
        # Get weekly usage data
        weekly_usage = await self.db.fetch("""
            SELECT 
                DATE_TRUNC('week', created_at) as week,
                SUM(word_count) as weekly_words
            FROM user_word_usage 
            WHERE user_id = $1 
                AND created_at BETWEEN $2 AND $3
            GROUP BY DATE_TRUNC('week', created_at)
            ORDER BY week
        """, user_id, start_date, end_date)
        
        if len(weekly_usage) < 2:
            return "insufficient_data"
        
        # Calculate trend using simple linear regression
        word_counts = [row["weekly_words"] for row in weekly_usage]
        
        if len(word_counts) >= 3:
            # Compare first half vs second half
            mid_point = len(word_counts) // 2
            first_half_avg = statistics.mean(word_counts[:mid_point])
            second_half_avg = statistics.mean(word_counts[mid_point:])
            
            if second_half_avg > first_half_avg * 1.2:
                return "increasing"
            elif second_half_avg < first_half_avg * 0.8:
                return "declining"
            else:
                return "stable"
        else:
            # Simple comparison for small datasets
            if word_counts[-1] > word_counts[0] * 1.2:
                return "increasing"
            elif word_counts[-1] < word_counts[0] * 0.8:
                return "declining"
            else:
                return "stable"
    
    async def _calculate_engagement_score(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate user engagement score based on feature usage."""
        
        engagement_factors = {}
        
        # Analysis frequency
        analysis_count = await self.db.fetchval("""
            SELECT COUNT(*) FROM lncp_analysis_results 
            WHERE writing_sample_id IN (
                SELECT id FROM writing_samples WHERE user_id = $1
            ) AND created_at BETWEEN $2 AND $3
        """, user_id, start_date, end_date) or 0
        engagement_factors["analysis_frequency"] = min(1.0, analysis_count / 10.0)  # Max at 10 analyses
        
        # Feature gate interactions
        feature_interactions = await self.db.fetchval("""
            SELECT COUNT(*) FROM feature_gate_logs 
            WHERE user_id = $1 
                AND created_at BETWEEN $2 AND $3
                AND action = 'access_granted'
        """, user_id, start_date, end_date) or 0
        engagement_factors["feature_usage"] = min(1.0, feature_interactions / 20.0)  # Max at 20 interactions
        
        # Writing consistency (days with activity)
        active_days = await self.db.fetchval("""
            SELECT COUNT(DISTINCT DATE(created_at)) FROM user_word_usage 
            WHERE user_id = $1 AND created_at BETWEEN $2 AND $3
        """, user_id, start_date, end_date) or 0
        expected_days = (end_date - start_date).days
        engagement_factors["consistency"] = min(1.0, (active_days / expected_days) * 2)  # Max if active 50% of days
        
        # Word count relative to tier
        total_words = await self.db.fetchval("""
            SELECT SUM(word_count) FROM user_word_usage 
            WHERE user_id = $1 AND created_at BETWEEN $2 AND $3
        """, user_id, start_date, end_date) or 0
        
        # Tier expectations (rough estimates)
        tier_expectations = {"anonymous": 500, "free": 2000, "pro": 10000, "partnership": 15000}
        user_tier = await self.db.fetchval("SELECT tier FROM users WHERE id = $1", user_id) or "anonymous"
        expected_words = tier_expectations.get(user_tier, 1000)
        engagement_factors["usage_volume"] = min(1.0, total_words / expected_words)
        
        # Calculate weighted engagement score
        weights = {
            "analysis_frequency": 0.3,
            "feature_usage": 0.2,
            "consistency": 0.3,
            "usage_volume": 0.2
        }
        
        engagement_score = sum(
            engagement_factors[factor] * weights[factor] 
            for factor in engagement_factors
        )
        
        return engagement_score
    
    def _generate_intervention_recommendations(self, risk_factors: List[str], tier: str, engagement_score: float) -> List[str]:
        """Generate specific intervention recommendations based on risk factors."""
        
        recommendations = []
        
        if "inactive_user" in risk_factors:
            recommendations.append("win_back_email_campaign")
            recommendations.append("feature_showcase_notification")
            
        if "declining_usage" in risk_factors:
            recommendations.append("usage_motivation_email")
            recommendations.append("writing_challenge_invitation")
            
        if "low_engagement" in risk_factors:
            recommendations.append("onboarding_refresher")
            recommendations.append("feature_discovery_tour")
            
        if tier == "anonymous" and engagement_score > 0.5:
            recommendations.append("signup_incentive")
            
        if tier == "free" and engagement_score > 0.7:
            recommendations.append("pro_upgrade_offer")
            
        if "long_term_free" in risk_factors:
            recommendations.append("value_demonstration")
            recommendations.append("social_proof_messaging")
        
        return recommendations
    
    async def _calculate_retention_metrics(self, risk_profiles: List[UserRiskProfile], start_date: datetime, end_date: datetime) -> RetentionMetrics:
        """Calculate overall retention metrics."""
        
        total_users = len(risk_profiles)
        at_risk_users = len([p for p in risk_profiles if p.risk_score >= self.config["risk_threshold_medium"]])
        high_risk_users = len([p for p in risk_profiles if p.risk_score >= self.config["risk_threshold_high"]])
        
        # Calculate retention rates
        retention_7_day = await self._calculate_retention_rate(7, end_date)
        retention_30_day = await self._calculate_retention_rate(30, end_date)
        
        # Recent churned users (inactive for churn_definition_days)
        churned_users = len([p for p in risk_profiles if 
            (end_date - p.last_activity).days >= self.config["churn_definition_days"]])
        
        avg_risk_score = statistics.mean([p.risk_score for p in risk_profiles]) if risk_profiles else 0
        
        # Risk distribution
        risk_distribution = {
            "low": len([p for p in risk_profiles if p.risk_score < self.config["risk_threshold_medium"]]),
            "medium": len([p for p in risk_profiles if self.config["risk_threshold_medium"] <= p.risk_score < self.config["risk_threshold_high"]]),
            "high": high_risk_users
        }
        
        return RetentionMetrics(
            total_users=total_users,
            at_risk_users=at_risk_users,
            high_risk_users=high_risk_users,
            recent_churned_users=churned_users,
            retention_rate_7_day=retention_7_day,
            retention_rate_30_day=retention_30_day,
            avg_risk_score=avg_risk_score,
            risk_distribution=risk_distribution
        )
    
    async def _calculate_retention_rate(self, days: int, end_date: datetime) -> float:
        """Calculate retention rate for specified number of days."""
        
        cohort_start = end_date - timedelta(days=days)
        
        # Users who signed up exactly 'days' ago
        cohort_users = await self.db.fetchval("""
            SELECT COUNT(*) FROM users 
            WHERE DATE(created_at) = DATE($1)
        """, cohort_start.date()) or 0
        
        if cohort_users == 0:
            return 0.0
        
        # Users from that cohort who were active in last 7 days
        retained_users = await self.db.fetchval("""
            SELECT COUNT(DISTINCT u.id) FROM users u
            WHERE DATE(u.created_at) = DATE($1)
                AND EXISTS (
                    SELECT 1 FROM user_word_usage uwo 
                    WHERE uwo.user_id = u.id 
                        AND uwo.created_at >= $2
                )
        """, cohort_start.date(), end_date - timedelta(days=7)) or 0
        
        return retained_users / cohort_users
    
    async def _identify_intervention_opportunities(self, risk_profiles: List[UserRiskProfile]) -> List[Dict[str, Any]]:
        """Identify specific intervention opportunities."""
        
        opportunities = []
        
        # Group users by common risk factors for cohort interventions
        risk_factor_groups = defaultdict(list)
        for profile in risk_profiles:
            for factor in profile.risk_factors:
                risk_factor_groups[factor].append(profile)
        
        # Cohort intervention opportunities
        for risk_factor, users in risk_factor_groups.items():
            if len(users) >= 10:  # Minimum cohort size
                opportunities.append({
                    "type": "cohort_intervention",
                    "cohort": risk_factor,
                    "user_count": len(users),
                    "avg_risk_score": statistics.mean([u.risk_score for u in users]),
                    "expected_improvement": 0.3,  # 30% risk reduction
                    "intervention_type": self._get_cohort_intervention_type(risk_factor)
                })
        
        # Feature engagement opportunities
        low_engagement_users = [p for p in risk_profiles if p.engagement_score < 0.4]
        if low_engagement_users:
            # Group by tier for targeted feature promotion
            tier_groups = defaultdict(list)
            for user in low_engagement_users:
                tier_groups[user.tier].append(user)
            
            for tier, users in tier_groups.items():
                if len(users) >= 5:
                    opportunities.append({
                        "type": "feature_engagement",
                        "feature": f"{tier}_tier_features",
                        "user_count": len(users),
                        "expected_improvement": 0.25,
                        "engagement_campaign": self._get_feature_engagement_campaign(tier)
                    })
        
        return opportunities
    
    def _get_cohort_intervention_type(self, risk_factor: str) -> str:
        """Get appropriate intervention type for risk factor."""
        
        intervention_map = {
            "inactive_user": "win_back_campaign",
            "declining_usage": "motivation_campaign",
            "low_engagement": "feature_discovery",
            "anonymous_user": "signup_conversion",
            "long_term_free": "upgrade_nudge"
        }
        
        return intervention_map.get(risk_factor, "general_retention")
    
    def _get_feature_engagement_campaign(self, tier: str) -> str:
        """Get feature engagement campaign for tier."""
        
        campaigns = {
            "anonymous": "basic_features_tour",
            "free": "full_analysis_showcase", 
            "pro": "advanced_features_training",
            "partnership": "collaboration_optimization"
        }
        
        return campaigns.get(tier, "general_features")
    
    async def _analyze_churn_patterns(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze patterns in user churn."""
        
        # Get recently churned users (inactive for churn_definition_days)
        churn_cutoff = end_date - timedelta(days=self.config["churn_definition_days"])
        
        churned_users = await self.db.fetch("""
            SELECT 
                u.id,
                u.tier,
                u.created_at,
                u.last_login,
                EXTRACT(DAY FROM u.last_login - u.created_at) as days_active
            FROM users u
            WHERE u.last_login < $1
                AND u.created_at >= $2
                AND u.last_login >= $2
            ORDER BY u.last_login DESC
            LIMIT 200
        """, churn_cutoff, start_date)
        
        if not churned_users:
            return {"patterns": [], "insights": "insufficient_churn_data"}
        
        # Analyze churn patterns
        patterns = {}
        
        # Churn by tier
        tier_churn = defaultdict(int)
        tier_totals = defaultdict(int)
        
        for user in churned_users:
            tier_churn[user["tier"]] += 1
        
        # Get total users by tier for churn rates
        for tier in tier_churn.keys():
            total = await self.db.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE tier = $1 AND created_at >= $2
            """, tier, start_date) or 1
            tier_totals[tier] = total
        
        patterns["churn_by_tier"] = {
            tier: {
                "churned_count": tier_churn[tier],
                "total_users": tier_totals[tier],
                "churn_rate": tier_churn[tier] / tier_totals[tier]
            }
            for tier in tier_churn.keys()
        }
        
        # Time to churn analysis
        days_active = [user["days_active"] for user in churned_users if user["days_active"]]
        if days_active:
            patterns["time_to_churn"] = {
                "avg_days": statistics.mean(days_active),
                "median_days": statistics.median(days_active),
                "early_churn_rate": len([d for d in days_active if d <= 7]) / len(days_active)
            }
        
        return patterns
    
    # Execution methods
    async def _execute_personalized_intervention(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute personalized retention intervention."""
        
        user_id = action["user_id"]
        intervention_type = action["intervention_type"]
        
        # Store intervention record
        intervention_data = {
            "user_id": user_id,
            "intervention_type": intervention_type,
            "risk_score": action.get("risk_score", 0),
            "recommendations": action.get("recommendations", []),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO retention_interventions (
                user_id, intervention_type, intervention_data, 
                agent_name, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        user_id,
        intervention_type,
        json.dumps(intervention_data),
        self.name
        )
        
        logger.info(f"Created retention intervention for user {user_id}: {intervention_type}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "intervention_type": intervention_type
        }
    
    async def _execute_cohort_intervention(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cohort-based retention intervention."""
        
        cohort = action["cohort"]
        intervention_type = action["intervention_type"]
        target_users = action.get("target_users", [])
        
        # Store cohort intervention
        cohort_data = {
            "cohort": cohort,
            "intervention_type": intervention_type,
            "user_count": len(target_users),
            "target_users": target_users[:50],  # Store sample of users
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO cohort_interventions (
                cohort_name, intervention_type, intervention_data,
                agent_name, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        cohort,
        intervention_type,
        json.dumps(cohort_data),
        self.name
        )
        
        logger.info(f"Created cohort intervention for {cohort}: {intervention_type} ({len(target_users)} users)")
        
        return {
            "status": "success",
            "cohort": cohort,
            "user_count": len(target_users)
        }
    
    async def _execute_feature_engagement(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute feature engagement campaign."""
        
        feature = action["feature"]
        campaign = action["engagement_campaign"]
        
        campaign_data = {
            "feature": feature,
            "campaign_type": campaign,
            "user_count": action.get("user_count", 0),
            "expected_improvement": action.get("expected_improvement", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO feature_engagement_campaigns (
                feature_name, campaign_type, campaign_data,
                agent_name, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        feature,
        campaign,
        json.dumps(campaign_data),
        self.name
        )
        
        logger.info(f"Created feature engagement campaign: {campaign} for {feature}")
        
        return {
            "status": "success",
            "feature": feature,
            "campaign": campaign
        }
    
    async def _execute_early_warning_system(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute early warning system improvements."""
        
        system_updates = action.get("system_updates", {})
        
        # Store early warning system configuration
        warning_data = {
            "updated_thresholds": system_updates.get("thresholds", {}),
            "new_patterns": system_updates.get("patterns", []),
            "improved_algorithms": system_updates.get("algorithms", []),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.db.execute("""
            INSERT INTO early_warning_updates (
                update_type, update_data, agent_name, created_at
            ) VALUES ($1, $2, $3, NOW())
        """,
        "retention_prediction_improvement",
        json.dumps(warning_data),
        self.name
        )
        
        logger.info("Updated early warning system for retention prediction")
        
        return {
            "status": "success",
            "updates_applied": len(system_updates)
        }
    
    # Helper methods
    def _calculate_prediction_confidence(self, retention_metrics: RetentionMetrics, risk_profiles: List[UserRiskProfile]) -> float:
        """Calculate confidence in retention predictions."""
        
        factors = []
        
        # Sample size factor
        if retention_metrics.total_users >= 200:
            factors.append(1.0)
        elif retention_metrics.total_users >= 100:
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Risk distribution factor (good spread indicates reliable model)
        risk_dist = retention_metrics.risk_distribution
        total_users = sum(risk_dist.values())
        if total_users > 0:
            entropy = sum(-(count/total_users) * math.log2(count/total_users + 1e-10) 
                         for count in risk_dist.values() if count > 0)
            max_entropy = math.log2(3)  # 3 risk categories
            distribution_quality = entropy / max_entropy if max_entropy > 0 else 0
            factors.append(distribution_quality)
        else:
            factors.append(0.5)
        
        # Retention rate consistency
        if 0.1 <= retention_metrics.retention_rate_30_day <= 0.9:  # Reasonable range
            factors.append(1.0)
        else:
            factors.append(0.7)
        
        return statistics.mean(factors)
    
    def _assess_retention_data_quality(self, retention_metrics: RetentionMetrics, risk_profiles: List[UserRiskProfile]) -> float:
        """Assess quality of retention analysis data."""
        
        quality_factors = []
        
        # User sample adequacy
        quality_factors.append(min(1.0, retention_metrics.total_users / 200))
        
        # Risk score distribution reasonableness
        if risk_profiles:
            risk_scores = [p.risk_score for p in risk_profiles]
            if 0.1 <= statistics.mean(risk_scores) <= 0.7:  # Reasonable average
                quality_factors.append(1.0)
            else:
                quality_factors.append(0.7)
        else:
            quality_factors.append(0.5)
        
        # Retention rate reasonableness
        if 0.2 <= retention_metrics.retention_rate_30_day <= 0.8:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.6)
        
        return statistics.mean(quality_factors)
    
    def _generate_retention_recommendations(self, retention_metrics: RetentionMetrics, opportunities: List[Dict], churn_patterns: Dict) -> List[Dict[str, Any]]:
        """Generate actionable retention recommendations."""
        
        recommendations = []
        
        # High-level recommendations based on metrics
        if retention_metrics.retention_rate_30_day < 0.4:
            recommendations.append({
                "title": "Critical retention issue - comprehensive intervention needed",
                "description": f"30-day retention at {retention_metrics.retention_rate_30_day:.1%} requires immediate action",
                "expected_impact": "Major retention improvement",
                "priority": "critical",
                "action_type": "strategic"
            })
        
        # Specific intervention recommendations
        for opportunity in opportunities:
            if opportunity["type"] == "cohort_intervention":
                recommendations.append({
                    "title": f"Target {opportunity['cohort']} cohort intervention",
                    "description": f"Implement {opportunity['intervention_type']} for {opportunity['user_count']} users",
                    "expected_impact": f"{opportunity['expected_improvement']:.1%} risk reduction",
                    "priority": "high",
                    "action_type": "immediate"
                })
        
        # At-risk user recommendations
        if retention_metrics.high_risk_users > 0:
            recommendations.append({
                "title": f"Immediate intervention for {retention_metrics.high_risk_users} high-risk users",
                "description": "Deploy personalized retention campaigns",
                "expected_impact": "40% churn risk reduction for target users",
                "priority": "high",
                "action_type": "immediate"
            })
        
        return recommendations
    
    def _assess_retention_optimization_risk(self, actions: List[Dict], results: AnalysisResults) -> float:
        """Assess risk of retention optimization actions."""
        
        # Retention interventions are generally low risk
        return 0.2
    
    async def _create_retention_rollback_plan(self, actions: List[Dict]) -> Dict[str, Any]:
        """Create rollback plan for retention actions."""
        
        return {
            "rollback_actions": ["disable_intervention_campaigns", "restore_default_messaging"],
            "trigger_conditions": ["user_complaints", "engagement_decrease"],
            "monitoring_period_days": 14
        }
    
    # Action creation methods (simplified for brevity)
    async def _create_personalized_intervention_action(self, user_profile: Dict) -> Dict[str, Any]:
        return {
            "type": "personalized_intervention",
            "user_id": user_profile["user_id"],
            "intervention_type": user_profile["intervention_recommendations"][0] if user_profile["intervention_recommendations"] else "general_retention",
            "risk_score": user_profile["risk_score"],
            "recommendations": user_profile["intervention_recommendations"]
        }
    
    async def _create_cohort_intervention_action(self, opportunity: Dict) -> Dict[str, Any]:
        return {
            "type": "cohort_intervention",
            "cohort": opportunity["cohort"],
            "intervention_type": opportunity["intervention_type"],
            "target_users": [],  # Would be populated with actual user IDs
            "expected_improvement": opportunity["expected_improvement"]
        }
    
    async def _create_feature_engagement_action(self, opportunity: Dict) -> Dict[str, Any]:
        return {
            "type": "feature_engagement",
            "feature": opportunity["feature"],
            "engagement_campaign": opportunity["engagement_campaign"],
            "user_count": opportunity["user_count"],
            "expected_improvement": opportunity["expected_improvement"]
        }
    
    async def _create_early_warning_action(self, churn_patterns: Dict) -> Dict[str, Any]:
        return {
            "type": "early_warning_system",
            "system_updates": {
                "patterns": churn_patterns,
                "thresholds": {"updated": True},
                "algorithms": ["improved_risk_scoring"]
            }
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
    
    # Create and run retention prediction agent
    agent = RetentionPredictionAgent(db_pool)
    
    try:
        performance_metrics = await agent.run_full_cycle()
        print(f"Retention prediction completed successfully!")
        print(f"ROI Estimate: {performance_metrics.roi_estimate:.2f}")
        print(f"System Improvement: {performance_metrics.system_improvement}")
        
    except Exception as e:
        print(f"Agent execution failed: {str(e)}")
        raise
    
    finally:
        await db_pool.close()

if __name__ == "__main__":
    import math  # For entropy calculation
    asyncio.run(main())