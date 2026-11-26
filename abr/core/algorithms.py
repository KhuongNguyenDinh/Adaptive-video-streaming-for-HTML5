"""Adaptive Bitrate (ABR) selection algorithms for MPEG-DASH / HLS streaming."""

from __future__ import annotations

import math
from typing import Sequence

ALL_ABR_ALGORITHMS = [
    "hybrid_mpc",
    "bola_inspired",
    "buffer_based",
    "throughput_based",
]


def _harmonic_mean(values: Sequence[float]) -> float:
    pos = [v for v in values if v > 0]
    if not pos:
        return 0.0
    return len(pos) / sum(1.0 / v for v in pos)


def choose_bitrate(
    algorithm: str,
    bitrate_ladder_kbps: Sequence[int],
    throughput_history_kbps: Sequence[float],
    buffer_level_s: float,
    last_bitrate_kbps: int,
    max_buffer_s: float = 30.0,
) -> int:
    """
    Select the next video segment bitrate (kbps) from `bitrate_ladder_kbps`.

    Algorithms:
      - `throughput_based`: EWMA/harmonic throughput with 0.85 safety factor.
      - `buffer_based`: BBA-0 linear reservoir/cushion mapping.
      - `bola_inspired`: Lyapunov utility maximization balancing bitrate & rebuffer risk.
      - `hybrid_mpc`: Looks ahead using harmonic throughput, buffer safety, and switch penalty.
    """
    algo = algorithm.strip().lower()
    if algo not in ALL_ABR_ALGORITHMS:
        raise ValueError(f"Unknown ABR algorithm '{algorithm}'. Valid: {ALL_ABR_ALGORITHMS}")

    ladder = sorted(bitrate_ladder_kbps)
    lowest = ladder[0]
    highest = ladder[-1]

    if algo == "throughput_based":
        recent = throughput_history_kbps[-5:]
        est = _harmonic_mean(recent) * 0.85 if recent else lowest
        chosen = lowest
        for br in ladder:
            if br <= est:
                chosen = br
        return chosen

    if algo == "buffer_based":
        reservoir = 6.0
        cushion = max(6.0, max_buffer_s - reservoir - 4.0)
        if buffer_level_s <= reservoir:
            return lowest
        if buffer_level_s >= reservoir + cushion:
            return highest
        ratio = (buffer_level_s - reservoir) / cushion
        target = lowest + ratio * (highest - lowest)
        return max((br for br in ladder if br <= target), default=lowest)

    if algo == "bola_inspired":
        # Utility u_m = ln(br / lowest), minimize rebuffer via Lyapunov parameter V
        utilities = [math.log(br / lowest) for br in ladder]
        gamma = 5.0
        V = (max_buffer_s - 4.0) / (utilities[-1] + gamma)
        best_idx = 0
        best_obj = -float("inf")
        for idx, (br, u) in enumerate(zip(ladder, utilities)):
            obj = (V * (u + gamma) - buffer_level_s) / br
            if obj > best_obj:
                best_obj = obj
                best_idx = idx
        return ladder[best_idx]

    # hybrid_mpc: combine harmonic throughput bound, buffer headroom, and switch smoothness
    recent = throughput_history_kbps[-5:]
    est_bw = _harmonic_mean(recent) if recent else float(lowest)
    # Effective available bandwidth scales up slightly when buffer is healthy
    headroom_factor = 0.72 + 0.28 * min(1.0, buffer_level_s / 18.0)
    safe_bw = est_bw * headroom_factor

    best_br = lowest
    best_qoe = -float("inf")
    for br in ladder:
        # Penalize bitrates exceeding safe bandwidth unless buffer is very full
        if br > safe_bw and buffer_level_s < 16.0:
            stall_pen = 4.0 * ((br - safe_bw) / max(1.0, safe_bw))
        else:
            stall_pen = 0.0
        switch_pen = 0.0006 * abs(br - last_bitrate_kbps)
        utility = math.log2(br / lowest) + 0.0004 * br
        qoe = utility - stall_pen - switch_pen
        if qoe > best_qoe:
            best_qoe = qoe
            best_br = br
    return best_br
