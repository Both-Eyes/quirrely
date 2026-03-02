# Sentense — SEO Readiness Checklist

## Pre-Auth/Payments Launch Checklist

---

## Current Status

| Item | Status |
|------|--------|
| Meta tags (title, description, keywords) | ✅ Done |
| Open Graph + Twitter Cards | ✅ Done |
| Hreflang tags (4 countries) | ✅ Done |
| Structured data (WebApplication + FAQ) | ✅ Done |
| Dynamic locale-based SEO | ✅ Done |
| sitemap.xml | ✅ Done |
| robots.txt | ✅ Done |
| Profile pages | ✅ 4 of 10 |
| Blog posts | ✅ 2 of 6 |
| OG/Twitter images | ✅ SVG (need PNG) |
| Outreach templates | ✅ Done |
| Search Console guide | ✅ Done |

---

## 🔴 CRITICAL — Before Launch

### 1. Convert OG Images to PNG
- **Status:** ⏳ Pending
- **Action:** Convert SVG → PNG (1200x630 for OG, 1200x628 for Twitter)
- **Tool:** Figma, Canva, or svgtopng.com
- **Why:** Social platforms don't render SVG

### 2. Complete Remaining Profile Pages
- **Status:** ⏳ 6 remaining
- **Missing:** DENSE, FORMAL, BALANCED, LONGFORM, INTERROGATIVE, HEDGED
- **Effort:** ~2 hours
- **Why:** Long-tail keyword targets

### 3. Submit to Google Search Console
- **Status:** ⏳ Requires domain access
- **Action:** Verify domain ownership, submit sitemap
- **Why:** Indexing won't begin without this

### 4. Core Web Vitals Audit
- **Status:** ⏳ Pending
- **Action:** Run Lighthouse audit
- **Targets:**
  - LCP (Largest Contentful Paint): < 2.5s
  - FID (First Input Delay): < 100ms
  - CLS (Cumulative Layout Shift): < 0.1
- **Why:** Google ranking factor

### 5. Mobile Responsiveness Check
- **Status:** ⏳ Pending
- **Action:** Test all screens on mobile devices
- **Why:** Mobile-first indexing

---

## 🟡 HIGH PRIORITY — Week 1

### 6. Create Remaining Blog Posts
- **Status:** 2 of 6 done
- **Missing:**
  - `/blog/british-writing-style` (UK target)
  - `/blog/australian-writing-style` (AU target)
  - `/blog/nz-writing-style` (NZ target)
  - `/blog/10-writing-profiles` (all markets)
- **Effort:** ~3 hours

### 7. Create FAQ Page
- **Status:** ⏳ Pending
- **Action:** Standalone `/faq` with FAQPage schema
- **Why:** Featured snippet opportunities

### 8. Create Pricing Page
- **Status:** ⏳ Pending
- **Action:** `/pricing` with Product/Offer schema
- **Why:** Captures "sentense pricing" queries

### 9. Add Internal Linking
- **Status:** ⏳ Pending
- **Action:** Link blog → profiles → main app
- **Why:** Distributes page authority

### 10. Set Up Google Analytics 4
- **Status:** ⏳ Pending
- **Action:** Add GA4 tracking code
- **Why:** Measure organic traffic from day 1

---

## 🟢 MEDIUM PRIORITY — Month 1

### 11. Create Comparison Pages
- `/compare/sentense-vs-grammarly`
- `/compare/sentense-vs-hemingway`
- **Why:** Captures "alternative to X" searches

### 12. Add Testimonials Page
- `/testimonials` with Review schema
- **Why:** Social proof + rich snippets

### 13. Create Glossary/Resources
- `/glossary/assertive-writing`
- `/resources/writing-voice-guide`
- **Why:** Educational content ranks well

### 14. Bing Webmaster Tools
- **Why:** ~5% of search traffic

### 15. Local Business Listings
- Google Business Profile (if applicable)
- **Why:** Local SEO signal

---

## Decisions Needed

### Decision 1: URL Structure for Countries

| Option | Pros | Cons |
|--------|------|------|
| `?locale=CA` (current) | Simple | Weak geo-signal |
| Subdomains (`ca.sentense.com`) | Strong geo-signal | Complex SSL, split authority |
| **Subdirectories (`/ca/`)** | Easy, shares authority | Requires routing |

**Recommendation:** Subdirectories (`/ca/`, `/uk/`, `/au/`, `/nz/`)

---

### Decision 2: Blog Platform

| Option | Pros | Cons |
|--------|------|------|
| **Static HTML** (current) | Fast, simple | Manual updates |
| CMS (Ghost) | Easy editing | Additional cost/complexity |
| Markdown + build | Dev-friendly | Requires build step |

**Recommendation:** Keep static for launch, migrate if needed

---

### Decision 3: Results URL Structure

| Option | SEO Value |
|--------|-----------|
| `/#results` (current) | ❌ Not indexable |
| **`/result/assertive-closed`** | ✅ Indexable, shareable |

**Recommendation:** Implement path-based results

**Why:** Each profile+stance combo becomes a keyword target

---

### Decision 4: Canonical Domain

| Option | Notes |
|--------|-------|
| **`sentense.com`** | Cleaner, modern |
| `www.sentense.com` | Traditional |

**Recommendation:** `sentense.com` (no www)

---

### Decision 5: HTTPS

- **Status:** Must enforce
- **Action:** Redirect all HTTP → HTTPS
- **Why:** Ranking factor + security

---

## Launch Sequence

### Week -1 (Before Launch)
- [ ] Convert OG images to PNG
- [ ] Complete 6 remaining profile pages
- [ ] Run Lighthouse audit, fix issues
- [ ] Test mobile responsiveness
- [ ] Implement path-based results URLs
- [ ] Add GA4 tracking

### Day 0 (Launch)
- [ ] Deploy to production
- [ ] Submit to Google Search Console
- [ ] Submit sitemap
- [ ] Request indexing for homepage + key pages
- [ ] Submit to Bing Webmaster

### Week 1
- [ ] Write 4 remaining blog posts
- [ ] Create FAQ page
- [ ] Create pricing page
- [ ] Begin backlink outreach
- [ ] Monitor Search Console for issues

### Week 2-4
- [ ] Create comparison pages
- [ ] Add testimonials (as they come in)
- [ ] Expand content based on Search Console data
- [ ] Continue outreach campaign

---

## Effort Estimate

| Category | Items | Time |
|----------|-------|------|
| **Critical** | OG images, profile pages, Lighthouse, mobile, results URLs, GA4 | 7-9 hrs |
| **High Priority** | Blog posts, FAQ, pricing, internal linking | 6 hrs |
| **Total Pre-Launch** | | **13-15 hrs** |

---

## Quick Wins (Can Do Now)

1. ✅ I can create the 6 remaining profile pages
2. ✅ I can create the 4 remaining blog posts
3. ✅ I can create the FAQ page
4. ✅ I can create the pricing page
5. ⏳ Path-based results requires routing implementation

---

*Checklist created: 2026-02-10*
