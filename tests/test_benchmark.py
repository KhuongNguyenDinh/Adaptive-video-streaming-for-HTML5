"""Regression tests for the continuous-improvement ABR QoE benchmark."""

from abr.eval.benchmark import run_benchmark_suite


def test_benchmark_meets_qoe_floor():
    summary = run_benchmark_suite(record=False)
    assert summary["best_mean_qoe"] >= 2.0
    assert len(summary["results"]) == 4
