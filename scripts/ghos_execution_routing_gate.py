from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

FEATURES = {"AUTONOMOUS_WAKE", "EXTERNAL_REUSABLE_JOB", "EXTERNAL_WAIT", "NON_RECONCILABLE_MUTATION",
    "OPAQUE_EXECUTION", "SCHEDULED", "SECRET_CREDENTIAL", "UNATTENDED_DISPATCH", "WRITE_CAPABLE"}
CLAIM_BOUNDARIES = {"constitutional": False, "merge": False, "certification": False, "production": False,
    "publication": False, "mathematical_claim": False, "claim_promotion": False, "commercial": False}
ADMITTED_CONTROLLERS = [{"controller_id": "GITHUB_ACTIONS", "executor_class": "PERSISTENT_CONTROLLER", "provider": "github",
    "durable_wake_mechanism": "repository-bound GitHub Actions event queue",
    "state_store": "GitHub Actions workflow run and job records bound to repository and commit SHA",
    "supported_features": sorted(FEATURES)}]


class RoutingGateError(ValueError):
    pass


def features(workflow: Mapping[str, Any]) -> list[str]:
    triggers = workflow.get("on", workflow.get(True, {}))
    names = {triggers} if isinstance(triggers, str) else set(triggers or ()) if isinstance(triggers, (list, Mapping)) else set()
    result: set[str] = set()
    if "schedule" in names: result.update({"SCHEDULED", "AUTONOMOUS_WAKE"})
    if names.intersection({"repository_dispatch", "workflow_run"}): result.update({"UNATTENDED_DISPATCH", "AUTONOMOUS_WAKE"})

    def writable(value: object) -> bool:
        return value == "write-all" or isinstance(value, Mapping) and any(item == "write" for item in value.values())
    if writable(workflow.get("permissions")): result.add("WRITE_CAPABLE")
    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, Mapping): raise RoutingGateError("workflow jobs must be a mapping")
    for job in jobs.values():
        if not isinstance(job, Mapping): raise RoutingGateError("workflow job must be a mapping")
        if "uses" in job: result.add("EXTERNAL_REUSABLE_JOB")
        if writable(job.get("permissions")): result.add("WRITE_CAPABLE")
        text = json.dumps(job, sort_keys=True).lower()
        if '"uses":' in text or '"run":' in text: result.add("OPAQUE_EXECUTION")
        if "${{ secrets." in text or "secrets[" in text or "github.token" in text: result.add("SECRET_CREDENTIAL")
        if any(token in text for token in ("gh run watch", "sleep ", "poll", "wait-for", "wait_for")): result.add("EXTERNAL_WAIT")
        if "ghos-non-reconcilable-mutation" in text: result.add("NON_RECONCILABLE_MUTATION")
        if any(token in text for token in ("gh pr merge", "git push", "git.exe push", "gh release create", "gh project item-add", "gh api", "-x post", "-x patch", "-x put", "-x delete")): result.add("WRITE_CAPABLE")
    return sorted(result)


def topology(observed: set[str]) -> str:
    if observed.intersection({"AUTONOMOUS_WAKE", "NON_RECONCILABLE_MUTATION", "OPAQUE_EXECUTION", "SECRET_CREDENTIAL", "WRITE_CAPABLE"}):
        return "PERSISTENT_CONTROLLER_REQUIRED"
    if observed.intersection({"EXTERNAL_REUSABLE_JOB", "EXTERNAL_WAIT", "UNATTENDED_DISPATCH"}): return "MULTI_SESSION_RESUMABLE"
    return "BOUNDED_ATOMIC"


def validate(root: Path, repository: str) -> None:
    registry_path = root / ".ghos-routing/workflows.json"
    if not registry_path.is_file(): raise RoutingGateError("mandatory execution-routing registry is missing")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("record_type") != "GHOS_EXECUTION_ROUTING_REGISTRY" or registry.get("schema_version") != "1.0.0":
        raise RoutingGateError("execution-routing registry identity is invalid")
    if registry.get("repository") != repository: raise RoutingGateError("execution-routing repository identity mismatch")
    if registry.get("controllers") != ADMITTED_CONTROLLERS: raise RoutingGateError("controller catalog is not the governed admitted-controller set")
    if registry.get("claim_boundaries") != CLAIM_BOUNDARIES: raise RoutingGateError("execution-routing registry widens authority")

    directory = root / ".github/workflows"
    paths = sorted(path.relative_to(root).as_posix() for pattern in ("*.yml", "*.yaml") for path in directory.glob(pattern) if path.is_file())
    entries = registry.get("workflows")
    if not isinstance(entries, list): raise RoutingGateError("workflow routing entries must be an array")
    registered = [entry.get("path") for entry in entries if isinstance(entry, Mapping)]
    if registered != paths or len(registered) != len(set(registered)): raise RoutingGateError("workflow routing coverage mismatch")
    controllers = {item["controller_id"]: item for item in ADMITTED_CONTROLLERS}
    for entry in entries:
        relative = entry["path"]
        workflow = yaml.safe_load((root / relative).read_text(encoding="utf-8"))
        if not isinstance(workflow, Mapping): raise RoutingGateError(f"workflow must be a mapping: {relative}")
        observed = features(workflow)
        if entry.get("observed_features") != observed: raise RoutingGateError(f"workflow feature declaration drift: {relative}")
        derived = topology(set(observed))
        if entry.get("topology") != derived: raise RoutingGateError(f"workflow topology declaration drift: {relative}")
        controller_id = entry.get("controller_id")
        if derived != "BOUNDED_ATOMIC":
            if controller_id not in controllers: raise RoutingGateError(f"persistent workflow lacks admitted controller: {relative}")
            if set(observed) - set(controllers[controller_id]["supported_features"]): raise RoutingGateError(f"controller capability mismatch: {relative}")
        elif controller_id is not None: raise RoutingGateError(f"bounded workflow cannot claim persistent controller: {relative}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, required=True); parser.add_argument("--repository", required=True)
    args = parser.parse_args(); validate(args.root.resolve(), args.repository); print("external GH-OS execution-routing gate passed")
