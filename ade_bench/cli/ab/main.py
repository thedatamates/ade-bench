"""Main entry point for the ADE-bench CLI."""

import typer
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Set

import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ade_bench import Harness
from ade_bench.agents import AgentName
from scripts_python.summarize_results import display_detailed_results

from ade_bench.cli.ab import runs, migrate, tasks

app = typer.Typer(help="ADE-bench: Analytics and Data Engineering Benchmark")


@app.command()
def run(
    tasks: List[str] = typer.Argument(
        ...,
        help="Task ID(s) to run. Use 'all' to run all ready tasks, '@experiment_set' to run an experiment set, 'task+' for wildcards"
    ),
    db: str = typer.Option(
        ...,
        "--db",
        help="Database type to filter variants (e.g., duckdb, postgres, sqlite, snowflake)"
    ),
    project_type: str = typer.Option(
        ...,
        "--project-type",
        help="Project type to filter variants (e.g., dbt, other)"
    ),
    output_path: Path = typer.Option(
        Path("experiments"),
        "--output-path",
        "-o",
        help="Path to the output directory"
    ),
    agent: str = typer.Option(
        "oracle",
        "--agent",
        case_sensitive=False,
        help="The agent to benchmark (e.g., oracle, claude, macro)"
    ),
    model_name: str = typer.Option(
        "",
        "--model",
        help="The LLM model to use (e.g., claude-3-5-sonnet-20241022, gpt-4)"
    ),
    no_rebuild: bool = typer.Option(
        False,
        "--no-rebuild",
        help="Don't rebuild Docker images"
    ),
    cleanup: bool = typer.Option(
        False,
        "--cleanup",
        help="Cleanup Docker containers and images after running the task"
    ),
    n_concurrent_trials: int = typer.Option(
        4,
        "--n-concurrent-trials",
        help="Maximum number of tasks to run concurrently"
    ),
    exclude_tasks: Optional[List[str]] = typer.Option(
        None,
        "--exclude-tasks",
        help="Task IDs to exclude from the run"
    ),
    n_attempts: int = typer.Option(
        1,
        "--n-attempts",
        help="Number of attempts to make for each task"
    ),
    seed: bool = typer.Option(
        False,
        "--seed",
        help="Extract specified tables as CSV files after harness run completes"
    ),
    agent_args: str = typer.Option(
        "",
        "--agent-args",
        help="Additional arguments to pass to the agent binary (e.g., '--verbose --debug')"
    ),
    no_diffs: bool = typer.Option(
        False,
        "--no-diffs",
        help="Disable file diffing and HTML generation"
    ),
    persist: bool = typer.Option(
        False,
        "--persist",
        help="Keep containers alive when tasks fail for debugging"
    ),
    run_id: str = typer.Option(
        datetime.now().strftime("%Y-%m-%d__%H-%M-%S"),
        "--run-id",
        help="Unique identifier for this harness run"
    ),
    max_episodes: int = typer.Option(
        50,
        "--max-episodes",
        help="The maximum number of episodes (i.e. calls to an agent's LM)"
    ),
    upload_results: bool = typer.Option(
        False,
        "--upload-results",
        help="Upload results to S3 bucket (bucket name is read from config)"
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        help="Set the logging level"
    ),
    with_profiling: bool = typer.Option(
        False,
        "--with-profiling",
        help="Run the harness with a python profiler",
    plugins: str = typer.Option(
        "",
        "--plugins",
        help="Comma-separated list of plugins to enable (e.g., 'superpowers,dbt-mcp')"
    )
):
    """
    Run ADE-bench with specified tasks and configuration.

    Example:
    ab run airbnb001 --db duckdb --project-type dbt --agent oracle
    """
    # Convert log level string to int
    log_level_int = getattr(logging, log_level.upper(), logging.INFO)

    # Check for common mistakes in task_ids that look like flags
    flag_looking_args = [task for task in tasks if task.startswith("run-id") or task.startswith("--")]
    if flag_looking_args:
        typer.echo(f"Warning: Some task IDs look like they might be flags: {', '.join(flag_looking_args)}")
        typer.echo("If you meant to use these as options, make sure to use '--option value' format.")
        if not typer.confirm("Continue anyway?"):
            typer.echo("Aborting.")
            raise typer.Exit(code=1)

    # Convert agent string to AgentName enum
    try:
        agent_name = AgentName(agent.lower())
    except ValueError:
        typer.echo(f"Error: Invalid agent name '{agent}'")
        typer.echo(f"Available agents: {', '.join([a.value for a in AgentName])}")
        raise typer.Exit(code=1)

    # Setup path variables
    dataset_path = Path("tasks")
    task_ids = tasks

    if len(tasks) == 1 and tasks[0].lower() == "all":
        task_ids = None

    agent_kwargs = {}

    if agent_name == AgentName.ORACLE:
        agent_kwargs["dataset_path"] = dataset_path
    elif agent_args:
        agent_kwargs["additional_args"] = agent_args

    # Parse plugins
    enabled_plugins = [p.strip() for p in plugins.split(",") if p.strip()]

    # Create and run the harness
    harness = Harness(
        dataset_path=dataset_path,
        output_path=output_path,
        run_id=run_id,
        agent_name=agent_name,
        model_name=model_name,
        agent_kwargs=agent_kwargs,
        no_rebuild=no_rebuild,
        cleanup=cleanup,
        log_level=log_level_int,
        task_ids=task_ids,
        max_episodes=max_episodes,
        upload_results=upload_results,
        n_concurrent_trials=n_concurrent_trials,
        exclude_task_ids=set(exclude_tasks) if exclude_tasks else None,
        n_attempts=n_attempts,
        create_seed=seed,
        disable_diffs=no_diffs,
        db_type=db,
        project_type=project_type,
        keep_alive=persist,
        with_profiling=with_profiling,
        enabled_plugins=enabled_plugins,
    )

    results = harness.run()
    display_detailed_results(results)


@app.command()
def view():
    """
    View the results of previous benchmark runs.

    Opens the results HTML viewer in your default browser.
    """
    from scripts_python.view_results import main as view_results_main
    view_results_main()


if __name__ == "__main__":
    app()

# Add sub-commands
app.add_typer(runs.app, name="runs")
app.add_typer(migrate.app, name="migrate")
app.add_typer(tasks.tasks_app, name="tasks", help="Manage ADE-bench tasks")
