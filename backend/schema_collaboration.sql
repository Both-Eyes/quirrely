-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY COLLABORATION SYSTEM SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Enables Pro tier users to:
-- 1. Pair with another Pro user for shared writing projects
-- 2. Pool half their monthly word allowances (25k + 25k = 50k shared)
-- 3. Maintain individual word allowances for solo work
-- 4. Collaborate on categorized projects (business, creative, personal, etc.)
-- 5. Submit for Featured Collaboration recognition
-- 6. Connect via existing compare feature → auth → upgrade → collaborate
--
-- Security: One collaboration per user at a time, secure invitation system
-- ═══════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════
-- ENUMS
-- ═══════════════════════════════════════════════════════════════════════════

-- Partnership types reflecting real-life contexts for women writers
DO $$ BEGIN
  CREATE TYPE partnership_type AS ENUM (
    'heart',              -- Life's most meaningful moments (weddings, eulogies, family stories)
    'growth',             -- Supporting each other's journey (mentorship, accountability)
    'professional',       -- Authentic voice at work (presentations, proposals)
    'creative',           -- Playing with possibilities (fiction, poetry, blogs)
    'life'                -- Getting important things done (planning, organizing, legacy)
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Collaboration invitation status
DO $$ BEGIN
  CREATE TYPE collaboration_status AS ENUM (
    'pending',            -- Invitation sent, awaiting response
    'active',             -- Both users accepted, collaboration is live
    'completed',          -- Project finished by mutual agreement
    'cancelled',          -- Cancelled by either party
    'expired'             -- Invitation expired without acceptance
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Featured submission status
DO $$ BEGIN
  CREATE TYPE featured_collab_status AS ENUM (
    'draft',              -- Being prepared for submission
    'submitted',          -- Submitted for review
    'under_review',       -- Being reviewed by team
    'approved',           -- Approved as Featured Collaboration
    'featured',           -- Currently featured on site
    'archived',           -- No longer featured but remains approved
    'rejected'            -- Submission rejected
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- COLLABORATIONS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE writing_partnerships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Partners (Pro tier required)
  initiator_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  partner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Partnership details
  partnership_name VARCHAR(200) NOT NULL,
  partnership_intention TEXT,  -- What they hope to create together
  partnership_type partnership_type NOT NULL,
  
  -- Status tracking
  status collaboration_status NOT NULL DEFAULT 'pending',
  
  -- Invitation system
  invitation_token VARCHAR(64) UNIQUE, -- Secure token for invitation links
  invitation_sent_at TIMESTAMPTZ,
  invitation_expires_at TIMESTAMPTZ,   -- 7 days from send
  accepted_at TIMESTAMPTZ,
  
  -- Shared creative space (monthly allocation)
  shared_creative_space INTEGER NOT NULL DEFAULT 0,
  shared_space_used INTEGER NOT NULL DEFAULT 0,
  
  -- Individual creative spaces remaining
  initiator_solo_space_remaining INTEGER NOT NULL DEFAULT 0,
  partner_solo_space_remaining INTEGER NOT NULL DEFAULT 0,
  
  -- Billing period tracking
  current_period_start TIMESTAMPTZ NOT NULL DEFAULT DATE_TRUNC('month', NOW()),
  current_period_end TIMESTAMPTZ NOT NULL DEFAULT DATE_TRUNC('month', NOW() + INTERVAL '1 month'),
  
  -- Project lifecycle
  started_at TIMESTAMPTZ,              -- When both users accepted
  completed_at TIMESTAMPTZ,            -- When marked as completed
  cancelled_at TIMESTAMPTZ,            -- When cancelled
  cancelled_by UUID REFERENCES users(id), -- Who cancelled
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT no_self_collaboration CHECK (initiator_user_id != collaborator_user_id),
  CONSTRAINT valid_shared_words CHECK (shared_words_used <= shared_words_available)
);

-- Indexes
CREATE INDEX idx_collaborations_initiator ON collaborations(initiator_user_id);
CREATE INDEX idx_collaborations_collaborator ON collaborations(collaborator_user_id);
CREATE INDEX idx_collaborations_status ON collaborations(status);
CREATE INDEX idx_collaborations_category ON collaborations(category);
CREATE INDEX idx_collaborations_invitation_token ON collaborations(invitation_token) WHERE invitation_token IS NOT NULL;
CREATE INDEX idx_collaborations_active ON collaborations(status) WHERE status = 'active';
CREATE INDEX idx_collaborations_pending ON collaborations(status, invitation_expires_at) WHERE status = 'pending';

-- ═══════════════════════════════════════════════════════════════════════════
-- COLLABORATION WORD USAGE LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE collaboration_word_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collaboration_id UUID NOT NULL REFERENCES collaborations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Usage details
  words_used INTEGER NOT NULL,
  usage_type VARCHAR(20) NOT NULL CHECK (usage_type IN ('shared', 'solo')),
  analysis_type VARCHAR(50),           -- e.g., 'writing_analysis', 'comparison'
  
  -- Context
  analysis_id UUID,                    -- Reference to specific analysis
  session_id VARCHAR(100),             -- For grouping related usage
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT positive_words_used CHECK (words_used > 0)
);

-- Indexes
CREATE INDEX idx_collab_word_usage_collaboration ON collaboration_word_usage(collaboration_id);
CREATE INDEX idx_collab_word_usage_user ON collaboration_word_usage(user_id);
CREATE INDEX idx_collab_word_usage_date ON collaboration_word_usage(created_at);
CREATE INDEX idx_collab_word_usage_type ON collaboration_word_usage(usage_type);

-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED COLLABORATIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE featured_collaborations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collaboration_id UUID NOT NULL REFERENCES collaborations(id) ON DELETE CASCADE,
  
  -- Submission details
  submission_title VARCHAR(200) NOT NULL,
  submission_summary TEXT NOT NULL,
  submission_tags VARCHAR(500),        -- Comma-separated tags
  
  -- Sample work (excerpts from their collaboration)
  sample_text TEXT NOT NULL,
  word_count INTEGER NOT NULL,
  
  -- Status and review
  status featured_collab_status NOT NULL DEFAULT 'draft',
  submitted_at TIMESTAMPTZ,
  reviewed_at TIMESTAMPTZ,
  reviewed_by UUID REFERENCES users(id), -- Admin who reviewed
  review_notes TEXT,
  
  -- Featured period (if approved)
  featured_start_date DATE,
  featured_end_date DATE,
  
  -- Public metadata (when featured)
  public_title VARCHAR(200),
  public_description TEXT,
  featured_image_url VARCHAR(500),     -- Optional featured image
  
  -- Analytics
  views_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(collaboration_id),             -- One submission per collaboration
  CONSTRAINT valid_word_count CHECK (word_count > 0),
  CONSTRAINT valid_featured_period CHECK (
    (featured_start_date IS NULL AND featured_end_date IS NULL) OR
    (featured_start_date IS NOT NULL AND featured_end_date IS NOT NULL AND featured_end_date >= featured_start_date)
  )
);

