"""
daemon.py — CLI entry point for running Kharg Island scenarios by name.

Usage
-----
  python daemon.py -scenario kharg_island          # all 30 kharg scenarios
  python daemon.py -scenario kharg_01              # scenario #01 only
  python daemon.py -scenario f35                   # any scenario whose filename contains 'f35'
  python daemon.py -scenario baseline              # any scenario whose filename contains 'baseline'
  python daemon.py -scenario all                   # same as kharg_island — run everything
  python daemon.py -list                           # print available scenarios and exit
  python daemon.py -list -scenario f35             # print only f35 scenarios

Matching is substring-based on the scenario filename stem (case-insensitive).
'all' and 'kharg_island' both match every scenario in the suite.
"""

import argparse
import os
import sys

# Ensure the repo root is on the path when invoked as `python daemon.py`
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

from persian_gulf_simulation.runner import build_scenarios, run_scenario_entry


def _scenarios_dir():
    return os.path.join(_here, "output", "scenarios")


def _match(fname: str, query: str) -> bool:
    """True if query appears in the filename stem (case-insensitive), or query is 'all'."""
    stem = fname.replace(".kmz", "")
    q    = query.lower().strip()
    return q in ("all", "kharg_island") or q in stem.lower()


def main():
    parser = argparse.ArgumentParser(
        prog="daemon.py",
        description="Run Kharg Island wargame scenarios and produce KMZ/HTML output.",
    )
    parser.add_argument(
        "-scenario",
        metavar="NAME",
        default=None,
        help=(
            "Scenario filter: substring of the filename stem, e.g. 'kharg_01', 'f35', "
            "'baseline', 'igla_s', 'ew_dominance'. "
            "Use 'all' or 'kharg_island' to run every scenario."
        ),
    )
    parser.add_argument(
        "-list",
        action="store_true",
        help="List matching scenarios and exit without running anything.",
    )
    args = parser.parse_args()

    scenarios = build_scenarios()

    # Default: run all if neither flag given (mirrors old python -m persian_gulf_simulation.runner)
    query = args.scenario if args.scenario else "all"

    matched = [(label, overrides, fname, desc)
               for label, overrides, fname, desc in scenarios
               if _match(fname, query)]

    if not matched:
        print(f"[daemon] No scenarios matched '{query}'.")
        print("[daemon] Available scenarios:")
        for _, _, fname, _ in scenarios:
            print(f"  {fname.replace('.kmz', '')}")
        sys.exit(1)

    if args.list:
        print(f"[daemon] {len(matched)} scenario(s) matching '{query}':\n")
        for i, (label, _, fname, desc) in enumerate(matched, 1):
            print(f"  {i:>2}. {label}")
            print(f"      file : {fname}")
            print(f"      desc : {desc[:100]}{'...' if len(desc) > 100 else ''}")
            print()
        sys.exit(0)

    sdir = _scenarios_dir()
    os.makedirs(sdir, exist_ok=True)

    print(f"[daemon] Running {len(matched)} scenario(s) matching '{query}' → {sdir}\n")
    for entry in matched:
        run_scenario_entry(*entry, scenarios_dir=sdir)

    print(f"\n[daemon] Done. {len(matched)} scenario(s) written to {sdir}")


if __name__ == "__main__":
    main()
