"""create books table

Revision ID: 0001
Revises:
Create Date: 2026-11-08 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

reading_status = postgresql.ENUM(
    "unread", "reading", "completed", name="reading_status", create_type=False
)


def upgrade() -> None:
    reading_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "books",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("isbn", sa.String(length=13), nullable=True),
        sa.Column("total_pages", sa.Integer(), nullable=True),
        sa.Column("current_page", sa.Integer(), nullable=False),
        sa.Column("status", reading_status, nullable=False),
        sa.Column("purchased_at", sa.Date(), nullable=True),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "total_pages IS NULL OR total_pages > 0", name=op.f("ck_books_total_pages_positive")
        ),
        sa.CheckConstraint("current_page >= 0", name=op.f("ck_books_current_page_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_books")),
    )
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=False)
    op.create_index(op.f("ix_books_status"), "books", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_books_status"), table_name="books")
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.drop_table("books")
    reading_status.drop(op.get_bind(), checkfirst=True)
