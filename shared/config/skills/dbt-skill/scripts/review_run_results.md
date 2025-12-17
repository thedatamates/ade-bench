# Review dbt Run Results

## When to Use

If a user tells you there is a problem with the project, review the `target/run_results.json` file to identify which resources failed and why.

Review the completion date to ensure the information is fresh.

## Python Script

```python
import json

def review_dbt_run_results(run_results_path: str):
    """Review dbt run_results.json and identify failures."""
    with open(run_results_path) as f:
        data = json.load(f)
    
    results = data.get('results', [])
    failed = [r for r in results if r.get('status') == 'error']
    
    print(f"Total: {len(results)} | Failed: {len(failed)}")
    
    if failed:
        print("\nFailed Resources:")
        for r in failed:
            # Extract resource name from unique_id (e.g., "model.project.name" -> "name")
            resource_name = r['unique_id'].split('.')[-1]
            resource_type = r['unique_id'].split('.')[0]
            
            print(f"\n- {resource_type}: {resource_name}")
            
            # Parse error message for key details
            message = r.get('message', '')
            if message:
                # Extract the main error line
                error_lines = [line for line in message.split('\n') if line.strip()]
                print(f"  Error: {error_lines[0] if error_lines else message}")
            
            # Show compiled SQL if available
            compiled = r.get('compiled_code', '').strip()
            if compiled and len(compiled) < 200:
                print(f"  SQL: {compiled}")
            elif compiled:
                print(f"  SQL: {compiled[:200]}...")
    
    return failed

# Usage
failed_resources = review_dbt_run_results('target/run_results.json')
```

## What to Do with Results

Once you identify failed resources:

1. **Read the error message** - Understand what went wrong (syntax error, missing column, type mismatch, etc.)

2. **Check the compiled SQL** - The `compiled_code` shows the actual SQL that was executed, which helps identify:
   - Typos in column names
   - Missing or incorrect joins
   - Invalid SQL syntax
   - Logic errors

3. **Locate the source file** - Find the model file using the `unique_id`:
   - `model.project_name.model_name` → `models/model_name.sql`
   - Check the error message for the file path

4. **Fix the issue** - Common fixes:
   - **Syntax errors**: Correct SQL syntax in the model file
   - **Missing columns**: Add missing columns or fix column references
   - **Duplicate columns**: Remove duplicate column names in SELECT statements
   - **Missing dependencies**: Ensure upstream models/sources exist and are materialized
   - **Schema mismatches**: Update column names to match source schema

5. **Re-run the specific model** - Test your fix:

   ```bash
   dbt build -s model_name
   ```
