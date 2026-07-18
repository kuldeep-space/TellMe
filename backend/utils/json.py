"""
JSON Utilities.

Stateless helper functions for serializing and deserializing JSON
with robust error handling and support for extended types (UUID, datetime).
"""

import json
from datetime import datetime
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    """Encodes extended Python types (UUIDs, datetimes) to JSON."""

    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
