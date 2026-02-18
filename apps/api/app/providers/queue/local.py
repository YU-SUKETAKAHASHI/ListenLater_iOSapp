from __future__ import annotations

import sys
from pathlib import Path

from app.db.session import SessionLocal
from app.models.enums import JobStatus
from app.models.job_run import JobRun


class LocalQueueProvider:
    """ローカル環境でキュー処理を同期実行するプロバイダ。"""

    def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
        """
        処理内容:
            workerモジュールを直接呼び出して当日Episode生成ジョブを実行します。
            実行中に例外が発生した場合は `JobRun` を `failed` に更新し、例外を再送出します。

        Parameters:
            user_id (str): ジョブ対象ユーザーID。
            episode_id (str): 生成対象Episode ID。
            job_run_id (str): 更新対象JobRun ID。

        Returns:
            None: キュー投入（ローカルでは同期実行）処理のみを行います。
        """
        worker_root = Path("/worker_app")
        if str(worker_root) not in sys.path:
            sys.path.insert(0, str(worker_root))

        try:
            from jobs.generate_today import run_generate_today_job  # type: ignore

            run_generate_today_job(user_id=user_id, episode_id=episode_id, job_run_id=job_run_id)
        except Exception as exc:  # noqa: BLE001
            with SessionLocal() as db:
                job = db.get(JobRun, job_run_id)
                if job is not None:
                    job.status = JobStatus.FAILED.value
                    job.error_message = str(exc)
                    db.commit()
            raise
