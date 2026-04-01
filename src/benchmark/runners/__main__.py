"""Allow running as: python -m benchmark.runners or benchmark-demo."""

import argparse

from benchmark.runners.orchestrator import print_benchmark_report


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the benchmark runner."""
    parser = argparse.ArgumentParser(description="Run the dual-track benchmark")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows (default: 1000)")
    parser.add_argument(
        "--evidence-dir",
        type=str,
        default=None,
        help="Directory for evidence bundle",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Console entry point for the benchmark demo."""
    args = build_parser().parse_args(argv)
    print_benchmark_report(seed=args.seed, n_rows=args.rows, evidence_dir=args.evidence_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
