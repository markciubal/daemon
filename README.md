# DAEMON
### *Dynamic Agent-based Engagement Model for Naval Operations*

---

## BOTTOM LINE UP FRONT

DAEMON is a combat simulator for the Persian Gulf. You run it on your laptop, it plays out the fight, and spits out a file you open in Google Earth. The file animates every aircraft, missile, ship, and Marine fire team moving across a map of Kharg Island and the Gulf — from H-Hour to end of engagement. Each scenario takes about 5–15 seconds to compute and produces a fully animated battle reconstruction you can scrub through, pause, and zoom into.

**What it tells you:** Whether a US Marine assault on Kharg Island succeeds or fails under different threat conditions — enemy force size, missile types, electronic warfare, Iranian SRBM retaliation — and where the line is between "Marines win" and "Marines get repelled."

**What it does NOT do:** Predict the future. It maps the terrain around outcomes so you understand which variables matter and how sensitive the result is to each one.

---

## THIS SOFTWARE IS DESIGNED TO BE MODIFIED BY AI

DAEMON is not finished software. It is a starting point you are meant to extend.

The codebase is structured specifically so that an AI coding assistant — Claude, Copilot, ChatGPT, or similar — can read it, understand it completely, and make changes on your instruction. Every constant is in one file. Every module has one clear job. The simulation, the visualization, and the scenarios are all separate so the AI can change one without breaking the others.

**How to use it:**

1. Open this project folder in VS Code (or any editor with AI assistant support)
2. Load the AI assistant — Claude Code, GitHub Copilot, Cursor, or similar
3. Tell it in plain English what you want changed

Examples of things you can say:

- *"Add a CH-53E Super Stallion as a second aircraft type with higher capacity but lower speed"*
- *"Create a scenario where Iran uses Fattah-1 hypersonic missiles instead of Fateh-313s"*
- *"Make the Ospreys fly in pairs so when one gets shot down the other turns back"*
- *"Add a USS Nimitz carrier to the fleet and show it on the map"*
- *"Change the ground combat to use Helmbold's modified Lanchester model instead"*
- *"Add a scenario where Iranian mini-submarines attack the fleet"*

The AI will read the code, find the right place to make the change, and do it. You do not need to know how to program. You need to know what question you want answered.

**The codebase is small on purpose.** Every Python file has a clear description at the top. The AI can read the whole thing in one pass and understand the full picture. If you ask it to add something, it knows where it goes.

**If the AI gets confused**, it's usually because the request touches more than one system at once. In that case, break it into steps: *"First add the new aircraft type. Now add the scenario that uses it."*

---

---

## CONTENTS

