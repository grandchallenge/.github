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


if __name__ == "__main__":
    unittest.main()
