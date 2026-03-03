"""
Share API — vanity slug profiles with OG meta for social sharing.
"""
from fastapi import APIRouter, HTTPException, Depends
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
RESERVED = {"admin","api","voice","blog","faq","settings","dashboard","signup","login","stretch","about","help","support","pro","free"}

from auth_api import require_auth

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
    profile = latest["profile"] if latest else None
    stance = latest["stance"] if latest else None
    confidence = None
    scores = None
    if latest:
        scores = {k.replace("score_",""):v for k,v in latest.items() if k.startswith("score_") and v is not None}
    totals = _q("""
        SELECT COALESCE(SUM(keystroke_words),0) as tw, COALESCE(SUM(analyses_count),0) as ta
        FROM daily_keystroke_totals WHERE user_id=%s
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
    return ShareProfileResponse(
        slug=slug, url=f"https://quirrely.ca/voice/{slug}",
        profile=profile, stance=stance, confidence=confidence,
        display_name=display_name
    )

@router.get("/me")
async def get_my_share(user: dict = Depends(require_auth)):
    uid = str(user["id"])
    row = _q("SELECT slug, display_name, profile, stance, confidence FROM share_profiles WHERE user_id=%s", (uid,))
    if not row:
        return {"has_share": False}
    return {"has_share": True, "slug": row["slug"], "url": f"https://quirrely.ca/voice/{row['slug']}",
            "profile": row["profile"], "display_name": row["display_name"]}

@router.post("/refresh")
async def refresh_share(user: dict = Depends(require_auth)):
    uid = str(user["id"])
    mine = _q("SELECT slug FROM share_profiles WHERE user_id=%s", (uid,))
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
    scores = None
    if latest:
        scores = {k.replace("score_",""):v for k,v in latest.items() if k.startswith("score_") and v is not None}
    _e("""
        UPDATE share_profiles SET profile=%s, stance=%s, confidence=%s, scores=%s,
        total_words=%s, total_analyses=%s, updated_at=NOW() WHERE user_id=%s
    """, (latest["profile"] if latest else None, latest["stance"] if latest else None,
          None, psycopg2.extras.Json(scores) if scores else None,
          totals["tw"] if totals else 0, totals["ta"] if totals else 0, uid))
    return {"refreshed": True, "slug": mine["slug"]}

def get_public_profile(slug: str):
    return _q("SELECT * FROM share_profiles WHERE slug=%s", (slug,))
