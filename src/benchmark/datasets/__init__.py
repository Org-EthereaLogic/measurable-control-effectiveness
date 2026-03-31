"""Datasets subpackage — deterministic synthetic data with fault and drift injection."""

from benchmark.datasets.synthetic import (
    DriftProfile,
    FaultProfile,
    GeneratedDataset,
    generate_dataset,
)

__all__ = ["DriftProfile", "FaultProfile", "GeneratedDataset", "generate_dataset"]
