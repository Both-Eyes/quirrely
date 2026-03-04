#!/usr/bin/env python3
"""
QUIRRELY AUTHENTICATION API v2.0
Secure, DB-backed authentication with bcrypt and parameterized queries.

Changes from v1.0:
- Replaced subprocess psql calls with psycopg2 (parameterized queries)
- Password hashes stored in users.password_hash column (survives restarts)
- Sessions stored in auth_sessions table (DB-backed, not in-memory)
- Login properly verifies bcrypt hash from DB
- Password change uses bcrypt correctly
- SQL injection eliminated

Token Architecture (v3.1.3):
- Session tokens: secrets.token_urlsafe(32) — high-entropy opaque tokens stored
  in auth_sessions table (DB-backed).
- JWT layer: python-jose JWT utilities in auth_middleware.py handle stateless
  token validation for API-to-API calls and the Chrome extension.
- Import jwt_utils from auth_middleware for JWT encode/decode operations.
"""

import os
import uuid
import secrets
import logging
import bcrypt
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel, EmailStr

from auth_config import (
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    SUPABASE_SERVICE_KEY,
    PASSWORD_POLICY,
    EMAIL_VERIFICATION_CONFIG,
    DISPLAY_NAME_CONFIG,
    PROFILE_VISIBILITY_CONFIG,
    ACCOUNT_DELETION_CONFIG,
    SESSION_CONFIG,
    ProfileVisibility,
    validate_display_name,
    requires_email_verification,
    requires_display_name,
    OAUTH_PROVIDERS,
    OAUTH_REDIRECT_BASE,
)

logger = logging.getLogger("quirrely.auth")

async def send_verification_email(user_id: str, email: str):
    """Create verification token and send email via Resend."""
    import hashlib
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    try:
        db_execute(
            """INSERT INTO email_verification_requests (user_id, email, token_hash, expires_at)
               VALUES (%s, %s, %s, %s)""",
            (user_id, email, token_hash, expires_at)
        )
        verify_url = f"https://quirrely.ca/auth/verify?token={token}"
        html = f"""<div style="font-family:system-ui;max-width:500px;margin:0 auto;padding:2rem;">
            <p>Click below to verify your email:</p>
            <a href="{verify_url}" style="display:inline-block;background:#FF6B6B;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;">Verify Email</a>
            <p style="color:#636E72;font-size:0.9rem;margin-top:1rem;">This link expires in 24 hours.</p>
        </div>"""
        from email_service import send_email_via_resend
        result = await send_email_via_resend(to=email, subject="Verify your Quirrely account", html=html)
        logger.info(f"Verification email sent to {email}: {result}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════════════════════════════════════

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://quirrely:password@localhost:5432/quirrely_prod")

from psycopg2.pool import ThreadedConnectionPool
try:
    _auth_pool = ThreadedConnectionPool(2, 10, DATABASE_URL)
except Exception:
    _auth_pool = None


def get_db():
    """Get a database connection from pool. Caller must return via put_db."""
    if _auth_pool:
        conn = _auth_pool.getconn()
        conn.autocommit = False
        return conn
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


def put_db(conn):
    """Return connection to pool."""
    if _auth_pool:
        _auth_pool.putconn(conn)
    else:
        conn.close()


def db_query_one(sql: str, params: tuple = ()) -> Optional[Dict]:
    """Execute query and return one row as dict, or None."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        put_db(conn)


def db_query_all(sql: str, params: tuple = ()) -> list:
    """Execute query and return all rows as list of dicts."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        put_db(conn)


def db_execute(sql: str, params: tuple = ()) -> None:
    """Execute a write query (INSERT/UPDATE/DELETE)."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        put_db(conn)


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/auth", tags=["auth"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class SignUpRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class SignUpResponse(BaseModel):
    user_id: str
    email: str
    requires_verification: bool
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MagicLinkRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: str
    email: str
    email_verified: bool
    display_name: Optional[str]
    profile_visibility: str
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    profile_visibility: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class DeleteAccountRequest(BaseModel):
    confirmation: Optional[str] = None
    hard_delete: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# PASSWORD HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# SESSION HELPERS (DB-backed)
# ═══════════════════════════════════════════════════════════════════════════

def create_session(user_id: str, ip_address: str = None, user_agent: str = None) -> Dict[str, str]:
    """Create a new session in the database. Returns access_token and refresh_token."""
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_CONFIG["session_lifetime_hours"])

    db_execute(
        """INSERT INTO auth_sessions (access_token, refresh_token, user_id, expires_at, ip_address, user_agent)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (access_token, refresh_token, user_id, expires_at, ip_address, user_agent)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    }


def get_session(access_token: str) -> Optional[Dict]:
    """Look up a session by access token. Returns None if expired or missing."""
    row = db_query_one(
        """SELECT access_token, refresh_token, user_id, expires_at
           FROM auth_sessions WHERE access_token = %s""",
        (access_token,)
    )
    if not row:
        return None
    if datetime.utcnow() > row["expires_at"].replace(tzinfo=None):
        # Expired — clean it up
        db_execute("DELETE FROM auth_sessions WHERE access_token = %s", (access_token,))
        return None
    return row


def delete_session(access_token: str) -> None:
    """Delete a single session."""
    db_execute("DELETE FROM auth_sessions WHERE access_token = %s", (access_token,))


def delete_user_sessions(user_id: str) -> int:
    """Delete all sessions for a user. Returns count deleted."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM auth_sessions WHERE user_id = %s", (user_id,))
            count = cur.rowcount
        conn.commit()
        return count
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def cleanup_expired_sessions() -> int:
    """Remove expired sessions. Call periodically."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM auth_sessions WHERE expires_at < now()")
            count = cur.rowcount
        conn.commit()
        return count
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# USER HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Fetch user from DB by ID."""
    return db_query_one(
        """SELECT id, email, email_verified, display_name, password_hash,
                  subscription_tier, public_profile, created_at, updated_at
           FROM users WHERE id = %s""",
        (user_id,)
    )


def get_user_by_email(email: str) -> Optional[Dict]:
    """Fetch user from DB by email."""
    return db_query_one(
        """SELECT id, email, email_verified, display_name, password_hash,
                  subscription_tier, public_profile, created_at, updated_at
           FROM users WHERE email = %s""",
        (email,)
    )


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[Dict]:
    """Extract user from auth header via DB session lookup."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]
    session = get_session(token)
    if not session:
        return None

    user = get_user_by_id(str(session["user_id"]))
    return user


def require_auth(authorization: Optional[str] = Header(None)) -> Dict:
    """Require authenticated user."""
    user = get_current_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_verified(authorization: Optional[str] = Header(None)) -> Dict:
    """Require verified email."""
    user = require_auth(authorization)
    if not user.get("email_verified"):
        raise HTTPException(status_code=403, detail="Email verification required")
    return user


# ═══════════════════════════════════════════════════════════════════════════
# SIGN UP
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/signup", response_model=SignUpResponse)
async def sign_up(request: SignUpRequest):
    email = request.email.lower().strip()

    if not request.password:
        raise HTTPException(status_code=400, detail="Password is required")

    # Validate password policy
    v = PASSWORD_POLICY.validate(request.password)
    if not v["valid"]:
        raise HTTPException(status_code=400, detail=v["error"])

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    pw_hash = hash_password(request.password)

    # Generate user ID
    user_id = str(uuid.uuid4())

    # Derive display name from email
    display_name = email.split("@")[0]

    # Insert user with parameterized query
    db_execute(
        """INSERT INTO users (id, email, display_name, subscription_tier, password_hash)
           VALUES (%s, %s, %s, 'free', %s)""",
        (user_id, email, display_name, pw_hash)
    )

    logger.info(f"New signup: {email} (user_id={user_id})")
    # Send verification email
    await send_verification_email(user_id, email)

    return SignUpResponse(
        user_id=user_id,
        email=email,
        requires_verification=True,
        message="Account created"
    )


# ═══════════════════════════════════════════════════════════════════════════
# SOCIAL / OAUTH LOGIN
# ═══════════════════════════════════════════════════════════════════════════

import httpx
from urllib.parse import urlencode, quote

# In-memory OAuth state store (short-lived, <10 min)
_oauth_states: Dict[str, Dict] = {}

def _cleanup_oauth_states():
    """Remove expired OAuth states (older than 10 minutes)."""
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    expired = [k for k, v in _oauth_states.items() if v.get("created_at", cutoff) < cutoff]
    for k in expired:
        del _oauth_states[k]


@router.get("/login/{provider}")
async def oauth_login(provider: str):
    """
    Initiate OAuth login. Returns redirect_url to provider's consent screen.
    Supported: google, facebook, linkedin
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    cfg = OAUTH_PROVIDERS[provider]
    if not cfg["client_id"]:
        raise HTTPException(status_code=503, detail=f"{provider} login not configured")

    _cleanup_oauth_states()

    # Generate CSRF state
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {"provider": provider, "created_at": datetime.utcnow()}

    redirect_uri = f"{OAUTH_REDIRECT_BASE}/api/v2/auth/callback/{provider}"

    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code",
    }

    # Provider-specific scope param
    if provider == "facebook":
        params["scope"] = cfg["scopes"]
    else:
        params["scope"] = cfg["scopes"]

    authorize_url = f"{cfg['authorize_url']}?{urlencode(params)}"
    return {"redirect_url": authorize_url}


