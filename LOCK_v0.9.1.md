# LNCP v0.9.1 - LOCKED
**Lock Date:** February 8, 2026

## Release Summary
Voice-matched shareable profile cards with book referral integration.

## Changes from v0.9.0
- **WRITER_BOOKS** data structure added (50+ writers × 3 books each)
- **Book recommendation on cards**: `find that voice in "Book Title"`
- **Affiliate link ready**: Amazon search URL with `tag=AFFILIATE_TAG` placeholder
- **Removed duplicate READING_LISTS** (code cleanup, -370 lines)

## Profile Card Structure
```
MY WRITING VOICE
[icon]
Profile Title

"Voice-matched quote line 1
Voice-matched quote line 2
Voice-matched quote line 3"

— like [Writer Name]
find that voice in "[Signature Book]"   ← clickable, teal

═══════════════════════════════════════

What's YOUR writing voice?
lncp.app
```

## Monetization Ready
- Book links point to: `amazon.com/s?k=[Book]+[Author]&tag=AFFILIATE_TAG`
- Replace `AFFILIATE_TAG` with actual Amazon Associates tag
- Each of 50+ writers has 3 books; first book shown on card

## File Stats
- `index.html`: 4,434 lines (down from 4,804)
- 10 example cards in `/lncp-cards/`
- WRITER_BOOKS: ~150 book entries

## Verified
✅ Voice-matched quotes (40 profile/stance combos)
✅ Book recommendations on all cards
✅ Affiliate URL structure
✅ JavaScript syntax valid
✅ All cards updated
