from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "governance"
    / "review-campaigns"
    / "GI-HUMAN-GOVERNANCE-TRANSITION-001.json"
)


class HumanGovernanceTransitionCampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_campaign_binds_only_the_exact_intellect_source_pr(self) -> None:
        self.assertEqual(
            self.config["primary_pr"],
            {"repository": "grandchallenge/INTELLECT", "pull_request": 54},
        )
        self.assertEqual(len(self.config["subjects"]), 1)
        subject = self.config["subjects"][0]
        self.assertEqual(subject["repository"], "grandchallenge/INTELLECT")
        self.assertEqual(subject["pull_request"], 54)
        self.assertEqual(subject["forbidden_changed_paths"], ["CONSTITUTION.md"])
        self.assertEqual(
            set(subject["required_changed_paths"]),
            {
                "governance/evidence/GCL-ORG-2FA-001.json",
                "governance/steward_directives/GI-STEWARD-0002.md",
                "requirements-ci.txt",
                "schemas/constitutional_authority_schedule.schema.json",
                "src/grand_intellect/constitutional_authority.py",
                "tests/test_constitutional_authority.py",
                "tests/test_gi_steward_0002_transition.py",
            },
        )

    def test_campaign_reserves_one_steward_and_admits_distinct_findings(self) -> None:
        self.assertEqual(self.config["finding_binding"], "campaign_contract_v1")
        self.assertEqual(self.config["staffing_mode"], "steward_supervised_agents")
        self.assertEqual(self.config["human_stewards"], ["fyremael"])
        findings = self.config["agent_findings"]
        self.assertEqual(set(findings), {"adversary", "referee"})
        for office, finding in findings.items():
            self.assertEqual(finding["office"], office)
            self.assertEqual(finding["status"], "approved")
            self.assertEqual(
                finding["subject_sha256"],
                "492cfec63cffc27c88381c53e9a079540e42fb2982d795096a19f17c785a3a3c",
            )
            self.assertTrue(finding["record_url"].startswith(
                "https://github.com/grandchallenge/INTELLECT/pull/54#issuecomment-"
            ))
        self.assertNotEqual(
            findings["adversary"]["reviewer_id"],
            findings["referee"]["reviewer_id"],
        )
        self.assertNotEqual(
            findings["adversary"]["session_id"],
            findings["referee"]["session_id"],
        )
        self.assertEqual(
            self.config["receipt"],
            {
                "repository": "grandchallenge/INTELLECT",
                "path_prefix": "governance/reviews",
            },
        )


if __name__ == "__main__":
    unittest.main()
