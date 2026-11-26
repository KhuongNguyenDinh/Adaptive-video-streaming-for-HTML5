# Continuous Improvement System

`abr/eval/benchmark.py` evaluates all 4 ABR algorithms across 4 network traces (`stable_4g`, `fluctuating_wifi`, `bandwidth_drop`, `high_latency_mobile`) and logs results to `benchmarks/history.jsonl`.

## Baseline QoE Results (v2.0)

| Algorithm | Mean QoE | Avg Bitrate (kbps) | Avg Stall (s) | Avg Switches |
| :--- | :---: | :---: | :---: | :---: |
| `hybrid_mpc` | **3.2126** | `3394.2` | `1.017` | `8.0` |
| `buffer_based` | `2.6575` | `2832.9` | `0.000` | `16.0` |
| `bola_inspired` | `2.6435` | `2982.9` | `0.000` | `22.0` |
| `throughput_based` | `1.9719` | `2046.7` | `0.000` | `7.75` |

GitHub Actions (`.github/workflows/ci.yml`) runs `pytest -v` (enforcing `best_mean_qoe >= 2.0`) and `python -m abr.cli benchmark` on every push and PR.
