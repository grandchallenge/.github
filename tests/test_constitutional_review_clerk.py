from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "constitutional_review_clerk",
    ROOT / "scripts" / "constitutional_review_clerk.py",
)
assert SPEC and SPEC.loader
clerk = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = clerk
SPEC.loader.exec_module(clerk)


def reaction(
    reaction_id: int,
    login: str,
    *,
    content: str = "+1",
    user_type: str = "User",
) -> dict[str, object]:
    return {
        "id": reaction_id,
        "content": content,
        "created_at": f"2026-07-29T00:00:{reaction_id:02d}Z",
        "user": {"login": login, "type": user_type},
    }


def finding(
    office: str,
    reviewer_id: str,
    session_id: str,
    subject_sha256: str,
) -> dict[str, object]:
    return {
        "office": office,
        "reviewer_id": reviewer_id,
        "session_id": session_id,
        "subject_sha256": subject_sha256,
        "status": "approved",
        "obligations": [f"{office} obligation"],
        "findings": [],
        "evidence_refs": ["https://example.test/evidence"],
        "residual_uncertainty": ["bootstrap agent correlation"],
        "recorded_at": "2026-07-29T00:00:00Z",
        "record_url": f"https://example.test/{office}",
    }


class ReviewClerkTests(unittest.TestCase):
    def campaign(self) -> dict[str, object]:
        return json.loads(
            (
                ROOT
                / "governance"
                / "review-campaigns"
                / "GI-AMEND-0001.json"
            ).read_text(encoding="utf-8")
        )

    def test_packet_digest_is_stable(self) -> None:
        value = {"b": [2, 1], "a": "same"}
        self.assertEqual(
            clerk.canonical_digest(value),
            clerk.canonical_digest({"a": "same", "b": [2, 1]}),
        )

    def test_gi_amend_campaign_matches_successor_subject_contract(self) -> None:
        config = self.campaign()
        subjects = {item["repository"]: item for item in config["subjects"]}
        self.assertEqual(config["primary_pr"]["pull_request"], 32)
        self.assertEqual(subjects["grandchallenge/INTELLECT"]["pull_request"], 32)
        self.assertEqual(subjects["grandchallenge/gcl-standards"]["pull_request"], 18)
        self.assertEqual(
            set(subjects["grandchallenge/INTELLECT"]["required_changed_paths"]),
            {
                "AMENDMENTS/0001-commentary-and-gcl-ghos.md",
                "governance/constitutional_authority_schedule.json",
                "schemas/constitutional_authority_schedule.schema.json",
                "src/grand_intellect/constitutional_authority.py",
                "tests/test_constitutional_authority.py",
            },
        )
        self.assertEqual(
            set(subjects["grandchallenge/gcl-standards"]["required_changed_paths"]),
            {
                "ci/validate.py",
                "decisions/ADR-0001_GITHUB_CONSTITUTIONAL_OPERATING_SYSTEM.md",
                "programme-adoption/MATH-PROGRAMME.yaml",
                "standards/GCL-GHOS-00.md",
                "tests/test_validate.py",
            },
        )

    def test_successor_packet_invalidates_prior_agent_findings(self) -> None:
        config = self.campaign()
        self.assertIsNone(config["agent_findings"]["adversary"])
        self.assertIsNone(config["agent_findings"]["referee"])
        subject_prs = {
            item["repository"]: item["pull_request"] for item in config["subjects"]
        }
        self.assertNotEqual(subject_prs["grandchallenge/INTELLECT"], 14)
        self.assertNotEqual(subject_prs["grandchallenge/gcl-standards"], 13)

    def test_proposal_author_cannot_supply_agent_review(self) -> None:
        with self.assertRaisesRegex(clerk.ClerkError, "proposal author"):
            clerk.validate_agent_findings(
                {
                    "adversary": finding(
                        "adversary", "author", "session-red", "a" * 64
                    )
                },
                subject_digest="a" * 64,
                proposal_authors={"author"},
            )

    def test_adversary_and_referee_require_distinct_agents(self) -> None:
        with self.assertRaisesRegex(clerk.ClerkError, "distinct agent identities"):
            clerk.validate_agent_findings(
                {
                    "adversary": finding(
                        "adversary", "reviewer", "session-red", "a" * 64
                    ),
                    "referee": finding(
                        "referee", "reviewer", "session-ref", "a" * 64
                    ),
                },
                subject_digest="a" * 64,
                proposal_authors={"author"},
            )

    def test_stale_agent_finding_is_rejected(self) -> None:
        with self.assertRaisesRegex(clerk.ClerkError, "stale"):
            clerk.validate_agent_findings(
                {
                    "adversary": finding(
                        "adversary", "red", "session-red", "b" * 64
                    )
                },
                subject_digest="a" * 64,
                proposal_authors={"author"},
            )

    def test_human_steward_is_the_only_human_signer(self) -> None:
        selected = clerk.select_human_steward(
            reactions=[reaction(1, "other"), reaction(2, "steward")],
            eligible_reviewers={"other", "steward"},
            human_stewards={"steward"},
        )
        assert selected is not None
        self.assertEqual(selected["user"]["login"], "steward")

    def test_non_steward_cannot_authorize(self) -> None:
        selected = clerk.select_human_steward(
            reactions=[reaction(1, "other")],
            eligible_reviewers={"other"},
            human_stewards={"steward"},
        )
        self.assertIsNone(selected)

    def test_receipt_binds_agent_findings_and_steward(self) -> None:
        packet = {
            "campaign_id": "GI-AMEND-0001",
            "staffing_mode": "steward_supervised_agents",
            "human_steward": "steward",
            "proposal_authors": ["author"],
            "packet_sha256": "a" * 64,
            "agent_findings": {
                "adversary": finding(
                    "adversary", "red", "session-red", "d" * 64
                ),
                "referee": finding(
                    "referee", "ref", "session-ref", "d" * 64
                ),
            },
            "subjects": [
                {
                    "repository": "grandchallenge/INTELLECT",
                    "pull_request": 32,
                    "head_sha": "b" * 40,
                }
            ],
        }
        comment = {
            "body": "Human Steward exact attestation",
            "html_url": "https://example.test/steward",
        }
        receipt = clerk.build_receipt(packet, reaction(3, "steward"), comment)
        self.assertEqual(receipt["schema_version"], "1.1.0")
        self.assertEqual(receipt["staffing_mode"], "steward_supervised_agents")
        self.assertEqual(
            {item["office"] for item in receipt["signoffs"]},
            set(clerk.ALL_ROLES),
        )
        self.assertEqual(
            {
                item["reviewer_kind"]
                for item in receipt["signoffs"]
                if item["office"] != "human_steward"
            },
            {"agent"},
        )


if __name__ == "__main__":
    unittest.main()
