"""Unit tests for ABR algorithms and MPEG-DASH simulator."""

from abr.core.algorithms import ALL_ABR_ALGORITHMS, choose_bitrate
from abr.core.simulator import NETWORK_TRACES, simulate_dash_session


def test_all_abr_algorithms_return_valid_ladder_bitrate():
    ladder = [400, 800, 1500, 2800, 4500]
    for algo in ALL_ABR_ALGORITHMS:
        br = choose_bitrate(
            algorithm=algo,
            bitrate_ladder_kbps=ladder,
            throughput_history_kbps=[3000.0, 3200.0],
            buffer_level_s=12.0,
            last_bitrate_kbps=1500,
        )
        assert br in ladder


def test_dash_simulation_across_all_traces():
    for algo in ALL_ABR_ALGORITHMS:
        for tr in NETWORK_TRACES:
            rep = simulate_dash_session(algorithm=algo, trace=tr, n_segments=30)
            assert rep.segments == 30
            assert len(rep.timeline) == 30
            assert rep.avg_bitrate_kbps >= 400
            assert rep.total_stall_s >= 0.0
