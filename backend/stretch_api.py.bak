"""
STRETCH Exercise API
Version: 1.0.0

Endpoints for the STRETCH writing exercise system.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import json

router = APIRouter(prefix="/stretch", tags=["stretch"])


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class KeystrokeData(BaseModel):
    """Keystroke tracking data for validation"""
    keystrokes: List[Dict[str, Any]]  # [{key, time, ctrl, meta}, ...]
    clipboard_events: List[Dict[str, Any]] = []
    content: str
    word_count: int
    duration_ms: int
    chars_per_second: float = 0


class StretchEligibility(BaseModel):
    """User's eligibility for STRETCH"""
    is_eligible: bool
    rounds_completed: int
    rounds_required: int = 5
    tier: str
    tier_allows_stretch: bool
    reason: Optional[str] = None


class StretchRecommendation(BaseModel):
    """Recommended stretch for user"""
    profile_from: str
    profile_to: str
    growth_type: str  # "opposite" or "adjacent"
    difficulty: int
    description: str
    why_recommended: str


class StretchExercise(BaseModel):
    """A stretch exercise"""
    id: UUID
    profile_from: str
    profile_to: str
    growth_type: str
    status: str
    cycles_completed: int
    total_words: int
    started_at: datetime
    expires_at: Optional[datetime]
    current_cycle: Optional[int]
    current_prompt: Optional[int]


class StretchCycle(BaseModel):
    """A single cycle within a stretch"""
    id: UUID
    cycle_number: int
    status: str
    prompts_completed: int
    total_words: int


class StretchPrompt(BaseModel):
    """A prompt within a cycle"""
    id: UUID
    prompt_number: int
    story_starter: str
    instruction: str
    word_minimum: int = 100
    cycle_word_target: int = 500


class StretchInput(BaseModel):
    """User's response to a prompt"""
    content: str
    keystroke_data: KeystrokeData


class StretchProgress(BaseModel):
    """User's overall stretch progress"""
    total_words_written: int
    total_exercises_completed: int
    total_cycles_completed: int
    current_exercise: Optional[StretchExercise]
    current_cycle: Optional[StretchCycle]
    current_prompt: Optional[StretchPrompt]
    streak_days: int
    profiles_explored: List[str]


class ValidationResult(BaseModel):
    """Result of keystroke validation"""
    valid: bool
    reason: str
    word_count: int
    paste_detected: bool
    message: str


# ═══════════════════════════════════════════════════════════════════════════════
# KEYSTROKE VALIDATOR
# 100% paste detection. Zero tolerance. No appeals.
# ═══════════════════════════════════════════════════════════════════════════════

