"""books テーブルの ORM エンティティ。ドメインモデルとは別物として扱う。"""

from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from domain.value_objects import ReadingStatus
from external.db.entities.base import Base, TimestampMixin


class BookEntity(TimestampMixin, Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("total_pages IS NULL OR total_pages > 0", name="total_pages_positive"),
        CheckConstraint("current_page >= 0", name="current_page_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255))
    isbn: Mapped[str | None] = mapped_column(String(13), index=True)
    total_pages: Mapped[int | None] = mapped_column(Integer)
    current_page: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(
            ReadingStatus,
            name="reading_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=ReadingStatus.UNREAD,
        index=True,
    )
    purchased_at: Mapped[date | None] = mapped_column(Date)
    memo: Mapped[str | None] = mapped_column(Text)
