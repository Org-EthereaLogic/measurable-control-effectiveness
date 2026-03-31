# Measurable Control Effectiveness Directives

These directives are enforceable rules for humans and agents working in this repository.

## CRITICAL

- **No placeholders**: do not add TODO, FIXME, TBD, XXX, or template brackets.
- **No secrets**: never commit credentials, tokens, passwords, or private endpoints.
- **No hidden dependencies**: implementation and verification dependencies must be explicit in repo-managed config or docs.
- **No claim inflation**: README and docs must not say the benchmark proves more than the measured output supports.
- **No benchmark unfairness**: baseline and challenger must run on identical data, seeds, and scoring conditions.
- **No destructive artifact mutation**: do not rewrite evidence bundles or generated artifacts to conceal failures.
- **Public-method discipline**: Shannon entropy and other public methods are allowed. UMIF or other proprietary formulas are prohibited.

## IMPORTANT

- `configs/gates.json` is the source of truth for gate thresholds.
- Ground-truth scoring must stay traceable to the synthetic manifest.
- Docs must distinguish measured benchmark results from broader interpretation.
- Deterministic seeds and synthetic scenario definitions must remain reproducible.

## RECOMMENDED

- Add tests for any new benchmark scenario, scoring rule, or gate.
- Keep evidence output structured and append-only when generated.

## Verification Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000 --evidence-dir runs/
```
