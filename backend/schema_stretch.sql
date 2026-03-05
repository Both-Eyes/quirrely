-- ═══════════════════════════════════════════════════════════════════════════════
-- STRETCH EXERCISE SYSTEM SCHEMA
-- Version: 1.0.0
-- Date: 2026-02-17
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────────
-- ENUMS
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TYPE stretch_status AS ENUM ('active', 'completed', 'abandoned', 'expired');
CREATE TYPE growth_type AS ENUM ('opposite', 'adjacent');
CREATE TYPE country_group AS ENUM ('commonwealth', 'us');
CREATE TYPE validation_result AS ENUM ('valid', 'paste_detected', 'minimum_not_met', 'pending');

-- ─────────────────────────────────────────────────────────────────────────────────
-- PROFILE STRETCH MAPPINGS
-- Defines valid FROM→TO combinations and their growth type
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_mappings (
    id SERIAL PRIMARY KEY,
    profile_from VARCHAR(20) NOT NULL,
    profile_to VARCHAR(20) NOT NULL,
    growth_type growth_type NOT NULL,
    difficulty_rating INT CHECK (difficulty_rating BETWEEN 1 AND 5),
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT different_profiles CHECK (profile_from != profile_to),
    UNIQUE(profile_from, profile_to)
);

-- Insert all valid stretch mappings
INSERT INTO stretch_mappings (profile_from, profile_to, growth_type, difficulty_rating, description) VALUES
-- ASSERTIVE stretches
('ASSERTIVE', 'HEDGED', 'opposite', 5, 'From certainty to qualification'),
('ASSERTIVE', 'POETIC', 'opposite', 5, 'From direct to evocative'),
('ASSERTIVE', 'BALANCED', 'adjacent', 2, 'From strong to fair-minded'),
('ASSERTIVE', 'CONVERSATIONAL', 'adjacent', 2, 'From commanding to friendly'),
('ASSERTIVE', 'DENSE', 'adjacent', 3, 'From clear to layered'),
('ASSERTIVE', 'FORMAL', 'adjacent', 2, 'From direct to elevated'),
('ASSERTIVE', 'INTERROGATIVE', 'adjacent', 3, 'From statements to questions'),
('ASSERTIVE', 'LONGFORM', 'adjacent', 3, 'From punchy to extended'),
('ASSERTIVE', 'MINIMAL', 'adjacent', 3, 'From full to stripped'),

-- BALANCED stretches
('BALANCED', 'ASSERTIVE', 'adjacent', 3, 'From fair to forceful'),
('BALANCED', 'CONVERSATIONAL', 'adjacent', 2, 'From measured to warm'),
('BALANCED', 'DENSE', 'adjacent', 3, 'From clear to rich'),
('BALANCED', 'FORMAL', 'adjacent', 2, 'From accessible to elevated'),
('BALANCED', 'HEDGED', 'adjacent', 2, 'From fair to cautious'),
('BALANCED', 'INTERROGATIVE', 'adjacent', 3, 'From weighing to questioning'),
('BALANCED', 'LONGFORM', 'adjacent', 3, 'From measured to thorough'),
('BALANCED', 'MINIMAL', 'adjacent', 3, 'From complete to essential'),
('BALANCED', 'POETIC', 'adjacent', 4, 'From analytical to lyrical'),

-- CONVERSATIONAL stretches
('CONVERSATIONAL', 'FORMAL', 'opposite', 5, 'From casual to elevated'),
('CONVERSATIONAL', 'ASSERTIVE', 'adjacent', 3, 'From friendly to commanding'),
('CONVERSATIONAL', 'BALANCED', 'adjacent', 2, 'From warm to measured'),
('CONVERSATIONAL', 'DENSE', 'adjacent', 4, 'From light to layered'),
('CONVERSATIONAL', 'HEDGED', 'adjacent', 3, 'From direct to cautious'),
('CONVERSATIONAL', 'INTERROGATIVE', 'adjacent', 2, 'From chatty to curious'),
('CONVERSATIONAL', 'LONGFORM', 'adjacent', 3, 'From breezy to thorough'),
('CONVERSATIONAL', 'MINIMAL', 'adjacent', 3, 'From flowing to stripped'),
('CONVERSATIONAL', 'POETIC', 'adjacent', 4, 'From casual to lyrical'),

