from datetime import datetime

from pydantic import BaseModel


class EpisodeTodayResponse(BaseModel):
    """当日Episode取得APIのレスポンススキーマ。"""

    episode_id: str
    status: str
    title: str | None
    duration_sec: int | None
    created_at: datetime


class GenerateTodayResponse(BaseModel):
    """当日Episode生成開始APIのレスポンススキーマ。"""

    episode_id: str
    job_run_id: str
    status: str


class AudioUrlResponse(BaseModel):
    """Episode音声URL取得APIのレスポンススキーマ。"""

    episode_id: str
    audio_url: str
    status: str
