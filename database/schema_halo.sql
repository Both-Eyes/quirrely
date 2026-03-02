-- ═══════════════════════════════════════════════════════════════
-- HALO SCHEMA — Hate, Abuse, Language, Outcomes
-- PostgreSQL (Supabase/Railway/Neon compatible)
-- ═══════════════════════════════════════════════════════════════

-- Violation categories enum
CREATE TYPE halo_category AS ENUM ('H', 'A', 'L', 'O');

-- Severity tiers enum
CREATE TYPE halo_tier AS ENUM ('T1', 'T2', 'T3');

-- Action types enum
CREATE TYPE halo_action AS ENUM ('WARN', 'CAUTION', 'COOLDOWN', 'BLOCK', 'SUSPEND');

-- ───────────────────────────────────────────────────────────────
-- HALO VIOLATIONS LOG
-- Records every detected violation
-- ───────────────────────────────────────────────────────────────
CREATE TABLE halo_violations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Who
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  session_id VARCHAR(100),
  ip_address INET,
  user_agent TEXT,
  
  -- What
  category halo_category NOT NULL,
  tier halo_tier NOT NULL,
  action_taken halo_action NOT NULL,
  
  -- Content (for review)
  content_hash VARCHAR(64) NOT NULL,
  content_snippet VARCHAR(200),  -- First 200 chars, for human review
  
  -- Detection details
  reason VARCHAR(100) NOT NULL,  -- e.g., "racial_slur", "rate_limit"
  matches JSONB,                 -- Array of matched patterns
  confidence DECIMAL(3,2),       -- 0.00 to 1.00
  
  -- Context
  source VARCHAR(50),            -- "test_input", "submission", "bio", "display_name"
  analysis_time_ms DECIMAL(10,2),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Resolution (for T2/T3)
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolved_by UUID REFERENCES users(id),
  resolution_notes TEXT
);

-- Indexes for common queries
CREATE INDEX idx_halo_violations_user ON halo_violations(user_id);
CREATE INDEX idx_halo_violations_session ON halo_violations(session_id);
CREATE INDEX idx_halo_violations_tier ON halo_violations(tier);
CREATE INDEX idx_halo_violations_category ON halo_violations(category);
CREATE INDEX idx_halo_violations_created ON halo_violations(created_at);
CREATE INDEX idx_halo_violations_hash ON halo_violations(content_hash);
CREATE INDEX idx_halo_violations_unresolved ON halo_violations(resolved_at) WHERE resolved_at IS NULL;

