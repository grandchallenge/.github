# GH-OS shared routing control runbook

**Campaign:** `GHOS-ESTATE-ROLLOUT-001`  
**Tracker:** `grandchallenge/.github#67`  
**Repository:** `grandchallenge/.github`

## Purpose

This runbook governs the organization-level GH-OS routing gate and the repository-local routing enforcement for `grandchallenge/.github`.

The `.github` repository is both a workflow-bearing repository and the host of the shared external gate consumed by other repositories. Those roles must remain distinct. Hosting the gate does not make `.github` automatically conformant, and changing gate bytes must not silently change the semantics enforced by consumers.

This control grants no constitutional, merge, certification, production, publication, mathematical-claim, claim-promotion, or commercial authority.

## Protected opening state

The Phase 0 implementation starts from protected head:

`355e029735961c29bf194985f885b0bda08579be`

The protected shared gate is:

- path: `scripts/ghos_execution_routing_gate.py`;
- blob: `b8a62a7f0ca8cb552e212f6ec9c36a5a48a33608`;
- SHA-256: `1c4f9d82b1817d69187f3d87efbe0f6e60dd617d51a8aa330b119d48d3c95a43`.

The opening main ruleset is `17137624` (`Community profile - main`). Before Phase 0 activation it requires `policy / policy` and `security / action-policy`, uses strict required-status-check semantics, and has no bypass actors. It does not yet require `routing-enforcement`.

## Repository-local control surface

The implementation introduces:

- `.ghos-routing/workflows.json`: exhaustive execution-routing registry;
- `.ghos-routing/control.json`: shared-gate identity, activation state, consumer pinning state, and named deviations;
- `.github/workflows/ghos-routing-enforcement.yml`: protected-base candidate-independent enforcement;
- `tests/test_ghos_execution_routing_gate.py`: synthetic hostile tests plus exact repository-registry validation.

The routing registry contains all ten pre-existing direct workflows plus the enforcement workflow itself. The gate derives features and topology from actual workflow bytes. Registry declarations cannot downgrade those derived values.

## Bootstrap admission

The enforcement workflow does not exist on the protected base before the bootstrap merge. Therefore the bootstrap pull request cannot honestly produce its own `routing-enforcement` required check and must not pretend otherwise.

The bootstrap sequence is:

1. validate the exact candidate with the existing protected policy and security checks;
2. obtain the required independent exact-head review and authorized disposition;
3. merge the exact reviewed bootstrap candidate through the existing protected pull-request route;
4. read back protected `main` and verify the registry, control record, tests, gate bytes, and enforcement workflow;
5. modify ruleset `17137624` through the authorized settings/bootstrap route so `routing-enforcement` is a strict required context while preserving all existing required contexts and zero bypass actors;
6. verify the complete ruleset readback;
7. execute a hostile candidate proving the required routing decision is outside candidate control;
8. close the bootstrap portion only after the hostile proof remains blocked from protected integration.

Failure to obtain an exact ruleset readback or to preserve the pre-existing contexts fails closed. Do not remove unrelated required checks to make the bootstrap convenient.

## Enforcement semantics after activation

For every ordinary pull request, protected-base `ghos-routing-enforcement.yml`:

1. checks out the protected base read-only;
2. checks out the candidate read-only;
3. requires the enforcement workflow to remain byte-identical to protected base;
4. requires the shared gate script to remain byte-identical to protected base;
5. verifies the protected gate SHA-256;
6. runs the protected gate against candidate workflow bytes and candidate routing records;
7. supplies no write credentials to candidate state and executes no candidate script.

Therefore an ordinary candidate cannot weaken its own routing gate by editing its validator, changing the shared gate, deleting a registry entry, adding an unregistered workflow, or declaring a weaker topology.

## Hostile acceptance proof

After the ruleset requires `routing-enforcement`, open an unmergeable hostile pull request that attempts at least the following:

- remove or alter `.github/workflows/ghos-routing-enforcement.yml`;
- alter or remove `.ghos-routing/workflows.json` coverage;
- add an unregistered scheduled or write-capable workflow;
- declare a weaker topology than the protected gate derives;
- alter `scripts/ghos_execution_routing_gate.py` through the ordinary candidate route.

Success requires that candidate-controlled checks may execute normally while `routing-enforcement` fails and protected integration remains blocked. Close the hostile PR without merge and record its exact head and failed check identity on #67.

## Shared-gate digest rotation

The current reference consumers, `grandchallenge/gcl-standards` and `grandchallenge/MATH-PROGRAMME`, check out `grandchallenge/.github@main` and then verify the gate SHA-256. That design fails closed if `.github/main` changes the gate, but it would also create an avoidable cross-repository outage during a legitimate gate upgrade.

Before changing shared gate bytes, migrate every active consumer to an immutable gate commit:

1. keep the current gate bytes unchanged;
2. in each consumer, replace the mutable `.github@main` gate checkout with exact commit `355e029735961c29bf194985f885b0bda08579be` while retaining SHA-256 `1c4f9d82b1817d69187f3d87efbe0f6e60dd617d51a8aa330b119d48d3c95a43`;
3. run exact-head policy, security, routing, and repository-specific checks;
4. obtain required review, merge, and protected readback in each consumer;
5. only then open a `.github` shared-gate upgrade PR;
6. compute and record the successor gate blob and SHA-256, run hostile/unit tests, and merge through the governed gate-upgrade route;
7. rotate each consumer independently to the successor exact gate commit plus successor digest;
8. retain the old exact gate commit as valid historical provenance; do not rewrite or delete it;
9. record the final consumer compatibility matrix on #67 and in `.ghos-routing/control.json`.

A gate-byte change must never require all consumers to follow a mutable branch to stay operational.

## Named classifier deviation

`gcl-project-sync.yml` performs organization Project mutation using `gh project item-add`. The currently protected gate does not lexically classify that operation as `WRITE_CAPABLE`.

This is a semantic completeness defect, but it does not presently downgrade topology: the same workflow already derives `PERSISTENT_CONTROLLER_REQUIRED` from scheduled autonomous wake, secret credential use, and opaque execution.

The defect is `GHOS-CLASSIFIER-PROJECT-MUTATION-001`. Close it only through the controlled shared-gate digest-rotation procedure above. The successor gate should classify Project mutation as `WRITE_CAPABLE` without weakening any existing feature or topology rule.

Do not close #67 as `GHOS_ROUTING_ENFORCED` until this deviation is closed or a later independently reviewed control decision explicitly changes the terminal criterion.

## Terminal readback

Phase 0 reaches `GHOS_ROUTING_ENFORCED` only when protected evidence shows all of the following simultaneously:

- exhaustive local workflow registry validates against protected workflow bytes;
- `routing-enforcement` exists on protected base and is required by the active main ruleset;
- strictness and all pre-existing required contexts are preserved;
- bypass actors remain empty;
- hostile candidate is blocked by routing enforcement;
- shared-gate consumers use immutable gate commit identities;
- `GHOS-CLASSIFIER-PROJECT-MUTATION-001` is closed;
- protected post-merge checks pass;
- #67 records the exact terminal protected head and evidence identities.

Until then, the correct state is an in-progress Phase 0 control-plane rollout, not estate conformance.