-- Indexes
CREATE INDEX idx_featured_collabs_collaboration ON featured_collaborations(collaboration_id);
CREATE INDEX idx_featured_collabs_status ON featured_collaborations(status);
CREATE INDEX idx_featured_collabs_submitted ON featured_collaborations(submitted_at);
CREATE INDEX idx_featured_collabs_featured_period ON featured_collaborations(featured_start_date, featured_end_date);
CREATE INDEX idx_featured_collabs_active ON featured_collaborations(status) WHERE status IN ('approved', 'featured');

-- ═══════════════════════════════════════════════════════════════════════════
-- USER COLLABORATION LIMITS
-- ═══════════════════════════════════════════════════════════════════════════
-- Enforces one active collaboration per user

CREATE TABLE user_collaboration_status (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Current collaboration
  active_collaboration_id UUID REFERENCES collaborations(id) ON DELETE SET NULL,
  
  -- Statistics
  total_collaborations_initiated INTEGER DEFAULT 0,
  total_collaborations_joined INTEGER DEFAULT 0,
  total_collaborations_completed INTEGER DEFAULT 0,
  
  -- Invitation history (prevent spam)
  last_invitation_sent_at TIMESTAMPTZ,
  invitations_sent_today INTEGER DEFAULT 0,
  
  -- Timestamps
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT max_daily_invitations CHECK (invitations_sent_today <= 3) -- Prevent spam
);

-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS AND FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Active collaborations with user details
CREATE OR REPLACE VIEW active_collaborations_view AS
SELECT 
  c.id,
  c.project_title,
  c.category,
  c.status,
  c.shared_words_available,
  c.shared_words_used,
  
  -- Initiator details
  u1.email AS initiator_email,
  u1.display_name AS initiator_name,
  c.initiator_solo_words_remaining,
  
  -- Collaborator details
  u2.email AS collaborator_email,
  u2.display_name AS collaborator_name,
  c.collaborator_solo_words_remaining,
  
  -- Timing
  c.started_at,
  c.current_period_end,
  
  -- Progress
  ROUND(
    (c.shared_words_used::DECIMAL / NULLIF(c.shared_words_available, 0)) * 100, 
    1
  ) AS shared_words_used_percent
  