-- DENSE stretches
('DENSE', 'MINIMAL', 'opposite', 5, 'From layered to stripped'),
('DENSE', 'ASSERTIVE', 'adjacent', 3, 'From rich to direct'),
('DENSE', 'BALANCED', 'adjacent', 2, 'From complex to fair'),
('DENSE', 'CONVERSATIONAL', 'adjacent', 4, 'From heavy to light'),
('DENSE', 'FORMAL', 'adjacent', 2, 'From packed to precise'),
('DENSE', 'HEDGED', 'adjacent', 3, 'From certain to qualified'),
('DENSE', 'INTERROGATIVE', 'adjacent', 3, 'From statements to questions'),
('DENSE', 'LONGFORM', 'adjacent', 2, 'From compressed to extended'),
('DENSE', 'POETIC', 'adjacent', 3, 'From intellectual to lyrical'),

-- FORMAL stretches
('FORMAL', 'CONVERSATIONAL', 'opposite', 5, 'From elevated to casual'),
('FORMAL', 'POETIC', 'opposite', 5, 'From precise to lyrical'),
('FORMAL', 'ASSERTIVE', 'adjacent', 2, 'From proper to direct'),
('FORMAL', 'BALANCED', 'adjacent', 2, 'From stiff to fair'),
('FORMAL', 'DENSE', 'adjacent', 2, 'From precise to rich'),
('FORMAL', 'HEDGED', 'adjacent', 2, 'From definite to cautious'),
('FORMAL', 'INTERROGATIVE', 'adjacent', 3, 'From statements to inquiry'),
('FORMAL', 'LONGFORM', 'adjacent', 2, 'From proper to thorough'),
('FORMAL', 'MINIMAL', 'adjacent', 4, 'From elaborate to essential'),

-- HEDGED stretches
('HEDGED', 'ASSERTIVE', 'opposite', 5, 'From cautious to certain'),
('HEDGED', 'BALANCED', 'adjacent', 2, 'From qualified to fair'),
('HEDGED', 'CONVERSATIONAL', 'adjacent', 3, 'From careful to warm'),
('HEDGED', 'DENSE', 'adjacent', 3, 'From light to layered'),
('HEDGED', 'FORMAL', 'adjacent', 2, 'From soft to proper'),
('HEDGED', 'INTERROGATIVE', 'adjacent', 2, 'From uncertain to curious'),
('HEDGED', 'LONGFORM', 'adjacent', 3, 'From brief to thorough'),
('HEDGED', 'MINIMAL', 'adjacent', 4, 'From qualified to stark'),
('HEDGED', 'POETIC', 'adjacent', 4, 'From cautious to expressive'),

-- INTERROGATIVE stretches
('INTERROGATIVE', 'MINIMAL', 'opposite', 5, 'From questioning to stark statements'),
('INTERROGATIVE', 'ASSERTIVE', 'adjacent', 4, 'From asking to telling'),
('INTERROGATIVE', 'BALANCED', 'adjacent', 2, 'From curious to fair'),
('INTERROGATIVE', 'CONVERSATIONAL', 'adjacent', 2, 'From probing to chatty'),
('INTERROGATIVE', 'DENSE', 'adjacent', 3, 'From light to layered'),
('INTERROGATIVE', 'FORMAL', 'adjacent', 3, 'From casual inquiry to proper'),
('INTERROGATIVE', 'HEDGED', 'adjacent', 2, 'From questioning to cautious'),
('INTERROGATIVE', 'LONGFORM', 'adjacent', 3, 'From brief to thorough'),
('INTERROGATIVE', 'POETIC', 'adjacent', 4, 'From questions to imagery'),

