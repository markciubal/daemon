"""
kml/styles.py — KML style definitions for the Kharg Island simulation.

Contains: build_kml_styles, _hp_style, _circle_coords_deg.
"""

import math

from persian_gulf_simulation.config import (
    SHIP_DEFS, LON_KM, LAT_KM,
)


def build_kml_styles():
    lines = []

    # ── Marines — coyote brown (KML AABBGGRR: R=0xa0, G=0x78, B=0x3c) ──────
    # man.png = infantry silhouette
    for style_id, color in [
        ("marine_hp4", "ff3c78a0"),   # full coyote brown
        ("marine_hp3", "ff305e80"),   # 80 %
        ("marine_hp2", "ff244462"),   # 65 %
        ("marine_hp1", "ff183045"),   # 45 % (badly wounded)
    ]:
        lc = "59" + color[2:]
        lines.append(f"""  <Style id="{style_id}">
    <IconStyle><color>{color}</color><scale>0.5</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon></IconStyle>
    <LineStyle><color>{lc}</color><width>1.5</width></LineStyle>
    <LabelStyle><color>{color}</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # US dead — dark grey
    lines.append("""  <Style id="marine_dead">
    <IconStyle><color>1affffff</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon></IconStyle>
    <LineStyle><color>40ffffff</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1affffff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── IRGC infantry — red (man.png) ────────────────────────────────────────
    for style_id, color in [
        ("irgc_hp4", "ff0000ff"), ("irgc_hp3", "ff0000cc"),
        ("irgc_hp2", "ff000088"), ("irgc_hp1", "ff000044"),
    ]:
        lc = "59" + color[2:]
        lines.append(f"""  <Style id="{style_id}">
    <IconStyle><color>{color}</color><scale>0.5</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon></IconStyle>
    <LineStyle><color>{lc}</color><width>1.5</width></LineStyle>
    <LabelStyle><color>{color}</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # Iranian dead — darker grey
    lines.append("""  <Style id="irgc_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── Iranian MANPADS (Stinger/Igla/Verba/QW-2/FN-6) — red, target icon ──
    for style_id, color in [("stinger_hp2", "ff0000ff"), ("stinger_hp1", "ff0000bb")]:
        lc = "59" + color[2:]
        lines.append(f"""  <Style id="{style_id}">
    <IconStyle><color>{color}</color><scale>0.7</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/target.png</href></Icon></IconStyle>
    <LineStyle><color>{lc}</color><width>1.5</width></LineStyle>
    <LabelStyle><color>{color}</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    lines.append("""  <Style id="stinger_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/man.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    lines.append("""  <Style id="stinger_wez">
    <LineStyle><color>400000ff</color><width>2</width></LineStyle>
    <PolyStyle><color>1a0000ff</color></PolyStyle>
  </Style>""")

    # ── Osprey (Marine Corps rotary-wing) — coyote brown, helicopter icon ────
    lines.append("""  <Style id="osprey_alive">
    <IconStyle><color>ff3c78a0</color><scale>0.9</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/helicopter.png</href></Icon></IconStyle>
    <LineStyle><color>593c78a0</color><width>1.5</width></LineStyle>
    <LabelStyle><color>ff3c78a0</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="osprey_dead">
    <IconStyle><color>1affffff</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40ffffff</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1affffff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── US ISR Drone (MQ-9 Reaper) — bright yellow, fixed-wing plane icon ───
    lines.append("""  <Style id="drone_alive">
    <IconStyle><color>ffffff00</color><scale>1.0</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/plane.png</href></Icon></IconStyle>
    <LineStyle><color>59ffff00</color><width>1.5</width></LineStyle>
    <LabelStyle><color>ffffff00</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="drone_dead">
    <IconStyle><color>1affffff</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40ffffff</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1affffff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── IRGCN FIAC drone boats — red, motorboat icon ─────────────────────────
    for style_id, color in [("dboat_hp2", "ff0000ff"), ("dboat_hp1", "ff0000bb")]:
        lc = "59" + color[2:]
        lines.append(f"""  <Style id="{style_id}">
    <IconStyle><color>{color}</color><scale>0.6</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/boat.png</href></Icon></IconStyle>
    <LineStyle><color>{lc}</color><width>1.5</width></LineStyle>
    <LabelStyle><color>{color}</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    lines.append("""  <Style id="dboat_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── Shahed kamikaze drone — red, plane icon ───────────────────────────────
    lines.append("""  <Style id="shahed_alive">
    <IconStyle><color>ff0000cc</color><scale>0.55</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>590000cc</color><width>1.5</width></LineStyle>
    <LabelStyle><color>ff0000cc</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="shahed_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── AI-capable Shahed — electric magenta, larger scale ───────────────────
    # KML AABBGGRR: magenta = ffff00ff  (full alpha, R=255, G=0, B=255)
    lines.append("""  <Style id="shahed_ai_alive">
    <IconStyle><color>ffff00ff</color><scale>0.85</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>99ff00ff</color><width>2.5</width></LineStyle>
    <LabelStyle><color>ffff00ff</color><scale>0.75</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="shahed_ai_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── US Navy ships — all blue tones (KML AABBGGRR format) ─────────────────
    # ship_healthy:  navy blue    RGB(0, 0, 200)  — full combat effectiveness
    # ship_damaged:  steel blue   RGB(0, 100, 150) — battle damage, reduced capability
    # ship_critical: cobalt blue  RGB(0, 68, 255)  — bright/urgent, still clearly naval
    lines.append("""  <Style id="ship_healthy">
    <IconStyle><color>ffc80000</color><scale>1.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/marina.png</href></Icon></IconStyle>
    <LineStyle><color>59c80000</color><width>2</width></LineStyle>
    <LabelStyle><color>ffc80000</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="ship_damaged">
    <IconStyle><color>ff966400</color><scale>1.3</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/marina.png</href></Icon></IconStyle>
    <LineStyle><color>59966400</color><width>2</width></LineStyle>
    <LabelStyle><color>ff966400</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="ship_critical">
    <IconStyle><color>ffff4400</color><scale>1.2</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/marina.png</href></Icon></IconStyle>
    <LineStyle><color>59ff4400</color><width>2</width></LineStyle>
    <LabelStyle><color>ffff4400</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="ship_sunk">
    <IconStyle><color>1affffff</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40ffffff</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1affffff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    lines.append("""  <Style id="irgc_site">
    <IconStyle><color>ff0000ff</color><scale>1.0</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/flag.png</href></Icon></IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # Narration event markers
    for sid, color, icon, scale in [
        ("narration_start",    "ffff0000", "paddle/blu-circle",   "1.2"),  # blue
        ("narration_osprey",   "ff00a5ff", "paddle/ylw-circle",   "1.2"),  # orange
        ("narration_ship_hit", "ff0055ff", "paddle/red-circle",   "1.2"),  # orange-red
        ("narration_sunk",     "ff0000ff", "paddle/red-stars",    "1.5"),  # bright red
        ("narration_cleared",  "ff00ff00", "paddle/grn-circle",   "1.2"),  # green
        ("narration_outcome",  "ffffffff", "paddle/wht-stars",    "1.4"),  # white
    ]:
        lines.append(f"""  <Style id="{sid}">
    <IconStyle><color>{color}</color><scale>{scale}</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/{icon}.png</href></Icon></IconStyle>
    <LabelStyle><color>{color}</color><scale>0.85</scale></LabelStyle>
  </Style>""")

    # Stinger missile trajectory arcs
    lines.append("""  <Style id="stinger_hit">
    <LineStyle><color>ff0000ff</color><width>3</width></LineStyle>
  </Style>""")
    lines.append("""  <Style id="stinger_miss">
    <LineStyle><color>66888888</color><width>1</width></LineStyle>
  </Style>""")

    # LZ hover zones — semi-transparent yellow circle (Stinger threat zone during drop)
    lines.append("""  <Style id="lz_hover_zone">
    <LineStyle><color>ff00ffff</color><width>2</width></LineStyle>
    <PolyStyle><color>2200ffff</color></PolyStyle>
  </Style>""")

    # LZ marker icon
    lines.append("""  <Style id="lz_marker">
    <IconStyle><color>ff00ffff</color><scale>1.1</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png</href></Icon></IconStyle>
    <LabelStyle><color>ff00ffff</color><scale>0.8</scale></LabelStyle>
  </Style>""")

    # ── Iranian SRBMs — colors match generate_wargame_kml.py MUNITIONS dict exactly ──
    # Fateh-313 SRBM: KML cc0055ff = 80% opaque, R=255 G=85 B=0 (deep orange-red)
    lines.append("""  <Style id="bm_fateh313">
    <IconStyle><color>ff0055ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>cc0055ff</color><width>3</width></LineStyle>
    <LabelStyle><color>ff0055ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")
    # Zolfaghar SRBM: KML cc0066ff = 80% opaque, R=255 G=102 B=0 (orange)
    lines.append("""  <Style id="bm_zolfaghar">
    <IconStyle><color>ff0066ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>cc0066ff</color><width>3</width></LineStyle>
    <LabelStyle><color>ff0066ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")
    # Fallback alias (keeps old references working)
    lines.append("""  <Style id="bm_active">
    <IconStyle><color>ff0055ff</color><scale>0.8</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>cc0055ff</color><width>3</width></LineStyle>
    <LabelStyle><color>ff0055ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="bm_intercepted">
    <IconStyle><color>ff00a5ff</color><scale>0.55</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LabelStyle><color>ff00a5ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")
    # bm_hit  — flash through red / orange / yellow then settle to red
    # KML AABBGGRR: red=ff0000ff  orange=ff0080ff  yellow=ff00ffff
    lines.append("""  <Style id="bm_hit">
    <IconStyle><color>ff0000ff</color><scale>1.1</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon></IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="bm_hit_orange">
    <IconStyle><color>ff0080ff</color><scale>1.3</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon></IconStyle>
    <LabelStyle><color>ff0080ff</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="bm_hit_yellow">
    <IconStyle><color>ff00ffff</color><scale>1.5</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href></Icon></IconStyle>
    <LabelStyle><color>ff00ffff</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    # Kill-radius circle flash colours (semi-transparent fill, AABBGGRR)
    lines.append("""  <Style id="bm_kill_radius_orange">
    <LineStyle><color>ff0080ff</color><width>2</width></LineStyle>
    <PolyStyle><color>660080ff</color><fill>1</fill><outline>1</outline></PolyStyle>
    <LabelStyle><color>ff0080ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="bm_kill_radius_yellow">
    <LineStyle><color>ff00ffff</color><width>2</width></LineStyle>
    <PolyStyle><color>6600ffff</color><fill>1</fill><outline>1</outline></PolyStyle>
    <LabelStyle><color>ff00ffff</color><scale>0.5</scale></LabelStyle>
  </Style>""")

    # ── BM CEP ring — yellow outline, no fill (shows target accuracy envelope) ──
    # Displayed from launch until intercept/impact; centered on planned target.
    lines.append("""  <Style id="bm_cep">
    <LineStyle><color>ff00d7ff</color><width>2</width></LineStyle>
    <PolyStyle><color>1900d7ff</color><fill>1</fill><outline>1</outline></PolyStyle>
    <LabelStyle><color>ff00d7ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")

    # ── BM kill-radius — red semi-transparent fill (persists at impact point) ──
    # Displayed from impact onwards; represents lethal-radius effect area.
    lines.append("""  <Style id="bm_kill_radius">
    <LineStyle><color>ff0000ff</color><width>2</width></LineStyle>
    <PolyStyle><color>660000ff</color><fill>1</fill><outline>1</outline></PolyStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.5</scale></LabelStyle>
  </Style>""")

    # ── Shahed kill-radius — orange semi-transparent fill (smaller than BM) ──
    # Displayed from drone impact onwards; 36 kg warhead, ~30 m lethal radius.
    lines.append("""  <Style id="shahed_kill_radius">
    <LineStyle><color>ff0080ff</color><width>1</width></LineStyle>
    <PolyStyle><color>440080ff</color><fill>1</fill><outline>1</outline></PolyStyle>
    <LabelStyle><color>ff0080ff</color><scale>0.4</scale></LabelStyle>
  </Style>""")

    # ── Shahed impact marker — red circle (placemark_circle) ─────────────────
    # KML AABBGGRR: red = ff0000ff
    lines.append("""  <Style id="shahed_impact">
    <IconStyle><color>ff0000ff</color><scale>1.1</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle>
    <LabelStyle><color>ff0000ff</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── Island-targeting Shahed — yellow-orange (distinct from ship-targeting red) ──
    lines.append("""  <Style id="island_shahed_alive">
    <IconStyle><color>ff00ccff</color><scale>0.55</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>5900ccff</color><width>1.5</width></LineStyle>
    <LabelStyle><color>ff00ccff</color><scale>0.6</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="island_shahed_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    # ── AI-capable island Shahed — bright cyan-white, larger scale ───────────
    # KML AABBGGRR: bright cyan = ffffff00  (R=0, G=255, B=255, A=255)
    lines.append("""  <Style id="island_shahed_ai_alive">
    <IconStyle><color>ffffff00</color><scale>0.85</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
    <LineStyle><color>99ffff00</color><width>2.5</width></LineStyle>
    <LabelStyle><color>ffffff00</color><scale>0.75</scale></LabelStyle>
  </Style>""")
    lines.append("""  <Style id="island_shahed_ai_dead">
    <IconStyle><color>1a222222</color><scale>0.4</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png</href></Icon></IconStyle>
    <LineStyle><color>40222222</color><width>1.5</width></LineStyle>
    <LabelStyle><color>1a222222</color><scale>0.6</scale></LabelStyle>
  </Style>""")

    raw = "\n".join(lines)
    balloon = ('    <BalloonStyle>'
               '<bgColor>ff000000</bgColor>'
               '<text>$[description]</text>'
               '</BalloonStyle>')
    raw = raw.replace('  </Style>', f'{balloon}\n  </Style>')
    return raw


def _hp_style(hp, is_marine, alive=True,
              is_stinger=False, is_drone=False, is_osprey=False,
              is_ship=False, is_dboat=False, is_shahed=False,
              is_island_shahed=False, is_ai=False):
    if is_ship:
        if not alive:
            return "#ship_sunk"
        max_hp = 6  # highest possible
        for s in SHIP_DEFS:
            if s[3] == max_hp:
                break
        # Use bands: full, mid, low
        all_max = [s[3] for s in SHIP_DEFS]
        # Determine which ship this is by hp value relative to band
        # Simple: >= 4 → healthy, 2-3 → damaged, 1 → critical
        if hp >= 4:
            return "#ship_healthy"
        elif hp >= 2:
            return "#ship_damaged"
        return "#ship_critical"
    if is_dboat:
        if not alive:
            return "#dboat_dead"
        return f"#dboat_hp{max(1, min(2, hp))}"
    if is_island_shahed:
        if is_ai:
            return "#island_shahed_ai_alive" if alive else "#island_shahed_ai_dead"
        return "#island_shahed_alive" if alive else "#island_shahed_dead"
    if is_shahed:
        if is_ai:
            return "#shahed_ai_alive" if alive else "#shahed_ai_dead"
        return "#shahed_alive" if alive else "#shahed_dead"
    if is_osprey:
        return "#osprey_alive" if alive else "#osprey_dead"
    if is_drone:
        return "#drone_alive" if alive else "#drone_dead"
    if not alive:
        if is_stinger:
            return "#stinger_dead"
        return "#marine_dead" if is_marine else "#irgc_dead"
    if is_stinger:
        return f"#stinger_hp{max(1, min(2, hp))}"
    prefix = "marine" if is_marine else "irgc"
    return f"#{prefix}_hp{max(1, min(4, hp))}"


def _circle_coords_deg(lon, lat, radius_km, n_pts=72):
    pts = []
    for i in range(n_pts + 1):
        a = 2.0 * math.pi * i / n_pts
        pts.append((
            lon + (radius_km / LON_KM) * math.cos(a),
            lat + (radius_km / LAT_KM) * math.sin(a),
        ))
    return pts
