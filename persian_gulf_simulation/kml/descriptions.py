"""
kml/descriptions.py — HTML description card builders for KML placemarks.

Contains: _card, _pct, _alive_badge, _speed_stats, _fmt_speed,
          all _*_desc and _*_folder_desc functions.
"""

import math

from persian_gulf_simulation.config import (
    MARINE_HP, IRGC_HP, STINGER_HP, DBOAT_HP, SHAHED_HP,
    STINGER_RATIO, STINGER_WEZ_KM, STINGER_PK, STINGER_HOVER_PK, STINGER_RELOAD_STEPS,
    LZ_DROP_WINDOW_S, LZ_HOVER_RADIUS_KM,
    IRGC_DEFENSE_MULT, IRGC_HOME_RADIUS_KM,
    LANCHESTER_Q, IRGC_PK, MARINE_PK,
    MV22_CAPACITY, OSPREYS_PER_SORTIE, _SORTIE_CYCLE, _N_SORTIES, N_TEAMS,
    DRONE_HELLFIRE, DRONE_PK, DRONE_ARRIVE_STEP, N_US_DRONES,
    SHIP_MAX_HP, SHIP_NAMES, SHIP_CLASSES,
    SHIP_SAM_RANGE_KM, SHIP_SAM_PK, SHIP_GUN_RANGE_KM, SHIP_GUN_PK,
    N_DRONE_BOATS, N_SHAHED, N_IRAN_BM, N_ISLAND_SHAHED,
    IRAN_BM_LETHAL_M, IRAN_BM_FLIGHT_STEPS, IRAN_BM_SALVO_STEP,
    IRAN_BM_INTERCEPT_PK, IRAN_BM_PEAK_ALT_M,
    ISLAND_SHAHED_SALVO_STEP,
    EW_IRGC_PK_MULT, EW_IRGC_DEFENSE_MULT_ADJ, EW_MANPADS_PK_MULT,
    EW_MILDEC_FRACTION, EW_MILDEC_DELAY_STEPS, EW_SHAHED_ABORT_RATE,
    EW_SHIP_SAM_PK_MULT,
    N_STEPS, STEP_S, SIM_DATE, SIM_BASE_H,
    LAT_KM, ENGAGE_KM,
    IRGC_CLUSTERS, CLUSTER_NAMES, LZS, LZ_NAMES,
    SHAHED_SPEED_KPS, DBOAT_SPEED_KPS,
)
from persian_gulf_simulation.simulation.spatial import ts_hhmm


def _card(title, accent, rows):
    base = (
        'font-family:"Courier New",monospace;'
        'background:#000000;color:#c9d1d9;'
        'padding:14px 18px;'
        f'border-left:5px solid {accent};'
        'min-width:320px;font-size:12px;line-height:1.5'
    )
    title_style = (
        f'font-weight:bold;color:{accent};'
        'font-family:"Courier New",monospace;'
        'font-size:14px;letter-spacing:0.05em;margin-bottom:8px'
    )
    sep = '<hr style="border:0;border-top:1px solid #333333;margin:8px 0"/>'
    tl  = 'style="color:#8b949e;font-family:\'Courier New\',monospace;padding:2px 14px 2px 0;white-space:nowrap;vertical-align:top"'
    tv  = 'style="color:#e6edf3;font-family:\'Courier New\',monospace;padding:2px 0"'
    th = 'style="color:#c9d1d9;font-family:\'Courier New\',monospace;padding:4px 0 2px 0;font-weight:bold"'
    rows_html = "".join(
        sep if k == "—" else
        f'<tr><td colspan="2" {th}>{k}</td></tr>' if v == "" else
        f'<tr><td {tl}>{k}</td><td {tv}>{v}</td></tr>'
        for k, v in rows
    )
    return (
        f'<![CDATA[<div style="{base}">'
        f'<div style="{title_style}">{title}</div>'
        f'{sep}'
        f'<table style="width:100%;border-collapse:collapse">{rows_html}</table>'
        f'</div>]]>'
    )


def _alive_badge(alive, alive_label="ALIVE", dead_label="KIA"):
    if alive:
        return f'<span style="color:#3fb950;font-weight:bold">&#9679; {alive_label}</span>'
    return f'<span style="color:#f85149;font-weight:bold">&#10005; {dead_label}</span>'


def _pct(n, d):
    """Return 'N/D (XX%)' string; safe against d=0."""
    return f"{n}/{d}  ({100 * n // max(d, 1)}%)"


def _speed_stats(track):
    """Return (avg_kmh, peak_kmh) computed from gx:Track points.
    Only alive steps (hp > 0) are included; stationary steps count as 0 speed.
    """
    if not track or len(track) < 2:
        return 0.0, 0.0
    total_dist_km = 0.0
    peak_kmh = 0.0
    for i in range(1, len(track)):
        s1, lon1, lat1, hp1 = track[i - 1]
        s2, lon2, lat2, hp2 = track[i]
        if hp1 <= 0 or hp2 <= 0:
            continue
        dt_steps = max(s2 - s1, 1)
        dt_h = dt_steps * STEP_S / 3600.0
        mid_lat = (lat1 + lat2) / 2.0
        dlon_km = (lon2 - lon1) * 111.0 * math.cos(math.radians(mid_lat))
        dlat_km = (lat2 - lat1) * LAT_KM
        dist_km_val = math.sqrt(dlon_km ** 2 + dlat_km ** 2)
        step_kmh = dist_km_val / dt_h
        total_dist_km += dist_km_val
        peak_kmh = max(peak_kmh, step_kmh)
    alive_pts = [(s, lo, la) for s, lo, la, hp in track if hp > 0]
    if len(alive_pts) < 2:
        return 0.0, peak_kmh
    elapsed_h = (alive_pts[-1][0] - alive_pts[0][0]) * STEP_S / 3600.0
    avg_kmh = total_dist_km / elapsed_h if elapsed_h > 0 else 0.0
    return avg_kmh, peak_kmh


def _fmt_speed(avg_kmh, peak_kmh, use_knots=False):
    """Format speed row value; optionally add knots."""
    if use_knots:
        avg_kts  = avg_kmh  / 1.852
        peak_kts = peak_kmh / 1.852
        return f"avg {avg_kts:.1f} kts  /  peak {peak_kts:.1f} kts"
    return f"avg {avg_kmh:.1f} km/h  /  peak {peak_kmh:.1f} km/h"


# ---------------------------------------------------------------------------
# INDIVIDUAL UNIT DESCRIPTIONS
# ---------------------------------------------------------------------------

def _marine_desc(m, stinger_kills, ship_loss_kills=None, hp_override=None):
    hp = hp_override if hp_override is not None else m.hp
    alive = hp > 0
    if not alive:
        if ship_loss_kills and m.agent_id in ship_loss_kills:
            cause = "Ship sunk (undeployed / airborne)"
        elif m.agent_id in stinger_kills:
            cause = "Stinger MANPADS (in-flight)"
        else:
            cause = "IRGC Ground Fire"
        dead_at = ts_hhmm(m.dead_step) if m.dead_step else "—"
    else:
        cause  = "—"
        dead_at = "—"
    hp_bar = ("&#9608;" * hp) + ("&#9617;" * (MARINE_HP - hp))
    avg_v, peak_v = _speed_stats(m.track)
    steps_alive = sum(1 for _, _, _, h in m.track if h > 0) if m.track else 0
    return _card(f"USMC FIRETEAM  {m.agent_id}", "#3fb950", [
        ("Status",         _alive_badge(alive)),
        ("HP",             f"{hp_bar}  {_pct(hp, MARINE_HP)}"),
        ("Personnel",      f"{hp * 4}/{MARINE_HP * 4} men  ({100 * hp // max(MARINE_HP, 1)}% effective)"),
        ("Engage Range",   f"{ENGAGE_KM} km  /  Pk={MARINE_PK}  ({int(MARINE_PK*100)}%)/step"),
        ("—", ""),
        ("Speed",          _fmt_speed(avg_v, peak_v)),
        ("Steps Alive",    f"{steps_alive} of {N_STEPS}  ({steps_alive * STEP_S // 60} min)"),
        ("LZ Target",      f"{m.lz[0]:.4f}°E  {m.lz[1]:.4f}°N"),
        ("—", ""),
        ("Time of Death",  dead_at),
        ("Cause of Death", cause),
    ])


