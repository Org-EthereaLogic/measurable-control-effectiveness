"""Allow running as: PYTHONPATH=src python -m benchmark.runners --seed 42 --rows 1000"""

import argparse

from benchmark.runners.orchestrator import print_benchmark_report

parser = argparse.ArgumentParser(description="Run the dual-track benchmark")
parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
parser.add_argument("--rows", type=int, default=1000, help="Number of rows (default: 1000)")
parser.add_argument("--evidence-dir", type=str, default=None, help="Directory for evidence bundle")

args = parser.parse_args()
print_benchmark_report(seed=args.seed, n_rows=args.rows, evidence_dir=args.evidence_dir)
