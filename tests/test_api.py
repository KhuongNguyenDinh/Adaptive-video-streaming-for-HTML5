"""Integration tests for AdaptiveStream Studio FastAPI endpoints."""

from fastapi.testclient import TestClient

from abr.api.app import create_app

client = TestClient(create_app())


def test_home_health_and_legacy_dash():
    r = client.get("/")
    assert r.status_code == 200
    assert "AdaptiveStream Studio" in r.text

    h = client.get("/api/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"

    d = client.get("/dash.all.js")
    assert d.status_code == 200


def test_simulate_and_benchmarks():
    sim = client.post(
        "/api/simulate",
        json={"algorithm": "hybrid_mpc", "trace": "bandwidth_drop", "n_segments": 40},
    )
    assert sim.status_code == 200
    assert sim.json()["segments"] == 40
    assert "qoe_score" in sim.json()

    bench = client.get("/api/benchmarks")
    assert bench.status_code == 200
    assert "runs" in bench.json()
