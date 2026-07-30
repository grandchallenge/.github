# GCL Quantum Technologies Research

Status: `incubation`

Target authority repository: `grandchallenge/QUANTUM-TECHNOLOGIES`

Programme identifier: `QTR`

## Purpose

GCL Quantum Technologies Research develops auditable quantum algorithms, operator encodings, resource estimates, simulations, and experimental protocols. The programme separates mathematical validity, algorithmic correctness, resource claims, simulation evidence, and hardware evidence.

The first research lane formalizes the chain

\[
\text{Boolean predicate}
\rightarrow
\text{coherently accessible signal}
\rightarrow
\text{polynomial separator}
\rightarrow
\text{QSP synthesis}
\rightarrow
\text{QSVT execution}.
\]

The central problem is not merely to approximate a Boolean function by a polynomial. It is to discover a scalar or operator-valued signal that is:

1. semantically sufficient for the predicate;
2. coherently accessible in the locked oracle model;
3. separated by a usable spectral or singular-value gap;
4. compatible with a bounded low-degree polynomial transformation;
5. cheaper end-to-end than competing encodings.

## Authority boundary

This incubation packet is an organizational bootstrap artifact. It does not establish a new constitutional authority by itself. Until the target repository is created and the charter is adopted:

- `grandchallenge/.github` holds this packet only as an organization-level staging surface;
- mathematical statements remain subject to the applicable GCL mathematical certification route;
- algorithmic and resource claims remain candidate claims;
- simulations are evidence about implementations, not evidence of asymptotic quantum advantage;
- hardware claims require device, calibration, compiler, shot, and uncertainty records.

## Initial work package

`QTR-SIG-WP00` establishes the governed signal-discovery substrate. It includes:

- a formal signal-candidate contract;
- oracle, encoding, separation, polynomial, and readout gates;
- a machine-readable registry and schema;
- an executable reference evaluator;
- baseline fixtures for OR, majority, and parity;
- a staged programme from symmetry reduction through QSVT resource audit;
- role-specific review obligations.

The package deliberately includes parity. Its one-dimensional phase perfectly separates labels, but constructing that phase from a bit-query oracle costs all input bits. This fixture prevents the false inference that low signal dimension implies low coherent-access complexity.

## Files

- `QTR-CHARTER-00.md`: programme charter and authority model.
- `work-packages/QTR-SIG-WP00.md`: first governed research package.
- `schemas/signal-candidate.schema.json`: machine-readable candidate contract.
- `registry/signal-candidates.json`: admitted baseline candidate records.
- `reference/signal_discovery.py`: dependency-free evaluator.
- `tests/test_signal_discovery.py`: executable acceptance and failure fixtures.
- `ci/validate.py`: packet and registry validation.
- `MIGRATION_MANIFEST.json`: target repository migration contract.

## Validation

From this directory:

```bash
python ci/validate.py
python -m unittest discover -s tests -p "test_*.py"
python reference/signal_discovery.py
```

## Foundational sources

- Low and Chuang, *Optimal Hamiltonian Simulation by Quantum Signal Processing*, arXiv:1606.02685.
- Gilyén, Su, Low, and Wiebe, *Quantum Singular Value Transformation and Beyond*, arXiv:1806.01838.
- Reichardt, *Span Programs and Quantum Query Complexity*, arXiv:0904.2759.

These sources motivate the QSP/QSVT and adversary/span-program lanes. Their presence does not discharge theorem-level source comparison or novelty review for future GCL claims.
