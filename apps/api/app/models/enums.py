from enum import Enum


class EpisodeStatus(str, Enum):
    SCHEDULED = "scheduled"
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobType(str, Enum):
    DAILY_EPISODE_GENERATION = "daily_episode_generation"
