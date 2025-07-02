#!/usr/bin/env python3
"""
Script to create a sandbox environment from a task.
"""

import os
import sys
import shutil
from pathlib import Path


def check_task_exists(task_name):
    """Check if task exists in tasks directory."""
    tasks_dir = Path("tasks")
    task_path = tasks_dir / task_name
    
    if not task_path.exists():
        print(f"Error: Task '{task_name}' does not exist in the tasks directory.")
        return False
    
    if not task_path.is_dir():
        print(f"Error: '{task_name}' exists but is not a directory.")
        return False
    
    return True


def wipe_sandbox_directory():
    """Wipe the contents of the sandbox directory."""
    sandbox_dir = Path("dev/sandbox")
    
    if not sandbox_dir.exists():
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created sandbox directory at {sandbox_dir}")
        return True
    
    try:
        # Remove all contents of the sandbox directory
        for item in sandbox_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        
        print(f"✓ Wiped contents of sandbox directory")
        return True
    except Exception as e:
        print(f"Error wiping sandbox directory: {e}")
        return False


def copy_dbt_project_contents(task_name):
    """Copy the contents of the dbt_project directory from the task to sandbox."""
    task_dbt_project = Path("tasks") / task_name / "dbt_project"
    sandbox_dir = Path("dev/sandbox")
    
    if not task_dbt_project.exists():
        print(f"Error: dbt_project directory not found in task '{task_name}'")
        return False
    
    try:
        # Copy all contents from task's dbt_project to sandbox
        for item in task_dbt_project.iterdir():
            if item.is_file():
                shutil.copy2(item, sandbox_dir)
            elif item.is_dir():
                shutil.copytree(item, sandbox_dir / item.name)
        
        print(f"✓ Copied dbt_project contents to sandbox")
        return True
    except Exception as e:
        print(f"Error copying dbt_project contents: {e}")
        return False


def find_and_copy_duckdb_file(task_name):
    """Find the associated DuckDB file in shared/databases/duckdb and copy it to sandbox."""
    duckdb_dir = Path("shared/databases/duckdb")
    sandbox_dir = Path("dev/sandbox")
    
    if not duckdb_dir.exists():
        print(f"Error: DuckDB directory not found at {duckdb_dir}")
        return False
    
    # Look for the .duckdb file with the same name as the task
    duckdb_file = duckdb_dir / f"{task_name}.duckdb"
    
    if not duckdb_file.exists():
        print(f"Error: DuckDB file '{task_name}.duckdb' not found in shared/databases/duckdb")
        return False
    
    try:
        # Copy the file to sandbox
        shutil.copy2(duckdb_file, sandbox_dir)
        print(f"✓ Copied {duckdb_file.name} to sandbox")
        return True
    except Exception as e:
        print(f"Error copying DuckDB file: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python create_sandbox.py <task_name>")
        sys.exit(1)
    
    task_name = sys.argv[1]
    
    print(f"Creating sandbox for task: {task_name}")
    print("-" * 50)
    
    # Step 1: Check if task exists
    if not check_task_exists(task_name):
        sys.exit(1)
    
    print(f"✓ Task '{task_name}' found")
    
    # Step 2: Wipe sandbox directory
    if not wipe_sandbox_directory():
        sys.exit(1)
    
    # Step 3: Copy dbt_project contents only
    if not copy_dbt_project_contents(task_name):
        sys.exit(1)
    
    # Step 4: Find and copy DuckDB file
    if not find_and_copy_duckdb_file(task_name):
        sys.exit(1)
    
    print("-" * 50)
    print(f"✓ Sandbox created successfully for task '{task_name}'!")
    
    # Get the absolute path to the sandbox directory
    sandbox_dir = Path("dev/sandbox").absolute()
    print(f"Sandbox location: {sandbox_dir}")
    print(f"\nTo change to the sandbox directory, run:")
    print(f"cd {sandbox_dir}")


if __name__ == "__main__":
    main() 