-- LONGFORM stretches
('LONGFORM', 'MINIMAL', 'opposite', 5, 'From extended to compressed'),
('LONGFORM', 'ASSERTIVE', 'adjacent', 3, 'From thorough to punchy'),
('LONGFORM', 'BALANCED', 'adjacent', 2, 'From comprehensive to fair'),
('LONGFORM', 'CONVERSATIONAL', 'adjacent', 3, 'From detailed to breezy'),
('LONGFORM', 'DENSE', 'adjacent', 2, 'From extended to packed'),
('LONGFORM', 'FORMAL', 'adjacent', 2, 'From thorough to proper'),
('LONGFORM', 'HEDGED', 'adjacent', 3, 'From confident to cautious'),
('LONGFORM', 'INTERROGATIVE', 'adjacent', 3, 'From telling to asking'),
('LONGFORM', 'POETIC', 'adjacent', 4, 'From prose to poetry'),

-- MINIMAL stretches
('MINIMAL', 'DENSE', 'opposite', 5, 'From stripped to layered'),
('MINIMAL', 'INTERROGATIVE', 'opposite', 5, 'From statements to questions'),
('MINIMAL', 'LONGFORM', 'opposite', 5, 'From compressed to extended'),
('MINIMAL', 'ASSERTIVE', 'adjacent', 3, 'From sparse to forceful'),
('MINIMAL', 'BALANCED', 'adjacent', 4, 'From stark to nuanced'),
('MINIMAL', 'CONVERSATIONAL', 'adjacent', 4, 'From terse to warm'),
('MINIMAL', 'FORMAL', 'adjacent', 4, 'From stripped to elaborate'),
('MINIMAL', 'HEDGED', 'adjacent', 4, 'From certain to qualified'),
('MINIMAL', 'POETIC', 'adjacent', 3, 'From stark to lyrical'),

-- POETIC stretches
('POETIC', 'ASSERTIVE', 'opposite', 5, 'From evocative to direct'),
('POETIC', 'FORMAL', 'opposite', 5, 'From lyrical to precise'),
('POETIC', 'BALANCED', 'adjacent', 4, 'From expressive to measured'),
('POETIC', 'CONVERSATIONAL', 'adjacent', 3, 'From elevated to casual'),
('POETIC', 'DENSE', 'adjacent', 3, 'From flowing to packed'),
('POETIC', 'HEDGED', 'adjacent', 4, 'From bold imagery to caution'),
('POETIC', 'INTERROGATIVE', 'adjacent', 4, 'From statements to questions'),
('POETIC', 'LONGFORM', 'adjacent', 2, 'From verse to prose'),
('POETIC', 'MINIMAL', 'adjacent', 3, 'From rich to sparse');

