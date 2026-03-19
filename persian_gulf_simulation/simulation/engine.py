"""
simulation/engine.py — run_simulation() for the Kharg Island simulation.

CRITICAL: imports config as a module (not 'from config import X') so that
_patch_scenario()'s setattr(cfg, name, val) calls are seen at call time.
"""

import math

import persian_gulf_simulation.config as cfg
from persian_gulf_simulation.simulation.spatial import (
    dist_km, step_toward, build_grid, neighbors_in_range,
)


def run_simulation(marines, flights, flight_lz_center,
                   irgc, irgc_homes,
                   stingers,
                   ospreys, osprey_trips,
                   drones,
                   ships, drone_boats, shahed,
                   rng,
                   pre_strike_survival_pct=None,
                   iran_bm=None, island_shahed=None,
                   sailors=None):
    ACTIVATE_RANGE_KM = 0.8
    LANDED_THRESH_KM  = 0.05
    DRONE_ON_STA_KM   = 0.5
    OSPREY_AT_LZ_KM   = 0.3

    # ── EW/IO effective values (JP 3-13, JP 3-13.1, JP 3-85) ─────────────────
    eff_irgc_pk          = cfg.IRGC_PK          * cfg.EW_IRGC_PK_MULT
    eff_irgc_def_mult    = cfg.IRGC_DEFENSE_MULT * cfg.EW_IRGC_DEFENSE_MULT_ADJ
    eff_stinger_pk       = cfg.STINGER_PK        * cfg.EW_MANPADS_PK_MULT
    eff_stinger_hover_pk = cfg.STINGER_HOVER_PK  * cfg.EW_MANPADS_PK_MULT
    eff_ship_sam_pk      = cfg.SHIP_SAM_PK       * cfg.EW_SHIP_SAM_PK_MULT

    # MILDEC — randomly select fraction of IRGC that are misdirected initially
    mildec_irgc = set()
    if cfg.EW_MILDEC_FRACTION > 0.0 and irgc:
        n_mildec = int(len(irgc) * cfg.EW_MILDEC_FRACTION)
        mildec_ids = rng.sample([s.agent_id for s in irgc], min(n_mildec, len(irgc)))
        mildec_irgc = set(mildec_ids)

    # Shahed GPS abort — kill fraction at step 1 (crash on launch / GPS-spoofed loss)
    shahed_abort_done   = False
    island_sh_abort_done = False

    # --- Kill / stats tracking ---
    stinger_kills     = set()
    stinger_air_kills = {}
    stinger_reload    = {}       # st_id → earliest step the team can fire again
    stinger_shots     = []       # each firing event: {step,hit,pk,st_id,ov_id,positions}
    drone_kill_count  = {}
    drone_ammo_fired  = {}
    osprey_trips_done = {}
    osprey_fteams_del = {}
    ship_db_hits      = {s.agent_id: 0 for s in ships}
    ship_sh_hits      = {s.agent_id: 0 for s in ships}
    ship_hit_log      = []   # (step, ship_id, source_label, hp_after)
    db_shot_down      = 0
    sh_shot_down      = 0
    sorties_cancelled = 0        # sorties aborted because a ship was sunk
    ship_loss_kills   = set()    # marine agent_ids killed by ship loss
    navy_dead         = 0        # ship crew KIA (2500 per ship lost)

    # Sailor fallback tracking — sailors sent ashore when Marine pool is exhausted
    sailor_pool       = list(sailors) if sailors else []   # undeployed sailor groups
    sailors_deployed  = 0   # how many sailor groups were inserted as cargo
    sailors_on_island = []  # sailor agents that have landed and are fighting
    sailor_dead       = 0   # sailor groups KIA on island

    # Iranian retaliation tracking
    bm_intercepted        = 0
    bm_hits               = 0
    bm_marine_kills       = 0
    island_sh_shot_down   = 0
    island_sh_hits        = 0
    island_sh_marine_kills = 0
    bm_outcome            = {}   # agent_id → "intercepted" | "hit"

    # Cache BM launch positions before simulation starts
    bm_launch_pos = {}
    if iran_bm:
        for bm in iran_bm:
            bm_launch_pos[bm.agent_id] = (bm.lon, bm.lat)

    tripoli_agent   = next((s for s in ships if s.agent_id == "SHIP_TRIPOLI"), None)
    ships_were_alive = {s.agent_id: True for s in ships}  # track which were alive

    for ov in ospreys:
        osprey_trips_done[ov.agent_id] = 0
        osprey_fteams_del[ov.agent_id] = 0
    for d in drones:
        drone_kill_count[d.agent_id] = 0
        drone_ammo_fired[d.agent_id] = 0

    marine_to_flight = {}
    for fid, members in flights.items():
        for m in members:
            marine_to_flight[m.agent_id] = fid

    ov_state    = {ov.agent_id: "outbound"  for ov in ospreys}
    ov_trip_idx = {ov.agent_id: 0           for ov in ospreys}
    ov_hold     = {ov.agent_id: 0           for ov in ospreys}
    ov_cargo    = {ov.agent_id: osprey_trips[ov.agent_id][0]
                   if osprey_trips[ov.agent_id] else None
                   for ov in ospreys}

    for step in range(cfg.N_STEPS + 1):

        for a in marines:     a.record(step)
        for a in irgc:        a.record(step)
        for a in stingers:    a.record(step)
        for a in ospreys:     a.record(step)
        for a in drones:      a.record(step)
        for a in ships:       a.record(step)
        for a in drone_boats: a.record(step)
        if iran_bm:
            for a in iran_bm:        a.record(step)
        if island_shahed:
            for a in island_shahed:  a.record(step)

        # Pre-strike: simultaneous destruction of IRGC/Stinger positions at H-Hour (step 0).
        # Agents record their alive position first (above), then are killed so the death
        # animation begins immediately. Survivors (pre_strike_survival_pct) fight normally.
        if step == 0 and pre_strike_survival_pct is not None:
            for agent in irgc + stingers:
                if agent.hp > 0 and rng.random() > pre_strike_survival_pct:
                    agent.damage(agent.hp, step)
        for a in shahed:      a.record(step)

        # EW: GPS-spoofed Shahed abort — kill fraction at step 1 (after first record)
        if step == 1 and cfg.EW_SHAHED_ABORT_RATE > 0.0:
            if not shahed_abort_done:
                alive_sh = [s for s in shahed if s.hp > 0]
                n_abort = int(len(alive_sh) * cfg.EW_SHAHED_ABORT_RATE)
                for s in rng.sample(alive_sh, min(n_abort, len(alive_sh))):
                    s.damage(s.hp, step)
                shahed_abort_done = True
            if island_shahed and not island_sh_abort_done:
                alive_ish = [s for s in island_shahed if s.hp > 0]
                n_abort = int(len(alive_ish) * cfg.EW_SHAHED_ABORT_RATE)
                for s in rng.sample(alive_ish, min(n_abort, len(alive_ish))):
                    s.damage(s.hp, step)
                island_sh_abort_done = True

        if step == cfg.N_STEPS:
            break

        marine_grid = build_grid(marines)
        irgc_grid   = build_grid(irgc + stingers)

        alive_marines   = [m for m in marines    if m.hp > 0]
        alive_irgc      = [s for s in irgc       if s.hp > 0]
        alive_stingers  = [s for s in stingers   if s.hp > 0]
        alive_drones    = [d for d in drones     if d.hp > 0]
        alive_ospreys   = [ov for ov in ospreys  if ov.hp > 0]
        alive_ships     = [s for s in ships      if s.hp > 0]
        alive_dboats    = [d for d in drone_boats if d.hp > 0]
        alive_shahed    = [s for s in shahed     if s.hp > 0]

        pre_move_airborne = {
            m.agent_id: (m.lon, m.lat)
            for m in alive_marines
            if not m.landed and m.launch_step <= step
        }

        # -- Marine movement --
        for m in alive_marines:
            if step < m.launch_step:
                m.lon += rng.uniform(-0.0002, 0.0002)
                m.lat += rng.uniform(-0.0002, 0.0002)
            elif not m.landed:
                m.lon, m.lat = step_toward(m.lon, m.lat, m.lz[0], m.lz[1], cfg.OSPREY_KPS)
                if dist_km(m.lon, m.lat, m.lz[0], m.lz[1]) <= LANDED_THRESH_KM:
                    m.landed = True
            else:
                all_def = alive_irgc + alive_stingers
                if all_def:
                    nearest = min(all_def, key=lambda s: dist_km(m.lon, m.lat, s.lon, s.lat))
                    m.lon, m.lat = step_toward(m.lon, m.lat, nearest.lon, nearest.lat, cfg.MARCH_KPS)

        # -- Sailor movement (mirrors marine logic; sailors use MARCH_KPS in transit/on-island) --
        for sal in [s for s in sailors_on_island if s.hp > 0]:
            if sal.lz is None:
                continue
            if not sal.landed:
                sal.lon, sal.lat = step_toward(sal.lon, sal.lat, sal.lz[0], sal.lz[1], cfg.OSPREY_KPS)
                if dist_km(sal.lon, sal.lat, sal.lz[0], sal.lz[1]) <= LANDED_THRESH_KM:
                    sal.landed = True
            else:
                all_def = alive_irgc + alive_stingers
                if all_def:
                    nearest = min(all_def, key=lambda s: dist_km(sal.lon, sal.lat, s.lon, s.lat))
                    sal.lon, sal.lat = step_toward(sal.lon, sal.lat, nearest.lon, nearest.lat, cfg.MARCH_KPS)

        # -- IRGC movement (MILDEC: misdirected squads skip activation until delay expires) --
        for s in alive_irgc:
            if s.agent_id in mildec_irgc and step < cfg.EW_MILDEC_DELAY_STEPS:
                continue  # MILDEC: this squad is responding to a decoy site
            nearby = neighbors_in_range(s.lon, s.lat, marine_grid, ACTIVATE_RANGE_KM)
            if nearby:
                nearest_m = min(nearby, key=lambda m: dist_km(s.lon, s.lat, m.lon, m.lat))
                s.lon, s.lat = step_toward(s.lon, s.lat, nearest_m.lon, nearest_m.lat, cfg.IRGC_KPS)

        # -- Osprey round-trip state machine --
        for ov in alive_ospreys:
            oid   = ov.agent_id
            state = ov_state[oid]
            if state == "outbound":
                lz_target = flight_lz_center[ov_cargo[oid]]
                ov.lon, ov.lat = step_toward(ov.lon, ov.lat, lz_target[0], lz_target[1], cfg.OSPREY_KPS)
                if dist_km(ov.lon, ov.lat, lz_target[0], lz_target[1]) <= OSPREY_AT_LZ_KM:
                    ov_state[oid] = "dropping"
                    ov_hold[oid]  = cfg.OSPREY_DROP_STEPS
            elif state == "dropping":
                ov_hold[oid] -= 1
                if ov_hold[oid] <= 0:
                    cargo_fid = ov_cargo[oid]
                    if cargo_fid is not None:
                        delivered = sum(1 for m in flights.get(cargo_fid, []) if m.hp > 0)
                        osprey_fteams_del[oid] = osprey_fteams_del.get(oid, 0) + delivered
                        osprey_trips_done[oid] = osprey_trips_done.get(oid, 0) + 1
                    ov_cargo[oid] = None
                    ov_state[oid] = "inbound"
            elif state == "inbound":
                ov.lon, ov.lat = step_toward(ov.lon, ov.lat, cfg.TRIPOLI_LON, cfg.TRIPOLI_LAT, cfg.OSPREY_KPS)
                if dist_km(ov.lon, ov.lat, cfg.TRIPOLI_LON, cfg.TRIPOLI_LAT) <= OSPREY_AT_LZ_KM:
                    ov_state[oid] = "loading"
                    ov_hold[oid]  = cfg.OSPREY_LOAD_STEPS
            elif state == "loading":
                ov_hold[oid] -= 1
                if ov_hold[oid] <= 0:
                    next_idx  = ov_trip_idx[oid] + 1
                    trip_list = osprey_trips[oid]
                    tripoli_up = (tripoli_agent is None or tripoli_agent.hp > 0)
                    if next_idx < len(trip_list) and tripoli_up:
                        ov_trip_idx[oid] = next_idx
                        ov_cargo[oid]    = trip_list[next_idx]
                        ov.lz            = flight_lz_center[ov_cargo[oid]]
                        ov_state[oid]    = "outbound"
                    elif next_idx < len(trip_list) and not tripoli_up:
                        # Ship sunk — cancel remaining sorties; kill marines still aboard
                        for cancelled_fid in trip_list[next_idx:]:
                            sorties_cancelled += 1
                            for m in flights.get(cancelled_fid, []):
                                if m.hp > 0 and not m.landed:
                                    m.damage(m.hp, step + 1)
                                    ship_loss_kills.add(m.agent_id)
                        ov_state[oid] = "done"
                    elif sailor_pool and tripoli_up:
                        # Marines exhausted — load sailors as a last-resort wave.
                        # Take up to MV22_CAPACITY sailor groups from the pool.
                        batch = sailor_pool[:cfg.MV22_CAPACITY]
                        del sailor_pool[:cfg.MV22_CAPACITY]
                        sailors_deployed += len(batch)
                        # Assign LZ: cycle through LZS by trip count
                        lz_idx = (next_idx) % len(cfg.LZS)
                        lz_target = cfg.LZS[lz_idx]
                        for sal in batch:
                            sal.lz = lz_target
                            sal.lon = cfg.TRIPOLI_LON + rng.uniform(-0.005, 0.005)
                            sal.lat = cfg.TRIPOLI_LAT + rng.uniform(-0.005, 0.005)
                        # Store as a pseudo-flight in a new flight_id so cargo tracking works
                        pseudo_fid = f"SAL_{oid}_{next_idx}"
                        flights[pseudo_fid]          = batch
                        flight_lz_center[pseudo_fid] = lz_target
                        trip_list.append(pseudo_fid)
                        ov_trip_idx[oid] = next_idx
                        ov_cargo[oid]    = pseudo_fid
                        ov.lz            = lz_target
                        ov_state[oid]    = "outbound"
                        sailors_on_island.extend(batch)
                    else:
                        ov_state[oid] = "done"

        # -- Drone transit --
        for d in alive_drones:
            if not d.landed:
                d.lon, d.lat = step_toward(d.lon, d.lat, d.lz[0], d.lz[1], cfg.DRONE_SPEED_KPS)
                if dist_km(d.lon, d.lat, d.lz[0], d.lz[1]) <= DRONE_ON_STA_KM:
                    d.landed = True

        # -- IRGCN drone boats move toward target ships --
        for db in alive_dboats:
            db.lon, db.lat = step_toward(db.lon, db.lat, db.lz[0], db.lz[1], cfg.DBOAT_SPEED_KPS)

        # -- Shahed move toward target ships --
        for sh in alive_shahed:
            sh.lon, sh.lat = step_toward(sh.lon, sh.lat, sh.lz[0], sh.lz[1], cfg.SHAHED_SPEED_KPS)

        # -- Ship defence: SAMs vs Shahed, guns vs drone boats --
        for ship in alive_ships:
            for sh in list(alive_shahed):
                if sh.hp > 0 and dist_km(ship.lon, ship.lat, sh.lon, sh.lat) <= cfg.SHIP_SAM_RANGE_KM:
                    pk = eff_ship_sam_pk * (cfg.AI_DRONE_SAM_PK_MULT if sh.is_ai else 1.0)
                    if rng.random() < pk:
                        sh.damage(sh.hp, step + 1)
                        sh_shot_down += 1
            for db in list(alive_dboats):
                if db.hp > 0 and dist_km(ship.lon, ship.lat, db.lon, db.lat) <= cfg.SHIP_GUN_RANGE_KM:
                    if rng.random() < cfg.SHIP_GUN_PK:
                        db.damage(1, step + 1)
                        if db.hp <= 0:
                            db_shot_down += 1

        # -- Impact check: threats that reach a ship --
        for db in alive_dboats:
            if db.hp <= 0:
                continue
            for ship in alive_ships:
                if dist_km(db.lon, db.lat, ship.lon, ship.lat) <= cfg.SHIP_IMPACT_KM:
                    ship.damage(1, step + 1)
                    db.damage(db.hp, step + 1)
                    ship_db_hits[ship.agent_id] += 1
                    ship_hit_log.append((step + 1, ship.agent_id, "IRGCN Drone Boat", ship.hp))
                    break

        for sh in alive_shahed:
            if sh.hp <= 0:
                continue
            for ship in alive_ships:
                if dist_km(sh.lon, sh.lat, ship.lon, ship.lat) <= cfg.SHIP_IMPACT_KM:
                    ship.damage(1, step + 1)
                    sh.damage(sh.hp, step + 1)
                    ship_sh_hits[ship.agent_id] += 1
                    ship_hit_log.append((step + 1, ship.agent_id, "Shahed-136", ship.hp))
                    break

        # Refresh alive lists after maritime combat
        alive_shahed = [s for s in shahed      if s.hp > 0]
        alive_dboats = [d for d in drone_boats if d.hp > 0]

        # ---- Ship-loss cascade: kill undeployed marines; landed marines fight on ---
        newly_sunk = [s for s in ships if s.hp <= 0 and ships_were_alive[s.agent_id]]
        if newly_sunk:
            for sunk_ship in newly_sunk:
                ships_were_alive[sunk_ship.agent_id] = False
                navy_dead += 2500            # ship crew
            # Kill only marines not yet ashore (still aboard ship or airborne)
            for m in marines:
                if m.hp > 0 and not m.landed:
                    m.damage(m.hp, step + 1)
                    ship_loss_kills.add(m.agent_id)
            # Cancel all remaining osprey sorties — no ship to sortie from
            for ov in ospreys:
                state = ov_state.get(ov.agent_id)
                if state in ("done",):
                    continue
                trip_list = osprey_trips.get(ov.agent_id, [])
                curr_idx  = ov_trip_idx.get(ov.agent_id, 0)
                if state in ("outbound", "dropping"):
                    # Current trip is mid-flight and aborted — count it and all future
                    for _ in trip_list[curr_idx:]:
                        sorties_cancelled += 1
                else:
                    # "inbound" or "loading": current trip already delivered — only future
                    for _ in trip_list[curr_idx + 1:]:
                        sorties_cancelled += 1
                ov_state[ov.agent_id] = "done"
            # Simulation continues — landed marines keep fighting

        # -- Rebuild grids after movement --
        marine_grid = build_grid(marines)
        irgc_grid   = build_grid(irgc + stingers)

        # -- Iranian SRBM barrage (staggered: each BM has its own launch_step) --
        if iran_bm and step >= cfg.IRAN_BM_SALVO_STEP:
            cur_alive_ships = [s for s in ships if s.hp > 0]
            cur_alive_mar   = [m for m in marines if m.hp > 0]
            # Only BMs whose individual launch_step has been reached and are still alive
            alive_bm = [b for b in iran_bm
                        if b.hp > 0 and step >= (b.launch_step or cfg.IRAN_BM_SALVO_STEP)]
            # Move each BM toward its target at constant angular speed
            for bm in alive_bm:
                llon, llat = bm_launch_pos[bm.agent_id]
                total_d    = dist_km(llon, llat, bm.lz[0], bm.lz[1])
                bm_spd     = total_d / (cfg.IRAN_BM_FLIGHT_STEPS * cfg.STEP_S)
                bm.lon, bm.lat = step_toward(bm.lon, bm.lat,
                                             bm.lz[0], bm.lz[1], bm_spd)
            # Ship SM-3/SM-6 intercept: each ship fires one shot per in-range BM
            for bm in alive_bm:
                if bm.hp <= 0:
                    continue
                for ship in cur_alive_ships:
                    if dist_km(ship.lon, ship.lat, bm.lon, bm.lat) <= 200.0:
                        if rng.random() < cfg.IRAN_BM_INTERCEPT_PK:
                            bm.damage(bm.hp, step + 1)
                            bm_intercepted += 1
                            bm_outcome[bm.agent_id] = "intercepted"
                            break
            # Impact: BMs that reached target strike marine positions
            lethal_bm_km = cfg.IRAN_BM_LETHAL_M / 1000.0
            for bm in alive_bm:
                if bm.hp <= 0:
                    continue
                if dist_km(bm.lon, bm.lat, bm.lz[0], bm.lz[1]) < 0.05:
                    for m in cur_alive_mar:
                        if m.hp > 0 and m.landed and \
                                dist_km(bm.lon, bm.lat, m.lon, m.lat) <= lethal_bm_km:
                            m.damage(m.hp, step + 1)
                            bm_marine_kills += 1
                    bm.damage(bm.hp, step + 1)
                    bm_hits += 1
                    bm_outcome[bm.agent_id] = "hit"

        # -- Island-targeting Shahed (fires from step ISLAND_SHAHED_SALVO_STEP) --
        if island_shahed and step >= cfg.ISLAND_SHAHED_SALVO_STEP:
            cur_alive_ships = [s for s in ships if s.hp > 0]
            cur_alive_mar   = [m for m in marines if m.hp > 0]
            alive_ish       = [s for s in island_shahed if s.hp > 0]
            # Ship SAM defense vs island Shahed
            for ship in cur_alive_ships:
                for sh in alive_ish:
                    if sh.hp > 0 and \
                            dist_km(ship.lon, ship.lat, sh.lon, sh.lat) <= cfg.SHIP_SAM_RANGE_KM:
                        pk = eff_ship_sam_pk * (cfg.AI_DRONE_SAM_PK_MULT if sh.is_ai else 1.0)
                        if rng.random() < pk:
                            sh.damage(sh.hp, step + 1)
                            island_sh_shot_down += 1
            # Move and impact
            lethal_ish_km = 30.0 / 1000.0   # 30 m lethal radius (small warhead vs infantry)
            for sh in alive_ish:
                if sh.hp <= 0:
                    continue
                sh.lon, sh.lat = step_toward(sh.lon, sh.lat,
                                             sh.lz[0], sh.lz[1], cfg.SHAHED_SPEED_KPS)
                if dist_km(sh.lon, sh.lat, sh.lz[0], sh.lz[1]) < 0.05:
                    for m in cur_alive_mar:
                        if m.hp > 0 and m.landed and \
                                dist_km(sh.lon, sh.lat, m.lon, m.lat) <= lethal_ish_km:
                            m.damage(m.hp, step + 1)
                            island_sh_marine_kills += 1
                    sh.damage(sh.hp, step + 1)
                    island_sh_hits += 1

        # -- Ground combat (Lanchester) --
        # Combatants = landed Marines + landed Sailors (sailors use SAILOR_PK)
        alive_sailors_on_island = [sal for sal in sailors_on_island if sal.hp > 0 and sal.landed]
        marine_dmg = {}
        irgc_dmg   = {}
        for m in alive_marines + alive_sailors_on_island:
            if m.hp <= 0:
                continue
            enemies = neighbors_in_range(m.lon, m.lat, irgc_grid, cfg.ENGAGE_KM)
            for s in enemies:
                if s.hp <= 0:
                    continue
                # MILDEC: misdirected squads don't fight until delay expires
                if s.agent_id in mildec_irgc and step < cfg.EW_MILDEC_DELAY_STEPS:
                    continue
                unit_pk = cfg.SAILOR_PK if getattr(m, "is_sailor", False) else cfg.MARINE_PK
                if rng.random() < unit_pk:
                    irgc_dmg[s.agent_id] = irgc_dmg.get(s.agent_id, 0) + 1
                home = irgc_homes.get(s.agent_id)
                in_defense = (home is not None
                    and dist_km(s.lon, s.lat, home[0], home[1]) <= cfg.IRGC_HOME_RADIUS_KM)
                eff_pk = eff_irgc_pk * (eff_irgc_def_mult if in_defense else 1.0)
                if rng.random() < eff_pk:
                    marine_dmg[m.agent_id] = marine_dmg.get(m.agent_id, 0) + 1

        for m in alive_marines + alive_sailors_on_island:
            dmg = marine_dmg.get(m.agent_id, 0)
            if dmg:
                m.damage(dmg, step + 1)
        for s in alive_irgc + alive_stingers:
            dmg = irgc_dmg.get(s.agent_id, 0)
            if dmg:
                s.damage(dmg, step + 1)

        # -- Stinger MANPADS vs Ospreys --
        # Outbound (transit) Pk=0.25; Hovering at LZ (dropping) Pk=0.75
        outbound_ospreys = {
            ov.agent_id: ov for ov in alive_ospreys
            if ov_state.get(ov.agent_id) == "outbound" and ov_cargo.get(ov.agent_id) is not None
        }
        dropping_ospreys = {
            ov.agent_id: ov for ov in alive_ospreys
            if ov_state.get(ov.agent_id) == "dropping" and ov_cargo.get(ov.agent_id) is not None
        }
        for st in alive_stingers:
            if st.hp <= 0:
                continue
            if step < stinger_reload.get(st.agent_id, 0):   # still reloading
                continue
            # Build candidate list: (osprey, pk) — dropping targets are priority/higher Pk
            candidates = []
            for ov in dropping_ospreys.values():
                if dist_km(st.lon, st.lat, ov.lon, ov.lat) <= cfg.STINGER_WEZ_KM:
                    candidates.append((ov, eff_stinger_hover_pk))
            for ov in outbound_ospreys.values():
                if dist_km(st.lon, st.lat, ov.lon, ov.lat) <= cfg.STINGER_WEZ_KM:
                    candidates.append((ov, eff_stinger_pk))
            if not candidates:
                continue
            target_ov, pk = rng.choice(candidates)
            roll = rng.random()
            hit  = roll < pk
            # Record this firing event for KML trajectory rendering
            stinger_reload[st.agent_id] = step + cfg.STINGER_RELOAD_STEPS + 1
            stinger_shots.append({
                "step":   step,
                "hit":    hit,
                "pk":     pk,
                "st_id":  st.agent_id,
                "ov_id":  target_ov.agent_id,
                "st_lon": st.lon,   "st_lat": st.lat,
                "ov_lon": target_ov.lon, "ov_lat": target_ov.lat,
            })
            if hit:
                target_ov.damage(1, step + 1)
                stinger_air_kills[st.agent_id] = stinger_air_kills.get(st.agent_id, 0) + 1
                cargo_fid = ov_cargo.get(target_ov.agent_id)
                if cargo_fid is not None:
                    for m in flights.get(cargo_fid, []):
                        if m.hp > 0 and m.agent_id in pre_move_airborne:
                            m.damage(m.hp, step + 1)
                            stinger_kills.add(m.agent_id)
                outbound_ospreys.pop(target_ov.agent_id, None)
                dropping_ospreys.pop(target_ov.agent_id, None)

        # -- MQ-9 Hellfire strikes --
        irgc_drone_dmg    = {}
        drone_kill_credit = {}
        if step >= cfg.DRONE_ARRIVE_STEP:
            for d in alive_drones:
                if not d.landed or d.drone_ammo is None or d.drone_ammo <= 0:
                    continue
                targets = [t for t in neighbors_in_range(d.lon, d.lat, irgc_grid, 99.0) if t.hp > 0]
                if not targets:
                    continue
                target = rng.choice(targets)
                drone_ammo_fired[d.agent_id] = drone_ammo_fired.get(d.agent_id, 0) + 1
                if rng.random() < cfg.DRONE_PK:
                    irgc_drone_dmg[target.agent_id] = (
                        irgc_drone_dmg.get(target.agent_id, 0) + target.hp
                    )
                    drone_kill_credit[target.agent_id] = d.agent_id
                d.drone_ammo -= 1

        for s in alive_irgc + alive_stingers:
            dmg = irgc_drone_dmg.get(s.agent_id, 0)
            if dmg:
                was_alive = s.hp > 0
                s.damage(dmg, step + 1)
                if was_alive and s.hp <= 0:
                    killer_drone = drone_kill_credit.get(s.agent_id)
                    if killer_drone:
                        drone_kill_count[killer_drone] = drone_kill_count.get(killer_drone, 0) + 1

    sailor_dead = sum(1 for s in sailors_on_island if s.hp <= 0)

    return {
        "stinger_kills":          stinger_kills,
        "stinger_air_kills":      stinger_air_kills,
        "stinger_shots":          stinger_shots,
        "drone_kill_count":       drone_kill_count,
        "drone_ammo_fired":       drone_ammo_fired,
        "osprey_trips_done":      osprey_trips_done,
        "osprey_fteams_del":      osprey_fteams_del,
        "osprey_trips_map":       osprey_trips,
        "ship_db_hits":           ship_db_hits,
        "ship_sh_hits":           ship_sh_hits,
        "ship_hit_log":           ship_hit_log,
        "db_shot_down":           db_shot_down,
        "sh_shot_down":           sh_shot_down,
        "sorties_cancelled":      sorties_cancelled,
        "ship_loss_kills":        ship_loss_kills,
        "navy_dead":              navy_dead,
        "bm_intercepted":         bm_intercepted,
        "bm_hits":                bm_hits,
        "bm_marine_kills":        bm_marine_kills,
        "bm_outcome":             bm_outcome,
        "island_sh_shot_down":    island_sh_shot_down,
        "island_sh_hits":         island_sh_hits,
        "island_sh_marine_kills": island_sh_marine_kills,
        "sailors_deployed":       sailors_deployed,
        "sailor_dead":            sailor_dead,
        "sailors_on_island":      sailors_on_island,
    }
