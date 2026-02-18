from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import check_database_health, get_db_session
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck(db: Session = Depends(get_db_session)) -> HealthResponse:
    """
    処理内容:
        APIサービスのヘルス情報を返します。
        DB接続確認結果を含め、運用監視で利用する最小情報を提供します。

    Parameters:
        db (Session): DB接続状態確認に利用するSQLAlchemyセッション。

    Returns:
        HealthResponse: サービス状態・バージョン・DB状態を含むヘルスレスポンス。
    """
    settings = get_settings()
    db_ok = check_database_health(db)
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        version=settings.service_version,
        database="up" if db_ok else "down",
    )
