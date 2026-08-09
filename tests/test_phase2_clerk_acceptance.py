from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "constitutional_review_clerk_phase2_acceptance",
    ROOT / "scripts" / "constitutional_review_clerk.py",
)
assert SPEC and SPEC.loader
clerk = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = clerk
SPEC.loader.exec_module(clerk)


def subject(
    *,
    head: str = "a" * 40,
    base: str = "b" * 40,
    checks_ready: bool = True,
    checks: tuple[tuple[str, str], ...] = (("required", "success"),),
) -> object:
    return clerk.Subject(
        repository="grandchallenge/example",
        pull_request=1,
        url="https://example.test/grandchallenge/example/pull/1",
        head_sha=head,
        base_sha=base,
        author="proposal-author",
        draft=False,
        mergeable_state="clean",
        changed_paths=("governance/example.json",),
        checks=checks,
        checks_ready=checks_ready,
        boundary_checks=(("changed:governance/example.json", True),),
    )


def finding(
    office: str,
    reviewer: str,
    session: str,
    digest: str,
) -> dict[str, object]:
    return {
        "office": office,
        "reviewer_id": reviewer,
        "session_id": session,
        "subject_sha256": digest,
        "status": "approved",
        "obligations": [f"preserve {office} exact-subject binding"],
        "findings": ["fixture finding"],
        "evidence_refs": ["https://example.test/evidence"],
        "residual_uncertainty": [],
        "recorded_at": "2026-08-09T07:20:00Z",
        "record_url": f"https://example.test/{office}",
    }


def config() -> dict[str, object]:
    return {
        "campaign_id": "GCL-PHASE2-CLERK-ACCEPTANCE-FIXTURE",
        "constitutional_source": {
            "repository": "grandchallenge/INTELLECT",
            "path": "governance/constitutional_authority_schedule.json",
        },
        "staffing_mode": "steward_supervised_agents",
        "human_stewards": ["fyremael"],
        "agent_findings": {},
    }


class Phase2ClerkAcceptanceTests(unittest.TestCase):
    def packet_with_findings(self, item: object) -> dict[str, object]:
        cfg = config()
        baseline = clerk.build_packet(cfg, [item])
        digest = baseline["subject_sha256"]
        cfg["agent_findings"] = {
            "adversary": finding(
                "adversary", "phase2-adversary", "phase2-session-a", digest
            ),
            "referee": finding(
                "referee", "phase2-referee", "phase2-session-r", digest
            ),
        }
        return clerk.build_packet(cfg, [item])

    def test_three_way_head_drift_invalidates_agent_and_steward_packet(self) -> None:
        original = subject(head="a" * 40, base="b" * 40)
        cfg = config()
        null_packet = clerk.build_packet(cfg, [original])
        digest = null_packet["subject_sha256"]
        cfg["agent_findings"] = {
            "adversary": finding(
                "adversary", "phase2-adversary", "phase2-session-a", digest
            ),
            "referee": finding(
                "referee", "phase2-referee", "phase2-session-r", digest
            ),
        }
        reviewed_packet = clerk.build_packet(cfg, [original])
        self.assertTrue(reviewed_packet["ready_for_steward_review"])
        old_steward_marker = clerk.marker(
            reviewed_packet["campaign_id"],
            reviewed_packet["packet_sha256"],
            "human_steward",
        )

        moved_head = subject(head="c" * 40, base="b" * 40)
        with self.assertRaisesRegex(clerk.ClerkError, "finding is stale"):
            clerk.build_packet(cfg, [moved_head])

        moved_base = subject(head="a" * 40, base="d" * 40)
        with self.assertRaisesRegex(clerk.ClerkError, "finding is stale"):
            clerk.build_packet(cfg, [moved_base])

        fresh_cfg = config()
        moved_null = clerk.build_packet(fresh_cfg, [moved_head])
        fresh_digest = moved_null["subject_sha256"]
        fresh_cfg["agent_findings"] = {
            "adversary": finding(
                "adversary", "phase2-adversary-2", "phase2-session-a-2", fresh_digest
            ),
            "referee": finding(
                "referee", "phase2-referee-2", "phase2-session-r-2", fresh_digest
            ),
        }
        fresh_packet = clerk.build_packet(fresh_cfg, [moved_head])
        new_steward_marker = clerk.marker(
            fresh_packet["campaign_id"],
            fresh_packet["packet_sha256"],
            "human_steward",
        )
        self.assertNotEqual(reviewed_packet["subject_sha256"], fresh_packet["subject_sha256"])
        self.assertNotEqual(reviewed_packet["packet_sha256"], fresh_packet["packet_sha256"])
        self.assertNotEqual(old_steward_marker, new_steward_marker)

    def test_duplicate_reviewer_or_session_is_rejected(self) -> None:
        item = subject()
        baseline = clerk.build_packet(config(), [item])
        digest = baseline["subject_sha256"]

        with self.subTest("duplicate reviewer"):
            with self.assertRaisesRegex(clerk.ClerkError, "distinct agent identities"):
                clerk.validate_agent_findings(
                    {
                        "adversary": finding(
                            "adversary", "same-agent", "session-a", digest
                        ),
                        "referee": finding(
                            "referee", "same-agent", "session-r", digest
                        ),
                    },
                    subject_digest=digest,
                    proposal_authors={"proposal-author"},
                )

        with self.subTest("duplicate session"):
            with self.assertRaisesRegex(clerk.ClerkError, "distinct agent sessions"):
                clerk.validate_agent_findings(
                    {
                        "adversary": finding(
                            "adversary", "agent-a", "same-session", digest
                        ),
                        "referee": finding(
                            "referee", "agent-r", "same-session", digest
                        ),
                    },
                    subject_digest=digest,
                    proposal_authors={"proposal-author"},
                )

    def test_unauthorized_steward_reaction_is_rejected(self) -> None:
        reactions = [
            {
                "id": 1,
                "content": "+1",
                "created_at": "2026-08-09T07:20:00Z",
                "user": {"login": "jimsteeg", "type": "User"},
            },
            {
                "id": 2,
                "content": "+1",
                "created_at": "2026-08-09T07:20:01Z",
                "user": {"login": "gcl-council-clerk[bot]", "type": "Bot"},
            },
        ]
        selected = clerk.select_human_steward(
            reactions=reactions,
            eligible_reviewers={"fyremael", "jimsteeg", "gcl-council-clerk[bot]"},
            human_stewards={"fyremael"},
        )
        self.assertIsNone(selected)

    def test_incomplete_or_failed_checks_keep_packet_not_ready(self) -> None:
        fixtures = (
            subject(checks_ready=False, checks=()),
            subject(
                checks_ready=False,
                checks=(("required", "failure"),),
            ),
            clerk.Subject(
                repository="grandchallenge/example",
                pull_request=1,
                url="https://example.test/grandchallenge/example/pull/1",
                head_sha="a" * 40,
                base_sha="b" * 40,
                author="proposal-author",
                draft=False,
                mergeable_state="clean",
                changed_paths=("governance/example.json",),
                checks=(("required", "success"),),
                checks_ready=True,
                boundary_checks=(("required-boundary", False),),
            ),
        )
        for item in fixtures:
            with self.subTest(checks=item.checks, boundaries=item.boundary_checks):
                packet = self.packet_with_findings(item)
                self.assertFalse(packet["ready_for_steward_review"])
                self.assertFalse(packet["ready_for_human_review"])


if __name__ == "__main__":
    unittest.main()
