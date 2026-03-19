import os
import random
import math
from datetime import datetime, timedelta

BASE_DIR = "persian_gulf_simulation"
LAYERS_DIR = os.path.join(BASE_DIR, "layers")
TILES_DIR = os.path.join(BASE_DIR, "tiles")

os.makedirs(LAYERS_DIR, exist_ok=True)
os.makedirs(TILES_DIR, exist_ok=True)

# -----------------------------
# CONFIGURATION
# -----------------------------

NUM_LAUNCH_SITES = 3000
TILE_SIZE = 200
MISSILE_COUNT = 600
INTERCEPTOR_COUNT = 300

START_TIME = datetime(2026, 3, 13, 12, 0, 0)

IRAN_LAT_MIN = 25
IRAN_LAT_MAX = 28.5
IRAN_LON_MIN = 51
IRAN_LON_MAX = 60

CARRIER_GROUPS = [
    (26.4, 56.5),
    (25.9, 55.3),
    (26.8, 57.2)
]

# speeds (m/s)
MISSILE_SPEED = 300
SUPERSONIC_SPEED = 1000
INTERCEPTOR_SPEED = 1200

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def random_coord():
    lat = random.uniform(IRAN_LAT_MIN, IRAN_LAT_MAX)
    lon = random.uniform(IRAN_LON_MIN, IRAN_LON_MAX)
    return lat, lon


def interpolate(lat1, lon1, lat2, lon2, steps=10):

    coords = []

    for i in range(steps + 1):
        f = i / steps
        lat = lat1 + (lat2 - lat1) * f
        lon = lon1 + (lon2 - lon1) * f
        coords.append((lat, lon))

    return coords


def circle(lat, lon, radius_km, points=72):

    coords = []

    for i in range(points):

        angle = math.radians(i / points * 360)

        dlat = radius_km * math.cos(angle) / 111
        dlon = radius_km * math.sin(angle) / (111 * math.cos(math.radians(lat)))

        coords.append((lat + dlat, lon + dlon))

    coords.append(coords[0])

    return coords


def kml_header():

    return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""


def kml_footer():

    return "</Document></kml>"


# -----------------------------
# GENERATE LAUNCH SITES
# -----------------------------

launch_sites = []

for i in range(NUM_LAUNCH_SITES):
    launch_sites.append(random_coord())

# -----------------------------
# TILE LAUNCH SITES
# -----------------------------

tiles = [
    launch_sites[i:i + TILE_SIZE]
    for i in range(0, len(launch_sites), TILE_SIZE)
]

for idx, tile in enumerate(tiles):

    kml = [kml_header()]

    for j, (lat, lon) in enumerate(tile):

        kml.append(f"""
<Placemark>
<name>Launch Battery {idx}_{j}</name>
<Point>
<coordinates>{lon},{lat},0</coordinates>
</Point>
</Placemark>
""")

    kml.append(kml_footer())

    with open(f"{TILES_DIR}/launch_tile_{idx}.kml", "w") as f:
        f.write("".join(kml))

# -----------------------------
# IRAN LAUNCH LAYER
# -----------------------------

layer = [kml_header()]

for i in range(len(tiles)):

    layer.append(f"""
<NetworkLink>
<name>Launch Tile {i}</name>
<Link>
<href>../tiles/launch_tile_{i}.kml</href>
</Link>
</NetworkLink>
""")

layer.append(kml_footer())

with open(f"{LAYERS_DIR}/iran_launch_sites.kml", "w") as f:
    f.write("".join(layer))

# -----------------------------
# US FORCES LAYER
# -----------------------------

kml = [kml_header()]

for i, (lat, lon) in enumerate(CARRIER_GROUPS):

    kml.append(f"""
<Placemark>
<name>Carrier Group {i+1}</name>
<Point>
<coordinates>{lon},{lat},0</coordinates>
</Point>
</Placemark>
""")

    ring = circle(lat, lon, 240)

    coords = ""

    for p in ring:
        coords += f"{p[1]},{p[0]},0\n"

    kml.append(f"""
<Placemark>
<name>SM6 Range Ring {i+1}</name>
<Polygon>
<outerBoundaryIs>
<LinearRing>
<coordinates>
{coords}
</coordinates>
</LinearRing>
</outerBoundaryIs>
</Polygon>
</Placemark>
""")

kml.append(kml_footer())

with open(f"{LAYERS_DIR}/us_forces.kml", "w") as f:
    f.write("".join(kml))

# -----------------------------
# MISSILE TRACKS
# -----------------------------

kml = [kml_header()]

for i in range(MISSILE_COUNT):

    lat, lon = random.choice(launch_sites)
    carrier = random.choice(CARRIER_GROUPS)

    launch_time = START_TIME + timedelta(seconds=i * 2)
    impact_time = launch_time + timedelta(seconds=240)

    path = interpolate(lat, lon, carrier[0], carrier[1])

    coord_string = ""

    for p in path:
        coord_string += f"{p[1]},{p[0]},0\n"

    kml.append(f"""
<Placemark>
<name>Missile {i}</name>

<TimeSpan>
<begin>{launch_time.isoformat()}Z</begin>
<end>{impact_time.isoformat()}Z</end>
</TimeSpan>

<LineString>
<coordinates>
{coord_string}
</coordinates>
</LineString>

</Placemark>
""")

kml.append(kml_footer())

with open(f"{LAYERS_DIR}/missile_tracks.kml", "w") as f:
    f.write("".join(kml))

# -----------------------------
# INTERCEPTOR TRACKS
# -----------------------------

kml = [kml_header()]

for i in range(INTERCEPTOR_COUNT):

    carrier = random.choice(CARRIER_GROUPS)

    launch_time = START_TIME + timedelta(seconds=120 + i)

    lat = carrier[0] + random.uniform(-0.05, 0.05)
    lon = carrier[1] + random.uniform(-0.05, 0.05)

    target = random.choice(launch_sites)

    path = interpolate(lat, lon, target[0], target[1], steps=6)

    coords = ""

    for p in path:
        coords += f"{p[1]},{p[0]},0\n"

    end_time = launch_time + timedelta(seconds=60)

    kml.append(f"""
<Placemark>
<name>SM6 Interceptor {i}</name>

<TimeSpan>
<begin>{launch_time.isoformat()}Z</begin>
<end>{end_time.isoformat()}Z</end>
</TimeSpan>

<LineString>
<coordinates>
{coords}
</coordinates>
</LineString>

</Placemark>
""")

kml.append(kml_footer())

with open(f"{LAYERS_DIR}/interceptor_tracks.kml", "w") as f:
    f.write("".join(kml))

# -----------------------------
# MASTER KML
# -----------------------------

master = [kml_header()]

layers = [
    "us_forces.kml",
    "iran_launch_sites.kml",
    "missile_tracks.kml",
    "interceptor_tracks.kml"
]

for layer in layers:

    master.append(f"""
<NetworkLink>
<name>{layer}</name>
<Link>
<href>layers/{layer}</href>
</Link>
</NetworkLink>
""")

master.append(kml_footer())

with open(f"{BASE_DIR}/master.kml", "w") as f:
    f.write("".join(master))

print("Simulation generated at:", BASE_DIR)