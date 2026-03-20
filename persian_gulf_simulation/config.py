"""
config.py — ALL simulation constants for the Kharg Island simulation.

This is the single patchable module.  runner._patch_scenario() calls
setattr(cfg, name, value) on this module so that engine.py and factory.py
(which import this module as cfg) always see the current values at call time.

Import pattern that MUST be used by engine.py and factory.py:
    import persian_gulf_simulation.config as cfg
    ... cfg.IRGC_PK ...
"""

import math
import os

from persian_gulf_simulation.geography import (
    IRGC_POLY_BBOX, IRGC_POLYGON, CLUSTER_NAMES, GRID_CELL,
)

# ---------------------------------------------------------------------------
# CONSTANTS — LAND BATTLE
# ---------------------------------------------------------------------------

SEED    = 42
STEP_S  = 60
N_STEPS = 120

N_SQUADS  = 250
MARINE_HP = 4
IRGC_HP   = 4

# Sailors — ship crew who can be inserted as a last-resort wave when Marines
# are exhausted but Ospreys still have sortie capacity.
# 2,500 sailors across three ships, represented as 625 four-man groups.
# Lower HP and PK than Marines: sailors are not infantry-trained.
N_SAILORS  = 2500
SAILOR_HP  = 2       # less robust than Marines (4 HP)
SAILOR_PK  = 0.04    # ~36% of MARINE_PK — support personnel, not ground-combat infantry

ENGAGE_KM = 0.30

# Lanchester Square Law quality multiplier — USMC vs IRGC Ground Force.
# Derived from Dupuy's QJM (Quantified Judgment Model) calibrated to historical data:
#   Israel vs Egypt 1967: CEV = 1.75  (closest analog: Western-doctrine professional vs
#                                       Soviet-equipped conscript army)
#   Israel vs Egypt 1973: CEV = 1.98
#   Adjusted down to 1.6 for IRGC's ideological cohesion, proxy-war experience, and
#   defensive terrain familiarity; consistent with Chosin/Fallujah implied ranges (1.3–2.0).
#   Low bound: 1.3 (urban/prepared terrain); high: 2.0 (maneuver, night ops, air support).
# Source: Trevor Dupuy, "Numbers, Predictions and War" (1979); Dupuy Institute CEV studies.
LANCHESTER_Q = 1.6   # USMC individual-unit quality relative to IRGC squad

IRGC_PK   = 0.07                       # P(IRGC deals 1 HP to marine) per squad per step
MARINE_PK = round(IRGC_PK * LANCHESTER_Q, 4)  # = 0.112 — derived, not hand-tuned

# Positional/terrain defensive bonus — kept separate from quality per Dupuy's model.
# Prepared island positions with interlocking fields of fire; 2.5x is consistent with
# Dupuy's terrain multipliers for fortified defensive positions.
IRGC_DEFENSE_MULT   = 2.5
IRGC_HOME_RADIUS_KM = 0.9

STINGER_RATIO    = 0.05   # 5 % of total IRGC carry MANPADS
STINGER_MAX_TEAMS = 100   # hard cap regardless of IRGC count
N_STINGER_TEAMS  = min(STINGER_MAX_TEAMS, max(1, round(STINGER_RATIO * N_SQUADS)))
STINGER_RELOAD_STEPS = 1   # steps a team must wait after firing (~1 min) before next shot
STINGER_WEZ_KM   = 4.5
STINGER_PK       = 0.25   # P(kill) vs outbound / inbound Osprey
STINGER_HOVER_PK = 0.75   # P(kill) vs Osprey hovering at LZ (drop window)
STINGER_HP       = 2

LZ_DROP_WINDOW_S   = 30    # seconds Osprey hovers while deploying marines (display only)
LZ_HOVER_RADIUS_KM = 0.30  # visual hover-zone circle radius around each LZ

