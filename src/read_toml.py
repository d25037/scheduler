import os
from pathlib import Path
from typing import Any

import tomllib
from models import AppSettings
from my_logger import my_loguru
from pydantic import ValidationError


def read_toml() -> AppSettings | FileNotFoundError | ValidationError:
    logger = my_loguru()
    executable_dir: Path = Path(os.path.dirname(__file__))
    settings_path = os.path.join(executable_dir.parent, "app_settings.toml")

    try:
        with open(settings_path, "rb") as f:
            logger.info(f"{settings_path} have been loaded.")
            toml_data: dict[str, Any] = tomllib.load(f)
            logger.debug(toml_data)
            app_settings = AppSettings(**toml_data)
            logger.debug(app_settings.model_dump())
            return app_settings
    except (FileNotFoundError, ValidationError) as e:
        return e
