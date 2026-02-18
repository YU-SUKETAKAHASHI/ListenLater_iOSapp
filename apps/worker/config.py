from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """workerプロセスで利用する環境設定を保持する設定モデル。"""

    app_env: str = "local"
    log_level: str = "INFO"
    storage_root: str = "/storage"
    database_url: str = "postgresql+psycopg://contextcast:contextcast@postgres:5432/contextcast"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    """
    処理内容:
        worker設定オブジェクトを生成して返します。
        `lru_cache` によりプロセス内で1回だけ生成し、以降は同一インスタンスを再利用します。

    Parameters:
        なし。

    Returns:
        WorkerSettings: worker実行時に参照する設定値の集合。
    """
    return WorkerSettings()
