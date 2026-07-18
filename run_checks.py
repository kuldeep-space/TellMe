import asyncio
import os
import sys
from pathlib import Path
import time
from uuid import uuid4

sys.path.insert(0, r"d:\TellMe")

# Set environment before loading modules
os.environ["APP_DEBUG"] = "True"
os.environ["APP_LOG_LEVEL"] = "DEBUG"

from backend.app.bootstrap import bootstrap
from backend.core.event_bus import EventBus
from backend.model_management.registry import ModelRegistry
from backend.config.settings import get_settings

async def main():
    print("\n--- Verifying Bootstrap ---")
    container = bootstrap()
    print("Bootstrap complete.")

    print("\n--- Verifying Runtime Directories ---")
    settings = get_settings()
    for d in [settings.runtime_cache_path, settings.runtime_logs_path, Path(settings.runtime_temp_dir).resolve(), Path(settings.runtime_sessions_dir).resolve()]:
        assert d.exists(), f"Directory {d} does not exist!"
        print(f"Verified directory: {d}")

    print("\n--- Verifying Dependency Injection ---")
    event_bus = container.resolve(EventBus)
    assert event_bus is not None
    print(f"Resolved EventBus instance: {event_bus}")
    print(f"Registered contracts: {container.registered_contracts()}")

    print("\n--- Verifying EventBus (Sync & Async) ---")
    events_received = []

    def sync_sub(payload):
        events_received.append(f"sync received: {payload}")
        print(f"Sync subscriber called with {payload}")

    async def async_sub(payload):
        await asyncio.sleep(0.1) # Simulate I/O
        events_received.append(f"async received: {payload}")
        print(f"Async subscriber called with {payload}")

    event_bus.subscribe("test.event", sync_sub)
    event_bus.subscribe("test.event", async_sub)

    print("Publishing event...")
    event_bus.publish("test.event", payload="Hello")
    
    # Wait to allow background thread/async execution to finish
    await asyncio.sleep(0.5)
    
    assert "sync received: Hello" in events_received
    assert "async received: Hello" in events_received
    print("Both sync and async subscribers processed the event successfully without blocking.")
    event_bus.shutdown()

    print("\n--- Verifying Model Registry ---")
    # We haven't bound ModelRegistry in bootstrap yet per the stubs, but we can verify it directly
    from backend.model_management.registry import ModelRegistry
    from backend.model_management.metadata import GGUFMetadataExtractor, GGUFMetadata
    from backend.shared.enums.model import ModelArchitecture
    registry = ModelRegistry()
    assert registry is not None
    print(f"Model Registry initialized: {registry}")

    print("\n--- Testing complete. Reading log files... ---")
    app_log = settings.runtime_logs_path / "app.log"
    if app_log.exists():
        with open(app_log, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print("\nLast 10 log lines:")
            for line in lines[-10:]:
                print(line.strip())
    else:
        print(f"Log file not found at {app_log}")
        
    print("\nALL CHECKS PASSED.")

if __name__ == "__main__":
    asyncio.run(main())
