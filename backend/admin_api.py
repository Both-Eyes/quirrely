"""Quirrely Admin API v2 — FastAPI router"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
import subprocess, json, os

router = APIRouter()

import os
from fastapi import Header

def verify_admin(x_admin_key: str = Header(None)):
    key = os.getenv("ADMIN_API_KEY","")
    if not key or x_admin_key != key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True



def get_db_stat(sql):
    try:
        r = subprocess.run(["sudo","-u","postgres","psql","-d","quirrely_prod","-t","-c",sql],
            capture_output=True, text=True, timeout=10)
        return r.stdout.strip(), r.returncode == 0
    except: return "", False

@router.get("/health")
def admin_health():
    return {"status":"healthy","api":"admin_v2","timestamp":datetime.now(timezone.utc).isoformat()}

@router.get("/overview")
def admin_overview(auth=Depends(verify_admin)):
    users,_   = get_db_stat("SELECT COUNT(*) FROM users;")
    subs,_    = get_db_stat("SELECT COUNT(*) FROM subscriptions WHERE status='active';")
    waitlist,_= get_db_stat("SELECT COUNT(*) FROM waitlist;")
    return {
        "users": int(users) if users.isdigit() else 0,
        "active_subscriptions": int(subs) if subs.isdigit() else 0,
        "waitlist": int(waitlist) if waitlist.isdigit() else 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/system")
def admin_system():
    return {
        "api": "healthy",
        "version": "3.1.3",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/stats/real")
async def get_real_stats(admin: str = Depends(verify_admin)):
    """Real database stats for Command Center."""
    import asyncpg
    from datetime import datetime, timedelta
    dsn = os.environ.get("DATABASE_URL")
    conn = await asyncpg.connect(dsn)
    try:
        now = datetime.utcnow()
        d1 = now - timedelta(hours=24)
        d7 = now - timedelta(days=7)
        r = {}
        r['users'] = await conn.fetchval("SELECT count(*) FROM users")
        r['users_24h'] = await conn.fetchval("SELECT count(*) FROM users WHERE created_at > $1", d1)
        r['users_7d'] = await conn.fetchval("SELECT count(*) FROM users WHERE created_at > $1", d7)
        r['analyses'] = await conn.fetchval("SELECT count(*) FROM writing_profiles")
        r['active_subs'] = await conn.fetchval("SELECT count(*) FROM subscriptions WHERE status='active'")
        r['newsletter'] = await conn.fetchval("SELECT count(*) FROM newsletter_subscribers")
        r['total_events'] = await conn.fetchval("SELECT count(*) FROM analytics_events")
        r['events_24h'] = await conn.fetchval("SELECT count(*) FROM analytics_events WHERE created_at > $1", d1)
        r['unique_visitors_24h'] = await conn.fetchval("SELECT count(DISTINCT user_hash) FROM analytics_events WHERE created_at > $1", d1)
        r['page_views_24h'] = await conn.fetchval("SELECT count(*) FROM analytics_events WHERE event_name='page_view' AND created_at > $1", d1)
        r['signups_24h'] = await conn.fetchval("SELECT count(*) FROM users WHERE created_at > $1", d1)
        r['analyses_24h'] = await conn.fetchval("SELECT count(*) FROM writing_profiles WHERE created_at > $1", d1)
        tiers = await conn.fetch("SELECT subscription_tier, count(*) as c FROM users GROUP BY subscription_tier")
        r['tiers'] = {row['subscription_tier']: row['c'] for row in tiers}
        events = await conn.fetch("SELECT event_name, count(*) as c FROM analytics_events WHERE created_at > $1 GROUP BY event_name ORDER BY c DESC", d1)
        r['events_breakdown'] = {row['event_name']: row['c'] for row in events}
        r['timestamp'] = now.isoformat()
        return r
    finally:
        await conn.close()
