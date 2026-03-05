-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY PAYMENTS DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Stripe subscriptions, trials, and payment history.
-- 
-- CURRENCIES: CAD, GBP, EUR, AUD (NEVER USD)

-- ═══════════════════════════════════════════════════════════════════════════
-- SUBSCRIPTIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  
  -- Stripe references
  stripe_customer_id TEXT NOT NULL,
  stripe_subscription_id TEXT NOT NULL UNIQUE,
  
  -- Plan details
  tier TEXT NOT NULL CHECK (tier IN ('pro', 'curator', 'bundle')),
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


-- ═══════════════════════════════════════════════════════════════════════════
-- TRIALS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS trials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  
  -- Trial details
  trial_type TEXT NOT NULL DEFAULT 'pro',
  
  -- Dates
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ends_at TIMESTAMPTZ NOT NULL,
  
  -- How was trial started
  trigger TEXT NOT NULL CHECK (trigger IN (
    'manual',         -- User clicked "Start Trial"
    'auto_500_words', -- Auto-unlocked at 500 words
    'promo_code',     -- Used a promo code
    'referral'        -- Referred by another user
  )),
  
  -- Outcome
  converted_to_paid BOOLEAN DEFAULT FALSE,
  converted_at TIMESTAMPTZ,
  converted_to_tier TEXT,
  
  -- Metadata
  auto_unlock_word_count INTEGER,
  promo_code TEXT,
  referrer_user_id UUID,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trials_user ON trials(user_id);
CREATE INDEX idx_trials_ends_at ON trials(ends_at);


-- ═══════════════════════════════════════════════════════════════════════════
-- PAYMENT HISTORY
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS payment_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Stripe references
  stripe_invoice_id TEXT UNIQUE,
  stripe_payment_intent_id TEXT,
  stripe_charge_id TEXT,
  
  -- Payment details
  amount_cents INTEGER NOT NULL,
  currency TEXT NOT NULL CHECK (currency IN ('cad', 'gbp', 'eur', 'aud', 'nzd')),
  status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed', 'pending', 'refunded')),
  
  -- Subscription context
  subscription_id UUID REFERENCES subscriptions(id),
  tier TEXT,
  interval TEXT,
  
  -- Failure details
  failure_code TEXT,
  failure_message TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payment_history_user ON payment_history(user_id, created_at DESC);
