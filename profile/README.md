# Grand Challenge Labs

Open research in mathematics, machine intelligence, scientific computing, and autonomous research systems.

> **Questions become programmes. Programmes produce evidence. What survives scrutiny becomes knowledge.**

Grand Challenge Labs builds executable research systems for turning difficult questions into evidence that can survive independent scrutiny.

[Research](https://github.com/orgs/grandchallenge/repositories) · [Mathematics Programme](https://grandchallenge.github.io/MATH-PROGRAMME/) · [Programme Atlas](https://grandchallenge.github.io/MATH-PROGRAMME/PROGRAMME_ATLAS/) · [Discussions](https://github.com/orgs/grandchallenge/discussions)

---

## Research frontiers

| Frontier | Programme |
|---|---|
| **Can neural systems phase-lock useful computational modes while suppressing error modes?** | Coupling-Phase Spectroscopy; collective neural computation; spectral dynamics |
| **When does sparse expert routing undergo genuine oscillatory instability rather than ordinary expert collapse?** | MoE flutter boundaries; bifurcation analysis; continuation experiments |
| **Can mathematical discovery become an auditable computational process?** | MATHFORGE → MATHSOLVE → MATHCERT |
| **How should learning systems remain capable under stress rather than merely stable at nominal conditions?** | Antifragile training; recovery dynamics; reserve and robustness |

These are active research questions, not promoted claims. Evidence and claim status remain with the governed programme records that support them.

[Explore all research →](https://github.com/orgs/grandchallenge/repositories)

---

## Recently verified · OpenAI Ten Proofs

MATHCERT has independently rebuilt and Lean-kernel-checked the exact supplied
formalizations for all ten results advertised by
[`openai/ten-proofs`](https://github.com/openai/ten-proofs) at pinned commit
`94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6`.

| Checked surface | Result |
|---|---|
| Exact Lean source modules | **10 / 10 passed** |
| Advertised headline declarations | **12 / 12 kernel accepted** |
| Unexpected axioms | **0** |
| Independent review and protected replay | **Complete** |

[Read the public verification note →](https://grandchallenge.github.io/MATH-PROGRAMME/OPENAI_TEN_PROOFS_VERIFICATION/) · [Inspect the protected MATHCERT record →](https://github.com/grandchallenge/MATHCERT/blob/main/governance/corpus_verifications/OPENAI-TEN-PROOFS-001.json) · [Replay evidence →](https://github.com/grandchallenge/MATHCERT/actions/runs/34838818609)

The result is exact: it verifies the supplied Lean proofs and their formal
dependency graphs under the retained statement qualifications. It does not
claim line-by-line identity with the PDF exposition, novelty, or priority.

---

## How GCL works

| Stage | Discipline |
|---|---|
| **1. Frame the question** | State the conjecture, engineering objective, or scientific uncertainty precisely. |
| **2. Make it executable** | Build theory, experiments, datasets, software, proofs, and diagnostics. |
| **3. Attack the result** | Reproduce, review, falsify, verify, and establish the claim boundary. |
| **4. Publish what survives** | Promote only the evidence-supported result, with provenance attached. |

GitHub supplies the operational and evidentiary substrate; it does not itself confer mathematical or scientific authority.

<details>
<summary><strong>View the GCL operational architecture</strong></summary>

![Grand Challenge Labs GitHub surface: organization capabilities, core programme repositories, research and engineering repositories, governance and workflow, infrastructure and automation, knowledge and documentation, observability, external integrations, and the Polity vision.](assets/gcl-github-surface-2026-09-01.webp)

*Organization-surface illustration, September 2026. This is a navigational summary; protected, content-addressed records in governed repositories remain authoritative.*

</details>

---

## Research architecture

The repositories are parts of one research system. They do not all occupy the same layer.

```text
GRAND CHALLENGE LABS
│
├── Institutional stack
│   ├── INTELLECT ........ institutional reasoning, authority, and review
│   ├── AETHER ........... semantic coordination, provenance, and replay
│   └── gcl-standards .... shared technical and operating standards
│
├── Mathematics Programme
│   ├── MATH-PROGRAMME ... programme governance and map
│   ├── MATHFORGE ........ discover and reconstruct
│   ├── MATHSOLVE ........ organize and solve
│   └── MATHCERT ......... independently certify
│
├── Research programmes
│   ├── MODULUS .......... geometry-aware optimization and operator control
│   ├── RUNT ............. reversible normalized neural architectures
│   ├── CPS .............. collective neural computation and phase dynamics
│   └── other active scientific and engineering programmes
│
└── Research infrastructure
    ├── GLOSS ............ formal-to-natural semantics and loss accounting
    ├── TROVE-CURATA ..... governed data-curation programme; pre-activation
    └── tooling, CI, publication, and supporting automation
```

The conceptual stack is:

| Layer | Question | Representative systems |
|---|---|---|
| **Institution** | Why and under what epistemic rules does research happen? | Grand Challenge Labs |
| **Constitution** | Who may judge, authorize, review, and preserve decisions? | [INTELLECT](https://github.com/grandchallenge/INTELLECT) |
| **Semantic substrate** | What does the system know, from what evidence, and at what point in history? | [AETHER](https://github.com/grandchallenge/AETHER) |
| **Research machinery** | How is inquiry turned into a repeatable discovery, solving, and certification process? | [MATH-PROGRAMME](https://github.com/grandchallenge/MATH-PROGRAMME), [MATHFORGE](https://github.com/grandchallenge/MATHFORGE), [MATHSOLVE](https://github.com/grandchallenge/MATHSOLVE), [MATHCERT](https://github.com/grandchallenge/MATHCERT) |
| **Research programmes** | Which scientific and engineering questions are being attacked? | [MODULUS](https://github.com/grandchallenge/MODULUS), [RUNT](https://github.com/fyremael/RUNT), [CPS](https://github.com/fyremael/CPS), and other active programmes |
| **Research infrastructure** | Which specialist systems make the research process more reliable or legible? | [GLOSS](https://github.com/grandchallenge/GLOSS), [TROVE-CURATA](https://github.com/grandchallenge/TROVE-CURATA), [gcl-standards](https://github.com/grandchallenge/gcl-standards), CI and publication tooling |

In the mathematics programme, the epistemic pipeline is deliberately explicit:

```text
MATHFORGE  →  MATHSOLVE  →  MATHCERT
 discover      organize       certify
```

A source can motivate a claim. A computation can suggest a claim. A solving campaign can develop a claim. Certification is a separate act.

[Browse all repositories →](https://github.com/orgs/grandchallenge/repositories)

---

## Evidence, not ceremony

GCL research is designed to be inspectable rather than merely persuasive. Depending on the programme and claim class, evidence can include exact-head review, reproducible experiments, protected records, independent review, formal verification, explicit claim boundaries, immutable attestations, and post-merge readback.

[Three-pillar architecture](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/ARCHITECTURE_OVERVIEW.md) · [Certification ladder](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/CERTIFICATION_LADDER.md) · [Claim-boundary doctrine](https://github.com/grandchallenge/MATH-PROGRAMME/blob/main/docs/CLAIM_BOUNDARY_DOCTRINE.md) · [Standards](https://github.com/grandchallenge/gcl-standards)

<details>
<summary><strong>Current governed status</strong></summary>

- `GI-AMEND-0001` is effective under the protected [INTELLECT authority schedule](https://github.com/grandchallenge/INTELLECT/blob/main/governance/constitutional_authority_schedule.json).
- `GCL-GHOS-00` `0.2.0` is the admitted bounded-execution-continuity successor selected for the MATH-PROGRAMME pilot by [protected admission `87307a0c1fe5ff19b34bb08451e7d6281a7d5dea`](https://github.com/grandchallenge/gcl-standards/commit/87307a0c1fe5ff19b34bb08451e7d6281a7d5dea).
- MATH-PROGRAMME actively adopts that exact admission through [protected adoption `1a5e9cb24257be578b091ecd2c99d4119ff73b2c`](https://github.com/grandchallenge/gcl-standards/commit/1a5e9cb24257be578b091ecd2c99d4119ff73b2c), while retaining the `0.1.1` and `0.1.0` lineage as history.

Machine-readable activation, admission, and adoption records take precedence over descriptive documents. These statuses do not grant GitHub independent constitutional, mathematical, certification, production, deployment, novelty, or commercial authority.

</details>

---

## Enter the laboratory

Read the research. Reproduce an experiment. Challenge a result. Improve a proof. Build on what survives.

[Programme Atlas](https://grandchallenge.github.io/MATH-PROGRAMME/PROGRAMME_ATLAS/) · [Repositories](https://github.com/orgs/grandchallenge/repositories) · [Discussions](https://github.com/orgs/grandchallenge/discussions) · [Mathematics Programme](https://grandchallenge.github.io/MATH-PROGRAMME/)

**Grand Challenge Labs**  
Reproducible · Traceable · Governed · Open by default
