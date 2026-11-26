# Architecture & Modernization

- `abr/core/algorithms.py`: Pure-Python ABR policies (`throughput_based`, `buffer_based`, `bola_inspired`, `hybrid_mpc`).
- `abr/core/simulator.py`: Segment-by-segment MPEG-DASH playback simulator with RTT, buffer dynamics, stall tracking, and composite QoE scoring.
- `abr/api/app.py` & `abr/web/templates/index.html`: FastAPI server hosting the live `dash.js` player, ABR simulator UI, `/api/simulate`, `/api/benchmarks`, and `/docs`.
- `abr/eval/benchmark.py`: Multi-trace ABR benchmark suite recording results to `benchmarks/history.jsonl`.
- `basicplayer.html`: Fixed broken `js/dash.all.js` script path to `dash.all.js` while preserving the original demo.
