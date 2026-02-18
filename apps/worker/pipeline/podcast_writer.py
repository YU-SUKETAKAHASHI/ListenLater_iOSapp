from __future__ import annotations

from datetime import datetime, timezone


def build_dummy_script_payload(*, user_id: str, episode_id: str) -> dict:
    """
    処理内容:
        ダミーのスクリプトJSONペイロードを生成します。

    Parameters:
        user_id (str): スクリプト生成対象のユーザーID。
        episode_id (str): スクリプト生成対象のEpisode ID。

    Returns:
        dict: 生成時刻と固定テキストを含むスクリプト構造体。
    """
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