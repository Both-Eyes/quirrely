-- ═══════════════════════════════════════════════════════════════════════════
-- COLLABORATION CANCELLATION RATE LIMITING MIGRATION v1.1
-- Adds rate limiting for collaboration cancellations (1 per month)
-- ═══════════════════════════════════════════════════════════════════════════

-- Migration metadata
INSERT INTO migrations (version, description, applied_at) VALUES 
('002', 'Add collaboration cancellation rate limiting', NOW())
ON CONFLICT (version) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════
-- UPDATE USER PARTNERSHIP STATUS TABLE
-- ═══════════════════════════════════════════════════════════════════════════

-- Add cancellation tracking to existing user partnership status table
ALTER TABLE user_partnership_status 
ADD COLUMN IF NOT EXISTS last_cancellation_date DATE,
ADD COLUMN IF NOT EXISTS cancellations_this_month INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS monthly_cancellation_period_start DATE DEFAULT DATE_TRUNC('month', NOW());

-- Create index for efficient cancellation rate limit checks
CREATE INDEX IF NOT EXISTS idx_user_partnership_status_cancellation_tracking 
ON user_partnership_status(user_id, last_cancellation_date, monthly_cancellation_period_start);

-- ═══════════════════════════════════════════════════════════════════════════
-- CANCELLATION RATE LIMITING FUNCTION
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION can_user_cancel_collaboration(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_status RECORD;
    current_month_start DATE := DATE_TRUNC('month', NOW());
BEGIN
    -- Get user's cancellation status
    SELECT last_cancellation_date, cancellations_this_month, monthly_cancellation_period_start
    INTO user_status
    FROM user_partnership_status 
    WHERE user_id = p_user_id;
    
    -- If no record exists, user can cancel (first time)
    IF NOT FOUND THEN
        RETURN TRUE;
    END IF;
    
    -- If last cancellation was in a previous month, reset and allow
    IF user_status.last_cancellation_date IS NULL OR 
       user_status.last_cancellation_date < current_month_start THEN
        RETURN TRUE;
    END IF;
    
    -- Check if user has exceeded monthly limit (1 cancellation per month)
    IF user_status.cancellations_this_month >= 1 THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- RECORD CANCELLATION FUNCTION
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION record_collaboration_cancellation(p_user_id UUID)
RETURNS VOID AS $$
DECLARE
    current_month_start DATE := DATE_TRUNC('month', NOW());
    current_date DATE := NOW()::DATE;
BEGIN
    -- Upsert cancellation tracking
    INSERT INTO user_partnership_status (
        user_id, 
        last_cancellation_date, 
        cancellations_this_month,
        monthly_cancellation_period_start,
        updated_at
    ) VALUES (
        p_user_id, 
        current_date, 
        1,
        current_month_start,
        NOW()
    )
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        last_cancellation_date = current_date,
        cancellations_this_month = CASE 
            WHEN user_partnership_status.monthly_cancellation_period_start < current_month_start THEN 1
            ELSE user_partnership_status.cancellations_this_month + 1
        END,
        monthly_cancellation_period_start = current_month_start,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- GET NEXT CANCELLATION DATE FUNCTION
-- ═══════════════════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION get_next_cancellation_date(p_user_id UUID)
RETURNS DATE AS $$
DECLARE
    user_status RECORD;
    current_month_start DATE := DATE_TRUNC('month', NOW());
    next_month_start DATE := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
BEGIN
    -- Get user's cancellation status
    SELECT last_cancellation_date, cancellations_this_month, monthly_cancellation_period_start
    INTO user_status
    FROM user_partnership_status 
    WHERE user_id = p_user_id;
    
    -- If no record exists or no cancellation this month, can cancel now
    IF NOT FOUND OR 
       user_status.last_cancellation_date IS NULL OR 
       user_status.last_cancellation_date < current_month_start THEN
        RETURN NOW()::DATE;
    END IF;
    
    -- If user has cancelled this month, next opportunity is next month
    IF user_status.cancellations_this_month >= 1 THEN
        RETURN next_month_start::DATE;
    END IF;
    
    -- Otherwise can cancel now
    RETURN NOW()::DATE;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- UPDATE COLLABORATION VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Update the active partnerships view to include cancellation info
CREATE OR REPLACE VIEW active_partnerships_with_cancellation_info AS
SELECT 
  p.id,
  p.partnership_name,
  p.partnership_type,
  p.status,
  p.shared_creative_space,
  p.shared_space_used,
  
  -- Initiator details
  u1.email AS initiator_email,
  u1.display_name AS initiator_name,
  p.initiator_solo_space_remaining,
  can_user_cancel_collaboration(p.initiator_user_id) AS initiator_can_cancel,
  get_next_cancellation_date(p.initiator_user_id) AS initiator_next_cancel_date,
  
  -- Partner details
  u2.email AS partner_email,
  u2.display_name AS partner_name,
  p.partner_solo_space_remaining,
  can_user_cancel_collaboration(p.partner_user_id) AS partner_can_cancel,
  get_next_cancellation_date(p.partner_user_id) AS partner_next_cancel_date,
  
  -- Timing
  p.started_at,
  p.current_period_end,
  
  -- Progress
  ROUND(
    (p.shared_space_used::DECIMAL / NULLIF(p.shared_creative_space, 0)) * 100, 
    1
  ) AS shared_words_used_percent
  
FROM writing_partnerships p
JOIN users u1 ON p.initiator_user_id = u1.id
LEFT JOIN users u2 ON p.partner_user_id = u2.id
WHERE p.status = 'active';

-- ═══════════════════════════════════════════════════════════════════════════
-- MIGRATION VERIFICATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Test the functions work correctly
DO $$ 
DECLARE 
    test_user_id UUID := gen_random_uuid();
    can_cancel_before BOOLEAN;
    can_cancel_after BOOLEAN;
    next_cancel_date DATE;
BEGIN 
    -- Test: User should be able to cancel initially
    SELECT can_user_cancel_collaboration(test_user_id) INTO can_cancel_before;
    
    IF NOT can_cancel_before THEN
        RAISE EXCEPTION 'Migration failed: New user cannot cancel collaboration';
    END IF;
    
    -- Test: Record a cancellation
    PERFORM record_collaboration_cancellation(test_user_id);
    
    -- Test: User should NOT be able to cancel again this month
    SELECT can_user_cancel_collaboration(test_user_id) INTO can_cancel_after;
    
    IF can_cancel_after THEN
        RAISE EXCEPTION 'Migration failed: User can cancel multiple times in same month';
    END IF;
    
    -- Test: Next cancellation date should be next month
    SELECT get_next_cancellation_date(test_user_id) INTO next_cancel_date;
    
    IF next_cancel_date <= NOW()::DATE THEN
        RAISE EXCEPTION 'Migration failed: Next cancellation date is not in the future';
    END IF;
    
    -- Cleanup test data
    DELETE FROM user_partnership_status WHERE user_id = test_user_id;
    
    RAISE NOTICE 'Cancellation rate limiting migration completed successfully';
    RAISE NOTICE 'Functions verified: can_user_cancel_collaboration, record_collaboration_cancellation, get_next_cancellation_date';
END $$;