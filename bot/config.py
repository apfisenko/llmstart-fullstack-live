from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    telegram_token: str = Field(..., description="Telegram Bot API token")
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout: int = 30
    system_prompt_path: str = "bot/prompts/system.txt"
    max_history_size: int = 20
    log_level: str = "INFO"
    proxy_url: str = ""

    def resolved_system_prompt_path(self) -> Path:
        return Path(self.system_prompt_path).resolve()
