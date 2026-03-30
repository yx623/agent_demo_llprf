"""集中定义应用配置。

这个文件是学习项目时最先应该理解的一层，因为数据库、Redis、
模型、工作流上限等运行参数都从这里进入系统。
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理应用运行时配置。

    使用 `BaseSettings` 的好处是，代码侧只依赖类型化字段，
    不再到处直接读环境变量，便于测试和教学说明。
    """

    app_env: str = Field("dev", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(None, alias="OPENAI_BASE_URL")
    openai_model: str | None = Field(None, alias="OPENAI_MODEL")
    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")
    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    max_revision_rounds: int = Field(2, alias="MAX_REVISION_ROUNDS")

    # 教学项目默认从 `.env` 读取配置，并忽略未声明字段，
    # 这样读者可以按需扩展自己的本地实验配置。
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """返回缓存后的配置实例，避免重复读取环境变量。"""
    return Settings()
