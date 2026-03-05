-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY MILESTONE SYSTEM DATABASE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Extends base schema with:
-- - User milestones tracking
-- - Daily keystroke totals
-- - Featured Writer submissions
-- 
-- Run after: schema_v2.sql

-- ═══════════════════════════════════════════════════════════════════════════
-- USER MILESTONES TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_milestones (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Lifetime stats
  lifetime_keystroke_words INTEGER DEFAULT 0,
  first_500_achieved BOOLEAN DEFAULT FALSE,
  first_500_achieved_at TIMESTAMPTZ,
  
  -- 500/day streak (auth'd users)
  streak_500_current INTEGER DEFAULT 0,
  streak_500_last_date DATE,
  streak_500_3_count INTEGER DEFAULT 0,
  
  -- 1K/day tracking (PRO only)
  daily_1k_count INTEGER DEFAULT 0,
  
  -- 1K/day streaks (PRO only)
  streak_1k_current INTEGER DEFAULT 0,
  streak_1k_last_date DATE,
  streak_1k_longest INTEGER DEFAULT 0,
  streak_1k_3_count INTEGER DEFAULT 0,
  streak_1k_7_count INTEGER DEFAULT 0,
  streak_1k_14_count INTEGER DEFAULT 0,
  streak_1k_30_count INTEGER DEFAULT 0,
  streak_1k_30_first_at TIMESTAMPTZ,
  
  -- Featured Writer
  featured_eligible BOOLEAN DEFAULT FALSE,
  featured_eligible_at TIMESTAMPTZ,
  featured_writer BOOLEAN DEFAULT FALSE,
  featured_writer_since TIMESTAMPTZ,
  featured_piece_url TEXT,
  
  -- Voice Profile (save consent)
  save_enabled BOOLEAN DEFAULT FALSE,
  save_enabled_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_user_milestones_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_milestones_updated
  BEFORE UPDATE ON user_milestones
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- DAILY KEYSTROKE TOTALS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS daily_keystroke_totals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  keystroke_words INTEGER DEFAULT 0,
  analyses_count INTEGER DEFAULT 0,
  
  -- Milestones triggered this day
  milestones_triggered TEXT[] DEFAULT '{}',
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id, date)
);

CREATE INDEX idx_daily_keystroke_user_date ON daily_keystroke_totals(user_id, date);

-- Trigger to update updated_at
CREATE TRIGGER daily_keystroke_totals_updated
  BEFORE UPDATE ON daily_keystroke_totals
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- MILESTONE EVENTS (Audit log)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS milestone_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  milestone_type TEXT NOT NULL,
  keystroke_words INTEGER NOT NULL,
  streak_days INTEGER,
  triggered_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Context
  session_id TEXT,
  source TEXT  -- 'web', 'extension', etc.
);

CREATE INDEX idx_milestone_events_user ON milestone_events(user_id, triggered_at DESC);
CREATE INDEX idx_milestone_events_type ON milestone_events(milestone_type);


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED WRITER SUBMISSIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS featured_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Submission content
  text TEXT NOT NULL,
  word_count INTEGER NOT NULL,
  keystroke_verified BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Agreements
  agreement_accepted_at TIMESTAMPTZ NOT NULL,
  agreement_original BOOLEAN NOT NULL DEFAULT FALSE,
  agreement_no_compensation BOOLEAN NOT NULL DEFAULT FALSE,
  agreement_grant_permission BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Review status
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
  reviewed_at TIMESTAMPTZ,
  reviewer_id UUID,
  reviewer_notes TEXT,  -- Internal only
  
  -- If accepted, the published URL
  published_url TEXT,
  published_at TIMESTAMPTZ,
  
  -- Timestamps
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_featured_submissions_user ON featured_submissions(user_id);
CREATE INDEX idx_featured_submissions_status ON featured_submissions(status);

-- Trigger to update updated_at
CREATE TRIGGER featured_submissions_updated
  BEFORE UPDATE ON featured_submissions
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED WRITERS (Published)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS featured_writers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  submission_id UUID REFERENCES featured_submissions(id),
  
  -- Profile info
  display_name TEXT,
  profile_type TEXT,
  profile_stance TEXT,
  
  -- Featured piece
  piece_title TEXT,
  piece_excerpt TEXT,  -- First ~100 words for preview
  piece_url TEXT NOT NULL,
  
  -- Stats at time of featuring
  lifetime_words_at_featuring INTEGER,
  
  -- Timestamps
  featured_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ordering
  display_order INTEGER DEFAULT 0
);

