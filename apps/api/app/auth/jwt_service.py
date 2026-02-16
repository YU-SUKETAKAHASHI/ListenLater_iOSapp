from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import get_settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> tuple[str, int]:
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
    settings = get_settings()
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("typ") != expected_typ:
        raise jwt.InvalidTokenError("invalid token type")
    return payload
