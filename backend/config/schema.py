"""
Configuration Schema Validation.

Provides Pydantic base models to validate configuration payloads
from external sources (like UI forms or API requests) before they
are serialized or persisted to the settings database.
"""

from pydantic import BaseModel, Field

from backend.config import defaults


class ConfigUpdateSchema(BaseModel):
    """
    Schema for validating updates to the runtime configuration.

    All fields are optional because the user may only update a
    subset of settings at a time (e.g., just changing the LLM top_p).
    """

    app_debug: bool | None = Field(default=None)
    app_log_level: str | None = Field(default=None)

    active_llm_backend: str | None = Field(default=None)
    active_stt_backend: str | None = Field(default=None)
    active_tts_backend: str | None = Field(default=None)
    search_backend: str | None = Field(default=None)

    search_enabled: bool | None = Field(default=None)
    plugins_enabled: bool | None = Field(default=None)


class AIModelConfigSchema(BaseModel):
    """
    Schema for validating updates to a specific registered model's
    runtime configuration.
    """

    gpu_layers: int = Field(default=defaults.DEFAULT_LLM_GPU_LAYERS, ge=0)
    context_length: int = Field(default=defaults.DEFAULT_LLM_CONTEXT_LENGTH, gt=0)
    max_tokens: int = Field(default=defaults.DEFAULT_LLM_MAX_TOKENS, gt=0)
    temperature: float = Field(default=defaults.DEFAULT_LLM_TEMPERATURE, ge=0.0, le=2.0)
    top_p: float = Field(default=defaults.DEFAULT_LLM_TOP_P, ge=0.0, le=1.0)
    repeat_penalty: float = Field(default=defaults.DEFAULT_LLM_REPEAT_PENALTY, ge=1.0)
    threads: int = Field(default=0, ge=0)
