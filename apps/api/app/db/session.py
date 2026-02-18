from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    """
    処理内容:
        リクエストごとに利用するDBセッションを生成し、依存性注入で提供します。
        処理終了後は必ずセッションをクローズして接続リークを防ぎます。

    Parameters:
        なし。

    Returns:
        Generator[Session, None, None]: 利用可能なSQLAlchemyセッションをyieldするジェネレータ。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_health(session: Session) -> bool:
    """
    処理内容:
        単純な `SELECT 1` を実行し、DB接続が正常かどうかを判定します。

    Parameters:
        session (Session): ヘルスチェック対象のSQLAlchemyセッション。

    Returns:
        bool: クエリ実行に成功した場合は `True`、例外発生時は `False`。
    """
    try:
        session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
