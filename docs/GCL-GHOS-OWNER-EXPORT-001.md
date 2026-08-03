# GCL-GHOS owner settings export

Operation: `GCL-GHOS-READBACK-GAP-001`

This package closes the collection gap recorded in `grandchallenge/.github#38`
without increasing the Council Clerk GitHub App permissions.

The collector performs `GET` requests only. It requires an authenticated
organization owner/admin and refuses incomplete, denied, duplicated, malformed,
or inferred results.

## Plan-tier disposition

GitHub Free does not expose organization-level repository rulesets. The
collector accepts `plan_unavailable` only when the organization ruleset list
returns HTTP `403` with this exact payload:

```json
{
  "message": "Upgrade to GitHub Team to enable this feature.",
  "documentation_url": "https://docs.github.com/rest/orgs/rules#get-all-organization-repository-rulesets",
  "status": "403"
}
```

Any other organization-ruleset `403` remains blocking.

When organization rulesets are `plan_unavailable`, repository ruleset lists and
every listed ruleset detail are mandatory for all 12 governed repositories.
Repository ruleset omission, denial, malformed content, duplicate identities,
or list/detail mismatch is blocking.

## Run

Use an existing GitHub CLI owner session with `admin:org`:

```bash
export GH_TOKEN="$(gh auth token)"
python scripts/gcl_ghos_owner_export.py \
  --output GCL-GHOS-OWNER-EXPORT-001.json
```

The command writes:

- `GCL-GHOS-OWNER-EXPORT-001.json`;
- `GCL-GHOS-OWNER-EXPORT-001.json.sha256`.

The export covers:

- organization Actions permissions;
- organization default workflow permissions;
- organization rulesets, or the exact `plan_unavailable` record;
- repository ruleset lists and every listed rule detail for all 12 repositories;
- legacy `main` branch protection;
- repository Actions permissions;
- repository default workflow permissions;
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
Every repository ruleset list and detail endpoint must return `200`.

## Validate

```bash
python scripts/gcl_ghos_owner_export.py \
  --validate GCL-GHOS-OWNER-EXPORT-001.json
```

The export schema version is `1.1.0`.

## Admission sequence

1. Merge `GCL-GHOS-OWNER-EXPORT-PLAN-CURE-001`.
2. Run the corrected collector from an organization-owner session.
3. Record the JSON and digest on a dedicated evidence branch.
4. Obtain independent non-author review.
5. Admit the exact export through protected merge.
6. Update `grandchallenge/gcl-standards` campaign issue #22 and the deviation
   ledger in a separate PR.
7. Do not claim organization-wide conformance until all P1 rows are closed and
   a post-repair reread is admitted.

This operation is read-only. It does not change organization or repository
settings and does not authorize mathematical, certification, novelty,
deployment, product, or commercial claims.
