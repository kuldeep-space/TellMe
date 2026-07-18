"""
TellMe Application Constants.

Defines immutable, system-wide constants that do not change across
environments or user sessions.

These values should never be overridden via environment variables.
For configurable defaults, see backend/config/defaults.py.
"""

from pathlib import Path

# ─────────────────────────────────────────────
# Application Identity
# ─────────────────────────────────────────────

APP_NAME: str = "TellMe"
APP_VERSION: str = "0.1.0"
APP_AUTHOR: str = "TellMe Team"

# ─────────────────────────────────────────────
# Root Paths
# ─────────────────────────────────────────────

#: Absolute path to the project root (parent of `backend/`)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

#: Absolute path to the runtime data directory
RUNTIME_DIR: Path = PROJECT_ROOT / "runtime"

#: Absolute path to the backend package
BACKEND_DIR: Path = PROJECT_ROOT / "backend"

#: Absolute path to the frontend package
FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"

# ─────────────────────────────────────────────
# Runtime Sub-Directories (data only, never source code)
# ─────────────────────────────────────────────

RUNTIME_CACHE_DIR: Path = RUNTIME_DIR / "cache"
RUNTIME_LOGS_DIR: Path = RUNTIME_DIR / "logs"
RUNTIME_TEMP_DIR: Path = RUNTIME_DIR / "temp"
RUNTIME_SESSIONS_DIR: Path = RUNTIME_DIR / "sessions"

# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────

DEFAULT_DB_FILENAME: str = "tellme.db"
DEFAULT_DB_PATH: Path = RUNTIME_DIR / DEFAULT_DB_FILENAME

# ─────────────────────────────────────────────
# GGUF Model Constants
# ─────────────────────────────────────────────

#: Magic bytes at the start of every valid GGUF file (little-endian)
GGUF_MAGIC: bytes = b"GGUF"

#: Minimum supported GGUF version
GGUF_MIN_VERSION: int = 2

#: Maximum file size the validator will attempt to read headers from (500 MB)
GGUF_MAX_HEADER_SCAN_BYTES: int = 500 * 1024 * 1024

# ─────────────────────────────────────────────
# Event Bus Channel Names
# ─────────────────────────────────────────────

EVENT_SESSION_STARTED: str = "session.started"
EVENT_SESSION_ENDED: str = "session.ended"
EVENT_TURN_COMPLETED: str = "session.turn.completed"
EVENT_TOKEN_GENERATED: str = "llm.token.generated"
EVENT_AUDIO_CAPTURED: str = "speech.audio.captured"
EVENT_AUDIO_READY: str = "speech.audio.ready"
EVENT_MODEL_LOADED: str = "model.loaded"
EVENT_MODEL_SWITCHED: str = "model.switched"
EVENT_EVALUATION_COMPLETE: str = "evaluation.complete"
EVENT_REPORT_READY: str = "report.ready"

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

LOG_APP_FILENAME: str = "app.log"
LOG_AI_FILENAME: str = "ai.log"
LOG_ERROR_FILENAME: str = "errors.log"
