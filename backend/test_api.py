#!/usr/bin/env python3
"""
LNCP API Integration Test
Version: 0.1.0

Tests the API endpoints without requiring a running server.
Uses FastAPI's TestClient for synchronous testing.
"""

from __future__ import annotations

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api import app


def test_health_check():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    print("✅ Health check passed")


def test_quick_analyze():
    """Test quick analysis endpoint."""
    client = TestClient(app)
    
    response = client.post(
        "/api/quick-analyze",
        json={
            "sentences": [
                "The morning light came through the window.",
                "She made coffee and sat down.",
                "Nothing happened for a long time.",
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["sentences_analyzed"]) == 3
    assert "phase1" in data
    assert "phase2" in data
    assert "phase3" in data
    assert "phase4a" in data
    assert "phase4b" in data
    
    print("✅ Quick analyze passed")
    print(f"   Phase-2 mode: {data['phase2']['presentation_mode']}")
    print(f"   Phase-3 syntheses: {len(data['phase3']['syntheses'])}")


def test_game_flow():
    """Test full game flow through API."""
    client = TestClient(app)
    
    # Initialize game
    response = client.post("/api/game/init", json={"mode": "STORY"})
    assert response.status_code == 200
    init_data = response.json()
    session_id = init_data["session_id"]
    
    print(f"✅ Game initialized: {session_id[:8]}...")
    print(f"   Mode: {init_data['mode']}")
    print(f"   Prompt: {init_data['current_prompt']['text'][:40]}...")
    
    # Submit 3 groups
    groups = [
        ["The morning light came through the window.", "She made coffee and sat down."],
        ["The book (a worn paperback) sat on the table.", "He opened it carefully."],
        ["The ratio was about 2/3 of the total.", "She calculated quickly."],
    ]
    
    for i, sentences in enumerate(groups, 1):
        response = client.post(
            "/api/game/submit",
            json={"session_id": session_id, "sentences": sentences}
        )
        assert response.status_code == 200
        submit_data = response.json()
        
        print(f"   Group {i}: {submit_data['last_submission']['status']} ({submit_data['gate']['completed']}/3)")
    
    assert submit_data["gate"]["is_complete"] == True
    print("✅ Gate complete")
    
    # Get game state
    response = client.get(f"/api/game/state/{session_id}")
    assert response.status_code == 200
    print("✅ Game state retrieved")
    
    # Run analysis
    response = client.post(f"/api/analyze?session_id={session_id}")
    assert response.status_code == 200
    results = response.json()
    
    print("✅ Analysis complete")
    print(f"   Sentences: {len(results['sentences_analyzed'])}")
    print(f"   Phase-2 mode: {results['phase2']['presentation_mode']}")
    print(f"   Phase-3 syntheses: {len(results['phase3']['syntheses'])}")
    print(f"   Phase-4a prompt sets: {len(results['phase4a']['prompt_sets'])}")
    print(f"   Phase-4b guidance sets: {len(results['phase4b']['guidance_sets'])}")
    
    # Get cached results
    response = client.get(f"/api/results/{session_id}")
    assert response.status_code == 200
    print("✅ Cached results retrieved")
    
    # Clean up
    response = client.delete(f"/api/session/{session_id}")
    assert response.status_code == 200
    print("✅ Session cleaned up")
    
    return True


def test_error_handling():
    """Test error handling."""
    client = TestClient(app)
    
    # Invalid session
    response = client.get("/api/game/state/invalid-session-id")
    assert response.status_code == 404
    print("✅ Invalid session returns 404")
    
    # Too few sentences
    response = client.post("/api/quick-analyze", json={"sentences": ["Only one."]})
    assert response.status_code == 422  # Validation error
    print("✅ Too few sentences rejected")
    
    # Invalid mode
    response = client.post("/api/game/init", json={"mode": "INVALID"})
    assert response.status_code == 400
    print("✅ Invalid mode rejected")


def main():
    """Run all tests."""
    print("=" * 60)
    print("LNCP API Integration Tests")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        print()
        
        test_quick_analyze()
        print()
        
        test_game_flow()
        print()
        
        test_error_handling()
        print()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
