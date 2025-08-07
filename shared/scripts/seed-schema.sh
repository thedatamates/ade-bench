#! /bin/bash

# Append _no-op.txt to dbt_project.yml if it exists
if [ -f "seeds/_no-op.txt" ]; then
    echo "Appending schema to dbt_project.yml..."
    
    # Find dbt_project.yml
    dbt_project_path=""
    if [ -f "dbt_project/dbt_project.yml" ]; then
        dbt_project_path="dbt_project/dbt_project.yml"
    elif [ -f "dbt_project.yml" ]; then
        dbt_project_path="dbt_project.yml"
    fi
    
    if [ -n "$dbt_project_path" ]; then
        # Append _no-op.txt content to dbt_project.yml
        cat "seeds/_no-op.txt" >> "$dbt_project_path"
        echo "Appended schema to $dbt_project_path"
    else
        echo "Warning: dbt_project.yml not found"
    fi
fi