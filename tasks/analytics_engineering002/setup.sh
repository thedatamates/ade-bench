#!/bin/bash

# Remove a comma
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

find="p.supplier_company,"
replace="p.supplier_company"

"${SED_CMD[@]}" "s/${find}/${replace}/g" models/analytics_obt/obt_product_inventory.sql

dbt deps
dbt run