from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError
from urllib.request import Request, urlopen


SUCCESSFUL_CHECK_CONCLUSIONS = {"success", "neutral", "skipped"}
AGENT_ROLES = ("adversary", "referee")
ALL_ROLES = (*AGENT_ROLES, "human_steward")


class ClerkError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str, *, api_url: str = "https://api.github.com") -> None:
        if not token:
            raise ClerkError("GH_TOKEN is required")
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.api_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "gcl-constitutional-review-clerk",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ClerkError(
                f"GitHub API {method} {path} failed: {exc.code} {detail}"
            ) from exc
        if not body:
            return None
        return json.loads(body)

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, payload: Mapping[str, Any]) -> Any:
        return self.request("POST", path, payload)


@dataclass(frozen=True, slots=True)
class Subject:
    repository: str
    pull_request: int
    url: str
    head_sha: str
    base_sha: str
    author: str
    draft: bool
    mergeable_state: str
    changed_paths: tuple[str, ...]
    checks: tuple[tuple[str, str], ...]
    checks_ready: bool
    boundary_checks: tuple[tuple[str, bool], ...]

    def packet_view(self) -> dict[str, Any]:
        return {
            "repository": self.repository,
            "pull_request": self.pull_request,
            "url": self.url,
            "head_sha": self.head_sha,
            "base_sha": self.base_sha,
            "author": self.author,
            "draft": self.draft,
            "mergeable_state": self.mergeable_state,
            "changed_paths": list(self.changed_paths),
            "checks": [
                {"name": name, "conclusion": conclusion}
                for name, conclusion in self.checks
            ],
            "checks_ready": self.checks_ready,
            "boundary_checks": [
                {"name": name, "passed": passed}
                for name, passed in self.boundary_checks
            ],
        }


def canonical_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def core_campaign_contract(config: Mapping[str, Any]) -> dict[str, Any]:
    """Return the immutable finding contract, excluding findings themselves."""

    required = (
        "schema_version",
        "campaign_id",
        "organization",
        "finding_binding",
        "staffing_mode",
        "constitutional_source",
        "primary_pr",
        "subjects",
        "human_stewards",
        "receipt",
    )
    missing = [field for field in required if field not in config]
    if missing:
        raise ClerkError(f"campaign finding contract is incomplete: {missing}")
    if config["finding_binding"] != "campaign_contract_v1":
        raise ClerkError("unknown campaign finding binding")
    return {field: config[field] for field in required}


def build_packet(
    config: Mapping[str, Any], subjects: Iterable[Subject]
) -> dict[str, Any]:
    ordered = sorted(subjects, key=lambda item: item.repository)
    subject_record = {
        "schema_version": "1.0.0",
        "campaign_id": config["campaign_id"],
        "constitutional_source": config["constitutional_source"],
        "subjects": [item.packet_view() for item in ordered],
    }
    binding = config.get("finding_binding")
    if binding is not None:
        subject_record["campaign_contract_sha256"] = canonical_digest(
            core_campaign_contract(config)
        )
    subject_digest = canonical_digest(subject_record)
    authors = sorted({item.author for item in ordered})
    agent_findings = validate_agent_findings(
        config.get("agent_findings", {}),
        subject_digest=subject_digest,
        proposal_authors=set(authors),
    )
    packet = {
        **subject_record,
        "staffing_mode": config["staffing_mode"],
        "human_steward": config["human_stewards"][0],
        "proposal_authors": authors,
        "subject_sha256": subject_digest,
        "agent_findings": agent_findings,
        "required_roles": list(ALL_ROLES),
        "authority_boundary": (
            "Distinct non-author agents supply Adversary and Referee findings; "
            "only the named Human Steward supplies reserved authorization."
        ),
    }
    packet["ready_for_steward_review"] = (
        set(agent_findings) == set(AGENT_ROLES)
    ) and all(
        subject.checks_ready
        and all(passed for _, passed in subject.boundary_checks)
        for subject in ordered
    )
    packet["ready_for_human_review"] = packet["ready_for_steward_review"]
    packet["packet_sha256"] = canonical_digest(packet)
    return packet


