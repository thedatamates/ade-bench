#!/bin/bash
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi


## Update estimate stg model
find="cast( {{ dbt.date_trunc('day', 'due_date') }} as date) as due_date,"
replace="cast( {{ dbt.date_trunc('day', 'cast(due_date as date)') }} as date) as due_date,"

"${SED_CMD[@]}" "s/${find}/${replace}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__estimate.sql


## Update sales receipt and refund receipt stg models
find="cast( {{ dbt.date_trunc('day', 'transaction_date') }} as date) as transaction_date,"
replace="cast( {{ dbt.date_trunc('day', 'cast(transaction_date as date)') }} as date) as transaction_date,"

"${SED_CMD[@]}" "s/${find}/${replace}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__sales_receipt.sql
"${SED_CMD[@]}" "s/${find}/${replace}/g" dbt_packages/quickbooks_source/models/stg_quickbooks__refund_receipt.sql


# Run dbt to create the models
dbt run
