from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path
from uuid import uuid4

from config import get_settings
from jobs.generate_today import run_generate_today_job
from pipeline.dummy_audio import generate_dummy_mp3
from worker_logging import configure_logging

logger = logging.getLogger(__name__)


def run_daily_episode_job(user_id: str | None = None) -> None:
    settings = get_settings()
    storage_root = Path(settings.storage_root)

    run_user_id = user_id or "local-demo-user"
    episode_id = str(uuid4())
    key = f"episodes/{run_user_id}/{date.today().isoformat()}_{episode_id}/audio.mp3"

    output_path = generate_dummy_mp3(storage_root=storage_root, key=key)
    logger.info("dummy audio generated", extra={"audio_path": str(output_path), "s3_key_equivalent": key})


def main() -> int:
    settings = get_settings()
    configure_logging(settings.log_level)

    parser = argparse.ArgumentParser(description="contextcast worker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_daily_cmd = subparsers.add_parser("run-daily-episode", help="Run daily episode dummy pipeline")
    run_daily_cmd.add_argument("--user-id", type=str, required=False)

    generate_today_cmd = subparsers.add_parser("run-generate-today", help="Run Step B generation job")
    generate_today_cmd.add_argument("--user-id", type=str, required=True)
    generate_today_cmd.add_argument("--episode-id", type=str, required=True)
    generate_today_cmd.add_argument("--job-run-id", type=str, required=True)

    args = parser.parse_args()

    if args.command == "run-daily-episode":
        run_daily_episode_job(user_id=args.user_id)
        return 0

    if args.command == "run-generate-today":
        run_generate_today_job(user_id=args.user_id, episode_id=args.episode_id, job_run_id=args.job_run_id)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
