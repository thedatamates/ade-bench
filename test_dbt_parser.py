#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ade_bench'))

from ade_bench.parsers.dbt_parser import DbtParser
from ade_bench.parsers.base_parser import UnitTestStatus

# Example log content from the user's case
test_content = """12:17:36  Concurrency: 1 threads (target='dev')
12:17:36
12:17:36  1 of 2 START test AUTO_dim_customer_equality ................................... [RUN]
12:17:36  1 of 2 ERROR AUTO_dim_customer_equality ........................................ [ERROR in 0.08s]
12:17:36  2 of 2 START test AUTO_dim_customer_existence .................................. [RUN]
12:17:36  2 of 2 PASS AUTO_dim_customer_existence ........................................ [PASS in 0.03s]
12:17:36
12:17:36  Finished running 2 data tests in 0 hours 0 minutes and 0.33 seconds (0.33s).
12:17:36
12:17:36  Completed with 1 error, 0 partial successes, and 0 warnings:
12:17:36
12:17:36    Compilation Error in test AUTO_dim_customer_equality (tests/AUTO_dim_customer_equality.sql)
  "analytics_engineering"."main"."dim_customer" has less columns than "analytics_engineering"."main"."solution__dim_customer", please ensure they have the same
columns or use the `compare_columns` or `exclude_columns` arguments to subset them.

  > in macro default__test_equality (macros/generic_tests/equality.sql)
  > called by macro test_equality (macros/generic_tests/equality.sql)
  > called by test AUTO_dim_customer_equality (tests/AUTO_dim_customer_equality.sql)
12:17:36
12:17:36  Done. PASS=1 WARN=0 ERROR=1 SKIP=0 TOTAL=2"""

def test_parser():
    parser = DbtParser()
    
    print("Testing DBT parser with example log...")
    print("=" * 50)
    
    try:
        results = parser.parse(test_content)
        
        print("Parse results:")
        for test_name, status in results.items():
            print(f"  {test_name}: {status.value}")
        
        print("\nAnalysis:")
        print(f"  Compilation status: {'PASSED' if results.get('dbt_compile') == UnitTestStatus.PASSED else 'FAILED'}")
        
        test_results = {k: v for k, v in results.items() if k != 'dbt_compile'}
        passing_tests = sum(1 for result in test_results.values() if result == UnitTestStatus.PASSED)
        total_tests = len(test_results)
        
        print(f"  Tests found: {total_tests}")
        print(f"  Tests passing: {passing_tests}")
        print(f"  Tests failing: {total_tests - passing_tests}")
        print(f"  Trial would be: {'RESOLVED' if passing_tests == total_tests else 'UNRESOLVED'}")
        
    except Exception as e:
        print(f"Error parsing: {e}")

if __name__ == "__main__":
    test_parser()
