"""Tests for quality track detectors."""

from benchmark.datasets.synthetic import generate_dataset
from benchmark.quality.detectors import baseline_quality_check, challenger_quality_check

_EXPECTED = [
    "record_id", "customer_id", "department", "region",
    "product_category", "status", "priority", "amount",
]


class TestBaselineQuality:
    def setup_method(self):
        self.ds = generate_dataset(seed=42, n_rows=200)

    def test_flags_some_rows(self):
        result = baseline_quality_check(
            self.ds.faulted_df, self.ds.clean_df, _EXPECTED,
        )
        assert result["total_flagged"] > 0

    def test_detects_schema_drop(self):
        result = baseline_quality_check(
            self.ds.faulted_df, self.ds.clean_df, _EXPECTED,
        )
        assert result["schema_drop_detected"]

    def test_clean_data_no_flags(self):
        result = baseline_quality_check(
            self.ds.clean_df, self.ds.clean_df, _EXPECTED,
        )
        assert result["total_flagged"] == 0


class TestChallengerQuality:
    def setup_method(self):
        self.ds = generate_dataset(seed=42, n_rows=200)

    def test_flags_at_least_as_many_as_baseline(self):
        bl = baseline_quality_check(
            self.ds.faulted_df, self.ds.clean_df, _EXPECTED,
        )
        ch = challenger_quality_check(
            self.ds.faulted_df, self.ds.clean_df, _EXPECTED,
        )
        assert ch["total_flagged"] >= bl["total_flagged"]

    def test_catches_type_errors(self):
        ch = challenger_quality_check(
            self.ds.faulted_df, self.ds.clean_df, _EXPECTED,
        )
        type_indices = set(self.ds.fault_manifest["type_error_indices"])
        flagged = set(ch["flagged_indices"])
        caught = type_indices & flagged
        assert len(caught) > 0

    def test_clean_data_no_flags(self):
        result = challenger_quality_check(
            self.ds.clean_df, self.ds.clean_df, _EXPECTED,
        )
        assert result["total_flagged"] == 0
