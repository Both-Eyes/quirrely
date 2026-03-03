# Quirrely v3.2.0 — Session 13 Handoff
**Date:** 2026-03-03 | **Tests:** 551/551 | **Version:** 3.1.3 → 3.2.0

## Commits
- `03ebb99` Dashboard QA (logo, nav, STRETCH flow, Featured, Writers 5x, Books 3x, buttons, voice page)
- `64f7ed9` Personalized OG images, `/user/` URLs, social share, viewPublicProfile
- `e27a5e6` Referral comparison viral loop (all flows + dashboard)
- `91f4c93` Security audit (XSS, CORS, dead code, path traversal, slug validation)
- `c5e1b70` Sitemap rebuild (removed auth-gated, added sitemap-users.xml)

## Key Changes
- Dashboard: master squirrel logo, STRETCH landing/resume/abandon, all auth'd users see Writers+Books
- `/user/{slug}` replaces `/voice/{slug}` (301 redirect preserved)
- Personalized OG images via `og_generator.py` (Pillow, auto on claim+refresh)
- Social share: LinkedIn+Facebook on share card + referral comparison
- Referral viral loop: `/?ref=slug` → compare card after analysis → share → signup CTA
- Security: XSS html.escape, CORS quirrely.ca added, null/wildcard removed, db_utils.py deleted, OG path sanitized

## New/Changed Endpoints
- `GET /user/{slug}` public profile | `GET /voice/{slug}` 301 redirect
- `GET /api/v2/share/public/{slug}` public JSON | `POST /api/v2/share/referral/track`
- OG generated on `/api/v2/share/generate` and `/api/v2/share/refresh`

## Architecture
- Apache(80/443)→nginx(8080)→FastAPI(8000). New routes need all three.
- Voice page: `_build_voice_html()` in app.py with `_html.escape()` on all user inputs
- OG images: `/home/quirrely/quirrely.ca/og/users/{slug}.png`
- Master logo: full-body squirrel SVG viewBox 0 0 80 120. Never concept-10.

## Not Done (Next Session)
- Bookstore affiliate integration
- Blog articles
- Auto-generate sitemap-users.xml from DB