def _irgc_desc(s, cluster_idx, hp_override=None):
    cname = CLUSTER_NAMES[cluster_idx] if 0 <= cluster_idx < len(CLUSTER_NAMES) else "Unknown"
    hp    = hp_override if hp_override is not None else s.hp
    alive = hp > 0
    hp_bar = ("&#9608;" * hp) + ("&#9617;" * (IRGC_HP - hp))
    avg_v, peak_v = _speed_stats(s.track)
    # Home cluster centroid for context
    if 0 <= cluster_idx < len(IRGC_CLUSTERS):
        hlon, hlat, _, _ = IRGC_CLUSTERS[cluster_idx]
        home_str = f"{hlon:.4f}°E  {hlat:.4f}°N  ({cname})"
    else:
        home_str = "Unknown"
    eff_pk   = IRGC_PK * EW_IRGC_PK_MULT
    eff_def  = IRGC_DEFENSE_MULT * EW_IRGC_DEFENSE_MULT_ADJ
    return _card(f"IRGC SQUAD  {s.agent_id}", "#f85149", [
        ("Status",         _alive_badge(alive, "DEFENDING", "NEUTRALIZED")),
        ("HP",             f"{hp_bar}  {_pct(hp, IRGC_HP)}"),
        ("Cluster",        cname),
        ("Home Position",  home_str),
        ("—", ""),
        ("Base Pk",        f"{IRGC_PK}  ({int(IRGC_PK*100)}%)/step  ×EW {EW_IRGC_PK_MULT:.2f} = {eff_pk:.3f} effective"),
        ("Def. Bonus",     f"×{IRGC_DEFENSE_MULT} within {IRGC_HOME_RADIUS_KM} km  ×EW adj {EW_IRGC_DEFENSE_MULT_ADJ:.2f} = ×{eff_def:.2f} net"),
        ("MILDEC",         f"{int(EW_MILDEC_FRACTION*100)}% of squads misdirected ×{EW_MILDEC_DELAY_STEPS} steps" if EW_MILDEC_FRACTION > 0 else "Inactive"),
        ("Speed",          _fmt_speed(avg_v, peak_v)),
        ("Neutralized At", ts_hhmm(s.dead_step) if not alive and s.dead_step else "—"),
    ])


def _stinger_desc(st, stats, hp_override=None):
    air_kills = stats["stinger_air_kills"].get(st.agent_id, 0)
    hp        = hp_override if hp_override is not None else st.hp
    alive     = hp > 0
    hp_bar    = ("&#9608;" * hp) + ("&#9617;" * (STINGER_HP - hp))
    avg_v, peak_v = _speed_stats(st.track)
    eff_pk        = STINGER_PK       * EW_MANPADS_PK_MULT
    eff_hover_pk  = STINGER_HOVER_PK * EW_MANPADS_PK_MULT
    ft_kills = sum(1 for aid in stats["stinger_kills"]
                   if True)   # conservative — all stinger kills pooled
    return _card(f"STINGER MANPADS  {st.agent_id}", "#d29922", [
        ("Status",              _alive_badge(alive, "ACTIVE", "DESTROYED")),
        ("HP",                  f"{hp_bar}  {_pct(hp, STINGER_HP)}"),
        ("Speed",               _fmt_speed(avg_v, peak_v)),
        ("—", ""),
        ("WEZ Radius",          f"{STINGER_WEZ_KM} km"),
        ("Reload Cycle",        f"{STINGER_RELOAD_STEPS} step(s)  ({STINGER_RELOAD_STEPS * STEP_S}s between shots)"),
        ("Pk — Transit",        f"{STINGER_PK} base  ×EW {EW_MANPADS_PK_MULT:.2f} = {eff_pk:.3f} effective  ({int(eff_pk*100)}%)"),
        ("Pk — Drop Window",    f'<span style="color:#f85149;font-weight:bold">'
                                 f'{STINGER_HOVER_PK} base  ×EW {EW_MANPADS_PK_MULT:.2f} = {eff_hover_pk:.3f}</span>'
                                 f'  ({LZ_DROP_WINDOW_S}s hover window)'),
        ("Aircraft Kills",      f"{air_kills} Osprey(s) confirmed"),
        ("Destroyed At",        ts_hhmm(st.dead_step) if not alive and st.dead_step else "—"),
    ])


def _osprey_desc(ov, stats, hp_override=None):
    trips_done  = stats["osprey_trips_done"].get(ov.agent_id, 0)
    fteams_del  = stats["osprey_fteams_del"].get(ov.agent_id, 0)
    total_trips = len(stats["osprey_trips_map"].get(ov.agent_id, []))
    alive       = hp_override > 0 if hp_override is not None else ov.hp > 0
    cap         = total_trips * MV22_CAPACITY
    men_del     = fteams_del * 4
    men_cap     = cap * 4
    avg_v, peak_v = _speed_stats(ov.track)
    return _card(f"MV-22 OSPREY  {ov.agent_id}", "#58a6ff", [
        ("Status",              _alive_badge(alive, "OPERATIONAL", "SHOT DOWN")),
        ("Speed",               _fmt_speed(avg_v, peak_v)),
        ("—", ""),
        ("Sorties Assigned",    str(total_trips)),
        ("Sorties Completed",   f"{_pct(trips_done, total_trips)}"),
        ("Fireteams Delivered", f"{fteams_del}/{cap}  ({100 * fteams_del // max(cap, 1)}% of planned load)"),
        ("Men Ashore",          f"{men_del}/{men_cap}  ({100*men_del//max(men_cap,1)}% capacity)"),
        ("Round-trip Cycle",    f"{_SORTIE_CYCLE} steps  ({_SORTIE_CYCLE} min)"),
        ("Capacity/Sortie",     f"{MV22_CAPACITY} fireteams  ({MV22_CAPACITY * 4} men)"),
        ("Shot Down At",        ts_hhmm(ov.dead_step) if not alive and ov.dead_step else "—"),
    ])


def _drone_desc(d, stats, hp_override=None):
    kills  = stats["drone_kill_count"].get(d.agent_id, 0)
    fired  = stats["drone_ammo_fired"].get(d.agent_id, 0)
    remain = d.drone_ammo if d.drone_ammo is not None else (DRONE_HELLFIRE - fired)
    fired_bar = ("&#9608;" * fired) + ("&#9617;" * max(0, DRONE_HELLFIRE - fired))
    hit_pct   = f"{100 * kills // max(fired, 1)}%" if fired > 0 else "—"
    avg_v, peak_v = _speed_stats(d.track)
    return _card(f"MQ-9 REAPER  {d.agent_id}", "#79c0ff", [
        ("Status",            _alive_badge(hp_override > 0 if hp_override is not None else d.hp > 0, "OPERATIONAL", "LOST")),
        ("Speed",             _fmt_speed(avg_v, peak_v)),
        ("—", ""),
        ("Hellfire Load",     f"{DRONE_HELLFIRE} missiles per airframe"),
        ("Missiles Fired",    f"{fired_bar}  {_pct(fired, DRONE_HELLFIRE)} expended"),
        ("Missiles Remaining",f"{remain}/{DRONE_HELLFIRE}"),
        ("Strike Pk",         f"{DRONE_PK}  ({int(DRONE_PK * 100)}%) per Hellfire engagement"),
        ("Confirmed Kills",   f"{kills} IRGC  (hit rate: {hit_pct})"),
        ("On Station From",   f"Step {DRONE_ARRIVE_STEP}  ({ts_hhmm(DRONE_ARRIVE_STEP)})"),
        ("Orbit Pattern",     f"Continuous  ({N_STEPS - DRONE_ARRIVE_STEP} steps on-station)"),
    ])


def _ship_desc(ship, stats, hp_override=None):
    sid      = ship.agent_id
    max_hp   = SHIP_MAX_HP[sid]
    db_hits  = stats["ship_db_hits"].get(sid, 0)
    sh_hits  = stats["ship_sh_hits"].get(sid, 0)
    bm_hits  = stats.get("ship_bm_hits", {}).get(sid, 0)
    total_dmg = db_hits + sh_hits + bm_hits
    hp       = hp_override if hp_override is not None else ship.hp
    pct_dmg  = f"{100 * total_dmg // max_hp}%" if max_hp else "0%"
    hp_bar   = ("&#9608;" * hp) + ("&#9617;" * (max_hp - hp))
    eff_sam  = SHIP_SAM_PK * EW_SHIP_SAM_PK_MULT
    if hp <= 0:
        status = '<span style="color:#f85149;font-weight:bold">&#9760; SUNK</span>'
    elif hp <= max_hp // 2:
        status = '<span style="color:#d29922;font-weight:bold">&#9888; DAMAGED</span>'
    else:
        status = '<span style="color:#3fb950;font-weight:bold">&#9679; OPERATIONAL</span>'
    avg_v, peak_v = _speed_stats(ship.track)
    rows = [
        ("Status",            status),
        ("Hull",              SHIP_CLASSES[sid]),
        ("HP",                f"{hp_bar}  {_pct(hp, max_hp)} integrity"),
        ("Speed",             _fmt_speed(avg_v, peak_v, use_knots=True)),
        ("—", ""),
        ("Total Damage",      f"{total_dmg}/{max_hp} hits  ({pct_dmg} capacity lost)"),
        ("  Drone Boat Hits", f"{db_hits}  ({100 * db_hits // max(total_dmg, 1)}% of hits)"),
        ("  Shahed Hits",     f"{sh_hits}  ({100 * sh_hits // max(total_dmg, 1)}% of hits)"),
    ]
    if bm_hits:
        rows.append(("  BM Hits",    f'<span style="color:#f85149">{bm_hits}  ({100*bm_hits//max(total_dmg,1)}% of hits)</span>'))
    rows += [
        ("—", ""),
        ("SAM System",        f"Pk={SHIP_SAM_PK} base  ×EW {EW_SHIP_SAM_PK_MULT:.2f} = {eff_sam:.3f}  (range {SHIP_SAM_RANGE_KM} km)"),
        ("Gun System",        f"Pk={SHIP_GUN_PK}  ({int(SHIP_GUN_PK*100)}%)  (range {SHIP_GUN_RANGE_KM} km)"),
        ("Sunk At",           ts_hhmm(ship.dead_step) if hp <= 0 and ship.dead_step else "—"),
    ]
    return _card(f"{SHIP_NAMES[sid]}", "#58a6ff", rows)


