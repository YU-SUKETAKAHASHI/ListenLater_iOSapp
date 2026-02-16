from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.enums import EpisodeStatus, JobStatus, JobType
from app.models.job_run import JobRun


def start_generate_today(*, user_id: str, episode: Episode, db: Session) -> JobRun:
    episode.status = EpisodeStatus.PROCESSING.value

    job = JobRun(
        job_type=JobType.DAILY_EPISODE_GENERATION.value,
        status=JobStatus.QUEUED.value,
        user_id=user_id,
        episode_id=episode.id,
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.flush()
    return job