@router.get("/callback/{provider}")
async def oauth_callback(provider: str, code: str = None, state: str = None, error: str = None):
    """
    OAuth callback. Exchanges code for token, fetches user info,
    creates/links account, creates session, redirects to frontend.
    """
    from fastapi.responses import HTMLResponse

    if error:
        return HTMLResponse(_oauth_error_page(f"OAuth error: {error}"))

    if not code or not state:
        return HTMLResponse(_oauth_error_page("Missing code or state"))

    # Validate CSRF state
    if state not in _oauth_states:
        return HTMLResponse(_oauth_error_page("Invalid or expired state"))

    state_data = _oauth_states.pop(state)
    if state_data["provider"] != provider:
        return HTMLResponse(_oauth_error_page("State mismatch"))

    if provider not in OAUTH_PROVIDERS:
        return HTMLResponse(_oauth_error_page(f"Unknown provider: {provider}"))

    cfg = OAUTH_PROVIDERS[provider]
    redirect_uri = f"{OAUTH_REDIRECT_BASE}/api/v2/auth/callback/{provider}"

    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(cfg["token_url"], data={
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }, headers={"Accept": "application/json"})

            if token_resp.status_code != 200:
                logger.error(f"OAuth token exchange failed: {token_resp.text}")
                return HTMLResponse(_oauth_error_page("Failed to authenticate"))

            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return HTMLResponse(_oauth_error_page("No access token received"))

            # Fetch user info
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_resp = await client.get(cfg["userinfo_url"], headers=headers)
            if userinfo_resp.status_code != 200:
                return HTMLResponse(_oauth_error_page("Failed to get user info"))

            userinfo = userinfo_resp.json()

        # Extract user details (provider-specific)
        oauth_user = _extract_oauth_user(provider, userinfo)
        if not oauth_user.get("email"):
            return HTMLResponse(_oauth_error_page("Email not provided by provider"))

        # Resolve user: find or create
        user, is_new = _resolve_oauth_user(provider, oauth_user)
        user_id = str(user["id"])

        # Create session
        session = create_session(user_id)

        # Log the login
        db_execute(
            """INSERT INTO login_history (user_id, method, success, country_code)
               VALUES (%s, %s, true, %s)""",
            (user_id, provider, None)
        )

        logger.info(f"OAuth login ({provider}): {oauth_user['email']} (user_id={user_id}, new={is_new})")

        # Return HTML page that stores session in localStorage and redirects
        return HTMLResponse(_oauth_success_page(session, user))

    except Exception as e:
        logger.error(f"OAuth callback error ({provider}): {e}")
        return HTMLResponse(_oauth_error_page("Authentication failed"))