def _dboat_desc(db, hp_override=None):
    hp     = hp_override if hp_override is not None else db.hp
    alive  = hp > 0
    hp_bar = ("&#9608;" * hp) + ("&#9617;" * (DBOAT_HP - hp))
    avg_v, peak_v = _speed_stats(db.track)
    rated_kts = DBOAT_SPEED_KPS * 3600 / 1.852
    return _card(f"IRGCN DRONE BOAT  {db.agent_id}", "#ff8c00", [
        ("Status",    _alive_badge(alive, "ACTIVE", "DESTROYED")),
        ("HP",        f"{hp_bar}  {_pct(hp, DBOAT_HP)}"),
        ("Speed",     _fmt_speed(avg_v, peak_v, use_knots=True)),
        ("Rated",     f"{rated_kts:.0f} knots max  ({DBOAT_SPEED_KPS*3600:.0f} km/h)"),
        ("Warhead",   "Shaped charge / ram — catastrophic hull breach on impact"),
        ("Target",    f"{db.lz[0]:.4f}°E  {db.lz[1]:.4f}°N"),
        ("Countermeasure", f"Ship gun Pk={SHIP_GUN_PK}  range={SHIP_GUN_RANGE_KM} km"),
        ("Killed At", ts_hhmm(db.dead_step) if not alive and db.dead_step else "—"),
    ])


def _shahed_desc(sh, hp_override=None, is_island=False):
    hp    = hp_override if hp_override is not None else sh.hp
    alive = hp > 0
    hp_bar = ("&#9608;" * hp) + ("&#9617;" * (SHAHED_HP - hp))
    avg_v, peak_v = _speed_stats(sh.track)
    rated_kmh = SHAHED_SPEED_KPS * 3600
    target_label = "USMC fireteams on island" if is_island else "US Navy ship"
    intercept_sys = "Ship SAM / IRGC" if is_island else f"Ship SAM Pk={SHIP_SAM_PK}×{EW_SHIP_SAM_PK_MULT:.2f}={SHIP_SAM_PK*EW_SHIP_SAM_PK_MULT:.3f}"
    abort_note = (f"GPS spoofing: {int(EW_SHAHED_ABORT_RATE*100)}% abort rate applied"
                  if EW_SHAHED_ABORT_RATE > 0 else "GPS spoofing: Inactive")
    return _card(f"{'ISLAND ' if is_island else ''}SHAHED-136  {sh.agent_id}",
                 "#f85149" if is_island else "#c0392b", [
        ("Status",    _alive_badge(alive, "IN-FLIGHT", "DESTROYED")),
        ("HP",        f"{hp_bar}  {_pct(hp, SHAHED_HP)}"),
        ("Speed",     _fmt_speed(avg_v, peak_v)),
        ("Rated",     f"{rated_kmh:.0f} km/h cruise  (terrain-following, 75 m AGL)"),
        ("Warhead",   "50 kg HE fragmentation  (lethal r=30 m vs infantry)"),
        ("Target",    f"{sh.lz[0]:.4f}°E  {sh.lz[1]:.4f}°N  [{target_label}]"),
        ("Intercept", intercept_sys),
        ("EW",        abort_note),
        ("Killed At", ts_hhmm(sh.dead_step) if not alive and sh.dead_step else "—"),
    ])


# ---------------------------------------------------------------------------
# KML — FOLDER SUMMARY DESCRIPTIONS
# ---------------------------------------------------------------------------

def _marine_folder_desc(marines, stinger_kills, ship_loss_kills=None, stats=None):
    total  = len(marines)
    alive  = sum(1 for m in marines if m.hp > 0)
    dead   = total - alive
    sk     = len(stinger_kills)
    slk    = len(ship_loss_kills) if ship_loss_kills else 0
    ground = dead - sk - slk
    survive_pct = 100 * alive // max(total, 1)
    rows = [
        ("Total Force",      f"{total} fireteams  ({total * 4} men)"),
        ("Alive",            f'<span style="color:#3fb950">{_pct(alive, total)}  ({alive * 4} men alive)</span>'),
        ("Combat Effective", f'{survive_pct}% of initial force'),
        ("—", ""),
        ("Total KIA",        f'<span style="color:#f85149">{_pct(dead, total)}  ({dead * 4} men)</span>'),
        ("  Ground Fire",    f"{_pct(ground, dead)}  ({ground * 4} men) — IRGC engagement"),
        ("  Stinger MANPADS",f"{_pct(sk, dead)}  ({sk * 4} men) — in-flight kill"),
    ]
    if slk:
        rows.append(("  Ship-loss KIA",
                     f'<span style="color:#d29922">{_pct(slk, dead)}  ({slk*4} men) — ship sunk (undeployed)</span>'))
    rows += [
        ("—", ""),
        ("Combat Parameters",""),
        ("  USMC Pk",        f"{MARINE_PK}  ({int(MARINE_PK * 100)}%)/step  (Lanchester Q={LANCHESTER_Q}×IRGC_Pk)"),
        ("  IRGC Pk",        f"{IRGC_PK}  ({int(IRGC_PK * 100)}%)/step base"),
        ("  Engage Range",   f"{ENGAGE_KM} km"),
        ("LZs",              "  ".join(LZ_NAMES.values())),
    ]
    if stats:
        t_men = sum(stats["osprey_fteams_del"].values()) * 4
        cancelled = stats.get("sorties_cancelled", 0)
        rows.append(("  Men Ashore",     f"{t_men} delivered by Osprey"))
        if cancelled:
            rows.append(("  Sorties Lost",
                         f'<span style="color:#d29922">{cancelled} flights aborted (ship sunk)</span>'))
    return _card("US MARINE FORCE — BATTLE SUMMARY", "#3fb950", rows)


def _irgc_folder_desc(irgc, irgc_cluster_map=None):
    total = len(irgc)
    alive = sum(1 for s in irgc if s.hp > 0)
    neut  = total - alive
    eff_pk  = IRGC_PK  * EW_IRGC_PK_MULT
    eff_def = IRGC_DEFENSE_MULT * EW_IRGC_DEFENSE_MULT_ADJ
    rows = [
        ("Total",           f"{total} squads  ({total * 4} men)"),
        ("Alive",           f'<span style="color:#3fb950">{_pct(alive, total)}  ({alive * 4} men)</span>'),
        ("Neutralized",     f'<span style="color:#f85149">{_pct(neut, total)}  ({neut * 4} men)</span>'),
        ("—", ""),
        ("Combat Parameters",""),
        ("  Base Pk",       f"{IRGC_PK}  ({int(IRGC_PK*100)}%)/step"),
        ("  EW adj Pk",     f"×{EW_IRGC_PK_MULT:.2f} = {eff_pk:.3f} effective  ({int(eff_pk*100)}%)"),
        ("  Defense Mult",  f"×{IRGC_DEFENSE_MULT} base  ×EW {EW_IRGC_DEFENSE_MULT_ADJ:.2f} = ×{eff_def:.2f} in home radius"),
        ("  Home Radius",   f"{IRGC_HOME_RADIUS_KM} km  (fortified positions)"),
        ("  Fortified Pk",  f"{IRGC_PK * eff_def:.4f}  ({int(IRGC_PK * eff_def * 100)}%) at home"),
    ]
    if EW_MILDEC_FRACTION > 0:
        rows.append(("  MILDEC",
                     f"{int(EW_MILDEC_FRACTION*100)}% squads ({int(total*EW_MILDEC_FRACTION)} units) "
                     f"misdirected for {EW_MILDEC_DELAY_STEPS} steps"))
    # Per-cluster breakdown
    if irgc_cluster_map:
        rows.append(("—", ""))
        rows.append(("Cluster Breakdown", ""))
        cluster_totals: dict = {}
        cluster_alive_ct: dict = {}
        for s in irgc:
            ci    = irgc_cluster_map.get(s.agent_id, 0)
            cname = CLUSTER_NAMES[ci] if 0 <= ci < len(CLUSTER_NAMES) else "Unknown"
            cluster_totals[cname]     = cluster_totals.get(cname, 0) + 1
            cluster_alive_ct[cname]   = cluster_alive_ct.get(cname, 0) + (1 if s.hp > 0 else 0)
        for cname in CLUSTER_NAMES:
            ct = cluster_totals.get(cname, 0)
            ca = cluster_alive_ct.get(cname, 0)
            if ct == 0:
                continue
            bar  = ("&#9608;" * ca) + ("&#9617;" * (ct - ca))
            rows.append((f"  {cname}", f"{bar} {_pct(ca, ct)} alive  ({ca*4}/{ct*4} men)"))
    return _card("IRGC DEFENDERS — BATTLE SUMMARY", "#f85149", rows)