class KeystrokeValidator:
    """
    Validates that user input was typed, not pasted.
    ZERO TOLERANCE policy - any paste detection = rejection.
    """
    
    # Maximum chars per second humanly possible (world record ~15)
    MAX_CHARS_PER_SECOND = 15
    
    # Minimum keystrokes required as % of content length
    MIN_KEYSTROKE_RATIO = 0.8
    
    # Burst detection: max chars in 100ms window
    MAX_BURST_CHARS = 10
    
    def validate(self, data: KeystrokeData) -> ValidationResult:
        """
        Validate input was typed, not pasted.
        Returns rejection if ANY paste indicator detected.
        """
        
        content = data.content.strip()
        word_count = len(content.split()) if content else 0
        
        # Check 1: Any clipboard events = immediate rejection
        if data.clipboard_events:
            return ValidationResult(
                valid=False,
                reason="PASTE_DETECTED",
                word_count=word_count,
                paste_detected=True,
                message="This exercise requires original typing. Pasted content is not accepted."
            )
        
        # Check 2: Not enough keystrokes for content length
        content_length = len(content)
        keystroke_count = len(data.keystrokes)
        
        if content_length > 0:
            keystroke_ratio = keystroke_count / content_length
            if keystroke_ratio < self.MIN_KEYSTROKE_RATIO:
                return ValidationResult(
                    valid=False,
                    reason="INSUFFICIENT_KEYSTROKES",
                    word_count=word_count,
                    paste_detected=True,
                    message="Input pattern suggests pasted content. Please type your response."
                )
        
        # Check 3: Impossible typing speed
        if data.duration_ms > 0:
            chars_per_second = (content_length / data.duration_ms) * 1000
            if chars_per_second > self.MAX_CHARS_PER_SECOND:
                return ValidationResult(
                    valid=False,
                    reason="IMPOSSIBLE_SPEED",
                    word_count=word_count,
                    paste_detected=True,
                    message="Typing speed exceeds human limits. Paste detected."
                )
        
        # Check 4: Burst detection (too many chars in short window)
        if self._detect_burst(data.keystrokes):
            return ValidationResult(
                valid=False,
                reason="BURST_DETECTED",
                word_count=word_count,
                paste_detected=True,
                message="Unusual input pattern detected. Please type your response."
            )
        
        # Check 5: Minimum word count
        if word_count < 100:
            return ValidationResult(
                valid=False,
                reason="MINIMUM_NOT_MET",
                word_count=word_count,
                paste_detected=False,
                message=f"Minimum 100 words required. Current: {word_count}"
            )
        
        # All checks passed
        return ValidationResult(
            valid=True,
            reason="VALID",
            word_count=word_count,
            paste_detected=False,
            message="Input validated successfully."
        )
    
    def _detect_burst(self, keystrokes: List[Dict]) -> bool:
        """Detect impossible bursts of characters"""
        if len(keystrokes) < 10:
            return False
        
        # Check for bursts in 100ms windows
        window_size_ms = 100
        for i in range(len(keystrokes) - self.MAX_BURST_CHARS):
            window_start = keystrokes[i].get('time', 0)
            chars_in_window = 0
            
            for j in range(i, len(keystrokes)):
                if keystrokes[j].get('time', 0) - window_start <= window_size_ms:
                    chars_in_window += 1
                else:
                    break
            
            if chars_in_window > self.MAX_BURST_CHARS:
                return True
        
        return False


validator = KeystrokeValidator()


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT RESOLVER
# Resolves base prompts with country/stance modifiers
# ═══════════════════════════════════════════════════════════════════════════════

class PromptResolver:
    """
    Resolves prompts from base + modifiers based on user context.
    """
    
    # Country to group mapping
    COUNTRY_GROUPS = {
        'CA': 'commonwealth',
        'UK': 'commonwealth', 
        'AU': 'commonwealth',
        'NZ': 'commonwealth',
        'IE': 'commonwealth',
        'US': 'us'
    }
    
    def resolve_prompt(
        self,
        base_prompt: Dict,
        user_country: str,
        user_stance: str
    ) -> Dict:
        """
        Apply country and stance modifiers to base prompt.
        """
        country_group = self.COUNTRY_GROUPS.get(user_country, 'commonwealth')
        
        # Get modifiers (would come from DB in production)
        country_mod = self._get_country_modifier(country_group)
        stance_mod = self._get_stance_modifier(user_stance)
        
        # Apply spelling substitutions
        story_starter = self._apply_substitutions(
            base_prompt['story_starter'],
            country_mod.get('substitutions', {})
        )
        
        # Combine instruction with stance guidance
        instruction = base_prompt['instruction']
        if stance_mod.get('instruction_suffix'):
            instruction = f"{instruction}\n\n{stance_mod['instruction_suffix']}"
        
        return {
            'story_starter': story_starter,
            'instruction': instruction,
            'voice_guidance': stance_mod.get('voice_guidance', ''),
            'word_minimum': 100,
            'cycle_word_target': 500
        }
    
    def _apply_substitutions(self, text: str, subs: Dict[str, str]) -> str:
        """Apply spelling/terminology substitutions"""
        for old, new in subs.items():
            text = text.replace(old, new)
        return text
    
    def _get_country_modifier(self, country_group: str) -> Dict:
        """Get country-specific modifiers"""
        # Would fetch from DB in production
        modifiers = {
            'commonwealth': {
                'substitutions': {
                    'harbor': 'harbour',
                    'color': 'colour',
                    'traveled': 'travelled'
                }
            },
            'us': {
                'substitutions': {
                    'harbour': 'harbor',
                    'colour': 'color',
                    'travelled': 'traveled'
                }
            }
        }
        return modifiers.get(country_group, {})
    
    def _get_stance_modifier(self, stance: str) -> Dict:
        """Get stance-specific modifiers"""
        # Would fetch from DB in production
        modifiers = {
            'OPEN': {
                'instruction_suffix': 'As you write, let questions emerge naturally. Leave room for uncertainty and exploration.',
                'voice_guidance': 'Your writing should invite dialogue. End with openings, not closures.'
            },
            'CLOSED': {
                'instruction_suffix': 'Write toward clarity and conclusion. Make definitive statements.',
                'voice_guidance': 'Your writing should resolve, not open. Certainty is your tool.'
            },
            'BALANCED': {
                'instruction_suffix': 'Weigh multiple perspectives as you write. Acknowledge complexity.',
                'voice_guidance': 'Your writing should be fair to all sides. Equilibrium is the goal.'
            },
            'CONTRADICTORY': {
                'instruction_suffix': 'Embrace tensions and paradoxes. Let opposing truths coexist.',
                'voice_guidance': 'Your writing should hold contradictions without resolving them.'
            }
        }
        return modifiers.get(stance, {})


