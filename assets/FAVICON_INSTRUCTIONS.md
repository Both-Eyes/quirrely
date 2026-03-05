# Favicon Generation Instructions

## Source File
`favicon.svg` — The master SVG favicon

## Required Sizes
Generate these PNG files from the SVG:

### Standard Favicons
- `favicon-16x16.png` — Browser tabs
- `favicon-32x32.png` — Browser tabs (retina)
- `favicon.ico` — Legacy browsers (include 16, 32, 48)

### Apple Touch Icons
- `apple-touch-icon.png` — 180x180 (iOS home screen)
- `apple-touch-icon-precomposed.png` — 180x180

### Android/PWA Icons
Place in `/icons/` folder:
- `icon-72.png`
- `icon-96.png`
- `icon-128.png`
- `icon-144.png`
- `icon-152.png`
- `icon-192.png`
- `icon-384.png`
- `icon-512.png`

### Microsoft Tile
- `mstile-150x150.png`

## Generation Tools
1. **RealFaviconGenerator.net** — Upload SVG, download all sizes
2. **Sharp (Node.js)** — Programmatic generation
3. **ImageMagick** — Command line

## HTML to Add
```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#FF6B6B">
<meta name="msapplication-TileColor" content="#FF6B6B">
```
