import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SETTINGS_CONFIG = SettingsConfigDict(
    alias_generator=lambda field_name: field_name.upper(),
    env_file='.env' if os.path.exists('.env') else None,
)


class AppConfig(BaseSettings):
    model_config = SETTINGS_CONFIG

    postgres_user: str
    postgres_password: str
    postgres_db: str


class APIConfig(BaseSettings):
    model_config = SETTINGS_CONFIG

    minio_root_user: str
    minio_root_password: str
    minio_bucket_name: str

    yandex_folder_id: str
    yandex_api_key: str

    start_date: int = Field(default=0, ge=0)


class BotConfig(BaseSettings):
    model_config = SETTINGS_CONFIG

    telegram_bot_token: str
    state_ttl_hours: int
    data_ttl_hours: int

    api_url: str


app_config = AppConfig()
