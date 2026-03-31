"""Gates subpackage — 10-gate evaluation framework."""

from benchmark.gates.evaluator import (
    GateConfig,
    GateResult,
    GateVerdict,
    evaluate_gates,
    load_gate_configs,
)

__all__ = [
    "GateConfig", "GateResult", "GateVerdict",
    "evaluate_gates", "load_gate_configs",
]
