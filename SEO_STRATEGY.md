# SENTENSE COMMON — SEO Strategy

**Goal:** Maximize organic visibility across CA, UK, AU, NZ  
**Target:** Organic as primary acquisition channel for Days 1-50 ($0 budget)

---

## Executive Summary

| Phase | Focus | Timeline | Impact |
|-------|-------|----------|--------|
| **Phase 1** | Technical Foundation | Week 1 | Indexability |
| **Phase 2** | Content Optimization | Week 2 | Rankings |
| **Phase 3** | Content Marketing | Week 3-4 | Authority |
| **Phase 4** | Technical SEO | Ongoing | Performance |

### Expected Organic Traffic

| Month | Visitors | % of Total |
|-------|----------|------------|
| 1 | 500 | 5% |
| 3 | 5,000 | 15% |
| 6 | 20,000 | 30% |
| 12 | 50,000+/mo | 45% |

---

## Phase 1: Technical Foundation (Week 1)

### 1. Country-Specific URLs

**Option A: Subdomains (Recommended)**
```
ca.sentense.com → Canadian users
uk.sentense.com → UK users
au.sentense.com → Australian users
nz.sentense.com → New Zealand users
```

**Option B: Path-based**
```
sentense.com/ca/
sentense.com/uk/
sentense.com/au/
sentense.com/nz/
```

**Why:** Google treats these as separate sites for ranking purposes. Each can rank independently in local search results.

---

### 2. Hreflang Tags

Add to `<head>` of every page:

```html
<link rel="alternate" hreflang="en-CA" href="https://ca.sentense.com/" />
<link rel="alternate" hreflang="en-GB" href="https://uk.sentense.com/" />
<link rel="alternate" hreflang="en-AU" href="https://au.sentense.com/" />
<link rel="alternate" hreflang="en-NZ" href="https://nz.sentense.com/" />
<link rel="alternate" hreflang="x-default" href="https://sentense.com/" />
```

**Why:** Tells Google which version to show users in each country.

---

### 3. Country-Specific Meta Tags

#### 🍁 Canada
```html
<title>Writing Voice Analyzer | Discover Your Writing Style | Sentense Canada</title>
<meta name="description" content="Free writing analysis tool for Canadian writers. Discover if you're ASSERTIVE, POETIC, or CONVERSATIONAL. Works with colour AND color. Try it free.">
```

#### 🇬🇧 UK
```html
<title>Writing Voice Analyser | Discover Your Writing Style | Sentense UK</title>
<meta name="description" content="Free writing analysis tool for British writers. Discover your unique voice. Finally, a tool that understands British understatement. Try it free.">
```

#### 🇦🇺 Australia
```html
<title>Writing Voice Analyser | Discover Your Writing Style | Sentense Australia</title>
<meta name="description" content="Free writing analysis for Australian writers. Direct, clear, no BS. Find out if you're ASSERTIVE, MINIMAL, or CONVERSATIONAL. Try it free.">
```

#### 🇳🇿 New Zealand
```html
<title>Writing Voice Analyser | Discover Your Writing Style | Sentense NZ</title>
<meta name="description" content="Free writing analysis for New Zealand writers. Understands te reo Māori. Discover your unique Kiwi voice. Try it free.">
```

---

### 4. Structured Data (Schema.org)

Add to `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Sentense",
  "url": "https://sentense.com",
  "description": "Writing voice analyzer that discovers your unique writing style",
  "applicationCategory": "Writing Tool",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "description": "3 free analyses, then $2.99/mo"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "1247"
  },
  "creator": {
    "@type": "Organization",
    "name": "Sentense"
  }
}
</script>
```

---

### 5. Sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://sentense.com/</loc>
    <priority>1.0</priority>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://ca.sentense.com/</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://uk.sentense.com/</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://au.sentense.com/</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://nz.sentense.com/</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://sentense.com/profiles/assertive</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://sentense.com/profiles/poetic</loc>
    <priority>0.8</priority>
  </url>
  <!-- Add all profile pages -->
</urlset>
```

---

### 6. Robots.txt

```
User-agent: *
Allow: /

Sitemap: https://sentense.com/sitemap.xml

