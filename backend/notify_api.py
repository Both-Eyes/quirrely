from fastapi import APIRouter
from pydantic import BaseModel
import httpx, logging, os
from datetime import datetime
from auth_api import db_execute

logger = logging.getLogger(__name__)
router = APIRouter()
RESEND_API_KEY = os.getenv("RESEND_API_KEY","")
FROM_EMAIL = "Quirrely <hello@quirrely.com>"
NOTIFY_EMAIL = "hello@quirrely.com"

class NotifyRequest(BaseModel):
    email: str

async def send_email(to, subject, html):
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}
    payload = {"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html}
    async with httpx.AsyncClient() as client:
        r = await client.post("https://api.resend.com/emails", headers=headers, json=payload)
        return r.json()

@router.post("/notify")
async def notify(req: NotifyRequest):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        return {"success": False, "error": "Invalid email"}
    ts = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
    sub_html = "<p>You are on the Quirrely list.</p>"
    int_html = f"<p>New waitlist signup: <strong>{email}</strong><br>Time: {ts}</p>"
    try:
        await send_email(email, "You are on the Quirrely list.", sub_html)
        await send_email(NOTIFY_EMAIL, f"New waitlist signup: {email}", int_html)
        db_execute("INSERT INTO waitlist (email) VALUES (%s) ON CONFLICT (email) DO NOTHING", (email,))
        return {"success": True}
    except Exception as e:
        logger.error(f"Notify error: {e}")
        return {"success": False, "error": "Service temporarily unavailable"}
