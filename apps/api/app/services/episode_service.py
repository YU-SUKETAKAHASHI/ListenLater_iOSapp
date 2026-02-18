from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.enums import EpisodeStatus


def get_or_create_today_episode(*, user_id: str, db: Session) -> Episode:
    """
    処理内容:
        指定ユーザーの「今日」のEpisodeを取得し、存在しない場合は初期状態で新規作成します。
        既存レコードがある場合はそのまま返し、未存在時のみ `scheduled` 状態で追加して `flush` します。

    Parameters:
        user_id (str): Episodeを取得・作成する対象ユーザーID。
        db (Session): SQLAlchemyのDBセッション。コミットは呼び出し元で制御します。

    Returns:
        Episode: 既存または新規作成された当日分のEpisodeエンティティ。
    """
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
