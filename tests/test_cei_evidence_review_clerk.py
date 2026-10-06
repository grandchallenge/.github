import unittest

from scripts.cei_evidence_review_clerk import (
    EXPECTED_REVIEWER,
    approve_exact_head,
    exact_approval_exists,
)


class FakeGithub:
    def __init__(self, reviews=None):
        self.reviews = reviews or []
        self.calls = []

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == "GET" and path.endswith("/reviews?per_page=100"):
            return self.reviews
        if method == "POST" and path.endswith("/reviews"):
            return {
                "id": 12345,
                "state": "APPROVED",
                "commit_id": payload["commit_id"],
                "user": {"login": EXPECTED_REVIEWER},
                "body": payload["body"],
            }
        raise AssertionError((method, path, payload))


class CeiEvidenceReviewClerkTests(unittest.TestCase):
    def test_exact_clerk_approval_is_idempotent(self):
        head = "a" * 40
        gh = FakeGithub(
            [
                {
                    "state": "APPROVED",
                    "commit_id": head,
                    "user": {"login": EXPECTED_REVIEWER},
                }
            ]
        )
        self.assertTrue(
            exact_approval_exists(
                gh, "grandchallenge", "MATHSOLVE", 919, head
            )
        )

    def test_stale_or_other_actor_approval_does_not_count(self):
        head = "a" * 40
        gh = FakeGithub(
            [
                {
                    "state": "APPROVED",
                    "commit_id": "b" * 40,
                    "user": {"login": EXPECTED_REVIEWER},
                },
                {
                    "state": "APPROVED",
                    "commit_id": head,
                    "user": {"login": "gcl-release-trust[bot]"},
                },
            ]
        )
        self.assertFalse(
            exact_approval_exists(
                gh, "grandchallenge", "MATHSOLVE", 919, head
            )
        )

    def test_review_binds_exact_head_and_documentary_scope(self):
        head = "c" * 40
        gh = FakeGithub()
        result = approve_exact_head(
            gh,
            "grandchallenge",
            "MATHSOLVE",
            919,
            head,
            "ERDOS-593-R1-IA-001",
        )
        self.assertEqual(result["state"], "APPROVED")
        method, path, payload = gh.calls[-1]
        self.assertEqual(
            (method, path),
            ("POST", "/repos/grandchallenge/MATHSOLVE/pulls/919/reviews"),
        )
        self.assertEqual(payload["commit_id"], head)
        self.assertEqual(payload["event"], "APPROVE")
        self.assertIn("documentary", payload["body"])
        self.assertIn("mathematical status unadjudicated", payload["body"])
        self.assertIn("does not approve mathematical correctness", payload["body"])


if __name__ == "__main__":
    unittest.main()