-- ─────────────────────────────────────────────────────────────────────────────────
-- TIER ACCESS CONFIGURATION
-- Defines which stretches each tier can access
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE tier_stretch_config (
    tier VARCHAR(20) PRIMARY KEY,
    max_stretch_types INT NOT NULL,
    allow_opposite BOOLEAN DEFAULT TRUE,
    allow_adjacent BOOLEAN DEFAULT FALSE,
    max_concurrent_exercises INT DEFAULT 1,
    features JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO tier_stretch_config (tier, max_stretch_types, allow_opposite, allow_adjacent, max_concurrent_exercises, features) VALUES
('free', 0, FALSE, FALSE, 0, '{"enabled": false}'),
('pro', 3, TRUE, FALSE, 1, '{"enabled": true, "basic_progress": true}'),
('authority', 6, TRUE, TRUE, 2, '{"enabled": true, "basic_progress": true, "analytics": true, "voice_comparison": true}'),
('curator', 10, TRUE, TRUE, 3, '{"enabled": true, "basic_progress": true, "analytics": true, "voice_comparison": true, "custom_creation": true}');

-- Pro tier specific stretches (opposites only, most accessible)
CREATE TABLE tier_stretch_allowlist (
    id SERIAL PRIMARY KEY,
    tier VARCHAR(20) NOT NULL,
    profile_from VARCHAR(20) NOT NULL,
    profile_to VARCHAR(20) NOT NULL,
    priority INT DEFAULT 0,  -- higher = shown first
    
    UNIQUE(tier, profile_from, profile_to)
);

-- Pro tier gets 3 core opposite stretches
INSERT INTO tier_stretch_allowlist (tier, profile_from, profile_to, priority) VALUES
('pro', 'ASSERTIVE', 'HEDGED', 10),
('pro', 'HEDGED', 'ASSERTIVE', 10),
('pro', 'DENSE', 'MINIMAL', 9),
('pro', 'MINIMAL', 'DENSE', 9),
('pro', 'FORMAL', 'CONVERSATIONAL', 8),
('pro', 'CONVERSATIONAL', 'FORMAL', 8);

-- ─────────────────────────────────────────────────────────────────────────────────
-- BASE PROMPT BANK
-- 450 base prompts: 10 profiles × 5 cycles × 3 positions × 3 variants
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_prompts_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Targeting (profile only - stance/country applied via modifiers)
    target_profile VARCHAR(20) NOT NULL,
    cycle_number INT NOT NULL CHECK (cycle_number BETWEEN 1 AND 5),
    prompt_position INT NOT NULL CHECK (prompt_position BETWEEN 1 AND 3),
    variant INT NOT NULL CHECK (variant BETWEEN 1 AND 3),
    
    -- Content
    story_starter TEXT NOT NULL,  -- "She woke with a start..."
    instruction TEXT NOT NULL,    -- What to write about
    word_guidance TEXT,           -- Tips for hitting word count
    
    -- Metadata
    difficulty INT CHECK (difficulty BETWEEN 1 AND 5) DEFAULT 3,
    tags TEXT[],
    
    -- Analytics
    times_used INT DEFAULT 0,
    avg_word_count FLOAT,
    avg_completion_time_minutes FLOAT,
    success_rate FLOAT,  -- % of users who complete this prompt
    
    -- Management
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(target_profile, cycle_number, prompt_position, variant)
);

-- ─────────────────────────────────────────────────────────────────────────────────
-- PROMPT MODIFIERS
-- Applied dynamically based on user's country and stance
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE prompt_modifiers_country (
    id SERIAL PRIMARY KEY,
    country_group country_group NOT NULL,
    
    -- Spelling/terminology substitutions
    substitutions JSONB DEFAULT '{}',  -- {"harbour": "harbor", "colour": "color"}
    
    -- Cultural reference additions
    cultural_refs JSONB DEFAULT '{}',
    
    -- Tone adjustments
    tone_notes TEXT,
    
    UNIQUE(country_group)
);

INSERT INTO prompt_modifiers_country (country_group, substitutions, cultural_refs, tone_notes) VALUES
('commonwealth', 
 '{"harbor": "harbour", "color": "colour", "traveled": "travelled", "center": "centre"}',
 '{"currency": "pounds/dollars", "seasons": "reversed_southern_hemisphere_aware"}',
 'Commonwealth English conventions. Aware of UK/AU/NZ/CA/IE variations.'),
('us',
 '{"harbour": "harbor", "colour": "color", "travelled": "traveled", "centre": "center"}',
 '{"currency": "dollars", "measurement": "imperial_primary"}',
 'American English conventions. US cultural references.');

CREATE TABLE prompt_modifiers_stance (
    id SERIAL PRIMARY KEY,
    stance VARCHAR(20) NOT NULL,
    
    -- Appended instruction
    instruction_suffix TEXT NOT NULL,
    
    -- Voice guidance
    voice_guidance TEXT NOT NULL,
    
    UNIQUE(stance)
);

INSERT INTO prompt_modifiers_stance (stance, instruction_suffix, voice_guidance) VALUES
('OPEN', 
 'As you write, let questions emerge naturally. Leave room for uncertainty and exploration.',
 'Your writing should invite dialogue. End with openings, not closures.'),
('CLOSED',
 'Write toward clarity and conclusion. Make definitive statements.',
 'Your writing should resolve, not open. Certainty is your tool.'),
('BALANCED',
 'Weigh multiple perspectives as you write. Acknowledge complexity.',
 'Your writing should be fair to all sides. Equilibrium is the goal.'),
