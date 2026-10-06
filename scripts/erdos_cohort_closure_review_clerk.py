#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any

EXPECTED_REVIEWER = "gcl-council-clerk[bot]"
EXPECTED_AUTHOR = "gcl-release-trust[bot]"
OWNER = "grandchallenge"
REPO = "MATHSOLVE"


def load_programme_controller(programme_root: Path):
    sys.path.insert(0, str(programme_root))
    from ci.ns_ci_intake_pr_controller import Github  # type: ignore
    from ci.erdos_open_postprotect_controller import (  # type: ignore
        BRANCH_RE,
        branch_name,
        validate_candidate,
    )
    return Github, BRANCH_RE, branch_name, validate_candidate


def list_candidate_branches(gh: Any) -> list[str]:
    prefix = urllib.parse.quote("heads/lifecycle/erdos-", safe="/")
    refs = gh.get_optional(f"/repos/{OWNER}/{REPO}/git/matching-refs/{prefix}")
    if refs is None:
        return []
    if not isinstance(refs, list):
        raise RuntimeError("ERDOS closure ref listing malformed")
    out = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        name = str(ref.get("ref", ""))
        if name.startswith("refs/heads/"):
            out.append(name[len("refs/heads/"):])
    return sorted(set(out))


def find_open_pr(gh: Any, branch: str) -> dict[str, Any] | None:
    head = urllib.parse.quote(f"{OWNER}:{branch}", safe="")
    prs = gh.request(
        "GET",
        f"/repos/{OWNER}/{REPO}/pulls?state=open&head={head}&base=main",
    )
    if not isinstance(prs, list):
        raise RuntimeError("ERDOS closure PR list malformed")
    return prs[0] if prs else None


def exact_approval_exists(gh: Any, pr_number: int, head_sha: str) -> bool:
    reviews = gh.request(
        "GET", f"/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews?per_page=100"
    )
    if not isinstance(reviews, list):
        raise RuntimeError("ERDOS closure review list malformed")
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


def validate_pr_binding(
    gh: Any,
    pr: dict[str, Any],
    branch: str,
    candidate: dict[str, Any],
) -> tuple[int, str]:
    if pr.get("state") != "open" or pr.get("draft") is True:
        raise RuntimeError(f"{branch}: closure PR is not an ordinary open PR")
    user = pr.get("user")
    author = user.get("login") if isinstance(user, dict) else None
    if author != EXPECTED_AUTHOR:
        raise RuntimeError(f"{branch}: closure PR author mismatch: {author!r}")
    base = pr.get("base")
    head = pr.get("head")
    base_ref = base.get("ref") if isinstance(base, dict) else None
    head_ref = head.get("ref") if isinstance(head, dict) else None
    head_sha = head.get("sha") if isinstance(head, dict) else None
    if base_ref != "main":
        raise RuntimeError(f"{branch}: closure PR base is not main")
    if head_ref != branch:
        raise RuntimeError(f"{branch}: closure PR head branch mismatch")
    if head_sha != candidate.get("head_sha"):
        raise RuntimeError(f"{branch}: closure PR exact head mismatch")
    number = pr.get("number")
    if not isinstance(number, int) or not isinstance(head_sha, str):
        raise RuntimeError(f"{branch}: closure PR identity unavailable")
    return number, head_sha


def approve_exact_head(
    gh: Any,
    pr_number: int,
    head_sha: str,
    problem: str,
) -> dict[str, Any]:
    body = (
        f"Bounded Council Clerk documentary review for ERDOS-{problem} blind-cohort "
        f"closure at exact head {head_sha}. Protected Programme validation re-established "
        "that the branch contains exactly one cohort-closure receipt generated from "
        "durably protected R1+A1 schema-valid evidence and that the closure has no "
        "mathematical, literature, certification, publication, prize, or parent-problem "
        "effect. APPROVE applies only to mechanical closure through existing MATHSOLVE "
        "repository protection."
    )
    out = gh.request(
        "POST",
        f"/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews",
        {"commit_id": head_sha, "event": "APPROVE", "body": body},
    )
    if not isinstance(out, dict) or out.get("state") != "APPROVED":
        raise RuntimeError(f"ERDOS-{problem}: closure review submission malformed")
    return out


def run(programme_root: Path, solve_root: Path, apply: bool) -> dict[str, Any]:
    token = os.environ.get("MATHSOLVE_COUNCIL_CLERK_TOKEN", "")
    if not token:
        raise RuntimeError("MATHSOLVE_COUNCIL_CLERK_TOKEN is empty")
    Github, BRANCH_RE, _, validate_candidate = load_programme_controller(programme_root)
    gh = Github(token)
    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "controller": "GCL_COUNCIL_CLERK_ERDOS_COHORT_CLOSURE_REVIEW",
        "target_repository": f"{OWNER}/{REPO}",
        "apply": apply,
        "reviewer": EXPECTED_REVIEWER,
        "authority": {
            "contents": "read",
            "pull_requests": "write",
            "repository_content_write": False,
            "merge": False,
            "admin_bypass": False,
            "mathematical_adjudication": False,
        },
        "candidates": [],
        "approvals": [],
        "already_approved": [],
        "errors": [],
    }

    for branch in list_candidate_branches(gh):
        match = BRANCH_RE.fullmatch(branch)
        if not match:
            continue
        problem = match.group(1)
        pr = find_open_pr(gh, branch)
        if pr is None:
            continue
        try:
            candidate = validate_candidate(gh, solve_root, branch)
            live = gh.request("GET", f"/repos/{OWNER}/{REPO}/pulls/{pr['number']}")
            if not isinstance(live, dict):
                raise RuntimeError(f"{branch}: closure PR response malformed")
            pr_number, head_sha = validate_pr_binding(gh, live, branch, candidate)
            item = {
                "problem": problem,
                "branch": branch,
                "pr_number": pr_number,
                "head_sha": head_sha,
                "state": "VALIDATED_FOR_DOCUMENTARY_REVIEW",
            }
            report["candidates"].append(item)
            if exact_approval_exists(gh, pr_number, head_sha):
                report["already_approved"].append(item)
                continue
            if apply:
                review = approve_exact_head(gh, pr_number, head_sha, problem)
                report["approvals"].append(
                    {
                        **item,
                        "review_id": review.get("id"),
                        "review_state": review.get("state"),
                    }
                )
        except Exception as exc:
            report["errors"].append({"branch": branch, "error": str(exc)})

    report["authority_created"] = False
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--programme-root", type=Path, required=True)
    ap.add_argument("--solve-root", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    try:
        report = run(args.programme_root.resolve(), args.solve_root.resolve(), args.apply)
        rc = 0
    except Exception as exc:
        report = {
            "schema_version": "1.0.0",
            "controller": "GCL_COUNCIL_CLERK_ERDOS_COHORT_CLOSURE_REVIEW",
            "fatal_error": str(exc),
            "authority_created": False,
        }
        rc = 2
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
