-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY COLLABORATION MIGRATION v1.0
-- Adds writing partnership tables to existing database
-- ═══════════════════════════════════════════════════════════════════════════

-- Migration metadata
INSERT INTO migrations (version, description, applied_at) VALUES 
('001', 'Add collaboration tables for writing partnerships', NOW())
ON CONFLICT (version) DO NOTHING;

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

-- Partnership invitation status
DO $$ BEGIN
  CREATE TYPE partnership_status AS ENUM (
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
  CREATE TYPE featured_partnership_status AS ENUM (
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
-- WRITING PARTNERSHIPS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS writing_partnerships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Partners (Pro tier required)
  initiator_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  partner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Partnership details
  partnership_name VARCHAR(200) NOT NULL,
  partnership_intention TEXT,  -- What they hope to create together
  partnership_type partnership_type NOT NULL,
  
  -- Status tracking
  status partnership_status NOT NULL DEFAULT 'pending',
  
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
  
  -- Partnership lifecycle
  started_at TIMESTAMPTZ,              -- When both users accepted
  completed_at TIMESTAMPTZ,            -- When marked as completed
  cancelled_at TIMESTAMPTZ,            -- When cancelled
  cancelled_by UUID REFERENCES users(id), -- Who cancelled
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT no_self_collaboration CHECK (initiator_user_id != partner_user_id),
  CONSTRAINT valid_shared_words CHECK (shared_space_used <= shared_creative_space)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_partnerships_initiator ON writing_partnerships(initiator_user_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_partner ON writing_partnerships(partner_user_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_status ON writing_partnerships(status);
CREATE INDEX IF NOT EXISTS idx_partnerships_type ON writing_partnerships(partnership_type);
CREATE INDEX IF NOT EXISTS idx_partnerships_invitation_token ON writing_partnerships(invitation_token) WHERE invitation_token IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_partnerships_active ON writing_partnerships(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_partnerships_pending ON writing_partnerships(status, invitation_expires_at) WHERE status = 'pending';

-- ═══════════════════════════════════════════════════════════════════════════
-- PARTNERSHIP WORD USAGE LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS partnership_word_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  partnership_id UUID NOT NULL REFERENCES writing_partnerships(id) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS idx_partnership_word_usage_partnership ON partnership_word_usage(partnership_id);
CREATE INDEX IF NOT EXISTS idx_partnership_word_usage_user ON partnership_word_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_partnership_word_usage_date ON partnership_word_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_partnership_word_usage_type ON partnership_word_usage(usage_type);

-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED PARTNERSHIPS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS featured_partnerships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  partnership_id UUID NOT NULL REFERENCES writing_partnerships(id) ON DELETE CASCADE,
  
  -- Submission details
  submission_title VARCHAR(200) NOT NULL,
  submission_summary TEXT NOT NULL,
  submission_tags VARCHAR(500),        -- Comma-separated tags
  
  -- Sample work (excerpts from their collaboration)
  sample_text TEXT NOT NULL,
  word_count INTEGER NOT NULL,
  
  -- Status and review
  status featured_partnership_status NOT NULL DEFAULT 'draft',
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
  UNIQUE(partnership_id),             -- One submission per collaboration
  CONSTRAINT valid_word_count CHECK (word_count > 0),
  CONSTRAINT valid_featured_period CHECK (
    (featured_start_date IS NULL AND featured_end_date IS NULL) OR
    (featured_start_date IS NOT NULL AND featured_end_date IS NOT NULL AND featured_end_date >= featured_start_date)
  )
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_featured_partnerships_partnership ON featured_partnerships(partnership_id);
CREATE INDEX IF NOT EXISTS idx_featured_partnerships_status ON featured_partnerships(status);
CREATE INDEX IF NOT EXISTS idx_featured_partnerships_submitted ON featured_partnerships(submitted_at);
CREATE INDEX IF NOT EXISTS idx_featured_partnerships_featured_period ON featured_partnerships(featured_start_date, featured_end_date);
CREATE INDEX IF NOT EXISTS idx_featured_partnerships_active ON featured_partnerships(status) WHERE status IN ('approved', 'featured');

-- ═══════════════════════════════════════════════════════════════════════════
-- USER PARTNERSHIP LIMITS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_partnership_status (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Current partnership
  active_partnership_id UUID REFERENCES writing_partnerships(id) ON DELETE SET NULL,
  
  -- Statistics
  total_partnerships_initiated INTEGER DEFAULT 0,
  total_partnerships_joined INTEGER DEFAULT 0,
  total_partnerships_completed INTEGER DEFAULT 0,
  
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

-- Active partnerships with user details
CREATE OR REPLACE VIEW active_partnerships_view AS
SELECT 
  p.id,
  p.partnership_name,
  p.partnership_type,
  p.status,
  p.shared_creative_space,
  p.shared_space_used,
  
  -- Initiator details
  u1.email AS initiator_email,
  u1.display_name AS initiator_name,
  p.initiator_solo_space_remaining,
  
  -- Partner details
  u2.email AS partner_email,
  u2.display_name AS partner_name,
  p.partner_solo_space_remaining,
  
  -- Timing
  p.started_at,
  p.current_period_end,
  
  -- Progress
  ROUND(
    (p.shared_space_used::DECIMAL / NULLIF(p.shared_creative_space, 0)) * 100, 
    1
  ) AS shared_words_used_percent
  
FROM writing_partnerships p
JOIN users u1 ON p.initiator_user_id = u1.id
LEFT JOIN users u2 ON p.partner_user_id = u2.id
WHERE p.status = 'active';

-- Featured partnerships public view
CREATE OR REPLACE VIEW featured_partnerships_public AS
SELECT 
  fp.id,
  fp.public_title,
  fp.public_description,
  fp.featured_image_url,
  fp.featured_start_date,
  fp.featured_end_date,
  fp.views_count,
  fp.shares_count,
  
  -- Partnership details
  p.partnership_type,
  
  -- Collaborator names (public)
  u1.display_name AS collaborator_1,
  u2.display_name AS collaborator_2,
  
  fp.created_at
  
FROM featured_partnerships fp
JOIN writing_partnerships p ON fp.partnership_id = p.id
JOIN users u1 ON p.initiator_user_id = u1.id
JOIN users u2 ON p.partner_user_id = u2.id
WHERE fp.status = 'featured'
  AND fp.featured_start_date <= CURRENT_DATE 
  AND fp.featured_end_date >= CURRENT_DATE;

-- Function to check if user can start partnership
CREATE OR REPLACE FUNCTION can_user_start_partnership(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  user_tier TEXT;
  has_active_partnership BOOLEAN;
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
  
  -- Check if user has active partnership
  SELECT EXISTS(
    SELECT 1 FROM writing_partnerships 
    WHERE (initiator_user_id = p_user_id OR partner_user_id = p_user_id)
      AND status IN ('pending', 'active')
  ) INTO has_active_partnership;
  
  RETURN NOT has_active_partnership;
END;
$$ LANGUAGE plpgsql;

-- Function to initialize partnership word pools
CREATE OR REPLACE FUNCTION initialize_partnership_words(
  p_partnership_id UUID,
  p_initiator_monthly_words INTEGER DEFAULT 25000,
  p_partner_monthly_words INTEGER DEFAULT 25000
) RETURNS VOID AS $$
BEGIN
  UPDATE writing_partnerships 
  SET 
    shared_creative_space = (p_initiator_monthly_words + p_partner_monthly_words) / 2,
    initiator_solo_space_remaining = p_initiator_monthly_words / 2,
    partner_solo_space_remaining = p_partner_monthly_words / 2,
    current_period_start = DATE_TRUNC('month', NOW()),
    current_period_end = DATE_TRUNC('month', NOW() + INTERVAL '1 month')
  WHERE id = p_partnership_id;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- MIGRATION VERIFICATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Verify all tables were created
DO $$ 
DECLARE 
    table_count INTEGER;
BEGIN 
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN (
        'writing_partnerships', 
        'partnership_word_usage', 
        'featured_partnerships',
        'user_partnership_status'
    );
    
    IF table_count != 4 THEN
        RAISE EXCEPTION 'Migration failed: Expected 4 tables, found %', table_count;
    END IF;
    
    RAISE NOTICE 'Partnership tables migration completed successfully';
END $$;