prompt_resolver = PromptResolver()


# ═══════════════════════════════════════════════════════════════════════════════
# STRETCH RECOMMENDER
# Recommends next stretch based on user profile and history
# ═══════════════════════════════════════════════════════════════════════════════

class StretchRecommender:
    """
    Recommends stretches based on user profile, tier, and history.
    """
    
    # Tier-based access
    TIER_CONFIG = {
        'free': {'enabled': False, 'max_types': 0, 'allow_adjacent': False},
        'pro': {'enabled': True, 'max_types': 3, 'allow_adjacent': False},
        'authority': {'enabled': True, 'max_types': 6, 'allow_adjacent': True},
        'curator': {'enabled': True, 'max_types': 10, 'allow_adjacent': True}
    }
    
    # Opposite pairs (highest value stretches)
    OPPOSITES = {
        'ASSERTIVE': ['HEDGED', 'POETIC'],
        'HEDGED': ['ASSERTIVE'],
        'CONVERSATIONAL': ['FORMAL'],
        'FORMAL': ['CONVERSATIONAL', 'POETIC'],
        'DENSE': ['MINIMAL'],
        'MINIMAL': ['DENSE', 'INTERROGATIVE', 'LONGFORM'],
        'POETIC': ['ASSERTIVE', 'FORMAL'],
        'INTERROGATIVE': ['MINIMAL'],
        'LONGFORM': ['MINIMAL'],
        'BALANCED': []  # No strong opposites
    }
    
    def get_recommendations(
        self,
        user_profile: str,
        user_tier: str,
        completed_stretches: List[str],
        max_results: int = 3
    ) -> List[StretchRecommendation]:
        """
        Get personalized stretch recommendations.
        """
        tier_config = self.TIER_CONFIG.get(user_tier, self.TIER_CONFIG['free'])
        
        if not tier_config['enabled']:
            return []
        
        recommendations = []
        
        # Priority 1: Opposites (if not already done)
        opposites = self.OPPOSITES.get(user_profile, [])
        for target in opposites:
            stretch_key = f"{user_profile}_TO_{target}"
            if stretch_key not in completed_stretches:
                recommendations.append(StretchRecommendation(
                    profile_from=user_profile,
                    profile_to=target,
                    growth_type="opposite",
                    difficulty=5,
                    description=f"Stretch from {user_profile} to {target}",
                    why_recommended=f"Maximum growth: {user_profile} is opposite to {target}"
                ))
        
        # Priority 2: Adjacent (if tier allows and space remains)
        if tier_config['allow_adjacent'] and len(recommendations) < max_results:
            # Add adjacent stretches (all other profiles)
            all_profiles = ['ASSERTIVE', 'BALANCED', 'CONVERSATIONAL', 'DENSE', 
                          'FORMAL', 'HEDGED', 'INTERROGATIVE', 'LONGFORM', 
                          'MINIMAL', 'POETIC']
            
            for target in all_profiles:
                if target == user_profile:
                    continue
                if target in opposites:
                    continue  # Already added as opposite
                
                stretch_key = f"{user_profile}_TO_{target}"
                if stretch_key not in completed_stretches:
                    recommendations.append(StretchRecommendation(
                        profile_from=user_profile,
                        profile_to=target,
                        growth_type="adjacent",
                        difficulty=3,
                        description=f"Stretch from {user_profile} to {target}",
                        why_recommended=f"Growth opportunity: explore {target} voice"
                    ))
        
        # Limit to tier max and requested max
        max_allowed = min(tier_config['max_types'], max_results)
        return recommendations[:max_allowed]


