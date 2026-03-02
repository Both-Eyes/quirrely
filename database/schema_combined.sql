-- SENTENSE DATABASE SCHEMA - PostgreSQL
-- Compatible with: Supabase, Railway, Neon, any PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login_at TIMESTAMP WITH TIME ZONE,
  display_name VARCHAR(50),
  avatar_url VARCHAR(500),
  country CHAR(2),
  city VARCHAR(100),
  subscription_tier VARCHAR(20) DEFAULT 'free',
  subscription_status VARCHAR(20) DEFAULT 'active',
  subscription_started_at TIMESTAMP WITH TIME ZONE,
  subscription_ends_at TIMESTAMP WITH TIME ZONE,
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  email_notifications BOOLEAN DEFAULT TRUE,
  public_profile BOOLEAN DEFAULT FALSE
);

-- WRITING PROFILES
CREATE TABLE writing_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id VARCHAR(100),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  score_assertive INTEGER, score_minimal INTEGER, score_poetic INTEGER,
  score_dense INTEGER, score_conversational INTEGER, score_formal INTEGER,
  score_balanced INTEGER, score_longform INTEGER, score_interrogative INTEGER,
  score_hedged INTEGER, score_open INTEGER, score_closed INTEGER,
  score_stance_balanced INTEGER, score_contradictory INTEGER,
  input_text TEXT, input_word_count INTEGER
);

-- FEATURED SUBMISSIONS
CREATE TABLE featured_submissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  sample TEXT NOT NULL,
  word_count INTEGER,
  display_name VARCHAR(50) NOT NULL,
  bio VARCHAR(150),
  link_linkedin VARCHAR(255),
  link_newsletter VARCHAR(255),
  link_facebook VARCHAR(255),
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  country CHAR(2) NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  featured_week DATE,
  permission_feature BOOLEAN DEFAULT TRUE,
  permission_profile BOOLEAN DEFAULT TRUE,
  permission_country BOOLEAN DEFAULT TRUE
);

-- FEATURED HISTORY
CREATE TABLE featured_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  submission_id UUID REFERENCES featured_submissions(id),
  featured_week DATE NOT NULL,
  display_name VARCHAR(50) NOT NULL,
  sample TEXT NOT NULL,
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  country CHAR(2) NOT NULL,
  bio VARCHAR(150),
  link_linkedin VARCHAR(255),
  link_newsletter VARCHAR(255),
  link_facebook VARCHAR(255)
);

-- NEWSLETTER
CREATE TABLE newsletter_subscribers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'active',
  country CHAR(2),
  source VARCHAR(50)
);

-- SESSIONS
CREATE TABLE sessions (
  id VARCHAR(100) PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  country CHAR(2),
  referrer VARCHAR(500),
  utm_source VARCHAR(100),
  utm_medium VARCHAR(100),
  utm_campaign VARCHAR(100),
  test_started BOOLEAN DEFAULT FALSE,
  test_completed BOOLEAN DEFAULT FALSE,
  signed_up BOOLEAN DEFAULT FALSE,
  converted_pro BOOLEAN DEFAULT FALSE
);

-- INDEXES
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
CREATE INDEX idx_profiles_user ON writing_profiles(user_id);
CREATE INDEX idx_submissions_status ON featured_submissions(status);
CREATE INDEX idx_submissions_week ON featured_submissions(featured_week);
CREATE INDEX idx_featured_week ON featured_history(featured_week);
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

