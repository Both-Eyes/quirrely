"""
STRETCH Exercise API - v2 (DB-wired, author-aware)
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json, os, random, psycopg2, psycopg2.extras

router = APIRouter(prefix="/stretch", tags=["stretch"])

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://quirrely:Quirr2026db@127.0.0.1:5432/quirrely_prod"
)

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def db_query_one(sql, params=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def db_query_all(sql, params=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def db_execute(sql, params=None):
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params)
        try:
            result = cur.fetchone()
        except psycopg2.ProgrammingError:
            result = None
        conn.commit()
        return dict(result) if result else None
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

from auth_api import require_auth

# ═══════════════════════════════════════════════════════════════
# KEYSTROKE VALIDATOR - zero tolerance paste detection
# ═══════════════════════════════════════════════════════════════
class KeystrokeValidator:
    MAX_CHARS_PER_SECOND = 15
    MIN_KEYSTROKE_RATIO = 0.3
    MAX_BURST_CHARS = 10

    def validate(self, content, keystrokes, clipboard_events,
                 duration_ms, word_count):
        wc = len(content.split()) if content.strip() else 0
        if clipboard_events:
            return {"valid": False, "reason": "PASTE_DETECTED",
                    "word_count": wc, "paste_detected": True,
                    "message": "Pasted content is not accepted."}
        clen = len(content)
        if clen > 0 and len(keystrokes) / clen < self.MIN_KEYSTROKE_RATIO:
            return {"valid": False, "reason": "INSUFFICIENT_KEYSTROKES",
                    "word_count": wc, "paste_detected": True,
                    "message": "Input pattern suggests pasted content."}
        if duration_ms > 0 and (clen / duration_ms) * 1000 > self.MAX_CHARS_PER_SECOND:
            return {"valid": False, "reason": "IMPOSSIBLE_SPEED",
                    "word_count": wc, "paste_detected": True,
                    "message": "Typing speed exceeds human limits."}
        if self._detect_burst(keystrokes):
            return {"valid": False, "reason": "BURST_DETECTED",
                    "word_count": wc, "paste_detected": True,
                    "message": "Unusual input pattern detected."}
        if wc < 50:
            return {"valid": False, "reason": "MINIMUM_NOT_MET",
                    "word_count": wc, "paste_detected": False,
                    "message": f"Minimum 50 words required. Current: {wc}"}
        return {"valid": True, "reason": "VALID",
                "word_count": wc, "paste_detected": False,
                "message": "Input validated."}

    def _detect_burst(self, keystrokes):
        if len(keystrokes) < 10:
            return False
        for i in range(len(keystrokes) - self.MAX_BURST_CHARS):
            t0 = keystrokes[i].get('time', 0)
            cnt = 0
            for j in range(i, len(keystrokes)):
                if keystrokes[j].get('time', 0) - t0 <= 100:
                    cnt += 1
                else:
                    break
            if cnt > self.MAX_BURST_CHARS:
                return True
        return False

validator = KeystrokeValidator()

# ═══════════════════════════════════════════════════════════════
# HELPERS: authors cache, user voice, eligibility
# ═══════════════════════════════════════════════════════════════
_authors_cache = None

def get_authors_by_voice():
    global _authors_cache
    if _authors_cache is None:
        rows = db_query_all("""
            SELECT id, voice_type, name, note, wikipedia_url,
                   book1_title, book1_isbn, book2_title, book2_isbn
            FROM stretch_authors WHERE active = TRUE
            ORDER BY display_order
        """)
        _authors_cache = {}
        for r in rows:
            vt = r['voice_type']
            if vt not in _authors_cache:
                _authors_cache[vt] = []
            _authors_cache[vt].append(r)
    return _authors_cache

def get_user_voice(user_id):
    return db_query_one("""
        SELECT profile, stance,
               score_assertive, score_minimal, score_poetic,
               score_dense, score_conversational, score_formal,
               score_balanced, score_longform, score_interrogative,
               score_hedged
        FROM writing_profiles
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (str(user_id),))

COUNTRY_MAP = {'CA':'commonwealth','UK':'commonwealth',
               'AU':'commonwealth','NZ':'commonwealth',
               'IE':'commonwealth','US':'us'}

