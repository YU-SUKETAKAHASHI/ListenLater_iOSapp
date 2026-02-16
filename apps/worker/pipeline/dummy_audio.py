from __future__ import annotations

from pathlib import Path


def generate_dummy_mp3(storage_root: Path, key: str) -> Path:
    """Generate a deterministic dummy binary payload with .mp3 extension.

    This is a prototype placeholder to validate the pipeline and storage path flow.
    """
    output_path = storage_root / key
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Not a valid audio stream, but enough for pipeline wiring tests.
    output_path.write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x21DUMMY_CONTEXTCAST_MP3_DATA")
    return output_path
