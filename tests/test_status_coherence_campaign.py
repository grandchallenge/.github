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
        self.assertIn(
            ".github/workflows/ci.yml",
            subjects["grandchallenge/gcl-standards"]["required_changed_paths"],
        )
        self.assertIn(
            "tests/test_validate.py",
            subjects["grandchallenge/gcl-standards"]["required_changed_paths"],
        )

    def test_campaign_admits_exact_distinct_agent_findings(self) -> None:
        findings = self.config["agent_findings"]
        self.assertEqual(set(findings), {"adversary", "referee"})
        adversary = findings["adversary"]
        referee = findings["referee"]
        self.assertEqual(adversary["office"], "adversary")
        self.assertEqual(referee["office"], "referee")
        self.assertEqual(adversary["status"], "approved")
        self.assertEqual(referee["status"], "approved")
        self.assertEqual(
            adversary["subject_sha256"],
            "2eb93829c45978256075b28d18b19084d48b68a565411e0af05e2c7d8918dd7b",
        )
        self.assertEqual(referee["subject_sha256"], adversary["subject_sha256"])
        self.assertEqual(
            adversary["record_url"],
            "https://github.com/grandchallenge/gcl-standards/issues/35"
            "#issuecomment-5229564404",
        )
        self.assertEqual(
            referee["record_url"],
            "https://github.com/grandchallenge/gcl-standards/issues/35"
            "#issuecomment-5229588884",
        )
        self.assertNotEqual(adversary["reviewer_id"], referee["reviewer_id"])
        self.assertNotEqual(adversary["session_id"], referee["session_id"])
        self.assertEqual(
            self.config["finding_binding"], "campaign_contract_v1"
        )
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
