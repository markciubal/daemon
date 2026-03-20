"""
runner.py — _patch_scenario, _run_scenario, and main() entry point.

_patch_scenario patches persian_gulf_simulation.config as a module so that
run_simulation() and factory functions (which import config as cfg) always
see the new values.
"""

import contextlib
import math
import os
import random
import zipfile

import persian_gulf_simulation.config as cfg
from persian_gulf_simulation.agents.factory import (
    init_marines, init_irgc, init_stingers, init_ospreys,
    init_drones, init_ships, init_drone_boats, init_shahed,
    init_iran_bm, init_sailors,
)
from persian_gulf_simulation.simulation.engine import run_simulation
from persian_gulf_simulation.kml.document import gen_kml
from persian_gulf_simulation.kml.descriptions import (
    _f35_strike_battle_desc, _iran_retaliation_desc,
)


@contextlib.contextmanager
def _patch_scenario(n_irgc=None, osprey_drop_steps=None,
                    stinger_pk=None, stinger_hover_pk=None, stinger_wez_km=None,
                    n_drone_boats=None, n_shahed=None, n_island_shahed=None,
                    ai_drone_fraction=None,
                    beach_assault=False,
                    ew_irgc_pk_mult=None, ew_irgc_defense_mult_adj=None,
                    ew_manpads_pk_mult=None, ew_mildec_fraction=None,
                    ew_mildec_delay_steps=None, ew_shahed_abort_rate=None,
                    ew_ship_sam_pk_mult=None):
    """Temporarily override scenario-specific globals then restore them."""
    mod = cfg
    saved = {}

    def _set(name, val):
        saved[name] = getattr(mod, name)
        setattr(mod, name, val)

    base_n = sum(c[2] for c in cfg.IRGC_CLUSTERS)

    if n_irgc is not None and n_irgc != base_n:
        scale = n_irgc / base_n
        _set("IRGC_CLUSTERS", [(lon, lat, max(1, round(n * scale)), sp)
                                for lon, lat, n, sp in cfg.IRGC_CLUSTERS])
        _set("N_SQUADS", n_irgc)
        _set("N_STINGER_TEAMS", min(cfg.STINGER_MAX_TEAMS, max(1, round(cfg.STINGER_RATIO * n_irgc))))

    if osprey_drop_steps is not None and osprey_drop_steps != cfg.OSPREY_DROP_STEPS:
        _set("OSPREY_DROP_STEPS", osprey_drop_steps)
        _set("LZ_DROP_WINDOW_S", osprey_drop_steps * cfg.STEP_S)
        new_cycle = max(
            cfg._one_way_steps(lz) * 2 + osprey_drop_steps + cfg.OSPREY_LOAD_STEPS
            for lz in cfg.LZS
        )
        _set("_SORTIE_CYCLE", new_cycle)
        new_waves = []
        for _si, _n in enumerate(cfg._SORTIE_TEAMS):
            _step = _si * new_cycle
            _base, _rem = divmod(_n, len(cfg.LZS))
            for _i, _lz in enumerate(cfg.LZS):
                _cnt = _base + (1 if _i < _rem else 0)
                if _cnt > 0:
                    new_waves.append((_step, _cnt, _lz))
        _set("MARINE_WAVES", new_waves)

    if stinger_pk is not None:
        _set("STINGER_PK", stinger_pk)
    if stinger_hover_pk is not None:
        _set("STINGER_HOVER_PK", stinger_hover_pk)
    if stinger_wez_km is not None:
        _set("STINGER_WEZ_KM", stinger_wez_km)

    if n_drone_boats is not None:
        _set("N_DRONE_BOATS", n_drone_boats)
    if n_shahed is not None:
        _set("N_SHAHED", n_shahed)
    if n_island_shahed is not None:
        _set("N_ISLAND_SHAHED", n_island_shahed)
    if ai_drone_fraction is not None:
        _set("AI_DRONE_FRACTION", ai_drone_fraction)

    if ew_irgc_pk_mult is not None:
        _set("EW_IRGC_PK_MULT", ew_irgc_pk_mult)
    if ew_irgc_defense_mult_adj is not None:
        _set("EW_IRGC_DEFENSE_MULT_ADJ", ew_irgc_defense_mult_adj)
    if ew_manpads_pk_mult is not None:
        _set("EW_MANPADS_PK_MULT", ew_manpads_pk_mult)
    if ew_mildec_fraction is not None:
        _set("EW_MILDEC_FRACTION", ew_mildec_fraction)
    if ew_mildec_delay_steps is not None:
        _set("EW_MILDEC_DELAY_STEPS", ew_mildec_delay_steps)
    if ew_shahed_abort_rate is not None:
        _set("EW_SHAHED_ABORT_RATE", ew_shahed_abort_rate)
    if ew_ship_sam_pk_mult is not None:
        _set("EW_SHIP_SAM_PK_MULT", ew_ship_sam_pk_mult)

    if beach_assault:
        # Beach landing: LCAC/RHIB drop marines directly at LZs from step 0.
        # Use near-instant transit (1 step) so all marines are ashore by step ~2.
        _set("OSPREY_KPS", 9999.0 / 3600)
        _set("OSPREY_LOAD_STEPS", 0)
        _set("OSPREY_DROP_STEPS", 0)
        instant_cycle = max(
            cfg._one_way_steps(lz) * 2 + 0 + 0
            for lz in cfg.LZS
        )
        _set("_SORTIE_CYCLE", instant_cycle)
        new_waves = []
        for _si, _n in enumerate(cfg._SORTIE_TEAMS):
            _step = _si * instant_cycle
            _base, _rem = divmod(_n, len(cfg.LZS))
            for _i, _lz in enumerate(cfg.LZS):
                _cnt = _base + (1 if _i < _rem else 0)
                if _cnt > 0:
                    new_waves.append((_step, _cnt, _lz))
        _set("MARINE_WAVES", new_waves)

    try:
        yield
    finally:
        for name, val in saved.items():
            setattr(mod, name, val)


