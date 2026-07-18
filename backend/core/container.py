"""
TellMe Lightweight Service Container.

A custom Dependency Injection (DI) container designed to:
  - Register dependencies as singletons or factories.
  - Resolve dependencies by their contract (abstract class / interface).
  - Avoid external DI framework dependencies.
  - Be fully readable and debuggable without framework knowledge.

This container is intentionally minimal, replacing heavy DI frameworks
with a simple, typed dictionary-based resolver.

Usage:
    from backend.core.container import ServiceContainer
    from backend.contracts.llm import ILLMProvider
    from backend.providers.llm.llamacpp import LlamaCppProvider

    container = ServiceContainer()

    # Register a singleton
    container.register_singleton(ILLMProvider, LlamaCppProvider())

    # Register a factory (new instance every resolve)
    container.register_factory(ILLMProvider, lambda: LlamaCppProvider())

    # Resolve
    llm: ILLMProvider = container.resolve(ILLMProvider)
"""

from typing import Any, Callable, Type, TypeVar
import threading

from backend.core.exceptions import DependencyError
from backend.core.logging import get_logger

T = TypeVar("T")
_logger = get_logger(__name__)


class ServiceContainer:
    """
    Lightweight, type-safe Dependency Injection container.

    Supports two registration modes:
      - **Singleton**: A single shared instance is returned on every resolve.
      - **Factory**: A new instance is created on every resolve call.

    Intended to be constructed once in `backend/app/bootstrap.py` and
    passed through the application as the central service registry.
    """

    def __init__(self) -> None:
        """Initialize an empty service container."""
        self._lock = threading.RLock()
        self._singletons: dict[type, Any] = {}
        self._factories: dict[type, Callable[[], Any]] = {}

    def register_singleton(self, contract: Type[T], instance: T) -> None:
        """
        Register a pre-constructed singleton instance for a contract.

        The same instance is returned every time `resolve` is called for
        this contract.

        Args:
            contract: The abstract class or interface being registered.
            instance: The concrete instance to return on resolution.
        """
        with self._lock:
            self._singletons[contract] = instance
        _logger.debug(
            "Registered singleton for '{}' -> {}",
            contract.__name__,
            type(instance).__name__,
        )

    def register_factory(self, contract: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory callable for a contract.

        A new instance is created and returned every time `resolve` is called
        for this contract. Use this for stateful, short-lived services.

        Args:
            contract: The abstract class or interface being registered.
            factory: A zero-argument callable returning a new instance.
        """
        with self._lock:
            self._factories[contract] = factory
        _logger.debug(
            "Registered factory for '{}'",
            contract.__name__,
        )

    def resolve(self, contract: Type[T]) -> T:
        """
        Resolve a registered dependency by its contract type.

        Checks singletons first, then factories.

        Args:
            contract: The abstract class or interface to look up.

        Returns:
            The resolved concrete implementation.

        Raises:
            DependencyError: If no registration exists for the given contract.
        """
        with self._lock:
            if contract in self._singletons:
                return self._singletons[contract]  # type: ignore[return-value]

            if contract in self._factories:
                return self._factories[contract]()  # type: ignore[return-value]

        raise DependencyError(
            f"No registration found for contract '{contract.__name__}'. "
            "Ensure it is registered in bootstrap.py before use.",
            context={"contract": contract.__name__},
        )

    def is_registered(self, contract: Type[T]) -> bool:
        """
        Check if a contract has a registered implementation.

        Args:
            contract: The contract type to look up.

        Returns:
            True if the contract is registered, False otherwise.
        """
        with self._lock:
            return contract in self._singletons or contract in self._factories

    def registered_contracts(self) -> list[str]:
        """
        Return the names of all registered contract types.

        Returns:
            A sorted list of registered contract class names.
        """
        with self._lock:
            names = (
                list(self._singletons.keys()) + list(self._factories.keys())
            )
        return sorted(c.__name__ for c in names)
