# LNCP Web App - Phase C Complete

## Frontend Files Created

| File | Description |
|------|-------------|
| `frontend/index.html` | Standalone HTML/CSS/JS app (no build required) |
| `frontend/LNCPApp.jsx` | React component version |

## Design Direction

**Aesthetic**: Editorial/Literary - Like a beautifully typeset manuscript

**Key Design Choices**:
- **Typography**: Playfair Display (display), Source Serif Pro (body), IBM Plex Mono (labels)
- **Color Palette**: Ink (#1a1a1a), Paper (#faf8f5), Sepia (#d4c4a8), Sage (#5d6d5e), Accent (#2d4a3e)
- **Feel**: Warm, literary, thoughtful - matches the writing-focused nature of LNCP

## Screens Implemented

### 1. Welcome Screen
- Introduction to LNCP
- Two paths: Story Prompts vs Lab Prompts
- Quick analysis option for pasting existing text

### 2. Game Mode (Phase-5)
- Progress indicator (0/3 → 3/3)
- Current prompt display
- Textarea for sentence input
- Validation feedback (2-3 sentences required)

### 3. Quick Analyze Screen
- Textarea for pasting text
- Direct analysis without game flow

### 4. Gate Complete Screen
- Celebration when 3/3 groups submitted
- "View My Analysis" CTA

### 5. Results Screen
- **Overview Tab**: Phase-2 outputs (6 metrics with insights)
- **Synthesis Tab**: Phase-3 syntheses (3 semiotic lenses)
- **Reflect Tab**: Phase-4a prompts OR Phase-4b guidance

## Features

✅ **Responsive design** - Works on desktop and mobile  
✅ **Mock API fallback** - Works without backend (demo mode)  
✅ **Smooth animations** - Fade-in and slide transitions  
✅ **Error handling** - Input validation with user-friendly messages  
✅ **Tab navigation** - Overview / Synthesis / Reflect  
✅ **Phase-4 toggle** - Switch between Prompting and Guidance modes  

## Running the Frontend

### Option 1: Standalone HTML (No Backend Required)

```bash
cd frontend
open index.html  # or just double-click the file
```

The app will run in **demo mode** with mock data.

### Option 2: With Backend

```bash
# Terminal 1: Start backend
cd backend
python api_simple.py --port 8000

# Terminal 2: Serve frontend
cd frontend
python -m http.server 3000
# Then open http://localhost:3000
```

### Option 3: React (requires npm)

```bash
# If using a React project
cp frontend/LNCPApp.jsx src/
# Import and use <LNCPApp /> component
```

## API Integration

The frontend connects to these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/game/init` | Start game session |
| `POST /api/game/submit` | Submit sentence group |
| `POST /api/analyze/{id}` | Run analysis |
| `POST /api/quick-analyze` | Quick analysis |

If the API is unavailable, the app automatically falls back to mock mode.

## Mock Mode

When running without the backend, the app uses built-in mock responses:
- Simulates game flow with 3 prompts
- Returns realistic mock analysis results
- Shows "Demo mode" badge at bottom

## Screenshots (Text Description)

**Welcome Screen**:
```
┌─────────────────────────────────────┐
│              LNCP                   │
│    Structural Writing Analysis      │
│                                     │
│  LNCP examines the structure of     │
│  your writing—not what you say,     │
│  but how your sentences are built.  │
│                                     │
│  [Begin with Story] [Begin with Lab]│
│                                     │
│     or paste your own text →        │
└─────────────────────────────────────┘
```

**Game Mode**:
```
┌─────────────────────────────────────┐
│  ● ○ ○   0 of 3                     │
│                                     │
│  PROMPT 1                           │
│  "Write 2–3 sentences about a       │
│   moment of quiet realization."     │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ Write your sentences here...│    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
│  Write 2–3 sentences      [Submit]  │
└─────────────────────────────────────┘
```

**Results Screen**:
```
┌─────────────────────────────────────┐
│  [Overview] [Synthesis] [Reflect]   │
│                                     │
│  PRESENTATION MODE                  │
│  Descriptive — We describe what     │
│  appears in this sample.            │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ How Much You Shared           │  │
│  │ 6 sentences present.          │  │
│  │ • A sample to work with.      │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Structural Fingerprints       │  │
│  │ Each sentence has a unique... │  │
│  └───────────────────────────────┘  │
│                                     │
│           [Start Over]              │
└─────────────────────────────────────┘
```

## Ready for Phase D

Phase C is complete. The frontend provides:

✅ Welcome/intro screen  
✅ Game mode UI (Phase-5)  
✅ Quick analyze screen  
✅ Gate completion screen  
✅ Results display (Phase-2, 3, 4a, 4b)  
✅ Tab navigation  
✅ Mock API fallback  
✅ Responsive design  
✅ Editorial/literary aesthetic  

Next: **Phase D - Results Display Polish** (already included in Phase C)

Or: **Phase E - State Management & UX Polish**
