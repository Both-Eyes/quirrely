# Quirrely Browser Extension

**Version:** 1.0.0  
**Platform:** Chrome (Manifest V3)

Discover your unique writing voice with LNCP-powered structural analysis, anywhere on the web.

---

## Features

### 🚀 Instant Analysis
- Analyze any selected text with one click
- Get your profile type, stance, and confidence score
- See unique traits derived from your writing structure

### 🌐 Works Everywhere
- Floating button appears on text selection
- Right-click context menu integration
- Keyboard shortcut (Ctrl+Shift+Q / ⌘+Shift+Q)

### 📊 Track Your Voice
- Local history of all analyses
- See your dominant profile over time
- Export history as JSON

### 🔒 Privacy First
- All analysis runs locally in the browser
- No data sent to servers without consent
- Optional anonymous data contribution

---

## Installation

### Development (Unpacked)

1. Clone or download this folder
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)
4. Click "Load unpacked"
5. Select the `quirrely-extension` folder
6. The extension is now installed!

### Production (Chrome Web Store)

Coming soon - pending Chrome Web Store submission.

---

## File Structure

```
quirrely-extension/
├── manifest.json           # Extension configuration
├── icons/
│   └── icon.svg           # Source icon (convert to PNG for production)
├── pages/
│   ├── popup.html         # Main popup interface
│   ├── popup.js           # Popup controller
│   ├── options.html       # Settings page
│   └── welcome.html       # First-install welcome page
├── scripts/
│   ├── background.js      # Service worker (message handling, context menu)
│   ├── content.js         # Content script (selection detection, floating button)
│   ├── lncp-classifier.js # LNCP v3.8 classifier (self-contained)
│   ├── storage.js         # Storage manager (optional, for advanced use)
│   └── api-client.js      # API client (for future server sync)
└── styles/
    ├── popup.css          # Popup styles
    └── content.css        # Content script styles
```

---

## Building for Production

### 1. Generate Icons

Convert `icons/icon.svg` to PNG at required sizes:
- icon-16.png (16x16)
- icon-32.png (32x32)
- icon-48.png (48x48)
- icon-128.png (128x128)

You can use tools like:
- [SVG to PNG converter](https://svgtopng.com/)
- ImageMagick: `convert -background none -resize 128x128 icon.svg icon-128.png`

### 2. Zip for Submission

```bash
cd quirrely-extension
zip -r quirrely-extension.zip . -x "*.git*" -x "*.DS_Store"
```

### 3. Submit to Chrome Web Store

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
2. Create new item
3. Upload the ZIP file
4. Fill in listing details
5. Submit for review

---

## Usage

### From Popup
1. Click the Quirrely icon in the toolbar
2. Paste or type text in the input area (min 50 characters)
3. Click "Analyze My Voice"
4. View your profile result

### From Any Webpage
1. Select text on any webpage (min 50 characters)
2. Click the floating Quirrely button that appears
3. Or right-click and select "Analyze with Quirrely"
4. View the result popup

### Keyboard Shortcut
- **Windows/Linux:** Ctrl+Shift+Q
- **Mac:** ⌘+Shift+Q

---

## Permissions

| Permission | Purpose |
|------------|---------|
| `storage` | Store settings, history, and session data locally |
| `activeTab` | Access selected text on the current page |
| `contextMenus` | Add "Analyze with Quirrely" to right-click menu |
| `alarms` | Schedule periodic sync (when connected to server) |

---

## Privacy

- **Local Analysis:** The LNCP classifier runs entirely in your browser
- **No Server Required:** Basic analysis works offline
- **Optional Sync:** Future versions will offer opt-in server sync
- **Anonymous Data:** You can choose to help improve Quirrely with anonymous pattern data

See [Privacy Policy](https://quirrely.com/privacy) for full details.

---

## API Integration (Future)

The extension is designed to work with the Quirrely API when available:

- Sync analysis history across devices
- Access profile evolution tracking
- Unlock Pro features with subscription

The API client (`scripts/api-client.js`) is ready for integration once the backend is deployed.

---

## Troubleshooting

### Button doesn't appear on selection
- Ensure the setting "Show floating button" is enabled
- Some sites block extension content scripts
- Try refreshing the page

### Analysis fails
- Ensure you've selected at least 50 characters
- Check if daily limit is reached (5/day for free)
- Try in the popup instead

### Extension not working
- Go to `chrome://extensions/`
- Ensure Quirrely is enabled
- Click "Reload" to refresh the extension

---

## Development

### Testing Changes

1. Make your changes
2. Go to `chrome://extensions/`
3. Click the refresh icon on the Quirrely card
4. Test your changes

### Adding New Features

1. **Background tasks:** Add to `scripts/background.js`
2. **Page interactions:** Add to `scripts/content.js`
3. **Popup UI:** Modify `pages/popup.html` and `pages/popup.js`
4. **Styles:** Update CSS files in `styles/`

---

## License

© 2026 Quirrely. All rights reserved.

---

## Links

- [Quirrely Website](https://quirrely.com)
- [Privacy Policy](https://quirrely.com/privacy)
- [Terms of Service](https://quirrely.com/terms)
- [Support](https://quirrely.com/support)
