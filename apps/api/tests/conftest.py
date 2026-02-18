from __future__ import annotations

import os
import subprocess
import sys
from typing import Generator

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, sessionmaker


API_APP_ROOT = "/app"
WORKER_APP_ROOT = "/worker_app"


def _clear_settings_caches() -> None:
    if WORKER_APP_ROOT not in sys.path:
        sys.path.insert(0, WORKER_APP_ROOT)

    from app.config import get_settings as get_api_settings
    from config import get_settings as get_worker_settings

    get_api_settings.cache_clear()
    get_worker_settings.cache_clear()


def _run_alembic_upgrade_head() -> None:
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=API_APP_ROOT,
        check=True,
    )


def _truncate_all_tables(database_url: str) -> None:
    engine = create_engine(database_url, future=True)
    with Session(engine) as session:
        session.execute(
            text(
                "TRUNCATE TABLE refresh_tokens, job_runs, episodes, x_accounts, users "
                "RESTART IDENTITY CASCADE"
            )
        )
        session.commit()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_environment(tmp_path_factory: pytest.TempPathFactory) -> Generator[dict[str, str], None, None]:
    storage_root = tmp_path_factory.mktemp("contextcast_test_storage")

    env_updates = {
        "APP_ENV": "test",
        "DATABASE_URL": os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://contextcast:contextcast@postgres:5432/contextcast_test",
        ),
        "STORAGE_ROOT": str(storage_root),
        "MEDIA_BASE_URL": "http://testserver",
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "test_secret_key_only"),
        "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
        "REFRESH_TOKEN_EXPIRE_DAYS": os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"),
    }

    previous: dict[str, str | None] = {k: os.environ.get(k) for k in env_updates}
    os.environ.update(env_updates)

    _clear_settings_caches()
    _run_alembic_upgrade_head()
    _truncate_all_tables(env_updates["DATABASE_URL"])

    yield env_updates

    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    _clear_settings_caches()


@pytest.fixture(scope="session")
def db_engine(test_environment: dict[str, str]):
    engine = create_engine(test_environment["DATABASE_URL"], future=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="function")
def db_connection(db_engine) -> Generator[Connection, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(
        bind=db_connection,
        autocommit=False,
        autoflush=False,
        class_=Session,
        join_transaction_mode="create_savepoint",
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def api_client(db_connection: Connection, test_environment: dict[str, str]) -> Generator[TestClient, None, None]:
    from app.db import session as db_session_module
    from app.main import create_app

    SessionLocal = sessionmaker(
        bind=db_connection,
        autocommit=False,
        autoflush=False,
        class_=Session,
        join_transaction_mode="create_savepoint",
    )

    def _override_get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[db_session_module.get_db_session] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def api_client_committed(test_environment: dict[str, str]) -> Generator[TestClient, None, None]:
    from app.main import create_app

    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def auth_headers(api_client: TestClient) -> dict[str, str]:
    handle = f"tester_{uuid4().hex[:8]}"
    response = api_client.post("/auth/mock_login", json={"handle": handle})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def truncate_tables_for_worker_flow(session: Session) -> None:
    session.execute(
        text(
            "TRUNCATE TABLE refresh_tokens, job_runs, episodes, x_accounts, users "
            "RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


@pytest.fixture(scope="function")
def worker_flow_db(test_environment: dict[str, str]) -> Generator[Session, None, None]:
    engine = create_engine(test_environment["DATABASE_URL"], future=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    session = SessionLocal()
    truncate_tables_for_worker_flow(session)
    try:
        yield session
    finally:
        truncate_tables_for_worker_flow(session)
        session.close()
        engine.dispose()
