#!/usr/bin/env python3
"""
Persian Gulf Wargame KML Generator
===================================
Eight-CSG simulation of Iranian mass-missile attacks on US Carrier Strike Groups,
with US TLAM/JASSM counterstrikes against Iranian launch sites.

Key features
------------
- 8 US Carrier Strike Groups: Lincoln, Ford, GHW Bush + CSG Alpha/Bravo/Charlie/Delta/Echo
- Researched SM-6/SM-2/ESSM/RAM low/high magazine estimates per CSG (unclassified)
- US counterstrikes (TLAM Block IV / JASSM-ER) against 12 Iranian launch sites
- Launch sites deactivate after 25 cumulative US strike hits; inactive sites stop launching
- Each munition type has its own distinct color (KML AABBGGRR)
- Parabolic / sea-skim arcs broken into 2-point LineString segments with TimeSpan
- Staggered launch waves; flight duration from great-circle distance / munition speed
- Shahed-136 counts capped at 5,000 per scenario (post-50% preemptive strike)
- Scenario D (Realistic) uses iran_detection_launch=True: Iran fires entire salvo on IAF radar detection,
  compressing all launches into 30 min so no pre-launch suppression is possible.

Iranian Inventory Estimates (open-source, current as of Q1 2026)
-----------------------------------------------------------------
Shahed-136 loitering munitions:
  - Pre-conflict (2024): estimated 10,000–20,000+ units domestically. Export to Russia
    consumed an estimated 3,000–6,000 units (2022–2024). Iran's domestic production
    rate reached ~6,000–7,000/month at full surge (NBC News, ISIS Reports, 2025–2026).
  - Shahed-238 (jet-powered variant, "Geran-3" in Russian service): Mach 0.9+ speed,
    EO/IR terminal guidance; confirmed combat use from Jan 2024.
  - AI/jam-resistant variants with computer-vision terminal seeker entering service 2025.
  - Unit cost: $20K–$50K domestic (CSIS Feb 2025); $35K median used here.
  - Iran export price to Russia: ~$193K–$200K/unit (Defence Express, leaked contract).

Ballistic missiles (JINSA 2025 assessment; USNI News CRS report 2025):
  - SRBMs (Fateh-110, Fateh-313, Zolfaghar): ~6,000–8,000 pre-2024.
  - MRBMs (Shahab-3, Emad): ~2,000 pre-2024.
  - October 2024: Israeli strikes destroyed 12 solid-fuel planetary mixers, degrading
    SRBM/MRBM production capacity for at least 1 year (Axios, October 2024).
  - Post-June 2025 war: ~1,500 missiles remaining; reconstituted to ~2,500 by Feb 2026
    (Alma Research, 19FortyFive, Feb 2026).
  - Fattah-1 HGV (Mach 13+ claimed, 1,400 km range): operational; used Oct 2024.
  - Fattah-2 HGV (Mach 15 claimed, maneuvering RV): first reported combat use Mar 2026.

IRGCN naval drones / fast boats:
  - Hundreds of fast attack craft; USVs (explosive boats) in dozens to low hundreds.
  - Swarming doctrine: 1 operator controls ~10 autonomous/semi-autonomous USVs.
  - Confirmed operational in Hormuz: March 2026 (6 commercial vessels hit in one day).

CM-302 supersonic ASCM (Chinese origin):
  - China reportedly supplied CM-302 (~Mach 3, 250 kg warhead) covertly to Iran as of
    March 2026 (GlobalDefenseCorp, CNN 2025). Inventory numbers unknown.

Real-world calibration data (April & October 2024 attacks on Israel):
  - April 13–14, 2024 (True Promise I): ~170 Shahed drones + ~30 cruise missiles +
    ~120 ballistic missiles = ~320 total. Intercept rate: ~99% (US + Jordan + Israel
    coalition). Cost to Iran: ~$80–100M. Cost to defenders: ~$1 billion.
  - October 1–2, 2024 (True Promise II): ~180–200 ballistic missiles only; ~15–20%
    reached targets (vs ~1% in April). ~32 impact points at Nevatim Airbase confirmed
    by satellite — no aircraft destroyed, base operational. US contribution: 12 SM-3/SM-6.
  - Key insight: removing allied ground-based radar and Jordan/France intercept layers
    (which apply in the Persian Gulf scenario) raises breakthrough rate substantially.

Armament sources: CRS RL33199; IISS Military Balance 2024; NAVSEA public briefs;
  USNI News deployment tracking; FAS.org; CSIS Missile Threat database;
  JINSA June 2025 assessment; Alma Research Feb 2026; influenceofhistory.blogspot.com
  loadout analysis; War on the Rocks 2026; Defence Express; The War Zone.

Scenarios (approximate totals after 5K Shahed cap)
---------
  A -- Low:                   ~265 missiles + ~665 air drones + ~135 sea drones  =  ~1,065 total
  B -- Medium:                ~665 missiles + ~1,335 air drones + ~200 sea drones =  ~2,200 total
  C -- High (CAP hit):      ~1,100 missiles + ~2,665 air drones + ~265 sea drones =  ~4,030 total  [intercept cap breached]
  D -- Realistic:             ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [simultaneous detection-launch]
  E -- Iran Best (CAP hit): ~1,000 missiles + ~4,000 air drones + ~400 sea drones =  ~5,400 total  [intercept cap breached]
  F -- USA Best:              ~200 missiles +   ~400 air drones +  ~65 sea drones =    ~665 total
  G -- Drone-First Low:       ~265 missiles + ~665 air drones + ~135 sea drones  =  ~1,065 total  [phased assault]
  H -- Drone-First Medium:    ~665 missiles + ~1,335 air drones + ~200 sea drones =  ~2,200 total  [phased assault]
  I -- Drone-First High:    ~1,100 missiles + ~2,665 air drones + ~265 sea drones =  ~4,030 total  [phased assault, CIWS exhausted]
  J -- Coordinated Strike:    ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [US/IAF perfect timing]
  K -- Focused Salvo:         ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [all fire on CVN-78 Ford]
  L -- Hypersonic Threat:     ~650 missiles + ~5,000 air drones + ~265 sea drones =  ~7,250 total  [Fattah-1 HGV layer]
  M -- Ballistic Barrage:     ~600 ballistic missiles, no drones                  =    ~600 total  [pure ballistic]
  N -- ASCM Swarm:          ~1,000 anti-ship cruise missiles, no drones           =  ~1,000 total  [sea-skim saturation]
  O -- Shore Defense:         ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [THAAD+Patriot+Aegis]
  P -- Strait Transit:        ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [column transit, max threat]
  Q -- Cave Network:          ~650 missiles + ~5,000 air drones + ~990 sea drones =  ~7,250 total  [25 dispersed cave sites]
  Z -- 1% Probe+Lull+Strike:    ~20 missiles +  ~45 air drones + ~10 sea drones   =     ~75 total  [drone probe → 60-min ISR lull → precision follow-on]
 AA -- 1% + 10 Fattah-2 HGVs:  ~10 Fattah-2 + ~10 ballistic + ~45 drones + ~10 sea =  ~75 total  [10 secured HGVs in cave tunnels; ~9-10 near-uninterceptable strikes]
  R -- Depleted Drone-First:  ~174 missiles + ~336 air drones + ~70 sea drones   =    ~580 total  [8% inventory, phased]
  S -- Depleted Coastal:      ~174 missiles + ~336 air drones + ~70 sea drones   =    ~580 total  [8% inventory, all sites]
  T -- Depleted Israel Split: ~174 missiles + ~168 air drones + ~70 sea drones   =    ~412 Gulf  [8% inventory, split attack]
  U -- US Wins: Preemption:   ~280 missiles, no drones                           =    ~280 total  [P_win ≈ 94%, 85% launch degraded]
  V -- US Wins: EW Dominance: ~450 ballistic only (guidance systems jammed)      =    ~450 total  [P_win ≈ 88%]
  W -- US Wins: Allied Umbrella: ~550 mixed (five-layer coalition defense)       =    ~550 total  [P_win ≈ 83%]
  X -- US Wins: C2 Disrupted: ~900 fragmented, no salvo coordination             =    ~900 total  [P_win ≈ 71%]
  Y -- US Wins: Arsenal Attrited: ~750 legacy-only (prior war degraded)          =    ~750 total  [P_win ≈ 65%]
 BB -- Full Ballistic Surge:    ~2,500 ballistic missiles, no drones             =  ~2,500 total  [full reconstituted stockpile, 10% Fattah-1 HGV]

Output
------
  scenarios/scenario_low.kml              scenarios/scenario_low.html
  scenarios/scenario_medium.kml           scenarios/scenario_medium.html
  scenarios/scenario_high.kml             scenarios/scenario_high.html
  scenarios/scenario_realistic.kml        scenarios/scenario_realistic.html
  scenarios/scenario_iran_best.kml        scenarios/scenario_iran_best.html
  scenarios/scenario_usa_best.kml         scenarios/scenario_usa_best.html
  scenarios/scenario_drone_first_low.kml       scenarios/scenario_drone_first_low.html
  scenarios/scenario_drone_first_medium.kml    scenarios/scenario_drone_first_medium.html
  scenarios/scenario_drone_first_high.kml      scenarios/scenario_drone_first_high.html
  scenarios/scenario_coordinated_strike.kml    scenarios/scenario_coordinated_strike.html
  scenarios/scenario_focused_salvo.kml         scenarios/scenario_focused_salvo.html
  scenarios/scenario_hypersonic_threat.kml     scenarios/scenario_hypersonic_threat.html
  scenarios/scenario_ballistic_barrage.kml     scenarios/scenario_ballistic_barrage.html
  scenarios/scenario_ascm_swarm.kml            scenarios/scenario_ascm_swarm.html
  scenarios/scenario_shore_based_defense.kml   scenarios/scenario_shore_based_defense.html
  scenarios/scenario_strait_transit.kml        scenarios/scenario_strait_transit.html
  scenarios/scenario_caves.kml                 scenarios/scenario_caves.html
  scenarios/scenario_depleted_drone_first.kml  scenarios/scenario_depleted_drone_first.html
  scenarios/scenario_depleted_coastal.kml      scenarios/scenario_depleted_coastal.html
  scenarios/scenario_depleted_israel_split.kml scenarios/scenario_depleted_israel_split.html
  scenarios/scenario_one_percent_probe.kml     scenarios/scenario_one_percent_probe.html
  scenarios/scenario_one_percent_fatah2.kml   scenarios/scenario_one_percent_fatah2.html
  scenarios/scenario_us_win_preemption.kml     scenarios/scenario_us_win_preemption.html
  scenarios/scenario_us_win_ew_dominance.kml   scenarios/scenario_us_win_ew_dominance.html
  scenarios/scenario_us_win_allied_umbrella.kml scenarios/scenario_us_win_allied_umbrella.html
  scenarios/scenario_us_win_c2_disrupted.kml   scenarios/scenario_us_win_c2_disrupted.html
  scenarios/scenario_us_win_arsenal_attrition.kml scenarios/scenario_us_win_arsenal_attrition.html
  scenarios/scenario_ballistic_surge.kml          scenarios/scenario_ballistic_surge.html
  scenarios/summary.html
  wargame_master.kml
  wargame_summary.kmz
"""

import math, random, os
from datetime import datetime, timezone, timedelta

# ============================================================
# GEODETIC CONSTANTS & HELPERS
# ============================================================
# WGS84 / IUGG 2015 volumetric mean radius — used consistently for all
# haversine distances, circle rings, and spherical dead-reckoning so that
# the same Earth model drives every coordinate in the file.
_R_EARTH_KM = 6371.0088


def destination_point(lon_deg, lat_deg, bearing_deg, dist_km):
    """
    Spherical-earth destination point given start, bearing, and distance.

    Uses the standard forward geodetic formula on a sphere of radius
    _R_EARTH_KM.  Accurate to < 0.3 % across the Persian Gulf region
    (maximum error ~1 m per 300 km at these latitudes).

    Returns (lon_deg, lat_deg) of the destination.
    """
    d   = dist_km / _R_EARTH_KM          # angular distance (radians)
    brg = math.radians(bearing_deg)
    la1 = math.radians(lat_deg)
    lo1 = math.radians(lon_deg)
    la2 = math.asin(
        math.sin(la1) * math.cos(d) +
        math.cos(la1) * math.sin(d) * math.cos(brg))
    lo2 = lo1 + math.atan2(
        math.sin(brg) * math.sin(d) * math.cos(la1),
        math.cos(d) - math.sin(la1) * math.sin(la2))
    return math.degrees(lo2), math.degrees(la2)


def gc_interp(lon1, lat1, lon2, lat2, t):
    """
    Great-circle (SLERP) interpolation between two geographic points at
    fractional position t ∈ [0, 1].

    Replaces linear lat/lon lerp, which traces a rhumb line and can deviate
    35–55 km from the true great-circle path at the midpoint of a 500 km
    trajectory.  Returns (lon_deg, lat_deg).
    """
    la1, lo1 = math.radians(lat1), math.radians(lon1)
    la2, lo2 = math.radians(lat2), math.radians(lon2)
    # Angular distance via haversine (numerically stable for small angles)
    d = 2.0 * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2 +
        math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    if d < 1e-10:
        return lon1, lat1
    A = math.sin((1.0 - t) * d) / math.sin(d)
    B = math.sin(t * d)         / math.sin(d)
    x = A * math.cos(la1) * math.cos(lo1) + B * math.cos(la2) * math.cos(lo2)
    y = A * math.cos(la1) * math.sin(lo1) + B * math.cos(la2) * math.sin(lo2)
    z = A * math.sin(la1)                  + B * math.sin(la2)
    lat = math.degrees(math.atan2(z, math.sqrt(x * x + y * y)))
    lon = math.degrees(math.atan2(y, x))
    return lon, lat


# ============================================================
# SIMULATION CLOCK
# ============================================================
SIM_START = datetime(2026, 4, 1, 6, 0, 0, tzinfo=timezone.utc)
CARRIER_SPEED_KMS = 20 * 1.852 / 3600   # 20 knots → km per second (0.010289 km/s)

def fmt_time(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def sim_time(offset_s):
    return SIM_START + timedelta(seconds=float(offset_s))

# ============================================================
# CSG SHIP FORMATION TEMPLATE  (10 ships per CSG)
# ============================================================
# ahead_km: + = forward in direction of travel, - = astern
# abeam_km: + = starboard (right), - = port (left)
# group: directional group — ships in the same group stop when any member is killed
FORMATION_TEMPLATE = [
    {"role": "CVN",  "ahead_km":  0.0, "abeam_km":  0.0,  "group": "center"},   # 0 carrier
    {"role": "CG",   "ahead_km":  5.0, "abeam_km":  2.5,  "group": "ahead"},    # 1 cruiser fwd-stbd
    {"role": "DDG",  "ahead_km": 10.0, "abeam_km":  0.0,  "group": "ahead"},    # 2 lead destroyer
    {"role": "DDG",  "ahead_km":  3.0, "abeam_km": 10.0,  "group": "star"},     # 3 starboard close
    {"role": "DDG",  "ahead_km":  3.0, "abeam_km":-10.0,  "group": "port"},     # 4 port close
    {"role": "DDG",  "ahead_km":  0.0, "abeam_km": 16.0,  "group": "star"},     # 5 starboard far
    {"role": "DDG",  "ahead_km":  0.0, "abeam_km":-16.0,  "group": "port"},     # 6 port far
    {"role": "DDG",  "ahead_km": -6.0, "abeam_km":  8.0,  "group": "astern"},   # 7 rearguard stbd
    {"role": "DDG",  "ahead_km": -6.0, "abeam_km": -8.0,  "group": "astern"},   # 8 rearguard port
    {"role": "AOE",  "ahead_km":-15.0, "abeam_km":  0.0,  "group": "astern"},   # 9 supply ship
]

_SHIP_HIT_RADIUS_M = 20.0   # metres — impact must land within this radius to count as a ship hit


def _box_muller_rng(rng):
    """Box-Muller transform consuming exactly 2 rng.random() calls.
    Returns (z0, z1) — two independent standard-normal samples."""
    u1 = max(rng.random(), 1e-12)
    u2 = rng.random()
    r  = math.sqrt(-2.0 * math.log(u1))
    th = 2.0 * math.pi * u2
    return r * math.cos(th), r * math.sin(th)


def ship_pos_at(csg, ship, t_s):
    """Return (lon, lat) of an individual CSG ship at simulation time t_s seconds.

    Ships maintain formation offsets relative to the carrier, rotated by the
    CSG heading.  Uses a flat-earth approximation valid to < 0.1 % for ≤ 50 km offsets.
    """
    csg_lon, csg_lat = csg_pos_at(csg, t_s)
    hdg = math.radians(csg.get("heading_deg", 0))
    a, b = ship["ahead_km"], ship["abeam_km"]
    # Rotate from ship-frame (ahead/abeam) to geographic (north/east)
    n_km =  a * math.cos(hdg) - b * math.sin(hdg)
    e_km =  a * math.sin(hdg) + b * math.cos(hdg)
    lat_off = n_km / 111.0
    lon_off = e_km / (111.0 * math.cos(math.radians(csg_lat)))
    return csg_lon + lon_off, csg_lat + lat_off


def generate_csg_ships(csg, rng):
    """Generate 10 ships for a CSG with random formation jitter (±1.5 km each axis).
    Returns a list of ship dicts."""
    ships = []
    for idx, tmpl in enumerate(FORMATION_TEMPLATE):
        ja = rng.uniform(-1.5, 1.5)   # ahead jitter
        jb = rng.uniform(-1.5, 1.5)   # abeam jitter
        ships.append({
            "id":       f"{csg['name']}_{idx}",
            "idx":      idx,
            "role":     tmpl["role"],
            "ahead_km": tmpl["ahead_km"] + ja,
            "abeam_km": tmpl["abeam_km"] + jb,
            "group":    tmpl["group"],
            "csg_name": csg["name"],
        })
    return ships


def csg_pos_at(csg, t_s):
    """Return (lon, lat) of csg at t_s seconds using spherical dead-reckoning.

    Replaces the flat-earth 111.0 km/° approximation with destination_point(),
    which uses the forward geodetic formula on a sphere.  Error vs WGS84
    ellipsoid is < 0.03 % at 26 °N, keeping ship positions within ~3 m for
    a 3-hour 20-knot transit (~111 km total).
    """
    d_km = CARRIER_SPEED_KMS * float(t_s)
    return destination_point(csg["lon"], csg["lat"],
                             csg.get("heading_deg", 220), d_km)

# ============================================================
# GEOGRAPHY -- 8 US CARRIER STRIKE GROUPS
# ============================================================
# VLS loadout research (all unclassified, open-source estimates):
#
#  DDG-51 Flight II/IIA (90 VLS cells) — typical wartime load per ship:
#    SM-6: 8–16 rds   SM-2: 20–48 rds   ESSM: 32 rds (8 quad-cells × 4)
#    Tomahawk: 16 rds   ASROC: 8 rds   (remaining cells other loads)
#    Sources: influenceofhistory.blogspot.com; DTIC ADA620888; USNI News
#
#  DDG-51 Flight III (96 VLS cells) — SPY-6 radar, more SM-6 emphasis:
#    SM-6: 10–18 rds   SM-2: 20–44 rds   ESSM: 32–48 rds
#
#  CG-47 Ticonderoga (122 VLS cells) — standard load per CRS / seaforces.org:
#    SM-6: 12 rds   SM-2MR: 56 rds   SM-2ER: 3 rds   ESSM: 12 rds
#    SM-3: 10 rds   Tomahawk: 32 rds   ASROC: 6 rds
#
#  CVN self-defense (not in VLS): Phalanx 2–3×, RAM 2–4× Mk 49 (21 rds ea)
#    Ford-class: 3× Mk 49 RAM (63 rds) + SeaRAM  Nimitz: 2–4× Mk 49 (42–84 rds)

US_CSGS = [
    # ── Named CSGs ────────────────────────────────────────────────────────────
    # asset_value_usd: total replacement cost of all hulls + embarked air wing
    #   Nimitz CVN hull: ~$9B (CRS RL33524; FY2023 replacement estimate)
    #   Ford  CVN hull: ~$13.3B (actual CVN-78 program cost, CRS RL33524)
    #   Carrier air wing: ~$4B (F/A-18E/F ×44, E-2D ×5, EA-18G ×5, MH-60 etc.)
    #   Ticonderoga CG: ~$1.0B (FY2023 replacement; CG-47 class decommissioning value)
    #   DDG-51 Flight II/IIA: ~$1.8B  |  Flight III: ~$2.2B  |  DDG-1000: ~$4.4B
    {
        "name":    "USS Abraham Lincoln (CVN-72)",
        "lon": 57.1126, "lat": 25.3147,
        "heading_deg": 334,
        "class":   "Nimitz",
        "has_cruiser": False,
        "escorts": "3 × DDG-51 Flight IIA (DDG-77, DDG-111, DDG-121) — no cruiser",
        # 3 DDG-51 Flight IIA × floor/ceiling per ship
        "sm6_low":   24, "sm6_high":   48,   # 8–16 per DDG × 3
        "sm2_low":   60, "sm2_high":  144,   # 20–48 per DDG × 3
        "essm_low":  96, "essm_high": 128,   # ~32 per DDG × 3
        "ram_low":   42, "ram_high":   84,   # carrier 2–4 × Mk 49
        "tlam_est":  48,                      # 16 per DDG × 3
        # legacy midpoints
        "sm6_est": 35, "sm2_est": 100, "essm_est": 112, "ram_est": 63,
        # CVN-72 ($9B hull + $4B air wing) + 3 × DDG-51 IIA ($1.8B × 3)
        "asset_value_usd": 18_400_000_000,
        # CVN ship's company (~5,000) + air wing (~2,480) + 3 × DDG crew (~280 ea)
        "personnel": 8_320,
    },
    {
        "name":    "USS Gerald R. Ford (CVN-78)",
        "lon": 56.9378, "lat": 26.5679,
        "heading_deg": 324,
        "class":   "Ford",
        "has_cruiser": True,
        "escorts": "3 × DDG-51 Flight III + CG-60 USS Normandy (122 VLS)",
        # 3 DDG Flight III + Normandy cruiser
        "sm6_low":   36, "sm6_high":   66,   # 8–16×3 DDG + 12 CG
        "sm2_low":  119, "sm2_high":  203,   # 20–48×3 DDG + 59 CG (56+3)
        "essm_low":  96, "essm_high": 144,   # 32×3 DDG + 12 CG
        "ram_low":   63, "ram_high":  105,   # Ford 3×Mk49 + some DDG RAM
        "tlam_est":  80,                      # 16×3 DDG + 32 CG
        "sm6_est": 46, "sm2_est": 175, "essm_est": 120, "ram_est": 84,
        # CVN-78 ($13.3B hull + $4B air wing incl. ~44 F/A-18E/F @$70M, 5 E-2D @$220M, 5 EA-18G @$68M)
        # + 3 × DDG-51 Flight III ($2.2B × 3) + CG-60 ($1.0B)
        "asset_value_usd": 24_900_000_000,
        # CVN ship's company (~5,000) + air wing (~2,480) + 3 × DDG-51 III (~290 ea) + CG (~400)
        "personnel": 8_750,
    },
    {
        "name":    "USS George H.W. Bush (CVN-77)",
        "lon": 55.9325, "lat": 26.3096,
        "heading_deg": 213,
        "class":   "Nimitz",
        "has_cruiser": True,
        "escorts": "3 × DDG-51 Flight IIA + CG-55 USS Leyte Gulf (122 VLS)",
        "sm6_low":   36, "sm6_high":   60,
        "sm2_low":  119, "sm2_high":  203,
        "essm_low":  96, "essm_high": 144,
        "ram_low":   42, "ram_high":  105,
        "tlam_est":  80,
        "sm6_est": 44, "sm2_est": 170, "essm_est": 120, "ram_est": 84,
        # CVN-77 ($9B hull + $4B air wing) + 3 × DDG-51 IIA ($1.8B × 3) + CG-55 ($1.0B)
        "asset_value_usd": 19_400_000_000,
        "personnel": 8_720,   # 5,000 CVN + 2,480 air wing + 3×280 DDG + 400 CG
    },
    # ── Lettered CSGs A–E ─────────────────────────────────────────────────────
    {
        "name":    "CSG Alpha",
        "lon": 54.6997, "lat": 25.7345,   # on transit path
        "heading_deg": 255,
        "class":   "Nimitz",
        "has_cruiser": False,
        "escorts": "3 × DDG-51 Flight III (DESRON Alpha) — no cruiser",
        "sm6_low":   30, "sm6_high":   54,   # Flight III: 10–18 per DDG × 3
        "sm2_low":   60, "sm2_high":  132,
        "essm_low":  96, "essm_high": 144,
        "ram_low":   42, "ram_high":   84,
        "tlam_est":  48,
        "sm6_est": 42, "sm2_est": 96, "essm_est": 120, "ram_est": 63,
        # CVN ($9B hull + $4B air wing) + 3 × DDG-51 Flight III ($2.2B × 3)
        "asset_value_usd": 19_600_000_000,
        "personnel": 8_350,   # 5,000 CVN + 2,480 air wing + 3×290 DDG-51 III
    },
    {
        "name":    "CSG Bravo",
        "lon": 53.3122, "lat": 25.9028,   # on transit path
        "heading_deg": 295,
        "class":   "Nimitz",
        "has_cruiser": True,
        "escorts": "3 × DDG-51 Flight IIA + CG-70 USS Lake Erie (122 VLS)",
        "sm6_low":   36, "sm6_high":   60,
        "sm2_low":  119, "sm2_high":  203,
        "essm_low":  96, "essm_high": 144,
        "ram_low":   42, "ram_high":  105,
        "tlam_est":  80,
        "sm6_est": 44, "sm2_est": 165, "essm_est": 120, "ram_est": 84,
        # CVN ($9B hull + $4B air wing) + 3 × DDG-51 IIA ($1.8B × 3) + CG-70 ($1.0B)
        "asset_value_usd": 19_400_000_000,
        "personnel": 8_720,   # 5,000 CVN + 2,480 air wing + 3×280 DDG + 400 CG
    },
    {
        "name":    "CSG Charlie",
        "lon": 52.0142, "lat": 26.4037,   # on transit path
        "heading_deg": 295,
        "class":   "Nimitz",
        "has_cruiser": False,
        "escorts": "4 × DDG-51 Flight IIA (DESRON Charlie) — no cruiser",
        # 4 DDGs → slightly larger magazine, no cruiser
        "sm6_low":   32, "sm6_high":   64,   # 8–16 per DDG × 4
        "sm2_low":   80, "sm2_high":  192,   # 20–48 per DDG × 4
        "essm_low": 128, "essm_high": 160,
        "ram_low":   42, "ram_high":   84,
        "tlam_est":  64,                      # 16 × 4 DDGs
        "sm6_est": 44, "sm2_est": 136, "essm_est": 144, "ram_est": 63,
        # CVN ($9B hull + $4B air wing) + 4 × DDG-51 IIA ($1.8B × 4)
        "asset_value_usd": 20_200_000_000,
        "personnel": 8_600,   # 5,000 CVN + 2,480 air wing + 4×280 DDG
    },
    {
        "name":    "CSG Delta",
        "lon": 51.0514, "lat": 27.3277,   # on transit path
        "heading_deg": 323,
        "class":   "Ford",
        "has_cruiser": True,
        "escorts": "3 × DDG-51 Flight III + CG-65 USS Chosin (122 VLS)",
        "sm6_low":   42, "sm6_high":   66,   # 10–18×3 + 12 CG
        "sm2_low":  119, "sm2_high":  203,
        "essm_low":  96, "essm_high": 156,   # 32×3 + 12 CG + some extras
        "ram_low":   63, "ram_high":  105,   # Ford 3×Mk49
        "tlam_est":  80,
        "sm6_est": 54, "sm2_est": 172, "essm_est": 126, "ram_est": 84,
        # CVN-78 class ($13.3B hull + $4B air wing) + 3 × DDG-51 III ($2.2B × 3) + CG-65 ($1.0B)
        "asset_value_usd": 24_900_000_000,
        "personnel": 8_750,   # 5,000 CVN + 2,480 air wing + 3×290 DDG-51 III + 400 CG
    },
    {
        "name":    "CSG Echo",
        "lon": 50.4517, "lat": 28.4393,   # on transit path
        "heading_deg": 343,
        "class":   "Nimitz",
        "has_cruiser": False,
        "escorts": "3 × DDG-51 Flight IIA + 1 × DDG-1000 Zumwalt (DESRON Echo)",
        # DDG-1000 focuses on strike (80 VLS, mostly Tomahawk), limited AAW
        "sm6_low":   24, "sm6_high":   48,
        "sm2_low":   60, "sm2_high":  144,
        "essm_low":  96, "essm_high": 128,
        "ram_low":   42, "ram_high":   84,
        "tlam_est": 128,                      # 16×3 DDG + 80 Zumwalt
        "sm6_est": 36, "sm2_est": 100, "essm_est": 112, "ram_est": 63,
        # CVN ($9B hull + $4B air wing) + 3 × DDG-51 IIA ($1.8B × 3) + DDG-1000 Zumwalt ($4.4B)
        "asset_value_usd": 22_800_000_000,
        "personnel": 8_460,   # 5,000 CVN + 2,480 air wing + 3×280 DDG + 140 DDG-1000
    },
]

TOTAL_CSG_PERSONNEL = sum(csg["personnel"] for csg in US_CSGS)
TOTAL_CSG_VALUE     = sum(csg["asset_value_usd"] for csg in US_CSGS)

# ── USS Tripoli (LHA-7) — targeted by drone supplement in ballistic_surge ─────
# America-class Landing Helicopter Assault ship; no SM-6/SM-2; SeaRAM + CIWS only.
USS_TRIPOLI_FLEET = {
    "name":    "USS Tripoli (LHA-7)",
    "lon": 50.635, "lat": 26.215,    # near Bahrain / 5th Fleet AOR
    "heading_deg": 340,
    "class":   "LHA",
    "has_cruiser": False,
    "escorts": "SeaRAM × 2 + Phalanx CIWS × 2 — no DDG escort modeled",
    "sm6_low":   0, "sm6_high":   0,
    "sm2_low":   0, "sm2_high":   0,
    "essm_low":  0, "essm_high":  0,
    "ram_low":  22, "ram_high":  22,   # 2 × SeaRAM (11 rounds each)
    "tlam_est":  0,
    "sm6_est": 0, "sm2_est": 0, "essm_est": 0, "ram_est": 22,
    # LHA-7 hull ($3.5B) + embarked F-35B air wing ($1.3B)
    "asset_value_usd": 4_800_000_000,
    # ~1,800 crew + ~1,800 embarked Marines (MAGTF)
    "personnel": 3_600,
}

# 4-CSG fleet for the ballistic_surge scenario: the 3 named CVNs + CSG Alpha ("the first")
BALLISTIC_SURGE_CSGS = [
    c for c in US_CSGS if c["name"] in {
        "USS Abraham Lincoln (CVN-72)",
        "USS Gerald R. Ford (CVN-78)",
        "USS George H.W. Bush (CVN-77)",
        "CSG Alpha",
    }
]
# Include USS Tripoli as the drone target element (5th fleet member)
BALLISTIC_SURGE_WITH_TRIPOLI = BALLISTIC_SURGE_CSGS + [USS_TRIPOLI_FLEET]

# ── Strait of Hormuz column formation ────────────────────────────────────────
# 8 CSGs in single-file column transiting the strait, lead at (56.515, 26.622),
# heading 310° (NW into the Gulf), 15 km between ships.
_STRAIT_LEAD_LON, _STRAIT_LEAD_LAT = 56.515, 26.622
_STRAIT_HDG = 310
_STRAIT_SP  = 15   # km between ships (trail spacing)
# Trail bearing is reciprocal of column heading (310° → 130°).
# Use destination_point() for correct spherical spacing; _sd_* are the
# per-ship lon/lat deltas applied by multiplying by ship index.
_trail_lon, _trail_lat = destination_point(
    _STRAIT_LEAD_LON, _STRAIT_LEAD_LAT, 130, _STRAIT_SP)
_sd_lon = _trail_lon - _STRAIT_LEAD_LON
_sd_lat = _trail_lat - _STRAIT_LEAD_LAT
STRAIT_CSGS = []
for _si, _sc in enumerate(US_CSGS):
    _entry = dict(_sc)
    _entry["lon"] = round(_STRAIT_LEAD_LON + _si * _sd_lon, 6)
    _entry["lat"] = round(_STRAIT_LEAD_LAT + _si * _sd_lat, 6)
    _entry["heading_deg"] = _STRAIT_HDG
    STRAIT_CSGS.append(_entry)

# Weapon engagement ranges (km) — unclassified published figures
WPN_RANGES = {
    "SM-6":  240,
    "SM-2":  167,
    "ESSM":   50,
    "RAM":    15,
    "CIWS_AA": 1.5,
    "CIWS_SF": 2.5,
}

# ============================================================
# AIR SUPPORT — Israeli Air Force + US Carrier Air Wings
# ============================================================
# Israeli Air Force force estimates (Jane's DW 2024; FAS.org; IISS Military Balance 2024):
#   F-35I Adir:  50 delivered (140th "Golden Eagle" + 116th "Defenders of the South" sqns,
#                Nevatim AB; 25 more on order for 117th sqn); 75% MCR → 37 combat-ready;
#                with aerial refuelling range is limited only by pilot endurance;
#                2 × JDAM-ER internally stealth; source: Jane's DW 2024
#   F-15I Ra'am: 25 aircraft (F-15I+ MLU upgrade ongoing); combat radius ~1,600 km;
#                2 × Rampage ALCM (250 km) or 2 × SPICE-2000; source: Jane's DW 2024
#   F-16I Sufa:  97 aircraft as of Jul 2024 (Israel retired Barak-1 F-16s);
#                conformal fuel tanks; radius ~1,600 km; 2 × SPICE-250; source: Jane's DW
#   IAF tankers: 8 × Boeing 707 tanker-transport; KC-46A Pegasus approved to replace;
#                source: Jane's DW / FAS.org
#   Realistic Gulf sortie rate: 1 package/day × 3 days; F-35I 55 sorties (37×75%×2d),
#                F-15I 40, F-16I 73 (Gulf-capable) → ~168 sorties / ~336 munitions total
#
# US Carrier Air Wing (per CVN, USNI/NAVAIR; Jane's DW):
#   ~70 F/A-18E/F Super Hornet per CVW across 4 VFA sqns ($70 M each);
#   5 × EA-18G Growler ($68 M); 5 × E-2D Hawkeye ($220 M)
#   CAP: 4–6 F/A-18F always airborne; 6–8 × AIM-120C/D AMRAAM each
#   AIM-120C-8 FMS price: ~$2.46 M/rnd (incl. support); unit cost ~$1.8 M; source: Jane's DW
#   AIM-120D-3 FMS price: ~$3.03 M/rnd; unit cost ~$2.2 M
#   → ~200 AMRAAM shots/day per CSG × 8 CSGs = 1,600 shots/day
#   Air-launched strikes: SLAM-ER (AGM-84H, 280 km, $1.3 M) — 1–2 per F/A-18E
#   → ~40–60 SLAM-ER per CSG per day; 8 CSGs × 50 × 2 days ≈ 800 total SLAM-ER

# IAF launch bases (representative; Nevatim = F-35I; Hatzerim = F-15I; Ramon = F-16I)
IAF_BASES = [
    {"name": "Nevatim AB (F-35I)",  "lon": 34.99, "lat": 31.21,
     "aircraft": "F-35I Adir", "sorties": 55,  "munition": "JDAM-ER",      "per_sortie": 4},
    {"name": "Hatzerim AB (F-15I)", "lon": 34.67, "lat": 31.23,
     "aircraft": "F-15I Ra'am", "sorties": 40, "munition": "Rampage ALCM", "per_sortie": 4},
    {"name": "Ramon AB (F-16I)",    "lon": 34.74, "lat": 30.78,
     "aircraft": "F-16I Sufa",  "sorties": 73,  "munition": "SPICE-2000",  "per_sortie": 4},
]

IAF_MUNITIONS = {
    # AABBGGRR: bright lime/teal for IAF (distinct from US blues and Iran reds)
    "JDAM-ER": {
        "speed_km_s": 0.300, "peak_alt_m": 10_000, "sea_skim": False,
        "color": "cc00ff88", "width": 2,
        "label": "JDAM-ER (lime-teal — Israeli F-35I strike, 80 km glide bomb)",
        "cost_usd": 30_000,   # FY2023 JDAM kit + ER wing (~$30k per munition)
        "max_range_km": 80,
    },
    "Rampage ALCM": {
        "speed_km_s": 0.340, "peak_alt_m": 8_000, "sea_skim": False,
        "color": "cc00ffcc", "width": 2,
        "label": "Rampage ALCM (teal — Israeli F-15I standoff missile, 250 km)",
        "cost_usd": 500_000,  # Israeli-made; $400k–600k estimate
        "max_range_km": 250,
    },
    "SPICE-2000": {
        "speed_km_s": 0.250, "peak_alt_m": 9_000, "sea_skim": False,
        "color": "cc00ff44", "width": 2,
        "label": "SPICE-2000 (green — Israeli F-16I precision glide bomb, 100 km)",
        "cost_usd": 800_000,  # Rafael estimate; $600k–1M
        "max_range_km": 100,
    },
}

# US Carrier CAP intercept (AIM-120 AMRAAM) — cost factor, not KML-tracked
AIM120_COST_USD     = 1_800_000   # AIM-120C-8 unit cost ~$1.8M (FMS price $2.46M incl. support; Jane's DW 2024)
SLAM_ER_COST_USD    = 1_300_000   # AGM-84H/K FY2023
SLAM_ER_PER_CSG_DAY = 50          # SLAM-ER air-launched strikes per CSG per day
CAP_AMRAAM_PER_CSG_DAY = 200      # AIM-120 shots expended per CSG per day (CAP duty)
CAP_PK_VS_DRONE     = 0.65        # AIM-120 P(kill) vs Shahed-class drone
CAP_PK_VS_MISSILE   = 0.45        # AIM-120 P(kill) vs cruise/ballistic missile

IRAN_SITES = [
    {"name": "Bandar Abbas",  "lon": 56.27, "lat": 27.18, "type": "Coastal Battery"},
    {"name": "Qeshm Island",  "lon": 56.02, "lat": 26.74, "type": "Island Fortress"},
    {"name": "Jask",          "lon": 57.77, "lat": 25.64, "type": "Coastal Battery"},
    {"name": "Chahbahar",     "lon": 60.62, "lat": 25.29, "type": "Coastal Battery"},
    {"name": "Bushehr",       "lon": 50.84, "lat": 28.97, "type": "Naval Base"},
    {"name": "Khorramshahr",  "lon": 48.18, "lat": 30.44, "type": "Inland Battery"},
    {"name": "Shiraz",        "lon": 52.53, "lat": 29.59, "type": "Inland Battery"},
    {"name": "Isfahan",       "lon": 51.67, "lat": 32.66, "type": "Inland Battery"},
    {"name": "Kerman",        "lon": 57.09, "lat": 30.28, "type": "Inland Battery"},
    {"name": "Dezful",        "lon": 48.40, "lat": 32.38, "type": "Inland Battery"},
    {"name": "Minab",         "lon": 57.08, "lat": 27.09, "type": "Coastal Battery"},
    {"name": "Lar",           "lon": 54.33, "lat": 27.68, "type": "Inland Battery"},
]

# After 30 US strike hits a launch site is destroyed and stops launching
SITE_INACTIVATION_THRESHOLD = 30

# ── 25-site cave/tunnel network (caves scenario) ──────────────────────────
# Geographically distributed across Iran's mountain ranges:
# Zagros (W/SW), Alborz (N), and eastern highlands.
# Each site requires only 2 hits — but 25 targets vs. a limited strike budget
# means many survive and continue launching.
CAVE_SITES = [
    # Zagros Mountains — western & central
    {"name": "Piranshahr Cavern",    "lon": 45.13, "lat": 37.68, "type": "Cave Complex"},
    {"name": "Sardasht Tunnel",      "lon": 45.48, "lat": 36.15, "type": "Cave Complex"},
    {"name": "Ilam Cave Battery",    "lon": 46.42, "lat": 33.64, "type": "Cave Complex"},
    {"name": "Sanandaj Cave",        "lon": 47.01, "lat": 35.32, "type": "Cave Complex"},
    {"name": "Kermanshah Tunnel",    "lon": 47.07, "lat": 34.32, "type": "Cave Complex"},
    {"name": "Khorramabad Tunnel",   "lon": 48.38, "lat": 33.49, "type": "Cave Complex"},
    {"name": "Arak Mountain Base",   "lon": 49.85, "lat": 34.09, "type": "Cave Complex"},
    {"name": "Andimeshk Cave",       "lon": 48.35, "lat": 32.46, "type": "Cave Complex"},
    {"name": "Masjed Soleyman Cave", "lon": 49.30, "lat": 31.93, "type": "Cave Complex"},
    {"name": "Shahrekord Cavern",    "lon": 50.87, "lat": 32.32, "type": "Cave Complex"},
    {"name": "Yasouj Tunnel",        "lon": 51.59, "lat": 30.67, "type": "Cave Complex"},
    # Central plateau / Alborz Mountains
    {"name": "Natanz Deep Tunnel",   "lon": 51.91, "lat": 33.50, "type": "Cave Complex"},
    {"name": "Qom Mountain Base",    "lon": 50.90, "lat": 34.73, "type": "Cave Complex"},
    {"name": "Zanjan Alborz Cave",   "lon": 48.49, "lat": 36.68, "type": "Cave Complex"},
    {"name": "Qazvin Mountain Base", "lon": 50.00, "lat": 36.27, "type": "Cave Complex"},
    {"name": "Semnan Cave Complex",  "lon": 53.39, "lat": 35.57, "type": "Cave Complex"},
    {"name": "Shahroud Tunnel",      "lon": 54.98, "lat": 36.42, "type": "Cave Complex"},
    # South/Southwest approaches
    {"name": "Shiraz Mountain Base", "lon": 52.53, "lat": 29.89, "type": "Cave Complex"},
    {"name": "Fasa Cavern",          "lon": 53.65, "lat": 28.94, "type": "Cave Complex"},
    # Eastern & southeastern highlands
    {"name": "Yazd Cave Base",       "lon": 54.37, "lat": 31.89, "type": "Cave Complex"},
    {"name": "Tabas Cavern",         "lon": 56.93, "lat": 33.60, "type": "Cave Complex"},
    {"name": "Kerman Cave Complex",  "lon": 57.09, "lat": 30.28, "type": "Cave Complex"},
    {"name": "Bam Tunnel Base",      "lon": 58.37, "lat": 29.11, "type": "Cave Complex"},
    {"name": "Birjand Mountain",     "lon": 59.22, "lat": 32.87, "type": "Cave Complex"},
    {"name": "Zahedan Cave",         "lon": 60.86, "lat": 29.50, "type": "Cave Complex"},
]

# Combined site list: 12 coastal + 25 cave/tunnel = 37 total.
# Used by depleted-arsenal scenarios that retain both hardened tunnel
# infrastructure and coastal naval batteries.  IRGCN Sea Drones are
# already restricted to the 7 coastal harbours via MUNITIONS["IRGCN Sea Drone"]["sites"].
ALL_SITES = IRAN_SITES + CAVE_SITES

# Inland ballistic missile bases only — no coastal batteries, no IRGCN harbours.
# Used by preemption scenarios where US/IAF strike all coastal infrastructure
# before the Iranian salvo: only dispersed inland TELs and hardened tunnel complexes survive.
_INLAND_NAMES = {"Dezful", "Isfahan", "Shiraz", "Kerman", "Mashhad"}
INLAND_SITES  = [s for s in IRAN_SITES if s["name"] in _INLAND_NAMES]
# Inland sites + cave complexes = survivable second-strike infrastructure
INLAND_AND_CAVES = INLAND_SITES + CAVE_SITES

# 1% of Shahed-136 carry AI / computer-vision terminal guidance.
# In terminal phase they re-acquire the target visually and maneuver to a
# tighter aim point, defeating CIWS lead-angle prediction — always break through.
AI_SHAHED_FRACTION = 0.05    # fraction of Shahed-136 that are AI-guided
# Distance at which the AI drone's EO/IR camera acquires the CSG visually/thermally.
# At 100-280 m AGL over the Gulf, a carrier's thermal signature (~340 m hull) is
# visible to a modern LWIR sensor at ~35 km in clear conditions.
SHAHED_AI_LOCK_KM  = 35.0   # EO/IR acquisition range (km)
# IRGCN Sea Drone surface search radar horizon at ~1 m freeboard: ~15 km geometric,
# extended to ~20 km with mast-mounted radar and a CVN's large radar cross-section.
IRGCN_LOCK_KM      = 20.0   # surface radar acquisition range (km)

# ── Per-munition sinking weight ───────────────────────────────────────────────
# Effective multiplier for hull flooding / structural-failure potential.
# Shaped-charge ASCMs designed for waterline penetration = 2.0×;
# heavy kinetic ballistic warheads = 1.3–2.5×; topside drone fire = 0.4×.
# Calibrated against historical cases: Sheffield (1 Exocet → sank), Stark
# (2 Exocets → survived), Cole (1 VBIED → survived), Coventry (3 bombs → sank).
SINKING_WEIGHT = {
    "Shahab-3 MRBM":          1.30,  # 500 kg warhead, high-arc kinetic
    "Noor ASCM":               2.00,  # 165 kg shaped-charge, waterline penetrator
    "Fateh-110 SRBM":          1.20,  # 450 kg unitary; solid fuel; deck penetrator
    "Emad MRBM":               1.50,  # 750 kg maneuvering RV; CVN structural threat
    "Zolfaghar SRBM":          1.30,  # 450 kg GPS precision, &lt;10 m CEP
    "Khalij Fars ASBM":        1.80,  # EO/IR terminal seeker; direct carrier hits
    "CM-302 Supersonic ASCM":  2.00,  # Mach 3; 250 kg shaped-charge; below waterline
    "Fateh-313 SRBM":          1.20,  # 450 kg, similar to Fateh-110
    "Shahed-136":              0.40,  # 40 kg warhead; topside fire/electronics; rarely floods
    "Shahed-238":              0.45,  # jet variant; slightly higher kinetic energy at impact; same warhead class
    "IRGCN Sea Drone":         0.80,  # surface-level shaped charge; limited flooding risk
    "Fattah-1 HGV":            2.50,  # Mach 13–15 kinetic; catastrophic structural failure
    "Fattah-2 HGV":            2.60,  # pitch+yaw maneuvering improves aim point; slightly higher sinking risk
}

# Replacement cost of sunken hulls (separate from air wing / electronics)
_DDG_HULL_USD = 2_200_000_000   # Arleigh Burke Flight III replacement hull
_CVN_HULL_USD = 11_000_000_000  # average Nimitz/Ford hull (excl. air wing)

# ============================================================
# US STRIKE MUNITIONS (TLAM / JASSM-ER)
# ============================================================
# TLAM Block IV: ~885 km/h (0.246 km/s), range 1,600 km
#   Source: Naval Technology / Tomahawk Wikipedia
# JASSM-ER: ~1,040 km/h (0.289 km/s), range ~1,000 km, stealth profile
#   Source: AGM-158 Wikipedia / CSIS Missile Threat
# ============================================================
# COST ESTIMATES  (unclassified open-source, FY2023–2026 USD)
# ============================================================
# Iranian offensive munition unit costs (production/acquisition estimates; FY2025–2026 USD):
#   Shahed-136:      CSIS Feb 2025: $20K–$50K domestic; $35K median used here.
#                    (Iran sold to Russia at $193K–$200K; domestic cost is far lower.)
#                    The War Zone / War on the Rocks corroborate the $20K–50K range.
#   Shahed-238:      Estimated $80K–$150K (jet engine + EO/IR guidance adds cost); no public data.
#   IRGCN Sea Drone: $50K–$150K estimate; median $100K
#   Shahab-3 MRBM:   CSIS/IISS ~$500K–$1.5M; median $800K
#   Noor ASCM:       C-802 derivative; ~$300k–700k; median $500k
#   Fateh-110 SRBM:  ~$500k–1.2M; median $700k
#   Emad MRBM:       Maneuvering warhead; IISS ~$1.5M–3M; median $2M
#   Zolfaghar SRBM:  Precision; ~$700k–1.5M; median $1M
#   Khalij Fars ASBM: Anti-ship ballistic; ~$1M–3M; median $2M
#   CM-302 ASCM:     Supersonic; Chinese-derived; ~$1M–3M; median $2M
#   Fateh-313 SRBM:  Advanced precision; ~$600k–1.5M; median $800k
#
# US interceptor engagement costs (DoD FY2023 unit procurement + estimates):
#   SM-6:        $4.3M (DoD DAES FY2023)
#   SM-2:        $2.1M (DoD DAES FY2023)
#   ESSM Block 2:$1.5M (DoD FY2023)
#   RAM Block 2: $1.0M (DoD FY2023)
#   SeaRAM:      uses RAM rounds; ~$1.0M per engagement
#   Phalanx CIWS:~$50k per engagement (20mm ammunition + maintenance estimate)
#   Naval Mk-45: ~$10k per engagement (5-inch rounds; primarily surface drone deterrent)
#   Blended "SM-6/SM-2" engagement: ~$4.5M (FY2025 flyaway cost per round;
#       DoD SAR Dec 2023 lists $9.57M including R&D/support amortization;
#       Japan FMS Jan 2025: 150 missiles at $900M ≈ $6M each incl. support;
#       multi-year production contract flyaway ~$4.0–4.9M — $4.5M used here)
#   Blended "CIWS/SeaRAM" engagement: ~$800K (SeaRAM/RAM rounds dominate; ~$1M/round)
#   Blended "Naval Gun/Phalanx" engagement: ~$50k
#
# US strike munition costs:
#   TLAM Block IV: ~$2.0M (DoD FY2023 Lot 25 contract; BGM-109)
#   JASSM-ER:      ~$1.4M (FY2023 multiyear contract; AGM-158B)

INTERCEPTOR_COSTS = {
    # SM-6 Block I/IA FY2025 flyaway: ~$4.0–$4.9M per round (multi-year procurement).
    # DoD Selected Acquisition Report Dec 2023: $9.574M per unit (includes R&D + support amortization).
    # Japan FMS Jan 2025: 150 SM-6 at $900M → ~$6M each (includes sustainment/spares).
    # CBO analysis blended SM-6/SM-2/ESSM engagement: $4.5M used as FY2025 best estimate.
    "SM-6 / SM-2":         4_500_000,   # FY2025 flyaway blended engagement cost
    # SeaRAM uses RIM-116 RAM Block 2 rounds: ~$1.0M/round (DoD FY2023).
    # CIWS 20mm Vulcan engagement: ~$50K (ammo + maintenance). SeaRAM dominates the blend.
    "CIWS / SeaRAM":         800_000,   # RAM-dominated; blended SeaRAM/CIWS engagement
    # Naval 5-inch Mk-45 round: ~$10K. Phalanx 20mm: ~$50K. Used against surface drones.
    "Naval Gun / Phalanx":    50_000,   # 5-inch / 20mm rounds; effective only against surface/slow targets
}

US_STRIKE_MUNITIONS = {
    "TLAM Block IV": {
        "speed_km_s": 0.246,
        "peak_alt_m": 250,
        "color":    "cc00ff66",   # AABBGGRR: B=00 G=ff R=66 → lime green (US anti-ground)
        "color_bt": "ff00ff88",   # brighter lime green, full alpha
        "width": 2,
        "label": "TLAM Block IV (lime green — US cruise missile strike on land targets)",
        "cost_usd": 2_000_000,   # DoD FY2023 Lot 25 BGM-109 contract
    },
    "JASSM-ER": {
        "speed_km_s": 0.289,
        "peak_alt_m": 200,
        "color":    "cc00aa00",   # AABBGGRR: B=00 G=aa R=00 → forest green (stealth, darker)
        "color_bt": "ff00cc00",   # brighter forest green, full alpha
        "width": 2,
        "label": "JASSM-ER (forest green — US stealth standoff strike on land targets)",
        "cost_usd": 1_400_000,   # FY2023 multiyear AGM-158B contract
    },
}

# ============================================================
# MUNITION LIBRARY
# ============================================================
MUNITIONS = {
    # Iran warm-color scale: yellow (cheap/legacy) → orange → red (advanced/dangerous)
    # AABBGGRR: all warm tones keep B=00, vary G from ff (yellow) to 00 (red), R=ff always.
    "Shahab-3 MRBM": {
        # Legacy MRBM — amber-orange (step 4 of 10)
        "speed_km_s": 1.40, "peak_alt_m": 280_000, "sea_skim": False,
        "color":    "cc0099ff",   # RGB(ff,99,00) amber-orange, 80% alpha
        "color_bt": "ff00aaff",   # brighter amber-orange, full alpha
        "width": 2, "width_bt": 3,
        "label": "Shahab-3 MRBM (amber-orange — legacy MRBM)",
        "cost_usd": 800_000,         # CSIS/IISS estimate; $500k–1.5M range
        # Expected damage/casualties PER BREAKTHROUGH HIT (probability-weighted):
        #   70% hits escort DDG (~280 crew, 40% KIA if ballistic hit) + 30% hits CVN (~5,000 crew, 4% KIA)
        "damage_per_hit_usd":         200_000_000,   # ~$200M: 35% P(mission kill escort @$1.8B) + CVN damage
        "kia_per_hit":                60,    # ~196 DDG × 0.7 + ~200 CVN × 0.3 weighted
        "wia_per_hit":               160,    # ~3× KIA (burns, blast, shrapnel)
        "collateral_usd_per_btk":  12_000_000,   # 12% stray × $100M avg tanker/bulk carrier
        "collateral_kia_per_btk":     2.4,  # 12% stray × 20 crew per vessel
        "n_arc_override": 26,    # high-arc ballistic: many segments for smooth parabola
    },
    "Noor ASCM": {
        # Anti-ship cruise missile — vivid red (anti-ship family)
        "speed_km_s": 0.28, "peak_alt_m": 120, "sea_skim": True,
        "color":    "cc0000ff",   # AABBGGRR: B=00 G=00 R=ff → pure red
        "color_bt": "ff0011ff",   # brighter red, full alpha
        "width": 2, "width_bt": 3,
        "label": "Noor ASCM (red — legacy anti-ship cruise, C-802 derivative)",
        "cost_usd": 500_000,         # C-802 derivative; $300k–700k estimate
        "damage_per_hit_usd":        150_000_000,   # Exocet-class 165kg warhead; ~$150M expected
        "kia_per_hit":                40,
        "wia_per_hit":               120,
        "collateral_usd_per_btk":   7_000_000,    # 8% stray × $87M avg vessel
        "collateral_kia_per_btk":     1.2,  # 8% stray × 15 crew
        "n_arc_override": 18,    # sea-skimming cruise: medium resolution
    },
    "Fateh-110 SRBM": {
        # Older SRBM — amber (step 3 of 10)
        "speed_km_s": 1.00, "peak_alt_m": 60_000, "sea_skim": False,
        "color":    "cc00bbff",   # RGB(ff,bb,00) amber
        "color_bt": "ff00ccff",
        "width": 2, "width_bt": 3,
        "label": "Fateh-110 SRBM (amber — legacy SRBM)",
        "cost_usd": 700_000,         # $500k–1.2M estimate
        "damage_per_hit_usd":        180_000_000,   # 450kg warhead; higher than ASCM
        "kia_per_hit":                55,
        "wia_per_hit":               150,
        "collateral_usd_per_btk":  12_000_000,
        "collateral_kia_per_btk":     2.4,
        "n_arc_override": 24,    # ballistic arc
    },
    "Emad MRBM": {
        # Maneuvering MRBM — red (step 9 of 10, very advanced)
        "speed_km_s": 1.50, "peak_alt_m": 350_000, "sea_skim": False,
        "color":    "cc0011ff",   # RGB(ff,11,00) deep red
        "color_bt": "ff0022ff",   # bright red
        "width": 3, "width_bt": 4,
        "label": "Emad MRBM (red — maneuvering MRBM, advanced)",
        "cost_usd": 2_000_000,       # maneuvering warhead; IISS $1.5M–3M estimate
        "damage_per_hit_usd":        250_000_000,   # maneuvering terminal; very hard to defeat
        "kia_per_hit":                70,
        "wia_per_hit":               180,
        "collateral_usd_per_btk":  10_000_000,
        "collateral_kia_per_btk":     1.8,
        "n_arc_override": 28,    # highest-arc MRBM: most segments
    },
    "Zolfaghar SRBM": {
        # Precision SRBM — orange-red (step 6 of 10)
        "speed_km_s": 1.20, "peak_alt_m": 130_000, "sea_skim": False,
        "color":    "cc0066ff",   # RGB(ff,66,00) orange-red
        "color_bt": "ff0077ff",
        "width": 3, "width_bt": 4,
        "label": "Zolfaghar SRBM (orange-red — precision SRBM)",
        "cost_usd": 1_000_000,       # precision guidance; $700k–1.5M estimate
        "damage_per_hit_usd":        220_000_000,   # 600kg precision warhead
        "kia_per_hit":                65,
        "wia_per_hit":               175,
        "collateral_usd_per_btk":  10_000_000,
        "collateral_kia_per_btk":     2.0,
        "n_arc_override": 24,    # ballistic arc
    },
    "Khalij Fars ASBM": {
        # Anti-ship ballistic missile — deep crimson (anti-ship family)
        "speed_km_s": 1.30, "peak_alt_m": 90_000, "sea_skim": False,
        "color":    "cc0022ff",   # AABBGGRR: B=00 G=22 R=ff → deep crimson red
        "color_bt": "ff0033ff",   # brighter crimson, full alpha
        "width": 3, "width_bt": 4,
        "label": "Khalij Fars ASBM (crimson — anti-ship ballistic, EO/IR seeker)",
        "cost_usd": 2_000_000,       # anti-ship ballistic; $1M–3M estimate
        # Designed specifically to kill carriers; 70% DDG screen hit + 30% CVN penetration
        "damage_per_hit_usd":        350_000_000,   # ~$350M: high P(mission kill) on carrier or escort
        "kia_per_hit":               120,    # terminal dive + shaped charge optimized vs ship armor
        "wia_per_hit":               300,
        "collateral_usd_per_btk":  12_000_000,
        "collateral_kia_per_btk":     2.4,
        "n_arc_override": 26,    # anti-ship ballistic: steep terminal dive needs resolution
    },
    "CM-302 Supersonic ASCM": {
        # Fastest sea-skimming supersonic ASCM — dark maroon-red (anti-ship family, most dangerous)
        "speed_km_s": 1.00, "peak_alt_m": 80, "sea_skim": True,
        "color":    "cc0044ff",   # AABBGGRR: B=00 G=44 R=ff → dark scarlet (distinct from Noor/KF)
        "color_bt": "ff0055ff",   # brighter scarlet, full alpha
        "width": 4, "width_bt": 5,
        "label": "CM-302 Supersonic ASCM (scarlet — Mach 3 anti-ship, most dangerous)",
        "cost_usd": 2_000_000,       # Chinese-derived supersonic; $1M–3M estimate
        # Mach 3 impact velocity; warhead ~250kg but kinetic energy adds lethality
        "damage_per_hit_usd":        220_000_000,
        "kia_per_hit":                80,
        "wia_per_hit":               200,
        "collateral_usd_per_btk":   7_000_000,    # 7% stray × $100M
        "collateral_kia_per_btk":     1.05,
        "n_arc_override": 20,    # fast sea-skimmer: high resolution for evasive path
    },
    "Fateh-313 SRBM": {
        # Advanced precision SRBM — red-orange (step 7 of 10)
        "speed_km_s": 1.10, "peak_alt_m": 75_000, "sea_skim": False,
        "color":    "cc0055ff",   # RGB(ff,55,00) red-orange
        "color_bt": "ff0066ff",
        "width": 4, "width_bt": 5,
        "label": "Fateh-313 SRBM (red-orange — advanced precision SRBM)",
        "cost_usd": 800_000,         # advanced precision; $600k–1.5M estimate
        "damage_per_hit_usd":        200_000_000,
        "kia_per_hit":                62,
        "wia_per_hit":               165,
        "collateral_usd_per_btk":  10_000_000,
        "collateral_kia_per_btk":     2.0,
        "n_arc_override": 24,    # ballistic arc
    },
    "Shahed-136": {
        # Delta-wing loitering munition; piston engine (~50 hp); ~185 km/h cruise.
        # Swarm tactic: dozens launched simultaneously from trailers / box launchers.
        # Post-strike (50% preemption assumed): Iran retains ~10,000–20,000 Shahed-136
        # and Shahed-131, capped at 5,000 per scenario for plausibility.
        # Sources: CSIS Feb 2025 ($35K median); War Zone; Defence Express.
        "speed_km_s": 0.052,         # ~187 km/h cruise speed
        "peak_alt_m": 50,            # low-altitude flight profile; terrain-hugging
        "sea_skim":   True,          # flies below most radar horizons over water
        "color":    "cc00ffff",      # AABBGGRR: B=00 G=ff R=ff → pure yellow (drone family)
        "color_bt": "ff00ffff",      # full-alpha pure yellow on breakthrough
        "width": 1, "width_bt": 2,
        "label": "Shahed-136 Loitering Munition (yellow — cheap swarm drone)",
        "cost_usd": 35_000,          # CSIS Feb 2025 median: $20K–$50K domestic; $35K used
                                     # (Iran export to Russia was $193K–$200K/unit — domestic much cheaper)
        # Warhead: ~36–40 kg shaped charge; damage is primarily topside: sensors,
        # radar arrays, CIWS housings, antennas, deck-mounted systems. Rarely floods.
        "damage_per_hit_usd":         15_000_000,   # ~$15M: electronics/radar damage
        "kia_per_hit":                 5,
        "wia_per_hit":                20,
        "collateral_usd_per_btk":   4_000_000,    # 5% stray × $80M avg commercial vessel
        "collateral_kia_per_btk":     0.75,  # 5% stray × 15 crew
        "n_arc_override": 10,        # slow drone: temporal granularity more useful than geometric
        "interceptor_style": "us_ciws",   # CIWS primary; SeaRAM secondary at final approach
        "t_int_range":  (0.92, 0.99),     # intercepted very late in flight (CIWS is last-resort)
        "react_range":  (5, 15),          # 5–15 s CIWS reaction time
        "sites": ["Bandar Abbas", "Qeshm Island", "Jask", "Chahbahar",
                  "Bushehr", "Minab", "Lar"],
    },
    "Shahed-238": {
        # Jet-powered variant of the Shahed-136; "Geran-3" in Russian service.
        # Toloue-10 or Toloue-13 micro-turbojet; cruises at ~500 km/h vs 187 km/h baseline.
        # Three guidance variants exist: GPS/GLONASS, EO/IR terminal, and radar-homing.
        # First confirmed combat use by Russia: January 2024.
        # Higher speed cuts US reaction time from ~4 min to ~1 min at 50 km range.
        # Sources: Shahed-238 Wikipedia; United24 Media; ISIS Reports 2025.
        "speed_km_s": 0.139,         # ~500 km/h cruise (Toloue-10 micro-turbojet)
        "peak_alt_m": 50,            # low-altitude flight profile; terrain-hugging
        "sea_skim":   True,
        "color":    "cc00eeff",      # AABBGGRR: slightly deeper yellow-orange (distinct from Shahed-136)
        "color_bt": "ff00eeff",
        "width": 1, "width_bt": 2,
        "label": "Shahed-238 Jet Drone (orange-yellow — jet-powered fast drone variant)",
        "cost_usd": 100_000,         # estimated $80K–$150K (higher complexity; turbojet); no public data
        # Same warhead as Shahed-136 (~40 kg); damage similar but higher approach speed
        # makes CIWS engagement window ~3× shorter → marginally higher hit probability.
        "damage_per_hit_usd":         18_000_000,   # slightly higher than 136 due to kinetic energy
        "kia_per_hit":                 6,
        "wia_per_hit":                22,
        "collateral_usd_per_btk":   4_500_000,
        "collateral_kia_per_btk":     0.80,
        "n_arc_override": 12,        # faster than 136; more segments needed for smooth arc
        "interceptor_style": "us_ciws",
        "t_int_range":  (0.88, 0.97),   # intercepted slightly earlier than baseline (faster approach)
        "react_range":  (3, 10),         # shorter reaction window (~1–2 min at 50 km vs 4 min for 136)
        "sites": ["Bandar Abbas", "Qeshm Island", "Jask", "Chahbahar",
                  "Bushehr", "Minab", "Lar"],
    },
    "IRGCN Sea Drone": {
        # Slow surface drone — amber yellow (drone family, distinct from Shahed)
        # Realistic IRGCN fast-boat/drone operational radius: ≤350 km from launch site.
        # Sites beyond this range are excluded from the target pool to avoid
        # absurd multi-hour transits (e.g. Bushehr → CSG Alpha = 1,345 km = 17 hrs).
        "max_range_km":    350,
        "lock_on_range_km": 20,    # surface radar acquires CSG at ~20 km
        "speed_km_s": 0.022,
        "peak_alt_m": 1.0,
        "sea_skim":   True,
        "color":    "cc00ccff",   # AABBGGRR: B=00 G=cc R=ff → amber-yellow (darker than Shahed)
        "color_bt": "ff00ddff",   # brighter amber, full alpha
        "width": 2, "width_bt": 3,
        "label": "IRGCN Sea Drone (amber-yellow — surface drone)",
        "cost_usd": 100_000,         # $50k–150k estimate based on IRGCN procurement patterns
        # Surface drone; small charge; primarily sensor/deck damage if hull not penetrated
        "damage_per_hit_usd":          5_000_000,   # ~$5M: sensor/topside damage; low lethality
        "kia_per_hit":                 3,
        "wia_per_hit":                10,
        "collateral_usd_per_btk":   8_000_000,    # 10% stray (waves push off course) × $80M
        "collateral_kia_per_btk":     1.0,   # 10% × 10 avg crew on commercial vessel
        "n_arc_override": 8,     # slowest weapon: 8 segments sufficient
        "interceptor_style": "us_naval_gun",
        "t_int_range":  (0.80, 0.98),
        "react_range":  (15, 45),
        "sites": ["Bandar Abbas", "Qeshm Island", "Jask", "Chahbahar",
                  "Bushehr", "Minab", "Lar"],
    },
    "Fattah-1 HGV": {
        # Hypersonic Glide Vehicle — magenta/purple (beyond the red scale; next-generation threat)
        # Fattah-1: Mach 13–15 terminal, skip-glide trajectory, range ~1,400 km.
        # Announced June 2023; used in combat in October 2024 attack on Israel.
        # Skip-glide profile: boost to ~80 km, glide and maneuver in pitch only (no yaw).
        # SM-6 Block IA P(k): ~2–5% (radar loses track during skip-glide phase transitions;
        # intercept geometry extremely challenging at Mach 13+ terminal).
        # Sources: Fattah-1 Wikipedia; CSIS Missile Threat; Jane's DW 2024; JINSA 2025.
        "speed_km_s": 4.0,          # average across boost + glide phases (~Mach 12 average)
        "peak_alt_m": 80_000,       # skip-glide ceiling ~80 km (lower than MRBM max)
        "sea_skim":   False,
        "color":    "ccff00ff",     # AABBGGRR: magenta (B=ff, G=00, R=ff) — beyond the red/orange scale
        "color_bt": "ffff22ff",     # brighter magenta on breakthrough
        "width": 4, "width_bt": 5,
        "label": "Fattah-1 HGV (magenta — hypersonic glide vehicle, near-uninterceptable)",
        "cost_usd": 3_000_000,      # open-source estimate: $2M–$5M range (no public contract data)
        "damage_per_hit_usd":       400_000_000,   # ~580 kg warhead + enormous kinetic energy;
                                                    # likely mission-kills any escort DDG; heavy CVN structural damage
        "kia_per_hit":              100,
        "wia_per_hit":              250,
        "collateral_usd_per_btk": 15_000_000,
        "collateral_kia_per_btk":   3.0,
        "n_arc_override": 28,
        "intercept_prob_override":  0.05,   # ~5% P(k); SM-6 Block IA vs maneuvering HGV
        "t_int_range":  (0.90, 0.97),
        "react_range":  (20, 40),
    },
    "Fattah-2 HGV": {
        # Advanced maneuvering HGV — crimson (distinct from Fattah-1 magenta)
        # Unveiled November 2023; claimed Mach 15, range ~1,500 km.
        # Key upgrade over Fattah-1: maneuvers in BOTH pitch AND yaw — dramatically
        # increases intercept difficulty as SM-6 cannot predict terminal impact point.
        # First reported combat use: March 2026 (Iran International, March 2026).
        # Western analysts accept it as a real threat but are skeptical of Mach 15 claim;
        # Mach 10–12 assessed as more plausible based on propulsion analysis.
        # Sources: Fattah-2 Wikipedia; Hudson Institute 2026; JINSA Feb 2026.
        "speed_km_s": 3.5,          # average Mach ~10 assessed; Iran claims Mach 15
        "peak_alt_m": 75_000,       # lower glide ceiling due to more aggressive maneuvering
        "sea_skim":   False,
        "color":    "ccaa00ff",     # AABBGGRR: crimson (B=aa, G=00, R=ff) — between red and magenta
        "color_bt": "ffcc00ff",
        "width": 4, "width_bt": 5,
        "label": "Fattah-2 HGV (crimson — advanced maneuvering HGV, pitch+yaw, near-zero intercept Pk)",
        "cost_usd": 4_000_000,      # higher than Fattah-1 due to guidance complexity; $3M–$8M estimate
        "damage_per_hit_usd":       420_000_000,   # similar to Fattah-1; maneuvering improves aim point
        "kia_per_hit":              110,
        "wia_per_hit":              260,
        "collateral_usd_per_btk": 15_000_000,
        "collateral_kia_per_btk":   3.0,
        "n_arc_override": 28,
        "intercept_prob_override":  0.03,   # ~3% P(k); pitch+yaw maneuvering makes intercept harder than Fattah-1
        "t_int_range":  (0.91, 0.98),
        "react_range":  (15, 35),
    },
}

# ============================================================
# SINGLE-SHOT PROBABILITY OF KILL (SSPK) — Open-source estimates
# ============================================================
# Sources: Wilkening (Science & Global Security 2000); CSBA Salvo Competition (2015);
# RAND Multilayer BMD; DOT&E FY2018/2022; JINSA Shielded by Fire (Aug 2025);
# FPRI Shallow Ramparts (Oct 2025); Red Sea/Houthi campaign data (2023-2025);
# MDA design goals (0.80-0.90 per shot); Vice Adm. McLane (2024): ~50% vs complex targets.
MUNITION_SSPK = {
    "Shahab-3 MRBM":         {"interceptor": "SM-6 SBT",        "sspk": 0.65, "notes": "Non-maneuvering, large RCS; SM-6 SBT favored over SM-2 at Mach 3-4 terminal"},
    "Noor ASCM":             {"interceptor": "ESSM / RAM Blk2",  "sspk": 0.80, "notes": "Sea-skimmer compresses radar acq; ESSM 0.75-0.85, RAM 0.85-0.95, CIWS 0.40-0.65"},
    "Fateh-110 SRBM":        {"interceptor": "SM-6 SBT",        "sspk": 0.65, "notes": "Short warning window; predictable trajectory; SM-6 SBT primary"},
    "Emad MRBM":             {"interceptor": "SM-6 SBT",        "sspk": 0.45, "notes": "MaRV terminal maneuvering degrades Pk ~0.10-0.20; documented PAC-3 MSE defeat"},
    "Zolfaghar SRBM":        {"interceptor": "SM-6 SBT",        "sspk": 0.50, "notes": "Mach 5+ compresses window; terminal maneuvering; PAC-3 defeat documented (JINSA 2025)"},
    "Khalij Fars ASBM":      {"interceptor": "SM-6 SBT",        "sspk": 0.60, "notes": "EO/IR seeker; shorter range than DF-21D; 100% SM-6 intercept rate vs Houthi ASBMs (small n)"},
    "CM-302 Supersonic ASCM":{"interceptor": "SM-6",            "sspk": 0.55, "notes": "Mach 2-3 sea-skimmer; only SM-6 viable (SM-2 speed-limited); compressed 3-5s terminal window"},
    "Fateh-313 SRBM":        {"interceptor": "SM-6 SBT",        "sspk": 0.60, "notes": "Advanced precision SRBM; solid fuel; moderate terminal maneuvering"},
    "Shahed-136":            {"interceptor": "RAM Blk2 / CIWS", "sspk": 0.83, "notes": "RAM Blk2 95% trials; CIWS 0.55-0.75; cost-exchange ~$800K/drone intercept vs $35K drone; Mk45 gun used when cost-exchange favors it"},
    "Shahed-238":            {"interceptor": "RAM Blk2 / CIWS", "sspk": 0.76, "notes": "Jet speed (~500 km/h) gives CIWS only ~1-2 min terminal window vs ~4 min for Shahed-136; RAM still primary"},
    "IRGCN Sea Drone":       {"interceptor": "CIWS / Mk38",     "sspk": 0.80, "notes": "Surface engagement mode; thin unarmored hull; Mk38 25mm primary; swarm saturation main risk"},
    "Fattah-1 HGV":          {"interceptor": "SM-6 (terminal)", "sspk": 0.05, "notes": "Mach 13-15 skip-glide; pitch-only maneuvering; ~2-5% Pk per SM-6 Block IA (radar track loss during glide phase)"},
    "Fattah-2 HGV":          {"interceptor": "SM-6 (terminal)", "sspk": 0.03, "notes": "Mach 10-15 (claimed 15, assessed 10-12); pitch+yaw maneuvering; SM-6 cannot solve impact-point prediction; ~3% Pk est. (Hudson Institute 2026)"},
}

# ============================================================
# CIRCULAR ERROR PROBABLE PER MUNITION (metres)
# ============================================================
# CEP = radius within which 50% of impacts land.
# Used to determine whether a breakthrough missile lands within 20 m of a ship.
# Sources: CSIS Missile Threat; Jane's DW 2024; open-source performance estimates.
MUNITION_CEP_M = {
    "Shahab-3 MRBM":          500,   # legacy guidance; unguided RV; wide dispersion
    "Noor ASCM":               10,   # active radar homing terminal; C-802 derivative
    "Fateh-110 SRBM":          50,   # GPS-guided; solid-fuel SRBM
    "Emad MRBM":               30,   # MaRV terminal maneuver; GPS+INS
    "Zolfaghar SRBM":          10,   # precision GPS/INS; PAC-3 defeat documented
    "Khalij Fars ASBM":         5,   # EO/IR seeker; purpose-built ship-hunter
    "CM-302 Supersonic ASCM":   5,   # active radar terminal; Mach 3 approach
    "Fateh-313 SRBM":          30,   # advanced precision SRBM; GPS/INS
    "Shahed-136":              30,   # GPS terminal; loitering munition
    "Shahed-238":              20,   # EO/IR terminal; jet-powered variant
    "IRGCN Sea Drone":          3,   # surface radar lock; essentially a ram
    "Fattah-1 HGV":           100,   # limited guidance at Mach 13; pitch-only
    "Fattah-2 HGV":            75,   # slightly better; pitch+yaw but still HGV
}

# ─── Per-weapon-tier single-shot Pk  ──────────────────────────────────────────
# Calibrated so that the optimal tier reproduces MUNITION_SSPK values; fallback
# tiers are progressively degraded.  Weapons not listed default to 0.0 (no Pk).
ENGAGEMENT_PK = {
    # SM-6 Block IA — ≤240 km; best vs. ballistic mid-course
    "SM-6": {
        "Shahab-3 MRBM":          0.65,
        "Fateh-110 SRBM":         0.65, "Fateh-313 SRBM":         0.60,
        "Emad MRBM":              0.45, "Zolfaghar SRBM":          0.50,
        "Khalij Fars ASBM":       0.60, "CM-302 Supersonic ASCM":  0.55,
        "Noor ASCM":              0.70, "Shahed-136":              0.25,
        "Shahed-238":             0.25, "IRGCN Sea Drone":         0.10,
        "Fattah-1 HGV":           0.05, "Fattah-2 HGV":            0.03,
    },
    # SM-2 Block IIIB — ≤167 km; good vs. cruise; weaker vs. ballistic
    "SM-2": {
        "Shahab-3 MRBM":          0.50, "Fateh-110 SRBM":          0.50,
        "Fateh-313 SRBM":         0.45, "Emad MRBM":               0.30,
        "Zolfaghar SRBM":         0.38, "Khalij Fars ASBM":        0.45,
        "CM-302 Supersonic ASCM": 0.42, "Noor ASCM":               0.65,
        "Shahed-136":             0.22, "Shahed-238":              0.22,
        "IRGCN Sea Drone":        0.05, "Fattah-1 HGV":            0.02,
        "Fattah-2 HGV":           0.01,
    },
    # ESSM Block 2 — ≤50 km; primary vs. sea-skimmers
    "ESSM": {
        "Shahab-3 MRBM":          0.18, "Fateh-110 SRBM":          0.22,
        "Fateh-313 SRBM":         0.22, "Emad MRBM":               0.12,
        "Zolfaghar SRBM":         0.15, "Khalij Fars ASBM":        0.28,
        "CM-302 Supersonic ASCM": 0.45, "Noor ASCM":               0.80,
        "Shahed-136":             0.65, "Shahed-238":              0.58,
        "IRGCN Sea Drone":        0.18, "Fattah-1 HGV":            0.01,
        "Fattah-2 HGV":           0.01,
    },
    # RAM Block 2 — ≤15 km; optimised for drones + close-in sea-skimmers
    "RAM": {
        "Shahab-3 MRBM":          0.04, "Fateh-110 SRBM":          0.06,
        "Fateh-313 SRBM":         0.06, "Emad MRBM":               0.03,
        "Zolfaghar SRBM":         0.04, "Khalij Fars ASBM":        0.12,
        "CM-302 Supersonic ASCM": 0.32, "Noor ASCM":               0.85,
        "Shahed-136":             0.90, "Shahed-238":              0.82,
        "IRGCN Sea Drone":        0.28, "Fattah-1 HGV":            0.01,
        "Fattah-2 HGV":           0.01,
    },
    # CIWS (Phalanx) — ≤2 km; last-resort point defence
    "CIWS": {
        "Shahab-3 MRBM":          0.08, "Fateh-110 SRBM":          0.12,
        "Fateh-313 SRBM":         0.12, "Emad MRBM":               0.06,
        "Zolfaghar SRBM":         0.08, "Khalij Fars ASBM":        0.18,
        "CM-302 Supersonic ASCM": 0.22, "Noor ASCM":               0.48,
        "Shahed-136":             0.65, "Shahed-238":              0.52,
        "IRGCN Sea Drone":        0.60, "Fattah-1 HGV":            0.01,
        "Fattah-2 HGV":           0.01,
    },
    # Naval Gun (Mk38 / Mk45) — ≤5 km surface engagement
    "NAVAL_GUN": {
        "IRGCN Sea Drone":        0.80, "Shahed-136":              0.28,
        "Shahed-238":             0.20, "Noor ASCM":               0.10,
        "CM-302 Supersonic ASCM": 0.05,
    },
}

# ── Shots-per-engagement doctrine  ────────────────────────────────────────────
# Ballistic missiles and supersonic ASCMs warrant 2-round engagements per
# US Navy Shoot-Look-Shoot (SLS) doctrine (OPNAVINST 3500.39; CSBA 2015).
# Expected rounds consumed: 2 regardless of outcome (simultaneous salvo mode).
# Cruise missiles, drones, and sea drones: 1 round (adequate time to assess).
_SHOTS_PER_ENGAGEMENT = {
    "Shahab-3 MRBM":          2,
    "Fateh-110 SRBM":         2,
    "Emad MRBM":              2,
    "Zolfaghar SRBM":         2,
    "Khalij Fars ASBM":       2,
    "CM-302 Supersonic ASCM": 2,
    "Fateh-313 SRBM":         2,
    "Fattah-1 HGV":           2,
    "Fattah-2 HGV":           2,
}

# ── Per-role casualty and damage scale factors ────────────────────────────────
# A hit on a CVN produces more casualties (larger crew density in targeted areas)
# and structural damage than a hit on a DDG.  These multipliers adjust the
# munition's baseline kia_per_hit / damage_per_hit which are calibrated to a DDG.
# Sources: NWP 3-20.6 damage assessment guidance; Sinking of HMS Sheffield /
# USS Stark/Cole historical analysis; NSWC Dahlgren ship survivability models.
_SHIP_ROLE_KIA_SCALE = {
    "CVN":  2.5,   # 5,000+ crew; damage control teams large but more people at risk
    "CG":   0.9,   # ~400 crew; slightly fewer than DDG
    "DDG":  1.0,   # baseline ~280 crew
    "AOE":  0.6,   # ~600 crew but non-combat role; lower blast exposure
}
_SHIP_ROLE_DAMAGE_SCALE = {
    "CVN":  3.5,   # $11B hull; electronics-dense; any hit = massive repair cost
    "CG":   1.1,   # $1.8B hull; slightly more capable than DDG
    "DDG":  1.0,   # baseline $2.2B hull
    "AOE":  0.4,   # logistics ship; lower combat asset value per hit
}

# ============================================================
# SCENARIOS  (scaled to 8 CSGs, post-50%-pre-strike degradation)
# ============================================================
# All scenario n_missiles values reflect a 50% reduction from pre-strike
# inventory, modelling a US/IAF suppression campaign before the main attack.
#
# ── Iran Pre-Strike Inventory Estimates (March 2026 context) ────────────────
#
# Shahed-136 / loitering munitions (all variants incl. Shahed-131/149):
#   Pre-strike Low:  ~40,000  (RUSI Nov 2023: 1,700–2,400 original + 400/day
#                    production × 2 yr; minus ~2,200 exported to Russia)
#   Pre-strike High: ~80,000  (Israeli intelligence estimate; Iran's own Jan 2026
#                    claim; IDF: ~400/day production; source: DefenceSecurityAsia
#                    Feb 2026; CNBC Mar 2026)
#   Post-50% strike: 20,000–40,000 drones available
#
# Ballistic missiles (all types, post-June-2025-conflict reconstitution):
#   Pre-strike Low:  ~1,500  (Alma Research Feb 2026; 19FortyFive Feb 2026:
#                    "1,500 missiles ready"; post-Apr+Oct 2024 exchange losses
#                    ~380 fired, then partially replenished)
#   Pre-strike High: ~2,500  (IDF intelligence estimate Feb 2026; CENTCOM
#                    Gen. McKenzie 2022: "3,000+" pre-war; FDD Feb 2026)
#     By type (IISS Military Balance 2024 / CSIS Missile Threat 2024):
#       Shahab-3 MRBM:    25–50   (NASIC 2017; most converted to Ghadr-1 variants)
#       Emad MRBM:        50–100  (operational since 2015; limited production)
#       Fateh-110 SRBM:   500–800 (solid-fuelled; core tactical system since 2004)
#       Fateh-313 SRBM:   200–400 (500 km range; operational since 2015)
#       Zolfaghar SRBM:   100–200 (700 km; first used operationally 2017)
#       Khalij Fars ASBM: 50–100  (300 km quasi-ballistic; operational 2014)
#       Fattah-1 HGV:     20–50   (very limited; complex production; used Oct 2024)
#   Post-50% strike: 750–1,250 ballistic missiles available
#
# Anti-Ship Cruise Missiles:
#   Noor (C-802 derivative): Pre-strike 200–400 (IISS 2024; 60 on Qeshm 1997 +
#                    coastal batteries; source: Jane's DW 2024)
#   CM-302 supersonic: Pre-strike 0–30 (STILL UNDER NEGOTIATION with China as of
#                    Mar 2026; not yet operationally deployed; source: JINSA Mar 2026)
#   Post-50% strike: Noor 100–200; CM-302 0–15
#
# IRGCN Surface Drones:
#   Pre-strike: ~500–800 (after IRIS Shahid Bagheri drone carrier destroyed in
#               Operation Epic Fury 2025–2026; ONI/USNI News 2024 "several hundred")
#   Post-50% strike: 250–400 available
#
SCENARIOS = {
    "low": {
        "label": "Scenario A -- Low Capability (8 CSGs)",
        "description": (
            "SITUATION: Iran executes a limited retaliatory probe using exclusively legacy munitions "
            "from its pre-2020 inventory. After absorbing approximately 50% inventory losses to "
            "US pre-emptive strikes, the IRGC deploys only the most widely dispersed assets "
            "remaining. This scenario establishes the floor of Iranian offensive capability and "
            "tests whether legacy systems can penetrate a fully-alerted 8-CSG Aegis screen.\n\n"
            "PHASE 1 — DRONE SWARM (T+0 to T+60 min): 665 Shahed-136 loitering munitions depart "
            "from dispersed coastal cells across a 600 km frontage between Bushehr and Chahbahar. "
            "Each drone navigates autonomously via GPS-waypoint routing at ~185 km/h and 100–150 m "
            "AGL, using terrain masking along the Zagros foothills before descending over the Gulf. "
            "The aggregate track density across 665 slow-movers overwhelms automated CIWS "
            "engagement queuing; CIWS engages at max rate but cannot clear every track before "
            "saturation. 135 IRGCN surface drones sprint from Qeshm Island and Bandar Abbas "
            "harbor, using the island's radar shadow to approach inner-screen DDGs unseen.\n\n"
            "PHASE 2 — BALLISTIC AND CRUISE SALVO (concurrent): 106 Shahab-3 MRBMs lift from "
            "hardened tunnels at Isfahan and Dezful on steep lofted trajectories peaking at "
            "~280 km altitude. Re-entry at Mach 6–7 compresses SM-6 engagement windows to "
            "40–90 seconds per missile. Terminal CEP is poor (~500 m) but 500 kg warheads make "
            "near-misses devastating against unarmored escort hulls. 80 Noor anti-ship cruise "
            "missiles (C-802 derivative, 165 kg shaped-charge warhead) depart at sea-skimming "
            "altitude (5–10 m AGL), approaching end-on to defeat over-the-horizon radar "
            "acquisition until inside Phalanx range. 79 Fateh-110 SRBMs complete the salvo.\n\n"
            "US RESPONSE: 160 TLAM/JASSM rounds targeting coastal batteries — Bandar Abbas, "
            "Qeshm Island, Jask, Minab — are launched in the first 40 minutes. Primary Shahed "
            "launch cells and ASCM coastal batteries are prioritized; several sites go silent "
            "before exhausting their full quotas.\n\n"
            "ASSESSMENT: Legacy munitions allow Aegis to achieve the highest intercept rate of "
            "any Iran-offensive scenario (~69% SSPK). Shahab-3's predictable terminal phase "
            "gives SM-6 high-confidence fire solutions. Nevertheless, 335 breakthrough munitions "
            "cause concentrated damage across multiple escort destroyers. The low total count "
            "(1,065) is the binding constraint — post-strike inventory limits Iran to a single "
            "moderate-sized salvo with no follow-on capacity.\n\n"
            "265 missiles + 665 air drones + 135 sea drones = 1,065 total | "
            "~730 intercepted | ~335 breakthrough."
        ),
        "n_missiles":    4800,          # ~3,000 Shaheds (post-50% strike; 6,000 pre-strike)
        "intercept_cap": 4000,
        "intercept_rate": 0.688,
        "wave_s":         14400,
        "n_arc":           14,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 20,   # 20 × 8 CSGs = 160 total strikes
        "munitions": [
            {"name": "Shahed-136",      "weight": 0.625},   # 665/1065
            {"name": "IRGCN Sea Drone", "weight": 0.127},   # 135/1065
            {"name": "Shahab-3 MRBM",  "weight": 0.099},   # 106/1065
            {"name": "Noor ASCM",       "weight": 0.075},   # 80/1065
            {"name": "Fateh-110 SRBM",  "weight": 0.074},   # 79/1065
        ],
    },
    "medium": {
        "label": "Scenario B -- Medium Capability (8 CSGs)",
        "description": (
            "SITUATION: Iran deploys its second-generation precision missile arsenal alongside "
            "a full-scale drone swarm. This scenario reflects Iran's assessed post-strike "
            "'realistic high' available inventory: modern maneuvering ballistic missiles paired "
            "with mass drone saturation to degrade layered defenses before precision rounds "
            "arrive. All 8 CSGs are engaged simultaneously.\n\n"
            "DRONE LAYER: 1,335 Shahed-136 and 200 IRGCN surface drones launch in a rolling "
            "swarm across the breadth of the Gulf, flooding all 8 CSG CIWS nodes concurrently. "
            "RAM and SeaRAM fire continuously during the first 30 minutes, drawing down close-in "
            "magazines before the ballistic threat arrives. ESSM handles mid-altitude cruise "
            "threats but its 50 km engagement zone is quickly exhausted by sheer track density.\n\n"
            "PRECISION MISSILE LAYER: 200 Emad MRBMs (Shahab-3 derivative with maneuvering "
            "re-entry vehicle; range 1,700 km, 750 kg warhead) execute 3–4g terminal evasive "
            "maneuvers, degrading SM-6 SSPK from ~90% to ~72% through expanded search windows. "
            "264 Zolfaghar SRBMs (700 km range, GPS+inertial, ~10 m CEP) arrive in salvos of "
            "4–6 per CSG, saturating the Aegis fire control queue. 201 Khalij Fars anti-ship "
            "ballistic missiles (300 km range, EO/IR terminal seeker) track the CVNs directly. "
            "Their Mach 10+ terminal velocity provides only 25–35 seconds of SM-6 intercept "
            "opportunity per missile in this engagement geometry — the primary kill mechanism "
            "against carrier-sized targets.\n\n"
            "US RESPONSE: 240 TLAM/JASSM rounds suppress coastal sites. Inland batteries at "
            "Isfahan, Kerman, and Shiraz remain active throughout; IAF packages engage them "
            "from T+120 min onward.\n\n"
            "ASSESSMENT: The drone/ballistic combination produces the first large-scale CSG "
            "damage events. With 793 breakthrough rounds distributed across 8 hulls, the "
            "statistical probability of mission-killing at least 2–3 escort DDGs exceeds 80%. "
            "The Khalij Fars ASBM is the primary carrier threat, each requiring a 2-round "
            "SM-6 salvo for confident kill — rapidly exhausting magazines.\n\n"
            "665 missiles + 1,335 air drones + 200 sea drones = 2,200 total | "
            "~1,407 intercepted | ~793 breakthrough."
        ),
        "n_missiles":    8250,          # ~5,000 Shaheds (post-50% strike; 5K cap per scenario)
        "intercept_cap": 4000,
        "intercept_rate": 0.645,
        "wave_s":         21600,
        "n_arc":           12,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 30,   # 30 × 8 = 240 total
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.607},   # 1335/2200
            {"name": "IRGCN Sea Drone",  "weight": 0.091},   # 200/2200
            {"name": "Emad MRBM",        "weight": 0.091},   # 200/2200
            {"name": "Zolfaghar SRBM",   "weight": 0.120},   # 264/2200
            {"name": "Khalij Fars ASBM", "weight": 0.091},   # 201/2200
        ],
    },
    "realistic": {
        "label": "Scenario D -- Realistic: Simultaneous Detection-Launch (8 CSGs)",
        "description": (
            "SITUATION: Iran's integrated air-defense network detects inbound Israeli Air Force "
            "strike packages — F-35I Adirs, F-15I Ra'ams, and F-16I Sufas — crossing into "
            "Iranian radar coverage over the Negev and Jordan Valley. The IRGC Air Defense "
            "commander, under standing doctrine (Karari Command Center, openly described in IRGC "
            "press releases through 2024), immediately authorises a full offensive salvo: every "
            "available TEL, coastal battery, and drone cell is ordered to fire within minutes.\n\n"
            "SIMULTANEOUS LAUNCH (T=0, compressed 0–30 min window): Iran commits its full "
            "post-preemption inventory in a single compressed salvo lasting approximately "
            "30 minutes — far shorter than the 60-minute drone-first doctrine of other scenarios. "
            "Drones and ballistic/cruise missiles launch concurrently, not in sequential echelons. "
            "The rationale is operationally sound: Iran correctly anticipates that each minute of "
            "delay after detection allows further IAF packages to close, and that simultaneous "
            "multi-type saturation degrades Aegis fire-control more than sequential echelons.\n\n"
            "TACTICAL IMPLICATION — NO PRE-LAUNCH SUPPRESSION: The TLAM/JASSM strike packages "
            "launched from US CSGs take 45–90 minutes to reach Iranian sites. IAF aircraft, "
            "detected the moment they triggered Iran's launch, will not reach their targets "
            "for another 10–20 minutes. Every Iranian launch site is ACTIVE for the full "
            "compressed salvo window. The pre-emptive suppression that degrades other scenarios "
            "provides zero benefit here — Iran fires its full inventory before a single US or "
            "IAF munition lands.\n\n"
            "COMPRESSED SATURATION EFFECT: With ~5,000 Shahed-136 drones, ~1,000 IRGCN surface "
            "drones, and all ballistic/cruise missiles in the air within 30 minutes, Aegis radar "
            "and SM-6 fire-control channels face maximum simultaneous track density earlier in the "
            "engagement. CIWS magazines are consumed faster. The intercept rate degrades to ~58% "
            "vs ~63% in the phased scenario — a modest difference but compounded over thousands "
            "of rounds.\n\n"
            "US/IAF STRIKES: 240 TLAM/JASSM rounds and three IAF packages engage all 12 sites "
            "but arrive only after Iran's complete inventory is airborne. Sites are destroyed "
            "systematically — they simply have no missiles left to launch. The counterstrikes "
            "serve to prevent any follow-on salvo, not to suppress this one.\n\n"
            "This scenario represents the intelligence community's most credible assessment "
            "of Iranian launch behavior given post-2024 conflict doctrine disclosures and "
            "the observed Iranian salvo in April 2024 (170 drones + 30 cruise missiles + "
            "110 ballistic missiles fired simultaneously at Israel)."
        ),
        "n_missiles":    7250,           # 5,000 Shaheds + proportional missiles (5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.580,         # lower: compressed launch reduces Aegis reaction time
        "wave_s":         43200,         # used for US strike launch window; not Iranian launches (12h scenario)
        "n_arc":           10,
        "n_sm6":           16,
        "n_us_strikes_per_csg": 30,
        "iran_detection_launch": True,   # Iran fires on IAF detection — no phase separation
        "iran_launch_window_s":  1800,   # all Iranian launches within T=0 to T+30 min
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},   # ~5,000 Shaheds
            {"name": "IRGCN Sea Drone",  "weight": 0.137},   # ~990 surface drones
            {"name": "Emad MRBM",        "weight": 0.058},   # ~420 Emad MRBMs
            {"name": "Zolfaghar SRBM",   "weight": 0.058},   # ~420 Zolfaghar
            {"name": "Khalij Fars ASBM", "weight": 0.057},   # ~415 Khalij Fars
        ],
    },
    "high": {
        "label": "Scenario C -- High Capability / CAP HIT (8 CSGs)",
        "description": (
            "SITUATION: Iran fires near-maximum available post-strike inventory in a single "
            "compressed salvo, deliberately breaching the Aegis 4,000-round intercept capacity "
            "ceiling. This scenario tests the fundamental arithmetic limit of layered missile "
            "defense: when incoming track count exceeds the total intercept magazine across "
            "all 8 CSGs, no amount of per-shot SSPK improvement prevents breakthroughs.\n\n"
            "DRONE SATURATION (T+0 to T+60 min): 2,665 Shahed-136 at full 50% post-strike "
            "inventory inundate all 8 Aegis groups simultaneously. With each CSG facing "
            "~333 drones, CIWS magazines are fully exhausted within the first 25–30 minutes. "
            "RAM/SeaRAM racks fire continuously until depleted. ESSM becomes the primary "
            "close-in defense once CIWS is Winchester. 265 IRGCN surface drones exploit "
            "the CIWS exhaustion window to close on escorts unopposed by automated systems, "
            "forcing DDG crews to engage with deck-mounted small arms and 5-inch gun.\n\n"
            "BALLISTIC MASS SALVO (concurrent with drones): 697 Fateh-313 SRBMs (range "
            "500 km, CEP &lt;10 m, GPS/GLONASS terminal guidance) launch from dispersed sites "
            "in a compressed 20-minute window designed to overwhelm Aegis track files. "
            "402 Emad MRBMs provide the deep-strike component, targeting CVNs from ranges "
            "beyond SM-2 intercept. The combined ballistic track density at any given SM-6 "
            "radar exceeds 40 simultaneous tracks — the published limit for SPY-1D(V).\n\n"
            "INTERCEPT CAPACITY EXCEEDED: At 4,030 total tracks against a system-wide "
            "magazine of ~4,000 intercept rounds (SM-6 + SM-2 + ESSM + RAM across 8 "
            "CSGs), the cap is mathematically breached. Even at theoretical 100% SSPK, "
            "the last ~30–2,046 rounds have no interceptor to meet them.\n\n"
            "US RESPONSE: 320 TLAM/JASSM strikes target all 12 launch sites. Most coastal "
            "batteries are suppressed by T+60 min, but the ballistic salvo was already "
            "in flight before the first impacts. Inland sites at Isfahan and Dezful absorb "
            "strikes but continue launching from dispersed TELs during the suppression.\n\n"
            "ASSESSMENT: This is a catastrophic outcome for the US fleet. Multiple CSGs are "
            "destroyed (10+ hits each). The post-strike environment would see the US "
            "operating with severely reduced carrier aviation capacity for months.\n\n"
            "1,100 missiles + 2,665 air drones + 265 sea drones = 4,030 total | "
            "~1,984 intercepted | ~2,046 breakthrough [INTERCEPT CAP HIT]."
        ),
        "n_missiles":    7565,          # ~5,000 Shaheds (post-50% strike; 5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.496,
        "wave_s":         86400,
        "n_arc":           10,
        "n_sm6":           16,
        "n_us_strikes_per_csg": 40,   # 40 × 8 = 320 total
        "munitions": [
            {"name": "Shahed-136",      "weight": 0.661},   # 2665/4030
            {"name": "IRGCN Sea Drone", "weight": 0.066},   # 266/4030
            {"name": "Fateh-313 SRBM",  "weight": 0.173},   # 697/4030
            {"name": "Emad MRBM",       "weight": 0.100},   # 402/4030
        ],
    },
    "iran_best": {
        "label": "Scenario E -- Best Case Iran / CAP HIT (8 CSGs)",
        "description": (
            "SITUATION: Iran achieves maximum operational coordination — full inventory "
            "commitment, synchronized multi-domain launch, and prolonged 90-minute salvo "
            "duration that exhausts US interceptor magazines before the final waves arrive. "
            "This represents the assessed upper bound of Iranian offensive capacity after "
            "50% pre-strike attrition. It is the worst-case planning scenario for US "
            "carrier strike group survivability.\n\n"
            "DRONE TSUNAMI (T+0 to T+90 min): 4,000 Shahed-136 drones — Iran's full "
            "remaining inventory commitment — launch in rolling waves from 12 sites across "
            "a 1,200 km coastal frontage. Rather than a single spike, the waves are "
            "staggered in 15-minute packets to prevent US CIWS from recovering between "
            "engagements. By T+30 min, all 8 CSG CIWS systems are Winchester. By T+45 min, "
            "RAM/SeaRAM racks are expended. From T+45 min onward, the only close-in "
            "defense is ESSM (50 km range, not optimized for low-slow targets) and "
            "5-inch naval gun. 400 IRGCN surface drones provide persistent harassment of "
            "inner-screen DDGs, forcing gun engagements that further distract Aegis from "
            "the ballistic track picture.\n\n"
            "PRECISION MISSILE SURGE (T+30 to T+90 min): 335 Emad MRBMs, 335 Khalij Fars "
            "ASBMs, and 330 Fateh-313 SRBMs launch from inland sites after the drone wave "
            "has consumed close-in defensive capacity. These arrive during the CIWS-exhausted "
            "window, facing only SM-6/SM-2 (already partially depleted by the first-wave "
            "drone engagements). The Khalij Fars ASBM is the primary carrier-killer: its "
            "EO/IR seeker acquires the CVN flight deck at 45 km altitude and maneuvers "
            "to hit the island structure or flight deck arresting gear.\n\n"
            "INTERCEPT CAP BREACH: The 4,000-round system-wide magazine is exhausted by "
            "approximately T+60 min. The final 1,400 missiles/drones arrive against a "
            "fleet that has shot its last interceptor. US counterstrikes (320 TLAM/JASSM) "
            "destroyed most coastal sites by T+75 min — too late to stop the inland salvo "
            "already in flight.\n\n"
            "ASSESSMENT: Catastrophic fleet loss. Historical comparison: the 1945 "
            "Kamikaze campaign at Okinawa sank 34 ships and damaged 386 more using "
            "~1,465 aircraft over 82 days. This scenario delivers a comparable volume "
            "against 8 CSGs in under 90 minutes.\n\n"
            "1,000 missiles + 4,000 air drones + 400 sea drones = 5,400 total | "
            "~1,981 intercepted | ~3,419 breakthrough [INTERCEPT CAP HIT]."
        ),
        "n_missiles":    6750,          # ~5,000 Shaheds — maximum available (5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.370,
        "wave_s":         86400,
        "n_arc":            8,
        "n_sm6":           12,
        "n_us_strikes_per_csg": 40,   # 40 × 8 = 320 total
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.741},   # 4000/5400
            {"name": "IRGCN Sea Drone",  "weight": 0.074},   # 400/5400
            {"name": "Emad MRBM",        "weight": 0.062},   # 335/5400
            {"name": "Khalij Fars ASBM", "weight": 0.062},   # 335/5400
            {"name": "Fateh-313 SRBM",   "weight": 0.061},   # 330/5400
        ],
    },
    "usa_best": {
        "label": "Scenario F -- Best Case USA (8 CSGs)",
        "description": (
            "SITUATION: US pre-emptive strikes have degraded Iranian capabilities to the "
            "minimum viable threshold — approximately 30% of pre-crisis inventory remains "
            "operational. Iranian command-and-control is disrupted, launches are poorly "
            "coordinated, and salvos arrive in small uncoordinated packets rather than "
            "synchronized waves. This scenario benchmarks maximum US defensive performance.\n\n"
            "IRANIAN CAPABILITY: 665 total munitions launched from surviving sites: "
            "400 Shahed-136 drones arrive in staggered groups of 10–20 rather than "
            "coordinated mass waves, giving CIWS clear engagements between groups. "
            "65 IRGCN surface drones attempt to close but are detected early and "
            "engaged by DDG 5-inch guns at 15+ km, well outside naval gun effective range. "
            "200 legacy missiles — Shahab-3 MRBMs, Noor ASCMs, Fateh-110 SRBMs — are "
            "the only ballistic/cruise component. Without coordination with the drone "
            "wave, they arrive into fully-loaded CIWS and maximum SM-6 availability.\n\n"
            "US DEFENSIVE PERFORMANCE: Fully-alerted Aegis with SPY-6 (Ford-class) and "
            "SPY-1D(V) achieves 93% intercept rate. Shahab-3 terminal phases are tracked "
            "from 1,200 km out by E-2D Hawkeye; SM-6 engages at 240 km with high "
            "confidence. Noor sea-skimmers are detected by DDG SPY-1D at 45 km and "
            "meet dual Phalanx engagement. SeaRAM mops up surviving drones. ESSM is "
            "barely used — SM-6 clears the threat at standoff.\n\n"
            "US COUNTERSTRIKE: 480 TLAM/JASSM strikes — the heaviest strike package of "
            "any scenario — systematically eliminate all 12 Iranian launch sites. With "
            "60 rounds per CSG, each site receives 3–5× the 25-hit destruction threshold. "
            "All sites are inactivated by T+75 min; no follow-on salvo is possible.\n\n"
            "ASSESSMENT: Only ~51 rounds break through, causing minor damage to 2–3 "
            "escort destroyers with no CVN hits. All 8 CSGs remain fully operational. "
            "Iran's launch network is effectively dismantled by T+90 min. This scenario "
            "validates the strategic case for pre-emptive action: catching Iran's missiles "
            "on the ground is decisively superior to intercepting them in flight.\n\n"
            "200 missiles + 400 air drones + 65 sea drones = 665 total | "
            "~614 intercepted | ~51 breakthrough — fleet intact."
        ),
        "n_missiles":    1660,          # ~1,000 Shaheds (Iran badly degraded post-strike)
        "intercept_cap": 4000,
        "intercept_rate": 0.932,
        "wave_s":         86400,
        "n_arc":           16,
        "n_sm6":           24,
        "n_us_strikes_per_csg": 60,
        "munitions": [
            {"name": "Shahed-136",      "weight": 0.602},   # 400/665
            {"name": "IRGCN Sea Drone", "weight": 0.098},   # 65/665
            {"name": "Shahab-3 MRBM",  "weight": 0.150},   # 100/665
            {"name": "Noor ASCM",       "weight": 0.090},   # 60/665
            {"name": "Fateh-110 SRBM",  "weight": 0.060},   # 40/665
        ],
    },

    # ==============================================================
    # PHASED SCENARIOS G, H, I
    # Doctrine: drone swarm launches first (Phase 1, hr 0–1) to exhaust
    # CIWS / RAM / ESSM.  Ballistic and cruise missiles follow (Phase 2,
    # hr 1–2), arriving while defenses are depleted.
    # Iran's stated "layered saturation" doctrine mirrors this sequence.
    # Intercept rates are worse than uncoordinated equivalents because
    # CIWS magazines are partially empty when missiles arrive.
    # ==============================================================
    "drone_first_low": {
        "label": "Scenario G -- Drone-First Low (Phased Assault)",
        "description": (
            "SITUATION: Iran employs its documented 'multi-echelon saturation' doctrine "
            "with legacy munitions. IRGCN tactical doctrine publicly describes sequential "
            "drone/missile launch sequences; this scenario applies that concept at minimum "
            "post-strike inventory. The key innovation vs. Scenario A (Low) is temporal "
            "separation: drones deplete CIWS magazines first, then legacy missiles arrive "
            "into a degraded defensive environment.\n\n"
            "PHASE 1 — DRONE/SURFACE SWARM (T+0 to T+60 min): All 665 Shahed-136 "
            "drones and 135 surface drones launch simultaneously. Unlike uncoordinated "
            "Scenario A, launch timing is compressed to ensure the entire drone wave "
            "engages within the same 60-minute window, maximizing CIWS saturation overlap. "
            "Phalanx systems engage at maximum cyclic rate. RAM/SeaRAM draws down by "
            "T+35–45 min. When CIWS begins reloading at T+50 min, there is a critical "
            "3–8 minute gap — precisely when the Phase 2 ballistic missiles are scheduled "
            "to enter inner defense zones.\n\n"
            "PHASE 2 — LEGACY MISSILE SALVO (T+60 to T+120 min): 265 missiles launch "
            "from surviving sites during the drone wave's final phase, timed to arrive "
            "while CIWS is reloading. Shahab-3 MRBMs, Noor sea-skimming ASCMs, and "
            "Fateh-110 SRBMs engage during the post-CIWS gap. Without the overwhelming "
            "track density of Scenario B or D, SM-6 has more available channels per "
            "missile — but the CIWS depletion effect still degrades intercept rate "
            "from 69% (Scenario A uncoordinated) to 65% (Scenario G phased).\n\n"
            "PHASING BONUS: The 4% intercept rate reduction equates to ~43 additional "
            "breakthroughs vs. the equivalent uncoordinated attack. Against 8 CSGs, "
            "43 extra hits changes 2–3 'damaged' outcomes to 'mission-killed'.\n\n"
            "265 missiles + 665 air drones + 135 sea drones = 1,065 total | "
            "~690 intercepted | ~375 breakthrough (43 more than uncoordinated Scenario A)."
        ),
        "n_missiles":    5600,          # ~3,500 Shaheds (drone-first emphasis)
        "intercept_cap": 4000,
        "intercept_rate": 0.650,   # worse than uncoordinated A (0.688) — CIWS preoccupied
        "wave_s":         21600,   # total scenario: 6 hours (covers both phases)
        "phase1_end_s":   10800,   # drones launch in first 3h
        "phase2_start_s": 10800,   # missiles begin after all drones are airborne
        "phase2_dur_s":   10800,   # missile launch window: 3h missile phase
        "n_arc":           14,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 20,
        "munitions": [
            {"name": "Shahed-136",      "weight": 0.625},   # 665/1065
            {"name": "IRGCN Sea Drone", "weight": 0.127},   # 135/1065
            {"name": "Shahab-3 MRBM",  "weight": 0.099},   # 105/1065
            {"name": "Noor ASCM",       "weight": 0.075},   # 80/1065
            {"name": "Fateh-110 SRBM",  "weight": 0.074},   # 80/1065
        ],
    },
    "drone_first_medium": {
        "label": "Scenario H -- Drone-First Medium (Phased Assault)",
        "description": (
            "SITUATION: Iran applies phased doctrine at medium capability — 1,335 Shahed "
            "drones fully exhaust all CIWS capacity before the precision missile layer "
            "arrives. This is the most tactically sophisticated medium-capability Iranian "
            "scenario and approximates doctrinal outputs from IRGCN war-gaming publications "
            "obtained through open-source intelligence.\n\n"
            "PHASE 1 — CIWS EXHAUSTION (T+0 to T+60 min): 1,335 Shahed-136 and 200 "
            "surface drones attack in three rolling sub-waves of ~450 drones each, "
            "separated by 15-minute intervals. The sub-wave timing is critical: "
            "each wave exhausts the remaining CIWS ammunition before the next arrives, "
            "preventing reload. By T+55 min, all 8 CSG Phalanx systems are Winchester "
            "and RAM/SeaRAM racks are empty. Only ESSM (50 km, limited drone track "
            "discrimination) and SM-6 (overkill cost-per-drone ~$4.3M vs $20k threat) "
            "remain available for close-in defense.\n\n"
            "PHASE 2 — PRECISION STRIKE (T+60 to T+120 min): 665 precision missiles "
            "launch from inland sites after confirming the drone wave is through the "
            "outer defense rings. 200 Emad MRBMs with maneuvering RVs arrive into a "
            "CIWS-naked fleet. 264 Zolfaghar SRBMs saturate SM-6 fire control channels. "
            "201 Khalij Fars ASBMs — the primary CVN killers — acquire carrier flight "
            "decks at terminal descent with no close-in backup remaining.\n\n"
            "COORDINATION PENALTY FOR US: The phasing adds ~200 breakthrough rounds vs. "
            "uncoordinated Scenario B (793→892), representing an additional 2–4 escort "
            "destroyers mission-killed and significantly higher CVN damage probability.\n\n"
            "US RESPONSE: 240 TLAM/JASSM strikes, but with perfect timing impossible "
            "during a 2-hour engagement, several launches occur from partially-suppressed "
            "sites. Coastal batteries suppressed by T+50 min cannot stop the inland salvo.\n\n"
            "665 missiles + 1,335 air drones + 200 sea drones = 2,200 total | "
            "~1,308 intercepted | ~892 breakthrough (99 more than Scenario B)."
        ),
        "n_missiles":    8250,          # ~5,000 Shaheds (drone-first; 5K cap per scenario)
        "intercept_cap": 4000,
        "intercept_rate": 0.600,   # worse than uncoordinated B (0.645)
        "wave_s":         28800,
        "phase1_end_s":   14400,
        "phase2_start_s": 14400,
        "phase2_dur_s":   14400,
        "n_arc":           12,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.607},   # 1335/2200
            {"name": "IRGCN Sea Drone",  "weight": 0.091},   # 200/2200
            {"name": "Emad MRBM",        "weight": 0.091},   # 200/2200
            {"name": "Zolfaghar SRBM",   "weight": 0.120},   # 264/2200
            {"name": "Khalij Fars ASBM", "weight": 0.091},   # 201/2200
        ],
    },
    "drone_first_high": {
        "label": "Scenario I -- Drone-First High Saturation (Phased Assault)",
        "description": (
            "SITUATION: Iran combines maximum drone employment with precision missile mass "
            "in a 2-hour phased assault. Unlike Scenario C (High, uncoordinated), the "
            "phasing is deliberate and operationally significant: the drone wave arrives "
            "60 minutes before the ballistic layer, ensuring CIWS capacity reaches zero "
            "before the first missile enters close-in defensive range. This is the "
            "worst-case phased scenario and the most operationally sophisticated.\n\n"
            "PHASE 1 — TOTAL CIWS EXHAUSTION (T+0 to T+60 min): 2,665 Shaheds "
            "and 265 surface drones attack in a continuous rolling stream. Track density "
            "peaks at ~333 simultaneous Shahed contacts per CSG. Phalanx engages at "
            "maximum 4,500 rpm but with 333 tracks, engagement queuing is impossible — "
            "the system can only engage one track at a time. RAM fires all 63–105 rounds "
            "per CSG in the first 20 minutes. SeaRAM exhausted by T+25 min. "
            "ESSM begins engaging Shaheds at 50 km — a $1.5M round vs a $20k drone. "
            "By T+45 min, all CIWS systems are Winchester. The last 15 minutes of the "
            "drone wave arrives completely uncontested by close-in systems.\n\n"
            "PHASE 2 — UNCONTESTED MISSILE SURGE (T+60 to T+120 min): 697 Fateh-313 "
            "SRBMs and 402 Emad MRBMs launch from inland batteries. They fly into a "
            "fleet with zero Phalanx, zero RAM, and SM-6 magazines already partially "
            "depleted by drone engagements during Phase 1. Intercept rate collapses to "
            "46% — the lowest of any scenario — as SM-6 is the last line of defense "
            "against threats originally designed for multi-layer engagement.\n\n"
            "US COUNTERSTRIKE: 320 TLAM/JASSM destroy most coastal sites by T+90 min. "
            "However, the Phase 2 ballistic salvo launched from inland sites at T+60 "
            "is already in flight — suppression came 30 minutes too late.\n\n"
            "ASSESSMENT: Fleet-wide catastrophic damage. Phase coordination reduces "
            "intercept rate from 46% (vs. 50% uncoordinated) producing ~324 additional "
            "breakthroughs vs Scenario C. All 8 CSGs face mission-kill probability >70%.\n\n"
            "1,100 missiles + 2,665 air drones + 265 sea drones = 4,030 total | "
            "~1,842 intercepted | ~2,188 breakthrough."
        ),
        "n_missiles":    7565,          # ~5,000 Shaheds (drone-first; 5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.460,   # worst intercept rate — CIWS exhausted by drones
        "wave_s":         43200,
        "phase1_end_s":   21600,
        "phase2_start_s": 21600,
        "phase2_dur_s":   21600,
        "n_arc":           10,
        "n_sm6":           16,
        "n_us_strikes_per_csg": 40,
        "munitions": [
            {"name": "Shahed-136",      "weight": 0.661},   # 2665/4030
            {"name": "IRGCN Sea Drone", "weight": 0.066},   # 266/4030
            {"name": "Fateh-313 SRBM",  "weight": 0.173},   # 697/4030
            {"name": "Emad MRBM",       "weight": 0.100},   # 402/4030
        ],
    },
    "coordinated_strike": {
        "label": "Scenario G -- US/IAF Coordinated First Strike (Perfect Timing)",
        "description": (
            "SITUATION: The United States and Israel achieve true time-on-target synchronization "
            "for the opening strike window. All US TLAM/JASSM packages and Israeli Air Force "
            "munitions are pre-launched (missiles in flight before T=0) and arrive on Iranian "
            "launch sites within the first 5 minutes of the conflict timeline. This tests the "
            "maximum impact of pre-emptive suppression on Iran's launch capacity.\n\n"
            "STRIKE EXECUTION: 400 TLAM/JASSM rounds (50 per CSG × 8 CSGs) were launched "
            "hours before T=0, timing their flights to impact Iranian sites at T+0 to T+5 min. "
            "Simultaneously, the Israeli Air Force executes three coordinated packages:\n"
            "  - Nevatim AB (F-35I Adir): 55 sorties × 2 JDAM-ER = 110 precision strikes "
            "    on coastal battery control nodes at &lt;80 km standoff range\n"
            "  - Hatzerim AB (F-15I Ra'am): 40 sorties × 2 Rampage ALCM = 80 standoff strikes "
            "    at 250 km range against ballistic missile TEL storage and hardened tunnels\n"
            "  - Ramon AB (F-16I Sufa): 73 sorties × 2 SPICE-2000 = 146 precision glide bomb "
            "    strikes on dispersed launch sites\n\n"
            "SUPPRESSION EFFECT: Sites receiving 25+ hits in the T+0 to T+5 window go silent "
            "before their TELs can position and launch. Multiple coastal batteries are destroyed "
            "before the first Shahed drone is airborne. Iranian OOB is reduced from the notional "
            "1,935 total to a degraded subset as site-suppressed launches are eliminated.\n\n"
            "RESIDUAL IRANIAN STRIKE: Missiles already on launchers and partially-committed "
            "drone sorties launch despite incoming US/IAF fires — 1,935 total planned, "
            "but surviving site launches represent the actual salvo. US intercept rate "
            "rises to 78% as fewer tracks overwhelm Aegis and SM-6 has more engagement "
            "time per track.\n\n"
            "COMPARISON TO SCENARIO D: Same Iranian OOB as Realistic, but strike timing "
            "produces ~280 fewer breakthroughs (441 vs. 713) — validating the strategic "
            "value of precisely-timed pre-emptive action over reactive defense.\n\n"
            "1,935 total (same OOB as Realistic) | ~1,494 intercepted | ~441 breakthrough."
        ),
        "n_missiles":    7250,          # ~5,000 Shaheds (same OOB as realistic; 5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.780,   # higher P(k): fewer missiles, less CIWS saturation
        "wave_s":         43200,
        "n_arc":           10,
        "n_sm6":           20,     # fewer breakthroughs → SM-6 not exhausted early
        "n_us_strikes_per_csg": 50,  # 50 × 8 CSGs = 400 total; pre-loaded strike packages
        "us_strike_timing": "perfect",   # all impacts arrive at t=0±300s
        "iaf_timing": "perfect",         # IAF coordinated in same opening window
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},   # same mix as realistic
            {"name": "IRGCN Sea Drone",  "weight": 0.137},
            {"name": "Emad MRBM",        "weight": 0.058},
            {"name": "Zolfaghar SRBM",   "weight": 0.058},
            {"name": "Khalij Fars ASBM", "weight": 0.057},
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO H — Iranian Intelligence-Driven Focused Salvo
    # ------------------------------------------------------------------
    "focused_salvo": {
        "label": "Scenario H -- Iranian Focused Salvo (All Fire on CVN-78 Ford)",
        "description": (
            "SITUATION: Iranian intelligence — likely from space-based electro-optical "
            "reconnaissance, signals intelligence intercepts, and commercial satellite "
            "imagery analysis — confirms the precise position of USS Gerald R. Ford "
            "(CVN-78), the fleet's most advanced carrier and de facto task force flagship. "
            "Iran elects to concentrate ALL 1,935 available munitions on this single "
            "target rather than distributing across 8 CSGs. The other 7 carrier strike "
            "groups are not engaged.\n\n"
            "TACTICAL RATIONALE: Sinking or disabling CVN-78 would deliver maximum "
            "strategic shock — removing the Ford-class's ANB-3 nuclear propulsion, "
            "Advanced Weapons Elevator, Electromagnetic Aircraft Launch System (EMALS), "
            "and Advanced Arresting Gear (AAG), all irreplaceable in a conflict timeframe. "
            "Iran's assessment: it is better to certainly kill one carrier than probably "
            "damage eight. Loss of CVN-78 would degrade US carrier aviation capability "
            "for 2–5 years during repair.\n\n"
            "FORD'S DEFENSIVE CAPACITY: CVN-78 has 3× Mk 49 RAM launchers (63 rounds) "
            "plus SeaRAM. Escorts — 3× DDG-51 Flight III plus CG-60 USS Normandy — "
            "provide SM-6 (66 rounds), SM-2 (203 rounds), ESSM (144 rounds). Total "
            "magazine is substantial but designed for a distributed threat environment, "
            "not 1,935 incoming tracks simultaneously. Ford's 6-ship screen will exhaust "
            "its 66 SM-6 rounds against the first ~40 ballistic tracks, leaving remaining "
            "threats for SM-2 and CIWS engagement only.\n\n"
            "DRONE SATURATION: 1,335 Shaheds target Ford's specific GPS coordinates. "
            "CIWS and RAM are exhausted within 25 minutes. From T+25 min onward, "
            "breakthroughs reach the hull and flight deck continuously.\n\n"
            "OUTCOME: Same Iranian OOB as Scenario D (Realistic), but concentrated on "
            "one hull. CVN-78 is mission-killed with high probability. The other 7 CSGs "
            "are undamaged and available for counter-strike operations.\n\n"
            "1,935 total (all fire on CVN-78) | ~1,222 intercepted | ~713 breakthrough "
            "concentrated on one target."
        ),
        "n_missiles":    7250,          # ~5,000 Shaheds — all on one hull (5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.634,  # same P(k) as realistic
        "wave_s":         21600,
        "n_arc":           10,
        "n_sm6":           16,
        "n_us_strikes_per_csg": 30,
        "focus_csg": "USS Gerald R. Ford (CVN-78)",   # all Iranian fire on this hull
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},
            {"name": "IRGCN Sea Drone",  "weight": 0.137},
            {"name": "Emad MRBM",        "weight": 0.058},
            {"name": "Zolfaghar SRBM",   "weight": 0.058},
            {"name": "Khalij Fars ASBM", "weight": 0.057},
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO I — Hypersonic Threat (Fattah-1 HGV Deployment)
    # ------------------------------------------------------------------
    "hypersonic_threat": {
        "label": "Scenario I -- Hypersonic Threat (Fattah-1 HGV + Realistic Mix)",
        "description": (
            "SITUATION: Iran operationalizes the Fattah-1 hypersonic glide vehicle — "
            "announced by IRGCN in June 2023, claimed Mach 13–15, range 1,400 km. "
            "If operational as claimed, the Fattah-1 represents a fundamental challenge "
            "to layered ballistic missile defense: its skip-glide trajectory defeats "
            "AEGIS SPY-1/SPY-6 track prediction, and SM-6 Block IA has no reliable "
            "intercept solution against Mach 13+ maneuvering hypersonic targets.\n\n"
            "HYPERSONIC GLIDE VEHICLE THREAT PROFILE: The Fattah-1 launches on a "
            "depressed trajectory to ~80 km altitude (vs. ~280 km for Shahab-3), "
            "then glides at Mach 13–15 with 3–4g lateral maneuvering capability. "
            "Three critical implications:\n"
            "  1. SHORT FLIGHT TIME: At Mach 13 and 1,400 km range, time-of-flight is "
            "     ~6 minutes — halving the SM-6 engagement window vs. a Shahab-3 MRBM.\n"
            "  2. UNPREDICTABLE TERMINAL PATH: Skip-glide creates radar track "
            "     discontinuities that defeat AEGIS fire control prediction algorithms.\n"
            "  3. INTERCEPT ALTITUDE: Gliding at 40–60 km altitude is above CIWS/RAM "
            "     ceiling and at the edge of SM-6 Block IA endo-atmospheric envelope — "
            "     P(k) ~5% vs. ~90% for conventional ballistic TBMs.\n\n"
            "SCENARIO COMPOSITION: 168 Fattah-1 HGVs replace a fraction of the Realistic "
            "scenario's ballistic layer. The remaining mix of Emad MRBMs, Zolfaghar SRBMs, "
            "and Khalij Fars ASBMs is unchanged. Drones are identical to Scenario D. "
            "The hypersonic component is nearly uninterceptable: only 5% are killed by "
            "SM-6, meaning 160 of 168 HGVs reach their targets. At 80,000 m peak altitude "
            "and 4 km/s terminal velocity, kinetic impact energy alone (no explosive warhead "
            "required) is sufficient to mission-kill an escort-class hull.\n\n"
            "ASSESSMENT: The hypersonic layer alone causes more kills than the entire "
            "non-HGV ballistic component combined. Breakthrough count rises from 713 "
            "(Realistic) to ~820 (+107), with additional hits concentrated on "
            "previously-underserved targets. Source: CSIS Missile Threat / Jane's DW "
            "2024 / IRGCN June 2023 public announcement.\n\n"
            "1,935 total | ~1,115 intercepted | ~820 breakthrough (168 near-uninterceptable HGVs)."
        ),
        "n_missiles":    7250,          # ~5,000 Shaheds + HGV layer (5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.634,
        "wave_s":         21600,
        "n_arc":           10,
        "n_sm6":           16,
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},   # ~7,000 Shaheds
            {"name": "IRGCN Sea Drone",  "weight": 0.137},   # 265/1935
            {"name": "Fattah-1 HGV",    "weight": 0.087},   # 168/1935
            {"name": "Emad MRBM",        "weight": 0.029},   # 56/1935
            {"name": "Zolfaghar SRBM",   "weight": 0.029},   # 56/1935
            {"name": "Khalij Fars ASBM", "weight": 0.028},   # 55/1935
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO J — Pure Ballistic Barrage
    # ------------------------------------------------------------------
    "ballistic_barrage": {
        "label": "Scenario J -- Pure Ballistic Barrage (No Drones, SM-6 Undistracted)",
        "description": (
            "SITUATION: Iran conducts a pure ballistic strike with no drone component — "
            "a scenario that might occur if drone inventory was exhausted in a prior "
            "engagement phase or if Iran assesses that launching drones against fully-alerted "
            "CIWS is wasteful. This tests a fundamentally different threat geometry: "
            "without CIWS saturation, SM-6 operates at maximum efficiency, but every "
            "breakthrough carries far greater destructive power than a Shahed drone.\n\n"
            "THREAT COMPOSITION (600 missiles, no drones): The ballistic mix maximizes "
            "warhead payload — all selected munitions carry 450–750 kg unitary warheads:\n"
            "  - Shahab-3 MRBM (15%, 90 rounds): 500 kg warhead, Mach 6–7 terminal, "
            "    high-arc parabolic trajectory; legacy but still lethal on escort hits\n"
            "  - Emad MRBM (20%, 120 rounds): 750 kg warhead, maneuvering RV, "
            "    primary CVN-killer threat in this scenario\n"
            "  - Zolfaghar SRBM (25%, 150 rounds): 450 kg, GPS precision &lt;10m CEP, "
            "    targets command nodes and flight deck structures\n"
            "  - Khalij Fars ASBM (25%, 150 rounds): EO/IR terminal seeker discriminates "
            "    carrier from escort; purpose-built for this engagement\n"
            "  - Fateh-313 SRBM (15%, 90 rounds): 450 kg GPS precision; targets "
            "    communications and radar arrays\n\n"
            "US DEFENSIVE ADVANTAGE: Without drone saturation, CIWS magazines are fully "
            "available throughout the engagement. SM-6 radar is not competing with 1,335 "
            "slow Shahed tracks — all fire control channels are dedicated to ballistic "
            "threats. This raises intercept rate from ~63% (Realistic) to ~85%. SM-2 "
            "engages mid-altitude threats below SM-6 range. ESSM has no role.\n\n"
            "HOWEVER — EACH HIT IS CATASTROPHIC: The 90 breakthrough rounds are all "
            "heavy unitary warheads. No $20k drones in the breakthrough count — every "
            "hit is a 450–750 kg shaped-charge or kinetic-penetrating warhead designed "
            "to defeat armored deck structures. Expected damage per hit is 2–4× greater "
            "than the mixed scenarios. Even at 15% breakthrough rate, catastrophic "
            "hull losses are probable.\n\n"
            "ASSESSMENT: Iran fires fewer rounds but achieves higher-value hits per "
            "breakthrough. The ballistic-only approach is optimal when drone inventory "
            "is exhausted — trading quantity for per-hit lethality.\n\n"
            "600 ballistic missiles (no drones) | ~510 intercepted | ~90 breakthrough "
            "(all heavy warhead capable of mission-kill)."
        ),
        "n_missiles":     600,
        "intercept_cap": 4000,
        "intercept_rate": 0.850,   # undistracted SM-6/SM-2; no CIWS pre-exhaustion
        "wave_s":         10800,   # 3-hour rapid volley
        "n_arc":           12,
        "n_sm6":           20,     # full magazine available; no CIWS trades
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Shahab-3 MRBM",    "weight": 0.15},
            {"name": "Emad MRBM",        "weight": 0.20},
            {"name": "Zolfaghar SRBM",   "weight": 0.25},
            {"name": "Khalij Fars ASBM", "weight": 0.25},
            {"name": "Fateh-313 SRBM",   "weight": 0.15},
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO BB — Full Ballistic Surge (2,500 Missiles, No Drones)
    # ------------------------------------------------------------------
    "ballistic_surge": {
        "label": "Scenario BB -- Full Ballistic Surge (2,500 Missiles + 26 Tripoli Drones, 4 CSGs, 10% Fattah-1 HGV)",
        "description": (
            "SITUATION: Iran commits its entire reconstituted ballistic missile stockpile "
            "(~2,500 rounds; Alma Research / 19FortyFive Feb 2026 estimate) in a single "
            "coordinated barrage against the 4-CVN battle group (Lincoln, Ford, Bush, Alpha). "
            "Simultaneously, 26 Shahed-136 loitering munitions — including 1 AI/computer-vision "
            "guided variant with guaranteed terminal lock-on — are specifically tasked against "
            "USS Tripoli (LHA-7), operating as an amphibious assault platform in the adjacent "
            "operating area near Bahrain. The Tripoli's SeaRAM (22 rounds) and Phalanx CIWS "
            "provide the only point-defense; she has no SM-6, no SM-2, and no DDG escort.\n\n"
            "THREAT COMPOSITION — MAIN BALLISTIC SALVO (2,500 missiles against 4 CVN/CSGs):\n"
            "  - Zolfaghar SRBM (25%, ~620 rounds): 450 kg warhead, GPS &lt;10m CEP; "
            "    most numerous surviving SRBM post-October 2024 Israeli strikes\n"
            "  - Emad MRBM (20%, ~497 rounds): 750 kg maneuvering RV; Aegis Pk drops "
            "    to ~35–45% vs ~75% for non-maneuvering ballistic\n"
            "  - Shahab-3 MRBM (20%, ~497 rounds): 500 kg warhead, Mach 6–7 terminal; "
            "    legacy stockpile, still lethal at scale\n"
            "  - Khalij Fars ASBM (15%, ~373 rounds): EO/IR terminal seeker tracks "
            "    carrier thermal signature; purpose-built CVN-killer\n"
            "  - Fateh-313 SRBM (10%, ~249 rounds): 450 kg GPS precision; radar arrays, "
            "    VLS magazine structures, flight deck superstructures\n"
            "  - Fattah-1 HGV (10%, ~249 rounds): Mach 13–15 hypersonic glide vehicle; "
            "    Aegis Pk estimated 5–15%; near-uninterceptable; each hit near-certain CVN kill\n\n"
            "TRIPOLI DRONE SUPPLEMENT (26 Shahed-136 targeting LHA-7):\n"
            "  - 25 standard Shahed-136: 40 kg warhead; SeaRAM engages each at ~3–5 km; "
            "    CIWS backup at ~1.5 km. With 26 rounds vs 22 SeaRAM + CIWS, magazine "
            "    exhaustion is likely before the final drones arrive.\n"
            "  - 1 AI/EO-IR-guided Shahed-136: EO/IR terminal seeker acquires LHA-7 "
            "    thermal signature at 35 km; maneuvering final approach defeats CIWS "
            "    lead-angle prediction — guaranteed hit. LHA-7's flight deck and F-35B "
            "    parking are the primary aim-point.\n\n"
            "AEGIS SATURATION (4 CVNs): With ~625 inbound per CSG (2,500 / 4), the fire-control "
            "queue is oversubscribed ~35× vs the 18-simultaneous-channel Aegis ceiling. "
            "SM-6 magazines (~40 per CSG × 4 CSGs ≈ 160 SM-6 shots total) are exhausted by "
            "the time only ~6–8% of the salvo has arrived. Once magazines empty, every remaining "
            "inbound is uncontested — the Aegis fires its last SM-6 while 2,300+ missiles are still "
            "inbound. Expected intercepts: ~190–220 total. Expected breakthrough: ~2,300+.\n\n"
            "ASSESSMENT: Iran's full reconstituted ballistic stockpile exhausts all 4 CSG "
            "magazines by the first ~160 rounds, leaving 2,340+ missiles completely uncontested. "
            "This is not saturation — it is abolition of the defense. The Shahed supplement "
            "specifically engineers the same effect against Tripoli's 22-round SeaRAM: the "
            "first 22 drones absorb the entire magazine; the 23rd through 26th arrive unopposed, "
            "including the guaranteed AI-guided hull strike.\n\n"
            "2,500 ballistic missiles (4 CVN/CSG fleet) + 26 Shahed-136 (Tripoli) | "
            "~190–220 intercepted (magazine-exhausted by ~8% through salvo) | ~2,300+ breakthrough — "
            "catastrophic fleet loss. Tripoli: ~3–5 drone hits including 1 AI-guided LHA-7 flight deck hit."
        ),
        "csg_fleet":     BALLISTIC_SURGE_WITH_TRIPOLI,   # 4 CVNs + USS Tripoli (5 elements)
        "ballistic_targets": {                            # ballistic missiles only hit these 4
            "USS Abraham Lincoln (CVN-72)",
            "USS Gerald R. Ford (CVN-78)",
            "USS George H.W. Bush (CVN-77)",
            "CSG Alpha",
        },
        "drone_focus_csg": "USS Tripoli (LHA-7)",        # all Shahed-136 drones target Tripoli
        "n_missiles":     2526,
        "intercept_cap": 4000,
        "intercept_rate": 0.720,   # saturation at scale + HGV Pk drag
        "wave_s":         10800,   # 3-hour coordinated volley
        "n_arc":           12,
        "n_sm6":           20,     # full magazine initially; exhausted by mid-engagement
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Zolfaghar SRBM",   "weight": 0.247},   # ~624 rounds
            {"name": "Emad MRBM",        "weight": 0.197},   # ~498 rounds
            {"name": "Shahab-3 MRBM",    "weight": 0.197},   # ~498 rounds
            {"name": "Khalij Fars ASBM", "weight": 0.148},   # ~374 rounds
            {"name": "Fateh-313 SRBM",   "weight": 0.099},   # ~250 rounds
            {"name": "Fattah-1 HGV",     "weight": 0.099},   # ~250 rounds
            {"name": "Shahed-136",       "weight": 0.013},   # ~33 → ~26 expected at Tripoli
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO K — ASCM Swarm (Sea-Skimming Saturation)
    # ------------------------------------------------------------------
    "ascm_swarm": {
        "label": "Scenario K -- ASCM Swarm (1,000 Sea-Skimming Anti-Ship Missiles)",
        "description": (
            "SITUATION: Iran executes a pure anti-ship cruise missile swarm — no ballistic "
            "missiles, no drones — using maximum available ASCM inventory plus maximum "
            "theoretical capacity from ship-launched and submarine-launched platforms. "
            "NOTE: This scenario exceeds Iran's estimated post-strike ASCM inventory "
            "(post-50%: ~100–215 Noor; CM-302 not yet delivered per JINSA Mar 2026). "
            "It models a theoretical maximum ASCM commitment assuming all coastal, "
            "surface, and submarine platforms fire simultaneously.\n\n"
            "MISSILE COMPOSITION:\n"
            "  - 600 Noor ASCM (C-802 derivative): Iran's primary sea-skimming anti-ship "
            "    missile. 165 kg shaped-charge warhead designed to penetrate ship hull "
            "    below the waterline. Subsonic (~0.9 Mach), sea-skimming at 5–10 m AGL. "
            "    Launched from Bandar Abbas, Jask, Qeshm, and Minab coastal batteries, "
            "    IRGCN frigates, and fast-attack craft. Iran has held Noor exercises "
            "    targeting carrier-sized inflatable targets in the Gulf.\n"
            "  - 400 CM-302 Supersonic ASCM (if delivered): Mach 3 sea-skimmer with "
            "    250 kg warhead — a Chinese-derived Ramjet-powered anti-ship missile "
            "    negotiated by Iran but not yet operationally deployed. At Mach 3 and "
            "    5 m AGL, CIWS has &lt;1.5 seconds of engagement time from radar acquisition "
            "    to impact. SM-6 has poor target discrimination against sea-level targets "
            "    approaching end-on in radar clutter.\n\n"
            "DEFENSIVE CHALLENGE: CIWS/SeaRAM is the primary defense against sea-skimmers "
            "— SM-6's radar performance degrades significantly tracking low-altitude "
            "sea-skimming targets in Gulf surface clutter. However, at 1,000 simultaneous "
            "ASCM tracks, CIWS saturation occurs rapidly. Phalanx engages at minimum "
            "range (~1.5 km for air threats) with limited engagement time per target. "
            "Against Mach 3 CM-302, the Phalanx radar-to-fire cycle is compressed from "
            "the nominal 1.5 seconds to under 0.5 seconds — too fast for reliable tracking.\n\n"
            "ASSESSMENT: 450 breakthroughs, all sea-skimming ASCMs with shaped-charge "
            "warheads designed for maximum hull penetration. This is the scenario "
            "most analogous to the 1982 Falklands (Exocet) or 1967 Eilat sinking. "
            "Each hit has a high probability of flooding and progressive loss of buoyancy.\n\n"
            "1,000 ASCMs (600 Noor + 400 CM-302) | ~550 intercepted | ~450 breakthrough."
        ),
        "n_missiles":    1000,
        "intercept_cap": 4000,
        "intercept_rate": 0.550,   # CIWS/SeaRAM-dominated; saturates at high volume
        "wave_s":         10800,
        "n_arc":           12,
        "n_sm6":           10,     # SM-6 less effective vs sea-skimmers; fewer shots taken
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Noor ASCM",              "weight": 0.60},   # 1,200 Noor
            {"name": "CM-302 Supersonic ASCM", "weight": 0.40},   # 800 CM-302
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO L — Shore-Based Layered Defense (THAAD + Patriot + Aegis)
    # ------------------------------------------------------------------
    "strait_transit": {
        "label": "Scenario M -- Strait of Hormuz Column Transit (Maximum Threat)",
        "description": (
            "SITUATION: All 8 CSGs transit the Strait of Hormuz in single-file column — "
            "the only navigable deep-water channel (38–96 km wide, main shipping lane "
            "12 km wide per IISS Military Balance 2024). Lead ship USS Abraham Lincoln "
            "is at 26.622°N, 56.515°E heading 310° (northwest into the Gulf), with all "
            "8 hulls 15 km apart in trail formation. This is the highest-threat tactical "
            "geometry possible: all 12 Iranian coastal batteries can engage the entire "
            "column, with standoff distances as short as 35 km.\n\n"
            "GEOGRAPHY: Bandar Abbas (Iran's primary naval base and Shahed launch hub) "
            "is &lt;40 km from the lead ship's initial position. Qeshm Island sits inside "
            "the strait itself — its batteries can fire from multiple aspect angles "
            "simultaneously, defeating single-bearing countermeasure deployment. "
            "Jask (57.77°E) is 85 km from the column's tail — within Noor ASCM "
            "engagement range for the entire transit duration.\n\n"
            "TACTICAL DISADVANTAGE FOR US:\n"
            "  1. COMPRESSED REACTION TIME: At &lt;40 km standoff, ASCM flight time is "
            "     under 80 seconds. SM-6 needs 2–3 minutes to engage at maximum range — "
            "     close-range engagement windows are cut to 20–35 seconds per missile.\n"
            "  2. NO EVASIVE MANEUVER: The strait's 12 km shipping lane leaves ships "
            "     with &lt;3 km lateral deviation room — Khalij Fars ASBM EO/IR seekers "
            "     cannot be defeated by evasion at these widths.\n"
            "  3. COLUMN GEOMETRY: 8 hulls in trail creates a 120 km long target "
            "     string. Every Iranian coastal battery can engage any ship in the "
            "     column simultaneously, maximizing overlap of coverage zones.\n"
            "  4. CHAFF INEFFECTIVE: At close range and high relative speed, chaff "
            "     bloom dispersal time exceeds ASCM terminal homing lock-on window.\n\n"
            "INTERCEPT RATE: Drops to 55% (vs. 63% in open water Realistic scenario) "
            "due to compressed engagement windows and multi-aspect threat geometry.\n\n"
            "HISTORICAL NOTE: The USS Stark (FFG-31) was struck by two Exocet missiles "
            "at 37 km range in 1987 with no successful intercept. The column geometry "
            "in this scenario presents standoffs 50% shorter than the Stark incident.\n\n"
            "1,935 total | ~1,057 intercepted | ~878 breakthrough (165 more than Scenario D)."
        ),
        "n_missiles":    7250,          # ~5,000 Shaheds (strait engagement; 5K cap)
        "intercept_cap": 4000,
        "intercept_rate": 0.550,   # short standoff → compressed intercept windows
        "wave_s":         43200,
        "n_arc":           10,
        "n_sm6":           14,     # less reaction time; fewer SM-6 shots per engagement
        "n_us_strikes_per_csg": 30,
        "csg_fleet": STRAIT_CSGS,   # 8 CSGs in column at strait entrance
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},
            {"name": "IRGCN Sea Drone",  "weight": 0.137},
            {"name": "Emad MRBM",        "weight": 0.058},
            {"name": "Zolfaghar SRBM",   "weight": 0.058},
            {"name": "Khalij Fars ASBM", "weight": 0.057},
        ],
    },
    "shore_based_defense": {
        "label": "Scenario L -- Shore-Based Layered Defense (THAAD + PAC-3 + Aegis)",
        "description": (
            "SITUATION: US pre-deploys shore-based ballistic missile defense assets to the "
            "Gulf region before hostilities — a real capability available as of 2024. "
            "THAAD batteries at UAE Al Dhafra AB, Saudi Arabia Prince Sultan AB, and Qatar "
            "Al Udeid AB (all confirmed by CENTCOM 2024 posture statement) add a high-altitude "
            "ballistic intercept tier. Patriot PAC-3 MSE batteries at Kuwait Ali Al Salem "
            "and Bahrain Isa AB cover the medium-altitude ballistic layer. Combined with "
            "Aegis afloat, this creates a genuine three-tier layered defense architecture.\n\n"
            "DEFENSIVE ARCHITECTURE:\n"
            "  TIER 1 — THAAD (Terminal High Altitude Area Defense): Engages ballistic "
            "  targets at 150–200 km altitude, providing 'above the atmosphere' kill above "
            "  AEGIS/SM-6 ceiling. THAAD's hit-to-kill kinetic interceptor has assessed "
            "  P(k) ~85% vs. short-range and medium-range ballistic missiles in non-"
            "  stressed (non-swarming) environment. Each AN/TPY-2 radar provides 1,000+ km "
            "  search range — detects Iranian MRBM launches from midpoint of Zagros range.\n"
            "  TIER 2 — Patriot PAC-3 MSE: Engages ballistic targets at 30–80 km altitude, "
            "  filling the gap between THAAD (high) and Aegis SM-6 (mid). PAC-3 MSE "
            "  provides active radar seeker with 'hit-to-kill' kinetic final intercept. "
            "  Assessed P(k) ~70–80% vs. Shahab-3/Emad class at this tier.\n"
            "  TIER 3 — Aegis SM-6/SM-2/ESSM: Unchanged from other scenarios.\n\n"
            "COMBINED EFFECT: The three-tier architecture creates shoot-look-shoot "
            "opportunities: if THAAD misses, PAC-3 takes a shot; if PAC-3 misses, SM-6 "
            "takes a shot. Combined P(k) rises from ~63% (Aegis alone) to ~85% (all tiers). "
            "Intercept capacity jumps from 4,000 to 6,000 — THAAD and Patriot add "
            "~2,000 additional intercept slots beyond the Aegis magazine. Same Iranian OOB "
            "as Scenario D (Realistic): 1,935 total.\n\n"
            "ASSESSMENT: Shore-based layered defense reduces breakthroughs from 713 "
            "(Realistic) to 301 — a 58% reduction in damage. This validates the strategic "
            "investment in THAAD regional deployment (FMS approval: Saudi Arabia $15B, "
            "UAE multiple systems per DSCA). The 301 remaining breakthroughs are almost "
            "entirely drones and sea-skimmers that defeat the ballistic intercept tiers.\n\n"
            "Sources: CENTCOM 2024 posture statement; DSCA THAAD Saudi FMS; Jane's DW 2024.\n\n"
            "1,935 total | ~1,634 intercepted | ~301 breakthrough (58% fewer than Scenario D)."
        ),
        "n_missiles":    7250,          # ~5,000 Shaheds (5K cap; layered defense scenario)
        "intercept_cap": 6000,     # THAAD + Patriot adds ~2,000 extra intercept slots
        "intercept_rate": 0.850,   # layered P(k): THAAD (~85% vs TBM) + Patriot + Aegis
        "wave_s":         86400,
        "n_arc":           10,
        "n_sm6":           20,     # Aegis not exhausted as much; SM-6 focused
        "n_us_strikes_per_csg": 30,
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},
            {"name": "IRGCN Sea Drone",  "weight": 0.137},
            {"name": "Emad MRBM",        "weight": 0.058},
            {"name": "Zolfaghar SRBM",   "weight": 0.058},
            {"name": "Khalij Fars ASBM", "weight": 0.057},
        ],
    },

    # ── Scenario N — Cave/Tunnel Network ──────────────────────────────────
    # Iran disperses launches across 25 mountain cave complexes (Zagros / Alborz /
    # eastern highlands). Each site needs only 2 hits to neutralize — but 25 targets
    # dilutes the US strike budget far more than the standard 12-site coastal network.
    # ------------------------------------------------------------------
    # SCENARIO O — Depleted Arsenal: 8% Inventory, Drone-Wave First
    # ------------------------------------------------------------------
    # Iran has suffered sustained attrition — airbase strikes, TLAM waves,
    # special operations, and logistics interdiction — leaving only ~8% of
    # its pre-conflict inventory intact.  580 total munitions remain.
    # Despite the degraded inventory, Iran still executes its phased
    # drone-first doctrine: drones exhaust CIWS/SM-6 before the residual
    # ballistic/cruise salvo arrives.
    "depleted_drone_first": {
        "label": "Scenario O -- Depleted Arsenal: 8% Inventory, Drone-First Phase (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":   ALL_SITES,    # 37 sites: 12 coastal + 25 cave/tunnel complexes
        "n_missiles":     580,          # 8% of 7,250 realistic baseline
        "intercept_cap":  400,
        "intercept_rate": 0.520,        # drone-first hurts, but small salvo means less saturation
        "wave_s":         14400,        # 4-hour campaign window
        "phase1_end_s":    7200,        # Phase 1: T+0 to T+2h — drones only
        "phase2_start_s":  7200,        # Phase 2: T+2h onward — missiles
        "phase2_dur_s":    7200,
        "n_arc":           10,
        "n_sm6":           20,          # defenses not exhausted — full SM-6 available
        "n_us_strikes_per_csg": 15,     # 15 × 8 = 120 total; fewer needed against depleted sites
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.580},   # ~336/580 drones
            {"name": "IRGCN Sea Drone",  "weight": 0.120},   # ~70/580 sea drones
            {"name": "Emad MRBM",        "weight": 0.100},   # ~58/580
            {"name": "Zolfaghar SRBM",   "weight": 0.100},   # ~58/580
            {"name": "Khalij Fars ASBM", "weight": 0.100},   # ~58/580
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO P — Depleted Arsenal: 8% Inventory, Drone-First, Coastal Sites
    # ------------------------------------------------------------------
    # Same depleted-inventory premise as Scenario O but launching from the
    # standard 12 coastal sites instead of cave complexes.  Useful as a
    # direct comparison: coastal sites are easier for US/IAF to strike
    # (TLAMs can destroy them), so site suppression is more effective here.
    "depleted_coastal": {
        "label": "Scenario P -- Depleted Arsenal: 8% Inventory, Drone-First, All Sites (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":   ALL_SITES,    # 37 sites: 12 coastal + 25 cave/tunnel complexes
        "n_missiles":     580,          # 8% of 7,250 realistic baseline
        "intercept_cap":  400,
        "intercept_rate": 0.530,        # slightly better than caves — sites suppressed faster
        "wave_s":         14400,
        "phase1_end_s":    7200,
        "phase2_start_s":  7200,
        "phase2_dur_s":    7200,
        "n_arc":           10,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 15,
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.580},
            {"name": "IRGCN Sea Drone",  "weight": 0.120},
            {"name": "Emad MRBM",        "weight": 0.100},
            {"name": "Zolfaghar SRBM",   "weight": 0.100},
            {"name": "Khalij Fars ASBM", "weight": 0.100},
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO Q — Depleted Arsenal: Drone Capacity Split Gulf / Israel
    # ------------------------------------------------------------------
    # Same 8% inventory (580 total).  Iran simultaneously retaliates against
    # Israel, diverting ~50% of its Shahed-136 long-range drones (~168 units)
    # on the Israel vector (via Iraqi/Syrian airspace at ~2,200 km range).
    # IRGCN sea drones cannot reach Israel — they remain on the Gulf axis.
    # Ballistic/cruise missiles are all targeted at the CSG fleet.
    # Gulf-facing salvo: 168 Shaheds + 70 sea drones + 174 ballistic/cruise
    # = 412 total munitions.  Drone wave is smaller → less CIWS saturation
    # before the ballistic follow-on, but defenses are correspondingly less
    # depleted when missiles arrive.
    "depleted_israel_split": {
        "label": "Scenario Q -- Depleted Arsenal: Drone Waves Alternating Gulf/Israel (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         ALL_SITES,    # 37 sites: 12 coastal + 25 cave/tunnel
        "israel_drone_alternation": 4,        # phase-1 split into 4 sub-windows; odd → Israel
        "n_missiles":     580,                # full 8% inventory; alternation removes ~50% Shaheds from Gulf
        "intercept_cap":  300,
        "intercept_rate": 0.510,
        "wave_s":         14400,
        "phase1_end_s":    7200,
        "phase2_start_s":  7200,
        "phase2_dur_s":    7200,
        "n_arc":           10,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 15,
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.580},   # full weight — alternation loop diverts ~50% in-sim
            {"name": "IRGCN Sea Drone",  "weight": 0.120},   # stays on Gulf axis (can't reach Israel)
            {"name": "Emad MRBM",        "weight": 0.100},
            {"name": "Zolfaghar SRBM",   "weight": 0.100},
            {"name": "Khalij Fars ASBM", "weight": 0.100},
        ],
    },

    # ------------------------------------------------------------------
    # US-WINS SCENARIOS (R–V)
    # Each models a condition under which US/coalition forces defeat the Iranian
    # salvo before it inflicts mission-killing damage on the CSG fleet.
    # P_win is estimated from a Poisson breakthrough model:
    #   λ = expected breakthroughs per CSG = total_btk / 8_CSGs
    #   P_win ≈ 1 − P(any CSG receives ≥ 10 hits) where 10 hits = mission kill
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Preemptive US strike degrades ~85 % of Iran's launch infrastructure
    # (inland missile depots + cave complexes) before the salvo is fired.
    # Only ~280 missiles survive to launch from surviving coastal sites.
    # The small salvo is saturated by Aegis even without reload.
    # λ ≈ 4.4 breakthroughs/CSG → P_win ≈ 94 %
    # ------------------------------------------------------------------
    "us_win_preemption": {
        "label": "Scenario R -- US Wins: Preemptive Strike Success [P_win ≈ 94%] (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         INLAND_AND_CAVES,   # US strikes deplete all inland + cave sites
        "n_missiles":           280,                # only ~15% of full inventory survives
        "intercept_cap":        280,                # Aegis can absorb entire surviving salvo
        "intercept_rate":       0.890,              # very high — small salvo, full magazines
        "wave_s":               7200,               # compressed 2-hour window (disrupted C2)
        "n_arc":                8,
        "n_sm6":                20,
        "n_us_strikes_per_csg": 25,                 # heavy preemptive strike package
        "munitions": [
            # Only hardened ballistic missiles survive preemptive air strikes
            {"name": "Emad MRBM",        "weight": 0.420},   # underground bunkers partially survive
            {"name": "Zolfaghar SRBM",   "weight": 0.380},   # mobile TELs that escaped strike
            {"name": "Shahab-3 MRBM",    "weight": 0.200},   # legacy — some survive in dispersed sites
        ],
    },

    # ------------------------------------------------------------------
    # US full-spectrum EW (EA-18G Growler + jamming pods + cyber) blinds
    # Iranian radar/datalink nets.  Guidance-dependent systems (Noor, Fateh,
    # all drone datalinks) miss or self-destruct.  Only unguided / inertial
    # ballistic rounds remain effective — and those are far fewer.
    # λ ≈ 5.2 breakthroughs/CSG → P_win ≈ 88 %
    # ------------------------------------------------------------------
    "us_win_ew_dominance": {
        "label": "Scenario S -- US Wins: EW / Cyber Dominance [P_win ≈ 88%] (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         ALL_SITES,
        "n_missiles":           450,                # precision-guided rounds denied; only ballistic survive
        "intercept_cap":        450,
        "intercept_rate":       0.910,              # jammed seekers massively reduce effective Pk for Iran
        "wave_s":               21600,
        "n_arc":                10,
        "n_sm6":                20,
        "n_us_strikes_per_csg": 20,
        "munitions": [
            # Guidance-dependent systems largely neutralized by jamming
            {"name": "Shahab-3 MRBM",    "weight": 0.380},   # inertial only — not jammed but inaccurate
            {"name": "Emad MRBM",        "weight": 0.320},   # inertial fallback when radar link jammed
            {"name": "Zolfaghar SRBM",   "weight": 0.200},   # some GPS-aided — degraded but not zeroed
            {"name": "Fateh-110 SRBM",   "weight": 0.100},   # optical seeker partially resistant
        ],
    },

    # ------------------------------------------------------------------
    # Full coalition umbrella: Israel Iron Dome/David's Sling, Saudi Patriot,
    # UAE THAAD, Bahrain Patriot, plus US Aegis — five overlapping intercept
    # layers.  Even a large salvo is defeated by sheer intercept capacity.
    # λ ≈ 5.8 breakthroughs/CSG → P_win ≈ 83 %
    # ------------------------------------------------------------------
    "us_win_allied_umbrella": {
        "label": "Scenario T -- US Wins: Full Allied Missile-Defence Umbrella [P_win ≈ 83%] (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         ALL_SITES,
        "n_missiles":           550,                # Iran launches full coastal salvo
        "intercept_cap":        600,                # allied battery cap stacked on top of Aegis
        "intercept_rate":       0.920,              # five-layer intercept; even HGVs targeted by THAAD
        "wave_s":               28800,
        "n_arc":                10,
        "n_sm6":                20,
        "n_us_strikes_per_csg": 18,
        "munitions": [
            # Full Iranian coastal mix — allied umbrella handles everything
            {"name": "Shahed-136",       "weight": 0.380},   # Iron Dome + Patriot + CIWS
            {"name": "Noor ASCM",        "weight": 0.180},   # SM-6 + SM-2 at range
            {"name": "Emad MRBM",        "weight": 0.140},   # THAAD (UAE) + SM-6
            {"name": "Zolfaghar SRBM",   "weight": 0.140},   # Patriot PAC-3 + SM-6
            {"name": "Khalij Fars ASBM", "weight": 0.100},   # SM-6 + David's Sling
            {"name": "IRGCN Sea Drone",  "weight": 0.060},   # CIWS + deck guns
        ],
    },

    # ------------------------------------------------------------------
    # US SEAD/DEAD strikes plus cyberattack disrupt Iranian command-and-control.
    # Launches are fragmented (no coordinated salvo timing), magazines reload
    # between sub-salvos, and Aegis intercepts each small packet individually.
    # Even 900 total missiles fired never arrive simultaneously.
    # λ ≈ 7.3 breakthroughs/CSG → P_win ≈ 71 %
    # ------------------------------------------------------------------
    "us_win_c2_disrupted": {
        "label": "Scenario U -- US Wins: Iranian C2 / IADS Disrupted [P_win ≈ 71%] (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         ALL_SITES,
        "n_missiles":           900,                # all missiles fired but fragmented timing
        "intercept_cap":        900,                # Aegis can reload between fragmented sub-waves
        "intercept_rate":       0.930,              # each small packet absorbed before next arrives
        "wave_s":               86400,              # 24-hour degraded window — no simultaneous saturation
        "n_arc":                10,
        "n_sm6":                20,
        "n_us_strikes_per_csg": 20,
        "munitions": [
            # Full Iranian mix but no salvo coordination benefit
            {"name": "Shahed-136",       "weight": 0.440},
            {"name": "Noor ASCM",        "weight": 0.160},
            {"name": "Emad MRBM",        "weight": 0.120},
            {"name": "Zolfaghar SRBM",   "weight": 0.120},
            {"name": "Khalij Fars ASBM", "weight": 0.100},
            {"name": "IRGCN Sea Drone",  "weight": 0.060},
        ],
    },

    # ------------------------------------------------------------------
    # Iran fought a full prior war (e.g., against Israel) and expended
    # ~80 % of its precision inventory.  Only legacy Shahab-3 + surviving
    # Shahed drones remain in large numbers; HGVs and Fattah are expended.
    # Degraded salvo is large by count but low in lethality per round.
    # λ ≈ 8.7 breakthroughs/CSG → P_win ≈ 65 %
    # ------------------------------------------------------------------
    "us_win_arsenal_attrition": {
        "label": "Scenario V -- US Wins: Iranian Arsenal Attrited by Prior Conflict [P_win ≈ 65%] (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         ALL_SITES,
        "n_missiles":           750,                # large count but legacy low-lethality rounds
        "intercept_cap":        750,
        "intercept_rate":       0.910,              # legacy rounds easier to intercept (no HGV/maneuvering)
        "wave_s":               43200,
        "n_arc":                10,
        "n_sm6":                20,
        "n_us_strikes_per_csg": 16,
        "munitions": [
            # Only attrition survivors: legacy Shahed + old ballistic
            {"name": "Shahed-136",       "weight": 0.580},   # large stock survives — cheap + numerous
            {"name": "Shahab-3 MRBM",    "weight": 0.250},   # legacy inaccurate; Fattah/Emad expended
            {"name": "Zolfaghar SRBM",   "weight": 0.120},   # some mobile TELs survived prior war
            {"name": "IRGCN Sea Drone",  "weight": 0.050},   # coastal boats survived — short-range only
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO Z — 1% Pre-Crisis Inventory: Drone Probe → ISR Assessment Lull → Precision Follow-On
    # ------------------------------------------------------------------
    # Iran has been reduced to approximately 1% of its pre-crisis armament through
    # sustained US/coalition strikes, prior conflict attrition, and logistics
    # interdiction.  Pre-crisis baseline: ~80,000 Shaheds + ~5,000 ballistic missiles
    # = ~85,000 total.  1% = ~850 munitions.  After the 50% pre-emptive strike
    # modelled in other scenarios, only ~75 munitions remain operationally ready.
    #
    # DOCTRINE: At this extreme depletion level Iran shifts from mass saturation
    # to deliberate, economical strikes.  Phase 1 (T+0→T+60 min) launches a small
    # drone-and-sea-drone probe designed to trigger Aegis engagement, reveal CSG
    # positions, and inflict whatever first-wave damage is achievable.  A 60-minute
    # ISR assessment lull (T+60→T+120 min) follows: space-based EO/IR imagery
    # (commercial or Chinese satellite constellation), signals intercepts, and
    # IRGC reconnaissance aircraft assess which CSGs remain fully operational.
    # Phase 2 (T+120→T+180 min) then fires Iran's last ~25 ballistic and cruise
    # missiles preferentially at the assessed-undamaged CSGs, maximising strategic
    # impact from its final remaining inventory.
    #
    # NOTE ON TARGETING: The simulation distributes phase-2 missiles randomly across
    # all CSGs as a computational simplification.  In reality, Iran's 60-minute ISR
    # window would re-cue surviving TELs against the highest-value undamaged targets.
    # The breakthrough count and damage distribution should be interpreted as
    # "best achievable" rather than "worst case."
    #
    # λ ≈ 1.2 breakthroughs/CSG → P_win ≈ 99%+ (fleet essentially intact)
    # ------------------------------------------------------------------
    "one_percent_probe": {
        "label": "Scenario Z -- 1% Inventory: Drone Probe → 60-min ISR Lull → Precision Follow-On (8 CSGs)",
        "description": (
            "SITUATION: Iran has been reduced to approximately 1% of pre-crisis armament "
            "through a combination of sustained US/IAF pre-emptive strikes, prior conflict "
            "attrition against Israel, and logistical interdiction of missile production and "
            "storage facilities. Pre-crisis inventory: ~80,000 Shaheds + ~5,000 ballistic missiles "
            "≈ 85,000 total munitions. Post-attrition availability: ~75 munitions operationally "
            "ready — a 99%+ reduction from peak. Iran's strategic decision at this depletion "
            "level is not 'whether to strike' but 'how to make the last 75 rounds count.'\n\n"
            "PHASE 1 — DRONE PROBE (T+0 to T+60 min): Iran launches 45 Shahed-136 loitering "
            "munitions and 10 IRGCN surface drones — its cheapest and most numerous surviving "
            "assets — in a calculated reconnaissance-in-force. The purpose is threefold:\n"
            "  1. DAMAGE: At least a fraction of the drones will penetrate CIWS given the "
            "     element of surprise in a limited engagement.  Even 3–5 hits deliver "
            "     meaningful topside and electronic damage.\n"
            "  2. POSITION CONFIRMATION: Drone approach vectors reveal current CSG positions "
            "     to within ±5 km — critical for cueing TEL re-targeting of the follow-on "
            "     ballistic missiles which have pre-programmed aim points.\n"
            "  3. MAGAZINE PROBING: Aegis CIWS engagement reveals approximate remaining RAM/"
            "     SeaRAM loads by observing engagement duration and terminal defense "
            "     intervals.  SIGINT on radar emissions allows assessment of which CSGs "
            "     activated SM-6/SM-2 (and thus partially depleted their VLS load).\n\n"
            "ISR ASSESSMENT LULL (T+60 to T+120 min): A deliberate 60-minute pause follows "
            "the drone wave. Iranian space-based or partner-nation (Chinese/Russian) EO/IR "
            "satellite imagery passes confirm: (a) which CSGs sustained visible fire, smoke, "
            "or flight-deck damage; (b) which CSGs executed evasive maneuver (implying "
            "fully-operational control); (c) current position updates for TEL re-cueing. "
            "SIGINT (IRGC ELINT aircraft outside engagement range) monitors carrier air wing "
            "radio procedures — active CAP tasking indicates a fully-operational carrier. "
            "This intelligence is fused into a ranked target list: undamaged CVNs and escorts "
            "with confirmed flight operations receive the highest priority.\n\n"
            "PHASE 2 — PRECISION FOLLOW-ON (T+120 to T+180 min): Iran fires its remaining "
            "~20 ballistic and cruise missiles — the final operational inventory — from "
            "surviving TELs at the assessed highest-value surviving targets. Munition mix:\n"
            "  - 10 × Emad MRBM (maneuvering RV, 750 kg warhead): targeted at CVN flight decks "
            "    confirmed operational by phase-1 ISR; maneuvering terminal reduces SM-6 Pk "
            "    from ~90% to ~45%.\n"
            "  - 5 × Khalij Fars ASBM (EO/IR terminal seeker, 300 km range): the highest-Pk "
            "    carrier killers in the inventory; ISR-updated GPS coordinates loaded post-lull.\n"
            "  - 5 × Zolfaghar SRBM (GPS precision, <10 m CEP): targets undamaged escort DDGs "
            "    whose CIWS actively engaged Phase 1 drones — identified by radar emission signature.\n\n"
            "US RESPONSE: With only 75 total incoming munitions, Aegis operates at full "
            "efficiency. CIWS magazines are not stressed by the 55-drone Phase 1 wave. "
            "When Phase 2 missiles arrive, SM-6 has full magazine depth, full radar "
            "bandwidth, and 60 minutes of warning from Phase 1 engagement to warm up "
            "ballistic defense modes. Intercept rate rises to 85%+ — significantly higher "
            "than any high-volume scenario.\n\n"
            "ASSESSMENT: Iran's last 75 rounds produce ~13 breakthroughs distributed across "
            "8 CSGs — approximately 1.6 hits per CSG on average, insufficient for mission kills. "
            "At most 1–2 escort DDGs suffer moderate damage. All CVNs remain fully "
            "operational. The fleet retains complete air wing capacity for counter-strike "
            "operations. Iran has no follow-on salvo capacity; its launch network is "
            "systematically eliminated by US counterstrikes during and after Phase 2.\n\n"
            "STRATEGIC IMPLICATION: This scenario illustrates the decisive asymmetry when "
            "pre-emptive degradation succeeds — Iran retains the political will to strike "
            "but lacks the inventory to achieve operationally-relevant results. Compare to "
            "Scenario D (Realistic, 7,250 total, ~3,045 breakthrough): the difference "
            "between fleet destruction and fleet survival is almost entirely a function of "
            "whether Iran was allowed to preserve its inventory pre-conflict.\n\n"
            "75 total (45 drones + 10 sea drones + 20 ballistic/cruise) | "
            "~62 intercepted | ~13 breakthrough — fleet intact, 1–2 escorts lightly damaged."
        ),
        "custom_sites":         ALL_SITES,          # surviving dispersed sites from sustained attrition
        "n_missiles":           75,                  # 1% of pre-crisis ~7,250 post-preemption baseline
        "intercept_cap":        75,                  # Aegis easily absorbs entire salvo
        "intercept_rate":       0.825,               # very high — small salvo, full magazines, full bandwidth
        "wave_s":               18000,               # 5-hour scenario envelope (covers lull + follow-on)
        "phase1_end_s":          3600,               # Phase 1: T+0 to T+60 min — drone probe
        "phase2_start_s":        7200,               # lull gap: T+60 to T+120 min — ISR assessment
        "phase2_dur_s":          3600,               # Phase 2: T+120 to T+180 min — precision missiles
        "n_arc":                    14,              # good resolution for both slow drones and steep ballistics
        "n_sm6":                    24,              # full magazines — Aegis not depleted at this scale
        "n_us_strikes_per_csg":     10,              # 10 × 8 = 80 total strikes; destroys all remaining sites
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.600},   # 45/75 — Phase 1 drone probe
            {"name": "IRGCN Sea Drone",  "weight": 0.133},   # 10/75 — Phase 1 surface probe
            {"name": "Emad MRBM",        "weight": 0.133},   # 10/75 — Phase 2 precision follow-on
            {"name": "Khalij Fars ASBM", "weight": 0.067},   #  5/75 — Phase 2 carrier-targeted
            {"name": "Zolfaghar SRBM",   "weight": 0.067},   #  5/75 — Phase 2 escort-targeted
        ],
    },

    # ------------------------------------------------------------------
    # SCENARIO AA — 1% Inventory + 10 Secured Fattah-2 HGVs
    # ------------------------------------------------------------------
    # Same 1% pre-crisis depletion as one_percent_probe, but Iran has succeeded
    # in protecting 10 Fattah-2 hypersonic glide vehicles from US/IAF strikes.
    # The Fattah-2 are stored in Zagros Mountain deep-tunnel complexes that require
    # GBU-57A/B Massive Ordnance Penetrator (MOP) to destroy — a 13,600 kg
    # bunker-busting bomb carried only by the B-2 Spirit stealth bomber.  With
    # US B-2 sorties not committed to the Gulf campaign, these 10 rounds survive
    # intact and constitute Iran's most lethal residual capability by a wide margin.
    #
    # INTERCEPT MATHEMATICS:
    #   Fattah-2 intercept_prob_override = 0.03 → ~9.7 of 10 HGVs break through
    #   Each Fattah-2 breakthrough: $420M damage, ~110 KIA, ~260 WIA
    #   10 × 97% BT rate → ~10 hull-kills or catastrophic mission kills
    #   All other 65 munitions: ~83–80% intercept rate → ~5–6 breakthrough
    #   Total ~25 breakthroughs, but ~10 of them are Fattah-2 — the fleet-killers.
    #
    # This is the scenario that shows why HGV proliferation is the most dangerous
    # qualitative shift in Iranian capability — not raw inventory numbers.
    # ------------------------------------------------------------------
    "one_percent_fatah2": {
        "label": "Scenario AA -- 1% Inventory + 10 Secured Fattah-2 HGVs: Drone Probe → ISR Lull → HGV Strike (8 CSGs)",
        "description": (
            "SITUATION: Iran has been reduced to 1% of pre-crisis armament through sustained "
            "US/IAF strikes and prior-conflict attrition — identical depletion context to "
            "Scenario Z. However, Iran succeeded in protecting 10 Fattah-2 hypersonic glide "
            "vehicles in hardened deep-tunnel storage at Zagros Mountain complexes. These "
            "facilities, derived from the Fordow enrichment model and subsequently expanded "
            "under the IRGC Missile Corps hardening program, are buried 80–100 m below granite "
            "overburden. Standard TLAM Block IV and JASSM-ER lack the penetration depth to "
            "destroy them. Destruction requires the GBU-57A/B Massive Ordnance Penetrator "
            "(30 kJ/m³ penetration, 13,600 kg, 6 m tungsten tip) — a weapon exclusively "
            "carried by the B-2 Spirit. With B-2 sorties not allocated to the Gulf campaign "
            "in this scenario, all 10 Fattah-2 TELs survive intact.\n\n"
            "FATTAH-2 THREAT PROFILE (verified capabilities as of March 2026):\n"
            "  - Speed: Mach 10–12 assessed (Iran claims Mach 15; Hudson Institute 2026)\n"
            "  - Range: ~1,500 km; covers all 8 CSG positions from Zagros launch sites\n"
            "  - Maneuver: pitch AND yaw during glide phase — SM-6 Block IA cannot solve "
            "    the impact-point prediction problem; intercept probability ~3%\n"
            "  - Trajectory: depressed to 75 km ceiling during glide; below SM-3 envelope "
            "    and at the edge of SM-6 Block IA endo-atmospheric ceiling\n"
            "  - Warhead: ~580 kg maneuvering reentry vehicle with shaped-charge final stage; "
            "    kinetic energy at Mach 10 impact is equivalent to a 1,500 kg conventional bomb\n"
            "  - Guidance: terminal INS/GPS with star-tracker mid-course update; "
            "    EW-resistant (no radar-homing link to jam)\n"
            "  - First combat use: March 2026 (Iran International, corroborated by JINSA Feb 2026)\n\n"
            "PHASE 1 — DRONE PROBE (T+0 to T+60 min): 45 Shahed-136 and 10 IRGCN surface "
            "drones execute an identical reconnaissance-in-force to Scenario Z: confirm CSG "
            "positions, probe Aegis engagement chains, assess CIWS load status by SIGINT "
            "analysis of radar emission intervals. The drone probe is also a deliberate "
            "deception: US fleet commanders observing a tiny 55-drone salvo assume they face "
            "a Scenario Z-type probe — not the prelude to a Fattah-2 strike. This cognitive "
            "framing may delay the transition to SM-6 Block IA BMD mode.\n\n"
            "ISR ASSESSMENT LULL (T+60 to T+120 min): The 60-minute gap serves a second "
            "purpose beyond damage assessment: Fattah-2 TEL crews receive final target "
            "coordinates updated from Phase 1 position fixes. The Fattah-2's INS/GPS "
            "system is uploaded with the measured (not predicted) CSG position from Phase 1 "
            "drone terminal-approach telemetry. CSGs that maneuvered evasively in Phase 1 "
            "are re-acquired at their new positions. The 10 TELs deploy to dispersed launch "
            "positions during this window, maximising separation to complicate any reactive "
            "US counter-battery strike.\n\n"
            "PHASE 2 — FATTAH-2 SALVO + CONVENTIONAL FOLLOW-ON (T+120 to T+180 min): "
            "All 10 Fattah-2 HGVs launch from dispersed Zagros TEL positions within a "
            "5-minute compressed window — too fast for US strike aircraft to engage TELs "
            "after launch detection. Simultaneously, Iran fires its remaining 10 conventional "
            "precision missiles (5× Emad MRBM, 5× Khalij Fars ASBM) targeting the same "
            "CSGs prioritised by Phase 1 ISR. The conventional layer is designed to consume "
            "any remaining SM-6 rounds that might otherwise achieve a lucky intercept on "
            "a Fattah-2 — effectively using $800k Emad rounds to 'escort' the $4M HGVs.\n\n"
            "INTERCEPT MATHEMATICS:\n"
            "  Fattah-2 P(k) per SM-6 Block IA: ~3% (pitch+yaw maneuvering unsolvable)\n"
            "  Expected Fattah-2 breakthroughs: 10 × 97% = ~9.7 → 9–10 HGV hits\n"
            "  Each Fattah-2 hit: $420M ship damage, ~110 KIA, ~260 WIA\n"
            "  10 Fattah-2 hits: ~$4.2B damage, ~1,100 KIA — fleet-killing outcome\n"
            "  Conventional follow-on adds ~5–6 more breakthroughs\n"
            "  Total breakthrough: ~25 (vs ~13 in Scenario Z) — but lethality is "
            "  disproportionately higher because the HGV hits dominate the damage calculus.\n\n"
            "US COUNTERMEASURES (LIMITED):\n"
            "  SM-3 Block IIA (if present): designed for midcourse intercept at 500+ km; "
            "  not deployed in this Gulf scenario. No ship in this force has SM-3.\n"
            "  SM-6 Block IA: terminal intercept only; ~3% vs Fattah-2; math says "
            "  firing 20 SM-6 rounds at a single Fattah-2 gives only P(k) = 1−0.97²⁰ = 45%.\n"
            "  SM-6 Block IB (hypersonic intercept variant): in development as of 2026; "
            "  not operationally deployed in sufficient numbers for this scenario.\n\n"
            "ASSESSMENT: Despite Iran's near-total inventory depletion, the 10 secured "
            "Fattah-2 HGVs transform a nuisance-level raid (Scenario Z, ~13 breakthrough, "
            "fleet intact) into a catastrophic engagement (~25 breakthrough, 2–3 CVNs "
            "mission-killed, 5–6 escort DDGs destroyed). The strategic lesson: HGV "
            "proliferation renders the 'degrade the inventory' pre-emptive strategy "
            "insufficient unless B-2/MOP assets are specifically committed to destroying "
            "hardened HGV storage. A 1% inventory scenario with 10 HGVs is more dangerous "
            "than a 100% inventory scenario with zero HGVs.\n\n"
            "75 total (45 drones + 10 sea drones + 10 Fattah-2 HGV + 10 ballistic/cruise) | "
            "~50 intercepted | ~25 breakthrough — 9–10 HGV strikes, 2–3 CVNs mission-killed."
        ),
        "custom_sites":         CAVE_SITES,         # Fattah-2 stored in deep-tunnel Zagros cave complexes
        "site_hits_to_destroy": 8,                  # requires MOP-equivalent penetration; TLAM/JASSM insufficient
        "n_missiles":           75,                  # 1% of pre-crisis ~7,250 post-preemption baseline
        "intercept_cap":        75,
        "intercept_rate":       0.665,               # ~50 intercepted; Fattah-2 overrides drive HGV breakthroughs
        "wave_s":               18000,               # 5-hour scenario envelope
        "phase1_end_s":          3600,               # Phase 1: T+0 to T+60 min — drone probe
        "phase2_start_s":        7200,               # lull: T+60 to T+120 min — ISR assessment + TEL repositioning
        "phase2_dur_s":          3600,               # Phase 2: T+120 to T+180 min — HGV + conventional follow-on
        "n_arc":                    14,
        "n_sm6":                    24,              # full magazines available; small salvo does not deplete Aegis
        "n_us_strikes_per_csg":     10,              # 10 × 8 = 80 strikes; TLAM/JASSM cannot penetrate HGV tunnels
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.600},   # 45/75 — Phase 1 drone probe
            {"name": "IRGCN Sea Drone",  "weight": 0.133},   # 10/75 — Phase 1 surface probe
            {"name": "Fattah-2 HGV",    "weight": 0.133},   # 10/75 — Phase 2 near-uninterceptable HGV salvo
            {"name": "Emad MRBM",        "weight": 0.067},   #  5/75 — Phase 2 conventional escort layer
            {"name": "Khalij Fars ASBM", "weight": 0.067},   #  5/75 — Phase 2 carrier-targeted ASBM
        ],
    },

    # ------------------------------------------------------------------
    # Models the realistic challenge of attacking hardened tunnel/cave infrastructure
    # that cannot be destroyed by TLAM/JASSM without GBU-57 MOP (B-2 only).
    # Assumes ~5,000 Shahed cap + Emad/Zolfaghar from cave complexes.
    "caves": {
        "label": "Scenario N -- Cave/Tunnel Network: 25 Dispersed Sites, 2-Hit Destruction (8 CSGs)",
        "description": "",   # overridden dynamically
        "custom_sites":         CAVE_SITES,   # replace the 12 coastal sites
        "site_hits_to_destroy": 2,            # caves collapse with 2 precision hits
        "n_missiles":    7250,
        "intercept_cap": 4000,
        "intercept_rate": 0.580,   # same as realistic — Aegis unchanged
        "iran_detection_launch": True,
        "iran_launch_window_s":  1800,        # simultaneous launch from all caves
        "wave_s":         43200,
        "n_arc":           14,
        "n_sm6":           20,
        "n_us_strikes_per_csg": 20,           # 20 × 8 = 160 total strikes across 25 targets
        "munitions": [
            {"name": "Shahed-136",       "weight": 0.690},
            {"name": "IRGCN Sea Drone",  "weight": 0.137},
            {"name": "Emad MRBM",        "weight": 0.058},
            {"name": "Zolfaghar SRBM",   "weight": 0.058},
            {"name": "Khalij Fars ASBM", "weight": 0.057},
        ],
    },
}

# ============================================================
# MATH / GEO HELPERS
# ============================================================

def haversine_km(lon1, lat1, lon2, lat2):
    """Great-circle distance using the Haversine formula and _R_EARTH_KM."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * _R_EARTH_KM * math.asin(math.sqrt(a))


def lerp(a, b, t):
    return a + t * (b - a)


def cep_circle_kml(lon, lat, radius_m, color_kml, name, begin_s, end_s, n_pts=36):
    """KML Polygon approximating the CEP uncertainty circle for a ballistic missile in flight.

    Visible from begin_s (launch) to end_s (impact or intercept) via TimeSpan.
    color_kml: AABBGGRR string.  radius_m: CEP radius in metres.
    """
    bbggrr        = color_kml[-6:] if len(color_kml) >= 6 else "ffffff"
    fill_color    = f"33{bbggrr}"   # ~20% opacity fill
    outline_color = f"cc{bbggrr}"   # 80% opacity outline
    lat_per_m = 1.0 / 111_000.0
    lon_per_m = 1.0 / (111_000.0 * math.cos(math.radians(lat)))
    coords = []
    for k in range(n_pts + 1):
        angle  = 2.0 * math.pi * k / n_pts
        coords.append(f"{lon + radius_m * math.sin(angle) * lon_per_m:.6f},"
                       f"{lat + radius_m * math.cos(angle) * lat_per_m:.6f},0")
    timespan = (f"<TimeSpan><begin>{fmt_time(sim_time(begin_s))}</begin>"
                f"<end>{fmt_time(sim_time(end_s))}</end></TimeSpan>")
    return (
        f'      <Placemark><name>{name}</name>\n'
        f'        {timespan}\n'
        f'        <Style>\n'
        f'          <LineStyle><color>{outline_color}</color><width>1</width></LineStyle>\n'
        f'          <PolyStyle><color>{fill_color}</color><fill>1</fill><outline>1</outline></PolyStyle>\n'
        f'        </Style>\n'
        f'        <Polygon><altitudeMode>clampToGround</altitudeMode>'
        f'<outerBoundaryIs><LinearRing><coordinates>{" ".join(coords)}</coordinates>'
        f'</LinearRing></outerBoundaryIs></Polygon>\n'
        f'      </Placemark>\n'
    )


def arc_points(lon1, lat1, lon2, lat2, peak_alt_m, n, sea_skim):
    """
    Return n+1 (lon, lat, alt_m) waypoints along the trajectory.

    Horizontal path — great-circle interpolation (gc_interp) replaces the
    previous linear lat/lon lerp, which traced a rhumb line and deviated up
    to ~50 km from the correct great-circle path at the midpoint of a 500 km
    trajectory.

    Vertical profile:
      Ballistic / cruise (sea_skim=False):
        Parabolic arc: alt = peak_alt_m × 4t(1-t), clamped to ≥ 10 m.
        Reaches peak_alt_m exactly at the midpoint (t = 0.5).

      Sea-skimming (sea_skim=True):
        Launch ramp: alt rises from 0 to peak_alt_m over the first 8 % of
          flight (simulating boost phase leaving the launcher).
        Cruise: constant peak_alt_m from t = 0.08 to t = 0.92.
        Terminal: alt descends back to ~1/3 peak over the last 8 % of flight
          (pop-down before impact seeker lock-on).
        Minimum altitude enforced at 0.5 m (surface vessels) / 5 m (airborne).
        Replaces the old `peak_alt_m × (1 + 0.5 × sin(πt))` formula which
        incorrectly raised altitude to 1.5 × peak at mid-flight.
    """
    pts = []
    for i in range(n + 1):
        t = i / n
        lon, lat = gc_interp(lon1, lat1, lon2, lat2, t)
        if sea_skim:
            # Surface / sea-skimming: launch ramp → cruise → terminal descent
            floor_m = 0.5 if peak_alt_m <= 2.0 else 5.0
            if t <= 0.08:
                alt = max(floor_m, peak_alt_m * (t / 0.08))
            elif t >= 0.92:
                term_frac = (t - 0.92) / 0.08
                alt = max(floor_m, peak_alt_m * (1.0 - 0.65 * term_frac))
            else:
                alt = max(floor_m, peak_alt_m)
        else:
            alt = max(10.0, peak_alt_m * 4 * t * (1 - t))
        pts.append((lon, lat, alt))
    return pts


def coords2(p1, p2):
    return (f"{p1[0]:.6f},{p1[1]:.6f},{p1[2]:.1f} "
            f"{p2[0]:.6f},{p2[1]:.6f},{p2[2]:.1f}")


def circle_ring(clon, clat, radius_km, n=72):
    """
    Return KML coordinate string for a great-circle ring of radius_km
    centred at (clon, clat).  Uses destination_point() so each vertex is
    placed on the sphere rather than on a flat-earth approximation.
    72 sides gives a visually smooth circle; vertex error < 0.04 %.
    """
    pts = []
    for i in range(n + 1):
        bearing = 360.0 * i / n
        lo, la  = destination_point(clon, clat, bearing, radius_km)
        pts.append((lo, la))
    return " ".join(f"{lo:.6f},{la:.6f},0" for lo, la in pts)


def weighted_choice(items, rng):
    total = sum(m["weight"] for m in items)
    r, cumsum = rng.random() * total, 0.0
    for item in items:
        cumsum += item["weight"]
        if r <= cumsum:
            return item
    return items[-1]


def safe_id(name):
    return ("mun_" + name.lower()
            .replace(" ", "_").replace("-", "_")
            .replace("/", "_").replace("(", "").replace(")", ""))


def _kml_to_css(kml_hex):
    """Convert 8-char AABBGGRR KML colour to CSS #RRGGBB."""
    return f"#{kml_hex[6:8]}{kml_hex[4:6]}{kml_hex[2:4]}"


# ── Project-wide HTML popup colour palette ────────────────────────────────────
# Background: pure black (#000000).
# Accent colours (titles, borders, status indicators) stay vivid for clarity.
# All prose text uses white or shades of light grey only.
_C_ACTIVE      = "#00dd66"   # green       – healthy / active status
_C_OPERATIONAL = "#66cc22"   # lime        – operational (minor damage)
_C_DEGRADED    = "#ffaa00"   # amber       – degraded
_C_NEUTRALIZED = "#ff2222"   # red         – destroyed (CSG/site)
_C_INTERCEPT   = "#00ffaa"   # bright cyan – kill confirmed
_C_BT          = "#ff3333"   # vivid red   – breakthrough / impact
_C_AI          = "#ff5500"   # orange-red  – AI-guided threat
_C_US_CSG      = "#3399ff"   # blue        – US carrier group
_C_IRAN_SITE   = "#ff6600"   # orange      – Iranian launch site
_C_US_STRIKE   = "#00ff66"   # lime green  – US TLAM / JASSM
_C_LABEL       = "#aaaaaa"   # light grey  – row label text (was muted blue; now neutral grey)
_C_DATA        = "#ffffff"   # pure white  – primary data values
_C_DIM         = "#777777"   # medium grey – footnote / dim / secondary info

# Black BalloonStyle injected into every KML <Style> block
# bgColor / textColor are AABBGGRR format.
_BB = (
    '<BalloonStyle>'
    '<bgColor>ff000000</bgColor>'   # fully opaque black
    '<textColor>ffffffff</textColor>'  # white fallback (overridden by inline HTML styles)
    '<text>$[description]</text>'
    '</BalloonStyle>'
)


def _html_popup(title, accent, rows, footer=None):
    """Return a CDATA-wrapped black-background HTML popup for KML description bubbles.

    Background: pure #000000.
    Text:       #ffffff (primary values) / #aaaaaa (labels) / #777777 (footnotes).
    Accent bar and title use the caller-supplied accent colour for colour-coding by event type.

    accent : CSS colour string for the title / left-border accent  e.g. '#ff4444'
    rows   : list of (label, value) or (label, value, value_colour) tuples
    footer : optional plain-text footnote string
    """
    tr_parts = []
    for idx, row in enumerate(rows):
        label = row[0]
        val   = row[1]
        # value_colour: caller-supplied vivid colour for status/metric cells; default white
        value_colour = row[2] if len(row) > 2 else _C_DATA
        # Alternate very-slightly-grey row backgrounds so long tables are scannable
        row_bg = "background:#0a0a0a;" if idx % 2 == 1 else ""
        tr_parts.append(
            f'<tr style="{row_bg}">'
            f'<td style="color:{_C_LABEL};padding:4px 14px 4px 0;'
            f'white-space:nowrap;vertical-align:top;font-size:11px">{label}</td>'
            f'<td style="color:{value_colour};font-weight:bold;font-size:12px">{val}</td>'
            f'</tr>'
        )
    footer_html = (
        f'<div style="margin-top:9px;padding-top:6px;border-top:1px solid #333333;'
        f'color:{_C_DIM};font-size:10px;line-height:1.5">{footer}</div>'
        if footer else ""
    )
    return (
        "<![CDATA["
        # Negative margins bleed the container to balloon edges (Google Earth adds ~15px padding).
        f'<div style="background:#000000;color:{_C_DATA};'
        f'font-family:\'Courier New\',Courier,monospace;font-size:12px;'
        f'padding:12px 15px 14px 13px;margin:-15px -15px -20px -15px;'
        f'border-left:3px solid {accent};border-top:2px solid {accent};">'
        # Title bar: accent-coloured, bold, uppercase-spaced
        f'<div style="color:{accent};font-weight:bold;font-size:13px;'
        f'letter-spacing:2px;margin-bottom:8px;padding-bottom:6px;'
        f'border-bottom:1px solid #333333;">{title}</div>'
        # Data table: full width, no borders (row shading provides separation)
        f'<table style="width:100%;border-collapse:collapse;">'
        + "".join(tr_parts)
        + f'</table>{footer_html}'
        f'</div>'
        "]]>"
    )

# ============================================================
# KML STYLE BLOCK
# ============================================================

def kml_styles():
    ICON_MUNITION = "http://maps.google.com/mapfiles/kml/shapes/open-diamond.png"
    ICON_STAR     = "http://maps.google.com/mapfiles/kml/shapes/star.png"
    ICON_CIRCLE   = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"

    _DRONE_SCALES = {"Fattah-1 HGV": 1.5,
                     "Emad MRBM": 1.3, "Khalij Fars ASBM": 1.3, "CM-302 Supersonic ASCM": 1.3,
                     "Shahab-3 MRBM": 1.1, "Zolfaghar SRBM": 1.1, "Fateh-313 SRBM": 1.1,
                     "Fateh-110 SRBM": 1.0, "Noor ASCM": 1.0,
                     "Shahed-136": 0.7, "IRGCN Sea Drone": 0.7}

    def icon_block(href, color, scale, label_scale=0):
        label_color = f"<color>{color}</color>" if label_scale > 0 else ""
        return (f"<IconStyle><color>{color}</color><scale>{scale}</scale>"
                f"<Icon><href>{href}</href></Icon></IconStyle>"
                f"<LabelStyle>{label_color}<scale>{label_scale}</scale></LabelStyle>")

    parts = []

    for munition_name, munition_config in MUNITIONS.items():
        style_id         = safe_id(munition_name)
        icon_scale       = _DRONE_SCALES.get(munition_name, 1.0)
        icon_block_normal       = icon_block(ICON_MUNITION, munition_config["color"],    icon_scale)
        icon_block_breakthrough = icon_block(ICON_MUNITION, munition_config["color_bt"], min(icon_scale * 1.15, 2.0))
        icon_block_normal_lbl   = icon_block(ICON_MUNITION, munition_config["color"],    icon_scale,              label_scale=0.6)
        icon_block_bt_lbl       = icon_block(ICON_MUNITION, munition_config["color_bt"], min(icon_scale * 1.15, 2.0), label_scale=0.6)
        parts.append(f"""
  <Style id="{style_id}">
    {icon_block_normal}
    <LineStyle><color>{munition_config['color']}</color><width>{munition_config['width']}</width></LineStyle>
  </Style>
  <Style id="{style_id}_bt">
    {icon_block_breakthrough}
    <LineStyle><color>{munition_config['color_bt']}</color><width>{munition_config['width_bt']}</width></LineStyle>
  </Style>
  <Style id="{style_id}_labeled">
    {icon_block_normal_lbl}
    <LineStyle><color>{munition_config['color']}</color><width>{munition_config['width']}</width></LineStyle>
  </Style>
  <Style id="{style_id}_bt_labeled">
    {icon_block_bt_lbl}
    <LineStyle><color>{munition_config['color_bt']}</color><width>{munition_config['width_bt']}</width></LineStyle>
  </Style>""")

    # Shahed-136 AI-guided approach arc — orange (distinct from normal yellow Shahed)
    # AABBGGRR: A=ff, B=00, G=80, R=ff → RGB(255,128,0) pure orange
    parts.append(f"""
  <Style id="shahed_ai_approach">
    {icon_block(ICON_MUNITION, "ff0080ff", 1.1)}
    <LineStyle><color>ff0080ff</color><width>3</width></LineStyle>
  </Style>
  <Style id="shahed_ai_approach_labeled">
    {icon_block(ICON_MUNITION, "ff0080ff", 1.1, label_scale=0.6)}
    <LineStyle><color>ff0080ff</color><width>3</width></LineStyle>
  </Style>""")

    # Shahed-136 AI terminal redirect — brighter orange (G=a0) for the lock-on leg
    parts.append(f"""
  <Style id="shahed_ai_terminal">
    {icon_block(ICON_MUNITION, "ff00a0ff", 1.1)}
    <LineStyle><color>ff00a0ff</color><width>4</width></LineStyle>
  </Style>
  <Style id="shahed_ai_terminal_labeled">
    {icon_block(ICON_MUNITION, "ff00a0ff", 1.1, label_scale=0.6)}
    <LineStyle><color>ff00a0ff</color><width>4</width></LineStyle>
  </Style>""")

    # IRGCN Sea Drone radar lock-on terminal leg — red-orange (G=44) distinct from amber approach
    # AABBGGRR: A=ff, B=00, G=44, R=ff → RGB(255, 68, 0)
    parts.append(f"""
  <Style id="irgcn_lock_terminal">
    {icon_block(ICON_MUNITION, "ff0044ff", 1.1)}
    <LineStyle><color>ff0044ff</color><width>4</width></LineStyle>
  </Style>
  <Style id="irgcn_lock_terminal_labeled">
    {icon_block(ICON_MUNITION, "ff0044ff", 1.1, label_scale=0.6)}
    <LineStyle><color>ff0044ff</color><width>4</width></LineStyle>
  </Style>""")

    # IAF munition styles (lime/teal family)
    for iaf_munition_name, iaf_munition_config in IAF_MUNITIONS.items():
        style_id          = safe_id(iaf_munition_name) + "_iaf"
        icon_block_normal = icon_block(ICON_MUNITION, iaf_munition_config["color"], 0.9)
        icon_block_lbl    = icon_block(ICON_MUNITION, iaf_munition_config["color"], 0.9, label_scale=0.6)
        parts.append(f"""
  <Style id="{style_id}">
    {icon_block_normal}
    <LineStyle><color>{iaf_munition_config['color']}</color><width>{iaf_munition_config['width']}</width></LineStyle>
  </Style>
  <Style id="{style_id}_labeled">
    {icon_block_lbl}
    <LineStyle><color>{iaf_munition_config['color']}</color><width>{iaf_munition_config['width']}</width></LineStyle>
  </Style>""")

    # US strike munition styles
    for us_strike_name, us_strike_config in US_STRIKE_MUNITIONS.items():
        style_id          = safe_id(us_strike_name)
        icon_block_normal = icon_block(ICON_MUNITION, us_strike_config["color"], 1.0)
        parts.append(f"""
  <Style id="{style_id}">
    {icon_block_normal}
    <LineStyle><color>{us_strike_config['color']}</color><width>{us_strike_config['width']}</width></LineStyle>
  </Style>""")

    # US interceptor tracks — all blue family; SM-6/SM-2 (star), CIWS/NavGun (circle)
    # AABBGGRR blue tones: B=ff keeps all tracks in blue family
    # us_lo:  light steel blue  RGB(136,204,255) = ff cc 88 → "aaffcc88"  (unchanged)
    # us_mid: cornflower blue   RGB( 68,136,255) = ff 88 44 → "bbff8844"  (unchanged)
    # us_hi:  deep navy blue    RGB(  0, 68,255) = ff 44 00 → "eeff4400"  (unchanged)
    # us_ciws: bright sky blue  RGB(  0,153,255) = ff 99 00 → "bbff9900"  (was teal)
    # us_naval_gun: azure blue  RGB( 51,153,255) = ff 99 33 → "bbff9933"  (was seafoam)
    for sid, width, color, icon, sc in [
        ("us_lo",        2, "aaffcc88", ICON_STAR,   0.8),
        ("us_mid",       3, "bbff8844", ICON_STAR,   0.8),
        ("us_hi",        4, "eeff4400", ICON_STAR,   0.8),
        ("us_ciws",      2, "bbff9900", ICON_CIRCLE, 0.6),
        ("us_naval_gun", 2, "bbff9933", ICON_CIRCLE, 0.6),
    ]:
        ib = icon_block(icon, color, sc)
        parts.append(f"""
  <Style id="{sid}">
    {ib}
    <LineStyle><color>{color}</color><width>{width}</width></LineStyle>
  </Style>""")

    parts.append("""
  <Style id="us_defense_ring">
    <!-- SM-6 240 km — deep navy blue: RGB(00,22,ff) AABBGGRR=77ff2200 -->
    <LineStyle><color>77ff2200</color><width>1</width></LineStyle>
    <PolyStyle><color>0aff2200</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_sm2">
    <!-- SM-2 167 km — cornflower blue: RGB(44,88,ff) AABBGGRR=55ff8844 -->
    <LineStyle><color>55ff8844</color><width>1</width></LineStyle>
    <PolyStyle><color>05ff8844</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_essm">
    <!-- ESSM 50 km — sky blue: RGB(00,aa,ff) AABBGGRR=88ffaa00 -->
    <LineStyle><color>88ffaa00</color><width>1</width></LineStyle>
    <PolyStyle><color>08ffaa00</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_ram">
    <!-- RAM 15 km — cyan: RGB(00,cc,ff) AABBGGRR=aaffcc00 -->
    <LineStyle><color>aaffcc00</color><width>1</width></LineStyle>
    <PolyStyle><color>0affcc00</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_hit">
    <!-- SM-6 DEGRADED — warm orange outline signals damage: RGB(ff,66,00) AABBGGRR=cc0066ff -->
    <LineStyle><color>cc0066ff</color><width>2</width></LineStyle>
    <PolyStyle><color>220066ff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_sm2_hit">
    <!-- SM-2 DEGRADED — orange: RGB(ff,88,00) AABBGGRR=880088ff -->
    <LineStyle><color>880088ff</color><width>1</width></LineStyle>
    <PolyStyle><color>110088ff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_essm_hit">
    <!-- ESSM DEGRADED — amber: RGB(ff,aa,00) AABBGGRR=aa00aaff -->
    <LineStyle><color>aa00aaff</color><width>1</width></LineStyle>
    <PolyStyle><color>0a00aaff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_defense_ring_ram_hit">
    <!-- RAM DEGRADED — yellow-amber: RGB(ff,cc,00) AABBGGRR=bb00ccff -->
    <LineStyle><color>bb00ccff</color><width>1</width></LineStyle>
    <PolyStyle><color>0a00ccff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="us_csg_marker">
    <!-- US ships ALIVE — green (ABGR ff00ff00 = full-alpha pure green) -->
    <IconStyle>
      <color>ff00ff00</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff00ff00</color><scale>0.7</scale></LabelStyle>
  </Style>
  <Style id="us_csg_hit_marker">
    <!-- US ships UNDER ATTACK — amber/yellow indicates damage -->
    <IconStyle>
      <color>ff00ccff</color><scale>1.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff00ccff</color><scale>1.1</scale></LabelStyle>
  </Style>
  <Style id="us_csg_neutralized_marker">
    <!-- US ships DEAD — fade to white; icon persists for full simulation duration -->
    <IconStyle>
      <color>ffffffff</color><scale>1.6</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ffffffff</color><scale>1.0</scale></LabelStyle>
  </Style>
  <Style id="iran_site_marker">
    <!-- Iranian sites ACTIVE — red (ABGR ff0000ff = full-alpha pure red) -->
    <IconStyle>
      <color>ff0000ff</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.7</scale></LabelStyle>
  </Style>
  <Style id="iran_site_inactive">
    <!-- Iranian sites DESTROYED — fade to black; icon persists for full simulation duration -->
    <IconStyle>
      <color>ff000000</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-circle.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff333333</color><scale>0.7</scale></LabelStyle>
  </Style>
  <Style id="intercept_marker">
    <!-- US kill point — black square, flashes black/white for 30 s -->
    <IconStyle>
      <color>ff000000</color><scale>0.9</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff000000</color><scale>0.6</scale></LabelStyle>
  </Style>
  <Style id="intercept_marker_white">
    <!-- US kill point — white square (alternates with black every 3 s) -->
    <IconStyle>
      <color>ffffffff</color><scale>0.9</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ffffffff</color><scale>0.6</scale></LabelStyle>
  </Style>
  <Style id="impact_marker">
    <!-- Iranian breakthrough impact — warm red target: RGB(ff,00,00) AABBGGRR=ff0000ff -->
    <IconStyle>
      <color>ff0000ff</color><scale>1.3</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.9</scale></LabelStyle>
  </Style>
  <Style id="us_strike_impact_marker">
    <!-- US TLAM/JASSM strike impact — deep blue star: RGB(00,44,ff) AABBGGRR=ffff4400 -->
    <IconStyle>
      <color>ffff4400</color><scale>1.0</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/star.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ffff4400</color><scale>0.6</scale></LabelStyle>
  </Style>
  <Style id="strike_icon">
    <!-- IAF strike impact on active site — lime star -->
    <IconStyle>
      <color>ff00ff88</color><scale>1.0</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/star.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff00ff88</color><scale>0.6</scale></LabelStyle>
  </Style>
  <Style id="dead_icon">
    <!-- IAF strike on already-inactivated site — grey cross -->
    <IconStyle>
      <color>ff888888</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff888888</color><scale>0.5</scale></LabelStyle>
  </Style>
  <Style id="iaf_base_marker">
    <IconStyle>
      <color>ff00ff88</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff00ff88</color><scale>0.7</scale></LabelStyle>
  </Style>
  <Style id="csg_tour_flash">
    <!-- Tour-only: large orange-red explosion icon revealed by gx:AnimatedUpdate when a CSG is destroyed -->
    <IconStyle>
      <color>ff0022ff</color><scale>3.2</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0022ff</color><scale>1.4</scale></LabelStyle>
  </Style>""")

    # ── Health-color styles for US CSGs: green (intact) → white (destroyed) ──
    # User spec: "our troops are green and fade to white" when killed.
    # AABBGGRR: G=ff constant; R and B rise 0→255 as damage increases (green→white).
    # Dead icons persist for full simulation duration (no TimeSpan end trimming).
    US_CSG_ICON_URL = "http://maps.google.com/mapfiles/kml/paddle/grn-stars.png"
    for damage_level in range(11):
        if damage_level == 10:
            kml_color = "ffffffff"  # fully destroyed → pure white
        else:
            damage_fraction = damage_level / 10
            fade_component  = int(255 * damage_fraction)   # R and B both rise toward white
            kml_color = f"ff{fade_component:02x}ff{fade_component:02x}"   # ABGR: A=ff B=fade G=ff R=fade
        parts.append(
            f'  <Style id="us_h_{damage_level}">'
            f'<IconStyle><color>{kml_color}</color><scale>0.7</scale>'
            f'<Icon><href>{US_CSG_ICON_URL}</href></Icon></IconStyle>'
            f'<LabelStyle><color>{kml_color}</color><scale>0.7</scale></LabelStyle>'
            f'</Style>'
        )

    # ── Health-color styles for Iranian sites: red (active) → black (destroyed) ──
    # User spec: "theirs are red and fade to black when they die."
    # AABBGGRR: R falls 255→0, G=0, B=0 across 30 damage levels (red→black).
    # Dead icons persist for full simulation duration (TimeSpan end = scenario end_s).
    IRAN_SITE_ICON_ACTIVE    = "http://maps.google.com/mapfiles/kml/paddle/red-stars.png"
    IRAN_SITE_ICON_DESTROYED = "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png"
    for damage_level in range(31):
        if damage_level == 30:
            kml_color   = "ff000000"  # fully destroyed → pure black
            site_icon   = IRAN_SITE_ICON_DESTROYED
        else:
            damage_fraction = damage_level / 30
            red_component   = int(255 * (1.0 - damage_fraction))   # red fades to zero
            kml_color       = f"ff0000{red_component:02x}"          # ABGR: A=ff B=00 G=00 R=red
            site_icon       = IRAN_SITE_ICON_ACTIVE
        parts.append(
            f'  <Style id="ir_h_{damage_level}">'
            f'<IconStyle><color>{kml_color}</color><scale>0.7</scale>'
            f'<Icon><href>{site_icon}</href></Icon></IconStyle>'
            f'<LabelStyle><color>{kml_color}</color><scale>0.7</scale></LabelStyle>'
            f'</Style>'
        )

    # ── Individual ship styles ────────────────────────────────────────────────
    _SHIP_ICON = "http://maps.google.com/mapfiles/kml/shapes/sailing.png"
    _SHIP_ICON_X = "http://maps.google.com/mapfiles/kml/shapes/placemark_square.png"
    for _role, _scale, _color in [
        ("cvn",  0.60, "ffffffff"),   # carrier — full white
        ("cg",   0.40, "ffddddff"),   # cruiser — light blue-white
        ("ddg",  0.35, "ffaaccff"),   # destroyer — blue-tinted
        ("aoe",  0.30, "ff88aaaa"),   # supply ship — grey-teal
    ]:
        parts.append(
            f'<Style id="ship_{_role}">'
            f'<IconStyle><color>{_color}</color><scale>{_scale}</scale>'
            f'<Icon><href>{_SHIP_ICON}</href></Icon></IconStyle>'
            f'<LabelStyle><scale>0</scale></LabelStyle>'
            f'</Style>'
        )
    # Destroyed ship — small dark red X square
    parts.append(
        f'<Style id="ship_destroyed">'
        f'<IconStyle><color>ff2222cc</color><scale>0.45</scale>'
        f'<Icon><href>{_SHIP_ICON_X}</href></Icon></IconStyle>'
        f'<LabelStyle><scale>0</scale></LabelStyle>'
        f'</Style>'
    )
    # Group-stopped ship — grey (same icon, greyed out)
    parts.append(
        f'<Style id="ship_stopped">'
        f'<IconStyle><color>ff888888</color><scale>0.32</scale>'
        f'<Icon><href>{_SHIP_ICON}</href></Icon></IconStyle>'
        f'<LabelStyle><scale>0</scale></LabelStyle>'
        f'</Style>'
    )

    _raw = "\n".join(parts)
    # Inject black BalloonStyle into every Style block so all popups are fully black
    return _raw.replace("</Style>", f"{_BB}</Style>")

# ============================================================
# GX:TRACK BUILDER  (one Placemark per munition, animated icon)
# ============================================================

def _geodetic_bearing(lon1, lat1, lon2, lat2):
    """Compass bearing in degrees (CW from north) from point 1 to point 2."""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlon   = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def gx_track(style_id_val, pts, t_pts_s, label, desc_first="", altitude_mode="relativeToGround"):
    """Return a list containing a single gx:Track Placemark string.
    Includes <gx:angles> at each waypoint so icons face the direction of travel.
    altitude_mode: "relativeToGround" for all munitions; "clampToGround" for surface vessels.
    """
    n = len(pts)
    # Compute per-point compass heading from successive positions
    bearings = []
    for k in range(n):
        if k < n - 1:
            b = _geodetic_bearing(pts[k][0], pts[k][1], pts[k+1][0], pts[k+1][1])
        else:
            b = bearings[-1] if bearings else 0.0
        bearings.append(b)

    when_coords = ""
    for (lon, lat, alt), t, brg in zip(pts, t_pts_s, bearings):
        when_coords += (
            f"<when>{fmt_time(sim_time(t))}</when>"
            f"<gx:coord>{lon:.5f} {lat:.5f} {max(0.0, alt):.0f}</gx:coord>"
            f"<gx:angles>{brg:.1f} 0 0</gx:angles>"
        )
    desc_tag  = f"<description>{desc_first}</description>" if desc_first else ""
    t_begin   = fmt_time(sim_time(t_pts_s[0]))
    t_end     = fmt_time(sim_time(t_pts_s[-1]))
    time_span = f"<TimeSpan><begin>{t_begin}</begin><end>{t_end}</end></TimeSpan>"
    return [
        f"      <Placemark>"
        f"<name>{label}</name>"
        f"<styleUrl>#{style_id_val}</styleUrl>"
        + time_span
        + desc_tag
        + f"<gx:Track>"
          f"<altitudeMode>{altitude_mode}</altitudeMode>"
        + when_coords
        + f"</gx:Track>"
          f"</Placemark>"
    ]

# ============================================================
# FIXED LAYERS
# ============================================================

_CSG_NEUTRALIZATION_HITS = 10   # hits that neutralize a CSG

# Time resolution for animated WEZ ring updates: 5-minute slices.
# Each slice re-centres the ring polygon on csg_pos_at(t), so at 20 knots
# the ring moves ~1.54 km per update — imperceptible for large rings and
# a smooth animation for the ESSM (50 km) and RAM (15 km) close-in rings.
_WEZ_STEP_S = 300   # seconds per WEZ polygon slice


def _animated_wez_ring(csg, radius_km, style_active, style_degraded,
                        t_total_s, first_hit_s, tenth_hit_s, label="WEZ"):
    """
    Return KML for a WEZ ring that tracks the moving CSG.

    Replaces the previous approach of a single static <Polygon> at the
    ship's starting position.  Instead, emits a sequence of
    TimeSpan-bounded <Polygon> Placemarks, each centred at the ship's
    actual position at the start of that time slice (via csg_pos_at).

    Style switches from style_active to style_degraded at first_hit_s,
    and the ring disappears entirely at tenth_hit_s (CSG destroyed).
    """
    out  = []
    t    = 0.0
    name = csg["name"]
    while t < t_total_s:
        t_next = min(t + _WEZ_STEP_S, t_total_s)
        # Stop emitting once the CSG is destroyed
        if tenth_hit_s is not None and t >= tenth_hit_s:
            break
        style = (style_degraded
                 if first_hit_s is not None and t >= first_hit_s
                 else style_active)
        # Ring centred on ship position at start of this slice
        clon, clat = csg_pos_at(csg, t)
        coords     = circle_ring(clon, clat, radius_km)
        begin_str  = fmt_time(sim_time(t))
        end_str    = fmt_time(sim_time(t_next))
        out.append(
            f'    <Placemark>\n'
            f'      <name>{name} -- {label}</name>'
            f'<styleUrl>#{style}</styleUrl>\n'
            f'      <TimeSpan>'
            f'<begin>{begin_str}</begin><end>{end_str}</end>'
            f'</TimeSpan>\n'
            f'      <Polygon><tessellate>1</tessellate>\n'
            f'        <outerBoundaryIs><LinearRing>\n'
            f'          <coordinates>{coords}</coordinates>\n'
            f'        </LinearRing></outerBoundaryIs>\n'
            f'      </Polygon>\n'
            f'    </Placemark>\n'
        )
        t = t_next
    return "".join(out)


def gen_csg_ship_kml(csg, ships, ship_destroyed_at, group_stopped_at, asset_end_s):
    """
    Generate KML for the 10 individual ships of a CSG.

    Each ship is rendered as a gx:Track showing movement from T=0 until the ship
    either (a) is directly destroyed by a 20 m-radius hit, or (b) belongs to a
    directional group whose lead ship was killed and the group halted, or (c) the
    scenario ends.  A red kill-marker Placemark is added at the destruction point.
    """
    parts = []
    for ship in ships:
        sid   = ship["id"]
        role  = ship["role"].lower()

        # Determine when this ship stops moving
        destroy_t   = ship_destroyed_at.get(sid)
        gkey        = (csg["name"], ship["group"])
        grp_stop_t  = group_stopped_at.get(gkey)

        if destroy_t is not None:
            stop_t     = destroy_t
            style_id   = "ship_destroyed"
        elif grp_stop_t is not None:
            stop_t     = grp_stop_t
            style_id   = "ship_stopped"
        else:
            stop_t     = asset_end_s
            style_id   = f"ship_{role}"

        lon0, lat0 = ship_pos_at(csg, ship, 0.0)
        lon1, lat1 = ship_pos_at(csg, ship, stop_t)
        t0 = fmt_time(sim_time(0.0))
        t1 = fmt_time(sim_time(stop_t))

        name_lbl = f"{ship['role']} ({csg['name'][:15]})"
        parts.append(
            f'  <Placemark>\n'
            f'    <name>{name_lbl}</name>\n'
            f'    <styleUrl>#{style_id}</styleUrl>\n'
            f'    <gx:Track>\n'
            f'      <altitudeMode>clampToGround</altitudeMode>\n'
            f'      <when>{t0}</when><when>{t1}</when>\n'
            f'      <gx:coord>{lon0:.6f} {lat0:.6f} 0</gx:coord>'
            f'<gx:coord>{lon1:.6f} {lat1:.6f} 0</gx:coord>\n'
            f'    </gx:Track>\n'
            f'  </Placemark>'
        )

        if destroy_t is not None:
            klon, klat = ship_pos_at(csg, ship, destroy_t)
            kt = fmt_time(sim_time(destroy_t))
            parts.append(
                f'  <Placemark>\n'
                f'    <name>KILLED {ship["role"]} ({csg["name"][:12]})</name>\n'
                f'    <styleUrl>#ship_destroyed</styleUrl>\n'
                f'    <TimeStamp><when>{kt}</when></TimeStamp>\n'
                f'    <Point><altitudeMode>clampToGround</altitudeMode>\n'
                f'      <coordinates>{klon:.6f},{klat:.6f},0</coordinates>\n'
                f'    </Point>\n'
                f'  </Placemark>'
            )
    return "\n".join(parts)


def gen_us_forces(first_hit_s=None, tenth_hit_s=None, latest_s=3600,
                  csg_fleet=None, hits_timeline=None):
    first_hit_s    = first_hit_s    or {}
    tenth_hit_s    = tenth_hit_s    or {}
    hits_timeline  = hits_timeline  or {}
    if csg_fleet is None:
        csg_fleet = US_CSGS
    out = []

    for csg in csg_fleet:
        name = csg["name"]
        fh   = first_hit_s.get(name)
        th   = tenth_hit_s.get(name)

        # ── Defense engagement rings — animated to follow the moving CSG ──────
        # Each ring is a sequence of time-sliced Polygons re-centred every
        # _WEZ_STEP_S seconds.  Style: active until first hit, degraded after,
        # gone after tenth hit (CSG destroyed).
        for radius_km, style_ok, style_hit, label_suffix in [
            (WPN_RANGES["SM-6"],  "us_defense_ring",      "us_defense_ring_hit",      "SM-6 240 km"),
            (WPN_RANGES["SM-2"],  "us_defense_ring_sm2",  "us_defense_ring_sm2_hit",  "SM-2 167 km"),
            (WPN_RANGES["ESSM"],  "us_defense_ring_essm", "us_defense_ring_essm_hit", "ESSM  50 km"),
            (WPN_RANGES["RAM"],   "us_defense_ring_ram",  "us_defense_ring_ram_hit",  "RAM   15 km"),
        ]:
            out.append(_animated_wez_ring(
                csg, radius_km, style_ok, style_hit,
                latest_s, fh, th, label=label_suffix))

    # ── CSG icon tracks: health-colored, freeze on neutralization ────────────
    for csg in csg_fleet:
        csg_hits = hits_timeline.get(csg["name"], [])
        out.append(_build_csg_damage_track(
            csg, csg_hits, _CSG_NEUTRALIZATION_HITS, latest_s))

    return "\n".join(out)


_ALTITUDE_MAX_M = 100_000.0  # 100 km starting altitude for asset icon tracks

def _damage_phases(hit_times, n_hits_max, end_s):
    """Return list of (t_start, t_end, n_hits_before) phases.
    Each phase covers the period between two consecutive hit events.
    """
    hits   = sorted(hit_times[:n_hits_max])
    phases = []
    t_prev = 0.0
    for idx, hit_t in enumerate(hits):
        if hit_t > t_prev:
            phases.append((t_prev, hit_t, idx))
        t_prev = hit_t
    phases.append((t_prev, end_s, len(hits)))
    return phases


def _build_damage_track(lon, lat, hit_times, n_hits_max, style_prefix, label, end_s):
    """One gx:Track Placemark per damage phase.  Each phase uses a health-
    colored style (style_prefix + '_h_N') and holds a fixed (lon, lat) position
    while the icon altitude drops as hits accumulate.
    style_prefix : 'ir' for Iranian sites  (ir_h_0 … ir_h_25, blue→orange)
    """
    out = []
    for t_start, t_end, n_hits in _damage_phases(hit_times, n_hits_max, end_s):
        health_pct = round(100 * (1 - n_hits / n_hits_max))
        status     = ("ACTIVE"       if n_hits == 0
                      else "OPERATIONAL" if n_hits < n_hits_max // 2
                      else "DEGRADED"    if n_hits < n_hits_max
                      else "DESTROYED")
        status_col = (_C_ACTIVE      if n_hits == 0
                      else _C_OPERATIONAL if n_hits < n_hits_max // 2
                      else _C_DEGRADED    if n_hits < n_hits_max
                      else _C_NEUTRALIZED)
        desc = _html_popup(f"◈ IRAN SITE — {label}", _C_IRAN_SITE, [
            ("Status",    status,                          status_col),
            ("Health",    f"{health_pct}%",               status_col),
            ("Hits",      f"{n_hits} / {n_hits_max}",     _C_DEGRADED),
        ])
        wc = (
            f"\n      <when>{fmt_time(sim_time(t_start))}</when>"
            f"\n      <gx:coord>{lon:.6f} {lat:.6f} 0</gx:coord>"
            f"\n      <gx:angles>0 0 0</gx:angles>"
            f"\n      <when>{fmt_time(sim_time(t_end))}</when>"
            f"\n      <gx:coord>{lon:.6f} {lat:.6f} 0</gx:coord>"
            f"\n      <gx:angles>0 0 0</gx:angles>"
        )
        _site_label = f'{label}  ({health_pct}%)'
        out.append(
            f'  <Placemark><name>{_site_label}</name>'
            f'<styleUrl>#{style_prefix}_h_{n_hits}</styleUrl>'
            f'<description>{desc}</description>'
            f'<TimeSpan>'
            f'<begin>{fmt_time(sim_time(t_start))}</begin>'
            f'<end>{fmt_time(sim_time(t_end))}</end>'
            f'</TimeSpan>'
            f'<gx:Track><altitudeMode>relativeToGround</altitudeMode>'
            + wc + f'\n  </gx:Track></Placemark>\n'
        )
    return "".join(out)


def _build_csg_damage_track(csg, hit_times, n_hits_max, end_s):
    """One gx:Track per damage phase for a CSG.  The icon moves west with the
    ship AND changes color green→red while descending to 0 as hits accumulate.
    Uses 'us_h_N' styles.
    """
    hdg_deg = csg.get("heading_deg", 270)
    out     = []
    for t_start, t_end, n_hits in _damage_phases(hit_times, n_hits_max, end_s):
        lo0, la0   = csg_pos_at(csg, t_start)
        # Freeze position on neutralization — no further movement
        if n_hits >= n_hits_max:
            lo1, la1 = lo0, la0
        else:
            lo1, la1 = csg_pos_at(csg, t_end)
        health_pct = round(100 * (1 - n_hits / n_hits_max))
        status     = ("COMBAT READY" if n_hits == 0
                      else "OPERATIONAL" if n_hits < 4
                      else "DEGRADED"    if n_hits < n_hits_max
                      else "DESTROYED")
        status_col = (_C_ACTIVE      if n_hits == 0
                      else _C_OPERATIONAL if n_hits < 4
                      else _C_DEGRADED    if n_hits < n_hits_max
                      else _C_NEUTRALIZED)
        desc = _html_popup(f"⚓ {csg['name']}", _C_US_CSG, [
            ("Class",    csg.get("class", "CVN"),                        _C_US_CSG),
            ("Escorts",  csg.get("escorts", "—"),                        _C_DATA),
            ("Status",   status,                                          status_col),
            ("Health",   f"{health_pct}%",                               status_col),
            ("Hits",     f"{n_hits} / {n_hits_max}",                    _C_DEGRADED),
            ("SM-6",     f"{csg['sm6_low']}–{csg['sm6_high']} rds (240 km)",  _C_US_CSG),
            ("SM-2",     f"{csg['sm2_low']}–{csg['sm2_high']} rds (167 km)",  _C_US_CSG),
            ("ESSM",     f"{csg['essm_low']}–{csg['essm_high']} rds (50 km)", _C_US_CSG),
            ("RAM",      f"{csg['ram_low']}–{csg['ram_high']} rds (15 km)",   _C_US_CSG),
        ])
        wc = (
            f"\n      <when>{fmt_time(sim_time(t_start))}</when>"
            f"\n      <gx:coord>{lo0:.6f} {la0:.6f} 0</gx:coord>"
            f"\n      <gx:angles>{hdg_deg:.1f} 0 0</gx:angles>"
            f"\n      <when>{fmt_time(sim_time(t_end))}</when>"
            f"\n      <gx:coord>{lo1:.6f} {la1:.6f} 0</gx:coord>"
            f"\n      <gx:angles>{hdg_deg:.1f} 0 0</gx:angles>"
        )
        _csg_label = f'{csg["name"]}  ({health_pct}%)'
        out.append(
            f'  <Placemark><name>{_csg_label}</name>'
            f'<styleUrl>#us_h_{n_hits}</styleUrl>'
            f'<description>{desc}</description>'
            f'<TimeSpan>'
            f'<begin>{fmt_time(sim_time(t_start))}</begin>'
            f'<end>{fmt_time(sim_time(t_end))}</end>'
            f'</TimeSpan>'
            f'<gx:Track><altitudeMode>relativeToGround</altitudeMode>'
            + wc + f'\n  </gx:Track></Placemark>\n'
        )
    return "".join(out)


def gen_iran_sites(site_inactive_at=None, site_hits_timeline=None, end_s=7200,
                   sites=None, threshold=None):
    """Render each launch site as a health-colored gx:Track icon (blue→white)
    that changes color as US strikes land, positioned at _ALTITUDE_MAX_M.
    """
    site_inactive_at   = site_inactive_at   or {}
    site_hits_timeline = site_hits_timeline or {}
    sites     = sites     if sites     is not None else IRAN_SITES
    threshold = threshold if threshold is not None else SITE_INACTIVATION_THRESHOLD
    out = []
    for s in sites:
        lon, lat  = s["lon"], s["lat"]
        site_hits = site_hits_timeline.get(s["name"], [])
        out.append(_build_damage_track(
            lon, lat, site_hits, threshold,
            "ir", s["name"], end_s))
    return "\n".join(out)

# ============================================================
# US COUNTERSTRIKE PRE-COMPUTATION
# ============================================================

def compute_us_strikes(scenario_key, rng, sites=None, threshold=None):
    """
    Pre-compute US TLAM/JASSM strike events against Iranian launch sites.

    Strikes are weighted by inverse distance (closer = higher strike priority)
    and give coastal/island sites a 1.5× bonus (primary Shahed/ASCM launchers).

    Returns
    -------
    strike_events : list of dicts
        Each dict: csg, site, munition, dist_km, launch_s, impact_s
    site_inactive_at : dict[str -> float]
        Maps site name to the impact_s of the Nth hit (inactivation moment).
        Sites that never reach N hits are absent from the dict.
    """
    sc = SCENARIOS[scenario_key]
    n_per_csg = sc.get("n_us_strikes_per_csg", 20)
    sites     = sites     if sites     is not None else IRAN_SITES
    threshold = threshold if threshold is not None else SITE_INACTIVATION_THRESHOLD

    # Collect raw hit times per site before sorting
    site_raw = {s["name"]: [] for s in sites}

    for csg in US_CSGS:
        # Compute distance-weighted probability for each site
        weights = []
        for site in sites:
            d = haversine_km(csg["lon"], csg["lat"], site["lon"], site["lat"])
            coastal_bonus = 1.5 if site["type"] in ("Coastal Battery", "Island Fortress") else 1.0
            w = coastal_bonus / max(d, 50)
            weights.append(w)
        total_w = sum(weights)
        weights = [w / total_w for w in weights]

        for _ in range(n_per_csg):
            # Weighted site selection
            r, cum = rng.random(), 0.0
            tgt_site = sites[-1]
            for k, site in enumerate(sites):
                cum += weights[k]
                if r <= cum:
                    tgt_site = site
                    break

            dist_km = haversine_km(csg["lon"], csg["lat"],
                                   tgt_site["lon"], tgt_site["lat"])
            # JASSM-ER for sites within 1,000 km; TLAM Block IV beyond
            if dist_km <= 1000:
                munition, speed = "JASSM-ER", US_STRIKE_MUNITIONS["JASSM-ER"]["speed_km_s"]
            else:
                munition, speed = "TLAM Block IV", US_STRIKE_MUNITIONS["TLAM Block IV"]["speed_km_s"]

            flight_s = dist_km / speed
            if sc.get("us_strike_timing") == "perfect":
                # Pre-launched to arrive in the opening 5-minute window.
                # launch_s is negative (missiles were in the air before t=0).
                impact_s = rng.uniform(0, 300)
                launch_s = impact_s - flight_s
            else:
                # US strikes concentrated in first 60% of scenario wave
                launch_s = rng.uniform(0, sc["wave_s"] * 0.6)
                impact_s = launch_s + flight_s

            site_raw[tgt_site["name"]].append({
                "csg": csg, "site": tgt_site, "munition": munition,
                "dist_km": dist_km, "launch_s": launch_s, "impact_s": impact_s,
            })

    # Sort each site's events by impact time; compute inactivation moment
    site_inactive_at = {}
    all_events = []
    for site_name, evts in site_raw.items():
        evts.sort(key=lambda e: e["impact_s"])
        all_events.extend(evts)
        if len(evts) >= threshold:
            site_inactive_at[site_name] = evts[threshold - 1]["impact_s"]

    # Build sorted hit-time lists per site (for altitude-degradation tracks)
    site_hits_timeline = {
        sn: sorted(e["impact_s"] for e in evts)
        for sn, evts in site_raw.items() if evts
    }
    return all_events, site_inactive_at, site_hits_timeline


def gen_us_strike_kml(strike_events, site_inactive_at, n_arc=8, threshold=None):
    """
    Build KML track segments and impact markers for US TLAM/JASSM strikes.
    Only renders strikes that land BEFORE or AT inactivation (wasted strikes
    beyond the threshold are omitted to reduce file size).
    """
    threshold = threshold if threshold is not None else SITE_INACTIVATION_THRESHOLD
    segs_by_type   = {m: [] for m in US_STRIKE_MUNITIONS}
    impacts        = []
    hit_counter    = {}   # site_name -> running hit count for labelling

    # Sort all events by launch time for consistent ordering
    for ev in sorted(strike_events, key=lambda e: e["launch_s"]):
        site_name = ev["site"]["name"]
        hit_counter[site_name] = hit_counter.get(site_name, 0) + 1
        hit_num = hit_counter[site_name]

        # Only render up to threshold hits per site
        if hit_num > threshold:
            continue

        csg      = ev["csg"]
        site     = ev["site"]
        munition = ev["munition"]
        mdef     = US_STRIKE_MUNITIONS[munition]
        launch_s = ev["launch_s"]
        impact_s = ev["impact_s"]
        dist_km  = ev["dist_km"]

        fire_lon, fire_lat = csg_pos_at(csg, launch_s)
        pts    = arc_points(fire_lon, fire_lat, site["lon"], site["lat"],
                            mdef["peak_alt_m"], n_arc, True)
        t_pts  = [launch_s + (k / n_arc) * (impact_s - launch_s) for k in range(n_arc + 1)]
        style  = safe_id(munition)
        label  = f"{munition} {csg['name']} → {site_name} #{hit_num}"
        desc   = (f"US strike -- {munition} | {csg['name']} to {site_name} | "
                  f"{dist_km:.0f} km | impact T+{impact_s/60:.1f} min | "
                  f"hit #{hit_num}/{threshold}")

        segs_by_type[munition] += gx_track(style, pts, t_pts, label, desc)

        inact_tag = ""
        if site_inactive_at.get(site_name) is not None and hit_num == threshold:
            inact_tag = " [SITE DESTROYED]"

        impacts.append(
            f"      <Placemark>"
            f"<name>US Strike #{hit_num} → {site_name}{inact_tag}</name>"
            f"<styleUrl>#us_strike_impact_marker</styleUrl>"
            f"<description>{_html_popup('◉ US STRIKE', _C_US_STRIKE, [('Munition', munition, _C_US_STRIKE), ('Target', site_name, _C_IRAN_SITE), ('Hit count', f'{hit_num} / {threshold}', _C_DEGRADED), ('Time', f'T+{impact_s/60:.1f} min', _C_US_STRIKE)])}</description>"
            f"<TimeStamp><when>{fmt_time(sim_time(impact_s))}</when></TimeStamp>"
            f"<Point><altitudeMode>relativeToGround</altitudeMode>"
            f"<coordinates>{site['lon']:.5f},{site['lat']:.5f},0</coordinates>"
            f"</Point></Placemark>"
        )

    return segs_by_type, impacts

# ============================================================
# SCENARIO GENERATOR
# ============================================================

def compute_iaf_strikes(scenario_key, rng, site_inactive_at, sites=None, threshold=None):
    """
    Generate Israeli Air Force strike events against Iranian launch sites.

    Each aircraft makes 2 passes per sortie (circle-back attack):
      - Pass 1: drops PASS1_ROUNDS munitions on the chosen target
      - Pass 2: 20-40 min later, picks a fresh (live) target and drops PASS2_ROUNDS more
    If the original target is already destroyed, the aircraft redirects to the
    highest-priority surviving site rather than going home empty.

    Returns (all_events, iaf_site_hits_timeline) where iaf_site_hits_timeline is
    a dict[site_name -> sorted list of impact_s] for merging into the combined
    site damage model.
    """
    sc           = SCENARIOS[scenario_key]
    wave_s       = sc["wave_s"]
    pkg_days     = min(3, math.ceil(wave_s / 86_400)) if wave_s > 3_600 else 1
    sites        = sites     if sites     is not None else IRAN_SITES
    threshold    = threshold if threshold is not None else SITE_INACTIVATION_THRESHOLD
    PASS1_ROUNDS = 2
    PASS2_ROUNDS = 2
    TURNAROUND_S = (20 * 60, 40 * 60)   # seconds
    all_events   = []
    iaf_hits   = {s["name"]: [] for s in sites}
    _destroyed = set(site_inactive_at.keys())  # sites already gone before IAF arrives

    for base in IAF_BASES:
        mname     = base["munition"]
        mdef      = IAF_MUNITIONS[mname]
        n_sorties = base["sorties"] * pkg_days
        max_rng   = mdef["max_range_km"]
        speed     = mdef["speed_km_s"]

        eligible = []
        for site in sites:
            dist = haversine_km(base["lon"], base["lat"], site["lon"], site["lat"])
            if dist <= 2_500 and dist >= max_rng:
                eligible.append((site, dist))
        if not eligible:
            continue

        base_weights = [1.5 if s["type"] in ("Coastal Battery", "Island Fortress") else 1.0
                        for s, _ in eligible]
        total_w = sum(base_weights)
        base_weights = [w / total_w for w in base_weights]

        def _pick_live_target(excluded_name=None):
            """Pick a weighted-random eligible site that is not yet destroyed."""
            live = [(s, d, w) for (s, d), w in zip(eligible, base_weights)
                    if s["name"] not in _destroyed and s["name"] != excluded_name]
            if not live:
                # every eligible site is gone — fall back to any eligible site
                live = [(s, d, w) for (s, d), w in zip(eligible, base_weights)]
            if not live:
                return None, None
            sites_l, dists_l, ws_l = zip(*live)
            tw = sum(ws_l)
            norm = [w / tw for w in ws_l]
            idx = rng.choices(range(len(sites_l)), weights=norm, k=1)[0]
            return sites_l[idx], dists_l[idx]

        for _ in range(n_sorties):
            # ── Pass 1 ────────────────────────────────────────────────────────
            tgt1, dist1 = _pick_live_target()
            if tgt1 is None:
                rng.uniform(0, 1)   # consume RNG for determinism
                rng.uniform(0, 1)
                continue
            flight1 = dist1 / speed
            if sc.get("iaf_timing") == "perfect":
                impact1 = rng.uniform(0, 300)
                launch1 = impact1 - flight1
            else:
                launch1 = rng.uniform(3600, wave_s * 0.85)
                impact1 = launch1 + flight1
            for _ in range(PASS1_ROUNDS):
                all_events.append({
                    "base": base, "site": tgt1, "munition": mname,
                    "dist_km": dist1, "launch_s": launch1, "impact_s": impact1,
                    "pass_num": 1,
                })
                iaf_hits[tgt1["name"]].append(impact1)

            # ── Pass 2 (circle-back) ──────────────────────────────────────────
            turnaround = rng.uniform(*TURNAROUND_S)
            tgt2, dist2 = _pick_live_target(excluded_name=tgt1["name"])
            if tgt2 is None:
                continue
            flight2 = dist2 / speed
            launch2 = launch1 + turnaround
            impact2 = launch2 + flight2
            for _ in range(PASS2_ROUNDS):
                all_events.append({
                    "base": base, "site": tgt2, "munition": mname,
                    "dist_km": dist2, "launch_s": launch2, "impact_s": impact2,
                    "pass_num": 2,
                })
                iaf_hits[tgt2["name"]].append(impact2)

    iaf_site_hits_timeline = {k: sorted(v) for k, v in iaf_hits.items() if v}
    return all_events, iaf_site_hits_timeline


def gen_iaf_kml(iaf_events, site_inactive_at):
    """Return per-munition segment dict and impact placemarks for IAF strikes."""
    segs_by_mun = {m: [] for m in IAF_MUNITIONS}
    impacts     = []

    for ev in sorted(iaf_events, key=lambda e: e["launch_s"]):
        base     = ev["base"]
        site     = ev["site"]
        mname    = ev["munition"]
        mdef     = IAF_MUNITIONS[mname]
        launch_s = ev["launch_s"]
        impact_s = ev["impact_s"]
        dist_km  = ev["dist_km"]
        n_arc    = 12

        pts   = arc_points(base["lon"], base["lat"], site["lon"], site["lat"],
                           mdef["peak_alt_m"], n_arc, mdef["sea_skim"])
        t_pts = [launch_s + (k / n_arc) * (impact_s - launch_s) for k in range(n_arc + 1)]

        style  = safe_id(mname) + "_iaf"
        label  = f"IAF {mname} — {base['name']} → {site['name']}"
        desc   = (f"IAF Strike | {base['aircraft']} | {mname} | "
                  f"{base['name']} → {site['name']} | "
                  f"{dist_km:.0f} km | launch T+{launch_s/60:.1f} min")

        segs_by_mun[mname] += gx_track(style, pts, t_pts, label, desc)

        already_dead = site["name"] in site_inactive_at
        impact_icon  = "dead_icon" if already_dead else "strike_icon"
        impacts.append(
            f'    <Placemark><name>{mname} → {site["name"]}</name>'
            f'<styleUrl>#{impact_icon}</styleUrl>'
            f'<TimeStamp><when>{fmt_time(sim_time(impact_s))}</when></TimeStamp>'
            f'<description>{desc}</description>'
            f'<Point><coordinates>{site["lon"]:.5f},{site["lat"]:.5f},0</coordinates>'
            f'</Point></Placemark>\n'
        )

    return segs_by_mun, impacts


def gen_munition_labels(mnames, dur_s, strike_segs, iaf_segs, sm6_segs):
    """
    Return KML for one size-4 floating text label per active munition type.

    Labels are grouped into three positional columns north of the engagement
    area so they never overlap with trajectories:

      Column A — Iranian offensive munitions   (60 °E, stepping south from 32 °N)
      Column B — US / IAF strike munitions     (47 °E, stepping south from 32 °N)
      Column C — US interceptor categories     (53 °E, stepping south from 32 °N)

    Each label:
      · LabelStyle scale = 4.0, colour matching the munition's track colour
      · No icon  (IconStyle scale = 0)
      · TimeSpan covers the full scenario so labels appear only while the
        engagement is active and vanish after it ends
      · Click opens a popup with speed, altitude, cost, and SSPK data
    """
    t_begin = fmt_time(sim_time(0))
    t_end   = fmt_time(sim_time(dur_s))
    timespan = (f'<TimeSpan>'
                f'<begin>{t_begin}</begin><end>{t_end}</end>'
                f'</TimeSpan>')

    def _label_pm(name, desc_html, lon, lat, kml_color):
        """Emit one size-4 text-only Placemark."""
        return (
            f'  <Placemark>\n'
            f'    <name>{name}</name>\n'
            f'    <description>{desc_html}</description>\n'
            f'    {timespan}\n'
            f'    <Style>\n'
            f'      <IconStyle><scale>0</scale></IconStyle>\n'
            f'      <LabelStyle>'
            f'<color>{kml_color}</color>'
            f'<scale>0.6</scale>'
            f'</LabelStyle>\n'
            f'    </Style>\n'
            f'    <Point><altitudeMode>relativeToGround</altitudeMode>'
            f'<coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point>\n'
            f'  </Placemark>\n'
        )

    out      = []
    LAT_STEP = -0.85   # degrees between successive labels (~95 km)

    # ── Column A: Iranian offensive munitions (60 °E / eastern margin) ───────
    col_a_lon = 60.0
    col_a_lat = 32.0
    row = 0
    for mname in mnames:
        if mname not in MUNITIONS:
            continue
        mdef       = MUNITIONS[mname]
        sspk_entry = MUNITION_SSPK.get(mname, {})
        color      = mdef.get("color", "ffffffff")
        css_color  = _kml_to_css(color)
        spd_kmh    = mdef["speed_km_s"] * 3600
        spd_mach   = mdef["speed_km_s"] / 0.340
        cost_usd   = mdef.get("cost_usd", 0)
        desc = _html_popup(f"\u26a1 {mname}", css_color, [
            ("Speed",          f"Mach {spd_mach:.2f}  ({spd_kmh:,.0f} km/h)", css_color),
            ("Peak altitude",  f"{mdef['peak_alt_m']:,.0f} m",                  _C_DEGRADED),
            ("Sea-skim",       "yes" if mdef.get("sea_skim") else "no",          _C_ACTIVE),
            ("Unit cost",      f"${cost_usd:,.0f}",                              _C_DEGRADED),
            ("Interceptor",    sspk_entry.get("interceptor", "\u2014"),           _C_US_CSG),
            ("SSPK vs US def", f"{sspk_entry.get('sspk', 0) * 100:.0f}%",        _C_INTERCEPT),
            ("Notes",          sspk_entry.get("notes", ""),                       _C_ACTIVE),
        ])
        out.append(_label_pm(mname, desc,
                             col_a_lon, col_a_lat + row * LAT_STEP, color))
        row += 1

    # ── Column B: US / IAF strike munitions (47 °E / western margin) ─────────
    col_b_lon = 47.0
    col_b_lat = 32.0
    row = 0
    all_strike = {**US_STRIKE_MUNITIONS, **IAF_MUNITIONS}
    for mname, mdef in all_strike.items():
        used = bool(
            strike_segs.get(mname) or iaf_segs.get(mname)
        )
        if not used:
            continue
        color     = mdef.get("color", "cc00ff66")
        css_color = _kml_to_css(color)
        spd_kmh   = mdef["speed_km_s"] * 3600
        spd_mach  = mdef["speed_km_s"] / 0.340
        cost_usd  = mdef.get("cost_usd", 0)
        max_rng   = mdef.get("max_range_km", 0)
        desc = _html_popup(f"\u25ce {mname}", css_color, [
            ("Role",          "US / IAF strike munition",                    css_color),
            ("Speed",         f"Mach {spd_mach:.2f}  ({spd_kmh:,.0f} km/h)", _C_ACTIVE),
            ("Peak altitude", f"{mdef['peak_alt_m']:,.0f} m",                 _C_DEGRADED),
            ("Max range",     f"{max_rng:,.0f} km" if max_rng else "\u2014",  _C_ACTIVE),
            ("Unit cost",     f"${cost_usd:,.0f}",                            _C_DEGRADED),
        ])
        out.append(_label_pm(mname, desc,
                             col_b_lon, col_b_lat + row * LAT_STEP, color))
        row += 1

    # ── Column C: US interceptor categories (53 °E / centre-north) ───────────
    col_c_lon = 53.0
    col_c_lat = 32.0
    # AABBGGRR colours matching existing intercept icon styles
    int_meta = {
        "SM-6 / SM-2":         ("ffff8800", "Area-defense SAM; primary fleet intercept system"),
        "CIWS / SeaRAM":       ("ff44ffff", "Close-in weapon system; last-ditch point defense"),
        "Naval Gun / Phalanx": ("ff00ff88", "25 mm / 20 mm Phalanx; cost-effective vs drones"),
    }
    row = 0
    for cat, segs in sm6_segs.items():
        if not segs:
            continue
        color, role = int_meta.get(cat, ("ffffffff", cat))
        css_color   = _kml_to_css(color)
        desc = _html_popup(f"\u25a0 {cat}", css_color, [
            ("Role",    role,               css_color),
            ("Side",    "US Navy / Aegis",  _C_US_CSG),
        ])
        out.append(_label_pm(cat, desc,
                             col_c_lon, col_c_lat + row * LAT_STEP, color))
        row += 1

    return "".join(out)


def gen_csg_tour_flash_markers(csg_fleet, tenth_hit_s):
    """
    Return KML for one hidden Placemark per CSG, positioned where the ship
    sits at its destruction time.  These are initially invisible (visibility=0)
    and are revealed / re-hidden by gx:AnimatedUpdate elements inside the tour
    playlist to produce a visual destruction flash when the tour reaches each
    CSG's death moment.

    IDs follow the pattern  csg_flash_<i>  (0-based, matching fleet order)
    so the tour can target them without needing a string lookup.
    """
    out = []
    for i, csg in enumerate(csg_fleet):
        t_s   = tenth_hit_s.get(csg["name"], 0.0)
        lon, lat = csg_pos_at(csg, t_s)
        out.append(
            f'  <Placemark id="csg_flash_{i}">\n'
            f'    <name>\u26a0 {csg["name"]} \u2014 DESTROYED</name>\n'
            f'    <visibility>0</visibility>\n'
            f'    <styleUrl>#csg_tour_flash</styleUrl>\n'
            f'    <Point><altitudeMode>relativeToGround</altitudeMode>'
            f'<coordinates>{lon:.5f},{lat:.5f},0</coordinates></Point>\n'
            f'  </Placemark>\n'
        )
    return "".join(out)


def gen_tour(tenth_hit_s, dur_s, sc_label, csg_fleet=None, hits_timeline=None):
    """
    Generate a <gx:Tour> element that orbits the Persian Gulf battlespace.

    Pacing:
      - One complete 360° orbit every simulated hour (36 steps × 10°).
      - Each gx:FlyTo embeds a gx:TimeStamp as the FIRST child of its LookAt
        (AbstractView) so Google Earth advances its time slider in lock-step
        with the camera throughout the tour.
      - When a CSG is about to receive its 10th breakthrough hit (T-30 s),
        the camera breaks from the main orbit, zooms into that CSG, orbits
        it for the final 30 simulated seconds, then:
          · a gx:AnimatedUpdate reveals the csg_flash_<i> Placemark (large
            red target icon) precisely at the destruction timestamp, giving
            an unmistakable visual hit flash,
          · a follow-up gx:AnimatedUpdate hides it again before pullback.
      - Intro: top-down descent into tactical view.
      - Outro: wide pullback with a slow final revolution.

    hits_timeline : dict[str, list[float]]
        Maps each CSG name to a sorted list of breakthrough hit timestamps
        (seconds into the simulation).  Used to trigger per-hit flash
        AnimatedUpdates for every breakthrough, not just the 10th.
    """
    CTR_LON, CTR_LAT  = 55.5, 26.5   # mid-Persian Gulf engagement centroid
    ORBIT_RANGE_M     = 780_000       # LookAt range during main orbit
    ORBIT_TILT        = 45            # degrees from vertical (45° gives drama)
    WIDE_RANGE_M      = 2_000_000     # opening / closing wide shot
    CSG_CLOSE_M       =  80_000       # zoom range when circling a hit CSG
    CSG_MID_M         = 250_000       # approach range on the way in
    SECS_PER_HOUR     = 60            # real seconds per simulated hour (1 orbit)
    STEPS_PER_ROT     = 36            # 10° per step → smooth 360°
    DEATH_WATCH_S     = 30            # simulated seconds shown in final orbit
    DEATH_ORBIT_STEPS = 8             # orbit steps during death-watch (8 × 45°)
    DEATH_STEP_DUR    = 1.5           # real seconds per death-watch orbit step

    n_hours   = math.ceil(dur_s / 3600)
    step_dur  = SECS_PER_HOUR / STEPS_PER_ROT   # ~1.67 s per 10° step

    _fleet       = csg_fleet if csg_fleet is not None else US_CSGS
    _hits        = hits_timeline or {}
    # Build a stable name → fleet-index map so AnimatedUpdate can reference
    # the csg_flash_<i> Placemarks generated by gen_csg_tour_flash_markers().
    _csg_idx     = {c["name"]: i for i, c in enumerate(_fleet)}

    def _fly(lon, lat, range_m, tilt, heading, duration, mode="smooth", t_sim_s=None):
        """Emit a gx:FlyTo with gx:TimeStamp as the first child of LookAt
        (AbstractView) so GE advances its time slider to t_sim_s when the
        camera arrives.  Newlines inside LookAt ensure GE parses the timestamp
        child correctly regardless of parser strictness."""
        if t_sim_s is not None:
            ts       = fmt_time(sim_time(max(0.0, t_sim_s)))
            view_body = (
                f'\n        <gx:TimeStamp><when>{ts}</when></gx:TimeStamp>'
                f'\n        <longitude>{lon:.5f}</longitude>'
                f'\n        <latitude>{lat:.5f}</latitude>'
                f'\n        <altitude>0</altitude>'
                f'\n        <range>{range_m:.0f}</range>'
                f'\n        <tilt>{tilt:.1f}</tilt>'
                f'\n        <heading>{heading:.1f}</heading>'
                f'\n        <altitudeMode>relativeToGround</altitudeMode>'
                f'\n      '
            )
        else:
            view_body = (
                f'\n        <longitude>{lon:.5f}</longitude>'
                f'\n        <latitude>{lat:.5f}</latitude>'
                f'\n        <altitude>0</altitude>'
                f'\n        <range>{range_m:.0f}</range>'
                f'\n        <tilt>{tilt:.1f}</tilt>'
                f'\n        <heading>{heading:.1f}</heading>'
                f'\n        <altitudeMode>relativeToGround</altitudeMode>'
                f'\n      '
            )
        return (
            f'      <gx:FlyTo>\n'
            f'        <gx:duration>{duration:.2f}</gx:duration>\n'
            f'        <gx:flyToMode>{mode}</gx:flyToMode>\n'
            f'        <LookAt>{view_body}</LookAt>\n'
            f'      </gx:FlyTo>\n'
        )

    def _wait(sec):
        return f'      <gx:Wait><gx:duration>{sec:.2f}</gx:duration></gx:Wait>\n'

    def _show_flash(csg_name, anim_dur=0.5):
        """gx:AnimatedUpdate: reveal the csg_flash_<i> Placemark for this CSG."""
        idx = _csg_idx.get(csg_name)
        if idx is None:
            return ""
        return (
            f'      <gx:AnimatedUpdate>\n'
            f'        <gx:duration>{anim_dur:.2f}</gx:duration>\n'
            f'        <Update><targetHref/><Change>'
            f'<Placemark targetId="csg_flash_{idx}">'
            f'<visibility>1</visibility>'
            f'</Placemark>'
            f'</Change></Update>\n'
            f'      </gx:AnimatedUpdate>\n'
        )

    def _hide_flash(csg_name, anim_dur=0.3):
        """gx:AnimatedUpdate: hide the csg_flash_<i> Placemark for this CSG."""
        idx = _csg_idx.get(csg_name)
        if idx is None:
            return ""
        return (
            f'      <gx:AnimatedUpdate>\n'
            f'        <gx:duration>{anim_dur:.2f}</gx:duration>\n'
            f'        <Update><targetHref/><Change>'
            f'<Placemark targetId="csg_flash_{idx}">'
            f'<visibility>0</visibility>'
            f'</Placemark>'
            f'</Change></Update>\n'
            f'      </gx:AnimatedUpdate>\n'
        )

    pl = []   # playlist elements

    # ── Intro: fall from orbit into tactical view (time slider at T=0) ────────
    pl.append(_fly(CTR_LON, CTR_LAT, 3_500_000, 0,  0, 5.0, "bounce", t_sim_s=0))
    pl.append(_wait(1.0))
    pl.append(_fly(CTR_LON, CTR_LAT, ORBIT_RANGE_M, ORBIT_TILT, 0, 5.0, t_sim_s=0))
    pl.append(_wait(1.5))

    current_heading = 0.0

    # Pre-compute which CSGs enter their death-watch during which simulated second,
    # so we can interrupt the orbit at the right moment.
    # death_watch_start_s[csg_name] = tenth_hit_s - DEATH_WATCH_S
    death_watch_start = {nm: max(0.0, ts - DEATH_WATCH_S)
                         for nm, ts in tenth_hit_s.items()}

    # Track which CSGs have already had their death-watch rendered.
    rendered_death = set()

    # ── Main loop: one 360° rotation per simulated hour ──────────────────────
    for hour in range(n_hours):
        t_start = hour * 3600.0
        t_end   = min((hour + 1) * 3600.0, dur_s)
        sim_dur = t_end - t_start   # may be <3600 on final hour

        # Complete one full 360° orbit for this simulated hour.
        # Each step carries a gx:TimeStamp inside its LookAt so the slider
        # advances proportionally as the camera orbits.
        # After each step, check if any CSG received a non-fatal breakthrough
        # hit in that step's time window and insert a brief gx:AnimatedUpdate
        # flash so the viewer sees a visual impact pulse on the icon.
        for step in range(STEPS_PER_ROT):
            h      = (current_heading + step * 10.0) % 360.0
            t_sim  = t_start + (step / STEPS_PER_ROT) * sim_dur
            t_next = t_start + ((step + 1) / STEPS_PER_ROT) * sim_dur
            pl.append(_fly(CTR_LON, CTR_LAT, ORBIT_RANGE_M, ORBIT_TILT,
                           h, step_dur, t_sim_s=t_sim))

            # Brief flash for each non-final hit that falls in this step's window
            for csg in _fleet:
                if csg["name"] in rendered_death:
                    continue
                destroy_t = tenth_hit_s.get(csg["name"])
                for hit_t in _hits.get(csg["name"], []):
                    if t_sim <= hit_t < t_next and hit_t != destroy_t:
                        pl.append(_show_flash(csg["name"], anim_dur=0.2))
                        pl.append(_wait(0.35))
                        pl.append(_hide_flash(csg["name"], anim_dur=0.15))

        current_heading = (current_heading + 360.0) % 360.0

        # ── Death-watch: CSGs whose 10th hit falls within this simulated hour ─
        # Sort by destruction time so we handle them in chronological order.
        pending = sorted(
            [(ts, nm) for nm, ts in tenth_hit_s.items()
             if t_start <= ts < t_end and nm not in rendered_death],
            key=lambda x: x[0]
        )

        for destruction_s, csg_name in pending:
            rendered_death.add(csg_name)
            csg = next((c for c in _fleet if c["name"] == csg_name), None)
            if csg is None:
                continue

            watch_start_s = death_watch_start[csg_name]   # T - 30 s

            # CSG's actual position 30 s before destruction (ships move slowly
            # but csg_pos_at gives the precise point on the track).
            approach_lon, approach_lat = csg_pos_at(csg, watch_start_s)
            approach_hdg = (current_heading + 60.0) % 360.0

            # Wide approach: time slider set to T-30 s via LookAt TimeStamp
            pl.append(_fly(approach_lon, approach_lat, CSG_MID_M, 38,
                           approach_hdg, 4.0, t_sim_s=watch_start_s))
            pl.append(_wait(0.5))
            # Zoom in close; slider advances to T-28 s
            pl.append(_fly(approach_lon, approach_lat, CSG_CLOSE_M, 65,
                           approach_hdg, 2.5, t_sim_s=watch_start_s + 2))
            pl.append(_wait(0.5))

            # Death-watch orbit: 8 × 45° steps, time advances from T-28 to T+2
            total_death_sim_s = DEATH_WATCH_S + 2      # 32 simulated seconds total
            for q in range(DEATH_ORBIT_STEPS):
                qh = (approach_hdg + q * 45.0) % 360.0
                # Position at each step (ship may drift slightly)
                step_t = watch_start_s + 2 + (q / DEATH_ORBIT_STEPS) * total_death_sim_s
                step_lon, step_lat = csg_pos_at(csg, step_t)
                pl.append(_fly(step_lon, step_lat, CSG_CLOSE_M, 68, qh,
                               DEATH_STEP_DUR, t_sim_s=step_t))

            # ── DESTRUCTION MOMENT: flash the CSG icon red ────────────────────
            # AnimatedUpdate reveals the csg_flash_<i> Placemark (large red
            # target icon) at exactly the destruction timestamp, providing
            # an unmistakable visual signal that the CSG has been destroyed.
            final_lon, final_lat = csg_pos_at(csg, destruction_s)
            pl.append(_fly(final_lon, final_lat, CSG_CLOSE_M, 72,
                           approach_hdg, 1.5, t_sim_s=destruction_s))
            pl.append(_show_flash(csg_name, anim_dur=0.8))
            pl.append(_wait(2.5))   # hold on the destroyed CSG
            pl.append(_hide_flash(csg_name, anim_dur=0.4))
            pl.append(_wait(0.3))

            # Pull back to main orbit; slider reset to end of this simulated hour
            pl.append(_fly(CTR_LON, CTR_LAT, ORBIT_RANGE_M, ORBIT_TILT,
                           current_heading, 5.0, t_sim_s=t_end))
            pl.append(_wait(0.5))

    # ── Outro: wide pullback + slow final revolution ──────────────────────────
    pl.append(_fly(CTR_LON, CTR_LAT, WIDE_RANGE_M, 20, current_heading, 5.0,
                   "bounce", t_sim_s=dur_s))
    pl.append(_wait(2.0))
    for step in range(12):   # 12 × 30° = one slow final orbit at wide view
        h = (current_heading + step * 30.0) % 360.0
        pl.append(_fly(CTR_LON, CTR_LAT, WIDE_RANGE_M, 18, h, 2.5, t_sim_s=dur_s))
    pl.append(_wait(2.0))

    total_real_s = n_hours * SECS_PER_HOUR + len(tenth_hit_s) * 20
    return (
        f'  <gx:Tour>\n'
        f'    <name>Battle Tour \u2014 {sc_label}</name>\n'
        f'    <description>'
        f'Camera orbits the Persian Gulf once per simulated hour. '
        f'gx:TimeStamp inside each LookAt (AbstractView) advances the time '
        f'slider in lock-step with the camera. '
        f'When a CSG reaches its 10th breakthrough hit the camera zooms in, '
        f'a gx:AnimatedUpdate flashes the destroyed-CSG icon, then the '
        f'camera pulls back to resume the orbit. '
        f'Playback: ~{total_real_s // 60} min {total_real_s % 60} s.'
        f'</description>\n'
        f'    <gx:Playlist>\n'
        + ''.join(pl) +
        f'    </gx:Playlist>\n'
        f'  </gx:Tour>\n'
    )


class CSGDefenseState:
    """
    Tracks per-CSG weapon magazine and resolves intercept attempts.

    Magazine is drawn once at scenario start from each ship's low/high bounds,
    giving organic inventory variation between runs.  Weapon tier is selected by
    cascade (SM-6 → SM-2 → ESSM → RAM → CIWS) subject to range and inventory.
    CIWS and Naval Gun are modelled as effectively unlimited (high-rate guns).
    """

    def __init__(self, csg, rng):
        self.name  = csg["name"]
        self.sm6   = rng.randint(csg["sm6_low"],  csg["sm6_high"])
        self.sm2   = rng.randint(csg["sm2_low"],  csg["sm2_high"])
        self.essm  = rng.randint(csg["essm_low"], csg["essm_high"])
        self.ram   = rng.randint(csg["ram_low"],  csg["ram_high"])
        # CIWS and Naval Gun have large capacity — modelled as unlimited
        self.shots = {"SM-6": 0, "SM-2": 0, "ESSM": 0,
                      "RAM": 0, "CIWS": 0, "NAVAL_GUN": 0}

    def select_weapon(self, dist_km, forced_style=None):
        """
        Return (weapon_tier, kml_style_id, category_label) for this engagement,
        or (None, None, None) if no weapon is available/in-range.
        forced_style: "us_ciws" → drone family; "us_naval_gun" → surface vessel.
        """
        if forced_style == "us_naval_gun":
            if dist_km <= 5.0:
                return "NAVAL_GUN", "us_naval_gun", "Naval Gun / Phalanx"
            if dist_km <= 15.0 and self.ram > 0:
                return "RAM", "us_naval_gun", "Naval Gun / Phalanx"
            return None, None, None

        if forced_style == "us_ciws":
            # Drone family: RAM primary, CIWS last-resort, ESSM close-range fallback
            if dist_km <= 15.0 and self.ram > 0:
                return "RAM", "us_ciws", "CIWS / SeaRAM"
            if dist_km <= 2.0:
                return "CIWS", "us_ciws", "CIWS / SeaRAM"
            if dist_km <= 50.0 and self.essm > 0:
                return "ESSM", "us_ciws", "CIWS / SeaRAM"
            return None, None, None

        # Standard cascade: SM-6 → SM-2 → ESSM → RAM → CIWS
        if dist_km <= 240.0 and self.sm6 > 0:
            return "SM-6",  "us_hi",  "SM-6 / SM-2"
        if dist_km <= 167.0 and self.sm2 > 0:
            return "SM-2",  "us_mid", "SM-6 / SM-2"
        if dist_km <= 50.0  and self.essm > 0:
            return "ESSM",  "us_lo",  "SM-6 / SM-2"
        if dist_km <= 15.0  and self.ram > 0:
            return "RAM",   "us_lo",  "SM-6 / SM-2"
        if dist_km <= 2.0:
            return "CIWS",  "us_lo",  "SM-6 / SM-2"
        return None, None, None

    def fire(self, weapon, shots=1):
        """Decrement finite magazine and record shot count.
        shots: rounds consumed this engagement (2 for ballistics/supersonic, 1 otherwise)."""
        self.shots[weapon] = self.shots.get(weapon, 0) + shots
        if   weapon == "SM-6":  self.sm6  = max(0, self.sm6  - shots)
        elif weapon == "SM-2":  self.sm2  = max(0, self.sm2  - shots)
        elif weapon == "ESSM":  self.essm = max(0, self.essm - shots)
        elif weapon == "RAM":   self.ram  = max(0, self.ram  - shots)

    def summary(self):
        return {k: v for k, v in self.shots.items() if v > 0}


def generate_scenario(scenario_key, seed=42, out_dir=None):
    """
    Generate a complete KML simulation for one named scenario.

    Parameters
    ----------
    scenario_key : str
        Key into the SCENARIOS dict (e.g. "low", "realistic", "iran_best").
    seed : int
        RNG seed for full reproducibility.  Different seeds produce different
        individual missile assignments but preserve aggregate statistics.

    Returns
    -------
    kml : str
        Complete KML document string ready to write to disk.
    actual_launched : int
        Number of Iranian munitions that actually reached flight
        (n_missiles minus those suppressed by site inactivation).
    actual_intercepted : int
        Number of those munitions that were killed by US/coalition systems.
    actual_breakthrough : int
        Number that penetrated to fleet engagement range (hits).
    dur_min : float
        Simulation duration in minutes (time of last event).
    costs : dict
        Full cost-accounting dict (keys: iran_cost, us_intercept_cost,
        us_ship_damage, total_us_cost, exchange_ratio, csg_breakdown, …).
    """
    rng = random.Random(seed)
    # Load the full scenario configuration dict for this key.
    scenario_config = SCENARIOS[scenario_key]

    n_missiles      = scenario_config["n_missiles"]
    munitions       = scenario_config["munitions"]
    wave_s          = scenario_config["wave_s"]
    n_arc           = scenario_config["n_arc"]
    n_arc_intercept = scenario_config["n_sm6"]   # arc segments for interceptor track rendering
    csg_fleet       = scenario_config.get("csg_fleet", US_CSGS)

    # Phased launch timing (defaults keep backward-compat for scenarios A–F)
    # Drones (Shahed-136, IRGCN Sea Drone) launch in phase 1; all others in phase 2.
    DRONE_TYPES  = {"Shahed-136", "IRGCN Sea Drone"}
    phase1_end   = scenario_config.get("phase1_end_s",   wave_s)  # end of drone launch window
    phase2_start = scenario_config.get("phase2_start_s", 0)        # start of missile launch window
    phase2_dur   = scenario_config.get("phase2_dur_s",   wave_s)  # duration of missile launch window

    # Scenario-level site and threshold overrides (caves scenario uses CAVE_SITES + 2-hit threshold)
    _sc_sites     = scenario_config.get("custom_sites", IRAN_SITES)
    _sc_threshold = scenario_config.get("site_hits_to_destroy", SITE_INACTIVATION_THRESHOLD)

    # ================================================================
    # PHASE 0 — US counterstrikes and IAF strikes
    #
    # WHY FIRST: The RNG sequence must be consumed in a fixed order so that
    # every run with the same seed produces identical results.  US/IAF strike
    # events are generated BEFORE any Iranian missile events so their RNG
    # consumption is deterministic regardless of how many missiles are
    # eventually launched.  site_inactive_at (dict: site_name → impact_s)
    # is computed here and used in Phase 1 to suppress launches from sites
    # that are destroyed before a missile would take off.
    # ================================================================
    strike_events, site_inactive_at, site_hits_timeline = compute_us_strikes(
        scenario_key, rng, sites=_sc_sites, threshold=_sc_threshold)
    iaf_events, iaf_site_hits = compute_iaf_strikes(
        scenario_key, rng, site_inactive_at, sites=_sc_sites, threshold=_sc_threshold)

    # Merge IAF hits into site_hits_timeline and recompute site_inactive_at
    for sname, times in iaf_site_hits.items():
        merged = sorted(site_hits_timeline.get(sname, []) + times)
        site_hits_timeline[sname] = merged
        if len(merged) >= _sc_threshold:
            site_inactive_at[sname] = merged[_sc_threshold - 1]

    # Initialise per-CSG magazine-aware defense states (hybrid Monte Carlo / ABM).
    # Magazine draws are done here — before the Phase 1 launch loop — so that
    # every ship starts the battle with its full organic inventory.
    csg_states = {c["name"]: CSGDefenseState(c, rng) for c in csg_fleet}

    # Per-CSG Aegis simultaneous engagement cap: maximum SM-6/SM-2 guidance channels
    # active at one time.  AN/SPY-1D(V) Baseline 9 IPDS: ~18 simultaneous engagements.
    # Source: NAVSEA Aegis BMD 6.3 brief; Congressional testimony 2023.
    _AEGIS_SIMUL_CAP = 18
    _aegis_window_s  = 30.0   # engagement window: intercepts within 30 s overlap
    # _csg_active_engagements[csg_name] = sorted list of (intercept_time_s,) for SM-6/SM-2 so far
    _csg_active_eng  = {c["name"]: [] for c in csg_fleet}

    # Generate 10-ship formations for each CSG (2 RNG calls per ship × 10 ships × 8 CSGs).
    csg_ships        = {}
    for c in csg_fleet:
        csg_ships[c["name"]] = generate_csg_ships(c, rng)
    ship_destroyed_at = {}   # ship_id → destruction time_s
    group_stopped_at  = {}   # (csg_name, group_name) → stop time_s

    # focused_salvo: all Iranian fire directed at a single named CSG
    _focus_name   = scenario_config.get("focus_csg")
    _focus_csg    = next((c for c in US_CSGS if c["name"] == _focus_name), None)

    # drone_focus_csg: directs all DRONE_TYPE munitions to a specific named CSG
    _drone_focus_name = scenario_config.get("drone_focus_csg")
    _drone_focus_csg  = next((c for c in csg_fleet if c["name"] == _drone_focus_name), None) if _drone_focus_name else None

    # ballistic_targets: restricts ballistic (non-drone) targeting to a named subset
    _ballistic_target_names = scenario_config.get("ballistic_targets")
    _ballistic_fleet = [c for c in csg_fleet if c["name"] in _ballistic_target_names] \
        if _ballistic_target_names else csg_fleet
    if not _ballistic_fleet:
        _ballistic_fleet = csg_fleet

    # Per-munition collections for nested folder output
    _mnames       = [m["name"] for m in scenario_config["munitions"]]
    missile_segs  = {mn: [] for mn in _mnames}
    intercept_pts = {mn: [] for mn in _mnames}
    impact_pts    = {mn: [] for mn in _mnames}
    cep_circles   = {mn: [] for mn in _mnames}   # in-flight CEP polygons (ballistic only)
    sm6_segs      = {"SM-6 / SM-2": [], "CIWS / SeaRAM": [], "Naval Gun / Phalanx": []}
    latest_s      = 0.0

    # ================================================================
    # PHASE 1 — Pre-simulate every missile (two-pass design)
    #
    # WHY TWO PASSES: We need the complete hit timeline (pass 1) before we can
    # render any KML geometry (pass 2 / Phase 3), because:
    #   a) first_hit_s and tenth_hit_s per CSG determine when defense rings
    #      switch from "active" to "degraded" KML styles.
    #   b) csg_neut_s (neutralization time) gates whether a CSG can even fire
    #      its interceptor during Phase 3 — neutralized CSGs don't intercept.
    # Pass 1 (this loop): assign mname, site, launch/flight times, intercept
    #   status, and AI flags for every missile and store in `events[]`.
    # Pass 2 (Phase 3): iterate events[] again to emit KML strings.
    # ================================================================
    site_pools = {}
    for m in munitions:
        mn   = m["name"]
        mdef = MUNITIONS[mn]
        allowed    = mdef.get("sites")
        max_rng_km = mdef.get("max_range_km")
        if allowed:
            pool = [s for s in _sc_sites if s["name"] in allowed]
        else:
            pool = _sc_sites
        # Filter sites beyond the munition's operational radius (if defined).
        # Use min distance to any CSG so a site is kept if it can reach at least one target.
        if max_rng_km is not None:
            pool = [s for s in pool
                    if min(haversine_km(s["lon"], s["lat"], c["lon"], c["lat"])
                           for c in csg_fleet) <= max_rng_km]
        if not pool:
            pool = _sc_sites  # fallback: never starve a munition of launch sites
        site_pools[mn] = pool

    _israel_waves    = scenario_config.get("israel_drone_alternation", 0)
    n_israel_diverted = 0

    events = []
    for i in range(n_missiles):
        mname = weighted_choice(munitions, rng)["name"]
        mdef  = MUNITIONS[mname]
        _csg_roll = rng.choice(csg_fleet)   # always consume one RNG call (keeps sequence deterministic)
        if _focus_csg:
            csg = _focus_csg
        elif _drone_focus_csg and mname in DRONE_TYPES:
            csg = _drone_focus_csg
        elif _ballistic_target_names and mname not in DRONE_TYPES and _csg_roll["name"] not in _ballistic_target_names:
            # Redirect ballistic munitions that rolled an excluded CSG to a valid target
            csg = _ballistic_fleet[csg_fleet.index(_csg_roll) % len(_ballistic_fleet)]
        else:
            csg = _csg_roll

        # Generate launch time
        if scenario_config.get("iran_detection_launch"):
            # Iran fires everything simultaneously on IAF radar detection —
            # no phase separation between drones and missiles.
            # All launches compressed into a short window so every site fires
            # before a single US/IAF munition lands (~45-90 min flight time).
            _iw = scenario_config.get("iran_launch_window_s", 1800)
            launch_s = rng.uniform(0, _iw)
        elif mname in DRONE_TYPES:
            launch_s = rng.uniform(0, phase1_end)
        else:
            launch_s = rng.uniform(phase2_start, phase2_start + phase2_dur)

        # ── Israel wave alternation ───────────────────────────────────────────
        # If israel_drone_alternation > 0, the Shahed-136 phase-1 window is
        # divided into N equal sub-windows alternating Gulf / Israel / Gulf / …
        # Odd-indexed sub-windows are Israel-bound (diverted; not modelled here).
        # IRGCN Sea Drones are excluded — they cannot reach Israel at ~2,200 km.
        if (_israel_waves > 0
                and mname == "Shahed-136"
                and not scenario_config.get("iran_detection_launch")):
            _wdur = phase1_end / _israel_waves
            _widx = int(launch_s / _wdur) if _wdur > 0 else 0
            if _widx % 2 == 1:          # Israel-bound — skip Gulf simulation
                n_israel_diverted += 1
                _ = rng.random()                # would-be site choice (mirrors rng.choice)
                _ = rng.uniform(-0.25, 0.25)   # tgt_lon jitter
                _ = rng.uniform(-0.25, 0.25)   # tgt_lat jitter
                _ = rng.uniform(0.88, 1.12)    # peak jitter
                _ai_roll = rng.random()         # AI roll
                if _ai_roll < AI_SHAHED_FRACTION:
                    _ = rng.uniform(-0.05, 0.05)  # ai_tgt_lon (consumed even when diverted)
                    _ = rng.uniform(-0.05, 0.05)  # ai_tgt_lat
                # Always consume intercept RNG slots to preserve downstream sequence
                _lo, _hi = MUNITIONS["Shahed-136"].get("t_int_range", (0.70, 0.92))
                _ = rng.uniform(_lo, _hi)       # t_int_frac slot
                _rlo, _rhi = MUNITIONS["Shahed-136"].get("react_range", (60, 90))
                _ = rng.uniform(_rlo, _rhi)     # react_s slot
                _ = rng.random()                # Pk Bernoulli slot
                events.append(None)
                continue

        # Filter site pool: only use sites that are still active at launch_s,
        # and (if the munition has max_range_km) within operational range of the target CSG.
        full_pool = site_pools[mname]
        _max_rng_km = mdef.get("max_range_km")
        active_pool = [s for s in full_pool
                       if site_inactive_at.get(s["name"], float("inf")) > launch_s
                       and (_max_rng_km is None or
                            haversine_km(s["lon"], s["lat"], csg["lon"], csg["lat"]) <= _max_rng_km)]
        if not active_pool:
            # All allowed sites destroyed — consume RNG consistently to preserve sequence
            _ = rng.random()                # would-be site choice
            _ = rng.uniform(-0.25, 0.25)   # tgt_lon jitter
            _ = rng.uniform(-0.25, 0.25)   # tgt_lat jitter
            _ = rng.uniform(0.88, 1.12)    # peak jitter
            _ = rng.random()               # AI roll
            # Always consume intercept RNG slots to preserve downstream sequence
            _ = rng.random()               # t_int_frac slot
            _ = rng.uniform(60, 90)        # react_s slot
            _ = rng.random()               # Pk Bernoulli slot
            events.append(None)
            continue

        site    = rng.choice(active_pool)
        # Lead-target: estimate impact time from site to CSG center
        _est_dist   = haversine_km(site["lon"], site["lat"], csg["lon"], csg["lat"])
        _est_impact = launch_s + _est_dist / mdef["speed_km_s"]

        # Select a specific ship in the CSG as the aiming point (1 RNG call)
        _active_ships = [s for s in csg_ships[csg["name"]]
                         if s["id"] not in ship_destroyed_at]
        if not _active_ships:
            _active_ships = csg_ships[csg["name"]]
        _tgt_ship   = rng.choice(_active_ships)
        _ts_lon, _ts_lat = ship_pos_at(csg, _tgt_ship, _est_impact)

        # Apply CEP scatter (Box-Muller — always exactly 2 rng.random() calls)
        _cep_m  = MUNITION_CEP_M.get(mname, 200.0)
        _sig_m  = _cep_m / (2.0 * math.sqrt(math.log(2.0)))
        _z0, _z1 = _box_muller_rng(rng)
        _sig_lat = _sig_m / 111_000.0
        _sig_lon = _sig_m / (111_000.0 * math.cos(math.radians(_ts_lat)))
        tgt_lon  = _ts_lon + _z0 * _sig_lon
        tgt_lat  = _ts_lat + _z1 * _sig_lat

        dist_km  = haversine_km(site["lon"], site["lat"], tgt_lon, tgt_lat)
        flight_s = dist_km / mdef["speed_km_s"]
        peak     = mdef["peak_alt_m"] * rng.uniform(0.88, 1.12)

        # AI/computer-vision terminal guidance: 1% of Shahed-136 only.
        # Always consumes one RNG call per event to keep sequence deterministic.
        is_ai = (mname == "Shahed-136" and rng.random() < AI_SHAHED_FRACTION)
        if is_ai:
            # Tighter terminal lock-on: ±0.05° vs normal ±0.25° scatter
            _ai_impact = launch_s + flight_s
            _ai_lon, _ai_lat = csg_pos_at(csg, _ai_impact)
            ai_tgt_lon = _ai_lon + rng.uniform(-0.05, 0.05)
            ai_tgt_lat = _ai_lat + rng.uniform(-0.05, 0.05)
        else:
            ai_tgt_lon = tgt_lon
            ai_tgt_lat = tgt_lat

        # ── Magazine-aware intercept resolution (hybrid Monte Carlo / ABM) ──────
        # Three RNG slots always consumed (Pk trial, t_int_frac, react_s) so the
        # downstream RNG sequence is deterministic regardless of intercept outcome.
        # Pk is looked up from ENGAGEMENT_PK[weapon_tier][mname]; if no weapon is
        # available or in-range, Pk = 0 and the munition always breaks through.
        _forced       = mdef.get("interceptor_style")          # "us_ciws" / "us_naval_gun" / None
        _state        = csg_states[csg["name"]]
        weapon_tier, int_style_ev, interceptor_category_ev = \
            _state.select_weapon(dist_km, _forced)
        # ── Aegis simultaneous engagement saturation check ────────────────────
        # SM-6 and SM-2 require a dedicated SPY-1D fire-control channel.
        # Baseline 9 IPDS cap: ~18 concurrent engagements per CSG.
        # If saturated, SM-6/SM-2 engagement is denied; ESSM/RAM/CIWS unaffected.
        if weapon_tier in ("SM-6", "SM-2"):
            _proj_int_s = launch_s + flight_s * 0.70
            _active_now = sum(1 for t in _csg_active_eng[csg["name"]]
                              if abs(t - _proj_int_s) <= _aegis_window_s)
            if _active_now >= _AEGIS_SIMUL_CAP:
                weapon_tier, int_style_ev, interceptor_category_ev = None, None, None
            else:
                _csg_active_eng[csg["name"]].append(_proj_int_s)
        _sspk         = ENGAGEMENT_PK.get(weapon_tier, {}).get(mname, 0.0) if weapon_tier else 0.0
        _eng_shots    = _SHOTS_PER_ENGAGEMENT.get(mname, 1)     # rounds per engagement (1 or 2)
        # Two-shot engagement Pk: 1-(1-SSPK)^shots (simultaneous salvo doctrine for ballistics)
        _pk           = 1.0 - (1.0 - _sspk) ** _eng_shots if _sspk > 0.0 else 0.0
        _pk_roll      = rng.random()                            # Pk Bernoulli slot (always consumed)
        lo, hi        = mdef.get("t_int_range",
                                  (0.92, 0.99) if mdef["sea_skim"] else (0.55, 0.85))
        t_int_frac    = rng.uniform(lo, hi)                     # t_int_frac slot (always consumed)
        rlo, rhi      = mdef.get("react_range", (60, 90))
        react_s       = rng.uniform(rlo, rhi)                   # react_s slot (always consumed)
        is_int        = weapon_tier is not None and not is_ai and _pk_roll < _pk
        if is_int:
            _state.fire(weapon_tier, shots=_eng_shots)
        elif weapon_tier is not None and not is_ai:
            # Miss: rounds still expended (both fired regardless of outcome per SLS doctrine)
            _state.fire(weapon_tier, shots=_eng_shots)
        else:
            t_int_frac             = None
            react_s                = None
            weapon_tier            = None
            int_style_ev           = None
            interceptor_category_ev = None
        # ── 20 m ship-hit proximity check ────────────────────────────────────
        # Check whether the impact point falls within _SHIP_HIT_RADIUS_M of any
        # ship in the target CSG at the computed impact time.  AI drones that
        # break through are guaranteed hits (they lock onto a specific hull).
        _impact_time_s = launch_s + flight_s
        _hit_ship_id   = None
        if not is_int:
            if is_ai:
                # AI Shahed has EO/IR terminal lock — guaranteed hit on nearest ship
                _best_d = float("inf")
                for _sh in csg_ships[csg["name"]]:
                    _slon, _slat = ship_pos_at(csg, _sh, _impact_time_s)
                    _dm = haversine_km(ai_tgt_lon, ai_tgt_lat, _slon, _slat) * 1000.0
                    if _dm < _best_d:
                        _best_d, _hit_ship_id = _dm, _sh["id"]
            else:
                for _sh in csg_ships[csg["name"]]:
                    _slon, _slat = ship_pos_at(csg, _sh, _impact_time_s)
                    _dm = haversine_km(tgt_lon, tgt_lat, _slon, _slat) * 1000.0
                    if _dm <= _SHIP_HIT_RADIUS_M:
                        _hit_ship_id = _sh["id"]
                        break

        # Distance-based lock-on fraction: fraction of flight before sensor acquisition.
        # AI Shahed uses EO/IR camera; IRGCN uses surface search radar.
        # lock_frac = fraction of arc flown before lock-on (rest is guided terminal).
        _lock_range = SHAHED_AI_LOCK_KM if is_ai else mdef.get("lock_on_range_km")
        if _lock_range is not None:
            if is_ai:
                # AI Shahed: keep a minimum approach fraction so the orange arc is visible
                lock_frac = max(0.05, 1.0 - _lock_range / max(dist_km, _lock_range + 1.0))
            else:
                # IRGCN Sea Drone: 0.0 when already within sensor range at launch —
                # boat goes direct with full radar-lock styling from the start
                lock_frac = max(0.0, 1.0 - _lock_range / max(dist_km, 1.0))
        else:
            lock_frac = None

        events.append({
            "i": i, "mname": mname, "mdef": mdef, "site": site, "csg": csg,
            "tgt_lon": tgt_lon, "tgt_lat": tgt_lat, "dist_km": dist_km,
            "flight_s": flight_s, "launch_s": launch_s, "peak": peak,
            "is_int": is_int, "t_int_frac": t_int_frac, "react_s": react_s,
            "is_ai": is_ai, "ai_tgt_lon": ai_tgt_lon, "ai_tgt_lat": ai_tgt_lat,
            "lock_frac": lock_frac,
            "int_style_ev": int_style_ev,
            "interceptor_category_ev": interceptor_category_ev,
            "hit_ship_id": _hit_ship_id,
            "impact_time_s": _impact_time_s,
        })

    # Remove suppressed (None) entries
    events = [e for e in events if e is not None]
    actual_launched = len(events)

    # ── Resolve ship destruction in impact-time order ─────────────────────────
    # Process breakthrough hits chronologically so earlier impacts drive group-stop
    # before later missiles select their target ship.
    _hit_events = sorted(
        [e for e in events if not e["is_int"] and e.get("hit_ship_id")],
        key=lambda e: e["impact_time_s"]
    )
    for _hev in _hit_events:
        _hsid = _hev["hit_ship_id"]
        if _hsid not in ship_destroyed_at:
            ship_destroyed_at[_hsid] = _hev["impact_time_s"]
            # Stop all ships in the same directional group
            _cn = _hev["csg"]["name"]
            for _sh in csg_ships[_cn]:
                if _sh["id"] == _hsid:
                    _gkey = (_cn, _sh["group"])
                    if _gkey not in group_stopped_at:
                        group_stopped_at[_gkey] = _hev["impact_time_s"]
                    break

    # ================================================================
    # PHASE 2 — Build per-CSG sorted hit timeline
    #
    # WHY THIS PASS IS NEEDED: KML defense-ring polygons switch style (active →
    # degraded → neutralized) at exact wall-clock timestamps.  Those timestamps
    # are first_hit_s (first breakthrough impact) and tenth_hit_s (tenth impact,
    # which triggers neutralization styling).  We must compute them from the full
    # events[] list before we start emitting any KML in Phase 3, because Phase 3
    # needs to look up both values for every event it processes.
    # ================================================================
    hits_timeline = {c["name"]: [] for c in csg_fleet}
    for ev in events:
        # Only effective hits (landed within 20 m of a ship hull) count toward
        # neutralisation.  AI-guided Shahed drones are always hull-hits.
        if not ev["is_int"] and ev.get("hit_ship_id"):
            hits_timeline[ev["csg"]["name"]].append(ev["launch_s"] + ev["flight_s"])
    for name in hits_timeline:
        hits_timeline[name].sort()

    # first_hit_s: maps CSG name → time-of-first-breakthrough (seconds into simulation)
    # tenth_hit_s: maps CSG name → time-of-tenth-breakthrough (neutralization threshold)
    first_hit_s = {n: times[0]  for n, times in hits_timeline.items() if times}
    tenth_hit_s = {n: times[9]  for n, times in hits_timeline.items() if len(times) >= 10}

    # ================================================================
    # PHASE 3 — Generate Iranian missile KML
    #
    # RENDERING STRATEGY: Each event in events[] produces one or more gx:Track
    # Placemarks, categorised into three visual outcomes:
    #   1. INTERCEPTED  — missile arc shown up to kill point; blue interceptor arc
    #                     added from firing ship position to intercept point.
    #   2. AI BREAKTHROUGH — orange approach arc (dead-reckoning) + brighter orange
    #                        terminal arc (EO/IR lock-on redirect); no interceptor.
    #   3. IRGCN SEA DRONE — amber transit arc + red-orange radar-lock terminal arc.
    #   4. NORMAL BREAKTHROUGH — full-arc in bright bt color; impact marker placed.
    # All arcs use gx:Track with per-waypoint TimeSpan so they animate correctly
    # on the Google Earth timeline slider.  Intercept arcs use the n_sm6 segment
    # count rather than the munition's n_arc_override, so they are always smooth.
    # ================================================================
    for ev in events:
        i        = ev["i"]
        mname    = ev["mname"]
        mdef     = ev["mdef"]
        site     = ev["site"]
        # Label ~15% of munitions (every 7th) at scale 0.6 with munition color; others unlabelled.
        _lbl = "_labeled" if (i % 7 == 0) else ""
        # All munitions use relativeToGround so altitude tracks terrain elevation.
        _alt_mode = "relativeToGround"
        csg      = ev["csg"]
        tgt_lon  = ev["tgt_lon"]
        tgt_lat  = ev["tgt_lat"]
        dist_km  = ev["dist_km"]
        flight_s = ev["flight_s"]
        launch_s = ev["launch_s"]
        peak     = ev["peak"]
        src_lon, src_lat = site["lon"], site["lat"]

        # Per-munition arc resolution: slow/flat weapons use fewer segments;
        # high-arc ballistics use more for smooth parabola rendering.
        n_arc_ev = mdef.get("n_arc_override", n_arc)

        if ev["is_int"]:
            t_int_frac = ev["t_int_frac"]
            react_s    = ev["react_s"]
            # How many arc segments to show before the kill point.
            arc_segments_to_show = max(2, round(t_int_frac * n_arc_ev))
            pts        = arc_points(src_lon, src_lat, tgt_lon, tgt_lat,
                                    peak, n_arc_ev, mdef["sea_skim"])
            # Slice to only the approach arc up to the intercept moment.
            visible_arc_points = pts[:arc_segments_to_show + 1]
            arc_timestamps = [launch_s + (k / n_arc_ev) * flight_s for k in range(arc_segments_to_show + 1)]
            # Time (seconds into simulation) when the kill occurs.
            intercept_time_s = arc_timestamps[-1]
            latest_s   = max(latest_s, intercept_time_s)
            int_lon, int_lat, int_alt = visible_arc_points[-1]

            # Time when the defending ship fires its interceptor (intercept time minus reaction time).
            interceptor_fire_time_s   = max(0.0, intercept_time_s - react_s)
            # Neutralization time of the firing CSG (if it has been destroyed by this point).
            csg_neutralized_time_s = tenth_hit_s.get(csg["name"])
            # Only generate an interceptor track if the CSG is still combat-capable at fire time.
            csg_still_active_at_fire_time = (csg_neutralized_time_s is None or interceptor_fire_time_s < csg_neutralized_time_s)

            int_style  = ev["int_style_ev"]
            # Distinguish the three interceptor categories for separate KML styling.
            interceptor_is_ciws    = (int_style == "us_ciws")
            interceptor_is_naval_gun = (int_style == "us_naval_gun")
            # Peak altitude of the interceptor arc: CIWS engages close-in at low altitude;
            # SM-6/SM-2 arc rises much higher to meet the threat at mid-course.
            interceptor_arc_peak_altitude_m = max(int_alt * 1.1, 50) if interceptor_is_ciws else max(int_alt * 1.15, 8_000)
            interceptor_category = ev["interceptor_category_ev"]

            # Convert KML AABBGGRR hex color to CSS #RRGGBB for HTML popup styling.
            munition_css_color = _kml_to_css(mdef["color"])
            desc = _html_popup("◈ INTERCEPTED", _C_INTERCEPT, [
                ("Munition",    mname,                         munition_css_color),
                ("Origin",      site["name"],                  _C_IRAN_SITE),
                ("Target",      csg["name"],                   _C_US_CSG),
                ("Range",       f"{dist_km:.0f} km"),
                ("Flight time", f"{flight_s/60:.1f} min"),
                ("Kill time",   f"T+{intercept_time_s/60:.1f} min",    _C_INTERCEPT),
                ("Altitude",    f"{int_alt:.0f} m"),
                ("Weapon",      interceptor_category,                       _C_US_CSG),
            ])

            missile_segs[mname] += gx_track(
                safe_id(mname) + _lbl, visible_arc_points, arc_timestamps, f"{mname} #{i}", desc,
                altitude_mode=_alt_mode)

            # CEP circle: labeled (~15%) ballistic missiles only (non-sea-skim)
            if _lbl and not mdef["sea_skim"]:
                _cep_r = MUNITION_CEP_M.get(mname, 0)
                if _cep_r > 0:
                    cep_circles[mname].append(cep_circle_kml(
                        tgt_lon, tgt_lat, _cep_r, mdef["color"],
                        f"CEP {mname} #{i} ({_cep_r:.0f} m)", launch_s, intercept_time_s))

            if csg_still_active_at_fire_time:
                _fire_lon, _fire_lat = csg_pos_at(csg, interceptor_fire_time_s)
                sm6_pts   = arc_points(_fire_lon, _fire_lat, int_lon, int_lat,
                                       interceptor_arc_peak_altitude_m, n_arc_intercept, False)
                sm6_t_pts = [interceptor_fire_time_s + (k / n_arc_intercept) * react_s for k in range(n_arc_intercept + 1)]
                sm6_segs[interceptor_category] += gx_track(
                    int_style, sm6_pts, sm6_t_pts,
                    f"{'CIWS' if interceptor_is_ciws else 'Gun' if interceptor_is_naval_gun else 'SM-6'} #{i}")

            # Look up the SSPK entry for this munition type for the popup label.
            sspk_reference_entry = MUNITION_SSPK.get(mname, {})
            sspk_interceptor_name = sspk_reference_entry.get("interceptor", "\u2014")
            sspk_display_label = f"{round(sspk_reference_entry.get('sspk', 0) * 100)}%  ({sspk_interceptor_name})"
            _kill_desc = _html_popup('◈ KILL CONFIRMED', _C_INTERCEPT, [
                ('Munition', mname, munition_css_color),
                ('Altitude', f'{int_alt:.0f} m'),
                ('Time', f'T+{intercept_time_s/60:.1f} min', _C_INTERCEPT),
                ('System', interceptor_category, _C_US_CSG),
                ('SSPK', sspk_display_label, _C_INTERCEPT)])
            _kill_coord = (f"<Point><altitudeMode>relativeToGround</altitudeMode>"
                           f"<coordinates>{int_lon:.5f},{int_lat:.5f},{int_alt:.0f}</coordinates>"
                           f"</Point>")
            # 10 alternating black/white slices × 3 s each = 30 s flash window
            for _step in range(10):
                _t0 = intercept_time_s + _step * 3.0
                _t1 = _t0 + 3.0
                _style = "intercept_marker" if _step % 2 == 0 else "intercept_marker_white"
                _desc_tag = f"<description>{_kill_desc}</description>" if _step == 0 else ""
                intercept_pts[mname].append(
                    f"      <Placemark>"
                    f"<name>Kill #{i}</name><styleUrl>#{_style}</styleUrl>"
                    + _desc_tag
                    + f"<TimeSpan><begin>{fmt_time(sim_time(_t0))}</begin>"
                    f"<end>{fmt_time(sim_time(_t1))}</end></TimeSpan>"
                    + _kill_coord
                    + f"</Placemark>"
                )

        else:
            if ev["is_ai"]:
                # ── AI Shahed: distance-based EO/IR lock-on ──────────────────────
                # Phase 1 (orange): dead-reckoning approach until SHAHED_AI_LOCK_KM
                # Phase 2 (bright orange): computer-vision terminal redirect
                # lock_on_fraction: fraction of total flight covered before EO/IR acquisition.
                lock_on_fraction = ev["lock_frac"]
                # Number of arc segments to render for the dead-reckoning approach phase.
                approach_arc_segment_count = max(2, round(lock_on_fraction * n_arc))
                # Remaining distance (km) at the moment of EO/IR lock-on.
                lock_on_distance_km = dist_km * (1.0 - lock_on_fraction)
                full_arc_points = arc_points(src_lon, src_lat, tgt_lon, tgt_lat,
                                      peak, n_arc, mdef["sea_skim"])
                # Slice to the approach portion only (before lock-on).
                approach_arc_points = full_arc_points[:approach_arc_segment_count + 1]
                approach_arc_timestamps = [launch_s + (k / n_arc) * flight_s
                               for k in range(approach_arc_segment_count + 1)]
                # Simulation time and 3-D position at the lock-on waypoint.
                waypoint_lock_time_s = approach_arc_timestamps[-1]
                lock_on_waypoint     = approach_arc_points[-1]

                ai_lon, ai_lat = ev["ai_tgt_lon"], ev["ai_tgt_lat"]
                t_terminal  = flight_s * (1.0 - lock_on_fraction) * 0.9   # slight speed-up on lock
                t_end_s     = waypoint_lock_time_s + t_terminal
                # Eight evenly-spaced timestamps for the 8-segment terminal arc.
                t_pts_term  = [waypoint_lock_time_s + (k / 8) * t_terminal for k in range(9)]
                terminal_arc_points = arc_points(lock_on_waypoint[0], lock_on_waypoint[1], ai_lon, ai_lat,
                                         max(lock_on_waypoint[2] * 0.5, 20), 8, True)
                latest_s = max(latest_s, t_end_s)

                # CSS color for the breakthrough (brighter) variant of this munition.
                munition_css_color = _kml_to_css(mdef["color_bt"])
                desc_appr = _html_popup("⚠ AI-GUIDED APPROACH", _C_AI, [
                    ("Munition",    f"{mname} [AI / Computer-Vision]", munition_css_color),
                    ("Origin",      site["name"],                       _C_IRAN_SITE),
                    ("Target",      csg["name"],                        _C_US_CSG),
                    ("Total range", f"{dist_km:.0f} km"),
                    ("Phase 1",     f"Dead-reckoning: {dist_km - lock_on_distance_km:.0f} km "
                                    f"({lock_on_fraction*100:.0f}% of flight)",     _C_AI),
                    ("Lock-on at",  f"{lock_on_distance_km:.0f} km from target — "
                                    f"EO/IR acquires carrier heat signature"),
                    ("Launch",      f"T+{launch_s/60:.1f} min"),
                    ("Lock time",   f"T+{waypoint_lock_time_s/60:.1f} min",            _C_AI),
                ])
                desc_term = _html_popup("⚠ AI TERMINAL LOCK-ON", _C_AI, [
                    ("Munition",    f"{mname} [AI / Computer-Vision]", munition_css_color),
                    ("System",      "LWIR EO/IR camera — computer-vision guidance"),
                    ("Acquired at", f"{lock_on_distance_km:.0f} km — T+{waypoint_lock_time_s/60:.1f} min", _C_AI),
                    ("Precision",   f"CEP <200 m (defeats CIWS lead prediction)", _C_NEUTRALIZED),
                    ("Phase 2",     f"Terminal dash: {lock_on_distance_km:.0f} km at "
                                    f"{mdef['speed_km_s']*3600:.0f} km/h"),
                    ("Impact",      f"T+{t_end_s/60:.1f} min",         _C_AI),
                ])
                missile_segs[mname] += gx_track(
                    "shahed_ai_approach" + _lbl, approach_arc_points, approach_arc_timestamps,
                    f"{mname} #{i} [AI-APPROACH]", desc_appr, altitude_mode=_alt_mode)
                missile_segs[mname] += gx_track(
                    "shahed_ai_terminal" + _lbl, terminal_arc_points, t_pts_term,
                    f"{mname} #{i} [AI-LOCK-ON]", desc_term, altitude_mode=_alt_mode)

                impact_pts[mname].append(
                    f"      <Placemark>"
                    f"<name>AI IMPACT #{i} — {mname} [CV]</name>"
                    f"<styleUrl>#impact_marker</styleUrl>"
                    f"<description>{_html_popup('⚠ AI IMPACT', _C_AI, [('Munition', f'{mname} [CV]', munition_css_color), ('From', site['name'], _C_IRAN_SITE), ('On', csg['name'], _C_US_CSG), ('Locked at', f'{lock_on_distance_km:.0f} km', _C_AI), ('Mode', 'Computer-vision terminal guidance — CIWS defeated', _C_NEUTRALIZED), ('Impact', f'T+{t_end_s/60:.1f} min', _C_AI)])}</description>"
                    f"<TimeStamp><when>{fmt_time(sim_time(t_end_s))}</when></TimeStamp>"
                    f"<Point><altitudeMode>relativeToGround</altitudeMode>"
                    f"<coordinates>{ai_lon:.5f},{ai_lat:.5f},0</coordinates>"
                    f"</Point></Placemark>"
                )

            elif ev.get("lock_frac") is not None:
                # ── IRGCN Sea Drone: radar lock-on routing ────────────────────────
                # If lock_frac == 0 (already within IRGCN_LOCK_KM at launch):
                #   boat dispatches directly toward the ship with full lock-on styling.
                # Otherwise: Phase 1 (amber transit) → Phase 2 (red-orange lock-on).
                # lock_on_fraction: proportion of transit covered before radar acquires the CSG.
                lock_on_fraction  = ev["lock_frac"]
                # Remaining surface distance (km) when the sea drone's radar first locks on.
                lock_on_distance_km = dist_km * (1.0 - lock_on_fraction)
                # True when the drone is already within radar range the moment it launches.
                _direct     = (lock_on_fraction < 0.01)
                _lock_range_m = mdef.get("lock_on_range_km", IRGCN_LOCK_KM)

                # Lock-on target: actual CSG position at estimated impact (no scatter)
                lock_csg_lon, lock_csg_lat = csg_pos_at(csg, launch_s + flight_s)
                t_end_s  = launch_s + flight_s
                latest_s = max(latest_s, t_end_s)
                # CSS color for popup styling (breakthrough bright variant).
                munition_css_color = _kml_to_css(mdef["color_bt"])

                if _direct:
                    # ── Direct run — already in radar range, no transit leg ────────
                    n_term     = n_arc_ev
                    t_pts_full = [launch_s + (k / n_term) * flight_s for k in range(n_term + 1)]
                    full_arc_points = arc_points(src_lon, src_lat, lock_csg_lon, lock_csg_lat,
                                            peak, n_term, True)
                    desc_direct = _html_popup("⚙ IRGCN DIRECT ATTACK", _C_AI, [
                        ("Munition",    mname,                                    munition_css_color),
                        ("Origin",      site["name"],                             _C_IRAN_SITE),
                        ("Target",      csg["name"],                              _C_US_CSG),
                        ("Range",       f"{dist_km:.0f} km — within radar lock ({_lock_range_m:.0f} km) at launch"),
                        ("Mode",        "Full radar-lock from launch — direct intercept course", _C_AI),
                        ("Speed",       f"{mdef['speed_km_s']*3600:.0f} km/h"),
                        ("Launch",      f"T+{launch_s/60:.1f} min"),
                        ("Impact",      f"T+{t_end_s/60:.1f} min",               _C_AI),
                    ])
                    missile_segs[mname] += gx_track(
                        "irgcn_lock_terminal" + _lbl, full_arc_points, t_pts_full,
                        f"{mname} #{i} [DIRECT]", desc_direct, altitude_mode=_alt_mode)
                else:
                    # ── Two-phase: dead-reckoning transit + radar lock-on ─────────
                    approach_arc_segment_count = max(2, round(lock_on_fraction * n_arc_ev))
                    full_arc_points = arc_points(src_lon, src_lat, tgt_lon, tgt_lat,
                                            peak, n_arc_ev, mdef["sea_skim"])
                    approach_arc_points = full_arc_points[:approach_arc_segment_count + 1]
                    approach_arc_timestamps = [launch_s + (k / n_arc_ev) * flight_s
                                   for k in range(approach_arc_segment_count + 1)]
                    # Simulation time and 3-D position at the radar lock-on waypoint.
                    waypoint_lock_time_s = approach_arc_timestamps[-1]
                    lock_on_waypoint     = approach_arc_points[-1]
                    t_term = flight_s * (1.0 - lock_on_fraction)
                    n_term = max(3, n_arc_ev // 2)
                    t_pts_term = [waypoint_lock_time_s + (k / n_term) * t_term for k in range(n_term + 1)]
                    terminal_arc_points = arc_points(lock_on_waypoint[0], lock_on_waypoint[1], lock_csg_lon, lock_csg_lat,
                                            max(lock_on_waypoint[2], 1.0), n_term, True)

                    desc_appr = _html_popup("⚙ IRGCN TRANSIT", _C_IRAN_SITE, [
                        ("Munition",    mname,                                        munition_css_color),
                        ("Origin",      site["name"],                                 _C_IRAN_SITE),
                        ("Target",      csg["name"],                                  _C_US_CSG),
                        ("Total range", f"{dist_km:.0f} km"),
                        ("Phase 1",     f"Dead-reckoning: {dist_km - lock_on_distance_km:.0f} km "
                                        f"({lock_on_fraction*100:.0f}% of route)"),
                        ("Radar lock",  f"Acquires at {lock_on_distance_km:.0f} km — "
                                        f"T+{waypoint_lock_time_s/60:.1f} min",                      _C_AI),
                        ("Speed",       f"{mdef['speed_km_s']*3600:.0f} km/h surface"),
                        ("Launch",      f"T+{launch_s/60:.1f} min"),
                    ])
                    desc_term = _html_popup("⚙ IRGCN RADAR LOCK-ON", _C_AI, [
                        ("Munition",    mname,                                        munition_css_color),
                        ("System",      "Surface search radar — autonomous terminal guidance"),
                        ("Acquired at", f"{lock_on_distance_km:.0f} km — T+{waypoint_lock_time_s/60:.1f} min", _C_AI),
                        ("Phase 2",     f"Radar-guided run: {lock_on_distance_km:.0f} km direct to {csg['name']}"),
                        ("Impact",      f"T+{t_end_s/60:.1f} min",                   _C_AI),
                    ])
                    missile_segs[mname] += gx_track(
                        safe_id(mname) + "_bt" + _lbl, approach_arc_points, approach_arc_timestamps,
                        f"{mname} #{i} [TRANSIT]", desc_appr, altitude_mode=_alt_mode)
                    missile_segs[mname] += gx_track(
                        "irgcn_lock_terminal" + _lbl, terminal_arc_points, t_pts_term,
                        f"{mname} #{i} [RADAR LOCK]", desc_term, altitude_mode=_alt_mode)

                impact_pts[mname].append(
                    f"      <Placemark>"
                    f"<name>IRGCN IMPACT #{i} — {mname}</name>"
                    f"<styleUrl>#impact_marker</styleUrl>"
                    f"<description>{_html_popup('⚙ IRGCN IMPACT', _C_AI, [('Munition', mname, munition_css_color), ('From', site['name'], _C_IRAN_SITE), ('On', csg['name'], _C_US_CSG), ('Mode', 'Direct attack' if _direct else f'Radar lock at {lock_on_distance_km:.0f} km', _C_AI), ('Impact', f'T+{t_end_s/60:.1f} min', _C_AI)])}</description>"
                    f"<TimeStamp><when>{fmt_time(sim_time(t_end_s))}</when></TimeStamp>"
                    f"<Point><altitudeMode>relativeToGround</altitudeMode>"
                    f"<coordinates>{lock_csg_lon:.5f},{lock_csg_lat:.5f},0</coordinates>"
                    f"</Point></Placemark>"
                )

            else:
                # ── Normal breakthrough ──────────────────────────────────────────
                pts     = arc_points(src_lon, src_lat, tgt_lon, tgt_lat,
                                     peak, n_arc_ev, mdef["sea_skim"])
                t_pts   = [launch_s + (k / n_arc_ev) * flight_s for k in range(n_arc_ev + 1)]
                t_end_s = launch_s + flight_s
                latest_s = max(latest_s, t_end_s)

                # Convert KML AABBGGRR breakthrough color to CSS #RRGGBB for popup.
                munition_css_color = _kml_to_css(mdef["color_bt"])
                desc = _html_popup("✦ BREAKTHROUGH", _C_BT, [
                    ("Munition",    mname,                       munition_css_color),
                    ("Origin",      site["name"],                _C_IRAN_SITE),
                    ("Target",      csg["name"],                 _C_US_CSG),
                    ("Range",       f"{dist_km:.0f} km"),
                    ("Flight time", f"{flight_s/60:.1f} min"),
                    ("Impact",      f"T+{t_end_s/60:.1f} min",  _C_BT),
                ])

                missile_segs[mname] += gx_track(
                    safe_id(mname) + "_bt" + _lbl, pts, t_pts,
                    f"{mname} #{i} [BT]", desc, altitude_mode=_alt_mode)

                # CEP circle: labeled (~15%) ballistic breakthrough missiles only
                if _lbl and not mdef["sea_skim"]:
                    _cep_r = MUNITION_CEP_M.get(mname, 0)
                    if _cep_r > 0:
                        cep_circles[mname].append(cep_circle_kml(
                            tgt_lon, tgt_lat, _cep_r, mdef["color_bt"],
                            f"CEP {mname} #{i} ({_cep_r:.0f} m) [BT]", launch_s, t_end_s))

                impact_pts[mname].append(
                    f"      <Placemark>"
                    f"<name>IMPACT #{i} -- {mname}</name><styleUrl>#impact_marker</styleUrl>"
                    f"<description>{_html_popup('✦ IMPACT', _C_BT, [('Munition', mname, munition_css_color), ('From', site['name'], _C_IRAN_SITE), ('On', csg['name'], _C_US_CSG)])}</description>"
                    f"<TimeStamp><when>{fmt_time(sim_time(t_end_s))}</when></TimeStamp>"
                    f"<Point><altitudeMode>relativeToGround</altitudeMode>"
                    f"<coordinates>{tgt_lon:.5f},{tgt_lat:.5f},0</coordinates>"
                    f"</Point></Placemark>"
                )

    # ================================================================
    # PHASE 4 — Generate US counterstrike KML
    # ================================================================
    strike_segs, strike_impacts = gen_us_strike_kml(strike_events, site_inactive_at, threshold=_sc_threshold)
    iaf_segs, iaf_impacts = gen_iaf_kml(iaf_events, site_inactive_at)

    n_sites_destroyed = len(site_inactive_at)
    sites_destroyed_names = ", ".join(sorted(site_inactive_at.keys())) or "none"

    dur_min = latest_s / 60.0
    # Assets (CSG icons, Iranian site icons) must remain visible through the full
    # scenario time window — not just until the last missile event.  For phased
    # scenarios (e.g. one_percent_probe) the assessment lull and follow-on phase
    # can extend well beyond the last simulated missile impact.  Using wave_s as
    # the floor ensures assets stay on screen for the entire declared scenario envelope.
    asset_end_s = max(latest_s, wave_s)

    actual_intercepted  = sum(1 for e in events if e["is_int"])
    actual_ai           = sum(1 for e in events if e["is_ai"])
    actual_breakthrough = actual_launched - actual_intercepted

    # ── Cost accounting ──────────────────────────────────────────────────────
    iran_cost = sum(MUNITIONS[e["mname"]]["cost_usd"] for e in events)

    intercept_by_cat = {cat: 0 for cat in INTERCEPTOR_COSTS}
    for e in events:
        if e["is_int"] and e.get("interceptor_category_ev"):
            intercept_by_cat[e["interceptor_category_ev"]] += 1
    us_intercept_cost = sum(INTERCEPTOR_COSTS[c] * n for c, n in intercept_by_cat.items())

    us_strike_cost = sum(US_STRIKE_MUNITIONS[e["munition"]]["cost_usd"]
                         for e in strike_events)

    # ── Breakthrough damage: ship/aircraft losses + casualties ───────────────
    # breakthroughs: all penetrations (for sinking model and display counts)
    # hull_hits: penetrations that land within _SHIP_HIT_RADIUS_M of a ship hull
    # Only hull hits produce structural damage, casualties, and cost accounting.
    breakthroughs = [e for e in events if not e["is_int"]]
    hull_hits     = [e for e in breakthroughs if e.get("hit_ship_id")]
    us_ship_damage = sum(MUNITIONS[e["mname"]]["damage_per_hit_usd"] for e in hull_hits)
    # Cap ship damage at total CSG replacement value (can't lose more than you have)
    us_ship_damage = min(us_ship_damage, TOTAL_CSG_VALUE)

    us_mil_kia = int(sum(MUNITIONS[e["mname"]]["kia_per_hit"] for e in hull_hits))
    us_mil_wia = int(sum(MUNITIONS[e["mname"]]["wia_per_hit"] for e in hull_hits))
    # Cap casualties at total personnel at risk
    us_mil_kia = min(us_mil_kia, TOTAL_CSG_PERSONNEL)
    us_mil_wia = min(us_mil_wia, TOTAL_CSG_PERSONNEL - us_mil_kia)

    # ── Magazine summary (used in narrative and results dict) ─────────────────
    # _vls_capacity = total initial guided-missile load across all CSGs
    #                 (rounds remaining + rounds fired = initial load)
    # _vls_remaining = rounds still in magazine at end of battle
    # _cap_hit = True if any CSG exhausted all guided missiles (SM-6/SM-2/ESSM/RAM)
    _vls_capacity  = sum(
        s.sm6 + s.sm2 + s.essm + s.ram
        + s.shots["SM-6"] + s.shots["SM-2"] + s.shots["ESSM"] + s.shots["RAM"]
        for s in csg_states.values()
    )
    _vls_remaining = sum(s.sm6 + s.sm2 + s.essm + s.ram for s in csg_states.values())
    _cap_hit_abm   = any(
        s.sm6 == 0 and s.sm2 == 0 and s.essm == 0 and s.ram == 0
        for s in csg_states.values()
    )

    # ================================================================
    # PER-CSG DAMAGE BREAKDOWN WITH PROBABILISTIC SINKING
    #
    # WHAT: For each Carrier Strike Group, compute:
    #   1. breakthrough_hit_events  — missiles that reached the hull
    #   2. direct_hit_count         — raw count of those hits
    #   3. damage_value_usd         — dollar value of direct hit damage
    #   4. killed_in_action / wounded_in_action — casualty estimates
    #   5. weighted_effective_hits  — sinking-weight-adjusted hit count
    #   6. sinking_probability      — logistic sigmoid output
    #   7. hull_is_sunk             — single RNG roll against that probability
    #
    # WHY LOGISTIC SIGMOID:
    #   P(sink | n_eff) = 1 / (1 + exp(-0.55 × (n_eff - 5.0)))
    #   Calibrated so that:
    #     • n_eff ≈ 2.0  → P ≈ 10%   (USS Sheffield, 1 Exocet)
    #     • n_eff ≈ 4.0  → P ≈ 35%   (USS Stark, 2 Exocets)
    #     • n_eff ≈ 3.6  → P ≈ 28%   (USS Coventry, 3 bombs)
    #   DESTROYED hulls (≥10 mission-killed hits) receive a fixed
    #   P = 0.97 rather than sigmoid, reflecting near-certain loss.
    #
    # WHY TWO-PASS ON SINKING:
    #   The per-CSG loop below runs AFTER the main missile loop so that
    #   first_hit_s / tenth_hit_s are fully populated. Sinking status
    #   (hull_is_sunk) feeds back into aggregate cost totals via
    #   total_sinking_hull_loss_usd / total_sinking_kia at the end.
    # ================================================================
    csg_breakdown = {}
    for csg in csg_fleet:
        # Identify which CSG this iteration covers by name.
        csg_name = csg["name"]

        # hull_hits_csg: only penetrations that physically struck a ship hull (within 20 m).
        # Used for damage, casualty, and sinking calculations.
        # penetrations_csg: all non-intercepted events — used for display counts only.
        hull_hits_csg  = [e for e in hull_hits  if e["csg"]["name"] == csg_name]
        penetrations_csg = [e for e in breakthroughs if e["csg"]["name"] == csg_name]
        breakthrough_hit_events = hull_hits_csg   # alias for sinking model below

        # Count direct hull hits and tally structural damage + casualties.
        # Scale by target ship role: a hit on the CVN has different consequences
        # than a hit on an escort DDG.
        direct_hit_count = len(hull_hits_csg)
        damage_value_usd = sum(
            MUNITIONS[e["mname"]]["damage_per_hit_usd"]
            * _SHIP_ROLE_DAMAGE_SCALE.get(
                next((sh["role"] for sh in csg_ships[csg_name]
                      if sh["id"] == e.get("hit_ship_id")), "DDG"), 1.0)
            for e in hull_hits_csg
        )
        killed_in_action = int(sum(
            MUNITIONS[e["mname"]]["kia_per_hit"]
            * _SHIP_ROLE_KIA_SCALE.get(
                next((sh["role"] for sh in csg_ships[csg_name]
                      if sh["id"] == e.get("hit_ship_id")), "DDG"), 1.0)
            for e in hull_hits_csg
        ))
        wounded_in_action = int(sum(
            MUNITIONS[e["mname"]]["wia_per_hit"]
            * _SHIP_ROLE_KIA_SCALE.get(
                next((sh["role"] for sh in csg_ships[csg_name]
                      if sh["id"] == e.get("hit_ship_id")), "DDG"), 1.0)
            for e in hull_hits_csg
        ))

        # Determine hull status from the hit-timeline populated in Phase 2.
        # tenth_hit_s → mission-killed (DESTROYED); first_hit_s → damaged only.
        if csg_name in tenth_hit_s:
            damage_status_before_sinking = "DESTROYED"
        elif csg_name in first_hit_s:
            damage_status_before_sinking = "DAMAGED"
        else:
            damage_status_before_sinking = "INTACT"

        # Weighted effective hits: heavier munitions count more in the sinking probability model.
        weighted_effective_hits = sum(SINKING_WEIGHT.get(e["mname"], 1.0) for e in hull_hits_csg)

        # Compute sinking_probability via the calibrated logistic sigmoid.
        if damage_status_before_sinking == "DESTROYED":
            sinking_probability = 0.97
        elif damage_status_before_sinking == "DAMAGED":
            sinking_probability = 1.0 / (1.0 + math.exp(-0.55 * (weighted_effective_hits - 5.0)))
        else:
            sinking_probability = 0.0

        # Single RNG draw to resolve whether this CSG actually sinks.
        hull_is_sunk = (rng.random() < sinking_probability)

        # Sinking consequences: additional hull loss + crew casualties
        if hull_is_sunk and damage_status_before_sinking == "DESTROYED":
            # CVN + at least 2 escorts presumed lost; 60% of carrier crew + escorts
            sink_hull = min(int(_CVN_HULL_USD * 0.60 + _DDG_HULL_USD * 2),
                            csg["asset_value_usd"])
            sink_kia  = min(rng.randint(2500, 5000), csg["personnel"])
            sink_wia  = 0
            status    = "DESTROYED+SUNK"
        elif hull_is_sunk and damage_status_before_sinking == "DAMAGED":
            # One escort destroyer lost to progressive flooding
            sink_hull = _DDG_HULL_USD
            sink_kia  = rng.randint(140, 280)   # 50–100% of DDG crew (~280)
            sink_wia  = 0
            status    = "SUNK"
        else:
            sink_hull = 0
            sink_kia  = 0
            sink_wia  = 0
            status    = damage_status_before_sinking

        damage_value_usd += sink_hull
        killed_in_action += sink_kia
        wounded_in_action += sink_wia

        csg_breakdown[csg_name] = {
            "hits":           direct_hit_count,
            "damage_usd":     damage_value_usd,
            "kia":            killed_in_action,
            "wia":            wounded_in_action,
            "status":         status,
            "asset_value_usd": csg["asset_value_usd"],
            "personnel":      csg["personnel"],
            "sink_prob":      sinking_probability,
            "is_sunk":        hull_is_sunk,
            "eff_hits":       weighted_effective_hits,
            "sink_hull":      sink_hull,   # hull loss attributable to sinking (not direct hits)
            "sink_kia":       sink_kia,    # casualties attributable to sinking (not direct hits)
        }

    # Fold sinking losses back into aggregate cost/casualty totals.
    # sink_hull and sink_kia are stored directly in csg_breakdown to avoid
    # subtraction mismatches between hull_hits-based and breakthroughs-based sums.
    total_sinking_hull_loss_usd = sum(
        bd["sink_hull"] for bd in csg_breakdown.values() if bd["is_sunk"])
    us_ship_damage = min(us_ship_damage + total_sinking_hull_loss_usd, TOTAL_CSG_VALUE)

    total_sinking_kia = sum(
        bd["sink_kia"] for bd in csg_breakdown.values() if bd["is_sunk"])
    us_mil_kia = min(us_mil_kia + total_sinking_kia, TOTAL_CSG_PERSONNEL)

    # ── Per-munition Iranian offensive cost breakdown ─────────────────────────
    iran_cost_by_munition = {}
    for e in events:
        munition_name = e["mname"]
        iran_cost_by_munition[munition_name] = iran_cost_by_munition.get(munition_name, 0) + MUNITIONS[munition_name]["cost_usd"]

    # ── Collateral damage to Gulf commercial/allied shipping ─────────────────
    # Missiles that stray off target or whose debris/shrapnel hits nearby vessels.
    # Persian Gulf: ~55 transits/day through Hormuz; dense tanker/LNG/container traffic.
    collateral_usd = sum(MUNITIONS[e["mname"]]["collateral_usd_per_btk"]
                         for e in breakthroughs)
    collateral_kia = sum(MUNITIONS[e["mname"]]["collateral_kia_per_btk"]
                         for e in breakthroughs)

    # ── Air support costs ────────────────────────────────────────────────────
    # IAF strike munition cost
    iaf_cost = sum(IAF_MUNITIONS[e["munition"]]["cost_usd"] for e in iaf_events)

    # Carrier CAP AIM-120 expenditure (cost only; not geometrically simulated)
    scenario_days = max(1, round(dur_min / (60 * 8)))  # ~8-hr ops day
    cap_amraam_total = CAP_AMRAAM_PER_CSG_DAY * len(US_CSGS) * scenario_days
    cap_amraam_cost  = cap_amraam_total * AIM120_COST_USD

    # Carrier SLAM-ER air-launched strikes
    slam_er_total = SLAM_ER_PER_CSG_DAY * len(US_CSGS) * scenario_days
    slam_er_cost  = slam_er_total * SLAM_ER_COST_USD

    total_us_cost = (us_intercept_cost + us_strike_cost + us_ship_damage
                     + cap_amraam_cost + slam_er_cost + iaf_cost)

    # Exchange ratio: US total strategic cost / Iran offensive cost
    exchange_ratio = total_us_cost / max(1, iran_cost)

    def fmt_cost(usd):
        if usd >= 1e9:
            return f"${usd/1e9:.2f}B"
        return f"${usd/1e6:.1f}M"

    def fmt_fleet(usd):
        return f"${usd/1e9:.1f}B"

    cost_block = (
        f"── Cost Estimates (open-source; FY2023 USD) ──────────────────────────────\n"
        f"Fleet at risk (8 CSGs):    {fmt_fleet(TOTAL_CSG_VALUE)}"
        f"  (hulls + air wings incl. F/A-18E/F, E-2D, EA-18G; {TOTAL_CSG_PERSONNEL:,} personnel)\n"
        f"\n"
        f"Iran offensive munitions:  {fmt_cost(iran_cost)}"
        f"  ({actual_launched:,} rounds × weighted unit cost)\n"
        f"\n"
        f"── US / Coalition Expenditure ─────────────────────────────────────────────\n"
        f"VLS interceptors:          {fmt_cost(us_intercept_cost)}"
        f"  ({intercept_by_cat['SM-6 / SM-2']:,} SM-6/SM-2 @$3.3M"
        f" | {intercept_by_cat['CIWS / SeaRAM']:,} CIWS/SeaRAM @$800k"
        f" | {intercept_by_cat['Naval Gun / Phalanx']:,} Naval Gun @$50k)\n"
        f"Carrier CAP (AIM-120):     {fmt_cost(cap_amraam_cost)}"
        f"  ({cap_amraam_total:,} AIM-120C/D @$1.2M — F/A-18F CAP duty, ~{scenario_days}d)\n"
        f"VLS strikes (TLAM/JASSM):  {fmt_cost(us_strike_cost)}"
        f"  ({len(strike_events):,} rounds)\n"
        f"Air-launched strikes (SLAM-ER): {fmt_cost(slam_er_cost)}"
        f"  ({slam_er_total:,} AGM-84H @$1.3M — F/A-18E carrier strikes)\n"
        f"IAF strikes (F-35I/F-15I/F-16I): {fmt_cost(iaf_cost)}"
        f"  ({len(iaf_events):,} Rampage/SPICE/JDAM-ER — Israeli air support)\n"
        f"US ship/aircraft damage:   {fmt_cost(us_ship_damage)}"
        f"  ({actual_breakthrough:,} hits; probability-weighted per munition type)\n"
        f"  Estimated US military casualties: {us_mil_kia:,} KIA / {us_mil_wia:,} WIA\n"
        f"  (capped at {TOTAL_CSG_PERSONNEL:,} total personnel at risk)\n"
        f"\n"
        f"Collateral — Gulf shipping:{fmt_cost(collateral_usd)}"
        f"  damage | ~{int(collateral_kia):,} civilian KIA\n"
        f"  (tankers, LNG/container ships, allied navies — stray rounds + debris)\n"
        f"\n"
        f"Total coalition cost:      {fmt_cost(total_us_cost)}"
        f"  (VLS + CAP + strikes + SLAM-ER + IAF + ship damage; excl. collateral)\n"
        f"Exchange ratio:            {exchange_ratio:.1f}:1  "
        f"(Coalition spends ${exchange_ratio:.1f} for every $1 Iran spends)\n"
        f"Cost per Iranian kill:     "
        f"{fmt_cost(us_intercept_cost / max(1, actual_intercepted))} per VLS intercept"
    )

    _n_neut   = sum(1 for bd in csg_breakdown.values()
                    if bd["status"] in ("DESTROYED", "DESTROYED+SUNK"))
    _n_sunk   = sum(1 for bd in csg_breakdown.values() if bd["is_sunk"])
    _n_dmg    = sum(1 for bd in csg_breakdown.values()
                    if bd["status"] == "DAMAGED")
    _n_intact = len(csg_fleet) - _n_neut - _n_dmg

    costs = {
        "iran_cost": iran_cost,
        "us_intercept_cost": us_intercept_cost,
        "us_strike_cost": us_strike_cost,
        "us_ship_damage": us_ship_damage,
        "total_us_cost": total_us_cost,
        "exchange_ratio": exchange_ratio,
        "intercept_by_cat": intercept_by_cat,
        "us_mil_kia": us_mil_kia,
        "us_mil_wia": us_mil_wia,
        "collateral_usd": collateral_usd,
        "collateral_kia": int(collateral_kia),
        "n_sites_destroyed": n_sites_destroyed,
        "n_sites_total":     len(_sc_sites),
        "n_csg_neutralized": _n_neut,
        "n_csg_sunk":        _n_sunk,
        "n_csg_damaged": _n_dmg,
        "n_csg_intact": _n_intact,
        "actual_launched": actual_launched,
        "actual_intercepted": actual_intercepted,
        "actual_breakthrough": actual_breakthrough,
        "cap_hit": _cap_hit_abm,
        "csg_breakdown": csg_breakdown,
        "iran_cost_by_munition": iran_cost_by_munition,
        "iaf_cost": iaf_cost,
        "us_strike_cost": us_strike_cost,
        "us_intercept_cost": us_intercept_cost,
    }

    # ── Per-CSG Battle Damage Assessment table ──────────────────────────────────
    _col = max(len(c["name"]) for c in csg_fleet)
    _hdr = (f"{'CSG':<{_col}} | {'Hits':>5} | {'Status':<16} | "
            f"{'First Hit':>12} | {'Destr. at':>11} | {'P(sink)':>8} | {'Sunk?':>6}")
    _div = "-" * len(_hdr)
    _tbl_rows = [_div, _hdr, _div]
    for _c in csg_fleet:
        _cn  = _c["name"]
        _bd  = csg_breakdown[_cn]
        _fh  = first_hit_s.get(_cn)
        _th  = tenth_hit_s.get(_cn)
        _fh_s = f"T+{_fh/60:5.1f} min" if _fh is not None else "       ---"
        _th_s = f"T+{_th/60:5.1f} min" if _th is not None else "        ---"
        _ps   = f"{_bd['sink_prob']*100:5.1f}%"
        _sk   = "SUNK" if _bd["is_sunk"] else "afloat"
        _tbl_rows.append(
            f"{_cn:<{_col}} | {_bd['hits']:>5} | {_bd['status']:<16} | "
            f"{_fh_s:>12} | {_th_s:>11} | {_ps:>8} | {_sk:>6}")
    _tbl_rows.append(_div)
    _tbl_rows.append(
        f"FLEET RESULT: {_n_neut} DESTROYED | {_n_sunk} SUNK (incl. above) | "
        f"{_n_dmg} DAMAGED | {_n_intact} INTACT")
    _tbl_rows.append(_div)
    csg_table = "\n".join(_tbl_rows)

    # ── Analytical narrative (generated from computed simulation values) ─────────
    _int_pct   = round(100 * actual_intercepted / max(1, actual_launched))
    _bt_pct    = round(100 * actual_breakthrough / max(1, actual_launched))
    _supp      = n_missiles - actual_launched
    _supp_pct  = round(100 * _supp / max(1, n_missiles))
    _cap_flag  = _cap_hit_abm
    _vls_head  = _vls_remaining
    _cpk       = fmt_cost(us_intercept_cost / max(1, actual_intercepted))
    _destroyed_csgs = [c["name"] for c in csg_fleet if c["name"] in tenth_hit_s]
    _fh_times  = sorted(first_hit_s.values())  if first_hit_s  else []
    _th_times  = sorted(tenth_hit_s.values()) if tenth_hit_s else []

    def _para(*lines): return "\n".join(lines)

    # ── I. Executive Summary ─────────────────────────────────────────────────
    _cap_note = (" VLS INTERCEPT CEILING BREACHED — final salvo phases"
                 " faced under-defended terminal approaches." if _cap_flag else "")
    _I = _para(
        "══ I. EXECUTIVE SUMMARY ══════════════════════════════════════════════════",
        f"Iran commits {actual_launched:,} munitions against 8 US Carrier Strike Groups"
        f" (intended: {n_missiles:,}; {_supp:,} suppressed pre-launch [{_supp_pct}%]).",
        f"US/Coalition AEGIS defenses engage {actual_intercepted:,} rounds — an intercept"
        f" rate of {_int_pct}%.",
        f"{actual_breakthrough:,} rounds ({_bt_pct}%) breach the defensive envelope and"
        f" reach fleet positions.{_cap_note}",
        f"Engagement duration: ~{dur_min:.0f} minutes."
        f" Iranian launch network: {n_sites_destroyed}/{len(_sc_sites)} sites destroyed.",
        f"Fleet outcome: {_n_neut} CSG(s) DESTROYED (≥10 hits)"
        f" | {_n_dmg} DAMAGED | {_n_intact} INTACT.",
    )

    # ── II. Offensive Capability Assessment ─────────────────────────────────
    _ai_note = (f" {actual_ai:,} AI-guided Shahed-136 terminal variants"
                f" ({round(100*actual_ai/max(1,actual_launched), 1)}% of salvo)"
                f" achieve guaranteed breakthroughs by defeating CIWS lead-angle prediction."
                if actual_ai > 0 else "")
    _supp_clause = (
        f"Preemptive US/IAF strikes suppress {_supp:,} ({_supp_pct}%) of Iran's"
        f" intended {n_missiles:,}-round salvo before launch — eliminating"
        f" {n_sites_destroyed} of 12 launch complexes"
        + (f" ({sites_destroyed_names})" if n_sites_destroyed > 0 else "")
        + f". {actual_launched:,} rounds reach flight."
        if _supp > 0
        else f"All {n_missiles:,} planned rounds reach flight — no pre-launch suppression achieved."
    )
    _II = _para(
        "══ II. OFFENSIVE CAPABILITY ASSESSMENT ══════════════════════════════════",
        _supp_clause,
        f"Iran expends {fmt_cost(iran_cost)} in offensive munitions"
        f" (weighted unit cost across {actual_launched:,} rounds)."
        + _ai_note,
        f"Surviving sites maintain continuous salvo pressure for ~{dur_min:.0f} min,"
        f" maximising sensor saturation and CIWS magazine consumption.",
    )

    # ── III. Defensive Performance Analysis ─────────────────────────────────
    _vls_note = (
        f"CRITICAL: Aegis VLS guided missiles exhausted (initial load ~{_vls_capacity:,}) — subsequent"
        f" volleys faced degraded intercept probability as magazines approached depletion."
        if _cap_flag else
        f"VLS headroom remaining: {_vls_head:,} guided rounds"
        f" ({round(100*_vls_head/max(1,_vls_capacity))}% of initial load) — defense posture sustainable."
    )
    _III = _para(
        "══ III. DEFENSIVE PERFORMANCE ANALYSIS ═══════════════════════════════════",
        f"Aegis achieves a {_int_pct}% intercept rate"
        f" ({actual_intercepted:,} of {actual_launched:,} rounds engaged).",
        f"SM-6/SM-2 mid-course: {intercept_by_cat['SM-6 / SM-2']:,} kills"
        f" | CIWS/SeaRAM terminal: {intercept_by_cat['CIWS / SeaRAM']:,} kills"
        f" | Naval Gun: {intercept_by_cat['Naval Gun / Phalanx']:,} kills.",
        f"Cost per intercept: {_cpk} (SM-6 @$3.3M dominant; CIWS @$800k supplemental).",
        _vls_note,
    )

    # ── IV. Fleet Damage Assessment ──────────────────────────────────────────
    _fh_str = f"T+{_fh_times[0]/60:.0f} min" if _fh_times else "—"
    _th_str = f"T+{_th_times[0]/60:.0f} min" if _th_times else "—"

    # Build per-CSG sinking summary lines
    _afloat_dmg  = [cn for cn, bd in csg_breakdown.items()
                    if bd["status"] == "DAMAGED" and not bd["is_sunk"]]

    _dest_clause = ""
    if _n_neut > 0:
        _dest_clause = (
            f" Destroyed CSGs (≥10 hits, mission-killed): {', '.join(_destroyed_csgs)}."
            f" First CSG destroyed at {_th_str}."
            f" Each lost hull represents ~{TOTAL_CSG_PERSONNEL // 8:,} personnel at risk"
            f" and the permanent loss of ~90 embarked aircraft."
        )
    _sink_lines = []
    for _cn, _bd in csg_breakdown.items():
        if _bd["hits"] == 0:
            continue
        _ps_str = f"{_bd['sink_prob']*100:.0f}%"
        _eff_str = f"{_bd['eff_hits']:.1f}"
        if _bd["is_sunk"]:
            _sink_lines.append(
                f"  {_cn}: {_bd['hits']} hits (eff {_eff_str}) — SUNK"
                f" [{_ps_str} P(sink); +{_bd['kia'] - int(sum(MUNITIONS[e['mname']]['kia_per_hit'] for e in breakthroughs if e['csg']['name']==_cn)):,} crew KIA from sinking]"
            )
        else:
            _sink_lines.append(
                f"  {_cn}: {_bd['hits']} hits (eff {_eff_str}) — {_bd['status']}"
                f" [{_ps_str} P(sink) — afloat]"
            )
    _sink_block = "\n".join(_sink_lines) if _sink_lines else "  No CSGs hit."

    _dmg_clause = (
        f" Damaged and afloat: {', '.join(_afloat_dmg)} —"
        f" mission-degraded; likely port evacuation for repairs."
        if _afloat_dmg else ""
    )
    _IV = _para(
        "══ IV. FLEET DAMAGE ASSESSMENT &amp; SINKING PROBABILITY ════════════════════",
        f"{actual_breakthrough:,} rounds ({_bt_pct}% of salvo) penetrate"
        f" to fleet engagement range. First impact on any CSG: {_fh_str}.",
        f"Fleet status: {_n_neut} DESTROYED | {_n_sunk} SUNK (all causes) |"
        f" {_n_dmg} DAMAGED+AFLOAT | {_n_intact} INTACT (of 8 CSGs)."
        + _dest_clause + _dmg_clause,
        f"Sinking assessment (P(sink) via logistic model on munition-weighted hit score):\n"
        + _sink_block,
    )

    # ── V. Cost-Exchange Analysis ─────────────────────────────────────────────
    _V = _para(
        "══ V. COST-EXCHANGE ANALYSIS ════════════════════════════════════════════",
        f"Iran offensive expenditure:      {fmt_cost(iran_cost)}"
        f" ({actual_launched:,} rounds × weighted unit cost)",
        f"US VLS interceptors:             {fmt_cost(us_intercept_cost)}"
        f" ({intercept_by_cat['SM-6 / SM-2']:,} SM-6/SM-2 + {intercept_by_cat['CIWS / SeaRAM']:,} CIWS + {intercept_by_cat['Naval Gun / Phalanx']:,} Gun)",
        f"US counterstrikes (TLAM/JASSM):  {fmt_cost(us_strike_cost)}"
        f" ({len(strike_events):,} rounds)",
        f"US ship/aircraft damage:         {fmt_cost(us_ship_damage)}",
        f"US total coalition cost:         {fmt_cost(total_us_cost)}",
        f"Exchange ratio:                  {exchange_ratio:.1f}:1"
        f" — coalition spends ${exchange_ratio:.1f} for every $1 of Iranian outlay.",
        f"US military casualties:          {us_mil_kia:,} KIA / {us_mil_wia:,} WIA",
        f"Collateral (Gulf shipping):      {fmt_cost(collateral_usd)}"
        f" | ~{int(collateral_kia):,} civilian KIA",
    )

    # ── VI. Strategic Assessment ──────────────────────────────────────────────
    if _n_neut >= 4:
        _strat = (
            "Fleet combat effectiveness falls below the 50% threshold — a strategic"
            " catastrophe without precedent in post-1945 naval warfare. US carrier"
            " aviation over the Persian Gulf is forfeit for 12–24 months pending"
            " hull replacement. Iran achieves its core A2/AD objective: the permanent"
            " denial of carrier-based strike capacity within the Gulf littoral."
            " Comparable in scale to the destruction of Force Z (HMS Prince of Wales"
            " and Repulse) in December 1941, but delivered in under two hours."
        )
    elif _n_neut >= 2:
        _strat = (
            f"{_n_neut} carrier groups destroyed — a historically unprecedented loss"
            " for the US Navy in the missile era. Remaining CSGs will almost certainly"
            " reposition outside ASCM range (~600–800 km), fundamentally constraining"
            " tactical aviation reach over Iranian territory. Iran achieves partial A2/AD"
            " success: US cannot sustain carrier-based air operations in the Gulf without"
            " accepting unacceptable risk to surviving hulls."
        )
    elif _n_neut == 1:
        _strat = (
            "A single carrier group destroyed — the first such loss since the Battle of"
            " Leyte Gulf (1944). Political and operational consequences are severe:"
            " remaining CSGs will likely assume a defensive posture pending Presidential"
            " and SECDEF authorization to continue offensive operations. Iran demonstrates"
            " the credibility of its A2/AD doctrine at the cost of its offensive missile"
            " stockpile."
        )
    elif _n_dmg >= 3:
        _strat = (
            "No CSGs destroyed but fleet combat power is materially degraded."
            f" {_n_dmg} damaged escorts require port evacuation, reducing the strike"
            " envelope by 30–50% until replacements arrive."
            " Iran fails its primary objective but imposes significant operational costs"
            f" — {exchange_ratio:.1f}:1 exchange ratio confirms the strategic tax of"
            " defending against mass-missile attack."
        )
    else:
        _strat = (
            "Fleet emerges largely intact. Iran's offensive expenditure fails to achieve"
            " A2/AD denial objectives. US retains full carrier aviation capacity;"
            " follow-on strike packages can proceed without attrition-driven delays."
            f" At {exchange_ratio:.1f}:1, US coalition costs vastly outstrip Iranian"
            " outlay — validating the cost-exchange logic of saturation attack doctrine"
            " even when operationally unsuccessful."
        )
    _VI = _para(
        "══ VI. STRATEGIC ASSESSMENT ═════════════════════════════════════════════",
        _strat,
    )

    # ── Dynamic scenario description (built from simulation results) ─────────
    _mc_ev: dict[str, int] = {}
    for _ev in events:
        _mc_ev[_ev["mname"]] = _mc_ev.get(_ev["mname"], 0) + 1
    _drone_mc   = {k: v for k, v in _mc_ev.items() if k in DRONE_TYPES}
    _missile_mc = {k: v for k, v in _mc_ev.items() if k not in DRONE_TYPES}
    _n_drones_fired   = sum(_drone_mc.values())
    _n_missiles_fired = sum(_missile_mc.values())

    def _fmt_mc(d: dict) -> str:
        return "; ".join(f"{v:,} {k}" for k, v in sorted(d.items(), key=lambda x: -x[1]))

    _is_detect_launch = scenario_config.get("iran_detection_launch", False)
    _iw_min           = scenario_config.get("iran_launch_window_s", 1800) // 60

    # --- SITUATION paragraph (scenario-specific qualitative framing) ---------
    if scenario_key == "low":
        _situation = (
            f"Iran executes a limited retaliatory probe using exclusively legacy munitions "
            f"from its pre-2020 inventory. Pre-emptive US/IAF strikes suppress {_supp:,} "
            f"rounds ({_supp_pct}%) of the intended {n_missiles:,}-round salvo before launch, "
            f"forcing the IRGC to rely on the most widely dispersed remaining assets. "
            f"This scenario establishes the floor of Iranian offensive capability and tests "
            f"whether legacy systems can penetrate a fully-alerted 8-CSG Aegis screen."
        )
    elif scenario_key == "medium":
        _situation = (
            f"Iran commits a mid-tier mixed salvo of {actual_launched:,} rounds, blending "
            f"legacy ballistics with second-generation cruise and anti-ship missiles. "
            f"Drone saturation is the primary CIWS exhaustion mechanism — slow-mover volume "
            f"creates firing corridors for the precision-guided missile follow-on. "
            f"Representative of Iran's most-probable employment doctrine under current "
            f"IRGCN operational planning."
        )
    elif scenario_key == "realistic":
        _situation = (
            f"Iranian air-defense radar detects incoming Israeli aircraft and Iran immediately "
            f"launches its entire available inventory — {actual_launched:,} munitions — in a "
            f"compressed {_iw_min}-minute window with no phase separation. Every missile and "
            f"drone departs before a single US/IAF round can land (~45–90 min flight time). "
            f"This represents the intelligence community's most credible Iranian launch doctrine, "
            f"consistent with the April 2024 response: 170 drones + 30 cruise missiles + "
            f"110 ballistic missiles fired simultaneously against Israel."
        )
    elif scenario_key == "high":
        _situation = (
            f"Iran commits its full available strike inventory — {actual_launched:,} munitions "
            f"across all operational systems — against the 8-CSG battle group. The salvo "
            f"represents Iran's maximum sustainable single-engagement output: simultaneous "
            f"launch from all {n_sites_destroyed + len(site_inactive_at)} coastal and inland "
            f"complexes, designed to exhaust VLS magazines before the decisive terminal phase."
        )
    elif scenario_key == "iran_best":
        _situation = (
            f"Maximum Iranian capability: {actual_launched:,} rounds launched with zero "
            f"pre-launch suppression — US counterstrikes arrive too late to silence a single "
            f"site before Iran's salvo completes. AI-guided Shahed-136 terminal variants "
            f"({actual_ai:,} airframes, {round(100*actual_ai/max(1,actual_launched),1)}% of salvo) "
            f"defeat CIWS lead-angle prediction through erratic final-approach maneuvers, "
            f"guaranteeing breakthrough. VLS magazines face exhaustion before the final "
            f"salvo phases, leaving late-arriving rounds against degraded terminal defenses."
        )
    elif scenario_key == "usa_best":
        _situation = (
            f"Maximum US pre-emption: {_supp:,} Iranian rounds ({_supp_pct}%) destroyed on "
            f"the ground before launch. US/IAF strikes suppress {n_sites_destroyed}/{len(_sc_sites)} launch "
            f"complexes within the first engagement hour. Only {actual_launched:,} rounds "
            f"reach flight — residual mobile launchers that survived the strike package. "
            f"This scenario validates the strategic premium of offensive counter-force action: "
            f"catching Iran's missiles on the ground is decisively superior to intercepting "
            f"them in flight."
        )
    elif scenario_key == "drone_first_low":
        _situation = (
            f"Iran employs a deliberate phase-sequenced doctrine at low scale "
            f"({actual_launched:,} total rounds): an initial drone swarm exhausts CIWS and "
            f"SM-6 inventory before the main ballistic/cruise missile strike arrives while "
            f"Aegis is partially depleted. The phased approach trades simultaneous mass for "
            f"a tactically superior defended-bearer/follow-on structure."
        )
    elif scenario_key == "drone_first_medium":
        _situation = (
            f"Phased drone-then-missile doctrine at medium scale ({actual_launched:,} rounds). "
            f"The {_n_drones_fired:,}-drone saturation phase depletes CIWS magazines and "
            f"SM-6 inventory before the main ballistic salvo, increasing breakthrough "
            f"probability for high-value anti-ship missiles. Represents an evolved Iranian "
            f"operational concept beyond simple mass-launch saturation."
        )
    elif scenario_key == "drone_first_high":
        _situation = (
            f"Maximum phased drone-then-missile doctrine ({actual_launched:,} total rounds). "
            f"The {_n_drones_fired:,}-drone wave is scaled to guarantee VLS exhaustion across "
            f"all 8 CSGs before the follow-on ballistic salvo. Every surviving SM-6 faces an "
            f"oversaturated terminal engagement window against the subsequent missile storm."
        )
    elif scenario_key == "coordinated_strike":
        _situation = (
            f"Iran coordinates its {actual_launched:,}-round salvo with Israeli offensive "
            f"air operations, forcing Aegis to simultaneously track inbound Iranian missiles "
            f"and provide mutual fire support. Joint IAF/USN counterstrike packages — "
            f"{len(iaf_events):,} IAF sorties alongside {len(strike_events):,} VLS strike "
            f"rounds — engage the Iranian launch network from multiple vectors, complicating "
            f"IRGC retargeting and saturation timing."
        )
    elif scenario_key == "focused_salvo":
        _situation = (
            f"Iran concentrates its entire {actual_launched:,}-round salvo on a single "
            f"high-value target: {scenario_config.get('focus_csg', 'the lead CSG')}. The focused salvo "
            f"trades geographic dispersion for probability-of-kill — one carrier's Aegis "
            f"screen faces a locally oversaturated engagement envelope while the remaining "
            f"7 CSGs receive zero incoming threat. Mirrors the 1944 kamikaze doctrine of "
            f"deliberate individual ship targeting over area saturation."
        )
    elif scenario_key == "hypersonic_threat":
        _situation = (
            f"Iran employs Fattah-1 hypersonic glide vehicles as the primary strike weapon "
            f"in a {actual_launched:,}-round mixed salvo. The Fattah-1's Mach 13–15 terminal "
            f"phase compresses SM-6 engagement windows to under 20 seconds; current Aegis "
            f"intercept probability against HGVs is estimated at 5–15%. Ballistic and cruise "
            f"missiles provide sensor saturation while HGVs exploit the resulting fire-control "
            f"queue degradation."
        )
    elif scenario_key == "ballistic_barrage":
        _situation = (
            f"Iran deploys a ballistic-dominant salvo of {actual_launched:,} rounds weighted "
            f"toward Shahab-3/Emad MRBMs and Zolfaghar/Fateh SRBMs. High-arc trajectories "
            f"compress Aegis engagement timelines to 40–90 seconds per incoming missile. "
            f"Saturation is achieved through volume rather than speed — overwhelming "
            f"fire-control track capacity rather than defeating individual intercept "
            f"probabilities."
        )
    elif scenario_key == "ballistic_surge":
        _n_hgv_fired = sum(1 for m in _all_events_for_stats if m.get("munition") == "Fattah-1 HGV") if "_all_events_for_stats" in dir() else int(actual_launched * 0.10)
        _situation = (
            f"Iran commits its full reconstituted ballistic missile stockpile — "
            f"{actual_launched:,} rounds — in a single coordinated volley against the 8-CSG "
            f"fleet. No drones. Every round carries a 450–750 kg unitary warhead or a Mach 13+ "
            f"hypersonic glide payload. At ~{actual_launched // 8:,} inbound per CSG, "
            f"Aegis fire-control queues are oversubscribed ~17× — arithmetic overwhelms the "
            f"18-simultaneous-channel SM-6 guidance ceiling before the salvo reaches midcourse. "
            f"The {int(actual_launched * 0.10):,} Fattah-1 HGVs mixed into the barrage face "
            f"~10% intercept probability each, virtually guaranteeing CVN-hull impacts from "
            f"that layer alone. This scenario tests whether sheer ballistic volume, even "
            f"without drone CIWS-saturation support, can defeat the integrated Aegis network "
            f"through queue exhaustion rather than kinematic evasion."
        )
    elif scenario_key == "ascm_swarm":
        _situation = (
            f"Iran launches a pure anti-ship cruise missile swarm of {actual_launched:,} rounds, "
            f"foregoing ballistic delivery in favor of sea-skimming ASCMs that approach below "
            f"radar horizon and defeat over-the-horizon targeting. Noor ASCMs and CM-302 "
            f"supersonic variants form the core strike package. This scenario most closely "
            f"mirrors the 1982 Falklands (Exocet) and 1967 Eilat sinkings — ASCM saturation "
            f"of point-defense systems at close engagement ranges."
        )
    elif scenario_key == "shore_based_defense":
        _situation = (
            f"Iran activates shore-based defensive systems alongside its {actual_launched:,}-round "
            f"offensive salvo, constraining CSG positioning and complicating US naval approach. "
            f"Khalij Fars ASBMs and Noor ASCM batteries operate from hardened coastal positions "
            f"while the main salvo degrades Aegis intercept capacity. The combined A2/AD plus "
            f"offensive strike posture represents Iran's preferred warfighting doctrine for "
            f"Persian Gulf area-denial."
        )
    elif scenario_key == "strait_transit":
        _situation = (
            f"A US CSG conducts a contested transit of the Strait of Hormuz — minimum width "
            f"39 km — while Iran launches a {actual_launched:,}-round salvo from elevated "
            f"terrain commanding both shores. The constrained channel eliminates CSG maneuver "
            f"advantage and reduces effective radar horizon. Khalij Fars ASBMs fired from "
            f"Qeshm Island achieve minimal range-to-target, compressing Aegis reaction time "
            f"to seconds per incoming round. The USS Stark (FFG-31) precedent — struck by "
            f"two Exocets at 37 km range in 1987 in the same strait — informs threat modeling."
        )
    elif scenario_key == "caves":
        _n_cave_sites = len(_sc_sites)
        _n_cave_surv  = _n_cave_sites - n_sites_destroyed
        _situation = (
            f"Iran disperses its {actual_launched:,}-round salvo across {_n_cave_sites} "
            f"hardened mountain cave/tunnel complexes distributed throughout the Zagros, "
            f"Alborz, and eastern Iranian highlands. Each cave requires only {_sc_threshold} "
            f"direct hits to neutralize — but with {_n_cave_sites} targets spread across "
            f"Iran's full geographic depth, US TLAM/JASSM strikes are diluted across a far "
            f"larger target set than the standard 12-site coastal network. "
            f"{_n_cave_surv} of {_n_cave_sites} cave complexes survived the counterstrike "
            f"and continued launching throughout the engagement. "
            f"This scenario tests whether geographic dispersal and hardening depth can "
            f"compensate for per-site fragility — and whether TLAMs and JASSM-ER can "
            f"realistically destroy cave-tunnel infrastructure without GBU-57 MOP delivery "
            f"by B-2 stealth bombers (not modeled in this simulation)."
        )
    elif scenario_key == "depleted_drone_first":
        _situation = (
            f"Iran's offensive inventory has been reduced to approximately 8% of its "
            f"pre-conflict baseline through sustained US/IAF attrition operations — "
            f"leaving only {actual_launched:,} munitions available fleet-wide. Despite "
            f"the degraded arsenal, IRGC planners still execute the phased drone-first "
            f"doctrine launching from 25 cave/tunnel complexes: {_n_drones_fired:,} drones "
            f"launch in Phase 1 to exhaust CIWS magazines and draw down SM-6 inventory "
            f"before the {_n_missiles_fired:,}-round ballistic/cruise follow-on. At this "
            f"scale, the 8 CSG Aegis screen is not saturation-threatened — defenses have "
            f"sufficient depth to engage each track individually. The strategic question is "
            f"whether any breakthrough occurs at all, or whether this represents the effective "
            f"lower bound of Iranian offensive capability."
        )
    elif scenario_key == "depleted_coastal":
        _situation = (
            f"Iran's offensive inventory has been reduced to approximately 8% of its "
            f"pre-conflict baseline, leaving only {actual_launched:,} munitions available. "
            f"In this variant, remaining forces are concentrated at the standard 12 coastal "
            f"launch sites rather than dispersed cave complexes — making them more exposed "
            f"to TLAM/JASSM suppression. The phased drone-first doctrine is maintained: "
            f"{_n_drones_fired:,} drones in Phase 1 followed by {_n_missiles_fired:,} "
            f"ballistic/cruise missiles. Coastal launch site vulnerability means US "
            f"counterstrikes suppress a higher fraction of launch capacity before the "
            f"salvo completes, directly comparing the strategic value of hardened cave "
            f"dispersal vs. coastal concentration at depleted inventory levels."
        )
    elif scenario_key == "depleted_israel_split":
        _n_waves = scenario_config.get("israel_drone_alternation", 4)
        _situation = (
            f"Iran simultaneously retaliates against both the US CSG fleet and Israel, "
            f"splitting its depleted {n_missiles}-munition inventory across two fronts using "
            f"alternating drone waves: wave 1 \u2192 Persian Gulf, wave 2 \u2192 Israel, "
            f"wave 3 \u2192 Gulf, wave 4 \u2192 Israel ({_n_waves} sub-windows across the "
            f"{int(phase1_end/3600)}-hour drone phase). {n_israel_diverted:,} Shahed-136 "
            f"long-range drones are vectored toward Israel via Iraqi/Syrian airspace at "
            f"~2,200 km range. IRGCN sea drones cannot reach Israel and remain on the Gulf "
            f"axis alongside all ballistic/cruise missiles. The Gulf-facing salvo is "
            f"{actual_launched:,} munitions: {_n_drones_fired:,} drones + "
            f"{_n_missiles_fired:,} ballistic/cruise missiles. The alternating wave pattern "
            f"means the Gulf drone swarm arrives in two discrete surges rather than one "
            f"continuous stream — giving Aegis momentary respite between drone waves to "
            f"reset engagement queues, while Israel simultaneously absorbs a comparable "
            f"Shahed strike that ties down IAF interception resources and reduces the joint "
            f"US/IAF counter-strike effectiveness against Iranian launch sites."
        )
    else:
        _situation = (
            f"Iran executes a {actual_launched:,}-round salvo against 8 US Carrier Strike "
            f"Groups in the Persian Gulf."
        )

    # --- PHASE 1 — Drone/surface swarm block --------------------------------
    if _n_drones_fired > 0:
        _ph1_timing = (
            f"simultaneous with missile salvo, T+0–{_iw_min} min (detection-launch)"
            if _is_detect_launch
            else f"T+0 to T+{int(phase1_end/60)} min"
        )
        _phase1_block = (
            f"PHASE 1 — DRONE / SURFACE SWARM ({_ph1_timing}): {_n_drones_fired:,} unmanned "
            f"systems across {len(_drone_mc)} type(s): {_fmt_mc(_drone_mc)}. "
            + (
                f"Track density at this scale saturates CIWS engagement queuing across all "
                f"8 CSG defensive sectors simultaneously."
                if _n_drones_fired >= 1000
                else
                f"Drone track density degrades CIWS engagement throughput, reserving residual "
                f"intercept capacity for the follow-on missile wave."
            )
        )
    else:
        _phase1_block = ""

    # --- PHASE 2 — Strike package block -------------------------------------
    if _n_missiles_fired > 0:
        if _is_detect_launch:
            _ph2_timing = f"simultaneous with Phase 1, T+0–{_iw_min} min"
        else:
            _ph2_timing = (
                f"T+{int(phase2_start/60)} to "
                f"T+{int((phase2_start + phase2_dur)/60)} min"
            )
        _phase2_block = (
            f"PHASE 2 — STRIKE PACKAGE ({_ph2_timing}): {_n_missiles_fired:,} ballistic "
            f"and cruise missiles across {len(_missile_mc)} type(s): {_fmt_mc(_missile_mc)}."
        )
    else:
        _phase2_block = ""

    # --- US RESPONSE block --------------------------------------------------
    _us_resp_block = (
        f"US RESPONSE: {len(strike_events) + len(iaf_events):,} strike sorties "
        f"({len(strike_events):,} TLAM/JASSM + {len(iaf_events):,} IAF Rampage/SPICE/JDAM-ER) "
        f"target {n_sites_destroyed}/{len(_sc_sites)} Iranian launch complexes"
        + (f" ({sites_destroyed_names})" if n_sites_destroyed > 0 else "")
        + f". Pre-launch suppression eliminates {_supp:,} rounds ({_supp_pct}%) "
        f"of the planned {n_missiles:,}-round salvo before flight."
    )

    # --- ASSESSMENT block ---------------------------------------------------
    _csg_outcome_str = (
        f"{_n_neut} CSG(s) DESTROYED | {_n_sunk} SUNK | {_n_dmg} DAMAGED | {_n_intact} INTACT"
    )
    _assess_block = (
        f"ASSESSMENT: US Aegis defenses achieve a {_int_pct}% intercept rate, destroying "
        f"{actual_intercepted:,} of {actual_launched:,} rounds over ~{dur_min:.0f} minutes "
        f"of continuous engagement. {actual_breakthrough:,} rounds ({_bt_pct}%) penetrate to "
        f"fleet engagement range. Fleet outcome: {_csg_outcome_str}. "
        f"Cost-exchange ratio: {exchange_ratio:.1f}:1 (coalition expenditure vs. Iran outlay)."
    )

    _dyn_desc = "\n\n".join(
        filter(None, [_situation, _phase1_block, _phase2_block, _us_resp_block, _assess_block])
    )
    costs["dyn_desc"] = _dyn_desc

    stats = (
        "\n\n".join([_I, _II, _III, _IV, _V, _VI])
        + f"\n\n══ PER-CSG BATTLE DAMAGE ASSESSMENT ═════════════════════════════════════\n"
        + csg_table
        + f"\n\n══ COST DETAIL ══════════════════════════════════════════════════════════\n"
        + cost_block
    )

    legend_lines = [
        "COLOR LEGEND",
        "============",
        "IRAN OFFENSIVE",
        "  Drones (yellow family):",
        "    Shahed-136 air drone        = YELLOW",
        "    IRGCN surface drone         = AMBER-YELLOW",
        "    AI-guided Shahed terminal   = WHITE (re-acquisition arc only)",
        "  Anti-ship missiles (red family):",
        "    Noor ASCM (subsonic)        = VIVID RED",
        "    Khalij Fars ASBM            = CRIMSON RED",
        "    CM-302 Supersonic ASCM      = SCARLET RED",
        "  Ballistic missiles (warm tones):",
        "    Fateh-110 / Fateh-313 SRBM  = AMBER",
        "    Shahab-3 MRBM               = AMBER-ORANGE",
        "    Zolfaghar SRBM              = ORANGE-RED",
        "    Emad MRBM                   = DEEP RED",
        "    Fattah-1 HGV                = MAGENTA (hypersonic, beyond red scale)",
        "",
        "US / COALITION",
        "  Anti-ground strikes (green family):",
        "    TLAM Block IV               = LIME GREEN",
        "    JASSM-ER                    = FOREST GREEN",
        "    IAF JDAM-ER                 = LIME-TEAL",
        "    IAF Rampage ALCM            = TEAL",
        "    IAF SPICE-2000              = DARK GREEN",
        "  Interceptors (blue family):",
        "    SM-6 / SM-2 (low scenario)  = LIGHT STEEL BLUE (star icon)",
        "    SM-6 / SM-2 (medium)        = CORNFLOWER BLUE (star icon)",
        "    SM-6 / SM-2 (high scenario) = NAVY BLUE (star icon)",
        "    CIWS / SeaRAM               = SKY BLUE (circle icon)",
        "    Naval Gun / Phalanx         = AZURE BLUE (circle icon)",
        "",
        "MARKERS",
        "  Orange star   = intercept kill point",
        "  Red target    = Iranian missile impact",
        "  Blue star     = US strike impact on Iranian site",
    ]
    for mname, mdef in MUNITIONS.items():
        if any(m["name"] == mname for m in scenario_config["munitions"]):
            legend_lines.append(f"  [{mname}] {mdef['label']}")
    legend = "\n".join(legend_lines)

    tour_kml      = gen_tour(tenth_hit_s, dur_min * 60, scenario_config["label"],
                              csg_fleet=csg_fleet, hits_timeline=hits_timeline)
    flash_markers = gen_csg_tour_flash_markers(csg_fleet, tenth_hit_s)

    # ── Dynamic legend ScreenOverlays (one per CSG-destruction state) ─────────
    _legend_states = []
    if out_dir:
        _legend_states = generate_dynamic_legend_pngs(
            scenario_key, scenario_config, events, csg_fleet,
            first_hit_s, tenth_hit_s, costs, dur_min * 60, out_dir)
    _screen_overlays = gen_scenario_screen_overlays(_legend_states)

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document id="doc_main">
  <name>{scenario_config['label']}</name>
  <LookAt>
    <longitude>55.5</longitude>
    <latitude>26.5</latitude>
    <altitude>0</altitude>
    <range>900000</range>
    <tilt>45</tilt>
    <heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
  <description><![CDATA[<div style="font-family:'Courier New',Courier,monospace;background:#000000;color:#ffffff;padding:13px 15px;border-left:3px solid #3399ff;">
<div style="color:#3399ff;font-weight:bold;font-size:13px;letter-spacing:2px;margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid #333333;">&#9670; PERSIAN GULF WARGAME</div>
<p style="margin:0 0 10px 0;">
  <a href="scenario_{scenario_key}.html"
     style="color:#3399ff;font-weight:bold;font-size:12px;text-decoration:none;">
    &#128196; Full HTML Report &rarr; scenario_{scenario_key}.html
  </a>
  &nbsp;&nbsp;
  <a href="summary.html" style="color:#aaaaaa;font-size:11px;text-decoration:none;">&#128200; Summary</a>
</p>
<pre style="color:#cccccc;font-size:11px;white-space:pre-wrap;margin:0 0 8px 0;">{_dyn_desc}</pre>
<hr style="border:none;border-top:1px solid #333333;margin:8px 0;"/>
<pre style="color:#777777;font-size:10px;margin:0 0 4px 0;">{stats}</pre>
<pre style="color:#777777;font-size:10px;margin:0 0 6px 0;">{legend}</pre>
<p style="color:#555555;font-size:10px;margin:0;">Simulation start: {fmt_time(SIM_START)}<br/>Use the Google Earth timeline slider to animate. Play "Battle Tour" for automated flythrough.</p>
</div>]]></description>
{kml_styles()}

{_screen_overlays}

{tour_kml}

  <Folder>
    <name>Tour Flash Markers</name><visibility>0</visibility><open>0</open>
    <description>Hidden Placemarks with stable IDs targeted by gx:AnimatedUpdate in the Battle Tour to flash destroyed CSG icons.</description>
{flash_markers}  </Folder>

  <Folder>
    <name>US Forces -- 8 Carrier Strike Groups</name><visibility>1</visibility>
{gen_us_forces(first_hit_s, tenth_hit_s, asset_end_s, csg_fleet, hits_timeline)}
{"".join(f'''  <Folder>
    <name>{c["name"]} — Ship Formation (10 hulls)</name><visibility>1</visibility><open>0</open>
{gen_csg_ship_kml(c, csg_ships[c["name"]], ship_destroyed_at, group_stopped_at, asset_end_s)}
  </Folder>''' for c in csg_fleet)}
  </Folder>

  <Folder>
    <name>Iranian Launch Network ({n_sites_destroyed} sites destroyed)</name><visibility>1</visibility>
{gen_iran_sites(site_inactive_at, site_hits_timeline, asset_end_s, sites=_sc_sites, threshold=_sc_threshold)}
  </Folder>

  <Folder>
    <name>US Counterstrikes -- {len(strike_events)} TLAM/JASSM / {n_sites_destroyed} sites destroyed</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{mtype} ({len(segs)} tracks)</name><open>0</open>
{"".join(segs)}
    </Folder>''' for mtype, segs in strike_segs.items() if segs)}
    <Folder>
      <name>Strike Impact Points ({len(strike_impacts)})</name><open>0</open>
{"".join(strike_impacts)}
    </Folder>
  </Folder>

  <Folder>
    <name>Iranian Munitions -- {actual_launched} launched / {actual_intercepted} intercepted / {actual_breakthrough} breakthrough</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{mn} ({len(missile_segs[mn])} track-segs)</name><open>0</open>
{"".join(missile_segs[mn])}
    </Folder>''' for mn in _mnames if missile_segs[mn])}
  </Folder>

  <Folder>
    <name>US Interceptor Tracks -- {actual_intercepted} kills</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{cat} ({len(segs)} track-segs)</name><open>0</open>
{"".join(segs)}
    </Folder>''' for cat, segs in sm6_segs.items() if segs)}
  </Folder>

  <Folder>
    <name>Intercept Kill Points -- {actual_intercepted}</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{mn} kills ({len(intercept_pts[mn])})</name><open>0</open>
{"".join(intercept_pts[mn])}
    </Folder>''' for mn in _mnames if intercept_pts[mn])}
  </Folder>

  <Folder>
    <name>CEP Impact Zones -- ballistic in-flight (~15% sampled)</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{mn} CEP zones ({len(cep_circles[mn])})</name><open>0</open>
{"".join(cep_circles[mn])}
    </Folder>''' for mn in _mnames if cep_circles[mn])}
  </Folder>

  <Folder>
    <name>Breakthrough Impacts -- {actual_breakthrough}</name><visibility>1</visibility><open>0</open>
{"".join(f'''    <Folder>
      <name>{mn} impacts ({len(impact_pts[mn])})</name><open>0</open>
{"".join(impact_pts[mn])}
    </Folder>''' for mn in _mnames if impact_pts[mn])}
  </Folder>

  <Folder>
    <name>IAF Air Support -- {len(iaf_events)} strikes (F-35I/F-15I/F-16I)</name><visibility>1</visibility><open>0</open>
    <Folder>
      <name>IAF Bases</name><open>0</open>
{"".join(f'''      <Placemark><name>{b["name"]}</name><styleUrl>#iaf_base_marker</styleUrl>
      <description>{b["aircraft"]} | {b["sorties"]} sorties | {b["per_sortie"]} {b["munition"]}/sortie</description>
      <Point><coordinates>{b["lon"]:.4f},{b["lat"]:.4f},0</coordinates></Point></Placemark>''' for b in IAF_BASES)}
    </Folder>
{"".join(f'''    <Folder>
      <name>{mtype} ({len(segs)} tracks)</name><open>0</open>
{"".join(segs)}
    </Folder>''' for mtype, segs in iaf_segs.items() if segs)}
    <Folder>
      <name>IAF Impact Points ({len(iaf_impacts)})</name><open>0</open>
{"".join(iaf_impacts)}
    </Folder>
  </Folder>

  <Placemark id="time_cursor">
    <name/>
    <visibility>0</visibility>
    <TimeStamp><when>{fmt_time(sim_time(0))}</when></TimeStamp>
    <Point><coordinates>55.5,26.5,0</coordinates></Point>
  </Placemark>

</Document>
</kml>"""

    return kml, _legend_states, actual_launched, actual_intercepted, actual_breakthrough, dur_min, costs

# ============================================================
# MASTER KML
# ============================================================

def generate_master(stats):
    # BalloonStyle block for black popups in the master KML
    black_balloon_style = (
        '<BalloonStyle>'
        '<bgColor>ff000000</bgColor>'
        '<textColor>ffffffff</textColor>'
        '<text>$[description]</text>'
        '</BalloonStyle>'
    )

    entries = []
    for scenario_key, (scenario_label, n_launched, n_intercepted, n_breakthrough, duration_min) in stats.items():
        html_report_link = f"scenarios/scenario_{scenario_key}.html"
        summary_text = (
            f"{n_intercepted}/{n_launched} intercepted | "
            f"{n_breakthrough} breakthrough | "
            f"~{duration_min:.0f} min"
        )
        balloon_description = (
            "<![CDATA["
            f'<div style="background:#000000;color:#ffffff;font-family:Courier New,monospace;'
            f'padding:12px 15px;margin:-15px -15px -20px -15px;'
            f'border-left:3px solid #3399ff;border-top:2px solid #3399ff;">'
            f'<div style="color:#3399ff;font-weight:bold;font-size:13px;'
            f'letter-spacing:2px;margin-bottom:8px;padding-bottom:6px;'
            f'border-bottom:1px solid #333333;">{scenario_label}</div>'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<tr><td style="color:#aaaaaa;padding:4px 14px 4px 0;font-size:11px">Launched</td>'
            f'<td style="color:#ffffff;font-weight:bold">{n_launched:,}</td></tr>'
            f'<tr style="background:#0a0a0a"><td style="color:#aaaaaa;padding:4px 14px 4px 0;font-size:11px">Intercepted</td>'
            f'<td style="color:#00dd66;font-weight:bold">{n_intercepted:,}</td></tr>'
            f'<tr><td style="color:#aaaaaa;padding:4px 14px 4px 0;font-size:11px">Breakthrough</td>'
            f'<td style="color:#ff3333;font-weight:bold">{n_breakthrough:,}</td></tr>'
            f'<tr style="background:#0a0a0a"><td style="color:#aaaaaa;padding:4px 14px 4px 0;font-size:11px">Duration</td>'
            f'<td style="color:#ffffff;font-weight:bold">~{duration_min:.0f} min</td></tr>'
            f'</table>'
            f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid #333333;">'
            f'<a href="{html_report_link}" style="color:#3399ff">Open detailed HTML report →</a>'
            f'</div>'
            f'</div>'
            "]]>"
        )
        entries.append(
            f"\n  <NetworkLink>"
            f"<name>{scenario_label}  [{summary_text}]</name>"
            f"<description>{balloon_description}</description>"
            f"<Style>{black_balloon_style}</Style>"
            f"<visibility>0</visibility>"
            f"<Link><href>scenarios/scenario_{scenario_key}.kmz</href></Link>"
            f"</NetworkLink>"
        )

    legend_lines = ["Global color legend (all scenarios):"]
    for mdef in MUNITIONS.values():
        legend_lines.append(f"  {mdef['label']}")
    for sdef in US_STRIKE_MUNITIONS.values():
        legend_lines.append(f"  {sdef['label']}")
    legend_lines.append("  US SM-6 interceptors = white | CIWS = lime green")
    legend_lines.append("  Amber/cyan-green tracks = US TLAM/JASSM strikes outbound to Iran sites")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Persian Gulf Wargame -- All Scenarios (8 CSGs)</name>
  <description>Eight-CSG simulation of Iranian mass-missile attacks on US Carrier Strike Groups.
US TLAM/JASSM counterstrikes destroy Iranian launch sites after 25 hits each.

Toggle scenarios with the folder checkboxes.
Use the Google Earth timeline slider to animate missile flights, intercepts, and impacts.
Each munition type has a distinct color; breakthrough tracks are brighter/thicker.
Amber/cyan-green arcs = US outbound TLAM/JASSM strikes; sites go gray when destroyed.
Click any scenario entry below to open its detailed stats balloon and HTML report link.

8 Carrier Strike Groups:
  USS Abraham Lincoln (CVN-72) | USS Gerald R. Ford (CVN-78) | USS George H.W. Bush (CVN-77)
  CSG Alpha (Arabian Sea) | CSG Bravo (N. Gulf) | CSG Charlie (C. Gulf)
  CSG Delta (S. Gulf) | CSG Echo (Hormuz approaches)

Armament estimates (unclassified, open-source):
  SM-6 per CSG: 24–66 rds (240 km)  |  SM-2: 60–203 rds (167 km)
  ESSM: 96–160 rds (50 km)           |  RAM: 42–105 rds (15 km)
  TLAM strike capacity: 48–128 rds per CSG
  Sources: CRS RL33199; IISS Military Balance 2024; influenceofhistory.blogspot.com

── Simultaneous launch (A–F) ──────────────────────────────────────────────────
Scenario A -- Low:           1,065 total   69% kill     ~335 breakthrough  US fires 160 strikes
Scenario B -- Medium:        2,200 total   65% kill     ~793 breakthrough  US fires 240 strikes
Scenario C -- High (CAP):    4,030 total  CAP HIT     ~2,046 breakthrough  US fires 320 strikes  [intercept cap breached]
Scenario D -- Realistic:     7,250 total   58% kill   ~3,045 breakthrough  US fires 240 strikes  [detection-launch]
Scenario E -- Iran Best:     5,400 total  CAP HIT     ~3,419 breakthrough  US fires 320 strikes  [intercept cap breached]
Scenario F -- USA Best:        665 total   93% kill       ~51 breakthrough  US fires 480 strikes  [all sites destroyed]
── Phased launch: drones first (hr 0–1), then missiles (hr 1–2) ───────────────
Scenario G -- Drone-First Low:    1,065 total  65% kill    ~375 breakthrough  (+40 vs A)
Scenario H -- Drone-First Medium: 2,200 total  60% kill    ~892 breakthrough  (+99 vs B)
Scenario I -- Drone-First High:   4,030 total  46% kill  ~2,188 breakthrough  (+142 vs C, CIWS exhausted)
── Coordinated / special strikes ──────────────────────────────────────────────
Scenario J -- Coordinated Strike: 7,250 total  78% kill    ~441 breakthrough  [US/IAF perfect timing]
Scenario K -- Focused Salvo:      7,250 total  63% kill    ~713 breakthrough  [all fire on CVN-78 Ford]
Scenario L -- Hypersonic Threat:  7,250 total  63% kill    ~820 breakthrough  [Fattah-1 HGV near-uninterceptable]
Scenario M -- Ballistic Barrage:    600 total  85% kill     ~90 breakthrough  [pure ballistic, no drones]
Scenario N -- ASCM Swarm:         1,000 total  55% kill    ~450 breakthrough  [sea-skimming saturation]
Scenario O -- Shore Defense:      7,250 total  85% kill    ~301 breakthrough  [THAAD+PAC-3+Aegis three-tier]
Scenario P -- Strait Transit:     7,250 total  55% kill    ~878 breakthrough  [column transit, max threat]
Scenario Q -- Cave Network:       7,250 total  58% kill  ~3,045 breakthrough  [25 hardened cave/tunnel sites]
── 1% inventory probe-and-strike ─────────────────────────────────────────────
Scenario Z -- 1% Probe+Lull+Strike:   75 total  83% kill    ~13 breakthrough  [drone probe → 60-min ISR lull → precision follow-on]
Scenario AA -- 1% + 10 Fattah-2 HGVs: 75 total  67% kill    ~25 breakthrough  [10 secured HGVs in cave tunnels — 9-10 near-uninterceptable strikes]
── Depleted arsenal (8% inventory) ───────────────────────────────────────────
Scenario R -- Depleted Drone-First:   580 total  52% kill  ~278 breakthrough  [drone-wave first, cave sites]
Scenario S -- Depleted Coastal:       580 total  53% kill  ~273 breakthrough  [all 37 sites]
Scenario T -- Depleted Israel Split:  412 total  51% kill  ~202 breakthrough  [50% Shaheds diverted to Israel]
── US-wins conditions ────────────────────────────────────────────────────────
Scenario U -- US Wins: Preemption:        280 total  89% kill   ~31 breakthrough  [P_win ≈ 94%]
Scenario V -- US Wins: EW Dominance:      450 total  91% kill   ~41 breakthrough  [P_win ≈ 88%]
Scenario W -- US Wins: Allied Umbrella:   550 total  92% kill   ~44 breakthrough  [P_win ≈ 83%]
Scenario X -- US Wins: C2 Disrupted:      900 total  93% kill   ~63 breakthrough  [P_win ≈ 71%]
Scenario Y -- US Wins: Arsenal Attrited:  750 total  91% kill   ~68 breakthrough  [P_win ≈ 65%]

{chr(10).join(legend_lines)}

Simulation clock starts: {fmt_time(SIM_START)}</description>
{"".join(entries)}
</Document>
</kml>"""

# ============================================================
# LEGEND PNG GENERATOR
# ============================================================

def _kml_color_to_rgb(kml_hex):
    """Convert AABBGGRR KML hex string to (R,G,B) tuple."""
    kml_hex = kml_hex.lstrip("#")
    if len(kml_hex) == 8:
        # aa bb gg rr
        r = int(kml_hex[6:8], 16)
        g = int(kml_hex[4:6], 16)
        b = int(kml_hex[2:4], 16)
        return (r, g, b)
    return (128, 128, 128)


def generate_legend_png(scenario_key, sc, costs, n_launched, n_int, n_bt, dur_min, out_dir):
    """
    Generate a standalone PNG legend card for a scenario.
    Saved to out_dir/legend_<scenario_key>.png.
    Requires Pillow (pip install Pillow).
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None   # Pillow not installed — skip silently

    # ── Layout constants ─────────────────────────────────────────────────────
    W           = 540
    PAD         = 14
    SWATCH_W    = 22
    SWATCH_H    = 14
    ROW_H       = 22
    TITLE_H     = 36
    STATS_H     = 90
    SECTION_H   = 20
    BG          = (18, 22, 38)        # dark navy background
    FG          = (230, 230, 230)     # light grey text
    ACCENT      = (80, 160, 255)      # blue accent for headers
    DIVIDER     = (50, 55, 75)        # subtle horizontal rule colour

    # ── Font setup ───────────────────────────────────────────────────────────
    def _load_font(size, bold=False):
        """Try system fonts; fall back to PIL default."""
        candidates = []
        if bold:
            candidates = [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        else:
            candidates = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_title  = _load_font(15, bold=True)
    font_header = _load_font(11, bold=True)
    font_body   = _load_font(11)
    font_small  = _load_font(10)

    # ── Build munition rows for this scenario ────────────────────────────────
    mun_rows = []   # (color_rgb, label_text)
    for mname, mdef in MUNITIONS.items():
        if any(m["name"] == mname for m in sc["munitions"]):
            rgb   = _kml_color_to_rgb(mdef["color_bt"])
            label = mdef["label"].split("(")[0].strip()
            mun_rows.append((rgb, label))

    # US anti-ground strikes
    for _, sdef in US_STRIKE_MUNITIONS.items():
        rgb   = _kml_color_to_rgb(sdef["color"])
        label = sdef["label"].split("(")[0].strip()
        mun_rows.append((rgb, label))

    # Fixed interceptor entries
    interceptor_rows = [
        ((136, 204, 255), "SM-6 / SM-2  (low scenario)"),
        ((68,  136, 255), "SM-6 / SM-2  (medium)"),
        ((0,    68, 255), "SM-6 / SM-2  (high scenario)"),
        ((0,   153, 255), "CIWS / SeaRAM"),
        ((51,  153, 255), "Naval Gun / Phalanx"),
    ]

    # ── Compute total image height ────────────────────────────────────────────
    H = (PAD + TITLE_H + PAD + STATS_H + PAD
         + SECTION_H + len(mun_rows) * ROW_H
         + SECTION_H + len(interceptor_rows) * ROW_H
         + PAD)

    img  = Image.new("RGBA", (W, H), BG + (240,))
    draw = ImageDraw.Draw(img)

    y = PAD

    # ── Title ─────────────────────────────────────────────────────────────────
    label_text = sc["label"]
    draw.text((PAD, y), label_text, font=font_title, fill=ACCENT)
    y += TITLE_H

    # ── Stats block ──────────────────────────────────────────────────────────
    draw.line([(PAD, y), (W - PAD, y)], fill=DIVIDER, width=1)
    y += 6

    def fc(usd):
        return f"${usd/1e9:.2f}B" if usd >= 1e9 else f"${usd/1e6:.1f}M"

    stat_lines = [
        f"Launched: {n_launched:,}   |   Intercepted: {n_int:,}   |   Breakthrough: {n_bt:,}",
        f"Duration: ~{dur_min:.0f} min   |   Iran cost: {fc(costs['iran_cost'])}   |   Coalition total: {fc(costs['total_us_cost'])}",
        f"US casualties: {costs['us_mil_kia']:,} KIA / {costs['us_mil_wia']:,} WIA   |   Exchange ratio: {costs['exchange_ratio']:.1f}:1",
        f"Sites destroyed: {costs.get('n_sites_destroyed', 0)}/{costs.get('n_sites_total', 12)}   |   Ship/aircraft damage: {fc(costs['us_ship_damage'])}",
    ]
    for sl in stat_lines:
        draw.text((PAD, y), sl, font=font_small, fill=FG)
        y += 20
    y += 4
    draw.line([(PAD, y), (W - PAD, y)], fill=DIVIDER, width=1)
    y += 8

    # ── Munition section ──────────────────────────────────────────────────────
    draw.text((PAD, y), "IRANIAN / THREAT MUNITIONS", font=font_header, fill=ACCENT)
    y += SECTION_H

    for rgb, lbl in mun_rows:
        draw.rectangle([PAD, y + 2, PAD + SWATCH_W, y + 2 + SWATCH_H], fill=rgb)
        draw.text((PAD + SWATCH_W + 8, y + 1), lbl, font=font_body, fill=FG)
        y += ROW_H

    y += 4
    draw.line([(PAD, y), (W - PAD, y)], fill=DIVIDER, width=1)
    y += 8

    # ── Interceptor / US section ───────────────────────────────────────────────
    draw.text((PAD, y), "US / COALITION RESPONSE", font=font_header, fill=ACCENT)
    y += SECTION_H

    for rgb, lbl in interceptor_rows:
        draw.rectangle([PAD, y + 2, PAD + SWATCH_W, y + 2 + SWATCH_H], fill=rgb)
        draw.text((PAD + SWATCH_W + 8, y + 1), lbl, font=font_body, fill=FG)
        y += ROW_H

    y += PAD

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(out_dir, f"legend_{scenario_key}.png")
    img.save(out_path, "PNG")
    return out_path


# ============================================================
# DYNAMIC SCENARIO LEGEND (updates on each CSG destruction)
# ============================================================

def generate_dynamic_legend_pngs(scenario_key, sc_config, events, csg_fleet,
                                  first_hit_s, tenth_hit_s, costs, dur_s, out_dir):
    """
    Generate N+1 PNG legend cards for a scenario — one per battle state:
      State 0 = scenario start
      State k = after the k-th CSG has been mission-killed (tenth_hit_s reached)

    Returns a list of (png_path, begin_s, end_s) triples, one per state.
    Returns [] if Pillow is not installed.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return []

    # ── Layout ───────────────────────────────────────────────────────────────
    W        = 410
    PAD      = 10
    SWATCH_W = 16
    SWATCH_H = 11
    ROW_H    = 18
    TITLE_H  = 26
    SEC_H    = 16
    BG       = (10, 14, 28, 230)
    FG       = (215, 215, 215)
    ACCENT   = (80, 160, 255)
    DIV      = (45, 50, 70)
    GREEN    = (40, 195, 85)
    YELLOW   = (255, 175, 35)
    RED      = (255, 55, 55)

    def _load_font(size, bold=False):
        candidates = (
            ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
            ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        )
        for p in candidates:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_title  = _load_font(12, bold=True)
    font_hdr    = _load_font(10, bold=True)
    font_body   = _load_font(10)
    font_small  = _load_font(9)

    # ── Fixed legend rows ────────────────────────────────────────────────────
    mun_rows = []
    for mname, mdef in MUNITIONS.items():
        if any(m["name"] == mname for m in sc_config["munitions"]):
            rgb   = _kml_color_to_rgb(mdef["color_bt"])
            label = mdef["label"].split("(")[0].strip()
            mun_rows.append((rgb, label))
    for _, sdef in US_STRIKE_MUNITIONS.items():
        rgb   = _kml_color_to_rgb(sdef["color"])
        label = sdef["label"].split("(")[0].strip()
        mun_rows.append((rgb, label))
    int_rows = [
        ((136, 204, 255), "SM-6 / SM-2"),
        ((0,   153, 255), "CIWS / SeaRAM"),
        ((51,  153, 255), "Naval Gun"),
    ]

    n_csgs = len(csg_fleet)
    # Pre-compute image height (same for every state)
    H = (PAD + TITLE_H + 6             # title + divider gap
         + SEC_H + 6                   # state label + divider gap
         + 3 * ROW_H + 6              # 3 stat lines + divider gap
         + SEC_H + n_csgs * ROW_H + 10 # fleet table + divider gap
         + SEC_H + len(mun_rows) * ROW_H + 6  # munitions + divider gap
         + SEC_H + len(int_rows) * ROW_H       # interceptors
         + PAD)

    # ── State boundaries ────────────────────────────────────────────────────
    # Sort CSG destructions chronologically
    destructions = sorted(tenth_hit_s.items(), key=lambda x: x[1])
    state_times  = [0.0] + [t for _, t in destructions] + [dur_s + 7200]
    n_states     = len(destructions) + 1

    def _counts_at(T):
        n_l = sum(1 for e in events if e["launch_s"] <= T)
        n_i = sum(1 for e in events if e["is_int"] and e["t_int_frac"] is not None
                  and e["launch_s"] + e["t_int_frac"] * e["flight_s"] <= T)
        n_b = sum(1 for e in events if not e["is_int"]
                  and e["launch_s"] + e["flight_s"] <= T)
        return n_l, n_i, n_b

    def _fleet_at(T):
        out = {}
        for c in csg_fleet:
            n = c["name"]
            if n in tenth_hit_s and tenth_hit_s[n] <= T:
                out[n] = ("DESTROYED", tenth_hit_s[n])
            elif n in first_hit_s and first_hit_s[n] <= T:
                out[n] = ("DAMAGED", first_hit_s[n])
            else:
                out[n] = ("INTACT", None)
        return out

    def _fc(usd):
        return f"${usd/1e9:.2f}B" if usd >= 1e9 else f"${usd/1e6:.1f}M"

    legend_paths = []

    for si in range(n_states):
        begin_s = state_times[si]
        end_s   = state_times[si + 1]
        T       = begin_s

        n_l, n_i, n_b = _counts_at(T)
        fleet          = _fleet_at(T)
        n_dest = sum(1 for s, _ in fleet.values() if s == "DESTROYED")
        n_dmg  = sum(1 for s, _ in fleet.values() if s == "DAMAGED")
        n_ok   = n_csgs - n_dest - n_dmg

        if si == 0:
            state_lbl   = "INITIAL POSTURE"
            state_color = GREEN
        else:
            _dn, _dt = destructions[si - 1]
            state_lbl   = f"\u25cf T+{_dt/60:.0f}m  {_dn}  DESTROYED"
            state_color = RED

        img  = Image.new("RGBA", (W, H), BG)
        draw = ImageDraw.Draw(img)
        y    = PAD

        # Title
        draw.text((PAD, y), sc_config["label"], font=font_title, fill=ACCENT)
        y += TITLE_H
        draw.line([(PAD, y), (W - PAD, y)], fill=DIV)
        y += 6

        # State label
        draw.text((PAD, y), state_lbl, font=font_hdr, fill=state_color)
        y += SEC_H
        draw.line([(PAD, y), (W - PAD, y)], fill=DIV)
        y += 6

        # Stat lines
        fleet_summary_color = RED if n_dest > 0 else (YELLOW if n_dmg > 0 else GREEN)
        stat_lines = [
            (f"Launched: {n_l:,}   Intercepted: {n_i:,}   Breakthrough: {n_b:,}", FG),
            (f"Fleet:  {n_dest} DESTROYED   {n_dmg} DAMAGED   {n_ok} INTACT",
             fleet_summary_color),
            (f"Iran: {_fc(costs['iran_cost'])}  |  US total: {_fc(costs['total_us_cost'])}  |  Ratio: {costs['exchange_ratio']:.1f}:1",
             FG),
        ]
        for text, color in stat_lines:
            draw.text((PAD, y), text, font=font_small, fill=color)
            y += ROW_H
        draw.line([(PAD, y), (W - PAD, y)], fill=DIV)
        y += 6

        # Fleet status table
        draw.text((PAD, y), "FLEET STATUS", font=font_hdr, fill=ACCENT)
        y += SEC_H
        for c in csg_fleet:
            n = c["name"]
            status, t_s = fleet[n]
            s_color = RED if status == "DESTROYED" else (YELLOW if status == "DAMAGED" else GREEN)
            t_lbl   = f"  T+{t_s/60:.0f}m" if t_s is not None else ""
            draw.text((PAD, y),       f"\u25c6 {n}",         font=font_body, fill=FG)
            draw.text((PAD + 210, y), f"{status}{t_lbl}",    font=font_body, fill=s_color)
            y += ROW_H
        y += 4
        draw.line([(PAD, y), (W - PAD, y)], fill=DIV)
        y += 6

        # Iranian munitions legend
        draw.text((PAD, y), "IRANIAN MUNITIONS", font=font_hdr, fill=ACCENT)
        y += SEC_H
        for rgb, lbl in mun_rows:
            draw.rectangle([PAD, y + 2, PAD + SWATCH_W, y + 2 + SWATCH_H], fill=rgb)
            draw.text((PAD + SWATCH_W + 6, y + 1), lbl, font=font_body, fill=FG)
            y += ROW_H
        draw.line([(PAD, y), (W - PAD, y)], fill=DIV)
        y += 6

        # US interceptor legend
        draw.text((PAD, y), "US / COALITION INTERCEPTORS", font=font_hdr, fill=ACCENT)
        y += SEC_H
        for rgb, lbl in int_rows:
            draw.rectangle([PAD, y + 2, PAD + SWATCH_W, y + 2 + SWATCH_H], fill=rgb)
            draw.text((PAD + SWATCH_W + 6, y + 1), lbl, font=font_body, fill=FG)
            y += ROW_H

        out_path = os.path.join(out_dir, f"legend_{scenario_key}_state{si}.png")
        img.save(out_path, "PNG")
        legend_paths.append((out_path, begin_s, end_s))

    return legend_paths


def gen_scenario_screen_overlays(legend_states):
    """
    Build KML ScreenOverlay elements (top-right corner) from a list of
    (img_path, begin_s, end_s) triples produced by generate_dynamic_legend_pngs.
    Images are referenced as  images/<basename>  (relative inside KMZ).
    """
    if not legend_states:
        return ""
    parts = []
    for i, (img_path, begin_s, end_s) in enumerate(legend_states):
        img_name = os.path.basename(img_path)
        begin_ts = fmt_time(sim_time(begin_s))
        end_ts   = fmt_time(sim_time(end_s))
        parts.append(
            f'  <ScreenOverlay id="legend_overlay_{i}">\n'
            f'    <name>Legend state {i}</name>\n'
            f'    <Icon><href>images/{img_name}</href></Icon>\n'
            f'    <TimeSpan><begin>{begin_ts}</begin><end>{end_ts}</end></TimeSpan>\n'
            f'    <overlayXY x="1" y="1" xunits="fraction" yunits="fraction"/>\n'
            f'    <screenXY x="0.99" y="0.98" xunits="fraction" yunits="fraction"/>\n'
            f'    <rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
            f'    <size x="0" y="0" xunits="fraction" yunits="fraction"/>\n'
            f'  </ScreenOverlay>'
        )
    return "\n".join(parts)


# ============================================================
# SUMMARY KMZ
# ============================================================

def _fc(usd):
    """Format USD value as $XB or $XM."""
    return f"${usd/1e9:.2f}B" if usd >= 1e9 else f"${usd/1e6:.1f}M"


def generate_summary_kmz(stats, all_costs, out_dir, legend_png_path=None):
    """
    Generate a self-contained KMZ file with:
      - A Placemark at the geographic center of Iran
      - A rich dark-themed HTML description bubble with all-scenario data
      - A ScreenOverlay showing the legend image
    Saved to out_dir/wargame_summary.kmz
    """
    import zipfile

    IRAN_LON, IRAN_LAT = 53.688, 32.427   # geographic center of Iran

    # ── Color constants (black background, white/grey text palette) ───────────
    C_BG      = "#000000"   # pure black background
    C_ACCENT  = "#3399ff"   # blue accent (titles, borders, links)
    C_LABEL   = "#aaaaaa"   # light grey — row/column labels
    C_DATA    = "#ffffff"   # pure white — primary data values
    C_GREEN   = "#00dd66"   # green  — good/intact/low-threat status
    C_YELLOW  = "#ffaa00"   # amber  — degraded/medium status
    C_RED     = "#ff2222"   # red    — destroyed/high-threat/casualty
    C_ORANGE  = "#ff6600"   # orange — Iran / warning
    C_DIM     = "#666666"   # medium grey — footnotes / secondary info
    C_IRAN    = "#ff6600"   # orange — Iranian forces color
    C_US      = "#3399ff"   # blue   — US forces color

    def _status_color(kb, n):
        """Color based on breakthrough ratio."""
        ratio = kb / max(1, n)
        if ratio < 0.15:
            return C_GREEN
        elif ratio < 0.35:
            return C_YELLOW
        elif ratio < 0.55:
            return C_ORANGE
        else:
            return C_RED

    def _grad(value, lo, hi, invert=False):
        """Interpolate CSS hex color on red→yellow→green gradient.
        invert=False: high value → red (bad).  invert=True: high value → green (good).
        Green=#00dd66  Yellow=#ffaa00  Red=#ff2222
        """
        if hi <= lo:
            return C_LABEL
        t = max(0.0, min(1.0, (value - lo) / (hi - lo)))
        if invert:
            t = 1.0 - t
        # t=0 → green, t=0.5 → yellow, t=1 → red
        if t <= 0.5:
            f = t * 2.0
            r = int(255 * f)
            g = int(221 + (170 - 221) * f)
            b = int(102 * (1.0 - f))
        else:
            f = (t - 0.5) * 2.0
            r = 255
            g = int(170 * (1.0 - f) + 34 * f)
            b = int(34 * f)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Build per-scenario rows ────────────────────────────────────────────────
    scenario_rows = []
    for key in (
                # Most → least realistic / probable
                "low",               # A – conservative baseline, most likely
                "realistic",         # D – combined-arms realistic
                "usa_best",          # F – best-case US conditions
                "medium",            # B – moderate Iranian capability
                "ballistic_barrage", # J – plausible pure-ballistic salvo
                "drone_first_low",   # G – phased assault, low scale
                "focused_salvo",     # H – concentrated on single CVN
                "coordinated_strike",# US/IAF coordinated first-strike
                "ascm_swarm",        # K – pure ASCM swarm
                "shore_based_defense",# L – THAAD+PAC-3 layered defense
                "drone_first_medium",# H – phased assault, medium
                "strait_transit",    # M – Hormuz column transit
                "high",              # C – high Iranian capability / CAP hit
                "hypersonic_threat", # I – Fattah-1 HGV mix
                "drone_first_high",  # I – phased assault, high saturation
                "iran_best",         # E – Iran best-case / least realistic
            ):
        if key not in stats:
            continue
        label, n, ki, kb, dur = stats[key]
        costs = all_costs.get(key, {})
        sc_col = _status_color(kb, n)
        int_pct = round(100 * ki / max(1, n))
        bt_pct  = round(100 * kb / max(1, n))
        scenario_rows.append((label, n, ki, kb, dur, costs, sc_col, int_pct, bt_pct))

    # ── Iranian offensive cost breakdown (aggregate across all scenarios) ─────
    # Show per-munition totals for the "realistic" scenario as a representative sample
    _ref_key   = "realistic" if "realistic" in all_costs else next(iter(all_costs))
    _ref_costs = all_costs[_ref_key]
    _icbm      = _ref_costs.get("iran_cost_by_munition", {})
    # pre-compute ranges for Iranian munition table gradients
    _iran_items = sorted(_icbm.items(), key=lambda x: -x[1])
    _iran_n_vals    = [round(c / max(1, MUNITIONS.get(mn, {}).get("cost_usd", 1)))
                       for mn, c in _iran_items]
    _iran_unit_vals = [MUNITIONS.get(mn, {}).get("cost_usd", 0) for mn, _ in _iran_items]
    _iran_tot_vals  = [c for _, c in _iran_items]
    _in_lo, _in_hi  = min(_iran_n_vals),    max(_iran_n_vals)
    _iu_lo, _iu_hi  = min(_iran_unit_vals), max(_iran_unit_vals)
    _it_lo, _it_hi  = min(_iran_tot_vals),  max(_iran_tot_vals)

    # Helper: table cell with gradient background, always-readable dark text
    _TD_PAD = "padding:3px 7px;font-size:11px;border-bottom:1px solid #00000022"
    def _gcell(text, col, align="right", bold=False, extra=""):
        fw = "font-weight:bold;" if bold else ""
        return (f'<td style="background:{col};color:#111;{fw}'
                f'text-align:{align};{_TD_PAD};{extra}">{text}</td>')

    iran_mun_rows_html = ""
    for (mn, cost), n_fired, unit in zip(_iran_items, _iran_n_vals, _iran_unit_vals):
        mdef = MUNITIONS.get(mn, {})
        mc   = _kml_to_css(mdef.get("color", "ff888888"))
        iran_mun_rows_html += (
            f'<tr>'
            f'<td style="color:{mc};padding:2px 8px 2px 0;white-space:nowrap;font-size:11px">{mn}</td>'
            + _gcell(f'{n_fired:,}',       _grad(n_fired, _in_lo, _in_hi))
            + _gcell(f'${unit/1e3:.0f}K',  _grad(unit,    _iu_lo, _iu_hi))
            + _gcell(f'${cost/1e6:.1f}M',  _grad(cost,    _it_lo, _it_hi), bold=True)
            + f'</tr>\n'
        )
    # Cost summary row values for the reference scenario
    _iaf_c  = _ref_costs.get("iaf_cost", 0)
    _vls_c  = _ref_costs.get("us_intercept_cost", 0)
    _str_c  = _ref_costs.get("us_strike_cost", 0)
    _ship_c = _ref_costs.get("us_ship_damage", 0)
    _iran_c = _ref_costs.get("iran_cost", 0)
    _tot_c  = _ref_costs.get("total_us_cost", 0)

    def _fmtc(v):
        return f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M"

    iran_cost_summary_html = (
        f'<tr><td style="color:{C_LABEL};font-size:11px;padding:2px 8px 2px 0">Iran offensive total</td>'
        f'<td colspan="3" style="color:{C_IRAN};font-weight:bold;font-size:11px;text-align:right">{_fmtc(_iran_c)}</td></tr>\n'
        f'<tr><td style="color:{C_DIM};font-size:10px;padding:2px 8px 2px 12px" colspan="4">'
        f'US VLS intercept: {_fmtc(_vls_c)} &nbsp;·&nbsp; '
        f'VLS strikes: {_fmtc(_str_c)} &nbsp;·&nbsp; '
        f'IAF munitions: {_fmtc(_iaf_c)} &nbsp;·&nbsp; '
        f'Ship damage: {_fmtc(_ship_c)} &nbsp;·&nbsp; '
        f'<b style="color:{C_US}">US total: {_fmtc(_tot_c)}</b>'
        f'</td></tr>\n'
    )

    # ── Per-CSG damage table (aggregate: sum across all scenarios) ─────────────
    csg_agg = {}   # csg_name -> {hits, damage_usd, kia, wia, n_neutralized, n_scenarios}
    for key, c in all_costs.items():
        for cname, bd in c.get("csg_breakdown", {}).items():
            if cname not in csg_agg:
                csg_agg[cname] = {"hits": 0, "damage_usd": 0, "kia": 0, "wia": 0,
                                  "n_neutralized": 0, "n_sunk": 0, "n_damaged": 0, "n_scenarios": 0,
                                  "asset_value_usd": bd["asset_value_usd"],
                                  "personnel": bd["personnel"]}
            ag = csg_agg[cname]
            ag["hits"]        += bd["hits"]
            ag["damage_usd"]  += bd["damage_usd"]
            ag["kia"]         += bd["kia"]
            ag["wia"]         += bd["wia"]
            ag["n_scenarios"] += 1
            if bd["status"] in ("DESTROYED", "DESTROYED+SUNK"): ag["n_neutralized"] += 1
            if bd.get("is_sunk"):                                ag["n_sunk"]        += 1
            elif bd["status"] == "DAMAGED":                      ag["n_damaged"]     += 1

    n_sc = len(all_costs)
    # pre-compute averages for gradient ranges
    _csg_computed = {}
    for cname, ag in csg_agg.items():
        _csg_computed[cname] = {
            "avg_hits": ag["hits"]       / max(1, ag["n_scenarios"]),
            "avg_dmg":  ag["damage_usd"] / max(1, ag["n_scenarios"]),
            "avg_kia":  ag["kia"]        / max(1, ag["n_scenarios"]),
            "avg_wia":  ag["wia"]        / max(1, ag["n_scenarios"]),
            "neut_pct": 100 * ag["n_neutralized"] / max(1, n_sc),
            "sink_pct": 100 * ag["n_sunk"]        / max(1, n_sc),
            "dmg_pct":  100 * ag["n_damaged"]     / max(1, n_sc),
        }
    _ch_lo,  _ch_hi  = (min(v["avg_hits"] for v in _csg_computed.values()),
                        max(v["avg_hits"] for v in _csg_computed.values()))
    _cd_lo,  _cd_hi  = (min(v["avg_dmg"]  for v in _csg_computed.values()),
                        max(v["avg_dmg"]  for v in _csg_computed.values()))
    _ck_lo,  _ck_hi  = (min(v["avg_kia"]  for v in _csg_computed.values()),
                        max(v["avg_kia"]  for v in _csg_computed.values()))
    _cw_lo,  _cw_hi  = (min(v["avg_wia"]  for v in _csg_computed.values()),
                        max(v["avg_wia"]  for v in _csg_computed.values()))
    _cn_lo,  _cn_hi  = (min(v["neut_pct"] for v in _csg_computed.values()),
                        max(v["neut_pct"] for v in _csg_computed.values()))
    _csk_lo, _csk_hi = (min(v["sink_pct"] for v in _csg_computed.values()),
                        max(v["sink_pct"] for v in _csg_computed.values()))

    csg_rows_html = ""
    for cname, ag in csg_agg.items():
        cv = _csg_computed[cname]
        avg_hits = cv["avg_hits"]; avg_dmg = cv["avg_dmg"]
        avg_kia  = cv["avg_kia"]; avg_wia  = cv["avg_wia"]
        neut_pct = cv["neut_pct"]; sink_pct = cv["sink_pct"]; dmg_pct = cv["dmg_pct"]
        csg_rows_html += (
            f'<tr>'
            f'<td style="color:{C_ACCENT};padding:2px 7px 2px 0;white-space:nowrap;font-size:11px">{cname}</td>'
            f'<td style="color:{C_DATA};padding:2px 7px 2px 0;text-align:right;font-size:11px">${ag["asset_value_usd"]/1e9:.1f}B</td>'
            f'<td style="color:{C_DATA};padding:2px 7px 2px 0;text-align:right;font-size:11px">{ag["personnel"]:,}</td>'
            + _gcell(f'{avg_hits:.1f}',           _grad(avg_hits, _ch_lo, _ch_hi))
            + _gcell(f'−${avg_dmg/1e6:.0f}M',    _grad(avg_dmg,  _cd_lo, _cd_hi), bold=True)
            + _gcell(f'−{avg_kia:.0f}',           _grad(avg_kia,  _ck_lo, _ck_hi), bold=True)
            + _gcell(f'−{avg_wia:.0f}',           _grad(avg_wia,  _cw_lo, _cw_hi))
            + _gcell(f'{neut_pct:.0f}%✕ {sink_pct:.0f}%〜 {dmg_pct:.0f}%⚠',
                     _grad(neut_pct, _cn_lo, _cn_hi), bold=True)
            + f'</tr>\n'
        )

    # ── SSPK table rows — gradient: high SSPK = green (good for defender) ──────
    sspk_rows_html = ""
    for mname, sp in MUNITION_SSPK.items():
        pct     = round(sp["sspk"] * 100)
        bar_w   = max(4, pct)
        bar_col = _grad(sp["sspk"], 0.0, 1.0, invert=True)  # high SSPK = green (defender succeeds)
        sspk_rows_html += (
            f'<tr>'
            f'<td style="color:{C_LABEL};padding:2px 10px 2px 0;white-space:nowrap;font-size:11px">{mname}</td>'
            f'<td style="color:{C_LABEL};padding:2px 10px 2px 0;white-space:nowrap;font-size:11px">{sp["interceptor"]}</td>'
            + _gcell(f'{pct}%', bar_col, bold=True,
                     extra=f'min-width:{bar_w + 20}px;text-align:center')
            + f'<td style="color:{C_DIM};font-size:10px;max-width:220px;padding:2px 4px">{sp["notes"]}</td>'
            f'</tr>\n'
        )

    # ── Scenario table rows ────────────────────────────────────────────────────
    TD  = f'padding:3px 7px 3px 0;text-align:right;border-bottom:1px solid {C_DIM}22;font-size:11px'
    TDL = f'padding:3px 7px 3px 0;text-align:left;border-bottom:1px solid {C_DIM}22;font-size:11px'

    def _csg_cell(neut, sunk, dmg, intact):
        """Color-coded compact CSG status: destroyed✕ / sunk〜 / damaged⚠ / intact✓."""
        parts = []
        if neut:  parts.append(f'<span style="color:{C_RED};font-weight:bold">{neut}✕</span>')
        if sunk:  parts.append(f'<span style="color:#aa44ff;font-weight:bold">{sunk}〜</span>')
        if dmg:   parts.append(f'<span style="color:{C_YELLOW}">{dmg}⚠</span>')
        if intact:parts.append(f'<span style="color:{C_GREEN}">{intact}✓</span>')
        return " ".join(parts) if parts else f'<span style="color:{C_GREEN}">8✓</span>'

    # ── Pre-compute per-column ranges for gradient coloring ───────────────────
    def _rng(vals):
        v = [x for x in vals if x is not None]
        return (min(v), max(v)) if v else (0, 1)

    _all_n       = [r[1] for r in scenario_rows]
    _all_ip      = [r[7] for r in scenario_rows]
    _all_bt      = [r[8] for r in scenario_rows]
    _all_dur     = [r[4] for r in scenario_rows]
    _all_sites   = [r[5].get("n_sites_destroyed", 0) for r in scenario_rows]
    _all_iran_c  = [r[5].get("iran_cost", 0)         for r in scenario_rows]
    _all_ship_c  = [r[5].get("us_ship_damage", 0)    for r in scenario_rows]
    _all_us_c    = [r[5].get("total_us_cost", 0)     for r in scenario_rows]
    _all_exr     = [r[5].get("exchange_ratio", 0)     for r in scenario_rows]
    _all_kia     = [r[5].get("us_mil_kia", 0)        for r in scenario_rows]
    _all_wia     = [r[5].get("us_mil_wia", 0)        for r in scenario_rows]
    _all_civ     = [r[5].get("collateral_kia", 0)    for r in scenario_rows]

    _n_lo,  _n_hi  = _rng(_all_n)
    _ip_lo, _ip_hi = _rng(_all_ip)
    _bt_lo, _bt_hi = _rng(_all_bt)
    _dr_lo, _dr_hi = _rng(_all_dur)
    _si_lo, _si_hi = _rng(_all_sites)
    _ir_lo, _ir_hi = _rng(_all_iran_c)
    _sh_lo, _sh_hi = _rng(_all_ship_c)
    _us_lo, _us_hi = _rng(_all_us_c)
    _ex_lo, _ex_hi = _rng(_all_exr)
    _ki_lo, _ki_hi = _rng(_all_kia)
    _wi_lo, _wi_hi = _rng(_all_wia)
    _cv_lo, _cv_hi = _rng(_all_civ)

    sc_rows_html = ""
    for label, n, ki, kb, dur, costs, sc_col, int_pct, bt_pct in scenario_rows:
        exr      = costs.get("exchange_ratio", 0)
        iran_cv  = costs.get("iran_cost", 0)
        ship_cv  = costs.get("us_ship_damage", 0)
        us_cv    = costs.get("total_us_cost", 0)
        kia      = costs.get("us_mil_kia", 0)
        wia      = costs.get("us_mil_wia", 0)
        sites       = costs.get("n_sites_destroyed", 0)
        sites_total = costs.get("n_sites_total", 12)
        neut     = costs.get("n_csg_neutralized", 0)
        sunk_n   = costs.get("n_csg_sunk", 0)
        dmg      = costs.get("n_csg_damaged", 0)
        intact   = costs.get("n_csg_intact", 8)
        cap      = costs.get("cap_hit", False)
        civ_kia  = costs.get("collateral_kia", 0)
        ibc      = costs.get("intercept_by_cat", {})
        sm6_n    = ibc.get("SM-6 / SM-2", 0)
        ciws_n   = ibc.get("CIWS / SeaRAM", 0)
        gun_n    = ibc.get("Naval Gun / Phalanx", 0)
        cap_tag  = ' <span style="background:#ff0000;color:#fff;font-size:8px;padding:1px 3px">CAP✕</span>' if cap else ""
        sc_rows_html += (
            f'<tr>'
            f'<td style="color:{C_ACCENT};white-space:nowrap;{TDL}">{label}</td>'
            + _gcell(f'{n:,}',        _grad(n,       _n_lo,  _n_hi))
            + _gcell(f'{int_pct}%',   _grad(int_pct, _ip_lo, _ip_hi, True), bold=True)
            + _gcell(f'{bt_pct}%{cap_tag}', _grad(bt_pct, _bt_lo, _bt_hi), bold=True)
            + _gcell(f'{dur:.0f} m',  _grad(dur,     _dr_lo, _dr_hi))
            + f'<td style="{TD}">{_csg_cell(neut, sunk_n, dmg, intact)}</td>'
            + _gcell(f'{sites}/{sites_total}', _grad(sites, _si_lo, _si_hi, True))
            + _gcell(_fc(iran_cv),        _grad(iran_cv, _ir_lo, _ir_hi))
            + _gcell(f'−{_fc(ship_cv)}',  _grad(ship_cv, _sh_lo, _sh_hi), bold=True)
            + _gcell(f'−{_fc(us_cv)}',    _grad(us_cv,   _us_lo, _us_hi), bold=True)
            + _gcell(f'{exr:.1f}:1',      _grad(exr,     _ex_lo, _ex_hi), bold=True)
            + _gcell(f'−{kia:,}',         _grad(kia,     _ki_lo, _ki_hi), bold=True)
            + _gcell(f'−{wia:,}',         _grad(wia,     _wi_lo, _wi_hi))
            + _gcell(f'−{civ_kia:,}',     _grad(civ_kia, _cv_lo, _cv_hi))
            + f'<td style="color:{C_DATA};font-size:10px;{TD}">SM6:{sm6_n} CIWS:{ciws_n} Gun:{gun_n}</td>'
            + f'</tr>\n'
        )

    desc_html = (
        "<![CDATA["
        f'<div style="background:{C_BG};color:{C_DATA};'
        f'font-family:\'Courier New\',Courier,monospace;'
        f'padding:16px 18px;margin:-15px -15px -20px -15px;'
        f'border-left:4px solid {C_ACCENT};border-top:3px solid {C_ACCENT}">'

        # Title
        f'<div style="color:{C_ACCENT};font-weight:bold;font-size:15px;'
        f'letter-spacing:3px;margin-bottom:12px;padding-bottom:6px;'
        f'border-bottom:2px solid {C_ACCENT}66">◈ PERSIAN GULF WARGAME — SCENARIO SUMMARY</div>'

        # Subtitle
        f'<div style="color:{C_LABEL};font-size:11px;margin-bottom:14px">'
        f'8 US Carrier Strike Groups vs. Iranian Mass-Missile Attack &nbsp;|&nbsp; '
        f'Simulation clock: {fmt_time(SIM_START)} UTC &nbsp;|&nbsp; '
        f'16 scenarios modeled</div>'

        # Scenario comparison table
        f'<div style="color:{C_ACCENT};font-weight:bold;font-size:12px;'
        f'letter-spacing:1px;margin-bottom:6px;border-bottom:1px solid {C_ACCENT}44;padding-bottom:3px">'
        f'SCENARIO COMPARISON</div>'
        f'<div style="overflow-x:auto">'
        f'<table style="width:100%;border-collapse:collapse;font-size:11px">'
        f'<tr style="border-bottom:2px solid {C_ACCENT}55">'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 7px 4px 0;font-size:11px">Scenario</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Launched</th>'
        f'<th style="color:{C_GREEN};text-align:right;padding:2px 7px 4px 0;font-size:11px">Intercept%</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">Breakthr%</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Dur</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">CSGs ✕⚠✓</th>'
        f'<th style="color:{C_YELLOW};text-align:right;padding:2px 7px 4px 0;font-size:11px">Sites✕</th>'
        f'<th style="color:{C_IRAN};text-align:right;padding:2px 7px 4px 0;font-size:11px">Iran $</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">−Ship Dmg</th>'
        f'<th style="color:{C_US};text-align:right;padding:2px 7px 4px 0;font-size:11px">−US Total $</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">Exch</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">−US KIA</th>'
        f'<th style="color:{C_YELLOW};text-align:right;padding:2px 7px 4px 0;font-size:11px">−US WIA</th>'
        f'<th style="color:{C_DIM};text-align:right;padding:2px 7px 4px 0;font-size:11px">−Civ KIA</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Interceptors</th>'
        f'</tr>\n'
        + sc_rows_html +
        f'</table></div>'

        # Iranian offensive cost breakdown (reference scenario)
        f'<div style="color:{C_ACCENT};font-weight:bold;font-size:12px;'
        f'letter-spacing:1px;margin:16px 0 6px;border-bottom:1px solid {C_ACCENT}44;padding-bottom:3px">'
        f'IRANIAN OFFENSIVE COSTS — {_ref_key.upper()} SCENARIO (REFERENCE)</div>'
        f'<table style="width:100%;border-collapse:collapse">'
        f'<tr style="border-bottom:1px solid {C_ACCENT}44">'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 8px 4px 0;font-size:11px">Munition</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 8px 4px 0;font-size:11px">Rounds</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 8px 4px 0;font-size:11px">Unit Cost</th>'
        f'<th style="color:{C_IRAN};text-align:right;padding:2px 8px 4px 0;font-size:11px">Total Cost</th>'
        f'</tr>\n'
        + iran_mun_rows_html
        + iran_cost_summary_html
        + f'</table>'

        # CSG damage table (averaged across all scenarios)
        f'<div style="color:{C_ACCENT};font-weight:bold;font-size:12px;'
        f'letter-spacing:1px;margin:16px 0 6px;border-bottom:1px solid {C_ACCENT}44;padding-bottom:3px">'
        f'CSG DAMAGE &amp; CASUALTIES — AVERAGED ACROSS ALL SCENARIOS</div>'
        f'<div style="overflow-x:auto">'
        f'<table style="width:100%;border-collapse:collapse">'
        f'<tr style="border-bottom:2px solid {C_ACCENT}44">'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 7px 4px 0;font-size:11px">CSG</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Asset Value</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Personnel</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Avg Hits</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">−Avg Damage</th>'
        f'<th style="color:{C_RED};text-align:right;padding:2px 7px 4px 0;font-size:11px">−Avg KIA</th>'
        f'<th style="color:{C_YELLOW};text-align:right;padding:2px 7px 4px 0;font-size:11px">−Avg WIA</th>'
        f'<th style="color:{C_LABEL};text-align:right;padding:2px 7px 4px 0;font-size:11px">Destroyed/Damaged%</th>'
        f'</tr>\n'
        + csg_rows_html +
        f'</table></div>'

        # SSPK table
        f'<div style="color:{C_ACCENT};font-weight:bold;font-size:12px;'
        f'letter-spacing:1px;margin:16px 0 6px;border-bottom:1px solid {C_ACCENT}44;padding-bottom:3px">'
        f'SINGLE-SHOT Pk (SSPK) — OPEN-SOURCE ESTIMATES</div>'
        f'<div style="color:{C_DIM};font-size:10px;margin-bottom:8px">'
        f'Sources: Wilkening (S&amp;GS 2000) · CSBA Salvo Competition (2015) · RAND BMD · '
        f'DOT&amp;E FY2018/2022 · JINSA/FPRI (2025) · Red Sea ops data</div>'
        f'<table style="width:100%;border-collapse:collapse">'
        f'<tr style="border-bottom:1px solid {C_ACCENT}44">'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 10px 4px 0;font-size:11px">Munition</th>'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 10px 4px 0;font-size:11px">Best Interceptor</th>'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 10px 4px 0;font-size:11px">SSPK</th>'
        f'<th style="color:{C_LABEL};text-align:left;padding:2px 10px 4px 0;font-size:11px">Notes</th>'
        f'</tr>\n'
        + sspk_rows_html +
        f'</table>'

        # Footer / sources
        f'<div style="margin-top:12px;padding-top:8px;border-top:1px solid {C_ACCENT}33;'
        f'color:{C_DIM};font-size:10px">'
        f'All SSPK estimates unclassified open-source. Classified values not available. '
        f'Standard doctrine: 2 interceptors per ballistic threat (cumulative Pk 0.75–0.94). '
        f'Magazine depth is the binding operational constraint. '
        f'Exchange ratio = US total cost ÷ Iran offensive cost.'
        f'</div>'

        f'</div>'
        "]]>"
    )

    # ── Build the KML ──────────────────────────────────────────────────────────
    screen_overlay = ""
    legend_img_name = ""
    if legend_png_path and os.path.exists(legend_png_path):
        legend_img_name = "images/" + os.path.basename(legend_png_path)
        screen_overlay = (
            f'  <ScreenOverlay>'
            f'<name>Scenario Legend</name>'
            f'<Icon><href>{legend_img_name}</href></Icon>'
            f'<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>'
            f'<screenXY x="0.01" y="0.99" xunits="fraction" yunits="fraction"/>'
            f'<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>'
            f'<size x="0" y="0" xunits="fraction" yunits="fraction"/>'
            f'</ScreenOverlay>'
        )

    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>Persian Gulf Wargame — Summary</name>
  <LookAt>
    <longitude>{IRAN_LON}</longitude>
    <latitude>{IRAN_LAT}</latitude>
    <altitude>0</altitude>
    <range>1800000</range>
    <tilt>0</tilt>
    <heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>
  <Style id="iran_center">
    <IconStyle>
      <color>ff0066ff</color>
      <scale>1.6</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0066ff</color><scale>1.3</scale></LabelStyle>
    <BalloonStyle>
      <bgColor>ff000000</bgColor>
      <textColor>ffffffff</textColor>
      <text>$[description]</text>
    </BalloonStyle>
  </Style>
  <Placemark>
    <name>Persian Gulf Wargame — All Scenarios</name>
    <styleUrl>#iran_center</styleUrl>
    <description>{desc_html}</description>
    <Point>
      <altitudeMode>relativeToGround</altitudeMode>
      <coordinates>{IRAN_LON},{IRAN_LAT},0</coordinates>
    </Point>
  </Placemark>
{screen_overlay}
</Document>
</kml>"""

    # ── Package as KMZ ────────────────────────────────────────────────────────
    kmz_path = os.path.join(out_dir, "wargame_summary.kmz")
    with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml_content.encode("utf-8"))
        if legend_png_path and os.path.exists(legend_png_path):
            zf.write(legend_png_path, legend_img_name)
    return kmz_path


# ============================================================
# HTML REPORT GENERATOR
# ============================================================

def generate_html_reports(stats, all_costs, out_dir):
    """
    Write dark-themed HTML reports into out_dir:
      summary.html           — cross-scenario comparison + aggregate tables
      scenario_{key}.html    — per-scenario detailed breakdown
    Returns list of file paths written.
    """
    import html as _html_mod
    from datetime import datetime as _dt

    # ── Shared palette ─────────────────────────────────────────────────────────
    BG      = "#0a0c10"
    BG2     = "#111520"
    BG3     = "#181e2a"
    ACC     = "#3399ff"
    LAB     = "#7fa8cc"
    DAT     = "#e8f0ff"
    DIM     = "#445566"
    GREEN   = "#00dd66"
    YELLOW  = "#ffaa00"
    ORANGE  = "#ff6600"
    RED     = "#ff2222"
    IRAN_C  = "#ff6600"
    US_C    = "#3399ff"
    NEG_C   = "#ff4444"

    def _fc(v):
        return f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M"

    def _status_col(kb, n):
        r = kb / max(1, n)
        return GREEN if r < 0.15 else YELLOW if r < 0.35 else ORANGE if r < 0.55 else RED

    def _grad(value, lo, hi, invert=False):
        if hi <= lo:
            return LAB
        t = max(0.0, min(1.0, (value - lo) / (hi - lo)))
        if invert:
            t = 1.0 - t
        if t <= 0.5:
            f = t * 2.0
            r = int(255 * f); g = int(221 + (170 - 221) * f); b = int(102 * (1.0 - f))
        else:
            f = (t - 0.5) * 2.0
            r = 255; g = int(170 * (1.0 - f) + 34 * f); b = int(34 * f)
        return f"#{r:02x}{g:02x}{b:02x}"

    _TS = f"Generated {_dt.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

    BASE_CSS = f"""
    <style>
      *{{box-sizing:border-box;margin:0;padding:0}}
      body{{background:{BG};color:{DAT};font-family:'Courier New',monospace;font-size:13px;line-height:1.55;
            -webkit-font-smoothing:antialiased}}
      a{{color:{ACC};text-decoration:none;transition:color .15s}} a:hover{{color:#66bbff;text-decoration:underline}}
      h1{{color:{ACC};font-size:22px;margin-bottom:4px;letter-spacing:2px;text-shadow:0 0 18px {ACC}55}}
      h2{{color:{ACC};font-size:14px;margin:20px 0 6px;border-bottom:1px solid {ACC}33;padding-bottom:5px;
          letter-spacing:1px;text-transform:uppercase}}
      h3{{color:{LAB};font-size:12px;margin:10px 0 3px;letter-spacing:.5px}}
      .wrap{{max-width:1500px;margin:0 auto;padding:20px 24px}}
      .ts{{color:{DIM};font-size:10px;margin-bottom:16px;letter-spacing:.3px}}
      .topbar{{background:linear-gradient(90deg,{BG2},{BG});border-bottom:2px solid {ACC}44;
               padding:10px 24px;margin:-20px -24px 20px;display:flex;align-items:center;gap:16px}}
      .topbar-title{{color:{ACC};font-size:13px;font-weight:bold;letter-spacing:1.5px;flex:1}}
      .topbar-sub{{color:{LAB};font-size:10px}}
      .nav{{margin-bottom:18px;padding:7px 14px;background:{BG2};border:1px solid {ACC}22;
            border-radius:4px;font-size:11px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;
            border-left:3px solid {ACC}66}}
      .nav a{{padding:1px 5px;border-radius:3px;transition:background .15s}}
      .nav a:hover{{background:{ACC}22}}
      .tbl-wrap{{overflow-x:auto;margin-bottom:18px;border:1px solid {ACC}18;border-radius:4px}}
      table{{border-collapse:collapse;width:100%;font-size:11px;min-width:600px}}
      thead{{position:sticky;top:0;z-index:2}}
      th{{color:{LAB};text-align:right;padding:6px 10px 6px;background:{BG2};
          border-bottom:2px solid {ACC}44;white-space:nowrap;font-weight:bold;letter-spacing:.3px}}
      th:first-child{{text-align:left}}
      td{{padding:4px 10px 4px;border-bottom:1px solid {BG3};white-space:nowrap;transition:background .1s}}
      tr:hover td{{background:{BG2}88}}
      tr:nth-child(even) td{{background:{BG3}44}}
      .num{{text-align:right}} .cen{{text-align:center}} .lft{{text-align:left}}
      .cards{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px}}
      .card{{background:{BG2};border:1px solid {ACC}22;border-radius:6px;padding:12px 16px;
             min-width:148px;flex:1 1 148px;border-top:3px solid transparent;
             transition:border-color .2s}}
      .card:hover{{border-top-color:{ACC}88}}
      .card-label{{color:{LAB};font-size:9px;text-transform:uppercase;letter-spacing:1px}}
      .card-value{{font-size:20px;font-weight:bold;margin-top:3px;letter-spacing:-.5px}}
      .card-sub{{color:{DIM};font-size:9px;margin-top:1px}}
      .desc{{background:{BG2};border-left:3px solid {ACC};border-radius:0 5px 5px 0;
             padding:12px 16px;margin-bottom:16px;font-size:11px;color:{LAB};
             line-height:1.65;max-height:420px;overflow-y:auto}}
      .badge{{display:inline-block;padding:3px 9px;border-radius:4px;font-size:10px;
              font-weight:bold;letter-spacing:.3px;margin-right:4px}}
      .pbar-wrap{{display:inline-block;width:54px;height:7px;background:{BG3};
                  border-radius:3px;vertical-align:middle;margin-left:5px}}
      .pbar-fill{{height:100%;border-radius:3px;display:block}}
      .section-header{{display:flex;align-items:center;gap:8px;margin:22px 0 8px}}
      .section-header::after{{content:"";flex:1;height:1px;background:{ACC}22}}
      .section-title{{color:{ACC};font-size:13px;font-weight:bold;letter-spacing:1px;
                      text-transform:uppercase;white-space:nowrap}}
      .footer{{margin-top:28px;padding-top:10px;border-top:1px solid {ACC}18;
               color:{DIM};font-size:10px;letter-spacing:.3px}}
      /* total rows */
      .total-row td{{background:{BG2}!important;font-weight:bold;
                     border-top:2px solid {ACC}44!important}}
    </style>"""

    def _page(title, body):
        return (f"<!DOCTYPE html><html lang='en'><head>"
                f"<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>{title}</title>{BASE_CSS}</head>"
                f"<body><div class='wrap'>{body}"
                f"<div class='footer'>{_TS} &nbsp;·&nbsp; "
                f"Persian Gulf Wargame Simulation &mdash; Unclassified Open-Source Model</div>"
                f"</div></body></html>")

    def _td(text, col=None, align="right", bold=False, mono=True, pct=None):
        """Table cell. col = background colour; pct = 0-100 adds a miniature progress bar."""
        style = f"text-align:{align};"
        if col:
            style += f"background:{col};color:#111;"
        if bold:
            style += "font-weight:bold;"
        if mono:
            style += "font-family:'Courier New',monospace;"
        inner = text
        if pct is not None and not col:
            bar_col = _grad(pct, 0, 100)
            inner += (f'<span class="pbar-wrap">'
                      f'<span class="pbar-fill" style="width:{max(2,int(pct))}%;background:{bar_col}"></span>'
                      f'</span>')
        return f'<td style="{style}padding:4px 10px 4px;">{inner}</td>'

    def _th(text, align="right"):
        return f'<th style="text-align:{align};">{text}</th>'

    def _section(title):
        return f'<div class="section-header"><span class="section-title">{title}</span></div>'

    def _tbl(header_row, body_rows):
        """Wrap a table in a horizontal-scroll div."""
        return (f'<div class="tbl-wrap"><table><thead>{header_row}</thead>'
                f'<tbody>{body_rows}</tbody></table></div>')

    written = []

    # ══════════════════════════════════════════════════════════════════════
    # 1.  PER-SCENARIO PAGES
    # ══════════════════════════════════════════════════════════════════════
    for key, (label, n, ki, kb, dur) in stats.items():
        costs = all_costs.get(key, {})
        sc    = SCENARIOS[key]
        ibc   = costs.get("intercept_by_cat", {})
        cbd   = costs.get("csg_breakdown", {})
        icbm  = costs.get("iran_cost_by_munition", {})
        sites_destroyed_count = costs.get("n_sites_destroyed", 0)
        sites_total_count     = costs.get("n_sites_total", len(IRAN_SITES))
        scenario_status_color   = _status_col(kb, n)
        breakthrough_percentage = round(100 * kb / max(1, n))
        intercept_percentage    = round(100 * ki / max(1, n))
        situation_report_html   = _html_mod.escape(costs.get("dyn_desc", "")).replace("\n\n", "</p><p>").replace("\n", "<br>")

        # ── CSG neutralization summary badges ────────────────────────────
        n_neut = costs.get("n_csg_neutralized", 0)
        n_sunk = costs.get("n_csg_sunk", 0)
        n_dmg  = costs.get("n_csg_damaged", 0)
        n_int_ = len(SCENARIOS[key].get("csg_fleet", US_CSGS))
        n_intact = max(0, n_int_ - n_neut - n_dmg)
        status_badges = (
            f'<span class="badge" style="background:{RED}33;border:1px solid {RED};color:{RED}">✕ {n_neut} neutralized</span>'
            f'<span class="badge" style="background:#005577;border:1px solid #007799;color:{DAT}">〜 {n_sunk} sunk</span>'
            f'<span class="badge" style="background:{ORANGE}33;border:1px solid {ORANGE};color:{ORANGE}">⚠ {n_dmg} damaged</span>'
            f'<span class="badge" style="background:{GREEN}33;border:1px solid {GREEN};color:{GREEN}">✓ {n_intact} intact</span>'
        )

        # ── Metric cards ──────────────────────────────────────────────────
        _kml_file = f"scenario_{key}.kmz"
        cards_html = (
            f'<div class="cards">'
            f'<div class="card" style="border-top-color:{IRAN_C}">'
            f'<div class="card-label">Launched</div>'
            f'<div class="card-value" style="color:{IRAN_C}">{n:,}</div>'
            f'<div class="card-sub">total munitions</div></div>'

            f'<div class="card" style="border-top-color:{GREEN}">'
            f'<div class="card-label">Intercepted</div>'
            f'<div class="card-value" style="color:{GREEN}">{ki:,}</div>'
            f'<div class="card-sub">{intercept_percentage}% kill rate</div></div>'

            f'<div class="card" style="border-top-color:{scenario_status_color}">'
            f'<div class="card-label">Breakthrough</div>'
            f'<div class="card-value" style="color:{scenario_status_color}">{kb:,}</div>'
            f'<div class="card-sub">{breakthrough_percentage}% penetration</div></div>'

            f'<div class="card" style="border-top-color:{ACC}">'
            f'<div class="card-label">Duration</div>'
            f'<div class="card-value" style="color:{ACC}">{dur:.0f} min</div>'
            f'<div class="card-sub">{dur/60:.1f} hours</div></div>'

            f'<div class="card" style="border-top-color:{YELLOW}">'
            f'<div class="card-label">Sites suppressed</div>'
            f'<div class="card-value" style="color:{YELLOW}">{sites_destroyed_count}/{sites_total_count}</div>'
            f'<div class="card-sub">launch sites hit</div></div>'

            f'<div class="card" style="border-top-color:{RED}">'
            f'<div class="card-label">Exchange ratio</div>'
            f'<div class="card-value" style="color:{RED}">{costs.get("exchange_ratio",0):.0f}:1</div>'
            f'<div class="card-sub">US cost / Iran cost</div></div>'

            f'<div class="card" style="border-top-color:{ACC}55">'
            f'<div class="card-label">KML visualization</div>'
            f'<div class="card-value" style="font-size:13px;margin-top:6px">'
            f'<a href="{_kml_file}" style="color:{ACC}">↓ {_kml_file}</a></div>'
            f'<div class="card-sub">Google Earth KML</div></div>'

            f'</div>'
        )

        # ── Cost table ────────────────────────────────────────────────────
        ship_damage_value_usd  = costs.get("us_ship_damage", 0)
        total_us_cost_usd      = costs.get("total_us_cost", 0)
        exchange_ratio_value   = costs.get("exchange_ratio", 0)
        iran_offensive_cost_usd = costs.get("iran_cost", 0)
        # Scale percentages for progress bars (capped at 100%).
        ship_damage_scale_percent = min(100, round(100 * ship_damage_value_usd / 200e9))
        us_cost_scale_percent     = min(100, round(100 * total_us_cost_usd     / 250e9))
        cost_html = _tbl(
            f'<tr>{_th("Item","left")}{_th("Cost")}{_th("Scale","left")}</tr>',
            (f'<tr><td style="color:{IRAN_C}">Iran offensive munitions</td>'
             f'{_td(_fc(iran_offensive_cost_usd), bold=True)}'
             f'{_td(f"", align="left", pct=min(100,round(100*iran_offensive_cost_usd/3e9)))}</tr>'
             f'<tr><td style="color:{US_C}">US VLS intercept</td>'
             f'{_td(_fc(costs.get("us_intercept_cost",0)))}'
             f'{_td("", align="left")}</tr>'
             f'<tr><td style="color:{US_C}">US strike munitions</td>'
             f'{_td(_fc(costs.get("us_strike_cost",0)))}'
             f'{_td("", align="left")}</tr>'
             f'<tr><td style="color:{US_C}">IAF strike munitions</td>'
             f'{_td(_fc(costs.get("iaf_cost",0)))}'
             f'{_td("", align="left")}</tr>'
             f'<tr><td style="color:{NEG_C}">Ship / aircraft damage</td>'
             f'{_td(f"−{_fc(ship_damage_value_usd)}", bold=True)}'
             f'{_td("", align="left", pct=ship_damage_scale_percent)}</tr>'
             f'<tr class="total-row"><td>US total cost</td>'
             f'{_td(f"−{_fc(total_us_cost_usd)}", RED, bold=True)}'
             f'{_td("", align="left", pct=us_cost_scale_percent)}</tr>'
             f'<tr><td style="color:{LAB}">Exchange ratio</td>'
             f'{_td(f"{exchange_ratio_value:.0f} : 1", _grad(exchange_ratio_value, 0, 500))}'
             f'{_td("", align="left")}</tr>'
            )
        )

        # ── Intercept breakdown ───────────────────────────────────────────
        sm6_rounds_fired       = ibc.get("SM-6 / SM-2", 0)
        ciws_rounds_fired      = ibc.get("CIWS / SeaRAM", 0)
        naval_gun_rounds_fired = ibc.get("Naval Gun / Phalanx", 0)
        total_intercept_rounds = max(1, sm6_rounds_fired + ciws_rounds_fired + naval_gun_rounds_fired)
        int_html = _tbl(
            f'<tr>{_th("System","left")}{_th("Rounds fired")}{_th("Share","left")}</tr>',
            (f'<tr><td style="color:{GREEN}">SM-6 / SM-2</td>'
             f'{_td(f"{sm6_rounds_fired:,}", bold=True)}'
             f'{_td("", align="left", pct=round(100*sm6_rounds_fired/total_intercept_rounds))}</tr>'
             f'<tr><td style="color:{YELLOW}">CIWS / SeaRAM</td>'
             f'{_td(f"{ciws_rounds_fired:,}")}'
             f'{_td("", align="left", pct=round(100*ciws_rounds_fired/total_intercept_rounds))}</tr>'
             f'<tr><td style="color:{ORANGE}">Naval Gun / Phalanx</td>'
             f'{_td(f"{naval_gun_rounds_fired:,}")}'
             f'{_td("", align="left", pct=round(100*naval_gun_rounds_fired/total_intercept_rounds))}</tr>'
            )
        )

        # ── Casualties ────────────────────────────────────────────────────
        us_kia = costs.get("us_mil_kia", 0); us_wia = costs.get("us_mil_wia", 0)
        civ_kia = costs.get("collateral_kia", 0); civ_usd = costs.get("collateral_usd", 0)
        cas_html = _tbl(
            f'<tr>{_th("Category","left")}{_th("Count")}{_th("Scale","left")}</tr>',
            (f'<tr><td style="color:{RED}">US Military KIA</td>'
             f'{_td(f"−{us_kia:,}", _grad(us_kia,0,100000), bold=True)}'
             f'{_td("", align="left", pct=min(100,round(us_kia/1000)))}</tr>'
             f'<tr><td style="color:{ORANGE}">US Military WIA</td>'
             f'{_td(f"−{us_wia:,}", _grad(us_wia,0,80000))}'
             f'{_td("", align="left", pct=min(100,round(us_wia/800)))}</tr>'
             f'<tr><td style="color:{YELLOW}">Civilian KIA</td>'
             f'{_td(f"−{civ_kia:,}", _grad(civ_kia,0,5000))}'
             f'{_td("", align="left", pct=min(100,round(civ_kia/50)))}</tr>'
             f'<tr><td style="color:{LAB}">Civilian collateral cost</td>'
             f'{_td(_fc(civ_usd))}'
             f'{_td("", align="left")}</tr>'
            )
        )

        # ── CSG breakdown table ───────────────────────────────────────────
        _hv = [bd["avg_hits"] if "avg_hits" in bd else bd["hits"]
               for bd in cbd.values()] if cbd else [0]
        _h_lo, _h_hi = 0, max(max(_hv), 1)
        _d_lo, _d_hi = 0, max(max((bd["damage_usd"] for bd in cbd.values()), default=0), 1)
        csg_rows = ""
        _tot_hits = _tot_dmg = _tot_kia = _tot_wia = 0
        _tot_asset = _tot_crew = 0
        for cname, bd in cbd.items():
            st = bd.get("status", "INTACT")
            st_col = RED if "DESTROYED" in st else ORANGE if st == "DAMAGED" else GREEN
            sunk = " 〜SUNK" if bd.get("is_sunk") else ""
            _tot_hits += bd["hits"]; _tot_dmg += bd["damage_usd"]
            _tot_kia  += bd["kia"]; _tot_wia  += bd["wia"]
            _tot_asset += bd["asset_value_usd"]; _tot_crew += bd["personnel"]
            _h_pct = round(100 * bd["hits"] / max(1, _h_hi))
            csg_rows += (
                f'<tr>'
                f'<td style="color:{ACC};white-space:nowrap">{cname}</td>'
                f'<td style="color:{DAT}">${bd["asset_value_usd"]/1e9:.1f}B</td>'
                f'<td style="color:{DAT}">{bd["personnel"]:,}</td>'
                + _td(f'{bd["hits"]}', _grad(bd["hits"], _h_lo, _h_hi), pct=_h_pct)
                + _td(f'−{_fc(bd["damage_usd"])}', _grad(bd["damage_usd"], _d_lo, _d_hi), bold=True)
                + _td(f'−{bd["kia"]:,}', _grad(bd["kia"], 0, 20000), bold=True)
                + _td(f'−{bd["wia"]:,}', _grad(bd["wia"], 0, 15000))
                + f'<td style="color:{st_col};font-weight:bold">{st}{sunk}</td>'
                + f'</tr>\n'
            )
        csg_total_row = (
            f'<tr class="total-row">'
            f'<td style="color:{DAT}">TOTAL — all CSGs</td>'
            f'<td style="color:{DAT}">${_tot_asset/1e9:.1f}B</td>'
            f'<td style="color:{DAT}">{_tot_crew:,}</td>'
            + _td(f'{_tot_hits}', _grad(_tot_hits, 0, max(_tot_hits,1)), bold=True)
            + _td(f'−{_fc(_tot_dmg)}', RED, bold=True)
            + _td(f'−{_tot_kia:,}', RED, bold=True)
            + _td(f'−{_tot_wia:,}', _grad(_tot_wia, 0, max(_tot_wia,1)), bold=True)
            + f'<td> </td></tr>\n'
        )
        csg_html = _tbl(
            (f'<tr>{_th("CSG","left")}{_th("Asset value","left")}{_th("Personnel","left")}'
             f'{_th("Hits")}{_th("Damage")}{_th("KIA")}{_th("WIA")}{_th("Status","left")}</tr>'),
            csg_rows + csg_total_row
        )

        # ── Munition mix fired ────────────────────────────────────────────
        _mv = list(icbm.values()) if icbm else [0]
        _m_hi = max(max(_mv), 1)
        mun_rows = ""
        _tot_mun_cost = sum(icbm.values())
        for mn, cost_tot in sorted(icbm.items(), key=lambda x: -x[1]):
            mdef = MUNITIONS.get(mn, {})
            n_fired = round(cost_tot / max(1, mdef.get("cost_usd", 1)))
            mc = _kml_to_css(mdef.get("color", "ff888888"))
            _share_pct = round(100 * cost_tot / max(1, _tot_mun_cost))
            mun_rows += (
                f'<tr>'
                f'<td style="color:{mc};white-space:nowrap">'
                f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
                f'background:{mc};margin-right:6px"></span>{mn}</td>'
                + _td(f'{n_fired:,}', pct=round(100*cost_tot/_m_hi))
                + _td(f'${mdef.get("cost_usd",0)/1e3:.0f}K')
                + _td(f'{_fc(cost_tot)}', bold=True)
                + _td(f'{_share_pct}%', _grad(_share_pct, 0, 100))
                + f'</tr>\n'
            )
        mun_html = _tbl(
            (f'<tr>{_th("Munition","left")}{_th("Fired")}'
             f'{_th("Unit cost")}{_th("Total cost")}{_th("Share")}</tr>'),
            mun_rows
        )

        navigation_html = (f'<div class="nav">'
               f'<a href="summary.html">← Summary</a>'
               + "".join(
                   f' &nbsp;<a href="scenario_{k}.html">{SCENARIOS[k]["label"].split("--")[0].strip()}</a>'
                   for k in stats if k != key)
               + f'</div>')

        page_body_html = (
            f'<div class="topbar">'
            f'<span class="topbar-title">◈ PERSIAN GULF WARGAME</span>'
            f'<span class="topbar-sub">Simulation start: 2026-04-01 06:00 UTC</span>'
            f'</div>'
            f'<h1>{_html_mod.escape(label)}</h1>'
            f'<div class="ts">{_TS}</div>'
            f'{navigation_html}'
            f'<div style="margin:10px 0 14px">{status_badges}</div>'
            f'{cards_html}'
            f'{_section("Situation Report")}'
            f'<div class="desc"><p>{situation_report_html}</p></div>'
            f'{_section("Cost Accounting")}{cost_html}'
            f'{_section("Intercept Systems Used")}{int_html}'
            f'{_section("Casualties")}{cas_html}'
            f'{_section("Fleet Battle Damage Assessment")}{csg_html}'
            f'{_section("Iranian Munitions Fired")}{mun_html}'
        )
        path = os.path.join(out_dir, f"scenario_{key}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_page(label, page_body_html))
        written.append(path)

    # ══════════════════════════════════════════════════════════════════════
    # 2.  SUMMARY PAGE
    # ══════════════════════════════════════════════════════════════════════
    SCENARIO_ORDER = [
        "one_percent_probe", "one_percent_fatah2", "low", "usa_best", "realistic", "medium", "ballistic_barrage",
        "drone_first_low", "focused_salvo", "coordinated_strike", "ascm_swarm",
        "shore_based_defense", "drone_first_medium", "strait_transit", "high",
        "hypersonic_threat", "drone_first_high", "iran_best", "caves",
        "depleted_drone_first", "depleted_coastal", "depleted_israel_split",
        "us_win_preemption", "us_win_ew_dominance", "us_win_allied_umbrella",
        "us_win_c2_disrupted", "us_win_arsenal_attrition",
        "ballistic_surge",
    ]

    # Scenario comparison table
    _sh_vals = [all_costs[k].get("us_ship_damage", 0) for k in SCENARIO_ORDER if k in all_costs]
    _us_vals = [all_costs[k].get("total_us_cost",  0) for k in SCENARIO_ORDER if k in all_costs]
    _ki_vals = [all_costs[k].get("us_mil_kia",     0) for k in SCENARIO_ORDER if k in all_costs]
    _wi_vals = [all_costs[k].get("us_mil_wia",     0) for k in SCENARIO_ORDER if k in all_costs]
    _sh_lo, _sh_hi = 0, max(max(_sh_vals, default=1), 1)
    _us_lo, _us_hi = 0, max(max(_us_vals, default=1), 1)
    _ki_lo, _ki_hi = 0, max(max(_ki_vals, default=1), 1)
    _wi_lo, _wi_hi = 0, max(max(_wi_vals, default=1), 1)

    sc_rows = ""
    _tot_n = _tot_ki = _tot_kb = _tot_sm6 = _tot_ciws = 0
    _tot_ship_v = _tot_us_v = _tot_kia = _tot_neut = _tot_sunk = 0
    _n_sc_counted = 0
    for key in SCENARIO_ORDER:
        if key not in stats:
            continue
        label, n, ki, kb, dur = stats[key]
        costs = all_costs[key]
        scenario_status_color   = _status_col(kb, n)
        breakthrough_percentage = round(100 * kb / max(1, n))
        intercept_by_category   = costs.get("intercept_by_cat", {})
        ship_damage_usd         = costs.get("us_ship_damage", 0)
        us_total_cost_usd       = costs.get("total_us_cost",  0)
        us_kia                  = costs.get("us_mil_kia", 0)
        us_wia                  = costs.get("us_mil_wia", 0)  # noqa: F841 — kept for completeness
        n_neut                  = costs.get("n_csg_neutralized", 0)
        n_sunk                  = costs.get("n_csg_sunk", 0)
        exchange_ratio          = costs.get("exchange_ratio", 0)
        scenario_short_description = label.split("--", 1)[-1].strip() if "--" in label else label
        _tot_n      += n;      _tot_ki   += ki;    _tot_kb    += kb
        _tot_sm6    += intercept_by_category.get("SM-6 / SM-2", 0)
        _tot_ciws   += intercept_by_category.get("CIWS / SeaRAM", 0)
        _tot_ship_v += ship_damage_usd; _tot_us_v += us_total_cost_usd;  _tot_kia   += us_kia
        _tot_neut   += n_neut; _tot_sunk += n_sunk
        _n_sc_counted += 1
        sc_rows += (
            f'<tr>'
            f'<td style="white-space:nowrap"><a href="scenario_{key}.html" style="color:{ACC}">'
            f'{label.split("--")[0].strip()}</a></td>'
            f'<td style="color:{LAB};font-size:10px;max-width:260px;overflow:hidden;'
            f'text-overflow:ellipsis;white-space:nowrap">{scenario_short_description}</td>'
            + _td(f'{n:,}',    _grad(n,  0, 10000, invert=True))
            + _td(f'{ki:,}',   _grad(ki/max(1,n), 0, 1, invert=True))
            + _td(f'<b style="color:{scenario_status_color}">{kb:,} ({breakthrough_percentage}%)</b>', None, bold=False)
            + _td(f'{dur:.0f}m')
            + _td(f'{intercept_by_category.get("SM-6 / SM-2",0):,}')
            + _td(f'{intercept_by_category.get("CIWS / SeaRAM",0):,}')
            + _td(f'−{_fc(ship_damage_usd)}', _grad(ship_damage_usd, _sh_lo, _sh_hi), bold=True)
            + _td(f'−{_fc(us_total_cost_usd)}',   _grad(us_total_cost_usd,   _us_lo, _us_hi), bold=True)
            + _td(f'−{us_kia:,}',       _grad(us_kia,     _ki_lo, _ki_hi), bold=True)
            + _td(f'{n_neut} neut / {n_sunk} sunk', _grad(n_neut, 0, 8))
            + _td(f'{exchange_ratio:.0f}:1',     _grad(exchange_ratio, 0, 500))
            + f'</tr>\n'
        )

    _tf_sc = f'background:{BG2};font-weight:bold;border-top:2px solid {ACC}55;'
    _avg_bt_pct = round(100 * _tot_kb / max(1, _tot_n))
    sc_total_row = (
        f'<tr style="{_tf_sc}">'
        f'<td style="color:{ACC};{_tf_sc}" colspan="2">TOTALS ({_n_sc_counted} scenarios)</td>'
        + _td(f'{_tot_n:,}',  RED,  bold=True)
        + _td(f'{_tot_ki:,}', GREEN, bold=True)
        + _td(f'<b style="color:{RED}">{_tot_kb:,} ({_avg_bt_pct}%)</b>', None, bold=False)
        + _td(f'—', None)
        + _td(f'{_tot_sm6:,}',  None, bold=True)
        + _td(f'{_tot_ciws:,}', None, bold=True)
        + _td(f'−{_fc(_tot_ship_v)}', RED, bold=True)
        + _td(f'−{_fc(_tot_us_v)}',   RED, bold=True)
        + _td(f'−{_tot_kia:,}',       RED, bold=True)
        + _td(f'{_tot_neut} neut / {_tot_sunk} sunk', _grad(_tot_neut, 0, 8*_n_sc_counted))
        + _td(f'—', None)
        + f'</tr>\n'
    )

    sc_table = _tbl(
        (f'<tr>{_th("Scenario","left")}{_th("Description","left")}'
         f'{_th("Launched")}{_th("Intercepted")}{_th("Breakthrough")}{_th("Duration")}'
         f'{_th("SM-6")}{_th("CIWS")}'
         f'{_th("Ship dmg")}{_th("US total")}{_th("US KIA")}'
         f'{_th("CSG status")}{_th("Exchange")}</tr>'),
        sc_rows + sc_total_row
    )

    # Aggregate CSG damage table
    csg_agg = {}
    for key, c in all_costs.items():
        for cname, bd in c.get("csg_breakdown", {}).items():
            if cname not in csg_agg:
                csg_agg[cname] = {"hits": 0, "damage_usd": 0, "kia": 0, "wia": 0,
                                  "n_neut": 0, "n_sunk": 0, "n_dmg": 0, "n_sc": 0,
                                  "asset": bd["asset_value_usd"], "crew": bd["personnel"]}
            ag = csg_agg[cname]
            ag["hits"]      += bd["hits"]
            ag["damage_usd"]+= bd["damage_usd"]
            ag["kia"]       += bd["kia"]
            ag["wia"]       += bd["wia"]
            ag["n_sc"]      += 1
            if "DESTROYED" in bd.get("status", ""): ag["n_neut"] += 1
            if bd.get("is_sunk"):                   ag["n_sunk"] += 1
            elif bd.get("status") == "DAMAGED":     ag["n_dmg"]  += 1

    n_sc = max(len(all_costs), 1)
    _avgh = [ag["hits"]/ag["n_sc"] for ag in csg_agg.values()]
    _avgd = [ag["damage_usd"]/ag["n_sc"] for ag in csg_agg.values()]
    _avgk = [ag["kia"]/ag["n_sc"] for ag in csg_agg.values()]
    _ah_lo, _ah_hi = 0, max(max(_avgh, default=1), 1)
    _ad_lo, _ad_hi = 0, max(max(_avgd, default=1), 1)
    _ak_lo, _ak_hi = 0, max(max(_avgk, default=1), 1)

    csg_agg_rows = ""
    _agg_tot_asset = _agg_tot_crew = 0
    _agg_tot_hits = _agg_tot_dmg = _agg_tot_kia = 0
    _agg_tot_neut = _agg_tot_sunk = 0
    _n_csg_rows = 0
    for cname, ag in csg_agg.items():
        ns = ag["n_sc"]
        avg_h = ag["hits"] / ns; avg_d = ag["damage_usd"] / ns; avg_k = ag["kia"] / ns
        neut_pct = 100 * ag["n_neut"] / n_sc; sunk_pct = 100 * ag["n_sunk"] / n_sc
        _agg_tot_asset += ag["asset"]; _agg_tot_crew += ag["crew"]
        _agg_tot_hits  += avg_h;       _agg_tot_dmg  += avg_d;  _agg_tot_kia += avg_k
        _agg_tot_neut  += ag["n_neut"]; _agg_tot_sunk += ag["n_sunk"]
        _n_csg_rows += 1
        csg_agg_rows += (
            f'<tr>'
            f'<td style="color:{ACC};white-space:nowrap">{cname}</td>'
            f'<td style="color:{DAT}">${ag["asset"]/1e9:.1f}B</td>'
            f'<td style="color:{DAT}">{ag["crew"]:,}</td>'
            + _td(f'{avg_h:.1f}',           _grad(avg_h, _ah_lo, _ah_hi))
            + _td(f'−{_fc(avg_d)}',         _grad(avg_d, _ad_lo, _ad_hi), bold=True)
            + _td(f'−{avg_k:.0f}',          _grad(avg_k, _ak_lo, _ak_hi), bold=True)
            + _td(f'{neut_pct:.0f}% ✕',     _grad(neut_pct, 0, 80))
            + _td(f'{sunk_pct:.0f}% 〜',    _grad(sunk_pct, 0, 60))
            + f'</tr>\n'
        )

    _tf_agg = f'background:{BG2};font-weight:bold;border-top:2px solid {ACC}55;'
    _agg_neut_pct = 100 * _agg_tot_neut / max(1, n_sc * _n_csg_rows)
    _agg_sunk_pct = 100 * _agg_tot_sunk / max(1, n_sc * _n_csg_rows)
    csg_agg_total_row = (
        f'<tr style="{_tf_agg}">'
        f'<td style="color:{ACC};{_tf_agg}">FLEET TOTAL</td>'
        f'<td style="color:{DAT};{_tf_agg}">${_agg_tot_asset/1e9:.1f}B</td>'
        f'<td style="color:{DAT};{_tf_agg}">{_agg_tot_crew:,}</td>'
        + _td(f'{_agg_tot_hits:.1f}',      RED,  bold=True)
        + _td(f'−{_fc(_agg_tot_dmg)}',     RED,  bold=True)
        + _td(f'−{_agg_tot_kia:.0f}',      RED,  bold=True)
        + _td(f'{_agg_neut_pct:.0f}% ✕',  _grad(_agg_neut_pct, 0, 80), bold=True)
        + _td(f'{_agg_sunk_pct:.0f}% 〜', _grad(_agg_sunk_pct, 0, 60), bold=True)
        + f'</tr>\n'
    )

    csg_agg_table = _tbl(
        (f'<tr>{_th("CSG","left")}{_th("Asset value","left")}{_th("Personnel","left")}'
         f'{_th("Avg hits")}{_th("Avg damage")}{_th("Avg KIA")}'
         f'{_th("Neutralized %")}{_th("Sunk %")}</tr>'),
        csg_agg_rows + csg_agg_total_row
    )

    # SSPK reference table
    sspk_rows = ""
    for mname, sp in MUNITION_SSPK.items():
        pct = round(sp["sspk"] * 100)
        mdef = MUNITIONS.get(mname, {})
        mc = _kml_to_css(mdef.get("color", "ff888888"))
        sspk_col = _grad(sp["sspk"], 0.0, 1.0, invert=True)
        bar = f'<div style="display:inline-block;width:{max(4,pct)}px;height:8px;background:{sspk_col};vertical-align:middle;border-radius:2px"></div>'
        sspk_rows += (
            f'<tr>'
            f'<td style="color:{mc};white-space:nowrap">{mname}</td>'
            + _td(f'{bar} {pct}%', sspk_col, align="left", bold=True)
            + f'<td style="color:{LAB};font-size:10px">{sp.get("interceptor","—")}</td>'
            + f'<td style="color:{DIM};font-size:10px;max-width:350px;white-space:normal">'
            + f'{sp.get("notes","")}</td>'
            + f'</tr>\n'
        )

    sspk_table = _tbl(
        (f'<tr>{_th("Munition","left")}{_th("SSPK","left")}'
         f'{_th("Best interceptor","left")}{_th("Notes","left")}</tr>'),
        sspk_rows
    )

    nav_links = "".join(
        f'<a href="scenario_{k}.html">{SCENARIOS[k]["label"].split("--")[0].strip()}</a> '
        for k in SCENARIO_ORDER if k in stats)

    # Fleet summary cards
    _all_n  = sum(s[1] for s in stats.values())
    _all_ki = sum(s[2] for s in stats.values())
    _all_kb = sum(s[3] for s in stats.values())
    _all_kia = sum(all_costs[k].get("us_mil_kia", 0) for k in stats)
    _all_dmg = sum(all_costs[k].get("us_ship_damage", 0) for k in stats)
    _all_ex  = sum(all_costs[k].get("exchange_ratio", 0) for k in stats) / max(1, len(stats))
    _sum_bt_pct = round(100 * _all_kb / max(1, _all_n))
    summary_cards = (
        f'<div class="cards">'
        f'<div class="card" style="border-top-color:{IRAN_C}">'
        f'<div class="card-label">Total launched (all scenarios)</div>'
        f'<div class="card-value" style="color:{IRAN_C}">{_all_n:,}</div>'
        f'<div class="card-sub">cumulative munitions</div></div>'

        f'<div class="card" style="border-top-color:{GREEN}">'
        f'<div class="card-label">Total intercepted</div>'
        f'<div class="card-value" style="color:{GREEN}">{_all_ki:,}</div>'
        f'<div class="card-sub">{round(100*_all_ki/max(1,_all_n))}% avg kill rate</div></div>'

        f'<div class="card" style="border-top-color:{RED}">'
        f'<div class="card-label">Total breakthrough</div>'
        f'<div class="card-value" style="color:{RED}">{_all_kb:,}</div>'
        f'<div class="card-sub">{_sum_bt_pct}% avg penetration</div></div>'

        f'<div class="card" style="border-top-color:{RED}">'
        f'<div class="card-label">Cumulative US KIA</div>'
        f'<div class="card-value" style="color:{RED}">{_all_kia:,}</div>'
        f'<div class="card-sub">across {len(stats)} scenarios</div></div>'

        f'<div class="card" style="border-top-color:{ORANGE}">'
        f'<div class="card-label">Cumulative ship damage</div>'
        f'<div class="card-value" style="color:{ORANGE}">{_fc(_all_dmg)}</div>'
        f'<div class="card-sub">hull + air wing losses</div></div>'

        f'<div class="card" style="border-top-color:{YELLOW}">'
        f'<div class="card-label">Avg exchange ratio</div>'
        f'<div class="card-value" style="color:{YELLOW}">{_all_ex:.0f}:1</div>'
        f'<div class="card-sub">US cost / Iran cost</div></div>'
        f'</div>'
    )

    sum_body = (
        f'<div class="topbar">'
        f'<span class="topbar-title">◈ PERSIAN GULF WARGAME — ALL-SCENARIO SUMMARY</span>'
        f'<span class="topbar-sub">Simulation start: 2026-04-01 06:00 UTC &nbsp;·&nbsp; {len(stats)} scenarios</span>'
        f'</div>'
        f'<h1>Persian Gulf Wargame — All-Scenario Summary</h1>'
        f'<div class="ts">{_TS}</div>'
        f'<div class="nav">{nav_links}</div>'
        f'{summary_cards}'
        f'{_section("Scenario Comparison")}{sc_table}'
        f'{_section("Aggregate CSG Damage — Averaged across all scenarios")}{csg_agg_table}'
        f'{_section("SSPK Reference — Interceptor Effectiveness")}{sspk_table}'
    )

    sum_path = os.path.join(out_dir, "summary.html")
    with open(sum_path, "w", encoding="utf-8") as fh:
        fh.write(_page("Persian Gulf Wargame — Summary", sum_body))
    written.append(sum_path)

    return written


# ============================================================
# KHARG ISLAND AIR ASSAULT SCENARIO
# ============================================================

def generate_kharg_assault_kml(out_dir=None, variant="north_west"):
    """
    KML/KMZ: USMC heliborne assault on Kharg Island + Shahed-136 drone counterattack.

    variant="north_west" (default):
      LHA-7 USS Tripoli approaches from south; Marines land on NW airstrip + plateau.

    variant="south_east":
      LHA-7 USS Tripoli approaches from SE; Marines land on southern beach + east
      plateau — flanking maneuver to avoid concentrated northern IRGC defences.

    Helicopter assault:
      12 × MV-22B Osprey  (24 troops, 446 km/h)
       4 × CH-53E Super Stallion (37 troops, 278 km/h)
       4 × AH-1Z Viper escort
      436 Marines/wave × 6 waves = 2,500 Marines ashore

    Drone counterattack (post-landing):
      2,000 Shahed-136 in 5 waves from multiple Iranian sites
      5% AI/CV-guided (guaranteed kills) | Stinger Pk 25% | 100-round magazine
      CEP 30m | kill radius 10m | 50m=-2HP | 100m=-1HP

    Fireteam icons: 1,250 × 4-man fireteams, colour-coded HP, random path walking
      green=4HP  yellow=3HP  orange=1-2HP  red=KIA (0HP)

    Sortie counter: placemark tracks completed/remaining trips with timeline
    Ground battle: Lanchester square-law attrition (IRGC vs. USMC, Marines 5× IRGC)
    Full gx:Track animated drone trajectories with AI two-phase terminal guidance

    Sources: NAVAIR MV-22B fact sheet; Boeing CH-53E spec; IISS Military Balance 2024;
             MAGTF Handbook; Jane's Intelligence Review; open-source Shahed-136 data
    """
    import math, zipfile as _zf, random as _random

    # ── Geography ──────────────────────────────────────────────────────────────
    KHARG_LON, KHARG_LAT = 50.3285, 29.2605

    if variant == "south_east":
        # SE flanking approach: fleet from south-east; LZs on south beach + east plateau
        LZ1_LON,   LZ1_LAT  = 50.317,  29.209    # LZ VIPER  — south beach
        LZ2_LON,   LZ2_LAT  = 50.334,  29.255    # LZ MAMBA  — east plateau
        LHA_LON,   LHA_LAT  = 50.510,  29.060    # LHA-7 USS Tripoli (SE approach)
        LPD1_LON,  LPD1_LAT = 50.430,  29.040    # LPD-30
        LPD2_LON,  LPD2_LAT = 50.590,  29.040    # LPD-29
        DDG_LON,   DDG_LAT  = 50.440,  29.150    # DDG escort
        # Restrict fireteam placement to southern+eastern portions of polygon
        # South zone: lat < 29.240; East zone: lon > 50.322
        PLACE_LAT_MAX = 29.240
        PLACE_LON_MIN = 50.295   # includes both south and east sub-zones
        SCENARIO_LABEL = "SE Flanking Assault (south beach + east plateau)"
        OUT_FILENAME   = "kharg_island_assault_se.kmz"
        SQ_SEED        = 43     # different seed for variety
    else:
        # Default NW approach: fleet from south; LZs on NW airstrip + plateau
        LZ1_LON,   LZ1_LAT  = 50.315,  29.252    # LZ FALCON — airstrip
        LZ2_LON,   LZ2_LAT  = 50.345,  29.258    # LZ EAGLE  — plateau
        LHA_LON,   LHA_LAT  = 50.325,  28.715    # LHA-7 USS Tripoli
        LPD1_LON,  LPD1_LAT = 50.175,  28.690    # LPD-30
        LPD2_LON,  LPD2_LAT = 50.475,  28.690    # LPD-29
        DDG_LON,   DDG_LAT  = 50.325,  28.855    # DDG escort
        PLACE_LAT_MAX = None   # full polygon
        PLACE_LON_MIN = None
        SCENARIO_LABEL = "NW Airstrip Assault (airstrip + plateau)"
        OUT_FILENAME   = "kharg_island_assault.kmz"
        SQ_SEED        = 42

    BUSH_LON,  BUSH_LAT = 50.843,  28.923    # Bushehr AB — Shahed launch site

    # ── Helicopter parameters ──────────────────────────────────────────────────
    MV22_KMH, MV22_TROOPS = 446, 24
    CH53_KMH, CH53_TROOPS = 278, 37
    AH1Z_KMH               = 295
    N_MV22, N_CH53, N_AH1Z = 12, 4, 4
    TROOPS_PER_WAVE = N_MV22 * MV22_TROOPS + N_CH53 * CH53_TROOPS  # 436
    TOTAL_MARINES   = 2_500
    FULL_WAVES      = TOTAL_MARINES // TROOPS_PER_WAVE
    REMAINDER       = TOTAL_MARINES %  TROOPS_PER_WAVE
    N_WAVES         = FULL_WAVES + (1 if REMAINDER else 0)
    UNLOAD_S, RELOAD_S = 180, 300

    # ── F-35B Lightning II parameters ─────────────────────────────────────────
    # LHA-7 USS Tripoli (America-class, aviation-centric) embarks 20 F-35Bs.
    # Real-world: America-class typically surges 13-16 F-35Bs; 20 is high-density
    # aviation configuration (no ground vehicles, full aviation stores).
    # Sources: NAVAIR F-35B STOVL fact sheet; USMC MAGTF Handbook 2025;
    #          USNI News LHA-7 deployment tracking; Jane's All the World's Aircraft.
    N_F35B           = 20           # F-35B Lightning IIs embarked on LHA-7
    F35B_KMH         = 850          # subsonic cruise ≈ Mach 0.8
    F35B_ALT_M       = 6_000        # strike cruise altitude (m AGL)
    F35B_CEP_M       = 3.0          # GBU-38 / GBU-32 JDAM GPS/INS CEP (m)
    # SEAD package (4 aircraft) — AGM-88E AARGM anti-radiation missile
    #   Range: 150+ km | Speed: Mach 1.8+ (sustained) → Mach 2+ (terminal)
    #   Guidance: passive-radar + GPS/INS + IIR terminal (can engage silent sites)
    #   Warhead: WDU-21/B 146 kg blast-fragmentation
    N_F35B_SEAD      = 4
    AGM88_PER_SEAD   = 2            # AGM-88E AARGM per SEAD aircraft
    AGM88_KMH        = 1_800        # AGM-88E sustained speed (≈ Mach 1.8)
    # CAS package (16 aircraft) — GBU-38 JDAM beast mode + self-defence AAMs
    #   GBU-38: Mk-82 500 lb body + JDAM kit | GPS/INS | CEP ≤ 3 m
    #   AIM-120C-7 AMRAAM: BVR self-defence (internal carry)
    #   AIM-9X Block II: short-range WVR (external pylons)
    N_F35B_CAS       = N_F35B - N_F35B_SEAD   # 16
    GBU38_PER_CAS    = 4            # GBU-38 JDAM (500 lb) per CAS sortie
    AIM120_PER_F35B  = 2            # AIM-120C-7 per aircraft (all sorties)
    AIM9X_PER_F35B   = 2            # AIM-9X Block II per CAS aircraft
    F35B_SORTIES     = 2            # sortie rotations (all CAS aircraft)
    F35B_REARM_S     = 1_800        # on-deck rearm + hot-refuel time (s)

    # ── Fireteam parameters ────────────────────────────────────────────────────
    MARINES_PER_SQUAD = 4                                    # 4-man fireteams
    N_SQUADS          = TOTAL_MARINES // MARINES_PER_SQUAD   # 625
    SQUAD_HP          = MARINES_PER_SQUAD                    # 4 HP per fireteam

    # ── Shahed-136 parameters ──────────────────────────────────────────────────
    SHAHED_KMH    = 185
    SHAHED_CEP_M  = 30.0
    KILL_M        = 10.0    # instant-kill radius
    DMG2_M        = 50.0    # -2 HP radius
    DMG1_M        = 100.0   # -1 HP radius
    DRONE_TOTAL   = 2_000
    # FIM-92 Stinger Pk vs. Shahed-136:
    #   DoD operational test baseline: 30% (FM 44-18-1; GAO-02-407T)
    #   Penalty for Shahed's weak piston-engine IR signature vs. turbojet: −5 pp
    #   Proximity fuze not fitted (standard RMP Block I issue): no bonus
    #   Adopted: 0.25 (25%) — consistent with academic median for IR MANPADS
    #   vs. slow, low-IR-signature targets (Laird & Keane, 2019; RAND MG-1104)
    STINGER_PK    = 0.25    # FIM-92 Stinger Pk vs. Shahed-136 — see note above
    STINGER_MAG   = 100     # total Stinger rounds available to the MAGTF
    STINGER_RNG   = 4.5     # km — Stinger max engagement range vs. slow/low target
    SHAHED_PEAK   = 50.0    # m — sea-skim cruise altitude
    SHAHED_SPD_KS = 0.052   # km/s — Shahed-136 cruise (≈187 km/h)
    # Helicopter proximity kill: AI drone within this radius → 50% Pk vs. helo
    HELO_KILL_KM  = 3.0     # km — AI drone lethal proximity to helicopter

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _dist_km(lon1, lat1, lon2, lat2):
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return 6_371 * 2 * math.asin(math.sqrt(a))

    def _flt_s(lon1, lat1, lon2, lat2, kmh):
        return _dist_km(lon1, lat1, lon2, lat2) / kmh * 3_600

    def _dist_m(lon1, lat1, lon2, lat2):
        """Equirectangular distance in metres — accurate enough for <500 m."""
        clat = math.cos(math.radians((lat1 + lat2) / 2))
        dx = (lon2 - lon1) * 111_000 * clat
        dy = (lat2 - lat1) * 111_000
        return math.sqrt(dx * dx + dy * dy)

    # ── Kharg Island polygon (user-supplied coastline, ~240 vertices) ─────────
    # Defines the actual island boundary for marine placement and LZ definition.
    KHARG_POLY = [
        (50.332952,29.262433),(50.332159,29.263401),(50.330614,29.265161),(50.329147,29.265400),
        (50.327973,29.265425),(50.327718,29.265526),(50.327053,29.265972),(50.326033,29.266666),
        (50.324599,29.266796),(50.323960,29.266787),(50.323503,29.266657),(50.322915,29.266488),
        (50.322449,29.266348),(50.321785,29.266149),(50.321033,29.266041),(50.320113,29.265830),
        (50.319075,29.265588),(50.318531,29.265541),(50.318011,29.265382),(50.317310,29.265695),
        (50.316590,29.266121),(50.316371,29.266397),(50.316169,29.266622),(50.315592,29.267258),
        (50.315143,29.267411),(50.314650,29.267721),(50.314309,29.267958),(50.314107,29.268180),
        (50.313906,29.268402),(50.313628,29.268658),(50.313442,29.268827),(50.313088,29.268889),
        (50.312796,29.268743),(50.312719,29.268325),(50.312489,29.268199),(50.312092,29.267741),
        (50.311917,29.267399),(50.311970,29.267181),(50.311896,29.266919),(50.311663,29.267013),
        (50.311198,29.267200),(50.310937,29.267397),(50.310565,29.267498),(50.310265,29.267633),
        (50.309357,29.268097),(50.307958,29.268302),(50.307273,29.268644),(50.306580,29.269047),
        (50.306114,29.269358),(50.305464,29.269594),(50.304985,29.269645),(50.304425,29.269789),
        (50.303866,29.269933),(50.302878,29.270274),(50.301782,29.270810),(50.300949,29.271316),
        (50.300348,29.271676),(50.299748,29.271804),(50.298854,29.271653),(50.298371,29.271579),
        (50.297623,29.271811),(50.297301,29.271864),(50.296839,29.271980),(50.296434,29.272119),
        (50.295642,29.272349),(50.294965,29.272389),(50.294349,29.272230),(50.293994,29.272215),
        (50.293404,29.272403),(50.293183,29.272555),(50.292653,29.272537),(50.291906,29.272660),
        (50.291638,29.272566),(50.290678,29.272232),(50.290253,29.272084),(50.289618,29.271866),
        (50.288475,29.271425),(50.287967,29.271199),(50.287564,29.271010),(50.287045,29.270833),
        (50.286631,29.270694),(50.286298,29.270476),(50.285906,29.270077),(50.285590,29.269811),
        (50.285326,29.269562),(50.284895,29.269310),(50.284224,29.268935),(50.283643,29.268451),
        (50.283532,29.268264),(50.283665,29.268005),(50.283892,29.267617),(50.284381,29.267288),
        (50.285631,29.266097),(50.285852,29.265729),(50.286049,29.265255),(50.286458,29.264264),
        (50.286974,29.263853),(50.287657,29.263437),(50.288160,29.263077),(50.289062,29.261978),
        (50.289631,29.261788),(50.290107,29.261892),(50.290637,29.261830),(50.291590,29.261181),
        (50.292182,29.260916),(50.292548,29.260650),(50.292851,29.260225),(50.293303,29.259153),
        (50.293687,29.258063),(50.293938,29.257616),(50.294227,29.257212),(50.294438,29.256693),
        (50.295179,29.255393),(50.295445,29.254888),(50.295774,29.254331),(50.296349,29.253521),
        (50.296987,29.252543),(50.297255,29.252046),(50.297486,29.251491),(50.297421,29.250623),
        (50.297351,29.249315),(50.297344,29.248951),(50.297416,29.248709),(50.297505,29.248212),
        (50.297489,29.247482),(50.297609,29.246892),(50.297681,29.245877),(50.297818,29.245032),
        (50.297962,29.244550),(50.298048,29.244261),(50.298134,29.243971),(50.298205,29.243729),
        (50.298466,29.243428),(50.298538,29.243187),(50.298788,29.242111),(50.298976,29.241435),
        (50.299096,29.241003),(50.299202,29.240571),(50.299348,29.239999),(50.299546,29.239287),
        (50.299890,29.238662),(50.300382,29.237962),(50.300684,29.237523),(50.301150,29.236557),
        (50.301532,29.235875),(50.302156,29.234543),(50.302294,29.234070),(50.302409,29.233889),
        (50.302652,29.233477),(50.302940,29.232922),(50.303290,29.232170),(50.303472,29.231624),
        (50.303779,29.230978),(50.304135,29.230181),(50.304654,29.229025),(50.304805,29.228605),
        (50.305014,29.227954),(50.305772,29.226403),(50.306254,29.225031),(50.306418,29.224427),
        (50.306727,29.223140),(50.306774,29.221700),(50.306740,29.220693),(50.306890,29.220174),
        (50.307135,29.219192),(50.307218,29.218881),(50.307366,29.218368),(50.307573,29.217687),
        (50.308024,29.216954),(50.308630,29.216144),(50.308975,29.215318),(50.309920,29.214064),
        (50.310457,29.213266),(50.311444,29.211816),(50.312359,29.210933),(50.313036,29.210234),
        (50.313614,29.209818),(50.314341,29.209574),(50.314776,29.209382),(50.315664,29.208882),
        (50.316869,29.208254),(50.317838,29.208192),(50.318454,29.208206),(50.319107,29.208288),
        (50.320147,29.208528),(50.321643,29.209034),(50.323227,29.209893),(50.323962,29.210058),
        (50.325721,29.211213),(50.326980,29.212475),(50.327427,29.213172),(50.328404,29.214410),
        (50.329264,29.215684),(50.329289,29.215843),(50.329504,29.217063),(50.329503,29.217414),
        (50.329074,29.218700),(50.328956,29.219236),(50.328336,29.220083),(50.327481,29.220932),
        (50.327010,29.221226),(50.326672,29.221493),(50.325702,29.222442),(50.325300,29.222828),
        (50.325056,29.222915),(50.324856,29.223108),(50.324608,29.223411),(50.324437,29.224706),
        (50.324515,29.226091),(50.324545,29.226682),(50.324493,29.227316),(50.324565,29.228326),
        (50.324127,29.229987),(50.323788,29.230948),(50.323655,29.231409),(50.323644,29.231895),
        (50.323117,29.233429),(50.323022,29.233738),(50.322950,29.234697),(50.323122,29.235319),
        (50.323147,29.235923),(50.323268,29.236974),(50.323633,29.237641),(50.323848,29.237847),
        (50.324387,29.239067),(50.324380,29.239288),(50.324282,29.239601),(50.324673,29.241241),
        (50.324603,29.241997),(50.324492,29.242680),(50.324664,29.244272),(50.324965,29.245064),
        (50.325466,29.245957),(50.326404,29.247346),(50.326797,29.248167),(50.327707,29.249053),
        (50.328076,29.249478),(50.328535,29.250492),(50.328894,29.251372),(50.329435,29.252413),
        (50.330273,29.253821),(50.330731,29.255660),(50.331129,29.256279),(50.332144,29.257579),
        (50.332705,29.257894),(50.333191,29.258251),(50.333577,29.258467),(50.333741,29.258685),
        (50.333891,29.258958),(50.334354,29.259492),(50.334584,29.259962),(50.334765,29.260361),
        (50.334862,29.260564),(50.335203,29.261012),(50.332952,29.262433),
    ]

    def _in_polygon(lon, lat, poly):
        """Ray-casting point-in-polygon test (Jordan curve theorem)."""
        n, inside = len(poly), False
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def _poly_bbox(poly):
        lons = [p[0] for p in poly]
        lats = [p[1] for p in poly]
        return min(lons), max(lons), min(lats), max(lats)

    POLY_LON_MIN, POLY_LON_MAX, POLY_LAT_MIN, POLY_LAT_MAX = _poly_bbox(KHARG_POLY)

    def _cep_scatter(lon, lat, cep_m, rng_):
        sigma = cep_m / 1.1774
        u1 = max(rng_.random(), 1e-10)
        u2 = rng_.random()
        z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z1 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        clat = math.cos(math.radians(lat))
        return lon + z0 * sigma / (111_000 * clat), lat + z1 * sigma / 111_000

    def _ts(t_s):
        return fmt_time(sim_time(t_s))

    def _tspan(b, e):
        return f"<TimeSpan><begin>{_ts(b)}</begin><end>{_ts(e)}</end></TimeSpan>"

    def _pm_point(name, lon, lat, style_id, desc="", ts_b=None, ts_e=None):
        ts = _tspan(ts_b, ts_e) if ts_b is not None else ""
        return (f'  <Placemark><name>{name}</name>'
                f'<description><![CDATA[{desc}]]></description>'
                f'<styleUrl>#{style_id}</styleUrl>{ts}'
                f'<Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates>'
                f'</Point></Placemark>\n')

    def _pm_line(name, pts, style_id, ts_b, ts_e, alt=300, n_segs=100):
        """LineString placemark with n_segs interpolated segments for smooth animation."""
        if n_segs > 1 and len(pts) == 2:
            (lo1, la1), (lo2, la2) = pts
            pts = [(lo1 + (lo2 - lo1) * i / n_segs,
                    la1 + (la2 - la1) * i / n_segs)
                   for i in range(n_segs + 1)]
        coords = " ".join(f"{lo:.5f},{la:.5f},{alt}" for lo, la in pts)
        return (f'  <Placemark><name>{name}</name>'
                f'<styleUrl>#{style_id}</styleUrl>'
                f'{_tspan(ts_b, ts_e)}'
                f'<LineString><altitudeMode>relativeToGround</altitudeMode>'
                f'<coordinates>{coords}</coordinates>'
                f'</LineString></Placemark>\n')

    def _ship_offset(idx, n, base_lon, base_lat, spread=0.006):
        angle = 2 * math.pi * idx / max(n, 1)
        return base_lon + spread * math.sin(angle), base_lat + spread * math.cos(angle)

    def _helo_arc_pts(lon1, lat1, lon2, lat2, cruise_m, n_pts=14):
        """NOE helicopter altitude profile for gx:Track (relativeToGround).

        Profile: ramp from 15 m (deck/hover) up to cruise_m over first 12% of
        flight, hold cruise, then descend to 15 m over final 12%.
        Realistic for rotary-wing NOE approach to an opposed landing zone.
        """
        pts = []
        for i in range(n_pts + 1):
            t = i / n_pts
            lon, lat = gc_interp(lon1, lat1, lon2, lat2, t)
            if t <= 0.12:
                alt = 15.0 + (cruise_m - 15.0) * (t / 0.12)
            elif t >= 0.88:
                alt = 15.0 + (cruise_m - 15.0) * ((1.0 - t) / 0.12)
            else:
                alt = cruise_m
            pts.append((lon, lat, alt))
        return pts

    def _jet_arc_pts(lon1, lat1, lon2, lat2, cruise_m=6_000, n_pts=14):
        """High-altitude jet strike altitude profile for gx:Track (relativeToGround).

        Profile: ramp from 50 m (deck launch / STOVL rotation) to cruise_m over
        the first 8% of flight, hold cruise, then descend to 300 m over the final
        10% for weapon-delivery pass.  Realistic for F-35B STOVL low-observable
        strike profile (no afterburner on transit; weapon-release above threat WEZ).
        """
        pts = []
        for i in range(n_pts + 1):
            t = i / n_pts
            lon, lat = gc_interp(lon1, lat1, lon2, lat2, t)
            if t <= 0.08:
                alt = 50.0 + (cruise_m - 50.0) * (t / 0.08)
            elif t >= 0.90:
                alt = 300.0 + (cruise_m - 300.0) * ((1.0 - t) / 0.10)
            else:
                alt = float(cruise_m)
            pts.append((lon, lat, alt))
        return pts

    def _circle_kml_pts(clon, clat, radius_km, n_pts=72):
        """Return KML coordinate string approximating a ground-level circle polygon."""
        clat_r = math.cos(math.radians(clat))
        coords = []
        for i in range(n_pts + 1):
            angle = 2 * math.pi * i / n_pts
            dlon = radius_km / (111.0 * clat_r) * math.sin(angle)
            dlat = radius_km / 111.0 * math.cos(angle)
            coords.append(f"{clon + dlon:.6f},{clat + dlat:.6f},0")
        return " ".join(coords)

    # ── Timing ────────────────────────────────────────────────────────────────
    T_MV22 = _flt_s(LHA_LON, LHA_LAT, LZ1_LON, LZ1_LAT, MV22_KMH)   # ≈484 s
    T_CH53 = _flt_s(LHA_LON, LHA_LAT, LZ1_LON, LZ1_LAT, CH53_KMH)   # ≈777 s
    T_AH1Z  = _flt_s(DDG_LON, DDG_LAT, LZ1_LON, LZ1_LAT, AH1Z_KMH)
    T_F35B  = _flt_s(LHA_LON, LHA_LAT, KHARG_LON, KHARG_LAT, F35B_KMH)
    # SEAD standoff fire point: 60% of the way from LHA to Kharg (~36 km south)
    # AGM-88E range is 150+ km so this gives massive margin; keeps F-35B outside
    # the HQ-2/HAWK 40 km engagement envelope during the fire run.
    F35B_SEAD_FIRE_LON = LHA_LON + (KHARG_LON - LHA_LON) * 0.60
    F35B_SEAD_FIRE_LAT = LHA_LAT + (KHARG_LAT - LHA_LAT) * 0.60
    T_F35B_TO_FIRE = _flt_s(LHA_LON, LHA_LAT,
                             F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT, F35B_KMH)
    WAVE_CYCLE_S  = T_MV22 + UNLOAD_S + T_MV22 + RELOAD_S             # ≈1448 s
    wave_depart_s = [w * WAVE_CYCLE_S for w in range(N_WAVES)]
    wave_arrive_s = [d + T_MV22 for d in wave_depart_s]
    wave_return_s = [d + T_MV22 + UNLOAD_S + T_MV22 for d in wave_depart_s]
    last_arrive_s = wave_arrive_s[-1]
    SIM_END_S     = last_arrive_s + 7_200   # 2 h after final wave

    # ── Generate fireteam positions uniformly inside Kharg Island polygon ────────
    # Rejection sampling within the polygon bounding box.
    # Each wave's fireteams land and disperse within the polygon.
    sq_rng = _random.Random(SQ_SEED)
    squads_per_wave = [TROOPS_PER_WAVE // MARINES_PER_SQUAD] * FULL_WAVES
    if REMAINDER:
        squads_per_wave.append(REMAINDER // MARINES_PER_SQUAD)

    def _rand_in_polygon(rng, poly, lon_min, lon_max, lat_min, lat_max, max_tries=500):
        for _ in range(max_tries):
            lon = rng.uniform(lon_min, lon_max)
            lat = rng.uniform(lat_min, lat_max)
            if _in_polygon(lon, lat, poly):
                return lon, lat
        return (lon_min + lon_max) / 2, (lat_min + lat_max) / 2  # fallback to centroid

    # For SE variant: restrict placement to southern+eastern portions of the polygon
    place_lon_min = PLACE_LON_MIN if PLACE_LON_MIN is not None else POLY_LON_MIN
    place_lat_max = PLACE_LAT_MAX if PLACE_LAT_MAX is not None else POLY_LAT_MAX

    squad_pos = []   # (lon, lat, wave_idx)
    for w_idx, n_sq in enumerate(squads_per_wave):
        for i in range(n_sq):
            lon, lat = _rand_in_polygon(sq_rng, KHARG_POLY,
                                        place_lon_min, POLY_LON_MAX,
                                        POLY_LAT_MIN, place_lat_max)
            squad_pos.append((lon, lat, w_idx))


    # ── Generate IRGC defensive positions ────────────────────────────────────────
    # 1,000 soldiers distributed inside the island polygon; 10% (100) carry MANPADS.
    N_IRGC           = 1_000
    IRGC_MP_FRAC      = 0.10
    N_IRGC_MP         = int(N_IRGC * IRGC_MP_FRAC)          # 100 MANPADS teams
    IRGC_MP_RNG_KM    = 4.0   # km — Misagh-2 (Iranian Stinger clone) effective range

    irgc_rng = _random.Random(55)
    irgc_pos = []   # (lon, lat, has_manpads)
    for _ii in range(N_IRGC):
        _lon, _lat = _rand_in_polygon(irgc_rng, KHARG_POLY,
                                      POLY_LON_MIN, POLY_LON_MAX,
                                      POLY_LAT_MIN, POLY_LAT_MAX)
        irgc_pos.append((_lon, _lat, _ii < N_IRGC_MP))

    # ── Generate 1,000 Shahed-136 drone waves ─────────────────────────────────
    # 5 waves from multiple Iranian launch sites, 7 min after last Marines ashore.
    # 5% are AI/computer-vision guided (AI_SHAHED_FRACTION) → guaranteed kills.
    # 95% standard → FIM-92 Stinger MANPADS intercept roll (Pk 70%).
    drone_rng   = _random.Random(77)
    # Drones launch immediately when first Marines touch down (T+0 of wave 1 arrival)
    BASE_LAUNCH = wave_arrive_s[0]

    # Iranian launch sites with (lon, lat, weight) for weighted selection
    D_SITES = [
        (50.843, 28.923, 0.35, "Bushehr AB"),        # very close — 82 km
        (54.332, 27.684, 0.25, "Lar Airbase"),        # 180 km
        (55.937, 26.783, 0.20, "Qeshm Island"),       # 280 km
        (56.375, 27.188, 0.12, "Bandar Abbas"),       # 260 km
        (57.798, 25.640, 0.08, "Jask Base"),          # 360 km
    ]
    _sw_acc, _site_cw = 0.0, []
    for *_, sw, _sn in D_SITES:
        _sw_acc += sw
        _site_cw.append(_sw_acc)

    def _pick_site():
        r = drone_rng.random()
        for i, cw in enumerate(_site_cw):
            if r <= cw:
                return D_SITES[i]
        return D_SITES[-1]

    # 2,000 drones in 5 escalating waves: 300 / 400 / 500 / 400 / 400
    DRONE_WAVES = [
        (0,     300, "α"),
        (1800,  400, "β"),
        (3600,  500, "γ"),
        (5400,  400, "δ"),
        (7200,  400, "ε"),
    ]

    # Weighted target clusters on Kharg Island
    D_TARGETS = [
        (LZ1_LON, LZ1_LAT,  0.30),   # airstrip — high priority
        (50.308,  29.275,   0.20),   # oil terminal
        (50.330,  29.265,   0.20),   # central
        (LZ2_LON, LZ2_LAT,  0.15),   # LZ EAGLE
        (50.320,  29.235,   0.15),   # south perimeter
    ]
    _tw_acc, _tgt_cw = 0.0, []
    for *_, tw in D_TARGETS:
        _tw_acc += tw
        _tgt_cw.append(_tw_acc)

    def _pick_tgt():
        r = drone_rng.random()
        for i, cw in enumerate(_tgt_cw):
            if r <= cw:
                return D_TARGETS[i][:2]
        return D_TARGETS[-1][:2]

    all_drones     = []
    stinger_rounds = STINGER_MAG   # magazine counter — depletes as rounds are fired
    for wave_off, n_d, wave_lbl in DRONE_WAVES:
        for d in range(n_d):
            site_info = _pick_site()
            s_lon, s_lat = site_info[0], site_info[1]
            site_name    = site_info[3]
            tlon, tlat   = _pick_tgt()
            imp_lon, imp_lat = _cep_scatter(tlon, tlat, SHAHED_CEP_M, drone_rng)

            # 5% AI-guided: guaranteed breakthrough, tighter scatter, two-phase path
            is_ai    = drone_rng.random() < AI_SHAHED_FRACTION
            launch_s = BASE_LAUNCH + wave_off + d * 8   # 8-s stagger within wave

            full_dist_km = _dist_km(s_lon, s_lat, imp_lon, imp_lat)
            flight_s     = full_dist_km / SHAHED_SPD_KS

            if is_ai:
                # AI terminal target — small ±0.01° extra scatter for visual variety
                ai_tgt_lon = imp_lon + drone_rng.uniform(-0.01, 0.01)
                ai_tgt_lat = imp_lat + drone_rng.uniform(-0.01, 0.01)
                lock_frac  = max(0.05, 1.0 - SHAHED_AI_LOCK_KM / max(full_dist_km, SHAHED_AI_LOCK_KM + 1))
                is_int     = False          # AI always breaks through
                int_lon, int_lat, int_s = None, None, None
                stinger_expended = False
            else:
                ai_tgt_lon = ai_tgt_lat = None
                lock_frac  = None
                # Stinger engages at STINGER_RNG km — magazine-limited
                if stinger_rounds > 0:
                    stinger_rounds -= 1
                    stinger_expended = True
                    if full_dist_km > STINGER_RNG:
                        int_frac = 1.0 - STINGER_RNG / full_dist_km
                        int_frac = min(int_frac, 0.97)
                    else:
                        int_frac = 0.50
                    is_int = drone_rng.random() < STINGER_PK
                else:
                    stinger_expended = False
                    is_int = False   # no rounds left — drone passes uncontested
                if is_int:
                    int_f   = int_frac + drone_rng.uniform(-0.03, 0.03)
                    int_lon = s_lon + (imp_lon - s_lon) * int_f
                    int_lat = s_lat + (imp_lat - s_lat) * int_f
                    int_s   = launch_s + flight_s * int_f
                else:
                    int_lon = int_lat = int_s = None

            impact_s = launch_s + flight_s

            all_drones.append({
                'launch_s':  launch_s,   'impact_s':  impact_s,
                'imp_lon':   imp_lon,    'imp_lat':   imp_lat,
                'src_lon':   s_lon,      'src_lat':   s_lat,
                'site_name': site_name,
                'dist_km':   full_dist_km,
                'flight_s':  flight_s,
                'is_ai':     is_ai,
                'ai_tgt_lon': ai_tgt_lon, 'ai_tgt_lat': ai_tgt_lat,
                'lock_frac': lock_frac,
                'is_int':    is_int,
                'stinger_fired': stinger_expended,
                'int_lon':   int_lon,    'int_lat':   int_lat,
                'int_s':     int_s,
                'wave':      wave_lbl,   'idx':       d + 1,
            })

    # ── Pre-compute helicopter sortie schedule ─────────────────────────────────
    # Track which helos are active and when, so AI drones can engage them.
    # Each entry: (helo_id, type, wave, dep_s, arr_s, mid_lon, mid_lat)
    helo_schedule = []    # all sorties for all helos
    helo_ids_mv22 = [f"MV22-{i+1}" for i in range(N_MV22)]
    helo_ids_ch53 = [f"CH53-{i+1}" for i in range(N_CH53)]
    helo_ids_ah1z = [f"AH1Z-{i+1}" for i in range(N_AH1Z)]
    all_helo_ids  = helo_ids_mv22 + helo_ids_ch53 + helo_ids_ah1z

    for w in range(N_WAVES):
        wave_start_s = wave_depart_s[w]
        arrive_lz_s  = wave_arrive_s[w]
        tlon = LZ1_LON if w % 2 == 0 else LZ2_LON
        tlat = LZ1_LAT if w % 2 == 0 else LZ2_LAT
        n_mv22_w = N_MV22 if w < FULL_WAVES else max(1, round(N_MV22 * REMAINDER / TROOPS_PER_WAVE))
        n_ch53_w = N_CH53 if w < FULL_WAVES else max(1, round(N_CH53 * REMAINDER / TROOPS_PER_WAVE))
        for i in range(n_mv22_w):
            slon, slat = _ship_offset(i, n_mv22_w, LHA_LON, LHA_LAT, 0.007)
            stag = i * 20
            dep_s = wave_start_s + stag
            arr_s = dep_s + T_MV22
            mid_lon = (slon + tlon) / 2
            mid_lat = (slat + tlat) / 2
            helo_schedule.append((helo_ids_mv22[i], "MV-22B", w, dep_s, arr_s, mid_lon, mid_lat))
        for i in range(n_ch53_w):
            ch53_src = [(LHA_LON, LHA_LAT), (LHA_LON, LHA_LAT), (LPD1_LON, LPD1_LAT), (LPD2_LON, LPD2_LAT)]
            blon, blat = ch53_src[i % len(ch53_src)]
            slon, slat = _ship_offset(i, n_ch53_w, blon, blat, 0.005)
            stag = i * 30
            dep_s = wave_start_s + stag
            arr_s = dep_s + _flt_s(slon, slat, LZ1_LON, LZ1_LAT, CH53_KMH)
            mid_lon = (slon + LZ1_LON) / 2
            mid_lat = (slat + LZ1_LAT) / 2
            helo_schedule.append((helo_ids_ch53[i], "CH-53E", w, dep_s, arr_s, mid_lon, mid_lat))
        for i in range(N_AH1Z):
            slon, slat = _ship_offset(i, N_AH1Z, DDG_LON, DDG_LAT, 0.004)
            dep_s  = wave_start_s
            arr_s  = dep_s + T_AH1Z
            mid_lon = (slon + LZ1_LON) / 2
            mid_lat = (slat + LZ1_LAT) / 2
            helo_schedule.append((helo_ids_ah1z[i], "AH-1Z", w, dep_s, arr_s, mid_lon, mid_lat))

    # ── AI drone vs. helicopter engagement ────────────────────────────────────
    # For each AI breakthrough drone, check if any helicopter is in its outbound
    # leg at impact time and within HELO_KILL_KM of the drone's terminal path.
    # If so: 50% Pk.  A downed helicopter is removed from all subsequent waves.
    helo_rng     = _random.Random(55)
    downed_helos = set()           # helo_ids of destroyed aircraft
    helo_kill_events = []          # [(helo_id, type, wave_idx, kill_time_s, drone_wave)]

    for drone in sorted(all_drones, key=lambda d: d['impact_s']):
        if not drone['is_ai'] or drone['is_int']:
            continue
        imp_lon_d = drone['ai_tgt_lon']
        imp_lat_d = drone['ai_tgt_lat']
        imp_t     = drone['impact_s']
        # Check all helos in outbound leg at impact time
        for helo_id, helo_type, helo_wave, dep_s, arr_s, mid_lon, mid_lat in helo_schedule:
            if helo_id in downed_helos:
                continue   # already shot down
            if not (dep_s <= imp_t <= arr_s):
                continue   # not in the air at this moment
            # Interpolate helo position at imp_t
            frac     = (imp_t - dep_s) / max(arr_s - dep_s, 1)
            tlon_h   = LZ1_LON if helo_wave % 2 == 0 else LZ2_LON
            tlat_h   = LZ1_LAT if helo_wave % 2 == 0 else LZ2_LAT
            h_lon = mid_lon - (1 - frac) * (mid_lon - LHA_LON) + frac * (tlon_h - mid_lon)
            h_lat = mid_lat - (1 - frac) * (mid_lat - LHA_LAT) + frac * (tlat_h - mid_lat)
            dist_km_hd = _dist_km(imp_lon_d, imp_lat_d, h_lon, h_lat)
            if dist_km_hd <= HELO_KILL_KM:
                if helo_rng.random() < 0.50:   # 50% Pk: AI drone kills helicopter
                    downed_helos.add(helo_id)
                    helo_kill_events.append((helo_id, helo_type, helo_wave, imp_t, drone['wave']))
                    break   # one drone downs one helicopter

    # ── IRGC Misagh-2 MANPADS vs. helicopter engagement ──────────────────────
    # Misagh-2 = Iranian FIM-92 Stinger analog (IR-guided, 4 km range, 4.5 km ceiling).
    # Pre-assault F-35B SEAD/CAS and AH-1Z escort suppress most teams, but the
    # remainder actively engage incoming helos on every approach leg.
    #
    # Pk calibration (IR MANPADS vs. rotary-wing — open-source assessments):
    #   MV-22B Osprey:       0.18  (fast 446 km/h tiltrotor; limited flare dispenser)
    #   CH-53E Super Stallion: 0.28  (large 278 km/h heavy-lift; high IR signature)
    #   AH-1Z Viper:         0.22  (armed escort; AN/AAR-47 MAWS but no towed decoy)
    # Sources: RAND MR-1078; Jane's Surface-to-Air Missiles 2024; DoD ATEC 2023
    MISAGH_PK_TYPE   = {'MV-22B': 0.18, 'CH-53E': 0.28, 'AH-1Z': 0.22}
    MISAGH_SPEED_KMH = 2_000    # ~Mach 1.8 IR pursuit (Misagh-2 spec)
    MISAGH_PER_TEAM  = 2        # pre-positioned missiles per team
    MISAGH_SEAD_SURV = 0.70     # fraction surviving SEAD (30% neutralised pre-assault)
    MISAGH_RETALIATE = 0.70     # prob. AH-1Z/CAS destroys team after it fires

    misagh_rng = _random.Random(87)

    # Build active MANPADS pool after SEAD suppression
    mp_remaining = {}   # {irgc_pos_idx: missiles_left}
    for _mi, (_mlon, _mlat, _hmp) in enumerate(irgc_pos):
        if not _hmp:
            continue
        if misagh_rng.random() < MISAGH_SEAD_SURV:
            mp_remaining[_mi] = MISAGH_PER_TEAM

    misagh_events = []   # engagement records → KML + stats

    # Process helo sorties in chronological departure order
    for helo_id, helo_type, helo_wave, dep_s, arr_s, mid_lon, mid_lat in sorted(
            helo_schedule, key=lambda x: x[3]):
        if helo_id in downed_helos:
            continue  # already killed by drone strike

        # Engagement point: 75% along the outbound leg (inside the island WEZ)
        eng_frac = 0.75
        tlon_h   = LZ1_LON if helo_wave % 2 == 0 else LZ2_LON
        tlat_h   = LZ1_LAT if helo_wave % 2 == 0 else LZ2_LAT
        eng_t    = dep_s + (arr_s - dep_s) * eng_frac
        h_lon    = LHA_LON + (tlon_h - LHA_LON) * eng_frac
        h_lat    = LHA_LAT + (tlat_h - LHA_LAT) * eng_frac

        # Select closest active MANPADS team within range
        best_idx, best_d = None, IRGC_MP_RNG_KM + 1.0
        for _mi, _mleft in mp_remaining.items():
            if _mleft <= 0:
                continue
            _mlon, _mlat, _ = irgc_pos[_mi]
            _d = _dist_km(_mlon, _mlat, h_lon, h_lat)
            if _d <= IRGC_MP_RNG_KM and _d < best_d:
                best_d, best_idx = _d, _mi

        if best_idx is None:
            continue  # no rounds in range

        # Expend one missile; compute intercept
        mp_remaining[best_idx] -= 1
        mp_lon, mp_lat, _ = irgc_pos[best_idx]
        pk    = MISAGH_PK_TYPE.get(helo_type, 0.20)
        hit   = misagh_rng.random() < pk
        flt_s = best_d / MISAGH_SPEED_KMH * 3_600
        kill_t = eng_t + flt_s

        misagh_events.append({
            'helo_id':  helo_id,   'helo_type': helo_type,
            'wave':     helo_wave, 'eng_t':     eng_t,
            'kill_t':   kill_t,
            'mp_lon':   mp_lon,    'mp_lat':    mp_lat,
            'h_lon':    h_lon,     'h_lat':     h_lat,
            'dist_km':  best_d,    'hit':       hit,
        })

        if hit:
            downed_helos.add(helo_id)
            # AH-1Z escort identifies launch flash and retaliates
            if misagh_rng.random() < MISAGH_RETALIATE:
                mp_remaining[best_idx] = 0   # team destroyed

    misagh_shots  = len(misagh_events)
    misagh_hits   = sum(1 for e in misagh_events if e['hit'])
    misagh_misses = misagh_shots - misagh_hits

    # ── Compute actual troops delivered accounting for lost helicopters ────────
    # Surviving helicopter capacity per type
    mv22_surviving = [h for h in helo_ids_mv22 if h not in downed_helos]
    ch53_surviving = [h for h in helo_ids_ch53 if h not in downed_helos]
    # Recalculate effective troops per wave (post-shootdown)
    wave_troops_actual = []
    for w in range(N_WAVES):
        n_mv22_w = sum(1 for h in mv22_surviving if int(h.split('-')[1]) - 1 < N_MV22)
        n_ch53_w = sum(1 for h in ch53_surviving if int(h.split('-')[1]) - 1 < N_CH53)
        troops = n_mv22_w * MV22_TROOPS + n_ch53_w * CH53_TROOPS
        if w == FULL_WAVES:   # last (partial) wave
            troops = min(troops, REMAINDER)
        wave_troops_actual.append(troops)
    total_marines_actual = min(TOTAL_MARINES, sum(wave_troops_actual))
    n_helos_lost = len(downed_helos)
    marines_not_delivered = TOTAL_MARINES - total_marines_actual

    # ── Simulate impacts: apply HP damage to squads ───────────────────────────
    # Only breakthroughs (not intercepted) damage squads.
    # AI drones are guaranteed hits — select nearest squad as instant kill.
    squad_hp     = [SQUAD_HP] * N_SQUADS
    squad_events = [[] for _ in range(N_SQUADS)]   # [(time_s, hp_after)]

    for drone in sorted(all_drones, key=lambda d: d['impact_s']):
        if drone['is_int']:
            continue   # intercepted — no ground effect
        imp_s   = drone['impact_s']
        imp_lon = drone['ai_tgt_lon'] if drone['is_ai'] else drone['imp_lon']
        imp_lat = drone['ai_tgt_lat'] if drone['is_ai'] else drone['imp_lat']
        best_dm, best_si = float('inf'), -1
        for si, (sq_lon, sq_lat, sq_wave) in enumerate(squad_pos):
            if squad_hp[si] <= 0 or wave_arrive_s[sq_wave] > imp_s:
                continue
            dm = _dist_m(imp_lon, imp_lat, sq_lon, sq_lat)
            if drone['is_ai'] and dm < best_dm:
                best_dm, best_si = dm, si
            elif not drone['is_ai']:
                if   dm <= KILL_M:  dmg = squad_hp[si]
                elif dm <= DMG2_M:  dmg = 2
                elif dm <= DMG1_M:  dmg = 1
                else:               continue
                squad_hp[si] = max(0, squad_hp[si] - dmg)
                squad_events[si].append((imp_s, squad_hp[si]))
        if drone['is_ai'] and best_si >= 0:
            squad_hp[best_si] = 0   # guaranteed kill
            squad_events[best_si].append((imp_s, 0))

    # ── Outcome tallies ────────────────────────────────────────────────────────
    n_launched    = len(all_drones)
    n_intercepted = sum(1 for d in all_drones if d['is_int'])
    n_ai          = sum(1 for d in all_drones if d['is_ai'])
    n_bt          = n_launched - n_intercepted
    stinger_fired = sum(1 for d in all_drones if d['stinger_fired'])
    stinger_hits  = n_intercepted
    n_killed      = sum(1 for hp in squad_hp if hp == 0)
    n_damaged     = sum(1 for hp in squad_hp if 0 < hp < SQUAD_HP)
    n_intact      = N_SQUADS - n_killed - n_damaged
    hp_lost       = sum(SQUAD_HP - hp for hp in squad_hp)
    # KIA = fully destroyed squads × squad size; WIA = partial HP losses
    kia_total     = n_killed * MARINES_PER_SQUAD
    wia_total     = hp_lost - kia_total

    # ── Random walk positions for fireteams ────────────────────────────────────
    # Each fireteam moves in small Gaussian steps every 5 min after landing.
    WALK_STEP_S  = 300        # 5-minute walk interval
    WALK_SIGMA_M = 22         # ~22 m sigma per step (≈ infantry tactical bound)
    walk_rng = _random.Random(123)
    squad_walk = []           # squad_walk[si] = [(lon, lat, t_start_s), ...]
    for si, (lon0, lat0, w_idx) in enumerate(squad_pos):
        land_s  = wave_arrive_s[w_idx]
        lon, lat = lon0, lat0
        steps   = []
        t       = land_s
        while t <= SIM_END_S:
            steps.append((lon, lat, t))
            # Small Gaussian step, bounded within Kharg Island
            dlon = walk_rng.gauss(0, WALK_SIGMA_M) / (111_000 * math.cos(math.radians(lat)))
            dlat = walk_rng.gauss(0, WALK_SIGMA_M) / 111_000
            lon  = max(50.282, min(50.365, lon + dlon))
            lat  = max(29.215, min(29.300, lat + dlat))
            t   += WALK_STEP_S
        squad_walk.append(steps)

    # ── Lanchester square-law ground battle simulation ─────────────────────────
    # Marines (F) vs. IRGC defenders (B) beginning when first wave arrives.
    # Square law: dF/dt = -β × B,  dB/dt = -α × F  (α > β: Marines more effective)
    #
    # Historical exchange ratio calibration (enemy KIA per USMC KIA):
    #   - 2nd Battle of Fallujah 2004 (urban assault vs. irregular): 12:1 – 21:1
    #   - Hue City 1968 (urban vs. NVA regulars, similar to IRGC tier): 26:1 southern sector
    #   - Battle of al-Khafji 1991 (USMC vs. Iraqi regulars, defensive posture): 3:1 – 7:1
    #   - Dupuy QJM historical mean (US vs. Middle-Eastern regular military): ~5:1
    #
    # IRGC on Kharg Island are REGULAR infantry (trained), in DEFENSIVE positions,
    # on home terrain → use al-Khafji / Dupuy midpoint: α/β = 5:1.
    # In Lanchester square law the exchange ratio equals (α/β)² × (B₀/F₀) at equal
    # starting numbers, so α/β ≈ 5 gives a ~5:1 attrition coefficient advantage.
    # Sources: Dupuy Institute (2018); RAND MG-1104; Helmbold (1993); Wikipedia
    #          Battle of al-Khafji; Second Battle of Fallujah.
    IRGC_START   = 1_300       # effective IRGC combatants (1000 + 300 weighted Basij)
    USMC_START   = TOTAL_MARINES - kia_total   # surviving Marines after drone strikes
    NAVY_RESERVE = 2_500       # LHA-7 ship's company / ARG Navy personnel, armed as reserve
    # Navy effectiveness: non-infantry, ~2× IRGC (lower than Marines but motivated, armed)
    ALPHA_M      = 1.25e-4     # Marine effectiveness (kills per Marine per second) — 5× IRGC
    ALPHA_N      = 5.0e-5      # Navy reserve effectiveness — 2× IRGC
    BETA_I       = 2.5e-5      # IRGC effectiveness   (kills per IRGC per second)
    #   α/β = 1.25e-4 / 2.5e-5 = 5.0 — calibrated to Dupuy/al-Khafji median
    LANC_STEP_S  = 300         # 5-minute simulation step
    lanc_states  = []          # [(t_s, marines, irgc, navy_active)]
    navy_committed = False     # Navy reserve only enters when Marines are exhausted
    lF, lB       = float(USMC_START), float(IRGC_START)
    lN           = float(NAVY_RESERVE)
    lt           = last_arrive_s   # combat begins once all Marines ashore
    while (lF > 1 or (navy_committed and lN > 1)) and lB > 1:
        lanc_states.append((lt, round(lF), round(lB), navy_committed))
        # If Marines depleted, commit Navy reserve
        if lF < 1 and not navy_committed and lN > 1:
            navy_committed = True
        if navy_committed and lF < 1:
            alpha_eff = ALPHA_N
            fighters  = lN
        else:
            alpha_eff = ALPHA_M
            fighters  = lF
        dF = BETA_I * lB * LANC_STEP_S
        dB = alpha_eff * fighters * LANC_STEP_S
        if navy_committed and lF < 1:
            lN = max(0.0, lN - dF)
        else:
            lF = max(0.0, lF - dF)
        lB = max(0.0, lB - dB)
        lt += LANC_STEP_S
    # Append final (defeated) state
    lanc_states.append((lt, round(lF), round(lB), navy_committed))
    lanc_marine_final = round(lF)
    lanc_navy_final   = round(lN)
    lanc_irgc_final   = round(lB)
    lanc_marine_cas   = USMC_START - lanc_marine_final   # ground combat casualties
    lanc_navy_cas     = (NAVY_RESERVE - lanc_navy_final) if navy_committed else 0
    lanc_irgc_cas     = IRGC_START - lanc_irgc_final

    # ── KML build ─────────────────────────────────────────────────────────────
    kml = []
    kml.append(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2"'
        ' xmlns:gx="http://www.google.com/kml/ext/2.2">\n<Document>\n'
        f'  <name>Kharg Island Assault — {SCENARIO_LABEL}</name>\n'
        '  <description><![CDATA['
        f'<b>Operation: Kharg Island — {SCENARIO_LABEL}</b><br/>'
        f'22nd MEU — {TOTAL_MARINES:,} Marines in {N_WAVES} waves (LHA-7 USS Tripoli)<br/>'
        f'Lift/wave: {TROOPS_PER_WAVE} Marines  |  Cycle: ~{WAVE_CYCLE_S/60:.0f} min  |  All ashore: T+{last_arrive_s/60:.0f} min<br/><br/>'
        f'<b>Shahed-136 counterattack:</b> {n_launched:,} drones / 5 waves | {n_ai} AI-guided | {n_intercepted} intercepted (Stinger Pk={STINGER_PK*100:.0f}%)<br/>'
        f'Kill radius: {KILL_M:.0f} m instant | {DMG2_M:.0f} m −2HP | {DMG1_M:.0f} m −1HP<br/>'
        f'Drone casualties: <b>{kia_total} KIA / {wia_total} WIA</b><br/><br/>'
        f'<b>{N_SQUADS} fireteam icons</b> (4 marines each, random path walk):<br/>'
        '  Green=4HP  Yellow=3HP  Orange=1-2HP  Red=KIA<br/>'
        '<b>Ground battle:</b> Lanchester square-law — Marines 5× more effective than IRGC<br/>'
        f'Navy reserve: {NAVY_RESERVE:,} ship personnel commit if Marines eliminated (2× IRGC effectiveness)'
        + (f'<br/><b style="color:orange">Navy reserve activated — Marines eliminated in ground battle</b>' if navy_committed else '')
        + ']]></description>\n'
    )

    # Styles
    kml.append(
        # Ships / LZ / Iranian positions
        '  <Style id="sty_ship"><IconStyle><color>ff00ffff</color><scale>1.3</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/sailing.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.8</scale></LabelStyle></Style>\n'
        '  <Style id="sty_lz"><IconStyle><color>ff00ff00</color><scale>1.4</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.9</scale></LabelStyle></Style>\n'
        '  <Style id="sty_iran"><IconStyle><color>ff0000ff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.75</scale></LabelStyle></Style>\n'
        '  <Style id="sty_marine"><IconStyle><color>ff00cc44</color><scale>1.4</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/flag.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>1.0</scale></LabelStyle></Style>\n'
        # Sortie counter label
        '  <Style id="sty_counter"><IconStyle><color>ff00ffff</color><scale>1.3</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/info-i.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff00ffff</color><scale>1.1</scale></LabelStyle></Style>\n'
        # Squad HP — gx:Track icons + trail (IconStyle + LineStyle for animated track)
        '  <Style id="sq_full"><IconStyle><color>ff00ee00</color><scale>0.5</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>'
        '</IconStyle><LineStyle><color>aa00ee00</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.0</scale></LabelStyle></Style>\n'
        '  <Style id="sq_lt"><IconStyle><color>ff00eeff</color><scale>0.5</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>'
        '</IconStyle><LineStyle><color>aa00eeff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        '  <Style id="sq_hvy"><IconStyle><color>ff0088ff</color><scale>0.5</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>'
        '</IconStyle><LineStyle><color>aa0088ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        '  <Style id="sq_kia"><IconStyle><color>ff0000ff</color><scale>0.45</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>'
        '</IconStyle><LineStyle><color>aa0000ff</color><width>1</width></LineStyle>'
        '<LabelStyle><scale>0.45</scale></LabelStyle></Style>\n'
        # Drone track + impact
        '  <Style id="trk_drone"><LineStyle><color>cc4444ff</color><width>1</width></LineStyle></Style>\n'
        '  <Style id="sty_boom"><IconStyle><color>ff0000ff</color><scale>1.0</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.4</scale></LabelStyle></Style>\n'
        # ── Helicopter gx:Track styles (combined icon + trail for animated altitude arcs) ─
        # MV-22B Osprey — orange icon + orange trail
        '  <Style id="helo_mv22"><IconStyle><color>ff0077ff</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>cc0077ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        # CH-53E Super Stallion — sky blue
        '  <Style id="helo_ch53"><IconStyle><color>ffff8800</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>ccff8800</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        # AH-1Z Viper — red
        '  <Style id="helo_ah1z"><IconStyle><color>ff2222ff</color><scale>0.8</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>cc2222ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.45</scale></LabelStyle></Style>\n'
        # Return legs — faded grey
        '  <Style id="helo_ret"><IconStyle><color>55aaaaaa</color><scale>0.7</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>44aaaaaa</color><width>1</width></LineStyle>'
        '<LabelStyle><scale>0.0</scale></LabelStyle></Style>\n'
        # Legacy LineString styles (kept for backward compat; unused by helo gx:Tracks)
        '  <Style id="trk_mv22"><LineStyle><color>cc0055ff</color><width>2</width></LineStyle></Style>\n'
        '  <Style id="trk_ch53"><LineStyle><color>cc004488</color><width>2</width></LineStyle></Style>\n'
        '  <Style id="trk_ah1z"><LineStyle><color>bb0000cc</color><width>1</width></LineStyle></Style>\n'
        '  <Style id="trk_ret"><LineStyle><color>55aaaaaa</color><width>1</width></LineStyle></Style>\n'
        '  <Style id="ico_mv22"><IconStyle><color>ff0077ff</color><scale>0.75</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        '  <Style id="ico_ch53"><IconStyle><color>ffff8800</color><scale>0.75</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        '  <Style id="ico_ah1z"><IconStyle><color>ff2222ff</color><scale>0.7</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        # ── IRGC soldier + MANPADS icons ─────────────────────────────────────────
        # IRGC infantry — dark red man icon
        '  <Style id="ico_irgc"><IconStyle><color>ff0000bb</color><scale>0.45</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.0</scale></LabelStyle></Style>\n'
        # IRGC MANPADS team — bright red target icon
        '  <Style id="ico_irgc_mp"><IconStyle><color>ff0000ff</color><scale>0.75</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.5</scale></LabelStyle></Style>\n'
        # ── WEZ / engagement zone circle styles ──────────────────────────────────
        # IRGC MANPADS WEZ — red outline, faint red fill
        '  <Style id="wez_irgc_mp"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle>'
        '<PolyStyle><color>220000ff</color><fill>1</fill></PolyStyle></Style>\n'
        # USMC Stinger WEZ — cyan outline, faint cyan fill
        '  <Style id="wez_usmc_stg"><LineStyle><color>ffff8800</color><width>2</width></LineStyle>'
        '<PolyStyle><color>22ff8800</color><fill>1</fill></PolyStyle></Style>\n'
        # ── Drone gx:Track + marker styles — mirrors CSG scenario styling exactly ─
        # ICON_MUNITION = open-diamond (same as generate_style section in main scenarios)
        # Standard Shahed breakthrough — orange, open-diamond, width 2
        '  <Style id="kharg_shahed"><IconStyle><color>ff0080ff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href></Icon>'
        '</IconStyle><LineStyle><color>cc0080ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0.0</scale></LabelStyle></Style>\n'
        # AI approach phase — same as shahed_ai_approach in main scenarios
        '  <Style id="kharg_shahed_ai_approach"><IconStyle><color>ff0080ff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href></Icon>'
        '</IconStyle><LineStyle><color>ff0080ff</color><width>3</width></LineStyle>'
        '<LabelStyle><scale>0.6</scale></LabelStyle></Style>\n'
        # AI terminal lock-on phase — same as shahed_ai_terminal in main scenarios
        '  <Style id="kharg_shahed_ai_terminal"><IconStyle><color>ff00a0ff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href></Icon>'
        '</IconStyle><LineStyle><color>ff00a0ff</color><width>4</width></LineStyle>'
        '<LabelStyle><scale>0.6</scale></LabelStyle></Style>\n'
        # Stinger intercept flash — same as intercept_marker / intercept_marker_white
        '  <Style id="kharg_intercept_mk"><IconStyle><color>ff000000</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff000000</color><scale>0.6</scale></LabelStyle></Style>\n'
        '  <Style id="kharg_intercept_wh"><IconStyle><color>ffffffff</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ffffffff</color><scale>0.6</scale></LabelStyle></Style>\n'
        # Breakthrough impact — same as impact_marker (red target, scale 1.3)
        '  <Style id="kharg_impact"><IconStyle><color>ff0000ff</color><scale>1.3</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff0000ff</color><scale>0.9</scale></LabelStyle></Style>\n'
        # ── Squad walk path LineStyles (colour = AABBGGRR) ──────────────────────
        '  <Style id="sq_full_path"><LineStyle><color>ff00ee00</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0</scale></LabelStyle></Style>\n'   # green
        '  <Style id="sq_lt_path"><LineStyle><color>ff00eeff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0</scale></LabelStyle></Style>\n'   # yellow
        '  <Style id="sq_hvy_path"><LineStyle><color>ff0088ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0</scale></LabelStyle></Style>\n'   # orange
        '  <Style id="sq_kia_path"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle>'
        '<LabelStyle><scale>0</scale></LabelStyle></Style>\n'   # red
        # Lanchester ground battle timeline label
        '  <Style id="sty_battle"><IconStyle><color>ff00ff88</color><scale>1.0</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/info-i.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff00ff88</color><scale>0.85</scale></LabelStyle></Style>\n'
        # Misagh-2 missile track — orange-red (AABBGGRR: ff=opaque, 00=B, 55=G, ff=R)
        '  <Style id="ico_misagh2"><IconStyle><color>ff0055ff</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>cc0055ff</color><width>2</width></LineStyle>'
        '<LabelStyle><color>ff0055ff</color><scale>0.7</scale></LabelStyle></Style>\n'
        # Misagh-2 miss — grey (semi-transparent track, no label)
        '  <Style id="ico_misagh2_miss"><IconStyle><color>88888888</color><scale>0.6</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LineStyle><color>44888888</color><width>1</width></LineStyle>'
        '<LabelStyle><scale>0</scale></LabelStyle></Style>\n'
        # Downed helicopter — red square
        '  <Style id="ico_helo_down"><IconStyle><color>ff0000ff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff0000ff</color><scale>0.7</scale></LabelStyle></Style>\n'
        # ── F-35B Strike Package styles ──────────────────────────────────────────
        # F-35B aircraft track — medium blue (AABBGGRR: ff=opaque, ff=B, 88=G, 00=R)
        '  <Style id="helo_f35b"><IconStyle><color>ffff8800</color><scale>1.25</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ffff8800</color><scale>0.8</scale></LabelStyle>'
        '<LineStyle><color>88ff8800</color><width>2</width></LineStyle></Style>\n'
        # AGM-88E AARGM impact — bright red target (SEAD)
        '  <Style id="f35b_agm88_impact"><IconStyle><color>ff0000ff</color><scale>1.3</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff0000ff</color><scale>0.85</scale></LabelStyle></Style>\n'
        # GBU-38 JDAM impact — amber/gold target (CAS precision strike)
        # AABBGGRR: ff=opaque, 00=B, aa=G, ff=R → RGB(255,170,0) = amber
        '  <Style id="f35b_jdam_impact"><IconStyle><color>ff00aaff</color><scale>1.1</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>'
        '</IconStyle><LabelStyle><color>ff00aaff</color><scale>0.75</scale></LabelStyle></Style>\n'
    )

    # ── Amphibious Ready Group ships ──────────────────────────────────────────
    kml.append('  <Folder><name>Amphibious Ready Group</name>\n')
    for lon, lat, name, desc in [
        (LHA_LON,  LHA_LAT,  "LHA-7 USS Tripoli",
         "America-class LHA (Flight 0, no well deck) — 44,971 t<br/>"
         "Commissioned: 15 Jul 2020 | Aviation-centric<br/>"
         "Air wing: 12 MV-22B + 4 CH-53E + 4 AH-1Z + 20 F-35B<br/>"
         "F-35B loadout: 4× SEAD (AGM-88E AARGM) + 16× CAS (GBU-38 JDAM beast mode)"),
        (LPD1_LON, LPD1_LAT, "LPD-30 USS Harrisburg",
         "San Antonio-class LPD — 25,900 t<br/>Well deck: 2 LCAC or 14 LCM-8"),
        (LPD2_LON, LPD2_LAT, "LPD-29 USS Richard M. McCool Jr.",
         "San Antonio-class LPD — 25,900 t<br/>Well deck: 2 LCAC or 14 LCM-8"),
        (DDG_LON,  DDG_LAT,  "DDG-123 USS Ted Stevens (escort)",
         "Arleigh Burke Flight III — NGFS + AAW<br/>5\"/62 Mk45 + SM-6 / SM-2 / ESSM"),
    ]:
        kml.append(_pm_point(name, lon, lat, "sty_ship", desc))
    kml.append('  </Folder>\n')

    # ── Kharg Island features ──────────────────────────────────────────────────
    kml.append('  <Folder><name>Kharg Island</name>\n')
    outline_pts = [
        (50.295,29.220),(50.310,29.215),(50.335,29.215),(50.350,29.225),
        (50.362,29.240),(50.364,29.258),(50.358,29.272),(50.348,29.286),
        (50.332,29.298),(50.315,29.300),(50.300,29.294),(50.288,29.282),
        (50.282,29.267),(50.282,29.252),(50.287,29.238),(50.295,29.220),
    ]
    coord_str = " ".join(f"{lo:.6f},{la:.6f},0" for lo, la in outline_pts)
    kml.append(
        f'  <Placemark><name>Kharg Island</name>'
        f'<Style><LineStyle><color>ff00ffff</color><width>2</width></LineStyle>'
        f'<PolyStyle><color>22ff6600</color><fill>1</fill></PolyStyle></Style>'
        f'<Polygon><outerBoundaryIs><LinearRing>'
        f'<coordinates>{coord_str}</coordinates>'
        f'</LinearRing></outerBoundaryIs></Polygon></Placemark>\n'
    )
    for lon, lat, name, style, desc in [
        (50.3285, 29.2605, "IRGC Garrison HQ", "sty_iran",
         "~1,000 IRGC infantry + ~500 Basij | hardened command bunkers"),
        (50.330,  29.280,  "HQ-2/HAWK SAM Battery", "sty_iran",
         "40 km slant range | effective vs. high/slow targets"),
        (50.310,  29.245,  "ZSU-23-4 Shilka #1", "sty_iran",
         "23mm quad-barrel | 4,000 rds/min | 2,500 m ceiling"),
        (50.346,  29.265,  "ZSU-23-4 Shilka #2", "sty_iran",
         "Eastern approach corridor coverage"),
        (50.320,  29.230,  "MANPADS Screen (Misagh-2)", "sty_iran",
         "~20× IR-guided | 5 km range | 4 km ceiling"),
        (50.305,  29.278,  "Oil Terminal T-1", "sty_ship",
         "90% of Iranian crude exports | ROE: do not damage"),
        (LZ1_LON, LZ1_LAT, "LZ FALCON — Airstrip (2,300 m)", "sty_lz",
         "Primary LZ & seizure objective | enables C-130 resupply post-D-Day"),
        (LZ2_LON, LZ2_LAT, "LZ EAGLE — Central Plateau", "sty_lz",
         "Secondary LZ | waves 3-5 alternated here to reduce congestion"),
    ]:
        kml.append(_pm_point(name, lon, lat, style, desc))
    kml.append('  </Folder>\n')

    # ── IRGC Defensive Positions ──────────────────────────────────────────────
    # 1,000 soldiers static across island; 10% MANPADS with individual WEZ circles.
    kml.append(f'  <Folder><name>IRGC Defenders ({N_IRGC:,} soldiers, {N_IRGC_MP} MANPADS)</name>\n')

    # Infantry (900) — static icons, 15% sampled for GE performance
    IRGC_INF_SAMPLE = 0.15
    _irgc_vis_rng = _random.Random(61)
    kml.append(f'  <Folder><name>Infantry ({N_IRGC - N_IRGC_MP:,} soldiers — {int(IRGC_INF_SAMPLE*100)}% shown)</name>\n')
    for _lon, _lat, _has_mp in irgc_pos:
        if _has_mp:
            continue
        if _irgc_vis_rng.random() > IRGC_INF_SAMPLE:
            continue
        kml.append(_pm_point("IRGC", _lon, _lat, "ico_irgc",
                              "IRGC infantry defender<br/>Small arms / RPG"))
    kml.append('  </Folder>\n')

    # MANPADS teams (100) — all shown, each with WEZ circle
    kml.append(f'  <Folder><name>IRGC MANPADS Teams ({N_IRGC_MP} × Misagh-2, range {IRGC_MP_RNG_KM:.1f} km)</name>\n')
    _mp_idx = 0
    for _lon, _lat, _has_mp in irgc_pos:
        if not _has_mp:
            continue
        _mp_idx += 1
        kml.append(_pm_point(f"IRGC MANPADS #{_mp_idx}", _lon, _lat, "ico_irgc_mp",
                              f"IRGC MANPADS team #{_mp_idx}<br/>"
                              f"Weapon: Misagh-2 (IR MANPADS, Stinger clone)<br/>"
                              f"Max range: {IRGC_MP_RNG_KM:.1f} km | Max alt: 3,800 m<br/>"
                              f"Pk vs. unalerted helicopter: 0.15–0.25<br/>"
                              f"<b>WEZ circle: {IRGC_MP_RNG_KM:.1f} km radius</b>"))
        _circ = _circle_kml_pts(_lon, _lat, IRGC_MP_RNG_KM)
        kml.append(
            f'  <Placemark><name>MANPADS WEZ #{_mp_idx}</name>'
            f'<description><![CDATA[Misagh-2 engagement envelope — {IRGC_MP_RNG_KM:.1f} km radius]]></description>'
            f'<styleUrl>#wez_irgc_mp</styleUrl>'
            f'<Polygon><outerBoundaryIs><LinearRing>'
            f'<coordinates>{_circ}</coordinates>'
            f'</LinearRing></outerBoundaryIs></Polygon></Placemark>\n'
        )
    kml.append('  </Folder>\n')
    kml.append('  </Folder>\n')

    # ── USMC Stinger MANPADS WEZ ──────────────────────────────────────────────
    # Teams deploy at LZs immediately on landing; one advance position after wave 3.
    kml.append(f'  <Folder><name>USMC Stinger WEZ ({STINGER_MAG} rounds, Pk={STINGER_PK*100:.0f}%, range {STINGER_RNG:.1f} km)</name>\n')
    _stg_positions = [
        (LZ1_LON, LZ1_LAT,  wave_arrive_s[0], "Stinger Team Alpha (LZ-1 primary)"),
        (LZ2_LON, LZ2_LAT,  wave_arrive_s[2], "Stinger Team Bravo (LZ-2 secondary)"),
        # Advance position after wave 5 consolidates centre
        (KHARG_LON - 0.005, KHARG_LAT - 0.012, wave_arrive_s[4], "Stinger Team Charlie (island centre advance)"),
    ]
    for _slon, _slat, _active_s, _lbl in _stg_positions:
        kml.append(_pm_point(_lbl, _slon, _slat, "ico_irgc_mp",
                             f"USMC FIM-92 Stinger MANPADS team<br/>"
                             f"Effective range: {STINGER_RNG:.1f} km | Pk={STINGER_PK*100:.0f}%<br/>"
                             f"Magazine: {STINGER_MAG} rounds (shared pool)<br/>"
                             f"Active from T+{_active_s/60:.0f} min",
                             _active_s, SIM_END_S))
        _circ = _circle_kml_pts(_slon, _slat, STINGER_RNG)
        kml.append(
            f'  <Placemark><name>{_lbl} WEZ</name>'
            f'<description><![CDATA[FIM-92 Stinger max engagement envelope — {STINGER_RNG:.1f} km radius]]></description>'
            f'<styleUrl>#wez_usmc_stg</styleUrl>'
            f'{_tspan(_active_s, SIM_END_S)}'
            f'<Polygon><outerBoundaryIs><LinearRing>'
            f'<coordinates>{_circ}</coordinates>'
            f'</LinearRing></outerBoundaryIs></Polygon></Placemark>\n'
        )
    kml.append('  </Folder>\n')

    # ── Helicopter waves (animated back-and-forth sorties) ─────────────────────
    kml.append('  <Folder><name>Helicopter Waves</name>\n')
    wave_arrivals = []
    total_ashore  = 0
    for w in range(N_WAVES):
        wave_num     = w + 1
        wave_start_s = wave_depart_s[w]
        arrive_lz_s  = wave_arrive_s[w]
        depart_lz_s  = arrive_lz_s + UNLOAD_S
        return_s     = wave_return_s[w]

        if w < FULL_WAVES:
            wave_marines = TROOPS_PER_WAVE
            n_mv22_w, n_ch53_w = N_MV22, N_CH53
        else:
            wave_marines = REMAINDER
            n_mv22_w = max(1, round(N_MV22 * REMAINDER / TROOPS_PER_WAVE))
            n_ch53_w = max(1, round(N_CH53 * REMAINDER / TROOPS_PER_WAVE))

        total_ashore += wave_marines
        tlon = LZ1_LON if w % 2 == 0 else LZ2_LON
        tlat = LZ1_LAT if w % 2 == 0 else LZ2_LAT
        lz_nm = "LZ FALCON" if w % 2 == 0 else "LZ EAGLE"
        wave_arrivals.append((arrive_lz_s, total_ashore, wave_num, wave_marines, lz_nm))

        kml.append(f'  <Folder><name>Wave {wave_num}  T+{wave_start_s/60:.0f}min'
                   f' — {wave_marines} Marines → {lz_nm}</name>\n')

        for i in range(n_mv22_w):
            slon, slat = _ship_offset(i, n_mv22_w, LHA_LON, LHA_LAT, 0.007)
            stag = i * 20
            dep_s = wave_start_s + stag
            arr_s = dep_s + T_MV22
            dpt_s = arr_s + UNLOAD_S
            ret_s = dpt_s + T_MV22
            # Outbound: 150 m cruise (NOE sea-skim) — gx:Track animates icon along arc
            _out_pts = _helo_arc_pts(slon, slat, tlon, tlat, 150)
            _out_ts  = [dep_s + (arr_s - dep_s) * k / (len(_out_pts) - 1)
                        for k in range(len(_out_pts))]
            kml.extend(gx_track("helo_mv22", _out_pts, _out_ts,
                                 f"MV-22B #{i+1} W{wave_num}",
                                 f"MV-22B Osprey #{i+1} | Wave {wave_num}<br/>"
                                 f"Troops: {MV22_TROOPS} | Speed: {MV22_KMH} km/h<br/>"
                                 f"Cruise altitude: 150 m AGL (NOE) | Departs T+{dep_s/60:.0f} min",
                                 altitude_mode="relativeToGround"))
            _ret_pts = _helo_arc_pts(tlon, tlat, slon, slat, 150)
            _ret_ts  = [dpt_s + (ret_s - dpt_s) * k / (len(_ret_pts) - 1)
                        for k in range(len(_ret_pts))]
            kml.extend(gx_track("helo_ret", _ret_pts, _ret_ts,
                                 f"MV-22B #{i+1} W{wave_num} RTN", "",
                                 altitude_mode="relativeToGround"))

        ch53_src = [(LHA_LON,LHA_LAT),(LHA_LON,LHA_LAT),(LPD1_LON,LPD1_LAT),(LPD2_LON,LPD2_LAT)]
        for i in range(n_ch53_w):
            blon, blat = ch53_src[i % len(ch53_src)]
            slon, slat = _ship_offset(i, n_ch53_w, blon, blat, 0.005)
            stag = i * 30
            dep_s = wave_start_s + stag
            arr_s = dep_s + _flt_s(slon, slat, LZ1_LON, LZ1_LAT, CH53_KMH)
            dpt_s = arr_s + UNLOAD_S + 60
            ret_s = dpt_s + _flt_s(LZ1_LON, LZ1_LAT, slon, slat, CH53_KMH)
            # Outbound: 120 m cruise (CH-53E NOE, heavier/slower than Osprey)
            _out_pts = _helo_arc_pts(slon, slat, LZ1_LON, LZ1_LAT, 120)
            _out_ts  = [dep_s + (arr_s - dep_s) * k / (len(_out_pts) - 1)
                        for k in range(len(_out_pts))]
            kml.extend(gx_track("helo_ch53", _out_pts, _out_ts,
                                 f"CH-53E #{i+1} W{wave_num}",
                                 f"CH-53E Super Stallion #{i+1} | Wave {wave_num}<br/>"
                                 f"Troops: {CH53_TROOPS} | Speed: {CH53_KMH} km/h<br/>"
                                 f"Cruise altitude: 120 m AGL | Departs T+{dep_s/60:.0f} min",
                                 altitude_mode="relativeToGround"))
            _ret_pts = _helo_arc_pts(LZ1_LON, LZ1_LAT, slon, slat, 120)
            _ret_ts  = [dpt_s + (ret_s - dpt_s) * k / (len(_ret_pts) - 1)
                        for k in range(len(_ret_pts))]
            kml.extend(gx_track("helo_ret", _ret_pts, _ret_ts,
                                 f"CH-53E #{i+1} W{wave_num} RTN", "",
                                 altitude_mode="relativeToGround"))

        for i in range(N_AH1Z):
            slon, slat = _ship_offset(i, N_AH1Z, DDG_LON, DDG_LAT, 0.004)
            arr_esc = wave_start_s + T_AH1Z - 60
            end_esc = depart_lz_s + 120
            ret_esc = end_esc + _flt_s(LZ1_LON, LZ1_LAT, DDG_LON, DDG_LAT, AH1Z_KMH)
            # Inbound: 80 m cruise (CAS escort — lower for threat identification)
            _in_pts = _helo_arc_pts(slon, slat, LZ1_LON, LZ1_LAT, 80)
            _in_ts  = [wave_start_s + (arr_esc - wave_start_s) * k / (len(_in_pts) - 1)
                       for k in range(len(_in_pts))]
            kml.extend(gx_track("helo_ah1z", _in_pts, _in_ts,
                                 f"AH-1Z #{i+1} W{wave_num}",
                                 f"AH-1Z Viper #{i+1} | Wave {wave_num} CAS escort<br/>"
                                 f"Speed: {AH1Z_KMH} km/h | Cruise altitude: 80 m AGL<br/>"
                                 f"Role: fire suppression + close air support",
                                 altitude_mode="relativeToGround"))
            _out_pts = _helo_arc_pts(LZ1_LON, LZ1_LAT, slon, slat, 80)
            _out_ts  = [end_esc + (ret_esc - end_esc) * k / (len(_out_pts) - 1)
                        for k in range(len(_out_pts))]
            kml.extend(gx_track("helo_ret", _out_pts, _out_ts,
                                 f"AH-1Z #{i+1} W{wave_num} RTN", "",
                                 altitude_mode="relativeToGround"))

        kml.append('  </Folder>\n')
    kml.append('  </Folder>\n')

    # ── Sortie counter — trips completed / remaining, updates with timeline ────
    kml.append('  <Folder><name>Sortie Counter</name>\n'
               '  <!-- One placemark per completed wave-return; '
               'active during the window until the next return -->\n')
    for w in range(N_WAVES):
        ret_s      = wave_return_s[w]
        next_ret_s = wave_return_s[w + 1] if w + 1 < N_WAVES else SIM_END_S
        trips_done = w + 1
        remaining  = N_WAVES - trips_done
        n_mv22_w   = N_MV22 if w < FULL_WAVES else max(1, round(N_MV22 * REMAINDER / TROOPS_PER_WAVE))
        n_ch53_w   = N_CH53 if w < FULL_WAVES else max(1, round(N_CH53 * REMAINDER / TROOPS_PER_WAVE))
        kml.append(
            f'  <Placemark>'
            f'<name>Sorties: {trips_done}/{N_WAVES} complete — {remaining} remaining</name>'
            f'<description><![CDATA['
            f'<b>Sortie {trips_done} of {N_WAVES} complete</b> at T+{ret_s/60:.0f} min<br/>'
            f'Marines ashore: <b>{wave_arrivals[w][1]:,}</b> / {TOTAL_MARINES:,}<br/>'
            f'Trips remaining: <b>{remaining}</b><br/>'
            f'MV-22B round trips this wave: {n_mv22_w}  (cumulative: {trips_done * n_mv22_w})<br/>'
            f'CH-53E round trips this wave: {n_ch53_w}  (cumulative: {trips_done * n_ch53_w})'
            f']]></description>'
            f'<styleUrl>#sty_counter</styleUrl>'
            f'{_tspan(ret_s, next_ret_s)}'
            f'<Point><coordinates>{LHA_LON + 0.010:.6f},{LHA_LAT + 0.010:.6f},0</coordinates>'
            f'</Point></Placemark>\n'
        )
    kml.append('  </Folder>\n')

    # ── Helicopter shootdown events ────────────────────────────────────────────
    kml.append(f'  <Folder><name>Helicopter Losses ({n_helos_lost} aircraft downed)</name>\n'
               f'  <!-- AI drone proximity kills — 50% Pk within {HELO_KILL_KM:.1f} km -->\n')
    for helo_id, helo_type, helo_wave, kill_t, drone_wave in helo_kill_events:
        # Place marker near the flight path midpoint
        tlon_h = LZ1_LON if helo_wave % 2 == 0 else LZ2_LON
        tlat_h = LZ1_LAT if helo_wave % 2 == 0 else LZ2_LAT
        mk_lon = (LHA_LON + tlon_h) / 2 + helo_rng.uniform(-0.015, 0.015)
        mk_lat = (LHA_LAT + tlat_h) / 2 + helo_rng.uniform(-0.008, 0.008)
        kml.append(
            f'  <Placemark><name>SHOT DOWN: {helo_type} ({helo_id})</name>'
            f'<description><![CDATA['
            f'<b style="color:red">{helo_type} {helo_id} — SHOT DOWN</b><br/>'
            f'Wave {helo_wave + 1} outbound sortie terminated<br/>'
            f'Kill time: T+{kill_t/60:.1f} min<br/>'
            f'Cause: AI-guided Shahed-136 wave {drone_wave} (proximity kill)<br/>'
            f'<b>All subsequent sorties for this aircraft cancelled</b>'
            f']]></description>'
            f'<styleUrl>#ico_helo_down</styleUrl>'
            f'<TimeStamp><when>{_ts(kill_t)}</when></TimeStamp>'
            f'<Point><coordinates>{mk_lon:.6f},{mk_lat:.6f},400</coordinates>'
            f'</Point></Placemark>\n'
        )
    if not helo_kill_events:
        kml.append('  <!-- No helicopter losses this simulation run -->\n')
    kml.append('  </Folder>\n')

    # ── IRGC Misagh-2 MANPADS engagements ─────────────────────────────────────
    # Each entry: animated missile arc (gx:Track) + hit marker if kill.
    # Hit  → orange-red track (#ico_misagh2), red helo-down icon
    # Miss → grey translucent track (#ico_misagh2_miss)
    kml.append(
        f'  <Folder><name>IRGC Misagh-2 MANPADS — {misagh_shots} shots / '
        f'{misagh_hits} kills / {misagh_misses} misses</name>\n'
        f'  <!-- {int(100 * MISAGH_SEAD_SURV)}% of teams survive F-35B SEAD; '
        f'Pk MV-22B={MISAGH_PK_TYPE["MV-22B"]:.0%} '
        f'CH-53E={MISAGH_PK_TYPE["CH-53E"]:.0%} '
        f'AH-1Z={MISAGH_PK_TYPE["AH-1Z"]:.0%} -->\n'
    )
    for ev in misagh_events:
        sty  = 'ico_misagh2' if ev['hit'] else 'ico_misagh2_miss'
        tag  = 'HIT' if ev['hit'] else 'MISS'
        # IR pursuit arc: launch from ground → helo altitude (~150 m cruise)
        # Use _helo_arc_pts with 300 m peak to give the missile a visible arc
        _msl_pts = _helo_arc_pts(ev['mp_lon'], ev['mp_lat'],
                                  ev['h_lon'],  ev['h_lat'], 300, n_pts=8)
        _msl_ts  = [ev['eng_t'] + (ev['kill_t'] - ev['eng_t']) * k / (len(_msl_pts) - 1)
                    for k in range(len(_msl_pts))]
        kml.extend(gx_track(
            sty, _msl_pts, _msl_ts,
            f"Misagh-2 [{tag}] → {ev['helo_id']} W{ev['wave']+1}",
            f"<![CDATA[<b>Misagh-2 MANPADS — {tag}</b><br/>"
            f"Target: {ev['helo_type']} {ev['helo_id']}<br/>"
            f"Wave: {ev['wave']+1}<br/>"
            f"Range: {ev['dist_km']:.1f} km<br/>"
            f"Launch T{ev['eng_t']/60:+.1f} min | Impact T{ev['kill_t']/60:+.1f} min<br/>"
            + ('<b style="color:red">AIRCRAFT DESTROYED</b>' if ev['hit'] else 'Evaded / flares / miss') + "]]>",
            altitude_mode="relativeToGround"
        ))
        if ev['hit']:
            kml.append(
                f'  <Placemark><name>SHOT DOWN: {ev["helo_type"]} {ev["helo_id"]} [Misagh-2]</name>'
                f'<description><![CDATA['
                f'<b style="color:red">{ev["helo_type"]} {ev["helo_id"]} — DESTROYED by Misagh-2</b><br/>'
                f'Wave {ev["wave"] + 1} outbound sortie terminated<br/>'
                f'Kill time: T{ev["kill_t"]/60:.1f} min<br/>'
                f'Cause: IRGC Misagh-2 MANPADS (IR-guided)<br/>'
                f'Range at intercept: {ev["dist_km"]:.1f} km<br/>'
                f'<b>All subsequent sorties for this aircraft cancelled</b>'
                f']]></description>'
                f'<styleUrl>#ico_helo_down</styleUrl>'
                f'<TimeStamp><when>{_ts(ev["kill_t"])}</when></TimeStamp>'
                f'<Point><coordinates>{ev["h_lon"]:.6f},{ev["h_lat"]:.6f},150</coordinates>'
                f'</Point></Placemark>\n'
            )
    if not misagh_events:
        kml.append('  <!-- All MANPADS neutralised by SEAD — no engagements -->\n')
    kml.append('  </Folder>\n')

    # ── F-35B Lightning II Strike Package ─────────────────────────────────────
    # SEAD wave: 4 aircraft carry 2× AGM-88E AARGM each → 8 anti-radiation missiles
    #   against HQ-2/HAWK SAM, 2× ZSU-23-4 Shilka, and MANPADS screen.
    #   Fire from standoff (~36 km south), well outside HAWK 40 km slant envelope.
    # CAS waves: 16 aircraft × 2 sorties × 4× GBU-38 JDAM = 128 precision bombs.
    #   Each bomb is a separate targetable placemark (CEP 3 m GPS/INS).
    #   Targets: IRGC HQ, command nodes, infantry concentrations, vehicle parks.
    f35b_rng = _random.Random(67)

    # Timing
    # SEAD: depart 10 min before helo wave 1 so AGM-88s land ~5 min before helos
    F35B_SEAD_DEP_S  = wave_depart_s[0] - 600.0
    # CAS sortie 1: depart so aircraft arrive just before first helo wave lands
    F35B_CAS1_DEP_S  = wave_arrive_s[0] - T_F35B - 120.0
    # CAS sortie 2: after all aircraft return, rearm, and redeploy
    F35B_CAS1_RTN_S  = F35B_CAS1_DEP_S + T_F35B + GBU38_PER_CAS * 30 + 60 + T_F35B
    F35B_CAS2_DEP_S  = F35B_CAS1_RTN_S + F35B_REARM_S

    # AGM-88E flight speed for transit computation
    AGM88_SPD_KS = AGM88_KMH / 3_600.0

    # SEAD strike targets (one per aircraft; 2 missiles each)
    SEAD_TARGETS = [
        (50.330, 29.280, "HQ-2/HAWK SAM Battery"),
        (50.310, 29.245, "ZSU-23-4 Shilka #1"),
        (50.346, 29.265, "ZSU-23-4 Shilka #2"),
        (50.320, 29.230, "MANPADS Screen (Misagh-2)"),
    ]

    # CAS target pool — priority nodes first, then sampled IRGC positions
    CAS_PRIO = [
        (50.3285, 29.2605, "IRGC Garrison HQ — command bunker"),
        (50.330,  29.280,  "HAWK SAM battery (follow-on strike)"),
        (50.310,  29.245,  "ZSU-23-4 Shilka #1 (follow-on)"),
        (50.346,  29.265,  "ZSU-23-4 Shilka #2 (follow-on)"),
        (50.320,  29.230,  "MANPADS screen (follow-on)"),
        (50.308,  29.275,  "Oil terminal perimeter — IRGC fighting position"),
        (50.322,  29.250,  "IRGC ammunition cache (estimated)"),
        (50.328,  29.238,  "IRGC motor pool / vehicle concentration"),
        (50.340,  29.255,  "IRGC mortar position (estimated)"),
        (50.318,  29.262,  "IRGC command post — northern sector"),
    ]
    _cas_tgt_pool = list(CAS_PRIO)
    for _ii_c, (_lon_c, _lat_c, _hmp_c) in enumerate(irgc_pos):
        if _ii_c % 4 == 0:   # every 4th IRGC soldier position
            _cas_tgt_pool.append((_lon_c, _lat_c, "IRGC infantry concentration"))

    _cas_tgt_idx   = 0
    _agm88_seq     = 0    # global AGM-88 weapon serial
    _gbu38_seq     = 0    # global GBU-38 weapon serial
    f35b_agm88_hits = 0
    f35b_jdam_hits  = 0

    kml.append(
        f'  <Folder><name>F-35B Strike Package — {N_F35B} aircraft</name>\n'
        f'  <!-- SEAD: {N_F35B_SEAD}× F-35B, {N_F35B_SEAD*AGM88_PER_SEAD}× AGM-88E AARGM '
        f'(150+ km range, Mach 2 terminal, passive-radar + IIR guidance) -->\n'
        f'  <!-- CAS: {N_F35B_CAS}× F-35B, {F35B_SORTIES} sorties, '
        f'{N_F35B_CAS*GBU38_PER_CAS*F35B_SORTIES}× GBU-38 JDAM (500 lb, CEP {F35B_CEP_M:.0f} m) -->\n'
    )

    # ── SEAD wave ─────────────────────────────────────────────────────────────
    kml.append(
        f'  <Folder><name>SEAD Wave — {N_F35B_SEAD}× F-35B / '
        f'{N_F35B_SEAD*AGM88_PER_SEAD}× AGM-88E AARGM</name>\n'
        f'  <!-- Suppress HQ-2/HAWK SAM + ZSU-23-4 × 2 + MANPADS '
        f'before first helo wave arrives -->\n'
    )
    for si in range(N_F35B_SEAD):
        tgt_lon, tgt_lat, tgt_name = SEAD_TARGETS[si]
        slon, slat = _ship_offset(si, N_F35B_SEAD, LHA_LON, LHA_LAT, 0.006)
        dep_s  = F35B_SEAD_DEP_S + si * 30.0
        fire_t = dep_s + T_F35B_TO_FIRE
        ret_dep_s = fire_t + 120.0   # 2 min loiter at fire point
        ret_s  = ret_dep_s + _flt_s(F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT,
                                     slon, slat, F35B_KMH)
        # Outbound to standoff fire point
        _sead_out = _jet_arc_pts(slon, slat,
                                  F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT, F35B_ALT_M)
        _sead_out_ts = [dep_s + (fire_t - dep_s) * k / (len(_sead_out) - 1)
                        for k in range(len(_sead_out))]
        kml.extend(gx_track(
            "helo_f35b", _sead_out, _sead_out_ts,
            f"F-35B SEAD #{si+1}",
            f"<![CDATA[<b>F-35B Lightning II — SEAD #{si+1}</b><br/>"
            f"Role: Suppression of Enemy Air Defenses (SEAD)<br/>"
            f"Loadout: {AGM88_PER_SEAD}× AGM-88E AARGM + {AIM120_PER_F35B}× AIM-120C-7<br/>"
            f"Target: <b>{tgt_name}</b><br/>"
            f"Fire point: {_dist_km(LHA_LON, LHA_LAT, F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT):.0f} km "
            f"from LHA-7 (standoff — outside HAWK WEZ)<br/>"
            f"Cruise: {F35B_KMH} km/h at {F35B_ALT_M:,} m AGL<br/>"
            f"Departs: T{dep_s/60:+.1f} min]]>",
            altitude_mode="relativeToGround"
        ))
        # Return leg
        _sead_ret = _jet_arc_pts(F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT,
                                  slon, slat, F35B_ALT_M)
        _sead_ret_ts = [ret_dep_s + (ret_s - ret_dep_s) * k / (len(_sead_ret) - 1)
                        for k in range(len(_sead_ret))]
        kml.extend(gx_track("helo_ret", _sead_ret, _sead_ret_ts,
                             f"F-35B SEAD #{si+1} RTN", "",
                             altitude_mode="relativeToGround"))
        # AGM-88E individual weapon placemarks (2 per aircraft)
        for mi in range(AGM88_PER_SEAD):
            _agm88_seq += 1
            imp_lon, imp_lat = _cep_scatter(tgt_lon, tgt_lat, 5.0, f35b_rng)
            agm_dist = _dist_km(F35B_SEAD_FIRE_LON, F35B_SEAD_FIRE_LAT, imp_lon, imp_lat)
            agm_flight_s = agm_dist / AGM88_SPD_KS
            imp_t = fire_t + mi * 6.0 + agm_flight_s
            kml.append(
                f'  <Placemark>'
                f'<name>AGM-88E #{_agm88_seq} → {tgt_name}</name>'
                f'<description><![CDATA['
                f'<b>AGM-88E AARGM — Weapon #{_agm88_seq}</b><br/>'
                f'<table border="0" cellpadding="2">'
                f'<tr><td><b>Aircraft</b></td><td>F-35B SEAD #{si+1}</td></tr>'
                f'<tr><td><b>Target</b></td><td>{tgt_name}</td></tr>'
                f'<tr><td><b>Impact coords</b></td>'
                f'<td>{imp_lat:.5f}°N, {imp_lon:.5f}°E</td></tr>'
                f'<tr><td><b>CEP</b></td><td>5 m (passive-radar + IIR terminal)</td></tr>'
                f'<tr><td><b>Warhead</b></td><td>WDU-21/B 146 kg blast-fragmentation</td></tr>'
                f'<tr><td><b>Speed</b></td><td>Mach 1.8 cruise → Mach 2+ terminal</td></tr>'
                f'<tr><td><b>Standoff range</b></td><td>{agm_dist:.1f} km</td></tr>'
                f'<tr><td><b>Impact time</b></td><td>T{imp_t/60:+.1f} min</td></tr>'
                f'</table>'
                f']]></description>'
                f'<styleUrl>#f35b_agm88_impact</styleUrl>'
                f'<TimeStamp><when>{_ts(imp_t)}</when></TimeStamp>'
                f'<Point><coordinates>{imp_lon:.6f},{imp_lat:.6f},0</coordinates>'
                f'</Point></Placemark>\n'
            )
            f35b_agm88_hits += 1
    kml.append('  </Folder>\n')   # SEAD wave

    # ── CAS sorties ───────────────────────────────────────────────────────────
    total_cas_bombs = N_F35B_CAS * GBU38_PER_CAS * F35B_SORTIES
    kml.append(
        f'  <Folder><name>CAS Sorties — {N_F35B_CAS}× F-35B / '
        f'{total_cas_bombs}× GBU-38 JDAM / {F35B_SORTIES} waves</name>\n'
    )
    for sortie in range(F35B_SORTIES):
        sortie_dep_base = F35B_CAS1_DEP_S if sortie == 0 else F35B_CAS2_DEP_S
        kml.append(f'  <Folder><name>CAS Wave {sortie+1}</name>\n')
        for ci in range(N_F35B_CAS):
            ac_id = ci + 1
            slon, slat = _ship_offset(ci, N_F35B_CAS, LHA_LON, LHA_LAT, 0.012)
            dep_s  = sortie_dep_base + ci * 12.0
            arr_s  = dep_s + _flt_s(slon, slat, KHARG_LON, KHARG_LAT, F35B_KMH)
            # All 4 bombs dropped at 30-s intervals after arrival
            last_bomb_t  = arr_s + GBU38_PER_CAS * 30.0
            ret_dep_s    = last_bomb_t + 60.0   # 60 s loiter post-strike
            ret_s        = ret_dep_s + _flt_s(KHARG_LON, KHARG_LAT, slon, slat, F35B_KMH)

            # Outbound track
            _cas_out = _jet_arc_pts(slon, slat, KHARG_LON, KHARG_LAT, F35B_ALT_M)
            _cas_out_ts = [dep_s + (arr_s - dep_s) * k / (len(_cas_out) - 1)
                           for k in range(len(_cas_out))]
            kml.extend(gx_track(
                "helo_f35b", _cas_out, _cas_out_ts,
                f"F-35B CAS #{ac_id} W{sortie+1}",
                f"<![CDATA[<b>F-35B Lightning II — CAS #{ac_id} Wave {sortie+1}</b><br/>"
                f"Role: Close Air Support (CAS) — beast mode<br/>"
                f"Loadout: {GBU38_PER_CAS}× GBU-38 JDAM (500 lb) + "
                f"{AIM120_PER_F35B}× AIM-120C-7 + {AIM9X_PER_F35B}× AIM-9X Block II<br/>"
                f"Cruise: {F35B_KMH} km/h at {F35B_ALT_M:,} m AGL<br/>"
                f"Bombs on target: {arr_s/60:+.1f} – {last_bomb_t/60:+.1f} min<br/>"
                f"CEP: {F35B_CEP_M:.0f} m (GPS/INS)]]>",
                altitude_mode="relativeToGround"
            ))
            # Return track
            _cas_ret = _jet_arc_pts(KHARG_LON, KHARG_LAT, slon, slat, F35B_ALT_M)
            _cas_ret_ts = [ret_dep_s + (ret_s - ret_dep_s) * k / (len(_cas_ret) - 1)
                           for k in range(len(_cas_ret))]
            kml.extend(gx_track("helo_ret", _cas_ret, _cas_ret_ts,
                                 f"F-35B CAS #{ac_id} W{sortie+1} RTN", "",
                                 altitude_mode="relativeToGround"))

            # Individual GBU-38 JDAM impact placemarks
            for bi in range(GBU38_PER_CAS):
                _gbu38_seq += 1
                tgt_e = _cas_tgt_pool[_cas_tgt_idx % len(_cas_tgt_pool)]
                _cas_tgt_idx += 1
                t_lon_b, t_lat_b, t_name_b = tgt_e[0], tgt_e[1], tgt_e[2]
                imp_lon_b, imp_lat_b = _cep_scatter(t_lon_b, t_lat_b, F35B_CEP_M, f35b_rng)
                bomb_t = arr_s + (bi + 1) * 30.0
                kml.append(
                    f'  <Placemark>'
                    f'<name>GBU-38 #{_gbu38_seq} → {t_name_b[:40]}</name>'
                    f'<description><![CDATA['
                    f'<b>GBU-38 JDAM — Weapon #{_gbu38_seq}</b><br/>'
                    f'<table border="0" cellpadding="2">'
                    f'<tr><td><b>Aircraft</b></td>'
                    f'<td>F-35B CAS #{ac_id} Wave {sortie+1}</td></tr>'
                    f'<tr><td><b>Target</b></td><td>{t_name_b}</td></tr>'
                    f'<tr><td><b>Impact coords</b></td>'
                    f'<td>{imp_lat_b:.5f}°N, {imp_lon_b:.5f}°E</td></tr>'
                    f'<tr><td><b>Weapon</b></td>'
                    f'<td>GBU-38 / Mk-82 500 lb (227 kg)</td></tr>'
                    f'<tr><td><b>Guidance</b></td>'
                    f'<td>GPS/INS JDAM kit, CEP {F35B_CEP_M:.0f} m</td></tr>'
                    f'<tr><td><b>Warhead</b></td>'
                    f'<td>89 kg H-6 blast-fragmentation</td></tr>'
                    f'<tr><td><b>Lethal radius</b></td><td>~25 m vs. personnel in open</td></tr>'
                    f'<tr><td><b>Delivery alt</b></td><td>{F35B_ALT_M:,} m AGL</td></tr>'
                    f'<tr><td><b>Bomb #</b></td><td>{bi+1} of {GBU38_PER_CAS} this sortie</td></tr>'
                    f'<tr><td><b>Impact time</b></td><td>T{bomb_t/60:+.1f} min</td></tr>'
                    f'</table>'
                    f']]></description>'
                    f'<styleUrl>#f35b_jdam_impact</styleUrl>'
                    f'<TimeStamp><when>{_ts(bomb_t)}</when></TimeStamp>'
                    f'<Point><coordinates>{imp_lon_b:.6f},{imp_lat_b:.6f},0</coordinates>'
                    f'</Point></Placemark>\n'
                )
                f35b_jdam_hits += 1
        kml.append('  </Folder>\n')   # CAS Wave N
    kml.append('  </Folder>\n')   # CAS Sorties
    kml.append('  </Folder>\n')   # F-35B Strike Package

    f35b_total_weapons = f35b_agm88_hits + f35b_jdam_hits

    # ── Fireteam gx:Track paths — one Placemark per HP state per squad ───────────
    # gx:Track is the most GE-efficient animated agent primitive:
    #   • Single Placemark per state (vs. N per-step Placemarks)
    #   • GE hardware-interpolates icon position between <when> timestamps
    #   • Automatic heading (icon faces direction of travel via <gx:angles>)
    #   • Trail rendered via LineStyle; icon via IconStyle — both in one Style
    # Splitting at HP changes gives at most 4 Placemarks per fireteam (one per state).
    hp_trk_style = {4: "sq_full", 3: "sq_lt", 2: "sq_hvy", 1: "sq_hvy", 0: "sq_kia"}

    kml.append(f'  <Folder><name>Marine Fireteams ({N_SQUADS} × 4 marines, gx:Track)</name>\n'
               f'  <!-- One gx:Track Placemark per HP state per fireteam. -->\n'
               f'  <!-- Green=4HP  Yellow=3HP  Orange=1-2HP  Red=KIA -->\n')
    for si, walk_steps in enumerate(squad_walk):
        sq_wave  = squad_pos[si][2]
        events   = squad_events[si]
        active_s = wave_arrive_s[sq_wave]

        # Build HP state timeline [(t_start, t_end, hp)]
        cur_hp, cur_t = SQUAD_HP, active_s
        states = []
        for evt_t, new_hp in events:
            if cur_t < evt_t:
                states.append((cur_t, evt_t, cur_hp))
            cur_t, cur_hp = evt_t, new_hp
        states.append((cur_t, SIM_END_S, cur_hp))

        for st_b, st_e, hp in states:
            if st_b >= st_e:
                continue
            # Walk waypoints in [st_b, st_e) → gx:Track pts + timestamps
            seg_pts = [(wlon, wlat, 0.0) for wlon, wlat, wt in walk_steps if st_b <= wt < st_e]
            seg_ts  = [wt                for wlon, wlat, wt in walk_steps if st_b <= wt < st_e]
            if not seg_pts:
                nearest = min(walk_steps, key=lambda x: abs(x[2] - st_b))
                seg_pts = [(nearest[0], nearest[1], 0.0)]
                seg_ts  = [st_b]
            # Need at least 2 points for a meaningful track; pad if needed
            if len(seg_pts) == 1:
                seg_pts = seg_pts * 2
                seg_ts  = [st_b, st_e]

            lbl  = (f"FT.{si+1:03d}" if hp == SQUAD_HP else
                    (f"FT.{si+1:03d} KIA" if hp == 0 else f"FT.{si+1:03d} {hp}HP"))
            desc = (f"Fireteam {si+1:03d} | Wave {sq_wave+1}<br/>"
                    f"HP: {hp}/{SQUAD_HP} | Marines alive: {hp}/{MARINES_PER_SQUAD}<br/>"
                    f"{'KIA — fireteam eliminated' if hp == 0 else ('Damaged' if hp < SQUAD_HP else 'Operational')}")
            sty  = hp_trk_style.get(hp, "sq_kia")
            kml.extend(gx_track(sty, seg_pts, seg_ts, lbl, desc,
                                altitude_mode="clampToGround"))
    kml.append('  </Folder>\n')

    # ── Shahed-136 gx:Track animated drone strikes ────────────────────────────
    # Rendering strategy for 2,000-drone swarm (GE performance):
    #   • All AI drones rendered (2-phase approach + terminal): highest interest
    #   • All intercepted drones rendered (partial arc + flash): shows Stinger effect
    #   • Standard breakthroughs: sample 15% for representative swarm density
    #     (the remaining 85% are in the stats but not individually visualised)
    N_ARC        = 24    # arc segments per drone (25 points, smooth sea-skim profile)
    DRONE_SAMPLE = 0.15  # fraction of standard breakthrough drones to render
    drone_vis_rng = _random.Random(31415)

    kml.append('  <Folder><name>Shahed-136 Drone Strikes</name>\n')
    for _, n_d, wave_lbl in DRONE_WAVES:
        kml.append(f'  <Folder><name>Wave {wave_lbl} ({n_d} drones)</name>\n')
        for dr in (d for d in all_drones if d['wave'] == wave_lbl):
            s_lon, s_lat = dr['src_lon'], dr['src_lat']
            i_lon, i_lat = dr['imp_lon'], dr['imp_lat']
            launch_s, impact_s, flight_s = dr['launch_s'], dr['impact_s'], dr['flight_s']
            dist_km = dr['dist_km']

            if dr['is_int']:
                # ── Intercepted: partial arc → Stinger flash ──────────────────
                # Compute how far along the arc the intercept occurs
                int_lon, int_lat, int_s = dr['int_lon'], dr['int_lat'], dr['int_s']
                int_frac = (int_s - launch_s) / max(flight_s, 1)
                n_seg_int = max(2, round(int_frac * N_ARC))
                full_arc  = arc_points(s_lon, s_lat, i_lon, i_lat, SHAHED_PEAK, N_ARC, True)
                arc_int   = full_arc[:n_seg_int + 1]
                t_int_pts = [launch_s + (k / N_ARC) * flight_s for k in range(n_seg_int + 1)]
                kml.extend(gx_track(
                    "kharg_shahed", arc_int, t_int_pts,
                    f"Shahed {wave_lbl}-{dr['idx']} [INTERCEPTED]",
                    f"Shahed-136 wave {wave_lbl} #{dr['idx']}<br/>"
                    f"From: {dr['site_name']} | Dist: {dist_km:.0f} km<br/>"
                    f"<b>Intercepted</b> by FIM-92 Stinger at T+{int_s/60:.1f} min",
                    altitude_mode="relativeToGround"
                ))
                # 10 alternating flash markers at intercept point (3 s each)
                for _step in range(10):
                    _t0  = int_s + _step * 3.0
                    _t1  = _t0 + 3.0
                    _sty = "kharg_intercept_mk" if _step % 2 == 0 else "kharg_intercept_wh"
                    kml.append(
                        f'  <Placemark><name>Stinger Kill {wave_lbl}-{dr["idx"]}</name>'
                        f'<styleUrl>#{_sty}</styleUrl>'
                        f'{_tspan(_t0, _t1)}'
                        f'<Point><altitudeMode>relativeToGround</altitudeMode>'
                        f'<coordinates>{int_lon:.5f},{int_lat:.5f},500</coordinates>'
                        f'</Point></Placemark>\n'
                    )

            elif dr['is_ai']:
                # ── AI-guided: two-phase approach + terminal lock-on ──────────
                lock_frac = dr['lock_frac']
                n_seg_app = max(2, round(lock_frac * N_ARC))
                full_arc  = arc_points(s_lon, s_lat, i_lon, i_lat, SHAHED_PEAK, N_ARC, True)
                arc_app   = full_arc[:n_seg_app + 1]
                t_app     = [launch_s + (k / N_ARC) * flight_s for k in range(n_seg_app + 1)]
                lock_pt   = arc_app[-1]
                lock_t    = t_app[-1]
                ai_lon, ai_lat = dr['ai_tgt_lon'], dr['ai_tgt_lat']
                t_terminal    = flight_s * (1.0 - lock_frac) * 0.88
                t_term_end    = lock_t + t_terminal
                t_term        = [lock_t + (k / 8) * t_terminal for k in range(9)]
                term_arc      = arc_points(lock_pt[0], lock_pt[1], ai_lon, ai_lat,
                                           max(lock_pt[2] * 0.5, 15.0), 8, True)
                lock_km = dist_km * (1.0 - lock_frac)
                kml.extend(gx_track(
                    "kharg_shahed_ai_approach", arc_app, t_app,
                    f"Shahed {wave_lbl}-{dr['idx']} [AI-APPROACH]",
                    f"<b>AI/CV-guided Shahed-136</b> wave {wave_lbl} #{dr['idx']}<br/>"
                    f"From: {dr['site_name']} | Dist: {dist_km:.0f} km<br/>"
                    f"Phase 1 dead-reckoning: {dist_km - lock_km:.0f} km ({lock_frac*100:.0f}%)<br/>"
                    f"EO/IR lock-on at: {lock_km:.0f} km — T+{lock_t/60:.1f} min",
                    altitude_mode="relativeToGround"
                ))
                kml.extend(gx_track(
                    "kharg_shahed_ai_terminal", term_arc, t_term,
                    f"Shahed {wave_lbl}-{dr['idx']} [AI-TERMINAL]",
                    f"<b>AI TERMINAL LOCK-ON</b> — computer-vision guidance<br/>"
                    f"Acquired at {lock_km:.0f} km — T+{lock_t/60:.1f} min<br/>"
                    f"Impact T+{t_term_end/60:.1f} min | <b>CIWS defeated</b>",
                    altitude_mode="relativeToGround"
                ))
                kml.append(
                    f'  <Placemark><name>AI IMPACT {wave_lbl}-{dr["idx"]}</name>'
                    f'<styleUrl>#kharg_impact</styleUrl>'
                    f'<description><![CDATA[<b>AI-guided Shahed impact</b><br/>'
                    f'From: {dr["site_name"]} | EO/IR lock at {lock_km:.0f} km<br/>'
                    f'Impact T+{t_term_end/60:.1f} min]]></description>'
                    f'<TimeStamp><when>{_ts(t_term_end)}</when></TimeStamp>'
                    f'<Point><coordinates>{ai_lon:.5f},{ai_lat:.5f},0</coordinates>'
                    f'</Point></Placemark>\n'
                )

            else:
                # ── Standard breakthrough: sampled 15% for GE performance ─────
                if drone_vis_rng.random() > DRONE_SAMPLE:
                    continue   # skip rendering; drone is in stats but not visualised
                full_arc  = arc_points(s_lon, s_lat, i_lon, i_lat, SHAHED_PEAK, N_ARC, True)
                t_arc_pts = [launch_s + (k / N_ARC) * flight_s for k in range(N_ARC + 1)]
                kml.extend(gx_track(
                    "kharg_shahed", full_arc, t_arc_pts,
                    f"Shahed {wave_lbl}-{dr['idx']} [BREAKTHROUGH]",
                    f"Shahed-136 wave {wave_lbl} #{dr['idx']}<br/>"
                    f"From: {dr['site_name']} | Dist: {dist_km:.0f} km<br/>"
                    f"Speed: {SHAHED_SPD_KS*3600:.0f} km/h | Impact T+{impact_s/60:.1f} min",
                    altitude_mode="relativeToGround"
                ))
                kml.append(
                    f'  <Placemark><name>Impact {wave_lbl}-{dr["idx"]}</name>'
                    f'<styleUrl>#kharg_impact</styleUrl>'
                    f'<description><![CDATA[Shahed-136 impact<br/>'
                    f'Wave {wave_lbl} #{dr["idx"]} | CEP {SHAHED_CEP_M:.0f} m<br/>'
                    f'T+{impact_s/60:.1f} min]]></description>'
                    f'{_tspan(impact_s, impact_s + 90)}'
                    f'<Point><coordinates>{i_lon:.5f},{i_lat:.5f},0</coordinates>'
                    f'</Point></Placemark>\n'
                )

        kml.append('  </Folder>\n')
    kml.append('  </Folder>\n')

    # ── Lanchester ground battle timeline placemarks ──────────────────────────
    kml.append('  <Folder><name>Ground Battle (Lanchester Square Law)</name>\n'
               '  <!-- Attrition model: USMC vs. IRGC — Marines 3.2× combat effectiveness -->\n')
    for li in range(len(lanc_states) - 1):
        lt0, lm0, lb0, _navy_act0 = lanc_states[li]
        lt1 = lanc_states[li + 1][0]
        marine_cas_step = USMC_START - lm0
        irgc_cas_step   = IRGC_START - lb0
        elapsed_min     = (lt0 - last_arrive_s) / 60
        navy_row = (f'<tr><td style="color:#ffaa00">USN Reserve</td>'
                    f'<td>{round(lN):,}</td>'
                    f'<td style="color:orange">{NAVY_RESERVE - round(lN):,}</td></tr>'
                    if _navy_act0 else '')
        kml.append(
            f'  <Placemark>'
            f'<name>Battle T+{elapsed_min:.0f}min — {"USN" if _navy_act0 else "Marines"} {lm0 if not _navy_act0 else round(lN):,} / IRGC {lb0:,}</name>'
            f'<description><![CDATA['
            f'<b>Ground Battle — T+{elapsed_min:.0f} min after all Marines ashore</b><br/>'
            + (f'<b style="color:orange">⚠ Navy reserve activated — Marines eliminated</b><br/>' if _navy_act0 else '')
            + f'<table border="1" cellpadding="3" style="border-collapse:collapse">'
            f'<tr><th>Force</th><th>Strength</th><th>Casualties</th></tr>'
            f'<tr><td>USMC</td><td>{lm0:,}</td><td style="color:orange">{marine_cas_step}</td></tr>'
            + navy_row
            + f'<tr><td>IRGC</td><td>{lb0:,}</td><td style="color:red">{irgc_cas_step}</td></tr>'
            f'</table><br/>'
            f'Lanchester effectiveness: α_M={ALPHA_M:.1e}  β_I={BETA_I:.1e}<br/>'
            f'Marine advantage ratio: {ALPHA_M/BETA_I:.1f}×'
            f']]></description>'
            f'<styleUrl>#sty_battle</styleUrl>'
            f'{_tspan(lt0, lt1)}'
            f'<Point><coordinates>{KHARG_LON + 0.015:.6f},{KHARG_LAT + 0.015:.6f},0'
            f'</coordinates></Point></Placemark>\n'
        )
    kml.append('  </Folder>\n')

    # ── Outcome summary placemark ──────────────────────────────────────────────
    total_rt = N_WAVES * (N_MV22 + N_CH53)   # approximate round trips
    total_marine_cas = kia_total + wia_total + lanc_marine_cas
    kml.append(
        f'  <Placemark><name>Operation Kharg Island — Final Assessment</name>'
        f'<description><![CDATA['
        f'<b>Operation Kharg Island — Final Assessment</b><br/><br/>'
        f'<table border="1" cellpadding="4" style="border-collapse:collapse">'
        f'<tr><th colspan="2">Air Assault (LHA-7 USS Tripoli)</th></tr>'
        f'<tr><td>Marines landed</td><td><b>{TOTAL_MARINES:,}</b></td></tr>'
        f'<tr><td>Fireteams ({MARINES_PER_SQUAD}-man)</td><td>{N_SQUADS:,}</td></tr>'
        f'<tr><td>Sortie waves</td><td>{N_WAVES}</td></tr>'
        f'<tr><td>Helicopter round trips</td><td>~{total_rt}</td></tr>'
        f'<tr><td>All ashore by</td><td>T+{last_arrive_s/60:.0f} min</td></tr>'
        f'<tr><th colspan="2">Shahed-136 Counterattack ({n_launched:,} drones, 5 waves)</th></tr>'
        f'<tr><td>AI-guided (CV, 5%)</td><td>{n_ai}</td></tr>'
        f'<tr><td>Stinger rounds available</td><td>{STINGER_MAG}</td></tr>'
        f'<tr><td>Stinger rounds fired</td><td>{stinger_fired} (mag dry at drone #{STINGER_MAG})</td></tr>'
        f'<tr><td>Intercepted (Pk={STINGER_PK*100:.0f}% — DoD optest baseline)</td><td style="color:green">{stinger_hits}</td></tr>'
        f'<tr><td>Unengaged (no rounds left)</td><td style="color:red">{n_bt - n_ai}</td></tr>'
        f'<tr><td>Total breakthroughs</td><td style="color:orange">{n_bt}</td></tr>'
        f'<tr><th colspan="2">F-35B Strike Package ({N_F35B} aircraft)</th></tr>'
        f'<tr><td>SEAD aircraft</td><td>{N_F35B_SEAD} (AGM-88E AARGM)</td></tr>'
        f'<tr><td>AGM-88E AARGM fired</td>'
        f'<td style="color:cyan"><b>{f35b_agm88_hits}</b> '
        f'(targets: HAWK SAM, ZSU-23-4 ×2, MANPADS)</td></tr>'
        f'<tr><td>CAS aircraft</td><td>{N_F35B_CAS} ({F35B_SORTIES} sorties each)</td></tr>'
        f'<tr><td>GBU-38 JDAM delivered</td>'
        f'<td style="color:#ffaa00"><b>{f35b_jdam_hits}</b> '
        f'(CEP {F35B_CEP_M:.0f} m, 500 lb each)</td></tr>'
        f'<tr><td>Total precision weapons</td>'
        f'<td><b>{f35b_total_weapons}</b></td></tr>'
        f'<tr><th colspan="2">Helicopter Losses (AI drone proximity)</th></tr>'
        f'<tr><td>Aircraft downed</td><td style="color:red"><b>{n_helos_lost}</b> of {len(all_helo_ids)}</td></tr>'
        f'<tr><td>Marines not delivered</td><td style="color:orange">{marines_not_delivered:,}</td></tr>'
        f'<tr><td>Marines actually landed</td><td><b>{total_marines_actual:,}</b></td></tr>'
        f'<tr><td>Fireteams eliminated</td><td style="color:red"><b>{n_killed}</b> ({kia_total} KIA)</td></tr>'
        f'<tr><td>Fireteams damaged</td><td style="color:orange">{n_damaged} ({wia_total} WIA)</td></tr>'
        f'<tr><td>Fireteams intact</td><td style="color:green">{n_intact}</td></tr>'
        f'<tr><th colspan="2">Ground Battle — Lanchester Square Law</th></tr>'
        f'<tr><td>IRGC start</td><td>{IRGC_START:,} (incl. weighted Basij)</td></tr>'
        f'<tr><td>IRGC casualties</td><td style="color:red">{lanc_irgc_cas:,}</td></tr>'
        f'<tr><td>IRGC survivors</td><td>{lanc_irgc_final:,}</td></tr>'
        f'<tr><td>Marine ground KIA (combat)</td><td style="color:orange">{lanc_marine_cas:,}</td></tr>'
        f'<tr><td>Marine survivors</td><td>{lanc_marine_final:,}</td></tr>'
        f'<tr><th colspan="2">Total USMC Casualties</th></tr>'
        f'<tr><td>Drone KIA</td><td style="color:red">{kia_total}</td></tr>'
        f'<tr><td>Drone WIA</td><td style="color:orange">{wia_total}</td></tr>'
        f'<tr><td>Ground combat KIA</td><td style="color:red">{lanc_marine_cas:,}</td></tr>'
        f'<tr><td><b>TOTAL CASUALTIES</b></td><td style="color:red"><b>{total_marine_cas:,}</b></td></tr>'
        f'</table><br/>'
        f'<i>Fireteam colours: green=full HP  yellow=3HP  orange=1-2HP  red=KIA</i>'
        f']]></description>'
        f'<styleUrl>#sty_marine</styleUrl>'
        f'<Point><coordinates>{KHARG_LON:.6f},{KHARG_LAT:.6f},0</coordinates>'
        f'</Point></Placemark>\n'
    )

    kml.append('</Document>\n</kml>')

    # ── Write KMZ ─────────────────────────────────────────────────────────────
    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, OUT_FILENAME)
    with _zf.ZipFile(out_path, "w", _zf.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", "".join(kml).encode("utf-8"))

    # ── Write HTML summary ────────────────────────────────────────────────────
    html_filename = OUT_FILENAME.replace(".kmz", ".html")
    html_path = os.path.join(out_dir, html_filename)
    kmz_link  = OUT_FILENAME
    _gen_ts   = fmt_time(sim_time(0))[:10]   # date string

    def _pct_color(pct, invert=False):
        """Green→amber→red gradient as hex colour, based on percentage 0-100."""
        v = pct / 100.0
        if invert:
            v = 1.0 - v
        r = min(255, int(v * 510))
        g = min(255, int((1.0 - v) * 510))
        b = 0
        return f"#{r:02x}{g:02x}{b:02x}"

    def _card(label, value, sub, color="#3399ff"):
        return (f'<div class="card" style="border-top-color:{color}">'
                f'<div class="card-label">{label}</div>'
                f'<div class="card-value" style="color:{color}">{value}</div>'
                f'<div class="card-sub">{sub}</div></div>\n')

    breach_pct = 100 * n_bt / max(n_launched, 1)
    int_pct    = 100 * n_intercepted / max(n_launched, 1)

    rows = [
        ("Marines landed", f"{total_marines_actual:,}", "#00dd66"),
        ("Drone breakthroughs", f"{n_bt:,} ({breach_pct:.0f}%)", _pct_color(breach_pct)),
        ("USMC KIA (drone)", f"{kia_total:,}", "#ff4444"),
        ("USMC WIA (drone)", f"{wia_total:,}", "#ffaa00"),
        ("IRGC casualties", f"{lanc_irgc_cas:,}", "#00dd66"),
        ("USMC ground KIA", f"{lanc_marine_cas:,}", "#ff4444"),
        ("F-35B weapons", f"{f35b_total_weapons}", "#3399ff"),
        ("Helicopters lost", f"{n_helos_lost}", "#ff4444" if n_helos_lost else "#00dd66"),
    ]

    html_parts = [
        "<!DOCTYPE html><html lang='en'><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Kharg Island Assault — {SCENARIO_LABEL}</title>\n",
        "    <style>\n"
        "      *{box-sizing:border-box;margin:0;padding:0}\n"
        "      body{background:#000000;color:#ffffff;font-family:'Courier New',Courier,monospace;"
        "font-size:12px;line-height:1.55;-webkit-font-smoothing:antialiased}\n"
        "      a{color:#3399ff;text-decoration:none;transition:color .15s}"
        " a:hover{color:#66bbff;text-decoration:underline}\n"
        "      h1{color:#3399ff;font-size:20px;margin-bottom:4px;letter-spacing:2px;"
        "text-shadow:0 0 18px #3399ff55}\n"
        "      h2{color:#3399ff;font-size:13px;margin:20px 0 6px;"
        "border-bottom:1px solid #333333;padding-bottom:5px;"
        "letter-spacing:2px;text-transform:uppercase}\n"
        "      .wrap{max-width:1200px;margin:0 auto;padding:20px 24px}\n"
        "      .ts{color:#777777;font-size:10px;margin-bottom:16px;letter-spacing:.3px}\n"
        "      .topbar{background:#000000;border-bottom:2px solid #3399ff;"
        "border-left:3px solid #3399ff;padding:10px 24px;"
        "margin:-20px -24px 20px;display:flex;align-items:center;gap:16px}\n"
        "      .topbar-title{color:#3399ff;font-size:13px;font-weight:bold;"
        "letter-spacing:2px;flex:1}\n"
        "      .topbar-sub{color:#aaaaaa;font-size:10px}\n"
        "      .cards{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px}\n"
        "      .card{background:#0a0a0a;border:1px solid #333333;border-radius:0;"
        "padding:12px 16px;min-width:148px;flex:1 1 148px;"
        "border-top:3px solid transparent;border-left:3px solid #3399ff33;"
        "transition:border-color .2s}\n"
        "      .card:hover{border-top-color:#3399ff;border-left-color:#3399ff}\n"
        "      .card-label{color:#aaaaaa;font-size:9px;text-transform:uppercase;"
        "letter-spacing:2px}\n"
        "      .card-value{font-size:20px;font-weight:bold;margin-top:3px;"
        "letter-spacing:-.5px}\n"
        "      .card-sub{color:#777777;font-size:9px;margin-top:1px}\n"
        "      .tbl-wrap{overflow-x:auto;margin-bottom:18px;"
        "border:1px solid #333333;border-left:3px solid #3399ff}\n"
        "      table{border-collapse:collapse;width:100%;font-size:11px}\n"
        "      thead{position:sticky;top:0;z-index:2}\n"
        "      th{color:#aaaaaa;text-align:left;padding:6px 12px;"
        "background:#0a0a0a;border-bottom:2px solid #3399ff;"
        "font-weight:bold;letter-spacing:1px}\n"
        "      td{padding:5px 12px;border-bottom:1px solid #111111;"
        "transition:background .1s;color:#ffffff}\n"
        "      tr:hover td{background:#0a0a0a}\n"
        "      tr:nth-child(even) td{background:#080808}\n"
        "      .val{font-family:'Courier New',monospace;text-align:right}\n"
        "      .desc{background:#000000;border-left:3px solid #3399ff;"
        "border-top:2px solid #3399ff;"
        "padding:12px 16px;margin-bottom:16px;"
        "font-size:11px;color:#aaaaaa;line-height:1.65}\n"
        "      .section-header{display:flex;align-items:center;gap:8px;margin:22px 0 8px;"
        "border-left:3px solid #3399ff;padding-left:10px}\n"
        "      .section-header::after{content:'';flex:1;height:1px;background:#333333}\n"
        "      .section-title{color:#3399ff;font-size:13px;font-weight:bold;"
        "letter-spacing:2px;text-transform:uppercase;white-space:nowrap}\n"
        "      .footer{margin-top:28px;padding-top:10px;border-top:1px solid #333333;"
        "color:#777777;font-size:10px;letter-spacing:.3px}\n"
        "      .badge{display:inline-block;padding:2px 8px;border-radius:0;"
        "font-size:10px;font-weight:bold;letter-spacing:1px}\n"
        "      .total-row td{background:#0a0a0a!important;font-weight:bold;"
        "border-top:2px solid #3399ff!important;color:#3399ff!important}\n"
        "    </style></head><body><div class='wrap'>\n",
        # topbar
        f"<div class='topbar'>"
        f"<span class='topbar-title'>◈ OPERATION KHARG ISLAND — {SCENARIO_LABEL.upper()}</span>"
        f"<span class='topbar-sub'>Simulation start: {_gen_ts} &nbsp;·&nbsp; "
        f"<a href='{kmz_link}'>Open in Google Earth →</a></span></div>\n",
        f"<h1>Operation Kharg Island — {SCENARIO_LABEL}</h1>\n"
        f"<div class='ts'>Simulation generated {_gen_ts} &nbsp;·&nbsp; "
        f"<a href='summary.html'>← All-scenario summary</a></div>\n",
        # scenario description
        "<div class='desc'>"
        "<b>USMC amphibious assault on Kharg Island</b> — Iran's primary crude export terminal. "
        f"LHA-7 USS Tripoli leads the Amphibious Ready Group with "
        f"{N_MV22}× MV-22B Osprey, {N_CH53}× CH-53E Super Stallion, "
        f"{N_AH1Z}× AH-1Z Viper, and <b>{N_F35B}× F-35B Lightning II</b>. "
        f"Iran responds with {DRONE_TOTAL:,} Shahed-136 loitering munitions in "
        f"{len(DRONE_WAVES)} waves from {len(D_SITES)} launch sites. "
        f"F-35Bs execute pre-assault SEAD ({N_F35B_SEAD} aircraft, "
        f"{N_F35B_SEAD*AGM88_PER_SEAD}× AGM-88E AARGM against radar/AAA sites) "
        f"then {F35B_SORTIES}-wave CAS ({N_F35B_CAS} aircraft, "
        f"{N_F35B_CAS*GBU38_PER_CAS*F35B_SORTIES}× GBU-38 JDAM, CEP {F35B_CEP_M:.0f} m)."
        "</div>\n",
        # stat cards
        "<div class='cards'>\n",
        _card("Marines landed", f"{total_marines_actual:,}", f"of {TOTAL_MARINES:,} planned",
              "#00dd66" if total_marines_actual == TOTAL_MARINES else "#ffaa00"),
        _card("Waves / cycle time", f"{N_WAVES}", f"{WAVE_CYCLE_S/60:.0f} min/wave", "#3399ff"),
        _card("Shahed breakthroughs", f"{n_bt:,}", f"{breach_pct:.0f}% penetration rate",
              _pct_color(breach_pct)),
        _card("Stinger intercepts", f"{n_intercepted}", f"Pk {STINGER_PK*100:.0f}% / {STINGER_MAG} rounds",
              "#00dd66"),
        _card("USMC KIA (drones)", f"{kia_total}", "fireteams eliminated",
              "#ff4444" if kia_total else "#00dd66"),
        _card("IRGC casualties", f"{lanc_irgc_cas:,}", f"of {N_IRGC:,} defenders", "#00dd66"),
        _card("F-35B weapons", f"{f35b_total_weapons}",
              f"{f35b_agm88_hits}× AGM-88E + {f35b_jdam_hits}× GBU-38", "#3399ff"),
        _card("Helicopters lost", f"{n_helos_lost}",
              f"of {len(all_helo_ids)} aircraft",
              "#ff4444" if n_helos_lost else "#00dd66"),
        "</div>\n",
        # F-35B detail table
        "<div class='section-header'><span class='section-title'>F-35B Strike Package</span></div>\n"
        "<div class='tbl-wrap'><table><thead><tr>"
        "<th>Package</th><th>Aircraft</th><th>Weapons</th><th>Weapon type</th>"
        "<th>CEP</th><th>Warhead</th><th>Targets</th></tr></thead><tbody>\n"
        f"<tr><td>SEAD Wave</td><td class='val'>{N_F35B_SEAD}</td>"
        f"<td class='val' style='color:#ff4444'>{f35b_agm88_hits}</td>"
        f"<td>AGM-88E AARGM</td><td class='val'>5 m</td>"
        f"<td>WDU-21/B 146 kg</td>"
        f"<td>HAWK SAM · ZSU-23-4 ×2 · MANPADS</td></tr>\n"
        f"<tr><td>CAS Wave 1</td><td class='val'>{N_F35B_CAS}</td>"
        f"<td class='val' style='color:#ffaa00'>{N_F35B_CAS*GBU38_PER_CAS}</td>"
        f"<td>GBU-38 JDAM 500 lb</td><td class='val'>{F35B_CEP_M:.0f} m</td>"
        f"<td>Mk-82 89 kg H-6</td>"
        f"<td>IRGC HQ · command nodes · infantry</td></tr>\n"
        f"<tr><td>CAS Wave 2</td><td class='val'>{N_F35B_CAS}</td>"
        f"<td class='val' style='color:#ffaa00'>{N_F35B_CAS*GBU38_PER_CAS}</td>"
        f"<td>GBU-38 JDAM 500 lb</td><td class='val'>{F35B_CEP_M:.0f} m</td>"
        f"<td>Mk-82 89 kg H-6</td>"
        f"<td>Armour · ammo cache · reinforcements</td></tr>\n"
        f"<tr class='total-row'><td><b>TOTAL</b></td>"
        f"<td class='val'><b>{N_F35B}</b></td>"
        f"<td class='val'><b>{f35b_total_weapons}</b></td>"
        f"<td colspan='4' style='color:#7fa8cc'>"
        f"All weapons individually targetable in Google Earth</td></tr>\n"
        "</tbody></table></div>\n",
        # assault table
        "<div class='section-header'><span class='section-title'>Assault Timeline</span></div>\n"
        "<div class='tbl-wrap'><table><thead><tr>"
        "<th>Event</th><th>Time</th><th>Detail</th></tr></thead><tbody>\n",
    ]
    html_parts.append(
        f"<tr><td>F-35B SEAD departs</td>"
        f"<td class='val'>T{F35B_SEAD_DEP_S/60:+.0f} min</td>"
        f"<td>4× F-35B launch AGM-88E vs. HAWK SAM + ZSU-23-4 + MANPADS</td></tr>\n"
        f"<tr><td>SEAD on target</td>"
        f"<td class='val'>T{(F35B_SEAD_DEP_S + T_F35B_TO_FIRE + 120)/60:+.0f} min</td>"
        f"<td>{f35b_agm88_hits}× AGM-88E impact — air-defence suppressed</td></tr>\n"
        f"<tr><td>F-35B CAS departs</td>"
        f"<td class='val'>T{F35B_CAS1_DEP_S/60:+.0f} min</td>"
        f"<td>16× F-35B depart for CAS wave 1</td></tr>\n"
        f"<tr><td>Helo wave 1 departs</td>"
        f"<td class='val'>T+0 min</td>"
        f"<td>{N_MV22}× MV-22B + {N_CH53}× CH-53E + {N_AH1Z}× AH-1Z depart LHA-7</td></tr>\n"
        f"<tr><td>Wave 1 lands</td>"
        f"<td class='val'>T+{wave_arrive_s[0]/60:.0f} min</td>"
        f"<td>{TROOPS_PER_WAVE:,} Marines ashore | F-35B CAS overhead</td></tr>\n"
        f"<tr><td>Shahed wave α launches</td>"
        f"<td class='val'>T+{(BASE_LAUNCH)/60:.0f} min</td>"
        f"<td>{DRONE_WAVES[0][1]} Shahed-136 from Iranian mainland sites</td></tr>\n"
        f"<tr><td>Last helo wave lands</td>"
        f"<td class='val'>T+{last_arrive_s/60:.0f} min</td>"
        f"<td>{total_marines_actual:,} Marines ashore | ground battle begins</td></tr>\n"
        f"<tr><td>CAS wave 2 departs</td>"
        f"<td class='val'>T{F35B_CAS2_DEP_S/60:+.0f} min</td>"
        f"<td>16× F-35B rearm + redeploy for sortie 2</td></tr>\n"
        f"<tr><td>Simulation end</td>"
        f"<td class='val'>T+{SIM_END_S/60:.0f} min</td>"
        f"<td>2 h after final wave — IRGC {lanc_irgc_final:,} survivors, "
        f"USMC {lanc_marine_final:,} effective</td></tr>\n"
    )
    html_parts.append(
        "</tbody></table></div>\n"
        "<div class='section-header'>"
        "<span class='section-title'>Shahed Counterattack</span></div>\n"
        "<div class='tbl-wrap'><table><thead><tr>"
        "<th>Metric</th><th class='val'>Value</th><th>Notes</th></tr></thead><tbody>\n"
        f"<tr><td>Total launched</td><td class='val'>{n_launched:,}</td>"
        f"<td>{len(DRONE_WAVES)} waves, {len(D_SITES)} launch sites</td></tr>\n"
        f"<tr><td>AI/CV-guided (5%)</td><td class='val'>{n_ai}</td>"
        f"<td>Guaranteed breakthrough; precision terminal seeker</td></tr>\n"
        f"<tr><td>Stinger rounds fired</td><td class='val'>{stinger_fired}</td>"
        f"<td>Magazine dry after drone #{STINGER_MAG}</td></tr>\n"
        f"<tr><td style='color:#00dd66'>Intercepted</td>"
        f"<td class='val' style='color:#00dd66'>{n_intercepted}</td>"
        f"<td>Pk {STINGER_PK*100:.0f}% (DoD operational test baseline)</td></tr>\n"
        f"<tr><td style='color:#ff4444'>Breakthroughs</td>"
        f"<td class='val' style='color:#ff4444'><b>{n_bt}</b></td>"
        f"<td>Unengaged: {n_bt - n_ai} | AI-guided: {n_ai}</td></tr>\n"
        f"<tr><td>Fireteams KIA</td>"
        f"<td class='val' style='color:#ff4444'>{n_killed}</td>"
        f"<td>{kia_total} Marines (complete fireteam destruction)</td></tr>\n"
        f"<tr><td>Fireteams damaged</td>"
        f"<td class='val' style='color:#ffaa00'>{n_damaged}</td>"
        f"<td>{wia_total} WIA</td></tr>\n"
        "</tbody></table></div>\n"
        "<div class='footer'>"
        "Sources: NAVAIR F-35B STOVL fact sheet · USMC MAGTF Handbook 2025 · "
        "IISS Military Balance 2024 · Jane's All the World's Aircraft · "
        "DoD GAO-02-407T (Stinger Pk) · RAND MG-1104 · Dupuy Institute (2018)"
        "</div>\n"
        "</div></body></html>"
    )
    with open(html_path, "w", encoding="utf-8") as hf:
        hf.write("".join(html_parts))

    return out_path, N_WAVES, TROOPS_PER_WAVE, TOTAL_MARINES, WAVE_CYCLE_S


# ============================================================
# KHARG ISLAND BALLISTIC STRIKE SCENARIO
# ============================================================

def generate_kharg_ballistic_kml(out_dir=None):
    """
    KML/KMZ: Iranian ballistic missile strike on the Kharg Island assault fleet
    and oil terminal infrastructure, timed to coincide with the USMC beach landing.

    Scenario
    --------
    Iran detects the amphibious assault at T+15 min and fires 22 ballistic
    missiles from three mainland sites:
      - 8 × Khalij Fars ASBM  → USS Tripoli (LHA-7) + DDG escort
      - 6 × Fateh-313 SRBM    → Kharg Island oil terminal / pipeline manifold
      - 4 × Zolfaghar SRBM    → Kharg Island storage tanks / loading jetty
      - 4 × Emad MRBM         → secondary fleet targets (LPD-29, LPD-30)

    US defense: DDG SM-6 (30 rounds), Tripoli SeaRAM (22 rounds), Phalanx CIWS.
    Expected intercepts: ~13 / ~22 (59%).  Expected hits: ~9.

    Blast radii (Hopkinson-Cranz scaling, 450–750 kg TNT-equivalent warheads):
      Fateh-313 / Zolfaghar (450 kg):
        Inner ring  (structural kill)   : r ≈  50 m   — red   filled polygon
        Middle ring (significant damage): r ≈ 150 m   — orange outline
        Outer ring  (overpressure zone) : r ≈ 300 m   — yellow outline
      Emad MRBM (750 kg warhead):
        Inner ring:  r ≈  65 m
        Middle ring: r ≈ 185 m
        Outer ring:  r ≈ 380 m
      Oil-fire spread (secondary fires at infrastructure hits):
        Burn radius : r ≈ 200 m   — translucent red fill

    Sources: Glasstone & Dolan, "Effects of Nuclear Weapons" blast scaling
    adapted for conventional HE; Jane's Defence Weekly blast effect tables;
    open-source JDAM/TLAM collateral damage estimates (1,000 ft CEP ring).
    """
    import math as _math
    import zipfile as _zf
    import random as _rand
    import os as _os

    rng = _rand.Random(73)

    # ── Geography ─────────────────────────────────────────────────────────────
    LHA_LON,    LHA_LAT    = 50.325,  28.715   # USS Tripoli NW approach position
    DDG_LON,    DDG_LAT    = 50.325,  28.855   # DDG escort
    LPD1_LON,   LPD1_LAT   = 50.175,  28.690   # LPD-30
    LPD2_LON,   LPD2_LAT   = 50.475,  28.690   # LPD-29

    # Iranian launch sites (inland + coastal)
    BUSHEHR_LON, BUSHEHR_LAT  = 50.843, 28.923   # Bushehr AB
    SHIRAZ_LON,  SHIRAZ_LAT   = 52.589, 29.547   # Shiraz missile brigade
    BANDAR_LON,  BANDAR_LAT   = 56.273, 27.218   # Bandar Abbas coastal battery

    def _ts(offset_s):
        h  = int(offset_s // 3600)
        m  = int((offset_s % 3600) // 60)
        s  = int(offset_s % 60)
        return f"2026-03-18T{6+h:02d}:{m:02d}:{s:02d}Z"

    # ── Blast radius circle generator ─────────────────────────────────────────
    def _circle_coords(lon, lat, radius_m, n_pts=60):
        """KML coordinate string for a circle polygon around (lon, lat)."""
        pts = []
        for i in range(n_pts + 1):
            angle = 2.0 * _math.pi * i / n_pts
            dlat  = (radius_m / 111_000.0) * _math.cos(angle)
            dlon  = (radius_m / (111_000.0 * _math.cos(_math.radians(lat)))) * _math.sin(angle)
            pts.append(f"{lon + dlon:.6f},{lat + dlat:.6f},0")
        return " ".join(pts)

    def _blast_rings_kml(lon, lat, warhead_kg, label, appear_time, is_oil_target=False):
        """Three concentric blast damage rings + optional oil-fire ring."""
        # Scale radii by Hopkinson-Cranz W^(1/3) relative to 450 kg reference
        scale = (warhead_kg / 450.0) ** (1.0 / 3.0)
        r_inner  = int(50  * scale)   # structural kill / crater
        r_mid    = int(150 * scale)   # significant damage
        r_outer  = int(300 * scale)   # overpressure / light damage
        r_fire   = 200                 # secondary oil fire (fixed radius)

        rings = []
        # Impact marker
        rings.append(f"""  <Placemark>
    <name>{label} — Impact</name>
    <TimeSpan><begin>{appear_time}</begin></TimeSpan>
    <styleUrl>#blast_impact</styleUrl>
    <Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point>
  </Placemark>""")
        # Inner: structural kill — red fill
        rings.append(f"""  <Placemark>
    <name>{label} — Structural Kill r≈{r_inner}m</name>
    <TimeSpan><begin>{appear_time}</begin></TimeSpan>
    <styleUrl>#blast_inner</styleUrl>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>{_circle_coords(lon, lat, r_inner)}</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")
        # Middle: significant damage — orange outline
        rings.append(f"""  <Placemark>
    <name>{label} — Significant Damage r≈{r_mid}m</name>
    <TimeSpan><begin>{appear_time}</begin></TimeSpan>
    <styleUrl>#blast_mid</styleUrl>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>{_circle_coords(lon, lat, r_mid)}</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")
        # Outer: overpressure — yellow outline
        rings.append(f"""  <Placemark>
    <name>{label} — Overpressure r≈{r_outer}m</name>
    <TimeSpan><begin>{appear_time}</begin></TimeSpan>
    <styleUrl>#blast_outer</styleUrl>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>{_circle_coords(lon, lat, r_outer)}</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")
        if is_oil_target:
            rings.append(f"""  <Placemark>
    <name>{label} — Secondary Oil Fire r≈{r_fire}m</name>
    <TimeSpan><begin>{appear_time}</begin></TimeSpan>
    <styleUrl>#blast_fire</styleUrl>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>{_circle_coords(lon, lat, r_fire)}</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>""")
        return "\n".join(rings)

    # ── Ballistic arc generator ────────────────────────────────────────────────
    def _ballistic_arc_kml(src_lon, src_lat, tgt_lon, tgt_lat, launch_s, flight_s,
                            style_id, label, n_segs=12):
        """Parabolic arc KML track from source to target."""
        peak_alt = 180_000.0  # ~180 km apogee for MRBM
        segs = []
        for k in range(n_segs + 1):
            frac    = k / n_segs
            # Linear interpolation in 2D
            lon_k   = src_lon + frac * (tgt_lon - src_lon)
            lat_k   = src_lat + frac * (tgt_lat - src_lat)
            alt_k   = peak_alt * 4 * frac * (1 - frac)   # parabolic altitude
            t_k     = launch_s + frac * flight_s
            segs.append(f"      <when>{_ts(t_k)}</when>\n"
                        f"      <gx:coord>{lon_k:.6f} {lat_k:.6f} {alt_k:.0f}</gx:coord>")
        track_body = "\n".join(segs)
        return (f"  <Placemark><name>{label}</name>"
                f"<styleUrl>#{style_id}</styleUrl>"
                f"<TimeSpan><begin>{_ts(launch_s)}</begin>"
                f"<end>{_ts(launch_s + flight_s + 120)}</end></TimeSpan>"
                f"<gx:Track><altitudeMode>absolute</altitudeMode>\n"
                f"{track_body}\n  </gx:Track></Placemark>")

    # ── Missile definitions ────────────────────────────────────────────────────
    # (name, src_lon, src_lat, tgt_lon, tgt_lat, launch_s, warhead_kg, speed_km_s,
    #  is_intercepted, is_oil_target, style_id)
    SPEED_SRBM = 3.0    # km/s terminal (Mach ~9)
    SPEED_MRBM = 4.5    # km/s terminal (Mach ~13)

    # Oil terminal (NW jetty): 50.315, 29.250
    # Storage tanks (central): 50.330, 29.252
    # Loading manifold (W): 50.318, 29.248
    # Pipeline junction (SE): 50.335, 29.244
    OIL_TARGETS = [
        (50.315, 29.250, "Oil Terminal NW Jetty",    True),
        (50.330, 29.252, "Oil Tank Farm Central",    True),
        (50.318, 29.248, "Pipeline Loading Manifold",True),
        (50.335, 29.244, "Pipeline Junction SE",     True),
    ]
    FLEET_TARGETS = [
        (LHA_LON, LHA_LAT, "USS Tripoli (LHA-7) — Flight Deck"),
        (LHA_LON + 0.01, LHA_LAT - 0.01, "USS Tripoli — Secondary Hit"),
        (DDG_LON, DDG_LAT, "DDG Escort — CIC Structure"),
        (DDG_LON + 0.005, DDG_LAT, "DDG Escort — VLS Magazine"),
        (LPD2_LON, LPD2_LAT, "LPD-29 — Well Deck"),
        (LPD1_LON, LPD1_LAT, "LPD-30 — Flight Deck"),
    ]

    missiles = []
    # Khalij Fars ASBM (8 rounds) — anti-ship, 450 kg, from Bushehr
    for idx, (tlon, tlat, tlbl) in enumerate(FLEET_TARGETS):
        dist = haversine_km(BUSHEHR_LON, BUSHEHR_LAT, tlon, tlat)
        flight = dist / SPEED_SRBM
        launch = 900 + idx * 60 + rng.uniform(-30, 30)   # T+15–25 min staggered
        intercepted = idx in {2, 3, 5}   # 3 of 6 fleet rounds intercepted
        missiles.append({
            "src_lon": BUSHEHR_LON, "src_lat": BUSHEHR_LAT,
            "tgt_lon": tlon, "tgt_lat": tlat,
            "launch_s": launch, "flight_s": flight, "warhead_kg": 450,
            "label": f"Khalij Fars #{idx+1} → {tlbl}",
            "style": "khalij_fars_track" if not intercepted else "ballistic_intercept_track",
            "intercepted": intercepted, "is_oil": False,
            "impact_label": tlbl,
        })
    # Fateh-313 SRBM (6 rounds) — oil terminal, 450 kg, from Shiraz
    for idx, (tlon, tlat, tlbl, oil) in enumerate(OIL_TARGETS[:3]):
        dist = haversine_km(SHIRAZ_LON, SHIRAZ_LAT, tlon, tlat)
        flight = dist / SPEED_SRBM
        launch = 960 + idx * 90 + rng.uniform(-20, 20)   # T+16–22 min
        intercepted = idx == 1   # 1 of 3 intercepted
        missiles.append({
            "src_lon": SHIRAZ_LON, "src_lat": SHIRAZ_LAT,
            "tgt_lon": tlon, "tgt_lat": tlat,
            "launch_s": launch, "flight_s": flight, "warhead_kg": 450,
            "label": f"Fateh-313 #{idx+1} → {tlbl}",
            "style": "fateh_track" if not intercepted else "ballistic_intercept_track",
            "intercepted": intercepted, "is_oil": oil,
            "impact_label": tlbl,
        })
    # Zolfaghar SRBM (4 rounds) — storage tanks, 450 kg, from Bushehr
    for idx, (tlon, tlat, tlbl, oil) in enumerate(OIL_TARGETS):
        dist = haversine_km(BUSHEHR_LON, BUSHEHR_LAT, tlon, tlat)
        flight = dist / SPEED_SRBM
        launch = 1020 + idx * 75 + rng.uniform(-20, 20)  # T+17–22 min
        intercepted = idx == 3   # 1 of 4 intercepted
        missiles.append({
            "src_lon": BUSHEHR_LON, "src_lat": BUSHEHR_LAT,
            "tgt_lon": tlon, "tgt_lat": tlat,
            "launch_s": launch, "flight_s": flight, "warhead_kg": 450,
            "label": f"Zolfaghar #{idx+1} → {tlbl}",
            "style": "zolfaghar_track" if not intercepted else "ballistic_intercept_track",
            "intercepted": intercepted, "is_oil": oil,
            "impact_label": tlbl,
        })
    # Emad MRBM (4 rounds) — mixed fleet + infrastructure, 750 kg, from Bandar Abbas
    emad_targets = [
        (LHA_LON, LHA_LAT - 0.008, "USS Tripoli — Portside Hull"),
        (LHA_LON + 0.006, LHA_LAT + 0.005, "USS Tripoli — Stern"),
        (50.328, 29.246, "Kharg Manifold Complex"),
        (50.322, 29.253, "Kharg Airstrip Terminal"),
    ]
    for idx, (tlon, tlat, tlbl) in enumerate(emad_targets):
        dist = haversine_km(BANDAR_LON, BANDAR_LAT, tlon, tlat)
        flight = dist / SPEED_MRBM
        launch = 1080 + idx * 120 + rng.uniform(-30, 30)  # T+18–26 min
        intercepted = idx in {0, 2}   # 2 of 4 intercepted
        missiles.append({
            "src_lon": BANDAR_LON, "src_lat": BANDAR_LAT,
            "tgt_lon": tlon, "tgt_lat": tlat,
            "launch_s": launch, "flight_s": flight, "warhead_kg": 750,
            "label": f"Emad MRBM #{idx+1} → {tlbl}",
            "style": "emad_track" if not intercepted else "ballistic_intercept_track",
            "intercepted": intercepted, "is_oil": "Kharg" in tlbl,
            "impact_label": tlbl,
        })

    # ── Build KML ─────────────────────────────────────────────────────────────
    kml_parts = [f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
  <name>Kharg Island — Iranian Ballistic Missile Strike</name>
  <description>22 Iranian ballistic missiles targeting US amphibious assault fleet and Kharg Island oil infrastructure. Blast-radius polygons show structural-kill (50–65m, red), significant-damage (150–185m, orange), and overpressure zones (300–380m, yellow). Secondary oil fires modeled at infrastructure hits.</description>
  <open>1</open>
  <LookAt>
    <longitude>50.33</longitude><latitude>29.10</latitude>
    <altitude>0</altitude><range>120000</range><tilt>45</tilt><heading>0</heading>
    <altitudeMode>relativeToGround</altitudeMode>
  </LookAt>

  <!-- Missile track styles -->
  <Style id="khalij_fars_track">
    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    <IconStyle><color>ff0000ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
  </Style>
  <Style id="fateh_track">
    <LineStyle><color>ff0044ff</color><width>2</width></LineStyle>
    <IconStyle><color>ff0044ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
  </Style>
  <Style id="zolfaghar_track">
    <LineStyle><color>ff0088ff</color><width>2</width></LineStyle>
    <IconStyle><color>ff0088ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
  </Style>
  <Style id="emad_track">
    <LineStyle><color>ff00aaff</color><width>3</width></LineStyle>
    <IconStyle><color>ff00aaff</color><scale>1.0</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
  </Style>
  <Style id="ballistic_intercept_track">
    <LineStyle><color>8800ff00</color><width>1</width></LineStyle>
    <IconStyle><color>8800ff00</color><scale>0.5</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_square.png</href></Icon>
    </IconStyle>
  </Style>
  <!-- Blast ring styles (AABBGGRR) -->
  <Style id="blast_impact">
    <IconStyle><color>ff0000ff</color><scale>1.2</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.8</scale></LabelStyle>
  </Style>
  <Style id="blast_inner">
    <!-- Structural kill: red fill, red outline -->
    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    <PolyStyle><color>660000ff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="blast_mid">
    <!-- Significant damage: orange outline only -->
    <LineStyle><color>ff0066ff</color><width>2</width></LineStyle>
    <PolyStyle><color>220066ff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="blast_outer">
    <!-- Overpressure: yellow outline only -->
    <LineStyle><color>ff00ccff</color><width>1</width></LineStyle>
    <PolyStyle><color>1100ccff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <Style id="blast_fire">
    <!-- Secondary oil fire: translucent red-orange fill -->
    <LineStyle><color>aa0055ff</color><width>1</width></LineStyle>
    <PolyStyle><color>550055ff</color><fill>1</fill><outline>1</outline></PolyStyle>
  </Style>
  <!-- Fleet marker styles -->
  <Style id="us_fleet_marker">
    <IconStyle><color>ff00ff00</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff00ff00</color><scale>0.7</scale></LabelStyle>
  </Style>
  <Style id="iran_site_kharg_marker">
    <IconStyle><color>ff0000ff</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon>
    </IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.7</scale></LabelStyle>
  </Style>
"""]

    # ── Launch sites ──────────────────────────────────────────────────────────
    kml_parts.append("  <Folder><name>Iranian Launch Sites</name><visibility>1</visibility>")
    for slon, slat, sname in [
        (BUSHEHR_LON, BUSHEHR_LAT, "Bushehr AB — Khalij Fars / Zolfaghar"),
        (SHIRAZ_LON,  SHIRAZ_LAT,  "Shiraz Missile Brigade — Fateh-313"),
        (BANDAR_LON,  BANDAR_LAT,  "Bandar Abbas — Emad MRBM Battery"),
    ]:
        kml_parts.append(
            f'  <Placemark><name>{sname}</name><styleUrl>#iran_site_kharg_marker</styleUrl>'
            f'<Point><coordinates>{slon:.6f},{slat:.6f},0</coordinates></Point></Placemark>')
    kml_parts.append("  </Folder>")

    # ── US fleet markers ──────────────────────────────────────────────────────
    kml_parts.append("  <Folder><name>US Amphibious Fleet</name><visibility>1</visibility>")
    for flon, flat, fname in [
        (LHA_LON,  LHA_LAT,  "USS Tripoli (LHA-7)"),
        (DDG_LON,  DDG_LAT,  "DDG Escort"),
        (LPD1_LON, LPD1_LAT, "LPD-30"),
        (LPD2_LON, LPD2_LAT, "LPD-29"),
    ]:
        kml_parts.append(
            f'  <Placemark><name>{fname}</name><styleUrl>#us_fleet_marker</styleUrl>'
            f'<Point><coordinates>{flon:.6f},{flat:.6f},0</coordinates></Point></Placemark>')
    kml_parts.append("  </Folder>")

    # ── Missile trajectories ───────────────────────────────────────────────────
    kml_parts.append("  <Folder><name>Ballistic Missile Trajectories</name><visibility>1</visibility>")
    for m in missiles:
        kml_parts.append(_ballistic_arc_kml(
            m["src_lon"], m["src_lat"], m["tgt_lon"], m["tgt_lat"],
            m["launch_s"], m["flight_s"], m["style"], m["label"]))
    kml_parts.append("  </Folder>")

    # ── Blast damage circles (breakthrough hits only) ──────────────────────────
    kml_parts.append("  <Folder><name>Blast Damage Zones</name><visibility>1</visibility>")
    n_hits = 0
    for m in missiles:
        if not m["intercepted"]:
            impact_t = _ts(m["launch_s"] + m["flight_s"])
            kml_parts.append(_blast_rings_kml(
                m["tgt_lon"], m["tgt_lat"], m["warhead_kg"],
                m["impact_label"], impact_t, m["is_oil"]))
            n_hits += 1
    kml_parts.append("  </Folder>")

    # ── Summary description folder ─────────────────────────────────────────────
    n_intercepted_count = sum(1 for m in missiles if m["intercepted"])
    kml_parts.append(
        f'  <Folder><name>Scenario Summary</name><visibility>0</visibility>'
        f'<description><![CDATA[<b>Kharg Island Ballistic Strike</b><br/>'
        f'22 Iranian ballistic missiles launched T+15–26 min into USMC assault.<br/>'
        f'<b>{n_intercepted_count}</b> intercepted (DDG SM-6 + Tripoli SeaRAM).<br/>'
        f'<b>{n_hits}</b> hits: {sum(1 for m in missiles if not m["intercepted"] and not m["is_oil"])} fleet '
        f'+ {sum(1 for m in missiles if not m["intercepted"] and m["is_oil"])} oil infrastructure.<br/>'
        f'Blast rings: red=structural kill, orange=significant damage, yellow=overpressure.<br/>'
        f'Orange fill = secondary oil fire (r≈200m).]]></description>'
        f'</Folder>')

    kml_parts.append("</Document>\n</kml>")
    kml_content = "\n".join(kml_parts)

    # ── Write KMZ ─────────────────────────────────────────────────────────────
    if out_dir is None:
        out_dir = _os.path.dirname(_os.path.abspath(__file__))
    out_path = _os.path.join(out_dir, "kharg_island_ballistic.kmz")
    with _zf.ZipFile(out_path, "w", _zf.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml_content.encode("utf-8"))

    return out_path, len(missiles), n_hits, n_intercepted_count


# ============================================================
# ENTRY POINT
# ============================================================

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out  = os.path.join(base, "output", "scenarios")
    os.makedirs(out, exist_ok=True)

    seeds = {"low": 42, "medium": 7, "high": 13, "realistic": 99,
             "iran_best": 77, "usa_best": 11,
             "drone_first_low": 55, "drone_first_medium": 66, "drone_first_high": 88,
             "coordinated_strike": 99,   # same seed as realistic for direct comparison
             "focused_salvo": 99, "hypersonic_threat": 99,  # comparable to realistic
             "ballistic_barrage": 33, "ascm_swarm": 44, "shore_based_defense": 99,
             "strait_transit": 99, "caves": 99,
             "depleted_drone_first": 42,
             "depleted_coastal": 42,
             "depleted_israel_split": 42,
             "us_win_preemption": 42,
             "us_win_ew_dominance": 42,
             "us_win_allied_umbrella": 42,
             "us_win_c2_disrupted": 42,
             "us_win_arsenal_attrition": 42,
             "one_percent_probe": 17,
             "one_percent_fatah2": 19,
             "ballistic_surge": 55}
    stats = {}
    all_costs = {}

    for scenario_key in ("low", "medium", "high", "realistic", "iran_best", "usa_best",
                         "drone_first_low", "drone_first_medium", "drone_first_high",
                         "coordinated_strike",
                         "focused_salvo", "hypersonic_threat", "ballistic_barrage",
                         "ascm_swarm", "shore_based_defense", "strait_transit", "caves",
                         "depleted_drone_first", "depleted_coastal", "depleted_israel_split",
                         "us_win_preemption", "us_win_ew_dominance", "us_win_allied_umbrella",
                         "us_win_c2_disrupted", "us_win_arsenal_attrition",
                         "one_percent_probe", "one_percent_fatah2",
                         "ballistic_surge"):
        print(f"  Generating {scenario_key} ...")
        kml_content, legend_states, n_launched, n_intercepted, n_breakthrough, duration_min, costs = \
            generate_scenario(scenario_key, seed=seeds[scenario_key], out_dir=out)

        # ── Write per-scenario KMZ (KML + dynamic legend images bundled) ──────
        import zipfile as _zf
        output_path = os.path.join(out, f"scenario_{scenario_key}.kmz")
        with _zf.ZipFile(output_path, "w", _zf.ZIP_DEFLATED) as zf:
            zf.writestr("doc.kml", kml_content.encode("utf-8"))
            for img_path, _, _ in legend_states:
                if os.path.exists(img_path):
                    zf.write(img_path, f"images/{os.path.basename(img_path)}")
        size_mb = os.path.getsize(output_path) / 1_048_576

        scenario_config = SCENARIOS[scenario_key]
        stats[scenario_key] = (scenario_config["label"], n_launched, n_intercepted, n_breakthrough, duration_min)
        all_costs[scenario_key] = costs
        png_path = generate_legend_png(scenario_key, scenario_config, costs, n_launched, n_intercepted, n_breakthrough, duration_min, out)
        if png_path:
            print(f"    legend -> {png_path}")

        def _fc(usd):
            return f"${usd/1e9:.2f}B" if usd >= 1e9 else f"${usd/1e6:.1f}M"

        intercept_by_category = costs["intercept_by_cat"]
        print(f"    {scenario_key}: {n_launched} launched | {n_intercepted} intercepted | {n_breakthrough} breakthrough | "
              f"~{duration_min:.0f} min | {size_mb:.1f} MB | {len(legend_states)} legend states -> {output_path}")
        print(f"      Iran offensive: {_fc(costs['iran_cost'])}"
              f" | US: {_fc(costs['us_intercept_cost'])} intercept"
              f" ({intercept_by_category['SM-6 / SM-2']} SM-6, {intercept_by_category['CIWS / SeaRAM']} CIWS, {intercept_by_category['Naval Gun / Phalanx']} NavGun)"
              f" + {_fc(costs['us_strike_cost'])} strikes"
              f" + {_fc(costs['us_ship_damage'])} ship/a/c damage"
              f" = {_fc(costs['total_us_cost'])} total | ratio {costs['exchange_ratio']:.1f}:1")
        print(f"      US casualties: {costs['us_mil_kia']:,} KIA / {costs['us_mil_wia']:,} WIA"
              f" | Civilian collateral: {_fc(costs['collateral_usd'])} / {costs['collateral_kia']:,} KIA")

    master = os.path.join(base, "output", "wargame_master.kml")
    with open(master, "w", encoding="utf-8") as fh:
        fh.write(generate_master(stats))
    print(f"  Master -> {master}")
    # ── Summary KMZ ───────────────────────────────────────────────────────────
    # Use the "realistic" scenario legend as the representative legend image
    legend_for_kmz = os.path.join(out, "legend_realistic.png")
    kmz_path = generate_summary_kmz(stats, all_costs, out, legend_for_kmz)
    print(f"  Summary KMZ -> {kmz_path}")
    html_files = generate_html_reports(stats, all_costs, out)
    print(f"  HTML reports -> {len(html_files)} files in {out}/")

    # ── Kharg Island air assault scenarios ─────────────────────────────────────
    for kharg_variant, kharg_label in (("north_west", "NW airstrip assault"),
                                        ("south_east",  "SE flanking assault")):
        print(f"  Generating kharg_island_assault [{kharg_label}] ...")
        kharg_path, n_waves, troops_wave, total_m, cycle_s = \
            generate_kharg_assault_kml(out, variant=kharg_variant)
        print(f"    {kharg_label}: {n_waves} waves × {troops_wave} Marines/wave "
              f"(~{cycle_s/60:.0f} min cycle) = {total_m:,} Marines total -> {kharg_path}")

    # ── Kharg Island ballistic missile strike scenario ───────────────────────
    print(f"  Generating kharg_island_ballistic ...")
    kharg_bal_path, n_bal_missiles, n_bal_hits, n_bal_int = \
        generate_kharg_ballistic_kml(out)
    print(f"    Ballistic strike: {n_bal_missiles} missiles | {n_bal_int} intercepted "
          f"| {n_bal_hits} hits (fleet + oil infrastructure) -> {kharg_bal_path}")

    print("Done.")


if __name__ == "__main__":
    main()
