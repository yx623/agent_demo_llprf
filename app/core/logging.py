import logging

from app.core.config import get_settings


def _resolve_log_level(level_name: str) -> int:
    """把配置中的日志级别字符串转换为 logging 常量。"""
    level = getattr(logging, level_name.upper(), logging.INFO)
    return level if isinstance(level, int) else logging.INFO


def get_logger(name: str) -> logging.Logger:
    """返回带统一格式的日志实例。"""
    settings = get_settings()
    log_level = _resolve_log_level(settings.log_level)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
    return logger
