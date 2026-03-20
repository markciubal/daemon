"""
kml/captions.py — Screen-overlay closed captions for KML battle playback.

Generates a semi-transparent caption bar anchored to the bottom-center of the
screen for each narration event.  Each caption is a PNG image (stored inside
the KMZ as captions/caption_NNN.png) with a <TimeSpan> so it appears and
disappears like a subtitle during Google Earth Pro timeline playback.

Requires Pillow (PIL).
"""

import io
import re

from PIL import Image, ImageDraw, ImageFont

from persian_gulf_simulation.simulation.spatial import ts

# ── Accent colour per event type (matches narration placemark palette) ──────
_ACCENT = {
    "start":           (88,  166, 255),   # blue
    "osprey_down":     (210, 153,  34),   # amber
    "ship_hit":        (255, 140,   0),   # orange
    "ship_sunk":       (248,  81,  73),   # red
    "cluster_cleared": (63,  185,  80),   # green
    "outcome":         (201, 209, 217),   # light grey
}

# ── Image geometry ────────────────────────────────────────────────────────────
_IMG_W  = 960    # px — wide enough for a full sentence
_IMG_H  = 96     # px — two text lines + accent bar + padding
_BAR_H  = 4      # px — accent stripe at top of each caption

# ── Font search order (Windows paths; fall back to PIL built-in) ──────────────
_FONT_PATHS = [
    "C:/Windows/Fonts/consola.ttf",   # Consolas — monospace, matches card style
    "C:/Windows/Fonts/cour.ttf",      # Courier New
    "C:/Windows/Fonts/arial.ttf",     # Arial
]


def _font(size: int) -> ImageFont.ImageFont:
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode the handful of entities used in description cards."""
    text = re.sub(r"<[^>]+>", "", str(text))
    return (text
            .replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&#9608;", "█").replace("&#9617;", "░")
            .replace("&#9679;", "●").replace("&#10005;", "✕")
            .replace("⚠", "!").replace("\u26a0", "!")).strip()


def _caption_lines(event: dict) -> tuple[str, str]:
    """Return (title_line, detail_line) as plain text for one narration event."""
    rows  = dict(event.get("rows", []))
    name  = _strip_html(event["name"])
    etype = event["type"]
    t_str = _strip_html(rows.get("Time", ""))

    if etype == "start":
        us = _strip_html(rows.get("US Forces", ""))
        return name, f"{t_str}  ·  {us}" if us else t_str

    if etype == "osprey_down":
        by = _strip_html(rows.get("By", ""))
        return name, f"{t_str}  ·  Downed by {by}" if by else t_str

    if etype == "ship_hit":
        src = _strip_html(rows.get("Source", ""))
        sta = _strip_html(rows.get("Status", ""))
        return name, "  ·  ".join(x for x in [t_str, src, sta] if x)

    if etype == "ship_sunk":
        crew = _strip_html(rows.get("Navy Crew KIA", ""))
        return name, f"{t_str}  ·  {crew}" if crew else t_str

    if etype == "cluster_cleared":
        sq = _strip_html(rows.get("Squads", ""))
        return name, f"{t_str}  ·  {sq}" if sq else t_str

    if etype == "outcome":
        res = _strip_html(rows.get("Result", ""))
        return name, f"{t_str}  ·  {res}" if res else t_str

    return name, t_str


def _make_png(title: str, detail: str, accent: tuple) -> bytes:
    """Render one caption as a PNG: dark translucent bar + accent stripe + two lines."""
    img  = Image.new("RGBA", (_IMG_W, _IMG_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Semi-transparent dark background
    draw.rectangle([0, 0, _IMG_W - 1, _IMG_H - 1], fill=(0, 0, 0, 190))
    # Accent bar at top
    draw.rectangle([0, 0, _IMG_W - 1, _BAR_H - 1], fill=(*accent, 255))

    f_title  = _font(22)
    f_detail = _font(15)
    cx       = _IMG_W // 2
    y_title  = _BAR_H + 14
    y_detail = y_title + 30

    draw.text((cx, y_title),  title,  fill=(*accent, 255),      font=f_title,  anchor="mt")
    draw.text((cx, y_detail), detail, fill=(200, 210, 220, 220), font=f_detail, anchor="mt")

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def gen_captions(narr_events: list) -> tuple[str, dict]:
    """Build ScreenOverlay KML + PNG file dict for all narration events.

    Returns:
        overlays_kml : str  — KML ScreenOverlay elements (ready to embed in Document)
        files        : dict — {"captions/caption_NNN.png": bytes, ...}
    """
    overlays = []
    files    = {}

    for i, event in enumerate(narr_events):
        path    = f"captions/caption_{i:03d}.png"
        accent  = _ACCENT.get(event["type"], (140, 140, 140))
        title, detail = _caption_lines(event)

        files[path] = _make_png(title, detail, accent)

        t_begin = ts(event["step"])
        t_end   = ts(event["end_step"])

        # Bottom-centre screen placement.
        # overlayXY: anchor = bottom-centre of the image.
        # screenXY:  that anchor sits 3% up from the bottom of the screen.
        # size: explicit pixel dimensions matching the generated PNG.
        overlays.append(f"""  <ScreenOverlay>
    <name>{_strip_html(event["name"])}</name>
    <TimeSpan><begin>{t_begin}</begin><end>{t_end}</end></TimeSpan>
    <Icon><href>{path}</href></Icon>
    <overlayXY x="0.5" y="0"    xunits="fraction" yunits="fraction"/>
    <screenXY  x="0.5" y="0.03" xunits="fraction" yunits="fraction"/>
    <size      x="{_IMG_W}"  y="{_IMG_H}"  xunits="pixels" yunits="pixels"/>
  </ScreenOverlay>""")

    return "\n".join(overlays), files
