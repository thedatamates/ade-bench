"""Utility for generating solution seed tests."""
from pathlib import Path
from typing import List, Optional

from ade_bench.harness_models import SolutionSeedConfig


def generate_equality_test(
    table_name: str, 
    config: Optional[SolutionSeedConfig] = None
) -> str:
    """Generate an equality test for a solution seed table.
    
    Args:
        table_name: Name of the table to test
        config: Optional configuration for column inclusion/exclusion
        
    Returns:
        Generated SQL test content
    """
    # Build column lists based on config
    cols_to_include = []
    cols_to_exclude = []
    
    if config:
        if config.include_columns:
            cols_to_include = config.include_columns
        if config.exclude_columns:
            cols_to_exclude = config.exclude_columns
    
    # Format columns as lists
    include_list = ",\n    ".join([f"'{col}'" for col in cols_to_include]) if cols_to_include else ""
    exclude_list = ",\n    ".join([f"'{col}'" for col in cols_to_exclude]) if cols_to_exclude else ""
    
    return f"""-- Define columns to compare
{{% set table_name = '{table_name}' %}}

{{% set cols_to_include = [
    {include_list}
] %}}

{{% set cols_to_exclude = [
    {exclude_list}
] %}}



-------------------------------------
---- DO NOT EDIT BELOW THIS LINE ----
{{% set answer_key = 'solution__' + table_name %}}

-- depends_on: {{{{ ref(answer_key) }}}}
-- depends_on: {{{{ ref(table_name) }}}}

{{% set table_a = adapter.get_relation(database=target.database, schema=target.schema, identifier=answer_key) %}}
{{% set table_b = adapter.get_relation(database=target.database, schema=target.schema, identifier=table_name) %}}

{{% if table_a is none or table_b is none %}}
    select 1
{{% else %}}    
    {{{{ dbt_utils.test_equality(
        model=ref(answer_key),
        compare_model=ref(table_name),
        compare_columns=cols_to_include,
        exclude_columns=cols_to_exclude
    ) }}}}
{{% endif %}}
"""


def generate_existence_test(table_name: str) -> str:
    """Generate an existence test for a solution seed table.
    
    Args:
        table_name: Name of the table to test
        
    Returns:
        Generated SQL test content
    """
    return f"""{{% set table_name = '{table_name}' %}}



-------------------------------------
---- DO NOT EDIT BELOW THIS LINE ----
{{% set answer_key = 'solution__' + table_name %}}

{{% set table_a = adapter.get_relation(database=target.database, schema=target.schema, identifier=answer_key) %}}
{{% set table_b = adapter.get_relation(database=target.database, schema=target.schema, identifier=table_name) %}}

{{% if table_a is none or table_b is none %}}
    select 1
{{% else %}}
    select 1 where false
{{% endif %}}
"""





def generate_solution_tests(
    table_name: str, 
    test_dir: Path,
    config: Optional[SolutionSeedConfig] = None
) -> None:
    """Generate both equality and existence tests for a solution seed table.
    
    Args:
        table_name: Name of the table to generate tests for
        test_dir: Directory to write the test files to
        config: Optional configuration for test generation
    """
    # Ensure test directory exists
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove existing AUTO tests for this table
    for auto_test in test_dir.glob(f"AUTO_*.sql"):
        auto_test.unlink()
    
    # Generate equality test
    equality_content = generate_equality_test(table_name, config)
    equality_path = test_dir / f"AUTO_{table_name}_equality.sql"
    equality_path.write_text(equality_content)
    
    # Generate existence test
    existence_content = generate_existence_test(table_name)
    existence_path = test_dir / f"AUTO_{table_name}_existence.sql"
    existence_path.write_text(existence_content) 