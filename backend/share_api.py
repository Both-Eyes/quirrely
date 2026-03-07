"""
Share API — vanity slug profiles with OG meta for social sharing.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import os, re, psycopg2, psycopg2.extras

router = APIRouter(prefix="/api/v2/share", tags=["Share"])

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://quirrely:Quirr2026db@127.0.0.1:5432/quirrely_prod"
)

def _db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def _q(sql, params=None):
    conn = _db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    finally:
        conn.close()

def _e(sql, params=None):
    conn = _db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$")
RESERVED = {"admin","api","voice","user","blog","faq","settings","dashboard","signup","login","stretch","about","help","support","pro","free"}

from auth_api import require_auth
from og_generator import generate_og_image

class GenerateRequest(BaseModel):
    slug: str = Field(..., min_length=3, max_length=30)
    display_name: Optional[str] = Field(None, max_length=50)

class ShareProfileResponse(BaseModel):
    slug: str
    url: str
    profile: Optional[str] = None
    stance: Optional[str] = None
    confidence: Optional[float] = None
    display_name: Optional[str] = None

@router.post("/generate", response_model=ShareProfileResponse)
async def generate_share(req: GenerateRequest, user: dict = Depends(require_auth)):
    uid = str(user["id"])
    slug = req.slug.lower().strip()
    if not SLUG_RE.match(slug):
        raise HTTPException(400, "Slug must be 3-30 chars, lowercase alphanumeric + hyphens, no leading/trailing hyphens.")
    if slug in RESERVED:
        raise HTTPException(400, "That slug is reserved. Try another.")
    existing = _q("SELECT id, user_id FROM share_profiles WHERE slug=%s", (slug,))
    if existing and str(existing["user_id"]) != uid:
        raise HTTPException(409, "That slug is already taken. Try another.")
    latest = _q("""
        SELECT profile, stance, score_assertive, score_minimal, score_poetic, score_dense,
        score_conversational, score_formal, score_longform, score_interrogative, score_hedged
        FROM writing_profiles WHERE user_id=%s
        ORDER BY created_at DESC LIMIT 1
    """, (uid,))
    # Derive dominant profile from scores (matches dashboard behaviour)
    stance = latest["stance"] if latest else None
    if latest:
        sc = {k.replace("score_",""):v for k,v in latest.items() if k.startswith("score_") and v is not None}
        profile = max(sc, key=lambda k: sc[k]) if sc else latest["profile"]
    else:
        profile = None
    confidence = None
    scores = None
    if latest:
        scores = {k.replace("score_",""):v for k,v in latest.items() if k.startswith("score_") and v is not None}
    totals = _q("""
        SELECT COALESCE(SUM(keystroke_words),0) as tw, COALESCE(SUM(analyses_count),0) as ta
        FROM daily_keystroke_totals WHERE user_id=%s
    """, (uid,))
    # Fallback to writing_profiles if daily totals are empty
    if not totals or (totals["tw"]==0 and totals["ta"]==0):
        totals = _q("""
            SELECT COALESCE(SUM(input_word_count),0) as tw, COUNT(*) as ta
            FROM writing_profiles WHERE user_id=%s
        """, (uid,))
    tw = totals["tw"] if totals else 0
    ta = totals["ta"] if totals else 0
    display_name = req.display_name or user.get("display_name") or slug

    mine = _q("SELECT id FROM share_profiles WHERE user_id=%s", (uid,))
    if mine:
        _e("""
            UPDATE share_profiles SET slug=%s, display_name=%s, profile=%s, stance=%s,
            confidence=%s, scores=%s, total_words=%s, total_analyses=%s, updated_at=NOW()
            WHERE user_id=%s
        """, (slug, display_name, profile, stance, confidence,
              psycopg2.extras.Json(scores) if scores else None, tw, ta, uid))
    else:
        _e("""
            INSERT INTO share_profiles (user_id, slug, display_name, profile, stance,
            confidence, scores, total_words, total_analyses)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (uid, slug, display_name, profile, stance, confidence,
              psycopg2.extras.Json(scores) if scores else None, tw, ta))
    # Generate personalized OG image on claim
    try:
        generate_og_image(slug=slug, name=display_name, profile=profile or "UNKNOWN",
                         scores=scores or {}, total_words=tw, total_analyses=ta, stance=stance)
    except Exception as oge:
        import logging; logging.warning(f"OG image gen failed: {oge}")
    return ShareProfileResponse(
        slug=slug, url=f"https://quirrely.ca/user/{slug}",
        profile=profile, stance=stance, confidence=confidence,
        display_name=display_name
    )

@router.get("/me")
async def get_my_share(user: dict = Depends(require_auth)):
    uid = str(user["id"])
    row = _q("SELECT slug, display_name, profile, stance, confidence FROM share_profiles WHERE user_id=%s", (uid,))
    if not row:
        return {"has_share": False}
    return {"has_share": True, "slug": row["slug"], "url": f"https://quirrely.ca/user/{row['slug']}",
            "profile": row["profile"], "display_name": row["display_name"]}