def _extract_oauth_user(provider: str, userinfo: Dict) -> Dict[str, str]:
    """Extract normalized user data from provider-specific userinfo."""
    if provider == "google":
        return {
            "provider_id": userinfo.get("sub", ""),
            "email": userinfo.get("email", ""),
            "name": userinfo.get("name", ""),
            "picture": userinfo.get("picture", ""),
        }
    elif provider == "facebook":
        return {
            "provider_id": userinfo.get("id", ""),
            "email": userinfo.get("email", ""),
            "name": userinfo.get("name", ""),
            "picture": (userinfo.get("picture", {}).get("data", {}).get("url", "")),
        }
    elif provider == "linkedin":
        return {
            "provider_id": userinfo.get("sub", ""),
            "email": userinfo.get("email", ""),
            "name": userinfo.get("name", ""),
            "picture": userinfo.get("picture", ""),
        }
    return {"provider_id": "", "email": "", "name": "", "picture": ""}


def _resolve_oauth_user(provider: str, oauth_user: Dict) -> tuple:
    """
    Find or create user for OAuth login.
    Returns (user_dict, is_new).

    Resolution order:
    1. Existing link in user_auth_providers → login that user
    2. Existing user with same email → link provider + login
    3. No match → create new user + link provider
    """
    email = oauth_user["email"].lower().strip()

    # 1. Check for existing provider link
    linked = db_query_one(
        """SELECT user_id FROM user_auth_providers
           WHERE provider = %s AND provider_user_id = %s""",
        (provider, oauth_user["provider_id"])
    )
    if linked:
        user = get_user_by_id(str(linked["user_id"]))
        if user:
            # Update last_used_at
            db_execute(
                "UPDATE user_auth_providers SET last_used_at = now() WHERE provider = %s AND provider_user_id = %s",
                (provider, oauth_user["provider_id"])
            )
            return user, False

    # 2. Check for existing user by email
    user = get_user_by_email(email)
    if user:
        _link_provider(str(user["id"]), provider, oauth_user)
        return user, False

    # 3. Create new user
    user_id = str(uuid.uuid4())
    display_name = oauth_user.get("name", email.split("@")[0])

    db_execute(
        """INSERT INTO users (id, email, display_name, email_verified, subscription_tier)
           VALUES (%s, %s, %s, true, 'free')""",
        (user_id, email, display_name)
    )

    _link_provider(user_id, provider, oauth_user)

    user = get_user_by_id(user_id)
    return user, True


def _link_provider(user_id: str, provider: str, oauth_user: Dict):
    """Link an OAuth provider to a user account."""
    try:
        db_execute(
            """INSERT INTO user_auth_providers (user_id, provider, provider_user_id, provider_email, provider_name, provider_avatar_url)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id, provider) DO UPDATE SET
                 provider_user_id = EXCLUDED.provider_user_id,
                 provider_email = EXCLUDED.provider_email,
                 provider_name = EXCLUDED.provider_name,
                 provider_avatar_url = EXCLUDED.provider_avatar_url,
                 last_used_at = now()""",
            (user_id, provider, oauth_user["provider_id"], oauth_user["email"],
             oauth_user.get("name", ""), oauth_user.get("picture", ""))
        )
    except Exception as e:
        logger.error(f"Failed to link provider {provider} for user {user_id}: {e}")


