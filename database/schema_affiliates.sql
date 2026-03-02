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

