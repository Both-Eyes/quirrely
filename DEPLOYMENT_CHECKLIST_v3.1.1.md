# ⚔️ KNIGHT OF WANDS v3.1.1
## Production Deployment Checklist
### Date: February 16, 2026

---

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   DEPLOYMENT CHECKLIST                                                    ║
║   Knight of Wands v3.1.1 → Production                                    ║
║                                                                           ║
║   Total Tasks: 89                                                         ║
║   Estimated Time: 2-3 days                                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## PHASE 1: DOMAIN ACQUISITION & DNS
**Estimated Time: 1-2 hours**
**Priority: CRITICAL - Do First**

### 1.1 Primary Domain

- [ ] **Purchase quirrely.com** (if not owned)
  - Registrar: Cloudflare Registrar (recommended) or Namecheap
  - Cost: ~$10-15/year
  - Enable: Auto-renew, WHOIS privacy

### 1.2 Country-Specific Domains

| Domain | Market | Priority | Est. Cost |
|--------|--------|----------|-----------|
| - [ ] quirrely.ca | Canada 🇨🇦 | HIGH | ~$15/yr |
| - [ ] quirrely.co.uk | UK 🇬🇧 | HIGH | ~$10/yr |
| - [ ] quirrely.com.au | Australia 🇦🇺 | MEDIUM | ~$15/yr |
| - [ ] quirrely.co.nz | New Zealand 🇳🇿 | MEDIUM | ~$20/yr |

### 1.3 Defensive Domains (Optional)

- [ ] quirrely.io (~$35/yr)
- [ ] quirrely.app (~$15/yr)
- [ ] getquirrely.com (~$12/yr)

### 1.4 DNS Configuration

- [ ] **Transfer DNS to Cloudflare** (all domains)
  - Create Cloudflare account (if needed)
  - Add each domain to Cloudflare
  - Update nameservers at registrar
  - Wait for propagation (up to 24 hours)

- [ ] **Configure DNS Records** (quirrely.com)
  ```
  Type    Name    Value                   Proxy
  ─────────────────────────────────────────────────
  A       @       76.76.21.21            ✓ (Vercel)
  CNAME   www     cname.vercel-dns.com   ✓
  CNAME   api     [railway-domain]       ✓
  TXT     @       [Stripe verification]  ✗
  TXT     @       [Resend DKIM]          ✗
  MX      @       [Resend MX records]    ✗
  ```

- [ ] **Configure Country Redirects**
  - quirrely.ca → quirrely.com (with ?country=CA)
  - quirrely.co.uk → quirrely.com (with ?country=GB)
  - quirrely.com.au → quirrely.com (with ?country=AU)
  - quirrely.co.nz → quirrely.com (with ?country=NZ)

---

## PHASE 2: CLOUDFLARE SETUP
**Estimated Time: 1-2 hours**
**Priority: CRITICAL**

### 2.1 Account & Plan

- [ ] Create Cloudflare account (or use existing)
- [ ] Add payment method
- [ ] Start with Free plan (upgrade to Pro if needed)

### 2.2 Security Configuration

- [ ] **SSL/TLS Settings**
  - [ ] Set SSL mode to "Full (Strict)"
  - [ ] Enable "Always Use HTTPS"
  - [ ] Enable "Automatic HTTPS Rewrites"
  - [ ] Set Minimum TLS Version to 1.2

- [ ] **Firewall Rules - US Blocking**
  ```
  Rule Name: Block United States
  Expression: (ip.geoip.country eq "US")
  Action: Block
  ```

- [ ] **Additional Firewall Rules**
  - [ ] Rate limiting: 100 requests/minute per IP
  - [ ] Bot protection: Challenge suspicious bots
  - [ ] Block known bad IPs

- [ ] **WAF (Web Application Firewall)**
  - [ ] Enable managed rules (if Pro plan)
  - [ ] Enable OWASP Core Ruleset

### 2.3 Performance

- [ ] Enable Auto Minify (JS, CSS, HTML)
- [ ] Enable Brotli compression
- [ ] Configure caching rules
- [ ] Enable Early Hints

### 2.4 Page Rules

```
Rule 1: quirrely.com/*
  - Cache Level: Standard
  - Edge Cache TTL: 1 month

Rule 2: api.quirrely.com/*
  - Cache Level: Bypass
  - Disable Apps
```

---

