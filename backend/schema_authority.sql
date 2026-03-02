-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY AUTHORITY SYSTEM DATABASE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Extends milestone and curator schemas with Authority tracking.
-- 
-- Run after: schema_milestones.sql, schema_curator.sql

-- ═══════════════════════════════════════════════════════════════════════════
-- ALTER WRITER MILESTONES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Add Authority Writer fields to user_milestones
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS featured_pieces_count INTEGER DEFAULT 0;
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS authority_eligible BOOLEAN DEFAULT FALSE;
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS authority_eligible_at TIMESTAMPTZ;
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS authority_writer BOOLEAN DEFAULT FALSE;
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS authority_writer_since TIMESTAMPTZ;
ALTER TABLE user_milestones ADD COLUMN IF NOT EXISTS authority_last_active TIMESTAMPTZ;


-- ═══════════════════════════════════════════════════════════════════════════
-- ALTER CURATOR MILESTONES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Add Authority Curator fields to curator_milestone_state
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS featured_paths_count INTEGER DEFAULT 0;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS lifetime_posts_read INTEGER DEFAULT 0;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS lifetime_deep_reads INTEGER DEFAULT 0;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS total_path_follows INTEGER DEFAULT 0;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS authority_eligible BOOLEAN DEFAULT FALSE;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS authority_eligible_at TIMESTAMPTZ;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS authority_curator BOOLEAN DEFAULT FALSE;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS authority_curator_since TIMESTAMPTZ;
ALTER TABLE curator_milestone_state ADD COLUMN IF NOT EXISTS authority_last_active TIMESTAMPTZ;


-- ═══════════════════════════════════════════════════════════════════════════
-- AUTHORITY EVENTS LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS authority_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Event type
  event_type TEXT NOT NULL CHECK (event_type IN (
    'authority_writer_eligible',
    'authority_writer_granted',
    'authority_writer_lapsed',
    'authority_writer_reactivated',
    'authority_curator_eligible',
    'authority_curator_granted',
    'authority_curator_lapsed',
    'authority_curator_reactivated',
    'voice_and_taste_achieved',
    'authority_voice_and_taste_achieved'
  )),
  
  -- Context
  metadata JSONB DEFAULT '{}',
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_authority_events_user ON authority_events(user_id, created_at DESC);
CREATE INDEX idx_authority_events_type ON authority_events(event_type);


