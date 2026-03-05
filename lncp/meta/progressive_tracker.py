#!/usr/bin/env python3
"""
LNCP META: PROGRESSIVE TRACKER v1.0.0
Tracks and optimizes the P3 Progressive Feature Unlocks system.

This tracker monitors:
- Feature unlock progression
- Day-by-day engagement
- Day 7 offer conversion
- Unlock timing effectiveness
- Free-to-paid conversion through progressive system
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESSIVE UNLOCK DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UnlockDefinition:
    """Definition of a progressive unlock."""
    unlock_id: str
    name: str
    description: str
    day_available: int
    feature_type: str
    is_teaser: bool = False


UNLOCKS = {
    "day1_basic_analysis": UnlockDefinition(
        unlock_id="day1_basic_analysis",
        name="Basic Voice Analysis",
        description="Initial voice confidence score",
        day_available=1,
        feature_type="analysis",
    ),
    "day3_voice_profile": UnlockDefinition(
        unlock_id="day3_voice_profile",
        name="Voice Profile",
        description="See your unique voice dimensions",
        day_available=3,
        feature_type="profile",
    ),
    "day5_author_comparison": UnlockDefinition(
        unlock_id="day5_author_comparison",
        name="Author Comparison",
        description="Compare your voice to famous writers",
        day_available=5,
        feature_type="comparison",
    ),
    "day7_history_upgrade": UnlockDefinition(
        unlock_id="day7_history_upgrade",
        name="Analysis History + Upgrade Offer",
        description="Track progress over time + special discount",
        day_available=7,
        feature_type="history",
        is_teaser=True,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class DayMetrics:
    """Metrics for a specific day."""
    day_number: int
    users_reached: int = 0
    users_engaged: int = 0
    engagement_rate: float = 0.0
    unlock_views: int = 0
    feature_uses: int = 0
    dropped_before: int = 0
    continued: int = 0


@dataclass
class Day7OfferMetrics:
    """Metrics for Day 7 offer."""
    offer_shown: int = 0
    offer_clicked: int = 0
    offer_dismissed: int = 0
    offer_claimed: int = 0
    conversion_rate: float = 0.0
    revenue_from_offer: float = 0.0
    avg_order_value: float = 0.0
    discount_percent: float = 20.0
    discount_given: float = 0.0


@dataclass
class ProgressiveHealth:
    """Overall progressive system health."""
    overall_score: float = 0.0
    progression_rate: float = 0.0
    engagement_score: float = 0.0
    conversion_score: float = 0.0
    day1_users: int = 0
    day3_users: int = 0
    day5_users: int = 0
    day7_users: int = 0
    day1_to_3_rate: float = 0.0
    day3_to_5_rate: float = 0.0
    day5_to_7_rate: float = 0.0
    free_to_paid_via_progressive: int = 0
    conversion_rate: float = 0.0
    day7_offer: Day7OfferMetrics = field(default_factory=Day7OfferMetrics)
    issues: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESSIVE TRACKER
# ═══════════════════════════════════════════════════════════════════════════

class ProgressiveTracker:
    """Tracks and optimizes the P3 Progressive Feature Unlocks system."""
    
    def __init__(self):
        self.unlocks = UNLOCKS
        self._user_progress: Dict[str, Dict] = {}
        self._unlock_events: List[Dict] = []
        self._day7_events: List[Dict] = []
        self._engagement_events: List[Dict] = []
        self._last_health: Optional[ProgressiveHealth] = None
        self._last_calculated: Optional[datetime] = None
    
    def track_user_started(self, user_id: str, country: str, referrer: Optional[str] = None) -> None:
        """Track user starting progressive journey."""
        self._user_progress[user_id] = {
            "user_id": user_id,
            "started_at": datetime.utcnow(),
            "current_day": 1,
            "country": country,
            "referrer": referrer,
            "days_active": [1],
            "unlocks_claimed": ["day1_basic_analysis"],
            "converted": False,
        }
    
    def track_day_reached(self, user_id: str, day_number: int) -> None:
        """Track user reaching a specific day."""
        if user_id in self._user_progress:
            self._user_progress[user_id]["current_day"] = day_number
            if day_number not in self._user_progress[user_id]["days_active"]:
                self._user_progress[user_id]["days_active"].append(day_number)
        
        self._engagement_events.append({
            "user_id": user_id,
            "type": "day_reached",
            "day_number": day_number,
            "timestamp": datetime.utcnow(),
        })
    
    def track_feature_unlocked(self, user_id: str, unlock_id: str, day_number: int) -> None:
        """Track a feature being unlocked."""
        if user_id in self._user_progress:
            if unlock_id not in self._user_progress[user_id]["unlocks_claimed"]:
                self._user_progress[user_id]["unlocks_claimed"].append(unlock_id)
        
        self._unlock_events.append({
            "user_id": user_id,
            "unlock_id": unlock_id,
            "day_number": day_number,
            "timestamp": datetime.utcnow(),
        })
    
    def track_feature_used(self, user_id: str, unlock_id: str, usage_seconds: float = 0) -> None:
        """Track user using an unlocked feature."""
        self._engagement_events.append({
            "user_id": user_id,
            "type": "feature_used",
            "unlock_id": unlock_id,
            "usage_seconds": usage_seconds,
            "timestamp": datetime.utcnow(),
        })
    
    def track_day7_offer_shown(self, user_id: str, discount_percent: float, products_shown: List[str]) -> None:
        """Track Day 7 offer being shown."""
        self._day7_events.append({
            "user_id": user_id,
            "type": "shown",
            "discount_percent": discount_percent,
            "products_shown": products_shown,
            "timestamp": datetime.utcnow(),
        })
    
    def track_day7_offer_claimed(self, user_id: str, product_purchased: str, 
                                   original_price: float, discounted_price: float, discount_percent: float) -> None:
        """Track Day 7 offer being claimed."""
        if user_id in self._user_progress:
            self._user_progress[user_id]["converted"] = True
        
        self._day7_events.append({
            "user_id": user_id,
            "type": "claimed",
            "product_purchased": product_purchased,
            "original_price": original_price,
            "discounted_price": discounted_price,
            "discount_percent": discount_percent,
            "discount_amount": original_price - discounted_price,
            "timestamp": datetime.utcnow(),
        })
    
    def track_day7_offer_dismissed(self, user_id: str, reason: Optional[str] = None) -> None:
        """Track Day 7 offer being dismissed."""
        self._day7_events.append({
            "user_id": user_id,
            "type": "dismissed",
            "reason": reason,
            "timestamp": datetime.utcnow(),
        })
    
    def get_day_metrics(self, day_number: int) -> DayMetrics:
        """Get metrics for a specific day."""
        reached = [u for u in self._user_progress.values() if day_number in u.get("days_active", [])]
        engaged_events = [e for e in self._engagement_events if e.get("day_number") == day_number]
        engaged_users = set(e["user_id"] for e in engaged_events)
        unlock_views = len([e for e in self._unlock_events if e.get("day_number") == day_number])
        feature_uses = len([e for e in self._engagement_events 
                           if e.get("type") == "feature_used" and e.get("unlock_id", "").startswith(f"day{day_number}")])
        
        return DayMetrics(
            day_number=day_number,
            users_reached=len(reached),
            users_engaged=len(engaged_users),
            engagement_rate=len(engaged_users) / len(reached) if reached else 0,
            unlock_views=unlock_views,
            feature_uses=feature_uses,
        )
    
    def get_day7_offer_metrics(self) -> Day7OfferMetrics:
        """Get Day 7 offer metrics."""
        shown = [e for e in self._day7_events if e.get("type") == "shown"]
        claimed = [e for e in self._day7_events if e.get("type") == "claimed"]
        dismissed = [e for e in self._day7_events if e.get("type") == "dismissed"]
        
        revenue = sum(e.get("discounted_price", 0) for e in claimed)
        discount_given = sum(e.get("discount_amount", 0) for e in claimed)
        
        return Day7OfferMetrics(
            offer_shown=len(shown),
            offer_claimed=len(claimed),
            offer_dismissed=len(dismissed),
            conversion_rate=len(claimed) / len(shown) if shown else 0,
            revenue_from_offer=revenue,
            avg_order_value=revenue / len(claimed) if claimed else 0,
            discount_given=discount_given,
        )
    
    def get_health(self) -> ProgressiveHealth:
        """Calculate overall progressive system health."""
        if (self._last_health and self._last_calculated and
            datetime.utcnow() - self._last_calculated < timedelta(minutes=5)):
            return self._last_health
        
        now = datetime.utcnow()
        day1 = self.get_day_metrics(1)
        day3 = self.get_day_metrics(3)
        day5 = self.get_day_metrics(5)
        day7 = self.get_day_metrics(7)
        
        d1_to_3 = day3.users_reached / day1.users_reached if day1.users_reached else 0
        d3_to_5 = day5.users_reached / day3.users_reached if day3.users_reached else 0
        d5_to_7 = day7.users_reached / day5.users_reached if day5.users_reached else 0
        progression_rate = day7.users_reached / day1.users_reached if day1.users_reached else 0
        
        day7_offer = self.get_day7_offer_metrics()
        converted_users = len([u for u in self._user_progress.values() if u.get("converted")])
        conversion_rate = converted_users / day7.users_reached if day7.users_reached else 0
        
        issues = []
        if d1_to_3 < 0.5:
            issues.append("High drop-off Day 1→3")
        if d5_to_7 < 0.7:
            issues.append("High drop-off Day 5→7")
        if day7_offer.conversion_rate < 0.15 and day7_offer.offer_shown > 20:
            issues.append("Low Day 7 offer conversion")
        
        health = ProgressiveHealth(
            overall_score=min(100, progression_rate * 50 + conversion_rate * 50),
            progression_rate=progression_rate * 100,
            day1_users=day1.users_reached,
            day3_users=day3.users_reached,
            day5_users=day5.users_reached,
            day7_users=day7.users_reached,
            day1_to_3_rate=d1_to_3,
            day3_to_5_rate=d3_to_5,
            day5_to_7_rate=d5_to_7,
            free_to_paid_via_progressive=converted_users,
            conversion_rate=conversion_rate,
            day7_offer=day7_offer,
            issues=issues,
            calculated_at=now,
        )
        
        self._last_health = health
        self._last_calculated = now
        return health
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Generate optimization suggestions."""
        suggestions = []
        health = self.get_health()
        
        if health.day1_to_3_rate < 0.5 and health.day1_users > 30:
            suggestions.append({
                "type": "unlock_timing",
                "unlock_id": "day3_voice_profile",
                "current_day": 3,
                "suggested_day": 2,
                "reason": "High Day 1→3 drop-off",
                "confidence": 0.65,
                "domain": "progressive",
            })
        
        if health.day7_offer.conversion_rate < 0.15 and health.day7_offer.offer_shown > 30:
            suggestions.append({
                "type": "day7_discount",
                "current_discount": health.day7_offer.discount_percent,
                "suggested_discount": 25,
                "reason": "Low Day 7 conversion rate",
                "confidence": 0.6,
                "domain": "progressive",
            })
        
        return suggestions


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_progressive_tracker: Optional[ProgressiveTracker] = None


def get_progressive_tracker() -> ProgressiveTracker:
    """Get singleton progressive tracker."""
    global _progressive_tracker
    if _progressive_tracker is None:
        _progressive_tracker = ProgressiveTracker()
    return _progressive_tracker
