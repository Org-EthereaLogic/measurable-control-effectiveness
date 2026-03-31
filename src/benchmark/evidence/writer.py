"""Structured evidence bundle writer — append-only JSON for auditability."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from benchmark.gates.evaluator import GateResult, GateVerdict
from benchmark.scoring.ground_truth import DriftScore, QualityScore


def write_evidence_bundle(
    output_dir: str | Path,
    seed: int,
    n_rows: int,
    baseline_quality: QualityScore,
    challenger_quality: QualityScore,
    baseline_drift: DriftScore,
    challenger_drift: DriftScore,
    gate_results: list[GateResult],
    overall_verdict: GateVerdict,
) -> Path:
    """Write a structured evidence bundle to JSON."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    bundle = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
            "n_rows": n_rows,
            "version": "0.1.0",
        },
        "quality_track": {
            "baseline": asdict(baseline_quality),
            "challenger": asdict(challenger_quality),
        },
        "drift_track": {
            "baseline": asdict(baseline_drift),
            "challenger": asdict(challenger_drift),
        },
        "gates": [
            {
                "name": gr.config.name,
                "track": gr.config.track,
                "type": gr.config.gate_type,
                "threshold": gr.config.threshold,
                "measured": gr.measured_value,
                "verdict": gr.verdict.value,
            }
            for gr in gate_results
        ],
        "overall_verdict": overall_verdict.value,
    }

    filename = f"bench_{seed}_{n_rows}.json"
    file_path = output_path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    return file_path
