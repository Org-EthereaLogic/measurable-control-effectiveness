# Constitution for Measurable Control Effectiveness

This constitution defines the governing principles for this Chapter 3 repository.

## Scope

It applies to:

- synthetic dataset generation and controlled fault/drift injection,
- baseline and challenger detector implementations,
- ground-truth scoring, gate evaluation, and evidence-bundle generation,
- docs, tests, CI, and governance artifacts.

## Required Decision Order

When principles conflict, resolve them in this order:

1. Safety and correctness.
2. Evidence traceability and benchmark fairness.
3. Security and secret hygiene.
4. Simplicity and proportionality.
5. Reproducibility and operational reliability.
6. Performance and speed.

## Governing Principles

### P1. Safety, Correctness, and Repository Integrity

- Never ship a change that knowingly violates acceptance criteria, policy boundaries, or repository integrity.
- Prefer explicit failure over silent unsafe behavior.
- Treat benchmark fairness, scoring logic, and chapter scope boundaries as hard constraints.

### P2. Evidence Traceability and Benchmark Fairness

- Every precision, recall, sensitivity, FPR, and gate-verdict claim must map to concrete evidence.
- Reports and docs must distinguish measured facts from interpretation.
- Missing evidence blocks completion claims.
- Baseline and challenger must be evaluated under identical conditions.

### P3. Security and Secret Hygiene

- No credentials, tokens, or secret material in repository content or committed artifacts.
- Treat secret exposure as a hard failure.

### P4. Simplicity and Proportionality

- Match implementation complexity to the size and risk of the benchmark problem.
- Prefer direct, explainable detector and scoring logic over speculative framework layers.
- Avoid adding infrastructure or vendor coupling not required by the benchmark.

### P5. Reproducibility and Operational Reliability

- Capture seeds, dataset sizes, score outputs, and gate results for every benchmark run.
- Keep synthetic scenarios deterministic and evidence bundles audit-friendly.
- Build workflows so another operator can replay the result or explain why it cannot be replayed.

### P6. Public Method Discipline

- This public repository may use standard public techniques and terminology.
- Shannon entropy is an approved public method in this project.
- Proprietary UMIF formulas, internal scoring logic, or protected IP are prohibited.

### P7. Chapter Scope Discipline

- Chapter 3 proves comparative control effectiveness on the checked-in synthetic benchmark only.
- It does not prove universal real-world robustness, production readiness, or undisclosed proprietary superiority.
- Do not widen claim scope beyond what the checked-in evidence supports.

## Related Documents

- `DIRECTIVES.md` defines enforceable repository rules.
- `AGENTS.md` defines operating behavior for coding agents.
- `SECURITY.md` defines the security policy.
- `README.md` and `docs/technical-approach.md` define the chapter contract and evidence narrative.
