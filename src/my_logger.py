from enum import Enum
from logging import (
    DEBUG,
    INFO,
    Formatter,
    Logger,
    getLogger,
)
from os import environ
from sys import stderr

from loguru import logger
from rich.logging import RichHandler


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"


def make_logger(name: str, level: LogLevel = LogLevel.INFO) -> Logger:
    logger: Logger = getLogger(name)
    match level:
        case LogLevel.INFO:
            logger.setLevel(INFO)
        case LogLevel.DEBUG:
            logger.setLevel(DEBUG)

    handler = RichHandler()
    logger.addHandler(handler)

    formatter = Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
    handler.setFormatter(formatter)

    return logger


def my_loguru():
    logger.remove()
    logger.add(stderr, level=environ.get("LOG_LEVEL", "INFO"))
    return logger
