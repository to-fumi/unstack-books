"""DB クライアント（engine / session の生成）。"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """リクエスト単位で 1 つのセッションを払い出す。"""
    async with SessionFactory() as session:
        yield session
