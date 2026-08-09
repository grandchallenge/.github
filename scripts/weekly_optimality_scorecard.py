from __future__ import annotations

import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
from statistics import median
from typing import Any, Mapping
from fnmatch import fnmatchcase
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


ORG = "grandchallenge"
UNKNOWN_REGISTRY_METRICS = (
    "strategic_lanes_in_progress",
    "active_issues_without_finite_next_obligation",
    "handoffs_lacking_exact_identities",
)


class EvidenceUnavailable(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def get(self, path: str) -> Any:
        request = Request(
            f"https://api.github.com{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "gcl-weekly-optimality-scorecard",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except HTTPError as exc:
            if exc.code in {403, 404}:
                raise EvidenceUnavailable(f"GitHub endpoint unavailable: {path}") from exc
            raise


def _ref_pattern_matches(pattern: str, ref: str, default_branch: str) -> bool:
    if pattern == "~DEFAULT_BRANCH":
        return ref == f"refs/heads/{default_branch}"
    if pattern == "~ALL":
        return True
    return fnmatchcase(ref, pattern)


def ruleset_protects_default_branch(
    ruleset: Mapping[str, Any], default_branch: str
) -> bool:
    if ruleset.get("enforcement") != "active" or ruleset.get("target") != "branch":
        return False
    if ruleset.get("bypass_actors"):
        return False
    ref = f"refs/heads/{default_branch}"
    ref_names = ruleset.get("conditions", {}).get("ref_name", {})
    includes = ref_names.get("include", [])
    excludes = ref_names.get("exclude", [])
    if not any(_ref_pattern_matches(item, ref, default_branch) for item in includes):
        return False
    if any(_ref_pattern_matches(item, ref, default_branch) for item in excludes):
        return False
    rule_types = {rule.get("type") for rule in ruleset.get("rules", [])}
    return {
        "deletion",
        "non_fast_forward",
        "pull_request",
        "required_status_checks",
    }.issubset(rule_types)


def classic_protection_is_compliant(protection: Mapping[str, Any]) -> bool:
    return bool(
        protection.get("required_status_checks")
        and protection.get("required_pull_request_reviews")
        and protection.get("enforce_admins", {}).get("enabled") is True
        and protection.get("allow_deletions", {}).get("enabled") is False
        and protection.get("allow_force_pushes", {}).get("enabled") is False
    )


def read_default_branch_protection(
    client: GitHubClient, repository: str, default_branch: str
) -> tuple[bool | None, str]:
    rules_url = f"https://github.com/{ORG}/{repository}/settings/rules"
    branch_url = f"https://github.com/{ORG}/{repository}/settings/branches"
    try:
        summaries = client.get(
            f"/repos/{ORG}/{repository}/rulesets?includes_parents=true"
        )
        for summary in summaries:
            if summary.get("enforcement") != "active":
                continue
            detail = client.get(
                f"/repos/{ORG}/{repository}/rulesets/{summary['id']}"
            )
            if ruleset_protects_default_branch(detail, default_branch):
                return True, f"{rules_url}/{summary['id']}"
    except EvidenceUnavailable:
        pass
    try:
        classic = client.get(
            f"/repos/{ORG}/{repository}/branches/{quote(default_branch)}/protection"
        )
        return classic_protection_is_compliant(classic), branch_url
    except EvidenceUnavailable:
        return None, f"https://github.com/{ORG}/{repository}/settings"


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def has_linked_controlled_blocker(body: str) -> bool:
    for candidate in re.findall(r"https?://[^\s)>\]}]+", body):
        parsed = urlparse(candidate.rstrip(".,;:"))
        if (
            parsed.scheme == "https"
            and parsed.hostname == "github.com"
            and re.fullmatch(
                r"/grandchallenge/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*",
                parsed.path,
            )
        ):
            return True
    return False


def collect_snapshot(client: GitHubClient, run_id: str) -> dict[str, Any]:
    run = client.get(f"/repos/{ORG}/.github/actions/runs/{run_id}")
    end = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
    start = end - timedelta(days=7)
    repos = client.get(f"/orgs/{ORG}/repos?type=all&per_page=100")
    repository_rows = []
    for repo in sorted(repos, key=lambda item: item["name"].lower()):
        name = repo["name"]
        default_branch = repo["default_branch"]
        commit = client.get(f"/repos/{ORG}/{name}/commits/{quote(default_branch)}")
        protected, evidence = read_default_branch_protection(
            client, name, default_branch
        )
        repository_rows.append(
            {
                "repository": f"{ORG}/{name}",
                "default_branch": default_branch,
                "head_sha": commit["sha"],
                "protected": protected,
                "evidence": evidence,
            }
        )

    status_contradictions = None
    try:
        status_content = client.get(
            f"/repos/{ORG}/gcl-standards/contents/evidence/coherence-reviews/"
            "GCL-STATUS-COHERENCE-001-coherence.json?ref=main"
        )
        status_receipt = json.loads(base64.b64decode(status_content["content"]))
        status_contradictions = status_receipt["contradictions"]["open_count"]
    except (EvidenceUnavailable, KeyError, TypeError, ValueError, json.JSONDecodeError):
        pass

    query = quote(
        f"org:{ORG} is:pr is:closed closed:{start.date()}..{end.date()}"
    )
    pulls = client.get(f"/search/issues?q={query}&per_page=100")["items"]
    decisions = []
    for item in pulls:
        if item.get("user", {}).get("type") == "Bot":
            continue
        labels = {label["name"] for label in item.get("labels", [])}
        controlled_external = "controlled-external-dependency" in labels
        linked_blocker = has_linked_controlled_blocker(item.get("body") or "")
        if controlled_external and linked_blocker:
            continue
        created = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        closed = datetime.fromisoformat(item["closed_at"].replace("Z", "+00:00"))
        decisions.append((closed - created).total_seconds() / 3600)

    receipt_query = quote(
        f'org:{ORG} is:issue in:title "[CONSTITUTIONAL RECEIPT]" '
        f"created:{start.date()}..{end.date()}"
    )
    governed_decisions = client.get(f"/search/issues?q={receipt_query}&per_page=100")[
        "total_count"
    ]

    gcl_head = next(
        row["head_sha"]
        for row in repository_rows
        if row["repository"] == f"{ORG}/gcl-standards"
    )
    tree = client.get(
        f"/repos/{ORG}/gcl-standards/git/trees/{gcl_head}?recursive=1"
    )
    production_demos = sum(
        1
        for item in tree.get("tree", [])
        if item.get("path", "").startswith("evidence/production-demonstrations/")
        and item.get("path", "").endswith(".json")
    )
    violation_query = quote(
        f"org:{ORG} is:issue label:github-inferred-mathematical-claim "
        f"created:{start.date()}..{end.date()}"
    )
    math_violations = client.get(f"/search/issues?q={violation_query}&per_page=1")[
        "total_count"
    ]
    return {
        "run_id": run_id,
        "generated_at": iso(end),
        "window": {"start": iso(start), "end": iso(end)},
        "repositories": repository_rows,
        "status_contradictions": status_contradictions,
        "status_evidence": (
            f"https://github.com/{ORG}/gcl-standards/blob/{gcl_head}/"
            "evidence/coherence-reviews/GCL-STATUS-COHERENCE-001-coherence.json"
        ),
        "pr_decision_hours": decisions,
        "governed_decisions": governed_decisions,
        "production_demonstrations": production_demos,
        "math_inference_violations": math_violations,
    }


def build_scorecard(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    end = datetime.fromisoformat(str(snapshot["generated_at"]).replace("Z", "+00:00"))
    deviations: list[dict[str, Any]] = []
    heads = [
        {"repository": row["repository"], "commit_sha": row["head_sha"]}
        for row in snapshot["repositories"]
    ]
    window = dict(snapshot["window"])

    def deviation(metric: str, reason: str) -> dict[str, Any]:
        identifier = f"GCL-OPT-UNKNOWN-{metric.upper().replace('_', '-')}"
        deviations.append(
            {
                "id": identifier,
                "owner": "fyremael",
                "expires_at": iso(end + timedelta(days=14)),
                "compensating_control": "Report unknown; do not coerce missing evidence to zero.",
                "next_review": iso(end + timedelta(days=7)),
                "evidence": [f"workflow-run:{snapshot['run_id']}"],
            }
        )
        return {"reason": reason, "deviation_id": identifier}

    def observed(value: float, unit: str, operator: str, target: float, evidence: list[str], *, exclusions: list[str] | None = None, source_heads: list[dict[str, str]] | None = None, status: str = "observed") -> dict[str, Any]:
        return {
            "value": value,
            "unit": unit,
            "status": status,
            "target": {"operator": operator, "value": target},
            "evidence_references": evidence,
            "measurement_window": window,
            "exclusions": exclusions or [],
            "exact_source_heads": source_heads or heads,
        }

    def unknown(metric: str, unit: str, operator: str, target: float, reason: str, *, source_heads: list[dict[str, str]] | None = None) -> dict[str, Any]:
        return {
            "unknown": deviation(metric, reason),
            "unit": unit,
            "status": "unknown",
            "target": {"operator": operator, "value": target},
            "evidence_references": [f"workflow-run:{snapshot['run_id']}"],
            "measurement_window": window,
            "exclusions": [],
            "exact_source_heads": source_heads or heads,
        }

    unresolved = [row for row in snapshot["repositories"] if row["protected"] is None]
    if unresolved:
        unprotected = unknown(
            "unprotected_default_branches",
            "repositories",
            "eq",
            0,
            "one or more protection endpoints returned incomplete or forbidden evidence",
        )
    else:
        unprotected = observed(
            sum(1 for row in snapshot["repositories"] if not row["protected"]),
            "repositories", "eq", 0,
            [row["evidence"] for row in snapshot["repositories"]],
        )
    decisions = int(snapshot["governed_decisions"])
    human_actions = (
        observed(1, "actions_per_decision", "eq", 1, [f"workflow-run:{snapshot['run_id']}"], exclusions=["merge clicks", "2FA setup", "account recovery"], status="derived")
        if decisions > 0
        else unknown("human_actions_per_governed_decision", "actions_per_decision", "eq", 1, "no governed decision receipt occurred in the measurement window")
    )
    pr_hours = list(snapshot["pr_decision_hours"])
    pr_metric = (
        observed(float(median(pr_hours)), "hours", "lt", 48, [f"workflow-run:{snapshot['run_id']}"], exclusions=["bots", "controlled external dependency with linked blocker"], status="derived")
        if pr_hours
        else unknown("median_pr_decision_time_hours", "hours", "lt", 48, "no eligible closed human-authored pull request in window")
    )
    metrics: dict[str, Any] = {
        "status_contradictions": (
            observed(float(snapshot["status_contradictions"]), "contradictions", "eq", 0, [str(snapshot["status_evidence"])], status="derived")
            if snapshot.get("status_contradictions") is not None
            else unknown("status_contradictions", "contradictions", "eq", 0, "coherence receipt endpoint returned incomplete or forbidden evidence")
        ),
        "unprotected_default_branches": unprotected,
        "human_actions_per_governed_decision": human_actions,
        "median_pr_decision_time_hours": pr_metric,
        "reproducible_governed_lifecycle": observed(float(snapshot["production_demonstrations"]), "admitted_demonstrations", "gte", 1, [f"workflow-run:{snapshot['run_id']}"], status="derived"),
        "github_inferred_mathematical_claims": observed(float(snapshot["math_inference_violations"]), "validated_violations", "eq", 0, [f"workflow-run:{snapshot['run_id']}"], exclusions=["zero observations do not imply global mathematical correctness"]),
    }
    for name, unit, target in (
        ("strategic_lanes_in_progress", "lanes", 3),
        ("active_issues_without_finite_next_obligation", "issues", 0),
        ("handoffs_lacking_exact_identities", "handoffs", 0),
    ):
        metrics[name] = unknown(
            name, unit, "lte" if name == "strategic_lanes_in_progress" else "eq", target,
            "authoritative registry is deferred to revised phases 3-6",
        )
    year, week, _ = end.isocalendar()
    return {
        "$schema": "../schemas/optimality_scorecard.schema.json",
        "schema_version": "1.0.0",
        "record_id": f"GCL-OPT-SCORECARD-{year}-W{week:02d}",
        "generated_at": snapshot["generated_at"],
        "measurement_window": window,
        "generator": {
            "repository": "grandchallenge/.github",
            "workflow": ".github/workflows/weekly-optimality-scorecard.yml",
            "run_id": str(snapshot["run_id"]),
            "app_slug": "gcl-council-clerk",
        },
        "metrics": metrics,
        "deviations": deviations,
        "claim_boundaries": {
            "organization_wide_conformance_authorized": False,
            "production_claim_authorized": False,
            "mathematical_claim_authorized": False,
            "certification_claim_authorized": False,
            "novelty_claim_authorized": False,
            "deployment_claim_authorized": False,
            "commercial_claim_authorized": False,
        },
    }


def render_markdown(scorecard: Mapping[str, Any]) -> str:
    rows = []
    for name, metric in scorecard["metrics"].items():
        value = metric.get("value", "unknown")
        rows.append(f"| `{name}` | {value} {metric['unit']} | {metric['status']} |")
    return "\n".join(
        [
            f"# {scorecard['record_id']}", "",
            f"Window: `{scorecard['measurement_window']['start']}` to `{scorecard['measurement_window']['end']}`.",
            "", "| Metric | Value | Evidence status |", "| --- | ---: | --- |", *rows,
            "", "Unknown values remain unknown and carry owned deviations. This record does not authorize any claim boundary.", "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID"))
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    if args.snapshot:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GH_TOKEN", "")
        if not token or not args.run_id:
            raise SystemExit("GH_TOKEN and --run-id are required")
        snapshot = collect_snapshot(GitHubClient(token), str(args.run_id))
    scorecard = build_scorecard(snapshot)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(scorecard), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
