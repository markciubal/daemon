#!/usr/bin/env python3
"""
Persian Gulf Wargame KML -- SIMPLIFIED GEOMETRY
================================================
Generates 16 simplified-geometry scenario KML files.

Each trajectory is broken into time-segmented LineString chains so Google Earth
animates smoothly.  Each segment is a 2-point absolute-altitude LineString with:

  TimeSpan begin = when that segment's leading edge arrives
  TimeSpan end   = when the whole trajectory ends (segment stays, building the trail)

Altitude profile for every path follows the parabolic sin(π·t) envelope so the
arcs look right in 3D without using gx:Track.

  Intercepted missile : N segments from launch site → intercept apex
  Interceptor         : M segments from ship pos    → same intercept apex
  Breakthrough missile: N segments from launch site → trajectory apex → target
  US strikes          : M segments from ship pos    → target site

Asset altitude-degradation tracks (50 km start → 0 as hits accumulate) are
generated identically to the full-fidelity version.

Output: scenarios/simplified_<key>.kml  (16 files)
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_wargame_kml as wg   # noqa: E402

# ── Segment counts (higher = smoother animation, larger files) ────────────────
N_MISSILE    = 12   # segments per Iranian missile trajectory
N_INTERCEPTOR = 6   # segments per US interceptor leg
N_STRIKE      = 8   # segments per US TLAM/JASSM strike leg

# ── Asset altitude-degradation (mirrors main script constant) ─────────────────
ALT_MAX_M             = 100_000.0  # 100 km starting altitude
CSG_NEUTRALIZE_HITS   = 10
SITE_NEUTRALIZE_HITS  = wg.SITE_INACTIVATION_THRESHOLD   # 25

# ── Line widths ───────────────────────────────────────────────────────────────
LW_INTERCEPTED  = 2
LW_BREAKTHROUGH = 3
LW_INTERCEPTOR  = 2
LW_STRIKE       = 2


# ─────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ─────────────────────────────────────────────────────────────────────────────
def _lerp(a, b, t):
    return a + (b - a) * t


def _parabolic_alt(peak_m, t_frac):
    """Height of a symmetric parabolic arc at fractional position t_frac ∈ [0,1]."""
    return peak_m * math.sin(math.pi * max(0.0, min(1.0, t_frac)))


def _waypoints_along(src_lon, src_lat, src_alt,
                     tgt_lon, tgt_lat, tgt_alt,
                     peak_m, n, t_start, t_end,
                     f_start=0.0, f_end=1.0):
    """
    Return a list of (t, lon, lat, alt) waypoints for a parabolic arc from
    (src → tgt) sampled at n+1 even steps.

    f_start / f_end let you take a sub-arc (e.g. only the first 70% of the path
    for an intercepted missile that is killed at t_int_frac).

    The parabolic altitude uses the FULL arc's sin envelope so height matches
    what the full trajectory would look like at that fractional position.
    """
    pts = []
    for k in range(n + 1):
        s   = k / n                                # 0 → 1 within this sub-arc
        f   = _lerp(f_start, f_end, s)             # fractional position on full arc
        t   = _lerp(t_start, t_end, s)
        lo  = _lerp(src_lon, tgt_lon, f)
        la  = _lerp(src_lat, tgt_lat, f)
        alt = _parabolic_alt(peak_m, f)
        pts.append((t, lo, la, alt))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
# KML segment emitters
# ─────────────────────────────────────────────────────────────────────────────
def _seg_pm(name, style_id, lo0, la0, a0, lo1, la1, a1, t_begin, t_end):
    """One 2-point absolute-altitude LineString Placemark with TimeSpan."""
    return (
        f'  <Placemark><name>{name}</name>'
        f'<styleUrl>#{style_id}</styleUrl>'
        f'<TimeSpan>'
        f'<begin>{wg.fmt_time(wg.sim_time(t_begin))}</begin>'
        f'<end>{wg.fmt_time(wg.sim_time(t_end))}</end>'
        f'</TimeSpan>'
        f'<LineString><tessellate>0</tessellate>'
        f'<altitudeMode>absolute</altitudeMode>'
        f'<coordinates>{lo0:.5f},{la0:.5f},{a0:.0f} {lo1:.5f},{la1:.5f},{a1:.0f}</coordinates>'
        f'</LineString></Placemark>\n'
    )


def _emit_segments(name, style_id, waypoints, t_trail_end):
    """
    Convert a waypoint list into time-segmented LineString placemarks.
    Each segment begins at its waypoint time and stays visible until t_trail_end
    so the path builds up as a trail during animation.
    """
    out = []
    for k in range(len(waypoints) - 1):
        t0, lo0, la0, a0 = waypoints[k]
        _,  lo1, la1, a1 = waypoints[k + 1]
        out.append(_seg_pm(f"{name}.{k}", style_id,
                            lo0, la0, a0, lo1, la1, a1,
                            t0, t_trail_end))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Asset altitude-degradation track (mirrors _build_damage_track in main)
# ─────────────────────────────────────────────────────────────────────────────
def _damage_track_segs(lon, lat, hit_times, n_hits_max, style_id, label, end_s):
    """
    Return LineString segments descending from ALT_MAX_M to 0 as hits land.
    Each vertical step is a 2-point line (current alt → new alt) at the hit time.
    Horizontal hold segments keep the icon at constant altitude between hits.
    """
    alt_step = ALT_MAX_M / n_hits_max
    current_alt = ALT_MAX_M
    out = []

    prev_t = 0.0
    for hit_t in sorted(hit_times[:n_hits_max]):
        # Horizontal hold: stay at current_alt from prev_t to just before hit
        if hit_t - 1 > prev_t:
            out.append(_seg_pm(f"{label} hold", style_id,
                               lon, lat, current_alt, lon, lat, current_alt,
                               prev_t, end_s))
        # Vertical drop at hit time
        new_alt = max(0.0, current_alt - alt_step)
        out.append(_seg_pm(f"{label} drop", style_id,
                           lon, lat, current_alt, lon, lat, new_alt,
                           hit_t, end_s))
        current_alt = new_alt
        prev_t = hit_t

    # Final hold at whatever altitude remains
    if prev_t < end_s and current_alt >= 0:
        out.append(_seg_pm(f"{label} hold", style_id,
                           lon, lat, current_alt, lon, lat, current_alt,
                           prev_t, end_s))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# KML Styles
# ─────────────────────────────────────────────────────────────────────────────
def simplified_styles():
    parts = []
    for mname, mdef in wg.MUNITIONS.items():
        sid = wg.safe_id(mname)
        parts.append(
            f'  <Style id="s_{sid}">'
            f'<LineStyle><color>{mdef["color"]}</color>'
            f'<width>{LW_INTERCEPTED}</width></LineStyle>'
            f'<PolyStyle><fill>0</fill></PolyStyle></Style>\n'
            f'  <Style id="s_{sid}_bt">'
            f'<LineStyle><color>{mdef["color_bt"]}</color>'
            f'<width>{LW_BREAKTHROUGH}</width></LineStyle>'
            f'<PolyStyle><fill>0</fill></PolyStyle></Style>'
        )
    for sid, color, w in [
        ("si_sm6",       "eeff4400", LW_INTERCEPTOR),
        ("si_ciws",      "bbff9900", LW_INTERCEPTOR),
        ("si_gun",       "bbff9933", LW_INTERCEPTOR),
        ("si_us_strike", "cc00ff66", LW_STRIKE),
    ]:
        parts.append(
            f'  <Style id="{sid}">'
            f'<LineStyle><color>{color}</color><width>{w}</width></LineStyle>'
            f'<PolyStyle><fill>0</fill></PolyStyle></Style>'
        )
    # Asset markers (static icons)
    parts.append(
        '  <Style id="simp_iran_site">'
        '<IconStyle><color>cc0000ff</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.7</scale></LabelStyle></Style>\n'
        '  <Style id="simp_us_csg">'
        '<IconStyle><color>ccff8800</color><scale>0.9</scale>'
        '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/ferry.png</href></Icon>'
        '</IconStyle><LabelStyle><scale>0.7</scale></LabelStyle></Style>\n'
        # Altitude-degradation track style (thin white, so it reads as a height indicator)
        '  <Style id="simp_alt_track">'
        '<LineStyle><color>88ffffff</color><width>1</width></LineStyle>'
        '<PolyStyle><fill>0</fill></PolyStyle></Style>'
    )
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Event simulation (exact RNG mirror of generate_scenario Phases 0-2)
# ─────────────────────────────────────────────────────────────────────────────
def _simulate_events(scenario_key, rng):
    sc         = wg.SCENARIOS[scenario_key]
    n_missiles = sc["n_missiles"]
    cap        = sc["intercept_cap"]
    munitions  = sc["munitions"]
    wave_s     = sc["wave_s"]
    csg_fleet  = sc.get("csg_fleet", wg.US_CSGS)

    DRONE_TYPES  = {"Shahed-136", "IRGCN Sea Drone"}
    phase1_end   = sc.get("phase1_end_s",   wave_s)
    phase2_start = sc.get("phase2_start_s", 0)
    phase2_dur   = sc.get("phase2_dur_s",   wave_s)

    # Phase 0 — consume RNG in same order as main
    strike_events, site_inactive_at, site_hits_tl = wg.compute_us_strikes(scenario_key, rng)
    _iaf = wg.compute_iaf_strikes(scenario_key, rng, site_inactive_at)

    n_intercepted   = min(round(n_missiles * sc["intercept_rate"]), cap)
    intercepted_set = set(rng.sample(range(n_missiles), n_intercepted))

    _focus_name = sc.get("focus_csg")
    _focus_csg  = next((c for c in wg.US_CSGS if c["name"] == _focus_name), None)

    site_pools = {}
    for m in munitions:
        mn      = m["name"]
        mdef    = wg.MUNITIONS[mn]
        allowed = mdef.get("sites")
        pool    = ([s for s in wg.IRAN_SITES if s["name"] in allowed]
                   if allowed else wg.IRAN_SITES)
        site_pools[mn] = pool

    events = []
    for i in range(n_missiles):
        mname     = wg.weighted_choice(munitions, rng)["name"]
        mdef      = wg.MUNITIONS[mname]
        _csg_roll = rng.choice(csg_fleet)
        csg       = _focus_csg if _focus_csg else _csg_roll

        if mname in DRONE_TYPES:
            launch_s = rng.uniform(0, phase1_end)
        else:
            launch_s = rng.uniform(phase2_start, phase2_start + phase2_dur)

        full_pool   = site_pools[mname]
        active_pool = [s for s in full_pool
                       if site_inactive_at.get(s["name"], float("inf")) > launch_s]
        if not active_pool:
            _ = rng.random()
            _ = rng.uniform(-0.25, 0.25)
            _ = rng.uniform(-0.25, 0.25)
            _ = rng.uniform(0.88, 1.12)
            _ = rng.random()
            if i in intercepted_set:
                _ = rng.random()
                _ = rng.uniform(60, 90)
            events.append(None)
            continue

        site     = rng.choice(active_pool)
        _est_d   = wg.haversine_km(site["lon"], site["lat"], csg["lon"], csg["lat"])
        _est_imp = launch_s + _est_d / mdef["speed_km_s"]
        _clon, _clat = wg.csg_pos_at(csg, _est_imp)
        tgt_lon  = _clon + rng.uniform(-0.25, 0.25)
        tgt_lat  = _clat + rng.uniform(-0.25, 0.25)
        dist_km  = wg.haversine_km(site["lon"], site["lat"], tgt_lon, tgt_lat)
        flight_s = dist_km / mdef["speed_km_s"]
        peak     = mdef["peak_alt_m"] * rng.uniform(0.88, 1.12)

        is_ai = (mname == "Shahed-136" and rng.random() < wg.AI_SHAHED_FRACTION)
        if is_ai:
            _ai_imp = launch_s + flight_s
            _alon, _alat = wg.csg_pos_at(csg, _ai_imp)
            _ = _alon + rng.uniform(-0.05, 0.05)
            _ = _alat + rng.uniform(-0.05, 0.05)

        is_int = (i in intercepted_set) and not is_ai
        if "intercept_prob_override" in mdef:
            is_int = rng.random() < mdef["intercept_prob_override"]
        if is_int:
            lo, hi     = mdef.get("t_int_range",
                                  (0.70, 0.92) if mdef["sea_skim"] else (0.55, 0.85))
            t_int_frac = rng.uniform(lo, hi)
            rlo, rhi   = mdef.get("react_range", (60, 90))
            react_s    = rng.uniform(rlo, rhi)
        else:
            t_int_frac = None
            react_s    = None

        events.append({
            "i": i, "mname": mname, "mdef": mdef, "site": site, "csg": csg,
            "tgt_lon": tgt_lon, "tgt_lat": tgt_lat, "dist_km": dist_km,
            "flight_s": flight_s, "launch_s": launch_s, "peak": peak,
            "is_int": is_int, "t_int_frac": t_int_frac, "react_s": react_s,
            "is_ai": is_ai,
        })

    events = [e for e in events if e is not None]

    # Phase 2 — hit timelines
    hits_timeline = {c["name"]: [] for c in csg_fleet}
    for ev in events:
        if not ev["is_int"]:
            hits_timeline[ev["csg"]["name"]].append(ev["launch_s"] + ev["flight_s"])
    for nm in hits_timeline:
        hits_timeline[nm].sort()

    tenth_hit_s = {n: times[9] for n, times in hits_timeline.items() if len(times) >= 10}

    return (events, hits_timeline, tenth_hit_s,
            strike_events, site_inactive_at, site_hits_tl, csg_fleet)


# ─────────────────────────────────────────────────────────────────────────────
# Main KML builder
# ─────────────────────────────────────────────────────────────────────────────
def generate_simplified_scenario(scenario_key, seed=42):
    rng = wg.random.Random(seed)
    sc  = wg.SCENARIOS[scenario_key]

    (events, hits_timeline, tenth_hit_s,
     strike_events, site_inactive_at, site_hits_tl, csg_fleet) = \
        _simulate_events(scenario_key, rng)

    latest_s = 0.0

    missile_intercepted = []
    missile_bt          = []
    interceptor_segs    = []
    strike_segs         = []
    asset_segs          = []

    # ── Iranian missiles ──────────────────────────────────────────────────────
    for ev in events:
        mname    = ev["mname"]
        mdef     = ev["mdef"]
        site     = ev["site"]
        csg      = ev["csg"]
        tgt_lon  = ev["tgt_lon"]
        tgt_lat  = ev["tgt_lat"]
        flight_s = ev["flight_s"]
        launch_s = ev["launch_s"]
        peak     = ev["peak"]
        is_int   = ev["is_int"]
        i        = ev["i"]
        sid      = wg.safe_id(mname)
        src_lon, src_lat = site["lon"], site["lat"]

        if is_int:
            tfrac    = ev["t_int_frac"]
            react_s  = ev["react_s"]
            t_int_s  = launch_s + tfrac * flight_s

            # Missile: launch site → intercept apex (parabolic sub-arc 0 → tfrac)
            wp_m = _waypoints_along(
                src_lon, src_lat, 0,
                tgt_lon, tgt_lat, 0,
                peak, N_MISSILE,
                launch_s, t_int_s,
                f_start=0.0, f_end=tfrac,
            )
            missile_intercepted.extend(
                _emit_segments(f"{mname}.{i}", f"s_{sid}", wp_m, t_int_s))

            # Interceptor: ship → same apex
            csg_neut_s = tenth_hit_s.get(csg["name"])
            if csg_neut_s is None or t_int_s < csg_neut_s:
                t_fire_s         = max(0.0, t_int_s - react_s)
                fire_lon, fire_lat = wg.csg_pos_at(csg, t_fire_s)

                # Intercept apex coordinates from the last missile waypoint
                _, int_lon, int_lat, int_alt = wp_m[-1]

                int_style = mdef.get("interceptor_style", "us_mid")
                int_sid   = ("si_ciws" if int_style == "us_ciws"
                             else "si_gun" if int_style == "us_naval_gun"
                             else "si_sm6")

                # Build straight-line waypoints from ship to apex
                wp_i = []
                for k in range(N_INTERCEPTOR + 1):
                    s  = k / N_INTERCEPTOR
                    t  = _lerp(t_fire_s, t_int_s, s)
                    lo = _lerp(fire_lon, int_lon, s)
                    la = _lerp(fire_lat, int_lat, s)
                    # Interceptor rises on a straight line to the intercept altitude
                    alt = int_alt * s
                    wp_i.append((t, lo, la, alt))

                interceptor_segs.extend(
                    _emit_segments(f"Int.{i}", int_sid, wp_i, t_int_s))

            latest_s = max(latest_s, t_int_s)

        else:
            # Breakthrough: full parabolic arc launch → apex → target
            impact_s = launch_s + flight_s

            wp_b = _waypoints_along(
                src_lon, src_lat, 0,
                tgt_lon, tgt_lat, 0,
                peak, N_MISSILE,
                launch_s, impact_s,
                f_start=0.0, f_end=1.0,
            )
            missile_bt.extend(
                _emit_segments(f"{mname}.{i}.bt", f"s_{sid}_bt", wp_b, impact_s))

            latest_s = max(latest_s, impact_s)

    # ── US TLAM/JASSM strikes ─────────────────────────────────────────────────
    for ev in strike_events:
        csg      = ev["csg"]
        site     = ev["site"]
        l_s      = ev["launch_s"]
        i_s      = ev["impact_s"]
        dist_km  = ev["dist_km"]

        if site_inactive_at.get(site["name"], float("inf")) < i_s:
            continue

        fire_lon, fire_lat = wg.csg_pos_at(csg, l_s)
        s_lon, s_lat       = site["lon"], site["lat"]
        peak_tlam          = min(12_000.0, dist_km * 18.0)

        wp_s = _waypoints_along(
            fire_lon, fire_lat, 0,
            s_lon, s_lat, 0,
            peak_tlam, N_STRIKE,
            l_s, i_s,
        )
        strike_segs.extend(
            _emit_segments("TLAM", "si_us_strike", wp_s, i_s))

        latest_s = max(latest_s, i_s)

    # ── Asset altitude-degradation tracks ─────────────────────────────────────
    # US CSGs
    for csg in csg_fleet:
        csg_hits = hits_timeline.get(csg["name"], [])
        if csg_hits:
            asset_segs.extend(_damage_track_segs(
                csg["lon"], csg["lat"], csg_hits,
                CSG_NEUTRALIZE_HITS, "simp_alt_track", csg["name"], latest_s))

    # Iranian sites
    for s in wg.IRAN_SITES:
        site_hits = site_hits_tl.get(s["name"], [])
        if site_hits:
            asset_segs.extend(_damage_track_segs(
                s["lon"], s["lat"], site_hits,
                SITE_NEUTRALIZE_HITS, "simp_alt_track", s["name"], latest_s))

    # ── Static site / CSG markers ─────────────────────────────────────────────
    site_pms = []
    for s in wg.IRAN_SITES:
        inact   = site_inactive_at.get(s["name"])
        end_tag = f"<end>{wg.fmt_time(wg.sim_time(inact))}</end>" if inact else ""
        span    = f"<TimeSpan>{end_tag}</TimeSpan>" if end_tag else ""
        site_pms.append(
            f'  <Placemark><name>{s["name"]}</name>'
            f'<styleUrl>#simp_iran_site</styleUrl>{span}'
            f'<Point><altitudeMode>clampToGround</altitudeMode>'
            f'<coordinates>{s["lon"]:.4f},{s["lat"]:.4f},0</coordinates>'
            f'</Point></Placemark>\n'
        )

    csg_pms = []
    for csg in csg_fleet:
        lon, lat = csg["lon"], csg["lat"]
        csg_pms.append(
            f'  <Placemark><name>{csg["name"]}</name>'
            f'<styleUrl>#simp_us_csg</styleUrl>'
            f'<Point><altitudeMode>clampToGround</altitudeMode>'
            f'<coordinates>{lon:.4f},{lat:.4f},0</coordinates>'
            f'</Point></Placemark>\n'
        )

    # ── Assemble KML ──────────────────────────────────────────────────────────
    n_bt  = sum(1 for e in events if not e["is_int"])
    n_int = sum(1 for e in events if e["is_int"])

    kml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2" '
        'xmlns:gx="http://www.google.com/kml/ext/2.2">\n'
        '<Document>\n'
        f'  <name>Simplified: {sc["label"]}</name>\n'
        f'  <description>{len(events)} missiles | {n_int} intercepted | '
        f'{n_bt} breakthrough</description>\n'
        + simplified_styles() + '\n'
        + '  <Folder><name>Iranian Launch Sites</name>\n'
        + ''.join(site_pms)
        + '  </Folder>\n'
        + '  <Folder><name>US Carrier Strike Groups</name>\n'
        + ''.join(csg_pms)
        + '  </Folder>\n'
        + '  <Folder><name>Asset Altitude Degradation</name>\n'
        + ''.join(asset_segs)
        + '  </Folder>\n'
        + '  <Folder><name>Intercepted Missiles</name>\n'
        + ''.join(missile_intercepted)
        + '  </Folder>\n'
        + '  <Folder><name>Breakthrough Missiles</name>\n'
        + ''.join(missile_bt)
        + '  </Folder>\n'
        + '  <Folder><name>US Interceptors</name>\n'
        + ''.join(interceptor_segs)
        + '  </Folder>\n'
        + '  <Folder><name>US Strikes</name>\n'
        + ''.join(strike_segs)
        + '  </Folder>\n'
        + '</Document></kml>\n'
    )
    return kml, len(events), n_int, n_bt


# ─────────────────────────────────────────────────────────────────────────────
def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out  = os.path.join(base, "scenarios")
    os.makedirs(out, exist_ok=True)

    seeds = {
        "low": 42, "medium": 7, "high": 13, "realistic": 99,
        "iran_best": 77, "usa_best": 11,
        "drone_first_low": 55, "drone_first_medium": 66, "drone_first_high": 88,
        "coordinated_strike": 99, "focused_salvo": 99, "hypersonic_threat": 99,
        "ballistic_barrage": 33, "ascm_swarm": 44, "shore_based_defense": 99,
        "strait_transit": 99,
    }

    for key, seed in seeds.items():
        print(f"  Generating simplified_{key} ...")
        kml, n, ki, kb = generate_simplified_scenario(key, seed=seed)
        path = os.path.join(out, f"simplified_{key}.kml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(kml)
        size_mb = os.path.getsize(path) / 1_048_576
        pct = f"{100*ki/n:.1f}%" if n else "0%"
        print(f"    {key}: {n} missiles | {ki} intercepted ({pct}) | "
              f"{kb} breakthrough | {size_mb:.1f} MB")

    print("Done.")


if __name__ == "__main__":
    main()
