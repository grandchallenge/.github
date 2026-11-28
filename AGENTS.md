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

## Open research execution and disclosure

For the Steward's authorized public research, use ordinary authenticated CONTROL Bash with the first-line public research designation described in [MATH-PROGRAMME's protected worker instructions](https://github.com/grandchallenge/MATH-PROGRAMME/blob/a7441fcc66ccd140bea0abe02a774142a3315bc5/AGENTS.md#public-research-execution-existing-control-lane) and [CONTROL's admitted native research contract](https://github.com/grandchallenge/CONTROL/blob/233013a2c2afeb9768320181b1ca5ea06bb041af/docs/PUBLIC_CONTROL_DISCLOSURE.md#native-public-research-ordinary-bash). Use the actual owning public repository and exact public commit, within the four admitted repositories. Execute once in the governed environment. No special runner or separate release submission is required. The caller declares its own command and output public; do not designate administration, credentials, third-party private records or unknown inputs/output. Preserve task custody, compute placement, dependency and certification requirements. No new authentication requirement for external workers. Verify actual correlated disclosure when practical, preserve durable full evidence and continue authorized work if publication fails.

For publishable research, annotate the existing native research command with the [live research thread convention](https://github.com/grandchallenge/grandchallenge.github.io/blob/1139be5a66a1e5111adcbe5c871cd5d4db7ece1b/README.md#live-research-console): contiguous `# GCL_THREAD:`, `# GCL_TITLE:`, `# GCL_OBJECTIVE:`, `# GCL_RESEARCH:` and `# GCL_EXECUTE:` comments immediately after the public designation. Reuse the stable thread ID for the investigation. Where supported by the actual result, emit `GCL_FINDING:`, `GCL_NEXT:` or `GCL_BLOCKER:` statements as captured output of the existing operation. These are public researcher statements, not certification or hidden reasoning. Never fabricate findings, add separate shell invocations solely for narration, or weaken the existing disclosure boundary. Continue the research if the public feed is unavailable.


## Binding open research doctrine (Human Steward, 2026-11-27)

Grand Challenge Labs is an open research institution. Openness is the default;
withholding is the exception and requires a concrete justification. Publish
the actual research question, mathematical argument, source, experimental or
compiler result, negative result, and unresolved obligation in the ordinary
course of authorized work. Scientific review or certification is not a
prerequisite for public scrutiny; distinguish candidates, observations and
conjectures from established or certified results. Do not require a separate
human release approval, repeat research for the console, or manufacture
narration or findings.

Use the existing CONTROL research publication and public repository evidence
lanes. Automatic release of independently verified public source and committed
research candidates needs no worker opt-in. For ordinary computational work
whose output cannot be independently obtained from public sources, exercise the
existing public research designation as the default for known publishable
work, with the actual owning repository and exact public revision. Preserve
complete evidence in the ordinary durable research return. A failed check is
research, not a reason to conceal it.

Withhold only material subject to a specific security/privacy, third-party
rights, unverified source/capture, or actual delivery boundary. Protect concrete
credentials, private records and sensitive administration; do not suppress
mathematical terms, failed approaches or provisional findings merely as a
precaution. A privileged shell is not automatically a public research scope.
No blanket disclosure of private journals, credentials or unknown data is
authorized. Preserve the exact assignment, custody, compute and scientific
certification gates; publication must not become a new research gate.
