#!/usr/bin/env python3
"""
generate_phase4a_v0_1_0.py
Phase-4a (Prompting Mode) deterministic generator.

Inputs: Phase-3 synthesis JSON (read-only)
Outputs: Phase-4a prompt_sets JSON matching phase4a-prompting-output-schema-v0.1.0.json

Determinism locks:
- prompt types emitted in fixed order: NOTICE → REFLECT → REWRITE → COMPARE
- prompt_set_id = PS_01, PS_02, ... in the same order as Phase-3 syntheses[]
- template variant selection = SHA-256(seed) % N
  seed = "{phase3_version}|{synthesis_id}|{prompt_type}|phase4a_v0.1.0"
- template library is a closed set embedded in this file (rev requires new version)

Note: Phase-4a is prompting (questions/invitations). It must not advise, diagnose,
recompute, or introduce new metric values. Prompts may reference the Phase-3 synthesis
text as the authoritative structural description.

Version: 0.1.0
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List


PHASE4A_VERSION = "0.1.0"
SOURCE_CONTRACT_VERSION = "1.0.0"
SOURCE_PHASE3_VERSION = "0.1.0"
SOURCE_PHASE2_VERSION = "0.1.0"

PROMPT_TYPE_ORDER = ["NOTICE", "REFLECT", "REWRITE", "COMPARE"]

# Closed template library (v0.1.0)
# Placeholders supported: {synthesis_text}, {semiotic_lens}, {n_outputs}, {outputs_list}
TEMPLATES: Dict[str, List[str]] = {
    "NOTICE": [
        "Read this slowly: {synthesis_text} What detail feels most central?",
        "Hold this in mind: {synthesis_text} Where does it feel simplest?",
        "Look for the structural move described here: {synthesis_text} Where is it?",
        "Notice what the synthesis calls out: {synthesis_text} What stands out first?",
        "Scan for the boundary-work named here: {synthesis_text} What is visible?",
    ],
    "REFLECT": [
        "If you stayed with this structure, what would be easy to repeat?",
        "What might this structure make effortless, in this sample only?",
        "Where does this structure leave room for the reader to fill in?",
        "What does this structural shape keep out of the sentence, for now?",
        "If you wrote three more sentences, what would you expect to recur?",
    ],
    "REWRITE": [
        "Rewrite one sentence by adding a single aside in parentheses.",
        "Rewrite the sentence once, then add a pause marker and compare.",
        "Rewrite with one connective symbol (like / or :) and reread it.",
        "Rewrite the sentence in two shorter sentences, then reread both.",
        "Rewrite the sentence as one longer sentence, keeping the same idea.",
    ],
    "COMPARE": [
        "Compare two versions: one plain, one with a small nested aside.",
        "Compare your original sentence to a version with one clear pause.",
        "Compare a version with a connector symbol to one without it.",
        "Compare a compact version to an expanded version—what changes first?",
        "Compare two rewrites and name which feels more \"you\" today.",
    ],
}


def _stable_index(seed: str, n: int) -> int:
    if n <= 0:
        raise ValueError("Template list size must be > 0")
    digest = sha256(seed.encode("utf-8")).hexdigest()
    return int(digest, 16) % n


def _render(template: str, *, synthesis_text: str, semiotic_lens: str, related_outputs: List[str]) -> str:
    # Keep rendering strict and predictable.
    outputs_list = ", ".join(related_outputs)
    rendered = template.format(
        synthesis_text=synthesis_text.strip(),
        semiotic_lens=semiotic_lens.strip(),
        n_outputs=str(len(related_outputs)),
        outputs_list=outputs_list,
    ).strip()
    # Ensure non-empty
    if not rendered or not rendered.strip():
        raise ValueError("Rendered prompt text is empty")
    return rendered


def generate_phase4a_prompting_output(phase3: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministically generate Phase-4a output from Phase-3 synthesis JSON.
    """
    # Basic shape checks (avoid assumptions)
    phase3_version = phase3.get("phase3_version")
    if phase3_version != SOURCE_PHASE3_VERSION:
        raise ValueError(f"Unsupported phase3_version: {phase3_version!r} (expected {SOURCE_PHASE3_VERSION})")

    syntheses = phase3.get("syntheses")
    if not isinstance(syntheses, list):
        raise ValueError("Phase-3 input must contain list field 'syntheses'")

    prompt_sets: List[Dict[str, Any]] = []

    for idx, syn in enumerate(syntheses, start=1):
        synthesis_id = syn.get("synthesis_id")
        semiotic_lens = syn.get("semiotic_lens", "")
        synthesis_text = syn.get("synthesis_text", "")
        related_outputs = syn.get("related_outputs", [])

        if not synthesis_id or not isinstance(synthesis_id, str):
            raise ValueError(f"Synthesis at index {idx-1} missing valid synthesis_id")
        if not isinstance(related_outputs, list) or not all(isinstance(x, str) for x in related_outputs):
            raise ValueError(f"Synthesis {synthesis_id} has invalid related_outputs (must be list[str])")
        if not isinstance(synthesis_text, str) or not synthesis_text.strip():
            raise ValueError(f"Synthesis {synthesis_id} has empty synthesis_text")

        prompt_set_id = f"PS_{idx:02d}"

        prompts: List[Dict[str, str]] = []
        for prompt_type in PROMPT_TYPE_ORDER:
            templates = TEMPLATES[prompt_type]
            seed = f"{phase3_version}|{synthesis_id}|{prompt_type}|phase4a_v{PHASE4A_VERSION}"
            template = templates[_stable_index(seed, len(templates))]
            prompt_text = _render(
                template,
                synthesis_text=synthesis_text,
                semiotic_lens=semiotic_lens or "",
                related_outputs=related_outputs,
            )
            prompts.append({
                "prompt_type": prompt_type,
                "prompt_text": prompt_text,
            })

        prompt_sets.append({
            "prompt_set_id": prompt_set_id,
            "synthesis_id": synthesis_id,
            "related_outputs": related_outputs,
            "semiotic_lens": semiotic_lens,
            "prompts": prompts,
        })

    return {
        "phase4a_version": PHASE4A_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "source_phase2_version": SOURCE_PHASE2_VERSION,
        "source_phase3_version": SOURCE_PHASE3_VERSION,
        "prompt_sets": prompt_sets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Phase-4a prompting output deterministically (v0.1.0)")
    parser.add_argument("--phase3", required=True, help="Path to Phase-3 synthesis JSON")
    parser.add_argument("--out", required=True, help="Path to write Phase-4a prompting JSON")
    args = parser.parse_args()

    phase3_path = Path(args.phase3)
    out_path = Path(args.out)

    with phase3_path.open("r", encoding="utf-8") as f:
        phase3 = json.load(f)

    phase4a = generate_phase4a_prompting_output(phase3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(phase4a, f, indent=2, sort_keys=True, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
