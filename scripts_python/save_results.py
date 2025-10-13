#!/usr/bin/env python3
"""Save the most recent experiment to experiments_saved directory."""

import shutil
import sys
from pathlib import Path

# Add the project root to the sys path
sys.path.append(str(Path(__file__).parent.parent))

from scripts_python.utils import get_latest_experiment_with_results


def main():
    """Copy the most recent experiment to experiments_saved."""
    # Find the latest experiment
    latest_experiment = get_latest_experiment_with_results()

    if not latest_experiment:
        print("Error: No experiments with results found.")
        sys.exit(1)

    # Create experiments_saved directory if it doesn't exist
    saved_dir = Path("experiments_saved")
    saved_dir.mkdir(exist_ok=True)

    # Get the experiment directory name
    exp_path = Path(latest_experiment)
    exp_name = exp_path.name

    # Destination path
    dest_path = saved_dir / exp_name

    # Check if it already exists
    if dest_path.exists():
        response = input(f"{exp_name} already exists in experiments_saved. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
        # Remove existing directory
        shutil.rmtree(dest_path)

    # Copy the experiment
    print(f"Copying {exp_name} to experiments_saved/...")
    shutil.copytree(exp_path, dest_path)
    print(f"✓ Saved to {dest_path}")


if __name__ == "__main__":
    main()

