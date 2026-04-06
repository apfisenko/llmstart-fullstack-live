from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="127.0.0.1", validation_alias="BACKEND_HOST")
    port: int = Field(default=8000, ge=1, le=65535, validation_alias="BACKEND_PORT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    api_client_token: str = Field(
        ...,
        min_length=1,
        validation_alias="BACKEND_API_CLIENT_TOKEN",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
