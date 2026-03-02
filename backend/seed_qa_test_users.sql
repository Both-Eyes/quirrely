-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY QA TEST USER SEED DATA
-- For Kim's Comprehensive QA Testing
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- This script creates 56 test accounts:
-- - 14 tier+addon combinations × 4 countries
-- 
-- Password for all test accounts: QuirrelyQA2026!
-- ═══════════════════════════════════════════════════════════════════════════

-- Clean up existing test users (if re-running)
DELETE FROM user_addons WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'kim_%@test.quirrely.com');
DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE email LIKE 'kim_%@test.quirrely.com');
DELETE FROM users WHERE email LIKE 'kim_%@test.quirrely.com';

-- ═══════════════════════════════════════════════════════════════════════════
-- CANADA TEST USERS (🇨🇦)
-- ═══════════════════════════════════════════════════════════════════════════

-- 1. Free, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_free_none_ca@test.quirrely.com', 'Kim Free CA', 'cad', 'active');

-- 2. Free + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_free_vs_ca@test.quirrely.com', 'Kim Free+VS CA', 'cad', 'active');
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'promotion', 'active' FROM users WHERE email = 'kim_free_vs_ca@test.quirrely.com';

-- 3. Pro, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_pro_none_ca@test.quirrely.com', 'Kim Pro CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_pro_ca', 'sub_test_pro_ca', 'pro', 'active', 'cad', 1499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_pro_none_ca@test.quirrely.com';

-- 4. Pro + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_pro_vs_ca@test.quirrely.com', 'Kim Pro+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_pro_vs_ca', 'sub_test_pro_vs_ca', 'pro', 'active', 'cad', 1499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_pro_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_pro_vs_ca@test.quirrely.com';

-- 5. Curator, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_curator_none_ca@test.quirrely.com', 'Kim Curator CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_curator_ca', 'sub_test_curator_ca', 'curator', 'active', 'cad', 1499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_curator_none_ca@test.quirrely.com';

-- 6. Curator + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_curator_vs_ca@test.quirrely.com', 'Kim Curator+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_curator_vs_ca', 'sub_test_curator_vs_ca', 'curator', 'active', 'cad', 1499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_curator_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_curator_vs_ca@test.quirrely.com';

-- 7. Featured Writer, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_fw_none_ca@test.quirrely.com', 'Kim Featured Writer CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_fw_ca', 'sub_test_fw_ca', 'featured_writer', 'active', 'cad', 2499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_fw_none_ca@test.quirrely.com';

-- 8. Featured Writer + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_fw_vs_ca@test.quirrely.com', 'Kim Featured Writer+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_fw_vs_ca', 'sub_test_fw_vs_ca', 'featured_writer', 'active', 'cad', 2499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_fw_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_fw_vs_ca@test.quirrely.com';

-- 9. Featured Curator, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_fc_none_ca@test.quirrely.com', 'Kim Featured Curator CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_fc_ca', 'sub_test_fc_ca', 'featured_curator', 'active', 'cad', 2499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_fc_none_ca@test.quirrely.com';

-- 10. Featured Curator + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_fc_vs_ca@test.quirrely.com', 'Kim Featured Curator+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_fc_vs_ca', 'sub_test_fc_vs_ca', 'featured_curator', 'active', 'cad', 2499, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_fc_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_fc_vs_ca@test.quirrely.com';

-- 11. Authority Writer, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_aw_none_ca@test.quirrely.com', 'Kim Authority Writer CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_aw_ca', 'sub_test_aw_ca', 'authority_writer', 'active', 'cad', 4999, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_aw_none_ca@test.quirrely.com';

-- 12. Authority Writer + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_aw_vs_ca@test.quirrely.com', 'Kim Authority Writer+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_aw_vs_ca', 'sub_test_aw_vs_ca', 'authority_writer', 'active', 'cad', 4999, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_aw_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_aw_vs_ca@test.quirrely.com';

-- 13. Authority Curator, no addon
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_ac_none_ca@test.quirrely.com', 'Kim Authority Curator CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_ac_ca', 'sub_test_ac_ca', 'authority_curator', 'active', 'cad', 4999, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_ac_none_ca@test.quirrely.com';

-- 14. Authority Curator + voice_style
INSERT INTO users (id, email, display_name, preferred_currency, status)
VALUES (gen_random_uuid(), 'kim_ac_vs_ca@test.quirrely.com', 'Kim Authority Curator+VS CA', 'cad', 'active');
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_ac_vs_ca', 'sub_test_ac_vs_ca', 'authority_curator', 'active', 'cad', 4999, 'month', NOW(), NOW() + INTERVAL '30 days' 
FROM users WHERE email = 'kim_ac_vs_ca@test.quirrely.com';
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email = 'kim_ac_vs_ca@test.quirrely.com';


