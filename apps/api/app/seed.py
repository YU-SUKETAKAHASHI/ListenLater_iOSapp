from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.episode import Episode
from app.models.enums import EpisodeStatus
from app.models.user import User
from app.models.x_account import XAccount


def run_seed() -> None:
    with SessionLocal() as session:
        existing_user = session.execute(select(User)).scalar_one_or_none()
        if existing_user is None:
            user = User(id=uuid4())
            session.add(user)
            session.flush()

            x_account = XAccount(
                user_id=user.id,
                x_user_id="demo_x_user_001",
                username="demo_user",
            )
            session.add(x_account)

            episode = Episode(
                user_id=user.id,
                episode_date=date.today(),
                status=EpisodeStatus.PENDING.value,
                title="Demo daily briefing",
                summary_s3_key="episodes/demo/summary.json",
                script_s3_key="episodes/demo/script.json",
                audio_s3_key="episodes/demo/audio.mp3",
            )
            session.add(episode)

        session.commit()


if __name__ == "__main__":
    run_seed()
