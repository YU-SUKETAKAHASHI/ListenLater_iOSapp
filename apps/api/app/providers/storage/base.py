from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageProvider(Protocol):
    """ストレージ入出力機能の共通インターフェースを定義するプロトコル。"""

    def write_json(self, key: str, payload: dict) -> str:
        """
        処理内容:
            指定キーにJSONデータを保存します。

        Parameters:
            key (str): 保存先オブジェクトキー（S3キー相当の相対パス）。
            payload (dict): JSONとして保存する辞書データ。

        Returns:
            str: 保存したオブジェクトキー。
        """
        ...

    def write_bytes(self, key: str, content: bytes) -> str:
        """
        処理内容:
            指定キーにバイナリデータを保存します。

        Parameters:
            key (str): 保存先オブジェクトキー（S3キー相当の相対パス）。
            content (bytes): 保存するバイナリ内容。

        Returns:
            str: 保存したオブジェクトキー。
        """
        ...

    def build_media_url(self, key: str) -> str:
        """
        処理内容:
            保存済みオブジェクトキーから配信用URLを構築します。

        Parameters:
            key (str): 保存済みオブジェクトキー。

        Returns:
            str: クライアントが取得に利用するmedia URL。
        """
        ...

    def resolve_path(self, key: str) -> Path:
        """
        処理内容:
            オブジェクトキーに対応するローカルファイルシステム上の実パスを解決します。

        Parameters:
            key (str): 保存対象のオブジェクトキー。

        Returns:
            Path: ローカルファイルシステム上の解決済みパス。
        """
        ...
