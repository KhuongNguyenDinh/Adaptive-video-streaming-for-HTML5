"""Automated ABR QoE benchmark & continuous-improvement tracker."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from abr.core.algorithms import ALL_ABR_ALGORITHMS
from abr.core.simulator import NETWORK_TRACES, simulate_dash_session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARK_HISTORY_PATH = ROOT_DIR / "benchmarks" / "history.jsonl"


def evaluate_algorithm(
    algorithm: str,
    traces: list[str] | None = None,
    n_segments: int = 60,
    seed: int = 42,
) -> dict[str, Any]:
    """Evaluate an ABR algorithm across all network traces."""
    target_traces = traces or NETWORK_TRACES
    reports = [
        simulate_dash_session(algorithm=algorithm, trace=tr, n_segments=n_segments, seed=seed)
        for tr in target_traces
    ]
    n = len(reports)
    return {
        "algorithm": algorithm,
        "mean_qoe": round(sum(r.qoe_score for r in reports) / n, 4),
        "avg_bitrate_kbps": round(sum(r.avg_bitrate_kbps for r in reports) / n, 1),
        "avg_stall_s": round(sum(r.total_stall_s for r in reports) / n, 3),
        "avg_switches": round(sum(r.bitrate_switches for r in reports) / n, 2),
    }


def run_benchmark_suite(record: bool = False) -> dict[str, Any]:
    """Benchmark all ABR algorithms and optionally record results to benchmarks/history.jsonl."""
    results = [evaluate_algorithm(algo) for algo in ALL_ABR_ALGORITHMS]
    best = max(results, key=lambda r: (r["mean_qoe"], -r["avg_stall_s"]))
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "best_algorithm": best["algorithm"],
        "best_mean_qoe": best["mean_qoe"],
        "results": results,
    }

    if record:
        BENCHMARK_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with BENCHMARK_HISTORY_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(summary) + "\n")

    return summary


if __name__ == "__main__":
    print(json.dumps(run_benchmark_suite(record=True), indent=2))
