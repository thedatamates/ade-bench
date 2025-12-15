---
name: dbt-debug
description: Toolkit for debugging dbt projects. Use when encountering dbt errors, test failures, unexpected results, or when needing to investigate model behavior, trace dependencies, examine compiled SQL, or troubleshoot any aspect of a dbt project's execution.
---

# dbt Debugging Skill

## Debugging Workflow

When debugging any dbt issue, follow this systematic approach:

1. Read the error message. The error message dbt produces will normally contain the type of error, and the file where the error occurred.
2. Inspect the file that was known to cause the issue, and see if there's an immediate fix.
3. Isolate the problem — for example, by running one model a time, or by undoing the code that broke things.
4. Review compiled files and the logs.
    - The target/compiled directory contains select statements that you can run in any query editor.
    - The target/run directory contains the SQL dbt executes to build your models.
    - The logs/dbt.log file contains all the queries that dbt runs, and additional logging. Recent errors will be at the bottom of the file.

## Available Commands

- `dbt debug` checks that dbt is correctly installed, and can successfully connect to the configured data warehouse. It will not take any project content into consideration beyond core pieces of `profiles.yml` and `dbt_project.yml`
- `dbt --version` will return the currently installed version of dbt (and adapters, for dbt Core). This is the best way to check whether the project is using dbt Core or the new dbt Fusion engine.
- `dbt parse` will validate that the dbt project is correctly structured (valid YAML and configs). It will not run queries against the remote warehouse.
- `dbt compile` will render Jinja templates. dbt Core's engine does not understand SQL, so a successful compile step does not mean the SQL is valid. By contrast, the dbt Fusion engine produces and statically analyze a logical plan (as long as the `static_analysis` config is not set to `off` for a model or any of its parents) during a `dbt compile` step, which is a cheap way to verify a project's content.
- `dbt show` returns the first 5 rows of a single node (when used with `--select`) or of an arbitrary query (when used with `--inline`). Use `--limit` to fetch a different number of rows. When writing an `--inline` query, do not provide a limit statement inside the query text.
- `dbt run` will attempt to materialize the selected models into the warehouse. For dbt Core, the rendered SQL can only be verified by running it against the warehouse.
- `dbt test` runs selected tests without verifying that the resources being tested already exist in the warehouse.
- `dbt build` runs all selected resources (tests, models, snapshots, seeds) in DAG order. It is the best command to use to pinpoint where in the project an issue exists, and to validate that an issue has been resolved.
- `dbt run-operation` allows invocation of arbitrary macros. This is unlikely to be relevant unless instructed by the user.
- `dbt clean` will delete the paths specified in `clean-targets` list of `dbt_project.yml`. It is normally used to delete the target directory and any installed packages.
- `dbt deps` will install the exact package versions specified in `package-lock.yml` if specified. If there is no `package-lock.yml`, dbt will resolve the requested dependencies (including transitive dependencies) in `packages.yml` or `dependencies.yml`.

## dbt Core vs the dbt Fusion engine

The dbt Fusion engine is the next-generation engine to execute dbt projects. If the dbt Fusion engine is installed (check with `dbt --version`), then try validating SQL using `dbt compile` before consuming warehouse resources with a `dbt run` or `dbt build`.

## Common misconceptions and mistakes

- Do not attempt to use `dbt run-query` or `dbt run-operation run_query`, they do not exist.
- Do not attempt to modify database tables directly. Instead, write models which transform the data as required.
- You should not just filter out data that doesn't match expectations, even if you don't think it's being used.
- Always use `{{ref()}}` or `{{source()}}` to point to objects. Do not guess at a table's schema or database.
