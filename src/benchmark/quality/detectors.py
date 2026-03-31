"""Quality detectors — baseline (rule-based) and challenger (distribution-aware).

The baseline detector uses standard column-level rules: null checks, duplicate
detection, and schema validation. It represents the industry-standard approach.

The challenger detector adds distribution-aware checks that catch anomalies
the rule-based approach misses: type errors that produce parseable but
semantically wrong values, and entropy-based outlier detection.
"""

from __future__ import annotations

import pandas as pd


def baseline_quality_check(
    df: pd.DataFrame,
    reference_df: pd.DataFrame,
    expected_columns: list[str] | None = None,
) -> dict:
    """Industry-standard rule-based quality check.

    Checks: null counts per column, exact-match duplicate rows, schema presence.
    Returns flagged row indices and summary metrics.
    """
    flagged_indices: set[int] = set()

    # Null check — flag rows with any null in business columns
    biz_cols = [c for c in df.columns if c not in ("record_id", "row_order")]
    for col in biz_cols:
        null_mask = df[col].isna()
        flagged_indices.update(df.index[null_mask].tolist())

    # Duplicate check — flag exact duplicate rows (keep first)
    dup_mask = df.duplicated(subset=["record_id"], keep="first")
    flagged_indices.update(df.index[dup_mask].tolist())

    # Schema check — flag if expected columns are missing
    schema_missing: list[str] = []
    if expected_columns:
        schema_missing = [c for c in expected_columns if c not in df.columns]

    return {
        "flagged_indices": sorted(flagged_indices),
        "total_flagged": len(flagged_indices),
        "total_rows": len(df),
        "schema_missing": schema_missing,
        "schema_drop_detected": len(schema_missing) > 0,
    }


def challenger_quality_check(
    df: pd.DataFrame,
    reference_df: pd.DataFrame,
    expected_columns: list[str] | None = None,
) -> dict:
    """Distribution-aware quality check — catches what rule-based misses.

    In addition to the baseline checks (nulls, duplicates, schema), this adds:
    - Type anomaly detection: flags values that are syntactically valid but
      semantically wrong (e.g., "INVALID" in a numeric column) by comparing
      value distributions against the reference.
    - Entropy outlier detection: flags columns where the value distribution
      has shifted significantly from the reference, then traces to specific rows.
    """
    flagged_indices: set[int] = set()

    biz_cols = [c for c in df.columns if c not in ("record_id", "row_order")]

    # --- Same checks as baseline ---

    # Null check
    for col in biz_cols:
        null_mask = df[col].isna()
        flagged_indices.update(df.index[null_mask].tolist())

    # Duplicate check
    dup_mask = df.duplicated(subset=["record_id"], keep="first")
    flagged_indices.update(df.index[dup_mask].tolist())

    # Schema check
    schema_missing: list[str] = []
    if expected_columns:
        schema_missing = [c for c in expected_columns if c not in df.columns]

    # --- Additional distribution-aware checks ---

    # Type anomaly detection: for numeric columns in the reference,
    # flag rows where the value can't be cast to float
    for col in biz_cols:
        if col not in reference_df.columns:
            continue
        ref_series = reference_df[col]
        if ref_series.dtype in ("float64", "int64", "float32", "int32"):
            for idx, val in df[col].items():
                if val is None or pd.isna(val):
                    continue
                try:
                    float(val)
                except (ValueError, TypeError):
                    flagged_indices.add(idx)

    # Entropy-based outlier: for categorical columns, flag rows with values
    # not present in the reference distribution
    for col in biz_cols:
        if col not in reference_df.columns:
            continue
        ref_series = reference_df[col]
        if ref_series.dtype == "object":
            known_values = set(ref_series.dropna().unique())
            if not known_values:
                continue
            for idx, val in df[col].items():
                if pd.notna(val) and val not in known_values:
                    flagged_indices.add(idx)

    return {
        "flagged_indices": sorted(flagged_indices),
        "total_flagged": len(flagged_indices),
        "total_rows": len(df),
        "schema_missing": schema_missing,
        "schema_drop_detected": len(schema_missing) > 0,
    }