def _oauth_success_page(session: Dict, user: Dict) -> str:
    """HTML page that stores session in localStorage and redirects to dashboard."""
    import json
    user_obj = {
        "id": str(user["id"]),
        "email": user["email"],
        "display_name": user.get("display_name", ""),
        "email_verified": user.get("email_verified", True),
        "subscription_tier": user.get("subscription_tier", "free"),
    }
    session_obj = {
        "token": session["access_token"],
        "refresh_token": session["refresh_token"],
    }

    return f"""<!DOCTYPE html>
<html><head><title>Signing in...</title></head>
<body>
<p style="font-family:system-ui;text-align:center;padding:3rem;">Signing you in...</p>
<script>
var sess = {json.dumps(session_obj)};
sess.createdAt = new Date().toISOString();
sess.expiresAt = new Date(Date.now() + 7*24*60*60*1000).toISOString();
localStorage.setItem('quirrely_session', JSON.stringify(sess));
localStorage.setItem('quirrely_user', {json.dumps(json.dumps(user_obj))});
window.location.href = '/frontend/dashboard.html';
</script>
</body></html>"""


def _oauth_error_page(message: str) -> str:
    """HTML error page for OAuth failures."""
    import html
    safe_msg = html.escape(message)
    return f"""<!DOCTYPE html>
<html><head><title>Login Error</title></head>
<body style="font-family:system-ui;text-align:center;padding:3rem;">
<h2 style="color:#E74C3C;">Login Failed</h2>
<p>{safe_msg}</p>
<a href="/auth/login.html" style="color:#FF6B6B;">Try again</a>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
# LOGIN (email/password)
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request = None):
    email = request.email.lower().strip()

    # Look up user by email
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password against stored hash
    if not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["id"])

    # Create DB-backed session
    ip_address = req.client.host if req and req.client else None
    user_agent = req.headers.get("user-agent") if req else None
    session = create_session(user_id, ip_address=ip_address, user_agent=user_agent)

    # Update last login
    db_execute("UPDATE users SET last_login_at = now() WHERE id = %s", (user_id,))

    logger.info(f"Login: {email} (user_id={user_id})")

    return TokenResponse(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        token_type="bearer",
        expires_in=SESSION_CONFIG["session_lifetime_hours"] * 3600,
        user={
            "id": user_id,
            "email": user["email"],
            "display_name": user.get("display_name", ""),
            "email_verified": user.get("email_verified", False),
            "subscription_tier": user.get("subscription_tier", "free"),
        }
    )


@router.post("/login/magic-link")
async def request_magic_link(request: MagicLinkRequest):
    """Request magic link login."""
    email = request.email.lower().strip()
    # In production: Send magic link via Supabase/Resend
    return {"message": "Check your email for the login link", "email": email}


# Note: Social login is handled by GET /login/{provider} above


# ═══════════════════════════════════════════════════════════════════════════
# TOKEN MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/refresh")
async def refresh_token_endpoint(refresh_token: str):
    """Refresh access token using refresh token."""
    # Find session by refresh token
    session = db_query_one(
        "SELECT access_token, user_id FROM auth_sessions WHERE refresh_token = %s",
        (refresh_token,)
    )

    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = str(session["user_id"])
    old_access_token = session["access_token"]

    # Delete old session
    delete_session(old_access_token)

    # Create new session
    new_session = create_session(user_id)

    user = get_user_by_id(user_id)

    return TokenResponse(
        access_token=new_session["access_token"],
        refresh_token=new_session["refresh_token"],
        expires_in=SESSION_CONFIG["session_lifetime_hours"] * 3600,
        user={
            "id": user_id,
            "email": user["email"] if user else "",
            "email_verified": user.get("email_verified", False) if user else False,
            "display_name": user.get("display_name", "") if user else "",
        }
    )


@router.post("/logout")
async def logout(user: Dict = Depends(require_auth), authorization: str = Header(None)):
    """Logout current session."""
    token = authorization[7:] if authorization else None
    if token:
        delete_session(token)
    return {"message": "Logged out successfully"}


@router.post("/logout/all")
async def logout_all_sessions(user: Dict = Depends(require_auth)):
    """Logout all sessions for user."""
    user_id = str(user["id"])
    count = delete_user_sessions(user_id)
    return {"message": f"Logged out of {count} sessions"}


# ═══════════════════════════════════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/verify/resend")
async def resend_verification(user: Dict = Depends(require_auth)):
    """Resend verification email."""
    if user.get("email_verified"):
        return {"message": "Email already verified"}
    await send_verification_email(user["id"], user["email"])
    return {"message": "Verification email sent"}


@router.post("/verify/confirm")
async def confirm_verification(token: str):
    """Confirm email verification."""
    import hashlib
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    row = db_query_one(
        """SELECT id, user_id, email FROM email_verification_requests
           WHERE token_hash = %s AND verified = false AND expires_at > NOW()""",
        (token_hash,)
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    db_execute("UPDATE users SET email_verified = true WHERE id = %s", (row["user_id"],))
    db_execute("UPDATE email_verification_requests SET verified = true, verified_at = NOW() WHERE id = %s", (row["id"],))
    logger.info(f"Email verified: {row["email"]}")
    return {"message": "Email verified successfully"}


@router.get("/verify/required")
async def check_verification_required(
    action: str,
    user: Dict = Depends(require_auth),
):
    """Check if verification is required for an action."""
    required = requires_email_verification(action)
    verified = user.get("email_verified", False)
    return {
        "action": action,
        "verification_required": required,
        "email_verified": verified,
        "can_proceed": not required or verified,
    }


# ═══════════════════════════════════════════════════════════════════════════
# USER PROFILE
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: Dict = Depends(require_auth)):
    """Get current user's profile."""
    return UserResponse(
        id=str(user["id"]),
        email=user["email"],
        email_verified=user.get("email_verified", False),
        display_name=user.get("display_name"),
        profile_visibility="public" if user.get("public_profile") else "private",
        created_at=user.get("created_at", datetime.utcnow()),
        updated_at=user.get("updated_at", datetime.utcnow()),
    )


