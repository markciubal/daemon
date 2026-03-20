"""
python -m daemon.ALL

Runs all 60 scenarios — 30 Kharg Island assault + 30 CSG naval engagement —
and writes KMZ files to output/scenarios/.

Total runtime: ~10 minutes on a modern laptop.
"""

import sys

from persian_gulf_simulation.runner import main as _kharg_main
from persian_gulf_simulation.generate_wargame_kml import main as _csg_main


def main():
    print("=" * 60)
    print("DAEMON — Running all scenarios")
    print("=" * 60)

    print("\n[1/2] KHARG ISLAND ASSAULT — 30 scenarios\n")
    _kharg_main()

    print("\n[2/2] CSG NAVAL ENGAGEMENT — 30 scenarios\n")
    _csg_main()

    print("\n" + "=" * 60)
    print("DAEMON — All scenarios complete.")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main() or 0)
