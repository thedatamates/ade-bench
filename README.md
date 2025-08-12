# ADE-Bench

A benchmarking framework for data analyst tasks using dbt and SQL.

## Overview

ADE-Bench (Analytics and Data Engineering Benchmark) is a framework for evaluating AI agents on data analyst tasks. It provides isolated dbt project environments with pre-configured databases (DuckDB/SQLite/PostgreSQL) and validates task completion through SQL queries.

## Installation

Fuck if I know.

## Usage

```bash
# Run the benchmark harness
uv run scripts_python/run_harness.py --agent claude-code --model-name claude-sonnet-4-20250514 --dataset-config datasets/ade-bench-core.yaml

# View logs of results
uv run scripts_python/view_logs.py

# Extract the details of all the tasks in the benchmark
uv run scripts_python/extract_task_details.py
```

## Task Structure

Each task contains:
- `task.yaml` - Task metadata and configuration
- `Dockerfile` - Container setup with dbt and database
- `tests/` - SQL validation queries
- `setup.sh` – A script that runs before the agent is given the task, for modifying files and source data.
- `solution.sh` – The oracle solution script that directly modifies files.
- `solutions/` – (Optional) Reference materials that are copied to `/solutions` in the container and can be used by setup.sh and solution.sh scripts.

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .
```