#!/usr/bin/env python3
"""
Phase-5 State Machine Runner
Version: 0.1.0

Implements the Phase-5 sample-building game state machine with:
- B3 strict gate: no downstream outputs until 3/3 valid groups
- H2 coverage tracking: zero/operator/scope event presence
- Failure handling: minimal messaging, retry, soft-cap, auto-skip
- Safety handling: anger detection and de-escalation

State Machine:
  ENTRY → PLAY → (submit group) → validate → 
    if valid: update progress/coverage → check gate
    if invalid: increment failure_count → check soft-cap → retry or auto-skip
  
  Gate complete (3/3 valid + coverage satisfied) →
    COMPLETION → PIPELINE_EXECUTION (enables Phase-1/2/3, optionally 4a/4b)

Frozen Behaviors (v0.1.0):
- Required valid groups: 3 (const)
- Soft-cap max failures before auto-skip: 5 (frozen default)
- Validation messages: <= 120 chars (strict gate UX minimalism)
- Only valid groups stored in progress.groups
- Invalid attempts tracked in failure_count only
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import from aligned selector
from phase5_select_cover_v0_1_0 import (
    PHASE5_VERSION,
    PROMPT_BANK_VERSION,
    Prompt,
    load_prompt_bank,
    select_next_prompt,
    infer_event_flags,
    coverage_profile,
    CoverageState,
    GameProgress,
    GameState as SelectorGameState,
)


# ----------------------------
# Locked Constants (v0.1.0)
# ----------------------------

REQUIRED_VALID_GROUPS = 3
DEFAULT_SOFT_CAP_MAX_FAILURES = 5
COVERAGE_SYSTEM = "H2"
ROUTING_RULE_NOTE = "Phase-4a and Phase-4b are never executed until Phase-5 gate completion (3/3 valid groups)."

# State machine states
STATE_ENTRY = "ENTRY"
STATE_PLAY = "PLAY"
STATE_COVERAGE_CHECK = "COVERAGE_CHECK"
STATE_LAB_CHALLENGE = "LAB_CHALLENGE"
STATE_COMPLETION = "COMPLETION"
STATE_PIPELINE_EXECUTION = "PIPELINE_EXECUTION"
STATE_ABORTED = "ABORTED"

# Validation statuses
VALIDATION_VALID = "VALID"
VALIDATION_INVALID = "INVALID"
VALIDATION_NOT_EVALUATED = "NOT_EVALUATED"

# Actor states
ACTOR_NORMAL = "NORMAL"
ACTOR_PLAYFUL = "PLAYFUL"
ACTOR_HOSTILE = "HOSTILE"
ACTOR_ANGRY = "ANGRY"

# Frozen minimal validation messages (strict gate UX)
MSG_VALID = "Group accepted."
MSG_INVALID_SENTENCE_COUNT = "Please provide 2-3 sentences."
MSG_INVALID_EMPTY = "Please write something."
MSG_INVALID_RETRY = "Not valid, try again."
MSG_SOFT_CAP_APPROACHING = "Take your time."
MSG_AUTO_SKIP = "Moving on to the next prompt."

# De-escalation messages (frozen)
DEESCALATE_MSG_HOSTILE = "Let's slow down a moment."
DEESCALATE_MSG_ANGRY = "It's okay to take a break."


# ----------------------------
# Data Structures
# ----------------------------

@dataclass
class ValidGroup:
    """A validated sentence group stored in progress.groups."""
    group_id: str  # G1, G2, G3
    sentences: List[str]
    is_valid: bool = True
    validation_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "group_id": self.group_id,
            "sentences": self.sentences,
            "is_valid": self.is_valid,
        }
        if self.validation_message:
            d["validation_message"] = self.validation_message
        return d


@dataclass
class Phase5GameState:
    """
    Complete Phase-5 game state conforming to phase5-game-output-schema-v0.1.0.json.
    """
    # Core state
    state: str = STATE_ENTRY
    
    # Gate tracking
    valid_groups_count: int = 0
    
    # Progress
    groups: List[ValidGroup] = field(default_factory=list)
    failure_count: int = 0
    soft_cap_active: bool = False
    soft_cap_max_failures: int = DEFAULT_SOFT_CAP_MAX_FAILURES
    
    # Prompting
    mode: str = "STORY"
    current_prompt_id: str = ""
    current_prompt_type: str = "NOTICE"
    current_prompt_text: str = ""
    last_submitted_sentences: List[str] = field(default_factory=list)
    last_validation_status: str = VALIDATION_NOT_EVALUATED
    last_validation_message: Optional[str] = None
    
    # Coverage (H2)
    zero_present: bool = False
    operator_present: bool = False
    scope_present: bool = False
    
    # Safety
    actor_state: str = ACTOR_NORMAL
    is_deescalating: bool = False
    deescalation_message: Optional[str] = None
    
    # Internal tracking
    seed_base: str = ""
    used_prompt_ids: List[str] = field(default_factory=list)

    @property
    def is_gate_complete(self) -> bool:
        return self.valid_groups_count >= REQUIRED_VALID_GROUPS

    @property
    def is_coverage_satisfied(self) -> bool:
        return self.zero_present and self.operator_present and self.scope_present

    def coverage_status_summary(self) -> str:
        """User-safe coverage summary."""
        if self.is_coverage_satisfied:
            return "Coverage complete."
        missing = []
        if not self.zero_present:
            missing.append("punctuation")
        if not self.operator_present:
            missing.append("symbols")
        if not self.scope_present:
            missing.append("brackets/quotes")
        return f"Building variety: {', '.join(missing)} not yet seen."

    def to_output_dict(self) -> Dict[str, Any]:
        """Generate schema-compliant output dict."""
        is_complete = self.is_gate_complete and self.is_coverage_satisfied
        
        # Determine routing based on gate completion
        if is_complete:
            routing = {
                "phase1_allowed": True,
                "phase2_allowed": True,
                "phase3_allowed": True,
                "phase4a_allowed": True,  # Optional unlock post-completion
                "phase4b_allowed": True,  # Optional unlock post-completion
                "rule_note": ROUTING_RULE_NOTE,
            }
        else:
            routing = {
                "phase1_allowed": False,
                "phase2_allowed": False,
                "phase3_allowed": False,
                "phase4a_allowed": False,
                "phase4b_allowed": False,
                "rule_note": ROUTING_RULE_NOTE,
            }
        
        # Build safety section
        safety: Dict[str, Any] = {
            "actor_state": self.actor_state,
            "is_deescalating": self.is_deescalating,
        }
        if self.is_deescalating and self.deescalation_message:
            safety["deescalation_message"] = self.deescalation_message
        
        # Build last_submission
        last_submission: Dict[str, Any] = {
            "submitted_group": {
                "sentences": self.last_submitted_sentences if self.last_submitted_sentences else ["", ""],
            },
            "validation": {
                "status": self.last_validation_status,
            },
        }
        if self.last_validation_message:
            last_submission["validation"]["message"] = self.last_validation_message
        
        # Ensure submitted_group.sentences has at least 2 items for schema compliance
        if len(last_submission["submitted_group"]["sentences"]) < 2:
            last_submission["submitted_group"]["sentences"] = ["", ""]
        
        return {
            "phase5_version": PHASE5_VERSION,
            "state": self.state,
            "gate": {
                "required_valid_groups": REQUIRED_VALID_GROUPS,
                "valid_groups_count": self.valid_groups_count,
                "is_complete": is_complete,
            },
            "progress": {
                "groups": [g.to_dict() for g in self.groups],
                "failure_count": self.failure_count,
                "soft_cap": {
                    "is_active": self.soft_cap_active,
                    "max_failures_before_autoskip": self.soft_cap_max_failures,
                },
            },
            "prompting": {
                "mode": self.mode,
                "current_prompt": {
                    "prompt_id": self.current_prompt_id or "NONE",
                    "prompt_type": self.current_prompt_type,
                    "text": self.current_prompt_text or "No prompt selected.",
                },
                "last_submission": last_submission,
            },
            "coverage": {
                "coverage_system": COVERAGE_SYSTEM,
                "is_satisfied": self.is_coverage_satisfied,
                "status_summary": self.coverage_status_summary(),
                "details": {
                    "zero_present": self.zero_present,
                    "operator_present": self.operator_present,
                    "scope_present": self.scope_present,
                },
            },
            "safety": safety,
            "routing": routing,
        }


# ----------------------------
# Group Validation (Lightweight)
# ----------------------------

def validate_group_structure(sentences: List[str]) -> Tuple[bool, str]:
    """
    Validate group structure (not LNCP content).
    Returns (is_valid, message).
    """
    if not sentences:
        return False, MSG_INVALID_EMPTY
    
    # Filter empty strings
    non_empty = [s.strip() for s in sentences if s.strip()]
    
    if len(non_empty) < 2:
        return False, MSG_INVALID_SENTENCE_COUNT
    if len(non_empty) > 3:
        return False, MSG_INVALID_SENTENCE_COUNT
    
    return True, MSG_VALID


def detect_actor_state(text: str) -> str:
    """
    Simple heuristic for anger/hostility detection.
    This is a placeholder; real implementation would use more sophisticated detection.
    """
    text_lower = text.lower()
    
    # Hostile indicators (explicit abuse)
    hostile_patterns = [
        r'\bstupid\b', r'\bidiot\b', r'\bhate\s+this\b', r'\bwaste\s+of\s+time\b',
        r'\bf+u+c+k+\b', r'\bs+h+i+t+\b', r'\bdamn\b',
    ]
    for pattern in hostile_patterns:
        if re.search(pattern, text_lower):
            return ACTOR_HOSTILE
    
    # Angry indicators (frustration)
    angry_patterns = [
        r'\bfrustrat', r'\bannoying\b', r'\bannoy', r'\bwhy\s+won\'?t\b',
        r'\bthis\s+is\s+ridiculous\b', r'\bgive\s+up\b',
    ]
    for pattern in angry_patterns:
        if re.search(pattern, text_lower):
            return ACTOR_ANGRY
    
    # Playful indicators
    playful_patterns = [
        r'\bhaha\b', r'\blol\b', r'\b:[\)\(]\b', r'\bfun\b', r'\bcool\b',
    ]
    for pattern in playful_patterns:
        if re.search(pattern, text_lower):
            return ACTOR_PLAYFUL
    
    return ACTOR_NORMAL


# ----------------------------
# State Machine Actions
# ----------------------------

class Phase5StateMachine:
    """
    Phase-5 state machine with B3 strict gate enforcement.
    """
    
    def __init__(self, prompts: List[Prompt], seed_base: str = "default"):
        self.prompts = prompts
        self.state = Phase5GameState(seed_base=seed_base)
    
    def initialize(self, mode: str = "STORY") -> Phase5GameState:
        """Initialize game and select first prompt."""
        self.state.mode = mode
        self.state.state = STATE_PLAY
        self._select_next_prompt()
        return self.state
    
    def _select_next_prompt(self) -> None:
        """Select next prompt using deterministic selector."""
        # Create selector-compatible state
        selector_state = SelectorGameState(
            mode=self.state.mode,
            seed_base=self.state.seed_base,
            progress=GameProgress(
                valid_groups=self.state.valid_groups_count,
                invalid_attempts=self.state.failure_count,
            ),
            coverage=CoverageState(
                zero_present=self.state.zero_present,
                operator_present=self.state.operator_present,
                scope_present=self.state.scope_present,
            ),
            used_prompt_ids=self.state.used_prompt_ids.copy(),
        )
        
        prompt = select_next_prompt(selector_state, self.prompts)
        
        self.state.current_prompt_id = prompt.prompt_id
        self.state.current_prompt_text = prompt.text
        # Map bank prompt to schema prompt_type (default NOTICE for story prompts)
        self.state.current_prompt_type = "NOTICE"
        
        if prompt.prompt_id not in self.state.used_prompt_ids:
            self.state.used_prompt_ids.append(prompt.prompt_id)
    
    def _update_coverage(self, text: str) -> None:
        """Update coverage state from submitted text."""
        flags = infer_event_flags(text)
        if flags["zero"]:
            self.state.zero_present = True
        if flags["operator"]:
            self.state.operator_present = True
        if flags["scope"]:
            self.state.scope_present = True
    
    def _apply_safety_check(self, text: str) -> None:
        """Check for anger/hostility and apply de-escalation if needed."""
        actor = detect_actor_state(text)
        self.state.actor_state = actor
        
        if actor == ACTOR_HOSTILE:
            self.state.is_deescalating = True
            self.state.deescalation_message = DEESCALATE_MSG_HOSTILE
        elif actor == ACTOR_ANGRY:
            self.state.is_deescalating = True
            self.state.deescalation_message = DEESCALATE_MSG_ANGRY
        else:
            self.state.is_deescalating = False
            self.state.deescalation_message = None
    
    def submit_group(self, sentences: List[str]) -> Phase5GameState:
        """
        Submit a sentence group for validation.
        Enforces B3 strict gate: no downstream until 3/3 valid groups.
        """
        # Store submission
        self.state.last_submitted_sentences = sentences
        combined_text = " ".join(sentences)
        
        # Safety check
        self._apply_safety_check(combined_text)
        
        # Validate structure
        is_valid, message = validate_group_structure(sentences)
        
        if is_valid:
            # Accept group
            self.state.valid_groups_count += 1
            group_id = f"G{self.state.valid_groups_count}"
            
            # Store in progress.groups
            valid_group = ValidGroup(
                group_id=group_id,
                sentences=[s.strip() for s in sentences if s.strip()],
                is_valid=True,
                validation_message=MSG_VALID,
            )
            self.state.groups.append(valid_group)
            
            # Update coverage
            self._update_coverage(combined_text)
            
            # Update validation status
            self.state.last_validation_status = VALIDATION_VALID
            self.state.last_validation_message = MSG_VALID
            
            # Reset failure count on success
            self.state.failure_count = 0
            self.state.soft_cap_active = False
            
            # Check gate completion
            if self.state.is_gate_complete and self.state.is_coverage_satisfied:
                self.state.state = STATE_COMPLETION
            else:
                # Continue play, select next prompt
                self._select_next_prompt()
        else:
            # Reject group
            self.state.failure_count += 1
            self.state.last_validation_status = VALIDATION_INVALID
            self.state.last_validation_message = message
            
            # Check soft-cap
            if self.state.failure_count >= self.state.soft_cap_max_failures:
                self.state.soft_cap_active = True
                self._handle_auto_skip()
            elif self.state.failure_count >= self.state.soft_cap_max_failures - 2:
                # Approaching soft-cap
                self.state.soft_cap_active = True
                self.state.last_validation_message = MSG_SOFT_CAP_APPROACHING
        
        return self.state
    
    def _handle_auto_skip(self) -> None:
        """Handle auto-skip when soft-cap is reached."""
        self.state.last_validation_message = MSG_AUTO_SKIP
        self.state.failure_count = 0  # Reset for next prompt
        self._select_next_prompt()
    
    def transition_to_pipeline(self) -> Phase5GameState:
        """Transition to pipeline execution after gate completion."""
        if not (self.state.is_gate_complete and self.state.is_coverage_satisfied):
            raise ValueError("Cannot transition to pipeline: gate not complete")
        
        self.state.state = STATE_PIPELINE_EXECUTION
        return self.state
    
    def abort(self) -> Phase5GameState:
        """Abort the game."""
        self.state.state = STATE_ABORTED
        return self.state
    
    def get_output(self) -> Dict[str, Any]:
        """Get schema-compliant output dict."""
        return self.state.to_output_dict()


# ----------------------------
# CLI
# ----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Phase-5 State Machine Runner (v0.1.0)")
    parser.add_argument("--bank", default="phase5-prompt-bank-v0.1.0.json", help="Path to prompt bank")
    parser.add_argument("--seed", default="default_user", help="Seed base for deterministic selection")
    parser.add_argument("--mode", choices=["STORY", "LAB"], default="STORY", help="Game mode")
    parser.add_argument("--action", choices=["init", "submit", "abort", "pipeline"], required=True)
    parser.add_argument("--sentences", nargs="*", help="Sentences to submit (for submit action)")
    parser.add_argument("--state-file", default="phase5_state.json", help="State file path")
    parser.add_argument("--out", default="phase5_game_output.json", help="Output file path")
    args = parser.parse_args()
    
    # Load prompt bank
    try:
        _, prompts = load_prompt_bank(args.bank)
    except Exception as e:
        print(f"FAIL: Cannot load prompt bank: {e}")
        return 1
    
    # Initialize or load state machine
    sm = Phase5StateMachine(prompts, seed_base=args.seed)
    
    if args.action == "init":
        sm.initialize(mode=args.mode)
    elif args.action == "submit":
        if not args.sentences or len(args.sentences) < 2:
            print("FAIL: submit action requires --sentences with 2-3 sentences")
            return 1
        # Load existing state if present
        state_path = Path(args.state_file)
        if state_path.exists():
            # For simplicity, re-init; real impl would deserialize state
            sm.initialize(mode=args.mode)
        else:
            sm.initialize(mode=args.mode)
        sm.submit_group(args.sentences)
    elif args.action == "abort":
        sm.initialize(mode=args.mode)
        sm.abort()
    elif args.action == "pipeline":
        sm.initialize(mode=args.mode)
        # Simulate completion for testing
        if not sm.state.is_gate_complete:
            print("FAIL: gate not complete, cannot transition to pipeline")
            return 1
        sm.transition_to_pipeline()
    
    # Write output
    output = sm.get_output()
    Path(args.out).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Output written to {args.out}")
    print(json.dumps(output, indent=2))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