# ---------------------------------------------------------------------------
# EW / IO FACTORS  (JP 3-13 Information Ops · JP 3-13.1 Electronic Warfare
#                   JP 3-85 Joint EMS Ops · JP 3-09 Joint Fire Support)
# ---------------------------------------------------------------------------
# All multipliers default to 1.0 (no EW effect).  Override via _patch_scenario.
#
# Doctrine basis (unclassified / open-source derived values):
#   JP 3-13.1:  DIRCM AN/AAQ-24 → 85–95% MANPADS defeat → EW_MANPADS_PK_MULT ≈ 0.10
#   JP 3-13.1:  Sustained COMJAM on HF/VHF nets → C2 effectiveness 40–60% →
#               EW_IRGC_PK_MULT = 0.50, EW_IRGC_DEFENSE_MULT_ADJ = 0.50
#   JP 3-13:    MILDEC (false landing site) → 30% defenders misdirected, ~20 min delay
#   JP 3-85:    GPS denial (IRGC ground jammers 50–200 km) → JDAM CEP 5–13 m → 30–50 m
#               Applied to pre-strike via higher pre_strike_survival_pct (8% → 22%)
#   JP 3-85:    Iranian ECM on ship SAM radar → SHIP_SAM_PK × 0.70
#   JP 3-13.1:  GPS spoofing on Shahed datalink → 30% mission abort rate
#   Source: RAND EW studies; CNA "Electronic Warfare in Modern Conflict" (2019);
#           IEEE EW handbook; RQ-170 GPS spoof incident (2011) open-source analysis.

EW_IRGC_PK_MULT          = 1.0  # COMJAM on IRGC tactical nets (0.50 = heavy sustained)
EW_IRGC_DEFENSE_MULT_ADJ = 1.0  # C2 disruption reduces positional bonus (0.50 = heavy)
EW_MANPADS_PK_MULT        = 1.0  # DIRCM/SPJ on Ospreys (0.10 = DIRCM equipped, 90% defeat)
EW_MILDEC_FRACTION        = 0.0  # Fraction of IRGC misdirected by MILDEC (0.30 = typical)
EW_MILDEC_DELAY_STEPS     = 0    # Steps before misdirected IRGC re-engage (20 = ~20 min)
EW_SHAHED_ABORT_RATE      = 0.0  # GPS-spoofed Shahed/island-Shahed abort fraction (0.30)
EW_SHIP_SAM_PK_MULT       = 1.0  # Iran ECM on US SAM radar (0.70 = contested EMS)

# ---------------------------------------------------------------------------
# KML ALTITUDE CONSTANTS  (relativeToGround, metres AGL)
# ---------------------------------------------------------------------------
# MV-22B Osprey — nap-of-earth assault profile
OSPREY_TRANSIT_ALT_M = 150    # cruise to/from LZ (~500 ft AGL, typical NOE)
OSPREY_DROP_ALT_M    = 30     # hover at LZ during troop offload (~100 ft)
# MQ-9 Reaper — medium-altitude loiter
REAPER_ALT_M         = 4_500  # ~15 000 ft AGL
# Shahed-136 — terrain-following low-level cruise
SHAHED_ALT_M         = 75     # ~250 ft AGL
# IRGCN FIAC drone boats — sea surface (tiny offset for KML visibility)
DBOAT_ALT_M          = 3

# Stinger arc geometry (end-point = OSPREY_TRANSIT_ALT_M, peak above that)
OSPREY_ALT_M           = OSPREY_TRANSIT_ALT_M  # alias used by arc code
STINGER_ARC_PEAK_M     = 400   # extra height above Osprey at arc apex
STINGER_ARC_SECS       = 10    # seconds each missile arc stays visible
NARRATION_DISPLAY_STEPS = 4    # steps each narration event stays visible
DEATH_RISE_STEPS = 6           # sim-steps over which dead icon rises (soul effect)
DEATH_RISE_ALT_M = 1000        # peak altitude for rising dead icon (metres)

MV22_CAPACITY      = 6
OSPREYS_PER_SORTIE = 20
OSPREY_LOAD_STEPS  = 2
OSPREY_DROP_STEPS  = 1

N_US_DRONES       = 6
DRONE_HELLFIRE    = 4
DRONE_PK          = 0.85
DRONE_ARRIVE_STEP = 8
DRONE_SPEED_KPS   = 480.0 / 3600
DRONE_LAUNCH_LON  = 50.32
DRONE_LAUNCH_LAT  = 28.90

OSPREY_KPS = 450.0 / 3600
MARCH_KPS  =   5.0 / 3600
IRGC_KPS   =   3.0 / 3600

LAT_KM = 111.0
LON_KM = 111.0 * math.cos(math.radians(29.26))

TRIPOLI_LON = 50.3285
TRIPOLI_LAT = 28.898

LZ_FALCON = (50.305, 29.248)
LZ_EAGLE  = (50.32394865263289, 29.257935589364)
LZ_VIPER  = (50.31859357253797, 29.22879777085731)
LZ_COBRA  = (50.312, 29.220)
LZS       = [LZ_FALCON, LZ_EAGLE, LZ_VIPER, LZ_COBRA]
LZ_NAMES  = {LZ_FALCON: "FALCON", LZ_EAGLE: "EAGLE",
             LZ_VIPER:  "VIPER",  LZ_COBRA:  "COBRA"}


