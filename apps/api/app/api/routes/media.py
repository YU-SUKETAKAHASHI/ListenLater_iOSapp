from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings

router = APIRouter(tags=["media"])


@router.get("/media/{file_path:path}")
def serve_media(file_path: str) -> FileResponse:
    """
    処理内容:
        ローカルストレージ配下のメディアファイルをパス指定で配信します。
        ファイルが存在しない場合は404を返します。

    Parameters:
        file_path (str): ストレージルートからの相対ファイルパス。

    Returns:
        FileResponse: 指定ファイルのストリーミングレスポンス。
    """
    settings = get_settings()
    root = Path(settings.storage_root)
    resolved = root / file_path

    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail="media not found")

    return FileResponse(path=resolved)
