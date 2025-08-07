import re
from ade_bench.parsers.base_parser import BaseParser, UnitTestStatus


class DbtParser(BaseParser):
    # Pattern to match individual test result lines
    # Examples:
    # "1 of 2 PASS test_one ........................................................... [PASS in 0.01s]"
    # "2 of 2 FAIL 1 test_two ......................................................... [FAIL 1 in 0.00s]"
    TEST_RESULT_PATTERN = r"\d+\s+of\s+\d+\s+(PASS|FAIL|ERROR)(?:\s+\d+)?\s+(\S+)\s+\.+\s+\[(PASS|FAIL|ERROR)"
    
    # Pattern to match the summary line
    TEST_SUMMARY_PATTERN = r"Done\.\s+PASS=(\d+)\s+WARN=(\d+)\s+ERROR=(\d+)\s+SKIP=(\d+)\s+TOTAL=(\d+)"
    
    def parse(self, content: str) -> dict[str, UnitTestStatus]:
        # Check for compilation error
        if "Compilation Error" in content:
            return { "dbt_compile": UnitTestStatus.FAILED }
        
        results = { "dbt_compile": UnitTestStatus.PASSED }
        
        # Find all test result lines
        for match in re.finditer(self.TEST_RESULT_PATTERN, content):
            status = match.group(1)  # PASS, FAIL, or ERROR
            test_name = match.group(2)  # test name
            
            # Map dbt status to UnitTestStatus
            if status == "PASS":
                results[test_name] = UnitTestStatus.PASSED
            elif status in ["FAIL", "ERROR"]:
                results[test_name] = UnitTestStatus.FAILED
        
        # Also check the summary line to ensure we got all tests
        summary_matches = list(re.finditer(self.TEST_SUMMARY_PATTERN, content))
        if summary_matches:
            # Use the last occurrence of the summary line
            summary_match = summary_matches[-1]
            pass_count = int(summary_match.group(1)) + 1 # include compile test
            error_count = int(summary_match.group(3))
            total_count = int(summary_match.group(5)) + 1 # include compile test
            
            self._logger.info(f"Test summary - PASS: {pass_count}, ERROR: {error_count}, TOTAL: {total_count}")
            self._logger.info(f"Parsed {len(results)} test results")
            
            # Verify we parsed the correct number of tests
            if len(results) != total_count:
                self._logger.warning(f"Mismatch: parsed {len(results)} tests but summary shows {total_count} total")
        
        if not results:
            raise ValueError("No test results found in the provided content.")
        
        return results