-- ═══════════════════════════════════════════════════════════════════════════
-- WORD POOL SYSTEM UPDATE MIGRATION
-- Transition to new word allocation structure:
-- Anonymous: 50/day, Free: 250/day, Pro: 20k/month, Partnership: 10k+10k shared
-- ═══════════════════════════════════════════════════════════════════════════

-- Create new word usage tracking tables
CREATE TABLE IF NOT EXISTS user_word_usage (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    usage_date DATE NOT NULL,
    pool_type TEXT DEFAULT 'personal', -- 'personal', 'shared'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, usage_date, pool_type)
);

-- Anonymous user word tracking (by session)
CREATE TABLE IF NOT EXISTS anonymous_word_usage (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    usage_date DATE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, usage_date)
);

-- Update existing partnership word pools to new allocation
UPDATE writing_partnerships 
SET shared_creative_space = 20000,  -- Down from 25000
    initiator_solo_space_remaining = 10000,  -- Down from 12500  
    partner_solo_space_remaining = 10000     -- Down from 12500
WHERE status = 'active' AND shared_creative_space = 25000;

-- Add usage tracking columns to partnerships if not exists
ALTER TABLE writing_partnerships 
ADD COLUMN IF NOT EXISTS monthly_reset_date DATE DEFAULT DATE_TRUNC('month', NOW());

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_word_usage_date 
ON user_word_usage(user_id, usage_date);

CREATE INDEX IF NOT EXISTS idx_user_word_usage_pool_type 
ON user_word_usage(user_id, pool_type, usage_date);

CREATE INDEX IF NOT EXISTS idx_anonymous_word_usage_date 
ON anonymous_word_usage(session_id, usage_date);

CREATE INDEX IF NOT EXISTS idx_anonymous_word_usage_ip_date 
ON anonymous_word_usage(ip_address, usage_date);

-- ═══════════════════════════════════════════════════════════════════════════
-- USAGE ANALYTICS VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- View for daily usage analytics
CREATE OR REPLACE VIEW daily_usage_analytics AS
SELECT 
    CASE 
        WHEN u.subscription_tier = 'pro' AND wp.id IS NOT NULL THEN 'partnership'
        WHEN u.subscription_tier IS NULL THEN 'anonymous' 
        ELSE COALESCE(u.subscription_tier, 'free')
    END as effective_tier,
    usage_date,
    COUNT(DISTINCT uwu.user_id) as active_users,
    SUM(uwu.word_count) as total_words_used,
    AVG(uwu.word_count) as avg_words_per_user,
    -- Usage by tier limits
    COUNT(CASE WHEN uwu.word_count >= 45 AND u.subscription_tier IS NULL THEN 1 END) as anon_near_limit,
    COUNT(CASE WHEN uwu.word_count >= 200 AND u.subscription_tier = 'free' THEN 1 END) as free_near_limit
FROM user_word_usage uwu
JOIN users u ON uwu.user_id = u.id
LEFT JOIN writing_partnerships wp ON (wp.initiator_user_id = u.id OR wp.partner_user_id = u.id) 
                                  AND wp.status = 'active'
WHERE usage_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY effective_tier, usage_date
ORDER BY usage_date DESC, effective_tier;

-- View for conversion pressure tracking  
CREATE OR REPLACE VIEW conversion_pressure_analytics AS
SELECT 
    usage_date,
    tier,
    COUNT(*) as users_near_limit,
    COUNT(*) * 100.0 / total_users as pressure_percentage
FROM (
    SELECT 
        uwu.usage_date,
        CASE 
            WHEN u.subscription_tier IS NULL THEN 'anonymous'
            WHEN u.subscription_tier = 'free' THEN 'free'
            ELSE 'pro'
        END as tier,
        uwu.word_count,
        COUNT(*) OVER (PARTITION BY uwu.usage_date, 
                      CASE WHEN u.subscription_tier IS NULL THEN 'anonymous'
                           WHEN u.subscription_tier = 'free' THEN 'free'
                           ELSE 'pro'
                      END) as total_users
    FROM user_word_usage uwu
    JOIN users u ON uwu.user_id = u.id
    WHERE uwu.usage_date >= CURRENT_DATE - INTERVAL '7 days'
) usage_data
WHERE 
    (tier = 'anonymous' AND word_count >= 40) OR  -- 80% of 50
    (tier = 'free' AND word_count >= 200) OR      -- 80% of 250
    (tier = 'pro' AND word_count >= 16000)        -- 80% of 20000/month ≈ 650/day
GROUP BY usage_date, tier, total_users
ORDER BY usage_date DESC, tier;

-- ═══════════════════════════════════════════════════════════════════════════
-- RATE LIMITING FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to check if user can use words
CREATE OR REPLACE FUNCTION can_user_use_words(
    p_user_id TEXT,
    p_requested_words INTEGER,
    p_session_id TEXT DEFAULT NULL
) RETURNS TABLE(
    allowed BOOLEAN,
    remaining INTEGER,
    tier TEXT,
    limit_type TEXT,
    reason TEXT
) AS $$
DECLARE
    v_tier TEXT;
    v_daily_used INTEGER := 0;
    v_monthly_used INTEGER := 0;
    v_daily_limit INTEGER;
    v_monthly_limit INTEGER;
    v_has_partnership BOOLEAN := FALSE;
    v_personal_remaining INTEGER;
    v_shared_remaining INTEGER;
