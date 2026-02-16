from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.x_account import XAccount


def upsert_user_and_x_account(handle: str, db: Session) -> User:
    existing_x = db.execute(select(XAccount).where(XAccount.username == handle)).scalar_one_or_none()
    if existing_x is not None:
        return db.get(User, existing_x.user_id)

    user = User()
    db.add(user)
    db.flush()

    x_account = XAccount(
        user_id=user.id,
        x_user_id=f"mock_{handle}",
        username=handle,
    )
    db.add(x_account)
    db.flush()
    return user


def store_refresh_token(
    *,
    user_id: str,
    token_hash: str,
    expires_at,
    db: Session,
) -> RefreshToken:
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(token)
    db.flush()
    return token
