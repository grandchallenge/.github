# Low-effort constitutional review

The Council Clerk converts a cross-repository constitutional proposal into one
immutable review packet and three role-bound attestations.

## Human effort

Each human reads the packet and performs one action:

1. the Adversary reacts 👍 to the Adversary attestation;
2. a different Referee reacts 👍 to the Referee attestation; and
3. an allowlisted Human Steward reacts 👍 to the Human Steward attestation.

The reaction is accepted only on the role-specific comment for the current
packet digest. The attestation text states the obligations being discharged.
Blocking findings are written as ordinary PR comments instead of signing.

## What the Clerk automates

For every configured subject PR, the Clerk:

- resolves the live head and base commits;
- records changed paths and completed check conclusions;
- verifies campaign-specific required and forbidden paths;
- produces a canonical SHA-256 packet digest;
- posts one packet and three role-specific attestations;
- rejects stale reactions after any subject commit changes;
- rejects bots, proposal authors, people without write access to every subject,
  non-stewards, and reuse of one person as both Adversary and Referee;
- rejects a signer whose latest PR review requests changes;
- creates a machine-readable receipt after all three valid attestations; and
- opens a receipt issue carrying the encoded record for an Amanuensis
  activation PR.

Automation never reacts, approves, merges, ratifies, or changes a claim. The
receipt issue is evidence awaiting repository admission; it is not itself
constitutional activation.

## Staleness and revision

The packet digest binds both exact PR heads and their check conclusions. A new
commit creates new attestation comments. Reactions on an older packet remain
visible for audit but cannot satisfy the current campaign.

## Current campaign

`governance/review-campaigns/GI-AMEND-0001.json` binds:

- `grandchallenge/INTELLECT#13`;
- `grandchallenge/gcl-standards#10`; and
- `fyremael` as the Human Steward.

The two independent roles remain open to any distinct, non-author organization
members with write access to both subject repositories.