('CONTRADICTORY',
 'Embrace tensions and paradoxes. Let opposing truths coexist.',
 'Your writing should hold contradictions without resolving them. Paradox is insight.');

-- ─────────────────────────────────────────────────────────────────────────────────
-- STRETCH EXERCISES
-- One record per user stretch attempt
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- References users table
    
    -- Stretch type
    profile_from VARCHAR(20) NOT NULL,
    profile_to VARCHAR(20) NOT NULL,
    growth_type growth_type NOT NULL,
    mapping_id INT REFERENCES stretch_mappings(id),
    
    -- User context at start
    user_country VARCHAR(2) NOT NULL,
    user_country_group country_group NOT NULL,
    user_stance VARCHAR(20) NOT NULL,
    user_track VARCHAR(20) NOT NULL,
    user_tier VARCHAR(20) NOT NULL,
    
    -- Progress
    status stretch_status DEFAULT 'active',
    cycles_completed INT DEFAULT 0 CHECK (cycles_completed BETWEEN 0 AND 5),
    total_words INT DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    abandoned_at TIMESTAMP,
    expires_at TIMESTAMP,  -- 7 days from start for trial users
    last_activity_at TIMESTAMP DEFAULT NOW(),
    
    -- Analytics
    total_time_minutes INT DEFAULT 0,
    avg_words_per_prompt FLOAT,
    
    -- Indexes
    CONSTRAINT valid_exercise CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status = 'abandoned' AND abandoned_at IS NOT NULL) OR
        (status IN ('active', 'expired'))
    )
);

CREATE INDEX idx_stretch_exercises_user ON stretch_exercises(user_id);
CREATE INDEX idx_stretch_exercises_status ON stretch_exercises(status);
CREATE INDEX idx_stretch_exercises_expires ON stretch_exercises(expires_at) WHERE status = 'active';

-- ─────────────────────────────────────────────────────────────────────────────────
-- STRETCH CYCLES
-- 5 cycles per exercise, 3 prompts per cycle
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES stretch_exercises(id) ON DELETE CASCADE,
    cycle_number INT NOT NULL CHECK (cycle_number BETWEEN 1 AND 5),
    
    -- Progress
    status stretch_status DEFAULT 'active',
    prompts_completed INT DEFAULT 0 CHECK (prompts_completed BETWEEN 0 AND 3),
    total_words INT DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Validation
    all_inputs_valid BOOLEAN DEFAULT FALSE,
    
    UNIQUE(exercise_id, cycle_number)
);

CREATE INDEX idx_stretch_cycles_exercise ON stretch_cycles(exercise_id);

-- ─────────────────────────────────────────────────────────────────────────────────
-- STRETCH INPUTS
-- Individual prompt responses (3 per cycle = 15 per exercise)
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_inputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_id UUID NOT NULL REFERENCES stretch_cycles(id) ON DELETE CASCADE,
    prompt_number INT NOT NULL CHECK (prompt_number BETWEEN 1 AND 3),
    
    -- Prompt given (resolved from base + modifiers)
    base_prompt_id UUID REFERENCES stretch_prompts_base(id),
    rendered_prompt TEXT NOT NULL,  -- Final prompt shown to user
    story_starter TEXT NOT NULL,
    
    -- User response
    user_input TEXT,
    word_count INT DEFAULT 0,
    
    -- Keystroke validation (ZERO TOLERANCE)
    keystroke_data JSONB,  -- Full keystroke log for audit
    keystroke_count INT DEFAULT 0,
    paste_attempts INT DEFAULT 0,  -- Logged even though blocked
    typing_duration_ms INT,
    chars_per_second FLOAT,
    
    -- Validation result
    validation_status validation_result DEFAULT 'pending',
    validation_timestamp TIMESTAMP,
    validation_details JSONB,
    
    -- Timing
    prompt_shown_at TIMESTAMP DEFAULT NOW(),
    input_started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    
    UNIQUE(cycle_id, prompt_number)
);

CREATE INDEX idx_stretch_inputs_cycle ON stretch_inputs(cycle_id);
CREATE INDEX idx_stretch_inputs_validation ON stretch_inputs(validation_status);

