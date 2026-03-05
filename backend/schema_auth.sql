-- ═══════════════════════════════════════════════════════════════════════════
-- QUIRRELY AUTHENTICATION DATABASE SCHEMA v1.0
-- ═══════════════════════════════════════════════════════════════════════════
-- 
-- User accounts, profiles, and session management.
-- Designed for Supabase Auth integration.
--
-- Auth Methods: Email/password, Magic link, Google (NEVER Apple)

-- ═══════════════════════════════════════════════════════════════════════════
-- USERS TABLE (extends Supabase auth.users)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS users (
  -- Links to Supabase auth.users
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Email (denormalized from auth.users for convenience)
  email TEXT NOT NULL UNIQUE,
  email_verified BOOLEAN DEFAULT FALSE,
  
  -- Profile
  display_name TEXT,
  profile_visibility TEXT NOT NULL DEFAULT 'private' 
    CHECK (profile_visibility IN ('private', 'public', 'featured_only')),
  
  -- Avatar (optional)
  avatar_url TEXT,
  
  -- Preferences
  preferred_currency TEXT CHECK (preferred_currency IN ('cad', 'gbp', 'eur', 'aud', 'nzd')),
  timezone TEXT,
  
  -- Account status
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'deleted', 'suspended')),
  deleted_at TIMESTAMPTZ,
  recovery_until TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_display_name ON users(display_name) WHERE display_name IS NOT NULL;
CREATE INDEX idx_users_status ON users(status);


-- ═══════════════════════════════════════════════════════════════════════════
-- DISPLAY NAME VALIDATION
-- ═══════════════════════════════════════════════════════════════════════════

-- Reserved names that cannot be used
CREATE TABLE IF NOT EXISTS reserved_display_names (
  name TEXT PRIMARY KEY
);

INSERT INTO reserved_display_names (name) VALUES
  ('admin'), ('quirrely'), ('support'), ('help'), ('system'),
  ('moderator'), ('mod'), ('staff'), ('official')
ON CONFLICT DO NOTHING;

-- Function to validate display name
CREATE OR REPLACE FUNCTION validate_display_name(p_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check length (2-50 characters)
  IF LENGTH(TRIM(p_name)) < 2 OR LENGTH(TRIM(p_name)) > 50 THEN
    RETURN FALSE;
  END IF;
  
  -- Check for valid characters (letters, numbers, spaces, hyphens, underscores)
  IF NOT TRIM(p_name) ~ '^[\w\s\-]+$' THEN
    RETURN FALSE;
  END IF;
  
  -- Check reserved names
  IF EXISTS (SELECT 1 FROM reserved_display_names WHERE name = LOWER(TRIM(p_name))) THEN
    RETURN FALSE;
  END IF;
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- EMAIL VERIFICATION TRACKING
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS email_verification_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  
  -- Token (hashed)
  token_hash TEXT NOT NULL,
  
  -- Status
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMPTZ,
  
  -- Expiration
  expires_at TIMESTAMPTZ NOT NULL,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_email_verification_user ON email_verification_requests(user_id);
CREATE INDEX idx_email_verification_expires ON email_verification_requests(expires_at);


-- ═══════════════════════════════════════════════════════════════════════════
-- PASSWORD RESET REQUESTS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS password_reset_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Token (hashed)
  token_hash TEXT NOT NULL,
  
  -- Status
  used BOOLEAN DEFAULT FALSE,
  used_at TIMESTAMPTZ,
  
  -- Expiration
  expires_at TIMESTAMPTZ NOT NULL,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_password_reset_user ON password_reset_requests(user_id);
CREATE INDEX idx_password_reset_expires ON password_reset_requests(expires_at);


-- ═══════════════════════════════════════════════════════════════════════════
-- ACCOUNT DELETION REQUESTS
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS account_deletion_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Request details
  deletion_type TEXT NOT NULL CHECK (deletion_type IN ('soft', 'hard')),
  reason TEXT,
  
  -- Status
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'cancelled')),
  
  -- For hard delete: cooldown period
  execute_after TIMESTAMPTZ,
  
  -- Completion
  completed_at TIMESTAMPTZ,
  
  -- Audit
  email_at_deletion TEXT,  -- Keep for records
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_deletion_requests_user ON account_deletion_requests(user_id);
CREATE INDEX idx_deletion_requests_status ON account_deletion_requests(status);


-- ═══════════════════════════════════════════════════════════════════════════
-- AUTH PROVIDERS (for tracking OAuth connections)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_auth_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Provider info
  provider TEXT NOT NULL CHECK (provider IN ('email', 'google')),  -- NEVER 'apple'
  provider_user_id TEXT,
  
  -- Metadata
  provider_email TEXT,
  provider_name TEXT,
  provider_avatar_url TEXT,
  
  -- Timestamps
  connected_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id, provider)
);

