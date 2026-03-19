# DAEMON
### *Dynamic Agent-based Engagement Model for Naval Operations*

> *"We may regard the present state of the universe as the effect of its past and the cause of its future. An intellect which at a certain moment would know all forces that set nature in motion, and all positions of all items of which nature is composed... nothing would be uncertain and the future just like the past would be present before its eyes."*
>
> — Pierre-Simon Laplace, *Philosophical Essay on Probabilities* (1814)

**DAEMON** inverts Laplace's premise. Rather than assuming perfect knowledge to predict a single future, it seeds thousands of interacting agents — each with incomplete information, probabilistic decisions, and position in space — and asks where the demon's certainty *breaks down*: the phase boundaries where tiny initial differences produce catastrophically different outcomes.

The theater is the Persian Gulf. The question is how many missiles, from which sites, in what sequence, with what defensive posture, tips an 8-CSG Combined Naval Force from survivable attrition to catastrophic loss. The simulation does not answer that question. It maps the terrain around it.

---

## Contents

- [Conceptual Model — The Forest Fire](#conceptual-model)
- [Phase Changes and Tipping Points](#phase-changes-and-tipping-points)
- [Simulation Architecture](#simulation-architecture)
- [Scenario Suite — CSG Naval Engagement](#scenario-suite--csg-naval-engagement)
- [Scenario Suite — Kharg Island Assault](#scenario-suite--kharg-island-assault)
- [Weapon Costs and Exchange Ratios](#weapon-costs-and-exchange-ratios)
- [Intercept System Costs](#intercept-system-costs)
- [Fleet Composition and Value at Risk](#fleet-composition-and-value-at-risk)
- [Combat Model Parameters](#combat-model-parameters)
- [Electronic Warfare Factors](#electronic-warfare-factors)
- [Sources and References](#sources-and-references)
- [Running the Simulation](#running-the-simulation)
- [Output — Google Earth KMZ](#output--google-earth-kmz)

---

## Conceptual Model

### The Forest Fire as a Template for Combat

A forest fire does not spread uniformly. It spreads through local interactions: each burning tree ignites adjacent trees according to wind, moisture, and fuel density. There is no central planner. The fire's shape, extent, and eventual stopping point emerge from millions of individual decisions made by individual trees.

Agent-based modeling (ABM) applies this logic to any system where macro-behavior emerges from micro-interactions rather than being imposed top-down. DAEMON uses ABM for two reasons:

1. **Real engagements are not equations.** The Lanchester differential equations describe population-level attrition averages. But the Aegis system's intercept capacity is a discrete integer (VLS cells), not a continuous variable. When the 66th SM-6 fires, the 67th does not exist. That discontinuity cannot live inside a differential equation; it must live inside an agent.

2. **Phase changes only appear in agent interactions, not in aggregate models.** If you model a fleet as a single "defense effectiveness" number, you will never see the moment CIWS reaches Winchester and the entire remaining salvo arrives uncontested. That is not a smooth degradation — it is a cliff. ABM finds the cliffs.

### How the Forest Fire Maps to Combat

| Forest Fire Element | DAEMON Equivalent |
|---|---|
| Individual tree | Individual agent (SRBM, Marine fire team, IRGC rifle squad, CVN, MV-22B) |
| Ignition probability | Single-shot Pk (probability of kill) per engagement step — configurable per weapon system |
| Wind direction | Movement vector toward assigned target (step_toward at system-specific km/s) |
| Moisture (resistance) | HP pool; Dupuy terrain/positional defense multiplier |
| Firebreak | Weapon Engagement Zone (WEZ), VLS magazine capacity, CIWS range gate |
| Fire reaching a gap in the firebreak | VLS depletion / CIWS Winchester — magazine exhaustion event |
| Crown fire (catastrophic spread) | IAMD saturation — all remaining leakers arrive uncontested |
| Fire stopping at a river | CSG survival boundary — sufficient SM-6 rounds remain to defeat the final wave |
| Burn scar | Dead-agent records: KMZ tracks every killed agent at exact position and sim step |

The simulation runs at 60-second steps. Every agent records position and HP at every step. The KMZ output animates the entire engagement, step by step, in Google Earth — the burn scar made visible.

---

## Phase Changes and Tipping Points

Laplace's demon fails at phase boundaries. DAEMON is designed to find them.

A **phase change** in this context is a discontinuity in the outcome surface: a region where increasing one input parameter by 1% changes the outcome not by 1% but by an order of magnitude. Four types appear repeatedly across the scenario suite:

### 1. VLS Depletion — The CIWS Winchester Event

Each DDG-51 carries a finite VLS magazine. When the last SM-6 is expended, the ship does not become "slightly less defended" — it becomes undefended against ballistic threats. In Scenario E (Iran Best Case), Aegis magazines across all 8 CSGs are exhausted at approximately T+60 minutes. The ~1,400 munitions already airborne at that moment arrive against a Combined Naval Force with only CIWS and 5-inch naval guns. Leaker count goes from 820 (Scenario D, Realistic) to 3,419 — a 4× jump from a roughly 15% increase in salvo size.

**This is the forest fire reaching the firebreak gap.**

### 2. IPDS Saturation — The Aegis Engagement Capacity Limit

The AN/SPY-1D(V) Baseline 9 IPDS (Integrated Passive Detection System) can engage approximately 18 targets simultaneously per CSG. Eight CSGs provide 144 simultaneous intercept tracks maximum. When Iranian munitions arrive faster than the 30-second engagement window clears, additional tracks queue. Queued tracks are not engaged — they are *leakers* or they are *not*. The UAS-saturation doctrine (Scenarios G/H/I) is specifically engineered to fill the Aegis track buffer with low-value OWA-UAS (Shahed-136, $35,000 each), forcing SM-6 expenditure against low-cost targets to suppress VLS capacity ahead of the $2M ballistic follow-on.

**This is the fire forcing smoke into the firebreak before the main front arrives.**

### 3. Phased vs. Simultaneous Launch — The Time-on-Target Compression Effect

Scenario D (Realistic: compressed 30-minute Time-on-Target window) achieves a 42% leaker rate. Scenario B (Medium: phased 6-hour window) achieves 36% with a larger total salvo. The compressed scenario produces *worse* outcomes for Iran despite the same arsenal — because it saturates Aegis radar tracks but also allows every defensive layer to reload between waves. The optimal doctrine is intermediate: OWA-UAS at T+0, ballistic at T+30 before CIWS reloads, ASCM at T+45 as SM-6 runs low.

**This is the fire timing its flanks to arrive at the firebreak simultaneously.**

### 4. IRGC Positional Advantage — The Fortified Defense Threshold

In the Kharg Island ground simulation, IRGC rifle squads within 0.9 km of their assigned defensive cluster fight with a 2.5× terrain/fortification multiplier (effective Pk 0.175 vs. the Marine's 0.112 per step). Once dislodged from prepared fighting positions, they fight in the open at 0.07 — a 60% degradation. The simulation shows an abrupt outcome shift at approximately 500 OPFOR defenders: below this threshold, Marines overwhelm prepared positions before the terrain advantage accumulates sufficient casualties; above it, the combined N²×terrain effect denies the vertical assault.

**This is the fire encountering a river — survivable below a threshold, uncrossable above.**

---

## Simulation Architecture

```
persian_gulf_simulation/
├── config.py              # All simulation constants — single patchable module
├── geography.py           # Kharg Island polygon, grid cell geometry
├── agents/
│   ├── base.py            # Agent class (position, HP, track, launch_step, peak_alt_m)
│   └── factory.py         # Agent initialization for all force types
├── simulation/
│   └── engine.py          # Main simulation loop — Lanchester, EW, intercept, movement
├── kml/
│   ├── document.py        # Top-level KML document assembly
│   ├── placemarks.py      # gx:Track / TimeSpan / parabolic arc generation
│   ├── styles.py          # KML style definitions (color-coded by force and weapon type)
│   ├── descriptions.py    # HTML balloon content (stats, JP citations, cost data)
│   ├── narration.py       # Battle narration event extraction
│   └── tour.py            # Google Earth fly-through tour generation
├── runner.py              # Scenario orchestration, _patch_scenario, main()
└── generate_wargame_kml.py # CSG naval engagement scenarios (independent module)
```

### Agent Lifecycle

Every agent follows the same lifecycle regardless of type:

```
Init → record(step=0) → [move / engage / be engaged] → record(step=N) → dead_step set → track ends
```

The complete position+HP history is preserved in `agent.track` as `[(step, lon, lat, hp), ...]`. KML generation reads this track and produces a `gx:Track` animated placemark with one keyframe per simulation step. Killed agents produce a separate static marker at their final position.

### Patching Scenarios

All constants live in `config.py`. The `_patch_scenario()` context manager calls `setattr(cfg, name, value)` for each scenario override, ensuring all submodules reading `cfg.X` see the patched value at call time. This allows 30+ scenarios to run from a single codebase with no code duplication.

---

## Scenario Suite — CSG Naval Engagement

> 60 KMZ files total. Each file contains fully animated agent tracks viewable in Google Earth.

### Primary Scenarios

| 🎯 Scenario | SRBMs/MRBMs | OWA-UAS | USV Swarm | Total | Intercept % | Leakers | Outcome |
|---|---|---|---|---|---|---|---|
| 🟢 **A — Low Capability** | 265 | 665 | 135 | 1,065 | ~69% | ~335 | CSG survives; degraded combat effectiveness |
| 🟡 **B — Medium Capability** | 665 | 1,335 | 200 | 2,200 | ~65% | ~793 | Multiple CVN/DDG hull impacts |
| 🟡 **D — Realistic** | 1,100 | ~5,000 | ~990 | 7,250 | 58% | ~820 | Non-permissive; indeterminate |
| 🔴 **C — High / IPDS CAP HIT** | 1,100 | 2,665 | 265 | 4,030 | ~66% | ~1,370 | Multiple CVN mission kills |
| 🔴 **E — Iran Best Case** | 1,000 | 4,000 | 400 | 5,400 | 37% | **3,419** | Catastrophic fleet loss |
| 🟢 **F — US Best Case** | 200 | — | — | 200 | ~81% | ~38 | CSG combat-effective; minimal damage |

### Phased Doctrine Scenarios — UAS-Saturation Sequencing (JP 3-30)

| 🎯 Scenario | Phase 1 (T+0) | Phase 2 (T+30) | Doctrine Effect |
|---|---|---|---|
| 🟢 **G — UAS-Saturation Low** | 665 OWA-UAS | 265 SRBMs | CIWS partially depleted prior to SRBM arrival |
| 🟡 **H — UAS-Saturation Medium** | 1,335 OWA-UAS | 665 SRBMs | CIWS Winchester by T+45; SRBM salvo uncontested by close-in defense |
| 🔴 **I — UAS-Saturation High** | 2,665 OWA-UAS | 1,100 SRBMs | Full CIWS/RAM depletion; Aegis IPDS overwhelmed |

### Specialized Scenarios

- 🟡 **J — Coordinated Strike** — US and IAF strike packages execute simultaneous SEAD/DEAD with time-on-target synchronization. Tests whether pre-H-Hour shaping operations reduce the threat enough to change the engagement outcome.
- 🟡 **K — Focused Salvo** — IRGC concentrates its entire missile inventory against a single hull (CVN-78 *Ford*) rather than distributing across the fleet. Tests single-ship IPDS saturation: can one carrier absorb a full national inventory?
- 🔴 **L2 — Hypersonic Threat** — 168 Fattah-1 HGV reentry vehicles mixed into a realistic salvo. Aegis single-shot Pk drops from ~60% (vs SRBM) to ~5% (vs HGV); tests whether the fleet can survive even a partial HGV integration.
- 🔴 **M — Pure Ballistic Salvo** — 600 SRBMs/MRBMs with no OWA-UAS preceding them. Tests the null hypothesis of the UAS-saturation doctrine: without CIWS pre-depletion, does a ballistic-only salvo fare better or worse?
- 🔴 **BB — Full Ballistic Surge** — Iran's full reconstituted inventory (2,500 missiles) against 4 CSGs, with 10% Fattah-1 HGV. The upper bound — what a fully recovered IRGC Aerospace Force looks like at maximum effort.
- 🟡 **N — ASCM Swarm** — 1,000 sea-skimming Anti-Ship Cruise Missiles approaching at wave-top altitude. Tests the horizon defense gap: Aegis radar sees ASCM only inside ~30 km, compressing the engagement window to seconds per target.
- 🔴 **O — SLOC Transit** — 8 CSGs transiting the 12 km-wide Strait of Hormuz channel. Constrained sea room eliminates evasive maneuvering; maximum threat density from coastal TELs on both shores.
- 🟡 **P — IAMD Layered Defense** — THAAD batteries + PAC-3 MSE + Aegis BMD operating as an integrated IAMD network. Tests how much additional intercept depth the layered architecture provides before VLS depletion.

### Depleted Arsenal Scenarios (Post-Strike — 8% Inventory)

> Reference: CSG Scenarios R/S/T. 8% of Iran's ~2,500 reconstituted SRBM stockpile ≈ 200 missiles (Alma Research, Feb 2026; 19FortyFive). Represents residual retaliatory capacity following US/Israeli SEAD/DEAD and counter-IADS shaping operations.

| 🎯 Scenario | Arsenal | IRGC C2 Posture | P(US Win) |
|---|---|---|---|
| 🟢 **R — US Wins: Preemption** | 15% survives H-Hour strike | Fragmented; TELs uncoordinated | ~94% |
| 🟢 **S — US Wins: EW Dominance** | 450 ballistic only (guidance denied) | GPS/INS denied; OWA-UAS non-functional | ~88% |
| 🟢 **T — US Wins: Allied IAMD Umbrella** | 550 (full coastal salvo) | Full salvo; degraded by Arrow/THAAD/Aegis BMD | ~83% |
| 🟡 **U — C2 Disrupted** | 900 (fragmented time-on-target) | IRGC C2 degraded; no wave coordination | ~71% |
| 🟡 **V — Arsenal Attrited** | 750 (high count, legacy lethality) | Legacy Shahab-3/Fateh-110 only; no MaRV | ~65% |
| 🟡 **Depleted UAS-First** | 8% inventory, UAS-saturation doctrine | Optimized sequencing despite reduced numbers | Contested |
| 🟡 **Depleted Coastal** | 8% inventory, coastal TEL batteries only | Coastal launch only; inland sites destroyed | Contested |
| 🟡 **Depleted Israel Split** | 8% split Gulf/Israel theater | Two-theater commitment; CENTCOM/EUCOM split | Contested |

### ISR Probe and HUF Scenarios

- 🟢 **Z — 1% ISR Probe** — 75 munitions (OWA-UAS → deliberate lull → precision follow-on). Iran uses a minimal salvo to force EMCON violations, observe Aegis track behavior, and perform Battle Damage Assessment before committing its main inventory.
- 🟡 **AA — 1% + Fattah-2 HGV** — Same 75-munition probe, with 10 Fattah-2 HGVs riding the terminal phase. Near-certain leakers (9–10 expected) at near-zero Pk against current Aegis BMD; tests precision strike under full detection.
- 🔴 **Caves — HUF Network** — 7,250 munitions launched from 25 dispersed Hardened Underground Facility sites. Each HUF requires a two-hit kill sequence to neutralize; TELs reload between sorties. Tests whether a geographically dispersed, hardened launch architecture can exhaust the strike package before the source is suppressed.

---

## Scenario Suite — Kharg Island Assault

30 KMZ files. Agent-based ground simulation: Lanchester Square Law attrition, FIM-92 Stinger MANPADS, MV-22B Osprey assault support sorties, Iranian SRBM and OWA-UAS retaliation in every scenario.

The operation models a USMC MAGTF (Marine Air-Ground Task Force) heliborne vertical assault against IRGC Ground Forces defending Kharg Island. Marines are organized into 4-man fire teams inserted by MV-22B in multiple assault waves.

### Scenario Rankings

**Likelihood** — probability that this specific configuration would occur in an actual operation. Anchored to open-source IRGC order of battle, US MAGTF doctrine, and Iranian retaliation precedent (Operation Martyr Soleimani, 2020; Operation True Promise, 2024).

| Rank | Scenario | Rationale |
|---|---|---|
| 🥇 1 | **F-35 Strike + Iranian BM Retaliation** | Most complete doctrinal scenario. US pre-strikes before any contested island assault; Iran retaliates with SRBMs as a near-certainty (JP 3-02 + historical precedent). |
| 2 | **Contested EMS — 250 OPFOR** | Bilateral EW is the baseline of modern combat. Iran fields GPS jammers and ECM routinely; US deploys DIRCM and COMJAM as standard package. |
| 3 | **F-35 Strike GPS Jammed (22% survive)** | Iran demonstrated persistent GPS jamming in Gulf operations. JDAM CEP degradation under jamming is documented (RQ-170 incident, 2011). |
| 4 | **Baseline — FIM-92 Stinger (250 OPFOR)** | Intelligence baseline. Kharg Island peace-time garrison ~200–300 IRGC GF; FIM-92 Mistrals/clones confirmed in IRGC inventory via captured Iraqi stocks. |
| 5 | **Russian Igla-S SA-24 — 250 OPFOR** | Iran has documented Igla-S acquisition; dual IR/UV seeker confirmed in IRGC MANPADS battalions (IISS 2024). |
| 6 | **F-35 Lightning Strike — 8% IRGC survive** | Standard pre-H-Hour SEAD/DEAD is doctrinal for any opposed MAGTF assault (JP 3-02). |
| 7 | **US EW Dominance — 250 OPFOR** | US would bring DIRCM + COMJAM; full dominance is optimistic but achievable at 250 OPFOR. |
| 8 | **FIM-92 Stinger — 500 OPFOR** | Crisis reinforcement to 500 is realistic; Kharg Island has garrison infrastructure for at least one reinforced battalion. |
| 9 | **DIRCM Suppressed MANPADS — 250 OPFOR** | AN/AAQ-24 DIRCM is standard on USMC assault support aircraft. Single-variable DIRCM test is operationally representative. |
| 10 | **Contested EMS — 1,500 OPFOR** | Crisis-reinforced garrison (1,500) with bilateral EW — realistic if Iran has 72+ hr warning of impending assault. |
| 11 | **Igla-S SA-24 — 1,500 OPFOR** | Reinforced garrison + Russian MANPADS transfer; consistent with Iranian procurement under sanctions-evasion channels. |
| 12 | **FIM-92 Stinger — 1,500 OPFOR** | 1,500 IRGC GF on Kharg plausible at full crisis mobilization. |
| 13 | **Russian Verba SA-25 — 250 OPFOR** | SA-25 newer; Iran pursuing acquisition per FDD/JINSA reporting (2025–2026). Credible near-term threat. |
| 14 | **FIM-92 Extended Hover (60s)** | Realistic operational risk — TRAP/CASEVAC tasking can extend hover exposure window. |
| 15 | **DIRCM Suppressed — 1,500 OPFOR** | DIRCM effectiveness against elevated OPFOR; operationally plausible combination. |
| 16 | **US EW Dominance — 1,500 OPFOR** | Full US EW package against reinforced garrison; ambitious but achievable. |
| 17 | **PRC QW-2 — 250 OPFOR** | Iran–China defense relationship; QW-2 confirmed in PLA export catalog. Plausible via intermediary. |
| 18 | **Russian Verba SA-25 — 1,500 OPFOR** | Advanced MANPADS + reinforced garrison; high-threat combination but requires SA-25 transfer completion. |
| 19 | **PRC QW-2 — 1,500 OPFOR** | Chinese MANPADS + crisis garrison. |
| 20 | **PRC FN-6 — 250 OPFOR** | FN-6 documented in Houthi and Hezbollah inventories; possible Iran pathway. Less likely than SA-24/QW-2. |
| 21 | **PRC FN-6 — 1,500 OPFOR** | Same as above at elevated OPFOR. |
| 22 | **FIM-92 Stinger — 2,000 OPFOR** | 2,000 on a 37 km² island is extreme; requires pre-war strategic warning and deliberate build-up over weeks. |
| 23–30 | **Permissive JAAT variants (250–2,000 OPFOR)** | Complete MANPADS suppression before Marines land is the optimistic end-state, not a baseline. Increasing OPFOR makes it less plausible that zero MANPADS survive. Permissive JAAT + 2,000 OPFOR is the least realistic scenario in the suite. |

---

**Complexity** — number of simultaneously active subsystems, EW variables, distinct phases, and agent interactions. Baseline = all defaults active (ground battle + maritime + retaliation).

| Rank | Scenario | Active Subsystems |
|---|---|---|
| 🥇 1 | **F-35 Strike + Iranian BM Retaliation** | 3 phases (pre-strike analysis → beach assault → retaliation); 100 SRBMs in 10 staggered waves from 3 launch sites; 100 island-targeting Shahed-136; ship SAM intercept chain; IRGCN drone boat swarm; Helmbold coverage model; Lanchester ground battle. |
| 2 | **Contested EMS — 1,500 OPFOR** | 6 simultaneous EW variables (COMJAM, DIRCM, MILDEC, GPS spoof, Iran ECM, Shahed abort); 1,500 OPFOR Lanchester; all maritime threats; OWA-UAS + SRBM retaliation. |
| 3 | **Contested EMS — 250 OPFOR** | Same 6 EW variables; baseline OPFOR. |
| 4 | **US EW Dominance — 1,500 OPFOR** | 5 US EW variables (DIRCM + COMJAM + MILDEC + GPS spoof + SAM mult); 1,500 OPFOR; full maritime + retaliation. |
| 5 | **US EW Dominance — 250 OPFOR** | 5 US EW variables; baseline OPFOR. |
| 6 | **F-35 Strike GPS Jammed (22%)** | Pre-strike Helmbold analysis + GPS jamming CEP model + beach assault + retaliation; 2 modified variables interacting. |
| 7 | **F-35 Lightning Strike — 8% survive** | Pre-strike analysis + beach assault + full retaliation phase; 2 phases. |
| 8 | **DIRCM Suppressed — 1,500 OPFOR** | 1 EW variable (DIRCM) + 1,500 OPFOR interaction; full maritime. |
| 9 | **Verba SA-25 — 1,500 OPFOR** | Highest-Pk MANPADS (0.40/0.90) + maximum plausible OPFOR; Osprey attrition compounds Lanchester losses. |
| 10 | **Igla-S SA-24 — 1,500 OPFOR** | Modified MANPADS + elevated OPFOR; dual-variable interaction. |
| 11 | **DIRCM Suppressed — 250 OPFOR** | Single EW variable; all other systems default. |
| 12 | **FIM-92 Stinger — 2,000 OPFOR** | Maximum OPFOR agent count; force-size boundary test. |
| 13 | **Verba SA-25 — 250 OPFOR** | MANPADS system substitution only. |
| 14 | **PRC QW-2 — 1,500 OPFOR** | Modified MANPADS + elevated OPFOR. |
| 15 | **PRC FN-6 — 1,500 OPFOR** | Modified MANPADS + elevated OPFOR. |
| 16 | **Igla-S SA-24 — 250 OPFOR** | MANPADS system substitution only. |
| 17 | **FIM-92 Stinger — 1,500 OPFOR** | Force-size change only. |
| 18 | **PRC QW-2 — 250 OPFOR** | MANPADS system substitution only. |
| 19 | **PRC FN-6 — 250 OPFOR** | MANPADS system substitution only. |
| 20 | **FIM-92 Stinger — 500 OPFOR** | Single force-size variable. |
| 21 | **FIM-92 Extended Hover (60s)** | Single timing variable (hover window). |
| 22 | **Baseline — FIM-92 Stinger (250 OPFOR)** | All defaults; reference scenario; fewest modified parameters. |
| 23–30 | **Permissive JAAT variants (2,000 → 250 OPFOR)** | MANPADS zeroed out; only OPFOR count varies. Decreasing OPFOR = decreasing active agent interactions. Permissive JAAT + 250 OPFOR is the least complex scenario: single modified parameter (MANPADS PK=0), minimum agent count, shortest simulation runtime. |

---

### Baseline and OPFOR Force-Size Scenarios

| 🎯 Scenario | OPFOR (IRGC) | MANPADS Teams | Outcome |
|---|---|---|---|
| 🟡 **Baseline** | 250 | 12 | Contested — objective not secured |
| 🔴 **OPFOR 500** | 500 | 25 | OPFOR repels vertical assault |
| 🔴 **OPFOR 1,500** | 1,500 | 75 | OPFOR repels vertical assault |
| 🔴 **OPFOR 2,000** | 2,000 | 100 | OPFOR repels vertical assault |
| 🟢 **Permissive JAAT** | 250 | 0 | USMC secures objective |
| 🟢 **Extended Loiter (60s)** | 250 | 12 | USMC secures objective |

### MANPADS System Scenarios — Threat Assessment

| 🎯 Scenario | System | Pk Transit | Pk Hover (LZ) | Outcome |
|---|---|---|---|---|
| 🟡 **FIM-92 Stinger** | US-origin MANPADS | 0.25 | 0.75 | Contested (250 OPFOR) |
| 🔴 **9K338 Igla-S (SA-24)** | Russian MANPADS; dual-channel IR/UV seeker | 0.35 | 0.85 | OPFOR repels (1,500) |
| 🔴 **9K333 Verba (SA-25)** | Russian MANPADS; 3-channel seeker, ECCM-resistant | 0.40 | 0.90 | OPFOR repels |
| 🔴 **QW-2** | PRC MANPADS; proportional navigation, IIR seeker | 0.30 | 0.80 | Contested (250) |
| 🔴 **FN-6 (HY-6)** | PRC MANPADS; passive IR + rosette scanning | 0.28 | 0.78 | Contested (250) |
| 🟢 **DIRCM-Suppressed (10%)** | AN/AAQ-24 DIRCM equipped Ospreys; 90% MANPADS defeat | 0.025 | 0.075 | USMC secures objective |

### F-35B SEAD Package and Electronic Warfare Scenarios

- 🟢 **F-35B Lightning Strike** — Coordinated F-35B/F/A-18/EA-18G SEAD/DEAD package reduces IRGC defenders to 8% before the Marine landing. No MANPADS survive the strike; beach insertion is permissive. USMC secures objective.
- 🟢 **F-35B Strike + SRBM Retaliation** — Same 8%-survival strike, but Iran responds with 100 SRBMs and 100 Shahed-136 OWA-UAS once Marines are ashore. Tests whether the fleet and landing force can absorb retaliation after a successful pre-H-Hour shaping package.
- 🟢 **GPS Denial (IRGC Jammers)** — IRGC ground-based GPS/INS jammers degrade JDAM CEP, causing 22% of defenders to survive the pre-strike instead of 8%. Tests the margin of the strike package against guidance degradation.
- 🟢 **EW Dominance (250 OPFOR)** — AN/AAQ-24 DIRCM on Ospreys defeats 90% of MANPADS shots; COMJAM on IRGC tactical nets halves their combat effectiveness; MILDEC misdirects 30% of defenders for 20 minutes. USMC secures, but Iranian sea drones create ship-loss risk.
- 🔴 **EW Dominance (1,500 OPFOR)** — Same full US EW package against 1,500 OPFOR. Tests whether electronic dominance can substitute for mass when the OPFOR force-size phase boundary has already been crossed.
- 🟡 **Contested EMS (250 OPFOR)** — US EW package active, but Iran counters with ECM on ship SAM radars (Pk −30%) and GPS spoofing on its own Shahed guidance (30% abort). Simultaneous degradation of both sides' EW effectiveness.
- 🔴 **Contested EMS (1,500 OPFOR)** — Same bilateral EW contest at 1,500 OPFOR. Outcome driven almost entirely by force-size phase change; EW factors become secondary.

### Iranian Retaliation — Present in All 30 Scenarios

All Kharg Island scenarios include an Iranian SRBM salvo and OWA-UAS retaliation phase following the Marine landing:

| Wave | Time | System | Launch Sites |
|---|---|---|---|
| **SRBM Salvo** | H+50 min | 100 SRBMs, staggered 10/step rolling wave | Shiraz MB (40%), Bushehr AB (20%), Bandar Abbas Complex (40%) |
| **OWA-UAS Strike** | H+55 min | 100 Shahed-136 loitering munitions | Eastern Iran coastal launch sites |

**SRBM types and KML trajectories match CSG scenario visualization exactly:**

| 🎨 Color | KML Code | System | Apogee | Launch Site |
|---|---|---|---|---|
| 🟠 Deep orange-red | `cc0055ff` | Fateh-313 SRBM | 75 km | Shiraz Missile Brigade + Bushehr AB |
| 🟡 Orange | `cc0066ff` | Zolfaghar SRBM | 130 km | Bandar Abbas Complex |

---

## Weapon Costs and Exchange Ratios

> All costs are unclassified open-source estimates. Range reflects uncertainty in domestic Iranian production costs vs. export pricing. Costs in USD.

### Iranian Offensive Munitions

| 🎨 Tier | System | Unit Cost | Range | CEP | Terminal Speed | Source |
|---|---|---|---|---|---|---|
| 🟢 Low | **Shahed-136** OWA-UAS (loitering munition) | **$35,000** | 2,000 km | 30 m | 185 km/h | CSIS Feb 2025 median; $20K–$50K domestic |
| 🟢 Low | **Shahed-238** jet-powered OWA-UAS | **$100,000** | 1,800 km | 20 m | 560 km/h | Wikipedia; United24 Media; ISIS 2025 |
| 🟡 Mid | **IRGCN FIAC/USV** (sea drone, 45 kts) | **$100,000** | 300 km | 3 m | 45 kts | IRGCN procurement estimates |
| 🟡 Mid | **Fateh-110 SRBM** | **$700,000** | 300 km | 50 m | Mach 3.0 | CSIS Missile Threat; $500K–$1.2M |
| 🟡 Mid | **Fateh-313 SRBM** (GPS/INS guided) | **$800,000** | 500 km | 30 m | Mach 3.3 | IISS; $600K–$1.5M |
| 🟡 Mid | **Shahab-3 MRBM** (legacy unguided RV) | **$800,000** | 1,300 km | 500 m | Mach 4.2 | CSIS/IISS; $500K–$1.5M |
| 🟡 Mid | **Noor ASCM** (C-802 derivative, active radar) | **$500,000** | 170 km | 10 m | Mach 0.9 | Jane's; $300K–$700K |
| 🔴 High | **Zolfaghar SRBM** (precision GPS/INS, <10m CEP spec) | **$1,000,000** | 700 km | 10 m | Mach 3.6 | IISS; $700K–$1.5M |
| 🔴 High | **Emad MRBM** (MaRV terminal maneuver) | **$2,000,000** | 1,700 km | 30 m | Mach 4.5 | IISS; $1.5M–$3M |
| 🔴 High | **CM-302 Supersonic ASCM** (PRC-derived) | **$2,000,000** | 400 km | 5 m | Mach 3.0 | Chinese-derived; $1M–$3M |
| 🔴 High | **Khalij Fars ASBM** (Anti-Ship Ballistic Missile, EO/IR seeker) | **$2,000,000** | 300 km | 5 m | Mach 3.9 | Jane's; $1M–$3M |
| 🔴 Very High | **Fattah-1 HGV** (Hypersonic Glide Vehicle, Mach 13–15) | **$3,000,000** | 1,400 km | 100 m | Mach 13+ | CSIS; $2M–$5M; JINSA 2025 |
| 🔴 Very High | **Fattah-2 HGV** (HGV with pitch/yaw correction) | **$4,000,000** | 1,400 km | 75 m | Mach 13+ | Hudson Institute 2026; JINSA Feb 2026 |

### US/Israeli Strike Munitions

| 🎨 Tier | System | Unit Cost | Platform | Source |
|---|---|---|---|---|
| 🟢 Low | **JDAM-ER** (GBU-38/32 + ER wing kit) | **$30,000** | F-35B/I | FY2023 DoD contract |
| 🟡 Mid | **JASSM-ER** (AGM-158B, stealthy ALCM) | **$1,400,000** | B-2, F-15E, F-35 | FY2023 multiyear contract |
| 🟡 Mid | **SPICE-2000** (IAF precision glide bomb) | **$800,000** | F-35I Adir | Rafael estimate; $600K–$1M |
| 🟡 Mid | **Rampage ALCM** (IAF air-launched CM) | **$500,000** | F-35I, F-16I Sufa | Israeli MoD estimate |
| 🟡 Mid | **AIM-120C-8 AMRAAM** (BVR AAM) | **$1,800,000** | F/A-18E/F, F-35 | FMS unit cost $2.46M incl. support |
| 🔴 High | **SLAM-ER** (AGM-84H/K, standoff land attack) | **$1,300,000** | F/A-18E/F Super Hornet | FY2023 procurement |
| 🔴 High | **TLAM Block IV** (BGM-109, land attack CM) | **$2,000,000** | DDG/CG/SSN VLS | DoD FY2023 Lot 25 contract |

---

## Intercept System Costs

> US expenditure per engagement event. These costs drive the exchange ratio asymmetry across all scenarios.

| 🎨 Tier | System | Cost per Engagement | Inventory per DDG-51 Flight III | Source |
|---|---|---|---|---|
| 🟢 Low | **Phalanx CIWS Mk 15** (20mm M61A1 rounds) | **$50,000** | 1,550-round magazine | DoD procurement data |
| 🟢 Low | **Mk 45 5-inch/54 Naval Gun** | **$50,000** per engagement | ~600 rounds | DoD |
| 🟡 Mid | **SeaRAM / Mk 49 RAM Block 2** (blended engagement) | **$800,000** | 21 rounds per Mk 49 launcher | DoD blended engagement cost |
| 🟡 Mid | **ESSM Block 2** (RIM-162D, quad-packed in VLS) | **$1,500,000** | ~32 per DDG-51 Flight III | FY2024 contract |
| 🔴 High | **SM-2 Block IIIB** (RIM-66M, medium-range SAM) | **$2,100,000** | ~20–44 per DDG | NAVSEA |
| 🔴 High | **SM-6 Block IA** (RIM-174A, blended flyaway) | **$4,500,000** | 10–18 per DDG-51 Flight III | CBO FY2025 estimate |
| 🔴 Very High | **SM-3 Block IA** (RIM-161A, Aegis BMD) | **$9,574,000** | Limited (BMD-configured ships) | DoD SAR Dec 2023 |

### Exchange Ratio Asymmetry

The fundamental economic problem: IRGC can expend a $35,000 OWA-UAS and compel the US to respond with a $4.5M SM-6.

| Matchup | Iran Expends | US Intercepts | Cost Ratio |
|---|---|---|---|
| Shahed-136 OWA-UAS vs SM-6 | $35,000 | $4,500,000 | **129:1** unfavorable to US |
| Fateh-313 SRBM vs SM-6 | $800,000 | $4,500,000 | **5.6:1** unfavorable to US |
| Emad MRBM vs SM-3 Block IA | $2,000,000 | $9,574,000 | **4.8:1** unfavorable to US |
| Fattah-1 HGV vs SM-3 Block IA | $3,000,000 | $9,574,000 | **3.2:1** unfavorable to US |

> Scenarios consistently show **total US cost (intercept expenditure + hull/air wing damage) running 80–300× Iran's offensive expenditure**, driven primarily by the OWA-UAS to interceptor cost differential. This asymmetry is the economic logic underlying the UAS-saturation doctrine.

---

## Fleet Composition and Value at Risk

### 8-CSG Combined Naval Force

| 🎨 Risk | Hull | Cost | Air Wing | VLS Cells | SM-6 Load | Ship's Company |
|---|---|---|---|---|---|---|
| 🔴 | **CVN-72 USS Abraham Lincoln** (Nimitz-class) | $9.0B | $4.0B | — | — | ~5,000 |
| 🔴 | **CVN-78 USS Gerald R. Ford** (Ford-class) | $13.3B | $4.0B | — | — | ~5,000 |
| 🔴 | **CVN-77 USS George H.W. Bush** (Nimitz-class) | $9.0B | $4.0B | — | — | ~5,000 |
| 🟡 | **DDG-51 Flight III** Arleigh Burke (per ship) | ~$2.2B | — | 96 VLS | 10–18 | ~330 |
| 🟡 | **DDG-51 Flight IIA** Arleigh Burke (per ship) | ~$1.9B | — | 90 VLS | 8–16 | ~330 |
| 🟡 | **CG-47 Ticonderoga**-class cruiser (per ship) | ~$1.1B | — | 122 VLS | 12 | ~400 |
| 🟢 | **DDG-1000 Zumwalt**-class (per ship) | ~$4.4B | — | 80 VLS | TBD | ~175 |

| Metric | Value |
|---|---|
| **Total Combined Naval Force value** (hulls + air wings, 8 CSGs) | **~$169.6 billion** |
| **Total personnel at risk** | **~68,000** |
| **Total SM-6 available** (8 CSGs × ~12 avg per DDG/CG) | **~480 rounds** |
| **Simultaneous engagement capacity** (8 CSGs × 18 IPDS tracks) | **~144 tracks** |
| **CIWS rounds per CVN** | **~3,100 (2× Phalanx Mk 15)** |
| **RAM rounds per CVN** | **~63 (3× Mk 49 Ford-class)** |

---

## Combat Model Parameters

### Lanchester Square Law — Ground Combat Attrition

The simulation applies Lanchester's Square Law: in directed fire, combat power scales as N² × Q (force size squared times quality multiplier). Attrition is applied per 60-second step for every engaged unit pair within the 300m Weapon Engagement Zone (WEZ).

| Parameter | Value | Derivation | Source |
|---|---|---|---|
| **LANCHESTER_Q** | **1.6** | USMC Combat Effectiveness Value (CEV) over IRGC Ground Forces | Dupuy QJM, calibrated to IDF/Egypt 1967–1973 |
| **IRGC_PK** | **0.07** | P(OPFOR kills 1 Marine HP) per 60s step | Baseline anchor; produces realistic 2–3 hr engagements |
| **MARINE_PK** | **0.112** | = IRGC_PK × Q = 0.07 × 1.6; derived automatically | Never hand-tuned; adjusts proportionally with Q |
| **IRGC_DEFENSE_MULT** | **2.5** | Dupuy terrain/positional multiplier for prepared fighting positions | Dupuy terrain tables; fortified positions with interlocking fields of fire |
| **IRGC_HOME_RADIUS_KM** | **0.9 km** | Positional advantage active within assigned defensive cluster | Lost when OPFOR is dislodged from prepared positions |
| **ENGAGE_KM** | **0.30 km** | Weapon Engagement Zone (WEZ) for direct-fire small arms | Small-unit infantry doctrine |
| **STEP_S** | **60 s** | Simulation step duration | — |

**Historical CEV calibration (Dupuy QJM):**

| Conflict | CEV | Notes |
|---|---|---|
| IDF vs Egyptian Army, 1967 | 1.75 | IDF professional vs Soviet-doctrine conscript — closest structural analog |
| IDF vs Egyptian Army, 1973 | 1.98 | Same OPFOR; better trained post-1967 |
| USMC vs NVA, Battle of Hue City, 1968 (implied) | ~1.3 | MOUT; prepared urban defense; lower bound |
| USMC vs IJA, Iwo Jima, 1945 (implied) | ~1.5–1.8 | Fortified island vertical assault — direct structural analog |
| **DAEMON (USMC vs IRGC Ground Forces)** | **1.6** | Adjusted down from IDF/Egypt for IRGC ideological cohesion and proxy-war experience |

Source: Trevor Dupuy, *Numbers, Predictions and War* (1979); Dupuy Institute CEV studies.

---

## Electronic Warfare Factors

All EW multipliers default to 1.0 (no effect). Scenario overrides apply values derived from unclassified Joint Publication doctrine.

| EW Capability | Parameter | Baseline | Active Value | Doctrine Basis |
|---|---|---|---|---|
| **COMJAM** — IRGC tactical net jamming | `EW_IRGC_PK_MULT` | 1.0 | 0.50 | JP 3-13.1: sustained COMJAM reduces C2 effectiveness 40–60% |
| **COMJAM** — C2 disruption, positional defense | `EW_IRGC_DEFENSE_MULT_ADJ` | 1.0 | 0.50 | JP 3-13.1 |
| **DIRCM/SPJ** — MV-22B self-protection jammer | `EW_MANPADS_PK_MULT` | 1.0 | 0.10 | AN/AAQ-24 DIRCM: 85–95% MANPADS defeat rate; JP 3-13.1 |
| **MILDEC** — false LZ deception operation | `EW_MILDEC_FRACTION` | 0.0 | 0.30 | 30% OPFOR misdirected for ~20 min; JP 3-13 |
| **GPS Denial** — IRGC ground-based jamming | `EW_SHAHED_ABORT_RATE` | 0.0 | 0.30 | JP 3-85: GPS denial degrades OWA-UAS datalink; 30% mission abort |
| **Iranian ECM** — shipborne SAM radar jamming | `EW_SHIP_SAM_PK_MULT` | 1.0 | 0.70 | JP 3-85: contested EMS reduces SAM Pk ~30% |

Sources: JP 3-13 *Information Operations*; JP 3-13.1 *Electronic Warfare*; JP 3-85 *Joint Electromagnetic Spectrum Operations*; JP 3-09 *Joint Fire Support*; RAND EW studies; CNA *Electronic Warfare in Modern Conflict* (2019); RQ-170 GPS spoof incident (2011) open-source analysis.

---

## Sources and References

### Doctrine and Military Studies

| Source | Used For |
|---|---|
| JP 3-13 *Information Operations* | IO/MILDEC factor derivation |
| JP 3-13.1 *Electronic Warfare* | COMJAM, DIRCM effectiveness values |
| JP 3-85 *Joint Electromagnetic Spectrum Operations* | GPS denial, SAM Pk degradation |
| JP 3-09 *Joint Fire Support* | EW/fires integration factors |
| JP 3-02 *Amphibious Operations* | MAGTF assault doctrine, LZ procedures |
| JP 3-30 *Command and Control of Joint Air Operations* | UAS sequencing doctrine |
| Trevor Dupuy, *Numbers, Predictions and War* (1979) | Lanchester Q / CEV calibration |
| Dupuy Institute CEV studies | IDF/Egypt 1967–1973 historical CEV data |
| RAND *Multilayer BMD* | SM-6/SM-3 single-shot Pk estimates |
| CSBA *Salvo Competition* (2015) | Naval VLS magazine saturation analysis |
| Wilkening, *Science & Global Security* (2000) | SSPK (Single-Shot Probability of Kill) methodology |
| DOT&E FY2018, FY2022 Annual Reports | Aegis intercept effectiveness validation |
| NAVSEA Aegis BMD 6.3 brief | IPDS simultaneous engagement capacity |
| CNA *Electronic Warfare in Modern Conflict* (2019) | EW degradation factor validation |

### Intelligence and Inventory Estimates

| Source | Used For |
|---|---|
| IISS *Military Balance 2024* | Iranian missile inventories, CSG fleet composition |
| CSIS Missile Threat database | Missile specifications, CEP, max range |
| Jane's Defence Weekly 2024 | Missile unit costs, aircraft loadouts |
| Alma Research, Feb 2026 | Iran reconstituted SRBM stockpile (~2,500 post-2025) |
| 19FortyFive, Feb 2026 | Post-conflict Iranian inventory assessment |
| IDF intelligence estimate, Feb 2026 | Current Iranian stockpile composition |
| CENTCOM Gen. McKenzie testimony, 2022 | Iranian ballistic missile threat assessment |
| FDD (Foundation for Defense of Democracies), Feb 2026 | Fattah-2 HGV operational capability |
| JINSA *Shielded by Fire* (Aug 2025) | SM-6 Pk, intercept cost validation |
| FPRI *Shallow Ramparts* (Oct 2025) | Layered IAMD effectiveness |
| Red Sea / OOD Prosperity Guardian data (2023–2025) | Real-world Shahed-136 cost and intercept validation |

### Procurement and Cost Data

| Source | Used For |
|---|---|
| DoD FY2023 Lot 25 contract (BGM-109) | TLAM Block IV unit cost $2.0M |
| FY2023 multiyear contract (AGM-158B) | JASSM-ER unit cost $1.4M |
| DoD Selected Acquisition Report, Dec 2023 | SM-3 Block IA unit cost $9.574M |
| Japan FMS notification Jan 2025 (150 SM-6 at $900M) | SM-6 reference cost $6.0M |
| CBO blended FY2025 estimate | SM-6 flyaway cost $4.5M |
| CSIS Feb 2025 | Shahed-136 OWA-UAS median unit cost $35,000 |
| NAVAIR MV-22B Osprey fact sheet | Assault support aircraft performance data |
| Boeing CH-53E Super Stallion specification | Heavy-lift assault support capacity |
| USMC MAGTF Handbook 2025 | Marine fire team assault doctrine |
| USNI News, NAVSEA public briefs | DDG/CG VLS magazine loadouts |

---

## Running the Simulation

### Requirements

```
Python 3.11+
No external dependencies — pure stdlib
```

### Installation

```bash
git clone https://github.com/your-org/daemon
cd daemon
pip install -e .
```

### Generate All Kharg Island Scenarios (30 KMZ files)

```bash
make kharg
# or: python -m persian_gulf_simulation.runner
# Output: output/scenarios/kharg_island_*.kmz
```

### Generate All CSG Naval Scenarios (30 KMZ files)

```bash
make csg
# or: python -m persian_gulf_simulation.generate_wargame_kml
# Output: output/scenarios/scenario_*.kmz
```

### Generate Everything

```bash
make all
```

### Run a Single Scenario Programmatically

```python
from persian_gulf_simulation.runner import _run_scenario, _patch_scenario

with _patch_scenario(n_irgc=500, stinger_pk=0.35, ew_manpads_pk_mult=0.10):
    _run_scenario("output/my_scenario.kmz",
                  scenario_label="OPFOR 500 — SA-24 with DIRCM Package",
                  iran_retaliation=True)
```

---

## Output — Google Earth KMZ

Each KMZ file contains:

- **Animated gx:Track placemarks** — every agent moves along its recorded path, step by step, in Google Earth's timeline
- **Parabolic SRBM/MRBM arcs** — absolute altitude mode, apogee 75–350 km depending on missile system
- **Color-coded forces** — green→yellow→red HP degradation for Marines and IRGC OPFOR; system-specific colors for SRBMs, OWA-UAS, USVs, and ships
- **Balloon descriptions** — every agent and folder carries a full HTML data card: unit stats, kill counts, cost data, JP doctrine citation for each parameter
- **Battle narration** — timestamped event placemarks (first Marine landing, first ship ordnance impact, CIWS Winchester, objective secured)
- **Fly-through tour** — automated Google Earth camera tour following key engagement events
- **Battle summary** — top-level document balloon with full outcome scorecard, EW status, cost exchange ratio, and Iranian retaliation BDA

Open any `.kmz` file directly in Google Earth Pro (free). Use the Timeline slider to scrub through the engagement or press Play to watch it animate.

---

## License

Research and educational use. All weapon specifications and cost estimates are derived from unclassified open-source materials. No classified information was used or referenced.

---

*DAEMON — where Laplace's demon meets the edge of its own certainty.*
