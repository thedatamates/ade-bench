#! /bin/bash

# Check if _no-op.txt exists
if [ ! -f "seeds/_no-op.txt" ]; then
    exit 0
fi

echo "Merging schema into dbt_project.yml..."

# Find dbt_project.yml
if [ -f "dbt_project/dbt_project.yml" ]; then
    dbt_project_path="dbt_project/dbt_project.yml"
elif [ -f "dbt_project.yml" ]; then
    dbt_project_path="dbt_project.yml"
else
    echo "Warning: dbt_project.yml not found"
    exit 0
fi

# Find merge_yaml.py script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/merge_yaml.py" ]; then
    merge_script="$SCRIPT_DIR/merge_yaml.py"
elif [ -f "./merge_yaml.py" ]; then
    merge_script="./merge_yaml.py"
elif [ -f "/scripts/merge_yaml.py" ]; then
    merge_script="/scripts/merge_yaml.py"
else
    echo "Error: merge_yaml.py not found"
    exit 1
fi

# Create temporary file for merged output
temp_file=$(mktemp)

# Merge using Python script
python3 "$merge_script" "$dbt_project_path" "seeds/_no-op.txt" "$temp_file"

# Replace original file with merged version
mv "$temp_file" "$dbt_project_path"

echo "Merged schema into $dbt_project_path"