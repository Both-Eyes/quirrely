# Sentense Blog System — SEO & Access Tiers

## Overview

The blog system has two tiers:

| Tier | Access | Posts | SEO |
|------|--------|-------|-----|
| **PUBLIC** | Everyone | 40 profile+stance posts | Full indexing |
| **PRO** | Subscribers only | Advanced guides, deep dives | noindex, paywall schema |

---

## PUBLIC BLOG POSTS (40 posts)

### URL Structure
```
/blog/how-{profile}-{stance}-writers-write
```

### Examples
- `/blog/how-assertive-closed-writers-write`
- `/blog/how-poetic-open-writers-write`
- `/blog/how-hedged-contradictory-writers-write`

### SEO Implementation

Each public post includes:

#### Meta Tags
```html
<title>{Title} | Sentense</title>
<meta name="description" content="{Unique 150-160 char description}">
<meta name="keywords" content="{5-7 relevant keywords}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{Full URL}">
```

#### Open Graph (Facebook, LinkedIn)
```html
<meta property="og:type" content="article">
<meta property="og:url" content="{Full URL}">
<meta property="og:title" content="{Title}">
<meta property="og:description" content="{Description}">
<meta property="og:image" content="{Profile+Stance specific image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="article:tag" content="{profile} writing">
<meta property="article:tag" content="{stance} voice">
```

#### Twitter Cards
```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Title}">
<meta name="twitter:description" content="{Description}">
<meta name="twitter:image" content="{Profile+Stance specific image}">
<meta name="twitter:site" content="@sentenseapp">
```

#### Structured Data (JSON-LD)
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{Title}",
  "description": "{Description}",
  "image": "{Image URL}",
  "author": {"@type": "Organization", "name": "Sentense"},
  "publisher": {"@type": "Organization", "name": "Sentense"},
  "datePublished": "2026-02-01",
  "isAccessibleForFree": true
}
```

### Unique Meta Descriptions (40 total)

Each profile+stance has a unique, keyword-rich description:

| Profile+Stance | Description |
|----------------|-------------|
| ASSERTIVE-OPEN | Learn how ASSERTIVE + OPEN writers combine conviction with curiosity. Direct statements that invite dialogue. Examples from Ondaatje, McEwan, Flanagan. |
| ASSERTIVE-CLOSED | Master the ASSERTIVE + CLOSED writing style. High certainty, no hedging. The definitive voice used by Atwood, Orwell, and Winton. |
| POETIC-OPEN | Learn POETIC + OPEN writing: lyrical and curious. The wondering voice of Ondaatje, Virginia Woolf, and Patricia Grace. |
| ... | (38 more unique descriptions) |

### OG Images (40 images needed)

Each post needs a unique 1200x630 OG image:

**Naming Convention:**
```
/blog/images/{profile}-{stance}.png
```

**Examples:**
- `/blog/images/assertive-closed.png`
- `/blog/images/poetic-open.png`

**Design Specs:**
- Size: 1200x630px
- Format: PNG
- Background: Gradient from profile color to stance color
- Text: Profile + Stance name
- Branding: Sentense logo in corner

---

## PRO-ONLY BLOG POSTS

### Access Control

Pro posts use a paywall check before showing content:

```javascript
// Check pro status
const isPro = localStorage.getItem('sentense_pro') === 'true';

if (!isPro) {
  // Show teaser + upgrade CTA
  showPaywall();
} else {
  // Show full content
  showContent();
}
```

### SEO for Paywalled Content

Pro posts use different meta tags to comply with Google guidelines:

```html
<!-- Prevent indexing of full content -->
<meta name="robots" content="noindex, nofollow">

<!-- OR use paywall structured data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "isAccessibleForFree": false,
  "hasPart": {
    "@type": "WebPageElement",
    "isAccessibleForFree": false,
    "cssSelector": ".pro-content"
  }
}
</script>
```

### Pro Post Topics (Planned)

| Category | Topics |
|----------|--------|
| **Deep Dives** | "The Psychology of Your Writing Voice", "How Your Stance Reveals Your Worldview" |
| **Improvement Guides** | "How to Shift from HEDGED to ASSERTIVE", "Adding POETIC Elements to FORMAL Writing" |
| **Professional Use** | "Writing Voice for Different Industries", "Matching Your Voice to Your Audience" |
| **Advanced Analysis** | "Dual Profile Writers", "When Your Voice and Stance Conflict" |

---

## Image Generation Specs

### OG Images (Public Posts)

**For Each of 40 Combinations:**

```
Filename: {profile}-{stance}.png
Size: 1200x630
Background: linear-gradient(135deg, {profile-color}, {stance-color})
Content:
  - Profile badge: {PROFILE} (white text, semi-transparent bg)
  - Stance badge: + {STANCE} (white text, dark bg)
  - Title: "How {PROFILE} + {STANCE} Writers Write"
  - Sentense logo (bottom right)
