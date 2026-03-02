-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY SUBSCRIPTIONS & ADDONS SCHEMA v2.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Updated subscription system with:
-- - 7 tiers (free, pro, curator, featured_writer, featured_curator, 
--            authority_writer, authority_curator)
-- - Addons system (voice_style as cross-track enhancement)
-- - Tier OR addon access pattern support
--
-- This schema extends/replaces schema_payments.sql subscriptions table

-- ═══════════════════════════════════════════════════════════════════════════
-- DROP OLD CONSTRAINTS (if migrating)
-- ═══════════════════════════════════════════════════════════════════════════

-- ALTER TABLE subscriptions DROP CONSTRAINT IF EXISTS subscriptions_tier_check;


-- ═══════════════════════════════════════════════════════════════════════════
-- USER TIERS ENUM
-- ═══════════════════════════════════════════════════════════════════════════

DO $$ BEGIN
  CREATE TYPE user_tier AS ENUM (
    'free',
    'pro',               -- Writer track - Paid Tier 1
    'curator',           -- Reader track - Paid Tier 1
    'featured_writer',   -- Writer track - Paid Tier 2
    'featured_curator',  -- Reader track - Paid Tier 2
    'authority_writer',  -- Writer track - Paid Tier 3
    'authority_curator'  -- Reader track - Paid Tier 3
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;


-- ═══════════════════════════════════════════════════════════════════════════
-- USER ADDONS ENUM
-- ═══════════════════════════════════════════════════════════════════════════

DO $$ BEGIN
  CREATE TYPE user_addon AS ENUM (
    'voice_style'  -- Voice + Style analysis (cross-track)
  );
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;


-- ═══════════════════════════════════════════════════════════════════════════
-- SUBSCRIPTIONS TABLE (Updated)
-- ═══════════════════════════════════════════════════════════════════════════

-- If table exists, add new tier values
DO $$ BEGIN
  ALTER TABLE subscriptions 
    DROP CONSTRAINT IF EXISTS subscriptions_tier_check;
  
  ALTER TABLE subscriptions 
    ALTER COLUMN tier TYPE TEXT;
  
  ALTER TABLE subscriptions 
    ADD CONSTRAINT subscriptions_tier_check 
    CHECK (tier IN (
      'pro', 'curator', 'bundle',
      'featured_writer', 'featured_curator',
      'authority_writer', 'authority_curator'
    ));
EXCEPTION
  WHEN undefined_table THEN
    -- Table doesn't exist, create it
    CREATE TABLE subscriptions (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
      
      -- Stripe references
      stripe_customer_id TEXT NOT NULL,
      stripe_subscription_id TEXT NOT NULL UNIQUE,
      
      -- Plan details
      tier TEXT NOT NULL CHECK (tier IN (
        'pro', 'curator', 'bundle',
        'featured_writer', 'featured_curator',
        'authority_writer', 'authority_curator'
      )),
      status TEXT NOT NULL CHECK (status IN (
        'active', 'past_due', 'cancelled', 'unpaid', 'trialing', 'incomplete'
      )),
      
      -- Billing
      currency TEXT NOT NULL CHECK (currency IN ('cad', 'gbp', 'eur', 'aud', 'nzd')),
      amount_cents INTEGER NOT NULL,
      interval TEXT NOT NULL CHECK (interval IN ('month', 'year')),
      
      -- Period
      current_period_start TIMESTAMPTZ NOT NULL,
      current_period_end TIMESTAMPTZ NOT NULL,
      
      -- Cancellation
      cancel_at_period_end BOOLEAN DEFAULT FALSE,
      cancelled_at TIMESTAMPTZ,
      
      -- Grace period tracking
      payment_failed_at TIMESTAMPTZ,
      grace_period_ends_at TIMESTAMPTZ,
      
      -- Timestamps
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
    CREATE INDEX idx_subscriptions_stripe_sub ON subscriptions(stripe_subscription_id);
    CREATE INDEX idx_subscriptions_status ON subscriptions(status);
    CREATE INDEX idx_subscriptions_tier ON subscriptions(tier);
END $$;


-- ═══════════════════════════════════════════════════════════════════════════
-- USER ADDONS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_addons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Addon details
  addon TEXT NOT NULL CHECK (addon IN ('voice_style')),
  
  -- Stripe references (if purchased separately)
  stripe_subscription_id TEXT,
  stripe_product_id TEXT,
  
  -- Status
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
    'active', 'cancelled', 'expired', 'pending'
  )),
  
  -- How was it acquired
  source TEXT NOT NULL CHECK (source IN (
    'purchase',      -- Purchased separately
    'bundle',        -- Came with subscription bundle
    'promotion',     -- Promotional grant
    'grandfathered'  -- Existing user grant
  )),
  
  -- Period (for time-limited addons)
  starts_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ,  -- NULL = never expires
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure user can only have one of each addon
  UNIQUE(user_id, addon)
);

