"""
kml/document.py — Top-level KML document generation (gen_kml).
"""

from persian_gulf_simulation.config import (
    N_STEPS, MARINE_HP, IRGC_HP, STINGER_HP, DBOAT_HP, SHAHED_HP,
    OSPREY_TRANSIT_ALT_M, REAPER_ALT_M, SHAHED_ALT_M, DBOAT_ALT_M,
    SHIP_MAX_HP, SHIP_NAMES,
    N_STINGER_TEAMS, STINGER_PK, STINGER_HOVER_PK, STINGER_WEZ_KM,
    OSPREY_ALT_M, STINGER_ARC_PEAK_M,
    OSPREYS_PER_SORTIE, _SORTIE_CYCLE, _SORTIE_TEAMS, _N_SORTIES, N_TEAMS,
    N_US_DRONES, DRONE_HELLFIRE, DRONE_PK,
    N_DRONE_BOATS, N_SHAHED, N_IRAN_BM, N_ISLAND_SHAHED,
    IRGC_CLUSTERS, CLUSTER_NAMES,
    LZS, LZ_NAMES, LZ_DROP_WINDOW_S, LZ_HOVER_RADIUS_KM,
    MV22_CAPACITY,
    STINGER_ARC_SECS, STINGER_ARC_PEAK_M, OSPREY_ALT_M,
    IRGC_DEFENSE_MULT, IRGC_HOME_RADIUS_KM,
    LAT_KM,
)
from persian_gulf_simulation.kml.styles import build_kml_styles
from persian_gulf_simulation.kml.descriptions import (
    _card, _alive_badge,
    _marine_desc, _irgc_desc, _stinger_desc, _osprey_desc,
    _drone_desc, _ship_desc, _dboat_desc, _shahed_desc,
    _marine_folder_desc, _irgc_folder_desc, _stinger_folder_desc,
    _osprey_folder_desc, _drone_folder_desc, _dboat_folder_desc,
    _shahed_folder_desc, _bm_folder_desc, _island_shahed_folder_desc,
    _ship_folder_desc, _battle_summary_desc,
)
from persian_gulf_simulation.kml.placemarks import (
    agent_to_placemarks, bm_to_placemarks,
    stinger_wez_placemark, stinger_shot_placemark,
    lz_hover_zone_placemark, lz_marker_placemark,
    island_shahed_impact_placemarks,
    osprey_simple_drop_placemarks,
)
from persian_gulf_simulation.kml.narration import (
    extract_narration_events, narration_placemark, _narration_folder_desc,
)
from persian_gulf_simulation.kml.tour import gen_battle_tour
from persian_gulf_simulation.kml.captions import gen_captions
from persian_gulf_simulation.simulation.spatial import ts, ts_offset, dist_km


