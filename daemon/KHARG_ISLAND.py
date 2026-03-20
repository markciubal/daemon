"""
python -m daemon.KHARG_ISLAND

Runs all 30 Kharg Island assault scenarios and writes KMZ files to
output/scenarios/.  Each scenario takes ~5-15 seconds; total ~5 minutes.

Optional argument: a scenario filter (substring of the filename stem).

    python -m daemon.KHARG_ISLAND              # all 30 scenarios
    python -m daemon.KHARG_ISLAND f35          # only F-35 scenarios
    python -m daemon.KHARG_ISLAND baseline     # only the baseline scenario
    python -m daemon.KHARG_ISLAND igla_s       # only Igla-S MANPADS scenarios
"""

import os
import sys

from persian_gulf_simulation.runner import build_scenarios, run_scenario_entry


def main():
    query = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    scenarios_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "output", "scenarios"
    )
    os.makedirs(scenarios_dir, exist_ok=True)

    all_scenarios = build_scenarios()
    matched = [
        s for s in all_scenarios
        if query in ("all",) or query in s[2].lower()
    ]

    if not matched:
        print(f"[daemon.KHARG_ISLAND] No scenarios matched '{query}'.")
        print("Available scenarios:")
        for _, _, fname, _ in all_scenarios:
            print(f"  {fname.replace('.kmz', '')}")
        sys.exit(1)

    print(f"[daemon.KHARG_ISLAND] Running {len(matched)} scenario(s) → {scenarios_dir}\n")
    for entry in matched:
        run_scenario_entry(*entry, scenarios_dir=scenarios_dir)
    print(f"\n[daemon.KHARG_ISLAND] Done. {len(matched)} KMZ file(s) written to {scenarios_dir}")


if __name__ == "__main__":
    main()
