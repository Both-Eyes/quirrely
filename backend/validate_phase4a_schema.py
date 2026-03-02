#!/usr/bin/env python3
"""
Phase-4a Prompting Output Validator
Version: 0.1.0

Validates Phase-4a output JSON against JSON Schema (Draft 2020-12)
and enforces locked Phase-4a prompt counts/relationships:

- Each prompt_set has exactly 4 prompts
- Exactly 1 of each type: NOTICE, REFLECT, REWRITE, COMPARE
- prompt_text must contain at least one non-whitespace character
- prompt_set_id and synthesis_id must be unique across prompt_sets

Usage:
  python validate_phase4a_schema.py --input phase4a_output.json --schema phase4a-prompting-output-schema-v0.1.0.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

REQUIRED_TYPES = ["NOTICE", "REFLECT", "REWRITE", "COMPARE"]


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(doc: Dict[str, Any], schema_path: str) -> Tuple[bool, str]:
    """Validate against JSON Schema. Returns (ok, error_message)."""
    if not Path(schema_path).exists():
        return False, f"Schema file not found: {schema_path}"

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        # Fall back gracefully if jsonschema not installed
        return True, "(jsonschema not installed; skipping JSON Schema validation)"

    try:
        schema = load_json(schema_path)
    except Exception as e:
        return False, f"Cannot read schema file: {e}"

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        err = errors[0]
        json_path = getattr(err, "json_path", None)
        if not json_path:
            json_path = "$"
            for p in list(err.path):
                if isinstance(p, int):
                    json_path += f"[{p}]"
                else:
                    json_path += f".{p}"
        return False, f"Schema validation: {json_path}: {err.message}"
    return True, ""


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_guardrails(doc: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate Phase-4a guardrails. Returns (ok, error_message)."""
    prompt_sets = doc.get("prompt_sets", [])
    
    if not isinstance(prompt_sets, list) or len(prompt_sets) == 0:
        return False, "Guardrail: 'prompt_sets' must be a non-empty array"

    seen_ps = set()
    seen_syn = set()

    for i, ps in enumerate(prompt_sets):
        if not isinstance(ps, dict):
            return False, f"Guardrail: prompt_sets[{i}] must be an object"

        ps_id = ps.get("prompt_set_id")
        syn_id = ps.get("synthesis_id")

        if not _nonempty_str(ps_id):
            return False, f"Guardrail: prompt_sets[{i}].prompt_set_id must be non-empty"

        if ps_id in seen_ps:
            return False, f"Guardrail: Duplicate prompt_set_id at prompt_sets[{i}]: {ps_id}"
        seen_ps.add(ps_id)

        if not _nonempty_str(syn_id):
            return False, f"Guardrail: prompt_sets[{i}].synthesis_id must be non-empty"

        if syn_id in seen_syn:
            return False, f"Guardrail: Duplicate synthesis_id at prompt_sets[{i}]: {syn_id}"
        seen_syn.add(syn_id)

        prompts = ps.get("prompts", [])
        if not isinstance(prompts, list) or len(prompts) != 4:
            return False, f"Guardrail: prompt_sets[{i}].prompts must have exactly 4 items, got {len(prompts) if isinstance(prompts, list) else 'non-list'}"

        types = [p.get("prompt_type") for p in prompts]
        if sorted(types) != sorted(REQUIRED_TYPES):
            return False, f"Guardrail: prompt_sets[{i}] must contain exactly one each of {REQUIRED_TYPES}; got {types}"

        for j, p in enumerate(prompts):
            if not isinstance(p, dict):
                return False, f"Guardrail: prompt_sets[{i}].prompts[{j}] must be an object"

            t = p.get("prompt_type")
            txt = p.get("prompt_text")

            if t not in REQUIRED_TYPES:
                return False, f"Guardrail: prompt_sets[{i}].prompts[{j}].prompt_type invalid: {t}"

            if not _nonempty_str(txt):
                return False, f"Guardrail: prompt_sets[{i}].prompts[{j}].prompt_text must be non-empty"

    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase-4a output JSON")
    parser.add_argument(
        "--input",
        dest="in_path",
        default="phase4a_prompting_output.json",
        help="Path to Phase-4a output JSON",
    )
    parser.add_argument(
        "--schema",
        dest="schema_path",
        default="phase4a-prompting-output-schema-v0.1.0.json",
        help="Path to Phase-4a schema JSON",
    )
    args = parser.parse_args()

    try:
        doc = load_json(args.in_path)
    except Exception as e:
        print(f"FAIL: Cannot read input JSON: {e}")
        sys.exit(1)

    ok, err = validate_schema(doc, args.schema_path)
    if not ok:
        print(f"FAIL: {err}")
        sys.exit(1)
    if err:
        print(f"NOTE: {err}")

    ok, err = validate_guardrails(doc)
    if not ok:
        print(f"FAIL: {err}")
        sys.exit(1)

    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
