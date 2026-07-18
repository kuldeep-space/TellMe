"""
TellMe Settings Loader.

Loads application configuration from the environment using Pydantic Settings.
Supports overriding values from a `.env` file, OS environment variables,
or hardcoded defaults from `backend.config.defaults`.

Priority (highest to lowest):
  1. OS-level environment variables
  2. `.env` file values
  3. Defaults defined in `backend.config.defaults`

Usage:
    from backend.config.settings import get_settings

    settings = get_settings()
    print(settings.app_log_level)
    print(settings.database_url)
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.config import defaults


class AppSettings(BaseSettings):
    """
    Application-wide settings loaded from the environment.

    All fields map directly to keys in the .env file (case-insensitive).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─────────────────────────────────────────────
    # Application
    # ─────────────────────────────────────────────

    app_name: str = Field(default="TellMe")
    app_version: str = Field(default="0.1.0")
    app_debug: bool = Field(default=defaults.DEFAULT_APP_DEBUG)
    app_log_level: str = Field(default=defaults.DEFAULT_APP_LOG_LEVEL)

    # ─────────────────────────────────────────────
    # Runtime Paths
    # ─────────────────────────────────────────────

    runtime_cache_dir: str = Field(default="runtime/cache")
    runtime_logs_dir: str = Field(default="runtime/logs")
    runtime_temp_dir: str = Field(default="runtime/temp")
    runtime_sessions_dir: str = Field(default="runtime/sessions")

    # ─────────────────────────────────────────────
    # Database
    # ─────────────────────────────────────────────

    database_url: str = Field(default=defaults.DEFAULT_DATABASE_URL)

    # ─────────────────────────────────────────────
    # LLM Provider
    # ─────────────────────────────────────────────

    active_llm_backend: str = Field(default=defaults.DEFAULT_LLM_BACKEND)
    active_model_id: str | None = Field(default=None)

    # ─────────────────────────────────────────────
    # Speech Provider
    # ─────────────────────────────────────────────

    active_stt_backend: str = Field(default=defaults.DEFAULT_STT_BACKEND)
    active_tts_backend: str = Field(default=defaults.DEFAULT_TTS_BACKEND)

    # ─────────────────────────────────────────────
    # Search Provider
    # ─────────────────────────────────────────────

    search_enabled: bool = Field(default=defaults.DEFAULT_SEARCH_ENABLED)
    search_backend: str = Field(default=defaults.DEFAULT_SEARCH_BACKEND)

    # ─────────────────────────────────────────────
    # Plugin System
    # ─────────────────────────────────────────────

    plugins_enabled: bool = Field(default=defaults.DEFAULT_PLUGINS_ENABLED)
    plugins_dir: str = Field(default=defaults.DEFAULT_PLUGINS_DIR)

    # ─────────────────────────────────────────────
    # Validators
    # ─────────────────────────────────────────────

    @field_validator("app_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure the log level is a valid Loguru level."""
        valid = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid log level '{v}'. Must be one of {valid}.")
        return upper

    @property
    def runtime_logs_path(self) -> Path:
        """Return the resolved Path for the logs directory."""
        return Path(self.runtime_logs_dir).resolve()

    @property
    def runtime_cache_path(self) -> Path:
        """Return the resolved Path for the cache directory."""
        return Path(self.runtime_cache_dir).resolve()


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """
    Return the cached application settings singleton.

    Uses `lru_cache` to ensure settings are loaded from disk exactly once
    per application process. Call `get_settings.cache_clear()` in tests
    to reset between test runs.

    Returns:
        The fully loaded and validated AppSettings instance.
    """
    return AppSettings()
