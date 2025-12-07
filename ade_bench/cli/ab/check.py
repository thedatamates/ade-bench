"""Commands for checking ADE-bench state."""

import typer

app = typer.Typer(
    help="Check ADE-bench's state",
    no_args_is_help=False,
)

@app.command("all")
def check_all():
    """
    Just run all of the checks.
    """
    is_docker_running()

@app.command("docker")
def is_docker_running():
    """
    Check if python can connect to an actively running docker daemon.
    """
    import docker
    try:
        docker.from_env()
        typer.echo("[✅] Connected to a running docker daemon.")
    except:
        typer.echo("[❌] Could not connect to a running docker daemon.")
