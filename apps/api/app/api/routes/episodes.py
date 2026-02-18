from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.db.session import get_db_session
from app.models.episode import Episode
from app.models.user import User
from app.providers import queue as queue_provider
from app.providers.storage.local import LocalStorageProvider
from app.schemas.episodes import AudioUrlResponse, EpisodeTodayResponse, GenerateTodayResponse
from app.services.episode_service import get_or_create_today_episode
from app.services.generation_service import start_generate_today

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/today", response_model=EpisodeTodayResponse)
def get_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> EpisodeTodayResponse:
    episode = get_or_create_today_episode(user_id=str(current_user.id), db=db)
    db.commit()
    db.refresh(episode)
    return EpisodeTodayResponse(
        episode_id=str(episode.id),
        status=episode.status,
        title=episode.title,
        duration_sec=episode.duration_sec,
        created_at=episode.created_at,
    )


@router.post("/generate_today", response_model=GenerateTodayResponse)
def generate_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> GenerateTodayResponse:
    episode = get_or_create_today_episode(user_id=str(current_user.id), db=db)
    job = start_generate_today(user_id=str(current_user.id), episode=episode, db=db)
    db.commit()

    queue = queue_provider.get_queue_provider()
    try:
        queue.enqueue_generate_today(user_id=str(current_user.id), episode_id=str(episode.id), job_run_id=str(job.id))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="failed to enqueue generation job") from exc

    db.refresh(episode)

    return GenerateTodayResponse(
        episode_id=str(episode.id),
        job_run_id=str(job.id),
        status=episode.status,
    )


@router.get("/{episode_id}/audio_url", response_model=AudioUrlResponse)
def get_audio_url(
    episode_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> AudioUrlResponse:
    episode = db.get(Episode, episode_id)
    if episode is None or str(episode.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="episode not found")
    if not episode.audio_s3_key:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="audio not ready")

    storage = LocalStorageProvider()
    return AudioUrlResponse(
        episode_id=str(episode.id),
        audio_url=storage.build_media_url(episode.audio_s3_key),
        status=episode.status,
    )
