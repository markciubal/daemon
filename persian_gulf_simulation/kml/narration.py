"""
kml/narration.py — Battle narration event extraction and KML placemark generation.

Contains: extract_narration_events, narration_placemark, _narration_folder_desc.
"""

from persian_gulf_simulation.config import (
    NARRATION_DISPLAY_STEPS, N_STEPS,
    TRIPOLI_LON, TRIPOLI_LAT,
    OSPREYS_PER_SORTIE, N_US_DRONES, N_DRONE_BOATS, N_SHAHED,
    SHIP_MAX_HP, SHIP_NAMES, SHIP_CLASSES,
    IRGC_CLUSTERS, CLUSTER_NAMES,
    STINGER_HOVER_PK,
    SIM_BASE_H, SIM_DATE,
)
from persian_gulf_simulation.simulation.spatial import ts, ts_hhmm
from persian_gulf_simulation.kml.descriptions import _card


def _narration_folder_desc(events):
    n_osprey  = sum(1 for e in events if e["type"] == "osprey_down")
    n_sh_hit  = sum(1 for e in events if e["type"] == "ship_hit")
    n_sh_sunk = sum(1 for e in events if e["type"] == "ship_sunk")
    n_cleared = sum(1 for e in events if e["type"] == "cluster_cleared")
    return _card("BATTLE NARRATION — EVENT TIMELINE", "#58a6ff", [
        ("Events Logged",    str(len(events))),
        ("Osprey Losses",    f'<span style="color:#d29922">{n_osprey}</span>'),
        ("Ship Hits",        f'<span style="color:#ff8c00">{n_sh_hit}</span>'),
        ("Ships Sunk",       f'<span style="color:#f85149">{n_sh_sunk}</span>'),
        ("Clusters Cleared", f'<span style="color:#3fb950">{n_cleared}</span>'),
        ("Display Window",   f"{NARRATION_DISPLAY_STEPS} min per event"),
        ("Usage",            "Scrub the timeline to replay events"),
    ])


