#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add the project root to the sys path
sys.path.append(str(Path(__file__).parent.parent))

from ade_bench.harness_models import BenchmarkResults
from scripts_python.summarize_results import display_detailed_results
from scripts_python.utils import get_latest_experiment_with_results

# Find latest experiment with results
latest_experiment = get_latest_experiment_with_results()
if not latest_experiment:
    print("Error: No experiments with results found. Run some tests first.")
    sys.exit(1)

results_file = Path(latest_experiment) / "results.json"

print(f"Latest experiment: {Path(latest_experiment).name}")

# Load and display results
with open(results_file) as f:
    data = json.load(f)

results = BenchmarkResults(**data)
print(f"\nExperiment Results Summary ({Path(latest_experiment).name}):")
print("=" * 60)
display_detailed_results(results)