- [This Software Is Designed to Be Modified by AI](#this-software-is-designed-to-be-modified-by-ai)
- [What This Is and Why It Exists](#what-this-is-and-why-it-exists)
- [Technical Requirements](#technical-requirements)
- [Installation — Step by Step](#installation--step-by-step)
- [Running the Simulation — Step by Step](#running-the-simulation--step-by-step)
- [Viewing the Output in Google Earth](#viewing-the-output-in-google-earth)
- [Changing Variables / Running Custom Scenarios](#changing-variables--running-custom-scenarios)
- [What the Colors Mean](#what-the-colors-mean)
- [Scenario Suite — Kharg Island Assault](#scenario-suite--kharg-island-assault)
- [Scenario Suite — CSG Naval Engagement](#scenario-suite--csg-naval-engagement)
- [Weapon Costs and Exchange Ratios](#weapon-costs-and-exchange-ratios)
- [Intercept System Costs](#intercept-system-costs)
- [Fleet Composition and Value at Risk](#fleet-composition-and-value-at-risk)
- [Combat Model Parameters](#combat-model-parameters)
- [Electronic Warfare Factors](#electronic-warfare-factors)
- [How the Model Works — The Technical Version](#how-the-model-works--the-technical-version)
- [Sources and References](#sources-and-references)

---

## WHAT THIS IS AND WHY IT EXISTS

### The Basic Idea

Imagine you have a map of Kharg Island. You place 625 Marine fire teams on ships offshore, 250 IRGC defenders on the island, a dozen Stinger MANPADS teams, 20 MV-22B Ospreys, some MQ-9 drones, and three US ships. You hit play.

Every unit moves, shoots, gets shot at, and either lives or dies — one minute at a time, for two hours of simulated battle. At the end, either the Marines hold the island or they don't.

Now change one thing. Give the Iranians Russian Igla-S MANPADS instead of Stingers. Run it again. See what changed.

That's DAEMON. It runs the battle repeatedly with different conditions and shows you what tips the outcome.

### Why This Matters

Military planners have always fought the last war. DAEMON forces the question forward: given what we know about current Iranian capabilities, under what conditions does a vertical assault on Kharg Island succeed, fail, or become a coin flip?

The answer isn't a single number. It's a threshold. Below 500 IRGC defenders with baseline MANPADS, Marines win under most conditions. Above that threshold — or if the Iranians have Russian SA-25 Verbas — the Osprey losses compound fast enough to deny the landing force before it can gain a foothold. DAEMON finds that threshold and shows you why it's where it is.

### Why Agent-Based, Not Just Math

Lanchester equations (the standard combat math) average everything out. DAEMON doesn't. Each Osprey is an individual aircraft. Each Stinger team fires, reloads, and fires again — or gets killed before reloading. When the 20th Osprey is shot down, there are no more Ospreys. That's a cliff, not a slope. You can't see cliffs in an equation. You can in DAEMON.

---

## TECHNICAL REQUIREMENTS

### Your Computer

| What | Minimum | Recommended |
|---|---|---|
| **Operating System** | Windows 10, macOS 12, or Ubuntu 20.04 | Same — any modern OS works |
| **RAM** | 4 GB | 8 GB or more |
| **CPU** | Any dual-core from the last 10 years | Quad-core or better (runs each scenario faster) |
| **Disk space** | 500 MB free | 2 GB free (stores all 60+ KMZ scenario files) |
| **Internet** | Needed once for installation | Not required to run simulations |

The simulation is pure computation — no GPU required, no gaming PC needed. A standard office laptop handles it fine.

### Software You Need

| Software | Cost | Where to Get It |
|---|---|---|
| **Python 3.11 or newer** | Free | python.org — download the installer for your OS |
| **Git** | Free | git-scm.com — or install via your OS package manager |
| **Google Earth Pro** | Free | earth.google.com/web/about/versions — desktop app, not the browser version |

**Important:** Download Google Earth **Pro** (the desktop app), not the browser version. The browser version does not support animated KMZ files.

### No Other Dependencies

DAEMON uses only Python's built-in standard library. No `pip install numpy`, no conda, no packages to manage. If Python runs, DAEMON runs.

---

## INSTALLATION — STEP BY STEP

### Step 1 — Install Python

Go to **python.org**, click Downloads, grab the installer for your operating system. Run it. When it asks, **check the box that says "Add Python to PATH"** — this is important.

To verify it worked, open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:
```
python --version
```
You should see something like `Python 3.11.8`. If you get an error, Python isn't on your PATH — go back and reinstall with the PATH checkbox checked.

### Step 2 — Install Git

Go to **git-scm.com** and download Git for your OS. Install it with default settings.

### Step 3 — Download DAEMON

Open your terminal and run:
```bash
git clone https://github.com/your-org/daemon
cd daemon
```

### Step 4 — Install DAEMON as a Package

Still in your terminal, inside the `daemon` folder:
```bash
pip install -e .
```

This registers the simulation package so Python can find it. The `-e` means "editable" — changes you make to the code take effect immediately without reinstalling.

**That's it.** No further setup required.

---

## RUNNING THE SIMULATION — STEP BY STEP

### Run All 30 Kharg Island Scenarios

Open a terminal in the `daemon` folder and run:
```bash
python -m persian_gulf_simulation.runner
```

This generates 30 KMZ files, one per scenario. You'll see output like:
```
[01/30] F-35 Strike + Iranian BM Retaliation
Initialising agents ...
  625 Marine fireteams in 104 Osprey flights
  20 MV-22s | cycle 13 steps (13 min)
  250 IRGC | 12 Stingers | 6 Reapers
  50 IRGCN drone boats | 50 Shahed-136 drones
  3 US ships  (SAM Pk=0.4, gun Pk=0.6)
Running simulation ...
=== BATTLE OUTCOME SUMMARY ===
  LAND  — Marines alive    : 411/625 fireteams  (1644 men)
  LAND  — IRGC neutralized : 20/20 squads
  ...
  OUTCOME: USMC secured Kharg Island — fleet intact
Writing output/scenarios/kharg_island_01_f35_retaliation.kmz ...
Done.
```

Each scenario takes roughly 5–15 seconds. All 30 finish in about 5 minutes total.

**Output location:** `daemon/output/scenarios/`

### Run All 30 CSG Naval Scenarios

```bash
python -m persian_gulf_simulation.generate_wargame_kml
```

### Run Everything at Once

```bash
python -m persian_gulf_simulation.runner && python -m persian_gulf_simulation.generate_wargame_kml
```

### Run a Single Custom Scenario

Create a Python script (e.g., `my_scenario.py`) in the `daemon` folder:
```python
from persian_gulf_simulation.runner import _run_scenario, _patch_scenario

# Change these numbers to test different conditions:
with _patch_scenario(
    n_irgc=500,                    # 500 IRGC defenders instead of 250
    stinger_pk=0.35,               # Russian Igla-S MANPADS
    stinger_hover_pk=0.80,
    ew_manpads_pk_mult=0.10,       # DIRCM active on Ospreys (90% defeat)
):
    _run_scenario(
        "output/my_test.kmz",
        scenario_label="My Test — 500 OPFOR with SA-24 and DIRCM",
        iran_retaliation=True,
    )
```
Then run: `python my_scenario.py`

---

## VIEWING THE OUTPUT IN GOOGLE EARTH

### Open a KMZ File

1. Open **Google Earth Pro** (the desktop app)
2. Go to **File → Open**
3. Navigate to `daemon/output/scenarios/`
4. Open any `.kmz` file

The file loads. You'll see the Persian Gulf region with colored markers scattered across Kharg Island and the surrounding water.

### Play the Animation

Look at the bottom of the Google Earth window — there's a **Timeline slider** with a play button.

- **Press Play** to watch the battle animate from H-Hour forward
- **Drag the slider** to jump to a specific time (e.g., drag to the 50-minute mark to see the Iranian SRBM salvo)
- **Scroll the clock speed** up or down to watch faster or slower

### Navigate the Map

- **Scroll to zoom** in and out
- **Click and drag** to pan
- **Right-click drag** to tilt the view into 3D

### Turn Layers On and Off

On the left panel you'll see folders:
- **US Forces** → Marines, Ospreys, ships, drones
- **IRGC / Iranian Forces** → ground troops, MANPADS, missiles, drones
- **Battle Overview** → narration events (text callouts at key moments)

Click the checkbox next to any folder to show or hide it. Start with everything off, then turn on one layer at a time.

### Click on Any Icon

Click any unit icon to open its data card — unit type, HP, kill count, cost, the doctrine reference that set its probability-of-kill number.

### The Timeline in Plain Terms

| Time | What's Happening |
|---|---|
| H+0 (slider at start) | Ospreys launch from USS Tripoli, Marines airborne |
| H+5–15 min | First Marine wave arrives at LZs (FALCON, EAGLE, VIPER, COBRA) |
| H+15–90 min | Ground combat — Marines push inward, IRGC defenders react |
| H+50 min | Iranian SRBM salvo launches (visible as orange/red parabolic arcs) |
| H+55 min | Shahed-136 loitering drones strike Marine positions on island |
| End | Count the survivors. Who holds the island? |

---

## CHANGING VARIABLES — RUNNING CUSTOM SCENARIOS

Every number that matters lives in one file: `persian_gulf_simulation/config.py`. You do not edit that file directly for custom runs — instead you use `_patch_scenario()` as shown above, which overrides values for that run only.

### The Variables You'll Want to Change Most

| Variable | What It Does | Example Value |
|---|---|---|
| `n_irgc` | How many IRGC defenders | 250, 500, 1500, 2000 |
| `stinger_pk` | MANPADS kill probability vs Osprey in transit | 0.25 (Stinger), 0.35 (Igla-S), 0.52 (Verba) |
| `stinger_hover_pk` | MANPADS kill probability vs Osprey hovering at LZ | 0.75 (Stinger), 0.80 (Igla-S), 0.88 (Verba) |
| `ew_manpads_pk_mult` | DIRCM multiplier — 0.10 means 90% of MANPADS shots defeated | 1.0 (no DIRCM), 0.10 (full DIRCM) |
| `ew_irgc_pk_mult` | COMJAM effect on IRGC fire effectiveness | 1.0 (no jam), 0.50 (heavy jamming) |
| `ew_mildec_fraction` | Fraction of IRGC misdirected by deception operation | 0.0 (no MILDEC), 0.30 (30% misdirected) |
| `n_drone_boats` | IRGCN drone boats attacking the fleet | 0–50 |
| `n_shahed` | Shahed-136 drones targeting ships | 0–50 |
| `iran_retaliation` | Include SRBM salvo + island Shahed strike | True / False |

---

## WHAT THE COLORS MEAN

| Color | Force | Unit |
|---|---|---|
| Coyote brown | USMC | Marine fire teams |
| Coyote brown | USMC | MV-22B Ospreys |
| Bright yellow | US | MQ-9 Reaper drones |
| Navy blue | US | Ships (green→orange→red as HP drops) |
| Red | IRGC | Ground defenders |
| Red | IRGC | MANPADS teams |
| Red | IRGCN | Drone boats |
| Red / dark red | IRGC | Shahed-136 drones targeting ships |
| Orange-yellow | IRGC | Shahed-136 drones targeting island |
| Deep orange-red | Iran | Fateh-313 SRBM (parabolic arc, apogee 75 km) |
| Orange | Iran | Zolfaghar SRBM (parabolic arc, apogee 130 km) |
| Grey (faded) | Any | Dead units |
| Cyan circles | US | Landing Zone (LZ) hover zones |

HP degradation: full-color icon = full strength. As a unit takes hits, its icon fades toward grey. At 0 HP it goes fully grey with a cross-hairs or fall animation.

---

## SCENARIO SUITE — KHARG ISLAND ASSAULT

30 KMZ files. Ground simulation: Lanchester Square Law attrition, FIM-92 Stinger MANPADS, MV-22B Osprey assault sorties, Iranian SRBM and OWA-UAS retaliation in every scenario.

The operation models a USMC MAGTF heliborne vertical assault against IRGC Ground Forces defending Kharg Island. 625 fire teams (2,500 men) in 104 Osprey flights across 6 assault waves.

### Scenario Rankings by Likelihood

| Rank | Scenario | Rationale |
|---|---|---|
| 1 | **F-35 Strike + Iranian BM Retaliation** | Most complete doctrinal scenario. US pre-strikes before any contested landing; Iran retaliates with SRBMs (historical precedent: Op Martyr Soleimani 2020, Op True Promise 2024). |
| 2 | **Contested EMS — 250 OPFOR** | Bilateral EW is baseline modern combat. Iran runs GPS jammers and ECM routinely; US deploys DIRCM and COMJAM as standard package. |
| 3 | **F-35 Strike GPS Jammed (22% survive)** | Iran demonstrated persistent GPS jamming in Gulf ops. JDAM CEP degradation under jamming is documented. |
| 4 | **Baseline — FIM-92 Stinger (250 OPFOR)** | Intelligence baseline. Kharg Island peacetime garrison ~200–300 IRGC; FIM-92 clones confirmed in IRGC inventory. |
| 5 | **Russian Igla-S SA-24 — 250 OPFOR** | Iran has documented Igla-S acquisition; dual IR/UV seeker confirmed in IRGC MANPADS battalions (IISS 2024). |
| 6 | **F-35 Lightning Strike — 8% IRGC survive** | Standard pre-H-Hour SEAD/DEAD is doctrinal for any opposed MAGTF assault (JP 3-02). |
| 7 | **US EW Dominance — 250 OPFOR** | US brings DIRCM + COMJAM; full dominance achievable at 250 OPFOR. |
| 8 | **FIM-92 Stinger — 500 OPFOR** | Crisis reinforcement to 500 is realistic; Kharg Island garrison infrastructure supports one reinforced battalion. |
| 9 | **DIRCM-Suppressed MANPADS — 250 OPFOR** | AN/AAQ-24 DIRCM is standard on USMC assault support aircraft. Single-variable DIRCM test. |
| 10 | **Contested EMS — 1,500 OPFOR** | Reinforced garrison with bilateral EW — realistic if Iran has 72+ hr warning. |
| 11–30 | Additional MANPADS systems, OPFOR sizes, EW combinations | See complexity ranking below |

### Scenario Rankings by Complexity

| Rank | Scenario | Active Subsystems |
|---|---|---|
| 1 | **F-35 Strike + Iranian BM Retaliation** | 3 phases; 100 SRBMs in 10 staggered waves from 3 launch sites; 100 island Shahed; ship SAM chain; IRGCN boats; Lanchester ground battle |
| 2 | **Contested EMS — 1,500 OPFOR** | 6 simultaneous EW variables; 1,500 OPFOR Lanchester; all maritime threats; OWA-UAS + SRBM retaliation |
| 3 | **Contested EMS — 250 OPFOR** | Same 6 EW variables; baseline OPFOR |
| 4–30 | Descending combinations | Fewer modified variables, smaller OPFOR counts |

### Baseline Force Sizes

| Scenario | OPFOR (IRGC) | MANPADS Teams | Typical Outcome |
|---|---|---|---|
| Baseline | 250 | 12 | Contested |
| OPFOR 500 | 500 | 25 | IRGC repels assault |
| OPFOR 1,500 | 1,500 | 75 | IRGC repels assault |
| OPFOR 2,000 | 2,000 | 100 | IRGC repels assault |
| Permissive JAAT | 250 | 0 | USMC secures objective |
| Extended Loiter (60s) | 250 | 12 | USMC secures objective |

### MANPADS System Comparison

| System | Origin | Pk Transit | Pk Hover (LZ) | Typical Outcome (250 OPFOR) |
|---|---|---|---|---|
| FIM-92 Stinger | US-origin | 0.25 | 0.75 | Contested |
| 9K338 Igla-S (SA-24) | Russia — dual IR/UV seeker | 0.35 | 0.85 | Heavy Osprey losses |
| 9K333 Verba (SA-25) | Russia — 3-channel, ECCM-resistant | 0.40 | 0.90 | Assault repelled |
| QW-2 | China — IIR seeker | 0.30 | 0.80 | Contested |
| FN-6 (HY-6) | China — passive IR + rosette | 0.28 | 0.78 | Contested |
| DIRCM-Suppressed | AN/AAQ-24 defeats 90% | 0.025 | 0.075 | USMC secures objective |

### Iranian Retaliation — Present in All 30 Scenarios

Every Kharg Island scenario includes an Iranian SRBM and OWA-UAS retaliation after the Marines land:

| Wave | Time | System | Launch Sites |
|---|---|---|---|
| SRBM Salvo | H+50 min | 100 SRBMs, 10 waves of 10 | Shiraz MB (40%), Bushehr AB (20%), Bandar Abbas (40%) |
| OWA-UAS Strike | H+55 min | 100 Shahed-136 | Eastern Iran coastal sites |

| Color on Map | KML Code | Missile | Apogee | Site |
|---|---|---|---|---|
| Deep orange-red | `cc0055ff` | Fateh-313 SRBM | 75 km | Shiraz + Bushehr |
| Orange | `cc0066ff` | Zolfaghar SRBM | 130 km | Bandar Abbas |

---

## SCENARIO SUITE — CSG NAVAL ENGAGEMENT

30 KMZ files. Naval engagement simulation: full 8-carrier strike group (CSG) Combined Naval Force vs Iranian missile, drone, and USV salvo. Tests Aegis magazine depletion, CIWS exhaustion, and cost exchange ratios.

### Primary Scenarios

| Scenario | SRBMs/MRBMs | OWA-UAS | USV Swarm | Total | Intercept % | Leakers | Outcome |
|---|---|---|---|---|---|---|---|
| **A — Low Capability** | 265 | 665 | 135 | 1,065 | ~69% | ~335 | CSG survives; degraded |
| **B — Medium Capability** | 665 | 1,335 | 200 | 2,200 | ~65% | ~793 | Multiple CVN/DDG impacts |
| **D — Realistic** | 1,100 | ~5,000 | ~990 | 7,250 | 58% | ~820 | Non-permissive |
| **C — High / IPDS CAP HIT** | 1,100 | 2,665 | 265 | 4,030 | ~66% | ~1,370 | Multiple CVN mission kills |
| **E — Iran Best Case** | 1,000 | 4,000 | 400 | 5,400 | 37% | **3,419** | Catastrophic fleet loss |
| **F — US Best Case** | 200 | — | — | 200 | ~81% | ~38 | Fleet combat-effective |

### UAS-Saturation Doctrine Scenarios

| Scenario | Phase 1 (T+0) | Phase 2 (T+30) | Effect |
|---|---|---|---|
| **G — UAS-Saturation Low** | 665 OWA-UAS | 265 SRBMs | CIWS partially depleted before SRBMs arrive |
| **H — UAS-Saturation Medium** | 1,335 OWA-UAS | 665 SRBMs | CIWS Winchester by T+45; SRBM salvo uncontested by close-in defense |
| **I — UAS-Saturation High** | 2,665 OWA-UAS | 1,100 SRBMs | Full CIWS/RAM depletion; Aegis IPDS overwhelmed |

### Depleted Arsenal Scenarios (Post-Strike — 8% Inventory)

| Scenario | Arsenal | P(US Win) |
|---|---|---|
| **R — US Wins: Preemption** | 15% survives H-Hour strike | ~94% |
| **S — US Wins: EW Dominance** | 450 ballistic, guidance denied | ~88% |
| **T — US Wins: Allied IAMD Umbrella** | 550 full coastal salvo | ~83% |
| **U — C2 Disrupted** | 900, fragmented | ~71% |
| **V — Arsenal Attrited** | 750, legacy lethality | ~65% |

---

## WEAPON COSTS AND EXCHANGE RATIOS

> All costs are unclassified open-source estimates.

### Iranian Offensive Munitions

| Tier | System | Unit Cost | Range | CEP | Source |
|---|---|---|---|---|---|
| Low | **Shahed-136** OWA-UAS | **$35,000** | 2,000 km | 30 m | CSIS Feb 2025 |
| Low | **Shahed-238** jet-powered OWA-UAS | **$100,000** | 1,800 km | 20 m | ISIS 2025 |
| Mid | **IRGCN FIAC/USV** (sea drone) | **$100,000** | 300 km | 3 m | IRGCN estimates |
| Mid | **Fateh-313 SRBM** (GPS/INS) | **$800,000** | 500 km | 30 m | IISS |
| Mid | **Shahab-3 MRBM** (legacy) | **$800,000** | 1,300 km | 500 m | CSIS/IISS |
| High | **Zolfaghar SRBM** (precision) | **$1,000,000** | 700 km | 10 m | IISS |
| High | **Emad MRBM** (maneuvering reentry) | **$2,000,000** | 1,700 km | 30 m | IISS |
| Very High | **Fattah-1 HGV** (hypersonic, Mach 13+) | **$3,000,000** | 1,400 km | 100 m | CSIS |
| Very High | **Fattah-2 HGV** (pitch/yaw correction) | **$4,000,000** | 1,400 km | 75 m | Hudson Institute 2026 |

### US/Israeli Strike Munitions

| Tier | System | Unit Cost | Platform | Source |
|---|---|---|---|---|
| Low | **JDAM-ER** (GBU-38/32 + ER wing) | **$30,000** | F-35B/I | FY2023 DoD contract |
| Mid | **JASSM-ER** (AGM-158B, stealthy ALCM) | **$1,400,000** | B-2, F-15E, F-35 | FY2023 contract |
| Mid | **AIM-120C-8 AMRAAM** (BVR AAM) | **$1,800,000** | F/A-18E/F, F-35 | FMS unit cost |
| High | **TLAM Block IV** (land attack CM) | **$2,000,000** | DDG/CG/SSN VLS | DoD FY2023 |

---

## INTERCEPT SYSTEM COSTS

| Tier | System | Cost per Engagement | Inventory per DDG-51 Flt III | Source |
|---|---|---|---|---|
| Low | **Phalanx CIWS Mk 15** (20mm) | **$50,000** | 1,550-round magazine | DoD procurement |
| Low | **Mk 45 5-inch Naval Gun** | **$50,000** | ~600 rounds | DoD |
| Mid | **SeaRAM / Mk 49 RAM Block 2** | **$800,000** | 21 rounds per launcher | DoD |
| Mid | **ESSM Block 2** (quad-packed VLS) | **$1,500,000** | ~32 per DDG-51 Flt III | FY2024 contract |
| High | **SM-2 Block IIIB** | **$2,100,000** | 20–44 per DDG | NAVSEA |
| High | **SM-6 Block IA** | **$4,500,000** | 10–18 per DDG-51 Flt III | CBO FY2025 |
| Very High | **SM-3 Block IA** (Aegis BMD) | **$9,574,000** | Limited (BMD ships only) | DoD SAR Dec 2023 |

### The Exchange Ratio Problem

Iran fires a $35,000 drone. The US responds with a $4,500,000 missile. That is a 129:1 cost ratio in Iran's favor. Scenarios consistently show **total US cost (intercepts + hull damage) running 80–300× Iran's offensive expenditure**. This asymmetry is the economic logic behind the UAS-saturation doctrine: flood Aegis with cheap drones, drain the VLS magazine, then send in the ballistic missiles.

| Matchup | Iran Spends | US Spends | Ratio |
|---|---|---|---|
| Shahed-136 vs SM-6 | $35,000 | $4,500,000 | **129:1** unfavorable to US |
| Fateh-313 SRBM vs SM-6 | $800,000 | $4,500,000 | **5.6:1** unfavorable to US |
| Emad MRBM vs SM-3 Block IA | $2,000,000 | $9,574,000 | **4.8:1** unfavorable to US |
| Fattah-1 HGV vs SM-3 Block IA | $3,000,000 | $9,574,000 | **3.2:1** unfavorable to US |

---

## FLEET COMPOSITION AND VALUE AT RISK

### 8-CSG Combined Naval Force

| Risk | Hull | Cost | VLS Cells | SM-6 Load | Ship's Company |
|---|---|---|---|---|---|
| CRITICAL | **CVN-72 USS Abraham Lincoln** (Nimitz-class) | $9.0B hull + $4.0B air wing | — | — | ~5,000 |
| CRITICAL | **CVN-78 USS Gerald R. Ford** (Ford-class) | $13.3B hull + $4.0B air wing | — | — | ~5,000 |
| HIGH | **DDG-51 Flight III** Arleigh Burke | ~$2.2B | 96 VLS | 10–18 | ~330 |
| HIGH | **CG-47 Ticonderoga** cruiser | ~$1.1B | 122 VLS | 12 | ~400 |

| Metric | Value |
|---|---|
| **Total force value** (hulls + air wings, 8 CSGs) | **~$169.6 billion** |
| **Personnel at risk** | **~68,000** |
| **Total SM-6 rounds** (8 CSGs × ~12 avg per DDG/CG) | **~480 rounds** |
| **Simultaneous engagement capacity** (8 CSGs × 18 IPDS tracks) | **~144 tracks** |

---

## COMBAT MODEL PARAMETERS

### Lanchester Square Law — Ground Combat

Lanchester's Square Law says combat power scales as N² × Q (force size squared times quality multiplier). This is why 500 IRGC doesn't just feel twice as hard as 250 — it is four times as powerful, because combat effectiveness grows with the square of numbers. Add terrain multipliers and it compounds further.

| Parameter | Value | What It Means |
|---|---|---|
| **LANCHESTER_Q** | **1.6** | One Marine fire team fights as effectively as 1.6 IRGC squads — derived from historical CEV data, not guessed |
| **IRGC_PK** | **0.07** | Probability an IRGC squad kills 1 Marine HP per 60-second step |
| **MARINE_PK** | **0.112** | = IRGC_PK × 1.6 — automatically derived from quality factor |
| **IRGC_DEFENSE_MULT** | **2.5** | Defenders in prepared positions are 2.5× more effective (Dupuy terrain multiplier) |
| **IRGC_HOME_RADIUS_KM** | **0.9 km** | Defenders only get this bonus within 900m of their assigned position — dislodge them and the multiplier drops |
| **ENGAGE_KM** | **0.30 km** | Units must be within 300m to exchange fire |
| **STEP_S** | **60 s** | One simulation tick = one real minute |

### Historical CEV Calibration

The Q=1.6 quality multiplier is derived from historical data, not invented:

| Conflict | CEV | Notes |
|---|---|---|
| IDF vs Egyptian Army, 1967 | 1.75 | Professional vs Soviet-doctrine conscript — closest structural analog |
| IDF vs Egyptian Army, 1973 | 1.98 | Better-trained Egyptians post-1967 |
| USMC vs NVA, Hue City, 1968 | ~1.3 | Urban/prepared defense — lower bound |
| USMC vs IJA, Iwo Jima, 1945 | ~1.5–1.8 | Fortified island vertical assault — direct analog |
| **DAEMON (USMC vs IRGC)** | **1.6** | Adjusted down from IDF/Egypt for IRGC ideological cohesion and proxy-war experience |

Source: Trevor Dupuy, *Numbers, Predictions and War* (1979); Dupuy Institute CEV studies.

---

## ELECTRONIC WARFARE FACTORS

All EW effects default to off (multiplier = 1.0). Scenario overrides apply values from unclassified Joint Publication doctrine.

| EW Capability | Parameter | Off | Active | Basis |
|---|---|---|---|---|
| **COMJAM** — jamming IRGC radio nets | `EW_IRGC_PK_MULT` | 1.0 | 0.50 | JP 3-13.1: sustained COMJAM cuts C2 effectiveness 40–60% |
| **COMJAM** — disrupting defensive coordination | `EW_IRGC_DEFENSE_MULT_ADJ` | 1.0 | 0.50 | JP 3-13.1 |
| **DIRCM** — laser jammer on MV-22Bs | `EW_MANPADS_PK_MULT` | 1.0 | 0.10 | AN/AAQ-24 DIRCM: 85–95% MANPADS defeat; JP 3-13.1 |
| **MILDEC** — deception to false LZ | `EW_MILDEC_FRACTION` | 0.0 | 0.30 | 30% OPFOR misdirected ~20 min; JP 3-13 |
| **GPS Denial** — Shahed guidance spoofed | `EW_SHAHED_ABORT_RATE` | 0.0 | 0.30 | JP 3-85: GPS denial → 30% drone abort |
| **Iranian ECM** — jamming US ship radars | `EW_SHIP_SAM_PK_MULT` | 1.0 | 0.70 | JP 3-85: contested EMS reduces SAM Pk ~30% |

---

## HOW THE MODEL WORKS — THE TECHNICAL VERSION

### Architecture

```
daemon/
├── persian_gulf_simulation/
│   ├── config.py              # All constants — the only file you edit for scenarios
│   ├── geography.py           # Kharg Island polygon, grid geometry
│   ├── agents/
│   │   ├── base.py            # Agent class (position, HP, track)
│   │   └── factory.py         # Creates all unit types at simulation start
│   ├── simulation/
│   │   └── engine.py          # The main loop — 120 steps × 60 seconds
│   ├── kml/
│   │   ├── document.py        # Assembles the final KMZ
│   │   ├── placemarks.py      # Converts agent tracks to Google Earth animations
│   │   ├── styles.py          # Colors and icons for each unit type
│   │   ├── descriptions.py    # The data cards that pop up when you click a unit
│   │   ├── narration.py       # Text callouts at key battle events
│   │   └── tour.py            # Google Earth fly-through camera tour
│   └── runner.py              # Scenario definitions and the main() entry point
└── generate_wargame_kml.py    # CSG naval scenarios (separate module)
```

### The Simulation Loop

Every 60-second step:
1. **Record** — every agent writes its current position and HP to its track
2. **Move** — agents move toward their target (Ospreys toward LZs, IRGC toward Marines, missiles toward ships)
3. **Engage** — units in range exchange fire using probability-of-kill rolls
4. **Kill** — agents at 0 HP are marked dead and stop moving

After 120 steps (2 simulated hours), the loop ends. The recorded tracks become the animated paths in Google Earth.

### Phase Changes — Where Outcomes Flip

The model is designed to find "cliffs" — conditions where a small change in input produces a large change in outcome. Four recurring cliffs:

**1. VLS Depletion.** Each DDG has a finite number of SM-6 missiles. When the last one fires, the ship is undefended against ballistic threats. In Scenario E (Iran Best Case), Aegis magazines run dry at ~T+60 min. Leaker count jumps 4× compared to Scenario D despite only a 15% increase in salvo size.

**2. Aegis Engagement Capacity.** The AN/SPY-1D(V) radar system can track ~18 targets simultaneously per CSG. Eight CSGs = 144 simultaneous tracks. When Iran launches faster than the 30-second engagement window clears, additional missiles are not engaged — they go straight through.

**3. IRGC Force-Size Threshold.** Below 500 IRGC defenders, Marines win under most conditions. Above 500, the N² Lanchester effect compounds fast enough that IRGC attrition outpaces Marine reinforcement through the Osprey sortie cycle.

**4. IRGC Positional Advantage.** IRGC squads in prepared positions (within 900m of their cluster) fight at 2.5× effectiveness. Dislodged into open terrain, they fight at 1.0× (a 60% drop). The simulation models this transition explicitly — which is why early fire support to disrupt defensive positions matters before Marines land.

### Conceptual Background

DAEMON is built on agent-based modeling (ABM). Rather than describing the battle as a set of equations (as Lanchester differential equations do), it places individual agents on a map and lets behavior emerge from interactions between them.

The analogy is a forest fire. A fire doesn't spread uniformly — it spreads through local interactions between adjacent trees. No central planner. The outcome (how far the fire spreads) emerges from millions of individual ignition decisions made by individual trees.

DAEMON applies this to combat: each agent makes discrete decisions (fire, move, die) at each step. Macro-outcomes (who holds the island) emerge from those interactions. The advantage over equations: you see the moment the 20th Osprey is shot down, or the moment CIWS runs out of rounds, or the moment the last IRGC squad is dislodged from its position. Equations smooth those moments out. ABM preserves them.

---

## SOURCES AND REFERENCES

### Doctrine

| Source | Used For |
|---|---|
| JP 3-13 *Information Operations* | IO/MILDEC factor derivation |
| JP 3-13.1 *Electronic Warfare* | COMJAM, DIRCM effectiveness values |
| JP 3-85 *Joint Electromagnetic Spectrum Operations* | GPS denial, SAM Pk degradation |
| JP 3-09 *Joint Fire Support* | EW/fires integration |
| JP 3-02 *Amphibious Operations* | MAGTF assault doctrine, LZ procedures |
| JP 3-30 *Command and Control of Joint Air Operations* | UAS sequencing doctrine |
| Trevor Dupuy, *Numbers, Predictions and War* (1979) | Lanchester Q / CEV calibration |
| RAND *Multilayer BMD* | SM-6/SM-3 single-shot Pk estimates |
| CSBA *Salvo Competition* (2015) | VLS magazine saturation analysis |
| DOT&E FY2018, FY2022 Annual Reports | Aegis intercept effectiveness |
| NAVSEA Aegis BMD 6.3 brief | IPDS simultaneous engagement capacity |
| CNA *Electronic Warfare in Modern Conflict* (2019) | EW degradation factor validation |

### Intelligence and Inventory Estimates

| Source | Used For |
|---|---|
| IISS *Military Balance 2024* | Iranian missile inventories, fleet composition |
| CSIS Missile Threat database | Missile specs, CEP, range |
| Jane's Defence Weekly 2024 | Unit costs, aircraft loadouts |
| Alma Research, Feb 2026 | Iran reconstituted SRBM stockpile (~2,500 post-2025) |
| CENTCOM Gen. McKenzie testimony, 2022 | Iranian ballistic missile threat |
| FDD (Foundation for Defense of Democracies), Feb 2026 | Fattah-2 HGV operational status |
| JINSA *Shielded by Fire* (Aug 2025) | SM-6 Pk, intercept cost |
| FPRI *Shallow Ramparts* (Oct 2025) | Layered IAMD effectiveness |
| Red Sea / OOD Prosperity Guardian data (2023–2025) | Real-world Shahed-136 cost and intercept validation |

### Procurement and Cost Data

| Source | Used For |
|---|---|
| DoD FY2023 Lot 25 contract (BGM-109) | TLAM Block IV unit cost $2.0M |
| FY2023 multiyear contract (AGM-158B) | JASSM-ER unit cost $1.4M |
| DoD Selected Acquisition Report, Dec 2023 | SM-3 Block IA unit cost $9.574M |
| CBO blended FY2025 estimate | SM-6 flyaway cost $4.5M |
| CSIS Feb 2025 | Shahed-136 OWA-UAS median $35,000 |
| NAVAIR MV-22B Osprey fact sheet | Assault support performance data |
| USMC MAGTF Handbook 2025 | Marine fire team assault doctrine |
| USNI News, NAVSEA public briefs | DDG/CG VLS magazine loadouts |

---

## LICENSE

Research and educational use. All weapon specifications and cost estimates are derived from unclassified open-source materials. No classified information was used or referenced.

---

*If you can see it on Google Earth, you can fight for it here.*
