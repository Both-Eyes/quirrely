#!/usr/bin/env python3
"""
Phase-5 Schema + Guardrails Validator
Version: 0.1.0

Validates a Phase-5 game-state JSON document against:
1) phase5-game-output-schema-v0.1.0.json (Draft 2020-12)
2) Extra LNCP Phase-5 guardrails that are not fully expressible in JSON Schema.

Usage:
  python validate_phase5_schema.py --input phase5_output.json --schema phase5-game-output-schema-v0.1.0.json

Exit codes:
  0 = PASS
  1 = FAIL
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(doc: dict, schema_path: str) -> tuple[bool, str]:
    if not Path(schema_path).exists():
        return False, f"Schema file not found: {schema_path}"

    try:
        from jsonschema import Draft202012Validator
    except Exception:
        return False, "jsonschema library not installed (requires Draft 2020-12 support)"

    schema = _load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)

    if errors:
        e = errors[0]
        # json_path is available in newer jsonschema; fall back if missing
        where = getattr(e, "json_path", None) or "/".join([str(x) for x in e.path]) or "$"
        return False, f"Schema validation: {where}: {e.message}"

    return True, ""


def _count_words(s: str) -> int:
    # word count for guardrails: split on whitespace, ignore empty chunks
    return len([w for w in s.strip().split() if w])


def validate_guardrails(doc: dict) -> tuple[bool, str]:
    """
    Guardrails (v0.1.0):
    - gate.is_complete must equal (gate.valid_groups_count == gate.required_valid_groups)
    - progress.groups may contain ONLY valid groups; count must equal gate.valid_groups_count
    - group_ids must be sequential from G1 with no gaps, matching list order
    - state must be coherent with gate completion:
        * ENTRY/PLAY/COVERAGE_CHECK/LAB_CHALLENGE => gate.is_complete must be False
        * COMPLETION/PIPELINE_EXECUTION => gate.is_complete must be True
        * ABORTED => no additional constraint
    - routing constraints:
        * If gate.is_complete is False => all phase*_allowed must be False
        * If gate.is_complete is True  => phase1/2/3_allowed must be True
        * Phase4a/4b remain optional unlocks (may be True or False), but never True before completion
    - safety de-escalation coherence:
        * If safety.is_deescalating is True => actor_state must be HOSTILE or ANGRY AND deescalation_message non-empty
        * If actor_state is NORMAL or PLAYFUL => safety.is_deescalating must be False AND deescalation_message must be absent or empty
    - strict-gate UX minimalism:
        * validation_message and last_submission.validation.message (if present) must be short (<= 120 chars)
    """
    gate = doc["gate"]
    required = gate["required_valid_groups"]
    count = gate["valid_groups_count"]
    is_complete = gate["is_complete"]

    if is_complete != (count == required):
        return False, "Guardrail: gate.is_complete must equal (valid_groups_count == required_valid_groups)"

    # progress.groups: only valid groups and must match valid_groups_count
    groups = doc["progress"]["groups"]
    if len(groups) != count:
        return False, "Guardrail: progress.groups length must equal gate.valid_groups_count"

    # Ensure only valid groups are stored in progress.groups
    for i, g in enumerate(groups):
        if g.get("is_valid") is not True:
            return False, f"Guardrail: progress.groups[{i}] must have is_valid=true (invalid attempts belong in prompting.last_submission)"

    # group_id sequential and ordered
    expected_ids = [f"G{i}" for i in range(1, len(groups) + 1)]
    actual_ids = [g.get("group_id") for g in groups]
    if actual_ids != expected_ids:
        return False, f"Guardrail: progress.groups group_id sequence must be {expected_ids}, got {actual_ids}"

    # state coherence with completion
    state = doc["state"]
    pre_complete_states = {"ENTRY", "PLAY", "COVERAGE_CHECK", "LAB_CHALLENGE"}
    post_complete_states = {"COMPLETION", "PIPELINE_EXECUTION"}

    if state in pre_complete_states and is_complete:
        return False, f"Guardrail: state={state} requires gate.is_complete=false"
    if state in post_complete_states and not is_complete:
        return False, f"Guardrail: state={state} requires gate.is_complete=true"

    # routing constraints
    routing = doc["routing"]
    if not is_complete:
        for k in ["phase1_allowed", "phase2_allowed", "phase3_allowed", "phase4a_allowed", "phase4b_allowed"]:
            if routing.get(k) is not False:
                return False, "Guardrail: before gate completion, all routing phase*_allowed flags must be false"
    else:
        for k in ["phase1_allowed", "phase2_allowed", "phase3_allowed"]:
            if routing.get(k) is not True:
                return False, "Guardrail: after gate completion, routing.phase1_allowed/phase2_allowed/phase3_allowed must be true"
        # Phase 4a/4b may be toggled post-completion; no further constraint.

    # safety coherence
    safety = doc["safety"]
    actor_state = safety["actor_state"]
    is_deescalating = safety["is_deescalating"]
    de_msg = safety.get("deescalation_message", "")

    if is_deescalating:
        if actor_state not in {"HOSTILE", "ANGRY"}:
            return False, "Guardrail: safety.is_deescalating=true requires actor_state in {HOSTILE, ANGRY}"
        if not isinstance(de_msg, str) or not de_msg.strip():
            return False, "Guardrail: safety.is_deescalating=true requires non-empty safety.deescalation_message"
    else:
        if actor_state in {"NORMAL", "PLAYFUL"} and isinstance(de_msg, str) and de_msg.strip():
            return False, "Guardrail: actor_state NORMAL/PLAYFUL requires no deescalation_message when not deescalating"

    # strict-gate UX minimalism: short messages only (no rule leakage)
    for i, g in enumerate(groups):
        if "validation_message" in g:
            vm = g["validation_message"]
            if not isinstance(vm, str):
                return False, f"Guardrail: progress.groups[{i}].validation_message must be a string"
            if len(vm) > 120:
                return False, f"Guardrail: progress.groups[{i}].validation_message must be <= 120 chars"

    last_msg = doc["prompting"]["last_submission"]["validation"].get("message")
    if last_msg is not None:
        if not isinstance(last_msg, str):
            return False, "Guardrail: prompting.last_submission.validation.message must be a string when present"
        if len(last_msg) > 120:
            return False, "Guardrail: prompting.last_submission.validation.message must be <= 120 chars"

    return True, ""


def main() -> int:
    p = argparse.ArgumentParser(description="Validate Phase-5 JSON against schema + guardrails")
    p.add_argument("--input", default="phase5_game_output.json", help="Path to Phase-5 JSON output")
    p.add_argument("--schema", default="phase5-game-output-schema-v0.1.0.json", help="Path to Phase-5 JSON Schema")
    args = p.parse_args()

    try:
        doc = _load_json(args.input)
    except Exception as e:
        print(f"FAIL: Cannot load input JSON: {e}")
        return 1

    ok, err = validate_schema(doc, args.schema)
    if not ok:
        print(f"FAIL: {err}")
        return 1

    ok, err = validate_guardrails(doc)
    if not ok:
        print(f"FAIL: {err}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
