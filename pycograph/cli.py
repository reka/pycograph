"""CLI for Pycograph."""

from typing import Optional

import typer

from pycograph import __version__, pycograph
from pycograph.config import settings
from pycograph.exceptions import PycographException

app = typer.Typer()


def version_callback(value: bool):
    """Provide the version option for the commands.

    :param value: Shows whether the version option was provided.
    :type value: bool
    :raises typer.Exit: exit after showing the version number.
    """
    if value:
        typer.echo(f"pycograph {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """Main command."""


@app.command()
def load(
    project_dir: str = "",
    graph_name: str = "",
    overwrite: bool = typer.Option(
        False, help="If a graph with this name already exists, delete it."
    ),
    test_types: bool = typer.Option(
        False, help="Determine the test types by detecting subdirectories of tests."
    ),
    redis_host: Optional[str] = typer.Option(None, help="Redis instance host."),
    redis_port: Optional[int] = typer.Option(None, help="Redis instance port."),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """Load a Python project's code into a graph model."""
    settings.overwrite_existing_graph = overwrite
    settings.determine_test_types = test_types
    if redis_host:
        settings.redis_host = redis_host
    if redis_port:
        settings.redis_port = redis_port
    try:
        redis_graph = pycograph.load(project_dir, graph_name)
    except PycographException as e:
        typer.echo(e, err=True)
        return
    output = {
        "graph name": redis_graph.name,
        "nodes added": len(redis_graph.nodes),
        "edges added": len(redis_graph.edges),
    }
    typer.echo("Graph successfully updated.")
    typer.echo(output)
