"""
Phase-1 Self-Assessment Compute Engine
Version: 1.0.0 (No Drift)

Implements the Phase-1 computation plan strictly derived from:
- LNCP Substrate Schema: v1.1.3-draft
- Phase-1 Output Contract: v1.0.0
- Phase-1 API Response Schema: v1.0.0

No schema drift. No invented fields. No additional outputs.
"""

import json
from collections import Counter
from typing import Any


def compute_phase1_response(rows: list[dict]) -> dict:
    """
    Compute Phase-1 Self-Assessment response from validated LNCP rows.
    
    Args:
        rows: List of LNCP row dictionaries (must conform to v1.1.3-draft schema)
    
    Returns:
        dict: Phase-1 API response conforming to phase1_api_response_schema_v1.0.0.json
    """
    
    # === OUTPUT 01: sentence_count ===
    sentence_count = len(rows)
    
    output_01 = {
        "output_id": "output_01",
        "name_user_facing": "How Much You Shared",
        "metrics": {
            "sentence_count": sentence_count
        }
    }
    
    # === OUTPUT 02: token_volume ===
    total_token_count = sum(len(row["tokens"]) for row in rows)
    mean_tokens_per_sentence = total_token_count / sentence_count if sentence_count > 0 else 0.0
    
    output_02 = {
        "output_id": "output_02",
        "name_user_facing": "Word-Level Detail",
        "metrics": {
            "total_token_count": total_token_count,
            "mean_tokens_per_sentence": mean_tokens_per_sentence
        }
    }
    
    # === OUTPUT 03: structural_variety ===
    signatures = [row["base_signature"] for row in rows]
    unique_signature_count = len(set(signatures))
    signature_variety_ratio = unique_signature_count / sentence_count if sentence_count > 0 else 0.0
    
    output_03 = {
        "output_id": "output_03",
        "name_user_facing": "Structural Fingerprints",
        "metrics": {
            "unique_signature_count": unique_signature_count,
            "signature_variety_ratio": signature_variety_ratio
        }
    }
    
    # === OUTPUT 04: signature_concentration ===
    signature_counter = Counter(signatures)
    signature_frequency_map = dict(signature_counter)
    
    # Sort by (count DESC, signature ASC), take top 3
    sorted_signatures = sorted(
        signature_counter.items(),
        key=lambda x: (-x[1], x[0])
    )
    top_3_signatures = sorted_signatures[:3]
    
    top_signatures = [
        {"signature": sig, "count": count}
        for sig, count in top_3_signatures
    ]
    
    top_signature_count_sum = sum(count for _, count in top_3_signatures)
    top_signature_coverage = top_signature_count_sum / sentence_count if sentence_count > 0 else 0.0
    
    output_04 = {
        "output_id": "output_04",
        "name_user_facing": "Your Most Common Patterns",
        "metrics": {
            "signature_frequency_map": signature_frequency_map,
            "top_signatures": top_signatures,
            "top_signature_coverage": top_signature_coverage
        }
    }
    
    # === OUTPUT 05: zero_event_presence ===
    total_zero_event_count = sum(len(row["zero_events"]) for row in rows)
    sentences_with_zero_events = sum(1 for row in rows if len(row["zero_events"]) > 0)
    zero_event_rate = sentences_with_zero_events / sentence_count if sentence_count > 0 else 0.0
    
    output_05 = {
        "output_id": "output_05",
        "name_user_facing": "What's Left Unsaid",
        "metrics": {
            "total_zero_event_count": total_zero_event_count,
            "sentences_with_zero_events": sentences_with_zero_events,
            "zero_event_rate": zero_event_rate
        }
    }
    
    # === OUTPUT 06: operator_event_presence ===
    total_operator_event_count = sum(len(row["operator_events"]) for row in rows)
    sentences_with_operator_events = sum(1 for row in rows if len(row["operator_events"]) > 0)
    operator_event_rate = sentences_with_operator_events / sentence_count if sentence_count > 0 else 0.0
    mean_operators_per_sentence = total_operator_event_count / sentence_count if sentence_count > 0 else 0.0
    
    output_06 = {
        "output_id": "output_06",
        "name_user_facing": "Connective Moves",
        "metrics": {
            "total_operator_event_count": total_operator_event_count,
            "sentences_with_operator_events": sentences_with_operator_events,
            "operator_event_rate": operator_event_rate,
            "mean_operators_per_sentence": mean_operators_per_sentence
        }
    }
    
    # === OUTPUT 07: scope_event_presence ===
    total_scope_event_count = sum(len(row["scope_events"]) for row in rows)
    sentences_with_scope_events = sum(1 for row in rows if len(row["scope_events"]) > 0)
    scope_event_rate = sentences_with_scope_events / sentence_count if sentence_count > 0 else 0.0
    mean_scopes_per_sentence = total_scope_event_count / sentence_count if sentence_count > 0 else 0.0
    
    output_07 = {
        "output_id": "output_07",
        "name_user_facing": "Layered Meaning",
        "metrics": {
            "total_scope_event_count": total_scope_event_count,
            "sentences_with_scope_events": sentences_with_scope_events,
            "scope_event_rate": scope_event_rate,
            "mean_scopes_per_sentence": mean_scopes_per_sentence
        }
    }
    
    # === OUTPUT 08: structural_density ===
    total_structural_events = total_operator_event_count + total_scope_event_count + total_zero_event_count
    structural_density = total_structural_events / sentence_count if sentence_count > 0 else 0.0
    
    output_08 = {
        "output_id": "output_08",
        "name_user_facing": "Complexity at a Glance",
        "metrics": {
            "total_structural_events": total_structural_events,
            "structural_density": structural_density
        }
    }
    
    # === OUTPUT 09: event_co_occurrence_profile ===
    sentences_with_all_three = 0
    sentences_with_none = 0
    sentences_with_operators_only = 0
    sentences_with_scopes_only = 0
    sentences_with_zeros_only = 0
    other_combinations = 0
    
    for row in rows:
        z = len(row["zero_events"])
        o = len(row["operator_events"])
        s = len(row["scope_events"])
        
        if z > 0 and o > 0 and s > 0:
            sentences_with_all_three += 1
        elif z == 0 and o == 0 and s == 0:
            sentences_with_none += 1
        elif o > 0 and z == 0 and s == 0:
            sentences_with_operators_only += 1
        elif s > 0 and z == 0 and o == 0:
            sentences_with_scopes_only += 1
        elif z > 0 and o == 0 and s == 0:
            sentences_with_zeros_only += 1
        else:
            other_combinations += 1
    
    co_occurrence_vector = [
        sentences_with_all_three,
        sentences_with_none,
        sentences_with_operators_only,
        sentences_with_scopes_only,
        sentences_with_zeros_only,
        other_combinations
    ]
    
    output_09 = {
        "output_id": "output_09",
        "name_user_facing": "How Your Patterns Combine",
        "metrics": {
            "sentences_with_all_three": sentences_with_all_three,
            "sentences_with_none": sentences_with_none,
            "sentences_with_operators_only": sentences_with_operators_only,
            "sentences_with_scopes_only": sentences_with_scopes_only,
            "sentences_with_zeros_only": sentences_with_zeros_only,
            "co_occurrence_vector": co_occurrence_vector
        }
    }
    
    # === OUTPUT 10: ticker_profile ===
    # Check if ANY row has ticker_expanded that is NOT null and NOT missing
    rows_with_ticker = [
        row for row in rows
        if row.get("ticker_expanded") is not None
    ]
    
    if len(rows_with_ticker) > 0:
        # AVAILABLE path
        all_tickers = []
        for row in rows_with_ticker:
            all_tickers.extend(row["ticker_expanded"])
        
        unique_ticker_count = len(set(all_tickers))
        ticker_counter = Counter(all_tickers)
        
        # Keys must be strings
        ticker_frequency_map = {str(k): v for k, v in ticker_counter.items()}
        
        # Sort by (count DESC, ticker_string ASC), take top 3
        sorted_tickers = sorted(
            ticker_counter.items(),
            key=lambda x: (-x[1], str(x[0]))
        )
        top_3_tickers = sorted_tickers[:3]
        
        top_tickers = [
            {"ticker": str(ticker), "count": count}
            for ticker, count in top_3_tickers
        ]
        
        output_10 = {
            "output_id": "output_10",
            "name_user_facing": "Your Structural Codes",
            "status": "AVAILABLE",
            "metrics": {
                "unique_ticker_count": unique_ticker_count,
                "ticker_frequency_map": ticker_frequency_map,
                "top_tickers": top_tickers
            }
        }
    else:
        # NOT_AVAILABLE path
        output_10 = {
            "output_id": "output_10",
            "name_user_facing": "Your Structural Codes",
            "status": "NOT_AVAILABLE",
            "reason": "ticker_expanded field not present in sample"
        }
    
    # === ASSEMBLE FINAL RESPONSE ===
    response = {
        "contract_version": "1.0.0",
        "outputs": {
            "sentence_count": output_01,
            "token_volume": output_02,
            "structural_variety": output_03,
            "signature_concentration": output_04,
            "zero_event_presence": output_05,
            "operator_event_presence": output_06,
            "scope_event_presence": output_07,
            "structural_density": output_08,
            "event_co_occurrence_profile": output_09,
            "ticker_profile": output_10
        }
    }
    
    return response


def compute_phase1_response_from_jsonl(text: str) -> dict:
    """
    Compute Phase-1 Self-Assessment response from JSONL text.
    
    Args:
        text: JSONL-formatted string with one LNCP row per line
    
    Returns:
        dict: Phase-1 API response conforming to phase1_api_response_schema_v1.0.0.json
    """
    rows = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    
    return compute_phase1_response(rows)


# === CLI Entry Point (optional) ===
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Read from file
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            jsonl_text = f.read()
    else:
        # Read from stdin
        jsonl_text = sys.stdin.read()
    
    result = compute_phase1_response_from_jsonl(jsonl_text)
    print(json.dumps(result, indent=2))
