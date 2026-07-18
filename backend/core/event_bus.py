"""
TellMe Central Event Bus.

Provides a lightweight, in-process Publish/Subscribe (PubSub) mechanism.
Modules emit named events with optional payloads; subscribers receive them
without needing direct references to the emitting module.

Design Goals:
  - Decouples UI, services, and AI providers from each other.
  - Supports both synchronous and asynchronous subscribers.
  - Enforces typed event payloads via the shared events package.

Usage:
    from backend.core.event_bus import EventBus

    bus = EventBus()

    # Subscribe
    bus.subscribe("session.started", on_session_started)

    # Publish
    bus.publish("session.started", payload={"session_id": "abc123"})

    # Unsubscribe
    bus.unsubscribe("session.started", on_session_started)
"""

import asyncio
import inspect
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from backend.core.logging import get_logger

_logger = get_logger(__name__)


class EventBus:
    """
    Centralized in-process publish/subscribe event bus.

    Supports:
      - Synchronous and asynchronous subscriber callbacks.
      - Named event channels (string keys).
      - Wildcard subscription (*) to receive all events.
      - Safe error isolation: a failing subscriber does not block others.

    This class is intended to be registered as a singleton in the
    application's service container.
    """

    def __init__(self) -> None:
        """Initialize the EventBus with an empty subscriber registry."""
        self._lock = threading.RLock()
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._executor = ThreadPoolExecutor(thread_name_prefix="EventBus_AsyncWorker")

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        Register a callback to be invoked when a named event is published.

        Args:
            event: The event channel name (e.g., "session.started").
            callback: A sync or async callable invoked with the event payload.
        """
        with self._lock:
            self._subscribers[event].append(callback)
        _logger.debug("Subscribed {} to event '{}'", callback.__name__, event)

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """
        Remove a previously registered callback from an event channel.

        Args:
            event: The event channel name.
            callback: The exact callable to remove.
        """
        with self._lock:
            callbacks = self._subscribers.get(event, [])
            if callback in callbacks:
                callbacks.remove(callback)
        _logger.debug("Unsubscribed {} from event '{}'", callback.__name__, event)

    def publish(self, event: str, payload: Any = None) -> None:
        """
        Emit a named event synchronously to all registered subscribers.

        Wildcard subscribers (registered under "*") are also notified.
        Errors in individual subscribers are caught and logged, preventing
        one bad subscriber from blocking others.

        Args:
            event: The event channel name.
            payload: Optional data passed to each subscriber callback.
        """
        _logger.debug("Publishing event '{}' with payload: {}", event, payload)
        with self._lock:
            # Create a shallow copy of targets to prevent mutation during iteration
            targets = list(self._subscribers.get(event, [])) + list(self._subscribers.get("*", []))

        for callback in targets:
            try:
                if inspect.iscoroutinefunction(callback):
                    # Schedule async callbacks on the running event loop if available.
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(callback(payload))
                    except RuntimeError:
                        # No running loop — dispatch to background thread to avoid blocking.
                        self._executor.submit(asyncio.run, callback(payload))
                else:
                    callback(payload)
            except Exception as exc:  # noqa: BLE001
                _logger.error(
                    "Subscriber {} raised an error on event '{}': {}",
                    callback.__name__, event, exc
                )

    def clear(self, event: str | None = None) -> None:
        """
        Remove all subscribers, optionally scoped to a single event.

        Args:
            event: If provided, clears only that event channel.
                   If None, clears all registered subscribers.
        """
        with self._lock:
            if event:
                self._subscribers.pop(event, None)
            else:
                self._subscribers.clear()

    def subscriber_count(self, event: str) -> int:
        """
        Return the number of active subscribers for a given event.

        Args:
            event: The event channel name.

        Returns:
            The count of registered callbacks.
        """
        with self._lock:
            return len(self._subscribers.get(event, []))

    def shutdown(self) -> None:
        """Shutdown the internal executor."""
        self._executor.shutdown(wait=False)
