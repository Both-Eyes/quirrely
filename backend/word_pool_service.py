#!/usr/bin/env python3
"""
QUIRRELY WORD POOL SERVICE
Comprehensive word allocation and rate limiting system for all user tiers.

New Word Pool Structure:
- Anonymous: 50 words/day
- Free Users: 250 words/day (7,500/month)
- Pro Users: 20,000 words/month
- Partnership: 10k personal + 10k shared = 20k total per user
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import asyncpg
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# WORD POOL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

class UserTier(Enum):
    ANONYMOUS = "anonymous"
    FREE = "free"
    PRO = "pro"
    PARTNERSHIP = "partnership"

# Word allocation limits
WORD_LIMITS = {
    UserTier.ANONYMOUS: {
        "daily_limit": 50,
        "period": "daily",
        "description": "Anonymous users get 50 words per day"
    },
    UserTier.FREE: {
        "daily_limit": 250,
        "monthly_limit": 7500,  # 250 * 30
        "period": "daily",
        "description": "Free users get 250 words per day"
    },
    UserTier.PRO: {
        "monthly_limit": 20000,
        "period": "monthly",
        "description": "Pro users get 20k words per month"
    },
    UserTier.PARTNERSHIP: {
        "personal_monthly": 10000,
        "shared_monthly": 20000,  # 10k per partner
        "total_per_user": 20000,  # 10k personal + 10k shared
        "period": "monthly",
        "description": "Partnership users get 10k personal + 10k shared"
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION (Reuse pattern from collaboration_service)
# ═══════════════════════════════════════════════════════════════════════════

class WordPoolDatabase:
    """Database operations for word pool tracking."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, database_url: str):
        """Connect to database."""
        self.pool = await asyncpg.create_pool(database_url)
    
    async def execute(self, query: str, *args):
        """Execute a query."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Fetch single value."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

# Global database instance
db = WordPoolDatabase()

# ═══════════════════════════════════════════════════════════════════════════
# WORD POOL TRACKING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_tier(user_id: Optional[str] = None) -> UserTier:
    """Determine user's tier for word pool allocation."""
    
    if not user_id:
        return UserTier.ANONYMOUS
    
    # Check if user has partnership
    partnership_query = """
        SELECT COUNT(*) FROM writing_partnerships 
        WHERE (initiator_user_id = $1 OR partner_user_id = $1) 
          AND status = 'active'
    """
    
    has_partnership = await db.fetchval(partnership_query, user_id)
    if has_partnership > 0:
        return UserTier.PARTNERSHIP
    
    # Check user subscription tier
    tier_query = "SELECT subscription_tier FROM users WHERE id = $1"
    subscription_tier = await db.fetchval(tier_query, user_id)
    
    if subscription_tier == "pro":
        return UserTier.PRO
    else:
        return UserTier.FREE


async def get_current_usage(user_id: Optional[str], period_type: str = "daily") -> Dict:
    """Get current word usage for user."""
    
    if not user_id:
        # Anonymous user - check daily usage by IP or session
        return {"used": 0, "limit": 50, "remaining": 50, "period": "daily"}
    
    user_tier = await get_user_tier(user_id)
    
    if period_type == "daily":
        # Get today's usage
        usage_query = """
            SELECT COALESCE(SUM(word_count), 0) as daily_used
            FROM user_word_usage 
            WHERE user_id = $1 
              AND usage_date = CURRENT_DATE
        """
        daily_used = await db.fetchval(usage_query, user_id) or 0
        
        if user_tier == UserTier.FREE:
            limit = WORD_LIMITS[UserTier.FREE]["daily_limit"]
            return {
                "used": daily_used,
                "limit": limit,
                "remaining": max(0, limit - daily_used),
                "period": "daily"
            }
        elif user_tier == UserTier.ANONYMOUS:
            limit = WORD_LIMITS[UserTier.ANONYMOUS]["daily_limit"]
            return {
                "used": daily_used,
                "limit": limit,
                "remaining": max(0, limit - daily_used),
                "period": "daily"
            }
    
    elif period_type == "monthly":
        # Get current month's usage
        usage_query = """
            SELECT COALESCE(SUM(word_count), 0) as monthly_used
            FROM user_word_usage 
            WHERE user_id = $1 
              AND usage_date >= DATE_TRUNC('month', CURRENT_DATE)
        """
        monthly_used = await db.fetchval(usage_query, user_id) or 0
        
        if user_tier == UserTier.PRO:
            limit = WORD_LIMITS[UserTier.PRO]["monthly_limit"]
            return {
                "used": monthly_used,
                "limit": limit,
                "remaining": max(0, limit - monthly_used),
                "period": "monthly"
            }
        elif user_tier == UserTier.PARTNERSHIP:
            # Partnership users have personal + shared pools
            return await get_partnership_usage(user_id)
    
    return {"used": 0, "limit": 0, "remaining": 0, "period": "unknown"}


