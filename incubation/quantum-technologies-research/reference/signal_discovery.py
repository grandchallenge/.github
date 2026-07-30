#!/usr/bin/env python3
"""Reference evaluator for QTR-SIG-WP00 signal candidates.

This program performs exact finite-domain enumeration and diagnostic metric
calculation. It does not prove asymptotic complexity, QSP admissibility, or
quantum advantage.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Callable, Iterable

EVALUATOR_VERSION = "0.1.0"
ROUND_DIGITS = 12


def hamming_weight(bits: tuple[int, ...]) -> int:
    return sum(bits)


def predicate_or(bits: tuple[int, ...]) -> int:
    return int(any(bits))


def predicate_majority(bits: tuple[int, ...]) -> int:
    return int(2 * hamming_weight(bits) > len(bits))


def predicate_parity(bits: tuple[int, ...]) -> int:
    return hamming_weight(bits) % 2


PREDICATES: dict[str, Callable[[tuple[int, ...]], int]] = {
    "or": predicate_or,
    "majority": predicate_majority,
    "parity": predicate_parity,
}


def signal_hamming_normalized(bits: tuple[int, ...]) -> tuple[float, ...]:
    n = len(bits)
    return (2.0 * hamming_weight(bits) / n - 1.0,)


def signal_marked_amplitude(bits: tuple[int, ...]) -> tuple[float, ...]:
    return (math.sqrt(hamming_weight(bits) / len(bits)),)


def signal_parity_phase(bits: tuple[int, ...]) -> tuple[float, ...]:
    return (-1.0 if hamming_weight(bits) % 2 else 1.0,)


SIGNALS: dict[str, Callable[[tuple[int, ...]], tuple[float, ...]]] = {
    "hamming_normalized": signal_hamming_normalized,
    "marked_amplitude": signal_marked_amplitude,
    "parity_phase": signal_parity_phase,
}


def enumerate_domain(candidate: dict[str, Any]) -> list[tuple[int, ...]]:
    n = candidate["input_width"]
    domain = list(itertools.product((0, 1), repeat=n))
    promise = candidate["promise_domain"]
    if promise["kind"] == "all_inputs":
        return domain
    if promise["kind"] == "hamming_weights":
        allowed = set(promise["weights"])
        return [bits for bits in domain if hamming_weight(bits) in allowed]
    raise ValueError(f"Unknown promise kind: {promise['kind']}")


def signature_key(signature: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(round(value, ROUND_DIGITS) for value in signature)


def euclidean(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("Signature dimensions differ")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evaluate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    predicate = PREDICATES[candidate["predicate_id"]]
    signal = SIGNALS[candidate["signal"]["implementation"]]
    domain = enumerate_domain(candidate)
    if not domain:
        raise ValueError(f"Empty promise domain for {candidate['candidate_id']}")

    rows: list[dict[str, Any]] = []
    grouped: dict[tuple[float, ...], list[dict[str, Any]]] = {}
    for bits in domain:
        signature = signal(bits)
        if len(signature) != candidate["signal"]["dimension"]:
            raise ValueError(
                f"Dimension mismatch for {candidate['candidate_id']}: "
                f"declared {candidate['signal']['dimension']}, observed {len(signature)}"
            )
        row = {
            "input": "".join(str(bit) for bit in bits),
            "hamming_weight": hamming_weight(bits),
            "label": predicate(bits),
            "signature": [round(value, ROUND_DIGITS) for value in signature],
        }
        rows.append(row)
        grouped.setdefault(signature_key(signature), []).append(row)

    collision_witnesses: list[dict[str, Any]] = []
    collision_pairs = 0
    for signature, members in sorted(grouped.items()):
        zero_members = [row for row in members if row["label"] == 0]
        one_members = [row for row in members if row["label"] == 1]
        collision_pairs += len(zero_members) * len(one_members)
        if zero_members and one_members:
            collision_witnesses.append(
                {
                    "signature": list(signature),
                    "zero_input": zero_members[0]["input"],
                    "one_input": one_members[0]["input"],
                }
            )

    zero_rows = [row for row in rows if row["label"] == 0]
    one_rows = [row for row in rows if row["label"] == 1]
    if not zero_rows or not one_rows:
        empirical_gap = 0.0
    else:
        empirical_gap = min(
            euclidean(tuple(zero["signature"]), tuple(one["signature"]))
            for zero in zero_rows
            for one in one_rows
        )

    ordered_scalar_labels: list[dict[str, Any]] | None = None
    alternations = 0
    if candidate["signal"]["dimension"] == 1:
        ordered_scalar_labels = []
        scalar_labels: list[int] = []
        for signature, members in sorted(grouped.items(), key=lambda item: item[0][0]):
            labels = sorted({member["label"] for member in members})
            ordered_scalar_labels.append(
                {
                    "signal": signature[0],
                    "labels": labels,
                    "multiplicity": len(members),
                }
            )
            scalar_labels.append(labels[0] if len(labels) == 1 else -1)
        if -1 not in scalar_labels:
            alternations = sum(
                left != right
                for left, right in zip(scalar_labels, scalar_labels[1:])
            )

    declared_queries = candidate["cost"]["declared_queries_per_signal_call"]
    dimension = candidate["signal"]["dimension"]
    utility_index = empirical_gap / (
        (1.0 + declared_queries)
        * (1.0 + alternations)
        * (1.0 + math.log2(1.0 + dimension))
    )

    report: dict[str, Any] = {
        "candidate_id": candidate["candidate_id"],
        "predicate_id": candidate["predicate_id"],
        "domain_size": len(domain),
        "dimension": dimension,
        "distinct_signal_count": len(grouped),
        "semantic_sufficient_on_domain": collision_pairs == 0,
        "cross_label_collisions": collision_pairs,
        "collision_witnesses": collision_witnesses,
        "empirical_gap": round(empirical_gap, ROUND_DIGITS),
        "alternation_degree_lower_bound": alternations,
        "declared_queries_per_signal_call": declared_queries,
        "utility_index": round(utility_index, ROUND_DIGITS),
        "ordered_scalar_labels": ordered_scalar_labels,
    }
    report["report_sha256"] = canonical_digest(report)
    return report


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("candidates"), list):
        raise ValueError("Registry must contain a candidates array")
    return payload


def evaluate_registry(
    registry: dict[str, Any], candidate_ids: Iterable[str] | None = None
) -> dict[str, Any]:
    selected = set(candidate_ids or [])
    reports = [
        evaluate_candidate(candidate)
        for candidate in registry["candidates"]
        if not selected or candidate["candidate_id"] in selected
    ]
    found = {report["candidate_id"] for report in reports}
    missing = selected - found
    if missing:
        raise ValueError(f"Unknown candidate identifiers: {sorted(missing)}")
    payload = {
        "evaluator_version": EVALUATOR_VERSION,
        "registry_version": registry["registry_version"],
        "reports": reports,
    }
    payload["payload_sha256"] = canonical_digest(payload)
    return payload


def default_registry_path() -> Path:
    return Path(__file__).resolve().parents[1] / "registry" / "signal-candidates.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=default_registry_path())
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="Evaluate only this candidate identifier. May be repeated.",
    )
    parser.add_argument("--output", type=Path, help="Write the canonical JSON report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = evaluate_registry(load_registry(args.registry), args.candidate)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
