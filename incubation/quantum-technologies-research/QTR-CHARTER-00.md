# QTR-CHARTER-00 — Quantum Technologies Research Charter

Status: `candidate`

Version: `0.1.0`

Programme: `GCL Quantum Technologies Research (QTR)`

Target repository: `grandchallenge/QUANTUM-TECHNOLOGIES`

## 1. Mandate

QTR governs GCL research whose primary object is a quantum technology, quantum algorithm, quantum information primitive, quantum software system, quantum control method, quantum sensing protocol, or quantum hardware-facing resource claim.

QTR shall develop results that are:

- mathematically explicit;
- operationally reproducible;
- clear about access and oracle assumptions;
- explicit about classical preprocessing and comparison baselines;
- separated by evidence class;
- replayable from pinned source, software, environment, and data identities;
- promoted only through declared review gates.

## 2. Initial research thesis

The first lane studies the construction of useful signals for QSP and QSVT.

For a predicate

\[
f:D\subseteq\{0,1\}^n\to\{0,1\},
\]

QTR seeks an encoding family that turns each input into a scalar, matrix, projected unitary, reflection pair, walk, Hamiltonian, or block encoding. The relevant signal must place yes- and no-instances into separated readout regions while preserving efficient coherent access.

The operational target is

\[
x
\mapsto
\mathcal E_x
\mapsto
A_x
\mapsto
p^{(\mathrm{SV})}(A_x)
\mapsto
\widehat f(x),
\]

where the complete cost includes input access, state preparation, block encoding, polynomial degree, success amplification, readout, and fault-tolerant synthesis when claimed.

## 3. Formal research object

A signal candidate is the tuple

\[
\mathfrak S=
(D,f,\mathcal O,\mathcal E,A,\alpha,\eta,\rho,R_0,R_1,\Delta,p,\varepsilon,C,\mathcal P).
\]

The fields have the following meanings.

- `D`: promise domain.
- `f`: target predicate.
- `O`: locked input or data-access model.
- `E`: coherent construction procedure.
- `A_x`: scalar or operator-valued signal.
- `alpha`: normalization used by the encoding.
- `eta`: block-encoding or implementation error.
- `rho_x`: prepared state or subspace on which readout is defined.
- `R_0`, `R_1`: disjoint no/yes readout regions.
- `Delta`: certified separation margin between the regions.
- `p`: bounded polynomial or polynomial family used for discrimination.
- `epsilon`: target transformation and decision error.
- `C`: end-to-end resource account.
- `P`: provenance and replay record.

A smaller representation is not presumptively superior. A candidate is useful only when its total coherent-access and transformation cost is competitive.

## 4. Required properties

### 4.1 Semantic sufficiency

A candidate shall state and justify a readout map `r` such that

\[
f(x)=r(A_x,\rho_x)
\]

on the entire promise domain, or shall state an approximation and its error model.

A signal fails semantic sufficiency when two opposite-label inputs produce indistinguishable readout data under the declared readout.

### 4.2 Coherent accessibility

The construction shall state the exact oracle and data-loading assumptions. It shall count all calls needed to implement the signal oracle, block encoding, state preparation, reflections, inverses, controls, and uncomputation.

Classically computing the answer and then encoding it is prohibited as an algorithmic shortcut.

### 4.3 Separated readout

The candidate shall identify disjoint regions `R_0` and `R_1` and a positive margin

\[
\Delta=\operatorname{dist}(R_0,R_1)>0
\]

for the promised instances. Zero-gap or instance-dependent-gap candidates remain exploratory until an explicit complexity statement is supplied.

### 4.4 Polynomial transformability

The target polynomial shall satisfy the parity, degree, boundedness, and approximation conditions required by the selected QSP or QSVT convention. Numerical phase synthesis is not a proof of admissibility. Grid checks are diagnostic evidence only.

### 4.5 End-to-end advantage accounting

The cost ledger shall include at least

\[
C_{\mathrm{total}}=
C_{\mathrm{access}}+
C_{\mathrm{prepare}}+
d\,C_{\mathrm{signal}}+
C_{\mathrm{amplify}}+
C_{\mathrm{readout}}+
C_{\mathrm{fault\ tolerance}},
\]

with inapplicable terms marked explicitly. Classical preprocessing, memory models, precision, success probability, and comparison baselines shall be stated.

## 5. Evidence classes

Every claim shall carry exactly one primary evidence class.

- `definition`: a stipulated object or interface.
- `derivation`: a mathematical consequence not yet independently certified.
- `theorem_candidate`: a complete theorem and proof awaiting certification.
- `certified_mathematics`: admitted through the applicable GCL mathematics route.
- `reference_implementation`: executable code intended to match a stated definition.
- `simulation_evidence`: numerical evidence from a classical simulator.
- `resource_estimate`: logical or physical resource projection under declared assumptions.
- `hardware_evidence`: results from identified hardware with calibration and uncertainty records.
- `negative_result`: a replayable failure, obstruction, lower bound, or falsification.

