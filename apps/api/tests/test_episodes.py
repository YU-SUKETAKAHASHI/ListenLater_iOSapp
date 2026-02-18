from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.job_run import JobRun


def test_today_requires_authentication(api_client: TestClient) -> None:
    """
    処理内容:
        未認証状態で `/episodes/today` を呼ぶと401が返ることを検証します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    response = api_client.get("/episodes/today")
    assert response.status_code == 401, response.text


def test_today_returns_episode_when_authenticated(api_client: TestClient, auth_headers: dict[str, str]) -> None:
    """
    処理内容:
        認証済みリクエストで `/episodes/today` がEpisode情報を返すことを検証します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。
        auth_headers (dict[str, str]): 認証済みAuthorizationヘッダー。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    response = api_client.get("/episodes/today", headers=auth_headers)
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["episode_id"]
    assert payload["status"] in {"scheduled", "pending", "processing", "ready"}
    assert payload["created_at"]


def test_generate_today_marks_processing_and_creates_job_run(
    api_client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    monkeypatch,
) -> None:
    """
    処理内容:
        `/episodes/generate_today` 実行時にEpisodeが `processing` へ遷移し、
        JobRunが `queued` で作成されることを検証します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。
        auth_headers (dict[str, str]): 認証済みAuthorizationヘッダー。
        db_session (Session): 生成後のDB状態確認に利用するセッション。
        monkeypatch: キュープロバイダ差し替えに利用するpytestフィクスチャ。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    from app.providers import queue as queue_module

    calls: list[tuple[str, str, str]] = []

    class _NoOpQueue:
        def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
            """
            処理内容:
                キュー投入処理の代替として呼び出し引数を記録します。

            Parameters:
                user_id (str): 対象ユーザーID。
                episode_id (str): 対象Episode ID。
                job_run_id (str): 対象JobRun ID。

            Returns:
                None: 呼び出し記録のみを行います。
            """
            calls.append((user_id, episode_id, job_run_id))

    monkeypatch.setattr(queue_module, "get_queue_provider", lambda: _NoOpQueue())

    response = api_client.post("/episodes/generate_today", headers=auth_headers)
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["episode_id"]
    assert payload["job_run_id"]
    assert payload["status"] == "processing"
    assert len(calls) == 1

    episode = db_session.get(Episode, payload["episode_id"])
    assert episode is not None
    assert episode.episode_date == date.today()
    assert episode.status == "processing"

    job = db_session.get(JobRun, payload["job_run_id"])
    assert job is not None
    assert job.episode_id == episode.id
    assert job.status == "queued"
