# Steward-supervised agent constitutional review

The Council Clerk converts a cross-repository constitutional proposal into one
immutable review packet, two structured agent findings, and one Human Steward
attestation.

## Staffing

`GI-STEWARD-0001` establishes the temporary bootstrap staffing mode:

- the Adversary is a non-author agent with a recorded identity and session;
- the Referee is a different non-author agent with a different session; and
- `fyremael` is the sole Human Steward.

Additional human reviewers are not required while the directive is effective.
The staffing change does not reduce any office obligation.

## Human effort

The Human Steward reads the exact packet and both agent findings, then reacts
👍 to the Human Steward attestation. The reaction is accepted only on the
attestation for the current packet digest. Blocking findings are written as
ordinary PR comments instead of signing.

## Agent findings

Each finding records the office, agent identity, invocation or session,
subject digest, obligations, findings, evidence, residual uncertainty,
timestamp, and durable record URL. The Adversary and Referee records are added
to the campaign configuration through reviewed repository changes.

The Clerk rejects a proposal author, duplicate agent identity, duplicate
session, stale subject digest, missing obligations, or missing evidence.

## What the Clerk automates

For every configured subject PR, the Clerk:

- resolves the live head and base commits;
- records changed paths and completed check conclusions;
- verifies campaign-specific required and forbidden paths;
- produces canonical subject and packet SHA-256 digests;
- posts one packet and the Human Steward attestation;
- rejects stale agent findings and reactions after any subject commit changes;
- rejects bots, non-stewards, ineligible Steward actions, and invalid agent
  separation;
- rejects a Steward whose latest PR review requests changes;
- creates a machine-readable receipt after both valid agent findings and the
  Human Steward authorization; and
- opens a receipt issue carrying the encoded record for an Amanuensis
  activation PR.

Automation never reacts, approves, merges, ratifies, or changes a claim. The
receipt issue is evidence awaiting repository admission; it is not itself
constitutional activation.

## Staleness and revision

The subject digest binds exact PR heads and check conclusions for agent
findings. The packet digest additionally binds those admitted findings. A new
subject commit invalidates the findings and creates a new Steward attestation.
Older records remain visible for audit but cannot satisfy the current campaign.

## Current campaign

`governance/review-campaigns/GI-AMEND-0001.json` binds:

- `grandchallenge/INTELLECT#14`;
- `grandchallenge/gcl-standards#13`;
- `fyremael` as the Human Steward; and
- pending non-author agent Adversary and Referee finding slots.

Human onboarding remains intended but is not a campaign activation gate while
`GI-STEWARD-0001` is effective.
