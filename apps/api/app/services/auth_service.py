from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.models.x_account import XAccount


def upsert_user_and_x_account(handle: str, db: Session) -> User:
    """
    処理内容:
        指定されたXハンドルに紐づく `XAccount` を検索し、既存であれば対応する `User` を返します。
        未登録の場合は新しい `User` と `XAccount` を作成して永続化し、その `User` を返します。

    Parameters:
        handle (str): Xアカウントのハンドル名。`XAccount.username` として一意に扱う識別子。
        db (Session): SQLAlchemyのDBセッション。呼び出し元でトランザクション管理されることを前提とします。

    Returns:
        User: 既存または新規作成された、対象ハンドルに対応するユーザーエンティティ。
    """
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
    """
    処理内容:
        リフレッシュトークンのハッシュ値と有効期限を `RefreshToken` テーブルへ保存します。
        インスタンス生成後に `flush` して、呼び出し側で即時参照可能な状態にします。

    Parameters:
        user_id (str): リフレッシュトークンを発行する対象ユーザーID。
        token_hash (str): 平文トークンではなく、保存用にハッシュ化した値。
        expires_at: トークン有効期限（日時オブジェクト）。DBモデルが受け取れる日時型で渡します。
        db (Session): SQLAlchemyのDBセッション。コミットは呼び出し元で行います。

    Returns:
        RefreshToken: 追加済み（flush済み）のリフレッシュトークンレコード。
    """
    token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(token)
    db.flush()
    return token