def _one_way_steps(lz):
    d = math.sqrt(
        ((lz[1] - TRIPOLI_LAT) * LAT_KM) ** 2
        + ((lz[0] - TRIPOLI_LON) * LON_KM) ** 2
    )
    return math.ceil(d / (OSPREY_KPS * STEP_S))


_SORTIE_CYCLE = max(
    _one_way_steps(lz) * 2 + OSPREY_DROP_STEPS + OSPREY_LOAD_STEPS
    for lz in LZS
)

_SORTIE_TEAMS = [120, 120, 120, 120, 120, 25]
_N_SORTIES    = len(_SORTIE_TEAMS)

MARINE_WAVES = []
N_TEAMS = 0
for _si, _n in enumerate(_SORTIE_TEAMS):
    _step = _si * _SORTIE_CYCLE
    _base, _rem = divmod(_n, len(LZS))
    for _i, _lz in enumerate(LZS):
        _cnt = _base + (1 if _i < _rem else 0)
        if _cnt > 0:
            MARINE_WAVES.append((_step, _cnt, _lz))
    N_TEAMS += _n

DRONE_ORBITS = [
    (50.314, 29.265), (50.330, 29.258), (50.350, 29.256),
    (50.353, 29.232), (50.325, 29.217), (50.305, 29.242),
]

IRGC_CLUSTERS = [
    (50.314, 29.265, 55, 0.011),
    (50.323, 29.254, 50, 0.009),
    (50.337, 29.247, 65, 0.016),
    (50.327, 29.220, 40, 0.010),
    (50.350, 29.252, 40, 0.008),
]

# ---------------------------------------------------------------------------
# CONSTANTS — MARITIME THREATS
# ---------------------------------------------------------------------------

# IRGCN Fast Inshore Attack Craft (FIAC) drone boats
N_DRONE_BOATS     = 50
DBOAT_SPEED_KPS   = 45.0 * 1.852 / 3600   # 45 knots → ~0.0231 km/s
DBOAT_HP          = 2
DBOAT_LAUNCH_LON  = 50.88
DBOAT_LAUNCH_LAT  = 29.08
DBOAT_SPREAD_DEG  = 0.12

# Shahed-136 / Geran-2 loitering munitions
N_SHAHED          = 50
SHAHED_SPEED_KPS  = 185.0 / 3600          # ~0.0514 km/s (185 km/h)
SHAHED_HP         = 1
SHAHED_LAUNCH_LON = 52.00
SHAHED_LAUNCH_LAT = 28.90
SHAHED_SPREAD_LON = 0.90
SHAHED_SPREAD_LAT = 0.50

# ---------------------------------------------------------------------------
# CONSTANTS — IRANIAN RETALIATION (post-F-35 beach assault)
# ---------------------------------------------------------------------------
# Fateh-110 SRBM (CEP ~10 m, 450 kg warhead) + Zelzal-2 (CEP ~200 m, 600 kg)
# launched from IRGC Bandar Abbas missile complex, ~150 km SE of Kharg Island.
# SM-3 Block IA single-shot Pk vs SRBM ~0.28 (DTRA / CBO 2019 unclassified).
# Each defending ship fires one intercept shot per inbound BM within SM-3 range.
#
# 100 SRBMs = ~4% of Iran's reconstituted post-2025-war stockpile (~2,500 SRBMs as of Feb 2026,
# per Alma Research / 19FortyFive).  Scenario-scaled retaliatory salvo: staggered across 10
# launch steps (10 missiles/step) to visualise rolling wave rather than instantaneous salvo.
N_IRAN_BM            = 100    # total SRBM salvo — staggered 10/step over 10 steps
IRAN_BM_SALVO_STEP   = 50     # step at which salvo launches (H+50 min post beach assault)
IRAN_BM_FLIGHT_STEPS = 8      # ballistic flight time in sim steps (~8 min, Bandar Abbas→Kharg)
IRAN_BM_LETHAL_M     = 110    # lethal radius (m) against dispersed infantry in open/light cover
IRAN_BM_CEP_FATEH_M  = 10     # Fateh-313 CEP (m) — laser/GPS terminal guidance (CBO 2019)
IRAN_BM_CEP_ZOLFAGHAR_M = 30  # Zolfaghar CEP (m) — inertial + GPS (IISS 2024 estimate)
IRAN_BM_INTERCEPT_PK = 0.28   # P(kill BM) per SM-3/SM-6 shot per defending ship
IRAN_BM_PEAK_ALT_M   = 75_000  # default arc apogee — Fateh-313 SRBM (~75 km)

