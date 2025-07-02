#!/usr/bin/env python3
"""
Script to initialize a new task by copying template and associated files.
"""

import os
import sys
import shutil
import re
from pathlib import Path


def check_task_exists(task_name):
    """Check if task already exists in tasks directory."""
    tasks_dir = Path("tasks")
    task_path = tasks_dir / task_name
    
    if task_path.exists():
        print(f"Error: Task '{task_name}' already exists in the tasks directory.")
        return True
    return False


def find_spider_dbt_directory(base_name):
    """Find the spider-dbt directory that matches the base name (ignoring trailing numbers)."""
    spider_dbt_dir = Path("dev/spider-dbt")
    
    if not spider_dbt_dir.exists():
        print(f"Error: Spider-dbt directory not found at {spider_dbt_dir}")
        return None
    
    # Look for directories that start with the base name
    for item in spider_dbt_dir.iterdir():
        if item.is_dir():
            # Remove trailing numbers and compare
            dir_name = item.name
            # Use regex to remove trailing numbers
            base_dir_name = re.sub(r'\d+$', '', dir_name)
            if base_dir_name == base_name:
                return item
    
    print(f"Error: No spider-dbt directory found for base name '{base_name}'")
    return None


def copy_template_to_task(task_name):
    """Copy the .template directory and rename it to the task name."""
    template_dir = Path("tasks/.template")
    task_dir = Path("tasks") / task_name
    
    if not template_dir.exists():
        print(f"Error: Template directory not found at {template_dir}")
        return False
    
    try:
        # Copy the entire template directory
        shutil.copytree(template_dir, task_dir)
        print(f"✓ Copied template to tasks/{task_name}")
        return True
    except Exception as e:
        print(f"Error copying template: {e}")
        return False


def copy_spider_dbt_contents(spider_dbt_dir, task_name):
    """Copy contents of spider-dbt directory to dbt_project in the task."""
    task_dbt_project = Path("tasks") / task_name / "dbt_project"
    
    if not task_dbt_project.exists():
        print(f"Error: dbt_project directory not found at {task_dbt_project}")
        return False
    
    try:
        # Copy all contents from spider-dbt directory to dbt_project
        for item in spider_dbt_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, task_dbt_project)
            elif item.is_dir():
                shutil.copytree(item, task_dbt_project / item.name)
        
        print(f"✓ Copied spider-dbt contents to dbt_project")
        return True
    except Exception as e:
        print(f"Error copying spider-dbt contents: {e}")
        return False


def find_and_copy_duckdb_file(base_name):
    """Find the associated .duckdb file in source-dbs and copy it to shared/databases/duckdb."""
    source_dbs_dir = Path("dev/source-dbs")
    target_dir = Path("shared/databases/duckdb")
    
    if not source_dbs_dir.exists():
        print(f"Error: Source databases directory not found at {source_dbs_dir}")
        return False
    
    # Look for the .duckdb file in source-dbs
    duckdb_file = None
    for item in source_dbs_dir.iterdir():
        if item.is_dir():
            # Check if this directory matches the base name
            dir_name = item.name
            base_dir_name = re.sub(r'\d+$', '', dir_name)
            if base_dir_name == base_name:
                # Look for .duckdb file in this directory
                for file_item in item.iterdir():
                    if file_item.is_file() and file_item.suffix == '.duckdb':
                        duckdb_file = file_item
                        break
                if duckdb_file:
                    break
    
    if not duckdb_file:
        print(f"Error: No .duckdb file found for base name '{base_name}' in source-dbs")
        return False
    
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the file to shared/databases/duckdb
    target_file = target_dir / duckdb_file.name
    try:
        shutil.copy2(duckdb_file, target_file)
        print(f"✓ Copied {duckdb_file.name} to shared/databases/duckdb")
        return True
    except Exception as e:
        print(f"Error copying .duckdb file: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python init_task.py <task_name>")
        sys.exit(1)
    
    task_name = sys.argv[1]
    
    print(f"Initializing task: {task_name}")
    print("-" * 50)
    
    # Step 1: Check if task already exists
    if check_task_exists(task_name):
        sys.exit(1)
    
    # Step 2: Check if spider-dbt directory exists (ignoring trailing numbers)
    spider_dbt_dir = find_spider_dbt_directory(task_name)
    if not spider_dbt_dir:
        sys.exit(1)
    
    print(f"✓ Found spider-dbt directory: {spider_dbt_dir.name}")
    
    # Step 3: Copy template directory
    if not copy_template_to_task(task_name):
        sys.exit(1)
    
    # Step 4: Copy spider-dbt contents to dbt_project
    if not copy_spider_dbt_contents(spider_dbt_dir, task_name):
        sys.exit(1)
    
    # Step 5: Find and copy .duckdb file
    if not find_and_copy_duckdb_file(task_name):
        sys.exit(1)
    
    print("-" * 50)
    print(f"✓ Task '{task_name}' initialized successfully!")
    print(f"Task directory: tasks/{task_name}")


if __name__ == "__main__":
    main() 