def extract_narration_events(marines, ospreys, ships, irgc, stingers, stats, irgc_cluster_map):
    events = []

    # ── Assault commences ────────────────────────────────────────────────────
    events.append({
        "step": 0, "end_step": NARRATION_DISPLAY_STEPS,
        "type": "start",
        "lon": TRIPOLI_LON, "lat": TRIPOLI_LAT,
        "name": "ASSAULT COMMENCES — H-Hour",
        "title": "OPERATION: KHARG ISLAND AMPHIBIOUS ASSAULT",
        "rows": [
            ("Time",       f"{SIM_BASE_H:02d}:00Z  {SIM_DATE}"),
            ("Objective",  "Seize Kharg Island oil terminal"),
            ("US Forces",  f"{len(marines)} fireteams  ·  {OSPREYS_PER_SORTIE} MV-22Bs  ·  {N_US_DRONES} MQ-9s"),
            ("IRGC Def.",  f"{len(irgc)} squads  ·  {len(stingers)} Stinger teams"),
            ("Threats",    f"{N_DRONE_BOATS} FIAC boats  ·  {N_SHAHED} Shahed-136"),
        ],
    })

    # ── Osprey shot down (one event per downed Osprey) ───────────────────────
    shot_osprey_ids = set()
    for shot in stats["stinger_shots"]:
        if not shot["hit"] or shot["ov_id"] in shot_osprey_ids:
            continue
        shot_osprey_ids.add(shot["ov_id"])
        ov = next((o for o in ospreys if o.agent_id == shot["ov_id"]), None)
        if ov is None or ov.dead_step is None:
            continue
        last_alive = next((r for r in reversed(ov.track) if r[3] > 0), None)
        lon = last_alive[1] if last_alive else ov.lon
        lat = last_alive[2] if last_alive else ov.lat
        mode = "hover / drop window" if shot["pk"] >= STINGER_HOVER_PK else "transit"
        events.append({
            "step": ov.dead_step, "end_step": ov.dead_step + NARRATION_DISPLAY_STEPS,
            "type": "osprey_down",
            "lon": lon, "lat": lat,
            "name": f"{ov.agent_id} SHOT DOWN",
            "title": f"MV-22 OSPREY SHOT DOWN — {ov.agent_id}",
            "rows": [
                ("Aircraft",  ov.agent_id),
                ("Time",      ts_hhmm(ov.dead_step)),
                ("By",        f"Stinger MANPADS  {shot['st_id']}"),
                ("Mode",      f'{mode}  '
                               f'<span style="color:#f85149">(Pk = {shot["pk"]})</span>'),
                ("Position",  f"{lon:.4f}°E  {lat:.4f}°N"),
            ],
        })

    # ── Ship hit events ───────────────────────────────────────────────────────
    ship_hit_counts = {}  # ship_id → running count for "Hit #N" label
    for hit_step, ship_id, source, hp_after in stats.get("ship_hit_log", []):
        ship = next((s for s in ships if s.agent_id == ship_id), None)
        if ship is None:
            continue
        max_hp  = SHIP_MAX_HP[ship_id]
        hit_num = ship_hit_counts.get(ship_id, 0) + 1
        ship_hit_counts[ship_id] = hit_num
        hp_bar  = ("&#9608;" * hp_after) + ("&#9617;" * (max_hp - hp_after))
        sname   = SHIP_NAMES[ship_id].split("(")[0].strip()
        dmg_pct = f"{100 * (max_hp - hp_after) // max_hp}%"
        status  = ("SUNK" if hp_after == 0 else
                   f'<span style="color:#f85149">CRITICAL</span>' if hp_after == 1 else
                   f'<span style="color:#d29922">DAMAGED</span>')
        events.append({
            "step": hit_step, "end_step": hit_step + NARRATION_DISPLAY_STEPS,
            "type": "ship_hit",
            "lon": ship.lon, "lat": ship.lat,
            "name": f"{sname} HIT (#{hit_num})",
            "title": f"US SHIP HIT — {sname}  (Hit #{hit_num})",
            "rows": [
                ("Ship",    SHIP_NAMES[ship_id]),
                ("Time",    ts_hhmm(hit_step)),
                ("Source",  source),
                ("HP",      f"{hp_bar}  {hp_after}/{max_hp}  ({dmg_pct} damage)"),
                ("Status",  status),
            ],
        })

    # ── Ship sunk ─────────────────────────────────────────────────────────────
    for ship in ships:
        if ship.dead_step is None:
            continue
        slk = len(stats["ship_loss_kills"])
        sc  = stats["sorties_cancelled"]
        sname = SHIP_NAMES[ship.agent_id].split("(")[0].strip()
        events.append({
            "step": ship.dead_step, "end_step": ship.dead_step + NARRATION_DISPLAY_STEPS * 2,
            "type": "ship_sunk",
            "lon": ship.lon, "lat": ship.lat,
            "name": f"\u26a0 {sname} SUNK",
            "title": f"SHIP SUNK — {SHIP_NAMES[ship.agent_id]}",
            "rows": [
                ("Ship",              SHIP_NAMES[ship.agent_id]),
                ("Hull Class",        SHIP_CLASSES[ship.agent_id]),
                ("Time",              ts_hhmm(ship.dead_step)),
                ("Navy Crew KIA",     f'<span style="color:#f85149">2 500 personnel</span>'),
                ("Marines Stranded",  f'<span style="color:#f85149">'
                                       f'{slk} fireteams  ({slk*4} men)</span>'
                                       f'  — undeployed / airborne'),
                ("Sorties Aborted",   f"{sc} flights cancelled"),
                ("Cascading Effect",  "Landed marines continue fighting ashore"),
            ],
        })

    # ── IRGC cluster fully cleared ────────────────────────────────────────────
    for ci, ((clon, clat, n_sq, _), cname) in enumerate(zip(IRGC_CLUSTERS, CLUSTER_NAMES)):
        cluster = [s for s in irgc if irgc_cluster_map.get(s.agent_id) == ci]
        if not cluster or any(s.hp > 0 for s in cluster):
            continue
        last_step = max(s.dead_step for s in cluster if s.dead_step is not None)
        events.append({
            "step": last_step, "end_step": last_step + NARRATION_DISPLAY_STEPS,
            "type": "cluster_cleared",
            "lon": clon, "lat": clat,
            "name": f"CLEARED — {cname}",
            "title": f"IRGC POSITION CLEARED — {cname}",
            "rows": [
                ("Position",  cname),
                ("Time",      ts_hhmm(last_step)),
                ("Squads",    f"{n_sq} neutralized"),
                ("Coords",    f"{clon:.4f}°E  {clat:.4f}°N"),
            ],
        })

    # ── All IRGC neutralized ──────────────────────────────────────────────────
    if all(s.hp <= 0 for s in irgc) and all(s.hp <= 0 for s in stingers):
        last_kill = max(
            (s.dead_step for s in irgc + stingers if s.dead_step is not None),
            default=N_STEPS
        )
        events.append({
            "step": last_kill, "end_step": last_kill + NARRATION_DISPLAY_STEPS,
            "type": "cluster_cleared",
            "lon": 50.328, "lat": 29.240,
            "name": "ALL IRGC NEUTRALIZED",
            "title": "KHARG ISLAND SECURED — ALL DEFENDERS NEUTRALIZED",
            "rows": [
                ("Time",    ts_hhmm(last_kill)),
                ("IRGC",    f"{len(irgc)} squads neutralized"),
                ("Stingers",f"{len(stingers)} MANPADS teams destroyed"),
                ("Result",  f'<span style="color:#3fb950;font-weight:bold">'
                             f'Island cleared for US forces</span>'),
            ],
        })

    # ── Simulation outcome ────────────────────────────────────────────────────
    alive_m   = sum(1 for m in marines if m.hp > 0)
    alive_i   = sum(1 for s in irgc    if s.hp > 0)
    alive_st  = sum(1 for s in stingers if s.hp > 0)
    island_held = alive_i == 0 and alive_st == 0
    sunk_names  = [SHIP_NAMES[s.agent_id] for s in ships if s.hp <= 0]
    outcome = ("USMC SECURED KHARG ISLAND" if island_held and not sunk_names
               else "USMC SECURED — SHIPS LOST" if island_held
               else "IRGC REPELLED ASSAULT"    if alive_m == 0
               else "CONTESTED")
    out_color = "#3fb950" if island_held else "#f85149" if alive_m == 0 else "#d29922"
    events.append({
        "step": N_STEPS, "end_step": N_STEPS + 10,
        "type": "outcome",
        "lon": 50.328, "lat": 29.240,
        "name": f"OUTCOME: {outcome}",
        "title": "BATTLE OUTCOME — FINAL ASSESSMENT",
        "rows": [
            ("Time",        ts_hhmm(N_STEPS)),
            ("Result",      f'<span style="color:{out_color};font-weight:bold">'
                             f'{outcome}</span>'),
            ("Marines",     f"{alive_m}/{len(marines)} fireteams alive  "
                             f"({alive_m * 4} men)"),
            ("IRGC",        f"{alive_i}/{len(irgc)} defenders alive"),
            ("Ships Lost",  ", ".join(sunk_names) if sunk_names else "None"),
        ],
    })

    events.sort(key=lambda e: e["step"])
    return events


def narration_placemark(event):
    style_map = {
        "start":           "#narration_start",
        "osprey_down":     "#narration_osprey",
        "ship_hit":        "#narration_ship_hit",
        "ship_sunk":       "#narration_sunk",
        "cluster_cleared": "#narration_cleared",
        "outcome":         "#narration_outcome",
    }
    desc = _card(event["title"],
                 {"start": "#58a6ff", "osprey_down": "#d29922", "ship_hit": "#ff8c00",
                  "ship_sunk": "#f85149", "cluster_cleared": "#3fb950",
                  "outcome": "#c9d1d9"}.get(event["type"], "#8b949e"),
                 event["rows"])
    return f"""    <Placemark>
      <name>{event["name"]}</name>
      <description>{desc}</description>
      <styleUrl>{style_map.get(event["type"], "#narration_start")}</styleUrl>
      <TimeSpan><begin>{ts(event["step"])}</begin><end>{ts(event["end_step"])}</end></TimeSpan>
      <Point>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>{event["lon"]:.6f},{event["lat"]:.6f},0</coordinates>
      </Point>
    </Placemark>"""
