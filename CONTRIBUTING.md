# Contributing

Contributions to the ADE-bench project are welcome.

## Contributing new datasets

ADE-bench supports both dbt Core and dbt Fusion projects ([with some exceptions](https://github.com/thedatamates/ade-bench/issues/12)).

In some situations, the dbt Fusion engine's SQL Comprehension capabilities can make it impossible to build a misconfigured project. Disable static analysis by setting the environment variable `DBT_STATIC_ANALYSIS=off` in your invocation. Using the environment variable instead of `--static-analysis off` flag ensures graceful degradation for dbt Core.

When creating a dbt project, include the `profiles.yml` and `dbt_project.yml` file in the root directory of the project. In `profiles.yml`, include a profile for all of the supported databases, where the name is `[project_name]-[database_type]. Do **NOT** fill in the Snowflake credentials, because these will get overwritten with the trial user:

```yaml
foo-duckdb:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "./foo.duckdb"
      schema: main

foo-snowflake:
  target: dev
  outputs:
    dev:
      type: snowflake
      ## Added by ADE-bench when task is created
      account: <account>
      user: <user>
      password: <password>
      role: <role>
      database: <database>
      schema: <schema>
      warehouse: <warehouse>
```

## Contributing new tasks or tests

**Project and DB specific tests:** Tests can be designated for specific environments using comment headers:

```sql
-- db: duckdb          # Only runs for DuckDB
-- db: snowflake duckdb # Runs for both Snowflake and DuckDB
-- project-type: dbt   # Only runs for dbt projects
```

Tests without environment specification run on all environments.

### Producing solution seeds

**You can generate these seeds by running ADE-bench with the `--seed flag`.** When you do this, the harness runs as it normally would,[^3] except, once trial is over, it exports two things into the task directory:

- **CSVs:** Each table defined in as solution seed will get exported into the task's `\seeds` directory as `solution__[table_name].csv`.
- **A seed config:** To ensure that the `dbt seed` command runs during the evaluation, ADE-bench will also create a schema file called `_no-op.txt`. This is utility file that is used when tables are uploaded. (Note that some shenanigans are necessary here to support cross-database compatibility. For example, DuckDB has a `hugeint` data type, whereas Snowflake does not. Why does the small database need huge integers?)

**ONLY RUN `--seed` WITH THE SAGE AGENT ON DUCKDB** Exporting seeds is not currently supported with Snowflake (TODO?), and because solution seeds are used as answer keys, they should never be created based on what an agent does.

1. **During --seed mode**: All tables (the main one and alternates) will be extracted as CSV files with the `solution__` prefix. For example, running the task above will extract `solution__table_name.csv` from `table_name`, `solution__another_good_answer.csv` from `another_good_answer`, and so on.

#### Solution seeds

Many tasks have `solution_seeds` defined in their `task.yaml` file. These are tables that are used to evaluate the agent's work.

As described in `task.yaml` description above, there are several additional configuration options when setting up solution seeds:

- You can exclude columns from being part of the table equality comparison.
- You can select specific columns to only include.
- You can disable the automatic generation of either the equality or existence test.
- You can specify alternate solution seeds for tasks that have multiple valid answers.

#### Alternate solution seeds

Some tasks may have multiple valid answers. For example, a query might be written in different ways that produce equally correct results. To handle this, you can specify alternate solution seeds:

```yaml
solution_seeds:
  - table_name: the_best_answer
    alternates:
    - another_good_answer
    - not_as_good_but_still_counts
```

When alternates are specified, ADE-bench will compare the table defined by `table_name` to solution seeds of that table _and_ of any alternatives.

In the example above, the agent would be expected to create a table called `the_best_answer` (and just that table), and for that table to match one of the three seeds (`solution__the_best_answer`, `solution__another_good_answer`, and `solution__not_as_good_but_still_counts`).



### Approximate equality tests

Here's a thing: Sometimes databases give slightly different results. (For reasons, `select round(23/40,2)` is 58 in Snowflake, and 57 in DuckDB. Computers, man.) Or, the agent could write a query that returns a number rounded to a different number of decimals, and you want to be tolerant to that. Though there currently isn't a way to automatically create a test like this, `airbnb007` includes examples of `_with_tolerance` tests. This test will:

- Compare the number of rows, expected an exact match
- Compare the min and max values of date columns, expecting an exact match
- Compare the sum and averages of numeric columns, expecting the test table to be within a specified percentage band.

The "configuration" of that test is defined in a block at the top of the test:

```sql
-- Add the table name and the solution CSV
{% set test_and_solution_tables = ['daily_agg_nps_reviews','solution__daily_agg_nps_reviews'] %}

-- List date columns
{% set date_cols = ['review_date'] %}
-- List numeric columns and the tolerances. These are percentages, so sum_tolerance of 0.01 means
-- that the sum of each numeric column needs to be between 98% and 102% of the sums of the
-- corresponding column in the solution table.
{% set numeric_cols = ['nps_daily', 'reviews_daily', 'nps_28d', 'reviews_28d'] %}
{% set sum_tolerance = 0.02 %}
{% set avg_tolerance = 0.02 %}
```

## Sharing projects across databases and project types

Tasks can be configured with different environment variants, so that they can be run against multiple databases or project types. Though this is useful for testing how agents perform against different types of databases, it's also very helpful for development. Because DuckDB is very easy to work with locally, it can often be easier to develop tasks against DuckDB; moreover, if outside contributors want to contribute tasks, they might want to contribute the task as a DuckDB database, since it can be contributed as a file. And in these cases, it can be very helpful to have migration paths.

There are three features to help migrate a shared dbt project between databases or dbt versions:

1. Configure the variants in the task. For example, in a task called `foo001`, you might have two variants: One for DuckDB, and one for Snowflake:

```yaml
variants:
- db_type: duckdb
  db_name: foo
  project_type: dbt
  project_name: foo

- db_type: snowflake
  db_name: foo
  project_type: dbt
  project_name: foo
  migration_directory: foo__duckdb_to_snowflake
```

2. Create a migration script. In the example above, when the task is run against DuckDB, ADE-bench will copy the shared dbt project `foo` in the trial environment. When the task is run against Snowflake, it will copy the same project *and the contents of the folder in `shared\migrations\foo__duckdb_to_snowflake`. It will then run the `migration.sh` script (prior to running the task `setup.sh` script). Note that this migration script has access to any other files in that migration directory, so if you want to fully update some files in the dbt project, you can include the new files in the migration directory.

3. When the `solution.sh` script runs, ADE-bench passes the corresponding database and project type into the script as an argument. So if different updates are needed to solve the trial depending on the database, these can be configured following patterns like the example below:

```bash
## This updates the schema config in the solution files, and then moves the files to the appropriate place

# Assign the solutions directory
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

# Assign the 'replace' value based on the database type
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    replace='schema="main"'
else
    replace='schema="public"'
fi

# Loop over the files, update the value in the file, and move them
# from the solutions directory in the project directory
files=(
    "foo.sql"
    "bar.sql"
)

for file in "${files[@]}"; do
    find='schema="main"'
    sed -i "s/${find}/${replace}/g" $SOLUTIONS_DIR/$file
    cp $SOLUTIONS_DIR/$file models/$file
done
```

## Running arbitrary SQL queries

ADE-bench provides a utility script (`run_sql.sh`) that allows you to run arbitrary SQL queries against the database from within `setup.sh` or `solution.sh` scripts. This can be useful when you need to modify the database schema or data directly.

**Usage:**

```bash
# In setup.sh or solution.sh, you can use run_sql.sh like this:
/scripts/run_sql.sh "$@" << SQL
-- Your SQL queries here
CREATE OR REPLACE TABLE foo_temp AS
  SELECT * REPLACE revenue * 10 as revenue
  FROM foo;

DROP TABLE foo;
ALTER TABLE foo_temp RENAME TO foo;
SQL
```

The script automatically:

- Extracts `--db-type` and `--project-type` from the arguments passed to your script
- Reads database connection details from `/app/profiles.yml`
- Detects the correct profile name based on the project and database type
- Executes the SQL against the appropriate database (DuckDB or Snowflake)
- Handles multiple SQL statements separated by semicolons

**Note:** In some instances, the text of the query may need to be modified depending on the database; you can use the if statements just above (i.e., `if [[ "$*" == *"--db-type=duckdb"* ]]...`) to modify the query based on the database type.

---

## Development

To develop a new task, there are a few things that can be useful:

### Use interactive mode

You can run a task, and then launch an interactive shell into a task environment. You can also halt the task after different stages (e.g., after the setup scripts run but before the agent runs), and interact with the environment at that stage. This uses the `ade interact` command, and is documented [here](CLI.md).

### Creating a local sandbox

You can create a local sandbox in a `/dev/sandbox` directory, which you can `cd` into and play around directly. This is especially helpful if you're developing on a DuckDB trial. To create that sandbox, run:

```
uv run scripts_python/create_sandbox.py --task [task_to_copy] --db [duckdb] --project-type [dbt]
```

This will move all of the relevant files into the directory above. Then, if you `cd` into that directory, you can manually execute the various steps of the task:

```bash
bash setup.sh # Run the setup script
bash migration.sh # Run the migration scripts, if needed
bash solution.sh # Run the solution script
dbt seed # Create the seed file
dbt test --select "test_type:singular" # Run the task tests
```

**Note:** This does **NOT** create a user or database in Snowflake like the task setup does. If you want to use this sandbox on Snowflake, you'll need to run the task first, which will create those resources in Snowflake.

### Creating seeds

When you're developing a task and ready to create CSVs for the solution seeds, run the following command:

```
ade run [task_to_copy] --db duckdb --project-type [dbt] --agent sage --seed
```

The final seed flag will export the CSVs from final project in the task's `/seeds` directory. **Read the warning in "Solution seeds" before doing this.**

#### Debugging

Stuff goes wrong. It's really finicky sometimes. To debug, it's often useful to use the sandbox, but the most helpful thing is running the trial with the `--persist` flag, which keeps your Docker container alive after the task is complete. Then, you can log into the container—either directly, or via the Docker desktop app[^3], and both look at the files in the container and run commands in a terminal.

Moreover, if you're working with Snowflake, the task will create task databases within your account. You can also query these directly.

Finally, if you want to stop the harness at any point throughout the trial, you can insert a breakpoint function into the harness. To do this, find the point within the script that you want to halt the run (you have to read the code; it's messy; I might make this an easier config at some point). Then, in the code, add:

```python
from ade_bench.utils.debug_breakpoint import breakpoint
breakpoint("optional message")
```

This will halt the harness at that point. If you run the harness with the `--persist` flag, the container will then be kept alive, as it was when the harness was halted.

[^3] A somewhat annoying thing about this: When you run ADE-bench with the `--seed` flag, it will evaluate each trial with whatever CSVs exist in the `/seeds` directory _before_ the new ones are created, and then, _after the tests have run_, it will export the results into the directory. This means that you may need to run it twice to check that task works: Once to create the seeds, and another time (without the `--seed` flag) to see if it passes.
