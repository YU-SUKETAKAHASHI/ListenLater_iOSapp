from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import check_database_health, get_db_session
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck(db: Session = Depends(get_db_session)) -> HealthResponse:
    settings = get_settings()
    db_ok = check_database_health(db)
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        version=settings.service_version,
        database="up" if db_ok else "down",
    )
