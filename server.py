#!/usr/bin/env python3
"""
server.py — FastAPI backend for the DAEMON wargame simulation web UI.

Run:
    python server.py
    # or: uvicorn server:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
    GET  /api/scenarios          — list all Kharg + CSG scenarios
    POST /api/run                — start a scenario run, returns job_id
    GET  /api/stream/{job_id}    — SSE stream of stdout lines
    GET  /api/results/{job_id}   — structured result dict
    GET  /api/download/{job_id}  — .kmz file download
    Static: /output → output/scenarios/
    Static: /       → web/
"""

import io
import os
import sys
import threading
import uuid
from collections import deque
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT    = os.path.dirname(os.path.abspath(__file__))
_SCENARIOS_DIR = os.path.join(_REPO_ROOT, "output", "scenarios")
_WEB_DIR       = os.path.join(_REPO_ROOT, "web")

os.makedirs(_SCENARIOS_DIR, exist_ok=True)
os.makedirs(_WEB_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Lazy imports — heavy simulation modules imported only when needed so the
# server starts quickly even when deps are slow to import.
# ---------------------------------------------------------------------------
def _import_kharg():
    from persian_gulf_simulation.runner import (
        build_scenarios, run_scenario_entry, _patch_scenario, _run_scenario,
        _STRIP,
    )
    import persian_gulf_simulation.config as cfg
    return build_scenarios, run_scenario_entry, _patch_scenario, _run_scenario, _STRIP, cfg


def _import_csg():
    from persian_gulf_simulation.generate_wargame_kml import (
        SCENARIOS as CSG_SCENARIOS,
        generate_scenario,
    )
    return CSG_SCENARIOS, generate_scenario


# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------
_jobs_lock = threading.Lock()
_jobs: dict = {}   # job_id → JobRecord dict

# CSG scenario rank order (same order as main() in generate_wargame_kml.py)
_CSG_RANK_ORDER = (
    "realistic", "one_percent_probe", "depleted_drone_first", "depleted_coastal",
    "one_percent_fatah2", "depleted_israel_split", "medium", "drone_first_low",
    "hypersonic_threat", "drone_first_medium", "low", "ballistic_barrage",
    "us_win_c2_disrupted", "us_win_arsenal_attrition", "usa_best", "ascm_swarm",
    "us_win_ew_dominance", "us_win_allied_umbrella", "us_win_preemption", "high",
    "shore_based_defense", "strait_transit", "drone_first_high", "caves",
    "ballistic_surge", "coordinated_strike", "focused_salvo", "iran_best",
)

app = FastAPI(title="DAEMON Wargame UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class RunRequest(BaseModel):
    id: str
    engine: str   # "kharg" or "csg"
    params: dict = {}


# ---------------------------------------------------------------------------
# Stdout capture helper
# ---------------------------------------------------------------------------
class _TeeWriter:
    """Write to both job log_lines deque and the real stdout."""
    def __init__(self, log_deque: deque, real_stdout):
        self._log   = log_deque
        self._real  = real_stdout
        self._buf   = ""

    def write(self, text: str):
        self._real.write(text)
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._log.append(line)

    def flush(self):
        self._real.flush()

    def fileno(self):
        return self._real.fileno()


# ---------------------------------------------------------------------------
# Scalar-only param extraction for CSG scenarios
# ---------------------------------------------------------------------------
_CSG_EXCLUDE_KEYS = {
    "munitions", "description", "label", "csg_fleet", "custom_sites",
    "ballistic_targets", "focus_csg", "drone_focus_csg",
    "us_strike_timing", "iaf_timing",
}


def _csg_params(sc_dict: dict) -> dict:
    """Return only scalar (int/float/bool/str) keys from a SCENARIOS entry."""
    return {
        k: v for k, v in sc_dict.items()
        if k not in _CSG_EXCLUDE_KEYS and isinstance(v, (int, float, bool, str))
    }


# ---------------------------------------------------------------------------
# /api/scenarios
# ---------------------------------------------------------------------------
@app.get("/api/scenarios")
def get_scenarios():
    build_scenarios, _, _, _, _, cfg = _import_kharg()
    CSG_SCENARIOS, _ = _import_csg()

    results = []

    # ---- Kharg scenarios ----
    kharg_list = build_scenarios()
    for rank, (label, overrides, fname, desc) in enumerate(kharg_list, start=1):
        # Derive a clean id from filename (strip .kmz)
        sc_id = fname.replace(".kmz", "")

        # Build params: all override keys that are numeric/bool scalars, plus
        # a few key defaults from config so the UI can show meaningful values.
        params = {}
        # Include defaults for the main tunable parameters
        params["n_irgc"]              = cfg.N_SQUADS
        params["stinger_pk"]          = cfg.STINGER_PK
        params["stinger_hover_pk"]    = cfg.STINGER_HOVER_PK
        params["stinger_wez_km"]      = cfg.STINGER_WEZ_KM
        params["n_drone_boats"]       = cfg.N_DRONE_BOATS
        params["n_shahed"]            = cfg.N_SHAHED
        params["n_island_shahed"]     = cfg.N_ISLAND_SHAHED
        params["ai_drone_fraction"]   = cfg.AI_DRONE_FRACTION
        params["ew_irgc_pk_mult"]     = cfg.EW_IRGC_PK_MULT
        params["ew_irgc_defense_mult_adj"] = cfg.EW_IRGC_DEFENSE_MULT_ADJ
        params["ew_manpads_pk_mult"]  = cfg.EW_MANPADS_PK_MULT
        params["ew_mildec_fraction"]  = cfg.EW_MILDEC_FRACTION
        params["ew_mildec_delay_steps"] = cfg.EW_MILDEC_DELAY_STEPS
        params["ew_shahed_abort_rate"] = cfg.EW_SHAHED_ABORT_RATE
        params["ew_ship_sam_pk_mult"] = cfg.EW_SHIP_SAM_PK_MULT
        params["osprey_drop_steps"]   = cfg.OSPREY_DROP_STEPS
        params["beach_assault"]       = False
        params["iran_retaliation"]    = True
        params["pre_strike_survival_pct"] = 0.0

        # Apply overrides on top of defaults (only scalar/bool values)
        for k, v in overrides.items():
            if isinstance(v, (int, float, bool, str)):
                params[k] = v

        results.append({
            "id":          sc_id,
            "engine":      "kharg",
            "rank":        rank,
            "label":       label,
            "description": desc,
            "params":      params,
        })

    # ---- CSG scenarios ----
    for rank, sc_key in enumerate(_CSG_RANK_ORDER, start=1):
        if sc_key not in CSG_SCENARIOS:
            continue
        sc = CSG_SCENARIOS[sc_key]
        results.append({
            "id":          sc_key,
            "engine":      "csg",
            "rank":        rank,
            "label":       sc.get("label", sc_key),
            "description": sc.get("description", ""),
            "params":      _csg_params(sc),
        })

    return results


# ---------------------------------------------------------------------------
# /api/run
# ---------------------------------------------------------------------------
@app.post("/api/run")
def run_scenario(req: RunRequest):
    job_id = str(uuid.uuid4())
    log_deque: deque = deque(maxlen=10000)

    with _jobs_lock:
        _jobs[job_id] = {
            "status":      "running",
            "log_lines":   log_deque,
            "result_dict": None,
            "kmz_path":    None,
            "engine":      req.engine,
            "scenario_id": req.id,
        }

    def _run():
        real_stdout = sys.stdout
        tee = _TeeWriter(log_deque, real_stdout)
        sys.stdout = tee
        try:
            if req.engine == "kharg":
                _run_kharg(job_id, req.id, req.params, log_deque)
            elif req.engine == "csg":
                _run_csg(job_id, req.id, req.params, log_deque)
            else:
                raise ValueError(f"Unknown engine: {req.engine!r}")
        except Exception as exc:
            log_deque.append(f"__ERROR__: {exc}")
            with _jobs_lock:
                _jobs[job_id]["status"] = "error"
        finally:
            sys.stdout = real_stdout

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"job_id": job_id}


def _run_kharg(job_id: str, scenario_id: str, user_params: dict, log_deque: deque):
    build_scenarios, run_scenario_entry, _patch_scenario, _run_scenario, _STRIP, cfg = _import_kharg()

    # Find the matching scenario in build_scenarios()
    scenario_list = build_scenarios()
    matched = None
    for entry in scenario_list:
        fname_id = entry[2].replace(".kmz", "")
        if fname_id == scenario_id:
            matched = entry
            break

    if matched is None:
        raise ValueError(f"Kharg scenario not found: {scenario_id!r}")

    label, overrides, fname, desc = matched

    # Merge user param overrides on top of scenario overrides
    merged_overrides = dict(overrides)
    for k, v in user_params.items():
        merged_overrides[k] = v

    # Determine output path
    out_kmz = os.path.join(_SCENARIOS_DIR, fname)

    # Replicate run_scenario_entry logic with merged overrides
    if "pre_strike_survival_pct" in merged_overrides:
        pre_pct = merged_overrides["pre_strike_survival_pct"]
        if pre_pct == 0.0:
            pre_pct = None
    elif merged_overrides.get("beach_assault"):
        pre_pct = 0.08
    else:
        pre_pct = None

    n_pre    = merged_overrides.get("n_irgc", cfg.N_SQUADS) if pre_pct else None
    iran_ret = merged_overrides.get("iran_retaliation", True)
    patch_args = {k: v for k, v in merged_overrides.items() if k not in _STRIP}

    print(f"\n{'='*60}")
    print(f"SCENARIO: {label}")
    print('='*60)

    with _patch_scenario(**patch_args,
                         beach_assault=merged_overrides.get("beach_assault", False)):
        result = _run_scenario(out_kmz, scenario_label=label,
                               pre_strike_survival_pct=pre_pct,
                               n_irgc_pre=n_pre,
                               iran_retaliation=iran_ret,
                               scenario_desc=desc)

    with _jobs_lock:
        _jobs[job_id]["result_dict"] = result
        _jobs[job_id]["kmz_path"]    = out_kmz
        _jobs[job_id]["status"]      = "done"

    log_deque.append("__DONE__")


def _run_csg(job_id: str, scenario_id: str, user_params: dict, log_deque: deque):
    import zipfile as _zf
    CSG_SCENARIOS, generate_scenario = _import_csg()

    if scenario_id not in CSG_SCENARIOS:
        raise ValueError(f"CSG scenario not found: {scenario_id!r}")

    # Apply user param overrides by temporarily patching SCENARIOS[key]
    original = dict(CSG_SCENARIOS[scenario_id])
    try:
        for k, v in user_params.items():
            if k not in _CSG_EXCLUDE_KEYS:
                CSG_SCENARIOS[scenario_id][k] = v

        rank = (_CSG_RANK_ORDER.index(scenario_id) + 1
                if scenario_id in _CSG_RANK_ORDER else 0)
        fname = f"scenario_{rank:02d}_{scenario_id}.kmz"
        out_kmz = os.path.join(_SCENARIOS_DIR, fname)

        seeds = {
            "low": 42, "medium": 7, "high": 13, "realistic": 99,
            "iran_best": 77, "usa_best": 11,
            "drone_first_low": 55, "drone_first_medium": 66, "drone_first_high": 88,
            "coordinated_strike": 99, "focused_salvo": 99, "hypersonic_threat": 99,
            "ballistic_barrage": 33, "ascm_swarm": 44, "shore_based_defense": 99,
            "strait_transit": 99, "caves": 99,
            "depleted_drone_first": 42, "depleted_coastal": 42,
            "depleted_israel_split": 42, "us_win_preemption": 42,
            "us_win_ew_dominance": 42, "us_win_allied_umbrella": 42,
            "us_win_c2_disrupted": 42, "us_win_arsenal_attrition": 42,
            "one_percent_probe": 17, "one_percent_fatah2": 19, "ballistic_surge": 55,
        }
        seed = seeds.get(scenario_id, 42)

        print(f"\n{'='*60}")
        print(f"CSG SCENARIO: {scenario_id}")
        print('='*60)

        kml_content, legend_states, n_launched, n_intercepted, n_breakthrough, dur_min, costs = \
            generate_scenario(scenario_id, seed=seed, out_dir=_SCENARIOS_DIR)

        # Write KMZ
        os.makedirs(_SCENARIOS_DIR, exist_ok=True)
        with _zf.ZipFile(out_kmz, "w", _zf.ZIP_DEFLATED) as zf:
            zf.writestr("doc.kml", kml_content.encode("utf-8"))
            for img_path, _, _ in legend_states:
                if os.path.exists(img_path):
                    zf.write(img_path, f"images/{os.path.basename(img_path)}")

        size_mb = os.path.getsize(out_kmz) / 1_048_576
        print(f"  {scenario_id}: {n_launched} launched | {n_intercepted} intercepted | "
              f"{n_breakthrough} breakthrough | ~{dur_min:.0f} min | {size_mb:.1f} MB -> {out_kmz}")
        print("Done.")

        result = {
            "n_launched":            n_launched,
            "n_intercepted":         n_intercepted,
            "n_breakthrough":        n_breakthrough,
            "intercept_rate_actual": costs.get("intercept_rate_actual", 0.0),
            "duration_min":          dur_min,
            "iran_cost_usd":         costs.get("iran_cost", 0.0),
            "us_total_cost_usd":     costs.get("total_us_cost", 0.0),
            "exchange_ratio":        costs.get("exchange_ratio", 0.0),
            "us_kia":                costs.get("us_mil_kia", 0),
            "us_wia":                costs.get("us_mil_wia", 0),
        }

    finally:
        # Restore original scenario dict
        CSG_SCENARIOS[scenario_id].clear()
        CSG_SCENARIOS[scenario_id].update(original)

    with _jobs_lock:
        _jobs[job_id]["result_dict"] = result
        _jobs[job_id]["kmz_path"]    = out_kmz
        _jobs[job_id]["status"]      = "done"

    log_deque.append("__DONE__")


# ---------------------------------------------------------------------------
# /api/stream/{job_id}  — SSE
# ---------------------------------------------------------------------------
@app.get("/api/stream/{job_id}")
def stream_job(job_id: str):
    with _jobs_lock:
        if job_id not in _jobs:
            raise HTTPException(status_code=404, detail="Job not found")

    def _event_gen():
        import time
        sent = 0
        while True:
            with _jobs_lock:
                job = _jobs.get(job_id)
            if job is None:
                yield "data: __ERROR__: job disappeared\n\n"
                return

            log = job["log_lines"]
            lines = list(log)
            while sent < len(lines):
                line = lines[sent]
                sent += 1
                if line == "__DONE__":
                    yield "data: __DONE__\n\n"
                    return
                if line.startswith("__ERROR__:"):
                    yield f"data: {line}\n\n"
                    return
                # Escape SSE data (newlines in line would break framing)
                safe = line.replace("\n", " ")
                yield f"data: {safe}\n\n"

            status = job["status"]
            if status in ("done", "error") and sent >= len(list(job["log_lines"])):
                if status == "done":
                    yield "data: __DONE__\n\n"
                else:
                    yield "data: __ERROR__: scenario run failed\n\n"
                return

            time.sleep(0.1)

    return StreamingResponse(
        _event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# /api/results/{job_id}
# ---------------------------------------------------------------------------
@app.get("/api/results/{job_id}")
def get_results(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=404, detail="Results not ready yet")
    return job["result_dict"]


# ---------------------------------------------------------------------------
# /api/download/{job_id}
# ---------------------------------------------------------------------------
@app.get("/api/download/{job_id}")
def download_kmz(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "done" or not job["kmz_path"]:
        raise HTTPException(status_code=404, detail="KMZ not ready yet")
    kmz_path = job["kmz_path"]
    if not os.path.exists(kmz_path):
        raise HTTPException(status_code=404, detail="KMZ file missing")
    filename = os.path.basename(kmz_path)
    return FileResponse(
        kmz_path,
        media_type="application/vnd.google-earth.kmz",
        filename=filename,
    )


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Static mounts + SPA root
# ---------------------------------------------------------------------------
if os.path.isdir(_SCENARIOS_DIR):
    app.mount("/output", StaticFiles(directory=_SCENARIOS_DIR), name="output")

# Serve index.html explicitly at "/" — do NOT use StaticFiles(directory=_WEB_DIR)
# mounted at "/" because Starlette's prefix matching would intercept /api/* routes.
@app.get("/")
def serve_index():
    index_path = os.path.join(_WEB_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path, media_type="text/html")


@app.get("/worker.js")
def serve_worker_js():
    """Serve the Pyodide Web Worker script."""
    path = os.path.join(_WEB_DIR, "worker.js")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="worker.js not found")
    return FileResponse(path, media_type="application/javascript")


@app.get("/persian_gulf_simulation/{file_path:path}")
def serve_python_source(file_path: str):
    """Serve simulation Python source files for the Pyodide worker to fetch.

    Only .py files are served; path traversal is rejected.
    """
    # Reject path traversal
    clean = os.path.normpath(file_path)
    if ".." in clean.split(os.sep):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Only serve Python source files
    if not clean.endswith(".py"):
        raise HTTPException(status_code=403, detail="Only .py files are served")

    full_path = os.path.join(_REPO_ROOT, "persian_gulf_simulation", clean)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path, media_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
