"""
TellMe Configuration Defaults.

Defines the default values for all user-configurable settings.
These values are used as fallbacks when a setting is not present
in the .env file or the database.

Rules:
  - Do NOT use Path objects here. Use plain strings so they can be
    overridden safely by environment variable strings.
  - All values must be safe, sensible defaults for first-time users.
"""

# ─────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────

DEFAULT_APP_LOG_LEVEL: str = "INFO"
DEFAULT_APP_DEBUG: bool = False

# ─────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────

DEFAULT_DATABASE_URL: str = "sqlite:///runtime/tellme.db"

# ─────────────────────────────────────────────
# LLM Provider
# ─────────────────────────────────────────────

DEFAULT_LLM_BACKEND: str = "llamacpp"
DEFAULT_LLM_CONTEXT_LENGTH: int = 4096
DEFAULT_LLM_MAX_TOKENS: int = 1024
DEFAULT_LLM_TEMPERATURE: float = 0.7
DEFAULT_LLM_TOP_P: float = 0.9
DEFAULT_LLM_REPEAT_PENALTY: float = 1.1
DEFAULT_LLM_GPU_LAYERS: int = 0          # 0 = CPU only; user configures this

# ─────────────────────────────────────────────
# Speech Provider
# ─────────────────────────────────────────────

DEFAULT_STT_BACKEND: str = "whisper"
DEFAULT_TTS_BACKEND: str = "piper"
DEFAULT_AUDIO_SAMPLE_RATE: int = 16000   # Hz, standard for speech models
DEFAULT_VAD_SILENCE_MS: int = 800        # Silence duration before cut-off

# ─────────────────────────────────────────────
# Search Provider
# ─────────────────────────────────────────────

DEFAULT_SEARCH_ENABLED: bool = False
DEFAULT_SEARCH_BACKEND: str = "duckduckgo"
DEFAULT_SEARCH_MAX_RESULTS: int = 5

# ─────────────────────────────────────────────
# Interview Engine
# ─────────────────────────────────────────────

DEFAULT_INTERVIEW_DURATION_MINUTES: int = 45
DEFAULT_INTERVIEW_DIFFICULTY: str = "intermediate"  # easy | intermediate | hard
DEFAULT_INTERVIEW_LANGUAGE: str = "en"

# ─────────────────────────────────────────────
# Plugin System
# ─────────────────────────────────────────────

DEFAULT_PLUGINS_ENABLED: bool = False
DEFAULT_PLUGINS_DIR: str = "plugins/"
