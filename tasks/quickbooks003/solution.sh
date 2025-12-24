#!/bin/bash

## Fix the data issue
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema='main'
else
    schema='public'
fi

# Execute SQL using the run_sql utility.
/scripts/run_sql.sh "$@" << SQL
create or replace table ${schema}.refund_receipt_data_temp as
  select * replace (transaction_date::date as transaction_date)
  from ${schema}.refund_receipt_data;

create or replace table ${schema}.sales_receipt_data_temp as
  select * replace (transaction_date::date as transaction_date)
  from ${schema}.sales_receipt_data;

create or replace table ${schema}.estimate_data_temp as
  select * replace (due_date::date as due_date)
  from ${schema}.estimate_data;

drop table ${schema}.sales_receipt_data;
drop table ${schema}.refund_receipt_data;
drop table ${schema}.estimate_data;

alter table ${schema}.sales_receipt_data_temp rename to sales_receipt_data;
alter table ${schema}.refund_receipt_data_temp rename to refund_receipt_data;
alter table ${schema}.estimate_data_temp rename to estimate_data;
SQL


## Remove the using_department variable
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

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