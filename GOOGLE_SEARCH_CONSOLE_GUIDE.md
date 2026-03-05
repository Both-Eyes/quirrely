# Google Search Console Setup Guide

## Overview

This guide walks you through submitting Sentense to Google Search Console for all four Commonwealth markets.

---

## Step 1: Create Google Search Console Account

1. Go to https://search.google.com/search-console
2. Sign in with your Google account
3. Click "Add Property"

---

## Step 2: Add Your Domain

### Option A: Domain Property (Recommended)

1. Select "Domain" property type
2. Enter: `sentense.com`
3. Click "Continue"
4. Copy the TXT record provided
5. Add to your DNS settings:
   - Type: TXT
   - Name: @ (or leave blank)
   - Value: (paste the record)
6. Wait for DNS propagation (up to 48 hours)
7. Click "Verify"

### Option B: URL Prefix (Faster)

1. Select "URL prefix" property type
2. Enter: `https://sentense.com`
3. Choose verification method:
   - **HTML file** (recommended): Download and upload to root
   - **HTML tag**: Add to `<head>` section
   - **Google Analytics**: If already installed
4. Click "Verify"

---

## Step 3: Submit Sitemap

1. In Search Console, go to "Sitemaps" (left sidebar)
2. Enter sitemap URL: `sitemap.xml`
3. Click "Submit"
4. Verify status shows "Success"

---

## Step 4: Set Up International Targeting

For each country, you should:

### Add URL Parameters (if using ?locale=XX pattern)

1. Go to Settings → URL Parameters
2. Add: `locale`
3. Set "Googlebot behavior": Let Googlebot decide

### Verify Hreflang Implementation

1. Use Google's Rich Results Test: https://search.google.com/test/rich-results
2. Enter your URL
3. Check that hreflang tags are detected

---

## Step 5: Create Separate Properties (Optional but Recommended)

For comprehensive tracking, add each locale as a separate property:

| Property URL | Market |
|--------------|--------|
| https://sentense.com/?locale=CA | Canada |
| https://sentense.com/?locale=UK | United Kingdom |
| https://sentense.com/?locale=AU | Australia |
| https://sentense.com/?locale=NZ | New Zealand |

Or, if using subdomains:

| Property URL | Market |
|--------------|--------|
| https://ca.sentense.com | Canada |
| https://uk.sentense.com | United Kingdom |
| https://au.sentense.com | Australia |
| https://nz.sentense.com | New Zealand |

---

## Step 6: Request Indexing

For priority pages, manually request indexing:

1. Go to "URL Inspection" (top search bar)
2. Enter URL (e.g., `https://sentense.com/`)
3. Click "Request Indexing"

Request indexing for:
- [ ] Homepage
- [ ] /profiles/assertive
- [ ] /profiles/poetic
- [ ] /profiles/conversational
- [ ] /profiles/minimal
- [ ] /blog/what-is-writing-voice
- [ ] /blog/canadian-writing-style

---

## Step 7: Set Up Bing Webmaster Tools (Bonus)

1. Go to https://www.bing.com/webmasters
2. Sign in with Microsoft account
3. Import from Google Search Console (easiest)
4. Or add site manually
5. Submit sitemap

---

## Verification Checklist

- [ ] Main domain verified in Search Console
- [ ] Sitemap submitted and accepted
- [ ] Hreflang tags validated
- [ ] Key pages requested for indexing
- [ ] Bing Webmaster Tools set up

---

## Monitoring Schedule

### Weekly
- Check "Coverage" for indexing issues
- Review "Performance" for search queries
- Look for new "Manual Actions" (penalties)

### Monthly
- Review "Core Web Vitals" report
- Check "Mobile Usability" issues
- Analyze top queries for content opportunities
- Compare country performance

---

## Common Issues & Fixes

### "Discovered - currently not indexed"
- Page may be low-quality or duplicate
- Add internal links to the page
- Improve content depth

### "Crawled - currently not indexed"
- Google found the page but didn't add it
- Improve content quality
- Check for thin content

### "Page with redirect"
- Redirect is working, not an error
- No action needed

### Mobile Usability Issues
- Test on mobile
- Fix viewport settings
- Ensure buttons are tap-friendly

---

## Expected Timeline

| Milestone | Timeframe |
|-----------|-----------|
| Initial indexing | 3-7 days |
| Homepage ranking | 1-2 weeks |
| Blog posts ranking | 2-4 weeks |
| Profile pages ranking | 2-4 weeks |
| First page rankings | 1-3 months |
| Stable rankings | 3-6 months |

---

## Resources

- [Google Search Console Help](https://support.google.com/webmasters)
- [Google's SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
- [Bing Webmaster Help](https://www.bing.com/webmasters/help)

---

*Guide created: 2026-02-10*
