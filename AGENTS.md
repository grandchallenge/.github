# Agent instructions

**Engineering architecture and reliability:** Adopt [GCL-ENGINEERING-001 v1.0.0](https://github.com/grandchallenge/gcl-standards/blob/2a3cfed9419ba9b74eeaaee70b9db8c3f47f3c9b/standards/GCL-ENGINEERING-001.md), pinned at protected `gcl-standards` commit `2a3cfed9419ba9b74eeaaee70b9db8c3f47f3c9b`. Engineering agents own architecture, necessity, integration, tests, deploy/readback and retirement; reuse GitHub and existing components before inventing infrastructure. Do not duplicate workflow authority or mistake CI/merge for live completion. Preserve this repository's superior, reserved, and domain-specific policies. Cross-repository adoption requires explicit readback, never assumption.

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

## Binding CHAD-local Lean placement

Apply the Human Steward's 2026-11-24 placement instruction in [MATH-PROGRAMME AGENTS.md](https://github.com/grandchallenge/MATH-PROGRAMME/blob/97d0f0d4b5aee119e4002778ecb870b66955aea9/AGENTS.md), reaffirmed 2026-11-25, to all new CHAD-local Lean development, scratch checks, replay preparation and bounded Lake builds. Before each local build use `~/.local/bin/gcl-lean-work status`, stage an exact source revision with `gcl-lean-work stage REPO EXACT_COMMIT PROJECT_SUBDIR NAME` (or `new NAME TOOLCHAIN` for scratch), seed only exact locked dependencies, and invoke `gcl-lean-work run NAME lean|lake ...`. Verify the resolved source, build, package, compiler, cache and temporary paths use the dedicated native ext4 NVMe-backed `/mnt/gcl-lean-work` or `/mnt/gcl-lean-ssd` volumes; do not merely move the compiler. Preserve exact toolchain/dependency pins, workspace isolation and capacity reserve. Existing HDD worktrees may remain for Git custody, not local compilation. On placement, mount or capacity failure, recover the SSD environment or use an authorized alternate runner; no silent HDD fallback and no bypass via absolute compiler paths. Record placement in local execution receipts. Do not remove other workers' active workspaces. This requirement does not alter protected review, evidence or certification gates.
