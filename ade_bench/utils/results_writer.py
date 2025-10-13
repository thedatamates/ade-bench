"""TSV results writer for real-time experiment tracking."""

import csv
from pathlib import Path
from typing import Dict

from ade_bench.harness_models import TrialResults, BenchmarkResults, FailureMode


def get_failure_type(result: TrialResults) -> str:
    """
    Determine the failure type based on the result.

    Returns:
        - Empty string if test passed
        - "eval_error" if dbt compile passed but tests failed
        - "compile_error" if dbt compile failed
        - "timeout" if test timed out
        - The failure_mode value for other failures
        - "unknown" if failure_mode is None/UNSET
    """
    # If test passed, no failure type
    if result.is_resolved:
        return ""

    # Check for timeout (regardless of is_resolved state)
    if result.failure_mode in [FailureMode.AGENT_TIMEOUT, FailureMode.SETUP_TIMEOUT, FailureMode.TEST_TIMEOUT]:
        return result.failure_mode.value

    # If is_resolved is False and failure_mode is UNSET, check parser results
    if result.is_resolved is False and result.failure_mode == FailureMode.UNSET:
        if result.parser_results and "dbt_compile" in result.parser_results:
            from ade_bench.parsers.base_parser import UnitTestStatus
            if result.parser_results["dbt_compile"] == UnitTestStatus.FAILED:
                return "compile_error"
            else:
                # dbt compile passed, but other tests failed
                return "eval_error"

    # Otherwise, use the failure_mode value
    if result.failure_mode in [FailureMode.NONE, FailureMode.UNSET, None]:
        return "unknown"

    # Return the actual failure mode value
    return result.failure_mode.value


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


def write_results_tsv(results: BenchmarkResults, output_path: Path, run_id: str) -> None:
    """
    Write benchmark results to a TSV file.

    Args:
        results: BenchmarkResults object containing all trial results
        output_path: Path to the output TSV file
        run_id: Experiment run ID
    """
    headers = [
        "experiment_id",
        "task_id",
        "result",
        "failure_type",
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

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(headers)

        for trial_result in sorted(results.results, key=lambda x: x.task_id):
            # Use shared formatting function to get calculated values
            calc = format_trial_result(trial_result)

            # Determine result status
            if calc['_is_resolved']:
                result_status = "pass"
            elif calc['_is_resolved'] is None:
                result_status = ""
            else:
                result_status = "fail"

            # Get failure type
            failure_type = get_failure_type(trial_result)

            row = [
                run_id,
                calc['task_id'],
                result_status,
                failure_type,
                calc['_tests'],
                calc['_tests_passed'],
                calc['_passed_percentage'],
                calc['_runtime_seconds'],
                calc['_cost_usd'],
                calc['_input_tokens'],
                calc['_output_tokens'],
                calc['_cache_tokens'],
                calc['_turns'],
                trial_result.agent or "",
                trial_result.db_type or "",
                trial_result.project_type or ""
            ]

            writer.writerow(row)

