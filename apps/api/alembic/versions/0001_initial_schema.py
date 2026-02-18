"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-16 15:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    処理内容:
        初期スキーマとして users / x_accounts / episodes / job_runs テーブルを作成し、
        必要なインデックスと制約を定義します。

    Parameters:
        なし。

    Returns:
        None: スキーマ変更を副作用として適用します。
    """
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "x_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x_user_id", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("access_token_encrypted", sa.String(length=1024), nullable=True),
        sa.Column("refresh_token_encrypted", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_x_accounts_user_id"), "x_accounts", ["user_id"], unique=False)
    op.create_index(op.f("ix_x_accounts_x_user_id"), "x_accounts", ["x_user_id"], unique=True)
    op.create_index(op.f("ix_x_accounts_username"), "x_accounts", ["username"], unique=False)

    op.create_table(
        "episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("episode_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("summary_s3_key", sa.String(length=512), nullable=True),
        sa.Column("script_s3_key", sa.String(length=512), nullable=True),
        sa.Column("audio_s3_key", sa.String(length=512), nullable=True),
        sa.Column("duration_sec", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "episode_date", name="uq_episodes_user_id_episode_date"),
    )
    op.create_index(op.f("ix_episodes_episode_date"), "episodes", ["episode_date"], unique=False)
    op.create_index(op.f("ix_episodes_user_id"), "episodes", ["user_id"], unique=False)

    op.create_table(
        "job_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """
    処理内容:
        初期スキーマで作成したテーブル・インデックスを逆順で削除し、
        `upgrade` 前の状態へロールバックします。

    Parameters:
        なし。

    Returns:
        None: スキーマ変更の巻き戻しを副作用として適用します。
    """
    op.drop_table("job_runs")
    op.drop_index(op.f("ix_episodes_user_id"), table_name="episodes")
    op.drop_index(op.f("ix_episodes_episode_date"), table_name="episodes")
    op.drop_table("episodes")
    op.drop_index(op.f("ix_x_accounts_username"), table_name="x_accounts")
    op.drop_index(op.f("ix_x_accounts_x_user_id"), table_name="x_accounts")
    op.drop_index(op.f("ix_x_accounts_user_id"), table_name="x_accounts")
    op.drop_table("x_accounts")
    op.drop_table("users")