recommender = StretchRecommender()


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/eligibility/{user_id}", response_model=StretchEligibility)
async def check_eligibility(user_id: UUID):
    """
    Check if user is eligible for STRETCH exercises.
    Requires: 5+ completed analysis rounds AND paid tier.
    """
    # In production, fetch from DB
    # Mock response for now
    return StretchEligibility(
        is_eligible=True,
        rounds_completed=7,
        rounds_required=5,
        tier="pro",
        tier_allows_stretch=True,
        reason=None
    )


@router.get("/recommend/{user_id}", response_model=List[StretchRecommendation])
async def get_recommendations(user_id: UUID, max_results: int = 3):
    """
    Get personalized stretch recommendations for user.
    Based on their profile, tier, and completion history.
    """
    # In production, fetch user data from DB
    user_profile = "ASSERTIVE"  # Mock
    user_tier = "pro"  # Mock
    completed = []  # Mock
    
    return recommender.get_recommendations(
        user_profile=user_profile,
        user_tier=user_tier,
        completed_stretches=completed,
        max_results=max_results
    )


@router.post("/start", response_model=StretchExercise)
async def start_stretch(
    user_id: UUID = Body(...),
    profile_from: str = Body(...),
    profile_to: str = Body(...)
):
    """
    Start a new stretch exercise.
    Creates exercise record and first cycle.
    """
    exercise_id = uuid4()
    now = datetime.utcnow()
    
    # 7-day expiry for trial incentive
    expires_at = now + timedelta(days=7)
    
    # In production, create DB records
    return StretchExercise(
        id=exercise_id,
        profile_from=profile_from,
        profile_to=profile_to,
        growth_type="opposite",  # Would be looked up
        status="active",
        cycles_completed=0,
        total_words=0,
        started_at=now,
        expires_at=expires_at,
        current_cycle=1,
        current_prompt=1
    )


@router.get("/current/{user_id}", response_model=Optional[StretchExercise])
async def get_current_exercise(user_id: UUID):
    """
    Get user's current active stretch exercise.
    Returns None if no active exercise.
    """
    # In production, fetch from DB
    return None


@router.get("/exercise/{exercise_id}", response_model=StretchExercise)
async def get_exercise(exercise_id: UUID):
    """Get details of a specific stretch exercise."""
    # In production, fetch from DB
    raise HTTPException(status_code=404, detail="Exercise not found")


@router.get("/cycle/{exercise_id}/{cycle_number}", response_model=StretchCycle)
async def get_cycle(exercise_id: UUID, cycle_number: int):
    """Get details of a specific cycle within an exercise."""
    if cycle_number < 1 or cycle_number > 5:
        raise HTTPException(status_code=400, detail="Cycle must be 1-5")
    
    # In production, fetch from DB
    raise HTTPException(status_code=404, detail="Cycle not found")


