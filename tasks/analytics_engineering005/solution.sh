#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## Update timestamp function config in solution files by db type
file="fact_inventory.sql"

if [[ "$*" != *"--db-type=duckdb"* ]]; then
    find="CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
    replace="TO_DATE(TO_TIMESTAMP(transaction_created_date, 'MM/DD/YYYY HH24:MI:SS'))"
    "${SED_CMD[@]}" "s|${find}|${replace}|g" $SOLUTIONS_DIR/$file
fi

cp $SOLUTIONS_DIR/$file models/warehouse/$file
