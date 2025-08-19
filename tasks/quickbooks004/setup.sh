#!/bin/bash

## Fix the data type issue. 
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi


## Update estimate stg model
f1="cast( {{ dbt.date_trunc('day', 'due_date') }} as date) as due_date,"
r1="cast( {{ dbt.date_trunc('day', 'cast(due_date as date)') }} as date) as due_date,"

"${SED_CMD[@]}" "s/${f1}/${r1}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__estimate.sql


## Update sales receipt and refund receipt stg models
f2="cast( {{ dbt.date_trunc('day', 'transaction_date') }} as date) as transaction_date,"
r2="cast( {{ dbt.date_trunc('day', 'cast(transaction_date as date)') }} as date) as transaction_date,"

"${SED_CMD[@]}" "s/${f2}/${r2}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__sales_receipt.sql
"${SED_CMD[@]}" "s/${f2}/${r2}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__refund_receipt.sql


# Run dbt to create the models
dbt run