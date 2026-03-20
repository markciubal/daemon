"""
daemon.py — DEPRECATED.

Use the module commands instead:

    python -m daemon.KHARG_ISLAND       # all 30 Kharg Island scenarios
    python -m daemon.CSG_SIM            # all 30 CSG naval scenarios
    python -m daemon.ALL                # all 60 scenarios

Optional filter for Kharg Island runs:

    python -m daemon.KHARG_ISLAND f35          # F-35 scenarios only
    python -m daemon.KHARG_ISLAND baseline     # baseline scenario only
    python -m daemon.KHARG_ISLAND igla_s       # Igla-S MANPADS scenarios
"""

import sys

print(__doc__)
print("This file is no longer the entry point. See usage above.")
sys.exit(1)
