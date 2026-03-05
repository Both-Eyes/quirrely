-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY ADMIN DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Admin users, audit logging, and system tracking.
-- Roles: Admin (full), Moderator (Featured review only)

-- ═══════════════════════════════════════════════════════════════════════════
-- ADMIN USERS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS admin_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Links to regular user account
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  email TEXT NOT NULL UNIQUE,
  
  -- Role
  role TEXT NOT NULL CHECK (role IN ('admin', 'moderator')),
  
  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  
  -- Metadata
  created_by UUID REFERENCES admin_users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_role ON admin_users(role);


-- ═══════════════════════════════════════════════════════════════════════════
-- AUDIT LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS admin_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Who
  admin_id UUID REFERENCES admin_users(id) ON DELETE SET NULL,
  admin_email TEXT NOT NULL,  -- Denormalized for history
  
  -- What
  action TEXT NOT NULL,
  
  -- Target
  target_type TEXT NOT NULL,  -- 'user', 'submission', 'content', 'admin'
  target_id TEXT NOT NULL,
  
  -- Details
  details JSONB DEFAULT '{}',
  
  -- Context
  ip_address INET,
  user_agent TEXT,
  
  -- When
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_log_action ON admin_audit_log(action);
CREATE INDEX idx_audit_log_target ON admin_audit_log(target_type, target_id);
CREATE INDEX idx_audit_log_created ON admin_audit_log(created_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED SUBMISSIONS (Extended for admin review)
-- ═══════════════════════════════════════════════════════════════════════════

-- Add review columns to existing featured_submissions table
ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  reviewed_by UUID REFERENCES admin_users(id);

ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  reviewed_at TIMESTAMPTZ;

ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  review_notes TEXT;

ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  rejection_reason TEXT;

ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  escalated BOOLEAN DEFAULT FALSE;

ALTER TABLE featured_submissions ADD COLUMN IF NOT EXISTS 
  escalation_reason TEXT;


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURED REVIEW HISTORY
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS featured_review_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  submission_id UUID REFERENCES featured_submissions(id) ON DELETE CASCADE,
  
  -- Review details
  action TEXT NOT NULL CHECK (action IN ('approve', 'reject', 'request_changes', 'escalate')),
  feedback TEXT,
  rejection_reason TEXT,
  
  -- Reviewer
  reviewer_id UUID REFERENCES admin_users(id),
  reviewer_email TEXT,
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_history_submission ON featured_review_history(submission_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- ADMIN NOTIFICATIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS admin_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Type
  notification_type TEXT NOT NULL,
  
  -- Content
  title TEXT NOT NULL,
  message TEXT,
  link TEXT,
  
  -- Targeting (null = all admins)
  target_admin_id UUID REFERENCES admin_users(id),
  target_role TEXT,  -- 'admin', 'moderator', or null for all
  
  -- Status
  read_by JSONB DEFAULT '[]',  -- Array of admin IDs who read it
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

CREATE INDEX idx_admin_notifications_type ON admin_notifications(notification_type);
CREATE INDEX idx_admin_notifications_created ON admin_notifications(created_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- USER SUSPENSIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_suspensions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Suspension details
  reason TEXT NOT NULL,
  suspended_by UUID REFERENCES admin_users(id),
  
  -- Duration
  suspended_at TIMESTAMPTZ DEFAULT NOW(),
  suspended_until TIMESTAMPTZ,  -- NULL = indefinite
  
  -- Resolution
  lifted_at TIMESTAMPTZ,
  lifted_by UUID REFERENCES admin_users(id),
  lift_reason TEXT
);

CREATE INDEX idx_suspensions_user ON user_suspensions(user_id);
CREATE INDEX idx_suspensions_active ON user_suspensions(user_id) 
  WHERE lifted_at IS NULL;


-- ═══════════════════════════════════════════════════════════════════════════
-- IMPERSONATION SESSIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS impersonation_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Who is impersonating whom
  admin_id UUID REFERENCES admin_users(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Token
  token_hash TEXT NOT NULL,
  
  -- Session
  started_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  
  -- Actions taken during session
  actions_log JSONB DEFAULT '[]',
  
  -- Context
  ip_address INET,
  user_agent TEXT
);

CREATE INDEX idx_impersonation_admin ON impersonation_sessions(admin_id);
CREATE INDEX idx_impersonation_user ON impersonation_sessions(user_id);
CREATE INDEX idx_impersonation_active ON impersonation_sessions(expires_at) 
  WHERE ended_at IS NULL;


-- ═══════════════════════════════════════════════════════════════════════════
-- SYSTEM METRICS (For dashboard)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS daily_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  metric_date DATE NOT NULL,
  
  -- User metrics
  total_users INTEGER,
  new_signups INTEGER,
  active_users INTEGER,
  
  -- Subscription metrics
  total_subscriptions INTEGER,
  new_subscriptions INTEGER,
  churned_subscriptions INTEGER,
  mrr_cents INTEGER,
  
  -- Activity metrics
  total_analyses INTEGER,
  total_words INTEGER,
  
  -- Featured metrics
  pending_submissions INTEGER,
  approved_submissions INTEGER,
  rejected_submissions INTEGER,
  
  -- Timestamps
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(metric_date)
);

CREATE INDEX idx_daily_metrics_date ON daily_metrics(metric_date DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Log admin action
CREATE OR REPLACE FUNCTION log_admin_action(
  p_admin_id UUID,
  p_action TEXT,
  p_target_type TEXT,
  p_target_id TEXT,
  p_details JSONB DEFAULT '{}',
  p_ip_address INET DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_admin_email TEXT;
  v_log_id UUID;
BEGIN
  SELECT email INTO v_admin_email FROM admin_users WHERE id = p_admin_id;
  
  INSERT INTO admin_audit_log (admin_id, admin_email, action, target_type, target_id, details, ip_address)
  VALUES (p_admin_id, v_admin_email, p_action, p_target_type, p_target_id, p_details, p_ip_address)
  RETURNING id INTO v_log_id;
  
  RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;


-- Check if user is admin
CREATE OR REPLACE FUNCTION is_admin(p_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM admin_users 
    WHERE user_id = p_user_id AND is_active = TRUE
  );
END;
$$ LANGUAGE plpgsql;


-- Get admin role
CREATE OR REPLACE FUNCTION get_admin_role(p_user_id UUID)
RETURNS TEXT AS $$
DECLARE
  v_role TEXT;
BEGIN
  SELECT role INTO v_role FROM admin_users 
  WHERE user_id = p_user_id AND is_active = TRUE;
  RETURN v_role;
END;
$$ LANGUAGE plpgsql;


-- Calculate daily metrics
CREATE OR REPLACE FUNCTION calculate_daily_metrics(p_date DATE)
RETURNS void AS $$
BEGIN
  INSERT INTO daily_metrics (
    metric_date,
    total_users,
    new_signups,
    active_users,
    total_subscriptions,
    new_subscriptions,
    churned_subscriptions,
    mrr_cents,
    total_analyses,
    total_words,
    pending_submissions,
    approved_submissions,
    rejected_submissions
  )
  SELECT
    p_date,
    (SELECT COUNT(*) FROM users WHERE status = 'active'),
    (SELECT COUNT(*) FROM users WHERE DATE(created_at) = p_date),
    (SELECT COUNT(DISTINCT user_id) FROM analyses WHERE DATE(created_at) = p_date),
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'active'),
    (SELECT COUNT(*) FROM subscriptions WHERE DATE(created_at) = p_date),
    (SELECT COUNT(*) FROM subscriptions WHERE DATE(cancelled_at) = p_date),
    (SELECT COALESCE(SUM(amount_cents), 0) FROM subscriptions WHERE status = 'active' AND interval = 'month'),
    (SELECT COUNT(*) FROM analyses WHERE DATE(created_at) = p_date),
    (SELECT COALESCE(SUM(word_count), 0) FROM analyses WHERE DATE(created_at) = p_date),
    (SELECT COUNT(*) FROM featured_submissions WHERE status = 'pending'),
    (SELECT COUNT(*) FROM featured_submissions WHERE DATE(reviewed_at) = p_date AND status = 'approved'),
    (SELECT COUNT(*) FROM featured_submissions WHERE DATE(reviewed_at) = p_date AND status = 'rejected')
  ON CONFLICT (metric_date) DO UPDATE SET
    total_users = EXCLUDED.total_users,
    new_signups = EXCLUDED.new_signups,
    active_users = EXCLUDED.active_users,
    total_subscriptions = EXCLUDED.total_subscriptions,
    new_subscriptions = EXCLUDED.new_subscriptions,
    churned_subscriptions = EXCLUDED.churned_subscriptions,
    mrr_cents = EXCLUDED.mrr_cents,
    total_analyses = EXCLUDED.total_analyses,
    total_words = EXCLUDED.total_words,
    pending_submissions = EXCLUDED.pending_submissions,
    approved_submissions = EXCLUDED.approved_submissions,
    rejected_submissions = EXCLUDED.rejected_submissions,
    calculated_at = NOW();
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Pending Featured submissions queue
CREATE OR REPLACE VIEW featured_queue AS
SELECT 
  fs.id,
  fs.user_id,
  u.email as user_email,
  u.display_name as user_display_name,
  fs.submission_type,
  fs.content,
  fs.status,
  fs.submitted_at,
  fs.escalated,
  fs.escalation_reason
FROM featured_submissions fs
JOIN users u ON fs.user_id = u.id
WHERE fs.status IN ('pending', 'escalated')
ORDER BY 
  CASE WHEN fs.escalated THEN 0 ELSE 1 END,
  fs.submitted_at ASC;


-- Active suspensions
CREATE OR REPLACE VIEW active_suspensions AS
SELECT 
  s.*,
  u.email as user_email,
  a.email as suspended_by_email
FROM user_suspensions s
JOIN users u ON s.user_id = u.id
JOIN admin_users a ON s.suspended_by = a.id
WHERE s.lifted_at IS NULL
  AND (s.suspended_until IS NULL OR s.suspended_until > NOW());


-- Recent admin activity
CREATE OR REPLACE VIEW recent_admin_activity AS
SELECT 
  a.action,
  a.admin_email,
  a.target_type,
  a.target_id,
  a.details,
  a.created_at
FROM admin_audit_log a
ORDER BY a.created_at DESC
LIMIT 100;


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

-- Admin tables should only be accessible via service role
-- No RLS policies needed as these are admin-only tables