BEGIN
    -- Determine user tier
    IF p_user_id IS NULL THEN
        v_tier := 'anonymous';
        -- Get today's usage for this session
        SELECT COALESCE(SUM(word_count), 0) INTO v_daily_used
        FROM anonymous_word_usage 
        WHERE session_id = p_session_id AND usage_date = CURRENT_DATE;
        v_daily_limit := 50;
        
        RETURN QUERY SELECT 
            (v_daily_used + p_requested_words <= v_daily_limit),
            (v_daily_limit - v_daily_used),
            v_tier,
            'daily'::TEXT,
            CASE WHEN v_daily_used + p_requested_words > v_daily_limit 
                 THEN 'Daily limit exceeded' 
                 ELSE 'OK' END;
        RETURN;
    END IF;
    
    -- Check for partnership
    SELECT COUNT(*) > 0 INTO v_has_partnership
    FROM writing_partnerships 
    WHERE (initiator_user_id = p_user_id OR partner_user_id = p_user_id) 
      AND status = 'active';
    
    -- Get user subscription tier
    SELECT COALESCE(subscription_tier, 'free') INTO v_tier
    FROM users WHERE id = p_user_id;
    
    IF v_has_partnership THEN
        v_tier := 'partnership';
    END IF;
    
    -- Get current usage
    SELECT COALESCE(SUM(word_count), 0) INTO v_monthly_used
    FROM user_word_usage 
    WHERE user_id = p_user_id 
      AND usage_date >= DATE_TRUNC('month', CURRENT_DATE)
      AND pool_type = 'personal';
      
    -- Apply tier-specific logic
    CASE v_tier
        WHEN 'free' THEN
            SELECT COALESCE(SUM(word_count), 0) INTO v_daily_used
            FROM user_word_usage 
            WHERE user_id = p_user_id AND usage_date = CURRENT_DATE;
            v_daily_limit := 250;
            
            RETURN QUERY SELECT 
                (v_daily_used + p_requested_words <= v_daily_limit),
                (v_daily_limit - v_daily_used),
                v_tier,
                'daily'::TEXT,
                CASE WHEN v_daily_used + p_requested_words > v_daily_limit 
                     THEN 'Daily limit exceeded' 
                     ELSE 'OK' END;
                     
        WHEN 'pro' THEN
            v_monthly_limit := 20000;
            
            RETURN QUERY SELECT 
                (v_monthly_used + p_requested_words <= v_monthly_limit),
                (v_monthly_limit - v_monthly_used),
                v_tier,
                'monthly'::TEXT,
                CASE WHEN v_monthly_used + p_requested_words > v_monthly_limit 
                     THEN 'Monthly limit exceeded' 
                     ELSE 'OK' END;
                     
        WHEN 'partnership' THEN
            -- Complex partnership logic
            v_personal_remaining := 10000 - v_monthly_used;
            
            -- Get shared pool remaining
            SELECT (shared_creative_space - shared_space_used) INTO v_shared_remaining
            FROM writing_partnerships 
            WHERE (initiator_user_id = p_user_id OR partner_user_id = p_user_id) 
              AND status = 'active'
            LIMIT 1;
            
            RETURN QUERY SELECT 
                (p_requested_words <= v_personal_remaining + COALESCE(v_shared_remaining, 0)),
                (v_personal_remaining + COALESCE(v_shared_remaining, 0)),
                v_tier,
                'monthly'::TEXT,
                CASE WHEN p_requested_words > v_personal_remaining + COALESCE(v_shared_remaining, 0)
                     THEN 'Partnership word limit exceeded' 
                     ELSE 'OK' END;
                     
        WHEN 'authority' THEN
            v_monthly_limit := 50000;
            
            RETURN QUERY SELECT 
                (v_monthly_used + p_requested_words <= v_monthly_limit),
                (v_monthly_limit - v_monthly_used),
                v_tier,
                'monthly'::TEXT,
                'OK'::TEXT;  -- Authority users rarely hit limits
                
        ELSE
            -- Default to free tier
            RETURN QUERY SELECT FALSE, 0, 'unknown'::TEXT, 'error'::TEXT, 'Invalid tier'::TEXT;
    END CASE;
    
END;
$$ LANGUAGE plpgsql;

