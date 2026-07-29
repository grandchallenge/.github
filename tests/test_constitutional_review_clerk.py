from __future__ import annotations

import importlib.util
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


class ReviewClerkTests(unittest.TestCase):
    def test_packet_digest_is_stable(self) -> None:
        value = {"b": [2, 1], "a": "same"}
        self.assertEqual(
            clerk.canonical_digest(value),
            clerk.canonical_digest({"a": "same", "b": [2, 1]}),
        )

    def test_author_cannot_supply_independent_review(self) -> None:
        selected, missing = clerk.select_signers(
            role_reactions={
                "adversary": [reaction(1, "author")],
                "referee": [reaction(2, "ref")],
                "human_steward": [reaction(3, "steward")],
            },
            authors={"author"},
            eligible_independent={"author", "ref", "steward"},
            human_stewards={"steward"},
        )
        self.assertNotIn("adversary", selected)
        self.assertIn("adversary", missing)

    def test_adversary_and_referee_must_be_distinct(self) -> None:
        selected, missing = clerk.select_signers(
            role_reactions={
                "adversary": [reaction(1, "reviewer")],
                "referee": [reaction(2, "reviewer")],
                "human_steward": [reaction(3, "steward")],
            },
            authors={"author"},
            eligible_independent={"reviewer", "steward"},
            human_stewards={"steward"},
        )
        self.assertEqual(selected["adversary"]["user"]["login"], "reviewer")
        self.assertNotIn("referee", selected)
        self.assertIn("referee", missing)

    def test_three_role_attestations_complete(self) -> None:
        selected, missing = clerk.select_signers(
            role_reactions={
                "adversary": [reaction(1, "red")],
                "referee": [reaction(2, "ref")],
                "human_steward": [reaction(3, "steward")],
            },
            authors={"author"},
            eligible_independent={"red", "ref", "steward"},
            human_stewards={"steward"},
        )
        self.assertFalse(missing)
        self.assertEqual(set(selected), set(clerk.ALL_ROLES))

    def test_non_steward_cannot_authorize(self) -> None:
        selected, missing = clerk.select_signers(
            role_reactions={
                "adversary": [reaction(1, "red")],
                "referee": [reaction(2, "ref")],
                "human_steward": [reaction(3, "other")],
            },
            authors={"author"},
            eligible_independent={"red", "ref", "other"},
            human_stewards={"steward"},
        )
        self.assertNotIn("human_steward", selected)
        self.assertIn("human_steward", missing)

    def test_receipt_binds_packet_subjects_and_attestations(self) -> None:
        packet = {
            "campaign_id": "GI-AMEND-0001",
            "packet_sha256": "a" * 64,
            "subjects": [
                {
                    "repository": "grandchallenge/INTELLECT",
                    "pull_request": 13,
                    "head_sha": "b" * 40,
                }
            ],
        }
        signers = {
            "adversary": reaction(1, "red"),
            "referee": reaction(2, "ref"),
            "human_steward": reaction(3, "steward"),
        }
        comments = {
            role: {
                "body": f"{role} exact attestation",
                "html_url": f"https://example.test/{role}",
            }
            for role in clerk.ALL_ROLES
        }
        receipt = clerk.build_receipt(packet, signers, comments)
        self.assertEqual(receipt["packet_sha256"], "a" * 64)
        self.assertEqual(receipt["subjects"][0]["head_sha"], "b" * 40)
        self.assertEqual(
            {item["office"] for item in receipt["signoffs"]},
            set(clerk.ALL_ROLES),
        )


if __name__ == "__main__":
    unittest.main()
