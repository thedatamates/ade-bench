# ADE-bench

_"Lord, forgive me, I've been running, running blind in truth."_

— [Beyonce  /  "Freedom"  /  Lemonade](https://www.youtube.com/watch?v=7FWF9375hUA&t=39s)

## Overview

ADE-bench[^1] is a framework for evaluating AI agents on data analyst tasks. The framework has several major parts:

- Isolated dbt project and database environments that can be provided to an agent.
- Methods for updating or corrupting those environments prior to giving them to agents.
- Sandboxes in which each task can be independently run.
- Methods for evaluating the agent's work against expected results.

Today, each ADE-bench trial consists of a dbt project and a database. However, the framework could be extended to include more environments, multiple databases, and other data engineering tools that more closely resemble the real environments in which analysts and data engineers work.

## An introduction to how ADE-bench works

ADE-bench has three primary components:

1. Tasks
2. Shared databases
3. Shared (dbt) projects

Each task represents a request that might be made to an agent. Though each task can include multiple evaluation criteria (e.g., it may require multiple models to be updated, or a model to have the correct SQL query and materialization configuration), the task is the primary unit of evaluation in ADE-bench.

When ADE-bench is asked to solve a task, here is what happens:

1. **Copy the project into a sandbox.** ADE-bench creates a sandbox environment (i.e., a Docker container) for the task. It loads the corresponding project into the container, and creates a sandbox environment for the corresponding database (see "How databases work" below).
2. **Take a first snapshot.** One the project is set up, ADE-bench takes a snapshot of all the files in the project. This allows it to log the changes made by additional setup tasks and by the agent.
3. **Run task-specific setup script.** After taking a snapshot, ADE-bench runs any of the tasks additonal setup scripts. These might make changes to the project, update the data in the database, or make changes to the project so that it can be run a against a different type of databases (see "Sharing projects across databases.")
4. **Take another snapshot.** ADE-bench takes another snapshot to log what changes made in the step above.
5. **Ask the agent to do stuff.** The environment is handed to the agent, which then tries to resolve the task.
6. **Take a final snapshot.** Once the agent declares itself done, ADE-bench takes a third snapshot.
7. **Evalute the result.** The changes are evaluted against the tests specified in the task. If all the tests pass, the task passes. **Note:** ADE-bench includes automatic ways to compare tables to one another. For example, if you want to evaluate a task by seeing if the agent created the correct `dim_users` table, you can define this table in the task configuration, and the comparison test is generated automatically.
8. **Clean up the sandbox.** Once the task has recorded its results, ADE-bench deletes the container.

## Task Configuration

Before getting into the details, it's useful to see how tasks are configured. This will help define the outline for how ADE-bench works, and the sections below will fill in the details.

Each task folder contains a handful of files:

- `task.yaml` - The task's configuration. This is an important file, so all the details are below.
- `setup.sh` – A setup script that runs before the agent is given the task, for modifying files and doing other computer stuff.
- `setup/` – (Optional) A directory containing files that the setup script can use. For example, suppose you want to replace `a_good_working_file.sql` with `one_with_a_bug.sql`. Put the one with a bug here and use `setup.sh` to replace it. This lets you modify the project for the specific task, without having to make changes to the shared project.
- `solution.sh` – A script that solves the task. The oracle agent is a agent that just runs this script. See "The oracle agent" below for more.
- `solutions/` – (Optional) Files that are available to the solution script. This is exactly analogous to the `/setup` directory for the setup script.
- `tests/` - dbt tests that are used to evaluate the trial. For a trial to pass, all the tests in this directory must pass. You can add manual tests, and if you include `solution_seeds` in the task configuration, tests will get added here automatically when a task is run. Automatically generated tests are appened with the name `AUTO_`. See "How trials are evaluated" below for more.
- `seeds/` - CSVs that are used to evaluate the automatically generated solution_seed tests. These are **NOT** created on every run; they are only updated when ADE-bench is run with the `--seed` flag. See "Solution seeds" below for more.

The task is defined in the `task.yaml` file:

```yaml
# task.yaml
task_id: The name of the task, which should match the name of the task directory.
status: An indicator of the task's development status.
description: A description of what the task does
notes: |-
  Optional notes about the task, things to add to it, issues with it, etc.
prompts: #
  # Tasks can have multiple prompt variants to see how well agents resolve issues
  # with different levels of detail. The base prompt is required; additional prompt
  # variants are optional. Each prompt will run as its own trial in its own sandbox.
  - key: base
    prompt: |-
      The prompt to give to the agent.
  - key: hard
    prompt: |-
      Optional prompt variants.
author_name: The name of the task author.
author_email: The author's email.
difficulty: How hard the task is.
category: The category of problem the task is testing.
tags:
  # Additional tags to help with organization
  - dbt
  - jinja

# An optional script to run after the agent runs, and before the tests are evaluated.
# This should be used if
#  1. the agent might update a file as part of the task
#  2. and might not run dbt,
#  3. which should be considered a success,
#  4. but dbt needs to run to evaluate the tests.
test_setup: |-
  dbt run --select obt_product_inventory

# ADE-bench will automatically do several things with the tables listed here:
#  1. Create solution seeds (called `solution__[table_name]`) after the agent runs.
#  2. Create a dbt test that checks for the existence of this table
#  3. Create a test to compare the table to corresponding solution seed.
#
# As is shown for with the second through fourth tables, you can:
#  1. Exclude some columns from the equality test
#  2. Only include certain columns in the equality test
#  3. Disable the creation of both the existence and equality tests.
solution_seeds:
  - table_name: dim_products
  - table_name: fct_sales
    inclulde_columns:
    - id
    - item_name_displayed
    - item_name_actual
  - table_name: fct_transactions
    exclude_columns:
    - bribe_amount_usd
  - table_name: generated_income_statement
    exclude_tests:
    - equality_test # Can also be `existence_test`

# These are the different database and project variants that the task supports
# If no migration directory is provided, then no migration script will run.
# If one is provided, it will be run against the project prior to the the task's
# setup.sh script.
variants:
- db_type: duckdb
  db_name: enron
  project_type: dbt
  project_name: enron

- db_type: snowflake
  db_name: enron
  project_type: dbt
  project_name: enron
  migration_directory: enron__duckdb_to_snowflake
```

## Usage

This command runs the benchmark. There are lots of flags for running it. Don't forget your favorites!

```bash
uv run scripts_python/run_harness.py \
  --tasks foo001 foo002 \ # Say `all` to run all the tasks in datasets/ade-bench-core.yaml.
  --db snowflake \ # Which database variant to run
  --project-type dbt \ # Which project variant to run (currently dbt or dbt-fusion)
  --agent oracle \ # Which agent to use (e.g., `oracle`, `claude-code`, `macro`)

  --exclude_task_ids foo001 \ #Optional; if you run all tasks, you can exclude tasks with this flag
  --n-concurrent-trials 4 \ # Optional; sets trial concurrency limit; defaults to 4.
  --n-attempts 1 \ # Optional; sets times to run each task; defaults to 1.
  --seed \ # Optional; flag for creating solution seed CSVs !! DESTRUCTIVE !! RUN WITH CAUTION !! SEE BELOW !!
  --no-diffs \ # Optional; disables taking snapshots of diffs
  --persist \ # Optional; keeps the container alive after the trial is over or is aborted.
```

---

## How it works, in detail

We skimmed over lots of details in the section above. This next section explains the painful tedium of those details.

### How dbt projects work

**ADE-bench currently supports `dbt` and `dbt-fusion`[^2] projects.** When creating a dbt project, include the `profile.yml` and `dbt_project.yml` file in the root directory of the project. In `profile.yml`, include a profile for all of the supported databases, where the name is `[project_name]-[database_type]. Do **NOT** fill in the Snowflake credentials, because these will get overwritten with the trial user:

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
      ## Added by when task is created
      account: <account>
      user: <user>
      password: <password>
      role: <role>
      database: <database>
      schema: <schema>
      warehouse: <warehouse>
```

### How databases work

ADE-bench currently supports these database types:

- DuckDB
- Snowflake

#### DuckDB

DuckDB databases should be stored in `shared/databases/duckdb`. When a task is run against a duckdb database, ADE-bench simply copies the `.duckdb` file from the shared directory into the task container.

#### Snowflake

Snowflake is more complicated:

**First,** add your Snowflake credentials to the `.env` file. **IMPORTANT:** This should be an adminstrative user that will create test environments within your Snowflake account. This is **NOT** the user the agent will control. Those users are created on demand for each trial. For more on what permissions this user needs, see the Installation section below.

```
SNOWFLAKE_ACCOUNT=[foo1234.us-east-1.snowflakecomputing.com / only the "foo1234" is necesary]
SNOWFLAKE_USER=[the user]
SNOWFLAKE_ROLE=[role name (see "What Snowflake role should I use?" below)]
SNOWFLAKE_PASSWORD=[the user's password]
SNOWFLAKE_WAREHOUSE=[the warehouse you want this user and all ade-bench agents to use]
```

**Second,** add data to your Snowflake database. If a task is configured to run against a Snowflake database, the name of that database should match the name of a database (i.e., [a collection of schemas](https://docs.snowflake.com/en/sql-reference/ddl-database)) in your Snowflake account. For help adding data to your Snowflake account, see "Adding data to Snowflake."

**Third,** when ADE-bench runs a task, three DDL scripts (found in `/ade_bench/setup/snowflake_setup.py`) are executed via the admin user above:

1. Clone the original database, with the name `TEMP_ADE_[name_of_task]_DATABASE`. (If that database already exists, it is first dropped, so this will reset any prior trials of that task.)
2. Create a new Snowflake user and role for the trial. The user is `TEMP_ADE_[name_of_task]_USER`; the role is `TEMP_ADE_[name_of_task]_ROLE`. If these already exist, they are also dropped.
3. Grant the appropriate permissions to the user and role. Snowflake is very particular about all of this; if you want to see the specifics, go to the `.py` file above.
4. The Snowflake credentials for this new user are added to `profiles.yml` in the dbt project. (Technically, this happens when the dbt project is set up and not after the Snowflake environment is set up, but, same same.)

**Fourth,** the trial is then conducted using the user created in the step above. Once the trial is complete, the users, roles, and databases all persist in the Snowflake account. If you want to clean these up, you can run this query, which will return a list of drop statements you can run all at once in the Snowflake UI:

```sql
select
  'user' as object_type,
  'drop user if exists "' || name || '";' as drop_statement
from snowflake.account_usage.users
where deleted_on is null
  and name ilike 'TEMP_ADE_%'

union all

select
    'role' as object_type,
    'drop role if exists "' || name || '";' as drop_statement
from snowflake.account_usage.roles
where deleted_on is null
  and name ilike 'TEMP_ADE_%'

union all

select
    'database' as object_type,
    'drop database if exists "' || database_name || '";' as drop_statement
from snowflake.account_usage.databases
where deleted is null
  and database_name ilike 'TEMP_ADE_%'

order by object_type, drop_statement;
```
### Agents

ADE-bench currently supports the following agents:

- Claude Code

#### Claude code

When a task is run with Claude Code, the following command runs in the repo:

```
claude --output-format json -p [ task prompt ] \
  --allowedTools Bash Edit Write NotebookEdit WebFetch
```

Additionally, a `CLAUDE.md` file is provided to Claude Code. That file can be found in the `/shared/config` directory.

### How trials are evaluated

After the agent runs, tasks are graded via dbt tests. You can add whatever manual tests you want to this directory. Additionally, you include solution seeds in your task, ADE-bench will automatically create tests for you.

More specifically, when the agent completes its work, several things happen:

1. If there are solution_seeds defined in the `task.yaml` file, the `\seeds` directory is copied into the sandbox. ADE-bench then runs `dbt seed` to create these tables in the database environment.
2. The existing test directory in the sandbox is replaced with the tests in the `\tests` directory of the task folder. If a task has no solution seeds, then it will only have manual tests; if a task has solution seeds, ADE-bench will automatically generate two tests (by default, `AUTO_{table_name}_equality.sql` and `AUTO_{table_name}_existence.sql`) and copy those. **Note:** ADE-bench automatically removes and regenerates all `AUTO_` tests prior to evaluating each trial, so if you update these files directly, your changes will probably get wiped away.
3. The tests in that directory are run and the results are recorded. If all of them pass, the task passes. If any fail, the task fails.

**Project and DB specific tests:** Tests can be designated for specific environments using comment headers:
```sql
-- db: duckdb          # Only runs for DuckDB
-- db: snowflake duckdb # Runs for both Snowflake and DuckDB
-- project-type: dbt   # Only runs for dbt projects
```
Tests without environment specification run on all environments.

#### Approximate equality tests

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

### Viewing results

As ADE-bench runs, it will tick through the progress of each trial. After the entire suite runs, it will print a summary of the results. To view a more detailed view of the results, run:
```
uv run scripts_python/view_results.py
```

This will open a local HTML page that includes much more detail, including details for each task:

- **Results**: Detailed JSON results of the trial.
- **Panes**: Terminal output from the setup, agent, and test phases of the trial.
- **Diffs**: File changes during task setup and changes made by the agent. If ADE-bench is run with the `--no-diffs` flag, these will not be available.

### The Oracle agent

The oracle agent is not really an agent—or, it's a very dumb agent. It's an agent that runs `$ bash solution.sh` and then shuts itself down.

In other words, the oracle agent is the answer key to the task. When ADE-bench is run where `--agent oracle` all the tests should pass. If they don't, something is wrong with the tasks themselves. So, it's important for tasks to have a solution script to make sure that the task is correctly configured.

**Note**: The `solution.sh` script might be different for different database and project variants. More on how to handle this is discussed in "Sharing projects across databases and project types" below.

#### Solution seeds

Many tasks have `solution_seeds` defined in their `task.yaml` file. These are tables that are used to evaluate the agent's work.

**You can generate these seeds by running ADE-bench with the `--seed flag`.** When you do this, the harness runs as it normally would,[^3] except, once trial is over, it exports two things into the task directory:

- **CSVs:** Each table defined in as solution seed will get exported into the task's `\seeds` directory as `solution__[table_name].csv`.
- **A seed config:** To ensure that the `dbt seed` command runs during the evaluation, ADE-bench will also create a schema file called `_no-op.txt`. This is utility file that is used when tables are uploaded. (Note that some shenanigans are necessary here to support cross-database compatibility. For example, DuckDB has a `hugeint` data type, whereas Snowflake does not. Why does the small database need huge integers?)

**ONLY RUN `--seed` WITH THE ORACLE AGENT ON DUCKDB** Exporting seeds is not currently supported with Snowflake (TODO?), and because solution seeds are used as answer keys, they should never be created based on what an agent does.

As described in `task.yaml` description above, there are several additional configuration options when setting up solution seeds:

- You can exclude columns from being part of the table equality comparision.
- You can select specific columns to only include.
- You can disable the automatic generation of either the equality or existence test.

### Sharing projects across databases and project types

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

3. When the `solution.sh` script runs, ADE-bench passes the corresponding database and project type into the script as an argument. So if different updates are needed to solve the trial depending on the database, these can configured follwing patterns like the example below:

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
#### Migrating DuckDB databases into Snowflake

ADE-bench includes a simple command for uploading DuckDB databases to Snowflake. This script will migrate all of the DuckDB files in `/shared/databases/duckdb` into their own databases (matching the name of the DuckDB database) in the Snowflake account in your `.env` file.

```bash
$ uv run scripts_python/migrate_duckdb_to_snowflake.py --use-database-export
```
The  `--use-database-export` flag is not necessary, but is recommended for better performance. You can also migrate specific databases using `--include` and `--exclude` flags:

```python
# Only foo.duckdb and bar.duckdb
$ uv run scripts_python/migrate_duckdb_to_snowflake.py --include foo bar

# All but bar.duckdb
$ uv run scripts_python/migrate_duckdb_to_snowflake.py --exclude bar
```

---

## Installation

Fuck if I know.

You need Docker? And uv? Honestly, I'd just trying running it and seeing what happens?

This is probably the easiest way to do that:

1. Clone the repo.
2. Download the DuckDB databases, and put them in the `/shared/databases/duckdb` directory. You can download those here: https://drive.google.com/drive/folders/1CNS_8mf81to02868HA-celmcPEFu4BPE
3. Run a basic execution:
```
uv run scripts_python/run_harness.py --tasks analytics_engineering001 --db duckdb --project-type dbt --agent oracle
```
4. See what it tells you to do? I think it'll ask if you have Docker and uv, and maybe some stuff like dbt, Snowflake CLIs, DuckDB, and Claude Code, for the agents. But that might all be handled by Dockerfile. Though, it is useful to have that stuff for dev. This section is still under development, ok?

### Snowflake setup

To run ADE-bench on a Snowflake database, the administrative role needs certain permissions. These are those permissions (I think; Snowflake permissions are special circle of hell):

```
GRANT CREATE DATABASE ON ACCOUNT TO ROLE <ade_bench_admin_role>;
GRANT MANAGE GRANTS ON ACCOUNT TO ROLE <ade_bench_admin_role>;

GRANT CREATE USER ON ACCOUNT TO ROLE <ade_bench_admin_role>;
GRANT CREATE ROLE ON ACCOUNT TO ROLE <ade_bench_admin_role>;
-- Alteratively:
GRANT ROLE useradmin TO ROLE <ade_bench_admin_role>;
```
---

## Configuration

Configuration is all managed through the `.env` file. It's fairly self-explanatory, but for completeness, why not:

```yaml
# API Keys for LLM providers
ANTHROPIC_API_KEY=[API key for Anthropic, if you want to run Claude Code agents]
OPENAI_API_KEY=[API key for OpenAI, if you want to run Codex agents]
MACRO_API_KEY=[API key for Macro, if you want to run Macro (Macro! https://getmacro.com/) agents]

# S3 Configuration (optional)
# This isn't used right now, so whatever, ignore it.
S3_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

# Snowflake configuration
# This is the admin user as described in the Snowflake setup above.
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_ROLE=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_WAREHOUSE=

# Timeout Settings (in seconds)
# These are default timeouts for each stage of the harness.
SETUP_TIMEOUT_SEC=120 # How long setup tasks can run
DEFAULT_AGENT_TIMEOUT_SEC=300 # How long the agent can run
DEFAULT_TEST_TIMEOUT_SEC=180 # How long test scripts can run
CLEANUP_TIMEOUT_SEC=60 # How long cleanup scripts can run

# Database Configuration (optional, for results storage)
# I don't know what this is? It's old.
DATABASE_URL=postgresql://user:password@localhost:5432/ade_bench

# Docker Configuration
# WE LOVE LINUX HERE AT ADE BENCH DOT COME
DOCKER_DEFAULT_PLATFORM=linux/amd64

# Logging
# This stuff is for nerds.
USE_DYNAMIC_LOGGING=TRUE # Set to FALSE if you want normal logs and not a fancy table.
FILE_DIFF_EXCLUDE_PATHS=/tmp,/logs,/var,/target,/build,/node_modules
LOG_LEVEL=INFO
```
---

## Development

To develop a new task, there are a few things that can be useful:

### Creating a local sanbox
You can create a local sandbox in a `/dev/sandbox` directory, which you can `cd` into and play around directly. This is especially helpful if you're developing on a DuckDB trial. To create that sandbox, run:
```
uv run scripts_python/create_sandbox.py --task [task_to_copy] --db [duckdb] --project-type [dbt]
```
This will move all of the relevant files into the directory above. Then, if you `cd` into that directory, you can manually execute the various steps of the task:

```bash
$ bash setup.sh # Run the setup script
$ bash migration.sh # Run the migration scripts, if needed
$ bash solution.sh # Run the solution script
$ dbt seed # Create the seed file
$ dbt test --select "test_type:singular" # Run the task tests
```
**Note:** This does **NOT** create a user or database in Snowflake like the task setup does. If you want to use this sandbox on Snowflake, you'll need to run the task first, which will create those resources in Snowflake.

### Creating seeds

When you're developing a task and ready to create CSVs for the solution seeds, run the following command:
```
uv run scripts_python/run_harness.py --task [task_to_copy] --db duckdb --project-type [dbt] --agent oracle --seed
```

The final seed flag will export the CSVs from final project in the task's `/seeds` directory. **Read the warning in "Solution seeds" before doing this.**

#### Debugging

Stuff goes wrong. It's really finicky sometimes. To debug, it's often useful to use the sanbox, but the most helpful thing is running the trial with the `--persist` flag, which keeps your Docker container alive after the task is complete. Then, you can log into the container—either directly, or via the Docker desktop app[^3], and both look at the files in the container and run commands in a terminal.

Moreover, if you're working with Snowflake, the task will create task databases within your account. You can also query these directly.

Finally, if you want to stop the harness at any point throughout the trial, you can insert a breakpoint function into the harness. To do this, find the point within the script that you want to halt the run (you have to read the code; it's messy; I might make this an easier config at somet point). Then, in the code, add:

```python
from ade_bench.utils.debug_breakpoint import breakpoint
breakpoint("optional message")
```

This will halt the harness at that point. If you run the harness with the `--persist` flag, the container will then be kept alive, as it was when the harness was halted.

---
## Tips! Tricks! Other things we recommend!

- **Disable diffs to speed things up.** If you trying to run a bunch of tasks, or testing something where you don't care about looking at diffs, use the `--no-diffs` flag. Diffs can be slow, and ADE-bench will run faster if they're turned off.
- **View all the tasks.** Running `uv run scripts_python/extract_task_details.py` will print a summary table of all the tasks in ADE-bench. It will also copy a more detailed summary to your clipboard, which you can paste into a spreadsheet.
- **Use aliases.** I've created a bunch of aliases to speed things up. These are some of the ones I use a lot:

```bash
# For running tests and viewing results
alias ade-run='uv run scripts_python/run_harness.py'
alias ade-log='uv run scripts_python/view_results.py'
# Usage
$ ade-run --db snowflake --project-type dbt --task all --agent oracle
$ ade-log


# For creating a sandbox environment for testing, navigating into it, and running
# various setup scripts, including opening it up in the DuckDB UI. You can obviously
# run whichever scripts here you want, to get the sandbox in whatever state you want
# to do development work in.
alias ade-dev='uv run scripts_python/create_sandbox.py'
alias sand='cd ~/ade-bench/dev/sandbox'
alias mg='bash migration.sh'
alias st='bash setup.sh'
alias sl='bash solution.sh'
alias ts='dbt test --select "test_type:singular"'
alias ddb='duckdb -ui'
# Usage:
$ ade-dev --task foo001 --db snowflake --project-type dbt # Create sandbox
$ sand # Navigate into sandbox
$ mg # If Snowflake, run the migration scripts
$ st # Run the setup scripts
$ sl # Run the solution scripts
$ dbt seed # Add the soltuion seeds
$ ts # Run the tests
$ ddb # If DuckDB, open the DuckDB UI


# For viewing all the tasks
alias ade-config='uv run scripts_python/extract_task_details.py'
# Usage
$ ade-config
```

---

[^1] ADE-bench is short for "Analytics and data engineering benchmark," and is pronounced ~lemon~ade-bench and not AYE-DEE-EE-bench, because that is how [we should pronounce things](https://en.wikipedia.org/wiki/SQL) around here.

[^2] For a full list of known issues with dbt Fusion support, see (#12)[https://github.com/thedatamates/ade-bench/issues/12].

[^3] A somewhat annoying thing about this: When you run ADE-bench with the `--seed` flag, it will evaluate each trial with whatever CSVs exist in the `/seeds` directory _before_ the new ones are created, and then, _after the tests have run_, it will export the results into the directory. This means that you may need to run it twice to check that task works: Once to create the seeds, and another time (without the `--seed` flag) to see if it passes.