def _stinger_folder_desc(stingers, stats):
    total      = len(stingers)
    alive      = sum(1 for s in stingers if s.hp > 0)
    dest       = total - alive
    air_kills  = sum(stats["stinger_air_kills"].values())
    ft_killed  = len(stats["stinger_kills"])
    eff_pk     = STINGER_PK       * EW_MANPADS_PK_MULT
    eff_hov    = STINGER_HOVER_PK * EW_MANPADS_PK_MULT
    rows = [
        ("Teams Deployed",   f"{total}  ({STINGER_RATIO*100:.0f}% of IRGC, capped at {total})"),
        ("Alive",            f'<span style="color:#3fb950">{_pct(alive, total)}</span>'),
        ("Destroyed",        f'<span style="color:#f85149">{_pct(dest, total)}</span>'),
        ("—", ""),
        ("Aircraft Down",    f"{_pct(air_kills, OSPREYS_PER_SORTIE)} Ospreys shot down"),
        ("Fireteam KIA",     f"{ft_killed} fireteams  ({ft_killed * 4} men killed in-flight)"),
        ("—", ""),
        ("Weapon Parameters",""),
        ("  WEZ",            f"{STINGER_WEZ_KM} km"),
        ("  Reload",         f"{STINGER_RELOAD_STEPS} step(s)  ({STINGER_RELOAD_STEPS * STEP_S}s between shots)"),
        ("  Pk Transit",     f"{STINGER_PK} base  ×EW {EW_MANPADS_PK_MULT:.2f} = {eff_pk:.3f}  ({int(eff_pk*100)}%)"),
        ("  Pk Hover",       f'<span style="color:#f85149">{STINGER_HOVER_PK} base  '
                              f'×EW {EW_MANPADS_PK_MULT:.2f} = {eff_hov:.3f}  ({int(eff_hov*100)}%)</span>'
                              f'  ({LZ_DROP_WINDOW_S}s drop window)'),
    ]
    # Top-performing teams
    ak = stats["stinger_air_kills"]
    top = sorted(ak.items(), key=lambda x: -x[1])
    if top:
        rows.append(("—", ""))
        rows.append(("Top Teams (kills)", ""))
        for tid, k in top[:5]:
            rows.append((f"  {tid}", f"{k} Osprey kill{'s' if k != 1 else ''}"))
    return _card("IRGC STINGER MANPADS — SUMMARY", "#d29922", rows)


def _osprey_folder_desc(ospreys, stats, flights):
    total        = len(ospreys)
    alive        = sum(1 for ov in ospreys if ov.hp > 0)
    down         = total - alive
    t_trips_done = sum(stats["osprey_trips_done"].values())
    t_trips_plan = sum(len(v) for v in stats["osprey_trips_map"].values())
    t_fteams     = sum(stats["osprey_fteams_del"].values())
    t_men        = t_fteams * 4
    int_fids     = [k for k in flights.keys() if isinstance(k, int)]
    n_flights    = max(int_fids) + 1 if int_fids else 0
    max_cap_men  = t_trips_plan * MV22_CAPACITY * 4
    cancelled    = stats.get("sorties_cancelled", 0)
    rows = [
        ("Aircraft",           f"{total} MV-22B Ospreys"),
        ("Operational",        f'<span style="color:#3fb950">{_pct(alive, total)}</span>'),
        ("Shot Down",          f'<span style="color:#f85149">{_pct(down, total)}</span>'),
        ("—", ""),
        ("Sorties Planned",    f"{t_trips_plan}  ({_N_SORTIES} waves × {total} aircraft)"),
        ("Sorties Completed",  f"{_pct(t_trips_done, t_trips_plan)}"),
        ("Sorties Cancelled",  f'<span style="color:#d29922">{cancelled} aborted (ship sunk)</span>' if cancelled else "0"),
        ("—", ""),
        ("Capacity/Sortie",    f"{MV22_CAPACITY} fireteams  ({MV22_CAPACITY * 4} men)"),
        ("Planned Lift",       f"{t_trips_plan * MV22_CAPACITY} fireteams  ({max_cap_men} men)"),
        ("Men Ashore",         f"{t_men}  ({100 * t_men // max(max_cap_men, 1)}% of planned capacity)"),
        ("Round-trip Cycle",   f"{_SORTIE_CYCLE} min"),
        ("LZs Served",         "  ".join(LZ_NAMES.values())),
    ]
    return _card("MV-22 OSPREY FLIGHT OPS — SUMMARY", "#58a6ff", rows)


def _drone_folder_desc(drones, stats):
    total   = len(drones)
    fired   = sum(stats["drone_ammo_fired"].values())
    kills   = sum(stats["drone_kill_count"].values())
    hit_pct = f"{100 * kills // max(fired, 1)}%" if fired else "—"
    cap     = total * DRONE_HELLFIRE
    remain  = cap - fired
    rows = [
        ("Airframes",       f"{total} MQ-9 Reapers"),
        ("Hellfire Capacity",f"{cap} total  ({DRONE_HELLFIRE} per airframe)"),
        ("—", ""),
        ("Missiles Fired",  f"{_pct(fired, cap)} expended"),
        ("Missiles Remaining",f"{remain}/{cap}  ({100*remain//max(cap,1)}%)"),
        ("IRGC Kills",      f"{kills}  ({100*kills//max(len(drones)*DRONE_HELLFIRE,1)}% of capacity → kills)"),
        ("Hit Rate",        f"{hit_pct}  (fired: {fired}  confirmed: {kills})"),
        ("Strike Pk",       f"{DRONE_PK}  ({int(DRONE_PK * 100)}%) per Hellfire engagement"),
        ("—", ""),
        ("On Station",      f"Step {DRONE_ARRIVE_STEP}  ({ts_hhmm(DRONE_ARRIVE_STEP)})  through end"),
        ("Active Steps",    f"{N_STEPS - DRONE_ARRIVE_STEP}  ({(N_STEPS - DRONE_ARRIVE_STEP) * STEP_S // 60} min)"),
    ]
    # Per-drone breakdown
    rows.append(("—", ""))
    rows.append(("Per-Airframe", "Kills / Fired"))
    for d in drones:
        dk = stats["drone_kill_count"].get(d.agent_id, 0)
        df = stats["drone_ammo_fired"].get(d.agent_id, 0)
        rows.append((f"  {d.agent_id}", f"{dk} kills  /  {df} fired"))
    return _card("MQ-9 REAPER DRONE OPS — SUMMARY", "#79c0ff", rows)


def _dboat_folder_desc(drone_boats, stats):
    total      = len(drone_boats)
    destroyed  = sum(1 for d in drone_boats if d.hp <= 0)
    total_hits = sum(stats["ship_db_hits"].values())
    sd         = stats["db_shot_down"]
    rated_kts  = DBOAT_SPEED_KPS * 3600 / 1.852
    rows = [
        ("Boats Launched",  f"{total} FIAC drone boats"),
        ("Shot Down",       f'<span style="color:#3fb950">{_pct(sd, total)}</span>  (ship gun Pk={SHIP_GUN_PK})'),
        ("Impacted Ships",  f'<span style="color:#f85149">{_pct(total_hits, total)} impacts</span>'),
        ("Still Active",    f"{_pct(total - destroyed, total)}"),
        ("—", ""),
        ("Performance",     ""),
        ("  Speed",         f"{rated_kts:.0f} knots  ({DBOAT_SPEED_KPS*3600:.0f} km/h)"),
        ("  Warhead",       "Shaped charge / ram — catastrophic on impact"),
        ("  Countermeasure",f"Ship gun  Pk={SHIP_GUN_PK}  range={SHIP_GUN_RANGE_KM} km"),
        ("—", ""),
        ("Ship Hit Distribution", ""),
    ]
    for sid, v in stats["ship_db_hits"].items():
        rows.append((f"  {SHIP_NAMES.get(sid, sid)}", f"{v} hit{'s' if v != 1 else ''}"))
    return _card("IRGCN DRONE BOAT SWARM — SUMMARY", "#ff8c00", rows)


def _shahed_folder_desc(shahed, stats):
    total      = len(shahed)
    destroyed  = sum(1 for s in shahed if s.hp <= 0)
    total_hits = sum(stats["ship_sh_hits"].values())
    si         = stats["sh_shot_down"]
    eff_sam    = SHIP_SAM_PK * EW_SHIP_SAM_PK_MULT
    rated_kmh  = SHAHED_SPEED_KPS * 3600
    abort_note = (f"{int(EW_SHAHED_ABORT_RATE*100)}% aborted (GPS spoofing)"
                  if EW_SHAHED_ABORT_RATE > 0 else "GPS spoofing: Inactive")
    rows = [
        ("Launched",        f"{total} Shahed-136 loitering munitions"),
        ("Intercepted",     f'<span style="color:#3fb950">{_pct(si, total)}</span>  (SAM Pk={SHIP_SAM_PK}×{EW_SHIP_SAM_PK_MULT:.2f}={eff_sam:.3f})'),
        ("Impacted Ships",  f'<span style="color:#f85149">{_pct(total_hits, total)}</span>'),
        ("Still Airborne",  f"{_pct(total - destroyed, total)}"),
        ("EW",              abort_note),
        ("—", ""),
        ("Performance",     ""),
        ("  Speed",         f"{rated_kmh:.0f} km/h cruise  (terrain-following 75 m AGL)"),
        ("  Warhead",       "50 kg HE fragmentation"),
        ("  SAM WEZ",       f"{SHIP_SAM_RANGE_KM} km  Pk={eff_sam:.3f} effective"),
        ("—", ""),
        ("Ship Hit Distribution", ""),
    ]
    for sid, v in stats["ship_sh_hits"].items():
        rows.append((f"  {SHIP_NAMES.get(sid, sid)}", f"{v} hit{'s' if v != 1 else ''}"))
    return _card("SHAHED-136 STRIKE PACKAGE — SUMMARY", "#c0392b", rows)


