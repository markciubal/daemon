"""kml — KML generation modules for the Kharg Island simulation."""
from persian_gulf_simulation.kml.styles import build_kml_styles, _hp_style, _circle_coords_deg
from persian_gulf_simulation.kml.descriptions import (
    _card, _pct, _alive_badge, _speed_stats, _fmt_speed,
    _marine_desc, _irgc_desc, _stinger_desc, _osprey_desc,
    _drone_desc, _ship_desc, _dboat_desc, _shahed_desc,
    _marine_folder_desc, _irgc_folder_desc, _stinger_folder_desc,
    _osprey_folder_desc, _drone_folder_desc, _dboat_folder_desc,
    _shahed_folder_desc, _bm_folder_desc, _island_shahed_folder_desc,
    _ship_folder_desc, _f35_strike_battle_desc, _iran_retaliation_desc,
    _battle_summary_desc,
)
from persian_gulf_simulation.kml.placemarks import (
    agent_to_placemarks, bm_to_placemarks,
    stinger_wez_placemark, stinger_shot_placemark,
    lz_hover_zone_placemark, lz_marker_placemark,
)
from persian_gulf_simulation.kml.narration import (
    extract_narration_events, narration_placemark, _narration_folder_desc,
)
from persian_gulf_simulation.kml.tour import gen_battle_tour
from persian_gulf_simulation.kml.document import gen_kml

__all__ = [
    "build_kml_styles", "_hp_style", "_circle_coords_deg",
    "_card", "_pct", "_alive_badge", "_speed_stats", "_fmt_speed",
    "_marine_desc", "_irgc_desc", "_stinger_desc", "_osprey_desc",
    "_drone_desc", "_ship_desc", "_dboat_desc", "_shahed_desc",
    "_marine_folder_desc", "_irgc_folder_desc", "_stinger_folder_desc",
    "_osprey_folder_desc", "_drone_folder_desc", "_dboat_folder_desc",
    "_shahed_folder_desc", "_bm_folder_desc", "_island_shahed_folder_desc",
    "_ship_folder_desc", "_f35_strike_battle_desc", "_iran_retaliation_desc",
    "_battle_summary_desc",
    "agent_to_placemarks", "bm_to_placemarks",
    "stinger_wez_placemark", "stinger_shot_placemark",
    "lz_hover_zone_placemark", "lz_marker_placemark",
    "extract_narration_events", "narration_placemark", "_narration_folder_desc",
    "gen_battle_tour",
    "gen_kml",
]