-- ═══════════════════════════════════════════════════════════════════════════
-- AUTHORITY REQUIREMENTS (Reference table)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS authority_requirements (
  id TEXT PRIMARY KEY,
  
  -- Writer requirements
  writer_featured_pieces INTEGER DEFAULT 3,
  writer_lifetime_words INTEGER DEFAULT 50000,
  writer_streak_30_count INTEGER DEFAULT 2,
  writer_days_as_featured INTEGER DEFAULT 90,
  
  -- Curator requirements
  curator_featured_paths INTEGER DEFAULT 3,
  curator_path_follows INTEGER DEFAULT 50,
  curator_lifetime_deep_reads INTEGER DEFAULT 100,
  curator_days_as_featured INTEGER DEFAULT 90,
  
  -- Inactivity threshold
  inactivity_days INTEGER DEFAULT 180,
  
  -- Timestamps
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default requirements
INSERT INTO authority_requirements (id) VALUES ('default')
ON CONFLICT (id) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Check Authority Writer eligibility
CREATE OR REPLACE FUNCTION check_authority_writer_eligibility(p_user_id UUID)
RETURNS TABLE (
  eligible BOOLEAN,
  featured_pieces_current INTEGER,
  featured_pieces_target INTEGER,
  lifetime_words_current INTEGER,
  lifetime_words_target INTEGER,
  streak_30_current INTEGER,
  streak_30_target INTEGER,
  days_featured_current INTEGER,
  days_featured_target INTEGER
) AS $$
DECLARE
  v_state user_milestones%ROWTYPE;
  v_reqs authority_requirements%ROWTYPE;
  v_days_featured INTEGER;
BEGIN
  SELECT * INTO v_state FROM user_milestones WHERE user_id = p_user_id;
  SELECT * INTO v_reqs FROM authority_requirements WHERE id = 'default';
  
  IF NOT FOUND OR NOT v_state.featured_writer THEN
    RETURN QUERY SELECT 
      FALSE, 0, v_reqs.writer_featured_pieces,
      0, v_reqs.writer_lifetime_words,
      0, v_reqs.writer_streak_30_count,
      0, v_reqs.writer_days_as_featured;
    RETURN;
  END IF;
  
  v_days_featured := EXTRACT(DAY FROM (NOW() - v_state.featured_writer_since))::INTEGER;
  
  RETURN QUERY SELECT
    (v_state.featured_pieces_count >= v_reqs.writer_featured_pieces AND
     v_state.lifetime_keystroke_words >= v_reqs.writer_lifetime_words AND
     v_state.streak_1k_30_count >= v_reqs.writer_streak_30_count AND
     v_days_featured >= v_reqs.writer_days_as_featured),
    v_state.featured_pieces_count, v_reqs.writer_featured_pieces,
    v_state.lifetime_keystroke_words, v_reqs.writer_lifetime_words,
    v_state.streak_1k_30_count, v_reqs.writer_streak_30_count,
    v_days_featured, v_reqs.writer_days_as_featured;
END;
$$ LANGUAGE plpgsql;


-- Check Authority Curator eligibility
CREATE OR REPLACE FUNCTION check_authority_curator_eligibility(p_user_id UUID)
RETURNS TABLE (
  eligible BOOLEAN,
  featured_paths_current INTEGER,
  featured_paths_target INTEGER,
  path_follows_current INTEGER,
  path_follows_target INTEGER,
  deep_reads_current INTEGER,
  deep_reads_target INTEGER,
  days_featured_current INTEGER,
  days_featured_target INTEGER
) AS $$
DECLARE
  v_state curator_milestone_state%ROWTYPE;
  v_reqs authority_requirements%ROWTYPE;
  v_days_featured INTEGER;
BEGIN
  SELECT * INTO v_state FROM curator_milestone_state WHERE user_id = p_user_id;
  SELECT * INTO v_reqs FROM authority_requirements WHERE id = 'default';
  
  IF NOT FOUND OR NOT v_state.featured_curator THEN
    RETURN QUERY SELECT 
      FALSE, 0, v_reqs.curator_featured_paths,
      0, v_reqs.curator_path_follows,
      0, v_reqs.curator_lifetime_deep_reads,
      0, v_reqs.curator_days_as_featured;
    RETURN;
  END IF;
  
  v_days_featured := EXTRACT(DAY FROM (NOW() - v_state.featured_curator_since))::INTEGER;
  
  RETURN QUERY SELECT
    (v_state.featured_paths_count >= v_reqs.curator_featured_paths AND
     v_state.total_path_follows >= v_reqs.curator_path_follows AND
     v_state.lifetime_deep_reads >= v_reqs.curator_lifetime_deep_reads AND
     v_days_featured >= v_reqs.curator_days_as_featured),
    v_state.featured_paths_count, v_reqs.curator_featured_paths,
    v_state.total_path_follows, v_reqs.curator_path_follows,
    v_state.lifetime_deep_reads, v_reqs.curator_lifetime_deep_reads,
    v_days_featured, v_reqs.curator_days_as_featured;
END;
$$ LANGUAGE plpgsql;


-- Grant Authority Writer status
CREATE OR REPLACE FUNCTION grant_authority_writer(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_eligible BOOLEAN;
BEGIN
  SELECT eligible INTO v_eligible FROM check_authority_writer_eligibility(p_user_id);
  
  IF NOT v_eligible THEN
    RETURN FALSE;
  END IF;
  
  UPDATE user_milestones
  SET authority_eligible = TRUE,
      authority_eligible_at = COALESCE(authority_eligible_at, NOW()),
      authority_writer = TRUE,
      authority_writer_since = NOW(),
      authority_last_active = NOW()
  WHERE user_id = p_user_id;
  
  INSERT INTO authority_events (user_id, event_type)
  VALUES (p_user_id, 'authority_writer_granted');
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Grant Authority Curator status
CREATE OR REPLACE FUNCTION grant_authority_curator(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_eligible BOOLEAN;
BEGIN
  SELECT eligible INTO v_eligible FROM check_authority_curator_eligibility(p_user_id);
  
  IF NOT v_eligible THEN
    RETURN FALSE;
  END IF;
  
  UPDATE curator_milestone_state
  SET authority_eligible = TRUE,
      authority_eligible_at = COALESCE(authority_eligible_at, NOW()),
      authority_curator = TRUE,
      authority_curator_since = NOW(),
      authority_last_active = NOW()
  WHERE user_id = p_user_id;
  
  INSERT INTO authority_events (user_id, event_type)
  VALUES (p_user_id, 'authority_curator_granted');
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Check for lapsed Authority status (run daily via cron)
CREATE OR REPLACE FUNCTION check_authority_lapses()
RETURNS INTEGER AS $$
DECLARE
  v_reqs authority_requirements%ROWTYPE;
  v_lapsed_count INTEGER := 0;
BEGIN
  SELECT * INTO v_reqs FROM authority_requirements WHERE id = 'default';
  
  -- Lapse Authority Writers who are inactive
  UPDATE user_milestones
  SET authority_writer = FALSE
  WHERE authority_writer = TRUE
    AND authority_last_active < NOW() - (v_reqs.inactivity_days || ' days')::INTERVAL;
  
  GET DIAGNOSTICS v_lapsed_count = ROW_COUNT;
  
  -- Log lapsed writers
  INSERT INTO authority_events (user_id, event_type)
  SELECT user_id, 'authority_writer_lapsed'
  FROM user_milestones
  WHERE authority_writer = FALSE
    AND authority_writer_since IS NOT NULL
    AND authority_last_active < NOW() - (v_reqs.inactivity_days || ' days')::INTERVAL;
  
  -- Lapse Authority Curators who are inactive
  UPDATE curator_milestone_state
  SET authority_curator = FALSE
  WHERE authority_curator = TRUE
    AND authority_last_active < NOW() - (v_reqs.inactivity_days || ' days')::INTERVAL;
  
  GET DIAGNOSTICS v_lapsed_count = v_lapsed_count + ROW_COUNT;
  
  -- Log lapsed curators
  INSERT INTO authority_events (user_id, event_type)
  SELECT user_id, 'authority_curator_lapsed'
  FROM curator_milestone_state
  WHERE authority_curator = FALSE
    AND authority_curator_since IS NOT NULL
    AND authority_last_active < NOW() - (v_reqs.inactivity_days || ' days')::INTERVAL;
  
  RETURN v_lapsed_count;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Authority Writers view
CREATE OR REPLACE VIEW authority_writers AS
SELECT 
  um.user_id,
  u.display_name,
  um.authority_writer_since,
  um.featured_pieces_count,
  um.lifetime_keystroke_words,
  um.streak_1k_30_count,
  um.authority_last_active,
  EXTRACT(DAY FROM (NOW() - um.authority_last_active))::INTEGER as days_since_active
FROM user_milestones um
JOIN users u ON um.user_id = u.id
WHERE um.authority_writer = TRUE
ORDER BY um.authority_writer_since ASC;


-- Authority Curators view
CREATE OR REPLACE VIEW authority_curators AS
SELECT 
  cms.user_id,
  u.display_name,
  cms.authority_curator_since,
  cms.featured_paths_count,
  cms.total_path_follows,
  cms.lifetime_deep_reads,
  cms.authority_last_active,
  EXTRACT(DAY FROM (NOW() - cms.authority_last_active))::INTEGER as days_since_active
FROM curator_milestone_state cms
JOIN users u ON cms.user_id = u.id
WHERE cms.authority_curator = TRUE
ORDER BY cms.authority_curator_since ASC;


-- Voice & Taste achievers
CREATE OR REPLACE VIEW voice_and_taste_achievers AS
SELECT 
  um.user_id,
  u.display_name,
  um.featured_writer,
  um.featured_writer_since,
  um.authority_writer,
  um.authority_writer_since,
  cms.featured_curator,
  cms.featured_curator_since,
  cms.authority_curator,
  cms.authority_curator_since,
  CASE
    WHEN um.authority_writer AND cms.authority_curator THEN 'authority_voice_and_taste'
    WHEN um.featured_writer AND cms.featured_curator THEN 'voice_and_taste'
    ELSE NULL
  END as combined_status
FROM user_milestones um
JOIN users u ON um.user_id = u.id
JOIN curator_milestone_state cms ON um.user_id = cms.user_id
WHERE um.featured_writer = TRUE AND cms.featured_curator = TRUE
ORDER BY 
  (um.authority_writer AND cms.authority_curator) DESC,
  LEAST(um.featured_writer_since, cms.featured_curator_since) ASC;
