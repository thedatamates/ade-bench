"""Commands for viewing ADE-bench results."""

import sys
import typer
from pathlib import Path
from typing import Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ade_bench.cli.ab import runs as runs_module
from ade_bench.cli.ab import tasks as tasks_module

app = typer.Typer(
    help="View ADE-bench results",
    invoke_without_command=True,
    no_args_is_help=False,
)


@app.callback()
def view_callback(ctx: typer.Context):
    """View ADE-bench results."""
    # If no subcommand, use the existing view_results logic
    if ctx.invoked_subcommand is None:
        from scripts_python.view_results import main as view_results_main
        view_results_main()


@app.command("run")
def view_run(
    run_id: Optional[str] = typer.Argument(
        None,
        help="Run ID to view. If not provided, opens the most recent run."
    ),
    output_path: Path = typer.Option(
        Path("experiments"),
        "--output-path",
        "-o",
        help="Path to the output directory"
    ),
):
    """
    View a specific run's results in your browser.

    If no run_id is provided, opens the most recent run.
    """
    # Reuse existing runs.open logic
    runs_module.open(run_id=run_id, output_path=output_path)


@app.command("runs")
def view_runs(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of runs to show"
    ),
    output_path: Path = typer.Option(
        Path("experiments"),
        "--output-path",
        "-o",
        help="Path to the output directory"
    ),
):
    """
    List recent benchmark runs.
    """
    # Reuse existing runs.list logic
    runs_module.list(limit=limit, output_path=output_path)


@app.command("tasks")
def view_tasks(
    tasks_dir: Path = typer.Option(
        Path("tasks"),
        "--tasks-dir",
        help="The path to the tasks directory."
    ),
    copy: bool = typer.Option(
        False,
        "--copy",
        help="Copy task details as TSV to clipboard"
    ),
):
    """List available tasks with their details and prompts."""
    # Reuse existing tasks.list logic
    tasks_module.list(tasks_dir=tasks_dir, copy=copy)