CREATE INDEX idx_user_addons_user ON user_addons(user_id);
CREATE INDEX idx_user_addons_addon ON user_addons(addon);
CREATE INDEX idx_user_addons_status ON user_addons(status);
CREATE INDEX idx_user_addons_active ON user_addons(user_id, addon) WHERE status = 'active';


-- ═══════════════════════════════════════════════════════════════════════════
-- USER EFFECTIVE TIER VIEW
-- ═══════════════════════════════════════════════════════════════════════════
-- Combines base subscription tier with any active addons

CREATE OR REPLACE VIEW user_effective_access AS
SELECT 
  u.id AS user_id,
  u.email,
  u.display_name,
  
  -- Effective tier
  COALESCE(s.tier, 'free') AS tier,
  s.status AS subscription_status,
  
  -- Tier level (for comparisons)
  CASE COALESCE(s.tier, 'free')
    WHEN 'free' THEN 0
    WHEN 'pro' THEN 1
    WHEN 'curator' THEN 1
    WHEN 'featured_writer' THEN 2
    WHEN 'featured_curator' THEN 2
    WHEN 'authority_writer' THEN 3
    WHEN 'authority_curator' THEN 3
    ELSE 0
  END AS tier_level,
  
  -- Track
  CASE 
    WHEN COALESCE(s.tier, 'free') IN ('pro', 'featured_writer', 'authority_writer') THEN 'writer'
    WHEN COALESCE(s.tier, 'free') IN ('curator', 'featured_curator', 'authority_curator') THEN 'curator'
    ELSE 'none'
  END AS track,
  
  -- Active addons as array
  COALESCE(
    (SELECT ARRAY_AGG(ua.addon) 
     FROM user_addons ua 
     WHERE ua.user_id = u.id 
       AND ua.status = 'active'
       AND (ua.expires_at IS NULL OR ua.expires_at > NOW())
    ),
    ARRAY[]::TEXT[]
  ) AS addons,
  
  -- Specific addon flags
  EXISTS (
    SELECT 1 FROM user_addons ua 
    WHERE ua.user_id = u.id 
      AND ua.addon = 'voice_style' 
      AND ua.status = 'active'
      AND (ua.expires_at IS NULL OR ua.expires_at > NOW())
  ) AS has_voice_style,
  
  -- Subscription period
  s.current_period_start,
  s.current_period_end,
  s.cancel_at_period_end

FROM users u
LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status IN ('active', 'trialing')
WHERE u.status = 'active';


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Get user's effective tier
CREATE OR REPLACE FUNCTION get_user_tier(p_user_id UUID)
RETURNS TEXT AS $$
BEGIN
  RETURN COALESCE(
    (SELECT tier FROM subscriptions 
     WHERE user_id = p_user_id AND status IN ('active', 'trialing')
     LIMIT 1),
    'free'
  );
END;
$$ LANGUAGE plpgsql;


-- Get user's active addons
CREATE OR REPLACE FUNCTION get_user_addons(p_user_id UUID)
RETURNS TEXT[] AS $$
BEGIN
  RETURN COALESCE(
    (SELECT ARRAY_AGG(addon) 
     FROM user_addons 
     WHERE user_id = p_user_id 
       AND status = 'active'
       AND (expires_at IS NULL OR expires_at > NOW())
    ),
    ARRAY[]::TEXT[]
  );
END;
$$ LANGUAGE plpgsql;


-- Check if user has specific addon
CREATE OR REPLACE FUNCTION user_has_addon(p_user_id UUID, p_addon TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM user_addons 
    WHERE user_id = p_user_id 
      AND addon = p_addon 
      AND status = 'active'
      AND (expires_at IS NULL OR expires_at > NOW())
  );
