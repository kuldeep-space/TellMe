import psutil
import dataclasses

@dataclasses.dataclass(frozen=True)
class ResourceSnapshot:
    available_ram_mb: float
    total_ram_mb: float
    process_ram_mb: float
    cpu_percent: float

class ResourceMonitor:
    """Service providing snapshots of system resources."""

    @staticmethod
    def get_snapshot() -> ResourceSnapshot:
        mem = psutil.virtual_memory()
        proc = psutil.Process()
        return ResourceSnapshot(
            available_ram_mb=mem.available / (1024 * 1024),
            total_ram_mb=mem.total / (1024 * 1024),
            process_ram_mb=proc.memory_info().rss / (1024 * 1024),
            cpu_percent=psutil.cpu_percent(interval=0.0)
        )
