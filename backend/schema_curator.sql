-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY CURATOR TIER DATABASE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Tables for Curator tier, milestone tracking, and Featured Curator paths.
-- 
-- Run after: schema_reader.sql

-- ═══════════════════════════════════════════════════════════════════════════
-- CURATOR MILESTONE STATE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS curator_milestone_state (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Window tracking
  window_start TIMESTAMPTZ,
  window_end TIMESTAMPTZ,
  window_active BOOLEAN DEFAULT FALSE,
  
  -- Posts read (target: 20)
  posts_read INTEGER DEFAULT 0,
  posts_read_ids TEXT[] DEFAULT '{}',
  posts_read_complete BOOLEAN DEFAULT FALSE,
  
  -- Deep reads (target: 5)
  deep_reads INTEGER DEFAULT 0,
  deep_read_ids TEXT[] DEFAULT '{}',
  deep_reads_complete BOOLEAN DEFAULT FALSE,
  
  -- Profile types explored (target: 5)
  profile_types_explored TEXT[] DEFAULT '{}',
  profile_types_complete BOOLEAN DEFAULT FALSE,
  
  -- Bookmarks (target: 10)
  bookmarks_count INTEGER DEFAULT 0,
  bookmarks_complete BOOLEAN DEFAULT FALSE,
  
  -- Reading streak (target: 7)
  reading_streak_current INTEGER DEFAULT 0,
  reading_streak_last_date DATE,
  streak_complete BOOLEAN DEFAULT FALSE,
  
  -- Featured eligibility
  featured_eligible BOOLEAN DEFAULT FALSE,
  featured_eligible_at TIMESTAMPTZ,
  
  -- Featured Curator status
  featured_curator BOOLEAN DEFAULT FALSE,
  featured_curator_since TIMESTAMPTZ,
  featured_path_id UUID,
  featured_path_url TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger for updated_at
CREATE TRIGGER curator_milestone_state_updated
  BEFORE UPDATE ON curator_milestone_state
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- CURATED PATHS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS curated_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Path content
  title TEXT NOT NULL,
  intro TEXT NOT NULL,  -- 100 words max
  post_ids TEXT[] NOT NULL,  -- 4-6 profile IDs
  
  -- Agreements
  agreement_original BOOLEAN NOT NULL DEFAULT FALSE,
  agreement_permission BOOLEAN NOT NULL DEFAULT FALSE,
  agreement_read_all BOOLEAN NOT NULL DEFAULT FALSE,
  agreement_accepted_at TIMESTAMPTZ NOT NULL,
  
  -- Review status
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  reviewed_at TIMESTAMPTZ,
  reviewer_id UUID,
  reviewer_notes TEXT,
  
  -- If accepted
  published_url TEXT,
  published_at TIMESTAMPTZ,
  
  -- Stats
  times_followed INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_curated_paths_user ON curated_paths(user_id);
CREATE INDEX idx_curated_paths_status ON curated_paths(status);
CREATE INDEX idx_curated_paths_published ON curated_paths(published_at DESC) WHERE status = 'accepted';

-- Trigger for updated_at
CREATE TRIGGER curated_paths_updated
  BEFORE UPDATE ON curated_paths
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- PATH FOLLOWS (When someone follows a curated path)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS path_follows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id TEXT,  -- For anonymous
  path_id UUID REFERENCES curated_paths(id) ON DELETE CASCADE,
  
  -- Progress
  posts_completed TEXT[] DEFAULT '{}',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  
  UNIQUE(user_id, path_id)
);

