"""Tests for synthetic data generation."""

from benchmark.datasets.synthetic import (
    GeneratedDataset,
    generate_dataset,
)


class TestGenerateDataset:
    def setup_method(self):
        self.ds = generate_dataset(seed=42, n_rows=100)

    def test_produces_dataset(self):
        assert isinstance(self.ds, GeneratedDataset)

    def test_clean_row_count(self):
        assert len(self.ds.clean_df) == 100

    def test_faulted_has_more_rows(self):
        # Duplicates are appended
        assert len(self.ds.faulted_df) > 100

    def test_fault_manifest_present(self):
        assert "null_indices" in self.ds.fault_manifest
        assert "duplicate_indices" in self.ds.fault_manifest
        assert "type_error_indices" in self.ds.fault_manifest

    def test_schema_drop(self):
        assert "priority" not in self.ds.faulted_df.columns
        assert "schema_dropped" in self.ds.fault_manifest

    def test_drifted_sudden_exists(self):
        assert len(self.ds.drifted_sudden_df) == 100

    def test_drifted_gradual_exists(self):
        assert len(self.ds.drifted_gradual_df) == 100

    def test_drifted_new_cat_exists(self):
        assert len(self.ds.drifted_new_cat_df) == 100

    def test_stable_exists(self):
        assert len(self.ds.stable_df) == 100

    def test_deterministic(self):
        ds2 = generate_dataset(seed=42, n_rows=100)
        assert list(self.ds.clean_df["record_id"]) == list(ds2.clean_df["record_id"])

    def test_different_seeds_differ(self):
        ds2 = generate_dataset(seed=99, n_rows=100)
        assert list(self.ds.clean_df["amount"]) != list(ds2.clean_df["amount"])
