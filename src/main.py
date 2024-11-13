from os import environ

from typer import Typer

import cli
import gui
from my_logger import my_loguru

app = Typer(no_args_is_help=True)

app.add_typer(gui.app, name="gui")
app.add_typer(cli.app, name="cli")


@app.command()
def testrun():
    # logger.remove()
    # logger.add(sys.stderr, level="INFO")
    environ["LOG_LEVEL"] = "DEBUG"
    logger = my_loguru()

    logger.info("test run")
    logger.debug("test run")
    logger.critical("test run")


if __name__ == "__main__":
    app()
