# ADE-bench CLI

The `ab` command line interface provides an easy way to run ADE-bench tasks and manage benchmark runs.

## Installation

ADE-bench CLI is installed when you install the ADE-bench package. You can also use the wrapper script directly from the repository:

```bash
# install local package from root of project
pip install -e .

# after installing the package
ade-bench --help
ade --help  # Shorthand alias
```

## Commands

### Run Benchmarks

Run ADE-bench tasks with specific configurations:

```bash
# Run a specific task
ab run airbnb001 --db duckdb --project-type dbt --agent oracle

# Run multiple tasks
ab run airbnb001 airbnb002 --db duckdb --project-type dbt --agent oracle

# Run all tasks
ab run all --db duckdb --project-type dbt --agent oracle

# Run with a specific run ID for tracking
ab run airbnb001 --db duckdb --project-type dbt --agent oracle --run-id my-experiment-001

# Note: All options require double-dashes (--option value), NOT single-dash or no dash
# CORRECT:    --run-id test-run-001
# INCORRECT:  run-id test-run-001 (will be treated as task IDs)
```

### View Results

View the results of your benchmark runs:

```bash
# Open the most recent run results in your browser
ab view

# List recent runs
ab runs list

# Open a specific run
ab runs open 2025-10-07__11-45-04
```

### Task Management

Interact with individual tasks:

```bash
# List all available tasks with their supported variants
ab tasks list

# Launch an interactive shell into a task
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt

# Include solution and test files in the interactive environment
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt --include-all

# Set up a specific agent for testing (in a tmux session)
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude-code

# Run the agent on a task and then drop into interactive mode
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude-code --step post-agent

# Run the agent, evaluate the results, and then drop into interactive mode
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude-code --step post-eval

# Specify a run ID for the output directory
ab tasks interact --task-id airbnb001 --db duckdb --project-type dbt --run-id debug-session
```

### Database Migration

Migrate DuckDB databases to Snowflake:

```bash
# Migrate all DuckDB databases to Snowflake
ab migrate duckdb-to-snowflake

# Migrate specific databases only
ab migrate duckdb-to-snowflake --include airbnb analytics_engineering

# Exclude specific databases
ab migrate duckdb-to-snowflake --exclude quickbooks

# Use database export for better performance
ab migrate duckdb-to-snowflake --use-database-export
```

## Command Help

For detailed help on any command, use the `--help` flag:

```bash
ab --help
ab run --help
ab runs --help
ab migrate --help
```