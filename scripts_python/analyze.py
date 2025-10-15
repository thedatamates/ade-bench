#!/usr/bin/env python3
"""
Analyze and merge experiment results from saved experiments.

This script:
1. Creates an "analysis" directory in dev
2. Merges all .tsv files from experiments_saved into a single TSV
3. Applies migrations to normalize column structure:
4. Extracts task details and saves to analysis directory
"""

import os
import csv
from pathlib import Path
from typing import Dict, List, Any


# =============================================================================
# MIGRATION CONFIGURATION
# =============================================================================
# Define how each experiment should be migrated.
# Add new experiments here with their specific settings.
EXPERIMENT_MIGRATIONS = {
    # These experiments had used_mcp: True in their TSVs, force to False
    '2025-10-13__23-26-56': {
        'used_mcp': False,
    },
    '2025-10-14__16-31-08': {
        'used_mcp': False,
    },
    '2025-10-15__08-38-38': {
        'model_name': 'claude-3-5-haiku-20241022',
    }
}

# Default migration settings for experiments not explicitly configured
DEFAULT_MIGRATION = {
    'used_mcp': False,
    'model_name': ''
}
# =============================================================================


def migrate_field(row: Dict[str, str], experiment_id: str, field_name: str) -> str:
    """
    Apply standard migration logic for a field.

    Args:
        row: The row data
        experiment_id: The experiment ID
        field_name: The field to migrate
    """

    if field_name not in row:
        # Set default
        return str(DEFAULT_MIGRATION.get(field_name, ''))
    elif experiment_id in EXPERIMENT_MIGRATIONS and field_name in EXPERIMENT_MIGRATIONS[experiment_id]:
        # Replace
        return str(EXPERIMENT_MIGRATIONS[experiment_id][field_name])
    else:
        # Use existing value
        return str(row[field_name])


def migrate_row(row: Dict[str, str], experiment_id: str) -> Dict[str, str]:
    """
    Apply migrations to normalize a row's structure based on experiment config.
    """
    migrated_row = row.copy()

    # Handle field migrations using the standard function
    migrated_row['used_mcp'] = migrate_field(row, experiment_id, 'used_mcp')
    migrated_row['model_name'] = migrate_field(row, experiment_id, 'model_name')

    # Remove old columns
    if 'result_num' in migrated_row:
        del migrated_row['result_num']

    return migrated_row


def get_canonical_column_order() -> List[str]:
    """
    Define the canonical column order for the merged TSV.
    """
    return [
        'experiment_id',
        'task_id',
        'result',
        'failure_type',
        'tests',
        'passed',
        'passed_percentage',
        'time_seconds',
        'cost',
        'input_tokens',
        'output_tokens',
        'cache_tokens',
        'turns',
        'agent',
        'model_name',
        'db_type',
        'project_type',
        'used_mcp'
    ]


def merge_experiment_results(
    experiments_dir: Path,
    output_file: Path
) -> None:
    """
    Merge all results.tsv files from saved experiments into a single TSV.

    Args:
        experiments_dir: Path to the experiments_saved directory
        output_file: Path to the output merged TSV file
    """
    all_rows = []
    canonical_columns = get_canonical_column_order()

    # Find all results.tsv files in subdirectories
    tsv_files = sorted(experiments_dir.glob('*/results.tsv'))

    if not tsv_files:
        print(f"No results.tsv files found in {experiments_dir}")
        return

    print(f"Found {len(tsv_files)} experiment result files:")
    for tsv_file in tsv_files:
        print(f"  - {tsv_file.parent.name}/results.tsv")

    # Read and migrate each TSV file
    for tsv_file in tsv_files:
        experiment_id = tsv_file.parent.name
        print(f"Processing {experiment_id}...")

        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            rows = list(reader)

            print(f"  - Read {len(rows)} rows")

            # Apply migrations to each row with the experiment_id
            migrated_rows = [migrate_row(row, experiment_id) for row in rows]
            all_rows.extend(migrated_rows)


    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=canonical_columns,
            delimiter='\t',
            extrasaction='ignore'
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Successfully wrote merged results to {output_file}")
    print(f"  - Total rows: {len(all_rows)}")


def extract_and_save_tasks(output_file: Path) -> None:
    """
    Extract task details from task.yaml files and save to TSV.
    Calls the extract_task_details script to do the work.

    Args:
        output_file: Path to the output TSV file
    """
    try:
        from extract_task_details import main as extract_main
        extract_main(output_file=output_file, quiet=False)
    except ImportError as e:
        print(f"Warning: Could not import extract_task_details: {e}")
    except Exception as e:
        print(f"Warning: Failed to extract task details: {e}")


def main():
    """Main entry point."""
    # Get project root directory (one level up from scripts_python)
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent

    # Define paths
    dev_dir = project_root / 'dev'
    analysis_dir = dev_dir / 'analysis'
    experiments_saved_dir = project_root / 'experiments_saved'
    merged_results_file = analysis_dir / 'merged_results.tsv'
    tasks_file = analysis_dir / 'tasks.tsv'

    # Step 1: Create analysis directory
    print("STARTING...")
    analysis_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created {analysis_dir}")

    # Step 2: Merge all TSV files
    if not experiments_saved_dir.exists():
        print(f"Error: {experiments_saved_dir} does not exist")
        return

    merge_experiment_results(experiments_saved_dir, merged_results_file)

    # Step 3: Extract and save task details
    extract_and_save_tasks(tasks_file)

    print(f"Merged results available at: {merged_results_file}")
    print(f"Task details available at: {tasks_file}")
    print("COMPLETE.")


if __name__ == '__main__':
    main()

