"""Tests for drift track detectors."""

from benchmark.datasets.synthetic import generate_dataset
from benchmark.drift.detectors import baseline_drift_check, challenger_drift_check

_COLS = ["department", "region", "product_category", "status", "priority"]


class TestBaselineDrift:
    def setup_method(self):
        self.ds = generate_dataset(seed=42, n_rows=500)

    def test_detects_sudden(self):
        result = baseline_drift_check(
            self.ds.clean_df, self.ds.drifted_sudden_df, _COLS,
        )
        assert result["drifted"]

    def test_stable_no_drift(self):
        result = baseline_drift_check(
            self.ds.clean_df, self.ds.stable_df, _COLS,
        )
        assert not result["drifted"]


class TestChallengerDrift:
    def setup_method(self):
        self.ds = generate_dataset(seed=42, n_rows=500)

    def test_detects_sudden(self):
        result = challenger_drift_check(
            self.ds.clean_df, self.ds.drifted_sudden_df, _COLS,
        )
        assert result["drifted"]

    def test_detects_gradual(self):
        result = challenger_drift_check(
            self.ds.clean_df, self.ds.drifted_gradual_df, _COLS,
        )
        assert result["drifted"]

    def test_detects_new_category(self):
        result = challenger_drift_check(
            self.ds.clean_df, self.ds.drifted_new_cat_df, _COLS,
        )
        assert result["drifted"]

    def test_stable_no_drift(self):
        result = challenger_drift_check(
            self.ds.clean_df, self.ds.stable_df, _COLS,
        )
        assert not result["drifted"]

    def test_new_values_identified(self):
        result = challenger_drift_check(
            self.ds.clean_df, self.ds.drifted_new_cat_df, _COLS,
        )
        status_result = result["column_results"].get("status", {})
        assert "Archived" in status_result.get("new_values", [])
