# Claude Code Instructions — Measurable Control Effectiveness

## Workspace Intent

This repository is Chapter 3 of the Enterprise Data Trust portfolio. It is a public, evidence-driven benchmark repository proving comparative control effectiveness on deterministic synthetic quality and drift scenarios with scored outputs and gate evaluation.

## Decision Order

1. `CLAUDE.md`
2. `CONSTITUTION.md`
3. `DIRECTIVES.md`
4. `AGENTS.md`
5. `SECURITY.md`
6. `README.md`
7. `docs/technical-approach.md`
8. `configs/gates.json`

## Non-Negotiable Rules

- Keep Chapter 3 claim-limited to the checked-in benchmark and its measured outputs.
- Keep baseline and challenger conditions identical.
- Shannon entropy is allowed and expected where the implementation uses it.
- Do not add proprietary UMIF formulas, hidden scoring logic, or protected IP terms.
- Do not claim universal superiority or production execution without separate evidence.

## Common Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000 --evidence-dir runs/
```

## What Exists Today

- `src/benchmark/datasets/` contains deterministic synthetic data generation and injection manifests.
- `src/benchmark/quality/` and `src/benchmark/drift/` contain baseline and challenger detectors.
- `src/benchmark/scoring/` contains ground-truth scoring.
- `src/benchmark/gates/` contains the 10-gate evaluation framework.
- `src/benchmark/evidence/` contains the JSON evidence-bundle writer.
- `tests/` contains 37 tests across datasets, quality, drift, scoring, and integration behavior.
- `.github/workflows/ci.yml` runs lint, tests, benchmark smoke, and security checks.

## What Does Not Exist Yet

- No benchmark evidence on production or customer data.
- No justification for universal vendor or platform claims beyond the checked-in synthetic scenarios.
- No live Databricks execution evidence in this repository.
