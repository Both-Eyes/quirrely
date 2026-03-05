#!/usr/bin/env python3
"""
LNCP Pipeline E2E Test (v0.2.0)
Version: 0.2.0

Tests the complete pipeline including:
- High-Intent detection
- Phase-6 summary generation
- Both Phase-4 modes (PROMPTING and GUIDANCE)
- Game flow and quick_analyze
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

# Import orchestrator
import lncp_orchestrator
from lncp_orchestrator import get_orchestrator, quick_analyze

# Reset global orchestrator to ensure fresh instance with new prompt bank
lncp_orchestrator._orchestrator = None


def test_quick_analyze_prompting_mode():
    """Test quick_analyze with PROMPTING mode."""
    print("Test 1: Quick Analyze (PROMPTING mode)")
    print("-" * 50)
    
    sentences = [
        "The morning light definitely came through the window.",
        "She made coffee (black, no sugar) and sat down.",
        "Perhaps nothing would happen for a long time.",
        "I believe the phone might ring eventually.",
    ]
    
    results = quick_analyze(sentences, phase4_mode="PROMPTING")
    
    # Validate structure
    assert "phase1" in results, "Missing phase1"
    assert "phase2" in results, "Missing phase2"
    assert "phase3" in results, "Missing phase3"
    assert "phase4a" in results, "Missing phase4a"
    assert "phase4b" in results, "Missing phase4b"
    assert "phase6" in results, "Missing phase6"
    assert "high_intent_profile" in results, "Missing high_intent_profile"
    assert results["selected_phase4_mode"] == "PROMPTING", "Wrong mode"
    
    # Validate Phase-6 structure
    phase6 = results["phase6"]
    assert "summary" in phase6, "Missing phase6.summary"
    assert "high_intent_reflection" in phase6, "Missing phase6.high_intent_reflection"
    assert "next_step" in phase6, "Missing phase6.next_step"
    assert "forward_pointers" in phase6, "Missing phase6.forward_pointers"
    assert phase6["source_phase4_mode"] == "PROMPTING", "Phase6 mode mismatch"
    
    # Validate High-Intent
    hi = results["high_intent_profile"]
    assert hi["total_high_intent_events"] > 0, "Should detect High-Intent markers"
    assert "epistemic_openness" in hi, "Missing epistemic_openness"
    
    print(f"  ✅ Sentences analyzed: {len(results['sentences_analyzed'])}")
    print(f"  ✅ High-Intent events: {hi['total_high_intent_events']}")
    print(f"  ✅ Epistemic openness: {hi['epistemic_openness']}")
    print(f"  ✅ Phase-6 title: {phase6['summary']['title']}")
    print(f"  ✅ Epistemic stance: {phase6['high_intent_reflection']['epistemic_stance']}")
    print(f"  ✅ Next step: {phase6['next_step']['prompt_id']}")
    print()
    
    return True


def test_quick_analyze_guidance_mode():
    """Test quick_analyze with GUIDANCE mode."""
    print("Test 2: Quick Analyze (GUIDANCE mode)")
    print("-" * 50)
    
    sentences = [
        "This is certainly the best approach.",
        "We must consider all options carefully.",
        "The results clearly show improvement.",
    ]
    
    results = quick_analyze(sentences, phase4_mode="GUIDANCE")
    
    assert results["selected_phase4_mode"] == "GUIDANCE", "Wrong mode"
    # Phase-6 now has separate mode field for Story/School (defaults to STORY for quick_analyze)
    assert results["phase6"]["mode"] == "STORY", "Phase6 mode mismatch"
    
    # This sample should have CLOSED epistemic stance (certainty markers)
    hi = results["high_intent_profile"]
    stance = results["phase6"]["high_intent_reflection"]["epistemic_stance"]
    
    print(f"  ✅ Mode: GUIDANCE")
    print(f"  ✅ Phase-6 mode: STORY (Warm-Companion tone)")
    print(f"  ✅ High-Intent events: {hi['total_high_intent_events']}")
    print(f"  ✅ Epistemic stance: {stance}")
    print(f"  ✅ Dominant category: {hi.get('dominant_category', 'N/A')}")
    print()
    
    return True


def test_game_flow_with_phase6():
    """Test full game flow including Phase-6."""
    print("Test 3: Full Game Flow with Phase-6")
    print("-" * 50)
    
    orch = get_orchestrator()
    
    # Initialize game
    session_id, state = orch.create_session(mode="STORY")
    print(f"  ✅ Session created: {session_id[:8]}...")
    
    # Submit 3 groups with varied High-Intent markers
    groups = [
        ["The light came through.", "She sat down quietly."],
        ["Perhaps this might work.", "I believe it could."],
        ["This is definitely correct.", "We must proceed."],
    ]
    
    for i, sentences in enumerate(groups, 1):
        state = orch.submit_group(session_id, sentences)
        print(f"  ✅ Group {i}: {state['last_submission']['status']} ({state['gate']['completed']}/3)")
    
    assert state["gate"]["is_complete"], "Gate should be complete"
    
    # Run analysis with PROMPTING mode
    results = orch.run_analysis(session_id, phase4_mode="PROMPTING")
    
    assert "phase6" in results, "Missing phase6 in results"
    assert "high_intent_profile" in results, "Missing high_intent_profile"
    
    print(f"  ✅ Analysis complete")
    print(f"  ✅ Sentences: {len(results['sentences_analyzed'])}")
    print(f"  ✅ Phase-6 generated: {results['phase6']['summary']['title']}")
    print(f"  ✅ High-Intent markers: {results['high_intent_profile']['total_high_intent_events']}")
    
    # Test cached results
    cached = orch.get_analysis_results(session_id)
    assert cached is not None, "Should have cached results"
    assert "phase6" in cached, "Cached results missing phase6"
    print(f"  ✅ Cached results retrieved")
    
    # Cleanup
    orch.cleanup_session(session_id)
    print(f"  ✅ Session cleaned up")
    print()
    
    return True


def test_high_intent_detection():
    """Test High-Intent detection accuracy."""
    print("Test 4: High-Intent Detection")
    print("-" * 50)
    
    # Test with known markers
    test_cases = [
        {
            "sentences": ["This is definitely true.", "We must act now."],
            "expected_stance": "CLOSED",
            "min_markers": 2,
        },
        {
            "sentences": ["Perhaps this might work.", "I believe it could possibly help."],
            "expected_stance": "OPEN",
            "min_markers": 3,
        },
        {
            "sentences": ["The cat sat on the mat.", "The dog ran in the park."],
            "expected_stance": "MINIMAL",
            "min_markers": 0,
        },
    ]
    
    for i, tc in enumerate(test_cases, 1):
        results = quick_analyze(tc["sentences"])
        hi = results["high_intent_profile"]
        stance = results["phase6"]["high_intent_reflection"]["epistemic_stance"]
        
        assert hi["total_high_intent_events"] >= tc["min_markers"], \
            f"Case {i}: Expected >= {tc['min_markers']} markers, got {hi['total_high_intent_events']}"
        
        print(f"  ✅ Case {i}: {hi['total_high_intent_events']} markers, stance={stance}")
    
    print()
    return True


def test_phase6_schema_compliance():
    """Test Phase-6 output conforms to schema."""
    print("Test 5: Phase-6 Schema Compliance")
    print("-" * 50)
    
    results = quick_analyze([
        "The light came through the window.",
        "She made coffee and sat down.",
        "Nothing happened.",
    ])
    
    phase6 = results["phase6"]
    
    # Required fields
    required = [
        "phase6_version",
        "source_contract_version",
        "source_phase4_mode",
        "synthesis_scope",
        "interpretive_frame",
        "summary",
        "high_intent_reflection",
        "next_step",
        "forward_pointers",
        "llm_enhanced",
    ]
    
    for field in required:
        assert field in phase6, f"Missing required field: {field}"
        print(f"  ✅ {field}: present")
    
    # Summary subfields (v0.2.0: no mode_reflection, paths_forward is at top level)
    summary = phase6["summary"]
    for field in ["title", "structural_overview", "semiotic_synthesis"]:
        assert field in summary, f"Missing summary.{field}"
    print(f"  ✅ summary: all subfields present")
    
    # Paths forward (new in v0.2.0)
    if "paths_forward" in phase6:
        pf = phase6["paths_forward"]
        for field in ["next_sample", "recommended_exercise", "school_mode"]:
            assert field in pf, f"Missing paths_forward.{field}"
        print(f"  ✅ paths_forward: all options present")
    
    # High-Intent reflection subfields
    hir = phase6["high_intent_reflection"]
    for field in ["present", "overview", "epistemic_stance", "notable_markers"]:
        assert field in hir, f"Missing high_intent_reflection.{field}"
    print(f"  ✅ high_intent_reflection: all subfields present")
    
    # Next step subfields
    ns = phase6["next_step"]
    for field in ["prompt_id", "prompt_text", "rationale", "category"]:
        assert field in ns, f"Missing next_step.{field}"
    print(f"  ✅ next_step: all subfields present")
    
    # Forward pointers
    assert len(phase6["forward_pointers"]) >= 1, "Should have at least 1 forward pointer"
    print(f"  ✅ forward_pointers: {len(phase6['forward_pointers'])} pointers")
    
    # LLM enhanced flag
    assert isinstance(phase6["llm_enhanced"], bool), "llm_enhanced should be boolean"
    print(f"  ✅ llm_enhanced: {phase6['llm_enhanced']}")
    
    if not phase6["llm_enhanced"]:
        assert "enhancement_notice" in phase6, "Should have enhancement_notice when not LLM enhanced"
        print(f"  ✅ enhancement_notice: present (fallback mode)")
    
    print()
    return True


def test_version_alignment():
    """Test version alignment across phases."""
    print("Test 6: Version Alignment")
    print("-" * 50)
    
    results = quick_analyze([
        "Test sentence one.",
        "Test sentence two.",
    ])
    
    # Check versions - Phase 2/3 v0.2.0, Phase 4a/4b v0.3.0, Phase-6 v0.3.0
    assert results["phase2"]["phase2_version"] == "0.2.0", "Phase-2 version mismatch"
    assert results["phase3"]["phase3_version"] == "0.2.0", "Phase-3 version mismatch"
    assert results["phase4a"]["phase4a_version"] == "0.3.0", "Phase-4a version mismatch"
    assert results["phase4b"]["phase4b_version"] == "0.3.0", "Phase-4b version mismatch"
    assert results["phase6"]["phase6_version"] == "0.3.0", "Phase-6 version mismatch"
    
    print(f"  ✅ Phase-2: v{results['phase2']['phase2_version']}")
    print(f"  ✅ Phase-3: v{results['phase3']['phase3_version']}")
    print(f"  ✅ Phase-4a: v{results['phase4a']['phase4a_version']}")
    print(f"  ✅ Phase-4b: v{results['phase4b']['phase4b_version']}")
    print(f"  ✅ Phase-6: v{results['phase6']['phase6_version']}")
    print()
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("LNCP Pipeline E2E Test (v0.2.0 with Phase-6 & High-Intent)")
    print("=" * 60)
    print()
    
    tests = [
        ("Quick Analyze (PROMPTING)", test_quick_analyze_prompting_mode),
        ("Quick Analyze (GUIDANCE)", test_quick_analyze_guidance_mode),
        ("Game Flow with Phase-6", test_game_flow_with_phase6),
        ("High-Intent Detection", test_high_intent_detection),
        ("Phase-6 Schema Compliance", test_phase6_schema_compliance),
        ("Version Alignment", test_version_alignment),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
