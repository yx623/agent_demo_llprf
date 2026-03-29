import logging

from app.core.config import get_settings
from app.core.logging import get_logger


def _set_required_env(monkeypatch, log_level: str = "INFO") -> None:
    """补齐配置对象要求的最小环境变量。"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-demo-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv(
        "POSTGRES_DSN",
        "postgresql+psycopg://postgres:postgres@localhost:5432/agent_demo_llprf",
    )
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("LOG_LEVEL", log_level)


def test_get_logger_uses_configured_log_level(monkeypatch):
    _set_required_env(monkeypatch, log_level="DEBUG")
    get_settings.cache_clear()

    logger = get_logger("tests.logging.debug")

    assert logger.level == logging.DEBUG


def test_get_logger_does_not_duplicate_handlers(monkeypatch):
    _set_required_env(monkeypatch)
    get_settings.cache_clear()

    logger = get_logger("tests.logging.handlers")
    handlers_before = len(logger.handlers)

    same_logger = get_logger("tests.logging.handlers")

    assert same_logger is logger
    assert len(logger.handlers) == handlers_before == 1


def test_get_logger_disables_propagation(monkeypatch):
    _set_required_env(monkeypatch)
    get_settings.cache_clear()

    logger = get_logger("tests.logging.propagate")

    assert logger.propagate is False