@router.get("/prompt/{exercise_id}/{cycle_number}/{prompt_number}", response_model=StretchPrompt)
async def get_prompt(exercise_id: UUID, cycle_number: int, prompt_number: int):
    """
    Get a specific prompt for user to respond to.
    Prompt is resolved from base + modifiers based on user context.
    """
    if cycle_number < 1 or cycle_number > 5:
        raise HTTPException(status_code=400, detail="Cycle must be 1-5")
    if prompt_number < 1 or prompt_number > 3:
        raise HTTPException(status_code=400, detail="Prompt must be 1-3")
    
    # In production:
    # 1. Get user context (country, stance)
    # 2. Get base prompt from DB
    # 3. Apply modifiers
    # 4. Return resolved prompt
    
    # Mock response
    return StretchPrompt(
        id=uuid4(),
        prompt_number=prompt_number,
        story_starter="The fog rolled in from the harbour. She hadn't expected to feel this way.",
        instruction="Continue this scene. Write in a voice that's different from your natural style.",
        word_minimum=100,
        cycle_word_target=500
    )


@router.post("/input/{exercise_id}/{cycle_number}/{prompt_number}")
async def submit_input(
    exercise_id: UUID,
    cycle_number: int,
    prompt_number: int,
    input_data: StretchInput
):
    """
    Submit user's response to a prompt.
    Validates keystrokes (ZERO TOLERANCE for paste).
    """
    if cycle_number < 1 or cycle_number > 5:
        raise HTTPException(status_code=400, detail="Cycle must be 1-5")
    if prompt_number < 1 or prompt_number > 3:
        raise HTTPException(status_code=400, detail="Prompt must be 1-3")
    
    # Validate keystrokes - ZERO TOLERANCE
    validation = validator.validate(input_data.keystroke_data)
    
    if not validation.valid:
        # Rejection - paste detected or minimum not met
        return {
            "accepted": False,
            "validation": validation.dict(),
            "next_action": "retry" if validation.reason == "MINIMUM_NOT_MET" else "blocked"
        }
    
    # Input accepted
    # In production:
    # 1. Save input to DB
    # 2. Update cycle progress
    # 3. Check if cycle complete (3 prompts)
    # 4. Check if exercise complete (5 cycles)
    # 5. Update user stats
    # 6. Emit meta events
    
    return {
        "accepted": True,
        "validation": validation.dict(),
        "word_count": validation.word_count,
        "cycle_progress": {
            "prompts_completed": prompt_number,
            "prompts_remaining": 3 - prompt_number,
            "words_this_cycle": validation.word_count,  # Would accumulate
            "target_words": 500
        },
        "next_action": "next_prompt" if prompt_number < 3 else "cycle_complete"
    }


@router.post("/complete-cycle/{exercise_id}/{cycle_number}")
async def complete_cycle(exercise_id: UUID, cycle_number: int):
    """
    Mark a cycle as complete.
    Called after all 3 prompts are submitted and validated.
    """
    # In production:
    # 1. Verify all 3 prompts completed
    # 2. Update cycle status
    # 3. Create next cycle if < 5
    # 4. Update exercise progress
    
    return {
        "cycle_completed": cycle_number,
        "total_cycles_completed": cycle_number,
        "exercise_complete": cycle_number >= 5,
        "next_cycle": cycle_number + 1 if cycle_number < 5 else None
    }


@router.get("/progress/{user_id}", response_model=StretchProgress)
async def get_progress(user_id: UUID):
    """
    Get user's overall stretch progress for dashboard display.
    """
    # In production, aggregate from DB
    return StretchProgress(
        total_words_written=0,
        total_exercises_completed=0,
        total_cycles_completed=0,
        current_exercise=None,
        current_cycle=None,
        current_prompt=None,
        streak_days=0,
        profiles_explored=[]
    )


