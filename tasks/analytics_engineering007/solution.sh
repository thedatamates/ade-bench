#!/bin/bash

SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## Update timestamp function config in solution files by db type
s1="fact_inventory.sql"
s2="fact_sales.sql"

if [[ "$*" != *"--db-type=duckdb"* ]]; then
    f1="CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
    r1="TO_DATE(TO_TIMESTAMP(transaction_created_date, 'MM/DD/YYYY HH24:MI:SS'))"
    sed -i "s|${f1}|${r1}|g" $SOLUTIONS_DIR/$s1

    f2="CAST(STRPTIME(o.order_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
    r2="TO_DATE(TO_TIMESTAMP(o.order_date, 'MM/DD/YYYY HH24:MI:SS'))"
    sed -i "s|${f2}|${r2}|g" $SOLUTIONS_DIR/$s2
fi

cp $SOLUTIONS_DIR/$s1 models/warehouse/$s1
cp $SOLUTIONS_DIR/$s2 models/warehouse/$s2
