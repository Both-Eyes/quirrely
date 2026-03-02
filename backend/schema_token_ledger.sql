-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY TOKEN LEDGER SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- Immutable ledger tracking all token generation and value changes.
-- Foundation for the self-sustaining token economy.
--
-- Token Generations:
--   Gen 0: Raw user input (feedstock)
--   Gen 1: Structured profile (LNCP output)
--   Gen 2: Explored variations (exercises, stances)
--   Gen 3: Behavioral patterns (streaks, consistency)
--   Gen 4: Social validation (Featured status)
--   Gen 5: Authority/permanence (Authority tier)
-- ═══════════════════════════════════════════════════════════════════════════


-- ═══════════════════════════════════════════════════════════════════════════
-- CORE LEDGER (Append-only, immutable)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS token_ledger (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Who
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- What happened
  event_type TEXT NOT NULL,  -- 'generation', 'upgrade', 'decay', 'destruction'
  
  -- Token generation transition
  gen_from INTEGER CHECK (gen_from >= 0 AND gen_from <= 5),
  gen_to INTEGER CHECK (gen_to >= 0 AND gen_to <= 5),
  
  -- Value change
  value_before NUMERIC(12, 4) NOT NULL,
  value_after NUMERIC(12, 4) NOT NULL,
  value_delta NUMERIC(12, 4) GENERATED ALWAYS AS (value_after - value_before) STORED,
  
  -- Context
  trigger_type TEXT NOT NULL,  -- What caused this event
  trigger_id TEXT,             -- Reference to the triggering entity
  metadata JSONB DEFAULT '{}',
  
  -- Geographic context
  country_code TEXT CHECK (country_code IN ('ca', 'uk', 'au', 'nz')),
  entry_domain TEXT,  -- Which domain user entered through
  
  -- Timestamp (immutable)
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for common queries
CREATE INDEX idx_token_ledger_user ON token_ledger(user_id, created_at DESC);
CREATE INDEX idx_token_ledger_event ON token_ledger(event_type, created_at DESC);
CREATE INDEX idx_token_ledger_gen ON token_ledger(gen_to, created_at DESC);
CREATE INDEX idx_token_ledger_country ON token_ledger(country_code, created_at DESC);
CREATE INDEX idx_token_ledger_date ON token_ledger(DATE(created_at));

-- Prevent updates and deletes (immutable)
CREATE OR REPLACE FUNCTION prevent_ledger_modification()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Token ledger is immutable. Updates and deletes are not allowed.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER token_ledger_immutable
BEFORE UPDATE OR DELETE ON token_ledger
FOR EACH ROW EXECUTE FUNCTION prevent_ledger_modification();


-- ═══════════════════════════════════════════════════════════════════════════
-- USER TOKEN PORTFOLIO (Materialized view, refreshed)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_token_portfolio (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  
  -- Current token holdings by generation
  gen_0_count INTEGER DEFAULT 0,  -- Raw inputs submitted
  gen_1_count INTEGER DEFAULT 0,  -- Profiles generated
  gen_2_count INTEGER DEFAULT 0,  -- Explorations completed
  gen_3_count INTEGER DEFAULT 0,  -- Behavioral milestones
  gen_4_count INTEGER DEFAULT 0,  -- Social validations
  gen_5_count INTEGER DEFAULT 0,  -- Authority achievements
  
  -- Aggregate value
  total_value NUMERIC(12, 4) DEFAULT 0,
  peak_value NUMERIC(12, 4) DEFAULT 0,
  
  -- Velocity metrics
  value_7d_delta NUMERIC(12, 4) DEFAULT 0,
  value_30d_delta NUMERIC(12, 4) DEFAULT 0,
  
  -- Health indicators
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  days_since_active INTEGER DEFAULT 0,
  
  -- Journey stage
  current_stage TEXT DEFAULT 'visitor',
  highest_stage TEXT DEFAULT 'visitor',
  
  -- Country
  country_code TEXT,
  entry_domain TEXT,
  
  -- Timestamps
  first_token_at TIMESTAMPTZ,
  last_token_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_portfolio_value ON user_token_portfolio(total_value DESC);
CREATE INDEX idx_portfolio_stage ON user_token_portfolio(current_stage);
CREATE INDEX idx_portfolio_country ON user_token_portfolio(country_code);


-- ═══════════════════════════════════════════════════════════════════════════
-- SYSTEM TOKEN METRICS (Aggregated, time-series)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS system_token_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  metric_timestamp TIMESTAMPTZ NOT NULL,
  granularity TEXT NOT NULL CHECK (granularity IN ('hourly', 'daily', 'weekly')),
  
  -- Token counts by generation
  gen_0_total BIGINT DEFAULT 0,
  gen_1_total BIGINT DEFAULT 0,
  gen_2_total BIGINT DEFAULT 0,
  gen_3_total BIGINT DEFAULT 0,
  gen_4_total BIGINT DEFAULT 0,
  gen_5_total BIGINT DEFAULT 0,
  
  -- Value metrics
  total_system_value NUMERIC(16, 4) DEFAULT 0,
  value_created NUMERIC(16, 4) DEFAULT 0,
  value_destroyed NUMERIC(16, 4) DEFAULT 0,
  net_value_delta NUMERIC(16, 4) DEFAULT 0,
  
  -- Flow metrics (tokens moving between generations)
  flow_0_to_1 INTEGER DEFAULT 0,
  flow_1_to_2 INTEGER DEFAULT 0,
  flow_1_to_3 INTEGER DEFAULT 0,
  flow_2_to_3 INTEGER DEFAULT 0,
  flow_3_to_4 INTEGER DEFAULT 0,
  flow_4_to_5 INTEGER DEFAULT 0,
  
  -- Decay/destruction
  decay_events INTEGER DEFAULT 0,
  destruction_events INTEGER DEFAULT 0,
  
  -- By country
  metrics_by_country JSONB DEFAULT '{}',
  
  -- Calculated
  token_velocity NUMERIC(12, 4),  -- Tokens moved per active user
  value_efficiency NUMERIC(8, 4), -- Value created per token
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(metric_timestamp, granularity)
);

CREATE INDEX idx_system_metrics_time ON system_token_metrics(metric_timestamp DESC);
CREATE INDEX idx_system_metrics_granularity ON system_token_metrics(granularity, metric_timestamp DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- FUNNEL METRICS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS funnel_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  metric_date DATE NOT NULL,
  country_code TEXT,  -- NULL for aggregate
  entry_type TEXT,    -- 'direct' or 'via_com'
  
  -- Stage counts
  visitors INTEGER DEFAULT 0,
  signups INTEGER DEFAULT 0,
  first_analysis INTEGER DEFAULT 0,
  hit_limit INTEGER DEFAULT 0,
  trial_started INTEGER DEFAULT 0,
  trial_converted INTEGER DEFAULT 0,
  subscribed INTEGER DEFAULT 0,
  featured_eligible INTEGER DEFAULT 0,
  featured_submitted INTEGER DEFAULT 0,
  featured_approved INTEGER DEFAULT 0,
  authority_achieved INTEGER DEFAULT 0,
  
  -- Conversion rates (calculated)
  signup_rate NUMERIC(5, 4),
  analysis_rate NUMERIC(5, 4),
  trial_start_rate NUMERIC(5, 4),
  trial_convert_rate NUMERIC(5, 4),
  featured_submit_rate NUMERIC(5, 4),
  featured_approve_rate NUMERIC(5, 4),
  
  -- Value at each stage
  avg_value_at_signup NUMERIC(12, 4),
  avg_value_at_trial NUMERIC(12, 4),
  avg_value_at_subscribe NUMERIC(12, 4),
  avg_value_at_featured NUMERIC(12, 4),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(metric_date, country_code, entry_type)
);

CREATE INDEX idx_funnel_date ON funnel_metrics(metric_date DESC);
CREATE INDEX idx_funnel_country ON funnel_metrics(country_code, metric_date DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- SIMULATION RUNS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS simulation_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Run configuration
  run_type TEXT NOT NULL CHECK (run_type IN ('master_test', 'scenario', 'calibration')),
  run_name TEXT,
  
  -- Parameters
  total_users INTEGER NOT NULL,
  simulation_days INTEGER NOT NULL,
  seed INTEGER,  -- For reproducibility
  parameters JSONB NOT NULL,
  
  -- Results summary
  results_summary JSONB,
  
  -- Comparison to baseline
  baseline_comparison JSONB,
  
  -- Prescriptive outputs
  opportunities JSONB DEFAULT '[]',
  watches JSONB DEFAULT '[]',
  risks JSONB DEFAULT '[]',
  
  -- Status
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error_message TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_simulation_runs_type ON simulation_runs(run_type, created_at DESC);
CREATE INDEX idx_simulation_runs_status ON simulation_runs(status);


-- ═══════════════════════════════════════════════════════════════════════════
-- SIMULATION USERS (Synthetic users for testing)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS simulation_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  run_id UUID NOT NULL REFERENCES simulation_runs(id) ON DELETE CASCADE,
  
  -- Synthetic user profile
  country_code TEXT NOT NULL,
  entry_type TEXT NOT NULL,  -- 'direct' or 'via_com'
  
  -- Journey tracking
  journey_stage TEXT DEFAULT 'visitor',
  stage_history JSONB DEFAULT '[]',
  
  -- Token state
  token_generation INTEGER DEFAULT 0,
  token_value NUMERIC(12, 4) DEFAULT 0,
  token_history JSONB DEFAULT '[]',
  
  -- Behavioral state
  days_active INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  stances_explored INTEGER DEFAULT 0,
  
  -- Outcome
  final_stage TEXT,
  final_value NUMERIC(12, 4),
  churned BOOLEAN DEFAULT FALSE,
  churn_day INTEGER,
  
  -- Simulation metadata
  created_day INTEGER DEFAULT 0,  -- Day in simulation when user arrived
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sim_users_run ON simulation_users(run_id);
CREATE INDEX idx_sim_users_stage ON simulation_users(run_id, journey_stage);
CREATE INDEX idx_sim_users_country ON simulation_users(run_id, country_code);


-- ═══════════════════════════════════════════════════════════════════════════
-- PRESCRIPTIVE ACTIONS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS prescriptive_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Source
  simulation_run_id UUID REFERENCES simulation_runs(id),
  generated_from TEXT NOT NULL,  -- 'simulation', 'real_data', 'anomaly_detection'
  
  -- Classification
  severity TEXT NOT NULL CHECK (severity IN ('opportunity', 'watch', 'risk')),
  category TEXT NOT NULL,  -- 'conversion', 'retention', 'value', 'velocity', 'funnel'
  
  -- The insight
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  
  -- Metrics
  current_value NUMERIC(12, 4),
  baseline_value NUMERIC(12, 4),
  delta_percent NUMERIC(8, 4),
  
  -- Affected scope
  country_code TEXT,  -- NULL for system-wide
  funnel_stage TEXT,
  token_generation INTEGER,
  
  -- Recommended action
  action_recommended TEXT NOT NULL,
  action_impact_estimate TEXT,
  action_effort_estimate TEXT CHECK (action_effort_estimate IN ('low', 'medium', 'high')),
  
  -- Status
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'acknowledged', 'in_progress', 'resolved', 'dismissed')),
  acknowledged_by UUID REFERENCES admin_users(id),
  acknowledged_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,
  resolution_notes TEXT,
  
  -- Priority (calculated: impact × urgency)
  priority_score INTEGER,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ  -- Actions can expire if not acted upon
);

