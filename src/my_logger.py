from enum import Enum
from logging import (
    DEBUG,
    INFO,
    Formatter,
    Logger,
    getLogger,
)

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
