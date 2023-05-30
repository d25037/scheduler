from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger
from typing import Literal, TypeAlias

Level: TypeAlias = Literal["info", "debug"]


def make_logger(name: str, level: Level = "info") -> Logger:
    logger: Logger = getLogger(name)
    match level:
        case "info":
            logger.setLevel(INFO)
        case "debug":
            logger.setLevel(DEBUG)

    handler = StreamHandler()
    logger.addHandler(handler)

    formatter = Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    return logger
