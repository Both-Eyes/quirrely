-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY PUBLIC PROFILES DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Public profiles, usernames, and showcase pages.
-- URL: /@username
-- Privacy: Private by default

-- ═══════════════════════════════════════════════════════════════════════════
-- USERNAMES
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS usernames (
  username TEXT PRIMARY KEY,  -- Stored lowercase
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Original casing
  display_username TEXT NOT NULL,
  
  -- History
  claimed_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id)  -- One username per user
);

CREATE INDEX idx_usernames_user ON usernames(user_id);


-- Username history (for preventing re-use)
CREATE TABLE IF NOT EXISTS username_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  username TEXT NOT NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  claimed_at TIMESTAMPTZ NOT NULL,
  released_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_username_history_username ON username_history(username);


-- Reserved usernames
CREATE TABLE IF NOT EXISTS reserved_usernames (
  username TEXT PRIMARY KEY,
  reason TEXT,
  reserved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert reserved usernames
INSERT INTO reserved_usernames (username, reason) VALUES
  ('quirrely', 'brand'),
  ('admin', 'system'),
  ('support', 'system'),
  ('help', 'system'),
  ('featured', 'feature'),
  ('authority', 'feature'),
  ('settings', 'page'),
  ('dashboard', 'page'),
  ('api', 'system')
ON CONFLICT (username) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- PUBLIC PROFILES
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public_profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Basic info
  display_name TEXT,
  bio TEXT CHECK (LENGTH(bio) <= 160),
  avatar_url TEXT,
  
  -- Visibility
  visibility TEXT NOT NULL DEFAULT 'private' 
    CHECK (visibility IN ('private', 'featured_only', 'public')),
  
  -- Sharing settings
  share_voice BOOLEAN DEFAULT FALSE,
  share_taste BOOLEAN DEFAULT FALSE,
  
  -- Cached voice profile (for display)
  voice_profile_type TEXT,
  voice_stance TEXT,
  voice_traits TEXT[],
  
  -- Cached reading taste (for display)
  reading_taste_type TEXT,
  
  -- Recognition status
  is_featured_writer BOOLEAN DEFAULT FALSE,
  is_featured_curator BOOLEAN DEFAULT FALSE,
  is_authority_writer BOOLEAN DEFAULT FALSE,
  is_authority_curator BOOLEAN DEFAULT FALSE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- PROFILE VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS profile_views (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  profile_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Viewer (null for anonymous)
  viewer_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Context
  referrer TEXT,
  
  -- Timestamp
  viewed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profile_views_profile ON profile_views(profile_user_id, viewed_at DESC);
CREATE INDEX idx_profile_views_date ON profile_views(DATE(viewed_at));


-- Daily view counts (for analytics)
CREATE TABLE IF NOT EXISTS profile_view_counts (
  profile_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  view_date DATE NOT NULL,
  view_count INTEGER DEFAULT 0,
  
  PRIMARY KEY (profile_user_id, view_date)
);


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED PIECES (Writer's showcase)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS profile_featured_pieces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Piece info
  title TEXT NOT NULL,
  preview TEXT,  -- First ~200 chars
  word_count INTEGER,
  voice_profile_type TEXT,
  
  -- Reference to original submission
  submission_id UUID REFERENCES featured_submissions(id),
  
  -- Order
  display_order INTEGER DEFAULT 0,
  
  -- Timestamps
  featured_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_featured_pieces_user ON profile_featured_pieces(user_id, display_order);


-- ═══════════════════════════════════════════════════════════════════════════
-- CURATED PATHS (Curator's showcase)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS profile_curated_paths (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Path info
  title TEXT NOT NULL,
  description TEXT,
  post_count INTEGER DEFAULT 0,
  
  -- Stats
  follow_count INTEGER DEFAULT 0,
  
  -- Order
  display_order INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_curated_paths_user ON profile_curated_paths(user_id, display_order);


-- Path follows
CREATE TABLE IF NOT EXISTS path_follows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  path_id UUID NOT NULL REFERENCES profile_curated_paths(id) ON DELETE CASCADE,
  follower_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  followed_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(path_id, follower_user_id)
);

CREATE INDEX idx_path_follows_path ON path_follows(path_id);
CREATE INDEX idx_path_follows_user ON path_follows(follower_user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Check if username is available
CREATE OR REPLACE FUNCTION is_username_available(p_username TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN NOT EXISTS (
    SELECT 1 FROM usernames WHERE username = LOWER(p_username)
  ) AND NOT EXISTS (
    SELECT 1 FROM reserved_usernames WHERE username = LOWER(p_username)
  );
END;
$$ LANGUAGE plpgsql;


-- Claim username
CREATE OR REPLACE FUNCTION claim_username(
  p_user_id UUID,
  p_username TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  v_old_username TEXT;
BEGIN
  -- Check availability
  IF NOT is_username_available(p_username) THEN
    RETURN FALSE;
  END IF;
  
  -- Get old username if exists
  SELECT username INTO v_old_username FROM usernames WHERE user_id = p_user_id;
  
  -- Release old username
  IF v_old_username IS NOT NULL THEN
    INSERT INTO username_history (username, user_id, claimed_at)
    SELECT username, user_id, claimed_at FROM usernames WHERE user_id = p_user_id;
    
    DELETE FROM usernames WHERE user_id = p_user_id;
  END IF;
  
  -- Claim new username
  INSERT INTO usernames (username, user_id, display_username)
  VALUES (LOWER(p_username), p_user_id, p_username);
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Get profile by username
CREATE OR REPLACE FUNCTION get_public_profile(p_username TEXT)
RETURNS TABLE (
  user_id UUID,
  username TEXT,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  visibility TEXT,
  share_voice BOOLEAN,
  share_taste BOOLEAN,
  voice_profile_type TEXT,
  voice_stance TEXT,
  reading_taste_type TEXT,
  is_featured_writer BOOLEAN,
  is_featured_curator BOOLEAN,
  is_authority_writer BOOLEAN,
  is_authority_curator BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    u.user_id,
    un.display_username,
    p.display_name,
    p.bio,
    p.avatar_url,
    p.visibility,
    p.share_voice,
    p.share_taste,
    p.voice_profile_type,
    p.voice_stance,
    p.reading_taste_type,
    p.is_featured_writer,
    p.is_featured_curator,
    p.is_authority_writer,
    p.is_authority_curator
  FROM usernames un
  JOIN public_profiles p ON un.user_id = p.user_id
  WHERE un.username = LOWER(p_username);
END;
$$ LANGUAGE plpgsql;


-- Record profile view
CREATE OR REPLACE FUNCTION record_profile_view(
  p_profile_user_id UUID,
  p_viewer_user_id UUID DEFAULT NULL,
  p_referrer TEXT DEFAULT NULL
)
RETURNS void AS $$
BEGIN
  -- Don't record self-views
  IF p_viewer_user_id = p_profile_user_id THEN
    RETURN;
  END IF;
  
  -- Insert view
  INSERT INTO profile_views (profile_user_id, viewer_user_id, referrer)
  VALUES (p_profile_user_id, p_viewer_user_id, p_referrer);
  
  -- Update daily count
  INSERT INTO profile_view_counts (profile_user_id, view_date, view_count)
  VALUES (p_profile_user_id, CURRENT_DATE, 1)
  ON CONFLICT (profile_user_id, view_date) DO UPDATE
  SET view_count = profile_view_counts.view_count + 1;
END;
$$ LANGUAGE plpgsql;


-- Get profile view count
CREATE OR REPLACE FUNCTION get_profile_view_count(
  p_user_id UUID,
  p_days INTEGER DEFAULT 30
)
RETURNS INTEGER AS $$
BEGIN
  RETURN COALESCE((
    SELECT SUM(view_count)
    FROM profile_view_counts
    WHERE profile_user_id = p_user_id
      AND view_date > CURRENT_DATE - p_days
  ), 0);
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Featured Writers for showcase
CREATE OR REPLACE VIEW featured_writers_showcase AS
SELECT 
  un.display_username as username,
  p.display_name,
  p.avatar_url,
  p.voice_profile_type,
  p.is_authority_writer,
  get_profile_view_count(p.user_id, 30) as views_30d
FROM public_profiles p
JOIN usernames un ON p.user_id = un.user_id
WHERE p.is_featured_writer = TRUE
  AND p.visibility IN ('public', 'featured_only')
ORDER BY p.is_authority_writer DESC, views_30d DESC;


-- Featured Curators for showcase
CREATE OR REPLACE VIEW featured_curators_showcase AS
SELECT 
  un.display_username as username,
  p.display_name,
  p.avatar_url,
  p.reading_taste_type,
  p.is_authority_curator,
  (SELECT COUNT(*) FROM path_follows pf 
   JOIN profile_curated_paths cp ON pf.path_id = cp.id 
   WHERE cp.user_id = p.user_id) as total_follows
FROM public_profiles p
JOIN usernames un ON p.user_id = un.user_id
WHERE p.is_featured_curator = TRUE
  AND p.visibility IN ('public', 'featured_only')
ORDER BY p.is_authority_curator DESC, total_follows DESC;


-- Authority members
CREATE OR REPLACE VIEW authority_members_showcase AS
SELECT 
  un.display_username as username,
  p.display_name,
  p.avatar_url,
  p.is_authority_writer,
  p.is_authority_curator,
  CASE 
    WHEN p.is_authority_writer AND p.is_authority_curator THEN 'voice_and_taste'
    WHEN p.is_authority_writer THEN 'writer'
    ELSE 'curator'
  END as authority_type
FROM public_profiles p
JOIN usernames un ON p.user_id = un.user_id
WHERE (p.is_authority_writer = TRUE OR p.is_authority_curator = TRUE)
  AND p.visibility IN ('public', 'featured_only')
ORDER BY 
  CASE WHEN p.is_authority_writer AND p.is_authority_curator THEN 0 ELSE 1 END,
  un.display_username;


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE public_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE usernames ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_featured_pieces ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_curated_paths ENABLE ROW LEVEL SECURITY;

-- Users can manage their own profiles
CREATE POLICY "Users manage own profile" ON public_profiles
  FOR ALL USING (auth.uid() = user_id);

-- Anyone can view public profiles
CREATE POLICY "Public profiles viewable" ON public_profiles
  FOR SELECT USING (visibility = 'public');

-- Featured profiles viewable on showcase
CREATE POLICY "Featured profiles on showcase" ON public_profiles
  FOR SELECT USING (
    visibility = 'featured_only' 
    AND (is_featured_writer OR is_featured_curator)
  );

-- Users manage own username
CREATE POLICY "Users manage own username" ON usernames
  FOR ALL USING (auth.uid() = user_id);

-- Usernames publicly viewable
CREATE POLICY "Usernames viewable" ON usernames
  FOR SELECT USING (TRUE);

-- Users manage own featured pieces
CREATE POLICY "Users manage own pieces" ON profile_featured_pieces
  FOR ALL USING (auth.uid() = user_id);

-- Users manage own paths
CREATE POLICY "Users manage own paths" ON profile_curated_paths
  FOR ALL USING (auth.uid() = user_id);