FROM collaborations c
JOIN users u1 ON c.initiator_user_id = u1.id
LEFT JOIN users u2 ON c.collaborator_user_id = u2.id
WHERE c.status = 'active';

-- Featured collaborations public view
CREATE OR REPLACE VIEW featured_collaborations_public AS
SELECT 
  fc.id,
  fc.public_title,
  fc.public_description,
  fc.featured_image_url,
  fc.featured_start_date,
  fc.featured_end_date,
  fc.views_count,
  fc.shares_count,
  
  -- Collaboration details
  c.category,
  
  -- Collaborator names (public)
  u1.display_name AS collaborator_1,
  u2.display_name AS collaborator_2,
  
  fc.created_at
  
FROM featured_collaborations fc
JOIN collaborations c ON fc.collaboration_id = c.id
JOIN users u1 ON c.initiator_user_id = u1.id
JOIN users u2 ON c.collaborator_user_id = u2.id
WHERE fc.status = 'featured'
  AND fc.featured_start_date <= CURRENT_DATE 
  AND fc.featured_end_date >= CURRENT_DATE;

-- Function to check if user can start new collaboration
CREATE OR REPLACE FUNCTION can_user_collaborate(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  user_tier TEXT;
  has_active_collaboration BOOLEAN;
BEGIN
  -- Check if user is Pro tier
  SELECT COALESCE(s.tier, 'free') INTO user_tier
  FROM users u
  LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active'
  WHERE u.id = p_user_id;
  
  -- Must be Pro tier or higher
  IF user_tier NOT IN ('pro', 'featured_writer', 'authority_writer', 
                       'curator', 'featured_curator', 'authority_curator') THEN
    RETURN FALSE;
  END IF;
  
  -- Check if user has active collaboration
  SELECT EXISTS(
    SELECT 1 FROM collaborations 
    WHERE (initiator_user_id = p_user_id OR collaborator_user_id = p_user_id)
      AND status IN ('pending', 'active')
  ) INTO has_active_collaboration;
  
  RETURN NOT has_active_collaboration;
END;
$$ LANGUAGE plpgsql;

-- Function to initialize collaboration word pools
CREATE OR REPLACE FUNCTION initialize_collaboration_words(
  p_collaboration_id UUID,
  p_initiator_monthly_words INTEGER DEFAULT 25000,
  p_collaborator_monthly_words INTEGER DEFAULT 25000
) RETURNS VOID AS $$
BEGIN
  UPDATE collaborations 
  SET 
    shared_words_available = (p_initiator_monthly_words + p_collaborator_monthly_words) / 2,
    initiator_solo_words_remaining = p_initiator_monthly_words / 2,
    collaborator_solo_words_remaining = p_collaborator_monthly_words / 2,
    current_period_start = DATE_TRUNC('month', NOW()),
    current_period_end = DATE_TRUNC('month', NOW() + INTERVAL '1 month')
  WHERE id = p_collaboration_id;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- SAMPLE DATA (for testing)
-- ═══════════════════════════════════════════════════════════════════════════

-- Sample collaboration categories with descriptions
INSERT INTO collaboration_categories_meta (category, description, examples) VALUES
  ('business', 'Professional documents and business communications', 'Proposals, reports, strategic documents'),
  ('creative', 'Creative writing and artistic projects', 'Fiction, poetry, screenplays, creative essays'),
  ('personal', 'Personal and ceremonial writing', 'Wedding speeches, eulogies, personal memoirs'),
  ('academic', 'Research and academic collaborations', 'Papers, research proposals, academic articles'),
  ('journalism', 'News and investigative writing', 'Articles, investigations, editorial pieces'),
  ('technical', 'Technical documentation and guides', 'User manuals, API docs, how-to guides'),
  ('marketing', 'Marketing and promotional content', 'Copy, campaigns, content marketing'),
  ('other', 'Unique or uncategorized projects', 'Experimental or genre-blending work')
ON CONFLICT DO NOTHING;

-- Create the metadata table if it doesn't exist
CREATE TABLE IF NOT EXISTS collaboration_categories_meta (
  category collaboration_category PRIMARY KEY,
  description TEXT NOT NULL,
  examples TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);