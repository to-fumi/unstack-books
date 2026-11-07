"""アプリケーション設定。

環境変数（および .env）をここで一括して読み込む。
他のモジュールは `get_settings()` 経由で設定値を参照すること。
"""

from functools import lru_cache

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- アプリケーション ---
    app_name: str = "unstack-books"
    app_env: str = Field(default="local", description="local / dev / prod など")
    debug: bool = False

    # --- データベース (PostgreSQL) ---
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "unstack_books"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    db_echo: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """SQLAlchemy (asyncpg) 用の接続 URL。"""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
