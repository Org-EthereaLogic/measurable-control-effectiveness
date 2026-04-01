# You Invested in Data Quality Controls. Can You Prove They Work?

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4f8278ed00124713a8f101dfa32845aa)](https://app.codacy.com/gh/Org-EthereaLogic/measurable-control-effectiveness?utm_source=github.com&utm_medium=referral&utm_content=Org-EthereaLogic/measurable-control-effectiveness&utm_campaign=Badge_Grade)

**Enterprise Data Trust — Chapter 3: Measurable Control Effectiveness**

Built by Anthony Johnson | EthereaLogic LLC

---

Every enterprise data platform includes some form of data quality monitoring. Few organizations can answer a direct question from the CFO: what percentage of failures would your controls actually catch?

This repository implements a **reproducible benchmark** that runs data controls against known failure scenarios and produces measurable evidence of their detection rates — precision, recall, false positive rates, and gate verdicts — compared against industry-standard alternatives.

## Executive summary

| Leadership question | Answer |
| ------------------- | ------ |
| What business risk does this address? | Organizations invest in data quality tooling without measurable evidence of its effectiveness. When a failure reaches production, there is no way to determine whether the controls were inadequate or simply misconfigured. |
| What does this solution demonstrate? | A dual-track benchmark that injects known quality and drift failures, runs both a custom approach and an industry-standard alternative against them, and produces ground-truth-scored evidence across 10 configured gates. |
| Why does it matter? | It transforms the conversation from "we have controls in place" to "our controls catch 100% of injected quality failures and show measured lift over the baseline where the challenger adds value — here is the reproducible evidence." |

## Decision / KPI contract

**Business decision:** are the data controls effective enough to trust in production?

The benchmark answers that question with six metrics:

| KPI | Meaning |
|-----|---------|
| `quality_recall` | Percentage of injected quality failures the control actually caught |
| `quality_precision` | Percentage of flagged rows that were real failures (not false alarms) |
| `quality_f1` | Balanced measure of detection accuracy |
| `drift_combined_score` | Aggregate drift detection effectiveness across 3 scenarios |
| `challenger_beats_baseline_quality` | Ratio of challenger recall to baseline recall (must be >= 1.0) |
| `challenger_beats_baseline_drift` | Ratio of challenger combined drift score to baseline (must be >= 1.0) |

**Control rule:** the benchmark passes only when all 10 gates clear — including the two "beats baseline" gates that require the custom approach to match or exceed the industry-standard alternative on both tracks.

## Why this pattern

Most organizations evaluate data quality tooling based on feature lists, vendor demos, or engineering intuition. None of these produce measurable evidence.

This benchmark pattern addresses three gaps:

- **Ground truth replaces heuristics.** Every injected fault is tracked to exact row indices. Scoring uses the injection manifest as truth, not statistical approximations or threshold tuning.
- **Dual-track comparison is built in.** The same failures are run through both a baseline (industry-standard) and a challenger (custom) approach. The benchmark doesn't just prove the challenger works — it measures exactly where and by how much it outperforms.
- **Evidence is structured and auditable.** Every run produces a JSON evidence bundle with quality scores, drift scores, gate verdicts, and metadata. This is the artifact a governance team reviews, not a dashboard screenshot.

## The business problem

Most enterprise data quality strategies share a common blind spot: they cannot prove their own effectiveness.

**Investment decisions lack evidence.** When the CTO asks whether the team should invest in better data quality tooling, the answer is usually qualitative rather than quantitative.

**Control gaps are invisible.** A monitoring tool that catches 80% of quality failures appears to be working well until the 20% it misses includes the one that corrupts a board-level KPI.

**Vendor comparisons are subjective.** Teams evaluate vendors based on feature lists and demos rather than measured detection rates against their own failure patterns.

## Verified evidence

The benchmark produces reproducible results from a deterministic seed (`seed=42`, `rows=1000`):

### Quality track

| Metric | Baseline (industry standard) | Challenger (custom approach) |
| ------ | ---------------------------: | --------------------------: |
| Recall | 0.8767 | **1.0000** |
| Precision | 1.0000 | 1.0000 |
| F1 | 0.9343 | **1.0000** |
| FPR | 0.0000 | 0.0000 |

The challenger catches every injected quality failure. The baseline misses approximately 12% — primarily type errors that produce syntactically valid but semantically wrong values.

### Drift track

| Metric | Baseline | Challenger |
| ------ | -------: | ---------: |
| Sudden drift sensitivity | 1.0000 | 1.0000 |
| Gradual drift sensitivity | 1.0000 | 1.0000 |
| New category sensitivity | 0.0000 | **1.0000** |
| FPR (stable data) | 0.0000 | 0.0000 |
| Combined score | 0.6667 | **1.0000** |

In the current seeded benchmark, both approaches detect the sudden and gradual drift scenarios. The challenger's measured lift comes from detecting novel category injection that the proportion-based baseline misses entirely, which raises the challenger's combined drift score above the baseline.

### Gate evaluation

All 10 configured gates pass:

```text
✓ quality_recall                       1.0000 >= 0.90  [PASS]
✓ quality_precision                    1.0000 >= 0.80  [PASS]
✓ quality_f1                           1.0000 >= 0.85  [PASS]
✓ quality_fpr                          0.0000 <= 0.15  [PASS]
✓ challenger_beats_baseline_quality    1.1406 >= 1.00  [PASS]
✓ sudden_drift_sensitivity             1.0000 >= 0.90  [PASS]
✓ gradual_drift_sensitivity            1.0000 >= 0.70  [PASS]
✓ drift_fpr                            0.0000 <= 0.20  [PASS]
✓ new_category_sensitivity             1.0000 >= 0.80  [PASS]
✓ challenger_beats_baseline_drift      1.4999 >= 1.00  [PASS]

Overall Verdict: PASS
```

Regression coverage: `PYTHONPATH=src pytest tests/ -q` completes with `37 passed`.

## How the benchmark works

1. **Synthetic data generation** produces clean datasets with controlled fault and drift injection using deterministic seeds.
2. **Baseline evaluation** runs industry-standard quality and drift detection against the injected failures.
3. **Challenger evaluation** runs the custom distribution-aware approach against the same failures.
4. **Ground-truth scoring** compares both sets of results against the known injection manifest.
5. **Gate evaluation** applies 10 configured thresholds and emits pass/warn/fail verdicts.
6. **Evidence generation** produces a structured JSON bundle for auditability.

## Platform alignment

This benchmark models the control effectiveness measurement that sits alongside a Databricks Medallion Architecture:

- **Quality gates** map to the Bronze-to-Silver boundary.
- **Drift gates** map to the Silver-to-Gold boundary.
- **Evidence bundles** provide governance and audit documentation.

The benchmark runs locally in pure Python with no infrastructure required.

## Reproducibility

```bash
git clone https://github.com/Org-EthereaLogic/measurable-control-effectiveness.git
cd measurable-control-effectiveness

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src pytest tests/ -q                                          # Expected: 37 passed
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000         # Expected: PASS
```

Generate an evidence bundle:

```bash
PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000 --evidence-dir runs/
```

## Technical approach

For the benchmark architecture, fault injection specifications, scoring methodology, gate definitions, and the windowed trend analysis design, see [docs/technical-approach.md](docs/technical-approach.md).

## Part of a series

This is **Chapter 3** of the *Enterprise Data Trust* portfolio — a three-part body of work addressing the full lifecycle of data reliability in enterprise Databricks platforms.

| Chapter | Focus | Repository |
|---------|-------|------------|
| 1. Trusted Source Intake | Validate and certify data before downstream consumption | [trusted-source-intake](https://github.com/Org-EthereaLogic/trusted-source-intake) |
| 2. Silent Failure Prevention | Detect distribution drift before it reaches executive dashboards | [silent-failure-prevention](https://github.com/Org-EthereaLogic/silent-failure-prevention) |
| **3. Measurable Control Effectiveness** | Prove that your data controls work against known failure scenarios | ← You are here |

---

<p align="left">
  <a href="https://github.com/Org-EthereaLogic/measurable-control-effectiveness/actions/workflows/ci.yml"><img src="https://github.com/Org-EthereaLogic/measurable-control-effectiveness/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://app.codacy.com/gh/Org-EthereaLogic/measurable-control-effectiveness/dashboard"><img src="https://app.codacy.com/project/badge/Grade/placeholder" alt="Codacy grade"></a>
  <a href="https://codecov.io/gh/Org-EthereaLogic/measurable-control-effectiveness"><img src="https://codecov.io/gh/Org-EthereaLogic/measurable-control-effectiveness/graph/badge.svg" alt="Codecov coverage"></a>
</p>

MIT License. See [LICENSE](LICENSE.md) for details.
