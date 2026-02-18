from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.enums import EpisodeStatus, JobStatus, JobType
from app.models.job_run import JobRun


def start_generate_today(*, user_id: str, episode: Episode, db: Session) -> JobRun:
    """
    処理内容:
        当日Episode生成ジョブの開始準備として、Episode状態を `processing` に更新し、
        対応する `JobRun` レコードを `queued` 状態で作成します。

    Parameters:
        user_id (str): 生成ジョブの実行主体となるユーザーID。
        episode (Episode): 対象Episodeエンティティ。関数内で `status` が更新されます。
        db (Session): SQLAlchemyのDBセッション。コミットは呼び出し元で行います。

    Returns:
        JobRun: 追加済み（flush済み）の生成ジョブ実行レコード。
    """
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
