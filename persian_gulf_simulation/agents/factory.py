"""
agents/factory.py — All init_* factory functions for the Kharg Island simulation.

CRITICAL: imports config as a module (not 'from config import X') so that
_patch_scenario()'s setattr(cfg, name, val) calls are seen at runtime.
"""

import math

import persian_gulf_simulation.config as cfg
from persian_gulf_simulation.agents.base import Agent
from persian_gulf_simulation.geography import (
    _point_in_polygon, _sample_in_polygon,
    IRGC_POLYGON, IRGC_POLY_BBOX,
)


def init_marines(rng):
    agents       = []
    flights      = {}
    team_idx     = 0
    flight_total = 0
    for launch_step, n_teams, lz in cfg.MARINE_WAVES:
        wave_flight_start = flight_total
        for i in range(n_teams):
            lz_lon = lz[0] + rng.uniform(-0.003, 0.003)
            lz_lat = lz[1] + rng.uniform(-0.003, 0.003)
            flight_id = wave_flight_start + (i // cfg.MV22_CAPACITY)
            lon = cfg.TRIPOLI_LON + rng.uniform(-0.005, 0.005)
            lat = cfg.TRIPOLI_LAT + rng.uniform(-0.005, 0.005)
            a = Agent(agent_id=f"M{team_idx:04d}", lon=lon, lat=lat, hp=cfg.MARINE_HP,
                      launch_step=launch_step, lz=(lz_lon, lz_lat))
            agents.append(a)
            flights.setdefault(flight_id, []).append(a)
            team_idx += 1
        flight_total += math.ceil(n_teams / cfg.MV22_CAPACITY)
    return agents, flights


def init_irgc(rng):
    agents      = []
    homes       = {}
    cluster_map = {}
    squad_idx   = 0
    for ci, (_, _, n_sq, _) in enumerate(cfg.IRGC_CLUSTERS):
        for _ in range(n_sq):
            lon, lat = _sample_in_polygon(rng)
            a = Agent(agent_id=f"I{squad_idx:04d}", lon=lon, lat=lat, hp=cfg.IRGC_HP)
            agents.append(a)
            homes[a.agent_id]       = (lon, lat)
            cluster_map[a.agent_id] = ci
            squad_idx += 1
    return agents, homes, cluster_map


def init_stingers(rng):
    weights = [n_sq for (_, _, n_sq, _) in cfg.IRGC_CLUSTERS]
    total_w = sum(weights)
    counts  = [max(1, round(cfg.N_STINGER_TEAMS * w / total_w)) for w in weights]
    while sum(counts) > cfg.N_STINGER_TEAMS:
        counts[counts.index(max(counts))] -= 1
    while sum(counts) < cfg.N_STINGER_TEAMS:
        counts[counts.index(min(counts))] += 1
    agents = []
    st_idx = 0
    for _, n_st in zip(cfg.IRGC_CLUSTERS, counts):
        for _ in range(n_st):
            lon, lat = _sample_in_polygon(rng)
            a = Agent(agent_id=f"ST{st_idx:03d}", lon=lon, lat=lat, hp=cfg.STINGER_HP)
            agents.append(a)
            st_idx += 1
    return agents


def init_ospreys(rng, flights, flight_lz_center):
    total_flights   = max(flights.keys()) + 1 if flights else 0
    osprey_trip_map = {f"OV{i:02d}": [] for i in range(cfg.OSPREYS_PER_SORTIE)}
    for fid in range(total_flights):
        ov_id = f"OV{fid % cfg.OSPREYS_PER_SORTIE:02d}"
        osprey_trip_map[ov_id].append(fid)
    ospreys = []
    for i in range(cfg.OSPREYS_PER_SORTIE):
        ov_id = f"OV{i:02d}"
        trips = osprey_trip_map[ov_id]
        if not trips:
            continue
        first_lz = flight_lz_center[trips[0]]
        lon = cfg.TRIPOLI_LON + rng.uniform(-0.003, 0.003)
        lat = cfg.TRIPOLI_LAT + rng.uniform(-0.003, 0.003)
        a = Agent(agent_id=ov_id, lon=lon, lat=lat, hp=1,
                  launch_step=0, lz=first_lz)
        ospreys.append(a)
    return ospreys, osprey_trip_map


def init_drones(rng):
    drones = []
    for i, orbit in enumerate(cfg.DRONE_ORBITS[:cfg.N_US_DRONES]):
        a = Agent(agent_id=f"DR{i:02d}",
                  lon=cfg.DRONE_LAUNCH_LON + rng.uniform(-0.004, 0.004),
                  lat=cfg.DRONE_LAUNCH_LAT + rng.uniform(-0.003, 0.003),
                  hp=1, launch_step=0, lz=orbit)
        a.drone_ammo = cfg.DRONE_HELLFIRE
        drones.append(a)
    return drones


def init_ships():
    ships = []
    for sid, lon, lat, hp, _name, _cls in cfg.SHIP_DEFS:
        a = Agent(agent_id=sid, lon=lon, lat=lat, hp=hp)
        ships.append(a)
    return ships


def init_drone_boats(rng, ships):
    """50 IRGCN FIAC drone boats. Target split: 50% Tripoli, 25% each LPD."""
    n0 = cfg.N_DRONE_BOATS // 2
    n1 = cfg.N_DRONE_BOATS // 4
    n2 = cfg.N_DRONE_BOATS - n0 - n1
    target_lzs = (
        [(ships[0].lon, ships[0].lat)] * n0 +
        [(ships[1].lon, ships[1].lat)] * n1 +
        [(ships[2].lon, ships[2].lat)] * n2
    )
    rng.shuffle(target_lzs)
    agents = []
    for i in range(cfg.N_DRONE_BOATS):
        lon = cfg.DBOAT_LAUNCH_LON + rng.uniform(-cfg.DBOAT_SPREAD_DEG, cfg.DBOAT_SPREAD_DEG)
        lat = cfg.DBOAT_LAUNCH_LAT + rng.uniform(-cfg.DBOAT_SPREAD_DEG / 2, cfg.DBOAT_SPREAD_DEG / 2)
        a = Agent(agent_id=f"DB{i:03d}", lon=lon, lat=lat, hp=cfg.DBOAT_HP,
                  lz=target_lzs[i])
        agents.append(a)
    return agents


def init_iran_bm(rng):
    """Multi-site SRBM salvo — Fateh-313 (Shiraz + Bushehr) and Zolfaghar (Bandar Abbas).
    Launch sites and missile types match generate_wargame_kml.py CSG IRAN_SITES exactly.
    Staggered 10 missiles/step over 10 steps for a rolling-wave visual in KML."""
    n_waves   = 10
    wave_size = max(1, cfg.N_IRAN_BM // n_waves)

    # Build site pool from IRAN_BM_SITES fractions
    site_pool = []
    for slon, slat, _sname, peak_alt, frac in cfg.IRAN_BM_SITES:
        count = round(frac * cfg.N_IRAN_BM)
        site_pool.extend([(slon, slat, peak_alt)] * count)
    # Pad or trim to exactly N_IRAN_BM then shuffle for mixed site ordering
    while len(site_pool) < cfg.N_IRAN_BM:
        site_pool.append(site_pool[-1])
    site_pool = site_pool[:cfg.N_IRAN_BM]
    rng.shuffle(site_pool)

    agents = []
    for i, (slon, slat, peak_alt) in enumerate(site_pool):
        # Small positional jitter within the launch complex (~5–10 km radius)
        lon = slon + rng.uniform(-0.06, 0.06)
        lat = slat + rng.uniform(-0.06, 0.06)
        tlon, tlat = _sample_in_polygon(rng)
        ls = cfg.IRAN_BM_SALVO_STEP + (i // wave_size)
        a = Agent(agent_id=f"BM{i:03d}", lon=lon, lat=lat, hp=1,
                  launch_step=ls, lz=(tlon, tlat), peak_alt_m=peak_alt)
        agents.append(a)
    return agents


def init_island_shahed(rng):
    """Shahed-136 loitering munitions targeting marine positions on island.
    AI_DRONE_FRACTION of agents are marked is_ai=True — harder to intercept."""
    n_ai   = round(cfg.N_ISLAND_SHAHED * cfg.AI_DRONE_FRACTION)
    ai_set = set(rng.sample(range(cfg.N_ISLAND_SHAHED), n_ai)) if n_ai > 0 else set()
    agents = []
    for i in range(cfg.N_ISLAND_SHAHED):
        lon = cfg.SHAHED_LAUNCH_LON + rng.uniform(-cfg.SHAHED_SPREAD_LON, cfg.SHAHED_SPREAD_LON)
        lat = cfg.SHAHED_LAUNCH_LAT + rng.uniform(-cfg.SHAHED_SPREAD_LAT, cfg.SHAHED_SPREAD_LAT)
        tlon, tlat = _sample_in_polygon(rng)
        a = Agent(agent_id=f"IS{i:04d}", lon=lon, lat=lat, hp=cfg.SHAHED_HP, lz=(tlon, tlat))
        a.is_ai = i in ai_set
        agents.append(a)
    return agents


def init_sailors(rng):
    """2,500 sailors across three ships, represented as 625 four-man groups.
    Distribution: Tripoli 350 groups (1,400), San Diego 150 (600), Boulder 125 (500).
    Sailors fight at SAILOR_PK when sent ashore as a last-resort wave."""
    dist = [
        (cfg.SHIP_DEFS[0], 350),   # Tripoli (LHA-7) — largest complement
        (cfg.SHIP_DEFS[1], 150),   # San Diego (LPD-29)
        (cfg.SHIP_DEFS[2], 125),   # Boulder (LPD-30)
    ]
    agents = []
    sal_idx = 0
    for (sid, lon, lat, hp, _name, _cls), n_groups in dist:
        for _ in range(n_groups):
            slon = lon + rng.uniform(-0.002, 0.002)
            slat = lat + rng.uniform(-0.002, 0.002)
            a = Agent(agent_id=f"SAL{sal_idx:04d}", lon=slon, lat=slat,
                      hp=cfg.SAILOR_HP, launch_step=0, lz=None)
            a.is_sailor = True
            agents.append(a)
            sal_idx += 1
    return agents


def init_shahed(rng, ships):
    """50 Shahed-136 loitering munitions. Target split: 60% Tripoli, 25%/15% LPDs."""
    n0 = int(cfg.N_SHAHED * 0.60)
    n1 = int(cfg.N_SHAHED * 0.25)
    n2 = cfg.N_SHAHED - n0 - n1
    target_lzs = (
        [(ships[0].lon, ships[0].lat)] * n0 +
        [(ships[1].lon, ships[1].lat)] * n1 +
        [(ships[2].lon, ships[2].lat)] * n2
    )
    rng.shuffle(target_lzs)
    agents = []
    n_ai   = round(cfg.N_SHAHED * cfg.AI_DRONE_FRACTION)
    ai_set = set(rng.sample(range(cfg.N_SHAHED), n_ai)) if n_ai > 0 else set()
    for i in range(cfg.N_SHAHED):
        lon = cfg.SHAHED_LAUNCH_LON + rng.uniform(-cfg.SHAHED_SPREAD_LON, cfg.SHAHED_SPREAD_LON)
        lat = cfg.SHAHED_LAUNCH_LAT + rng.uniform(-cfg.SHAHED_SPREAD_LAT, cfg.SHAHED_SPREAD_LAT)
        a = Agent(agent_id=f"SH{i:04d}", lon=lon, lat=lat, hp=cfg.SHAHED_HP,
                  lz=target_lzs[i])
        a.is_ai = i in ai_set
        agents.append(a)
    return agents
