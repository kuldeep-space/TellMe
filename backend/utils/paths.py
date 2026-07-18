"""
Path Utilities.

Stateless helper functions for manipulating and resolving file paths
safely.
"""

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path