No evidence class promotes automatically into another.

## 6. Claim boundaries

The following language is prohibited unless the corresponding gate is complete.

- “Quantum advantage” requires a declared comparison class and end-to-end cost model.
- “Efficient” requires an asymptotic statement and the access model.
- “Practical” requires concrete resource and platform assumptions.
- “Hardware validated” requires device and run identities.
- “QSVT implementation” requires an actual block-encoding and admissible phase sequence, not only a polynomial plot.
- “Novel” requires a theorem-level or mechanism-level prior-art audit.

## 7. Programme architecture

QTR shall maintain the following ledgers.

1. `PROBLEM_REGISTRY`: governed research questions and promise domains.
2. `ORACLE_REGISTRY`: exact access models and equivalence records.
3. `SIGNAL_REGISTRY`: scalar and operator-valued candidates.
4. `POLYNOMIAL_REGISTRY`: target polynomials, admissibility records, and phase identities.
5. `IMPLEMENTATION_REGISTRY`: code, compiler, circuit, and environment identities.
6. `EVIDENCE_REGISTRY`: simulations, hardware runs, and negative results.
7. `CLAIM_REGISTRY`: claim text, evidence class, dependencies, and disposition.
8. `DECISION_REGISTRY`: ADRs and promotion decisions.

## 8. Work-package sequence

- `QTR-SIG-WP00`: governed signal-discovery substrate.
- `QTR-SIG-WP01`: symmetry quotient and invariant-coordinate atlas.
- `QTR-SIG-WP02`: witness, certificate, range, kernel, and singular-value linearization.
- `QTR-SIG-WP03`: adversary-SDP and span-program extraction on finite benchmarks.
- `QTR-SIG-WP04`: bounded-polynomial search, QSP admissibility, and phase synthesis.
- `QTR-SIG-WP05`: block-encoding and QSVT implementation audit.
- `QTR-SIG-WP06`: end-to-end resource and classical-baseline comparison.
- `QTR-SIG-WP07`: hardware-facing experiment design, only where justified.

WP01, WP02, and finite-instance WP03 may proceed after WP00 promotion. Claims of speedup, novelty, or hardware relevance remain gated through WP06 or WP07 as applicable.

## 9. Review roles

Each promoted package shall receive role-specific review.

- `Axiomatist`: locks domains, promises, norms, errors, and access assumptions.
- `Cartographer`: maps the candidate against known algorithms and representations.
- `Grammarian`: checks definitions, symbols, types, and terminology.
- `Verifier`: replays code, fixtures, schemas, and numerical identities.
- `Adversary`: searches for hidden preprocessing, vanishing gaps, bad overlaps, and misleading baselines.
- `Formalist`: identifies theorem obligations and suitable formalization boundaries.
- `Amanuensis`: maintains provenance, manifests, and stable records.
- `Referee`: determines promotion, rejection, revision, or termination.

## 10. Promotion ladder

A candidate progresses through the following states:

`proposed -> normalized -> executable -> verified -> adversarially_reviewed -> referee_promoted`.

The transition gates are:

- `G0 Oracle Lock`: exact input and access model.
- `G1 Semantic Gate`: proof or exhaustive finite-domain evidence of sufficiency.
- `G2 Encoding Gate`: executable coherent-access construction and complete cost account.
- `G3 Separation Gate`: certified or explicitly empirical readout gap.
- `G4 Polynomial Gate`: bounded approximation and admissibility record.
- `G5 Replay Gate`: deterministic fixtures and pinned environment.
- `G6 Comparative Gate`: appropriate classical and quantum baselines.
- `G7 Review Gate`: all required role dispositions.

Failure at any gate fails closed. Negative results are retained.

## 11. Initial benchmark suite

The first benchmark family shall contain:

- OR and promised OR;
- threshold and majority with explicit margin promises;
- parity as an access-cost control;
- exact-weight and interval predicates as oscillation controls;
- formula evaluation for composition tests;
- graph `s-t` connectivity for witness/span-program tests;
- linear-system consistency for range/kernel tests.

The suite is diagnostic, not a leaderboard. It is designed to expose whether a method discovers genuine coherent structure or merely compresses an already-computed answer.

## 12. Adoption and migration

This charter becomes binding only after:

1. creation of `grandchallenge/QUANTUM-TECHNOLOGIES`;
2. migration with byte and SHA-256 identities;
3. repository-level review and CI replay;
4. programme adoption through the applicable GCL authority process;
5. pinning of the adopted charter revision.

Until then, its status remains `candidate`.
