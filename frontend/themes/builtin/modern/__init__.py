from .theme import ModernTheme

# This allows the ThemeRegistry to auto-discover the theme
def get_theme():
    return ModernTheme()
