"""
kml/tour.py — KML battle tour generation for the Kharg Island simulation.

Contains: gen_battle_tour.
"""

from persian_gulf_simulation.config import N_STEPS
from persian_gulf_simulation.simulation.spatial import ts, ts_offset


# Exact centroid of Kharg Island bounding polygon (computed from IRGC_POLY_BBOX)
_ISLAND_LON = 50.309318
_ISLAND_LAT = 29.244447

# Island extent: ~4.85 km EW x ~6.47 km NS (NS is the limiting dimension)
# At tilt=0, GE ~60° vFOV: range≈9000 m frames the island with ~20% padding.
# For tilted views the effective footprint shrinks → scale accordingly.
_ISLAND_RANGE_TOP  =  9000   # top-down / near-top-down fill
_ISLAND_RANGE_TILT = 14000   # range for ~55-60° tilt orbit
_ISLAND_RANGE_MID  = 11500   # range for ~45-50° tilt battle phase


def gen_battle_tour(stinger_shots, ships, n_steps,
                    ospreys=None,
                    scenario_label="Kharg Island Assault"):
    """
    Returns gx:Tour XML string.
    Time synchronisation uses gx:TimeStamp / gx:TimeSpan embedded inside
    each LookAt (AbstractView) element — this is the mechanism GE Pro uses
    to drive its timeslider from a tour.
    """
    items = []

    # ── helpers ──────────────────────────────────────────────────────────────
    def look(lon, lat, heading, tilt, range_m, dur, mode="smooth",
             t_when=None, t_begin=None, t_end=None):
        """FlyTo with LookAt.  Embed time in the AbstractView when supplied."""
        if t_when:
            time_xml = (f"\n        <gx:TimeStamp>"
                        f"<when>{t_when}</when></gx:TimeStamp>")
        elif t_begin:
            t_end = t_end or t_begin
            time_xml = (f"\n        <gx:TimeSpan>"
                        f"<begin>{t_begin}</begin>"
                        f"<end>{t_end}</end></gx:TimeSpan>")
        else:
            time_xml = ""
        return (
            f"    <gx:FlyTo>\n"
            f"      <gx:duration>{dur:.1f}</gx:duration>\n"
            f"      <gx:flyToMode>{mode}</gx:flyToMode>\n"
            f"      <LookAt>\n"
            f"        <longitude>{lon:.6f}</longitude>\n"
            f"        <latitude>{lat:.6f}</latitude>\n"
            f"        <altitude>0</altitude>\n"
            f"        <heading>{heading:.1f}</heading>\n"
            f"        <tilt>{tilt:.1f}</tilt>\n"
            f"        <range>{range_m:.0f}</range>\n"
            f"        <altitudeMode>relativeToGround</altitudeMode>"
            f"{time_xml}\n"
            f"      </LookAt>\n"
            f"    </gx:FlyTo>"
        )

    def pause(dur):
        return f"    <gx:Wait><gx:duration>{dur:.1f}</gx:duration></gx:Wait>"

    # ── 1. Open — top-down overview fills screen, timeslider at sim start ──────
    items.append(look(_ISLAND_LON, _ISLAND_LAT, 0, 0, _ISLAND_RANGE_TOP,
                      0.1, "bounce", t_when=ts(0)))
    items.append(pause(1.5))

    # ── 2. 360° orbit — 15 s total (36 steps × ~0.42 s each), time frozen ────
    N_ORBIT = 36
    orbit_step_dur = 15.0 / N_ORBIT          # ≈ 0.42 s per heading step
    for i in range(N_ORBIT + 1):
        heading = (i * 360 / N_ORBIT) % 360
        items.append(look(_ISLAND_LON, _ISLAND_LAT, heading, 58,
                          _ISLAND_RANGE_TILT, orbit_step_dur, "smooth", t_when=ts(0)))

    # ── 3. Battle — three-speed pass: approach / fighting / cleanup ──────────
    items.append(pause(1.0))

    # Derive engagement window from stinger shots; fall back to fractions
    if stinger_shots:
        fight_start = max(0, min(s["step"] for s in stinger_shots) - 3)
        fight_end   = min(n_steps, max(s["step"] for s in stinger_shots) + 5)
    else:
        fight_start = n_steps // 8
        fight_end   = 7 * n_steps // 8

    stride   = max(1, n_steps // 20)  # consistent stride across all phases
    dur_fast = 1.0
    dur_slow = 10.0                   # 10% speed: same stride, 10× real time per frame

    # Build set of steps on which an Osprey was shot down (for tour pauses)
    osprey_kill_steps = set()
    if ospreys:
        for ov in ospreys:
            if ov.dead_step is not None:
                osprey_kill_steps.add(ov.dead_step)

    heading = 340.0

    def _phase(start, end, dur):
        nonlocal heading
        for step in range(start, end, stride):
            heading = (heading + 4) % 360
            items.append(look(_ISLAND_LON, _ISLAND_LAT, heading, 48,
                              _ISLAND_RANGE_MID, dur, "smooth",
                              t_begin=ts(step),
                              t_end=ts(min(step + stride, end - 1))))
            # Pause 3 s whenever an Osprey goes down in this stride window
            if any(step <= k < step + stride for k in osprey_kill_steps):
                items.append(pause(3.0))

    _phase(0,           fight_start, dur_fast)   # approach
    _phase(fight_start, fight_end,   dur_slow)   # fighting (50% speed)
    _phase(fight_end,   n_steps,     dur_fast)   # cleanup
    items.append(pause(1.0))

    # ── 4. Kill events — slow-motion zoom-in ─────────────────────────────────
    hit_shots = [s for s in stinger_shots if s["hit"]]
    for shot in hit_shots:
        kstep = shot["step"]
        klon  = shot["ov_lon"]
        klat  = shot["ov_lat"]

        # Fly to kill zone; show the preceding step
        items.append(look(klon, klat, 30, 65, 5000, 3.0, "smooth",
                          t_when=ts(max(0, kstep - 1))))
        items.append(pause(0.8))

        # Slow-motion replay: 60 sim-seconds → 12 tour-seconds (5× slow-mo)
        # Each sub-frame advances the TimeSpan by 10 sim-seconds
        for sub in range(6):
            t_b = ts_offset(kstep, sub * 10)
            t_e = ts_offset(kstep, sub * 10 + 10)
            items.append(look(klon, klat, 30 + sub * 3, 65, 5000,
                              2.0, "smooth",
                              t_begin=t_b, t_end=t_e))

        # Pull back before next event
        items.append(look(klon, klat, 30, 50, 9000, 1.5, "smooth",
                          t_when=ts(kstep + 1)))
        items.append(pause(0.5))

    # ── 5. Ship sinkings — zoom to each lost ship ─────────────────────────────
    ship_pos = {s.agent_id: (s.track[0][1], s.track[0][2])
                if s.track else (s.lon, s.lat)
                for s in ships}
    for s in sorted(ships, key=lambda x: x.dead_step or 9999):
        if s.dead_step is None:
            continue
        slon, slat = ship_pos[s.agent_id]
        items.append(look(slon, slat, 0, 65, 8000, 3.5, "smooth",
                          t_when=ts(max(0, s.dead_step - 1))))
        items.append(pause(4.0))

    # ── 6. Final state — island fills frame for the reveal ───────────────────
    items.append(look(_ISLAND_LON, _ISLAND_LAT, 10, 35, _ISLAND_RANGE_MID,
                      5.0, "smooth", t_when=ts(n_steps - 1)))
    items.append(pause(3.0))
    for i in range(19):
        heading = (i * 10) % 360
        items.append(look(_ISLAND_LON, _ISLAND_LAT, heading, 45,
                          _ISLAND_RANGE_TILT, 2.0, "smooth",
                          t_when=ts(n_steps - 1)))

    playlist = "\n".join(items)
    return (
        f"  <gx:Tour>\n"
        f"    <name>Battle Tour — {scenario_label}</name>\n"
        f"    <gx:Playlist>\n"
        f"{playlist}\n"
        f"    </gx:Playlist>\n"
        f"  </gx:Tour>"
    )
