#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add the project root to the sys path
sys.path.append(str(Path(__file__).parent.parent))

from ade_bench.harness_models import BenchmarkResults
from scripts_python.display_results import display_detailed_results

# Find latest experiment
experiments_dir = Path(__file__).parent.parent / "experiments"
latest_experiment = sorted(experiments_dir.iterdir(), key=lambda x: x.name, reverse=True)[0]
print(f"Latest experiment: {latest_experiment.name}")

# Load and display results
with open(latest_experiment / "results.json") as f:
    data = json.load(f)

results = BenchmarkResults(**data)
print(f"\nExperiment Results Summary ({latest_experiment.name}):")
print("=" * 60)
display_detailed_results(results)