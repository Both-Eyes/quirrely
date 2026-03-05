#!/usr/bin/env python3
"""
LNCP META: ACHIEVEMENT OBSERVER v1.0.0
Tracks and optimizes the P3 Achievement System.

This observer monitors:
- Badge earning patterns
- XP accumulation rates
- Challenge participation/completion
- Streak maintenance
- Leaderboard engagement

It provides:
- Real-time achievement metrics
- Engagement health scoring
- Optimization suggestions for XP/badge thresholds
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BadgeMetrics:
    """Metrics for a single badge type."""
    badge_id: str
    badge_name: str
    category: str                    # reading, writing, community, special
    
    # Earning stats
    total_earned: int = 0
    earned_24h: int = 0
    earned_7d: int = 0
    
    # Progress stats
    users_in_progress: int = 0
    avg_progress_percent: float = 0.0
    
    # Timing
    avg_days_to_earn: float = 0.0
    median_days_to_earn: float = 0.0
    
    # Threshold
    current_threshold: int = 0
    suggested_threshold: Optional[int] = None


@dataclass 
class ChallengeMetrics:
    """Metrics for weekly challenges."""
    challenge_id: str
    challenge_name: str
    
    # Participation
    total_participants: int = 0
    active_participants: int = 0
    
    # Completion
    completed_count: int = 0
    completion_rate: float = 0.0
    
    # Progress distribution
    progress_0_25: int = 0
    progress_25_50: int = 0
    progress_50_75: int = 0
    progress_75_100: int = 0
    
    # XP
    xp_reward: int = 0
    total_xp_awarded: int = 0


@dataclass
class StreakMetrics:
    """Metrics for streak behavior."""
    # Active streaks
    users_with_streak: int = 0
    avg_streak_length: float = 0.0
    max_active_streak: int = 0
    
    # Streak distribution
    streak_1_7: int = 0
    streak_8_14: int = 0
    streak_15_30: int = 0
    streak_30_plus: int = 0
    
    # Streak health
    streaks_broken_24h: int = 0
    streaks_at_risk: int = 0       # Haven't logged in today
    
    # XP from streaks
    streak_xp_24h: int = 0
    streak_xp_7d: int = 0


@dataclass
class LeaderboardMetrics:
    """Metrics for leaderboard engagement."""
    # Views
    views_24h: int = 0
    views_7d: int = 0
    unique_viewers_24h: int = 0
    
    # Engagement
    avg_time_on_leaderboard: float = 0.0
    clicks_to_profile: int = 0
    
    # Movement
    rank_changes_24h: int = 0
    users_moved_up: int = 0
    users_moved_down: int = 0


@dataclass
class AchievementHealth:
    """Overall achievement system health."""
    # Scores (0-100)
    overall_score: float = 0.0
    badge_engagement: float = 0.0
    challenge_engagement: float = 0.0
    streak_health: float = 0.0
    leaderboard_engagement: float = 0.0
    
    # XP economy
    total_xp_24h: int = 0
    avg_xp_per_user_24h: float = 0.0
    xp_inflation_rate: float = 0.0    # % change week over week
    
    # Concerns
    issues: List[str] = field(default_factory=list)
    
    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class AchievementObserver:
    """
    Observes and optimizes the P3 Achievement System.
    
    Responsibilities:
    1. Track badge earning patterns
    2. Monitor challenge participation
    3. Analyze streak behavior
    4. Measure leaderboard engagement
    5. Suggest XP/threshold optimizations
    """
    
    def __init__(self):
        # Badge definitions (from v3.1.1)
        self.badges = {
            # Reading Streaks
            "first_week": {"name": "First Week", "category": "reading", "threshold": 7, "xp": 100},
            "committed": {"name": "Committed", "category": "reading", "threshold": 14, "xp": 200},
            "dedicated": {"name": "Dedicated", "category": "reading", "threshold": 21, "xp": 300},
            "bookworm": {"name": "Bookworm", "category": "reading", "threshold": 30, "xp": 500},
            # Writing Achievements
            "first_analysis": {"name": "First Analysis", "category": "writing", "threshold": 1, "xp": 50},
            "voice_found": {"name": "Voice Found", "category": "writing", "threshold": 70, "xp": 150},  # 70% confidence
            "prolific": {"name": "Prolific", "category": "writing", "threshold": 50, "xp": 400},  # 50 analyses
            "voice_master": {"name": "Voice Master", "category": "writing", "threshold": 90, "xp": 1000},  # 90% confidence
            # Community
            "social": {"name": "Social", "category": "community", "threshold": 10, "xp": 100},  # 10 follows
            "engaged": {"name": "Engaged", "category": "community", "threshold": 25, "xp": 150},  # 25 comments
            "influencer": {"name": "Influencer", "category": "community", "threshold": 100, "xp": 300},  # 100 followers
            "thought_leader": {"name": "Thought Leader", "category": "community", "threshold": 1000, "xp": 1000},
            # Special
            "early_adopter": {"name": "Early Adopter", "category": "special", "threshold": 1, "xp": 500},
            "beta_tester": {"name": "Beta Tester", "category": "special", "threshold": 1, "xp": 250},
            "referrer": {"name": "Referrer", "category": "special", "threshold": 3, "xp": 300},
            "annual_pro": {"name": "Annual Pro", "category": "special", "threshold": 1, "xp": 500},
        }
        
        # XP configuration
        self.xp_config = {
            "streak_daily": 50,
            "analysis_completed": 25,
            "challenge_completed": 500,
            "level_up_base": 1000,
            "level_multiplier": 1.2,
        }
        
        # Storage (in production, this would be database)
        self._badge_events: List[Dict] = []
        self._challenge_events: List[Dict] = []
        self._streak_events: List[Dict] = []
        self._leaderboard_events: List[Dict] = []
        self._xp_events: List[Dict] = []
        
        # Cached metrics
        self._last_health: Optional[AchievementHealth] = None
        self._last_calculated: Optional[datetime] = None
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_badge_earned(
        self,
        user_id: str,
        badge_id: str,
        xp_awarded: int,
        days_to_earn: Optional[float] = None
    ) -> None:
        """Track a badge earning event."""
        self._badge_events.append({
            "user_id": user_id,
            "badge_id": badge_id,
            "xp_awarded": xp_awarded,
            "days_to_earn": days_to_earn,
            "timestamp": datetime.utcnow(),
        })
    
    def track_badge_progress(
        self,
        user_id: str,
        badge_id: str,
        current: int,
        target: int
    ) -> None:
        """Track badge progress update."""
        progress = (current / target * 100) if target > 0 else 0
        self._badge_events.append({
            "user_id": user_id,
            "badge_id": badge_id,
            "type": "progress",
            "current": current,
            "target": target,
            "progress_percent": progress,
            "timestamp": datetime.utcnow(),
        })
    
    def track_xp_gained(
        self,
        user_id: str,
        amount: int,
        source: str,    # "badge", "streak", "challenge", "analysis"
        source_id: Optional[str] = None
    ) -> None:
        """Track XP gain event."""
        self._xp_events.append({
            "user_id": user_id,
            "amount": amount,
            "source": source,
            "source_id": source_id,
            "timestamp": datetime.utcnow(),
        })
    
    def track_level_up(
        self,
        user_id: str,
        new_level: int,
        total_xp: int
    ) -> None:
        """Track level up event."""
        self._xp_events.append({
            "user_id": user_id,
            "type": "level_up",
            "new_level": new_level,
            "total_xp": total_xp,
            "timestamp": datetime.utcnow(),
        })
    
    def track_challenge_event(
        self,
        user_id: str,
        challenge_id: str,
        event_type: str,    # "started", "progress", "completed", "failed"
        progress: Optional[int] = None,
        target: Optional[int] = None
    ) -> None:
        """Track challenge participation."""
        self._challenge_events.append({
            "user_id": user_id,
            "challenge_id": challenge_id,
            "event_type": event_type,
            "progress": progress,
            "target": target,
            "timestamp": datetime.utcnow(),
        })
    
    def track_streak_event(
        self,
        user_id: str,
        event_type: str,    # "started", "continued", "broken", "milestone"
        streak_length: int,
        xp_awarded: int = 0
    ) -> None:
        """Track streak events."""
        self._streak_events.append({
            "user_id": user_id,
            "event_type": event_type,
            "streak_length": streak_length,
            "xp_awarded": xp_awarded,
            "timestamp": datetime.utcnow(),
        })
    
    def track_leaderboard_view(
        self,
        user_id: str,
        duration_seconds: float = 0,
        clicked_profile: bool = False
    ) -> None:
        """Track leaderboard engagement."""
        self._leaderboard_events.append({
            "user_id": user_id,
            "duration_seconds": duration_seconds,
            "clicked_profile": clicked_profile,
            "timestamp": datetime.utcnow(),
        })
    
    # ─────────────────────────────────────────────────────────────────────
    # METRICS CALCULATION
    # ─────────────────────────────────────────────────────────────────────
    
    def get_badge_metrics(self, badge_id: str) -> BadgeMetrics:
        """Get metrics for a specific badge."""
        badge_def = self.badges.get(badge_id, {})
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        # Filter events for this badge
        earned_events = [
            e for e in self._badge_events
            if e.get("badge_id") == badge_id and e.get("type") != "progress"
        ]
        progress_events = [
            e for e in self._badge_events
            if e.get("badge_id") == badge_id and e.get("type") == "progress"
        ]
        
        # Calculate metrics
        earned_24h = len([e for e in earned_events if e["timestamp"] > day_ago])
        earned_7d = len([e for e in earned_events if e["timestamp"] > week_ago])
        
        # Days to earn
        days_list = [e.get("days_to_earn", 0) for e in earned_events if e.get("days_to_earn")]
        avg_days = sum(days_list) / len(days_list) if days_list else 0
        
        # Progress
        unique_users_in_progress = len(set(e["user_id"] for e in progress_events))
        avg_progress = (
            sum(e.get("progress_percent", 0) for e in progress_events) / len(progress_events)
            if progress_events else 0
        )
        
        return BadgeMetrics(
            badge_id=badge_id,
            badge_name=badge_def.get("name", badge_id),
            category=badge_def.get("category", "unknown"),
            total_earned=len(earned_events),
            earned_24h=earned_24h,
            earned_7d=earned_7d,
            users_in_progress=unique_users_in_progress,
            avg_progress_percent=avg_progress,
            avg_days_to_earn=avg_days,
            current_threshold=badge_def.get("threshold", 0),
        )
    
    def get_challenge_metrics(self, challenge_id: str) -> ChallengeMetrics:
        """Get metrics for a specific challenge."""
        events = [e for e in self._challenge_events if e.get("challenge_id") == challenge_id]
        
        # Participation
        unique_participants = set(e["user_id"] for e in events)
        started = [e for e in events if e.get("event_type") == "started"]
        completed = [e for e in events if e.get("event_type") == "completed"]
        
        # Progress distribution
        progress_events = [e for e in events if e.get("event_type") == "progress"]
        p_0_25 = len([e for e in progress_events if e.get("progress", 0) / max(e.get("target", 1), 1) < 0.25])
        p_25_50 = len([e for e in progress_events if 0.25 <= e.get("progress", 0) / max(e.get("target", 1), 1) < 0.5])
        p_50_75 = len([e for e in progress_events if 0.5 <= e.get("progress", 0) / max(e.get("target", 1), 1) < 0.75])
        p_75_100 = len([e for e in progress_events if e.get("progress", 0) / max(e.get("target", 1), 1) >= 0.75])
        
        completion_rate = len(completed) / len(started) if started else 0
        
        return ChallengeMetrics(
            challenge_id=challenge_id,
            challenge_name=f"Challenge {challenge_id}",
            total_participants=len(unique_participants),
            active_participants=len(unique_participants),
            completed_count=len(completed),
            completion_rate=completion_rate,
            progress_0_25=p_0_25,
            progress_25_50=p_25_50,
            progress_50_75=p_50_75,
            progress_75_100=p_75_100,
            xp_reward=500,  # From v3.1.1 config
            total_xp_awarded=len(completed) * 500,
        )
    
    def get_streak_metrics(self) -> StreakMetrics:
        """Get overall streak metrics."""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        # Current streaks (most recent per user)
        user_streaks: Dict[str, int] = {}
        for e in self._streak_events:
            if e.get("event_type") in ["started", "continued", "milestone"]:
                user_streaks[e["user_id"]] = max(
                    user_streaks.get(e["user_id"], 0),
                    e.get("streak_length", 0)
                )
        
        # Broken streaks
        broken_24h = len([
            e for e in self._streak_events
            if e.get("event_type") == "broken" and e["timestamp"] > day_ago
        ])
        
        # Distribution
        streak_values = list(user_streaks.values())
        s_1_7 = len([s for s in streak_values if 1 <= s <= 7])
        s_8_14 = len([s for s in streak_values if 8 <= s <= 14])
        s_15_30 = len([s for s in streak_values if 15 <= s <= 30])
        s_30_plus = len([s for s in streak_values if s > 30])
        
        # XP from streaks
        streak_xp_24h = sum(
            e.get("xp_awarded", 0) for e in self._streak_events
            if e["timestamp"] > day_ago
        )
        streak_xp_7d = sum(
            e.get("xp_awarded", 0) for e in self._streak_events
            if e["timestamp"] > week_ago
        )
        
        return StreakMetrics(
            users_with_streak=len(user_streaks),
            avg_streak_length=sum(streak_values) / len(streak_values) if streak_values else 0,
            max_active_streak=max(streak_values) if streak_values else 0,
            streak_1_7=s_1_7,
            streak_8_14=s_8_14,
            streak_15_30=s_15_30,
            streak_30_plus=s_30_plus,
            streaks_broken_24h=broken_24h,
            streaks_at_risk=0,  # Would need login data
            streak_xp_24h=streak_xp_24h,
            streak_xp_7d=streak_xp_7d,
        )
    
    def get_leaderboard_metrics(self) -> LeaderboardMetrics:
        """Get leaderboard engagement metrics."""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        views_24h = len([e for e in self._leaderboard_events if e["timestamp"] > day_ago])
        views_7d = len([e for e in self._leaderboard_events if e["timestamp"] > week_ago])
        
        unique_24h = len(set(
            e["user_id"] for e in self._leaderboard_events
            if e["timestamp"] > day_ago
        ))
        
        durations = [e.get("duration_seconds", 0) for e in self._leaderboard_events]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        clicks = len([e for e in self._leaderboard_events if e.get("clicked_profile")])
        
        return LeaderboardMetrics(
            views_24h=views_24h,
            views_7d=views_7d,
            unique_viewers_24h=unique_24h,
            avg_time_on_leaderboard=avg_duration,
            clicks_to_profile=clicks,
        )
    
    def get_health(self) -> AchievementHealth:
        """Calculate overall achievement system health."""
        # Cache for 5 minutes
        if (
            self._last_health and self._last_calculated and
            datetime.utcnow() - self._last_calculated < timedelta(minutes=5)
        ):
            return self._last_health
        
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        # Badge engagement (0-100)
        badge_events_24h = len([e for e in self._badge_events if e["timestamp"] > day_ago])
        badge_engagement = min(100, badge_events_24h * 2)  # Target: 50+ events/day
        
        # Challenge engagement
        challenge_events_24h = len([e for e in self._challenge_events if e["timestamp"] > day_ago])
        challenge_engagement = min(100, challenge_events_24h * 5)  # Target: 20+ events/day
        
        # Streak health
        streak_metrics = self.get_streak_metrics()
        streak_health = min(100, (
            streak_metrics.users_with_streak * 2 +
            streak_metrics.avg_streak_length * 3 -
            streak_metrics.streaks_broken_24h * 5
        ))
        streak_health = max(0, streak_health)
        
        # Leaderboard
        lb_metrics = self.get_leaderboard_metrics()
        leaderboard_engagement = min(100, lb_metrics.views_24h * 3)
        
        # Overall
        overall = (
            badge_engagement * 0.3 +
            challenge_engagement * 0.2 +
            streak_health * 0.3 +
            leaderboard_engagement * 0.2
        )
        
        # XP
        xp_24h = sum(e.get("amount", 0) for e in self._xp_events if e["timestamp"] > day_ago)
        unique_users_24h = len(set(e["user_id"] for e in self._xp_events if e["timestamp"] > day_ago))
        avg_xp = xp_24h / unique_users_24h if unique_users_24h else 0
        
        # Issues
        issues = []
        if badge_engagement < 30:
            issues.append("Low badge earning rate")
        if streak_metrics.streaks_broken_24h > 10:
            issues.append("High streak breakage")
        if leaderboard_engagement < 20:
            issues.append("Low leaderboard engagement")
        
        health = AchievementHealth(
            overall_score=overall,
            badge_engagement=badge_engagement,
            challenge_engagement=challenge_engagement,
            streak_health=streak_health,
            leaderboard_engagement=leaderboard_engagement,
            total_xp_24h=xp_24h,
            avg_xp_per_user_24h=avg_xp,
            issues=issues,
            calculated_at=now,
        )
        
        self._last_health = health
        self._last_calculated = now
        
        return health
    
    # ─────────────────────────────────────────────────────────────────────
    # OPTIMIZATION SUGGESTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions for the achievement system."""
        suggestions = []
        health = self.get_health()
        
        # Badge threshold adjustments
        for badge_id, badge_def in self.badges.items():
            metrics = self.get_badge_metrics(badge_id)
            
            # If too few people earning, suggest lowering threshold
            if metrics.earned_7d == 0 and metrics.users_in_progress > 10:
                suggestions.append({
                    "type": "badge_threshold",
                    "badge_id": badge_id,
                    "current_threshold": metrics.current_threshold,
                    "suggested_threshold": int(metrics.current_threshold * 0.8),
                    "reason": "No earners but active progress - threshold may be too high",
                    "confidence": 0.7,
                    "domain": "gamification",
                })
            
            # If too easy (everyone earning quickly), suggest raising
            if metrics.earned_7d > 50 and metrics.avg_days_to_earn < 2:
                suggestions.append({
                    "type": "badge_threshold",
                    "badge_id": badge_id,
                    "current_threshold": metrics.current_threshold,
                    "suggested_threshold": int(metrics.current_threshold * 1.2),
                    "reason": "Badge earned too quickly - may feel less valuable",
                    "confidence": 0.6,
                    "domain": "gamification",
                })
        
        # XP rate adjustments
        if health.avg_xp_per_user_24h < 50:
            suggestions.append({
                "type": "xp_rate",
                "parameter": "streak_daily",
                "current_value": self.xp_config["streak_daily"],
                "suggested_value": int(self.xp_config["streak_daily"] * 1.25),
                "reason": "Low daily XP - increase streak rewards for engagement",
                "confidence": 0.65,
                "domain": "gamification",
            })
        
        # Challenge difficulty
        # Would analyze completion rates and suggest adjustments
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_achievement_observer: Optional[AchievementObserver] = None


def get_achievement_observer() -> AchievementObserver:
    """Get singleton achievement observer."""
    global _achievement_observer
    if _achievement_observer is None:
        _achievement_observer = AchievementObserver()
    return _achievement_observer
