-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY ANALYTICS DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Event tracking, metrics storage, and user analytics.
-- Privacy-focused: User IDs are hashed in events.

-- ═══════════════════════════════════════════════════════════════════════════
-- RAW EVENTS (90-day retention)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS analytics_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Event info
  event_name TEXT NOT NULL,
  event_category TEXT NOT NULL,
  
  -- User (hashed for privacy)
  user_hash TEXT,  -- SHA256 hash of user ID, not PII
  
  -- Properties
  properties JSONB DEFAULT '{}',
  
  -- Context
  session_id TEXT,
  page_url TEXT,
  referrer TEXT,
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partition by month for efficient retention
CREATE INDEX idx_events_created ON analytics_events(created_at DESC);
CREATE INDEX idx_events_name ON analytics_events(event_name, created_at DESC);
CREATE INDEX idx_events_user ON analytics_events(user_hash, created_at DESC);
CREATE INDEX idx_events_category ON analytics_events(event_category);


-- ═══════════════════════════════════════════════════════════════════════════
-- USER ACTIVITY (1-year retention)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_activity (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Activity type
  activity_type TEXT NOT NULL,  -- 'analyze', 'read', 'bookmark', etc.
  
  -- Details
  details JSONB DEFAULT '{}',
  
  -- For aggregation
  word_count INTEGER DEFAULT 0,
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_activity_user ON user_activity(user_id, created_at DESC);
CREATE INDEX idx_user_activity_type ON user_activity(activity_type, created_at DESC);
CREATE INDEX idx_user_activity_date ON user_activity(DATE(created_at));


-- ═══════════════════════════════════════════════════════════════════════════
-- DAILY METRICS SNAPSHOTS (Forever)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS daily_analytics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  metric_date DATE NOT NULL UNIQUE,
  
  -- User metrics
  dau INTEGER DEFAULT 0,
  wau INTEGER DEFAULT 0,
  mau INTEGER DEFAULT 0,
  total_users INTEGER DEFAULT 0,
  new_signups INTEGER DEFAULT 0,
  
  -- Subscription metrics
  mrr_cents INTEGER DEFAULT 0,
  active_subscriptions INTEGER DEFAULT 0,
  active_trials INTEGER DEFAULT 0,
  trial_starts INTEGER DEFAULT 0,
  trial_conversions INTEGER DEFAULT 0,
  churns INTEGER DEFAULT 0,
  
  -- Activity metrics
  analyses_count INTEGER DEFAULT 0,
  words_analyzed INTEGER DEFAULT 0,
  posts_read INTEGER DEFAULT 0,
  deep_reads INTEGER DEFAULT 0,
  
  -- Feature metrics
  active_streaks INTEGER DEFAULT 0,
  featured_writers INTEGER DEFAULT 0,
  featured_curators INTEGER DEFAULT 0,
  new_milestones INTEGER DEFAULT 0,
  
  -- Calculated
  trial_conversion_rate NUMERIC(5,2),
  churn_rate NUMERIC(5,2),
  
  -- Timestamps
  calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_daily_analytics_date ON daily_analytics(metric_date DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- FUNNEL EVENTS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS funnel_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Funnel info
  funnel_name TEXT NOT NULL,
  step_name TEXT NOT NULL,
  step_order INTEGER NOT NULL,
  
  -- Timestamp
  completed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_funnel_events_user ON funnel_events(user_id);
CREATE INDEX idx_funnel_events_funnel ON funnel_events(funnel_name, step_order);
CREATE INDEX idx_funnel_events_date ON funnel_events(DATE(completed_at));

-- Unique constraint: user can only complete each step once per funnel
CREATE UNIQUE INDEX idx_funnel_events_unique ON funnel_events(user_id, funnel_name, step_name);


-- ═══════════════════════════════════════════════════════════════════════════
-- RETENTION COHORTS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS retention_cohorts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Cohort definition
  cohort_date DATE NOT NULL,
  cohort_type TEXT NOT NULL DEFAULT 'signup',  -- 'signup', 'first_analysis', etc.
  period_type TEXT NOT NULL DEFAULT 'weekly',  -- 'daily', 'weekly', 'monthly'
  
  -- Cohort size
  cohort_size INTEGER NOT NULL,
  
  -- Retention by period
  retention JSONB NOT NULL,  -- [{"period": 0, "retained": 100, "rate": 100.0}, ...]
  
  -- Timestamps
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(cohort_date, cohort_type, period_type)
);

CREATE INDEX idx_retention_cohorts_date ON retention_cohorts(cohort_date DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- USER ANALYTICS CACHE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_analytics_cache (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Writer stats
  total_words INTEGER DEFAULT 0,
  total_analyses INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  
  -- Reader stats
  total_posts_read INTEGER DEFAULT 0,
  total_deep_reads INTEGER DEFAULT 0,
  
  -- Featured stats
  profile_views_30d INTEGER DEFAULT 0,
  piece_views_30d INTEGER DEFAULT 0,
  path_follows_30d INTEGER DEFAULT 0,
  
  -- Last updated
  updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- FEATURE FLAGS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS feature_flags (
  name TEXT PRIMARY KEY,
  
  description TEXT,
  
  -- State
  enabled BOOLEAN DEFAULT FALSE,
  percentage INTEGER DEFAULT 0 CHECK (percentage >= 0 AND percentage <= 100),
  
  -- Targeting
  allowed_users TEXT[] DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════
-- PROFILE DISTRIBUTION (Daily snapshot)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS profile_distribution (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  snapshot_date DATE NOT NULL,
  
  -- Distribution
  distribution JSONB NOT NULL,  -- [{"type": "The Analyst", "count": 234, "percent": 18.8}, ...]
  
  -- Total
  total_profiles INTEGER NOT NULL,
  
  -- Timestamps
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(snapshot_date)
);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Hash user ID for privacy
CREATE OR REPLACE FUNCTION hash_user_id(p_user_id UUID)
RETURNS TEXT AS $$
BEGIN
  RETURN ENCODE(SHA256(p_user_id::TEXT::BYTEA), 'hex');
END;
$$ LANGUAGE plpgsql;


-- Track event
CREATE OR REPLACE FUNCTION track_event(
  p_event_name TEXT,
  p_event_category TEXT,
  p_user_id UUID DEFAULT NULL,
  p_properties JSONB DEFAULT '{}',
  p_session_id TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_event_id UUID;
  v_user_hash TEXT;
BEGIN
  IF p_user_id IS NOT NULL THEN
    v_user_hash := SUBSTRING(hash_user_id(p_user_id), 1, 16);
  END IF;
  
  INSERT INTO analytics_events (event_name, event_category, user_hash, properties, session_id)
  VALUES (p_event_name, p_event_category, v_user_hash, p_properties, p_session_id)
  RETURNING id INTO v_event_id;
  
  RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;


-- Record user activity
CREATE OR REPLACE FUNCTION record_activity(
  p_user_id UUID,
  p_activity_type TEXT,
  p_details JSONB DEFAULT '{}',
  p_word_count INTEGER DEFAULT 0
)
RETURNS UUID AS $$
DECLARE
  v_activity_id UUID;
BEGIN
  INSERT INTO user_activity (user_id, activity_type, details, word_count)
  VALUES (p_user_id, p_activity_type, p_details, p_word_count)
  RETURNING id INTO v_activity_id;
  
  -- Update cache
  INSERT INTO user_analytics_cache (user_id, total_words, total_analyses)
  VALUES (p_user_id, p_word_count, CASE WHEN p_activity_type = 'analyze' THEN 1 ELSE 0 END)
  ON CONFLICT (user_id) DO UPDATE SET
    total_words = user_analytics_cache.total_words + p_word_count,
    total_analyses = user_analytics_cache.total_analyses + CASE WHEN p_activity_type = 'analyze' THEN 1 ELSE 0 END,
    updated_at = NOW();
  
  RETURN v_activity_id;
END;
$$ LANGUAGE plpgsql;


-- Record funnel step
CREATE OR REPLACE FUNCTION record_funnel_step(
  p_user_id UUID,
  p_funnel_name TEXT,
  p_step_name TEXT,
  p_step_order INTEGER
)
RETURNS void AS $$
BEGIN
  INSERT INTO funnel_events (user_id, funnel_name, step_name, step_order)
  VALUES (p_user_id, p_funnel_name, p_step_name, p_step_order)
  ON CONFLICT (user_id, funnel_name, step_name) DO NOTHING;
END;
$$ LANGUAGE plpgsql;


-- Calculate DAU
CREATE OR REPLACE FUNCTION get_dau(p_date DATE)
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(DISTINCT user_id) 
    FROM user_activity 
    WHERE DATE(created_at) = p_date
  );
END;
$$ LANGUAGE plpgsql;


-- Calculate WAU
CREATE OR REPLACE FUNCTION get_wau(p_date DATE)
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(DISTINCT user_id) 
    FROM user_activity 
    WHERE created_at >= p_date - INTERVAL '7 days'
      AND created_at < p_date + INTERVAL '1 day'
  );
END;
$$ LANGUAGE plpgsql;


-- Calculate MAU
CREATE OR REPLACE FUNCTION get_mau(p_date DATE)
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(DISTINCT user_id) 
    FROM user_activity 
    WHERE created_at >= p_date - INTERVAL '30 days'
      AND created_at < p_date + INTERVAL '1 day'
  );
END;
$$ LANGUAGE plpgsql;


-- Calculate daily metrics
CREATE OR REPLACE FUNCTION calculate_daily_analytics(p_date DATE)
RETURNS void AS $$
BEGIN
  INSERT INTO daily_analytics (
    metric_date,
    dau, wau, mau,
    total_users, new_signups,
    mrr_cents, active_subscriptions, active_trials,
    analyses_count, words_analyzed,
    active_streaks, featured_writers, featured_curators
  )
  SELECT
    p_date,
    get_dau(p_date),
    get_wau(p_date),
    get_mau(p_date),
    (SELECT COUNT(*) FROM users WHERE status = 'active'),
    (SELECT COUNT(*) FROM users WHERE DATE(created_at) = p_date),
    (SELECT COALESCE(SUM(amount_cents), 0) FROM subscriptions WHERE status = 'active' AND interval = 'month'),
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'active'),
    (SELECT COUNT(*) FROM trials WHERE status = 'active'),
    (SELECT COUNT(*) FROM analyses WHERE DATE(created_at) = p_date),
    (SELECT COALESCE(SUM(word_count), 0) FROM analyses WHERE DATE(created_at) = p_date),
    (SELECT COUNT(*) FROM user_milestones WHERE streak_1k_current > 0),
    (SELECT COUNT(*) FROM featured_writers WHERE status = 'active'),
    (SELECT COUNT(*) FROM featured_curators WHERE status = 'active')
  ON CONFLICT (metric_date) DO UPDATE SET
    dau = EXCLUDED.dau,
    wau = EXCLUDED.wau,
    mau = EXCLUDED.mau,
    total_users = EXCLUDED.total_users,
    new_signups = EXCLUDED.new_signups,
    mrr_cents = EXCLUDED.mrr_cents,
    active_subscriptions = EXCLUDED.active_subscriptions,
    active_trials = EXCLUDED.active_trials,
    analyses_count = EXCLUDED.analyses_count,
    words_analyzed = EXCLUDED.words_analyzed,
    active_streaks = EXCLUDED.active_streaks,
    featured_writers = EXCLUDED.featured_writers,
    featured_curators = EXCLUDED.featured_curators,
    calculated_at = NOW();
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- DATA RETENTION CLEANUP
-- ═══════════════════════════════════════════════════════════════════════════

-- Delete old raw events (90 days)
CREATE OR REPLACE FUNCTION cleanup_old_events()
RETURNS INTEGER AS $$
DECLARE
  v_deleted INTEGER;
BEGIN
  DELETE FROM analytics_events
  WHERE created_at < NOW() - INTERVAL '90 days';
  
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;


-- Delete old user activity (1 year)
CREATE OR REPLACE FUNCTION cleanup_old_activity()
RETURNS INTEGER AS $$
DECLARE
  v_deleted INTEGER;
BEGIN
  DELETE FROM user_activity
  WHERE created_at < NOW() - INTERVAL '1 year';
  
  GET DIAGNOSTICS v_deleted = ROW_COUNT;
  RETURN v_deleted;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Real-time metrics
CREATE OR REPLACE VIEW realtime_metrics AS
SELECT
  (SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE created_at > NOW() - INTERVAL '15 minutes') as active_now,
  (SELECT COUNT(*) FROM analyses WHERE created_at > NOW() - INTERVAL '1 hour') as analyses_last_hour,
  (SELECT COALESCE(SUM(word_count), 0) FROM analyses WHERE created_at > NOW() - INTERVAL '1 hour') as words_last_hour,
  (SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE) as signups_today;


-- Latest daily metrics
CREATE OR REPLACE VIEW latest_metrics AS
SELECT * FROM daily_analytics
ORDER BY metric_date DESC
LIMIT 1;
