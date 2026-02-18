from __future__ import annotations

from pathlib import Path


def generate_dummy_mp3(storage_root: Path, key: str) -> Path:
    """
    処理内容:
        ダミーのMP3風バイナリファイルを指定パスへ生成します。
        プロトタイプ段階でパイプライン疎通と保存先解決を検証するための処理です。

    Parameters:
        storage_root (Path): 保存先ルートディレクトリ。
        key (str): ルート配下の保存キー（相対パス）。

    Returns:
        Path: 生成したダミー音声ファイルの実パス。
    """
    output_path = storage_root / key
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Not a valid audio stream, but enough for pipeline wiring tests.
    output_path.write_bytes(b"ID3\x03\x00\x00\x00\x00\x00\x21DUMMY_CONTEXTCAST_MP3_DATA")
    return output_path
