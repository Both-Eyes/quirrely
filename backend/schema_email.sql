-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY EMAIL DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Email preferences, send history, and analytics.

-- ═══════════════════════════════════════════════════════════════════════════
-- EMAIL PREFERENCES
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_preferences (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Category toggles
  engagement_enabled BOOLEAN DEFAULT TRUE,
  digest_enabled BOOLEAN DEFAULT TRUE,
  
  -- Digest settings
  digest_day INTEGER DEFAULT 0 CHECK (digest_day >= 0 AND digest_day <= 6),  -- 0 = Monday
  
  -- Timing preferences
  preferred_hour INTEGER DEFAULT 9 CHECK (preferred_hour >= 0 AND preferred_hour <= 23),
  timezone TEXT DEFAULT 'UTC',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- EMAIL SEND LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_sends (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Recipient
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  to_email TEXT NOT NULL,
  
  -- Email details
  email_type TEXT NOT NULL,
  subject TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('transactional', 'engagement', 'digest')),
  
  -- Provider response
  provider TEXT DEFAULT 'resend',
  provider_id TEXT,  -- Resend message ID
  
  -- Status
  status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')),
  
  -- Analytics
  opened_at TIMESTAMPTZ,
  clicked_at TIMESTAMPTZ,
  click_count INTEGER DEFAULT 0,
  
  -- Error tracking
  error_message TEXT,
  
  -- Timestamps
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_sends_user ON email_sends(user_id, sent_at DESC);
CREATE INDEX idx_email_sends_type ON email_sends(email_type);
CREATE INDEX idx_email_sends_status ON email_sends(status);
CREATE INDEX idx_email_sends_sent ON email_sends(sent_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- EMAIL EVENTS (Webhook tracking)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Reference to send
  email_send_id UUID REFERENCES email_sends(id) ON DELETE CASCADE,
  
  -- Event details
  event_type TEXT NOT NULL CHECK (event_type IN ('delivered', 'opened', 'clicked', 'bounced', 'complained', 'unsubscribed')),
  
  -- Click tracking
  click_url TEXT,
  
  -- Client info
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamps
  occurred_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_events_send ON email_events(email_send_id);
CREATE INDEX idx_email_events_type ON email_events(event_type);


-- ═══════════════════════════════════════════════════════════════════════════
-- UNSUBSCRIBE LOG
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_unsubscribes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  email TEXT NOT NULL,
  
  -- What was unsubscribed
  category TEXT NOT NULL CHECK (category IN ('engagement', 'digest', 'all')),
  
  -- How
  method TEXT NOT NULL CHECK (method IN ('one_click', 'preferences', 'complaint')),
  
  -- From which email
  email_send_id UUID REFERENCES email_sends(id) ON DELETE SET NULL,
  
  -- Timestamps
  unsubscribed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_unsubscribes_user ON email_unsubscribes(user_id);
CREATE INDEX idx_email_unsubscribes_email ON email_unsubscribes(email);


-- ═══════════════════════════════════════════════════════════════════════════
-- SUPPRESSION LIST (bounced/complained emails)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_suppression (
  email TEXT PRIMARY KEY,
  
  reason TEXT NOT NULL CHECK (reason IN ('bounce', 'complaint', 'manual')),
  
  -- Timestamps
  added_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Check if email is suppressed
CREATE OR REPLACE FUNCTION is_email_suppressed(p_email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (SELECT 1 FROM email_suppression WHERE email = LOWER(p_email));
END;
$$ LANGUAGE plpgsql;


-- Log email send
CREATE OR REPLACE FUNCTION log_email_send(
  p_user_id UUID,
  p_to_email TEXT,
  p_email_type TEXT,
  p_subject TEXT,
  p_category TEXT,
  p_provider_id TEXT
)
RETURNS UUID AS $$
DECLARE
  v_send_id UUID;
BEGIN
  INSERT INTO email_sends (user_id, to_email, email_type, subject, category, provider_id)
  VALUES (p_user_id, p_to_email, p_email_type, p_subject, p_category, p_provider_id)
  RETURNING id INTO v_send_id;
  
  RETURN v_send_id;
END;
$$ LANGUAGE plpgsql;


-- Log email event
CREATE OR REPLACE FUNCTION log_email_event(
  p_email_send_id UUID,
  p_event_type TEXT,
  p_click_url TEXT DEFAULT NULL,
  p_ip_address INET DEFAULT NULL,
  p_user_agent TEXT DEFAULT NULL
)
RETURNS void AS $$
BEGIN
  INSERT INTO email_events (email_send_id, event_type, click_url, ip_address, user_agent)
  VALUES (p_email_send_id, p_event_type, p_click_url, p_ip_address, p_user_agent);
  
  -- Update send record
  UPDATE email_sends
  SET status = p_event_type,
      opened_at = CASE WHEN p_event_type = 'opened' AND opened_at IS NULL THEN NOW() ELSE opened_at END,
      clicked_at = CASE WHEN p_event_type = 'clicked' AND clicked_at IS NULL THEN NOW() ELSE clicked_at END,
      click_count = CASE WHEN p_event_type = 'clicked' THEN click_count + 1 ELSE click_count END
  WHERE id = p_email_send_id;
  
  -- Handle bounces and complaints
  IF p_event_type IN ('bounced', 'complained') THEN
    INSERT INTO email_suppression (email, reason)
    SELECT to_email, CASE WHEN p_event_type = 'bounced' THEN 'bounce' ELSE 'complaint' END
    FROM email_sends WHERE id = p_email_send_id
    ON CONFLICT (email) DO NOTHING;
  END IF;
END;
$$ LANGUAGE plpgsql;


-- Get user email stats
CREATE OR REPLACE FUNCTION get_user_email_stats(p_user_id UUID)
RETURNS TABLE (
  total_sent BIGINT,
  total_opened BIGINT,
  total_clicked BIGINT,
  open_rate NUMERIC,
  click_rate NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*) as total_sent,
    COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as total_opened,
    COUNT(*) FILTER (WHERE clicked_at IS NOT NULL) as total_clicked,
    ROUND(COUNT(*) FILTER (WHERE opened_at IS NOT NULL)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1) as open_rate,
    ROUND(COUNT(*) FILTER (WHERE clicked_at IS NOT NULL)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1) as click_rate
  FROM email_sends
  WHERE user_id = p_user_id
    AND sent_at > NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Email analytics summary
CREATE OR REPLACE VIEW email_analytics_summary AS
SELECT 
  email_type,
  category,
  DATE_TRUNC('day', sent_at) as date,
  COUNT(*) as sent,
  COUNT(*) FILTER (WHERE status IN ('delivered', 'opened', 'clicked')) as delivered,
  COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as opened,
  COUNT(*) FILTER (WHERE clicked_at IS NOT NULL) as clicked,
  COUNT(*) FILTER (WHERE status = 'bounced') as bounced,
  COUNT(*) FILTER (WHERE status = 'complained') as complained
FROM email_sends
WHERE sent_at > NOW() - INTERVAL '30 days'
GROUP BY email_type, category, DATE_TRUNC('day', sent_at)
ORDER BY date DESC;


-- Users who need streak reminder today
CREATE OR REPLACE VIEW users_needing_streak_reminder AS
SELECT 
  u.id,
  u.email,
  ep.timezone,
  um.streak_1k_current as streak_days
FROM users u
JOIN email_preferences ep ON u.id = ep.user_id
JOIN user_milestones um ON u.id = um.user_id
WHERE um.streak_1k_current > 0
  AND um.streak_1k_last_date < CURRENT_DATE
  AND ep.engagement_enabled = TRUE
  AND u.status = 'active'
  -- Haven't sent streak reminder today
  AND NOT EXISTS (
    SELECT 1 FROM email_sends es
    WHERE es.user_id = u.id
      AND es.email_type = 'streak_at_risk'
      AND es.sent_at > CURRENT_DATE
  );


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE email_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sends ENABLE ROW LEVEL SECURITY;

-- Users can view/update their own preferences
CREATE POLICY "Users can manage own preferences" ON email_preferences
  FOR ALL USING (auth.uid() = user_id);

-- Users can view their own email history
CREATE POLICY "Users can view own emails" ON email_sends
  FOR SELECT USING (auth.uid() = user_id);
