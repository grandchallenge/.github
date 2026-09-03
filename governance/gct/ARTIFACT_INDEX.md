# GCT Executive Artifact Index

This index defines the minimum public-safe artifact spine. Sensitive source records remain outside public GitHub; this repository may retain only public-safe metadata, references, hashes, status, and review-routing information.

| Artifact | Owner | Purpose | Update trigger | Public-safe default |
| --- | --- | --- | --- | --- |
| `ENTERPRISE_MISSION.md` | Founder/CEO | Stable enterprise purpose and non-negotiables | material mission change | yes, curated |
| `EXECUTIVE_PRIORITIES.md` | GCT-COO | Current bounded enterprise priorities | priority change | yes if scrubbed |
| `PORTFOLIO_REGISTER.md` | GCT-COO + GCT-CPO | Current programme/venture dispositions | material programme change | yes, claim-safe projection |
| `TECHNOLOGY_PORTFOLIO.md` | GCT-CTO | Technical capabilities, dependencies, leverage | architecture/capability change | selected projection |
| `RESEARCH_PORTFOLIO.md` | GCT-CSO | Grand questions, active hypotheses, evidence gaps | research decision | selected projection |
| `PRODUCT_VENTURE_PORTFOLIO.md` | GCT-CPO | Product and venture options | productization decision | selected projection |
| `ENTERPRISE_RISK_REGISTER.md` | GCT-CTA | Material risks and controls | risk change | no; public projection only |
| `PUBLIC_CLAIM_REGISTER.md` | GCT-CTA | Claims GCT/GCL may state publicly and support | public claim change | yes |
| `OPPORTUNITY_PIPELINE.md` | GCT-CCP | External opportunities and status | opportunity change | no |
| `PROFESSIONAL_REVIEW_QUEUE.md` | GCT-FLO | Questions/actions needing counsel, accountant, tax, IP, etc. | item change | no |
| `CORPORATE_CALENDAR.md` | GCT-FLO | Filing/review/renewal metadata | deadline change | no |
| `CAPABILITY_MAP.md` | GCT-PCO | Human/agent capability and gaps | capability change | no/selected |
| `DECISION_QUEUE.md` | GCT-COO | Founder-reserved pending decisions | decision state change | no |
| `MANDATE_REGISTER.md` | GCT-COO | GCT→GCL mandates and return status | mandate transition | public projection allowed |
| `EXCEPTION_REGISTER.md` | GCT-CTA | Temporary deviations, expiry, controls | exception transition | selected projection |

## Artifact contract

Every executive artifact SHOULD state:

- owner office;
- authority class (`CORPORATE`, `EXECUTIVE_ADVISORY`, `GCL_GOVERNED`, `PROGRAMME_EVIDENCE`, `PUBLIC_PROJECTION`, `PRIVATE_REFERENCE`);
- source-of-truth location;
- last material update;
- update trigger;
- dependencies;
- public/private class;
- retirement or supersession rule.

## Anti-sprawl rule

Do not create an artifact because an agent can. Create or retain one only when it performs at least one of these functions:

1. controls authority;
2. records a decision;
3. routes work;
4. preserves evidence or provenance;
5. exposes risk;
6. maintains institutional memory;
7. supports a public interface;
8. reduces repeated Founder or reviewer effort.

If an artifact does none of these, fold it into an existing artifact or retire it.