async def get_partnership_usage(user_id: str) -> Dict:
    """Get word usage for partnership users (personal + shared)."""
    
    # Get user's partnership
    partnership_query = """
        SELECT id, shared_creative_space, shared_space_used,
               CASE 
                   WHEN initiator_user_id = $1 THEN initiator_solo_space_remaining
                   ELSE partner_solo_space_remaining
               END as personal_remaining,
               current_period_start, current_period_end
        FROM writing_partnerships 
        WHERE (initiator_user_id = $1 OR partner_user_id = $1) 
          AND status = 'active'
        LIMIT 1
    """
    
    partnership = await db.fetchrow(partnership_query, user_id)
    
    if not partnership:
        # Fallback to regular Pro tier if no partnership
        return await get_current_usage(user_id, "monthly")
    
    # Calculate personal usage this month
    personal_usage_query = """
        SELECT COALESCE(SUM(word_count), 0) as personal_used
        FROM user_word_usage 
        WHERE user_id = $1 
          AND usage_date >= DATE_TRUNC('month', CURRENT_DATE)
          AND pool_type = 'personal'
    """
    personal_used = await db.fetchval(personal_usage_query, user_id) or 0
    personal_limit = WORD_LIMITS[UserTier.PARTNERSHIP]["personal_monthly"]
    personal_remaining = personal_limit - personal_used
    
    # Shared pool info
    shared_limit = partnership["shared_creative_space"]
    shared_used = partnership["shared_space_used"]
    shared_remaining = shared_limit - shared_used
    user_shared_limit = shared_limit // 2  # Split between partners
    
    return {
        "personal": {
            "used": personal_used,
            "limit": personal_limit,
            "remaining": max(0, personal_remaining)
        },
        "shared": {
            "total_used": shared_used,
            "total_limit": shared_limit,
            "total_remaining": max(0, shared_remaining),
            "user_share_limit": user_shared_limit
        },
        "total": {
            "available": max(0, personal_remaining) + max(0, shared_remaining),
            "theoretical_max": personal_limit + user_shared_limit
        },
        "period": "monthly"
    }


async def check_word_limit(user_id: Optional[str], requested_words: int) -> Dict:
    """Check if user can use the requested number of words."""
    
    user_tier = await get_user_tier(user_id)
    
    if user_tier in [UserTier.ANONYMOUS, UserTier.FREE]:
        usage = await get_current_usage(user_id, "daily")
    else:
        usage = await get_current_usage(user_id, "monthly")
    
    # For partnership users, handle complex logic
    if user_tier == UserTier.PARTNERSHIP:
        partnership_usage = usage
        total_available = partnership_usage["total"]["available"]
        
        return {
            "allowed": requested_words <= total_available,
            "remaining": total_available,
            "tier": user_tier.value,
            "limit_type": "partnership",
            "usage_details": partnership_usage
        }
    
    # Standard tier logic
    remaining = usage.get("remaining", 0)
    
    return {
        "allowed": requested_words <= remaining,
        "remaining": remaining,
        "tier": user_tier.value,
        "limit_type": usage.get("period", "unknown"),
        "usage_details": usage
    }


async def record_word_usage(
    user_id: Optional[str], 
    word_count: int, 
    pool_type: str = "personal",
    session_id: Optional[str] = None
) -> bool:
    """Record word usage for a user."""
    
    if not user_id:
        # Handle anonymous user tracking by session
        if not session_id:
            return False
        
        # Record anonymous usage
        insert_query = """
            INSERT INTO anonymous_word_usage (session_id, word_count, usage_date, created_at)
            VALUES ($1, $2, CURRENT_DATE, NOW())
            ON CONFLICT (session_id, usage_date) 
            DO UPDATE SET 
                word_count = anonymous_word_usage.word_count + EXCLUDED.word_count,
                updated_at = NOW()
        """
        await db.execute(insert_query, session_id, word_count)
        return True
    
    # Record authenticated user usage
    insert_query = """
        INSERT INTO user_word_usage (user_id, word_count, usage_date, pool_type, created_at)
        VALUES ($1, $2, CURRENT_DATE, $3, NOW())
        ON CONFLICT (user_id, usage_date, pool_type)
        DO UPDATE SET 
            word_count = user_word_usage.word_count + EXCLUDED.word_count,
            updated_at = NOW()
    """
    
    await db.execute(insert_query, user_id, word_count, pool_type)
    
    # If partnership user using shared pool, update partnership record
    user_tier = await get_user_tier(user_id)
    if user_tier == UserTier.PARTNERSHIP and pool_type == "shared":
        await update_partnership_shared_usage(user_id, word_count)
    
    return True