-- Function to record word usage
CREATE OR REPLACE FUNCTION record_word_usage(
    p_user_id TEXT,
    p_word_count INTEGER,
    p_pool_type TEXT DEFAULT 'personal',
    p_session_id TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    IF p_user_id IS NULL THEN
        -- Record anonymous usage
        INSERT INTO anonymous_word_usage (session_id, word_count, usage_date)
        VALUES (p_session_id, p_word_count, CURRENT_DATE)
        ON CONFLICT (session_id, usage_date) 
        DO UPDATE SET 
            word_count = anonymous_word_usage.word_count + EXCLUDED.word_count,
            updated_at = NOW();
    ELSE
        -- Record authenticated usage
        INSERT INTO user_word_usage (user_id, word_count, usage_date, pool_type)
        VALUES (p_user_id, p_word_count, CURRENT_DATE, p_pool_type)
        ON CONFLICT (user_id, usage_date, pool_type)
        DO UPDATE SET 
            word_count = user_word_usage.word_count + EXCLUDED.word_count,
            updated_at = NOW();
            
        -- Update partnership shared pool if needed
        IF p_pool_type = 'shared' THEN
            UPDATE writing_partnerships 
            SET shared_space_used = shared_space_used + p_word_count
            WHERE (initiator_user_id = p_user_id OR partner_user_id = p_user_id) 
              AND status = 'active';
        END IF;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- META/OBSERVERS INTEGRATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to get conversion pressure metrics
CREATE OR REPLACE FUNCTION get_conversion_pressure_metrics()
RETURNS TABLE(
    tier TEXT,
    users_near_limit INTEGER,
    total_tier_users INTEGER,
    pressure_percentage NUMERIC,
    avg_usage_percentage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tier_data.tier,
        tier_data.near_limit_count,
        tier_data.total_count,
        ROUND((tier_data.near_limit_count::NUMERIC / tier_data.total_count) * 100, 2),
        ROUND(tier_data.avg_usage, 2)
    FROM (
        SELECT 
            CASE 
                WHEN u.subscription_tier IS NULL THEN 'anonymous'
                WHEN u.subscription_tier = 'free' THEN 'free' 
                WHEN u.subscription_tier = 'pro' AND wp.id IS NULL THEN 'pro'
                WHEN u.subscription_tier = 'pro' AND wp.id IS NOT NULL THEN 'partnership'
                ELSE u.subscription_tier
            END as tier,
            COUNT(*) as total_count,
            COUNT(CASE 
                WHEN (u.subscription_tier IS NULL AND COALESCE(daily_usage.word_count, 0) >= 40) OR
                     (u.subscription_tier = 'free' AND COALESCE(daily_usage.word_count, 0) >= 200) OR
                     (u.subscription_tier = 'pro' AND COALESCE(monthly_usage.word_count, 0) >= 16000)
                THEN 1 END) as near_limit_count,
            AVG(
                CASE 
                    WHEN u.subscription_tier IS NULL 
                    THEN COALESCE(daily_usage.word_count, 0) / 50.0 * 100
                    WHEN u.subscription_tier = 'free' 
                    THEN COALESCE(daily_usage.word_count, 0) / 250.0 * 100
                    WHEN u.subscription_tier = 'pro' 
                    THEN COALESCE(monthly_usage.word_count, 0) / 20000.0 * 100
                    ELSE 0
                END
            ) as avg_usage
        FROM users u
        LEFT JOIN writing_partnerships wp ON (wp.initiator_user_id = u.id OR wp.partner_user_id = u.id) 
                                          AND wp.status = 'active'
        LEFT JOIN (
            SELECT user_id, SUM(word_count) as word_count
            FROM user_word_usage 
            WHERE usage_date = CURRENT_DATE
            GROUP BY user_id
        ) daily_usage ON u.id = daily_usage.user_id
        LEFT JOIN (
            SELECT user_id, SUM(word_count) as word_count
            FROM user_word_usage 
            WHERE usage_date >= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY user_id
        ) monthly_usage ON u.id = monthly_usage.user_id
        WHERE u.created_at >= CURRENT_DATE - INTERVAL '30 days'  -- Active users only
        GROUP BY tier
    ) tier_data;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- DATA VALIDATION AND CLEANUP
-- ═══════════════════════════════════════════════════════════════════════════

-- Clean up old anonymous sessions (keep only last 30 days)
DELETE FROM anonymous_word_usage 
WHERE usage_date < CURRENT_DATE - INTERVAL '30 days';

-- Clean up old user usage data (keep only last 12 months for non-current users)
DELETE FROM user_word_usage 
WHERE usage_date < CURRENT_DATE - INTERVAL '12 months' 
  AND user_id NOT IN (
      SELECT id FROM users 
      WHERE last_login >= CURRENT_DATE - INTERVAL '6 months'
         OR subscription_tier = 'pro'
  );

-- Update partnership allocations that might be in old format
UPDATE writing_partnerships 
SET shared_creative_space = 20000,
    initiator_solo_space_remaining = 10000,
    partner_solo_space_remaining = 10000
WHERE shared_creative_space != 20000 AND status = 'active';

-- Add comment for documentation
COMMENT ON TABLE user_word_usage IS 'Tracks word usage by authenticated users per day and pool type';
COMMENT ON TABLE anonymous_word_usage IS 'Tracks word usage by anonymous users via session ID';
COMMENT ON FUNCTION can_user_use_words IS 'Checks if user can use requested words based on tier and current usage';
COMMENT ON FUNCTION record_word_usage IS 'Records word usage for user, updating daily/monthly counters';
COMMENT ON FUNCTION get_conversion_pressure_metrics IS 'Gets metrics for users approaching tier limits for conversion optimization';