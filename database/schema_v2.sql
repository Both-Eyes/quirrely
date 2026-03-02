-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY DATABASE SCHEMA v2.0
-- Adds: Pattern Storage, Profile History, Trial Tracking, Session Linking
-- Compatible with: Supabase, Railway, Neon, any PostgreSQL
-- ═══════════════════════════════════════════════════════════════════════════

-- Run this AFTER schema_combined.sql (this is additive)

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. TOKEN PATTERN STORAGE (feeds the virtuous cycle)
-- ═══════════════════════════════════════════════════════════════════════════

-- Stores aggregate token patterns observed across all analyses
-- This is the core of "LNCP GROWS" - tokens accumulate, patterns emerge
CREATE TABLE IF NOT EXISTS token_patterns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- The pattern itself (first N tokens as signature)
  token_signature VARCHAR(100) NOT NULL,          -- e.g., "3-1-4-1-5-9-2-6"
  token_count INTEGER NOT NULL,                    -- How many tokens in signature
  
  -- Aggregated profile associations
  profile_counts JSONB DEFAULT '{}',              -- {"ASSERTIVE": 45, "POETIC": 12, ...}
  stance_counts JSONB DEFAULT '{}',               -- {"OPEN": 30, "CLOSED": 20, ...}
  total_observations INTEGER DEFAULT 1,
  
  -- Pattern characteristics
  avg_word_count DECIMAL(6,2),
  avg_sentence_count DECIMAL(4,2),
  
  -- Timestamps
  first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Uniqueness constraint
  UNIQUE(token_signature)
);

