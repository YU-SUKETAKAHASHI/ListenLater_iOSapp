from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings
from pipeline.dummy_audio import generate_dummy_mp3
from pipeline.script_builder import build_script_payload


def run_generate_today_job(*, user_id: str, episode_id: str, job_run_id: str) -> None:
    """
    処理内容:
        当日Episode生成ジョブ本体を実行します。
        DB上のジョブ/エピソード状態を更新しつつ、script.json と audio.mp3 を生成して保存します。

    Parameters:
        user_id (str): ジョブ対象ユーザーID。
        episode_id (str): 生成対象Episode ID。
        job_run_id (str): 実行状態を更新するJobRun ID。

    Returns:
        None: 生成処理とDB更新を副作用として実行します。
    """
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    start_at = datetime.now(timezone.utc)

    with SessionLocal() as db:
        import sys

        api_root = Path("/app")
        if str(api_root) not in sys.path:
            sys.path.insert(0, str(api_root))

        from app.models.episode import Episode
        from app.models.enums import EpisodeStatus, JobStatus
        from app.models.job_run import JobRun

        episode = db.get(Episode, episode_id)
        job = db.get(JobRun, job_run_id)

        if episode is None or job is None:
            raise RuntimeError("episode/job not found")

        episode.status = EpisodeStatus.PROCESSING.value
        job.status = JobStatus.RUNNING.value
        job.started_at = start_at
        db.commit()

        script_key = f"episodes/{episode_id}/script.json"
        audio_key = f"episodes/{episode_id}/audio.mp3"

        payload = build_script_payload(user_id=user_id, episode_id=episode_id)
        script_path = Path(settings.storage_root) / script_key
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        generate_dummy_mp3(storage_root=Path(settings.storage_root), key=audio_key)

        finish_at = datetime.now(timezone.utc)
        episode.status = EpisodeStatus.READY.value
        episode.script_s3_key = script_key
        episode.audio_s3_key = audio_key
        episode.duration_sec = 60

        job.status = JobStatus.SUCCEEDED.value
        job.finished_at = finish_at
        job.duration_ms = int((finish_at - start_at).total_seconds() * 1000)
        db.commit()
