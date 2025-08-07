#!/usr/bin/env python3
"""
Script to create a sandbox environment from a task.
"""

import os
import sys
import shutil
import yaml
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


def get_task_config(task_name):
    """Get the task configuration from task.yaml."""
    task_yaml_path = Path("tasks") / task_name / "task.yaml"
    
    if not task_yaml_path.exists():
        print(f"Error: task.yaml not found for task '{task_name}'")
        return None
    
    try:
        with open(task_yaml_path, 'r') as f:
            task_data = yaml.safe_load(f)
        
        return task_data
    except Exception as e:
        print(f"Error reading task.yaml: {e}")
        return None


def copy_item(source_path, dest_path, item_name, create_dest_dir=False):
    """Generic function to copy files or directories."""
    if not source_path.exists():
        print(f"Warning: {item_name} not found at {source_path}")
        return True
    
    try:
        if create_dest_dir:
            dest_path.mkdir(parents=True, exist_ok=True)
        
        if source_path.is_file():
            shutil.copy2(source_path, dest_path)
        elif source_path.is_dir():
            if dest_path.exists():
                # Copy contents into existing directory
                for item in source_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, dest_path)
                    elif item.is_dir():
                        shutil.copytree(item, dest_path / item.name)
            else:
                # Copy entire directory
                shutil.copytree(source_path, dest_path)
        
        print(f"✓ Copied {item_name} to sandbox")
        return True
    except Exception as e:
        print(f"Error copying {item_name}: {e}")
        return False


def copy_project_contents(task_name):
    """Copy shared project contents to sandbox."""
    project_config = get_project_config(task_name)
    if not project_config:
        return False
    
    project_name = project_config['name']
    shared_project_dir = Path("shared/projects/dbt") / project_name
    
    if not shared_project_dir.exists():
        print(f"Error: Shared project directory '{shared_project_dir}' not found")
        return False
    
    sandbox_dir = Path("dev/sandbox")
    return copy_item(shared_project_dir, sandbox_dir, f"project '{project_name}'")


def get_project_config(task_name):
    """Get the project configuration from task.yaml."""
    task_data = get_task_config(task_name)
    if not task_data:
        return None
    
    # Check if project configuration exists
    if 'project' not in task_data:
        print(f"Error: No project configuration found in task '{task_name}'")
        return None
    
    project_config = task_data['project']
    
    # Validate project configuration
    if project_config.get('source') != 'shared':
        print(f"Error: Task '{task_name}' does not use a shared project")
        return None
    
    if 'name' not in project_config:
        print(f"Error: No project name specified in task '{task_name}'")
        return None
    
    return project_config


def get_database_config(task_name):
    """Get the database configuration from task.yaml."""
    task_data = get_task_config(task_name)
    if not task_data:
        return None
    
    # Check if database configuration exists
    if 'database' not in task_data:
        print(f"Error: No database configuration found in task '{task_name}'")
        return None
    
    database_config = task_data['database']
    
    # Validate database configuration
    if database_config.get('source') != 'shared':
        print(f"Error: Task '{task_name}' does not use a shared database")
        return None
    
    if 'name' not in database_config:
        print(f"Error: No database name specified in task '{task_name}'")
        return None
    
    return database_config


def copy_database_file(task_name):
    """Copy the database file to sandbox."""
    database_config = get_database_config(task_name)
    if not database_config:
        return False
    
    database_name = database_config['name']
    duckdb_dir = Path("shared/databases/duckdb")
    sandbox_dir = Path("dev/sandbox")
    
    # Look for the .duckdb file with the database name from task config
    duckdb_file = duckdb_dir / f"{database_name}.duckdb"
    
    if not duckdb_file.exists():
        print(f"Error: DuckDB file '{database_name}.duckdb' not found in shared/databases/duckdb")
        return False
    
    return copy_item(duckdb_file, sandbox_dir, f"database '{database_name}.duckdb'")


def copy_task_files(task_name):
    """Copy various task files to sandbox."""
    task_dir = Path("tasks") / task_name
    sandbox_dir = Path("dev/sandbox")
    
    # Define what to copy
    items_to_copy = [
        (task_dir / "setup.sh", sandbox_dir, "setup.sh"),
        (task_dir / "solution.sh", sandbox_dir, "solution.sh"),
        (task_dir / "seeds", sandbox_dir / "seeds", "seeds directory"),
        (task_dir / "tests", sandbox_dir / "tests", "tests directory"),
    ]
    
    success = True
    for source, dest, name in items_to_copy:
        if not copy_item(source, dest, name, create_dest_dir=(name.endswith("directory"))):
            success = False
    
    return success


def copy_shared_scripts():
    """Copy shared scripts to sandbox."""
    script_path = Path("shared/scripts/seed-schema.sh")
    sandbox_dir = Path("dev/sandbox")
    
    return copy_item(script_path, sandbox_dir, "seed-schema.sh script")


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
    
    # Step 3: Copy shared project contents
    if not copy_project_contents(task_name):
        sys.exit(1)
    
    # Step 4: Copy database file
    if not copy_database_file(task_name):
        sys.exit(1)
    
    # Step 5: Copy task files (scripts, seeds, tests)
    if not copy_task_files(task_name):
        sys.exit(1)
    
    # Step 6: Copy shared scripts
    if not copy_shared_scripts():
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