CREATE INDEX idx_path_follows_path ON path_follows(path_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- CURATOR MILESTONE EVENTS (Audit log)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS curator_milestone_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  milestone_type TEXT NOT NULL,  -- posts_read, deep_reads, profile_types, bookmarks, reading_streak, featured_eligible
  
  -- Context
  profile_id TEXT,
  is_deep_read BOOLEAN,
  
  -- Triggered at
  triggered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_curator_milestone_events_user ON curator_milestone_events(user_id, triggered_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE curator_milestone_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE curated_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE path_follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE curator_milestone_events ENABLE ROW LEVEL SECURITY;

-- Users can view/update their own milestone state
CREATE POLICY "Users can view own curator state" ON curator_milestone_state
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own curator state" ON curator_milestone_state
  FOR UPDATE USING (auth.uid() = user_id);

-- Users can view their own paths and all published paths
CREATE POLICY "Users can view own paths" ON curated_paths
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Published paths are public" ON curated_paths
  FOR SELECT USING (status = 'accepted');

CREATE POLICY "Users can create paths" ON curated_paths
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can manage their own follows
CREATE POLICY "Users can manage own follows" ON path_follows
  FOR ALL USING (auth.uid() = user_id);

-- Users can view their own milestone events
CREATE POLICY "Users can view own milestone events" ON curator_milestone_events
  FOR SELECT USING (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Start or reset 30-day window
CREATE OR REPLACE FUNCTION start_curator_window(p_user_id UUID)
RETURNS curator_milestone_state AS $$
DECLARE
  v_state curator_milestone_state;
BEGIN
  INSERT INTO curator_milestone_state (
    user_id,
    window_start,
    window_end,
    window_active
  ) VALUES (
    p_user_id,
    NOW(),
    NOW() + INTERVAL '30 days',
    TRUE
  )
  ON CONFLICT (user_id) DO UPDATE SET
    window_start = NOW(),
    window_end = NOW() + INTERVAL '30 days',
    window_active = TRUE,
    posts_read = 0,
    posts_read_ids = '{}',
    posts_read_complete = FALSE,
    deep_reads = 0,
    deep_read_ids = '{}',
    deep_reads_complete = FALSE,
    profile_types_explored = '{}',
    profile_types_complete = FALSE,
    bookmarks_count = 0,
    bookmarks_complete = FALSE,
    reading_streak_current = 0,
    reading_streak_last_date = NULL,
    streak_complete = FALSE,
    featured_eligible = FALSE,
    featured_eligible_at = NULL
  RETURNING * INTO v_state;
  
  RETURN v_state;
END;
$$ LANGUAGE plpgsql;


-- Record post read and check milestones
CREATE OR REPLACE FUNCTION record_curator_post_read(
  p_user_id UUID,
  p_profile_id TEXT,
  p_is_deep_read BOOLEAN DEFAULT FALSE
)
RETURNS TABLE (
  milestone_type TEXT,
  complete BOOLEAN
) AS $$
DECLARE
  v_state curator_milestone_state;
  v_profile_type TEXT;
  v_today DATE := CURRENT_DATE;
BEGIN
  -- Get current state
  SELECT * INTO v_state FROM curator_milestone_state WHERE user_id = p_user_id;
  
  IF NOT FOUND OR NOT v_state.window_active THEN
    RETURN;
  END IF;
  
  -- Check if window expired
  IF NOW() > v_state.window_end THEN
    UPDATE curator_milestone_state SET window_active = FALSE WHERE user_id = p_user_id;
    RETURN;
  END IF;
  
  -- Extract profile type
  v_profile_type := SPLIT_PART(p_profile_id, '-', 1);
  
  -- Update posts read
  IF NOT p_profile_id = ANY(v_state.posts_read_ids) THEN
    UPDATE curator_milestone_state 
    SET posts_read_ids = array_append(posts_read_ids, p_profile_id),
        posts_read = array_length(array_append(posts_read_ids, p_profile_id), 1)
    WHERE user_id = p_user_id
    RETURNING * INTO v_state;
    
    IF v_state.posts_read >= 20 AND NOT v_state.posts_read_complete THEN
      UPDATE curator_milestone_state SET posts_read_complete = TRUE WHERE user_id = p_user_id;
      INSERT INTO curator_milestone_events (user_id, milestone_type, profile_id)
      VALUES (p_user_id, 'posts_read', p_profile_id);
      RETURN QUERY SELECT 'posts_read'::TEXT, TRUE;
    END IF;
  END IF;
  
  -- Update deep reads
  IF p_is_deep_read AND NOT p_profile_id = ANY(v_state.deep_read_ids) THEN
    UPDATE curator_milestone_state 
    SET deep_read_ids = array_append(deep_read_ids, p_profile_id),
        deep_reads = array_length(array_append(deep_read_ids, p_profile_id), 1)
    WHERE user_id = p_user_id
    RETURNING * INTO v_state;
    
    IF v_state.deep_reads >= 5 AND NOT v_state.deep_reads_complete THEN
      UPDATE curator_milestone_state SET deep_reads_complete = TRUE WHERE user_id = p_user_id;
      INSERT INTO curator_milestone_events (user_id, milestone_type, profile_id, is_deep_read)
      VALUES (p_user_id, 'deep_reads', p_profile_id, TRUE);
      RETURN QUERY SELECT 'deep_reads'::TEXT, TRUE;
    END IF;
  END IF;
  
  -- Update profile types
  IF NOT v_profile_type = ANY(v_state.profile_types_explored) THEN
    UPDATE curator_milestone_state 
    SET profile_types_explored = array_append(profile_types_explored, v_profile_type)
    WHERE user_id = p_user_id
    RETURNING * INTO v_state;
    
    IF array_length(v_state.profile_types_explored, 1) >= 5 AND NOT v_state.profile_types_complete THEN
      UPDATE curator_milestone_state SET profile_types_complete = TRUE WHERE user_id = p_user_id;
      INSERT INTO curator_milestone_events (user_id, milestone_type, profile_id)
      VALUES (p_user_id, 'profile_types', p_profile_id);
      RETURN QUERY SELECT 'profile_types'::TEXT, TRUE;
    END IF;
  END IF;
  
  -- Update reading streak
  IF v_state.reading_streak_last_date = v_today THEN
    -- Already counted today
    NULL;
  ELSIF v_state.reading_streak_last_date = v_today - 1 THEN
    UPDATE curator_milestone_state 
    SET reading_streak_current = reading_streak_current + 1,
        reading_streak_last_date = v_today
    WHERE user_id = p_user_id
    RETURNING * INTO v_state;
  ELSE
    UPDATE curator_milestone_state 
    SET reading_streak_current = 1,
        reading_streak_last_date = v_today
    WHERE user_id = p_user_id
    RETURNING * INTO v_state;
  END IF;
  
  IF v_state.reading_streak_current >= 7 AND NOT v_state.streak_complete THEN
    UPDATE curator_milestone_state SET streak_complete = TRUE WHERE user_id = p_user_id;
    INSERT INTO curator_milestone_events (user_id, milestone_type)
    VALUES (p_user_id, 'reading_streak');
    RETURN QUERY SELECT 'reading_streak'::TEXT, TRUE;
  END IF;
  
  -- Check for featured eligibility
  SELECT * INTO v_state FROM curator_milestone_state WHERE user_id = p_user_id;
  
  IF v_state.posts_read_complete AND v_state.deep_reads_complete AND 
     v_state.profile_types_complete AND v_state.bookmarks_complete AND 
     v_state.streak_complete AND NOT v_state.featured_eligible THEN
    UPDATE curator_milestone_state 
    SET featured_eligible = TRUE, featured_eligible_at = NOW()
    WHERE user_id = p_user_id;
    INSERT INTO curator_milestone_events (user_id, milestone_type)
    VALUES (p_user_id, 'featured_eligible');
    RETURN QUERY SELECT 'featured_eligible'::TEXT, TRUE;
  END IF;
  
  RETURN;
END;
$$ LANGUAGE plpgsql;


-- Record bookmark and check milestone
CREATE OR REPLACE FUNCTION record_curator_bookmark(p_user_id UUID)
RETURNS TABLE (
  milestone_type TEXT,
  complete BOOLEAN
) AS $$
DECLARE
  v_state curator_milestone_state;
BEGIN
  UPDATE curator_milestone_state 
  SET bookmarks_count = bookmarks_count + 1
  WHERE user_id = p_user_id
  RETURNING * INTO v_state;
  
  IF NOT FOUND THEN
    RETURN;
  END IF;
  
  IF v_state.bookmarks_count >= 10 AND NOT v_state.bookmarks_complete THEN
    UPDATE curator_milestone_state SET bookmarks_complete = TRUE WHERE user_id = p_user_id;
    INSERT INTO curator_milestone_events (user_id, milestone_type)
    VALUES (p_user_id, 'bookmarks');
    RETURN QUERY SELECT 'bookmarks'::TEXT, TRUE;
  END IF;
  
  -- Check for featured eligibility
  SELECT * INTO v_state FROM curator_milestone_state WHERE user_id = p_user_id;
  
  IF v_state.posts_read_complete AND v_state.deep_reads_complete AND 
     v_state.profile_types_complete AND v_state.bookmarks_complete AND 
     v_state.streak_complete AND NOT v_state.featured_eligible THEN
    UPDATE curator_milestone_state 
    SET featured_eligible = TRUE, featured_eligible_at = NOW()
    WHERE user_id = p_user_id;
    INSERT INTO curator_milestone_events (user_id, milestone_type)
    VALUES (p_user_id, 'featured_eligible');
    RETURN QUERY SELECT 'featured_eligible'::TEXT, TRUE;
  END IF;
  
  RETURN;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Featured Curators public view
CREATE OR REPLACE VIEW featured_curators AS
SELECT 
  cms.user_id,
  u.display_name,
  cms.featured_curator_since,
  cms.featured_path_url,
  cp.title as path_title,
  cp.intro as path_intro,
  cp.post_ids,
  cp.times_followed
FROM curator_milestone_state cms
JOIN users u ON cms.user_id = u.id
LEFT JOIN curated_paths cp ON cms.featured_path_id = cp.id
WHERE cms.featured_curator = TRUE
ORDER BY cms.featured_curator_since DESC;


-- Curator progress view
CREATE OR REPLACE VIEW curator_progress AS
SELECT 
  cms.user_id,
  cms.window_active,
  cms.window_end,
  EXTRACT(DAY FROM (cms.window_end - NOW())) as days_remaining,
  cms.posts_read,
  cms.deep_reads,
  array_length(cms.profile_types_explored, 1) as profile_types_count,
  cms.bookmarks_count,
  cms.reading_streak_current,
  cms.posts_read_complete,
  cms.deep_reads_complete,
  cms.profile_types_complete,
  cms.bookmarks_complete,
  cms.streak_complete,
  cms.featured_eligible,
  cms.featured_curator
FROM curator_milestone_state cms;