def _bm_folder_desc(iran_bm, stats):
    total   = len(iran_bm)
    bm_int  = stats.get("bm_intercepted", 0)
    bm_hit  = stats.get("bm_hits", 0)
    bm_mk   = stats.get("bm_marine_kills", 0)
    bm_pct_int = bm_int / total * 100 if total else 0
    bm_pct_hit = bm_hit / total * 100 if total else 0
    # SM-3 math
    n_ships      = 3
    shots_per_bm = n_ships   # one intercept attempt per ship per BM in range
    total_shots  = total * shots_per_bm
    expected_int = total * (1 - (1 - IRAN_BM_INTERCEPT_PK) ** n_ships)
    return _card("IRANIAN SRBM SALVO — FATEH-110 / ZELZAL-2", "#f85149", [
        ("Missiles Fired",     f'{total}  (Fateh-110 + Zelzal-2 mix)'),
        ("Salvo Time",         f'H+{IRAN_BM_SALVO_STEP} min  ({ts_hhmm(IRAN_BM_SALVO_STEP)})'),
        ("Launch Site",        "IRGC Bandar Abbas complex  (~150 km SE of Kharg Island)"),
        ("Flight Time",        f"~{IRAN_BM_FLIGHT_STEPS} min  (SRBM ballistic arc)"),
        ("Peak Altitude",      f"{IRAN_BM_PEAK_ALT_M/1000:.0f} km apogee  (~{IRAN_BM_PEAK_ALT_M/304.8:.0f},000 ft)"),
        ("—", ""),
        ("SM-3 Defence",       ""),
        ("  Ships Firing",     f"{n_ships}  ({shots_per_bm} shots/BM)"),
        ("  Intercept Pk",     f"{IRAN_BM_INTERCEPT_PK} per shot  (JP CBO 2019 assessment)"),
        ("  Expected Kills",   f"{expected_int:.1f}/{total}  ({expected_int/total*100:.1f}%)"),
        ("  Actual Intercepts",f'<span style="color:#3fb950">{_pct(bm_int, total)}  ({bm_pct_int:.1f}%)</span>'),
        ("—", ""),
        ("Impacts on Island",  f'<span style="color:#f85149">{bm_hit}/{total}  ({bm_pct_hit:.1f}%)</span>'),
        ("Lethal Radius",      f"{IRAN_BM_LETHAL_M} m  (soft targets, open terrain)"),
        ("Marine Kills",       f'<span style="color:#f85149;font-weight:bold">{bm_mk} fireteams  ({bm_mk*4} men)</span>'),
        ("—", ""),
        ("Weapon Mix",         "Fateh-110: CEP 10 m, 450 kg warhead, range 300 km"),
        ("",                   "Zelzal-2:  CEP 200 m, 600 kg warhead, unguided (range 200 km)"),
    ])


def _island_shahed_folder_desc(island_shahed, stats):
    total    = len(island_shahed)
    ish_down = stats.get("island_sh_shot_down", 0)
    ish_hit  = stats.get("island_sh_hits", 0)
    ish_mk   = stats.get("island_sh_marine_kills", 0)
    eff_sam  = SHIP_SAM_PK * EW_SHIP_SAM_PK_MULT
    rated_kmh = SHAHED_SPEED_KPS * 3600
    abort_note = (f"{int(EW_SHAHED_ABORT_RATE*100)}% aborted pre-launch (GPS spoofing)"
                  if EW_SHAHED_ABORT_RATE > 0 else "GPS spoofing: Inactive")
    return _card("IRANIAN ISLAND STRIKE — SHAHED-136 (MARINE TARGETS)", "#f85149", [
        ("Drones Launched",    f"{total}"),
        ("Salvo Time",         f'H+{ISLAND_SHAHED_SALVO_STEP} min  ({ts_hhmm(ISLAND_SHAHED_SALVO_STEP)})  '
                                f'(5 min after SRBM)'),
        ("Target",             "USMC fireteams at beach LZs  FALCON/EAGLE/VIPER/COBRA"),
        ("EW",                 abort_note),
        ("—", ""),
        ("Performance",        ""),
        ("  Speed",            f"{rated_kmh:.0f} km/h  (terrain-following, 75 m AGL)"),
        ("  Warhead",          "50 kg HE fragmentation  (lethal r=30 m vs infantry)"),
        ("—", ""),
        ("SAM Intercepts",     f'<span style="color:#3fb950">{_pct(ish_down, total)}</span>'
                                f'  (Pk={SHIP_SAM_PK}×{EW_SHIP_SAM_PK_MULT:.2f}={eff_sam:.3f})'),
        ("Reached Island",     f'<span style="color:#f85149">{_pct(ish_hit, total)}</span>'),
        ("Marine Kills",       f'<span style="color:#f85149;font-weight:bold">'
                                f'{ish_mk} fireteams  ({ish_mk*4} men)</span>'),
    ])


def _ship_folder_desc(ships, stats):
    sunk    = sum(1 for s in ships if s.hp <= 0)
    damaged = sum(1 for s in ships if 0 < s.hp < SHIP_MAX_HP[s.agent_id])
    ok      = sum(1 for s in ships if s.hp >= SHIP_MAX_HP[s.agent_id])
    db_total = sum(stats["ship_db_hits"].values())
    sh_total = sum(stats["ship_sh_hits"].values())
    total_hits = db_total + sh_total
    eff_sam  = SHIP_SAM_PK * EW_SHIP_SAM_PK_MULT
    n = len(ships)
    rows = [
        ("Ships",            f"{n} vessels  (Amphibious Ready Group)"),
        ("Operational",      f'<span style="color:#3fb950">{_pct(ok, n)}</span>'),
        ("Damaged",          f'<span style="color:#d29922">{_pct(damaged, n)}</span>'),
        ("Sunk",             f'<span style="color:#f85149">{_pct(sunk, n)}</span>'),
        ("—", ""),
        ("Total Hits",       f"{total_hits}  (boats: {db_total}  ·  Shahed: {sh_total})"),
        ("SAM System",       f"Pk={SHIP_SAM_PK} base  ×EW {EW_SHIP_SAM_PK_MULT:.2f} = {eff_sam:.3f}  "
                              f"(range {SHIP_SAM_RANGE_KM} km)"),
        ("Gun System",       f"Pk={SHIP_GUN_PK}  range={SHIP_GUN_RANGE_KM} km"),
        ("—", ""),
        ("Per-Vessel Status","HP / Hits / Sunk Time"),
    ]
    for s in ships:
        sid    = s.agent_id
        max_hp = SHIP_MAX_HP[sid]
        db     = stats["ship_db_hits"].get(sid, 0)
        sh     = stats["ship_sh_hits"].get(sid, 0)
        hp_bar = ("&#9608;" * s.hp) + ("&#9617;" * (max_hp - s.hp))
        sunk_t = f"  SUNK {ts_hhmm(s.dead_step)}" if s.hp <= 0 and s.dead_step else ""
        name   = SHIP_NAMES[sid].split("(")[0].strip()
        rows.append((name,
                     f"{hp_bar} {s.hp}/{max_hp}  boats:{db} shahed:{sh}{sunk_t}"))
    if stats.get("navy_dead", 0):
        rows.append(("—", ""))
        rows.append(("Navy Crew KIA",
                     f'<span style="color:#f85149">{stats["navy_dead"]} personnel KIA</span>'))
    return _card("US NAVAL GROUP — STATUS BOARD", "#58a6ff", rows)


# ---------------------------------------------------------------------------
# SCENARIO-LEVEL DOCUMENT DESCRIPTIONS
# ---------------------------------------------------------------------------

