from app.providers.queue.base import QueueProvider
from app.providers.queue.local import LocalQueueProvider


def get_queue_provider() -> QueueProvider:
    return LocalQueueProvider()


__all__ = ["QueueProvider", "LocalQueueProvider", "get_queue_provider"]
