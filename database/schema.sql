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
