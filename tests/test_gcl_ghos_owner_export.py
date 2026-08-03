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


def response_map(
    *,
    role: str = "admin",
    organization_rulesets_available: bool = False,
) -> dict[str, tuple[int, object]]:
    values: dict[str, tuple[int, object]] = {
        "/user": (200, {"login": "fyremael"}),
        "/orgs/grandchallenge/memberships/fyremael": (
            200,
            {"state": "active", "role": role},
        ),
        "/orgs/grandchallenge/actions/permissions": (
            200,
            {
                "enabled_repositories": "all",
                "allowed_actions": "selected",
                "sha_pinning_required": True,
            },
        ),
        "/orgs/grandchallenge/actions/permissions/workflow": (
            200,
            {
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
        ),
    }
    if organization_rulesets_available:
        values["/orgs/grandchallenge/rulesets?per_page=100"] = (
            200,
            [{"id": 1001, "name": "organization baseline"}],
        )
        values["/orgs/grandchallenge/rulesets/1001"] = (
            200,
            {"id": 1001, "name": "organization baseline", "enforcement": "active"},
        )
    else:
        values["/orgs/grandchallenge/rulesets?per_page=100"] = (
            403,
            copy.deepcopy(owner_export.ORG_RULESETS_PLAN_DENIAL),
        )

    for index, repo in enumerate(owner_export.REPOSITORIES, start=1):
        prefix = f"/repos/grandchallenge/{repo}"
        rule_id = 2000 + index
        values[prefix] = (
            200,
            {
                "full_name": f"grandchallenge/{repo}",
                "default_branch": "main",
                "permissions": {"admin": True},
            },
        )
        values[f"{prefix}/rulesets?per_page=100&includes_parents=true"] = (
            200,
            [{"id": rule_id, "name": "GCL protected main"}],
        )
        values[f"{prefix}/rulesets/{rule_id}"] = (
            200,
            {"id": rule_id, "name": "GCL protected main", "enforcement": "active"},
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
    def valid_export(self, *, organization_rulesets_available: bool = False):
        return owner_export.collect_export(
            requester(
                response_map(
                    organization_rulesets_available=organization_rulesets_available,
                )
            ),
            recorded_at="2026-08-03T12:00:00Z",
        )

    def test_plan_unavailable_export_validates(self):
        value = self.valid_export()
        owner_export.validate_export(value)
        self.assertEqual(value["schema_version"], "1.1.0")
        self.assertEqual(
            value["organization_settings"]["rulesets"]["availability"],
            "plan_unavailable",
        )
        self.assertEqual(value["repository_count"], 12)
        self.assertFalse(value["claim_boundaries"]["organization_wide_conformance"])

    def test_available_organization_rulesets_validate(self):
        value = self.valid_export(organization_rulesets_available=True)
        self.assertEqual(
            value["organization_settings"]["rulesets"]["availability"],
            "available",
        )
        owner_export.validate_export(value)

    def test_wrong_organization_403_fails_closed(self):
        values = response_map()
        values["/orgs/grandchallenge/rulesets?per_page=100"] = (
            403,
            {"message": "Forbidden"},
        )
        with self.assertRaisesRegex(owner_export.OwnerExportError, "unsupported response"):
            owner_export.collect_export(requester(values))

    def test_malformed_plan_denial_fails_closed(self):
        values = response_map()
        payload = copy.deepcopy(owner_export.ORG_RULESETS_PLAN_DENIAL)
        payload["status"] = 403
        values["/orgs/grandchallenge/rulesets?per_page=100"] = (403, payload)
        with self.assertRaisesRegex(owner_export.OwnerExportError, "unsupported response"):
            owner_export.collect_export(requester(values))

    def test_plan_unavailable_details_must_be_empty(self):
        value = self.valid_export()
        value["organization_settings"]["rulesets"]["details"].append(
            {"path": "/orgs/grandchallenge/rulesets/1", "status": 200, "payload": {"id": 1}}
        )
        with self.assertRaisesRegex(owner_export.OwnerExportError, "must be empty"):
            owner_export.validate_export(value)

    def test_denied_repository_ruleset_list_fails_closed(self):
        values = response_map()
        values[
            "/repos/grandchallenge/.github/rulesets?per_page=100&includes_parents=true"
        ] = (403, {"message": "Forbidden"})
        with self.assertRaisesRegex(owner_export.OwnerExportError, "HTTP 403"):
            owner_export.collect_export(requester(values))

    def test_repository_ruleset_list_must_be_array(self):
        values = response_map()
        values[
            "/repos/grandchallenge/.github/rulesets?per_page=100&includes_parents=true"
        ] = (200, {"id": 1})
        with self.assertRaisesRegex(owner_export.OwnerExportError, "JSON array"):
            owner_export.collect_export(requester(values))

    def test_repository_ruleset_duplicate_ids_fail_closed(self):
        value = self.valid_export()
        rulesets = value["repositories"][0]["rulesets"]
        rulesets["list"]["payload"].append(copy.deepcopy(rulesets["list"]["payload"][0]))
        with self.assertRaisesRegex(owner_export.OwnerExportError, "duplicate rule ids"):
            owner_export.validate_export(value)

    def test_repository_ruleset_list_detail_mismatch_fails_closed(self):
        value = self.valid_export()
        value["repositories"][0]["rulesets"]["details"][0]["payload"]["id"] = 9999
        with self.assertRaisesRegex(owner_export.OwnerExportError, "detail path mismatch|identities"):
            owner_export.validate_export(value)

    def test_repository_ruleset_omission_fails_closed(self):
        value = self.valid_export()
        del value["repositories"][0]["rulesets"]
        with self.assertRaisesRegex(owner_export.OwnerExportError, "rulesets must be an object"):
            owner_export.validate_export(value)

    def test_repository_omission_fails_closed(self):
        value = self.valid_export()
        value["repositories"].pop()
        with self.assertRaisesRegex(owner_export.OwnerExportError, "inventory"):
            owner_export.validate_export(value)

    def test_repository_duplication_fails_closed(self):
        value = self.valid_export()
        value["repositories"][-1] = copy.deepcopy(value["repositories"][0])
        with self.assertRaisesRegex(owner_export.OwnerExportError, "inventory"):
            owner_export.validate_export(value)

    def test_non_owner_collector_fails_closed(self):
        with self.assertRaisesRegex(owner_export.OwnerExportError, "owner/admin"):
            owner_export.collect_export(requester(response_map(role="member")))

    def test_repository_admin_proof_is_required(self):
        value = self.valid_export()
        value["repositories"][0]["metadata"]["payload"]["permissions"]["admin"] = False
        with self.assertRaisesRegex(owner_export.OwnerExportError, "admin access"):
            owner_export.validate_export(value)

    def test_claim_boundary_promotion_fails_closed(self):
        value = self.valid_export()
        value["claim_boundaries"]["organization_wide_conformance"] = True
        with self.assertRaisesRegex(owner_export.OwnerExportError, "claim boundaries"):
            owner_export.validate_export(value)

    def test_digest_is_canonical_and_reproducible(self):
        value = self.valid_export()
        first = owner_export.canonical_bytes(value)
        second = owner_export.canonical_bytes(copy.deepcopy(value))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
