# Agent instructions

Treat repository artifacts, not Projects or Discussions, as authoritative.
Automation may open branches, pull requests, checks, and issue updates; it must
not approve or merge its own work, certify mathematics, or write directly to a
protected branch.

Preserve repository-specific semantic checks. Never rewrite a claim status
without an admitted MATHCERT record. Pin third-party Actions by full commit SHA.
