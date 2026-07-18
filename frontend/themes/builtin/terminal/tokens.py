"""
Terminal Theme — Token Population.

All 14 token categories populated with the phosphor-green terminal aesthetic.
Values match the existing ThemeColors, Typography, and Constants classes exactly
to guarantee zero visual regression after migration.
"""
from frontend.themes.base_theme import (
    ThemeTokens, ColorTokens, TypographyTokens, SpacingTokens, RadiusTokens,
    ShadowTokens, ShadowConfig, ElevationTokens, ElevationConfig,
    BorderTokens, AnimationTokens, IconTokens, GradientTokens,
    TextureTokens, LEDTokens, StatusColorTokens, LayoutTokens,
)


def make_terminal_tokens() -> ThemeTokens:
    """Construct and return the complete Terminal ThemeTokens instance."""
    return ThemeTokens(
        colors=ColorTokens(
            background       = "#0a0a0a",
            surface          = "#101010",
            surface_elevated = "#151515",
            surface_hover    = "#0d200d",
            muted            = "#0f290f",
            text_primary     = "#33ff00",
            text_secondary   = "#8fd68f",
            text_muted       = "#456145",
            text_disabled    = "#2a3d2a",
            text_inverse     = "#0a0a0a",
            accent           = "#33ff00",
            accent_dim       = "#1f9900",
            accent_hover     = "#4dff1a",
            accent_fg        = "#0a0a0a",
            border           = "#1f521f",
            border_light     = "#2a7a2a",
            border_dark      = "#0f290f",
            selection        = "#194d19",
        ),
        typography=TypographyTokens(
            family_sans      = "JetBrains Mono",  # terminal uses mono everywhere
            family_mono      = "JetBrains Mono",
            family_full_sans = "JetBrains Mono, Fira Code, Consolas, Courier New, monospace",
            family_full_mono = "JetBrains Mono, Fira Code, Consolas, Courier New, monospace",
            size_xs   = 9,
            size_sm   = 10,
            size_base = 12,
            size_lg   = 14,
            size_xl   = 16,
            size_2xl  = 18,
            size_3xl  = 24,
            weight_regular  = 400,
            weight_medium   = 400,   # terminal has no medium weight
            weight_semibold = 700,
            weight_bold     = 700,
            weight_black    = 700,
        ),
        spacing=SpacingTokens(
            px2=2, px4=4, px8=8, px12=12, px16=16,
            px20=20, px24=24, px32=32, px40=40, px48=48,
            px64=64, px96=96,
        ),
        radius=RadiusTokens(
            none=0, sm=0, md=0, lg=0, xl=0, xxl=0, full=0,
            # Terminal: zero rounding everywhere (hard edges)
        ),
        shadows=ShadowTokens(
            card=ShadowConfig(
                dark_x=0, dark_y=2, dark_blur=4, dark_color="#00000060",
                light_x=0, light_y=0, light_blur=0, light_color="#00000000",
            ),
            floating=ShadowConfig(
                dark_x=0, dark_y=4, dark_blur=8, dark_color="#00000080",
                light_x=0, light_y=0, light_blur=0, light_color="#00000000",
            ),
            pressed=ShadowConfig(inset=True,
                dark_x=1, dark_y=1, dark_blur=2, dark_color="#00000060",
                light_x=0, light_y=0, light_blur=0, light_color="#00000000",
            ),
            recessed=ShadowConfig(inset=True,
                dark_x=1, dark_y=1, dark_blur=3, dark_color="#00000050",
                light_x=0, light_y=0, light_blur=0, light_color="#00000000",
            ),
            glow=ShadowConfig(
                dark_x=0, dark_y=0, dark_blur=8,
                glow_color="#33ff00", glow_radius=8,
            ),
        ),
        elevation=ElevationTokens(
            chassis  = ElevationConfig(level=0,  label="chassis"),
            panel    = ElevationConfig(level=1,  label="panel"),
            floating = ElevationConfig(level=2,  label="floating"),
            recessed = ElevationConfig(level=-1, label="recessed"),
        ),
        borders=BorderTokens(
            width_thin=1, width_medium=1, width_thick=2,
            style_solid="solid", style_dashed="dashed",
        ),
        animation=AnimationTokens(
            duration_fast   = 80,
            duration_normal = 150,
            duration_slow   = 300,
            easing_spring   = 0,    # terminal: linear (mechanical, no bounce)
            easing_out      = 16,
            easing_in_out   = 17,
            easing_bounce   = 0,
            easing_linear   = 0,
            led_pulse_period_ms = 0,  # no LED pulse in terminal
        ),
        icons=IconTokens(
            size_xs=12, size_sm=14, size_md=16, size_lg=20, size_xl=24,
            stroke_thin=1.0, stroke_normal=1.5, stroke_bold=2.0,
        ),
        gradients=GradientTokens(
            chassis_noise_alpha=0.0,
            lighting_hotspot_alpha=0.0,
            radial_tint_color="#33ff00",
            button_top_alpha=0.0,
            button_bottom_alpha=0.0,
        ),
        textures=TextureTokens(
            noise_enabled=False,
            carbon_enabled=False,
            noise_opacity=0.0,
            carbon_opacity=0.0,
        ),
        led=LEDTokens(
            dot_size=6,
            glow_radius=4,
            pulse_enabled=False,
            pulse_period_ms=0,
            online_color="#33ff00",
            warn_color="#ffb000",
            error_color="#ff3333",
            info_color="#33ffcc",
            offline_color="#2a3d2a",
        ),
        status=StatusColorTokens(
            success="#33ff00",
            warning="#ffb000",
            danger="#ff3333",
            info="#33ffcc",
            busy="#456145",
            offline="#2a3d2a",
        ),
        layout=LayoutTokens(
            sidebar_width      = 220,
            toolbar_height     = 32,
            statusbar_height   = 24,
            navigation_width   = 220,
            panel_margin       = 12,
            window_padding     = 0,
            content_padding    = 12,
            section_gap        = 8,
            grid_gap           = 8,
            dialog_min_width   = 480,
            dialog_min_height  = 320,
            splitter_handle_px = 1,
            card_padding       = 12,
            input_min_height   = 28,
            button_min_height  = 28,
            touch_target_min   = 44,
        ),
    )
