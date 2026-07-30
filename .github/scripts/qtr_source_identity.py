#!/usr/bin/env python3
"""Emit exact byte lengths and SHA-256 identities for the QTR migration payload."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


DEFAULT_ROOT = Path("incubation/quantum-technologies-research")


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root
    manifest_path = root / "MIGRATION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    required = manifest["required_files"]

    records = []
    for relative in required:
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"missing migration payload file: {relative}")
        record = digest(path)
        record["relative_path"] = relative
        records.append(record)

    payload_identity = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    ledger = {
        "ledger_version": "0.1.0",
        "programme_id": "QTR",
        "source_repository": "grandchallenge/.github",
        "source_commit": args.source_commit,
        "source_path": root.as_posix(),
        "target_repository": "grandchallenge/QUANTUM-TECHNOLOGIES",
        "target_path": ".",
        "payload_identity_sha256": payload_identity,
        "files": records,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(ledger, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
