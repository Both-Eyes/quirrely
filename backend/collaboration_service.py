#!/usr/bin/env python3
"""
QUIRRELY COLLABORATION SERVICE
Real database implementation for collaboration system.

Implements all database operations for writing partnerships using 
Quirrely's existing database connection patterns.
"""

import asyncio
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncpg
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION (Using Quirrely's pattern)
# ═══════════════════════════════════════════════════════════════════════════

class DatabaseConnection:
    """Database connection manager."""
    
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
db = DatabaseConnection()

async def get_db():
    """Get database connection."""
    return db


# ═══════════════════════════════════════════════════════════════════════════
# USER & ELIGIBILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def check_collaboration_eligibility(user_id: str) -> bool:
    """Check if user can start/join collaboration."""
    
    # Check if user is Pro tier
    user_tier_query = """
        SELECT COALESCE(s.tier, 'free') AS tier
        FROM users u
        LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active'
        WHERE u.id = $1
    """
    
    tier = await db.fetchval(user_tier_query, user_id)
    
    # Must be Pro tier or higher
    if tier not in ('pro', 'featured_writer', 'authority_writer', 
                    'curator', 'featured_curator', 'authority_curator'):
        return False
    
    # Check if user has active collaboration
    active_collab_query = """
        SELECT EXISTS(
            SELECT 1 FROM writing_partnerships 
            WHERE (initiator_user_id = $1 OR partner_user_id = $1)
              AND status IN ('pending', 'active')
        )
    """
    
    has_active = await db.fetchval(active_collab_query, user_id)
    return not has_active


async def find_user_by_email(email: str) -> Optional[Dict]:
    """Find user by email address."""
    query = """
        SELECT id, email, display_name, created_at
        FROM users 
        WHERE email = $1
    """
    
    row = await db.fetchrow(query, email.lower().strip())
    if row:
        return dict(row)
    return None


async def get_user_info(user_id: str) -> Dict:
    """Get user information."""
    query = """
        SELECT id, email, display_name
        FROM users 
        WHERE id = $1
    """
    
    row = await db.fetchrow(query, user_id)
    if row:
        return dict(row)
    
    # Return minimal info if not found
    return {"id": user_id, "email": "unknown", "display_name": "Unknown User"}


async def get_user_name(user_id: str) -> str:
    """Get user's display name."""
    query = "SELECT display_name FROM users WHERE id = $1"
    name = await db.fetchval(query, user_id)
    return name or "Unknown User"


# ═══════════════════════════════════════════════════════════════════════════
# INVITATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def check_invitation_limits(user_id: str) -> None:
    """Check if user has exceeded daily invitation limits."""
    
    # Check invitations sent today
    today_count_query = """
        SELECT invitations_sent_today 
        FROM user_collaboration_status 
        WHERE user_id = $1
    """
    
    count = await db.fetchval(today_count_query, user_id)
    
    if count and count >= 3:
        raise Exception("Daily invitation limit reached (3 per day)")
    
    # Check if it's a new day (reset counter)
    last_invite_query = """
        SELECT last_invitation_sent_at 
        FROM user_collaboration_status 
        WHERE user_id = $1
    """
    
    last_invite = await db.fetchval(last_invite_query, user_id)
    
    if last_invite and last_invite.date() < datetime.utcnow().date():
        # Reset daily counter
        await db.execute("""
            UPDATE user_collaboration_status 
            SET invitations_sent_today = 0 
            WHERE user_id = $1
        """, user_id)


async def create_collaboration_invitation(
    initiator_id: str,
    target_email: str,
    target_user_id: str,
    partnership_name: str,
    partnership_intention: str,
    partnership_type: str,
    invitation_token: str,
    expires_at: datetime
) -> str:
    """Create collaboration invitation record."""
    
    collaboration_id = str(uuid.uuid4())
    
    # Insert partnership record
    partnership_query = """
        INSERT INTO writing_partnerships (
            id, initiator_user_id, partner_user_id, partnership_name, 
            partnership_intention, partnership_type, status,
            invitation_token, invitation_sent_at, invitation_expires_at
        ) VALUES ($1, $2, $3, $4, $5, $6, 'pending', $7, $8, $9)
    """
    
    await db.execute(
        partnership_query,
        collaboration_id, initiator_id, target_user_id, partnership_name,
        partnership_intention, partnership_type, invitation_token,
        datetime.utcnow(), expires_at
    )
    
    return collaboration_id


async def update_invitation_tracking(user_id: str) -> None:
    """Update invitation tracking for spam prevention."""
    
    # Upsert user collaboration status
    upsert_query = """
        INSERT INTO user_collaboration_status (
            user_id, last_invitation_sent_at, invitations_sent_today
        ) VALUES ($1, $2, 1)
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            last_invitation_sent_at = $2,
            invitations_sent_today = user_collaboration_status.invitations_sent_today + 1
    """
    
    await db.execute(upsert_query, user_id, datetime.utcnow())


async def find_collaboration_by_token(token: str) -> Optional[Dict]:
    """Find collaboration by invitation token."""
    
    query = """
        SELECT wp.*, u.display_name as initiator_name
        FROM writing_partnerships wp
        JOIN users u ON wp.initiator_user_id = u.id
        WHERE wp.invitation_token = $1 
          AND wp.status = 'pending'
          AND wp.invitation_expires_at > $2
    """
    
    row = await db.fetchrow(query, token, datetime.utcnow())
    if row:
        return dict(row)
    return None


# ═══════════════════════════════════════════════════════════════════════════
# PARTNERSHIP MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

async def activate_collaboration(collaboration_id: str) -> None:
    """Activate collaboration after acceptance."""
    
    update_query = """
        UPDATE writing_partnerships 
        SET status = 'active',
            accepted_at = $1,
            started_at = $1,
            invitation_token = NULL
        WHERE id = $2
    """
    
    await db.execute(update_query, datetime.utcnow(), collaboration_id)


async def initialize_word_pools(collaboration_id: str) -> None:
    """Initialize word allocations for new collaboration."""
    
    # New tier allocation system:
    # Partnership users: 10k personal + share of 20k shared pool
    # Each partner gets 10k personal + 10k shared = 20k total per user
    
    update_query = """
        UPDATE writing_partnerships 
        SET shared_creative_space = 20000,
            shared_space_used = 0,
            initiator_solo_space_remaining = 10000,
            partner_solo_space_remaining = 10000,
            current_period_start = DATE_TRUNC('month', NOW()),
            current_period_end = DATE_TRUNC('month', NOW() + INTERVAL '1 month')
        WHERE id = $1
    """
    
    await db.execute(update_query, collaboration_id)


async def get_user_collaboration(user_id: str) -> Optional[Dict]:
    """Get user's current collaboration."""
    
    query = """
        SELECT wp.*, 
               ui.display_name as initiator_name, ui.email as initiator_email,
               up.display_name as partner_name, up.email as partner_email
        FROM writing_partnerships wp
        JOIN users ui ON wp.initiator_user_id = ui.id
        LEFT JOIN users up ON wp.partner_user_id = up.id
        WHERE (wp.initiator_user_id = $1 OR wp.partner_user_id = $1)
          AND wp.status IN ('pending', 'active')
        ORDER BY wp.created_at DESC
        LIMIT 1
    """
    
    row = await db.fetchrow(query, user_id)
    if row:
        return dict(row)
    return None


async def can_user_cancel_collaboration(user_id: str) -> bool:
    """Check if user can cancel collaboration (rate limiting)."""
    
    query = "SELECT can_user_cancel_collaboration($1)"
    result = await db.fetchval(query, user_id)
    return result


async def get_next_cancellation_date(user_id: str) -> datetime:
    """Get the next date when user can cancel a collaboration."""
    
    query = "SELECT get_next_cancellation_date($1)"
    result = await db.fetchval(query, user_id)
    return result


async def cancel_collaboration(collaboration_id: str, user_id: str) -> None:
    """Cancel collaboration with rate limiting."""
    
    # Check if user can cancel (rate limiting)
    can_cancel = await can_user_cancel_collaboration(user_id)
    if not can_cancel:
        next_date = await get_next_cancellation_date(user_id)
        raise ValueError(f"You can only cancel one collaboration per month. Next available: {next_date.strftime('%B %d, %Y')}")
    
    # Update collaboration status
    update_query = """
        UPDATE writing_partnerships 
        SET status = 'cancelled',
            cancelled_at = $1,
            cancelled_by = $2
        WHERE id = $3
    """
    
    await db.execute(update_query, datetime.utcnow(), user_id, collaboration_id)
    
    # Record the cancellation for rate limiting
    record_query = "SELECT record_collaboration_cancellation($1)"
    await db.execute(record_query, user_id)


# ═══════════════════════════════════════════════════════════════════════════
# WORD USAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_word_usage_history(user_id: str, collaboration_id: str) -> List[Dict]:
    """Get recent word usage history."""
    
    query = """
        SELECT usage_type, words_used, analysis_type, created_at
        FROM collaboration_word_usage 
        WHERE collaboration_id = $1 AND user_id = $2
        ORDER BY created_at DESC
        LIMIT 20
    """
    
    rows = await db.fetch(query, collaboration_id, user_id)
    return [dict(row) for row in rows]


async def record_word_usage(
    collaboration_id: str,
    user_id: str,
    words_used: int,
    usage_type: str,
    analysis_type: Optional[str] = None,
    analysis_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> None:
    """Record word usage in collaboration."""
    
    insert_query = """
        INSERT INTO collaboration_word_usage (
            collaboration_id, user_id, words_used, usage_type,
            analysis_type, analysis_id, session_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    
    await db.execute(
        insert_query,
        collaboration_id, user_id, words_used, usage_type,
        analysis_type, analysis_id, session_id
    )


async def update_word_allocation(collaboration_id: str, user_id: str, words_used: int, usage_type: str) -> None:
    """Update word allocation after usage."""
    
    if usage_type == 'shared':
        # Update shared pool
        update_query = """
            UPDATE writing_partnerships 
            SET shared_space_used = shared_space_used + $1
            WHERE id = $2
        """
        await db.execute(update_query, words_used, collaboration_id)
    
    else:  # solo usage
        # Determine which user's solo space to update
        partnership = await db.fetchrow("""
            SELECT initiator_user_id, partner_user_id 
            FROM writing_partnerships 
            WHERE id = $1
        """, collaboration_id)
        
        if user_id == partnership['initiator_user_id']:
            update_query = """
                UPDATE writing_partnerships 
                SET initiator_solo_space_remaining = initiator_solo_space_remaining - $1
                WHERE id = $2
            """
        else:
            update_query = """
                UPDATE writing_partnerships 
                SET partner_solo_space_remaining = partner_solo_space_remaining - $1
                WHERE id = $2
            """
        
        await db.execute(update_query, words_used, collaboration_id)


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED COLLABORATIONS
# ═══════════════════════════════════════════════════════════════════════════

async def get_featured_submission(collaboration_id: str) -> Optional[Dict]:
    """Get featured submission for collaboration."""
    
    query = """
        SELECT * FROM featured_collaborations 
        WHERE collaboration_id = $1
    """
    
    row = await db.fetchrow(query, collaboration_id)
    if row:
        return dict(row)
    return None


async def create_featured_submission(
    collaboration_id: str,
    submission_title: str,
    submission_summary: str,
    submission_tags: Optional[str],
    sample_text: str,
    word_count: int
) -> str:
    """Create featured collaboration submission."""
    
    submission_id = str(uuid.uuid4())
    
    insert_query = """
        INSERT INTO featured_collaborations (
            id, collaboration_id, submission_title, submission_summary,
            submission_tags, sample_text, word_count, status, submitted_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'submitted', $8)
    """
    
    await db.execute(
        insert_query,
        submission_id, collaboration_id, submission_title, submission_summary,
        submission_tags, sample_text, word_count, datetime.utcnow()
    )
    
    return submission_id


async def get_featured_collaborations(limit: int) -> List[Dict]:
    """Get currently featured collaborations."""
    
    query = """
        SELECT fc.id, fc.public_title, fc.public_description, 
               wp.partnership_type as category,
               ui.display_name as collaborator_1,
               up.display_name as collaborator_2,
               fc.featured_start_date, fc.views_count
        FROM featured_collaborations fc
        JOIN writing_partnerships wp ON fc.collaboration_id = wp.id
        JOIN users ui ON wp.initiator_user_id = ui.id
        JOIN users up ON wp.partner_user_id = up.id
        WHERE fc.status = 'featured'
          AND fc.featured_start_date <= CURRENT_DATE 
          AND fc.featured_end_date >= CURRENT_DATE
        ORDER BY fc.featured_start_date DESC
        LIMIT $1
    """
    
    rows = await db.fetch(query, limit)
    return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL SERVICE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

async def send_invitation_email(
    target_email: str,
    target_name: str,
    initiator_name: str,
    partnership_name: str,
    partnership_type: str,
    partnership_intention: str,
    invitation_token: str
) -> None:
    """Send invitation email to collaborator."""
    
    from email_templates import send_partnership_invitation_email
    
    await send_partnership_invitation_email(
        target_email=target_email,
        target_name=target_name,
        initiator_name=initiator_name,
        partnership_name=partnership_name,
        partnership_type=partnership_type,
        partnership_intention=partnership_intention,
        invitation_token=invitation_token
    )


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

async def initialize_collaboration_service(database_url: str):
    """Initialize the collaboration service with database connection."""
    await db.connect(database_url)
    logger.info("Collaboration service initialized with database connection")