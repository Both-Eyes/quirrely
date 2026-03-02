#!/usr/bin/env python3
"""
Phase-5 Deterministic Prompt Selector + Coverage Engine
Version: 0.1.0

Purpose
- Deterministically select the next Phase-5 prompt from a locked prompt bank.
- Track simple coverage targets across 3 valid sentence-groups (Phase-5 gate).
- Provide lightweight, transparent, non-Phase-1 coverage inference utilities.

This file is intentionally:
- deterministic (same inputs -> same outputs)
- read-only w.r.t. Phase-1..4 (it does not recompute any LNCP metrics)
- compatible with the Phase-5 gate concept: 3/3 valid sentence-groups before feedback.

NOTES
- This engine does NOT validate LNCP canonical rows; Phase-5 group validity is assumed
  to be enforced elsewhere (e.g., a group-level validator).
- Coverage here is *structural presence* (operators / scopes / zeros) inferred from raw text.
  It is used only to steer prompt selection and to evaluate "coverage complete" under H2.

ALIGNMENT (v0.1.0):
- Text field: prompt_text (bank uses prompt_text)
- Coverage tags: tags.coverage (array of strings)
- Coverage vocabulary: NONE_EVENTS, ZERO_ONLY, OPERATOR_ONLY, SCOPE_ONLY,
                       ZERO+OPERATOR, ZERO+SCOPE, OPERATOR+SCOPE, ALL_THREE
- Safety field: tags.safety (STRING, not array): NEUTRAL, DEESCALATE, RESET
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ----------------------------
# Locked constants (v0.1.0)
# ----------------------------

PHASE5_VERSION = "0.1.0"
PROMPT_BANK_VERSION = "0.4.0"
PROMPT_BANK_COMPATIBLE_VERSIONS = ["0.1.0", "0.2.0", "0.3.0", "0.4.0"]

# Deterministic selection salt (keep constant for this version)
SELECTION_SALT = "phase5_prompt_select_v0.1.0"

# Coverage targets (H2-style: ensure each event type appears at least once across valid groups)
COVERAGE_EVENT_TYPES = ("zero", "operator", "scope")

# Coverage tag vocabulary as used in phase5-prompt-bank-v0.1.0.json (EXACT MATCH)
COVERAGE_TAGS = (
    "NONE_EVENTS",
    "ZERO_ONLY",
    "OPERATOR_ONLY",
    "SCOPE_ONLY",
    "ZERO+OPERATOR",
    "ZERO+SCOPE",
    "OPERATOR+SCOPE",
    "ALL_THREE",
)

# Safety tag vocabulary as used in phase5-prompt-bank-v0.1.0.json (EXACT MATCH)
SAFETY_TAGS = ("NEUTRAL", "DEESCALATE", "RESET")

# Priority order for selecting prompts to cover missing event-types
# (Fixed order prevents drift)
COVERAGE_PRIORITY = ("ZERO_ONLY", "OPERATOR_ONLY", "SCOPE_ONLY", "ALL_THREE", "NONE_EVENTS")


# ----------------------------
# Data structures
# ----------------------------

@dataclasses.dataclass(frozen=True)
class Prompt:
    prompt_id: str
    mode: str  # "STORY" or "LAB"
    text: str  # from prompt_text field in bank
    tags: Dict[str, Any]
    safety: str  # from tags.safety (string): NEUTRAL, DEESCALATE, RESET

    @property
    def coverage_tags(self) -> List[str]:
        """Extract coverage tags from tags.coverage (array of strings)."""
        cov = self.tags.get("coverage", [])
        if isinstance(cov, str):
            return [cov] if cov else []
        if isinstance(cov, list):
            return [c for c in cov if isinstance(c, str)]
        return []


@dataclasses.dataclass
class CoverageState:
    """
    Tracks which event-types have been observed at least once across valid groups.
    """
    zero_present: bool = False
    operator_present: bool = False
    scope_present: bool = False

    # Counts for debugging/telemetry (optional)
    groups_counted: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "zero_present": self.zero_present,
            "operator_present": self.operator_present,
            "scope_present": self.scope_present,
            "groups_counted": self.groups_counted,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CoverageState":
        return cls(
            zero_present=bool(d.get("zero_present", False)),
            operator_present=bool(d.get("operator_present", False)),
            scope_present=bool(d.get("scope_present", False)),
            groups_counted=int(d.get("groups_counted", 0)),
        )

    def is_complete(self) -> bool:
        return self.zero_present and self.operator_present and self.scope_present


@dataclasses.dataclass
class GameProgress:
    valid_groups: int = 0
    invalid_attempts: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {"valid_groups": self.valid_groups, "invalid_attempts": self.invalid_attempts}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GameProgress":
        return cls(
            valid_groups=int(d.get("valid_groups", 0)),
            invalid_attempts=int(d.get("invalid_attempts", 0)),
        )


@dataclasses.dataclass
class GameState:
    """
    Minimal state needed for deterministic selection and coverage tracking.
    """
    mode: str  # "STORY" or "LAB"
    seed_base: str  # stable seed per session/user
    progress: GameProgress
    coverage: CoverageState

    # Tracking for determinism + avoiding repeats
    used_prompt_ids: List[str] = dataclasses.field(default_factory=list)

    # Active prompt (selected)
    current_prompt_id: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "phase5_version": PHASE5_VERSION,
            "mode": self.mode,
            "seed_base": self.seed_base,
            "progress": self.progress.as_dict(),
            "coverage": self.coverage.as_dict(),
            "used_prompt_ids": list(self.used_prompt_ids),
            "current_prompt_id": self.current_prompt_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GameState":
        return cls(
            mode=str(d.get("mode", "STORY")),
            seed_base=str(d.get("seed_base", "")),
            progress=GameProgress.from_dict(d.get("progress", {})),
            coverage=CoverageState.from_dict(d.get("coverage", {})),
            used_prompt_ids=list(d.get("used_prompt_ids", [])),
            current_prompt_id=d.get("current_prompt_id"),
        )


# ----------------------------
# Prompt bank IO
# ----------------------------

def load_prompt_bank(path: str | Path) -> Tuple[str, List[Prompt]]:
    """
    Load prompt bank from JSON file.
    
    Bank structure (v0.1.0):
    - prompt_text: string (the prompt text)
    - tags.coverage: array of strings (coverage tags)
    - tags.safety: string (safety tag: NEUTRAL, DEESCALATE, RESET)
    """
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))

    bank_version = data.get("prompt_bank_version", "")
    if bank_version not in PROMPT_BANK_COMPATIBLE_VERSIONS:
        raise ValueError(f"Prompt bank version mismatch: expected one of {PROMPT_BANK_COMPATIBLE_VERSIONS}, got {bank_version}")

    prompts_raw = data.get("prompts", [])
    prompts: List[Prompt] = []
    for item in prompts_raw:
        # Extract tags dict
        tags = item.get("tags", {})
        if not isinstance(tags, dict):
            tags = {}

        # Bank uses prompt_text (not text)
        text = item.get("prompt_text", "")
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Bank uses tags.safety as STRING (not list)
        safety = tags.get("safety", "NEUTRAL")
        if not isinstance(safety, str):
            safety = str(safety) if safety is not None else "NEUTRAL"

        prompts.append(
            Prompt(
                prompt_id=str(item.get("prompt_id", "")),
                mode=str(item.get("mode", "")),
                text=text,
                tags=tags,
                safety=safety,
            )
        )
    return bank_version, prompts


# ----------------------------
# Deterministic selection
# ----------------------------

def _sha256_int(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h, 16)


def _choice_deterministic(items: List[Any], seed: str) -> Any:
    if not items:
        raise ValueError("No items to choose from")
    idx = _sha256_int(seed) % len(items)
    return items[idx]


def _desired_coverage_tags(state: GameState) -> List[str]:
    """
    Determine desired coverage tags based on missing event-types.
    H2-aligned: aim to achieve at least one instance of each event type (zero/operator/scope).
    """
    missing = []
    if not state.coverage.zero_present:
        missing.append("ZERO_ONLY")
    if not state.coverage.operator_present:
        missing.append("OPERATOR_ONLY")
    if not state.coverage.scope_present:
        missing.append("SCOPE_ONLY")

    # If all complete, default to "NONE_EVENTS" for lightweight/baseline prompts
    if not missing:
        return ["NONE_EVENTS"]

    # Return first missing in priority order
    for tag in COVERAGE_PRIORITY:
        if tag in missing:
            return [tag]
    return missing


def select_next_prompt(state: GameState, prompts: List[Prompt]) -> Prompt:
    """
    Deterministically selects the next prompt, using:
    - mode filter (STORY/LAB)
    - coverage targeting (missing event types)
    - no-repeat preference (avoid used_prompt_ids when possible)
    - stable hash selection for tie-breaking
    """
    if state.mode not in ("STORY", "LAB"):
        raise ValueError(f"Invalid mode: {state.mode}")

    desired_tags = _desired_coverage_tags(state)

    # Candidates: same mode AND matching at least one desired coverage tag
    def matches(prompt: Prompt) -> bool:
        if prompt.mode != state.mode:
            return False
        cov = set(prompt.coverage_tags)
        return any(tag in cov for tag in desired_tags)

    candidates = [p for p in prompts if matches(p)]
    if not candidates:
        # Fallback: mode-only
        candidates = [p for p in prompts if p.mode == state.mode]

    # Prefer unused prompts if possible
    unused = [p for p in candidates if p.prompt_id not in set(state.used_prompt_ids)]
    pool = unused if unused else candidates

    # Deterministic tie-break seed
    step_index = state.progress.valid_groups + state.progress.invalid_attempts
    desired_key = ",".join(desired_tags)
    seed = f"{PHASE5_VERSION}|{state.seed_base}|{state.mode}|{step_index}|{desired_key}|{SELECTION_SALT}"

    chosen = _choice_deterministic(pool, seed)

    # Record selection
    state.current_prompt_id = chosen.prompt_id
    if chosen.prompt_id not in state.used_prompt_ids:
        state.used_prompt_ids.append(chosen.prompt_id)

    return chosen


# ----------------------------
# Coverage inference (lightweight)
# ----------------------------

_ZERO_RE = re.compile(r"[.!?;:…]+")  # punctuation stops/pauses (conservative)
_OPERATOR_RE = re.compile(r"[%+\-*/=<>^|\\&]+")  # connective symbols (conservative)
_SCOPE_RE = re.compile(r"[\(\)\[\]\{\}\"'""'']+")  # brackets/quotes (conservative)


def infer_event_flags(text: str) -> Dict[str, bool]:
    """
    Infer structural event presence from raw text.
    This is NOT Phase-1; it's a lightweight Phase-5 coverage helper.
    """
    t = text or ""
    return {
        "zero": bool(_ZERO_RE.search(t)),
        "operator": bool(_OPERATOR_RE.search(t)),
        "scope": bool(_SCOPE_RE.search(t)),
    }


def coverage_profile(flags: Dict[str, bool]) -> str:
    """
    Map event flags to bank coverage categories.
    Uses EXACT vocabulary from phase5-prompt-bank-v0.1.0.json.
    """
    z = bool(flags.get("zero"))
    o = bool(flags.get("operator"))
    s = bool(flags.get("scope"))
    count = sum([z, o, s])

    if count == 0:
        return "NONE_EVENTS"
    if count == 1:
        if z:
            return "ZERO_ONLY"
        if o:
            return "OPERATOR_ONLY"
        return "SCOPE_ONLY"
    if count == 2:
        if z and o:
            return "ZERO+OPERATOR"
        if z and s:
            return "ZERO+SCOPE"
        return "OPERATOR+SCOPE"
    # count == 3
    return "ALL_THREE"


def apply_valid_group_to_coverage(state: GameState, group_text: str) -> Dict[str, Any]:
    """
    Update coverage state based on a VALID group submission.
    Returns a small audit dict (flags + profile).
    """
    flags = infer_event_flags(group_text)
    prof = coverage_profile(flags)

    if flags["zero"]:
        state.coverage.zero_present = True
    if flags["operator"]:
        state.coverage.operator_present = True
    if flags["scope"]:
        state.coverage.scope_present = True

    state.coverage.groups_counted += 1

    return {"flags": flags, "profile": prof}


def is_gate_complete(state: GameState, required_valid_groups: int = 3) -> bool:
    """
    Gate completion rule (B3 strict gate + H2 coverage):
    - Must have required_valid_groups valid groups (default 3)
    - Coverage must be complete (zero/operator/scope each present at least once)
    """
    return state.progress.valid_groups >= required_valid_groups and state.coverage.is_complete()


# ----------------------------
# Minimal CLI (optional utility)
# ----------------------------

def _load_state(path: str | Path) -> GameState:
    p = Path(path)
    d = json.loads(p.read_text(encoding="utf-8"))
    return GameState.from_dict(d)


def _save_state(path: str | Path, state: GameState) -> None:
    p = Path(path)
    p.write_text(json.dumps(state.as_dict(), indent=2, sort_keys=True), encoding="utf-8")


def cli():
    parser = argparse.ArgumentParser(description="Phase-5 deterministic prompt selection + coverage engine")
    parser.add_argument("--bank", default="phase5-prompt-bank-v0.1.0.json", help="Path to prompt bank JSON")
    parser.add_argument("--state", required=True, help="Path to state JSON (read/write)")
    parser.add_argument("--action", choices=["select", "accept_group", "fail"], required=True)
    parser.add_argument("--group_text", default="", help="Group text (only for accept_group)")
    args = parser.parse_args()

    _, prompts = load_prompt_bank(args.bank)
    state = _load_state(args.state)

    if args.action == "select":
        prompt = select_next_prompt(state, prompts)
        _save_state(args.state, state)
        print(json.dumps({
            "selected_prompt": {
                "prompt_id": prompt.prompt_id,
                "mode": prompt.mode,
                "text": prompt.text,
                "tags": prompt.tags,
                "safety": prompt.safety,
            },
            "state": state.as_dict(),
        }, indent=2, sort_keys=True))
        return

    if args.action == "fail":
        state.progress.invalid_attempts += 1
        # No additional UX logic here (soft-cap/auto-skip is handled by the caller/UI layer)
        _save_state(args.state, state)
        print(json.dumps({"state": state.as_dict()}, indent=2, sort_keys=True))
        return

    if args.action == "accept_group":
        state.progress.valid_groups += 1
        audit = apply_valid_group_to_coverage(state, args.group_text)
        _save_state(args.state, state)
        print(json.dumps({
            "audit": audit,
            "gate_complete": is_gate_complete(state),
            "state": state.as_dict(),
        }, indent=2, sort_keys=True))
        return


if __name__ == "__main__":
    cli()