CREATE INDEX idx_prescriptive_severity ON prescriptive_actions(severity, status, created_at DESC);
CREATE INDEX idx_prescriptive_status ON prescriptive_actions(status, created_at DESC);
CREATE INDEX idx_prescriptive_category ON prescriptive_actions(category, created_at DESC);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Record a token event
CREATE OR REPLACE FUNCTION record_token_event(
  p_user_id UUID,
  p_event_type TEXT,
  p_gen_from INTEGER,
  p_gen_to INTEGER,
  p_value_before NUMERIC,
  p_value_after NUMERIC,
  p_trigger_type TEXT,
  p_trigger_id TEXT DEFAULT NULL,
  p_metadata JSONB DEFAULT '{}',
  p_country_code TEXT DEFAULT NULL,
  p_entry_domain TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_event_id UUID;
BEGIN
  INSERT INTO token_ledger (
    user_id, event_type, gen_from, gen_to,
    value_before, value_after,
    trigger_type, trigger_id, metadata,
    country_code, entry_domain
  )
  VALUES (
    p_user_id, p_event_type, p_gen_from, p_gen_to,
    p_value_before, p_value_after,
    p_trigger_type, p_trigger_id, p_metadata,
    p_country_code, p_entry_domain
  )
  RETURNING id INTO v_event_id;
  
  -- Update portfolio (async in production, inline for simplicity)
  PERFORM update_user_portfolio(p_user_id);
  
  RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;


-- Update user portfolio from ledger
CREATE OR REPLACE FUNCTION update_user_portfolio(p_user_id UUID)
RETURNS void AS $$
BEGIN
  INSERT INTO user_token_portfolio (user_id, updated_at)
  VALUES (p_user_id, NOW())
  ON CONFLICT (user_id) DO UPDATE SET
    gen_0_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 0),
    gen_1_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 1),
    gen_2_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 2),
    gen_3_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 3),
    gen_4_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 4),
    gen_5_count = (SELECT COUNT(*) FROM token_ledger WHERE user_id = p_user_id AND gen_to = 5),
    total_value = (SELECT COALESCE(SUM(value_after), 0) FROM token_ledger WHERE user_id = p_user_id),
    last_token_at = NOW(),
    updated_at = NOW();
