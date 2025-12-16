---
name: dbt-skill
description: Interact with dbt projects. dbt is a data transformation tool.
---

# Using dbt for analytics and data engineering

## Key terminology

- A **[model](https://docs.getdbt.com/docs/build/models)** is a select statement which will be persisted to the database as a view, table, materialized view, iceberg table, etc. Ephemeral models are inlined CTEs.
- A **[dbt project](https://docs.getdbt.com/docs/build/projects)** is a collection of models, tests, seeds, snapshots, macros, and configuration files that define data transformations and their dependencies.
- A **[source](https://docs.getdbt.com/docs/build/sources)** is a reference to raw data tables in your warehouse that exist outside of dbt. Sources are defined in YAML files and used as the starting point for your transformations.
- A **[seed](https://docs.getdbt.com/docs/build/seeds)** is a CSV file in your dbt project that gets loaded into your warehouse as a table. Seeds are typically used for small reference or lookup tables.
- A **[snapshot](https://docs.getdbt.com/docs/build/snapshots)** captures the state of a mutable table at a point in time, enabling Type 2 Slowly Changing Dimension tracking.
- A **[test](https://docs.getdbt.com/docs/build/data-tests)** is an assertion about your data. Tests can be generic (e.g., `unique`, `not_null`) or singular (custom SQL queries that return failing rows).
- A **[macro](https://docs.getdbt.com/docs/build/jinja-macros)** is a reusable Jinja template function that generates SQL or performs other logic. Macros enable code reuse and abstraction.
- A **[package](https://docs.getdbt.com/docs/build/packages)** is a collection of dbt resources (models, macros, etc.) that can be installed and reused across projects.
- A **[materialization](https://docs.getdbt.com/docs/build/materializations)** is the strategy dbt uses to persist a model in the warehouse (e.g., table, view, incremental, ephemeral).
- The **[DAG](https://docs.getdbt.com/terms/dag)** (Directed Acyclic Graph) is the dependency structure of your dbt project, showing how models depend on each other.
- A **[node](https://docs.getdbt.com/reference/node-selection/syntax)** is any object in the DAG (model, test, seed, snapshot, source, etc.) that dbt can select and execute.
- A **[selector](https://docs.getdbt.com/reference/node-selection/syntax)** is a pattern used to specify which nodes to run (e.g., `model_name`, `+model_name` for upstream, `model_name+` for downstream).
- A **[resource](https://docs.getdbt.com/reference/configs-and-properties)** is any dbt object defined in your project (models, sources, tests, etc.). Resources are nodes that can be referenced and built.
- An **[adapter](https://docs.getdbt.com/docs/connect-adapters)** is a plugin that enables dbt to work with different data warehouses (e.g., Snowflake, BigQuery, DuckDB).

## Core loop

I have:

- a dbt project
- a CLI with dbt installed
- a database connection

You are being asked to make changes that will affect the dbt models and resources in the DAG, in the service of producing data artifacts for use in other downstream tools.

This could look like:

- creating a new dbt model based off of sources or models that currently exist in your project
- modifying an existing model in your dbt project
- adding a new source of data to your dbt project
- changing the settings or configurations of your dbt project, for example adding descriptions or tests to a column, or changing a model's materialization strategy.
- running CLI commands to apply the state defined in your dbt project to your database (for example to build a new table in the database or refresh the existing data)

These are the primitives you will use when fulfilling a user request. Many requests will require you to do some combination of tasks in that list, in a specific order.

Much of the complexity of this work will boil down to the following:

- Ensuring that you have an understanding of the tables, their columns and their data types
- Taking actions in the correct order, and validating that you have done the correct thing at each step of the process, instead of waiting until the end to check

The best way to ensure you are correctly following your instructions is to adhere to the below workflow.

When asked to make changes to a dbt project, you should:

1. Understand the problem you are trying to solve. Do you need to add new models or modify existing models?
2. Gather context on what you have available to you:
    - the dbt project (models, seeds, YAML files, etc)
    - the objects in the warehouse (databases, schemas, tables, UDFs)
3. Plan how to perform the desired transformations:
    - Determine which models will need to be modified.
    - Decide which order to modify the models in, working in DAG order from parents to children.
4. For each model you modify:
    - Plan out what will change. Which columns need to be added, modified or deleted. Which rows need to be added or removed based on modifications to joins or filters?
    - Define success criteria you can use to validate whether your changes were correct.
    - Apply the changes you planned, by writing dbt code into the model file.
    - Build the changed model with `dbt build`.
    - Run `dbt show` to validate that the success criteria you defined have been met.
    - Carefully validate that there are no subtle issues in the data such as type mismatches.
    - Repeat with the next model.
5. If you encounter compilation errors or warehouse errors during iteration, use the debugging guide.

## Debugging

- Read the error message. The error message dbt produces will normally contain the type of error, and the file where the error occurred.
- Work out whether the problem is in the code or the data. Recent code changes imply a code problem, otherwise the underlying data from an upstream source is likely to be the cause.
- Isolate the problem — for example, by running one model a time, or by undoing the code that broke things.
- Review compiled files and the logs:
  - The `target/compiled` directory contains the rendered model code as a select statement.
  - The `target/run` directory contains that rendered code inside of DDL statements such as `CREATE TABLE AS SELECT`.
  - The `logs/dbt.log` file contains all the queries that dbt rans, and additional logging. Recent errors will be at the bottom of the file.

If the issue is in the code:

- Inspect the file that was known to cause the issue, and see if there's an immediate fix.

If the issue is in the data:

- Identify the problematic column(s) with bisection or by reading the error message
- Profile suspect columns using the sample code in `scripts/profiling.md` to identify the underlying cause.

## Available Commands

- `dbt debug` checks that dbt is correctly installed, and can successfully connect to the configured data warehouse. It will not take any project content into consideration beyond core pieces of `profiles.yml` and `dbt_project.yml`
- `dbt --version` will return the currently installed version of dbt (and adapters, for dbt Core). This is the best way to check whether the project is using dbt Core or the new dbt Fusion engine.
- `dbt parse` will validate that the dbt project is correctly structured (valid YAML and configs). It will not run queries against the remote warehouse. It is implicitly run during the following commands, so does not need to be explicitly invoked.
- `dbt compile` will render Jinja templates. dbt Core's engine does not understand SQL, so a successful compile step does not mean the SQL is valid. By contrast, the dbt Fusion engine produces and statically analyze a logical plan (as long as the `static_analysis` config is not set to `off` for a model or any of its parents) during a `dbt compile` step, which is a cheap way to verify a project's content.
- `dbt show` returns the first 5 rows of a single node (when used with `--select`) or of an arbitrary query (when used with `--inline`). Use `--limit` to fetch a different number of rows. When writing an `--inline` query, do not provide a limit statement inside the query text.
- `dbt run` will attempt to materialize the selected models into the warehouse. For dbt Core, the rendered SQL can only be verified by running it against the warehouse.
- `dbt test` runs selected tests without verifying that the resources being tested already exist in the warehouse.
- `dbt build` runs all selected resources (tests, models, snapshots, seeds) in DAG order. It is the best command to use to pinpoint where in the project an issue exists, and to validate that an issue has been resolved.
- `dbt run-operation` allows invocation of arbitrary macros. This is unlikely to be relevant unless instructed by the user.
- `dbt clean` will delete the paths specified in `clean-targets` list of `dbt_project.yml`. It is normally used to delete the target directory and any installed packages.
- `dbt deps` will install the exact package versions specified in `package-lock.yml` if specified. If there is no `package-lock.yml`, dbt will resolve the requested dependencies (including transitive dependencies) in `packages.yml` or `dependencies.yml`.

## Other warnings

- You should NEVER write DDL or DML directly to the warehouse; always use dbt for this.
- Do not filter data out of models unless asked to.

<!-- Before making any change to any table, run `dbt show` to have a look at the data. TODO add sample code for fetching count(*) etc.
        - Come up with up to three questions you can ask of the data before modifying the model, and fetch the results from the existing table (if possible) so that you can compare them afterwards. -->