-- ═══════════════════════════════════════════════════════════════════════════
-- UK TEST USERS (🇬🇧) - Same pattern, different currency
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO users (id, email, display_name, preferred_currency, status) VALUES
(gen_random_uuid(), 'kim_free_none_uk@test.quirrely.com', 'Kim Free UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_free_vs_uk@test.quirrely.com', 'Kim Free+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_pro_none_uk@test.quirrely.com', 'Kim Pro UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_pro_vs_uk@test.quirrely.com', 'Kim Pro+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_curator_none_uk@test.quirrely.com', 'Kim Curator UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_curator_vs_uk@test.quirrely.com', 'Kim Curator+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_fw_none_uk@test.quirrely.com', 'Kim Featured Writer UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_fw_vs_uk@test.quirrely.com', 'Kim Featured Writer+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_fc_none_uk@test.quirrely.com', 'Kim Featured Curator UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_fc_vs_uk@test.quirrely.com', 'Kim Featured Curator+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_aw_none_uk@test.quirrely.com', 'Kim Authority Writer UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_aw_vs_uk@test.quirrely.com', 'Kim Authority Writer+VS UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_ac_none_uk@test.quirrely.com', 'Kim Authority Curator UK', 'gbp', 'active'),
(gen_random_uuid(), 'kim_ac_vs_uk@test.quirrely.com', 'Kim Authority Curator+VS UK', 'gbp', 'active');

-- UK subscriptions
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_' || REPLACE(email, '@test.quirrely.com', ''), 'sub_test_' || REPLACE(email, '@test.quirrely.com', ''),
  CASE 
    WHEN email LIKE '%_pro_%' THEN 'pro'
    WHEN email LIKE '%_curator_%' THEN 'curator'
    WHEN email LIKE '%_fw_%' THEN 'featured_writer'
    WHEN email LIKE '%_fc_%' THEN 'featured_curator'
    WHEN email LIKE '%_aw_%' THEN 'authority_writer'
    WHEN email LIKE '%_ac_%' THEN 'authority_curator'
  END,
  'active', 'gbp',
  CASE 
    WHEN email LIKE '%_pro_%' OR email LIKE '%_curator_%' THEN 1199
    WHEN email LIKE '%_fw_%' OR email LIKE '%_fc_%' THEN 1999
    ELSE 3999
  END,
  'month', NOW(), NOW() + INTERVAL '30 days'
FROM users WHERE email LIKE 'kim_%_uk@test.quirrely.com' AND email NOT LIKE '%free%';

-- UK voice_style addons
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email LIKE 'kim_%_vs_uk@test.quirrely.com';


-- ═══════════════════════════════════════════════════════════════════════════
-- AUSTRALIA TEST USERS (🇦🇺)
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO users (id, email, display_name, preferred_currency, status) VALUES
(gen_random_uuid(), 'kim_free_none_au@test.quirrely.com', 'Kim Free AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_free_vs_au@test.quirrely.com', 'Kim Free+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_pro_none_au@test.quirrely.com', 'Kim Pro AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_pro_vs_au@test.quirrely.com', 'Kim Pro+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_curator_none_au@test.quirrely.com', 'Kim Curator AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_curator_vs_au@test.quirrely.com', 'Kim Curator+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_fw_none_au@test.quirrely.com', 'Kim Featured Writer AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_fw_vs_au@test.quirrely.com', 'Kim Featured Writer+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_fc_none_au@test.quirrely.com', 'Kim Featured Curator AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_fc_vs_au@test.quirrely.com', 'Kim Featured Curator+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_aw_none_au@test.quirrely.com', 'Kim Authority Writer AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_aw_vs_au@test.quirrely.com', 'Kim Authority Writer+VS AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_ac_none_au@test.quirrely.com', 'Kim Authority Curator AU', 'aud', 'active'),
(gen_random_uuid(), 'kim_ac_vs_au@test.quirrely.com', 'Kim Authority Curator+VS AU', 'aud', 'active');

-- AU subscriptions
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_' || REPLACE(email, '@test.quirrely.com', ''), 'sub_test_' || REPLACE(email, '@test.quirrely.com', ''),
  CASE 
    WHEN email LIKE '%_pro_%' THEN 'pro'
    WHEN email LIKE '%_curator_%' THEN 'curator'
    WHEN email LIKE '%_fw_%' THEN 'featured_writer'
    WHEN email LIKE '%_fc_%' THEN 'featured_curator'
    WHEN email LIKE '%_aw_%' THEN 'authority_writer'
    WHEN email LIKE '%_ac_%' THEN 'authority_curator'
  END,
  'active', 'aud',
  CASE 
    WHEN email LIKE '%_pro_%' OR email LIKE '%_curator_%' THEN 1999
    WHEN email LIKE '%_fw_%' OR email LIKE '%_fc_%' THEN 3499
    ELSE 6999
  END,
  'month', NOW(), NOW() + INTERVAL '30 days'
