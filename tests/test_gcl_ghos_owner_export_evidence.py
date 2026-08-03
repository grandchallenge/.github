from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = (
    ROOT
    / "governance"
    / "settings-readback"
    / "evidence"
    / "GCL-GHOS-OWNER-EXPORT-001.json"
)
DIGEST = EVIDENCE.with_suffix(EVIDENCE.suffix + ".sha256")
EXPECTED_SHA256 = "b60f42d46e6044358d70d0f673f08afbc4e295afba95cd2fe3e9a65d8ab57d7c"
EXPECTED_REPOSITORIES = {
    "grandchallenge/.github",
    "grandchallenge/INTELLECT",
    "grandchallenge/gcl-standards",
    "grandchallenge/MATH-PROGRAMME",
    "grandchallenge/MATHFORGE",
    "grandchallenge/MATHSOLVE",
    "grandchallenge/MATHCERT",
    "grandchallenge/MODULUS",
    "grandchallenge/GLOSS",
    "grandchallenge/QUANTUM-TECHNOLOGIES",
    "grandchallenge/lean-action",
    "grandchallenge/upload-pages-artifact",
}
PLAN_PAYLOAD = {
    "message": "Upgrade to GitHub Team to enable this feature.",
    "documentation_url": (
        "https://docs.github.com/rest/orgs/rules"
        "#get-all-organization-repository-rulesets"
    ),
    "status": "403",
}

SPEC = importlib.util.spec_from_file_location(
    "gcl_ghos_owner_export",
    ROOT / "scripts" / "gcl_ghos_owner_export.py",
)
assert SPEC and SPEC.loader
owner_export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner_export)


def load_evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


class OwnerExportEvidenceAdmissionTests(unittest.TestCase):
    def test_exact_evidence_digest_and_canonical_bytes(self) -> None:
        raw = EVIDENCE.read_bytes()
        value = json.loads(raw)
        self.assertEqual(raw, owner_export.canonical_bytes(value))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(
            DIGEST.read_text(encoding="utf-8"),
            f"{EXPECTED_SHA256}  {EVIDENCE.name}\n",
        )

    def test_protected_contract_accepts_exact_evidence(self) -> None:
        value = load_evidence()
        owner_export.validate_export(value)
        self.assertEqual(value["schema_version"], "1.1.0")
        self.assertEqual(value["recorded_at"], "2026-08-03T13:15:59Z")
        self.assertEqual(
            value["collector"],
            {
                "login": "fyremael",
                "membership_state": "active",
                "organization_role": "admin",
            },
        )
        self.assertEqual(value["repository_count"], 12)
        self.assertEqual(
            {row["repository"] for row in value["repositories"]},
            EXPECTED_REPOSITORIES,
        )
        self.assertTrue(
            all(flag is False for flag in value["claim_boundaries"].values())
        )

    def test_exact_plan_unavailable_record_is_retained(self) -> None:
        rulesets = load_evidence()["organization_settings"]["rulesets"]
        self.assertEqual(rulesets["availability"], "plan_unavailable")
        self.assertEqual(rulesets["details"], [])
        self.assertEqual(rulesets["list"]["status"], 403)
        self.assertEqual(rulesets["list"]["payload"], PLAN_PAYLOAD)

    def test_every_repository_ruleset_list_matches_details(self) -> None:
        for row in load_evidence()["repositories"]:
            repository = row["repository"]
            rulesets = row["rulesets"]
            self.assertEqual(rulesets["availability"], "available")
            self.assertEqual(rulesets["list"]["status"], 200)
            listed = [item["id"] for item in rulesets["list"]["payload"]]
            detailed = [item["payload"]["id"] for item in rulesets["details"]]
            self.assertEqual(len(listed), len(set(listed)), repository)
            self.assertEqual(len(detailed), len(set(detailed)), repository)
            self.assertEqual(set(listed), set(detailed), repository)
            for detail in rulesets["details"]:
                rule_id = detail["payload"]["id"]
                self.assertEqual(detail["status"], 200)
                self.assertEqual(
                    detail["path"],
                    f"/repos/{repository}/rulesets/{rule_id}",
                )

    def test_no_embedded_credentials_or_tokens(self) -> None:
        raw = EVIDENCE.read_text(encoding="utf-8")
        forbidden_patterns = (
            r"github_pat_[A-Za-z0-9_]{20,}",
            r"gh[pousr]_[A-Za-z0-9]{20,}",
            r"Bearer\s+[A-Za-z0-9._-]{12,}",
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        )
        for pattern in forbidden_patterns:
            self.assertIsNone(re.search(pattern, raw, flags=re.IGNORECASE))

        def walk(value: object, path: str = "$") -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    item_path = f"{path}.{key}"
                    if (
                        re.search(
                            r"(token|secret|password|private[_-]?key|authorization)",
                            key,
                            flags=re.IGNORECASE,
                        )
                        and isinstance(item, str)
                        and item.strip()
                    ):
                        self.fail(f"nonempty credential-like field at {item_path}")
                    walk(item, item_path)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, f"{path}[{index}]")

        walk(load_evidence())

    def test_plan_denial_substitution_fails_closed(self) -> None:
        value = load_evidence()
        value["organization_settings"]["rulesets"]["list"]["payload"]["message"] = (
            "Forbidden"
        )
        with self.assertRaises(owner_export.OwnerExportError):
            owner_export.validate_export(value)

    def test_repository_ruleset_detail_omission_fails_closed(self) -> None:
        value = load_evidence()
        value["repositories"][0]["rulesets"]["details"].pop()
        with self.assertRaisesRegex(
            owner_export.OwnerExportError,
            "list/detail identities",
        ):
            owner_export.validate_export(value)

    def test_duplicate_repository_identity_fails_closed(self) -> None:
        value = load_evidence()
        value["repositories"][-1]["repository"] = value["repositories"][0][
            "repository"
        ]
        with self.assertRaisesRegex(owner_export.OwnerExportError, "inventory"):
            owner_export.validate_export(value)

    def test_claim_promotion_fails_closed(self) -> None:
        value = load_evidence()
        value["claim_boundaries"]["organization_wide_conformance"] = True
        with self.assertRaisesRegex(
            owner_export.OwnerExportError,
            "claim boundaries",
        ):
            owner_export.validate_export(value)


if __name__ == "__main__":
    unittest.main()
