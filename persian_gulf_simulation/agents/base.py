"""
agents/base.py — Agent class for the Kharg Island simulation.
"""


class Agent:
    __slots__ = (
        "agent_id", "lon", "lat", "hp",
        "track", "dead_step",
        "launch_step", "lz", "landed",
        "drone_ammo", "peak_alt_m",
        "is_sailor", "is_ai",
    )

    def __init__(self, agent_id, lon, lat, hp, launch_step=None, lz=None, peak_alt_m=None):
        self.agent_id    = agent_id
        self.lon         = lon
        self.lat         = lat
        self.hp          = hp
        self.track       = []
        self.dead_step   = None
        self.launch_step = launch_step
        self.lz          = lz
        self.landed      = False
        self.drone_ammo  = None
        self.peak_alt_m  = peak_alt_m
        self.is_sailor   = False
        self.is_ai       = False

    def record(self, step):
        self.track.append((step, self.lon, self.lat, self.hp))

    def damage(self, amount, step):
        self.hp -= amount
        if self.hp <= 0 and self.dead_step is None:
            self.hp = 0
            self.dead_step = step
