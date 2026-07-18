"""
TellMe Logging Configuration.

Configures the Loguru logging library with multiple sinks:
  - Console sink: INFO level, formatted for readability during development.
  - File sink:    DEBUG level, formatted for structured diagnostics.
  - AI sink:      Specialized sink for capturing LLM prompt/response traces.

Usage:
    from backend.core.logging import configure_logging, get_logger

    configure_logging(log_dir="runtime/logs", debug=False)
    logger = get_logger(__name__)
    logger.info("Application started.")
"""

import sys
from pathlib import Path

from loguru import logger


# ─────────────────────────────────────────────
# Log Format Templates
# ─────────────────────────────────────────────

_CONSOLE_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

_AI_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "AI | "
    "{message}"
)


def configure_logging(log_dir: str | Path, debug: bool = False) -> None:
    """
    Configure all Loguru sinks for the TellMe application.

    Sets up three sinks:
      - Console: human-readable, INFO level (or DEBUG if debug=True).
      - Application file: all levels, rotated daily.
      - AI trace file: captures detailed LLM prompt/response traces.

    Args:
        log_dir: Absolute or relative path to the log output directory.
        debug: If True, sets the console sink to DEBUG level.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove Loguru's default sink before configuring custom ones.
    logger.remove()

    # Console Sink
    logger.add(
        sys.stdout,
        format=_CONSOLE_FORMAT,
        level="DEBUG" if debug else "INFO",
        colorize=True,
    )

    # Application File Sink
    logger.add(
        log_path / "app.log",
        format=_FILE_FORMAT,
        level="DEBUG",
        rotation="00:00",       # Rotate at midnight
        retention="14 days",    # Keep last 14 days
        compression="zip",
        encoding="utf-8",
    )

    # AI Trace Sink (filtered by custom "AI" level)
    logger.add(
        log_path / "ai.log",
        format=_AI_FORMAT,
        level="DEBUG",
        filter=lambda record: record["extra"].get("ai_trace", False),
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        encoding="utf-8",
    )

    # Crash / Error Sink
    logger.add(
        log_path / "errors.log",
        format=_FILE_FORMAT,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )

    logger.info("Logging configured. Log directory: {}", log_path.resolve())


def get_logger(name: str):
    """
    Return a contextually bound Loguru logger for a given module name.

    Args:
        name: Typically `__name__` of the calling module.

    Returns:
        A Loguru logger instance bound with the module name.
    """
    return logger.bind(module=name)


def get_ai_logger():
    """
    Return a Loguru logger pre-bound with the 'ai_trace' flag.

    This logger routes to the dedicated AI trace sink, keeping LLM
    prompt/response data isolated from application logs.

    Returns:
        A Loguru logger instance bound for AI tracing.
    """
    return logger.bind(ai_trace=True)
