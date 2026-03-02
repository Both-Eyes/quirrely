# LNCP Web App - Phase B Complete

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/game/init` | Initialize game session |
| POST | `/api/game/submit` | Submit sentence group |
| GET | `/api/game/state/{id}` | Get game state |
| POST | `/api/analyze` | Run full analysis |
| POST | `/api/quick-analyze` | Quick analysis (no game) |
| GET | `/api/results/{id}` | Get cached results |
| DELETE | `/api/session/{id}` | Clean up session |

## New Files Created

| File | Purpose | Dependencies |
|------|---------|--------------|
| `api.py` | FastAPI server | fastapi, uvicorn, pydantic |
| `api_simple.py` | Stdlib HTTP server | None (Python stdlib only) |
| `requirements.txt` | Backend dependencies | - |
| `test_api.py` | FastAPI tests | fastapi, httpx |
| `test_api_simple.py` | Direct orchestrator tests | None |

## API Usage Examples

### Initialize Game

```bash
curl -X POST http://localhost:8000/api/game/init \
  -H "Content-Type: application/json" \
  -d '{"mode": "STORY"}'
```

Response:
```json
{
  "session_id": "uuid-here",
  "mode": "STORY",
  "current_prompt": {
    "prompt_id": "PB_001",
    "text": "Write 2–3 sentences..."
  },
  "gate": {
    "required": 3,
    "completed": 0,
    "is_complete": false
  }
}
```

### Submit Sentences

```bash
curl -X POST http://localhost:8000/api/game/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "sentences": [
      "The morning light came through the window.",
      "She made coffee and sat down."
    ]
  }'
```

Response:
```json
{
  "session_id": "uuid-here",
  "state": "PLAY",
  "gate": {"required": 3, "completed": 1, "is_complete": false},
  "current_prompt": {...},
  "last_submission": {"status": "VALID", "message": "Group accepted."},
  "coverage": {"zero": true, "operator": false, "scope": false, "is_satisfied": false},
  "safety": {"actor_state": "NORMAL", "is_deescalating": false, "message": null}
}
```

### Run Analysis (after gate complete)

```bash
curl -X POST "http://localhost:8000/api/analyze?session_id=uuid-here"
```

Response:
```json
{
  "session_id": "uuid-here",
  "sentences_analyzed": ["...", "..."],
  "phase1": {...},
  "phase2": {...},
  "phase3": {...},
  "phase4a": {...},
  "phase4b": {...}
}
```

### Quick Analysis (no game)

```bash
curl -X POST http://localhost:8000/api/quick-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": [
      "The morning light came through the window.",
      "She made coffee and sat down.",
      "Nothing happened for a long time."
    ]
  }'
```

## Running the Server

### Option 1: FastAPI (Production)

```bash
cd backend
pip install -r requirements.txt
python api.py
# Or with uvicorn directly:
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Features:
- Auto-generated OpenAPI docs at `/api/docs`
- Request validation with Pydantic
- Async support

### Option 2: Simple Server (No Dependencies)

```bash
cd backend
python api_simple.py --port 8000
```

Features:
- Zero external dependencies
- Works with Python stdlib only
- Good for development/testing

## Test Results

```
============================================================
LNCP API Tests (Direct Orchestrator)
============================================================

Test 1: Quick Analyze
✅ Quick analyze succeeded
   Sentences: 3
   Phase-1 outputs: 10
   Phase-2 mode: DESCRIPTIVE
   Phase-3 syntheses: 3
   Phase-4a prompt sets: 3
   Phase-4b guidance sets: 3

Test 2: Full Game Flow
✅ Session created
✅ Gate complete (3/3 groups)
✅ Analysis complete
✅ Cached results retrieved
✅ Session cleaned up

Test 3: Error Handling
✅ Invalid session returns None
✅ Single sentence rejected

ALL TESTS PASSED ✅
```

## Session Management

- Sessions stored in memory (orchestrator singleton)
- Each session has unique UUID
- Sessions track:
  - Phase-5 state machine
  - All phase outputs after analysis
  - Sentence groups submitted

**Note**: For production, implement persistent session storage (Redis, database, etc.)

## CORS Configuration

Both servers include CORS headers for frontend access:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

**Note**: Restrict origins in production.

## Ready for Phase C

Phase B is complete. The API layer provides:

✅ Game initialization endpoint  
✅ Sentence submission endpoint  
✅ Game state retrieval  
✅ Full analysis pipeline execution  
✅ Quick analysis (bypass game)  
✅ Session management  
✅ CORS support  
✅ Error handling  
✅ Two server options (FastAPI / stdlib)  

Next: **Phase C - Frontend Game Mode UI**
