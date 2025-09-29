#! /bin/bash
# remove any existing singular tests and add solution tests
rm -rf tests
mkdir tests

# Parse arguments
for arg in "$@"; do
    case $arg in
        --db-type=*) db_type="${arg#*=}" ;;
        --project-type=*) project_type="${arg#*=}" ;;
    esac
done

echo "Filtering for db_type='$db_type', project_type='$project_type'"

# Copy files with filtering
for file in /tests/*; do
    [[ -f "$file" ]] || continue

    # Non-SQL files: always include
    if [[ ! "$file" =~ \.sql$ ]]; then
        cp "$file" tests/
        continue
    fi

    # SQL files: apply filtering
    include=true

    # Check db specification
    if [[ -n "$db_type" ]] && grep -q "^-- *db:" "$file"; then
        if ! grep -q "^-- *db:.*$db_type" "$file"; then
            include=false
        fi
    fi

    # Check project-type specification
    if [[ -n "$project_type" ]] && grep -q "^-- *project-type:" "$file"; then
        if ! grep -q "^-- *project-type:.*$project_type" "$file"; then
            include=false
        fi
    fi

    if [[ "$include" == true ]]; then
        echo "Including: $(basename "$file")"
        cp "$file" tests/
    else
        echo "Excluding: $(basename "$file")"
    fi
done

# Run test setup script if it exists
if [ -f "tests/test-setup.sh" ]; then
    bash tests/test-setup.sh
fi

# Setup seeds and convert schema if needed
if [ -d "/seeds" ]; then
    mkdir -p seeds
    cp /seeds/* seeds/

    bash tests/seed-schema.sh

    dbt seed
fi

# run dbt data tests for evaluation
dbt test --select "test_type:singular"