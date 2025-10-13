from tabulate import tabulate
from ade_bench.harness_models import BenchmarkResults
from ade_bench.utils.results_writer import format_trial_result, get_failure_type
from typing import Dict, List, Any


def summarize_results(results: BenchmarkResults) -> Dict[str, Any]:
    """Generate a JSON summary of benchmark results."""
    table_data = []
    headers = ["Task", "Result", "Failure Type", "Tests", "Passed", "Passed %", "Time (s)", "Cost", "Input Tokens", "Output Tokens", "Cache Tokens", "Turns"]

    total_tests = 0
    total_tests_passed = 0
    total_runtime = 0
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_tokens = 0
    total_turns = 0
    resolved_count = 0

    for result in sorted(results.results, key=lambda x: x.task_id):
        # Use shared formatting function to get calculated values
        calc = format_trial_result(result)

        # Accumulate totals
        total_tests += calc['_tests']
        total_tests_passed += calc['_tests_passed']
        total_runtime += calc['_runtime_ms']
        total_cost += calc['_cost_usd']
        total_input_tokens += calc['_input_tokens']
        total_output_tokens += calc['_output_tokens']
        total_cache_tokens += calc['_cache_tokens']
        total_turns += calc['_turns']
        if calc['_is_resolved']:
            resolved_count += 1

        # Format values for HTML display (with commas)
        result_status = "p" if calc['_is_resolved'] else "FAIL"
        failure_type = get_failure_type(result)
        cost_str = f"${calc['_cost_usd']:.2f}"
        input_tokens_str = f"{calc['_input_tokens']:,}"
        output_tokens_str = f"{calc['_output_tokens']:,}"
        cache_tokens_str = f"{calc['_cache_tokens']:,}"
        turns_str = f"{calc['_turns']:,}"
        percentage_str = "" if calc['_passed_percentage'] == 100.0 else f"{calc['_passed_percentage']:.0f}%"

        table_data.append({
            'task_id': calc['task_id'],
            'result': result_status,
            'failure_type': failure_type,
            'status_class': calc['status_class'],
            'tests': str(calc['_tests']),
            'passed': str(calc['_tests_passed']),
            'passed_percentage': percentage_str,
            'time_seconds': f"{calc['_runtime_seconds']:.0f}",
            'cost': cost_str,
            'input_tokens': input_tokens_str,
            'output_tokens': output_tokens_str,
            'cache_tokens': cache_tokens_str,
            'turns': turns_str,
            # Store numeric values for totals calculation
            '_tests_num': calc['_tests'],
            '_passed_num': calc['_tests_passed'],
            '_runtime_ms': calc['_runtime_ms'],
            '_cost_usd': calc['_cost_usd'],
            '_input_tokens': calc['_input_tokens'],
            '_output_tokens': calc['_output_tokens'],
            '_cache_tokens': calc['_cache_tokens'],
            '_turns': calc['_turns'],
            '_is_resolved': calc['_is_resolved']
        })

    # Calculate totals
    total_passed_percentage = (total_tests_passed / total_tests * 100) if total_tests > 0 else 0
    overall_accuracy = (resolved_count / len(results.results) * 100) if results.results else 0
    total_runtime_seconds = total_runtime / 1000

    total_row = {
        'task_id': f"TOTAL (n={len(results.results)})",
        'result': f"{overall_accuracy:.0f}%",
        'failure_type': "",
        'status_class': 'total-row',
        'tests': str(total_tests),
        'passed': str(total_tests_passed),
        'passed_percentage': f"{total_passed_percentage:.0f}%",
        'time_seconds': f"{total_runtime_seconds:.0f}",
        'cost': f"${total_cost:.2f}",
        'input_tokens': f"{total_input_tokens:,}",
        'output_tokens': f"{total_output_tokens:,}",
        'cache_tokens': f"{total_cache_tokens:,}",
        'turns': f"{total_turns:,}"
    }

    return {
        'headers': headers,
        'tasks': table_data,
        'total_row': total_row
    }


def format_summary_table(summary: Dict[str, Any]) -> List[List[str]]:
    """Format the summary data into a table format for display."""
    table_data = []

    # Add task rows
    for task in summary['tasks']:
        table_data.append([
            task['task_id'],
            task['result'],
            task['failure_type'],
            task['tests'],
            task['passed'],
            task['passed_percentage'],
            task['time_seconds'],
            task['cost'],
            task['input_tokens'],
            task['output_tokens'],
            task['cache_tokens'],
            task['turns']
        ])

    # Add blank row as divider
    table_data.append([""] * len(summary['headers']))

    # Add total row
    total_row = summary['total_row']
    table_data.append([
        total_row['task_id'],
        total_row['result'],
        total_row['failure_type'],
        total_row['tests'],
        total_row['passed'],
        total_row['passed_percentage'],
        total_row['time_seconds'],
        total_row['cost'],
        total_row['input_tokens'],
        total_row['output_tokens'],
        total_row['cache_tokens'],
        total_row['turns']
    ])

    return table_data


def generate_html_table(results: BenchmarkResults) -> str:
    """Generate an HTML table of benchmark results with action links."""
    summary = summarize_results(results)

    # Generate table with unique placeholders for action links
    headers = summary['headers'] + ['Actions']
    table_data = []

    # Add task rows with unique placeholders
    for i, task in enumerate(summary['tasks']):
        row = [
            task['task_id'],
            task['result'],
            task['failure_type'],
            task['tests'],
            task['passed'],
            task['passed_percentage'],
            task['time_seconds'],
            task['cost'],
            task['input_tokens'],
            task['output_tokens'],
            task['cache_tokens'],
            task['turns'],
            f"__ACTION_LINKS_{i}__"  # Unique placeholder
        ]
        table_data.append(row)

    # Add total row
    total_row = summary['total_row']
    total_row_data = [
        total_row['task_id'],
        total_row['result'],
        total_row['failure_type'],
        total_row['tests'],
        total_row['passed'],
        total_row['passed_percentage'],
        total_row['time_seconds'],
        total_row['cost'],
        total_row['input_tokens'],
        total_row['output_tokens'],
        total_row['cache_tokens'],
        total_row['turns'],
        ""  # No action links for total row
    ]
    table_data.append(total_row_data)

    # Generate the base table
    html_table = tabulate(table_data, headers=headers, tablefmt="html")

    # Now replace the placeholders with actual action links
    for i, task in enumerate(summary['tasks']):
        action_links = f'<div class="links"><a href="{task["task_id"]}/results.html" class="link results">Results</a> <a href="{task["task_id"]}/panes.html" class="link panes">Panes</a> <a href="{task["task_id"]}/diffs.html" class="link diffs">Diffs</a></div>'
        html_table = html_table.replace(f"__ACTION_LINKS_{i}__", action_links)

    return html_table


def display_detailed_results(results: BenchmarkResults) -> None:
    """Display a detailed summary table of benchmark results."""
    summary = summarize_results(results)
    table_data = format_summary_table(summary)
    print(f"\n{'=' * 40} RESULTS SUMMARY {'=' * 40}\n")
    print(tabulate(table_data, headers=summary['headers'], tablefmt="psql"))
    print(f"\nFor more details, run the command below:\nuv run scripts_python/view_results.py")