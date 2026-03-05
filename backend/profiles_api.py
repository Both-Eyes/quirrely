#!/usr/bin/env python3
"""
QUIRRELY PUBLIC PROFILES API v1.0
Profile viewing, username management, and showcase pages.

URL: /@username
Privacy: Private by default
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel

from profiles_config import (
    ProfileVisibility,
    DEFAULT_VISIBILITY,
    USERNAME_CHANGE_COOLDOWN_DAYS,
    BIO_MAX_LENGTH,
    SHOWCASE_PAGES,
    SHARE_PLATFORMS,
    SharePlatform,
    validate_username,
    get_profile_url,
    get_share_url,
    generate_og_tags,
    get_robots_directive,
    get_badges,
    PublicProfileContent,
)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/profiles", tags=["profiles"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class SetUsernameRequest(BaseModel):
    username: str


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    visibility: Optional[str] = None
    share_voice: Optional[bool] = None
    share_taste: Optional[bool] = None


class PublicProfileResponse(BaseModel):
    username: str
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    join_date: str
    
    # Voice (if sharing)
    voice_profile_type: Optional[str]
    voice_stance: Optional[str]
    voice_traits: Optional[List[str]]
    
    # Taste (if sharing)
    reading_taste_type: Optional[str]
    
    # Badges
    badges: List[Dict[str, str]]
    
    # Featured content
    featured_pieces: Optional[List[Dict]]
    curated_paths: Optional[List[Dict]]
    
    # Meta
    profile_url: str
    share_urls: Dict[str, str]
    og_tags: Dict[str, str]


class FeaturedMemberResponse(BaseModel):
    username: str
    display_name: str
    avatar_url: Optional[str]
    voice_profile_type: Optional[str]
    badges: List[Dict[str, str]]
    profile_url: str


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (Replace with database)
# ═══════════════════════════════════════════════════════════════════════════

_profiles: Dict[str, Dict] = {}
_usernames: Dict[str, str] = {}  # username -> user_id
_profile_views: Dict[str, int] = {}  # user_id -> view count


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    return None


def require_auth(authorization: Optional[str] = Header(None)) -> str:
    user_id = get_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


# ═══════════════════════════════════════════════════════════════════════════
# USERNAME MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/username/check")
async def check_username_availability(username: str):
    """Check if username is available."""
    validation = validate_username(username)
    
    if not validation.valid:
        return {"available": False, "error": validation.error}
    
    username_lower = username.lower()
    is_taken = username_lower in _usernames
    
    return {
        "available": not is_taken,
        "error": "Username is already taken" if is_taken else None,
    }


@router.post("/username")
async def set_username(
    request: SetUsernameRequest,
    user_id: str = Depends(require_auth),
):
    """Set or change username."""
    validation = validate_username(request.username)
    
    if not validation.valid:
        raise HTTPException(status_code=400, detail=validation.error)
    
    username_lower = request.username.lower()
    
    # Check if taken by someone else
    if username_lower in _usernames and _usernames[username_lower] != user_id:
        raise HTTPException(status_code=400, detail="Username is already taken")
    
    # Check cooldown
    profile = _profiles.get(user_id, {})
    last_change = profile.get("username_changed_at")
    if last_change:
        cooldown_end = last_change + timedelta(days=USERNAME_CHANGE_COOLDOWN_DAYS)
        if datetime.utcnow() < cooldown_end:
            days_left = (cooldown_end - datetime.utcnow()).days
            raise HTTPException(
                status_code=400, 
                detail=f"You can change your username again in {days_left} days"
            )
    
    # Remove old username
    old_username = profile.get("username")
    if old_username and old_username.lower() in _usernames:
        del _usernames[old_username.lower()]
    
    # Set new username
    _usernames[username_lower] = user_id
    
    if user_id not in _profiles:
        _profiles[user_id] = {}
    
    _profiles[user_id]["username"] = request.username
    _profiles[user_id]["username_lower"] = username_lower
    _profiles[user_id]["username_changed_at"] = datetime.utcnow()
    
    return {
        "success": True,
        "username": request.username,
        "profile_url": get_profile_url(username_lower),
    }


@router.get("/username")
async def get_my_username(user_id: str = Depends(require_auth)):
    """Get current user's username."""
    profile = _profiles.get(user_id, {})
    username = profile.get("username")
    
    return {
        "username": username,
        "profile_url": get_profile_url(username) if username else None,
        "can_change": True,  # Would check cooldown
    }


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/me")
async def get_my_profile(user_id: str = Depends(require_auth)):
    """Get current user's profile settings."""
    profile = _profiles.get(user_id, {})
    
    return {
        "username": profile.get("username"),
        "display_name": profile.get("display_name"),
        "bio": profile.get("bio"),
        "avatar_url": profile.get("avatar_url"),
        "visibility": profile.get("visibility", DEFAULT_VISIBILITY.value),
        "share_voice": profile.get("share_voice", False),
        "share_taste": profile.get("share_taste", False),
        "profile_url": get_profile_url(profile.get("username")) if profile.get("username") else None,
        "profile_views": _profile_views.get(user_id, 0),
    }


