# QTR-SIG-WP00 — Governed Signal-Discovery Substrate

Status: `candidate`

Parent charter: `QTR-CHARTER-00`

## 1. Question

Given a Boolean predicate and a locked input oracle, how shall GCL discover, compare, reject, and promote low-dimensional or operator-valued signals for QSP and QSVT without hiding the cost of constructing the signal?

## 2. Scope

This work package establishes the contract and executable substrate. It does not claim a new quantum algorithm, QSP synthesis method, QSVT theorem, or quantum advantage.

In scope:

- scalar, amplitude, phase, singular-value, eigenvalue, projector-overlap, reflection, and walk signals;
- finite Boolean predicates and promise domains;
- semantic collision tests;
- readout-gap calculation;
- ordered-sign alternation lower bounds for scalar separators;
- declared oracle-query and construction costs;
- machine-readable candidate records;
- baseline positive and negative fixtures.

Out of scope:

- general-purpose optimal phase synthesis;
- fault-tolerant gate compilation;
- hardware execution;
- theorem-level novelty claims;
- replacement of adversary or approximate-degree lower bounds by heuristics.

## 3. Locked definitions

### 3.1 Predicate instance

A predicate instance is

\[
\mathfrak P=(n,D,f,\mathcal O),
\]

where `n` is input width, `D` is a finite promise domain, `f` is the Boolean label, and `O` is the exact access model.

The WP00 reference suite uses the bit-query oracle

\[
O_x|i,b\rangle=|i,b\oplus x_i\rangle
\]

as its accounting baseline. Candidate records may declare another model, but comparisons across models are prohibited unless a reduction is supplied.

### 3.2 Readout signature

A candidate maps each input to a finite real signature

\[
s(x)=(s_1(x),\ldots,s_k(x)).
\]

The signature may be a scalar, selected eigenvalues, selected singular values, principal-angle functions, or another explicitly declared observable. WP00 does not treat an unobserved full matrix as evidence of sufficiency.

### 3.3 Semantic collision

A cross-label semantic collision occurs when

\[
f(x)\neq f(y)
\quad\text{and}\quad
s(x)=s(y)
\]

under the declared numerical equivalence rule.

Zero cross-label collisions are necessary for exact finite-domain sufficiency. They are not sufficient for an efficient quantum algorithm.

### 3.4 Readout gap

For scalar signatures, the empirical finite-domain gap is

\[
\Delta_{\mathrm{emp}}
=
\min_{f(x)\neq f(y)}|s(x)-s(y)|.
\]

For vector signatures, WP00 uses Euclidean distance unless another metric is declared.

An empirical finite-domain gap is not a theorem about an asymptotic family.

### 3.5 Alternation lower bound

For scalar signatures, sort the distinct signal values and attach their labels. If labels alternate `a` times, any real polynomial whose sign realizes those labels at the sampled values has degree at least `a`.

This is a diagnostic lower bound. It does not equal approximate degree in general, and it does not include boundedness or approximation error.

### 3.6 Declared coherent-access cost

Each candidate shall declare a query-cost expression and a cost class. WP00 fixtures use exact integer query counts for fixed `n`.

A declared cost is an assertion until supported by a circuit or reduction.

## 4. Candidate acceptance contract

A registry record is structurally admissible only if it contains:

- stable candidate and predicate identifiers;
- input width and promise description;
- oracle model;
- signal type and mathematical definition;
- readout signature definition;
- normalization and error conventions;
- declared construction/query cost;
- expected yes/no regions or readout rule;
- evidence class and claim status;
- source and replay provenance;
- known limitations.

A candidate is WP00-executable when the reference evaluator can instantiate it and produce a deterministic report.

A candidate is WP00-verified when:

1. the schema and registry validation pass;
2. all tests pass;
3. the report is reproduced from a clean checkout;
4. declared expected collisions and gaps match the executable result;
5. an independent Verifier signs the replay record.

## 5. Baseline fixtures

### 5.1 OR through marked amplitude

For Hamming weight `w(x)`, define

\[
s_{\mathrm{OR}}(x)=\sqrt{w(x)/n}.
\]

This is the nonzero singular value of the normalized row operator

\[
M_x=\frac{1}{\sqrt n}[x_1\;\cdots\;x_n].
\]

