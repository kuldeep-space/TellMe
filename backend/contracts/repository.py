"""
Repository Contract.

Defines the generic, type-safe CRUD repository interface for all
domain entity persistence.

Every concrete repository implementation (SQLite, in-memory, cloud)
must implement `IRepository` to remain interchangeable without
modifying the service layer.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

# T is the domain entity type stored by this repository
T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Generic CRUD contract for all domain entity repositories.

    Implementations hide the underlying storage mechanism (SQLite,
    in-memory, cloud) from the business logic layer.

    Type Parameters:
        T: The domain entity type this repository manages.
    """

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> T | None:
        """
        Retrieve a single entity by its unique identifier.

        Args:
            entity_id: The UUID of the entity to retrieve.

        Returns:
            The entity if found, or None if not present.

        Raises:
            StorageError: On database access failure.
        """

    @abstractmethod
    def get_all(self) -> list[T]:
        """
        Retrieve all entities managed by this repository.

        Returns:
            A list of all stored entities (may be empty).

        Raises:
            StorageError: On database access failure.
        """

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Persist a new entity or update an existing one.

        If the entity's ID already exists in storage, it will be
        overwritten. Otherwise, a new record will be created.

        Args:
            entity: The domain entity to persist.

        Returns:
            The persisted entity (may include server-generated fields).

        Raises:
            StorageError: On database access failure.
        """

    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """
        Remove an entity from storage by its unique identifier.

        Args:
            entity_id: The UUID of the entity to remove.

        Returns:
            True if the entity was found and removed; False if not found.

        Raises:
            StorageError: On database access failure.
        """

    @abstractmethod
    def exists(self, entity_id: UUID) -> bool:
        """
        Check if an entity with the given ID exists in storage.

        Args:
            entity_id: The UUID to check.

        Returns:
            True if the entity exists; False otherwise.
        """
