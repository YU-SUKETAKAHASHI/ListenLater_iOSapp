import logging


def configure_logging(level: str = "INFO") -> None:
    """
    処理内容:
        workerプロセス向けの標準ロギング設定を初期化します。

    Parameters:
        level (str): 適用するログレベル文字列（例: `INFO`, `DEBUG`）。

    Returns:
        None: ロギング設定を適用する副作用のみを持ちます。
    """
    logging.basicConfig(
        level=level,
        format="ts=%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s",
    )
