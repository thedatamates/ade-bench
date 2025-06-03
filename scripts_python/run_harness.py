#!/usr/bin/env python3
"""Main entry point for running ADE-Bench."""

import argparse
import logging
import sys
from pathlib import Path

from ade_bench.config import config
from ade_bench.harness import Harness


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run ADE-Bench benchmarks for data analyst tasks"
    )
    
    # Core arguments
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        help="Name of the agent to use (e.g., oracle, terminus)",
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        help="Model name for LLM-based agents (e.g., anthropic/claude-3-5-sonnet)",
    )
    
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=config.tasks_dir,
        help="Path to dataset directory (default: tasks/)",
    )
    
    parser.add_argument(
        "--dataset-config",
        type=Path,
        help="Path to dataset YAML configuration file",
    )
    
    parser.add_argument(
        "--output-path",
        type=Path,
        default=config.experiments_dir,
        help="Path to output directory (default: experiments/)",
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        help="Unique identifier for this run (auto-generated if not provided)",
    )
    
    # Task selection
    parser.add_argument(
        "--task-ids",
        type=str,
        nargs="+",
        help="Specific task IDs to run",
    )
    
    parser.add_argument(
        "--exclude-task-ids",
        type=str,
        nargs="+",
        help="Task IDs to exclude from the run",
    )
    
    parser.add_argument(
        "--n-tasks",
        type=int,
        help="Number of tasks to run (randomly selected if less than total)",
    )
    
    # Execution options
    parser.add_argument(
        "--n-concurrent-trials",
        type=int,
        default=4,
        help="Number of trials to run concurrently (default: 4)",
    )
    
    parser.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Number of attempts per task (default: 1)",
    )
    
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=50,
        help="Maximum number of agent interactions per task (default: 50)",
    )
    
    # Docker options
    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Skip rebuilding Docker images",
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove Docker images and volumes after run",
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )
    
    # Agent-specific arguments
    parser.add_argument(
        "--agent-kwargs",
        type=str,
        help="JSON string of additional agent arguments",
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Generate run ID if not provided
    if not args.run_id:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.run_id = f"{args.agent}_{timestamp}"
    
    # Parse agent kwargs if provided
    agent_kwargs = {}
    if args.agent_kwargs:
        import json
        try:
            agent_kwargs = json.loads(args.agent_kwargs)
        except json.JSONDecodeError as e:
            print(f"Error parsing agent-kwargs: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Convert exclude_task_ids to set
    exclude_task_ids = set(args.exclude_task_ids) if args.exclude_task_ids else None
    
    # Create and run harness
    harness = Harness(
        dataset_path=args.dataset_path,
        output_path=args.output_path,
        run_id=args.run_id,
        agent_name=args.agent,
        model_name=args.model_name,
        agent_kwargs=agent_kwargs,
        no_rebuild=args.no_rebuild,
        cleanup=args.cleanup,
        log_level=getattr(logging, args.log_level),
        task_ids=args.task_ids,
        n_tasks=args.n_tasks,
        max_episodes=args.max_episodes,
        n_concurrent_trials=args.n_concurrent_trials,
        exclude_task_ids=exclude_task_ids,
        n_attempts=args.n_attempts,
        dataset_config=args.dataset_config,
    )
    
    # Run the benchmark
    results = harness.run()
    
    # Exit with appropriate code
    if results.success_rate < 1.0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()