#!/bin/bash

## Create duplicates in the inventory table
## Get the schema based on the database type.
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema='main'
else
    schema='public'
fi

## Run the query to duplicate rows
/scripts/run_sql.sh "$@" << SQL
insert into ${schema}.inventory_transactions
    select *
    from ${schema}.inventory_transactions
    where mod(product_id,2) = 0;
SQL


## Copy the new fact_inventory model that doesn't handle duplicates
file="fact_inventory.sql"

SETUP_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/setup"

if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

if [[ "$*" != *"--db-type=duckdb"* ]]; then
    find="CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
    replace="TO_DATE(TO_TIMESTAMP(transaction_created_date, 'MM/DD/YYYY HH24:MI:SS'))"
    "${SED_CMD[@]}" "s|${find}|${replace}|g" $SETUP_DIR/$file
fi

cp $SETUP_DIR/$file models/warehouse/$file

dbt deps
dbt run