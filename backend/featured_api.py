from fastapi import APIRouter, Request, HTTPException, Depends, Header
from pydantic import BaseModel
import logging, os, uuid
from typing import Optional

logger = logging.getLogger(__name__)
from auth_api import require_auth, db_query_one, db_query_all, db_execute
router = APIRouter()

class SubmitRequest(BaseModel):
    sample: str
    display_name: str
    bio: Optional[str] = ""
    link_linkedin: Optional[str] = ""
    link_newsletter: Optional[str] = ""
    link_facebook: Optional[str] = ""
    permission_feature: bool = True
    permission_profile: bool = True
    permission_country: bool = True

@router.post("/api/v2/featured/submit")
async def submit_featured(req: SubmitRequest, user: dict = Depends(require_auth)):
    user_id = str(user.get("id") or user.get("user_id"))
    tier = (user.get("subscription_tier") or "free").lower()
    if tier not in ("pro","featured","authority"):
        raise HTTPException(status_code=403, detail="Pro subscription required")
    words = req.sample.strip().split()
    if len(words) < 50 or len(words) > 150:
        raise HTTPException(status_code=400, detail="Sample must be 50-150 words")
    if len(req.display_name.strip()) < 1 or len(req.display_name) > 50:
        raise HTTPException(status_code=400, detail="Display name required (max 50 chars)")
    existing = db_query_one("SELECT id FROM featured_submissions WHERE user_id=%s AND status='pending'", (user_id,))
    if existing:
        raise HTTPException(status_code=409, detail="You already have a pending submission")
    prof = db_query_one("SELECT profile, stance FROM writing_profiles WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user_id,))
    profile = prof["profile"] if prof else "unknown"
    stance = prof["stance"] if prof else "unknown"
    crow = db_query_one("SELECT country FROM users WHERE id=%s::uuid", (user_id,))
    country = (crow["country"] if crow and crow.get("country") else "CA")[:2].upper()
    sid = str(uuid.uuid4())
    db_execute(
        "INSERT INTO featured_submissions (id,user_id,sample,word_count,display_name,bio,"
        "link_linkedin,link_newsletter,link_facebook,profile,stance,country,status,"
        "permission_feature,permission_profile,permission_country) "
        "VALUES (%s,%s::uuid,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending',%s,%s,%s)",
        (sid, user_id, req.sample.strip()[:1500], len(words),
         req.display_name.strip()[:50], (req.bio or "")[:150],
         (req.link_linkedin or "")[:255], (req.link_newsletter or "")[:255],
         (req.link_facebook or "")[:255], profile[:20], stance[:20], country[:2],
         req.permission_feature, req.permission_profile, req.permission_country))
    return {"success": True, "submission_id": sid, "status": "pending"}

@router.get("/api/v2/featured/approved")
async def get_approved():
    rows = db_query_all(
        "SELECT fs.display_name,fs.sample,fs.bio,fs.profile,fs.stance,fs.country,"
        "fs.link_linkedin,fs.link_newsletter,fs.link_facebook "
        "FROM featured_submissions fs INNER JOIN featured_writers fw ON fw.submission_id=fs.id "
        "WHERE fs.status='approved' ORDER BY fw.display_order,fw.featured_at DESC LIMIT 20")
    return {"writers": [dict(r) for r in rows]}

@router.get("/api/v2/featured/my-submission")
async def my_submission(user: dict = Depends(require_auth)):
    uid = str(user.get("id") or user.get("user_id"))
    row = db_query_one("SELECT id,status,created_at FROM featured_submissions WHERE user_id=%s::uuid ORDER BY created_at DESC LIMIT 1", (uid,))
    if not row:
        return {"has_submission": False}
    return {"has_submission": True, "status": row.get("status","unknown"), "submitted_at": str(row.get("created_at",""))}

# ===== ADMIN ENDPOINTS =====
def verify_admin_key(request: Request):
    key = os.getenv("ADMIN_API_KEY","")
    admin_key = request.headers.get("X-Admin-Key","")
    if not key or admin_key != key:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/api/v2/featured/admin/pending")
async def admin_pending(request: Request):
    verify_admin_key(request)
    rows = db_query_all(
        "SELECT id,user_id,display_name,sample,word_count,bio,"
        "profile,stance,country,created_at,"
        "link_linkedin,link_newsletter,link_facebook "
        "FROM featured_submissions WHERE status='pending' ORDER BY created_at ASC")
    return {"submissions": [dict(r) for r in rows]}

class ReviewRequest(BaseModel):
    reason: Optional[str] = ""

@router.post("/api/v2/featured/admin/approve/{submission_id}")
async def admin_approve(submission_id: str, request: Request):
    verify_admin_key(request)
    sub = db_query_one(
        "SELECT user_id,display_name,profile,stance,sample,word_count "
        "FROM featured_submissions WHERE id=%s AND status='pending'", (submission_id,))
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or not pending")
    db_execute("UPDATE featured_submissions SET status='approved',reviewed_at=NOW() WHERE id=%s", (submission_id,))
    fw_id = str(uuid.uuid4())
    db_execute(
        "INSERT INTO featured_writers (id,user_id,submission_id,display_name,profile_type,profile_stance,"
        "piece_title,piece_excerpt,piece_url,lifetime_words_at_featuring) "
        "VALUES (%s,%s::uuid,%s,%s,%s,%s,'Featured Writing',%s,'/blog/featured',%s) "
        "ON CONFLICT (user_id) DO UPDATE SET submission_id=%s,display_name=%s,"
        "piece_excerpt=%s,featured_at=NOW()",
        (fw_id, str(sub["user_id"]), submission_id, str(sub["display_name"])[:50],
         str(sub["profile"])[:20], str(sub["stance"])[:20], str(sub.get("sample",""))[:200],
         sub.get("word_count") or 0,
         submission_id, str(sub["display_name"])[:50], str(sub.get("sample",""))[:200]))
    return {"success": True, "submission_id": submission_id, "featured_writer_id": fw_id}

@router.post("/api/v2/featured/admin/reject/{submission_id}")
async def admin_reject(submission_id: str, req: ReviewRequest, request: Request):
    verify_admin_key(request)
    sub = db_query_one("SELECT id FROM featured_submissions WHERE id=%s AND status='pending'", (submission_id,))
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or not pending")
    db_execute("UPDATE featured_submissions SET status='rejected',rejection_reason=%s,reviewed_at=NOW() WHERE id=%s",
               ((req.reason or "")[:500], submission_id))
    return {"success": True, "submission_id": submission_id, "status": "rejected"}