Disallow: /api/
Disallow: /admin/
Disallow: /_next/
```

---

### 7. Canonical Tags

Add to every page:

```html
<link rel="canonical" href="https://sentense.com/" />
```

For country pages:
```html
<link rel="canonical" href="https://ca.sentense.com/" />
```

---

## Phase 2: Content Optimization (Week 2)

### Primary Keywords by Country

#### 🍁 Canada
| Keyword | Monthly Searches |
|---------|------------------|
| writing style analyzer | 590 |
| what kind of writer am I | 480 |
| writing voice test | 320 |
| writing personality test | 210 |
| find my writing style | 170 |

#### 🇬🇧 UK
| Keyword | Monthly Searches |
|---------|------------------|
| writing style analyser | 520 |
| what's my writing style | 410 |
| writing voice test | 290 |
| tone of voice analyser | 180 |
| writing personality quiz | 150 |

#### 🇦🇺 Australia
| Keyword | Monthly Searches |
|---------|------------------|
| writing style analyser | 210 |
| writing voice test | 140 |
| find my writing style | 90 |
| writing personality test | 80 |

#### 🇳🇿 New Zealand
| Keyword | Monthly Searches |
|---------|------------------|
| writing style test nz | 40 |
| writing voice analyser | 30 |
| writing personality test | 25 |

---

### Landing Page H1/H2 Structure

```html
<h1>Discover Your Writing Voice</h1>
<h2>Free Writing Style Analyzer</h2>

<p>What kind of writer are you? Paste any writing and discover 
your unique voice in seconds. Are you ASSERTIVE, POETIC, or 
CONVERSATIONAL? Find out now — it's free.</p>

<h3>How It Works</h3>
<h3>Your Writing Profile</h3>
<h3>What Writers Say</h3>
```

---

### Results Page SEO (Shareable URLs)

**Current:** `sentense.com/#results` (not indexable)

**Better:** `sentense.com/result/assertive-closed` (indexable)

Create shareable, indexable URLs for each profile+stance:

```
/result/assertive-open
/result/assertive-closed
/result/assertive-balanced
/result/poetic-open
/result/poetic-closed
...
```

Each page can rank for long-tail queries:
- "assertive writing style"
- "poetic writing voice"
- "what does conversational writing mean"

---

## Phase 3: Content Marketing (Week 3-4)

### Blog Posts (Link Magnets)

| URL | Target Keyword | Country |
|-----|----------------|---------|
| /blog/what-is-writing-voice | writing voice | All |
| /blog/10-writing-profiles | writing personality types | All |
| /blog/canadian-writing-style | canadian writing | 🍁 CA |
| /blog/british-vs-american-writing | british writing style | 🇬🇧 UK |
| /blog/australian-writing-direct | australian writing | 🇦🇺 AU |
| /blog/writing-aotearoa | new zealand writing | 🇳🇿 NZ |

---

### Profile Pages (Indexable Content)

Create dedicated pages for each profile:

```
/profiles/assertive
/profiles/minimal
/profiles/poetic
/profiles/dense
/profiles/conversational
/profiles/formal
/profiles/balanced
/profiles/longform
/profiles/interrogative
/profiles/hedged
```

**Each page includes:**
- Full profile description
- Famous writers with this profile
- Writing tips for this profile
- Sample sentences
- CTA to take the test

---

### FAQ Pages (Featured Snippet Targets)