CREATE INDEX idx_payment_history_stripe_invoice ON payment_history(stripe_invoice_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- STRIPE EVENTS LOG (Webhook audit)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS stripe_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  stripe_event_id TEXT UNIQUE NOT NULL,
  event_type TEXT NOT NULL,
  
  -- Related objects
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
  
  -- Raw event data
  payload JSONB NOT NULL,
  
  -- Processing
  processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMPTZ,
  error_message TEXT,
  
  -- Timestamp
  received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stripe_events_type ON stripe_events(event_type);
CREATE INDEX idx_stripe_events_received ON stripe_events(received_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- USER CURRENCY PREFERENCE
-- ═══════════════════════════════════════════════════════════════════════════

-- Add to users table (if not exists)
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_currency TEXT 
  CHECK (preferred_currency IN ('cad', 'gbp', 'eur', 'aud', 'nzd'));


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Get user's effective tier
CREATE OR REPLACE FUNCTION get_user_tier(p_user_id UUID)
RETURNS TABLE (
  tier TEXT,
  source TEXT,
  expires_at TIMESTAMPTZ,
  is_grace_period BOOLEAN
) AS $$
DECLARE
  v_sub subscriptions%ROWTYPE;
  v_trial trials%ROWTYPE;
BEGIN
  -- Check active subscription
  SELECT * INTO v_sub FROM subscriptions 
  WHERE user_id = p_user_id AND status = 'active';
  
  IF FOUND THEN
    RETURN QUERY SELECT 
      v_sub.tier, 
      'subscription'::TEXT, 
      v_sub.current_period_end, 
      FALSE;
    RETURN;
  END IF;
  
  -- Check grace period
  SELECT * INTO v_sub FROM subscriptions 
  WHERE user_id = p_user_id 
    AND status = 'past_due'
    AND grace_period_ends_at > NOW();
  
  IF FOUND THEN
    RETURN QUERY SELECT 
      v_sub.tier, 
      'grace_period'::TEXT, 
      v_sub.grace_period_ends_at, 
      TRUE;
    RETURN;
  END IF;
  
  -- Check active trial
  SELECT * INTO v_trial FROM trials 
  WHERE user_id = p_user_id 
    AND ends_at > NOW()
    AND converted_to_paid = FALSE;
  
  IF FOUND THEN
    RETURN QUERY SELECT 
      v_trial.trial_type, 
      'trial'::TEXT, 
      v_trial.ends_at, 
      FALSE;
    RETURN;
  END IF;
  
  -- Default to free
  RETURN QUERY SELECT 'free'::TEXT, 'default'::TEXT, NULL::TIMESTAMPTZ, FALSE;
END;
$$ LANGUAGE plpgsql;


-- Start trial for user
CREATE OR REPLACE FUNCTION start_trial(
  p_user_id UUID,
  p_trigger TEXT DEFAULT 'manual',
  p_word_count INTEGER DEFAULT NULL
)
RETURNS trials AS $$
DECLARE
  v_trial trials;
BEGIN
  -- Check if user already has active subscription
  IF EXISTS (SELECT 1 FROM subscriptions WHERE user_id = p_user_id AND status = 'active') THEN
    RAISE EXCEPTION 'User already has active subscription';
  END IF;
  
  -- Check if user already trialed
  IF EXISTS (SELECT 1 FROM trials WHERE user_id = p_user_id) THEN
    RAISE EXCEPTION 'User has already used trial';
  END IF;
  
  INSERT INTO trials (
    user_id, trial_type, ends_at, trigger, auto_unlock_word_count
  ) VALUES (
    p_user_id, 'pro', NOW() + INTERVAL '7 days', p_trigger, p_word_count
  )
  RETURNING * INTO v_trial;
  
  RETURN v_trial;
END;
$$ LANGUAGE plpgsql;


-- Handle payment failure (start grace period)
CREATE OR REPLACE FUNCTION handle_payment_failure(p_stripe_subscription_id TEXT)
RETURNS void AS $$
BEGIN
  UPDATE subscriptions
  SET status = 'past_due',
      payment_failed_at = NOW(),
      grace_period_ends_at = NOW() + INTERVAL '2 days'
  WHERE stripe_subscription_id = p_stripe_subscription_id;
END;
$$ LANGUAGE plpgsql;


-- Handle payment success (clear grace period)
CREATE OR REPLACE FUNCTION handle_payment_success(p_stripe_subscription_id TEXT)
RETURNS void AS $$
BEGIN
  UPDATE subscriptions
  SET status = 'active',
      payment_failed_at = NULL,
      grace_period_ends_at = NULL
  WHERE stripe_subscription_id = p_stripe_subscription_id;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Active subscribers
CREATE OR REPLACE VIEW active_subscribers AS
SELECT 
  s.user_id,
  u.email,
  s.tier,
  s.currency,
  s.amount_cents,
  s.interval,
  s.current_period_end,
  s.cancel_at_period_end
FROM subscriptions s
JOIN users u ON s.user_id = u.id
WHERE s.status = 'active'
ORDER BY s.created_at DESC;


-- Trial users
CREATE OR REPLACE VIEW active_trials AS
SELECT 
  t.user_id,
  u.email,
  t.trial_type,
  t.trigger,
  t.started_at,
  t.ends_at,
  t.ends_at - NOW() as time_remaining
FROM trials t
JOIN users u ON t.user_id = u.id
WHERE t.ends_at > NOW()
  AND t.converted_to_paid = FALSE
ORDER BY t.ends_at ASC;


-- Revenue summary by currency
CREATE OR REPLACE VIEW revenue_by_currency AS
SELECT 
  currency,
  COUNT(*) as subscriber_count,
  SUM(CASE WHEN interval = 'month' THEN amount_cents ELSE amount_cents / 12 END) as monthly_revenue_cents,
  SUM(CASE WHEN interval = 'year' THEN amount_cents ELSE amount_cents * 12 END) as annual_revenue_cents
FROM subscriptions
WHERE status = 'active'
GROUP BY currency;


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trials ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;

-- Users can view their own subscription
CREATE POLICY "Users can view own subscription" ON subscriptions
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own trial
CREATE POLICY "Users can view own trial" ON trials
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own payment history
CREATE POLICY "Users can view own payments" ON payment_history
  FOR SELECT USING (auth.uid() = user_id);
