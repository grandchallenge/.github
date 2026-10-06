#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

EXPECTED_REVIEWER = "gcl-council-clerk[bot]"


def load_programme_controller(programme_root: Path):
    sys.path.insert(0, str(programme_root))
    from ci.ns_ci_intake_pr_controller import (  # type: ignore
        ControllerError,
        Github,
        find_open_pr,
        list_intake_branches,
        validate_candidate,
    )
    from ci.external_intake_evidence_admission import validate_pr_binding  # type: ignore

    return (
        ControllerError,
        Github,
        find_open_pr,
        list_intake_branches,
        validate_candidate,
        validate_pr_binding,
    )


def exact_approval_exists(
    gh: Any,
    owner: str,
    repo: str,
    pr_number: int,
    head_sha: str,
) -> bool:
    reviews = gh.request(
        "GET", f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews?per_page=100"
    )
    if not isinstance(reviews, list):
        raise RuntimeError("pull-request review list response malformed")
    for review in reviews:
        if not isinstance(review, dict):
            continue
        user = review.get("user")
        login = user.get("login") if isinstance(user, dict) else None
        if (
            login == EXPECTED_REVIEWER
            and review.get("state") == "APPROVED"
            and review.get("commit_id") == head_sha
        ):
            return True
    return False


def approve_exact_head(
    gh: Any,
    owner: str,
    repo: str,
    pr_number: int,
    head_sha: str,
    dispatch_id: str,
) -> dict[str, Any]:
    body = (
        f"Bounded Council Clerk documentary review for {dispatch_id} at exact head "
        f"{head_sha}. Protected Programme validators re-established that the branch "
        "contains exactly one registered RESULT/1 raw snapshot plus its machine "
        "receipt, bound to the protected dispatch and source comment, with "
        "canonical_claim_effect=false and mathematical status unadjudicated. "
        "APPROVE applies only to documentary preservation through existing "
        "MATHSOLVE protection. It does not approve mathematical correctness, "
        "independence strength, certification, claim promotion, publication, or "
        "campaign advancement."
    )
    result = gh.request(
        "POST",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews",
        {"commit_id": head_sha, "event": "APPROVE", "body": body},
    )
    if not isinstance(result, dict) or result.get("state") != "APPROVED":
        raise RuntimeError(f"{dispatch_id}: review submission malformed: {result!r}")
    return result


def run(programme_root: Path, apply: bool) -> dict[str, Any]:
    token = os.environ.get("MATHSOLVE_COUNCIL_CLERK_TOKEN", "")
    if not token:
        raise RuntimeError("MATHSOLVE_COUNCIL_CLERK_TOKEN is empty")

    (
        ControllerError,
        Github,
        find_open_pr,
        list_intake_branches,
        validate_candidate,
        validate_pr_binding,
    ) = load_programme_controller(programme_root)

    owner = "grandchallenge"
    repo = "MATHSOLVE"
    gh = Github(token)

    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "controller": "GCL_COUNCIL_CLERK_CEI_EVIDENCE_REVIEW",
        "target_repository": f"{owner}/{repo}",
        "apply": apply,
        "reviewer": EXPECTED_REVIEWER,
        "authority": {
            "contents": "read",
            "pull_requests": "write",
            "repository_content_write": False,
            "merge": False,
            "admin_bypass": False,
            "campaign_mutation": False,
            "mathematical_adjudication": False,
        },
        "candidates": [],
        "approvals": [],
        "already_approved": [],
        "errors": [],
    }

    for branch in list_intake_branches(gh):
        pr = find_open_pr(gh, branch)
        if pr is None:
            continue
        try:
            item = validate_candidate(gh, branch)
            if item.get("state") != "OPEN_PR_EXISTS":
                raise ControllerError(
                    f"{item['dispatch_id']}: unexpected intake state "
                    f"{item.get('state')}"
                )
            live = gh.request(
                "GET", f"/repos/{owner}/{repo}/pulls/{pr['number']}"
            )
            if not isinstance(live, dict):
                raise ControllerError(
                    f"{item['dispatch_id']}: evidence PR response malformed"
                )
            binding = validate_pr_binding(gh, item, live)
            pr_number = binding["pr_number"]
            head_sha = binding["head_sha"]
            if not isinstance(pr_number, int) or not isinstance(head_sha, str):
                raise ControllerError(
                    f"{item['dispatch_id']}: PR identity unavailable"
                )
            candidate = {
                "campaign": item["campaign"],
                "dispatch_id": item["dispatch_id"],
                "branch": branch,
                "pr_number": pr_number,
                "head_sha": head_sha,
                "state": "VALIDATED_FOR_DOCUMENTARY_REVIEW",
            }
            report["candidates"].append(candidate)
            if exact_approval_exists(gh, owner, repo, pr_number, head_sha):
                report["already_approved"].append(candidate)
                continue
            if apply:
                review = approve_exact_head(
                    gh,
                    owner,
                    repo,
                    pr_number,
                    head_sha,
                    item["dispatch_id"],
                )
                report["approvals"].append(
                    {
                        **candidate,
                        "review_id": review.get("id"),
                        "review_state": review.get("state"),
                    }
                )
        except (ControllerError, RuntimeError) as exc:
            report["errors"].append({"branch": branch, "error": str(exc)})

    report["authority_created"] = False
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--programme-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    try:
        report = run(args.programme_root.resolve(), args.apply)
    except Exception as exc:
        report = {
            "schema_version": "1.0.0",
            "controller": "GCL_COUNCIL_CLERK_CEI_EVIDENCE_REVIEW",
            "apply": args.apply,
            "fatal_error": str(exc),
            "authority_created": False,
        }
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(str(exc), file=sys.stderr)
        return 2

    args.report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
