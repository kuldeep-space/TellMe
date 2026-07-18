"""
Terminal Design Token System — Layout Constants
Based on 8pt grid, but expressed as integer pixel values.
"""

class Spacing:
    PX2  = 2
    PX4  = 4
    PX8  = 8
    PX12 = 12
    PX16 = 16
    PX20 = 20
    PX24 = 24
    PX32 = 32
    PX40 = 40
    PX48 = 48
    PX64 = 64

class Radius:
    NONE = "0px"   # Terminal: no rounding anywhere
    SM   = "0px"
    MD   = "0px"
    LG   = "0px"
    FULL = "0px"

class Constants:
    SIDEBAR_WIDTH           = 220
    SIDEBAR_COLLAPSED_WIDTH = 52
    TOOLBAR_HEIGHT          = 32
    STATUSBAR_HEIGHT        = 24
    WIN_MIN_WIDTH           = 1024
    WIN_MIN_HEIGHT          = 720
    ICON_SM                 = 14
    ICON_MD                 = 16
    ICON_LG                 = 20
    ANIMATION_FAST          = 80
    ANIMATION_NORMAL        = 150
    BLINK_INTERVAL_MS       = 530   # terminal cursor blink