@router.post("/refresh")
async def refresh_share(user: dict = Depends(require_auth)):
    uid = str(user["id"])
    mine = _q("SELECT slug, display_name FROM share_profiles WHERE user_id=%s", (uid,))
    if not mine:
        raise HTTPException(404, "No share profile found. Generate one first.")
    latest = _q("""
        SELECT profile, stance, score_assertive, score_minimal, score_poetic, score_dense,
        score_conversational, score_formal, score_longform, score_interrogative, score_hedged
        FROM writing_profiles WHERE user_id=%s
        ORDER BY created_at DESC LIMIT 1
    """, (uid,))
    totals = _q("""
        SELECT COALESCE(SUM(keystroke_words),0) as tw, COALESCE(SUM(analyses_count),0) as ta
        FROM daily_keystroke_totals WHERE user_id=%s
    """, (uid,))
    # Fallback to writing_profiles if daily totals are empty
    if not totals or (totals["tw"]==0 and totals["ta"]==0):
        totals = _q("""
            SELECT COALESCE(SUM(input_word_count),0) as tw, COUNT(*) as ta
            FROM writing_profiles WHERE user_id=%s
        """, (uid,))
    scores = None
    if latest:
        scores = {k.replace("score_",""):v for k,v in latest.items() if k.startswith("score_") and v is not None}
    _e("""
        UPDATE share_profiles SET profile=%s, stance=%s, confidence=%s, scores=%s,
        total_words=%s, total_analyses=%s, updated_at=NOW() WHERE user_id=%s
    """, (latest["profile"] if latest else None, latest["stance"] if latest else None,
          None, psycopg2.extras.Json(scores) if scores else None,
          totals["tw"] if totals else 0, totals["ta"] if totals else 0, uid))
    # Generate personalized OG image
    try:
        generate_og_image(
            slug=mine["slug"],
            name=mine.get("display_name") or mine["slug"],
            profile=latest["profile"] if latest else "UNKNOWN",
            scores=scores or {},
            total_words=totals["tw"] if totals else 0,
            total_analyses=totals["ta"] if totals else 0,
            stance=latest["stance"] if latest else None
        )
    except Exception as oge:
        import logging; logging.warning(f"OG image gen failed: {oge}")
    return {"refreshed": True, "slug": mine["slug"]}


class TrackRequest(BaseModel):
    ref: str = Field(..., min_length=1, max_length=30)
    action: str = Field(..., pattern="^(visit|analyze|signup)$")
    visitor_id: Optional[str] = Field(None, max_length=64)

@router.post("/referral/track")
async def track_referral(request: Request, req: TrackRequest):
    """Track a referral event (public, no auth needed)."""
    ref_profile = _q("SELECT user_id FROM share_profiles WHERE slug=%s", (req.ref,))
    _e("""INSERT INTO referrals (referrer_slug, referrer_user_id, visitor_id, action)
          VALUES (%s, %s, %s, %s)""",
       (req.ref, ref_profile["user_id"] if ref_profile else None,
        req.visitor_id, req.action))
    return {"tracked": True}

@router.get("/referral/stats")
async def referral_stats(user: dict = Depends(require_auth)):
    """Get referral stats for the authenticated user's share profile."""
    uid = str(user["id"])
    mine = _q("SELECT slug, display_name FROM share_profiles WHERE user_id=%s", (uid,))
    if not mine:
        return {"has_share": False, "stats": {}}
    slug = mine["slug"]
    conn = _db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""SELECT action, COUNT(*) as cnt FROM referrals
                       WHERE referrer_slug=%s GROUP BY action""", (slug,))
        rows = cur.fetchall()
        stats = {r["action"]: r["cnt"] for r in rows}
        cur.execute("SELECT COUNT(*) as total FROM referrals WHERE referrer_slug=%s", (slug,))
        total = cur.fetchone()["total"]
        conn.commit()
        return {"has_share": True, "slug": slug, "total": total, "stats": stats}
    finally:
        conn.close()

@router.get("/public/{slug}")
async def get_public_share(slug: str, request: Request):
    """Public endpoint to get a share profile by slug (no auth)."""
    import re as _re
    if not _re.match(r'^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$', slug):
        raise HTTPException(400, "Invalid slug")
    p = get_public_profile(slug)
    if not p:
        raise HTTPException(404, "Profile not found")
    return {
        "slug": p["slug"], "display_name": p.get("display_name"),
        "profile": p.get("profile"), "stance": p.get("stance"),
        "scores": p.get("scores"), "total_words": p.get("total_words"),
        "total_analyses": p.get("total_analyses")
    }

def get_public_profile(slug: str):
    return _q("SELECT * FROM share_profiles WHERE slug=%s", (slug,))
