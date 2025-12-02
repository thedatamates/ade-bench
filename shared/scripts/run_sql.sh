#!/bin/bash
# Bash wrapper for run_sql.py utility
# This makes it easier to use from setup.sh and solution.sh scripts

# Find the run_sql.py script
if [ -f "/scripts/run_sql.py" ]; then
    RUN_SQL="/scripts/run_sql.py"
elif [ -f "./run_sql.py" ]; then
    RUN_SQL="./run_sql.py"
elif [ -f "$(dirname "$0")/run_sql.py" ]; then
    RUN_SQL="$(dirname "$0")/run_sql.py"
else
    echo "Error: run_sql.py not found" >&2
    exit 1
fi

# Extract db-type and project-type from command line arguments or use defaults
DB_TYPE="duckdb"  # default
PROJECT_TYPE="dbt"  # default

for arg in "$@"; do
    if [[ "$arg" == --db-type=* ]]; then
        DB_TYPE="${arg#*=}"
    elif [[ "$arg" == --project-type=* ]]; then
        PROJECT_TYPE="${arg#*=}"
    fi
done

# Execute the Python script with all arguments
exec python3 "$RUN_SQL" --db-type="$DB_TYPE" --project-type="$PROJECT_TYPE" "$@"