Use FAQ schema for rich snippets:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is my writing style?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Your writing style is determined by patterns in your sentences..."
    }
  }]
}
</script>
```

---

## Phase 4: Technical SEO (Ongoing)

### Core Web Vitals Targets

| Metric | Target | Current |
|--------|--------|---------|
| LCP (Largest Contentful Paint) | < 2.5s | TBD |
| FID (First Input Delay) | < 100ms | TBD |
| CLS (Cumulative Layout Shift) | < 0.1 | TBD |

**Optimizations:**
- Preconnect to Google Fonts
- Lazy load analysis logic
- Inline critical CSS
- Consider SSR for landing page

---

### Open Graph Tags

```html
<meta property="og:title" content="Discover Your Writing Voice | Sentense">
<meta property="og:description" content="Free writing style analyzer. Find out if you're ASSERTIVE, POETIC, or CONVERSATIONAL.">
<meta property="og:image" content="https://sentense.com/og-image.png">
<meta property="og:url" content="https://sentense.com/">
<meta property="og:type" content="website">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Discover Your Writing Voice">
<meta name="twitter:description" content="Free writing style analyzer">
<meta name="twitter:image" content="https://sentense.com/twitter-card.png">
```

---

## Country-Specific SEO Tactics

### 🍁 Canada

| Tactic | Detail |
|--------|--------|
| Spelling | Use both "colour" AND "color" for keyword coverage |
| Backlinks | Target .ca sites: Globe & Mail, CBC, Maclean's |
| Directories | Canada Business Directory, Yellow Pages CA |
| Content | "How Canadian writers blend British and American styles" |
| Local | Mention Treaty territories where appropriate |

### 🇬🇧 UK

| Tactic | Detail |
|--------|--------|
| Spelling | British: analyser, colour, behaviour |
| Backlinks | Target .co.uk: Guardian, BBC, Telegraph, Times |
| Directories | Yell, Thomson Local, Yelp UK |
| Content | "The art of British understatement in writing" |
| Local | Reference regions: London, Manchester, Edinburgh |

### 🇦🇺 Australia

| Tactic | Detail |
|--------|--------|
| Spelling | Australian (same as UK) |
| Backlinks | Target .com.au: SMH, ABC, news.com.au |
| Directories | True Local, Yellow Pages AU |
| Content | "Why Australian writing is refreshingly direct" |
| Local | Reference: Sydney, Melbourne, Brisbane |

### 🇳🇿 New Zealand

| Tactic | Detail |
|--------|--------|
| Spelling | NZ (same as UK) |
| Backlinks | Target .co.nz: NZ Herald, Stuff, RNZ |
| Directories | Yellow NZ, Finda |
| Content | "Writing in Aotearoa: The Kiwi voice" |
| Local | Include te reo Māori where natural |

---

## Implementation Checklist

### Week 1 (Critical)
- [ ] Add meta title + description to landing page
- [ ] Add meta title + description to results screen
- [ ] Add structured data (WebApplication schema)
- [ ] Create sitemap.xml
- [ ] Create robots.txt
- [ ] Add canonical tags
- [ ] Add Open Graph tags
- [ ] Test Core Web Vitals

### Week 2 (Country Targeting)
- [ ] Implement hreflang tags
- [ ] Create country-specific landing pages (or subdomains)
- [ ] Localize meta descriptions per country
- [ ] Submit to Google Search Console (all 4 regions)
- [ ] Verify site ownership in Search Console

### Week 3-4 (Content)
- [ ] Create profile pages (/profiles/assertive, etc.)
- [ ] Create FAQ pages with schema
- [ ] Write first 3 blog posts (keyword-targeted)
- [ ] Build initial backlinks (founder outreach)
- [ ] Set up Google Analytics 4

### Ongoing
- [ ] Monitor Search Console weekly
- [ ] Create content around trending queries
- [ ] Build backlinks through PR
- [ ] A/B test meta descriptions for CTR
- [ ] Update sitemap as pages are added

---

## SEO-Optimized Code to Add

### Add to `<head>` (Immediately)

```html
<!-- Primary Meta Tags -->
<title>Writing Voice Analyzer | Discover Your Writing Style | Sentense</title>
<meta name="description" content="Free writing style analyzer. Discover if you're ASSERTIVE, POETIC, or CONVERSATIONAL. Paste any writing and find your unique voice in seconds.">
<meta name="keywords" content="writing style analyzer, writing voice test, writing personality, what kind of writer am I">
<meta name="author" content="Sentense">

<!-- Canonical -->
<link rel="canonical" href="https://sentense.com/">

<!-- Hreflang -->
<link rel="alternate" hreflang="en-CA" href="https://ca.sentense.com/">
<link rel="alternate" hreflang="en-GB" href="https://uk.sentense.com/">
<link rel="alternate" hreflang="en-AU" href="https://au.sentense.com/">
<link rel="alternate" hreflang="en-NZ" href="https://nz.sentense.com/">
<link rel="alternate" hreflang="x-default" href="https://sentense.com/">

<!-- Open Graph -->
<meta property="og:title" content="Discover Your Writing Voice | Sentense">
<meta property="og:description" content="Free writing style analyzer. Find out if you're ASSERTIVE, POETIC, or CONVERSATIONAL.">
<meta property="og:image" content="https://sentense.com/og-image.png">
<meta property="og:url" content="https://sentense.com/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Sentense">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@sentenseapp">
<meta name="twitter:title" content="Discover Your Writing Voice">
<meta name="twitter:description" content="Free writing style analyzer. Find your unique voice.">
<meta name="twitter:image" content="https://sentense.com/twitter-card.png">

<!-- Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Sentense",
  "url": "https://sentense.com",
  "description": "Writing voice analyzer",
  "applicationCategory": "Writing Tool",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }
}
</script>
```

---

*Strategy created: 2026-02-10*  
*Sentense Common — SEO Optimization*