END;
$$ LANGUAGE plpgsql;


-- Get system token velocity (tokens/user/day)
CREATE OR REPLACE FUNCTION get_token_velocity(p_days INTEGER DEFAULT 7)
RETURNS NUMERIC AS $$
DECLARE
  v_events BIGINT;
  v_users BIGINT;
BEGIN
  SELECT COUNT(*), COUNT(DISTINCT user_id)
  INTO v_events, v_users
  FROM token_ledger
  WHERE created_at > NOW() - (p_days || ' days')::INTERVAL;
  
  IF v_users = 0 THEN
    RETURN 0;
  END IF;
  
  RETURN (v_events::NUMERIC / v_users::NUMERIC) / p_days;
END;
$$ LANGUAGE plpgsql;


-- Get funnel conversion rate between stages
CREATE OR REPLACE FUNCTION get_stage_conversion(
  p_from_stage TEXT,
  p_to_stage TEXT,
  p_days INTEGER DEFAULT 30
)
RETURNS NUMERIC AS $$
DECLARE
  v_from_count BIGINT;
  v_to_count BIGINT;
BEGIN
  SELECT COUNT(*) INTO v_from_count
  FROM user_token_portfolio
  WHERE highest_stage = p_from_stage
    AND last_token_at > NOW() - (p_days || ' days')::INTERVAL;
  
  SELECT COUNT(*) INTO v_to_count
  FROM user_token_portfolio
  WHERE highest_stage = p_to_stage
    AND last_token_at > NOW() - (p_days || ' days')::INTERVAL;
  
  IF v_from_count = 0 THEN
    RETURN 0;
  END IF;
  
  RETURN v_to_count::NUMERIC / v_from_count::NUMERIC;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Real-time system pulse
