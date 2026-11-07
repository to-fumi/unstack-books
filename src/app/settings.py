from functools import lru_cache

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 環境ごとに値が変わるものはデフォルトを持たせず、未設定なら起動時にエラーにする。
    # デフォルトがあるのは、環境に依存しないもの・入れ忘れても安全側に倒れるものだけ。

    app_name: str = "unstack-books"
    app_env: str = Field(description="local / dev / prod など")
    debug: bool = False

    postgres_user: str
    postgres_password: SecretStr  # repr / ログでは伏せる
    postgres_db: str
    postgres_host: str
    postgres_port: int
    db_echo: bool = False

    @property
    def database_url(self) -> str:
        # パスワードを含むのでログに出さないこと
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
