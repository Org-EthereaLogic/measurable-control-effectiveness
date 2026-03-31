# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-03-31

### Added

- Deterministic synthetic data generator with FaultProfile and DriftProfile injection
- Quality track: baseline (rule-based) and challenger (distribution-aware) detectors
- Drift track: baseline (proportion-based) and challenger (entropy + windowed trend) detectors
- Ground-truth scoring: precision, recall, F1 for quality; sensitivity, FPR for drift
- 10-gate evaluation framework with JSON-configurable thresholds
- Structured JSON evidence bundle writer
- CLI benchmark runner with --seed and --rows parameters
- Verified benchmark output: all 10 gates PASS, overall verdict PASS
- Challenger wins on quality (recall 1.0 vs baseline 0.88), gradual drift (1.0 vs baseline 1.0), and new category detection (1.0 vs baseline 0.0)
- CI workflow with pytest, ruff, Codacy, Codecov, Snyk, and benchmark smoke test
- Technical approach documentation with architecture, scoring methodology, and gate definitions
- 37 passing tests across datasets, quality, drift, and integration
