# DAEMON
### *Dynamic Agent-based Engagement Model for Naval Operations*

---

**DAEMON simulates a US Marine assault on Kharg Island and an Iranian naval missile strike on a carrier strike group. Run it on your laptop. Open the output in Google Earth. Watch the battle animate.**

Each scenario takes 5–15 seconds to compute. Output is a KMZ file — every aircraft, ship, Marine fire team, drone, and missile moves across a live map of the Persian Gulf in real time.

---

## REQUIREMENTS

**Computer:** Any laptop from the last 10 years. 4 GB RAM minimum. No GPU needed.

**Software (all free):**
- Python 3.11+ — [python.org](https://python.org)
- Git — [git-scm.com](https://git-scm.com)
- Google Earth **Pro** (desktop app, not browser) — [earth.google.com](https://earth.google.com/web/about/versions)

---

## INSTALL

```bash
git clone https://github.com/markciubal/daemon.git
cd daemon
pip install -e .
```

Done.

---

## RUN

```bash
# All 30 Kharg Island scenarios (~5 min)
python -m daemon.KHARG_ISLAND

# All 30 CSG naval scenarios (~5 min)
python -m daemon.CSG_SIM

# Everything (60 scenarios, ~10 min)
python -m daemon.ALL

# Filter to one type
python -m daemon.KHARG_ISLAND f35
python -m daemon.KHARG_ISLAND baseline
```

Output goes to `output/scenarios/`.

---

## VIEW

1. Open **Google Earth Pro**
2. **File → Open** → pick any `.kmz` from `output/scenarios/`
3. In the layers side menu, double click on the generated "Battle Tour" and adjust the timeline with the slider at the bottom left once it starts playing.
4. Click any unit for its data card

Left panel folders toggle layers on/off. Start with everything off, enable one group at a time.

---

## WHAT THE COLORS MEAN

| Color | Unit |
|---|---|
| Coyote brown | USMC Marines / MV-22B Ospreys |
| Bright yellow | MQ-9 Reaper drones |
| Blue → orange → red | US Ships (degrades with HP) |
| Red | IRGC infantry / MANPADS / drone boats |
| Yellow diamond | Shahed-136 drones (all types) |
| Deep orange arc | Iranian SRBM (Fateh-313 / Zolfaghar) |
| Grey + crosshairs | Dead / destroyed |

---

## CHANGE VARIABLES

All constants live in `persian_gulf_simulation/config.py`. To test a custom scenario without editing that file:

```python
from persian_gulf_simulation.runner import _run_scenario, _patch_scenario

with _patch_scenario(
    n_irgc=500,
    stinger_pk=0.35,           # Russian Igla-S
    stinger_hover_pk=0.80,
    ew_manpads_pk_mult=0.10,   # DIRCM active (90% defeat)
):
    _run_scenario("output/my_test.kmz", scenario_label="My Test")
```

Key variables:

| Variable | Effect |
|---|---|
| `n_irgc` | IRGC defenders (250 / 500 / 1500 / 2000) |
| `stinger_pk` | MANPADS Pk in transit (0.25 Stinger → 0.52 Verba) |
| `stinger_hover_pk` | MANPADS Pk at LZ (0.75 → 0.88) |
| `ew_manpads_pk_mult` | DIRCM multiplier (1.0 = none, 0.10 = full DIRCM) |
| `ew_irgc_pk_mult` | COMJAM on IRGC fire effectiveness |
| `iran_retaliation` | Enable SRBM salvo + island Shahed strike |
| `ai_drone_fraction` | Fraction of Shahed with AI guidance (floor: 2.5%) |

---

## BUILT TO BE MODIFIED BY AI

Load this project in VS Code with Claude Code, Copilot, or Cursor. Tell the AI what you want in plain English. It will read the code, find the right file, and make the change.

Examples:
- *"Add a CH-53E Super Stallion with higher capacity but lower speed"*
- *"Create a scenario using Fattah-1 hypersonic missiles"*
- *"Make Ospreys fly in pairs — if one is shot down the other turns back"*
- *"Add a scenario where Iranian mini-submarines attack the fleet"*

You do not need to know how to program. Every file has a clear description at the top. The AI can read the whole codebase in one pass.

---

---

## THE STORY

### Why Kharg Island

Kharg Island handles 90% of Iran's oil exports. Seizing or destroying it ends the Iranian economy in weeks. That makes it simultaneously the most valuable target in a conflict and the most defended. Any US military action against Iran eventually comes back to the same question: what does it cost to take Kharg?

### What the Simulation Shows

At 250 IRGC defenders with baseline FIM-92 Stinger MANPADS, the outcome is contested. Marines take the island but at significant Osprey loss. At 500 IRGC, the assault fails. That threshold — somewhere between 250 and 500 defenders — is where the vertical assault doctrine breaks down.

It breaks down for a specific reason: Osprey losses compound. Each aircraft shot down carries 24 Marines who never reach the beach. By the time you've lost eight Ospreys, you've lost 192 men still airborne. The unit that was supposed to hold the northern cluster never landed. The northern cluster never falls. The southern cluster can't hold alone. The math cascades.

Russian MANPADS accelerate this. The Verba SA-25 (Pk 0.52 in transit, 0.88 at hover) doesn't just increase losses linearly — it pushes the first Osprey kill forward in time, which cascades the rest of the engagement. Scenarios with Verba at 250 OPFOR look worse than scenarios with baseline Stinger at 500 OPFOR.

Electronic warfare cuts both ways. Full DIRCM (AN/AAQ-24) knocks MANPADS effectiveness down by 90% and flips most scenarios to US wins. But Iran's GPS jammers degrade JDAM accuracy on any pre-assault F-35 strike, meaning the OPFOR strength entering H-Hour is higher than planned. The F-35 + GPS jamming scenario captures this: the air strike happens, but only 22% of aimed munitions land within lethal radius.

### The CSG Scenarios

The naval scenarios are about magazines. The US Navy defends with SM-6 ($4.5M per round) against Shahed-136 drones ($35,000 each). Every Shahed that forces a SM-6 launch costs Iran $35,000 and costs the US $4,500,000. That is a 129:1 cost exchange in Iran's favor before accounting for any missile that gets through.

The UAS-saturation doctrine makes this explicit: send cheap drones first to drain CIWS and RAM magazines, then send the SRBMs when the close-in defense is Winchester. Scenarios G, H, and I model this in sequence. By Scenario I (2,665 drones followed by 1,100 SRBMs), Aegis is overwhelmed and multiple carriers take mission-kill hits.

The fleet's total value at risk in a full CSG engagement is approximately $170 billion in hulls and air wings, defended by roughly 480 SM-6 rounds spread across all ships. Iran needs to get through with fewer than 480 missiles total to exhaust the magazine. In Scenario E (Iran Best Case), they launch 5,400 systems. The intercept rate is 37%. 3,419 leakers reach their targets.

### The AI Drone Factor

2.5% of every Shahed swarm is now modeled as AI-guided. These drones use computer-vision targeting to track specific ship compartments and infantry concentrations, reducing their intercept probability to 30% of normal SAM effectiveness and doubling their lethality on impact. This floor reflects assessed IRGC fielding as of 2024.

The number sounds small. In a 5,000-drone swarm, that is 125 drones that are nearly impossible to shoot down and twice as lethal when they hit.

### The Bottom Line

Below 500 IRGC with baseline MANPADS and no EW: the Marines can take the island, at cost.

Above that threshold, or with Russian MANPADS, or with Iranian EW active and DIRCM absent: the assault fails before a foothold is established.

At sea: the exchange ratio has always favored Iran. The question is whether Iran can mass enough simultaneous launches to exhaust US magazine depth before US strike packages destroy enough launch infrastructure. Scenarios D through E suggest that answer is yes, under current assessed inventories.

None of this predicts what will happen. It maps the terrain around what is possible and shows you where the cliffs are.

---

## SOURCES

- RAND *Countering AI-enabled UAS* (2023)
- CNAS *AI Autonomy in Drone Swarms* (2024)
- IISS *The Military Balance* (2024)
- CSIS Missile Defense Project — missile cost and CEP data
- JP 3-02 *Amphibious Operations* (2019)
- Dupuy Institute — combat effectiveness values
- DoD FY2023/2025 budget exhibits — intercept system unit costs
