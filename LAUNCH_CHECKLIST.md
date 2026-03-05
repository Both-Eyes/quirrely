# QUIRRELY LAUNCH CHECKLIST
## Version 1.0 — Soft Launch

**Target Launch:** TBD  
**Launch Mode:** Soft Launch (quiet, iterate)

---

## ✅ INFRASTRUCTURE

### Hosting
- [ ] Vercel project created for frontend
- [ ] Railway project created for backend API
- [ ] Supabase project created for database
- [ ] All environments configured (dev, staging, production)

### Domains
- [ ] quirrely.com registered and DNS configured
- [ ] quirrely.ca registered and DNS configured
- [ ] quirrely.co.uk registered and DNS configured
- [ ] quirrely.com.au registered and DNS configured
- [ ] quirrely.co.nz registered and DNS configured
- [ ] SSL certificates active on all domains
- [ ] Geo-redirect logic tested on quirrely.com

### CDN & Performance
- [ ] Vercel Edge caching enabled
- [ ] Static assets optimized
- [ ] Images compressed and served in WebP
- [ ] Core Web Vitals passing (LCP < 2.5s, CLS < 0.1)

---

## ✅ SECURITY

### Authentication
- [ ] Supabase Auth configured
- [ ] Email verification working
- [ ] Password reset flow working
- [ ] Magic link login working
- [ ] Google OAuth configured (NOT Apple)

### API Security
- [ ] Rate limiting enabled
- [ ] CORS configured for all country domains
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)
- [ ] All endpoints require authentication (except public)
- [ ] Admin endpoints require admin role

### Secrets
- [ ] All API keys in environment variables
- [ ] No secrets in code repository
- [ ] Secrets different per environment
- [ ] Stripe keys (test vs live) configured

---

## ✅ DATA

### Database
- [ ] All migrations run on production
- [ ] Indexes created for performance
- [ ] Row Level Security policies enabled
- [ ] Database backups verified (daily + PITR)

### Seed Data
- [ ] Reserved usernames inserted
- [ ] Feature flags configured
- [ ] Admin user created
- [ ] Test data cleaned from production

---

## ✅ INTEGRATIONS

### Stripe (Payments)
- [ ] Live Stripe account activated
- [ ] Products and prices created (all 5 currencies)
- [ ] Webhook endpoint configured
- [ ] Checkout flow tested end-to-end
- [ ] Billing portal configured

### Resend (Email)
- [ ] Domain verified (quirrely.com)
- [ ] DNS records configured (SPF, DKIM, DMARC)
- [ ] API key configured
- [ ] All email templates tested
- [ ] Webhook for email events configured

### Plausible (Analytics)
- [ ] Site created for quirrely.com
- [ ] Script added to all pages
- [ ] Custom events configured
- [ ] Dashboard accessible

### Sentry (Errors)
- [ ] Project created
- [ ] DSN configured in environment
- [ ] Source maps uploaded
- [ ] Alert rules configured

---

## ✅ LEGAL

### Documents
- [ ] Terms of Service published at /terms
- [ ] Privacy Policy published at /privacy
- [ ] No-refund policy clearly stated in Terms
- [ ] DMCA contact information available

### Compliance
- [ ] GDPR compliant (no tracking cookies)
- [ ] Data export feature working
- [ ] Account deletion feature working
- [ ] Age verification notice present

---

## ✅ CONTENT

### Marketing Pages
- [ ] Landing page complete
- [ ] Pricing page complete (all currencies)
- [ ] Features page complete
- [ ] About page complete

### Blog Posts
- [ ] 40 writer voice profile posts published
- [ ] 40 reader taste profile posts published
- [ ] Blog index pages working

### Help & Support
- [ ] Help center / FAQ created
- [ ] Contact form working
- [ ] support@quirrely.com receiving mail

### Featured Showcase
- [ ] /featured landing page ready
- [ ] /featured/writers page ready
- [ ] /featured/curators page ready
- [ ] /featured/authority page ready

---

## ✅ TESTING

### Functional Testing
- [ ] Signup flow works
- [ ] Login flow works (email + Google)
- [ ] Writing analysis works
- [ ] Subscription flow works
- [ ] All dashboard sections render
- [ ] Settings save correctly
- [ ] Profile pages display correctly

### Cross-Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Mobile Testing
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] Responsive layouts verified

### Load Testing
- [ ] API can handle expected load
- [ ] Database queries optimized
- [ ] No memory leaks

---

## ✅ MONITORING

### Uptime Monitoring
- [ ] Better Uptime / UptimeRobot configured
- [ ] Health check endpoints monitored
- [ ] Alert email configured
- [ ] Slack webhook configured (optional)

### Error Monitoring
- [ ] Sentry capturing errors
- [ ] Alert thresholds configured
- [ ] On-call person designated

### Analytics
- [ ] Plausible receiving data
- [ ] Internal metrics dashboard working
- [ ] Funnel tracking configured

---

## ✅ SEO

### Technical SEO
- [ ] Sitemap.xml generated
- [ ] Robots.txt configured
- [ ] Canonical URLs set
- [ ] hreflang tags on landing/pricing/featured pages
- [ ] Open Graph tags on all public pages
- [ ] Structured data (JSON-LD) for organization

### Search Console
- [ ] Google Search Console verified
- [ ] Sitemap submitted
- [ ] All country domains verified

---

## ✅ LAUNCH DAY

### T-1 Day (Day Before)
- [ ] Final staging deployment tested
- [ ] DNS TTL lowered (if changing)
- [ ] Team notified of launch time
- [ ] Monitoring dashboards open

### T-0 (Launch)
- [ ] Production deployment triggered
- [ ] Smoke test all critical paths
- [ ] Verify payments work (small test purchase)
- [ ] Verify emails sending
- [ ] Monitor error rates

### T+1 Hour
- [ ] Check Plausible for traffic
- [ ] Check Sentry for errors
- [ ] Check email delivery rates
- [ ] Address any hotfixes

### T+1 Day
- [ ] Review analytics
- [ ] Review user feedback
- [ ] Prioritize bug fixes
- [ ] Plan next iteration

---

## 🚫 EXCLUSION LIST VERIFICATION

Confirm these are NOT present anywhere:

- [ ] ❌ No USD pricing or currency references
- [ ] ❌ No Amazon affiliate links
- [ ] ❌ No X/Twitter share buttons or links
- [ ] ❌ No Apple sign-in
- [ ] ❌ No shiny gold (#FFD700) — only soft gold (#D4A574)

---

## 📞 EMERGENCY CONTACTS

| Role | Contact |
|------|---------|
| Technical Lead | TBD |
| On-Call Engineer | TBD |
| Stripe Support | dashboard.stripe.com |
| Supabase Support | supabase.com/dashboard |
| Vercel Support | vercel.com/support |

---

## 📝 POST-LAUNCH NOTES

*(Fill in after launch)*

**Launch Date:** _______________  
**Initial Issues:** _______________  
**Resolution:** _______________  
**Lessons Learned:** _______________

---

*Good luck! You've got this. 🐿️*
