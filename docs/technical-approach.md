# Technical Approach — Measurable Control Effectiveness

Author: Anthony Johnson | EthereaLogic LLC

## Overview

This document describes the benchmark architecture, fault injection
methodology, scoring approach, and gate evaluation framework.

## Benchmark Architecture

```
┌─────────────────────────────────────┐
│  Synthetic Data Generator           │
│  (seed=42, n_rows=1000)             │
│                                     │
│  Outputs:                           │
│  • clean_df (baseline)              │
│  • faulted_df (quality faults)      │
│  • drifted_sudden_df                │
│  • drifted_gradual_df               │
│  • drifted_new_cat_df               │
│  • stable_df (FPR control)          │
│  • fault_manifest (ground truth)    │
│  • drift_manifest (ground truth)    │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│  Quality    │ │  Drift      │
│  Track      │ │  Track      │
│             │ │             │
│  Baseline:  │ │  Baseline:  │
│  rule-based │ │  proportion │
│  checks     │ │  difference │
│             │ │             │
│  Challenger:│ │  Challenger:│
│  distrib-   │ │  entropy +  │
│  aware      │ │  windowed   │
│  detection  │ │  trend      │
└──────┬──────┘ └──────┬──────┘
       │               │
       ▼               ▼
┌────────────────────────────────────┐
│  Ground-Truth Scoring              │
│  Quality: precision, recall, F1    │
│  Drift: sensitivity, FPR, combined │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  10-Gate Evaluation                │
│  5 quality gates + 5 drift gates   │
│  PASS / WARN / FAIL per gate       │
│  Overall verdict                   │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│  Evidence Bundle (JSON)            │
│  Structured, append-only,          │
│  audit-ready output                │
└────────────────────────────────────┘
```

## Fault Injection (Quality Track)

The `FaultProfile` controls four types of quality fault injection:

| Fault Type | Default Rate | Mechanism |
|-----------|-------------|-----------|
| Null injection | 5% per column | Selected rows in `customer_id` and `amount` set to null |
| Duplicate injection | 3% | Random rows appended as exact duplicates |
| Type error injection | 2% | Numeric `amount` values replaced with "INVALID" |
| Schema drop | 1 column | `priority` column removed entirely |

All injected faults are recorded in the `fault_manifest` with exact row
indices, enabling ground-truth scoring without heuristics.

## Drift Injection (Drift Track)

The `DriftProfile` controls three drift scenarios:

| Scenario | Mechanism | Detection Challenge |
|----------|-----------|-------------------|
| Sudden shift | Entire column collapsed to one value | Easy — large distribution change |
| Gradual drift | Progressive shift toward target value (linear probability) | Hard — small per-row change, cumulative effect |
| New category | Novel values injected into categorical column | Medium — requires reference comparison |

A fourth scenario (stable data from a different seed) measures the false
positive rate — drift should NOT be detected on structurally similar data.

## Scoring Methodology

**Quality scoring** compares detector output against the fault manifest:
- True positive: flagged row that was actually faulted
- False positive: flagged row that was clean
- False negative: faulted row that was not flagged
- Precision, recall, F1 computed from TP/FP/FN

**Drift scoring** evaluates each scenario independently:
- Sensitivity: did the detector flag the scenario as drifted?
- FPR: did the detector flag stable data as drifted?
- Combined score: mean sensitivity penalized by FPR

## Gate Definitions

The 10 gates are defined in `configs/gates.json`:

| # | Gate | Track | Type | Threshold |
|---|------|-------|------|-----------|
| 1 | quality_recall | Quality | FAIL | >= 0.90 |
| 2 | quality_precision | Quality | FAIL | >= 0.80 |
| 3 | quality_f1 | Quality | FAIL | >= 0.85 |
| 4 | quality_fpr | Quality | WARN | <= 0.15 |
| 5 | challenger_beats_baseline_quality | Quality | FAIL | >= 1.00 |
| 6 | sudden_drift_sensitivity | Drift | FAIL | >= 0.90 |
| 7 | gradual_drift_sensitivity | Drift | FAIL | >= 0.70 |
| 8 | drift_fpr | Drift | WARN | <= 0.20 |
| 9 | new_category_sensitivity | Drift | WARN | >= 0.80 |
| 10 | challenger_beats_baseline_drift | Drift | FAIL | >= 1.00 |

## Challenger Advantage: Windowed Trend Analysis

The key innovation in the challenger drift detector is **windowed trend
analysis**. The baseline detector compares overall value proportions between
reference and test data — which works for sudden shifts but misses gradual
drift where the aggregate proportions haven't shifted enough to cross the
threshold.

The challenger splits the test data into ordered halves and compares the
entropy of each half. If the distribution is shifting progressively (as in
gradual drift), the second half will have measurably lower entropy than the
first — even when the overall entropy hasn't changed enough to trigger a
point comparison. This is what allows the challenger to detect gradual drift
that the proportion-based baseline misses.

## Repo Map

| Path | Role |
|------|------|
| `src/benchmark/datasets/synthetic.py` | Deterministic data gen with fault/drift injection |
| `src/benchmark/quality/detectors.py` | Baseline + challenger quality detectors |
| `src/benchmark/drift/detectors.py` | Baseline + challenger drift detectors |
| `src/benchmark/scoring/ground_truth.py` | Precision/recall/F1 and sensitivity scoring |
| `src/benchmark/gates/evaluator.py` | 10-gate evaluation framework |
| `src/benchmark/evidence/writer.py` | Structured JSON evidence bundle |
| `src/benchmark/runners/orchestrator.py` | Full benchmark orchestrator + CLI |
| `configs/gates.json` | Gate definitions and thresholds |
| `tests/` | 37 tests across datasets, quality, drift, and integration |
