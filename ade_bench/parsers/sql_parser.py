"""SQL test parser for validating task results."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import duckdb
import pandas as pd
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SQLTestResult(BaseModel):
    """Result of a single SQL test."""
    
    test_name: str
    query: str
    status: str  # PASSED, FAILED, ERROR
    error_message: Optional[str] = None
    actual_result: Optional[Any] = None
    expected_result: Optional[Any] = None
    difference: Optional[str] = None


class SQLParserResult(BaseModel):
    """Overall result of SQL test parsing."""
    
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    test_results: List[SQLTestResult] = Field(default_factory=list)
    
    @property
    def all_passed(self) -> bool:
        """Check if all tests passed."""
        return self.total_tests > 0 and self.passed_tests == self.total_tests
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


class SQLParser:
    """Parser for SQL-based test validation."""
    
    def __init__(self, database_path: str):
        """Initialize SQL parser with database connection.
        
        Args:
            database_path: Path to DuckDB or SQLite database file
        """
        self.database_path = database_path
        self._connection = None
    
    @property
    def connection(self):
        """Lazy connection initialization."""
        if self._connection is None:
            if self.database_path.endswith('.duckdb'):
                self._connection = duckdb.connect(self.database_path)
            elif self.database_path.endswith(('.db', '.sqlite', '.sqlite3')):
                self._connection = sqlite3.connect(self.database_path)
                # Enable better row factory for SQLite
                self._connection.row_factory = sqlite3.Row
            else:
                raise ValueError(f"Unsupported database type for: {self.database_path}")
        return self._connection
    
    def parse_tests(self, test_dir: Path, expected_dir: Path) -> SQLParserResult:
        """Parse and execute SQL tests against expected results.
        
        Args:
            test_dir: Directory containing SQL test files
            expected_dir: Directory containing expected result files
            
        Returns:
            SQLParserResult with test outcomes
        """
        result = SQLParserResult()
        
        # Find all SQL test files
        sql_files = sorted(test_dir.glob("*.sql"))
        
        for sql_file in sql_files:
            test_name = sql_file.stem
            expected_file = expected_dir / f"{test_name}.json"
            
            test_result = self._run_single_test(
                test_name=test_name,
                sql_file=sql_file,
                expected_file=expected_file
            )
            
            result.test_results.append(test_result)
            result.total_tests += 1
            
            if test_result.status == "PASSED":
                result.passed_tests += 1
            elif test_result.status == "FAILED":
                result.failed_tests += 1
            else:  # ERROR
                result.error_tests += 1
        
        return result
    
    def _run_single_test(
        self,
        test_name: str,
        sql_file: Path,
        expected_file: Path
    ) -> SQLTestResult:
        """Run a single SQL test and compare with expected results.
        
        Args:
            test_name: Name of the test
            sql_file: Path to SQL query file
            expected_file: Path to expected results file
            
        Returns:
            SQLTestResult for this test
        """
        # Read SQL query
        try:
            query = sql_file.read_text().strip()
        except Exception as e:
            return SQLTestResult(
                test_name=test_name,
                query="",
                status="ERROR",
                error_message=f"Failed to read SQL file: {e}"
            )
        
        # Execute query
        try:
            if self.database_path.endswith('.duckdb'):
                df = self.connection.execute(query).fetchdf()
                actual_result = df.to_dict(orient='records')
            else:  # SQLite
                cursor = self.connection.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # Convert SQLite results to list of dicts
                if rows and cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    actual_result = [dict(zip(columns, row)) for row in rows]
                else:
                    actual_result = []
                
                cursor.close()
        except Exception as e:
            return SQLTestResult(
                test_name=test_name,
                query=query,
                status="ERROR",
                error_message=f"Query execution failed: {e}"
            )
        
        # Load expected results
        if not expected_file.exists():
            return SQLTestResult(
                test_name=test_name,
                query=query,
                status="ERROR",
                error_message=f"Expected results file not found: {expected_file}",
                actual_result=actual_result
            )
        
        try:
            with open(expected_file) as f:
                expected_data = json.load(f)
            
            # Handle different expected formats
            if isinstance(expected_data, dict):
                # Could have metadata + results
                expected_result = expected_data.get('results', expected_data)
            else:
                expected_result = expected_data
                
        except Exception as e:
            return SQLTestResult(
                test_name=test_name,
                query=query,
                status="ERROR",
                error_message=f"Failed to load expected results: {e}",
                actual_result=actual_result
            )
        
        # Compare results
        comparison = self._compare_results(actual_result, expected_result)
        
        if comparison['match']:
            return SQLTestResult(
                test_name=test_name,
                query=query,
                status="PASSED",
                actual_result=actual_result,
                expected_result=expected_result
            )
        else:
            return SQLTestResult(
                test_name=test_name,
                query=query,
                status="FAILED",
                actual_result=actual_result,
                expected_result=expected_result,
                difference=comparison['difference']
            )
    
    def _compare_results(
        self,
        actual: Union[List[Dict], Dict, Any],
        expected: Union[List[Dict], Dict, Any]
    ) -> Dict[str, Any]:
        """Compare actual and expected results.
        
        Args:
            actual: Actual query results
            expected: Expected query results
            
        Returns:
            Dictionary with 'match' boolean and 'difference' string
        """
        # Handle numeric tolerance for floating point comparisons
        def compare_values(a, b):
            if isinstance(a, float) and isinstance(b, float):
                return abs(a - b) < 1e-6
            return a == b
        
        # Convert to comparable format
        if isinstance(actual, list) and isinstance(expected, list):
            if len(actual) != len(expected):
                return {
                    'match': False,
                    'difference': f"Row count mismatch: {len(actual)} vs {len(expected)}"
                }
            
            # Sort both lists by all keys for consistent comparison
            if actual and isinstance(actual[0], dict):
                keys = sorted(actual[0].keys())
                actual = sorted(actual, key=lambda x: tuple(str(x.get(k, '')) for k in keys))
                expected = sorted(expected, key=lambda x: tuple(str(x.get(k, '')) for k in keys))
            
            # Compare each row
            for i, (a_row, e_row) in enumerate(zip(actual, expected)):
                if isinstance(a_row, dict) and isinstance(e_row, dict):
                    for key in set(a_row.keys()) | set(e_row.keys()):
                        if key not in a_row:
                            return {
                                'match': False,
                                'difference': f"Row {i}: Missing key '{key}' in actual"
                            }
                        if key not in e_row:
                            return {
                                'match': False,
                                'difference': f"Row {i}: Extra key '{key}' in actual"
                            }
                        if not compare_values(a_row[key], e_row[key]):
                            return {
                                'match': False,
                                'difference': f"Row {i}: Value mismatch for '{key}': {a_row[key]} vs {e_row[key]}"
                            }
                elif a_row != e_row:
                    return {
                        'match': False,
                        'difference': f"Row {i}: {a_row} vs {e_row}"
                    }
        else:
            # Simple equality check
            if not compare_values(actual, expected):
                return {
                    'match': False,
                    'difference': f"Value mismatch: {actual} vs {expected}"
                }
        
        return {'match': True, 'difference': None}
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None