@router.get("/eligibility/{user_id}")
async def check_eligibility(user_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    tier = user.get('subscription_tier', 'free')
    row = db_query_one(
        "SELECT COUNT(*) as cnt FROM writing_profiles WHERE user_id=%s",
        (uid,))
    rounds = row['cnt'] if row else 0
    tc = db_query_one(
        "SELECT * FROM tier_stretch_config WHERE tier=%s", (tier,))
    enabled = False
    if tc:
        feat = tc.get('features') or {}
        if isinstance(feat, str):
            import json as j; feat = j.loads(feat)
        enabled = feat.get('enabled', False)
    eligible = rounds >= 1 and enabled
    db_execute("""
        INSERT INTO stretch_eligibility (user_id, is_eligible, rounds_completed)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET is_eligible=EXCLUDED.is_eligible,
            rounds_completed=EXCLUDED.rounds_completed,
            updated_at=NOW()
    """, (uid, eligible, rounds))
    return {
        "eligible": eligible,
        "is_eligible": eligible,
        "rounds_completed": rounds,
        "rounds_required": 1,
        "tier": tier,
        "tier_allows_stretch": enabled
    }

@router.get("/recommend/{user_id}")
async def get_recommendations(user_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    tier = user.get('subscription_tier', 'free')
    voice = get_user_voice(uid)
    if not voice:
        return {"exercises": []}
    user_profile = voice['profile'].upper()
    tc = db_query_one("SELECT * FROM tier_stretch_config WHERE tier=%s", (tier,))
    if not tc:
        return {"exercises": []}
    max_types = tc['max_stretch_types']
    allow_opp = tc['allow_opposite']
    allow_adj = tc['allow_adjacent']
    done = db_query_all("""
        SELECT DISTINCT profile_to FROM stretch_exercises
        WHERE user_id=%s AND status='completed'
    """, (uid,))
    done_profiles = {r['profile_to'] for r in done}
    mappings = db_query_all("""
        SELECT id, profile_from, profile_to, growth_type,
               difficulty_rating, description
        FROM stretch_mappings
        WHERE profile_from=%s AND active=TRUE
        ORDER BY
            CASE growth_type WHEN 'opposite' THEN 0 ELSE 1 END,
            difficulty_rating DESC
    """, (user_profile,))
    authors_by_voice = get_authors_by_voice()
    exercises = []
    for m in mappings:
        gt = m['growth_type']
        if gt == 'opposite' and not allow_opp:
            continue
        if gt == 'adjacent' and not allow_adj:
            continue
        target = m['profile_to'].lower()
        authors = authors_by_voice.get(target, [])
        featured = authors[0] if authors else None
        title = f"Write like {featured['name']}" if featured else f"Stretch to {m['profile_to']}"
        desc = featured['note'] if featured else (m['description'] or f"Explore the {m['profile_to']} voice")
        exercises.append({
            "id": str(m['id']),
            "mapping_id": m['id'],
            "title": title,
            "name": title,
            "description": desc,
            "profile_from": m['profile_from'],
            "profile_to": m['profile_to'],
            "growth_type": gt,
            "difficulty": m['difficulty_rating'] or 3,
            "authors": [{
                "id": a['id'], "name": a['name'], "note": a['note'],
                "wikipedia": a['wikipedia_url'],
                "books": [
                    {"title": a['book1_title'], "isbn": a['book1_isbn']},
                    {"title": a['book2_title'], "isbn": a['book2_isbn']}
                ]
            } for a in authors],
            "completed": m['profile_to'] in done_profiles
        })
        if len(exercises) >= max_types:
            break
    return {"exercises": exercises}

@router.post("/start")
async def start_stretch(
    body: dict = Body(...),
    user: dict = Depends(require_auth)
):
    uid = str(user['id'])
    tier = user.get('subscription_tier', 'free')
    mapping_id = body.get('mapping_id') or body.get('exercise_id')
    author_id = body.get('author_id')
    if not mapping_id:
        raise HTTPException(400, "mapping_id required")
    m = db_query_one("SELECT * FROM stretch_mappings WHERE id=%s", (int(mapping_id),))
    if not m:
        raise HTTPException(404, "Mapping not found")
    active = db_query_one("""
        SELECT id FROM stretch_exercises
        WHERE user_id=%s AND status='active'
    """, (uid,))
    if active:
        raise HTTPException(409, "Already have an active exercise.")
    voice = get_user_voice(uid)
    stance = voice['stance'] if voice else 'BALANCED'
    country = 'CA'
    cgroup = COUNTRY_MAP.get(country, 'commonwealth')
    expires = datetime.utcnow() + timedelta(days=7)
    ex = db_execute("""
        INSERT INTO stretch_exercises
            (user_id, profile_from, profile_to, growth_type, mapping_id,
             user_country, user_country_group, user_stance, user_track,
             user_tier, status, expires_at, author_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'active',%s,%s)
        RETURNING id, profile_from, profile_to, growth_type, status,
                  cycles_completed, total_words, started_at, expires_at
    """, (uid, m['profile_from'], m['profile_to'], m['growth_type'],
          m['id'], country, cgroup, stance, m['growth_type'], tier,
          expires, author_id))
    db_execute("""
        INSERT INTO stretch_cycles (exercise_id, cycle_number)
        VALUES (%s, 1)
    """, (ex['id'],))
    db_execute("""
        INSERT INTO user_stretch_stats (user_id, exercises_started,
            current_exercise_id, first_stretch_at, last_activity_date)
        VALUES (%s, 1, %s, NOW(), CURRENT_DATE)
        ON CONFLICT (user_id) DO UPDATE SET
            exercises_started = user_stretch_stats.exercises_started + 1,
            current_exercise_id = EXCLUDED.current_exercise_id,
            last_activity_date = CURRENT_DATE,
            updated_at = NOW()
    """, (uid, ex['id']))
    return {
        "id": str(ex['id']),
        "profile_from": ex['profile_from'],
        "profile_to": ex['profile_to'],
        "growth_type": ex['growth_type'],
        "status": ex['status'],
        "cycles_completed": ex['cycles_completed'],
        "total_words": ex['total_words'],
        "started_at": ex['started_at'].isoformat() if ex.get('started_at') else None,
        "expires_at": ex['expires_at'].isoformat() if ex.get('expires_at') else None,
        "current_cycle": 1,
        "current_prompt": 1
    }

@router.get("/current/{user_id}")
async def get_current_exercise(user_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    ex = db_query_one("""
        SELECT e.*, a.name as author_name, a.note as author_note
        FROM stretch_exercises e
        LEFT JOIN stretch_authors a ON e.author_id = a.id
        WHERE e.user_id=%s AND e.status='active'
        ORDER BY e.started_at DESC LIMIT 1
    """, (uid,))
    return ex

@router.get("/prompt/{exercise_id}/{cycle_number}/{prompt_number}")
async def get_prompt(exercise_id: UUID, cycle_number: int,
                     prompt_number: int, user: dict = Depends(require_auth)):
    if not (1 <= cycle_number <= 5):
        raise HTTPException(400, "Cycle must be 1-5")
    if not (1 <= prompt_number <= 3):
        raise HTTPException(400, "Prompt must be 1-3")
    ex = db_query_one("SELECT * FROM stretch_exercises WHERE id=%s", (str(exercise_id),))
    if not ex:
        raise HTTPException(404, "Exercise not found")
    target = ex['profile_to']
    variant = random.randint(1, 3)
    prompt = db_query_one("""
        SELECT * FROM stretch_prompts_base
        WHERE target_profile=%s AND cycle_number=%s
              AND prompt_position=%s AND variant=%s AND active=TRUE
    """, (target, cycle_number, prompt_number, variant))
    if not prompt:
        prompt = db_query_one("""
            SELECT * FROM stretch_prompts_base
            WHERE target_profile=%s AND cycle_number=%s
                  AND prompt_position=%s AND active=TRUE LIMIT 1
        """, (target, cycle_number, prompt_number))
    if not prompt:
        raise HTTPException(404, "No prompt available")
    cgroup = ex.get('user_country_group', 'commonwealth')
    mod_c = db_query_one(
        "SELECT * FROM prompt_modifiers_country WHERE country_group=%s", (cgroup,))
    story = prompt['story_starter']
    if mod_c and mod_c.get('substitutions'):
        subs = mod_c['substitutions']
        if isinstance(subs, str):
            subs = json.loads(subs)
        for old, new in subs.items():
            story = story.replace(old, new)
    mod_s = db_query_one(
        "SELECT * FROM prompt_modifiers_stance WHERE stance=%s",
        (ex.get('user_stance', 'BALANCED'),))
    instruction = prompt['instruction']
    if mod_s and mod_s.get('instruction_suffix'):
        instruction = f"{instruction}\n\n{mod_s['instruction_suffix']}"
    # Style example and author info now displayed in frontend technique card
    # No longer appended to instruction text to avoid redundancy
    inp = db_query_one("""
        SELECT si.id FROM stretch_inputs si
        JOIN stretch_cycles c ON si.cycle_id=c.id
        WHERE c.exercise_id=%s AND c.cycle_number=%s AND si.prompt_number=%s
    """, (str(exercise_id), cycle_number, prompt_number))
    if not inp:
        inp = db_execute("""
            INSERT INTO stretch_inputs (cycle_id, prompt_number, base_prompt_id,
                rendered_prompt, story_starter)
            SELECT c.id, %s, %s, %s, %s
            FROM stretch_cycles c
            WHERE c.exercise_id=%s AND c.cycle_number=%s
            RETURNING id
        """, (prompt_number, prompt['id'], instruction, story,
              str(exercise_id), cycle_number))
    return {
        "id": str(inp['id']) if inp else str(uuid4()),
        "prompt_number": prompt_number,
        "story_starter": story,
        "instruction": instruction,
        "technique_name": prompt.get('technique_name') or '',
        "technique_tip": prompt.get('technique_tip') or '',
        "learning_goal": prompt.get('learning_goal') or '',
        "style_example": prompt.get('style_example') or '',
        "word_minimum": 50,
        "cycle_word_target": 150
    }

@router.post("/input/{exercise_id}/{cycle_number}/{prompt_number}")
async def submit_input(exercise_id: UUID, cycle_number: int,
                       prompt_number: int, body: dict = Body(...),
                       user: dict = Depends(require_auth)):
    if not (1 <= cycle_number <= 4 and 1 <= prompt_number <= 3):
        raise HTTPException(400, "Invalid cycle/prompt number")
    content = body.get('content', '')
    ks = body.get('keystroke_data', {})
    v = validator.validate(
        content,
        ks.get('keystrokes', []),
        ks.get('clipboard_events', []),
        ks.get('duration_ms', 0),
        ks.get('word_count', 0))
    if not v['valid']:
        return {"accepted": False, "validation": v,
                "next_action": "retry" if v['reason'] == 'MINIMUM_NOT_MET' else "blocked"}
    cycle = db_query_one("""
        SELECT id FROM stretch_cycles
        WHERE exercise_id=%s AND cycle_number=%s
    """, (str(exercise_id), cycle_number))
    if not cycle:
        raise HTTPException(404, "Cycle not found")
    db_execute("""
        UPDATE stretch_inputs SET
            user_input=%s, word_count=%s,
            keystroke_data=%s, keystroke_count=%s,
            typing_duration_ms=%s, chars_per_second=%s,
            validation_status='valid', validation_timestamp=NOW(),
            submitted_at=NOW()
        WHERE cycle_id=%s AND prompt_number=%s
    """, (content, v['word_count'],
          json.dumps(ks.get('keystrokes', [])[:50]),
          len(ks.get('keystrokes', [])),
          ks.get('duration_ms', 0),
          ks.get('chars_per_second', 0),
          str(cycle['id']), prompt_number))
    db_execute("""
        UPDATE stretch_cycles SET
            prompts_completed = GREATEST(prompts_completed, %s),
            total_words = total_words + %s
        WHERE id=%s
    """, (prompt_number, v['word_count'], str(cycle['id'])))
    is_cycle_done = prompt_number >= 3
    if is_cycle_done:
        db_execute("""
            UPDATE stretch_cycles SET status='completed', completed_at=NOW()
            WHERE id=%s
        """, (str(cycle['id']),))
        db_execute("""
            UPDATE stretch_exercises SET
                cycles_completed = cycles_completed + 1,
                total_words = total_words + (
                    SELECT total_words FROM stretch_cycles WHERE id=%s),
                last_activity_at = NOW()
            WHERE id=%s
        """, (str(cycle['id']), str(exercise_id)))
        ex = db_query_one("SELECT cycles_completed FROM stretch_exercises WHERE id=%s",
                          (str(exercise_id),))
        if ex and ex['cycles_completed'] >= 4:
            db_execute("""
                UPDATE stretch_exercises SET status='completed', completed_at=NOW()
                WHERE id=%s
            """, (str(exercise_id),))
        elif ex and ex['cycles_completed'] < 4:
            db_execute("""
                INSERT INTO stretch_cycles (exercise_id, cycle_number)
                VALUES (%s, %s)
            """, (str(exercise_id), ex['cycles_completed'] + 1))
    # Record STRETCH words against user's word limit
    uid = str(user['id'])
    from datetime import datetime as _dt
    _today = _dt.utcnow().strftime("%Y-%m-%d")
    db_execute("""
        INSERT INTO daily_keystroke_totals (user_id, date, keystroke_words)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, date) DO UPDATE SET
            keystroke_words = daily_keystroke_totals.keystroke_words + EXCLUDED.keystroke_words,
            updated_at = NOW()
    """, (uid, _today, v['word_count']))

    return {
        "accepted": True, "validation": v,
        "word_count": v['word_count'],
        "cycle_progress": {
            "prompts_completed": prompt_number,
            "prompts_remaining": 3 - prompt_number,
            "words_this_cycle": v['word_count'],
            "target_words": 500
        },
        "next_action": "cycle_complete" if is_cycle_done else "next_prompt"
    }

@router.get("/progress/{user_id}")
async def get_progress(user_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    stats = db_query_one("SELECT * FROM user_stretch_stats WHERE user_id=%s", (uid,))
    if not stats:
        return {"total_words_written": 0, "total_exercises_completed": 0,
                "total_cycles_completed": 0, "current_exercise": None,
                "streak_days": 0, "profiles_explored": []}
    return {
        "total_words_written": stats['total_words_written'],
        "total_exercises_completed": stats['total_exercises_completed'],
        "total_cycles_completed": stats['total_cycles_completed'],
        "current_exercise_id": str(stats['current_exercise_id']) if stats.get('current_exercise_id') else None,
        "streak_days": stats['current_streak_days'],
        "profiles_explored": stats.get('profiles_stretched_to', [])
    }

@router.post("/abandon/{exercise_id}")
async def abandon_exercise(exercise_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    ex = db_query_one("""
        SELECT * FROM stretch_exercises
        WHERE id=%s AND user_id=%s AND status='active'
    """, (str(exercise_id), uid))
    if not ex:
        raise HTTPException(404, "No active exercise found")
    db_execute("""
        UPDATE stretch_exercises SET status='abandoned', abandoned_at=NOW()
        WHERE id=%s
    """, (str(exercise_id),))
    db_execute("""
        UPDATE user_stretch_stats SET
            current_exercise_id=NULL,
            exercises_abandoned = exercises_abandoned + 1,
            updated_at=NOW()
        WHERE user_id=%s
    """, (uid,))
    return {"abandoned": True, "saved_at_cycle": ex['cycles_completed'],
            "words_counted": ex['total_words']}

@router.get("/history/{user_id}")
async def get_history(user_id: UUID, user: dict = Depends(require_auth)):
    uid = str(user['id'])
    rows = db_query_all("""
        SELECT e.*, a.name as author_name
        FROM stretch_exercises e
        LEFT JOIN stretch_authors a ON e.author_id = a.id
        WHERE e.user_id=%s ORDER BY e.started_at DESC LIMIT 20
    """, (uid,))
    return {"exercises": rows, "total": len(rows)}

@router.get("/cta/{user_id}")
async def get_stretch_cta(user_id: UUID, user: dict = Depends(require_auth)):
    return {"show_cta": True, "cta_type": "initial_offer",
            "headline": "Ready to Stretch?",
            "subhead": "Push your voice into new territory",
            "cta_text": "Start Your First Stretch"}