END;
$$ LANGUAGE plpgsql;


-- Check feature access (tier OR addon pattern)
CREATE OR REPLACE FUNCTION check_feature_access(
  p_user_id UUID,
  p_required_tiers TEXT[],
  p_required_addon TEXT DEFAULT NULL,
  p_tier_or_addon BOOLEAN DEFAULT FALSE
)
RETURNS BOOLEAN AS $$
DECLARE
  v_tier TEXT;
  v_has_addon BOOLEAN;
  v_has_tier BOOLEAN;
BEGIN
  -- Get user's tier
  v_tier := get_user_tier(p_user_id);
  
  -- Check tier requirement
  v_has_tier := v_tier = ANY(p_required_tiers);
  
  -- Check addon requirement
  IF p_required_addon IS NOT NULL THEN
    v_has_addon := user_has_addon(p_user_id, p_required_addon);
  ELSE
    v_has_addon := FALSE;
  END IF;
  
  -- Evaluate based on tier_or_addon mode
  IF p_tier_or_addon THEN
    RETURN v_has_tier OR v_has_addon;
  ELSE
    -- Both must be satisfied if both specified
    IF p_required_addon IS NOT NULL AND NOT v_has_addon THEN
      RETURN FALSE;
    END IF;
    RETURN v_has_tier;
  END IF;
END;
$$ LANGUAGE plpgsql;


-- Grant addon to user
CREATE OR REPLACE FUNCTION grant_addon(
  p_user_id UUID,
  p_addon TEXT,
  p_source TEXT DEFAULT 'purchase',
  p_expires_at TIMESTAMPTZ DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_addon_id UUID;
BEGIN
  INSERT INTO user_addons (user_id, addon, source, expires_at)
  VALUES (p_user_id, p_addon, p_source, p_expires_at)
  ON CONFLICT (user_id, addon) DO UPDATE
  SET status = 'active',
      source = EXCLUDED.source,
      expires_at = EXCLUDED.expires_at,
      updated_at = NOW()
  RETURNING id INTO v_addon_id;
  
  RETURN v_addon_id;
END;
$$ LANGUAGE plpgsql;


-- Revoke addon from user
CREATE OR REPLACE FUNCTION revoke_addon(p_user_id UUID, p_addon TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE user_addons
  SET status = 'cancelled',
      updated_at = NOW()
  WHERE user_id = p_user_id AND addon = p_addon;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE user_addons ENABLE ROW LEVEL SECURITY;

-- Users can view their own addons
CREATE POLICY "Users can view own addons" ON user_addons
  FOR SELECT USING (auth.uid() = user_id);

-- Only service role can modify addons
CREATE POLICY "Service role can manage addons" ON user_addons
  FOR ALL USING (auth.role() = 'service_role');


-- ═══════════════════════════════════════════════════════════════════════════
-- TRIGGERS
-- ═══════════════════════════════════════════════════════════════════════════

-- Update timestamp on addon changes
CREATE OR REPLACE FUNCTION update_addon_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_user_addons_updated ON user_addons;
CREATE TRIGGER tr_user_addons_updated
  BEFORE UPDATE ON user_addons
  FOR EACH ROW
  EXECUTE FUNCTION update_addon_timestamp();


-- ═══════════════════════════════════════════════════════════════════════════
-- EXAMPLE QUERIES
-- ═══════════════════════════════════════════════════════════════════════════

-- Get full user access profile:
-- SELECT * FROM user_effective_access WHERE user_id = 'xxx';

-- Check if user can access authority_hub (tier OR addon):
-- SELECT check_feature_access(
--   'user-uuid', 
--   ARRAY['featured_writer', 'featured_curator', 'authority_writer', 'authority_curator'],
--   'voice_style',
--   TRUE  -- tier_or_addon
-- );

-- Grant voice_style to a user:
-- SELECT grant_addon('user-uuid', 'voice_style', 'purchase');

-- Get user with addons:
-- SELECT 
--   u.id, u.email,
--   get_user_tier(u.id) AS tier,
--   get_user_addons(u.id) AS addons
-- FROM users u WHERE u.id = 'xxx';