@router.get("/history/{user_id}")
async def get_history(user_id: UUID, limit: int = 10):
    """
    Get user's stretch exercise history.
    """
    # In production, fetch from DB
    return {
        "exercises": [],
        "total": 0,
        "words_written": 0
    }


@router.post("/abandon/{exercise_id}")
async def abandon_exercise(exercise_id: UUID):
    """
    Abandon current exercise.
    Saves progress at last completed cycle.
    """
    # In production:
    # 1. Mark exercise as abandoned
    # 2. Save last completed cycle
    # 3. Update user stats
    
    return {
        "abandoned": True,
        "saved_at_cycle": 2,  # Example
        "can_resume": False,  # Fresh start required
        "words_counted": 1000  # Words from completed cycles still count
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CTA ENDPOINTS (for dashboard/sidebar/funnel integration)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/cta/{user_id}")
async def get_stretch_cta(user_id: UUID):
    """
    Get CTA data for stretch feature.
    Returns appropriate CTA based on user state.
    """
    # In production, determine user state
    # Mock: user is eligible but hasn't started
    
    return {
        "show_cta": True,
        "cta_type": "initial_offer",  # or "resume", "completed", "upgrade"
        "headline": "Ready to Stretch?",
        "subhead": "Push your voice into new territory",
        "cta_text": "Start Your First Stretch",
        "cta_url": "/stretch/start",
        "urgency": None,  # Or "3 days left in trial"
        "progress": None  # Or progress data if mid-exercise
    }


@router.post("/cta/clicked/{user_id}")
async def track_cta_click(user_id: UUID, cta_location: str = Body(...)):
    """Track CTA click for analytics."""
    # In production, log to DB and emit meta event
    return {"tracked": True}


@router.post("/cta/dismissed/{user_id}")
async def track_cta_dismissed(user_id: UUID):
    """Track CTA dismissal for analytics."""
    # In production, log and potentially reduce CTA frequency
    return {"tracked": True}


# ═══════════════════════════════════════════════════════════════════════════════
# APPROVED IMPLEMENTATIONS (v3.1.3)
# ═══════════════════════════════════════════════════════════════════════════════

# Decision 5C: Trial Extension
async def extend_trial_on_stretch_start(user_id: str, exercise_id: str):
    """Extend trial by 3 days when user starts first STRETCH."""
    # Implementation per MARS assignment
    pass


# Decision 6A: Milestone System
MILESTONES = [1000, 5000, 10000, 25000, 50000, 100000]

def check_milestone_reached(old_total: int, new_total: int):
    """Check if a new milestone was crossed."""
    for milestone in MILESTONES:
        if old_total < milestone <= new_total:
            return milestone
    return None


# Decision 11A: Feature Flag
STRETCH_ROLLOUT = {
    'enabled': True,
    'percentage': 10,  # Week 1: 10%
    'phase': 'soft_launch'
}

def is_stretch_enabled_for_user(user_id: str) -> bool:
    """Check if STRETCH is enabled for this user."""
    import hashlib
    if not STRETCH_ROLLOUT['enabled']:
        return False
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    return (hash_value % 100) < STRETCH_ROLLOUT['percentage']


# Decision 11C: Rollback Thresholds
ROLLBACK_THRESHOLDS = {
    'error_rate': 0.02,
    'negative_feedback': 0.15,
    'churn_lift': 0.10
}


# ═══════════════════════════════════════════════════════════════════════════════
# P1-FIX-3: VOICE PROFILE UPDATE AFTER STRETCH
# ═══════════════════════════════════════════════════════════════════════════════

async def update_voice_profile_after_stretch(
    user_id: str,
    exercise_id: str,
    profile_from: str,
    profile_to: str,
    total_words: int
):
    """
    Update user's Voice Profile after completing a STRETCH exercise.
    
    This adds the 'stretched to' profile to the user's explored voices
    and adjusts their voice profile metrics accordingly.
    """
    try:
        # Get current voice profile
        voice_profile = await get_voice_profile(user_id)
        
        if not voice_profile:
            voice_profile = {
                'user_id': user_id,
                'primary_voice': profile_from,
                'explored_voices': [],
                'stretch_history': [],
                'total_stretch_words': 0
            }
        
        # Add to explored voices if not already there
        if profile_to not in voice_profile.get('explored_voices', []):
            voice_profile['explored_voices'].append(profile_to)
        
        # Add to stretch history
        stretch_record = {
            'exercise_id': exercise_id,
            'from': profile_from,
            'to': profile_to,
            'words': total_words,
            'completed_at': datetime.utcnow().isoformat()
        }
        voice_profile.setdefault('stretch_history', []).append(stretch_record)
        
        # Update total stretch words
        voice_profile['total_stretch_words'] = voice_profile.get('total_stretch_words', 0) + total_words
        
        # Calculate voice flexibility score (0-100)
        # More explored voices = higher flexibility
        explored_count = len(voice_profile.get('explored_voices', []))
        voice_profile['flexibility_score'] = min(100, explored_count * 10 + (total_words // 1000))
        
        # Save updated profile
        await save_voice_profile(user_id, voice_profile)
        
        # Emit event for meta orchestrator
        await emit_event('voice_profile.updated', {
            'user_id': user_id,
            'exercise_id': exercise_id,
            'new_explored_voice': profile_to,
            'total_explored': explored_count,
            'flexibility_score': voice_profile['flexibility_score']
        })
        
        return voice_profile
        
    except Exception as e:
        print(f"[VoiceProfile] Update failed for user {user_id}: {e}")
        raise


async def get_voice_profile(user_id: str):
    """Get user's voice profile from database."""
    # Placeholder - implement with actual DB
    return None


async def save_voice_profile(user_id: str, profile: dict):
    """Save user's voice profile to database."""
    # Placeholder - implement with actual DB
    pass


async def emit_event(event_name: str, data: dict):
    """Emit event to meta orchestrator."""
    # Placeholder - implement with actual event system
    print(f"[Event] {event_name}: {data}")


# ═══════════════════════════════════════════════════════════════════════════════
# P1-FIX-4: ANALYTICS EVENT TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

STRETCH_ANALYTICS_EVENTS = [
    'stretch.eligible',
    'stretch.cta.shown',
    'stretch.cta.clicked',
    'stretch.started',
    'stretch.prompt.completed',
    'stretch.cycle.completed',
    'stretch.completed',
    'stretch.abandoned',
    'stretch.shared',  # This was missing!
]


async def track_stretch_event(
    event_name: str,
    user_id: str,
    data: dict
):
    """
    Track STRETCH analytics events.
    P1-FIX-4: Ensures stretch.shared is properly tracked.
    """
    if event_name not in STRETCH_ANALYTICS_EVENTS:
        print(f"[Analytics] Warning: Unknown event {event_name}")
    
    event_record = {
        'event': event_name,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    # Log to analytics system
    await log_analytics_event(event_record)
    
    # Also emit to meta orchestrator for real-time tracking
    await emit_event(event_name, {
        'user_id': user_id,
        **data
    })
    
    return event_record


async def log_analytics_event(event: dict):
    """Log event to analytics storage."""
    # Placeholder - implement with actual analytics
    print(f"[Analytics] {event['event']}: {event['data']}")


# API endpoint for share tracking
from fastapi import APIRouter

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

@analytics_router.post("/event")
async def track_event_endpoint(
    event_name: str = Body(...),
    user_id: str = Body(...),
    data: dict = Body(default={})
):
    """
    Track analytics event.
    P1-FIX-4: This endpoint handles stretch.shared events from frontend.
    """
    result = await track_stretch_event(event_name, user_id, data)
    return {"success": True, "event_id": str(uuid4())}
