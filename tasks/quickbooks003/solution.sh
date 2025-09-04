#!/bin/bash
## Remove the using_department variable
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

## Update estimate stg model to fix underlying data issue
f1="cast( {{ dbt.date_trunc('day', 'due_date') }} as date) as due_date,"
r1="cast( {{ dbt.date_trunc('day', 'cast(due_date as date)') }} as date) as due_date,"

"${SED_CMD[@]}" "s/${f1}/${r1}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__estimate.sql

## Update sales receipt and refund receipt stg models
f2="cast( {{ dbt.date_trunc('day', 'transaction_date') }} as date) as transaction_date,"
r2="cast( {{ dbt.date_trunc('day', 'cast(transaction_date as date)') }} as date) as transaction_date,"

"${SED_CMD[@]}" "s/${f2}/${r2}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__sales_receipt.sql
"${SED_CMD[@]}" "s/${f2}/${r2}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__refund_receipt.sql


## Remove the department variable
f3="using_department: true"
r3=""

"${SED_CMD[@]}" "s/${f3}/${r3}/g" dbt_project.yml


## Remove all the references to using_department
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## In intermediate directory
cp $SOLUTIONS_DIR/int_quickbooks__expenses_union.sql models/intermediate/int_quickbooks__expenses_union.sql
cp $SOLUTIONS_DIR/int_quickbooks__sales_union.sql models/intermediate/int_quickbooks__sales_union.sql

## Not in intermediate directory
cp $SOLUTIONS_DIR/quickbooks__ap_ar_enhanced.sql models/quickbooks__ap_ar_enhanced.sql