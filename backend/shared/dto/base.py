"""
Base Data Transfer Objects.

Data Transfer Objects (DTOs) are used to move structured data between
the core application layers and external boundaries (like the UI or APIs)
without exposing raw domain models.
"""

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """
    Base class for all Data Transfer Objects.

    Provides a standard configuration:
      - Ignores extra fields dynamically.
      - Uses strict type validation by default.
      - Allows population from attribute aliases.
    """

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        strict=True,
    )
