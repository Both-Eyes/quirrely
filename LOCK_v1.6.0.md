# SENTENSE v1.6.0 — LOCKED

## Lock Information

| Field | Value |
|-------|-------|
| **Version** | 1.6.0 |
| **Codename** | "Bookworm" |
| **Lock Date** | February 10, 2026 23:00 UTC |
| **Lock Type** | Affiliate System Integration |
| **Previous Version** | v1.5.0 "Guardian" |

---

## What's New in v1.6.0

### Affiliate Book Recommendation System

Country-specific book recommendations with affiliate links to national bookstores.

#### Retailers
| Country | Retailer | Network | Commission |
|---------|----------|---------|------------|
| 🍁 Canada | Indigo | Rakuten | 6% |
| 🇬🇧 UK | Waterstones | Awin | 6% |
| 🇦🇺 Australia | Booktopia | Direct | 7% |
| 🇳🇿 New Zealand | Mighty Ape | Direct | 6% |

#### Book Catalog
- **48 curated books** (8 profiles × 2 stances × 3 books)
- Price target: $28-35 hardcovers (1.5-1.7x revenue)
- Selection criteria: price × velocity × profile match × evergreen

#### Integration Points
- Test results page (60% of revenue)
- Blog posts (future)
- Newsletter (future)
- Featured writer profiles (future)

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `affiliate-config.js` | 191 | Retailer configuration |
| `data/affiliate-books.json` | 512 | 48-book catalog |
| `components/BookRecommendation.html` | 306 | Display component |
| `backend/affiliate_service.py` | 401 | Link generation + tracking |
| `database/schema_affiliates.sql` | 242 | 4 database tables |
| `legal/affiliate-disclosure.html` | 89 | Legal disclosure page |
| `assets/affiliates/*.svg` | 4 files | Retailer logos |

---

## Revenue Projections

### Conservative (Year 1)
| Metric | Value |
|--------|-------|
| Test completions | 219,788 |
| Book impressions | 219,788 |
| Click-through rate | 4% |
| Clicks | 8,792 |
| Conversion rate | 10% |
| Purchases | 879 |
| Avg commission | $1.68 |
| **Year 1 Revenue** | **$1,477** |

### With All Touchpoints (Year 1)
| Metric | Value |
|--------|-------|
| Total impressions | ~500,000 |
| Total clicks | ~20,000 |
| Purchases | ~2,000 |
| **Year 1 Revenue** | **$3,360** |

### Optimized (Good Curation)
| Metric | Value |
|--------|-------|
| CTR | 8% |
| Conversion | 12% |
| **Year 1 Revenue** | **$6,000-8,000** |

---

## Curation Strategy

### Profile → Psychology → Purchase Trigger

| Profile | Psychology | Book Type | Trigger Copy |
|---------|------------|-----------|--------------|
| ASSERTIVE | Action-oriented | Leadership, business | "Level up your impact" |
| MINIMAL | Efficiency | Design, productivity | "Essential reading" |
| POETIC | Emotional depth | Literary fiction, memoir | "Feed your soul" |
| DENSE | Intellectual | Philosophy, science | "Go deeper" |
| CONVERSATIONAL | Connection | Essays, pop psych | "Join the conversation" |
| HEDGED | Careful analysis | Research, balanced | "Explore all sides" |
| INTERROGATIVE | Curiosity | Mystery, science | "Find answers" |
| LONGFORM | Patience | Epic novels, series | "The complete story" |

---

## Database Schema

```sql
affiliate_retailers    -- 4 retailers (CA, UK, AU, NZ)
affiliate_books        -- Curated catalog
affiliate_clicks       -- Click tracking
affiliate_daily_stats  -- Analytics aggregates
```

---

## Environment Variables

```
INDIGO_AFFILIATE_ID=...
WATERSTONES_AWIN_ID=...
BOOKTOPIA_AFFILIATE_ID=...
MIGHTYAPE_AFFILIATE_ID=...
```

---

## Version History

| Version | Date | Codename | Key Feature |
|---------|------|----------|-------------|
| v1.0.0 | — | — | First stable |
| v1.1.0 | Feb 9 | "The Listener" | Mobile UX |
| v1.4.0 | Feb 10 | "Pre-Flight" | E2E verified |
| v1.5.0 | Feb 10 | "Guardian" | HALO System |
| **v1.6.0** | **Feb 10** | **"Bookworm"** | **Affiliate System** |

---

**LOCKED** ✅

