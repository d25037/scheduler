from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger
from typing import Literal, TypeAlias

Level: TypeAlias = Literal["info", "debug"]


def make_logger(name: str, level: Level = "info") -> Logger:
    logger: Logger = getLogger(name)
    handler = StreamHandler()
    formatter = Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    match level:
        case "info":
            logger.setLevel(INFO)
        case "debug":
            logger.setLevel(DEBUG)
    return logger
