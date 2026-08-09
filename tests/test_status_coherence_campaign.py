from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "governance"
    / "review-campaigns"
    / "GCL-STATUS-COHERENCE-001.json"
)


class StatusCoherenceCampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_campaign_has_exact_two_source_subjects(self) -> None:
        subjects = {
            row["repository"]: row for row in self.config["subjects"]
        }
        self.assertEqual(
            {
                repository: row["pull_request"]
                for repository, row in subjects.items()
            },
            {
                "grandchallenge/INTELLECT": 52,
                "grandchallenge/gcl-standards": 36,
            },
        )
        self.assertNotIn("grandchallenge/.github", subjects)

    def test_constitution_is_forbidden_and_all_repair_paths_are_required(self) -> None:
        subjects = {
            row["repository"]: row for row in self.config["subjects"]
        }
        self.assertEqual(
            subjects["grandchallenge/INTELLECT"]["forbidden_changed_paths"],
            ["CONSTITUTION.md"],
        )
        self.assertIn(
            "governance/constitutional_authority_schedule.json",
            subjects["grandchallenge/INTELLECT"]["required_changed_paths"],
        )
        self.assertIn(
            "standards/history/GCL-GHOS-00-0.1.0.md",
            subjects["grandchallenge/gcl-standards"]["required_changed_paths"],
        )
        self.assertIn(
            "tests/test_status_coherence.py",
            subjects["grandchallenge/gcl-standards"]["required_changed_paths"],
        )

    def test_campaign_starts_without_fabricated_findings_or_authorization(self) -> None:
        self.assertEqual(self.config["agent_findings"], {})
        self.assertEqual(self.config["human_stewards"], ["fyremael"])
        self.assertEqual(
            self.config["primary_pr"],
            {"repository": "grandchallenge/gcl-standards", "pull_request": 36},
        )
        self.assertEqual(
            self.config["receipt"]["repository"],
            "grandchallenge/gcl-standards",
        )


if __name__ == "__main__":
    unittest.main()
