# GCL-GHOS owner settings export

Operation: `GCL-GHOS-READBACK-GAP-001`

This package closes the collection gap recorded in `grandchallenge/.github#38`
without increasing the Council Clerk GitHub App permissions.

The collector performs `GET` requests only. It requires an authenticated
organization owner/admin and refuses incomplete, denied, duplicated, or
inferred results.

## Run

Use an existing GitHub CLI owner session:

```bash
export GH_TOKEN="$(gh auth token)"
python scripts/gcl_ghos_owner_export.py \
  --output GCL-GHOS-OWNER-EXPORT-001.json
```

The command writes:

- `GCL-GHOS-OWNER-EXPORT-001.json`;
- `GCL-GHOS-OWNER-EXPORT-001.json.sha256`.

The export covers organization Actions permissions, organization workflow
permissions, organization rulesets and details, and the following settings for
all 12 current repositories:

- legacy `main` branch protection;
- Actions permissions;
- default workflow permissions;
- vulnerability alerts;
- Dependabot security updates;
- CodeQL default setup.

The collector treats documented negative responses as evidence only when
repository metadata in the same run proves admin access. It accepts:

- `404` for absent legacy branch protection;
- `204` or `404` for vulnerability alerts;
- `200` or `404` for Dependabot security updates;
- `200`, `403`, or `404` for CodeQL default setup.

Every organization and repository Actions endpoint must return `200`.
Organization ruleset list/detail identities must match exactly.

## Validate

```bash
python scripts/gcl_ghos_owner_export.py \
  --validate GCL-GHOS-OWNER-EXPORT-001.json
```

## Admission sequence

1. Run the collector from an organization-owner session.
2. Record the JSON and digest on a dedicated evidence branch.
3. Obtain independent non-author review.
4. Admit the exact export through protected merge.
5. Update `grandchallenge/gcl-standards` campaign issue #22 and deviation
   ledger in a separate PR.
6. Do not claim organization-wide conformance until all P1 rows are closed and
   a post-repair reread is admitted.

This operation is read-only. It does not change organization or repository
settings and does not authorize mathematical, certification, novelty,
deployment, product, or commercial claims.
