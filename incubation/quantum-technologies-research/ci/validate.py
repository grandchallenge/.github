#!/usr/bin/env python3
"""Fail-closed structural and executable validation for QTR-SIG-WP00."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

import signal_discovery as sd  # noqa: E402


class ValidationError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"Missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_candidate_shape(candidate: dict[str, Any], schema: dict[str, Any]) -> None:
    candidate_id = candidate.get("candidate_id", "<missing>")
    required = set(schema["required"])
    properties = set(schema["properties"])
    missing = sorted(required - set(candidate))
    extra = sorted(set(candidate) - properties)
    require(not missing, f"{candidate_id}: missing fields {missing}")
    require(not extra, f"{candidate_id}: unknown fields {extra}")

    require(candidate["input_width"] > 0, f"{candidate_id}: input_width must be positive")
    require(candidate["predicate_id"] in sd.PREDICATES, f"{candidate_id}: unknown predicate")
    implementation = candidate["signal"]["implementation"]
    require(implementation in sd.SIGNALS, f"{candidate_id}: unknown signal implementation")
    require(candidate["signal"]["dimension"] > 0, f"{candidate_id}: invalid dimension")

    for field in ("family", "status", "evidence_class"):
        allowed = set(schema["properties"][field]["enum"])
        require(candidate[field] in allowed, f"{candidate_id}: invalid {field}")

    promise = candidate["promise_domain"]
    require(promise["kind"] in {"all_inputs", "hamming_weights"}, f"{candidate_id}: bad promise")
    if promise["kind"] == "hamming_weights":
        weights = promise.get("weights", [])
        require(weights, f"{candidate_id}: empty promised weight set")
        require(
            all(0 <= weight <= candidate["input_width"] for weight in weights),
            f"{candidate_id}: promised weight outside input range",
        )

    require(
        candidate["oracle_model"]["id"] == "bit_query",
        f"{candidate_id}: WP00 registry requires the locked bit-query model",
    )
    require(
        candidate["cost"]["declared_queries_per_signal_call"] >= 0,
        f"{candidate_id}: negative query count",
    )


def validate_expected_metrics(candidate: dict[str, Any], report: dict[str, Any]) -> None:
    expected = candidate["expected_metrics"]
    candidate_id = candidate["candidate_id"]
    require(
        report["semantic_sufficient_on_domain"]
        == expected["semantic_sufficient_on_domain"],
        f"{candidate_id}: semantic sufficiency mismatch",
    )
    require(
        report["cross_label_collisions"] == expected["cross_label_collisions"],
        f"{candidate_id}: collision count mismatch",
    )
    require(
        math.isclose(report["empirical_gap"], expected["empirical_gap"], abs_tol=1e-10),
        f"{candidate_id}: empirical gap mismatch",
    )
    require(
        report["alternation_degree_lower_bound"]
        == expected["alternation_degree_lower_bound"],
        f"{candidate_id}: alternation lower-bound mismatch",
    )


def validate_migration_manifest(manifest: dict[str, Any]) -> None:
    require(manifest["programme_id"] == "QTR", "Migration manifest has wrong programme")
    require(
        manifest["target_repository"] == "grandchallenge/QUANTUM-TECHNOLOGIES",
        "Migration manifest has wrong target repository",
    )
    require(
        manifest["status"] in {"awaiting_target_repository", "migrated_candidate", "adopted"},
        "Migration manifest has invalid status",
    )
    for relative in manifest["required_files"]:
        require((ROOT / relative).is_file(), f"Migration manifest references missing file: {relative}")


def main() -> int:
    schema = load_json(ROOT / "schemas" / "signal-candidate.schema.json")
    registry = load_json(ROOT / "registry" / "signal-candidates.json")
    manifest = load_json(ROOT / "MIGRATION_MANIFEST.json")
    baseline = load_json(ROOT / "evidence" / "baseline-report.json")

    require(schema.get("additionalProperties") is False, "Schema must fail closed on unknown fields")
    require(registry.get("registry_version") == "0.1.0", "Unexpected registry version")
    candidates = registry.get("candidates")
    require(isinstance(candidates, list) and candidates, "Registry candidates must be nonempty")

    seen: set[str] = set()
    for candidate in candidates:
        validate_candidate_shape(candidate, schema)
        candidate_id = candidate["candidate_id"]
        require(candidate_id not in seen, f"Duplicate candidate identifier: {candidate_id}")
        seen.add(candidate_id)
        report = sd.evaluate_candidate(candidate)
        validate_expected_metrics(candidate, report)

    replay = sd.evaluate_registry(registry)
    require(replay == baseline, "Baseline report does not match deterministic replay")
    validate_migration_manifest(manifest)

    print(
        f"QTR-SIG-WP00 validation passed: {len(candidates)} candidates, "
        f"payload {replay['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"QTR validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
