"""
Common Type Aliases.

Defines standardized type aliases used across the application to
improve readability and intent.
"""

from pathlib import Path
from typing import Any

#: A dictionary representing a JSON object.
JsonObject = dict[str, Any]

#: A path that can be either a string or a Path object.
PathLike = str | Path