def _f35_strike_battle_desc(marines, irgc, stingers, ospreys, ships, stats,
                             survival_pct, n_irgc_pre, scenario_label="",
                             scenario_desc=None):
    """
    Document description for the F-35 coordinated strike + beach assault scenario.
    Includes pre-strike CEP/area-destruction analysis then battle outcome.
    """
    import math as _math

    ISLAND_AREA_M2  = 37_000_000

    weapons = [
        ("GBU-31 JDAM",  16, 2000, 120, 13, "4× F/A-18E/F (Al Udeid AB, 4 wpns each)"),
        ("GBU-32 JDAM",  24, 1000,  90, 10, "12× F-35B stealth (2 internal each)"),
        ("GBU-38 JDAM",  48,  500,  40,  9, "12× F-35B beast-mode (4 external each)"),
        ("TLAM Block V",  80,  450,  35, 10, "3× DDG escorts (~27 each)"),
    ]
    sead_row = ("AGM-88 HARM", 8, None, None, None, "2× EA-18G Growler (4 each, SEAD)")

    total_weapons = sum(w[1] for w in weapons)
    total_A_w     = sum(w[1] * _math.pi * w[3]**2 for w in weapons)
    coverage_frac = 1.0 - _math.exp(-total_A_w / ISLAND_AREA_M2)
    coverage_pct  = coverage_frac * 100.0

    r_L_rep, r_c_rep = 40.0, 9.0
    sspk_rep = 1.0 - _math.exp(-0.693 * (r_L_rep / r_c_rep)**2)
    pd_2wpn  = 1.0 - (1.0 - sspk_rep)**2

    killed_in_strike = round(n_irgc_pre * (1.0 - survival_pct))
    survived = n_irgc_pre - killed_in_strike

    alive_m   = sum(1 for m in marines   if m.hp > 0)
    alive_i   = sum(1 for s in irgc      if s.hp > 0)
    alive_st  = sum(1 for s in stingers  if s.hp > 0)
    sk        = len(stats["stinger_kills"])
    slk       = len(stats["ship_loss_kills"])
    destroyed_ov = sum(1 for ov in ospreys if ov.hp <= 0)
    d_kills   = sum(stats["drone_kill_count"].values())
    d_fired   = sum(stats["drone_ammo_fired"].values())
    d_hit_pct = f"{100*d_kills//max(d_fired,1)}%" if d_fired else "—"
    total_hits = (sum(stats["ship_db_hits"].values()) +
                  sum(stats["ship_sh_hits"].values()))
    sunk_ships = [SHIP_NAMES[s.agent_id] for s in ships if s.hp <= 0]
    island_held = alive_i == 0 and alive_st == 0
    outcome = ("USMC SECURED KHARG ISLAND" if island_held and not sunk_ships
               else "USMC SECURED — SHIPS LOST" if island_held
               else "IRGC REPELLED ASSAULT"     if alive_m == 0
               else "CONTESTED")
    out_color = "#3fb950" if island_held else "#f85149" if alive_m == 0 else "#d29922"
    ground_kia = len(marines) - alive_m - sk - slk
    navy_dead  = stats.get("navy_dead", 0)
    nm = len(marines); ni = len(irgc); nst = len(stingers)
    db_hits = sum(stats['ship_db_hits'].values())
    sh_hits = sum(stats['ship_sh_hits'].values())
    t_men   = sum(stats["osprey_fteams_del"].values()) * 4

    rows = [
        ("SCENARIO",          scenario_label or "F-35 Lightning Strike"),
    ]
    if scenario_desc:
        rows.append(("", f'<span style="color:#8b949e;font-style:italic">{scenario_desc}</span>'))
    rows += [
        ("DATE / TIME",       f"{SIM_DATE}  {SIM_BASE_H:02d}:00Z"),
        ("DURATION",          f"{N_STEPS} steps × {STEP_S}s = {N_STEPS*STEP_S//60} min"),
        ("OUTCOME",
         f'<span style="color:{out_color};font-weight:bold">{outcome}</span>'),
        ("—", ""),
        ("═══ PHASE 1 — F-35 PRE-STRIKE  H-HOUR ═══", ""),
        ("Strike window",     "All weapons simultaneous time-on-target (TOT ±2 min)"),
        ("F-35B sorties",     "12 stealth  +  12 beast-mode  (USS Tripoli LHA-7)"),
        ("Supporting",        "4× F/A-18E/F (Al Udeid)  ·  3× DDG Tomahawk  ·  2× EA-18G SEAD"),
        ("—", ""),
    ]
    for label, count, wt, r_L, cep, platform in weapons:
        a_w  = _math.pi * r_L**2 if r_L else 0
        sspk = 1.0 - _math.exp(-0.693 * (r_L / cep)**2) if r_L else 0
        rows.append((
            f"{label}  ×{count}",
            f"{wt:,} lb  ·  r_L={r_L} m  ·  CEP={cep} m  ·  SSPK={sspk*100:.1f}%  ·  {platform}"
        ))
    rows.append((f"{sead_row[0]}  ×{sead_row[1]}", sead_row[5]))
    rows += [
        ("—", ""),
        ("Total Rounds",
         f"{total_weapons} PGM + {sead_row[1]} HARM = {total_weapons + sead_row[1]} total"),
        ("Total Lethal Area",
         f"{total_A_w/1e6:.2f} km²  vs  {ISLAND_AREA_M2/1e6:.0f} km² island"),
        ("Island Coverage",
         f'<span style="color:#f85149;font-weight:bold">'
         f'{coverage_pct:.1f}% at 50% P_k  (Helmbold random-coverage model)</span>'),
        ("Aim-point P_d",
         f"SSPK={sspk_rep*100:.2f}%/wpn  →  P_d(2 wpns/aim-point)={pd_2wpn*100:.4f}%"),
        ("IRGC in Strike",
         f'<span style="color:#f85149">{killed_in_strike}/{n_irgc_pre}  '
         f'({(1-survival_pct)*100:.0f}% killed)  —  {survived} survivors</span>'),
        ("Survivability",
         f"{survival_pct*100:.0f}%:  hardened bunkers (2–3%)  ·  GPS jam → INS drift CEP (2–3%)"
         f"  ·  dispersed elements outside footprint (2–3%)"),
        ("—", ""),
        ("═══ PHASE 2 — BEACH ASSAULT ═══", ""),
        ("Insertion method",  "LCAC hovercraft + RHIB  (no Osprey — no MANPADS window)"),
        ("Marines Landed",    f"{nm} fireteams  ({nm*4} men)  —  LZs FALCON/EAGLE/VIPER/COBRA"),
        ("Men Ashore",        f"{t_men} delivered"),
        ("—", ""),
        ("═══ BATTLE OUTCOME ═══", ""),
        ("US MARINES",        f"{_pct(alive_m, nm)} fireteams  ({alive_m * 4} men alive)"),
        ("  Ground KIA",      f"{_pct(ground_kia, nm)}  ({ground_kia * 4} men)"),
        ("  Stinger KIA",     f"{_pct(sk, nm)}  ({sk * 4} men — MANPADS)"),
        ("IRGC Survivors",    f"{_pct(alive_i, ni)} alive after assault  ({alive_i*4} men)"),
        ("  Stingers",        f"{_pct(nst - alive_st, nst)} MANPADS teams destroyed"),
        ("Drone Strikes",     f"{d_kills} IRGC kills  (fired: {d_fired}  hit rate: {d_hit_pct})"),
        ("OSPREYS",           f"{_pct(destroyed_ov, OSPREYS_PER_SORTIE)} shot down"),
        ("—", ""),
        ("═══ NAVAL ═══", ""),
        ("Ship Hits",         f"{total_hits} total  (boats: {db_hits}  ·  Shahed: {sh_hits})"),
        ("Ships Sunk",        ", ".join(sunk_ships) if sunk_ships else "None"),
        ("Drone Boats",
         f"{_pct(db_hits, N_DRONE_BOATS)} impacts  ({_pct(stats['db_shot_down'], N_DRONE_BOATS)} destroyed)"),
        ("Shahed",
         f"{_pct(sh_hits, N_SHAHED)} impacts  ({_pct(stats['sh_shot_down'], N_SHAHED)} intercepted)"),
    ]
    for ship in ships:
        sid    = ship.agent_id
        max_hp = SHIP_MAX_HP[sid]
        db     = stats["ship_db_hits"].get(sid, 0)
        sh     = stats["ship_sh_hits"].get(sid, 0)
        hp_bar = ("&#9608;" * ship.hp) + ("&#9617;" * (max_hp - ship.hp))
        sunk_t = f" SUNK {ts_hhmm(ship.dead_step)}" if ship.hp <= 0 and ship.dead_step else ""
        rows.append((SHIP_NAMES[sid].split("(")[0].strip(),
                     f"{hp_bar} {ship.hp}/{max_hp} HP  boats:{db} shahed:{sh}{sunk_t}"))
    if navy_dead:
        rows.append(("US NAVY CREW",
                     f'<span style="color:#f85149">{navy_dead} personnel KIA</span>'))
    rows += [
        ("—", ""),
        ("References",
         "Dupuy QJM  ·  Lanchester Q={:.1f}  ·  Helmbold random-coverage  ·  Boeing/Raytheon CEP specs".format(LANCHESTER_Q)),
        ("Simulation",        f"{N_STEPS} steps × {STEP_S}s = {N_STEPS*STEP_S//60} min"),
    ]
    return _card(
        f"KHARG ISLAND — F-35 LIGHTNING STRIKE  +  BEACH ASSAULT",
        "#58a6ff", rows)


