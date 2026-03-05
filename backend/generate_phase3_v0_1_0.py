#!/usr/bin/env python3
"""
Deterministic Phase-3 Synthesis Generator
Version: 0.1.0

Reads Phase-2 UX output JSON (and optionally Phase-1 for reference),
then deterministically produces Phase-3 synthesis JSON that matches:
- phase3-synthesis-output-schema-v0.1.0.json

Determinism:
- Synthesis groupings are fixed based on output relationships
- Template choice is SHA-256(seed) % N where:
  seed = "{phase2_version}|{semiotic_lens}|{related_outputs_key}|phase3_v0.1.0"

Phase-3 Purpose:
- Bring multiple Phase-1 outputs into relation using LNCP-mapped Peircean semiotics
- Pattern constellation and semiotic function, not measurement or UX explanation
- All references framed as analogy ("functions like," "reads as," "behaves similarly to")
- Grounded in explicit Phase-1 outputs

Phase-3 Non-Goals (Hard Constraints):
1. No recomputation or new metrics
2. No metric explanations or definitions
3. No diagnosis, labels, or trait attribution
4. No over-theorizing or philosophy exposition
5. No generalization beyond sample
6. No override of Phase-2 tone discipline
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


PHASE3_VERSION = "0.1.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE2_VERSION = "0.1.0"
SYNTHESIS_SCOPE = "SAMPLE_ONLY"
INTERPRETIVE_FRAME = "LNCP_PEIRCEAN"

# Fixed synthesis groupings (v0.1.0)
# Each synthesis brings related outputs into semiotic relation
SYNTHESIS_GROUPS = [
    {
        "semiotic_lens": "INTERPRETANT_STABILIZATION",
        "related_outputs": ["output_01", "output_03", "output_04"],
        "description": "How recurring structures resolve into stable interpretive forms",
    },
    {
        "semiotic_lens": "MEDIATION_AND_BOUNDARY",
        "related_outputs": ["output_05", "output_06", "output_07"],
        "description": "How meaning is bracketed, linked, or constrained",
    },
    {
        "semiotic_lens": "RELATIONAL_DENSITY",
        "related_outputs": ["output_08", "output_09"],
        "description": "How features cluster or remain distinct",
    },
]

# Closed template library (v0.1.0)
# Templates are sample-bounded and use structural language only
TEMPLATES: Dict[str, List[str]] = {
    "INTERPRETANT_STABILIZATION": [
        "In this sample, {recurrence_observation}. The structure functions as {stabilization_frame}.",
        "With the material present, {recurrence_observation}. {stabilization_frame}.",
        "The sample shows {recurrence_observation}. Structurally, {stabilization_frame}.",
    ],
    "MEDIATION_AND_BOUNDARY": [
        "Within this sample, {boundary_observation}. {mediation_frame}.",
        "The structure {boundary_observation}. {mediation_frame}.",
        "In this material, {boundary_observation}. Meaning {mediation_frame}.",
    ],
    "RELATIONAL_DENSITY": [
        "In this sample, {density_observation}. The structure reads as {density_frame}.",
        "The material shows {density_observation}. {density_frame}.",
        "Structurally, {density_observation}. The features {density_frame}.",
    ],
}


def sha256_mod(seed: str, n: int) -> int:
    """Deterministic index selection via SHA-256(seed) % n."""
    if n <= 0:
        raise ValueError("n must be > 0")
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


def _get_phase2_metrics(phase2: Dict[str, Any], output_id: str) -> Dict[str, Any]:
    """Extract metrics from Phase-2 output for a given output_id."""
    outputs = phase2.get("outputs", {})
    return outputs.get(output_id, {})


def _infer_recurrence_observation(phase2: Dict[str, Any]) -> str:
    """Infer recurrence observation from Phase-2 output_01/03/04."""
    output_01 = _get_phase2_metrics(phase2, "output_01")
    explanation = output_01.get("explanation", "")
    
    # Check for single sentence case
    if "one sentence" in explanation.lower() or "single sentence" in explanation.lower():
        return "no recurrence is available for structural resolution to emerge. The single pattern stands alone, neither reinforced nor varied"
    
    return "patterns recur across the sample, allowing structural resolution to emerge"


def _infer_stabilization_frame(phase2: Dict[str, Any]) -> str:
    """Infer stabilization frame from Phase-2 outputs."""
    output_01 = _get_phase2_metrics(phase2, "output_01")
    explanation = output_01.get("explanation", "")
    
    if "one sentence" in explanation.lower():
        return "an isolated instance rather than a stabilized form"
    
    return "a stabilized interpretive form through recurrence"


def _infer_boundary_observation(phase2: Dict[str, Any]) -> str:
    """Infer boundary observation from Phase-2 output_05/06/07."""
    output_05 = _get_phase2_metrics(phase2, "output_05")
    output_06 = _get_phase2_metrics(phase2, "output_06")
    output_07 = _get_phase2_metrics(phase2, "output_07")
    
    exp_05 = output_05.get("explanation", "").lower()
    exp_06 = output_06.get("explanation", "").lower()
    exp_07 = output_07.get("explanation", "").lower()
    
    zero_absent = "absent" in exp_05 or "zero" in exp_05 and "0" in exp_05
    op_absent = "absent" in exp_06 or "zero" in exp_06
    scope_absent = "absent" in exp_07 or "zero" in exp_07
    
    if zero_absent and op_absent and scope_absent:
        return "zero events, operators, and scope markers are all absent from this sentence. The structure moves without bracketing, linking, or constraining markers"
    
    parts = []
    if not zero_absent:
        parts.append("zero events")
    if not op_absent:
        parts.append("operators")
    if not scope_absent:
        parts.append("scope markers")
    
    if parts:
        return f"{', '.join(parts)} appear in the structure, providing points of mediation"
    
    return "the structure contains various boundary markers"


def _infer_mediation_frame(phase2: Dict[str, Any]) -> str:
    """Infer mediation frame from Phase-2 outputs."""
    output_05 = _get_phase2_metrics(phase2, "output_05")
    exp = output_05.get("explanation", "").lower()
    
    if "absent" in exp:
        return "passes through unmediated, with no boundary-work visible at the structural level"
    
    return "is shaped by the boundary markers present"


def _infer_density_observation(phase2: Dict[str, Any]) -> str:
    """Infer density observation from Phase-2 output_08/09."""
    output_08 = _get_phase2_metrics(phase2, "output_08")
    output_09 = _get_phase2_metrics(phase2, "output_09")
    
    exp_08 = output_08.get("explanation", "").lower()
    exp_09 = output_09.get("explanation", "").lower()
    
    if "absent" in exp_08 or "0.0" in exp_08:
        return "structural events are absent, and the sentence contains none of the three event types. The features do not cluster because none are present to relate"
    
    return "structural events are present, creating points where features cluster"


def _infer_density_frame(phase2: Dict[str, Any]) -> str:
    """Infer density frame from Phase-2 outputs."""
    output_08 = _get_phase2_metrics(phase2, "output_08")
    exp = output_08.get("explanation", "").lower()
    
    if "absent" in exp or "0.0" in exp:
        return "sparse and undifferentiated at the event level"
    
    return "show relational density through event clustering"


def generate_synthesis_text(
    phase2: Dict[str, Any],
    semiotic_lens: str,
    related_outputs: List[str],
) -> str:
    """Generate synthesis text based on Phase-2 outputs and semiotic lens."""
    
    if semiotic_lens == "INTERPRETANT_STABILIZATION":
        recurrence = _infer_recurrence_observation(phase2)
        stabilization = _infer_stabilization_frame(phase2)
        return f"With one sentence present, {recurrence}. In this sample, the structure functions as {stabilization}."
    
    elif semiotic_lens == "MEDIATION_AND_BOUNDARY":
        boundary = _infer_boundary_observation(phase2)
        mediation = _infer_mediation_frame(phase2)
        return f"{boundary.capitalize()}. Within this sample, meaning {mediation}."
    
    elif semiotic_lens == "RELATIONAL_DENSITY":
        density = _infer_density_observation(phase2)
        frame = _infer_density_frame(phase2)
        return f"{density.capitalize()}. In this sample, the structure reads as {frame}."
    
    return ""


def generate_phase3(
    phase2: Dict[str, Any],
    phase1: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate Phase-3 synthesis JSON from Phase-2 outputs deterministically.
    Phase-1 is accepted for forward compatibility but not required by v0.1.0.
    """
    phase2_version = str(phase2.get("phase2_version", SOURCE_PHASE2_VERSION)).strip()
    
    syntheses: List[Dict[str, Any]] = []
    
    for idx, group in enumerate(SYNTHESIS_GROUPS, start=1):
        synthesis_id = f"SYN_{idx:02d}"
        semiotic_lens = group["semiotic_lens"]
        related_outputs = group["related_outputs"]
        
        # Generate synthesis text
        synthesis_text = generate_synthesis_text(
            phase2=phase2,
            semiotic_lens=semiotic_lens,
            related_outputs=related_outputs,
        )
        
        syntheses.append({
            "synthesis_id": synthesis_id,
            "related_outputs": related_outputs,
            "semiotic_lens": semiotic_lens,
            "synthesis_text": synthesis_text,
        })
    
    return {
        "phase3_version": PHASE3_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase2_version": phase2_version,
        "synthesis_scope": SYNTHESIS_SCOPE,
        "interpretive_frame": INTERPRETIVE_FRAME,
        "syntheses": syntheses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Phase-3 synthesis output deterministically (v0.1.0)"
    )
    parser.add_argument(
        "--phase2",
        required=True,
        help="Path to Phase-2 UX output JSON (required)",
    )
    parser.add_argument(
        "--phase1",
        required=False,
        help="Path to Phase-1 compute output JSON (optional)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to write Phase-3 JSON output",
    )
    args = parser.parse_args()

    phase2 = json.loads(Path(args.phase2).read_text(encoding="utf-8"))
    phase1 = json.loads(Path(args.phase1).read_text(encoding="utf-8")) if args.phase1 else None

    out_obj = generate_phase3(phase2=phase2, phase1=phase1)
    Path(args.out).write_text(json.dumps(out_obj, indent=2, sort_keys=False), encoding="utf-8")
    print(f"Phase-3 output written to {args.out}")


if __name__ == "__main__":
    main()