## PHASE 3: SUPABASE (DATABASE + AUTH)
**Estimated Time: 2-3 hours**
**Priority: CRITICAL**

### 3.1 Project Setup

- [ ] Create Supabase account
- [ ] Create new project: "quirrely-production"
- [ ] Select region: Toronto (for Canada primary)
- [ ] Set strong database password (save securely)
- [ ] Wait for project provisioning (~2 minutes)

### 3.2 Database Schema

- [ ] Run migration scripts
  ```sql
  -- Users table
  -- Subscriptions table
  -- Analyses table
  -- Achievements table
  -- Events table
  -- etc.
  ```

- [ ] Create indexes for performance
- [ ] Set up Row Level Security (RLS) policies
- [ ] Create database functions/triggers

### 3.3 Authentication

- [ ] **Configure Auth Providers**
  - [ ] Enable Email/Password
  - [ ] Configure email templates
  - [ ] Set password requirements (min 8 chars)

- [ ] **Optional Providers**
  - [ ] Google OAuth (if desired)
  - [ ] Configure redirect URLs

- [ ] **Email Settings**
  - [ ] Configure SMTP (use Resend)
  - [ ] Customize email templates:
    - [ ] Welcome email
    - [ ] Password reset
    - [ ] Email verification

### 3.4 API Configuration

- [ ] Note down project URL
- [ ] Note down anon key (public)
- [ ] Note down service key (private - KEEP SECURE)
- [ ] Configure API rate limiting

### 3.5 Backups

- [ ] Verify daily backups enabled (Pro plan)
- [ ] Test backup restoration process

---

## PHASE 4: STRIPE (PAYMENTS)
**Estimated Time: 3-4 hours**
**Priority: CRITICAL**

### 4.1 Account Setup

- [ ] Create Stripe account (or use existing)
- [ ] Complete business verification
- [ ] Add bank account for payouts
- [ ] Enable live mode

### 4.2 Product Configuration

#### Create Products

- [ ] **Pro Tier**
  - [ ] Product: "Quirrely Pro"
  - [ ] Price (Monthly): $4.99 CAD
  - [ ] Price (Annual): $44.99 CAD
  - [ ] Metadata: `{ "tier": "pro" }`

- [ ] **Growth Tier**
  - [ ] Product: "Quirrely Growth"
  - [ ] Price (Monthly): $6.99 CAD
  - [ ] Price (Annual): $62.99 CAD
  - [ ] Metadata: `{ "tier": "growth" }`

- [ ] **Featured Tier**
  - [ ] Product: "Quirrely Featured"
  - [ ] Price (Monthly): $7.99 CAD
  - [ ] Price (Annual): $71.99 CAD
  - [ ] Metadata: `{ "tier": "featured" }`

- [ ] **Authority Tier**
  - [ ] Product: "Quirrely Authority"
  - [ ] Price (Monthly): $8.99 CAD
  - [ ] Price (Annual): $80.99 CAD
  - [ ] Metadata: `{ "tier": "authority" }`

- [ ] **Voice & Style Addon**
  - [ ] Product: "Voice & Style Analysis"
  - [ ] Price (Monthly): $9.99 CAD
  - [ ] Price (Annual): $89.99 CAD
  - [ ] Metadata: `{ "type": "addon", "addon": "voice_style" }`

#### Create Bundles

- [ ] **Pro + V&S Bundle**
  - [ ] Price: $12.99 CAD/month
  - [ ] Metadata: `{ "bundle": "pro_vs" }`

- [ ] **Authority + V&S Bundle**
  - [ ] Price: $16.99 CAD/month
  - [ ] Metadata: `{ "bundle": "authority_vs" }`

### 4.3 Multi-Currency Pricing

- [ ] **GBP Prices**
  - [ ] Pro: £2.49/£22.49
  - [ ] Growth: £3.49/£31.49
  - [ ] Featured: £3.99/£35.99
  - [ ] Authority: £4.49/£40.49
  - [ ] V&S: £4.99/£44.99

- [ ] **AUD Prices**
  - [ ] Pro: A$4.99/A$44.99
  - [ ] Growth: A$6.99/A$62.99
  - [ ] Featured: A$7.99/A$71.99
  - [ ] Authority: A$8.99/A$80.99
  - [ ] V&S: A$9.99/A$89.99

