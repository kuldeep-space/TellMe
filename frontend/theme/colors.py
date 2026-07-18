"""
Terminal Design Token System — Color Palette
Dark phosphor-green terminal on pure black background.
"""

class ThemeColors:
    # Background
    BACKGROUND      = "#0a0a0a"
    SURFACE         = "#101010"
    SURFACE_ELEVATED= "#151515"

    # Primary phosphor green
    PRIMARY         = "#33ff00"
    PRIMARY_DIM     = "#1f9900"
    PRIMARY_MUTED   = "#8fd68f"

    # Amber accent (secondary)
    SECONDARY       = "#ffb000"
    SECONDARY_DIM   = "#996a00"

    # Border / separators
    BORDER          = "#1f521f"
    BORDER_DIM      = "#0f290f"

    # Text
    TEXT_PRIMARY    = "#33ff00"
    TEXT_SECONDARY  = "#8fd68f"
    TEXT_MUTED      = "#456145"
    TEXT_DISABLED   = "#2a3d2a"
    TEXT_INVERSE    = "#0a0a0a"   # used on inverted (hover) buttons

    # Selection / highlight
    SELECTION       = "#194d19"
    SURFACE_HOVER   = "#0d200d"

    # Semantic
    SUCCESS         = "#33ff00"
    WARNING         = "#ffb000"
    DANGER          = "#ff3333"
    DANGER_DIM      = "#7a1a1a"
    INFO            = "#33ffcc"

    # Legacy aliases used by ThemeManager hydration
    SURFACE_HOVER   = "#0d200d"
    PRIMARY_HOVER   = "#4dff1a"
    ERROR           = "#ff3333"
