#!/usr/bin/env python3
"""
QUIRRELY ANALYTICS SERVICE v1.0
Event tracking, metrics collection, and reporting.

Privacy-first: No cookies, no PII in events, server-side only.
"""

import os
import hashlib
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import httpx

from analytics_config import (
    PLAUSIBLE_DOMAIN,
    PLAUSIBLE_API_KEY,
    EventCategory,
    EventName,
    EVENT_CATEGORIES,
    MetricType,
    INTERNAL_METRICS,
    DATA_RETENTION,
    FUNNELS,
    is_feature_enabled,
)


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TRACKING
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AnalyticsEvent:
    """An analytics event."""
    name: EventName
    user_id: Optional[str] = None  # Hashed, not PII
    properties: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        # Hash user_id for privacy
        if self.user_id:
            self.user_id = hashlib.sha256(self.user_id.encode()).hexdigest()[:16]


class AnalyticsService:
    """Service for tracking events and collecting metrics."""
    
    def __init__(self):
        self._event_buffer: List[AnalyticsEvent] = []
        self._buffer_size = 100
    
    async def track(
        self,
        event_name: EventName,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Track an event."""
        event = AnalyticsEvent(
            name=event_name,
            user_id=user_id,
            properties=properties or {},
        )
        
        # Add to buffer
        self._event_buffer.append(event)
        
        # Flush if buffer full
        if len(self._event_buffer) >= self._buffer_size:
            await self.flush()
        
        # Also send to Plausible for key events
        if self._should_send_to_plausible(event_name):
            await self._send_to_plausible(event)
    
    async def flush(self):
        """Flush event buffer to database."""
        if not self._event_buffer:
            return
        
        events = self._event_buffer.copy()
        self._event_buffer.clear()
        
        # Would batch insert to database
        await self._store_events(events)
    
    def _should_send_to_plausible(self, event_name: EventName) -> bool:
        """Check if event should be sent to Plausible."""
        # Send conversions and core actions to Plausible
        category = EVENT_CATEGORIES.get(event_name)
        return category in [EventCategory.CONVERSION, EventCategory.CORE_ACTION]
    
    async def _send_to_plausible(self, event: AnalyticsEvent):
        """Send event to Plausible."""
        if not PLAUSIBLE_API_KEY:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://plausible.io/api/event",
                    headers={
                        "Content-Type": "application/json",
                    },
                    json={
                        "domain": PLAUSIBLE_DOMAIN,
                        "name": event.name.value,
                        "url": f"https://{PLAUSIBLE_DOMAIN}/app",
                        "props": event.properties or {},
                    },
                )
        except Exception as e:
            # Log but don't fail
            print(f"Plausible error: {e}")
    
    async def _store_events(self, events: List[AnalyticsEvent]):
        """Store events in database."""
        # Would batch insert
        pass


# ═══════════════════════════════════════════════════════════════════════════
# METRICS COLLECTION
# ═══════════════════════════════════════════════════════════════════════════

class MetricsCollector:
    """Collects and aggregates internal metrics."""
    
    async def collect_daily_metrics(self, for_date: date = None) -> Dict[str, Any]:
        """Collect all daily metrics."""
        if for_date is None:
            for_date = date.today() - timedelta(days=1)
        
        metrics = {
            "date": for_date.isoformat(),
            "collected_at": datetime.utcnow().isoformat(),
        }
        
        # User metrics
        metrics["dau"] = await self._get_dau(for_date)
        metrics["wau"] = await self._get_wau(for_date)
        metrics["mau"] = await self._get_mau(for_date)
        metrics["total_users"] = await self._get_total_users()
        metrics["new_signups"] = await self._get_new_signups(for_date)
        
        # Subscription metrics
        metrics["mrr"] = await self._get_mrr()
        metrics["active_subscriptions"] = await self._get_active_subscriptions()
        metrics["trial_conversion_rate"] = await self._get_trial_conversion_rate()
        metrics["churn_rate"] = await self._get_churn_rate(for_date)
        
        # Activity metrics
        metrics["analyses_count"] = await self._get_analyses_count(for_date)
        metrics["words_analyzed"] = await self._get_words_analyzed(for_date)
        
        # Feature metrics
        metrics["active_streaks"] = await self._get_active_streaks()
        metrics["featured_writers"] = await self._get_featured_count("writer")
        metrics["featured_curators"] = await self._get_featured_count("curator")
        
        return metrics
    
    # User metrics
    async def _get_dau(self, for_date: date) -> int:
        # Would query: SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE DATE(created_at) = for_date
        return 0
    
    async def _get_wau(self, for_date: date) -> int:
        # Would query: SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE created_at > for_date - 7 days
        return 0
    
    async def _get_mau(self, for_date: date) -> int:
        # Would query: SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE created_at > for_date - 30 days
        return 0
    
    async def _get_total_users(self) -> int:
        # Would query: SELECT COUNT(*) FROM users WHERE status = 'active'
        return 0
    
    async def _get_new_signups(self, for_date: date) -> int:
        # Would query: SELECT COUNT(*) FROM users WHERE DATE(created_at) = for_date
        return 0
    
    # Subscription metrics
    async def _get_mrr(self) -> float:
        # Would calculate from active subscriptions
        return 0.0
    
    async def _get_active_subscriptions(self) -> int:
        # Would query: SELECT COUNT(*) FROM subscriptions WHERE status = 'active'
        return 0
    
    async def _get_trial_conversion_rate(self) -> float:
        # Would calculate: converted_trials / total_ended_trials * 100
        return 0.0
    
    async def _get_churn_rate(self, for_date: date) -> float:
        # Would calculate: churned_this_month / active_start_of_month * 100
        return 0.0
    
    # Activity metrics
    async def _get_analyses_count(self, for_date: date) -> int:
        # Would query: SELECT COUNT(*) FROM analyses WHERE DATE(created_at) = for_date
        return 0
    
    async def _get_words_analyzed(self, for_date: date) -> int:
        # Would query: SELECT SUM(word_count) FROM analyses WHERE DATE(created_at) = for_date
        return 0
    
    # Feature metrics
    async def _get_active_streaks(self) -> int:
        # Would query users with streak > 0
        return 0
    
    async def _get_featured_count(self, feature_type: str) -> int:
        # Would query featured_writers or featured_curators
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# FUNNEL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

class FunnelAnalyzer:
    """Analyzes conversion funnels."""
    
    async def analyze_funnel(
        self,
        funnel_name: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Analyze a funnel for a date range."""
        funnel = FUNNELS.get(funnel_name)
        if not funnel:
            return {"error": "Funnel not found"}
        
        steps = funnel["steps"]
        results = {
            "funnel_name": funnel["name"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "steps": [],
        }
        
        previous_count = None
        for i, step in enumerate(steps):
            count = await self._get_step_count(step, start_date, end_date)
            conversion = None
            
            if previous_count is not None and previous_count > 0:
                conversion = round((count / previous_count) * 100, 1)
            
            results["steps"].append({
                "step": step,
                "count": count,
                "conversion_from_previous": conversion,
            })
            
            previous_count = count
        
        # Overall conversion
        if results["steps"] and results["steps"][0]["count"] > 0:
            results["overall_conversion"] = round(
                (results["steps"][-1]["count"] / results["steps"][0]["count"]) * 100, 1
            )
        
        return results
    
    async def _get_step_count(self, step: str, start_date: date, end_date: date) -> int:
        """Get count of users who completed a funnel step."""
        # Would query based on step type
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# RETENTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

class RetentionAnalyzer:
    """Analyzes user retention cohorts."""
    
    async def get_cohort_retention(
        self,
        cohort_date: date,
        periods: int = 12,
        period_type: str = "weekly",
    ) -> Dict[str, Any]:
        """Get retention for a cohort."""
        cohort_size = await self._get_cohort_size(cohort_date, period_type)
        
        retention = {
            "cohort_date": cohort_date.isoformat(),
            "cohort_size": cohort_size,
            "period_type": period_type,
            "retention": [],
        }
        
        for period in range(periods + 1):
            retained = await self._get_retained_count(cohort_date, period, period_type)
            rate = round((retained / cohort_size) * 100, 1) if cohort_size > 0 else 0
            
            retention["retention"].append({
                "period": period,
                "retained": retained,
                "rate": rate,
            })
        
        return retention
    
    async def _get_cohort_size(self, cohort_date: date, period_type: str) -> int:
        """Get number of users in cohort."""
        # Would query users who signed up in the period
        return 0
    
    async def _get_retained_count(self, cohort_date: date, period: int, period_type: str) -> int:
        """Get number of retained users in period."""
        # Would query users who were active in the period
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# USER-FACING ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

class UserAnalytics:
    """Analytics visible to users about their own activity."""
    
    async def get_writer_analytics(
        self,
        user_id: str,
        period: str = "30d",
    ) -> Dict[str, Any]:
        """Get writer's personal analytics."""
        days = 30 if period == "30d" else 90 if period == "90d" else 365
        start_date = date.today() - timedelta(days=days)
        
        return {
            "period": period,
            "words_over_time": await self._get_words_over_time(user_id, start_date),
            "streak_history": await self._get_streak_history(user_id),
            "voice_evolution": await self._get_voice_evolution(user_id, start_date),
            "total_words": await self._get_total_words(user_id),
            "total_analyses": await self._get_total_analyses(user_id),
            "longest_streak": await self._get_longest_streak(user_id),
            "current_streak": await self._get_current_streak(user_id),
        }
    
    async def get_reader_analytics(
        self,
        user_id: str,
        period: str = "30d",
    ) -> Dict[str, Any]:
        """Get reader's personal analytics."""
        days = 30 if period == "30d" else 90 if period == "90d" else 365
        start_date = date.today() - timedelta(days=days)
        
        return {
            "period": period,
            "reading_over_time": await self._get_reading_over_time(user_id, start_date),
            "deep_read_ratio": await self._get_deep_read_ratio(user_id),
            "taste_evolution": await self._get_taste_evolution(user_id, start_date),
            "total_posts_read": await self._get_total_posts_read(user_id),
            "total_deep_reads": await self._get_total_deep_reads(user_id),
            "profiles_explored": await self._get_profiles_explored(user_id),
        }
    
    async def get_featured_analytics(
        self,
        user_id: str,
        period: str = "30d",
    ) -> Dict[str, Any]:
        """Get Featured member's analytics."""
        days = 30 if period == "30d" else 90 if period == "90d" else 365
        start_date = date.today() - timedelta(days=days)
        
        return {
            "period": period,
            "profile_views": await self._get_profile_views(user_id, start_date),
            "piece_engagement": await self._get_piece_engagement(user_id, start_date),
            "path_follows": await self._get_path_follows(user_id, start_date),
        }
    
    # Implementation stubs
    async def _get_words_over_time(self, user_id: str, start_date: date) -> List[Dict]:
        return []
    
    async def _get_streak_history(self, user_id: str) -> List[Dict]:
        return []
    
    async def _get_voice_evolution(self, user_id: str, start_date: date) -> List[Dict]:
        return []
    
    async def _get_total_words(self, user_id: str) -> int:
        return 0
    
    async def _get_total_analyses(self, user_id: str) -> int:
        return 0
    
    async def _get_longest_streak(self, user_id: str) -> int:
        return 0
    
    async def _get_current_streak(self, user_id: str) -> int:
        return 0
    
    async def _get_reading_over_time(self, user_id: str, start_date: date) -> List[Dict]:
        return []
    
    async def _get_deep_read_ratio(self, user_id: str) -> float:
        return 0.0
    
    async def _get_taste_evolution(self, user_id: str, start_date: date) -> List[Dict]:
        return []
    
    async def _get_total_posts_read(self, user_id: str) -> int:
        return 0
    
    async def _get_total_deep_reads(self, user_id: str) -> int:
        return 0
    
    async def _get_profiles_explored(self, user_id: str) -> List[str]:
        return []
    
    async def _get_profile_views(self, user_id: str, start_date: date) -> int:
        return 0
    
    async def _get_piece_engagement(self, user_id: str, start_date: date) -> Dict:
        return {}
    
    async def _get_path_follows(self, user_id: str, start_date: date) -> int:
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCES
# ═══════════════════════════════════════════════════════════════════════════

_analytics_service: Optional[AnalyticsService] = None
_metrics_collector: Optional[MetricsCollector] = None
_funnel_analyzer: Optional[FunnelAnalyzer] = None
_retention_analyzer: Optional[RetentionAnalyzer] = None
_user_analytics: Optional[UserAnalytics] = None


def get_analytics_service() -> AnalyticsService:
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service


def get_metrics_collector() -> MetricsCollector:
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_funnel_analyzer() -> FunnelAnalyzer:
    global _funnel_analyzer
    if _funnel_analyzer is None:
        _funnel_analyzer = FunnelAnalyzer()
    return _funnel_analyzer


def get_retention_analyzer() -> RetentionAnalyzer:
    global _retention_analyzer
    if _retention_analyzer is None:
        _retention_analyzer = RetentionAnalyzer()
    return _retention_analyzer


def get_user_analytics() -> UserAnalytics:
    global _user_analytics
    if _user_analytics is None:
        _user_analytics = UserAnalytics()
    return _user_analytics