- [ ] **NZD Prices**
  - [ ] Pro: NZ$5.49/NZ$49.49
  - [ ] Growth: NZ$7.49/NZ$67.49
  - [ ] Featured: NZ$8.49/NZ$76.49
  - [ ] Authority: NZ$9.49/NZ$85.49
  - [ ] V&S: NZ$10.99/NZ$98.99

### 4.4 Customer Portal

- [ ] Enable Customer Portal
- [ ] Configure portal settings:
  - [ ] Allow subscription cancellation
  - [ ] Allow subscription pausing
  - [ ] Allow payment method updates
  - [ ] Show invoices

### 4.5 Webhooks

- [ ] Create webhook endpoint: `https://api.quirrely.com/webhooks/stripe`
- [ ] Subscribe to events:
  - [ ] `customer.subscription.created`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `invoice.paid`
  - [ ] `invoice.payment_failed`
  - [ ] `customer.created`
  - [ ] `checkout.session.completed`
- [ ] Note webhook signing secret

### 4.6 Tax Configuration

- [ ] Enable Stripe Tax (or configure manually)
- [ ] Set up tax rates for CA, GB, AU, NZ
- [ ] Configure tax ID collection if needed

### 4.7 Fraud Prevention

- [ ] Enable Radar for Fraud Teams (if needed)
- [ ] Configure Radar rules
- [ ] Set up 3D Secure for high-risk payments

---

## PHASE 5: RESEND (EMAIL)
**Estimated Time: 1-2 hours**
**Priority: HIGH**

### 5.1 Account Setup

- [ ] Create Resend account
- [ ] Upgrade to Pro plan ($20/month)

### 5.2 Domain Verification

- [ ] Add domain: quirrely.com
- [ ] Add DNS records to Cloudflare:
  - [ ] DKIM record (TXT)
  - [ ] SPF record (TXT)
  - [ ] DMARC record (TXT)
- [ ] Verify domain in Resend

### 5.3 Email Templates

- [ ] **Welcome Email**
  - Subject: "Welcome to Quirrely! 🎉"
  - Content: Onboarding steps, first analysis CTA

- [ ] **Trial Started**
  - Subject: "Your 7-day Pro trial has begun"
  - Content: Feature highlights, day-by-day unlocks

- [ ] **Trial Ending (Day 5)**
  - Subject: "2 days left in your trial"
  - Content: Upgrade CTA, benefits reminder

- [ ] **Subscription Confirmed**
  - Subject: "You're now a Quirrely Pro! 🚀"
  - Content: Receipt, getting started

- [ ] **Payment Failed**
  - Subject: "Action needed: Payment issue"
  - Content: Update payment method CTA

- [ ] **Cancellation Confirmed**
  - Subject: "We're sorry to see you go"
  - Content: Win-back offer, feedback request

### 5.4 API Key

- [ ] Generate API key
- [ ] Store securely in environment variables

---

## PHASE 6: ANTHROPIC (AI/ML)
**Estimated Time: 30 minutes**
**Priority: HIGH**

### 6.1 Account Setup

- [ ] Create Anthropic account (or use existing)
- [ ] Add payment method
- [ ] Set usage limits/alerts

### 6.2 API Configuration

- [ ] Generate API key
- [ ] Store securely
- [ ] Configure rate limiting in app

### 6.3 Model Selection

- [ ] Use `claude-sonnet-4-20250514` for voice analysis
- [ ] Configure fallback to Haiku for simple tasks

---

## PHASE 7: SENTRY (MONITORING)
**Estimated Time: 30 minutes**
**Priority: MEDIUM**

### 7.1 Account Setup

- [ ] Create Sentry account
- [ ] Create project: "quirrely-frontend"
- [ ] Create project: "quirrely-backend"

### 7.2 Configuration

- [ ] Note DSN for frontend
- [ ] Note DSN for backend
- [ ] Configure alert rules
- [ ] Set up Slack/email notifications

---

## PHASE 8: VERCEL (FRONTEND)
**Estimated Time: 1-2 hours**
**Priority: CRITICAL**

### 8.1 Account Setup

- [ ] Create Vercel account (or use existing)
- [ ] Upgrade to Pro plan ($20/month)
- [ ] Add payment method

### 8.2 Project Setup

- [ ] Import project from repository (or deploy manually)
- [ ] Configure build settings:
  - Framework: React
  - Build Command: `npm run build`
  - Output Directory: `dist` or `build`

