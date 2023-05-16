import os
from pathlib import Path
from pprint import pprint
from typing import Any

import tomllib
from models import AppSettings
from pydantic import ValidationError


def read_toml() -> AppSettings | FileNotFoundError | ValidationError:
    executable_dir: Path = Path(os.path.dirname(__file__))
    settings_path = os.path.join(executable_dir.parent, "app_settings.toml")

    try:
        with open(settings_path, "rb") as f:
            toml_data: dict[str, Any] = tomllib.load(f)
            pprint(toml_data)
            app_settings = AppSettings(**toml_data)
            pprint(app_settings.dict())
            return app_settings
    except (FileNotFoundError, ValidationError) as e:
        return e
