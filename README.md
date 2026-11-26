# AdaptiveStream Studio v2.0 — HTML5 MPEG-DASH & ABR QoE

**AdaptiveStream Studio** modernizes the original HTML5 `dash.js` player demo into a complete **Adaptive Bitrate (ABR) Streaming & Quality-of-Experience (QoE) Studio**, featuring 4 ABR algorithms, a segment-level MPEG-DASH network simulator, a FastAPI + HTML5 DASH dashboard, and an automated Continuous Improvement QoE benchmark loop.

---

## Key Features

- **Live HTML5 MPEG-DASH Player**: Built-in `dash.js` player supporting any `.mpd` manifest URL (plus fixed `basicplayer.html` path).
- **4 ABR Bitrate Selection Algorithms** (`abr/core/algorithms.py`):
  - `hybrid_mpc` (Best: **Mean QoE = 3.2126**, Avg Bitrate = `3394.2 kbps`)
  - `buffer_based` (BBA-0 reservoir/cushion — **Mean QoE = 2.6575**, `0.0s` stalls)
  - `bola_inspired` (Lyapunov utility optimization — **Mean QoE = 2.6435**, `0.0s` stalls)
  - `throughput_based` (Harmonic throughput with safety factor — **Mean QoE = 1.9719**)
- **MPEG-DASH Network Simulator**: Evaluates playback across `stable_4g`, `fluctuating_wifi`, `bandwidth_drop`, and `high_latency_mobile`.
- **Continuous Improvement Loop**: `abr benchmark --record` logs QoE metrics to `benchmarks/history.jsonl` and is gated by GitHub Actions CI.

---

## Quick Start

```bash
pip install -e ".[dev]"

# Launch HTML5 DASH Player & ABR QoE Studio
python -m abr.cli serve --host 127.0.0.1 --port 8002

# Run a single ABR simulation from CLI
python -m abr.cli simulate --algorithm hybrid_mpc --trace bandwidth_drop

# Run and record continuous-improvement QoE benchmarks
python -m abr.cli benchmark --record

# Run tests
pytest -v
```

---

## Documentation

- [Architecture & Modernization](docs/ARCHITECTURE.md)
- [ABR Algorithms & QoE Model](docs/ABR_ALGORITHMS.md)
- [Continuous Improvement System](docs/CONTINUOUS_IMPROVEMENT.md)
