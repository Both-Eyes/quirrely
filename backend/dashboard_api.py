from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from auth_api import require_auth, get_current_user, db_execute, db_query_all as db_query

logger = logging.getLogger("quirrely.dashboard")
router = APIRouter(prefix="/api/v2/me", tags=["Dashboard"])

class SaveAnalysisRequest(BaseModel):
    session_id: Optional[str] = None
    profile: str
    stance: str
    input_text: Optional[str] = None
    input_word_count: Optional[int] = None
    score_assertive: Optional[int] = None
    score_minimal: Optional[int] = None
    score_poetic: Optional[int] = None
    score_dense: Optional[int] = None
    score_conversational: Optional[int] = None
    score_formal: Optional[int] = None
    score_balanced: Optional[int] = None
    score_longform: Optional[int] = None
    score_interrogative: Optional[int] = None
    score_hedged: Optional[int] = None
    score_open: Optional[int] = None
    score_closed: Optional[int] = None
    score_stance_balanced: Optional[int] = None
    score_contradictory: Optional[int] = None

@router.post("/save-analysis")
async def save_analysis(req: SaveAnalysisRequest, user: Dict = Depends(require_auth)):
    user_id = str(user["id"])
    try:
        # Auto-compute scores if not provided
        sa = req.score_assertive
        sm = req.score_minimal
        sp = req.score_poetic
        sd = req.score_dense
        sc = req.score_conversational
        sf = req.score_formal
        sb = req.score_balanced
        sl = req.score_longform
        si = req.score_interrogative
        sh = req.score_hedged
        so = req.score_open
        scl = req.score_closed
        ssb = req.score_stance_balanced
        sco = req.score_contradictory
        if all(v is None for v in [sa, sm, sp, sd, sc, sf, sl, si, sh]):
            try:
                from api_v2 import get_classifier
                text = req.input_text or req.profile
                result = get_classifier().classify(text)
                ps = result.get("scores", {}).get("profiles", {})
                sts = result.get("scores", {}).get("stances", {})
                sa = round(ps.get("ASSERTIVE", 0) * 100)
                sm = round(ps.get("MINIMAL", 0) * 100)
                sp = round(ps.get("POETIC", 0) * 100)
                sd = round(ps.get("DENSE", 0) * 100)
                sc = round(ps.get("CONVERSATIONAL", 0) * 100)
                sf = round(ps.get("FORMAL", 0) * 100)
                sb = round(sts.get("BALANCED", 0) * 100)
                sl = round(ps.get("LONGFORM", 0) * 100)
                si = round(ps.get("INTERROGATIVE", 0) * 100)
                sh = round(ps.get("HEDGED", 0) * 100)
                so = round(sts.get("OPEN", 0) * 100)
                scl = round(sts.get("CLOSED", 0) * 100)
                ssb = round(sts.get("BALANCED", 0) * 100)
                sco = round(sts.get("CONTRADICTORY", 0) * 100)
                logger.info(f"Auto-computed scores for {user_id}")
            except Exception as ce:
                logger.warning(f"Auto-score failed: {ce}")
        db_execute(
            """INSERT INTO writing_profiles
               (user_id, session_id, profile, stance,
                score_assertive, score_minimal, score_poetic, score_dense,
                score_conversational, score_formal, score_balanced, score_longform,
                score_interrogative, score_hedged,
                score_open, score_closed, score_stance_balanced, score_contradictory,
                input_text, input_word_count)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, req.session_id, req.profile, req.stance,
             sa, sm, sp, sd, sc, sf, sb, sl, si, sh, so, scl, ssb, sco,
             req.input_text, req.input_word_count))
        return {"status": "saved", "profile": req.profile, "stance": req.stance}
    except Exception as e:
        logger.error(f"Failed to save analysis for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save analysis")

@router.delete("/history")
async def clear_history(user: Dict = Depends(require_auth)):
    user_id = str(user["id"])
    try:
        db_execute("DELETE FROM writing_profiles WHERE user_id = %s", (user_id,))
        logger.info(f"Cleared history for {user_id}")
        return {"status": "cleared"}
    except Exception as e:
        logger.error(f"Failed to clear history for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")

@router.get("/dashboard")
async def get_dashboard(user: Dict = Depends(require_auth)):
    user_id = str(user["id"])
    user_data = {
        "id": user_id,
        "email": user.get("email", ""),
        "display_name": user.get("display_name") or user.get("email", "").split("@")[0],
        "country": (user.get("country") or "").strip(),
        "city": user.get("city") or "",
        "subscription_tier": user.get("subscription_tier", "free"),
        "subscription_status": user.get("subscription_status", ""),
        "subscription_started_at": str(user.get("subscription_started_at") or ""),
        "created_at": str(user.get("created_at") or ""),
        "avatar_url": user.get("avatar_url") or "",
        "public_profile": user.get("public_profile", False),
    }
    profiles = db_query(
        """SELECT id, created_at, profile, stance,
                  score_assertive, score_minimal, score_poetic, score_dense,
                  score_conversational, score_formal, score_balanced, score_longform,
                  score_interrogative, score_hedged,
                  score_open, score_closed, score_stance_balanced, score_contradictory,
                  input_word_count
           FROM writing_profiles WHERE user_id = %s ORDER BY created_at DESC""",
        (user_id,)) or []
    test_count = len(profiles)
    total_words = sum((p.get("input_word_count") or 0) for p in profiles)
    latest = profiles[0] if profiles else None
    style_keys = ["score_assertive","score_minimal","score_poetic","score_dense",
                  "score_conversational","score_formal","score_balanced","score_longform",
                  "score_interrogative","score_hedged"]
    avg_scores = {}
    if profiles:
        for key in style_keys:
            vals = [p[key] for p in profiles if p.get(key) is not None]
            avg_scores[key] = round(sum(vals)/len(vals),1) if vals else 0
    else:
        avg_scores = {k: 0 for k in style_keys}
    if test_count >= 2:
        primary_profiles = [p["profile"] for p in profiles]
        most_common = max(set(primary_profiles), key=primary_profiles.count)
        consistency = round((primary_profiles.count(most_common)/len(primary_profiles))*100)
    else:
        consistency = 100 if test_count == 1 else 0
    response = {
        "user": user_data, "latest_profile": None,
        "stats": {"test_count": test_count, "total_words": total_words, "consistency": consistency},
        "avg_scores": avg_scores,
        "profiles": [{"id": str(p["id"]), "created_at": str(p["created_at"]),
                       "profile": p["profile"], "stance": p["stance"],
                       "word_count": p.get("input_word_count"),
                       "score_assertive": p.get("score_assertive"), "score_minimal": p.get("score_minimal"),
                       "score_poetic": p.get("score_poetic"), "score_dense": p.get("score_dense"),
                       "score_conversational": p.get("score_conversational"), "score_formal": p.get("score_formal"),
                       "score_longform": p.get("score_longform"), "score_interrogative": p.get("score_interrogative"),
                       "score_hedged": p.get("score_hedged"), "score_balanced": p.get("score_balanced")} for p in profiles[:20]],
    }
    if latest:
        response["latest_profile"] = {
            "profile": latest["profile"], "stance": latest["stance"],
            "created_at": str(latest["created_at"]),
            "scores": {k: latest.get(k, 0) for k in style_keys},
        }
    return response