CREATE INDEX idx_auth_providers_user ON user_auth_providers(user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- LOGIN HISTORY (for security)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS login_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Login details
  method TEXT NOT NULL CHECK (method IN ('password', 'magic_link', 'google', 'refresh')),
  success BOOLEAN NOT NULL,
  
  -- Client info
  ip_address INET,
  user_agent TEXT,
  country_code TEXT,
  
  -- Failure reason (if applicable)
  failure_reason TEXT,
  
  -- Timestamp
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_login_history_user ON login_history(user_id, created_at DESC);
CREATE INDEX idx_login_history_ip ON login_history(ip_address);


-- ═══════════════════════════════════════════════════════════════════════════
-- HELPER FUNCTIONS
-- ═══════════════════════════════════════════════════════════════════════════

-- Create user profile after Supabase auth signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, email, email_verified)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.email_confirmed_at IS NOT NULL
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new Supabase auth users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_new_user();


-- Update email_verified when Supabase confirms email
CREATE OR REPLACE FUNCTION handle_email_verified()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.email_confirmed_at IS NOT NULL AND OLD.email_confirmed_at IS NULL THEN
    UPDATE users SET email_verified = TRUE WHERE id = NEW.id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_email_verified ON auth.users;
CREATE TRIGGER on_email_verified
  AFTER UPDATE ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION handle_email_verified();


-- Soft delete user
CREATE OR REPLACE FUNCTION soft_delete_user(p_user_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE users
  SET status = 'deleted',
      deleted_at = NOW(),
      recovery_until = NOW() + INTERVAL '30 days'
  WHERE id = p_user_id;
  
  INSERT INTO account_deletion_requests (user_id, deletion_type, status, completed_at, email_at_deletion)
  SELECT p_user_id, 'soft', 'completed', NOW(), email
  FROM users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql;


-- Hard delete user
CREATE OR REPLACE FUNCTION hard_delete_user(p_user_id UUID)
RETURNS void AS $$
DECLARE
  v_email TEXT;
BEGIN
  SELECT email INTO v_email FROM users WHERE id = p_user_id;
  
  -- Log deletion
  INSERT INTO account_deletion_requests (user_id, deletion_type, status, completed_at, email_at_deletion)
  VALUES (p_user_id, 'hard', 'completed', NOW(), v_email);
  
  -- Delete from users (cascade handles related data)
  DELETE FROM users WHERE id = p_user_id;
  
  -- Delete from Supabase auth
  DELETE FROM auth.users WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Recover soft-deleted user
CREATE OR REPLACE FUNCTION recover_user(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_user users%ROWTYPE;
BEGIN
  SELECT * INTO v_user FROM users WHERE id = p_user_id;
  
  IF NOT FOUND THEN
    RETURN FALSE;
  END IF;
  
  IF v_user.status != 'deleted' THEN
    RETURN FALSE;
  END IF;
  
  IF NOW() > v_user.recovery_until THEN
    RETURN FALSE;
  END IF;
  
  UPDATE users
  SET status = 'active',
      deleted_at = NULL,
      recovery_until = NULL,
      updated_at = NOW()
  WHERE id = p_user_id;
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_auth_providers ENABLE ROW LEVEL SECURITY;
ALTER TABLE login_history ENABLE ROW LEVEL SECURITY;

-- Users can view/update their own profile
CREATE POLICY "Users can view own profile" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
  FOR UPDATE USING (auth.uid() = id);

-- Public profiles are viewable
CREATE POLICY "Public profiles are viewable" ON users
  FOR SELECT USING (profile_visibility = 'public' AND status = 'active');

-- Users can view their own auth providers
CREATE POLICY "Users can view own providers" ON user_auth_providers
  FOR SELECT USING (auth.uid() = user_id);

-- Users can view their own login history
CREATE POLICY "Users can view own login history" ON login_history
  FOR SELECT USING (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- VIEWS
-- ═══════════════════════════════════════════════════════════════════════════

-- Public profile view (respects visibility settings)
CREATE OR REPLACE VIEW public_profiles AS
SELECT 
  id,
  display_name,
  avatar_url,
  created_at
FROM users
WHERE profile_visibility = 'public'
  AND status = 'active'
  AND display_name IS NOT NULL;


-- Users pending deletion (for cleanup job)
CREATE OR REPLACE VIEW users_pending_hard_delete AS
SELECT 
  u.id,
  u.email,
  u.deleted_at,
  u.recovery_until
FROM users u
WHERE u.status = 'deleted'
  AND u.recovery_until < NOW();
