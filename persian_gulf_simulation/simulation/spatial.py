"""
simulation/spatial.py — Spatial utilities for the Kharg Island simulation.

Contains: dist_km, step_toward, ts, ts_offset, ts_hhmm, _cell,
          build_grid, neighbors_in_range.
"""

import math

import persian_gulf_simulation.config as cfg


def dist_km(lon1, lat1, lon2, lat2):
    dlat = (lat2 - lat1) * cfg.LAT_KM
    dlon = (lon2 - lon1) * cfg.LON_KM
    return math.sqrt(dlat * dlat + dlon * dlon)


def step_toward(lon, lat, tlon, tlat, speed_kps):
    d = dist_km(lon, lat, tlon, tlat)
    move = speed_kps * cfg.STEP_S
    if d <= move or d == 0.0:
        return tlon, tlat
    frac = move / d
    return lon + (tlon - lon) * frac, lat + (tlat - lat) * frac


def ts(step):
    total_s = cfg.SIM_BASE_H * 3600 + step * cfg.STEP_S
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{cfg.SIM_DATE}T{h:02d}:{m:02d}:{s:02d}Z"


def ts_offset(step, extra_s):
    """Timestamp at step start + extra_s seconds (for sub-step precision)."""
    total_s = cfg.SIM_BASE_H * 3600 + step * cfg.STEP_S + extra_s
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{cfg.SIM_DATE}T{h:02d}:{m:02d}:{s:02d}Z"


def ts_hhmm(step):
    total_s = cfg.SIM_BASE_H * 3600 + step * cfg.STEP_S
    total_h = total_s // 3600
    m       = (total_s % 3600) // 60
    return f"{total_h:02d}:{m:02d}Z"


def _cell(lon, lat):
    return (int(lon / cfg.GRID_CELL), int(lat / cfg.GRID_CELL))


def build_grid(agents):
    grid = {}
    for a in agents:
        if a.hp > 0:
            c = _cell(a.lon, a.lat)
            grid.setdefault(c, []).append(a)
    return grid


def neighbors_in_range(lon, lat, grid, range_km):
    cell_r = max(1, int(range_km / (cfg.GRID_CELL * cfg.LAT_KM)) + 1)
    cx, cy = _cell(lon, lat)
    result = []
    for dx in range(-cell_r, cell_r + 1):
        for dy in range(-cell_r, cell_r + 1):
            for a in grid.get((cx + dx, cy + dy), []):
                if dist_km(lon, lat, a.lon, a.lat) <= range_km:
                    result.append(a)
    return result
