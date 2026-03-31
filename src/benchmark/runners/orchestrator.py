"""Benchmark orchestrator — generates data, runs both tracks, scores, evaluates gates.

Usage:
    PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000
"""

from __future__ import annotations

from pathlib import Path

from benchmark.datasets.synthetic import generate_dataset
from benchmark.drift.detectors import baseline_drift_check, challenger_drift_check
from benchmark.evidence.writer import write_evidence_bundle
from benchmark.gates.evaluator import evaluate_gates, load_gate_configs
from benchmark.quality.detectors import (
    baseline_quality_check,
    challenger_quality_check,
)
from benchmark.scoring.ground_truth import score_drift, score_quality

_MONITORED_COLUMNS = [
    "department", "region", "product_category", "status", "priority",
]
_EXPECTED_COLUMNS = [
    "record_id", "customer_id", "department", "region",
    "product_category", "status", "priority", "amount",
]


def _find_config() -> Path:
    candidates = [
        Path("configs/gates.json"),
        Path(__file__).resolve().parent.parent.parent.parent
        / "configs" / "gates.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("Cannot find configs/gates.json")


def run_benchmark(
    seed: int = 42,
    n_rows: int = 1000,
    evidence_dir: str | Path | None = None,
) -> dict:
    """Run the full dual-track benchmark and return structured results."""
    dataset = generate_dataset(seed=seed, n_rows=n_rows)

    # --- Quality track ---
    baseline_q = baseline_quality_check(
        dataset.faulted_df, dataset.clean_df, _EXPECTED_COLUMNS,
    )
    challenger_q = challenger_quality_check(
        dataset.faulted_df, dataset.clean_df, _EXPECTED_COLUMNS,
    )
    baseline_q_score = score_quality(
        baseline_q["flagged_indices"], dataset.fault_manifest, n_rows,
    )
    challenger_q_score = score_quality(
        challenger_q["flagged_indices"], dataset.fault_manifest, n_rows,
    )

    # --- Drift track ---
    bl_sudden = baseline_drift_check(
        dataset.clean_df, dataset.drifted_sudden_df, _MONITORED_COLUMNS,
    )
    ch_sudden = challenger_drift_check(
        dataset.clean_df, dataset.drifted_sudden_df, _MONITORED_COLUMNS,
    )
    bl_gradual = baseline_drift_check(
        dataset.clean_df, dataset.drifted_gradual_df, _MONITORED_COLUMNS,
    )
    ch_gradual = challenger_drift_check(
        dataset.clean_df, dataset.drifted_gradual_df, _MONITORED_COLUMNS,
    )
    bl_newcat = baseline_drift_check(
        dataset.clean_df, dataset.drifted_new_cat_df, _MONITORED_COLUMNS,
    )
    ch_newcat = challenger_drift_check(
        dataset.clean_df, dataset.drifted_new_cat_df, _MONITORED_COLUMNS,
    )
    bl_stable = baseline_drift_check(
        dataset.clean_df, dataset.stable_df, _MONITORED_COLUMNS,
    )
    ch_stable = challenger_drift_check(
        dataset.clean_df, dataset.stable_df, _MONITORED_COLUMNS,
    )

    baseline_d_score = score_drift(
        bl_sudden, bl_gradual, bl_newcat, bl_stable,
    )
    challenger_d_score = score_drift(
        ch_sudden, ch_gradual, ch_newcat, ch_stable,
    )

    # --- Gate evaluation ---
    config_path = _find_config()
    gate_configs = load_gate_configs(config_path)

    q_recall_ratio = (
        challenger_q_score.recall / max(baseline_q_score.recall, 0.001)
    )
    d_combined_ratio = (
        challenger_d_score.combined_score
        / max(baseline_d_score.combined_score, 0.001)
    )

    measured = {
        "quality_recall": challenger_q_score.recall,
        "quality_precision": challenger_q_score.precision,
        "quality_f1": challenger_q_score.f1,
        "quality_fpr": challenger_q_score.fpr,
        "challenger_beats_baseline_quality": round(q_recall_ratio, 4),
        "sudden_drift_sensitivity": challenger_d_score.sudden_sensitivity,
        "gradual_drift_sensitivity": challenger_d_score.gradual_sensitivity,
        "drift_fpr": challenger_d_score.drift_fpr,
        "new_category_sensitivity": challenger_d_score.new_category_sensitivity,
        "challenger_beats_baseline_drift": round(d_combined_ratio, 4),
    }

    gate_results, overall_verdict = evaluate_gates(gate_configs, measured)

    # --- Evidence bundle ---
    evidence_path = None
    if evidence_dir:
        evidence_path = write_evidence_bundle(
            evidence_dir, seed, n_rows,
            baseline_q_score, challenger_q_score,
            baseline_d_score, challenger_d_score,
            gate_results, overall_verdict,
        )

    return {
        "seed": seed,
        "n_rows": n_rows,
        "baseline_quality": baseline_q_score,
        "challenger_quality": challenger_q_score,
        "baseline_drift": baseline_d_score,
        "challenger_drift": challenger_d_score,
        "gate_results": gate_results,
        "overall_verdict": overall_verdict,
        "measured": measured,
        "evidence_path": evidence_path,
    }


_ROW_FMT = "  {:<24s} {:>10.4f} {:>12.4f}"


def _drift_row(label, bd_val, cd_val):
    """Print a drift track row."""
    print(_ROW_FMT.format(label, bd_val, cd_val))


def print_benchmark_report(
    seed: int = 42,
    n_rows: int = 1000,
    evidence_dir: str | Path | None = None,
) -> dict:
    """Run the benchmark and print a human-readable report."""
    results = run_benchmark(seed, n_rows, evidence_dir)

    bq = results["baseline_quality"]
    cq = results["challenger_quality"]
    bd = results["baseline_drift"]
    cd = results["challenger_drift"]

    print("=" * 64)
    print("MEASURABLE CONTROL EFFECTIVENESS — Benchmark Report")
    print("  seed={}  rows={}".format(seed, n_rows))
    print("=" * 64)
    print()

    print("Quality Track")
    print("-" * 48)
    hdr = "  {:<24s} {:>10s} {:>12s}"
    print(hdr.format("Metric", "Baseline", "Challenger"))
    print(_ROW_FMT.format("Recall", bq.recall, cq.recall))
    print(_ROW_FMT.format("Precision", bq.precision, cq.precision))
    print(_ROW_FMT.format("F1", bq.f1, cq.f1))
    print(_ROW_FMT.format("FPR", bq.fpr, cq.fpr))
    print()

    print("Drift Track")
    print("-" * 48)
    print(hdr.format("Metric", "Baseline", "Challenger"))
    _drift_row("Sudden sensitivity", bd.sudden_sensitivity, cd.sudden_sensitivity)
    _drift_row("Gradual sensitivity", bd.gradual_sensitivity, cd.gradual_sensitivity)
    _drift_row("New category sens.", bd.new_category_sensitivity, cd.new_category_sensitivity)
    _drift_row("FPR (stable data)", bd.drift_fpr, cd.drift_fpr)
    _drift_row("Combined score", bd.combined_score, cd.combined_score)
    print()

    print("Gate Evaluation (10 gates)")
    print("-" * 48)
    for gr in results["gate_results"]:
        sym = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗"}[gr.verdict.value]
        line = "  {} {:<36s} {:.4f} {} {:.2f}  [{}]".format(
            sym, gr.config.name, gr.measured_value,
            gr.config.operator, gr.config.threshold,
            gr.verdict.value,
        )
        print(line)
    print()
    print("Overall Verdict: {}".format(results["overall_verdict"].value))
    print()

    return results
