from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import hashlib
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


VIDEO_DIR = "/home/quirrely/quirrely.ca/videos"
VIDEO_SCRIPT = "/opt/quirrely/quirrely_v313_integrated/backend/utils/voice-video.py"
AUDIO_SCRIPT = "/opt/quirrely/quirrely_v313_integrated/backend/utils/voice-audio.py"
PYTHON = "/usr/bin/python3.12"

PROFILE_META = {
    'assertive': 'The Direct Voice',
    'minimal': 'The Quiet Inviter',
    'poetic': 'The Lyric Wanderer',
    'dense': 'The Deep Diver',
    'conversational': 'The Natural Storyteller',
    'formal': 'The Measured Authority',
    'balanced': 'The Even Hand',
    'longform': 'The Long View',
    'interrogative': 'The Restless Questioner',
    'hedged': 'The Careful Navigator',
}

STANCE_LABELS = {
    'open': 'Open ears.',
    'closed': 'Closed form.',
    'balanced': 'Balanced stance.',
    'contradictory': 'Contradictions held.',
}


@router.get("/video")
async def get_voice_video(user: Dict = Depends(require_auth)):
    """
    Generate or return cached voice video for the authenticated user.
    Requires: Pro subscription, 5+ analyses, 1000+ words.
    """
    import subprocess, hashlib, json, os
    from fastapi.responses import FileResponse

    user_id = str(user["id"])
    tier = (user.get("subscription_tier") or "free").lower()

    # === TIER CHECK ===
    if tier != "pro":
        raise HTTPException(status_code=403, detail="Pro subscription required")

    # === THRESHOLD CHECK ===
    stats = db_query(
        """SELECT COUNT(*) as cnt, COALESCE(SUM(input_word_count), 0) as words
           FROM writing_profiles WHERE user_id = %s""",
        (user_id,)
    )
    row = stats[0] if stats else {"cnt": 0, "words": 0}
    test_count = row.get("cnt", 0)
    total_words = row.get("words", 0)

    if test_count < 5 or total_words < 1000:
        remaining = []
        if test_count < 5:
            remaining.append(f"{5 - test_count} more analyses")
        if total_words < 1000:
            remaining.append(f"{1000 - total_words} more words")
        raise HTTPException(
            status_code=403,
            detail=f"Not enough data. Need: {', '.join(remaining)}."
        )

    # === GET VOICE DATA ===
    profiles = db_query(
        """SELECT profile, stance,
                  AVG(score_assertive) as score_assertive,
                  AVG(score_minimal) as score_minimal,
                  AVG(score_poetic) as score_poetic,
                  AVG(score_dense) as score_dense,
                  AVG(score_conversational) as score_conversational,
                  AVG(score_formal) as score_formal,
                  AVG(score_balanced) as score_balanced,
                  AVG(score_longform) as score_longform,
                  AVG(score_interrogative) as score_interrogative,
                  AVG(score_hedged) as score_hedged,
                  COUNT(*) as cnt
           FROM writing_profiles WHERE user_id = %s
           GROUP BY profile, stance
           ORDER BY cnt DESC LIMIT 1""",
        (user_id,)
    )

    if not profiles:
        raise HTTPException(status_code=404, detail="No voice profile found")

    p = profiles[0]
    profile = (p.get("profile") or "conversational").lower()
    stance = (p.get("stance") or "balanced").lower()
    username = user.get("display_name") or user.get("email", "").split("@")[0]

    scores = {
        "score_assertive": float(p.get("score_assertive") or 0),
        "score_minimal": float(p.get("score_minimal") or 0),
        "score_poetic": float(p.get("score_poetic") or 0),
        "score_dense": float(p.get("score_dense") or 0),
        "score_conversational": float(p.get("score_conversational") or 0),
        "score_formal": float(p.get("score_formal") or 0),
        "score_balanced": float(p.get("score_balanced") or 0),
        "score_longform": float(p.get("score_longform") or 0),
        "score_interrogative": float(p.get("score_interrogative") or 0),
        "score_hedged": float(p.get("score_hedged") or 0),
    }

    # Build tagline
    meta_title = PROFILE_META.get(profile, profile.capitalize())
    stance_label = STANCE_LABELS.get(stance, '')
    tagline = f"{meta_title} \u2014 {stance_label}" if stance_label else meta_title

    # === CACHE CHECK ===
    # Hash scores to detect changes — regenerate if profile shifts
    score_hash = hashlib.md5(json.dumps(scores, sort_keys=True).encode()).hexdigest()[:8]
    os.makedirs(VIDEO_DIR, exist_ok=True)
    video_path = os.path.join(VIDEO_DIR, f"{user_id}_{score_hash}.mp4")

    if os.path.exists(video_path):
        logger.info(f"Video cache hit: {user_id}")
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{username}-voice.mp4",
            headers={"Cache-Control": "public, max-age=86400"}
        )

    # === GENERATE VIDEO ===
    logger.info(f"Generating video for {user_id} ({profile}/{stance})")

    tmp_video = f"/tmp/voice-video-{user_id}.mp4"
    tmp_audio = f"/tmp/voice-audio-{user_id}.wav"
    tmp_final = f"/tmp/voice-final-{user_id}.mp4"

    try:
        # Generate video frames
        cmd_video = [
            PYTHON, VIDEO_SCRIPT,
            "--username", username,
            "--profile", profile,
            "--stance", stance,
            "--tagline", tagline,
            "--scores", json.dumps(scores),
            "--output", tmp_video,
        ]
        result = subprocess.run(cmd_video, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            logger.error(f"Video gen failed: {result.stderr[-300:]}")
            raise HTTPException(status_code=500, detail="Video generation failed")

        # Generate audio
        cmd_audio = [
            PYTHON, AUDIO_SCRIPT,
            "--profile", profile,
            "--stance", stance,
            "--scores", json.dumps(scores),
            "--output", tmp_audio,
            "--mux", tmp_video,
            "--final", tmp_final,
        ]
        result = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"Audio gen failed: {result.stderr[-300:]}")
            raise HTTPException(status_code=500, detail="Audio generation failed")

        # Move to cache
        import shutil
        shutil.move(tmp_final, video_path)

        # Clean up old videos for this user (keep only current hash)
        for f in os.listdir(VIDEO_DIR):
            if f.startswith(f"{user_id}_") and f != os.path.basename(video_path):
                try:
                    os.remove(os.path.join(VIDEO_DIR, f))
                except:
                    pass

        logger.info(f"Video generated: {video_path} ({os.path.getsize(video_path)} bytes)")

        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{username}-voice.mp4",
            headers={"Cache-Control": "public, max-age=86400"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail="Video generation failed")
    finally:
        # Clean temp files
        for tmp in [tmp_video, tmp_audio]:
            try:
                os.remove(tmp)
            except:
                pass

