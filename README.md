# ADE-Bench

A benchmarking framework for data analyst tasks using dbt and SQL.

## Overview

ADE-Bench (Analytics and Data Engineering Benchmark) is a framework for evaluating AI agents on data analyst tasks. It provides isolated dbt project environments with pre-configured databases (DuckDB/SQLite/PostgreSQL) and validates task completion through SQL queries.

## Installation

```bash
uv sync
```

## Usage

```bash
# Run the benchmark harness
uv run scripts_python/run_harness.py --agent claude-code --model-name claude-sonnet-4-20250514 --dataset-config datasets/ade-bench-core.yaml

# Create a new task
uv run wizard
```

## Task Structure

Each task contains:
- `task.yaml` - Task metadata and configuration
- `Dockerfile` - Container setup with dbt and database
- `dbt_project/` - dbt project files
- `tests/` - SQL validation queries
- `expected/` - Expected query results

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