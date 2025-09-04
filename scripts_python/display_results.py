from tabulate import tabulate
from ade_bench.harness_models import BenchmarkResults


def display_detailed_results(results: BenchmarkResults) -> None:
    """Display a detailed summary table of benchmark results."""
    
    # Create detailed summary table
    table_data = []
    headers = ["Task", "Result", "Tests", "Passed", "Passed %", "Time (s)", "Cost", "Input Tokens", "Output Tokens"]
    
    total_tests = 0
    total_tests_passed = 0
    total_runtime = 0
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    resolved_count = 0
    
    for result in results.results:
        # Calculate test statistics
        if result.parser_results:
            tests = len(result.parser_results)
            tests_passed = sum(1 for status in result.parser_results.values() if status.value == "passed")
            passed_percentage = (tests_passed / tests * 100) if tests > 0 else 0
        else:
            tests = 0
            tests_passed = 0
            passed_percentage = 0
        
        # Accumulate totals
        total_tests += tests
        total_tests_passed += tests_passed
        total_runtime += result.runtime_ms or 0
        total_cost += result.cost_usd or 0.0
        total_input_tokens += result.total_input_tokens or 0
        total_output_tokens += result.total_output_tokens or 0
        if result.is_resolved:
            resolved_count += 1
        
        # Format values
        result_status = "p" if result.is_resolved else "FAIL"
        runtime_seconds = (result.runtime_ms / 1000) if result.runtime_ms else 0
        runtime_str = f"{runtime_seconds:.3f}"
        cost_str = f"${result.cost_usd:.6f}" if result.cost_usd else "$0.000000"
        input_tokens_str = f"{result.total_input_tokens:,}" if result.total_input_tokens else "0"
        output_tokens_str = f"{result.total_output_tokens:,}" if result.total_output_tokens else "0"
        
        # Format percentage - show nothing if 100%
        percentage_str = "" if passed_percentage == 100.0 else f"{passed_percentage:.1f}%"
        
        table_data.append([
            result.task_id,
            result_status,
            str(tests),
            str(tests_passed),
            percentage_str,
            runtime_str,
            cost_str,
            input_tokens_str,
            output_tokens_str
        ])
    
    # Add TOTAL row
    total_passed_percentage = (total_tests_passed / total_tests * 100) if total_tests > 0 else 0
    overall_accuracy = (resolved_count / len(results.results) * 100) if results.results else 0
    total_runtime_seconds = total_runtime / 1000
    
    table_data.append([
        "TOTAL",
        f"{overall_accuracy:.1f}%",
        str(total_tests),
        str(total_tests_passed),
        f"{total_passed_percentage:.1f}%",
        f"{total_runtime_seconds:.3f}",
        f"${total_cost:.6f}",
        f"{total_input_tokens:,}",
        f"{total_output_tokens:,}"
    ])

    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

def display_all_results(results: BenchmarkResults) -> None:
    display_detailed_results(results)