CREATE INDEX idx_featured_writers_order ON featured_writers(display_order, featured_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE user_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_keystroke_totals ENABLE ROW LEVEL SECURITY;
ALTER TABLE milestone_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE featured_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE featured_writers ENABLE ROW LEVEL SECURITY;

-- Users can view/update their own milestones
CREATE POLICY "Users can view own milestones" ON user_milestones
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own milestones" ON user_milestones
  FOR UPDATE USING (auth.uid() = user_id);

-- Users can view/update their own daily totals
CREATE POLICY "Users can view own daily totals" ON daily_keystroke_totals
  FOR ALL USING (auth.uid() = user_id);

-- Users can view their own milestone events
CREATE POLICY "Users can view own milestone events" ON milestone_events
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view/create their own submissions
CREATE POLICY "Users can view own submissions" ON featured_submissions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create submissions" ON featured_submissions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Featured writers are public
CREATE POLICY "Featured writers are public" ON featured_writers
  FOR SELECT USING (true);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to record keystroke words and check milestones
CREATE OR REPLACE FUNCTION record_keystroke_words(
  p_user_id UUID,
  p_word_count INTEGER,
  p_tier TEXT,
  p_session_id TEXT DEFAULT NULL,
  p_source TEXT DEFAULT 'web'
)
RETURNS TABLE (
  milestone_type TEXT,
  keystroke_words INTEGER,
  streak_days INTEGER
) AS $$
DECLARE
  v_state user_milestones%ROWTYPE;
  v_today DATE := CURRENT_DATE;
  v_daily_total INTEGER;
  v_prev_daily INTEGER;
BEGIN
  -- Get or create user milestone state
  INSERT INTO user_milestones (user_id)
  VALUES (p_user_id)
  ON CONFLICT (user_id) DO NOTHING;
  
  SELECT * INTO v_state FROM user_milestones WHERE user_id = p_user_id;
  
  -- Check if save is enabled
  IF NOT v_state.save_enabled THEN
    RETURN;
  END IF;
  
  -- Update lifetime total
  UPDATE user_milestones 
  SET lifetime_keystroke_words = lifetime_keystroke_words + p_word_count
  WHERE user_id = p_user_id
  RETURNING * INTO v_state;
  
  -- Get/update daily total
  INSERT INTO daily_keystroke_totals (user_id, date, keystroke_words, analyses_count)
  VALUES (p_user_id, v_today, p_word_count, 1)
  ON CONFLICT (user_id, date) DO UPDATE
  SET keystroke_words = daily_keystroke_totals.keystroke_words + p_word_count,
      analyses_count = daily_keystroke_totals.analyses_count + 1
  RETURNING keystroke_words INTO v_daily_total;
  
  v_prev_daily := v_daily_total - p_word_count;
  
  -- Check FIRST 500
  IF NOT v_state.first_500_achieved AND v_state.lifetime_keystroke_words >= 500 THEN
    UPDATE user_milestones 
    SET first_500_achieved = TRUE, first_500_achieved_at = NOW()
    WHERE user_id = p_user_id;
    
    INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, session_id, source)
    VALUES (p_user_id, 'first_500', v_state.lifetime_keystroke_words, p_session_id, p_source);
    
    RETURN QUERY SELECT 'first_500'::TEXT, v_state.lifetime_keystroke_words, NULL::INTEGER;
  END IF;
  
  -- Check 500/day streak
  IF v_daily_total >= 500 THEN
    IF v_state.streak_500_last_date = v_today THEN
      -- Already counted today
      NULL;
    ELSIF v_state.streak_500_last_date = v_today - 1 THEN
      -- Extend streak
      UPDATE user_milestones 
      SET streak_500_current = streak_500_current + 1,
          streak_500_last_date = v_today
      WHERE user_id = p_user_id
      RETURNING * INTO v_state;
    ELSE
      -- Reset streak
      UPDATE user_milestones 
      SET streak_500_current = 1,
          streak_500_last_date = v_today
      WHERE user_id = p_user_id
      RETURNING * INTO v_state;
    END IF;
    
    -- Check for 3-day milestone
    IF v_state.streak_500_current = 3 THEN
      UPDATE user_milestones SET streak_500_3_count = streak_500_3_count + 1 WHERE user_id = p_user_id;
      
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, streak_days, session_id, source)
      VALUES (p_user_id, 'streak_3_day', v_state.lifetime_keystroke_words, 3, p_session_id, p_source);
      
      RETURN QUERY SELECT 'streak_3_day'::TEXT, v_state.lifetime_keystroke_words, 3;
    END IF;
  END IF;
  
  -- PRO-only: Check 1K milestones
  IF p_tier = 'pro' AND v_daily_total >= 1000 THEN
    -- Daily 1K (first time today)
    IF v_prev_daily < 1000 THEN
      UPDATE user_milestones SET daily_1k_count = daily_1k_count + 1 WHERE user_id = p_user_id;
      
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, session_id, source)
      VALUES (p_user_id, 'daily_1k', v_daily_total, p_session_id, p_source);
      
      RETURN QUERY SELECT 'daily_1k'::TEXT, v_daily_total, NULL::INTEGER;
    END IF;
    
    -- Update 1K streak
    IF v_state.streak_1k_last_date = v_today THEN
      NULL;
    ELSIF v_state.streak_1k_last_date = v_today - 1 THEN
      UPDATE user_milestones 
      SET streak_1k_current = streak_1k_current + 1,
          streak_1k_last_date = v_today,
          streak_1k_longest = GREATEST(streak_1k_longest, streak_1k_current + 1)
      WHERE user_id = p_user_id
      RETURNING * INTO v_state;
    ELSE
      UPDATE user_milestones 
      SET streak_1k_current = 1,
          streak_1k_last_date = v_today
      WHERE user_id = p_user_id
      RETURNING * INTO v_state;
    END IF;
    
    -- Check 1K streak milestones
    IF v_state.streak_1k_current = 3 THEN
      UPDATE user_milestones SET streak_1k_3_count = streak_1k_3_count + 1 WHERE user_id = p_user_id;
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, streak_days, session_id, source)
      VALUES (p_user_id, 'streak_3_day_1k', v_state.lifetime_keystroke_words, 3, p_session_id, p_source);
      RETURN QUERY SELECT 'streak_3_day_1k'::TEXT, v_state.lifetime_keystroke_words, 3;
    END IF;
    
    IF v_state.streak_1k_current = 7 THEN
      UPDATE user_milestones 
      SET streak_1k_7_count = streak_1k_7_count + 1,
          featured_eligible = TRUE,
          featured_eligible_at = NOW()
      WHERE user_id = p_user_id;
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, streak_days, session_id, source)
      VALUES (p_user_id, 'streak_7_day_1k', v_state.lifetime_keystroke_words, 7, p_session_id, p_source);
      RETURN QUERY SELECT 'streak_7_day_1k'::TEXT, v_state.lifetime_keystroke_words, 7;
    END IF;
    
    IF v_state.streak_1k_current = 14 THEN
      UPDATE user_milestones SET streak_1k_14_count = streak_1k_14_count + 1 WHERE user_id = p_user_id;
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, streak_days, session_id, source)
      VALUES (p_user_id, 'streak_14_day_1k', v_state.lifetime_keystroke_words, 14, p_session_id, p_source);
      RETURN QUERY SELECT 'streak_14_day_1k'::TEXT, v_state.lifetime_keystroke_words, 14;
    END IF;
    
    IF v_state.streak_1k_current = 30 THEN
      UPDATE user_milestones 
      SET streak_1k_30_count = streak_1k_30_count + 1,
          streak_1k_30_first_at = COALESCE(streak_1k_30_first_at, NOW())
      WHERE user_id = p_user_id;
      INSERT INTO milestone_events (user_id, milestone_type, keystroke_words, streak_days, session_id, source)
      VALUES (p_user_id, 'streak_30_day_1k', v_state.lifetime_keystroke_words, 30, p_session_id, p_source);
      RETURN QUERY SELECT 'streak_30_day_1k'::TEXT, v_state.lifetime_keystroke_words, 30;
    END IF;
  END IF;
  
  RETURN;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Public profile view (for /writer/:username pages)
CREATE OR REPLACE VIEW public_writer_profiles AS
SELECT 
  u.id,
  u.display_name,
  um.lifetime_keystroke_words,
  um.first_500_achieved,
  um.streak_500_3_count,
  um.daily_1k_count,
  um.streak_1k_3_count,
  um.streak_1k_7_count,
  um.streak_1k_14_count,
  um.streak_1k_30_count,
  um.featured_writer,
  um.featured_writer_since,
  um.featured_piece_url,
  fw.piece_title,
  fw.piece_excerpt
FROM users u
JOIN user_milestones um ON u.id = um.user_id
LEFT JOIN featured_writers fw ON u.id = fw.user_id
WHERE um.save_enabled = TRUE;  -- Only show users who opted in
