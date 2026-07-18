"""
File Utilities.

Stateless helper functions for reading, writing, and hashing files.
"""

import hashlib
from pathlib import Path


def hash_file(path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()