```

**Color Reference:**
```
ASSERTIVE: #FF6B6B
MINIMAL: #FDCB6E
POETIC: #A29BFE
DENSE: #6C5CE7
CONVERSATIONAL: #4ECDC4
FORMAL: #2D3436
BALANCED: #74B9FF
LONGFORM: #00B894
INTERROGATIVE: #E17055
HEDGED: #B2BEC3

OPEN: #4ECDC4
CLOSED: #FF6B6B
BALANCED: #A29BFE
CONTRADICTORY: #FDCB6E
```

### Twitter Images

Same as OG images (summary_large_image uses same dimensions).

---

## Sitemap Entries

### Public Posts (add to sitemap.xml)
```xml
<!-- Blog Posts - 40 Profile+Stance Combinations -->
<url>
  <loc>https://sentense.com/blog/how-assertive-open-writers-write</loc>
  <lastmod>2026-02-01</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.7</priority>
</url>
<!-- ... repeat for all 40 combinations -->
```

### Pro Posts (do NOT add to sitemap)
Pro-only posts should not be in the sitemap since they are not publicly accessible.

---

## Internal Linking Strategy

### From Public Posts
Each public post links to:
1. **Adjacent styles** (L/R navigation)
2. **The main analyzer tool** (CTA)
3. **Related writer pages** (if created)

### From Pro Posts
Pro posts can link to:
1. Public posts (for context)
2. Other pro posts (cross-sell)
3. Account upgrade page

---

## Performance Checklist

- [ ] All 40 public posts have unique meta descriptions
- [ ] All 40 OG images created (1200x630)
- [ ] Structured data validates (test with Google Rich Results)
- [ ] All 40 URLs added to sitemap.xml
- [ ] Canonical URLs set correctly
- [ ] robots.txt allows /blog/ directory
- [ ] Internal links working (L/R navigation)
- [ ] Pro posts have paywall schema OR noindex

---

---

## FEATURED WRITERS SYSTEM

### Overview

Every week, we feature 4 writers—one from each country (CA, UK, AU, NZ)—showcasing real examples of different writing voices. This creates:

1. **User-generated content** — Fresh, authentic writing samples
2. **Community engagement** — Users aspire to be featured
3. **Pro value proposition** — Exclusive submission access
4. **SEO benefit** — Regular new content, long-tail keywords

### Access Tiers

| Feature | Free Users | Pro Users |
|---------|------------|-----------|
| View featured writers | ✅ | ✅ |
| View archive | ✅ | ✅ |
| Submit writing | ❌ | ✅ |
| Get featured | ❌ | ✅ |

### Weekly Cadence

**Monday:** Submissions close for current week
**Tuesday:** Editorial review (1-2 hours)
**Wednesday:** Featured writers announced
**Thursday-Sunday:** Submissions open for next week

### Selection Criteria

1. **Authenticity** — Writing matches their Sentense profile
2. **Quality** — Clear, engaging, well-crafted
3. **Diversity** — Different profiles/stances each week
4. **Originality** — No copied or AI-generated content

### Files

| File | Purpose |
|------|---------|
| `featured-writer-system.html` | Public showcase page |
| `submit-writing.html` | Pro submission form |

### Database Schema (for backend)

```sql
CREATE TABLE featured_submissions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  sample TEXT NOT NULL,
  display_name VARCHAR(50) NOT NULL,
  bio VARCHAR(100),
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  country CHAR(2) NOT NULL,
  submitted_at TIMESTAMP DEFAULT NOW(),
  status ENUM('pending', 'approved', 'rejected', 'featured') DEFAULT 'pending',
  featured_week DATE,
  permission_feature BOOLEAN DEFAULT TRUE,
  permission_profile BOOLEAN DEFAULT TRUE,
  permission_country BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_submissions_status ON featured_submissions(status);
CREATE INDEX idx_submissions_country ON featured_submissions(country);
CREATE INDEX idx_submissions_week ON featured_submissions(featured_week);
```

### Admin Workflow

1. Query pending submissions by country
2. Review each submission (50-150 words)
3. Verify profile match (does writing match their test results?)
4. Mark as approved/rejected
5. Select 1 per country for featuring
6. Generate weekly page

### Notification System

**On Selection:**
```
Subject: You've Been Featured on Sentense! 🎉

