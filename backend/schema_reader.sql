-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY READER FUNNEL DATABASE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Tracks reader behavior and computes reading taste profiles.
-- 
-- Tables:
-- - reader_events: Raw behavioral events
-- - reader_profile: Computed taste profile
-- 
-- Run after: schema_milestones.sql

-- ═══════════════════════════════════════════════════════════════════════════
-- READER EVENTS (Raw behavioral data)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS reader_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- User identification (one of these required)
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id TEXT,  -- For anonymous visitors
  
  -- Event details
  event_type TEXT NOT NULL CHECK (event_type IN (
    'page_view',      -- Viewed a reading post
    'read_complete',  -- Scrolled to bottom / spent sufficient time
    'click_writer',   -- Clicked on a writer link
    'click_book',     -- Clicked on a book affiliate link
    'click_featured', -- Clicked on Featured Writer piece
    'bookmark',       -- Saved/bookmarked content
    'dismiss',        -- "Not for me" action
    'more_like_this'  -- Clicked "More like this"
  )),
  
  -- Content context
  profile_type TEXT NOT NULL,  -- ASSERTIVE, MINIMAL, etc.
  profile_stance TEXT NOT NULL, -- OPEN, CLOSED, BALANCED, CONTRADICTORY
  profile_id TEXT GENERATED ALWAYS AS (profile_type || '-' || profile_stance) STORED,
  
  content_type TEXT NOT NULL CHECK (content_type IN (
    'reading_post',   -- /blog/reading/{profile}
    'writing_post',   -- /blog/writing/{profile}
    'featured_piece', -- Featured Writer article
    'book',           -- Book recommendation
    'writer'          -- Famous writer page/link
  )),
  
  content_id TEXT,  -- Specific book ISBN, writer slug, etc.
  
  -- Engagement metrics
  time_on_page_seconds INTEGER,
  scroll_depth_percent INTEGER CHECK (scroll_depth_percent BETWEEN 0 AND 100),
  
  -- Affiliate tracking
  affiliate_partner TEXT,  -- 'indigo_ca', 'bookshop_uk', etc.
  affiliate_clicked BOOLEAN DEFAULT FALSE,
  
  -- Context
  referrer TEXT,
  user_agent TEXT,
  country_code TEXT,  -- CA, UK, AU, NZ, US, etc.
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_reader_events_user ON reader_events(user_id, created_at DESC) WHERE user_id IS NOT NULL;
CREATE INDEX idx_reader_events_session ON reader_events(session_id, created_at DESC) WHERE session_id IS NOT NULL;
CREATE INDEX idx_reader_events_profile ON reader_events(profile_id, event_type);
CREATE INDEX idx_reader_events_type ON reader_events(event_type, created_at DESC);
CREATE INDEX idx_reader_events_content ON reader_events(content_type, content_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- READER PROFILE (Computed taste preferences)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS reader_profile (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Inferred taste (dominant profile)
  inferred_profile_type TEXT,
  inferred_profile_stance TEXT,
  inferred_profile_id TEXT,
  inferred_confidence DECIMAL(3, 2),  -- 0.00 to 1.00
  
  -- Ranked preferences (JSONB arrays)
  -- e.g., ["ASSERTIVE", "CONVERSATIONAL", "POETIC"]
  top_types JSONB DEFAULT '[]',
  
  -- e.g., ["OPEN", "BALANCED", "CLOSED"]
  top_stances JSONB DEFAULT '[]',
  
  -- Full profile scores (for recommendations)
  -- e.g., {"ASSERTIVE-OPEN": 0.85, "CONVERSATIONAL-OPEN": 0.72, ...}
  profile_scores JSONB DEFAULT '{}',
  
  -- Engagement stats
  total_reading_posts_viewed INTEGER DEFAULT 0,
  total_books_clicked INTEGER DEFAULT 0,
  total_writers_clicked INTEGER DEFAULT 0,
  total_featured_clicked INTEGER DEFAULT 0,
  total_bookmarks INTEGER DEFAULT 0,
  
  -- Affiliate engagement
  preferred_affiliate_partner TEXT,
  
  -- Reading vs Writing comparison
  writing_profile_id TEXT,  -- From their writing analysis (if exists)
  taste_matches_voice BOOLEAN,  -- Do they read what they write?
  
  -- Computation metadata
  events_processed INTEGER DEFAULT 0,
  last_computed_at TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger for updated_at
CREATE TRIGGER reader_profile_updated
  BEFORE UPDATE ON reader_profile
  FOR EACH ROW
  EXECUTE FUNCTION update_user_milestones_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- READER BOOKMARKS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS reader_bookmarks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- What was bookmarked
  content_type TEXT NOT NULL CHECK (content_type IN (
    'reading_post', 'writing_post', 'featured_piece', 'book', 'writer'
  )),
  content_id TEXT NOT NULL,  -- profile_id, ISBN, writer slug, etc.
  
  -- Context
  profile_id TEXT,  -- Associated profile if applicable
  title TEXT,
  url TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id, content_type, content_id)
);

