from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "governance/credentials/GCL-CREDENTIAL-BOUNDARY-001.json"
SCHEMA_PATH = ROOT / "governance/credentials/credential-boundary.schema.json"


class CredentialBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_inventory_validates(self) -> None:
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.validate(
            self.inventory,
            self.schema,
            format_checker=jsonschema.FormatChecker(),
        )

    def test_inventory_contains_no_secret_values(self) -> None:
        serialized = json.dumps(self.inventory)
        for marker in ("-----BEGIN", "ghp_", "gho_", "github_pat_"):
            self.assertNotIn(marker, serialized)

    def test_installed_app_identities_are_exact(self) -> None:
        apps = {item["slug"]: item for item in self.inventory["apps"]}
        self.assertEqual(
            {name: item["app_id"] for name, item in apps.items()},
            {
                "chatgpt-codex-connector": 1144995,
                "gcl-council-clerk": 4423674,
                "gcl-release-trust": 4423678,
            },
        )
        self.assertTrue(all(item["repository_selection"] == "all" for item in apps.values()))

    def test_human_bound_administrative_credential_is_open_deviation(self) -> None:
        credentials = self.inventory["interactive_credentials"]
        self.assertEqual(len(credentials), 1)
        self.assertEqual(credentials[0]["status"], "open_deviation")
        self.assertEqual(credentials[0]["administrative_settings_path"], "break_glass_only")
        deviations = {item["id"]: item for item in self.inventory["deviations"]}
        self.assertEqual(deviations["GCL-HUMAN-CLI-ADMIN-SCOPE-001"]["status"], "open")

    def test_open_deviations_have_complete_ownership_and_expiry(self) -> None:
        for item in self.inventory["deviations"]:
            if item["status"] == "open":
                for key in (
                    "owner",
                    "expires_at",
                    "compensating_control",
                    "closure_condition",
                    "next_review",
                    "tracking_issue",
                ):
                    self.assertTrue(item[key])

    def test_no_claim_boundary_can_be_enabled(self) -> None:
        broken = copy.deepcopy(self.inventory)
        broken["authority_boundaries"]["organization_wide_conformance"] = True
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(broken, self.schema)

    def test_council_clerk_and_release_administration_are_app_backed(self) -> None:
        clerk = (ROOT / ".github/workflows/constitutional-review-clerk.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("actions/create-github-app-token@", clerk)
        self.assertIn("GCL_COUNCIL_CLERK_APP_ID", clerk)
        self.assertIn("GCL_COUNCIL_CLERK_PRIVATE_KEY", clerk)
        apps = {item["slug"]: item for item in self.inventory["apps"]}
        self.assertEqual(
            apps["gcl-release-trust"]["credential_storage"],
            ["grandchallenge/MATH-PROGRAMME release-trust environment secrets"],
        )
        secret_names = {item["name"] for item in self.inventory["secret_metadata"]}
        self.assertIn("GCL_RELEASE_TRUST_APP_ID", secret_names)
        self.assertIn("GCL_RELEASE_TRUST_PRIVATE_KEY", secret_names)


if __name__ == "__main__":
    unittest.main()
