# LNCP Web App - Phase A Complete

## Project Structure

```
lncp-web-app/
├── backend/
│   ├── __init__.py                          # Package init
│   ├── lncp_orchestrator.py                 # Main pipeline orchestrator
│   ├── lncp_parser.py                       # Sentence → LNCP canonical format
│   │
│   ├── # LNCP Core Modules (locked)
│   ├── phase1_compute_v1_0_0.py             # Phase-1 compute engine
│   ├── phase5_state_machine_v0_1_0.py       # Phase-5 game state machine
│   ├── phase5_select_cover_v0_1_0.py        # Prompt selector + coverage
│   ├── generate_phase2_v0_1_0.py            # Phase-2 UX generator (NEW)
│   ├── generate_phase3_v0_1_0.py            # Phase-3 synthesis generator
│   ├── generate_phase4a_v0_1_0.py           # Phase-4a prompt generator
│   ├── generate_phase4b_v0_1_0.py           # Phase-4b guidance generator
│   │
│   ├── # Schemas
│   ├── phase2-ux-output-schema-v0.1.0.json
│   ├── phase3-synthesis-output-schema-v0.1.0.json
│   ├── phase4a-prompting-output-schema-v0.1.0.json
│   ├── phase4b-guidance-output-schema-v0.1.0.json
│   ├── phase5-game-output-schema-v0.1.0.json
│   │
│   ├── # Validators
│   ├── validate_phase3_schema.py
│   ├── validate_phase4a_schema.py
│   ├── validate_phase4b_schema.py
│   ├── validate_phase5_schema.py
│   │
│   └── # Data
│       └── phase5-prompt-bank-v0.1.0.json   # 44 prompts for game mode
│
├── frontend/                                 # (Phase C - not yet built)
│
└── shared/
    └── LNCP_UNIFIED_MANIFEST_v0.1.0.json    # Complete artifact manifest
```

## New Files Created in Phase A

| File | Purpose | Lines |
|------|---------|-------|
| `lncp_orchestrator.py` | Pipeline orchestration, session management | ~300 |
| `lncp_parser.py` | Convert raw sentences to LNCP canonical format | ~250 |
| `generate_phase2_v0_1_0.py` | Template-based Phase-2 UX generation | ~350 |

## API Surface (for Phase B)

### Orchestrator API

```python
from lncp_orchestrator import get_orchestrator, quick_analyze

# Option 1: Full game flow
orch = get_orchestrator()

# Create session
session_id, state = orch.create_session(mode="STORY")  # or "LAB"

# Submit groups (repeat until gate complete)
state = orch.submit_group(session_id, ["Sentence 1.", "Sentence 2."])

# Run analysis after gate completion
results = orch.run_analysis(session_id)

# Option 2: Quick analysis (no game)
results = quick_analyze(["Sentence 1.", "Sentence 2.", "Sentence 3."])
```

### State Object Structure

```python
state = {
    "session_id": "uuid",
    "mode": "STORY",
    "gate": {
        "required": 3,
        "completed": 1,
        "is_complete": False
    },
    "current_prompt": {
        "prompt_id": "PB_001",
        "text": "Write 2-3 sentences..."
    },
    "last_submission": {
        "status": "VALID",
        "message": "Group accepted."
    },
    "progress": {
        "groups": [...],
        "failure_count": 0
    },
    "coverage": {
        "zero": True,
        "operator": False,
        "scope": True,
        "is_satisfied": False
    },
    "safety": {
        "actor_state": "NORMAL",
        "is_deescalating": False,
        "message": None
    }
}
```

### Results Object Structure

```python
results = {
    "session_id": "uuid",
    "sentences_analyzed": ["...", "..."],
    "phase1": { ... },  # 10 metrics
    "phase2": { ... },  # UX presentation (DESCRIPTIVE/REFLECTIVE)
    "phase3": { ... },  # 3 syntheses
    "phase4a": { ... }, # 3 prompt sets (4 prompts each)
    "phase4b": { ... }  # 3 guidance sets (4 items each)
}
```

## Verified Working

```bash
cd lncp-web-app/backend

# Quick analysis (no game)
python3 -c "
from lncp_orchestrator import quick_analyze
results = quick_analyze(['Sentence one.', 'Sentence two.', 'Sentence three.'])
print(f'Phase-2 mode: {results[\"phase2\"][\"presentation_mode\"]}')
"

# Full game flow
python3 -c "
from lncp_orchestrator import get_orchestrator
orch = get_orchestrator()
sid, state = orch.create_session(mode='STORY')
state = orch.submit_group(sid, ['Test one.', 'Test two.'])
state = orch.submit_group(sid, ['Test three.', 'Test four.'])
state = orch.submit_group(sid, ['Test five.', 'Test six.'])
results = orch.run_analysis(sid)
print(f'Analyzed {len(results[\"sentences_analyzed\"])} sentences')
"
```

## Ready for Phase B

Phase A is complete. The backend has:

✅ All LNCP core modules imported  
✅ LNCP parser for raw text → canonical format  
✅ Phase-2 generator (template-based, no LLM)  
✅ Pipeline orchestrator with session management  
✅ Working `quick_analyze()` function  
✅ Working game flow with `create_session()` → `submit_group()` → `run_analysis()`  

Next: **Phase B - Backend API Layer** (FastAPI/Flask endpoints)