-- Index for fast pattern lookups
CREATE INDEX IF NOT EXISTS idx_patterns_signature ON token_patterns(token_signature);
CREATE INDEX IF NOT EXISTS idx_patterns_observations ON token_patterns(total_observations DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_last_seen ON token_patterns(last_seen_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- 2. PROFILE HISTORY (user evolution tracking)
-- ═══════════════════════════════════════════════════════════════════════════

-- Tracks every profile result for a user over time
-- Enables: "See how your voice has evolved"
CREATE TABLE IF NOT EXISTS profile_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Who (can be user_id OR session_id, not both required)
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id VARCHAR(100),
  
  -- The result
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  
  -- Analysis details
  word_count INTEGER,
  sentence_count INTEGER,
  token_signature VARCHAR(100),                   -- Links to token_patterns
  confidence_score DECIMAL(4,3),                  -- 0.000 to 1.000
  
  -- Source context
  source VARCHAR(50) DEFAULT 'web',               -- web, extension, api
  input_preview VARCHAR(100),                     -- First 100 chars (for user reference)
  
  -- Full scores (for detailed comparison)
  scores JSONB,                                   -- All profile/stance scores
  
  -- Timestamp
  analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Ensure at least one identifier
  CONSTRAINT profile_history_has_identifier 
    CHECK (user_id IS NOT NULL OR session_id IS NOT NULL)
);

-- Indexes for history queries
CREATE INDEX IF NOT EXISTS idx_history_user ON profile_history(user_id, analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_history_session ON profile_history(session_id);
CREATE INDEX IF NOT EXISTS idx_history_profile ON profile_history(profile, stance);
CREATE INDEX IF NOT EXISTS idx_history_date ON profile_history(analyzed_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- 3. TRIAL TRACKING
-- ═══════════════════════════════════════════════════════════════════════════

-- Tracks 7-day trial status for users
CREATE TABLE IF NOT EXISTS trials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  
  -- Trial period
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ends_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days'),
  
  -- Status
  status VARCHAR(20) DEFAULT 'active',            -- active, expired, converted, cancelled
  
  -- Conversion tracking
  converted_to_pro BOOLEAN DEFAULT FALSE,
  conversion_date TIMESTAMP WITH TIME ZONE,
  conversion_price DECIMAL(6,2),                  -- $0.99 first month or $4.99 regular
  
  -- Engagement during trial
  analyses_count INTEGER DEFAULT 0,
  features_used JSONB DEFAULT '[]',               -- ["save_results", "history", "insights"]
  
  -- Reminder tracking
  reminder_sent_day3 BOOLEAN DEFAULT FALSE,
  reminder_sent_day6 BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trials_user ON trials(user_id);
CREATE INDEX IF NOT EXISTS idx_trials_status ON trials(status);
CREATE INDEX IF NOT EXISTS idx_trials_ends ON trials(ends_at) WHERE status = 'active';


-- ═══════════════════════════════════════════════════════════════════════════
-- 4. SESSION LINKING (anonymous → authenticated handoff)
-- ═══════════════════════════════════════════════════════════════════════════

-- Links anonymous sessions to user accounts after signup
-- Enables: "Your previous analyses are now saved to your account"
CREATE TABLE IF NOT EXISTS session_links (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- The link
  session_id VARCHAR(100) NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  
  -- Metadata
  linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  profiles_migrated INTEGER DEFAULT 0,            -- How many profile_history records migrated
  
  UNIQUE(session_id)
);

CREATE INDEX IF NOT EXISTS idx_session_links_user ON session_links(user_id);
CREATE INDEX IF NOT EXISTS idx_session_links_session ON session_links(session_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 5. LNCP LEARNING LOG (system improvement tracking)
-- ═══════════════════════════════════════════════════════════════════════════

-- Tracks when and how LNCP improves from accumulated patterns
-- This closes the virtuous cycle: patterns → learning → better profiles
CREATE TABLE IF NOT EXISTS lncp_learning_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- What was learned
  learned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  pattern_type VARCHAR(50) NOT NULL,              -- "threshold_adjustment", "new_signal", "weight_change"
  
  -- Details
  pattern_data JSONB NOT NULL,                    -- The actual learning data
  source_pattern_count INTEGER,                   -- How many patterns informed this
  
  -- Application
  applied_in_version VARCHAR(20),                 -- e.g., "v3.9"
  impact_description TEXT,
  
  -- Validation
  accuracy_before DECIMAL(5,4),
  accuracy_after DECIMAL(5,4),
  
  -- Status
  status VARCHAR(20) DEFAULT 'proposed',          -- proposed, tested, applied, rejected
  applied_at TIMESTAMP WITH TIME ZONE,
  applied_by VARCHAR(100)                         -- admin or "auto"
);

CREATE INDEX IF NOT EXISTS idx_learning_type ON lncp_learning_log(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learning_status ON lncp_learning_log(status);
CREATE INDEX IF NOT EXISTS idx_learning_date ON lncp_learning_log(learned_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- 6. FEATURE FLAGS (for gating)
-- ═══════════════════════════════════════════════════════════════════════════

-- Simple feature flag system for tier-based gating
CREATE TABLE IF NOT EXISTS feature_flags (
  id SERIAL PRIMARY KEY,
  feature_key VARCHAR(50) NOT NULL UNIQUE,
  feature_name VARCHAR(100) NOT NULL,
  description TEXT,
  
  -- Tier access (true = has access)
  tier_free BOOLEAN DEFAULT FALSE,
  tier_trial BOOLEAN DEFAULT FALSE,
  tier_pro BOOLEAN DEFAULT TRUE,
  
  -- Override for specific users
  user_overrides JSONB DEFAULT '{}',              -- {"user_id": true/false}
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed default feature flags
INSERT INTO feature_flags (feature_key, feature_name, description, tier_free, tier_trial, tier_pro) VALUES
  ('basic_analysis', 'Basic Analysis', 'Run LNCP analysis and see profile', TRUE, TRUE, TRUE),
  ('writer_matches', 'Writer Matches', 'See famous writer recommendations', TRUE, TRUE, TRUE),
  ('save_results', 'Save Results', 'Save analysis results to account', FALSE, TRUE, TRUE),
  ('profile_history', 'Profile History', 'View past analyses and compare', FALSE, TRUE, TRUE),
  ('evolution_tracking', 'Evolution Tracking', 'See how voice changes over time', FALSE, TRUE, TRUE),
  ('detailed_insights', 'Detailed Insights', 'Deep dive into profile characteristics', FALSE, FALSE, TRUE),
  ('export_results', 'Export Results', 'Download results as PDF/JSON', FALSE, FALSE, TRUE),
  ('featured_submission', 'Featured Submission', 'Submit writing for featured writers', FALSE, FALSE, TRUE),
  ('unlimited_analyses', 'Unlimited Analyses', 'No daily analysis limit', FALSE, TRUE, TRUE),
  ('extension_sync', 'Extension Sync', 'Sync with browser extension', FALSE, TRUE, TRUE)
ON CONFLICT (feature_key) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- 7. DAILY ANALYTICS (for system health)
-- ═══════════════════════════════════════════════════════════════════════════

-- Aggregated daily stats for monitoring the virtuous cycle
CREATE TABLE IF NOT EXISTS daily_analytics (
  date DATE PRIMARY KEY,
  
  -- Volume
  total_analyses INTEGER DEFAULT 0,
  unique_users INTEGER DEFAULT 0,
  unique_sessions INTEGER DEFAULT 0,
  
  -- Profiles distribution
  profile_distribution JSONB DEFAULT '{}',        -- {"ASSERTIVE": 120, "POETIC": 89, ...}
  stance_distribution JSONB DEFAULT '{}',         -- {"OPEN": 200, "CLOSED": 150, ...}
  
  -- Patterns
  new_patterns_discovered INTEGER DEFAULT 0,
  patterns_reinforced INTEGER DEFAULT 0,
  
  -- Funnel
  signups INTEGER DEFAULT 0,
  trials_started INTEGER DEFAULT 0,
  trials_converted INTEGER DEFAULT 0,
  
  -- Engagement
  avg_word_count DECIMAL(8,2),
  avg_analyses_per_user DECIMAL(4,2),
  
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- 8. HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to record a pattern observation
CREATE OR REPLACE FUNCTION record_pattern_observation(
  p_signature VARCHAR,
  p_token_count INTEGER,
  p_profile VARCHAR,
  p_stance VARCHAR,
  p_word_count INTEGER DEFAULT NULL,
  p_sentence_count INTEGER DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  v_pattern_id UUID;
  v_profile_counts JSONB;
  v_stance_counts JSONB;
BEGIN
  -- Try to get existing pattern
  SELECT id, profile_counts, stance_counts 
  INTO v_pattern_id, v_profile_counts, v_stance_counts
  FROM token_patterns 
  WHERE token_signature = p_signature;
  
  IF v_pattern_id IS NULL THEN
    -- Create new pattern
    INSERT INTO token_patterns (
      token_signature, token_count, profile_counts, stance_counts,
      avg_word_count, avg_sentence_count
    ) VALUES (
      p_signature, p_token_count,
      jsonb_build_object(p_profile, 1),
      jsonb_build_object(p_stance, 1),
      p_word_count, p_sentence_count
    ) RETURNING id INTO v_pattern_id;
  ELSE
    -- Update existing pattern
    UPDATE token_patterns SET
      profile_counts = profile_counts || 
        jsonb_build_object(p_profile, COALESCE((profile_counts->>p_profile)::INTEGER, 0) + 1),
      stance_counts = stance_counts || 
        jsonb_build_object(p_stance, COALESCE((stance_counts->>p_stance)::INTEGER, 0) + 1),
      total_observations = total_observations + 1,
      last_seen_at = NOW(),
      avg_word_count = CASE 
        WHEN p_word_count IS NOT NULL 
        THEN (COALESCE(avg_word_count, 0) * (total_observations - 1) + p_word_count) / total_observations
        ELSE avg_word_count 
      END,
      avg_sentence_count = CASE 
        WHEN p_sentence_count IS NOT NULL 
        THEN (COALESCE(avg_sentence_count, 0) * (total_observations - 1) + p_sentence_count) / total_observations
        ELSE avg_sentence_count 
      END
    WHERE id = v_pattern_id;
  END IF;
  
  RETURN v_pattern_id;
END;
$$ LANGUAGE plpgsql;


-- Function to link session to user and migrate history
CREATE OR REPLACE FUNCTION link_session_to_user(
  p_session_id VARCHAR,
  p_user_id UUID
) RETURNS INTEGER AS $$
DECLARE
  v_migrated INTEGER;
BEGIN
  -- Create the link
  INSERT INTO session_links (session_id, user_id)
  VALUES (p_session_id, p_user_id)
  ON CONFLICT (session_id) DO NOTHING;
  
  -- Migrate profile history
  UPDATE profile_history
  SET user_id = p_user_id
  WHERE session_id = p_session_id AND user_id IS NULL;
  
  GET DIAGNOSTICS v_migrated = ROW_COUNT;
  
  -- Update the link record
  UPDATE session_links
  SET profiles_migrated = v_migrated
  WHERE session_id = p_session_id;
  
  -- Update sessions table if it exists
  UPDATE sessions
  SET user_id = p_user_id
  WHERE id = p_session_id AND user_id IS NULL;
  
  RETURN v_migrated;
END;
$$ LANGUAGE plpgsql;


-- Function to check feature access
CREATE OR REPLACE FUNCTION check_feature_access(
  p_user_id UUID,
  p_feature_key VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
  v_tier VARCHAR;
  v_flag RECORD;
  v_override BOOLEAN;
BEGIN
  -- Get user tier
  SELECT subscription_tier INTO v_tier
  FROM users WHERE id = p_user_id;
  
  IF v_tier IS NULL THEN
    v_tier := 'free';
  END IF;
  
  -- Check for trial status
  IF v_tier = 'free' THEN
    IF EXISTS (
      SELECT 1 FROM trials 
      WHERE user_id = p_user_id 
        AND status = 'active' 
        AND ends_at > NOW()
    ) THEN
      v_tier := 'trial';
    END IF;
  END IF;
  
  -- Get feature flag
  SELECT * INTO v_flag
  FROM feature_flags
  WHERE feature_key = p_feature_key AND is_active = TRUE;
  
  IF v_flag IS NULL THEN
    RETURN FALSE;
  END IF;
  
  -- Check user override
  v_override := (v_flag.user_overrides->>p_user_id::TEXT)::BOOLEAN;
  IF v_override IS NOT NULL THEN
    RETURN v_override;
  END IF;
  
  -- Check tier access
  RETURN CASE v_tier
    WHEN 'pro' THEN v_flag.tier_pro
    WHEN 'trial' THEN v_flag.tier_trial
    ELSE v_flag.tier_free
  END;
END;
$$ LANGUAGE plpgsql;


-- Function to start a trial
CREATE OR REPLACE FUNCTION start_trial(
  p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
  v_existing RECORD;
BEGIN
  -- Check if user already had a trial
  SELECT * INTO v_existing FROM trials WHERE user_id = p_user_id;
  
  IF v_existing IS NOT NULL THEN
    -- Already had trial - don't allow another
    RETURN FALSE;
  END IF;
  
  -- Create trial
  INSERT INTO trials (user_id) VALUES (p_user_id);
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Function to get user's profile evolution
CREATE OR REPLACE FUNCTION get_profile_evolution(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 20
) RETURNS TABLE (
  profile VARCHAR,
  stance VARCHAR,
  analyzed_at TIMESTAMP WITH TIME ZONE,
  word_count INTEGER,
  days_ago INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ph.profile,
    ph.stance,
    ph.analyzed_at,
    ph.word_count,
    EXTRACT(DAY FROM NOW() - ph.analyzed_at)::INTEGER as days_ago
  FROM profile_history ph
  WHERE ph.user_id = p_user_id
  ORDER BY ph.analyzed_at DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- 9. VIEWS FOR COMMON QUERIES
-- ═══════════════════════════════════════════════════════════════════════════

-- View: Users with their current tier (including trial status)
CREATE OR REPLACE VIEW user_tiers AS
SELECT 
  u.id,
  u.email,
  u.subscription_tier,
  CASE 
    WHEN u.subscription_tier = 'pro' THEN 'pro'
    WHEN t.status = 'active' AND t.ends_at > NOW() THEN 'trial'
    ELSE 'free'
  END as effective_tier,
  t.ends_at as trial_ends_at,
  t.analyses_count as trial_analyses
FROM users u
LEFT JOIN trials t ON u.id = t.user_id;


-- View: Top patterns (most observed)
CREATE OR REPLACE VIEW top_patterns AS
SELECT 
  token_signature,
  total_observations,
  profile_counts,
  stance_counts,
  first_seen_at,
  last_seen_at,
  -- Calculate dominant profile
  (SELECT key FROM jsonb_each_text(profile_counts) ORDER BY value::INTEGER DESC LIMIT 1) as dominant_profile,
  -- Calculate dominant stance
  (SELECT key FROM jsonb_each_text(stance_counts) ORDER BY value::INTEGER DESC LIMIT 1) as dominant_stance
FROM token_patterns
WHERE total_observations >= 5
ORDER BY total_observations DESC;


-- View: Recent profile distribution
CREATE OR REPLACE VIEW recent_profile_distribution AS
SELECT 
  profile,
  stance,
  COUNT(*) as count,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(word_count) as avg_word_count
FROM profile_history
WHERE analyzed_at > NOW() - INTERVAL '7 days'
GROUP BY profile, stance
ORDER BY count DESC;


-- ═══════════════════════════════════════════════════════════════════════════
-- DONE - Schema v2 applied
-- ═══════════════════════════════════════════════════════════════════════════
