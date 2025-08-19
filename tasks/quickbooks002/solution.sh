#!/bin/bash
## Remove the using_department variable
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

f="using_department: true"
r=""

"${SED_CMD[@]}" "s/${f}/${r}/g" dbt_project.yml


## Remove all the references to using_department
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## In intermediate directory
cp $SOLUTIONS_DIR/int_quickbooks__expenses_union.sql models/intermediate/int_quickbooks__expenses_union.sql
cp $SOLUTIONS_DIR/int_quickbooks__sales_union.sql models/intermediate/int_quickbooks__sales_union.sql

## Not in intermediate directory
cp $SOLUTIONS_DIR/quickbooks__ap_ar_enhanced.sql models/quickbooks__ap_ar_enhanced.sql


dbt run