# ADE-Bench

A benchmarking framework for data analyst tasks using dbt and SQL.

## Overview

ADE-Bench (Analytics and Data Engineering Benchmark) is a framework for evaluating AI agents on data analyst tasks. It provides isolated dbt project environments with pre-configured databases (DuckDB/SQLite/PostgreSQL) and validates task completion through SQL queries.

## Installation

Fuck if I know.

## Configuration

ADE-Bench uses environment variables for configuration. You can set these values directly in your `.env` file or as environment variables:

```bash
# Create .env file with timeout settings
cat > .env << 'EOF'
# Timeout Settings (in seconds)
SETUP_TIMEOUT_SEC=120
DEFAULT_AGENT_TIMEOUT_SEC=180
DEFAULT_TEST_TIMEOUT_SEC=30
CLEANUP_TIMEOUT_SEC=30

# AWS Settings
AWS_REGION=us-west-2
S3_BUCKET_NAME=

# Database Settings
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
EOF
```

### Timeout Configuration

The following timeout values can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SETUP_TIMEOUT_SEC` | 120 | Timeout for setup scripts (seconds) |
| `DEFAULT_AGENT_TIMEOUT_SEC` | 180 | Default timeout for agent execution (seconds) |
| `DEFAULT_TEST_TIMEOUT_SEC` | 30 | Default timeout for test execution (seconds) |
| `CLEANUP_TIMEOUT_SEC` | 30 | Timeout for cleanup operations (seconds) |

### Example Configuration

You can set these values in your `.env` file or as environment variables:

```bash
# For faster iteration during development
export SETUP_TIMEOUT_SEC=60
export DEFAULT_AGENT_TIMEOUT_SEC=120
export DEFAULT_TEST_TIMEOUT_SEC=20

# For production runs with longer timeouts
export SETUP_TIMEOUT_SEC=300
export DEFAULT_AGENT_TIMEOUT_SEC=600
export DEFAULT_TEST_TIMEOUT_SEC=120
```

Or create a `.env` file with these values:
```bash
# .env file
SETUP_TIMEOUT_SEC=60
DEFAULT_AGENT_TIMEOUT_SEC=120
DEFAULT_TEST_TIMEOUT_SEC=20
```

### Overriding Timeouts for Specific Tasks

You can also override timeout values for individual tasks by adding them to the task's `task.yaml` file:

```yaml
# In tasks/my_task/task.yaml
max_agent_timeout_sec: 300.0  # Override default agent timeout
max_test_timeout_sec: 60.0    # Override default test timeout
```

## Usage

```bash
# Run the benchmark harness
uv run scripts_python/run_harness.py --agent claude-code --model-name claude-sonnet-4-20250514 --dataset-config datasets/ade-bench-core.yaml


```

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
- `setup/` – (Optional) Directory containing files that are copied to the container before setup.sh runs. These files can be used by the setup script for file manipulation, copying, or as templates. The setup directory is automatically cleaned up after the setup script completes.
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