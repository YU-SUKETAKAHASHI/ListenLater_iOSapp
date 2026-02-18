from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.jwt_service import create_access_token, create_refresh_token
from app.auth.security import hash_token
from app.db.session import get_db_session
from app.schemas.auth import MockLoginRequest, TokenPairResponse
from app.services.auth_service import store_refresh_token, upsert_user_and_x_account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/mock_login", response_model=TokenPairResponse)
def mock_login(payload: MockLoginRequest, db: Session = Depends(get_db_session)) -> TokenPairResponse:
    """
    処理内容:
        モックログインとして、ハンドル名に対応するユーザーとXアカウントを取得・作成し、
        アクセストークン/リフレッシュトークンを発行して返します。

    Parameters:
        payload (MockLoginRequest): ログイン要求情報（handle）を含むリクエストボディ。
        db (Session): ユーザー・トークン情報の永続化に利用するSQLAlchemyセッション。

    Returns:
        TokenPairResponse: 発行済みトークンペアと有効秒数を含むレスポンス。
    """
    user = upsert_user_and_x_account(handle=payload.handle.strip(), db=db)
    access_token, expires_in = create_access_token(user_id=str(user.id))
    refresh_token, refresh_exp = create_refresh_token(user_id=str(user.id))
    store_refresh_token(
        user_id=str(user.id),
        token_hash=hash_token(refresh_token),
        expires_at=refresh_exp,
        db=db,
    )
    db.commit()
    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )
