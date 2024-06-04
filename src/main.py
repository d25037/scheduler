import cli_app
import streamlit_app
from rich import print
from typer import Typer

app = Typer()

app.command()(streamlit_app.streamlit)
app.command()(cli_app.cli)


@app.command()
def testrun():
    print("[magenta]test run")


if __name__ == "__main__":
    app()