@router.patch("/me")
@router.post("/me/update")
async def update_profile(
    request: UpdateProfileRequest,
    user: Dict = Depends(require_auth),
):
    """Update user profile."""
    user_id = str(user["id"])
    updates = {}

    if request.display_name is not None:
        validation = validate_display_name(request.display_name)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        db_execute(
            "UPDATE users SET display_name = %s, updated_at = now() WHERE id = %s",
            (request.display_name.strip(), user_id)
        )
        updates["display_name"] = request.display_name.strip()

    if request.profile_visibility is not None:
        try:
            visibility = ProfileVisibility(request.profile_visibility)
            is_public = visibility == ProfileVisibility.PUBLIC
            db_execute(
                "UPDATE users SET public_profile = %s, updated_at = now() WHERE id = %s",
                (is_public, user_id)
            )
            updates["profile_visibility"] = visibility.value
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid profile visibility")

    if request.avatar_url is not None:
        import re as _re
        if not _re.match(r"^https://[a-zA-Z0-9]", request.avatar_url or ""):
            raise HTTPException(status_code=400, detail="Avatar must be a valid HTTPS URL")
        if len(request.avatar_url) > 500:
            raise HTTPException(status_code=400, detail="Avatar URL too long")
        db_execute("UPDATE users SET avatar_url = %s, updated_at = now() WHERE id = %s", (request.avatar_url, user_id))
        updates["avatar_url"] = request.avatar_url
    return {"message": "Profile updated", "updates": updates}


