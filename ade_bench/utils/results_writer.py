"""TSV results writer for real-time experiment tracking."""

import csv
from pathlib import Path
from typing import Dict

from ade_bench.harness_models import TrialResults
from ade_bench.agents.agent_name import AgentName


def format_trial_result(result: TrialResults) -> Dict[str, any]:
    """
    Format a single trial result with calculated statistics.

    This is a shared utility used by both the TSV writer and summarize_results.

    Args:
        trial_result: The trial result to format

    Returns:
        Dictionary with formatted values and raw numeric values
    """
    # Calculate test statistics
    if result.parser_results:
        tests = len(result.parser_results)
        tests_passed = sum(1 for status in result.parser_results.values() if status.value == "passed")
        passed_percentage = (tests_passed / tests * 100) if tests > 0 else 0
    else:
        tests = 0
        tests_passed = 0
        passed_percentage = 0

    # Calculate derived values
    runtime_seconds = (result.runtime_ms / 1000) if result.runtime_ms else 0

    return {
        # Raw calculated values
        '_tests': tests,
        '_tests_passed': tests_passed,
        '_passed_percentage': passed_percentage,
        '_runtime_seconds': runtime_seconds,
        '_runtime_ms': result.runtime_ms or 0,
        '_cost_usd': result.cost_usd or 0.0,
        '_input_tokens': result.input_tokens or 0,
        '_output_tokens': result.output_tokens or 0,
        '_cache_tokens': result.cache_tokens or 0,
        '_turns': result.num_turns or 0,
        '_is_resolved': result.is_resolved,
        # Common metadata
        'task_id': result.task_id,
        'status_class': 'success' if result.is_resolved else 'failed',
    }


class ResultsTSVWriter:
    """Writes experiment results to a TSV file in real-time."""

    def __init__(self, output_path: Path, agent_name: AgentName, run_id: str):
        """
        Initialize the TSV writer.

        Args:
            output_path: Directory where the TSV file will be created
            agent_name: Name of the agent being used
            run_id: Unique identifier for this experiment run
        """
        self.tsv_path = output_path / "results.tsv"
        self.agent_name = agent_name
        self.run_id = run_id

    def initialize(self) -> None:
        """Initialize the TSV file with headers."""
        headers = [
            "experiment_id",
            "task_id",
            "result",
            "tests",
            "passed",
            "passed_percentage",
            "time_seconds",
            "cost",
            "input_tokens",
            "output_tokens",
            "cache_tokens",
            "turns",
            "agent",
            "db_type",
            "project_type"
        ]

        with open(self.tsv_path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(headers)

    def append_result(self, trial_result: TrialResults, config: Dict) -> None:
        """
        Append a single task result to the TSV file.

        Args:
            trial_result: The trial results to append
            config: The variant configuration containing db_type and project_type
        """
        # Use shared formatting function to get calculated values
        calc = format_trial_result(trial_result)

        # Format for TSV (no commas, simple formatting)
        result_status = "PASS" if calc['_is_resolved'] else "FAIL"

        row = [
            self.run_id,
            calc['task_id'],
            result_status,
            calc['_tests'],
            calc['_tests_passed'],
            calc['_passed_percentage'],
            calc['_runtime_seconds'],
            calc['_cost_usd'],
            calc['_input_tokens'],
            calc['_output_tokens'],
            calc['_cache_tokens'],
            calc['_turns'],
            str(self.agent_name.value),
            config.get("db_type", ""),
            config.get("project_type", "")
        ]

        with open(self.tsv_path, 'a', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(row)

