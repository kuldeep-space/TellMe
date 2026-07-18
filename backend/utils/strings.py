"""
String Utilities.

Stateless helper functions for text manipulation, trimming, and formatting.
"""

def truncate(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length with an ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