def _run_scenario(out_kmz, scenario_label="Kharg Island Assault",
                  pre_strike_survival_pct=None, n_irgc_pre=None,
                  iran_retaliation=True, scenario_desc=None):
    rng = random.Random(cfg.SEED)

    print("Initialising agents ...")
    marines,  flights              = init_marines(rng)
    irgc,     irgc_homes, irgc_cm = init_irgc(rng)
    stingers                       = init_stingers(rng)
    drones                         = init_drones(rng)
    ships                          = init_ships()
    drone_boats                    = init_drone_boats(rng, ships)
    shahed_drones                  = init_shahed(rng, ships)
    sailors                        = init_sailors(rng)
    iran_bm_agents      = init_iran_bm(rng)                          if iran_retaliation else None
    island_sh_agents    = init_shahed(rng, None, prefix="IS")         if iran_retaliation else None
    if iran_retaliation:
        print(f"  {cfg.N_IRAN_BM} Iranian SRBMs  |  {cfg.N_ISLAND_SHAHED} island-targeting Shahed-136")

    flight_lz_center = {}
    flight_total = 0
    for launch_step, n_teams, lz in cfg.MARINE_WAVES:
        n_fl = math.ceil(n_teams / cfg.MV22_CAPACITY)
        for fid in range(flight_total, flight_total + n_fl):
            flight_lz_center[fid] = lz
        flight_total += n_fl

    ospreys, osprey_trips = init_ospreys(rng, flights, flight_lz_center)

    n_flights = max(flights.keys()) + 1 if flights else 0
    cycle_min = cfg._SORTIE_CYCLE * cfg.STEP_S // 60
    print(f"  {len(marines)} Marine fireteams in {n_flights} Osprey flights")
    print(f"  {cfg.OSPREYS_PER_SORTIE} MV-22s | cycle {cfg._SORTIE_CYCLE} steps ({cycle_min} min)")
    print(f"  {len(irgc)} IRGC | {len(stingers)} Stingers | {len(drones)} Reapers")
    print(f"  {cfg.N_DRONE_BOATS} IRGCN drone boats | {cfg.N_SHAHED} Shahed-136 drones")
    print(f"  {len(ships)} US ships  (SAM Pk={cfg.SHIP_SAM_PK}, gun Pk={cfg.SHIP_GUN_PK})")
    print(f"  {cfg.N_SAILORS} sailors ({len(sailors)} groups, Pk={cfg.SAILOR_PK}) — fallback wave")

    print("Running simulation ...")
    sim_stats = run_simulation(
        marines, flights, flight_lz_center,
        irgc, irgc_homes,
        stingers,
        ospreys, osprey_trips,
        drones,
        ships, drone_boats, shahed_drones,
        rng,
        pre_strike_survival_pct=pre_strike_survival_pct,
        iran_bm=iran_bm_agents,
        island_shahed=island_sh_agents,
        sailors=sailors,
    )
    stinger_kills = sim_stats["stinger_kills"]

    # ---- Outcome ---
    alive_marines  = sum(1 for m in marines    if m.hp > 0)
    alive_irgc     = sum(1 for s in irgc       if s.hp > 0)
    alive_stingers = sum(1 for s in stingers   if s.hp > 0)
    kia_marines    = len(marines) - alive_marines
    kia_irgc       = len(irgc)    - alive_irgc

    destroyed_ospreys = sum(1 for ov in ospreys if ov.hp <= 0)
    total_drone_kills = sum(sim_stats["drone_kill_count"].values())
    total_ship_hits   = (sum(sim_stats["ship_db_hits"].values()) +
                         sum(sim_stats["ship_sh_hits"].values()))

    print("\n=== BATTLE OUTCOME SUMMARY ===")
    print(f"  LAND  — Marines alive    : {alive_marines}/{len(marines)} "
          f"fireteams  ({alive_marines*4} men)")
    print(f"  LAND  — IRGC neutralized : {kia_irgc}/{len(irgc)} squads")
    print(f"  LAND  — Ospreys lost     : {destroyed_ospreys}/{cfg.OSPREYS_PER_SORTIE}")
    print(f"  LAND  — Drone kills      : {total_drone_kills} IRGC")
    print(f"  SEA   — Ship hits total  : {total_ship_hits}")
    for s in ships:
        sid = s.agent_id
        status = "SUNK" if s.hp <= 0 else f"HP {s.hp}/{cfg.SHIP_MAX_HP[sid]}"
        db_h = sim_stats["ship_db_hits"].get(sid, 0)
        sh_h = sim_stats["ship_sh_hits"].get(sid, 0)
        print(f"    {cfg.SHIP_NAMES[sid]:<30s}: {status}  "
              f"(boats: {db_h}  Shahed: {sh_h})")
    print(f"  SEA   — Drone boats down : {sim_stats['db_shot_down']}/{cfg.N_DRONE_BOATS}")
    print(f"  SEA   — Shahed down      : {sim_stats['sh_shot_down']}/{cfg.N_SHAHED}")
    if sim_stats["sorties_cancelled"] or sim_stats["navy_dead"]:
        slk = len(sim_stats["ship_loss_kills"])
        print(f"  SEA   — Sorties cancelled: {sim_stats['sorties_cancelled']} flights "
              f"({slk} marines KIA — ship sunk)")
        if sim_stats["navy_dead"]:
            print(f"  SEA   — Navy crew KIA    : {sim_stats['navy_dead']} personnel")

    if sim_stats.get("sailors_deployed", 0):
        sd = sim_stats["sailors_deployed"]
        sk = sim_stats.get("sailor_dead", 0)
        print(f"  SEA   — Sailors deployed : {sd} groups ({sd * 4} personnel) — Marine fallback")
        print(f"  SEA   — Sailors KIA      : {sk} groups ({sk * 4} personnel)")

    island_held = alive_irgc == 0 and alive_stingers == 0
    sunk = [cfg.SHIP_NAMES[s.agent_id] for s in ships if s.hp <= 0]
    if island_held and not sunk:
        print("  OUTCOME: USMC secured Kharg Island — fleet intact")
    elif island_held:
        print(f"  OUTCOME: USMC secured Kharg Island — SHIPS LOST: {', '.join(sunk)}")
    elif alive_marines == 0:
        print("  OUTCOME: IRGC repelled the assault")
    else:
        print("  OUTCOME: Contested")

    print("\nGenerating KML ...")
    extra_desc = None
    _n_pre = n_irgc_pre if n_irgc_pre is not None else cfg.N_SQUADS
    if iran_retaliation and pre_strike_survival_pct is not None:
        extra_desc = _iran_retaliation_desc(
            marines, irgc, stingers, ospreys, ships,
            iran_bm_agents, island_sh_agents, sim_stats,
            survival_pct=pre_strike_survival_pct,
            n_irgc_pre=_n_pre,
            scenario_label=scenario_label,
            scenario_desc=scenario_desc,
        )
    elif pre_strike_survival_pct is not None:
        extra_desc = _f35_strike_battle_desc(
            marines, irgc, stingers, ospreys, ships, sim_stats,
            survival_pct=pre_strike_survival_pct,
            n_irgc_pre=_n_pre,
            scenario_label=scenario_label,
            scenario_desc=scenario_desc,
        )
    kml_str, extra_files = gen_kml(
        marines, irgc, stingers, ospreys, drones,
        ships, drone_boats, shahed_drones,
        sim_stats, irgc_cm, flights,
        sim_stats["stinger_shots"],
        scenario_label=scenario_label,
        extra_doc_desc=extra_desc,
        iran_bm=iran_bm_agents,
        island_shahed=island_sh_agents,
        scenario_desc=scenario_desc,
    )

    os.makedirs(os.path.dirname(out_kmz), exist_ok=True)
    print(f"Writing {out_kmz} ...")
    with zipfile.ZipFile(out_kmz, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("doc.kml", kml_str.encode("utf-8"))
        for path, data in extra_files.items():
            zf.writestr(path, data)

    kml_bytes = len(kml_str.encode("utf-8"))
    kmz_bytes = os.path.getsize(out_kmz)
    print(f"  KML size : {kml_bytes/1024:.1f} KB")
    print(f"  KMZ size : {kmz_bytes/1024:.1f} KB")
    print("Done.")


def build_scenarios():
    """Return the ordered list of scenario 4-tuples: (label, overrides, filename, description).
    Called by both main() and daemon.py so the scenario table is defined in one place."""
    # MANPADS performance parameters:
    #   FIM-92 Stinger (US baseline): Pk=0.25/0.75, WEZ=4.5 km
    #   9K38 Igla-S  SA-24 (Russia): Pk=0.35/0.80, WEZ=6.0 km  — dual-channel IR/UV seeker, higher off-boresight
    #   9K333 Verba  SA-25 (Russia): Pk=0.52/0.88, WEZ=6.4 km  — 3-channel seeker, ECCM-resistant
    #   QW-2         (China):        Pk=0.30/0.72, WEZ=5.0 km  — proportional navigation, IIR seeker
    #   FN-6 HY-6    (China):        Pk=0.42/0.82, WEZ=5.5 km  — passive IR + rosette scanning

    _igla_s  = dict(stinger_pk=0.35, stinger_hover_pk=0.80, stinger_wez_km=6.0)
    _verba   = dict(stinger_pk=0.52, stinger_hover_pk=0.88, stinger_wez_km=6.4)
    _qw2     = dict(stinger_pk=0.30, stinger_hover_pk=0.72, stinger_wez_km=5.0)
    _fn6     = dict(stinger_pk=0.42, stinger_hover_pk=0.82, stinger_wez_km=5.5)

    _degraded = dict(stinger_pk=round(0.25 * 0.10, 4), stinger_hover_pk=round(0.75 * 0.10, 4))

    # F-35 lightning strike scenario: 250 IRGC at full strength, 8% survive the pre-strike.
    # Drone boats and Shahed also degraded to 8%.  Beach assault, no MANPADS threat.
    _f35_overrides = dict(
        stinger_pk=0.0, stinger_hover_pk=0.0,   # MANPADS destroyed in strike
        n_drone_boats=4, n_shahed=4,             # 8% of 50 surviving
        beach_assault=True,                      # LCAC insertion, no Osprey transit
    )
    # Iranian retaliation: same F-35 pre-strike, then Iran launches SRBM + island Shahed
    _f35_retaliation_overrides = dict(
        stinger_pk=0.0, stinger_hover_pk=0.0,
        n_drone_boats=4, n_shahed=4,
        beach_assault=True,
        iran_retaliation=True,                   # triggers SRBM + island Shahed at H+50/55
    )

    # EW / IO scenarios (JP 3-13 · JP 3-13.1 · JP 3-85 · JP 3-09)
    # US EW Dominance: DIRCM on Ospreys (90% MANPADS defeat) + COMJAM on IRGC nets (50%)
    #                  + MILDEC (30% defenders misdirected for ~20 steps)
    _ew_dominance = dict(
        ew_manpads_pk_mult=0.10,        # AN/AAQ-24 DIRCM: 85-95% defeat rate
        ew_irgc_pk_mult=0.50,           # COMJAM on IRGC tactical nets
        ew_irgc_defense_mult_adj=0.60,  # C2 disruption reduces defensive bonus
        ew_mildec_fraction=0.30,        # MILDEC: 30% of IRGC misdirected
        ew_mildec_delay_steps=20,       # ~20 min before re-engage
    )
    # Contested EMS: US EW dominance + Iranian counter-EW (ECM on US SAMs, GPS jamming)
    _contested_ems = dict(
        **_ew_dominance,
        ew_shahed_abort_rate=0.25,      # partial GPS spoofing on Shahed
        ew_ship_sam_pk_mult=0.80,       # Iran ECM degrades US ship SAM pk
    )
    # F-35 strike with GPS jamming: pre-strike CEP degrades, fewer IRGC killed → 22% survive
    _f35_gps_jammed = dict(
        stinger_pk=0.0, stinger_hover_pk=0.0,
        n_drone_boats=11, n_shahed=11,  # ~22% of 50
        beach_assault=True,
        pre_strike_survival_pct=0.22,   # GPS jamming → INS-only → wider CEP
    )

    # Scenarios ordered from most to least likely (see README Scenario Rankings)
    scenarios = [
        # 01 — Mass island-drone saturation: 1,000 Shahed-136 targeting Marine LZs.
        # Impact areas visualised as orange kill-radius circles (30 m lethal radius, 36 kg HE).
        # Marines within 500 m of any Shahed impact rendered at full track resolution.
        ("#01 — Island Drone Swarm — 1,000 Shahed-136 LZ Strike",
         {"n_island_shahed": 1000,
          "iran_retaliation": True,
          "stinger_pk": 0.0, "stinger_hover_pk": 0.0,
          "n_drone_boats": 4, "n_shahed": 4,
          "beach_assault": True},
         "kharg_01_island_drone_swarm_1000.kmz",
         "Post-F-35 pre-strike scenario: MANPADS suppressed (8% IRGC survive). "
         "Iran launches 1,000 Shahed-136 loitering munitions against Marine LZs simultaneously "
         "with a 100-SRBM retaliation salvo. "
         "Tests LZ survivability under mass drone saturation: each drone carries a 36 kg HE "
         "warhead (30 m lethal radius); impact areas are visualised as persistent orange "
         "kill-radius circles. Marines within 500 m of any impact point are tracked at full "
         "resolution so individual fireteam movement through contested kill-zones is preserved."),

        # 02 — IRGC swarm doctrine at wartime surge + US EW dominance active.
        # Iran floods the engagement envelope with 4,500 island-strike Shahed-136 + 500 CSG-targeting
        # Shahed + 500 FIAC drone boats (5,000 total). Precedent: IRGC/Houthi multi-axis saturation
        # attacks 2024–2025 scaled to full wartime surge inventory. US EW dominance active.
        ("#02 — Iranian 5,000-Drone Saturation Swarm — US EW Dominance",
         {**_ew_dominance,
          "n_shahed": 500, "n_drone_boats": 500, "n_island_shahed": 4500,
          "ai_drone_fraction": 0.05},
         "kharg_02_drone_swarm_5000_ew_dominance.kmz",
         "Iran launches a 5,000-drone saturation attack: 90% (4,500 Shahed-136) target Marine LZs "
         "on the island; 10% (500 Shahed-136) plus 500 FIAC drone boats target the CSG. "
         "US EW dominance active — DIRCM defeats 90% of MANPADS, COMJAM halves IRGC ground "
         "effectiveness, MILDEC misdirects 30% of defenders. "
         "Primary stress-test: Marine survivability on the island against 4,500 inbound loitering munitions. "
         "Precedent: IRGC/Houthi island-denial swarm doctrine scaled to full wartime surge inventory."),

        # 03 — Doctrinal two-phase operation with near-certain retaliation
        ("#03 — F-35 Strike + Iranian SRBM/Shahed Retaliation",
         _f35_retaliation_overrides,
         "kharg_03_f35_strike_srbm_retaliation.kmz",
         "Pre-H-Hour SEAD/DEAD eliminates 92% of IRGC defenders and their MANPADS. "
         "Iran retaliates at H+50 with 100 SRBMs from Shiraz, Bushehr, and Bandar Abbas, "
         "followed by 100 Shahed-136 OWA-UAS targeting Marine LZs. "
         "Tests fleet survivability against a post-strike 8% reconstituted SRBM stockpile."),

        # 04 — Bilateral EW is the baseline of modern contested operations
        ("#04 — Contested EMS, Bilateral EW — 250 OPFOR",
         _contested_ems,
         "kharg_04_contested_ems_bilateral_ew_250opfor.kmz",
         "US EW active, but Iran counters with ECM on ship SAM radars (Pk −30%) "
         "and GPS spoofing on its own Shahed guidance (30% abort). "
         "Bilateral EW contest — both sides degrade each other simultaneously."),

        # 05 — Iran demonstrates persistent GPS jamming in Gulf operations
        ("#05 — F-35 Strike, GPS Jammed — 22% IRGC Survive",
         _f35_gps_jammed,
         "kharg_05_f35_strike_gps_jammed_22pct_survive.kmz",
         "IRGC ground-based GPS/INS jammers degrade JDAM CEP, allowing 22% of defenders "
         "to survive the pre-strike instead of the baseline 8%. "
         "Tests the margin of the F-35 strike package against guidance denial."),

        # 06 — Intelligence baseline: peacetime Kharg garrison + FIM-92 clones
        ("#06 — Baseline, FIM-92 Stinger — 250 OPFOR",
         {},
         "kharg_06_baseline_fim92_stinger_250opfor.kmz",
         "Reference scenario. FIM-92 Stinger MANPADS at baseline effectiveness "
         "(Pk 0.25 transit / 0.75 hover), 250 IRGC defenders. "
         "All scenario comparisons in the DAEMON suite are measured against this run."),

        # 07 — Igla-S confirmed in IRGC MANPADS battalions (IISS 2024)
        ("#07 — Russian 9K338 Igla-S SA-24 — 250 OPFOR",
         _igla_s,
         "kharg_07_igla_s_sa24_250opfor.kmz",
         "9K338 Igla-S (SA-24) with dual IR/UV seeker — Pk 0.35 transit / 0.85 hover vs FIM-92 0.25/0.75. "
         "250 OPFOR. Quantifies the operational impact of Russian MANPADS transfer to IRGC."),

        # 08 — Standard pre-H-Hour SEAD/DEAD is doctrinal for any opposed MAGTF assault
        ("#08 — F-35 Lightning Strike, No Retaliation — 8% IRGC Survive",
         _f35_overrides,
         "kharg_08_f35_lightning_strike_8pct_survive.kmz",
         "Full F-35B/FA-18/EA-18G SEAD/DEAD package destroys 92% of defenders and all MANPADS "
         "before the Marine landing. LCAC/RHIB beach insertion with no Osprey transit threat. "
         "Tests best-case kinetic shaping as the baseline for the retaliation scenario."),

        # 09 — US would bring EW assets; plausible at baseline OPFOR
        ("#09 — US EW Dominance, DIRCM + COMJAM + MILDEC — 250 OPFOR",
         _ew_dominance,
         "kharg_09_ew_dominance_dircm_comjam_mildec_250opfor.kmz",
         "AN/AAQ-24 DIRCM defeats 90% of MANPADS shots; COMJAM halves IRGC ground effectiveness; "
         "MILDEC misdirects 30% of defenders for 20 minutes. 250 OPFOR. "
         "Tests the ceiling of US EW advantage — how much does full EW dominance shift the margin?"),

        # 10 — Crisis reinforcement to 500 is realistic; Kharg infrastructure supports one reinforced battalion
        ("#10 — FIM-92 Stinger — 500 OPFOR",
         {"n_irgc": 500},
         "kharg_10_fim92_stinger_500opfor.kmz",
         "FIM-92 Stinger at full effectiveness; 500 IRGC. "
         "Dual-threat scenario — Osprey attrition from MANPADS compounds ground combat losses."),

        # 11 — AN/AAQ-24 DIRCM is standard on USMC assault support aircraft
        ("#11 — DIRCM Suppressed MANPADS (10% Pk) — 250 OPFOR",
         _degraded,
         "kharg_11_dircm_suppressed_manpads_250opfor.kmz",
         "MANPADS effectiveness reduced to 10% — equivalent to full AN/AAQ-24 DIRCM coverage. "
         "Isolates the DIRCM contribution from other EW variables at baseline OPFOR strength."),

        # 12 — Realistic if Iran has 72+ hr warning; bilateral EW + reinforced garrison
        ("#12 — Contested EMS, Bilateral EW — 1,500 OPFOR",
         {**_contested_ems, "n_irgc": 1500},
         "kharg_12_contested_ems_bilateral_ew_1500opfor.kmz",
         "Bilateral EW contest at 1,500 OPFOR. "
         "EW factors become secondary — outcome driven almost entirely by the force-size phase change."),

        # 13 — Reinforced garrison + Russian MANPADS transfer via sanctions-evasion channels
        ("#13 — Russian Igla-S SA-24 — 1,500 OPFOR",
         {**_igla_s, "n_irgc": 1500},
         "kharg_13_igla_s_sa24_1500opfor.kmz",
         "SA-24 MANPADS against 1,500 OPFOR. Elevated MANPADS lethality interacts with "
         "the Lanchester force-size phase boundary."),

        # 14 — 1,500 IRGC GF on Kharg plausible at full crisis mobilization
        ("#14 — FIM-92 Stinger — 1,500 OPFOR",
         {"n_irgc": 1500},
         "kharg_14_fim92_stinger_1500opfor.kmz",
         "FIM-92 Stinger at full effectiveness; 1,500 IRGC. "
         "Heavy MANPADS attrition reduces the Marine landing force before the ground battle begins."),

        # 15 — SA-25 newer; Iran pursuing acquisition per FDD/JINSA reporting (2025–2026)
        ("#15 — Russian 9K333 Verba SA-25 — 250 OPFOR",
         _verba,
         "kharg_15_verba_sa25_250opfor.kmz",
         "9K333 Verba (SA-25) with 3-channel seeker and ECCM resistance — Pk 0.40/0.90. "
         "Near-certain Osprey kills at LZ hover; tests whether a vertical assault remains viable."),

        # 16 — TRAP/CASEVAC tasking can extend hover exposure window
        ("#16 — FIM-92 Stinger, Extended LZ Hover 60s — 250 OPFOR",
         {"osprey_drop_steps": 2},
         "kharg_16_fim92_stinger_60s_lz_hover_250opfor.kmz",
         "Osprey hover time at LZ extended from 30 to 60 seconds. "
         "MANPADS Pk at hover is 0.75 — doubling the exposure window roughly doubles Osprey losses "
         "before a single Marine fires a shot."),

        # 17 — DIRCM effectiveness against elevated OPFOR; operationally plausible combination
        ("#17 — DIRCM Suppressed MANPADS (10% Pk) — 1,500 OPFOR",
         {**_degraded, "n_irgc": 1500},
         "kharg_17_dircm_suppressed_manpads_1500opfor.kmz",
         "DIRCM-suppressed MANPADS at 1,500 OPFOR. "
         "Tests whether DIRCM package can compensate for a 6× OPFOR force increase."),

        # 18 — Ambitious but achievable US EW package against reinforced garrison
        ("#18 — US EW Dominance, DIRCM + COMJAM + MILDEC — 1,500 OPFOR",
         {**_ew_dominance, "n_irgc": 1500},
         "kharg_18_ew_dominance_dircm_comjam_mildec_1500opfor.kmz",
         "Full US EW package against 1,500 OPFOR. "
         "Tests whether EW dominance can substitute for mass once the force-size phase threshold is crossed."),

        # 19 — Iran–China defense relationship; QW-2 confirmed in PLA export catalog
        ("#19 — PRC QW-2 MANPADS — 250 OPFOR",
         _qw2,
         "kharg_19_prc_qw2_manpads_250opfor.kmz",
         "PRC QW-2 with proportional navigation IIR seeker — Pk 0.30/0.72. "
         "250 OPFOR. Represents Chinese MANPADS procurement pathway for IRGC."),

        # 20 — Advanced MANPADS + reinforced garrison; requires SA-25 transfer completion
        ("#20 — Russian Verba SA-25 — 1,500 OPFOR",
         {**_verba, "n_irgc": 1500},
         "kharg_20_verba_sa25_1500opfor.kmz",
         "SA-25 against 1,500 OPFOR — worst-case MANPADS threat combined with maximum OPFOR strength."),

        # 21 — Chinese MANPADS + crisis garrison
        ("#21 — PRC QW-2 MANPADS — 1,500 OPFOR",
         {**_qw2, "n_irgc": 1500},
         "kharg_21_prc_qw2_manpads_1500opfor.kmz",
         "QW-2 against 1,500 OPFOR."),

        # 22 — FN-6 documented in Houthi/Hezbollah inventories; possible Iran pathway
        ("#22 — PRC FN-6 HY-6 MANPADS — 250 OPFOR",
         _fn6,
         "kharg_22_prc_fn6_hy6_manpads_250opfor.kmz",
         "PRC FN-6 (HY-6) with passive IR and rosette scanning seeker — Pk 0.28/0.78. "
         "250 OPFOR."),

        # 23 — Same procurement pathway at elevated OPFOR
        ("#23 — PRC FN-6 HY-6 MANPADS — 1,500 OPFOR",
         {**_fn6, "n_irgc": 1500},
         "kharg_23_prc_fn6_hy6_manpads_1500opfor.kmz",
         "FN-6 against 1,500 OPFOR."),

        # 24 — 2,000 on a 37 km² island; requires weeks of deliberate pre-war buildup
        ("#24 — FIM-92 Stinger — 2,000 OPFOR",
         {"n_irgc": 2000},
         "kharg_24_fim92_stinger_2000opfor.kmz",
         "FIM-92 Stinger at full effectiveness; 2,000 IRGC. Maximum OPFOR with full MANPADS threat active."),

        # 25–32 — Permissive JAAT: complete MANPADS suppression before landing (optimistic end-state)
        ("#25 — Permissive JAAT, No MANPADS — 250 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0},
         "kharg_25_permissive_jaat_no_manpads_250opfor.kmz",
         "MANPADS threat fully suppressed; 250 IRGC at baseline strength. "
         "Establishes the pure ground-combat outcome — no Osprey attrition to corrupt the Lanchester exchange."),

        ("#26 — Permissive JAAT, No MANPADS — 500 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc":  500},
         "kharg_26_permissive_jaat_no_manpads_500opfor.kmz",
         "No MANPADS; 500 IRGC. Approaches the Lanchester phase threshold — "
         "roughly the force-size at which the N² terrain advantage begins overcoming USMC quality superiority."),

        ("#27 — Permissive JAAT, No MANPADS — 750 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc":  750},
         "kharg_27_permissive_jaat_no_manpads_750opfor.kmz",
         "No MANPADS; 750 IRGC. Above the phase boundary — OPFOR force-size plus positional "
         "terrain bonus begins denying the assault in most Monte Carlo runs."),

        ("#28 — Permissive JAAT, No MANPADS — 1,000 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc": 1000},
         "kharg_28_permissive_jaat_no_manpads_1000opfor.kmz",
         "No MANPADS; 1,000 IRGC. Well above the phase boundary. "
         "Demonstrates the N² exponent: 4× OPFOR count produces roughly 16× effective Lanchester combat power."),

        ("#29 — Permissive JAAT, No MANPADS — 1,250 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc": 1250},
         "kharg_29_permissive_jaat_no_manpads_1250opfor.kmz",
         "No MANPADS; 1,250 IRGC. OPFOR force sufficient to repel a full MAGTF "
         "even without any MANPADS contribution to the defense."),

        ("#30 — Permissive JAAT, No MANPADS — 1,500 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc": 1500},
         "kharg_30_permissive_jaat_no_manpads_1500opfor.kmz",
         "No MANPADS; 1,500 IRGC. Permissive aviation environment; IRGC repels regardless. "
         "Shows the upper ceiling of USMC quality advantage over pure OPFOR mass."),

        ("#31 — Permissive JAAT, No MANPADS — 1,750 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc": 1750},
         "kharg_31_permissive_jaat_no_manpads_1750opfor.kmz",
         "No MANPADS; 1,750 IRGC. Upper end of the permissive-aviation force-size study."),

        ("#32 — Permissive JAAT, No MANPADS — 2,000 OPFOR",
         {"stinger_pk": 0.0, "stinger_hover_pk": 0.0, "n_irgc": 2000},
         "kharg_32_permissive_jaat_no_manpads_2000opfor.kmz",
         "No MANPADS; 2,000 IRGC — equivalent to a full IRGC Ground Forces regiment "
         "on a 37 km² island. Least likely scenario: extreme pre-war buildup combined with "
         "complete MANPADS suppression before a single Marine lands."),
    ]
    return scenarios


