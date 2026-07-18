"""
Industrial QPainter Utilities.
"""
from frontend.components.industrial.painters.neumorphic import draw_neumorphic_panel, draw_inset_shadow
from frontend.components.industrial.painters.screw_painter import draw_screws
from frontend.components.industrial.painters.vent_painter import draw_vents
from frontend.components.industrial.painters.noise_painter import draw_noise_overlay

__all__ = [
    "draw_neumorphic_panel",
    "draw_inset_shadow",
    "draw_screws",
    "draw_vents",
    "draw_noise_overlay"
]
