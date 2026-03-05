#!/usr/bin/env python3
"""
Phase-4b Guidance Mode Validator
Version: 0.1.0

Validates a Phase-4b guidance output JSON against:
1) JSON Schema (Draft 2020-12) in phase4b-guidance-output-schema-v0.1.0.json
2) Extra guardrails (schema-light, drift-resistant):
   - All free-text fields must contain at least one non-whitespace character
   - guidance_set_id must be unique and follow GS_01..GS_N sequentially
   - synthesis_id must be unique across guidance_sets
   - items must be exactly 4, and item_type order must be:
       GUIDE → PRACTICE → SCENARIO → COMPARE
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

EXPECTED_ITEM_TYPE_ORDER = ["GUIDE", "PRACTICE", "SCENARIO", "COMPARE"]
GS_ID_RE = re.compile(r"^GS_(\d{2})$")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(doc: Dict[str, Any], schema_path: str) -> Tuple[bool, str]:
    if not Path(schema_path).exists():
        return False, f"Schema file not found: {schema_path}"

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return False, "jsonschema library not installed"

    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        err = errors[0]
        # jsonschema has both "json_path" (newer) and "path" (older)
        json_path = getattr(err, "json_path", None)
        if not json_path:
            # Build a reasonable path string from err.path
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
    # Top-level required strings (schema enforces consts; we ensure non-empty anyway)
    # DIFF FIX: Check for correct field names per schema
    for k in [
        "phase4b_version",
        "source_contract_version",
        "source_phase2_version",
        "source_phase3_version",
        "synthesis_scope",
        "interpretive_frame",
    ]:
        if k not in doc:
            return False, f"Guardrail: missing required field '{k}'"
        if not _nonempty_str(doc[k]):
            return False, f"Guardrail: '{k}' must be non-empty"

    guidance_sets = doc.get("guidance_sets")
    if not isinstance(guidance_sets, list) or len(guidance_sets) == 0:
        return False, "Guardrail: 'guidance_sets' must be a non-empty array"

    seen_gs_ids = set()
    seen_synth_ids = set()

    for idx, gs in enumerate(guidance_sets, start=1):
        if not isinstance(gs, dict):
            return False, f"Guardrail: guidance_sets[{idx-1}] must be an object"

        gs_id = gs.get("guidance_set_id")
        if not _nonempty_str(gs_id):
            return False, f"Guardrail: guidance_sets[{idx-1}].guidance_set_id must be non-empty"

        if gs_id in seen_gs_ids:
            return False, f"Guardrail: duplicate guidance_set_id '{gs_id}'"
        seen_gs_ids.add(gs_id)

        # Enforce sequential GS_01..GS_N to support deterministic pipelines
        m = GS_ID_RE.match(gs_id)
        if not m:
            return False, f"Guardrail: guidance_set_id '{gs_id}' must match 'GS_01' style"
        expected = f"GS_{idx:02d}"
        if gs_id != expected:
            return False, f"Guardrail: guidance_set_id '{gs_id}' out of sequence; expected '{expected}'"

        synthesis_id = gs.get("synthesis_id")
        if not _nonempty_str(synthesis_id):
            return False, f"Guardrail: guidance_sets[{idx-1}].synthesis_id must be non-empty"
        if synthesis_id in seen_synth_ids:
            return False, f"Guardrail: duplicate synthesis_id '{synthesis_id}' across guidance_sets"
        seen_synth_ids.add(synthesis_id)

        semiotic_lens = gs.get("semiotic_lens")
        if not _nonempty_str(semiotic_lens):
            return False, f"Guardrail: guidance_sets[{idx-1}].semiotic_lens must be non-empty"

        # DIFF FIX: Schema uses "items" not "guidance_items"
        items = gs.get("items")
        if not isinstance(items, list):
            return False, f"Guardrail: guidance_sets[{idx-1}].items must be an array"
        if len(items) != 4:
            return False, f"Guardrail: guidance_sets[{idx-1}].items must have exactly 4 items"

        for j, item in enumerate(items):
            if not isinstance(item, dict):
                return False, f"Guardrail: items[{j}] in {gs_id} must be an object"

            item_type = item.get("item_type")
            if item_type != EXPECTED_ITEM_TYPE_ORDER[j]:
                return False, (
                    f"Guardrail: {gs_id}.items[{j}].item_type must be "
                    f"'{EXPECTED_ITEM_TYPE_ORDER[j]}' (got '{item_type}')"
                )

            # DIFF FIX: Schema uses "text" not "item_text"
            text = item.get("text")
            if not _nonempty_str(text):
                return False, f"Guardrail: {gs_id}.items[{j}].text must be non-empty"

    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase-4b guidance output JSON")
    parser.add_argument("--input", dest="in_path", default="phase4b_guidance_output.json", help="Path to Phase-4b output JSON")
    parser.add_argument("--schema", dest="schema_path", default="phase4b-guidance-output-schema-v0.1.0.json", help="Path to Phase-4b JSON Schema")
    args = parser.parse_args()

    try:
        doc = load_json(args.in_path)
    except Exception as e:
        print(f"FAIL: Cannot load input JSON: {e}")
        sys.exit(1)

    ok, err = validate_schema(doc, args.schema_path)
    if not ok:
        print(f"FAIL: {err}")
        sys.exit(1)

    ok, err = validate_guardrails(doc)
    if not ok:
        print(f"FAIL: {err}")
        sys.exit(1)

    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