It separates `w=0` from `w\ge 1` by the finite-instance gap `1/sqrt(n)`. The operator interpretation exposes the singular-value threshold used by amplitude amplification or QSVT filtering.

### 5.2 Majority through normalized Hamming signal

Define

\[
s_{\mathrm{maj}}(x)=2w(x)/n-1.
\]

On an explicit margin promise `|s| >= Delta`, majority becomes a sign classifier. Without the promise, the minimum gap shrinks with `n`; the candidate record must not hide this scaling.

### 5.3 Parity phase control

Define

\[
s_{\oplus}(x)=(-1)^{w(x)}.
\]

This signal has two points and a constant label gap. However, under the bit-query oracle its exact construction requires all `n` bits in the worst case. It is admitted as a negative-control fixture:

\[
\text{low signal dimension}\not\Rightarrow\text{low coherent-access cost}.
\]

### 5.4 Hamming scalar applied to parity

Apply `s(x)=2w(x)/n-1` to parity. The labels alternate at every consecutive Hamming weight, producing an alternation lower bound of `n`. This fixture tests whether the evaluator exposes polynomial oscillation rather than reporting only semantic sufficiency.

## 6. Candidate scorecard

WP00 reports, but does not canonize, the following quantities:

- `cross_label_collisions`;
- `semantic_sufficient_on_domain`;
- `empirical_gap`;
- `distinct_signal_count`;
- `alternation_degree_lower_bound` for scalar signatures;
- `declared_query_cost`;
- `dimension`;
- `utility_index`.

The provisional utility index is

\[
U=\frac{\Delta_{\mathrm{emp}}}
{(1+C_{\mathrm{query}})(1+a)(1+\log_2(1+k))},
\]

where `a` is the alternation lower bound and `k` is signature dimension.

`U` is a triage heuristic only. It shall never be presented as quantum query complexity, advantage, or an invariant ranking across oracle models.

## 7. Required executable outputs

The reference evaluator shall emit a deterministic JSON report containing:

- predicate and candidate identifiers;
- enumerated domain size;
- all scorecard quantities;
- collision witnesses, if any;
- ordered scalar labels, when applicable;
- evaluator version;
- a SHA-256 digest of the canonical report payload.

The validator shall fail closed for:

- missing required registry fields;
- duplicate identifiers;
- unknown predicate or implementation names;
- invalid evidence classes;
- nonpositive input width;
- inconsistent expected metrics;
- absent migration metadata.

## 8. Review obligations

### Axiomatist

Confirm that each predicate, promise, oracle model, norm, equality tolerance, and cost unit is explicit.

### Cartographer

Map each candidate to the appropriate family: symmetric statistic, amplitude encoding, witness operator, adversary/span program, walk, Hamiltonian, or Fourier/representation signal.

### Grammarian

Check that “signal,” “encoding,” “signature,” “gap,” “degree,” “query,” “simulation,” and “advantage” are not used interchangeably.

### Verifier

Replay the validator, unit tests, and reference reports. Confirm deterministic digests.

### Adversary

Attempt to break each candidate through cross-label collisions, vanishing margins, hidden classical preprocessing, low-overlap states, normalization inflation, numerical tolerance, and incompatible oracle comparisons.

### Formalist

Separate finite enumeration claims from asymptotic theorem obligations. Identify definitions suitable for Lean or another proof assistant without pretending the numerical evaluator is a proof.

### Amanuensis

Record file identities, source revisions, environment, commands, outputs, and migration identities.

### Referee

Promote WP00 only if the package establishes a trustworthy substrate and makes no unsupported algorithmic claim.

## 9. Promotion criteria

WP00 may be Referee-promoted when all conditions hold:

- [ ] charter and scope are accepted;
- [ ] schema and registry are valid;
- [ ] OR, majority, parity phase, and parity-on-Hamming fixtures execute;
- [ ] positive and negative tests pass;
- [ ] deterministic report digests are recorded;
- [ ] all eight role reviews are present;
- [ ] migration to the target repository is complete and identity-checked;
- [ ] no claim exceeds `reference_implementation` or `negative_result` without a separate route.

## 10. Authorized next work

After WP00 promotion:

- WP01 may build a symmetry and invariant atlas.
- WP02 may build witness/range/kernel operator candidates.
- finite-instance WP03 may solve adversary SDPs and inspect span-program geometry.

WP04 and later remain gated on candidate records that pass semantic, encoding, and separation review.
