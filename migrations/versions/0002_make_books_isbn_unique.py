"""make books.isbn unique (normalize to ISBN-13)

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-08 01:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _isbn10_to_13(isbn10: str) -> str:
    # マイグレーションはアプリのコード変更に影響されないよう、ドメインの Isbn を import せずに持つ
    body = "978" + isbn10[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(body))
    return body + str((10 - total % 10) % 10)


def upgrade() -> None:
    # 1. 既存の ISBN-10 を ISBN-13 に揃える（同じ本が 10 桁/13 桁で別扱いになるのを防ぐ）
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, isbn FROM books WHERE length(isbn) = 10")).all()
    for book_id, isbn in rows:
        bind.execute(
            sa.text("UPDATE books SET isbn = :isbn WHERE id = :id"),
            {"isbn": _isbn10_to_13(isbn), "id": book_id},
        )

    # 2. 重複があるとユニーク化できないので、分かりやすいメッセージで止める
    duplicates = (
        bind.execute(
            sa.text(
                "SELECT isbn FROM books WHERE isbn IS NOT NULL GROUP BY isbn HAVING count(*) > 1"
            )
        )
        .scalars()
        .all()
    )
    if duplicates:
        raise RuntimeError(
            f"Duplicate ISBNs exist in books; resolve them before upgrading: {duplicates}"
        )

    # 3. インデックスをユニークに張り替える（NULL 同士は重複扱いされない）
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=True)


def downgrade() -> None:
    # ISBN-13 への正規化は元に戻さない（ISBN-13 のままでも 0001 のスキーマで問題なく動く）
    op.drop_index(op.f("ix_books_isbn"), table_name="books")
    op.create_index(op.f("ix_books_isbn"), "books", ["isbn"], unique=False)