_STRIP = {"beach_assault", "iran_retaliation", "pre_strike_survival_pct"}


def run_scenario_entry(label, overrides, fname, desc, scenarios_dir=None):
    """Run a single scenario 4-tuple.  scenarios_dir defaults to output/scenarios/."""
    if scenarios_dir is None:
        scenarios_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "output", "scenarios"
        )
    print(f"\n{'='*60}")
    print(f"SCENARIO: {label}")
    print('='*60)
    out = os.path.join(scenarios_dir, fname)
    if "pre_strike_survival_pct" in overrides:
        pre_pct = overrides["pre_strike_survival_pct"]
    elif overrides.get("beach_assault"):
        pre_pct = 0.08
    else:
        pre_pct = None
    n_pre      = overrides.get("n_irgc", cfg.N_SQUADS) if pre_pct else None
    iran_ret   = overrides.get("iran_retaliation", True)
    patch_args = {k: v for k, v in overrides.items() if k not in _STRIP}
    with _patch_scenario(**patch_args,
                         beach_assault=overrides.get("beach_assault", False)):
        _run_scenario(out, scenario_label=label,
                      pre_strike_survival_pct=pre_pct,
                      n_irgc_pre=n_pre,
                      iran_retaliation=iran_ret,
                      scenario_desc=desc)


def main():
    scenarios_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "scenarios")
    for entry in build_scenarios():
        run_scenario_entry(*entry, scenarios_dir=scenarios_dir)


if __name__ == "__main__":
    main()
