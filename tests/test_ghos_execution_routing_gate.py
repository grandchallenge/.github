from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ghos_execution_routing_gate", ROOT / "scripts/ghos_execution_routing_gate.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name] = MODULE; SPEC.loader.exec_module(MODULE)


class ExternalRoutingGateTests(unittest.TestCase):
    def fixture(self) -> Path:
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        root = Path(temporary.name); (root / ".github/workflows").mkdir(parents=True); (root / ".ghos-routing").mkdir()
        return root

    def registry(self, root: Path, entries: list[dict]) -> None:
        value = {"record_type": "GHOS_EXECUTION_ROUTING_REGISTRY", "schema_version": "1.0.0", "repository": "grandchallenge/gcl-standards",
            "controllers": MODULE.ADMITTED_CONTROLLERS, "workflows": entries, "claim_boundaries": MODULE.CLAIM_BOUNDARIES}
        (root / ".ghos-routing/workflows.json").write_text(json.dumps(value), encoding="utf-8")

    def test_external_gate_rejects_validator_removal_plus_hidden_workflow(self):
        root = self.fixture()
        (root / ".github/workflows/ci.yml").write_text("name: standards-policy\non: pull_request\njobs:\n  standards-policy:\n    runs-on: ubuntu-latest\n    steps: []\n", encoding="utf-8")
        self.registry(root, [{"path": ".github/workflows/ci.yml", "observed_features": [], "topology": "BOUNDED_ATOMIC", "controller_id": None}])
        (root / ".github/workflows/hidden.yml").write_text("on:\n  schedule:\n    - cron: '0 0 * * *'\njobs:\n  write:\n    runs-on: ubuntu-latest\n    steps:\n      - run: gh api -X POST repos/x/y/issues\n", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.RoutingGateError, "coverage mismatch"):
            MODULE.validate(root, "grandchallenge/gcl-standards")

    def test_external_gate_accepts_exact_registered_controller(self):
        root = self.fixture()
        (root / ".github/workflows/ci.yml").write_text("on: push\njobs:\n  write:\n    runs-on: ubuntu-latest\n    steps:\n      - run: gh api -X POST repos/x/y/issues\n", encoding="utf-8")
        observed = ["OPAQUE_EXECUTION", "WRITE_CAPABLE"]
        self.registry(root, [{"path": ".github/workflows/ci.yml", "observed_features": observed, "topology": "PERSISTENT_CONTROLLER_REQUIRED", "controller_id": "GITHUB_ACTIONS"}])
        MODULE.validate(root, "grandchallenge/gcl-standards")

    def test_project_item_add_is_write_capable(self):
        workflow = {"jobs": {"sync": {"runs-on": "ubuntu-latest", "steps": [{"run": "gh project item-add 1 --owner grandchallenge --url https://github.com/grandchallenge/example/issues/1"}]}}}
        self.assertEqual(["OPAQUE_EXECUTION", "WRITE_CAPABLE"], MODULE.features(workflow))

    def test_external_gate_rejects_cross_repository_registry_reuse(self):
        root = self.fixture()
        (root / ".github/workflows/ci.yml").write_text("on: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps: []\n", encoding="utf-8")
        self.registry(root, [{"path": ".github/workflows/ci.yml", "observed_features": [], "topology": "BOUNDED_ATOMIC", "controller_id": None}])
        with self.assertRaisesRegex(MODULE.RoutingGateError, "repository identity mismatch"):
            MODULE.validate(root, "grandchallenge/.github")

    def test_proposed_repository_registry_matches_all_workflow_bytes(self):
        MODULE.validate(ROOT, "grandchallenge/.github")


if __name__ == "__main__": unittest.main()
