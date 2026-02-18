from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import get_settings


def _now_utc() -> datetime:
    """
    処理内容:
        タイムゾーン付きUTC現在時刻を取得します。

    Parameters:
        なし。

    Returns:
        datetime: UTCタイムゾーン付き現在時刻。
    """
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> tuple[str, int]:
    """
    処理内容:
        指定ユーザー向けのアクセストークンを生成し、有効秒数と合わせて返します。

    Parameters:
        user_id (str): アクセストークンを発行する対象ユーザーID。

    Returns:
        tuple[str, int]: JWT文字列と、トークン有効秒数（int）のタプル。
    """
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    exp = _now_utc() + expires_delta
    payload = {
        "sub": user_id,
        "typ": "access",
        "exp": exp,
        "iat": _now_utc(),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """
    処理内容:
        指定ユーザー向けのリフレッシュトークンを生成し、有効期限日時と合わせて返します。

    Parameters:
        user_id (str): リフレッシュトークンを発行する対象ユーザーID。

    Returns:
        tuple[str, datetime]: JWT文字列と、有効期限日時（UTC）のタプル。
    """
    settings = get_settings()
    exp = _now_utc() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "typ": "refresh",
        "jti": str(uuid4()),
        "exp": exp,
        "iat": _now_utc(),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, exp


def decode_token(token: str, expected_typ: str) -> dict:
    """
    処理内容:
        JWTを検証・デコードし、期待するトークン種別（typ）であることを確認します。

    Parameters:
        token (str): 検証対象のJWT文字列。
        expected_typ (str): 期待する `typ` クレーム値（例: `access`, `refresh`）。

    Returns:
        dict: 検証済みJWTペイロード。
    """
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("typ") != expected_typ:
        raise jwt.InvalidTokenError("invalid token type")
    return payload
