from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings

router = APIRouter(tags=["media"])


@router.get("/media/{file_path:path}")
def serve_media(file_path: str) -> FileResponse:
    settings = get_settings()
    root = Path(settings.storage_root)
    resolved = root / file_path

    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail="media not found")

    return FileResponse(path=resolved)
