#!/usr/bin/env python3
"""
QUIRRELY READER API ENDPOINTS
Tracks reading behavior and serves reading taste profiles.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/reader", tags=["reader"])


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & MODELS
# ═══════════════════════════════════════════════════════════════════════════

class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    READ_COMPLETE = "read_complete"
    CLICK_WRITER = "click_writer"
    CLICK_BOOK = "click_book"
    CLICK_FEATURED = "click_featured"
    BOOKMARK = "bookmark"
    DISMISS = "dismiss"
    MORE_LIKE_THIS = "more_like_this"


class ContentType(str, Enum):
    READING_POST = "reading_post"
    WRITING_POST = "writing_post"
    FEATURED_PIECE = "featured_piece"
    BOOK = "book"
    WRITER = "writer"


class ReaderEventRequest(BaseModel):
    event_type: EventType
    profile_type: str = Field(..., description="ASSERTIVE, MINIMAL, etc.")
    profile_stance: str = Field(..., description="OPEN, CLOSED, BALANCED, CONTRADICTORY")
    content_type: ContentType
    content_id: Optional[str] = None
    time_on_page_seconds: Optional[int] = None
    scroll_depth_percent: Optional[int] = Field(None, ge=0, le=100)
    affiliate_partner: Optional[str] = None


class ReaderEventResponse(BaseModel):
    success: bool
    event_id: str
    message: Optional[str] = None


class ReadingTasteResponse(BaseModel):
    inferred_profile_id: Optional[str]
    inferred_profile_type: Optional[str]
    inferred_profile_stance: Optional[str]
    confidence: float
    top_types: List[str]
    top_stances: List[str]
    profile_scores: Dict[str, float]
    total_posts_viewed: int
    total_books_clicked: int
    total_bookmarks: int
    writing_voice: Optional[str] = None
    taste_matches_voice: Optional[bool] = None


class BookmarkRequest(BaseModel):
    content_type: ContentType
    content_id: str
    profile_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None


class BookmarkResponse(BaseModel):
    success: bool
    bookmark_id: Optional[str] = None
    action: str  # "added" or "removed"


class RecommendationResponse(BaseModel):
    profile_id: str
    profile_type: str
    profile_stance: str
    title: str
    tagline: str
    reason: str
    url: str


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE METADATA (shared with frontend)
# ═══════════════════════════════════════════════════════════════════════════

PROFILE_META = {
    'ASSERTIVE-OPEN': {'title': 'The Confident Listener', 'tagline': 'Bold ideas, open ears'},
    'ASSERTIVE-CLOSED': {'title': 'The Commander', 'tagline': 'Decisive and direct'},
    'ASSERTIVE-BALANCED': {'title': 'The Measured Leader', 'tagline': 'Strong views, fair consideration'},
    'ASSERTIVE-CONTRADICTORY': {'title': 'The Confident Paradox', 'tagline': 'Embracing contradiction'},
    'MINIMAL-OPEN': {'title': 'The Quiet Inviter', 'tagline': 'Few words, much space'},
    'MINIMAL-CLOSED': {'title': 'The Essentialist', 'tagline': 'Nothing wasted'},
    'MINIMAL-BALANCED': {'title': 'The Brief Diplomat', 'tagline': 'Concise and fair'},
    'MINIMAL-CONTRADICTORY': {'title': 'The Zen Paradox', 'tagline': 'Simplicity in complexity'},
    'POETIC-OPEN': {'title': 'The Lyrical Explorer', 'tagline': 'Beauty seeking truth'},
    'POETIC-CLOSED': {'title': 'The Oracle', 'tagline': 'Truth dressed in beauty'},
    'POETIC-BALANCED': {'title': 'The Dual Painter', 'tagline': 'Light and shadow'},
    'POETIC-CONTRADICTORY': {'title': 'The Shadow Dancer', 'tagline': 'Opposites in harmony'},
    'DENSE-OPEN': {'title': 'The Curious Scholar', 'tagline': 'Deep and questioning'},
    'DENSE-CLOSED': {'title': 'The Authority', 'tagline': 'Thorough and certain'},
    'DENSE-BALANCED': {'title': 'The Synthesizer', 'tagline': 'Weaving perspectives'},
    'DENSE-CONTRADICTORY': {'title': 'The Complexity Theorist', 'tagline': 'Finding pattern in chaos'},
    'CONVERSATIONAL-OPEN': {'title': 'The Curious Friend', 'tagline': 'Warm and wondering'},
    'CONVERSATIONAL-CLOSED': {'title': 'The Straight Talker', 'tagline': 'Friendly and direct'},
    'CONVERSATIONAL-BALANCED': {'title': 'The Thoughtful Pal', 'tagline': 'Easy and fair'},
    'CONVERSATIONAL-CONTRADICTORY': {'title': 'The Honest Mess', 'tagline': 'Genuinely conflicted'},
    'FORMAL-OPEN': {'title': 'The Diplomatic Professional', 'tagline': 'Proper yet curious'},
    'FORMAL-CLOSED': {'title': 'The Executive', 'tagline': 'Professional certainty'},
    'FORMAL-BALANCED': {'title': 'The Impartial Analyst', 'tagline': 'Objective assessment'},
    'FORMAL-CONTRADICTORY': {'title': 'The Institutional Realist', 'tagline': 'Structured complexity'},
    'BALANCED-OPEN': {'title': 'The Humble Seeker', 'tagline': 'Genuinely uncertain'},
    'BALANCED-CLOSED': {'title': 'The Fair Judge', 'tagline': 'Considered conclusion'},
    'BALANCED-BALANCED': {'title': 'The True Moderate', 'tagline': 'Centered perspective'},
    'BALANCED-CONTRADICTORY': {'title': 'The Tension Holder', 'tagline': 'Comfortable with conflict'},
    'LONGFORM-OPEN': {'title': 'The Patient Explorer', 'tagline': 'Slow and searching'},
    'LONGFORM-CLOSED': {'title': 'The Thorough Advocate', 'tagline': 'Complete and convinced'},
    'LONGFORM-BALANCED': {'title': 'The Deep Diver', 'tagline': 'Comprehensive exploration'},
    'LONGFORM-CONTRADICTORY': {'title': 'The Complexity Navigator', 'tagline': 'Mapping contradictions'},
    'INTERROGATIVE-OPEN': {'title': 'The Questioner', 'tagline': 'Always asking'},
    'INTERROGATIVE-CLOSED': {'title': 'The Socratic', 'tagline': 'Questions that conclude'},
    'INTERROGATIVE-BALANCED': {'title': 'The Facilitator', 'tagline': 'Questions for all sides'},
    'INTERROGATIVE-CONTRADICTORY': {'title': 'The Koan Master', 'tagline': 'Questions without answers'},
    'HEDGED-OPEN': {'title': 'The Tentative Thinker', 'tagline': 'Careful and curious'},
    'HEDGED-CLOSED': {'title': 'The Careful Concluder', 'tagline': 'Qualified certainty'},
    'HEDGED-BALANCED': {'title': 'The Nuanced Voice', 'tagline': 'Thoughtfully uncertain'},
    'HEDGED-CONTRADICTORY': {'title': 'The Uncertain Sage', 'tagline': 'Wisdom in doubt'},
}


# ═══════════════════════════════════════════════════════════════════════════
# STORAGE (in-memory for now; replace with database)
# ═══════════════════════════════════════════════════════════════════════════

# In production, these would be database operations
_events_store: Dict[str, List[Dict]] = {}  # user_id/session_id -> events
_profile_store: Dict[str, Dict] = {}  # user_id -> computed profile
_bookmarks_store: Dict[str, List[Dict]] = {}  # user_id -> bookmarks


def get_user_events(user_id: str) -> List[Dict]:
    return _events_store.get(user_id, [])


def add_event(user_id: str, event: Dict) -> str:
    import uuid
    event_id = str(uuid.uuid4())
    event["id"] = event_id
    event["created_at"] = datetime.utcnow().isoformat()
    
    if user_id not in _events_store:
        _events_store[user_id] = []
    _events_store[user_id].append(event)
    
    return event_id


def compute_profile(user_id: str) -> Dict:
    """Compute reading taste profile from events."""
    events = get_user_events(user_id)
    
    if not events:
        return {
            "inferred_profile_id": None,
            "confidence": 0.0,
            "top_types": [],
            "top_stances": [],
            "profile_scores": {},
        }
    
    # Score weights by event type
    weights = {
        "read_complete": 3,
        "bookmark": 5,
        "more_like_this": 4,
        "click_book": 2,
        "click_writer": 2,
        "click_featured": 3,
        "page_view": 1,
        "dismiss": -3,
    }
    
    type_scores: Dict[str, float] = {}
    stance_scores: Dict[str, float] = {}
    profile_scores: Dict[str, float] = {}
    
    for event in events:
        weight = weights.get(event.get("event_type"), 0)
        ptype = event.get("profile_type")
        stance = event.get("profile_stance")
        profile_id = f"{ptype}-{stance}"
        
        type_scores[ptype] = type_scores.get(ptype, 0) + weight
        stance_scores[stance] = stance_scores.get(stance, 0) + weight
        profile_scores[profile_id] = profile_scores.get(profile_id, 0) + weight
    
    # Sort by score
    top_types = sorted(type_scores.keys(), key=lambda x: type_scores[x], reverse=True)
    top_stances = sorted(stance_scores.keys(), key=lambda x: stance_scores[x], reverse=True)
    
    # Infer dominant profile
    top_profile = max(profile_scores.keys(), key=lambda x: profile_scores[x]) if profile_scores else None
    
    # Calculate confidence (0-1 based on event count)
    confidence = min(1.0, len(events) / 20.0)
    
    profile = {
        "inferred_profile_id": top_profile,
        "inferred_profile_type": top_types[0] if top_types else None,
        "inferred_profile_stance": top_stances[0] if top_stances else None,
        "confidence": round(confidence, 2),
        "top_types": top_types[:5],
        "top_stances": top_stances,
        "profile_scores": {k: round(v, 2) for k, v in profile_scores.items()},
        "events_processed": len(events),
        "last_computed_at": datetime.utcnow().isoformat(),
    }
    
    _profile_store[user_id] = profile
    return profile


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_user_or_session(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> tuple[Optional[str], Optional[str]]:
    """Get user_id if authenticated, or session_id for anonymous."""
    user_id = None
    session_id = None
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            user_id = token[:36]
    
    if not user_id:
        # Use session cookie or generate session ID
        session_id = request.cookies.get("quirrely_session") or request.headers.get("X-Session-ID")
    
    return user_id, session_id


def get_country_code(request: Request) -> str:
    """Get country code from request (via header or geo-IP)."""
    # In production, use CF-IPCountry or similar
    return request.headers.get("CF-IPCountry", "US")


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/event", response_model=ReaderEventResponse)
async def record_event(
    event: ReaderEventRequest,
    request: Request,
):
    """Record a reader behavior event."""
    user_id, session_id = get_user_or_session(request)
    identifier = user_id or session_id or "anonymous"
    
    event_data = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event.event_type.value,
        "profile_type": event.profile_type,
        "profile_stance": event.profile_stance,
        "content_type": event.content_type.value,
        "content_id": event.content_id,
        "time_on_page_seconds": event.time_on_page_seconds,
        "scroll_depth_percent": event.scroll_depth_percent,
        "affiliate_partner": event.affiliate_partner,
        "country_code": get_country_code(request),
    }
    
    event_id = add_event(identifier, event_data)
    
    # Recompute profile if authenticated
    if user_id:
        compute_profile(user_id)
    
    return ReaderEventResponse(
        success=True,
        event_id=event_id,
    )


@router.get("/taste", response_model=ReadingTasteResponse)
async def get_reading_taste(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """Get the user's computed reading taste profile."""
    user_id, session_id = get_user_or_session(request, authorization)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required for reading taste profile"
        )
    
    # Compute fresh profile
    profile = compute_profile(user_id)
    
    # Get engagement stats
    events = get_user_events(user_id)
    posts_viewed = sum(1 for e in events if e.get("event_type") == "page_view")
    books_clicked = sum(1 for e in events if e.get("event_type") == "click_book")
    bookmarks = len(_bookmarks_store.get(user_id, []))
    
    return ReadingTasteResponse(
        inferred_profile_id=profile.get("inferred_profile_id"),
        inferred_profile_type=profile.get("inferred_profile_type"),
        inferred_profile_stance=profile.get("inferred_profile_stance"),
        confidence=profile.get("confidence", 0.0),
        top_types=profile.get("top_types", []),
        top_stances=profile.get("top_stances", []),
        profile_scores=profile.get("profile_scores", {}),
        total_posts_viewed=posts_viewed,
        total_books_clicked=books_clicked,
        total_bookmarks=bookmarks,
        # TODO: Add writing voice comparison
    )


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: Request,
    limit: int = 5,
    authorization: Optional[str] = Header(None),
):
    """Get personalized reading recommendations based on taste."""
    user_id, session_id = get_user_or_session(request, authorization)
    identifier = user_id or session_id
    
    if not identifier:
        # Return popular profiles for anonymous users
        popular = ["CONVERSATIONAL-OPEN", "ASSERTIVE-OPEN", "POETIC-OPEN", "MINIMAL-CLOSED", "BALANCED-BALANCED"]
        return [
            RecommendationResponse(
                profile_id=pid,
                profile_type=pid.split("-")[0],
                profile_stance=pid.split("-")[1],
                title=PROFILE_META[pid]["title"],
                tagline=PROFILE_META[pid]["tagline"],
                reason="Popular with readers",
                url=f"/blog/reading/{pid.lower()}",
            )
            for pid in popular[:limit]
        ]
    
    # Get user's profile
    profile = _profile_store.get(identifier) or compute_profile(identifier)
    scores = profile.get("profile_scores", {})
    
    if not scores:
        # No data yet - return diverse recommendations
        diverse = ["ASSERTIVE-OPEN", "POETIC-CLOSED", "CONVERSATIONAL-BALANCED", "DENSE-OPEN", "MINIMAL-CLOSED"]
        return [
            RecommendationResponse(
                profile_id=pid,
                profile_type=pid.split("-")[0],
                profile_stance=pid.split("-")[1],
                title=PROFILE_META[pid]["title"],
                tagline=PROFILE_META[pid]["tagline"],
                reason="Explore this style",
                url=f"/blog/reading/{pid.lower()}",
            )
            for pid in diverse[:limit]
        ]
    
    # Sort by score and return top recommendations
    sorted_profiles = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    recommendations = []
    for pid in sorted_profiles[:limit]:
        if pid in PROFILE_META:
            recommendations.append(RecommendationResponse(
                profile_id=pid,
                profile_type=pid.split("-")[0],
                profile_stance=pid.split("-")[1],
                title=PROFILE_META[pid]["title"],
                tagline=PROFILE_META[pid]["tagline"],
                reason="Based on your reading taste",
                url=f"/blog/reading/{pid.lower()}",
            ))
    
    return recommendations