### 8.3 Environment Variables

```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_STRIPE_PUBLISHABLE_KEY=
VITE_API_URL=https://api.quirrely.com
VITE_SENTRY_DSN=
VITE_META_PIXEL_ID=
```

### 8.4 Domain Configuration

- [ ] Add custom domain: quirrely.com
- [ ] Add custom domain: www.quirrely.com
- [ ] Verify DNS configuration
- [ ] Enable SSL

### 8.5 Deployment

- [ ] Deploy to production
- [ ] Verify deployment
- [ ] Test all routes

---

## PHASE 9: RAILWAY (BACKEND)
**Estimated Time: 1-2 hours**
**Priority: CRITICAL**

### 9.1 Account Setup

- [ ] Create Railway account
- [ ] Upgrade to Pro plan ($20/month + usage)
- [ ] Add payment method

### 9.2 Project Setup

- [ ] Create new project: "quirrely-api"
- [ ] Connect to repository (or deploy via CLI)
- [ ] Configure build settings:
  - Builder: Nixpacks
  - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 9.3 Environment Variables

```
# Database
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Anthropic
ANTHROPIC_API_KEY=

# Resend
RESEND_API_KEY=

# Sentry
SENTRY_DSN=

# App
APP_ENV=production
CORS_ORIGINS=https://quirrely.com,https://www.quirrely.com

# Meta
META_PIXEL_ID=
META_CAPI_TOKEN=
```

### 9.4 Custom Domain

- [ ] Add custom domain: api.quirrely.com
- [ ] Configure DNS CNAME in Cloudflare
- [ ] Verify SSL

### 9.5 Scaling

- [ ] Configure auto-scaling
- [ ] Set memory limits
- [ ] Configure health checks

---

## PHASE 10: META EVENTS API
**Estimated Time: 1 hour**
**Priority: MEDIUM**

### 10.1 Meta Business Setup

- [ ] Create Meta Business account (if needed)
- [ ] Create or connect Facebook Page
- [ ] Set up Meta Pixel

### 10.2 Pixel Configuration

- [ ] Note Pixel ID
- [ ] Install pixel on frontend
- [ ] Configure standard events:
  - [ ] PageView
  - [ ] Lead (signup)
  - [ ] StartTrial
  - [ ] Subscribe (conversion)

### 10.3 Conversions API (CAPI)

- [ ] Generate CAPI access token
- [ ] Configure server-side events
- [ ] Test event delivery

---

## PHASE 11: INTEGRATION TESTING
**Estimated Time: 2-3 hours**
**Priority: CRITICAL**

### 11.1 Authentication Flow

- [ ] Sign up with email
- [ ] Email verification
- [ ] Login
- [ ] Password reset
- [ ] Logout

### 11.2 Subscription Flow

- [ ] View pricing page
- [ ] Select tier
- [ ] Complete checkout (test mode first)
- [ ] Verify subscription active
- [ ] Access gated features

### 11.3 Analysis Flow

- [ ] Submit writing sample
- [ ] Receive analysis
- [ ] View results
- [ ] Export/save results

### 11.4 Billing Operations

- [ ] Upgrade subscription
- [ ] Downgrade subscription
- [ ] Cancel subscription
- [ ] Pause subscription
- [ ] Update payment method

### 11.5 Achievement System

- [ ] Earn badge
- [ ] Track XP
- [ ] View leaderboard
- [ ] Complete challenge

### 11.6 Multi-Currency

- [ ] Test CA pricing
- [ ] Test GB pricing
- [ ] Test AU pricing
- [ ] Test NZ pricing

### 11.7 Email Delivery

- [ ] Welcome email received
- [ ] Trial emails received
- [ ] Receipt email received

---

## PHASE 12: FINAL CHECKS
**Estimated Time: 1-2 hours**
**Priority: CRITICAL**

### 12.1 Security Audit

- [ ] All API keys in environment variables (not code)
- [ ] HTTPS enforced everywhere
- [ ] CORS configured correctly
- [ ] Rate limiting active
- [ ] US blocking active

### 12.2 Performance

- [ ] Page load < 3 seconds
- [ ] API response < 500ms
- [ ] Images optimized
- [ ] Caching configured

### 12.3 SEO

- [ ] Meta tags configured
- [ ] Open Graph tags
- [ ] robots.txt
- [ ] sitemap.xml

