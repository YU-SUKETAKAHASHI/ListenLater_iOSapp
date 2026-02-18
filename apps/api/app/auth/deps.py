from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt_service import decode_token
from app.db.session import get_db_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/mock_login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    """
    処理内容:
        アクセストークンを検証してユーザーIDを抽出し、DBから対応ユーザーを取得します。
        不正トークンやユーザー未存在時は401例外を送出します。

    Parameters:
        token (str): OAuth2依存性から注入されるBearerアクセストークン。
        db (Session): ユーザー照会に利用するSQLAlchemyセッション。

    Returns:
        User: 認証済みのユーザーエンティティ。
    """
    try:
        payload = decode_token(token, expected_typ="access")
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    return user
