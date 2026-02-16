from datetime import datetime

from pydantic import BaseModel


class EpisodeTodayResponse(BaseModel):
    episode_id: str
    status: str
    title: str | None
    duration_sec: int | None
    created_at: datetime


class GenerateTodayResponse(BaseModel):
    episode_id: str
    job_run_id: str
    status: str


class AudioUrlResponse(BaseModel):
    episode_id: str
    audio_url: str
    status: str
