from __future__ import annotations

import json
from pathlib import Path

from app.config import get_settings


class LocalStorageProvider:
    """ローカルファイルシステムを利用するストレージプロバイダ。"""

    def __init__(self) -> None:
        """
        処理内容:
            環境設定からストレージルートとmedia配信ベースURLを読み込み、
            ローカル保存・URL生成で利用する内部設定を初期化します。

        Parameters:
            なし。

        Returns:
            None: インスタンスの初期化のみを行います。
        """
        settings = get_settings()
        self.storage_root = Path(settings.storage_root)
        self.media_base_url = settings.media_base_url.rstrip("/")

    def write_json(self, key: str, payload: dict) -> str:
        """
        処理内容:
            指定キーのパスへJSON文字列をUTF-8で保存します。
            必要に応じて親ディレクトリを作成し、保存したキーを返します。

        Parameters:
            key (str): 保存先オブジェクトキー（S3キー相当の相対パス）。
            payload (dict): JSON化して保存する辞書データ。

        Returns:
            str: 保存に使用したオブジェクトキー。
        """
        path = self.resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return key

    def write_bytes(self, key: str, content: bytes) -> str:
        """
        処理内容:
            指定キーのパスへバイナリデータを書き込みます。
            必要に応じて親ディレクトリを作成し、保存したキーを返します。

        Parameters:
            key (str): 保存先オブジェクトキー（S3キー相当の相対パス）。
            content (bytes): 保存するバイナリデータ。

        Returns:
            str: 保存に使用したオブジェクトキー。
        """
        path = self.resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def build_media_url(self, key: str) -> str:
        """
        処理内容:
            オブジェクトキーに対応する `/media/...` 形式の取得URLを構築します。

        Parameters:
            key (str): 保存済みオブジェクトキー。

        Returns:
            str: クライアント取得用のmedia URL。
        """
        return f"{self.media_base_url}/media/{key}"

    def resolve_path(self, key: str) -> Path:
        """
        処理内容:
            オブジェクトキーをローカルストレージルート配下の実ファイルパスへ変換します。

        Parameters:
            key (str): 解決対象のオブジェクトキー。

        Returns:
            Path: 保存・読み取りに利用するローカルファイルパス。
        """
        return self.storage_root / key
