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
    """
    処理内容:
        API/worker双方の設定キャッシュをクリアし、環境変数変更を即時反映できる状態にします。

    Parameters:
        なし。

    Returns:
        None: キャッシュクリアを副作用として実行します。
    """
    if WORKER_APP_ROOT not in sys.path:
        sys.path.insert(0, WORKER_APP_ROOT)

    from app.config import get_settings as get_api_settings
    from config import get_settings as get_worker_settings

    get_api_settings.cache_clear()
    get_worker_settings.cache_clear()


def _run_alembic_upgrade_head() -> None:
    """
    処理内容:
        Alembicの最新リビジョンまでマイグレーションを適用します。

    Parameters:
        なし。

    Returns:
        None: DBスキーマ更新を副作用として実行します。
    """
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=API_APP_ROOT,
        check=True,
    )


def _truncate_all_tables(database_url: str) -> None:
    """
    処理内容:
        テスト対象テーブルをTRUNCATEし、IDカウンタを含めて初期状態へ戻します。

    Parameters:
        database_url (str): 接続対象テストDBのURL。

    Returns:
        None: テーブル初期化を副作用として実行します。
    """
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
    """
    処理内容:
        テスト全体で共有する環境変数・ストレージ・DB初期化をセットアップします。
        テスト終了時には環境変数を元へ戻し、設定キャッシュを再クリアします。

    Parameters:
        tmp_path_factory (pytest.TempPathFactory): 一時ディレクトリ作成用ファクトリ。

    Returns:
        Generator[dict[str, str], None, None]: テスト用環境設定値をyieldするジェネレータ。
    """
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
    """
    処理内容:
        テストセッション全体で利用するSQLAlchemy Engineを生成して提供します。

    Parameters:
        test_environment (dict[str, str]): テスト環境設定情報。

    Returns:
        Generator: テスト用Engineをyieldし、終了時にdisposeするジェネレータ。
    """
    engine = create_engine(test_environment["DATABASE_URL"], future=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="function")
def db_connection(db_engine) -> Generator[Connection, None, None]:
    """
    処理内容:
        各テスト関数向けにDB接続とトランザクションを開始し、終了時にロールバックします。

    Parameters:
        db_engine: テストセッションで共有するSQLAlchemy Engine。

    Returns:
        Generator[Connection, None, None]: ロールバック付き接続をyieldするジェネレータ。
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    """
    処理内容:
        テスト関数ごとにsavepointベースのSQLAlchemy Sessionを生成して提供します。

    Parameters:
        db_connection (Connection): テスト関数単位のDB接続。

    Returns:
        Generator[Session, None, None]: テスト用Sessionをyieldするジェネレータ。
    """
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
    """
    処理内容:
        DB依存性をテスト用セッションに差し替えたFastAPI TestClientを提供します。

    Parameters:
        db_connection (Connection): テスト関数単位のDB接続。
        test_environment (dict[str, str]): テスト環境設定情報。

    Returns:
        Generator[TestClient, None, None]: 依存性上書き済みTestClientをyieldするジェネレータ。
    """
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
        """
        処理内容:
            テスト用のSessionLocalからDBセッションを生成し、依存性オーバーライド向けに提供します。

        Parameters:
            なし。

        Returns:
            Generator[Session, None, None]: テスト用DBセッションをyieldするジェネレータ。
        """
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
    """
    処理内容:
        実運用に近いコミット挙動を持つFastAPI TestClientを提供します。

    Parameters:
        test_environment (dict[str, str]): テスト環境設定情報。

    Returns:
        Generator[TestClient, None, None]: 標準依存性のTestClientをyieldするジェネレータ。
    """
    from app.main import create_app

    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def auth_headers(api_client: TestClient) -> dict[str, str]:
    """
    処理内容:
        モックログインを実行して有効なBearerトークン付きAuthorizationヘッダーを生成します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。

    Returns:
        dict[str, str]: 認証済みAuthorizationヘッダー。
    """
    handle = f"tester_{uuid4().hex[:8]}"
    response = api_client.post("/auth/mock_login", json={"handle": handle})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def truncate_tables_for_worker_flow(session: Session) -> None:
    """
    処理内容:
        workerフローテスト用に関連テーブルをTRUNCATEして初期化します。

    Parameters:
        session (Session): TRUNCATE実行に利用するSQLAlchemyセッション。

    Returns:
        None: テーブル初期化を副作用として実行します。
    """
    session.execute(
        text(
            "TRUNCATE TABLE refresh_tokens, job_runs, episodes, x_accounts, users "
            "RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


@pytest.fixture(scope="function")
def worker_flow_db(test_environment: dict[str, str]) -> Generator[Session, None, None]:
    """
    処理内容:
        worker統合フローテスト向けに独立Sessionを提供し、前後でテーブルを初期化します。

    Parameters:
        test_environment (dict[str, str]): テスト環境設定情報。

    Returns:
        Generator[Session, None, None]: workerフロー検証用Sessionをyieldするジェネレータ。
    """
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
