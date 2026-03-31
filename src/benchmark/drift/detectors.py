"""Drift detectors — baseline (proportion-based) and challenger (entropy + trend).

The baseline detector compares value proportions between reference and test
data. It catches sudden shifts effectively but can miss gradual drift when
the overall proportions haven't shifted enough.

The challenger detector uses normalized Shannon entropy for point-in-time
comparison PLUS a windowed trend analysis that splits ordered data into
segments and detects progressive distribution shifts. This catches gradual
drift that proportion-based methods miss.
"""

from __future__ import annotations

import math

import pandas as pd


def _proportion_diff(
    ref: pd.Series,
    test: pd.Series,
) -> float:
    """Max absolute proportion difference across all values."""
    ref_props = ref.value_counts(normalize=True, dropna=False)
    test_props = test.value_counts(normalize=True, dropna=False)
    all_vals = set(ref_props.index) | set(test_props.index)
    max_diff = 0.0
    for v in all_vals:
        diff = abs(ref_props.get(v, 0.0) - test_props.get(v, 0.0))
        max_diff = max(max_diff, diff)
    return max_diff


def _shannon_entropy(series: pd.Series) -> float:
    """Compute Shannon entropy."""
    counts = series.value_counts(dropna=False)
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts / total
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _normalized_entropy(series: pd.Series) -> float:
    """Entropy normalized to [0, 1] by max possible entropy."""
    n_unique = series.nunique(dropna=False)
    if n_unique <= 1:
        return 0.0
    h = _shannon_entropy(series)
    h_max = math.log2(n_unique)
    return min(h / h_max, 1.0) if h_max > 0 else 0.0


def baseline_drift_check(
    reference_df: pd.DataFrame,
    test_df: pd.DataFrame,
    columns: list[str],
    threshold: float = 0.25,
) -> dict:
    """Proportion-based drift detection (industry standard).

    For each column, computes the maximum absolute proportion difference.
    Flags drift when the difference exceeds the threshold.
    """
    column_results: dict[str, dict] = {}
    drifted_columns: list[str] = []

    for col in columns:
        if col not in reference_df.columns or col not in test_df.columns:
            column_results[col] = {"drifted": True, "score": 1.0, "reason": "missing"}
            drifted_columns.append(col)
            continue

        diff = _proportion_diff(reference_df[col], test_df[col])
        is_drifted = diff > threshold
        column_results[col] = {
            "drifted": is_drifted,
            "score": round(diff, 4),
            "reason": "proportion_shift" if is_drifted else "stable",
        }
        if is_drifted:
            drifted_columns.append(col)

    return {
        "drifted": len(drifted_columns) > 0,
        "drifted_columns": drifted_columns,
        "column_results": column_results,
        "method": "proportion_difference",
    }


def challenger_drift_check(
    reference_df: pd.DataFrame,
    test_df: pd.DataFrame,
    columns: list[str],
    entropy_threshold: float = 0.25,
    trend_threshold: float = 0.10,
) -> dict:
    """Entropy-based drift detection with windowed trend analysis.

    Two detection layers:
    1. Point comparison: normalized entropy of test vs reference.
    2. Trend detection: split test data into ordered halves, compare entropy
       between first and second half. Detects gradual drift that point
       comparison misses.
    """
    column_results: dict[str, dict] = {}
    drifted_columns: list[str] = []

    for col in columns:
        if col not in reference_df.columns or col not in test_df.columns:
            column_results[col] = {"drifted": True, "score": 1.0, "reason": "missing"}
            drifted_columns.append(col)
            continue

        ref_entropy = _normalized_entropy(reference_df[col])
        test_entropy = _normalized_entropy(test_df[col])
        entropy_delta = abs(test_entropy - ref_entropy)

        # Point comparison
        point_drifted = entropy_delta > entropy_threshold

        # Trend detection: split ordered data into halves
        n = len(test_df)
        mid = n // 2
        if mid > 10 and "row_order" in test_df.columns:
            sorted_df = test_df.sort_values("row_order")
            first_half = sorted_df.iloc[:mid]
            second_half = sorted_df.iloc[mid:]
            h_first = _normalized_entropy(first_half[col])
            h_second = _normalized_entropy(second_half[col])
            trend_delta = abs(h_first - h_second)
            trend_drifted = trend_delta > trend_threshold
        else:
            trend_delta = 0.0
            trend_drifted = False

        # New category detection
        ref_values = set(reference_df[col].dropna().unique())
        test_values = set(test_df[col].dropna().unique())
        new_values = test_values - ref_values
        new_cat_drifted = len(new_values) > 0

        is_drifted = point_drifted or trend_drifted or new_cat_drifted

        reason = "stable"
        if point_drifted:
            reason = "entropy_shift"
        elif trend_drifted:
            reason = "gradual_trend"
        elif new_cat_drifted:
            reason = "new_categories"

        column_results[col] = {
            "drifted": is_drifted,
            "entropy_delta": round(entropy_delta, 4),
            "trend_delta": round(trend_delta, 4),
            "new_values": sorted(new_values) if new_values else [],
            "reason": reason,
        }
        if is_drifted:
            drifted_columns.append(col)

    return {
        "drifted": len(drifted_columns) > 0,
        "drifted_columns": drifted_columns,
        "column_results": column_results,
        "method": "entropy_with_trend",
    }
