from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "weekly_optimality_scorecard",
    ROOT / "scripts" / "weekly_optimality_scorecard.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIXTURE = ROOT / "tests" / "fixtures" / "weekly_optimality_snapshot.json"


class WeeklyOptimalityScorecardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.scorecard = MODULE.build_scorecard(self.snapshot)

    def test_build_is_deterministic_and_uses_fixed_metric_set(self) -> None:
        self.assertEqual(self.scorecard, MODULE.build_scorecard(self.snapshot))
        self.assertEqual(self.scorecard["record_id"], "GCL-OPT-SCORECARD-2026-W32")
        self.assertEqual(len(self.scorecard["metrics"]), 9)
        self.assertEqual(
            self.scorecard["metrics"]["median_pr_decision_time_hours"]["value"],
            24.0,
        )

    def test_incomplete_protection_readback_is_unknown_not_zero(self) -> None:
        metric = self.scorecard["metrics"]["unprotected_default_branches"]
        self.assertNotIn("value", metric)
        self.assertEqual(metric["status"], "unknown")
        deviation_id = metric["unknown"]["deviation_id"]
        self.assertIn(deviation_id, {item["id"] for item in self.scorecard["deviations"]})

    def test_deferred_registries_remain_unknown(self) -> None:
        for name in MODULE.UNKNOWN_REGISTRY_METRICS:
            metric = self.scorecard["metrics"][name]
            self.assertEqual(metric["status"], "unknown")
            self.assertNotIn("value", metric)

    def test_human_action_count_excludes_mechanical_actions(self) -> None:
        metric = self.scorecard["metrics"]["human_actions_per_governed_decision"]
        self.assertEqual(metric["value"], 1)
        self.assertEqual(
            metric["exclusions"], ["merge clicks", "2FA setup", "account recovery"]
        )

    def test_zero_math_violations_is_explicitly_not_global_correctness(self) -> None:
        metric = self.scorecard["metrics"]["github_inferred_mathematical_claims"]
        self.assertEqual(metric["value"], 0)
        self.assertIn(
            "zero observations do not imply global mathematical correctness",
            metric["exclusions"],
        )

    def test_only_exact_no_bypass_default_branch_ruleset_is_compliant(self) -> None:
        ruleset = {
            "enforcement": "active",
            "target": "branch",
            "bypass_actors": [],
            "conditions": {
                "ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}
            },
            "rules": [
                {"type": "deletion"},
                {"type": "non_fast_forward"},
                {"type": "pull_request"},
                {"type": "required_status_checks"},
            ],
        }
        self.assertTrue(MODULE.ruleset_protects_default_branch(ruleset, "main"))
        for mutation in (
            lambda value: value["bypass_actors"].append({"actor_id": 1}),
            lambda value: value["conditions"]["ref_name"].__setitem__(
                "include", ["refs/heads/release"]
            ),
            lambda value: value["rules"].pop(),
            lambda value: value.__setitem__("enforcement", "evaluate"),
        ):
            candidate = json.loads(json.dumps(ruleset))
            mutation(candidate)
            self.assertFalse(
                MODULE.ruleset_protects_default_branch(candidate, "main")
            )

    def test_status_readback_failure_remains_unknown(self) -> None:
        snapshot = json.loads(json.dumps(self.snapshot))
        snapshot["status_contradictions"] = None
        scorecard = MODULE.build_scorecard(snapshot)
        metric = scorecard["metrics"]["status_contradictions"]
        self.assertEqual(metric["status"], "unknown")
        self.assertNotIn("value", metric)

    def test_controlled_blocker_requires_exact_https_issue_link(self) -> None:
        self.assertTrue(
            MODULE.has_linked_controlled_blocker(
                "Blocked by https://github.com/grandchallenge/AETHER/issues/58"
            )
        )
        for body in (
            "https://github.com.evil.test/grandchallenge/AETHER/issues/58",
            "http://github.com/grandchallenge/AETHER/issues/58",
            "https://github.com/another-org/AETHER/issues/58",
            "https://github.com/grandchallenge/AETHER/pull/59",
            "https://github.com/grandchallenge/AETHER/issues/not-a-number",
        ):
            self.assertFalse(MODULE.has_linked_controlled_blocker(body))


if __name__ == "__main__":
    unittest.main()
