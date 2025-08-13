#!/bin/bash

## Fix casting error caused by fivetran package version mismatch
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

find="cast(coalesce(due_on, due_at) as {{ dbt.type_timestamp() }}) as due_date,"
replace="cast(coalesce(cast(due_on as {{ dbt.type_timestamp() }}), cast(due_at as {{ dbt.type_timestamp() }})) as {{ dbt.type_timestamp() }}) as due_date,"

"${SED_CMD[@]}" "s/${find}/${replace}/g" dbt_packages/asana_source/models/stg_asana__task.sql

## MOVE FILES
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

project="asana__project.sql"
agg="int_asana__project_user_agg.sql"

cp $SOLUTIONS_DIR/$project models/$project
cp $SOLUTIONS_DIR/$agg models/intermediate/$agg


dbt run
