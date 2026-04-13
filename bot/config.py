from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Репозиторий: bot/config.py → родитель каталога bot/
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _env_files_for_bot() -> tuple[str, ...]:
    """Переменные бота — только из корневого `.env` репозитория (`./.env`)."""
    return (str(_REPO_ROOT / ".env"),)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files_for_bot(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_token: str = Field(..., description="Telegram Bot API token")

    @field_validator("telegram_token", mode="before")
    @classmethod
    def telegram_token_non_empty(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            raise ValueError(
                "TELEGRAM_TOKEN пустой: задайте токен в корневом .env репозитория "
                f"({_REPO_ROOT / '.env'})."
            )
        return value

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    backend_base_url: str = Field(
        default="",
        description="Полный URL backend; если пусто — http://BACKEND_HOST:BACKEND_PORT",
    )
    backend_api_client_token: str = ""
    backend_request_timeout: int = 120
    cohort_id: Optional[UUID] = Field(
        default=None,
        description="UUID потока (cohort) в backend",
    )
    membership_id: Optional[UUID] = Field(
        default=None,
        description="UUID участия (cohort_memberships) для вызовов API",
    )
    log_level: str = "INFO"
    proxy_url: str = Field(
        default="",
        description="Прокси только для Telegram (aiogram); не используется для запросов к backend.",
    )
    backend_http_proxy: str = Field(
        default="",
        description=(
            "Необязательно: прокси только для httpx → backend (если пусто — прямое подключение)."
        ),
    )

    @field_validator("cohort_id", "membership_id", mode="before")
    @classmethod
    def empty_env_uuid_to_none(cls, value: Any) -> Any:
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    def resolved_backend_base_url(self) -> str:
        base = self.backend_base_url.strip()
        if base:
            return base.rstrip("/")
        return f"http://{self.backend_host}:{self.backend_port}"