def validate_agent_findings(
    raw_findings: Mapping[str, Any],
    *,
    subject_digest: str,
    proposal_authors: set[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(raw_findings, Mapping):
        raise ClerkError("agent_findings must be an object")
    if any(role not in AGENT_ROLES for role in raw_findings):
        raise ClerkError("agent_findings contains an unknown office")

    admitted: dict[str, dict[str, Any]] = {}
    for role in AGENT_ROLES:
        finding = raw_findings.get(role)
        if finding is None:
            continue
        if not isinstance(finding, Mapping):
            raise ClerkError(f"{role} finding must be an object or null")
        required = {
            "office",
            "reviewer_id",
            "session_id",
            "subject_sha256",
            "status",
            "obligations",
            "findings",
            "evidence_refs",
            "residual_uncertainty",
            "recorded_at",
            "record_url",
        }
        missing = sorted(required - set(finding))
        if missing:
            raise ClerkError(f"{role} finding is incomplete: {missing}")
        if finding["office"] != role or finding["status"] != "approved":
            raise ClerkError(f"{role} finding has the wrong office or status")
        if finding["subject_sha256"] != subject_digest:
            raise ClerkError(f"{role} finding is stale")
        if finding["reviewer_id"] in proposal_authors:
            raise ClerkError(f"{role} reviewer is a proposal author")
        for field in (
            "reviewer_id",
            "session_id",
            "recorded_at",
            "record_url",
        ):
            if not isinstance(finding[field], str) or not finding[field]:
                raise ClerkError(f"{role} finding requires {field}")
        for field in (
            "obligations",
            "findings",
            "evidence_refs",
            "residual_uncertainty",
        ):
            if not isinstance(finding[field], list):
                raise ClerkError(f"{role} finding requires {field}")
        if not finding["obligations"] or not finding["evidence_refs"]:
            raise ClerkError(f"{role} finding lacks obligations or evidence")
        admitted[role] = dict(finding)

    if set(admitted) == set(AGENT_ROLES):
        adversary = admitted["adversary"]
        referee = admitted["referee"]
        if adversary["reviewer_id"] == referee["reviewer_id"]:
            raise ClerkError("Adversary and Referee require distinct agent identities")
        if adversary["session_id"] == referee["session_id"]:
            raise ClerkError("Adversary and Referee require distinct agent sessions")
    return admitted


def marker(campaign_id: str, packet_digest: str, role: str) -> str:
    return (
        f"<!-- gcl-constitutional-review:{campaign_id}:"
        f"{packet_digest}:{role} -->"
    )


def packet_comment_body(packet: Mapping[str, Any]) -> str:
    rows = []
    for subject in packet["subjects"]:
        checks = ", ".join(
            f"{item['name']}={item['conclusion']}" for item in subject["checks"]
        )
        boundaries = ", ".join(
            f"{item['name']}={'pass' if item['passed'] else 'FAIL'}"
            for item in subject["boundary_checks"]
        )
        rows.append(
            f"| [{subject['repository']}#{subject['pull_request']}]"
            f"({subject['url']}) | `{subject['head_sha']}` | "
            f"{checks or 'none'} | {boundaries or 'none'} |"
        )
    ready = "READY" if packet["ready_for_human_review"] else "NOT READY"
    return "\n".join(
        [
            marker(
                packet["campaign_id"],
                packet["packet_sha256"],
                "packet",
            ),
            f"## Constitutional review packet — {packet['campaign_id']}",
            "",
            f"**Automated evidence status:** {ready}",
            f"**Packet digest:** `{packet['packet_sha256']}`",
            "",
            "| Exact subject | Head commit | Checks | Boundary tests |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "This packet is evidence, not approval. Any new subject commit creates "
            "a new digest and makes agent findings and Steward reactions stale.",
            "",
            "The Clerk recognizes structured, distinct agent Adversary and Referee "
            "findings, then one eligible `+1` reaction on the Human Steward "
            "attestation. Other reactions and comments do not sign.",
        ]
    )


def attestation_text(role: str) -> tuple[str, ...]:
    if role == "human_steward":
        return (
            "I substantively inspected the exact revisions, agent findings, "
            "authority boundary, compatibility plan, and consequences.",
            "Acting as Human Steward, I authorize admission of these exact revisions "
            "subject to the separate activation PR and its checks.",
            "This reaction is reserved to an allowlisted Human Steward.",
        )
    raise ClerkError(f"unknown role: {role}")


def attestation_comment_body(
    packet: Mapping[str, Any], role: str
) -> str:
    title = role.replace("_", " ").title()
    statements = attestation_text(role)
    return "\n".join(
        [
            marker(packet["campaign_id"], packet["packet_sha256"], role),
            f"## {title} attestation — {packet['campaign_id']}",
            "",
            f"Packet: `{packet['packet_sha256']}`",
            *[f"- {statement}" for statement in statements],
            "",
            "**To sign:** after inspection, react 👍 to this comment. That single "
            "reaction attests to every statement above.",
            "",
            "The Clerk rejects missing or duplicate agent findings, bots, "
            "non-stewards, and reactions attached to a stale packet.",
        ]
    )


def select_human_steward(
    *,
    reactions: list[Mapping[str, Any]],
    eligible_reviewers: set[str],
    human_stewards: set[str],
) -> Mapping[str, Any] | None:
    candidates = sorted(
        reactions,
        key=lambda item: (item.get("created_at", ""), item["user"]["login"]),
    )
    for reaction in candidates:
        user = reaction["user"]
        login = user["login"]
        if (
            reaction.get("content") == "+1"
            and user.get("type") == "User"
            and login in human_stewards
            and login in eligible_reviewers
        ):
            return reaction
    return None


def build_receipt(
    packet: Mapping[str, Any],
    steward_reaction: Mapping[str, Any],
    steward_comment: Mapping[str, Any],
) -> dict[str, Any]:
    signoffs = []
    for role in AGENT_ROLES:
        finding = packet["agent_findings"][role]
        signoffs.append(
            {
                "office": role,
                "reviewer": finding["reviewer_id"],
                "reviewer_kind": "agent",
                "session_id": finding["session_id"],
                "authentication_id": finding["session_id"],
                "authenticated_at": finding["recorded_at"],
                "attestation_record": finding["record_url"],
                "attestation_sha256": canonical_digest(finding),
            }
        )
    body = steward_comment["body"]
    signoffs.append(
        {
            "office": "human_steward",
            "reviewer": steward_reaction["user"]["login"],
            "reviewer_kind": "human",
            "session_id": None,
            "authentication_id": str(steward_reaction["id"]),
            "authenticated_at": steward_reaction.get("created_at"),
            "attestation_record": steward_comment["html_url"],
            "attestation_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        }
    )
    return {
        "schema_version": "1.1.0",
        "campaign_id": packet["campaign_id"],
        "staffing_mode": packet["staffing_mode"],
        "human_steward": packet["human_steward"],
        "proposal_authors": packet["proposal_authors"],
        "packet_sha256": packet["packet_sha256"],
        "subjects": [
            {
                "repository": subject["repository"],
                "pull_request": subject["pull_request"],
                "head_sha": subject["head_sha"],
            }
            for subject in packet["subjects"]
        ],
        "signoffs": signoffs,
        "recorded_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "complete",
        "authority_boundary": (
            "This receipt records separated agent findings and Human Steward "
            "authorization. It does not merge or activate the proposal; admission "
            "remains a separate reviewed pull request."
        ),
    }


class ReviewClerk:
    def __init__(
        self,
        client: GitHubClient,
        config: Mapping[str, Any],
        *,
        apply: bool,
    ) -> None:
        self.client = client
        self.config = config
        self.apply = apply

    def run(self, output_dir: Path) -> dict[str, Any]:
        subjects = [self._load_subject(item) for item in self.config["subjects"]]
        packet = build_packet(self.config, subjects)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "review-packet.json").write_text(
            json.dumps(packet, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        primary = self.config["primary_pr"]
        comments = self._issue_comments(
            primary["repository"], primary["pull_request"]
        )
        packet_comment = self._ensure_comment(
            primary,
            comments,
            marker(
                packet["campaign_id"],
                packet["packet_sha256"],
                "packet",
            ),
            packet_comment_body(packet),
        )
        steward_comment = self._ensure_comment(
            primary,
            comments,
            marker(
                packet["campaign_id"],
                packet["packet_sha256"],
                "human_steward",
            ),
            attestation_comment_body(packet, "human_steward"),
        )

        status: dict[str, Any] = {
            "campaign_id": packet["campaign_id"],
            "packet_sha256": packet["packet_sha256"],
            "packet_comment": packet_comment.get("html_url"),
            "ready_for_human_review": packet["ready_for_human_review"],
            "ready_for_steward_review": packet["ready_for_steward_review"],
            "agent_findings": sorted(packet["agent_findings"]),
            "complete": False,
        }
        if not self.apply:
            status["mode"] = "dry-run"
            status["missing"] = {
                role: "structured agent finding is not admitted"
                for role in AGENT_ROLES
                if role not in packet["agent_findings"]
            }
            status["missing"]["human_steward"] = (
                "comments and reactions are not read in dry-run mode"
            )
            self._write_status(output_dir, status)
            return status

        steward_reactions = self.client.get(
            f"/repos/{primary['repository']}/issues/comments/"
            f"{steward_comment['id']}/reactions?per_page=100"
        )
        candidate_logins = {
            reaction["user"]["login"]
            for reaction in steward_reactions
            if reaction.get("content") == "+1"
            and reaction.get("user", {}).get("type") == "User"
        }
        eligible = {
            login
            for login in candidate_logins
            if self._eligible_on_all_subjects(login, subjects)
            and not self._has_current_changes_requested(login, subjects)
        }
        steward = select_human_steward(
            reactions=steward_reactions,
            eligible_reviewers=eligible,
            human_stewards=set(self.config["human_stewards"]),
        )
        missing = {
            role: "structured agent finding is not admitted"
            for role in AGENT_ROLES
            if role not in packet["agent_findings"]
        }
        if steward is None:
            missing["human_steward"] = (
                "no eligible +1 attestation on the current packet"
            )
        status["missing"] = missing
        status["signers"] = (
            {"human_steward": steward["user"]["login"]} if steward else {}
        )

        if packet["ready_for_steward_review"] and not missing and steward:
            receipt = build_receipt(packet, steward, steward_comment)
            receipt_path = output_dir / "constitutional-review-receipt.json"
            receipt_path.write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            receipt_issue = self._ensure_receipt_issue(receipt)
            status["complete"] = True
            status["receipt_issue"] = receipt_issue.get("html_url")
            self._ensure_completion_comments(receipt, subjects)

        self._write_status(output_dir, status)
        return status

    def _load_subject(self, spec: Mapping[str, Any]) -> Subject:
        repository = spec["repository"]
        number = int(spec["pull_request"])
        pull = self.client.get(f"/repos/{repository}/pulls/{number}")
        files = self.client.get(
            f"/repos/{repository}/pulls/{number}/files?per_page=100"
        )
        check_data = self.client.get(
            f"/repos/{repository}/commits/{pull['head']['sha']}/check-runs"
            "?per_page=100"
        )
        changed_paths = tuple(sorted(item["filename"] for item in files))
        checks = tuple(
            sorted(
                {
                    (
                        item["name"],
                        (item.get("conclusion") or item["status"]).lower(),
                    )
                    for item in check_data.get("check_runs", [])
                }
            )
        )
        checks_ready = bool(checks) and all(
            conclusion in SUCCESSFUL_CHECK_CONCLUSIONS
            for _, conclusion in checks
        )
        boundaries: list[tuple[str, bool]] = []
        for path in spec.get("forbidden_changed_paths", []):
            boundaries.append((f"unchanged:{path}", path not in changed_paths))
        for path in spec.get("required_changed_paths", []):
            boundaries.append((f"changed:{path}", path in changed_paths))
        return Subject(
            repository=repository,
            pull_request=number,
            url=pull["html_url"],
            head_sha=pull["head"]["sha"],
            base_sha=pull["base"]["sha"],
            author=pull["user"]["login"],
            draft=bool(pull["draft"]),
            mergeable_state=pull.get("mergeable_state") or "unknown",
            changed_paths=changed_paths,
            checks=checks,
            checks_ready=checks_ready,
            boundary_checks=tuple(boundaries),
        )

    def _issue_comments(self, repository: str, number: int) -> list[dict[str, Any]]:
        if not self.apply:
            return []
        return self.client.get(
            f"/repos/{repository}/issues/{number}/comments?per_page=100"
        )

    def _ensure_comment(
        self,
        primary: Mapping[str, Any],
        comments: list[Mapping[str, Any]],
        exact_marker: str,
        body: str,
    ) -> dict[str, Any]:
        for comment in comments:
            if exact_marker in comment.get("body", ""):
                return dict(comment)
        if not self.apply:
            return {"id": None, "body": body, "html_url": None}
        created = self.client.post(
            f"/repos/{primary['repository']}/issues/"
            f"{primary['pull_request']}/comments",
            {"body": body},
        )
        comments.append(created)
        return created

    def _eligible_on_all_subjects(
        self, login: str, subjects: Iterable[Subject]
    ) -> bool:
        try:
            for subject in subjects:
                permission = self.client.get(
                    f"/repos/{subject.repository}/collaborators/{login}/permission"
                )
                if permission.get("permission") not in {"admin", "maintain", "write"}:
                    return False
        except ClerkError:
            return False
        return True

    def _has_current_changes_requested(
        self, login: str, subjects: Iterable[Subject]
    ) -> bool:
        for subject in subjects:
            reviews = self.client.get(
                f"/repos/{subject.repository}/pulls/"
                f"{subject.pull_request}/reviews?per_page=100"
            )
            authored = [
                review
                for review in reviews
                if review.get("user", {}).get("login") == login
                and review.get("submitted_at")
            ]
            if authored:
                latest = max(authored, key=lambda item: item["submitted_at"])
                if latest.get("state") == "CHANGES_REQUESTED":
                    return True
        return False

    def _ensure_receipt_issue(
        self, receipt: Mapping[str, Any]
    ) -> dict[str, Any]:
        target = self.config["receipt"]
        title = (
            f"[CONSTITUTIONAL RECEIPT] {receipt['campaign_id']} "
            f"{receipt['packet_sha256'][:12]}"
        )
        issues = self.client.get(
            f"/repos/{target['repository']}/issues?state=all&per_page=100"
        )
        for issue in issues:
            if issue.get("title") == title:
                return issue
        encoded = base64.b64encode(
            (
                json.dumps(receipt, sort_keys=True, separators=(",", ":"))
                + "\n"
            ).encode("utf-8")
        ).decode("ascii")
        body = "\n".join(
            [
                f"<!-- gcl-constitutional-receipt:{receipt['packet_sha256']} -->",
                "The Council Clerk generated this immutable review receipt from "
                "separated agent findings and Human Steward authorization.",
                "",
                "Automation must copy the decoded JSON into the configured "
                "repository path through a separate reviewed pull request. This "
                "issue does not activate or merge the proposal.",
                "",
                f"Target path: `{target['path_prefix']}/"
                f"{receipt['campaign_id']}-{receipt['packet_sha256'][:12]}.json`",
                "",
                "```text",
                encoded,
                "```",
            ]
        )
        return self.client.post(
            f"/repos/{target['repository']}/issues",
            {"title": title, "body": body},
        )

    def _ensure_completion_comments(
        self, receipt: Mapping[str, Any], subjects: Iterable[Subject]
    ) -> None:
        completion_marker = (
            f"<!-- gcl-constitutional-review-complete:"
            f"{receipt['packet_sha256']} -->"
        )
        body = "\n".join(
            [
                completion_marker,
                "Agent findings and Human Steward authorization are complete for "
                "this exact review packet.",
                "",
                f"Packet digest: `{receipt['packet_sha256']}`",
                "",
                "A receipt issue has been opened. This status records review only; "
                "a separate activation pull request remains required.",
            ]
        )
        for subject in subjects:
            comments = self._issue_comments(
                subject.repository, subject.pull_request
            )
            if any(completion_marker in item.get("body", "") for item in comments):
                continue
            self.client.post(
                f"/repos/{subject.repository}/issues/"
                f"{subject.pull_request}/comments",
                {"body": body},
            )

    @staticmethod
    def _write_status(output_dir: Path, status: Mapping[str, Any]) -> None:
        (output_dir / "review-status.json").write_text(
            json.dumps(status, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "campaign_id",
        "organization",
        "constitutional_source",
        "staffing_mode",
        "agent_findings",
        "primary_pr",
        "subjects",
        "human_stewards",
        "receipt",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ClerkError(f"missing config fields: {missing}")
    if config["schema_version"] != "1.0.0":
        raise ClerkError("unsupported config version")
    if config["staffing_mode"] != "steward_supervised_agents":
        raise ClerkError("unsupported staffing mode")
    if len(config["human_stewards"]) != 1:
        raise ClerkError("exactly one Human Steward is required")
    if len(config["subjects"]) < 1:
        raise ClerkError("at least one review subject is required")
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    token = os.environ.get("GH_TOKEN", "")
    if not token and not args.apply:
        token = os.environ.get("GITHUB_TOKEN", "")
    client = GitHubClient(token)
    status = ReviewClerk(client, config, apply=args.apply).run(args.output_dir)
    print(json.dumps(status, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ClerkError as exc:
        print(f"constitutional review clerk failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