# ═══════════════════════════════════════════════════════════════════════════
# PASSWORD MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/password/change")
async def change_password(
    request: ChangePasswordRequest,
    user: Dict = Depends(require_auth),
):
    """Change password."""
    user_id = str(user["id"])

    # Verify current password against DB hash
    if not user.get("password_hash"):
        raise HTTPException(status_code=400, detail="No password set on this account")

    if not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    validation = PASSWORD_POLICY.validate(request.new_password)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    # Hash and store new password
    new_hash = hash_password(request.new_password)
    db_execute(
        "UPDATE users SET password_hash = %s, updated_at = now() WHERE id = %s",
        (new_hash, user_id)
    )

    # Invalidate all sessions if configured
    if SESSION_CONFIG.get("invalidate_on_password_change"):
        delete_user_sessions(user_id)

    return {"message": "Password changed successfully"}


@router.post("/password/reset")
async def request_password_reset(email: EmailStr):
    """Request password reset email."""
    # In production: Send reset email via Resend
    return {"message": "If this email exists, a reset link has been sent"}


@router.get("/password/strength")
async def check_password_strength(password: str):
    """Check password strength (for UI meter)."""
    return PASSWORD_POLICY.get_strength(password)


@router.post("/password/validate")
async def validate_password(password: str):
    """Validate password against policy."""
    return PASSWORD_POLICY.validate(password)


# ═══════════════════════════════════════════════════════════════════════════
# ACCOUNT DELETION
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/account/delete")
async def delete_account(
    request: DeleteAccountRequest,
    user: Dict = Depends(require_auth),
):
    """Delete account (soft or hard)."""
    user_id = str(user["id"])

    if request.hard_delete:
        if request.confirmation != ACCOUNT_DELETION_CONFIG["hard_delete"]["confirmation_phrase"]:
            raise HTTPException(
                status_code=400,
                detail=f"Type '{ACCOUNT_DELETION_CONFIG['hard_delete']['confirmation_phrase']}' to confirm"
            )

        # Remove all sessions
        delete_user_sessions(user_id)

        # Record deletion then remove user
        db_execute(
            """INSERT INTO account_deletion_requests (user_id, deletion_type, status)
               VALUES (%s, 'hard', 'completed')
               ON CONFLICT DO NOTHING""",
            (user_id,)
        )
        db_execute("DELETE FROM users WHERE id = %s", (user_id,))

        return {"message": "Account permanently deleted"}

    else:
        # Soft delete — deactivate
        db_execute(
            "UPDATE users SET subscription_status = 'deleted', updated_at = now() WHERE id = %s",
            (user_id,)
        )
        delete_user_sessions(user_id)

        recovery_until = datetime.utcnow() + timedelta(
            days=ACCOUNT_DELETION_CONFIG["soft_delete"]["recovery_days"]
        )

        return {"message": "Account deactivated", "recovery_until": recovery_until}


@router.post("/account/recover")
async def recover_account(email: EmailStr, password: str):
    """Recover soft-deleted account."""
    email = email.lower().strip()

    user = get_user_by_email(email)
    if not user or user.get("subscription_status") != "deleted":
        raise HTTPException(status_code=404, detail="Account not found")

    # Verify password
    if not user.get("password_hash") or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Reactivate
    db_execute(
        "UPDATE users SET subscription_status = 'active', updated_at = now() WHERE id = %s",
        (str(user["id"]),)
    )

    return {"message": "Account recovered successfully"}


# ═══════════════════════════════════════════════════════════════════════════
# SESSIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/sessions")
async def list_sessions(user: Dict = Depends(require_auth)):
    """List all active sessions for user."""
    user_id = str(user["id"])

    sessions = db_query_all(
        """SELECT access_token, expires_at, created_at, ip_address, user_agent
           FROM auth_sessions WHERE user_id = %s AND expires_at > now()
           ORDER BY created_at DESC""",
        (user_id,)
    )

    return {
        "sessions": [
            {
                "token_prefix": s["access_token"][:8] + "...",
                "expires_at": s["expires_at"],
                "created_at": s["created_at"],
                "ip_address": s.get("ip_address"),
            }
            for s in sessions
        ],
        "count": len(sessions),
    }
