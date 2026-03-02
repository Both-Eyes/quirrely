from fastapi import APIRouter
from pydantic import BaseModel
import httpx, logging, os, re
from datetime import datetime
from auth_api import db_query_one, db_execute

logger = logging.getLogger(__name__)
router = APIRouter()

RESEND_API_KEY = os.getenv("RESEND_API_KEY","")
FROM_EMAIL = "Quirrely <hello@quirrely.com>"
NOTIFY_EMAIL = "hello@quirrely.com"

class SubscribeRequest(BaseModel):
    email: str
    source: str = "blog_sidebar"

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

async def send_email(to, subject, html):
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}
    payload = {"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html}
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.resend.com/emails", headers=headers, json=payload)
        return r.json()

@router.post("/api/v2/newsletter/subscribe")
async def subscribe(req: SubscribeRequest):
    email = req.email.strip().lower()
    source = req.source.strip()[:50]
    if not EMAIL_RE.match(email):
        return {"success": False, "error": "Invalid email address"}
    existing = db_query_one("SELECT id FROM newsletter_subscribers WHERE email=%s", (email,))
    is_new = not bool(existing)
    if is_new:
        db_execute("INSERT INTO newsletter_subscribers (email,source) VALUES (%s,%s) ON CONFLICT (email) DO NOTHING", (email, source))
    confirm_html = '<div style="font-family:system-ui,sans-serif;max-width:500px;margin:0 auto;padding:2rem;"><h2 style="color:#2D3436;">Welcome to Quirrely Insights!</h2><p>You are now signed up for writing tips and voice insights from Quirrely.</p><p style="color:#636E72;font-size:0.9rem;">You can unsubscribe anytime by replying to any email.</p><a href="https://quirrely.ca" style="display:inline-block;background:#FF6B6B;color:white;padding:0.5rem 1.5rem;border-radius:20px;text-decoration:none;font-weight:600;margin-top:1rem;">Visit Quirrely</a></div>'
    try:
        if is_new:
            await send_email(email, "Welcome to Quirrely Insights!", confirm_html)
            ts = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
            await send_email(NOTIFY_EMAIL, f"New newsletter subscriber: {email}",
                f"<p>New newsletter sub: <strong>{email}</strong><br>Source: {source}<br>Time: {ts}</p>")
    except Exception as e:
        logger.warning(f"Email send error (sub saved): {e}")
    return {"success": True, "new": is_new}

@router.get("/api/v2/newsletter/count")
async def newsletter_count():
    row = db_query_one("SELECT COUNT(*) as cnt FROM newsletter_subscribers")
    return {"count": row["cnt"] if row else 0}
