"""
python -m daemon.CSG_SIM

Runs all 30 CSG naval engagement scenarios (carrier strike group vs Iranian
missile/drone/USV salvo) and writes KMZ files to output/scenarios/.

Each scenario takes ~5-15 seconds; total ~5 minutes.
"""

import sys

from persian_gulf_simulation.generate_wargame_kml import main


if __name__ == "__main__":
    sys.exit(main() or 0)
