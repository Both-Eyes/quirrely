#!/usr/bin/env python3
"""
Deterministic Phase-4b Guidance Generator
Version: 0.1.0

Reads Phase-3 synthesis JSON (and optionally Phase-2/Phase-1 for future-proofing),
then deterministically produces Phase-4b guidance JSON that matches:
- phase4b-guidance-output-schema-v0.1.0.json

Determinism:
Template choice is SHA-256(seed) % N where:
seed = "{phase3_version}|{synthesis_id}|{item_type}|phase4b_v0.1.0"

DIFF FIXES APPLIED:
- Output includes synthesis_scope and interpretive_frame (required by schema)
- Uses correct field names: items, text (not guidance_items, item_text)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


PHASE4B_VERSION = "0.1.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.1.0"

# DIFF FIX: Add required schema constants
SYNTHESIS_SCOPE = "SAMPLE_ONLY"
INTERPRETIVE_FRAME = "LNCP_PEIRCEAN"

# Closed template library (v0.1.0) — edit only by bumping Phase-4b version + schema/validator.
TEMPLATES: Dict[str, List[str]] = {
    "GUIDE": [
        "Treat this synthesis as a structural snapshot: {synthesis_text}",
        "Use this as a map of the structure in this sample: {synthesis_text}",
        "Hold this lightly as a read of the sample's structure: {synthesis_text}",
    ],
    "PRACTICE": [
        "Try writing one more sentence that keeps the same structural feel, then compare.",
        "Draft a second sentence that matches this structure, and see what changes.",
        "Create a short follow-up sentence in the same style, then read them side-by-side.",
    ],
    "SCENARIO": [
        "Imagine this structure showing up in an email—what effect would it have?",
        "Picture this structure in a message to a friend—how would it land?",
        "Put this structure into a work note—what does it make easier or harder?",
    ],
    "COMPARE": [
        "Now try the opposite: add one boundary or connector and notice the shift.",
        "As a contrast, remove one structural layer and see how it reads.",
        "Compare with a version that adds a pause or bracket, then reread both.",
    ],
}


def sha256_mod(seed: str, n: int) -> int:
    """Deterministic index selection via SHA-256(seed) % n."""
    if n <= 0:
        raise ValueError("n must be > 0")
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


def pick_template(phase3_version: str, synthesis_id: str, item_type: str) -> str:
    """Pick a template deterministically for a given synthesis + item type."""
    variants = TEMPLATES[item_type]
    seed = f"{phase3_version}|{synthesis_id}|{item_type}|phase4b_v{PHASE4B_VERSION}"
    idx = sha256_mod(seed, len(variants))
    return variants[idx]


def render_item_text(template: str, synthesis_text: str) -> str:
    """Render template with minimal placeholders; keep Phase-3 wording intact when inserted."""
    return template.format(synthesis_text=synthesis_text.strip())


def generate_phase4b(
    phase3: Dict[str, Any],
    phase2: Optional[Dict[str, Any]] = None,
    phase1: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-4b guidance JSON from Phase-3 syntheses deterministically.
    Phase-2/Phase-1 are accepted for forward compatibility but are not required by v0.1.0 schema.
    """
    # Basic input assertions (non-exhaustive; validator handles the final contract)
    phase3_version = str(phase3.get("phase3_version", "")).strip()
    if not phase3_version:
        raise ValueError("Phase-3 input missing 'phase3_version'")

    source_contract_version = str(phase3.get("source_contract_version", SOURCE_CONTRACT_VERSION)).strip()

    # Prefer Phase-3 embedded versions when present
    source_phase2_version = str(phase3.get("source_phase2_version", "")).strip()
    if not source_phase2_version and isinstance(phase2, dict):
        source_phase2_version = str(phase2.get("phase2_version", "")).strip()
    if not source_phase2_version:
        source_phase2_version = SOURCE_PHASE2_VERSION

    syntheses = phase3.get("syntheses")
    if not isinstance(syntheses, list) or len(syntheses) == 0:
        raise ValueError("Phase-3 input 'syntheses' must be a non-empty list")

    guidance_sets: List[Dict[str, Any]] = []
    for idx, syn in enumerate(syntheses, start=1):
        synthesis_id = str(syn.get("synthesis_id", "")).strip()
        if not synthesis_id:
            raise ValueError(f"Synthesis at index {idx-1} missing 'synthesis_id'")

        related_outputs = syn.get("related_outputs")
        if not isinstance(related_outputs, list) or len(related_outputs) == 0:
            raise ValueError(f"{synthesis_id}: 'related_outputs' must be a non-empty list")

        semiotic_lens = str(syn.get("semiotic_lens", "")).strip()
        if not semiotic_lens:
            raise ValueError(f"{synthesis_id}: missing 'semiotic_lens'")

        synthesis_text = str(syn.get("synthesis_text", "")).strip()
        if not synthesis_text:
            raise ValueError(f"{synthesis_id}: missing 'synthesis_text'")

        guidance_set_id = f"GS_{idx:02d}"

        # Fixed order, per schema: GUIDE → PRACTICE → SCENARIO → COMPARE
        items = []
        for item_type in ("GUIDE", "PRACTICE", "SCENARIO", "COMPARE"):
            template = pick_template(
                phase3_version=phase3_version,
                synthesis_id=synthesis_id,
                item_type=item_type,
            )
            # GUIDE uses synthesis_text insertion; others are static
            if item_type == "GUIDE":
                text = render_item_text(template, synthesis_text=synthesis_text)
            else:
                text = template
            # DIFF FIX: Use correct field names per schema
            items.append({"item_type": item_type, "text": text})

        guidance_sets.append({
            "guidance_set_id": guidance_set_id,
            "synthesis_id": synthesis_id,
            "related_outputs": related_outputs,
            "semiotic_lens": semiotic_lens,
            "items": items,  # DIFF FIX: "items" not "guidance_items"
        })

    # DIFF FIX: Include synthesis_scope and interpretive_frame (required by schema)
    return {
        "phase4b_version": PHASE4B_VERSION,
        "source_contract_version": source_contract_version,
        "source_phase2_version": source_phase2_version,
        "source_phase3_version": phase3_version,
        "synthesis_scope": SYNTHESIS_SCOPE,
        "interpretive_frame": INTERPRETIVE_FRAME,
        "guidance_sets": guidance_sets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Phase-4b guidance output deterministically (v0.1.0)")
    parser.add_argument("--phase3", required=True, help="Path to Phase-3 synthesis JSON (required)")
    parser.add_argument("--phase2", required=False, help="Path to Phase-2 UX output JSON (optional)")
    parser.add_argument("--phase1", required=False, help="Path to Phase-1 compute output JSON (optional)")
    parser.add_argument("--out", required=True, help="Path to write Phase-4b JSON output")
    args = parser.parse_args()

    phase3 = json.loads(Path(args.phase3).read_text(encoding="utf-8"))
    phase2 = json.loads(Path(args.phase2).read_text(encoding="utf-8")) if args.phase2 else None
    phase1 = json.loads(Path(args.phase1).read_text(encoding="utf-8")) if args.phase1 else None

    out_obj = generate_phase4b(phase3=phase3, phase2=phase2, phase1=phase1)
    Path(args.out).write_text(json.dumps(out_obj, indent=2, sort_keys=False), encoding="utf-8")
    print(f"Phase-4b output written to {args.out}")


if __name__ == "__main__":
    main()
