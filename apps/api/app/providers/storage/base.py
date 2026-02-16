from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageProvider(Protocol):
    def write_json(self, key: str, payload: dict) -> str:
        ...

    def write_bytes(self, key: str, content: bytes) -> str:
        ...

    def build_media_url(self, key: str) -> str:
        ...

    def resolve_path(self, key: str) -> Path:
        ...
