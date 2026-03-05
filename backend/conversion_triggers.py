#!/usr/bin/env python3
"""
QUIRRELY CONVERSION TRIGGERS - NEW WORD POOL SYSTEM
Business logic and automated conversion optimization for new tier structure.

Conversion Flow:
Anonymous (50/day) → Free (250/day) → Pro (20k/month) → Partnership (10k+10k shared)
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import asyncpg
import logging

from word_pool_service import get_user_tier, get_current_usage, UserTier, WORD_LIMITS

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION TRIGGER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class TriggerType(Enum):
    USAGE_WARNING = "usage_warning"           # 80% limit reached
    LIMIT_APPROACHING = "limit_approaching"   # 90% limit reached  
    LIMIT_HIT = "limit_hit"                   # 100% limit reached
    TRIAL_CONVERSION = "trial_conversion"     # Free → Pro timing
    PARTNERSHIP_INVITE = "partnership_invite" # Pro → Partnership timing
    RETENTION_RISK = "retention_risk"         # User disengagement

# Trigger thresholds for each tier
TRIGGER_THRESHOLDS = {
    UserTier.ANONYMOUS: {
        "usage_warning": 0.8,      # 40 words used (80% of 50)
        "limit_approaching": 0.9,   # 45 words used (90% of 50)  
        "limit_hit": 1.0,          # 50 words used
        "urgency_level": "high",   # High conversion pressure
    },
    UserTier.FREE: {
        "usage_warning": 0.7,      # 175 words/day (70% of 250)
        "limit_approaching": 0.85,  # 212 words/day (85% of 250)
        "limit_hit": 1.0,          # 250 words used
        "urgency_level": "medium", # Medium conversion pressure
    },
    UserTier.PRO: {
        "usage_warning": 0.75,     # 15k words/month (75% of 20k)
        "limit_approaching": 0.9,   # 18k words/month (90% of 20k)
        "limit_hit": 1.0,          # 20k words used
        "urgency_level": "low",    # Low pressure (partnership upsell)
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION EVENT TRACKING
# ═══════════════════════════════════════════════════════════════════════════

class ConversionEventTracker:
    """Track conversion events for Meta/Observers integration."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
    
    async def track_conversion_event(
        self,
        user_id: Optional[str],
        event_type: TriggerType,
        current_tier: UserTier,
        usage_data: Dict,
        metadata: Optional[Dict] = None
    ) -> str:
        """Track a conversion-related event."""
        
        event_id = f"conv_{int(datetime.now().timestamp())}_{user_id or 'anon'}"
        
        event_data = {
            "event_id": event_id,
            "user_id": user_id,
            "event_type": event_type.value,
            "current_tier": current_tier.value,
            "usage_data": usage_data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in conversion events table
        await self.db.execute("""
            INSERT INTO conversion_events (
                event_id, user_id, event_type, current_tier, 
                usage_percentage, event_data, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """, 
        event_id, user_id, event_type.value, current_tier.value,
        usage_data.get('percentage', 0), json.dumps(event_data)
        )
        
        # Send to Meta/Observers for real-time optimization
        await self.send_to_meta_observers(event_data)
        
        return event_id
    
    async def send_to_meta_observers(self, event_data: Dict) -> None:
        """Send conversion event to Meta/Observers for optimization."""
        
        # This would integrate with your Meta/Observers system
        # For now, we'll log for the analytics pipeline
        
        meta_event = {
            "event_type": "conversion_trigger",
            "source": "word_pool_service", 
            "data": event_data,
            "optimization_hints": {
                "trigger_type": event_data["event_type"],
                "tier": event_data["current_tier"],
                "usage_level": event_data["usage_data"].get("percentage", 0),
                "urgency": TRIGGER_THRESHOLDS.get(
                    UserTier(event_data["current_tier"]), {}
                ).get("urgency_level", "medium")
            }
        }
        
        # Insert into meta_events for observer processing
        await self.db.execute("""
            INSERT INTO meta_events (
                event_type, source_service, event_data, 
                optimization_priority, created_at
            ) VALUES ($1, $2, $3, $4, NOW())
        """,
        "conversion_optimization",
        "word_pool_triggers", 
        json.dumps(meta_event),
        meta_event["optimization_hints"]["urgency"]
        )

# ═══════════════════════════════════════════════════════════════════════════
# CONVERSION TRIGGER ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class ConversionTriggerEngine:
    """Main engine for managing conversion triggers."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
        self.event_tracker = ConversionEventTracker(db_pool)
    
    async def check_conversion_triggers(
        self, 
        user_id: Optional[str], 
        current_word_count: int,
        session_id: Optional[str] = None
    ) -> List[Dict]:
        """Check if any conversion triggers should fire for this user."""
        
        triggers_fired = []
        
        # Get user's current tier and usage
        user_tier = await get_user_tier(user_id)
        
        if user_tier in [UserTier.ANONYMOUS, UserTier.FREE]:
            usage = await get_current_usage(user_id, "daily")
        else:
            usage = await get_current_usage(user_id, "monthly")
        
        # Calculate usage percentage
        if usage.get("limit", 0) > 0:
            usage_percentage = usage["used"] / usage["limit"]
        else:
            usage_percentage = 0
        
        # Check thresholds
        thresholds = TRIGGER_THRESHOLDS.get(user_tier, {})
        
        # Usage warning trigger (80-90% depending on tier)
        if (usage_percentage >= thresholds.get("usage_warning", 0.8) and 
            usage_percentage < thresholds.get("limit_approaching", 0.9)):
            
            trigger = await self.create_usage_warning_trigger(
                user_id, user_tier, usage, usage_percentage, session_id
            )
            triggers_fired.append(trigger)
        
        # Limit approaching trigger (90-95% depending on tier)  
        elif (usage_percentage >= thresholds.get("limit_approaching", 0.9) and
              usage_percentage < 1.0):
            
            trigger = await self.create_limit_approaching_trigger(
                user_id, user_tier, usage, usage_percentage, session_id
            )
            triggers_fired.append(trigger)
        
        # Limit hit trigger (100%)
        elif usage_percentage >= 1.0:
            trigger = await self.create_limit_hit_trigger(
                user_id, user_tier, usage, usage_percentage, session_id
            )
            triggers_fired.append(trigger)
        
        # Check for additional behavioral triggers
        additional_triggers = await self.check_behavioral_triggers(
            user_id, user_tier, usage_percentage
        )
        triggers_fired.extend(additional_triggers)
        
        return triggers_fired
    
    async def create_usage_warning_trigger(
        self,
        user_id: Optional[str],
        tier: UserTier,
        usage: Dict,
        usage_percentage: float,
        session_id: Optional[str]
    ) -> Dict:
        """Create usage warning trigger."""
        
        # Track the event
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.USAGE_WARNING,
            tier,
            {"percentage": usage_percentage * 100, **usage},
            {"session_id": session_id}
        )
        
        # Generate appropriate messaging
        if tier == UserTier.ANONYMOUS:
            message = f"You've used {usage['used']} of your {usage['limit']} daily words."
            cta_text = "Sign up free for 250 words/day"
            cta_action = "signup"
            urgency = "medium"
            
        elif tier == UserTier.FREE:
            remaining_words = usage['remaining']
            message = f"Only {remaining_words} words remaining today."
            cta_text = "Upgrade to Pro for 20k words/month"
            cta_action = "upgrade_pro"
            urgency = "medium"
            
        else:  # PRO tier
            remaining_words = usage['remaining'] 
            message = f"You have {remaining_words:,} words remaining this month."
            cta_text = "Start a partnership for collaborative writing"
            cta_action = "partnership_invite"
            urgency = "low"
        
        return {
            "trigger_type": TriggerType.USAGE_WARNING.value,
            "event_id": event_id,
            "user_id": user_id,
            "session_id": session_id,
            "tier": tier.value,
            "usage_percentage": usage_percentage * 100,
            "message": message,
            "cta_text": cta_text,
            "cta_action": cta_action,
            "urgency": urgency,
            "display_type": "banner",  # or "modal", "notification"
            "auto_dismiss": False
        }
    
    async def create_limit_approaching_trigger(
        self,
        user_id: Optional[str],
        tier: UserTier,
        usage: Dict,
        usage_percentage: float,
        session_id: Optional[str]
    ) -> Dict:
        """Create limit approaching trigger (high urgency)."""
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.LIMIT_APPROACHING,
            tier,
            {"percentage": usage_percentage * 100, **usage},
            {"session_id": session_id, "high_urgency": True}
        )
        
        if tier == UserTier.ANONYMOUS:
            remaining = usage['remaining']
            message = f"Only {remaining} words left today! Don't lose your progress."
            cta_text = "Sign up now (Free)"
            urgency = "high"
            
        elif tier == UserTier.FREE:
            remaining = usage['remaining']
            message = f"Running low: only {remaining} words left today!"
            cta_text = "Upgrade to Pro (Unlimited monthly)"
            urgency = "high"
            
        else:  # PRO
            remaining = usage['remaining']
            message = f"Approaching monthly limit: {remaining:,} words remaining."
            cta_text = "Start partnership for shared pool"
            urgency = "medium"
        
        return {
            "trigger_type": TriggerType.LIMIT_APPROACHING.value,
            "event_id": event_id,
            "user_id": user_id,
            "session_id": session_id,
            "tier": tier.value,
            "usage_percentage": usage_percentage * 100,
            "message": message,
            "cta_text": cta_text,
            "cta_action": "urgent_upgrade",
            "urgency": urgency,
            "display_type": "modal",  # More prominent display
            "auto_dismiss": False,
            "highlight_benefits": True
        }
    
    async def create_limit_hit_trigger(
        self,
        user_id: Optional[str],
        tier: UserTier,
        usage: Dict,
        usage_percentage: float,
        session_id: Optional[str]
    ) -> Dict:
        """Create limit hit trigger (maximum urgency)."""
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.LIMIT_HIT,
            tier,
            {"percentage": usage_percentage * 100, **usage},
            {"session_id": session_id, "blocked": True}
        )
        
        if tier == UserTier.ANONYMOUS:
            message = "Daily limit reached! Sign up to continue with 250 words/day."
            cta_text = "Continue with Free Account"
            reset_time = "tomorrow"
            
        elif tier == UserTier.FREE:
            message = "Daily limit reached! Upgrade for 80x more words monthly."
            cta_text = "Upgrade to Pro Now"
            reset_time = "tomorrow"
            
        else:  # PRO
            message = "Monthly limit reached. Start a partnership for additional words."
            cta_text = "Start Partnership"
            reset_time = "next month"
        
        return {
            "trigger_type": TriggerType.LIMIT_HIT.value,
            "event_id": event_id,
            "user_id": user_id,
            "session_id": session_id,
            "tier": tier.value,
            "usage_percentage": 100.0,
            "message": message,
            "cta_text": cta_text,
            "cta_action": "immediate_upgrade",
            "urgency": "critical",
            "display_type": "blocking_modal",  # Blocks further usage
            "auto_dismiss": False,
            "reset_time": reset_time,
            "show_usage_reset_countdown": True
        }
    
    async def check_behavioral_triggers(
        self, 
        user_id: Optional[str], 
        tier: UserTier, 
        usage_percentage: float
    ) -> List[Dict]:
        """Check for behavioral-based conversion triggers."""
        
        triggers = []
        
        if not user_id:  # Anonymous user behavioral triggers
            # Check if user has hit limit multiple times
            repeated_limits = await self.check_repeated_limit_hits(None, "session")
            if repeated_limits >= 2:
                triggers.append(await self.create_persistent_user_trigger(None, tier))
        
        else:  # Authenticated user behavioral triggers
            
            # Trial conversion timing (Free users after 7 days)
            if tier == UserTier.FREE:
                days_since_signup = await self.get_days_since_signup(user_id)
                if days_since_signup >= 7 and usage_percentage > 0.6:  # Active user
                    triggers.append(await self.create_trial_conversion_trigger(user_id))
            
            # Partnership invitation timing (Pro users)
            elif tier == UserTier.PRO:
                months_since_pro = await self.get_months_since_pro_upgrade(user_id)
                monthly_usage = await self.get_average_monthly_usage(user_id)
                
                if months_since_pro >= 1 and monthly_usage > 15000:  # Heavy usage
                    triggers.append(await self.create_partnership_invite_trigger(user_id))
            
            # Retention risk detection
            risk_score = await self.calculate_retention_risk(user_id, tier)
            if risk_score > 0.7:  # High risk of churn
                triggers.append(await self.create_retention_trigger(user_id, tier, risk_score))
        
        return triggers
    
    async def create_trial_conversion_trigger(self, user_id: str) -> Dict:
        """Create trial conversion trigger for free users."""
        
        usage = await get_current_usage(user_id, "daily")
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.TRIAL_CONVERSION,
            UserTier.FREE,
            usage,
            {"conversion_opportunity": "trial_to_pro"}
        )
        
        return {
            "trigger_type": TriggerType.TRIAL_CONVERSION.value,
            "event_id": event_id,
            "user_id": user_id,
            "tier": UserTier.FREE.value,
            "message": "Ready for unlimited writing? You've been actively using Quirrely!",
            "cta_text": "Upgrade to Pro - First month 50% off",
            "cta_action": "trial_conversion_offer",
            "urgency": "medium",
            "display_type": "feature_highlight",
            "discount_offer": "50_percent_first_month",
            "social_proof": True
        }
    
    async def create_partnership_invite_trigger(self, user_id: str) -> Dict:
        """Create partnership invitation trigger for Pro users."""
        
        usage = await get_current_usage(user_id, "monthly")
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.PARTNERSHIP_INVITE,
            UserTier.PRO,
            usage,
            {"partnership_opportunity": "collaborative_writing"}
        )
        
        return {
            "trigger_type": TriggerType.PARTNERSHIP_INVITE.value,
            "event_id": event_id,
            "user_id": user_id,
            "tier": UserTier.PRO.value,
            "message": "You're a power user! Consider partnering with another writer.",
            "cta_text": "Find Writing Partner",
            "cta_action": "partnership_discovery",
            "urgency": "low",
            "display_type": "suggestion_card",
            "partnership_benefits": [
                "Shared 20k word pool",
                "Collaborative features", 
                "Mutual inspiration",
                "Expanded creative space"
            ]
        }
    
    # Helper methods
    async def check_repeated_limit_hits(self, user_id: Optional[str], period: str) -> int:
        """Count how many times user has hit limits in period."""
        if user_id:
            query = """
                SELECT COUNT(*) FROM conversion_events 
                WHERE user_id = $1 AND event_type = 'limit_hit' 
                AND created_at >= NOW() - INTERVAL '7 days'
            """
            return await self.db.fetchval(query, user_id) or 0
        else:
            # For anonymous users, we'd need session tracking
            return 0
    
    async def get_days_since_signup(self, user_id: str) -> int:
        """Get days since user signed up."""
        query = "SELECT EXTRACT(DAY FROM NOW() - created_at) FROM users WHERE id = $1"
        return await self.db.fetchval(query, user_id) or 0
    
    async def get_months_since_pro_upgrade(self, user_id: str) -> int:
        """Get months since user upgraded to Pro."""
        # This would need subscription history tracking
        return 1  # Placeholder
    
    async def get_average_monthly_usage(self, user_id: str) -> int:
        """Get user's average monthly word usage."""
        query = """
            SELECT AVG(monthly_total) FROM (
                SELECT EXTRACT(MONTH FROM usage_date) as month,
                       SUM(word_count) as monthly_total
                FROM user_word_usage 
                WHERE user_id = $1 
                  AND usage_date >= NOW() - INTERVAL '3 months'
                GROUP BY EXTRACT(MONTH FROM usage_date)
            ) monthly_usage
        """
        return await self.db.fetchval(query, user_id) or 0
    
    async def calculate_retention_risk(self, user_id: str, tier: UserTier) -> float:
        """Calculate user's retention risk score (0-1)."""
        # Simplified risk calculation
        # Real implementation would use ML model
        
        # Check recent usage decline
        recent_usage = await self.db.fetchval("""
            SELECT AVG(word_count) FROM user_word_usage 
            WHERE user_id = $1 AND usage_date >= NOW() - INTERVAL '7 days'
        """, user_id) or 0
        
        historical_usage = await self.db.fetchval("""
            SELECT AVG(word_count) FROM user_word_usage 
            WHERE user_id = $1 AND usage_date BETWEEN NOW() - INTERVAL '30 days' 
                                                 AND NOW() - INTERVAL '7 days'
        """, user_id) or 1
        
        usage_decline = 1 - (recent_usage / historical_usage) if historical_usage > 0 else 0
        return max(0, min(1, usage_decline))  # Clamp to 0-1
    
    async def create_retention_trigger(self, user_id: str, tier: UserTier, risk_score: float) -> Dict:
        """Create retention-focused trigger."""
        
        usage = await get_current_usage(user_id, "daily" if tier == UserTier.FREE else "monthly")
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.RETENTION_RISK,
            tier,
            {**usage, "risk_score": risk_score},
            {"retention_intervention": True}
        )
        
        return {
            "trigger_type": TriggerType.RETENTION_RISK.value,
            "event_id": event_id,
            "user_id": user_id,
            "tier": tier.value,
            "message": "We miss your writing! Here's inspiration to get back on track.",
            "cta_text": "Resume Writing Journey",
            "cta_action": "retention_engagement",
            "urgency": "medium",
            "display_type": "encouragement_message",
            "risk_score": risk_score,
            "personalized_content": True
        }
    
    async def create_persistent_user_trigger(self, user_id: Optional[str], tier: UserTier) -> Dict:
        """Create trigger for persistent anonymous users."""
        
        event_id = await self.event_tracker.track_conversion_event(
            user_id,
            TriggerType.LIMIT_HIT,
            tier,
            {"repeated_usage": True},
            {"persistent_user": True}
        )
        
        return {
            "trigger_type": "persistent_anonymous",
            "event_id": event_id,
            "user_id": user_id,
            "tier": tier.value,
            "message": "You keep coming back! Join free for unlimited daily writing analysis.",
            "cta_text": "Claim Your Free Account",
            "cta_action": "persistent_signup",
            "urgency": "high",
            "display_type": "loyalty_offer",
            "special_offer": "VIP treatment for persistent users"
        }

# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION WITH META/OBSERVERS
# ═══════════════════════════════════════════════════════════════════════════

async def initialize_conversion_triggers(db_pool: asyncpg.Pool) -> ConversionTriggerEngine:
    """Initialize the conversion trigger engine."""
    
    # Create tables if they don't exist
    await db_pool.execute("""
        CREATE TABLE IF NOT EXISTS conversion_events (
            id SERIAL PRIMARY KEY,
            event_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            event_type TEXT NOT NULL,
            current_tier TEXT NOT NULL,
            usage_percentage NUMERIC,
            event_data JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    await db_pool.execute("""
        CREATE TABLE IF NOT EXISTS meta_events (
            id SERIAL PRIMARY KEY,
            event_type TEXT NOT NULL,
            source_service TEXT NOT NULL,
            event_data JSONB,
            optimization_priority TEXT DEFAULT 'medium',
            processed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Create indexes
    await db_pool.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversion_events_user_type 
        ON conversion_events(user_id, event_type, created_at);
    """)
    
    await db_pool.execute("""
        CREATE INDEX IF NOT EXISTS idx_meta_events_processing 
        ON meta_events(event_type, processed_at, optimization_priority);
    """)
    
    return ConversionTriggerEngine(db_pool)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Example usage of conversion triggers."""
    
    # Connect to database
    db_pool = await asyncpg.create_pool("postgresql://user:pass@localhost/quirrely")
    
    # Initialize trigger engine
    trigger_engine = await initialize_conversion_triggers(db_pool)
    
    # Example: Check triggers for a user who just used 45 words (90% of anonymous limit)
    triggers = await trigger_engine.check_conversion_triggers(
        user_id=None,  # Anonymous user
        current_word_count=45,
        session_id="session_123"
    )
    
    print(f"Triggered {len(triggers)} conversion events:")
    for trigger in triggers:
        print(f"- {trigger['trigger_type']}: {trigger['message']}")
        print(f"  CTA: {trigger['cta_text']} (urgency: {trigger['urgency']})")
        print()

if __name__ == "__main__":
    asyncio.run(main())