async def update_partnership_shared_usage(user_id: str, word_count: int) -> None:
    """Update shared pool usage for partnership."""
    
    update_query = """
        UPDATE writing_partnerships 
        SET shared_space_used = shared_space_used + $2
        WHERE (initiator_user_id = $1 OR partner_user_id = $1) 
          AND status = 'active'
    """
    
    await db.execute(update_query, user_id, word_count)


# ═══════════════════════════════════════════════════════════════════════════
# USAGE ANALYTICS FOR META/OBSERVERS
# ═══════════════════════════════════════════════════════════════════════════

async def get_usage_analytics() -> Dict:
    """Get word pool usage analytics for Meta/Observers system."""
    
    analytics = {}
    
    # Usage by tier
    tier_usage_query = """
        SELECT 
            CASE 
                WHEN u.subscription_tier = 'pro' AND wp.id IS NOT NULL THEN 'partnership'
                WHEN u.subscription_tier IS NULL THEN 'anonymous'
                ELSE u.subscription_tier
            END as effective_tier,
            COUNT(DISTINCT u.id) as user_count,
            AVG(daily_usage.word_count) as avg_daily_usage,
            SUM(monthly_usage.word_count) as total_monthly_usage
        FROM users u
        LEFT JOIN writing_partnerships wp ON (wp.initiator_user_id = u.id OR wp.partner_user_id = u.id) 
                                          AND wp.status = 'active'
        LEFT JOIN (
            SELECT user_id, SUM(word_count) as word_count
            FROM user_word_usage 
            WHERE usage_date = CURRENT_DATE
            GROUP BY user_id
        ) daily_usage ON u.id = daily_usage.user_id
        LEFT JOIN (
            SELECT user_id, SUM(word_count) as word_count
            FROM user_word_usage 
            WHERE usage_date >= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY user_id
        ) monthly_usage ON u.id = monthly_usage.user_id
        GROUP BY effective_tier
    """
    
    tier_stats = await db.fetch(tier_usage_query)
    analytics["tier_usage"] = [dict(row) for row in tier_stats]
    
    # Conversion pressure points
    limit_approach_query = """
        SELECT 
            tier,
            COUNT(*) as users_near_limit,
            AVG(usage_percentage) as avg_usage_percentage
        FROM (
            SELECT 
                user_id,
                CASE WHEN subscription_tier = 'pro' THEN 'pro' ELSE 'free' END as tier,
                (daily_word_count / CASE WHEN subscription_tier = 'pro' THEN 666.67 ELSE 250 END) * 100 as usage_percentage
            FROM (
                SELECT 
                    uwu.user_id,
                    u.subscription_tier,
                    SUM(uwu.word_count) as daily_word_count
                FROM user_word_usage uwu
                JOIN users u ON uwu.user_id = u.id
                WHERE uwu.usage_date = CURRENT_DATE
                GROUP BY uwu.user_id, u.subscription_tier
            ) usage_data
        ) percentage_data
        WHERE usage_percentage > 80
        GROUP BY tier
    """
    
    limit_stats = await db.fetch(limit_approach_query)
    analytics["conversion_pressure"] = [dict(row) for row in limit_stats]
    
    return analytics


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

async def initialize_word_pool_tables() -> None:
    """Create tables for word pool tracking if they don't exist."""
    
    # User word usage table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS user_word_usage (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            usage_date DATE NOT NULL,
            pool_type TEXT DEFAULT 'personal',
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, usage_date, pool_type)
        )
    """)
    
    # Anonymous user tracking
    await db.execute("""
        CREATE TABLE IF NOT EXISTS anonymous_word_usage (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            usage_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(session_id, usage_date)
        )
    """)
    
    # Indexes for performance
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_word_usage_date 
        ON user_word_usage(user_id, usage_date);
    """)
    
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_anonymous_word_usage_date 
        ON anonymous_word_usage(session_id, usage_date);
    """)


async def main():
    """Test function."""
    # Connect to database (use your actual connection string)
    await db.connect("postgresql://user:pass@localhost/quirrely")
    await initialize_word_pool_tables()
    
    # Test usage checking
    result = await check_word_limit("test-user-id", 100)
    print(f"Word limit check result: {result}")


if __name__ == "__main__":
    asyncio.run(main())