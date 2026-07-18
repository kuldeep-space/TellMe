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
import os
from pathlib import Path

from pydantic import Field, field_validator, model_validator
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
    allow_unsafe_loading: bool = Field(default=defaults.DEFAULT_ALLOW_UNSAFE_LOADING)


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

    @model_validator(mode="after")
    def resolve_runtime_paths(self) -> "AppSettings":
        """
        Resolve default runtime paths relative to user local app data when running from 
        a non-writable or installation directory (e.g. Program Files).
        """
        # Check if the app is installed or running in a non-writable directory
        program_files_paths = []
        for var in ["PROGRAMFILES", "PROGRAMFILES(X86)", "ProgramW6432"]:
            val = os.environ.get(var)
            if val:
                program_files_paths.append(Path(val).resolve())
        for path in ["C:\\Program Files", "C:\\Program Files (x86)"]:
            program_files_paths.append(Path(path).resolve())
            
        cwd = Path.cwd().resolve()
        import sys
        exe_path = Path(sys.executable).resolve()
        
        is_installed = False
        for pf in program_files_paths:
            try:
                if cwd.is_relative_to(pf) or exe_path.is_relative_to(pf):
                    is_installed = True
                    break
            except ValueError:
                continue
                
        if not is_installed:
            # Test write permission in current directory (or runtime if it exists)
            try:
                test_dir = cwd / "runtime"
                test_dir.mkdir(parents=True, exist_ok=True)
                test_file = test_dir / ".write_test"
                test_file.touch()
                test_file.unlink()
            except (OSError, PermissionError):
                is_installed = True
                
        if is_installed:
            local_appdata = os.environ.get("LOCALAPPDATA")
            if local_appdata:
                runtime_root = Path(local_appdata).resolve() / "TellMe" / "runtime"
            else:
                runtime_root = Path.home().resolve() / ".tellme" / "runtime"
        else:
            runtime_root = cwd / "runtime"

        # If any of the runtime dirs are their default (relative to "runtime"), redirect them to runtime_root
        if self.runtime_cache_dir.startswith("runtime"):
            self.runtime_cache_dir = str(runtime_root / Path(self.runtime_cache_dir).relative_to("runtime"))
        if self.runtime_logs_dir.startswith("runtime"):
            self.runtime_logs_dir = str(runtime_root / Path(self.runtime_logs_dir).relative_to("runtime"))
        if self.runtime_temp_dir.startswith("runtime"):
            self.runtime_temp_dir = str(runtime_root / Path(self.runtime_temp_dir).relative_to("runtime"))
        if self.runtime_sessions_dir.startswith("runtime"):
            self.runtime_sessions_dir = str(runtime_root / Path(self.runtime_sessions_dir).relative_to("runtime"))
            
        # Adjust database_url if it defaults to "sqlite:///runtime/tellme.db"
        if self.database_url.startswith("sqlite:///runtime"):
            suffix = self.database_url[len("sqlite:///runtime"):]
            suffix = suffix.lstrip("/\\")
            db_path = runtime_root / suffix
            db_path_str = str(db_path.resolve()).replace("\\", "/")
            self.database_url = f"sqlite:///{db_path_str}"
            
        return self

    @property
    def runtime_path(self) -> Path:
        """Return the resolved Path for the base runtime directory."""
        return Path(self.runtime_cache_dir).parent.resolve()

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
