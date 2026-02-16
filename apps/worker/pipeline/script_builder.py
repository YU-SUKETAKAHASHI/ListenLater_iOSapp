from __future__ import annotations

from datetime import datetime, timezone


def build_script_payload(*, user_id: str, episode_id: str) -> dict:
    return {
        "episode_id": episode_id,
        "user_id": user_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": [
            "こんにちは、contextcast のデイリーエピソードです。",
            "これはStep B向けのダミースクリプトです。",
            "将来的にLLM生成へ置き換える想定です。",
        ],
    }
