"""Segment-level MPEG-DASH streaming & QoE simulator."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from abr.core.algorithms import choose_bitrate

DEFAULT_LADDER_KBPS = [400, 800, 1500, 2800, 4500, 7000]
NETWORK_TRACES = [
    "stable_4g",
    "fluctuating_wifi",
    "bandwidth_drop",
    "high_latency_mobile",
]


@dataclass
class SimulationReport:
    algorithm: str
    trace: str
    segments: int
    avg_bitrate_kbps: float
    total_stall_s: float
    rebuffer_ratio_pct: float
    bitrate_switches: int
    qoe_score: float
    timeline: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_network_trace(
    trace_name: str = "fluctuating_wifi",
    n_segments: int = 60,
    seed: int = 42,
) -> tuple[np.ndarray, float]:
    """Return (throughput_kbps_per_segment, rtt_seconds) for a named network profile."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_segments, dtype=np.float64)

    if trace_name == "stable_4g":
        bw = 5200.0 + rng.normal(0, 350.0, n_segments)
        rtt = 0.035
    elif trace_name == "fluctuating_wifi":
        bw = 3600.0 + 2100.0 * np.sin(2 * np.pi * t / 18.0) + rng.normal(0, 450.0, n_segments)
        rtt = 0.045
    elif trace_name == "bandwidth_drop":
        bw = np.full(n_segments, 5500.0)
        bw[n_segments // 3 : 2 * n_segments // 3] = 1100.0
        bw += rng.normal(0, 220.0, n_segments)
        rtt = 0.055
    elif trace_name == "high_latency_mobile":
        bw = 2200.0 + 900.0 * np.cos(2 * np.pi * t / 14.0) + rng.normal(0, 380.0, n_segments)
        rtt = 0.140
    else:
        raise ValueError(f"Unknown trace '{trace_name}'. Valid: {NETWORK_TRACES}")

    return np.clip(bw, 350.0, 12000.0), rtt


def simulate_dash_session(
    algorithm: str = "hybrid_mpc",
    trace: str = "fluctuating_wifi",
    n_segments: int = 60,
    segment_duration_s: float = 2.0,
    max_buffer_s: float = 30.0,
    seed: int = 42,
) -> SimulationReport:
    """Simulate a full MPEG-DASH playback session and compute SIGCOMM-style QoE."""
    bw_trace, rtt_s = generate_network_trace(trace, n_segments=n_segments, seed=seed)
    ladder = DEFAULT_LADDER_KBPS

    buffer_s = 4.0
    last_br = ladder[0]
    tp_history: list[float] = []

    bitrates: list[int] = []
    stalls: list[float] = []
    switches = 0
    timeline: list[dict[str, Any]] = []

    for idx in range(n_segments):
        selected = choose_bitrate(
            algorithm=algorithm,
            bitrate_ladder_kbps=ladder,
            throughput_history_kbps=tp_history,
            buffer_level_s=buffer_s,
            last_bitrate_kbps=last_br,
            max_buffer_s=max_buffer_s,
        )
        if idx > 0 and selected != last_br:
            switches += 1

        seg_size_kb = selected * segment_duration_s
        actual_bw = float(bw_trace[idx])
        download_s = rtt_s + (seg_size_kb / actual_bw)

        stall_s = max(0.0, download_s - buffer_s)
        buffer_s = max(0.0, buffer_s - download_s) + segment_duration_s
        buffer_s = min(max_buffer_s, buffer_s)

        effective_tp = seg_size_kb / max(1e-3, download_s)
        tp_history.append(effective_tp)
        bitrates.append(selected)
        stalls.append(stall_s)
        last_br = selected

        timeline.append(
            {
                "segment": idx + 1,
                "network_kbps": round(actual_bw, 1),
                "selected_kbps": selected,
                "buffer_s": round(buffer_s, 2),
                "stall_s": round(stall_s, 3),
            }
        )

    avg_br = float(np.mean(bitrates))
    total_stall = float(np.sum(stalls))
    total_video_s = n_segments * segment_duration_s
    rebuffer_pct = (total_stall / (total_video_s + total_stall)) * 100.0
    switch_mag = sum(abs(bitrates[i] - bitrates[i - 1]) for i in range(1, len(bitrates))) / max(1, len(bitrates) - 1)

    # Composite QoE: reward average bitrate (Mbps), penalize stalls heavily, penalize switches mildly
    qoe = (avg_br / 1000.0) - 4.3 * (total_stall / max(1.0, n_segments)) - 0.5 * (switch_mag / 1000.0)

    return SimulationReport(
        algorithm=algorithm,
        trace=trace,
        segments=n_segments,
        avg_bitrate_kbps=round(avg_br, 1),
        total_stall_s=round(total_stall, 3),
        rebuffer_ratio_pct=round(rebuffer_pct, 2),
        bitrate_switches=switches,
        qoe_score=round(qoe, 4),
        timeline=timeline,
    )
