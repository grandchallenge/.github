#!/usr/bin/env python3
"""Collect or validate the GCL-GHOS organization-owner settings export.

The collector is read-only. It requires an organization-owner token through
GH_TOKEN and fails closed when a required endpoint is denied or ambiguous.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

API_ROOT = "https://api.github.com"
API_VERSION = "2026-03-10"
OWNER = "grandchallenge"
CAMPAIGN_ID = "GCL-GHOS-READBACK-GAP-001"
SCHEMA_PATH = "governance/settings-readback/GCL-GHOS-OWNER-EXPORT-001.schema.json"
REPOSITORIES = (
    ".github",
    "INTELLECT",
    "gcl-standards",
    "MATH-PROGRAMME",
    "MATHFORGE",
    "MATHSOLVE",
    "MATHCERT",
    "MODULUS",
    "GLOSS",
    "QUANTUM-TECHNOLOGIES",
    "lean-action",
    "upload-pages-artifact",
)
CLAIM_BOUNDARIES = {
    "organization_wide_conformance": False,
    "mathematical_claim_authorized": False,
    "certification_claim_authorized": False,
    "novelty_claim_authorized": False,
    "deployment_claim_authorized": False,
    "commercial_claim_authorized": False,
}

RequestFn = Callable[[str], tuple[int, Any]]


class OwnerExportError(ValueError):
    """Raised when the owner export is incomplete, ambiguous, or malformed."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_requester(token: str) -> RequestFn:
    if not token:
        raise OwnerExportError("GH_TOKEN is required")

    def request(path: str) -> tuple[int, Any]:
        req = urllib.request.Request(
            API_ROOT + path,
            method="GET",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "gcl-ghos-owner-export-001",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read()
                return response.status, json.loads(data) if data else None
        except urllib.error.HTTPError as exc:
            data = exc.read()
            try:
                payload = json.loads(data) if data else None
            except json.JSONDecodeError:
                payload = data.decode("utf-8", errors="replace")
            return exc.code, payload

    return request


def require_status(name: str, result: tuple[int, Any], allowed: set[int]) -> tuple[int, Any]:
    status, payload = result
    if status not in allowed:
        raise OwnerExportError(f"{name} returned HTTP {status}; allowed={sorted(allowed)}")
    return status, payload


def require_object(name: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise OwnerExportError(f"{name} must return a JSON object")
    return payload


def require_list(name: str, payload: Any) -> list[Any]:
    if not isinstance(payload, list):
        raise OwnerExportError(f"{name} must return a JSON array")
    return payload


def capture_json(request: RequestFn, name: str, path: str) -> dict[str, Any]:
    status, payload = require_status(name, request(path), {200})
    return {"path": path, "status": status, "payload": payload}


def capture_optional(
    request: RequestFn,
    name: str,
    path: str,
    allowed: set[int],
) -> dict[str, Any]:
    status, payload = require_status(name, request(path), allowed)
    return {"path": path, "status": status, "payload": payload}


def collect_export(request: RequestFn, recorded_at: str | None = None) -> dict[str, Any]:
    user = require_object("authenticated user", capture_json(request, "authenticated user", "/user")["payload"])
    login = user.get("login")
    if not isinstance(login, str) or not login:
        raise OwnerExportError("authenticated user login is missing")

    membership_path = f"/orgs/{OWNER}/memberships/{urllib.parse.quote(login)}"
    membership = require_object(
        "organization membership",
        capture_json(request, "organization membership", membership_path)["payload"],
    )
    if membership.get("state") != "active" or membership.get("role") != "admin":
        raise OwnerExportError("collector must be an active organization owner/admin")

    org_actions = capture_json(
        request,
        "organization Actions permissions",
        f"/orgs/{OWNER}/actions/permissions",
    )
    org_workflow = capture_json(
        request,
        "organization workflow permissions",
        f"/orgs/{OWNER}/actions/permissions/workflow",
    )
    org_rulesets_list = capture_json(
        request,
        "organization rulesets",
        f"/orgs/{OWNER}/rulesets?per_page=100",
    )
    org_rulesets = require_list("organization rulesets", org_rulesets_list["payload"])
    org_rule_details: list[dict[str, Any]] = []
    for item in org_rulesets:
        if not isinstance(item, dict) or not isinstance(item.get("id"), int):
            raise OwnerExportError("organization ruleset list contains an invalid item")
        rule_id = item["id"]
        org_rule_details.append(
            capture_json(
                request,
                f"organization ruleset {rule_id}",
                f"/orgs/{OWNER}/rulesets/{rule_id}",
            )
        )

    repositories: list[dict[str, Any]] = []
    for repo in REPOSITORIES:
        quoted_repo = urllib.parse.quote(repo)
        prefix = f"/repos/{OWNER}/{quoted_repo}"
        metadata = capture_json(request, f"{repo} metadata", prefix)
        metadata_payload = require_object(f"{repo} metadata", metadata["payload"])
        permissions = metadata_payload.get("permissions")
        if not isinstance(permissions, dict) or permissions.get("admin") is not True:
            raise OwnerExportError(f"{repo} metadata does not prove repository admin access")
        if metadata_payload.get("default_branch") != "main":
            raise OwnerExportError(f"{repo} default branch is not main")

        repositories.append(
            {
                "repository": f"{OWNER}/{repo}",
                "metadata": metadata,
                "main_protection": capture_optional(
                    request,
                    f"{repo} main protection",
                    f"{prefix}/branches/main/protection",
                    {200, 404},
                ),
                "actions_permissions": capture_json(
                    request,
                    f"{repo} Actions permissions",
                    f"{prefix}/actions/permissions",
                ),
                "actions_workflow_permissions": capture_json(
                    request,
                    f"{repo} workflow permissions",
                    f"{prefix}/actions/permissions/workflow",
                ),
                "vulnerability_alerts": capture_optional(
                    request,
                    f"{repo} vulnerability alerts",
                    f"{prefix}/vulnerability-alerts",
                    {204, 404},
                ),
                "automated_security_fixes": capture_optional(
                    request,
                    f"{repo} Dependabot security updates",
                    f"{prefix}/automated-security-fixes",
                    {200, 404},
                ),
                "code_scanning_default_setup": capture_optional(
                    request,
                    f"{repo} code scanning default setup",
                    f"{prefix}/code-scanning/default-setup",
                    {200, 403, 404},
                ),
            }
        )

    result = {
        "$schema": SCHEMA_PATH,
        "schema_version": "1.0.0",
        "campaign_id": CAMPAIGN_ID,
        "recorded_at": recorded_at or utc_now(),
        "api_version": API_VERSION,
        "organization": OWNER,
        "collector": {
            "login": login,
            "membership_state": membership["state"],
            "organization_role": membership["role"],
        },
        "organization_settings": {
            "actions_permissions": org_actions,
            "actions_workflow_permissions": org_workflow,
            "rulesets": {
                "list": org_rulesets_list,
                "details": org_rule_details,
            },
        },
        "repository_count": len(repositories),
        "repositories": repositories,
        "claim_boundaries": dict(CLAIM_BOUNDARIES),
    }
    validate_export(result)
    return result


def _require_endpoint(
    endpoint: Any,
    *,
    name: str,
    allowed: set[int],
) -> dict[str, Any]:
    if not isinstance(endpoint, dict):
        raise OwnerExportError(f"{name} must be an object")
    if endpoint.get("status") not in allowed:
        raise OwnerExportError(f"{name} has unsupported status {endpoint.get('status')!r}")
    if not isinstance(endpoint.get("path"), str):
        raise OwnerExportError(f"{name} path is missing")
    if "payload" not in endpoint:
        raise OwnerExportError(f"{name} payload field is missing")
    return endpoint


def validate_export(value: dict[str, Any]) -> None:
    if not isinstance(value, dict):
        raise OwnerExportError("owner export must be an object")
    if value.get("$schema") != SCHEMA_PATH:
        raise OwnerExportError("schema identity mismatch")
    if value.get("schema_version") != "1.0.0":
        raise OwnerExportError("schema version mismatch")
    if value.get("campaign_id") != CAMPAIGN_ID:
        raise OwnerExportError("campaign identity mismatch")
    if value.get("organization") != OWNER:
        raise OwnerExportError("organization identity mismatch")
    if value.get("api_version") != API_VERSION:
        raise OwnerExportError("API version mismatch")
    if value.get("claim_boundaries") != CLAIM_BOUNDARIES:
        raise OwnerExportError("claim boundaries must remain closed")

    collector = value.get("collector")
    if not isinstance(collector, dict):
        raise OwnerExportError("collector identity is missing")
    if collector.get("membership_state") != "active" or collector.get("organization_role") != "admin":
        raise OwnerExportError("collector is not an active organization owner/admin")
    if not isinstance(collector.get("login"), str) or not collector["login"]:
        raise OwnerExportError("collector login is missing")

    organization_settings = value.get("organization_settings")
    if not isinstance(organization_settings, dict):
        raise OwnerExportError("organization settings are missing")
    _require_endpoint(
        organization_settings.get("actions_permissions"),
        name="organization Actions permissions",
        allowed={200},
    )
    _require_endpoint(
        organization_settings.get("actions_workflow_permissions"),
        name="organization workflow permissions",
        allowed={200},
    )
    rulesets = organization_settings.get("rulesets")
    if not isinstance(rulesets, dict):
        raise OwnerExportError("organization rulesets are missing")
    listed = _require_endpoint(rulesets.get("list"), name="organization ruleset list", allowed={200})
    if not isinstance(listed["payload"], list):
        raise OwnerExportError("organization ruleset list payload must be an array")
    details = rulesets.get("details")
    if not isinstance(details, list):
        raise OwnerExportError("organization ruleset details must be an array")
    listed_ids = {
        item.get("id")
        for item in listed["payload"]
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }
    detail_ids: set[int] = set()
    for index, endpoint in enumerate(details):
        item = _require_endpoint(endpoint, name=f"organization ruleset detail {index}", allowed={200})
        if not isinstance(item["payload"], dict) or not isinstance(item["payload"].get("id"), int):
            raise OwnerExportError("organization ruleset detail payload is invalid")
        detail_ids.add(item["payload"]["id"])
    if listed_ids != detail_ids:
        raise OwnerExportError("organization ruleset list/detail identities do not match")

    repositories = value.get("repositories")
    if not isinstance(repositories, list):
        raise OwnerExportError("repositories must be an array")
    expected = {f"{OWNER}/{repo}" for repo in REPOSITORIES}
    actual = [row.get("repository") if isinstance(row, dict) else None for row in repositories]
    if value.get("repository_count") != len(REPOSITORIES):
        raise OwnerExportError("repository count mismatch")
    if set(actual) != expected or len(actual) != len(set(actual)):
        raise OwnerExportError("repository inventory drift or duplication")

    for row in repositories:
        if not isinstance(row, dict):
            raise OwnerExportError("repository row must be an object")
        repo = row["repository"]
        metadata = _require_endpoint(row.get("metadata"), name=f"{repo} metadata", allowed={200})
        metadata_payload = metadata["payload"]
        if not isinstance(metadata_payload, dict):
            raise OwnerExportError(f"{repo} metadata payload must be an object")
        permissions = metadata_payload.get("permissions")
        if not isinstance(permissions, dict) or permissions.get("admin") is not True:
            raise OwnerExportError(f"{repo} metadata does not prove admin access")
        if metadata_payload.get("full_name") != repo:
            raise OwnerExportError(f"{repo} metadata identity mismatch")
        if metadata_payload.get("default_branch") != "main":
            raise OwnerExportError(f"{repo} default branch drift")

        _require_endpoint(row.get("main_protection"), name=f"{repo} main protection", allowed={200, 404})
        _require_endpoint(row.get("actions_permissions"), name=f"{repo} Actions permissions", allowed={200})
        _require_endpoint(
            row.get("actions_workflow_permissions"),
            name=f"{repo} workflow permissions",
            allowed={200},
        )
        _require_endpoint(
            row.get("vulnerability_alerts"),
            name=f"{repo} vulnerability alerts",
            allowed={204, 404},
        )
        _require_endpoint(
            row.get("automated_security_fixes"),
            name=f"{repo} Dependabot security updates",
            allowed={200, 404},
        )
        _require_endpoint(
            row.get("code_scanning_default_setup"),
            name=f"{repo} code scanning default setup",
            allowed={200, 403, 404},
        )


def canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_export(value: dict[str, Any], output: Path, digest_output: Path | None) -> str:
    data = canonical_bytes(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    target = digest_output or output.with_suffix(output.suffix + ".sha256")
    target.write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("GCL-GHOS-OWNER-EXPORT-001.json"),
        help="path for the canonical JSON export",
    )
    parser.add_argument("--digest-output", type=Path)
    parser.add_argument("--validate", type=Path, help="validate an existing export instead of collecting")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.validate:
            value = json.loads(args.validate.read_text(encoding="utf-8"))
            validate_export(value)
            digest = hashlib.sha256(canonical_bytes(value)).hexdigest()
            print(json.dumps({"valid": True, "sha256": digest}, sort_keys=True))
            return 0

        request = make_requester(os.environ.get("GH_TOKEN", ""))
        value = collect_export(request)
        digest = write_export(value, args.output, args.digest_output)
        print(json.dumps({"output": str(args.output), "sha256": digest}, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, OwnerExportError) as exc:
        print(f"owner export failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