CREATE OR REPLACE VIEW system_pulse AS
SELECT
  (SELECT COUNT(*) FROM token_ledger WHERE created_at > NOW() - INTERVAL '1 hour') as events_last_hour,
  (SELECT COUNT(*) FROM token_ledger WHERE created_at > NOW() - INTERVAL '24 hours') as events_last_24h,
  (SELECT SUM(value_delta) FROM token_ledger WHERE created_at > NOW() - INTERVAL '24 hours') as value_created_24h,
  (SELECT get_token_velocity(7)) as velocity_7d,
  (SELECT COUNT(*) FROM user_token_portfolio WHERE current_streak > 0) as active_streaks,
  (SELECT COUNT(*) FROM user_token_portfolio WHERE days_since_active > 30) as at_risk_users,
  (SELECT AVG(total_value) FROM user_token_portfolio WHERE total_value > 0) as avg_user_value;


-- Latest prescriptive actions by severity
CREATE OR REPLACE VIEW latest_prescriptive_actions AS
SELECT * FROM prescriptive_actions
WHERE status IN ('new', 'acknowledged')
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY 
  CASE severity WHEN 'risk' THEN 1 WHEN 'watch' THEN 2 WHEN 'opportunity' THEN 3 END,
  priority_score DESC,
  created_at DESC
LIMIT 20;
