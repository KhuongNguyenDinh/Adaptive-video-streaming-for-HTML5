"""FastAPI backend for AdaptiveStream Studio (HTML5 DASH Player + ABR QoE Simulator)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from abr.core.algorithms import ALL_ABR_ALGORITHMS
from abr.core.simulator import NETWORK_TRACES, simulate_dash_session

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "web" / "templates"
BENCHMARK_HISTORY_PATH = ROOT_DIR / "benchmarks" / "history.jsonl"


class SimulateRequest(BaseModel):
    algorithm: str = "hybrid_mpc"
    trace: str = "fluctuating_wifi"
    n_segments: int = 60
    seed: int = 42


def create_app() -> FastAPI:
    app = FastAPI(
        title="AdaptiveStream Studio v2.0",
        description="HTML5 MPEG-DASH Player, ABR Algorithms, and QoE Continuous Improvement",
        version="2.0.0",
    )
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "algorithms": ALL_ABR_ALGORITHMS,
                "traces": NETWORK_TRACES,
            },
        )

    @app.get("/dash.all.js")
    async def serve_legacy_dash() -> FileResponse:
        p = ROOT_DIR / "dash.all.js"
        if not p.exists():
            raise HTTPException(status_code=404, detail="dash.all.js not found")
        return FileResponse(p, media_type="application/javascript")

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": "2.0.0",
            "algorithms": ALL_ABR_ALGORITHMS,
            "traces": NETWORK_TRACES,
        }

    @app.post("/api/simulate")
    async def simulate(req: SimulateRequest) -> dict[str, Any]:
        try:
            report = simulate_dash_session(
                algorithm=req.algorithm,
                trace=req.trace,
                n_segments=req.n_segments,
                seed=req.seed,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return report.to_dict()

    @app.get("/api/benchmarks")
    async def get_benchmarks() -> dict[str, Any]:
        if not BENCHMARK_HISTORY_PATH.exists():
            return {"runs": []}
        runs = [
            json.loads(line)
            for line in BENCHMARK_HISTORY_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return {"runs": runs[-20:]}

    return app


app = create_app()
