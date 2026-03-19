"""agents — Agent class and factory functions for the Kharg Island simulation."""
from persian_gulf_simulation.agents.base import Agent
from persian_gulf_simulation.agents.factory import (
    init_marines,
    init_irgc,
    init_stingers,
    init_ospreys,
    init_drones,
    init_ships,
    init_drone_boats,
    init_iran_bm,
    init_island_shahed,
    init_shahed,
)

__all__ = [
    "Agent",
    "init_marines",
    "init_irgc",
    "init_stingers",
    "init_ospreys",
    "init_drones",
    "init_ships",
    "init_drone_boats",
    "init_iran_bm",
    "init_island_shahed",
    "init_shahed",
]
