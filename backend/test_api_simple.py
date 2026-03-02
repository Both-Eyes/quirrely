#!/usr/bin/env python3
"""
LNCP API Test (No External Dependencies)
Version: 0.1.0

Tests the API by directly calling handler methods.
No HTTP server or external libraries required.
"""

from __future__ import annotations

import json
import os
import sys
from io import BytesIO
from typing import Any, Dict

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lncp_orchestrator import get_orchestrator, quick_analyze


def test_orchestrator_directly():
    """Test the orchestrator without HTTP layer."""
    print("=" * 60)
    print("LNCP API Tests (Direct Orchestrator)")
    print("=" * 60)
    print()
    
    # Test 1: Quick analyze
    print("Test 1: Quick Analyze")
    print("-" * 40)
    
    try:
        results = quick_analyze([
            "The morning light came through the window.",
            "She made coffee and sat down.",
            "Nothing happened for a long time.",
        ])
        
        print(f"✅ Quick analyze succeeded")
        print(f"   Sentences: {len(results['sentences_analyzed'])}")
        print(f"   Phase-1 outputs: {len(results['phase1']['outputs'])}")
        print(f"   Phase-2 mode: {results['phase2']['presentation_mode']}")
        print(f"   Phase-3 syntheses: {len(results['phase3']['syntheses'])}")
        print(f"   Phase-4a prompt sets: {len(results['phase4a']['prompt_sets'])}")
        print(f"   Phase-4b guidance sets: {len(results['phase4b']['guidance_sets'])}")
    except Exception as e:
        print(f"❌ Quick analyze failed: {e}")
        return False
    
    print()
    
    # Test 2: Game flow
    print("Test 2: Full Game Flow")
    print("-" * 40)
    
    try:
        orch = get_orchestrator()
        
        # Initialize
        session_id, state = orch.create_session(mode="STORY")
        print(f"✅ Session created: {session_id[:8]}...")
        print(f"   Mode: {state['mode']}")
        print(f"   Prompt: {state['current_prompt']['text'][:40]}...")
        
        # Submit groups
        groups = [
            ["The morning light came through the window.", "She made coffee and sat down."],
            ["The book (a worn paperback) sat on the table.", "He opened it carefully."],
            ["The ratio was about 2/3 of the total.", "She calculated quickly."],
        ]
        
        for i, sentences in enumerate(groups, 1):
            state = orch.submit_group(session_id, sentences)
            status = state["last_submission"]["status"]
            completed = state["gate"]["completed"]
            print(f"   Group {i}: {status} ({completed}/3)")
        
        if not state["gate"]["is_complete"]:
            print("❌ Gate not complete after 3 groups")
            return False
        
        print(f"✅ Gate complete")
        
        # Run analysis
        results = orch.run_analysis(session_id)
        print(f"✅ Analysis complete")
        print(f"   Sentences: {len(results['sentences_analyzed'])}")
        print(f"   Phase-2 mode: {results['phase2']['presentation_mode']}")
        
        # Get cached results
        cached = orch.get_analysis_results(session_id)
        if cached:
            print(f"✅ Cached results retrieved")
        
        # Cleanup
        deleted = orch.cleanup_session(session_id)
        if deleted:
            print(f"✅ Session cleaned up")
        
    except Exception as e:
        print(f"❌ Game flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 3: Error handling
    print("Test 3: Error Handling")
    print("-" * 40)
    
    try:
        orch = get_orchestrator()
        
        # Invalid session
        session = orch.get_session("invalid-session-id")
        if session is None:
            print("✅ Invalid session returns None")
        else:
            print("❌ Invalid session should return None")
            return False
        
        # Too few sentences
        try:
            quick_analyze(["Only one."])
            print("❌ Should reject single sentence")
            return False
        except ValueError:
            print("✅ Single sentence rejected")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print()
    print("=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    
    return True


def test_api_endpoints_simulation():
    """Simulate API endpoint calls."""
    print()
    print("=" * 60)
    print("API Endpoint Simulation")
    print("=" * 60)
    print()
    
    # Simulate the JSON payloads that would go through HTTP
    
    print("POST /api/game/init")
    print("  Request: {'mode': 'STORY'}")
    orch = get_orchestrator()
    session_id, state = orch.create_session(mode="STORY")
    response = {
        "session_id": session_id,
        "mode": state["mode"],
        "current_prompt": state["current_prompt"],
        "gate": state["gate"],
    }
    print(f"  Response: session_id={response['session_id'][:8]}..., gate={response['gate']}")
    print()
    
    print("POST /api/game/submit")
    sentences = ["Test sentence one.", "Test sentence two."]
    print(f"  Request: session_id=..., sentences={sentences}")
    state = orch.submit_group(session_id, sentences)
    response = {
        "state": state["state"],
        "gate": state["gate"],
        "last_submission": state["last_submission"],
    }
    print(f"  Response: state={response['state']}, gate={response['gate']}, submission={response['last_submission']}")
    print()
    
    # Submit 2 more to complete gate
    orch.submit_group(session_id, ["Test three.", "Test four."])
    orch.submit_group(session_id, ["Test five.", "Test six."])
    
    print("POST /api/analyze")
    print(f"  Request: session_id={session_id[:8]}...")
    results = orch.run_analysis(session_id)
    print(f"  Response: {len(results['sentences_analyzed'])} sentences, {len(results['phase3']['syntheses'])} syntheses")
    print()
    
    print("GET /api/results/{session_id}")
    cached = orch.get_analysis_results(session_id)
    print(f"  Response: phase2_mode={cached['phase2']['presentation_mode']}")
    print()
    
    print("DELETE /api/session/{session_id}")
    deleted = orch.cleanup_session(session_id)
    print(f"  Response: deleted={deleted}")
    print()
    
    print("✅ All endpoint simulations complete")
    return True


if __name__ == "__main__":
    success = test_orchestrator_directly()
    if success:
        test_api_endpoints_simulation()
    
    sys.exit(0 if success else 1)
