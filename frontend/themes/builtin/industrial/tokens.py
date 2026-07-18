"""
Industrial Tokens — Heavy metal, LEDs, hardware switches.
"""

INDUSTRIAL_TOKENS = {
    # Typography
    "font.family.primary": "Roboto",
    "font.family.mono": "Courier New",
    "font.size.sm": "10px",
    "font.size.md": "12px",
    "font.size.lg": "16px",
    
    # Colors
    "colors.background": "#1e2226",  # Dark matte steel
    "colors.surface": "#2d3339",     # Lighter steel
    "colors.surface_hover": "#3a4149",
    "colors.border": "#0f1114",      # Deep shadows
    
    # Text
    "colors.text_primary": "#e6e6e6",
    "colors.text_secondary": "#a0a5ab",
    "colors.text_muted": "#6a7178",
    "colors.text_inverse": "#ffffff",
    
    # Accents (Safety Orange)
    "colors.accent": "#ff6600",
    "colors.accent_dim": "#993d00",
    
    # Status (LEDs)
    "status.success": "#33ff33",
    "status.warning": "#ffcc00",
    "status.danger": "#ff0000",
    "status.info": "#00ccff",
    
    # LED Specifics
    "led.online_color": "#33ff33",
    "led.error_color": "#ff0000",
    "led.warn_color": "#ffcc00",
    "led.info_color": "#00ccff",
    "led.offline_color": "#555555",
    "led.dot_size": 10,
    "led.glow_radius": 6,
    "led.pulse_enabled": True,
    
    # Radii
    "radius.sm": 2,
    "radius.md": 4,
    "radius.lg": 8,
    
    # Shadows (handled via custom painters mostly)
    "shadows.card": "drop-shadow(0 4px 6px rgba(0,0,0,0.5))",
    
    # Textures
    "textures.noise_tile": "metal_noise",
    "textures.noise_opacity": 0.05,
    
    # Layout
    "layout.button_min_height": 32,
    "layout.input_min_height": 32,
    
    # Animations
    "animation.button_lift_ms": 100,
    "animation.button_press_ms": 50,
    "animation.led_pulse_period_ms": 2000,
    "animation.duration_fast": 100,
    "animation.duration_normal": 200,
    "animation.easing_out": 16,     # OutSine
    "animation.easing_spring": 36,  # OutBack
}
