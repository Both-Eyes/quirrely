# QUIRRELY DEPLOYMENT GUIDE
## Complete Step-by-Step Instructions

**Version:** 2.1.0  
**Date:** February 12, 2026  
**Stack:** Vercel (Frontend) + Railway (Backend) + Supabase (Database) + Stripe (Payments)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup (Supabase)](#database-setup-supabase)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Stripe Integration](#stripe-integration)
6. [Extension Publishing](#extension-publishing)
7. [Environment Variables](#environment-variables)
8. [Post-Deployment Checklist](#post-deployment-checklist)
9. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Accounts Required
- [ ] GitHub account (code repository)
- [ ] Vercel account (frontend hosting)
- [ ] Railway account (backend hosting)
- [ ] Supabase account (database)
- [ ] Stripe account (payments)
- [ ] Google Developer account (extension publishing)

### Local Tools
```bash
# Node.js 18+
node --version

# Python 3.10+
python3 --version

# Git
git --version

# Railway CLI (optional)
npm install -g @railway/cli

# Vercel CLI (optional)
npm install -g vercel
```

---

## Database Setup (Supabase)

### 1. Create Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project: `quirrely-prod`
3. Choose region closest to users
4. Save the database password securely

### 2. Run Schema Migration

Execute in Supabase SQL Editor:

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT,
  subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'trial', 'pro')),
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trials table
CREATE TABLE trials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ends_at TIMESTAMPTZ NOT NULL,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'converted')),
  analyses_count INTEGER DEFAULT 0,
  total_words_analyzed INTEGER DEFAULT 0,
  features_used TEXT[] DEFAULT '{}',
  conversion_date TIMESTAMPTZ,
  conversion_price DECIMAL(10, 2),
  UNIQUE(user_id)
);

-- Daily word usage table
CREATE TABLE daily_word_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id TEXT,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  keystroke_words INTEGER DEFAULT 0,
  pasted_words INTEGER DEFAULT 0,
  locked_method TEXT CHECK (locked_method IN ('keystroke', 'pasted')),
  analyses_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- Analysis history table
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_id TEXT,
  text_hash TEXT NOT NULL,
  text_preview TEXT,
  word_count INTEGER NOT NULL,
  input_method TEXT NOT NULL CHECK (input_method IN ('keystroke', 'pasted')),
  profile_id TEXT NOT NULL,
  profile_type TEXT NOT NULL,
  stance TEXT NOT NULL,
  confidence DECIMAL(3, 2),
  metrics JSONB,
  source TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_daily_usage_user_date ON daily_word_usage(user_id, date);
CREATE INDEX idx_analyses_user_created ON analyses(user_id, created_at DESC);
CREATE INDEX idx_trials_user ON trials(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe ON users(stripe_customer_id);

-- Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE trials ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_word_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

-- Policies (users can only access their own data)
CREATE POLICY "Users can view own data" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own trials" ON trials
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own usage" ON daily_word_usage
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own analyses" ON analyses
  FOR ALL USING (auth.uid() = user_id);
```

### 3. Get Connection Strings

From Supabase dashboard, copy:
- `SUPABASE_URL`: Project URL
- `SUPABASE_ANON_KEY`: Public anon key
- `SUPABASE_SERVICE_KEY`: Service role key (for backend)
- `DATABASE_URL`: PostgreSQL connection string

---

## Backend Deployment (Railway)

### 1. Prepare Repository

```bash
# Create backend directory structure
mkdir -p quirrely-backend
cd quirrely-backend

# Copy backend files
cp /path/to/lncp-web-app/backend/*.py .
cp /path/to/quirrely-word-limits/feature_gate_v2.py ./feature_gate.py
cp /path/to/quirrely-word-limits/api_v2_1.py ./main.py

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
supabase==2.3.0
stripe==7.0.0
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
EOF

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Initialize git
git init
git add .
git commit -m "Initial backend deployment"
```

### 2. Deploy to Railway

```bash
# Login to Railway
railway login

# Create new project
railway init

# Link to GitHub (recommended) or deploy directly
railway up

# Set environment variables
railway variables set SUPABASE_URL="your-url"
railway variables set SUPABASE_SERVICE_KEY="your-key"
railway variables set STRIPE_SECRET_KEY="sk_live_..."
railway variables set JWT_SECRET="your-random-secret"
railway variables set ENVIRONMENT="production"
```

### 3. Configure Domain

1. In Railway dashboard, go to Settings
2. Add custom domain: `api.quirrely.com`
3. Configure DNS with provided CNAME

---

## Frontend Deployment (Vercel)

### 1. Prepare Repository

```bash
# Create frontend directory
mkdir -p quirrely-frontend
cd quirrely-frontend

# Copy frontend files
cp -r /path/to/lncp-web-app/frontend/* .
cp -r /path/to/lncp-web-app/blog ./blog
cp /path/to/lncp-web-app/index.html .

# Create vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    { "src": "**/*.html", "use": "@vercel/static" },
    { "src": "**/*.js", "use": "@vercel/static" },
    { "src": "**/*.css", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "https://api.quirrely.com/api/$1" },
    { "src": "/blog/(.*)", "dest": "/blog/$1" },
    { "src": "/(.*)", "dest": "/$1" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
EOF

# Initialize git
git init
git add .
git commit -m "Initial frontend deployment"
```

### 2. Deploy to Vercel

```bash
# Login to Vercel
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://api.quirrely.com

vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
```

### 3. Configure Domain

1. In Vercel dashboard, go to Domains
2. Add: `quirrely.com` and `www.quirrely.com`
3. Configure DNS with provided records

---

## Stripe Integration

### 1. Create Products

In Stripe Dashboard:

```
Product: Quirrely Pro Monthly
- Price: $4.99/month
- Price ID: price_monthly_xxx

Product: Quirrely Pro Annual
- Price: $50/year
- Price ID: price_annual_xxx
```

### 2. Configure Webhooks

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://api.quirrely.com/api/v2/webhooks/stripe`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`

### 3. Backend Webhook Handler

Add to `main.py`:

```python
from fastapi import Request
import stripe

@app.post("/api/v2/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["client_reference_id"]
        # Upgrade user to Pro
        gate.set_user_tier(user_id, Tier.PRO)
        gate.convert_trial(user_id)
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        # Downgrade user to Free
        # (lookup user by stripe_customer_id)
    
    return {"received": True}
```

---

## Extension Publishing

### 1. Prepare Extension

```bash
cd /path/to/quirrely-extension

# Update manifest with production values
cat > manifest.json << 'EOF'
{
  "manifest_version": 3,
  "name": "Quirrely - Writing Voice Analyzer",
  "version": "1.0.0",
  "description": "Discover your writing voice with LNCP analysis",
  "permissions": ["storage", "activeTab", "contextMenus"],
  "host_permissions": ["https://api.quirrely.com/*"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "css": ["content.css"]
  }],
  "background": {
    "service_worker": "background.js"
  }
}
EOF

# Create ZIP for Chrome Web Store
zip -r quirrely-extension-v1.0.0.zip . -x "*.git*"
```

### 2. Submit to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Pay one-time $5 developer fee
3. Upload ZIP
4. Fill in listing:
   - Description
   - Screenshots (1280x800)
   - Promotional images
   - Privacy policy URL
5. Submit for review (1-3 days)

---

## Environment Variables

### Backend (Railway)

```env
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
DATABASE_URL=postgresql://...

# Auth
JWT_SECRET=your-256-bit-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_MONTHLY=price_...
STRIPE_PRICE_ANNUAL=price_...

# App
ENVIRONMENT=production
CORS_ORIGINS=https://quirrely.com,https://www.quirrely.com
```

### Frontend (Vercel)

```env
NEXT_PUBLIC_API_URL=https://api.quirrely.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

## Post-Deployment Checklist

### Immediate (Day 1)

- [ ] Backend health check: `curl https://api.quirrely.com/api/v2/health`
- [ ] Frontend loads: `curl https://quirrely.com`
- [ ] Auth flow works (signup, login, logout)
- [ ] Analysis works (with word limits)
- [ ] Trial start works
- [ ] Stripe checkout works (test mode first)
- [ ] Extension loads popup
- [ ] Extension content script works
- [ ] Blog posts load

### Week 1

- [ ] Switch Stripe to live mode
- [ ] Monitor error rates
- [ ] Check word limit enforcement
- [ ] Verify trial expiration
- [ ] Test upgrade flow end-to-end
- [ ] Extension published and approved

### Ongoing

- [ ] Weekly backup verification
- [ ] Monitor usage metrics
- [ ] Review error logs
- [ ] Update LNCP if needed
- [ ] Respond to user feedback

---

## Monitoring & Maintenance

### Health Endpoints

```bash
# Backend health
curl https://api.quirrely.com/api/v2/health

# Expected response:
{
  "status": "healthy",
  "version": "2.1.0",
  "lncp_version": "3.8",
  "word_based_limits": true
}
```

### Logs

- **Railway:** Dashboard → Project → Logs
- **Vercel:** Dashboard → Project → Functions → Logs
- **Supabase:** Dashboard → Logs

### Alerts

Configure alerts for:
- Error rate > 1%
- Response time > 2s
- Database connections > 80%
- Storage > 80%

### Backups

Supabase automatic daily backups. Additional:

```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

---

## Rollback Procedure

### Backend

```bash
# Railway
railway rollback

# Or redeploy previous commit
git checkout <previous-commit>
railway up
```

### Frontend

```bash
# Vercel
vercel rollback

# Or
vercel --prod --force
```

---

## Support

- **Documentation:** https://docs.quirrely.com
- **Status Page:** https://status.quirrely.com
- **Support Email:** support@quirrely.com

---

*Last updated: February 12, 2026*
