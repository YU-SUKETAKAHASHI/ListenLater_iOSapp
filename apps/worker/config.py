from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    storage_root: str = "/storage"
    database_url: str = "postgresql+psycopg://contextcast:contextcast@postgres:5432/contextcast"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
