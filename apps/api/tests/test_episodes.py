from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.episode import Episode
from app.models.job_run import JobRun


def test_today_requires_authentication(api_client: TestClient) -> None:
    response = api_client.get("/episodes/today")
    assert response.status_code == 401, response.text


def test_today_returns_episode_when_authenticated(api_client: TestClient, auth_headers: dict[str, str]) -> None:
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
    from app.providers import queue as queue_module

    calls: list[tuple[str, str, str]] = []

    class _NoOpQueue:
        def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
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
