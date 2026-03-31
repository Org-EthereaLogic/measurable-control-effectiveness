"""Integration test — runs the full benchmark and verifies key claims."""

from benchmark.gates.evaluator import GateVerdict
from benchmark.runners.orchestrator import run_benchmark


class TestFullBenchmark:
    def setup_method(self):
        self.results = run_benchmark(seed=42, n_rows=1000)

    def test_overall_verdict_pass(self):
        assert self.results["overall_verdict"] == GateVerdict.PASS

    def test_ten_gates_evaluated(self):
        assert len(self.results["gate_results"]) == 10

    def test_challenger_quality_recall_perfect(self):
        assert self.results["challenger_quality"].recall == 1.0

    def test_challenger_beats_baseline_quality(self):
        bq = self.results["baseline_quality"]
        cq = self.results["challenger_quality"]
        assert cq.recall >= bq.recall

    def test_challenger_sudden_drift(self):
        assert self.results["challenger_drift"].sudden_sensitivity == 1.0

    def test_challenger_gradual_drift(self):
        assert self.results["challenger_drift"].gradual_sensitivity == 1.0

    def test_challenger_new_category(self):
        assert self.results["challenger_drift"].new_category_sensitivity == 1.0

    def test_challenger_no_false_positives_drift(self):
        assert self.results["challenger_drift"].drift_fpr == 0.0

    def test_challenger_beats_baseline_drift(self):
        bd = self.results["baseline_drift"]
        cd = self.results["challenger_drift"]
        assert cd.combined_score >= bd.combined_score

    def test_all_gates_pass(self):
        for gr in self.results["gate_results"]:
            assert gr.verdict == GateVerdict.PASS, (
                "Gate {} failed: {} {} {}".format(
                    gr.config.name, gr.measured_value,
                    gr.config.operator, gr.config.threshold,
                )
            )


class TestDeterminism:
    def test_repeated_runs_match(self):
        r1 = run_benchmark(seed=42, n_rows=1000)
        r2 = run_benchmark(seed=42, n_rows=1000)
        assert r1["overall_verdict"] == r2["overall_verdict"]
        assert r1["challenger_quality"].recall == r2["challenger_quality"].recall
        assert r1["challenger_drift"].combined_score == r2["challenger_drift"].combined_score


class TestEvidenceBundle:
    def test_writes_evidence(self, tmp_path):
        results = run_benchmark(seed=42, n_rows=100, evidence_dir=tmp_path)
        assert results["evidence_path"] is not None
        assert results["evidence_path"].exists()

    def test_evidence_is_json(self, tmp_path):
        import json
        results = run_benchmark(seed=42, n_rows=100, evidence_dir=tmp_path)
        with open(results["evidence_path"]) as f:
            bundle = json.load(f)
        assert "quality_track" in bundle
        assert "drift_track" in bundle
        assert "gates" in bundle
        assert bundle["overall_verdict"] == "PASS"
