from enum import Enum


class EpisodeStatus(str, Enum):
    """Episodeのライフサイクル状態を表す列挙型。"""

    SCHEDULED = "scheduled"
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobStatus(str, Enum):
    """バックグラウンドジョブ実行状態を表す列挙型。"""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobType(str, Enum):
    """ジョブ種別を表す列挙型。"""

    DAILY_EPISODE_GENERATION = "daily_episode_generation"
