from __future__ import annotations

import hashlib


def hash_token(token: str) -> str:
    """
    処理内容:
        トークン文字列をSHA-256でハッシュ化し、保存・比較用の固定長文字列へ変換します。

    Parameters:
        token (str): ハッシュ化対象のトークン平文。

    Returns:
        str: SHA-256ハッシュの16進文字列。
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
