from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg://contextcast:contextcast@postgres:5432/contextcast"
    storage_root: str = "/storage"
    jwt_secret_key: str = "change_me_in_local"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    media_base_url: str = "http://localhost:8000"
    service_name: str = "contextcast-api"
    service_version: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("api_port", mode="before")
    @classmethod
    def normalize_api_port(cls, value: object) -> object:
        if value in (None, ""):
            return 8000
        return value

    @field_validator("access_token_expire_minutes", mode="before")
    @classmethod
    def normalize_access_minutes(cls, value: object) -> object:
        if value in (None, ""):
            return 30
        return value

    @field_validator("refresh_token_expire_days", mode="before")
    @classmethod
    def normalize_refresh_days(cls, value: object) -> object:
        if value in (None, ""):
            return 14
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