-- ─────────────────────────────────────────────────────────────────────────────────
-- USER STRETCH STATISTICS
-- Lifetime accumulation (never decreases)
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE user_stretch_stats (
    user_id UUID PRIMARY KEY,  -- References users table
    
    -- Lifetime totals (NEVER DECREASE)
    total_words_written INT DEFAULT 0,
    total_prompts_completed INT DEFAULT 0,
    total_cycles_completed INT DEFAULT 0,
    total_exercises_completed INT DEFAULT 0,
    
    -- Attempt tracking
    exercises_started INT DEFAULT 0,
    exercises_abandoned INT DEFAULT 0,
    
    -- Current state
    current_exercise_id UUID REFERENCES stretch_exercises(id),
    
    -- Streaks
    current_streak_days INT DEFAULT 0,
    longest_streak_days INT DEFAULT 0,
    last_activity_date DATE,
    
    -- Profile exploration
    profiles_stretched_to TEXT[] DEFAULT '{}',  -- Which profiles user has written in
    favorite_stretch_type VARCHAR(50),  -- Most completed type
    
    -- Performance
    avg_words_per_prompt FLOAT,
    avg_completion_time_days FLOAT,
    completion_rate FLOAT,  -- exercises completed / exercises started
    
    -- Timestamps
    first_stretch_at TIMESTAMP,
    last_stretch_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────────
-- STRETCH ELIGIBILITY TRACKING
-- Track when users become eligible (5 rounds completed)
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE TABLE stretch_eligibility (
    user_id UUID PRIMARY KEY,
    
    -- Eligibility
    is_eligible BOOLEAN DEFAULT FALSE,
    became_eligible_at TIMESTAMP,
    rounds_completed INT DEFAULT 0,
    
    -- Engagement
    cta_shown_count INT DEFAULT 0,
    cta_last_shown_at TIMESTAMP,
    cta_clicked BOOLEAN DEFAULT FALSE,
    cta_clicked_at TIMESTAMP,
    
    -- Conversion (trial to paid via stretch)
    started_stretch_in_trial BOOLEAN DEFAULT FALSE,
    converted_via_stretch BOOLEAN DEFAULT FALSE,
    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────────
-- FUNCTIONS AND TRIGGERS
-- ─────────────────────────────────────────────────────────────────────────────────

-- Function to update user stats when input is validated
CREATE OR REPLACE FUNCTION update_stretch_stats_on_input()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.validation_status = 'valid' AND OLD.validation_status != 'valid' THEN
        -- Update user lifetime stats
        UPDATE user_stretch_stats
        SET 
            total_words_written = total_words_written + NEW.word_count,
            total_prompts_completed = total_prompts_completed + 1,
            last_activity_date = CURRENT_DATE,
            updated_at = NOW()
        WHERE user_id = (
            SELECT se.user_id 
            FROM stretch_exercises se
            JOIN stretch_cycles sc ON sc.exercise_id = se.id
            WHERE sc.id = NEW.cycle_id
        );
        
        -- Update cycle word count
        UPDATE stretch_cycles
        SET total_words = total_words + NEW.word_count,
            prompts_completed = prompts_completed + 1
        WHERE id = NEW.cycle_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stretch_stats
AFTER UPDATE ON stretch_inputs
FOR EACH ROW
EXECUTE FUNCTION update_stretch_stats_on_input();

-- Function to check cycle completion
CREATE OR REPLACE FUNCTION check_cycle_completion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.prompts_completed = 3 AND OLD.prompts_completed < 3 THEN
        -- Mark cycle as completed
        UPDATE stretch_cycles
        SET status = 'completed',
            completed_at = NOW(),
            all_inputs_valid = TRUE
        WHERE id = NEW.id;
        
        -- Update exercise progress
        UPDATE stretch_exercises
        SET cycles_completed = cycles_completed + 1,
            total_words = total_words + NEW.total_words,
            last_activity_at = NOW()
        WHERE id = NEW.exercise_id;
        
        -- Update user stats
        UPDATE user_stretch_stats
        SET total_cycles_completed = total_cycles_completed + 1,
            updated_at = NOW()
        WHERE user_id = (
            SELECT user_id FROM stretch_exercises WHERE id = NEW.exercise_id
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_cycle_completion
AFTER UPDATE ON stretch_cycles
FOR EACH ROW
EXECUTE FUNCTION check_cycle_completion();

-- Function to check exercise completion
CREATE OR REPLACE FUNCTION check_exercise_completion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.cycles_completed = 5 AND OLD.cycles_completed < 5 THEN
        -- Mark exercise as completed
        UPDATE stretch_exercises
        SET status = 'completed',
            completed_at = NOW()
        WHERE id = NEW.id;
        
        -- Update user stats
        UPDATE user_stretch_stats
        SET 
            total_exercises_completed = total_exercises_completed + 1,
            current_exercise_id = NULL,
            profiles_stretched_to = array_append(
                profiles_stretched_to, 
                NEW.profile_to
            ),
            updated_at = NOW()
        WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_exercise_completion
AFTER UPDATE ON stretch_exercises
FOR EACH ROW
EXECUTE FUNCTION check_exercise_completion();

-- Function to check eligibility on analysis completion
CREATE OR REPLACE FUNCTION check_stretch_eligibility()
RETURNS TRIGGER AS $$
BEGIN
    -- This would be called from the analysis completion trigger
    -- When rounds_completed reaches 5, user becomes eligible
    IF NEW.rounds_completed >= 5 AND NOT NEW.is_eligible THEN
        UPDATE stretch_eligibility
        SET is_eligible = TRUE,
            became_eligible_at = NOW()
        WHERE user_id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─────────────────────────────────────────────────────────────────────────────────
-- INDEXES FOR PERFORMANCE
-- ─────────────────────────────────────────────────────────────────────────────────

CREATE INDEX idx_stretch_mappings_from ON stretch_mappings(profile_from);
CREATE INDEX idx_stretch_mappings_type ON stretch_mappings(growth_type);
CREATE INDEX idx_stretch_prompts_profile ON stretch_prompts_base(target_profile);
CREATE INDEX idx_stretch_prompts_active ON stretch_prompts_base(active) WHERE active = TRUE;
CREATE INDEX idx_user_stretch_stats_current ON user_stretch_stats(current_exercise_id) WHERE current_exercise_id IS NOT NULL;

-- ─────────────────────────────────────────────────────────────────────────────────
-- VIEWS FOR COMMON QUERIES
-- ─────────────────────────────────────────────────────────────────────────────────

-- User's current stretch status
CREATE VIEW v_user_stretch_status AS
SELECT 
    uss.user_id,
    uss.total_words_written,
    uss.total_exercises_completed,
    uss.current_exercise_id,
    se.profile_from,
    se.profile_to,
    se.cycles_completed,
    se.status as exercise_status,
    se.expires_at,
    CASE 
        WHEN se.expires_at < NOW() THEN TRUE 
        ELSE FALSE 
    END as is_expired,
    sc.cycle_number as current_cycle,
    sc.prompts_completed as prompts_in_current_cycle
FROM user_stretch_stats uss
LEFT JOIN stretch_exercises se ON se.id = uss.current_exercise_id
LEFT JOIN stretch_cycles sc ON sc.exercise_id = se.id AND sc.status = 'active';

-- Available stretches for a user based on their tier
CREATE VIEW v_available_stretches AS
SELECT 
    sm.*,
    tsc.tier
FROM stretch_mappings sm
CROSS JOIN tier_stretch_config tsc
WHERE sm.active = TRUE
AND (
    (tsc.allow_opposite = TRUE AND sm.growth_type = 'opposite') OR
    (tsc.allow_adjacent = TRUE AND sm.growth_type = 'adjacent')
);

-- ─══════════════════════════════════════════════════════════════════════════════
-- SCHEMA VERSION
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS schema_versions (
    schema_name VARCHAR(50) PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_versions (schema_name, version) VALUES ('stretch', '1.0.0')
ON CONFLICT (schema_name) DO UPDATE SET version = '1.0.0', applied_at = NOW();
