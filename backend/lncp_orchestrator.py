#!/usr/bin/env python3
"""
LNCP Pipeline Orchestrator
Version: 0.4.0

Orchestrates the complete LNCP pipeline for the web application.
Provides a clean API surface for the web backend to consume.

CHANGELOG v0.4.0:
- Story Mode with Warm-Companion tone and intimacy gradient
- Session-based prompt unlocking (MEMORY at 3+, FEELING at 5+, INSIGHT at 7+)
- Mode-aware Phase-6 generation (Story vs School)
- Updated to prompt bank v0.4.0

CHANGELOG v0.3.0:
- Updated to use Phase-4a/4b v0.3.0 with Collaborative-Curious tone
- Updated to use prompt bank v0.3.0 with SCHOOL mode tone update

CHANGELOG v0.2.0:
- Updated to use Phase-6 v0.2.0 with sample-specific content
- Updated to use prompt bank v0.2.0 with School mode
- Added session persistence integration
- LAB mode renamed to SCHOOL mode
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import LNCP modules
from phase1_compute_v1_0_0 import compute_phase1_response
from phase5_state_machine_v0_1_0 import Phase5StateMachine, STATE_COMPLETION
from phase5_select_cover_v0_1_0 import load_prompt_bank
from generate_phase2_v0_2_0 import generate_phase2
from generate_phase3_v0_2_0 import generate_phase3
from generate_phase4a_v0_3_0 import generate_phase4a_prompting_output
from generate_phase4b_v0_3_0 import generate_phase4b
from generate_phase6_v0_3_0 import generate_phase6
from lncp_parser import sentences_to_lncp_rows, compute_high_intent_profile, compute_full_profile
from session_persistence import get_session_store, SessionStore


# Path to prompt bank (relative to this file) - v0.4.0 with Story Mode
PROMPT_BANK_PATH = Path(__file__).parent / "phase5-prompt-bank-v0.4.0.json"


@dataclass
class LNCPSession:
    """Represents an LNCP user session."""
    session_id: str
    state_machine: Phase5StateMachine
    mode: str = "STORY"  # STORY or SCHOOL
    created_at: str = ""
    phase1_output: Optional[Dict[str, Any]] = None
    phase2_output: Optional[Dict[str, Any]] = None
    phase3_output: Optional[Dict[str, Any]] = None
    phase4a_output: Optional[Dict[str, Any]] = None
    phase4b_output: Optional[Dict[str, Any]] = None
    phase6_output: Optional[Dict[str, Any]] = None
    high_intent_profile: Optional[Dict[str, Any]] = None
    selected_phase4_mode: str = "PROMPTING"  # Default to prompting
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def get_all_sentences(self) -> List[str]:
        """Extract all sentences from valid groups."""
        sentences = []
        for group in self.state_machine.state.groups:
            # Handle both dict and ValidGroup dataclass
            if hasattr(group, 'sentences'):
                sentences.extend(group.sentences)
            else:
                sentences.extend(group.get("sentences", []))
        return sentences


class LNCPOrchestrator:
    """
    Main orchestrator for the LNCP pipeline.
    
    Manages sessions and coordinates pipeline execution.
    """
    
    def __init__(self, prompt_bank_path: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            prompt_bank_path: Path to Phase-5 prompt bank JSON
        """
        bank_path = prompt_bank_path or str(PROMPT_BANK_PATH)
        self._bank_version, self._prompts = load_prompt_bank(bank_path)
        self._sessions: Dict[str, LNCPSession] = {}
    
    def create_session(self, mode: str = "STORY") -> Tuple[str, Dict[str, Any]]:
        """
        Create a new LNCP session and initialize Phase-5 game.
        
        Args:
            mode: Game mode ("STORY" or "SCHOOL")
            
        Returns:
            (session_id, initial_state)
        """
        # Normalize mode (support legacy LAB → SCHOOL)
        if mode == "LAB":
            mode = "SCHOOL"
        
        session_id = str(uuid.uuid4())
        
        # Create state machine with session ID as seed for determinism
        sm = Phase5StateMachine(self._prompts, seed_base=session_id)
        sm.initialize(mode=mode)
        
        session = LNCPSession(
            session_id=session_id,
            state_machine=sm,
            mode=mode,
        )
        self._sessions[session_id] = session
        
        return session_id, self._get_game_state(session)
    
    def get_session(self, session_id: str) -> Optional[LNCPSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def submit_group(self, session_id: str, sentences: List[str]) -> Dict[str, Any]:
        """
        Submit a sentence group to Phase-5.
        
        Args:
            session_id: Session identifier
            sentences: List of 2-3 sentences
            
        Returns:
            Updated game state
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session.state_machine.submit_group(sentences)
        return self._get_game_state(session)
    
    def run_analysis(self, session_id: str, phase4_mode: str = "PROMPTING", save: bool = True) -> Dict[str, Any]:
        """
        Run the full analysis pipeline after Phase-5 gate completion.
        
        Args:
            session_id: Session identifier
            phase4_mode: "PROMPTING" or "GUIDANCE" - determines Phase-4 and Phase-6 variation
            save: Whether to save results to persistence
            
        Returns:
            Complete analysis results including Phase-6 summary
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if not session.state_machine.state.is_gate_complete:
            raise ValueError("Phase-5 gate not complete. Submit more sentence groups.")
        
        # Store selected mode
        session.selected_phase4_mode = phase4_mode
        
        # Get all sentences from valid groups
        sentences = session.get_all_sentences()
        
        # Convert to LNCP canonical format and compute full profile (v0.6.0)
        lncp_rows = sentences_to_lncp_rows(sentences)
        session.high_intent_profile = compute_full_profile(sentences, lncp_rows)
        
        # Phase-1: Compute metrics
        session.phase1_output = compute_phase1_response(lncp_rows)
        
        # Phase-2: Generate UX presentation
        session.phase2_output = generate_phase2(session.phase1_output)
        
        # Phase-3: Generate syntheses
        session.phase3_output = generate_phase3(session.phase2_output)
        
        # Phase-4a: Generate prompts
        session.phase4a_output = generate_phase4a_prompting_output(session.phase3_output)
        
        # Phase-4b: Generate guidance
        session.phase4b_output = generate_phase4b(session.phase3_output)
        
        # Phase-6: Generate summary with mode-aware, sample-specific content
        session.phase6_output = generate_phase6(
            session.phase1_output,
            session.phase2_output,
            session.phase3_output,
            session.phase4a_output,
            session.phase4b_output,
            session.high_intent_profile,
            sentences=sentences,
            mode=session.mode,  # Pass mode for tone selection
        )
        
        # Get results
        results = self._get_analysis_results(session)
        
        # Save to persistence if requested
        if save:
            try:
                store = get_session_store()
                store.save_session(
                    session_id,
                    results,
                    {"mode": session.mode, "created_at": session.created_at}
                )
            except Exception as e:
                # Don't fail analysis if persistence fails
                print(f"Warning: Failed to save session to persistence: {e}")
        
        return results
    
    def get_game_state(self, session_id: str) -> Dict[str, Any]:
        """Get current game state for a session."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        return self._get_game_state(session)
    
    def get_analysis_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis results if available."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        if session.phase1_output is None:
            return None
        
        return self._get_analysis_results(session)
    
    def _get_game_state(self, session: LNCPSession) -> Dict[str, Any]:
        """Extract game state from session."""
        sm = session.state_machine
        state = sm.state
        
        return {
            "session_id": session.session_id,
            "state": state.state,
            "mode": state.mode,
            "gate": {
                "required": 3,
                "completed": state.valid_groups_count,
                "is_complete": state.is_gate_complete,
            },
            "current_prompt": {
                "prompt_id": state.current_prompt_id,
                "text": state.current_prompt_text,
            },
            "last_submission": {
                "status": state.last_validation_status,
                "message": state.last_validation_message,
            } if state.last_validation_status else None,
            "progress": {
                "groups": state.groups,
                "failure_count": state.failure_count,
            },
            "coverage": {
                "zero": state.zero_present,
                "operator": state.operator_present,
                "scope": state.scope_present,
                "is_satisfied": state.is_coverage_satisfied,
            },
            "safety": {
                "actor_state": state.actor_state,
                "is_deescalating": state.is_deescalating,
                "message": state.deescalation_message,
            },
        }
    
    def _get_analysis_results(self, session: LNCPSession) -> Dict[str, Any]:
        """Package analysis results for API response."""
        return {
            "session_id": session.session_id,
            "sentences_analyzed": session.get_all_sentences(),
            "selected_phase4_mode": session.selected_phase4_mode,
            "phase1": session.phase1_output,
            "phase2": session.phase2_output,
            "phase3": session.phase3_output,
            "phase4a": session.phase4a_output,
            "phase4b": session.phase4b_output,
            "phase6": session.phase6_output,
            "high_intent_profile": session.high_intent_profile,
        }
    
    def cleanup_session(self, session_id: str) -> bool:
        """Remove a session from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Singleton instance for the web app
_orchestrator: Optional[LNCPOrchestrator] = None


def get_orchestrator() -> LNCPOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LNCPOrchestrator()
    return _orchestrator


# Direct function API for simpler use cases

def quick_analyze(sentences: List[str], phase4_mode: str = "PROMPTING", save: bool = False) -> Dict[str, Any]:
    """
    Quick analysis without game mode.
    
    Runs Phase-1 through Phase-6 directly on provided sentences.
    
    Args:
        sentences: List of sentences to analyze
        phase4_mode: "PROMPTING" or "GUIDANCE" - determines Phase-6 variation
        save: Whether to save to persistence
        
    Returns:
        Complete analysis results including Phase-6 summary
    """
    if len(sentences) < 2:
        raise ValueError("At least 2 sentences required for analysis")
    
    # Generate session ID for persistence
    session_id = str(uuid.uuid4())
    
    # Convert to LNCP canonical format and compute full profile (v0.6.0)
    lncp_rows = sentences_to_lncp_rows(sentences)
    high_intent_profile = compute_full_profile(sentences, lncp_rows)
    
    # Phase-1: Compute
    phase1 = compute_phase1_response(lncp_rows)
    
    # Phase-2: UX
    phase2 = generate_phase2(phase1)
    
    # Phase-3: Synthesis
    phase3 = generate_phase3(phase2)
    
    # Phase-4a: Prompts
    phase4a = generate_phase4a_prompting_output(phase3)
    
    # Phase-4b: Guidance
    phase4b = generate_phase4b(phase3)
    
    # Phase-6: Summary with mode-aware, sample-specific content
    # Quick analyze defaults to STORY mode for warm tone
    phase6 = generate_phase6(
        phase1, phase2, phase3, phase4a, phase4b, high_intent_profile,
        sentences=sentences,
        mode="STORY",  # Default to Story Mode for quick analysis
    )
    
    results = {
        "session_id": session_id,
        "sentences_analyzed": sentences,
        "selected_phase4_mode": phase4_mode,
        "phase1": phase1,
        "phase2": phase2,
        "phase3": phase3,
        "phase4a": phase4a,
        "phase4b": phase4b,
        "phase6": phase6,
        "high_intent_profile": high_intent_profile,
    }
    
    # Save to persistence if requested
    if save:
        try:
            store = get_session_store()
            store.save_session(session_id, results, {"mode": "QUICK"})
        except Exception as e:
            print(f"Warning: Failed to save session: {e}")
    
    # Add user profile data (evolving profile from history)
    try:
        from user_profile_aggregator import get_profile_tab_data
        results["user_profile"] = get_profile_tab_data()
    except Exception as e:
        print(f"Warning: Failed to load user profile: {e}")
        results["user_profile"] = {"status": "ERROR", "message": str(e)}
    
    return results


if __name__ == "__main__":
    # Demo usage
    print("LNCP Pipeline Orchestrator Demo")
    print("=" * 40)
    
    # Quick analysis demo
    demo_sentences = [
        "The morning light came through the window.",
        "She definitely made coffee and sat down.",
        "Nothing happened for a long time.",
        "Perhaps the phone might ring.",
    ]
    
    print(f"\nAnalyzing {len(demo_sentences)} sentences...")
    results = quick_analyze(demo_sentences)
    
    print(f"\nPhase-1: {len(results['phase1']['outputs'])} metrics computed")
    print(f"Phase-2: {results['phase2']['presentation_mode']} mode")
    print(f"Phase-3: {len(results['phase3']['syntheses'])} syntheses")
    print(f"Phase-4a: {len(results['phase4a']['prompt_sets'])} prompt sets")
    print(f"Phase-4b: {len(results['phase4b']['guidance_sets'])} guidance sets")
    print(f"Phase-6: {results['phase6']['summary']['title']}")
    print(f"High-Intent: {results['high_intent_profile']['total_high_intent_events']} markers detected")
    print(f"Epistemic Stance: {results['phase6']['high_intent_reflection']['epistemic_stance']}")
    print(f"Next Step: {results['phase6']['next_step']['prompt_text'][:50]}...")
    
    print("\n✅ Pipeline execution complete")
