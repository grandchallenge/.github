from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "gcl_ghos_owner_export",
    ROOT / "scripts" / "gcl_ghos_owner_export.py",
)
assert SPEC and SPEC.loader
owner_export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner_export)


def response_map(*, role: str = "admin") -> dict[str, tuple[int, object]]:
    values: dict[str, tuple[int, object]] = {
        "/user": (200, {"login": "fyremael"}),
        "/orgs/grandchallenge/memberships/fyremael": (
            200,
            {"state": "active", "role": role},
        ),
        "/orgs/grandchallenge/actions/permissions": (
            200,
            {"enabled_repositories": "all", "allowed_actions": "selected"},
        ),
        "/orgs/grandchallenge/actions/permissions/workflow": (
            200,
            {
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
        ),
        "/orgs/grandchallenge/rulesets?per_page=100": (
            200,
            [{"id": 1001, "name": "organization baseline"}],
        ),
        "/orgs/grandchallenge/rulesets/1001": (
            200,
            {"id": 1001, "name": "organization baseline", "enforcement": "active"},
        ),
    }
    for repo in owner_export.REPOSITORIES:
        prefix = f"/repos/grandchallenge/{repo}"
        values[prefix] = (
            200,
            {
                "full_name": f"grandchallenge/{repo}",
                "default_branch": "main",
                "permissions": {"admin": True},
            },
        )
        values[f"{prefix}/branches/main/protection"] = (404, {"message": "Not Found"})
        values[f"{prefix}/actions/permissions"] = (
            200,
            {"enabled": True, "allowed_actions": "selected"},
        )
        values[f"{prefix}/actions/permissions/workflow"] = (
            200,
            {
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
        )
        values[f"{prefix}/vulnerability-alerts"] = (204, None)
        values[f"{prefix}/automated-security-fixes"] = (
            200,
            {"enabled": True, "paused": False},
        )
        values[f"{prefix}/code-scanning/default-setup"] = (
            403,
            {"message": "GitHub Advanced Security is not enabled"},
        )
    return values


def requester(values: dict[str, tuple[int, object]]):
    def request(path: str):
        if path not in values:
            raise AssertionError(f"unexpected path: {path}")
        return values[path]
    return request


class OwnerExportTests(unittest.TestCase):
    def valid_export(self):
        return owner_export.collect_export(
            requester(response_map()),
            recorded_at="2026-08-03T12:00:00Z",
        )

    def test_complete_owner_export_validates(self):
        value = self.valid_export()
        owner_export.validate_export(value)
        self.assertEqual(value["repository_count"], 12)
        self.assertEqual(value["collector"]["organization_role"], "admin")
        self.assertFalse(value["claim_boundaries"]["organization_wide_conformance"])

    def test_denied_organization_endpoint_fails_closed(self):
        values = response_map()
        values["/orgs/grandchallenge/actions/permissions"] = (403, {"message": "Forbidden"})
        with self.assertRaisesRegex(owner_export.OwnerExportError, "HTTP 403"):
            owner_export.collect_export(requester(values))

    def test_non_owner_collector_fails_closed(self):
        with self.assertRaisesRegex(owner_export.OwnerExportError, "owner/admin"):
            owner_export.collect_export(requester(response_map(role="member")))

    def test_repository_omission_fails_closed(self):
        value = self.valid_export()
        value["repositories"].pop()
        with self.assertRaisesRegex(owner_export.OwnerExportError, "inventory"):
            owner_export.validate_export(value)

    def test_ambiguous_vulnerability_status_fails_closed(self):
        value = self.valid_export()
        value["repositories"][0]["vulnerability_alerts"]["status"] = 403
        with self.assertRaisesRegex(owner_export.OwnerExportError, "unsupported status"):
            owner_export.validate_export(value)

    def test_code_scanning_ghas_response_is_retained(self):
        value = self.valid_export()
        endpoint = value["repositories"][0]["code_scanning_default_setup"]
        self.assertEqual(endpoint["status"], 403)
        owner_export.validate_export(value)

    def test_ruleset_list_detail_mismatch_fails_closed(self):
        value = self.valid_export()
        value["organization_settings"]["rulesets"]["details"][0]["payload"]["id"] = 9999
        with self.assertRaisesRegex(owner_export.OwnerExportError, "identities"):
            owner_export.validate_export(value)

    def test_claim_boundary_promotion_fails_closed(self):
        value = self.valid_export()
        value["claim_boundaries"]["organization_wide_conformance"] = True
        with self.assertRaisesRegex(owner_export.OwnerExportError, "claim boundaries"):
            owner_export.validate_export(value)

    def test_repository_admin_proof_is_required(self):
        value = self.valid_export()
        value["repositories"][0]["metadata"]["payload"]["permissions"]["admin"] = False
        with self.assertRaisesRegex(owner_export.OwnerExportError, "admin access"):
            owner_export.validate_export(value)

    def test_digest_is_canonical_and_reproducible(self):
        value = self.valid_export()
        first = owner_export.canonical_bytes(value)
        second = owner_export.canonical_bytes(copy.deepcopy(value))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
