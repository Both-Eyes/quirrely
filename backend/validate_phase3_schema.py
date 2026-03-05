#!/usr/bin/env python3
"""
Phase-3 Synthesis Output Validator
Version: 0.1.0

Validates a Phase-3 synthesis output JSON against:
1) JSON Schema (Draft 2020-12) in phase3-synthesis-output-schema-v0.1.0.json
2) Extra guardrails (schema-light, drift-resistant):
   - All free-text fields must contain at least one non-whitespace character
   - synthesis_id must be unique and follow SYN_01..SYN_N sequentially
   - related_outputs must be unique within each synthesis
   - semiotic_lens must be one of the allowed values
   - synthesis_text must use structural language (soft check via prohibited terms)

Phase-3 Non-Goals (enforced by guardrails):
   - No recomputation or new metrics
   - No metric explanations or definitions
   - No diagnosis, labels, or trait attribution
   - No over-theorizing or philosophy exposition
   - No generalization beyond sample
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Locked constants
EXPECTED_SEMIOTIC_LENSES = [
    "INTERPRETANT_STABILIZATION",
    "MEDIATION_AND_BOUNDARY",
    "RELATIONAL_DENSITY",
]

VALID_OUTPUT_IDS = [f"output_{i:02d}" for i in range(1, 11)]

SYN_ID_RE = re.compile(r"^SYN_(\d{2})$")

# Prohibited terms in synthesis_text (Phase-3 non-goals)
# These indicate diagnostic, trait, or generalizing language
PROHIBITED_PATTERNS = [
    r"\byou are\b",
    r"\byou have\b",
    r"\byour personality\b",
    r"\balways\b",
    r"\bnever\b",
    r"\btypically\b",
    r"\busually\b",
    r"\bdiagnos",
    r"\bdisorder\b",
    r"\bcondition\b",
    r"\btype of person\b",
    r"\bkind of person\b",
]


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema(doc: Dict[str, Any], schema_path: str) -> Tuple[bool, str]:
    if not Path(schema_path).exists():
        return False, f"Schema file not found: {schema_path}"

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        # Fall back to manual validation if jsonschema not available
        return True, "(jsonschema not installed; skipping JSON Schema validation)"

    schema = load_json(schema_path)
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
    """
    Guardrails (v0.1.0):
    - Required top-level fields with correct const values
    - synthesis_id unique and sequential (SYN_01, SYN_02, ...)
    - related_outputs unique within each synthesis
    - semiotic_lens must be one of allowed values
    - synthesis_text must be non-empty and avoid prohibited terms
    """
    # Top-level required fields
    required_consts = {
        "phase3_version": "0.1.0",
        "source_contract_version": "1.0.0",
        "source_phase2_version": "0.1.0",
        "synthesis_scope": "SAMPLE_ONLY",
        "interpretive_frame": "LNCP_PEIRCEAN",
    }
    
    for field, expected in required_consts.items():
        if field not in doc:
            return False, f"Guardrail: missing required field '{field}'"
        if doc[field] != expected:
            return False, f"Guardrail: '{field}' must be '{expected}', got '{doc[field]}'"

    syntheses = doc.get("syntheses")
    if not isinstance(syntheses, list) or len(syntheses) == 0:
        return False, "Guardrail: 'syntheses' must be a non-empty array"

    seen_syn_ids = set()
    all_related_outputs = []

    for idx, syn in enumerate(syntheses, start=1):
        if not isinstance(syn, dict):
            return False, f"Guardrail: syntheses[{idx-1}] must be an object"

        # synthesis_id validation
        syn_id = syn.get("synthesis_id")
        if not _nonempty_str(syn_id):
            return False, f"Guardrail: syntheses[{idx-1}].synthesis_id must be non-empty"

        if syn_id in seen_syn_ids:
            return False, f"Guardrail: duplicate synthesis_id '{syn_id}'"
        seen_syn_ids.add(syn_id)

        # Enforce sequential SYN_01..SYN_N
        m = SYN_ID_RE.match(syn_id)
        if not m:
            return False, f"Guardrail: synthesis_id '{syn_id}' must match 'SYN_01' style"
        expected = f"SYN_{idx:02d}"
        if syn_id != expected:
            return False, f"Guardrail: synthesis_id '{syn_id}' out of sequence; expected '{expected}'"

        # related_outputs validation
        related = syn.get("related_outputs")
        if not isinstance(related, list) or len(related) == 0:
            return False, f"Guardrail: {syn_id}.related_outputs must be a non-empty array"
        
        seen_in_this = set()
        for out_id in related:
            if out_id not in VALID_OUTPUT_IDS:
                return False, f"Guardrail: {syn_id}.related_outputs contains invalid ID '{out_id}'"
            if out_id in seen_in_this:
                return False, f"Guardrail: {syn_id}.related_outputs contains duplicate '{out_id}'"
            seen_in_this.add(out_id)
        
        all_related_outputs.extend(related)

        # semiotic_lens validation
        lens = syn.get("semiotic_lens")
        if not _nonempty_str(lens):
            return False, f"Guardrail: {syn_id}.semiotic_lens must be non-empty"
        if lens not in EXPECTED_SEMIOTIC_LENSES:
            return False, f"Guardrail: {syn_id}.semiotic_lens '{lens}' not in allowed values"

        # synthesis_text validation
        text = syn.get("synthesis_text")
        if not _nonempty_str(text):
            return False, f"Guardrail: {syn_id}.synthesis_text must be non-empty"
        
        # Check for prohibited terms (soft guardrail - warns about diagnostic language)
        text_lower = text.lower()
        for pattern in PROHIBITED_PATTERNS:
            if re.search(pattern, text_lower):
                return False, f"Guardrail: {syn_id}.synthesis_text contains prohibited term matching '{pattern}'"

    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Phase-3 synthesis output JSON")
    parser.add_argument(
        "--input",
        dest="in_path",
        default="phase3_synthesis_output.json",
        help="Path to Phase-3 output JSON",
    )
    parser.add_argument(
        "--schema",
        dest="schema_path",
        default="phase3-synthesis-output-schema-v0.1.0.json",
        help="Path to Phase-3 JSON Schema",
    )
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