# Multi-site launch table — coordinates match CSG scenario IRAN_SITES dict exactly.
# Each entry: (lon, lat, site_name, peak_alt_m, fraction_of_salvo)
# Missile types and altitudes match generate_wargame_kml.py MUNITIONS dict:
#   Fateh-313 SRBM  → 75,000 m  (red-orange,  KML cc0055ff)  ~500 km range
#   Zolfaghar SRBM  → 130,000 m (orange-red,  KML cc0066ff)  ~700 km range
IRAN_BM_SITES = [
    (52.589, 29.547, "Shiraz Missile Brigade",  75_000, 0.40),   # Fateh-313 SRBM
    (50.843, 28.923, "Bushehr AB",               75_000, 0.20),   # Fateh-313 SRBM
    (56.273, 27.218, "Bandar Abbas Complex",    130_000, 0.40),   # Zolfaghar SRBM
]

N_ISLAND_SHAHED          = 100 # Shahed-136 loitering munitions targeting island marine positions
ISLAND_SHAHED_SALVO_STEP = 55  # launches 5 steps after BMs (drone assembly / launch lag)

# Shahed-136 warhead / guidance parameters for KML impact visualization
SHAHED_LETHAL_M = 30   # lethal radius (m) against dispersed infantry (36 kg HE warhead)
SHAHED_CEP_M    = 50   # GPS navigation CEP (m) — accuracy envelope around target LZ

# ---------------------------------------------------------------------------
# AI-CAPABLE DRONE PARAMETERS
# ---------------------------------------------------------------------------
# Minimum 2.5% of every Shahed swarm is AI-guided.  AI drones use computer-vision
# target tracking and terrain-following routing, giving them two distinct advantages:
#   1. Survivability: SAM Pk reduced to 30% of baseline (guidance spoofing + evasive
#      routing makes intercept geometry harder).
#   2. Lethality: when an AI drone reaches its target it deals 2× ship damage (precision
#      fuze timing / hull-strike aiming) and has 2× lethal radius vs infantry (optimal
#      burst-height detonation).
# Floor of 2.5% reflects assessed IRGC fielding as of 2024.
# Sources: RAND "Countering AI-enabled UAS" (2023); CNAS "AI Autonomy in Drone Swarms" (2024).
AI_DRONE_FRACTION    = 0.025  # minimum fraction of Shahed/island-Shahed marked AI
AI_DRONE_SAM_PK_MULT = 0.30   # SAM Pk multiplier vs AI drones (70% harder to intercept)
AI_DRONE_SHIP_DMG    = 2      # HP damage dealt to ship by one AI drone hit (vs 1 for normal)
AI_DRONE_LETHAL_KM   = 0.060  # lethal radius vs infantry for AI drone (60 m, vs 30 m normal)

# US ship defence
SHIP_SAM_RANGE_KM = 12.0   # SAM / ESSM engages Shahed
SHIP_SAM_PK       = 0.40   # P(kill Shahed) per step in WEZ
SHIP_GUN_RANGE_KM = 5.0    # CIWS / 57mm deck gun vs drone boats
SHIP_GUN_PK       = 0.60   # P(kill drone boat) per step in range
SHIP_IMPACT_KM    = 0.20   # detonation/ramming range

# US ship definitions: (agent_id, lon, lat, hp, display_name, hull_class)
SHIP_DEFS = [
    ("SHIP_TRIPOLI",   TRIPOLI_LON, TRIPOLI_LAT,   6, "USS Tripoli (LHA-7)",   "America-class LHA"),
    ("SHIP_SAN_DIEGO", 50.475,      28.690,        4, "USS San Diego (LPD-29)","San Antonio-class LPD"),
    ("SHIP_BOULDER",   50.175,      28.690,        4, "USS Boulder (LPD-30)",  "San Antonio-class LPD"),
]
SHIP_MAX_HP   = {s[0]: s[3] for s in SHIP_DEFS}
SHIP_NAMES    = {s[0]: s[4] for s in SHIP_DEFS}
SHIP_CLASSES  = {s[0]: s[5] for s in SHIP_DEFS}

SIM_DATE   = "2026-03-26"
SIM_BASE_H = 0   # midnight local / Zulu start

OUT_KMZ = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "scenarios", "kharg_island_simulation.kmz")