CREATE INDEX idx_reader_bookmarks_user ON reader_bookmarks(user_id, created_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE reader_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE reader_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE reader_bookmarks ENABLE ROW LEVEL SECURITY;

-- Users can insert their own events
CREATE POLICY "Users can insert own events" ON reader_events
  FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Users can view their own events
CREATE POLICY "Users can view own events" ON reader_events
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view/update their own profile
CREATE POLICY "Users can view own reader profile" ON reader_profile
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own reader profile" ON reader_profile
  FOR UPDATE USING (auth.uid() = user_id);

-- Users can manage their own bookmarks
CREATE POLICY "Users can manage own bookmarks" ON reader_bookmarks
  FOR ALL USING (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Record a reader event
CREATE OR REPLACE FUNCTION record_reader_event(
  p_user_id UUID,
  p_session_id TEXT,
  p_event_type TEXT,
  p_profile_type TEXT,
  p_profile_stance TEXT,
  p_content_type TEXT,
  p_content_id TEXT DEFAULT NULL,
  p_time_on_page INTEGER DEFAULT NULL,
  p_scroll_depth INTEGER DEFAULT NULL,
  p_affiliate_partner TEXT DEFAULT NULL,
  p_country_code TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_event_id UUID;
BEGIN
  INSERT INTO reader_events (
    user_id, session_id, event_type,
    profile_type, profile_stance, content_type, content_id,
    time_on_page_seconds, scroll_depth_percent,
    affiliate_partner, affiliate_clicked, country_code
  ) VALUES (
    p_user_id, p_session_id, p_event_type,
    p_profile_type, p_profile_stance, p_content_type, p_content_id,
    p_time_on_page, p_scroll_depth,
    p_affiliate_partner, (p_affiliate_partner IS NOT NULL), p_country_code
  )
  RETURNING id INTO v_event_id;
  
  RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;


-- Compute/update reader profile from events
CREATE OR REPLACE FUNCTION compute_reader_profile(p_user_id UUID)
RETURNS void AS $$
DECLARE
  v_type_scores JSONB;
  v_stance_scores JSONB;
  v_profile_scores JSONB;
  v_top_type TEXT;
  v_top_stance TEXT;
  v_confidence DECIMAL;
  v_total_events INTEGER;
BEGIN
  -- Calculate type scores (weighted by engagement)
  WITH type_engagement AS (
    SELECT 
      profile_type,
      SUM(CASE event_type
        WHEN 'read_complete' THEN 3
        WHEN 'bookmark' THEN 5
        WHEN 'more_like_this' THEN 4
        WHEN 'click_book' THEN 2
        WHEN 'click_writer' THEN 2
        WHEN 'click_featured' THEN 3
        WHEN 'page_view' THEN 1
        WHEN 'dismiss' THEN -3
        ELSE 0
      END) as score
    FROM reader_events
    WHERE user_id = p_user_id
    GROUP BY profile_type
  )
  SELECT 
    jsonb_object_agg(profile_type, score),
    (SELECT profile_type FROM type_engagement ORDER BY score DESC LIMIT 1)
  INTO v_type_scores, v_top_type
  FROM type_engagement;
  
  -- Calculate stance scores
  WITH stance_engagement AS (
    SELECT 
      profile_stance,
      SUM(CASE event_type
        WHEN 'read_complete' THEN 3
        WHEN 'bookmark' THEN 5
        WHEN 'more_like_this' THEN 4
        WHEN 'click_book' THEN 2
        WHEN 'click_writer' THEN 2
        WHEN 'click_featured' THEN 3
        WHEN 'page_view' THEN 1
        WHEN 'dismiss' THEN -3
        ELSE 0
      END) as score
    FROM reader_events
    WHERE user_id = p_user_id
    GROUP BY profile_stance
  )
  SELECT 
    jsonb_object_agg(profile_stance, score),
    (SELECT profile_stance FROM stance_engagement ORDER BY score DESC LIMIT 1)
  INTO v_stance_scores, v_top_stance
  FROM stance_engagement;
  
  -- Calculate full profile scores
  WITH profile_engagement AS (
    SELECT 
      profile_id,
      SUM(CASE event_type
        WHEN 'read_complete' THEN 3
        WHEN 'bookmark' THEN 5
        WHEN 'more_like_this' THEN 4
        WHEN 'click_book' THEN 2
        WHEN 'click_writer' THEN 2
        WHEN 'click_featured' THEN 3
        WHEN 'page_view' THEN 1
        WHEN 'dismiss' THEN -3
        ELSE 0
      END) as score
    FROM reader_events
    WHERE user_id = p_user_id
    GROUP BY profile_id
  )
  SELECT jsonb_object_agg(profile_id, score)
  INTO v_profile_scores
  FROM profile_engagement;
  
  -- Count total events
  SELECT COUNT(*) INTO v_total_events
  FROM reader_events WHERE user_id = p_user_id;
  
  -- Calculate confidence based on event count
  v_confidence := LEAST(1.0, v_total_events::DECIMAL / 20.0);
  
  -- Upsert reader profile
  INSERT INTO reader_profile (
    user_id,
    inferred_profile_type, inferred_profile_stance, inferred_profile_id, inferred_confidence,
    top_types, top_stances, profile_scores,
    events_processed, last_computed_at
  ) VALUES (
    p_user_id,
    v_top_type, v_top_stance, v_top_type || '-' || v_top_stance, v_confidence,
    (SELECT jsonb_agg(profile_type ORDER BY score DESC) FROM (SELECT * FROM jsonb_each_text(v_type_scores) AS x(profile_type, score)) t),
    (SELECT jsonb_agg(profile_stance ORDER BY score DESC) FROM (SELECT * FROM jsonb_each_text(v_stance_scores) AS x(profile_stance, score)) t),
    v_profile_scores,
    v_total_events, NOW()
  )
  ON CONFLICT (user_id) DO UPDATE SET
    inferred_profile_type = EXCLUDED.inferred_profile_type,
    inferred_profile_stance = EXCLUDED.inferred_profile_stance,
    inferred_profile_id = EXCLUDED.inferred_profile_id,
    inferred_confidence = EXCLUDED.inferred_confidence,
    top_types = EXCLUDED.top_types,
    top_stances = EXCLUDED.top_stances,
    profile_scores = EXCLUDED.profile_scores,
    events_processed = EXCLUDED.events_processed,
    last_computed_at = NOW();
    
END;
$$ LANGUAGE plpgsql;


-- Get reading recommendations for a user
CREATE OR REPLACE FUNCTION get_reading_recommendations(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
  profile_id TEXT,
  score DECIMAL,
  reason TEXT
) AS $$
BEGIN
  RETURN QUERY
  WITH user_scores AS (
    SELECT 
      key as profile_id,
      value::DECIMAL as score
    FROM reader_profile rp,
         jsonb_each_text(rp.profile_scores)
    WHERE rp.user_id = p_user_id
  ),
  all_profiles AS (
    SELECT unnest(ARRAY[
      'ASSERTIVE-OPEN', 'ASSERTIVE-CLOSED', 'ASSERTIVE-BALANCED', 'ASSERTIVE-CONTRADICTORY',
      'MINIMAL-OPEN', 'MINIMAL-CLOSED', 'MINIMAL-BALANCED', 'MINIMAL-CONTRADICTORY',
      'POETIC-OPEN', 'POETIC-CLOSED', 'POETIC-BALANCED', 'POETIC-CONTRADICTORY',
      'DENSE-OPEN', 'DENSE-CLOSED', 'DENSE-BALANCED', 'DENSE-CONTRADICTORY',
      'CONVERSATIONAL-OPEN', 'CONVERSATIONAL-CLOSED', 'CONVERSATIONAL-BALANCED', 'CONVERSATIONAL-CONTRADICTORY',
      'FORMAL-OPEN', 'FORMAL-CLOSED', 'FORMAL-BALANCED', 'FORMAL-CONTRADICTORY',
      'BALANCED-OPEN', 'BALANCED-CLOSED', 'BALANCED-BALANCED', 'BALANCED-CONTRADICTORY',
      'LONGFORM-OPEN', 'LONGFORM-CLOSED', 'LONGFORM-BALANCED', 'LONGFORM-CONTRADICTORY',
      'INTERROGATIVE-OPEN', 'INTERROGATIVE-CLOSED', 'INTERROGATIVE-BALANCED', 'INTERROGATIVE-CONTRADICTORY',
      'HEDGED-OPEN', 'HEDGED-CLOSED', 'HEDGED-BALANCED', 'HEDGED-CONTRADICTORY'
    ]) as profile_id
  ),
  not_yet_explored AS (
    SELECT ap.profile_id
    FROM all_profiles ap
    LEFT JOIN user_scores us ON ap.profile_id = us.profile_id
    WHERE us.profile_id IS NULL
  )
  -- Recommend: similar profiles (high scores) + unexplored with matching stance
  SELECT 
    us.profile_id,
    us.score,
    'Based on your reading taste'::TEXT as reason
  FROM user_scores us
  WHERE us.score > 0
  ORDER BY us.score DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Reader taste summary (for dashboard)
CREATE OR REPLACE VIEW reader_taste_summary AS
SELECT 
  rp.user_id,
  rp.inferred_profile_id as reading_taste,
  rp.inferred_confidence as confidence,
  rp.top_types,
  rp.top_stances,
  rp.total_reading_posts_viewed,
  rp.total_books_clicked,
  rp.total_bookmarks,
  um.first_500_achieved as has_written,
  CASE 
    WHEN um.lifetime_keystroke_words > 0 THEN 
      (SELECT profile_id FROM analyses WHERE user_id = rp.user_id ORDER BY created_at DESC LIMIT 1)
    ELSE NULL
  END as writing_voice,
  rp.inferred_profile_id != (
    SELECT profile_id FROM analyses WHERE user_id = rp.user_id ORDER BY created_at DESC LIMIT 1
  ) as taste_differs_from_voice
FROM reader_profile rp
LEFT JOIN user_milestones um ON rp.user_id = um.user_id;
