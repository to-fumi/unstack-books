# Alembic の autogenerate が全テーブルを認識できるよう、ここで全エンティティを import する
from external.db.entities.base import Base
from external.db.entities.book import BookEntity

__all__ = ["Base", "BookEntity"]
