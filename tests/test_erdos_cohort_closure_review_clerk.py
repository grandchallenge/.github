import unittest

from scripts.erdos_cohort_closure_review_clerk import (
    EXPECTED_AUTHOR,
    EXPECTED_REVIEWER,
    exact_approval_exists,
    validate_pr_binding,
)


class FakeGithub:
    def __init__(self, reviews=None):
        self.reviews = reviews or []
        self.calls = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if path.endswith("/reviews?per_page=100"):
            return self.reviews
        raise AssertionError((method, path, payload))


class ErdosCohortClosureReviewClerkTests(unittest.TestCase):
    def test_exact_head_clerk_approval_is_idempotent(self):
        gh = FakeGithub(
            [
                {
                    "state": "APPROVED",
                    "commit_id": "a" * 40,
                    "user": {"login": EXPECTED_REVIEWER},
                }
            ]
        )
        self.assertTrue(exact_approval_exists(gh, 77, "a" * 40))
        self.assertFalse(exact_approval_exists(gh, 77, "b" * 40))

    def test_release_trust_exact_head_binding_is_accepted(self):
        pr = {
            "number": 77,
            "state": "open",
            "draft": False,
            "user": {"login": EXPECTED_AUTHOR},
            "base": {"ref": "main"},
            "head": {
                "ref": "lifecycle/erdos-593-cohort-closure-001",
                "sha": "c" * 40,
            },
        }
        number, sha = validate_pr_binding(
            FakeGithub(),
            pr,
            "lifecycle/erdos-593-cohort-closure-001",
            {"head_sha": "c" * 40},
        )
        self.assertEqual(number, 77)
        self.assertEqual(sha, "c" * 40)

    def test_non_release_trust_author_is_rejected(self):
        pr = {
            "number": 77,
            "state": "open",
            "draft": False,
            "user": {"login": "untrusted"},
            "base": {"ref": "main"},
            "head": {
                "ref": "lifecycle/erdos-593-cohort-closure-001",
                "sha": "c" * 40,
            },
        }
        with self.assertRaisesRegex(RuntimeError, "author mismatch"):
            validate_pr_binding(
                FakeGithub(),
                pr,
                "lifecycle/erdos-593-cohort-closure-001",
                {"head_sha": "c" * 40},
            )

    def test_head_drift_is_rejected(self):
        pr = {
            "number": 77,
            "state": "open",
            "draft": False,
            "user": {"login": EXPECTED_AUTHOR},
            "base": {"ref": "main"},
            "head": {
                "ref": "lifecycle/erdos-593-cohort-closure-001",
                "sha": "d" * 40,
            },
        }
        with self.assertRaisesRegex(RuntimeError, "exact head mismatch"):
            validate_pr_binding(
                FakeGithub(),
                pr,
                "lifecycle/erdos-593-cohort-closure-001",
                {"head_sha": "c" * 40},
            )

    def test_load_programme_controller_without_canary3(self):
        import sys
        import types
        from unittest.mock import patch
        from pathlib import Path
        from scripts.erdos_cohort_closure_review_clerk import load_programme_controller

        ci_mod = types.ModuleType("ci")
        fake_intake = types.ModuleType("ci.ns_ci_intake_pr_controller")
        fake_intake.Github = FakeGithub

        fake_postprotect = types.ModuleType("ci.erdos_open_postprotect_controller")
        import re
        fake_postprotect.BRANCH_RE = re.compile(r"^lifecycle/erdos-(\d+)-cohort-closure-001$")
        fake_postprotect.CANARY_CLOSURE_BRANCH = "lifecycle/gcl-e2e-canary-001-cohort-closure"
        fake_postprotect.CANARY_ADVANCE_BRANCH = "lifecycle/gcl-e2e-canary-001-cohort-advance"
        fake_postprotect.CANARY2_CLOSURE_BRANCH = "lifecycle/gcl-e2e-canary-002-cohort-closure"
        fake_postprotect.CANARY2_ADVANCE_BRANCH = "lifecycle/gcl-e2e-canary-002-cohort-advance"
        fake_postprotect.branch_name = lambda x: x
        fake_postprotect.validate_candidate = lambda *args: {}
        fake_postprotect.validate_canary_candidate = lambda *args: {}
        fake_postprotect.validate_canary2_candidate = lambda *args: {}
        # Notice CANARY3 symbols are NOT present in fake_postprotect

        with patch.dict(sys.modules, {
            "ci": ci_mod,
            "ci.ns_ci_intake_pr_controller": fake_intake,
            "ci.erdos_open_postprotect_controller": fake_postprotect,
        }):
            res = load_programme_controller(Path("."))
            (
                github_cls,
                branch_re,
                canary_closure,
                canary_advance,
                canary2_closure,
                canary2_advance,
                canary3_closure,
                canary3_advance,
                bname,
                val_cand,
                val_canary,
                val_canary2,
                val_canary3,
            ) = res
            self.assertEqual(github_cls, FakeGithub)
            self.assertIsNone(canary3_closure)
            self.assertIsNone(canary3_advance)
            self.assertIsNone(val_canary3)

    def test_canary3_unregistered_is_fail_closed(self):
        import os
        import re
        import sys
        import types
        from unittest.mock import patch
        from pathlib import Path
        from scripts.erdos_cohort_closure_review_clerk import run

        class MockGithub(FakeGithub):
            def __init__(self):
                super().__init__()
                self.matching_refs = [
                    {"ref": "refs/heads/lifecycle/gcl-e2e-canary-003-cohort-closure"},
                    {"ref": "refs/heads/lifecycle/gcl-e2e-canary-002-cohort-closure"},
                ]

            def get_optional(self, path):
                return self.matching_refs

            def request(self, method, path, payload=None):
                if "pulls?state=open" in path:
                    return [{
                        "number": 88,
                        "state": "open",
                        "draft": False,
                        "user": {"login": EXPECTED_AUTHOR},
                        "base": {"ref": "main"},
                        "head": {
                            "ref": "lifecycle/gcl-e2e-canary-002-cohort-closure",
                            "sha": "e" * 40,
                        },
                    }]
                if path.endswith("/pulls/88"):
                    return {
                        "number": 88,
                        "state": "open",
                        "draft": False,
                        "user": {"login": EXPECTED_AUTHOR},
                        "base": {"ref": "main"},
                        "head": {
                            "ref": "lifecycle/gcl-e2e-canary-002-cohort-closure",
                            "sha": "e" * 40,
                        },
                    }
                if path.endswith("/reviews?per_page=100"):
                    return [{
                        "state": "APPROVED",
                        "commit_id": "e" * 40,
                        "user": {"login": EXPECTED_REVIEWER},
                    }]
                return super().request(method, path, payload)

        ci_mod = types.ModuleType("ci")
        fake_intake = types.ModuleType("ci.ns_ci_intake_pr_controller")
        fake_intake.Github = lambda token: MockGithub()

        fake_postprotect = types.ModuleType("ci.erdos_open_postprotect_controller")
        fake_postprotect.BRANCH_RE = re.compile(r"^lifecycle/erdos-(\d+)-cohort-closure-001$")
        fake_postprotect.CANARY_CLOSURE_BRANCH = "lifecycle/gcl-e2e-canary-001-cohort-closure"
        fake_postprotect.CANARY_ADVANCE_BRANCH = "lifecycle/gcl-e2e-canary-001-cohort-advance"
        fake_postprotect.CANARY2_CLOSURE_BRANCH = "lifecycle/gcl-e2e-canary-002-cohort-closure"
        fake_postprotect.CANARY2_ADVANCE_BRANCH = "lifecycle/gcl-e2e-canary-002-cohort-advance"
        fake_postprotect.branch_name = lambda x: x
        fake_postprotect.validate_candidate = lambda *args: {}
        fake_postprotect.validate_canary_candidate = lambda *args: {}
        fake_postprotect.validate_canary2_candidate = lambda gh, root, branch: {"head_sha": "e" * 40}
        # CANARY3 symbols missing from postprotect

        with patch.dict(sys.modules, {
            "ci": ci_mod,
            "ci.ns_ci_intake_pr_controller": fake_intake,
            "ci.erdos_open_postprotect_controller": fake_postprotect,
        }), patch.dict(os.environ, {"MATHSOLVE_COUNCIL_CLERK_TOKEN": "dummy_token"}):
            report = run(Path("."), Path("."), apply=False)
            self.assertEqual(len(report["candidates"]), 1)
            self.assertEqual(report["candidates"][0]["problem"], "GCL-E2E-CANARY-002")
            self.assertEqual(report["errors"], [])



if __name__ == "__main__":
    unittest.main()