def _iran_retaliation_desc(marines, irgc, stingers, ospreys, ships,
                            iran_bm, island_shahed, stats,
                            survival_pct, n_irgc_pre, scenario_label="",
                            scenario_desc=None):
    """
    Document description for the F-35 strike + Iranian ballistic missile/drone retaliation.
    Combines pre-strike analysis with the retaliation salvo stats.
    """
    import math as _math

    ISLAND_AREA_M2 = 37_000_000
    weapons = [
        ("GBU-31 JDAM",  16, 2000, 120, 13, "4× F/A-18E/F"),
        ("GBU-32 JDAM",  24, 1000,  90, 10, "12× F-35B stealth"),
        ("GBU-38 JDAM",  48,  500,  40,  9, "12× F-35B beast-mode"),
        ("TLAM Block V",  80,  450,  35, 10, "3× DDG escorts"),
    ]
    total_weapons = sum(w[1] for w in weapons)
    total_A_w     = sum(w[1] * _math.pi * w[3]**2 for w in weapons)
    coverage_pct  = (1.0 - _math.exp(-total_A_w / ISLAND_AREA_M2)) * 100.0

    killed_in_strike = round(n_irgc_pre * (1.0 - survival_pct))
    survived = n_irgc_pre - killed_in_strike

    alive_m  = sum(1 for m in marines  if m.hp > 0)
    alive_i  = sum(1 for s in irgc     if s.hp > 0)
    alive_st = sum(1 for s in stingers if s.hp > 0)
    island_held = alive_i == 0 and alive_st == 0
    sunk_ships  = [SHIP_NAMES[s.agent_id] for s in ships if s.hp <= 0]
    outcome = ("USMC SECURED KHARG ISLAND" if island_held and not sunk_ships
               else "USMC SECURED — SHIPS LOST" if island_held
               else "IRGC REPELLED ASSAULT"     if alive_m == 0
               else "CONTESTED")
    out_color = "#3fb950" if island_held else "#f85149" if alive_m == 0 else "#d29922"

    bm_total   = len(iran_bm)      if iran_bm      else 0
    ish_total  = len(island_shahed) if island_shahed else 0
    bm_int     = stats.get("bm_intercepted",       0)
    bm_hit     = stats.get("bm_hits",              0)
    bm_mkills  = stats.get("bm_marine_kills",      0)
    ish_down   = stats.get("island_sh_shot_down",  0)
    ish_hit    = stats.get("island_sh_hits",        0)
    ish_mkills = stats.get("island_sh_marine_kills",0)
    bm_pct_int = bm_int / bm_total * 100 if bm_total else 0.0
    bm_pct_hit = bm_hit / bm_total * 100 if bm_total else 0.0

    n_ships      = 3
    expected_int = bm_total * (1 - (1 - IRAN_BM_INTERCEPT_PK) ** n_ships)

    nm  = len(marines)
    sk  = len(stats["stinger_kills"])
    slk = len(stats["ship_loss_kills"])
    db_hits = sum(stats['ship_db_hits'].values())
    sh_hits = sum(stats['ship_sh_hits'].values())
    d_kills = sum(stats["drone_kill_count"].values())
    d_fired = sum(stats["drone_ammo_fired"].values())
    navy_dead = stats.get("navy_dead", 0)

    rows = [
        ("SCENARIO",           scenario_label or "F-35 Strike + Iranian Retaliation"),
    ]
    if scenario_desc:
        rows.append(("", f'<span style="color:#8b949e;font-style:italic">{scenario_desc}</span>'))
    rows += [
        ("DATE / TIME",        f"{SIM_DATE}  {SIM_BASE_H:02d}:00Z"),
        ("DURATION",           f"{N_STEPS} steps × {STEP_S}s = {N_STEPS*STEP_S//60} min"),
        ("FINAL OUTCOME",
         f'<span style="color:{out_color};font-weight:bold">{outcome}</span>'),
        ("—", ""),
        ("═══ PHASE 1 — F-35 PRE-STRIKE ═══", ""),
        ("Strike Package",
         f"{total_weapons}× PGM + 8× AGM-88 HARM  (F-35B / F/A-18E / DDG / EA-18G)"),
        ("Island Coverage",
         f'<span style="color:#f85149;font-weight:bold">'
         f'{coverage_pct:.1f}% at 50% P_k  (Helmbold random-coverage)</span>'),
        ("IRGC Killed",
         f'<span style="color:#f85149">{killed_in_strike}/{n_irgc_pre} '
         f'({(1-survival_pct)*100:.0f}%)  —  {survived} survivors</span>'),
        ("Survivability",
         f"{survival_pct*100:.0f}%:  bunkers (2–3%)  ·  GPS jam → INS drift (2–3%)  ·  dispersed (2–3%)"),
        ("—", ""),
        ("═══ PHASE 2 — BEACH ASSAULT ═══", ""),
        ("Insertion",          "LCAC hovercraft + RHIB  (no Osprey MANPADS window)"),
        ("Marines Landed",     f"{nm} fireteams  ({nm*4} men)  —  LZs FALCON/EAGLE/VIPER/COBRA"),
        ("Drone Support",      f"{d_kills} IRGC kills from MQ-9  (fired: {d_fired})"),
        ("—", ""),
        ("═══ PHASE 3 — IRANIAN RETALIATION ═══", ""),
        ("SRBM Mix",
         "Fateh-110 (CEP 10 m, 450 kg warhead)  +  Zelzal-2 (CEP 200 m, 600 kg unguided)"),
        ("Launch Site",
         "IRGC Bandar Abbas complex  (~150 km SE of Kharg,  ~8 min flight)"),
        ("SRBM Salvo",
         f'<span style="color:#f85149;font-weight:bold">{bm_total} missiles at H+{IRAN_BM_SALVO_STEP} min</span>'),
        ("Peak Altitude",      f"{IRAN_BM_PEAK_ALT_M/1000:.0f} km  ({IRAN_BM_PEAK_ALT_M/304.8:.0f},000 ft)"),
        ("SM-3 Expected",      f"{expected_int:.1f}/{bm_total}  ({expected_int/bm_total*100:.1f}%)  "
                                f"Pk={IRAN_BM_INTERCEPT_PK} × {n_ships} ships"),
        ("SM-3 Actual",        f'<span style="color:#3fb950">{bm_int}/{bm_total}  ({bm_pct_int:.1f}%)</span>'),
        ("SRBM Impacts",
         f'<span style="color:#f85149">{bm_hit} hits ({bm_pct_hit:.1f}%)  lethal r={IRAN_BM_LETHAL_M} m</span>'),
        ("SRBM Marine Kills",
         f'<span style="color:#f85149">{bm_mkills} fireteams  ({bm_mkills*4} men)</span>'),
        ("—", ""),
        ("Shahed Island Strike",f"{ish_total} drones at H+{ISLAND_SHAHED_SALVO_STEP} min  (marine LZs)"),
        ("SAM Intercepts",
         f'{ish_down}/{ish_total}  (ESSM Pk={SHIP_SAM_PK}×{EW_SHIP_SAM_PK_MULT:.2f}={SHIP_SAM_PK*EW_SHIP_SAM_PK_MULT:.3f})'),
        ("Shahed Impacts",
         f'{ish_hit} reached island  (lethal r=30 m each)'),
        ("Shahed Marine Kills",
         f'<span style="color:#f85149">{ish_mkills} fireteams  ({ish_mkills*4} men)</span>'),
        ("—", ""),
        ("═══ FINAL SCORECARD ═══", ""),
        ("Marines Alive",
         f'<span style="color:#3fb950">{alive_m}/{nm}</span>  fireteams  ({alive_m*4} men)'),
        ("Marines KIA",
         f'{nm-alive_m} total  '
         f'(stinger:{sk}  ship-loss:{slk}  BM/drone:{bm_mkills+ish_mkills}  '
         f'ground:{nm-alive_m-sk-slk-bm_mkills-ish_mkills})'),
        ("IRGC Remaining",
         f'{alive_i+alive_st} combatants  ({alive_i} squads + {alive_st} Stinger teams)'),
        ("Ship Hits",          f"Drone boats: {db_hits}  ·  Shahed: {sh_hits}"),
        ("Ships Sunk",
         "All intact" if not sunk_ships else
         f'<span style="color:#f85149">SUNK: {", ".join(sunk_ships)}</span>'),
    ]
    for ship in ships:
        sid    = ship.agent_id
        max_hp = SHIP_MAX_HP[sid]
        db     = stats["ship_db_hits"].get(sid, 0)
        sh     = stats["ship_sh_hits"].get(sid, 0)
        hp_bar = ("&#9608;" * ship.hp) + ("&#9617;" * (max_hp - ship.hp))
        sunk_t = f" SUNK {ts_hhmm(ship.dead_step)}" if ship.hp <= 0 and ship.dead_step else ""
        rows.append((SHIP_NAMES[sid].split("(")[0].strip(),
                     f"{hp_bar} {ship.hp}/{max_hp} HP  boats:{db} shahed:{sh}{sunk_t}"))
    if navy_dead:
        rows.append(("Navy Crew KIA",
                     f'<span style="color:#f85149">{navy_dead} personnel KIA</span>'))
    return _card(
        "KHARG ISLAND — F-35 STRIKE  +  BEACH ASSAULT  +  IRANIAN RETALIATION",
        "#f85149", rows)


