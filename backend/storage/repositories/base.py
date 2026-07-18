"""
Base SQLAlchemy Repository implementation.

Provides generic CRUD operations for SQLAlchemy models, implementing
the IRepository contract.
"""

from typing import TypeVar, Generic
from uuid import UUID

from sqlalchemy.orm import Session
from backend.contracts.repository import IRepository

T = TypeVar("T")


class SQLAlchemyRepository(IRepository[T], Generic[T]):
    """Generic repository implementation for SQLAlchemy."""

    def __init__(self, session: Session, model_cls: type[T]) -> None:
        """Initialize with an active session and target model class."""
        self.session = session
        self.model_cls = model_cls

    def get(self, id: UUID) -> T | None:
        """Retrieve an entity by UUID."""
        return self.session.query(self.model_cls).get(id)

    def save(self, entity: T) -> None:
        """Save or update an entity."""
        self.session.add(entity)
        self.session.commit()

    def delete(self, id: UUID) -> bool:
        """Delete an entity by UUID."""
        entity = self.get(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
