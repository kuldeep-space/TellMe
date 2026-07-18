"""
Standard API/Service Responses.

Provides standard structures for returning operational results from
the service layer back to the presentation layer.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ServiceResponse(BaseModel, Generic[T]):
    """
    Standard generic response envelope for service layer operations.

    Ensures the UI always receives a consistent shape, regardless of
    whether the operation succeeded or failed.

    Attributes:
        success: True if the operation succeeded.
        data: The typed payload if successful.
        error_message: Human-readable error message if success is False.
        error_code: Optional machine-readable error code.
    """

    success: bool
    data: T | None = Field(default=None)
    error_message: str | None = Field(default=None)
    error_code: str | None = Field(default=None)

    @classmethod
    def ok(cls, data: T) -> "ServiceResponse[T]":
        """Construct a successful response."""
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, message: str, code: str | None = None) -> "ServiceResponse[Any]":
        """Construct a failed response."""
        return cls(success=False, error_message=message, error_code=code)
