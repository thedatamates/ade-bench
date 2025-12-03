#!/bin/bash

## Fix the error by changing the data type of the underlying table.

## Get the schema based on the database type.
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema='main'
else
    schema='public'
fi

# Execute SQL using the run_sql utility.
/scripts/run_sql.sh "$@" << SQL
-- Update the id field to be a string.
create or replace table ${schema}.task_data_temp as
  select
    * replace (due_at::timestamp as due_at)
  from ${schema}.task_data;

-- Rename the table to the original name.
drop table ${schema}.task_data;
alter table ${schema}.task_data_temp rename to task_data;
SQL

## MOVE FILES
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

project="asana__project.sql"
agg="int_asana__project_user_agg.sql"

cp $SOLUTIONS_DIR/$project models/$project
cp $SOLUTIONS_DIR/$agg models/intermediate/$agg