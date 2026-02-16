from __future__ import annotations

import json
from pathlib import Path

from app.config import get_settings


class LocalStorageProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.storage_root = Path(settings.storage_root)
        self.media_base_url = settings.media_base_url.rstrip("/")

    def write_json(self, key: str, payload: dict) -> str:
        path = self.resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return key

    def write_bytes(self, key: str, content: bytes) -> str:
        path = self.resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def build_media_url(self, key: str) -> str:
        return f"{self.media_base_url}/media/{key}"

    def resolve_path(self, key: str) -> Path:
        return self.storage_root / key