FROM users WHERE email LIKE 'kim_%_au@test.quirrely.com' AND email NOT LIKE '%free%';

-- AU voice_style addons
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email LIKE 'kim_%_vs_au@test.quirrely.com';


-- ═══════════════════════════════════════════════════════════════════════════
-- NEW ZEALAND TEST USERS (🇳🇿)
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO users (id, email, display_name, preferred_currency, status) VALUES
(gen_random_uuid(), 'kim_free_none_nz@test.quirrely.com', 'Kim Free NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_free_vs_nz@test.quirrely.com', 'Kim Free+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_pro_none_nz@test.quirrely.com', 'Kim Pro NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_pro_vs_nz@test.quirrely.com', 'Kim Pro+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_curator_none_nz@test.quirrely.com', 'Kim Curator NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_curator_vs_nz@test.quirrely.com', 'Kim Curator+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_fw_none_nz@test.quirrely.com', 'Kim Featured Writer NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_fw_vs_nz@test.quirrely.com', 'Kim Featured Writer+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_fc_none_nz@test.quirrely.com', 'Kim Featured Curator NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_fc_vs_nz@test.quirrely.com', 'Kim Featured Curator+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_aw_none_nz@test.quirrely.com', 'Kim Authority Writer NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_aw_vs_nz@test.quirrely.com', 'Kim Authority Writer+VS NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_ac_none_nz@test.quirrely.com', 'Kim Authority Curator NZ', 'nzd', 'active'),
(gen_random_uuid(), 'kim_ac_vs_nz@test.quirrely.com', 'Kim Authority Curator+VS NZ', 'nzd', 'active');

-- NZ subscriptions
INSERT INTO subscriptions (user_id, stripe_customer_id, stripe_subscription_id, tier, status, currency, amount_cents, interval, current_period_start, current_period_end)
SELECT id, 'cus_test_' || REPLACE(email, '@test.quirrely.com', ''), 'sub_test_' || REPLACE(email, '@test.quirrely.com', ''),
  CASE 
    WHEN email LIKE '%_pro_%' THEN 'pro'
    WHEN email LIKE '%_curator_%' THEN 'curator'
    WHEN email LIKE '%_fw_%' THEN 'featured_writer'
    WHEN email LIKE '%_fc_%' THEN 'featured_curator'
    WHEN email LIKE '%_aw_%' THEN 'authority_writer'
    WHEN email LIKE '%_ac_%' THEN 'authority_curator'
  END,
  'active', 'nzd',
  CASE 
    WHEN email LIKE '%_pro_%' OR email LIKE '%_curator_%' THEN 2199
    WHEN email LIKE '%_fw_%' OR email LIKE '%_fc_%' THEN 3799
    ELSE 7499
  END,
  'month', NOW(), NOW() + INTERVAL '30 days'
FROM users WHERE email LIKE 'kim_%_nz@test.quirrely.com' AND email NOT LIKE '%free%';

-- NZ voice_style addons
INSERT INTO user_addons (user_id, addon, source, status)
SELECT id, 'voice_style', 'purchase', 'active' FROM users WHERE email LIKE 'kim_%_vs_nz@test.quirrely.com';


-- ═══════════════════════════════════════════════════════════════════════════
-- VERIFICATION QUERY
-- ═══════════════════════════════════════════════════════════════════════════

-- Run this to verify all 56 users were created correctly:
SELECT 
  u.email,
  u.display_name,
  u.preferred_currency,
  COALESCE(s.tier, 'free') AS tier,
  COALESCE(
    (SELECT ARRAY_AGG(ua.addon) FROM user_addons ua WHERE ua.user_id = u.id AND ua.status = 'active'),
    ARRAY[]::TEXT[]
  ) AS addons,
  CASE WHEN s.id IS NOT NULL THEN 'subscribed' ELSE 'free' END AS subscription_status
FROM users u
LEFT JOIN subscriptions s ON s.user_id = u.id AND s.status = 'active'
WHERE u.email LIKE 'kim_%@test.quirrely.com'
ORDER BY u.preferred_currency, tier, u.email;

-- Expected: 56 rows (14 tier combos × 4 countries)
