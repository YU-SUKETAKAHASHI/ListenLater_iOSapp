from __future__ import annotations

from typing import Protocol


class QueueProvider(Protocol):
    """キュー投入機能のインターフェースを定義するプロトコル。"""

    def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
        """
        処理内容:
            当日Episode生成ジョブをキューへ投入します。
            実装クラス側で非同期基盤やローカル実行へ橋渡しするための抽象メソッドです。

        Parameters:
            user_id (str): ジョブ対象ユーザーID。
            episode_id (str): 生成対象Episode ID。
            job_run_id (str): ジョブ実行トラッキング用のJobRun ID。

        Returns:
            None: キュー投入のみを行い、結果は呼び出し元または後続処理で扱います。
        """
        ...
