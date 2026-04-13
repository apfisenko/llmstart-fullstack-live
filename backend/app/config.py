from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки читаются из `backend/.env` (cwd процесса — каталог backend)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(
        ...,
        validation_alias="DATABASE_URL",
        description="Async PostgreSQL URL (postgresql+asyncpg://...). Только в backend/.env.",
    )

    host: str = Field(default="127.0.0.1", validation_alias="BACKEND_HOST")
    port: int = Field(default=8000, ge=1, le=65535, validation_alias="BACKEND_PORT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    api_client_token: Optional[str] = Field(
        default=None,
        validation_alias="BACKEND_API_CLIENT_TOKEN",
    )

    openrouter_api_key: Optional[str] = Field(
        default=None,
        validation_alias="OPENROUTER_API_KEY",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        validation_alias="OPENROUTER_BASE_URL",
    )
    openrouter_model: str = Field(
        default="openai/gpt-4o-mini",
        validation_alias="OPENROUTER_MODEL",
    )
    openrouter_timeout: int = Field(
        default=30,
        ge=1,
        validation_alias="OPENROUTER_TIMEOUT",
    )
    system_prompt_path: str = Field(
        default="bot/prompts/system.txt",
        validation_alias="SYSTEM_PROMPT_PATH",
    )
    proxy_url: str = Field(default="", validation_alias="PROXY_URL")

    @field_validator("database_url", mode="before")
    @classmethod
    def require_postgres_database_url(cls, value: object) -> object:
        if value == "" or value is None:
            raise ValueError("DATABASE_URL обязателен: postgresql+asyncpg://...")
        s = str(value)
        if not s.startswith("postgresql"):
            raise ValueError("Поддерживается только PostgreSQL (postgresql+asyncpg://...).")
        return value

    @field_validator("openrouter_api_key", mode="before")
    @classmethod
    def empty_openrouter_key_as_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @field_validator("api_client_token", mode="before")
    @classmethod
    def empty_api_client_token_as_none(cls, value: object) -> object:
        if value == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
