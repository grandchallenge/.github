from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference"))

import signal_discovery as sd  # noqa: E402


class SignalDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = sd.load_registry(ROOT / "registry" / "signal-candidates.json")
        cls.candidates = {
            candidate["candidate_id"]: candidate
            for candidate in cls.registry["candidates"]
        }

    def report(self, candidate_id: str):
        return sd.evaluate_candidate(self.candidates[candidate_id])

    def test_registry_metrics_match_executable_results(self):
        for candidate in self.registry["candidates"]:
            report = sd.evaluate_candidate(candidate)
            expected = candidate["expected_metrics"]
            self.assertEqual(
                report["semantic_sufficient_on_domain"],
                expected["semantic_sufficient_on_domain"],
            )
            self.assertEqual(
                report["cross_label_collisions"],
                expected["cross_label_collisions"],
            )
            self.assertAlmostEqual(
                report["empirical_gap"], expected["empirical_gap"], places=10
            )
            self.assertEqual(
                report["alternation_degree_lower_bound"],
                expected["alternation_degree_lower_bound"],
            )

    def test_parity_phase_exposes_access_cost(self):
        phase = self.report("parity_phase_n4")
        majority = self.report("majority_hamming_n5")
        self.assertEqual(phase["dimension"], majority["dimension"])
        self.assertGreater(phase["empirical_gap"], majority["empirical_gap"])
        self.assertGreater(
            phase["declared_queries_per_signal_call"],
            majority["declared_queries_per_signal_call"],
        )

    def test_parity_hamming_exposes_oscillation(self):
        report = self.report("parity_hamming_n4")
        self.assertTrue(report["semantic_sufficient_on_domain"])
        self.assertEqual(report["alternation_degree_lower_bound"], 4)

    def test_cross_label_collision_fails_semantic_gate(self):
        candidate = copy.deepcopy(self.candidates["parity_phase_n4"])
        candidate["candidate_id"] = "or_bad_parity_phase_n4"
        candidate["predicate_id"] = "or"
        report = sd.evaluate_candidate(candidate)
        self.assertFalse(report["semantic_sufficient_on_domain"])
        self.assertGreater(report["cross_label_collisions"], 0)
        self.assertTrue(report["collision_witnesses"])

    def test_registry_digest_is_deterministic(self):
        first = sd.evaluate_registry(self.registry)
        second = sd.evaluate_registry(json.loads(json.dumps(self.registry)))
        self.assertEqual(first["payload_sha256"], second["payload_sha256"])
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
