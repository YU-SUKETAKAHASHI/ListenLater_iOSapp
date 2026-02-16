from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.episodes import router as episodes_router
from app.api.routes.health import router as health_router
from app.api.routes.media import router as media_router
from app.config import get_settings
from app.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(title="contextcast-api", version=settings.service_version)
    application.include_router(auth_router)
    application.include_router(episodes_router)
    application.include_router(health_router)
    application.include_router(media_router)
    return application


app = create_app()