### 12.4 Legal

- [ ] Privacy Policy page
- [ ] Terms of Service page
- [ ] Cookie consent banner
- [ ] GDPR compliance (for UK)

### 12.5 Monitoring

- [ ] Error tracking active (Sentry)
- [ ] Uptime monitoring configured
- [ ] Alert notifications set up
- [ ] Log aggregation working

---

## PHASE 13: GO LIVE
**Estimated Time: 1 hour**
**Priority: CRITICAL**

### 13.1 Pre-Launch

- [ ] All tests passing
- [ ] Team notified
- [ ] Support ready
- [ ] Rollback plan documented

### 13.2 Launch

- [ ] Switch Stripe to live mode
- [ ] Remove test data
- [ ] Update environment variables
- [ ] Deploy final version

### 13.3 Post-Launch

- [ ] Verify live transactions
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Check email delivery
- [ ] Test one real signup

### 13.4 Announcement

- [ ] Update status page
- [ ] Social media announcement (if applicable)
- [ ] Team celebration 🎉

---

## COST SUMMARY

### One-Time Costs

| Item | Cost |
|------|------|
| quirrely.com | ~$12/yr |
| quirrely.ca | ~$15/yr |
| quirrely.co.uk | ~$10/yr |
| quirrely.com.au | ~$15/yr |
| quirrely.co.nz | ~$20/yr |
| **Total Domains** | **~$72/yr** |

### Monthly Costs (Launch)

| Service | Cost |
|---------|------|
| Vercel Pro | $20 |
| Railway Pro | $25 |
| Supabase Pro | $25 |
| Resend Pro | $20 |
| Anthropic API | ~$100 |
| Sentry Team | $26 |
| Cloudflare | $0 |
| **Total Monthly** | **$216** |

### Variable Costs

| Service | Rate |
|---------|------|
| Stripe | 2.9% + $0.30 per transaction |
| Anthropic | ~$0.03 per analysis |
| Railway overage | $0.000463/min compute |

---

## ROLLBACK PLAN

If critical issues arise:

1. **Frontend**: Revert to previous Vercel deployment
2. **Backend**: Revert to previous Railway deployment
3. **Database**: Restore from Supabase backup
4. **DNS**: Point to maintenance page

---

## CONTACTS & RESOURCES

### Vendor Support

| Vendor | Support URL |
|--------|-------------|
| Vercel | vercel.com/support |
| Railway | railway.app/help |
| Supabase | supabase.com/support |
| Stripe | stripe.com/support |
| Cloudflare | support.cloudflare.com |
| Resend | resend.com/support |

### Documentation

| Resource | URL |
|----------|-----|
| Vercel Docs | vercel.com/docs |
| Railway Docs | docs.railway.app |
| Supabase Docs | supabase.com/docs |
| Stripe Docs | stripe.com/docs |
| Cloudflare Docs | developers.cloudflare.com |

---

## SIGN-OFF

| Phase | Status | Completed By | Date |
|-------|--------|--------------|------|
| Phase 1: Domains | ⬜ Pending | | |
| Phase 2: Cloudflare | ⬜ Pending | | |
| Phase 3: Supabase | ⬜ Pending | | |
| Phase 4: Stripe | ⬜ Pending | | |
| Phase 5: Resend | ⬜ Pending | | |
| Phase 6: Anthropic | ⬜ Pending | | |
| Phase 7: Sentry | ⬜ Pending | | |
| Phase 8: Vercel | ⬜ Pending | | |
| Phase 9: Railway | ⬜ Pending | | |
| Phase 10: Meta | ⬜ Pending | | |
| Phase 11: Testing | ⬜ Pending | | |
| Phase 12: Final Checks | ⬜ Pending | | |
| Phase 13: Go Live | ⬜ Pending | | |

---

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ⚔️ KNIGHT OF WANDS v3.1.1                                              ║
║   PRODUCTION DEPLOYMENT CHECKLIST                                        ║
║                                                                           ║
║   Total Tasks: 89                                                         ║
║   Phases: 13                                                              ║
║   Estimated Time: 2-3 days                                               ║
║   Launch Cost: $216/month + domains                                      ║
║                                                                           ║
║   Status: ⬜ READY TO EXECUTE                                            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

*Checklist Created: February 16, 2026*
*Knight of Wands v3.1.1*
