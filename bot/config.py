from __future__ import annotations

from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Каталог пакета бота — рядом с `bot/.env`
_BOT_DIR = Path(__file__).resolve().parent
_BOT_ENV_PATH = _BOT_DIR / ".env"

# В Docker env из compose; файла bot/.env внутри образа может не быть — только переменные окружения.
_bot_settings_kwargs: dict = {
    "env_file_encoding": "utf-8",
    "extra": "ignore",
}
if _BOT_ENV_PATH.is_file():
    _bot_settings_kwargs["env_file"] = (str(_BOT_ENV_PATH),)


class Config(BaseSettings):
    model_config = SettingsConfigDict(**_bot_settings_kwargs)

    telegram_token: str = Field(..., description="Telegram Bot API token")

    @field_validator("telegram_token", mode="before")
    @classmethod
    def telegram_token_non_empty(cls, value: Any) -> Any:
        if isinstance(value, str):
            value = value.strip()
        if value == "" or value is None:
            raise ValueError(
                f"TELEGRAM_TOKEN пустой: задайте токен в bot/.env ({_BOT_DIR / '.env'}) "
                "или переменные окружения контейнера."
            )
        return value

    @field_validator(
        "proxy_url",
        "backend_base_url",
        "backend_api_client_token",
        "backend_http_proxy",
        "backend_host",
        "log_level",
        mode="before",
    )
    @classmethod
    def strip_optional_str(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    backend_base_url: str = Field(
        default="",
        description="Полный URL backend; если пусто — http://BACKEND_HOST:BACKEND_PORT",
    )
    backend_api_client_token: str = ""
    backend_request_timeout: int = 120
    telegram_request_timeout: float = Field(
        default=120.0,
        ge=5.0,
        le=600.0,
        description=(
            "HTTP-таймаут aiogram к Telegram Bot API (сек). "
            "При медленном api.telegram.org увеличьте или задайте PROXY_URL."
        ),
    )
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