@router.post("/bookmark", response_model=BookmarkResponse)
async def toggle_bookmark(
    bookmark: BookmarkRequest,
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """Add or remove a bookmark."""
    user_id, _ = get_user_or_session(request, authorization)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required to bookmark")
    
    if user_id not in _bookmarks_store:
        _bookmarks_store[user_id] = []
    
    # Check if already bookmarked
    existing = next(
        (b for b in _bookmarks_store[user_id] 
         if b["content_type"] == bookmark.content_type and b["content_id"] == bookmark.content_id),
        None
    )
    
    if existing:
        # Remove bookmark
        _bookmarks_store[user_id].remove(existing)
        return BookmarkResponse(success=True, action="removed")
    else:
        # Add bookmark
        import uuid
        new_bookmark = {
            "id": str(uuid.uuid4()),
            "content_type": bookmark.content_type.value,
            "content_id": bookmark.content_id,
            "profile_id": bookmark.profile_id,
            "title": bookmark.title,
            "url": bookmark.url,
            "created_at": datetime.utcnow().isoformat(),
        }
        _bookmarks_store[user_id].append(new_bookmark)
        
        # Record as event
        if bookmark.profile_id:
            ptype, stance = bookmark.profile_id.split("-")
            add_event(user_id, {
                "event_type": "bookmark",
                "profile_type": ptype,
                "profile_stance": stance,
                "content_type": bookmark.content_type.value,
                "content_id": bookmark.content_id,
            })
            compute_profile(user_id)
        
        return BookmarkResponse(success=True, bookmark_id=new_bookmark["id"], action="added")


@router.get("/bookmarks")
async def get_bookmarks(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """Get user's bookmarks."""
    user_id, _ = get_user_or_session(request, authorization)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    bookmarks = _bookmarks_store.get(user_id, [])
    return {"bookmarks": bookmarks, "count": len(bookmarks)}


@router.get("/compare")
async def compare_taste_and_voice(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    """Compare reading taste with writing voice."""
    user_id, _ = get_user_or_session(request, authorization)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get reading taste
    taste_profile = _profile_store.get(user_id) or compute_profile(user_id)
    reading_taste = taste_profile.get("inferred_profile_id")
    
    # TODO: Get writing voice from analyses table
    writing_voice = None  # Placeholder
    
    if not reading_taste:
        return {
            "has_reading_data": False,
            "has_writing_data": False,
            "message": "Keep reading to discover your taste!",
        }
    
    if not writing_voice:
        return {
            "has_reading_data": True,
            "has_writing_data": False,
            "reading_taste": reading_taste,
            "reading_taste_title": PROFILE_META.get(reading_taste, {}).get("title"),
            "message": "You know what you like to read. Now discover how you write!",
            "cta": "Analyze My Writing",
        }
    
    matches = reading_taste == writing_voice
    
    return {
        "has_reading_data": True,
        "has_writing_data": True,
        "reading_taste": reading_taste,
        "reading_taste_title": PROFILE_META.get(reading_taste, {}).get("title"),
        "writing_voice": writing_voice,
        "writing_voice_title": PROFILE_META.get(writing_voice, {}).get("title"),
        "matches": matches,
        "insight": (
            "You read what you write! Your taste and voice are aligned."
            if matches else
            f"Interesting! You're drawn to {PROFILE_META.get(reading_taste, {}).get('title')} writing, but you write as {PROFILE_META.get(writing_voice, {}).get('title')}."
        ),
    }
