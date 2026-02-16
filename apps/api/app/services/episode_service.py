from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.enums import EpisodeStatus


def get_or_create_today_episode(*, user_id: str, db: Session) -> Episode:
    episode = db.execute(
        select(Episode).where(
            Episode.user_id == user_id,
            Episode.episode_date == date.today(),
        )
    ).scalar_one_or_none()
    if episode is not None:
        return episode

    episode = Episode(
        user_id=user_id,
        episode_date=date.today(),
        status=EpisodeStatus.SCHEDULED.value,
        title="Daily Episode",
    )
    db.add(episode)
    db.flush()
    return episode
