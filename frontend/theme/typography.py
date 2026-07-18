"""
Terminal Design Token System — Typography
All text rendered in bundled JetBrains Mono.
Fallback chain: JetBrains Mono → Fira Code → Consolas → Courier New
"""

class Typography:
    FAMILY_PRIMARY  = "JetBrains Mono"
    FAMILY_FALLBACK = "Fira Code, Consolas, Courier New, monospace"
    FAMILY_FULL     = "JetBrains Mono, Fira Code, Consolas, Courier New, monospace"

    # Sizes (px integers, used via setPointSize or stylesheet)
    SIZE_XL     = 18
    SIZE_LG     = 14
    SIZE_MD     = 12
    SIZE_SM     = 11
    SIZE_XS     = 10

    # QSS string aliases used in style hydration
    SIZE_H1     = "18px"
    SIZE_H2     = "14px"
    SIZE_BODY   = "12px"
    SIZE_SMALL  = "11px"
    SIZE_CAPTION= "10px"

    # Weights
    WEIGHT_REGULAR  = 400
    WEIGHT_BOLD     = 700

    # Deprecated aliases kept for ThemeManager hydration
    H1 = "18px"
    H2 = "14px"
    H3 = "13px"
    BODY = "12px"
    BODY_SMALL = "11px"
    CAPTION = "10px"
