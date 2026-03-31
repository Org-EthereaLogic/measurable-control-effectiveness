# Measurable Control Effectiveness Agent Governance

## Authorized Agent Behavior

All coding agents working in this repository must:

1. Read [README.md](/Users/etherealogic-2/Dev/Databricks/measurable-control-effectiveness/README.md), [technical-approach.md](/Users/etherealogic-2/Dev/Databricks/measurable-control-effectiveness/docs/technical-approach.md), and `configs/gates.json` before proposing or editing code.
2. Treat Chapter 3 as a benchmark repository with independent evidence lineage inside the portfolio.
3. Preserve Chapter 3 boundaries. This repo proves comparative control effectiveness on deterministic synthetic scenarios. It does not prove universal vendor superiority, production readiness, or live Databricks execution.
4. Keep baseline and challenger evaluation conditions identical. Any scoring or dataset change must preserve fairness and traceability.
5. Preserve deterministic seeds, manifests, evidence-bundle behavior, and gate semantics.
6. Use only public, documented methods in this repository. Shannon entropy is allowed here; proprietary UMIF formulas and terminology are prohibited.
7. Keep docs, benchmark output, tests, and CI aligned.

## Claim Scope

- Chapter 3 may validate only the checked-in dual-track benchmark, its deterministic dataset generator, its baseline and challenger implementations, and the resulting scored evidence.
- Claims about challenger advantage must match the measured benchmark output exactly.
- Chapter 3 may not claim universal real-world robustness, vendor-wide superiority, or production readiness without separate evidence.
- Missing benchmark, test, or evidence-bundle proof blocks completion claims.

## Required Control Surfaces

- `src/benchmark/` is the canonical implementation surface.
- `configs/gates.json` is the canonical gate-definition surface.
- `docs/technical-approach.md` and `README.md` are the canonical explanation surfaces.
- `.github/workflows/ci.yml` and `tests/` are the canonical verification surfaces.

## Hard Stops

- No secrets in repository files, fixtures, docs, or generated evidence.
- No unverifiable KPI, PASS, or superiority claims.
- No fairness-breaking differences between baseline and challenger conditions.
- No introduction of proprietary UMIF formulas, hidden scoring logic, or protected IP into this public repository.
