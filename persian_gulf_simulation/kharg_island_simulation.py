"""
Compatibility shim — functionality moved to sub-modules.

The original monolithic script has been refactored into the
persian_gulf_simulation package.  This file is retained so that any
external references to kharg_island_simulation still work.
"""
from persian_gulf_simulation.runner import main

if __name__ == "__main__":
    main()
