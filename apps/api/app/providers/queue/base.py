from __future__ import annotations

from typing import Protocol


class QueueProvider(Protocol):
    def enqueue_generate_today(self, *, user_id: str, episode_id: str, job_run_id: str) -> None:
        ...
