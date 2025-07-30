#!/usr/bin/env python3
"""
Script to extract task details from all task.yaml files and generate a CSV.
"""

import os
import yaml
import pandas as pd
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any


def clean_text_for_spreadsheet(text: str) -> str:
    """Clean text for spreadsheet compatibility."""
    if not text:
        return ""
    # Remove line breaks and normalize whitespace
    cleaned = ' '.join(text.split())
    # Remove any control characters that might cause issues
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\t\n\r')
    return cleaned


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def extract_task_details(tasks_dir: Path) -> List[Dict[str, Any]]:
    """Extract details from all task.yaml files."""
    task_details = []
    
    # Iterate through all task directories
    for task_dir in tasks_dir.iterdir():
        if not task_dir.is_dir() or task_dir.name.startswith('.'):
            continue
            
        task_yaml_path = task_dir / "task.yaml"
        if not task_yaml_path.exists():
            print(f"Warning: No task.yaml found in {task_dir}")
            continue
            
        # Load task configuration
        task_config = load_yaml_file(task_yaml_path)
        if not task_config:
            continue
            
        # Extract basic task info
        task_id = clean_text_for_spreadsheet(task_config.get('task_id', ''))
        title = clean_text_for_spreadsheet(task_config.get('title', ''))
        status = clean_text_for_spreadsheet(task_config.get('status', ''))
        difficulty = clean_text_for_spreadsheet(task_config.get('difficulty', ''))
        category = clean_text_for_spreadsheet(task_config.get('category', ''))
        tags = task_config.get('tags', [])
        
        # Extract database info
        database_config = task_config.get('database', {})
        database_name = clean_text_for_spreadsheet(database_config.get('name', ''))
        
        # Extract project info
        project_config = task_config.get('project', {})
        project_name = clean_text_for_spreadsheet(project_config.get('name', ''))
        
        # Extract descriptions
        descriptions = task_config.get('descriptions', [])
        
        if not descriptions:
            # If no descriptions, create one row with empty key and description
            task_details.append({
                'task_id': task_id,
                'title': title,
                'status': status,
                'project_name': project_name,
                'database_name': database_name,
                'key': '',
                'description': '',
                'difficulty': difficulty,
                'category': category,
                'tags': clean_text_for_spreadsheet(', '.join(tags) if tags else '')
            })
        else:
            # Create one row per description key
            for desc in descriptions:
                key = clean_text_for_spreadsheet(desc.get('key', ''))
                description = clean_text_for_spreadsheet(desc.get('description', ''))
                
                task_details.append({
                    'task_id': task_id,
                    'title': title,
                    'status': status,
                    'project_name': project_name,
                    'database_name': database_name,
                    'key': key,
                    'description': description,
                    'difficulty': difficulty,
                    'category': category,
                    'tags': clean_text_for_spreadsheet(', '.join(tags) if tags else '')
                })
    
    return task_details


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using pbcopy (macOS) or xclip (Linux)."""
    try:
        if sys.platform == "darwin":  # macOS
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            return True
        elif sys.platform.startswith('linux'):  # Linux
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            return True
        else:
            print("Warning: Clipboard copy not supported on this platform")
            return False
    except Exception as e:
        print(f"Warning: Failed to copy to clipboard: {e}")
        return False


def main():
    """Main function to extract task details and generate CSV."""
    # Get the tasks directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tasks_dir = project_root / "tasks"
    
    if not tasks_dir.exists():
        print(f"Error: Tasks directory not found at {tasks_dir}")
        sys.exit(1)
    
    print(f"Extracting task details from {tasks_dir}...")
    
    # Extract task details
    task_details = extract_task_details(tasks_dir)
    
    if not task_details:
        print("No task details found!")
        sys.exit(1)
    
    # Create DataFrame
    df = pd.DataFrame(task_details)
    
    # Reorder columns as requested
    column_order = [
        'status',
        'task_id',
        'project_name',
        'database_name',
        'category',
        'key',
        'title',
        'description',
        'difficulty',
        'tags'
    ]
    
    df = df[column_order]
    
    # Sort by task_id and key
    df = df.sort_values(['task_id', 'key'])
    
    # Generate TSV for clipboard (better for Google Sheets)
    tsv_content = df.to_csv(index=False, sep='\t')
    
    # Print the CSV in a pretty format
    print("\n" + "="*80)
    print("TASK DETAILS")
    print("="*80)
    
    # Print header
    print(f"{'status':<8} | {'task_id':<25} | {'description':<60}")
    print("-" * 100)
    
    # Print data rows
    for _, row in df.iterrows():
        status = str(row['status'])[:7]
        task_id = str(row['task_id'])[:24]
        description = str(row['description'])[:59]
        print(f"{status:<8} | {task_id:<25} | {description:<60}")
    
    print("="*80)
    
    # Copy TSV to clipboard 
    if copy_to_clipboard(tsv_content):
        print("✓ TSV copied to clipboard!")
    else:
        print("✗ Failed to copy to clipboard")
    
    # Print summary
    print(f"\nSummary:")
    print(f"- Total tasks: {len(df['task_id'].unique())}")
    print(f"- Total rows: {len(df)}")
    print(f"- Categories: {', '.join(sorted(df['category'].unique()))}")
    print(f"- Difficulties: {', '.join(sorted(df['difficulty'].unique()))}")


if __name__ == "__main__":
    main() 