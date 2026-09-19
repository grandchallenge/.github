# Agent instructions

Treat repository artifacts, not Projects or Discussions, as authoritative.

`GCL-AGENT-STAFFING-001` version `1.0.0` governs agent staffing under protected
INTELLECT authority commit `7e01dc6b1be46171f0cba5e140ca881f6ab2f50f`
and protected gcl-standards admission commit
`94e94ddf2d4158494c084d0acaff04009971c16c`.

One Codex system may implement and staff multiple
non-reserved council roles through distinct, role-scoped logical audit passes.
Separation requires a unique `logical_pass_id`, exact subject and evidence,
role-specific criteria and finding, and `non_authoring_read_only` mode when the
authoring system later acts as Adversary or Referee. It does not intrinsically
require a different agent, invocation, task, model, account, human, or generic
approval click. Routine and non-reserved substantive work may proceed through
protected merge and readback when the applicable evidence gates pass.

For authorized GitHub operations, follow the canonical GCL GitHub execution
transport invariant in protected `grandchallenge/INTELLECT` at
`governance/handoffs/README.md`. Use the connected GitHub action when it exposes
the required capability. A missing connector endpoint is not, by itself, an
authority boundary: use authenticated `gh`/GitHub API execution directly when
available. If direct CLI/API execution is unavailable in the current
environment, provide one complete self-contained `gh`/bash script that validates
prerequisites and live state, performs the authorized mutation, and reads back
the result. Do not send the operator to the GitHub UI solely because the
connector lacks an endpoint when `gh` or the GitHub API can express the
operation. Fallback scripts must preserve the caller's interactive shell and
must not use parent-shell `set -e`, `exit`, `kill`, `exec`, or terminating traps
as control flow. Transport fallback never weakens protection, evidence, or
authority boundaries.

Automation must not manufacture a Human Steward decision, certify mathematics
from its own sole construction or verification evidence, exercise a reserved
power, bypass protection, or write directly to a protected branch.

For a reserved decision, automation may assemble one exact-commit packet,
publish the consolidated attestation text, validate signer eligibility, record
the decision, and execute it mechanically. It must never create the decision or
infer approval from presence, assignment, silence, or a generic comment.

Preserve repository-specific semantic checks. Never rewrite a claim status
without an admitted MATHCERT record. Pin third-party Actions by full commit SHA.