def _battle_summary_desc(marines, irgc, stingers, ospreys, ships, stats,
                          scenario_label="", scenario_desc=None):
    alive_m      = sum(1 for m in marines  if m.hp > 0)
    alive_i      = sum(1 for s in irgc     if s.hp > 0)
    alive_st     = sum(1 for s in stingers if s.hp > 0)
    sk           = len(stats["stinger_kills"])
    slk          = len(stats["ship_loss_kills"])
    destroyed_ov = sum(1 for ov in ospreys if ov.hp <= 0)
    d_kills      = sum(stats["drone_kill_count"].values())
    d_fired      = sum(stats["drone_ammo_fired"].values())
    d_hit_pct    = f"{100*d_kills//max(d_fired,1)}%" if d_fired else "—"
    total_hits   = sum(stats["ship_db_hits"].values()) + sum(stats["ship_sh_hits"].values())
    sunk_ships   = [SHIP_NAMES[s.agent_id] for s in ships if s.hp <= 0]
    island_held  = alive_i == 0 and alive_st == 0
    outcome = ("USMC SECURED KHARG ISLAND" if island_held and not sunk_ships
               else "USMC SECURED — SHIPS LOST" if island_held
               else "IRGC REPELLED ASSAULT"     if alive_m == 0
               else "CONTESTED")
    out_color   = "#3fb950" if island_held else "#f85149" if alive_m == 0 else "#d29922"
    ground_kia  = len(marines) - alive_m - sk - slk
    navy_dead   = stats.get("navy_dead", 0)
    nm = len(marines); ni = len(irgc); nst = len(stingers)
    db_hits = sum(stats['ship_db_hits'].values())
    sh_hits = sum(stats['ship_sh_hits'].values())
    n_ospreys       = len(ospreys)
    t_sorties_done  = sum(stats["osprey_trips_done"].values())
    t_sorties_plan  = sum(len(v) for v in stats["osprey_trips_map"].values())
    t_men_ashore    = sum(stats["osprey_fteams_del"].values()) * 4
    air_kills_total = sum(stats["stinger_air_kills"].values())
    eff_sam         = SHIP_SAM_PK * EW_SHIP_SAM_PK_MULT
    cancelled       = stats.get("sorties_cancelled", 0)

    rows = [
        ("SCENARIO",         scenario_label or "Kharg Island Assault"),
    ]
    if scenario_desc:
        rows.append(("", f'<span style="color:#8b949e;font-style:italic">{scenario_desc}</span>'))
    rows += [
        ("DATE / TIME",      f"{SIM_DATE}  {SIM_BASE_H:02d}:00Z"),
        ("DURATION",         f"{N_STEPS} steps × {STEP_S}s = {N_STEPS*STEP_S//60} min simulated"),
        ("OUTCOME",
         f'<span style="color:{out_color};font-weight:bold">{outcome}</span>'),
        ("—", ""),
        ("═══ LAND BATTLE ═══", ""),
        ("US Marines",       f"{_pct(alive_m, nm)} fireteams  ({alive_m*4}/{nm*4} men alive)"),
        ("  Effective",      f"{100*alive_m*4//max(nm*4,1)}% combat-effective"),
        ("  Ground KIA",     f"{_pct(ground_kia, nm)}  ({ground_kia*4} men) — IRGC fire"),
        ("  Stinger KIA",    f"{_pct(sk, nm)}  ({sk*4} men) — MANPADS in-flight"),
    ]
    if slk:
        rows.append(("  Ship-loss KIA",
                     f'<span style="color:#f85149">{_pct(slk, nm)}  ({slk*4} men) — ship sunk</span>'))
    rows += [
        ("IRGC",             f"{_pct(alive_i, ni)} defenders alive  ({alive_i*4} men remaining)"),
        ("  Neutralized",    f"{ni-alive_i}/{ni} squads  ({(ni-alive_i)*4} men)"),
        ("  MANPADS Teams",  f"{_pct(nst-alive_st, nst)} Stinger teams destroyed"),
        ("Drone Strikes",    f"{d_kills} IRGC kills  (fired:{d_fired}  hit rate:{d_hit_pct})"),
        ("Combat Model",     f"Lanchester Square  Q={LANCHESTER_Q}  "
                              f"USMC Pk={MARINE_PK}  IRGC Pk={IRGC_PK}  range={ENGAGE_KM} km"),
        ("—", ""),
        ("═══ AVIATION OPS ═══", ""),
        ("MV-22 Ospreys",    f"{_pct(n_ospreys-destroyed_ov, n_ospreys)} operational  "
                              f"({destroyed_ov} shot down by Stingers)"),
        ("  Sorties",        f"{t_sorties_done}/{t_sorties_plan} completed  "
                              f"({100*t_sorties_done//max(t_sorties_plan,1)}%)"),
        ("  Men Ashore",     f"{t_men_ashore} delivered by Osprey"),
    ]
    if cancelled:
        rows.append(("  Cancelled",
                     f'<span style="color:#d29922">{cancelled} sorties aborted (ship sunk)</span>'))
    rows += [
        ("Stinger MANPADS",  f"{air_kills_total} Ospreys down  →  {air_kills_total*MV22_CAPACITY} fireteams at risk  "
                              f"({sk*4} men KIA in-flight)"),
        ("—", ""),
        ("═══ NAVAL SITUATION ═══", ""),
        ("Ships Sunk",       ", ".join(sunk_ships) if sunk_ships else "None"),
        ("Total Hits",       f"{total_hits}  (drone boats:{db_hits}  ·  Shahed:{sh_hits})"),
    ]
    if navy_dead:
        rows.append(("Navy Crew KIA",
                     f'<span style="color:#f85149">{navy_dead} personnel KIA</span>'))
    for ship in ships:
        sid    = ship.agent_id
        max_hp = SHIP_MAX_HP[sid]
        db     = stats["ship_db_hits"].get(sid, 0)
        sh     = stats["ship_sh_hits"].get(sid, 0)
        hp_bar = ("&#9608;" * ship.hp) + ("&#9617;" * (max_hp - ship.hp))
        sunk_t = f'<span style="color:#f85149"> SUNK {ts_hhmm(ship.dead_step)}</span>' \
                 if ship.hp <= 0 and ship.dead_step else ""
        rows.append((SHIP_NAMES[sid].split("(")[0].strip(),
                     f"{hp_bar} {ship.hp}/{max_hp} HP  boats:{db} shahed:{sh}{sunk_t}"))
    rows += [
        ("Drone Boats",      f"{_pct(db_hits, N_DRONE_BOATS)} impacts  "
                              f"({_pct(stats['db_shot_down'], N_DRONE_BOATS)} destroyed)"),
        ("Shahed-136",       f"{_pct(sh_hits, N_SHAHED)} impacts  "
                              f"({_pct(stats['sh_shot_down'], N_SHAHED)} intercepted)"),
        ("SAM Pk",           f"{SHIP_SAM_PK} base  ×EW {EW_SHIP_SAM_PK_MULT:.2f} = {eff_sam:.3f}  "
                              f"(range {SHIP_SAM_RANGE_KM} km)"),
        ("Gun Pk",           f"{SHIP_GUN_PK}  ({int(SHIP_GUN_PK*100)}%)  (range {SHIP_GUN_RANGE_KM} km)"),
        ("—", ""),
        ("═══ EW / IO STATUS ═══", "(JP 3-13 · 3-13.1 · 3-85 · 3-09)"),
    ]
    ew_active = any([
        EW_IRGC_PK_MULT != 1.0, EW_IRGC_DEFENSE_MULT_ADJ != 1.0,
        EW_MANPADS_PK_MULT != 1.0, EW_MILDEC_FRACTION > 0.0,
        EW_SHAHED_ABORT_RATE > 0.0, EW_SHIP_SAM_PK_MULT != 1.0,
    ])
    if ew_active:
        rows.append(("EW Status",
                     '<span style="color:#d29922;font-weight:bold">ACTIVE</span>'))
        if EW_IRGC_PK_MULT != 1.0 or EW_IRGC_DEFENSE_MULT_ADJ != 1.0:
            rows.append(("COMJAM",
                         f"IRGC PK ×{EW_IRGC_PK_MULT:.2f}  Defense ×{EW_IRGC_DEFENSE_MULT_ADJ:.2f}  (JP 3-13.1)"))
        if EW_MANPADS_PK_MULT != 1.0:
            rows.append(("DIRCM/SPJ",
                         f"MANPADS Pk ×{EW_MANPADS_PK_MULT:.2f}  (AN/AAQ-24 — JP 3-85)"))
        if EW_MILDEC_FRACTION > 0.0:
            rows.append(("MILDEC",
                         f"{int(EW_MILDEC_FRACTION*100)}% IRGC misdirected  "
                         f"×{EW_MILDEC_DELAY_STEPS} steps  (JP 3-13)"))
        if EW_SHAHED_ABORT_RATE > 0.0:
            rows.append(("GPS Spoof",
                         f"{int(EW_SHAHED_ABORT_RATE*100)}% Shahed abort rate  (JP 3-85)"))
        if EW_SHIP_SAM_PK_MULT != 1.0:
            rows.append(("Iran ECM",
                         f"Ship SAM Pk ×{EW_SHIP_SAM_PK_MULT:.2f}  (contested EMS — JP 3-85)"))
    else:
        rows.append(("EW Status",
                     '<span style="color:#8b949e">INACTIVE — baseline engagement, no EW modifiers</span>'))
    bm_int   = stats.get("bm_intercepted", 0)
    bm_hit   = stats.get("bm_hits", 0)
    bm_mk    = stats.get("bm_marine_kills", 0)
    bm_fired = bm_int + bm_hit
    ish_down = stats.get("island_sh_shot_down", 0)
    ish_hit  = stats.get("island_sh_hits", 0)
    ish_mk   = stats.get("island_sh_marine_kills", 0)
    ish_total = ish_down + ish_hit
    if bm_fired > 0 or ish_total > 0:
        rows += [
            ("—", ""),
            ("═══ IRANIAN RETALIATION ═══", f"(H+{IRAN_BM_SALVO_STEP} min — 8% reconstituted stockpile)"),
            ("SRBM Salvo",        f"{bm_fired} fired  —  {bm_int} intercepted (SM-3 Pk={IRAN_BM_INTERCEPT_PK})  "
                                   f"—  {bm_hit} impacts  ({N_IRAN_BM}×Fateh-110/Zelzal-2)"),
            ("SRBM Marine KIA",   f'{bm_mk} fireteams  ({bm_mk*4} men)' if bm_mk else "0"),
            ("Island Shahed",     f"{ish_total} launched  —  {ish_down} intercepted  —  {ish_hit} impacts  "
                                   f"({N_ISLAND_SHAHED}×Shahed-136)"),
            ("Shahed Marine KIA", f'{ish_mk} fireteams  ({ish_mk*4} men)' if ish_mk else "0"),
        ]
    return _card(
        f"BATTLE REPORT — {(scenario_label or 'KHARG ISLAND ASSAULT').upper()}",
        "#58a6ff", rows)
