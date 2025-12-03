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
ade run airbnb001 --db duckdb --project-type dbt --agent oracle

# Run a specific task with a specific variant
ade run f1006.hard --db duckdb --project-type dbt --agent oracle

# Run multiple tasks
ade run airbnb001 airbnb002 --db duckdb --project-type dbt --agent oracle

# Run all ready tasks
ade run all --db duckdb --project-type dbt --agent oracle

# Run an experiment set
ade run @coalesce --db duckdb --project-type dbt --agent oracle

# Run wildcard patterns
ade run f1+ simple+ --db duckdb --project-type dbt --agent oracle

# Note: All options require double-dashes (--option value), NOT single-dash or no dash
# CORRECT:    --run-id test-run-001
# INCORRECT:  run-id test-run-001 (will be treated as task IDs)
```

### View Results

View the results of your benchmark runs:

```bash
# Open the most recent run results in your browser
ade view

# List recent runs
ade view runs

# View a specific run
ade view run 2025-10-07__11-45-04

# List all available tasks with their prompts
ade view tasks

# Copy task details as TSV to clipboard
ade view tasks --copy
```

### Interactive Mode

Launch an interactive shell into a task environment:

```bash
# Launch an interactive shell into a task
ade interact --task-id airbnb001 --db duckdb --project-type dbt

# Include solution and test files in the interactive environment
ade interact --task-id airbnb001 --db duckdb --project-type dbt --include-all

# Set up a specific agent for testing (in a tmux session)
ade interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude

# Run the agent on a task and then drop into interactive mode
ade interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude --step post-agent

# Run the agent, evaluate the results, and then drop into interactive mode
ade interact --task-id airbnb001 --db duckdb --project-type dbt --agent claude --step post-eval

# Specify a run ID for the output directory
ade interact --task-id airbnb001 --db duckdb --project-type dbt --run-id debug-session
```

### Save Results

Save benchmark runs to the `experiments_saved` directory:

```bash
# Save the most recent run
ade save

# Same as above
ade save run

# Save a specific run
ade save run 2025-10-07__11-45-04

# Force overwrite without prompting
ade save run --force
```

### Database Migration

Migrate DuckDB databases to Snowflake:

```bash
# Migrate all DuckDB databases to Snowflake
ade migrate duckdb-to-snowflake

# Migrate specific databases only
ade migrate duckdb-to-snowflake --include airbnb analytics_engineering

# Exclude specific databases
ade migrate duckdb-to-snowflake --exclude quickbooks

# Use database export for better performance
ade migrate duckdb-to-snowflake --use-database-export
```

## Command Help

For detailed help on any command, use the `--help` flag:

```bash
ade --help
ade run --help
ade view --help
ade save --help
ade interact --help
ade migrate --help
```
