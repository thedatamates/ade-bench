#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"
inventory_file="fact_inventory.sql"
products_file="dim_products.sql"
obt_file="obt_product_inventory.sql"

## Update timestamp function config in solution files by db type
if [[ "$*" != *"--db-type=duckdb"* ]]; then
    find="CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
    replace="TO_DATE(TO_TIMESTAMP(transaction_created_date, 'MM/DD/YYYY HH24:MI:SS'))"
    "${SED_CMD[@]}" "s|${find}|${replace}|g" $SOLUTIONS_DIR/$inventory_file
fi

cp $SOLUTIONS_DIR/$inventory_file models/warehouse/$inventory_file
cp $SOLUTIONS_DIR/$products_file models/warehouse/$products_file
cp $SOLUTIONS_DIR/$obt_file models/analytics_obt/$obt_file
