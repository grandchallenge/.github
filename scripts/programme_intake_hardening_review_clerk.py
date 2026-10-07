#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from typing import Any

OWNER = "grandchallenge"
REPO = "MATH-PROGRAMME"
EXPECTED_REVIEWER = "gcl-council-clerk[bot]"
EXPECTED_TITLE = "Harden live-intake and canary lifecycle gates"
EXPECTED_FILES = {
    "ci/ns_ci_intake_pr_controller.py",
    "ci/external_intake_evidence_admission.py",
    "ci/erdos_open_postprotect_controller.py",
    "tests/test_external_intake_evidence_admission.py",
    "tests/test_erdos_open_postprotect_controller.py",
}

def req(method: str, path: str, token: str, payload: dict[str, Any] | None = None) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(
        "https://api.github.com" + path,
        method=method,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "gcl-programme-intake-hardening-review-clerk",
            **({"Content-Type":"application/json"} if data else {}),
        },
    )
    with urllib.request.urlopen(r, timeout=30) as h:
        raw=h.read()
    return json.loads(raw) if raw else None

def run(pr_number: int, apply: bool) -> dict[str, Any]:
    token=os.environ["PROGRAMME_COUNCIL_CLERK_TOKEN"]
    pr=req("GET",f"/repos/{OWNER}/{REPO}/pulls/{pr_number}",token)
    if not isinstance(pr,dict): raise RuntimeError("PR response malformed")
    if pr.get("state")!="open" or pr.get("draft") is True: raise RuntimeError("PR is not ordinary open")
    if pr.get("title")!=EXPECTED_TITLE: raise RuntimeError("PR title mismatch")
    if (pr.get("base") or {}).get("ref")!="main": raise RuntimeError("PR base mismatch")
    head=(pr.get("head") or {}).get("sha")
    if not isinstance(head,str) or len(head)!=40: raise RuntimeError("head unavailable")
    files=req("GET",f"/repos/{OWNER}/{REPO}/pulls/{pr_number}/files?per_page=100",token)
    changed={x.get("filename") for x in files if isinstance(x,dict)}
    if changed!=EXPECTED_FILES:
        raise RuntimeError(f"changed-file set mismatch: {sorted(changed)}")
    reviews=req("GET",f"/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews?per_page=100",token)
    already=any(
        isinstance(x,dict)
        and (x.get("user") or {}).get("login")==EXPECTED_REVIEWER
        and x.get("state")=="APPROVED"
        and x.get("commit_id")==head
        for x in reviews
    )
    out={"pr_number":pr_number,"head_sha":head,"changed_files":sorted(changed),"already_approved":already,"apply":apply}
    if apply and not already:
        review=req("POST",f"/repos/{OWNER}/{REPO}/pulls/{pr_number}/reviews",token,{
            "commit_id":head,
            "event":"APPROVE",
            "body":"Bounded Council Clerk exact-head review of the live-intake controller hardening. The PR is restricted to the registered intake discovery, evidence-admission gate, canary lifecycle controller, and their regression tests. This approval creates no mathematical, certification, publication, or campaign authority.",
        })
        out["review_id"]=review.get("id")
        out["review_state"]=review.get("state")
    return out

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--pr-number",type=int,required=True)
    p.add_argument("--apply",action="store_true")
    p.add_argument("--report",required=True)
    a=p.parse_args()
    try:
        out=run(a.pr_number,a.apply); rc=0
    except Exception as e:
        out={"error":str(e),"pr_number":a.pr_number,"apply":a.apply}; rc=2
    open(a.report,"w",encoding="utf-8").write(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    return rc

if __name__=="__main__": raise SystemExit(main())