Hi [Name],

Great news! Your writing has been selected for this week's Featured Writers showcase.

Your piece is now live at: https://sentense.com/blog/featured

Your [PROFILE] + [STANCE] voice really shines through in your submission. Thank you for sharing it with our community.

— The Sentense Team
```

**On Rejection (optional):**
```
Subject: Your Sentense Submission

Hi [Name],

Thank you for submitting your writing to be featured. While we weren't able to include it this week, we encourage you to submit again.

Tips for next time:
- Ensure your writing reflects your [PROFILE] + [STANCE] profile
- Keep it between 50-150 words
- Choose a topic that lets your natural voice shine

— The Sentense Team
```

---

## NEWSLETTER INTEGRATION

### Hard Rule
**Featured writer content = 50%+ of weekly newsletter**

### Newsletter Structure

```
SUBJECT: This Week's Voices: 🍁 Sarah M. · 🇬🇧 James T. · 🇦🇺 Mei L. · 🇳🇿 Te Koha R.

---

[HEADER IMAGE]

4 WRITERS. 4 COUNTRIES. 4 VOICES.

This week's featured writers from the Sentense community.

---

🍁 SARAH M. — CONVERSATIONAL + OPEN
Toronto, Canada

"So here is the thing about starting a business in your forties. 
Everyone tells you it is too late, but honestly? I think it might 
be exactly the right time. What do you think—is there ever a 
wrong moment to chase what matters?"

→ Read more from Sarah: [Profile Link]
→ Her newsletter: [Substack Link]

---

🇬🇧 JAMES T. — ASSERTIVE + BALANCED
Edinburgh, UK

"Remote work increases productivity. The data is clear. But office 
culture has value too—collaboration suffers at a distance. Both 
matter. Here is how to hold them together."

→ Read more from James: [Profile Link]
→ Connect on LinkedIn: [LinkedIn Link]

---

[... AU and NZ writers ...]

---

DISCOVER YOUR VOICE

These writers know their style. Do you?

[TAKE THE FREE TEST →]

---

[Footer with unsubscribe, etc.]
```

### Newsletter Metrics to Track

| Metric | Target |
|--------|--------|
| Open rate | 35%+ |
| Click-through to profiles | 10%+ |
| Click-through to test | 5%+ |
| External link clicks | Track per writer |

### Content Breakdown

| Section | % of Newsletter |
|---------|-----------------|
| Featured writers (4 × ~100 words) | 50-60% |
| CTA to take test | 15% |
| Other content (tips, updates) | 25-35% |

---

## PUBLIC USER PROFILES

### Access Rules

| User Type | Profile Visibility |
|-----------|-------------------|
| Free user | Private (no public profile) |
| Pro user (default) | Private |
| Pro user (opted in) | Public |
| Featured writer | Public (required for featuring) |

### Profile URL Structure
```
/writer/{username}
```

Example: `/writer/sarah-m-toronto`

### Profile Contains

1. **Display name** — e.g., "Sarah M."
2. **Location** — Country + optional city
3. **Profile + Stance badges**
4. **One-line bio**
5. **External links** (LinkedIn, Newsletter, Facebook)
6. **Featured writing samples** — All times they were featured

### External Links Allowed

| Platform | Field |
|----------|-------|
| LinkedIn | `linkedin.com/in/...` |
| Newsletter/Substack | `*.substack.com` or custom |
| Facebook | `facebook.com/...` |

### Database Schema

```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  display_name VARCHAR(50) NOT NULL,
  city VARCHAR(50),
  country CHAR(2) NOT NULL,
  bio VARCHAR(100),
  profile VARCHAR(20) NOT NULL,
  stance VARCHAR(20) NOT NULL,
  
  -- External links
  link_linkedin VARCHAR(255),
  link_newsletter VARCHAR(255),
  link_facebook VARCHAR(255),
  
  -- Privacy
  is_public BOOLEAN DEFAULT FALSE,
  is_pro BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE featured_history (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  sample TEXT NOT NULL,
  featured_week DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profiles_public ON user_profiles(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_profiles_country ON user_profiles(country);
```

---

## Expected SEO Impact

### Month 1
- 40 pages indexed
- Long-tail keyword visibility for "writing style" + "voice" queries
- ~500 organic sessions

### Month 6
- Featured snippets for "how do [profile] writers write"
- ~5,000 organic sessions
- Backlinks from writing blogs

### Month 12
- Authority for "writing voice" topic cluster
- ~15,000 organic sessions
- Top 10 rankings for multiple profile+stance combinations