def gen_kml(marines, irgc, stingers, ospreys, drones,
            ships, drone_boats, shahed,
            stats, irgc_cluster_map, flights, stinger_shots,
            scenario_label="Kharg Island Assault",
            extra_doc_desc=None,
            iran_bm=None, island_shahed=None,
            scenario_desc=None):
    styles = build_kml_styles()
    sk     = stats["stinger_kills"]

    _folder_balloon = (
        '    <Style><BalloonStyle>'
        '<bgColor>ff000000</bgColor>'
        '<text>$[description]</text>'
        '</BalloonStyle></Style>\n'
    )

    def folder(name, open_val, desc, placemarks):
        desc_tag = f"    <description>{desc}</description>\n" if desc else ""
        return (
            f"  <Folder>\n    <name>{name}</name>\n    <visibility>0</visibility>\n    <open>{open_val}</open>\n"
            + _folder_balloon
            + desc_tag
            + "\n".join(placemarks)
            + "\n  </Folder>"
        )

    def _xml(s):
        """Escape characters that are invalid in XML element text content."""
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def group(name, open_val, subfolders):
        """Nesting wrapper — subfolders is a list of already-rendered folder strings."""
        active = [f for f in subfolders if f]  # drop empty strings (optional BM/ISH)
        if not active:
            return ""
        return (
            f"  <Folder>\n    <name>{_xml(name)}</name>\n    <visibility>0</visibility>\n    <open>{open_val}</open>\n"
            + _folder_balloon
            + "\n".join(active)
            + "\n  </Folder>"
        )

    # --- Pre-compute island Shahed impact positions for marine proximity logic ---
    # A Shahed "hit" is one that died within 2 km of its own target LZ (on-island).
    # Marines whose LZ is within 500 m of any hit get full track resolution (sample=1)
    # so their movement through contested kill-zones is fully preserved.
    slk = stats["ship_loss_kills"]
    _ish_impact_pts = []   # [(lon, lat)] of on-island Shahed hits
    if island_shahed:
        for sh in island_shahed:
            if sh.hp == 0 and sh.dead_step is not None and sh.track and sh.lz:
                recs = [r for r in sh.track if r[0] <= sh.dead_step]
                if recs:
                    _, flon, flat, _ = recs[-1]
                    if dist_km(flon, flat, sh.lz[0], sh.lz[1]) < 2.0:
                        _ish_impact_pts.append((flon, flat))

    def _marine_track_sample(m):
        """Full resolution if marine's LZ is within 500 m of any Shahed impact."""
        if m.lz and _ish_impact_pts:
            if any(dist_km(m.lz[0], m.lz[1], ilon, ilat) < 0.5
                   for ilon, ilat in _ish_impact_pts):
                return 1
        return 3

    # --- Marines ---
    marine_pms = []
    for m in marines:
        marine_pms.extend(agent_to_placemarks(
            m, is_marine=True, n_steps=N_STEPS,
            desc_fn=lambda hp, _m=m: _marine_desc(_m, sk, slk, hp_override=hp),
            max_hp=MARINE_HP, track_sample=_marine_track_sample(m),
            trim_pre_launch=True,
        ))
    marine_folder = folder("USMC Ground Element — Fireteams", 0,
                           _marine_folder_desc(marines, sk, slk, stats=stats), marine_pms)

    # --- IRGC ---
    irgc_pms = []
    for s in irgc:
        irgc_pms.extend(agent_to_placemarks(
            s, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _s=s: _irgc_desc(_s, irgc_cluster_map.get(_s.agent_id, 0), hp_override=hp),
            max_hp=IRGC_HP, track_sample=3,
        ))
    irgc_folder = folder("IRGC Ground Defenders — Squads", 0,
                         _irgc_folder_desc(irgc, irgc_cluster_map=irgc_cluster_map),
                         irgc_pms)

    # --- Stingers ---
    stinger_pms = []
    for st in stingers:
        stinger_pms.append(stinger_wez_placemark(st))
        stinger_pms.extend(agent_to_placemarks(
            st, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _st=st: _stinger_desc(_st, stats, hp_override=hp),
            is_stinger=True, max_hp=STINGER_HP
        ))
    stinger_folder = folder(
        f"IRGC Stinger MANPADS ({N_STINGER_TEAMS} teams, Pk={STINGER_PK}/{STINGER_HOVER_PK})",
        0, _stinger_folder_desc(stingers, stats), stinger_pms
    )

    # --- Ospreys (simplified: 4 keyframes per trip instead of every step) ---
    osprey_pms = []
    _osprey_trips_map = stats.get("osprey_trips_map", {})
    for ov in ospreys:
        trip_list = _osprey_trips_map.get(ov.agent_id, [])
        osprey_pms.extend(osprey_simple_drop_placemarks(ov, trip_list, flights))
    osprey_folder = folder(
        f"MV-22 Ospreys ({OSPREYS_PER_SORTIE} aircraft, cycle {_SORTIE_CYCLE} min)",
        0, _osprey_folder_desc(ospreys, stats, flights), osprey_pms
    )

    # --- Drones ---
    drone_pms = []
    for d in drones:
        drone_pms.extend(agent_to_placemarks(
            d, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _d=d: _drone_desc(_d, stats, hp_override=hp),
            is_drone=True,
            altitude_m=REAPER_ALT_M, max_hp=1
        ))
    drone_folder = folder(
        f"US MQ-9 Reapers ({N_US_DRONES} drones, {DRONE_HELLFIRE} Hellfires, Pk={DRONE_PK})",
        0, _drone_folder_desc(drones, stats), drone_pms
    )

    # --- Ships ---
    ship_pms = []
    for s in ships:
        ship_pms.extend(agent_to_placemarks(
            s, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _s=s: _ship_desc(_s, stats, hp_override=hp),
            is_ship=True, max_hp=SHIP_MAX_HP[s.agent_id],
            unit_name=SHIP_NAMES[s.agent_id],
        ))
    ship_folder = folder(
        "US Naval Group (3 ships)", 0,
        _ship_folder_desc(ships, stats), ship_pms
    )

    # --- IRGCN Drone Boats ---
    dboat_pms = []
    for db in drone_boats:
        dboat_pms.extend(agent_to_placemarks(
            db, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _db=db: _dboat_desc(_db, hp_override=hp),
            is_dboat=True,
            altitude_m=DBOAT_ALT_M, max_hp=DBOAT_HP, track_sample=2,
        ))
    dboat_folder = folder(
        f"IRGCN Drone Boat Swarm ({N_DRONE_BOATS} FIAC, 45 kts)",
        0, _dboat_folder_desc(drone_boats, stats), dboat_pms
    )

    # --- Shahed Drones ---
    shahed_pms = []
    for sh in shahed:
        shahed_pms.extend(agent_to_placemarks(
            sh, is_marine=False, n_steps=N_STEPS,
            desc_fn=lambda hp, _sh=sh: _shahed_desc(_sh, hp_override=hp),
            is_shahed=True,
            altitude_m=SHAHED_ALT_M, max_hp=SHAHED_HP,
            is_ai=sh.is_ai, track_sample=2,
        ))
    shahed_folder = folder(
        f"Shahed-136 Strike Package ({N_SHAHED} drones, 185 km/h)",
        0, _shahed_folder_desc(shahed, stats), shahed_pms
    )

    # --- Iranian SRBM Salvo ---
    bm_folder = ""
    if iran_bm:
        bm_pms = []
        bm_outcome_map = stats.get("bm_outcome", {})
        for i, bm in enumerate(iran_bm):
            bm_pms.extend(bm_to_placemarks(bm, bm_outcome_map, show_label=(i % 10 == 0)))
        n_bm_hit = stats.get("bm_hits", 0)
        n_bm_int = stats.get("bm_intercepted", 0)
        bm_folder = folder(
            f"Iranian SRBM Salvo — {N_IRAN_BM} missiles"
            f"  ({n_bm_hit} impacts / {n_bm_int} intercepted)",
            1, _bm_folder_desc(iran_bm, stats), bm_pms
        )

    # --- Island-targeting Shahed ---
    ish_folder = ""
    if island_shahed:
        ish_pms = []
        ish_impact_pms = []
        for i, sh in enumerate(island_shahed):
            ish_pms.extend(agent_to_placemarks(
                sh, is_marine=False, n_steps=N_STEPS,
                desc_fn=lambda hp, _sh=sh: _shahed_desc(_sh, hp_override=hp, is_island=True),
                is_shahed=True,
                altitude_m=SHAHED_ALT_M, max_hp=SHAHED_HP,
                is_ai=sh.is_ai, show_label=(i % 10 == 0),
                track_sample=2, trim_pre_launch=True,
            ))
            # Impact circles for on-island hits only (drone died within 2 km of its own LZ)
            if sh.hp == 0 and sh.dead_step is not None and sh.lz and sh.track:
                _recs = [r for r in sh.track if r[0] <= sh.dead_step]
                if _recs:
                    _, _flon, _flat, _ = _recs[-1]
                    if dist_km(_flon, _flat, sh.lz[0], sh.lz[1]) < 2.0:
                        ish_impact_pms.extend(
                            island_shahed_impact_placemarks(sh, show_icon=(i % 10 == 0))
                        )
        ish_hit  = stats.get("island_sh_hits", 0)
        ish_down = stats.get("island_sh_shot_down", 0)
        n_ish    = len(island_shahed)
        ish_folder = folder(
            f"Iranian Island Strike — {n_ish} Shahed-136"
            f"  ({ish_hit} impacts / {ish_down} intercepted)",
            1, _island_shahed_folder_desc(island_shahed, stats), ish_pms
        )
        if ish_impact_pms:
            ish_folder += "\n" + folder(
                f"Shahed Impact Areas  ({ish_hit} hits)",
                1, None, ish_impact_pms,
            )

    # --- IRGC Cluster Sites ---
    site_pms = []
    for ci, ((clon, clat, n_sq, spread), cname) in enumerate(zip(IRGC_CLUSTERS, CLUSTER_NAMES)):
        cluster_irgc = [s for s in irgc if irgc_cluster_map.get(s.agent_id) == ci]
        alive_sq = sum(1 for s in cluster_irgc if s.hp > 0)
        site_desc = _card(f"IRGC CLUSTER — {cname}", "#f85149", [
            ("Position",        f"{clon:.4f}°E  {clat:.4f}°N"),
            ("Total Squads",    f"{n_sq}"),
            ("Alive",           f'<span style="color:#3fb950">{alive_sq}</span>'),
            ("Neutralized",     f'<span style="color:#f85149">{n_sq - alive_sq}</span>'),
            ("Spread Radius",   f"{spread:.3f}°  (~{spread * LAT_KM:.1f} km)"),
            ("Def. Bonus",      f"{IRGC_DEFENSE_MULT}x within {IRGC_HOME_RADIUS_KM} km of home"),
        ])
        site_pms.append(f"""    <Placemark>
      <name>{cname} ({n_sq} squads)</name>
      <description>{site_desc}</description>
      <styleUrl>#irgc_site</styleUrl>
      <Point><coordinates>{clon},{clat},0</coordinates></Point>
    </Placemark>""")
    sites_folder = folder("IRGC Cluster Positions", 0, None, site_pms)

    # --- Stinger Missile Trajectories ---
    n_hits  = sum(1 for s in stinger_shots if s["hit"])
    n_miss  = len(stinger_shots) - n_hits
    shot_pms = []
    for idx, shot in enumerate(stinger_shots):
        shot_pms.append(stinger_shot_placemark(shot, idx))
    shots_folder_desc = _card("STINGER ENGAGEMENTS — TRAJECTORY LOG", "#d29922", [
        ("Total Shots",    str(len(stinger_shots))),
        ("Hits",           f'<span style="color:#f85149;font-weight:bold">{n_hits}</span>  (solid red arc)'),
        ("Misses",         f'<span style="color:#8b949e">{n_miss}</span>  (grey arc — overshoots target)'),
        ("Pk Transit",     str(STINGER_PK)),
        ("Pk Hover",       f'<span style="color:#f85149">{STINGER_HOVER_PK}</span>  (drop window)'),
        ("Arc Duration",   f"{STINGER_ARC_SECS}s visible  (missile flight time)"),
        ("Altitude Mode",  "relativeToGround  (3D parabola)"),
        ("Osprey Alt",     f"{OSPREY_ALT_M:.0f} m  (cruise)  →  arc apex ~{OSPREY_ALT_M + STINGER_ARC_PEAK_M:.0f} m"),
    ])
    shots_folder = folder(
        f"Stinger Trajectories  ({n_hits} hits  /  {n_miss} misses)",
        0, shots_folder_desc, shot_pms
    )

    # --- LZ Hover Zones ---
    teams_first  = _SORTIE_TEAMS[0]
    teams_per_lz = max(1, teams_first // len(LZS))
    lz_pms = []
    for lz in LZS:
        lz_name = LZ_NAMES[lz]
        lz_pms.append(lz_hover_zone_placemark(lz, lz_name, teams_per_lz))
        lz_pms.append(lz_marker_placemark(lz, lz_name, teams_per_lz))
    lz_folder_desc = _card("LANDING ZONES — DROP ZONE OVERVIEW", "#00ffff", [
        ("LZs Active",       "FALCON  EAGLE  VIPER  COBRA"),
        ("Drop Window",      f'<span style="color:#f85149;font-weight:bold">'
                              f'{LZ_DROP_WINDOW_S}s hover</span>  per sortie'),
        ("Stinger Pk",       f'{STINGER_HOVER_PK} during hover  /  {STINGER_PK} in transit'),
        ("Osprey Capacity",  f"{MV22_CAPACITY} fireteams  ({MV22_CAPACITY * 4} men) per aircraft"),
        ("Total Sorties",    f"{_N_SORTIES}  ({N_TEAMS} fireteams  /  {N_TEAMS * 4} men)"),
        ("Cycle",            f"{_SORTIE_CYCLE} min round-trip"),
    ])
    lz_folder = folder("LZ Hover Zones (Drop Windows)", 0, lz_folder_desc, lz_pms)

    # --- Battle Narration ---
    narr_events = extract_narration_events(
        marines, ospreys, ships, irgc, stingers, stats, irgc_cluster_map
    )
    narr_pms = [narration_placemark(e) for e in narr_events]
    narration_folder = folder(
        f"Battle Narration  ({len(narr_events)} events)",
        0, _narration_folder_desc(narr_events), narr_pms
    )

    # --- Closed Captions (screen overlays) ---
    captions_kml, caption_files = gen_captions(narr_events)

    doc_desc = (extra_doc_desc if extra_doc_desc is not None
                else _battle_summary_desc(marines, irgc, stingers, ospreys, ships, stats,
                                          scenario_label=scenario_label,
                                          scenario_desc=scenario_desc))

    tour = gen_battle_tour(stinger_shots, ships, N_STEPS,
                           ospreys=ospreys,
                           scenario_label=scenario_label)

    # ── Grouped folder hierarchy ──────────────────────────────────────────────
    # US Aviation sub-group
    us_aviation = group("US Aviation — Ospreys, Reapers & LZs", 0, [
        osprey_folder,
        lz_folder,
        drone_folder,
    ])

    # US Forces top-level group
    us_forces = group("US Forces", 0, [
        marine_folder,
        us_aviation,
        ship_folder,
    ])

    # IRGC Ground Defense sub-group
    irgc_ground = group("IRGC Ground Defense", 0, [
        irgc_folder,
        sites_folder,
    ])

    # IRGC Air Defense (MANPADS) sub-group
    irgc_air_defense = group("IRGC Air Defense — MANPADS", 0, [
        stinger_folder,
        shots_folder,
    ])

    # IRGC Maritime Threat sub-group
    irgc_maritime = group("IRGC Maritime Threat", 0, [
        dboat_folder,
        shahed_folder,
    ])

    # Iranian Strategic Retaliation sub-group (only present in retaliation scenarios)
    iran_strategic = group("Iranian Strategic Retaliation", 0, [
        bm_folder,
        ish_folder,
    ])

    # IRGC Forces top-level group
    irgc_forces = group("IRGC / Iranian Forces", 0, [
        irgc_ground,
        irgc_air_defense,
        irgc_maritime,
        iran_strategic,
    ])

    # Battle Overview top-level group
    battle_overview = group("Battle Overview", 0, [
        narration_folder,
    ])

    _t0     = ts(0)
    _t2min  = ts_offset(0, 120)   # 2-minute initial window
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document id="battle_doc">
  <name>Kharg Island — {scenario_label}</name>
  <visibility>0</visibility>
  <Snippet maxLines="1">TOGGLE WANTED VISIBILITY</Snippet>
  <TimeSpan><begin>{_t0}</begin><end>{_t2min}</end></TimeSpan>
  <Style><BalloonStyle><bgColor>ff000000</bgColor><text>$[description]</text></BalloonStyle></Style>
  <description>{doc_desc}</description>
{styles}
{tour}
{captions_kml}
{battle_overview}
{us_forces}
{irgc_forces}
</Document>
</kml>"""
    return kml, caption_files
