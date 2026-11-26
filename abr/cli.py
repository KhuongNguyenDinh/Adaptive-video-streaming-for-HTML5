"""Command-line interface for AdaptiveStream Studio."""

from __future__ import annotations

import argparse
import json
import sys

import uvicorn

from abr.core.simulator import simulate_dash_session
from abr.eval.benchmark import run_benchmark_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="abr", description="AdaptiveStream Studio CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    serve_p = sub.add_parser("serve", help="Start the HTML5 DASH Studio & QoE Simulator")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8002)
    serve_p.add_argument("--reload", action="store_true")

    sim_p = sub.add_parser("simulate", help="Run a single ABR simulation")
    sim_p.add_argument("--algorithm", default="hybrid_mpc")
    sim_p.add_argument("--trace", default="fluctuating_wifi")
    sim_p.add_argument("--segments", type=int, default=60)

    bench_p = sub.add_parser("benchmark", help="Run the continuous-improvement ABR QoE benchmark")
    bench_p.add_argument("--record", action="store_true", help="Append results to benchmarks/history.jsonl")

    args = parser.parse_args(argv)

    if args.command == "serve":
        uvicorn.run("abr.api.app:app", host=args.host, port=args.port, reload=args.reload)
        return 0

    if args.command == "simulate":
        rep = simulate_dash_session(
            algorithm=args.algorithm,
            trace=args.trace,
            n_segments=args.segments,
        )
        print(json.dumps(rep.to_dict(), indent=2))
        return 0

    if args.command == "benchmark":
        summary = run_benchmark_suite(record=args.record)
        print(json.dumps(summary, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
