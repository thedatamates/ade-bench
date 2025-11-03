import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the sys path
sys.path.append(str(Path(__file__).parent.parent))

from ade_bench import Harness
from ade_bench.agents import AgentName
from scripts_python.summarize_results import display_detailed_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("experiments"),
        help="Path to the output directory",
    )

    parser.add_argument(
        "-t", "--tasks",
        type=str,
        nargs="+",
        required=True,
        help=("Task ID(s) to run. Use 'all' to run all tasks from the YAML configuration"),
    )

    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Don't rebuild Docker images",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Cleanup Docker containers and images after running the task",
    )
    parser.add_argument(
        "--agent",
        type=AgentName,
        choices=list(AgentName),
        default=AgentName.ORACLE,
        help="The agent to benchmark, defaults to oracle. "
        "Available agents: " + ", ".join([agent.value for agent in AgentName]) + ".",
    )
    parser.add_argument(
        "--log-level",
        type=lambda level: getattr(logging, level.upper(), logging.INFO),
        choices=logging._nameToLevel.values(),
        default=logging.INFO,
        help="Set the logging level. Available levels: "
        f"{', '.join([name.lower() for name in logging._nameToLevel.keys()])}",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        help="Unique identifier for this harness run",
        default=datetime.now().strftime("%Y-%m-%d__%H-%M-%S"),
    )
    parser.add_argument(
        "--model",
        type=str,
        help="The LLM model to use (e.g., claude-3-5-sonnet-20241022, gpt-4)",
        default=""
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        help="The maximum number of episodes (i.e. calls to an agent's LM).",
        default=50,
    )
    parser.add_argument(
        "--upload-results",
        action="store_true",
        help="Upload results to S3 bucket (bucket name is read from config)",
    )
    parser.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=4,
        help="Maximum number of tasks to run concurrently",
    )
    parser.add_argument(
        "--exclude-tasks",
        type=str,
        nargs="+",
        help=(
            "Task IDs to exclude from the run or path to a text file containing "
            "task IDs to exclude (one per line)"
        ),
        default=None,
    )
    parser.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Number of attempts to make for each task.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Extract specified tables as CSV files after harness run completes",
    )
    parser.add_argument(
        "--agent-args",
        type=str,
        help="Additional arguments to pass to the agent binary (e.g., '--verbose --debug')",
        default="",
    )
    parser.add_argument(
        "--no-diffs",
        action="store_true",
        help="Disable file diffing and HTML generation.",
    )
    parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Database type to filter variants (e.g., duckdb, postgres, sqlite, snowflake)",
    )
    parser.add_argument(
        "--project-type",
        type=str,
        required=True,
        help="Project type to filter variants (e.g., dbt, other)",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Keep containers alive when tasks fail for debugging",
    )
    parser.add_argument(
        "--use-mcp",
        action="store_true",
        help="Start a dbt MCP server after setup completes",
    )
    parser.add_argument(
        "--with-profiling",
        action="store_true",
        help="Run the harness with a python profiler",
    )
    parser.add_argument(
        "--plugins",
        type=str,
        default="",
        help="Comma-separated list of plugins to enable (e.g., 'superpowers,dbt-mcp')",
    )
    args = parser.parse_args()

    dataset_path = Path("tasks")
    task_ids = args.tasks

    if len(args.tasks) == 1 and args.tasks[0].lower() == "all":
        task_ids = None

    agent_kwargs = {}

    match args.agent:
        case AgentName.ORACLE:
            agent_kwargs["dataset_path"] = dataset_path
        case _:
            if args.agent_args:
                agent_kwargs["additional_args"] = args.agent_args

    # Parse plugins string into list
    enabled_plugins = [p.strip() for p in args.plugins.split(",") if p.strip()]

    harness = Harness(
        dataset_path=dataset_path,
        output_path=args.output_path,
        run_id=args.run_id,
        agent_name=args.agent,
        model_name=args.model,
        agent_kwargs=agent_kwargs,
        no_rebuild=args.no_rebuild,
        cleanup=args.cleanup,
        log_level=args.log_level,
        task_ids=task_ids,
        max_episodes=args.max_episodes,
        upload_results=args.upload_results,
        n_concurrent_trials=args.n_concurrent_trials,
        exclude_task_ids=set(args.exclude_tasks) if args.exclude_tasks else None,
        n_attempts=args.n_attempts,
        create_seed=args.seed,
        disable_diffs=args.no_diffs,
        db_type=args.db,
        project_type=args.project_type,
        keep_alive=args.persist,
        use_mcp=args.use_mcp,
        with_profiling=args.with_profiling,
        enabled_plugins=enabled_plugins,
    )

    results = harness.run()

    # Display results using the separate module
    display_detailed_results(results)
