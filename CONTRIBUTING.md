# Contributing

Thank you for your interest in this project. This repository is part of the
**Enterprise Data Trust** portfolio by Anthony Johnson / EthereaLogic LLC.

## Scope

This project implements a dual-track benchmark for measuring data control
effectiveness. Contributions should stay within that scope: improving
detectors, adding fault/drift scenarios, strengthening scoring, or improving
documentation.

## Development Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src pytest -q
ruff check src tests
```

## Running the benchmark

```bash
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000
```

## Pull Request Guidelines

1. All tests must pass.
2. New features must include tests.
3. Ruff must report zero issues.
4. Commit messages should follow conventional commit format.