-- ═══════════════════════════════════════════════════════════════
-- AFFILIATE SCHEMA
-- PostgreSQL (Supabase/Railway/Neon compatible)
-- ═══════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────────────────────────
-- RETAILERS
-- ───────────────────────────────────────────────────────────────
CREATE TABLE affiliate_retailers (
  id SERIAL PRIMARY KEY,
  country_code CHAR(2) NOT NULL UNIQUE,
  retailer_name VARCHAR(50) NOT NULL,
  retailer_slug VARCHAR(50) NOT NULL,
  affiliate_network VARCHAR(50),
  affiliate_id VARCHAR(100),
  base_url VARCHAR(255) NOT NULL,
  search_url_template VARCHAR(500),
  product_url_template VARCHAR(500),
  commission_rate DECIMAL(4,3) DEFAULT 0.060,
  currency CHAR(3) DEFAULT 'USD',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed retailers
INSERT INTO affiliate_retailers (country_code, retailer_name, retailer_slug, affiliate_network, base_url, commission_rate, currency) VALUES
('CA', 'Indigo', 'indigo', 'rakuten', 'https://www.indigo.ca', 0.060, 'CAD'),
('UK', 'Waterstones', 'waterstones', 'awin', 'https://www.waterstones.com', 0.060, 'GBP'),
('AU', 'Booktopia', 'booktopia', 'booktopia', 'https://www.booktopia.com.au', 0.070, 'AUD'),
('NZ', 'Mighty Ape', 'mightyape', 'mightyape', 'https://www.mightyape.co.nz', 0.060, 'NZD');

-- ───────────────────────────────────────────────────────────────
-- BOOKS (Curated Catalog)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE affiliate_books (
  id SERIAL PRIMARY KEY,
  isbn VARCHAR(20) NOT NULL UNIQUE,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  hook VARCHAR(100),  -- Short marketing copy
  cover_url VARCHAR(500),
  year_published INTEGER,
  price_tier CHAR(1) DEFAULT 'M',  -- L, M, H
  
  -- Profile matching
  primary_profile VARCHAR(20),
  primary_stance VARCHAR(20),
  rank_in_combo INTEGER DEFAULT 1,  -- 1=hero, 2=alt1, 3=alt2
  
  -- Metadata
  is_active BOOLEAN DEFAULT TRUE,
  click_count INTEGER DEFAULT 0,
  conversion_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_books_profile ON affiliate_books(primary_profile, primary_stance);
CREATE INDEX idx_books_isbn ON affiliate_books(isbn);

-- ───────────────────────────────────────────────────────────────
-- AFFILIATE CLICKS (Tracking)
-- ───────────────────────────────────────────────────────────────
CREATE TABLE affiliate_clicks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Who clicked
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  session_id VARCHAR(100),
  
  -- What was clicked
  book_id INTEGER REFERENCES affiliate_books(id),
  isbn VARCHAR(20),
  
  -- Context
  country_code CHAR(2),
  retailer_id INTEGER REFERENCES affiliate_retailers(id),
  profile VARCHAR(20),
  stance VARCHAR(20),
  source VARCHAR(50),  -- test_results, blog, newsletter, profile, featured
  
  -- Tracking
  clicked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Conversion (updated via webhook)
  converted BOOLEAN DEFAULT FALSE,
  converted_at TIMESTAMP WITH TIME ZONE,
  order_value DECIMAL(10,2),
  commission_earned DECIMAL(10,2)
);

CREATE INDEX idx_clicks_date ON affiliate_clicks(clicked_at);
CREATE INDEX idx_clicks_book ON affiliate_clicks(book_id);
CREATE INDEX idx_clicks_user ON affiliate_clicks(user_id);
CREATE INDEX idx_clicks_source ON affiliate_clicks(source);

-- ───────────────────────────────────────────────────────────────
-- DAILY AFFILIATE STATS
-- ───────────────────────────────────────────────────────────────
CREATE TABLE affiliate_daily_stats (
  date DATE PRIMARY KEY,
  
  -- Impressions (book recommendation views)
  impressions INTEGER DEFAULT 0,
  
  -- Clicks
  total_clicks INTEGER DEFAULT 0,
  clicks_ca INTEGER DEFAULT 0,
  clicks_uk INTEGER DEFAULT 0,
  clicks_au INTEGER DEFAULT 0,
  clicks_nz INTEGER DEFAULT 0,
  
  -- By source
  clicks_test_results INTEGER DEFAULT 0,
  clicks_blog INTEGER DEFAULT 0,
  clicks_newsletter INTEGER DEFAULT 0,
  clicks_profile INTEGER DEFAULT 0,
  clicks_featured INTEGER DEFAULT 0,
  
  -- Conversions
  conversions INTEGER DEFAULT 0,
  total_order_value DECIMAL(12,2) DEFAULT 0,
  total_commission DECIMAL(10,2) DEFAULT 0,
  
  -- Rates
  ctr DECIMAL(5,4),  -- Click-through rate
  conversion_rate DECIMAL(5,4),
  avg_commission DECIMAL(8,2),
  
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ───────────────────────────────────────────────────────────────
-- TOP PERFORMING BOOKS VIEW
-- ───────────────────────────────────────────────────────────────
CREATE VIEW affiliate_top_books AS
SELECT 
  b.isbn,
  b.title,
  b.author,
  b.primary_profile,
  b.primary_stance,
  b.click_count,
  b.conversion_count,
  CASE WHEN b.click_count > 0 
       THEN b.conversion_count::DECIMAL / b.click_count 
       ELSE 0 END as conversion_rate,
  SUM(c.commission_earned) as total_commission
FROM affiliate_books b
LEFT JOIN affiliate_clicks c ON b.id = c.book_id AND c.converted = TRUE
GROUP BY b.id
ORDER BY b.click_count DESC;

-- ───────────────────────────────────────────────────────────────
-- FUNCTIONS
-- ───────────────────────────────────────────────────────────────

-- Record a click
CREATE OR REPLACE FUNCTION record_affiliate_click(
  p_isbn VARCHAR,
  p_country CHAR(2),
  p_profile VARCHAR,
  p_stance VARCHAR,
  p_source VARCHAR,
  p_user_id UUID DEFAULT NULL,
  p_session_id VARCHAR DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  v_click_id UUID;
  v_book_id INTEGER;
  v_retailer_id INTEGER;
BEGIN
  -- Get book ID
  SELECT id INTO v_book_id FROM affiliate_books WHERE isbn = p_isbn;
  
  -- Get retailer ID
  SELECT id INTO v_retailer_id FROM affiliate_retailers WHERE country_code = p_country;
  
  -- Insert click
  INSERT INTO affiliate_clicks (
    user_id, session_id, book_id, isbn, country_code, 
    retailer_id, profile, stance, source
  ) VALUES (
    p_user_id, p_session_id, v_book_id, p_isbn, p_country,
    v_retailer_id, p_profile, p_stance, p_source
  ) RETURNING id INTO v_click_id;
  
  -- Update book click count
  IF v_book_id IS NOT NULL THEN
    UPDATE affiliate_books SET click_count = click_count + 1 WHERE id = v_book_id;
  END IF;
  
  RETURN v_click_id;
END;
$$ LANGUAGE plpgsql;

-- Aggregate daily stats (run at end of day)
CREATE OR REPLACE FUNCTION aggregate_affiliate_daily_stats(target_date DATE)
RETURNS void AS $$
BEGIN
  INSERT INTO affiliate_daily_stats (
    date, total_clicks,
    clicks_ca, clicks_uk, clicks_au, clicks_nz,
    clicks_test_results, clicks_blog, clicks_newsletter, clicks_profile, clicks_featured,
    conversions, total_order_value, total_commission
  )
  SELECT
    target_date,
    COUNT(*),
    COUNT(*) FILTER (WHERE country_code = 'CA'),
    COUNT(*) FILTER (WHERE country_code = 'UK'),
    COUNT(*) FILTER (WHERE country_code = 'AU'),
    COUNT(*) FILTER (WHERE country_code = 'NZ'),
    COUNT(*) FILTER (WHERE source = 'test_results'),
    COUNT(*) FILTER (WHERE source = 'blog'),
    COUNT(*) FILTER (WHERE source = 'newsletter'),
    COUNT(*) FILTER (WHERE source = 'profile'),
    COUNT(*) FILTER (WHERE source = 'featured'),
    COUNT(*) FILTER (WHERE converted = TRUE),
    COALESCE(SUM(order_value) FILTER (WHERE converted = TRUE), 0),
    COALESCE(SUM(commission_earned) FILTER (WHERE converted = TRUE), 0)
  FROM affiliate_clicks
  WHERE DATE(clicked_at) = target_date
  ON CONFLICT (date) DO UPDATE SET
    total_clicks = EXCLUDED.total_clicks,
    clicks_ca = EXCLUDED.clicks_ca,
    clicks_uk = EXCLUDED.clicks_uk,
    clicks_au = EXCLUDED.clicks_au,
    clicks_nz = EXCLUDED.clicks_nz,
    clicks_test_results = EXCLUDED.clicks_test_results,
    clicks_blog = EXCLUDED.clicks_blog,
    clicks_newsletter = EXCLUDED.clicks_newsletter,
    clicks_profile = EXCLUDED.clicks_profile,
    clicks_featured = EXCLUDED.clicks_featured,
    conversions = EXCLUDED.conversions,
    total_order_value = EXCLUDED.total_order_value,
    total_commission = EXCLUDED.total_commission,
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