-- ───────────────────────────────────────────────────────────────
-- USER HALO STATUS
-- Current moderation status per user
-- ───────────────────────────────────────────────────────────────
CREATE TABLE user_halo_status (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Violation counts (rolling windows)
  t1_count_24h INTEGER DEFAULT 0,
  t2_count_7d INTEGER DEFAULT 0,
  t3_count_total INTEGER DEFAULT 0,
  
  -- Current status
  is_suspended BOOLEAN DEFAULT FALSE,
  is_shadowbanned BOOLEAN DEFAULT FALSE,
  
  -- Suspension details
  suspended_at TIMESTAMP WITH TIME ZONE,
  suspension_reason TEXT,
  suspension_tier halo_tier,
  suspension_expires_at TIMESTAMP WITH TIME ZONE,  -- NULL = permanent
  
  -- Cooldown
  cooldown_until TIMESTAMP WITH TIME ZONE,
  
  -- Trust score (can be used for graduated moderation)
  trust_score INTEGER DEFAULT 100,  -- 0-100, starts at 100
  
  -- Timestamps
  first_violation_at TIMESTAMP WITH TIME ZONE,
  last_violation_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ───────────────────────────────────────────────────────────────
-- HALO APPEALS
-- For users to appeal T2/T3 actions
-- ───────────────────────────────────────────────────────────────
CREATE TABLE halo_appeals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  violation_id UUID REFERENCES halo_violations(id),
  
  -- Appeal content
  appeal_text TEXT NOT NULL,
  appeal_submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Review
  status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, denied
  reviewed_at TIMESTAMP WITH TIME ZONE,
  reviewed_by UUID REFERENCES users(id),
  review_notes TEXT,
  
  -- Outcome
  action_reversed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_halo_appeals_status ON halo_appeals(status);
CREATE INDEX idx_halo_appeals_user ON halo_appeals(user_id);

-- ───────────────────────────────────────────────────────────────
-- SESSION HALO TRACKING
-- Per-session violation tracking (for escalation)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE session_halo_status (
  session_id VARCHAR(100) PRIMARY KEY,
  
  -- Counts this session
  t1_count INTEGER DEFAULT 0,
  t2_count INTEGER DEFAULT 0,
  
  -- Status
  is_blocked BOOLEAN DEFAULT FALSE,
  blocked_at TIMESTAMP WITH TIME ZONE,
  
  -- Cooldown
  cooldown_until TIMESTAMP WITH TIME ZONE,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_violation_at TIMESTAMP WITH TIME ZONE
);

-- ───────────────────────────────────────────────────────────────
-- BLOCKED CONTENT HASHES
-- Prevent resubmission of blocked content
-- ───────────────────────────────────────────────────────────────
CREATE TABLE halo_blocked_hashes (
  content_hash VARCHAR(64) PRIMARY KEY,
  tier halo_tier NOT NULL,
  category halo_category NOT NULL,
  reason VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE  -- NULL = permanent
);

-- ───────────────────────────────────────────────────────────────
-- HALO DAILY AGGREGATES
-- For analytics dashboard
-- ───────────────────────────────────────────────────────────────
CREATE TABLE halo_daily_stats (
  date DATE PRIMARY KEY,
  
  -- Violation counts by tier
  t1_count INTEGER DEFAULT 0,
  t2_count INTEGER DEFAULT 0,
  t3_count INTEGER DEFAULT 0,
  
  -- Violation counts by category
  hate_count INTEGER DEFAULT 0,
  abuse_count INTEGER DEFAULT 0,
  language_count INTEGER DEFAULT 0,
  outcomes_count INTEGER DEFAULT 0,
  
  -- Actions taken
  warnings_issued INTEGER DEFAULT 0,
  cooldowns_issued INTEGER DEFAULT 0,
  suspensions_issued INTEGER DEFAULT 0,
  
  -- Users affected
  unique_users_warned INTEGER DEFAULT 0,
  unique_users_suspended INTEGER DEFAULT 0,
  
  -- Appeals
  appeals_submitted INTEGER DEFAULT 0,
  appeals_approved INTEGER DEFAULT 0,
  appeals_denied INTEGER DEFAULT 0,
  
  -- Performance
  avg_analysis_time_ms DECIMAL(10,2),
  total_analyses INTEGER DEFAULT 0,
  
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ───────────────────────────────────────────────────────────────
-- FUNCTIONS
-- ───────────────────────────────────────────────────────────────

-- Update user status after violation
CREATE OR REPLACE FUNCTION update_user_halo_status()
RETURNS TRIGGER AS $$
BEGIN
  -- Insert or update user status
  INSERT INTO user_halo_status (user_id, first_violation_at, last_violation_at)
  VALUES (NEW.user_id, NOW(), NOW())
  ON CONFLICT (user_id) DO UPDATE SET
    last_violation_at = NOW(),
    updated_at = NOW();
  
  -- Update tier counts
  IF NEW.tier = 'T1' THEN
    UPDATE user_halo_status 
    SET t1_count_24h = t1_count_24h + 1,
        trust_score = GREATEST(0, trust_score - 5)
    WHERE user_id = NEW.user_id;
  ELSIF NEW.tier = 'T2' THEN
    UPDATE user_halo_status 
    SET t2_count_7d = t2_count_7d + 1,
        cooldown_until = NOW() + INTERVAL '1 hour',
        trust_score = GREATEST(0, trust_score - 20)
    WHERE user_id = NEW.user_id;
  ELSIF NEW.tier = 'T3' THEN
    UPDATE user_halo_status 
    SET t3_count_total = t3_count_total + 1,
        is_suspended = TRUE,
        suspended_at = NOW(),
        suspension_reason = NEW.reason,
        suspension_tier = 'T3',
        trust_score = 0
    WHERE user_id = NEW.user_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_user_halo_status
  AFTER INSERT ON halo_violations
  FOR EACH ROW
  WHEN (NEW.user_id IS NOT NULL)
  EXECUTE FUNCTION update_user_halo_status();

-- Reset daily T1 counts (run via cron)
CREATE OR REPLACE FUNCTION reset_daily_t1_counts()
RETURNS void AS $$
BEGIN
  UPDATE user_halo_status SET t1_count_24h = 0;
END;
$$ LANGUAGE plpgsql;

-- Reset weekly T2 counts (run via cron)
CREATE OR REPLACE FUNCTION reset_weekly_t2_counts()
RETURNS void AS $$
BEGIN
  UPDATE user_halo_status SET t2_count_7d = 0;
END;
$$ LANGUAGE plpgsql;

-- Aggregate daily stats (run at end of day)
CREATE OR REPLACE FUNCTION aggregate_halo_daily_stats(target_date DATE)
RETURNS void AS $$
BEGIN
  INSERT INTO halo_daily_stats (
    date, t1_count, t2_count, t3_count,
    hate_count, abuse_count, language_count, outcomes_count,
    total_analyses, avg_analysis_time_ms
  )
  SELECT
    target_date,
    COUNT(*) FILTER (WHERE tier = 'T1'),
    COUNT(*) FILTER (WHERE tier = 'T2'),
    COUNT(*) FILTER (WHERE tier = 'T3'),
    COUNT(*) FILTER (WHERE category = 'H'),
    COUNT(*) FILTER (WHERE category = 'A'),
    COUNT(*) FILTER (WHERE category = 'L'),
    COUNT(*) FILTER (WHERE category = 'O'),
    COUNT(*),
    AVG(analysis_time_ms)
  FROM halo_violations
  WHERE DATE(created_at) = target_date
  ON CONFLICT (date) DO UPDATE SET
    t1_count = EXCLUDED.t1_count,
    t2_count = EXCLUDED.t2_count,
    t3_count = EXCLUDED.t3_count,
    hate_count = EXCLUDED.hate_count,
    abuse_count = EXCLUDED.abuse_count,
    language_count = EXCLUDED.language_count,
    outcomes_count = EXCLUDED.outcomes_count,
    total_analyses = EXCLUDED.total_analyses,
    avg_analysis_time_ms = EXCLUDED.avg_analysis_time_ms,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ───────────────────────────────────────────────────────────────
-- VIEWS
-- ───────────────────────────────────────────────────────────────

-- Pending reviews (T2/T3 unresolved)
CREATE VIEW halo_pending_reviews AS
SELECT 
  v.id,
  v.user_id,
  v.tier,
  v.category,
  v.content_snippet,
  v.reason,
  v.created_at,
  u.email,
  u.display_name
FROM halo_violations v
LEFT JOIN users u ON v.user_id = u.id
WHERE v.tier IN ('T2', 'T3')
  AND v.resolved_at IS NULL
ORDER BY 
  CASE v.tier WHEN 'T3' THEN 1 WHEN 'T2' THEN 2 END,
  v.created_at DESC;

-- Suspended users
CREATE VIEW halo_suspended_users AS
SELECT 
  s.user_id,
  u.email,
  u.display_name,
  s.suspended_at,
  s.suspension_reason,
  s.suspension_tier,
  s.suspension_expires_at,
  s.t3_count_total
FROM user_halo_status s
JOIN users u ON s.user_id = u.id
WHERE s.is_suspended = TRUE
ORDER BY s.suspended_at DESC;

-- Today's stats
CREATE VIEW halo_today_stats AS
SELECT
  COUNT(*) as total_violations,
  COUNT(*) FILTER (WHERE tier = 'T1') as t1_count,
  COUNT(*) FILTER (WHERE tier = 'T2') as t2_count,
  COUNT(*) FILTER (WHERE tier = 'T3') as t3_count,
  COUNT(*) FILTER (WHERE category = 'H') as hate_count,
  COUNT(*) FILTER (WHERE category = 'A') as abuse_count,
  COUNT(*) FILTER (WHERE category = 'L') as language_count,
  COUNT(*) FILTER (WHERE category = 'O') as outcomes_count,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(analysis_time_ms) as avg_analysis_ms
FROM halo_violations
WHERE DATE(created_at) = CURRENT_DATE;

