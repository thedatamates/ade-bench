import re
from ade_bench.parsers.base_parser import BaseParser, UnitTestStatus, ParserResult


class DbtParser(BaseParser):
    # Pattern to match individual test result lines
    # Examples:
    # "1 of 2 PASS test_one ........................................................... [PASS in 0.01s]"
    # "2 of 2 FAIL 1 test_two ......................................................... [FAIL 1 in 0.00s]"
    TEST_RESULT_PATTERN = r"\d+\s+of\s+\d+\s+(PASS|FAIL|ERROR)(?:\s+\d+)?\s+(\S+)\s+\.+\s+\[(PASS|FAIL|ERROR)"

    # Pattern to match the summary line
    # Handles both formats: with and without NO-OP field
    TEST_SUMMARY_PATTERN = r"Done\.\s+PASS=(\d+)\s+WARN=(\d+)\s+ERROR=(\d+)\s+SKIP=(\d+)(?:\s+NO-OP=(\d+))?\s+TOTAL=(\d+)"

    def _create_status_message(self, results: dict, summary_data: dict | None, has_compilation_error: bool) -> str:
        """Create the final status message based on parsed results."""

        def _z(int) -> str:
            return f"{int:2d}"

        test_results = {k: v for k, v in results.items() if k != "dbt_compile"}

        # Case 1: Compilation error
        if has_compilation_error:
            return "ERROR - dbt compilation error found"

        # Case 2: No test results found (no summary data and no individual test results)
        if not summary_data and not test_results:
            return "ERROR - no dbt test results found"

        # Case 3: We have summary data - use it for the message
        if summary_data:
            pass_count = summary_data['pass_count']
            error_count = summary_data['error_count']
            total_count = summary_data['total_count']

            # Check for mismatch between parsed tests and summary
            if len(test_results) != total_count:
                return f"WARN  - dbt parsing mismatch - Parser found {len(test_results)} tests but summary shows {total_count} tests."

        # Case 4: We have individual test results but no summary
        if test_results:
            pass_count = sum(1 for status in test_results.values() if status == UnitTestStatus.PASSED)
            error_count = sum(1 for status in test_results.values() if status == UnitTestStatus.FAILED)
            total_count = pass_count + error_count

        # Construct the status message if pass counts and error counts are present
        if pass_count and error_count:
            if error_count == 0:
                message_lead = "PASS"
            else:
                message_lead = "FAIL"

            return f"{message_lead}  - dbt test results - Pass- {_z(pass_count)}, Fail- {_z(error_count)}, Total- {_z(total_count)}"

        # Return error if no pass or error counts are present
        return "ERROR - no dbt test results found"

    def _has_test_results(self, content: str) -> bool:
        """Check if the content contains actual test results (not just compilation errors)."""
        # Look for test result lines or summary lines
        return bool(re.search(self.TEST_RESULT_PATTERN, content) or re.search(self.TEST_SUMMARY_PATTERN, content))

    def parse(self, content: str) -> ParserResult:
        # First, parse all the results without creating status messages
        results = {}
        summary_data = None

        # Check for compilation error - this should only happen when dbt fails to run at all
        # If we see test results, even with failures, compilation succeeded
        has_compilation_error = "Compilation Error" in content and not self._has_test_results(content)

        if has_compilation_error:
            results = {"dbt_compile": UnitTestStatus.FAILED}
        else:
            results = {"dbt_compile": UnitTestStatus.PASSED}

            # Find all test result lines
            for match in re.finditer(self.TEST_RESULT_PATTERN, content):
                status = match.group(1)  # PASS, FAIL, or ERROR
                test_name = match.group(2)  # test name

                # Map dbt status to UnitTestStatus
                if status == "PASS":
                    results[test_name] = UnitTestStatus.PASSED
                elif status in ["FAIL", "ERROR"]:
                    results[test_name] = UnitTestStatus.FAILED

            # Parse summary line if it exists
            summary_matches = list(re.finditer(self.TEST_SUMMARY_PATTERN, content))
            if summary_matches:
                # Use the last occurrence of the summary line
                summary_match = summary_matches[-1]
                summary_data = {
                    'pass_count': int(summary_match.group(1)),
                    'warn_count': int(summary_match.group(2)),
                    'error_count': int(summary_match.group(3)),
                    'skip_count': int(summary_match.group(4)),
                    'total_count': int(summary_match.group(6))
                }

        # Now construct the final status message based on the parsed results
        status_message = self._create_status_message(results, summary_data, has_compilation_error)

        return ParserResult(test_results=results, status_message=status_message)