@router.patch("/me")
async def update_my_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(require_auth),
):
    """Update current user's profile."""
    if user_id not in _profiles:
        _profiles[user_id] = {}
    
    profile = _profiles[user_id]
    
    if request.display_name is not None:
        profile["display_name"] = request.display_name
    
    if request.bio is not None:
        if len(request.bio) > BIO_MAX_LENGTH:
            raise HTTPException(status_code=400, detail=f"Bio must be {BIO_MAX_LENGTH} characters or less")
        profile["bio"] = request.bio
    
    if request.avatar_url is not None:
        profile["avatar_url"] = request.avatar_url
    
    if request.visibility is not None:
        try:
            visibility = ProfileVisibility(request.visibility)
            profile["visibility"] = visibility.value
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid visibility setting")
    
    if request.share_voice is not None:
        profile["share_voice"] = request.share_voice
    
    if request.share_taste is not None:
        profile["share_taste"] = request.share_taste
    
    profile["updated_at"] = datetime.utcnow()
    
    return {"success": True}


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC PROFILE VIEWING
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/{username}")
async def get_public_profile(
    username: str,
    viewer_id: Optional[str] = Depends(get_user_id),
):
    """Get public profile by username."""
    username_lower = username.lower()
    
    # Find user ID
    user_id = _usernames.get(username_lower)
    if not user_id:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = _profiles.get(user_id, {})
    visibility = ProfileVisibility(profile.get("visibility", DEFAULT_VISIBILITY.value))
    
    # Check visibility
    is_owner = viewer_id == user_id
    
    if not is_owner:
        if visibility == ProfileVisibility.PRIVATE:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Track view (only non-owners)
        _profile_views[user_id] = _profile_views.get(user_id, 0) + 1
    
    # Build profile content
    content = PublicProfileContent(
        display_name=profile.get("display_name", username),
        username=profile.get("username", username),
        join_date=profile.get("join_date", "2026"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
    )
    
    # Voice profile (if sharing enabled)
    if profile.get("share_voice"):
        voice = profile.get("voice_profile", {})
        content.voice_profile_type = voice.get("type")
        content.voice_stance = voice.get("stance")
        content.voice_traits = voice.get("traits", [])[:5]
    
    # Reading taste (if sharing enabled)
    if profile.get("share_taste"):
        taste = profile.get("reading_taste", {})
        content.reading_taste_type = taste.get("type")
    
    # Recognition status
    content.is_featured_writer = profile.get("is_featured_writer", False)
    content.is_featured_curator = profile.get("is_featured_curator", False)
    content.is_authority_writer = profile.get("is_authority_writer", False)
    content.is_authority_curator = profile.get("is_authority_curator", False)
    
    # Featured content
    if content.is_featured_writer:
        content.featured_pieces = profile.get("featured_pieces", [])
    if content.is_featured_curator:
        content.curated_paths = profile.get("curated_paths", [])
    
    # Generate URLs and meta
    profile_url = get_profile_url(username_lower)
    full_url = f"https://quirrely.com{profile_url}"
    
    share_urls = {
        platform.value: get_share_url(platform, full_url, content.display_name)
        for platform in SHARE_PLATFORMS
    }
    share_urls["copy_link"] = full_url
    
    og_tags = generate_og_tags(content, profile_url)
    
    return {
        "username": content.username,
        "display_name": content.display_name,
        "avatar_url": content.avatar_url,
        "bio": content.bio,
        "join_date": content.join_date,
        
        "voice_profile_type": content.voice_profile_type,
        "voice_stance": content.voice_stance,
        "voice_traits": content.voice_traits,
        
        "reading_taste_type": content.reading_taste_type,
        
        "badges": get_badges(content),
        
        "featured_pieces": content.featured_pieces,
        "curated_paths": content.curated_paths,
        
        "profile_url": profile_url,
        "share_urls": share_urls,
        "og_tags": {
            "title": og_tags.title,
            "description": og_tags.description,
            "image": og_tags.image,
            "url": og_tags.url,
            "type": og_tags.type,
        },
        "robots": get_robots_directive(visibility),
        
        "is_owner": is_owner,
    }


# ═══════════════════════════════════════════════════════════════════════════
# FEATURED SHOWCASE PAGES
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/featured/writers")
async def get_featured_writers(
    page: int = 1,
    per_page: int = 24,
):
    """Get list of Featured Writers for showcase."""
    # Would query featured_writers table
    writers = [
        profile for profile in _profiles.values()
        if profile.get("is_featured_writer") and 
           profile.get("visibility") in [ProfileVisibility.PUBLIC.value, ProfileVisibility.FEATURED_ONLY.value]
    ]
    
    # Paginate
    total = len(writers)
    start = (page - 1) * per_page
    writers = writers[start:start + per_page]
    
    return {
        "writers": [
            {
                "username": w.get("username"),
                "display_name": w.get("display_name", w.get("username")),
                "avatar_url": w.get("avatar_url"),
                "voice_profile_type": w.get("voice_profile", {}).get("type") if w.get("share_voice") else None,
                "badges": get_badges(PublicProfileContent(
                    display_name=w.get("display_name", ""),
                    username=w.get("username", ""),
                    join_date="",
                    is_featured_writer=w.get("is_featured_writer", False),
                    is_authority_writer=w.get("is_authority_writer", False),
                )),
                "profile_url": get_profile_url(w.get("username", "")),
            }
            for w in writers
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "meta": SHOWCASE_PAGES["featured_writers"],
    }


@router.get("/featured/curators")
async def get_featured_curators(
    page: int = 1,
    per_page: int = 24,
):
    """Get list of Featured Curators for showcase."""
    curators = [
        profile for profile in _profiles.values()
        if profile.get("is_featured_curator") and 
           profile.get("visibility") in [ProfileVisibility.PUBLIC.value, ProfileVisibility.FEATURED_ONLY.value]
    ]
    
    total = len(curators)
    start = (page - 1) * per_page
    curators = curators[start:start + per_page]
    
    return {
        "curators": [
            {
                "username": c.get("username"),
                "display_name": c.get("display_name", c.get("username")),
                "avatar_url": c.get("avatar_url"),
                "reading_taste_type": c.get("reading_taste", {}).get("type") if c.get("share_taste") else None,
                "badges": get_badges(PublicProfileContent(
                    display_name=c.get("display_name", ""),
                    username=c.get("username", ""),
                    join_date="",
                    is_featured_curator=c.get("is_featured_curator", False),
                    is_authority_curator=c.get("is_authority_curator", False),
                )),
                "profile_url": get_profile_url(c.get("username", "")),
            }
            for c in curators
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "meta": SHOWCASE_PAGES["featured_curators"],
    }


@router.get("/featured/authority")
async def get_authority_members(
    page: int = 1,
    per_page: int = 24,
):
    """Get list of Authority members for showcase."""
    authorities = [
        profile for profile in _profiles.values()
        if (profile.get("is_authority_writer") or profile.get("is_authority_curator")) and 
           profile.get("visibility") in [ProfileVisibility.PUBLIC.value, ProfileVisibility.FEATURED_ONLY.value]
    ]
    
    total = len(authorities)
    start = (page - 1) * per_page
    authorities = authorities[start:start + per_page]
    
    return {
        "members": [
            {
                "username": a.get("username"),
                "display_name": a.get("display_name", a.get("username")),
                "avatar_url": a.get("avatar_url"),
                "badges": get_badges(PublicProfileContent(
                    display_name=a.get("display_name", ""),
                    username=a.get("username", ""),
                    join_date="",
                    is_featured_writer=a.get("is_featured_writer", False),
                    is_featured_curator=a.get("is_featured_curator", False),
                    is_authority_writer=a.get("is_authority_writer", False),
                    is_authority_curator=a.get("is_authority_curator", False),
                )),
                "profile_url": get_profile_url(a.get("username", "")),
            }
            for a in authorities
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "meta": SHOWCASE_PAGES["authority"],
    }


@router.get("/featured")
async def get_featured_landing():
    """Get combined Featured landing page data."""
    # Get counts
    featured_writers = len([p for p in _profiles.values() if p.get("is_featured_writer")])
    featured_curators = len([p for p in _profiles.values() if p.get("is_featured_curator")])
    authority_members = len([p for p in _profiles.values() if p.get("is_authority_writer") or p.get("is_authority_curator")])
    
    return {
        "counts": {
            "featured_writers": featured_writers,
            "featured_curators": featured_curators,
            "authority_members": authority_members,
        },
        "meta": SHOWCASE_PAGES["featured"],
        "sections": [
            SHOWCASE_PAGES["featured_writers"],
            SHOWCASE_PAGES["featured_curators"],
            SHOWCASE_PAGES["authority"],
        ],
    }
