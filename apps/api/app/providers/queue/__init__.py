from app.providers.queue.base import QueueProvider
from app.providers.queue.local import LocalQueueProvider


def get_queue_provider() -> QueueProvider:
    """
    処理内容:
        アプリケーションで利用するキュー実装のプロバイダインスタンスを返します。
        現在はローカル実行用の `LocalQueueProvider` を返す固定実装です。

    Parameters:
        なし。

    Returns:
        QueueProvider: キュー投入インターフェースを満たすプロバイダ実装。
    """
    return LocalQueueProvider()


__all__ = ["QueueProvider", "LocalQueueProvider", "get_queue_provider"]
