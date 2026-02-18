from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.job_run import JobRun


def test_worker_generation_and_media_serving(
    api_client_committed: TestClient,
    worker_flow_db: Session,
    test_environment: dict[str, str],
    monkeypatch,
) -> None:
    """
    処理内容:
        生成API実行後にworkerジョブを直接起動し、
        音声/スクリプト生成・DB状態更新・media配信が一連で成立することを検証します。

    Parameters:
        api_client_committed (TestClient): コミット挙動を含むテストクライアント。
        worker_flow_db (Session): workerフロー検証用のDBセッション。
        test_environment (dict[str, str]): テスト環境設定情報。
        monkeypatch: キュープロバイダ差し替えに利用するpytestフィクスチャ。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    from app.providers import queue as queue_module
    from jobs.generate_today import run_generate_today_job

    class _NoOpQueue:
        def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
            """
            処理内容:
                テスト内でキュー実行を抑止するためのNo-Op実装です。

            Parameters:
                user_id (str): 対象ユーザーID。
                episode_id (str): 対象Episode ID。
                job_run_id (str): 対象JobRun ID。

            Returns:
                None: 何も実行しません。
            """
            return None

    monkeypatch.setattr(queue_module, "get_queue_provider", lambda: _NoOpQueue())

    login = api_client_committed.post("/auth/mock_login", json={"handle": "worker_tester"})
    assert login.status_code == 200, login.text
    access_token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    generated = api_client_committed.post("/episodes/generate_today", headers=headers)
    assert generated.status_code == 200, generated.text
    payload = generated.json()

    episode_id = payload["episode_id"]
    job_run_id = payload["job_run_id"]
    assert payload["status"] == "processing"

    episode_before = worker_flow_db.get(Episode, episode_id)
    assert episode_before is not None
    user_id = str(episode_before.user_id)

    run_generate_today_job(
        user_id=user_id,
        episode_id=episode_id,
        job_run_id=job_run_id,
    )

    worker_flow_db.expire_all()
    episode = worker_flow_db.get(Episode, episode_id)
    assert episode is not None
    assert episode.status == "ready"
    assert episode.audio_s3_key
    assert episode.script_s3_key

    job = worker_flow_db.get(JobRun, job_run_id)
    assert job is not None
    assert job.status == "succeeded"

    storage_root = Path(test_environment["STORAGE_ROOT"])
    audio_path = storage_root / str(episode.audio_s3_key)
    script_path = storage_root / str(episode.script_s3_key)

    assert audio_path.exists() and audio_path.is_file()
    assert audio_path.stat().st_size > 0
    assert script_path.exists() and script_path.is_file()

    script_payload = json.loads(script_path.read_text(encoding="utf-8"))
    assert script_payload["episode_id"] == episode_id

    audio_resp = api_client_committed.get(f"/episodes/{episode_id}/audio_url", headers=headers)
    assert audio_resp.status_code == 200, audio_resp.text
    audio_url = audio_resp.json()["audio_url"]

    media_resp = api_client_committed.get(audio_url)
    assert media_resp.status_code == 200, media_resp.text
    assert len(media_resp.content) > 0
    assert media_resp.headers.get("content-type") in {
        "audio/mpeg",
        "application/octet-stream",
    }
