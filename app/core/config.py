from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理应用运行时配置。"""

    app_env: str = Field("dev", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(None, alias="OPENAI_BASE_URL")
    openai_model: str | None = Field(None, alias="OPENAI_MODEL")
    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    max_revision_rounds: int = Field(2, alias="MAX_REVISION_ROUNDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """返回缓存后的配置实例，避免重复读取环境变量。"""
    return Settings()
